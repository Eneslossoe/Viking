"""Tüm çekimleri SVG olarak yazar, PNG'ye çevirir ve build/kare/plan.json oluşturur.

Kullanım: python cizim/hazirla.py [sahne_id ...]
"""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sahneler import SAHNELER  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG_DIR = os.path.join(ROOT, "build", "svg")
PNG_DIR = os.path.join(ROOT, "build", "kare")


def kaydet(svg_text, isler, transparent):
    h = hashlib.sha1(svg_text.encode()).hexdigest()[:16]
    png = os.path.join(PNG_DIR, f"{h}.png")
    if not os.path.exists(png) and not any(j["png"] == png for j in isler):
        yol = os.path.join(SVG_DIR, f"{h}.svg")
        with open(yol, "w", encoding="utf-8") as f:
            f.write(svg_text)
        isler.append({"svg": yol, "png": png, "transparent": transparent})
    return os.path.basename(png)


def main():
    os.makedirs(SVG_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    secili = set(sys.argv[1:])
    plan_yolu = os.path.join(PNG_DIR, "plan.json")
    plan = json.load(open(plan_yolu)) if os.path.exists(plan_yolu) else {}
    isler = []
    for sid, fn in SAHNELER.items():
        if secili and sid not in secili:
            continue
        cekimler = []
        for c in fn():
            akt = []
            for a in c["aktorler"]:
                kayit = {"anim": a.get("anim")}
                if "frames" in a:
                    kayit["frames"] = [kaydet(f, isler, True) for f in a["frames"]]
                else:
                    kayit["png"] = kaydet(a["svg"], isler, True)
                    if a.get("kapali"):
                        kayit["kapali"] = kaydet(a["kapali"], isler, True)
                akt.append(kayit)
            cekimler.append({"cumle": c["cumle"], "bg": kaydet(c["bg"], isler, False),
                             "aktorler": akt, "fx": c["fx"], "kb": c["kb"]})
        plan[sid] = cekimler
    is_yolu = os.path.join(SVG_DIR, "isler.json")
    json.dump(isler, open(is_yolu, "w"))
    print(f"{len(isler)} yeni görsel çiziliyor...", flush=True)
    if isler:
        subprocess.run(["node", os.path.join(ROOT, "cizim", "render.js"), is_yolu], check=True)
    json.dump(plan, open(plan_yolu, "w"), indent=1)


if __name__ == "__main__":
    main()
