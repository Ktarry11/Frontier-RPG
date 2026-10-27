"""
Create and position Tarren Mill's NPCs and vendors in data/npcs/*.json.  Idempotent.

    PYTHONPATH=. python3 tools/sync_hillsbrad_npcs.py

Unlike tools/sync_barrens_town_npcs.py, which only MOVES records that already exist, this one also creates them:
Hillsbrad shipped with zero NPCs in either zone and none in any of its towns, so there was nothing to move.

Coordinates are never written here. They come from handbuilt_tarren_mill.NPC_POSITIONS so the layout stays the one
source of truth for where a person stands - the same reason the baker reads the layout's own fields.

WHO STANDS WHERE IS THE ARCHETYPE.  The race divides the town, so it divides the roster: the WEST bank is the
living village and its people are human - the innkeeper, the miller, the smith, the chaplain - still doing the work
the village was built for. The EAST bank is the Royal Apothecary Society's, and every one of them is Forsaken. The
two guards on the bridges are the seam. A player who notices that everyone on one side is dead and everyone on the
other is not has read the town correctly.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import tools.handbuilt_tarren_mill as TM  # noqa: E402

ZONE = "tarren_mill"
GEAR = 16                      # the town band is 23-26; Brill (a 10-12 town) sits at 8

#: vendor_id -> (name, race, gender, variant, [stock], sells_gear, greeting)
VENDORS = {
    "tarren_mill_innkeeper": (
        "Innkeeper Mallory Dunn", "human", "female", 4,
        ["healing_potion_standard", "mana_potion_standard", "bread_and_cheese", "roasted_meat",
         "spiced_stew", "spiced_wine", "guardian_elixir_standard"], False,
        "Room's yours if you want it. I'll not ask which bank you came off."),
    "tarren_mill_trader": (
        "Goodwife Serrin Holt", "human", "female", 11,
        ["healing_potion_minor", "mana_potion_minor", "bread_and_cheese", "parchment", "glue",
         "salt", "thread_coarse", "vial_empty"], False,
        "Flour, thread, lamp oil. Whatever the mill does not eat, I sell."),
    "tarren_mill_smith": (
        "Smith Odrin Vance", "human", "male", 7,
        ["whetstone", "flux_medium", "flux_strong", "coal", "resin"], True,
        "I shoe their horses and mend their cart axles. A trade is a trade."),
    "tarren_mill_bowyer": (
        "Bowyer Tess Aldren", "human", "female", 16,
        ["fletching", "sinew", "component_string", "resin", "glue"], True,
        "Yew from the river stand, strung the way my father strung them."),
    "tarren_mill_reagent_seller": (
        "Factor Vell", "forsaken", "male", 9,
        ["vial_empty", "vial_leaded", "vial_crystal", "dye_mild", "bleach", "parchment"], False,
        "The Society requisitions. I merely keep the ledger, and the ledger keeps everyone honest."),
    "tarren_mill_apothecary": (
        "Apothecary Lysbet Crane", "forsaken", "female", 14,
        ["elixir_of_toughness", "elixir_of_warding", "elixir_of_agility", "arcane_elixir",
         "healing_potion_standard", "mana_potion_standard"], False,
        "Mind the vats. What is in them is not finished, and it does not like being looked at."),
    "tarren_mill_vat_tender": (
        "Vat-Tender Grusk", "forsaken", "male", 18,
        ["battle_elixir_standard", "guardian_elixir_standard", "elixir_of_firepower",
         "mushroom_broth", "tanning_reagent"], False,
        "Stir it, skim it, log it. Twelve years dead and I have a trade again."),
}

#: npc_id -> (name, race, gender, variant, greeting)
AMBIENT = {
    # --- the seam: the two who stand where the banks meet
    "tarren_mill_gate_guard": (
        "Gate Guard Hollis", "forsaken", "male", 8,
        "South gate. State your business, keep to the road, and do not swim the race."),
    "tarren_mill_watchman": (
        "Watchman Grell", "forsaken", "male", 20,
        "Three bridges, three of us. You would be amazed how many try the water anyway."),
    # --- west bank: the village still working
    "tarren_mill_miller": (
        "Miller Aldous Reed", "human", "male", 2,
        "The wheel has turned every day for sixty years. Who holds the town has never once stopped it."),
    "tarren_mill_stablemaster": (
        "Stablemaster Brann Teague", "human", "male", 13,
        "Horses will not cross the bridges at night. Clever animals, horses."),
    "tarren_mill_farrier": (
        "Farrier Nell Marsh", "human", "female", 6,
        "Hooves and hinges. Half this town runs on things I hammered flat."),
    "tarren_mill_chaplain": (
        "Chaplain Ewen Blackwood", "human", "male", 17,
        "I keep the chapel on this side. They have never asked me to stop. I have never asked why."),
    "tarren_mill_sluice_keeper": (
        "Sluice-Keeper Pate", "human", "male", 10,
        "Crank's mine. Drop the gate and the wheel stops, the vats go cold, and everyone remembers my name."),
    "tarren_mill_farmhand": (
        "Farmhand Dorrin", "human", "male", 19,
        "Barley in the north plots, oats in the south. Same as my mother sowed, same rows."),
    # --- east bank: the Society
    "tarren_mill_apprentice": (
        "Apprentice Nilla Stitch", "forsaken", "female", 5,
        "I label everything. If a jar has no label, do not open it, and do not tell me you opened it."),
    "tarren_mill_commander": (
        "Commander Vellis Thorne", "forsaken", "female", 12,
        "Alterac to the north, Southshore to the south, and the Syndicate in between. We hold the middle."),
    "tarren_mill_scout": (
        "Scout Mirren Vask", "forsaken", "male", 15,
        "Durnholde is thick with Syndicate and the hills are thick with gnolls. Walk the road."),
}


def _load(path, key):
    d = json.loads(Path(path).read_text())
    return d, d[key]


def main():
    pos = TM.NPC_POSITIONS
    missing = [k for k in list(VENDORS) + list(AMBIENT) if k not in pos]
    if missing:
        raise SystemExit(f"no NPC_POSITIONS entry for: {missing}")
    spare = [k for k in pos if k not in VENDORS and k not in AMBIENT]
    if spare:
        raise SystemExit(f"NPC_POSITIONS has spots with nobody to stand in them: {spare}")

    made = moved = 0

    vd, vendors = _load("data/npcs/vendors.json", "vendors")
    by_id = {r["vendor_id"]: r for r in vendors}
    for vid, (name, race, gender, var, sells, gear, greet) in VENDORS.items():
        x, y = pos[vid]
        rec = by_id.get(vid)
        if rec is None:
            vendors.append({"vendor_id": vid, "name": name, "zone": ZONE, "x": x, "y": y,
                            "tile_sprite": "npc", "sells": sells, "buys_from_player": True,
                            "faction": "forsaken" if race == "forsaken" else "neutral",
                            "gear_level": GEAR, "sells_gear": gear, "race": race,
                            "gender": gender, "appearance_variant": var, "greeting": greet})
            made += 1
        elif (rec["x"], rec["y"]) != (x, y):
            rec["x"], rec["y"] = x, y
            moved += 1
    Path("data/npcs/vendors.json").write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n")

    ad, npcs = _load("data/npcs/ambient_npcs.json", "npcs")
    by_id = {r["npc_id"]: r for r in npcs}
    for nid, (name, race, gender, var, greet) in AMBIENT.items():
        x, y = pos[nid]
        rec = by_id.get(nid)
        if rec is None:
            npcs.append({"npc_id": nid, "name": name, "zone": ZONE, "x": x, "y": y,
                         "greeting": greet, "gender": gender, "race": race,
                         "appearance_variant": var, "facing": "down"})
            made += 1
        elif (rec["x"], rec["y"]) != (x, y):
            rec["x"], rec["y"] = x, y
            moved += 1
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n")

    print(f"Tarren Mill: {made} records created, {moved} moved "
          f"({len(VENDORS)} vendors, {len(AMBIENT)} ambient)")


if __name__ == "__main__":
    main()
