#!/usr/bin/env python3
"""Deadwind Pass's creatures, rares, bosses, encounter tables, loot and gathering: both maps of the pass, its two
caves and the Exclusion Zone. Idempotent.

    PYTHONPATH=. python3 tools/build_deadwind_content.py

The vision is docs/deadwind_brief.md (Kyle, 17 Nov 2026: "a disgusting mix of mutation, radiation, HORROR!!!!!",
"Make it dark and disgusting") and the story docs/deadwind_quest_plan.md. The sprites are Kyle's Deadwind creature
sheets (sliced 18 Nov 2026 to assets/creatures/_src/deadwind/); this script copies the ones it uses into
assets/creatures/ and creature_sprites.py names them. Two are kept off every hostile: dw_twice_ogre is Grull the
Younger and dw_echo is the Bridge Echo (tools/build_deadwind.py).

    DEADWIND WEST (55-57)   the mutated wild in the dead forest: tumour wolves, pustule boars, many-eyed crows
      The Cracked Tunnel      the slag crawlers in the glowing rock
      Morgan's Plot           the dead who don't stay down
      Coachman's Bend         the same                                               rare: the Wagon Driver
      Deadwind Ravine         Grosh'gok's ogres, swollen and fused
      Grosh'gok Compound      the same, and their chained beasts                     rare: Mog'grak the Twice-Born
      The Widows' Wood        the widows, bloated, their egg sacs glowing
      The Sickwater, the Black Tarn   leeches and the things that grow in the tarn
      Delgado's Fence, Deadman's Crossing   safe
    DEADWIND EAST (56-58)   the stuck: wolves at three ages, hounds that flicker, things with too many of themselves
      The Sleeping Gorge      slag and seep wyrms on the floor
      The Broken Bridge       the onlookers who came to watch the glow, and stayed
      The Drowned Hollow      the mud horrors in the mere                            rare: the Crow King
      The Vice                shard wraiths and the many moments
      Karazhan                the tower's spill: its servants, its stablehand, its ballroom, its books
      The Stopped Places      the same, thickest                                     rare: Old Three-Heads
      The Hanging Slide       wolves and wraiths
      The Rupture             the fallout's worst: bloated walkers, fused masses, the many-armed
      Ariden's Camp           safe
    THE WIDOWS' NEST (56-58)  funnel widows and their hatchlings                    the Silk Mother
    THE DROWNED SEEP (57-58)  leeches, drain horrors, the drowned                    the Drowned Thing
    THE EXCLUSION ZONE (57-60)   six bosses, round the rim and in along the spoke:
        GRISTLEMAW            57  a heap of Grosh'gok's ogres moving as one body; it pulls more of the heap up
        BROODMOTHER VEXIS     58  the brood's mother, fused with her clutch; hatches them on the party
        THE GLOW-EATER        58  eats the seep in the Bubbler Pools and grows; the longer it lives the harder it hits
        ARCHIVIST NINE        59  Karazhan's librarian at nine ages at once; reads you your own death
        THE STOPPED MAN       59  a liquidator frozen mid-scream, Halyna's brother Mykola; time stops round him
        THE WOUND'S HEART     60  the knot that keeps every copy; the Elephant's Foot. Drops the T0 bracers token

THE NUMBERS are the game's 55-60 band (Azshara's open world, caves and dungeons, measured): trash basic 4L - 10, a
boss's 10L - 200; rares at boss multiplier 2.2, cave bosses 2.5, dungeon bosses 2.5 and 2.8 for the last. Every boss
carries something dangerous (tools/qa_dungeon_boss_turns.py).

LOOT. One item per kill. Rares and cave bosses carry four (rares item level = level + 3, caves + 2). The Exclusion
Zone's bosses carry three, like every token dungeon's (+ 3), and no bracers among them, because the T0 bracers token is its (Kyle, 16 Nov 2026: "we will move bracers to
deadwind"): 20% a boss, always from the Wound's Heart (data/items/set_tokens.json).
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402
from tools.build_plaguelands_dungeons_content import (  # noqa: E402
    opener, phase, stun_hit, shell, heal, last_gasp, hit_with)
from tools import handbuilt_deadwind_west as DWW  # noqa: E402
from tools import handbuilt_deadwind_east as DWE  # noqa: E402
from tools import handbuilt_deadwind_caves as DWC  # noqa: E402
from tools import handbuilt_exclusion_zone as EZ  # noqa: E402

LOOT = ROOT / "data/loot/deadwind_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
TOKENS = ROOT / "data/items/set_tokens.json"
SRC = ROOT / "assets/creatures/_src/deadwind"
WEST, EAST = DWW.NAME, DWE.NAME
NEST, SEEP, EXZ = DWC.NEST, DWC.SEEP, EZ.NAME
ZONE_LEVELS = {WEST: [55, 57], EAST: [56, 58], NEST: [56, 58], SEEP: [57, 58],
               **{f: list(EZ.LEVELS[f]) for f in EZ.FLOORS}}
#: the dungeon's roster as a whole (each floor is checked against its own band in check())
EXZ_BAND = (57, 60)
ARMOUR = ("plate", "mail", "leather", "cloth")
#: the sprites that are people, never hostiles
NOT_HOSTILE = {"dw_twice_ogre", "dw_echo"}


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, boss multiplier or None, sprite, where, kit shape, school, [ability names])
#: where: an open map, or a cave / the dungeon by name
ROSTER = {
    # ================================================================ Deadwind West
    "Tumour Wolf":           ("beast_fast", 55, 57, None, "dw_tumour_wolf", WEST, "beast", "nature",
                              ["Bite", "Lunge", "Weeping Sores"]),
    "Pustule Boar":          ("beast_large", 55, 56, None, "dw_pustule_boar", WEST, "warrior", "physical",
                              ["Tusk", "Boar Charge", "Calloused Hide"]),
    "Many-Eyed Crow":        ("beast_fast", 55, 57, None, "dw_many_eyed_crow", WEST, "beast", "physical",
                              ["Peck", "Swoop", "Pecked Raw"]),
    "Fused Bat":             ("beast_fast", 56, 57, None, "dw_fused_bat", WEST, "beast", "nature",
                              ["Bite", "Screeching Dive", "Fevered Bite"]),
    "Tunnel Slagcrawler":    ("elemental_bruiser", 55, 56, None, "dw_slag_crawler", WEST, "bruiser", "nature",
                              ["Slag Claw", "Glowing Spit", "Corroded"]),
    "Plot Risen":            ("undead_warrior", 55, 56, None, "dw_aged_walker", WEST, "warrior", "shadow",
                              ["Grave Fist", "Clawing Swipe", "Grave-Dust Hide"]),
    "Grave Ooze":            ("elemental_caster", 55, 56, None, "dw_bone_ooze", WEST, "caster", "nature",
                              ["Bone Spit", "Ooze Splash", "Marrow Rot"]),
    "Grosh'gok Brute":       ("humanoid_warrior", 56, 57, None, "dw_ogre_brute", WEST, "bruiser", "physical",
                              ["Swollen Fist", "Ground Pound", "Crushed"]),
    "Grosh'gok Two-Face":    ("humanoid_warrior", 56, 57, None, "dw_two_faced_ogre", WEST, "warrior", "physical",
                              ["Club", "Both Mouths Bite", "Two Heads, One Hide"]),
    "Grosh'gok Sore-Shaman": ("humanoid_caster", 56, 57, None, "dw_sore_shaman", WEST, "caster", "nature",
                              ["Pus Bolt", "Burst the Sores", "Shaman's Rot"]),
    "Chained Mauler":        ("beast_large", 56, 57, None, "dw_chained_mauler", WEST, "bruiser", "physical",
                              ["Maul", "Chain Sweep", "Hamstrung"]),
    "Deadwind Widow":        ("vermin_sneaky", 55, 57, None, "dw_widow", WEST, "beast", "nature",
                              ["Fang", "Pounce", "Glowing Venom"]),
    "Widow Hatchlings":      ("vermin_swarm", 55, 56, None, "dw_widow_hatchlings", WEST, "beast", "nature",
                              ["Swarm Bite", "Skitter Over", "Hatchling Venom"]),
    "Glowsac Broodmother":   ("vermin_sneaky", 56, 57, None, "dw_broodmother", WEST, "caster", "nature",
                              ["Venom Spit", "Burst Sac", "Brood Venom"]),
    "Sickwater Leech":       ("vermin_sneaky", 55, 56, None, "dw_cave_leech", WEST, "beast", "nature",
                              ["Latch", "Drain", "Leech Fever"]),
    "Tarn Horror":           ("elemental_bruiser", 56, 57, None, "dw_mud_horror", WEST, "bruiser", "nature",
                              ["Mud Fist", "Drowning Slam", "Sucking Mud"]),
    "Dissolving Stag":       ("beast_large", 55, 57, None, "dw_cage_deer", WEST, "warrior", "physical",
                              ["Antler Rake", "Trample", "Bare Ribs"]),
    "The Wagon Driver":      ("undead_warrior", 56, 56, 2.2, "dw_rare_wagon_driver", WEST, "rare", "shadow",
                              ["Coachwhip", "The Crash", "Thrown from the Seat", "Again, and Again"]),
    "Mog'grak the Twice-Born": ("humanoid_warrior", 57, 57, 2.2, "dw_rare_moggrak", WEST, "rare", "physical",
                                ["Two Fists", "Clan Stomp", "Held by the Little One", "Both of Him"]),
    # ================================================================ Deadwind East
    "Three-Age Wolf":        ("beast_fast", 56, 58, None, "dw_three_age_wolf", EAST, "beast", "physical",
                              ["Young Bite", "Old Lunge", "Torn Three Ways"]),
    "Flicker Hound":         ("beast_fast", 56, 58, None, "dw_flicker_hound", EAST, "beast", "arcane",
                              ["Bite from Nowhere", "Flicker", "Out of Step"]),
    "Gorge Slagcrawler":     ("elemental_bruiser", 56, 57, None, "dw_slag_crawler", EAST, "bruiser", "nature",
                              ["Slag Claw", "Molten Spray", "Corroded"]),
    "Seep Wyrm":             ("beast_fast", 56, 58, None, "dw_seep_wyrm", EAST, "caster", "nature",
                              ["Glowing Bite", "Seep Spray", "Wyrm Rot"]),
    "Bridge Onlooker":       ("undead_basic", 56, 57, None, "dw_aged_walker", EAST, "beast", "shadow",
                              ["Grasp", "Pull Closer", "Ash in the Lungs"]),
    "Hollow Mudhorror":      ("elemental_bruiser", 57, 58, None, "dw_mud_horror", EAST, "bruiser", "nature",
                              ["Mud Fist", "Mire Slam", "Sucking Mud"]),
    "Shard Wraith":          ("undead_caster", 57, 58, None, "dw_shard_wraith", EAST, "caster", "arcane",
                              ["Shard Bolt", "Shatter", "Splintered Moment"]),
    "Many Moments":          ("undead_warrior", 57, 58, None, "dw_many_moments", EAST, "warrior", "arcane",
                              ["Strike, Strike, Strike", "All at Once", "Somewhere Else"]),
    "Arcane Anomaly":        ("elemental_caster", 57, 58, None, "dw_arcane_anomaly", EAST, "caster", "arcane",
                              ["Arcane Bolt", "Unravel", "Mana Leak"]),
    "Spectral Servant":      ("undead_caster", 56, 57, None, "dw_spectral_servant", EAST, "caster", "frost",
                              ["Cold Tray", "Dinner Is Served", "The Master's Chill"]),
    "Spectral Stablehand":   ("undead_warrior", 56, 57, None, "dw_spectral_stablehand", EAST, "warrior", "shadow",
                              ["Pitchfork", "Spectral Kick", "Old Livery"]),
    "Ballroom Phantom":      ("undead_caster", 57, 58, None, "dw_dancing_ghost", EAST, "caster", "shadow",
                              ["Cold Embrace", "The Last Waltz", "Danced Off Your Feet"]),
    "Violet Sentinel":       ("elemental_bruiser", 57, 58, None, "dw_violet_armour", EAST, "warrior", "arcane",
                              ["Halberd", "Sweeping Halberd", "Enchanted Plate"]),
    "Book Flock":            ("elemental_caster", 56, 58, None, "dw_book_flock", EAST, "caster", "arcane",
                              ["Paper Cut", "Whirl of Pages", "Wrong Chapter"]),
    "Bloated Walker":        ("undead_basic", 57, 58, None, "dw_bloated_walker", EAST, "bruiser", "nature",
                              ["Swollen Fist", "Burst", "Spattered"]),
    "Fused Mass":            ("elemental_bruiser", 57, 58, None, "dw_fused_abomination", EAST, "bruiser", "physical",
                              ["Many Fists", "Heave", "Pinned Under"]),
    "Many-Armed Thing":      ("elemental_bruiser", 57, 58, None, "dw_many_arms", EAST, "warrior", "physical",
                              ["Grab", "Every Arm", "Held Fast"]),
    "Old Three-Heads":       ("beast_large", 58, 58, 2.2, "dw_rare_three_heads", EAST, "rare", "physical",
                              ["Young Bite", "Old Howl", "Three Ages at Once", "The Last of Him"]),
    "The Crow King":         ("beast_fast", 58, 58, 2.2, "dw_rare_crow_king", EAST, "rare", "shadow",
                              ["A Hundred Beaks", "Murder of Crows", "Pinned by Talons", "Every Crow in the Pass"]),
    # ================================================================ The Widows' Nest
    "Funnel Widow":          ("vermin_sneaky", 56, 57, None, "dw_widow", NEST, "beast", "nature",
                              ["Fang", "Drop from the Silk", "Funnel Venom"]),
    "Nest Hatchlings":       ("vermin_swarm", 56, 57, None, "dw_widow_hatchlings", NEST, "beast", "nature",
                              ["Swarm Bite", "Skitter Over", "Hatchling Venom"]),
    "Cocoon Burrower":       ("vermin_sneaky", 57, 58, None, "dw_cave_burrower", NEST, "bruiser", "physical",
                              ["Burrowing Bite", "Erupt", "Wrapped"]),
    "The Silk Mother":       ("vermin_sneaky", 58, 58, 2.5, "dw_boss_silk_mother", NEST, "cave_boss", "nature", []),
    # ================================================================ The Drowned Seep
    "Seep Leech":            ("vermin_sneaky", 57, 58, None, "dw_cave_leech", SEEP, "beast", "nature",
                              ["Latch", "Drain", "Leech Fever"]),
    "Drain Horror":          ("elemental_bruiser", 57, 58, None, "dw_mud_horror", SEEP, "bruiser", "nature",
                              ["Mud Fist", "Undertow", "Sucking Mud"]),
    "Bloated Drowner":       ("undead_basic", 57, 58, None, "dw_bloated_walker", SEEP, "bruiser", "nature",
                              ["Waterlogged Fist", "Burst", "Spattered"]),
    "The Drowned Thing":     ("elemental_bruiser", 58, 58, 2.5, "dw_boss_drowned_thing", SEEP, "cave_boss", "nature", []),
    # ================================================================ The Exclusion Zone
    "Exclusion Ogre":        ("humanoid_warrior", 57, 58, None, "dw_leaking_ogre", EXZ, "", "physical", []),
    "Heaped Abomination":    ("elemental_bruiser", 57, 58, None, "dw_fused_abomination", EXZ, "", "physical", []),
    "Bursting Walker":       ("undead_basic", 57, 58, None, "dw_bloated_walker", EXZ, "", "nature", []),
    "Brood Seepwidow":       ("vermin_sneaky", 58, 59, None, "dw_widow", EXZ, "", "nature", []),
    "Brood Hatchling Swarm": ("vermin_swarm", 58, 59, None, "dw_widow_hatchlings", EXZ, "", "nature", []),
    "Brood Burrower":        ("vermin_sneaky", 58, 59, None, "dw_cave_burrower", EXZ, "", "physical", []),
    "Bubbler Slagcrawler":   ("elemental_bruiser", 59, 60, None, "dw_slag_crawler", EXZ, "", "nature", []),
    "Bubbler Wyrm":          ("beast_fast", 58, 59, None, "dw_seep_wyrm", EXZ, "", "nature", []),
    "Bubbler Ooze":          ("elemental_caster", 58, 59, None, "dw_bone_ooze", EXZ, "", "nature", []),
    "Archive Wraith":        ("undead_caster", 58, 59, None, "dw_shard_wraith", EXZ, "", "arcane", []),
    "Archive Anomaly":       ("elemental_caster", 58, 59, None, "dw_arcane_anomaly", EXZ, "", "arcane", []),
    "Hollow Guardian":       ("elemental_bruiser", 58, 59, None, "dw_violet_armour", EXZ, "", "arcane", []),
    "Swarming Pages":        ("elemental_caster", 58, 59, None, "dw_book_flock", EXZ, "", "arcane", []),
    "Stopped Volunteer":     ("undead_warrior", 59, 60, None, "dw_stopped_soldier", EXZ, "", "arcane", []),
    "Moment Without End":    ("undead_warrior", 59, 60, None, "dw_many_moments", EXZ, "", "arcane", []),
    "Aged Volunteer":        ("undead_basic", 59, 60, None, "dw_aged_walker", EXZ, "", "shadow", []),
    "Gristlemaw":            ("elemental_bruiser", 57, 57, 2.5, "fz_boss_gristlemaw", EXZ, "", "physical", []),
    "Broodmother Vexis":     ("vermin_sneaky", 58, 58, 2.5, "fz_boss_vexis", EXZ, "", "nature", []),
    "The Glow-Eater":        ("elemental_bruiser", 58, 58, 2.5, "fz_boss_glow_eater", EXZ, "", "nature", []),
    "Archivist Nine":        ("undead_caster", 59, 59, 2.5, "fz_boss_archivist", EXZ, "", "arcane", []),
    "The Stopped Man":       ("undead_warrior", 59, 59, 2.5, "fz_boss_stopped_man", EXZ, "", "arcane", []),
    "The Wound's Heart":     ("elemental_caster", 60, 60, 2.8, "fz_boss_wound_heart", EXZ, "", "nature", []),
}
RARES = {n for n, r in ROSTER.items() if r[3] and r[5] in (WEST, EAST)}
CAVE_BOSSES = {n for n, r in ROSTER.items() if r[3] and r[5] in (NEST, SEEP)}
EZ_BOSSES = [b[2] for b in EZ.BOSS_LIST]
EZ_FINAL = "The Wound's Heart"
EZ_TRASH = [n for n, r in ROSTER.items() if r[5] == EXZ and not r[3]]


def ez_floor_creatures(floor):
    """One floor's bosses and trash, in the roster's order."""
    on = {b[2] for b in EZ.FLOOR[floor]["bosses"]} | {m for p in EZ._trash(floor) for (_x, _y, m, _l) in p}
    return [n for n in ROSTER if n in on]


def summon(name, creature, cooldown, max_alive, max_casts):
    return dict(name=name, kind="summon", amount=0, cooldown=cooldown, mana_cost=0,
                summon={"name": creature, "template": ROSTER[creature][0], "kit": kit_slug(creature),
                        "count": 1, "level_offset": -1, "max_alive": max_alive, "max_casts": max_casts})


def open_kit(name):
    """The open world's and the caves' trash, and the rares, in Azshara's shapes."""
    template, lo, hi, mult, _sp, _w, shape, s, names = ROSTER[name]
    t = T(hi)
    dispel = {"nature": "poison", "shadow": "curse", "frost": "magic", "arcane": "magic"}.get(s)
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                dot(names[2], int(t * 0.27), 3, 3, school=s, **({"dispel_type": dispel} if dispel else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 220})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel or "magic")]
    if shape == "bruiser":
        return [dmg(names[0], t + 10, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -24}, school=s)]
    # a rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand or its ward
    b = B(hi)
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s),
            dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5, school=s), last]


def boss_kit(level, school, basic, second, heavy, spread, mechanic, phase_name, *, signature, aoe=True, extra=()):
    """Every boss carries something dangerous (Kyle, 16 Nov 2026: "make sure bosses are not just debuffing")."""
    b = B(level)
    kit = [opener(basic, b, school), dmg(second, int(b * 0.88), cooldown=4, school=school),
           dmg(heavy, int(b * 1.3), cooldown=4, school=school)]
    kit.append(dmg(spread, int(b * 0.68), cooldown=5, school=school, is_aoe=True) if aoe
               else dot(spread, int(b * 0.36), 5, 4, school=school))
    if mechanic:
        kit.append(mechanic)
    kit.extend(extra)
    kit.extend(signature)
    kit.append(phase(phase_name, level, school))
    return kit


def trash3(level, basic, second, third, school="physical"):
    t = T(level)
    return [dmg(basic, t, school=school), second(t), third(t)]


def kits():
    k = {n: open_kit(n) for n, r in ROSTER.items() if r[5] in (WEST, EAST) or (r[6] and r[6] != "cave_boss")}
    # ---- the caves' bosses
    k["The Silk Mother"] = boss_kit(          # the widow queen grown into her own cocoon
        58, "nature", "Mandibles", "Silk Lash", "Crushing Legs", "Venom Rain",
        summon("The Brood Answers", "Nest Hatchlings", 4, 3, 6), "The Cocoon Splits",
        signature=[stun_hit("Cocooned", int(B(58) * 0.9), cooldown=6, school="nature"),
                   dot("Glowing Venom", int(B(58) * 0.5), 5, 4, school="nature", dispel_type="poison"),
                   last_gasp("The Funnel Closes", 58, "nature")])
    k["The Drowned Thing"] = boss_kit(        # mud, roots and every animal the sump ever drowned
        58, "nature", "Sodden Fist", "Root Lash", "Everything It Drowned", "Sump Wave",
        stun_hit("Pulled Under", int(B(58) * 0.9), cooldown=6, school="nature"), "Swollen with the Seep",
        extra=[heal("Drinks the Seep", int(B(58) * 1.1), cooldown=6, school="nature")],
        signature=[hit_with("Lungful of Seep", int(B(58) * 0.8), {"haste": -15, "healing_power": -40}, 3,
                            school="nature", cooldown=5),
                   last_gasp("The Sump Overflows", 58, "nature")])
    # ---- the Exclusion Zone's trash
    k["Exclusion Ogre"] = trash3(58, "Leaking Fist", lambda t: dmg("Ogre Slam", int(t * 1.3), cooldown=4),
                                 lambda t: dot("Weeping Seep", int(t * 0.28), 4, 3, school="nature",
                                               dispel_type="disease"))
    k["Heaped Abomination"] = trash3(58, "Many Fists", lambda t: dmg("Heave", int(t * 0.7), cooldown=4, is_aoe=True),
                                     lambda t: stun_hit("Pinned Under", int(t * 0.9), cooldown=6))
    k["Bursting Walker"] = trash3(58, "Swollen Fist",
                                  lambda t: dmg("Burst", int(t * 0.75), cooldown=5, school="nature", is_aoe=True),
                                  lambda t: dot("Spattered", int(t * 0.28), 4, 3, school="nature",
                                                dispel_type="disease"), school="nature")
    k["Brood Seepwidow"] = trash3(59, "Fang", lambda t: dmg("Pounce", int(t * 1.3), cooldown=4),
                                  lambda t: dot("Seepwidow Venom", int(t * 0.3), 4, 3, school="nature",
                                                dispel_type="poison"))
    k["Brood Hatchling Swarm"] = trash3(59, "Swarm Bite",
                                        lambda t: dmg("Skitter Over", int(t * 0.7), cooldown=4, is_aoe=True),
                                        lambda t: dot("Hatchling Venom", int(t * 0.26), 4, 3, school="nature",
                                                      dispel_type="poison"))
    k["Brood Burrower"] = trash3(59, "Burrowing Bite", lambda t: stun_hit("Erupt", int(t * 1.0), cooldown=5),
                                 lambda t: hit_with("Wrapped", int(t * 0.8), {"haste": -12}, 3, school="nature"))
    k["Bubbler Slagcrawler"] = trash3(59, "Slag Claw",
                                      lambda t: dmg("Molten Spray", int(t * 0.72), cooldown=4, school="fire", is_aoe=True),
                                      lambda t: hit_with("Corroded", int(t * 0.8), {"armor": -160}, 3, school="nature"))
    k["Bubbler Wyrm"] = trash3(59, "Glowing Bite", lambda t: dmg("Seep Spray", int(t * 0.72), cooldown=4,
                                                                  school="nature", is_aoe=True),
                               lambda t: dot("Wyrm Rot", int(t * 0.28), 4, 3, school="nature", dispel_type="poison"),
                               school="nature")
    k["Bubbler Ooze"] = trash3(59, "Bone Spit", lambda t: dmg("Bubbling Over", int(t * 0.72), cooldown=4,
                                                               school="nature", is_aoe=True),
                               lambda t: heal("Reabsorb", int(t * 1.4), cooldown=5, school="nature"), school="nature")
    k["Archive Wraith"] = trash3(60, "Shard Bolt", lambda t: dmg("Shatter", int(t * 0.72), cooldown=4, school="arcane",
                                                                 is_aoe=True),
                                 lambda t: hit_with("Filed Away", int(t * 0.8), {"haste": -15}, 3, school="arcane"),
                                 school="arcane")
    k["Archive Anomaly"] = trash3(60, "Arcane Bolt", lambda t: hit_with("Unravel", int(t * 0.8), {"spell_power": -50},
                                                                         3, school="arcane"),
                                  lambda t: dot("Mana Leak", int(t * 0.28), 4, 3, school="arcane", dispel_type="magic"),
                                  school="arcane")
    k["Hollow Guardian"] = trash3(60, "Halberd", lambda t: dmg("Sweeping Halberd", int(t * 0.72), cooldown=4,
                                                                is_aoe=True),
                                  lambda t: hit_with("Enchanted Plate", int(t * 0.8), {"armor": 200}, 3, on="buff"))
    k["Swarming Pages"] = trash3(60, "Paper Cut", lambda t: dmg("Whirl of Pages", int(t * 0.72), cooldown=4,
                                                                 school="arcane", is_aoe=True),
                                 lambda t: hit_with("Wrong Chapter", int(t * 0.8), {"intellect": -30}, 3,
                                                    school="arcane"), school="arcane")
    k["Stopped Volunteer"] = trash3(60, "Shovel", lambda t: dmg("Last Swing", int(t * 1.3), cooldown=4),
                                    lambda t: stun_hit("Caught in the Moment", int(t * 0.9), cooldown=6,
                                                       school="arcane"))
    k["Moment Without End"] = trash3(60, "Strike, Strike, Strike",
                                     lambda t: dmg("All at Once", int(t * 0.72), cooldown=4, school="arcane", is_aoe=True),
                                     lambda t: hit_with("Somewhere Else", int(t * 0.8), {"dodge_rating": 30}, 3,
                                                        on="buff"), school="arcane")
    k["Aged Volunteer"] = trash3(60, "Withered Grip", lambda t: dmg("Dust to Dust", int(t * 1.3), cooldown=4,
                                                                     school="shadow"),
                                 lambda t: hit_with("Ninety Years in a Second", int(t * 0.8), {"haste": -15}, 3,
                                                    school="shadow"), school="shadow")
    # ---- the Exclusion Zone's bosses
    k["Gristlemaw"] = boss_kit(                 # a heap of Grosh'gok's ogres moving as one body
        57, "physical", "Heap Fist", "Many Mouths", "Rolling Crush", "Shockwave of Flesh",
        summon("Pulled from the Heap", "Exclusion Ogre", 4, 2, 4), "The Heap Comes Apart",
        signature=[dmg("All of Them at Once", int(B(57) * 1.9), cooldown=5),
                   last_gasp("The Heap Falls on You", 57)])
    k["Broodmother Vexis"] = boss_kit(          # the brood's mother, fused with her clutch
        58, "nature", "Fused Mandibles", "Brood Lash", "Egg-Heavy Slam", "Sac Burst",
        summon("Hatch", "Brood Hatchling Swarm", 4, 3, 6), "The Last Clutch",
        extra=[stun_hit("Webbed to the Wall", int(B(58) * 0.8), cooldown=6, school="nature")],
        signature=[dot("Brood Venom", int(B(58) * 0.5), 5, 4, school="nature", dispel_type="poison"),
                   dmg("Every Egg Opens", int(B(58) * 1.15), cooldown=6, school="nature", is_aoe=True)])
    k["The Glow-Eater"] = boss_kit(             # eats the seep in the Bubbler Pools and grows on it
        58, "nature", "Glowing Maw", "Slag Spit", "Swallow Whole", "Bubbler Surge",
        stun_hit("Swallowed", int(B(58) * 0.9), cooldown=6, school="nature"), "Gorged",
        extra=[heal("Drinks from the Pool", int(B(58) * 1.1), cooldown=6, school="nature"),
               hit_with("Glow", int(B(58) * 0.6), {"attack_power": int(B(58) * 0.15)}, 99, on="buff",
                        school="nature", cooldown=5)],
        signature=[dmg("The Pools Boil", int(B(58) * 1.2), cooldown=6, school="nature", is_aoe=True)])
    k["Archivist Nine"] = boss_kit(             # Karazhan's librarian at nine ages at once
        59, "arcane", "Ink-Black Bolt", "Page Cut", "The Heavy Volume", "Every Page Turns",
        hit_with("Read Aloud", int(B(59) * 0.8), {"spell_power": -60, "attack_power": -60}, 3, school="arcane",
                 cooldown=5), "The Ninth Age",
        extra=[shell("Filed Under Never", 6, 3, int(B(59) * 1.2), school="arcane")],
        signature=[dmg("Your Own Death, Read to You", int(B(59) * 2.0), cooldown=6, school="arcane"),
                   last_gasp("The Library Closes", 59, "arcane")])
    k["The Stopped Man"] = boss_kit(            # Mykola Bondar, frozen mid-scream, ninety seconds too long
        59, "arcane", "Stopped Fist", "Scream Without Sound", "The Moment Breaks", "Time Lets Go",
        stun_hit("Stopped", int(B(59) * 0.9), cooldown=5, school="arcane"), "Ninety Seconds",
        signature=[dmg("Everything He Was Carrying", int(B(59) * 1.9), cooldown=5, school="arcane"),
                   dot("Too Long in the Hall", int(B(59) * 0.5), 5, 4, school="arcane", dispel_type="magic")])
    k[EZ_FINAL] = boss_kit(                     # the knot that keeps every copy; the Elephant's Foot
        60, "nature", "Wound Pulse", "Black Glass Lash", "Melted Weight", "The Wound Breathes",
        summon("Remembered", "Aged Volunteer", 4, 2, 5), "Every Copy Wakes",
        extra=[hit_with("Too Close to the Foot", int(B(60) * 0.7), {"healing_power": -60, "haste": -10}, 3,
                        school="nature", cooldown=5)],
        signature=[dmg("Five Minutes Beside It", int(B(60) * 2.0), cooldown=6, school="nature"),
                   dot("The Fallout", int(B(60) * 0.5), 5, 4, school="nature", dispel_type="disease"),
                   last_gasp("It Remembers Everything", 60, "nature", mult=1.7)])
    return k


#: rare or boss -> four (name, slot, suffix, (a|w, type) or None, stat template), spread over every type
POOLS = {
    # ---- the rares
    "The Wagon Driver": [
        ("Coachman's Greatcoat", "chest", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Reins of the Crash", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Coachwhip", "main_hand", "of the Tiger", ("w", "sword_1h"), "agi_physical"),
        ("Driver's Lantern Hood", "head", "of the Physician", ("a", "cloth"), "spi_healer")],
    "Mog'grak the Twice-Born": [
        ("Twice-Born Maul", "main_hand", "of the Bear", ("w", "mace_2h"), "str_physical"),
        ("Grosh'gok Chieftain's Belt", "waist", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Little One's Charm", "neck", "of the Prophet", None, "spi_healer"),
        ("Swollen Hide Gloves", "hands", "of the Monkey", ("a", "leather"), "agi_physical")],
    "Old Three-Heads": [
        ("Three-Age Pelt", "back", "of the Monkey", None, "agi_physical"),
        ("Pup's Tooth Necklace", "neck", "of the Gorilla", None, "str_int_hybrid"),
        ("Grey Muzzle Helm", "head", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Old Wolf's Leggings", "legs", "of the Sorcerer", ("a", "cloth"), "int_caster")],
    "The Crow King": [
        ("Crown of Many Eyes", "head", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Talon-Stitched Boots", "feet", "of the Tiger", ("a", "leather"), "agi_physical"),
        ("Murder-Feather Mantle", "shoulder", "of the Owl", ("a", "mail"), "spi_healer"),
        ("Crow King's Signet", "ring", "of the Champion", None, "str_physical")],
    # ---- the caves
    "The Silk Mother": [
        ("Silk Mother's Shroud", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Funnel-Weave Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Brood-Chitin Pauldrons", "shoulder", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Cocoon-Bound Tome", "off_hand", "of the Sorcerer", ("w", "tome"), "int_caster")],
    "The Drowned Thing": [
        ("Sump-Root Staff", "main_hand", "of the Owl", ("w", "staff"), "spi_healer"),
        ("Drowned Hauberk", "chest", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Mud-Caked Greaves", "feet", "of the Bear", ("a", "plate"), "str_physical"),
        ("Seep-Soaked Sash", "waist", "of the Invoker", ("a", "cloth"), "int_caster")],
    # ---- the Exclusion Zone: three each, like every token dungeon's bosses (no bracers: that's the token)
    "Gristlemaw": [
        ("Heap-Hide Breastplate", "chest", "of the Bear", ("a", "plate"), "str_physical"),
        ("Ogre-Bone Cudgel", "main_hand", "of the Gorilla", ("w", "mace_1h"), "str_int_hybrid"),
        ("Gristle-Stitched Cowl", "head", "of the Prophet", ("a", "cloth"), "spi_healer")],
    "Broodmother Vexis": [
        ("Vexis's Fang", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical"),
        ("Clutch-Silk Robe", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Broodguard Spaulders", "shoulder", "of the Champion", ("a", "plate"), "str_physical")],
    "The Glow-Eater": [
        ("Bubbler Diver's Hood", "head", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Glow-Eater's Gullet Shield", "off_hand", "of the Bear", ("w", "shield"), "str_physical"),
        ("Slag-Plated Leggings", "legs", "of the Hunt", ("a", "mail"), "agi_physical")],
    "Archivist Nine": [
        ("Ninth Age Spellblade", "main_hand", "of the Sorcerer", ("w", "sword_1h"), "int_caster"),
        ("Archivist's Ink-Stained Gloves", "hands", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Page-Leather Jerkin", "chest", "of the Monkey", ("a", "leather"), "agi_physical")],
    "The Stopped Man": [
        ("Liquidator's Shovel", "main_hand", "of the Champion", ("w", "polearm"), "str_physical"),
        ("Stopped Watch Pendant", "neck", "of the Owl", None, "spi_healer"),
        ("Mykola's Scarf", "back", "of the Sorcerer", None, "int_caster")],
    EZ_FINAL: [
        ("Heart of the Wound", "off_hand", "of the Prophet", ("w", "idol"), "spi_healer"),
        ("Black Glass Greatsword", "main_hand", "of the Bear", ("w", "sword_2h"), "str_physical"),
        ("Foot-Fused Leggings", "legs", "of the Sorcerer", ("a", "cloth"), "int_caster")],
}

SAFE = None
TABLES = {
    WEST: {
        "open_zone": {"Tumour Wolf": 4, "Pustule Boar": 4, "Many-Eyed Crow": 3, "Dissolving Stag": 2},
        "subzones": {
            "The Dead Forest": {"Tumour Wolf": 4, "Pustule Boar": 4, "Many-Eyed Crow": 3, "Dissolving Stag": 2},
            "The Sickwater": {"Sickwater Leech": 5, "Pustule Boar": 3, "Fused Bat": 3},
            "The Widows' Wood": {"Deadwind Widow": 5, "Widow Hatchlings": 4, "Glowsac Broodmother": 3},
            "Deadwind Ravine": {"Grosh'gok Brute": 4, "Grosh'gok Two-Face": 4, "Chained Mauler": 3},
            "Grosh'gok Compound": {"Grosh'gok Brute": 4, "Grosh'gok Two-Face": 4, "Grosh'gok Sore-Shaman": 4,
                                   "Chained Mauler": 2, "Mog'grak the Twice-Born": 0},
            "Deadman's Crossing": SAFE,
            "Coachman's Bend": {"Plot Risen": 4, "Many-Eyed Crow": 3, "Tumour Wolf": 2, "The Wagon Driver": 0},
            "Morgan's Plot": {"Plot Risen": 5, "Grave Ooze": 4, "Many-Eyed Crow": 2},
            "The Black Tarn": {"Tarn Horror": 4, "Sickwater Leech": 4, "Dissolving Stag": 3, "Fused Bat": 2},
            "The Cracked Tunnel": {"Tunnel Slagcrawler": 5, "Fused Bat": 3},
            "Delgado's Fence": SAFE,
        },
    },
    EAST: {
        "open_zone": {"Three-Age Wolf": 4, "Flicker Hound": 4, "Many-Eyed Crow": 2},
        "subzones": {
            "The Ashen Rise": {"Three-Age Wolf": 4, "Flicker Hound": 4, "Many-Eyed Crow": 2},
            "The Sleeping Gorge": {"Gorge Slagcrawler": 4, "Seep Wyrm": 4, "Flicker Hound": 2},
            "The Broken Bridge": {"Bridge Onlooker": 6, "Many-Eyed Crow": 2},
            "Ariden's Camp": SAFE,
            "The Drowned Hollow": {"Hollow Mudhorror": 5, "Many-Eyed Crow": 3, "Seep Wyrm": 2, "The Crow King": 0},
            "The Vice": {"Shard Wraith": 4, "Many Moments": 4, "Three-Age Wolf": 2},
            "Karazhan": {"Spectral Servant": 4, "Spectral Stablehand": 3, "Ballroom Phantom": 4, "Violet Sentinel": 3,
                         "Book Flock": 3},
            "The Stopped Places": {"Many Moments": 4, "Shard Wraith": 4, "Arcane Anomaly": 3, "Book Flock": 2,
                                   "Old Three-Heads": 0},
            "The Hanging Slide": {"Three-Age Wolf": 4, "Shard Wraith": 3, "Flicker Hound": 3},
            "The Rupture": {"Bloated Walker": 4, "Fused Mass": 4, "Many-Armed Thing": 3, "Gorge Slagcrawler": 2},
        },
    },
}
CAVE_TABLES = {
    NEST: (WEST, {"Funnel Widow": 5, "Nest Hatchlings": 4, "Cocoon Burrower": 3, "The Silk Mother": 0}),
    SEEP: (EAST, {"Seep Leech": 5, "Drain Horror": 4, "Bloated Drowner": 4, "The Drowned Thing": 0}),
}

#: gathering: the 50s tier, darker herbs in the dead forest, ore in the gorge and the tunnel's rock
NODES = {
    "deadwind_west": {"slots": 22, "active_percent": 0.42, "table": {
        "herb_blindweed": 3, "herb_dreamfoil": 3, "herb_purple_lotus": 2, "herb_golden_sansam": 2,
        "ore_thorium": 4, "ore_truesilver": 2, "ore_dark_iron": 2,
        "wood_starleaf_tree": 2}},
    "deadwind_east": {"slots": 22, "active_percent": 0.42, "table": {
        "herb_blindweed": 3, "herb_dreamfoil": 3, "herb_icecap": 2,
        "ore_thorium": 3, "ore_ashen_steel": 3, "ore_elementium": 2, "ore_dark_iron": 2}},
}


def _ilvl(name):
    r = ROSTER[name]
    if name in RARES:
        return r[2] + 3
    if name in CAVE_BOSSES:
        return r[2] + 2
    return r[2] + 3


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows, moved = {}, [], 0
    for b, items in POOLS.items():
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, _ilvl(b), "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = "dw_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
                moved += 1
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[b] = built
    return out, rows, moved


def tokens():
    """The Exclusion Zone carries the T0 bracers: 20% a boss on three armour types (the one it lacks rotates), all
    four and always from the Wound's Heart."""
    out = {}
    for i, name in enumerate(EZ_BOSSES):
        fin = name == EZ_FINAL
        out[name] = {"slot": "wrist", "guaranteed": fin,
                     "types": list(ARMOUR) if fin else [t for k, t in enumerate(ARMOUR) if k != i % 4]}
    return out


def check(k, loot):
    bad = []
    if set(k) != set(ROSTER):
        bad.append(f"kits and roster differ: {sorted(set(k) ^ set(ROSTER))}")
    bosses = RARES | CAVE_BOSSES | set(EZ_BOSSES)
    if set(POOLS) != bosses:
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ bosses)}")
    for zone, mod in ((WEST, DWW), (EAST, DWE)):
        declared = {s[0] for s in mod.SUBZONES}
        if set(TABLES[zone]["subzones"]) != declared:
            bad.append(f"{zone} subzones disagree with the map: {sorted(set(TABLES[zone]['subzones']) ^ declared)}")
    named = set()
    for t in TABLES.values():
        named |= set(t["open_zone"])
        if RARES & set(t["open_zone"]):
            bad.append("a rare is in an open-zone table")
        for s in t["subzones"].values():
            named |= set(s or {})
    for _p, c in CAVE_TABLES.values():
        named |= set(c)
    named |= set(EZ_BOSSES) | set(EZ_TRASH)
    if named != set(ROSTER):
        bad.append(f"tables and roster differ: {sorted(named ^ set(ROSTER))}")
    for cave in (NEST, SEEP):
        if set(DWC.BOSSES[cave]) != {n for n in CAVE_BOSSES if ROSTER[n][5] == cave}:
            bad.append(f"{cave}'s map places {sorted(DWC.BOSSES[cave])}")
    placed = {n for f in EZ.FLOORS for n in EZ.BOSSES.get(f, {})}
    if placed != set(EZ_BOSSES):
        bad.append(f"the Exclusion Zone's maps place {sorted(placed)}")
    for f in EZ.FLOORS:
        lo, hi = EZ.LEVELS[f]
        for n in ez_floor_creatures(f):
            r = ROSTER[n]
            if not (lo <= r[1] and r[2] <= hi):
                bad.append(f"{n} ({r[1]}-{r[2]}) is on {f}, which is {lo}-{hi}")
        for p in EZ._trash(f):
            for (_x, _y, m, lvl) in p:
                if not (ROSTER[m][1] <= lvl <= ROSTER[m][2]) or not (lo <= lvl <= hi):
                    bad.append(f"a pack on {f} puts {m} at {lvl}")
    on_map = {m for (_x, _y, m, _l) in [s for p in EZ._trash() for s in p]}
    if on_map != set(EZ_TRASH):
        bad.append(f"the Exclusion Zone's trash and the roster differ: {sorted(on_map ^ set(EZ_TRASH))}")
    for b in EZ_BOSSES:
        if any(i["slot"] == "wrist" for i in loot[b]):
            bad.append(f"{b} carries bracers in the dungeon whose token they are")
    for zone, (lo, hi) in list(ZONE_LEVELS.items()) + [(EXZ, EXZ_BAND)]:
        if zone in EZ.FLOORS:
            continue                    # the floors are checked above, each against its own band
        for n, r in ROSTER.items():
            if r[5] == zone and not (lo <= r[1] and r[2] <= hi):
                bad.append(f"{n} ({r[1]}-{r[2]}) sits outside {zone} {lo}-{hi}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ROSTER.items():
        if r[4] in NOT_HOSTILE:
            bad.append(f"{name} wears {r[4]}, which is a person in the pass")
        if not ((ROOT / "assets/creatures" / f"{r[4]}.png").exists() or (SRC / f"{r[4]}.png").exists()):
            bad.append(f"{name}'s sprite {r[4]} is not on disk")
        prev = existing.get(name)
        if prev and prev.get("ability_kit") != kit_slug(name):
            bad.append(f"{name} is already a different creature in creatures.json")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ROSTER.items():
        if CS.sprite_for(name, r[0]) != r[4]:
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {r[4]}")
    return bad


def install_sprites():
    n = 0
    for r in ROSTER.values():
        src, dst = SRC / f"{r[4]}.png", ROOT / "assets/creatures" / f"{r[4]}.png"
        if src.exists() and not dst.exists():
            shutil.copyfile(src, dst)
            n += 1
    return n


def _write(path, data, raw):
    indent, newline = _detect_format(json.loads(raw), raw)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")


def main():
    for cave in (NEST, SEEP):
        DWC.build(cave)                 # the maps place the bosses; build them so the check can read them
    for f in EZ.FLOORS:
        EZ.build_floor(f)               # the maps place the bosses; build them so the check can read them
    copied = install_sprites()
    k = kits()
    loot, rows, moved = build_loot()
    bad = check(k, loot) + loot_audit(rows)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    for zone, table in TABLES.items():
        entry = enc["zones"].setdefault(zone, {})
        entry["name"] = zone
        entry["open_zone"] = {"name": zone, "creatures": dict(table["open_zone"])}
        entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                                 {"name": s, "creatures": dict(c)}) for s, c in table["subzones"].items()}
    for cave, (parent, table) in CAVE_TABLES.items():
        enc["zones"][parent].setdefault("caves", {})[cave] = {"name": cave, "creatures": dict(table)}
    for f in EZ.FLOORS:
        enc["zones"][EAST].setdefault("caves", {})[f] = {
            "name": f, "creatures": {n: (0 if n in EZ_BOSSES else 4) for n in ez_floor_creatures(f)}}
    _write(ENCOUNTERS, enc, raw)

    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    lv["zones"].update(ZONE_LEVELS)
    _write(LEVELS, lv, raw)

    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    fish = (nd["zones"].get("north_felwood") or {}).get("fishing")
    for key, pool in NODES.items():
        nd["zones"][key] = dict(pool, **({"fishing": fish} if fish else {}))
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    t = json.loads(TOKENS.read_text(encoding="utf-8"))
    t["bosses"].update(tokens())
    TOKENS.write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = {"_notes": ("Deadwind Pass (55-60): the open world's four rares (level + 3), the two caves' bosses (+ 2) and "
                      "the Exclusion Zone's six (+ 3, no bracers: the T0 bracers token is theirs). ONE item per kill "
                      "from the four. Hand-authored in tools/build_deadwind_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(RARES)} rares, {len(CAVE_BOSSES)} cave bosses, {len(EZ_BOSSES)} dungeon "
          f"bosses); {copied} sprites installed; {sum(len(v) for v in loot.values())} items ({moved} put on the "
          f"curve); gathering on {', '.join(NODES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
