import math
import os
import random
from PIL import Image, ImageDraw

ROOT = "/root/RealIndustry/sprites"
S = 32
VAN = "/tmp/opencode/vanilla"

MET_L = (176, 184, 192, 255)
MET_M = (152, 152, 160, 255)
MET_D = (104, 112, 128, 255)
MET_F = (72, 74, 84, 255)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def shade(c, f):
    if f >= 1:
        t = min(1.0, f - 1)
        return tuple(min(255, int(v + (255 - v) * t * 0.85)) for v in c[:3]) + (255,)
    return tuple(int(v * f) for v in c[:3]) + (255,)


def tri(c):
    return [shade(c, 1.3), c, shade(c, 0.66)]


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


def oct(d, cx, cy, r, rot=22, fill=MET_F, line=None):
    pts = [(cx + r * math.cos(math.radians(rot + i * 45)),
            cy + r * math.sin(math.radians(rot + i * 45))) for i in range(8)]
    poly(d, pts, fill, line=line)


def plate(w, L=MET_L, M=MET_M, D=MET_D):
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    rect(d, [0, 0, w - 1, w - 1], M)
    e = max(2, w // 16)
    d.line([0, 0, w - 1, 0], fill=L, width=e)
    d.line([0, 0, 0, w - 1], fill=L, width=e)
    d.line([0, w - e, w - 1, w - e], fill=D, width=e)
    d.line([w - e, 0, w - e, w - 1], fill=D, width=e)
    return img, d


def claws(d, w, u, color=MET_F):
    s = int(w * u)
    c = s
    for sx, sy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        x = 0 if sx == 0 else w - c
        y = 0 if sy == 0 else w - c
        rect(d, [x, y, x + c, y + c], color)
        pass


ITEMS = {
    "bauxite": ("lump", "d4a373"), "hematite": ("lump", "9c5630"),
    "chalcopyrite": ("lump", "daa520"), "cassiterite": ("lump", "b0b0b6"),
    "galena": ("lump", "708090"), "limestone": ("lump", "d8cba8"),
    "uraninite": ("crystal", "50c878"), "quartz": ("crystal", "e8e4d8"),
    "beryl": ("crystal", "7cc87c"), "aluminum": ("ingot", "ccd4dc"),
    "steel": ("ingot", "8f9aa6"), "bronze": ("ingot", "cd7f32"),
    "enriched-uranium": ("alloy", "45e07a"), "gravel": ("chunks", "9d968a"),
    "cement": ("sack", "b8b4ac"), "fertilizer": ("sack", "7cb342"),
}

LIQUIDS = {"sulfuric-acid": "d9c25f", "spent-acid": "b5722f",
           "waste-sludge": "6a6c40"}


def item_lump(seed, hexs):
    L, M, D = tri(hx(hexs))
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    cx = cy = 16
    r0 = 11
    pts = [(cx + r0 * math.cos(2 * math.pi * i / 6 + rng.uniform(-0.2, 0.2)) * rng.uniform(0.85, 1.05),
            cy + r0 * math.sin(2 * math.pi * i / 6 + rng.uniform(-0.2, 0.2)) * rng.uniform(0.85, 1.05))
           for i in range(6)]
    poly(d, pts, M, line=D, lw=1)
    poly(d, [pts[4], pts[5], pts[0], (cx, cy)], L, line=None, lw=0)
    poly(d, [pts[1], pts[2], pts[3], (cx, cy)], D, line=None, lw=0)
    d.line(pts + [pts[0]], fill=D, width=1)
    return img


def item_crystal(seed, hexs):
    L, M, D = tri(hx(hexs))
    img = img_new()
    d = ImageDraw.Draw(img)
    for i, sp in enumerate([[(7, 27), (6, 13), (10, 5), (14, 14), (13, 27)],
                            [(13, 26), (14, 6), (19, 3), (22, 13), (21, 26)],
                            [(20, 27), (23, 12), (26, 10), (26, 21), (24, 27)]]):
        c = [M, L, shade(M, 0.82)][i]
        poly(d, sp, c, line=D, lw=1)
        d.line([sp[1], sp[2]], fill=shade(L, 1.2) if i == 1 else L, width=1)
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
    poly(d, [(5, 21), (17, 26), (17, 29), (5, 24)], D)
    d.line([(5, 21), (16, 12)], fill=L, width=1)
    return img


def item_alloy(hexs):
    L, M, D = tri(hx(hexs))
    img = img_new()
    d = ImageDraw.Draw(img)
    rect(d, [7, 7, 25, 25], M, line=D, lw=1, r=3)
    for i in range(3):
        off = 9 + i * 5
        d.line([off, 24, off + 6, 12], fill=L if i % 2 == 0 else shade(M, 1.14),
               width=2)
    d.line([8, 8, 24, 8], fill=L, width=1)
    return img


def item_chunks(seed, hexs):
    L, M, D = tri(hx(hexs))
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    for x, y, s in [(8, 22, 5), (18, 23, 6), (14, 13, 5), (23, 13, 4)]:
        pts = [(x - s, y + s * 0.6), (x - s * 0.6, y - s * 0.7),
               (x + s * 0.5, y - s), (x + s, y + s * 0.5), (x + s * 0.2, y + s)]
        pts = [(px + rng.uniform(-1, 1), py + rng.uniform(-1, 1)) for px, py in pts]
        poly(d, pts, M, line=D, lw=1)
        poly(d, [pts[1], pts[2], pts[3]], L, line=None, lw=0)
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
    "rotary-drill": "cd7f32", "copper-smelter": "e8a85c", "blast-furnace": "ff8f3d",
    "alloy-furnace": "cd7f32", "electrolysis-plant": "5cd8e8",
    "chemical-processor": "8fce4e", "centrifuge": "50c878",
    "nuclear-reactor": "b088f0", "coal-generator": "ffb35c",
    "battery-cell": "ffd54f", "recycler": "9ccc65", "neutralizer": "8fc6f0",
    "filter-press": "a5d86a", "cement-kiln": "e8a05c", "unit-factory": "ffd37f",
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
    "steel-container": 2, "steel-vault": 3, "supply-unloader": 1,
}

TURRET_CANVAS = {"bronze-gun": 32, "steel-howitzer": 64, "aluminum-flak": 64,
                 "uranium-lance": 128}
TURRET_HUE = {"bronze-gun": "c08858", "steel-howitzer": "8a96a4",
              "aluminum-flak": "c8d0d8", "uranium-lance": "45b878"}

WALLS = {"cement-wall": "c8c0ac", "bronze-wall": "c08858", "steel-wall": "98a0aa",
         "steel-wall-large": "98a0aa", "aluminum-wall": "ccd4dc"}
WALL_SIZES = {"cement-wall": 1, "bronze-wall": 1, "steel-wall": 1,
              "steel-wall-large": 2, "aluminum-wall": 1}

UNITS = {
    "bronze-crawler": {"size": 48, "accent": "b088f0", "legs": True},
    "aluminum-wasp": {"size": 48, "accent": "5cd8e8", "legs": False},
    "steel-brawler": {"size": 48, "accent": "f8a05c", "legs": True},
}


def bp_smelter(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    claws(d, w, 0.16)
    r = w * 0.30
    oct(d, w / 2, w / 2, r, fill=MET_F, line=shade(MET_F, 0.8))
    oct(d, w / 2, w / 2, r * 0.62, fill=MET_D)
    r3 = r * 0.34
    ell(d, [w / 2 - r3, w / 2 - r3, w / 2 + r3, w / 2 + r3], shade(ac, 0.9),
        line=shade(ac, 0.6))
    ri = r3 * 0.5
    ell(d, [w / 2 - ri, w / 2 - ri, w / 2 + ri, w / 2 + ri], shade(ac, 1.5))
    return img


def bp_kiln_furnace(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    u = w / 64
    for qx, qy in [(u * 6, u * 6), (w - u * 6, u * 6), (u * 6, w - u * 6),
                   (w - u * 6, w - u * 6)]:
        rect(d, [min(qx, qx + u * 8 * (1 if qx < w / 2 else -1)),
                 min(qy, qy + u * 8 * (1 if qy < w / 2 else -1)),
                 max(qx, qx + u * 8 * (1 if qx < w / 2 else -1)),
                 max(qy, qy + u * 8 * (1 if qy < w / 2 else -1))], MET_F)
    oct(d, w / 2, w / 2, w * 0.32, fill=MET_F)
    oct(d, w / 2, w / 2, w * 0.22, fill=shade(MET_F, 0.75))
    oct(d, w / 2, w / 2, w * 0.14, fill=shade(ac, 0.85))
    for i, fy in enumerate([w * 0.2, w * 0.72]):
        rect(d, [w * 0.08, fy, w * 0.14, fy + w * 0.08], shade(ac, 1.1))
        rect(d, [w * 0.86, fy, w * 0.92, fy + w * 0.08], shade(ac, 1.1))
    return img


def bp_mixer(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    u = w / 64
    for qx, qy in [(u * 8, u * 8), (w - u * 14, u * 8), (u * 8, w - u * 14),
                   (w - u * 14, w - u * 14)]:
        rect(d, [qx, qy, qx + u * 6, qy + u * 6], MET_D, line=MET_F)
    r = w * 0.30
    ell(d, [w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r], MET_F, line=shade(MET_F, 0.8))
    r2 = r * 0.72
    ell(d, [w / 2 - r2, w / 2 - r2, w / 2 + r2, w / 2 + r2], shade(MET_F, 1.2))
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        px = w / 2 + math.cos(a) * r2 * 0.55
        py = w / 2 + math.sin(a) * r2 * 0.55
        ell(d, [px - u * 3, py - u * 3, px + u * 3, py + u * 3], ac)
    return img


def bp_centrifuge(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    u = w / 96
    for qx, qy in [(u * 8, u * 8), (w - u * 20, u * 8), (u * 8, w - u * 20),
                   (w - u * 20, w - u * 20)]:
        rect(d, [qx, qy, qx + u * 12, qy + u * 12], MET_D, line=MET_F)
    r = w * 0.30
    ell(d, [w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r], MET_F, line=shade(MET_F, 0.8))
    r2 = r * 0.7
    ell(d, [w / 2 - r2, w / 2 - r2, w / 2 + r2, w / 2 + r2], shade(MET_F, 1.25))
    r3 = r * 0.4
    ell(d, [w / 2 - r3, w / 2 - r3, w / 2 + r3, w / 2 + r3], ac, line=shade(ac, 0.6))
    ri = r3 * 0.45
    ell(d, [w / 2 - ri, w / 2 - ri, w / 2 + ri, w / 2 + ri], shade(ac, 1.6))
    for ang in range(0, 360, 90):
        ax = math.cos(math.radians(ang + 45)) * r2 * 0.8
        ay = math.sin(math.radians(ang + 45)) * r2 * 0.8
        d.line([w / 2, w / 2, w / 2 + ax, w / 2 + ay], fill=MET_D, width=max(2, int(u * 3)))
    return img


def bp_reactor(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    u = w / 96
    for ang_box in [(w * 0.42, u * 2, w * 0.58, u * 12),
                    (w * 0.42, w - u * 12, w * 0.58, w - u * 2),
                    (u * 2, w * 0.42, u * 12, w * 0.58),
                    (w - u * 12, w * 0.42, w - u * 2, w * 0.58)]:
        rect(d, list(ang_box), shade(ac, 0.8), line=shade(ac, 0.55))
    claws(d, w, u * 4, MET_F)
    r = w * 0.30
    ell(d, [w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r], MET_F, line=shade(MET_F, 0.8))
    oct(d, w / 2, w / 2, r * 0.72, fill=shade(MET_F, 1.2), line=MET_F)
    r3 = r * 0.38
    ell(d, [w / 2 - r3, w / 2 - r3, w / 2 + r3, w / 2 + r3], ac, line=shade(ac, 0.6))
    ri = r3 * 0.5
    ell(d, [w / 2 - ri, w / 2 - ri, w / 2 + ri, w / 2 + ri], shade(ac, 1.6))
    return img


def bp_combustion(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    u = w / 64
    rect(d, [w * 0.3, w * 0.3, w * 0.7, w * 0.7], MET_F, r=2)
    rect(d, [w * 0.36, w * 0.36, w * 0.64, w * 0.56], shade(MET_F, 1.3))
    rect(d, [w * 0.42, w * 0.42, w * 0.58, w * 0.52], ac, line=shade(ac, 0.6))
    rect(d, [w * 0.14, w * 0.14, w * 0.24, w * 0.3], MET_D, line=MET_F)
    rect(d, [w * 0.76, w * 0.14, w * 0.86, w * 0.3], MET_D, line=MET_F)
    d.line([int(w * 0.5), int(w * 0.14), int(w * 0.5), int(w * 0.3)],
           fill=shade(ac, 1.2), width=max(2, int(u * 3)))
    return img


def bp_airfactory(name, size):
    w = size * S
    ac = hx(BLOCK_ACCENTS[name])
    img, d = plate(w)
    u = w / 96
    rect(d, [u * 12, u * 12, w - u * 12, w - u * 12], shade(MET_M, 1.06),
         line=MET_D, r=6)
    rect(d, [u * 20, u * 20, w - u * 20, w - u * 20], MET_D, r=4)
    rect(d, [u * 28, u * 28, w - u * 28, w - u * 28], shade(MET_D, 1.15), r=3)
    r = w * 0.14
    ell(d, [w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r], ac, line=shade(ac, 0.6))
    for qx, qy in [(u * 8, u * 8), (w - u * 16, u * 8), (u * 8, w - u * 16),
                   (w - u * 16, w - u * 16)]:
        rect(d, [qx, qy, qx + u * 8, qy + u * 8], MET_F)
    return img


def bp_drill(size):
    w = size * S
    img, d = plate(w)
    u = w / 64
    rect(d, [w * 0.42, u * 4, w * 0.58, w * 0.42], MET_F)
    rect(d, [w * 0.42, w * 0.58, w * 0.58, w - u * 4], MET_F)
    rect(d, [u * 4, w * 0.42, w * 0.42, w * 0.58], MET_F)
    rect(d, [w * 0.58, w * 0.42, w - u * 4, w * 0.58], MET_F)
    r = w * 0.2
    ell(d, [w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r], MET_D, line=MET_F)
    r2 = r * 0.5
    ell(d, [w / 2 - r2, w / 2 - r2, w / 2 + r2, w / 2 + r2], MET_L, line=MET_D)
    return img


def drill_rotator():
    w = 2 * S
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    r = w * 0.32
    for i in range(3):
        a = i * 2 * math.pi / 3
        pts = [(cx + math.cos(a) * r, cx + math.sin(a) * r),
               (cx + math.cos(a + 2.2) * r * 0.45, cx + math.sin(a + 2.2) * r * 0.45),
               (cx + math.cos(a - 2.2) * r * 0.45, cx + math.sin(a - 2.2) * r * 0.45)]
        poly(d, pts, MET_M, line=MET_D, lw=1)
        poly(d, [(cx + math.cos(a) * r * 0.9, cx + math.sin(a) * r * 0.9),
                 (cx + math.cos(a + 2.0) * r * 0.4, cx + math.sin(a + 2.0) * r * 0.4),
                 (cx + math.cos(a - 2.0) * r * 0.4, cx + math.sin(a - 2.0) * r * 0.4)],
             MET_L, line=None, lw=0)
    ell(d, [cx - r * 0.3, cx - r * 0.3, cx + r * 0.3, cx + r * 0.3], MET_D,
        line=MET_F)
    return img


def bp_turret(name):
    w = TURRET_CANVAS[name]
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    L, M, D = tri(hx(TURRET_HUE[name]))
    m = 4
    if name == "bronze-gun":
        rect(d, [cx - 3, m, cx + 3, 15], D)
        rect(d, [cx - 1, m + 1, cx + 1, 13], L, line=None, lw=0)
        rect(d, [cx - 8, 13, cx + 8, 28], M, line=D, lw=1)
        rect(d, [cx - 8, 15, cx + 8, 17], L, line=None, lw=0)
        d.line([cx - 8, 26, cx + 8, 26], fill=D, width=1)
    elif name == "steel-howitzer":
        rect(d, [cx - 8, m, cx + 8, 12], D)
        rect(d, [cx - 4, 8, cx + 4, 36], M, line=D)
        rect(d, [cx - 4, 12, cx + 4, 15], L, line=None, lw=0)
        rect(d, [cx - 14, 30, cx + 14, 58], M, line=D, lw=1, r=3)
        rect(d, [cx - 14, 34, cx + 14, 37], L, line=None, lw=0)
        d.line([cx - 14, 55, cx + 14, 55], fill=D, width=2)
        ell(d, [cx - 5, 44, cx + 5, 52], D)
    elif name == "aluminum-flak":
        for off in (-7, 7):
            rect(d, [cx + off - 2, m, cx + off + 2, 24], M, line=D)
            d.line([cx + off - 1, m + 1, cx + off - 1, 7], fill=L, width=1)
        ell(d, [cx - 13, 20, cx + 13, 46], M, line=D)
        ell(d, [cx - 7, 26, cx + 7, 40], L, line=D)
        ell(d, [cx - 2, 31, cx + 2, 35], shade(L, 1.2))
    elif name == "uranium-lance":
        rect(d, [cx - 16, 8, cx - 12, 96], D)
        rect(d, [cx + 12, 8, cx + 16, 96], D)
        rect(d, [cx - 5, m, cx + 5, 102], M, line=D)
        rect(d, [cx - 1, 8, cx + 1, 100], L, line=None, lw=0)
        rect(d, [cx - 22, 92, cx + 22, 122], M, line=D, r=4)
        rect(d, [cx - 22, 98, cx + 22, 102], L, line=None, lw=0)
        d.line([cx - 22, 119, cx + 22, 119], fill=D, width=2)
        ell(d, [cx - 9, 106, cx + 9, 118], L, line=D)
    return img


def wall_sprite(name):
    size = WALL_SIZES[name]
    w = size * S
    L, M, D = tri(hx(WALLS[name]))
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    e = max(2, w // 16)
    rect(d, [0, 0, w - 1, w - 1], M)
    d.line([0, 0, w - 1, 0], fill=L, width=e)
    d.line([0, 0, 0, w - 1], fill=L, width=e)
    d.line([0, w - e, w - 1, w - e], fill=D, width=e)
    d.line([w - e, 0, w - e, w - 1], fill=D, width=e)
    inset = max(3, w // 7)
    d.line([inset, inset, w - inset, inset], fill=shade(L, 1.05), width=1)
    d.line([inset, w - inset, w - inset, w - inset], fill=shade(D, 0.92), width=1)
    return img


def core_sprite(size, accent_hex):
    w = size * S
    acc = hx(accent_hex)
    img, d = plate(w)
    u = w / 96
    for mx, my in [(u * 16, u * 16), (w - u * 16, u * 16),
                   (u * 16, w - u * 16), (w - u * 16, w - u * 16)]:
        rect(d, [mx - u * 9, my - u * 9, mx + u * 9, my + u * 9], MET_F, r=2)
        rect(d, [mx - u * 4, my - u * 4, mx + u * 4, my + u * 4], MET_D)
    r = w * 0.26
    pts = [(w / 2 + r * math.cos(math.pi / 4 + i * math.pi / 2),
            w / 2 + r * math.sin(math.pi / 4 + i * math.pi / 2)) for i in range(4)]
    poly(d, pts, MET_F)
    r2 = r * 0.62
    pts2 = [(w / 2 + r2 * math.cos(math.pi / 4 + i * math.pi / 2),
             w / 2 + r2 * math.sin(math.pi / 4 + i * math.pi / 2)) for i in range(4)]
    poly(d, pts2, MET_D)
    cr = r * 0.3
    ell(d, [w / 2 - cr, w / 2 - cr, w / 2 + cr, w / 2 + cr], acc,
        line=shade(acc, 0.6))
    cri = cr * 0.45
    ell(d, [w / 2 - cri, w / 2 - cri, w / 2 + cri, w / 2 + cri], shade(acc, 1.55))
    return img


def bp_storage(name, size):
    w = size * S
    img, d = plate(w)
    inset = int(w * 0.14)
    rect(d, [inset, inset, w - inset, w - inset], shade(MET_M, 0.95),
         line=MET_D, lw=1)
    for i in range(1, 3):
        yy = int(inset + (w - 2 * inset) * i / 3)
        d.line([inset + 2, yy, w - inset - 2, yy], fill=MET_D, width=2)
        d.line([inset + 2, yy + 2, w - inset - 2, yy + 2], fill=MET_L, width=1)
    return img


def bp_unloader(size):
    w = size * S
    img, d = plate(w)
    r = w * 0.32
    ell(d, [w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r], MET_F)
    r2 = r * 0.66
    ell(d, [w / 2 - r2, w / 2 - r2, w / 2 + r2, w / 2 + r2], MET_D, line=MET_F)
    r3 = r * 0.3
    ell(d, [w / 2 - r3, w / 2 - r3, w / 2 + r3, w / 2 + r3], shade(MET_L, 1.1),
        line=MET_D)
    return img


ORE_STONE_L = (86, 84, 82, 255)


def ore_tile(seed, item_hex):
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    mineral = hx(item_hex)
    M, L, D = shade(mineral, 0.92), shade(mineral, 1.25), shade(mineral, 0.62)
    for _ in range(5):
        x, y = rng.randrange(6, 26), rng.randrange(6, 26)
        s = rng.uniform(3.5, 6.5)
        pts = []
        for i in range(5):
            a = 2 * math.pi * i / 5 + rng.uniform(-0.3, 0.3)
            rr = s * rng.uniform(0.7, 1.15)
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a) * 0.8))
        poly(d, pts, M, line=D, lw=1)
        poly(d, [pts[3], pts[4], pts[0]], L, line=None, lw=0)
    return img


def unit_body(name):
    u = UNITS[name]
    w = u["size"]
    acc = hx(u["accent"])
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    if name == "bronze-crawler":
        poly(d, [(cx - 15, cx + 6), (cx - 12, cx - 10), (cx, cx - 15),
                 (cx + 12, cx - 10), (cx + 15, cx + 6), (cx, cx + 13)],
             MET_M, line=MET_D, lw=1)
        poly(d, [(cx - 10, cx - 8), (cx, cx - 12), (cx + 10, cx - 8),
                 (cx, cx - 3)], MET_L, line=None, lw=0)
        r = 5
        ell(d, [cx - r, cx - r + 2, cx + r, cx + r + 2], acc, line=shade(acc, 0.6))
        ri = r * 0.45
        ell(d, [cx - ri, cx - ri + 2, cx + ri, cx + ri + 2], shade(acc, 1.5))
    elif name == "aluminum-wasp":
        poly(d, [(cx, 5), (cx + 11, cx - 6), (cx + 8, cx + 8), (cx + 3, cx + 12),
                 (cx - 3, cx + 12), (cx - 8, cx + 8), (cx - 11, cx - 6)],
             MET_M, line=MET_D, lw=1)
        poly(d, [(cx, 7), (cx + 5, cx - 6), (cx - 5, cx - 6)], MET_L, line=None, lw=0)
        ell(d, [cx - 3, cx - 5, cx + 3, cx], shade(acc, 1.1), line=MET_D)
        ell(d, [cx - 3, cx + 9, cx + 3, cx + 14], acc)
    else:
        poly(d, [(cx - 17, cx - 2), (cx - 11, cx - 12), (cx + 11, cx - 12),
                 (cx + 17, cx - 2), (cx + 12, cx + 11), (cx - 12, cx + 11)],
             MET_M, line=MET_D, lw=1)
        rect(d, [cx - 19, cx - 3, cx - 10, cx + 6], MET_L, line=MET_D, lw=1, r=2)
        rect(d, [cx + 10, cx - 3, cx + 19, cx + 6], MET_L, line=MET_D, lw=1, r=2)
        poly(d, [(cx - 9, cx - 9), (cx + 9, cx - 9), (cx + 5, cx - 4),
                 (cx - 5, cx - 4)], MET_L, line=None, lw=0)
        r = 5
        ell(d, [cx - r, cx + 1, cx + r, cx + 11], acc, line=shade(acc, 0.6))
        rect(d, [cx - 3, cx - 18, cx + 3, cx - 11], MET_D)
        rect(d, [cx - 14, cx - 17, cx - 9, cx - 11], MET_D)
        rect(d, [cx + 9, cx - 17, cx + 14, cx - 11], MET_D)
    return img


def unit_base(name):
    w = UNITS[name]["size"]
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    ell(d, [cx - w * 0.28, cx - w * 0.22, cx + w * 0.28, cx + w * 0.22], MET_F)
    ell(d, [cx - w * 0.19, cx - w * 0.14, cx + w * 0.19, cx + w * 0.14], MET_D)
    return img


def unit_leg():
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
        elif kind == "alloy":
            item_alloy(hexs).save(f"{ROOT}/items/{name}.png")
        elif kind == "chunks":
            item_chunks(hash(name) & 0xFFFF, hexs).save(f"{ROOT}/items/{name}.png")
        else:
            item_sack(hexs).save(f"{ROOT}/items/{name}.png")
        count += 1
    os.makedirs(f"{ROOT}/liquids", exist_ok=True)
    for name, hexs in LIQUIDS.items():
        liquid_icon(hexs).save(f"{ROOT}/liquids/{name}.png")
        count += 1
    for name, size in MACHINE_SIZES.items():
        if name == "rotary-drill":
            bp_drill(size).save(f"{ROOT}/blocks/{name}.png")
        elif name in ("copper-smelter", "blast-furnace", "alloy-furnace"):
            bp_smelter(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "cement-kiln":
            bp_kiln_furnace(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name in ("electrolysis-plant", "chemical-processor", "neutralizer",
                      "filter-press", "acid-plant"):
            bp_mixer(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "centrifuge":
            bp_centrifuge(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "nuclear-reactor":
            bp_reactor(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "coal-generator":
            bp_combustion(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "unit-factory":
            bp_airfactory(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "resource-refinery":
            bp_mixer(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name in ("steel-container", "steel-vault"):
            bp_storage(name, size).save(f"{ROOT}/blocks/{name}.png")
        elif name == "supply-unloader":
            bp_unloader(size).save(f"{ROOT}/blocks/{name}.png")
        else:
            draw_machine_fallback(name, size).save(f"{ROOT}/blocks/{name}.png")
        count += 1
    drill_rotator().save(f"{ROOT}/blocks/rotary-drill-rotator.png")
    count += 1
    for name in TURRET_CANVAS:
        bp_turret(name).save(f"{ROOT}/blocks/{name}.png")
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
            unit_leg().save(f"{ROOT}/units/{name}-leg.png")
            count += 1
    ores = ["bauxite", "hematite", "chalcopyrite", "cassiterite", "galena",
            "uraninite", "quartz", "graphite", "limestone", "beryl"]
    colors = {"bauxite": "d4a373", "hematite": "9c5630", "chalcopyrite": "daa520",
              "cassiterite": "b0b0b6", "galena": "708090", "uraninite": "50c878",
              "quartz": "e8e4d8", "graphite": "606060", "limestone": "d8cba8",
              "beryl": "7cc87c"}
    for ore in ores:
        for v in (1, 2):
            ore_tile(hash((ore, v)) & 0xFFFF, colors[ore]).save(
                f"{ROOT}/blocks/ore-{ore}{v}.png")
            count += 1
    print(f"generated {count} sprites")


def draw_machine_fallback(name, size):
    w = size * S
    img, d = plate(w)
    return img


if __name__ == "__main__":
    main()
