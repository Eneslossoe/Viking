"""Kısık arka plan müziği ve ortam seslerini kodla üretir (numpy/scipy).

Uğultu yapmaması için müzikte bas/drone yok: sadece orta-tiz lir arpeji ve yumuşak pad;
her şey 150 Hz altından filtrelenir.

Girdi : build/video/<ad>_zaman.json, build/kare/plan.json
Çıktı : build/ses/muzik_<ad>.wav, build/ses/efekt_<ad>.wav
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
rng = np.random.default_rng(7)

ENERJI = {
    "s01_acilis": 0.9, "s02_ragnar": 0.5, "s03_piramit": 0.4, "s04_dogum": 0.3, "s05_uzun_ev": 0.35,
    "s06_yemek": 0.35, "s07_tarla": 0.45, "s08_kadinlar": 0.35, "s09_temizlik": 0.45, "s10_ting": 0.6,
    "s11_din": 0.6, "s12_cagri": 0.85, "s13_deniz": 0.9, "s14_paris": 1.0, "s15_salgin": 0.25,
    "s16_evlilik": 0.5, "s17_kis": 0.3, "s18_aclik": 0.2, "s19_olum": 0.2, "s20_kapanis": 0.8,
}
DENIZ = {("s01_acilis", 0), ("s01_acilis", 1), ("s07_tarla", 3), ("s08_kadinlar", 1), ("s12_cagri", 0),
         ("s12_cagri", 3), ("s13_deniz", 0), ("s13_deniz", 1), ("s13_deniz", 2), ("s19_olum", 1), ("s20_kapanis", 3)}


def nota(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def filtre(x, tip, fc, order=2):
    w = np.array(fc) / (SR / 2) if isinstance(fc, (list, tuple)) else fc / (SR / 2)
    return sosfilt(butter(order, w, tip, output="sos"), x).astype(np.float32)


def egri(noktalar, n):
    t = np.arange(n) / SR
    return np.interp(t, [p[0] for p in noktalar], [p[1] for p in noktalar]).astype(np.float32)


def reverb(x, sure=2.4, islak=0.3):
    m = int(sure * SR)
    ir = rng.standard_normal(m).astype(np.float32) * np.exp(-np.arange(m) / SR / 0.6).astype(np.float32)
    ir = filtre(ir, "low", 4500)
    ir /= np.sqrt(np.sum(ir ** 2))
    return (1 - islak) * x + islak * fftconvolve(x, ir)[: len(x)].astype(np.float32) * 0.6


# ------------------------------------------------------------------ müzik
AKORLAR = [[62, 65, 69], [58, 62, 65], [60, 64, 67], [62, 65, 69],
           [62, 65, 69], [65, 69, 72], [60, 64, 67], [57, 61, 64]]   # Dm Bb C Dm / Dm F C A


def lir(f, sure=2.2):
    m = int(sure * SR)
    t = np.arange(m) / SR
    x = np.zeros(m, dtype=np.float32)
    for k in range(1, 7):
        x += (np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (1.6 + 1.2 * k))).astype(np.float32)
    x *= np.minimum(1, t / 0.004).astype(np.float32)
    return x


def muzik(toplam, sahneler):
    n = int(toplam * SR) + 3 * SR
    out = np.zeros(n, dtype=np.float32)
    pad = np.zeros(n, dtype=np.float32)
    akor_sure = 5.0
    enerji_pts = []
    for s in sahneler:
        e = ENERJI.get(s["sid"], 0.4)
        enerji_pts += [(s["bas"] + 1.0, e), (s["bas"] + s["sure"] - 0.5, e)]
    t0, i = 0.0, 0
    while t0 < toplam:
        akor = AKORLAR[i % len(AKORLAR)]
        e = float(np.interp(t0, [p[0] for p in enerji_pts], [p[1] for p in enerji_pts]))
        adim = 0.42 if e >= 0.7 else (0.62 if e >= 0.4 else 0.84)
        desen = akor + [akor[0] + 12, akor[2], akor[1]]
        tt, j = 0.0, 0
        while tt < akor_sure - 0.1:
            a = int((t0 + tt + rng.uniform(-0.01, 0.01)) * SR)
            if a >= 0:
                nt = lir(nota(desen[j % len(desen)])) * rng.uniform(0.6, 1.0)
                b = min(n, a + len(nt))
                out[a:b] += nt[: b - a]
            tt += adim
            j += 1
        # yumuşak pad (saf sinüs, bas yok)
        a, b = int(t0 * SR), min(n, int((t0 + akor_sure + 1.5) * SR))
        m = b - a
        tm = np.arange(m) / SR
        blok = sum(np.sin(2 * np.pi * nota(x) * tm + rng.random() * 6) for x in akor).astype(np.float32)
        zarf = np.minimum(1, np.minimum(tm / 1.5, (m / SR - tm) / 1.5)).astype(np.float32)
        pad[a:b] += blok * zarf * 0.10
        t0 += akor_sure
        i += 1
    out = out * 0.5 + filtre(pad, "low", 2000)
    out = reverb(out, islak=0.35)
    out = filtre(out, "high", 150, order=4)
    out *= egri([(0, 0), (2.5, 1), (toplam - 4, 1), (toplam + 0.5, 0)], n)
    out /= max(1e-6, np.max(np.abs(out)))
    return out[: int(toplam * SR)] * 0.9


# ------------------------------------------------------------------ efektler
def gurultu(n):
    return rng.standard_normal(n).astype(np.float32)


def yagmur_ses(n):
    x = filtre(gurultu(n), "band", [1000, 7000])
    damla = np.zeros(n, dtype=np.float32)
    for p in rng.integers(0, n - 600, int(n / SR * 40)):
        damla[p:p + 400] += gurultu(400) * np.exp(-np.arange(400) / 60).astype(np.float32) * rng.uniform(0.2, 1)
    return x * 0.35 + filtre(damla, "band", [2000, 8000]) * 0.5


def ruzgar_ses(n):
    t = np.arange(n) / SR
    x = filtre(gurultu(n), "band", [300, 1400]) * 2.0
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 9.0 + 1) * np.sin(2 * np.pi * t / 4.3)
    return (x * swell).astype(np.float32)


def dalga_ses(n):
    t = np.arange(n) / SR
    x = filtre(gurultu(n), "band", [250, 2500]) * 1.6
    swell = (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.0)) ** 2
    return (x * (0.2 + swell)).astype(np.float32)


def ates_ses(n):
    hisirti = filtre(gurultu(n), "band", [500, 2500]) * 0.25
    cit = np.zeros(n, dtype=np.float32)
    for p in rng.integers(0, n - 2000, int(n / SR * 10)):
        ln = int(rng.integers(150, 1200))
        cit[p:p + ln] += gurultu(ln) * np.exp(-np.arange(ln) / (ln / 5)).astype(np.float32) * rng.uniform(0.3, 1.0)
    return hisirti + filtre(cit, "band", [1200, 9000]) * 0.9


def gok_gurultusu():
    m = int(3.0 * SR)
    t = np.arange(m) / SR
    x = filtre(gurultu(m), "band", [60, 500], order=2) * 3
    crack = filtre(gurultu(m), "band", [400, 4000]) * np.exp(-t / 0.1).astype(np.float32)
    env = (np.minimum(1, t / 0.03) * np.exp(-t / 0.9)).astype(np.float32)
    return (x * env + crack) * 0.7


def boru():
    m = int(3.2 * SR)
    t = np.arange(m) / SR
    f = 147 * (1 + 0.004 * np.sin(2 * np.pi * 5 * t)) * np.where(t < 1.4, 1.0, 1.335)
    x = (2 * ((np.cumsum(f) / SR) % 1.0) - 1).astype(np.float32)
    env = (np.minimum(1, t / 0.25) * np.clip((3.2 - t) / 0.5, 0, 1)).astype(np.float32)
    return reverb(filtre(x, "band", [150, 1200]) * env, islak=0.45)


def efektler(toplam, segmentler, plan):
    n = int(toplam * SR)
    out = np.zeros(n, dtype=np.float32)
    katman = {"yagmur": (yagmur_ses, 0.30), "ruzgar": (ruzgar_ses, 0.14),
              "dalga": (dalga_ses, 0.28), "ates": (ates_ses, 0.22)}
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
        if "simsek" in c["fx"]:
            g = gok_gurultusu()
            for tt in np.arange(0.3, s["son"] - s["bas"] - 1.0, 5.0):
                p = a + int(tt * SR)
                q = min(n, p + len(g))
                out[p:q] += g[: q - p] * 0.5
        if (s["sid"], s["k"]) == ("s12_cagri", 0):
            h = boru()
            p = a + int(0.2 * SR)
            q = min(n, p + len(h))
            out[p:q] += h[: q - p] * 0.6
    out = filtre(out, "high", 120, order=4)
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
