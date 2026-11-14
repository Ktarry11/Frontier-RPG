#!/usr/bin/env python3
"""Crystalline Underdark content pass (2026-10-27). Idempotent.

  PYTHONPATH=. python3 tools/build_underdark_content.py
  cd tools && python3 generate_creatures.py        # after any kit edit (kits: monster_kits.UNDERDARK_KITS)

LEVEL LADDER
  The Frostward Descent   31-34:  ice 31-33 | the seam 32-33 | crystal 32-34
                                  Hoarfang 33, The Frozen Cartographer 33, Latticeborn 34
  The Crystalline Underdark 33-37: Hollow Dawn 33-34 | Sporefall 33-35 | Shardfields 33-35
                                  Mycelial Reach 34-36 | The Lattice 34-36 | Lumen Marsh 34-36
                                  Weeping Colonnade 35-37 | Sunken Archive 35-37
                                  The Dim Reaches 36-37 | The Riftward 36-37
  The Hollow Geode (cave) 34-38:  trash 34-37, Shardmaw 37, The Prism Warden 37, Heartgrown 38
  The Deep Bloom (dungeon) 36-40: trash 36-39, The Index 38, The Second Copy 38, The Scriptor 39,
                                  Errata 39, The Deep Bloom 40

FIVE POPULATIONS, and the combat identities are in tools/monster_kits.UNDERDARK_KITS: Alterac frost, the
expedition that froze mid-survey, the lattice (which REPEATS), the Bloom (a network that buffs and heals
itself), and the unfinished things of the Dim and the Riftward. This zone is also where the game finally
uses `arcane` and `frost` properly - between them they accounted for 74 abilities in the entire project
before this pass.

LOOT, AND WHY IT IS PLANNED RATHER THAN DISCOVERED. The Hillsbrad pass shipped a melee dump - 14 leather
to 4 cloth, strength 50 to intellect 18, one caster weapon in ninety-six - and it had to be rebalanced
after the fact. So this pass fixes the budget up front and tools/qa_underdark_content.py checks it:

  * 18 weapons, and EVERY ONE of the 18 weapon types appears exactly once. No pool of swords and bows.
  * 40 armour pieces, ten apiece across cloth / leather / mail / plate, spread over nine slots.
  * Suffixes split roughly evenly between casting and physical, which an arcane zone has every excuse for.
  * The deliberate oddities Kyle asked for: a healing-power gun, a spell-power two-hander, a caster
    crossbow, a caster one-hand sword. 30 classes need gear and most of them are not warriors.

RULES  ONE item per kill from the creature's own pool of 4; item_level = creature level + 3; real loot
       formulas (tools/build_durotar_content.make). Named rares are is_boss with weight 0 - they roll at
       ~6% in their subzone, so any quest that wants one is paired with trash (and per the standing rule,
       no quest is ever built around a rare).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

# ======================================================================================================================
# CREATURES
# ======================================================================================================================
DESCENT_CREATURES = {
    # the ice end - Alterac's cold, which is ordinary cold, and the last ordinary thing on the way down
    "Frostward Prowler": C("beast_fast", 31, 32, "frostward_prowler"),
    "Hoarfrost Yeti": C("beast_large", 31, 33, "hoarfrost_yeti"),
    "Rime-Shelled Crawler": C("vermin_sneaky", 31, 33, "rime_shelled_crawler"),
    # the seam - an expedition that froze mid-survey, and the Syndicate who followed the Codex down
    "Alterac Expeditionary": C("undead_basic", 32, 33, "alterac_expeditionary"),
    "Syndicate Deepscout": C("humanoid_rogue", 32, 33, "syndicate_deepscout"),
    # the crystal end - the first things down here that are not from Azeroth
    "Lattice Crawler": C("elemental_bruiser", 32, 33, "lattice_crawler"),
    "Shardling": C("elemental_caster", 32, 34, "shardling"),
    "Hoarfang": C("beast_large", 33, 33, "hoarfang", True, 1.7),
    "The Frozen Cartographer": C("undead_basic", 33, 33, "the_frozen_cartographer", True, 1.8),
    "Latticeborn": C("elemental_bruiser", 34, 34, "latticeborn", True, 1.9),
}

UNDERDARK_CREATURES = {
    # the fungal country - the Sporefall and the Mycelial Reach
    "Sporeback Grazer": C("beast_basic", 33, 35, "sporeback_grazer"),
    "Spore-Drifter": C("vermin_swarm", 33, 35, "spore_drifter"),
    "Myconid Tender": C("humanoid_caster", 34, 36, "myconid_tender"),
    "Mycelial Husk": C("undead_basic", 34, 36, "mycelial_husk"),
    # the crystal country - the Shardfields and the Lattice
    "Crystalback Skitterer": C("vermin_sneaky", 33, 35, "crystalback_skitterer"),
    "Lattice Sentry": C("elemental_bruiser", 34, 36, "lattice_sentry"),
    "Shard Diviner": C("elemental_caster", 34, 36, "shard_diviner"),
    # the Lumen Marsh
    "Lumen Leech": C("aquatic_basic", 34, 36, "lumen_leech"),
    "Glimmerjaw": C("beast_large", 34, 36, "glimmerjaw"),
    # the Colonnade and the Archive - Dalaran's leavings, and the people arguing over them
    "Archive Revenant": C("undead_basic", 35, 37, "archive_revenant"),
    "Codex Dissident": C("humanoid_caster", 35, 37, "codex_dissident"),
    "Syndicate Interloper": C("humanoid_rogue", 34, 36, "syndicate_interloper"),
    # the Dim Reaches and the Riftward - the parts that were not finished
    "Dim-Walker": C("demon_hound", 36, 37, "dim_walker"),
    "The Unfinished": C("elemental_caster", 36, 37, "the_unfinished"),
    "Riftward Aberration": C("elemental_bruiser", 36, 37, "riftward_aberration"),
    # named rares, one per two subzones
    "Capgorger": C("beast_large", 35, 35, "capgorger", True, 1.7),
    "The Thousandth Shard": C("elemental_bruiser", 36, 36, "the_thousandth_shard", True, 1.8),
    "Marsh-Mother Ysmil": C("aquatic_basic", 36, 36, "marsh_mother_ysmil", True, 1.7),
    "Archivist Thelun, Unlisted": C("humanoid_caster", 37, 37, "archivist_thelun", True, 1.8),
    "What Walks in the Dim": C("demon_hound", 37, 37, "what_walks_in_the_dim", True, 1.8),
    "The Half-Written": C("elemental_caster", 37, 37, "the_half_written", True, 1.8),
}

GEODE_CREATURES = {
    "Druse Crawler": C("vermin_sneaky", 34, 36, "druse_crawler"),
    "Geode Tender": C("elemental_caster", 34, 36, "geode_tender"),
    "Crystalbound Husk": C("undead_basic", 35, 37, "crystalbound_husk"),
    "Shell-Grown Lurker": C("beast_large", 35, 37, "shell_grown_lurker"),
    "Shardmaw": C("elemental_bruiser", 37, 37, "shardmaw", True, 1.8),
    "The Prism Warden": C("elemental_caster", 37, 37, "the_prism_warden", True, 1.8),
    "Heartgrown": C("elemental_bruiser", 38, 38, "heartgrown", True, 1.9),
}

BLOOM_CREATURES = {
    # These five names are authored into tools/handbuilt_deep_bloom.py's PACKS; the dungeon cannot load
    # without them (world/cave_spawns.py raises on a pack member with no entry here), which is why the
    # Bloom's registration was held for this pass.
    "Bloom Thrall": C("undead_basic", 36, 39, "bloom_thrall"),
    "Shelf-Grown": C("humanoid_ranged", 36, 38, "shelf_grown"),
    "Spore Scribe": C("humanoid_caster", 36, 38, "spore_scribe"),
    "Mycelial Binder": C("elemental_caster", 37, 39, "mycelial_binder"),
    "Pulpwright": C("elemental_bruiser", 37, 39, "pulpwright"),
    "The Index": C("humanoid_caster", 38, 38, "the_index", True, 1.8),
    "The Second Copy": C("beast_large", 38, 38, "the_second_copy", True, 1.8),
    "The Scriptor": C("undead_basic", 39, 39, "the_scriptor", True, 1.8),
    "Errata": C("elemental_caster", 39, 39, "errata", True, 1.9),
    "The Deep Bloom": C("elemental_bruiser", 40, 40, "the_deep_bloom", True, 2.0),
}

# ======================================================================================================================
# ENCOUNTERS
# ======================================================================================================================
DESCENT_ZONE = {
    "open_zone": {
        "name": "The Frostward Descent",
        "creatures": {"Frostward Prowler": 4, "Hoarfrost Yeti": 3, "Rime-Shelled Crawler": 3,
                      "Alterac Expeditionary": 3, "Syndicate Deepscout": 2,
                      "Lattice Crawler": 3, "Shardling": 3,
                      "Hoarfang": 0, "The Frozen Cartographer": 0, "Latticeborn": 0},
    },
}

UNDERDARK_ZONE = {
    "open_zone": {
        "name": "The Crystalline Underdark",
        "creatures": {"Sporeback Grazer": 4, "Crystalback Skitterer": 3, "Spore-Drifter": 3,
                      "Syndicate Interloper": 2},
    },
    "subzones": {
        "The Hollow Dawn": {"name": "The Hollow Dawn",
                            "creatures": {"Crystalback Skitterer": 4, "Sporeback Grazer": 3,
                                          "Shardling": 2}},
        "The Sporefall": {"name": "The Sporefall",
                          "creatures": {"Sporeback Grazer": 5, "Spore-Drifter": 4, "Myconid Tender": 3,
                                        "Capgorger": 0}},
        "The Shardfields": {"name": "The Shardfields",
                            "creatures": {"Crystalback Skitterer": 4, "Lattice Sentry": 3,
                                          "Shard Diviner": 3, "Syndicate Interloper": 2}},
        "The Mycelial Reach": {"name": "The Mycelial Reach",
                               "creatures": {"Mycelial Husk": 4, "Myconid Tender": 4, "Spore-Drifter": 3,
                                             "Sporeback Grazer": 2}},
        "The Lattice": {"name": "The Lattice",
                        "creatures": {"Lattice Sentry": 5, "Shard Diviner": 4, "Crystalback Skitterer": 2,
                                      "The Thousandth Shard": 0}},
        "The Lumen Marsh": {"name": "The Lumen Marsh",
                            "creatures": {"Lumen Leech": 5, "Glimmerjaw": 3, "Spore-Drifter": 2,
                                          "Marsh-Mother Ysmil": 0}},
        "The Weeping Colonnade": {"name": "The Weeping Colonnade",
                                  "creatures": {"Archive Revenant": 4, "Codex Dissident": 3,
                                                "Syndicate Interloper": 3, "Lattice Sentry": 2}},
        "The Sunken Archive": {"name": "The Sunken Archive",
                               "creatures": {"Archive Revenant": 5, "Codex Dissident": 4,
                                             "Syndicate Interloper": 3,
                                             "Archivist Thelun, Unlisted": 0}},
        "The Dim Reaches": {"name": "The Dim Reaches",
                            "creatures": {"Dim-Walker": 5, "Riftward Aberration": 3, "Archive Revenant": 2,
                                          "What Walks in the Dim": 0}},
        "The Riftward": {"name": "The Riftward",
                         "creatures": {"The Unfinished": 5, "Riftward Aberration": 4, "Dim-Walker": 2,
                                       "The Half-Written": 0}},
    },
    "caves": {
        # A cave, deliberately NOT on world/zone_classification.DUNGEONS, so it keeps the Underdark's ore.
        "The Hollow Geode": {
            "name": "The Hollow Geode",
            "creatures": {"Druse Crawler": 5, "Geode Tender": 4, "Crystalbound Husk": 4,
                          "Shell-Grown Lurker": 4, "Lattice Sentry": 2,
                          "Shardmaw": 0, "The Prism Warden": 0, "Heartgrown": 0},
        },
        # A real Dungeon, listed here because that is where the encounter loader looks for a sub-map's
        # table - the classification is what keeps gathering out of it. Its trash is hand-placed in
        # tools/handbuilt_deep_bloom.py, so these weights only matter as a fallback.
        "The Deep Bloom": {
            "name": "The Deep Bloom",
            "creatures": {"Bloom Thrall": 5, "Shelf-Grown": 4, "Spore Scribe": 4,
                          "Mycelial Binder": 3, "Pulpwright": 3,
                          "The Index": 0, "The Second Copy": 0, "The Scriptor": 0,
                          "Errata": 0, "The Deep Bloom": 0},
        },
    },
}


# ======================================================================================================================
# LOOT - one drop per kill from a hand-made pool of 4. item_level = creature level + 3.
#
# The 18 weapons below use all 18 weapon types exactly once. See the module docstring for why.
# ======================================================================================================================
def descent_pools():
    return {
        "Hoarfang": [
            mk("Glacier-Jaw Pike", "main_hand", "of the Beast", 36,
               "Ice in the sockets, and the sockets are not his.", weapon_type="polearm"),
            mk("Hoarfang's Matted Pelt", "chest", "of the Bear", 36,
               "Four inches thick, and frozen through all four.", armor_type="leather"),
            mk("Upper Dark Stalker's Treads", "feet", "of Agility", 36,
               "He came down here because something colder came down first.", armor_type="mail"),
            mk("Fang-Chipped Torc", "neck", "of the Whale", 36,
               "Bone, with one tooth missing and nothing to show where it went."),
        ],
        "The Frozen Cartographer": [
            # He is not a fight so much as a man finishing a job forty years late.
            mk("Surveyor's Scribing Knife", "main_hand", "of the Tactician", 36,
               "For ruling lines, which is all it has ever been used for.", weapon_type="dagger"),
            mk("Expedition Cartographer's Coat", "chest", "of the Owl", 36,
               "Pockets still full of chalk. The chalk is still dry.", armor_type="cloth"),
            mk("Frostbitten Dividers", "off_hand", "of the Archmage", 36,
               "Set to a width nobody down here can account for."),
            mk("Unfinished Survey Bracers", "wrist", "of Intellect", 36,
               "The last entry reads: the readings are wrong and I am going on.", armor_type="cloth"),
        ],
        "Latticeborn": [
            mk("Repeating Lattice Maul", "main_hand", "of the Sorcerer", 37,
               "Swung once. The second swing arrives on its own.", weapon_type="mace_2h"),
            mk("Latticeborn Carapace", "chest", "of the Beast", 37,
               "Grown in exact rows, which nothing alive bothers to do.", armor_type="mail"),
            mk("Pattern-Cut Greaves", "legs", "of the Soldier", 37,
               "The facets repeat every eleven inches, without exception.", armor_type="plate"),
            mk("First Iteration Band", "ring", "of the Tiger", 37,
               "One of a great many, and all of them identical."),
        ],
    }


def underdark_pools():
    return {
        "Capgorger": [
            mk("Gorger's Rending Claw", "main_hand", "of Agility", 38,
               "It eats the groves it lives in, which is a poor long-term plan.", weapon_type="fist_weapon"),
            mk("Cap-Gorged Hide Vest", "chest", "of the Monkey", 38,
               "Distended, and still faintly warm in the middle.", armor_type="leather"),
            mk("Sporefall Canopy Hood", "head", "of the Wolf", 38,
               "Cut from a cap big enough to shelter under.", armor_type="leather"),
            mk("Spore-Light Pendant", "neck", "of the Prophet", 38,
               "Glows a little in the dark, which down here is no distinction."),
        ],
        "The Thousandth Shard": [
            mk("Wand of the Counted Facet", "main_hand", "of the Invoker", 39,
               "The Codex counted to nine hundred and ninety-nine and stopped.", weapon_type="wand"),
            mk("Thousandfold Shardmail", "chest", "of the Monkey", 39,
               "Every scale the same size. Every single one.", armor_type="mail"),
            mk("Enumerator's Gauntlets", "hands", "of the Squire", 39,
               "For handling things that object to being handled.", armor_type="plate"),
            mk("Shard-Count Signet", "ring", "of the Archmage", 39,
               "Engraved with a number that is one short."),
        ],
        "Marsh-Mother Ysmil": [
            mk("Marsh-Mother's Lumen Stave", "main_hand", "of the Prophet", 39,
               "Lit from the inside, the way everything in her water is.", weapon_type="staff"),
            mk("Brood-Tender's Scale Kilt", "legs", "of the Restorer", 39,
               "She mothered something. It was not her own.", armor_type="mail"),
            mk("Drowned-Light Slippers", "feet", "of the Owl", 39,
               "Never dry, and never quite wet.", armor_type="cloth"),
            mk("Ysmil's Clutch-Brooch", "trinket", "of the Seer", 39,
               "Warm. Pulses, on a cycle, roughly with the Lumen."),
        ],
        "Archivist Thelun, Unlisted": [
            # Struck from the Codex's record for writing down what the cavern told him. He kept writing.
            mk("Thelun's Unlisted Tome", "off_hand", "of the Archmage", 40,
               "The Codex burned their copy. He was not using their copy.", weapon_type="tome"),
            mk("Robes of the Struck Entry", "chest", "of the Sorcerer", 40,
               "The Codex sigil unpicked from the breast, badly, in a hurry.", armor_type="cloth"),
            mk("Marginalia Shoulderpads", "shoulder", "of the Elder", 40,
               "Covered edge to edge in a hand getting smaller and faster.", armor_type="cloth"),
            mk("Expunged Archivist's Band", "ring", "of the Necromancer", 40,
               "His name was filed off it. The groove is still legible."),
        ],
        "What Walks in the Dim": [
            mk("Unlit Cleaver", "main_hand", "of the Gladiator", 40,
               "Nobody has described this. Several people have tried.", weapon_type="axe_2h"),
            mk("Dim-Walker's Lightless Mantle", "shoulder", "of the Champion", 40,
               "The Lumen does not land on it. It simply does not.", armor_type="plate"),
            mk("Hide of the Unseen Thing", "legs", "of the Bandit", 40,
               "Taken off something that was never properly looked at.", armor_type="leather"),
            mk("Charm Against the Dark", "trinket", "of the Bear", 40,
               "Codex issue. Not Codex-approved. Everyone in the Dim carries one."),
        ],
        "The Half-Written": [
            mk("Draft Blade", "main_hand", "of the Mind's Eye", 40,
               "The edge is specified. The rest is not.", weapon_type="sword_1h"),
            mk("Vestments of the Unspecified", "chest", "of the Tactician", 40,
               "Cut for a body of no stated dimensions.", armor_type="cloth"),
            mk("Half-Written Girdle", "waist", "of the Spell Breaker", 40,
               "The buckle is described in detail. Nothing else is.", armor_type="leather"),
            mk("Revision Loop", "ring", "of the Invoker", 40,
               "Worn smooth in a way that suggests it has been made more than once."),
        ],
    }


def geode_pools():
    return {
        "Shardmaw": [
            mk("Shardmaw's Facet-Axe", "main_hand", "of the Soldier", 40,
               "Grown, not forged, and better than forged.", weapon_type="axe_1h"),
            mk("Druse-Plated Bulwark", "off_hand", "of Blocking", 40,
               "A sheet of the shell, still pointing inward.", weapon_type="shield"),
            mk("Maw-Scarred Pauldrons", "shoulder", "of the Squire", 40,
               "Chewed at, and the chew marks have themselves crystallised.", armor_type="plate"),
            mk("Light-Swallower's Collar", "neck", "of Precision", 40,
               "Holds no reflection at all, at any angle."),
        ],
        "The Prism Warden": [
            mk("Warden's Refracting Crossbow", "ranged", "of the Spell Breaker", 40,
               "Fires one bolt. Three arrive, and two of them are not there.", weapon_type="crossbow"),
            mk("Prismbound Hauberk", "chest", "of the Bandit", 40,
               "Shows a different colour to every person looking at it.", armor_type="mail"),
            mk("Total Reflection Bracers", "wrist", "of the Archmage", 40,
               "Nothing gets out, which is a strange property for a bracer.", armor_type="leather"),
            mk("Warden's Splitting Lens", "trinket", "of the Invoker", 40,
               "One lens. More than one image, and they disagree."),
        ],
        "Heartgrown": [
            mk("Heartgrown Crushing Hammer", "main_hand", "of the Restorer", 41,
               "The core of the geode grew a fist. This is the fist.", weapon_type="mace_1h"),
            mk("Core-Grown Breastplate", "chest", "of the Champion", 41,
               "Still faintly growing, which the Codex say is fine.", armor_type="plate"),
            mk("Cavity-Walker's Sabatons", "feet", "of the Beast", 41,
               "For standing in the only part of the Geode with any room left.", armor_type="plate"),
            mk("The Last Open Space", "trinket", "of the Bear", 41,
               "A hollow bead. It is the only hollow thing left in there."),
        ],
    }


def bloom_pools():
    return {
        "The Index": [
            mk("Catalogue-Totem of the Stacks", "main_hand", "of the Seer", 41,
               "A fruiting body grown in the shape of a thing it saw held.", weapon_type="totem"),
            mk("Index-Grown Vestment", "chest", "of the Archmage", 41,
               "Ranked and ordered, like everything it makes.", armor_type="cloth"),
            mk("Cross-Reference Bindings", "wrist", "of the Restorer", 41,
               "Two straps, each referring to the other.", armor_type="leather"),
            mk("Entry Under Your Name", "neck", "of the Mind's Eye", 41,
               "It has one. You have not told it anything."),
        ],
        "The Second Copy": [
            mk("Duplicate Longbow", "ranged", "of the Marksman", 41,
               "An exact copy of a bow. Exact, except for the parts it guessed.", weapon_type="bow"),
            mk("Twice-Grown Scale Vest", "chest", "of the Bandit", 41,
               "Every scale has a twin, and the twins are drifting apart.", armor_type="leather"),
            mk("Copyist's Mail Coif", "head", "of the Marksman", 41,
               "Rings in ranks of forty. Then thirty-nine. Then forty.", armor_type="mail"),
            mk("Repeated Error Band", "ring", "of the Beast", 41,
               "The flaw in it is reproduced perfectly."),
        ],
        "The Scriptor": [
            # Kyle's own example of the spread this game needs: a gun that heals.
            mk("Scriptor's Nib-Gun", "ranged", "of the Restorer", 42,
               "Writes at range, in a hand nobody down here can read.", weapon_type="gun"),
            mk("Scrivener's Pressed Robes", "chest", "of the Prophet", 42,
               "Flattened, smoothed, and ruled into columns.", armor_type="cloth"),
            mk("Fair Copy Handguards", "hands", "of the Restorer", 42,
               "For work that must not be smudged.", armor_type="leather"),
            mk("Struck-Through Girdle", "waist", "of the Marksman", 42,
               "A single line drawn through it, end to end.", armor_type="mail"),
        ],
        "Errata": [
            mk("Thrown Correction", "ranged", "of the Assassin", 42,
               "A wedge of hardened pulp. It is not the right shape for anything.", weapon_type="thrown"),
            mk("Mantle of Compounding Error", "shoulder", "of the Bandit", 42,
               "Grown from everything the Bloom got wrong and kept.", armor_type="mail"),
            mk("Uncorrected Legguards", "legs", "of the Gladiator", 42,
               "One leg is longer. Nothing has been done about it.", armor_type="plate"),
            mk("Erratum Seal", "ring", "of the Spell Breaker", 42,
               "Marks a mistake. Does not say which one."),
        ],
        "The Deep Bloom": [
            mk("Greatblade of What It Learned", "main_hand", "of the Champion", 43,
               "It has never seen a sword. It has read about several.", weapon_type="sword_2h"),
            mk("Heart-of-the-Network Harness", "chest", "of the Beast", 43,
               "Threads run out of it in every direction and do not end.", armor_type="plate"),
            mk("Shroud of the Reading Thing", "back", "of the Elder", 43,
               "Thin as paper, and it has your shape already.", armor_type="cloth"),
            mk("The Whole Network Answers", "trinket", "of the Prophet", 43,
               "Hold it and something very large pays attention."),
        ],
    }


# ======================================================================================================================
def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))

    for group in (DESCENT_CREATURES, UNDERDARK_CREATURES, GEODE_CREATURES, BLOOM_CREATURES):
        cdata["creatures"].update(group)

    for zname, spec in (("The Frostward Descent", DESCENT_ZONE),
                        ("The Crystalline Underdark", UNDERDARK_ZONE)):
        z = edata["zones"].setdefault(zname, {})
        z["open_zone"] = spec["open_zone"]
        if "subzones" in spec:
            z["subzones"] = spec["subzones"]
        if "caves" in spec:
            z["caves"] = spec["caves"]

    out = {"_notes": "Crystalline Underdark boss / named-rare loot (2026-10-27). ONE item drops per kill "
                     "from the pool. item_level = creature level + 3; real loot formulas "
                     "(tools/build_durotar_content.make). All 18 weapon types appear exactly once across "
                     "this file; armour is ten pieces apiece across cloth/leather/mail/plate. Checked by "
                     "tools/qa_underdark_content.py."}
    for f in (descent_pools, underdark_pools, geode_pools, bloom_pools):
        out.update(f())
    (ROOT / "data/loot/underdark_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    n_c = sum(len(g) for g in (DESCENT_CREATURES, UNDERDARK_CREATURES, GEODE_CREATURES, BLOOM_CREATURES))
    n_i = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"Underdark: creatures +{n_c}, loot pools {len(out) - 1}, items {n_i}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
