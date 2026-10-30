#!/usr/bin/env python3
"""Creatures, kits, encounter table and loot for The Undercrust. Idempotent.

    PYTHONPATH=. python3 tools/build_undercrust_content.py

Same contract as the other content builders: the roster is READ FROM THE ZONE MODULE rather than
retyped, so a name that does not match fails here instead of the game raising on zone entry.

IT IS A CAVE, so it follows the cave rules rather than the dungeon ones (claude/dungeon_authoring_rules):

  * RANDOM TRASH. Kyle, 2026-10-22: "Hand placed mobs are only in full dungeons!" The zone sets
    fixed_spawns = False and the trash comes from the per-step encounter roll. There is no pack list
    here and there should not be one.
  * THE BOSS AND BOTH RARES SIT IN THE SAME TABLE AT WEIGHT 0. They are never rolled as filler; they
    are placed only via zone.boss_positions. A separate "bosses" key is silently ignored by the
    spawn code, which is the kind of thing that looks like it works.
  * FOUR ABILITIES for a 20+ boss, and the first must be a zero-cooldown damage.

THE CAVE IS 39-41, ABOVE ITS ZONE'S 35-40. The cave level rule allows that and the geography asks for
it: this is the deepest thing in the Flats and the Deep Shaft is most of the way across the pan.

THE SILITHID ROSTER TOPPED OUT AT 24 before this - the Broodspiral Queen. Everything here is new, which
is correct rather than inconvenient: this hive is older and bigger than the one in the Barrens and
should not be sharing its rank and file. Damage calibrated against what already exists near this level:
38-42 trash sits at 85-110 and bosses at 120-175.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, BOSS_MULT, kit_slug, merge_json, _detect_format,
    dmg, dot, debuff, buff, loot_audit,
)

LOOT = ROOT / "data/loot/undercrust_boss_loot.json"

ROSTER = {
    "Undercrust Swarmer":  ("vermin_sneaky",    39, 40, False),
    "Undercrust Ripper":   ("humanoid_warrior", 39, 41, False),
    "Hive Excavator":      ("humanoid_warrior", 40, 41, False),
    "Salt-Crusted Drone":  ("vermin_sneaky",    39, 41, False),
    "The Hollow Queen":    ("humanoid_caster",  41, 41, True),
    "Saltback":            ("humanoid_warrior", 40, 40, True),
    "Riftjaw":             ("vermin_sneaky",    40, 40, True),
}

KITSETS = {
    "Undercrust Swarmer": [
        dmg("Scything Limb", 92),
        dmg("Swarm Over", 78, cooldown=3),
        dot("Formic Burn", 26, 3, 3, school="nature"),
    ],
    "Undercrust Ripper": [
        dmg("Ripping Claw", 104),
        dmg("Open the Seam", 88, cooldown=4),
        debuff("Torn Open", 4, 3, {"defense_rating": -28}),
    ],
    "Hive Excavator": [
        dmg("Digging Claw", 98),
        dmg("Bring the Roof", 86, cooldown=5, is_aoe=True),
        buff("Dig In", 6, 4, {"defense_rating": 34}),
    ],
    "Salt-Crusted Drone": [
        dmg("Crusted Mandible", 94),
        dot("Salt in the Wound", 30, 3, 3),
        debuff("Grit", 4, 2, {"hit_rating": -22}),
    ],
    # ---- the boss and the two rares. Four abilities each, first a 0-cd damage.
    "The Hollow Queen": [
        dmg("The Queen's Reach", 158, boss_rework=1),
        dmg("Birthing Shriek", 134, cooldown=3, school="nature"),
        dmg("The Whole Brood Answers", 120, cooldown=5, school="nature", is_aoe=True),
        dot("Clutch of Eggs", 42, 4, 3, school="nature"),
    ],
    # The west rare: slow, armoured, and the thing the shallow galleries are built around.
    "Saltback": [
        dmg("Saltback's Weight", 148, boss_rework=1),
        dmg("Crust and Carapace", 126, cooldown=3),
        dmg("Shake the Gallery", 112, cooldown=5, is_aoe=True),
        buff("Plated Over", 7, 4, {"defense_rating": 46}),
    ],
    # The east rare: fast, and it hits much harder than it can take. The deep end introduces itself.
    "Riftjaw": [
        dmg("Riftjaw's Bite", 172, boss_rework=1),
        dmg("Out of the Floor", 146, cooldown=4),
        dot("Jaw Locked", 44, 3, 3),
        debuff("Dragged Under", 5, 2, {"agility": -36, "dodge_rating": -30}),
    ],
}

#: Bosses and rares at weight 0 - see the module docstring. The trash weights lean on the two
#: commonest types, with the excavators rarer because they are the ones doing the digging.
TABLE = {
    "Undercrust Swarmer": 7,
    "Undercrust Ripper": 6,
    "Salt-Crusted Drone": 5,
    "Hive Excavator": 3,
    "The Hollow Queen": 0,
    "Saltback": 0,
    "Riftjaw": 0,
}

POOLS = {
    "The Hollow Queen": (43, [
        ("The Hollow Crown", "head", "armor", "cloth", "int_caster"),
        ("Brood-Mother's Carapace", "chest", "armor", "mail", "agi_physical"),
        ("Clutchwarden's Grasp", "hands", "armor", "plate", "str_int_hybrid"),
        ("Chitinspine Rod", "main_hand", "weapon", "mace_1h", "spi_healer"),
    ]),
    "Saltback": (42, [
        ("Saltback's Plating", "shoulder", "armor", "plate", "str_physical"),
        ("Gallery-Shaker's Maul", "main_hand", "weapon", "mace_2h", "str_physical"),
        ("Crust-Walker's Treads", "feet", "armor", "leather", "agi_int_hybrid"),
        ("Undercrust Wrap", "waist", "armor", "cloth", "int_caster"),
    ]),
    "Riftjaw": (42, [
        ("Riftjaw's Mandible", "main_hand", "weapon", "dagger", "agi_physical"),
        ("Deep Shaft Jerkin", "chest", "armor", "leather", "agi_physical"),
        ("Tunnel-Sense Band", "wrist", "armor", "mail", "agi_int_hybrid"),
        ("Hollowed Bracer", "wrist", "armor", "cloth", "spi_healer"),
    ]),
}


def main():
    import tools.handbuilt_undercrust as U

    declared = set(U.TRASH) | set(U.BOSSES)
    unknown, unused = declared - set(ROSTER), set(ROSTER) - declared
    if unknown or unused:
        print("FAILED: the zone module and this file disagree about the roster")
        for n in sorted(unknown):
            print(f"  - the zone places '{n}', which nothing defines")
        for n in sorted(unused):
            print(f"  - this file defines '{n}', which no zone places")
        return 1
    # and the table must name exactly the same set, or a pinned boss raises on zone entry
    if set(TABLE) != declared:
        print(f"FAILED: the encounter table and the roster differ: "
              f"{sorted(set(TABLE) ^ declared)}")
        return 1
    print(f"roster agrees: {len(declared)} creatures, all in the table")

    creatures = {}
    for name, (template, lo, hi, is_boss) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": is_boss,
             "ability_kit": kit_slug(name)}
        if is_boss:
            e["boss_multiplier"] = BOSS_MULT
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    enc_raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(enc_raw)
    indent, newline = _detect_format(enc, enc_raw)
    caves = (enc.setdefault("zones", {})
                .setdefault("The Shimmering Flats", {})
                .setdefault("caves", {}))
    caves["The Undercrust"] = {"creatures": dict(TABLE)}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    print("  encounters.json: The Undercrust under 'The Shimmering Flats'")

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("The Undercrust's boss and two rares. Identity hand-authored in "
                      "tools/build_undercrust_content.py; stats from LootGenerator at rare budget.")}
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
            d = it.to_dict() if hasattr(it, "to_dict") else {}
            d["name"] = name
            d["item_id"] = "uc_" + name.lower().replace("'", "").replace(" ", "_")
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
