#!/usr/bin/env python3
"""Give the eight dead-end gathering materials somewhere to go.

    PYTHONPATH=. python3 tools/build_material_sink_recipes.py [--dry-run]

WHAT WAS WRONG. tools/qa_materials.py: eight materials a player can gather
at or below the content ceiling that "no chain of recipes turns into
anything a player can equip, use or carry". The report blames the raw
material, but every chain actually dies one step LATER than that, which is
why it looked like a gathering problem and is really a crafting one:

    ore_gold      -> bar_gold        -> nothing
    ore_mithril   -> bar_mithril     -> nothing
    wood_silverbark_tree -> plank_silverbark -> nothing
    wood_goldenleaf_tree -> plank_goldenleaf -> nothing
    wood_sapglow_stump   -> plank_sapglow    -> nothing
    wood_redbark_tree    -> plank_redbark    -> nothing
    wood_duskwood_stump  -> plank_duskwood   -> nothing
    wood_marshwillow     -> plank_marshwillow-> nothing

The smelting and milling steps are all authored and correct. What is
missing is the tier of finished goods on the end, so a player mines mithril
in Tanaris, smelts it, and holds a bar no recipe in the game wants.

WHERE EACH TIER SITS, and none of it is invented: the levels come from the
zones the node pools actually put these materials in
(data/gathering/node_pools.json), and the skill numbers continue each
profession's own existing ladder rather than starting a new one.

    bar_gold     Arathi Central/East, Drywhisker Deeps (~30-38)
                 ENGINEERING, because gold is engineering's metal in real
                 Classic (Gold Power Core, Golden Rod) and engineering's
                 ladder already ends at steel, skill 126-150 / ilvl 26-30.
                 Gold continues it at 155-180 / ilvl 32-38.
    bar_mithril  Northern Tanaris, Abyssal Sands, Glittervein, Arathi East
                 (~40-48). BLACKSMITHING, whose ladder is copper (ilvl
                 2-20) -> bronze (21-41) -> iron (42-43, and only three
                 items). Mithril is the tier above iron at skill 215-245 /
                 ilvl 44-50.
    the planks   WOODWORKING, whose ladder is ashwood (ilvl 2-20) ->
                 ironbark (13-42). Each plank's items sit at the level of
                 the zone its tree grows in: silverbark 27 (The Aspen
                 Wilderness), goldenleaf 32 (Northern Stranglethorn),
                 sapglow 34 (The Crystalline Underdark), redbark 35
                 (Central Stranglethorn), duskwood and marshwillow 40
                 (Southern Stranglethorn).

Output shapes are taken from what each profession already makes - staves,
bows, wands, shields and tomes for woodworking; plate and mail for
blacksmithing; guns, goggles and trinkets for engineering - so nothing
here introduces a slot or weapon type the profession has never produced.

Idempotent: re-running rewrites the same ids and touches nothing else.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: material_tier -> (plank id, item level, first skill). The item level is
#: the level of the zone the tree grows in; see the module docstring.
PLANKS = {
    "silverbark":  ("plank_silverbark",  27, 150),
    "goldenleaf":  ("plank_goldenleaf",  32, 165),
    "sapglow":     ("plank_sapglow",     34, 172),
    "redbark":     ("plank_redbark",     35, 178),
    "duskwood":    ("plank_duskwood",    40, 196),
    "marshwillow": ("plank_marshwillow", 40, 196),
}

#: Two items per plank, both shapes woodworking already makes a lot of, so
#: each tier gives a caster and a hunter something rather than one item
#: that only suits one kind of character.
PLANK_ITEMS = [
    ("staff", dict(kind="weapon", slot="main_hand", weapon_type="staff",
                   stat_template="int_caster", rarity="uncommon"), 4, 0),
    ("bow", dict(kind="weapon", slot="ranged", weapon_type="bow",
                 stat_template="agi_physical", rarity="uncommon"), 3, 6),
]

PLANK_NAMES = {
    "silverbark":  ("Silverbark Stave", "Silverbark Longbow"),
    "goldenleaf":  ("Goldenleaf Stave", "Goldenleaf Hunting Bow"),
    "sapglow":     ("Sapglow Stave", "Sapglow Shortbow"),
    "redbark":     ("Redbark Stave", "Redbark Warbow"),
    "duskwood":    ("Duskwood Stave", "Duskwood Longbow"),
    "marshwillow": ("Marshwillow Stave", "Marshwillow Recurve"),
}

#: Blacksmithing's mithril tier - the step above iron. Plate and mail, the
#: two armour types blacksmithing already makes, plus a weapon and a
#: shield, which is the shape its bronze tier has.
MITHRIL = [
    ("bs_mithril_coif", "Mithril Coif", 215,
     dict(kind="armor", slot="head", armor_type="mail",
          stat_template="agi_physical", item_level=44, rarity="uncommon"),
     {"bar_mithril": 6}),
    ("bs_mithril_breastplate", "Mithril Breastplate", 222,
     dict(kind="armor", slot="chest", armor_type="plate",
          stat_template="str_physical", item_level=46, rarity="uncommon"),
     {"bar_mithril": 10}),
    ("bs_mithril_gauntlets", "Mithril Gauntlets", 228,
     dict(kind="armor", slot="hands", armor_type="plate",
          stat_template="str_physical", item_level=46, rarity="uncommon"),
     {"bar_mithril": 6}),
    ("bs_mithril_shield", "Mithril Shield", 234,
     dict(kind="weapon", slot="off_hand", weapon_type="shield",
          stat_template="str_physical", item_level=48, rarity="uncommon"),
     {"bar_mithril": 8, "plank_ironbark": 2}),
    ("bs_mithril_warhammer", "Mithril Warhammer", 240,
     dict(kind="weapon", slot="main_hand", weapon_type="mace_1h",
          stat_template="str_physical", item_level=48, rarity="rare"),
     {"bar_mithril": 12, "plank_ironbark": 2}),
    ("bs_mithril_greaves", "Mithril Greaves", 245,
     dict(kind="armor", slot="legs", armor_type="plate",
          stat_template="str_physical", item_level=50, rarity="rare"),
     {"bar_mithril": 12}),
]

#: Engineering's gold tier - the step above steel. Gold is the metal real
#: Classic engineering uses, and these are the three shapes engineering
#: already makes most: goggles, a gun and a trinket.
GOLD = [
    ("eng_gold_power_core", "Gold Power Core", 155,
     dict(kind="armor", slot="trinket", armor_type="accessory",
          stat_template="agi_int_hybrid", item_level=32, rarity="uncommon"),
     {"bar_gold": 4, "bar_steel": 2}),
    ("eng_gilded_goggles", "Gilded Marksman's Goggles", 165,
     dict(kind="armor", slot="head", armor_type="mail",
          stat_template="agi_physical", item_level=34, rarity="uncommon"),
     {"bar_gold": 6, "bar_steel": 2}),
    ("eng_goldwired_longrifle", "Gold-Wired Longrifle", 180,
     dict(kind="weapon", slot="ranged", weapon_type="gun",
          stat_template="agi_physical", item_level=38, rarity="rare"),
     {"bar_gold": 8, "bar_steel": 4, "plank_ironbark": 2}),
]

SOURCE = ("tools/build_material_sink_recipes.py - the sink for a material "
          "whose smelting or milling step existed and whose finished-goods "
          "tier did not (qa_materials).")


def skill_range(first):
    """The four-step green/yellow/grey ladder every recipe here carries,
    same +5/+15/+25/+35 shape as the authored ones."""
    return [first + 5, first + 15, first + 25, first + 35]


def build():
    out = {"woodworking": {}, "blacksmithing": {}, "engineering": {}}

    for tier, (plank, ilvl, skill) in PLANKS.items():
        for (shape_name, shape, qty, bump), name in zip(PLANK_ITEMS,
                                                        PLANK_NAMES[tier]):
            rid = f"ww_{tier}_{shape_name}"
            out["woodworking"][rid] = {
                "name": name,
                "skill_required": skill + bump,
                "skill_range": skill_range(skill + bump),
                "source": "trainer",
                "inputs": {plank: qty},
                "output": dict(shape, item_level=ilvl, material_tier=tier),
                "_source": SOURCE,
            }

    for rid, name, skill, shape, inputs in MITHRIL:
        out["blacksmithing"][rid] = {
            "name": name,
            "skill_required": skill,
            "skill_range": skill_range(skill),
            "source": "trainer",
            "inputs": inputs,
            "output": dict(shape, material_tier="mithril"),
            "_source": SOURCE,
        }

    for rid, name, skill, shape, inputs in GOLD:
        out["engineering"][rid] = {
            "name": name,
            "skill_required": skill,
            "skill_range": skill_range(skill),
            "source": "trainer",
            "inputs": inputs,
            "output": dict(shape, material_tier="gold"),
            "_source": SOURCE,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    new = build()
    total = sum(len(v) for v in new.values())

    # Blacksmithing is its own flat file; woodworking and engineering live
    # under data/crafting/recipes.json's "professions" map.
    bs_path = ROOT / "data/blacksmithing/recipes.json"
    cr_path = ROOT / "data/crafting/recipes.json"
    bs = json.loads(bs_path.read_text(encoding="utf-8"))
    cr = json.loads(cr_path.read_text(encoding="utf-8"))

    added = 0
    for rid, rec in new["blacksmithing"].items():
        if bs["recipes"].get(rid) != rec:
            added += 1
        bs["recipes"][rid] = rec
    for prof in ("woodworking", "engineering"):
        block = cr["professions"].setdefault(prof, {})
        recs = block.setdefault("recipes", {})
        for rid, rec in new[prof].items():
            if recs.get(rid) != rec:
                added += 1
            recs[rid] = rec

    print(f"  {total} recipe(s) in the pass, {added} new or changed")
    for prof, v in new.items():
        print(f"    {prof:16} {len(v)}: {', '.join(sorted(v))}")
    if args.dry_run:
        print("  --dry-run, nothing written")
        return 0
    bs_path.write_text(json.dumps(bs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    cr_path.write_text(json.dumps(cr, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  wrote {bs_path}")
    print(f"  wrote {cr_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
