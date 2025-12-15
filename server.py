#!/usr/bin/env python3
"""
Simple HTTP server to run the audio player.
This avoids CORS issues when loading JSON and audio files.
Handles POST requests for downloading YouTube videos.
"""
import http.server
import socketserver
import webbrowser
import os
import json
import subprocess
import sys
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlparse, unquote

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow loading resources
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range')
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests with range support for streaming"""
        # Check if this is a request for an audio file
        if self.path.endswith(('.mp3', '.m4a', '.ogg', '.wav', '.flac')):
            self.handle_range_request()
        else:
            super().do_GET()
    
    def handle_range_request(self):
        """Handle HTTP range requests for audio streaming"""
        import re
        
        # Get the file path
        path = self.translate_path(self.path)
        
        try:
            # Check if file exists
            if not os.path.exists(path):
                self.send_error(404, "File not found")
                return
            
            file_size = os.path.getsize(path)
            
            # Parse range header
            range_header = self.headers.get('Range')
            
            if range_header:
                # Extract byte range
                match = re.search(r'bytes=(\d+)-(\d*)', range_header)
                if match:
                    start = int(match.group(1))
                    end = int(match.group(2)) if match.group(2) else file_size - 1
                    
                    # Validate range
                    if start >= file_size or end >= file_size or start > end:
                        self.send_error(416, "Range Not Satisfiable")
                        return
                    
                    # Read the requested range
                    with open(path, 'rb') as f:
                        f.seek(start)
                        content = f.read(end - start + 1)
                    
                    # Send partial content response
                    content_type, _ = mimetypes.guess_type(path)
                    if not content_type:
                        content_type = 'application/octet-stream'
                    
                    self.send_response(206)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Range', f'bytes {start}-{end}/{file_size}')
                    self.send_header('Content-Length', str(len(content)))
                    self.send_header('Accept-Ranges', 'bytes')
                    self.end_headers()
                    self.wfile.write(content)
                    return
            
            # No range header - send full file
            with open(path, 'rb') as f:
                content = f.read()
            
            content_type, _ = mimetypes.guess_type(path)
            if not content_type:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(file_size))
            self.send_header('Accept-Ranges', 'bytes')
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")
    
    def translate_path(self, path):
        """Translate URL path to filesystem path"""
        # Remove query string
        path = path.split('?')[0]
        # URL decode the path to handle special characters (emojis, spaces, etc.)
        path = unquote(path)
        # Remove leading slash
        path = path.lstrip('/')
        # Default to current directory
        if not path:
            path = 'index.html'
        return path

    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        """Handle POST requests for downloading videos"""
        if self.path == '/download':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                url = data.get('url', '')

                if not url:
                    self.send_error_response(400, 'URL is required')
                    return

                # Validate YouTube URL
                if 'youtube.com' not in url and 'youtu.be' not in url:
                    self.send_error_response(400, 'Invalid YouTube URL')
                    return

                # Download the video
                result = self.download_video(url)
                
                if result['success']:
                    # Regenerate playlist (this will also rename all files with prefixes)
                    try:
                        self.regenerate_playlist()
                        # Small delay to ensure file system sync
                        import time
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"Warning: Playlist regeneration had issues: {e}")
                    
                    self.send_json_response(200, {
                        'success': True,
                        'title': result['title'],
                        'message': 'Download completed successfully',
                        'playlist_updated': True
                    })
                else:
                    self.send_error_response(500, result.get('error', 'Download failed'))

            except json.JSONDecodeError:
                self.send_error_response(400, 'Invalid JSON in request')
            except Exception as e:
                self.send_error_response(500, f'Server error: {str(e)}')
        else:
            self.send_error_response(404, 'Not found')

    def download_video(self, url):
        """Download video from YouTube and convert to MP3"""
        try:
            audio_dir = Path('audio')
            audio_dir.mkdir(exist_ok=True)

            # Get SSL certificate path
            try:
                import certifi
                cert_path = certifi.where()
            except ImportError:
                cert_path = None

            # Build yt-dlp command
            cmd = [
                sys.executable, '-m', 'yt_dlp',
                '-x',  # Extract audio
                '--audio-format', 'mp3',
                '--audio-quality', '0',  # Best quality
                '-o', str(audio_dir / '%(title)s.%(ext)s'),
                url
            ]

            # Set environment variable for SSL if certifi is available
            env = os.environ.copy()
            if cert_path:
                env['SSL_CERT_FILE'] = cert_path

            # Run yt-dlp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                return {
                    'success': False,
                    'error': f'yt-dlp error: {error_msg[:200]}'
                }

            # Find the downloaded file
            # yt-dlp outputs the filename, try to extract it
            output_lines = result.stdout.split('\n')
            downloaded_file = None
            
            for line in output_lines:
                if '[download] Destination:' in line or '[ExtractAudio] Destination:' in line:
                    # Extract filename from line
                    parts = line.split('Destination:')
                    if len(parts) > 1:
                        downloaded_file = parts[1].strip()
                        break

            # If we can't find it in output, search for newest MP3 file
            if not downloaded_file or not os.path.exists(downloaded_file):
                mp3_files = sorted(audio_dir.glob('*.mp3'), key=os.path.getmtime, reverse=True)
                if mp3_files:
                    downloaded_file = str(mp3_files[0])

            if downloaded_file and os.path.exists(downloaded_file):
                # Rename the downloaded file with numeric prefix
                renamed_file = self.rename_with_prefix(Path(downloaded_file))
                title = renamed_file.stem
                # Remove prefix from title for display
                import re
                prefix_match = re.match(r'^(\d{2})_(.+)$', title)
                if prefix_match:
                    title = prefix_match.group(2)
                title = re.sub(r'\[.*?\]', '', title).strip()
                
                return {
                    'success': True,
                    'title': title,
                    'file': str(renamed_file)
                }
            else:
                return {
                    'success': False,
                    'error': 'Downloaded file not found'
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Download timeout (5 minutes exceeded)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def rename_with_prefix(self, file_path):
        """Rename a file with the next available numeric prefix"""
        audio_dir = file_path.parent
        
        # Get all existing MP3 files sorted by modification time
        existing_files = sorted(audio_dir.glob('*.mp3'), key=lambda f: f.stat().st_mtime)
        
        # Find the highest existing prefix
        import re
        max_prefix = -1
        for existing_file in existing_files:
            prefix_match = re.match(r'^(\d{2})_', existing_file.name)
            if prefix_match:
                prefix_num = int(prefix_match.group(1))
                max_prefix = max(max_prefix, prefix_num)
        
        # Next prefix
        next_prefix = max_prefix + 1
        prefix_str = f"{next_prefix:02d}"
        
        # Get the title from the file (remove extension)
        title = file_path.stem
        # Remove YouTube ID patterns
        title = re.sub(r'\[.*?\]', '', title).strip()
        
        # Create new filename
        new_name = f"{prefix_str}_{title}.mp3"
        new_path = audio_dir / new_name
        
        # Rename the file
        if file_path != new_path:
            # Handle case where target already exists
            counter = 1
            while new_path.exists() and new_path != file_path:
                new_name = f"{prefix_str}_{title}_{counter}.mp3"
                new_path = audio_dir / new_name
                counter += 1
            
            file_path.rename(new_path)
            print(f"Renamed downloaded file: {file_path.name} -> {new_name}")
        
        return new_path
    
    def regenerate_playlist(self):
        """Regenerate the playlist.json file"""
        try:
            # Import and call the playlist generator function
            import importlib.util
            spec = importlib.util.spec_from_file_location("generate_playlist", "generate_playlist.py")
            generate_playlist_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generate_playlist_module)
            generate_playlist_module.generate_playlist()
        except Exception as e:
            print(f"Error regenerating playlist: {e}")

    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, status_code, message):
        """Send error response"""
        self.send_json_response(status_code, {
            'success': False,
            'error': message
        })

    def log_message(self, format, *args):
        """Override to customize logging"""
        # Only log errors and important messages
        if '404' not in format % args:
            super().log_message(format, *args)

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if yt-dlp is installed
    try:
        subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: yt-dlp is not installed!")
        print("Please install it with: pip3 install yt-dlp")
        sys.exit(1)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print(f"Server running at {url}")
        print("Press Ctrl+C to stop the server")
        print("\nOpening browser...")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")

if __name__ == '__main__':
    main()
