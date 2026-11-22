#!/usr/bin/env python3
"""High-level shops with full shelves (21 Nov 2026).

    PYTHONPATH=. python3 tools/build_highlevel_shelves.py            # report only
    PYTHONPATH=. python3 tools/build_highlevel_shelves.py --write    # top the shelves up

Kyle, 21 Nov 2026: "most of the new shops are ONCE AGAIN falling into selling almost nothing at high level". The
newer towns (Aurelion, Timbermaw Hold, Moonglade, the sky camps, Ariden's Watch) had smiths selling a whetstone and
some coal, and quartermasters with three things on the front shelf. Cinderwharf, at the same level, sells sixteen.

Every vendor in a level 44+ town is given a role from its name (smith, food, trader, alchemist, quartermaster) and
topped up to that role's count from the items already sold at that level somewhere in the game: consumables whose
level suits the town, the trade's reagents and kits, and a few patterns and cut gems picked per vendor so two smiths
don't carry the same six. Nothing is ever taken off a shelf. Hidden sellers, the heroic quartermasters and the egg
are left alone, and a quartermaster's standing-locked stock is separate (data/factions/factions.json).
"""
import contextlib
import hashlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

MIN_LEVEL = 44
SKIP_PREFIX = ("secret_", "fq_", "egg_")
TARGET = {"smith": 16, "food": 15, "trader": 14, "alchemist": 13, "quartermaster": 10}
ROLE_WORDS = [
    ("quartermaster", ("quartermaster",)),
    ("smith", ("smith", "forge", "armour", "armor", "ironmonger")),
    ("alchemist", ("alchemist", "reagent", "herbal", "brewer")),
    ("food", ("provision", "cook", "innkeeper", "honeymother", "chef", "baker")),
    ("trader", ("trader", "goods", "broker", "supply", "peg", "merchant")),
]
BASE = {
    "smith": ["whetstone", "flux_strong", "coal", "kit_field_repair", "jewelers_kit", "setting_ring_gold",
              "setting_necklace_gold", "setting_ring_silver"],
    "food": ["cook_flour", "cook_spice", "cook_honey", "cook_cheese", "cook_fruit", "cook_roots", "cook_mushroom",
             "cook_ale", "cook_water"],
    "trader": ["parchment", "kit_field_repair", "vial_crystal", "beast_lure", "beast_lure_greater"],
    "alchemist": ["vial_empty", "vial_leaded", "vial_crystal"],
    "quartermaster": ["kit_field_repair"],
}
#: what a role may draw from the consumables already sold at this level (by id prefix), never more than eight levels
#: under the town (tools/qa_vendor_stock.py's tier-chain rule); explosives are left to the shops that stock the
#: whole line, because that check wants the best bomb wherever any bomb is sold
CONSUMABLE_KINDS = {
    "food": ("meal_", "drink_", "high_table_feast", "hunters_brace_platter"),
    "trader": ("healing_potion_", "mana_potion_", "barbed_arrows", "broadhead_arrows", "shot_", "quarrel_"),
    "alchemist": ("healing_potion_", "mana_potion_", "elixir_", "flask_", "battle_elixir_", "guardian_elixir_"),
    "quartermaster": ("healing_potion_", "mana_potion_", "meal_", "drink_"),
    "smith": (),
}
#: patterns and cut gems a role picks a handful of, per vendor
PATTERNS = {"smith": ("bs300_", "bs_mithril", "bs_runeplate", "bs_runescale", "jc_cut_"),
            "food": ("cookx_", "cook300_"), "alchemist": ("alch_",), "trader": (), "quartermaster": ()}
PATTERN_COUNT = {"smith": 6, "food": 2, "alchemist": 2, "trader": 0, "quartermaster": 0}
BAGS = ("duskwoven_carryall", "deepdelve_bearer", "runeforged_strongbox", "warden_reliquary")


def role_of(v):
    text = f"{v['vendor_id']} {v.get('name', '')}".lower()
    for role, words in ROLE_WORDS:
        if any(w in text for w in words):
            return role
    return None


def pick(seq, n, salt):
    seq = sorted(set(seq), key=lambda s: hashlib.md5(f"{salt}:{s}".encode()).hexdigest())
    return seq[:n]


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from world.vendor_stock import resolve_vendor_item
        from entities.consumable_manager import get_consumable_manager
        from world.gathering_manager import GatheringNodeManager
        from entities.loot_generator import LootGenerator
        cm, gm, lg = get_consumable_manager(), GatheringNodeManager(), LootGenerator()
    path = ROOT / "data/npcs/vendors.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    vendors = doc["vendors"]
    level_of = {}
    pool = set()
    sold_at = {}          # item -> the highest town level it's already sold at: a pattern's level, near enough
    for v in vendors:
        pool |= set(v.get("sells") or [])
        for i in v.get("sells") or []:
            sold_at[i] = max(sold_at.get(i, 0), v.get("gear_level") or 0)
    for i in sorted(pool):
        with contextlib.redirect_stdout(io.StringIO()):
            t = resolve_vendor_item(i, consumable_manager=cm, gathering_manager=gm, loot_generator=lg)
        if t is not None:
            level_of[i] = getattr(t, "required_level", None) or getattr(t, "level", None) or 1
    changed = 0
    for v in vendors:
        gl = v.get("gear_level") or 0
        if gl < MIN_LEVEL or v["vendor_id"].startswith(SKIP_PREFIX):
            continue
        role = role_of(v)
        if role is None:
            continue
        have = list(v.get("sells") or [])
        want = TARGET[role]
        if len(have) >= want:
            continue
        add = [b for b in BASE[role] if b in level_of and b not in have]
        kinds = CONSUMABLE_KINDS[role]
        cons = [i for i, lv in level_of.items() if kinds and i.startswith(kinds) and gl - 8 <= (lv or 0) <= gl + 2]
        # the best of each line first: highest level that the town can use
        cons.sort(key=lambda i: -(level_of[i] or 0))
        add += [c for c in cons if c not in have and c not in add][:6]
        if role == "quartermaster":
            add += pick([b for b in BAGS if b in level_of], 1, v["vendor_id"])
        if PATTERN_COUNT[role]:
            pats = [i for i in level_of if i.startswith(PATTERNS[role]) and i not in have
                    and sold_at.get(i, 0) >= gl - 12]
            add += pick(pats, PATTERN_COUNT[role], v["vendor_id"])
        new = have + [a for a in dict.fromkeys(add) if a not in have]
        new = new[:max(want, len(have))]
        if len(new) > len(have):
            print(f"  {v['vendor_id']:28s} {role:13s} L{gl}: {len(have):2d} -> {len(new):2d}")
            if "--write" in sys.argv:
                v["sells"] = new
            changed += 1
    if "--write" in sys.argv:
        path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  wrote {changed} shelves")
    else:
        print(f"  {changed} shelves would be topped up (run with --write)")


if __name__ == "__main__":
    main()
