# Vercel Deployment Guide

## Overview

This project can be deployed to Vercel, but there are **important limitations** regarding the Python download functionality.

## ⚠️ Important Limitations on Vercel

### What Works ✅
- Audio player interface (HTML/CSS/JS)
- Streaming and playing all uploaded MP3 files
- Responsive design and all player controls
- Automatic HTTPS and global CDN

### What Doesn't Work ❌
- **YouTube download feature** - Vercel serverless functions have limitations:
  1. **Read-only filesystem** - Can't save MP3 files permanently
  2. **Execution timeout** - 10 seconds (Hobby plan) / 60 seconds (Pro)
  3. **No persistent storage** - Files would need external storage (S3, Vercel Blob)
  4. **ffmpeg not included** - Required for MP3 conversion

## 🎯 Recommended Workflow

### For Vercel Production Deployment:

**Download and add songs locally, then deploy:**

1. **Download songs locally:**
   ```bash
   python3 download_mp3.py "YOUTUBE_URL"
   ```

2. **Update playlist:**
   ```bash
   python3 generate_playlist.py
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add new songs"
   git push
   ```

4. **Vercel auto-deploys** (1-2 minutes)

### For Local Development:

Use the full Python server with download capabilities:

```bash
python3 server.py
# Access at http://localhost:8000
```

## 🚀 Advanced: Enable Downloads on Vercel (Requires Setup)

If you really need the download feature in production, you'll need:

### Option 1: Vercel Blob Storage
```bash
npm i @vercel/blob
```
- Store MP3 files in Vercel Blob Storage
- Update playlist.json to reference blob URLs
- Requires Vercel Pro plan for larger files

### Option 2: External Storage (S3/Cloudflare R2)
- Download to `/tmp` in serverless function
- Upload to S3/R2 bucket
- Update playlist.json with CDN URLs
- More cost-effective for large files

### Option 3: Separate Backend
- Deploy Python backend to Railway/Render/Heroku
- Keep frontend on Vercel
- Configure CORS properly

## 📊 File Size Considerations

- Vercel has deployment size limits:
  - **Hobby plan**: 100MB per deployment
  - **Pro plan**: 500MB per deployment
- Your current project has **47 MP3 files**
- Consider using external storage if library grows large

## 🔧 Current Setup

The project includes:
- `api/download.py` - Serverless function (shows instructions)
- `requirements.txt` - Python dependencies
- `vercel.json` - Configuration with API routes

The API endpoint returns helpful instructions instead of actually downloading.

## 💡 Best Practice

**For most users, the recommended approach is:**
1. Manage songs locally
2. Push to GitHub when adding new content
3. Let Vercel auto-deploy
4. This keeps it simple, free, and reliable!

## 🆘 Need Help?

If you need the download feature to work in production, consider:
- Using a different hosting platform (Railway, Render, DigitalOcean)
- Setting up external storage
- Creating a separate backend service

