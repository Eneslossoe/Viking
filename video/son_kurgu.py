"""Anlatımı videoyla birleştirir kısık müzik ve ortam sesleriyle ve SRT altyazı üretir.

Kullanım: python video/son_kurgu.py [ad]   (ad: sessiz | onizleme_s01 ...)
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SES = os.path.join(ROOT, "build", "ses")
CIKTI = os.path.join(ROOT, "cikti")
SR = 48000
DOSYA_ADI = "Ragnar_Zamaninda_Viking_Koylusu"


def anlatim(zaman, ad):
    parca = []
    for s in zaman["sahneler"]:
        yol = os.path.join(SES, "sahne", f"{s['sid']}.wav")
        n = int(round(s["sure"] * SR))
        if os.path.exists(yol) and not s.get("tahmini"):
            x, sr = sf.read(yol, dtype="float32")
            assert sr == SR
            x = x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))
        else:
            print("  ! ses yok, sessiz bırakıldı:", s["sid"])
            x = np.zeros(n, dtype=np.float32)
        parca.append(x)
    yol = os.path.join(SES, f"anlatim_{ad}.wav")
    sf.write(yol, np.concatenate(parca), SR)
    return yol


def zaman_fmt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def satirla(metin, genislik=42):
    kelimeler, satirlar, cur = metin.split(), [], ""
    for k in kelimeler:
        if cur and len(cur) + 1 + len(k) > genislik:
            satirlar.append(cur)
            cur = k
        else:
            cur = (cur + " " + k).strip()
    if cur:
        satirlar.append(cur)
    return satirlar


def altyazi(zaman, yol):
    kayit, no = [], 1
    for s in zaman["sahneler"]:
        for c in s["cumleler"]:
            satirlar = satirla(c["metin"])
            gruplar = [satirlar[i:i + 2] for i in range(0, len(satirlar), 2)]
            toplam_harf = sum(len(" ".join(g)) for g in gruplar)
            t = s["bas"] + c["bas"]
            sure = c["son"] - c["bas"]
            for g in gruplar:
                metin = "\n".join(g)
                d = sure * len(" ".join(g)) / max(1, toplam_harf)
                kayit.append(f"{no}\n{zaman_fmt(t)} --> {zaman_fmt(t + d - 0.02)}\n{metin}\n")
                no += 1
                t += d
    with open(yol, "w", encoding="utf-8") as f:
        f.write("\n".join(kayit))


def main():
    ad = sys.argv[1] if len(sys.argv) > 1 else "sessiz"
    os.makedirs(CIKTI, exist_ok=True)
    zaman = json.load(open(os.path.join(ROOT, "build", "video", f"{ad}_zaman.json")))
    a = anlatim(zaman, ad)
    v = os.path.join(ROOT, "build", "video", f"{ad}.mp4")
    hedef = os.path.join(CIKTI, f"{DOSYA_ADI}.mp4" if ad == "sessiz" else f"{ad}.mp4")
    muz = os.path.join(SES, f"muzik_{ad}.wav")
    efk = os.path.join(SES, f"efekt_{ad}.wav")
    # Anlatım -14 LUFS; müzik ve efektler çok kısık, konuşurken müzik ayrıca kısılır
    filtre = ("[0:a]loudnorm=I=-14:TP=-2:LRA=11,aresample=48000,asplit=2[ses][sc];"
              "[1:a]loudnorm=I=-30:LRA=11,aresample=48000[m0];"
              "[m0][sc]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=600[muz];"
              "[2:a]loudnorm=I=-27:LRA=15,aresample=48000[efk];"
              "[ses][muz][efk]amix=inputs=3:normalize=0:duration=first,"
              "alimiter=limit=0.89:level=disabled[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-i", muz, "-i", efk, "-i", v,
                    "-filter_complex", filtre,
                    "-map", "3:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", hedef], check=True)
    srt = os.path.splitext(hedef)[0] + ".srt"
    altyazi(zaman, srt)
    print("tamam:", hedef, srt)


if __name__ == "__main__":
    main()
