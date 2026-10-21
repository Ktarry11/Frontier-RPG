#!/usr/bin/env python3
"""The Broodspiral content pass (2026-10-21).  Idempotent.

  python3 tools/build_broodspiral_content.py && python3 tools/generate_creatures.py

What was broken: the dungeon spawned NOTHING (its table lived under a bogus top-level zone key instead of
zones["Southern Barrens"]["caves"]), all six creatures pointed at kits that did not exist, and the loot used the
invalid slot "weapon" with tiny stat numbers.

Dungeon ladder (Kyle's confirmed table): trash 18-23 | Carapace Warden 19 | Broodkeeper 21 | Larval Broodguard 22 |
Broodspiral Queen 24.  Named rares Mother Amberwing 20 / Gnash 22 / Chitterlord Skrix 23 (pinned in side nurseries).
Trash is HAND-PLACED (tools/handbuilt_broodspiral.TRASH -> zone.trash_spawns), levels ramping with depth.
LOOT: ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    "Hive Drone": C("vermin_swarm", 18, 20, "hive_drone"),
    "Hive Skulker": C("vermin_sneaky", 19, 21, "hive_skulker"),
    "Resin Spitter": C("humanoid_ranged", 20, 22, "resin_spitter"),
    "Brood Tender": C("humanoid_caster", 20, 22, "brood_tender"),
    "Carapace Crusher": C("elemental_bruiser", 21, 23, "carapace_crusher"),
    "Gorged Larva": C("vermin_swarm", 21, 23, "gorged_larva"),
    "Hive Weaver": C("elemental_caster", 21, 23, "hive_weaver"),
    "Amber Sentinel": C("humanoid_warrior", 22, 23, "amber_sentinel"),
    "Mother Amberwing": C("vermin_sneaky", 20, 20, "mother_amberwing", True, 1.7),
    "Gnash the Hollow-Maw": C("beast_large", 22, 22, "gnash_hollow_maw", True, 1.7),
    "Chitterlord Skrix": C("humanoid_caster", 23, 23, "chitterlord_skrix", True, 1.6),
}
FIXES = {
    "Silithid Guardian": {"level_range": [18, 21]},
    "Silithid Stinger": {"level_range": [19, 23]},
}

CAVE = {
    "creatures": {
        "Silithid Guardian": 3, "Silithid Stinger": 3, "Hive Drone": 3, "Hive Skulker": 2, "Resin Spitter": 2,
        "Brood Tender": 2, "Carapace Crusher": 2, "Gorged Larva": 2, "Hive Weaver": 2, "Amber Sentinel": 1,
        "Carapace Warden": 0, "The Broodkeeper": 0, "Larval Broodguard": 0, "Broodspiral Queen": 0,
        "Mother Amberwing": 0, "Gnash the Hollow-Maw": 0, "Chitterlord Skrix": 0},
    # bosses/rares ride in the same table at weight 0 (engine convention: CaveSpawnManager splits them by
    # creatures.json is_boss; weight 0 = never rolled as filler, only placed by zone.boss_positions pins)
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Hive Weaver": [qd("hive_amber_shard", "Hive-Amber Shard",
                       "A shard of hard golden resin with something very small, and very annoyed, preserved inside.", 0.5)],
    "Resin Spitter": [qd("hive_amber_shard", "Hive-Amber Shard",
                         "A shard of hard golden resin with something very small, and very annoyed, preserved inside.", 0.25)],
}


def pools():
    P = {}
    # ---------------- bosses ----------------------------------------------------------------------------------
    P["Carapace Warden"] = [      # L19 -> 22: leather shoulder / cloth wrist / mail belt / 1H axe
        make("Cracked Carapace Mantle", "shoulder", "of the Assassin", 22,
             "Plates of shell the Warden shed, strapped over soft hide. They still ring when struck.", armor_type="leather"),
        make("Warden's Chitin Bands", "wrist", "of the Archmage", 22,
             "Bands of pale chitin sewn onto cloth. They hum faintly, as if the hive were listening.", armor_type="cloth"),
        make("Burrower's Girdle", "waist", "of the Falcon", 22,
             "Links of chitin and old mail, built for something that spends its life underground.", armor_type="mail"),
        make("Carapace-Splitter", "main_hand", "of the Soldier", 22,
             "A short axe with a head ground from the Warden's own claw. It finishes what the claw started.",
             weapon_type="axe_1h")]
    P["The Broodkeeper"] = [      # L21 -> 24: healer chest / leather legs / plate gloves / healer staff
        make("Broodkeeper's Vestments", "chest", "of the Physician", 24,
             "Silk spun by something that was not meant to be spun by. Wounds mend faster under it, and so does the dread.",
             armor_type="cloth"),
        make("Caustic-Woven Leggings", "legs", "of the Tiger", 24,
             "Woven with acid-treated thread. They resist everything, including being washed.", armor_type="leather"),
        make("Chitinguard Gauntlets", "hands", "of the Juggernaut", 24,
             "Heavy chitin gauntlets, still faintly warm from the brood they guarded.", armor_type="plate"),
        make("Keeper's Brood-Crook", "main_hand", "of the Prophet", 24,
             "A shepherd's crook for a flock of larvae. It hums when something nearby is hungry.", weapon_type="staff")]
    P["Larval Broodguard"] = [    # L22 -> 25: healing-power gun / tank helm / healer ring / tank shield
        make("Venomspitter Rifle", "ranged", "of the Physician", 25,
             "A rifle that fires a mist of larval venom. Strangely, it heals the friendlies it misses.", weapon_type="gun"),
        make("Screenwarden's Helm", "head", "of the Defender", 25,
             "A helm of mail and chitin, built to hold the line against things that bite.", armor_type="mail"),
        make("Broodguard's Signet", "ring", "of the Restorer", 25,
             "A ring of larval amber. It warms when you heal and cools when you stop."),
        make("Larval Shell Buckler", "off_hand", "of Blocking", 25,
             "A shield cut from a molted larval shell. It remembers every blow, and returns a few.", weapon_type="shield")]
    P["Broodspiral Queen"] = [    # L24 -> 27: tank chest / caster legs / 1H mace / healer cloak
        make("Queen's Bulwark", "chest", "of the Bastion", 27,
             "Plate grown, not forged, over a queen's own carapace. It is very hard to leave the hive in it.",
             armor_type="plate"),
        make("Hivemind Legguards", "legs", "of the Sorcerer", 27,
             "Layered chitin, linked by something that thinks. It occasionally finishes your sentences.",
             armor_type="mail"),
        make("Queenmother's Mace", "main_hand", "of the Champion", 27,
             "A mace carved from the queen's own mandible. It is heavy, and it is unfriendly.", weapon_type="mace_1h"),
        make("Broodspiral Cloak", "back", "of the Restorer", 27,
             "A cloak of pale silk drawn from the queen's own spinnerets. It soothes you, and it watches.",
             armor_type="cloth")]
    # ---------------- named rares -----------------------------------------------------------------------------
    P["Mother Amberwing"] = [     # L20 -> 23: mail wrist / neck / dagger
        make("Egg-Guard Bracers", "wrist", "of the Wolf", 23,
             "Chitin bracers lined with egg-membrane. They keep a person's pulse low and their guard high.",
             armor_type="mail"),
        make("Amber-Drop Pendant", "neck", "of the Whale", 23,
             "A tear of hard amber on a cord. Something inside is very still, very patient."),
        make("Brood-Mother's Stinger", "main_hand", "of the Assassin", 23,
             "A short stinger set in a bone grip. It's faster than it looks and meaner than it should be.",
             weapon_type="dagger")]
    P["Gnash the Hollow-Maw"] = [  # L22 -> 25: 2H axe / leather chest / ring
        make("Gnash's Hollow-Tusk Cleaver", "main_hand", "of the Gladiator", 25,
             "A broad axe built around a split tusk. It hungers, in the way that tusks do.", weapon_type="axe_2h"),
        make("Maw-Hide Jerkin", "chest", "of the Bear", 25,
             "Tough hide from the pit, rough-cured and rank. It laughs at claws.", armor_type="leather"),
        make("Marrow-Cracker Band", "ring", "of the Soldier", 25,
             "A band of bone-iron, scarred by a hundred knuckle-cracks. It doesn't mind.")]
    P["Chitterlord Skrix"] = [    # L23 -> 26: nature wand / caster shoulders / caster cloak
        make("Skrix's Chitter-Rod", "ranged", "of Nature's Wrath", 26,
             "A slender rod of resin that clicks and chitters when you aim it. Loudly.", weapon_type="wand"),
        make("Swarm-Lord's Mantle", "shoulder", "of the Sorcerer", 26,
             "A mantle of tiny shell-plates. Each one moves a little. Don't look at it for long.",
             armor_type="cloth"),
        make("Veil of a Thousand Legs", "back", "of the Eagle", 26,
             "A cloak of fine chitin-silk. It prickles. It is very, very warm.", armor_type="cloth")]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    data = json.loads(cp.read_text())
    cr = data["creatures"]
    cr.update(NEW_CREATURES)
    for n, patch in FIXES.items():
        cr[n].update(patch)
    cp.write_text(json.dumps(data, indent=2) + "\n")

    ep = ROOT / "data/creatures/encounters.json"
    data = json.loads(ep.read_text())
    z = data["zones"]["Southern Barrens"]
    z.setdefault("caves", {})["The Broodspiral"] = CAVE
    data["zones"].pop("The Broodspiral", None)      # the dead top-level key the old dungeon never read
    ep.write_text(json.dumps(data, indent=2) + "\n")

    qp = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(qp.read_text())
    D = data["drops"]
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    out = {"_notes": "The Broodspiral boss + named-rare loot (rebuilt 2026-10-21; the old pool used the invalid slot 'weapon'). "
                     "ONE item drops per kill from the pool. item_level = creature level + 3; real loot formulas "
                     "(tools/build_durotar_content.make). The gun carries Healing Power on purpose (wide CoA weapon spread)."}
    out.update(pools())
    (ROOT / "data/loot/broodspiral_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
