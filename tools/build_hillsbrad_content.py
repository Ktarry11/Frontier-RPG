#!/usr/bin/env python3
"""Hillsbrad content pass (2026-10-27). Idempotent.

  PYTHONPATH=. python3 tools/build_hillsbrad_content.py
  cd tools && python3 generate_creatures.py        # after any kit edit (kits: monster_kits.HILLSBRAD_KITS)

LEVEL LADDER
  Western Hillsbrad 20-24 (arrival): Southpoint Tower 20-22 | Hillsbrad Fields 20-23 | Foothill Pastures 21-24
                                     Azurelode Mine (outside) 21-24 | Western Strand 22-25 | Orchard 22-25
                                     Southshore 23-26 | Purgation Shore 24-26
  Azurelode Mine (cave)   23-26:     trash 23-25, Grimewick 25, Deepmuck 25, Ashlan Silvervein 26
  Dun Garok (hold)        25-28:     trash 25-27, Brannic 26, Dunmar 27, Morgrin 27, Stonewatch 28
  Eastern Hillsbrad 23-27:           Tarren Mill 23-24 | Mudsnout Hollow 23-25 | Gavin's Naze 24-26
                                     Eastern Strand 23-25 | Dun Garok Road 25-27 | Nethander Stead 25-27
                                     Durnholde Keep 25-27 | Thoradin's Wall 26-27

THREE POPULATIONS, and they fight differently on purpose. The Alliance (farmers, militia, marines) are
organised: they buff each other and grind armour down, and the farmhands are the weakest thing in the zone
because they are people defending a field, not soldiers. The Daggerspine and the drowned use brine - damage
over time and slows. The Syndicate, kobolds, gnolls and ogres are tricks and blunt force, scaling toward
Durnholde.

RULES  ONE item per kill from the creature's own pool of 4; item_level = creature level + 3; real loot
       formulas (tools/build_durotar_content.make). Named rares are is_boss with weight 0 - they roll at
       ~6% in their subzone, so any quest that wants one is paired with trash.
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
WEST_CREATURES = {
    # Hillsbrad Fields
    "Hillsbrad Farmhand": C("humanoid_warrior", 20, 22, "hillsbrad_farmhand"),
    "Hillsbrad Militiaman": C("humanoid_warrior", 21, 23, "hillsbrad_militia"),
    "Field Marshal Calder": C("humanoid_warrior", 24, 24, "field_marshal_calder", True, 1.7),
    # The Foothill Pastures
    "Highland Ram": C("beast_basic", 21, 23, "highland_ram"),
    "Mountain Yeti": C("beast_large", 22, 24, "mountain_yeti"),
    "Old Icehide": C("beast_large", 24, 24, "old_icehide", True, 1.7),
    # Azurelode approach + the mine
    "Azurelode Kobold": C("humanoid_warrior", 21, 23, "azurelode_kobold"),
    "Kobold Tunneler": C("humanoid_warrior", 22, 24, "kobold_tunneler"),
    "Syndicate Prospector": C("humanoid_rogue", 22, 24, "syndicate_prospector"),
    "Sump Lurker": C("beast_large", 23, 25, "sump_lurker"),
    "Drowned Miner": C("undead_basic", 23, 25, "drowned_miner"),
    "Overseer Ashlan Silvervein": C("humanoid_warrior", 26, 26, "ashlan_silvervein", True, 1.8),
    "Grimewick the Drowned": C("humanoid_warrior", 25, 25, "grimewick_the_drowned", True, 1.7),
    "Deepmuck": C("beast_large", 25, 25, "deepmuck", True, 1.7),
    # The Western Strand
    "Daggerspine Murloc": C("humanoid_warrior", 22, 24, "daggerspine_murloc"),
    "Daggerspine Siren": C("humanoid_caster", 23, 25, "daggerspine_siren"),
    "Bloodtide Harpooner": C("humanoid_warrior", 25, 25, "bloodtide_harpooner", True, 1.7),
    # Southshore
    "Southshore Marine": C("humanoid_warrior", 23, 26, "southshore_marine"),
    "Bosun Harlow": C("humanoid_warrior", 26, 26, "bosun_harlow", True, 1.7),
    # Purgation Shore
    "Drowned Castaway": C("undead_basic", 24, 26, "drowned_castaway"),
    "The Tidewrack": C("undead_basic", 26, 26, "the_tidewrack", True, 1.8),
    # Hillsbrad Orchard
    "Orchard Wasp": C("vermin_swarm", 22, 24, "orchard_wasp"),
    "Queen Thistlewing": C("vermin_swarm", 25, 25, "queen_thistlewing", True, 1.7),
}

EAST_CREATURES = {
    # Mudsnout Hollow
    "Mudsnout Gnoll": C("humanoid_warrior", 23, 25, "mudsnout_gnoll"),
    "Mudsnout Shaman": C("humanoid_caster", 23, 25, "mudsnout_shaman"),
    "Chief Grik": C("humanoid_warrior", 25, 25, "chief_grik", True, 1.7),
    # Gavin's Naze + Durnholde
    "Syndicate Bandit": C("humanoid_rogue", 24, 26, "syndicate_bandit"),
    "Syndicate Spellbinder": C("humanoid_caster", 24, 26, "syndicate_spellbinder"),
    "Gavin the Fence": C("humanoid_rogue", 26, 26, "gavin_the_fence", True, 1.7),
    "Durnholde Watchman": C("humanoid_warrior", 25, 27, "durnholde_watchman"),
    "Warden Stillwater": C("humanoid_warrior", 27, 27, "warden_stillwater", True, 1.9),
    # Nethander Stead
    "Nethander Ogre": C("humanoid_warrior", 25, 27, "nethander_ogre"),
    "Ogre Maul-Hand": C("humanoid_warrior", 26, 27, "ogre_maul_hand"),
    "Gorbash the Thick": C("humanoid_warrior", 27, 27, "gorbash_the_thick", True, 1.8),
    # Dun Garok Road
    "Dun Garok Rifleman": C("humanoid_warrior", 25, 27, "dun_garok_rifleman"),
    "Sergeant Ironbeard": C("humanoid_warrior", 27, 27, "sergeant_ironbeard", True, 1.8),
    # Thoradin's Wall
    "Wall-Watcher Teague": C("humanoid_warrior", 27, 27, "wall_watcher_teague", True, 1.8),
    # Dun Garok (dwarf hold)
    "Dun Garok Mountaineer": C("humanoid_warrior", 25, 27, "dun_garok_mountaineer"),
    "Dun Garok Priest": C("humanoid_caster", 25, 27, "dun_garok_priest"),
    "Stormpike Sapper": C("humanoid_rogue", 25, 27, "stormpike_sapper"),
    "Gatewarden Brannic": C("humanoid_warrior", 26, 26, "gatewarden_brannic", True, 1.7),
    "Rifle-Sergeant Dunmar": C("humanoid_warrior", 27, 27, "rifle_sergeant_dunmar", True, 1.8),
    "Shrine-Keeper Morgrin": C("humanoid_caster", 27, 27, "shrine_keeper_morgrin", True, 1.8),
    "Thane Korrin Stonewatch": C("humanoid_warrior", 28, 28, "thane_korrin_stonewatch", True, 1.9),
    # Durnholde Keep (dungeon)
    "Durnholde Hound": C("beast_fast", 26, 28, "durnholde_hound"),
    "Keep Revenant": C("undead_basic", 27, 29, "keep_revenant"),
    "Sergeant-at-Arms Varth": C("humanoid_warrior", 27, 27, "sergeant_varth", True, 1.8),
    "Houndmaster Sable": C("humanoid_warrior", 28, 28, "houndmaster_sable", True, 1.8),
    "Magister Yvaine": C("humanoid_caster", 28, 28, "magister_yvaine", True, 1.8),
    "The Keepkeeper": C("undead_basic", 29, 29, "the_keepkeeper", True, 1.9),
    "Baron Aliden Perenolde": C("humanoid_warrior", 30, 30, "baron_perenolde", True, 2.0),
}

# Creatures borrowed from neighbouring zones, re-levelled for Hillsbrad's bands.
WEST_OVERRIDES = {
    "Worg Prowler": [20, 22], "Giant Spider": [21, 23],
}
EAST_OVERRIDES = {
    "Worg Prowler": [23, 25], "Giant Spider": [24, 26],
}

# ======================================================================================================================
# ENCOUNTERS
# ======================================================================================================================
WEST_ZONE = {
    "open_zone": {
        "name": "The Hillsbrad Road",
        "creatures": {"Hillsbrad Farmhand": 4, "Highland Ram": 3, "Worg Prowler": 2, "Orchard Wasp": 2},
    },
    "subzones": {
        "Southpoint Tower": {"name": "Southpoint Tower",
                             "creatures": {"Hillsbrad Farmhand": 3, "Worg Prowler": 3, "Highland Ram": 2}},
        "Hillsbrad Fields": {"name": "Hillsbrad Fields",
                             "creatures": {"Hillsbrad Farmhand": 4, "Hillsbrad Militiaman": 4,
                                           "Orchard Wasp": 2, "Field Marshal Calder": 0}},
        "The Foothill Pastures": {"name": "The Foothill Pastures",
                                  "creatures": {"Highland Ram": 4, "Mountain Yeti": 3, "Worg Prowler": 2,
                                                "Old Icehide": 0}},
        "Azurelode Mine": {"name": "Azurelode Mine",
                           "creatures": {"Azurelode Kobold": 4, "Kobold Tunneler": 3,
                                         "Syndicate Prospector": 2, "Giant Spider": 2}},
        "The Western Strand": {"name": "The Western Strand",
                               "creatures": {"Daggerspine Murloc": 4, "Daggerspine Siren": 3,
                                             "Drowned Castaway": 2, "Bloodtide Harpooner": 0}},
        "Hillsbrad Orchard": {"name": "Hillsbrad Orchard",
                              "creatures": {"Orchard Wasp": 4, "Worg Prowler": 2, "Giant Spider": 3,
                                            "Queen Thistlewing": 0}},
        "Southshore": {"name": "Southshore",
                       "creatures": {"Southshore Marine": 5, "Hillsbrad Militiaman": 3, "Bosun Harlow": 0}},
        "Purgation Shore": {"name": "Purgation Shore",
                            "creatures": {"Drowned Castaway": 4, "Daggerspine Murloc": 2,
                                          "Sump Lurker": 2, "The Tidewrack": 0}},
    },
    "caves": {
        "Azurelode Mine": {
            "name": "Azurelode Mine",
            "creatures": {"Azurelode Kobold": 4, "Kobold Tunneler": 3, "Syndicate Prospector": 3,
                          "Sump Lurker": 3, "Drowned Miner": 3,
                          "Overseer Ashlan Silvervein": 0, "Grimewick the Drowned": 0, "Deepmuck": 0},
        },
    },
}

EAST_ZONE = {
    "open_zone": {
        "name": "The Tarren Mill Road",
        "creatures": {"Syndicate Bandit": 3, "Worg Prowler": 3, "Mudsnout Gnoll": 2, "Giant Spider": 2},
    },
    "subzones": {
        "Tarren Mill": {"name": "Tarren Mill",
                        "creatures": {"Worg Prowler": 3, "Mudsnout Gnoll": 2, "Syndicate Bandit": 2}},
        "Mudsnout Hollow": {"name": "Mudsnout Hollow",
                            "creatures": {"Mudsnout Gnoll": 5, "Mudsnout Shaman": 3, "Worg Prowler": 2,
                                          "Chief Grik": 0}},
        "Gavin's Naze": {"name": "Gavin's Naze",
                         "creatures": {"Syndicate Bandit": 4, "Syndicate Spellbinder": 3,
                                       "Gavin the Fence": 0}},
        "Durnholde Keep": {"name": "Durnholde Keep",
                           "creatures": {"Durnholde Watchman": 4, "Syndicate Bandit": 3,
                                         "Syndicate Spellbinder": 3, "Warden Stillwater": 0}},
        "Nethander Stead": {"name": "Nethander Stead",
                            "creatures": {"Nethander Ogre": 4, "Ogre Maul-Hand": 3, "Worg Prowler": 2,
                                          "Gorbash the Thick": 0}},
        "The Eastern Strand": {"name": "The Eastern Strand",
                               "creatures": {"Daggerspine Murloc": 4, "Daggerspine Siren": 2,
                                             "Drowned Castaway": 2}},
        "Dun Garok Road": {"name": "Dun Garok Road",
                           "creatures": {"Dun Garok Rifleman": 4, "Syndicate Bandit": 2,
                                         "Sergeant Ironbeard": 0}},
        "Thoradin's Wall": {"name": "Thoradin's Wall",
                            "creatures": {"Dun Garok Rifleman": 3, "Syndicate Bandit": 3,
                                          "Nethander Ogre": 2, "Wall-Watcher Teague": 0}},
    },
    "caves": {
        # A dwarf HOLD, deliberately not on the DUNGEONS list, so it inherits Eastern Hillsbrad's ore the
        # way a mountain fort should.
        "Dun Garok": {
            "name": "Dun Garok",
            "creatures": {"Dun Garok Rifleman": 5, "Dun Garok Mountaineer": 5, "Dun Garok Priest": 3,
                          "Stormpike Sapper": 3,
                          "Gatewarden Brannic": 0, "Rifle-Sergeant Dunmar": 0,
                          "Shrine-Keeper Morgrin": 0, "Thane Korrin Stonewatch": 0},
        },
        # A real Dungeon (world/zone_classification.DUNGEONS), listed here because that is where the
        # encounter loader looks for a sub-map's table - the classification is what keeps ore out of it.
        "Durnholde Keep": {
            "name": "Durnholde Keep",
            "creatures": {"Durnholde Watchman": 5, "Syndicate Bandit": 4, "Syndicate Spellbinder": 4,
                          "Durnholde Hound": 4, "Keep Revenant": 3,
                          "Sergeant-at-Arms Varth": 0, "Houndmaster Sable": 0, "Magister Yvaine": 0,
                          "The Keepkeeper": 0, "Baron Aliden Perenolde": 0},
        },
    },
}


# ======================================================================================================================
# LOOT - one drop per kill from a hand-made pool of 4. item_level = creature level + 3.
# ======================================================================================================================
def west_pools():
    return {
        "Field Marshal Calder": [
            mk("Hillsbrad Field Blade", "main_hand", "of the Soldier", 27,
               "Kept sharp for a war that never came this far south.", weapon_type="sword_1h"),
            mk("Marshal's Muster Tabard", "chest", "of the Bear", 27,
               "Stitched with the sheaf-and-sickle of the Hillsbrad fields.", armor_type="mail"),
            mk("Furrowed Oath-Ring", "ring", "of the Eagle", 27,
               "He swore on the soil. The soil kept its half."),
            mk("Militia Drill Gauntlets", "hands", "of Strength", 27,
               "Worn smooth where a hundred recruits were corrected.", armor_type="leather"),
        ],
        "Old Icehide": [
            mk("Icehide Pelt Cloak", "back", "of the Bear", 27,
               "Still cold to the touch, a long way below the snowline.", armor_type="leather"),
            mk("Yeti-Tooth Gouger", "main_hand", "of the Monkey", 27,
               "A tooth the size of a forearm, lashed to a haft.", weapon_type="dagger"),
            mk("Pasture-Walker's Boots", "feet", "of Agility", 27,
               "The ram tracks stop here. So did the shepherd.", armor_type="leather"),
            mk("Hoarfrost Charm", "neck", "of the Whale", 27,
               "Frost beads on it even in the sun."),
        ],
        "Bloodtide Harpooner": [
            mk("Daggerspine Harpoon", "main_hand", "of the Monkey", 28,
               "Barbed so it cannot be drawn back out.", weapon_type="polearm"),
            mk("Bloodtide Scale Vest", "chest", "of the Monkey", 28,
               "Scales overlapping the wrong way, like a fish turned inside out.", armor_type="leather"),
            mk("Harpooner's Coil Belt", "waist", "of Agility", 28,
               "Rope burn worn into the leather in a spiral.", armor_type="leather"),
            mk("Strand-Drowned Pearl", "neck", "of the Owl", 28,
               "Grey, and warm, which a pearl should not be."),
        ],
        "Bosun Harlow": [
            mk("Southshore Cutlass", "main_hand", "of the Soldier", 29,
               "Harbour-issue, and used far outside the harbour.", weapon_type="sword_1h"),
            mk("Bosun's Storm Coat", "chest", "of the Bear", 29,
               "Salt has gone through it so often the cloth has given up.", armor_type="mail"),
            mk("Press-Gang Shackles", "wrist", "of Strength", 29,
               "Three sets of initials filed into the inside.", armor_type="mail"),
            mk("Harbourmaster's Signet", "ring", "of the Soldier", 29,
               "Opens a strongbox nobody has found yet."),
        ],
        "The Tidewrack": [
            mk("Tidewrack Anchor-Maul", "main_hand", "of Strength", 29,
               "The chain is still attached. So is some of the ship.", weapon_type="mace_2h"),
            mk("Barnacled Plate Guard", "shoulder", "of the Bear", 29,
               "The barnacles are load-bearing now.", armor_type="plate"),
            mk("Drowned Purgation Censer", "off_hand", "of the Owl", 29,
               "Whatever it burned, the sea put out."),
            mk("Castaway's Last Ring", "ring", "of the Whale", 29,
               "Worn thin on the inside, turned and turned for years."),
        ],
        "Queen Thistlewing": [
            mk("Thistlewing Stinger", "main_hand", "of the Monkey", 28,
               "Still twitches if you hold it wrong.", weapon_type="dagger"),
            mk("Orchard Queen's Carapace", "chest", "of Agility", 28,
               "Lacquer-hard, and the colour of windfall apples.", armor_type="leather"),
            mk("Hive-Warden's Veil", "head", "of the Owl", 28,
               "Gauze and wire. It did not save the orchardist.", armor_type="cloth"),
            mk("Royal Jelly Phial", "trinket", "of the Whale", 28,
               "Sealed with wax. Faintly, it hums."),
        ],
        "Overseer Ashlan Silvervein": [
            mk("Silvervein Overseer's Mattock", "main_hand", "of Strength", 29,
               "Silver in the head, which is a waste, and he knew it.", weapon_type="mace_2h"),
            mk("Azurelode Mail Hauberk", "chest", "of the Bear", 29,
               "Rings cut from the seam itself, blue in the lamplight.", armor_type="mail"),
            mk("Sumpwater Signet", "ring", "of the Eagle", 29,
               "Tarnished black, except where a thumb rubbed it."),
            mk("Vein-Chaser's Lamp", "off_hand", "of the Owl", 29,
               "Burned until the water reached it, and a while after."),
        ],
        "Grimewick the Drowned": [
            mk("Pump-House Hammer", "main_hand", "of Strength", 28,
               "Used to beat the pumps into working. It did not work.", weapon_type="mace_1h"),
            mk("Boiler-Scalded Grips", "hands", "of the Bear", 28,
               "The leather took the heat so the hands did not. Mostly.", armor_type="leather"),
            mk("Kobold Foreman's Candle", "trinket", "of the Owl", 28,
               "He did take the candle. That was the whole problem."),
            mk("Drowned Works Pendant", "neck", "of the Whale", 28,
               "Brass, green with it, strung on boot-lace."),
        ],
        "Deepmuck": [
            mk("Silt-Caked Carapace Shield", "off_hand", "of the Bear", 28,
               "Something grew this, and something else wore it.", weapon_type="shield"),
            mk("Deepmuck Hide Leggings", "legs", "of the Monkey", 28,
               "Weeps brown water for a week after skinning.", armor_type="leather"),
            mk("Sump-Dweller's Fang", "main_hand", "of Agility", 28,
               "Serrated, and set the wrong way round.", weapon_type="dagger"),
            mk("Stillwater Charm", "trinket", "of the Whale", 28,
               "Holds a bead of water that will not evaporate."),
        ],
    }


def east_pools():
    return {
        "Chief Grik": [
            mk("Mudsnout Chieftain's Cleaver", "main_hand", "of Strength", 28,
               "Notched once for every farm between here and the hollow.", weapon_type="axe_1h"),
            mk("Hollow-Chief's Hide Mantle", "shoulder", "of the Bear", 28,
               "Gnoll work: three hides, badly cured, worn proudly.", armor_type="leather"),
            mk("Bone-Fetish Totem", "trinket", "of the Owl", 28,
               "Rattles on its own in the dark. Gnolls find this funny."),
            mk("Pack-Runner's Treads", "feet", "of Agility", 28,
               "Built for the long loping run, not for standing still.", armor_type="leather"),
        ],
        "Gavin the Fence": [
            mk("Fence's Quiet Dirk", "main_hand", "of the Monkey", 29,
               "No maker's mark. That is the selling point.", weapon_type="dagger"),
            mk("Naze Smuggler's Jerkin", "chest", "of Agility", 29,
               "More pockets than panels.", armor_type="leather"),
            mk("Stolen Dalaran Seal", "ring", "of the Owl", 29,
               "Worth more than everything else he had, and he knew it."),
            mk("Cutpurse's Clasp", "waist", "of the Monkey", 29,
               "Opens silently. Everything of his does.", armor_type="leather"),
        ],
        "Warden Stillwater": [
            mk("Durnholde Warden's Greatsword", "main_hand", "of the Soldier", 30,
               "A keep-guard's blade, kept long after the keep fell.", weapon_type="sword_2h"),
            mk("Stillwater's Breastplate", "chest", "of the Bear", 30,
               "The Syndicate's violet painted over Durnholde's grey.", armor_type="plate"),
            mk("Keep-Warden's Gorget", "neck", "of Strength", 30,
               "Issued to men who were told to hold a ruin."),
            mk("Broken Garrison Band", "ring", "of the Soldier", 30,
               "Snapped and re-soldered, badly, more than once."),
        ],
        "Gorbash the Thick": [
            mk("Stead-Breaker Maul", "main_hand", "of Strength", 30,
               "The Nethanders built that barn in a season. This took an hour.", weapon_type="mace_2h"),
            mk("Ogre-Hide Girdle", "waist", "of the Bear", 30,
               "A human could make a cloak from the offcut.", armor_type="leather"),
            mk("Thick-Skull Helm", "head", "of Strength", 30,
               "Dented outward, which takes some doing.", armor_type="mail"),
            mk("Millstone Shard Charm", "trinket", "of the Bear", 30,
               "A chip off the stead's own millstone, worn as a trophy."),
        ],
        "Sergeant Ironbeard": [
            mk("Dun Garok Mountaineer's Hammer", "main_hand", "of Strength", 30,
               "Dwarven make, and it shows in the balance.", weapon_type="mace_1h"),
            mk("Ironbeard's Garrison Plate", "chest", "of the Bear", 30,
               "Stormpike grey, with the fort's mark at the collar.", armor_type="plate"),
            mk("Rifleman's Powder Horn", "trinket", "of the Monkey", 30,
               "Still dry inside, which in this country is an achievement."),
            mk("Mountaineer's Studded Boots", "feet", "of Strength", 30,
               "Nailed for scree. Loud on flagstone.", armor_type="mail"),
        ],
        "Gatewarden Brannic": [
            mk("Gatewarden's Bearded Axe", "main_hand", "of Strength", 29,
               "Dwarf-made, and it has only ever swung in one doorway.", weapon_type="axe_1h"),
            mk("Dun Garok Gate-Shield", "off_hand", "of the Bear", 29,
               "Scarred in a band at exactly shoulder height.", weapon_type="shield"),
            mk("Threshold-Warden's Greaves", "legs", "of Strength", 29,
               "Braced for standing still, for years.", armor_type="plate"),
            mk("Stormpike Watch-Ring", "ring", "of the Bear", 29,
               "Issued at the gate. Never handed back."),
        ],
        "Rifle-Sergeant Dunmar": [
            mk("Dunmar's Long Rifle", "ranged", "of the Monkey", 30,
               "Sighted for the length of the muster yard, and no further.", weapon_type="gun"),
            mk("Rifle-Sergeant's Brigandine", "chest", "of Agility", 30,
               "Powder-burned at the right shoulder.", armor_type="mail"),
            mk("Marksman's Eye Glass", "trinket", "of the Monkey", 30,
               "Cracked across one lens. He shot fine anyway."),
            mk("Barracks Drill Belt", "waist", "of the Soldier", 30,
               "Notched for cartridges, every notch worn smooth.", armor_type="mail"),
        ],
        "Shrine-Keeper Morgrin": [
            mk("Keeper's Vault Maul", "main_hand", "of the Owl", 30,
               "A smith's hammer, blessed until it stopped being one.", weapon_type="mace_1h"),
            mk("Shrine-Keeper's Vestments", "chest", "of the Owl", 30,
               "Stone-grey wool, stiff with age and incense.", armor_type="cloth"),
            mk("Vault-Light Lantern", "off_hand", "of the Whale", 30,
               "Lit at the door of a vault nobody opens."),
            mk("Morgrin's Prayer-Beads", "neck", "of the Owl", 30,
               "Granite, worn to ovals by one thumb."),
        ],
        "Thane Korrin Stonewatch": [
            mk("Stonewatch Greataxe", "main_hand", "of Strength", 31,
               "The thane's own, and heavier than it has any right to be.", weapon_type="axe_2h"),
            mk("Thane's Hold-Plate", "chest", "of the Bear", 31,
               "Dun Garok's mark hammered into the breast, not painted on.", armor_type="plate"),
            mk("Crypt-Warden's Crown", "head", "of Strength", 31,
               "A circlet of iron. He was buried in it, and did not stay.", armor_type="plate"),
            mk("Stonewatch Oathband", "ring", "of the Bear", 31,
               "Sworn to hold the ridge. He is still technically holding it."),
        ],
        "Sergeant-at-Arms Varth": [
            mk("Gate-Warden's Halberd", "main_hand", "of the Soldier", 30,
               "Issued to hold a gate. It held, for a while.", weapon_type="polearm"),
            mk("Durnholde Gate-Guard Plate", "chest", "of the Bear", 30,
               "Grey beneath the violet paint, if you scratch it.", armor_type="plate"),
            mk("Sergeant's Whistle", "trinket", "of the Soldier", 30,
               "One short blast for the watch. Nobody is left to answer it."),
            mk("Portcullis Keyband", "ring", "of Strength", 30,
               "The key is long gone. The habit of wearing it was not."),
        ],
        "Houndmaster Sable": [
            mk("Houndmaster's Barbed Lash", "main_hand", "of the Monkey", 31,
               "The hounds learned it faster than the recruits did.", weapon_type="fist_weapon"),
            mk("Kennelmaster's Studded Hide", "chest", "of Agility", 31,
               "Bite marks, inside and out.", armor_type="leather"),
            mk("Sable's Houndhorn", "trinket", "of the Monkey", 31,
               "Blow it and something in the kennels still answers."),
            mk("Pack-Leader's Collar", "neck", "of Strength", 31,
               "Too large for a hound. She wore it anyway."),
        ],
        "Magister Yvaine": [
            mk("Violet Focus Staff", "main_hand", "of the Owl", 31,
               "Alterac work, re-cut by someone with less patience.", weapon_type="staff"),
            mk("Syndicate Magister's Robes", "chest", "of the Owl", 31,
               "Violet, silver-trimmed, and burned through at one cuff.", armor_type="cloth"),
            mk("Binding Sigil Ring", "ring", "of the Sorcerer", 31,
               "Still warm. It has been still warm for some years."),
            mk("Yvaine's Ledger Clasp", "trinket", "of the Owl", 31,
               "Held shut a book of names. The book is not here."),
        ],
        "The Keepkeeper": [
            mk("Keepkeeper's Keyring Flail", "main_hand", "of Strength", 32,
               "Thirty keys on a chain, swung as one.", weapon_type="mace_1h"),
            mk("Undercroft Warden's Mail", "chest", "of the Bear", 32,
               "Rusted into one piece. It still fits something.", armor_type="mail"),
            mk("Lamp of the Lower Door", "off_hand", "of the Owl", 32,
               "Burns without oil, which nobody wants to think about."),
            mk("Gaoler's Iron Band", "ring", "of the Bear", 32,
               "Worn on the outside of a gauntlet, by the look of it."),
        ],
        "Baron Aliden Perenolde": [
            mk("Perenolde Ancestral Blade", "main_hand", "of the Soldier", 33,
               "Alterac's royal house kept better smiths than it kept promises.", weapon_type="sword_2h"),
            mk("Baron's Treacherous Mantle", "shoulder", "of the Bear", 33,
               "The sigil of a kingdom that sold itself, worn without embarrassment.", armor_type="plate"),
            mk("Crown-Sold Signet", "ring", "of the Soldier", 33,
               "The seal of Alterac, on the hand that traded it away."),
            mk("Lordaeron Betrayer's Gorget", "neck", "of Strength", 33,
               "Taken from a better man at Durnholde's fall."),
        ],
        "Wall-Watcher Teague": [
            mk("Thoradin Border Pike", "main_hand", "of the Soldier", 30,
               "Long enough to keep Arathi on the other side of the stone.", weapon_type="polearm"),
            mk("Wall-Watcher's Hauberk", "chest", "of the Soldier", 30,
               "Thirty years on a wall nobody attacks.", armor_type="mail"),
            mk("Old Empire Signet", "ring", "of the Eagle", 30,
               "Thoradin's mark, worn to a suggestion."),
            mk("Border Vigil Cloak", "back", "of the Bear", 30,
               "Faded on one shoulder only - the side the wind comes from.", armor_type="cloth"),
        ],
    }


# ======================================================================================================================
def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())

    cdata["creatures"].update(WEST_CREATURES)
    cdata["creatures"].update(EAST_CREATURES)

    for zname, spec, overrides in (("Western Hillsbrad", WEST_ZONE, WEST_OVERRIDES),
                                   ("Eastern Hillsbrad", EAST_ZONE, EAST_OVERRIDES)):
        z = edata["zones"].setdefault(zname, {})
        z["open_zone"] = spec["open_zone"]
        z["subzones"] = spec["subzones"]
        if "caves" in spec:
            z["caves"] = spec["caves"]
        z["level_overrides"] = {k: list(v) for k, v in overrides.items()}

    out = {"_notes": "Hillsbrad boss / named-rare loot (2026-10-27). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(west_pools())
    out.update(east_pools())
    (ROOT / "data/loot/hillsbrad_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")

    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"Hillsbrad: creatures +{len(WEST_CREATURES) + len(EAST_CREATURES)}, "
          f"loot pools {len(out) - 1}, items {n}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")


if __name__ == "__main__":
    main()
