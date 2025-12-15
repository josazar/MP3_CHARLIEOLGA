#!/usr/bin/env python3
"""
Script to rename all MP3 files in the audio folder with numbered prefixes.
"""
import os
from pathlib import Path

def rename_audio_files():
    audio_dir = Path('audio')
    
    if not audio_dir.exists():
        print("Audio directory not found.")
        return
    
    # Get all MP3 files
    mp3_files = sorted(audio_dir.glob('*.mp3'))
    
    if not mp3_files:
        print("No MP3 files found in audio/ directory")
        return
    
    print(f"Found {len(mp3_files)} MP3 files to rename:")
    print()
    
    # Rename files with numbered prefixes
    renamed_count = 0
    for index, mp3_file in enumerate(mp3_files):
        # Create new filename with zero-padded number prefix
        prefix = f"{index:02d}_"
        old_name = mp3_file.name
        
        # Check if already has a numbered prefix
        if old_name.startswith(f"{index:02d}_"):
            print(f"  {index:02d}. {old_name} (already has correct prefix, skipping)")
            continue
        
        # Create new filename
        new_name = prefix + old_name
        new_path = audio_dir / new_name
        
        # Check if target file already exists
        if new_path.exists() and new_path != mp3_file:
            print(f"  {index:02d}. {old_name} -> {new_name} (target exists, skipping)")
            continue
        
        try:
            mp3_file.rename(new_path)
            print(f"  {index:02d}. {old_name} -> {new_name} ✓")
            renamed_count += 1
        except Exception as e:
            print(f"  {index:02d}. {old_name} -> ERROR: {e}")
    
    print()
    print(f"Renamed {renamed_count} file(s).")
    
    # Regenerate playlist
    print("\nRegenerating playlist...")
    try:
        import generate_playlist
        generate_playlist.generate_playlist()
        print("✅ Playlist updated!")
    except Exception as e:
        print(f"Error updating playlist: {e}")

if __name__ == '__main__':
    rename_audio_files()

