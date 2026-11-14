#!/usr/bin/env python3
"""Silverpine rebuild content pass (2026-10-23).  Idempotent.  Sections are added stage by stage.

  PYTHONPATH=. python3 tools/build_silverpine_content.py     (kits live in tools/monster_kits.py SILVERPINE_NORTH_KITS ...;
                                                               run `cd tools && python3 generate_creatures.py` after kit edits)

LEVEL LADDER  North:  Raven Hill Cemetery 12-16 | Olsen's Farthing 12-14 | The Dead Field 13-15 | Shadowspring Pools 13-16
                      Malden's Orchard 14-16 | The Skittering Dark 15-17 | open woods 11-14
RULES         ONE item per kill from the creature's own pool of 4, item_level = creature level + 3, real loot formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

# ======================================================================================================================
# SILVERPINE NORTH
# ======================================================================================================================
NORTH_CREATURES = {
    # Olsen's Farthing
    "Farthing Hound": C("beast_fast", 12, 14, "farthing_hound"),
    "Risen Farmhand": C("undead_basic", 12, 14, "risen_farmhand"),
    "Old Hob": C("beast_fast", 14, 14, "old_hob", True, 1.7),
    # The Dead Field
    "Dead Field Harrower": C("undead_basic", 13, 15, "dead_field_harrower"),
    "Blighted Crow": C("beast_fast", 13, 15, "blighted_crow"),
    "Gaunt the Scarecrow-King": C("undead_basic", 15, 15, "gaunt_scarecrow_king", True, 1.7),
    # Malden's Orchard
    "Orchard Shambler": C("undead_basic", 14, 16, "orchard_shambler"),
    "Windfall Wasp": C("vermin_swarm", 14, 16, "windfall_wasp"),
    "Orchardkeeper Gnarl": C("elemental_bruiser", 16, 16, "orchardkeeper_gnarl", True, 1.7),
    # The Skittering Dark
    "Venomfang Skitterer": C("vermin_sneaky", 15, 17, "venomfang_skitterer"),
    "Longleg the Stalker": C("vermin_sneaky", 17, 17, "longleg_the_stalker", True, 1.7),
}

NORTH_OVERRIDES = {
    "Worg Prowler": [11, 14], "Feral Ghoul": [11, 14], "Silverpine Spider": [11, 14], "Corrupted Treant": [12, 15],
    "Risen Husk": [12, 15], "Grave Moss Creeper": [12, 15], "Skeletal Groundskeeper": [12, 15],
    "Bog Beast": [13, 16], "Murky Crocolisk": [13, 16], "Rot Hide Slitherer": [13, 16],
    "Giant Spider": [15, 17],
}

NORTH_ZONE = {
    "open_zone": {"name": "The Silverpine Woods", "creatures": {
        "Worg Prowler": 3, "Silverpine Spider": 2, "Feral Ghoul": 2, "Corrupted Treant": 1}},
    "subzones": {
        "Olsen's Farthing": {"name": "Olsen's Farthing", "creatures": {
            "Farthing Hound": 4, "Risen Farmhand": 3, "Worg Prowler": 1, "Old Hob": 0}},
        "Raven Hill Cemetery": {"name": "Raven Hill Cemetery", "creatures": {
            "Risen Husk": 3, "Grave Moss Creeper": 2, "Skeletal Groundskeeper": 2, "The Forsaken Watchman": 0}},
        "The Dead Field": {"name": "The Dead Field", "creatures": {
            "Dead Field Harrower": 3, "Blighted Crow": 3, "Risen Husk": 1, "Gaunt the Scarecrow-King": 0}},
        "Malden's Orchard": {"name": "Malden's Orchard", "creatures": {
            "Orchard Shambler": 3, "Windfall Wasp": 3, "Corrupted Treant": 2, "Orchardkeeper Gnarl": 0}},
        "Shadowspring Pools": {"name": "Shadowspring Pools", "creatures": {
            "Bog Beast": 3, "Murky Crocolisk": 2, "Rot Hide Slitherer": 2, "Muckmaw": 0}},
        "The Skittering Dark": {"name": "The Skittering Dark", "creatures": {
            "Venomfang Skitterer": 4, "Giant Spider": 2, "Silverpine Spider": 2, "Longleg the Stalker": 0}},
    },
}


def north_pools():
    P = {}
    P["Old Hob"] = [                       # L14 -> ilvl 17
        mk("Hob's Gnawed Collar", "neck", "of the Beast", 17,
           "Spiked leather, chewed through at the clasp. He got out. He did not stay out."),
        mk("Farthing Hound-Hide Jerkin", "chest", "of the Hunt", 17,
           "Cured from a dog that never learned to fear a pitchfork.", armor_type="leather"),
        mk("Boneyard Dog-Tooth Dirk", "main_hand", "of the Assassin", 17,
           "A canine fang the length of a hand, set in a farmhand's knife handle.", weapon_type="dagger"),
        mk("Mud-Caked Hunter's Boots", "feet", "of the Wolf", 17,
           "Silent on wet earth. Loud, somehow, in every other way.", armor_type="leather"),
    ]
    P["Gaunt the Scarecrow-King"] = [      # L15 -> ilvl 18
        mk("Straw-King's Hollow Crown", "head", "of the Necromancer", 18,
           "Woven from stalks of the Dead Field. It whispers in the voice of the harvest.", armor_type="cloth"),
        mk("Gaunt's Threshing Flail", "main_hand", "of the Juggernaut", 18,
           "Two sticks, one chain, and a very long grudge against anything that grows.", weapon_type="mace_2h"),
        mk("Crow-Feather Cloak", "back", "of the Falcon", 18,
           "Black feathers, sewn in rows. Some of the rows are still muttering.", armor_type="leather"),
        mk("Burlap Belt of Binding", "waist", "of the Bear", 18,
           "Rough-spun sacking, knotted tight. It remembers what it was tied around.", armor_type="mail"),
    ]
    P["Orchardkeeper Gnarl"] = [           # L16 -> ilvl 19
        mk("Gnarl's Windfall Staff", "main_hand", "of the Invoker", 19,
           "Apple-wood, split by lightning, healed over with something that is not bark.", weapon_type="staff"),
        mk("Rotapple-Studded Bracers", "wrist", "of the Restorer", 19,
           "Dried fruit and bark, bound with root. They smell sweeter than they should.", armor_type="cloth"),
        mk("Orchard-Warden's Heartwood Shield", "off_hand", "of the Bulwark", 19,
           "A slice from the old tree's heart. It has grown a little since you picked it up.", weapon_type="shield"),
        mk("Malden's Last Harvest Ring", "ring", "of the Owl", 19,
           "A band of polished root. Planted, it would probably grow."),
    ]
    P["Longleg the Stalker"] = [           # L17 -> ilvl 20
        mk("Longleg's Venom-Barbed Spear", "main_hand", "of the Soldier", 20,
           "A leg-spine as long as a man, hollow, and still weeping.", weapon_type="polearm"),
        mk("Skitterer's Silk Leggings", "legs", "of the Prophet", 20,
           "Woven in the dark, soft as breath, and sticky in ways that do not wash out.", armor_type="cloth"),
        mk("Stalker's Carapace Pauldrons", "shoulder", "of the Bandit", 20,
           "Chitin plates laced with web. Each one is a different shade of wrong.", armor_type="leather"),
        mk("Dark-Eyed Fang Pendant", "neck", "of the Tiger", 20,
           "Eight small eyes, polished, set in a single fang. It does not like being worn."),
    ]
    P["The Forsaken Watchman"] = [         # L16 -> ilvl 19
        mk("Watchman's Rusted Lance", "main_hand", "of the Champion", 19,
           "Still sharp at the tip. The rest of it has given up.", weapon_type="polearm"),
        mk("Raven Hill Warden's Plate", "chest", "of the Defender", 19,
           "Rust-red plate, dented from holding a gate that was never going to be attacked.", armor_type="plate"),
        mk("Cemetery Keeper's Gauntlets", "hands", "of the Warder", 19,
           "Gloves for digging and for not digging. They are good at both.", armor_type="mail"),
        mk("Sentinel's Grave-Ward Signet", "ring", "of the Bastion", 19,
           "An old guard's seal. It keeps the quiet dead quiet."),
    ]
    P["Muckmaw"] = [                       # L16 -> ilvl 19
        mk("Muckmaw's Gnashing Jaw", "main_hand", "of the Beast", 19,
           "An entire crocolisk jaw on a bone haft. It still snaps.", weapon_type="axe_2h"),
        mk("Mire-Slick Hide Vest", "chest", "of the Whale", 19,
           "Black, scaled, and never dry. It repels water and sympathy equally.", armor_type="leather"),
        mk("Shadowspring Algae Bracers", "wrist", "of the Physician", 19,
           "Green, slimy, and curiously healing. Do not ask where they were cut.", armor_type="cloth"),
        mk("Swamp-Tooth Totem Charm", "neck", "of the Eagle", 19,
           "A tooth the size of a thumb, strung on mud-rope."),
    ]
    return P


# ======================================================================================================================
# SILVERPINE SOUTH  (L16-20)
# ======================================================================================================================
SOUTH_CREATURES = {
    # Bucklebree Farm
    "Blightfed Hog": C("beast_basic", 15, 17, "blightfed_hog"),
    "Barn Ghoul": C("undead_basic", 15, 17, "barn_ghoul"),
    "Tusk-Mother Gorra": C("beast_basic", 17, 17, "tusk_mother_gorra", True, 1.7),
    # Deep Elem Mine
    "Deep Elem Digger": C("humanoid_warrior", 16, 18, "deep_elem_digger"),
    "Mine Shambler": C("undead_basic", 16, 18, "mine_shambler"),
    "Gnawbone the Foreman": C("humanoid_warrior", 18, 18, "gnawbone_foreman", True, 1.7),
    # Valgan's Field
    "Field Deserter": C("humanoid_rogue", 16, 18, "field_deserter"),
    "Battlefield Wight": C("undead_basic", 17, 18, "battlefield_wight"),
    # Berard's Talon
    "Crag Stalker": C("beast_fast", 17, 19, "crag_stalker"),
    "Talon Wraith": C("humanoid_caster", 17, 19, "talon_wraith"),
    "Berard the Forgotten": C("undead_basic", 19, 19, "berard_the_forgotten", True, 1.7),
    # Beren's Peril
    "Peril Packmaster": C("humanoid_warrior", 18, 20, "peril_packmaster"),
    "Bloodmaw the Alpha": C("beast_fast", 20, 20, "bloodmaw_alpha", True, 1.7),
    # Greymane Wall
    "Wallbreaker Worgen": C("beast_fast", 18, 20, "wallbreaker_worgen"),
    "Wall Wraith": C("undead_basic", 18, 20, "wall_wraith"),
    "Gilnean Wall-Warden": C("humanoid_warrior", 20, 20, "wall_warden", True, 1.7),
    # Ambermill
    "Ambermill Ghost-Mage": C("humanoid_caster", 18, 20, "ambermill_ghost_mage"),
    "Ambermill Warden": C("elemental_bruiser", 19, 20, "ambermill_warden"),
    "Magister Quillfire": C("humanoid_caster", 20, 20, "magister_quillfire", True, 1.7),
    # The Decrepit Ferry
    "Drowned Deckhand": C("undead_basic", 16, 18, "drowned_deckhand"),
    "Drowned Ferryman": C("undead_basic", 18, 18, "drowned_ferryman", True, 1.7),
}

SOUTH_LEVEL_PATCH = {"Lord Godfrey's Remnant": (19, 19)}          # the Pyrewood boss, now an L19 finale

SOUTH_OVERRIDES = {
    "Diseased Wolf": [16, 18], "Zombie Bear": [16, 18], "Carrion Bird": [16, 18], "Rotting Ghoul": [16, 18],
    "Feral Rotting Kobold": [16, 18], "Marsh Ooze": [16, 18], "Swamp Ghoul": [16, 18], "Bloated Corpse": [16, 18],
    "Skeletal Sentry": [17, 18], "Worgen Ambusher": [17, 19], "Feral Worgen": [17, 19], "Pyrewood Cultist": [17, 19],
    "Feral Worgen Stalker": [18, 20],
}

SOUTH_ZONE = {
    "open_zone": {"name": "The Silverpine Pines", "creatures": {
        "Diseased Wolf": 3, "Zombie Bear": 2, "Carrion Bird": 2, "Rotting Ghoul": 2}},
    "subzones": {
        "Bucklebree Farm": {"name": "Bucklebree Farm", "creatures": {
            "Blightfed Hog": 4, "Barn Ghoul": 3, "Zombie Bear": 1, "Tusk-Mother Gorra": 0}},
        "Olivia's Pond": {"name": "Olivia's Pond", "creatures": {
            "Marsh Ooze": 3, "Swamp Ghoul": 3, "Bloated Corpse": 2, "The Bloated One": 0}},
        "Deep Elem Mine": {"name": "Deep Elem Mine", "creatures": {
            "Feral Rotting Kobold": 3, "Deep Elem Digger": 3, "Mine Shambler": 3, "Gnawbone the Foreman": 0}},
        "Valgan's Field": {"name": "Valgan's Field", "creatures": {
            "Field Deserter": 3, "Battlefield Wight": 3, "Skeletal Sentry": 2, "Deathguard Captain": 0}},
        "The Decrepit Ferry": {"name": "The Decrepit Ferry", "creatures": {
            "Drowned Deckhand": 4, "Carrion Bird": 2, "Rotting Ghoul": 1, "Drowned Ferryman": 0}},
        "Ambermill": {"name": "Ambermill", "creatures": {
            "Ambermill Ghost-Mage": 3, "Ambermill Warden": 3, "Carrion Bird": 1, "Magister Quillfire": 0}},
        "Pyrewood Village": {"name": "Pyrewood Village", "creatures": {
            "Worgen Ambusher": 3, "Feral Worgen": 3, "Pyrewood Cultist": 3, "Lord Godfrey's Remnant": 0}},
        "Berard's Talon": {"name": "Berard's Talon", "creatures": {
            "Crag Stalker": 4, "Talon Wraith": 3, "Rotting Ghoul": 1, "Berard the Forgotten": 0}},
        "Beren's Peril": {"name": "Beren's Peril", "creatures": {
            "Feral Worgen Stalker": 3, "Peril Packmaster": 3, "Worgen Ambusher": 2, "Bloodmaw the Alpha": 0}},
        "The Greymane Wall": {"name": "The Greymane Wall", "creatures": {
            "Wallbreaker Worgen": 3, "Wall Wraith": 3, "Feral Worgen Stalker": 2, "Gilnean Wall-Warden": 0}},
    },
}


def south_pools():
    P = {}
    P["Tusk-Mother Gorra"] = [             # L17 -> ilvl 20
        mk("Gorra's Tusk-Splitter", "main_hand", "of the Juggernaut", 20,
           "A tusk the length of a forearm, hafted on a fence-post. It has already split something.", weapon_type="axe_2h"),
        mk("Boarhide Greaves", "legs", "of the Wolf", 20,
           "Thick, bristled, and stiff as a plank. Warm in winter and loud in a stairwell.", armor_type="leather"),
        mk("Sow-Mother's Girdle", "waist", "of the Bear", 20,
           "Woven rope and a chewed brass buckle. It has fed a very large family.", armor_type="mail"),
        mk("Bristle-Studded Bracers", "wrist", "of the Tiger", 20,
           "Every bristle is a small warning. You've been warned.", armor_type="leather"),
    ]
    P["The Bloated One"] = [               # L18 -> ilvl 21
        mk("Bloated One's Gut-Splitter", "main_hand", "of the Soldier", 21,
           "A rusted cleaver, bloated at the blade with something that won't scrape off.", weapon_type="axe_1h"),
        mk("Swollen Mire-Robe", "chest", "of the Prophet", 21,
           "Soaked, stretched and glowing faintly green. It has a pulse.", armor_type="cloth"),
        mk("Marsh-Gas Pendant", "neck", "of the Seer", 21,
           "A vial of something that was never meant to be bottled. It whispers."),
        mk("Rot-Taut Waders", "feet", "of the Whale", 21,
           "Skin-tight, damp, and permanently smelling of the pond floor.", armor_type="leather"),
    ]
    P["Gnawbone the Foreman"] = [          # L18 -> ilvl 21
        mk("Foreman's Bone Pick", "main_hand", "of the Champion", 21,
           "A pick carved from a femur. The foreman insisted on the finest materials.", weapon_type="mace_1h"),
        mk("Deep Elem Hardhat", "head", "of the Defender", 21,
           "Battered iron over padded leather. It has survived three cave-ins and a mutiny.", armor_type="mail"),
        mk("Foreman's Tally Ring", "ring", "of the Tactician", 21,
           "Engraved with every ore cart he ever lost. It's a long list."),
        mk("Pit-Stained Work Gloves", "hands", "of the Bandit", 21,
           "The thumbs are sewn from different hands entirely.", armor_type="leather"),
    ]
    P["Deathguard Captain"] = [            # L18 -> ilvl 21
        mk("Deathguard Captain's Longsword", "main_hand", "of the Champion", 21,
           "Issued in the Rotunda, carried since the Third War, never once sheathed.", weapon_type="sword_1h"),
        mk("Captain's Gorget of Duty", "neck", "of the Tactician", 21,
           "A gorget engraved with a motto in Common that no one now remembers."),
        mk("Deathguard Plate Cuirass", "chest", "of the Defender", 21,
           "Black plate, rimed with frost. The plume is still crisp.", armor_type="plate"),
        mk("Field-Commander's Signet", "ring", "of the Bastion", 21,
           "The ring of an officer who never stopped holding the line."),
    ]
    P["Drowned Ferryman"] = [              # L18 -> ilvl 21
        mk("Ferryman's Waterlogged Oar", "main_hand", "of the Hierophant", 21,
           "It pulls at your arms. It still wants to be in the water.", weapon_type="staff"),
        mk("Lakewater Cloak", "back", "of the Whale", 21,
           "Dripping, even when dry. The drip is a clock.", armor_type="cloth"),
        mk("Fare-Collector's Pouch Belt", "waist", "of the Monkey", 21,
           "Still heavy with coins from passengers that never reached the other bank.", armor_type="leather"),
        mk("Mooring-Rope Bracers", "wrist", "of the Bear", 21,
           "Tarred hemp wound over wet leather. Knots that never slip.", armor_type="mail"),
    ]
    P["Lord Godfrey's Remnant"] = [        # L19 -> ilvl 22
        mk("Godfrey's Pistol-Cane", "main_hand", "of the Marksman", 22,
           "A noble's walking cane with a barrel hidden in the shaft. Its last shot is still loaded.", weapon_type="gun"),
        mk("Pyrewood Lord's Surcoat", "chest", "of the Duelist", 22,
           "Embroidered in a house colour no one can name any more.", armor_type="leather"),
        mk("Remnant's Signet of Silverlaine", "ring", "of the Prophet", 22,
           "A cracked signet. The seal depicts a wolf and a tower."),
        mk("Godfrey's Gloves of Courtesy", "hands", "of the Archmage", 22,
           "Fine white calfskin, stained at the cuffs. They were removed for violence.", armor_type="cloth"),
    ]
    P["Berard the Forgotten"] = [          # L19 -> ilvl 22
        mk("Berard's Grief-Wrought Staff", "main_hand", "of the Necromancer", 22,
           "He carved it to remember something. It has forgotten what.", weapon_type="staff"),
        mk("Wraith-Thread Robe", "chest", "of the Sorcerer", 22,
           "Spun from a mourning shroud. It is warmer than it looks, and quieter.", armor_type="cloth"),
        mk("Forgotten Warder's Greaves", "legs", "of the Warder", 22,
           "Plate that has stood in the rain for a century. It has not noticed.", armor_type="plate"),
        mk("Talon-Stone Amulet", "neck", "of the Elder", 22,
           "A grey stone that remembers every name carved on the hill."),
    ]
    P["Bloodmaw the Alpha"] = [             # L20 -> ilvl 23
        mk("Bloodmaw's Fang-Cleaver", "main_hand", "of the Beast", 23,
           "A single, huge fang, set in a handle of bound sinew. It is not subtle.", weapon_type="sword_2h"),
        mk("Alpha's Pelt Mantle", "shoulder", "of the Hunt", 23,
           "Grey and black, still warm. Wolves leave you alone, for the wrong reasons.", armor_type="leather"),
        mk("Peril-Hunter's Boots", "feet", "of the Falcon", 23,
           "Quiet in the brush. Loud in the memory of whatever caught the last wearer.", armor_type="leather"),
        mk("Packleader's Claw Charm", "neck", "of the Tiger", 23,
           "A claw on a thong. Somewhere nearby, something raises its head."),
    ]
    P["Gilnean Wall-Warden"] = [            # L20 -> ilvl 23
        mk("Warden's Greymane Halberd", "main_hand", "of the Soldier", 23,
           "The blade is stamped with a lion's head. The shaft is worn smooth by a very long watch.", weapon_type="polearm"),
        mk("Wall-Sworn Tower Shield", "off_hand", "of the Bulwark", 23,
           "A slab of old Gilnean iron with an inscription: 'None shall pass, in or out.'", weapon_type="shield"),
        mk("Sentinel's Stone-Plate Pauldrons", "shoulder", "of the Bastion", 23,
           "Weathered like masonry. They hold the line, and say nothing of it.", armor_type="plate"),
        mk("Gilnean Border-Seal", "ring", "of the Champion", 23,
           "A heavy signet of the wall's own guard. It was never meant to be taken off."),
    ]
    P["Magister Quillfire"] = [             # L20 -> ilvl 23
        mk("Quillfire's Arcane Quill", "main_hand", "of the Archmage", 23,
           "It writes in light. Only the light knows what it's written.", weapon_type="wand"),
        mk("Ambermill Magister's Robes", "chest", "of the Invoker", 23,
           "Violet, silver-trimmed, scorched at the cuff. The scorches are deliberate.", armor_type="cloth"),
        mk("Waygate-Touched Circlet", "head", "of the Seer", 23,
           "A band of silver wire. When you close your eyes you see a door.", armor_type="cloth"),
        mk("Mill-Tower Spellbinder's Ring", "ring", "of the Sorcerer", 23,
           "Etched with a half-finished incantation. Finishing it is not recommended."),
    ]
    return P


# ======================================================================================================================
def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))

    cdata["creatures"].update(NORTH_CREATURES)
    cdata["creatures"].update(SOUTH_CREATURES)
    for n, (lo, hi) in SOUTH_LEVEL_PATCH.items():
        cdata["creatures"][n]["level_range"] = [lo, hi]

    z = edata["zones"]["Silverpine North"]
    z["open_zone"] = NORTH_ZONE["open_zone"]
    z["subzones"] = NORTH_ZONE["subzones"]
    z["level_overrides"] = {k: list(v) for k, v in NORTH_OVERRIDES.items()}
    z = edata["zones"]["Silverpine South"]
    z["open_zone"] = SOUTH_ZONE["open_zone"]
    z["subzones"] = SOUTH_ZONE["subzones"]
    z["level_overrides"] = {k: list(v) for k, v in SOUTH_OVERRIDES.items()}

    out = {"_notes": "Silverpine rebuild boss / named-rare loot (2026-10-23). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(north_pools())
    out.update(south_pools())
    (ROOT / "data/loot/silverpine_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"Silverpine: creatures +{len(NORTH_CREATURES) + len(SOUTH_CREATURES)}, pools {len(out) - 1}, items {n}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
