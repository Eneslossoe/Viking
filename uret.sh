#!/usr/bin/env bash
# Videoyu baştan sona üretir. Her adım kaldığı yerden devam eder.
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate
export HF_HUB_DISABLE_XET=1

python ses/seslendir.py      # 1. Cümle cümle Türkçe seslendirme (Chatterbox) + Whisper ile kontrol
python ses/birlestir.py      # 2. Sahne sesleri, sertleştirme (kalınlaştırma, EQ, kompresör)
python cizim/hazirla.py      # 3. Tüm çekimler: SVG -> PNG
python video/animasyon.py    # 4. Animasyon -> build/video/sessiz.mp4
python ses/muzik.py          # 5. Müzik ve ortam sesleri (kodla sentez)
python video/son_kurgu.py    # 6. Karışım + video + SRT altyazı -> cikti/
python cizim/kapak.py        # 7. Kapak görseli -> cikti/kapak_1280x720.jpg
python video/youtube_metin.py  # 8. Başlık, açıklama (bölüm zamanlarıyla), etiketler
