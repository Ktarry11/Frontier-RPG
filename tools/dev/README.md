# Dev helpers (not shipped, not imported by the game)

Run from the repo root.

- `qa_push.sh`: the full QA gate (`tools/qa_quest_overhaul.py`). Pushes to `origin/main` only if it passes.
- `mapshot.py "Zone Name=out.png" ...`: renders a zone's world map to a PNG.
- `castshot.py`, `invshot.py`, `diffshot.py`, `talkshot.py`: render the cast screen, the backpack, the Difficulty window and the interactive-party windows to PNGs.
- `cmp_dps.py a.json b.json`: compares two damage-sim result files (keys are `spec|level`).
- `gd_drive.py [seed]`: drives a party of four pilot recruits through 30 outings and prints every group scene, argument and talk.
- `residents.py`, `clump.py`: townsfolk population and clumping checks used while populating towns.
