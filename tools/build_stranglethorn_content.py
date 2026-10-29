#!/usr/bin/env python3
"""Stranglethorn open-world content pass (2026-10-29). Idempotent.

  PYTHONPATH=. python3 tools/build_stranglethorn_content.py
  cd tools && python3 generate_creatures.py      # after any kit edit (kits: monster_kits.STRANGLETHORN_KITS)

The three jungle zones shipped today with terrain, roads, Grom'gol, Booty Bay, three caves and the
Gurbashi Arena, and NOTHING ALIVE IN THE OPEN WORLD. This is the pass that fixes that. The caves
(tools/build_stranglethorn_cave_content.py) and the arena (tools/build_gurbashi_content.py) are
somebody else's; this script never writes to a `caves` key and adds no boss to a pinned chamber.

  Northern Stranglethorn   30-34   you arrive by zeppelin into Grom'gol and the only way out is south
  Central Stranglethorn    33-37   no town in it at all. You walk the Vine Road or you do not get south
  Southern Stranglethorn   38-42   the cape, where the jungle runs out and the sea takes the rest

LEVEL LADDER. It sorts on ONE axis and that axis is the road, because the road is the only thing in
this jungle that goes anywhere. Grom'gol at the top, Booty Bay at the bottom, and the ladder is simply
how far down the Vine Road and the Cape Road you have walked. What changes with distance is not the
difficulty so much as WHO IS STANDING ON THE GROUND: at the top the trolls are a remnant keeping a
stair, in the middle they are a going concern selling tickets, and at the bottom they are fanatics
trying to bail out a city.

  NORTHERN STRANGLETHORN
    The Vine Road        30-32   the whole zone's spine. Jungle animals and whatever the road disturbs
    The Green Cut        31-33   the one cut line east off Grom'gol's gate. Apes have taken the gap
    Mistvale Lagoon      31-33   brackish, mangrove, crocolisk. Nothing here is in a hurry
    Zul'Marosh Steps     31-34   the stair-temple on the crag, and the trolls still holding its top
    Rotvine Fen          32-34   downhill of the Hollow's outflow, and the water arrives wrong

  CENTRAL STRANGLETHORN
    The Vine Road        33-35   same road, and the only zone where it is the whole of the accommodation
    The Snapjaw Marsh    34-36   standing brackish water, rotted trunks, and what the marsh is named for
    Veilfall Basin       34-36   the river goes over a lip into a plunge pool. Prettiest corner, and busy
    Gurbashi Flats       34-37   bare trampled dirt, the arena gate, and the people who run the gate
    Mosh'Ogg Shelf       35-37   ogre country on broken high ground with exactly one road up it

  SOUTHERN STRANGLETHORN
    The Cape Road        38-40   the road's last leg, sea on your right, Booty Bay at the end of it
    Zul'Kundaraz         39-41   the biggest troll ruin in the jungle, and it has been reoccupied
    The Drowned Coast    39-42   shallow water standing over cut stone, and the naga sitting on it
    Bloodsail Shallows   40-42   beach, bars, three wrecks, and whoever put them there
    Jaguero Spit         40-42   a sand spit past the cape. Whatever is out there got there and stayed

SIX POPULATIONS. The jungle's argument is the first one and the other five hang off it.

  THE TROLLS       the throughline, and the point is that they are NOT ONE PEOPLE. Zul'Marosh in the
                   north, the Gurbashi in the middle, Zul'Kundaraz in the south: three generations of
                   the same stonework, three hundred miles of the same jungle, and three completely
                   different answers to having lost an empire.
                     ZUL'MAROSH are a remnant. The stair-temple's bottom is under water (the Hollow),
                   so they hold the top of it, and they are holding it with fewer people every year.
                   Their one named rare is "the Last Stairkeeper" and the word is not decoration.
                     THE GURBASHI did not lose anything, because they stopped being a war band and
                   became a business. They run the arena, they take bets, they ship beasts in crates,
                   and the gate crew are not guarding a holy site - they are checking whether your name
                   is on the board. They fight you for the same reason a dock crew fights you.
                     THE KUNDARAZ RETURNED came BACK. Nobody had lived in Zul'Kundaraz for generations;
                   these are trolls who walked into the biggest ruin on the cape and started cutting
                   vine off the courts, and the sea is a span further up the terraces every season. The
                   naga on the drowned coast are not an enemy they chose. They are the tide, with arms.
  THE JUNGLE       raptors, panthers, serpents, boars, apes. The natives, the only things down here
                   that are where they belong, and the only ones with nothing to say about any of it.
                   They run the length of all three zones and they get bigger going south, which is the
                   only part of this ladder that is about nothing but distance from the harbour.
  THE OGRES        Mosh'Ogg, on the shelf, which has mesas all round it and one road up. They have kept
                   it because of the road, not because of anything they did, and they know it.
  THE WATER        crocolisks and mangrove things in Mistvale Lagoon and the Snapjaw Marsh. Two brackish
                   places at opposite ends of the jungle with the same list of problems.
  THE ROT          Rotvine Fen, and this one is a consequence rather than a population: the Hollow's
                   outflow comes downhill into the fen and arrives wrong, so the fen is the only part
                   of the jungle where the animals are a symptom.
  THE SEA'S PEOPLE the Bloodsail in the shallows and the naga on the drowned terraces. Both of them are
                   on the harbour's water, which is why both of them are in the Booty Bay Authority's
                   kill_rep and the jaguar on the spit is not.

NAMED RARES  seven, roughly one per two subzones, weight 0 in every table they appear in, and NEVER
             quested (standing rule). Their pools are this pass's whole loot budget.

LOOT  ONE item per kill from the rare's own pool of 4; item_level = creature level + 3.
      BUDGET FIXED UP FRONT across the seven pools: SIX weapons of SIX DIFFERENT types with at least
      TWO caster weapons, TWENTY armour pieces at FIVE APIECE across cloth/leather/mail/plate, TWO
      accessories, and a casting share of 40-60%. audit() fails the build rather than letting that
      drift toward a melee dump, which is what the Aspen pass shipped before anyone was checking.
      NO MAGIC-RESISTANCE GEAR ANYWHERE IN THIS PASS: the deepest thing here is level 42 and the floor
      for resistance is 45, so audit() rejects any resistance stat outright.
      NO CRAFTING MATERIAL AND NO GATHERING NODES: every item is an equippable, audit() checks it, and
      this script does not go near data/gathering/node_pools.json.

FACTIONS  fills data/factions/factions.json -> booty_bay_authority.kill_rep.creatures, which shipped
          empty with a comment saying what belongs in it. Bloodsail and naga only. No other faction is
          touched by this script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

#: Weapon families a caster actually wants in hand. Used by audit() so "six weapons" cannot quietly
#: mean six ways to hit something with a stick.
CASTER_WEAPONS = {"staff", "wand", "tome", "idol", "libram", "totem"}

#: Equip slots. audit() checks every item has one, which is how "no crafting material in this pass"
#: becomes a check rather than a promise.
EQUIP_SLOTS = {"head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet",
               "main_hand", "off_hand", "ranged", "ring", "trinket"}

CREATURES = {
    # =====================================================================================
    # NORTHERN STRANGLETHORN 30-34
    # =====================================================================================
    # ---- the jungle. These are the baseline the whole pass is measured against ----------
    "Vinecrest Raptor": C("beast_fast", 30, 32, "vinecrest_raptor"),
    "Greenpelt Panther": C("beast_fast", 30, 32, "greenpelt_panther"),
    "Rootgrubber Boar": C("beast_basic", 30, 31, "rootgrubber_boar"),
    "Coilvine Python": C("beast_fast", 31, 33, "coilvine_python"),
    "Thornback Ape": C("beast_large", 31, 33, "thornback_ape"),

    # ---- Mistvale Lagoon: brackish, slow, and everything in it waits ---------------------
    "Mistvale Crocolisk": C("aquatic_basic", 31, 33, "mistvale_crocolisk"),
    "Mangrove Stiltstalker": C("beast_fast", 31, 32, "mangrove_stiltstalker"),

    # ---- ZUL'MAROSH: a remnant holding the top of a stair whose bottom is under water ----
    "Zul'Marosh Stonehand": C("humanoid_warrior", 30, 32, "zulmarosh_stonehand"),
    "Zul'Marosh Stairwarden": C("humanoid_warrior", 31, 33, "zulmarosh_stairwarden"),
    "Zul'Marosh Vinespeaker": C("humanoid_caster", 32, 34, "zulmarosh_vinespeaker"),

    # ---- Rotvine Fen: downhill of the Hollow's outflow, and a symptom rather than a people
    "Bloatspawn Toad": C("beast_basic", 31, 33, "bloatspawn_toad"),
    "Fenrot Creeper": C("beast_large", 32, 34, "fenrot_creeper"),
    "Sourwater Ooze": C("elemental_bruiser", 32, 34, "sourwater_ooze"),

    # =====================================================================================
    # CENTRAL STRANGLETHORN 33-37
    # =====================================================================================
    # ---- the jungle again, a size up -----------------------------------------------------
    "Bloodvine Raptor": C("beast_fast", 33, 35, "bloodvine_raptor"),
    "Nightpelt Panther": C("beast_fast", 34, 36, "nightpelt_panther"),
    "Greenwater Adder": C("beast_fast", 33, 35, "greenwater_adder"),
    "Drumhide Gorilla": C("beast_large", 34, 36, "drumhide_gorilla"),

    # ---- The Snapjaw Marsh: the other brackish end of the jungle -------------------------
    "Snapjaw Crocolisk": C("aquatic_basic", 34, 36, "snapjaw_crocolisk"),
    "Snapjaw Leechswarm": C("vermin_swarm", 33, 35, "snapjaw_leechswarm"),

    # ---- THE GURBASHI: a going concern. Gate crew, drovers and the drums -----------------
    "Gurbashi Gatekeeper": C("humanoid_warrior", 34, 36, "gurbashi_gatekeeper"),
    "Gurbashi Beast-Drover": C("humanoid_warrior", 34, 36, "gurbashi_beast_drover"),
    "Gurbashi Drum-Caller": C("humanoid_caster", 35, 37, "gurbashi_drum_caller"),

    # ---- MOSH'OGG: they kept the shelf because of the one road up it ---------------------
    "Mosh'Ogg Brute": C("humanoid_warrior", 34, 36, "moshogg_brute"),
    "Mosh'Ogg Rockthrower": C("humanoid_ranged", 34, 36, "moshogg_rockthrower"),
    "Mosh'Ogg Mauler": C("humanoid_warrior", 35, 37, "moshogg_mauler"),
    "Mosh'Ogg Spellgorger": C("humanoid_caster", 35, 37, "moshogg_spellgorger"),

    # =====================================================================================
    # SOUTHERN STRANGLETHORN 38-42
    # =====================================================================================
    # ---- the jungle, running out ---------------------------------------------------------
    "Capecrest Raptor": C("beast_fast", 38, 40, "capecrest_raptor"),
    "Blackpelt Panther": C("beast_fast", 38, 40, "blackpelt_panther"),
    "Thicketbreaker Boar": C("beast_large", 38, 40, "thicketbreaker_boar"),
    "Stonecourt Gorilla": C("beast_large", 39, 41, "stonecourt_gorilla"),

    # ---- THE KUNDARAZ RETURNED: trolls who walked back into the biggest ruin on the cape -
    "Kundaraz Vinecutter": C("humanoid_warrior", 38, 40, "kundaraz_vinecutter"),
    "Kundaraz Stoneshaper": C("humanoid_caster", 39, 41, "kundaraz_stoneshaper"),
    "Kundaraz Terrace-Watch": C("humanoid_ranged", 39, 41, "kundaraz_terrace_watch"),

    # ---- the naga on the drowned terraces the Authority would like back ------------------
    "Saltscale Salvager": C("humanoid_warrior", 38, 40, "saltscale_salvager"),
    "Saltscale Reaver": C("humanoid_warrior", 40, 42, "saltscale_reaver"),
    "Saltscale Siren": C("humanoid_caster", 40, 42, "saltscale_siren"),

    # ---- the Bloodsail, on the harbour's water --------------------------------------------
    "Bloodsail Swab": C("humanoid_warrior", 38, 39, "bloodsail_swab"),
    "Bloodsail Cannoneer": C("humanoid_ranged", 39, 41, "bloodsail_cannoneer"),
    "Bloodsail Bosun": C("humanoid_warrior", 40, 42, "bloodsail_bosun"),

    # ---- Jaguero Spit: a sand bar with arena cargo loose on it ----------------------------
    "Spit Scavenger Crab": C("aquatic_basic", 38, 40, "spit_scavenger_crab"),
    "Pit-Stock Raptor": C("beast_fast", 40, 42, "pit_stock_raptor"),

    # =====================================================================================
    # NAMED RARES. weight 0 everywhere, boss multipliers, and NEVER quest targets.
    # Their kits put every buff and debuff on a damage rider, because Monster.choose_action
    # refuses to let a boss spend a turn on a bare self-buff while it has an attack - a
    # standalone "Thrash" on a rare is an ability that never once fires in play.
    # =====================================================================================
    "Mistvale Longjaw": C("beast_large", 33, 33, "mistvale_longjaw", True, 1.7),
    "Ka'tesh the Last Stairkeeper": C("humanoid_caster", 34, 34, "katesh_last_stairkeeper", True, 1.8),
    "Gorbuk the Shelf-King": C("humanoid_warrior", 36, 36, "gorbuk_shelf_king", True, 1.8),
    "Drumhide": C("beast_large", 37, 37, "drumhide", True, 1.7),
    "The Cargo": C("beast_fast", 40, 40, "the_cargo", True, 1.7),
    "Ssaren the Salvage-Taker": C("humanoid_caster", 41, 41, "ssaren_salvage_taker", True, 1.8),
    "Captain Orlee Vantch": C("humanoid_warrior", 42, 42, "captain_orlee_vantch", True, 1.9),
}

LEVELS = {"Mistvale Longjaw": 33, "Ka'tesh the Last Stairkeeper": 34, "Gorbuk the Shelf-King": 36,
          "Drumhide": 37, "The Cargo": 40, "Ssaren the Salvage-Taker": 41,
          "Captain Orlee Vantch": 42}

ZONES = {
    # -------------------------------------------------------------------------------------------
    # NORTHERN STRANGLETHORN. open_zone is the jungle itself, because the jungle IS the zone - the
    # trolls are a corner of it, not the background. All four of the north's rares sit at 0 here so
    # a rare can turn up on the road rather than only in its own box.
    # -------------------------------------------------------------------------------------------
    "Northern Stranglethorn": {
        "open_zone": {
            "name": "Northern Stranglethorn",
            "creatures": {"Vinecrest Raptor": 5, "Greenpelt Panther": 4, "Rootgrubber Boar": 3,
                          "Coilvine Python": 3, "Thornback Ape": 2, "Mistvale Crocolisk": 2,
                          "Zul'Marosh Stonehand": 2,
                          "Mistvale Longjaw": 0, "Ka'tesh the Last Stairkeeper": 0},
        },
        "subzones": {
            # the spine. Grom'gol's gate to the south seam, and what the road disturbs
            "The Vine Road": {
                "name": "The Vine Road",
                "creatures": {"Vinecrest Raptor": 5, "Greenpelt Panther": 4, "Rootgrubber Boar": 3,
                              "Coilvine Python": 3, "Zul'Marosh Stonehand": 2},
            },
            # the one cut line east off the gate. A gap in solid canopy, and the apes have it
            "The Green Cut": {
                "name": "The Green Cut",
                "creatures": {"Thornback Ape": 5, "Coilvine Python": 4, "Greenpelt Panther": 3,
                              "Vinecrest Raptor": 2},
            },
            # mangrove and standing brackish water. Nothing in here is in a hurry
            "Mistvale Lagoon": {
                "name": "Mistvale Lagoon",
                "creatures": {"Mistvale Crocolisk": 5, "Mangrove Stiltstalker": 4,
                              "Coilvine Python": 3, "Bloatspawn Toad": 2,
                              "Mistvale Longjaw": 0},
            },
            # the stair-temple. The trolls hold the top because the bottom is the Hollow's water
            "Zul'Marosh Steps": {
                "name": "Zul'Marosh Steps",
                "creatures": {"Zul'Marosh Stairwarden": 5, "Zul'Marosh Stonehand": 4,
                              "Zul'Marosh Vinespeaker": 3, "Thornback Ape": 2,
                              "Ka'tesh the Last Stairkeeper": 0},
            },
            # downhill of the outflow. The animals here are a symptom, not a population
            "Rotvine Fen": {
                "name": "Rotvine Fen",
                "creatures": {"Fenrot Creeper": 5, "Bloatspawn Toad": 4, "Sourwater Ooze": 3,
                              "Zul'Marosh Vinespeaker": 2,
                              "Ka'tesh the Last Stairkeeper": 0},
            },
        },
    },

    # -------------------------------------------------------------------------------------------
    # CENTRAL STRANGLETHORN. The only zone with no bed in it, so the open_zone table is weighted
    # hard toward things that are ON THE ROAD and the two organised peoples stay in their corners.
    # -------------------------------------------------------------------------------------------
    "Central Stranglethorn": {
        "open_zone": {
            "name": "Central Stranglethorn",
            "creatures": {"Bloodvine Raptor": 5, "Nightpelt Panther": 4, "Greenwater Adder": 3,
                          "Drumhide Gorilla": 3, "Snapjaw Crocolisk": 2,
                          "Gurbashi Beast-Drover": 2,
                          "Gorbuk the Shelf-King": 0, "Drumhide": 0},
        },
        "subzones": {
            "The Vine Road": {
                "name": "The Vine Road",
                "creatures": {"Bloodvine Raptor": 5, "Nightpelt Panther": 4, "Greenwater Adder": 3,
                              "Gurbashi Beast-Drover": 3, "Drumhide Gorilla": 2},
            },
            # brackish standing water and rotted trunks, and the thing the marsh is named for
            "The Snapjaw Marsh": {
                "name": "The Snapjaw Marsh",
                "creatures": {"Snapjaw Crocolisk": 5, "Snapjaw Leechswarm": 4,
                              "Greenwater Adder": 3, "Bloodvine Raptor": 2},
            },
            # the river comes off the shelf, runs west and goes over a lip. Busiest water in the zone
            "Veilfall Basin": {
                "name": "Veilfall Basin",
                "creatures": {"Greenwater Adder": 4, "Drumhide Gorilla": 4, "Nightpelt Panther": 3,
                              "Snapjaw Leechswarm": 2,
                              "Drumhide": 0},
            },
            # bare trampled dirt, the arena gate, and the crew who check the board for your name
            "Gurbashi Flats": {
                "name": "Gurbashi Flats",
                "creatures": {"Gurbashi Gatekeeper": 5, "Gurbashi Beast-Drover": 4,
                              "Gurbashi Drum-Caller": 3, "Bloodvine Raptor": 2,
                              "Drumhide": 0},
            },
            # broken high ground, mesas all round it, one road up
            "Mosh'Ogg Shelf": {
                "name": "Mosh'Ogg Shelf",
                "creatures": {"Mosh'Ogg Brute": 5, "Mosh'Ogg Rockthrower": 4, "Mosh'Ogg Mauler": 3,
                              "Mosh'Ogg Spellgorger": 3, "Nightpelt Panther": 2,
                              "Gorbuk the Shelf-King": 0},
            },
        },
    },

    # -------------------------------------------------------------------------------------------
    # SOUTHERN STRANGLETHORN. Four of the five subzones are somebody's territory and only the road
    # is still plain jungle, which is the read for a cape: the land runs out and the people crowd.
    # -------------------------------------------------------------------------------------------
    "Southern Stranglethorn": {
        "open_zone": {
            "name": "Southern Stranglethorn",
            "creatures": {"Capecrest Raptor": 5, "Blackpelt Panther": 4, "Thicketbreaker Boar": 3,
                          "Stonecourt Gorilla": 2, "Kundaraz Vinecutter": 2,
                          "Bloodsail Swab": 2,
                          "The Cargo": 0, "Ssaren the Salvage-Taker": 0,
                          "Captain Orlee Vantch": 0},
        },
        "subzones": {
            # the road's last leg, with the sea on your right the whole way down
            "The Cape Road": {
                "name": "The Cape Road",
                "creatures": {"Capecrest Raptor": 5, "Blackpelt Panther": 4,
                              "Thicketbreaker Boar": 3, "Kundaraz Vinecutter": 2,
                              "Bloodsail Swab": 2,
                              "Captain Orlee Vantch": 0},
            },
            # the biggest troll ruin in the jungle, reoccupied, and losing a terrace a season
            "Zul'Kundaraz": {
                "name": "Zul'Kundaraz",
                "creatures": {"Kundaraz Vinecutter": 5, "Kundaraz Stoneshaper": 4,
                              "Kundaraz Terrace-Watch": 3, "Stonecourt Gorilla": 3,
                              "Ssaren the Salvage-Taker": 0},
            },
            # shallow water standing over cut stone, and the people who moved in with the sea
            "The Drowned Coast": {
                "name": "The Drowned Coast",
                "creatures": {"Saltscale Salvager": 5, "Saltscale Reaver": 4, "Saltscale Siren": 3,
                              "Kundaraz Terrace-Watch": 2,
                              "Ssaren the Salvage-Taker": 0},
            },
            # beach, bars, three wrecks, and whoever put them there
            "Bloodsail Shallows": {
                "name": "Bloodsail Shallows",
                "creatures": {"Bloodsail Swab": 5, "Bloodsail Cannoneer": 4, "Bloodsail Bosun": 3,
                              "Spit Scavenger Crab": 2,
                              "Captain Orlee Vantch": 0},
            },
            # the walk out is the walk back, and the only things on it came by water
            "Jaguero Spit": {
                "name": "Jaguero Spit",
                "creatures": {"Pit-Stock Raptor": 5, "Spit Scavenger Crab": 4,
                              "Blackpelt Panther": 2,
                              "The Cargo": 0},
            },
        },
    },
}

#: What costs the harbour money, per the comment the faction shipped with. Bloodsail on the water
#: first, then the naga sitting on terraces the Authority would like to salvage. Ordinary 12-18 on the
#: scale the other factions use (8-20), the naga rare 120, and the Bloodsail captain more than anyone
#: because she is the thing the whole comment is about: a hull that does not arrive.
#: NOTHING from the jungle is in here. A raptor has never cost anyone a cargo.
AUTHORITY_KILL_REP = {
    "Bloodsail Swab": 12,
    "Bloodsail Cannoneer": 15,
    "Bloodsail Bosun": 18,
    "Saltscale Salvager": 12,
    "Saltscale Reaver": 15,
    "Saltscale Siren": 15,
    "Ssaren the Salvage-Taker": 120,
    "Captain Orlee Vantch": 160,
}


def pools():
    """Seven pools of four. The spread is declared in the module docstring and enforced by audit().

    No pool is a complete set for one character, and no two adjacent pools lead on the same thing -
    walking the road from Grom'gol to Booty Bay should pay out to a different party member each time
    something rare actually turns up.
    """
    return {
        # ---- Mistvale Lagoon, L33 -> ilvl 36. dagger + leather/mail/plate ---------------------
        "Mistvale Longjaw": [
            mk("Longjaw's Tooth-Knife", "main_hand", "of the Assassin", 36,
               "Pulled from the front of the jaw, where the old ones go hollow.",
               weapon_type="dagger"),
            mk("Mangrove-Wader's Boots", "feet", "of the Monkey", 36,
               "Laced high. The lagoon floor is mud to the shin and then it is roots.",
               armor_type="leather"),
            mk("Brackwater Hauberk", "chest", "of the Eagle", 36,
               "Salt and fresh water both, which is harder on mail than either one alone.",
               armor_type="mail"),
            mk("Still-Water Greaves", "legs", "of the Bear", 36,
               "Nothing in the lagoon moves fast. That is not the same as nothing moving.",
               armor_type="plate"),
        ],
        # ---- Zul'Marosh Steps, L34 -> ilvl 37. staff (caster) + cloth/cloth/mail --------------
        "Ka'tesh the Last Stairkeeper": [
            mk("Stairkeeper's Vinestaff", "main_hand", "of the Owl", 37,
               "Cut from the vine that is pulling his temple apart. He uses it anyway.",
               weapon_type="staff"),
            mk("Robes of the Thinning Watch", "chest", "of the Sorcerer", 37,
               "Cut for a man with a wider back than he has now.", armor_type="cloth"),
            mk("Last Keeper's Cowl", "head", "of the Prophet", 37,
               "There were nine of these made. He is wearing the only one still above water.",
               armor_type="cloth"),
            mk("Crag-Stair Spaulders", "shoulder", "of the Eagle", 37,
               "The stair goes up the crag in forty turns and he knows every one of them.",
               armor_type="mail"),
        ],
        # ---- Mosh'Ogg Shelf, L36 -> ilvl 39. mace_2h + plate/plate/leather -------------------
        "Gorbuk the Shelf-King": [
            mk("Shelf-King's Roadbreaker", "main_hand", "of the Bear", 39,
               "One road comes up the shelf. He has stood at the top of it for eleven years.",
               weapon_type="mace_2h"),
            mk("Mosh'Ogg Slab Breastplate", "chest", "of the Champion", 39,
               "Three plates where there should be one, lapped and bound with cable.",
               armor_type="plate"),
            mk("One-Road Legplates", "legs", "of the Soldier", 39,
               "He did not take the shelf. He was on it when everyone else left.",
               armor_type="plate"),
            mk("Shelf-Climber's Grips", "hands", "of the Monkey", 39,
               "Ogre-made for an ogre hand, so there is room in them for two of yours.",
               armor_type="leather"),
        ],
        # ---- Gurbashi Flats / Veilfall Basin, L37 -> ilvl 40. accessory + leather/mail/plate --
        "Drumhide": [
            mk("The Uncrated Tally", "neck", "of the Gorilla", 40,
               "A drover's cord with eleven knots on it and no twelfth.",
               ),
            mk("Drum-Skin Jerkin", "chest", "of the Monkey", 40,
               "The arena buys hide by the hand-span. This much of it never got to the arena.",
               armor_type="leather"),
            mk("Drover's Broken Chain", "waist", "of the Eagle", 40,
               "Opened outward. Whatever was in it did not pick the lock.", armor_type="mail"),
            mk("Crate-Hauler's Sabatons", "feet", "of the Bear", 40,
               "The Flats are bare dirt because of what gets dragged across them.",
               armor_type="plate"),
        ],
        # ---- Jaguero Spit, L40 -> ilvl 43. fist_weapon + leather/cloth/mail ------------------
        "The Cargo": [
            mk("Manifest-Line Claw", "main_hand", "of the Tiger", 43,
               "The entry read: one crate, livestock, unmarked. The Authority still has the page.",
               weapon_type="fist_weapon"),
            mk("Spit-Walker's Vest", "chest", "of the Bandit", 43,
               "Sand gets into the stitching and stays there until the garment gives up.",
               armor_type="leather"),
            mk("Hood of the Long Walk Back", "head", "of the Owl", 43,
               "You can see the whole spit from the root of it. That is the trouble with a spit.",
               armor_type="cloth"),
            mk("Driftwood-Bound Bracers", "wrist", "of the Falcon", 43,
               "Hull timber, cut down twice, by two people who did not know each other.",
               armor_type="mail"),
        ],
        # ---- The Drowned Coast, L41 -> ilvl 44. wand (caster) + cloth/leather/plate ----------
        "Ssaren the Salvage-Taker": [
            mk("Salvage-Taker's Rod", "main_hand", "of the Invoker", 44,
               "Cut stone comes up off the terraces in pieces and she decides which pieces.",
               weapon_type="wand"),
            mk("Shallows-Sitter's Wrap", "chest", "of the Archmage", 44,
               "Never dry, never quite wet. Whoever wove it knew which it would be.",
               armor_type="cloth"),
            mk("Terrace-Diver's Mantle", "shoulder", "of the Wolf", 44,
               "Four spans down is the second court. Six is the third. Nobody goes to the fourth.",
               armor_type="leather"),
            mk("Flooded Court Legplates", "legs", "of the Juggernaut", 44,
               "Standing in water to the knee all day does to plate what you would expect.",
               armor_type="plate"),
        ],
        # ---- Bloodsail Shallows, L42 -> ilvl 45. sword_1h + accessory + cloth/mail -----------
        "Captain Orlee Vantch": [
            mk("Vantch's Shallows Cutlass", "main_hand", "of the Gladiator", 45,
               "Short in the blade. She has never fought anybody on open deck in her life.",
               weapon_type="sword_1h"),
            mk("Three-Wrecks Signet", "ring", "of the Mind's Eye", 45,
               "She put all three on the bars inside a season and the harbour counted every one.",
               ),
            mk("Bosun's Weather Coat", "back", "of the Seer", 45,
               "Waxed, patched, and warmer than anything else on that beach.",
               armor_type="cloth"),
            mk("Bar-Pilot's Coif", "head", "of the Marksman", 45,
               "She knows where the sand is. That is the entire trick and it is worth a ship.",
               armor_type="mail"),
        ],
    }


def audit(out, levels):
    """FAIL THE BUILD rather than ship a lopsided jungle.

    Seven rares spread over fifteen subzones means the player meets maybe two of them on a run from
    Grom'gol to Booty Bay, so the spread IS the reward structure - one plate-heavy pool too many and
    half the party walks the whole jungle for nothing. Same shape as the Southern Thousand Needles
    audit(), plus the two standing rules that bite at this band and a crafting-material check.
    """
    pools_only = {k: v for k, v in out.items() if not k.startswith("_")}
    items = [i for v in pools_only.values() for i in v]
    wt = [i["weapon_type"] for i in items if i.get("weapon_type")]
    ar = {}
    for i in items:
        if i.get("armor_type"):
            ar[i["armor_type"]] = ar.get(i["armor_type"], 0) + 1
    acc = [i for i in items if not i.get("armor_type") and not i.get("weapon_type")]
    # mk() bakes the suffix into primary_stats and keeps no suffix key - reading a "suffix" key here
    # scored a flat 0 on the Drowning Floor pass and would have waved a melee dump straight through.
    casting = sum(1 for i in items if {"intellect", "spirit"} & set(i.get("primary_stats", {})))
    errs = []

    if len(pools_only) != 7:
        errs.append(f"want 7 pools (one per named rare), got {len(pools_only)}")
    for k, v in pools_only.items():
        if len(v) != 4:
            errs.append(f"{k}: pool has {len(v)} items, want 4")
        if k not in levels:
            errs.append(f"{k}: no declared level")

    if len(wt) != 6 or len(set(wt)) != 6:
        errs.append(f"want 6 weapons of 6 different types, got {wt}")
    if len(set(wt) & CASTER_WEAPONS) < 2:
        errs.append(f"want at least 2 caster weapons, got {sorted(set(wt) & CASTER_WEAPONS)}")
    if sorted(ar.values()) != [5, 5, 5, 5] or set(ar) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour not 5 apiece across four classes: {ar}")
    if len(acc) != 2:
        errs.append(f"want 2 accessories (no armour class, no weapon), got {len(acc)}")

    # NO POOL IS A SET. Four pieces of one armour class in one pool is a lopsided payout even when
    # the zone-wide totals come out level, which is exactly how the Aspen pass passed its own audit.
    for k, v in pools_only.items():
        counts = {}
        for i in v:
            if i.get("armor_type"):
                counts[i["armor_type"]] = counts.get(i["armor_type"], 0) + 1
        if max(counts.values(), default=0) > 2:
            errs.append(f"{k}: {max(counts.values())} pieces of one armour class in one pool ({counts})")

    for k, v in pools_only.items():
        for i in v:
            if i["item_level"] != levels[k] + 3:
                errs.append(f"{i['name']}: ilvl {i['item_level']} != {levels[k]} + 3")

    # STANDING RULE: no magic-resistance gear below level 45, and Southern Stranglethorn tops out at
    # 42, so NOTHING in this pass may carry a resistance stat at all.
    for i in items:
        stats = set(i.get("primary_stats", {})) | set(i.get("secondary_stats", {}))
        res = sorted(s for s in stats if "resist" in s)
        if res:
            errs.append(f"{i['name']}: magic-resistance gear below level 45 ({res})")

    # STANDING RULE: no crafting material, and no gathering material of any tier. Every item in this
    # pass is an equippable, which is a check rather than a promise.
    for i in items:
        if i.get("slot") not in EQUIP_SLOTS:
            errs.append(f"{i['name']}: slot {i.get('slot')!r} is not an equip slot")
        for key in ("material", "reagent", "stack_size", "tradeskill", "gather_tier"):
            if key in i:
                errs.append(f"{i['name']}: carries crafting/gathering key {key!r}")

    if not 0.40 <= casting / len(items) <= 0.60:
        errs.append(f"casting share {casting}/{len(items)} outside 40-60%")

    if errs:
        raise SystemExit("LOOT BUDGET FAILED:\n  " + "\n  ".join(errs))
    print(f"  loot ok: {len(items)} items across {len(pools_only)} named rares")
    print(f"    weapons      {wt}")
    print(f"    casters      {sorted(set(wt) & CASTER_WEAPONS)}")
    print(f"    armour       {ar}   accessories {len(acc)}")
    print(f"    casting      {casting}/{len(items)} ({casting / len(items):.0%})")
    print(f"    resistance   0 pieces (rule: none below level 45)")
    print(f"    materials    0 items (rule: no crafting or gathering material in this pass)")


def check_rosters():
    """Every name in every table must be a creature this script defines, or already exist.

    An encounter table referencing a creature that is not in creatures.json is a spawn that silently
    returns None - the subzone just feels empty, which is the exact bug this whole pass exists to fix.
    """
    known = set(CREATURES) | set(json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"])
    errs = []
    for zone, z in ZONES.items():
        tables = [("open_zone", z["open_zone"])] + list(z["subzones"].items())
        for key, t in tables:
            for n in t["creatures"]:
                if n not in known:
                    errs.append(f"{zone} / {key}: unknown creature {n!r}")
            if key != "open_zone" and sum(t["creatures"].values()) <= 0:
                errs.append(f"{zone} / {key}: no non-rare weight, the table would fall through")
        # Rares are weight 0 wherever they appear, in every table, with no exceptions.
        for key, t in tables:
            for n, w in t["creatures"].items():
                if CREATURES.get(n, {}).get("is_boss") and w != 0:
                    errs.append(f"{zone} / {key}: rare {n!r} has weight {w}, must be 0")
    for n in AUTHORITY_KILL_REP:
        if n not in CREATURES:
            errs.append(f"booty_bay_authority kill_rep names {n!r}, which this pass does not create")
    # The harbour pays for hulls, not for wildlife (the faction's own comment).
    for n in AUTHORITY_KILL_REP:
        if not (n.startswith("Bloodsail") or n.startswith("Saltscale")
                or n in ("Ssaren the Salvage-Taker", "Captain Orlee Vantch")):
            errs.append(f"booty_bay_authority kill_rep: {n!r} is not Bloodsail or naga")
    if errs:
        raise SystemExit("ROSTER CHECK FAILED:\n  " + "\n  ".join(errs))
    n_sub = sum(len(z["subzones"]) for z in ZONES.values())
    print(f"  rosters ok: {len(ZONES)} zones, {n_sub} subzones, {len(CREATURES)} creatures, "
          f"{sum(1 for c in CREATURES.values() if c['is_boss'])} named rares")


def main():
    check_rosters()

    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    # NAME COLLISIONS ARE SILENT DATA LOSS - dict.update() replaced an existing boss on the Drowning
    # Floor pass with no error at all. Two other agents wrote Stranglethorn creatures today (the three
    # caves and the arena); forty-seven names is not worth trusting to memory.
    clash = [n for n in CREATURES if n in cdata["creatures"]
             and cdata["creatures"][n].get("ability_kit") != CREATURES[n].get("ability_kit")]
    if clash:
        raise SystemExit(f"CREATURE NAME COLLISION (would overwrite existing): {clash}")
    cdata["creatures"].update(CREATURES)

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())
    for zone, z in ZONES.items():
        # setdefault, and only the two keys this script owns: all three zone entries already exist and
        # already carry a `caves` key written by tools/build_stranglethorn_cave_content.py. Assigning
        # a fresh dict here would delete Rotvine Hollow, the Veilfall and the Drowned Shrine outright.
        tgt = edata["zones"].setdefault(zone, {})
        tgt["open_zone"] = z["open_zone"]
        tgt["subzones"] = z["subzones"]

    fp = ROOT / "data/factions/factions.json"
    fdata = json.loads(fp.read_text())
    kr = fdata["factions"]["booty_bay_authority"]["kill_rep"]
    kr["creatures"] = dict(AUTHORITY_KILL_REP)       # the only faction this script writes to

    out = {"_notes": "Stranglethorn open-world named-rare loot (2026-10-29). ONE item drops per kill "
                     "from the rare's pool of four. item_level = creature level + 3. Budget checked by "
                     "audit() in tools/build_stranglethorn_content.py. Rares are never quested, and "
                     "nothing here carries magic resistance (the floor for that is level 45) or any "
                     "crafting material."}
    out.update(pools())
    audit(out, LEVELS)

    (ROOT / "data/loot/stranglethorn_openworld_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")
    fp.write_text(json.dumps(fdata, indent=2) + "\n")
    print(f"Stranglethorn open world: creatures +{len(CREATURES)}, zones {len(ZONES)}, subzones "
          f"{sum(len(z['subzones']) for z in ZONES.values())}, loot pools {len(out) - 1}, items "
          f"{sum(len(v) for k, v in out.items() if not k.startswith('_'))}, "
          f"Authority kill_rep {len(AUTHORITY_KILL_REP)} entries")


if __name__ == "__main__":
    main()
