from http.server import BaseHTTPRequestHandler
import json
import subprocess
import os
import sys

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            youtube_url = data.get('url', '')
            
            if not youtube_url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': 'No URL provided'
                }).encode())
                return
            
            # Note: yt-dlp needs to be installed in the Vercel environment
            # This is a serverless function, so we need to handle file storage differently
            
            # For Vercel, files can't be persisted to the filesystem
            # You would need to:
            # 1. Download to /tmp (temporary storage)
            # 2. Upload to a storage service (S3, Vercel Blob, etc.)
            # 3. Update playlist.json in the storage
            
            # For now, return a message that this requires additional setup
            self.send_response(501)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': 'Download feature requires storage setup. For now, please download locally and push to GitHub.',
                'instructions': [
                    '1. Run locally: python3 download_mp3.py "' + youtube_url + '"',
                    '2. Run: python3 generate_playlist.py',
                    '3. Commit and push: git add . && git commit -m "Add new song" && git push'
                ]
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'message': f'Error: {str(e)}'
            }).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

