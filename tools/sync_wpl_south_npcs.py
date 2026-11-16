#!/usr/bin/env python3
"""Create and position South Western Plaguelands' people (docs/plaguelands_design.md). Idempotent; follows
tools/npc_data_guard.py (creates who it names, moves people to the layout's spot, deletes nobody).

    PYTHONPATH=. python3 tools/sync_wpl_south_npcs.py

Two hubs, each with an inn and a flight master:

THE BULWARK, the Forsaken's front line on the Tirisfal border. The apothecaries here give the cauldron quests
(Kyle: "Keep the similar cauldron quests"), and they want samples, not ashes.

SORROW HILL, the Order of the Pale Flame's keep beside Uther's Tomb, under Hearthglen's nose. Kyle: "the leader and
top fighters are FROM EARTH ... they recruited defects from The Scarlet Crusade and they're more selective in who
they kill, they don't go after all undead, only mindless ones." The Order talks about Earth freely among itself
(Kyle chose "Loud in the Order, normal elsewhere"). Flamekeeper Rory Callahan joined the Crusade during the
Integration and walked out of it (Kyle: "The leader WAS part of the Scarlet Crusade though! that is Important!").

Every line is plain speech: whole sentences, contractions, the useful thing first.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from tools.handbuilt_wpl_south import NPC_POSITIONS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402

ZONE = "western_plaguelands_south"
M, F = "male", "female"

#: id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Bulwark
    "wpl_bulwark_commander": ("High Executor Marla Venn", "undead", F, 3, "down",
                              "This wall is the last thing between the Plaguelands and Tirisfal. Everything east "
                              "of it wants to come west, and none of it is getting through while I'm standing."),
    "wpl_bulwark_apothecary": ("Apothecary Dorian Vesk", "undead", M, 5, "down",
                               "The Scourge brew their plague in cauldrons out in the fields. I want to know what's "
                               "in them, and I'd much rather you brought me a sample than a story."),
    "wpl_bulwark_innkeeper": ("Innkeeper Sabine Holt", "undead", F, 2, "down",
                              "The beds are hard and the stew is grey, but the door locks, and out here that's "
                              "the part that matters."),
    "wpl_bulwark_bat_handler": ("Bat Handler Tobias Crane", "undead", M, 4, "right",
                                "The bats fly anywhere you've been. They don't like Andorhal, so if you're going "
                                "there, you're walking."),
    "wpl_bulwark_sewer_agent": ("Deathstalker Ilsa Rook", "undead", F, 6, "left",
                                "There's an old way under the city that comes out near here. The Royal "
                                "Apothecaries want it open again, and they want it quietly."),
    # ---- Sorrow Hill (the Order of the Pale Flame)
    "wpl_pf_flamekeeper": ("Flamekeeper Rory Callahan", "human", M, 8, "down",
                           "I wore the red for a year. I was born in Cork and I laid steel in Boston, and when the "
                           "world ended the Crusade were the only ones killing what was killing us. Then I saw what "
                           "else they were killing, so I scraped the red off and walked out. We hunt the mindless "
                           "dead here, and nobody else."),
    "wpl_pf_innkeeper": ("Innkeeper Priya Raman", "human", F, 4, "down",
                         "I ran a guesthouse in Kochi before all this. The guests here are heavier armed and they "
                         "tip worse, but they always say thank you."),
    "wpl_pf_bat_keeper": ("Roostkeeper Anders Holm", "human", M, 3, "right",
                          "We fly hawks, not bats. The Forsaken think that's a statement. It isn't, I just don't "
                          "like bats."),
    "wpl_pf_drillmaster": ("Drillmaster Kofi Mensah", "human", M, 6, "down",
                           "Half my recruits came out of the Crusade and the other half came off the road. The first "
                           "half can fight, and the second half can think, and I'm trying to get both out of everyone."),
    "wpl_pf_chaplain": ("Chaplain Odile Marchand", "human", F, 5, "left",
                        "Uther's Tomb is the one place on this hill that everyone agrees is holy. I keep it that way "
                        "by not letting anyone argue about it."),
}

#: id -> (name, race, gender, variant, facing, greeting, sells, sells_gear)
VENDORS = {
    "wpl_bulwark_quartermaster": ("Quartermaster Ezra Pell", "undead", M, 2, "down",
                                  "Deathguard issue, all of it. The potions taste like the cauldrons smell, and they "
                                  "work, which is more than I can say for the cauldrons.",
                                  ["healing_potion_masterwork", "mana_potion_masterwork", "kit_field_repair",
                                   "whetstone", "flux_strong", "vial_crystal", "drink_waterskin", "roasted_meat"],
                                  True),
    "wpl_pf_quartermaster": ("Quartermaster Hollis Burke", "human", M, 7, "down",
                             "The Order buys plain steel and good bread, and that's what I've got. When you've earned "
                             "it, I've got better than that too.",
                             ["bread_and_cheese", "spiced_stew", "drink_waterskin", "healing_potion_masterwork",
                              "kit_field_repair", "whetstone", "beast_lure"], True),
}

SERVICES = {"wpl_bulwark_innkeeper": ["inn"], "wpl_bulwark_bat_handler": ["flight"],
            "wpl_pf_innkeeper": ["inn"], "wpl_pf_bat_keeper": ["flight"]}
FLIGHT_NODES = [
    ("the_bulwark", {"name": "The Bulwark", "zone": "Western Plaguelands South", "master": "wpl_bulwark_bat_handler",
                     "pos": [46, -8], "continent": "eastern_kingdoms"}),
    ("sorrow_hill", {"name": "Sorrow Hill", "zone": "Western Plaguelands South", "master": "wpl_pf_bat_keeper",
                     "pos": [78, 24], "continent": "eastern_kingdoms"}),
]
GEAR_LEVEL = 53


def main():
    names = set(AMBIENT) | set(VENDORS)
    if names != set(NPC_POSITIONS):
        raise SystemExit(f"roster and layout disagree: {sorted(names ^ set(NPC_POSITIONS))}")
    ap, vp = ROOT / "data/npcs/ambient_npcs.json", ROOT / "data/npcs/vendors.json"
    ad, vd = json.loads(ap.read_text(encoding="utf-8")), json.loads(vp.read_text(encoding="utf-8"))
    by_n = {r["npc_id"]: r for r in ad["npcs"]}
    by_v = {r["vendor_id"]: r for r in vd["vendors"]}
    from entities.consumable_manager import get_consumable_manager
    cm = get_consumable_manager()
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    made = moved = 0
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=ZONE, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in by_n:
            moved += bool(safe_update(by_n[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    for vid, (name, race, gender, var, facing, greet, sells, sg) in VENDORS.items():
        missing = [s for s in sells if not cm.has_consumable(s) and s not in mats]
        if missing:
            raise SystemExit(f"{vid} sells things that don't exist: {missing}")
        x, y = NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=ZONE, x=x, y=y, tile_sprite="npc", sells=sells,
                   buys_from_player=True, faction="neutral", gear_level=GEAR_LEVEL, sells_gear=sg, race=race,
                   appearance_variant=var, gender=gender, greeting=greet, facing=facing)
        if vid in by_v:
            moved += bool(safe_update(by_v[vid], rec))
        else:
            vd["vendors"].append(rec)
            made += 1
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"].setdefault(key, node)
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"South WPL: {made} created, {moved} moved ({len(names)} people); two inns and two flight points")


if __name__ == "__main__":
    main()
