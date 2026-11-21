#!/usr/bin/env python3
"""The Fading Firmament's creatures, rares, encounter tables, loot, gathering and fishing (57-60), and its three caves'
(the Hearthdeep and the Wellspring under the Threefold Forge, and the Hollow Engine). Idempotent.

    PYTHONPATH=. python3 tools/build_fading_firmament_content.py [--dry]

docs/worldtree_brief.md: "the Ascendancy's last push to seize the tree; the sky itself coming apart". No dungeons (Kyle,
21 Nov 2026: "No Dungeons but some caves are fine").

    open zone               dusk kestrels and fading wisps between the islands
    The Road's End          the Ascendancy's columns coming up the road
    The Emptied Quarter     the quarter's old sentinels, crawlers, scavengers           rare: The Last Watchman
    The Greyfall Gardens    grey moths, ash puffballs, pale stags                           rare: The Grey Hart
    The Last Green          the sprites that keep the last tree
    The Coldforges          salvagers, slag golems, salvage drones                          rare: Foreman Dask Corrow
    The Threefold Forge     the forge's waking guardians, hearth-bound storms, cutters      rare: The Anvil-Thane
    The Dead Engines        dead-crystal golems, void-touched drifters, broken constructs   rare: The Stalled Colossus
    The Siege Line          legionaries, artillerists, lancers, bombardier constructs       rare: Siegemaster Varek Toll
    The Breaking            unmoored stone, hollow storms, drift eels                       rare: Old Driftmother
    The Wound's Edge        wound crawlers, unmade wisps, edge gales                        rare: The Unmade
    The Moorage             the flagship's marines, battlemages, wardens      the general: Ascendant-General Maelis Ardane
    Lastlight, Forgewatch: safe
    The Hearthdeep (cave)   salvage-cutters, cinderlings, flue guardians, wind-spirits
                            bosses: The Bellows-Warden, Salvage-Master Corin Hask
    The Wellspring (cave)   seedbed golems, wellwater, unsung gusts, stonecutters
                            bosses: The Seedbed Warden, The Unsung
    The Hollow Engine (cave) crystallings, gear-tenders, coolant lurkers, void motes
                            bosses: The Last Governor, The Black Lattice

THE PURE 60 RULE (Kyle, 21 Nov 2026: "Keep firm as 57-60 and ensure since it's not pure 60, no frontier nodes in it"):
nothing here grows, drops or fishes up a post-game material; the caves stay under 60.

THE NUMBERS follow the tiers (tools/build_sunward_crown_content.py): trash basic 4L - 10, a rare's 10L - 200 at
multiplier 2.2, item level = the rare's level + 3, a cave boss's + 2. The general is an elite group fight at 60.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402
from tools.build_scarlet_monastery_content import opener, stun_hit, heal  # noqa: E402

RARE_LOOT = ROOT / "data/loot/fading_firmament_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/firmament_caves_boss_loot.json"
ZONE = "The Fading Firmament"
MAP_MODULE = "handbuilt_worldtree_fading_firmament"
#: the caves: name -> its map module
CAVES = {"The Hearthdeep": "handbuilt_hearthdeep", "The Wellspring": "handbuilt_wellspring",
         "The Hollow Engine": "handbuilt_hollow_engine"}


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- between the islands
    "Dusk Kestrel":           ("beast_fast", 57, 59, None, "sk_gale_hawk", "beast", "nature",
                               ["Talons", "Out of the Dusk", "Wind-Torn"]),
    "Fading Wisp":            ("elemental_caster", 57, 59, None, "sk_fading_wisp", "caster", "arcane",
                               ["Flicker", "Last Light", "Guttering"]),
    # ---------------------------------------------------------------- the Road's End
    "Column Legionary":       ("humanoid_warrior", 57, 57, None, "ae_legionary", "warrior", "physical",
                               ["Crystal Blade", "Close the Column", "Braced"]),
    "Column Storm Caller":    ("humanoid_caster", 57, 57, None, "ae_storm_caller", "caster", "nature",
                               ["Call Lightning", "Stormfront", "Static"]),
    # ---------------------------------------------------------------- the Emptied Quarter
    "Quarter Sentinel":       ("elemental_bruiser", 57, 58, None, "ae_sentinel", "bruiser", "physical",
                               ["Patrol Strike", "Clear the Street", "Rattled"]),
    "Quarter Crawler":        ("beast_fast", 57, 58, None, "sk_rift_crawler", "beast", "shadow",
                               ["Rending Claws", "Out of the Crack", "Rift-Sick"]),
    "Ascendancy Scavenger":   ("humanoid_warrior", 57, 58, None, "ae_forge_worker", "warrior", "physical",
                               ["Pry Bar", "Grab and Run", "Braced"]),
    "The Last Watchman":      ("elemental_bruiser", 58, 58, 2.2, "ae_sentinel", "rare", "physical",
                               ["Watchman's Fist", "Curfew", "Locked In", "Nobody Leaves the Quarter"]),
    # ---------------------------------------------------------------- the Greyfall Gardens
    "Greyfall Moth":          ("beast_fast", 57, 58, None, "sk_sky_moth", "beast", "nature",
                               ["Ash Wings", "Grey Dust", "Choking Dust"]),
    "Ash Puffball":           ("elemental_caster", 57, 58, None, "sk_puffball", "caster", "nature",
                               ["Spore Puff", "Burst of Ash", "Spore-Sick"]),
    "Pale Stag":              ("beast_fast", 57, 58, None, "sk_golden_stag", "beast", "physical",
                               ["Antler Strike", "Pale Charge", "Gored"]),
    "The Grey Hart":          ("beast_large", 58, 58, 2.2, "sk_golden_stag", "rare", "nature",
                               ["Grey Antlers", "The Garden Fades", "Trampled", "The Last of the Herd"]),
    # ---------------------------------------------------------------- the Last Green
    "Greenwatch Sprite":      ("elemental_caster", 58, 58, None, "sk_gust_sprite", "caster", "nature",
                               ["Leaf Gust", "Keep Away", "Bramble-Sting"]),
    # ---------------------------------------------------------------- the Coldforges
    "Ascendancy Salvager":    ("humanoid_caster", 58, 58, None, "ae_engineer", "caster", "fire",
                               ["Cutting Torch", "Strip the Forge", "Scorched"]),
    "Cold Slag Golem":        ("elemental_bruiser", 58, 58, None, "kh_mineral_elemental", "bruiser", "physical",
                               ["Slag Fist", "Cold Pour", "Slagged"]),
    "Salvage Drone":          ("elemental_caster", 58, 58, None, "ae_repair_drone", "caster", "arcane",
                               ["Cutting Beam", "Sweep the Ruin", "Weld-Burn"]),
    "Foreman Dask Corrow":    ("humanoid_caster", 59, 59, 2.2, "ae_officer", "rare", "fire",
                               ["Foreman's Torch", "Strip It All", "Knocked Flat", "The Quota Stands"]),
    # ---------------------------------------------------------------- the Threefold Forge
    "Waking Forge-Guardian":  ("elemental_bruiser", 58, 59, None, "kh_waking_guardian", "bruiser", "physical",
                               ["Guardian's Fist", "Wake the Hearth", "Staggered"]),
    "Hearth-Bound Storm":     ("elemental_caster", 58, 59, None, "kh_bound_storm", "caster", "nature",
                               ["Hearth Bolt", "Storm in the Flue", "Static"]),
    "Ascendancy Cutter":      ("humanoid_caster", 58, 59, None, "ae_crystal_weaver", "caster", "arcane",
                               ["Crystal Shard", "Cut It Loose", "Crystal Burn"]),
    "The Anvil-Thane":        ("elemental_bruiser", 59, 59, 2.2, "kh_sentinel_construct", "rare", "physical",
                               ["Anvil Blow", "Ring the Anvil", "Hammered Flat", "The Forge Is Not Yours"]),
    # ---------------------------------------------------------------- the Dead Engines
    "Dead-Crystal Golem":     ("elemental_bruiser", 59, 59, None, "kh_gravity_golem", "bruiser", "arcane",
                               ["Black Crystal Fist", "Dead Weight", "Crystal-Cracked"]),
    "Void-Touched Drifter":   ("elemental_caster", 59, 59, None, "sk_void_touched", "caster", "shadow",
                               ["Void Lash", "Pull of the Drop", "Hollowed"]),
    "Broken Construct":       ("humanoid_warrior", 59, 59, None, "ae_broken_construct", "warrior", "physical",
                               ["Broken Arm", "Lurch", "Braced"]),
    "The Stalled Colossus":   ("elemental_bruiser", 59, 59, 2.2, "ae_siege_walker", "rare", "physical",
                               ["Colossus Stomp", "Grind Forward", "Crushed", "One Last Step"]),
    # ---------------------------------------------------------------- the Siege Line
    "Siege Legionary":        ("humanoid_warrior", 59, 60, None, "ae_legionary", "warrior", "physical",
                               ["Crystal Blade", "Hold the Trench", "Braced"]),
    "Siege Artillerist":      ("humanoid_caster", 59, 60, None, "ae_artillerist", "caster", "nature",
                               ["Crackling Rod", "Ranging Shot", "Static"]),
    "Vanguard Sky Lancer":    ("humanoid_warrior", 59, 60, None, "ae_lancer_mounted", "bruiser", "arcane",
                               ["Mounted Thrust", "Vanguard Charge", "Trampled"]),
    "Bombardier Construct":   ("elemental_caster", 59, 60, None, "ae_bomber_construct", "caster", "fire",
                               ["Bombard", "Carpet of Fire", "Burning"]),
    "Siegemaster Varek Toll": ("humanoid_caster", 60, 60, 2.2, "ae_artillerist", "rare", "nature",
                               ["Siegemaster's Bolt", "Walk the Fire In", "Thrown Down", "Every Gun on the Line"]),
    # ---------------------------------------------------------------- the Breaking
    "Unmoored Stone":         ("elemental_bruiser", 58, 59, None, "kh_gravity_golem", "bruiser", "physical",
                               ["Stone Fist", "The Ground Shifts", "Off Balance"]),
    "Hollow Storm":           ("elemental_caster", 58, 59, None, "sk_hollow_storm", "caster", "nature",
                               ["Hollow Bolt", "Empty Gale", "Static"]),
    "Drift Eel":              ("beast_fast", 58, 59, None, "sk_sky_eel", "beast", "shadow",
                               ["Eel Bite", "Coil and Strike", "Drift-Sick"]),
    "Old Driftmother":        ("beast_large", 59, 59, 2.2, "sk_cloud_serpent", "rare", "nature",
                               ["Driftmother's Coil", "Down With the Island", "Swallowed Whole", "The Drop Takes All"]),
    # ---------------------------------------------------------------- the Wound's Edge
    "Wound Crawler":          ("beast_fast", 59, 60, None, "sk_rift_crawler", "beast", "shadow",
                               ["Rending Claws", "Up Over the Edge", "Rift-Sick"]),
    "Unmade Wisp":            ("elemental_caster", 59, 60, None, "sk_fading_wisp", "caster", "shadow",
                               ["Unmaking", "Nothing Where You Stood", "Unravelling"]),
    "Edge Gale":              ("elemental_caster", 59, 60, None, "sk_gale_elemental", "caster", "nature",
                               ["Gale Strike", "Over the Edge", "Wind-Torn"]),
    "The Unmade":             ("elemental_caster", 60, 60, 2.2, "sk_hollow_storm", "rare", "shadow",
                               ["Unmake", "The Hole Widens", "Taken Apart", "Nothing Left to Hold"]),
    # ---------------------------------------------------------------- the Moorage
    "Moorage Marine":         ("humanoid_warrior", 60, 60, None, "ae_legionary", "warrior", "physical",
                               ["Boarding Blade", "Repel Boarders", "Braced"]),
    "Ascendant Battlemage":   ("humanoid_caster", 60, 60, None, "ae_magister", "caster", "arcane",
                               ["Arcane Lance", "Lens of War", "Arcane Burn"]),
    "Flagship Warden":        ("humanoid_warrior", 60, 60, None, "ae_warden", "warrior", "arcane",
                               ["Warden's Blade", "Guard the Gangway", "Warded"]),
    "Ascendant-General Maelis Ardane": ("humanoid_caster", 60, 60, 3.0, "ae_high_commander", "general", "arcane",
                                        ["Lens-Blade", "The Sky Is Mine", "Pinned by the Lens", "Every Ship at Once"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: the caves' trash and bosses: trash rolled from each cave's own table, the bosses pinned by the map
CAVE_ROSTERS = {
    "The Hearthdeep": {
        "Ascendancy Salvage-Cutter": ("humanoid_warrior", 58, 59, None, "ae_forge_worker", "warrior", "fire",
                                      ["Cutting Saw", "Cut the Flue", "Braced"]),
        "Ash-Hall Cinderling":   ("elemental_caster", 58, 59, None, "sk_fading_wisp", "caster", "fire",
                                  ["Cinder", "Ash Cloud", "Smouldering"]),
        "Flue Guardian":         ("elemental_bruiser", 58, 59, None, "kh_stonewarden", "bruiser", "physical",
                                  ["Flue Fist", "Close the Flue", "Staggered"]),
        "Gallery Wind-Spirit":   ("elemental_caster", 58, 59, None, "sk_gust_sprite", "caster", "nature",
                                  ["Wind-Way Gust", "Song Through Stone", "Wind-Torn"]),
        "The Bellows-Warden":    ("elemental_bruiser", 59, 59, 2.5, "kh_temple_guardian", "boss", "physical",
                                  ["Bellows Blow", "Draw the Draught", "Pinned to the Anvil", "The Forge Breathes"]),
        "Salvage-Master Corin Hask": ("humanoid_caster", 59, 59, 2.3, "ae_officer", "boss", "fire",
                                      ["Salvage Torch", "Cut It All Out", "Knocked Flat", "Every Crew to Me"]),
    },
    "The Wellspring": {
        "Seedbed Golem":         ("elemental_bruiser", 59, 59, None, "kh_gravity_golem", "bruiser", "physical",
                                  ["Trough Fist", "Turn the Bed", "Staggered"]),
        "Wellwater Elemental":   ("elemental_caster", 59, 59, None, "sk_cloud_elemental", "caster", "frost",
                                  ["Cold Spring", "Well Over", "Chilled"]),
        "Unsung Gust":           ("elemental_caster", 59, 59, None, "sk_gale_elemental", "caster", "nature",
                                  ["Wild Gust", "No Song to Hold It", "Wind-Torn"]),
        "Ascendancy Stonecutter": ("humanoid_caster", 59, 59, None, "ae_engineer", "caster", "arcane",
                                   ["Stonecutter's Beam", "Cut the Seed", "Crystal Burn"]),
        "The Seedbed Warden":    ("humanoid_caster", 59, 59, 2.3, "kh_ancestral_spirit", "boss", "arcane",
                                  ["Warden's Rune", "Tend the Beds", "Held in Stone", "The Beds Are Mine to Keep"]),
        "The Unsung":            ("elemental_caster", 59, 59, 2.5, "vy_bound_elemental", "boss", "nature",
                                  ["Unsung Gale", "The Song That Isn't", "Torn Off Your Feet", "The Wellspring Howls"]),
    },
    "The Hollow Engine": {
        "Dead-Core Crystalling": ("elemental_caster", 58, 59, None, "sk_crystal_elemental", "caster", "arcane",
                                  ["Black Shard", "Dead Light", "Crystal Burn"]),
        "Gear-Tender Construct": ("humanoid_warrior", 58, 59, None, "ae_scout_construct", "warrior", "physical",
                                  ["Gear Arm", "Wind the Gears", "Braced"]),
        "Coolant Lurker":        ("beast_fast", 58, 59, None, "sk_sky_eel", "beast", "frost",
                                  ["Cold Bite", "Out of the Coolant", "Frostbitten"]),
        "Void Mote":             ("elemental_caster", 58, 59, None, "sk_void_touched", "caster", "shadow",
                                  ["Void Spark", "Hollow Pulse", "Hollowed"]),
        "The Last Governor":     ("elemental_bruiser", 59, 59, 2.3, "ae_storm_construct", "boss", "nature",
                                  ["Governor's Arc", "Restart the Engine", "Locked in the Circuit", "Full Power"]),
        "The Black Lattice":     ("elemental_caster", 59, 59, 2.5, "ae_crystal_golem", "boss", "shadow",
                                  ["Black Lattice", "It Grows", "Caught in the Lattice", "The Core Goes Dark"]),
    },
}
CAVE_ALL = {n: r for c in CAVE_ROSTERS.values() for n, r in c.items()}
CAVE_BOSSES = {n for n, r in CAVE_ALL.items() if r[3]}
#: the bosses whose kit gets a heal instead of a big blast
HEALER_BOSSES = {"The Last Governor", "The Seedbed Warden"}
ALL = {**ROSTER, **CAVE_ALL}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE FADING FIRMAMENT (generated by tools/build_fading_firmament_content.py; do not edit by hand)\n"
RULES_END = "    # END THE FADING FIRMAMENT\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE ASCENDANT BASTIONS (generated by tools/build_ascendant_bastions_content.py; do not edit by hand)\n"
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def kit(name):
    template, lo, hi, mult, _s, shape, school, names = ALL[name]
    t = T(hi)
    s = school
    dispel = {"nature": "poison", "shadow": "curse"}.get(s, "magic")
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                dot(names[2], int(t * 0.27), 3, 3, school=s, **({"dispel_type": dispel} if s != "physical" else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 190})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 8, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -20}, school=s)]
    b = B(hi)
    stun_ = stun_hit(names[2], int(b * 1.1), 6, school=s) if s != "physical" else stun_hit(names[2], int(b * 1.1), 6)
    deep = dot(f"{names[1]}, Deep", int(b * 0.45), 5, 4, school=s,
               **({"dispel_type": dispel} if s != "physical" else {}))
    if shape == "boss":
        # a cave boss: an opener, a hard hit, a party hit, a stun, something dangerous, a heal or a flood, last stand
        kit_ = [opener(names[0], b, s), dmg(names[1], int(b * 0.88), cooldown=4, school=s),
                dmg(f"{names[0]}, Twice", int(b * 1.3), cooldown=4, school=s),
                dmg(names[3], int(b * 0.7), cooldown=5, school=s, is_aoe=True), stun_, deep]
        if name in HEALER_BOSSES:
            kit_.append(heal("Mend and Carry On", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("Everything at Once", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    if shape == "general":
        # the general: the elite end of the chain. Her lens-blade, the decree that hits the whole party, the pin, a
        # magic burn the healers dispel, her fleet's broadside on a long cooldown, and the shield she raises at the end
        # (a burn check every school can break)
        return [opener(names[0], b, s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True), stun_, deep,
                dmg(f"{names[0]}, Twice", int(b * 1.3), cooldown=4, school=s),
                dmg(names[3], int(b * 1.1), cooldown=6, school="fire", is_aoe=True),
                shield("Ascendant's Ward", int(b * 1.6), school=s),
                dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s, duration=30,
                     self_only=True, hp_below=0.25, stat_mods={"attack_power": int(b * 0.35)})]
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Dusk Kestrel": 5, "Fading Wisp": 4},
    "subzones": {
        "The Road's End": {"Column Legionary": 5, "Column Storm Caller": 4},
        "Lastlight": None,
        "The Emptied Quarter": {"Quarter Sentinel": 4, "Quarter Crawler": 4, "Ascendancy Scavenger": 5,
                                "The Last Watchman": 0},
        "The Greyfall Gardens": {"Greyfall Moth": 5, "Ash Puffball": 4, "Pale Stag": 4, "The Grey Hart": 0},
        "The Last Green": {"Greenwatch Sprite": 4},
        "The Coldforges": {"Ascendancy Salvager": 5, "Cold Slag Golem": 4, "Salvage Drone": 4,
                           "Foreman Dask Corrow": 0},
        "The Threefold Forge": {"Waking Forge-Guardian": 4, "Hearth-Bound Storm": 4, "Ascendancy Cutter": 5,
                                "The Anvil-Thane": 0},
        "Forgewatch": None,
        "The Dead Engines": {"Dead-Crystal Golem": 4, "Void-Touched Drifter": 4, "Broken Construct": 5,
                             "The Stalled Colossus": 0},
        "The Siege Line": {"Siege Legionary": 5, "Siege Artillerist": 4, "Vanguard Sky Lancer": 3,
                           "Bombardier Construct": 3, "Siegemaster Varek Toll": 0},
        "The Breaking": {"Unmoored Stone": 4, "Hollow Storm": 4, "Drift Eel": 5, "Old Driftmother": 0},
        "The Wound's Edge": {"Wound Crawler": 5, "Unmade Wisp": 4, "Edge Gale": 4, "The Unmade": 0},
        "The Moorage": {"Moorage Marine": 5, "Ascendant Battlemage": 4, "Flagship Warden": 4,
                        "Ascendant-General Maelis Ardane": 0},
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template); the general's are at her level + 4
POOLS = {
    "The Last Watchman": [
        ("Watchman's Curfew Mace", "main_hand", "of the Champion", ("w", "mace_1h"), "str_physical"),
        ("Empty-Street Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Quarter Lamplight Cowl", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Locked Door Band", "ring", "of the Monkey", None, "agi_physical")],
    "The Grey Hart": [
        ("Grey Hart Antler Bow", "ranged", "of the Monkey", ("w", "bow"), "agi_physical"),
        ("Greyfall Hide Jerkin", "chest", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Last-of-the-Herd Mantle", "shoulder", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Pale Velvet Cloak", "back", "of the Prophet", None, "spi_healer")],
    "Foreman Dask Corrow": [
        ("Foreman's Cutting Torch", "off_hand", "of the Invoker", ("w", "tome"), "int_caster"),
        ("Quota-Keeper's Gauntlets", "hands", "of the Bear", ("a", "plate"), "str_physical"),
        ("Coldforge Salvage Belt", "waist", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Strip-It-All Signet", "ring", "of the Sorcerer", None, "int_caster")],
    "The Anvil-Thane": [
        ("Anvil-Thane's Hammer", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical"),
        ("Giant's Hearth Bracers", "wrist", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Threefold Ember Pendant", "neck", "of the Prophet", None, "spi_healer"),
        ("Ringing Anvil Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid")],
    "The Stalled Colossus": [
        ("Colossus Plate Girdle", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Stalled Gear Treads", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Dead Engine Bulwark", "off_hand", "of the Gorilla", ("w", "shield"), "str_int_hybrid"),
        ("One Last Step Charm", "trinket", "of the Sorcerer", None, "int_caster")],
    "Siegemaster Varek Toll": [
        ("Toll's Siege Rifle", "ranged", "of the Monkey", ("w", "gun"), "agi_physical"),
        ("Siegemaster's Mantle", "shoulder", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Trench-Line Spaulders", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Walked-In Fire Band", "ring", "of the Prophet", None, "spi_healer")],
    "Old Driftmother": [
        ("Driftmother Coil Whip", "main_hand", "of the Tiger", ("w", "fist_weapon"), "agi_physical"),
        ("Swallowed Whole Leggings", "legs", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Breaking-Ground Sabatons", "feet", "of the Bear", ("a", "plate"), "str_physical"),
        ("Drift-Scale Vest", "chest", "of the Prophet", ("a", "leather"), "spi_healer")],
    "The Unmade": [
        ("Unmade Rod", "ranged", "of the Invoker", ("w", "wand"), "int_caster"),
        ("Nothing-Left Cord", "waist", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Wound's Edge Helm", "head", "of the Bear", ("a", "plate"), "str_physical"),
        ("Hole-in-the-Sky Grips", "hands", "of the Monkey", ("a", "leather"), "agi_physical")],
    "Ascendant-General Maelis Ardane": [
        ("Maelis's Lens-Blade", "main_hand", "of the Sorcerer", ("w", "sword_1h"), "int_caster"),
        ("Ascendant-General's Warplate", "chest", "of the Champion", ("a", "plate"), "str_physical"),
        ("The Patient Lens, Unlearned", "off_hand", "of the Prophet", ("w", "tome"), "spi_healer"),
        ("Every Ship at Once", "trinket", "of the Monkey", None, "agi_physical")],
}

#: the caves' bosses: item level = boss level + 2
CAVE_POOLS = {
    "The Bellows-Warden": [
        ("Bellows-Warden's Maul", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical"),
        ("Draught-Keeper's Spaulders", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Deep Anvil Signet", "ring", "of the Gorilla", None, "str_int_hybrid"),
        ("Ash Hall Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer")],
    "Salvage-Master Corin Hask": [
        ("Hask's Cutting Blade", "main_hand", "of the Monkey", ("w", "sword_1h"), "agi_physical"),
        ("Salvage-Master's Gloves", "hands", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Crew Boss Girdle", "waist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Cut-It-All-Out Cloak", "back", "of the Wolf", None, "agi_int_hybrid")],
    "The Seedbed Warden": [
        ("Seedbed Warden's Staff", "two_hand", "of the Prophet", ("w", "staff"), "spi_healer"),
        ("Giant's Trough Greaves", "legs", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Cut Seed Pendant", "neck", "of the Sorcerer", None, "int_caster"),
        ("Bedkeeper's Leather Cap", "head", "of the Monkey", ("a", "leather"), "agi_physical")],
    "The Unsung": [
        ("The Unsung's Song", "trinket", "of the Prophet", None, "spi_healer"),
        ("Wind-Way Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Motherstone Shard Wand", "ranged", "of the Sorcerer", ("w", "wand"), "int_caster"),
        ("Howling Wellspring Boots", "feet", "of the Bear", ("a", "plate"), "str_physical")],
    "The Last Governor": [
        ("Governor's Circuit Shield", "off_hand", "of the Bear", ("w", "shield"), "str_physical"),
        ("Restarted Engine Bracers", "wrist", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Full Power Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Last Governor's Band", "ring", "of the Prophet", None, "spi_healer")],
    "The Black Lattice": [
        ("Black Lattice Shard", "trinket", "of the Sorcerer", None, "int_caster"),
        ("Dead Core Chestguard", "chest", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Lattice-Grown Spear", "two_hand", "of the Monkey", ("w", "polearm"), "agi_physical"),
        ("Dark Crystal Coif", "head", "of the Wolf", ("a", "mail"), "agi_int_hybrid")],
}

#: gathering at 57-60, never past the pure-60 line: the high herbs (black lotus rarely) on the natural ground, thorium,
#: truesilver and dark iron in the old plate's stone, and wood off the last dead stands. Fishing: the four wellstone pools.
NODES = {"fading_firmament": {"slots": 38, "active_percent": 0.42, "table": {
    "herb_dreamfoil": 3, "herb_golden_sansam": 2, "herb_icecap": 2, "herb_purple_lotus": 1, "herb_black_lotus": 1,
    "ore_thorium": 4, "ore_truesilver": 2, "ore_dark_iron": 1, "wood_thornveil_stump": 3}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(57, 59)
    fits = sorted([(fid, sk) for fid, _n, sk, _i, _d in FISH if s_lo <= sk <= s_hi], key=lambda f: -f[1])[:4]
    return {"slots": 8, "active_percent": 0.6, "table": {fid: 3 if n else 2 for n, (fid, _s) in enumerate(fits)}}


def build_loot(pools, roster, lift, prefix, extra_lift=None):
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for who, items in pools.items():
        ilvl = roster[who][2] + lift + (extra_lift or {}).get(who, 0)
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = prefix + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[who] = built
    return out, rows


def check(loot):
    import importlib
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    bad = []
    mod = importlib.import_module(f"tools.{MAP_MODULE}")
    declared = {s[0] for s in mod.SUBZONES}
    if set(TABLE["subzones"]) != declared:
        bad.append(f"subzones disagree with the map: {sorted(set(TABLE['subzones']) ^ declared)}")
    named = set(TABLE["open_zone"])
    if RARES & named:
        bad.append("a rare is in the open-zone table")
    for s in TABLE["subzones"].values():
        named |= set(s or {})
    if named != set(ROSTER) or set(POOLS) != RARES:
        bad.append(f"tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
    for cave, modname in CAVES.items():
        m = importlib.import_module(f"tools.{modname}")
        getattr(m, [f for f in dir(m) if f.startswith("build_") and f.endswith("_baked")][0])()
        mine = {n for n, r in CAVE_ROSTERS[cave].items() if r[3]}
        if set(m.BOSSES) != mine:
            bad.append(f"{cave}'s bosses differ: map {sorted(m.BOSSES)}, roster {sorted(mine)}")
    if set(CAVE_POOLS) != CAVE_BOSSES:
        bad.append(f"cave pools and bosses differ: {sorted(set(CAVE_POOLS) ^ CAVE_BOSSES)}")
    if any(r[2] >= 60 and r[1] >= 60 for r in CAVE_ALL.values()):
        bad.append("a cave creature is pure 60 (Kyle: the Firmament isn't pure 60)")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ALL.items():
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
        if prev and (prev.get("ability_kit") != kit_slug(name) or list(prev.get("level_range") or [])[:2] != list(r[1:3])):
            bad.append(f"{name} is already a different creature in creatures.json")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ALL.items():
        if CS.sprite_for(name, r[0]) != sprite(name):
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {sprite(name)}")
    return bad


def main():
    write_sprite_rules()
    import importlib
    import creature_sprites
    importlib.reload(creature_sprites)
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "ffi_", {"Ascendant-General Maelis Ardane": 1})
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ALL, 2, "fci_")
    bad = check({**rare_loot, **cave_loot}) + loot_audit(rows + crows)
    if "--dry" in sys.argv or bad:
        print("\n".join(bad) if bad else f"dry run clean: {len(ALL)} creatures, {len(RARES)} rares, "
                                         f"{len(CAVE_BOSSES)} cave bosses")
        return 1 if bad else 0
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ALL.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): kit(n) for n in ALL}, "ability_kits.json")
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(json.loads(raw), raw)
    entry = enc["zones"].setdefault(ZONE, {})
    entry["name"] = ZONE
    entry["open_zone"] = {"name": ZONE, "creatures": dict(TABLE["open_zone"])}
    entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                             {"name": s, "creatures": dict(c)}) for s, c in TABLE["subzones"].items()}
    caves = entry.setdefault("caves", {})
    for cave, roster in CAVE_ROSTERS.items():
        caves[cave] = {"name": cave, "creatures": {n: (0 if r[3] else 4) for n, r in roster.items()}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["fading_firmament"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Fading Firmament's open-world rares (58-60) and Ascendant-General Maelis Ardane. ONE item per "
                      "kill from the rare's four; item_level = the rare's level + 3, the general's + 4. Hand-authored "
                      "in tools/build_fading_firmament_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for the Firmament's caves (the Hearthdeep, the Wellspring and the Hollow Engine, 58-59). "
                      "ONE item per kill from the boss's four; item_level = boss level + 2. Hand-authored in "
                      "tools/build_fading_firmament_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares and the general), {len(CAVE_ALL)} in the caves "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
