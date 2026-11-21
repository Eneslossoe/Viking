"""Her sahnenin çekimleri. Her çekim, sahnedeki bir cümle indeksinden itibaren ekranda kalır.

Çekim sözlüğü:
  cumle   : bu çekimin başladığı cümle (sahne içi indeks)
  bg      : arka plan SVG
  aktorler: animasyonlu katmanlar [{svg, kapali?, frames?, anim}]
  fx      : parçacık efektleri ["kar", "yagmur", "duman:x,y", "kivilcim:x,y", "simsek", "toz", "isik"]
  kb      : kamera {z:(z0,z1), f0:(x,y), f1:(x,y)}
"""
from sanat import *
from sanat2 import *

SEN = dict(sac="sari", govde="kahve", sakal="kisa", kolye=True)
ES = dict(kadin=True, sac="kizil", govde="yesil", onluk="krem", anahtar=True)
JARL = dict(bas="kask", pelerin="kirmizi", govde="koyu", sakal="orgu", sac="siyah", vif="sert")
RAGNAR = dict(bas="kask", pelerin="kirmizi", govde="koyu", sakal="orgu", sac="sari", vif="sert")
KOLE = dict(govde="gri", yirtik=True, tasma=True, sakal=None, biyik=False, sac="kahve", vif="uzgun")
ZEMIN = 985


def _svg(icerik, defs=""):
    return svg(icerik, defs=ORTAK_DEFS + defs)


def kisi(x, y=ZEMIN, s=0.8, anim="nefes", **kw):
    kw.setdefault("ifade", kw.pop("vif", "normal"))
    kw.pop("vif", None)
    acik = _svg(insan(x, y, s, **kw))
    kw2 = dict(kw)
    kw2["goz"] = "kapali"
    return {"svg": acik, "kapali": _svg(insan(x, y, s, **kw2)), "anim": anim}


def aktor(icerik, anim="nefes", defs=""):
    return {"svg": _svg(icerik, defs), "anim": anim}


def ates_aktor(x, y, s=1.0):
    return {"frames": [_svg(ates(x, y, s, faz=i)) for i in range(3)], "anim": "cycle"}


def cekim(cumle, bg, defs="", aktorler=(), fx=(), kb=None):
    return {"cumle": cumle, "bg": _svg(bg, defs), "aktorler": list(aktorler), "fx": list(fx),
            "kb": kb or {"z": (1.0, 1.06), "f0": (0.5, 0.5), "f1": (0.5, 0.5)}}


def KB(z0=1.0, z1=1.07, f0=(0.5, 0.5), f1=None):
    return {"z": (z0, z1), "f0": f0, "f1": f1 or f0}


# ------------------------------------------------------------- ortak arka planlar
def bg_koy(saat="gunduz", ev=True, ev_x=1400, kar=False, seed=1):
    renk = {"gunduz": ("#86c0e6", "#e3f1f7"), "sabah": ("#f6b26b", "#fde9c4"),
            "aksam": ("#e9875a", "#f8d38c"), "gri": ("#8a96a0", "#c9d0d4")}[saat]
    d, gok = gokyuzu(*renk, gid="gk" + saat)
    s = gok
    if saat == "gunduz":
        s += bulut(300, 180, 1.0) + bulut(1300, 120, 0.8, op=0.9)
    if saat == "sabah":
        s += gunes(1500, 560, 90, "#ffe5a0")
    if saat == "gri":
        s += bulut(400, 160, 1.3, "#aeb6bb") + bulut(1200, 200, 1.5, "#9fa8ad") + bulut(1700, 120, 1.1, "#b5bcc0")
    s += daglar(650, "#93a9b8" if saat != "gri" else "#7d8b94", seed=seed, kar=True)
    s += daglar(720, "#6f8a9b" if saat != "gri" else "#66737b", tepe=(80, 180), seed=seed + 5)
    zemin = "#eef3f6" if kar else ("#6fa34a" if saat != "gri" else "#7f8d5e")
    s += tepeler(760, zemin, seed=seed + 2)
    if ev:
        s += uzun_ev(ev_x, 800, w=640, s=0.75, kar=kar)
    s += tepeler(880, "#f6f9fb" if kar else ("#5f9640" if saat != "gri" else "#6f7c50"), genlik=25, seed=seed + 3)
    if not kar:
        s += cimen_tutamlari(900, 1070, n=50, seed=seed)
    return d, s


def bg_ic(ocak_x=960):
    d, s = ic_mekan()
    if ocak_x is not None:
        s += ocak(ocak_x, 905, 1.0)
    return d, s


def bg_bolunmus(sol, sag, zigzag=True):
    d1 = lin_grad("bsol", [(0, sol[0]), (1, sol[1])]) + lin_grad("bsag", [(0, sag[0]), (1, sag[1])])
    s = f'<rect width="1920" height="1080" fill="url(#bsol)"/>'
    s += P("M1010,0 L1920,0 L1920,1080 L860,1080 L960,620 L900,600 Z", fill="url(#bsag)", sw=0, stroke="none")
    if zigzag:
        s += P("M1010,0 L900,600 L960,620 L860,1080", sw=22, stroke="#fff6c8") + P("M1010,0 L900,600 L960,620 L860,1080", sw=8, stroke="#ffffff")
    return d1, s


def bg_deniz(saat="gece", firtina=False):
    renk = {"gece": ("#0b1726", "#22395a"), "firtina": ("#3b4752", "#6e7b85"), "safak": ("#f2a46a", "#fde3b0"),
            "gunduz": ("#86c0e6", "#e3f1f7")}[saat]
    d, gok = gokyuzu(*renk, gid="gd" + saat)
    s = gok
    if saat == "gece":
        s += yildizlar(140, 520) + ay(1520, 200, 60)
    if saat == "firtina":
        s += bulut(300, 150, 1.8, "#5c6770") + bulut(1000, 120, 2.0, "#4f5962") + bulut(1650, 170, 1.7, "#5a656e")
    if saat == "safak":
        s += gunes(960, 640, 110, "#fff1c4")
    dd, sea = deniz(620, *(("#1c3d5c", "#0b1e30") if saat == "gece" else ("#4a6c80", "#25404f") if saat == "firtina" else ("#5fa2c2", "#2a6a8a")), gid="dz" + saat)
    return d + dd, s + sea


# ================================================================ SAHNELER
def s01():
    c = []
    d, bg = bg_deniz("gece")
    sil = "".join(gemi_silueti(x, 650 + abs(x - 960) * 0.02, 0.35 + (i % 3) * 0.05) for i, x in enumerate(range(160, 1800, 150)))
    c.append(cekim(0, bg + sil + buyuk_yazi(960, 330, "845", 220), d,
                   aktorler=[aktor(gemi(1180, 900, 0.75, yelken=True), anim="sallan")], kb=KB(1.0, 1.08, (0.5, 0.45))))
    d, bg = bg_deniz("firtina")
    c.append(cekim(2, bg + gemi(960, 980, 1.0, kurek=True) + etiket(1500, 210, "RAGNAR LODBROK", 50), d,
                   aktorler=[kisi(980, 870, 0.95, kol="tek_yukari", esya="kilic", anim="nefes", **RAGNAR)],
                   fx=["yagmur"], kb=KB(1.0, 1.08, (0.5, 0.5), (0.52, 0.42))))
    d, bg = bg_koy("aksam", ev=False)
    uzak = "".join(gemi_silueti(x, 735, 0.18, "#3a3040") for x in (600, 760, 900, 1050, 1200))
    c.append(cekim(4, bg + uzak + tarla(0, 900, 1920, 180), d,
                   aktorler=[kisi(760, ZEMIN, 0.95, ifade="uzgun", bak=(5, -3), kol="tut", esya="orak", **SEN)],
                   kb=KB(1.0, 1.06, (0.42, 0.6))))
    d, bg = bg_bolunmus(("#6d7780", "#a5adb3"), ("#f3b04a", "#fbe08a"))
    bg += gemi(1500, 830, 0.55) + uzun_ev(420, 830, w=520, s=0.6)
    bg += serit_baslik(960, 140, "RAGNAR ZAMANINDA", 54, rot=-2)
    bg += buyuk_yazi(960, 300, "VİKİNG KÖYLÜSÜ", 120, sw=12)
    bg += buyuk_yazi(960, 430, "OLSAYDIN?", 92, fill="#ffffff", sw=10)
    c.append(cekim(7, bg, d, aktorler=[kisi(560, ZEMIN, 0.85, ifade="saskin", **SEN),
                                       kisi(1390, ZEMIN, 0.85, kol="tek_yukari", esya="kilic", **RAGNAR)],
                   kb=KB(1.04, 1.0)))
    return c


def s02():
    c = []
    bg = '<rect width="1920" height="1080" fill="#3a2a1e"/>' + parsomen(260, 140, 1400, 800)
    bg += T(960, 300, "ANNALES · DCCCXLV", 64, fill="#6b4a2a", font="Cinzel")
    bg += T(960, 390, "Reginherus, dux Nordmannorum...", 48, fill="#6b4a2a", font="Cinzel", weight=700)
    bg += "".join(L(420, 470 + i * 52, 1500 - (i % 3) * 120, 470 + i * 52, sw=6, stroke="#b39a6a") for i in range(6))
    bg += T(1450, 860, "?", 300, fill="#b3262b", font="Cinzel", stroke=OUT, sw=10)
    c.append(cekim(0, bg + etiket(960, 900, "GERÇEK Mİ?", 52), aktorler=[], kb=KB(1.0, 1.08, (0.5, 0.5), (0.5, 0.42))))
    d = rad_grad("cukur", [(0, "#4a6a2a", 1), (1, "#1a2410", 1)])
    bg = f'<rect width="1920" height="1080" fill="#1b1410"/>' + E(960, 900, 760, 220, "url(#cukur)", sw=8)
    yilan = ""
    for i in range(9):
        x0 = 380 + i * 135
        yilan += P(f"M{x0},960 q30,-60 0,-110 q-30,-50 10,-100", sw=26, stroke=OUT) + P(f"M{x0},960 q30,-60 0,-110 q-30,-50 10,-100", sw=16, stroke=["#5f8f3a", "#8faa3a"][i % 2])
        yilan += C(x0 + 10, 750, 18, ["#5f8f3a", "#8faa3a"][i % 2], sw=5)
    c.append(cekim(2, bg + yilan + serit_baslik(960, 140, "EFSANE: YILAN ÇUKURU", 50), d,
                   aktorler=[kisi(960, 980, 0.9, ifade="kizgin", kol="yukari", **RAGNAR)], kb=KB(1.0, 1.07, (0.5, 0.55))))
    d, bg = bg_koy("gri", ev=True, ev_x=1500)
    c.append(cekim(4, bg, d, aktorler=[kisi(700, ZEMIN, 0.95, ifade="yorgun", kol="tut", esya="orak", **SEN)],
                   fx=["yagmur"], kb=KB(1.0, 1.06, (0.4, 0.6))))
    return c


def s03():
    c = []
    bg = '<rect width="1920" height="1080" fill="#e9dcc0"/>' + piramit()
    bg += etiket(1600, 330, "JARL", 56) + etiket(1660, 590, "KARL", 56) + etiket(1740, 850, "KÖLE", 56)
    akt = [kisi(960, 445, 0.55, kol="bel", **JARL), kisi(960, 705, 0.55, **SEN),
           kisi(760, 965, 0.55, **KOLE), kisi(1160, 965, 0.55, **KOLE)]
    c.append(cekim(0, bg, aktorler=akt, kb=KB(1.0, 1.04)))
    c.append(cekim(1, bg, aktorler=akt, kb=KB(1.25, 1.35, (0.55, 0.3))))
    c.append(cekim(2, bg, aktorler=akt, kb=KB(1.25, 1.35, (0.55, 0.78))))
    akt2 = akt[:1] + [kisi(960, 705, 0.55, ifade="mutlu", **SEN)] + akt[2:]
    c.append(cekim(4, bg + etiket(760, 560, "SEN", 48, bg="#f2c14e"), aktorler=akt2, kb=KB(1.25, 1.4, (0.52, 0.55))))
    d, bg = bg_koy("gunduz", ev_x=1450)
    kart = bilgi_karti(1000, 180, 820, "ÖZGÜR KÖYLÜ", ["Silah taşıyabilir", "Mecliste söz hakkı var", "Kimseye ait değil"], 44, ikon="tik")
    c.append(cekim(6, bg + kart, d, aktorler=[kisi(560, ZEMIN, 0.95, ifade="mutlu", kol="tut", esya="balta", **SEN)]))
    d, bg = bg_koy("gri", ev_x=1500)
    c.append(cekim(7, bg + tarla(0, 900, 1920, 180, renk="#a89a5a", koyu="#7f7340"), d,
                   aktorler=[kisi(800, ZEMIN, 0.95, ifade="uzgun", kol="bel", **SEN)], kb=KB(1.0, 1.08, (0.45, 0.6))))
    return c


def s04():
    c = []
    d, bg = bg_ic()
    akt = [ates_aktor(960, 900, 0.9), kisi(560, 990, 0.9, kol="bel", ifade="sert", sac="kahve", govde="mavi", sakal="uzun"),
           kisi(1380, 990, 0.85, ifade="yorgun", **{**ES, "kol": "onde"})]
    bebek = G(E(0, 0, 70, 30, "#8c7a5a", sw=5) + E(0, -24, 30, 44, "#efe6d2", sw=5) + C(0, -64, 22, TEN, sw=5), 760, 975)
    c.append(cekim(0, bg + bebek, d, aktorler=akt, fx=["kivilcim:960,820", "isik"], kb=KB(1.0, 1.06, (0.45, 0.6))))
    akt2 = [ates_aktor(960, 900, 0.9), kisi(700, 990, 0.95, kol="kaldir", esya="bebek", ifade="mutlu", sac="kahve", govde="mavi", sakal="uzun"),
            kisi(1380, 990, 0.85, ifade="mutlu", **{**ES, "kol": "onde"})]
    c.append(cekim(3, bg + etiket(700, 330, "KABUL EDİLDİ!", 48, bg="#f2c14e"), d, aktorler=akt2, fx=["kivilcim:960,820", "isik"],
                   kb=KB(1.05, 1.12, (0.4, 0.5))))
    c.append(cekim(4, bg + bilgi_karti(1150, 160, 680, "İSİM VERME", ["Bebeğe su serpilir", "Çoğu zaman", "bir atanın adı verilir"], 42), d,
                   aktorler=[ates_aktor(960, 900, 0.9), kisi(600, 990, 0.95, kol="onde", esya="kase", ifade="mutlu", sac="kahve", govde="mavi", sakal="uzun")],
                   fx=["isik"], kb=KB(1.0, 1.05, (0.5, 0.5))))
    d, bg = bg_koy("gri", ev=True, ev_x=960, kar=True)
    ikon = (G(C(0, 0, 90, "#cfe8f2", sw=6) + "".join(L(0, 0, 60 * math.cos(a), 60 * math.sin(a), sw=8, stroke="#4f8fb8") for a in [i * math.pi / 3 for i in range(6)]), 480, 300)
            + G(C(0, 0, 90, "#f3e6c4", sw=6) + P("M-50,-5 Q0,60 50,-5 Z", fill="#8a5a35", sw=5), 960, 300)
            + G(C(0, 0, 90, "#f8d0c0", sw=6) + C(0, 0, 50, TEN, sw=5) + L(-20, -10, -8, -10, sw=5) + L(8, -10, 20, -10, sw=5) + P("M-14,22 Q0,10 14,22", sw=5), 1440, 300))
    ikon += etiket(480, 450, "SOĞUK", 40) + etiket(960, 450, "AÇLIK", 40) + etiket(1440, 450, "HASTALIK", 40)
    c.append(cekim(7, bg + ikon, d, fx=["kar"], kb=KB(1.0, 1.05)))
    return c


def s05():
    c = []
    d, bg = bg_koy("gunduz", ev=False)
    bg += uzun_ev(960, 860, w=1100, s=1.0)
    bg += P("M410,960 L1510,960", sw=6) + P("M410,940 L410,980 M1510,940 L1510,980", sw=6) + etiket(960, 1010, "20 - 30 METRE", 44)
    c.append(cekim(0, bg, d, fx=["duman:960,500"], aktorler=[aktor(koyun(300, 990, 0.8)), aktor(keci(1700, 990, 0.8, flip=True))],
                   kb=KB(1.0, 1.06, (0.5, 0.5))))
    d, bg = bg_ic()
    c.append(cekim(2, bg + etiket(960, 120, "PENCERE YOK!", 50, bg="#f2c14e"), d,
                   aktorler=[ates_aktor(960, 900, 0.9), kisi(1350, 990, 0.95, ifade="yorgun", kol="tara", **SEN)],
                   fx=["duman:960,700", "kivilcim:960,820", "isik"], kb=KB(1.0, 1.1, (0.55, 0.55), (0.5, 0.3))))
    akt = [ates_aktor(960, 900, 0.8),
           kisi(260, 985, 0.75, ifade="mutlu", sac="kahve", govde="mavi", sakal="uzun"),
           kisi(470, 985, 0.75, ifade="normal", **ES),
           kisi(1420, 985, 0.72, ifade="yorgun", kadin=True, yasli=True, bas="basortu", bas_renk="#7d7a72", govde="koyu"),
           kisi(1640, 985, 0.6, ifade="mutlu", sakal=None, biyik=False, sac="sari", govde="kirmizi"),
           kisi(1800, 985, 0.72, **KOLE)]
    c.append(cekim(5, bg + etiket(960, 120, "HERKES AYNI ÇATI ALTINDA", 46), d, aktorler=akt, fx=["isik"], kb=KB(1.0, 1.05)))
    d, bg = bg_ic(700)
    bg2 = bg + cit(1150, 1900, 990) + inek(1450, 900, 1.0) + inek(1760, 905, 0.9, renk="#5a3a24")
    c.append(cekim(8, bg2 + etiket(1600, 620, "CANLI SOBA", 50, bg="#f2c14e"), d,
                   aktorler=[ates_aktor(700, 900, 0.8), kisi(900, 990, 0.95, ifade="yorgun", **SEN)], fx=["isik"],
                   kb=KB(1.0, 1.08, (0.6, 0.6))))
    return c


def s06():
    c = []
    d, bg = bg_koy("sabah", ev_x=1450)
    c.append(cekim(0, bg + cit(80, 640, 990), d,
                   aktorler=[kisi(860, ZEMIN, 0.95, ifade="yorgun", kol="tut", esya="balta", **SEN), aktor(inek(420, 960, 0.75)),
                             aktor(koyun(1140, 990, 0.7))], fx=["duman:1450,520"], kb=KB(1.0, 1.06, (0.45, 0.6))))
    d, bg = bg_ic(None)
    masa = yemek_masasi(960, 870, 1.25)
    lab = etiket(510, 700, "LAPA", 38) + etiket(772, 650, "YASSI EKMEK", 38) + etiket(1072, 700, "SKYR", 38) + etiket(1340, 650, "KURU BALIK", 38) + etiket(1555, 590, "BİRA", 38)
    c.append(cekim(2, bg + masa + lab + serit_baslik(960, 130, "DAGMAL: GÜNÜN İLK YEMEĞİ", 48), d, fx=["isik"], kb=KB(1.0, 1.08, (0.5, 0.65))))
    d, bg = bg_ic(560)
    kart = bilgi_karti(1060, 180, 760, "GÜNDE 2 ÖĞÜN", ["DAGMAL  ·  sabah", "NATTMAL  ·  akşam"], 46)
    c.append(cekim(5, bg + kart, d, aktorler=[ates_aktor(560, 900, 0.8), kisi(820, 990, 1.0, ifade="mutlu", kol="onde", esya="kase", **SEN)],
                   fx=["isik"], kb=KB(1.0, 1.05, (0.5, 0.55))))
    return c


def s07():
    c = []
    d, bg = bg_koy("gunduz", ev=True, ev_x=1600)
    bg += tarla(0, 870, 1920, 210)
    c.append(cekim(0, bg + etiket(400, 140, "KISA YAZ", 50, bg="#f2c14e"), d,
                   aktorler=[kisi(760, 1010, 1.0, ifade="normal", kol="tut", esya="orak", **SEN)], kb=KB(1.0, 1.06, (0.45, 0.6))))
    d, bg = bg_koy("gunduz", ev=False, seed=4)
    bg += cit(60, 1860, 1050)
    c.append(cekim(3, bg, d, aktorler=[aktor(inek(420, 900, 0.9)), aktor(koyun(820, 950, 0.9)), aktor(keci(1180, 950, 0.95, flip=True)),
                                       aktor(domuz(1520, 970, 0.9, flip=True)), kisi(1760, ZEMIN, 0.8, ifade="mutlu", **SEN)],
                   kb=KB(1.0, 1.05)))
    d, bg = bg_koy("gunduz", ev=False, seed=7)
    bg += saman(380, 960, 1.4) + saman(1500, 940, 1.1) + saman(1720, 970, 1.3)
    c.append(cekim(4, bg + etiket(960, 140, "OT YETMEZSE HAYVANLAR KESİLİR", 46), d,
                   aktorler=[kisi(940, ZEMIN, 1.0, ifade="sert", kol="kurek", **SEN), aktor(tirpan(900, 960, 1.0))],
                   kb=KB(1.0, 1.06, (0.5, 0.6))))
    d, bg = bg_deniz("gunduz")
    bg += tepeler(860, "#6fa34a", seed=8) + kurutma_rafi(560, 990, 1.4) + fici(1260, 1000, 1.2) + fici(1420, 1010, 1.0, "#7b4a25")
    bg += etiket(560, 520, "KURU BALIK", 44) + etiket(1340, 780, "TUZLU ET", 44)
    c.append(cekim(6, bg, d, kb=KB(1.0, 1.05)))
    d, bg = bg_koy("aksam", ev=True, ev_x=960, seed=2)
    c.append(cekim(7, bg + serit_baslik(960, 180, "BU KIŞI ÇIKARABİLECEK MİYİZ?", 56, rot=-1), d,
                   aktorler=[kisi(600, ZEMIN, 0.95, ifade="uzgun", kol="bel", **SEN), kisi(1320, ZEMIN, 0.92, ifade="uzgun", **ES)],
                   kb=KB(1.0, 1.06)))
    return c


def s08():
    c = []
    d, bg = bg_ic(None)
    bg += dokuma_tezgahi(1300, 990, 1.25)
    c.append(cekim(0, bg, d, aktorler=[kisi(860, 990, 1.0, ifade="sert", **{**ES, "kol": "onde"})], fx=["isik"], kb=KB(1.0, 1.06, (0.55, 0.55))))
    d, bg = bg_deniz("gunduz")
    bg += gemi(600, 980, 0.85)
    bg += bilgi_karti(1060, 200, 760, "TEK BİR YELKEN", ["Yıllar süren", "eğirme ve dokuma"], 50)
    c.append(cekim(2, bg + dokuma_tezgahi(1600, 1030, 0.7), d,
                   kb=KB(1.0, 1.06)))
    d, bg = bg_ic(None)
    c.append(cekim(3, bg + etiket(430, 700, "EVİN ANAHTARLARI", 46, bg="#f2c14e") + P("M560,740 Q680,800 780,900", sw=8), d,
                   aktorler=[kisi(860, 1040, 1.25, ifade="mutlu", **{**ES, "kol": "bel"})], fx=["isik"],
                   kb=KB(1.05, 1.18, (0.47, 0.6))))
    kart = bilgi_karti(1000, 220, 820, "VİKİNG KADINI", ["Mülk sahibi olabilir", "Boşanabilir"], 48, ikon="tik")
    c.append(cekim(6, bg + kart, d, aktorler=[kisi(560, 990, 1.0, ifade="sert", **{**ES, "kol": "bel"})], fx=["isik"]))
    return c


def s09():
    c = []
    d, bg = bg_bolunmus(("#5f7a8c", "#8fa6b4"), ("#f2c14e", "#f8e08a"), zigzag=True)
    c.append(cekim(0, bg + T(1450, 560, "!", 420, fill="#b3262b", font="Cinzel", stroke=OUT, sw=12), d,
                   aktorler=[kisi(700, ZEMIN, 1.05, ifade="saskin", kol="yukari", **SEN)], kb=KB(1.0, 1.08, (0.45, 0.55))))
    bg = '<rect width="1920" height="1080" fill="#e9dcc0"/>' + R(160, 260, 1600, 560, "#c9b48c", sw=8, rx=20)
    esya = (G(R(-110, -26, 220, 52, "#e9dcc0", sw=5, rx=10) + "".join(L(-95 + i * 14, 26, -95 + i * 14, 80, sw=4) for i in range(14)), 450, 520)
            + G(P("M-10,-120 L10,-120 L40,100 L28,104 L0,-80 L-28,104 L-40,100 Z", fill="#d7a64a", sw=5), 830, 560)
            + G(L(0, -110, 0, 100, sw=12) + L(0, -110, 0, 100, sw=6, stroke="#d7a64a") + E(0, -118, 14, 10, "#d7a64a", sw=4), 1130, 560)
            + G(R(-90, -60, 180, 120, "#efe3c0", sw=6, rx=30) + E(-20, -10, 30, 16, "#ffffff", sw=0) + C(40, 20, 12, "#ffffff", sw=0), 1460, 560))
    lab = etiket(450, 720, "TARAK", 40) + etiket(830, 720, "CIMBIZ", 40) + etiket(1130, 720, "KULAK KAŞIĞI", 40) + etiket(1460, 720, "SABUN", 40)
    c.append(cekim(2, bg + esya + lab + serit_baslik(960, 160, "VİKİNG MEZARLARINDAN", 50), kb=KB(1.0, 1.06)))
    d, bg = bg_ic(None)
    kart = bilgi_karti(980, 170, 860, "CUMARTESİ", ["laugardagr", "= YIKANMA GÜNÜ"], 54)
    c.append(cekim(4, bg + kart, d, aktorler=[kisi(560, 990, 1.0, ifade="mutlu", kol="tara", esya="tarak", **SEN)], fx=["isik"]))
    d, bg = bg_koy("gunduz", ev_x=1600)
    akt = [kisi(620, ZEMIN, 1.0, ifade="mutlu", kol="tara", esya="tarak", **SEN),
           kisi(1180, ZEMIN, 0.85, ifade="mutlu", kadin=True, sac="kahve", govde="mavi", bas="basortu", bas_renk="#e3d3b0", bak=(-6, 0)),
           kisi(1420, ZEMIN, 0.85, ifade="mutlu", kadin=True, sac="siyah", govde="kirmizi", bak=(-6, 0))]
    c.append(cekim(6, bg + kalp(1180, 520, 0.9) + kalp(1420, 520, 0.9) + kalp(1300, 440, 0.7) + etiket(1300, 160, "İNGİLİZ KRONİĞİ", 44), d,
                   aktorler=akt, kb=KB(1.0, 1.06)))
    return c


def s10():
    c = []
    d, bg = bg_koy("gunduz", ev=True, ev_x=1650, seed=3)
    bg += tarla(0, 900, 1920, 180)
    c.append(cekim(0, bg, d, aktorler=[kisi(620, 1000, 0.95, ifade="kizgin", kol="isaret", **SEN),
                                       kisi(1220, 1000, 0.95, ifade="kizgin", kol="bel", sac="kahve", govde="yesil", sakal="uzun", flip=True),
                                       aktor(inek(920, 950, 0.8))], kb=KB(1.0, 1.06)))
    d, bg = bg_koy("gunduz", ev=False, seed=9)
    bg += kaya(960, 900, 2.2)
    kalabalik = ""
    for i, x in enumerate(range(120, 1900, 150)):
        if 760 < x < 1160:
            continue
        kalabalik += insan(x, 1080, 0.7, sac=["sari", "kahve", "kizil", "siyah"][i % 4], govde=["kahve", "yesil", "mavi", "yun", "kirmizi"][i % 5],
                           kol="tek_yukari" if i % 3 == 0 else "asagi", esya="mizrak" if i % 3 == 0 else None, ifade="sert")
    c.append(cekim(2, bg + kalabalik + serit_baslik(960, 130, "TİNG: ÖZGÜR ERKEKLERİN MECLİSİ", 48), d,
                   aktorler=[kisi(960, 730, 0.8, kol="isaret", ifade="sert", yasli=True, sakal="uzun", govde="mavi", pelerin="koyu")],
                   kb=KB(1.0, 1.06, (0.5, 0.5))))
    d, bg = bg_bolunmus(("#e3c46a", "#f2dc94"), ("#5a1f1f", "#8c2f2f"), zigzag=True)
    bg += sandik(480, 820, 1.6) + etiket(480, 300, "KAN BEDELİ", 56, bg="#ffffff")
    kilic = lambda x, r: G(P("M-8,0 L-8,-300 L0,-330 L8,-300 L8,0 Z", fill="#d7dce0", sw=5) + R(-40, -6, 80, 16, "#7b5a2a", sw=5, rx=4) + R(-8, 10, 16, 60, "#4a2c17", sw=4), x, 900, rot=r)
    bg += kilic(1380, -25) + kilic(1520, 25) + etiket(1450, 300, "KAN DAVASI", 56)
    c.append(cekim(5, bg, d, kb=KB(1.0, 1.05)))
    d, bg = bg_koy("gri", ev=False, seed=11)
    orman = "".join(cam(x, 860 + (i % 2) * 40, 1.1 + (i % 3) * 0.2, "#2a4a32") for i, x in enumerate(range(80, 1900, 170)))
    c.append(cekim(7, bg + orman + etiket(1400, 220, "KANUN DIŞI", 60, bg="#b3262b", fg="#ffffff"), d,
                   aktorler=[kisi(800, ZEMIN, 0.95, ifade="uzgun", govde="gri", yirtik=True, sac="kahve", sakal="uzun")],
                   fx=["yagmur"], kb=KB(1.0, 1.08, (0.45, 0.6))))
    return c


def s11():
    c = []
    d, bg = bg_koy("aksam", ev=True, ev_x=1550, seed=5)
    c.append(cekim(0, bg, d, aktorler=[kisi(760, ZEMIN, 1.0, ifade="saskin", kol="yukari", bak=(0, -6), **SEN)], kb=KB(1.0, 1.06, (0.45, 0.55))))
    d, bg = gokyuzu("#2a3550", "#6a7aa0", gid="odin")
    bg += bulut(960, 900, 4.5, "#c9d2e0") + bulut(300, 200, 1.4, "#8a96b5", 0.8) + bulut(1650, 260, 1.2, "#8a96b5", 0.8)
    bg += kuzgun(560, 380, 1.3) + kuzgun(1380, 340, 1.3, flip=True) + etiket(960, 120, "ODİN", 60, bg="#f2c14e")
    c.append(cekim(1, bg, d, aktorler=[aktor(odin(960, 900, 1.25))], kb=KB(1.0, 1.06)))
    d, bg = gokyuzu("#1f2a3a", "#55657a", gid="thor")
    bg += bulut(960, 920, 4.5, "#9aa6b5") + simsek(300, 120, 1.3) + simsek(1580, 160, 1.1) + etiket(960, 120, "THOR", 60, bg="#f2c14e")
    c.append(cekim(4, bg, d, aktorler=[kisi(960, 930, 1.25, ifade="kizgin", kol="tek_yukari", esya="cekic", sac="kizil", sakal="uzun", govde="kirmizi")],
                   fx=["simsek"], kb=KB(1.0, 1.07)))
    d, bg = bg_ic(None)
    ic_kare = (C(1380, 500, 250, "#f3e6c4", sw=8, extra='filter="url(#golge)"')
               + G(P("M-22,-120 L22,-120 L22,30 L85,30 Q95,90 70,125 L-70,125 Q-95,90 -85,30 L-22,30 Z", fill="#d7dce0", sw=8)
                   + C(0, -146, 24, "none", sw=8) + P("M-60,62 Q0,80 60,62", sw=4, stroke="#9aa3ab") + P("M-55,95 Q0,112 55,95", sw=4, stroke="#9aa3ab"), 1380, 500, 1.15))
    c.append(cekim(5, bg + ic_kare + etiket(1380, 820, "THOR'UN ÇEKİCİ", 48, bg="#f2c14e") + P("M1130,560 Q900,700 760,840", sw=8, extra='stroke-dasharray="18 14"'), d,
                   aktorler=[kisi(620, 1380, 1.8, ifade="mutlu", **SEN)], fx=["isik"], kb=KB(1.0, 1.06, (0.55, 0.5))))
    d, bg = gokyuzu("#9fd0ee", "#fdf0c4", gid="freyr")
    bg += gunes(960, 300, 120) + tarla(0, 820, 1920, 260) + etiket(960, 110, "FREYR: BEREKET", 56, bg="#f2c14e")
    c.append(cekim(6, bg, d, aktorler=[kisi(960, 1000, 1.15, ifade="mutlu", kol="tut", esya="basak", sac="sari", sakal="kisa", govde="yesil", bas="bant", bas_renk="#d9a63a")],
                   kb=KB(1.0, 1.06)))
    d, bg = bg_koy("aksam", ev=False, seed=12)
    akt = [ates_aktor(960, 940, 1.2)]
    for i, (x, f) in enumerate([(380, False), (620, False), (1300, True), (1540, True)]):
        akt.append(kisi(x, ZEMIN, 0.85, ifade="mutlu", kol="tut", esya="boynuz", flip=f,
                        sac=["sari", "kahve", "kizil", "siyah"][i], govde=["kahve", "mavi", "yesil", "kirmizi"][i]))
    c.append(cekim(8, bg + serit_baslik(960, 140, "BLÓT: KURBAN ŞÖLENİ", 52), d, aktorler=akt, fx=["kivilcim:960,800"], kb=KB(1.0, 1.05)))
    d, bg = bg_bolunmus(("#f2c14e", "#fbe8a8"), ("#1a1d24", "#3a3f4a"), zigzag=True)
    bg += salon(470, 900, 1.0) + hel_kapisi(1450, 900, 1.0)
    bg += etiket(470, 200, "VALHALLA", 58) + etiket(1450, 200, "HEL", 58, bg="#3a3f4a", fg="#ffffff")
    bg += etiket(470, 300, "SAVAŞTA ÖLENLER", 36) + etiket(1450, 300, "YATAKTA ÖLENLER", 36, bg="#3a3f4a", fg="#ffffff")
    c.append(cekim(9, bg, d, aktorler=[kisi(1150, ZEMIN, 0.85, ifade="uzgun", **SEN)], kb=KB(1.0, 1.05)))
    return c


def s12():
    c = []
    d, bg = bg_deniz("gunduz")
    bg += tepeler(840, "#6fa34a", seed=21) + uzun_ev(380, 860, w=500, s=0.6) + gemi(1450, 900, 0.8)
    c.append(cekim(0, bg, d, aktorler=[kisi(960, ZEMIN, 1.0, kol="boru", esya="boru", **{**JARL, "sac": "kahve", "pelerin": None, "govde": "mavi"}),
                                       kisi(620, ZEMIN, 0.85, ifade="saskin", **SEN)], kb=KB(1.0, 1.06)))
    d, bg = bg_bolunmus(("#a8c86a", "#e3d38a"), ("#2a5a7a", "#6fa8c8"), zigzag=True)
    bg += tarla(0, 820, 900, 260) + uzun_ev(400, 820, w=420, s=0.55) + gemi(1500, 960, 0.6)
    bg += etiket(400, 160, "1. TARLA", 56) + etiket(1500, 160, "2. KÜREK", 56)
    bg += etiket(400, 250, "GÜVENLİ AMA FAKİR", 36) + etiket(1500, 250, "GÜMÜŞ YA DA ÖLÜM", 36)
    c.append(cekim(3, bg, d, aktorler=[kisi(960, ZEMIN, 0.95, ifade="saskin", bak=(-7, 0), **SEN)], kb=KB(1.0, 1.04)))
    bg = '<rect width="1920" height="1080" fill="#e9dcc0"/>'
    for i, (renk, baslik, alt, x) in enumerate([("#8fc46a", "BAHAR", "TOHUM", 380), ("#f2c14e", "YAZ", "AKIN", 960), ("#d98a3a", "SONBAHAR", "HASAT", 1540)]):
        bg += C(x, 520, 210, renk, sw=8) + T(x, 500, baslik, 56, fill=OUT, font="Cinzel") + T(x, 580, alt, 46, fill="#fff", stroke=OUT, sw=8)
        if i < 2:
            bg += P(f"M{x+225},520 L{x+355},520 M{x+325},490 L{x+355},520 L{x+325},550", sw=12)
    c.append(cekim(8, bg + serit_baslik(960, 170, "YARI ZAMANLI VİKİNG", 52), kb=KB(1.0, 1.05)))
    d, bg = bg_deniz("gunduz")
    bg += tepeler(880, "#c9b48c", seed=22)
    c.append(cekim(10, bg, d, aktorler=[aktor(gemi(1350, 930, 0.9), anim="sallan"),
                                        kisi(620, ZEMIN, 1.05, ifade="sert", kol="kurek", **SEN), aktor(_esya_kurek(620))],
                   kb=KB(1.0, 1.07, (0.45, 0.55))))
    return c


def _esya_kurek(x):
    return G(L(-140, -380, 120, -40, sw=18) + L(-140, -380, 120, -40, sw=10, stroke="#a0703f")
             + P("M100,-70 L170,40 Q160,64 140,58 L80,-50 Z", fill="#a0703f", sw=5), x, ZEMIN)


def s13():
    c = []
    d, bg = bg_deniz("firtina")
    c.append(cekim(0, bg, d, aktorler=[aktor(gemi(960, 960, 1.15, insan_sayisi=6), anim="sallan")], fx=["yagmur"], kb=KB(1.0, 1.06)))
    d, bg = bg_deniz("gece")
    deck = R(-10, 860, 1940, 240, "#7b4a25", sw=6) + "".join(L(0, 900 + i * 40, 1920, 900 + i * 40, sw=3, stroke="#4a2c17") for i in range(5))
    tulum = "".join(G(E(0, 0, 170, 50, "#8c6a4a", sw=5) + C(-150, -10, 40, TEN, sw=5) + P("M-170,-20 Q-160,-6 -150,-20", sw=4) + P("M-140,-20 Q-130,-6 -120,-20", sw=4), x, 960) for x in (380, 1500))
    c.append(cekim(2, bg + deck + tulum + etiket(960, 140, "KABİN YOK", 50, bg="#f2c14e"), d,
                   aktorler=[kisi(960, 1060, 1.0, ifade="yorgun", kol="onde", **SEN)], kb=KB(1.0, 1.06, (0.5, 0.6))))
    d, bg = bg_deniz("gunduz")
    bg += gemi(960, 700, 1.1, yelken=False, kurek=False)
    bg += L(300, 640, 1620, 640, sw=6, stroke="#ffffff", extra='stroke-dasharray="30 20"') + etiket(1650, 600, "SU HATTI", 40)
    bg += bilgi_karti(560, 780, 800, "SIĞ GÖVDE", ["Denizden nehre girebilir"], 48)
    c.append(cekim(4, bg, d, kb=KB(1.0, 1.05)))
    bg = harita() + etiket(1500, 200, "İSKANDİNAVYA", 44) + etiket(960, 1010, "PARİS", 44, bg="#f2c14e") + etiket(760, 830, "SEN NEHRİ", 40)
    c.append(cekim(6, bg + gemi(1300, 470, 0.18), kb=KB(1.0, 1.15, (0.6, 0.45), (0.5, 0.75))))
    return c


def s14():
    c = []
    d, bg = gokyuzu("#e9875a", "#f8d38c", gid="pargok")
    bg += P(f"M0,760 L1920,760 L1920,1080 L0,1080 Z", fill="#4f8fb8", sw=0, stroke="none") + paris(960, 800, 1.1)
    bg += gemi(260, 1020, 0.4) + gemi(1660, 1030, 0.42, flip=True) + buyuk_yazi(960, 200, "PARİS · 845", 120)
    c.append(cekim(0, bg, d, fx=["duman:760,520", "duman:1200,500"], kb=KB(1.0, 1.06)))
    d, bg = bg_bolunmus(("#6b4a7a", "#a07ab0"), ("#f2c14e", "#fbe8a8"), zigzag=True)
    bg += sandik(1350, 960, 1.4) + sandik(1650, 980, 1.2) + etiket(480, 160, "KEL CHARLES", 56) + etiket(1500, 160, "VİKİNGLER", 56)
    c.append(cekim(3, bg, d, aktorler=[aktor(kel_charles(500, ZEMIN, 0.95)), kisi(1500, 760, 0.7, ifade="mutlu", kol="bel", **RAGNAR)], kb=KB(1.0, 1.05)))
    bg = '<rect width="1920" height="1080" fill="#2b2118"/>' + sandik(560, 900, 2.2) + sandik(1100, 920, 1.8) + sandik(1500, 940, 1.5)
    bg += bilgi_karti(460, 120, 1000, "7.000 LİBRE", ["≈ 2,5 TON GÜMÜŞ VE ALTIN"], 56)
    c.append(cekim(4, bg, kb=KB(1.0, 1.07, (0.5, 0.6))))
    d, bg = bg_koy("gunduz", ev=True, ev_x=1550)
    bg += sikke(1150, 420, 1.2) + sikke(1260, 380, 1.2) + sikke(1370, 430, 1.2) + bilezik(1260, 530, 1.4)
    c.append(cekim(5, bg + etiket(1260, 660, "SENİN PAYIN", 48, bg="#f2c14e"), d,
                   aktorler=[kisi(720, ZEMIN, 1.0, ifade="mutlu", kol="tut", esya="kese", **SEN)], kb=KB(1.0, 1.06)))
    return c


def s15():
    c = []
    d, bg = bg_koy("gri", ev=False, seed=13)
    bg += cadir(400, 900, 1.2) + cadir(1500, 880, 1.0) + cadir(1150, 860, 0.8)
    bg += yatan_insan(700, 1000, 1.1) + yatan_insan(1250, 1040, 1.0, battaniye="#8c6a4a", sac="#e0a93b", flip=True)
    c.append(cekim(0, bg + etiket(960, 150, "SALGIN", 60, bg="#b3262b", fg="#ffffff"), d, kb=KB(1.0, 1.06)))
    bg = '<rect width="1920" height="1080" fill="#e9dcc0"/>'
    bg += bilgi_karti(460, 260, 1000, "9. YÜZYILDA TIP", ["Antibiyotik yok", "Mikrop bilgisi yok"], 56, ikon="carpi")
    c.append(cekim(3, bg, kb=KB(1.0, 1.05)))
    d, bg = bg_ic(400)
    bg += yatan_insan(1150, 980, 1.3, sac="#3a2a20")
    c.append(cekim(4, bg + serit_baslik(960, 140, "SOĞAN ÇORBASI TESTİ", 52), d,
                   aktorler=[ates_aktor(400, 900, 0.8), kisi(700, 990, 1.0, ifade="uzgun", kadin=True, yasli=True, bas="basortu", bas_renk="#7d7a72", govde="koyu", kol="onde", esya="kase")],
                   fx=["isik"], kb=KB(1.0, 1.06)))
    d, bg = bg_koy("gunduz", ev=True, ev_x=1450)
    c.append(cekim(7, bg, d, aktorler=[kisi(700, ZEMIN, 1.0, ifade="mutlu", kol="tut", esya="kese", **SEN),
                                       kisi(1250, ZEMIN, 0.85, ifade="mutlu", kol="yukari", sac="kahve", govde="mavi", sakal="uzun", yasli=True),
                                       kisi(1500, ZEMIN, 0.8, ifade="mutlu", kadin=True, yasli=True, bas="basortu", bas_renk="#7d7a72", govde="koyu", kol="yukari")],
                   fx=["duman:1450,520"], kb=KB(1.0, 1.05)))
    return c


def s16():
    c = []
    d, bg = bg_koy("aksam", ev=True, ev_x=1600, seed=14)
    bg += sandik(260, 1010, 1.0) + etiket(260, 820, "BAŞLIK", 40) + sandik(1700, 1020, 0.9) + etiket(1700, 840, "ÇEYİZ", 40)
    akt = [ates_aktor(960, 1000, 0.9), kisi(780, ZEMIN, 0.95, ifade="mutlu", kol="tut", esya="boynuz", **SEN),
           kisi(1140, ZEMIN, 0.92, ifade="mutlu", flip=True, **{**ES, "kol": "tut", "esya": "boynuz"}),
           kisi(480, ZEMIN, 0.8, ifade="mutlu", sac="kahve", govde="mavi", sakal="uzun", yasli=True),
           kisi(1440, ZEMIN, 0.8, ifade="mutlu", sac="siyah", govde="kirmizi", sakal="uzun", yasli=True, flip=True)]
    c.append(cekim(0, bg + kalp(960, 420, 1.1) + serit_baslik(960, 140, "VİKİNG DÜĞÜNÜ", 54), d, aktorler=akt, fx=["kivilcim:960,880"], kb=KB(1.0, 1.05)))
    d, bg = bg_koy("gunduz", ev=True, ev_x=960, seed=15)
    akt = [kisi(560, ZEMIN, 0.95, ifade="mutlu", kol="bel", **SEN), kisi(1360, ZEMIN, 0.92, ifade="mutlu", **ES),
           kisi(1560, ZEMIN, 0.55, ifade="mutlu", sakal=None, biyik=False, sac="sari", govde="kirmizi"),
           aktor(koyun(300, 1000, 0.7)), aktor(inek(1780, 960, 0.6, flip=True))]
    c.append(cekim(6, bg + etiket(960, 150, "EVİN REİSİ", 54, bg="#f2c14e"), d, aktorler=akt, fx=["duman:960,560"], kb=KB(1.0, 1.05)))
    return c


def s17():
    c = []
    d, gok = gokyuzu("#06101c", "#1b3150", gid="kis")
    bg = gok + yildizlar(150, 600, seed=8) + aurora() + daglar(700, "#22344a", seed=17, kar=True)
    bg += tepeler(780, "#dfe8ef", seed=18) + uzun_ev(960, 860, w=900, s=0.9, kar=True) + tepeler(900, "#eef3f6", genlik=20, seed=19)
    c.append(cekim(0, bg, d, fx=["kar", "duman:960,550"], kb=KB(1.0, 1.07, (0.5, 0.45))))
    d, bg = bg_ic()
    akt = [ates_aktor(960, 900, 0.9), kisi(520, 990, 0.9, ifade="normal", kol="tut", esya="balta", **SEN),
           kisi(1400, 990, 0.88, ifade="normal", **{**ES, "kol": "onde"})]
    c.append(cekim(2, bg, d, aktorler=akt, fx=["kivilcim:960,820", "isik"], kb=KB(1.0, 1.05)))
    d2, bgx = bg_ic(None)
    bg2 = bgx + hnefatafl(960, 760, 1.2) + R(500, 980, 920, 120, "#6b4226", sw=6)
    c.append(cekim(3, bg2 + etiket(960, 130, "HNEFATAFL", 54, bg="#f2c14e"), d,
                   aktorler=[kisi(360, 1100, 1.0, ifade="sert", bak=(6, 4), **SEN), kisi(1560, 1100, 1.0, ifade="mutlu", flip=True, bak=(-6, 4), sac="kahve", govde="mavi", sakal="uzun")],
                   fx=["isik"], kb=KB(1.0, 1.06, (0.5, 0.6))))
    balon = E(1350, 330, 420, 200, "#ffffff", sw=7) + C(1020, 520, 30, "#ffffff", sw=6) + C(960, 580, 18, "#ffffff", sw=5)
    balon += gemi(1350, 420, 0.35) + T(1350, 230, "RAGNAR...", 56, fill=OUT, font="Cinzel")
    c.append(cekim(4, bg + balon, d, aktorler=[ates_aktor(960, 900, 0.9), kisi(700, 990, 1.0, ifade="mutlu", kol="isaret", yasli=True, sakal="uzun", govde="yun"),
                                                kisi(360, 990, 0.6, ifade="saskin", sakal=None, biyik=False, sac="sari", govde="kirmizi")],
                   fx=["kivilcim:960,820", "isik"], kb=KB(1.0, 1.06)))
    return c


def s18():
    c = []
    d, bg = bg_koy("gri", ev=True, ev_x=1550, kar=True, seed=20)
    bg += kuru_agac(300, 960, 1.4) + fici(1150, 1000, 1.0, "#6b5a4a")
    c.append(cekim(0, bg + etiket(1150, 760, "BOŞ", 40), d, aktorler=[kisi(760, ZEMIN, 1.0, ifade="uzgun", kol="tut", esya="kese", **SEN)],
                   fx=["kar"], kb=KB(1.0, 1.06)))
    c.append(cekim(3, bg + etiket(960, 150, "AĞAÇ KABUĞU EKMEĞİ", 52, bg="#f2c14e"), d,
                   aktorler=[kisi(560, ZEMIN, 1.0, ifade="yorgun", kol="onde", esya="kase", **SEN)], fx=["kar"], kb=KB(1.05, 1.1, (0.3, 0.6))))
    bg = '<rect width="1920" height="1080" fill="#d9ccb0"/>' + piramit()
    bg += P("M1260,660 Q1500,760 1260,880", sw=14, stroke="#b3262b") + P("M1240,840 L1262,882 L1300,850", sw=14, stroke="#b3262b")
    bg += etiket(1600, 590, "KARL", 56) + etiket(1660, 850, "KÖLE", 56)
    c.append(cekim(4, bg, aktorler=[kisi(960, 965, 0.55, **{**SEN, "govde": "gri", "yirtik": True}, tasma=True, ifade="uzgun"),
                                    kisi(960, 705, 0.55, ifade="saskin", **SEN)], kb=KB(1.1, 1.2, (0.5, 0.65))))
    return c


def s19():
    c = []
    d, bg = bg_ic()
    c.append(cekim(0, bg, d, aktorler=[ates_aktor(960, 900, 0.8), kisi(600, 990, 1.0, ifade="yorgun", yasli=True, sakal="uzun", **{k: v for k, v in SEN.items() if k != "sakal"})],
                   fx=["kivilcim:960,820", "isik"], kb=KB(1.0, 1.08, (0.4, 0.55))))
    d, bg = bg_deniz("safak")
    bg += gemi(960, 860, 0.9) + etiket(960, 150, "GEMİ GÖMÜSÜ: SADECE ZENGİNLERE", 46)
    c.append(cekim(4, bg, d, kb=KB(1.0, 1.05)))
    bg = '<rect width="1920" height="1080" fill="#3a2a1e"/>' + parsomen(260, 300, 1400, 480) + mezar_esyasi_kart()
    bg += etiket(520, 720, "BIÇAK", 40) + etiket(960, 720, "TARAK", 40) + etiket(1400, 720, "GÜMÜŞ BİLEZİK", 40)
    c.append(cekim(5, bg + serit_baslik(960, 180, "MEZAR EŞYALARI", 52), kb=KB(1.0, 1.05)))
    d, bg = bg_koy("aksam", ev=False, seed=23)
    bg += tas_gemi(960, 950, 1.3)
    c.append(cekim(6, bg + etiket(960, 150, "TAŞ GEMİ MEZAR", 54), d,
                   aktorler=[kisi(170, ZEMIN, 0.75, ifade="uzgun", **ES), kisi(1780, ZEMIN, 0.6, ifade="uzgun", sakal=None, biyik=False, sac="sari", govde="kirmizi")],
                   kb=KB(1.0, 1.06)))
    return c


def s20():
    c = []
    bg = '<rect width="1920" height="1080" fill="#2b2118"/>' + kitap(560, 800, 1.6) + lir(1360, 860, 1.4)
    bg += buyuk_yazi(960, 300, "RAGNAR", 180)
    c.append(cekim(0, bg, kb=KB(1.0, 1.06)))
    d, bg = bg_koy("gri", ev=False, seed=24)
    bg += G(P("M-90,0 L-80,-300 Q0,-360 80,-300 L90,0 Z", fill="#9a9a92", sw=7), 960, 980)
    c.append(cekim(2, bg + etiket(960, 760, "...", 60), d, kb=KB(1.0, 1.08)))
    bg = '<rect width="1920" height="1080" fill="#2b1b12"/>'
    for i, (x, renk) in enumerate([(320, "#86c0e6"), (960, "#4a2c17"), (1600, "#e3b448")]):
        bg += R(x - 300, 140, 600, 800, renk, sw=8, rx=10)
    bg += cam(250, 900, 1.2) + dokuma_tezgahi(1050, 900, 0.9) + tarla(1310, 760, 580, 170)
    bg += etiket(320, 990, "KERESTE", 40) + etiket(960, 990, "YELKEN", 40) + etiket(1600, 990, "ARPA", 40)
    akt = [kisi(400, 900, 0.75, ifade="sert", kol="tut", esya="balta", **SEN), kisi(800, 900, 0.75, ifade="sert", **{**ES, "kol": "onde"}),
           kisi(1600, 900, 0.75, ifade="mutlu", kol="tut", esya="orak", **SEN)]
    c.append(cekim(3, bg, aktorler=akt, kb=KB(1.0, 1.04)))
    d, bg = bg_deniz("safak")
    bg += tepeler(820, "#3f5a3a", seed=25) + "".join(gemi_silueti(x, 700, 0.3, "#3a3040") for x in (1200, 1400, 1600))
    c.append(cekim(4, bg, d, aktorler=[kisi(560, 900, 1.0, ifade="sert", bak=(6, -2), **SEN)], kb=KB(1.0, 1.07, (0.45, 0.5))))
    d, bg = bg_bolunmus(("#a8c86a", "#e3d38a"), ("#2a5a7a", "#6fa8c8"), zigzag=True)
    bg += tarla(0, 820, 900, 260) + gemi(1500, 960, 0.6) + etiket(400, 170, "TARLA", 60) + etiket(1500, 170, "KÜREK", 60)
    bg += serit_baslik(960, 330, "SEN OLSAN HANGİSİNİ SEÇERDİN?", 50, rot=-1)
    c.append(cekim(6, bg, d, aktorler=[kisi(960, ZEMIN, 0.95, ifade="saskin", **SEN)], kb=KB(1.0, 1.04)))
    bg = '<rect width="1920" height="1080" fill="#16100b"/>' + C(960, 420, 260, "#2b1f14", sw=0) + kum_saati(960, 420, 1.1)
    bg += buyuk_yazi(960, 790, "ZAMAN KIRIĞI", 120) + serit_baslik(960, 930, "ABONE OL", 56, rot=0)
    c.append(cekim(8, bg, kb=KB(1.0, 1.04)))
    return c


SAHNELER = {
    "s01_acilis": s01, "s02_ragnar": s02, "s03_piramit": s03, "s04_dogum": s04, "s05_uzun_ev": s05,
    "s06_yemek": s06, "s07_tarla": s07, "s08_kadinlar": s08, "s09_temizlik": s09, "s10_ting": s10,
    "s11_din": s11, "s12_cagri": s12, "s13_deniz": s13, "s14_paris": s14, "s15_salgin": s15,
    "s16_evlilik": s16, "s17_kis": s17, "s18_aclik": s18, "s19_olum": s19, "s20_kapanis": s20,
}
