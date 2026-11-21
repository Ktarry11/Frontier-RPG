#!/usr/bin/env python3
"""The Aetherians' quartermaster shelf, supply and tabard, now that Aurelion is built. Idempotent.

    PYTHONPATH=. python3 tools/build_aetherians_faction.py
    PYTHONPATH=. python3 tools/build_aetherians_shelf.py

docs/worldtree_brief.md, "The factions": the scholar houses' shelf is the TBC shelf like the others' (Friendly supplies,
Honored recipes, Revered ilvl 67 blues, Exalted ilvl 73 epics and the mount), with a direction and never a cage:
arcane, crystal and engineering, cloth and plate leaning, and the shelf still serves tanks, healers, casters and
fighters. Built on Moonglade's shelf code (tools/build_moonglade.shelves and write_factions), the same way
tools/build_highbough_tribes.py is. Reputation comes from the Crown's, Lenswatch's, the Expanse's, the Anchorfields' and
Aurelion's quests by giver; the quest builders write the faction's `also` list, and write_factions keeps it.

The quartermaster is Quartermaster Bertil Arn on the Council Ring (au_quartermaster, tools/build_aurelion.py).

THE MOUNT is the Lumen Stag (sheet H14, assets/mounts/aetherian_lumen_stag_*), listed with the other Exalted mounts in
tools/build_collection.py.
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_moonglade as BM  # noqa: E402
import build_feathermoon_sentinels as SEN  # noqa: E402

FID = "aetherians"
QM = {FID: "au_quartermaster"}
HONORED = {FID: [("aet_lensbearers_pendant", "Lens-Bearer's Pendant", "neck", "armor", None, "caster", 34,
                  "A disc of survey glass in a gold setting. The House of the Patient Lens gives one to everyone who "
                  "walks down the tree and comes back.")]}
REVERED = {FID: [
    ("aet_starweave_magister_robe", "Starweave Magister's Robe", "chest", "armor", "cloth", "caster", 58,
     "Academy silk with thread of crystal through it, cut the way the magisters have cut it for eight centuries."),
    ("aet_ringwardens_crested_helm", "Ringwarden's Crested Helm", "head", "armor", "plate", "tank", 56,
     "White plate with a gold crest, worn by the wardens who walked the rings before the Ascendancy took the walls."),
    ("aet_spireguard_gauntlets", "Spireguard's Gilded Gauntlets", "hands", "armor", "plate", "plate_healer", 52,
     "The Keepers of the Spire wear these to tend the city's first stone, and they've never once dropped anything."),
    ("aet_conservatory_leggings", "Conservatory Leggings", "legs", "armor", "cloth", "spirit_healer", 54,
     "Woven in the Gardens from silver-grove bark fibre. They smell faintly of gold apples for years."),
    ("aet_skiffrunners_mantle", "Skiffrunner's Mantle", "shoulder", "armor", "leather", "agility", 50,
     "Oiled hide over a crystal frame, for the skiff crews who stand at the rail in a crosswind."),
    ("aet_signet_of_the_high_houses", "Signet of the High Houses", "ring", "armor", None, "strength_crit", 48,
     "A ring cut from one crystal with every house's mark inside it, so the light shows all of them at once."),
]}
EXALTED = {FID: [
    ("aet_staff_of_the_patient_lens", "Staff of the Patient Lens", "main_hand", "weapon", "staff", "caster", 300,
     "A white staff crowned with the survey's finest lens. Look through it and the World Tree is close enough to "
     "touch."),
    ("aet_spirewardens_maul", "Spirewarden's Maul", "main_hand", "weapon", "mace_2h", "strength", 320,
     "A gold-bound maul of Spire stone. The keepers say the head was quarried from the same rock the palace stands on."),
    ("aet_aegis_of_the_rings", "Aegis of the Rings", "off_hand", "weapon", "shield", "tank", 280,
     "A round shield of white crystal with the city's rings cut into its face, warm in the hand and very hard to break."),
]}
EXALTED_RECIPES = {FID: [
    ("rep_aet_ringwarden_legplates", "blacksmithing", "Ringwarden's Legplates", "legs", "armor", "plate", "tank",
     "The wardens' own pattern: white plate inlaid with gold, heavy enough to stand on a ring's edge in a gale.",
     "gear_wow_legs_plate_03_1"),
    ("rep_aet_starweave_vestments", "tailoring", "Starweave Vestments", "chest", "armor", "cloth", "caster",
     "Woven at the Academy from silk and crystal thread. They hold a little light after dark.",
     "gear_inv_chest_cloth_14"),
]}
SHELF_PATTERNS = {FID: [
    ("rep_aet_crystalweave_cuffs", "tailoring", "Crystalweave Cuffs", "wrist", "armor", "cloth", "healer",
     "The first thing an Aurelion weaver learns: cuffs with a thread of crystal that keeps the hands steady.",
     "gear_inv_chest_cloth_06", "honored"),
    ("rep_aet_gilded_sabatons", "blacksmithing", "Gilded Sabatons", "feet", "armor", "plate", "strength",
     "Made at the sky-forge for the dockhands who walk the rim in plate. The gold is on the inside.",
     "gear_inv_boots_plate_09", "revered"),
]}
CONSUMABLES = {FID: ("elixirs", {
    "consumable_id": "aet_lenslight_draught", "name": "Lenslight Draught", "consumable_type": "elixir",
    "description": ("Water off a wellstone with a mote of anchorlight dissolved in it, the way the Academy's students "
                    "brew it for long nights. +20 Intellect for 30 minutes. Battle elixir: one at a time."),
    "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": 50,
    "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 90, "buff_category": "battle",
    "stat_bonuses": {"intellect": 20},
})}
HONORED_SUPPLIES = {FID: ["flask_mending"]}
#: every unique item has ONE icon (Kyle, 16 Nov 2026)
EPIC_ICONS = {"aet_spirewardens_maul": "gear_inv_hammer_18"}   # its first pick was an epic's (Threshing Day)
COLOURS = ((235, 235, 245), (205, 160, 50))      # white and gold: the houses' colours, for the tabard


def faction_base():
    fd = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))
    rec = copy.deepcopy(fd["factions"][FID])
    rec.pop("rewards", None)
    rec["leader"]["npc_id"] = "au_first_speaker"
    rec["leader"]["location"] = "The Council Hall of the High Houses, on Aurelion's Council Ring"
    rec["_lore_note"] = rec["_lore_note"].replace(" The leader has no npc_id until Aurelion is built.", "")
    return rec


def real_ingredients():
    for name in ("EXALTED_RECIPES", "SHELF_PATTERNS"):
        setattr(SEN, name, {SEN.FID: globals()[name][FID]})
    return SEN.real_ingredients()


def tabard_colours():
    p = ROOT / "tools/build_tabards.py"
    s = p.read_text(encoding="utf-8")
    if f'"{FID}"' in s:
        return
    a = '    "highbough_tribes": ((30, 120, 120), (200, 70, 40)),\n'
    assert a in s
    p.write_text(s.replace(a, a + f'    "{FID}": {COLOURS!r},\n'), encoding="utf-8")


def main():
    BM.FACTIONS = {FID: faction_base()}
    for name in ("QM", "HONORED", "REVERED", "EXALTED", "EXALTED_RECIPES", "SHELF_PATTERNS", "CONSUMABLES",
                 "HONORED_SUPPLIES"):
        setattr(BM, name, copy.deepcopy(globals()[name]))
    BM.EPIC_ICONS = dict(EPIC_ICONS)
    BM.OLD_NAMES = []
    bad = []
    cd, fr, picks, docs = BM.shelves(bad)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    fd = BM.load("data/factions/factions.json")
    BM.write_factions(fd)
    fd["factions"][FID]["rewards"]["_comment"] = [
        "Gates, not a displayed ladder (the faction panel stays information only).",
        "TBC-style shelf (tools/build_aetherians_shelf.py, 21 Nov 2026): friendly the Academy's Lenslight Draught, "
        "honored a neck piece and a pattern, revered six ilvl 67 blues and a pattern, exalted three ilvl 73 epics and "
        "two recipes, and the Lumen Stag at Exalted."]
    BM.save("data/factions/factions.json", fd)
    BM.save("data/items/faction_rewards.json", fr)
    BM.save("data/items/crafted_icons.json", picks)
    BM.save("data/consumables/consumable_types.json", cd)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    swapped = real_ingredients()
    tabard_colours()
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/build_tabards.py"), "--write"], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"The Aetherians: 7 blues, 3 epics, 2 recipes, 2 patterns, a supply and a tabard; "
          f"{swapped} patterns on their real ingredients")
    return 0


if __name__ == "__main__":
    sys.exit(main())
