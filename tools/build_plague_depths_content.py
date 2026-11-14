#!/usr/bin/env python3
"""Plague Depths content pass.  Idempotent.

  PYTHONPATH=. python3 tools/build_plague_depths_content.py     (kits live in tools/monster_kits.py PLAGUE_DEPTHS_KITS;
                                                                   run `cd tools && python3 generate_creatures.py` after kit edits)

Ladder (claude/dungeon_levels_and_loot_plan.md row 28): trash 30-32; bosses Plagueweaver Vex 31 | The Infected Noble 32 |
Plague Keeper Voss 32 | Vile Plague Abomination 33 | Dark Sorcerer Zul'keth 34.  Story: Forsaken alchemists of the Royal
Apothecary Society are breeding a plague to overthrow Sylvanas (Kyle's brief).
LOOT: ONE item per kill from a pool of 4, item_level = creature level + 3, real formulas (build_durotar_content.make).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

REGION, CAVE = "Undercity", "Plague Depths"

CREATURES = {
    # cistern vermin
    "Plagued Rat": C("beast_basic", 30, 31, "pd_plagued_rat"),
    "Rot Worm": C("beast_basic", 30, 31, "pd_rot_worm"),
    "Plagued Hound": C("beast_fast", 30, 31, "pd_plagued_hound"),
    "Plague Spore": C("vermin_swarm", 30, 31, "pd_plague_spore"),
    "Plague Zombie": C("humanoid_warrior", 30, 32, "pd_plague_zombie"),
    # the Court
    "Forsaken Traitor": C("humanoid_warrior", 30, 32, "pd_forsaken_traitor"),
    "Forsaken Witch": C("humanoid_caster", 30, 32, "pd_forsaken_witch"),
    "Infected Retainer": C("humanoid_warrior", 30, 32, "pd_infected_retainer"),
    "Blighted Courtier": C("humanoid_caster", 31, 32, "pd_blighted_courtier"),
    # the Lab
    "Plague Surgeon": C("humanoid_caster", 31, 32, "pd_plague_surgeon"),
    "Blight Cultist": C("humanoid_caster", 31, 32, "pd_blight_cultist"),
    "Failed Experiment": C("elemental_bruiser", 31, 32, "pd_failed_experiment"),
    "Plague Abomination": C("humanoid_warrior", 32, 32, "pd_plague_abomination"),
    # bosses
    "Plagueweaver Vex": C("humanoid_caster", 31, 31, "pd_plagueweaver_vex", True, 2.3),
    "The Infected Noble": C("humanoid_warrior", 32, 32, "pd_infected_noble", True, 2.4),
    "Plague Keeper Voss": C("humanoid_caster", 32, 32, "pd_plague_keeper_voss", True, 2.4),
    "Vile Plague Abomination": C("humanoid_warrior", 33, 33, "pd_vile_plague_abomination", True, 2.6),
    "Dark Sorcerer Zul'keth": C("humanoid_caster", 34, 34, "pd_dark_sorcerer_zulketh", True, 2.8),
}

TABLE = {
    "Plagued Rat": 3, "Rot Worm": 3, "Plagued Hound": 2, "Plague Spore": 2, "Plague Zombie": 3,
    "Forsaken Traitor": 2, "Forsaken Witch": 2, "Infected Retainer": 2, "Blighted Courtier": 2,
    "Plague Surgeon": 2, "Blight Cultist": 2, "Failed Experiment": 2, "Plague Abomination": 2,
    "Plagueweaver Vex": 0, "The Infected Noble": 0, "Plague Keeper Voss": 0, "Vile Plague Abomination": 0,
    "Dark Sorcerer Zul'keth": 0,
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Plague Spore": [qd("pd_sump_vial", "Sump Sludge Vial",
                        "A stoppered vial of the green-grey sludge the Cistern breeds. The glass is warm.", 0.4)],
    "Rot Worm": [qd("pd_sump_vial", "Sump Sludge Vial",
                    "A stoppered vial of the green-grey sludge the Cistern breeds. The glass is warm.", 0.3)],
    "Plague Surgeon": [qd("pd_surgeon_notes", "Surgeon's Case Notes",
                          "Bloodstained pages in a steady hand. The last entries are less steady.", 0.45)],
    "Blighted Courtier": [qd("pd_courtier_ledger", "Courtier's Blighted Ledger",
                             "A court ledger, every name struck through and every sum still correct.", 0.45)],
    "Failed Experiment": [qd("pd_vat_tissue", "Vat-Born Tissue",
                             "A fist of grey tissue that is still working out what it was meant to be.", 0.45)],
    "The Infected Noble": [qd("pd_noble_signet", "Faulkner Signet",
                              "A heavy gold ring set with the crest of a house that no longer exists. The crest is wet.", 1.0)],
    "Plague Keeper Voss": [qd("pd_voss_codex", "Voss's Plague Codex",
                              "A ledger bound in something that used to be skin. Every page is a recipe.", 1.0)],
}


def pools():
    P = {}
    P["Plagueweaver Vex"] = [       # L31 -> 34
        make("Plaguethread Spindle", "main_hand", "of the Assassin", 34,
             "A bone needle as long as a forearm. The Society used it to sew the conspiracy together, and to unpick the loyal.",
             weapon_type="dagger"),
        make("Fevered-Silk Robes", "chest", "of the Sorcerer", 34,
             "Cloth spun from something that should not spin. It clings, and it is warm, and it is not yours.",
             armor_type="cloth"),
        make("Weaver's Mourning Wraps", "wrist", "of the Falcon", 34,
             "Black thread over black leather. Each stitch is a name. She ran out of room.", armor_type="leather"),
        make("Wand of Slow Rot", "ranged", "of Shadow Wrath", 34,
             "A wand of grey wood, speckled where the blight has found it. It does not hurry.", weapon_type="wand")]
    P["The Infected Noble"] = [     # L32 -> 35
        make("Faulkner's Rotting Claymore", "main_hand", "of Strength", 35,
             "A nobleman's two-hander, still gilded at the quillons and green everywhere else.", weapon_type="sword_2h"),
        make("Gilded Gauntlets of the Fallen House", "hands", "of the Bulwark", 35,
             "Plate that remembers a coat of arms. The gilding is peeling, and so is the owner.", armor_type="plate"),
        make("Moth-Eaten Ermine Mantle", "shoulder", "of the Archmage", 35,
             "A court mantle the moths found first. They left the dignity and took the rest.", armor_type="cloth"),
        make("Signet of the Last Heir", "ring", "of the Champion", 35,
             "A ring for a house with one name left. It is not the wearer's.")]
    P["Plague Keeper Voss"] = [     # L32 -> 35
        make("Keeper's Index-Staff", "main_hand", "of the Necromancer", 35,
             "A long staff of bound spines. Each vertebra is a section of the catalogue, and none is out of order.",
             weapon_type="staff"),
        make("Archivist's Hood of Quiet", "head", "of the Restorer", 35,
             "A cowl lined with paper. It muffles every sound but the one you were hoping not to hear.",
             armor_type="cloth"),
        make("Codex-Bound Legwraps", "legs", "of the Hunt", 35,
             "Leather stamped with a library's mark. It was a very thorough library.", armor_type="leather"),
        make("Ledger-Pin Brooch", "neck", "of the Seer", 35,
             "A brass pin for holding a page. The page, when you look, is still there.")]
    P["Vile Plague Abomination"] = [  # L33 -> 36
        make("Stitchwork Girdle", "waist", "of the Bear", 36,
             "Mail sewn into hide sewn into mail. It stopped being clear which was holding which.", armor_type="mail"),
        make("Vatborn Maul", "main_hand", "of the Juggernaut", 36,
             "A two-handed mace of fused bone and iron, still warm from wherever it was grown.", weapon_type="mace_2h"),
        make("Slab-Hide Pauldrons", "shoulder", "of the Defender", 36,
             "Plate riveted to a hide that did not consent. The hide, to be fair, no longer objects.",
             armor_type="plate"),
        make("Gut-Ward Buckler", "off_hand", "of Stamina", 36,
             "A shield of stretched hide on a bone ring. It flinches before the blow lands.", weapon_type="shield")]
    P["Dark Sorcerer Zul'keth"] = [   # L34 -> 37
        make("Crown of the Plague Heart", "head", "of the Plague", 37,
             "A circlet of black iron, grown over with something that pulses in time with the Heart below.",
             armor_type="cloth"),
        make("Zul'keth's Corruption Rod", "main_hand", "of the Prophet", 37,
             "A short mace of dark glass. Strike something with it and the something remembers being healthy, briefly.",
             weapon_type="mace_1h"),
        make("Heartbound Greatcloak", "back", "of the Archmage", 37,
             "A cloak the colour of old bruises. It beats, faintly, at the shoulder.", armor_type="cloth"),
        make("Blightsworn Legplates", "legs", "of the Soldier", 37,
             "Plate of blackened iron, pitted by something patient. It fits the way an apology fits.",
             armor_type="plate")]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))
    qp = ROOT / "data/creatures/quest_drops.json"
    qdata = json.loads(qp.read_text(encoding="utf-8"))

    cdata["creatures"].update(CREATURES)
    if CAVE in edata:                                # legacy top-level table (never read by the spawn code)
        edata.pop(CAVE)
    z = edata["zones"].setdefault(REGION, {"name": REGION})
    z.setdefault("caves", {})[CAVE] = {"name": CAVE, "creatures": TABLE}
    for creature, drops in QUEST_DROPS.items():
        qdata["drops"].setdefault(creature, [])
        keep = [d for d in qdata["drops"][creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        qdata["drops"][creature] = keep + drops

    out = {"_notes": "Plague Depths boss loot (2026-10-23). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/plague_depths_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"Plague Depths: creatures {len(CREATURES)}, pools {len(out) - 1}, items {n}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")
    qp.write_text(json.dumps(qdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
