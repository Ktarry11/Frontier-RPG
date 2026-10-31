#!/usr/bin/env python3
"""Creatures, encounter tables and loot for Glittervein and both halves of its dungeon. Idempotent.

    PYTHONPATH=. python3 tools/build_glittervein_content.py
    cd tools && python3 generate_creatures.py     # after any kit edit (monster_kits.GLITTERVEIN_KITS)

CALIBRATED AGAINST THE ABYSSAL SANDS, which is the band directly below. 44-47 trash runs 134-166
and its rares 190-225, so this steps to trash 150-185 and rares 210-250. Calibrating against the
ADJACENT band rather than re-extrapolating from the one below it is the whole discipline - do it
the other way twice and the numbers drift upward every time anybody adds a zone.

THIS IS THE ZONE THAT INTRODUCES MAGIC RESISTANCE, and two things follow from that.

  MOST OF IT IS ON TANK GEAR. Kyle, explicitly. So the resistance pieces are plate and shields,
  with a trinket and a neck as the only exceptions - the audit below REQUIRES that, and requires
  that resistance exists at all, because a zone that was given a theme and quietly declined to use
  it is worse than one that never had it.

  AND THE BESTIARY HAS TO MAKE IT WORTH WEARING. Resistance gear is worthless against things that
  only swing swords, so everything grown from the seam hits ARCANE and everything that came with
  the water hits FROST (see monster_kits.GLITTERVEIN_KITS). A tank who brings arcane to the Choir
  and frost to the Cistern should be able to tell. The last boss uses both, so there is no single
  answer to the fight the whole zone has been teaching you to prepare for.

RARES LIVE IN SUBZONES, NOWHERE ELSE (Kyle, enforced game-wide by tools/qa_rare_placement.py). One
per surface subzone - except Lastwater, which is a camp and is flagged "safe" so nothing spawns in
it at all. See CreatureManager.is_safe_subzone: without that flag a subzone with no roster falls
through to the parent zone's table AND rolls at 5% a step against the open zone's 2%, so the
quietest place on the map would be the most dangerous one.

THE DUNGEON IS TWO MAPS AND THEY ARE "caves" IN THIS FILE'S SENSE. encounters["zones"][region]
["caves"][map name], where region is the PARENT ZONE NAME - both dungeon modules set
zone.region = "Glittervein" for exactly this lookup. Their bosses sit in the same tables at weight
0 and are pinned by boss_positions, which is the standing rule for every hand-placed fight.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as _make, C  # noqa: E402

#: Every item, with the suffix it was ASKED for, so audit() can catch a suffix that did not take.
_ASKED = []


def mk(name, slot, suffix, ilvl, flavor, **kw):
    """make(), with the requested suffix recorded.

    WHY. make() short-circuits for shields - it returns a fixed stamina/armour/block profile and
    NEVER LOOKS AT THE SUFFIX - so a shield asked for "of Arcane Protection" comes out with no
    resistance on it at all and nothing says so. That is exactly the dead data this project keeps
    finding: the pool reads as if it has six tank resistance pieces, the audit counts four, and
    without this record there is no way to tell which it is. The check is in audit().
    """
    d = _make(name, slot, suffix, ilvl, flavor, **kw)
    _ASKED.append((d, suffix))
    return d

ENC = ROOT / "data/creatures/encounters.json"
CRE = ROOT / "data/creatures/creatures.json"
RARE_LOOT = ROOT / "data/loot/glittervein_rare_loot.json"
BOSS_LOOT = ROOT / "data/loot/glittervein_dungeon_boss_loot.json"


GLITTERVEIN_CREATURES = {
    # ---- the dry rim: nothing up here grew here, it came for what comes out of the hole
    "Rimfall Jackal": C("beast_fast", 46, 47, "rimfall_jackal"),
    "Sunbleached Stalker": C("humanoid_rogue", 46, 47, "sunbleached_stalker"),
    # ---- the terraces
    "Terrace Basilisk": C("beast_large", 46, 48, "terrace_basilisk"),
    "Shardback Crawler": C("vermin_sneaky", 46, 48, "shardback_crawler"),
    # ---- the seams
    "Vein-Lit Wisp": C("elemental_caster", 47, 48, "vein_lit_wisp"),
    "Lattice-Grown": C("elemental_bruiser", 47, 49, "lattice_grown"),
    # ---- the green shelf
    "Shelf Prowler": C("beast_fast", 47, 49, "shelf_prowler"),
    "Sporefed Hulk": C("beast_large", 48, 49, "sporefed_hulk"),
    # ---- the waterline
    "Waterline Serpent": C("aquatic_basic", 48, 49, "waterline_serpent"),
    "Pool Horror": C("aquatic_basic", 48, 49, "pool_horror"),
    # ---- named rares, one per surface subzone, weight 0, never quested
    "Thirstjaw": C("beast_fast", 47, 47, "thirstjaw", True, 1.7),
    "Old Riser": C("beast_large", 47, 47, "old_riser", True, 1.8),
    "Shatterlight": C("elemental_caster", 48, 48, "shatterlight", True, 1.8),
    "Rootbound": C("beast_large", 48, 48, "rootbound", True, 1.9),
    "Stillwater": C("aquatic_basic", 49, 49, "stillwater", True, 2.0),

    # ---- THE MOTHER VEIN (48-50)
    "Sodden Digger": C("undead_basic", 48, 49, "sodden_digger"),
    "Vein Crawler": C("vermin_sneaky", 48, 49, "vein_crawler"),
    "Glass Weaver": C("elemental_caster", 49, 51, "glass_weaver"),
    "Lattice Hound": C("beast_fast", 49, 51, "lattice_hound"),
    "Brinewrought Hulk": C("elemental_bruiser", 50, 52, "brinewrought_hulk"),
    "Pitboss Grebble Vask": C("humanoid_warrior", 50, 50, "pitboss_grebble_vask", True, 2.3),
    "The Sump": C("elemental_bruiser", 50, 50, "the_sump", True, 2.3),
    "Glassmaw": C("beast_large", 51, 51, "glassmaw", True, 2.4),

    # ---- THE CISTERN (50-52)
    "Seam Singer": C("elemental_caster", 50, 52, "seam_singer"),
    "Cistern Lurker": C("aquatic_basic", 51, 52, "cistern_lurker"),
    "Resonance": C("elemental_caster", 52, 52, "resonance", True, 2.4),
    "The Siphon": C("elemental_bruiser", 52, 52, "the_siphon", True, 2.5),
    "The Standing Wave": C("aquatic_basic", 52, 52, "the_standing_wave", True, 2.5),
    "The Thirst": C("elemental_caster", 53, 53, "the_thirst", True, 2.8),
}

#: The seven bosses are hand-placed by their maps and pinned by boss_positions. They sit in these
#: tables at weight 0 so the data is complete and the roll can never produce them.
MV_BOSSES = ("Pitboss Grebble Vask", "The Sump", "Glassmaw")
CI_BOSSES = ("Resonance", "The Siphon", "The Standing Wave", "The Thirst")

GLITTERVEIN_ZONE = {
    "open_zone": {
        "name": "Glittervein",
        "creatures": {"Rimfall Jackal": 5, "Shardback Crawler": 4, "Terrace Basilisk": 4,
                      "Sunbleached Stalker": 3, "Shelf Prowler": 3, "Vein-Lit Wisp": 2},
    },
    "subzones": {
        "The Dry Rim": {
            "name": "The Dry Rim",
            "creatures": {"Rimfall Jackal": 6, "Sunbleached Stalker": 5, "Terrace Basilisk": 2,
                          "Thirstjaw": 0},
        },
        "The First Terrace": {
            "name": "The First Terrace",
            "creatures": {"Terrace Basilisk": 5, "Shardback Crawler": 4, "Rimfall Jackal": 3,
                          "Sunbleached Stalker": 2, "Old Riser": 0},
        },
        "The Vein Galleries": {
            "name": "The Vein Galleries",
            "creatures": {"Vein-Lit Wisp": 5, "Lattice-Grown": 4, "Shardback Crawler": 4,
                          "Terrace Basilisk": 2, "Shatterlight": 0},
        },
        "The Green Shelf": {
            "name": "The Green Shelf",
            "creatures": {"Shelf Prowler": 5, "Sporefed Hulk": 4, "Lattice-Grown": 3,
                          "Vein-Lit Wisp": 2, "Rootbound": 0},
        },
        "The Waterline": {
            "name": "The Waterline",
            "creatures": {"Waterline Serpent": 5, "Pool Horror": 4, "Sporefed Hulk": 3,
                          "Shelf Prowler": 2, "Stillwater": 0},
        },
        # TEN VENDORS AND A DUNGEON DOORWAY. Nothing spawns here - see is_safe_subzone.
        "Lastwater": {
            "name": "Lastwater",
            "safe": True,
            "creatures": {},
        },
    },
    "caves": {
        "The Mother Vein": {
            "name": "The Mother Vein",
            "creatures": {"Sodden Digger": 5, "Vein Crawler": 5, "Glass Weaver": 4,
                          "Lattice Hound": 4, "Brinewrought Hulk": 2,
                          **{b: 0 for b in MV_BOSSES}},
        },
        "The Cistern": {
            "name": "The Cistern",
            "creatures": {"Glass Weaver": 4, "Lattice Hound": 4, "Seam Singer": 5,
                          "Cistern Lurker": 5, "Brinewrought Hulk": 4,
                          **{b: 0 for b in CI_BOSSES}},
        },
    },
}


def rare_pools():
    """Five surface rares, 20 items.

    SPREAD CONTRACTED UP FRONT: five weapons of five different types with two caster weapons,
    thirteen armour pieces, one neck and one trinket. 20 minus 5 minus 2 is 13, which does not
    divide by four - cloth 3, leather 3, mail 4, plate 3. Writing that arithmetic down because the
    audit has caught it wrong in the CONTRACT rather than the pools three times now.

    Two resistance pieces, both plate. The surface is where the player first sees the stat; the
    dungeon is where they get a set of it.
    """
    return {
        "Thirstjaw": [
            mk("Thirstjaw's Hooked Fang", "main_hand", "of the Assassin", 50,
               "It waits at the lip, where the tired come up.", weapon_type="dagger"),
            mk("Lip-of-the-Hole Hauberk", "chest", "of the Monkey", 50,
               "Everything that climbs out of there climbs out slowly.", armor_type="mail"),
            mk("Rimwatcher's Cowl", "head", "of the Owl", 50,
               "You can see the whole pan from up there and none of it is worth watching.",
               armor_type="cloth"),
            mk("Dry Rim Pendant", "neck", "of the Eagle", 50,
               "Forty-six feet above the only water for a hundred miles."),
        ],
        "Old Riser": [
            mk("Riser's Stepping Maul", "main_hand", "of the Bear", 50,
               "The terraces are steps and something has been walking up them for a long time.",
               weapon_type="mace_2h"),
            # ---- resistance, on plate: the first piece of it in the game
            mk("Terrace-Warden Greaves", "legs", "of Arcane Protection", 50,
               "Crystal dust in every seam of them, and it does not brush out.",
               armor_type="plate"),
            mk("First-Terrace Jerkin", "chest", "of the Monkey", 50,
               "Whatever is on that bench has had the run of it for years.",
               armor_type="leather"),
            mk("Old Riser's Tooth", "trinket", "of the Bear", 50,
               "Worn flat on one side from going up the same stone."),
        ],
        "Shatterlight": [
            mk("Shatterlight Prism-Rod", "main_hand", "of the Archmage", 51,
               "Hold it up in the galleries and the walls answer.", weapon_type="wand"),
            mk("Split-Beam Mantle", "shoulder", "of the Sorcerer", 51,
               "The light in those galleries comes from the stone and goes where it likes.",
               armor_type="cloth"),
            mk("Gallery-Walker's Grips", "hands", "of the Monkey", 51,
               "Everyone who works the seams loses the pads off their fingers.",
               armor_type="leather"),
            mk("Refracted Scale Coif", "head", "of the Eagle", 51,
               "Looks like four of itself in the right light.", armor_type="mail"),
        ],
        "Rootbound": [
            mk("Rootbound's Creeping Limb", "main_hand", "of the Bear", 51,
               "Six feet of green that has had three years and no winter.",
               weapon_type="staff"),
            # ---- resistance, on plate
            mk("Greenshelf Breastplate", "chest", "of Nature Protection", 51,
               "Rust would be easier. This has something growing in the rivets.",
               armor_type="plate"),
            mk("Damp-Band Bracers", "wrist", "of the Monkey", 51,
               "The only band on that wall where anything is alive.", armor_type="mail"),
            mk("Fern-Shadow Slippers", "feet", "of the Physician", 51,
               "Quiet, on the one part of the hole that has leaf litter.", armor_type="cloth"),
        ],
        "Stillwater": [
            mk("Stillwater's Drowning Spear", "main_hand", "of the Eagle", 52,
               "Cold all the way through, in a desert, at the bottom of a hole.",
               weapon_type="polearm"),
            mk("Waterline Scale Girdle", "waist", "of the Bear", 52,
               "The mark round the rock where the pool used to stop.", armor_type="mail"),
            mk("Unmoving-Pool Guards", "shoulder", "of the Bear", 52,
               "Nothing on that water moves. Not even the surface.", armor_type="plate"),
            mk("Deep-Still Treads", "feet", "of the Monkey", 52,
               "The only standing water for a hundred miles and it stands very still.",
               armor_type="leather"),
        ],
    }


def boss_pools():
    """Seven dungeon bosses, 28 items.

    SPREAD CONTRACTED UP FRONT: seven weapons of seven different types with three caster weapons,
    nineteen armour pieces (cloth 5, leather 5, mail 5, plate 4), one neck and one trinket.
    28 - 7 - 2 = 19.

    EIGHT RESISTANCE PIECES AND SIX OF THEM ARE TANK. Kyle: "most magic resist will be on tank
    gear." So the four plate pieces and both shields carry it, plus a neck and a trinket for
    everyone else - the audit requires at least 70% of resistance items to be plate or shield, and
    requires that resistance exists at all.
    """
    return {
        # ===================== THE MOTHER VEIN =====================
        "Pitboss Grebble Vask": [
            mk("Foreman's Settling Hammer", "main_hand", "of the Bear", 53,
               "He went down with the wage book and he did not come up with it.",
               weapon_type="mace_1h"),
            # A SHIELD'S SUFFIX IS COSMETIC - make() gives shields a fixed stamina/armour/block
            # profile and ignores it, so this cannot be a resistance piece however it is labelled.
            mk("Wage-Book Bulwark", "off_hand", "of Stamina", 53,
               "Eleven months of figures, lacquered to a board and strapped to an arm.",
               weapon_type="shield"),
            mk("Pitboss's Shift Coat", "chest", "of the Monkey", 53,
               "Company issue. Nobody has issued anything down here in a year.",
               armor_type="leather"),
            mk("Evacuation-Order Band", "wrist", "of the Owl", 53,
               "He signed it. He did not read it to anybody.", armor_type="cloth"),
        ],
        "The Sump": [
            mk("Sump-Drawn Pumprod", "main_hand", "of the Archmage", 53,
               "Four hundred feet of pipe and this is the end that was in the water.",
               weapon_type="staff"),
            # ---- resistance on plate
            mk("Pump-Chief's Plate Harness", "chest", "of Frost Protection", 53,
               "Six pumps. Four were the Company's. These are not.", armor_type="plate"),
            mk("Silt-Choked Scale Leggings", "legs", "of the Bear", 53,
               "Whatever the pumps were lifting, it was not only water.", armor_type="mail"),
            mk("Standing-Water Cord", "waist", "of the Physician", 53,
               "Damp to the touch and it has been out of the gallery for a year.",
               armor_type="cloth"),
        ],
        "Glassmaw": [
            mk("Glassmaw's Shearing Edge", "main_hand", "of the Assassin", 54,
               "A vug is a room made of knives and this is one of its teeth.",
               weapon_type="dagger"),
            mk("Vug-Lined Shoulderguards", "shoulder", "of the Monkey", 54,
               "The walls of those rooms ARE the loot, which is a problem when they bite.",
               armor_type="leather"),
            mk("Crystal-Cut Chain Vest", "chest", "of the Eagle", 54,
               "Every link scored, none of them through.", armor_type="mail"),
            mk("Swallowed-Light Hood", "head", "of the Sorcerer", 54,
               "It goes dark where that thing has been.", armor_type="cloth"),
        ],
        # ===================== THE CISTERN =====================
        "Resonance": [
            mk("Struck-Note Chime", "main_hand", "of the Archmage", 55,
               "Ring it once and the whole seam answers, which is how everyone here died.",
               weapon_type="mace_2h"),
            # ---- resistance on plate: the Choir is pure arcane, so this is the fight it is for
            mk("Choir-Deaf Greatplate", "chest", "of Arcane Protection", 55,
               "Thick enough that the note arrives late.", armor_type="plate"),
            mk("Sympathetic Lattice Gloves", "hands", "of the Sorcerer", 55,
               "They hum. Not loudly. Constantly.", armor_type="cloth"),
            mk("Pitch-Shattered Buckler", "off_hand", "of Stamina", 55,
               "Cracked across in a pattern that is too regular to be damage.",
               weapon_type="shield"),
        ],
        "The Siphon": [
            mk("Siphon's Drawing Arm", "main_hand", "of the Eagle", 55,
               "It is the proof. The water does not rise on its own and this is what raises it.",
               weapon_type="fist_weapon"),
            # ---- resistance on plate
            mk("Drawn-Dry Legplates", "legs", "of Frost Protection", 55,
               "Cold enough to ache, in a desert, below a desert.", armor_type="plate"),
            mk("Lift-and-Pull Scale Belt", "waist", "of the Monkey", 55,
               "Five zones of water came up through something shaped like this.",
               armor_type="mail"),
            mk("Running-Dry Charm", "trinket", "of Arcane Protection", 55,
               "Ulla was right. This is what being right looks like when you dig it up."),
        ],
        "The Standing Wave": [
            mk("Wave-Held Trident", "main_hand", "of the Eagle", 56,
               "Water does not stand up. This has been standing up for three years.",
               weapon_type="polearm"),
            mk("Upright-Water Vestments", "chest", "of the Archmage", 56,
               "Soaked through and it will not dry and it will not drip.", armor_type="cloth"),
            mk("Unbroken-Surface Boots", "feet", "of the Monkey", 56,
               "You can walk on it. You should not want to.", armor_type="leather"),
            # ---- resistance on plate
            mk("Lattice-Bound Spaulders", "shoulder", "of Frost Protection", 56,
               "The crystal is holding it. That is the whole sentence.", armor_type="plate"),
        ],
        "The Thirst": [
            mk("The Drinking Lattice", "main_hand", "of the Archmage", 57,
               "Five zones of water, three years, and this is the shape it all went through.",
               weapon_type="tome"),
            # ---- resistance: the last plate piece, and the fight uses BOTH schools
            mk("Thirst-Denying Battleplate", "chest", "of Arcane Protection", 57,
               "The seam gave up trying to grow through this one.", armor_type="plate"),
            mk("Water-Table Pendant", "neck", "of the Owl", 57,
               "A walled city died of thirst with a well in the middle of it. This is why."),
            mk("Aquifer-Walker's Striders", "feet", "of the Assassin", 57,
               "You come out where the water comes out, which is beside the camp you started at.",
               armor_type="leather"),
        ],
    }


RARE_CONTRACT = dict(weapons=5, weapon_types=5, caster_weapons=2,
                     armor={"cloth": 3, "leather": 3, "mail": 4, "plate": 3},
                     neck=1, trinket=1, min_resist=2, tank_resist_fraction=1.0)
#: Nine weapons because SHIELDS COUNT AS WEAPONS here - they carry a weapon_type. 28 - 9 - 2 = 17
#: armour, which is cloth 5, leather 4, mail 3, plate 5. Plate is the big class on purpose: it is
#: where the resistance lives, and shields cannot hold any (see mk above).
BOSS_CONTRACT = dict(weapons=9, weapon_types=8, caster_weapons=3,
                     armor={"cloth": 5, "leather": 4, "mail": 3, "plate": 5},
                     neck=1, trinket=1, min_resist=6, tank_resist_fraction=0.70)
CASTER_WEAPONS = {"staff", "wand", "tome", "idol", "libram", "totem", "mace_1h"}


def audit(pls, contract, label):
    import collections
    items = [i for p in pls.values() for i in p]
    w = [i for i in items if i.get("weapon_type")]
    arm = collections.Counter(i["armor_type"] for i in items if i.get("armor_type"))
    bad = []
    if len(w) != contract["weapons"]:
        bad.append(f"{label}: {len(w)} weapons, contract says {contract['weapons']}")
    types = {i["weapon_type"] for i in w}
    if len(types) != contract["weapon_types"]:
        bad.append(f"{label}: weapon types {sorted(types)} - want {contract['weapon_types']}")
    caster = [i for i in w if i["weapon_type"] in CASTER_WEAPONS]
    if len(caster) < contract["caster_weapons"]:
        bad.append(f"{label}: {len(caster)} caster weapons, want {contract['caster_weapons']}")
    for t, n in contract["armor"].items():
        if arm[t] != n:
            bad.append(f"{label}: {t} {arm[t]}, contract says {n}")
    for s in ("neck", "trinket"):
        got = sum(1 for i in items if i["slot"] == s)
        if got != contract[s]:
            bad.append(f"{label}: {s} {got}, contract says {contract[s]}")

    # ---- THE RESISTANCE CONTRACT, which is the one thing this zone exists to get right
    res = [i for i in items
           if any("resistance" in k for k in (i.get("secondary_stats") or {}))
           or any("resistance" in k for k in (i.get("primary_stats") or {}))]
    if len(res) < contract["min_resist"]:
        bad.append(f"{label}: {len(res)} resistance pieces, want at least "
                   f"{contract['min_resist']} - this is the zone that introduces the stat and a "
                   f"theme nobody used is worse than one nobody had")
    # ---- A SUFFIX THAT DID NOT TAKE is dead data, and it reads as content that is there.
    for (d, suffix) in _ASKED:
        if ("Protection" in suffix or "Resistance" in suffix) and d in items:
            stats = dict(d.get("secondary_stats") or {}, **(d.get("primary_stats") or {}))
            if not any("resistance" in k for k in stats):
                bad.append(f"{label}: {d['name']} was asked for '{suffix}' and came out with no "
                           f"resistance stat at all - make() ignored it (shields do this)")
    if res:
        tank = [i for i in res
                if i.get("armor_type") == "plate" or i.get("weapon_type") == "shield"]
        frac = len(tank) / len(res)
        if frac < contract["tank_resist_fraction"]:
            bad.append(f"{label}: only {len(tank)}/{len(res)} resistance pieces are plate or "
                       f"shield ({frac:.0%}); Kyle: most magic resist goes on TANK gear, want "
                       f"{contract['tank_resist_fraction']:.0%}")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_glittervein as G
    import tools.handbuilt_mother_vein as MV
    import tools.handbuilt_cistern as CI

    bad = []

    declared = {s[0] for s in G.SUBZONES}
    mine = set(GLITTERVEIN_ZONE["subzones"])
    if mine != declared:
        bad.append(f"subzones disagree with the zone module: {sorted(mine ^ declared)}")

    named = set(GLITTERVEIN_ZONE["open_zone"]["creatures"])
    for s in GLITTERVEIN_ZONE["subzones"].values():
        named |= set(s["creatures"])
    for c in GLITTERVEIN_ZONE["caves"].values():
        named |= set(c["creatures"])
    if named != set(GLITTERVEIN_CREATURES):
        bad.append(f"tables and roster differ: {sorted(named ^ set(GLITTERVEIN_CREATURES))}")

    bosses = {n for n, c in GLITTERVEIN_CREATURES.items() if c["is_boss"]}
    stray = bosses & set(GLITTERVEIN_ZONE["open_zone"]["creatures"])
    if stray:
        bad.append(f"rares in the open_zone table, where they can never spawn: {sorted(stray)}")
    subzone_named = {n for s in GLITTERVEIN_ZONE["subzones"].values() for n in s["creatures"]}
    cave_named = {n for c in GLITTERVEIN_ZONE["caves"].values() for n in c["creatures"]}
    homeless = bosses - subzone_named - cave_named
    if homeless:
        bad.append(f"named creatures with no subzone and no cave: {sorted(homeless)}")

    # EVERY MOB THE MAPS PLACE BY HAND MUST EXIST. world/cave_spawns.py raises on a pack member
    # with no creature entry, which is why the Deep Bloom sat unregistered for a pass - and the
    # failure is at zone-load, i.e. the whole game, not just this dungeon.
    for mod, key in ((MV, "The Mother Vein"), (CI, "The Cistern")):
        placed = {n for (_x, _y, n, _l) in mod.TRASH} | set(mod.BOSSES)
        table = set(GLITTERVEIN_ZONE["caves"][key]["creatures"])
        if placed - table:
            bad.append(f"{key}: hand-placed mobs missing from its table: {sorted(placed - table)}")
        if placed - set(GLITTERVEIN_CREATURES):
            bad.append(f"{key}: hand-placed mobs missing from the roster: "
                       f"{sorted(placed - set(GLITTERVEIN_CREATURES))}")

    rp, bp = rare_pools(), boss_pools()
    if set(bp) != bosses - set(subzone_named):
        bad.append(f"boss loot pools do not match the dungeon bosses: "
                   f"{sorted(set(bp) ^ (bosses - set(subzone_named)))}")
    bad += audit(rp, RARE_CONTRACT, "surface rares")
    bad += audit(bp, BOSS_CONTRACT, "dungeon bosses")

    if bad:
        print("FAILED - fix the content, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    print(f"roster {len(GLITTERVEIN_CREATURES)} | {len(bosses)} named "
          f"({len(bosses) - len(bp)} surface rares in subzones, {len(bp)} dungeon bosses)")

    cre = json.loads(CRE.read_text(encoding="utf-8"))
    cre["creatures"].update(GLITTERVEIN_CREATURES)
    CRE.write_text(json.dumps(cre, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    enc = json.loads(ENC.read_text(encoding="utf-8"))
    enc["zones"]["Glittervein"] = GLITTERVEIN_ZONE
    ENC.write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  encounters.json: open_zone + 6 subzones (Lastwater safe) + 2 dungeon maps")

    for path, pls, note in (
            (RARE_LOOT, rp, "Named rares of Glittervein. One item per kill."),
            (BOSS_LOOT, bp, "Bosses of The Mother Vein and The Cistern.")):
        out = {"_notes": note + " Hand-authored in tools/build_glittervein_content.py; spread and "
                                "resistance placement checked by its audit()."}
        out.update(pls)
        path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"loot: {len(rp)} rare pools ({sum(len(v) for v in rp.values())} items), "
          f"{len(bp)} boss pools ({sum(len(v) for v in bp.values())} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
