#!/usr/bin/env python3
"""Slice Kyle's consumables sheet and his three crafted-epic sheets into the game, and point the items at them.
Idempotent.

    PYTHONPATH=. python3 tools/install_crafted_art_sheets.py

THE SHEETS (Kyle delivered all four on 17 Nov 2026):
  consumables   docs: claude/crafting_icon_prompts_sheet3.md. 21 potions and elixirs, 4 meals, 2 drinks and Al'ar Down,
                each a 96px icon named for its consumable_id in assets/icons/consumables/, which
                entities/consumable_icons.icon_for picks up by name. They replace the pack icons the 16 Nov pass lent
                them.
  E1, E2, E3    docs: claude/crafting_epic_icon_prompts.md. The 82 crafted epics, one icon each, a collection sharing
                one look, as assets/icons/gear/gear_epic_crafted_<name>.png (tools/build_crafted_gear.epic_icon_id).
                Each epic's icon_id in the recipe files and its pick in data/items/crafted_icons.json move to its own
                art, so a rebuild keeps it (build_crafted_gear.icon_for reads crafted_icons.json first).

Icons are found as whole objects on the magenta and assigned to the nearest grid slot (tools/slice_crafting_fix_icons).
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.slice_crafting_fix_icons import objects  # noqa: E402
from tools.slice_mob_reagents import key  # noqa: E402

SHEETS = ROOT / "tools/icon_sheets"
CONS = ROOT / "assets/icons/consumables"
GEAR = ROOT / "assets/icons/gear"
SIZE = 96
RECIPE_FILES = ["data/crafting/recipes.json", "data/blacksmithing/recipes.json", "data/leatherworking/recipes.json",
                "data/jewelcrafting/recipes.json"]
PICKS = ROOT / "data/items/crafted_icons.json"

CONSUMABLES = [
    "healing_potion_greater", "healing_potion_major", "healing_potion_masterwork", "healing_potion_supreme",
    "healing_potion_sansam", "mana_potion_greater", "mana_potion_major",
    "mana_potion_masterwork", "mana_potion_supreme", "mana_potion_dreamfoil", "elixir_steelbloom",
    "elixir_purple_lotus", "elixir_icecap", "flask_black_lotus",
    "elixir_of_the_current", "elixir_of_the_firefin", "elixir_of_stonescale", "elixir_shadow_power", "flask_mending",
    "potion_free_action", "potion_invulnerability",
    "hunters_brace_platter", "high_table_feast", "meal_saltback_roast", "meal_ember_glazed_ribs",
    "drink_deepwell_cordial", "drink_starfall_wine", "alar_down",
]
E1 = [
    "Felcloth Robe", "Felcloth Cuffs", "Felcloth Gloves", "Soulcloth Sash", "Soulcloth Leggings", "Soulcloth Slippers",
    "Soulcloth Cloak",
    "Windwool Hood", "Windwool Mantle", "Windwool Robe", "Windwool Cuffs", "Imperial Silk Gloves",
    "Imperial Silk Sash", "Imperial Silk Leggings",
    "Imperial Silk Slippers", "Voidweave Cloak", "Voidweave Hood", "Voidweave Mantle", "Voidweave Robe",
    "Starleaf Crossbow", "Starleaf Codex",
    "Stormoak Wand", "Stormoak Staff", "Stormoak Longbow", "Thorium Gyro-Visor", "Arcanite Dragonling Core",
    "Arcanite Longrifle", "Elementium Siege Harness",
]
E2 = [
    "Thorium Halberd", "Thorium Bulwark", "Ashen Steel Spaulders", "Ashen Steel Hauberk", "Ashen Steel Wristguards",
    "Ashen Steel Blade", "Ashen Steel Dirk",
    "Ashen Steel Bulwark", "Arcanite Gauntlets", "Arcanite Girdle", "Arcanite Legplates", "Arcanite Sabatons",
    "Arcanite Bulwark", "Arcanite Mace",
    "Elementium Helm", "Elementium Pauldrons", "Elementium Breastplate", "Elementium Bracers", "Elementium Halberd",
    "Elementium Bulwark", "Savage Leather Pants",
    "Rugged Vest", "Rugged Bracers", "Rugged Gloves", "Netherdrake Belt", "Netherdrake Pants", "Netherdrake Boots",
    "Netherdrake Cloak",
]
E3 = [
    "Duskfang Leather Boots", "Duskfang Bracers", "Duskfang Gloves", "Duskfang Belt", "Duskfang Pants",
    "Bloodtanned Jerkin", "Bloodtanned Mask",
    "Bloodtanned Cloak", "Bloodtanned Helm", "Bloodtanned Spaulders", "Bloodtanned Vest", "Emberscale Coif",
    "Emberscale Helm", "Emberscale Spaulders",
    "Emberscale Vest", "Emberscale Bracers", "Frostscale Vest", "Frostscale Boots", "Frostscale Cloak",
    "Frostscale Helm", "Frostscale Spaulders",
    "Mossback Spaulders", "Mossback Gloves", "Mossback Belt", "Mossback Pants", "Mossback Boots",
]
#: sheet file, columns, rows, ids in reading order, where they go, how they're named
JOBS = [
    ("crafting_consumables_sheet3.png", 7, 4, CONSUMABLES, CONS, lambda n: n),
    ("crafted_epics_e1.png", 7, 4, E1, GEAR, None),
    ("crafted_epics_e2.png", 7, 4, E2, GEAR, None),
    ("crafted_epics_e3.png", 7, 4, E3, GEAR, None),
]


def epic_icon_id(name):
    return "gear_epic_crafted_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def cut(sheet, box):
    W, H = sheet.size
    x0, y0, x1, y1 = box
    pad = 6
    im = key(sheet.crop((max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))))
    bbox = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    im = im.crop(bbox)
    side = int(max(im.size) * 1.06) + 2
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.size[0]) // 2, (side - im.size[1]) // 2))
    return sq.resize((SIZE, SIZE), Image.LANCZOS)


def slice_all():
    out = {}
    for fname, cols, rows, ids, dest, naming in JOBS:
        sheet = Image.open(SHEETS / fname).convert("RGB")
        boxes = objects(sheet, cols, rows)
        for i, n in enumerate(ids):
            slot = (i % cols, i // cols)
            if slot not in boxes:
                raise SystemExit(f"{n}: nothing found in slot {slot} of {fname}")
            stem = naming(n) if naming else epic_icon_id(n)
            cut(sheet, boxes[slot]).save(dest / f"{stem}.png")
            out[n] = stem
    return out


def point_epics(stems):
    epics = {n: stems[n] for n in E1 + E2 + E3}
    seen, moved = set(), 0

    def walk(x):
        nonlocal moved
        if isinstance(x, dict):
            o = x.get("output")
            if isinstance(o, dict) and isinstance(o.get("item"), dict) and o["item"].get("name") in epics:
                it = o["item"]
                seen.add(it["name"])
                if it.get("icon_id") != epics[it["name"]]:
                    it["icon_id"] = epics[it["name"]]
                    moved += 1
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    for f in RECIPE_FILES:
        p = ROOT / f
        raw = p.read_text(encoding="utf-8")
        d = json.loads(raw)
        walk(d)
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""),
                     encoding="utf-8")
    missing = sorted(set(epics) - seen)
    if missing:
        raise SystemExit(f"epics on the sheets with no recipe: {missing}")
    raw = PICKS.read_text(encoding="utf-8")
    picks = json.loads(raw)
    picks["icons"].update(epics)
    PICKS.write_text(json.dumps(picks, indent=2, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""),
                     encoding="utf-8")
    return moved


def main():
    stems = slice_all()
    moved = point_epics(stems)
    print(f"{len(CONSUMABLES)} consumable icons, {len(E1 + E2 + E3)} crafted epic icons; {moved} recipe outputs moved")


if __name__ == "__main__":
    main()
