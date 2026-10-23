"""
Write the hand-chosen NPC / vendor positions from the Tirisfal modules (Western, Eastern, Brill) into data/npcs/*.json and the
fixed creature spawn points (SPAWNS) into data/creatures/spawn_points.json.  Idempotent.

    python3 tools/sync_tirisfal_npcs.py
"""
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

MODULES = {"Western Tirisfal": "tools.handbuilt_western_tirisfal", "Eastern Tirisfal": "tools.handbuilt_eastern_tirisfal",
           "Brill": "tools.handbuilt_brill"}


def _patch(path, list_key, id_key, pos):
    data = json.loads(Path(path).read_text())
    n = 0
    for rec in data[list_key]:
        p = pos.get(rec.get(id_key))
        if p and (rec.get("x"), rec.get("y")) != tuple(p):
            rec["x"], rec["y"] = p
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return n


def main():
    pos = {}
    for zone, mod in MODULES.items():
        M = importlib.import_module(mod)
        pos.update(M.NPC_POSITIONS)
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id", pos)
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id", pos)
    # Brill's forge is an interaction tile (data/npcs/forges.json), kept clear via the NPC_POSITIONS key "brill_forge"
    ff = Path("data/npcs/forges.json")
    fd = json.loads(ff.read_text())
    bx, by = pos["brill_forge"]
    rec = next((f for f in fd["forges"] if f["forge_id"] == "brill_forge"), None)
    if rec is None:
        fd["forges"].append({"forge_id": "brill_forge", "name": "Brill Forge", "zone": "brill", "x": bx, "y": by})
        total += 1
    elif (rec["x"], rec["y"]) != (bx, by):
        rec["x"], rec["y"] = bx, by
        total += 1
    ff.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n")
    fp = Path("data/creatures/spawn_points.json")
    data = json.loads(fp.read_text())
    for zone, mod in MODULES.items():
        M = importlib.import_module(mod)
        sp = getattr(M, "SPAWNS", None)
        if sp is not None:
            new = [{"creature": c, "x": x, "y": y} for (c, x, y) in sp]
            if data.get(zone, {}).get("spawns") != new:
                data[zone] = {"spawns": new}
                total += 1
    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"moved/added {total} records")


if __name__ == "__main__":
    main()
