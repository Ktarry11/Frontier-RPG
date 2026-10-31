#!/usr/bin/env python3
"""Creatures, encounter table and boss loot for The Lashings. Idempotent.

    PYTHONPATH=. python3 tools/build_lashings_content.py
    cd tools && python3 generate_creatures.py     # after any kit edit (monster_kits.LASHINGS_KITS)

CALIBRATED BETWEEN THE TWO BANDS EITHER SIDE OF IT. Northern Tanaris at 41-44 runs trash 104-138;
the Abyssal Sands at 44-47 run 134-166. This sits at 44-48, so trash 140-178 and bosses 230-275
before their multiplier.

PIRATES ARE PHYSICAL, AND THAT IS THE POINT OF THIS PLACE EXISTING NEXT TO GLITTERVEIN. That zone
spends 46-52 teaching the player that magic resistance is an answer; this one, at an overlapping
band, is full of people who swing things. A party that has geared entirely into arcane and frost
finds out here that armour and dodge did not stop mattering. The one exception is Juss Wick, who
is fire, and he is a powder hulk rather than a caster.

NO MAGIC RESISTANCE IN THE LOOT. Three of this band's five levels qualify under the 45+ rule and
the pass stays off it anyway, for the same reason the Abyssal Sands do: Glittervein owns that
theme and a sibling zone handing it out first takes it away.

THE TABLE LIVES UNDER NORTHERN TANARIS, because zone_manager looks a cave or dungeon's encounters
up under `region` as a ZONE NAME - encounters["zones"][region]["caves"][map name] - and this map
sets zone.region = "Northern Tanaris". The Drownbell is already in there; this is its second cave,
and they are deliberately different crews.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as _make, C  # noqa: E402

ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"
LOOT = ROOT / "data/loot/lashings_boss_loot.json"

_ASKED = []


def mk(name, slot, suffix, ilvl, flavor, **kw):
    """make(), with the requested suffix recorded so audit() can catch one that did not take -
    make() short-circuits for shields and never looks at the suffix."""
    d = _make(name, slot, suffix, ilvl, flavor, **kw)
    _ASKED.append((d, suffix))
    return d


LASHINGS_CREATURES = {
    "Southsea Swabbie": C("humanoid_rogue", 44, 45, "southsea_swabbie"),
    "Southsea Rigger": C("humanoid_rogue", 45, 46, "southsea_rigger"),
    "Southsea Powdermonkey": C("humanoid_warrior", 46, 47, "southsea_powdermonkey"),
    "Southsea Netcaster": C("humanoid_rogue", 45, 48, "southsea_netcaster"),
    "Hulk Rat": C("vermin_sneaky", 44, 46, "hulk_rat"),
    "Bosun Grell Tarpot": C("humanoid_warrior", 46, 46, "bosun_grell_tarpot", True, 2.1),
    "Sailmaker Oona Flay": C("humanoid_rogue", 46, 46, "sailmaker_oona_flay", True, 2.2),
    "Powder-Master Juss Wick": C("humanoid_warrior", 47, 47, "powder_master_juss_wick", True, 2.2),
    "Quartermaster Nadd Kell": C("humanoid_rogue", 47, 47, "quartermaster_nadd_kell", True, 2.3),
    "Captain Ardessa Rake": C("humanoid_warrior", 49, 49, "captain_ardessa_rake", True, 2.6),
}

BOSSES = ("Bosun Grell Tarpot", "Sailmaker Oona Flay", "Powder-Master Juss Wick",
          "Quartermaster Nadd Kell", "Captain Ardessa Rake")

LASHINGS_TABLE = {
    "name": "The Lashings",
    "creatures": {"Southsea Swabbie": 5, "Southsea Rigger": 5, "Southsea Netcaster": 4,
                  "Southsea Powdermonkey": 3, "Hulk Rat": 3,
                  **{b: 0 for b in BOSSES}},
}


def pools():
    """Five bosses, 20 items.

    SPREAD CONTRACTED UP FRONT: five weapons of five different types with two caster weapons,
    thirteen armour pieces, one neck and one trinket. 20 - 5 - 2 = 13, which does not divide by
    four - cloth 3, leather 4, mail 3, plate 3. Leather takes the extra because this is a cove
    full of sailors and the loot should look like it came off them.
    """
    return {
        "Bosun Grell Tarpot": [
            mk("Starter's Knotted Rope", "main_hand", "of Striking", 48,
               "A bosun's rope has one knot for calling the watch and three for the other thing.",
               weapon_type="mace_1h"),
            mk("Bosun's Tarred Jerkin", "chest", "of the Monkey", 48,
               "Tarred against weather on a ship that has not met weather in twenty years.",
               armor_type="leather"),
            mk("Deck-Caller's Gorget", "neck", "of the Bear", 48,
               "He could be heard the length of nine hulls and he knew it."),
            mk("Hulk-Walker's Boots", "feet", "of the Monkey", 48,
               "Soled for wet planking, which out here is all the planking.",
               armor_type="mail"),
        ],
        "Sailmaker Oona Flay": [
            mk("Flay's Sailmaker's Needle", "main_hand", "of the Assassin", 48,
               "Six inches of steel for canvas, and canvas is not what it has been through.",
               weapon_type="dagger"),
            mk("Stitched-Canvas Hauberk", "chest", "of the Eagle", 48,
               "Sailcloth, folded eleven times and sewn by somebody with nothing else to do.",
               armor_type="mail"),
            mk("Sailmaker's Palm", "hands", "of Striking", 48,
               "The leather pad a sailmaker drives a needle with. Hers is worn through twice.",
               armor_type="leather"),
            mk("Unfurled Mantle", "shoulder", "of the Sorcerer", 48,
               "Nobody on this fleet has unfurled anything in twenty years.",
               armor_type="cloth"),
        ],
        "Powder-Master Juss Wick": [
            mk("Wick's Linstock", "main_hand", "of the Archmage", 49,
               "A yard of match-cord on a pole, and he has never once been seen to hurry.",
               weapon_type="staff"),
            mk("Powder-Hulk Breastplate", "chest", "of the Bear", 49,
               "Scorched in four places and holed in none, which is a career summary.",
               armor_type="plate"),
            mk("Slow-Match Bracers", "wrist", "of Striking", 49,
               "They smell of it. Everything of his does.", armor_type="leather"),
            mk("Charge-Counter's Cap", "head", "of the Owl", 49,
               "Forty-one barrels, and he could tell you where every one of them was.",
               armor_type="cloth"),
        ],
        "Quartermaster Nadd Kell": [
            mk("The Share-Out Blade", "main_hand", "of the Assassin", 49,
               "A quartermaster settles disputes. This is how the ones that will not settle end.",
               weapon_type="sword_1h"),
            mk("Prize-Court Legguards", "legs", "of the Bear", 49,
               "Everything that came aboard was logged before it was divided. Everything.",
               armor_type="plate"),
            mk("Ledger-Keeper's Grips", "hands", "of the Owl", 49,
               "Ink in the seams, four years deep.", armor_type="cloth"),
            mk("Fair-Shares Girdle", "waist", "of the Monkey", 49,
               "Fair by the articles, which is not the same as fair.", armor_type="mail"),
        ],
        "Captain Ardessa Rake": [
            mk("Rake's Boarding Cutlass", "main_hand", "of the Bear", 51,
               "She is the one who was good at it. That is the whole difference between this cove "
               "and the Barrens.", weapon_type="sword_2h"),
            mk("Captain's Rated Plate", "chest", "of the Bear", 51,
               "Kept like a ship, on the one hull in this cove that still is one.",
               armor_type="plate"),
            mk("Twenty-Years-at-Anchor Spaulders", "shoulder", "of the Monkey", 51,
               "She has not sailed since the sky changed and she has not stopped being a captain.",
               armor_type="leather"),
            mk("Articles of the Southsea", "trinket", "of the Eagle", 51,
               "Signed by every hand aboard. The first signature is a cross and it is hers."),
        ],
    }


CONTRACT = dict(weapons=5, weapon_types=5, caster_weapons=2,
                armor={"cloth": 3, "leather": 4, "mail": 3, "plate": 3}, neck=1, trinket=1)
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
        bad.append(f"resistance in a pass that leaves that theme to Glittervein: {res}")
    for (d, suffix) in _ASKED:
        if ("Protection" in suffix or "Resistance" in suffix) and d in items:
            stats = dict(d.get("secondary_stats") or {}, **(d.get("primary_stats") or {}))
            if not any("resistance" in k for k in stats):
                bad.append(f"{d['name']} was asked for '{suffix}' and make() ignored it")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_lashings as LA

    bad = []
    placed = {n for (_x, _y, n, _l) in LA.TRASH} | set(LA.BOSSES)
    if not LA.TRASH:
        zone, L = LA.build_lashings()
        LA.dress(zone, L)
        LA.finish(zone, L)
        placed = {n for (_x, _y, n, _l) in LA.TRASH} | set(LA.BOSSES)

    # EVERY HAND-PLACED MOB MUST EXIST. world/cave_spawns.py raises on a pack member with no
    # creature entry, and that failure is at zone-load - the whole game, not just this map.
    table = set(LASHINGS_TABLE["creatures"])
    if placed - table:
        bad.append(f"hand-placed mobs missing from the table: {sorted(placed - table)}")
    if placed - set(LASHINGS_CREATURES):
        bad.append(f"hand-placed mobs missing from the roster: "
                   f"{sorted(placed - set(LASHINGS_CREATURES))}")
    if set(LA.BOSSES) != set(BOSSES):
        bad.append(f"the map's bosses and this file's differ: "
                   f"{sorted(set(LA.BOSSES) ^ set(BOSSES))}")

    pls = pools()
    if set(pls) != set(BOSSES):
        bad.append(f"loot pools do not match the bosses: {sorted(set(pls) ^ set(BOSSES))}")
    bad += audit(pls)

    if bad:
        print("FAILED - fix the content, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    print(f"roster {len(LASHINGS_CREATURES)} | {len(BOSSES)} bosses, all pinned by the map")

    cre = json.loads(CRE.read_text(encoding="utf-8"))
    cre["creatures"].update(LASHINGS_CREATURES)
    CRE.write_text(json.dumps(cre, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    enc = json.loads(ENC.read_text(encoding="utf-8"))
    enc["zones"]["Northern Tanaris"].setdefault("caves", {})["The Lashings"] = LASHINGS_TABLE
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  encounters.json: Northern Tanaris -> caves -> The Lashings")

    out = {"_notes": "Bosses of The Lashings. Hand-authored in tools/build_lashings_content.py; "
                     "spread checked by its audit()."}
    out.update(pls)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"loot: {len(pls)} pools, {sum(len(v) for v in pls.values())} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
