import math
import random
from PIL import Image, ImageDraw

ROOT = "/root/RealIndustry/sprites"
S = 32
OUT = (0, 0, 0, 235)
GREY = (74, 74, 76, 255)
GREY_L = (104, 104, 106, 255)
GREY_D = (52, 52, 54, 255)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def shade(c, f):
    if f >= 1:
        return tuple(min(255, int(v + (255 - v) * (f - 1) * 1.5)) for v in c[:3]) + (255,)
    return tuple(int(v * f) for v in c[:3]) + (255,)


def img_new(w=S, h=S):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def poly(d, pts, fill, line=OUT, lw=1):
    d.polygon(pts, fill=fill, outline=line, width=lw)


def rect(d, box, fill, line=OUT, lw=1, r=0):
    if r:
        d.rounded_rectangle(box, radius=r, fill=fill, outline=line, width=lw)
    else:
        d.rectangle(box, fill=fill, outline=line, width=lw)


def rivet(d, x, y, c=GREY_L):
    d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=c, outline=OUT)


def facet_poly(seed, base, size=20, n=7, lo=0.8, hi=1.05):
    rng = random.Random(seed)
    cx = cy = S / 2
    r0 = size / 2
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.16, 0.16)
        r = r0 * rng.uniform(0.8, 1.04)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    img = img_new()
    d = ImageDraw.Draw(img)
    poly(d, pts, base)
    top = [(x, y) for x, y in pts if y < cy]
    if len(top) >= 2:
        poly(d, top, shade(base, 1.28), line=None, lw=0)
    bot = [(x, y) for x, y in pts if y > cy + r0 * 0.3]
    if len(bot) >= 2:
        poly(d, bot, shade(base, 0.72), line=None, lw=0)
    d.line(pts + [pts[0]], fill=OUT, width=1)
    d.point([(cx - r0 * 0.25, cy - r0 * 0.35)], fill=shade(base, 1.55))
    return img


def item_ore(seed, hexs):
    return facet_poly(seed, hx(hexs), 22)


def item_ingot(hexs, glow=False):
    base = hx(hexs)
    img = img_new()
    d = ImageDraw.Draw(img)
    top = [(6, 20), (16, 13), (27, 18), (17, 24)]
    front = [(6, 20), (17, 24), (17, 29), (6, 25)]
    side = [(17, 24), (27, 18), (27, 23), (17, 29)]
    poly(d, front, shade(base, 0.78))
    poly(d, side, shade(base, 0.62))
    poly(d, top, shade(base, 1.22))
    d.line([(6, 20), (16, 13), (27, 18)], fill=shade(base, 1.45), width=1)
    if glow:
        d.ellipse([12, 16, 21, 21], fill=shade(base, 1.8))
    return img


def item_crystal(seed, hexs):
    base = hx(hexs)
    img = img_new()
    d = ImageDraw.Draw(img)
    spikes = [
        ((8, 27), (6, 12), (11, 5), (14, 14)),
        ((12, 26), (13, 7), (19, 3), (21, 13)),
        ((19, 27), (22, 11), (26, 9), (26, 20)),
    ]
    for i, sp in enumerate(spikes):
        c = base if i == 1 else shade(base, 0.85 if i == 0 else 1.18)
        poly(d, list(sp), c)
    d.line([spikes[1][1], spikes[1][2]], fill=shade(base, 1.5), width=1)
    return img


def item_slab(hexs):
    base = hx(hexs)
    img = img_new()
    d = ImageDraw.Draw(img)
    for (x0, y0, x1, y1), f in zip([(6, 12, 26, 17), (5, 17, 27, 22), (6, 22, 26, 27)],
                                   [1.18, 1.0, 0.8]):
        rect(d, [x0, y0, x1, y1], shade(base, f))
        d.line([x0 + 1, y0 + 1, x1 - 1, y0 + 1], fill=shade(base, f + 0.2), width=1)
    return img


def item_gem(hexs):
    base = hx(hexs)
    img = img_new()
    d = ImageDraw.Draw(img)
    cx, cy, r = 16, 16, 11
    pts = [(cx + r * math.cos(math.pi / 6 + 2 * math.pi * i / 6),
            cy + r * math.sin(math.pi / 6 + 2 * math.pi * i / 6)) for i in range(6)]
    poly(d, pts, base)
    inner = [(cx + r * 0.5 * math.cos(math.pi / 6 + 2 * math.pi * i / 6),
              cy + r * 0.5 * math.sin(math.pi / 6 + 2 * math.pi * i / 6)) for i in range(6)]
    poly(d, inner, shade(base, 1.3), line=None, lw=0)
    d.line([pts[5], pts[0]], fill=shade(base, 1.5), width=1)
    return img


def item_pebbles(seed, hexs):
    base = hx(hexs)
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    for i, (x, y, r) in enumerate(sorted([(8, 21, 6), (18, 23, 7), (13, 14, 5), (23, 14, 5)],
                                         key=lambda p: p[1])):
        c = shade(base, [0.85, 1.05, 1.2, 0.95][i])
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=c, outline=OUT, width=1)
    return img


def item_sack(hexs, mark):
    base = hx(hexs)
    img = img_new()
    d = ImageDraw.Draw(img)
    poly(d, [(9, 12), (23, 12), (25, 27), (7, 27)], base)
    poly(d, [(11, 8), (21, 8), (23, 12), (9, 12)], shade(base, 0.8))
    d.line([(9, 18), (23, 18)], fill=OUT, width=1)
    d.line([(9, 22), (23, 22)], fill=OUT, width=1)
    d.ellipse([13, 13, 19, 19], fill=mark)
    return img


ITEMS = {
    "bauxite": lambda: item_ore(101, "d4a373"),
    "hematite": lambda: item_ore(102, "8b4513"),
    "chalcopyrite": lambda: item_ore(103, "daa520"),
    "cassiterite": lambda: item_ore(104, "c0c0c0"),
    "galena": lambda: item_ore(105, "708090"),
    "uraninite": lambda: item_crystal(106, "50c878"),
    "quartz": lambda: item_crystal(107, "f5f5dc"),
    "limestone": lambda: item_slab("e8d5b7"),
    "beryl": lambda: item_gem("90ee90"),
    "aluminum": lambda: item_ingot("dfe5ea"),
    "steel": lambda: item_ingot("8f9aa6"),
    "bronze": lambda: item_ingot("cd7f32"),
    "enriched-uranium": lambda: item_ingot("45e07a", glow=True),
    "gravel": lambda: item_pebbles(108, "9d968a"),
    "cement": lambda: item_sack("bfbdb6", (120, 120, 120, 255)),
    "fertilizer": lambda: item_sack("7cb342", (40, 80, 30, 255)),
}

LIQUIDS = {"sulfuric-acid": "d9c25f", "spent-acid": "b5722f", "waste-sludge": "5f6136"}


def liquid_icon(hexs):
    base = hx(hexs)
    img = img_new()
    d = ImageDraw.Draw(img)
    d.polygon([(8, 17), (16, 4), (24, 17)], fill=base)
    d.pieslice([8, 10, 24, 26], 180, 360, fill=base)
    d.line([(8, 17), (16, 4), (24, 17)], fill=OUT, width=1)
    d.arc([8, 10, 24, 26], 180, 360, fill=OUT, width=1)
    d.line([(10, 17), (16, 7)], fill=shade(base, 1.5), width=1)
    d.ellipse([12, 15, 15, 19], fill=shade(base, 1.4))
    return img


def plate(size_px, base=GREY, accent=None, r=4):
    img = img_new(size_px, size_px)
    d = ImageDraw.Draw(img)
    m = 1
    rect(d, [m, m, size_px - m, size_px - m], base, r=r)
    d.line([m + 1, m + 1, size_px - m - 1, m + 1], fill=shade(base, 1.3), width=2)
    d.line([m + 1, m + 1, m + 1, size_px - m - 1], fill=shade(base, 1.15), width=2)
    d.line([m + 1, size_px - 3, size_px - m - 1, size_px - 3], fill=shade(base, 0.7), width=2)
    d.line([size_px - 3, m + 1, size_px - 3, size_px - m - 1], fill=shade(base, 0.7), width=2)
    if accent:
        rect(d, [size_px // 2 - 3, m + 4, size_px // 2 + 3, m + 8], accent, line=None, lw=0)
    return img, d


def machine_plate(size, accent_hex=None, r=4):
    acc = hx(accent_hex) if accent_hex else None
    return plate(size * S, GREY, acc, r)


def draw_arch(d, w, h, ac):
    cx = w / 2
    aw, ah = w * 0.46, h * 0.38
    x0, y0 = cx - aw / 2, h * 0.36
    rect(d, [x0, y0, x0 + aw, y0 + ah], GREY_D, r=int(aw / 3))
    rect(d, [x0 + 2, y0 + 2, x0 + aw - 2, y0 + ah * 0.7], ac, r=int(aw / 4))
    rect(d, [cx - aw * 0.16, y0 + ah * 0.3, cx + aw * 0.16, y0 + ah - 2],
         shade(ac, 1.5), line=None, lw=0)


def draw_machine(name, size):
    acc_hex = BLOCK_ACCENTS[name]
    w = size * S
    img, d = machine_plate(size, acc_hex)
    ac = hx(acc_hex)
    cx = w / 2
    if name in ("copper-smelter", "blast-furnace", "alloy-furnace", "cement-kiln"):
        draw_arch(d, w, w, ac)
        for rx in (w * 0.14, w * 0.86):
            rivet(d, rx, w * 0.16)
            rivet(d, rx, w * 0.86)
    elif name == "rotary-drill":
        rect(d, [w * 0.3, w * 0.3, w * 0.7, w * 0.7], GREY_D, r=3)
        for rx in (w * 0.18, w * 0.82):
            for ry in (w * 0.18, w * 0.82):
                rivet(d, rx, ry)
    elif name == "electrolysis-plant":
        for i, fx in enumerate([0.3, 0.5, 0.7]):
            px = w * fx
            rect(d, [px - 3, w * 0.24, px + 3, w * 0.76],
                 ac if i % 2 == 0 else shade(ac, 1.3))
        d.line([w * 0.3, w * 0.34, w * 0.7, w * 0.62], fill=shade(ac, 1.6), width=2)
    elif name == "chemical-processor":
        rect(d, [w * 0.22, w * 0.24, w * 0.5, w * 0.52], ac, r=3)
        d.polygon([(w * 0.6, w * 0.52), (w * 0.78, w * 0.52), (w * 0.69, w * 0.34)],
                  fill=shade(ac, 0.85))
        d.line([w * 0.5, w * 0.38, w * 0.6, w * 0.44], fill=GREY_D, width=2)
    elif name == "centrifuge":
        d.ellipse([w * 0.22, w * 0.22, w * 0.78, w * 0.78], fill=GREY_D, outline=OUT)
        d.ellipse([w * 0.34, w * 0.34, w * 0.66, w * 0.66], fill=ac, outline=OUT)
        for ang in (30, 150, 270):
            ax = math.cos(math.radians(ang)) * w * 0.28
            ay = math.sin(math.radians(ang)) * w * 0.28
            d.line([cx, cx, cx + ax, cx + ay], fill=shade(ac, 1.5), width=3)
    elif name == "nuclear-reactor":
        ring = w * 0.34
        d.ellipse([cx - ring, cx - ring, cx + ring, cx + ring], fill=GREY_D, outline=OUT)
        core = w * 0.2
        d.ellipse([cx - core, cx - core, cx + core, cx + core], fill=ac, outline=OUT)
        ci = core * 0.5
        d.ellipse([cx - ci, cx - ci, cx + ci, cx + ci], fill=shade(ac, 1.8))
    elif name == "coal-generator":
        rect(d, [w * 0.2, w * 0.2, w * 0.8, w * 0.58], GREY_D, r=3)
        flame = [(cx, w * 0.2), (cx + w * 0.13, w * 0.4), (cx + w * 0.06, w * 0.56),
                 (cx - w * 0.06, w * 0.56), (cx - w * 0.13, w * 0.4)]
        poly(d, flame, ac)
        poly(d, [(cx, w * 0.3), (cx + w * 0.06, w * 0.44), (cx - w * 0.06, w * 0.44)],
             shade(ac, 1.6))
        rect(d, [w * 0.26, w * 0.66, w * 0.74, w * 0.78], GREY_D)
    elif name == "battery-cell":
        bw = w * 0.5
        x0, y0 = cx - bw / 2, w * 0.24
        rect(d, [x0, y0, x0 + bw, y0 + w * 0.52], ac, r=2)
        rect(d, [x0 + 3, y0 + w * 0.12, x0 + bw - 3, y0 + w * 0.2], shade(ac, 1.5),
             line=None, lw=0)
        rect(d, [x0 - 4, cx - 4, x0, cx + 4], GREY_L)
        rect(d, [x0 + bw, cx - 4, x0 + bw + 4, cx + 4], GREY_D)
    elif name == "recycler":
        d.ellipse([w * 0.24, w * 0.24, w * 0.76, w * 0.76], fill=GREY_D, outline=OUT)
        rr = w * 0.24
        for start in (210, 330, 90):
            pts = [(cx + math.cos(math.radians(start + t)) * rr,
                    cx + math.sin(math.radians(start + t)) * rr) for t in range(0, 61, 12)]
            d.line(pts, fill=ac, width=3)
            ex, ey = pts[-1]
            a = math.atan2(ey - pts[-2][1], ex - pts[-2][0])
            d.polygon([(ex + math.cos(a) * 5, ey + math.sin(a) * 5),
                       (ex + math.cos(a + 2.5) * 5, ey + math.sin(a + 2.5) * 5),
                       (ex + math.cos(a - 2.5) * 5, ey + math.sin(a - 2.5) * 5)], fill=ac)
    elif name in ("neutralizer", "filter-press"):
        if name == "neutralizer":
            d.ellipse([w * 0.26, w * 0.26, w * 0.74, w * 0.74], fill=GREY_D, outline=OUT)
            for i in range(3):
                yy = cx - 6 + i * 6
                pts = [(w * 0.32 + k * (w * 0.36 / 8), yy + math.sin(k * 1.3) * 2)
                       for k in range(9)]
                d.line(pts, fill=shade(ac, 1 + i * 0.2), width=2)
        else:
            for i, fy in enumerate([0.26, 0.44, 0.62]):
                rect(d, [w * 0.24, w * fy, w * 0.76, w * fy + w * 0.1],
                     ac if i != 1 else shade(ac, 1.25))
            d.line([cx, w * 0.16, cx, w * 0.84], fill=OUT, width=1)
    elif name == "acid-plant":
        d.ellipse([w * 0.18, w * 0.24, w * 0.58, w * 0.64], fill=ac, outline=OUT)
        d.ellipse([w * 0.24, w * 0.3, w * 0.52, w * 0.58], fill=shade(ac, 1.4))
        rect(d, [w * 0.62, w * 0.2, w * 0.8, w * 0.8], GREY_D, r=2)
        d.line([w * 0.58, w * 0.44, w * 0.62, w * 0.44], fill=OUT, width=2)
        rect(d, [w * 0.66, w * 0.28, w * 0.76, w * 0.4], shade(ac, 1.2), line=None, lw=0)
    elif name == "resource-refinery":
        rect(d, [w * 0.16, w * 0.3, w * 0.32, w * 0.82], shade(ac, 0.8))
        rect(d, [w * 0.4, w * 0.18, w * 0.56, w * 0.82], GREY_D)
        rect(d, [w * 0.44, w * 0.26, w * 0.52, w * 0.74], ac)
        rect(d, [w * 0.64, w * 0.4, w * 0.82, w * 0.82], shade(ac, 1.2))
        d.line([w * 0.32, w * 0.5, w * 0.4, w * 0.5], fill=OUT, width=2)
        d.line([w * 0.56, w * 0.5, w * 0.64, w * 0.5], fill=OUT, width=2)
        rect(d, [w * 0.14, w * 0.84, w * 0.84, w * 0.88], GREY_D, line=None, lw=0)
    elif name in ("steel-container", "steel-vault"):
        inset = w * 0.14
        rect(d, [inset, inset, w - inset, w - inset], shade(hx("8f9aa6"), 0.85), r=3)
        d.line([inset + 2, inset + 2, w - inset - 2, inset + 2],
               fill=shade(hx("8f9aa6"), 1.2), width=2)
        for i in range(1, 3):
            yy = inset + (w - 2 * inset) * i / 3
            d.line([inset + 2, yy, w - inset - 2, yy], fill=GREY_D, width=2)
        rivet(d, w * 0.5, w * 0.5, GREY_L)
    elif name == "supply-unloader":
        d.ellipse([w * 0.22, w * 0.22, w * 0.78, w * 0.78], fill=GREY_D, outline=OUT)
        d.ellipse([w * 0.36, w * 0.36, w * 0.64, w * 0.64], fill=ac, outline=OUT)
        d.ellipse([w * 0.45, w * 0.45, w * 0.55, w * 0.55], fill=shade(ac, 1.7))
    return img


def turret_gun(name, size):
    w = size * S
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    acc = hx(BLOCK_ACCENTS_TURRET[name])
    dark = shade(acc, 0.6)
    if name == "bronze-gun":
        rect(d, [cx - 5, 2, cx + 5, 16], dark, r=1)
        rect(d, [cx - 3, 2, cx - 1, 14], shade(acc, 1.3), line=None, lw=0)
        rect(d, [cx - 7, 14, cx + 7, 27], acc, r=2)
        d.line([cx - 7, 16, cx + 7, 16], fill=shade(acc, 1.3), width=1)
        rivet(d, cx - 4, 24, GREY_L)
        rivet(d, cx + 4, 24, GREY_L)
    elif name == "steel-howitzer":
        rect(d, [cx - 7, 2, cx + 7, 12], dark, r=1)
        rect(d, [cx - 4, 8, cx + 4, 34], acc, r=1)
        d.line([cx - 4, 12, cx + 4, 12], fill=shade(acc, 1.3), width=2)
        rect(d, [cx - 14, 30, cx + 14, 56], shade(acc, 0.85), r=3)
        rect(d, [cx - 14, 34, cx + 14, 37], shade(acc, 1.25), line=None, lw=0)
        for rx in (cx - 10, cx + 10):
            rivet(d, rx, 48)
            rivet(d, rx, 40)
    elif name == "aluminum-flak":
        for off in (-6, 6):
            rect(d, [cx + off - 2, 4, cx + off + 2, 26], shade(acc, 0.75), r=1)
            rect(d, [cx + off - 1, 4, cx + off + 1, 8], shade(acc, 1.4), line=None, lw=0)
        d.ellipse([cx - 12, 22, cx + 12, 48], fill=acc, outline=OUT, width=1)
        d.ellipse([cx - 6, 28, cx + 6, 42], fill=shade(acc, 1.25), outline=OUT, width=1)
        d.ellipse([cx - 2, 32, cx + 2, 38], fill=shade(acc, 1.7))
    elif name == "uranium-lance":
        rect(d, [cx - 10, 4, cx - 7, 58], dark)
        rect(d, [cx + 7, 4, cx + 10, 58], dark)
        rect(d, [cx - 4, 2, cx + 4, 60], acc, r=1)
        rect(d, [cx - 1, 4, cx + 1, 58], shade(acc, 1.8), line=None, lw=0)
        rect(d, [cx - 14, 54, cx + 14, 82], shade(acc, 0.8), r=3)
        d.ellipse([cx - 6, 62, cx + 6, 74], fill=shade(acc, 1.6), outline=OUT, width=1)
        for rx in (cx - 10, cx + 10):
            rivet(d, rx, 68)
            rivet(d, rx, 78)
    return img


BLOCK_ACCENTS = {
    "rotary-drill": "a2734d",
    "copper-smelter": "daa520",
    "blast-furnace": "c96a2a",
    "alloy-furnace": "cd7f32",
    "electrolysis-plant": "4dd0e1",
    "chemical-processor": "7cb342",
    "centrifuge": "50c878",
    "nuclear-reactor": "50c878",
    "coal-generator": "ff8f3d",
    "battery-cell": "ffd54f",
    "recycler": "9ccc65",
    "neutralizer": "90caf9",
    "filter-press": "8bc34a",
    "cement-kiln": "e0c9a6",
    "acid-plant": "d9c25f",
    "resource-refinery": "45e07a",
    "steel-container": "8f9aa6",
    "steel-vault": "8f9aa6",
    "supply-unloader": "4dd0e1",
}

BLOCK_ACCENTS_TURRET = {
    "bronze-gun": "cd7f32",
    "steel-howitzer": "8f9aa6",
    "aluminum-flak": "dfe5ea",
    "uranium-lance": "45e07a",
}

TURRET_SIZES = {"bronze-gun": 1, "steel-howitzer": 2, "aluminum-flak": 2,
                "uranium-lance": 3}

MACHINE_SIZES = {
    "rotary-drill": 2, "copper-smelter": 2, "blast-furnace": 3, "alloy-furnace": 2,
    "electrolysis-plant": 2, "chemical-processor": 2, "centrifuge": 3,
    "nuclear-reactor": 3, "coal-generator": 2, "battery-cell": 1, "recycler": 2,
    "neutralizer": 2, "filter-press": 2, "cement-kiln": 2, "unit-factory": 3,
    "acid-plant": 2, "resource-refinery": 3,
    "steel-container": 2, "steel-vault": 3, "supply-unloader": 1,
}

WALLS = {"cement-wall": "bfbdb6", "bronze-wall": "cd7f32", "steel-wall": "8f9aa6",
         "steel-wall-large": "8f9aa6", "aluminum-wall": "dfe5ea"}
WALL_SIZES = {"cement-wall": 1, "bronze-wall": 1, "steel-wall": 1,
              "steel-wall-large": 2, "aluminum-wall": 1}


def wall_sprite(name):
    size = WALL_SIZES[name]
    w = size * S
    base = hx(WALLS[name])
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    rect(d, [1, 1, w - 1, w - 1], base)
    d.line([2, 2, w - 2, 2], fill=shade(base, 1.35), width=2)
    d.line([2, 2, 2, w - 2], fill=shade(base, 1.15), width=2)
    d.line([2, w - 3, w - 2, w - 3], fill=shade(base, 0.68), width=2)
    d.line([w - 3, 2, w - 3, w - 2], fill=shade(base, 0.68), width=2)
    inset = 7
    rect(d, [inset, inset, w - inset, w - inset], shade(base, 0.92))
    d.line([inset + 1, inset + 1, w - inset - 1, inset + 1], fill=shade(base, 1.1),
           width=1)
    for rx, ry in [(5, 5), (w - 5, 5), (5, w - 5), (w - 5, w - 5)]:
        rivet(d, rx, ry, shade(base, 1.3))
    if name == "aluminum-wall":
        d.line([inset + 2, w // 2, w - inset - 2, w // 2], fill=shade(base, 1.25),
               width=2)
    if name == "cement-wall":
        d.line([w // 2, inset + 1, w // 2, w - inset - 1], fill=shade(base, 0.75),
               width=1)
    return img


def core_sprite(size, accent_hex):
    w = size * S
    base = hx("6a6d71")
    acc = hx(accent_hex)
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    rect(d, [2, 2, w - 2, w - 2], shade(base, 0.85), r=8)
    d.line([4, 4, w - 4, 4], fill=shade(base, 1.2), width=3)
    r1 = w * 0.36
    d.regular_polygon((cx, cx, r1), 6, rotation=30, fill=shade(base, 1.05),
                      outline=OUT)
    r2 = w * 0.24
    d.regular_polygon((cx, cx, r2), 6, rotation=30, fill=shade(base, 1.25), outline=OUT)
    ring = w * 0.13
    d.ellipse([cx - ring, cx - ring, cx + ring, cx + ring], fill=acc, outline=OUT)
    ri = ring * 0.5
    d.ellipse([cx - ri, cx - ri, cx + ri, cx + ri], fill=shade(acc, 1.6))
    for rx, ry in [(w * 0.12, w * 0.12), (w - w * 0.12, w * 0.12),
                   (w * 0.12, w - w * 0.12), (w - w * 0.12, w - w * 0.12)]:
        rivet(d, rx, ry, GREY_L)
    return img


def unit_factory_sprite():
    size = 3
    w = size * S
    img, d = machine_plate(size, "8f9aa6", r=5)
    cx = w / 2
    d.ellipse([w * 0.22, w * 0.22, w * 0.78, w * 0.78], fill=GREY_D, outline=OUT)
    d.ellipse([w * 0.3, w * 0.3, w * 0.7, w * 0.7], fill=GREY, outline=OUT)
    d.ellipse([w * 0.42, w * 0.42, w * 0.58, w * 0.58], fill=shade(hx("8f9aa6"), 1.2),
              outline=OUT)
    for rx, ry in [(w * 0.12, w * 0.12), (w - w * 0.12, w * 0.12),
                   (w * 0.12, w - w * 0.12), (w - w * 0.12, w - w * 0.12)]:
        rect(d, [rx - 4, ry - 4, rx + 4, ry + 4], GREY_D, r=1)
    return img


def drill_rotator():
    w = 2 * S
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    r = w * 0.3
    ac = hx(BLOCK_ACCENTS["rotary-drill"])
    d.ellipse([cx - r, cx - r, cx + r, cx + r], fill=shade(ac, 0.7), outline=OUT)
    for i in range(4):
        a = math.radians(i * 90 + 45)
        d.line([cx + math.cos(a) * r * 0.25, cx + math.sin(a) * r * 0.25,
                cx + math.cos(a) * r * 0.85, cx + math.sin(a) * r * 0.85],
               fill=shade(ac, 1.3), width=3)
    d.ellipse([cx - r * 0.22, cx - r * 0.22, cx + r * 0.22, cx + r * 0.22],
              fill=shade(ac, 1.1), outline=OUT)
    return img


UNITS = {
    "bronze-crawler": {"size": 48, "color": "cd7f32", "leg": 24},
    "aluminum-wasp": {"size": 48, "color": "dfe5ea", "leg": 0},
    "steel-brawler": {"size": 64, "color": "8f9aa6", "leg": 28},
}


def unit_body(name):
    u = UNITS[name]
    w = u["size"]
    base = hx(u["color"])
    img = img_new(w, w)
    d = ImageDraw.Draw(img)
    cx = w / 2
    if name == "bronze-crawler":
        rect(d, [cx - 10, cx - 12, cx + 10, cx + 12], base, r=4)
        rect(d, [cx - 6, cx - 9, cx + 6, cx - 4], shade(base, 1.3), line=None, lw=0)
        d.ellipse([cx - 3, cx + 1, cx + 3, cx + 7], fill=shade(base, 1.6), outline=OUT)
        rect(d, [cx - 2, cx - 18, cx + 2, cx - 10], shade(base, 0.7), r=1)
    elif name == "aluminum-wasp":
        poly(d, [(cx, 4), (cx + 9, cx - 2), (cx + 6, cx + 12), (cx - 6, cx + 12),
                 (cx - 9, cx - 2)], base)
        poly(d, [(cx, 6), (cx + 4, cx - 4), (cx - 4, cx - 4)], shade(base, 1.3),
             line=None, lw=0)
        d.ellipse([cx - 3, cx - 4, cx + 3, cx + 2], fill=shade(base, 0.6), outline=OUT)
        d.ellipse([cx - 2, cx + 12, cx + 2, cx + 16], fill=shade(hx("4dd0e1"), 1.3))
    else:
        rect(d, [cx - 14, cx - 12, cx + 14, cx + 14], base, r=5)
        rect(d, [cx - 19, cx - 6, cx - 12, cx + 6], shade(base, 0.75), r=2)
        rect(d, [cx + 12, cx - 6, cx + 19, cx + 6], shade(base, 0.75), r=2)
        rect(d, [cx - 9, cx - 9, cx + 9, cx - 3], shade(base, 1.3), line=None, lw=0)
        d.ellipse([cx - 4, cx + 1, cx + 4, cx + 9], fill=shade(base, 1.55), outline=OUT)
        rect(d, [cx - 3, cx - 20, cx + 3, cx - 10], shade(base, 0.7), r=1)
        rect(d, [cx - 14, cx - 20, cx - 9, cx - 12], shade(base, 0.7), r=1)
        rect(d, [cx + 9, cx - 20, cx + 14, cx - 12], shade(base, 0.7), r=1)
    return img


def unit_leg(size):
    img = img_new(size, size)
    d = ImageDraw.Draw(img)
    base = hx("5a5a5c")
    d.line([2, size - 2, size - 4, 2], fill=base, width=max(3, size // 5))
    d.line([3, size - 3, size - 5, 3], fill=shade(base, 1.3),
           width=max(1, size // 8))
    d.ellipse([size - 6, 0, size - 1, 5], fill=shade(base, 0.8), outline=OUT)
    return img


def unit_joint(size):
    img = img_new(size, size)
    d = ImageDraw.Draw(img)
    c = size // 2
    d.ellipse([1, 1, size - 1, size - 1], fill=hx("6a6a6c"), outline=OUT)
    d.ellipse([c - 2, c - 2, c + 1, c + 1], fill=shade(hx("6a6a6c"), 1.4))
    return img


def unit_outline(src):
    px = src.load()
    w, h = src.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 40:
                op[x, y] = OUT
    return out


ORE_STONE = (79, 79, 77, 255)


def ore_tile(seed, item_hex):
    rng = random.Random(seed)
    img = img_new()
    d = ImageDraw.Draw(img)
    for _ in range(5):
        x, y = rng.randrange(2, 29), rng.randrange(2, 29)
        s = rng.choice((1, 2))
        d.rectangle([x, y, x + s, y + s], fill=shade(ORE_STONE, rng.uniform(0.85, 1.2)))
    mineral = hx(item_hex)
    for _ in range(4):
        x, y = rng.randrange(5, 23), rng.randrange(5, 23)
        for _ in range(rng.randint(3, 5)):
            ox, oy = x + rng.randint(-4, 4), y + rng.randint(-4, 4)
            s = rng.choice((1, 2))
            f = rng.uniform(0.8, 1.2)
            c = shade(mineral, f)
            d.rectangle([ox, oy, ox + s, oy + s], fill=c)
            if rng.random() < 0.4:
                d.point([(ox + s, oy)], fill=OUT)
    return img


def main():
    import os
    count = 0
    for name, fn in ITEMS.items():
        fn().save(f"{ROOT}/items/{name}.png")
        count += 1
    os.makedirs(f"{ROOT}/liquids", exist_ok=True)
    for name, hexs in LIQUIDS.items():
        liquid_icon(hexs).save(f"{ROOT}/liquids/{name}.png")
        count += 1
    for name, size in MACHINE_SIZES.items():
        if name == "unit-factory":
            unit_factory_sprite().save(f"{ROOT}/blocks/{name}.png")
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
    core_sprite(3, "50c878").save(f"{ROOT}/blocks/core-bastion.png")
    core_sprite(4, "45e07a").save(f"{ROOT}/blocks/core-citadel.png")
    count += 2
    for name, u in UNITS.items():
        body = unit_body(name)
        body.save(f"{ROOT}/units/{name}.png")
        body.save(f"{ROOT}/units/{name}-full.png")
        unit_outline(body).save(f"{ROOT}/units/{name}-outline.png")
        count += 3
        if u["leg"]:
            unit_leg(u["leg"]).save(f"{ROOT}/units/{name}-leg.png")
            unit_joint(14).save(f"{ROOT}/units/{name}-joint.png")
            count += 2
    ores = ["bauxite", "hematite", "chalcopyrite", "cassiterite", "galena",
            "uraninite", "quartz", "graphite", "limestone", "beryl"]
    colors = {"bauxite": "d4a373", "hematite": "8b4513", "chalcopyrite": "daa520",
              "cassiterite": "c0c0c0", "galena": "708090", "uraninite": "50c878",
              "quartz": "f5f5dc", "graphite": "565656", "limestone": "e8d5b7",
              "beryl": "90ee90"}
    os.makedirs(f"{ROOT}/units", exist_ok=True)
    for ore in ores:
        for v in (1, 2):
            ore_tile(hash((ore, v)) & 0xFFFF, colors[ore]).save(
                f"{ROOT}/blocks/ore-{ore}{v}.png")
            count += 1
    print(f"generated {count} sprites")


if __name__ == "__main__":
    main()
