#!/usr/bin/env python3
"""
Fix playlist.json with actual GitHub Release asset URLs
"""
import json
import subprocess
import sys

GITHUB_REPO = "josazar/MP3_CHARLIEOLGA"
RELEASE_TAG = "audio-files-v1.0"

def get_github_release_assets():
    """Get actual asset names from GitHub Release"""
    try:
        result = subprocess.run(
            ['gh', 'release', 'view', RELEASE_TAG, '--repo', GITHUB_REPO, '--json', 'assets'],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json as j
        data = j.loads(result.stdout)
        assets = data.get('assets', [])
        
        # Create mapping: original name -> GitHub asset name
        asset_map = {}
        for asset in assets:
            name = asset['name']
            # Try to extract the number prefix
            if '_' in name:
                prefix = name.split('_')[0]
                asset_map[prefix] = {
                    'name': name,
                    'url': asset['url']
                }
        
        return assets
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error fetching GitHub Release: {e}")
        sys.exit(1)

def fix_playlist():
    """Update playlist.json with correct URLs"""
    
    # Get GitHub assets
    print("🔍 Récupération des assets depuis GitHub Release...")
    assets = get_github_release_assets()
    
    if not assets:
        print("❌ No assets found in release")
        sys.exit(1)
    
    print(f"✅ Trouvé {len(assets)} fichiers")
    
    # Sort assets by name (they have number prefixes)
    assets.sort(key=lambda x: x['name'])
    
    # Create playlist
    playlist = []
    base_url = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}"
    
    for asset in assets:
        filename = asset['name']
        
        # Extract title (remove number prefix and .mp3)
        title = filename
        if '_' in filename:
            title = '_'.join(filename.split('_')[1:])
        title = title.replace('.mp3', '').replace('.', ' ')
        
        # Build URL with actual filename
        file_url = f"{base_url}/{filename}"
        
        playlist.append({
            "title": title,
            "file": file_url
        })
    
    # Write playlist.json
    with open('playlist.json', 'w', encoding='utf-8') as f:
        json.dump(playlist, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ playlist.json mis à jour avec {len(playlist)} pistes")
    print(f"\n📝 Exemple d'URL:")
    print(f"   {playlist[0]['file']}")
    
    return playlist

if __name__ == "__main__":
    print("🎵 Correction des URLs du playlist.json")
    print("=" * 70)
    
    playlist = fix_playlist()
    
    print("\n✅ TERMINÉ!")
    print("\nMaintenant, commit et push:")
    print("  git add playlist.json")
    print("  git commit -m 'Fix playlist URLs with actual GitHub Release asset names'")
    print("  git push")

