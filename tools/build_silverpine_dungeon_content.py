#!/usr/bin/env python3
"""Silverpine dungeon content (2026-10-23): Widow's Lair (17-19), Ambermill Tower (21-23), Shadowfang Keep (19-25).  Idempotent.

    cd tools && python3 generate_creatures.py        (after editing kits)
    python3 tools/build_silverpine_dungeon_content.py

  * new trash creatures + boss level / kit / multiplier patches -> data/creatures/creatures.json
  * cave encounter tables (zones[<region>]["caves"][<cave>]) -> data/creatures/encounters.json
  * hand-crafted boss loot pools (one item per kill from a pool of 4, ilvl = level + 3) -> data/loot/silverpine_dungeon_loot.json
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

NEW_CREATURES = {
    # Widow's Lair
    "Lair Hatchling": C("vermin_swarm", 17, 18, "lair_hatchling"),
    "Silkbound Weaver": C("vermin_sneaky", 17, 19, "silkbound_weaver"),
    "Brood Warden": C("beast_large", 18, 19, "brood_warden"),
    "Venom Stalker": C("beast_fast", 18, 19, "venom_stalker"),
    # Ambermill Tower
    "Tome Wraith": C("humanoid_caster", 21, 23, "tome_wraith"),
    "Animated Spellblade": C("elemental_bruiser", 22, 23, "animated_spellblade"),
    "Forsaken Alchemist": C("humanoid_caster", 21, 23, "forsaken_alchemist"),
    # Shadowfang Keep
    "Keep Worg": C("beast_fast", 19, 20, "keep_worg"),
    "Slavering Worg": C("beast_fast", 20, 21, "slavering_worg"),
    "Wolfguard Worg": C("beast_large", 21, 22, "wolfguard_worg"),
    "Shadowfang Moonwalker": C("humanoid_caster", 21, 22, "shadowfang_moonwalker"),
    "Shadowfang Darksoul": C("humanoid_caster", 21, 23, "shadowfang_darksoul"),
    "Arugal's Voidwalker": C("elemental_bruiser", 22, 23, "arugal_voidwalker"),
    "Haunted Servitor": C("undead_basic", 22, 23, "haunted_servitor"),
    "Tormented Officer": C("undead_basic", 22, 24, "tormented_officer"),
    "Wailing Guardsman": C("undead_basic", 20, 22, "wailing_guardsman"),
    "Deathsworn Captain": C("humanoid_warrior", 23, 24, "deathsworn_captain"),
    "Son of Arugal": C("humanoid_warrior", 23, 25, "son_of_arugal"),
    "Lupine Horror": C("beast_large", 24, 25, "lupine_horror"),
}

# boss patches: (level, boss_multiplier, ability_kit or None to keep)
BOSS_PATCH = {
    "Broodmother Silka": (17, 2.0, None), "Weaver Skitter": (18, 2.1, None), "Matriarch Velaxis": (19, 2.4, None),
    "Magister Hawren": (22, 2.0, "magister_hawren"), "Apothecary Helbrim": (23, 2.0, "apothecary_helbrim"),
    "Archmage Atiesh": (23, 2.4, "archmage_atiesh"),
    "Rethilgore": (21, 2.0, None), "Razorclaw the Butcher": (22, 2.0, None), "Baron Silverlaine": (23, 2.2, None),
    "Fenrus the Devourer": (24, 2.2, None), "Archmage Arugal": (25, 2.6, None),
}

CAVES = {
    "Silverpine North": {"Widow's Lair": {"name": "Widow's Lair", "creatures": {
        "Lair Hatchling": 5, "Silkbound Weaver": 3, "Brood Warden": 3, "Venom Stalker": 3,
        "Broodmother Silka": 0, "Weaver Skitter": 0, "Matriarch Velaxis": 0}}},
    "Silverpine South": {
        "Ambermill Tower": {"name": "Ambermill Tower", "creatures": {
            "Kirin Tor Mage": 3, "Forsaken Mage": 3, "Arcane-Bound Imp": 2, "Tome Wraith": 3, "Animated Spellblade": 3,
            "Forsaken Alchemist": 2, "Magister Hawren": 0, "Apothecary Helbrim": 0, "Archmage Atiesh": 0}},
        "Shadowfang Keep": {"name": "Shadowfang Keep", "creatures": {
            "Forsaken Warrior": 2, "Forsaken Knight": 2, "Worgen Warrior": 2, "Keep Worg": 3, "Slavering Worg": 3,
            "Wolfguard Worg": 2, "Shadowfang Moonwalker": 3, "Shadowfang Darksoul": 3, "Arugal's Voidwalker": 2,
            "Haunted Servitor": 2, "Tormented Officer": 2, "Wailing Guardsman": 3, "Deathsworn Captain": 1,
            "Son of Arugal": 2, "Lupine Horror": 1,
            "Rethilgore": 0, "Razorclaw the Butcher": 0, "Baron Silverlaine": 0, "Fenrus the Devourer": 0, "Archmage Arugal": 0}},
    },
}
TOWER_LEVELS = {"Kirin Tor Mage": [21, 23], "Forsaken Mage": [21, 23], "Arcane-Bound Imp": [21, 23]}


def pools():
    P = {}
    # ---------------------------------------------------------------- WIDOW'S LAIR
    P["Broodmother Silka"] = [             # L17 -> ilvl 20
        mk("Brood-Fang Stiletto", "main_hand", "of the Assassin", 20,
           "A single fang of the first brood, set in a handle of silk-wound bone. It remembers the hunt.", weapon_type="dagger"),
        mk("Egg-Sac Sash", "waist", "of the Wolf", 20,
           "Soft, sticky and unexpectedly strong. Do not ask what is still in the knots.", armor_type="leather"),
        mk("Web-Spun Mantle", "shoulder", "of the Prophet", 20,
           "Silk drawn thin as breath and wound by something with eight opinions.", armor_type="cloth"),
        mk("Broodmother's Hatchling Locket", "neck", "of the Restorer", 20,
           "A locket of amber with a tiny, motionless thing inside. It is only asleep."),
    ]
    P["Weaver Skitter"] = [                # L18 -> ilvl 21
        mk("Silk-Wrapped Knuckles", "main_hand", "of the Bandit", 21,
           "Layered web hardened into a fist. It pulls back slightly every time you throw it.", weapon_type="fist_weapon"),
        mk("Weaver's Chitin Greaves", "legs", "of the Bear", 21,
           "Segmented, glossy, and a little too flexible at the knee.", armor_type="mail"),
        mk("Gossamer Cowl", "head", "of the Seer", 21,
           "A cowl of silk so fine you can see through it, and so can everything else.", armor_type="cloth"),
        mk("Venomfang Signet", "ring", "of the Tiger", 21,
           "A fang bent into a ring. It stays warm on the finger."),
    ]
    P["Matriarch Velaxis"] = [             # L19 -> ilvl 22
        mk("Widow's Spire", "main_hand", "of the Sorcerer", 22,
           "A staff of stacked, silk-bound vertebrae. It hums when anything walks near the web.", weapon_type="staff"),
        mk("Matriarch's Carapace Cuirass", "chest", "of the Defender", 22,
           "Black plate grown rather than forged. It has opinions about being worn.", armor_type="plate"),
        mk("Spinneret Gloves", "hands", "of the Hunt", 22,
           "Glossy leather with a faint spiral pattern. Your fingers will leave silk behind.", armor_type="leather"),
        mk("Shroud of Eight Eyes", "back", "of the Eagle", 22,
           "A cloak that never quite hangs the same way twice. It is looking around.", armor_type="cloth"),
    ]
    # ---------------------------------------------------------------- AMBERMILL TOWER
    P["Magister Hawren"] = [               # L22 -> ilvl 25
        mk("Hawren's Archive Staff", "main_hand", "of the Invoker", 25,
           "Capped in a violet gem the shape of a closed book. It occasionally reads aloud.", weapon_type="staff"),
        mk("Gallery-Warden's Hauberk", "chest", "of the Warder", 25,
           "Dalaran mail with a library's worth of tiny sigils beaten into every link.", armor_type="mail"),
        mk("Scholar's Quilted Cuffs", "wrist", "of the Mind's Eye", 25,
           "Cuffs stitched with a footnote that never ends.", armor_type="cloth"),
        mk("Quill of the Archivist", "main_hand", "of the Sorcerer", 25,
           "A long feather-quill, still wet. It writes your name, and then does not stop.", weapon_type="wand"),
    ]
    P["Apothecary Helbrim"] = [            # L23 -> ilvl 26
        mk("Helbrim's Flask-Mace", "main_hand", "of the Physician", 26,
           "A heavy glass mace, brimful of something that keeps almost, but never quite, boiling over.", weapon_type="mace_1h"),
        mk("Alchemist's Splash-Apron", "chest", "of the Restorer", 26,
           "Treated leather, stained in fourteen incompatible colours.", armor_type="leather"),
        mk("Reagent-Stained Gloves", "hands", "of the Necromancer", 26,
           "Yellow at the fingertips, green at the knuckles, and never washed.", armor_type="cloth"),
        mk("Alembic Signet", "ring", "of the Tiger", 26,
           "A ring that is also a tiny still. A drop condenses at the bezel every few hours."),
    ]
    P["Archmage Atiesh"] = [               # L23 -> ilvl 26
        mk("Orrery Rod", "main_hand", "of the Archmage", 26,
           "A rod ringed with tiny rotating spheres. Each is a world; each is lit.", weapon_type="staff"),
        mk("Observatory Star-Robes", "chest", "of the Prophet", 26,
           "Midnight cloth stitched with the actual night sky. One star is the wrong colour.", armor_type="cloth"),
        mk("Spellblade-Guard Tower Shield", "off_hand", "of the Bulwark", 26,
           "A flat plate of animated steel that swings to meet a blow before you do.", weapon_type="shield"),
        mk("Waygate Shard Pendant", "neck", "of the Invoker", 26,
           "A violet sliver of the old waygate. Hold it, and you hear a door that isn't there."),
    ]
    # ---------------------------------------------------------------- SHADOWFANG KEEP
    P["Rethilgore"] = [                    # L21 -> ilvl 24
        mk("Rethilgore's Chain-Flail", "main_hand", "of the Soldier", 24,
           "A hound-master's flail: three links, one heavy knot, and a lot of repeated use.", weapon_type="mace_1h"),
        mk("Kennel-Master's Hide Coat", "chest", "of the Wolf", 24,
           "Chewed at the hem by animals that stopped biting once they were in charge.", armor_type="leather"),
        mk("Collar of the Lead Hound", "neck", "of the Beast", 24,
           "A studded collar. It still has a name engraved on the underside."),
        mk("Hound-Warden's Gauntlets", "hands", "of the Defender", 24,
           "Bite-proof plate, scarred by every dog in the keep.", armor_type="plate"),
    ]
    P["Razorclaw the Butcher"] = [          # L22 -> ilvl 25
        mk("Razorclaw's Meat-Cleaver", "main_hand", "of the Juggernaut", 25,
           "A two-handed cleaver with a hook for a handle-end. The hook sees plenty of use.", weapon_type="axe_2h"),
        mk("Butcher's Apron Leggings", "legs", "of the Tiger", 25,
           "Stiff with old stains and not quite as dry as they should be.", armor_type="leather"),
        mk("Hooked Chain Belt", "waist", "of the Gladiator", 25,
           "A belt of S-hooks and short chain. Each hook has hung something.", armor_type="mail"),
        mk("Skinning-Knife Band", "ring", "of the Assassin", 25,
           "A thin band of steel sharpened on the inside. It is not a comfortable ring."),
    ]
    P["Baron Silverlaine"] = [             # L23 -> ilvl 26
        mk("Silverlaine's Dress Sabre", "main_hand", "of the Duelist", 26,
           "A noble's sabre, thin and balanced, and entirely uninterested in dignity.", weapon_type="sword_1h"),
        mk("Baron's Moth-Eaten Mantle", "shoulder", "of the Sorcerer", 26,
           "Velvet and silver braid, gnawed by the heirs it outlived.", armor_type="cloth"),
        mk("Hall-of-the-Damned Shield", "off_hand", "of the Bulwark", 26,
           "A tall shield painted with a crest nobody left alive can read.", weapon_type="shield"),
        mk("Signet of the Silverlaine Line", "ring", "of the Tactician", 26,
           "A cracked family ring. Its stone is the colour of old moonlight."),
    ]
    P["Fenrus the Devourer"] = [           # L24 -> ilvl 27
        mk("Fenrus' Devouring Maw", "main_hand", "of the Champion", 27,
           "A two-handed maul with a jaw-shaped head. The teeth are real.", weapon_type="mace_2h"),
        mk("Crypt-Stalker's Hide Vest", "chest", "of the Hunt", 27,
           "Cured from something that fed in the crypt and did not feed lightly.", armor_type="leather"),
        mk("Devourer's Bone-Plate Greaves", "legs", "of the Bastion", 27,
           "Plate hammered over actual bone. The marrow's still warm.", armor_type="plate"),
        mk("Mantle of the Hollow Pup", "back", "of the Spell Breaker", 27,
           "A small grey cloak with a tiny hood. It is distressingly sized for the previous owner.", armor_type="cloth"),
    ]
    P["Archmage Arugal"] = [               # L25 -> ilvl 28
        mk("Arugal's Voidcaller Staff", "main_hand", "of the Archmage", 28,
           "The staff that opened the first door, and has been open ever since.", weapon_type="staff"),
        mk("Cloak of the Cursed Archmage", "back", "of the Sorcerer", 28,
           "Silver-grey wool with a moon-pattern that is, at certain angles, a wolf.", armor_type="cloth"),
        mk("Arugal's Shadow-Silk Robes", "chest", "of the Necromancer", 28,
           "Cut for a man who valued his reflection. It is no longer anywhere in the lining.", armor_type="cloth"),
        mk("Wolf-Fang Pendant of Arugal", "neck", "of the Wolf", 28,
           "A fang carved with a spiral, strung on three strands of dark hair."),
    ]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))
    cdata["creatures"].update(NEW_CREATURES)
    for name, (lvl, mult, kit) in BOSS_PATCH.items():
        c = cdata["creatures"][name]
        c["level_range"] = [lvl, lvl]
        c["boss_multiplier"] = mult
        if kit:
            c["ability_kit"] = kit
            c.pop("kit", None)
    for n, rng in TOWER_LEVELS.items():
        cdata["creatures"][n]["level_range"] = rng
    for region, caves in CAVES.items():
        edata["zones"][region].setdefault("caves", {}).update(caves)
    out = {"_notes": "Silverpine dungeon boss loot (2026-10-23): Widow's Lair, Ambermill Tower, Shadowfang Keep. ONE item drops per "
                     "kill from the pool. item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/silverpine_dungeon_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"dungeon content: +{len(NEW_CREATURES)} creatures, {len(BOSS_PATCH)} boss patches, {len(out) - 1} pools / {n} items")


if __name__ == "__main__":
    main()
