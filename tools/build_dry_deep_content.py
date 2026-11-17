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

THE OPTIONAL THREE (Kyle, 16 Nov 2026: "more tunnels, more places, optional bosses round the edge"). Off every
route a quest walks you along, at the edge of the recut map, each with its own loot and a quest that names it:

  THE SALT WIDOW - the first Saltbone Revenant, in the Salt Galleries. A caster: a frost bolt, a salt curse on
      the healer that wants dispelling, and a wail that hits everyone.
  COIL OF THE OLD SEA - something that swam here when it was a sea, on the Fossil Shelf, and did not die with
      it. Constricts (a stun), and its bite bleeds.
  MOTHER OF CRAWLERS - where the Limestone Crawlers come from, on the Brood Shelf. She calls her brood, and
      they come.

WRITES ONLY WHAT IS MISSING. The first two kits have been added to since they were written here (the boss-turn
and boss-AoE passes append to them), so a re-run leaves an existing creature, kit and loot pool alone and
adds the new ones. --rewrite rewrites all of it, which undoes those passes: do not.
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
    # the optional three
    "The Salt Widow":          ("undead_caster",     46, 1.8),
    "Coil of the Old Sea":     ("beast_large",       47, 1.9),
    "Mother of Crawlers":      ("beast_large",       46, 1.8),
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
    "The Salt Widow": [
        # a caster's numbers: the undead_caster template's spell scaling already carries her (authored like a
        # bruiser she measured at 70% of T an action, the clamp's ceiling)
        dmg("Brine Bolt", 260, school="frost", boss_rework=1),
        dot("Salt in the Wound", 84, 5, 5, school="shadow", dispel_type="curse",
            authored_mechanic="curse"),
        dmg("The Widow's Wail", 200, cooldown=5, school="shadow", is_aoe=True),
        dmg("Dried to the Bone", 222, cooldown=4, school="frost",
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"attack_speed": -44}}),
        enrage("Nothing Left to Keep", 104, school="frost"),
    ],
    "Coil of the Old Sea": [
        dmg("Old Sea Bite", 402, boss_rework=1),
        dmg("Constrict", 498, cooldown=5, authored_mechanic="stun",
            rider={"effect": "debuff", "duration": 1, "is_stun": True, "stat_mods": {}}),
        dot("Fossil Teeth", 126, 4, 4, dispel_type="bleed", authored_mechanic="bleed"),
        dmg("Tail Through the Shelf", 312, cooldown=5, is_aoe=True),
        enrage("The Sea Comes Back", 128),
    ],
    "Mother of Crawlers": [
        dmg("Brood Mandible", 378, boss_rework=1),
        dict(name="Call the Brood", kind="summon", amount=0, cooldown=7, mana_cost=0, school="physical",
             duration=0, authored_mechanic="summon",
             summon={"name": "Limestone Crawler", "template": "vermin_sneaky", "kit": "limestone_crawler",
                     "count": 2, "level_offset": -1, "max_alive": 3, "max_casts": 2}),
        dot("Limestone Acid", 120, 5, 4, school="nature", dispel_type="poison",
            authored_mechanic="curse"),
        dmg("Up Out of the Floor", 292, cooldown=5, is_aoe=True),
        enrage("Every Last One", 116),
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
    "The Salt Widow": (50, [
        ("Salt-Woven Veil", "head", "armor", "cloth", "int_caster"),
        ("Widow's Brine Wraps", "wrist", "armor", "mail", "spi_healer"),
        ("Saltbound Girdle", "waist", "armor", "plate", "str_physical"),
        ("The Widow's Rod", "main_hand", "weapon", "staff", "int_caster"),
    ]),
    "Coil of the Old Sea": (51, [
        ("Coilscale Spaulders", "shoulder", "armor", "mail", "agi_int_hybrid"),
        ("Old Sea Treads", "feet", "armor", "leather", "agi_physical"),
        ("Fossil-Plate Gauntlets", "hands", "armor", "plate", "str_int_hybrid"),
        ("Spine of the Old Sea", "main_hand", "weapon", "polearm", "str_physical"),
    ]),
    "Mother of Crawlers": (50, [
        ("Nestsilk Robe", "chest", "armor", "cloth", "spi_healer"),
        ("Crawlerhide Cowl", "head", "armor", "leather", "agi_int_hybrid"),
        ("Broodshell Legguards", "legs", "armor", "mail", "str_physical"),
        ("Mother's Mandible", "main_hand", "weapon", "sword_1h", "agi_physical"),
    ]),
}


def main():
    import tools.handbuilt_dry_deep as D
    if set(ROSTER) != set(D.BOSSES):
        print(f"FAILED: the zone places {sorted(D.BOSSES)}, this file defines {sorted(ROSTER)}")
        return 1

    rewrite = "--rewrite" in sys.argv
    have_c = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    have_k = json.loads(KITS.read_text(encoding="utf-8"))["kits"]
    creatures = {n: {"template": t, "level_range": [lv, lv], "is_boss": True,
                     "ability_kit": kit_slug(n), "boss_multiplier": mult}
                 for n, (t, lv, mult) in ROSTER.items() if rewrite or n not in have_c}
    kits = {kit_slug(n): k for n, k in KITSETS.items() if rewrite or kit_slug(n) not in have_k}
    if creatures:
        merge_json(CREATURES, "creatures", creatures, "creatures.json")
    if kits:
        merge_json(KITS, "kits", kits, "ability_kits.json")
    old = json.loads(LOOT.read_text(encoding="utf-8")) if LOOT.exists() else {}

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("The Dry Deep's boss and rare. Identity hand-authored in "
                      "tools/build_dry_deep_content.py; stats from LootGenerator at rare budget.")}
    rows = []
    for boss, (ilvl, items) in POOLS.items():
        if boss in old and not rewrite:
            out[boss] = old[boss]
            rows.extend(items)
            continue
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
