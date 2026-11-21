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
OUT = os.path.join(ROOT, "build", "ses", "parcalar2")
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

EXAGGERATION = 0.45   # sade, abartısız anlatım
CFG_WEIGHT = 0.50     # normal tempo
TEMPERATURE = 0.70
MAX_DENEME = 4
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


BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def sayi_yazi(n):
    if n == 0:
        return "sıfır"
    p = []
    b, n = divmod(n, 1000)
    if b:
        p.append("bin" if b == 1 else sayi_yazi(b) + " bin")
    y, n = divmod(n, 100)
    if y:
        p.append("yüz" if y == 1 else BIRLER[y] + " yüz")
    o, r = divmod(n, 10)
    p += [ONLAR[o], BIRLER[r]]
    return " ".join(x for x in p if x)


def rakamlari_yaz(s):
    s = re.sub(r"(\d)\.(\d{3})", r"\1\2", s)
    s = re.sub(r"(\d+),5", lambda m: sayi_yazi(int(m.group(1))) + " buçuk", s)
    return re.sub(r"\d+", lambda m: " " + sayi_yazi(int(m.group(0))) + " ", s)


def normalize(s):
    s = rakamlari_yaz(s)
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
        onceki = manifest.get(sid, {}).get("parcalar", [])
        for i, cumle in enumerate(cumleler):
            yol = os.path.join(OUT, f"{sid}_{i:02d}.wav")
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
                segs, _ = asr.transcribe(w16, language="tr", beam_size=3, word_timestamps=True)
                segs = list(segs)
                duyulan = " ".join(s.text for s in segs)
                skor = benzerlik(okunus(cumle), duyulan)
                # konuşmanın dışında kalan mırıltı/uğultuyu kelime sınırlarından kes
                kelimeler = [w for s in segs for w in (s.words or [])]
                if kelimeler:
                    a = max(0, int((kelimeler[0].start - 0.10) * tts.sr))
                    b = min(wav.shape[-1], int((kelimeler[-1].end + 0.18) * tts.sr))
                    wav = wav[:, a:b]
                sure = wav.shape[-1] / tts.sr
                beklenen = len(cumle) / 14.0
                if sure > beklenen * 1.9 or sure < beklenen * 0.45:
                    skor -= 0.2   # anormal uzunluk: tekrar/yutma şüphesi
                torchaudio.save(tmp, wav, tts.sr)
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
