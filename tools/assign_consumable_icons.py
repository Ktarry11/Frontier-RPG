#!/usr/bin/env python3
"""Every potion, elixir, flask, food and drink gets an icon of its own, from Kyle's WoW icon pack.

    PYTHONPATH=. python3 tools/assign_consumable_icons.py --pack "/path/to/WoW Icon Pack" [--apply]

Kyle, 16 Nov 2026: "every unique item in the game can only have ONE icon", and with the pack: "Take what you need
and include it for current crafting and cooking or other professions as needed!"

Two jobs:
  * NAMED: consumables that had no art at all (the higher potion ranks, the herb potions and flasks, the newer
    meals and drinks) take the pack icon chosen for them by eye in NAMED below.
  * SHARED: the alchemy sheet gave each elixir family one LESSER and one GREATER bottle and let the middle ranks
    reuse them (entities/consumable_icons.py). Every id after the first on a shared bottle now takes the pack
    potion nearest that bottle's colour, so a family still reads as a family and no two items share a picture.

A file named after the consumable wins over the family map (entities/consumable_icons.icon_for), so each pick is a
96x96 file in assets/icons/consumables/<consumable_id>.png. Only the files used are copied in.
"""
import argparse
import collections
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

DEST = ROOT / "assets/icons/consumables"

#: consumable_id -> pack-relative file, picked by eye (healing red, mana blue, the herb's colour for herb potions)
NAMED = {
    "healing_potion_greater": "Trade/51_potion_potion.png",
    "healing_potion_major": "Trade/53_potion_potion.png",
    "healing_potion_masterwork": "Trade/142_potion_potion.png",
    "healing_potion_supreme": "Trade/131_potion_potion.png",
    "healing_potion_sansam": "Trade/54_potion_potion.png",
    "mana_potion_greater": "Trade/71_potion_potion.png",
    "mana_potion_major": "Trade/73_potion_potion.png",
    "mana_potion_masterwork": "Trade/137_potion_potion.png",
    "mana_potion_supreme": "Trade/126_potion_potion.png",
    "mana_potion_dreamfoil": "Trade/74_potion_potion.png",
    "elixir_icecap": "Trade/98_potion_potion.png",
    "elixir_of_stonescale": "Trade/86_potion_potion.png",
    "elixir_of_the_current": "Trade/77_potion_potion.png",
    "elixir_of_the_firefin": "Trade/38_potion_potion.png",
    "elixir_purple_lotus": "Trade/45_potion_potion.png",
    "elixir_shadow_power": "Trade/87_potion_potion.png",
    "elixir_steelbloom": "Trade/85_potion_potion.png",
    "flask_black_lotus": "Trade/132_potion_potion.png",
    "flask_mending": "Trade/149_potion_potion.png",
    "potion_free_action": "Trade/57_potion_potion.png",
    "potion_invulnerability": "Trade/62_potion_potion.png",
    "meal_ember_glazed_ribs": "Miscellaneous/Food_48.png",
    "meal_saltback_roast": "Miscellaneous/Food_84_RoastClefthoof.png",
    "high_table_feast": "Miscellaneous/Food_15.png",
    "hunters_brace_platter": "Miscellaneous/Food_123_Roast.png",
    "drink_deepwell_cordial": "Miscellaneous/Beer_03.png",
    "drink_starfall_wine": "Miscellaneous/Beer_07.png",
}


def consumable_ids():
    ids = set()

    def walk(o):
        if isinstance(o, dict):
            if o.get("consumable_id"):
                ids.add(o["consumable_id"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for f in glob.glob(str(ROOT / "data/consumables/*.json")) + glob.glob(str(ROOT / "data/**/recipes.json"),
                                                                           recursive=True):
        walk(json.loads(Path(f).read_text(encoding="utf-8")))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    from PIL import Image
    from entities.consumable_icons import icon_for
    from assign_crafted_icons import _measure_path
    from crafted_icon_palette import distance
    pack = Path(a.pack)
    ids = sorted(consumable_ids())

    picks = {}
    for cid, src in NAMED.items():
        if cid in ids and icon_for(cid) is None:
            picks[cid] = src
    # the shared bottles: everyone after the first holder gets the nearest pack potion by colour
    by_icon = collections.defaultdict(list)
    for cid in ids:
        stem = icon_for(cid)
        if stem:
            by_icon[stem].append(cid)
    potions = sorted(p.relative_to(pack).as_posix() for p in (pack / "Trade").glob("*_potion_potion.png"))
    taken = set(picks.values())
    measured = {}
    for stem, holders in sorted(by_icon.items()):
        if len(holders) < 2:
            continue
        want = _measure_path(DEST / f"{stem}.png")
        for cid in sorted(holders)[1:]:
            free = [p for p in potions if p not in taken]
            best = min(free, key=lambda p: (distance(want, measured.setdefault(p, _measure_path(pack / p))), p))
            picks[cid] = best
            taken.add(best)
    missing = [cid for cid in ids if icon_for(cid) is None and cid not in picks]
    print(f"{len(ids)} consumables: {sum(1 for c in picks if icon_for(c) is None)} had no icon, "
          f"{sum(1 for c in picks if icon_for(c))} shared a bottle; {len(missing)} still without art {missing[:5]}")
    if len(set(picks.values())) != len(picks):
        print("FAILED: one pack file picked twice")
        return 1
    if a.apply:
        for cid, src in picks.items():
            Image.open(pack / src).convert("RGBA").resize((96, 96), Image.LANCZOS).save(DEST / f"{cid}.png")
        print(f"copied {len(picks)} icons into {DEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
