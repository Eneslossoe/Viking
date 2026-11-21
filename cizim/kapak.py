"""YouTube kapak görseli (1280x720). Kanalın 1453 / 1260 kapaklarıyla aynı dil:
çapraz bölünmüş arka plan, şimşek çizgisi, iri karakterler, isim etiketleri, büyük yıl yazısı."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

from sanat import *  # noqa: E402,F401
from sanat2 import *  # noqa: E402,F401
from sahneler import SEN, RAGNAR, bg_bolunmus  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kapak():
    d, bg = bg_bolunmus(("#4f5d68", "#8a98a3"), ("#f0a83c", "#fbe28c"), zigzag=True)
    s = bg
    # sol: yağmurlu köy
    s += bulut(220, 120, 1.3, "#6b7882") + bulut(640, 90, 1.1, "#76838c")
    s += "".join(L(x, y, x - 14, y + 44, sw=4, stroke="#c9d6e0", extra='opacity="0.6"')
                 for x, y in [(80, 260), (200, 340), (330, 230), (450, 380), (560, 280), (700, 360), (140, 520), (620, 520), (380, 600), (760, 220)])
    s += tepeler(900, "#6f7c50", genlik=20, seed=31, sw=6) + uzun_ev(330, 900, w=520, s=0.62)
    # sağ: altın gün batımı, filo
    s += gunes(1640, 520, 120, "#fff1b0")
    s += gemi(1700, 930, 0.62) + gemi_silueti(1250, 720, 0.28, "#b0702a") + gemi_silueti(1450, 700, 0.24, "#b0702a")
    # karakterler
    s += insan(560, 1110, 1.55, ifade="korku", kol="tut", esya="orak", bak=(6, 0), **SEN)
    s += insan(1330, 1110, 1.5, kol="tek_yukari", esya="kilic", ifade="kizgin",
               **{k: v for k, v in RAGNAR.items() if k != "vif"})
    # yazılar
    s += buyuk_yazi(960, 215, "845", 230, sw=18)
    s += serit_baslik(960, 320, "VİKİNG KÖYLÜSÜ OLSAYDIN?", 62, rot=-3)
    s += etiket(330, 620, "KÖYLÜ", 62) + etiket(1660, 420, "RAGNAR", 62, bg="#f2c14e")
    return svg(s, defs=ORTAK_DEFS + d)


def main():
    out = os.path.join(ROOT, "build", "svg")
    os.makedirs(out, exist_ok=True)
    yol = os.path.join(out, "kapak.svg")
    png = os.path.join(out, "kapak.png")
    open(yol, "w", encoding="utf-8").write(kapak())
    jobs = os.path.join(out, "kapak_is.json")
    json.dump([{"svg": yol, "png": png}], open(jobs, "w"))
    subprocess.run(["node", os.path.join(ROOT, "cizim", "render.js"), jobs], check=True,
                   env={**os.environ, "RENDER_SCALE": "1.0"})
    os.makedirs(os.path.join(ROOT, "cikti"), exist_ok=True)
    Image.open(png).convert("RGB").resize((1280, 720), Image.LANCZOS).save(
        os.path.join(ROOT, "cikti", "kapak_1280x720.jpg"), quality=92)
    print("kapak hazır")


if __name__ == "__main__":
    main()
