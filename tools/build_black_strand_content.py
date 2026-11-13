#!/usr/bin/env python3
"""Creatures, kits, encounter tables and rare loot for The Black Strand (50-53). Idempotent.

    PYTHONPATH=. python3 tools/build_black_strand_content.py

Kyle, 13 Nov 2026: "We will need quests, mobs, subzones etc." This is the mobs.

THREE FOOD CHAINS AND THE PEOPLE WHO WERE THROWN OUT. The zone is black sand with fungi and a hive
on it, and the tables say the same thing the ground does:

    the sand      basilisks, scorpions and bats - what lives on a shore with no sea
    the fungi     sporelings and shamblers, thickest in the Lantern Wood and at the Last Water
    the hive      silithid, in the Chitin Reach and the Royal Cell, and raiding west toward the wood
    the castouts  Dark Iron who were put outside Onyxhollow's gate and went back to the old diggings

AN OPEN ZONE: every creature is in a subzone table, each subzone's rare is at weight 0 (the rare
roll picks it, not the weights), and the gate is flagged safe - see CreatureManager.

Rares are written in FINAL form and carry boss_rework, like the Dry Deep's (see
tools/rework_boss_kits.raw_kit). All six stand on sturdy bodies: Kyle, same day, of a 1,324-health
rare: "Dont make the boss with 1300 HP".
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format,
    dmg, dot, debuff, buff, loot_audit,
)

LOOT = ROOT / "data/loot/black_strand_rare_loot.json"
ZONE = "The Black Strand"

#: name -> (template, lo, hi, boss multiplier or None)
ROSTER = {
    # ---- the sand
    "Ashdune Basilisk":      ("beast_large",      50, 51, None),
    "Blacksand Scorpion":    ("vermin_sneaky",    50, 51, None),
    "Strand Bat":            ("beast_fast",       50, 51, None),
    # ---- the fungi
    "Lantern Sporeling":     ("elemental_caster", 51, 52, None),
    "Gloomcap Trampler":     ("beast_large",      51, 52, None),
    "Blindwater Lurker":     ("aquatic_basic",    51, 52, None),
    # ---- the castouts
    "Castout Digger":        ("humanoid_warrior", 51, 52, None),
    "Castout Slagcaller":    ("humanoid_caster",  51, 52, None),
    "Castout Cutthroat":     ("humanoid_rogue",   51, 52, None),
    # ---- the hive
    "Hive Swarmer":          ("vermin_swarm",     52, 53, None),
    "Hive Reaver":           ("humanoid_warrior", 52, 53, None),
    "Hive Sandburrower":     ("beast_large",      52, 53, None),
    "Hive Resinspitter":     ("elemental_caster", 52, 53, None),
    # ---- the rares, one per place
    "Old Ashback the Basilisk":             ("beast_large",       51, 51, 1.9),
    "The Gloomcap Elder":         ("elemental_bruiser", 52, 52, 2.0),
    "The Last Lurker":            ("beast_large",       52, 52, 1.9),
    "Foreman Durn the Castout":   ("humanoid_warrior",  52, 52, 2.3),
    "Hive Champion Khix'ar":      ("beast_large",       53, 53, 2.0),
    "Hive Queen Zil'kesh":        ("beast_large",       53, 53, 2.3),
}


def enrage(name, ap, school="physical"):
    return dict(name=name, kind="buff", amount=0, cooldown=99, mana_cost=0, school=school,
                duration=30, self_only=True, hp_below=0.35, stat_mods={"attack_power": ap})


def stun(name, amount, cooldown=5, school="physical"):
    return dmg(name, amount, cooldown=cooldown, school=school, authored_mechanic="stun",
               rider={"effect": "debuff", "duration": 1, "is_stun": True, "stat_mods": {}})


def shield(name, absorb, school="physical"):
    return dict(name=name, kind="buff", amount=0, cooldown=6, mana_cost=0, school=school,
                duration=4, self_only=True, stat_mods={}, absorb=absorb, authored_mechanic="shield")


KITSETS = {
    "Ashdune Basilisk": [
        dmg("Stone Bite", 194),
        dmg("Tail Sweep", 168, cooldown=4),
        debuff("Glassy Stare", 5, 2, {"agility": -40}),
    ],
    "Blacksand Scorpion": [
        dmg("Pincer", 186),
        dot("Black Sting", 52, 3, 3, school="nature", dispel_type="poison"),
        debuff("Grit in the Joints", 5, 3, {"dodge_rating": -36}),
    ],
    "Strand Bat": [
        dmg("Needle Teeth", 182),
        dmg("Out of the Dark", 160, cooldown=3),
        debuff("Shriek", 5, 2, {"hit_rating": -30}),
    ],
    "Lantern Sporeling": [
        dmg("Spore Burst", 190, school="nature"),
        dot("Lit From Inside", 54, 3, 3, school="nature", dispel_type="poison"),
        debuff("Soft Light", 5, 3, {"spell_power": -44, "attack_power": -44}),
    ],
    "Gloomcap Trampler": [
        dmg("Heavy Cap", 200),
        dmg("Trample the Ring", 172, cooldown=4, is_aoe=True),
        buff("Rooted", 6, 4, {"armor": 90}),
    ],
    "Blindwater Lurker": [
        dmg("Cold Grab", 196, school="frost"),
        dmg("Pull Under", 170, cooldown=3, school="frost"),
        debuff("Numb", 5, 3, {"agility": -44}),
    ],
    "Castout Digger": [
        dmg("Pick Swing", 198),
        dmg("Bring the Shoring Down", 170, cooldown=4, is_aoe=True),
        buff("Nothing Left to Lose", 6, 4, {"attack_power": 60}),
    ],
    "Castout Slagcaller": [
        dmg("Slag Bolt", 192, school="fire"),
        dot("Cinders in the Seams", 56, 3, 3, school="fire"),
        debuff("Brand of the Unnamed", 5, 3, {"armor": -84}),
    ],
    "Castout Cutthroat": [
        dmg("Shiv", 188),
        dot("Opened Up", 54, 3, 3),
        debuff("Hamstring", 5, 2, {"dodge_rating": -40}),
    ],
    "Hive Swarmer": [
        dmg("Scything Limb", 190),
        dmg("Swarm Over", 164, cooldown=3),
        dot("Formic Burn", 54, 3, 3, school="nature", dispel_type="poison"),
    ],
    "Hive Reaver": [
        dmg("Reaving Claw", 204),
        dmg("Open the Shell", 176, cooldown=4),
        debuff("Torn Plate", 5, 3, {"armor": -92}),
    ],
    "Hive Sandburrower": [
        dmg("Up Through the Sand", 206),
        dmg("Collapse the Tunnel", 176, cooldown=5, is_aoe=True),
        buff("Dug In", 6, 4, {"armor": 96}),
    ],
    "Hive Resinspitter": [
        dmg("Resin Spit", 196, school="nature"),
        dot("Setting Amber", 56, 3, 3, school="nature"),
        debuff("Stuck Fast", 5, 2, {"agility": -48, "dodge_rating": -36}),
    ],
    # ---------------------------------------------------------------- the rares, final form
    # The oldest thing on the sand. It turns you to stone a little at a time.
    "Old Ashback the Basilisk": [
        dmg("Ashback's Jaws", 436, boss_rework=1),
        stun("The Long Stare", 566),
        dmg("Shed the Ash", 366, cooldown=4, is_aoe=True),
        dot("Turning to Stone", 142, 5, 4, school="nature", dispel_type="curse",
            authored_mechanic="curse"),
        enrage("Older Than the Sand", 138),
    ],
    # A mushroom the size of a house that has been lighting the wood since before the hive came.
    "The Gloomcap Elder": [
        dmg("The Elder's Weight", 448, school="nature", boss_rework=1),
        dmg("Light the Whole Wood", 376, cooldown=4, school="nature", is_aoe=True),
        dot("Spores in the Lungs", 148, 5, 4, school="nature", dispel_type="poison",
            authored_mechanic="curse"),
        shield("Layer on Layer", 820, school="nature"),
        enrage("The Lights Go Red", 142, school="nature"),
    ],
    # What stayed in the water when the water left.
    "The Last Lurker": [
        dmg("The Lurker's Reach", 444, school="frost", boss_rework=1),
        stun("Held Under", 574, school="frost"),
        dmg("The Water Stands Up", 372, cooldown=4, school="frost", is_aoe=True),
        dmg("Cold That Stayed", 392, cooldown=5, school="frost",
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"agility": -60}}),
        enrage("Nowhere Else to Go", 140, school="frost"),
    ],
    # He ran the old working, was put out of the gate for what he did there, and went back to it.
    "Foreman Durn the Castout": [
        dmg("Foreman's Maul", 452, boss_rework=1),
        stun("Knock Them Down the Shaft", 584),
        dmg("Slag Tip", 380, cooldown=4, school="fire", is_aoe=True),
        shield("Old Company Plate", 840),
        enrage("They Took My Name", 146),
    ],
    # The hive's raider, the one the fingers of resin toward the wood belong to.
    "Hive Champion Khix'ar": [
        dmg("Khix'ar's Scythes", 462, boss_rework=1),
        dmg("Through the Line", 392, cooldown=3,
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"armor": -120}}),
        dmg("Call the Raid", 384, cooldown=5, is_aoe=True),
        dot("Formic Flood", 152, 5, 4, school="nature", dispel_type="poison",
            authored_mechanic="curse"),
        enrage("For the Queen", 150),
    ],
    # The end of the zone, in the Royal Cell.
    "Hive Queen Zil'kesh": [
        dmg("The Queen's Reach", 478, boss_rework=1),
        stun("Birthing Shriek", 612, school="nature"),
        dmg("The Whole Hive Answers", 400, cooldown=4, school="nature", is_aoe=True),
        dot("Clutch in the Wound", 158, 5, 4, school="nature", dispel_type="poison",
            authored_mechanic="curse"),
        shield("Sealed in Amber", 900, school="nature"),
        enrage("The Cell Wakes", 156, school="nature"),
    ],
}

RARES = {n for n, r in ROSTER.items() if r[3]}

TABLE = {
    "open_zone": {
        "name": ZONE,
        "creatures": {"Ashdune Basilisk": 5, "Blacksand Scorpion": 5, "Strand Bat": 4,
                      "Lantern Sporeling": 2, "Hive Swarmer": 2},
    },
    "subzones": {
        # The foot of the stair. The lookout keeps a brazier lit and two people stand by it.
        "The Bottom Step": {"name": "The Bottom Step", "safe": True, "creatures": {}},
        "The Ash Dunes": {
            "name": "The Ash Dunes",
            "creatures": {"Ashdune Basilisk": 5, "Blacksand Scorpion": 5, "Strand Bat": 3,
                          "Castout Cutthroat": 2, "Old Ashback the Basilisk": 0},
        },
        "The Lantern Wood": {
            "name": "The Lantern Wood",
            "creatures": {"Lantern Sporeling": 6, "Gloomcap Trampler": 5, "Strand Bat": 2,
                          "Hive Swarmer": 2, "The Gloomcap Elder": 0},
        },
        "The Last Water": {
            "name": "The Last Water",
            "creatures": {"Blindwater Lurker": 6, "Lantern Sporeling": 4, "Gloomcap Trampler": 2,
                          "Hive Resinspitter": 2, "The Last Lurker": 0},
        },
        # The gate. Nothing spawns on the road in front of a Dark Iron watchtower.
        "Onyxhollow Gate": {"name": "Onyxhollow Gate", "safe": True, "creatures": {}},
        "The Castout Diggings": {
            "name": "The Castout Diggings",
            "creatures": {"Castout Digger": 6, "Castout Slagcaller": 4, "Castout Cutthroat": 4,
                          "Foreman Durn the Castout": 0},
        },
        "The Chitin Reach": {
            "name": "The Chitin Reach",
            "creatures": {"Hive Reaver": 5, "Hive Swarmer": 5, "Hive Sandburrower": 4,
                          "Hive Resinspitter": 3, "Hive Champion Khix'ar": 0},
        },
        "The Royal Cell": {
            "name": "The Royal Cell",
            "creatures": {"Hive Reaver": 6, "Hive Resinspitter": 4, "Hive Sandburrower": 4,
                          "Hive Queen Zil'kesh": 0},
        },
    },
}

#: (item level, [(name, slot, kind, type, stat template)])
POOLS = {
    "Old Ashback the Basilisk": (55, [
        ("Ashback Scale Pauldrons", "shoulder", "armor", "mail", "agi_physical"),
        ("Stare-Proof Visor", "head", "armor", "plate", "str_physical"),
        ("Ashdune Wraps", "wrist", "armor", "cloth", "int_caster"),
        ("Petrified Fang", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
    "The Gloomcap Elder": (56, [
        ("Elder's Cap", "head", "armor", "cloth", "spi_healer"),
        ("Lanternlit Jerkin", "chest", "armor", "leather", "agi_int_hybrid"),
        ("Mycelium Girdle", "waist", "armor", "mail", "agi_int_hybrid"),
        ("Stem of the Elder", "main_hand", "weapon", "staff", "int_caster"),
    ]),
    "The Last Lurker": (56, [
        ("Last Water Treads", "feet", "armor", "leather", "agi_physical"),
        ("Drowned Shore Legplates", "legs", "armor", "plate", "str_int_hybrid"),
        ("Stillwater Cowl", "head", "armor", "cloth", "int_caster"),
        ("The Lurker's Hook", "main_hand", "weapon", "axe_1h", "str_physical"),
    ]),
    "Foreman Durn the Castout": (56, [
        ("Old Company Breastplate", "chest", "armor", "plate", "str_physical"),
        ("Castout's Chain Hood", "head", "armor", "mail", "agi_physical"),
        ("Shaft-Boss Gloves", "hands", "armor", "leather", "agi_physical"),
        ("Durn's Maul", "main_hand", "weapon", "mace_2h", "str_physical"),
    ]),
    "Hive Champion Khix'ar": (57, [
        ("Khix'ar's Carapace", "chest", "armor", "mail", "agi_physical"),
        ("Raider's Chitin Greaves", "legs", "armor", "leather", "agi_int_hybrid"),
        ("Resin-Set Bracers", "wrist", "armor", "plate", "str_int_hybrid"),
        ("Scythe of the Raid", "main_hand", "weapon", "sword_2h", "str_physical"),
    ]),
    "Hive Queen Zil'kesh": (58, [
        ("The Amber Crown", "head", "armor", "cloth", "int_caster"),
        ("Royal Cell Pauldrons", "shoulder", "armor", "plate", "str_physical"),
        ("Brood-Silk Leggings", "legs", "armor", "cloth", "spi_healer"),
        ("Queen's Carapace Grips", "hands", "armor", "mail", "agi_int_hybrid"),
        ("Zil'kesh's Ovipositor", "main_hand", "weapon", "wand", "int_caster"),
        ("Hivemind Sceptre", "main_hand", "weapon", "mace_1h", "spi_healer"),
    ]),
}


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_black_strand as M

    declared = {c[0] for c in M.CHAMBERS}
    if set(TABLE["subzones"]) != declared:
        print(f"FAILED: subzones disagree with the zone: {sorted(set(TABLE['subzones']) ^ declared)}")
        return 1
    named = set(TABLE["open_zone"]["creatures"])
    for s in TABLE["subzones"].values():
        named |= set(s["creatures"])
    if named != set(ROSTER) or set(KITSETS) != set(ROSTER):
        print(f"FAILED: tables, roster and kits differ: {sorted(named ^ set(ROSTER))} "
              f"{sorted(set(KITSETS) ^ set(ROSTER))}")
        return 1
    if RARES & set(TABLE["open_zone"]["creatures"]) or set(POOLS) != RARES:
        print("FAILED: a rare is in the open table, or the pools do not match the rares")
        return 1

    creatures = {}
    for name, (template, lo, hi, mult) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult),
             "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    enc.setdefault("zones", {})[ZONE] = TABLE
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    print(f"  encounters.json: {ZONE}, open zone + {len(TABLE['subzones'])} subzones (the gate safe)")

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("The Black Strand's six rares. Identity hand-authored in "
                      "tools/build_black_strand_content.py; stats from LootGenerator at rare budget.")}
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
            d["item_id"] = "bst_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_")
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
