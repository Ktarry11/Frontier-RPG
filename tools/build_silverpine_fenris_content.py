#!/usr/bin/env python3
"""Fenris Isle (17-22) + Shadowpine Altar (20-24) content (2026-10-23).  Idempotent.

    cd tools && python3 generate_creatures.py       (after editing kits)
    python3 tools/build_silverpine_fenris_content.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.build_durotar_content import make as mk, C  # noqa: E402

NEW = {
    "Tidewrack Crawler": C("vermin_sneaky", 17, 19, "tidewrack_crawler"),
    "Manor Hound": C("beast_basic", 19, 21, "manor_hound"),
    "Ashbury's Footman": C("undead_basic", 19, 21, "ashburys_footman"),
    "Drowned Harpooner": C("humanoid_ranged", 19, 21, "drowned_harpooner"),
    "Cur-Warden": C("humanoid_caster", 19, 21, "cur_warden"),
    # Shadowpine Altar
    "Shadowpine Cultist": C("humanoid_caster", 20, 22, "shadowpine_cultist"),
    "Altar Bonewalker": C("undead_basic", 20, 22, "altar_bonewalker"),
    "Moonhowl Worgen": C("beast_fast", 21, 23, "moonhowl_worgen"),
    "Altar Wraith": C("undead_basic", 21, 23, "altar_wraith"),
    "Bonewarden Aldric": C("undead_basic", 21, 21, "bonewarden_aldric", boss=True, mult=2.0),
}
# existing creatures: (lo, hi, kit or None, boss_multiplier or None)
PATCH = {
    "Feral Worgen Stalker": (17, 19, "fenris_stalker", None),
    "Rabid Wolf": (17, 19, "rabid_shorewolf", None),
    "Grave Worg": (18, 20, "grave_worg", None),
    "Bone-Strewn Cur": (18, 20, "bone_cur", None),
    "Waterlogged Wretch": (18, 20, "waterlogged_wretch", None),
    "Bilge Rat Swarm": (18, 20, "bilge_swarm", None),
    "Ancient Curse-Beast": (21, 21, "curse_beast", 2.0),
    "Baron Ashbury": (22, 22, "baron_ashbury_fenris", 2.2),
    "Captain's Ghost": (22, 22, "captains_ghost_fenris", 2.2),
    "The Alpha Cur": (22, 22, "alpha_cur_fenris", 2.2),
    "Curse Keeper Tael": (22, 22, "curse_keeper_tael", 2.2),
    "Alpha Fenris": (24, 24, "alpha_fenris", 2.6),
}

ZONE = {
    "open_zone": {"name": "The Cursed Shore", "creatures": {
        "Feral Worgen Stalker": 3, "Rabid Wolf": 2, "Cursed Villager": 2, "Isle Banshee": 2, "Tidewrack Crawler": 2,
        "Ancient Curse-Beast": 0}},
    "subzones": {
        "Bloodmoon Village": {"name": "Bloodmoon Village", "creatures": {"Cursed Villager": 3, "Rabid Wolf": 1}},
        "Fenris Proper": {"name": "Fenris Proper", "creatures": {
            "Worgen Keeper": 3, "Fenris Guardian": 2, "Cursed Noble": 2, "Manor Hound": 3, "Ashbury's Footman": 3, "Baron Ashbury": 0}},
        "The Drowned Docks": {"name": "The Drowned Docks", "creatures": {
            "Drowned Sailor": 3, "Bilge Rat Swarm": 2, "Waterlogged Wretch": 3, "Drowned Harpooner": 2, "Captain's Ghost": 0}},
        "Cur's Grave": {"name": "Cur's Grave", "creatures": {
            "Grave Worg": 3, "Bone-Strewn Cur": 3, "Feral Packmaster": 2, "Cur-Warden": 2, "The Alpha Cur": 0}},
    },
    "level_overrides": {
        "Cursed Villager": [17, 19], "Isle Banshee": [18, 20], "Worgen Keeper": [19, 21], "Fenris Guardian": [19, 21],
        "Cursed Noble": [19, 21], "Drowned Sailor": [18, 20], "Feral Packmaster": [19, 21],
    },
    "caves": {"Shadowpine Altar": {"name": "Shadowpine Altar", "creatures": {
        "Shadowpine Cultist": 3, "Altar Bonewalker": 3, "Moonhowl Worgen": 3, "Altar Wraith": 2, "Worgen Warrior": 2,
        "Bonewarden Aldric": 0, "Curse Keeper Tael": 0, "Alpha Fenris": 0}}},
}


def pools():
    P = {}
    P["Ancient Curse-Beast"] = [          # L21 -> ilvl 24
        mk("Curse-Beast Hide Jerkin", "chest", "of the Bear", 24, "Matted, stitched with its own sinew, and still faintly warm.", armor_type="leather"),
        mk("Ironclaw of the Isle", "main_hand", "of the Tiger", 24, "A claw the length of a forearm, bound to a bone grip.", weapon_type="dagger"),
        mk("Rotted Heartstone Pendant", "neck", "of the Soldier", 24, "Something that was once a heart, calcified and heavy."),
        mk("Cursed Fang Greaves", "legs", "of the Defender", 24, "Plate studded with fangs. Not all of them were the beast's.", armor_type="plate"),
    ]
    P["Baron Ashbury"] = [                # L22 -> ilvl 25
        mk("Baron's Signet of Fenris", "ring", "of the Seer", 25, "The family seal, worn thin by a hand that would not let go."),
        mk("Ashbury's Gilded Rapier", "main_hand", "of the Duelist", 25, "A duelling blade for a man who never lost a duel and never forgave one.", weapon_type="sword_1h"),
        mk("Mouldering Manor Cloak", "back", "of the Prophet", 25, "Velvet gone to moss. It still hangs with great dignity.", armor_type="cloth"),
        mk("Footman's Last Orders Mail", "chest", "of the Soldier", 25, "Mail issued to a house guard who was never relieved.", armor_type="mail"),
    ]
    P["Captain's Ghost"] = [               # L22 -> ilvl 25
        mk("Drowned Captain's Cutlass", "main_hand", "of the Bandit", 25, "Salt-pitted but wickedly sharp. It drips on dry decks.", weapon_type="sword_1h"),
        mk("Barnacled Tricorn", "head", "of the Whale", 25, "Crusted with shells, with a fish somehow still living in the brim.", armor_type="leather"),
        mk("Spectral Logbook Charm", "trinket", "of the Mind's Eye", 25, "The last entry reads only: the water is inside the ship."),
        mk("Harpooner's Brine Gloves", "hands", "of the Marksman", 25, "Waxed leather, stiff with salt and old blood.", armor_type="leather"),
    ]
    P["The Alpha Cur"] = [                 # L22 -> ilvl 25
        mk("Alpha's Gnawed Bone Club", "main_hand", "of the Champion", 25, "A thighbone worked into a club. Every notch is a tooth-mark.", weapon_type="mace_1h"),
        mk("Packmaster's Studded Collar", "neck", "of the Beast", 25, "A heavy collar. Some dog was very, very good."),
        mk("Cur-Hide Leggings", "legs", "of the Wolf", 25, "Patchwork of ten different pelts, all of them snarling.", armor_type="leather"),
        mk("Howling Skull Mantle", "shoulder", "of the Warder", 25, "A skull on each shoulder. They howl in a stiff wind.", armor_type="mail"),
    ]
    P["Bonewarden Aldric"] = [             # L21 -> ilvl 24
        mk("Aldric's Femur Hammer", "main_hand", "of the Juggernaut", 24, "Two-handed, ugly, and entirely made of someone's leg.", weapon_type="mace_2h"),
        mk("Bone-Ward Pauldrons", "shoulder", "of the Bastion", 24, "Overlapping plates of knitted rib. They knock when you walk.", armor_type="plate"),
        mk("Ritual Knucklebone Ring", "ring", "of the Necromancer", 24, "A ring of finger-bone, with a stone that watches."),
        mk("Wardens' Shroud Belt", "waist", "of the Hierophant", 24, "Burial linen, bound with knotted hair.", armor_type="cloth"),
    ]
    P["Curse Keeper Tael"] = [             # L22 -> ilvl 25
        mk("Tael's Moonlit Scepter", "main_hand", "of the Invoker", 25, "A silver rod tipped with a glass moon. It's never quite full.", weapon_type="staff"),
        mk("Keeper's Hexed Vestments", "chest", "of the Sorcerer", 25, "Robes cut so that every fold hides a smaller curse.", armor_type="cloth"),
        mk("Curse-Breaker's Bracers", "wrist", "of the Spell Breaker", 25, "Silvered leather bracers; they warm against a hex.", armor_type="leather"),
        mk("Pendant of the Last Rite", "neck", "of the Restorer", 25, "A small wooden holy symbol. It has been reused too many times."),
    ]
    P["Alpha Fenris"] = [                  # L24 -> ilvl 27
        mk("Fenris' Cursed Fang", "main_hand", "of the Hunt", 27, "A fang the length of a short sword, still wet at the root.", weapon_type="sword_1h"),
        mk("Alpha's Moonhide Hauberk", "chest", "of the Tiger", 27, "Silver-grey hide that shifts colour in moonlight.", armor_type="leather"),
        mk("Greaves of the Howling Dark", "feet", "of the Champion", 27, "Plate boots with claw-marks cut deep down both shins.", armor_type="plate"),
        mk("Moonbound Curse-Ring", "ring", "of the Archmage", 27, "A band that tightens each full moon and loosens after. It is a patient ring."),
    ]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cd = json.loads(cp.read_text())
    ep = ROOT / "data/creatures/encounters.json"
    ed = json.loads(ep.read_text())
    cd["creatures"].update(NEW)
    for n, (lo, hi, kit, mult) in PATCH.items():
        c = cd["creatures"][n]
        c["level_range"] = [lo, hi]
        c["ability_kit"] = kit
        if mult:
            c["boss_multiplier"] = mult
            c["is_boss"] = True
    ed["zones"]["Fenris Isle"] = ZONE
    ed["zones"].pop("Shadowpine Altar", None)
    out = {"_notes": "Fenris Isle + Shadowpine Altar boss/rare loot (2026-10-23). ONE item per kill from the pool; ilvl = creature level + 3."}
    out.update(pools())
    (ROOT / "data/loot/fenris_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    cp.write_text(json.dumps(cd, indent=2) + "\n")
    ep.write_text(json.dumps(ed, indent=2) + "\n")
    print(f"fenris content: +{len(NEW)} creatures, {len(PATCH)} patches, {len(out) - 1} pools")


if __name__ == "__main__":
    main()
