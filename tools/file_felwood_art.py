#!/usr/bin/env python3
"""File the two Felwood sheets (claude/felwood_art_prompts.md) where the game looks for them. Idempotent.

    PYTHONPATH=. python3 tools/slice_building_sheet.py felwood_creatures tools/building_sheets/felwood_creatures.png
    PYTHONPATH=. python3 tools/slice_building_sheet.py felwood tools/building_sheets/felwood_buildings_props.png
    PYTHONPATH=. python3 tools/file_felwood_art.py

Creatures go flat into assets/creatures/ (get_creature_sprite_by_id reads them by file stem).
Sheet 2 splits: the town, camp and hold buildings and the Deadwood hut into assets/buildings/, the
forest and the Legion's marks into assets/tiles/felwood/props/.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRE_SRC = ROOT / "assets/creatures/_src/felwood"
ART_SRC = ROOT / "assets/tiles/felwood/_src"
BUILDINGS = {
    "fw_moonwell_shrine", "fw_sentinel_hall", "fw_druid_treehouse", "fw_inn", "fw_hippogryph_roost",
    "fw_supply_house", "fw_timbermaw_lodge", "fw_sentinel_tower", "fw_stake_barricade", "fw_sentinel_tent",
    "fw_jaedenar_gatehouse", "fw_taken_hall", "fw_cult_tent", "fw_deadwood_hut",
}


def main():
    n_c = n_b = n_p = 0
    for f in sorted(CRE_SRC.glob("fw_*.png")):
        shutil.copyfile(f, ROOT / "assets/creatures" / f.name)
        n_c += 1
    props = ROOT / "assets/tiles/felwood/props"
    props.mkdir(parents=True, exist_ok=True)
    for f in sorted(ART_SRC.glob("fw_*.png")):
        if f.stem in BUILDINGS:
            shutil.copyfile(f, ROOT / "assets/buildings" / f.name)
            n_b += 1
        else:
            shutil.copyfile(f, props / f.name)
            n_p += 1
    print(f"{n_c} creatures, {n_b} buildings, {n_p} props filed")


if __name__ == "__main__":
    main()
