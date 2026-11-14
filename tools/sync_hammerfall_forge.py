#!/usr/bin/env python3
"""Hammerfall gets a forge you can smelt and smith at. Idempotent.

    PYTHONPATH=. python3 tools/sync_hammerfall_forge.py

The town has had a weaponsmith and a blacksmithing trainer since it was built, and the war forge
they were written to stand at was never on the map (it was sited in the rock and refused). So
there was a trainer who taught smithing and nowhere in the Arathi Highlands to do any. The building
is back (tools/handbuilt_hammerfall.py) and this adds the forge record at its door.
"""
import json
from pathlib import Path

from tools import handbuilt_hammerfall as HF

FORGE_ID = "hammerfall_forge"


def main():
    p = Path("data/npcs/forges.json")
    doc = json.loads(p.read_text())
    x, y = HF.FORGE
    rec = next((f for f in doc["forges"] if f["forge_id"] == FORGE_ID), None)
    if rec is None:
        doc["forges"].append({"forge_id": FORGE_ID, "name": "Hammerfall War Forge",
                              "zone": "hammerfall", "x": x, "y": y})
        print("forge added")
    else:
        rec["x"], rec["y"] = x, y
        print("forge in place")
    raw = p.read_text()
    p.write_text(json.dumps(doc, indent=2, ensure_ascii="\\u" in raw) + ("\n" if raw.endswith("\n") else ""))


if __name__ == "__main__":
    main()
