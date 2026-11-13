#!/usr/bin/env python3
"""Cut the Dark Iron dwarves sheet and file each figure where the game looks for it.

    python3 tools/slice_dark_iron_dwarves.py

Kyle, 13 Nov 2026, of the layer under the Dry Deep and its town: "We have all the art." The
buildings were one sheet (di_*); this is the other - thirty dwarves. Sixteen of them are the people
of Onyxhollow, filed as assets/npcs/leaders/<npc_id>/down.png, which is the per-NPC override the map
already honours (ui/tilemap_renderer.py). Four are the Castouts of The Black Strand, filed as
creature sprites so they stop drawing as human bandits and cultists.

The mapping is the only thing in this file. Who each person IS lives in tools/onyxhollow_npc_roster.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
from slice_building_sheet import slice_sheet  # noqa: E402

SHEET = ROOT / "assets/creatures/_src/tempest_dark_iron_dwarves_sheet_30.png"
STAGE = ROOT / "assets/creatures/_src/dark_iron_dwarves"

#: Onyxhollow npc_id -> figure on the sheet
NPCS = {
    "oh_innkeeper": "did_cooper",
    "oh_quartermaster": "did_engineer",
    "oh_smith": "did_smith",
    "oh_armorer": "did_runesmith",
    "oh_mining_supplier": "did_miner",
    "oh_reagents": "did_alchemist",
    "oh_powder": "did_sapper",
    "oh_thane": "did_thane",
    "oh_forgemaster": "did_gilded_engineer",
    "oh_gate_captain": "did_captain",
    "oh_gate_guard_w": "did_guard_axe",
    "oh_gate_guard_e": "did_guard_spear",
    "oh_wall_sentry": "did_crossbow",
    "oh_vault_keeper": "did_elder",
    "oh_shrine_keeper": "did_censer",
    "oh_stoker": "did_stoker",
    "oh_loremaster": "did_scholar",
    "oh_geomancer": "did_geomancer",
    # two of the three people outside the gate, in The Black Strand
    "bs_lookout": "did_cleaver",
    "bs_castout": "did_ragged",
}

#: creature sprite id -> figure
CREATURES = {
    "dark_iron_digger": "did_chained",
    "dark_iron_cutthroat": "did_iron_mask",
    "dark_iron_slagcaller": "did_ash_cultist",
    "dark_iron_warlord": "did_warlord",
}


def main():
    slice_sheet("dark_iron_dwarves", SHEET, out_dir=STAGE)
    for npc_id, fig in NPCS.items():
        d = ROOT / "assets/npcs/leaders" / npc_id
        d.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(STAGE / f"{fig}.png", d / "down.png")
    for sprite, fig in CREATURES.items():
        shutil.copyfile(STAGE / f"{fig}.png", ROOT / "assets/creatures" / f"{sprite}.png")
    print(f"{len(NPCS)} Dark Iron people and {len(CREATURES)} creature sprites filed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
