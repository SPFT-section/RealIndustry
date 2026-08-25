import os

B = "/root/RealIndustry/content/blocks"
L = "/root/RealIndustry/content/liquids"
ST = "/root/RealIndustry/content/status"
os.makedirs(ST, exist_ok=True)


def insert_before(path, anchor, block):
    s = open(path).read()
    if "drawer:" in s or "shootEffect:" in s:
        return
    s = s.replace(anchor, block + anchor, 1)
    open(path, "w").write(s)


def drawer(drawers):
    parts = []
    for t, props in drawers:
        body = "type: %s" % t
        if props:
            body += "\n          " + props.replace("\n          ", "\n          ")
        parts.append("    {\n        " + body + "\n    }")
    return ("drawer: {\n    type: DrawMulti\n    drawers: [\n"
            + "\n".join(parts) + "\n    ]\n}\n\n")


MACHINES = {
    "copper-smelter.hjson": [("DrawDefault", ""), ("DrawFlame",
        "flameColor: \"ff8f3d\""), ("DrawGlowRegion",
        "color: \"ff8f3d\"\n          glowScale: 8\n          glowIntensity: 0.5")],
    "blast-furnace.hjson": [("DrawDefault", ""), ("DrawFlame",
        "flameColor: \"ff8f3d\""), ("DrawGlowRegion",
        "color: \"ff8f3d\"\n          glowScale: 12\n          glowIntensity: 0.7")],
    "alloy-furnace.hjson": [("DrawDefault", ""), ("DrawFlame",
        "flameColor: \"e8a05c\""), ("DrawGlowRegion",
        "color: \"e8a05c\"\n          glowScale: 8\n          glowIntensity: 0.5")],
    "cement-kiln.hjson": [("DrawDefault", ""), ("DrawFlame",
        "flameColor: \"e8a05c\""), ("DrawGlowRegion",
        "color: \"e8a05c\"\n          glowScale: 9\n          glowIntensity: 0.55")],
    "electrolysis-plant.hjson": [("DrawDefault", ""), ("DrawGlowRegion",
        "color: \"5cd8e8\"\n          glowScale: 7\n          glowIntensity: 0.6")],
    "chemical-processor.hjson": [("DrawDefault", ""), ("DrawParticles",
        "color: \"8fce4e\"\n          particles: 12\n          particleSize: 2\n          particleLife: 50")],
    "centrifuge.hjson": [("DrawDefault", ""), ("DrawBlurSpin",
        "suffix: \"-rotator\"\n          rotateSpeed: 2"), ("DrawCircles",
        "color: \"50c878\"\n          amount: 3\n          radius: 10")],
    "nuclear-reactor.hjson": [("DrawDefault", ""), ("DrawGlowRegion",
        "color: \"b088f0\"\n          glowScale: 14\n          glowIntensity: 0.8"),
        ("DrawSpikes",
        "color: \"b088f0\"\n          amount: 6\n          radius: 12\n          length: 5\n          rotateSpeed: 0.5")],
    "coal-generator.hjson": [("DrawDefault", ""), ("DrawGlowRegion",
        "color: \"ffb35c\"\n          glowScale: 9\n          glowIntensity: 0.6")],
    "recycler.hjson": [("DrawDefault", ""), ("DrawBlurSpin",
        "suffix: \"-rotator\"\n          rotateSpeed: 3")],
    "neutralizer.hjson": [("DrawDefault", ""), ("DrawBubbles",
        "color: \"8fc6f0\"\n          amount: 8\n          radius: 6"),
        ("DrawLiquidRegion", "suffix: \"-liquid\"")],
    "filter-press.hjson": [("DrawDefault", ""), ("DrawGlowRegion",
        "color: \"a5d86a\"\n          glowScale: 6\n          glowIntensity: 0.45")],
    "acid-plant.hjson": [("DrawDefault", ""), ("DrawBubbles",
        "color: \"e8cf52\"\n          amount: 10\n          radius: 7"),
        ("DrawLiquidRegion", "suffix: \"-liquid\"")],
    "resource-refinery.hjson": [("DrawDefault", ""), ("DrawBlurSpin",
        "suffix: \"-rotator\"\n          rotateSpeed: 2.5"), ("DrawGlowRegion",
        "color: \"45e07a\"\n          glowScale: 8\n          glowIntensity: 0.55"),
        ("DrawParticles",
        "color: \"45e07a\"\n          particles: 8\n          particleSize: 2")],
}

for fname, drawers in MACHINES.items():
    insert_before(f"{B}/{fname}", "requirements: [",
                  drawer(drawers) + "\n")

insert_before(f"{B}/coal-generator.hjson", "requirements: [",
              "generateEffect: fuelburn\n\n")

TURRETS = {
    "bronze-gun.hjson": ("shootSmall", "shootSmallSmoke", "casing1", 0),
    "steel-howitzer.hjson": ("shootBig", "shootBigSmoke", "casing2", 1),
    "aluminum-flak.hjson": ("shootSmall", "shootSmokeSquare", "casing3", 0),
    "uranium-lance.hjson": ("railShoot", "shootBigSmoke2", "casing4", 2),
}
for fname, (se, sm, ae, shake) in TURRETS.items():
    block = (f"shootEffect: {se}\nsmokeEffect: {sm}\n"
             f"ammoUseEffect: {ae}\n")
    if shake:
        block += f"shake: {shake}\n"
    insert_before(f"{B}/{fname}", "requirements: [", block + "\n")

open(f"{ST}/acid-corrosion.hjson", "w").write(
    """type: StatusEffect
name: กรดกัดกร่อน
description: สัมผัสกับกรดอุตสาหกรรม โครงสร้างถูกกัดกร่อนอย่างต่อเนื่อง
color: "d9c25f"
damage: 0.12
effectChance: 0.25
show: true
""")

open(f"{ST}/irradiated.hjson", "w").write(
    """type: StatusEffect
name: ได้รับรังสี
description: สัมผัสกัมมันตรังสีจากยูเรเนียม อ่อนแรงและเสียหายต่อเนื่อง
color: "45e07a"
damage: 0.2
healthMultiplier: 0.85
speedMultiplier: 0.8
effectChance: 0.2
show: true
""")

for fname, eff in [("sulfuric-acid.hjson", "acid-corrosion"),
                   ("spent-acid.hjson", "acid-corrosion"),
                   ("waste-sludge.hjson", "irradiated")]:
    p = f"{L}/{fname}"
    s = open(p).read().replace("effect: none", f"effect: {eff}")
    open(p, "w").write(s)

print("patched", len(MACHINES), "machines +", len(TURRETS), "turrets + 3 liquids + 2 statuses")
