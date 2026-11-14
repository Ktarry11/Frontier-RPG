#!/usr/bin/env python3
"""Ragefire Chasm content pass (2026-10-21).

 * Boss levels set to the ladder (Oggleflint 15, Taragaman 16, Jergosh 16, Bazzalan 17).
 * 5 new trash types + 3 named optional rares (pinned in handbuilt_dungeons).
 * Encounter table for Orgrimmar > Ragefire Chasm.
 * Hand-crafted loot: ONE item drops per kill from a pool of 4 (rares: 3-4);
   item_level = boss level + 3, primary + secondary stats, spread across archetypes.
 * Replaces data/loot/ragefire_chasm_boss_loot.json (old ilvl-16, primary-only pools).

Run:  python3 tools/build_ragefire_content.py && python3 tools/generate_creatures.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    "Ragefire Digger": C("humanoid_ranged", 13, 15, "ragefire_digger"),
    "Trogg Skullcrusher": C("humanoid_warrior", 14, 16, "trogg_skullcrusher"),
    "Searing Blade Pyromancer": C("humanoid_caster", 14, 16, "searing_blade_pyromancer"),
    "Searing Blade Ward-Priest": C("humanoid_caster", 14, 16, "searing_blade_wardpriest"),
    "Cinder Salamander": C("beast_fast", 14, 16, "cinder_salamander"),
    # optional named rares (pinned, one each) - chase pools below
    "Grulgash the Pitbreaker": C("humanoid_warrior", 14, 14, "grulgash_pitbreaker", True, 1.6),
    "Acolyte Zhurra Bloodhex": C("humanoid_caster", 15, 15, "zhurra_bloodhex", True, 1.6),
    "Cinderfang": C("beast_fast", 16, 16, "cinderfang", True, 1.7),
}

# existing creature fixes: boss levels / kits
FIXES = {
    "Oggleflint": {"level_range": [15, 15]},
    "Taragaman the Hungerer": {"level_range": [16, 16]},
    "Jergosh the Invoker": {"level_range": [16, 16]},
    "Bazzalan": {"level_range": [17, 17]},
    "Ragefire Trogg": {"level_range": [13, 16]},
}

CAVE = {"name": "Ragefire Chasm", "creatures": {
    "Ragefire Trogg": 3, "Ragefire Shaman": 2, "Ragefire Digger": 2, "Trogg Skullcrusher": 1,
    "Searing Blade Cultist": 2, "Searing Blade Fanatic": 2, "Searing Blade Invoker": 1,
    "Searing Blade Pyromancer": 1, "Searing Blade Ward-Priest": 1,
    "Voidwalker Minion": 1, "Molten Elemental": 2, "Cinder Salamander": 1, "Earthborer": 1,
    "Oggleflint": 0, "Taragaman the Hungerer": 0, "Jergosh the Invoker": 0, "Bazzalan": 0,
    "Grulgash the Pitbreaker": 0, "Acolyte Zhurra Bloodhex": 0, "Cinderfang": 0}}

QUEST_DROPS = {
    "Ragefire Digger": {"item_id": "ragefire_ore_sample", "name": "Ragefire Ore Sample", "category": "quest",
                        "description": "Black rock shot through with orange veins. Still faintly warm, still faintly angry.",
                        "chance": 0.55},
    "Molten Elemental": {"item_id": "ragefire_ore_sample", "name": "Ragefire Ore Sample", "category": "quest",
                         "description": "Black rock shot through with orange veins. Still faintly warm, still faintly angry.",
                         "chance": 0.35},
    "Searing Blade Pyromancer": {"item_id": "searing_ritual_ash", "name": "Searing Ritual Ash", "category": "quest",
                                 "description": "Grey ash that smells of sulphur and iron. Nobody burns this by accident.",
                                 "chance": 0.5},
    "Searing Blade Cultist": {"item_id": "searing_ritual_ash", "name": "Searing Ritual Ash", "category": "quest",
                              "description": "Grey ash that smells of sulphur and iron. Nobody burns this by accident.",
                              "chance": 0.3},
}


def pools():
    P = {}
    # Oggleflint (L15 -> 18): warband melee. 2H dps axe / tank shoulders / shaman totem / druid-tank ring
    P["Oggleflint"] = [
        make("Warlord's Rending Cleaver", "main_hand", "of the Gladiator", 18,
             "A trogg-forged blade the size of a door. It has been used as one.", weapon_type="axe_2h"),
        make("Warband Bulwark Pauldrons", "shoulder", "of the Defender", 18,
             "Slab plate chipped by a hundred raiders' hammers. It remembers every one.", armor_type="plate"),
        make("Cavespeaker's Thunder-Totem", "ranged", "of the Restorer", 18,
             "A rune-cut bone that hums when the stone shifts. Healers say it calms them.", weapon_type="totem"),
        make("Bear-Claw Signet", "ring", "of the Ironfur", 18,
             "Too small for trogg fingers - taken as tribute, not worn."),
    ]
    # Taragaman (L16 -> 19): fire hunger. fire staff / caster neck / leather belt / plate legs
    P["Taragaman the Hungerer"] = [
        make("Cinder-Hearted Staff", "main_hand", "of Fiery Wrath", 19,
             "The Hungerer's spirit still burns at its tip. It wants feeding.", weapon_type="staff"),
        make("Enslaved Cinderspirit Pendant", "neck", "of the Invoker", 19,
             "A fragment of the elemental Taragaman bound to his will. It has opinions."),
        make("Felscorched Waistguard", "waist", "of the Hunt", 19,
             "The leather never stopped smoldering.", armor_type="leather"),
        make("Lavaforged Legguards", "legs", "of the Champion", 19,
             "Plate poured, not hammered. It cools slower than it should.", armor_type="plate"),
    ]
    # Jergosh (L16 -> 19): cult invoker. shadow wand / healer robe / mp5 ring / caster dagger
    P["Jergosh the Invoker"] = [
        make("Invoker's Grasp", "ranged", "of Shadow Wrath", 19,
             "Still warm from the last Immolate it channeled.", weapon_type="wand"),
        make("Searing Blade Ritual Robes", "chest", "of the Prophet", 19,
             "A cult that answers to no orc, in a cloth that answers to nobody.", armor_type="cloth"),
        make("Warlock's Binding Ring", "ring", "of the Seer", 19,
             "The binding runes are still legible, if you dare read them aloud."),
        make("Voidcaller's Kris", "main_hand", "of the Mind's Eye", 19,
             "The blade is cold. The hilt is colder. Neither is yours yet.", weapon_type="dagger"),
    ]
    # Bazzalan (L17 -> 20): the Sinister Edge. 1H sword / crossbow / caster hood / tank shield
    P["Bazzalan"] = [
        make("Bazzalan's Sinister Edge", "main_hand", "of the Bandit", 20,
             "Quenched in poison and half-hidden grudges.", weapon_type="sword_1h"),
        make("Cultist's Repeater", "ranged", "of the Marksman", 20,
             "Fel-etched bolts load themselves. Do not ask who taught them.", weapon_type="crossbow"),
        make("Shadowcrown Hood", "head", "of the Archmage", 20,
             "Stitched from the cult's old ritual veils. It does not shed.", armor_type="cloth"),
        make("Bulwark of the Searing Throne", "off_hand", "of the Bulwark", 20,
             "The throne room's door, cut down to a shield. It still slams.", weapon_type="shield"),
    ]
    # --- optional named rares ---------------------------------------------
    P["Grulgash the Pitbreaker"] = [   # L14 -> 17
        make("Pitbreaker's Pick", "main_hand", "of Striking", 17,
             "A miner's tool, sharpened by a trogg who knows exactly what it's for.", weapon_type="axe_1h"),
        make("Ore-Dusted Leggings", "legs", "of the Ironfur", 17,
             "Stiff with a century of cave dust. It deflects more than it looks like.", armor_type="leather"),
        make("Sootblack Miner's Cap", "head", "of the Soldier", 17,
             "A lantern hook, a dent, and a stubborn will to live.", armor_type="mail"),
    ]
    P["Acolyte Zhurra Bloodhex"] = [    # L15 -> 18
        make("Bloodhex Mantle", "shoulder", "of the Hierophant", 18,
             "Stained in a way that doesn't wash. The wearer heals anyway.", armor_type="cloth"),
        make("Zhurra's Sacrificial Kris", "main_hand", "of the Tactician", 18,
             "Notched on the pommel, once for each altar.", weapon_type="dagger"),
        make("Hexbinder's Wristwraps", "wrist", "of the Spell Breaker", 18,
             "Knots in the cord keep a curse from slipping.", armor_type="cloth"),
        make("Blood-Sworn Fist-Blades", "main_hand", "of the Assassin", 18,
             "Cult-issue claws. Zhurra preferred talking to the people she cut.", weapon_type="fist_weapon"),
    ]
    P["Cinderfang"] = [                # L16 -> 19
        make("Cinderfang Pelt-Cloak", "back", "of the Wolf", 19,
             "Scorched fur that has never once been cold.", armor_type="cloth"),
        make("Emberclaw Grips", "hands", "of the Tiger", 19,
             "Salamander hide, stitched while it was still sulking.", armor_type="leather"),
        make("Salamander-Tooth Spear", "main_hand", "of the Beast", 19,
             "A single curved fang on a charred haft. It wants to be thrown.", weapon_type="polearm"),
        make("Emberheart Amulet", "neck", "of Spellfire", 19,
             "A living coal, caged in black glass. Warm in the cold, loud in the quiet."),
    ]
    return P


def main():
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["creatures"].update(NEW_CREATURES)
    for n, patch in FIXES.items():
        data["creatures"][n].update(patch)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["zones"]["Orgrimmar"]["caves"]["Ragefire Chasm"] = CAVE
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    for creature, drop in QUEST_DROPS.items():
        data["drops"][creature] = [drop]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = {"_notes": "Ragefire Chasm boss + named-rare loot (2026-10-21). ONE item drops per kill from "
                     "the pool. item_level = boss level + 3; real loot formulas "
                     "(tools/build_durotar_content.make), primary + secondary stats."}
    out.update(pools())
    (ROOT / "data/loot/ragefire_chasm_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
