"""Ek çizimler: Paris, piramit, dokuma tezgahı, tanrılar, harita, eşyalar, ikonlar."""
import math
import random

from sanat import (OUT, TEN, W, H, KUMAS, SAC, P, C, E, R, L, G, T, insan, bulut, etiket)


def piramit(cx=960, taban=960, gen=1100, yuk=780):
    katlar = [("#d9a63a", "JARL"), ("#7da34f", "KARL"), ("#8c8c86", "KÖLE")]
    s = ""
    for i, (renk, _) in enumerate(katlar):
        y0 = taban - yuk + i * yuk / 3
        y1 = y0 + yuk / 3
        w0 = gen * (i / 3)
        w1 = gen * ((i + 1) / 3)
        s += P(f"M{cx-w0/2},{y0} L{cx+w0/2},{y0} L{cx+w1/2},{y1} L{cx-w1/2},{y1} Z", fill=renk, sw=7)
    return s


def dokuma_tezgahi(x, y, s=1.0):
    g = [L(-200, 0, -170, -560, sw=22) + L(-200, 0, -170, -560, sw=13, stroke="#7b5532"),
         L(200, 0, 170, -560, sw=22) + L(200, 0, 170, -560, sw=13, stroke="#7b5532"),
         L(-210, -540, 210, -540, sw=26) + L(-210, -540, 210, -540, sw=16, stroke="#8a5a35")]
    kumas = P("M-165,-525 L165,-525 L160,-330 L-160,-330 Z", fill="#a8452f", sw=5)
    for i in range(5):
        yy = -505 + i * 36
        kumas += L(-160, yy, 160, yy, sw=8, stroke=["#f0e6d0", "#2e6f95"][i % 2])
    g.append(kumas)
    for i in range(22):
        xx = -150 + i * 14.3
        g.append(L(xx, -330, xx + (i % 2) * 4 - 2, -120, sw=2, stroke="#e8dcc0"))
    g.append(L(-175, -260, 175, -260, sw=10) + L(-175, -260, 175, -260, sw=5, stroke="#a0703f"))
    for i in range(11):
        g.append(E(-145 + i * 29, -100, 13, 17, "#8c8c86", sw=4))
    return G("".join(g), x, y, s)


def simsek(x, y, s=1.0, renk="#fff6a8"):
    return G(P("M0,0 L-40,140 L5,135 L-30,290 L70,100 L22,108 L55,0 Z", fill=renk, sw=5,
               extra='filter="url(#golge)"'), x, y, s)


def kuzgun(x, y, s=1.0, flip=False):
    d = (P("M-50,0 Q-20,-30 20,-10 Q50,-40 80,-30 Q60,-10 40,5 Q10,25 -30,15 Z", fill="#1f1f24", sw=4)
         + P("M-50,0 L-80,8 L-48,10 Z", fill="#1f1f24", sw=3) + C(52, -26, 3, "#fff", sw=0)
         + P("M70,-28 L92,-22 L72,-18 Z", fill="#3a3a40", sw=3))
    return G(d, x, y, s, flip)


def kalp(x, y, s=1.0, renk="#e0455a"):
    return G(P("M0,30 C-60,-10 -40,-60 0,-30 C40,-60 60,-10 0,30 Z", fill=renk, sw=5), x, y, s)


def tik(x, y, s=1.0):
    return G(P("M-30,0 L-8,24 L34,-26", sw=16, stroke="#2f8f46"), x, y, s)


def carpi(x, y, s=1.0):
    return G(L(-26, -26, 26, 26, sw=16, stroke="#c0392b") + L(26, -26, -26, 26, sw=16, stroke="#c0392b"), x, y, s)


def sandik(x, y, s=1.0, dolu=True):
    g = R(-110, -90, 220, 110, "#7b4a25", sw=6, rx=8) + R(-110, -90, 220, 22, "#b08d3c", sw=5) + R(-14, -60, 28, 30, "#b08d3c", sw=4)
    if dolu:
        rnd = random.Random(11)
        sik = ""
        for _ in range(26):
            cx, cy = rnd.uniform(-95, 95), rnd.uniform(-130, -92)
            sik += E(cx, cy, 16, 9, rnd.choice(["#e6e8ea", "#cfd3d6", "#f2c14e"]), sw=3)
        g = sik + g
    return G(g, x, y, s)


def bilezik(x, y, s=1.0):
    return G(E(0, 0, 60, 36, "none", sw=20, stroke=OUT) + E(0, 0, 60, 36, "none", sw=11, stroke="#dfe3e6")
             + "".join(C(-40 + i * 20, -30 if i % 2 else 30, 4, "#9aa3ab", sw=0) for i in range(5)), x, y, s)


def sikke(x, y, s=1.0):
    return G(C(0, 0, 30, "#dfe3e6", sw=5) + C(0, 0, 18, "none", sw=3, stroke="#9aa3ab") + L(-8, 0, 8, 0, sw=3, stroke="#9aa3ab"), x, y, s)


def kum_saati(x, y, s=1.0):
    g = (R(-90, -170, 180, 26, "#7b4a25", sw=6, rx=6) + R(-90, 144, 180, 26, "#7b4a25", sw=6, rx=6)
         + P("M-70,-144 L70,-144 Q70,-60 12,0 Q70,60 70,144 L-70,144 Q-70,60 -12,0 Q-70,-60 -70,-144 Z", fill="#cfe8f2", sw=6)
         + P("M-50,-110 L50,-110 Q40,-50 8,-8 L-8,-8 Q-40,-50 -50,-110 Z", fill="#e3b448", sw=0, stroke="none")
         + P("M-60,140 Q0,70 60,140 Z", fill="#e3b448", sw=0, stroke="none") + L(0, -8, 0, 110, sw=4, stroke="#e3b448")
         + L(-80, -144, -80, 144, sw=12) + L(80, -144, 80, 144, sw=12))
    return G(g, x, y, s)


def cadir(x, y, s=1.0, renk="#c9b07a"):
    g = (P("M-170,0 L0,-230 L170,0 Z", fill=renk, sw=6) + P("M-60,0 L0,-230 L60,0 Z", fill="#3e2a1a", sw=5)
         + L(0, -230, -30, -270, sw=8) + L(0, -230, 30, -270, sw=8)
         + "".join(L(-170 + i * 42, 0, 0, -230, sw=2, stroke="#a08d5c") for i in range(1, 8)))
    return G(g, x, y, s)


def yatan_insan(x, y, s=1.0, battaniye="#7d7a72", sac="#7b4a25", flip=False):
    g = (E(30, -30, 150, 40, battaniye, sw=5) + C(-140, -40, 46, TEN, sw=5)
         + P("M-186,-40 Q-180,-96 -130,-88 Q-110,-82 -100,-60", fill=sac, sw=5)
         + P("M-158,-48 Q-150,-42 -142,-48", sw=4) + P("M-132,-48 Q-124,-42 -116,-48", sw=4)
         + P("M-145,-18 Q-136,-26 -127,-18", sw=4))
    return G(g, x, y, s, flip)


def hnefatafl(x, y, s=1.0):
    g = R(-220, -220, 440, 440, "#c9a26a", sw=8, rx=10)
    for i in range(1, 11):
        v = -220 + i * 40
        g += L(v, -220, v, 220, sw=2, stroke="#8a6a3a") + L(-220, v, 220, v, sw=2, stroke="#8a6a3a")
    for (cx, cy) in [(0, 0)]:
        g += C(cx * 40 - 0, cy, 22, "#f2c14e", sw=4) + C(0, 0, 8, "#b08d3c", sw=0)
    for (i, j) in [(-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        g += C(i * 40 - 20 + 20, j * 40, 15, "#f0e6d0", sw=4)
    for (i, j) in [(-5, -1), (-5, 0), (-5, 1), (-4, 0), (5, -1), (5, 0), (5, 1), (4, 0), (-1, -5), (0, -5), (1, -5), (0, -4), (-1, 5), (0, 5), (1, 5), (0, 4)]:
        g += C(i * 40, j * 40, 15, "#3a2a20", sw=4)
    return G(g, x, y, s)


def tas_gemi(x, y, s=1.0):
    g = ""
    n = 26
    tas = []
    for i in range(n):
        a = 2 * math.pi * i / n
        px, py = 520 * math.cos(a), 150 * math.sin(a)
        boy = 70 + 130 * abs(math.cos(a)) ** 4
        tas.append((py, P(f"M{px-24},{py} L{px-18},{py-boy} Q{px},{py-boy-20} {px+18},{py-boy} L{px+24},{py} Z", fill="#a3a39b", sw=6)))
    g += "".join(t for _, t in sorted(tas))
    return G(g, x, y, s)


def tumulus(x, y, s=1.0, renk="#5d8a3c"):
    return G(P("M-320,0 Q-260,-170 0,-190 Q260,-170 320,0 Z", fill=renk, sw=6), x, y, s)


def kurutma_rafi(x, y, s=1.0):
    g = (L(-200, 0, -170, -260, sw=16) + L(-200, 0, -170, -260, sw=8, stroke="#7b5532")
         + L(200, 0, 170, -260, sw=16) + L(200, 0, 170, -260, sw=8, stroke="#7b5532")
         + L(-190, -240, 190, -240, sw=14) + L(-190, -240, 190, -240, sw=7, stroke="#8a5a35"))
    for i in range(7):
        bx = -150 + i * 50
        g += P(f"M{bx},-236 L{bx-12},-150 L{bx},-120 L{bx+12},-150 Z", fill="#b8a07a", sw=4)
        g += P(f"M{bx-12},-120 L{bx},-100 L{bx+12},-120", fill="#b8a07a", sw=4)
    return G(g, x, y, s)


def fici(x, y, s=1.0, renk="#8a5a35"):
    return G(P("M-55,0 Q-70,-70 -55,-140 L55,-140 Q70,-70 55,0 Z", fill=renk, sw=6)
             + L(-62, -35, 62, -35, sw=7, stroke="#4a4a4a") + L(-62, -105, 62, -105, sw=7, stroke="#4a4a4a")
             + E(0, -140, 55, 12, "#a87a4a", sw=5), x, y, s)


def saman(x, y, s=1.0):
    return G(P("M-110,0 Q-120,-120 0,-170 Q120,-120 110,0 Z", fill="#d9b24a", sw=6)
             + "".join(P(f"M{-80+i*32},-10 Q{-70+i*30},-80 {-40+i*20},-130", sw=3, stroke="#b08d2a") for i in range(6)), x, y, s)


def kuru_agac(x, y, s=1.0):
    return G(P("M-18,0 L-12,-200 L-60,-290 M-12,-200 L20,-330 M8,-260 L70,-310 M-30,-240 L-80,-250", sw=22, stroke=OUT)
             + P("M-18,0 L-12,-200 L-60,-290 M-12,-200 L20,-330 M8,-260 L70,-310 M-30,-240 L-80,-250", sw=13, stroke="#5a4030"), x, y, s)


def paris(x, y, s=1.0):
    g = [E(0, 30, 620, 90, "#7f9a5a", sw=6)]
    g.append(P("M-520,10 L-520,-120 L520,-120 L520,10 Z", fill="#c8b48c", sw=6))
    for i in range(-520, 521, 40):
        g.append(R(i - 12, -144, 24, 26, "#c8b48c", sw=4))
    for tx in (-520, -180, 180, 520):
        g.append(R(tx - 50, -230, 100, 240, "#b8a47c", sw=6) + P(f"M{tx-60},-230 L{tx},-310 L{tx+60},-230 Z", fill="#8c3b2b", sw=6))
    g.append(R(-80, -300, 160, 180, "#d8c8a0", sw=6) + P("M-95,-300 L0,-380 L95,-300 Z", fill="#6b4a7a", sw=6)
             + R(-6, -440, 12, 70, OUT, sw=0) + R(-24, -420, 48, 10, OUT, sw=0) + P("M-26,-120 L-26,-190 Q0,-220 26,-190 L26,-120 Z", fill="#3e2a1a", sw=5))
    return G("".join(g), x, y, s)


def harita():
    s = '<rect width="1920" height="1080" fill="#6fa8c8"/>'
    for i in range(0, 1920, 60):
        s += L(i, 0, i, 1080, sw=1, stroke="#8cbcd6")
    for j in range(0, 1080, 60):
        s += L(0, j, 1920, j, sw=1, stroke="#8cbcd6")
    kara = "#e8d6a8"
    s += P("M1050,0 L1920,0 L1920,420 L1700,520 L1560,430 L1500,300 L1380,250 L1300,330 L1180,300 L1120,180 Z", fill=kara, sw=6)
    s += P("M1240,380 L1320,360 L1330,520 L1280,560 L1220,520 Z", fill=kara, sw=6)
    s += P("M620,160 L740,120 L800,260 L760,400 L820,520 L700,600 L560,580 L600,440 L540,320 Z", fill=kara, sw=6)
    s += P("M640,1080 L600,820 L700,700 L900,690 L1100,640 L1300,640 L1500,700 L1920,640 L1920,1080 Z", fill=kara, sw=6)
    s += P("M940,690 Q980,760 960,820 Q930,880 990,940", sw=10, stroke="#4f8fb8")
    s += C(990, 940, 18, "#c0392b", sw=5)
    s += P("M1300,420 Q1200,560 1040,620 Q960,650 945,700 Q960,780 980,920", sw=8, stroke="#b3262b",
           extra='stroke-dasharray="26 18"')
    s += C(1300, 420, 16, "#2b1b12", sw=0)
    return s


def yemek_masasi(x, y, s=1.0):
    g = [R(-520, -40, 1040, 60, "#8a5a35", sw=7, rx=8), L(-460, 20, -460, 200, sw=26), L(460, 20, 460, 200, sw=26)]
    g.append(P("M-420,-40 Q-360,30 -300,-40 Z", fill="#8a5a35", sw=5) + E(-360, -40, 60, 12, "#e8d9a8", sw=4))
    g.append(E(-150, -52, 90, 26, "#d9a865", sw=5) + "".join(C(-150 + dx, -54 + dy, 4, "#a87a3a", sw=0) for dx, dy in [(-40, -4), (0, -8), (30, 4), (-10, 6), (50, -6)]))
    g.append(P("M40,-40 Q90,20 140,-40 Z", fill="#c9b07a", sw=5) + E(90, -40, 50, 10, "#ffffff", sw=4))
    g.append(P("M230,-60 Q300,-110 380,-62 L420,-90 L414,-40 L380,-52 Q300,-10 230,-60 Z", fill="#b8a07a", sw=5) + C(260, -64, 4, OUT, sw=0))
    g.append(R(440, -140, 70, 100, "#7b4a25", sw=5, rx=6) + R(440, -126, 70, 10, "#4a4a4a", sw=0) + R(440, -70, 70, 10, "#4a4a4a", sw=0)
             + E(475, -140, 35, 8, "#f2d48c", sw=4))
    return G("".join(g), x, y, s)


def salon(x, y, s=1.0):
    g = (P("M-360,0 L-360,-220 L360,-220 L360,0 Z", fill="#c8962e", sw=7)
         + P("M-420,-200 L0,-420 L420,-200 Z", fill="#e3b448", sw=7)
         + "".join(C(-300 + i * 75, -250 + abs(i - 4) * 18, 30, "#f2c14e", sw=5) for i in range(9))
         + P("M-60,0 L-60,-140 Q0,-190 60,-140 L60,0 Z", fill="#ffefb0", sw=6)
         + P("M-370,-210 L-410,-260 M370,-210 L410,-260", sw=10))
    return G(g, x, y, s)


def hel_kapisi(x, y, s=1.0):
    g = (P("M-300,0 L-300,-300 Q0,-460 300,-300 L300,0 Z", fill="#2a2f3a", sw=7)
         + P("M-150,0 L-150,-220 Q0,-320 150,-220 L150,0 Z", fill="#0e1116", sw=6)
         + "".join(R(-300 + i * 75, -330 + abs(i - 4) * 10, 20, 30, "#3a4050", sw=4) for i in range(9)))
    return G(g, x, y, s)


def kitap(x, y, s=1.0):
    return G(P("M-160,0 Q-80,-30 0,0 Q80,-30 160,0 L160,-200 Q80,-230 0,-200 Q-80,-230 -160,-200 Z", fill="#f3e6c4", sw=6)
             + L(0, 0, 0, -200, sw=5) + "".join(L(-130, -170 + i * 30, -30, -170 + i * 30, sw=3, stroke="#9a8a6a") + L(30, -170 + i * 30, 130, -170 + i * 30, sw=3, stroke="#9a8a6a") for i in range(5)), x, y, s)


def lir(x, y, s=1.0):
    return G(P("M-90,0 Q-130,-150 -70,-260 L70,-260 Q130,-150 90,0 Z", fill="#a0703f", sw=6)
             + P("M-50,-30 Q-70,-150 -40,-210 L40,-210 Q70,-150 50,-30 Z", fill="#2b1b12", sw=4)
             + "".join(L(-30 + i * 15, -40, -30 + i * 15, -205, sw=2, stroke="#f2e6c8") for i in range(5)), x, y, s)


def mezar_esyasi_kart():
    s = ""
    s += G(P("M-120,0 L60,0 L110,-20 L60,-40 L-120,-40 Z", fill="#cfd3d6", sw=5) + R(-200, -32, 90, 24, "#7b4a25", sw=5, rx=6), 520, 560)
    s += G(R(-90, -20, 180, 40, "#e9dcc0", sw=5, rx=8) + "".join(L(-75 + i * 15, 20, -75 + i * 15, 55, sw=4) for i in range(11)), 960, 560)
    s += bilezik(1400, 540, 1.2)
    return s


def tirpan(x, y, s=1.0):
    return G(L(0, 0, 60, -380, sw=16) + L(0, 0, 60, -380, sw=8, stroke="#8a5a35")
             + P("M58,-370 Q150,-380 230,-300 Q150,-350 62,-340 Z", fill="#c9ced3", sw=5), x, y, s)


def odin(x, y, s=1.0):
    g = insan(0, 0, 1.0, sac="gri", sakal="uzun", govde="mavi", pelerin="koyu", ifade="sert", kol="tut", esya="mizrak", yasli=False)
    goz_bandi = P("M-48,-330 L-6,-322 L-8,-296 Q-26,-288 -44,-298 Z", fill=OUT, sw=3) + L(-70, -340, 70, -322, sw=5)
    sapka = E(0, -372, 120, 22, "#4a3b30", sw=6) + P("M-70,-372 Q-66,-450 0,-460 Q66,-450 70,-372 Z", fill="#4a3b30", sw=6)
    return G(g + goz_bandi + sapka, x, y, s)


def kel_charles(x, y, s=1.0):
    g = insan(0, 0, 1.0, sac=None, sakal="kisa", biyik=True, govde="mor", pelerin="kirmizi", ifade="korku", kol="onde")
    tac = (P("M-58,-372 L-58,-410 L-30,-388 L0,-420 L30,-388 L58,-410 L58,-372 Z", fill="#f2c14e", sw=5)
           + C(0, -398, 6, "#c0392b", sw=0))
    return G(g + tac, x, y, s)
