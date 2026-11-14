#!/usr/bin/env python3
"""Razorfen Kraul content pass (2026-10-21).  Idempotent.

  PYTHONPATH=. python3 tools/build_razorfen_content.py && python3 tools/generate_creatures.py

What was broken: the cave's table held two generic trash types (Quilboar Warrior/Shaman) with the six bosses under a
bogus "bosses" key the spawn code never reads, none of the six bosses had an ability kit, no boss had a loot pool, and
the only quest was a one-line explore.

Ladder (Kyle's confirmed table): trash 25-31 | Roogug 28 | Aggem Thorncurse 30 | Death Speaker Jargba 30 |
Overlord Ramtusk 32 | Agathelos the Raging 32 | Charlga Razorflank 34.   Named rares: Blind Hunter 29, Earthcaller
Halmgar 31, Thornjaw the Gorger 31 (pinned in side nooks).  Trash is HAND-PLACED (tools/handbuilt_razorfen.TRASH).
LOOT: ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    "Razorfen Spearhide": C("humanoid_warrior", 25, 28, "razorfen_spearhide"),
    "Razorfen Defender": C("humanoid_warrior", 26, 30, "razorfen_defender"),
    "Razorfen Beast Trainer": C("humanoid_warrior", 26, 29, "razorfen_beast_trainer"),
    "Razorfen Handler": C("humanoid_ranged", 25, 29, "razorfen_handler"),
    "Razorfen Geomancer": C("humanoid_caster", 27, 30, "razorfen_geomancer"),
    "Razorfen Totemic": C("humanoid_caster", 28, 31, "razorfen_totemic"),
    "Razorfen Ward-Keeper": C("humanoid_caster", 29, 31, "razorfen_ward_keeper"),
    "Death's Head Acolyte": C("humanoid_caster", 27, 30, "deaths_head_acolyte"),
    "Death's Head Cultist": C("humanoid_caster", 28, 31, "deaths_head_cultist"),
    "Kraul Bristleboar": C("beast_basic", 25, 28, "kraul_bristleboar"),
    "Raging Agam'ar": C("beast_fast", 28, 31, "raging_agamar"),
    "Thornback Sow": C("beast_large", 27, 31, "thornback_sow"),
    "Blind Hunter": C("humanoid_ranged", 29, 29, "blind_hunter", True, 1.7),
    "Earthcaller Halmgar": C("humanoid_caster", 31, 31, "earthcaller_halmgar", True, 1.7),
    "Thornjaw the Gorger": C("beast_large", 31, 31, "thornjaw_the_gorger", True, 1.7),
}
FIXES = {                      # pre-existing bosses: exact ladder levels, multipliers tuned so HP climbs through the dungeon: Roogug < Aggem/Jargba < Agathelos < Ramtusk < Charlga
    "Roogug": {"level_range": [28, 28], "boss_multiplier": 1.35},
    "Aggem Thorncurse": {"level_range": [30, 30], "boss_multiplier": 2.1},
    "Death Speaker Jargba": {"level_range": [30, 30], "boss_multiplier": 2.1},
    "Overlord Ramtusk": {"level_range": [32, 32]},
    "Agathelos the Raging": {"level_range": [32, 32], "boss_multiplier": 1.7},
    "Charlga Razorflank": {"level_range": [34, 34], "boss_multiplier": 3.5},
}
CAVE = {
    "creatures": {
        "Razorfen Spearhide": 3, "Razorfen Defender": 2, "Razorfen Beast Trainer": 2, "Razorfen Handler": 2,
        "Razorfen Geomancer": 2, "Razorfen Totemic": 2, "Razorfen Ward-Keeper": 1, "Death's Head Acolyte": 2,
        "Death's Head Cultist": 2, "Kraul Bristleboar": 3, "Raging Agam'ar": 2, "Thornback Sow": 2,
        # bosses/rares ride in the same table at weight 0 (engine convention; placed only by zone.boss_positions pins)
        "Roogug": 0, "Aggem Thorncurse": 0, "Death Speaker Jargba": 0, "Overlord Ramtusk": 0,
        "Agathelos the Raging": 0, "Charlga Razorflank": 0,
        "Blind Hunter": 0, "Earthcaller Halmgar": 0, "Thornjaw the Gorger": 0},
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Razorfen Geomancer": [qd("kraul_seed_pod", "Kraul Seed-Pod",
                              "A barbed seed-pod the size of a fist. It ticks when you hold it. Oggra wants them gone from the hill.", 0.45)],
    "Razorfen Ward-Keeper": [qd("ward_seal_stone", "Ward Seal-Stone",
                                "A palm-sized stone etched with a binding ward, still warm from the force that held the pit shut.", 0.5)],
}


def pools():
    P = {}
    # ---------------- bosses ----------------------------------------------------------------------------------
    P["Roogug"] = [               # L28 -> 31: 1H axe / leather wrist / plate waist / cloth cloak
        make("Roogug's Vine-Cutter", "main_hand", "of the Gladiator", 31,
             "A hooked axe made for cutting thorn and, when thorn is not available, other things.", weapon_type="axe_1h"),
        make("Thornhide Bracers", "wrist", "of the Falcon", 31,
             "Leather wrapped over a brace of dried thorn. Every pull of the strap draws a little blood.", armor_type="leather"),
        make("Boarhide War-Belt", "waist", "of the Juggernaut", 31,
             "A broad belt of boar-skin and iron studs. It smells, honestly, of boar.", armor_type="plate"),
        make("Bridgewalker's Mantle", "back", "of the Eagle", 31,
             "A cloak of woven vine and wool. It sways, even when you do not.", armor_type="cloth")]
    P["Aggem Thorncurse"] = [     # L30 -> 33: caster shoulders / healer staff / mail boots / healer ring
        make("Thorncursed Mantle", "shoulder", "of the Sorcerer", 33,
             "Spun from briar-fibre and hexed twice. It whispers in a boar's voice, which is unsettling.", armor_type="cloth"),
        make("Aggem's Gnarled Staff", "main_hand", "of the Prophet", 33,
             "A knot of ironwood with a boar's tusk at the head. It remembers the herd.", weapon_type="staff"),
        make("Spiritbound Greaves", "feet", "of the Wolf", 33,
             "Mail boots lined with something warm that is not fur. They keep their footing on any hill.", armor_type="mail"),
        make("Thorncurse Signet", "ring", "of the Restorer", 33,
             "A ring of braided thorn. Wounds nearby close a little faster, and a little reluctantly.")]
    P["Death Speaker Jargba"] = [ # L30 -> 33: cloth head / shadow wand / mail chest / 1H mace
        make("Death Speaker's Cowl", "head", "of the Archmage", 33,
             "A cowl stitched from burial shrouds. The dead are very chatty, if you are the one wearing it.", armor_type="cloth"),
        make("Mind-Bound Wand", "ranged", "of the Sorcerer", 33,
             "A wand wound with a lock of someone's hair. It's best not to ask whose.", weapon_type="wand"),
        make("Death's Head Hauberk", "chest", "of the Tiger", 33,
             "Mail sewn over a quilboar-skull gorget. It settles on the shoulders like a hand.", armor_type="mail"),
        make("Hexbinder's Mace", "main_hand", "of the Champion", 33,
             "A bone-capped mace, carved with the names of those who stopped arguing.", weapon_type="mace_1h")]
    P["Overlord Ramtusk"] = [     # L32 -> 35: plate helm / 2H axe / leather belt / gun
        make("Ramtusk's Tusk-Crown", "head", "of the Defender", 35,
             "A great helm with a pair of real tusks. It rings like a bell when you are struck.", armor_type="plate"),
        make("Overlord's Warcleaver", "main_hand", "of the Gladiator", 35,
             "A two-handed axe made for a boar-lord. It's heavy, and it makes up its own mind about direction.", weapon_type="axe_2h"),
        make("Boarlord's Girdle", "waist", "of the Assassin", 35,
             "A belt of cured hide, scarred where something bit it. The scars are, so far, mostly decorative.", armor_type="leather"),
        make("Pen-Keeper's Longrifle", "ranged", "of the Marksman", 35,
             "A long rifle that Ramtusk's pen-keepers used on escapees. It has opinions about range.", weapon_type="gun")]
    P["Agathelos the Raging"] = [ # L32 -> 35: dagger / leather chest / cloth cloak / mail legs
        make("Agathelos's Rending Fang", "main_hand", "of the Assassin", 35,
             "A fang the length of a forearm, mounted on a bone grip. It tears more than it cuts.", weapon_type="dagger"),
        make("Beastpit Hide Jerkin", "chest", "of the Bear", 35,
             "The cured pelt of something that did not like its keepers. It does not particularly like you, either.",
             armor_type="leather"),
        make("Raging Pelt Cloak", "back", "of the Eagle", 35,
             "A fur cloak, matted with dried blood. It warms you, and it makes you irritable.", armor_type="cloth"),
        make("Chainbound Legguards", "legs", "of the Soldier", 35,
             "Mail legguards with a broken manacle still hanging from one knee. It rings a little, in a way that feels sarcastic.",
             armor_type="mail")]
    P["Charlga Razorflank"] = [   # L34 -> 37: healer staff / cloth head / plate legs / 1H sword
        make("Razorflank's Heartstaff", "main_hand", "of the Physician", 37,
             "A staff of sunbaked thorn with a pulsing heartwood knot. Wounds close faster around it, and quietly.",
             weapon_type="staff"),
        make("Thorn-Crown of Agamaggan", "head", "of the Archmage", 37,
             "A circlet of interlaced thorn, old as the hill. The spirits of the boar-god lean in when you wear it.",
             armor_type="cloth"),
        make("Chieftain's Thornplate Legs", "legs", "of the Bastion", 37,
             "Plate grown through with living briar. It hurts to be hit, and it hurts to hit it.", armor_type="plate"),
        make("Thornfang Longsword", "main_hand", "of the Champion", 37,
             "A long blade with a sawtooth edge, traded for the lives of three of Charlga's guards.", weapon_type="sword_1h")]
    # ---------------- named rares -----------------------------------------------------------------------------
    P["Blind Hunter"] = [         # L29 -> 32: bow / leather gloves / ring
        make("Blind Hunter's Shortbow", "ranged", "of the Marksman", 32,
             "A bow strung with sinew. It was built for someone who had to listen for the target.", weapon_type="bow"),
        make("Listener's Leather Gloves", "hands", "of the Falcon", 32,
             "Soft leather gloves, cut to feel the pull of a string. They are very quiet.", armor_type="leather"),
        make("Hunter's Bone Signet", "ring", "of the Eagle", 32,
             "A ring of carved bone. It doesn't have eyes, but it seems to be looking.")]
    P["Earthcaller Halmgar"] = [   # L31 -> 34: cloth shoulders / healer mace / neck
        make("Earthcaller's Mantle", "shoulder", "of the Prophet", 34,
             "A mantle of woven root. It hums, faintly, with the pitch of a buried stone.", armor_type="cloth"),
        make("Halmgar's Stoneclaw Mace", "main_hand", "of the Restorer", 34,
             "A mace topped with a smooth grey stone. When you swing it, the ground notices.", weapon_type="mace_1h"),
        make("Pendant of the Deep Root", "neck", "of the Whale", 34,
             "A pendant of petrified root. It is heavier than it looks, and much calmer.")]
    P["Thornjaw the Gorger"] = [  # L31 -> 34: leather helm / fist weapon / ring
        make("Thornjaw's Gorge-Cap", "head", "of the Bear", 34,
             "A helm cured from a sow's skull, thorns left in. It makes you feel hungry and a little ridiculous.",
             armor_type="leather"),
        make("Gorger's Claw-Knuckles", "main_hand", "of the Tiger", 34,
             "Claws set in a fist-bar of bone. It bites at the end of a punch.", weapon_type="fist_weapon"),
        make("Wallow-Mud Band", "ring", "of the Soldier", 34,
             "A ring of baked mud and bone. It's gross, and it fits perfectly.")]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    data = json.loads(cp.read_text(encoding="utf-8"))
    cr = data["creatures"]
    cr.update(NEW_CREATURES)
    for n, patch in FIXES.items():
        cr[n].update(patch)
    cp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    ep = ROOT / "data/creatures/encounters.json"
    data = json.loads(ep.read_text(encoding="utf-8"))
    data["zones"]["Southern Barrens"].setdefault("caves", {})["Razorfen Kraul"] = CAVE
    ep.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    qp = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(qp.read_text(encoding="utf-8"))
    D = data["drops"]
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = {"_notes": "Razorfen Kraul boss + named-rare loot (2026-10-21). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/razorfen_kraul_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
