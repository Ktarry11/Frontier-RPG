#!/bin/bash
# Rebake every zone whose art uses a texture fixed by tools/fix_water_seams.py.
# Run from the repo root after that tool. Prints one line per script and its exit status.
export PYTHONPATH=.
run() { echo ">>> $*"; timeout 3000 python3 "$@" > /tmp/rebake_one.log 2>&1; rc=$?; grep -a "baked\|wrote\|Error\|Traceback" /tmp/rebake_one.log | tail -4; echo "<<< exit $rc  $*"; }
run tools/bake_arathi_caves.py
run tools/bake_ashenvale.py
run tools/bake_ashenvale.py west
run tools/bake_ashenvale_dungeons.py
run tools/bake_aspen_zone.py
run tools/bake_durotar_caves.py
run tools/bake_echo_caves.py
run tools/bake_glittervein.py
run tools/bake_glittervein_dungeon.py
run tools/bake_hillsbrad.py all
run tools/bake_lashings.py
run tools/bake_return_voyage.py
run tools/bake_silverpine.py all
run tools/bake_southern_needles.py
run tools/bake_stranglethorn.py all
run tools/bake_stranglethorn_caves.py
run tools/bake_tanaris_places.py
run tools/bake_tempest.py all
run tools/bake_undercity.py
run tools/bake_vot_caves.py
run tools/bake_zeppelin_tower.py --skin orc
run tools/bake_zeppelin_tower.py --skin forsaken
echo "ALL DONE"
