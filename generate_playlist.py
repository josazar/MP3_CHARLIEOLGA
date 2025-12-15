#!/usr/bin/env python3
"""
Script to scan the audio folder and generate a playlist.json file
for the web audio player. Also renames all MP3 files with numeric prefixes.
"""
import os
import json
import re
from pathlib import Path

def rename_files_with_prefixes(audio_dir):
    """Rename all MP3 files with numeric prefixes (00, 01, 02, etc.)"""
    # Get all MP3 files, sorted by modification time (oldest first)
    mp3_files = sorted(audio_dir.glob('*.mp3'), key=lambda f: f.stat().st_mtime)
    
    if not mp3_files:
        return []
    
    renamed_files = []
    
    for index, mp3_file in enumerate(mp3_files):
        # Generate prefix (00, 01, 02, etc.)
        prefix = f"{index:02d}"
        
        # Get the current filename without extension
        current_name = mp3_file.stem
        
        # Check if file already has a numeric prefix
        prefix_match = re.match(r'^(\d{2})_(.+)$', current_name)
        if prefix_match:
            # File already has prefix, extract the actual title
            actual_title = prefix_match.group(2)
        else:
            # No prefix, use the whole name as title
            actual_title = current_name
        
        # Clean up title (remove YouTube ID patterns like [video_id])
        actual_title = re.sub(r'\[.*?\]', '', actual_title).strip()
        
        # Create new filename with prefix
        new_name = f"{prefix}_{actual_title}.mp3"
        new_path = audio_dir / new_name
        
        # Only rename if the name is different
        if mp3_file.name != new_name:
            # Check if target file already exists
            if new_path.exists() and new_path != mp3_file:
                # If it's a different file, we need to handle this
                # For now, add a suffix to avoid conflicts
                counter = 1
                while new_path.exists():
                    new_name = f"{prefix}_{actual_title}_{counter}.mp3"
                    new_path = audio_dir / new_name
                    counter += 1
            
            try:
                mp3_file.rename(new_path)
                print(f"Renamed: {mp3_file.name} -> {new_name}")
            except Exception as e:
                print(f"Error renaming {mp3_file.name}: {e}")
                new_path = mp3_file  # Use original file if rename fails
        
        renamed_files.append(new_path)
    
    return renamed_files

def generate_playlist():
    audio_dir = Path('audio')
    playlist = []
    
    if not audio_dir.exists():
        print("Audio directory not found. Creating it...")
        audio_dir.mkdir()
        return
    
    # First, rename all files with numeric prefixes
    print("Renaming files with numeric prefixes...")
    mp3_files = rename_files_with_prefixes(audio_dir)
    
    # If rename_files_with_prefixes didn't return files, get them again
    if not mp3_files:
        mp3_files = sorted(audio_dir.glob('*.mp3'), key=lambda f: f.stat().st_mtime)
    
    if not mp3_files:
        print("No MP3 files found in audio/ directory")
        return
    
    # Sort by filename (which now includes numeric prefix)
    mp3_files = sorted(mp3_files, key=lambda f: f.name)
    
    for mp3_file in mp3_files:
        # Extract title from filename
        title = mp3_file.stem
        
        # Remove numeric prefix if present (format: 00_Title)
        prefix_match = re.match(r'^(\d{2})_(.+)$', title)
        if prefix_match:
            title = prefix_match.group(2)
        
        # Remove common YouTube patterns like [video_id]
        title = re.sub(r'\[.*?\]', '', title).strip()
        
        playlist.append({
            'src': f'audio/{mp3_file.name}',
            'title': title
        })
    
    # Write playlist.json
    with open('playlist.json', 'w', encoding='utf-8') as f:
        json.dump(playlist, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated playlist.json with {len(playlist)} tracks:")
    for i, track in enumerate(playlist, 1):
        print(f"  {i}. {track['title']}")

if __name__ == '__main__':
    generate_playlist()

