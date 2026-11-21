"""Cümle parçalarını sahne sahne birleştirir, sesi sertleştirir ve zamanlamaları yazar.

Çıktılar:
  build/ses/sahne/<sid>.wav       işlenmiş anlatım (48 kHz mono)
  build/ses/zamanlama.json        her sahnenin süresi ve cümle zamanları (altyazı için)
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARCA = os.path.join(ROOT, "build", "ses", "parcalar")
SAHNE = os.path.join(ROOT, "build", "ses", "sahne")
SR = 48000

BAS_BOSLUK = 0.35
SON_BOSLUK = 0.80

# Sert, tok anlatıcı: hafif kalınlaştırma + gövde + netlik + kompresör + yükseklik normalizasyonu
SES_ZINCIRI = (
    "rubberband=pitch=0.93,"
    "highpass=f=65,"
    "equalizer=f=140:t=q:w=1.0:g=3.5,"
    "equalizer=f=420:t=q:w=1.2:g=-2,"
    "equalizer=f=3200:t=q:w=1.0:g=2.5,"
    "acompressor=threshold=-20dB:ratio=3.5:attack=4:release=90:makeup=2,"
    "aecho=0.85:0.4:28:0.08,"
    "loudnorm=I=-16:TP=-1.5:LRA=9"
)


def kirp(x, sr, esik_db=-42, pay=0.04):
    env = np.abs(x)
    esik = 10 ** (esik_db / 20) * max(env.max(), 1e-6)
    idx = np.where(env > esik)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pay * sr))
    b = min(len(x), idx[-1] + int(pay * sr * 2))
    return x[a:b]


def ara_bosluk(metin):
    if metin.endswith("?"):
        return 0.60
    if metin.endswith(":"):
        return 0.45
    return 0.42


def isle(giris, cikis):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", giris, "-af", SES_ZINCIRI,
         "-ar", str(SR), "-ac", "1", cikis],
        check=True,
    )


def main():
    os.makedirs(SAHNE, exist_ok=True)
    manifest = json.load(open(os.path.join(PARCA, "manifest.json"), encoding="utf-8"))
    senaryo = json.load(open(os.path.join(ROOT, "senaryo", "sahneler.json"), encoding="utf-8"))
    secili = set(sys.argv[1:])
    zaman_yolu = os.path.join(ROOT, "build", "ses", "zamanlama.json")
    zamanlama = json.load(open(zaman_yolu)) if os.path.exists(zaman_yolu) else {}

    for sahne in senaryo["sahneler"]:
        sid = sahne["id"]
        if sid not in manifest or (secili and sid not in secili):
            continue
        parcalar = manifest[sid]["parcalar"]
        sesler, cumleler = [], []
        t = BAS_BOSLUK
        sesler.append(np.zeros(int(BAS_BOSLUK * SR), dtype=np.float32))
        for j, p in enumerate(parcalar):
            x, sr = sf.read(os.path.join(PARCA, p["dosya"]), dtype="float32")
            if x.ndim > 1:
                x = x.mean(axis=1)
            if sr != SR:
                import soxr
                x = soxr.resample(x, sr, SR)
            x = kirp(x, SR)
            sesler.append(x)
            cumleler.append({"metin": p["metin"], "bas": round(t, 3), "son": round(t + len(x) / SR, 3)})
            t += len(x) / SR
            bosluk = ara_bosluk(p["metin"]) if j < len(parcalar) - 1 else SON_BOSLUK
            sesler.append(np.zeros(int(bosluk * SR), dtype=np.float32))
            t += bosluk
        ham = np.concatenate(sesler)
        ham_yol = os.path.join(SAHNE, f"{sid}.ham.wav")
        sf.write(ham_yol, ham, SR)
        isle(ham_yol, os.path.join(SAHNE, f"{sid}.wav"))
        os.remove(ham_yol)
        zamanlama[sid] = {"sure": round(len(ham) / SR, 3), "cumleler": cumleler}
        print(f"{sid}: {len(ham)/SR:.1f}s", flush=True)

    json.dump(zamanlama, open(zaman_yolu, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
