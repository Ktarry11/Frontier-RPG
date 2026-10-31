#!/usr/bin/env python3
"""Creatures, encounter tables and rare loot for The Abyssal Sands. Idempotent.

    PYTHONPATH=. python3 tools/build_abyssal_content.py
    cd tools && python3 generate_creatures.py        # after any kit edit (monster_kits.ABYSSAL_KITS)

CALIBRATED AGAINST NORTHERN TANARIS, which is the thing that block asked for. 41-44 trash runs
104-138 and its rares 150-185, so this steps to trash 134-166 and rares 190-225. Re-extrapolating
from 35-40 a second time would have put trash near 180, which is how a band drifts upward every
time somebody adds a zone - and this is the first chance anyone has had to get that wrong.

TWO POPULATIONS AND THEY ARE THE SAME EVENT. Things that FELL IN - caravans, their beasts, the
people on them - and things that came UP, because the collapses opened a way to them. Nothing in
this zone is native to a desert, which is the point: the entire bestiary is a consequence of the
water leaving.

The split is also the difficulty curve. The fallen are near the north gate, where the first holes
opened and where a road used to run. What came up is concentrated in the south and east, around the
biggest and deepest pits - which is the direction Glittervein lies in, and the direction the water
went.

RARES LIVE IN SUBZONES, NOWHERE ELSE (Kyle, 2026-10-30, now enforced game-wide by
tools/qa_rare_placement.py). One per surface subzone, none in the open_zone table, none quested.

"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"
LOOT = ROOT / "data/loot/abyssal_sands_rare_loot.json"


ABYSSAL_CREATURES = {
    # ---- what fell in
    "Cartfall Scavenger": C("humanoid_rogue", 44, 45, "cartfall_scavenger"),
    "Sunken Drover": C("undead_basic", 44, 46, "sunken_drover"),
    "Pitfall Kodo": C("beast_large", 44, 46, "pitfall_kodo"),
    # ---- what came up
    "Limestone Crawler": C("vermin_sneaky", 44, 46, "limestone_crawler"),
    "Pit Shrike": C("beast_fast", 44, 45, "pit_shrike"),
    "Hollowing Ooze": C("elemental_caster", 45, 46, "hollowing_ooze"),
    "Sinkhole Lurker": C("beast_large", 45, 47, "sinkhole_lurker"),
    "Saltbone Revenant": C("undead_basic", 45, 47, "saltbone_revenant"),
    "Glasswall Elemental": C("elemental_bruiser", 46, 47, "glasswall_elemental"),
    "Deepwater Horror": C("aquatic_basic", 46, 47, "deepwater_horror"),
    # ---- named rares, one per subzone, weight 0, never quested
    "The First Down": C("beast_large", 45, 45, "the_first_down", True, 1.7),
    "Axleback": C("beast_large", 45, 45, "axleback", True, 1.7),
    "The Wide Sink Mother": C("vermin_sneaky", 46, 46, "the_wide_sink_mother", True, 1.8),
    "Glasswall Warden": C("elemental_bruiser", 46, 46, "glasswall_warden", True, 1.8),
    "The Thing in the Throat": C("aquatic_basic", 46, 46, "the_thing_in_the_throat", True, 1.9),
    "Longcollapse": C("beast_large", 47, 47, "longcollapse", True, 1.9),
    "Underlight": C("elemental_caster", 47, 47, "underlight", True, 2.0),
}

ABYSSAL_ZONE = {
    "open_zone": {
        "name": "The Abyssal Sands",
        "creatures": {"Limestone Crawler": 5, "Pit Shrike": 4, "Cartfall Scavenger": 4,
                      "Pitfall Kodo": 3, "Saltbone Revenant": 3, "Sinkhole Lurker": 2},
    },
    "subzones": {
        "The First Hole": {
            "name": "The First Hole",
            "creatures": {"Cartfall Scavenger": 5, "Sunken Drover": 4, "Pitfall Kodo": 4,
                          "Pit Shrike": 2, "The First Down": 0},
        },
        "Cartfall": {
            "name": "Cartfall",
            "creatures": {"Pitfall Kodo": 5, "Cartfall Scavenger": 4, "Sunken Drover": 3,
                          "Limestone Crawler": 2, "Axleback": 0},
        },
        "The Wide Sink": {
            "name": "The Wide Sink",
            "creatures": {"Limestone Crawler": 5, "Hollowing Ooze": 4, "Pit Shrike": 3,
                          "Sinkhole Lurker": 2, "The Wide Sink Mother": 0},
        },
        "The Glasswall": {
            "name": "The Glasswall",
            "creatures": {"Glasswall Elemental": 5, "Hollowing Ooze": 4, "Limestone Crawler": 3,
                          "Saltbone Revenant": 2, "Glasswall Warden": 0},
        },
        "The Throats": {
            "name": "The Throats",
            "creatures": {"Deepwater Horror": 4, "Sinkhole Lurker": 4, "Hollowing Ooze": 3,
                          "Saltbone Revenant": 3, "The Thing in the Throat": 0},
        },
        "The Long Collapse": {
            "name": "The Long Collapse",
            "creatures": {"Sinkhole Lurker": 5, "Saltbone Revenant": 4, "Pitfall Kodo": 3,
                          "Limestone Crawler": 3, "Longcollapse": 0},
        },
        # FOURTH PEG. Eight people in tents, and nothing spawns on them - see
        # CreatureManager.is_safe_subzone. A subzone with no roster of its own falls through to the
        # parent zone's table AND rolls at 5% a step against the open zone's 2%, so without this
        # the quietest place on the map would be the most dangerous one.
        "Fourth Peg": {
            "name": "Fourth Peg",
            "safe": True,
            "creatures": {},
        },
        "Underlight": {
            "name": "Underlight",
            "creatures": {"Glasswall Elemental": 4, "Deepwater Horror": 4, "Hollowing Ooze": 4,
                          "Sinkhole Lurker": 3, "Underlight": 0},
        },
    },
}


def pools():
    """Seven named rares, 28 items.

    SPREAD CONTRACTED UP FRONT: seven weapons of seven different types with three caster weapons,
    nineteen armour pieces across the four classes, one neck and one trinket. 28 minus 7 minus 2 is
    19, which does not divide by four - three classes take five and one takes four. Writing that
    arithmetic down here because the audit has caught me getting it wrong twice now, on the
    Shimmering Flats and again on Northern Tanaris, both times in the CONTRACT rather than the pools.

    NO MAGIC RESISTANCE. This band runs 44-47 and the rule is 45+, so two levels of it are legal -
    and the whole pass still stays off it, because a zone that introduces resistance gear on a third
    of its items is a zone that has decided resistance is its theme. Glittervein at 46-49 is where
    that belongs and it can have it properly.
    """
    return {
        "The First Down": [
            mk("First-Down Goad", "main_hand", "of the Bear", 49,
               "Still in the hand it was in. The hand came up with it.", weapon_type="polearm"),
            mk("Harness-Scarred Breastplate", "chest", "of the Bear", 49,
               "Four years in a hole and the buckles still work.", armor_type="plate"),
            mk("Drover's Last Wraps", "hands", "of the Monkey", 49,
               "Whoever went down first went down holding the reins.", armor_type="leather"),
            mk("Three-Year Pendant", "neck", "of the Owl", 49,
               "The date scratched inside is the season the shallow wells went."),
        ],
        "Axleback": [
            mk("Axleback's Hauling Chain", "main_hand", "of the Bear", 49,
               "Dragged out of a pit with a cart still attached to the other end.",
               weapon_type="mace_2h"),
            mk("Cartfall Hide Jerkin", "chest", "of the Monkey", 49,
               "It went in with the caravan and it came out without it.", armor_type="leather"),
            mk("Teamster's Scaled Boots", "feet", "of the Bear", 49,
               "The ground gave way under these and they are still walking on it.",
               armor_type="mail"),
            mk("Spoil-Ring Circlet", "head", "of the Sorcerer", 49,
               "Everything a hole throws up ends up in a ring round it.", armor_type="cloth"),
        ],
        "The Wide Sink Mother": [
            mk("Brood-Mother's Shearing Limb", "main_hand", "of the Assassin", 50,
               "Articulated. It should not be, and it is.", weapon_type="fist_weapon"),
            mk("Hollowed Carapace Guard", "shoulder", "of the Bear", 50,
               "Shell plate off something that only came up because the floor went down.",
               armor_type="plate"),
            mk("Sink-Mother's Veil", "head", "of the Archmage", 50,
               "There is a smell in the Wide Sink and this has it.", armor_type="cloth"),
            mk("Crawler-Scale Bracers", "wrist", "of the Monkey", 50,
               "Thin, curved, and sharper than they have any right to be.", armor_type="mail"),
        ],
        "Glasswall Warden": [
            mk("Annealed Wall-Shard", "main_hand", "of the Sorcerer", 50,
               "Sand fused into glass where something very hot came up through it.",
               weapon_type="wand"),
            mk("Glasswall Plate", "chest", "of the Bear", 50,
               "One face of it is still glass and will not take a scratch.", armor_type="plate"),
            mk("Fused-Face Leggings", "legs", "of the Monkey", 50,
               "The south face of that hole is a mirror in the afternoon.", armor_type="leather"),
            mk("Annealing Band", "wrist", "of the Archmage", 50,
               "Warm, hours after sundown, in a desert that goes cold.", armor_type="cloth"),
        ],
        "The Thing in the Throat": [
            mk("Throat-Cold Rod", "main_hand", "of the Archmage", 50,
               "Cold in a hole that has never held water in living memory.", weapon_type="mace_1h"),
            mk("Remembered-Water Mantle", "shoulder", "of the Physician", 50,
               "Damp. Nobody has worked out how.", armor_type="cloth"),
            mk("Deep-Throat Scale Vest", "chest", "of the Monkey", 50,
               "Whatever is down there came from somewhere that still has water in it.",
               armor_type="mail"),
            mk("Undertow Treads", "feet", "of the Assassin", 50,
               "It pulls, and there is nothing to pull with.", armor_type="leather"),
        ],
        "Longcollapse": [
            mk("Longcollapse Sweeper", "main_hand", "of the Bear", 51,
               "Twenty-two tiles of ground went in one afternoon and this was under it.",
               weapon_type="axe_2h"),
            mk("Nothing-Left-Standing Girdle", "waist", "of the Bear", 51,
               "The longest hole on the map and the newest.", armor_type="plate"),
            mk("Collapse-Walker's Leggings", "legs", "of the Bear", 51,
               "You can walk the length of that one and never be more than a step from the edge.",
               armor_type="mail"),
            mk("Fallen-Ground Charm", "trinket", "of the Owl", 51,
               "Picked up off ground that was twenty feet higher four years ago."),
        ],
        "Underlight": [
            mk("Underlight's Lantern-Staff", "main_hand", "of the Archmage", 51,
               "Something is lit down there and it was not lit by anybody.", weapon_type="staff"),
            mk("Glow-Touched Robes", "chest", "of the Sorcerer", 51,
               "Stand on that rim at night and you can read by it.", armor_type="cloth"),
            mk("Drawn-Downward Spaulders", "shoulder", "of the Monkey", 51,
               "Everybody who looks in wants to go in. That is the part nobody says.",
               armor_type="leather"),
            mk("Deep-Shine Gauntlets", "hands", "of Striking", 51,
               "The light comes UP, which is the wrong direction for a hole.", armor_type="mail"),
        ],
    }


CONTRACT = dict(weapons=7, weapon_types=7, caster_weapons=3,
                armor={"cloth": 5, "leather": 5, "mail": 5, "plate": 4}, neck=1, trinket=1)
CASTER_WEAPONS = {"staff", "wand", "tome", "idol", "libram", "totem", "mace_1h"}


def audit(pls):
    import collections
    items = [i for p in pls.values() for i in p]
    w = [i for i in items if i.get("weapon_type")]
    arm = collections.Counter(i["armor_type"] for i in items if i.get("armor_type"))
    bad = []
    if len(w) != CONTRACT["weapons"]:
        bad.append(f"{len(w)} weapons, contract says {CONTRACT['weapons']}")
    types = {i["weapon_type"] for i in w}
    if len(types) != CONTRACT["weapon_types"]:
        bad.append(f"weapon types {sorted(types)} - want {CONTRACT['weapon_types']} distinct")
    caster = [i for i in w if i["weapon_type"] in CASTER_WEAPONS]
    if len(caster) < CONTRACT["caster_weapons"]:
        bad.append(f"{len(caster)} caster weapons, want {CONTRACT['caster_weapons']}")
    for t, n in CONTRACT["armor"].items():
        if arm[t] != n:
            bad.append(f"{t} {arm[t]}, contract says {n}")
    for s in ("neck", "trinket"):
        got = sum(1 for i in items if i["slot"] == s)
        if got != CONTRACT[s]:
            bad.append(f"{s} {got}, contract says {CONTRACT[s]}")
    res = [i["name"] for i in items
           if any("resistance" in k for k in (i.get("secondary_stats") or {}))]
    if res:
        bad.append(f"resistance stats in a pass that deliberately stays off them: {res}")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_abyssal_sands as A

    declared = {s[0] for s in A.SUBZONES}
    mine = set(ABYSSAL_ZONE["subzones"])
    if mine != declared:
        print(f"FAILED: subzones disagree with the zone module: {sorted(mine ^ declared)}")
        return 1
    named = set(ABYSSAL_ZONE["open_zone"]["creatures"])
    for s in ABYSSAL_ZONE["subzones"].values():
        named |= set(s["creatures"])
    if named != set(ABYSSAL_CREATURES):
        print(f"FAILED: tables and roster differ: {sorted(named ^ set(ABYSSAL_CREATURES))}")
        return 1
    rares = {n for n, c in ABYSSAL_CREATURES.items() if c["is_boss"]}
    stray = rares & set(ABYSSAL_ZONE["open_zone"]["creatures"])
    if stray:
        print(f"FAILED: rares in the open_zone table, where they can never spawn: {sorted(stray)}")
        return 1
    homeless = rares - {n for s in ABYSSAL_ZONE["subzones"].values() for n in s["creatures"]}
    if homeless:
        print(f"FAILED: rares with no subzone: {sorted(homeless)}")
        return 1
    print(f"subzones agree: {len(declared)} | roster: {len(ABYSSAL_CREATURES)}, "
          f"{len(rares)} rares all in subzones only")

    cre = json.loads(CRE.read_text(encoding="utf-8"))
    cre["creatures"].update(ABYSSAL_CREATURES)
    CRE.write_text(json.dumps(cre, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    enc = json.loads(ENC.read_text(encoding="utf-8"))
    enc["zones"]["The Abyssal Sands"] = ABYSSAL_ZONE
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  encounters.json: open_zone + {len(ABYSSAL_ZONE['subzones'])} subzones (Fourth Peg safe)")

    pls = pools()
    bad = audit(pls)
    if bad:
        print("\nFAILED - fix the pools, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1
    out = {"_notes": ("Named rares of the Abyssal Sands. One item per kill. Hand-authored in "
                      "tools/build_abyssal_content.py; spread checked by its audit().")}
    out.update(pls)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"loot: {len(pls)} pools, {sum(len(v) for v in pls.values())} items, spread holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
