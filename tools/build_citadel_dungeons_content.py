#!/usr/bin/env python3
"""The Citadel of Ascent's two dungeons: creatures, fighting kits, encounter tables, zone levels, boss loot and the
Aetherians' pay for boss kills. Idempotent.

    PYTHONPATH=. python3 tools/build_citadel_dungeons_content.py

The maps are tools/handbuilt_gravity_foundry.py (56-58) and tools/handbuilt_ascendant_spire.py (60); their docstrings
have the rooms and what each boss asks of a party. Kyle, 21 Nov 2026: "a 'Hellfire Citadel' like style", "a lvl 56-58
and a lvl 60 dungeon. Both into one mega structure but different entrances", "around 8-9 bosss over two floors".
Nine fights each, two of them a pair (two bosses, one fight, one loot roll from both their pools).

    THE GRAVITY FOUNDRY
      the Foundry Halls  Brannoc Teal 56 | the Slag Colossus 56 | Pourmasters Ilka and Dov 57 | Prototype Nine 57
                         (optional) | Foundry-Master Cassor Vane 57 (the floor's last)
      the Keelworks      Dessa Marn 58 | Iselle Varr 58 | the Coreless 58 | the Warheart 58 (the last)
    THE ASCENDANT SPIRE
      the Halls of Ascent  Kaine Vorr | Aris Thane | the Storm Choir | Mallen Roe (optional) | Seren Vash, all 60
      the Command Spire    the Aegis Engine | Dravin Kell | the Ascendant Guard Corvo and Lysse | Exarch Lucan Thessaly

THE NUMBERS are the 54-60 band's (tools/build_plaguelands_dungeons_content.py): boss basic 10L - 200, trash basic
4L - 10, boss health 2.5, 2.8 the last of a floor and 1.6 each for a pair. Every boss carries something dangerous
(tools/qa_dungeon_boss_turns.py), and no fight shuts out a damage school.

ART is Kyle's sheet AB2 (docs/bastions_art_prompts.md): eighteen bosses. The two guards of the Exarch weren't on it,
so Corvo and Lysse wear the Ascendancy's stock commander and warden art for now.

LOOT. Four items a boss, a pair's eight; item level = boss level + 3. The Warheart and the Exarch each roll two named
epics at 5% (tools/epic_table.py). A boss kill pays the Aetherians 75 (data/factions/factions.json, dungeon_rep).
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
from tools.build_plaguelands_dungeons_content import (  # noqa: E402
    opener, phase, stun_hit, shell, heal, last_gasp, hit_with)
from tools import handbuilt_gravity_foundry as GF  # noqa: E402
from tools import handbuilt_ascendant_spire as AS  # noqa: E402

LOOT = ROOT / "data/loot/citadel_dungeons_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
FACTIONS = ROOT / "data/factions/factions.json"
SRC = ROOT / "assets/creatures/_src/bastions"
PARENT = GF.REGION
F1, F2, S1, S2 = GF.HALLS, GF.KEEL, AS.HALLS, AS.COMMAND
MAPS = {F1: GF, F2: GF, S1: AS, S2: AS}
ZONE_LEVELS = {F1: [56, 57], F2: [57, 58], S1: [60, 60], S2: [60, 60]}


def B(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


#: name -> (template, lo, hi, boss multiplier or None, sprite, floor)
ROSTER = {
    # ---- the Foundry Halls: the smiths, the guard, and what they pour
    "Foundry Guard":         ("humanoid_warrior", 56, 57, None, "ae_legionary", F1),
    "Foundry Smith":         ("humanoid_warrior", 56, 57, None, "ae_forge_worker", F1),
    "Crucible Tender":       ("humanoid_caster", 56, 57, None, "ae_engineer", F1),
    "Intake Hound":          ("beast_fast", 56, 57, None, "ae_construct_hound", F1),
    "Slag Elemental":        ("elemental_bruiser", 56, 57, None, "elemental_fire_1", F1),
    "Quench Hand":           ("humanoid_caster", 56, 57, None, "ae_crystal_weaver", F1),
    "Proving Frame":         ("elemental_bruiser", 57, 57, None, "ae_sentinel", F1),
    "Assembly Construct":    ("elemental_bruiser", 57, 57, None, "ae_crystal_golem", F1),
    "Foundry Gravity-Binder": ("humanoid_caster", 57, 57, None, "ae_gravity_binder", F1),
    "Foundry Overseer":      ("humanoid_caster", 57, 57, None, "ae_officer", F1),
    "Intake-Warden Brannoc Teal": ("humanoid_warrior", 56, 56, 2.5, "ab_intake_warden", F1),
    "The Slag Colossus":     ("elemental_bruiser", 56, 56, 2.5, "ab_slag_colossus", F1),
    "Pourmaster Ilka":       ("humanoid_caster", 57, 57, 1.6, "ab_pourmaster_ilka", F1),
    "Pourmaster Dov":        ("humanoid_warrior", 57, 57, 1.6, "ab_pourmaster_dov", F1),
    "Prototype Nine":        ("elemental_bruiser", 57, 57, 2.5, "ab_prototype_nine", F1),
    "Foundry-Master Cassor Vane": ("humanoid_caster", 57, 57, 2.8, "ab_foundry_master", F1),
    # ---- the Keelworks: the dry-dock crews, and the engine they're building
    "Keelworks Rigger":      ("humanoid_warrior", 57, 58, None, "ae_forge_worker", F2),
    "Keelworks Marine":      ("humanoid_warrior", 57, 58, None, "ae_legionary", F2),
    "Hull Welder":           ("humanoid_caster", 57, 58, None, "ae_engineer", F2),
    "Gantry Bomber":         ("elemental_caster", 57, 58, None, "ae_bomber_construct", F2),
    "Gravity Adept":         ("humanoid_caster", 57, 58, None, "ae_gravity_binder", F2),
    "Keel Sentinel":         ("elemental_bruiser", 57, 58, None, "ae_siege_walker", F2),
    "Repair Swarm":          ("elemental_caster", 58, 58, None, "ae_repair_drone", F2),
    "Gantry-Chief Dessa Marn": ("humanoid_caster", 58, 58, 2.5, "ab_gantry_chief", F2),
    "Gravity-Wright Iselle Varr": ("humanoid_caster", 58, 58, 2.5, "ab_gravity_wright", F2),
    "The Coreless":          ("elemental_caster", 58, 58, 2.5, "ab_coreless", F2),
    "The Warheart":          ("elemental_bruiser", 58, 58, 2.8, "ab_warheart", F2),
    # ---- the Halls of Ascent: the drill, the lancers, the storm and the question
    "Spire Recruit":         ("humanoid_warrior", 60, 60, None, "ae_legionary", S1),
    "Spire Drill Sergeant":  ("humanoid_warrior", 60, 60, None, "ae_officer", S1),
    "Spire Lancer":          ("humanoid_warrior", 60, 60, None, "ae_sky_lancer", S1),
    "Mounted Spire Lancer":  ("humanoid_warrior", 60, 60, None, "ae_lancer_mounted", S1),
    "Storm Chorister":       ("humanoid_caster", 60, 60, None, "ae_storm_caller", S1),
    "Bound Storm":           ("elemental_caster", 60, 60, None, "sk_storm_elemental", S1),
    "Spire Warden":          ("humanoid_warrior", 60, 60, None, "ae_city_guard", S1),
    "Spire Inquisitor":      ("humanoid_caster", 60, 60, None, "ae_inquisitor", S1),
    "Ash-Page Wisp":         ("elemental_caster", 60, 60, None, "sk_fading_wisp", S1),
    "Drillmaster Kaine Vorr": ("humanoid_warrior", 60, 60, 2.5, "ab_drillmaster", S1),
    "Lance-Commander Aris Thane": ("humanoid_warrior", 60, 60, 2.5, "ab_lance_commander", S1),
    "The Storm Choir":       ("humanoid_caster", 60, 60, 2.5, "ab_storm_choir", S1),
    "Archivist-Censor Mallen Roe": ("humanoid_caster", 60, 60, 2.5, "ab_archivist_censor", S1),
    "High Inquisitor Seren Vash": ("humanoid_caster", 60, 60, 2.8, "ab_high_inquisitor", S1),
    # ---- the Command Spire: the Exarch's own
    "Ascendant Honour Guard": ("humanoid_warrior", 60, 60, None, "ae_city_guard", S2),
    "Aegis Drone":           ("elemental_caster", 60, 60, None, "ae_shield_drone", S2),
    "War-Room Strategist":   ("humanoid_caster", 60, 60, None, "ae_officer", S2),
    "Ascendant Battle-Mage": ("humanoid_caster", 60, 60, None, "ae_magister", S2),
    "Exarch's Sentinel":     ("elemental_bruiser", 60, 60, None, "ae_construct_titan", S2),
    "The Aegis Engine":      ("elemental_caster", 60, 60, 2.5, "ab_aegis_engine", S2),
    "Warmarshal Dravin Kell": ("humanoid_warrior", 60, 60, 2.5, "ab_warmarshal", S2),
    "Ascendant Guard Corvo": ("humanoid_warrior", 60, 60, 1.6, "ae_high_commander", S2),
    "Ascendant Guard Lysse": ("humanoid_warrior", 60, 60, 1.6, "ae_warden", S2),
    "Exarch Lucan Thessaly": ("humanoid_caster", 60, 60, 2.8, "ab_exarch", S2),
}
BOSSES = {n for n, r in ROSTER.items() if r[3]}
#: one fight, two bosses: the second stands with the first, and the loot is the first's
PACK_MEMBER = {"Pourmaster Dov": "Pourmaster Ilka", "Ascendant Guard Lysse": "Ascendant Guard Corvo"}
FINALS = {"The Warheart": F2, "Exarch Lucan Thessaly": S2}
DUNGEONS = {GF.NAME: (F1, F2), AS.NAME: (S1, S2)}

#: trash: name -> (shape, school, [three ability names])
TRASH = {
    "Foundry Guard":         ("warrior", "physical", ["Crystal Halberd", "Hold the Door", "Braced"]),
    "Foundry Smith":         ("warrior", "fire", ["Forge Hammer", "Hot Iron", "Leather Apron"]),
    "Crucible Tender":       ("caster", "fire", ["Ladle of Slag", "Spilled Pour", "Seared"]),
    "Intake Hound":          ("beast", "physical", ["Bronze Bite", "Run Down", "Mauled"]),
    "Slag Elemental":        ("bruiser", "fire", ["Slag Fist", "Spatter", "Clinging Slag"]),
    "Quench Hand":           ("caster", "frost", ["Quench", "Steam Burst", "Chilled to the Bone"]),
    "Proving Frame":         ("bruiser", "physical", ["Test Strike", "Calibration Sweep", "Dented"]),
    "Assembly Construct":    ("bruiser", "arcane", ["Riveting Arm", "Assembly Pulse", "Pinned"]),
    "Foundry Gravity-Binder": ("caster", "arcane", ["Weight of Stone", "Gravity Well", "Heavy Limbs"]),
    "Foundry Overseer":      ("caster", "arcane", ["Overseer's Rod", "Work Faster", "Lashed"]),
    "Keelworks Rigger":      ("warrior", "physical", ["Marlinspike", "Cut the Line", "Sea Legs"]),
    "Keelworks Marine":      ("warrior", "physical", ["Boarding Blade", "Repel Boarders", "Shield Up"]),
    "Hull Welder":           ("caster", "fire", ["Welding Torch", "Seam Flare", "Weld-Burn"]),
    "Gantry Bomber":         ("caster", "fire", ["Drop Charge", "Carpet Bomb", "Shrapnel"]),
    "Gravity Adept":         ("caster", "arcane", ["Crushing Field", "Lift and Drop", "Weighed Down"]),
    "Keel Sentinel":         ("bruiser", "physical", ["Keel Hammer", "Stamp", "Flattened"]),
    "Repair Swarm":          ("caster", "arcane", ["Cutting Beam", "Swarm", "Arc-Burn"]),
    "Spire Recruit":         ("warrior", "physical", ["Practice Blade", "Eager Lunge", "Steadied"]),
    "Spire Drill Sergeant":  ("warrior", "physical", ["Drill Baton", "On Your Feet", "Parade Rest"]),
    "Spire Lancer":          ("warrior", "arcane", ["Lance Thrust", "Skyward Charge", "Crystal-Tipped"]),
    "Mounted Spire Lancer":  ("bruiser", "arcane", ["Mounted Thrust", "Wheeling Charge", "Trampled"]),
    "Storm Chorister":       ("caster", "nature", ["Sung Lightning", "Chorus of Thunder", "Static"]),
    "Bound Storm":           ("caster", "nature", ["Storm Bolt", "Wild Discharge", "Crackling"]),
    "Spire Warden":          ("warrior", "arcane", ["Warden's Blade", "Seal the Hall", "Warded"]),
    "Spire Inquisitor":      ("caster", "holy", ["Searing Word", "Redaction", "Condemned"]),
    "Ash-Page Wisp":         ("caster", "fire", ["Burning Word", "Ash of Pages", "Ink-Burn"]),
    "Ascendant Honour Guard": ("warrior", "physical", ["Honour Blade", "Close Ranks", "Bulwark"]),
    "Aegis Drone":           ("caster", "arcane", ["Pulse", "Projected Ward", "Arcane Burn"]),
    "War-Room Strategist":   ("caster", "arcane", ["Pointer Bolt", "Called Strike", "Marked"]),
    "Ascendant Battle-Mage": ("caster", "arcane", ["Crystal Lance", "Shard Storm", "Shard-Cut"]),
    "Exarch's Sentinel":     ("bruiser", "holy", ["Gilded Fist", "Radiant Sweep", "Dazzled"]),
}


def summon(name, creature, cooldown, max_alive, max_casts):
    return dict(name=name, kind="summon", amount=0, cooldown=cooldown, mana_cost=0,
                summon={"name": creature, "template": ROSTER[creature][0], "kit": kit_slug(creature),
                        "count": 1, "level_offset": -1, "max_alive": max_alive, "max_casts": max_casts})


def trash_kit(name):
    shape, s, names = TRASH[name]
    t = T(ROSTER[name][2])
    dispel = {"nature": "poison", "shadow": "curse"}.get(s, "magic")
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                debuff(names[2], 5, 3, {"agility": -30})]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 240})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.64), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.26), 4, 3, school=s, dispel_type=dispel)]
    return [dmg(names[0], t + 10, school=s), dmg(names[1], int(t * 0.64), cooldown=5, school=s, is_aoe=True),
            stun_hit(names[2], int(t * 0.6), cooldown=6, school=s)]


def boss_kit(level, school, basic, second, heavy, spread, mechanic, phase_name, *, signature, aoe=True, extra=()):
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


def kits():
    k = {n: trash_kit(n) for n in TRASH}
    # ---- the Foundry Halls
    k["Intake-Warden Brannoc Teal"] = boss_kit(   # the officer at the door: his hound, and he calls the guard
        56, "physical", "Warden's Rod", "Crystal Jab", "Rod of Office", "Sweep the Hall",
        stun_hit("Hound, Take Them", int(B(56) * 0.7), cooldown=6), "Shut the Gate",
        extra=[summon("Guard, to the Door", "Foundry Guard", 5, 2, 4)],
        signature=[dmg("Crystal Discharge", int(B(56) * 1.9), cooldown=5, school="arcane"),
                   last_gasp("Lock It Down", 56)])
    k["The Slag Colossus"] = boss_kit(            # slag that climbs out of the pour: burns, and slows as it cools
        56, "fire", "Slag Fist", "Molten Spatter", "Pour Over", "Slag Wave",
        hit_with("Cooling Crust", int(B(56) * 0.7), {"haste": -15, "agility": -30}, 3, school="fire", cooldown=5),
        "Reheated",
        extra=[hit_with("Hardened Slag", int(B(56) * 0.8), {"armor": 300}, 3, school="fire", on="buff", cooldown=6)],
        signature=[dot("Clinging Slag", int(B(56) * 0.5), 5, 4, school="fire", dispel_type="magic"),
                   last_gasp("Breaks Open", 56, "fire")])
    k["Pourmaster Ilka"] = boss_kit(              # she pours molten crystal
        57, "fire", "Ladle Strike", "Crucible Splash", "The Pour", "Spilled Crucible",
        dot("Molten Crystal", int(B(57) * 0.45), 5, 4, school="fire", dispel_type="magic"), "Pour It All",
        signature=[dmg("Pour on the Floor", int(B(57) * 1.2), cooldown=6, school="fire", is_aoe=True),
                   last_gasp("For My Brother", 57, "fire")])
    k["Pourmaster Dov"] = boss_kit(               # he quenches it ice-cold
        57, "frost", "Forge Hammer", "Quench", "Hammer Down", "Quenching Mist",
        stun_hit("Cold Shock", int(B(57) * 0.7), cooldown=6, school="frost"), "Steam and Fury",
        signature=[dmg("Shattering Blow", int(B(57) * 1.9), cooldown=5),
                   last_gasp("For My Sister", 57, "frost")])
    k["Prototype Nine"] = boss_kit(               # the construct nobody's ever switched off
        57, "arcane", "Crystal Fist", "Shield Bash", "Overcharged Blow", "Discharge",
        stun_hit("Crushing Grip", int(B(57) * 0.7), cooldown=6), "Never Switched Off",
        extra=[shell("Reflecting Shield", 6, 3, int(B(57) * 1.4), school="arcane")],
        signature=[dmg("Returned to Sender", int(B(57) * 1.9), cooldown=5, school="arcane"),
                   last_gasp("Core Breach", 57, "arcane", mult=1.7)])
    k["Foundry-Master Cassor Vane"] = boss_kit(   # gravity stones, and he drops the ceiling on you
        57, "arcane", "Gravity Hammer", "Orbiting Stone", "Hammer of Weight", "Stones Fall",
        hit_with("Doubled Weight", int(B(57) * 0.7), {"haste": -15, "agility": -30}, 3, school="arcane", cooldown=5),
        "The Foundry Answers",
        extra=[summon("Bring Me a Frame", "Assembly Construct", 5, 2, 4)],
        signature=[dmg("Drop the Ceiling", int(B(57) * 1.3), cooldown=6, is_aoe=True),
                   dmg("Crushing Field", int(B(57) * 2.0), cooldown=6, school="arcane"),
                   last_gasp("Everything Falls", 57, "arcane", mult=1.7)])
    # ---- the Keelworks
    k["Gantry-Chief Dessa Marn"] = boss_kit(      # the bomb-crystals, and the little bomber at her shoulder
        58, "fire", "Spanner", "Bomb-Crystal", "Satchel Charge", "Bombing Run",
        stun_hit("Concussion Charge", int(B(58) * 0.7), cooldown=6, school="fire"), "Light the Fuses",
        extra=[summon("Launch the Bomber", "Gantry Bomber", 5, 2, 4)],
        signature=[dot("Burning Shrapnel", int(B(58) * 0.5), 5, 4, school="fire", dispel_type="magic"),
                   last_gasp("Blow the Gantry", 58, "fire")])
    k["Gravity-Wright Iselle Varr"] = boss_kit(   # lifts the floor out from under you and drops it again
        58, "arcane", "Floating Rubble", "Lift", "Drop", "Rubble Storm",
        stun_hit("Pinned to the Ceiling", int(B(58) * 0.7), cooldown=6, school="arcane"), "Weightless",
        extra=[hit_with("Crushing Weight", int(B(58) * 0.7), {"haste": -15, "attack_power": -60}, 3, school="arcane",
                        cooldown=5)],
        signature=[dmg("Floor Falls Away", int(B(58) * 1.2), cooldown=6, school="arcane", is_aoe=True),
                   dmg("Collapse", int(B(58) * 1.9), cooldown=6)])
    k["The Coreless"] = boss_kit(                 # an engine core with no ship: unstable, and it overloads
        58, "nature", "Arc", "Ring Strike", "Surge", "Unstable Field",
        hit_with("Static Lock", int(B(58) * 0.7), {"haste": -15, "spell_power": -40}, 3, school="nature", cooldown=5),
        "Overload Building",
        extra=[hit_with("Containment Rings", int(B(58) * 0.8), {"armor": 300}, 3, school="arcane", on="buff",
                        cooldown=6)],
        signature=[dmg("Overload", int(B(58) * 1.3), cooldown=6, school="nature", is_aoe=True),
                   dot("Radiant Arcs", int(B(58) * 0.5), 5, 4, school="nature", dispel_type="magic"),
                   last_gasp("Core Meltdown", 58, "arcane", mult=1.7)])
    k["The Warheart"] = boss_kit(                 # the first warship's heart, awake: cannons, and the engine burns hotter
        58, "fire", "Bronze Rib", "Deck Cannon", "Broadside", "Engine Wash",
        stun_hit("Grapeshot", int(B(58) * 0.75), cooldown=6), "Full Burn",
        extra=[summon("Crew to Stations", "Keelworks Marine", 4, 2, 5),
               hit_with("Scalding Steam", int(B(58) * 0.7), {"healing_power": -60, "haste": -10}, 3, school="fire",
                        cooldown=5)],
        signature=[dmg("Every Gun at Once", int(B(58) * 1.3), cooldown=6, school="fire", is_aoe=True),
                   dmg("Ram", int(B(58) * 2.0), cooldown=6),
                   last_gasp("The Engine Burns", 58, "fire", mult=1.8)])
    # ---- the Halls of Ascent
    k["Drillmaster Kaine Vorr"] = boss_kit(       # the drill: shield wall, and he calls his recruits in
        60, "physical", "Drill Baton", "Shield Slam", "Drill Strike", "Form Ranks",
        stun_hit("Tower Shield Charge", int(B(60) * 0.7), cooldown=6), "Again, Properly",
        extra=[summon("Recruits, Forward", "Spire Recruit", 5, 2, 4),
               shell("Shield Wall", 6, 3, int(B(60) * 1.3))],
        signature=[dmg("The Drill Bit", int(B(60) * 2.0), cooldown=6),
                   last_gasp("Last Drill", 60)])
    k["Lance-Commander Aris Thane"] = boss_kit(   # the charge down the hall, and the lance through the front line
        60, "arcane", "Crystal Lance", "Wheeling Strike", "Lance Through", "Trample",
        stun_hit("The Charge", int(B(60) * 0.75), cooldown=6), "Lances Down",
        extra=[summon("Wing, Form Up", "Mounted Spire Lancer", 5, 2, 4)],
        signature=[dmg("Skewer", int(B(60) * 2.0), cooldown=6, school="arcane"),
                   last_gasp("The Grand Charge", 60, "arcane")])
    k["The Storm Choir"] = boss_kit(              # three callers, one voice: the storm builds while they sing
        60, "nature", "Sung Lightning", "Harmony", "Crescendo", "Chorus of Thunder",
        hit_with("Deafening", int(B(60) * 0.7), {"haste": -15, "spell_power": -40}, 3, school="nature", cooldown=5),
        "The Storm Builds",
        extra=[summon("Call the Storm", "Bound Storm", 5, 2, 4)],
        signature=[dmg("Thunderhead", int(B(60) * 1.3), cooldown=6, school="nature", is_aoe=True),
                   dot("Static Charge", int(B(60) * 0.5), 5, 4, school="nature", dispel_type="magic")])
    k["Archivist-Censor Mallen Roe"] = boss_kit(  # burns what he's told to, and you with it
        60, "fire", "Burning Book", "Crystal Quill", "Strike It Out", "Pages in the Air",
        hit_with("Redacted", int(B(60) * 0.7), {"spell_power": -40, "attack_power": -60}, 3, school="holy", cooldown=5),
        "Into the Fire",
        signature=[dot("Burning Pages", int(B(60) * 0.5), 5, 4, school="fire", dispel_type="magic"),
                   dmg("Burn the Archive", int(B(60) * 1.2), cooldown=6, school="fire", is_aoe=True),
                   last_gasp("Nothing Left to Read", 60, "fire")])
    k["High Inquisitor Seren Vash"] = boss_kit(   # the censer, the question, and the cell for whoever won't answer
        60, "holy", "Censer Swing", "Blue Fire", "The Question", "Censer Smoke",
        stun_hit("To the Cell", int(B(60) * 0.75), cooldown=6, school="holy"), "No More Questions",
        extra=[heal("Absolution", int(B(60) * 1.2), cooldown=6),
               hit_with("Interrogation", int(B(60) * 0.7), {"healing_power": -60, "haste": -10}, 3, school="shadow",
                        cooldown=5)],
        signature=[dmg("Purge the Unworthy", int(B(60) * 1.3), cooldown=6, school="holy", is_aoe=True),
                   dmg("Confession", int(B(60) * 2.0), cooldown=6, school="shadow"),
                   last_gasp("Final Judgement", 60, "holy", mult=1.7)])
    # ---- the Command Spire
    k["The Aegis Engine"] = boss_kit(             # drones, and a dome you fight inside
        60, "arcane", "Pylon Strike", "Shield Pulse", "Focused Beam", "Dome Pulse",
        hit_with("Drained Ward", int(B(60) * 0.7), {"armor": -300, "spell_power": -40}, 3, school="arcane", cooldown=5),
        "Overcharge the Dome",
        extra=[summon("Launch Drones", "Aegis Drone", 5, 2, 4),
               shell("Aegis", 6, 3, int(B(60) * 1.4), school="arcane")],
        signature=[dmg("The Dome Closes", int(B(60) * 1.3), cooldown=6, school="arcane", is_aoe=True),
                   last_gasp("Shield Collapse", 60, "arcane", mult=1.7)])
    k["Warmarshal Dravin Kell"] = boss_kit(       # calls the guns: bombardment, and orders for whoever's left
        60, "physical", "Command Baton", "Officer's Blade", "Decisive Blow", "Call the Guns",
        stun_hit("Bombardment", int(B(60) * 0.75), cooldown=6, school="fire"), "All Batteries",
        extra=[hit_with("Marked for the Guns", int(B(60) * 0.7), {"armor": -300, "haste": -10}, 3, cooldown=5)],
        signature=[dmg("Fire for Effect", int(B(60) * 1.3), cooldown=6, school="fire", is_aoe=True),
                   dmg("Execute the Order", int(B(60) * 2.0), cooldown=6),
                   last_gasp("Danger Close", 60, "fire")])
    k["Ascendant Guard Corvo"] = boss_kit(        # the shield
        60, "physical", "Shield Edge", "Guard's Blade", "Bulwark Slam", "Shield Sweep",
        stun_hit("Shield Charge", int(B(60) * 0.7), cooldown=6), "Hold for the Exarch",
        extra=[shell("Interpose", 6, 3, int(B(60) * 1.3))],
        signature=[dmg("Crushing Shield", int(B(60) * 1.9), cooldown=6),
                   last_gasp("For the Exarch", 60)])
    k["Ascendant Guard Lysse"] = boss_kit(        # the blade
        60, "arcane", "Twin Blades", "Crystal Cut", "Flurry", "Whirling Edge",
        dot("Deep Cuts", int(B(60) * 0.45), 5, 4, dispel_type="magic", school="arcane"), "Blades Bright",
        signature=[dmg("Through the Gap", int(B(60) * 1.9), cooldown=5, school="arcane"),
                   last_gasp("For the General", 60, "arcane")])
    k["Exarch Lucan Thessaly"] = boss_kit(        # the general's right hand: crystal, light, and the sky itself
        60, "arcane", "Crystal Sword", "Shard Crown", "Judgement of the Sky", "Shardstorm",
        stun_hit("Kneel to the Ascendancy", int(B(60) * 0.75), cooldown=6, school="holy"), "The Sky Obeys",
        extra=[summon("Honour Guard", "Ascendant Honour Guard", 4, 2, 5),
               hit_with("Unworthy of the Sky", int(B(60) * 0.7), {"healing_power": -60, "haste": -10}, 3,
                        school="holy", cooldown=5)],
        signature=[dmg("The Sky Falls", int(B(60) * 1.3), cooldown=6, school="nature", is_aoe=True),
                   dmg("Lance of Light", int(B(60) * 2.0), cooldown=6, school="holy"),
                   last_gasp("Ascendant", 60, "arcane", mult=1.8)])
    return k


A, W = (lambda t: ("a", t)), (lambda t: ("w", t))
#: boss -> [(item, slot, suffix, (a|w, type) or None, stat template)], four each, a pair's leader eight
POOLS = {
    "Intake-Warden Brannoc Teal": [
        ("Intake-Warden's Coat", "chest", "of the Monkey", A("leather"), "agi_physical"),
        ("Rod of the South Gate", "main_hand", "of the Sorcerer", W("mace_1h"), "int_caster"),
        ("Soot-Stained Gauntlets", "hands", "of the Bear", A("plate"), "str_physical"),
        ("Hound-Handler's Bracers", "wrist", "of the Wolf", A("mail"), "agi_int_hybrid")],
    "The Slag Colossus": [
        ("Slagborn Greaves", "feet", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("Cooling Crust Girdle", "waist", "of the Tiger", A("leather"), "agi_physical"),
        ("Heart of the Pour", "neck", "of the Prophet", None, "spi_healer"),
        ("Slag-Crusted Maul", "main_hand", "of the Champion", W("mace_2h"), "str_physical")],
    "Pourmaster Ilka": [
        ("Ilka's Crucible Ladle", "main_hand", "of the Invoker", W("staff"), "int_caster"),
        ("Pourmaster's Apron", "chest", "of the Prophet", A("cloth"), "spi_healer"),
        ("Molten-Dipped Gloves", "hands", "of the Sorcerer", A("cloth"), "int_caster"),
        ("Ring of the Pour", "ring", "of the Monkey", None, "agi_physical"),
        ("Dov's Quenching Hammer", "main_hand", "of the Champion", W("mace_1h"), "str_physical"),
        ("Quench-Hardened Pauldrons", "shoulder", "of the Bear", A("plate"), "str_physical"),
        ("Twin Smiths' Leggings", "legs", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Steam-Scarred Boots", "feet", "of the Tiger", A("leather"), "agi_physical")],
    "Prototype Nine": [
        ("Reflecting Crystal Bulwark", "off_hand", "of the Bear", W("shield"), "str_physical"),
        ("Exposed-Cable Wristguards", "wrist", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("Ninth Prototype's Core", "neck", "of the Sorcerer", None, "int_caster"),
        ("Test-Hall Leggings", "legs", "of the Monkey", A("leather"), "agi_physical")],
    "Foundry-Master Cassor Vane": [
        ("Cassor's Gravity Hammer", "main_hand", "of the Champion", W("mace_2h"), "str_physical"),
        ("Harness of Orbiting Stones", "chest", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Foundry-Master's Mantle", "shoulder", "of the Prophet", A("cloth"), "spi_healer"),
        ("Overseer's Signet", "ring", "of the Invoker", None, "int_caster")],
    "Gantry-Chief Dessa Marn": [
        ("Gantry-Chief's Hover Boots", "feet", "of the Monkey", A("leather"), "agi_physical"),
        ("Bomb-Crystal Launcher", "ranged", "of the Hunt", W("gun"), "agi_physical"),
        ("Crystal Goggle Band", "head", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Satchel-Strap Belt", "waist", "of the Sorcerer", A("cloth"), "int_caster")],
    "Gravity-Wright Iselle Varr": [
        ("Iselle's Weightless Robes", "chest", "of the Sorcerer", A("cloth"), "int_caster"),
        ("Rubble-Bound Gauntlets", "hands", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("Gravity-Wright's Focus", "off_hand", "of the Prophet", W("tome"), "spi_healer"),
        ("Cloak of the Lifted Floor", "back", "of the Tiger", A("cloth"), "agi_physical")],
    "The Coreless": [
        ("Containment Ring Girdle", "waist", "of the Bear", A("plate"), "str_physical"),
        ("Flickering Core Shard", "ranged", "of the Invoker", W("wand"), "int_caster"),
        ("Arc-Scorched Spaulders", "shoulder", "of the Monkey", A("leather"), "agi_physical"),
        ("Unstable Band", "ring", "of the Prophet", None, "spi_healer")],
    "The Warheart": [
        ("Warheart Cannon-Barrel", "ranged", "of the Hunt", W("crossbow"), "agi_physical"),
        ("Keel-Rib Breastplate", "chest", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("First Warship's Wheel-Spoke", "main_hand", "of the Champion", W("polearm"), "str_physical"),
        ("Engine-Stoker's Leggings", "legs", "of the Prophet", A("cloth"), "spi_healer")],
    "Drillmaster Kaine Vorr": [
        ("Drillmaster's Tower Shield", "off_hand", "of the Gorilla", W("shield"), "str_int_hybrid"),
        ("Parade-Ground Greaves", "legs", "of the Bear", A("plate"), "str_physical"),
        ("Recruit-Breaker's Bracers", "wrist", "of the Monkey", A("leather"), "agi_physical"),
        ("Drill Baton", "main_hand", "of the Prophet", W("mace_1h"), "spi_healer")],
    "Lance-Commander Aris Thane": [
        ("Lance of the Winged Charge", "main_hand", "of the Champion", W("polearm"), "str_physical"),
        ("Lancer-Commander's Spurs", "feet", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Crystal Wing Cloak", "back", "of the Monkey", A("cloth"), "agi_physical"),
        ("Thane's Riding Gloves", "hands", "of the Tiger", A("leather"), "agi_physical")],
    "The Storm Choir": [
        ("Chorister's Storm Staff", "main_hand", "of the Sorcerer", W("staff"), "int_caster"),
        ("Robes of the Three Voices", "chest", "of the Prophet", A("cloth"), "spi_healer"),
        ("Thunder-Sung Coif", "head", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Pendant of Harmony", "neck", "of the Invoker", None, "int_caster")],
    "Archivist-Censor Mallen Roe": [
        ("The Censor's Burning Book", "off_hand", "of the Sorcerer", W("tome"), "int_caster"),
        ("Ash-Grey Cuffs", "wrist", "of the Prophet", A("cloth"), "spi_healer"),
        ("Crystal Quill-Knife", "main_hand", "of the Monkey", W("dagger"), "agi_physical"),
        ("Ember-Singed Sash", "waist", "of the Wolf", A("mail"), "agi_int_hybrid")],
    "High Inquisitor Seren Vash": [
        ("Mask of the High Inquisitor", "head", "of the Prophet", A("cloth"), "spi_healer"),
        ("Censer of Blue Fire", "main_hand", "of the Gorilla", W("mace_1h"), "str_int_hybrid"),
        ("Inquisitor's Restraints", "hands", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Interrogator's Leggings", "legs", "of the Tiger", A("leather"), "agi_physical")],
    "The Aegis Engine": [
        ("Aegis-Core Pendant", "neck", "of the Bear", None, "str_physical"),
        ("Dome-Projector Pauldrons", "shoulder", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("Drone-Linked Wristwraps", "wrist", "of the Sorcerer", A("cloth"), "int_caster"),
        ("Shield-Pylon Leggings", "legs", "of the Hunt", A("mail"), "agi_physical")],
    "Warmarshal Dravin Kell": [
        ("Warmarshal's Crested Helm", "head", "of the Bear", A("plate"), "str_physical"),
        ("Gunnery Spyglass Rifle", "ranged", "of the Hunt", W("gun"), "agi_physical"),
        ("Command Baton of the Spire", "main_hand", "of the Invoker", W("sword_1h"), "int_caster"),
        ("Map-Table Gloves", "hands", "of the Prophet", A("leather"), "spi_healer")],
    "Ascendant Guard Corvo": [
        ("Corvo's Bulwark Belt", "waist", "of the Bear", A("plate"), "str_physical"),
        ("Honour Guard's Greatblade", "main_hand", "of the Champion", W("sword_2h"), "str_physical"),
        ("Exarch's Guard Mantle", "shoulder", "of the Wolf", A("mail"), "agi_int_hybrid"),
        ("Band of the Sworn Guard", "ring", "of the Gorilla", None, "str_int_hybrid"),
        ("Lysse's Crystal Edge", "main_hand", "of the Monkey", W("sword_1h"), "agi_physical"),
        ("Lysse's Second Edge", "main_hand", "of the Tiger", W("fist_weapon"), "agi_physical"),
        ("Bladedancer's Jerkin", "chest", "of the Monkey", A("leather"), "agi_physical"),
        ("Guard's Vigil Cloak", "back", "of the Prophet", A("cloth"), "spi_healer")],
    "Exarch Lucan Thessaly": [
        ("Shard-Crown of the Exarch", "head", "of the Sorcerer", A("cloth"), "int_caster"),
        ("Right Hand's Crystal Sword", "main_hand", "of the Champion", W("sword_1h"), "str_physical"),
        ("Deep-Blue Cloak of Command", "back", "of the Prophet", A("cloth"), "spi_healer"),
        ("Gleaming Ascendant Sabatons", "feet", "of the Gorilla", A("plate"), "str_int_hybrid")],
}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows, moved = {}, [], 0
    for b, items in POOLS.items():
        ilvl = ROSTER[b][2] + 3
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
            d["item_id"] = "cit_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
                moved += 1
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[b] = built
    return out, rows, moved


def check(k, loot):
    bad = []
    if set(k) != set(ROSTER):
        bad.append(f"kits and roster differ: {sorted(set(k) ^ set(ROSTER))}")
    want = BOSSES - set(PACK_MEMBER)
    if set(POOLS) != want:
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ want)}")
    for b, items in POOLS.items():
        n = 8 if b in PACK_MEMBER.values() else 4
        if len(items) != n:
            bad.append(f"{b}: {len(items)} items, wanted {n}")
    for fl, mod in MAPS.items():
        mod.build_floor(fl)
        spec = mod.FLOOR[fl]
        placed = set(mod.BOSSES[fl]) | {m[2] for ms in spec.get("pack", {}).values() for m in ms}
        ours = {n for n in BOSSES if ROSTER[n][5] == fl}
        if placed != ours:
            bad.append(f"{fl}: bosses on the map {sorted(placed)} differ from the roster {sorted(ours)}")
        on_map = {m for p in mod.trash(fl) for (_x, _y, m, _l) in p}
        theirs = {n for n, r in ROSTER.items() if r[5] == fl and not r[3]}
        if on_map - theirs:
            bad.append(f"{fl}: trash on the map that isn't this floor's: {sorted(on_map - theirs)}")
        if theirs - on_map:
            bad.append(f"{fl}: trash in the roster that never stands on the map: {sorted(theirs - on_map)}")
        lo, hi = ZONE_LEVELS[fl]
        for n, r in ROSTER.items():
            if r[5] == fl and not (lo <= r[1] and r[2] <= hi):
                bad.append(f"{n} ({r[1]}-{r[2]}) sits outside {fl} {lo}-{hi}")
        for p in mod.trash(fl):
            for (_x, _y, m, lvl) in p:
                if not ROSTER[m][1] <= lvl <= ROSTER[m][2]:
                    bad.append(f"{fl}: {m} placed at {lvl}, outside its {ROSTER[m][1]}-{ROSTER[m][2]}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, (_t, lo_, hi_, _m, sprite, _f) in ROSTER.items():
        prior = existing.get(name)
        if prior and prior.get("level_range") != [lo_, hi_]:
            bad.append(f"{name} already exists elsewhere at {prior.get('level_range')}; names never repeat")
        if not ((ROOT / "assets/creatures" / f"{sprite}.png").exists() or (SRC / f"{sprite}.png").exists()):
            bad.append(f"{name}'s sprite {sprite} is not on disk")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    return bad


RULES_START = "    # THE CITADEL DUNGEONS (generated by tools/build_citadel_dungeons_content.py; do not edit by hand)\n"
RULES_END = "    # END THE CITADEL DUNGEONS\n"


def write_sprite_rules():
    import re
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{r[4]}"),\n'
                                  for n, r in ROSTER.items()) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE ASCENDANT BASTIONS (generated by tools/build_ascendant_bastions_content.py; do not edit by hand)\n"
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def install_sprites():
    n = 0
    for (_t, _lo, _hi, _m, sprite, _f) in ROSTER.values():
        src, dst = SRC / f"{sprite}.png", ROOT / "assets/creatures" / f"{sprite}.png"
        if src.exists() and (not dst.exists() or src.read_bytes() != dst.read_bytes()):
            shutil.copyfile(src, dst)
            n += 1
    return n


def _write(path, data, raw):
    indent, newline = _detect_format(json.loads(raw), raw)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")


def pay_the_aetherians():
    raw = FACTIONS.read_text(encoding="utf-8")
    d = json.loads(raw)
    fs = d["factions"] if "factions" in d else d
    fs["aetherians"]["dungeon_rep"] = {
        "_comment": "A boss kill in the Citadel of Ascent's two dungeons pays 75 "
                    "(tools/build_citadel_dungeons_content.py).",
        "per_boss": 75,
        "dungeons": [F1, F2, S1, S2],
    }
    _write(FACTIONS, d, raw)


def main():
    copied = install_sprites()
    k = kits()
    loot, rows, moved = build_loot()
    bad = check(k, loot)
    problems = loot_audit(rows)
    if bad or problems:
        print("FAILED - fix the data, not the check:")
        for b in bad + problems:
            print("  -", b)
        return 1
    creatures = {}
    for name, (template, lo, hi, mult, _s, _f) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")
    write_sprite_rules()

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    caves = enc["zones"].setdefault(PARENT, {"name": PARENT}).setdefault("caves", {})
    for fl in MAPS:
        caves[fl] = {"name": fl, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items() if r[5] == fl}}
    _write(ENCOUNTERS, enc, raw)
    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    lv["zones"].update(ZONE_LEVELS)
    _write(LEVELS, lv, raw)
    pay_the_aetherians()
    out = {"_notes": ("Boss loot for the Citadel of Ascent's two dungeons on the Ascendant Bastions: the Gravity "
                      "Foundry (56-58) and the Ascendant Spire (60). ONE item per kill from the boss's four (a pair's "
                      "eight); item_level = boss level + 3. Hand-authored in tools/build_citadel_dungeons_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(BOSSES)} bosses); {copied} sprites installed; "
          f"{sum(len(v) for v in loot.values())} boss items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
