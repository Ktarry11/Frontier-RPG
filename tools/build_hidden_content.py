#!/usr/bin/env python3
"""Creatures, kits, encounter tables, loot and the registry for the hidden zones. Idempotent.

    PYTHONPATH=. python3 tools/build_hidden_content.py

SPOILERS (Kyle, 14 Nov 2026: "I don't want to see as I want these to be secrets"). This file says
what lives in each hidden zone and what it drops. It does not say how to get in: the doors are
picked by tools/build_secrets.py.

Writes:
  data/world/hidden_zones.json            the registry world/hidden_zones.py reads
  data/creatures/ability_kits.json        the kits (merged)
  data/creatures/creatures.json           the creatures (merged)
  data/creatures/encounters.json          each zone's table (a layer under its region's caves,
                                          a skull zone at the top level)
  data/loot/hidden_boss_loot.json         every boss's pool: 4-5 item levels over the boss, two
                                          drops a kill, and from level 30 a one-of-a-kind epic

HOW HARD (data/balance/monster_difficulty.json): a layer's monsters are 4x health and 4.5x damage,
a skull zone's 2.5x and 2.5x, trash and bosses alike. Kits below are written at the ordinary
strength for the creature's level (KIT_CURVE, measured off the game's own kits) and the
multiplier does the rest, so the two stay separate and either can be tuned alone.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_durotar_content import make  # noqa: E402
from tools.build_return_voyage_content import merge_json  # noqa: E402

DATA = ROOT / "data"

#: Median first-ability damage of the game's existing kits by level band (trash, boss), measured
#: 14 Nov 2026 over creatures.json + ability_kits.json.
KIT_CURVE = {5: (32, 68), 10: (44, 97), 15: (51, 124), 20: (62, 165), 25: (87, 205),
             30: (134, 287), 35: (147, 314), 40: (162, 365), 45: (196, 385)}


def base(level, boss=False):
    ks = sorted(KIT_CURVE)
    lo = max([k for k in ks if k <= level] or [ks[0]])
    hi = min([k for k in ks if k >= level] or [ks[-1]])
    a, b = KIT_CURVE[lo][1 if boss else 0], KIT_CURVE[hi][1 if boss else 0]
    t = 0 if hi == lo else (level - lo) / (hi - lo)
    return a + (b - a) * t


def kit(level, boss, abilities):
    """abilities: (name, kind, mult, cd, school, extra). mult scales the level's basic hit;
    for a buff/debuff it is ignored. Mana is a token cost for casters."""
    b = base(level, boss)
    out = []
    for (name, kind, mult, cd, school, extra) in abilities:
        amt = 0 if kind in ("buff", "debuff") else int(round(b * mult))
        if kind == "dot":
            amt = int(round(b * mult))
        mana = 0 if (cd == 0 and not out) else (12 if school == "magic" else 0)
        e = {"name": name, "kind": kind, "amount": amt, "cooldown": cd, "mana_cost": mana, "school": school}
        e.update(extra or {})
        out.append(e)
    first = out[0]
    assert first["kind"] == "damage" and first["cooldown"] == 0, first
    first["mana_cost"] = 0
    for e in out:
        if e["kind"] in ("dot", "buff", "debuff"):
            assert "duration" in e, e
        if e["kind"] in ("buff", "debuff"):
            assert e.get("stat_mods"), e
    return out


def D(n):
    return {"duration": n}


def MODS(n, **mods):
    return {"duration": n, "stat_mods": mods}


def SELF(n, **mods):
    return {"duration": n, "stat_mods": mods, "self_only": True}


# ============================================================================== THE ZONES
# Each creature: name -> (template, level, boss, sprite, abilities)
ZONES = {}

ZONES["The Cinderwell"] = dict(
    kind="layer", parent="Ragefire Chasm", region="Orgrimmar", levels=(17, 19),
    creatures={
        "Cinderwell Zealot": ("humanoid_warrior", 17, False, "cultist_robed", [
            ("Brand", "damage", 1.0, 0, "physical", {}),
            ("Kindle the Faithful", "buff", 0, 4, "magic", SELF(3, attack_power=14)),
            ("Searing Cut", "dot", 0.35, 3, "physical", D(3))]),
        "Cinderwell Pyrecaller": ("humanoid_caster", 17, False, "fel_cultist", [
            ("Cinder Bolt", "damage", 1.0, 0, "magic", {}),
            ("Pyre Hymn", "dot", 0.4, 3, "magic", D(3)),
            ("Ash in the Eyes", "debuff", 0, 4, "magic", MODS(3, agility=-10))]),
        "Slagborn Elemental": ("elemental_bruiser", 18, False, "elemental_fire", [
            ("Slag Fist", "damage", 1.05, 0, "physical", {}),
            ("Molten Skin", "buff", 0, 5, "magic", SELF(3, armor=40)),
            ("Spatter", "damage", 1.4, 3, "magic", {})]),
        "Kiln Hound": ("demon_hound", 17, False, "felhound", [
            ("Scorch Bite", "damage", 0.95, 0, "physical", {}),
            ("Coal Breath", "dot", 0.3, 3, "magic", D(3))]),
        "Ashcaller Vorn": ("humanoid_caster", 18, True, "cult_overseer", [
            ("Word of Ash", "damage", 1.0, 0, "magic", {}),
            ("Call the Pyre", "dot", 0.45, 3, "magic", D(4)),
            ("Burn the Doubt Out", "debuff", 0, 4, "magic", MODS(3, magic_resistance=-25, intellect=-8)),
            ("Ash Ward", "buff", 0, 5, "magic", SELF(3, magic_resistance=30, armor=30)),
            ("Immolation Sermon", "damage", 1.8, 4, "magic", {})]),
        "The Furnace Heart": ("elemental_bruiser", 19, True, "elemental_fire", [
            ("Heartbeat", "damage", 1.0, 0, "magic", {}),
            ("Overflow", "damage", 1.9, 3, "magic", {}),
            ("Melt", "debuff", 0, 4, "magic", MODS(3, armor=-60)),
            ("Fed by the Faithful", "buff", 0, 6, "magic", SELF(3, attack_power=30)),
            ("Living Fire", "dot", 0.5, 3, "magic", D(4))]),
    },
    weights={"Cinderwell Zealot": 3, "Cinderwell Pyrecaller": 2, "Slagborn Elemental": 2, "Kiln Hound": 3},
    loot={
        "Ashcaller Vorn": [
            ("Vorn's Unburnt Hand", "main_hand", "of the Sorcerer", "A wand of fused bone. The cult said it never cooled.", None, "wand"),
            ("Cassock of the Inner Kiln", "chest", "of Fiery Wrath", "Stitched from robes that went into the well and came back.", "cloth", None),
            ("Tithe-Taker's Grips", "hands", "of the Tiger", "Every finger is scarred where the coins were hot.", "leather", None),
            ("Smoke-Stained Cord", "waist", "of the Eagle", "It smells of the deep vents no matter how long it's aired.", "mail", None),
        ],
        "The Furnace Heart": [
            ("Heartstone Maul", "main_hand", "of the Bear", "It's warm. It's always going to be warm.", None, "mace_2h"),
            ("Kilnplate Pauldrons", "shoulder", "of the Champion", "Hammered out over the well itself.", "plate", None),
            ("Cinder-Walker's Boots", "feet", "of the Monkey", "The soles are glass.", "leather", None),
            ("Ember of the Well", "neck", "of the Invoker", "A coal on a chain that has never gone out.", None, None),
            ("Furnace-Born Bulwark", "off_hand", None, "A shield poured, not forged.", None, "shield"),
        ],
    },
)

ZONES["The Dreaming Root"] = dict(
    kind="layer", parent="Wailing Caverns", region="Central Barrens", levels=(23, 25),
    creatures={
        "Dreamrot Lasher": ("beast_basic", 23, False, "vine_strangler", [
            ("Rotting Lash", "damage", 1.0, 0, "physical", {}),
            ("Sleep-Thorn", "debuff", 0, 4, "magic", MODS(3, agility=-12)),
            ("Strangle", "dot", 0.35, 3, "physical", D(3))]),
        "Nightmare Deviate": ("beast_fast", 23, False, "raptor", [
            ("Waking Claw", "damage", 1.0, 0, "physical", {}),
            ("Night Terror", "damage", 1.5, 3, "magic", {}),
            ("Fevered Bite", "dot", 0.3, 3, "physical", D(3))]),
        "Sleepwalking Druid": ("humanoid_caster", 24, False, "priest_hooded", [
            ("Murmured Wrath", "damage", 1.0, 0, "magic", {}),
            ("Dream-Mend", "heal", 1.6, 4, "magic", {}),
            ("Somnolence", "debuff", 0, 4, "magic", MODS(3, intellect=-10, attack_power=-12))]),
        "Vel'dran the Unwaking": ("humanoid_caster", 25, True, "treant", [
            ("Root-Wrath", "damage", 1.0, 0, "magic", {}),
            ("The Long Sleep", "debuff", 0, 4, "magic", MODS(3, agility=-20, intellect=-15)),
            ("Nightmare Bloom", "dot", 0.5, 3, "magic", D(4)),
            ("Bark of the Dreamer", "buff", 0, 5, "magic", SELF(3, armor=70)),
            ("Drink the Pool", "heal", 2.2, 5, "magic", {}),
            ("Wake Screaming", "damage", 1.9, 4, "magic", {})]),
    },
    weights={"Dreamrot Lasher": 3, "Nightmare Deviate": 3, "Sleepwalking Druid": 2},
    loot={
        "Vel'dran the Unwaking": [
            ("Staff of the Unwaking", "main_hand", "of the Prophet", "Root, knotted round a pearl that dreams.", None, "staff"),
            ("Dreamwalker Leggings", "legs", "of the Wolf", "Worn by someone who walked a long way without waking.", "leather", None),
            ("Thornbed Hauberk", "chest", "of the Hunt", "The thorns are on the inside. They don't hurt. That's worse.", "mail", None),
            ("Somnus Band", "ring", "of the Owl", "You feel rested wearing it, and you shouldn't.", None, None),
            ("Pool-Drinker's Bracers", "wrist", "of the Bear", "Stained a green that won't wash out.", "plate", None),
        ],
    },
)

ZONES["The Ossuary Below"] = dict(
    kind="layer", parent="Shadowfang Keep", region="Silverpine South", levels=(26, 28),
    creatures={
        "Ossuary Ghoul": ("undead_basic", 26, False, "ghoul", [
            ("Gnaw", "damage", 1.0, 0, "physical", {}),
            ("Grave Fever", "dot", 0.35, 3, "physical", D(3)),
            ("Frenzy of the Starved", "buff", 0, 5, "physical", SELF(3, attack_power=20))]),
        "Bonewrought Worgen": ("humanoid_warrior", 27, False, "worgen", [
            ("Rend", "damage", 1.0, 0, "physical", {}),
            ("Bone-Splitter", "damage", 1.5, 3, "physical", {}),
            ("Howl of the Kept", "debuff", 0, 4, "physical", MODS(3, armor=-30))]),
        "Whispering Shade": ("undead_caster", 26, False, "wraith_pale", [
            ("Cold Whisper", "damage", 1.0, 0, "magic", {}),
            ("What He Told Them", "debuff", 0, 4, "magic", MODS(3, intellect=-12, magic_resistance=-15)),
            ("Grief", "dot", 0.4, 3, "magic", D(3))]),
        "Gnasher, the Bone-Fed": ("beast_large", 27, True, "worg", [
            ("Crunch", "damage", 1.0, 0, "physical", {}),
            ("Marrow Hunger", "heal", 1.8, 5, "physical", {}),
            ("Hamstring Bite", "debuff", 0, 4, "physical", MODS(3, agility=-20)),
            ("Bone Shrapnel", "dot", 0.45, 3, "physical", D(3)),
            ("Gorge", "damage", 2.0, 4, "physical", {})]),
        "The Archmage's Shade": ("undead_caster", 28, True, "spectre", [
            ("Shadowbolt, Remembered", "damage", 1.0, 0, "magic", {}),
            ("The Curse He Gave the Wolves", "dot", 0.5, 3, "magic", D(4)),
            ("Unmake Ward", "debuff", 0, 4, "magic", MODS(3, magic_resistance=-35)),
            ("Not Quite Here", "buff", 0, 5, "magic", SELF(3, armor=60, magic_resistance=40)),
            ("Void Rupture", "damage", 2.0, 4, "magic", {})]),
    },
    weights={"Ossuary Ghoul": 3, "Bonewrought Worgen": 2, "Whispering Shade": 2},
    loot={
        "Gnasher, the Bone-Fed": [
            ("Marrowcrack Axe", "main_hand", "of the Tiger", "Notched where it caught on something it didn't cut.", None, "axe_1h"),
            ("Kennelmaster's Hide", "chest", "of the Monkey", "Whoever kept him here wore this. It didn't help.", "leather", None),
            ("Gnawed Greaves", "legs", "of the Champion", "Tooth-marks a finger deep.", "plate", None),
            ("Collar of the Bone-Fed", "neck", "of the Bear", "Too big for any dog.", None, None),
        ],
        "The Archmage's Shade": [
            ("Arugal's Last Lesson", "main_hand", "of the Necromancer", "A staff that still remembers the words.", None, "staff"),
            ("Mantle of the Unquiet Mage", "shoulder", "of Shadow Wrath", "Cold to the touch even in summer.", "cloth", None),
            ("Ossuary Warden's Coif", "head", "of the Eagle", "Taken off a guard who never left his post.", "mail", None),
            ("Signet of the Pale Study", "ring", "of the Sorcerer", "Engraved on the inside: 'for my children'.", None, None),
            ("Grave-Cold Cuffs", "wrist", "of the Physician", "They keep a wound from bleeding. They keep a lot of things.", "leather", None),
        ],
    },
)

ZONES["The Lightless Reach"] = dict(
    kind="layer", parent="Blackfathom Deeps", region="Ashenvale West", levels=(29, 31),
    creatures={
        "Reach Myrmidon": ("humanoid_warrior", 29, False, "naga_myrmidon", [
            ("Trident Thrust", "damage", 1.0, 0, "physical", {}),
            ("Coil and Strike", "damage", 1.5, 3, "physical", {}),
            ("Scaled Guard", "buff", 0, 5, "physical", SELF(3, armor=50))]),
        "Lightless Lurker": ("aquatic_basic", 30, False, "tide_lurker", [
            ("Grasp", "damage", 1.0, 0, "physical", {}),
            ("Drag Under", "debuff", 0, 4, "physical", MODS(3, agility=-15, armor=-25)),
            ("Brine Rot", "dot", 0.35, 3, "magic", D(3))]),
        "Twilight Drowner": ("humanoid_caster", 30, False, "twilight_cultist", [
            ("Drowning Word", "damage", 1.0, 0, "magic", {}),
            ("Lungs Full of Water", "dot", 0.45, 3, "magic", D(3)),
            ("Hymn to the Old Ones", "heal", 1.5, 4, "magic", {})]),
        "Ul'gotha, Mother of the Deep": ("aquatic_basic", 31, True, "tentacle_horror", [
            ("Crushing Coil", "damage", 1.0, 0, "physical", {}),
            ("Pull Into the Dark", "debuff", 0, 4, "magic", MODS(3, agility=-25, armor=-50)),
            ("Ink of the Abyss", "dot", 0.5, 3, "magic", D(4)),
            ("Hardened Mantle", "buff", 0, 5, "physical", SELF(3, armor=90)),
            ("Brood-Call", "damage", 1.7, 4, "magic", {}),
            ("Tidal Crush", "damage", 2.1, 5, "physical", {})]),
    },
    weights={"Reach Myrmidon": 3, "Lightless Lurker": 2, "Twilight Drowner": 2},
    loot={
        "Ul'gotha, Mother of the Deep": [
            ("Ul'gotha's Unblinking Eye", "neck", "of the Void", "It closes when you sleep. Only then.", None, None, "epic"),
            ("Tidecrush Trident", "main_hand", "of the Vanquisher", "Pulled from the mother's mantle, still wet.", None, "polearm"),
            ("Robes of the Lightless Choir", "chest", "of the Invoker", "The drowned sang in these.", "cloth", None),
            ("Deepcoil Spaulders", "shoulder", "of the Hunt", "Shell, ground smooth by water that never saw light.", "mail", None),
            ("Lurker-Skin Gloves", "hands", "of the Assassin", "Cold, slick, and they never slip.", "leather", None),
        ],
    },
)

ZONES["The Blood Pits"] = dict(
    kind="layer", parent="Gurbashi Arena", region="Eastern Kingdoms - Stranglethorn", levels=(38, 40),
    creatures={
        "Pit-Bound Gladiator": ("humanoid_warrior", 38, False, "troll_axe", [
            ("Pit Strike", "damage", 1.0, 0, "physical", {}),
            ("Crowd-Pleaser", "damage", 1.6, 3, "physical", {}),
            ("Blood Up", "buff", 0, 5, "physical", SELF(3, attack_power=40))]),
        "Blood Ravager": ("beast_fast", 38, False, "raptor", [
            ("Rake", "damage", 1.0, 0, "physical", {}),
            ("Disembowel", "dot", 0.4, 3, "physical", D(3)),
            ("Pack Leap", "damage", 1.4, 3, "physical", {})]),
        "Pit Bloodcaller": ("humanoid_caster", 39, False, "troll_witchdoctor", [
            ("Blood Hex", "damage", 1.0, 0, "magic", {}),
            ("Feed the Pit", "heal", 1.4, 4, "magic", {}),
            ("Bleeding Mark", "debuff", 0, 4, "magic", MODS(3, armor=-50, magic_resistance=-20))]),
        "Ja'kesh the Unchained": ("humanoid_warrior", 39, True, "troll_axe", [
            ("Chainbreaker", "damage", 1.0, 0, "physical", {}),
            ("Swing the Shackles", "damage", 1.8, 3, "physical", {}),
            ("Unbowed", "buff", 0, 5, "physical", SELF(3, armor=80, attack_power=30)),
            ("Bloodletting", "dot", 0.5, 3, "physical", D(4)),
            ("Last Man Standing", "heal", 2.0, 6, "physical", {})]),
        "Skrell, Mother of Ravagers": ("beast_large", 40, True, "raptor", [
            ("Mother's Jaws", "damage", 1.0, 0, "physical", {}),
            ("Shred", "dot", 0.5, 3, "physical", D(4)),
            ("Brood Shriek", "debuff", 0, 4, "physical", MODS(3, agility=-30, attack_power=-25)),
            ("Pounce From the Dark", "damage", 2.1, 4, "physical", {}),
            ("Thick Hide", "buff", 0, 5, "physical", SELF(3, armor=90))]),
    },
    weights={"Pit-Bound Gladiator": 3, "Blood Ravager": 3, "Pit Bloodcaller": 2},
    loot={
        "Ja'kesh the Unchained": [
            ("The Broken Chain", "main_hand", "of the Gladiator", "He wore it for forty years and then he didn't.", None, "fist_weapon", "epic"),
            ("Pitfighter's Harness", "chest", "of the Tiger", "Older than the arena above.", "leather", None),
            ("Shacklebreaker Gauntlets", "hands", "of the Juggernaut", "One link still dangles from each wrist.", "plate", None),
            ("Crowd-Roar Band", "ring", "of the Vanquisher", "You can almost hear them.", None, None),
            ("Bloodcaller's Loincloth", "legs", "of the Prophet", "Dyed the colour of the pit floor.", "cloth", None),
        ],
        "Skrell, Mother of Ravagers": [
            ("Skrell's Last Clutch", "neck", "of the Beast", "Three eggs on a cord. They never hatched.", None, None, "epic"),
            ("Ravager-Bone Glaive", "main_hand", "of the Vanquisher", "Her own spine, sharpened.", None, "polearm"),
            ("Mothershell Mantle", "shoulder", "of the Defender", "Plates from her back, and they turn steel.", "mail", None),
            ("Den-Stalker Treads", "feet", "of the Assassin", "You walk softer in them. So did she.", "leather", None),
            ("Pit-Priest's Wraps", "wrist", "of the Invoker", "Wound tight against the heat of the blood-fires.", "cloth", None),
        ],
    },
)

ZONES["The Unwritten Stacks"] = dict(
    kind="layer", parent="The Deep Bloom", region="The Crystalline Underdark", levels=(40, 42),
    creatures={
        "Unbound Folio": ("elemental_caster", 40, False, "elemental_arcane", [
            ("Papercut Gale", "damage", 1.0, 0, "magic", {}),
            ("Overwritten", "debuff", 0, 4, "magic", MODS(3, intellect=-20)),
            ("Ink Bleed", "dot", 0.35, 3, "magic", D(3))]),
        "Stack-Grown Reader": ("beast_large", 41, False, "lattice_grown", [
            ("Shelf-Slam", "damage", 1.0, 0, "physical", {}),
            ("Bound Spine", "buff", 0, 5, "physical", SELF(3, armor=60)),
            ("Spore Bookmark", "dot", 0.35, 3, "magic", D(3))]),
        "Spore Archivist": ("humanoid_caster", 41, False, "spore_cap", [
            ("Catalogue", "damage", 1.0, 0, "magic", {}),
            ("Reshelve", "heal", 1.5, 4, "magic", {}),
            ("Silence in the Stacks", "debuff", 0, 4, "magic", MODS(3, magic_resistance=-30))]),
        "The First Draft": ("elemental_caster", 42, True, "archmage_robed", [
            ("Rewrite", "damage", 1.0, 0, "magic", {}),
            ("Strike the Line", "damage", 2.0, 4, "magic", {}),
            ("Edit for Length", "debuff", 0, 4, "magic", MODS(3, intellect=-25, agility=-20)),
            ("Revised Edition", "heal", 2.0, 5, "magic", {}),
            ("Footnotes", "dot", 0.5, 3, "magic", D(4)),
            ("Hardback", "buff", 0, 6, "magic", SELF(3, armor=80, magic_resistance=60))]),
        "Marginalia": ("undead_caster", 41, True, "wisp", [
            ("Scribble", "damage", 1.0, 0, "magic", {}),
            ("Crossed Out", "debuff", 0, 4, "magic", MODS(3, attack_power=-30, intellect=-20)),
            ("Annotate", "dot", 0.5, 3, "magic", D(4)),
            ("Ibid.", "damage", 1.8, 4, "magic", {})]),
    },
    weights={"Unbound Folio": 3, "Stack-Grown Reader": 2, "Spore Archivist": 2},
    loot={
        "Marginalia": [
            ("Quill of Marginalia", "off_hand", "of the Sorcerer", "It writes on its own if you let it.", None, "tome", "epic"),
            ("Annotated Mantle", "shoulder", "of the Owl", "Notes in a hand nobody recognises cover every inch.", "cloth", None),
            ("Scribe's Fingerless Gloves", "hands", "of the Falcon", "Inkstains that move when you aren't looking.", "leather", None),
            ("Margin-Ruled Bracers", "wrist", "of the Defender", "Straight lines, ruled into steel.", "plate", None),
        ],
        "The First Draft": [
            ("The Unedited Word", "main_hand", "of the Invoker", "A staff of pressed fungus-paper, and whatever it says, it means.", None, "staff", "epic"),
            ("Bound Volume Breastplate", "chest", "of the Champion", "Pages hammered flat into plate. Some of them are still legible.", "plate", None),
            ("Archivist's Spore-Hood", "head", "of the Physician", "Grows back if you cut it.", "mail", None),
            ("Errata Loop", "ring", "of the Assassin", "Corrected. Then corrected again.", None, None),
            ("Stackwalker's Slippers", "feet", "of the Wellspring", "Made for long nights between the shelves.", "cloth", None),
        ],
    },
)


# ============================================================================ SKULL ZONES
def _skull_table(zone, open_w, subs):
    """An encounter table for an open map: the open ground and each named part of it."""
    def f(_table):
        return {"open_zone": {"name": zone, "creatures": open_w},
                "subzones": {k: {"name": k, "creatures": v} for k, v in subs.items()}}
    return f


ZONES["The Saltgrave"] = dict(
    kind="skull", parent="Arathi East", levels=(38, 41),
    creatures={
        "Brine-Wight": ("undead_warrior", 39, False, "revenant", [
            ("Barrow Blade", "damage", 1.0, 0, "physical", {}),
            ("Grave-Salt", "debuff", 0, 4, "magic", MODS(3, armor=-40)),
            ("Old Oath", "buff", 0, 5, "physical", SELF(3, armor=50))]),
        "Drowned Barrow-Thane": ("undead_warrior", 40, False, "drowned_sailor", [
            ("Thane's Axe", "damage", 1.05, 0, "physical", {}),
            ("Cleave the Line", "damage", 1.5, 3, "physical", {}),
            ("Waterlogged Grip", "dot", 0.35, 3, "physical", D(3))]),
        "Barrow Lantern": ("undead_caster", 39, False, "wisp", [
            ("Corpse-Light", "damage", 1.0, 0, "magic", {}),
            ("Lead Astray", "debuff", 0, 4, "magic", MODS(3, agility=-18, intellect=-12)),
            ("Cold Flame", "dot", 0.4, 3, "magic", D(3))]),
        "Saltgrave Crab": ("beast_large", 38, False, "crab_giant", [
            ("Crush", "damage", 1.0, 0, "physical", {}),
            ("Shell Up", "buff", 0, 5, "physical", SELF(3, armor=70))]),
        "Gravegull": ("beast_fast", 38, False, "vulture", [
            ("Peck", "damage", 0.9, 0, "physical", {}),
            ("Eye-Raker", "debuff", 0, 4, "physical", MODS(3, agility=-14)),
            ("Carrion Dive", "damage", 1.4, 3, "physical", {})]),
        "The Brine King": ("undead_warrior", 41, True, "revenant", [
            ("Crown of Salt", "damage", 1.0, 0, "physical", {}),
            ("Call the Barrow-Host", "buff", 0, 5, "magic", SELF(3, attack_power=50, armor=60)),
            ("Tide of the Dead", "damage", 1.8, 3, "magic", {}),
            ("King's Grief", "debuff", 0, 4, "magic", MODS(3, attack_power=-35, intellect=-25)),
            ("Brine-Rot", "dot", 0.5, 3, "magic", D(4))]),
    },
    encounters=_skull_table("The Saltgrave", {"Saltgrave Crab": 3, "Gravegull": 2}, {
        "The Landing Bar": {"Saltgrave Crab": 3, "Gravegull": 2},
        "The West Barrow": {"Brine-Wight": 3, "Barrow Lantern": 2, "Gravegull": 1},
        "The East Barrow": {"Brine-Wight": 2, "Drowned Barrow-Thane": 2, "Barrow Lantern": 1},
        "The Middle Bar": {"Saltgrave Crab": 2, "Gravegull": 2, "Brine-Wight": 1, "Gullmother Shrike": 0},
        "The King's Barrow": {"Drowned Barrow-Thane": 3, "Brine-Wight": 2, "Barrow Lantern": 2, "The Brine King": 0}}),
    weights={},
    loot={
        "The Brine King": [
            ("Crown of the Drowned Thane", "head", "of the Champion", "Salt-crusted gold. It still fits somebody.", "plate", None, "epic"),
            ("Barrow-King's Bane", "main_hand", "of the Vanquisher", "Buried with him so nobody else could have it.", None, "sword_2h"),
            ("Saltgrave Shroud", "back", "of the Eagle", "Grey wool, and never once dry.", None, None),
            ("Lantern-Keeper's Wraps", "wrist", "of the Invoker", "Warm, which is the strangest thing about them.", "cloth", None),
            ("Tidewalker's Treads", "feet", "of the Monkey", "Sand runs out of them forever.", "leather", None),
        ],
    },
)

ZONES["The Glasswaste"] = dict(
    kind="skull", parent="Durotar", levels=(15, 18),
    creatures={
        "Glassback Basilisk": ("beast_large", 16, False, "basilisk", [
            ("Glass Bite", "damage", 1.0, 0, "physical", {}),
            ("Crystal Gaze", "debuff", 0, 4, "magic", MODS(3, agility=-10, armor=-20)),
            ("Shard-Hide", "buff", 0, 5, "physical", SELF(3, armor=40))]),
        "Kiln-Walker": ("elemental_bruiser", 17, False, "elemental_fire", [
            ("Furnace Fist", "damage", 1.05, 0, "magic", {}),
            ("Scald", "dot", 0.4, 3, "magic", D(3)),
            ("Heat Haze", "debuff", 0, 4, "magic", MODS(3, intellect=-8))]),
        "Glasswing Wasp": ("vermin_swarm", 15, False, "wasp", [
            ("Sting", "damage", 0.9, 0, "physical", {}),
            ("Burning Venom", "dot", 0.35, 3, "magic", D(3))]),
        "Ash Hyena": ("beast_fast", 15, False, "hyena", [
            ("Snap", "damage", 0.95, 0, "physical", {}),
            ("Cackle", "debuff", 0, 4, "physical", MODS(3, attack_power=-8)),
            ("Hamstring", "damage", 1.3, 3, "physical", {})]),
        "Old Blister": ("beast_large", 18, True, "basilisk", [
            ("Molten Jaws", "damage", 1.0, 0, "physical", {}),
            ("Glassing Stare", "debuff", 0, 4, "magic", MODS(3, agility=-20, armor=-40)),
            ("Blister Burst", "dot", 0.5, 3, "magic", D(4)),
            ("Fused Hide", "buff", 0, 5, "physical", SELF(3, armor=60)),
            ("Spit Glass", "damage", 1.8, 4, "physical", {})]),
    },
    encounters=_skull_table("The Glasswaste", {"Ash Hyena": 3, "Glasswing Wasp": 2}, {
        "The Scorched Mouth": {"Ash Hyena": 3, "Glasswing Wasp": 2, "Cindermaw": 0},
        "The Shard Fields": {"Glassback Basilisk": 3, "Glasswing Wasp": 2, "Ash Hyena": 1},
        "The Kiln Rise": {"Kiln-Walker": 3, "Glassback Basilisk": 1, "Glasswing Wasp": 1},
        "Blister's Hollow": {"Glassback Basilisk": 2, "Kiln-Walker": 2, "Old Blister": 0}}),
    weights={},
    loot={
        "Old Blister": [
            ("Blister's Fused Fang", "main_hand", "of the Tiger", "Half tooth, half glass. Sharper than either.", None, "dagger"),
            ("Glasswalker's Jerkin", "chest", "of the Monkey", "Basilisk hide that turns a blade.", "leather", None),
            ("Kiln-Fired Gauntlets", "hands", "of the Bear", "Hammered out on a hot stone in the canyon.", "plate", None),
            ("Shard of the Glasswaste", "neck", "of the Sorcerer", "It holds the heat of a fire nobody lit.", None, None),
            ("Ashfoot's Hauberk", "chest", "of the Hunt", "Durek's old mail, from before he stopped going out.", "mail", None),
        ],
    },
)

ZONES["The Weeping Pines"] = dict(
    kind="skull", parent="The Sepulcher", levels=(17, 20),
    creatures={
        "Weeping Worgen": ("humanoid_warrior", 18, False, "worgen", [
            ("Grieving Claw", "damage", 1.0, 0, "physical", {}),
            ("Howl at Nothing", "buff", 0, 5, "physical", SELF(3, attack_power=18)),
            ("Tear", "dot", 0.35, 3, "physical", D(3))]),
        "Mere Wraith": ("undead_caster", 19, False, "wraith_pale", [
            ("Drowned Touch", "damage", 1.0, 0, "magic", {}),
            ("What the Water Remembers", "debuff", 0, 4, "magic", MODS(3, intellect=-10, magic_resistance=-15)),
            ("Mere-Chill", "dot", 0.4, 3, "magic", D(3))]),
        "Gloom Spider": ("beast_fast", 17, False, "spider", [
            ("Bite", "damage", 0.95, 0, "physical", {}),
            ("Webbed", "debuff", 0, 4, "physical", MODS(3, agility=-12)),
            ("Gloom Venom", "dot", 0.35, 3, "magic", D(3))]),
        "Rotbark Treant": ("beast_large", 19, False, "treant", [
            ("Rotten Branch", "damage", 1.05, 0, "physical", {}),
            ("Barkskin", "buff", 0, 5, "physical", SELF(3, armor=50)),
            ("Spore Burst", "dot", 0.35, 3, "magic", D(3))]),
        "The Widow of the Mere": ("undead_caster", 20, True, "banshee", [
            ("Keening", "damage", 1.0, 0, "magic", {}),
            ("She Calls Your Name", "debuff", 0, 4, "magic", MODS(3, intellect=-20, agility=-15)),
            ("Black Water", "dot", 0.5, 3, "magic", D(4)),
            ("Veil of Fog", "buff", 0, 5, "magic", SELF(3, armor=50, magic_resistance=50)),
            ("Wail", "damage", 1.9, 4, "magic", {})]),
    },
    encounters=_skull_table("The Weeping Pines", {"Gloom Spider": 3, "Weeping Worgen": 2}, {
        "The Fogbound Track": {"Gloom Spider": 3, "Weeping Worgen": 2},
        "The Hanging Wood": {"Gloom Spider": 3, "Rotbark Treant": 2},
        "The Weeping Mere": {"Mere Wraith": 3, "Weeping Worgen": 2, "The Widow of the Mere": 0},
        "The Stillwater Shrine": {"Mere Wraith": 2, "Weeping Worgen": 2},
        "The Drowned Copse": {"Rotbark Treant": 3, "Mere Wraith": 1, "Old Hollowbark": 0}}),
    weights={},
    loot={
        "The Widow of the Mere": [
            ("Veil of the Weeping Widow", "head", "of the Owl", "Black lace, soaked through and never dripping.", "cloth", None),
            ("Mere-Drowned Longbow", "ranged", "of the Hunt", "Strung with something that isn't gut.", None, "bow"),
            ("Mourning Band", "ring", "of the Physician", "Inside it says 'until the water's still'.", None, None),
            ("Pinewalker's Leggings", "legs", "of the Wolf", "They make no noise at all.", "leather", None),
            ("Stillwater Girdle", "waist", "of the Champion", "Rusted, and stronger for it.", "plate", None),
        ],
    },
)


# ================================================================ THE TANGLEWOOD AND ITS ROOT
ZONES["The Tanglewood Shoals"] = dict(
    kind="skull", parent="Echo Isles", levels=(14, 17),
    creatures={
        "Mangrove Snapper": ("beast_large", 15, False, "crocolisk", [
            ("Snap", "damage", 1.0, 0, "physical", {}),
            ("Death Roll", "damage", 1.5, 3, "physical", {}),
            ("Thick Scales", "buff", 0, 5, "physical", SELF(3, armor=40))]),
        "Shoal Stalker": ("beast_fast", 15, False, "panther", [
            ("Rake", "damage", 1.0, 0, "physical", {}),
            ("Pounce", "damage", 1.4, 3, "physical", {}),
            ("Bleeding Claws", "dot", 0.3, 3, "physical", D(3))]),
        "Tangle Lurker": ("beast_basic", 16, False, "vine_strangler", [
            ("Lash", "damage", 1.0, 0, "physical", {}),
            ("Root Snare", "debuff", 0, 4, "physical", MODS(3, agility=-10)),
            ("Sap Burn", "dot", 0.35, 3, "magic", D(3))]),
        "Rootbound Guardian": ("beast_large", 16, False, "treant", [
            ("Branch Slam", "damage", 1.05, 0, "physical", {}),
            ("Bark Up", "buff", 0, 5, "physical", SELF(3, armor=45)),
            ("Spore Puff", "debuff", 0, 4, "magic", MODS(3, intellect=-8))]),
        "Glimmerwing Darter": ("vermin_swarm", 14, False, "sprite_darter", [
            ("Glimmer Bolt", "damage", 0.9, 0, "magic", {}),
            ("Dazzle", "debuff", 0, 4, "magic", MODS(3, agility=-8, intellect=-6))]),
        "Grandfather Mangrove": ("beast_large", 17, True, "treant", [
            ("Old Wood", "damage", 1.0, 0, "physical", {}),
            ("Drown the Roots", "dot", 0.5, 3, "magic", D(4)),
            ("Strangling Vines", "debuff", 0, 4, "physical", MODS(3, agility=-18, armor=-30)),
            ("Ironbark", "buff", 0, 5, "physical", SELF(3, armor=70)),
            ("Fall of a Great Bough", "damage", 1.9, 4, "physical", {})]),
        "Old Snag-Jaw": ("beast_large", 16, True, "crocolisk", [
            ("Snag", "damage", 1.0, 0, "physical", {}),
            ("Pull Under", "debuff", 0, 4, "physical", MODS(3, agility=-14)),
            ("Gnash", "dot", 0.45, 3, "physical", D(3)),
            ("Lunge", "damage", 1.7, 4, "physical", {})]),
    },
    encounters=_skull_table("The Tanglewood Shoals", {"Mangrove Snapper": 2, "Glimmerwing Darter": 2}, {
        "The Mangrove Landing": {"Mangrove Snapper": 3, "Glimmerwing Darter": 2, "Old Snag-Jaw": 0},
        "The Rootward Isle": {"Rootbound Guardian": 3, "Tangle Lurker": 2, "Shoal Stalker": 1, "Grandfather Mangrove": 0},
        "The West Tangle": {"Tangle Lurker": 3, "Shoal Stalker": 2},
        "The East Tangle": {"Shoal Stalker": 3, "Glimmerwing Darter": 2},
        "The Northern Shoals": {"Mangrove Snapper": 2, "Rootbound Guardian": 2, "Glimmerwing Darter": 1}}),
    weights={},
    loot={
        "Grandfather Mangrove": [
            ("Mangrove-Heart Staff", "main_hand", "of the Prophet", "A living branch. It still puts out leaves in spring.", None, "staff"),
            ("Barkweave Jerkin", "chest", "of the Monkey", "Grown, not stitched.", "leather", None),
            ("Shoalwalker Boots", "feet", "of the Bear", "They grip wet roots like they were made for it.", "mail", None),
            ("Seed of the Old Wood", "neck", "of the Owl", "It's warm, and it's growing. Slowly.", None, None),
        ],
        "Old Snag-Jaw": [
            ("Snag-Tooth Dagger", "main_hand", "of the Tiger", "One of his teeth. He has plenty more.", None, "dagger"),
            ("Crocscale Bracers", "wrist", "of the Champion", "Tough enough to turn a bite.", "mail", None),
            ("Swamp-Lurker's Cord", "waist", "of the Eagle", "Smells of the shallows forever.", "cloth", None),
        ],
    },
)

ZONES["The World-Root Hollow"] = dict(
    kind="frontier", frontier_type="deep", parent="The Tanglewood Shoals", region="The Tanglewood Shoals",
    levels=(18, 20),
    creatures={
        "Hollow Rootling": ("beast_basic", 18, False, "sapling_thorn", [
            ("Thorn Jab", "damage", 1.0, 0, "physical", {}),
            ("Sap Spit", "dot", 0.35, 3, "magic", D(3)),
            ("Root Down", "buff", 0, 5, "physical", SELF(3, armor=40))]),
        "Sapdrunk Bat": ("beast_fast", 18, False, "bat", [
            ("Bite", "damage", 0.95, 0, "physical", {}),
            ("Amber Shriek", "debuff", 0, 4, "magic", MODS(3, intellect=-10, agility=-8)),
            ("Drain", "heal", 1.2, 4, "physical", {})]),
        "Heartwood Spider": ("beast_fast", 19, False, "spider", [
            ("Fang", "damage", 1.0, 0, "physical", {}),
            ("Amber Web", "debuff", 0, 4, "physical", MODS(3, agility=-16)),
            ("Sapvenom", "dot", 0.4, 3, "magic", D(3))]),
        "Lost Rootspeaker": ("humanoid_caster", 19, False, "troll_witchdoctor", [
            ("Root-Hex", "damage", 1.0, 0, "magic", {}),
            ("The Tree Answers", "heal", 1.5, 4, "magic", {}),
            ("Thorn Ward", "buff", 0, 5, "magic", SELF(3, armor=40, magic_resistance=30)),
            ("Grasping Roots", "debuff", 0, 4, "magic", MODS(3, agility=-14))]),
        "Gnarl the Unburied": ("beast_large", 19, True, "treant", [
            ("Gnarled Fist", "damage", 1.0, 0, "physical", {}),
            ("Unburied", "heal", 1.8, 5, "physical", {}),
            ("Splinter Storm", "dot", 0.45, 3, "physical", D(3)),
            ("Bark Shell", "buff", 0, 5, "physical", SELF(3, armor=60))]),
        "Amberheart, the Sap-Mother": ("elemental_caster", 20, True, "elemental_earth", [
            ("Amber Lance", "damage", 1.0, 0, "magic", {}),
            ("Entomb in Amber", "debuff", 0, 4, "magic", MODS(3, agility=-25, armor=-40)),
            ("Sapflood", "dot", 0.5, 3, "magic", D(4)),
            ("Harden", "buff", 0, 5, "magic", SELF(3, armor=70, magic_resistance=50)),
            ("Mother's Tears", "heal", 2.0, 5, "magic", {}),
            ("Burst of Sap", "damage", 1.9, 4, "magic", {})]),
        "The Root-Father": ("beast_large", 21, True, "treant", [
            ("Root of the World", "damage", 1.0, 0, "physical", {}),
            ("The Tree Wakes", "buff", 0, 5, "physical", SELF(3, attack_power=40, armor=80)),
            ("Crushing Roots", "damage", 2.1, 4, "physical", {}),
            ("Strangle", "dot", 0.55, 3, "physical", D(4)),
            ("Old as the Isles", "debuff", 0, 4, "magic", MODS(3, attack_power=-30, intellect=-25, agility=-20)),
            ("Drink the Deep Water", "heal", 2.2, 6, "magic", {})]),
    },
    weights={"Hollow Rootling": 3, "Sapdrunk Bat": 2, "Heartwood Spider": 2, "Lost Rootspeaker": 2},
    loot={
        "Gnarl the Unburied": [
            ("Gnarlwood Bludgeon", "main_hand", "of the Bear", "Pulled out of him. He didn't miss it.", None, "mace_2h", "epic"),
            ("Unburied Mantle", "shoulder", "of the Wolf", "Moss grows on it even in a bag.", "leather", None),
            ("Rootknot Ring", "ring", "of the Physician", "A ring of living root. It tightens when you're hurt.", None, None),
        ],
        "Amberheart, the Sap-Mother": [
            ("Tear of the Sap-Mother", "neck", "of the Invoker", "A drop of amber with a flower in it that hasn't grown anywhere for ten thousand years.", None, None, "epic"),
            ("Amber-Sealed Aegis", "off_hand", None, "A shield with a beetle in it the size of your hand. It's still alive.", None, "shield", "epic"),
            ("Sapweave Robes", "chest", "of the Sorcerer", "Sticky. Worth it.", "cloth", None),
            ("Amberplate Greaves", "legs", "of the Champion", "Plate set in amber, and the amber doesn't crack.", "plate", None),
            ("Heartwood Grips", "hands", "of the Assassin", "Carved from the inside of the tree.", "leather", None),
        ],
        "The Root-Father": [
            ("World-Root", "main_hand", "of the Invoker", "A staff cut from the root of the oldest tree in the world. It cut back.", None, "staff", "epic"),
            ("Root-Father's Reach", "main_hand", "of the Vanquisher", "A spear of root as hard as iron and twice as patient.", None, "polearm", "epic"),
            ("Bark of the First Tree", "chest", "of the Defender", "Armour that grows back.", "plate", None, "epic"),
            ("Crown of Living Wood", "head", "of the Prophet", "Small white flowers open on it at dawn.", "cloth", None),
            ("Treewalker's Hauberk", "chest", "of the Hunt", "Rings of bark, linked like mail.", "mail", None),
            ("Hollow-Stalker Leggings", "legs", "of the Monkey", "You don't make a sound in them.", "leather", None),
        ],
    },
)

ZONES["The Drowned Idols"] = dict(
    kind="skull", parent="Northern Stranglethorn", levels=(33, 36),
    creatures={
        "Idol-Drowned Troll": ("undead_warrior", 34, False, "zombie", [
            ("Waterlogged Axe", "damage", 1.0, 0, "physical", {}),
            ("Dead God's Hymn", "buff", 0, 5, "magic", SELF(3, attack_power=30)),
            ("Silt in the Lungs", "dot", 0.35, 3, "physical", D(3))]),
        "Drowned Hexer": ("undead_caster", 35, False, "troll_witchdoctor", [
            ("Hex of the Deep", "damage", 1.0, 0, "magic", {}),
            ("Curse of the Old Gods", "debuff", 0, 4, "magic", MODS(3, magic_resistance=-25, intellect=-15)),
            ("Mend the Dead", "heal", 1.5, 4, "magic", {})]),
        "Lagoon Crocolisk": ("beast_large", 33, False, "crocolisk", [
            ("Jaws", "damage", 1.0, 0, "physical", {}),
            ("Death Roll", "damage", 1.5, 3, "physical", {}),
            ("Mud Hide", "buff", 0, 5, "physical", SELF(3, armor=50))]),
        "Jade Serpent": ("beast_fast", 34, False, "serpent", [
            ("Fang", "damage", 1.0, 0, "physical", {}),
            ("Jade Venom", "dot", 0.4, 3, "magic", D(3)),
            ("Hypnotic Sway", "debuff", 0, 4, "magic", MODS(3, agility=-16))]),
        "Mire Gorilla": ("beast_large", 35, False, "gorilla", [
            ("Pound", "damage", 1.05, 0, "physical", {}),
            ("Chest Beat", "buff", 0, 5, "physical", SELF(3, attack_power=35)),
            ("Hurl Mud", "debuff", 0, 4, "physical", MODS(3, agility=-14))]),
        "Idol-Keeper Zun'jal": ("undead_caster", 36, True, "troll_witchdoctor", [
            ("Word of the Drowned God", "damage", 1.0, 0, "magic", {}),
            ("The God Looks At You", "debuff", 0, 4, "magic", MODS(3, intellect=-25, armor=-50)),
            ("Tide of Hexes", "dot", 0.5, 3, "magic", D(4)),
            ("Idol's Ward", "buff", 0, 5, "magic", SELF(3, armor=60, magic_resistance=60)),
            ("Offering", "heal", 2.0, 5, "magic", {}),
            ("Wrath of the Forgotten", "damage", 1.9, 4, "magic", {})]),
        "Mother Mire": ("beast_large", 35, True, "gorilla", [
            ("Crushing Grip", "damage", 1.0, 0, "physical", {}),
            ("Protect the Young", "buff", 0, 5, "physical", SELF(3, armor=60, attack_power=30)),
            ("Ground Slam", "damage", 1.8, 4, "physical", {}),
            ("Roar", "debuff", 0, 4, "physical", MODS(3, attack_power=-25))]),
    },
    encounters=_skull_table("The Drowned Idols", {"Lagoon Crocolisk": 3, "Jade Serpent": 2}, {
        "The Idol Landing": {"Lagoon Crocolisk": 3, "Jade Serpent": 2},
        "The Western Idols": {"Idol-Drowned Troll": 3, "Drowned Hexer": 2, "Mire Gorilla": 1},
        "The Eastern Idols": {"Idol-Drowned Troll": 2, "Drowned Hexer": 2, "Jade Serpent": 1},
        "The Sunken Altar": {"Drowned Hexer": 2, "Idol-Drowned Troll": 2, "Lagoon Crocolisk": 1},
        "The Jade Isles": {"Mire Gorilla": 3, "Jade Serpent": 2, "Mother Mire": 0},
        "The Last God's Isle": {"Drowned Hexer": 3, "Idol-Drowned Troll": 2, "Idol-Keeper Zun'jal": 0}}),
    weights={},
    loot={
        "Idol-Keeper Zun'jal": [
            ("Eye of the Drowned God", "neck", "of the Void", "A jade eye on a cord of hair. It blinks.", None, None, "epic"),
            ("Zun'jal's Hexing Rod", "main_hand", "of the Necromancer", "Carved from an idol's finger.", None, "wand"),
            ("Waterlogged Ritual Robes", "chest", "of the Prophet", "They never dry, and they never rot.", "cloth", None),
            ("Idol-Breaker's Pauldrons", "shoulder", "of the Champion", "Hammered from the bronze of a drowned god.", "plate", None),
            ("Lagoon-Stalker's Boots", "feet", "of the Assassin", "Silent on wet stone.", "leather", None),
        ],
        "Mother Mire": [
            ("Mire-Mother's Knuckles", "main_hand", "of the Tiger", "Big enough for her. They'll do for you.", None, "fist_weapon"),
            ("Silverback Mantle", "shoulder", "of the Beast", "Grey fur over hard hide.", "mail", None),
            ("Mudslick Gloves", "hands", "of the Eagle", "You'll never drop anything again.", "cloth", None),
        ],
    },
)

ZONES["The Buried Caravan"] = dict(
    kind="skull", parent="Northern Tanaris", levels=(44, 47),
    creatures={
        "Dune Revenant": ("undead_warrior", 45, False, "revenant", [
            ("Sand-Scoured Blade", "damage", 1.0, 0, "physical", {}),
            ("Still Owed", "debuff", 0, 4, "magic", MODS(3, armor=-50)),
            ("Grit Storm", "dot", 0.35, 3, "physical", D(3))]),
        "Sandscour Scorpid": ("beast_large", 44, False, "scorpion", [
            ("Pincer", "damage", 1.0, 0, "physical", {}),
            ("Sting", "dot", 0.4, 3, "magic", D(3)),
            ("Carapace", "buff", 0, 5, "physical", SELF(3, armor=60))]),
        "Caravan Ghoul": ("undead_basic", 45, False, "ghoul", [
            ("Claw", "damage", 1.0, 0, "physical", {}),
            ("Hunger of the Lost", "buff", 0, 5, "physical", SELF(3, attack_power=35)),
            ("Rot", "dot", 0.35, 3, "physical", D(3))]),
        "Sandstone Colossus": ("elemental_bruiser", 46, False, "mountain_giant_sandstone", [
            ("Boulder Fist", "damage", 1.1, 0, "physical", {}),
            ("Quake", "damage", 1.5, 4, "physical", {}),
            ("Stone Skin", "buff", 0, 5, "physical", SELF(3, armor=90))]),
        "The Last Caravan Master": ("undead_warrior", 47, True, "revenant", [
            ("Ledger Blade", "damage", 1.0, 0, "physical", {}),
            ("Call the Teamsters", "buff", 0, 5, "magic", SELF(3, attack_power=60, armor=60)),
            ("Buried Alive", "debuff", 0, 4, "magic", MODS(3, agility=-30, armor=-60)),
            ("Sandstorm", "dot", 0.55, 3, "physical", D(4)),
            ("Collect the Debt", "damage", 2.0, 4, "physical", {})]),
        "Old Stinger": ("beast_large", 46, True, "scorpion", [
            ("Great Pincer", "damage", 1.0, 0, "physical", {}),
            ("Paralysing Sting", "debuff", 0, 4, "magic", MODS(3, agility=-30)),
            ("Venom Pool", "dot", 0.5, 3, "magic", D(4)),
            ("Old Shell", "buff", 0, 5, "physical", SELF(3, armor=80))]),
    },
    encounters=_skull_table("The Buried Caravan", {"Sandscour Scorpid": 3, "Dune Revenant": 1}, {
        "The Last Dune": {"Sandscour Scorpid": 3, "Caravan Ghoul": 1},
        "The Wagon Graves": {"Caravan Ghoul": 3, "Dune Revenant": 2, "Old Stinger": 0},
        "The Drowned Market": {"Dune Revenant": 3, "Caravan Ghoul": 2},
        "The Buried Gate": {"Sandstone Colossus": 2, "Dune Revenant": 2, "Sandscour Scorpid": 1},
        "The Caravan Master's Rest": {"Dune Revenant": 3, "Sandstone Colossus": 1, "The Last Caravan Master": 0}}),
    weights={},
    loot={
        "The Last Caravan Master": [
            ("The Master's Ledger", "off_hand", "of the Sorcerer", "Every debt ever owed this caravan, in a hand that never shook.", None, "tome", "epic"),
            ("Caravan-Breaker", "main_hand", "of the Gladiator", "A wagon axle, sharpened. He wasn't picky.", None, "axe_2h", "epic"),
            ("Dune-Buried Breastplate", "chest", "of the Defender", "Sand pours out of it for a week.", "plate", None),
            ("Teamster's Duster", "chest", "of the Hunt", "Sun-faded, sand-scoured, still waterproof.", "mail", None),
            ("Silk of the Lost Market", "legs", "of the Invoker", "The finest thing the caravan carried.", "cloth", None),
        ],
        "Old Stinger": [
            ("Stinger's Barb", "main_hand", "of the Assassin", "Still wet at the tip. Don't lick it.", None, "dagger"),
            ("Chitin Pauldrons", "shoulder", "of the Juggernaut", "Plates off the oldest scorpid in the desert.", "plate", None),
            ("Sand-Shed Wraps", "wrist", "of the Owl", "Light as a moult.", "cloth", None),
        ],
    },
)


# a rare of its own for each of the other open hidden maps (Kyle: "even rares >;)")
ZONES["The Saltgrave"]["creatures"]["Gullmother Shrike"] = ("beast_fast", 39, True, "vulture", [
    ("Rending Beak", "damage", 1.0, 0, "physical", {}),
    ("Flock", "dot", 0.45, 3, "physical", D(3)),
    ("Shriek", "debuff", 0, 4, "physical", MODS(3, agility=-20)),
    ("Stoop", "damage", 1.8, 4, "physical", {})])
ZONES["The Saltgrave"]["loot"]["Gullmother Shrike"] = [
    ("Shrike-Feather Cloak", "back", "of the Falcon", "Grey and white, and it moves in a wind you can't feel.", None, None),
    ("Talon-Hook Knife", "main_hand", "of the Assassin", "One of her claws, fitted with a grip.", None, "dagger"),
    ("Gull-Bone Wristguards", "wrist", "of the Bear", "Light as anything and harder than they look.", "plate", None),
]
ZONES["The Glasswaste"]["creatures"]["Cindermaw"] = ("beast_fast", 17, True, "hyena", [
    ("Burning Bite", "damage", 1.0, 0, "physical", {}),
    ("Laugh of the Pack", "buff", 0, 5, "physical", SELF(3, attack_power=25)),
    ("Ember Mange", "dot", 0.45, 3, "magic", D(3)),
    ("Tear Out", "damage", 1.7, 4, "physical", {})])
ZONES["The Glasswaste"]["loot"]["Cindermaw"] = [
    ("Cindermaw Fang Necklace", "neck", "of the Tiger", "Still smells of smoke.", None, None),
    ("Scorchhide Leggings", "legs", "of the Monkey", "Singed, but they hold.", "leather", None),
    ("Ember-Sworn Wraps", "wrist", "of the Sorcerer", "Warm whatever the weather.", "cloth", None),
]
ZONES["The Weeping Pines"]["creatures"]["Old Hollowbark"] = ("beast_large", 19, True, "treant", [
    ("Rotten Swing", "damage", 1.0, 0, "physical", {}),
    ("Hollow Moan", "debuff", 0, 4, "magic", MODS(3, intellect=-15, attack_power=-15)),
    ("Spore Cloud", "dot", 0.45, 3, "magic", D(3)),
    ("Petrify Bark", "buff", 0, 5, "physical", SELF(3, armor=60))])
ZONES["The Weeping Pines"]["loot"]["Old Hollowbark"] = [
    ("Hollowbark Shield", "off_hand", None, "Cut from his chest. He's hollow there anyway.", None, "shield"),
    ("Pinesap Gloves", "hands", "of the Owl", "Sticky with something that smells like rain.", "cloth", None),
    ("Mosswalker Boots", "feet", "of the Hunt", "Soft soled, made for dead ground.", "mail", None),
]


# =============================================================================== THE PEOPLE
# One person in each open hidden map, and three or four things they need doing; the last is an
# elite job. Kyle: "max of like 3 or 4....they're not quest hubs but they CAN have elite quests."
NPCS = {
    "hz_saltgrave_maud": dict(name="Maud Saltpenny", zone="The Saltgrave", race="human", gender="female",
                              greeting="You came out past the last island on purpose? Then you're either a "
                                       "fool or a beachcomber, and I'm both. Sit down before the gulls see you."),
    "hz_glasswaste_durek": dict(name="Durek Ashfoot", zone="The Glasswaste", race="orc", gender="male",
                                greeting="Nobody walks in here by accident. I didn't. I came for the glass and "
                                         "the glass kept me. Don't touch anything that's still glowing."),
    "hz_tangle_kojira": dict(name="Koji'ra", zone="The Tanglewood Shoals", race="troll", gender="female",
                             greeting="You found the way out here. Then the isles let you. They don't let many."),
    "hz_idols_fizzle": dict(name="Fizzle Brassgut", zone="The Drowned Idols", race="goblin", gender="male",
                            greeting="Shh! Keep your voice down, the gods are napping. Probably. Want to get rich?"),
    "hz_caravan_rizzo": dict(name="Rizzo Dustwhistle", zone="The Buried Caravan", race="goblin", gender="female",
                             greeting="My great-great-grandmother's caravan is under this sand somewhere. So's her money."),
    "hz_pines_ilsabet": dict(name="Ilsabet Graves", zone="The Weeping Pines", race="forsaken", gender="female",
                             greeting="Keep your voice down. The water listens, and when it hears a living "
                                      "voice it starts to cry."),
}

#: quest item drops: creature -> (item id, name, description, chance)
DROPS = {
    "Brine-Wight": ("barrow_coin", "Barrow Coin", "Old gold, green with salt, stamped with a king nobody remembers.", 0.6),
    "Drowned Barrow-Thane": ("barrow_coin", "Barrow Coin", "Old gold, green with salt, stamped with a king nobody remembers.", 0.6),
    "Glassback Basilisk": ("fused_glass_shard", "Fused Glass Shard", "A splinter of the canyon's glass, pulled from a basilisk's back. Still warm.", 0.7),
    "Rootbound Guardian": ("glowing_sap", "Glowing Sap", "Amber sap that gives off its own light. It's warm, like something's alive in it.", 0.65),
    "Idol-Drowned Troll": ("jade_idol_shard", "Jade Idol Shard", "A chip of green stone off a drowned god. It's cold, and it hums.", 0.6),
    "Drowned Hexer": ("jade_idol_shard", "Jade Idol Shard", "A chip of green stone off a drowned god. It's cold, and it hums.", 0.6),
    "Dune Revenant": ("caravan_manifest_page", "Caravan Manifest Page", "A page from a ledger, sand-scoured, every line a debt.", 0.6),
    "Mere Wraith": ("vial_of_mere_water", "Vial of Mere-Water", "Black water that doesn't settle. It moves a little when you aren't holding it still.", 0.65),
}


def Q(qid, title, giver, zone, lvl, objectives, desc, accept, turn_in, rewards, nxt=None, elite=False):
    exp = int(95 * lvl * (2.0 if elite else 1.15))
    gold = int(380 * lvl * (2.0 if elite else 1.1))
    return {"quest_id": qid, "title": title + (" (Elite)" if elite else ""), "giver_npc_id": giver,
            "zone": zone, "level_min": lvl, "level_max": lvl + 2, "elite": elite, "description": desc,
            "objectives": objectives, "reward_exp": exp, "reward_gold": gold, "accept_text": accept,
            "turn_in_text": turn_in, "unique_item_defs": rewards, "next_quest_id": nxt}


def R(lvl, *items):
    out = []
    for (name, slot, suffix, armor, weapon, label) in items:
        kw = {}
        if armor:
            kw["armor_type"] = armor
        if weapon:
            kw["weapon_type"] = weapon
        d = make(name, slot, suffix, lvl + 4, "", rarity="rare", req=lvl, **kw)
        d.pop("flavor_text", None)
        d["label"] = label
        out.append(d)
    return out


def quests():
    sz, gw, wp, tw = "the_saltgrave", "the_glasswaste", "the_weeping_pines", "the_tanglewood_shoals"
    di, bc = "the_drowned_idols", "the_buried_caravan"
    return [
        # ------------------------------------------------------------------ The Saltgrave
        Q("hz_saltgrave_coins", "Grave-Gold", "hz_saltgrave_maud", sz, 38,
          [{"type": "fetch", "target": "barrow_coin", "count": 8}],
          "I'm Maud. I comb this sand for a living, and the living's been thin since the barrows "
          "opened.\n\nThe dead out here were buried with their gold, and now they walk about with it "
          "in their pockets. Coins with a king on them that nobody remembers. I've a buyer in the "
          "highlands who'll pay for every one, and I'm too old to argue with a wight over it.\n\n"
          "They come up out of the west barrow and the east one. Bring me eight coins and I'll make "
          "it worth the trip.",
          "The west barrow and the east one. Mind your feet on the way over, the shallows shift.",
          "Eight. Look at that king. Nobody's spent one of these in a thousand years, and now I'm "
          "going to.\n\nYou've earned your cut.",
          R(38, ("Beachcomber's Hauberk", "chest", "of the Hunt", "mail", None, "Mail Chest (Agi/Int/AP)"),
            ("Wight-Gold Signet", "ring", "of the Sorcerer", None, None, "Ring (Int/Sta/SP)"),
            ("Saltpenny's Cudgel", "main_hand", "of the Bear", None, "mace_1h", "Mace (Str/Sta)")),
          nxt="hz_saltgrave_lanterns"),
        Q("hz_saltgrave_lanterns", "Lights on the Barrows", "hz_saltgrave_maud", sz, 39,
          [{"type": "kill", "target": "Barrow Lantern", "count": 6},
           {"type": "kill", "target": "Brine-Wight", "count": 6}],
          "You've seen the lights out on the barrows at night. Corpse-lights, my mother called them. "
          "They're not lights. They're the dead that couldn't find their bodies, and they lead the "
          "living ones out into the water.\n\nI lost a boat to them last winter. I'd like to stop "
          "losing things.\n\nPut out six of the lights, and six of the wights they keep lit for.",
          "The barrows, west and east. Don't follow a light anywhere it wants you to go.",
          "It's darker out there tonight. Good dark. The kind you can sleep in.",
          R(39, ("Corpse-Light Mantle", "shoulder", "of the Invoker", "cloth", None, "Cloth Shoulders (Int/SP/Crit)"),
            ("Barrow-Warden's Belt", "waist", "of the Champion", "plate", None, "Plate Belt (Str/Sta/Def)"),
            ("Tide-Slick Leggings", "legs", "of the Assassin", "leather", None, "Leather Legs (Agi/Hit/Crit)")),
          nxt="hz_saltgrave_king"),
        Q("hz_saltgrave_king", "The Brine King", "hz_saltgrave_maud", sz, 40,
          [{"type": "kill", "target": "The Brine King", "count": 1},
           {"type": "kill", "target": "Drowned Barrow-Thane", "count": 5}],
          "There's a fourth barrow, out on its own to the north. The King's. The others are his "
          "thanes, and they don't rest because he doesn't.\n\nHe walks the top of his barrow at low "
          "tide with his crown on, and he doesn't like visitors. I won't lie to you: I wouldn't go "
          "alone. I wouldn't go at all. But if anyone's going to put him back in the ground, it'll "
          "be somebody who brought friends.\n\nHis thanes stand round him. Cut through five and "
          "you'll find him.",
          "North, out past the middle bar. Bring friends. I mean it.",
          "You did it. The water's gone still out there, first time since I came.\n\nThat's the "
          "best thing I own. Take it.",
          R(40, ("Kingsbane Greataxe", "main_hand", "of the Gladiator", None, "axe_2h", "Two-Hand Axe (Str/Hit/Crit)"),
            ("Thane-Breaker's Helm", "head", "of the Defender", "plate", None, "Plate Helm (Sta/Def/Dodge)"),
            ("Robes of the Low Tide", "chest", "of the Prophet", "cloth", None, "Cloth Robe (Int/Spi/Healing)"),
            ("Barrowstalker Hood", "head", "of the Monkey", "leather", None, "Leather Helm (Agi/Sta)")),
          elite=True),
        # ------------------------------------------------------------------ The Glasswaste
        Q("hz_glass_shards", "Glass Teeth", "hz_glasswaste_durek", gw, 15,
          [{"type": "fetch", "target": "fused_glass_shard", "count": 8}],
          "The basilisks here grow glass on their backs. They lie in the hot sand and it fuses to "
          "them, a little more every year, till they're walking about wearing a fortune.\n\nI make "
          "blades from it. Best edge you'll ever see, and it never rusts. But I've got one good leg "
          "left and I'm keeping it.\n\nThe shard fields, west of the mouth. Eight shards.",
          "West of the mouth, where the sand shines. They'll see you coming. Let them.",
          "Feel the edge on that one. Careful. See?\n\nI'll have one of these sharpened for you by "
          "the time you're back.",
          R(15, ("Glass-Edge Shiv", "main_hand", "of the Tiger", None, "dagger", "Dagger (Str/Agi)"),
            ("Shardscale Vest", "chest", "of the Monkey", "leather", None, "Leather Chest (Agi/Sta)"),
            ("Fused Sand Cord", "waist", "of the Eagle", "cloth", None, "Cloth Belt (Int/Sta)")),
          nxt="hz_glass_kilns"),
        Q("hz_glass_kilns", "Walking Kilns", "hz_glasswaste_durek", gw, 16,
          [{"type": "kill", "target": "Kiln-Walker", "count": 8}],
          "Whatever burned this canyon didn't stop. It's still up on the rise to the north, walking "
          "about on its own, and every time one of them comes down the sand goes to glass under it "
          "and my camp gets smaller.\n\nKiln-walkers, I call them. Put out eight and I'll get a "
          "season's peace.",
          "Up the rise to the north. Water won't help. Hitting them will.",
          "I could hear them stop. You don't notice a noise till it stops.\n\nHere, for your "
          "trouble.",
          R(16, ("Ashfoot's Spare Axe", "main_hand", "of the Bear", None, "axe_2h", "Two-Hand Axe (Str/Sta)"),
            ("Kilnwalker Gloves", "hands", "of the Sorcerer", "cloth", None, "Cloth Gloves (Int/Sta/SP)"),
            ("Heat-Tempered Bracers", "wrist", "of the Champion", "mail", None, "Mail Bracers (Str/Sta/Def)")),
          nxt="hz_glass_blister"),
        Q("hz_glass_blister", "Old Blister", "hz_glasswaste_durek", gw, 17,
          [{"type": "kill", "target": "Old Blister", "count": 1},
           {"type": "kill", "target": "Glassback Basilisk", "count": 6}],
          "There's one basilisk up in the hollow at the north end that's more glass than beast. Old "
          "Blister. She's the reason I've got one good leg.\n\nShe's been growing that hide since "
          "before I was born, and nothing I own cuts it. Don't go alone. Take people you trust and "
          "go up through the basilisks round her, and when she opens her mouth, don't be in front "
          "of it.",
          "North, into the hollow. Bring people. She'll take your leg too.",
          "You've no idea. You've no idea what that means.\n\nI made this from the first shard I "
          "ever took off her. It's yours.",
          R(17, ("Blister-Glass Glaive", "main_hand", "of the Vanquisher", None, "polearm", "Polearm (Str/AP/Hit)"),
            ("Glassbreaker Pauldrons", "shoulder", "of the Defender", "plate", None, "Plate Shoulders (Sta/Def/Dodge)"),
            ("Kiln-Fired Focus", "off_hand", "of the Invoker", None, "tome", "Tome (Int/SP/Crit)"),
            ("Canyon-Runner's Boots", "feet", "of the Assassin", "leather", None, "Leather Boots (Agi/Hit/Crit)")),
          elite=True),
        # ------------------------------------------------------------------ The Tanglewood Shoals
        Q("hz_tangle_shallows", "Teeth in the Green Water", "hz_tangle_kojira", tw, 14,
          [{"type": "kill", "target": "Mangrove Snapper", "count": 6},
           {"type": "kill", "target": "Shoal Stalker", "count": 6}],
          "I'm Koji'ra. My grandmother told me about these shoals, and everybody laughed at her, and "
          "I came anyway. Now I'm the one nobody would believe.\n\nThe snappers own the water and "
          "the stalkers own the trees, and between them I can't get off this beach. Thin them out "
          "for me. Six of each.",
          "The snappers are in the water round the landing. The stalkers are in the tangles east and "
          "west. Watch the branches.",
          "I walked to the big island this morning and nothing tried to eat me. First time.",
          R(14, ("Snapper-Hide Vest", "chest", "of the Monkey", "leather", None, "Leather Chest (Agi/Sta)"),
            ("Shoal-Runner's Sandals", "feet", "of the Eagle", "cloth", None, "Cloth Boots (Int/Sta)"),
            ("Stalker's Claw", "main_hand", "of the Tiger", None, "fist_weapon", "Fist (Str/Agi)")),
          nxt="hz_tangle_sap"),
        Q("hz_tangle_sap", "Sap That Glows", "hz_tangle_kojira", tw, 15,
          [{"type": "fetch", "target": "glowing_sap", "count": 6}],
          "The trees out here bleed light. The guardians on the big island carry it in them, and "
          "my grandmother said it came up from the roots of one tree, older than the isles.\n\nI "
          "want to know if she was right. Bring me six of it and I'll read what's in it.",
          "The big island. The guardians are slow, but they don't forget you.",
          "Look at it move. It's not sap at all. It's coming up from something, a long way down.\n\n"
          "She was right. I knew she was right.",
          R(15, ("Sapglow Wand", "main_hand", "of the Sorcerer", None, "wand", "Wand (Int/Sta/SP)"),
            ("Rootward Bracers", "wrist", "of the Champion", "plate", None, "Plate Bracers (Str/Sta/Def)"),
            ("Glimmerwing Mantle", "shoulder", "of the Hunt", "mail", None, "Mail Shoulders (Agi/Int/AP)")),
          nxt="hz_tangle_grandfather"),
        Q("hz_tangle_grandfather", "Grandfather Mangrove", "hz_tangle_kojira", tw, 16,
          [{"type": "kill", "target": "Grandfather Mangrove", "count": 1},
           {"type": "kill", "target": "Rootbound Guardian", "count": 5}],
          "There's one guardian on the big island bigger than the rest. Grandfather Mangrove, my "
          "grandmother called him, and she said he walks round the old tree the way a dog walks "
          "round a door it's guarding.\n\nI'd like to see that door. I'm not getting past him, and "
          "you won't either, not alone. Bring friends. Cut through his guardians and put him down.",
          "The big island, where the trees get older. Bring friends. He's been growing a long time.",
          "He's down. Now let's see what he was standing in front of.\n\nTake this, you've earned it "
          "twice over.",
          R(16, ("Grandfather's Cudgel", "main_hand", "of the Bear", None, "mace_2h", "Two-Hand Mace (Str/Sta)"),
            ("Mangrove-Bark Helm", "head", "of the Defender", "plate", None, "Plate Helm (Sta/Def/Dodge)"),
            ("Leafwoven Robe", "chest", "of the Prophet", "cloth", None, "Cloth Robe (Int/Spi/Healing)"),
            ("Tanglewalker's Hood", "head", "of the Assassin", "leather", None, "Leather Helm (Agi/Hit/Crit)")),
          elite=True),
        # ------------------------------------------------------------------ The Drowned Idols
        Q("hz_idols_teeth", "Nothing Bites Like a Lagoon", "hz_idols_fizzle", di, 33,
          [{"type": "kill", "target": "Lagoon Crocolisk", "count": 6},
           {"type": "kill", "target": "Jade Serpent", "count": 6}],
          "Fizzle Brassgut, treasure hunter, at your service. I've got a boat, a map and a lagoon "
          "full of drowned gods made of solid jade, and I can't get off this beach because every "
          "single thing in the water wants to eat me.\n\nCrocs and serpents. Six of each and I'll "
          "cut you in.",
          "They're all round the landing. You'll hear the crocs before you see them.",
          "Look at that! I can see the water! I can see the TREASURE in the water!",
          R(33, ("Croc-Leather Jerkin", "chest", "of the Monkey", "leather", None, "Leather Chest (Agi/Sta)"),
            ("Treasure Hunter's Goggles", "head", "of the Eagle", "cloth", None, "Cloth Helm (Int/Sta)"),
            ("Serpent-Scale Girdle", "waist", "of the Champion", "plate", None, "Plate Belt (Str/Sta/Def)")),
          nxt="hz_idols_jade"),
        Q("hz_idols_jade", "Small Pieces of God", "hz_idols_fizzle", di, 34,
          [{"type": "fetch", "target": "jade_idol_shard", "count": 8}],
          "The trolls that drowned with the idols carry bits of them. Shards. Chipped off for luck, "
          "I reckon, and it didn't work, did it?\n\nThe drowned ones on the west and east isles have "
          "them. Eight shards and I've got enough to buy a bigger boat.",
          "The western and eastern isles. The hexers will try to put a curse on you. Don't let them.",
          "Eight! These are going to make me so rich. Us. Us rich. Here, your share up front.",
          R(34, ("Jade-Edge Scimitar", "main_hand", "of the Tiger", None, "sword_1h", "Sword (Str/Agi)"),
            ("Hexward Mantle", "shoulder", "of the Invoker", "cloth", None, "Cloth Shoulders (Int/SP/Crit)"),
            ("Drowned-Idol Coif", "head", "of the Hunt", "mail", None, "Mail Helm (Agi/Int/AP)")),
          nxt="hz_idols_zunjal"),
        Q("hz_idols_zunjal", "The Idol-Keeper", "hz_idols_fizzle", di, 35,
          [{"type": "kill", "target": "Idol-Keeper Zun'jal", "count": 1},
           {"type": "kill", "target": "Drowned Hexer", "count": 5}],
          "Bad news. The biggest idol, on the last isle up north, has a keeper. Zun'jal. Drowned "
          "with the rest of them and didn't let it slow him down one bit. He's got his hexers round "
          "him and he's not sharing.\n\nI'm not asking you to go alone. I'm asking you to bring "
          "every friend you've got.",
          "The last isle, north past the jade isles. Bring friends. Lots of friends.",
          "He's gone? He's GONE! Fizzle Brassgut, richest goblin in the jungle!\n\nTake your pick, "
          "partner. You earned it.",
          R(35, ("Keeper's Hexblade", "main_hand", "of the Necromancer", None, "dagger", "Dagger (Int/Sta/Hit)"),
            ("Jadeplate Breastplate", "chest", "of the Defender", "plate", None, "Plate Chest (Sta/Def/Dodge)"),
            ("Drowned God's Vestments", "chest", "of the Prophet", "cloth", None, "Cloth Robe (Int/Spi/Healing)"),
            ("Lagoon-Runner's Leggings", "legs", "of the Assassin", "leather", None, "Leather Legs (Agi/Hit/Crit)")),
          elite=True),
        # ------------------------------------------------------------------ The Buried Caravan
        Q("hz_caravan_dunes", "Things in the Sand", "hz_caravan_rizzo", bc, 44,
          [{"type": "kill", "target": "Sandscour Scorpid", "count": 6},
           {"type": "kill", "target": "Caravan Ghoul", "count": 6}],
          "Rizzo Dustwhistle. My family's been looking for this caravan for four generations and "
          "I'm the one who found it. Of course I am.\n\nProblem is it's full of scorpids and the "
          "people who were on it, who aren't people any more. Clear me a way in. Six of each.",
          "The dunes by the landing, and the wagon graves west. Watch the sand, it moves.",
          "I can see a wagon wheel sticking up out of the sand. Grandma's wagon wheel, maybe!",
          R(44, ("Scorpid-Shell Gauntlets", "hands", "of the Juggernaut", "plate", None, "Plate Gloves (Sta/Armor/Parry)"),
            ("Sandwalker's Sash", "waist", "of the Owl", "cloth", None, "Cloth Belt (Int/Spi)"),
            ("Dune-Dancer's Boots", "feet", "of the Monkey", "leather", None, "Leather Boots (Agi/Sta)")),
          nxt="hz_caravan_manifest"),
        Q("hz_caravan_manifest", "The Manifest", "hz_caravan_rizzo", bc, 45,
          [{"type": "fetch", "target": "caravan_manifest_page", "count": 8}],
          "The caravan's ledger got torn up when they went under. Every guard on that caravan was "
          "carrying a piece of it, because the Master didn't trust anybody.\n\nThe revenants in "
          "the market still have them. Eight pages and I'll know what's buried here, and where.",
          "The drowned market, north of the dunes. The revenants carry them. They won't give them up.",
          "Silk, spice, a dragon's egg... a DRAGON'S EGG? Oh, Grandma.",
          R(45, ("Ledger-Keeper's Wand", "main_hand", "of the Sorcerer", None, "wand", "Wand (Int/Sta/SP)"),
            ("Caravan Guard's Hauberk", "chest", "of the Hunt", "mail", None, "Mail Chest (Agi/Int/AP)"),
            ("Trader's Ring of Sand", "ring", "of the Assassin", None, None, "Ring (Agi/Hit/Crit)")),
          nxt="hz_caravan_master"),
        Q("hz_caravan_master", "The Last Caravan Master", "hz_caravan_rizzo", bc, 46,
          [{"type": "kill", "target": "The Last Caravan Master", "count": 1},
           {"type": "kill", "target": "Sandstone Colossus", "count": 3}],
          "The ledger says the Master kept the good stuff in his own wagon, at the very back. And "
          "he's still in it. He still thinks he's delivering it.\n\nThe colossi at the gate keep "
          "people away from him, and he'll be harder than all of them. Bring a crew. Then I'll "
          "finally know what four generations of my family died looking for.",
          "North, through the buried gate to the back of the caravan. Bring a crew.",
          "It's real. All of it. Four generations, and it's real.\n\nPick something. Pick two, I "
          "won't tell.",
          R(46, ("Caravan Master's Halberd", "main_hand", "of the Vanquisher", None, "polearm", "Polearm (Str/AP/Hit)"),
            ("Sunscoured Cowl", "head", "of the Invoker", "cloth", None, "Cloth Helm (Int/SP/Crit)"),
            ("Dunewarden Helm", "head", "of the Defender", "plate", None, "Plate Helm (Sta/Def/Dodge)"),
            ("Sandstalker's Hood", "head", "of the Assassin", "leather", None, "Leather Helm (Agi/Hit/Crit)")),
          elite=True),
        # ------------------------------------------------------------------ The Weeping Pines
        Q("hz_pines_webs", "The Hanging Wood", "hz_pines_ilsabet", wp, 17,
          [{"type": "kill", "target": "Gloom Spider", "count": 8}],
          "I'm Ilsabet. I came here to study the mere and I've stayed because I can't leave it "
          "unfinished.\n\nThe spiders in the west wood hang their kills in the pines, and then the "
          "kills come down again on their own. I'd like fewer of both.\n\nEight spiders. The wood "
          "west of the track.",
          "West of the track, where the pines are thickest. Look up before you look down.",
          "Quieter. I can hear the water again, which isn't better, but at least I know where it is.",
          R(17, ("Gloomsilk Gloves", "hands", "of the Owl", "cloth", None, "Cloth Gloves (Int/Spi)"),
            ("Pine-Needle Leggings", "legs", "of the Wolf", "leather", None, "Leather Legs (Agi/Spi)"),
            ("Webcutter", "main_hand", "of the Tiger", None, "sword_1h", "Sword (Str/Agi)")),
          nxt="hz_pines_water"),
        Q("hz_pines_water", "Mere-Water", "hz_pines_ilsabet", wp, 18,
          [{"type": "fetch", "target": "vial_of_mere_water", "count": 6}],
          "The wraiths at the mere are made of it. The water, I mean. If you break one apart there's "
          "a little left that won't drain away, and that's what I need. It remembers things, and I "
          "want to know what.\n\nSix vials. The wraiths keep to the mere and the shrine above it.",
          "The mere, and the shrine north of it. Don't drink any. I know you weren't going to.",
          "Six. Hold one up to the light. See the shapes? Those are the pines, from before.\n\nThank "
          "you. Truly.",
          R(18, ("Mere-Dipped Wand", "main_hand", "of the Necromancer", None, "wand", "Wand (Int/Sta/Hit)"),
            ("Stillwater Coif", "head", "of the Eagle", "mail", None, "Mail Helm (Int/Sta)"),
            ("Drowned Copse Girdle", "waist", "of the Bear", "plate", None, "Plate Belt (Str/Sta)")),
          nxt="hz_pines_weeping"),
        Q("hz_pines_weeping", "What Weeps", "hz_pines_ilsabet", wp, 18,
          [{"type": "kill", "target": "Weeping Worgen", "count": 8},
           {"type": "kill", "target": "Rotbark Treant", "count": 4}],
          "The worgen here don't hunt. They walk the track and weep, and if you get between one and "
          "the water it'll tear you apart to get past. The trees in the drowned copse have started "
          "doing the same.\n\nI've read enough to know they're not the cause. But they're in the way "
          "of the cause. Eight worgen and four of the rotbarks.",
          "The track, and the copse east of the mere. They won't stop crying. Don't let it get to you.",
          "It's not the worgen. It never was. It's her.",
          R(18, ("Weeping Hide Jerkin", "chest", "of the Hunt", "mail", None, "Mail Chest (Agi/Int/AP)"),
            ("Rotbark Buckler", "off_hand", None, None, "shield", "Shield (Sta/Block)"),
            ("Mourner's Sash", "waist", "of the Physician", "cloth", None, "Cloth Belt (Sta/Int/Healing)")),
          nxt="hz_pines_widow"),
        Q("hz_pines_widow", "The Widow of the Mere", "hz_pines_ilsabet", wp, 19,
          [{"type": "kill", "target": "The Widow of the Mere", "count": 1},
           {"type": "kill", "target": "Mere Wraith", "count": 5}],
          "She drowned herself in the mere after the pines died, and she took the wood with her. "
          "That's what the vials showed me. Everything here weeps because she does.\n\nShe rises "
          "out of the water when the fog's thickest, with her wraiths round her. I can't fight her. "
          "You can't either, not alone. Bring people who aren't afraid of crying things.",
          "The mere. Wait for the fog. Bring friends, and don't listen when she says your name.",
          "The fog's thinning. I can see the far shore.\n\nI think I can go home now. Take this. "
          "I won't need it where I'm going.",
          R(19, ("Widow's Lament", "main_hand", "of the Invoker", None, "staff", "Staff (Int/SP/Crit)"),
            ("Fogpiercer Bow", "ranged", "of the Sharpshooter", None, "bow", "Bow (Agi/AP/Hit)"),
            ("Mere-Guard Breastplate", "chest", "of the Champion", "plate", None, "Plate Chest (Str/Sta/Def)"),
            ("Stillwater Cowl", "head", "of the Prophet", "cloth", None, "Cloth Helm (Int/Spi/Healing)")),
          elite=True),
    ]


# ============================================================================== BUILD
def build():
    kits, creatures, loot = {}, {}, {"_notes": (
        "Hidden zones' bosses (tools/build_hidden_content.py). Item level is the boss's level + 5; "
        "every boss drops two of these (world/hidden_zones multi_drop); from level 30 one of them is "
        "a one-of-a-kind epic. Kyle, 14 Nov 2026: 'they drop at 4 to 5 ilvl and can have unique "
        "epics above level 30.'")}
    registry = {}
    enc = json.loads((DATA / "creatures/encounters.json").read_text(encoding="utf-8"))
    for zname, z in ZONES.items():
        names = []
        for cname, (tmpl, lvl, boss, sprite, abilities) in z["creatures"].items():
            kid = "hidden_" + "".join(ch for ch in cname.lower().replace(" ", "_") if ch.isalnum() or ch == "_")
            kits[kid] = kit(lvl, boss, abilities)
            d = {"template": tmpl, "level_range": [lvl, lvl], "ability_kit": kid}
            if boss:
                d.update({"is_boss": True, "boss_multiplier": 2.5})
            creatures[cname] = d
            names.append(cname)
        table = {n: (0 if z["creatures"][n][2] else z["weights"].get(n, 1)) for n in names}
        if z["kind"] == "layer" or (z["kind"] == "frontier" and z.get("frontier_type") == "deep"):
            region = enc["zones"].setdefault(z["region"], {})
            region.setdefault("caves", {})[zname] = {"name": zname, "creatures": table}
        else:
            enc["zones"][zname] = z["encounters"](table) if callable(z.get("encounters")) else z["encounters"]
        for boss, items in z["loot"].items():
            lvl = z["creatures"][boss][1]
            pool = []
            for it in items:
                iname, slot, suffix, flavor, armor, weapon = it[:6]
                rarity = it[6] if len(it) > 6 else "rare"
                ilvl = lvl + (8 if z["kind"] == "frontier" else 5)
                kw = {}
                if armor:
                    kw["armor_type"] = armor
                if weapon:
                    kw["weapon_type"] = weapon
                if rarity == "epic" and z["kind"] != "frontier":
                    assert lvl >= 30, f"{iname}: unique epics only from level 30 (Kyle)"
                pool.append(make(iname, slot, suffix or "of the Bear", ilvl, flavor, rarity=rarity,
                                 req=max(1, lvl - 2), **kw))
            loot[boss] = pool
        registry[zname] = {"kind": z["kind"], "parent": z["parent"], "levels": list(z["levels"]),
                           "region": z.get("region"),
                           **({"frontier_type": z["frontier_type"]} if z.get("frontier_type") else {}),
                           "bosses": [n for n in names if z["creatures"][n][2]],
                           "multi_drop": 2}
        for ex in z.get("extra_registry", {}).items():
            registry[zname][ex[0]] = ex[1]
    return kits, creatures, loot, registry, enc


def write_people():
    """The givers (ambient_npcs.json), their quests (data/quests/hidden_zones.json) and the quest
    items' sources (data/creatures/quest_drops.json)."""
    from tools.handbuilt_skull_zones import GIVERS
    p = DATA / "npcs/ambient_npcs.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    lst = doc if isinstance(doc, list) else doc["npcs"]
    lst[:] = [n for n in lst if not str(n.get("npc_id", "")).startswith("hz_")]
    for nid, n in NPCS.items():
        zone, x, y = GIVERS[nid]
        lst.append({"npc_id": nid, "name": n["name"], "zone": zone.lower().replace(" ", "_").replace("'", ""),
                    "x": x, "y": y, "greeting": n["greeting"], "facing": "down", "race": n["race"],
                    "gender": n["gender"], "appearance_variant": 3})
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA / "quests/hidden_zones.json").write_text(json.dumps({"quests": quests()}, indent=2, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
    p = DATA / "creatures/quest_drops.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    for cname, (iid, iname, desc, chance) in DROPS.items():
        lst = [d for d in doc["drops"].get(cname, []) if d.get("item_id") != iid]
        lst.append({"item_id": iid, "name": iname, "category": "quest", "description": desc, "chance": chance})
        doc["drops"][cname] = lst
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


#: the ground a skull zone's herbs, ore and fish come from (data/gathering/node_pools.json key)
NODE_PARENT = {"The Saltgrave": "arathi_east", "The Glasswaste": "durotar", "The Weeping Pines": "silverpine_north",
               "The Tanglewood Shoals": "echo_isles", "The Drowned Idols": "northern_stranglethorn",
               "The Buried Caravan": "northern_tanaris"}


def write_node_pools():
    """Kyle: "I WANT to be rewarded for exploring." A skull zone's ground carries what its parent's
    does, half again as much of it, and more of it showing at once."""
    p = DATA / "gathering/node_pools.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    z = doc["zones"]
    for zone, parent in NODE_PARENT.items():
        src = z.get(parent)
        if not src:
            continue
        key = zone.lower().replace(" ", "_").replace("'", "")
        pool = json.loads(json.dumps(src))
        pool["slots"] = int(round(pool.get("slots", 12) * 1.5))
        pool["active_percent"] = min(0.8, pool.get("active_percent", 0.45) + 0.25)
        if "fishing" in pool:
            pool["fishing"]["slots"] = int(round(pool["fishing"].get("slots", 4) * 1.5))
        z[key] = pool
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sprite_rules():
    """name -> sprite id, for creature_sprites.py (tools/build_hidden_content.SPRITES)."""
    return {c: v[3] for z in ZONES.values() for c, v in z["creatures"].items()}


def main():
    kits, creatures, loot, registry, enc = build()
    merge_json(DATA / "creatures/ability_kits.json", "kits", kits, "kits")
    merge_json(DATA / "creatures/creatures.json", "creatures", creatures, "creatures")
    (DATA / "creatures/encounters.json").write_text(json.dumps(enc, indent=2, ensure_ascii=False) + "\n",
                                                    encoding="utf-8")
    (DATA / "loot/hidden_boss_loot.json").write_text(json.dumps(loot, indent=2, ensure_ascii=False) + "\n",
                                                     encoding="utf-8")
    doc = {"_about": ("Hidden zones (world/hidden_zones.py). Written by tools/build_hidden_content.py. "
                      "Kyle, 14 Nov 2026: 'I don't want to see as I want these to be secrets.'"),
           "zones": registry}
    (DATA / "world/hidden_zones.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
    (DATA / "creatures/hidden_sprites.json").write_text(json.dumps(sprite_rules(), indent=2, ensure_ascii=False) + "\n",
                                                        encoding="utf-8")
    write_people()
    write_node_pools()
    print(f"{len(registry)} hidden zones, {len(creatures)} creatures, {sum(len(v) for k, v in loot.items() if not k.startswith('_'))} boss items")


if __name__ == "__main__":
    main()
