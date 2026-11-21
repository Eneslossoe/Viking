"""Senaryodaki her cümleyi yerel Chatterbox (Türkçe) modeliyle seslendirir.

Her cümle üretildikten sonra faster-whisper ile geri dinlenir; metinle
yeterince örtüşmüyorsa (yanlış okuma, yutulan kelime, tekrar) yeniden üretilir.
Çıktılar build/ses/parcalar/ altına yazılır; yarıda kalırsa kaldığı yerden devam eder.

Kullanım:  python ses/seslendir.py [sahne_id ...]
"""
import difflib
import json
import os
import re
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import torch
import torchaudio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENARYO = os.path.join(ROOT, "senaryo", "sahneler.json")
OUT = os.path.join(ROOT, "build", "ses", "parcalar")
REF = os.path.join(ROOT, ".models", "tr_m.flac")

# Sadece seslendirmede kullanılan okunuş düzeltmeleri (altyazı orijinal yazımı korur)
OKUNUS = {
    "thrall'lar": "tral'lar",
    "thrall": "tral",
    "blót": "blot",
    "laugardagr": "lavgardagır",
    "Hnefatafl": "Hınefatafıl",
    "skyr": "skir",
    "nattmal": "natmal",
    "Lodbrok": "Lodbrok",
}

EXAGGERATION = 0.55   # biraz daha dramatik vurgu
CFG_WEIGHT = 0.40     # daha ağır, oturaklı tempo
TEMPERATURE = 0.75
MAX_DENEME = 3
ESIK = 0.86           # whisper benzerlik eşiği


def cumlelere_bol(metin):
    parcalar = re.split(r"(?<=[.!?])\s+", metin.strip())
    sonuc = []
    for p in parcalar:
        p = p.strip()
        if not p:
            continue
        # çok kısa cümleleri bir sonrakine yapıştır (model kısa metinde tökezleyebiliyor)
        if sonuc and len(sonuc[-1]) < 22:
            sonuc[-1] = sonuc[-1] + " " + p
        else:
            sonuc.append(p)
    if len(sonuc) > 1 and len(sonuc[-1]) < 22:
        son = sonuc.pop()
        sonuc[-1] = sonuc[-1] + " " + son
    return sonuc


def okunus(metin):
    for k, v in OKUNUS.items():
        metin = metin.replace(k, v)
    return metin


def normalize(s):
    s = s.lower().replace("i̇", "i")
    s = re.sub(r"[^a-zçğıöşüâîû0-9 ]", " ", s)
    return " ".join(s.split())


def benzerlik(a, b):
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def main():
    torch.set_num_threads(int(os.environ.get("TTS_THREADS", "4")))
    os.makedirs(OUT, exist_ok=True)
    data = json.load(open(SENARYO, encoding="utf-8"))
    secili = set(sys.argv[1:])

    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    from faster_whisper import WhisperModel

    tts = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    asr = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)

    manifest_yolu = os.path.join(OUT, "manifest.json")
    manifest = json.load(open(manifest_yolu)) if os.path.exists(manifest_yolu) else {}

    for sahne in data["sahneler"]:
        sid = sahne["id"]
        if secili and sid not in secili:
            continue
        cumleler = cumlelere_bol(sahne["metin"])
        kayitlar = []
        for i, cumle in enumerate(cumleler):
            yol = os.path.join(OUT, f"{sid}_{i:02d}.wav")
            onceki = manifest.get(sid, {}).get("parcalar", [])
            if os.path.exists(yol) and i < len(onceki) and onceki[i]["metin"] == cumle:
                kayitlar.append(onceki[i])
                continue
            en_iyi = None
            for deneme in range(MAX_DENEME):
                torch.manual_seed(1000 + i * 7 + deneme * 101)
                t0 = time.time()
                wav = tts.generate(
                    okunus(cumle), language_id="tr", audio_prompt_path=REF,
                    exaggeration=EXAGGERATION, cfg_weight=CFG_WEIGHT,
                    temperature=TEMPERATURE,
                )
                tmp = yol + ".tmp.wav"
                torchaudio.save(tmp, wav, tts.sr)
                w16 = torchaudio.functional.resample(wav, tts.sr, 16000)[0].numpy().astype("float32")
                segs, _ = asr.transcribe(w16, language="tr", beam_size=3)
                duyulan = " ".join(s.text for s in segs)
                skor = benzerlik(okunus(cumle), duyulan)
                sure = wav.shape[-1] / tts.sr
                print(f"[{sid} {i+1}/{len(cumleler)} d{deneme+1}] skor={skor:.2f} "
                      f"{sure:.1f}s ({time.time()-t0:.0f}s)", flush=True)
                if en_iyi is None or skor > en_iyi[0]:
                    if en_iyi:
                        os.remove(en_iyi[1])
                    best_tmp = yol + f".best.wav"
                    os.replace(tmp, best_tmp)
                    en_iyi = (skor, best_tmp, duyulan, sure)
                else:
                    os.remove(tmp)
                if skor >= ESIK:
                    break
            os.replace(en_iyi[1], yol)
            if en_iyi[0] < ESIK:
                print(f"  ! düşük skor, en iyisi tutuldu: {cumle!r} -> {en_iyi[2]!r}", flush=True)
            kayitlar.append({"metin": cumle, "dosya": os.path.basename(yol),
                             "sure": en_iyi[3], "skor": round(en_iyi[0], 3)})
            manifest[sid] = {"parcalar": kayitlar}
            json.dump(manifest, open(manifest_yolu, "w"), ensure_ascii=False, indent=1)
        manifest[sid] = {"parcalar": kayitlar}
        json.dump(manifest, open(manifest_yolu, "w"), ensure_ascii=False, indent=1)
    print("BITTI", flush=True)


if __name__ == "__main__":
    main()
