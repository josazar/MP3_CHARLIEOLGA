"""
Vercel Serverless Function - Audio Proxy
Proxies audio files from GitHub releases with CORS headers
"""
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import ssl

# Try to use certifi for SSL certificates, fallback to unverified context if not available
try:
    import certifi
    import ssl
    ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    # If certifi is not available, create an unverified context (less secure but works)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

class handler(BaseHTTPRequestHandler):
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Range')
        self.send_header('Access-Control-Expose-Headers', 'Content-Length, Content-Range, Accept-Ranges')
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Proxy audio file from GitHub"""
        try:
            # Get URL from query parameter
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            url = query_params.get('url', [None])[0]
            
            if not url:
                self.send_error_response(400, 'Missing url parameter')
                return
            
            # Validate that URL is from GitHub releases
            if 'github.com' not in url or '/releases/download/' not in url:
                self.send_error_response(400, 'Invalid URL. Must be a GitHub release download URL')
                return
            
            # Get Range header for partial content support (for seeking)
            range_header = self.headers.get('Range', '')
            
            # Create request to GitHub
            req = urllib.request.Request(url)
            
            # Forward Range header if present
            if range_header:
                req.add_header('Range', range_header)
            
            # Fetch the file
            try:
                # Set a timeout and use SSL context
                response = urllib.request.urlopen(req, timeout=30, context=ssl_context)
                
                # Get status code
                status_code = response.getcode()
                
                # Get headers from GitHub response
                content_type = response.headers.get('Content-Type', 'audio/mpeg')
                if not content_type or content_type == 'application/octet-stream':
                    # Try to determine from URL
                    if url.endswith('.mp3'):
                        content_type = 'audio/mpeg'
                    else:
                        content_type = 'audio/mpeg'  # Default to MP3
                
                content_length = response.headers.get('Content-Length')
                content_range = response.headers.get('Content-Range')
                accept_ranges = response.headers.get('Accept-Ranges', 'bytes')
                
                # Send response headers
                if status_code == 206:  # Partial content
                    self.send_response(206)
                else:
                    self.send_response(200)
                
                self.send_header('Content-Type', content_type)
                self.send_cors_headers()
                
                if content_length:
                    self.send_header('Content-Length', content_length)
                if content_range:
                    self.send_header('Content-Range', content_range)
                self.send_header('Accept-Ranges', accept_ranges)
                self.send_header('Cache-Control', 'public, max-age=31536000')
                
                self.end_headers()
                
                # Stream the file in chunks
                chunk_size = 8192
                try:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                finally:
                    response.close()
                        
            except urllib.error.HTTPError as e:
                self.send_error_response(e.code, f'Error fetching file: {e.reason}')
            except Exception as e:
                self.send_error_response(500, f'Error: {str(e)}')
                
        except Exception as e:
            self.send_error_response(500, f'Error: {str(e)}')
    
    def send_error_response(self, code, message):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            'error': message
        }).encode())

