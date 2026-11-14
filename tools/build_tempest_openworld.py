#!/usr/bin/env python3
"""Open-world creatures, rares, encounter tables and rare loot for Tempest Isle. Idempotent.

    PYTHONPATH=. python3 tools/build_tempest_openworld.py

Both of the isle's open zones were built, dressed and given their dungeons, and had NOTHING
living in them: Tempest Shallows (52-55) and The Ashen Reach (55-58) each had a dungeon table and
no open-zone table at all. Kyle, 13 Nov 2026: "Lets finish tempest isle first."

WHAT LIVES WHERE. The isle is Un'Goro: jungle, with a volcano standing in it.

  TEMPEST SHALLOWS, the south
    the Green Belt          raptors, panthers and gorillas: jungle, and nothing in it is afraid
    Khaz Varun's Gate       Dark Iron who never left the dead city and squat in its gatehouse
    the Scoured Slope       ash and scree on the volcano's shoulder: fire, scorpions, whelps
    the Tempest Shallows    the wadeable islets: snappers, crabs, and murlocs picking the wrecks
    Ashclaim Landing        safe - the camp at the jetty

  THE ASHEN REACH, the north
    the Scoured Coast       crabs, oozes round the steam vents, and naga after the same wrecks
    the Cinder Flats        the burnt ring at the volcano's foot: fire elementals and what eats ash
    the Emberdeep Approach  what comes out of the door when nobody is holding it shut
    the Ashclaim Works      safe - the works are a hub with people standing at them
    Cinderwharf Gate        safe - the road in front of a town gate

AN OPEN ZONE: every creature is in a table, each subzone's rare is at weight 0 (the rare roll
picks it, not the weights), and rares are in subzone tables only. The dungeon tables under
"caves" are left exactly as they are.

Rares are written in FINAL form and carry boss_rework, on sturdy bodies (Kyle: "Dont make the
boss with 1300 HP"). Their loot is item level = level + 3, the isle's offset.
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

LOOT = ROOT / "data/loot/tempest_isle_rare_loot.json"
SHALLOWS, REACH = "Tempest Shallows", "The Ashen Reach"

#: name -> (template, lo, hi, boss multiplier or None)
ROSTER = {
    # ================= TEMPEST SHALLOWS =================
    "Greenbelt Raptor":          ("beast_fast",       52, 53, None),
    "Canopy Panther":            ("beast_fast",       52, 53, None),
    "Ashfur Gorilla":            ("beast_large",      53, 54, None),
    "Gate-Squatter Brawler":     ("humanoid_warrior", 53, 54, None),
    "Gate-Squatter Ashpreacher": ("humanoid_caster",  53, 54, None),
    "Rubble Basilisk":           ("beast_large",      53, 54, None),
    "Cinderslope Flame Spirit":  ("elemental_caster", 54, 55, None),
    "Ashscree Scorpion":         ("vermin_sneaky",    54, 55, None),
    "Ashwing Whelp":             ("beast_fast",       54, 55, None),
    "Shallows Snapper":          ("aquatic_basic",    53, 54, None),
    "Bargebreaker Crab":         ("beast_large",      53, 54, None),
    "Wreckpicker Murloc":        ("humanoid_rogue",   54, 55, None),
    # ================= THE ASHEN REACH =================
    "Tarfoot Gorilla":           ("beast_large",      55, 56, None),
    "Scourcoast Crab":           ("beast_large",      55, 56, None),
    "Stormscale Naga Raider":    ("humanoid_warrior", 55, 56, None),
    "Steamvent Ooze":            ("elemental_bruiser", 55, 56, None),
    "Scoria Fire Elemental":     ("elemental_caster", 56, 57, None),
    "Ashplain Basilisk":         ("beast_large",      56, 57, None),
    "Sulphur Raptor":            ("beast_fast",       56, 57, None),
    "Ventborn Flame Spirit":     ("elemental_caster", 57, 58, None),
    "Crag Earth Elemental":      ("elemental_bruiser", 57, 58, None),
    "Calderaborn Drake":         ("beast_large",      57, 58, None),
    # ================= the rares, one per place =================
    "Mother Canopy":             ("beast_large",       53, 53, 1.9),
    "Borrik the Unhoused":       ("humanoid_warrior",  54, 54, 2.3),
    "Sootwing":                  ("beast_large",       55, 55, 2.0),
    "The Barge-Eater":           ("beast_large",       54, 54, 2.0),
    "Wreck-Captain Vess'ira":    ("humanoid_warrior",  56, 56, 2.3),
    "Old Scoria":                ("elemental_bruiser", 57, 57, 2.0),
    "Karrath the Ventlord":      ("elemental_bruiser", 58, 58, 2.2),
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
    # ---------------------------------------------------------------- the Shallows
    "Greenbelt Raptor": [
        dmg("Hooked Claw", 200),
        dmg("Run It Down", 172, cooldown=3),
        dot("Open Flank", 56, 3, 3),
    ],
    "Canopy Panther": [
        dmg("Drop From the Branch", 202),
        dmg("Rake", 172, cooldown=3),
        debuff("Hunted", 5, 2, {"dodge_rating": -40}),
    ],
    "Ashfur Gorilla": [
        dmg("Both Fists", 210),
        dmg("Throw the Log", 180, cooldown=4, is_aoe=True),
        buff("Chest Beating", 6, 4, {"attack_power": 64}),
    ],
    "Gate-Squatter Brawler": [
        dmg("Rusted Pick", 208),
        dmg("Shoulder Through", 178, cooldown=4),
        buff("This Is My Gate", 6, 4, {"armor": 98}),
    ],
    "Gate-Squatter Ashpreacher": [
        dmg("Handful of Embers", 202, school="fire"),
        dot("Ash in the Eyes", 58, 3, 3, school="fire"),
        debuff("Sermon to the Rubble", 5, 3, {"spell_power": -46, "attack_power": -46}),
    ],
    "Rubble Basilisk": [
        dmg("Stone Bite", 206),
        dmg("Tail Sweep", 176, cooldown=4),
        debuff("Glassy Stare", 5, 2, {"agility": -44}),
    ],
    "Cinderslope Flame Spirit": [
        dmg("Lick of Flame", 206, school="fire"),
        dot("Catch Alight", 60, 3, 3, school="fire"),
        dmg("Flare Up", 178, cooldown=4, school="fire", is_aoe=True),
    ],
    "Ashscree Scorpion": [
        dmg("Pincer", 202),
        dot("Ash Sting", 58, 3, 3, school="nature", dispel_type="poison"),
        debuff("Grit in the Joints", 5, 3, {"dodge_rating": -40}),
    ],
    "Ashwing Whelp": [
        dmg("Snap", 204),
        dmg("Cough of Soot", 176, cooldown=3, school="fire"),
        debuff("Smoke in the Face", 5, 2, {"hit_rating": -32}),
    ],
    "Shallows Snapper": [
        dmg("Snap Shut", 204),
        dmg("Drag Into the Wash", 174, cooldown=4, school="frost"),
        buff("Pull In", 6, 4, {"armor": 104}),
    ],
    "Bargebreaker Crab": [
        dmg("Crush", 208),
        dmg("Sidelong Rush", 176, cooldown=3),
        debuff("Cracked Greave", 5, 3, {"armor": -96}),
    ],
    "Wreckpicker Murloc": [
        dmg("Salvage Hook", 204),
        dot("Rusty Gash", 58, 3, 3),
        debuff("Net Over the Head", 5, 2, {"agility": -46, "dodge_rating": -36}),
    ],
    # ---------------------------------------------------------------- the Reach
    "Tarfoot Gorilla": [
        dmg("Tarred Fists", 218),
        dmg("Uproot", 186, cooldown=4, is_aoe=True),
        buff("Drumming", 6, 4, {"attack_power": 68}),
    ],
    "Scourcoast Crab": [
        dmg("Black Claw", 216),
        dmg("Scuttle and Pinch", 184, cooldown=3),
        debuff("Split Shell-Plate", 5, 3, {"armor": -102}),
    ],
    "Stormscale Naga Raider": [
        dmg("Wrecker's Trident", 220),
        dmg("Coil and Crush", 188, cooldown=4),
        debuff("Dragged Down the Shingle", 5, 2, {"dodge_rating": -44}),
    ],
    "Steamvent Ooze": [
        dmg("Scalding Slop", 214, school="fire"),
        dot("Boiling On", 62, 3, 3, school="fire"),
        buff("Thickens", 6, 4, {"armor": 110}),
    ],
    "Scoria Fire Elemental": [
        dmg("Cinder Blast", 220, school="fire"),
        dot("Glowing Clinker", 64, 3, 3, school="fire"),
        dmg("Throw Sparks", 188, cooldown=4, school="fire", is_aoe=True),
    ],
    "Ashplain Basilisk": [
        dmg("Ashen Bite", 222),
        dmg("Tail Sweep", 190, cooldown=4),
        debuff("Dull Stare", 5, 2, {"agility": -50}),
    ],
    "Sulphur Raptor": [
        dmg("Yellow Claw", 220),
        dmg("Pack Rush", 188, cooldown=3),
        dot("Sulphur Burn", 64, 3, 3, school="nature", dispel_type="poison"),
    ],
    "Ventborn Flame Spirit": [
        dmg("Vent Flare", 226, school="fire"),
        dot("Still Burning", 66, 3, 3, school="fire"),
        debuff("Heat Haze", 5, 3, {"hit_rating": -36}),
    ],
    "Crag Earth Elemental": [
        dmg("Basalt Fist", 232),
        dmg("Shake the Slope", 196, cooldown=5, is_aoe=True),
        buff("Set Like Rock", 6, 4, {"armor": 120}),
    ],
    "Calderaborn Drake": [
        dmg("Drake's Bite", 230),
        dmg("Smoke Breath", 196, cooldown=4, school="fire", is_aoe=True),
        debuff("Wing Buffet", 5, 2, {"dodge_rating": -48}),
    ],
    # ---------------------------------------------------------------- the rares, final form
    # The oldest cat in the Green Belt. Every panther on the isle is hers.
    "Mother Canopy": [
        dmg("Mother's Claws", 470, boss_rework=1),
        dmg("From Above", 398, cooldown=3,
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"dodge_rating": -70}}),
        dot("Laid Open", 154, 5, 4, authored_mechanic="curse"),
        dmg("Call the Litter", 390, cooldown=5, is_aoe=True),
        enrage("Cornered at the Den", 152),
    ],
    # A Dark Iron who stayed at the gate of the dead city and decided it was his.
    "Borrik the Unhoused": [
        dmg("The Door-Bar", 482, boss_rework=1),
        stun("Bar the Way", 618),
        dmg("Bring the Lintel Down", 402, cooldown=4, is_aoe=True),
        shield("Gatehouse Plate", 920),
        enrage("Nobody Else Kept It", 158),
    ],
    # A whelp that lived long enough on the slope to stop being one.
    "Sootwing": [
        dmg("Sootwing's Bite", 490, school="fire", boss_rework=1),
        dmg("Black Breath", 410, cooldown=4, school="fire", is_aoe=True),
        dot("Soot in the Lungs", 162, 5, 4, school="fire", authored_mechanic="curse"),
        dmg("Stoop", 420, cooldown=5,
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"armor": -130}}),
        enrage("The Slope Is Mine", 160, school="fire"),
    ],
    # The crab that sank the goblin barge on the islets, and has been eating it since.
    "The Barge-Eater": [
        dmg("The Big Claw", 484, boss_rework=1),
        stun("Pinned to the Hull", 620),
        dmg("Thrash in the Shallows", 404, cooldown=4, is_aoe=True),
        shield("Barnacle and Iron", 940),
        enrage("Still Hungry", 158),
    ],
    # She came for the same wrecks the Ashclaim did, and she got to them first.
    "Wreck-Captain Vess'ira": [
        dmg("Vess'ira's Trident", 500, boss_rework=1),
        dmg("Run Them Through", 426, cooldown=3,
            rider={"effect": "debuff", "duration": 3, "stat_mods": {"armor": -136}}),
        dmg("The Tide Comes In", 416, cooldown=4, school="frost", is_aoe=True),
        dot("Salt in the Wound", 166, 5, 4, school="nature", dispel_type="poison",
            authored_mechanic="curse"),
        enrage("Mine by Right of Salvage", 164),
    ],
    # The first thing that crawled out when the Cinder Flats burned.
    "Old Scoria": [
        dmg("Scoria's Weight", 512, school="fire", boss_rework=1),
        stun("Buried in Clinker", 656, school="fire"),
        dmg("The Flats Burn Again", 428, cooldown=4, school="fire", is_aoe=True),
        shield("Crust Over", 980, school="fire"),
        enrage("Split to the Core", 168, school="fire"),
    ],
    # It stands outside the Emberdeep's door, and it came from inside.
    "Karrath the Ventlord": [
        dmg("Karrath's Brand", 524, school="fire", boss_rework=1),
        dmg("Open Every Vent", 438, cooldown=4, school="fire", is_aoe=True),
        dot("Branded", 172, 5, 4, school="fire", authored_mechanic="curse"),
        stun("The Ground Lets Go", 672, school="fire"),
        shield("Wall of Steam", 1010, school="fire"),
        enrage("The Mountain Behind Me", 172, school="fire"),
    ],
}

RARES = {n for n, r in ROSTER.items() if r[3]}

TABLES = {
    SHALLOWS: {
        "open_zone": {"name": SHALLOWS,
                      "creatures": {"Greenbelt Raptor": 5, "Canopy Panther": 4, "Ashfur Gorilla": 3,
                                    "Rubble Basilisk": 2}},
        "subzones": {
            "Ashclaim Landing": {"name": "Ashclaim Landing", "safe": True, "creatures": {}},
            "The Green Belt": {"name": "The Green Belt",
                               "creatures": {"Greenbelt Raptor": 5, "Canopy Panther": 5,
                                             "Ashfur Gorilla": 4, "Mother Canopy": 0}},
            "Khaz Varun's Gate": {"name": "Khaz Varun's Gate",
                                  "creatures": {"Gate-Squatter Brawler": 6, "Gate-Squatter Ashpreacher": 4,
                                                "Rubble Basilisk": 4, "Borrik the Unhoused": 0}},
            "The Scoured Slope": {"name": "The Scoured Slope",
                                  "creatures": {"Cinderslope Flame Spirit": 5, "Ashscree Scorpion": 5,
                                                "Ashwing Whelp": 4, "Sootwing": 0}},
            "The Tempest Shallows": {"name": "The Tempest Shallows",
                                     "creatures": {"Shallows Snapper": 5, "Bargebreaker Crab": 5,
                                                   "Wreckpicker Murloc": 4, "The Barge-Eater": 0}},
        },
    },
    REACH: {
        "open_zone": {"name": REACH,
                      "creatures": {"Tarfoot Gorilla": 4, "Sulphur Raptor": 4, "Ashplain Basilisk": 3,
                                    "Scoria Fire Elemental": 2}},
        "subzones": {
            "The Scoured Coast": {"name": "The Scoured Coast",
                                  "creatures": {"Scourcoast Crab": 5, "Stormscale Naga Raider": 5,
                                                "Steamvent Ooze": 3, "Wreck-Captain Vess'ira": 0}},
            # A hub: people stand at the smelter and the mine head. Flagged safe like every camp.
            "The Ashclaim Works": {"name": "The Ashclaim Works", "safe": True, "creatures": {}},
            "The Emberdeep Approach": {"name": "The Emberdeep Approach",
                                       "creatures": {"Ventborn Flame Spirit": 5, "Crag Earth Elemental": 5,
                                                     "Calderaborn Drake": 3, "Karrath the Ventlord": 0}},
            "The Cinder Flats": {"name": "The Cinder Flats",
                                 "creatures": {"Scoria Fire Elemental": 6, "Ashplain Basilisk": 4,
                                               "Sulphur Raptor": 4, "Old Scoria": 0}},
            "Cinderwharf Gate": {"name": "Cinderwharf Gate", "safe": True, "creatures": {}},
        },
    },
}

#: (item level, [(name, slot, kind, type, stat template)]). Item level = the rare's level + 3.
POOLS = {
    "Mother Canopy": (56, [
        ("Canopy-Mother's Pelt", "chest", "armor", "leather", "agi_physical"),
        ("Treetop Stalker's Hood", "head", "armor", "mail", "agi_int_hybrid"),
        ("Greenbelt Mantle", "shoulder", "armor", "cloth", "int_caster"),
        ("Mother's Claw", "main_hand", "weapon", "fist_weapon", "agi_physical"),
    ]),
    "Borrik the Unhoused": (57, [
        ("Unhoused Thane's Breastplate", "chest", "armor", "plate", "str_physical"),
        ("Squatter's Chain Leggings", "legs", "armor", "mail", "agi_physical"),
        ("Gate-Ash Gloves", "hands", "armor", "cloth", "spi_healer"),
        ("Borrik's Door-Bar", "main_hand", "weapon", "mace_2h", "str_physical"),
    ]),
    "Sootwing": (58, [
        ("Sootwing Scale Boots", "feet", "armor", "mail", "agi_int_hybrid"),
        ("Ashen Drakehide Shoulders", "shoulder", "armor", "leather", "agi_physical"),
        ("Slope-Scorched Helm", "head", "armor", "plate", "str_int_hybrid"),
        ("Sootwing's Fang", "main_hand", "weapon", "dagger", "agi_physical"),
    ]),
    "The Barge-Eater": (57, [
        ("Barge-Plate Greaves", "feet", "armor", "plate", "str_physical"),
        ("Tidepool Robe", "chest", "armor", "cloth", "spi_healer"),
        ("Pincer-Shell Gauntlets", "hands", "armor", "leather", "agi_int_hybrid"),
        ("The Eater's Claw", "main_hand", "weapon", "axe_2h", "str_physical"),
    ]),
    "Wreck-Captain Vess'ira": (59, [
        ("Wreck-Captain's Coat", "chest", "armor", "mail", "agi_physical"),
        ("Stormscale Circlet", "head", "armor", "cloth", "int_caster"),
        ("Scoured Coast Legguards", "legs", "armor", "leather", "agi_physical"),
        ("Vess'ira's Trident", "main_hand", "weapon", "polearm", "agi_physical"),
    ]),
    "Old Scoria": (60, [
        ("Scoria-Crust Pauldrons", "shoulder", "armor", "plate", "str_physical"),
        ("Cinderflat Treads", "feet", "armor", "cloth", "int_caster"),
        ("Ashplain Hauberk", "chest", "armor", "mail", "agi_int_hybrid"),
        ("Heart of Old Scoria", "main_hand", "weapon", "staff", "int_caster"),
    ]),
    "Karrath the Ventlord": (61, [
        ("Ventlord's Crown", "head", "armor", "leather", "agi_int_hybrid"),
        ("Emberdeep Approach Legplates", "legs", "armor", "plate", "str_int_hybrid"),
        ("Steamwoven Gloves", "hands", "armor", "cloth", "spi_healer"),
        ("Karrath's Brand", "main_hand", "weapon", "sword_1h", "str_physical"),
        ("Ventlord's Focus", "main_hand", "weapon", "mace_1h", "spi_healer"),
    ]),
}


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_tempest_shallows as TS
    import tools.handbuilt_ashen_reach as AR

    for zone, mod in ((SHALLOWS, TS), (REACH, AR)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            print(f"FAILED: {zone} subzones disagree with the map: "
                  f"{sorted(set(TABLES[zone]['subzones']) ^ declared)}")
            return 1
    named = set()
    for t in TABLES.values():
        named |= set(t["open_zone"]["creatures"])
        if RARES & set(t["open_zone"]["creatures"]):
            print("FAILED: a rare is in an open-zone table")
            return 1
        for s in t["subzones"].values():
            named |= set(s["creatures"])
    if named != set(ROSTER) or set(KITSETS) != set(ROSTER) or set(POOLS) != RARES:
        print(f"FAILED: tables, roster, kits and pools differ: {sorted(named ^ set(ROSTER))} "
              f"{sorted(set(KITSETS) ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
        return 1
    for name, (_t, lo, hi, mult) in ROSTER.items():
        if mult and POOLS[name][0] != hi + 3:
            print(f"FAILED: {name} is level {hi} and its loot is item level {POOLS[name][0]}")
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
    for zone, table in TABLES.items():
        entry = enc.setdefault("zones", {}).setdefault(zone, {})
        entry["open_zone"] = table["open_zone"]
        entry["subzones"] = table["subzones"]          # "caves" is left as it is
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    for zone, table in TABLES.items():
        print(f"  encounters.json: {zone}, open zone + {len(table['subzones'])} subzones")

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("Tempest Isle's seven open-world rares. Identity hand-authored in "
                      "tools/build_tempest_openworld.py; stats from LootGenerator at rare budget.")}
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
            d["item_id"] = "ti_" + name.lower().replace("'", "").replace(" ", "_").replace("-", "_")
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
