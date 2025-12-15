#!/usr/bin/env python3
"""
Script to upload MP3 files to GitHub Releases and update playlist.json
"""
import os
import json
import sys

GITHUB_REPO = "josazar/MP3_CHARLIEOLGA"
RELEASE_TAG = "audio-files-v1.0"
RELEASE_NAME = "Audio Files"

def get_audio_files():
    """Get all MP3 files from audio directory"""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        print(f"❌ Error: '{audio_dir}' directory not found")
        sys.exit(1)
    
    mp3_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    mp3_files.sort()
    return mp3_files

def generate_playlist_with_github_urls():
    """Generate playlist.json with GitHub Release URLs"""
    mp3_files = get_audio_files()
    
    playlist = []
    base_url = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}"
    
    for filename in mp3_files:
        # Remove number prefix and .mp3 extension for title
        title = filename
        if '_' in filename:
            title = '_'.join(filename.split('_')[1:])
        title = title.replace('.mp3', '')
        
        # URL encode the filename for GitHub
        from urllib.parse import quote
        encoded_filename = quote(filename)
        
        playlist.append({
            "title": title,
            "file": f"{base_url}/{encoded_filename}"
        })
    
    # Write playlist.json
    with open('playlist.json', 'w', encoding='utf-8') as f:
        json.dump(playlist, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated playlist.json with {len(playlist)} tracks")
    return playlist

def print_instructions():
    """Print instructions for creating the GitHub Release"""
    print("\n" + "="*70)
    print("📦 INSTRUCTIONS POUR CRÉER LA RELEASE GITHUB")
    print("="*70)
    print("\n🔹 ÉTAPE 1: Créer la Release sur GitHub")
    print("-" * 70)
    print(f"1. Va sur: https://github.com/{GITHUB_REPO}/releases/new")
    print(f"2. Tag version: {RELEASE_TAG}")
    print(f"3. Release title: {RELEASE_NAME}")
    print("4. Description: Audio files for the music player")
    print("\n🔹 ÉTAPE 2: Uploader les fichiers MP3")
    print("-" * 70)
    print("5. Fais glisser TOUS les fichiers du dossier 'audio/' dans la zone")
    print("   'Attach binaries' en bas de la page")
    print("6. Attends que tous les fichiers soient uploadés (238 MB)")
    print("7. Clique sur 'Publish release'")
    print("\n🔹 ÉTAPE 3: Vérification")
    print("-" * 70)
    print(f"8. Les URLs seront du type:")
    print(f"   {get_example_url()}")
    print("\n✅ Une fois la release publiée, reviens ici et tape 'done'")
    print("="*70 + "\n")

def get_example_url():
    """Get an example URL for the first MP3"""
    from urllib.parse import quote
    mp3_files = get_audio_files()
    if mp3_files:
        encoded = quote(mp3_files[0])
        return f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/{encoded}"
    return ""

def create_gh_cli_script():
    """Create a bash script to upload using GitHub CLI (if available)"""
    mp3_files = get_audio_files()
    
    script_content = f"""#!/bin/bash
# Script pour uploader automatiquement via GitHub CLI
# Nécessite: gh CLI (https://cli.github.com/)

echo "🚀 Création de la release GitHub..."

# Créer la release
gh release create {RELEASE_TAG} \\
  --repo {GITHUB_REPO} \\
  --title "{RELEASE_NAME}" \\
  --notes "Audio files for the music player" \\
"""
    
    # Add all MP3 files
    for mp3 in mp3_files:
        script_content += f'  "audio/{mp3}" \\\n'
    
    script_content = script_content.rstrip(" \\\n")
    script_content += "\n\necho \"✅ Release créée avec succès!\"\n"
    
    with open('upload_release.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('upload_release.sh', 0o755)
    print("✅ Script 'upload_release.sh' créé (pour GitHub CLI)")

if __name__ == "__main__":
    print("🎵 Configuration GitHub Releases pour les MP3")
    print("=" * 70)
    
    # Generate playlist with GitHub URLs
    playlist = generate_playlist_with_github_urls()
    
    # Create upload script for GitHub CLI
    create_gh_cli_script()
    
    # Print manual instructions
    print_instructions()
    
    print("💡 DEUX OPTIONS:")
    print("   A) Manuelle: Suis les instructions ci-dessus")
    print("   B) Automatique: Si tu as GitHub CLI installé, tape: ./upload_release.sh")
    print()

