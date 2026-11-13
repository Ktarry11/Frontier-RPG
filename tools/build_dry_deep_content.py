#!/usr/bin/env python3
"""The Dry Deep's boss and rare get kits and loot of their own. Idempotent.

    PYTHONPATH=. python3 tools/build_dry_deep_content.py

When the cave was dug (898fd8c) its two named creatures were stood up on borrowed kits so the map
could be walked the same day: The Weight of the Floor fought as the Glasswall Warden - a FIRE
elemental, under a desert, in a room called the Drained Sea - and Old Dry-Eye as the Wide Sink
Mother. Neither dropped anything. This gives each its own.

Both kits are written in their FINAL form and carry boss_rework on the first ability, which is
what tools/rework_boss_kits.py reads as "authored finished, do not rework" (see raw_kit there).
Amounts are set against the neighbours at the same level, the reworked Glasswall Warden (46) and
Underlight (47), not against the raw numbers in tools/monster_kits.py, which are pre-rework.

  THE WEIGHT OF THE FLOOR - a piece of the roof that came down whole and did not lie still. Slow
      and heavy: a stun to answer, a shield to burn through, and it gets worse when it cracks.
  OLD DRY-EYE - blind, on a beach at the bottom of a desert. Fast, hits the back row, and leaves a
      poison somebody has to take off.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, kit_slug, merge_json, dmg, dot, loot_audit,
)

LOOT = ROOT / "data/loot/dry_deep_boss_loot.json"

#: name -> (template, level, boss multiplier). Unchanged from 898fd8c except the kit.
ROSTER = {
    "The Weight of the Floor": ("elemental_bruiser", 47, 2.0),
    "Old Dry-Eye":             ("beast_large",       46, 1.8),   # vermin_sneaky left it at 1,324 health (Kyle: no)
}


def enrage(name, ap, school="physical"):
    return dict(name=name, kind="buff", amount=0, cooldown=99, mana_cost=0, school=school,
                duration=30, self_only=True, hp_below=0.35, stat_mods={"attack_power": ap})


KITSETS = {
    "The Weight of the Floor": [
        dmg("The Floor's Weight", 412, boss_rework=1),
        dmg("Comes Down Whole", 536, cooldown=5, authored_mechanic="stun",
            rider={"effect": "debuff", "duration": 1, "is_stun": True, "stat_mods": {}}),
        dmg("The Roof Lets Go", 348, cooldown=4, is_aoe=True),
        dict(name="Settled", kind="buff", amount=0, cooldown=6, mana_cost=0, school="physical",
             duration=4, self_only=True, stat_mods={}, absorb=750, authored_mechanic="shield"),
        enrage("Nothing Holding It Up", 132),
    ],
    "Old Dry-Eye": [
        dmg("Dry-Eye's Snap", 384, boss_rework=1),
        dmg("Hears You Breathe", 326, cooldown=4,
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"dodge_rating": -44}}),
        dot("Brine Rot", 132, 5, 4, school="nature", dispel_type="poison",
            authored_mechanic="curse"),
        dmg("Thrash in the Shallows", 298, cooldown=5, is_aoe=True),
        enrage("Blind and Cornered", 112),
    ],
}

#: (item level, [(name, slot, kind, type, stat template)]). Two of each armour class across the
#: pair and two different weapons - loot_audit's rule, checked over the set.
POOLS = {
    "The Weight of the Floor": (51, [
        ("Keystone Pauldrons", "shoulder", "armor", "plate", "str_physical"),
        ("Roofbearer's Hauberk", "chest", "armor", "mail", "agi_int_hybrid"),
        ("Drained Sea Leggings", "legs", "armor", "leather", "agi_physical"),
        ("Mantle of the Long Dark", "shoulder", "armor", "cloth", "int_caster"),
        ("The Floor's Share", "main_hand", "weapon", "mace_2h", "str_physical"),
    ]),
    "Old Dry-Eye": (50, [
        ("Old Shoreline Greaves", "feet", "armor", "plate", "str_int_hybrid"),
        ("Brine-Stiff Coif", "head", "armor", "mail", "agi_physical"),
        ("Blindfish Grips", "hands", "armor", "leather", "agi_int_hybrid"),
        ("Tideless Sash", "waist", "armor", "cloth", "spi_healer"),
        ("Dry-Eye's Tooth", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
}


def main():
    import tools.handbuilt_dry_deep as D
    if set(ROSTER) != set(D.BOSSES):
        print(f"FAILED: the zone places {sorted(D.BOSSES)}, this file defines {sorted(ROSTER)}")
        return 1

    creatures = {n: {"template": t, "level_range": [lv, lv], "is_boss": True,
                     "ability_kit": kit_slug(n), "boss_multiplier": mult}
                 for n, (t, lv, mult) in ROSTER.items()}
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("The Dry Deep's boss and rare. Identity hand-authored in "
                      "tools/build_dry_deep_content.py; stats from LootGenerator at rare budget.")}
    rows = []
    for boss, (ilvl, items) in POOLS.items():
        built = []
        for (name, slot, kind, atype, template) in items:
            if kind == "armor":
                it = gen.generate_armor_piece(slot, atype, template, ilvl, "rare")
            else:
                it = gen.generate_weapon(slot, atype, template, ilvl, "rare", strict=True)
            if it is None:
                print(f"FAILED: the generator would not build {name}")
                return 1
            d = it.to_dict()
            d["name"] = name
            d["item_id"] = "dd_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_")
            built.append(d)
            rows.append((name, slot, kind, atype, template))
        out[boss] = built
    problems = loot_audit(rows)
    if problems:
        print("\nFAILED - fix the pools, not the check:")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {LOOT.relative_to(ROOT)}: {len(POOLS)} pools, {len(rows)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
