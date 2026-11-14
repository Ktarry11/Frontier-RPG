#!/usr/bin/env python3
"""Deathknell cave levels (Kyle, 2026-10-22): the zone is 1-6, so Scarlet Crypt comes down to level 8 (boss 8, trash 6-8).
Idempotent (absolute values).  Creatures used only by the crypt, so no per-zone overrides are needed; ability kits scale
with level at spawn.

    python3 tools/relevel_deathknell_caves.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEVELS = {
    "Crypt Crawler": [6, 7],
    "Scarlet Initiate": [7, 8],
    "Scarlet Chaplain": [7, 8],
    "Restless Crypt Fiend": [7, 8],
    "High Inquisitor Fairbanks": [8, 8],
}


def main():
    p = ROOT / "data/creatures/creatures.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for n, r in LEVELS.items():
        d["creatures"][n]["level_range"] = list(r)
    p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    print("Scarlet Crypt ->", LEVELS)


if __name__ == "__main__":
    main()
