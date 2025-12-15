"""
Vercel Serverless Function for downloading YouTube videos as MP3
and uploading to GitHub Releases
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import subprocess
import tempfile
import requests
from urllib.parse import quote

class handler(BaseHTTPRequestHandler):
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        try:
            # Get GitHub token from environment
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                self.send_error_response(500, 'Server configuration error: GITHUB_TOKEN not set')
                return
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            youtube_url = data.get('url', '').strip()
            
            if not youtube_url:
                self.send_error_response(400, 'No URL provided')
                return
            
            # Validate YouTube URL
            if 'youtube.com' not in youtube_url and 'youtu.be' not in youtube_url:
                self.send_error_response(400, 'Invalid YouTube URL')
                return
            
            # Download MP3 to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Download with yt-dlp
                    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')
                    result = subprocess.run([
                        'yt-dlp',
                        '-x',
                        '--audio-format', 'mp3',
                        '--audio-quality', '0',
                        '-o', output_template,
                        youtube_url
                    ], capture_output=True, text=True, timeout=120)
                    
                    if result.returncode != 0:
                        self.send_error_response(500, f'Download failed: {result.stderr}')
                        return
                    
                    # Find the downloaded file
                    files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
                    if not files:
                        self.send_error_response(500, 'No MP3 file generated')
                        return
                    
                    mp3_file = files[0]
                    mp3_path = os.path.join(temp_dir, mp3_file)
                    
                    # Get file count for numbering
                    repo_owner = 'josazar'
                    repo_name = 'MP3_CHARLIEOLGA'
                    release_tag = 'audio-files-v1.0'
                    
                    # Get current assets count
                    assets_count = self.get_assets_count(repo_owner, repo_name, release_tag, github_token)
                    new_number = str(assets_count).zfill(2)
                    
                    # Rename file with number prefix
                    new_filename = f"{new_number}_{mp3_file}"
                    new_path = os.path.join(temp_dir, new_filename)
                    os.rename(mp3_path, new_path)
                    
                    # Upload to GitHub Release
                    upload_success = self.upload_to_github_release(
                        repo_owner, repo_name, release_tag,
                        new_path, new_filename, github_token
                    )
                    
                    if not upload_success:
                        self.send_error_response(500, 'Failed to upload to GitHub Release')
                        return
                    
                    # Update playlist.json
                    self.update_playlist(repo_owner, repo_name, github_token)
                    
                    # Send success response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True,
                        'title': mp3_file.replace('.mp3', ''),
                        'filename': new_filename,
                        'message': 'MP3 downloaded and uploaded to GitHub Release successfully!'
                    }).encode())
                    
                except subprocess.TimeoutExpired:
                    self.send_error_response(504, 'Download timeout (max 2 minutes)')
                except Exception as e:
                    self.send_error_response(500, f'Processing error: {str(e)}')
                    
        except Exception as e:
            self.send_error_response(500, f'Server error: {str(e)}')
    
    def get_assets_count(self, owner, repo, tag, token):
        """Get number of assets in release"""
        try:
            url = f'https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}'
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return len(response.json().get('assets', []))
            return 0
        except:
            return 0
    
    def upload_to_github_release(self, owner, repo, tag, file_path, filename, token):
        """Upload file to GitHub Release"""
        try:
            # Get release ID
            url = f'https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}'
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return False
            
            release_id = response.json()['id']
            upload_url = f'https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets'
            
            # Clean filename for URL
            clean_filename = filename.replace(' ', '.').replace('(', '').replace(')', '').replace("'", '').replace('"', '')
            
            # Upload file
            with open(file_path, 'rb') as f:
                upload_headers = {
                    'Authorization': f'token {token}',
                    'Content-Type': 'application/octet-stream'
                }
                params = {'name': clean_filename}
                upload_response = requests.post(
                    upload_url, 
                    headers=upload_headers,
                    params=params,
                    data=f
                )
            
            return upload_response.status_code == 201
            
        except Exception as e:
            print(f'Upload error: {e}')
            return False
    
    def update_playlist(self, owner, repo, token):
        """Update playlist.json in the repository"""
        try:
            # Get all release assets
            url = f'https://api.github.com/repos/{owner}/{repo}/releases/tags/audio-files-v1.0'
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                return False
            
            assets = response.json().get('assets', [])
            assets.sort(key=lambda x: x['name'])
            
            # Create playlist
            playlist = []
            base_url = f"https://github.com/{owner}/{repo}/releases/download/audio-files-v1.0"
            
            for asset in assets:
                filename = asset['name']
                title = filename
                if '_' in filename:
                    title = '_'.join(filename.split('_')[1:])
                title = title.replace('.mp3', '').replace('.', ' ')
                
                playlist.append({
                    "title": title,
                    "file": f"{base_url}/{filename}"
                })
            
            # Update playlist.json in repo
            playlist_json = json.dumps(playlist, ensure_ascii=False, indent=2)
            
            # Get current file SHA
            file_url = f'https://api.github.com/repos/{owner}/{repo}/contents/playlist.json'
            file_response = requests.get(file_url, headers=headers)
            
            if file_response.status_code == 200:
                current_sha = file_response.json()['sha']
            else:
                current_sha = None
            
            # Update file
            import base64
            content_encoded = base64.b64encode(playlist_json.encode()).decode()
            
            update_data = {
                'message': 'Update playlist.json with new track',
                'content': content_encoded,
                'branch': 'master'
            }
            
            if current_sha:
                update_data['sha'] = current_sha
            
            update_response = requests.put(file_url, headers=headers, json=update_data)
            return update_response.status_code in [200, 201]
            
        except Exception as e:
            print(f'Playlist update error: {e}')
            return False
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': False,
            'error': message
        }).encode())

