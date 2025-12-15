#!/usr/bin/env python3
"""
Simple script to download YouTube videos as MP3.
Usage: python3 download_mp3.py "YOUTUBE_URL"
"""
import sys
import subprocess
import os
from pathlib import Path

def download_mp3(url):
    """Download YouTube video and convert to MP3"""
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
    
    print(f"Downloading: {url}")
    print("This may take a moment...")
    
    # Run yt-dlp
    try:
        result = subprocess.run(cmd, env=env, check=True)
        print("\n✅ Download complete!")
        
        # Regenerate playlist
        print("Updating playlist...")
        import generate_playlist
        generate_playlist.generate_playlist()
        print("✅ Playlist updated!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Download failed")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 download_mp3.py 'YOUTUBE_URL'")
        print("\nExample:")
        print("  python3 download_mp3.py 'https://www.youtube.com/watch?v=pxISmahJ-4A'")
        sys.exit(1)
    
    url = sys.argv[1]
    download_mp3(url)

