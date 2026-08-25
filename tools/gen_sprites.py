import math
import os
import random
from PIL import Image, ImageDraw

ROOT = "/root/RealIndustry/sprites"
S = 32

MET_L = (176, 184, 192, 255)
MET_M = (152, 152, 160, 255)
MET_D = (104, 112, 128, 255)
FRAME = (72, 72, 80, 255)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def shade(c, f):
    if f >= 1:
        t = min(1.0, (f - 1))
        return tuple(min(255, int(v + (255 - v) * t * 0.9)) for v in c[:3]) + (255,)
    return tuple(int(v * f) for v in c[:3]) + (255,)


def tri(c):
    return [shade(c, 1.28), c, shade(c, 0.68)]


def img_new(w=S, h=S):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def poly(d, pts, fill, line=None, lw=1):
    d.polygon(pts, fill=fill, outline=line, width=lw)


def rect(d, box, fill, line=None, lw=1, r=0):
    if r:
        d.rounded_rectangle(box, radius=r, fill=fill, outline=line, width=lw)
    else:
        d.rectangle(box, fill=fill, outline=line, width=lw)


def ell(d, box, fill, line=None, lw=1):
    d.ellipse(box, fill=fill, outline=line, width=lw)


def bevel_rect(d, x0, y0, x1, y1, L, M, D, edge=2):
    rect(d, [x0, y0, x1, y1], M)
    d.line([x0, y0, x1, y0], fill=L, width=edge)
    d.line([x0, y0, x0, y1], fill=L, width=edge)
    d.line([x0, y1 - edge + 1, x1, y1 - edge + 1], fill=D, width=edge)
    d.line([x1 - edge + 1, y0, x1 - edge + 1, y1], fill=D, width=edge)


ITEMS = {
    "bauxite": ("lump", "d4a373"),
    "hematite": ("lump", "9c5630"),
    "chalcopyrite": ("lump", "daa520"),
    "cassiterite": ("lump", "b8b8bc"),
    "galena": ("lump", "708090"),
    "uraninite": ("crystal", "50c878"),
    "quartz": ("crystal", "e8e4d8"),
    "beryl": ("crystal", "7cc87c"),
    "limestone": ("lump", "d8cba8"),
    "aluminum": ("ingot", "ccd4dc"),
    "steel": ("ingot", "8f9aa6"),
    "bronze": ("ingot", "cd7f32"),
    "enriched-uranium": ("ingot", "45e07a"),
    "gravel": ("pebbles", "9d968a"),
    "cement": ("sack", "b8b4ac"),
    "fertilizer": ("sack", "7cb342"),
}


def item_lump(seed, hexs):
    L, M, D = tri(hx(hexs))
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    cx = cy = 16
    r0 = 11
    pts = []
    for i in range(7):
        a = 2 * math.pi * i / 7 + rng.uniform(-0.15, 0.15)
        r = r0 * rng.uniform(0.82, 1.02)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(d, pts, M, line=D, lw=1)
    top = [(x, y) for x, y in pts if y < cy - 2]
    if len(top) >= 3:
        poly(d, top, L)
    bot = [(x, y) for x, y in pts if y > cy + 4]
    if len(bot) >= 3:
        poly(d, bot, D)
    d.line(pts + [pts[0]], fill=D, width=1)
    d.line([pts[1][0], pts[1][1] + 1, pts[2][0], pts[2][1] + 1],
           fill=shade(L, 1.15), width=1)
    return img


def item_crystal(seed, hexs):
    L, M, D = tri(hx(hexs))
    img = img_new()
    d = ImageDraw.Draw(img)
    shards = [
        [(7, 27), (6, 13), (10, 5), (14, 14), (13, 27)],
        [(13, 26), (14, 6), (19, 3), (22, 13), (21, 26)],
        [(20, 27), (23, 12), (26, 10), (26, 21), (24, 27)],
    ]
    for i, sp in enumerate(shards):
        c = [M, L, shade(M, 0.85)][i]
        poly(d, sp, c, line=D, lw=1)
        mid = sp[2]
        d.line([sp[1], mid], fill=L if i != 1 else shade(L, 1.25), width=1)
    return img


def item_ingot(hexs):
    L, M, D = tri(hx(hexs))
    img = img_new()
    d = ImageDraw.Draw(img)
    body = [(5, 21), (16, 12), (28, 17), (17, 26)]
    poly(d, body, M, line=D, lw=1)
    for i, (fx, fy) in enumerate([(9, 18), (14, 15), (19, 16)]):
        d.line([(fx, fy + 3), (fx + 4, fy)], fill=L if i % 2 == 0 else shade(M, 1.12),
               width=2)
    poly(d, [(5, 21), (17, 26), (17, 29), (5, 24)], D, line=D, lw=1)
    d.line([(5, 21), (16, 12)], fill=L, width=1)
    d.line([(17, 26), (28, 17)], fill=shade(D, 0.92), width=1)
    return img


def item_pebbles(seed, hexs):
    L, M, D = tri(hx(hexs))
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    for i, (x, y, r) in enumerate(sorted([(9, 21, 6), (19, 23, 7), (13, 14, 5),
                                          (23, 15, 5)], key=lambda p: p[1])):
        c = [M, L, shade(M, 0.88), shade(M, 1.08)][i % 4]
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2 + 1], fill=c, outline=D, width=1)
        d.arc([x - r + 1, y - r // 2 + 1, x + r - 1, y + r // 2], 200, 320,
              fill=shade(c, 1.2), width=1)
    return img


def item_sack(hexs):
    L, M, D = tri(hx(hexs))
    img = img_new()
    d = ImageDraw.Draw(img)
    poly(d, [(9, 12), (23, 12), (26, 27), (6, 27)], M, line=D, lw=1)
    poly(d, [(11, 8), (21, 8), (23, 12), (9, 12)], L, line=D, lw=1)
    d.line([(8, 18), (24, 18)], fill=D, width=1)
    d.line([(7, 22), (25, 22)], fill=D, width=1)
    d.line([(10, 13), (12, 26)], fill=L, width=2)
    return img


LIQUIDS = {"sulfuric-acid": "d9c25f", "spent-acid": "b5722f",
           "waste-sludge": "6a6c40"}


def liquid_icon(hexs):
    L, M, D = tri(hx(hexs))
    img = img_new()
    d = ImageDraw.Draw(img)
    d.polygon([(9, 17), (16, 5), (23, 17)], fill=M)
    d.pieslice([9, 11, 23, 25], 180, 360, fill=M)
    d.polygon([(9, 17), (16, 5), (16, 17)], fill=L)
    d.line([(9, 17), (16, 5), (23, 17)], fill=D, width=1)
    d.arc([9, 11, 23, 25], 180, 360, fill=D, width=1)
    d.ellipse([12, 15, 15, 19], fill=L)
    return img


BLOCK_ACCENTS = {
    "rotary-drill": "cd7f32", "copper-smelter": "daa520", "blast-furnace": "ff8f3d",
    "alloy-furnace": "cd7f32", "electrolysis-plant": "5cd8e8",
    "chemical-processor": "8fce4e", "centrifuge": "50c878",
    "nuclear-reactor": "54e08a", "coal-generator": "ffb35c",
    "battery-cell": "ffd54f", "recycler": "9ccc65", "neutralizer": "8fc6f0",
    "filter-press": "a5d86a", "cement-kiln": "e8d0a0", "unit-factory": "ffd37f",
    "acid-plant": "e8cf52", "resource-refinery": "45e07a",
    "steel-container": "9898a0", "steel-vault": "9898a0",
    "supply-unloader": "5cd8e8",
}

MACHINE_SIZES = {
    "rotary-drill": 2, "copper-smelter": 2, "blast-furnace": 3, "alloy-furnace": 2,
    "electrolysis-plant": 2, "chemical-processor": 2, "centrifuge": 3,
    "nuclear-reactor": 3, "coal-generator": 2, "battery-cell": 1, "recycler": 2,
    "neutralizer": 2, "filter-press": 2, "cement-kiln": 2, "unit-factory": 3,
    "acid-plant": 2, "resource-refinery": 3,
}

TURRET_SIZES = {"bronze-gun": 1, "steel-howitzer": 2, "aluminum-flak": 2,
                "uranium-lance": 4}
TURRET_HUE = {"bronze-gun": "cd7f32", "steel-howitzer": "9aa6b2",
              "aluminum-flak": "cdd5dc", "uranium-lance": "45e07a"}

WALLS = {"cement-wall": "c8c0ac", "bronze-wall": "c08858", "steel-wall": "98a0aa",
         "steel-wall-large": "98a0aa", "aluminum-wall": "ccd4dc"}
WALL_SIZES = {"cement-wall": 1, "bronze-wall": 1, "steel-wall": 1,
              "steel-wall-large": 2, "aluminum-wall": 1}

UNITS = {
    "bronze-crawler": {"size": 48, "accent": "f8a05c", "legs": True},
    "aluminum-wasp": {"size": 48, "accent": "5cd8e8", "legs": False},
    "steel-brawler": {"size": 48, "accent": "f8a05c", "legs": True},
}


def machine_plate(w):
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    bevel_rect(d, 1, 1, w - 1, w - 1, MET_L, MET_M, MET_D)
    return img, d


def claw_corners(d, w, inset, size, color=FRAME):
    for cx, cy in [(inset, inset), (w - inset, inset), (inset, w - inset),
                   (w - inset, w - inset)]:
        sx = 1 if cx < w / 2 else -1
        sy = 1 if cy < w / 2 else -1
        rect(d, [min(cx, cx + sx * size), min(cy, cy + sy * size),
                 max(cx, cx + sx * size), max(cy, cy + sy * size)], color)


def draw_machine(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    A_L, A_M, A_D = tri(ac)
    img, d = machine_plate(w)
    cx = w / 2
    if name == "rotary-drill":
        rect(d, [w * 0.28, w * 0.28, w * 0.72, w * 0.72], FRAME)
        rect(d, [w * 0.34, w * 0.34, w * 0.66, w * 0.66], MET_D)
        ell(d, [w * 0.42, w * 0.42, w * 0.58, w * 0.58], A_M, A_D)
    elif name in ("copper-smelter", "blast-furnace", "alloy-furnace", "cement-kiln"):
        aw = w * 0.5
        x0, y0 = cx - aw / 2, w * 0.34
        rect(d, [x0, y0, x0 + aw, y0 + w * 0.38], FRAME, r=int(aw / 4))
        rect(d, [x0 + 2, y0 + 2, x0 + aw - 2, y0 + w * 0.30],
             shade(A_M, 0.9), r=int(aw / 5))
        rect(d, [cx - aw * 0.14, y0 + w * 0.12, cx + aw * 0.14, y0 + w * 0.36],
             A_L, line=None, lw=0)
        claw_corners(d, w, 3, int(w * 0.09))
    elif name == "electrolysis-plant":
        for i, fx in enumerate([0.28, 0.5, 0.72]):
            px = int(w * fx)
            c = [A_M, MET_L, A_M][i]
            rect(d, [px - 3, w * 0.22, px + 3, w * 0.78], c, line=A_D)
        d.line([int(w * 0.28), int(w * 0.32), int(w * 0.72), int(w * 0.62)],
               fill=A_L, width=2)
    elif name == "chemical-processor":
        rect(d, [w * 0.2, w * 0.24, w * 0.46, w * 0.5], A_M, line=A_D, r=2)
        poly(d, [(w * 0.58, w * 0.5), (w * 0.78, w * 0.5), (w * 0.68, w * 0.3)],
             A_L, line=A_D, lw=1)
        d.line([int(w * 0.46), int(w * 0.37), int(w * 0.58), int(w * 0.44)],
               fill=FRAME, width=2)
    elif name == "centrifuge":
        ell(d, [w * 0.2, w * 0.2, w * 0.8, w * 0.8], FRAME)
        ell(d, [w * 0.3, w * 0.3, w * 0.7, w * 0.7], MET_D, line=FRAME)
        ell(d, [w * 0.42, w * 0.42, w * 0.58, w * 0.58], A_M, A_D)
        for ang in (20, 140, 260):
            ax = math.cos(math.radians(ang)) * w * 0.24
            ay = math.sin(math.radians(ang)) * w * 0.24
            d.line([cx, cx, cx + ax, cx + ay], fill=A_L, width=3)
    elif name == "nuclear-reactor":
        ring = w * 0.32
        ell(d, [cx - ring, cx - ring, cx + ring, cx + ring], FRAME)
        ell(d, [cx - ring * 0.72, cx - ring * 0.72, cx + ring * 0.72,
                cx + ring * 0.72], MET_D)
        core = w * 0.18
        ell(d, [cx - core, cx - core, cx + core, cx + core], A_M, line=A_D)
        ci = core * 0.5
        ell(d, [cx - ci, cx - ci, cx + ci, cx + ci], A_L)
        for ang in range(0, 360, 45):
            ax = math.cos(math.radians(ang))
            ay = math.sin(math.radians(ang))
            d.line([cx + ax * core, cx + ay * core, cx + ax * ring * 0.95,
                    cx + ay * ring * 0.95], fill=FRAME, width=2)
    elif name == "coal-generator":
        rect(d, [w * 0.18, w * 0.18, w * 0.82, w * 0.6], FRAME, r=2)
        flame = [(cx, w * 0.18), (cx + w * 0.14, w * 0.4), (cx + w * 0.07, w * 0.58),
                 (cx - w * 0.07, w * 0.58), (cx - w * 0.14, w * 0.4)]
        poly(d, flame, A_M, line=A_D, lw=1)
        poly(d, [(cx, w * 0.28), (cx + w * 0.07, w * 0.44), (cx - w * 0.07, w * 0.44)],
             A_L)
        rect(d, [w * 0.24, w * 0.68, w * 0.76, w * 0.8], MET_D)
    elif name == "battery-cell":
        bw = w * 0.52
        x0, y0 = cx - bw / 2, w * 0.22
        rect(d, [x0, y0, x0 + bw, y0 + w * 0.56], A_M, line=A_D, r=2)
        rect(d, [x0 + 3, y0 + 3, x0 + bw - 3, y0 + w * 0.16], A_L, line=None, lw=0)
        rect(d, [x0 - 4, cx - 4, x0, cx + 4], MET_L, line=MET_D)
        rect(d, [x0 + bw, cx - 4, x0 + bw + 4, cx + 4], MET_D, line=FRAME)
    elif name == "recycler":
        ell(d, [w * 0.22, w * 0.22, w * 0.78, w * 0.78], FRAME)
        rr = w * 0.24
        for start in (210, 330, 90):
            pts = [(cx + math.cos(math.radians(start + t)) * rr,
                    cx + math.sin(math.radians(start + t)) * rr)
                   for t in range(0, 61, 12)]
            d.line(pts, fill=A_M, width=3)
            ex, ey = pts[-1]
            a = math.atan2(ey - pts[-2][1], ex - pts[-2][0])
            d.polygon([(ex + math.cos(a) * 5, ey + math.sin(a) * 5),
                       (ex + math.cos(a + 2.5) * 5, ey + math.sin(a + 2.5) * 5),
                       (ex + math.cos(a - 2.5) * 5, ey + math.sin(a - 2.5) * 5)],
                      fill=A_M)
    elif name == "neutralizer":
        ell(d, [w * 0.24, w * 0.24, w * 0.76, w * 0.76], FRAME)
        for i in range(3):
            yy = cx - 6 + i * 6
            pts = [(w * 0.32 + k * (w * 0.36 / 8), yy + math.sin(k * 1.3) * 2)
                   for k in range(9)]
            d.line(pts, fill=[A_D, A_M, A_L][i], width=2)
    elif name == "filter-press":
        for i, fy in enumerate([0.26, 0.44, 0.62]):
            rect(d, [w * 0.24, w * fy, w * 0.76, w * fy + w * 0.1],
                 [A_M, A_L, A_M][i], line=A_D)
        d.line([cx, w * 0.16, cx, w * 0.84], fill=FRAME, width=1)
    elif name == "acid-plant":
        ell(d, [w * 0.16, w * 0.24, w * 0.56, w * 0.64], A_M, line=A_D)
        ell(d, [w * 0.22, w * 0.3, w * 0.5, w * 0.58], A_L)
        rect(d, [w * 0.62, w * 0.2, w * 0.8, w * 0.8], FRAME, r=2)
        rect(d, [w * 0.66, w * 0.26, w * 0.76, w * 0.42], A_M, line=None, lw=0)
        d.line([int(w * 0.56), int(w * 0.44), int(w * 0.62), int(w * 0.44)],
               fill=FRAME, width=2)
    elif name == "resource-refinery":
        rect(d, [w * 0.14, w * 0.3, w * 0.3, w * 0.84], MET_D)
        rect(d, [w * 0.38, w * 0.16, w * 0.54, w * 0.84], FRAME)
        rect(d, [w * 0.42, w * 0.24, w * 0.5, w * 0.76], A_M, line=None, lw=0)
        rect(d, [w * 0.62, w * 0.4, w * 0.82, w * 0.84], shade(A_M, 1.1),
             line=A_D)
        d.line([int(w * 0.3), int(w * 0.5), int(w * 0.38), int(w * 0.5)],
               fill=FRAME, width=2)
        d.line([int(w * 0.54), int(w * 0.5), int(w * 0.62), int(w * 0.5)],
               fill=FRAME, width=2)
    elif name in ("steel-container", "steel-vault"):
        inset = w * 0.12
        bevel_rect(d, int(inset), int(inset), int(w - inset), int(w - inset),
                   MET_L, shade(MET_M, 0.96), MET_D, edge=1)
        for i in range(1, 3):
            yy = int(inset + (w - 2 * inset) * i / 3)
            d.line([inset + 2, yy, w - inset - 2, yy], fill=MET_D, width=2)
        d.line([inset + 2, int(yy + 2), w - inset - 2, int(yy + 2)],
               fill=MET_L, width=1)
    elif name == "supply-unloader":
        ell(d, [w * 0.2, w * 0.2, w * 0.8, w * 0.8], FRAME)
        ell(d, [w * 0.32, w * 0.32, w * 0.68, w * 0.68], A_M, line=A_D)
        ell(d, [w * 0.44, w * 0.44, w * 0.56, w * 0.56], A_L)
    elif name == "unit-factory":
        ell(d, [w * 0.2, w * 0.2, w * 0.8, w * 0.8], FRAME)
        ell(d, [w * 0.28, w * 0.28, w * 0.72, w * 0.72], MET_D, line=FRAME)
        ell(d, [w * 0.4, w * 0.4, w * 0.6, w * 0.6], A_M, line=A_D)
        for rx, ry in [(w * 0.12, w * 0.12), (w - w * 0.12, w * 0.12),
                       (w * 0.12, w - w * 0.12), (w - w * 0.12, w - w * 0.12)]:
            rect(d, [rx - 4, ry - 4, rx + 4, ry + 4], MET_D)
    return img


def drill_rotator():
    w = 2 * S
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    r = w * 0.3
    ell(d, [cx - r, cx - r, cx + r, cx + r], MET_D, line=FRAME)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        d.line([cx + math.cos(a) * r * 0.25, cx + math.sin(a) * r * 0.25,
                cx + math.cos(a) * r * 0.85, cx + math.sin(a) * r * 0.85],
               fill=MET_L, width=3)
    ell(d, [cx - r * 0.22, cx - r * 0.22, cx + r * 0.22, cx + r * 0.22],
        MET_L, line=FRAME)
    return img


def turret_gun(name, size):
    w = size * S
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    L, M, D = tri(hx(TURRET_HUE[name]))
    m = 4
    if name == "bronze-gun":
        rect(d, [cx - 4, m, cx + 4, 16], D, r=1)
        rect(d, [cx - 2, m, cx, 14], L, line=None, lw=0)
        rect(d, [cx - 7, 14, cx + 7, 27], M, line=D, r=2)
        d.line([cx - 6, 17, cx + 6, 17], fill=L, width=1)
    elif name == "steel-howitzer":
        rect(d, [cx - 7, m, cx + 7, 12], D, r=1)
        rect(d, [cx - 4, 8, cx + 4, 34], M, line=D)
        d.line([cx - 4, 12, cx + 4, 12], fill=L, width=2)
        rect(d, [cx - 13, 30, cx + 13, 56], M, line=D, r=3)
        rect(d, [cx - 13, 34, cx + 13, 36], L, line=None, lw=0)
        d.line([cx - 13, 53, cx + 13, 53], fill=D, width=2)
    elif name == "aluminum-flak":
        for off in (-6, 6):
            rect(d, [cx + off - 2, m, cx + off + 2, 26], M, line=D)
            d.line([cx + off - 1, m + 1, cx + off - 1, 8], fill=L, width=1)
        ell(d, [cx - 12, 22, cx + 12, 46], M, line=D)
        ell(d, [cx - 6, 28, cx + 6, 40], L, line=D)
    elif name == "uranium-lance":
        rect(d, [cx - 15, 8, cx - 11, 98], D)
        rect(d, [cx + 11, 8, cx + 15, 98], D)
        rect(d, [cx - 5, m, cx + 5, 104], M, line=D)
        rect(d, [cx - 1, 8, cx + 1, 102], L, line=None, lw=0)
        rect(d, [cx - 20, 94, cx + 20, 122], M, line=D, r=4)
        rect(d, [cx - 20, 100, cx + 20, 104], L, line=None, lw=0)
        d.line([cx - 20, 119, cx + 20, 119], fill=D, width=2)
        ell(d, [cx - 8, 108, cx + 8, 120], L, line=D)
    return img


def wall_sprite(name):
    size = WALL_SIZES[name]
    w = size * S
    L, M, D = tri(hx(WALLS[name]))
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    bevel_rect(d, 0, 0, w - 1, w - 1, L, M, D, edge=max(2, w // 16))
    inset = max(4, w // 6)
    d.line([inset, inset, w - inset, inset], fill=shade(L, 1.06), width=1)
    d.line([inset, w - inset - 1, w - inset, w - inset - 1], fill=D, width=1)
    return img


def core_sprite(size, accent_hex):
    w = size * S
    L, M, D = tri(hx("9aa0a8"))
    acc = hx(accent_hex)
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    bevel_rect(d, 0, 0, w - 1, w - 1, L, M, D, edge=max(2, w // 24))
    u = w / 96
    for mx, my in [(u * 14, u * 14), (w - u * 14, u * 14),
                   (u * 14, w - u * 14), (w - u * 14, w - u * 14)]:
        rect(d, [mx - u * 8, my - u * 8, mx + u * 8, my + u * 8], FRAME, r=2)
        rect(d, [mx - u * 3, my - u * 3, mx + u * 3, my + u * 3], MET_D)
    ring = w * 0.30
    pts = [(w / 2 + ring * math.cos(math.pi / 4 + i * math.pi / 2) * 1.2,
            w / 2 + ring * math.sin(math.pi / 4 + i * math.pi / 2)) for i in range(4)]
    poly(d, pts, FRAME)
    r2 = ring * 0.72
    pts2 = [(w / 2 + r2 * math.cos(math.pi / 4 + i * math.pi / 2) * 1.2,
             w / 2 + r2 * math.sin(math.pi / 4 + i * math.pi / 2)) for i in range(4)]
    poly(d, pts2, MET_D)
    cr = ring * 0.42
    ell(d, [w / 2 - cr, w / 2 - cr, w / 2 + cr, w / 2 + cr], acc, line=shade(acc, 0.7))
    cri = cr * 0.45
    ell(d, [w / 2 - cri, w / 2 - cri, w / 2 + cri, w / 2 + cri],
        shade(acc, 1.55))
    return img


ORE_STONE_L = (86, 84, 82, 255)
ORE_STONE_D = (70, 69, 67, 255)


def ore_tile(seed, item_hex):
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    rect(d, [0, 0, S - 1, S - 1], ORE_STONE_L)
    for _ in range(6):
        x, y = rng.randrange(1, 30), rng.randrange(1, 30)
        s = rng.choice((1, 2))
        d.rectangle([x, y, x + s, y + s], fill=ORE_STONE_D)
    mineral = hx(item_hex)
    MM, ML, MD = shade(mineral, 0.95), shade(mineral, 1.25), shade(mineral, 0.7)
    for _ in range(4):
        x, y = rng.randrange(5, 22), rng.randrange(5, 22)
        for _ in range(rng.randint(3, 5)):
            ox, oy = x + rng.randint(-4, 4), y + rng.randint(-4, 4)
            s = rng.choice((1, 2))
            c = rng.choice((MM, ML))
            d.rectangle([ox, oy, ox + s, oy + s], fill=c)
            d.point([(ox, oy + s)], fill=MD)
    return img


def unit_body(name):
    u = UNITS[name]
    w = u["size"]
    acc = hx(u["accent"])
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    if name == "bronze-crawler":
        poly(d, [(cx - 12, cx + 8), (cx - 14, cx - 2), (cx - 8, cx - 12),
                 (cx + 8, cx - 12), (cx + 14, cx - 2), (cx + 12, cx + 8)], MET_M,
             line=MET_D, lw=1)
        poly(d, [(cx - 9, cx - 9), (cx + 9, cx - 9), (cx + 5, cx - 3),
                 (cx - 5, cx - 3)], MET_L, line=None, lw=0)
        ell(d, [cx - 4, cx + 1, cx + 4, cx + 9], acc, line=shade(acc, 0.7))
        rect(d, [cx - 2, cx - 17, cx + 2, cx - 11], MET_D)
    elif name == "aluminum-wasp":
        poly(d, [(cx, 4), (cx + 10, cx - 4), (cx + 7, cx + 10), (cx - 7, cx + 10),
                 (cx - 10, cx - 4)], MET_M, line=MET_D, lw=1)
        poly(d, [(cx, 6), (cx + 5, cx - 5), (cx - 5, cx - 5)], MET_L, line=None, lw=0)
        ell(d, [cx - 3, cx - 4, cx + 3, cx + 2], shade(acc, 1.1), line=MET_D)
        ell(d, [cx - 3, cx + 10, cx + 3, cx + 15], acc)
    else:
        poly(d, [(cx - 16, cx - 4), (cx - 10, cx - 13), (cx + 10, cx - 13),
                 (cx + 16, cx - 4), (cx + 12, cx + 12), (cx - 12, cx + 12)],
             MET_M, line=MET_D, lw=1)
        rect(d, [cx - 18, cx - 4, cx - 10, cx + 6], MET_L, line=MET_D, r=2)
        rect(d, [cx + 10, cx - 4, cx + 18, cx + 6], MET_L, line=MET_D, r=2)
        poly(d, [(cx - 8, cx - 10), (cx + 8, cx - 10), (cx + 4, cx - 4),
                 (cx - 4, cx - 4)], MET_L, line=None, lw=0)
        ell(d, [cx - 4, cx + 2, cx + 4, cx + 10], acc, line=shade(acc, 0.7))
        rect(d, [cx - 3, cx - 19, cx + 3, cx - 12], MET_D)
        rect(d, [cx - 13, cx - 18, cx - 8, cx - 12], MET_D)
        rect(d, [cx + 8, cx - 18, cx + 13, cx - 12], MET_D)
    return img


def unit_base(name):
    w = UNITS[name]["size"]
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    ell(d, [cx - w * 0.26, cx - w * 0.2, cx + w * 0.26, cx + w * 0.2], FRAME)
    ell(d, [cx - w * 0.18, cx - w * 0.13, cx + w * 0.18, cx + w * 0.13], MET_D)
    return img


def unit_leg(size):
    img = img_new(48, 48)
    d = ImageDraw.Draw(img)
    d.line([6, 42, 40, 6], fill=MET_D, width=7)
    d.line([8, 41, 39, 8], fill=MET_M, width=3)
    d.line([8, 40, 38, 7], fill=MET_L, width=1)
    return img


def main():
    count = 0
    for name, (kind, hexs) in ITEMS.items():
        if kind == "lump":
            item_lump(hash(name) & 0xFFFF, hexs).save(f"{ROOT}/items/{name}.png")
        elif kind == "crystal":
            item_crystal(hash(name) & 0xFFFF, hexs).save(f"{ROOT}/items/{name}.png")
        elif kind == "ingot":
            item_ingot(hexs).save(f"{ROOT}/items/{name}.png")
        elif kind == "pebbles":
            item_pebbles(hash(name) & 0xFFFF, hexs).save(f"{ROOT}/items/{name}.png")
        else:
            item_sack(hexs).save(f"{ROOT}/items/{name}.png")
        count += 1
    os.makedirs(f"{ROOT}/liquids", exist_ok=True)
    for name, hexs in LIQUIDS.items():
        liquid_icon(hexs).save(f"{ROOT}/liquids/{name}.png")
        count += 1
    for name, size in MACHINE_SIZES.items():
        if name == "unit-factory":
            draw_machine(name, size).save(f"{ROOT}/blocks/{name}.png")
        else:
            draw_machine(name, size).save(f"{ROOT}/blocks/{name}.png")
        count += 1
    drill_rotator().save(f"{ROOT}/blocks/rotary-drill-rotator.png")
    count += 1
    for name, size in TURRET_SIZES.items():
        turret_gun(name, size).save(f"{ROOT}/blocks/{name}.png")
        count += 1
    for name in WALLS:
        wall_sprite(name).save(f"{ROOT}/blocks/{name}.png")
        count += 1
    core_sprite(3, "50c878").save(f"{ROOT}/blocks/core-industry.png")
    core_sprite(4, "45e07a").save(f"{ROOT}/blocks/core-fortress.png")
    count += 2
    os.makedirs(f"{ROOT}/units", exist_ok=True)
    for name, u in UNITS.items():
        unit_body(name).save(f"{ROOT}/units/{name}.png")
        unit_base(name).save(f"{ROOT}/units/{name}-base.png")
        count += 2
        if u["legs"]:
            unit_leg(u["size"]).save(f"{ROOT}/units/{name}-leg.png")
            count += 1
    ores = ["bauxite", "hematite", "chalcopyrite", "cassiterite", "galena",
            "uraninite", "quartz", "graphite", "limestone", "beryl"]
    colors = {"bauxite": "d4a373", "hematite": "9c5630", "chalcopyrite": "daa520",
              "cassiterite": "b8b8bc", "galena": "708090", "uraninite": "50c878",
              "quartz": "e8e4d8", "graphite": "606060", "limestone": "d8cba8",
              "beryl": "7cc87c"}
    for ore in ores:
        for v in (1, 2):
            ore_tile(hash((ore, v)) & 0xFFFF, colors[ore]).save(
                f"{ROOT}/blocks/ore-{ore}{v}.png")
            count += 1
    print(f"generated {count} sprites")


if __name__ == "__main__":
    main()
