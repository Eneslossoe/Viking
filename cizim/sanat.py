"""Zaman Kırığı tarzı düz 2D çizim kütüphanesi (SVG üretir).

Kalın koyu kontur, düz renkler, yuvarlak kafalı iri gözlü karakterler.
Koordinat sistemi: 1920x1080.
"""
import math
import random

W, H = 1920, 1080
OUT = "#2b1b12"

# ---------------------------------------------------------------- renkler
TEN = "#f3c99b"
TEN_GOLGE = "#e0a571"
SAC = {"sari": "#e0a93b", "kahve": "#7b4a25", "kizil": "#b8572a",
       "gri": "#cfcac1", "siyah": "#3a2a20", "beyaz": "#ece8e0"}
KUMAS = {"kahve": "#8c5a32", "yesil": "#6f7d3c", "kirmizi": "#a8452f",
         "mavi": "#4e6a86", "yun": "#b9a67a", "gri": "#7d7a72",
         "koyu": "#4a3b30", "mor": "#6b4a7a", "krem": "#e3d3b0"}


def P(d, fill="none", sw=5, stroke=OUT, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def C(cx, cy, r, fill, sw=5, stroke=OUT, extra=""):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def E(cx, cy, rx, ry, fill, sw=5, stroke=OUT, extra=""):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def R(x, y, w, h, fill, sw=5, rx=0, stroke=OUT, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def L(x1, y1, x2, y2, sw=5, stroke=OUT, extra=""):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" {extra}/>'


def G(icerik, x=0, y=0, s=1.0, flip=False, rot=0, extra=""):
    sx = -s if flip else s
    t = f"translate({x:.1f},{y:.1f}) rotate({rot}) scale({sx},{s})"
    return f'<g transform="{t}" {extra}>{icerik}</g>'


def T(x, y, metin, size=60, fill="#fff", font="Nunito", weight=900, anchor="middle",
      stroke=OUT, sw=0, extra=""):
    st = f'stroke="{stroke}" stroke-width="{sw}" paint-order="stroke" stroke-linejoin="round"' if sw else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-weight="{weight}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" {st} {extra}>{metin}</text>')


def svg(icerik, defs="", bg=None):
    arka = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{defs}</defs>{arka}{icerik}</svg>')


def lin_grad(gid, renkler, x2=0, y2=1):
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in renkler)
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{stops}</linearGradient>'


def rad_grad(gid, renkler, cx=0.5, cy=0.5, r=0.5):
    stops = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in renkler)
    return f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">{stops}</radialGradient>'


ORTAK_DEFS = (
    '<filter id="blur8"><feGaussianBlur stdDeviation="8"/></filter>'
    '<filter id="blur20"><feGaussianBlur stdDeviation="20"/></filter>'
    '<filter id="blur40"><feGaussianBlur stdDeviation="40"/></filter>'
    '<filter id="golge" x="-20%" y="-20%" width="140%" height="140%">'
    '<feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000" flood-opacity="0.35"/></filter>'
)


# ================================================================= KARAKTER
def _kol(omuz, dirsek, el, renk):
    pts = [omuz] + ([dirsek] if dirsek else []) + [el]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    return (P(d, sw=34, stroke=OUT) + P(d, sw=24, stroke=renk))


EL_POZ = {
    "asagi": {"L": (None, (-70, -138)), "R": (None, (70, -138))},
    "onde": {"L": ((-70, -175), (-30, -178)), "R": ((70, -175), (30, -178))},
    "yukari": {"L": ((-92, -280), (-100, -360)), "R": ((92, -280), (100, -360))},
    "tek_yukari": {"L": (None, (-70, -138)), "R": ((92, -285), (96, -365))},
    "bel": {"L": ((-92, -190), (-52, -152)), "R": ((92, -190), (52, -152))},
    "tut": {"L": (None, (-70, -138)), "R": ((82, -175), (92, -188))},
    "kaldir": {"L": ((-80, -310), (-34, -410)), "R": ((80, -310), (34, -410))},
    "tara": {"L": (None, (-70, -138)), "R": ((95, -270), (70, -372))},
    "boru": {"L": ((-60, -190), (-14, -262)), "R": ((66, -205), (34, -262))},
    "isaret": {"L": (None, (-70, -138)), "R": ((90, -240), (140, -268))},
    "kurek": {"L": ((-65, -185), (-24, -170)), "R": ((60, -190), (46, -168))},
}


def _esya(ad, el, ikinci_el=None):
    x, y = el
    if ad == "orak":
        return (L(x, y + 10, x, y - 60, sw=14, stroke=OUT) + L(x, y + 10, x, y - 60, sw=8, stroke="#8a5a35")
                + P(f"M{x},{y-58} Q{x+70},{y-110} {x+95},{y-40} Q{x+60},{y-85} {x},{y-48} Z", fill="#c9ced3", sw=5))
    if ad == "kurek":
        return (L(x - 110, y - 160, x + 70, y + 150, sw=16) + L(x - 110, y - 160, x + 70, y + 150, sw=9, stroke="#a0703f")
                + P(f"M{x+55},{y+120} L{x+105},{y+215} Q{x+95},{y+235} {x+80},{y+230} L{x+40},{y+135} Z", fill="#a0703f"))
    if ad == "balta":
        return (L(x, y + 40, x, y - 120, sw=16) + L(x, y + 40, x, y - 120, sw=9, stroke="#8a5a35")
                + P(f"M{x},{y-115} L{x+28},{y-130} Q{x+55},{y-115} {x+52},{y-80} L{x},{y-90} Z", fill="#c9ced3"))
    if ad == "kilic":
        return (P(f"M{x-6},{y-14} L{x-6},{y-170} L{x},{y-190} L{x+6},{y-170} L{x+6},{y-14} Z", fill="#d7dce0", sw=4)
                + R(x - 22, y - 18, 44, 10, "#7b5a2a", sw=4, rx=4))
    if ad == "mizrak":
        return (L(x, y + 140, x, y - 200, sw=14) + L(x, y + 140, x, y - 200, sw=7, stroke="#8a5a35")
                + P(f"M{x},{y-250} L{x+14},{y-205} L{x},{y-195} L{x-14},{y-205} Z", fill="#c9ced3", sw=4))
    if ad == "kase":
        cx = (x + ikinci_el[0]) / 2 if ikinci_el else x
        return (P(f"M{cx-62},{y-2} Q{cx},{y+66} {cx+62},{y-2} Z", fill="#8a5a35")
                + E(cx, y - 2, 62, 13, "#e8d9a8", sw=4))
    if ad == "tarak":
        dis = "".join(L(x - 22 + i * 7, y + 6, x - 22 + i * 7, y + 22, sw=3) for i in range(7))
        return R(x - 26, y - 8, 52, 16, "#e9dcc0", sw=4, rx=6) + dis
    if ad == "bebek":
        cx = (x + ikinci_el[0]) / 2
        return (E(cx, y - 25, 34, 52, "#efe6d2", sw=5) + C(cx, y - 70, 24, TEN, sw=5)
                + P(f"M{cx-10},{y-72} Q{cx-6},{y-68} {cx-2},{y-72}", sw=3) + P(f"M{cx+2},{y-72} Q{cx+6},{y-68} {cx+10},{y-72}", sw=3)
                + P(f"M{cx-26},{y-20} L{cx+26},{y-5}", sw=3) + P(f"M{cx-26},{y+5} L{cx+26},{y+20}", sw=3))
    if ad == "boru":
        return P(f"M{x-10},{y-4} Q{x+80},{y-30} {x+150},{y-140} L{x+175},{y-120} Q{x+110},{y+5} {x},{y+14} Z",
                 fill="#d9c28c", sw=5)
    if ad == "kese":
        return (L(x, y, x, y + 20, sw=4) + P(f"M{x-20},{y+22} Q{x-34},{y+70} {x},{y+72} Q{x+34},{y+70} {x+20},{y+22} Z", fill="#9b7446")
                + C(x, y + 50, 6, "#e8e8e8", sw=3))
    if ad == "boynuz":
        return P(f"M{x-14},{y-20} Q{x-10},{y-80} {x+40},{y-100} L{x+44},{y-82} Q{x+8},{y-62} {x+10},{y-16} Z", fill="#e8d6a8", sw=5)
    if ad == "cekic":
        return (L(x, y + 20, x, y - 70, sw=18) + L(x, y + 20, x, y - 70, sw=10, stroke="#7b4a25")
                + R(x - 60, y - 135, 120, 70, "#9aa3ab", sw=6, rx=10) + L(x - 40, y - 100, x + 40, y - 100, sw=4, stroke="#6c757d"))
    if ad == "basak":
        s = ""
        for k in range(-2, 3):
            ex, ey = x + k * 16, y - 120 - abs(k) * 6
            s += L(x, y, ex, ey, sw=4, stroke="#b58a2a")
            s += E(ex, ey - 16, 8, 20, "#e8bd4a", sw=3)
        return s
    if ad == "kurek_tut":
        return ""
    return ""


def insan(x=0, y=0, s=1.0, flip=False, ten=TEN, sac="sari", sakal="kisa", biyik=True,
          govde="kahve", pantolon="#6b5a45", sarg="#b3a382", pelerin=None, bas=None,
          bas_renk="#b9a67a", kadin=False, onluk="krem", ifade="normal", goz="acik",
          bak=(0, 0), kol="asagi", esya=None, kolye=False, yasli=False, tasma=False,
          yirtik=False, anahtar=False, kemer=True, rot=0):
    """Ayak ortası (x,y) olan, ~410px boyunda bir karakter."""
    kel = sac is None
    sac_renk = SAC["kahve"] if kel else SAC.get(sac, sac)
    if yasli and sac in ("sari", "kahve", "kizil", "siyah"):
        sac_renk = SAC["gri"]
    govde_renk = KUMAS.get(govde, govde)
    g = []
    # pelerin (arkada)
    if pelerin:
        g.append(P("M-58,-238 Q-120,-120 -96,-30 L96,-30 Q120,-120 58,-238 Z", fill=KUMAS.get(pelerin, pelerin)))
    # uzun saç (kadın, arkada)
    if kadin and bas != "basortu" and not kel:
        g.append(P("M-72,-330 Q-95,-250 -70,-190 L70,-190 Q95,-250 72,-330 Z", fill=sac_renk))
    # bacaklar
    if not kadin:
        for sx in (-1, 1):
            x0 = 8 if sx > 0 else -30
            g.append(R(x0, -112, 22, 100, pantolon, sw=5))
            g.append(R(x0, -80, 22, 66, sarg, sw=4))
            g.append(L(x0 + 2, -70, x0 + 20, -60, sw=3) + L(x0 + 2, -52, x0 + 20, -42, sw=3) + L(x0 + 2, -34, x0 + 20, -24, sw=3))
            g.append(E(sx * 22, -10, 26, 12, "#4a2c17", sw=5))
    else:
        g.append(E(-22, -8, 22, 10, "#4a2c17", sw=5) + E(22, -8, 22, 10, "#4a2c17", sw=5))
    # gövde
    if kadin:
        g.append(P("M-46,-242 Q0,-254 46,-242 L84,-14 Q0,0 -84,-14 Z", fill=govde_renk))
        g.append(P("M-36,-232 L36,-232 L58,-30 Q0,-20 -58,-30 Z", fill=KUMAS.get(onluk, onluk), sw=4))
        g.append(E(-30, -226, 12, 16, "#d9a63a", sw=4) + E(30, -226, 12, 16, "#d9a63a", sw=4))
        g.append(P("M-30,-212 Q0,-190 30,-212", stroke="#c9b26a", sw=4))
    else:
        govde_d = "M-48,-242 Q0,-254 48,-242 L66,-108 " + (
            "L44,-95 L28,-108 L12,-94 L-4,-108 L-20,-95 L-36,-110 L-50,-96 L-66,-108 Z" if yirtik else "Q0,-96 -66,-108 Z")
        g.append(P(govde_d, fill=govde_renk))
        g.append(P("M-14,-246 L0,-222 L14,-246", sw=4))
        if kemer:
            g.append(R(-62, -168, 124, 15, "#4a2c17", sw=4) + R(-9, -170, 18, 19, "#d9a63a", sw=3))
    if anahtar:
        g.append(L(-44, -150, -48, -118, sw=3) + C(-48, -112, 7, "none", sw=3)
                 + L(-52, -106, -56, -84, sw=4, stroke="#d9a63a") + L(-44, -106, -42, -86, sw=4, stroke="#d9a63a"))
    if kolye:
        g.append(L(-22, -244, 0, -208, sw=2) + L(22, -244, 0, -208, sw=2)
                 + P("M-10,-208 L10,-208 L6,-198 L3,-198 L3,-186 L-3,-186 L-3,-198 L-6,-198 Z", fill="#d7dce0", sw=3))
    # kollar
    poz = EL_POZ.get(kol, EL_POZ["asagi"])
    kol_renk = govde_renk
    el_L = poz["L"][1]
    el_R = poz["R"][1]
    g.append(_kol((-46, -228), poz["L"][0], el_L, kol_renk))
    g.append(_kol((46, -228), poz["R"][0], el_R, kol_renk))
    # baş
    hy = -312
    g.append(C(-68, hy + 6, 14, ten, sw=5) + C(68, hy + 6, 14, ten, sw=5))
    g.append(C(0, hy, 72, ten, sw=5))
    if tasma:
        g.append(R(-34, -250, 68, 16, "#6c757d", sw=4, rx=6) + C(0, -236, 6, "#6c757d", sw=3))
    # saç
    if bas != "basortu" and not kel:
        if kadin:
            g.append(P(f"M-72,{hy-2} Q-74,{hy-82} 0,{hy-84} Q74,{hy-82} 72,{hy-2} Q60,{hy-40} 18,{hy-50} Q0,{hy-38} -18,{hy-50} Q-60,{hy-40} -72,{hy-2} Z", fill=sac_renk))
        else:
            g.append(P(f"M-72,{hy+4} Q-76,{hy-82} 0,{hy-86} Q76,{hy-82} 72,{hy+4} Q66,{hy-34} 30,{hy-46} Q0,{hy-56} -30,{hy-46} Q-66,{hy-34} -72,{hy+4} Z", fill=sac_renk))
    # sakal
    if not kadin and sakal:
        uzun = {"kisa": 58, "uzun": 112, "orgu": 120}.get(sakal, 58)
        g.append(P(f"M-66,{hy+10} Q-62,{hy+uzun*0.75} 0,{hy+uzun} Q62,{hy+uzun*0.75} 66,{hy+10} Q52,{hy+40} 30,{hy+36} Q0,{hy+52} -30,{hy+36} Q-52,{hy+40} -66,{hy+10} Z", fill=sac_renk))
        if sakal == "orgu":
            g.append(P(f"M-8,{hy+uzun-6} L8,{hy+uzun-6} L6,{hy+uzun+34} L-6,{hy+uzun+34} Z", fill=sac_renk, sw=4)
                     + R(-9, hy + uzun + 6, 18, 8, "#d9a63a", sw=3))
    if not kadin and biyik:
        g.append(P(f"M0,{hy+27} Q-20,{hy+19} -38,{hy+38} Q-18,{hy+33} 0,{hy+33} Q18,{hy+33} 38,{hy+38} Q20,{hy+19} 0,{hy+27} Z", fill=sac_renk, sw=4))
    # gözler
    for sx in (-1, 1):
        ex, ey = sx * 26, hy - 2
        if goz == "kapali":
            g.append(P(f"M{ex-17},{ey} Q{ex},{ey+11} {ex+17},{ey}", sw=5))
        else:
            g.append(C(ex, ey, 19, "#ffffff", sw=4))
            pr = 5.5 if ifade == "korku" else 7.5
            g.append(f'<circle cx="{ex+bak[0]:.1f}" cy="{ey+bak[1]:.1f}" r="{pr}" fill="{OUT}"/>')
            g.append(f'<circle cx="{ex+bak[0]+2.5:.1f}" cy="{ey+bak[1]-2.5:.1f}" r="2.2" fill="#fff"/>')
            if ifade == "yorgun":
                g.append(P(f"M{ex-20},{ey-1} A20,20 0 0 1 {ex+20},{ey-1} Z", fill=ten, sw=4))
    # kaşlar
    kas = {"normal": (-30, -32), "mutlu": (-37, -35), "korku": (-44, -40), "saskin": (-44, -40),
           "uzgun": (-40, -26), "kizgin": (-22, -38), "yorgun": (-28, -26), "sert": (-26, -36)}[ifade]
    kas_renk = "#5a3a20" if sac in ("sari", "gri", "beyaz") or yasli else OUT
    for sx in (-1, 1):
        ic_x, dis_x = sx * 8, sx * 44
        g.append(P(f"M{ic_x},{hy+kas[0]} Q{sx*26},{hy+min(kas)-6} {dis_x},{hy+kas[1]}", sw=8, stroke=kas_renk))
    # burun
    g.append(E(0, hy + 18, 10, 8, TEN_GOLGE if ten == TEN else ten, sw=3))
    # ağız
    my = hy + 50
    agiz = {
        "normal": P(f"M-12,{my} Q0,{my+4} 12,{my}", sw=5),
        "mutlu": P(f"M-20,{my-4} Q0,{my+22} 20,{my-4} Z", fill="#8c2f2f", sw=4),
        "korku": E(0, my + 4, 10, 13, "#5a1f1f", sw=4),
        "saskin": E(0, my + 2, 7, 9, "#5a1f1f", sw=4),
        "uzgun": P(f"M-14,{my+6} Q0,{my-6} 14,{my+6}", sw=5),
        "kizgin": P(f"M-17,{my-3} L17,{my-3} L14,{my+9} L-14,{my+9} Z", fill="#fff", sw=4) + L(-15, my + 3, 15, my + 3, sw=2),
        "yorgun": L(-10, my + 2, 10, my + 2, sw=5),
        "sert": L(-14, my + 1, 14, my + 1, sw=6),
    }[ifade]
    g.append(agiz)
    if yasli:
        g.append(P(f"M-22,{hy-58} Q0,{hy-62} 22,{hy-58}", sw=3) + P(f"M-16,{hy-50} Q0,{hy-53} 16,{hy-50}", sw=3))
    # başlık
    if bas == "kask":
        g.append(P(f"M-75,{hy-14} Q-74,{hy-98} 0,{hy-104} Q74,{hy-98} 75,{hy-14} Z", fill="#9aa3ab", sw=5))
        g.append(R(-76, hy - 26, 152, 16, "#b08d3c", sw=4, rx=4))
        g.append(L(0, hy - 102, 0, hy - 28, sw=3, stroke="#6c757d"))
        g.append(R(-6, hy - 28, 12, 44, "#9aa3ab", sw=4, rx=3))
    elif bas == "basortu":
        g.append(P(f"M-80,{hy+30} Q-90,{hy-92} 0,{hy-92} Q90,{hy-92} 80,{hy+30} Q76,{hy+80} 60,{hy+70} Q66,{hy-30} 0,{hy-50} Q-66,{hy-30} -60,{hy+70} Q-76,{hy+80} -80,{hy+30} Z", fill=bas_renk))
    elif bas == "bant":
        g.append(R(-73, hy - 44, 146, 14, bas_renk, sw=4, rx=6))
    # eşya
    if esya:
        g.append(_esya(esya, el_R, el_L))
    # eller (en üstte)
    g.append(C(el_L[0], el_L[1], 14, ten, sw=5) + C(el_R[0], el_R[1], 14, ten, sw=5))
    icerik = "".join(g)
    if yasli:
        icerik = G(icerik, rot=4)
    return G(icerik, x, y, s, flip, rot)


# ================================================================= HAYVANLAR
def koyun(x, y, s=1.0, flip=False, renk="#f1ead8"):
    g = [L(-30, -10, -30, 30, sw=10) + L(30, -10, 30, 30, sw=10) + L(-12, -5, -12, 32, sw=10) + L(14, -5, 14, 32, sw=10)]
    bulut = "".join(C(cx, cy, r, renk, sw=5) for cx, cy, r in
                    [(-40, -30, 30), (-10, -50, 34), (25, -45, 32), (45, -20, 28), (10, -10, 34), (-30, 0, 26)])
    g.append(bulut + E(0, -28, 56, 34, renk, sw=0))
    g.append(E(68, -42, 22, 28, "#3a2e28", sw=5) + E(52, -60, 12, 6, "#3a2e28", sw=4, extra='transform="rotate(-30 52 -60)"')
             + C(74, -48, 5, "#fff", sw=0))
    return G("".join(g), x, y, s, flip)


def inek(x, y, s=1.0, flip=False, renk="#a0623a"):
    g = [L(-60, 10, -60, 60, sw=16) + L(-30, 10, -30, 62, sw=16) + L(40, 10, 40, 62, sw=16) + L(66, 10, 66, 60, sw=16)]
    g.append(R(-90, -60, 180, 90, renk, sw=5, rx=40))
    g.append(E(-30, -30, 30, 22, "#f3ece0", sw=0) + E(30, 5, 22, 16, "#f3ece0", sw=0))
    g.append(R(-90, -60, 180, 90, "none", sw=5, rx=40))
    g.append(P("M-90,-30 Q-115,-10 -108,20", sw=6))
    g.append(E(110, -50, 34, 40, renk, sw=5) + E(118, -24, 26, 18, "#e9b9a0", sw=4))
    g.append(P("M88,-82 Q80,-104 94,-108", sw=6, stroke="#e8dcc0") + P("M128,-84 Q138,-104 126,-110", sw=6, stroke="#e8dcc0"))
    g.append(C(100, -58, 5, OUT, sw=0) + C(122, -58, 5, OUT, sw=0))
    return G("".join(g), x, y, s, flip)


def keci(x, y, s=1.0, flip=False, renk="#9a8a74"):
    g = [L(-36, 0, -36, 50, sw=9) + L(-16, 0, -16, 52, sw=9) + L(24, 0, 24, 52, sw=9) + L(40, 0, 40, 50, sw=9)]
    g.append(E(0, -18, 58, 32, renk, sw=5))
    g.append(P("M50,-30 L66,-70 L92,-66 L86,-36 Z", fill=renk))
    g.append(P("M70,-70 Q60,-110 40,-100", sw=7, stroke="#5a4a3a") + P("M84,-36 L88,-14 L80,-30", fill="#e8e0d0", sw=3))
    g.append(C(80, -58, 4, OUT, sw=0))
    return G("".join(g), x, y, s, flip)


def domuz(x, y, s=1.0, flip=False, renk="#c98f7a"):
    g = [L(-30, 0, -30, 34, sw=12) + L(30, 0, 30, 34, sw=12)]
    g.append(E(0, -20, 64, 38, renk, sw=5))
    g.append(E(64, -22, 16, 14, "#e2a894", sw=4) + C(60, -22, 3, OUT, sw=0) + C(68, -22, 3, OUT, sw=0))
    g.append(P("M30,-52 L40,-74 L50,-50 Z", fill=renk, sw=4) + C(44, -34, 4, OUT, sw=0))
    g.append(P("M-64,-26 q-14,-6 -10,-18 q8,-4 4,8", sw=4))
    return G("".join(g), x, y, s, flip)


# ================================================================= MANZARA
def gokyuzu(ust, alt, gid="gok"):
    return lin_grad(gid, [(0, ust), (1, alt)]), f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>'


def daglar(taban_y, renk, tepe=(180, 320), n=7, seed=1, kar=False, sw=0):
    rnd = random.Random(seed)
    xs = [-100]
    while xs[-1] < W + 100:
        xs.append(xs[-1] + rnd.randint(180, 340))
    d = f"M-100,{H} L-100,{taban_y}"
    kar_d = ""
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]
        tx = (a + b) / 2 + rnd.randint(-40, 40)
        ty = taban_y - rnd.randint(*tepe)
        d += f" L{tx},{ty} L{b},{taban_y - rnd.randint(0, 60)}"
        if kar:
            kar_d += f"M{tx-38},{ty+52} L{tx},{ty} L{tx+38},{ty+52} L{tx+16},{ty+40} L{tx},{ty+56} L{tx-16},{ty+40} Z "
    d += f" L{W+100},{H} Z"
    s = P(d, fill=renk, sw=sw, stroke=OUT if sw else "none")
    if kar:
        s += P(kar_d, fill="#f4f6f8", sw=0, stroke="none")
    return s


def tepeler(y, renk, genlik=40, seed=2, sw=5):
    rnd = random.Random(seed)
    d = f"M-50,{H+10} L-50,{y}"
    x = -50
    while x < W + 50:
        nx = x + rnd.randint(250, 450)
        d += f" Q{(x+nx)/2},{y - rnd.randint(-genlik, genlik*2)} {nx},{y + rnd.randint(-genlik//2, genlik//2)}"
        x = nx
    d += f" L{W+50},{H+10} Z"
    return P(d, fill=renk, sw=sw)


def deniz(y, ust="#3f86a8", alt="#1d4f6b", gid="deniz", dalga=True, seed=3):
    s = f'<rect x="0" y="{y}" width="{W}" height="{H-y}" fill="url(#{gid})"/>'
    rnd = random.Random(seed)
    if dalga:
        for i in range(26):
            wx = rnd.randint(0, W)
            wy = rnd.randint(y + 20, H - 10)
            ww = rnd.randint(30, 70) * (0.5 + (wy - y) / (H - y))
            s += P(f"M{wx},{wy} q{ww/2},-{ww/4} {ww},0", sw=4, stroke="#cfe8f2", extra='opacity="0.7"')
    return lin_grad(gid, [(0, ust), (1, alt)]), s


def bulut(x, y, s=1.0, renk="#ffffff", op=1.0):
    d = "".join(C(cx, cy, r, renk, sw=0) for cx, cy, r in [(-60, 0, 40), (-15, -25, 52), (40, -10, 45), (80, 8, 32), (0, 15, 40)])
    return G(d + R(-95, 0, 205, 42, renk, sw=0, rx=20), x, y, s, extra=f'opacity="{op}"')


def gunes(x, y, r=70, renk="#ffe08a"):
    return C(x, y, r * 1.8, renk, sw=0, extra='opacity="0.25"') + C(x, y, r, renk, sw=0)


def ay(x, y, r=55):
    return C(x, y, r * 2.2, "#fdf6d8", sw=0, extra='opacity="0.12"') + C(x, y, r, "#fdf6d8", sw=0) + C(x - 18, y - 10, r * 0.22, "#e9dfb5", sw=0) + C(x + 15, y + 18, r * 0.15, "#e9dfb5", sw=0)


def yildizlar(n=120, y_max=600, seed=4):
    rnd = random.Random(seed)
    return "".join(C(rnd.randint(0, W), rnd.randint(0, y_max), rnd.choice([1.5, 2, 2.5, 3]), "#ffffff", sw=0,
                     extra=f'opacity="{rnd.uniform(0.4, 1):.2f}"') for _ in range(n))


def aurora():
    s = ""
    for i, (renk, yy, op) in enumerate([("#53f5a0", 220, 0.55), ("#3fd6c8", 300, 0.4), ("#8a6cf0", 170, 0.3)]):
        d = f"M-100,{yy} Q400,{yy-150} 800,{yy-30} T1700,{yy-80} T2100,{yy}"
        s += P(d, sw=90 - i * 20, stroke=renk, extra=f'opacity="{op}" filter="url(#blur40)"')
    return s


def cam(x, y, s=1.0, renk="#2f5d3a"):
    d = (P("M0,-260 L60,-150 L30,-150 L85,-60 L45,-60 L105,30 L-105,30 L-45,-60 L-85,-60 L-30,-150 L-60,-150 Z", fill=renk, sw=5)
         + R(-14, 30, 28, 40, "#5a3a20", sw=5))
    return G(d, x, y, s)


def kaya(x, y, s=1.0, renk="#8c8c86"):
    return G(P("M-80,0 Q-90,-60 -40,-80 Q10,-110 50,-80 Q95,-50 85,0 Z", fill=renk) + P("M-30,-60 Q0,-75 30,-62", sw=4, stroke="#6e6e68"), x, y, s)


def cit(x1, x2, y, renk="#7b5532"):
    s = L(x1, y - 50, x2, y - 50, sw=10) + L(x1, y - 50, x2, y - 50, sw=5, stroke=renk)
    s += L(x1, y - 25, x2, y - 25, sw=10) + L(x1, y - 25, x2, y - 25, sw=5, stroke=renk)
    x = x1
    while x <= x2:
        s += R(x - 7, y - 75, 14, 80, renk, sw=4, rx=3)
        x += 80
    return s


def tarla(x, y, w, h, renk="#e3b448", koyu="#c79226", seed=5):
    rnd = random.Random(seed)
    s = R(x, y, w, h, renk, sw=0)
    for row in range(int(h / 22)):
        yy = y + 12 + row * 22
        for k in range(int(w / 26)):
            xx = x + 8 + k * 26 + rnd.randint(-5, 5)
            s += L(xx, yy + 14, xx + rnd.randint(-3, 3), yy - 6, sw=3, stroke=koyu)
            s += E(xx, yy - 10, 4, 8, koyu, sw=0)
    return s


def cimen_tutamlari(y0, y1, n=60, seed=6, renk="#4f7f35"):
    rnd = random.Random(seed)
    s = ""
    for _ in range(n):
        x, y = rnd.randint(0, W), rnd.randint(y0, y1)
        s += P(f"M{x-8},{y} L{x-4},{y-16} L{x},{y} L{x+4},{y-20} L{x+8},{y}", sw=3, stroke=renk)
    return s


# ================================================================= YAPILAR
def uzun_ev(x, y, w=900, s=1.0, kar=False):
    """Dışarıdan uzun ev. (x,y) zemin ortası."""
    hw = w / 2
    duvar = P(f"M{-hw},0 Q{-hw-20},-110 {-hw+10},-150 L{hw-10},-150 Q{hw+20},-110 {hw},0 Z", fill="#6b4226")
    tahta = "".join(L(xx, -6, xx, -146, sw=3, stroke="#4a2c17") for xx in range(int(-hw + 40), int(hw - 20), 42))
    cati_renk = "#f2f4f6" if kar else "#5d8a3c"
    cati = P(f"M{-hw-60},-120 Q{-hw-30},-330 0,-350 Q{hw+30},-330 {hw+60},-120 Q0,-150 {-hw-60},-120 Z", fill=cati_renk)
    tutam = ""
    if not kar:
        rnd = random.Random(7)
        for _ in range(40):
            tx = rnd.uniform(-hw, hw)
            ty = -150 - (1 - (tx / hw) ** 2) * 180 + rnd.uniform(-20, 40)
            tutam += P(f"M{tx-6},{ty} L{tx},{ty-14} L{tx+6},{ty}", sw=3, stroke="#3f6a2a")
    else:
        tutam = P(f"M{-hw-60},-120 Q0,-160 {hw+60},-120", sw=6, stroke="#c9d6e0")
    kapi = P("M-50,0 L-50,-110 Q0,-150 50,-110 L50,0 Z", fill="#3e2412") + L(0, -132, 0, 0, sw=3, stroke="#2b1b12")
    baca = R(-30, -365, 60, 24, "#4a2c17", sw=5, rx=4)
    return G(duvar + tahta + cati + tutam + kapi + baca, x, y, s)


def gemi(x, y, s=1.0, flip=False, yelken=True, kalkan=True, kurek=True, yelken_renk=("#b8372b", "#f0e6d0"), insan_sayisi=0):
    g = []
    if yelken:
        g.append(L(0, -40, 0, -470, sw=14) + L(0, -40, 0, -470, sw=7, stroke="#7b5532"))
        g.append(L(-210, -440, 210, -440, sw=12) + L(-210, -440, 210, -440, sw=6, stroke="#7b5532"))
        serit = ""
        for i in range(6):
            x0 = -200 + i * 66.6
            serit += f'<rect x="{x0:.1f}" y="-440" width="66.6" height="330" fill="{yelken_renk[i % 2]}"/>'
        g.append(f'<g clip-path="url(#yelkenClip)">{serit}</g>')
        g.append(P("M-200,-440 L200,-440 Q215,-270 200,-110 L-200,-110 Q-185,-270 -200,-440 Z", sw=6))
        g.append(L(-200, -110, -330, -20, sw=3) + L(200, -110, 330, -20, sw=3))
    if kurek:
        for i in range(8):
            ox = -230 + i * 62
            g.append(L(ox, -40, ox - 50, 60, sw=8) + L(ox, -40, ox - 50, 60, sw=4, stroke="#a0703f"))
    for i in range(insan_sayisi):
        ox = -200 + i * 80
        g.append(C(ox, -95, 26, TEN, sw=4) + P(f"M{ox-28},-100 Q{ox},-140 {ox+28},-100 Z", fill="#9aa3ab", sw=4))
    govde = P("M-380,-60 Q-430,-120 -420,-200 Q-440,-250 -400,-260 Q-380,-230 -395,-195 Q-390,-130 -330,-70 "
              "L330,-70 Q390,-130 395,-195 Q380,-230 400,-260 Q440,-250 420,-200 Q430,-120 380,-60 Q300,20 0,20 Q-300,20 -380,-60 Z",
              fill="#7b4a25", sw=6)
    g.append(govde)
    g.append(P("M-350,-50 Q0,-10 350,-50", sw=4, stroke="#4a2c17") + P("M-310,-20 Q0,15 310,-20", sw=4, stroke="#4a2c17"))
    # ejder başı
    g.append(P("M-400,-260 Q-430,-300 -400,-320 Q-370,-330 -360,-300 Q-380,-300 -385,-280 Z", fill="#7b4a25", sw=5)
             + C(-392, -305, 5, "#f2c14e", sw=0))
    if kalkan:
        renkler = ["#c0392b", "#f2c14e", "#2e6f95", "#f0e6d0"]
        for i in range(10):
            cx = -300 + i * 66
            g.append(C(cx, -78, 27, renkler[i % 4], sw=5) + C(cx, -78, 8, "#9aa3ab", sw=3))
    defs = '<clipPath id="yelkenClip"><path d="M-200,-440 L200,-440 Q215,-270 200,-110 L-200,-110 Q-185,-270 -200,-440 Z"/></clipPath>'
    return G(f"<defs>{defs}</defs>" + "".join(g), x, y, s, flip)


def gemi_silueti(x, y, s=1.0, renk="#14202c"):
    d = (P("M-200,0 Q-230,-50 -215,-110 Q-200,-60 -160,-30 L160,-30 Q200,-60 215,-110 Q230,-50 200,0 Q0,25 -200,0 Z", fill=renk, sw=0, stroke="none")
         + R(-6, -260, 12, 240, renk, sw=0, stroke="none") + P("M-110,-250 L110,-250 L115,-60 L-115,-60 Z", fill=renk, sw=0, stroke="none"))
    return G(d, x, y, s)


def ocak(x, y, s=1.0):
    taslar = "".join(E(-110 + i * 44, 0, 26, 16, "#8c8c86", sw=4) for i in range(6))
    kor = E(0, -8, 110, 18, "#5a2c17", sw=0)
    return G(kor + taslar, x, y, s)


def ates(x, y, s=1.0, faz=0):
    """Alev; faz 0-2 arası farklı kareler (titreme için)."""
    k = [(0, 0, 0), (8, -14, 6), (-8, 10, -6)][faz % 3]
    d = (P(f"M-70,0 Q-80,-70 {-30+k[0]},{-120+k[1]} Q-20,-70 0,{-160+k[1]} Q20,-90 {35+k[2]},{-130-k[1]} Q80,-60 70,0 Z", fill="#f08a24", sw=5)
         + P(f"M-40,0 Q-45,-50 {-12+k[2]},{-80+k[1]} Q0,-50 {10},{-100-k[1]} Q40,-40 40,0 Z", fill="#ffd44d", sw=0, stroke="none"))
    glow = C(0, -60, 220, "#ffb347", sw=0, extra='opacity="0.18" filter="url(#blur40)"')
    return G(glow + d, x, y, s)


def ic_mekan(gid="icgrad"):
    """Uzun evin içi: koyu ahşap duvarlar, çatı makasları, sekiler."""
    defs = lin_grad(gid, [(0, "#2a170c"), (0.6, "#4a2c17"), (1, "#5a3a20")]) + rad_grad(
        "isik", [(0, "#ffb347", 0.55), (0.5, "#ff8c2a", 0.15), (1, "#000", 0)], cy=0.65, r=0.6)
    s = f'<rect width="{W}" height="{H}" fill="url(#{gid})"/>'
    for xx in range(0, W, 70):
        s += L(xx, 0, xx, 760, sw=3, stroke="#22130a")
    for cx in (240, 960, 1680):
        s += P(f"M{cx-420},360 L{cx},40 L{cx+420},360", sw=26, stroke="#22130a") + P(f"M{cx-420},360 L{cx},40 L{cx+420},360", sw=16, stroke="#5a3a20")
    s += L(0, 360, W, 360, sw=24, stroke="#22130a") + L(0, 360, W, 360, sw=14, stroke="#5a3a20")
    for px in (300, 860, 1060, 1620):
        s += R(px - 22, 340, 44, 460, "#5a3a20", sw=6)
    s += R(-10, 760, W + 20, 330, "#3b2414", sw=0)
    s += P(f"M-10,700 L520,700 L560,800 L-10,800 Z", fill="#6b4226", sw=5) + P(f"M{W+10},700 L{W-520},700 L{W-560},800 L{W+10},800 Z", fill="#6b4226", sw=5)
    s += E(200, 690, 120, 22, "#b9a67a", sw=4) + E(W - 220, 690, 120, 22, "#8c7a5a", sw=4)
    s += C(140, 300, 46, "#c0392b", sw=5) + C(140, 300, 12, "#9aa3ab", sw=3)
    s += C(1780, 300, 46, "#2e6f95", sw=5) + C(1780, 300, 12, "#9aa3ab", sw=3)
    s += f'<rect width="{W}" height="{H}" fill="url(#isik)"/>'
    return defs, s


# ================================================================= GRAFİK ÖĞELER
def etiket(x, y, metin, size=40, bg="#ffffff", fg="#2b1b12", rot=0):
    w = len(metin) * size * 0.68 + 40
    h = size * 1.45
    icerik = (R(-w / 2, -h / 2, w, h, bg, sw=5, rx=14)
              + T(0, size * 0.36, metin, size=size, fill=fg))
    return G(icerik, x, y, rot=rot, extra='filter="url(#golge)"')


def serit_baslik(x, y, metin, size=46, bg="#b3262b", fg="#ffffff", rot=-2):
    w = len(metin) * size * 0.66 + 70
    h = size * 1.5
    icerik = (P(f"M{-w/2-30},{-h/2} L{w/2+30},{-h/2} L{w/2+10},0 L{w/2+30},{h/2} L{-w/2-30},{h/2} L{-w/2-10},0 Z", fill=bg, sw=5)
              + T(0, size * 0.36, metin, size=size, fill=fg))
    return G(icerik, x, y, rot=rot, extra='filter="url(#golge)"')


def buyuk_yazi(x, y, metin, size=140, fill="#f4e3b5", sw=14, font="Cinzel", weight=900, anchor="middle"):
    return T(x, y, metin, size=size, fill=fill, font=font, weight=weight, anchor=anchor, stroke=OUT, sw=sw,
             extra='filter="url(#golge)"')


def bilgi_karti(x, y, w, baslik, satirlar, size=40, renk="#f3e6c4", ikon=None):
    h = 90 + len(satirlar) * size * 1.35
    s = R(x, y, w, h, renk, sw=6, rx=20, extra='filter="url(#golge)"')
    s += T(x + w / 2, y + 62, baslik, size=size * 1.15, fill="#8c2f1f", font="Cinzel", weight=900)
    for i, st in enumerate(satirlar):
        ty = y + 62 + (i + 1) * size * 1.35
        if ikon:
            iy = ty - size * 0.36
            ix = x + 70
            if ikon == "tik":
                s += P(f"M{ix-22},{iy} L{ix-6},{iy+17} L{ix+24},{iy-19}", sw=12, stroke="#2f8f46")
            else:
                s += L(ix - 17, iy - 17, ix + 17, iy + 17, sw=12, stroke="#c0392b") + L(ix + 17, iy - 17, ix - 17, iy + 17, sw=12, stroke="#c0392b")
            s += T(x + 120, ty, st, size=size, fill=OUT, weight=800, anchor="start")
        else:
            s += T(x + w / 2, ty, st, size=size, fill=OUT, weight=800)
    return s


def parsomen(x, y, w, h):
    s = R(x, y, w, h, "#ead8a8", sw=6, rx=10)
    s += E(x, y + h / 2, 28, h / 2 + 14, "#d9c28c", sw=6) + E(x + w, y + h / 2, 28, h / 2 + 14, "#d9c28c", sw=6)
    rnd = random.Random(9)
    for _ in range(14):
        cx, cy = rnd.uniform(x + 40, x + w - 40), rnd.uniform(y + 30, y + h - 30)
        s += C(cx, cy, rnd.uniform(8, 30), "#d9c28c", sw=0, extra='opacity="0.45"')
    return s


def vinyet(guc=0.55):
    d = rad_grad("vinyet", [(0.55, "#000", 0), (1, "#000", guc)], r=0.75)
    return d, f'<rect width="{W}" height="{H}" fill="url(#vinyet)"/>'
