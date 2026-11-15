#!/usr/bin/env python3
"""No bag holds more than 20, and tailoring makes a short ladder of them, not one per cloth.

    PYTHONPATH=. python3 tools/cap_bags.py

Kyle, 15 Nov 2026: "fix up the tailoring bags. They're way too strong and easy to make.....like 28 spot
bags? No thanks. Have tailor bags capped out at 20 slots for now..not ever cloth needs a bag."

The catalog ran 4 to 28 slots and tailoring made 17 of its 21 bags, one for nearly every cloth, five of them
over 20. Every bag is capped at 20 here, shop bags included, because a 24-slot bag on a Booty Bay shelf
would beat the tailor's best the day it was bought. The ladder is re-spaced so the slots still climb with
price, and tailoring keeps eight bags, one every 30-40 skill:

    linen 6, wool 8, silk 10, mageweave 12, runecloth 14, shadowsilk 16, bloodsilk 18 then 20

The other nine recipes are gone (their bags stay in the world, from shops and loot). Prices follow the slots.
A bag already in a save keeps the size it was made with. Idempotent.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = 20

#: bag id -> slots
SLOTS = {
    "small_burlap_sack": 4, "green_dyed_sack": 4, "worn_leather_satchel": 6, "buckled_saddlebag": 6,
    "clasped_traveling_bag": 6, "rose_clasped_bag": 8, "sage_clasped_bag": 8, "violet_clasped_bag": 10,
    "locked_drawstring_pack": 10, "frostward_pack": 12, "runeforged_strongbox": 12, "flameward_coffer": 14,
    "verdant_reagent_case": 14, "tideworn_bosun_chest": 16, "ironbound_prospector_case": 16,
    "duskwoven_carryall": 16, "brass_fitted_haversack": 16, "warden_reliquary": 18, "stormglass_strongbox": 18,
    "deepdelve_bearer": 18, "sunsteel_quartermaster_trunk": 20,
}
#: slots -> (vendor price, sell price) in copper
PRICE = {4: (500, 100), 6: (1000, 250), 8: (2500, 600), 10: (5000, 1250), 12: (10000, 2500),
         14: (40000, 10000), 16: (150000, 37500), 18: (340000, 85000), 20: (600000, 150000)}

#: the recipes tailoring keeps
KEEP = {"tail_linen_bag", "tail_wool_bag", "tail_silk_bag", "tail_mageweave_bag", "tail_runecloth_bag",
        "tail_shadowsilk_case", "tail_bloodsilk_bearer", "tail_bloodsilk_trunk"}


def main():
    bp = ROOT / "data/items/bags.json"
    bd = json.loads(bp.read_text(encoding="utf-8"))
    for b in bd["bags"]:
        n = SLOTS.get(b["item_id"], min(b["bag_capacity"], CAP))
        b["bag_capacity"] = n
        b["vendor_price"], b["sell_price"] = PRICE[n]
    assert max(b["bag_capacity"] for b in bd["bags"]) <= CAP
    bd["_notes"] = (bd.get("_notes") or []) if isinstance(bd.get("_notes"), list) else [bd.get("_notes")]
    note = "Capped at 20 slots (tools/cap_bags.py, Kyle 15 Nov 2026: \"28 spot bags? No thanks\")."
    if note not in bd["_notes"]:
        bd["_notes"].append(note)
    bp.write_text(json.dumps(bd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rp = ROOT / "data/crafting/recipes.json"
    rd = json.loads(rp.read_text(encoding="utf-8"))
    tail = rd["professions"]["tailoring"]["recipes"]
    gone = [rid for rid, r in tail.items() if (r.get("output") or {}).get("kind") == "bag" and rid not in KEEP]
    for rid in gone:
        del tail[rid]
    rp.write_text(json.dumps(rd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    vp = ROOT / "data/npcs/vendors.json"
    vd = json.loads(vp.read_text(encoding="utf-8"))
    for v in vd["vendors"]:
        if v.get("sells"):
            v["sells"] = [s for s in v["sells"] if s not in gone]
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    kept = sorted(((r["skill_required"], r["name"]) for rid, r in tail.items() if rid in KEEP))
    print(f"bags capped at {CAP}; {len(gone)} tailoring bag recipes removed; tailoring makes: {kept}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
