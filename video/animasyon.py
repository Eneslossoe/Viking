"""Çekimleri canlandırıp kare kare video üretir (PIL + ffmpeg).

Kullanım:
  python video/animasyon.py                 # tüm video
  python video/animasyon.py s01_acilis ...  # sadece seçili sahneler (önizleme)
Çıktı: build/video/sessiz.mp4 (veya önizleme_<...>.mp4) + build/video/zaman_cizelgesi.json
"""
import json
import math
import os
import random
import subprocess
import sys
from multiprocessing import Process

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KARE = os.path.join(ROOT, "build", "kare")
OUTDIR = os.path.join(ROOT, "build", "video")
FPS = 30
OW, OH = 1920, 1080
XF = 0.35          # çekimler arası geçiş (sn)
ISCI = int(os.environ.get("ISCI", "4"))

sys.path.insert(0, os.path.join(ROOT, "ses"))


# ------------------------------------------------------------------ zamanlama
def tahmini_zamanlama(sid, metin):
    from seslendir import cumlelere_bol
    t, cumleler = 0.35, []
    for c in cumlelere_bol(metin):
        d = len(c) / 13.5
        cumleler.append({"metin": c, "bas": t, "son": t + d})
        t += d + 0.42
    return {"sure": t + 0.4, "cumleler": cumleler, "tahmini": True}


def zaman_cizelgesi(secili=None):
    senaryo = json.load(open(os.path.join(ROOT, "senaryo", "sahneler.json"), encoding="utf-8"))
    plan = json.load(open(os.path.join(KARE, "plan.json")))
    zy = os.path.join(ROOT, "build", "ses", "zamanlama.json")
    zaman = json.load(open(zy)) if os.path.exists(zy) else {}
    seg, sahneler, t0 = [], [], 0.0
    for s in senaryo["sahneler"]:
        sid = s["id"]
        if secili and sid not in secili:
            continue
        z = zaman.get(sid) or tahmini_zamanlama(sid, s["metin"])
        cekimler = plan[sid]
        baslar = []
        for k, c in enumerate(cekimler):
            idx = min(c["cumle"], len(z["cumleler"]) - 1)
            baslar.append(0.0 if k == 0 else max(0.0, z["cumleler"][idx]["bas"] - 0.15))
        for k, c in enumerate(cekimler):
            a = baslar[k]
            b = baslar[k + 1] if k + 1 < len(cekimler) else z["sure"]
            seg.append({"sid": sid, "k": k, "bas": t0 + a, "son": t0 + b, "cekim": c})
        sahneler.append({"sid": sid, "bas": t0, "sure": z["sure"], "cumleler": z["cumleler"],
                         "tahmini": z.get("tahmini", False)})
        t0 += z["sure"]
    return seg, sahneler, t0


# ------------------------------------------------------------------ yardımcılar
def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


class Aktor:
    def __init__(self, a, seed):
        self.anim = a.get("anim")
        rnd = random.Random(seed)
        self.faz = rnd.uniform(0, 6.28)
        if "frames" in a:
            ims = [Image.open(os.path.join(KARE, f)).convert("RGBA") for f in a["frames"]]
        else:
            ims = [Image.open(os.path.join(KARE, a["png"])).convert("RGBA")]
            if a.get("kapali"):
                ims.append(Image.open(os.path.join(KARE, a["kapali"])).convert("RGBA"))
        bbox = None
        for im in ims:
            b = im.getbbox()
            if b:
                bbox = b if bbox is None else (min(bbox[0], b[0]), min(bbox[1], b[1]), max(bbox[2], b[2]), max(bbox[3], b[3]))
        bbox = bbox or (0, 0, 1, 1)
        self.x, self.y = bbox[0], bbox[1]
        self.ims = [im.crop(bbox) for im in ims]
        self.kirpma = "kapali" in a and "frames" not in a
        # göz kırpma zamanları
        self.kirp = []
        t = rnd.uniform(0.5, 3.0)
        while t < 120:
            self.kirp.append(t)
            t += rnd.uniform(2.2, 5.0)

    def ciz(self, tuval, t):
        im = self.ims[0]
        if self.anim == "cycle":
            im = self.ims[int(t / 0.13) % len(self.ims)]
        elif self.kirpma and any(k <= t < k + 0.14 for k in self.kirp):
            im = self.ims[1]
        x, y = self.x, self.y
        if self.anim == "nefes":
            s = 1 + 0.012 * math.sin(2 * math.pi * t / 3.0 + self.faz)
            w, h = im.size
            nh = max(1, int(round(h * s)))
            im = im.resize((w, nh), Image.BILINEAR)
            y = y + h - nh
        elif self.anim == "sallan":
            ang = 1.6 * math.sin(2 * math.pi * t / 3.4 + self.faz)
            w, h = im.size
            im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
            x -= (im.size[0] - w) // 2
            y -= (im.size[1] - h) // 2
            y += int(7 * math.sin(2 * math.pi * t / 3.4 + self.faz + 1.2))
        tuval.paste(im, (int(x), int(y)), im)


class Cekim:
    def __init__(self, c, seed):
        self.bg = Image.open(os.path.join(KARE, c["bg"])).convert("RGB")
        self.W, self.H = self.bg.size
        self.sc = self.W / OW
        self.aktorler = [Aktor(a, seed * 31 + i) for i, a in enumerate(c["aktorler"])]
        self.fx = c["fx"]
        self.kb = c["kb"]
        self.rnd_seed = seed

    def kare(self, t, sure):
        tuval = self.bg.copy()
        for a in self.aktorler:
            a.ciz(tuval, t)
        d = ImageDraw.Draw(tuval, "RGBA")
        for f in self.fx:
            if f.startswith("duman:"):
                x, y = (float(v) * self.sc for v in f[6:].split(","))
                duman(d, x, y, t, self.sc, self.rnd_seed)
            elif f.startswith("kivilcim:"):
                x, y = (float(v) * self.sc for v in f[9:].split(","))
                kivilcim(d, x, y, t, self.sc, self.rnd_seed)
        # Ken Burns
        p = ease(t / max(sure, 0.01))
        z = self.kb["z"][0] + (self.kb["z"][1] - self.kb["z"][0]) * p
        fx = self.kb["f0"][0] + (self.kb["f1"][0] - self.kb["f0"][0]) * p
        fy = self.kb["f0"][1] + (self.kb["f1"][1] - self.kb["f0"][1]) * p
        cw, ch = self.W / z, self.H / z
        x0 = min(max(fx * self.W - cw / 2, 0), self.W - cw)
        y0 = min(max(fy * self.H - ch / 2, 0), self.H - ch)
        out = tuval.resize((OW, OH), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        if "kar" in self.fx or "yagmur" in self.fx:
            d2 = ImageDraw.Draw(out, "RGBA")
            if "kar" in self.fx:
                kar(d2, t)
            if "yagmur" in self.fx:
                yagmur(d2, t)
        if "isik" in self.fx:
            k = 1.0 + 0.035 * math.sin(t * 7.3) + 0.02 * math.sin(t * 13.1 + 1)
            out = out.point(lambda v: min(255, int(v * k)))
        if "simsek" in self.fx:
            ph = (t + 1.0) % 4.2
            if ph < 0.35:
                a = (1 - ph / 0.35) * 0.75
                out = Image.blend(out, Image.new("RGB", out.size, (255, 255, 240)), a)
        return out


def duman(d, x, y, t, sc, seed):
    rnd = random.Random(seed)
    off = [rnd.uniform(0, 1) for _ in range(40)]
    per = 0.35
    for i in range(40):
        born = (math.floor(t / per) - i) * per
        age = t - born
        if age < 0 or age > 4.5:
            continue
        j = off[int(abs(born / per)) % 40]
        px = x + (age * 18 + 25 * math.sin(age * 1.3 + j * 6)) * sc
        py = y - age * 70 * sc
        r = (18 + age * 22) * sc
        a = int(110 * (1 - age / 4.5))
        d.ellipse([px - r, py - r, px + r, py + r], fill=(200, 200, 205, a))


def kivilcim(d, x, y, t, sc, seed):
    for i in range(14):
        per = 1.6
        born = (math.floor(t / per * 14) - i) * per / 14
        age = t - born
        if age < 0 or age > per:
            continue
        h = (i * 73 % 100) / 100
        px = x + (h - 0.5) * 120 * sc + 20 * math.sin(age * 5 + i) * sc
        py = y - age * 180 * sc
        r = 3.2 * sc
        a = int(255 * (1 - age / per))
        d.ellipse([px - r, py - r, px + r, py + r], fill=(255, 190, 80, a))


def kar(d, t):
    for i in range(170):
        x0 = (i * 397) % OW
        sp = 40 + (i * 31) % 70
        y = (((i * 233) % OH) + sp * t) % (OH + 20) - 10
        x = x0 + 25 * math.sin(t * 0.8 + i)
        r = 2 + (i % 3)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 220))


def yagmur(d, t):
    for i in range(160):
        x0 = (i * 521) % (OW + 200)
        sp = 900 + (i * 37) % 400
        y = (((i * 307) % OH) + sp * t) % (OH + 60) - 30
        x = x0 - 0.25 * y
        d.line([x, y, x - 8, y + 30], fill=(210, 225, 240, 140), width=2)


# ------------------------------------------------------------------ işleme
def isci(no, seg, kare_bas, kare_son, cikti):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-threads", "2", cikti]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    cache = {}

    def al(i):
        if i not in cache:
            if len(cache) > 3:
                cache.pop(next(iter(cache)))
            cache[i] = Cekim(seg[i]["cekim"], seed=i + 1)
        return cache[i]

    si = 0
    for f in range(kare_bas, kare_son):
        t = f / FPS
        while si < len(seg) - 1 and t >= seg[si]["son"]:
            si += 1
        s = seg[si]
        sure = s["son"] - s["bas"] + XF
        im = al(si).kare(t - s["bas"], sure)
        if si + 1 < len(seg) and t > s["son"] - XF:
            n = seg[si + 1]
            a = ease((t - (s["son"] - XF)) / XF)
            im2 = al(si + 1).kare(max(0.0, t - n["bas"]), n["son"] - n["bas"] + XF)
            im = Image.blend(im, im2, a)
        ff.stdin.write(im.tobytes())
        if no == 0 and (f - kare_bas) % 300 == 0:
            print(f"  işçi0: {f - kare_bas}/{kare_son - kare_bas}", flush=True)
    ff.stdin.close()
    ff.wait()


def main():
    secili = sys.argv[1:]
    os.makedirs(OUTDIR, exist_ok=True)
    seg, sahneler, toplam = zaman_cizelgesi(set(secili) if secili else None)
    ad = "sessiz" if not secili else "onizleme_" + "_".join(s[:3] for s in secili)
    json.dump({"toplam": toplam, "sahneler": sahneler, "segmentler": [{k: v for k, v in s.items() if k != "cekim"} for s in seg]},
              open(os.path.join(OUTDIR, f"{ad}_zaman.json"), "w"), ensure_ascii=False, indent=1)
    n = int(math.ceil(toplam * FPS))
    print(f"{len(seg)} çekim, {toplam:.1f} sn, {n} kare, {ISCI} işçi", flush=True)
    sinirlar = [n * i // ISCI for i in range(ISCI + 1)]
    parcalar = [os.path.join(OUTDIR, f"{ad}_p{i}.mp4") for i in range(ISCI)]
    ps = [Process(target=isci, args=(i, seg, sinirlar[i], sinirlar[i + 1], parcalar[i])) for i in range(ISCI)]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    liste = os.path.join(OUTDIR, f"{ad}_liste.txt")
    with open(liste, "w") as f:
        for p in parcalar:
            f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", liste, "-c", "copy",
                    os.path.join(OUTDIR, f"{ad}.mp4")], check=True)
    for p in parcalar:
        os.remove(p)
    os.remove(liste)
    print("tamam:", os.path.join(OUTDIR, f"{ad}.mp4"))


if __name__ == "__main__":
    main()
