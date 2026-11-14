#!/usr/bin/env python3
"""The town enchanters, who teach Enchanting. Idempotent.

    PYTHONPATH=. python3 tools/build_enchanters.py
    PYTHONPATH=. python3 tools/vendor_trades.py        # then stock the shops

Kyle, 14 Nov 2026, on who teaches Enchanting: "The town enchanters."

THREE WERE ALREADY STANDING IN TOWN, with nothing to do: Voren Glimmerhand in Orgrimmar, Enchantress
Maeve Dunmoor in the Undercity and Enchanter Vaelios in Kael's Bastion. They now train it
(data/training/trainers.json, written by tools/build_enchanting.py). They stay where they are.

TWO MORE TOWNS GET ONE, so there's somewhere to learn the upper ranks further along: Steamwheedle
Port and Onyxhollow. These two keep a shop as well, selling runed rods, vials and formulas
(tools/vendor_trades.py stocks anyone titled Enchanter). They're added to their town's roster and
NPC spots too, so the town's sync tool keeps them.

Rods are also sold by reagent shops (the copper one) and made by blacksmiths.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_gem_sellers import _roster_add, _position_add  # noqa: E402

VENDORS = ROOT / "data/npcs/vendors.json"
AMBIENT = ROOT / "data/npcs/ambient_npcs.json"

NOTE = "enchanter (tools/build_enchanters.py, 14 Nov 2026)"

#: the three already in town: their ambient records learn the trade
STANDING = ["org_enchanter", "uc_enchanter", "kb_enchanter"]

NEW = {
    "stw_enchanter": dict(
        name="Enchanter Zizzle Sparkwick", zone="steamwheedle_port", race="goblin", gender="male",
        variant=7, xy=(73, 45), faction="neutral", gear_level=44, roster="steamwheedle",
        sells=["runed_copper_rod", "runed_silver_rod", "runed_golden_rod", "vial_leaded"],
        greeting=("I teach enchanting, and I sell the rods for it. The good rods cost a fortune, "
                  "and that's because the bars cost a fortune. Get a blacksmith to make you one if "
                  "you know a blacksmith.\n\nBring me your green gear before you sell it. You'll "
                  "get more out of it as dust.")),
    "oh_enchanter": dict(
        name="Enchanter Halvard Runeglow", zone="onyxhollow", race="dwarf", gender="male",
        variant=5, xy=(23, 68), faction="neutral", gear_level=52, roster="onyxhollow",
        figure_from="oh_shrine_keeper",
        sells=["runed_copper_rod", "runed_silver_rod", "runed_golden_rod", "runed_truesilver_rod",
               "vial_crystal"],
        greeting=("Garrun's people make the rods and I put the runes in them. Then I sell them back "
                  "at a price that annoys him.\n\nIf you want to learn enchanting, I'll teach you. "
                  "It starts with breaking good gear into dust, and nobody enjoys that part.")),
}


def main():
    vd = json.loads(VENDORS.read_text(encoding="utf-8"))
    ad = json.loads(AMBIENT.read_text(encoding="utf-8"))
    vendors, ambient = vd["vendors"], ad["npcs"]
    for a in ambient:
        if a["npc_id"] in STANDING:
            a["trains_profession"] = ["enchanting"]
    for vid, s in NEW.items():
        vendors[:] = [v for v in vendors if v["vendor_id"] != vid]
        vendors.append({
            "vendor_id": vid, "name": s["name"], "zone": s["zone"], "x": s["xy"][0], "y": s["xy"][1],
            "tile_sprite": "npc", "sells": list(s["sells"]), "buys_from_player": True,
            "faction": s["faction"], "gear_level": s["gear_level"], "sells_gear": False,
            "race": s["race"], "gender": s["gender"], "appearance_variant": s["variant"],
            "greeting": s["greeting"], "trains_profession": ["enchanting"]})
        if s["roster"] == "steamwheedle":
            _roster_add(ROOT / "tools/steamwheedle_npc_roster.py", "STEAMWHEEDLE_VENDORS", vid, s, s["sells"], NOTE)
            _position_add(ROOT / "tools/handbuilt_steamwheedle_port.py", vid, s["xy"], NOTE)
        else:
            _roster_add(ROOT / "tools/onyxhollow_npc_roster.py", "ONYXHOLLOW_VENDORS", vid, s, s["sells"], NOTE)
            _position_add(ROOT / "tools/handbuilt_onyxhollow.py", vid, s["xy"], NOTE)
        if s.get("figure_from"):
            src = ROOT / "assets/npcs/leaders" / s["figure_from"]
            dst = ROOT / "assets/npcs/leaders" / vid
            if src.exists() and not dst.exists():
                shutil.copytree(src, dst)
        print(f"{s['name']} ({s['zone']})")
    VENDORS.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    AMBIENT.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
