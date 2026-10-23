"""
Tirisfal rebuild content pass (2026-10-22): creatures, level bands, encounter tables and hand-crafted rare loot for
the rebuilt Western Tirisfal (L4-10), Eastern Tirisfal (L7-12) and Brill (town, no spawns).  Idempotent.

  tools/monster_kits.py (TIRISFAL_REBUILD_KITS) is the source of truth for ability kits
  (run tools/generate_creatures.py after editing it).  This script owns:
    * data/creatures/creatures.json   (new creatures, level bands)
    * data/creatures/encounters.json  (Western / Eastern Tirisfal tables + per-zone level_overrides; Brill has none)
    * data/loot/tirisfal_boss_loot.json (named-rare + boss pools)

LEVEL LADDER  Western: Nightmare Vale 5-7 | Stillwater Pond 5-8 | Solliden 6-8 | Whispering Shore 6-9 | Crusader Outpost 7-9
                       Cold Hearth Manor 6-9 | Agamand Mills 8-10 | Garren's Haunt 8-10 | Agamand Family Crypt 9-10
              Eastern: Zeppelin Landing / open glades 7-9 | Crusader's Outpost 8-10 | Brightwater Lake 8-10 | Faol's Rest 8-10
                       Balnir 9-11 | Ruins of Lordaeron 9-11 | Venomweb Vale 10-11 | North Coast 10-12 | Cult Farm 10-12
                       Scarlet Watch Post 10-12 | Bulwark Road 9-12
RULES         ONE item per kill from the creature's pool, real loot formulas, item_level = creature level + 3.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import build_durotar_content as HIGH  # noqa: E402  (every pool here is ilvl >= 10)


def mk(name, slot, suffix, ilvl, flavor, **kw):
    return HIGH.make(name, slot, suffix, ilvl, flavor, **kw)


def C(template, lo, hi, kit, boss=False, mult=None):
    d = {"template": template, "level_range": [lo, hi], "is_boss": boss, "ability_kit": kit}
    if boss and mult:
        d["boss_multiplier"] = mult
    return d


NEW_CREATURES = {
    # ---- Western
    "Vile Fin Puddlejumper": C("humanoid_warrior", 6, 8, "vile_fin_puddlejumper"),
    "Vile Fin Minor Oracle": C("humanoid_caster", 7, 9, "vile_fin_oracle"),
    "Stillwater Lurker": C("beast_basic", 5, 7, "stillwater_lurker"),
    "Agamand Crypt Wight": C("undead_basic", 9, 10, "agamand_crypt_wight"),
    "Rot Hide Mongrel": C("beast_basic", 8, 10, "rot_hide_mongrel"),
    "Rot Hide Gnoll": C("humanoid_warrior", 8, 10, "rot_hide_gnoll"),
    "Rot Hide Graverobber": C("humanoid_warrior", 8, 10, "rot_hide_graverobber"),
    "Ressan the Needler": C("beast_fast", 7, 7, "ressan_the_needler", True, 1.8),
    "Old Gillrot": C("humanoid_caster", 9, 9, "old_gillrot", True, 1.7),
    "Meven Korgal": C("humanoid_warrior", 9, 9, "meven_korgal", True, 1.7),
    "Goodman Solliden": C("undead_basic", 8, 8, "goodman_solliden", True, 1.7),
    "Murk the Bloated": C("undead_basic", 7, 7, "murk_the_bloated", True, 1.8),
    "Captain Dargol": C("undead_basic", 10, 10, "captain_dargol", True, 1.6),
    "Maggot Eye": C("humanoid_warrior", 10, 10, "maggot_eye", True, 1.6),
    "Reaper-Lord Aldous": C("undead_basic", 9, 9, "reaper_lord_aldous", True, 1.7),
    # ---- Eastern
    "Faol's Restless": C("undead_basic", 8, 10, "faols_restless"),
    "Venomweb Skitterer": C("vermin_sneaky", 10, 11, "venomweb_skitterer"),
    "Lordaeron Remnant": C("undead_basic", 9, 11, "lordaeron_remnant"),
    "Cult Acolyte": C("humanoid_caster", 10, 12, "cult_acolyte"),
    "Cult Fanatic": C("humanoid_warrior", 10, 12, "cult_fanatic"),
    "Bethor Iceshard": C("elemental_caster", 10, 10, "bethor_iceshard", True, 1.6),
    "Captain Melrache": C("humanoid_warrior", 10, 10, "captain_melrache", True, 1.6),
    "Crusader Brennic": C("humanoid_warrior", 10, 10, "crusader_brennic", True, 1.6),
    "Mother Venomweb": C("vermin_sneaky", 11, 11, "mother_venomweb", True, 1.6),
    "Captain Vachon": C("humanoid_warrior", 11, 11, "captain_vachon", True, 1.6),
    "Cult Overseer Thaddeus": C("humanoid_caster", 12, 12, "cult_overseer_thaddeus", True, 1.6),
    # ---- Scourge Cave (Eastern, L10-13)
    "Scourge Ghoul": C("undead_basic", 10, 12, "scourge_ghoul"),
    "Ghoulmaster Krag": C("undead_basic", 11, 11, "ghoulmaster_krag", True, 1.6),
    "Plaguemaster Orvyn": C("humanoid_caster", 12, 12, "plaguemaster_orvyn", True, 1.6),
}

# creatures that only one Tirisfal zone uses now (global bands)
LEVEL_PATCH = {
    "Manor Reaper": (6, 9), "Solliden Farmhand": (6, 8), "Blighted Grain Thresher": (6, 8),
    "Captured Farmer": (8, 10), "Agamand Servant": (8, 10), "Agamand Family Ghoul": (8, 10),
    "Thurman Agamand": (10, 10),
    "Scarlet Zealot": (10, 12), "Scarlet Bowman": (10, 12), "Scarlet Preacher": (10, 12), "Interrogator Vishas": (12, 12),
    "Scourge Warrior": (10, 12), "Scourge Necromancer": (10, 12), "Scourge Abomination": (13, 13),
}
KIT_PATCH = {}

OVERRIDES = {
    "Western Tirisfal": {
        "Mangy Duskbat": [4, 7], "Wretched Zombie": [5, 8], "Rotting Dead": [6, 9], "Bleak Worg": [5, 7],
        "Young Nightcrawler": [5, 7], "Rattlecage Skeleton": [5, 7], "Scarlet Convert": [7, 9],
        "Scarlet Initiate": [8, 9], "Drowned Wretch": [5, 7],
    },
    "Eastern Tirisfal": {
        "Mangy Duskbat": [7, 9], "Wretched Zombie": [7, 9], "Rotting Dead": [8, 10], "Ragged Scavenger": [7, 9],
        "Rattlecage Skeleton": [8, 10], "Bleak Worg": [8, 10], "Young Nightcrawler": [8, 9],
        "Drowned Wretch": [8, 10], "Weeping Shade": [8, 10], "Scarlet Convert": [8, 10], "Scarlet Initiate": [9, 10],
        "Balnir Stableboy": [9, 10], "Vicious Night Web Spider": [10, 11],
    },
}

ENCOUNTERS = {
    "Western Tirisfal": {
        "open_zone": {"name": "The Glades", "creatures": {
            "Mangy Duskbat": 2, "Rotting Dead": 2, "Wretched Zombie": 1, "Bleak Worg": 1, "Rattlecage Skeleton": 1}},
        "subzones": {
            "Whispering Shore": {"name": "Whispering Shore", "creatures": {
                "Vile Fin Puddlejumper": 4, "Vile Fin Minor Oracle": 3, "Rotting Dead": 1, "Old Gillrot": 0}},
            "Crusader Outpost": {"name": "Crusader Outpost", "creatures": {
                "Scarlet Convert": 4, "Scarlet Initiate": 1, "Meven Korgal": 0}},
            "Solliden Farmstead": {"name": "Solliden Farmstead", "creatures": {
                "Solliden Farmhand": 3, "Blighted Grain Thresher": 3, "Rotting Dead": 1, "Goodman Solliden": 0}},
            "Stillwater Pond": {"name": "Stillwater Pond", "creatures": {
                "Stillwater Lurker": 4, "Rotting Dead": 3, "Drowned Wretch": 1, "Murk the Bloated": 0}},
            "Agamand Mills": {"name": "Agamand Mills", "creatures": {
                "Agamand Servant": 3, "Agamand Family Ghoul": 2, "Captured Farmer": 1, "Thurman Agamand": 0}},
            "Agamand Family Crypt": {"name": "Agamand Family Crypt", "creatures": {
                "Agamand Crypt Wight": 3, "Agamand Family Ghoul": 2, "Captain Dargol": 0}},
            "Garren's Haunt": {"name": "Garren's Haunt", "creatures": {
                "Rot Hide Mongrel": 3, "Rot Hide Gnoll": 3, "Rot Hide Graverobber": 2, "Maggot Eye": 0}},
            "Cold Hearth Manor": {"name": "Cold Hearth Manor", "creatures": {
                "Manor Reaper": 4, "Wretched Zombie": 2, "Rotting Dead": 1, "Reaper-Lord Aldous": 0}},
            "Nightmare Vale": {"name": "Nightmare Vale", "creatures": {
                "Bleak Worg": 4, "Young Nightcrawler": 2, "Scarlet Convert": 1, "Ressan the Needler": 0}},
        },
    },
    "Eastern Tirisfal": {
        "open_zone": {"name": "The Glades", "creatures": {
            "Mangy Duskbat": 2, "Rotting Dead": 2, "Young Nightcrawler": 1, "Wretched Zombie": 1, "Bleak Worg": 1,
            "Rattlecage Skeleton": 1}},
        "subzones": {
            "Brightwater Lake": {"name": "Brightwater Lake", "creatures": {
                "Drowned Wretch": 4, "Weeping Shade": 3, "Young Nightcrawler": 1, "Bethor Iceshard": 0}},
            "The North Coast": {"name": "The North Coast", "creatures": {
                "Scarlet Bowman": 2, "Rattlecage Skeleton": 2, "Ragged Scavenger": 2}},
            "Scarlet Watch Post": {"name": "Scarlet Watch Post", "creatures": {
                "Scarlet Zealot": 3, "Scarlet Bowman": 2, "Scarlet Preacher": 2, "Interrogator Vishas": 0}},
            "Faol's Rest": {"name": "Faol's Rest", "creatures": {
                "Faol's Restless": 4, "Rotting Dead": 2, "Rattlecage Skeleton": 1, "Captain Melrache": 0}},
            "Crusader's Outpost": {"name": "Crusader's Outpost", "creatures": {
                "Scarlet Convert": 3, "Scarlet Initiate": 2, "Crusader Brennic": 0}},
            "Venomweb Vale": {"name": "Venomweb Vale", "creatures": {
                "Venomweb Skitterer": 4, "Vicious Night Web Spider": 3, "Mother Venomweb": 0}},
            "Ruins of Lordaeron": {"name": "Ruins of Lordaeron", "creatures": {
                "Lordaeron Remnant": 4, "Wretched Zombie": 2, "Rattlecage Skeleton": 2}},
            "Balnir Farmstead": {"name": "Balnir Farmstead", "creatures": {
                "Bleak Worg": 3, "Balnir Stableboy": 3, "Scarlet Convert": 1, "Captain Vachon": 0}},
            "Cult of the Damned Farm": {"name": "Cult of the Damned Farm", "creatures": {
                "Cult Acolyte": 3, "Cult Fanatic": 3, "Rotting Dead": 1, "Cult Overseer Thaddeus": 0}},
            "The Bulwark Road": {"name": "The Bulwark Road", "creatures": {
                "Wretched Zombie": 2, "Bleak Worg": 2}},
        },
        # the Scourge Cave (hand-built 2026-10-23, tools/handbuilt_scourge_cave.py): random trash, boss + 2 rares pinned
        "caves": {
            "Scourge Cave": {"name": "Scourge Cave", "creatures": {
                "Scourge Warrior": 4, "Scourge Ghoul": 4, "Scourge Necromancer": 3, "Cult Acolyte": 2, "Cult Fanatic": 1,
                "Scourge Abomination": 0, "Ghoulmaster Krag": 0, "Plaguemaster Orvyn": 0}},
        },
    },
}


# ----------------------------------------------------------------------
def pools():
    P = {}
    P["Ressan the Needler"] = [          # L7 -> ilvl 10
        mk("Needle-Fang Dirk", "main_hand", "of the Assassin", 10,
           "A bat's tooth the length of your finger, honed to a point you can barely see.", weapon_type="dagger"),
        mk("Duskwing Mantle", "shoulder", "of the Bandit", 10,
           "Stitched from wing membrane. It flaps when you run and it never quite stops.", armor_type="leather"),
        mk("Echolocator's Cord", "waist", "of the Mind's Eye", 10,
           "It hums at a pitch only the dead can hear. Nobody has told the living.", armor_type="cloth"),
        mk("Shrill Whistle Pendant", "neck", "of the Falcon", 10,
           "Blow it and every bat in the Vale turns to look. Do not blow it."),
    ]
    P["Murk the Bloated"] = [            # L7 -> ilvl 10
        mk("Murk's Waterlogged Cudgel", "main_hand", "of the Bear", 10,
           "Swollen with pond water. Every swing leaves a puddle.", weapon_type="mace_1h"),
        mk("Bog-Slick Waders", "feet", "of the Whale", 10,
           "Tall, black and permanently damp. They will never smell like anything else.", armor_type="mail"),
        mk("Bloat-Skin Vest", "chest", "of the Wolf", 10,
           "Stretched hide, drum-tight. It holds in more than it should.", armor_type="leather"),
        mk("Silt-Crusted Ring", "ring", "of the Eagle", 10,
           "Something fell in the pond with this on its finger. It was not the first."),
    ]
    P["Goodman Solliden"] = [            # L8 -> ilvl 11
        mk("Solliden's Rusted Pitchfork", "main_hand", "of the Soldier", 11,
           "Three tines, two of them straight. It has been through a harvest and a siege.", weapon_type="polearm"),
        mk("Harvest-Blighted Overalls", "legs", "of the Wolf", 11,
           "Patched at the knee, stained at the hem. The pockets are full of seed that will never grow.",
           armor_type="leather"),
        mk("Scarecrow-Stuffed Hat", "head", "of the Owl", 11,
           "Straw sticks out of the brim. Some of the straw is looking at you.", armor_type="cloth"),
        mk("Pumpkin-Vine Belt", "waist", "of the Monkey", 11,
           "Braided vine, tough as rope. It still blooms in the dark, which is unsettling.", armor_type="leather"),
    ]
    P["Old Gillrot"] = [                 # L9 -> ilvl 12
        mk("Gillrot's Tidecaller Staff", "main_hand", "of the Invoker", 12,
           "Driftwood bound with kelp and a salt-white pearl. The tide answers it, a little too eagerly.",
           weapon_type="staff"),
        mk("Kelp-Sodden Robe", "chest", "of the Restorer", 12,
           "It has never been dry. It does not seem to want to be.", armor_type="cloth"),
        mk("Pearl-Studded Circlet", "head", "of the Seer", 12,
           "Oracle-pearls, set by someone who did not know what they were.", armor_type="cloth"),
        mk("Brinewrack Ring", "ring", "of the Archmage", 12,
           "Cold, salt-pitted and humming a very old tune."),
    ]
    P["Meven Korgal"] = [                # L9 -> ilvl 12
        mk("Korgal's Zealot Blade", "main_hand", "of the Champion", 12,
           "Blessed once, polished daily, and keen enough that the blessing is almost beside the point.",
           weapon_type="sword_1h"),
        mk("Crusader's Oathplate Pauldrons", "shoulder", "of the Bulwark", 12,
           "Crimson enamel over dented plate. An oath is scratched on the inside.", armor_type="plate"),
        mk("Standard-Bearer's Tabard", "chest", "of the Soldier", 12,
           "The Crusade's red, faded from carrying it in the rain.", armor_type="mail"),
        mk("Hallowed Prayer Beads", "neck", "of the Hierophant", 12,
           "Worn smooth. Some of the prayers on them are for you."),
    ]
    P["Reaper-Lord Aldous"] = [          # L9 -> ilvl 12
        mk("Aldous' Harvest Scythe", "main_hand", "of the Champion", 12,
           "The manor's reapers were all cut from his pattern. So was this.", weapon_type="polearm"),
        mk("Death's Hour Cowl", "head", "of the Necromancer", 12,
           "A hood that remembers when the manor's clock stopped.", armor_type="cloth"),
        mk("Manor Reaper's Coat", "chest", "of the Assassin", 12,
           "Black leather, old stitching, a hundred small cuts.", armor_type="leather"),
        mk("Cold Hearth Brazier Charm", "neck", "of the Invoker", 12,
           "Ash and iron. It glows when the manor's chimney draws."),
    ]
    P["Captain Dargol"] = [              # L10 -> ilvl 13
        mk("Dargol's Family Blade", "main_hand", "of the Champion", 13,
           "Handed down in the Agamand line and, eventually, back up out of the crypt.", weapon_type="sword_1h"),
        mk("Crypt-Captain's Hauberk", "chest", "of the Defender", 13,
           "Mail the colour of old rain, rusted along the seams.", armor_type="mail"),
        mk("Ancestral Signet", "ring", "of the Soldier", 13,
           "A family crest, worn thin. The family did not do the wearing."),
        mk("Mausoleum Ward-Shield", "off_hand", "of the Bastion", 13,
           "A slab of crypt door with a handle. It was built to keep things in.", weapon_type="shield"),
    ]
    P["Maggot Eye"] = [                  # L10 -> ilvl 13
        mk("Maggot Eye's Gnoll-Smasher", "main_hand", "of the Juggernaut", 13,
           "A fence-post, a chunk of anvil, and a great deal of ill will.", weapon_type="mace_2h"),
        mk("Rot Hide Warpaint Vest", "chest", "of the Hunt", 13,
           "Hide, stained in colours no gnoll ever wore on purpose.", armor_type="leather"),
        mk("Gnawed Bone Necklace", "neck", "of the Tiger", 13,
           "Every bone is a bite-mark. Every bite-mark is a story."),
        mk("Maggot-Crusted Gloves", "hands", "of the Bandit", 13,
           "Do not look inside. They are warm.", armor_type="leather"),
    ]
    P["Thurman Agamand"] = [             # L10 -> ilvl 13
        mk("Thurman's Miller's Maul", "main_hand", "of the Juggernaut", 13,
           "The mill's mallet, grown heavy with a family's grudge.", weapon_type="mace_2h"),
        mk("Mill-Dust Bracers", "wrist", "of the Hunt", 13,
           "Leather caked in grey flour that is not flour.", armor_type="leather"),
        mk("Agamand Family Crest", "neck", "of the Tactician", 13,
           "A cracked gold pendant. The crest is a mill-wheel and a wreath."),
        mk("Grinding-Stone Belt", "waist", "of the Bear", 13,
           "Iron links and a millstone buckle. It never shifts.", armor_type="mail"),
    ]
    P["Bethor Iceshard"] = [             # L10 -> ilvl 13
        mk("Iceshard Scepter", "main_hand", "of the Invoker", 13,
           "A sliver of lake-ice that has refused to melt for three seasons.", weapon_type="wand"),
        mk("Frostbitten Mage-Robe", "chest", "of the Archmage", 13,
           "Frozen stiff on the shoulders and warm, strangely, at the heart.", armor_type="cloth"),
        mk("Brightwater Shard Pendant", "neck", "of the Seer", 13,
           "A shard of the lake bed, clear as glass. It shows you somewhere else."),
        mk("Rimed Gauntlets", "hands", "of the Sorcerer", 13,
           "They crackle when you close your fists.", armor_type="cloth"),
    ]
    P["Captain Melrache"] = [            # L10 -> ilvl 13
        mk("Melrache's Zealot Cleaver", "main_hand", "of the Soldier", 13,
           "A broad axe from the Crusade's armoury, notched with Forsaken tallies.", weapon_type="axe_2h"),
        mk("Faol's Rest Warplate", "chest", "of the Champion", 13,
           "The captain's own, hammered back into shape a dozen times.", armor_type="plate"),
        mk("Rallying Banner Cloak", "back", "of the Tactician", 13,
           "Cut from a regimental banner. It still smells of candle-smoke.", armor_type="cloth"),
        mk("Crusader Captain's Greaves", "feet", "of the Defender", 13,
           "Heavy and polished. The polish is mostly vanity.", armor_type="mail"),
    ]
    P["Crusader Brennic"] = [            # L10 -> ilvl 13
        mk("Brennic's Shieldwall", "off_hand", "of the Bulwark", 13,
           "A tower of dented steel painted Crusade red. It has stopped more than blades.", weapon_type="shield"),
        mk("Outpost Lance", "main_hand", "of the Soldier", 13,
           "A cavalry lance with no cavalry left to carry it.", weapon_type="polearm"),
        mk("Crusader's Mail Coif", "head", "of the Warder", 13,
           "Rings of steel, rubbed bright. Whoever wore it prayed in it.", armor_type="mail"),
        mk("Oath-Bound Bracers", "wrist", "of the Champion", 13,
           "Iron cuffs engraved with the Crusade's vows.", armor_type="plate"),
    ]
    P["Mother Venomweb"] = [             # L11 -> ilvl 14
        mk("Venomweb Fang", "main_hand", "of the Assassin", 14,
           "A fang as long as a dagger. It weeps when you hold it.", weapon_type="dagger"),
        mk("Brood-Mother's Silk Wrap", "legs", "of the Prophet", 14,
           "Pale silk, woven tight, warm with something still alive.", armor_type="cloth"),
        mk("Vale-Walker's Chitin Cap", "head", "of the Hunt", 14,
           "Cunningly layered shell, cut for a head with fewer eyes.", armor_type="leather"),
        mk("Cocoon-Wrapped Cloak", "back", "of the Wolf", 14,
           "Something struggled in this once. It kept the shape.", armor_type="leather"),
    ]
    P["Captain Vachon"] = [              # L11 -> ilvl 14
        mk("Vachon's Balnir Saber", "main_hand", "of the Duelist", 14,
           "A cavalry saber, ground thin. The stable-boys call it 'Old Faithful'.", weapon_type="sword_1h"),
        mk("Stable-Warden's Hauberk", "chest", "of the Defender", 14,
           "Chain over leather, smelling of hay and horse.", armor_type="mail"),
        mk("Pitted Captain's Pauldrons", "shoulder", "of the Bastion", 14,
           "Dented in a dozen places. He called each dent by name.", armor_type="plate"),
        mk("Rusted Horseshoe Charm", "neck", "of the Tiger", 14,
           "Lucky, they say. The horse it came off would disagree."),
    ]
    P["Cult Overseer Thaddeus"] = [      # L12 -> ilvl 15
        mk("Thaddeus' Shadowlash Rod", "main_hand", "of the Necromancer", 15,
           "A black rod that lashes out without being swung.", weapon_type="wand"),
        mk("Overseer's Black Vestments", "chest", "of the Prophet", 15,
           "Wool the colour of a closed eye. The cult's sigil is stitched where the heart would be.",
           armor_type="cloth"),
        mk("Ledger-Keeper's Ring", "ring", "of the Seer", 15,
           "Engraved with a tally that never reaches the bottom of the page."),
        mk("Damned Vestment Mantle", "shoulder", "of the Sorcerer", 15,
           "Hooded, hungry, and faintly warm.", armor_type="cloth"),
    ]
    P["Interrogator Vishas"] = [         # L12 -> ilvl 15
        mk("Vishas' Branding Iron", "main_hand", "of the Hierophant", 15,
           "The head is shaped like the Crusade's sunburst. The reason is not pleasant.", weapon_type="mace_1h"),
        mk("Interrogator's Black Coat", "chest", "of the Assassin", 15,
           "Leather, buckled to the throat. It does not creak when he walks.", armor_type="leather"),
        mk("Penance Gauntlets", "hands", "of the Champion", 15,
           "Studded on the inside. You find out why.", armor_type="plate"),
        mk("Confessor's Signet", "ring", "of the Prophet", 15,
           "Everyone who has worn it said exactly what he wanted to hear."),
    ]
    P["Scourge Abomination"] = [        # L13 -> ilvl 16
        mk("Abomination's Hook-Spear", "main_hand", "of the Juggernaut", 16,
           "A butcher's hook the length of a lance. The meat is still on it.", weapon_type="polearm"),
        mk("Stitched-Hide Cuirass", "chest", "of the Defender", 16,
           "Plate riveted over a hide that was never meant to be worn.", armor_type="plate"),
        mk("Scourge Sinew Cord", "waist", "of the Bear", 16,
           "A belt of cured tendon. It tightens when you aren't looking.", armor_type="mail"),
        mk("Ring of Borrowed Bone", "ring", "of the Soldier", 16,
           "Carved from a rib that fit someone else, once."),
    ]
    P["Ghoulmaster Krag"] = [            # L11 -> ilvl 14
        mk("Ghoulmaster's Bone Whip", "main_hand", "of the Assassin", 14,
           "Knuckle-bones on a gut cord. The pack comes when it cracks.", weapon_type="dagger"),
        mk("Pack-Leader's Mantle", "shoulder", "of the Bandit", 14,
           "Tanned ghoul hide, still twitching at the edges.", armor_type="leather"),
        mk("Gnawed Femur Cudgel", "main_hand", "of the Soldier", 14,
           "Somebody's thigh bone, chewed to a handle.", weapon_type="mace_1h"),
        mk("Marrowband Choker", "neck", "of the Tiger", 14,
           "A string of small teeth. None of them are his."),
    ]
    P["Plaguemaster Orvyn"] = [          # L12 -> ilvl 15
        mk("Orvyn's Plague Rod", "main_hand", "of the Invoker", 15,
           "A glass rod with something alive swirling in it.", weapon_type="staff"),
        mk("Alchemist's Stained Apron", "chest", "of the Sorcerer", 15,
           "Every colour of rot, all of it permanent.", armor_type="cloth"),
        mk("Vial-Studded Bracers", "wrist", "of the Seer", 15,
           "The vials are corked. Most of them.", armor_type="cloth"),
        mk("Formula-Etched Signet", "ring", "of the Archmage", 15,
           "The recipe is engraved inside the band. You do not want to read it."),
    ]
    return P


def main():
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text())
    cr = data["creatures"]
    for n, d in NEW_CREATURES.items():
        cr[n] = d
    for n, (lo, hi) in LEVEL_PATCH.items():
        cr[n]["level_range"] = [lo, hi]
    for n, k in KIT_PATCH.items():
        cr[n]["ability_kit"] = k
    p.write_text(json.dumps(data, indent=2) + "\n")

    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text())
    z = data["zones"]
    for zone, enc in ENCOUNTERS.items():
        z[zone]["open_zone"] = enc["open_zone"]
        z[zone]["subzones"] = enc["subzones"]
        z[zone]["level_overrides"] = {k: list(v) for k, v in OVERRIDES[zone].items()}
        if "caves" in enc:
            z[zone]["caves"] = enc["caves"]
    z.pop("Brill", None)                     # Brill is a town: nothing spawns there any more (Balnir moved to Eastern)
    p.write_text(json.dumps(data, indent=2) + "\n")

    out = {"_notes": "Tirisfal rebuild named-rare + boss loot (2026-10-22). One item drops per kill "
                     "from the creature's pool. Numbers from the real loot formulas (tools/build_tirisfal_content.py)."}
    out.update(pools())
    (ROOT / "data/loot/tirisfal_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n_items = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, level patches {len(LEVEL_PATCH)}, loot pools {len(out)-1}, items {n_items}")


if __name__ == "__main__":
    main()
