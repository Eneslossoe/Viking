"""Dikey (1080x1920) Reels/Shorts videosu: kısa metin, aynı ses, mevcut çizimler,
kelime kelime yanan büyük altyazı, kısık müzik ve ortam sesleri.

Kullanım: python reels/reels.py [ses|montaj|render|mix]   (boş: hepsi)
Çıktı   : cikti/Reels_Viking_Koylusu.mp4
"""
import difflib
import json
import math
import os
import subprocess
import sys
from multiprocessing import Process

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "ses"))
sys.path.insert(0, os.path.join(ROOT, "video"))
import seslendir as S  # noqa: E402

B = os.path.join(ROOT, "build", "reels")
SES_DIR = os.path.join(B, "ses")
SENARYO = json.load(open(os.path.join(ROOT, "reels", "reels.json"), encoding="utf-8"))
CIKTI = os.path.join(ROOT, "cikti", "Reels_Viking_Koylusu.mp4")
SR = 48000
FPS = 30
W, H = 1080, 1920
PY0, PY1 = 450, 1330          # çizim paneli
PW, PH = W, PY1 - PY0
ALT_Y = 1450                  # altyazı merkez
BAS = 0.25
ARA_CUMLE = 0.28
ARA_SATIR = 0.38
XF = 0.30
ISCI = int(os.environ.get("ISCI", "4"))
FONT = os.path.join(ROOT, "cizim", "fontlar")


# ------------------------------------------------------------------ 1. seslendirme
def ses():
    import torch
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    from faster_whisper import WhisperModel

    torch.set_num_threads(4)
    os.makedirs(SES_DIR, exist_ok=True)
    man_yol = os.path.join(SES_DIR, "manifest.json")
    man = json.load(open(man_yol)) if os.path.exists(man_yol) else {}
    tts = asr = None
    for li, satir in enumerate(SENARYO["satirlar"]):
        for ci, cumle in enumerate(S.cumlelere_bol(satir["metin"])):
            key = f"l{li:02d}_c{ci}"
            yol = os.path.join(SES_DIR, key + ".wav")
            if key in man and man[key]["metin"] == cumle and os.path.exists(yol):
                continue
            if tts is None:
                tts = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
                asr = WhisperModel(S.ASR_MODEL, device="cpu", compute_type="int8", cpu_threads=4)
            en = None
            for d in range(S.MAX_DENEME):
                torch.manual_seed(2000 + li * 13 + ci * 5 + d * 101)
                wav = tts.generate(S.okunus(cumle), language_id="tr", audio_prompt_path=S.REF,
                                   exaggeration=S.EXAGGERATION, cfg_weight=S.CFG_WEIGHT,
                                   temperature=S.TEMPERATURE)
                w16 = torchaudio.functional.resample(wav, tts.sr, 16000)[0].numpy().astype("float32")
                segs = list(asr.transcribe(w16, language="tr", beam_size=5, word_timestamps=True)[0])
                duy = " ".join(s.text for s in segs)
                sk = S.benzerlik(S.okunus(cumle), duy)
                kel = [w for s in segs for w in (s.words or [])]
                a = max(0.0, kel[0].start - 0.10) if kel else 0.0
                b = min(wav.shape[-1] / tts.sr, kel[-1].end + 0.18) if kel else wav.shape[-1] / tts.sr
                wav = wav[:, int(a * tts.sr):int(b * tts.sr)]
                kelimeler = [{"w": w.word.strip(), "s": round(w.start - a, 3), "e": round(w.end - a, 3)} for w in kel]
                beklenen = len(cumle) / 14.0
                if not (beklenen * 0.45 < b - a < beklenen * 1.9):
                    sk -= 0.2
                print(f"[{key} d{d+1}] skor={sk:.2f} {b-a:.1f}s  {duy.strip()}", flush=True)
                if en is None or sk > en[0]:
                    en = (sk, wav, kelimeler)
                if sk >= S.ESIK:
                    break
            torchaudio.save(yol, en[1], tts.sr)
            if en[0] < S.ESIK:
                print(f"  ! düşük skor: {cumle}", flush=True)
            man[key] = {"metin": cumle, "skor": round(en[0], 3), "kelimeler": en[2]}
            json.dump(man, open(man_yol, "w"), ensure_ascii=False, indent=1)
    print("ses tamam", flush=True)


# ------------------------------------------------------------------ 2. montaj + kelime zamanları
def hizala(metin, kelimeler, t0, sure):
    """Senaryodaki her kelimeye, Whisper kelime zamanlarından bir başlangıç/bitiş verir."""
    gor = metin.split()
    gt = [S.normalize(w) or "_" for w in gor]
    wt, ws = [], []
    for k in kelimeler:
        parca = S.normalize(k["w"]).split() or ["_"]
        d = (k["e"] - k["s"]) / len(parca)
        for j, p in enumerate(parca):
            wt.append(p)
            ws.append((k["s"] + j * d, k["s"] + (j + 1) * d))
    zam = [None] * len(gor)
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, gt, wt, autojunk=False).get_opcodes():
        if op == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                zam[i] = ws[j]
        elif op == "replace":
            a, b = ws[j1][0], ws[j2 - 1][1]
            uz = [len(g) for g in gt[i1:i2]]
            top, acc = sum(uz), 0
            for i, u in zip(range(i1, i2), uz):
                zam[i] = (a + (b - a) * acc / top, a + (b - a) * (acc + u) / top)
                acc += u
    # boş kalanları komşulardan doldur
    for i in range(len(zam)):
        if zam[i] is None:
            onc = zam[i - 1][1] if i > 0 and zam[i - 1] else 0.0
            snr = next((z[0] for z in zam[i + 1:] if z), sure)
            zam[i] = (onc, max(onc, min(snr, onc + 0.25)))
    return [{"w": g, "s": round(t0 + z[0], 3), "e": round(t0 + z[1], 3)} for g, z in zip(gor, zam)]


def montaj():
    import soxr
    man = json.load(open(os.path.join(SES_DIR, "manifest.json")))
    parca = [np.zeros(int(BAS * SR), dtype=np.float32)]
    t = BAS
    satirlar = []
    for li, satir in enumerate(SENARYO["satirlar"]):
        cumleler = S.cumlelere_bol(satir["metin"])
        kayit = []
        for ci, cumle in enumerate(cumleler):
            key = f"l{li:02d}_c{ci}"
            x, sr = sf.read(os.path.join(SES_DIR, key + ".wav"), dtype="float32")
            x = soxr.resample(x, sr, SR) if sr != SR else x
            sure = len(x) / SR
            kayit.append({"metin": cumle, "bas": round(t, 3), "son": round(t + sure, 3),
                          "kelimeler": hizala(cumle, man[key]["kelimeler"], t, sure)})
            parca.append(x)
            t += sure
            bosluk = ARA_CUMLE if ci < len(cumleler) - 1 else ARA_SATIR
            parca.append(np.zeros(int(bosluk * SR), dtype=np.float32))
            t += bosluk
        satirlar.append({"cumleler": kayit, "cekimler": satir["cekimler"]})
    ham = os.path.join(B, "anlatim_ham.wav")
    sf.write(ham, np.concatenate(parca), SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ham, "-af",
                    "highpass=f=80,acompressor=threshold=-24dB:ratio=2:attack=15:release=200,loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", str(SR), "-ac", "1", os.path.join(B, "anlatim.wav")], check=True)
    anlatim_son = t
    sk = SENARYO["son_kart"]
    toplam = anlatim_son + sk["sure"]
    # çekim zaman çizelgesi
    seg = []
    for satir in satirlar:
        for c in satir["cekimler"]:
            idx = min(c.get("cumle", 0), len(satir["cumleler"]) - 1)
            bas = satir["cumleler"][idx]["bas"] - 0.15
            seg.append({**c, "bas": round(max(0.0, bas), 3)})
    seg[0]["bas"] = 0.0
    seg.append({"sid": sk["sid"], "k": sk["k"], "x": sk["x"], "bas": round(anlatim_son - 0.1, 3), "son_kart": True})
    for i, s in enumerate(seg):
        s["son"] = seg[i + 1]["bas"] if i + 1 < len(seg) else toplam
    json.dump({"toplam": round(toplam, 3), "anlatim_son": round(anlatim_son, 3), "satirlar": satirlar,
               "segmentler": seg}, open(os.path.join(B, "zaman.json"), "w"), ensure_ascii=False, indent=1)
    print(f"montaj: anlatım {anlatim_son:.1f}s, toplam {toplam:.1f}s", flush=True)


# ------------------------------------------------------------------ 3. görüntü
def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def sayfalar(zaman):
    """Altyazıyı 1-2 satırlık sayfalara böler (en fazla 4 kelime / 24 harf)."""
    out = []
    for satir in zaman["satirlar"]:
        for c in satir["cumleler"]:
            cur = []
            for w in c["kelimeler"]:
                metin = " ".join(x["w"] for x in cur + [w])
                if cur and (len(cur) >= 4 or len(metin) > 24):
                    out.append(cur)
                    cur = []
                cur.append(w)
                if w["w"][-1] in ",.?!:":
                    out.append(cur)
                    cur = []
            if cur:
                out.append(cur)
    for i, p in enumerate(out):
        bas = p[0]["s"] - 0.05
        son = out[i + 1][0]["s"] - 0.05 if i + 1 < len(out) else zaman["anlatim_son"]
        out[i] = {"kelimeler": p, "bas": bas, "son": son}
    return out


class Kurgu:
    def __init__(self):
        from PIL import Image, ImageDraw, ImageFont
        import animasyon as A
        self.Image, self.ImageDraw, self.A = Image, ImageDraw, A
        A.OW, A.OH = PW, PH          # kar/yağmur paneli doldursun
        self.zaman = json.load(open(os.path.join(B, "zaman.json")))
        self.plan = json.load(open(os.path.join(ROOT, "build", "kare", "plan.json")))
        self.seg = self.zaman["segmentler"]
        self.sayfa = sayfalar(self.zaman)
        self.f_alt = {s: ImageFont.truetype(os.path.join(FONT, "Nunito-Black.ttf"), s) for s in range(56, 92, 4)}
        self.zemin = self.zemin_ciz()
        self.cache = {}

    def zemin_ciz(self):
        from PIL import ImageFont
        Image, ImageDraw = self.Image, self.ImageDraw
        g = np.linspace(0, 1, H)[:, None]
        ust, alt = np.array([30, 22, 18]), np.array([46, 34, 27])
        arr = (ust * (1 - g) + alt * g)[:, None, :].repeat(W, 1).astype(np.uint8)
        im = Image.fromarray(arr.reshape(H, W, 3), "RGB")
        d = ImageDraw.Draw(im)
        # kırmızı şerit
        f1 = ImageFont.truetype(os.path.join(FONT, "Nunito-Black.ttf"), 40)
        yazi = SENARYO["baslik_ust"]
        tw = d.textlength(yazi, font=f1)
        x0, y0 = (W - tw) / 2 - 34, 200
        d.polygon([(x0, y0), (x0 + tw + 68, y0 - 6), (x0 + tw + 60, y0 + 56), (x0 - 8, y0 + 62)], fill=(192, 45, 38))
        d.text((W / 2, y0 + 28), yazi, font=f1, fill="white", anchor="mm")
        f2 = ImageFont.truetype(os.path.join(FONT, "Cinzel-Black.ttf"), 76)
        for i, satir in enumerate(SENARYO["baslik"]):
            d.text((W / 2, 318 + i * 78), satir, font=f2, fill=(245, 230, 200), anchor="mm",
                   stroke_width=5, stroke_fill=(20, 14, 10))
        d.rectangle([0, PY0 - 6, W, PY0 - 1], fill=(232, 199, 122))
        d.rectangle([0, PY1, W, PY1 + 5], fill=(232, 199, 122))
        return im

    def cekim(self, i):
        if i not in self.cache:
            if len(self.cache) > 3:
                self.cache.pop(next(iter(self.cache)))
            s = self.seg[i]
            c = self.plan[s["sid"]][s["k"]]
            bg = self.Image.open(os.path.join(self.A.KARE, c["bg"])).convert("RGB")
            akt = [self.A.Aktor(a, (i + 1) * 31 + j) for j, a in enumerate(c["aktorler"])]
            self.cache[i] = (bg, akt, c["fx"])
        return self.cache[i]

    def panel(self, i, t):
        A, Image = self.A, self.Image
        bg, akt, fx = self.cekim(i)
        s = self.seg[i]
        sure = s["son"] - s["bas"] + XF
        tuval = bg.copy()
        for a in akt:
            a.ciz(tuval, t)
        Wc, Hc = tuval.size
        sc = Wc / 1920
        d = self.ImageDraw.Draw(tuval, "RGBA")
        for f in fx:
            if f.startswith("duman:"):
                x, y = (float(v) * sc for v in f[6:].split(","))
                A.duman(d, x, y, t, sc, i + 1)
            elif f.startswith("kivilcim:"):
                x, y = (float(v) * sc for v in f[9:].split(","))
                A.kivilcim(d, x, y, t, sc, i + 1)
        p = A.ease(t / max(sure, 0.01))
        z = 1.0 + 0.07 * (p if i % 2 == 0 else 1 - p)
        ch = Hc / z
        cw = ch * PW / PH
        x0 = min(max(s["x"] * Wc - cw / 2, 0), Wc - cw)
        y0 = min(max(0.5 * Hc - ch / 2, 0), Hc - ch)
        out = tuval.resize((PW, PH), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        d2 = self.ImageDraw.Draw(out, "RGBA")
        if "kar" in fx:
            A.kar(d2, t)
        if "yagmur" in fx:
            A.yagmur(d2, t)
        if "isik" in fx:
            k = 1.0 + 0.035 * math.sin(t * 7.3) + 0.02 * math.sin(t * 13.1 + 1)
            out = out.point(lambda v: min(255, int(v * k)))
        return out

    def altyazi(self, im, t):
        d = self.ImageDraw.Draw(im)
        if t >= self.zaman["anlatim_son"] - 0.05:
            yazi = SENARYO["son_kart"]["yazi"]
            d.text((W / 2, ALT_Y), yazi, font=self.f_alt[76], fill=(255, 210, 63), anchor="mm",
                   stroke_width=8, stroke_fill=(10, 8, 6))
            return
        sayfa = next((p for p in self.sayfa if p["bas"] <= t < p["son"]), None)
        if not sayfa:
            return
        kel = sayfa["kelimeler"]
        aktif = max([j for j, w in enumerate(kel) if w["s"] - 0.03 <= t] or [0])
        yazilar = [tr_upper(w["w"]) for w in kel]
        # satırlara böl (en fazla 2)
        satirlar, cur = [], []
        for j, y in enumerate(yazilar):
            if cur and len(" ".join(yazilar[k] for k in cur + [j])) > 15:
                satirlar.append(cur)
                cur = []
            cur.append(j)
        satirlar.append(cur)
        if len(satirlar) > 2:
            satirlar = [satirlar[0], [j for s_ in satirlar[1:] for j in s_]]
        boy = 84
        while boy > 56 and max(d.textlength(" ".join(yazilar[j] for j in s_), font=self.f_alt[boy]) for s_ in satirlar) > 880:
            boy -= 4
        f = self.f_alt[boy]
        # küçük "pop" efekti: sayfa açılınca hafif yukarı kayar
        kay = int(14 * max(0.0, 1 - (t - sayfa["bas"]) / 0.12))
        bosluk = d.textlength(" ", font=f)
        y = ALT_Y - (len(satirlar) - 1) * boy * 0.58 + kay
        for s_ in satirlar:
            gen = sum(d.textlength(yazilar[j], font=f) for j in s_) + bosluk * (len(s_) - 1)
            x = (W - gen) / 2
            for j in s_:
                renk = (255, 210, 63) if j == aktif else (255, 255, 255)
                d.text((x, y), yazilar[j], font=f, fill=renk, anchor="lm", stroke_width=8, stroke_fill=(10, 8, 6))
                x += d.textlength(yazilar[j], font=f) + bosluk
            y += boy * 1.16

    def kare(self, t):
        A = self.A
        si = 0
        while si < len(self.seg) - 1 and t >= self.seg[si]["son"]:
            si += 1
        s = self.seg[si]
        pan = self.panel(si, t - s["bas"])
        if si + 1 < len(self.seg) and t > s["son"] - XF:
            a = A.ease((t - (s["son"] - XF)) / XF)
            pan = self.Image.blend(pan, self.panel(si + 1, max(0.0, t - self.seg[si + 1]["bas"])), a)
        im = self.zemin.copy()
        im.paste(pan, (0, PY0))
        self.altyazi(im, t)
        return im


def isci(no, bas, son, cikti):
    k = Kurgu()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "2", cikti], stdin=subprocess.PIPE)
    for f in range(bas, son):
        ff.stdin.write(k.kare(f / FPS).tobytes())
        if no == 0 and (f - bas) % 150 == 0:
            print(f"  işçi0: {f - bas}/{son - bas}", flush=True)
    ff.stdin.close()
    ff.wait()


def render():
    zaman = json.load(open(os.path.join(B, "zaman.json")))
    n = int(math.ceil(zaman["toplam"] * FPS))
    sin = [n * i // ISCI for i in range(ISCI + 1)]
    par = [os.path.join(B, f"v{i}.mp4") for i in range(ISCI)]
    ps = [Process(target=isci, args=(i, sin[i], sin[i + 1], par[i])) for i in range(ISCI)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    liste = os.path.join(B, "liste.txt")
    open(liste, "w").write("".join(f"file '{p}'\n" for p in par))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", liste,
                    "-c", "copy", os.path.join(B, "sessiz.mp4")], check=True)
    print("render tamam", n, "kare", flush=True)


# ------------------------------------------------------------------ 4. müzik + efekt + karışım
def mix():
    import muzik as M
    zaman = json.load(open(os.path.join(B, "zaman.json")))
    plan = json.load(open(os.path.join(ROOT, "build", "kare", "plan.json")))
    toplam = zaman["toplam"]
    seg = zaman["segmentler"]
    sahneler = [{"sid": s["sid"], "bas": s["bas"], "sure": s["son"] - s["bas"]} for s in seg]
    muz = os.path.join(B, "muzik.wav")
    efk = os.path.join(B, "efekt.wav")
    sf.write(muz, M.muzik(toplam, sahneler, giris=0.3), M.SR)
    sf.write(efk, M.efektler(toplam, seg, plan), M.SR)
    filtre = ("[0:a]loudnorm=I=-14:TP=-2:LRA=11,aresample=48000,apad,asplit=2[ses][sc];"
              "[1:a]loudnorm=I=-29:LRA=11,aresample=48000[m0];"
              "[m0][sc]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=600[muz];"
              "[2:a]loudnorm=I=-27:LRA=15,aresample=48000[efk];"
              "[muz][ses][efk]amix=inputs=3:normalize=0:duration=first,"
              "alimiter=limit=0.89:level=disabled[out]")
    os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(B, "anlatim.wav"), "-i", muz,
                    "-i", efk, "-i", os.path.join(B, "sessiz.mp4"), "-filter_complex", filtre,
                    "-map", "3:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{toplam:.3f}", CIKTI], check=True)
    print("tamam:", CIKTI, f"{toplam:.1f}s", flush=True)


if __name__ == "__main__":
    os.makedirs(B, exist_ok=True)
    adimlar = sys.argv[1:] or ["ses", "montaj", "render", "mix"]
    for a in adimlar:
        {"ses": ses, "montaj": montaj, "render": render, "mix": mix}[a]()
