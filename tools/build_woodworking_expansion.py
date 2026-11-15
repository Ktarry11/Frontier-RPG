#!/usr/bin/env python3
"""Woodworking expansion: the trade's top half, its missing lines, and the kits and parts behind them.

    PYTHONPATH=. python3 tools/build_woodworking_expansion.py          # write recipes, materials, icons
    PYTHONPATH=. python3 tools/build_crafted_gear.py                   # then author the items' stats
    PYTHONPATH=. python3 tools/build_recipe_vendors.py                 # then stock the vendor patterns

Kyle, 15 Nov 2026: "Massively expand out wood working." And straight after: "we don't want it flooded with
garbage things that make no sense. The crafted items need to be logical and not full of drip stats. Most
staves should have spell power or healing power but ALSO don't forget.....Beetle tanks and bear tanks
(venomancer and druids) can use staves....so agi staves and tank staves are real".

WHAT WAS WRONG (the audit, before this ran)
  - From skill 150 every wood had two or three pieces, and fourteen woods carried 43 items between them.
    The Stormoak caster had a staff and a wand and no off-hand; the Moonpetal healer had no off-hand at all.
  - Four planks (Emberwood, Frostheart, Ebonthorn, Sunheart) were cut and sawn and made into nothing.
  - Every staff was a caster's. Bear druids and Venomancer beetles tank with a staff and had none.
  - Spears were all Agility. Warriors, Barbarians, Reapers (a polearm is all a Reaper can use) and
    Knights of Xoroth had one strength polearm, at skill 178.
  - Wooden shields stopped at skill 125. No totems, idols or librams were made by anyone.
  - Two upgrade kits (Ashwood, Ironbark) for sixteen woods: a Felbark or Moonpetal piece could never be
    upgraded.
  - Bow and crossbow attachments stopped at skill 140 (+11 damage), as did the engineer's scopes.
  - Arrows and bolts stopped at level 30 (fixed earlier the same day; their reagents are re-tiered here).

WHAT THIS ADDS. Every piece's role comes from its WOOD or its NAMED LINE (tools/build_crafted_gear.py
WOODS, WOOD_LINES, WOOD_RELIC_LINES), and its stats from that file's identities: a caster's staff leads
with spell power, a healer's with healing, a Stalker's staff with attack power, a Barkguard staff with
Stamina. Nothing here is a random roll and nothing is a stat dribble (the gear builder's audit fails one).

Reagents follow tools/tier_crafting_reagents.py's ladders (a stick for every shaft, glue or resin for every
bond) and the fibre and page ladders by the skill each is made at, so nothing asks for a reagent the
woodworker can't make yet. Woods follow the trade's existing order (Silverbark at 150 ... Stormoak at 290),
with the four new woods placed where their planks are cut.

Idempotent: it rewrites only the recipes and materials it owns (ids starting "wwx_", the kits and the parts).
"""
import colorsys
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "data/crafting/recipes.json"
MATERIALS = ROOT / "data/gathering/materials.json"
CONSUMABLES = ROOT / "data/consumables/consumable_types.json"
NODES = ROOT / "assets/gathering_nodes"

#: piece kind -> (slot, weapon_type, armour_type, plank count, takes a stick, takes fibre, takes pages)
KINDS = {
    "staff": ("main_hand", "staff", None, 8, True, False, False),
    "wand": ("ranged", "wand", None, 5, True, False, False),
    "tome": ("off_hand", "tome", None, 4, False, False, True),
    "bow": ("ranged", "bow", None, 7, True, True, False),
    "crossbow": ("ranged", "crossbow", None, 7, True, True, False),
    "polearm": ("main_hand", "polearm", None, 8, True, False, False),
    "shield": ("off_hand", "shield", None, 7, False, True, False),
    "totem": ("ranged", "totem", None, 4, False, True, False),
    "idol": ("ranged", "idol", None, 4, False, True, False),
    "libram": ("ranged", "libram", None, 3, False, False, True),
    "trinket": ("trinket", None, "accessory", 3, False, True, False),
    "head": ("head", None, None, 5, False, True, False),
}

#: template the reference item is generated with (the gear builder re-derives it from the identity)
TEMPLATE = {"staff": "int_caster", "wand": "int_caster", "tome": "int_caster", "bow": "agi_physical",
            "crossbow": "agi_physical", "polearm": "agi_physical", "shield": None, "totem": "int_caster",
            "idol": "int_caster", "libram": "int_caster", "trinket": "int_caster", "head": "agi_physical"}

# (id, name, skill, kind, wood, rarity, source)
PIECES = [
    # ---- casting weapons: every wood gets the staff, wand and off-hand its school deserves
    ("silverbark_wand", "Silverbark Wand", 152, "wand", "silverbark", "uncommon", "trainer"),
    ("silverbark_codex", "Silverbark Codex", 158, "tome", "silverbark", "uncommon", "trainer"),
    ("goldenleaf_codex", "Goldenleaf Codex", 168, "tome", "goldenleaf", "uncommon", "trainer"),
    ("sapglow_wand", "Sapglow Wand", 175, "wand", "sapglow", "uncommon", "trainer"),
    ("redbark_wand", "Redbark Wand", 181, "wand", "redbark", "uncommon", "vendor"),
    ("redbark_codex", "Redbark Codex", 186, "tome", "redbark", "rare", "drop"),
    ("marshwillow_wand", "Marshwillow Wand", 199, "wand", "marshwillow", "uncommon", "trainer"),
    ("marshwillow_codex", "Marshwillow Codex", 204, "tome", "marshwillow", "rare", "vendor"),
    ("bloodwood_codex", "Bloodwood Codex", 218, "tome", "bloodwood", "rare", "trainer"),
    ("felbark_wand", "Felbark Wand", 228, "wand", "felbark", "rare", "trainer"),
    ("felbark_staff", "Felbark Staff", 232, "staff", "felbark", "rare", "vendor"),
    ("moonpetal_codex", "Moonpetal Codex", 248, "tome", "moonpetal", "rare", "trainer"),
    ("emberwood_greatstaff", "Emberwood Greatstaff", 252, "staff", "emberwood", "rare", "trainer"),
    ("emberwood_wand", "Emberwood Wand", 255, "wand", "emberwood", "rare", "trainer"),
    ("emberwood_codex", "Emberwood Codex", 258, "tome", "emberwood", "rare", "vendor"),
    ("frostheart_staff", "Frostheart Staff", 262, "staff", "frostheart", "rare", "trainer"),
    ("frostheart_wand", "Frostheart Wand", 264, "wand", "frostheart", "rare", "trainer"),
    ("frostheart_codex", "Frostheart Codex", 267, "tome", "frostheart", "rare", "drop"),
    ("ebonthorn_staff", "Ebonthorn Staff", 272, "staff", "ebonthorn", "rare", "trainer"),
    ("ebonthorn_wand", "Ebonthorn Wand", 274, "wand", "ebonthorn", "rare", "trainer"),
    ("ebonthorn_codex", "Ebonthorn Codex", 277, "tome", "ebonthorn", "rare", "vendor"),
    ("starleaf_staff", "Starleaf Staff", 280, "staff", "starleaf", "rare", "trainer"),
    ("starleaf_wand", "Starleaf Wand", 282, "wand", "starleaf", "rare", "drop"),
    ("stormoak_codex", "Stormoak Codex", 292, "tome", "stormoak", "rare", "trainer"),
    ("sunheart_staff", "Sunheart Staff", 300, "staff", "sunheart", "epic", "drop"),
    ("blessed_sunheart_staff", "Blessed Sunheart Staff", 300, "staff", "sunheart", "epic", "drop"),
    ("blessed_sunheart_codex", "Blessed Sunheart Codex", 300, "tome", "sunheart", "rare", "trainer"),

    # ---- staves for fighters: Stalker's (cat druid, hunter) and Barkguard (bear druid, Venomancer beetle)
    ("ironbark_prowlers_staff", "Ironbark Prowler's Staff", 95, "staff", "ironbark", "uncommon", "trainer"),
    ("ironbark_barkguard_staff", "Ironbark Barkguard Staff", 100, "staff", "ironbark", "uncommon", "trainer"),
    ("silverbark_prowlers_staff", "Silverbark Prowler's Staff", 150, "staff", "silverbark", "uncommon", "trainer"),
    ("silverbark_barkguard_staff", "Silverbark Barkguard Staff", 155, "staff", "silverbark", "rare", "vendor"),
    ("bloodroot_stalkers_staff", "Bloodroot Stalker's Staff", 195, "staff", "bloodroot", "rare", "trainer"),
    ("bloodroot_barkguard_staff", "Bloodroot Barkguard Staff", 200, "staff", "bloodroot", "rare", "trainer"),
    ("emberwood_stalkers_staff", "Emberwood Stalker's Staff", 250, "staff", "emberwood", "rare", "drop"),
    ("emberwood_barkguard_staff", "Emberwood Barkguard Staff", 254, "staff", "emberwood", "rare", "trainer"),
    ("stormoak_stalkers_staff", "Stormoak Stalker's Staff", 290, "staff", "stormoak", "rare", "trainer"),
    ("stormoak_barkguard_staff", "Stormoak Barkguard Staff", 295, "staff", "stormoak", "epic", "drop"),

    # ---- bows, crossbows and spears the hunter ladder skipped
    ("duskwood_crossbow", "Duskwood Crossbow", 185, "crossbow", "duskwood", "uncommon", "trainer"),
    ("felbark_bow", "Felbark Longbow", 238, "bow", "felbark", "rare", "trainer"),
    ("emberwood_crossbow", "Emberwood Crossbow", 259, "crossbow", "emberwood", "rare", "trainer"),
    ("frostheart_bow", "Frostheart Longbow", 268, "bow", "frostheart", "rare", "trainer"),
    ("ebonthorn_spear", "Ebonthorn Spear", 278, "polearm", "ebonthorn", "rare", "drop"),
    ("starleaf_bow", "Starleaf Longbow", 284, "bow", "starleaf", "rare", "vendor"),
    ("stormoak_crossbow", "Stormoak Crossbow", 295, "crossbow", "stormoak", "epic", "drop"),
    ("sunheart_bow", "Sunheart Longbow", 300, "bow", "sunheart", "epic", "drop"),

    # ---- strength polearms (Warpike) and a paladin's (Warden's)
    ("ironbark_warpike", "Ironbark Warpike", 120, "polearm", "ironbark", "uncommon", "trainer"),
    ("redbark_warpike", "Redbark Warpike", 178, "polearm", "redbark", "uncommon", "trainer"),
    ("bloodwood_wardens_glaive", "Bloodwood Warden's Glaive", 210, "polearm", "bloodwood", "rare", "trainer"),
    ("felbark_warpike", "Felbark Warpike", 230, "polearm", "felbark", "rare", "trainer"),
    ("starleaf_wardens_glaive", "Starleaf Warden's Glaive", 282, "polearm", "starleaf", "rare", "drop"),
    ("stormoak_warpike", "Stormoak Warpike", 288, "polearm", "stormoak", "rare", "vendor"),

    # ---- shields for the shaman-shaped classes: healer (Tideguard) and elemental (Thundershield)
    ("goldenleaf_tideguard", "Goldenleaf Tideguard", 165, "shield", "goldenleaf", "uncommon", "trainer"),
    ("thornveil_tideguard", "Thornveil Tideguard", 188, "shield", "thornveil", "rare", "vendor"),
    ("marshwillow_thundershield", "Marshwillow Thundershield", 200, "shield", "marshwillow", "rare", "trainer"),
    ("moonpetal_tideguard", "Moonpetal Tideguard", 242, "shield", "moonpetal", "rare", "trainer"),
    ("emberwood_thundershield", "Emberwood Thundershield", 256, "shield", "emberwood", "rare", "drop"),
    ("stormoak_thundershield", "Stormoak Thundershield", 290, "shield", "stormoak", "rare", "trainer"),
    ("sunheart_tideguard", "Sunheart Tideguard", 300, "shield", "sunheart", "epic", "drop"),

    # ---- relics: two of each role, mid-30s and mid-50s
    ("goldenleaf_tide_totem", "Goldenleaf Tide Totem", 165, "totem", "goldenleaf", "uncommon", "trainer"),
    ("sapglow_storm_totem", "Sapglow Storm Totem", 172, "totem", "sapglow", "uncommon", "trainer"),
    ("redbark_earthshaker_totem", "Redbark Earthshaker Totem", 180, "totem", "redbark", "uncommon", "trainer"),
    ("frostheart_tide_totem", "Frostheart Tide Totem", 266, "totem", "frostheart", "rare", "vendor"),
    ("ebonthorn_earthshaker_totem", "Ebonthorn Earthshaker Totem", 274, "totem", "ebonthorn", "rare", "drop"),
    ("stormoak_storm_totem", "Stormoak Storm Totem", 290, "totem", "stormoak", "rare", "trainer"),
    ("goldenleaf_grove_idol", "Goldenleaf Grove Idol", 168, "idol", "goldenleaf", "uncommon", "trainer"),
    ("nightshade_moon_idol", "Nightshade Moon Idol", 172, "idol", "nightshade", "uncommon", "trainer"),
    ("thornveil_claw_idol", "Thornveil Claw Idol", 185, "idol", "thornveil", "uncommon", "trainer"),
    ("bloodroot_barkguard_idol", "Bloodroot Barkguard Idol", 198, "idol", "bloodroot", "rare", "vendor"),
    ("moonpetal_grove_idol", "Moonpetal Grove Idol", 246, "idol", "moonpetal", "rare", "trainer"),
    ("frostheart_claw_idol", "Frostheart Claw Idol", 262, "idol", "frostheart", "rare", "drop"),
    ("ebonthorn_barkguard_idol", "Ebonthorn Barkguard Idol", 270, "idol", "ebonthorn", "rare", "trainer"),
    ("starleaf_moon_idol", "Starleaf Moon Idol", 278, "idol", "starleaf", "rare", "vendor"),
    ("goldenleaf_libram_of_mercy", "Goldenleaf Libram of Mercy", 170, "libram", "goldenleaf", "uncommon", "trainer"),
    ("redbark_libram_of_zeal", "Redbark Libram of Zeal", 182, "libram", "redbark", "uncommon", "trainer"),
    ("bloodroot_libram_of_the_bulwark", "Bloodroot Libram of the Bulwark", 196, "libram", "bloodroot", "rare", "vendor"),
    ("moonpetal_libram_of_mercy", "Moonpetal Libram of Mercy", 250, "libram", "moonpetal", "rare", "trainer"),
    ("ebonthorn_libram_of_the_bulwark", "Ebonthorn Libram of the Bulwark", 272, "libram", "ebonthorn", "rare", "drop"),
    ("stormoak_libram_of_zeal", "Stormoak Libram of Zeal", 286, "libram", "stormoak", "rare", "trainer"),

    # ---- trinkets that do things (tools/build_crafted_gear.py WOOD_PROCS)
    ("carved_hawk_fetish", "Carved Hawk Fetish", 165, "trinket", "sapglow", "rare", "trainer"),
    ("barkguard_ward", "Barkguard Ward", 190, "trinket", "thornveil", "rare", "vendor"),
    ("moonpetal_blossom", "Moonpetal Blossom", 244, "trinket", "moonpetal", "rare", "trainer"),
    ("emberwood_brand", "Emberwood Brand", 254, "trinket", "emberwood", "rare", "drop"),
    ("stormoak_heart", "Stormoak Heart", 292, "trinket", "stormoak", "epic", "drop"),

    # ---- masks and crowns, the druid's and the shaman's
    ("bloodroot_mask", "Bloodroot Mask", 192, "head", "bloodroot", "rare", "trainer"),
    ("felbark_helm", "Felbark Helm", 235, "head", "felbark", "rare", "vendor"),
    ("starleaf_crown", "Starleaf Crown", 276, "head", "starleaf", "rare", "drop"),
]

#: woods with crafted gear and no upgrade kit, and the skill their kit is learned at (just past each
#: wood's first piece). Ashwood and Ironbark already have theirs.
KITS = {"silverbark": 152, "duskwood": 155, "goldenleaf": 168, "nightshade": 168, "sapglow": 174,
        "redbark": 180, "thornveil": 184, "bloodroot": 198, "marshwillow": 198, "bloodwood": 212,
        "felbark": 228, "moonpetal": 244, "emberwood": 254, "frostheart": 264, "starleaf": 265,
        "ebonthorn": 274, "stormoak": 288, "sunheart": 300}

#: bow and crossbow attachments past Heartwood Limbs (+11 at skill 140), sized to keep each at about a
#: fifth of a crafted bow's average hit at its level, as Heartwood is (+11 on ~55)
ATTACH = [  # id, name, skill, damage, wood, extra input, description
    ("limbs_bloodroot", "Bloodroot Limbs", 185, 14, "bloodroot", {"component_string": 1},
     "Recurved limbs of bloodroot. They snap back hard enough to sting the hand."),
    ("pin_moonpetal", "Moonpetal Sight Pin", 230, 17, "moonpetal", {"component_string": 1},
     "A pale moonpetal sight pin. It catches the light on the darkest night."),
    ("nock_starleaf", "Starleaf Nock", 265, 20, "starleaf", {"component_string": 1},
     "A starleaf nock that seats every arrow the same way, every time."),
    ("limbs_stormoak", "Stormoak Limbs", 290, 24, "stormoak", {"component_string": 2},
     "Stormoak limbs, heavy and alive. The draw fights you, and the shot doesn't miss."),
]
#: the engineer's scopes, kept level with the woodworker's parts (crossbows take either)
SCOPES = [  # id, name, skill, damage, inputs, description
    ("scope_mithril", "Mithril Scope", 185, 14, {"part_precision_sight": 1, "bar_mithril": 2},
     "A mithril-bodied scope with a ground lens. Fits a gun or a crossbow."),
    ("scope_thorium", "Thorium Scope", 245, 18, {"part_precision_sight": 1, "part_resonant_core": 1, "bar_thorium": 2},
     "A heavy thorium scope with a resonant crosshair."),
    ("scope_arcanite", "Arcanite Scope", 290, 24, {"part_precision_sight": 1, "crystal_voidglass": 1, "bar_arcanite": 2},
     "Arcanite and voidglass. It sees a little further than it should."),
]


def fibre(skill):
    """The best fibre a woodworker of this skill can twist (fibre recipes: tough to 180, braided 195+,
    corded 260+, warded 290+)."""
    return "fiber_tough" if skill < 195 else "fiber_braided" if skill < 260 else \
        "fiber_corded" if skill < 290 else "fiber_warded"


def pages(skill):
    return "pages_fine" if skill < 205 else "pages_vellum" if skill < 270 else \
        "pages_leafed" if skill < 300 else "pages_gilded"


def stick(skill):
    """tools/tier_crafting_reagents.py's shaft ladder."""
    for cap, sid in ((55, "stick_green"), (115, "stick_seasoned"), (185, "stick_hardened"),
                     (245, "stick_lacquered"), (285, "stick_banded")):
        if skill < cap:
            return sid
    return "stick_ironbound"


def bond(skill):
    return "glue" if skill < 150 else "resin"


def skill_range(s):
    return [s + 5, s + 15, s + 25, s + 35]


def piece_recipe(name, skill, kind, wood, rarity, source):
    slot, wt, arm, planks, takes_stick, takes_fibre, takes_pages = KINDS[kind]
    inputs = {f"plank_{wood}": planks}
    if takes_stick:
        inputs[stick(skill)] = 1
    if takes_fibre:
        inputs[fibre(skill)] = 2 if kind in ("bow", "crossbow", "shield") else 1
    if takes_pages:
        inputs[pages(skill)] = 3 if kind == "libram" else 2
    inputs[bond(skill)] = 1
    out = {"kind": "armor" if kind in ("trinket", "head") else "weapon", "slot": slot}
    if wt:
        out["weapon_type"] = wt
    if arm:
        out["armor_type"] = arm
    out.update(stat_template=TEMPLATE[kind], item_level=skill // 5 + 1, rarity=rarity, material_tier=wood)
    return {"name": name, "inputs": inputs, "skill_required": skill, "output": out,
            "skill_range": skill_range(skill), "source": source}


def plank_rgb(wood):
    from PIL import Image
    im = Image.open(NODES / "planks" / f"plank_{wood}.png").convert("RGBA").resize((24, 24))
    px = [p[:3] for p in im.getdata() if p[3] > 128]
    return tuple(sum(c[i] for c in px) / len(px) for i in range(3))


def tinted(src, rgb, dst):
    """Recolour an icon to a wood: keep each pixel's lightness, take the wood's hue and some of its
    saturation. The same pack art, a different timber."""
    from PIL import Image
    h, _l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    im = Image.open(src).convert("RGBA")
    out = []
    for r, g, b, a in im.getdata():
        _h, l, s0 = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        nr, ng, nb = colorsys.hls_to_rgb(h, l, min(1.0, 0.35 * s0 + 0.65 * s))
        out.append((int(nr * 255), int(ng * 255), int(nb * 255), a))
    im.putdata(out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst)


def main():
    rd = json.loads(RECIPES.read_text(encoding="utf-8"))
    WW = rd["professions"]["woodworking"]["recipes"]
    ENG = rd["professions"]["engineering"]["recipes"]
    md = json.loads(MATERIALS.read_text(encoding="utf-8"))
    M = md.get("materials", md)
    names = {r["name"] for k, r in WW.items() if not k.startswith("wwx_")}

    n_piece = 0
    for pid, name, skill, kind, wood, rarity, source in PIECES:
        assert name not in names, f"{name} already exists"
        WW[f"wwx_{pid}"] = piece_recipe(name, skill, kind, wood, rarity, source)
        n_piece += 1

    # half the kits are taught, half sold as patterns (qa_recipe_sources holds each trade's trainer share at 50-55%)
    for i, (wood, skill) in enumerate(sorted(KITS.items(), key=lambda kv: kv[1])):
        kid = f"upgrade_kit_{wood}"
        label = wood.replace("_", " ").title()
        WW[f"wwx_kit_{wood}"] = {"name": f"{label} Upgrade Kit", "inputs": {f"plank_{wood}": 4, fibre(skill): 2,
                                                                          bond(skill): 1},
                                 "skill_required": skill, "output": {"kind": "material", "material_id": kid},
                                 "skill_range": skill_range(skill), "source": "vendor" if i % 2 else "trainer"}
        M[kid] = {"name": f"{label} Upgrade Kit", "material_type": "upgrade_kit", "profession": "woodworking",
                  "tier": "kit", "description": f"Shaping tools and {label.lower()} inlay, used to refine any "
                  f"{label}-tier crafted item up one rarity rank. Only works on Woodworked {label} gear.",
                  "stack_limit": 20, "sell_price": max(60, skill * 2), "icon_id": kid, "skill_range": None}
        tinted(NODES / "upgrade_kits" / "upgrade_kit_ironbark.png", plank_rgb(wood),
               NODES / "upgrade_kits" / f"{kid}.png")

    base_icon = {"limbs": "limbs_heartwood", "pin": "pin_truesight", "nock": "nock_horn"}
    for aid, name, skill, dmg, wood, extra, desc in ATTACH:
        WW[f"wwx_{aid}"] = {"name": name, "inputs": {f"plank_{wood}": 3, fibre(skill): 2, **extra},
                            "skill_required": skill, "output": {"kind": "material", "material_id": aid},
                            "skill_range": skill_range(skill), "count": 1,
                            "source": "drop" if aid == "limbs_stormoak" else "trainer"}
        M[aid] = {"name": name, "material_type": "part", "profession": "woodworking", "tier": "endgame",
                  "description": f"{desc} Fits a bow or crossbow: +{dmg} weapon damage, permanently.",
                  "stack_limit": 20, "vendor_price": 0, "sell_price": skill // 3, "icon_id": aid, "skill_range": None}
        tinted(NODES / "parts" / f"{base_icon[aid.split('_')[0]]}.png", plank_rgb(wood), NODES / "parts" / f"{aid}.png")
    for sid, name, skill, dmg, inputs, desc in SCOPES:
        ENG[f"engx_{sid}"] = {"name": name, "inputs": inputs, "skill_required": skill,
                              "output": {"kind": "material", "material_id": sid}, "skill_range": skill_range(skill),
                              "count": 1, "source": {"scope_mithril": "trainer", "scope_thorium": "vendor",
                                                     "scope_arcanite": "drop"}[sid]}
        M[sid] = {"name": name, "material_type": "part", "profession": "engineering", "tier": "endgame",
                  "description": f"{desc} +{dmg} weapon damage, permanently.", "stack_limit": 20, "vendor_price": 0,
                  "sell_price": skill // 3, "icon_id": sid, "skill_range": None}
    for sid, src in (("scope_mithril", "scope_precision"), ("scope_thorium", "scope_resonant"),
                     ("scope_arcanite", "scope_resonant")):
        rgb = {"scope_mithril": (150, 175, 205), "scope_thorium": (120, 160, 120), "scope_arcanite": (90, 170, 220)}[sid]
        tinted(NODES / "parts" / f"{src}.png", rgb, NODES / "parts" / f"{sid}.png")

    # arrows and bolts (added earlier on 15 Nov) take the fibre and bond their skill can make
    for rid in ("ww_broadhead_arrows", "ww_quarrel_bolts", "ww_barbed_arrows", "ww_barbed_bolts",
                "ww_starleaf_arrows", "ww_starleaf_bolts"):
        r = WW[rid]
        r["inputs"] = {k: v for k, v in r["inputs"].items() if not k.startswith(("fiber_", "glue", "resin"))}
        r["inputs"][fibre(r["skill_required"])] = 1
        r["inputs"][bond(r["skill_required"])] = 1

    RECIPES.write_text(json.dumps(rd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MATERIALS.write_text(json.dumps(md, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{n_piece} pieces, {len(KITS)} kits, {len(ATTACH)} bow parts, {len(SCOPES)} scopes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
