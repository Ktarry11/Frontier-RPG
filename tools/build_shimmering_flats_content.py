#!/usr/bin/env python3
"""Creatures, encounter tables and rare loot for The Shimmering Flats (35-40). Idempotent.

    PYTHONPATH=. python3 tools/build_shimmering_flats_content.py
    cd tools && python3 generate_creatures.py        # after any kit edit (kits: monster_kits.FLATS_KITS)

THE ZONE HAD A CAVE AND NO SURFACE. The Undercrust was populated when it was built; the pan above it
has been walkable and empty since. This is the pan.

THREE POPULATIONS, AND THE ZONE IS THE ARGUMENT BETWEEN THEM.

  THE SILITHID are what happened here. Kyle: "We can have the silithids fuuuuucked the place up. So
  salt flats are still there but its infested with silithids more." They are not a monster closet at
  the far end - they hold the middle and the east of the map outright, and the density climbs the
  whole way across, which is why the subzone bands run 35-36 at the Shore and 39-40 in the Deep Pan.

  THE PAN'S OWN fauna - vulture, scorpid, basilisk - were here before and are doing fine, because
  nothing that lives on a salt flat was ever relying on the salt flat being pleasant.

  THE DUSTWHEEL are the other half of Saltwheel's story. When the track died, some goblins went into
  the town and some stayed out on the course, and the ones who stayed are stripping it for parts.
  They are the reason the Raceway is dangerous and the reason the town pretends it is not: Saltwheel
  will not call them bandits, because half of them are somebody's cousin.

RARES LIVE IN SUBZONES, NOWHERE ELSE (Kyle, 2026-10-30). Not a style choice - creature_manager only
rolls a named is_boss creature when location_type == "subzone", so a rare in an open_zone table is
dead data. tools/qa_rare_placement.py enforces it across the game. One rare per subzone here, and
NO QUEST IS EVER BUILT AROUND ONE.

LEVEL BANDS COME FROM THE ZONE MODULE'S OWN SUBZONE COMMENTS, not from a second opinion typed here:
Shore 35-36, Crust 36-37, Raceway 37-38, Brine 37-38, Mounds 38-39, Deep Pan 39-40. The walk east is
the difficulty curve and the creature levels have to agree with it or the map lies to the player.

NO RESISTANCE SUFFIXES ANYWHERE IN THIS FILE. Magic resistance gear starts after 45 and this is a
35-40 zone - the suffix table offers "of Fire Protection" and friends and they are all off-limits here.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"
LOOT = ROOT / "data/loot/shimmering_flats_rare_loot.json"

FLATS_CREATURES = {
    # ---- THE SILITHID: what happened to this place
    "Saltcrust Skitterer": C("vermin_sneaky", 35, 36, "saltcrust_skitterer"),
    "Pan-Crawler Drone": C("vermin_swarm", 35, 37, "pan_crawler_drone"),
    "Glasswing Darter": C("beast_fast", 36, 38, "glasswing_darter"),
    "Flats Tunneler": C("vermin_sneaky", 37, 38, "flats_tunneler"),
    "Hive Spitter": C("humanoid_caster", 37, 39, "hive_spitter"),
    "Mound Sentinel": C("humanoid_warrior", 38, 40, "mound_sentinel"),

    # ---- THE PAN'S OWN: here before, and unbothered
    "Salt Vulture": C("beast_fast", 35, 36, "salt_vulture"),
    "Crustback Scorpid": C("beast_basic", 36, 38, "crustback_scorpid"),
    "Mirage Basilisk": C("beast_large", 38, 40, "mirage_basilisk"),

    # ---- THE DUSTWHEEL: the goblins who stayed out on the track
    "Dustwheel Scrapper": C("humanoid_rogue", 36, 37, "dustwheel_scrapper"),
    "Dustwheel Boilerman": C("humanoid_caster", 37, 38, "dustwheel_boilerman"),
    "Dustwheel Wheelman": C("humanoid_warrior", 38, 39, "dustwheel_wheelman"),

    # ---- named rares. One per subzone, weight 0, never quested.
    "Scourbite": C("beast_basic", 36, 36, "scourbite", True, 1.6),
    "Gearjaw": C("humanoid_warrior", 38, 38, "gearjaw", True, 1.7),
    "Rustcoat": C("beast_large", 38, 38, "rustcoat", True, 1.7),
    "Hollowcrust": C("humanoid_warrior", 39, 39, "hollowcrust", True, 1.8),
    "Paneater": C("beast_large", 40, 40, "paneater", True, 1.9),
}

#: open_zone carries the ordinary pan between the subzones and NO RARES - see the module docstring.
FLATS_ZONE = {
    "open_zone": {
        "name": "The Shimmering Flats",
        "creatures": {"Saltcrust Skitterer": 5, "Salt Vulture": 4, "Pan-Crawler Drone": 4,
                      "Crustback Scorpid": 3, "Glasswing Darter": 3, "Flats Tunneler": 3,
                      "Dustwheel Scrapper": 2, "Mound Sentinel": 2},
    },
    "subzones": {
        # west, where you come in off the range. The gentlest ground on the map and the only place
        # the silithid are still a minority.
        "The Shore": {
            "name": "The Shore",
            "creatures": {"Salt Vulture": 5, "Saltcrust Skitterer": 4, "Crustback Scorpid": 3,
                          "Pan-Crawler Drone": 2, "Scourbite": 0},
        },
        "The Crust": {
            "name": "The Crust",
            "creatures": {"Saltcrust Skitterer": 5, "Pan-Crawler Drone": 4, "Crustback Scorpid": 3,
                          "Glasswing Darter": 2},
        },
        # the dead racetrack. The only place on the pan where the danger is people.
        "The Mirage Raceway": {
            "name": "The Mirage Raceway",
            "creatures": {"Dustwheel Scrapper": 5, "Dustwheel Boilerman": 4, "Dustwheel Wheelman": 3,
                          "Glasswing Darter": 2, "Gearjaw": 0},
        },
        "The Brine": {
            "name": "The Brine",
            "creatures": {"Crustback Scorpid": 4, "Flats Tunneler": 4, "Hive Spitter": 3,
                          "Mirage Basilisk": 2, "Rustcoat": 0},
        },
        # the hives. From here east it is theirs and the map stops pretending otherwise.
        "The Mounds": {
            "name": "The Mounds",
            "creatures": {"Mound Sentinel": 5, "Hive Spitter": 4, "Flats Tunneler": 4,
                          "Pan-Crawler Drone": 3, "Hollowcrust": 0},
        },
        "The Deep Pan": {
            "name": "The Deep Pan",
            "creatures": {"Mound Sentinel": 5, "Mirage Basilisk": 4, "Hive Spitter": 3,
                          "Flats Tunneler": 3, "Glasswing Darter": 2, "Paneater": 0},
        },
    },
}


def flats_pools():
    """Five named rares, four items each.

    THE SPREAD IS FIXED HERE AND CHECKED BELOW rather than noticed afterwards. Twenty items:
    FIVE weapons of five DIFFERENT types with two of them caster weapons, THIRTEEN armour pieces
    across cloth/leather/mail/plate, one neck and one trinket.

    Thirteen does not divide by four, and the odd piece goes to MAIL. That was not the plan - the
    contract said twelve at three apiece and the audit failed the build on mail 4, which is the check
    working even though the error turned out to be in the contract rather than in the pools. Five
    rares at four items each is twenty; five weapons and two accessories leave thirteen; so one
    armour type was always going to get four, and the only question was which. Mail carries hunters,
    shamans and enhancement, so it is the one that misses least if it is wrong.

    Thirty classes need gear and most of them are not warriors - and the agility has to be on more
    than daggers, which is why Hollowcrust's polearm is an agi polearm and not another strength stick.
    """
    return {
        "Scourbite": [
            mk("Scourbite's Sting", "main_hand", "of the Assassin", 39,
               "Came off the thing still twitching. It does that for about a day.",
               weapon_type="dagger"),
            mk("Rimward Shroud", "chest", "of the Sorcerer", 39,
               "The west rim throws a shadow for about an hour a day and everything out here knows "
               "the hour.", armor_type="cloth"),
            mk("Shorewalker's Sabatons", "feet", "of the Bear", 39,
               "Salt gets into the seams and stays. You learn to walk differently.",
               armor_type="mail"),
            mk("Pan-Glass Charm", "trinket", "of the Owl", 39,
               "Salt fused to glass by something hot enough that nobody has explained it yet."),
        ],
        "Gearjaw": [
            mk("Gearjaw's Scattergun", "main_hand", "of the Monkey", 41,
               "Goblin-built, which means it works and nobody can tell you why.", weapon_type="gun"),
            mk("Pit-Crew Gauntlets", "hands", "of the Bear", 41,
               "Scorched through at both thumbs. He kept wearing them.", armor_type="plate"),
            mk("Scrapper's Breeches", "legs", "of the Monkey", 41,
               "Half the track is under these as stitching. He would say that proudly.",
               armor_type="leather"),
            mk("Dustwheel Tally-Chain", "neck", "of the Physician", 41,
               "One link a season. There are more links than there were seasons, which tells you "
               "what he counted."),
        ],
        "Rustcoat": [
            mk("Rustcoat's Spine-Stave", "main_hand", "of the Sorcerer", 41,
               "It kept growing after the animal stopped.", weapon_type="staff"),
            mk("Brine-Scaled Hauberk", "chest", "of the Bear", 41,
               "Rinse it and the rings come away in your hand. Nobody rinses it.", armor_type="mail"),
            mk("Mirage-Watcher's Leggings", "legs", "of the Owl", 41,
               "The heat out there shows you a lake. There has never been a lake.",
               armor_type="cloth"),
            mk("Flaking Bracers", "wrist", "of the Monkey", 41,
               "Three years of salt and they are thinner than they were. So is everything here.",
               armor_type="leather"),
        ],
        "Hollowcrust": [
            mk("Hollowcrust's Limb", "main_hand", "of the Monkey", 42,
               "Still articulated. It should not be.", weapon_type="polearm"),
            mk("Mound-Warden's Breastplate", "chest", "of the Bear", 42,
               "Plated salt over plated chitin, and the salt is the harder of the two.",
               armor_type="plate"),
            mk("Spitter's Resin Mantle", "shoulder", "of the Physician", 42,
               "Sets hard in an hour and never fully sets. They build whole galleries out of it.",
               armor_type="cloth"),
            mk("Sentinel-Shell Bracers", "wrist", "of Striking", 42,
               "The mound sentinels do not sleep and do not move. Nobody has worked out which is "
               "worse.", armor_type="mail"),
        ],
        "Paneater": [
            mk("Paneater's Tooth-Rod", "main_hand", "of the Archmage", 43,
               "A tooth out of a thing that eats ground. Very little impresses it.",
               weapon_type="mace_1h"),
            mk("Deep Pan Greaves", "legs", "of the Bear", 43,
               "The far end of the flats is a day's walk and nobody does it twice.",
               armor_type="plate"),
            mk("Swallowed Jerkin", "chest", "of the Monkey", 43,
               "Recovered. The man was not.", armor_type="leather"),
            mk("Grinding-Hunger Spaulders", "shoulder", "of Striking", 43,
               "You hear it under the crust before you see anything at all.", armor_type="mail"),
        ],
    }


#: the spread the pools are contracted to hold - see flats_pools().
CONTRACT = dict(weapons=5, weapon_types=5, caster_weapons=2,
                armor={"cloth": 3, "leather": 3, "mail": 4, "plate": 3}, neck=1, trinket=1)
CASTER_WEAPONS = {"staff", "wand", "tome", "idol", "libram", "totem", "mace_1h"}


def audit(pools):
    """Fail the build if the spread drifts. Thirty classes, and most are not warriors."""
    import collections
    items = [i for p in pools.values() for i in p]
    w = [i for i in items if i.get("weapon_type")]
    arm = collections.Counter(i["armor_type"] for i in items if i.get("armor_type"))
    neck = sum(1 for i in items if i["slot"] == "neck")
    trink = sum(1 for i in items if i["slot"] == "trinket")
    caster = [i for i in w if i["weapon_type"] in CASTER_WEAPONS]
    bad = []
    if len(w) != CONTRACT["weapons"]:
        bad.append(f"{len(w)} weapons, contract says {CONTRACT['weapons']}")
    if len({i['weapon_type'] for i in w}) != CONTRACT["weapon_types"]:
        bad.append(f"weapon types {sorted({i['weapon_type'] for i in w})} - want "
                   f"{CONTRACT['weapon_types']} distinct")
    if len(caster) < CONTRACT["caster_weapons"]:
        bad.append(f"{len(caster)} caster weapons, want {CONTRACT['caster_weapons']}")
    for t, n in CONTRACT["armor"].items():
        if arm[t] != n:
            bad.append(f"{t} {arm[t]}, contract says {n}")
    if neck != CONTRACT["neck"] or trink != CONTRACT["trinket"]:
        bad.append(f"neck {neck}/trinket {trink}, contract says {CONTRACT['neck']}/{CONTRACT['trinket']}")
    # the level rule, not a preference: nothing resistance-flavoured below 45
    res = [i["name"] for i in items
           if any("resistance" in k for k in (i.get("secondary_stats") or {}))]
    if res:
        bad.append(f"resistance stats below level 45: {res}")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    # THE ZONE MODULE IS THE AUTHORITY ON ITS OWN SUBZONES. Retyping the names here is how a table
    # ends up attached to a subzone that does not exist - silently, because nothing looks it up until
    # a player walks into the rectangle.
    import tools.handbuilt_shimmering_flats as F
    declared = {s[0] for s in F.SUBZONES}
    mine = set(FLATS_ZONE["subzones"])
    if mine - declared:
        print(f"FAILED: tables for subzones the zone does not have: {sorted(mine - declared)}")
        return 1
    if declared - mine:
        print(f"FAILED: subzones with nobody in them: {sorted(declared - mine)}")
        return 1
    print(f"subzones agree: {len(declared)}")

    # every creature named in a table has to exist, or the first roll in that subzone returns None
    named = set(FLATS_ZONE["open_zone"]["creatures"])
    for s in FLATS_ZONE["subzones"].values():
        named |= set(s["creatures"])
    if named - set(FLATS_CREATURES):
        print(f"FAILED: tables name creatures nothing defines: {sorted(named - set(FLATS_CREATURES))}")
        return 1
    if set(FLATS_CREATURES) - named:
        print(f"FAILED: creatures defined that no table uses: {sorted(set(FLATS_CREATURES) - named)}")
        return 1

    # RARES IN SUBZONES ONLY (Kyle). Checked here as well as in qa_rare_placement, because this is
    # the file that would reintroduce it.
    rares = {n for n, c in FLATS_CREATURES.items() if c["is_boss"]}
    stray = rares & set(FLATS_ZONE["open_zone"]["creatures"])
    if stray:
        print(f"FAILED: rares in the open_zone table, where they can never spawn: {sorted(stray)}")
        return 1
    homeless = rares - {n for s in FLATS_ZONE["subzones"].values() for n in s["creatures"]}
    if homeless:
        print(f"FAILED: rares with no subzone: {sorted(homeless)}")
        return 1
    print(f"roster: {len(FLATS_CREATURES)} creatures, {len(rares)} rares, all in subzones only")

    cre = json.loads(CRE.read_text(encoding="utf-8"))
    cre["creatures"].update(FLATS_CREATURES)
    CRE.write_text(json.dumps(cre, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    enc = json.loads(ENC.read_text(encoding="utf-8"))
    z = enc["zones"].setdefault("The Shimmering Flats", {})
    z["open_zone"] = FLATS_ZONE["open_zone"]
    z["subzones"] = FLATS_ZONE["subzones"]          # caves key is left exactly as it is
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  encounters.json: open_zone + 6 subzones (The Undercrust untouched)")

    pools = flats_pools()
    bad = audit(pools)
    if bad:
        print("\nFAILED - fix the pools, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1
    n = sum(len(v) for v in pools.values())
    print(f"loot: {len(pools)} pools, {n} items, spread holds")
    out = {"_notes": ("Named rares of the Shimmering Flats. One item per kill. Identity hand-authored "
                      "in tools/build_shimmering_flats_content.py; spread checked by its audit().")}
    out.update(pools)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {LOOT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
