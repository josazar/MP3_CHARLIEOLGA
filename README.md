# Audio Player - YouTube MP3 Downloader & Player

A web-based audio player with playlist functionality for playing downloaded MP3 files from YouTube.

🌐 **Live Demo:** [Deploy on Vercel](#deployment-to-vercel)

## Features

- 🎵 Beautiful, modern web interface
- 📋 Automatic playlist generation
- ▶️ Play, pause, next, previous controls
- 🔊 Volume control
- ⏱️ Progress bar with time display
- 📱 Responsive design
- ☁️ Deployable to Vercel

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install yt-dlp certifi
   ```

2. **Download MP3 from YouTube (Easy Method):**
   ```bash
   python3 download_mp3.py "YOUTUBE_URL"
   ```
   
   This automatically downloads, converts to MP3, and updates the playlist!
   
   **Alternative (Manual):**
   ```bash
   SSL_CERT_FILE=$(python3 -m certifi) yt-dlp -x --audio-format mp3 --audio-quality 0 "YOUTUBE_URL"
   python3 generate_playlist.py
   ```

   The MP3 will be automatically saved to the `audio/` folder.

4. **Start the web server:**
   ```bash
   python3 server.py
   ```

   The player will open automatically in your browser at `http://localhost:8000`

## Usage

### Downloading New Tracks

**Option 1: Simple Script (Recommended)**
```bash
python3 download_mp3.py "https://www.youtube.com/watch?v=VIDEO_ID"
```
This downloads, converts, and updates the playlist automatically!

**Option 2: Web Interface**
1. Start the server: `python3 server.py`
2. Open `http://localhost:8000` in your browser
3. Paste YouTube URL and click "Export video to MP3"

**Option 3: Manual Command**
```bash
SSL_CERT_FILE=$(python3 -m certifi) yt-dlp -x --audio-format mp3 --audio-quality 0 "YOUTUBE_URL"
python3 generate_playlist.py
```

After downloading, refresh the browser to see new tracks.

### Player Controls

- **▶/⏸** - Play/Pause
- **⏮** - Previous track
- **⏭** - Next track
- **Progress bar** - Click to seek
- **Volume slider** - Adjust volume

## Project Structure

```
MP3_CHARLIEOLGA/
├── audio/              # MP3 files folder
├── index.html          # Web player interface
├── playlist.json       # Auto-generated playlist
├── download_mp3.py     # Simple download script (recommended!)
├── generate_playlist.py # Script to scan and generate playlist
├── server.py           # Simple HTTP server
└── README.md           # This file
```

## Deployment to Vercel

Deploy your audio player to the web with Vercel:

1. **Push your code to GitHub**
2. **Visit [Vercel](https://vercel.com)** and sign in
3. **Import your repository**
4. **Deploy!** 

Your player will be live at `https://your-project.vercel.app`

### Adding New Songs

MP3 files are hosted on GitHub Releases for better performance:

```bash
# 1. Download a song
python3 download_mp3.py "YOUTUBE_URL"

# 2. Upload to GitHub Releases
python3 upload_to_github_releases.py
./upload_release.sh

# 3. Push changes
git push
```

Vercel auto-deploys on every push!

## Notes

- Make sure `ffmpeg` is installed for audio conversion (local development only)
- The player automatically loads all MP3 files from the `audio/` folder
- Run `generate_playlist.py` after adding new MP3 files to update the playlist
- For production deployment on Vercel, manage your MP3 files locally and push to Git

