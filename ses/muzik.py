"""Arka plan müziği ve ortam seslerini tamamen kodla sentezler (numpy/scipy).

Girdi : build/video/<ad>_zaman.json (animasyon.py üretir)
Çıktı : build/ses/muzik.wav, build/ses/efekt.wav
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
rng = np.random.default_rng(7)

# Sahne başına enerji (0 sakin - 1 gergin) ve davul
ENERJI = {
    "s01_acilis": 0.9, "s02_ragnar": 0.5, "s03_piramit": 0.4, "s04_dogum": 0.3, "s05_uzun_ev": 0.35,
    "s06_yemek": 0.35, "s07_tarla": 0.45, "s08_kadinlar": 0.35, "s09_temizlik": 0.45, "s10_ting": 0.6,
    "s11_din": 0.6, "s12_cagri": 0.85, "s13_deniz": 0.9, "s14_paris": 1.0, "s15_salgin": 0.25,
    "s16_evlilik": 0.5, "s17_kis": 0.3, "s18_aclik": 0.2, "s19_olum": 0.2, "s20_kapanis": 0.8,
}
DAVUL = {"s01_acilis", "s10_ting", "s12_cagri", "s13_deniz", "s14_paris", "s20_kapanis"}
DENIZ = {("s01_acilis", 0), ("s01_acilis", 1), ("s07_tarla", 3), ("s08_kadinlar", 1), ("s12_cagri", 0),
         ("s12_cagri", 3), ("s13_deniz", 0), ("s13_deniz", 1), ("s13_deniz", 2), ("s19_olum", 1), ("s20_kapanis", 3)}


def nota(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), "low", output="sos")
    return sosfilt(sos, x)


def bp(x, f1, f2, order=2):
    sos = butter(order, [f1 / (SR / 2), f2 / (SR / 2)], "band", output="sos")
    return sosfilt(sos, x)


def testere(f, n, faz=0.0):
    t = np.arange(n) / SR
    return (2 * ((t * f + faz) % 1.0) - 1).astype(np.float32)


def egri(noktalar, n):
    """[(zaman, değer), ...] -> örnek bazında doğrusal eğri."""
    t = np.arange(n) / SR
    xs = [p[0] for p in noktalar]
    ys = [p[1] for p in noktalar]
    return np.interp(t, xs, ys).astype(np.float32)


def reverb(x, sure=2.6, islak=0.32):
    n = int(sure * SR)
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-np.arange(n) / SR / 0.7).astype(np.float32)
    ir = lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = fftconvolve(x, ir)[: len(x)]
    return (1 - islak) * x + islak * y * 0.6


# ------------------------------------------------------------------ müzik
AKORLAR = [  # Re minör: Dm - Bb - C - Dm / Dm - F - C - A
    [50, 53, 57], [46, 50, 53], [48, 52, 55], [50, 53, 57],
    [50, 53, 57], [53, 57, 60], [48, 52, 55], [45, 49, 52],
]


def muzik(toplam, sahneler):
    n = int(toplam * SR) + SR
    out = np.zeros(n, dtype=np.float32)
    akor_sure = 6.0
    # enerji eğrisi
    en_pts, dv_pts = [], []
    for s in sahneler:
        e = ENERJI.get(s["sid"], 0.4)
        en_pts += [(s["bas"] + 1.5, e), (s["bas"] + s["sure"] - 0.5, e)]
        d = 1.0 if s["sid"] in DAVUL else 0.0
        dv_pts += [(s["bas"] + 1.0, d), (s["bas"] + s["sure"] - 1.0, d)]
    enerji = egri([(0, en_pts[0][1])] + en_pts + [(toplam + 2, en_pts[-1][1])], n)
    davul_k = egri([(0, dv_pts[0][1])] + dv_pts + [(toplam + 2, dv_pts[-1][1])], n)
    # pad
    i = 0
    t0 = 0.0
    while t0 < toplam + 1:
        akor = AKORLAR[i % len(AKORLAR)]
        a, b = int(t0 * SR), int(min(n, (t0 + akor_sure + 2.0) * SR))
        m = b - a
        blok = np.zeros(m, dtype=np.float32)
        for nt in akor:
            for det in (-0.0018, 0.0, 0.0021):
                blok += testere(nota(nt) * (1 + det), m, rng.random()) * 0.11
            blok += testere(nota(nt + 12) * 1.001, m, rng.random()) * 0.035
        zarf = np.minimum(1.0, np.minimum(np.arange(m) / (1.6 * SR), (m - np.arange(m)) / (1.8 * SR))).astype(np.float32)
        out[a:b] += blok * zarf
        i += 1
        t0 += akor_sure
    # filtre: enerji ile açılan
    parca = []
    blk = SR // 2
    zi = None
    for k in range(0, n, blk):
        fc = 500 + 1400 * float(enerji[min(k, n - 1)])
        bb, aa = butter(2, fc / (SR / 2), "low")
        if zi is None or len(zi) != max(len(aa), len(bb)) - 1:
            zi = np.zeros(max(len(aa), len(bb)) - 1)
        y, zi = lfilter(bb, aa, out[k:k + blk], zi=zi)
        parca.append(y)
    out = np.concatenate(parca).astype(np.float32)
    # drone
    t = np.arange(n) / SR
    drone = (np.sin(2 * np.pi * nota(38) * t) * 0.5 + lp(testere(nota(38), n), 300) * 0.35
             + np.sin(2 * np.pi * nota(45) * t) * 0.22).astype(np.float32)
    drone *= (0.8 + 0.2 * np.sin(2 * np.pi * t / 11.0)).astype(np.float32)
    out += drone * 0.5
    # davul (72 BPM, 1 ve 3. vuruş + hafif ara vuruş)
    vurus = 60 / 72
    hit_n = int(0.9 * SR)
    th = np.arange(hit_n) / SR
    frek = 55 + 70 * np.exp(-th / 0.05)
    hit = (np.sin(2 * np.pi * np.cumsum(frek) / SR) * np.exp(-th / 0.32)).astype(np.float32)
    hit += lp(rng.standard_normal(hit_n).astype(np.float32), 1200) * np.exp(-th / 0.025).astype(np.float32) * 0.4
    davul = np.zeros(n, dtype=np.float32)
    k = 0
    tt = 0.0
    while tt < toplam:
        poz = k % 8
        guc = {0: 1.0, 4: 0.85, 6: 0.35, 7: 0.5}.get(poz, 0.0)
        if guc:
            a = int(tt * SR)
            b = min(n, a + hit_n)
            davul[a:b] += hit[: b - a] * guc
        k += 1
        tt += vurus / 2
    out += davul * davul_k * 0.9
    out = reverb(out, islak=0.35)
    # başta ve sonda yumuşak giriş/çıkış
    out *= egri([(0, 0), (3, 1), (toplam - 4, 1), (toplam + 0.5, 0)], n)
    out /= max(1e-6, np.max(np.abs(out)))
    return out[: int(toplam * SR)] * 0.9


# ------------------------------------------------------------------ efektler
def gurultu(n):
    return rng.standard_normal(n).astype(np.float32)


def yagmur_ses(n):
    x = bp(gurultu(n), 1200, 7000)
    return x * 0.35


def ruzgar_ses(n):
    t = np.arange(n) / SR
    x = lp(gurultu(n), 500, order=2) * 2.5
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * t / 9.0 + 1) * np.sin(2 * np.pi * t / 4.3)
    return (x * swell).astype(np.float32)


def dalga_ses(n):
    t = np.arange(n) / SR
    x = lp(gurultu(n), 700) * 2.0
    swell = (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.0)) ** 2
    return (x * (0.25 + swell)).astype(np.float32)


def ates_ses(n):
    x = lp(gurultu(n), 180) * 1.5
    cit = np.zeros(n, dtype=np.float32)
    say = int(n / SR * 9)
    for p in rng.integers(0, n - 2000, say):
        ln = rng.integers(200, 1500)
        cit[p:p + ln] += rng.standard_normal(ln).astype(np.float32) * np.exp(-np.arange(ln) / (ln / 5)).astype(np.float32) * rng.uniform(0.3, 1.0)
    cit = bp(cit, 1500, 9000)
    return (x + cit * 0.8).astype(np.float32)


def gok_gurultusu():
    n = int(3.5 * SR)
    t = np.arange(n) / SR
    x = lp(gurultu(n), 160, order=3) * 6
    crack = bp(gurultu(n), 300, 3000) * np.exp(-t / 0.12) * 1.2
    env = np.minimum(1, t / 0.04) * np.exp(-t / 1.2)
    return ((x * env + crack) * 0.8).astype(np.float32)


def boru():
    n = int(3.2 * SR)
    t = np.arange(n) / SR
    f = 98 * (1 + 0.004 * np.sin(2 * np.pi * 5 * t)) * np.where(t < 1.4, 1.0, 1.335)
    faz = np.cumsum(f) / SR
    x = (2 * (faz % 1.0) - 1).astype(np.float32)
    env = np.minimum(1, t / 0.25) * np.minimum(1, np.maximum(0, (3.2 - t) / 0.5))
    y = lp(x, 900) * env
    return reverb(y.astype(np.float32), islak=0.45) * 0.9


def efektler(toplam, segmentler, plan):
    n = int(toplam * SR)
    out = np.zeros(n, dtype=np.float32)
    katman = {"yagmur": (yagmur_ses, 0.30), "ruzgar": (ruzgar_ses, 0.22), "dalga": (dalga_ses, 0.30), "ates": (ates_ses, 0.20)}
    uzun = {k: f(n) for k, (f, _) in katman.items()}
    for s in segmentler:
        c = plan[s["sid"]][s["k"]]
        aktif = set()
        if "yagmur" in c["fx"]:
            aktif |= {"yagmur", "ruzgar"}
        if "kar" in c["fx"]:
            aktif.add("ruzgar")
        if "isik" in c["fx"] or any(a.get("anim") == "cycle" for a in c["aktorler"]):
            aktif.add("ates")
        if (s["sid"], s["k"]) in DENIZ:
            aktif |= {"dalga", "ruzgar"}
        a, b = int(s["bas"] * SR), min(n, int(s["son"] * SR))
        if b <= a:
            continue
        m = b - a
        f = min(int(0.6 * SR), m // 2)
        zarf = np.ones(m, dtype=np.float32)
        zarf[:f] = np.linspace(0, 1, f)
        zarf[-f:] = np.linspace(1, 0, f)
        for k in aktif:
            out[a:b] += uzun[k][a:b] * katman[k][1] * zarf
        if "simsek" in c["fx"] or (s["sid"], s["k"]) == ("s01_acilis", 1):
            g = gok_gurultusu()
            for tt in np.arange(0.0, s["son"] - s["bas"] - 1.0, 4.2):
                p = a + int(tt * SR)
                q = min(n, p + len(g))
                out[p:q] += g[: q - p] * 0.5
        if (s["sid"], s["k"]) == ("s12_cagri", 0):
            h = boru()
            p = a + int(0.2 * SR)
            q = min(n, p + len(h))
            out[p:q] += h[: q - p] * 0.6
    out /= max(1e-6, np.max(np.abs(out)))
    return out * 0.9


def main():
    ad = sys.argv[1] if len(sys.argv) > 1 else "sessiz"
    zaman = json.load(open(os.path.join(ROOT, "build", "video", f"{ad}_zaman.json")))
    plan = json.load(open(os.path.join(ROOT, "build", "kare", "plan.json")))
    toplam = zaman["toplam"]
    sf.write(os.path.join(ROOT, "build", "ses", f"muzik_{ad}.wav"), muzik(toplam, zaman["sahneler"]), SR)
    sf.write(os.path.join(ROOT, "build", "ses", f"efekt_{ad}.wav"), efektler(toplam, zaman["segmentler"], plan), SR)
    print("müzik ve efektler hazır", toplam)


if __name__ == "__main__":
    main()
