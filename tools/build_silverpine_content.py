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
def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())

    cdata["creatures"].update(NORTH_CREATURES)
    z = edata["zones"]["Silverpine North"]
    z["open_zone"] = NORTH_ZONE["open_zone"]
    z["subzones"] = NORTH_ZONE["subzones"]
    z["level_overrides"] = {k: list(v) for k, v in NORTH_OVERRIDES.items()}

    pools = north_pools()
    out = {"_notes": "Silverpine rebuild boss / named-rare loot (2026-10-23). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools)
    (ROOT / "data/loot/silverpine_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"Silverpine: creatures +{len(NORTH_CREATURES)}, pools {len(out) - 1}, items {n}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")


if __name__ == "__main__":
    main()
