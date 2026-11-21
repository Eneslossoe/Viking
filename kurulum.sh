#!/usr/bin/env bash
# Tek seferlik kurulum (Linux). Gerekenler: python3, node + playwright (chromium), ffmpeg (rubberband ile).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install chatterbox-tts==0.1.7 faster-whisper "setuptools<81"
mkdir -p .models
# Chatterbox'ın Türkçe erkek referans sesi (demo istemi)
curl -sL -o .models/tr_m.flac https://storage.googleapis.com/chatterbox-demo-samples/mtl_prompts/tr_m.flac
mkdir -p cizim/fontlar   # Cinzel ve Nunito (Google Fonts, OFL) bu klasörde
