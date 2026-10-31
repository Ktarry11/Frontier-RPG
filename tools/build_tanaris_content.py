#!/usr/bin/env python3
"""Creatures, encounter tables and rare loot for Northern Tanaris and The Drownbell. Idempotent.

    PYTHONPATH=. python3 tools/build_tanaris_content.py
    cd tools && python3 generate_creatures.py        # after any kit edit (monster_kits.TANARIS_KITS)

THE FIRST ROSTER ABOVE 40. Everything below this band could be calibrated against content that
already existed; this one had nothing to measure against, because audit_quests has been reporting
"NOTHING TO DO at level(s): 43-60". The damage numbers in monster_kits.TANARIS_KITS carry the note
on how they were extrapolated and why the NEXT zone in this band must be calibrated against them
rather than re-extrapolated.

THREE POPULATIONS ON THE SURFACE, and the geography sorts them:

  THE SANDFURY are still at their own ruin, which is the point of leaving Zul'Farrak standing after
  Kyle scrapped the dungeon. Whatever happened there did not finish the trolls, it took the roof off.
  They are densest at the pyramid and thin out fast.
  THE DESERT is doing fine - raptors, scorpids, basilisks, hyenas and the things that follow a road
  waiting for something on it to stop moving.
  THE PIRATES are a spill out of the cove. Common on the Drownbell Shore, rare on the road, absent
  in the west. A player can feel the cove before they find it.

RARES LIVE IN SUBZONES, NOWHERE ELSE (Kyle, 2026-10-30, now enforced game-wide by
tools/qa_rare_placement.py). One per surface subzone, none in the open_zone table, none quested.

THE DROWNBELL IS A CAVE, so its boss and rare sit in its table at weight 0 and are placed only via
zone.boss_positions, and it carries no pack list at all.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"
LOOT = ROOT / "data/loot/tanaris_rare_loot.json"

TANARIS_CREATURES = {
    # ---- the Sandfury, still at their own ruin
    "Sandfury Scavenger": C("humanoid_rogue", 41, 42, "sandfury_scavenger"),
    "Sandfury Axethrower": C("humanoid_ranged", 41, 43, "sandfury_axethrower"),
    "Sandfury Hexxer": C("humanoid_caster", 42, 44, "sandfury_hexxer"),
    # ---- the desert, which is doing fine
    "Dunecrest Raptor": C("beast_fast", 41, 42, "dunecrest_raptor"),
    "Thornback Scorpid": C("beast_basic", 41, 43, "thornback_scorpid"),
    "Carrion Vulture of Tanaris": C("beast_fast", 41, 42, "tan_carrion_vulture"),
    "Bonefield Hyena": C("beast_fast", 42, 43, "bonefield_hyena"),
    "Sunbleached Basilisk": C("beast_large", 42, 44, "sunbleached_basilisk"),
    "Sunstone Elemental": C("elemental_bruiser", 43, 44, "sunstone_elemental"),
    # ---- what nests in a dead city
    "Gadgetzan Scrapjaw": C("vermin_sneaky", 41, 43, "gadgetzan_scrapjaw"),
    # ---- the cove's spill, on the surface
    "Drownbell Deckhand": C("humanoid_warrior", 42, 44, "drownbell_deckhand"),
    "Drownbell Powdermonkey": C("humanoid_caster", 43, 44, "drownbell_powdermonkey"),
    # ---- named rares, one per subzone, weight 0, never quested
    "Thaka the Unburied": C("humanoid_warrior", 43, 43, "thaka_the_unburied", True, 1.7),
    "The Last Tenant": C("vermin_sneaky", 42, 42, "the_last_tenant", True, 1.6),
    "Nineteen Mile": C("beast_large", 43, 43, "nineteen_mile", True, 1.7),
    "Marrowmaw": C("beast_fast", 43, 43, "marrowmaw", True, 1.8),
    "Saltjaw": C("beast_large", 44, 44, "saltjaw", True, 1.8),
    "The Drowned Purser": C("humanoid_rogue", 44, 44, "the_drowned_purser", True, 1.9),
}

DROWNBELL_CREATURES = {
    "Drownbell Cutthroat": C("humanoid_rogue", 43, 44, "drownbell_cutthroat"),
    "Drownbell Bosun": C("humanoid_warrior", 43, 45, "drownbell_bosun"),
    "Cove Tidecaller": C("humanoid_caster", 44, 45, "cove_tidecaller"),
    "Bilge Crawler": C("vermin_swarm", 43, 44, "bilge_crawler"),
    "Captain Vaile Drownbell": C("humanoid_warrior", 45, 45, "captain_vaile_drownbell", True, 2.0),
    "The Bellwarden": C("humanoid_warrior", 44, 44, "the_bellwarden", True, 1.8),
}

TANARIS_ZONE = {
    "open_zone": {
        "name": "Northern Tanaris",
        "creatures": {"Thornback Scorpid": 5, "Dunecrest Raptor": 4,
                      "Carrion Vulture of Tanaris": 4, "Bonefield Hyena": 3,
                      "Sunbleached Basilisk": 3, "Sandfury Scavenger": 2, "Sunstone Elemental": 2},
    },
    "subzones": {
        "Zul'Farrak Ruins": {
            "name": "Zul'Farrak Ruins",
            "creatures": {"Sandfury Scavenger": 5, "Sandfury Axethrower": 4, "Sandfury Hexxer": 3,
                          "Carrion Vulture of Tanaris": 2, "Thaka the Unburied": 0},
        },
        "Gadgetzan Ruins": {
            "name": "Gadgetzan Ruins",
            "creatures": {"Gadgetzan Scrapjaw": 5, "Thornback Scorpid": 3,
                          "Carrion Vulture of Tanaris": 3, "Sandfury Scavenger": 2,
                          "The Last Tenant": 0},
        },
        "The Caravan Road": {
            "name": "The Caravan Road",
            "creatures": {"Dunecrest Raptor": 5, "Bonefield Hyena": 4, "Thornback Scorpid": 3,
                          "Drownbell Deckhand": 2, "Nineteen Mile": 0},
        },
        "The Bonefields": {
            "name": "The Bonefields",
            "creatures": {"Bonefield Hyena": 5, "Carrion Vulture of Tanaris": 4,
                          "Dunecrest Raptor": 3, "Sunbleached Basilisk": 2, "Marrowmaw": 0},
        },
        "Steamwheedle Approach": {
            "name": "Steamwheedle Approach",
            "creatures": {"Sunbleached Basilisk": 4, "Sunstone Elemental": 4,
                          "Thornback Scorpid": 3, "Drownbell Deckhand": 2, "Saltjaw": 0},
        },
        "The Drownbell Shore": {
            "name": "The Drownbell Shore",
            "creatures": {"Drownbell Deckhand": 5, "Drownbell Powdermonkey": 4,
                          "Sunstone Elemental": 3, "Sunbleached Basilisk": 2,
                          "The Drowned Purser": 0},
        },
    },
    "caves": {
        "The Drownbell": {
            "name": "The Drownbell",
            "creatures": {"Drownbell Cutthroat": 6, "Drownbell Bosun": 5, "Bilge Crawler": 4,
                          "Cove Tidecaller": 3,
                          "Captain Vaile Drownbell": 0, "The Bellwarden": 0},
        },
    },
}


def pools():
    """Six surface rares and the cave's boss and rare: 32 items.

    THE SPREAD IS CONTRACTED UP FRONT - EIGHT weapons of eight different types with three of them
    caster weapons, TWENTY-TWO armour pieces across cloth/leather/mail/plate, one neck and one
    trinket. Thirty classes need gear and most of them are not warriors.

    NO MAGIC RESISTANCE ANYWHERE. The rule is 45+, this band is 41-45, and only the cave boss is
    actually at 45 - a single item's worth of headroom is not worth opening that door for, so the
    whole pass stays off it and the Abyssal Sands can be the zone that introduces it properly.
    """
    return {
        "Thaka the Unburied": [
            mk("Thaka's Grave-Haft", "main_hand", "of the Bear", 46,
               "Troll iron, buried with him, dug back up by him.", weapon_type="polearm"),
            mk("Unburied Pauldrons", "shoulder", "of the Bear", 46,
               "Sand came out of the seams for a week.", armor_type="plate"),
            mk("Sandfury Ritual Wraps", "hands", "of the Sorcerer", 46,
               "Whatever was done at that pyramid, it was done with hands like these.",
               armor_type="cloth"),
            mk("Pyramid-Step Treads", "feet", "of the Monkey", 46,
               "The steps are still there. That is most of what is left.", armor_type="leather"),
        ],
        "The Last Tenant": [
            mk("The Tenant's Ledger", "main_hand", "of the Sorcerer", 45,
               "It nested in a counting house and chewed a nest out of the books. This one survived.",
               weapon_type="tome"),
            mk("Hoarded Scrap Vest", "chest", "of the Monkey", 45,
               "Goblin plate, chewed into a shape that suited something else.", armor_type="mail"),
            mk("Lintel-Fall Girdle", "waist", "of the Bear", 45,
               "Taken from under a doorway that is still standing, which is more than can be said "
               "for the door.", armor_type="plate"),
            mk("Empty-City Mantle", "shoulder", "of the Physician", 45,
               "Nobody locked anything. They just went.", armor_type="cloth"),
        ],
        "Nineteen Mile": [
            mk("Milepost Breaker", "main_hand", "of the Bear", 46,
               "Named for the stone it uprooted and carried for a season.", weapon_type="mace_2h"),
            mk("Nineteen-Mile Hide", "chest", "of the Bear", 46,
               "Road dust worked so far in it is part of the hide.", armor_type="leather"),
            mk("Drover's Vigil Bracers", "wrist", "of the Monkey", 46,
               "You hear it on the road long before the road shows you anything.", armor_type="mail"),
            mk("Roadwatch Pendant", "neck", "of the Owl", 46,
               "Carried by somebody who counted the posts out loud to stay awake."),
        ],
        "Marrowmaw": [
            mk("Marrowmaw's Rib-Hook", "main_hand", "of the Assassin", 46,
               "Not a tooth. Something it found and kept using.", weapon_type="fist_weapon"),
            mk("Bonefield Jerkin", "chest", "of the Monkey", 46,
               "There is a smell in the bonefields and this has it.", armor_type="leather"),
            mk("Hyena-Laugh Helm", "head", "of the Bear", 46,
               "You hear them before dark and then you hear them all night.", armor_type="plate"),
            mk("Carrion-Watch Leggings", "legs", "of the Sorcerer", 46,
               "Whatever stops on that road is theirs by morning.", armor_type="cloth"),
        ],
        "Saltjaw": [
            mk("Saltjaw's Spine-Rod", "main_hand", "of the Archmage", 47,
               "Brine got into it and did something nobody has explained.", weapon_type="mace_1h"),
            mk("Brine-Crusted Hauberk", "chest", "of the Bear", 47,
               "Rinse it and it comes away in your hand. Nobody rinses it.", armor_type="mail"),
            mk("Shorebreaker Gauntlets", "hands", "of the Bear", 47,
               "It works the tideline where the sand stops being sand.", armor_type="plate"),
            mk("Tidewrack Shoulderpads", "shoulder", "of the Owl", 47,
               "Everything the sea gives back, it gives back here.", armor_type="cloth"),
        ],
        "The Drowned Purser": [
            mk("The Purser's Tally-Staff", "main_hand", "of the Sorcerer", 47,
               "Still counting. That is the part people find difficult.", weapon_type="staff"),
            mk("Short-Measure Wraps", "wrist", "of the Physician", 47,
               "He was thrown over for exactly what you think.", armor_type="cloth"),
            mk("Ledger-Keeper's Jerkin", "chest", "of the Assassin", 47,
               "The book went in with him and the book is not in the pockets.", armor_type="leather"),
            mk("Drowned Purser's Signet", "trinket", "of the Owl", 47,
               "It has a number on the inside and the number is not a date."),
        ],
        "The Bellwarden": [
            mk("The Warden's Chain-Axe", "main_hand", "of the Bear", 47,
               "A length of the bell's own chain with something heavy wired to the end of it.",
               weapon_type="axe_2h"),
            mk("Careenage Scale Greaves", "legs", "of the Monkey", 47,
               "They hauled hulls over on this ground for years before anybody took the cove.",
               armor_type="mail"),
            mk("Bellwarden's Breastplate", "chest", "of the Bear", 47,
               "Whatever it is guarding, it was not told to stop.", armor_type="plate"),
            mk("Chain-Rust Band", "wrist", "of the Monkey", 47,
               "Salt water and iron, given a very long time.", armor_type="mail"),
        ],
        "Captain Vaile Drownbell": [
            mk("Vaile's Cutlass", "main_hand", "of the Assassin", 48,
               "She took this cove off people who were only trying to lift something out of it.",
               weapon_type="sword_1h"),
            mk("Drownbell's Longcoat", "chest", "of the Monkey", 48,
               "Dry on the inside, which down there is a kind of wealth.", armor_type="leather"),
            mk("Captain's Storm-Hood", "head", "of the Archmage", 48,
               "She does not go down to the bell either.", armor_type="cloth"),
            mk("Cove-Taker's Spaulders", "shoulder", "of Striking", 48,
               "Two of them went down to look at it. Neither came back up.", armor_type="mail"),
        ],
    }


# THE SAME ARITHMETIC SLIP AS THE SHIMMERING FLATS PASS, caught the same way - by the audit, on the
# contract rather than on the pools. 32 items minus 8 weapons and 2 accessories leaves 22 armour,
# and 22 does not divide by four. Two classes get six. Cloth and mail take them, because those two
# cover the most specs between them.
CONTRACT = dict(weapons=8, weapon_types=8, caster_weapons=3,
                armor={"cloth": 6, "leather": 5, "mail": 6, "plate": 5}, neck=1, trinket=1)
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
        bad.append(f"resistance stats in a 41-45 pass (the rule is 45+): {res}")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_northern_tanaris as T
    import tools.handbuilt_drownbell as D

    # THE ZONE MODULES ARE THE AUTHORITY ON THEIR OWN SUBZONES AND ROSTERS. Retyping either here is
    # how a table ends up attached to a subzone that does not exist, silently, until a player walks
    # into the rectangle.
    declared = {s[0] for s in T.SUBZONES}
    mine = set(TANARIS_ZONE["subzones"])
    if mine != declared:
        print(f"FAILED: subzones disagree: {sorted(mine ^ declared)}")
        return 1
    cave_declared = set(D.TRASH) | set(D.BOSSES)
    if cave_declared != set(DROWNBELL_CREATURES):
        print(f"FAILED: the cave's roster disagrees with the zone module: "
              f"{sorted(cave_declared ^ set(DROWNBELL_CREATURES))}")
        return 1
    print(f"subzones agree: {len(declared)} | cave roster agrees: {len(cave_declared)}")

    allc = {**TANARIS_CREATURES, **DROWNBELL_CREATURES}
    named = set(TANARIS_ZONE["open_zone"]["creatures"])
    for grp in ("subzones", "caves"):
        for s in TANARIS_ZONE[grp].values():
            named |= set(s["creatures"])
    if named != set(allc):
        print(f"FAILED: tables and roster differ: {sorted(named ^ set(allc))}")
        return 1

    # rares in subzones only, and the cave's pair pinned rather than rolled
    rares = {n for n, c in TANARIS_CREATURES.items() if c["is_boss"]}
    stray = rares & set(TANARIS_ZONE["open_zone"]["creatures"])
    if stray:
        print(f"FAILED: rares in the open_zone table, where they can never spawn: {sorted(stray)}")
        return 1
    homeless = rares - {n for s in TANARIS_ZONE["subzones"].values() for n in s["creatures"]}
    if homeless:
        print(f"FAILED: rares with no subzone: {sorted(homeless)}")
        return 1
    print(f"roster: {len(allc)} creatures, {len(rares)} surface rares all in subzones only")

    cre = json.loads(CRE.read_text(encoding="utf-8"))
    cre["creatures"].update(allc)
    CRE.write_text(json.dumps(cre, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    enc = json.loads(ENC.read_text(encoding="utf-8"))
    enc["zones"]["Northern Tanaris"] = TANARIS_ZONE
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  encounters.json: open_zone + 6 subzones + 1 cave")

    pls = pools()
    bad = audit(pls)
    if bad:
        print("\nFAILED - fix the pools, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1
    out = {"_notes": ("Named rares of Northern Tanaris and the Drownbell's boss and rare. One item "
                      "per kill. Hand-authored in tools/build_tanaris_content.py; spread checked by "
                      "its audit().")}
    out.update(pls)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"loot: {len(pls)} pools, {sum(len(v) for v in pls.values())} items, spread holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
