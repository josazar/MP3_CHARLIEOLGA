"""
Vercel Serverless Function - Simplified version
Due to Vercel limitations (yt-dlp too large), this provides instructions
and a webhook endpoint for updates
"""
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """Handle download request"""
        try:
            # Read request
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                youtube_url = data.get('url', '').strip()
            else:
                youtube_url = ''
            
            if not youtube_url:
                self.send_error_response(400, 'No URL provided')
                return
            
            # Return instructions (yt-dlp can't run on Vercel due to size)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                'success': False,
                'message': '⚠️ Direct download not available on Vercel (size limitations)',
                'instructions': [
                    '📋 To add this song, use the local script:',
                    '',
                    f'1. python3 download_mp3.py "{youtube_url}"',
                    '2. python3 generate_playlist.py',
                    '3. gh release delete audio-files-v1.0 --yes',
                    '4. ./upload_release.sh',
                    '5. git add playlist.json && git commit -m "Add new song" && git push',
                    '',
                    '✨ Or use the automated script: python3 upload_to_github_releases.py && ./upload_release.sh'
                ],
                'alternative': 'For now, please download locally and push to GitHub. The playlist will update automatically!',
                'url': youtube_url
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
            
        except Exception as e:
            self.send_error_response(500, f'Error: {str(e)}')
    
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {
            'status': 'ok',
            'message': 'API is running',
            'note': 'Direct YouTube download not available due to Vercel size limits. Use local scripts instead.'
        }
        
        self.wfile.write(json.dumps(response).encode())
    
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
