#!/usr/bin/env python3
"""Put the vendor-source recipes on the right counters, and plant four hidden sellers. Idempotent.

    PYTHONPATH=. python3 tools/build_recipe_vendors.py

Kyle, 2026-10-28: "We can also spice up the new zones and have hidden vendors, ensure there are nice
rare drops of useful recipies to learn etc."

57 recipes carried source "vendor" and nobody stocked a single one. They were not generic, either -
they are named for places: Ratchet Scattergun, Astranaar Moonrobe, Orgrimmar Felweave Robe, Taurajo
Warbands, Fenris Mail Spaulders, Razorfen Tusk Bracers. Somebody wrote each one for a particular
shop and the last step never happened, so the matching is mostly just reading the names.

Three passes, in order of how much the match can be trusted:

  1. PLACE. The recipe names a town, and that town has vendors. This is the author's own intent and
     it wins over everything else.
  2. TRADE. A smith sells Plans, a tailor sells Patterns, a bowyer sells bows. Among the vendors
     whose id carries the right trade, take the one whose gear level is closest to the recipe's own
     level, so a skill-200 pattern does not land on a level-8 tailor in Brill.
  3. LEVEL. Nothing else matched, so the nearest gear-level vendor of any trade gets it.

Anything still unmatched is reported as a failure rather than quietly dropped, because quietly
dropped is exactly how all 57 got here.

THE HIDDEN SELLERS are a different job. The new zones have no themed recipes of their own, and what
makes a hidden vendor worth finding is not a bargain but a stock you cannot get in town. Each one
gets the handful of highest-skill patterns in its band plus the field supplies you want when you are
a long way from an inn. Positions come from tools/find_hidden_vendor_spots.py, which flood-fills the
map and only offers tiles in the region the player can actually reach - Ivan spent a while at
Ragefire standing inside a sealed pocket of rock because a bare is_walkable check says yes to that.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Place word in a recipe name -> the zone key whose vendors should stock it.
PLACES = {
    "ratchet": "ratchet", "taurajo": "camp_taurajo", "orgrimmar": "orgrimmar",
    "undercity": "undercity", "fenris": "fenris_isle", "hillsbrad": "western_hillsbrad",
    "astranaar": "zoram_strand", "razorfen": "southern_barrens", "barrens": "crossroads",
    "warsong": "orgrimmar", "silverpine": "silverpine_south", "tarren": "tarren_mill",
    "sepulcher": "sepulcher", "freewind": "freewind_post", "plains": "camp_taurajo",
}

#: Profession -> the id fragments of vendors who would plausibly sell its patterns, best first.
TRADES = {
    "blacksmithing": ("smith", "weaponsmith", "quartermaster"),
    "tailoring": ("tailor", "trader", "general_goods", "provisioner", "market"),
    "leatherworking": ("hide", "quartermaster", "trader", "provisioner"),
    "woodworking": ("bowyer", "fletcher", "weaponsmith", "smith"),
    "engineering": ("engineer", "explosives", "dockmaster", "smith"),
    "alchemy": ("alchemist", "apothecary", "reagent", "elixir", "vat"),
    "cooking": ("cook", "butcher", "innkeeper", "provisioner"),
}

#: (vendor_id, name, zone key, x, y, race, gear_level, greeting, extra stock)
#: Positions verified reachable by tools/find_hidden_vendor_spots.py - never hand-guessed.
HIDDEN = [
    ("needles_gully_trader", "Pell Dunewright", "southern_thousand_needles", 5, 134, "goblin", 33,
     "Nobody comes down this gully by accident, so I'll assume you want something.",
     ["meal_spiced_haunch", "drink_honeyed_mead", "healing_potion_superior", "mana_potion_superior",
      "thread_fine", "vial_empty"]),
    ("weeping_moulin_keeper", "Hesta Coldhand", "the_weeping_ice", 48, 129, "dwarf", 30,
     "I came down here to look at the ice. Staying was a separate decision.",
     ["meal_spiced_haunch", "drink_honeyed_mead", "healing_potion_superior", "vial_empty",
      "curing_salt", "flux_strong"]),
    ("ashenvale_satyr_fence", "Veln Ashgrease", "ashenvale_east", 213, 156, "goblin", 28,
     "You didn't see me and I didn't see what you're carrying. Now, business.",
     ["meal_river_fish", "drink_spring_flask", "healing_potion_superior", "battle_elixir_superior",
      "sturdy_arrows"]),
    ("underdark_seam_trader", "Quill Lampwright", "the_crystalline_underdark", 9, 97, "gnome", 38,
     "Down here you buy what you need before you need it. Nobody comes back up for a second trip.",
     ["meal_kodo_ribs", "drink_birch_wine", "healing_potion_superior", "mana_potion_superior",
      "flux_strong", "coal"]),
]


def pick_vendor(vendors, prof, recipe_name, level):
    """(vendor, how) for the vendor who should stock this recipe."""
    low = recipe_name.lower()
    for word, zone in PLACES.items():
        if word in low:
            here = [v for v in vendors if v["zone"] == zone]
            if here:
                for frag in TRADES.get(prof, ()):
                    match = [v for v in here if frag in v["vendor_id"]]
                    if match:
                        return min(match, key=lambda v: abs((v.get("gear_level") or 10) - level)), "place+trade"
                return min(here, key=lambda v: abs((v.get("gear_level") or 10) - level)), "place"
    for frag in TRADES.get(prof, ()):
        match = [v for v in vendors if frag in v["vendor_id"]]
        if match:
            return min(match, key=lambda v: abs((v.get("gear_level") or 10) - level)), "trade"
    if vendors:
        return min(vendors, key=lambda v: abs((v.get("gear_level") or 10) - level)), "level"
    return None, "none"


def main():
    from world.recipe_manager import all_recipes_by_source

    p = ROOT / "data/npcs/vendors.json"
    doc = json.loads(p.read_text())
    vendors = doc["vendors"]

    # ---------------------------------------------------------------- hidden sellers first,
    # so the attach pass below can also consider them as counters.
    existing = {v["vendor_id"] for v in vendors}
    for vid, name, zone, x, y, race, gear, greeting, stock in HIDDEN:
        if vid in existing:
            continue
        vendors.append({
            "vendor_id": vid, "name": name, "zone": zone, "x": x, "y": y,
            "tile_sprite": "npc", "sells": list(stock), "buys_from_player": True,
            "faction": "neutral", "gear_level": gear, "sells_gear": False,
            "race": race, "appearance_variant": 7, "greeting": greeting,
            "hidden": True,
        })
        print(f"  planted {name} in {zone} at ({x},{y})")

    # ---------------------------------------------------------------- attach the recipes
    wanted = all_recipes_by_source("vendor")
    counts, unmatched = {}, []
    for rid, (prof, r) in sorted(wanted.items(), key=lambda kv: kv[1][1].get("skill_required", 0)):
        skill = r.get("skill_required", 0)
        level = max(1, skill // 5)
        v, how = pick_vendor(vendors, prof, r.get("name", rid), level)
        if v is None:
            unmatched.append(rid)
            continue
        sells = v.setdefault("sells", [])
        if rid not in sells:
            sells.append(rid)
        counts[how] = counts.get(how, 0) + 1

    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    print(f"\n{len(wanted)} vendor-source recipes attached: "
          + ", ".join(f"{n} by {how}" for how, n in sorted(counts.items())))
    if unmatched:
        print(f"FAILED to place {len(unmatched)}: {unmatched}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
