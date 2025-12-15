#!/bin/bash
# Script pour uploader automatiquement via GitHub CLI
# Nécessite: gh CLI (https://cli.github.com/)

echo "🚀 Création de la release GitHub..."

# Créer la release
gh release create audio-files-v1.0 \
  --repo josazar/MP3_CHARLIEOLGA \
  --title "Audio Files" \
  --notes "Audio files for the music player" \
  "audio/00_Bongo Cat - APT. (Cover Version) 🎧.mp3" \
  "audio/01_Bongo Cat - Golden (Cover Version) 🎧.mp3" \
  "audio/02_Bongo Cat - Soda Pop (Cover Version) 🎧.mp3" \
  "audio/03_＂Briller＂ ｜ KPop Demon Hunters - Clip VF Restaurée avec Paroles.mp3" \
  "audio/04_MV Kpop Demon Hunters - How It’s Done VF.mp3" \
  "audio/05_＂Libres＂ - KPOP Demon Hunters - ＂Free＂ VF.mp3" \
  "audio/06_Miel Pops Remix.mp3" \
  "audio/07_Minecraft Le Film - Lava Chicken (Version Française).mp3" \
  "audio/08_A Minecraft Movie - Lava Chicken Song (COVER).mp3" \
  "audio/09_I Feel Alive (from “A Minecraft Movie”).mp3" \
  "audio/10_When I'm Gone (＂A Minecraft Movie＂ Version).mp3" \
  "audio/11_Change Song.mp3" \
  "audio/12_Zero to Hero.mp3" \
  "audio/13_Could This Be Love？.mp3" \
  "audio/14_Just Can't Get Enough (from ＂A Minecraft Movie＂) (Instrumental Version).mp3" \
  "audio/15_Steve's Lava Chicken.mp3" \
  "audio/16_Birthday Rap.mp3" \
  "audio/17_Ode to Dennis.mp3" \
  "audio/18_Minecraft (from ＂A Minecraft Movie＂).mp3" \
  "audio/19_Mintage.mp3" \
  "audio/20_Midport Village.mp3" \
  "audio/21_Day to Night.mp3" \
  "audio/22_Steve in The Nether.mp3" \
  "audio/23_Chicken Fight Club.mp3" \
  "audio/24_I Need a Win, Man.mp3" \
  "audio/25_I'm Coming With ⧸ Minecraft.mp3" \
  "audio/26_Nitwit Crosses and Steve Finds ⧸ Minecraft.mp3" \
  "audio/27_Woodland Mansion Planning.mp3" \
  "audio/28_Steve vs. Malgosha.mp3" \
  "audio/29_Piglins Attack.mp3" \
  "audio/30_Heroic Henry ⧸ Minecraft.mp3" \
  "audio/31_Let's Go Fight Some Pigs.mp3" \
  "audio/32_Run from the Great Hog.mp3" \
  "audio/33_Back in The Nether.mp3" \
  "audio/34_Steve's Lava Chicken (Extended Version).mp3" \
  "audio/35_Birthday Rap (Extended Version).mp3" \
  "audio/36_Ode to Dennis (Extended Version).mp3" \
  "audio/37_Welcome to Steve's!.mp3" \
  "audio/38_GIMS - CIEL (Official Lyrics Video).mp3" \
  "audio/39_Best Tavern Music ckd2.mp3" \
  "audio/40_113, Rim'K - Tonton du bled (Clip officiel).mp3" \
  "audio/41_OrelSan - Basique.mp3" \
  "audio/42_OrelSan - Ailleurs.mp3" \
  "audio/43_Stromae - Alors on danse (Official Video).mp3" \
  "audio/44_Stromae - Santé (Live From The Tonight Show Starring Jimmy Fallon).mp3" \
  "audio/45_Will Smith - Men In Black (Official Video).mp3" \
  "audio/46_Ne parlons pas de Bruno (De ＂Encanto： La fantastique famille Madrigal＂).mp3"

echo "✅ Release créée avec succès!"
