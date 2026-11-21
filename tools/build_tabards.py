#!/usr/bin/env python3
"""Faction tabards: wear one in a heroic dungeon and the dungeon's kill rep goes to that faction instead.

    PYTHONPATH=. python3 tools/build_tabards.py          # check
    PYTHONPATH=. python3 tools/build_tabards.py --write  # data/items/tabards.json, the quartermasters, the icons

Kyle, 18 Nov 2026: "I want to have the tabbard style rep where wearing a factions tabbard will shift all rep gained to
that faction. Since no factions will gain rep in dungeons past revered unless the dungeon is heroic - this will help
to get all factions to exalted and lets the player pick." His answers on the details: dungeon kills only (quest and
zone rep never move), heroics only, and build it now with heroic mode next (docs/tabards_design.md).

One tabard per faction, the secret one excepted. Each faction's quartermaster sells it at Friendly for 1 gold. No
stats: it sits in its own slot (entities/equipment.py "tabard"). Its icon is sheet T1's (docs/tabard_art_prompts.md); a
new faction's tabard gets the guild tabard tinted to its colours until it has art.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "items" / "tabards.json"
FACTIONS = ROOT / "data" / "factions" / "factions.json"
BASE_ICON = ROOT / "assets" / "icons" / "gear" / "gear_inv_shirt_guildtabard_01.png"
PRICE = 10000   # 1 gold

#: the faction's colours, for the stand-in icon: (main, trim)
COLOURS = {
    "crimson_codex": ((150, 20, 30), (220, 180, 70)),
    "orgrimmar": ((170, 30, 20), (40, 30, 25)),
    "darkspear_tribe": ((30, 130, 140), (150, 60, 170)),
    "the_forsaken": ((60, 40, 80), (110, 160, 60)),
    "steamwheedle_cartel": ((40, 120, 50), (220, 180, 60)),
    "thunder_bluff": ((150, 100, 50), (230, 220, 200)),
    "booty_bay_authority": ((30, 70, 150), (230, 200, 90)),
    "the_ashclaim": ((50, 45, 45), (230, 110, 30)),
    "emerald_reclamation": ((30, 140, 70), (230, 230, 210)),
    "pale_flame": ((235, 230, 215), (220, 170, 60)),
    "argent_dawn": ((210, 210, 220), (60, 90, 170)),
    "timbermaw_hold": ((90, 110, 50), (140, 90, 50)),
    "sunreach_conclave": ((190, 40, 30), (240, 200, 70)),
    "the_liquidators": ((230, 190, 30), (40, 40, 40)),
    "cenarion_circle": ((70, 130, 70), (120, 80, 160)),
    "the_wakened": ((150, 170, 210), (240, 230, 160)),
    "feathermoon_sentinels": ((80, 55, 140), (205, 205, 225)),
    "highbough_tribes": ((30, 120, 120), (200, 70, 40)),
    "aetherians": ((235, 235, 245), (205, 160, 50)),
}


def factions():
    return json.loads(FACTIONS.read_text(encoding="utf-8"))["factions"]


def tabard_id(fid):
    return f"tabard_{fid}"


def build():
    items, plan = {}, {}
    for fid, f in factions().items():
        if f.get("secret") or fid == "the_unnamed":
            continue                       # the secret faction has no tabard: it's never advertised
        qms = list(((f.get("rewards") or {}).get("vendor_stock") or {}).keys())
        if not qms:
            raise SystemExit(f"{fid} has no quartermaster to sell its tabard")
        name = f["name"][4:] if f["name"].startswith("The ") else f["name"]
        items[tabard_id(fid)] = {
            "name": f"Tabard of {name}", "slot": "tabard", "item_level": 1, "rarity": "common",
            "armor_type": None, "weapon_type": None, "primary_stats": {}, "secondary_stats": {},
            "armor_value": 0, "required_level": 1, "sell_price": PRICE // 4,
            "flavor_text": f"Worn in a heroic dungeon, it sends what you earn there to {f['name']}.",
            "icon_id": tabard_id(fid), "price": PRICE, "faction": fid, "tabard_of": fid,
        }
        plan[fid] = qms[0]
    return items, plan


def tint_icon(fid):
    """The guild tabard recoloured: its light cloth to the faction's main colour, its dark trim to the trim."""
    main, trim = COLOURS[fid]
    im = np.array(Image.open(BASE_ICON).convert("RGBA")).astype(float)
    rgb, a = im[..., :3], im[..., 3:]
    lum = (rgb @ np.array([0.299, 0.587, 0.114]))[..., None] / 255.0
    cloth = np.clip((lum - 0.35) / 0.25, 0, 1)            # the pale cloth takes the main colour
    shade = 0.35 + 0.85 * lum                             # keep the folds and the shading
    col = np.array(main) * cloth + np.array(trim) * (1 - cloth)
    out = np.clip(col * shade, 0, 255) * 0.9 + rgb * 0.1 * (1 - cloth) + rgb * 0.05 * cloth
    img = np.concatenate([np.clip(out, 0, 255), a], axis=2).astype(np.uint8)
    dst = ROOT / "assets" / "icons" / "gear" / f"{tabard_id(fid)}.png"
    Image.fromarray(img, "RGBA").save(dst)


def main():
    items, plan = build()
    print(f"  {len(items)} tabards")
    if "--write" not in sys.argv:
        return 0
    OUT.write_text(json.dumps({"_doc": "Built by tools/build_tabards.py; docs/tabards_design.md", "items": items},
                              indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    data = json.loads(FACTIONS.read_text(encoding="utf-8"))
    for fid, qm in plan.items():
        friendly = data["factions"][fid]["rewards"]["vendor_stock"][qm].setdefault("friendly", [])
        entry = f"unique:{tabard_id(fid)}"
        if entry not in friendly:
            friendly.insert(0, entry)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    FACTIONS.write_text(text, encoding="utf-8")
    for fid in plan:
        # the real icons landed 18 Nov (sheet T1, docs/tabard_art_prompts.md): a stand-in is only made for a
        # tabard that has none, so a rebuild never paints over the art
        if not (ROOT / "assets" / "icons" / "gear" / f"{tabard_id(fid)}.png").exists():
            tint_icon(fid)
    print(f"  written {OUT.relative_to(ROOT)}, {len(plan)} quartermasters, {len(plan)} icons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
