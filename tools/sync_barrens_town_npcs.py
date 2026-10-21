"""
Write the hand-chosen NPC / vendor / recruit positions (and town forges) from the Crossroads, Camp
Taurajo and Ratchet layout modules into data/npcs/*.json.  Idempotent.

    python3 tools/sync_barrens_town_npcs.py
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

MODULES = ["tools.handbuilt_crossroads", "tools.handbuilt_camp_taurajo", "tools.handbuilt_ratchet"]
FORGES = {"tools.handbuilt_crossroads": ("crossroads_forge", "Crossroads Forge", "crossroads"),
          "tools.handbuilt_ratchet": ("ratchet_forge", "Ratchet Forge", "ratchet")}


def _patch(path, list_key, id_key, positions):
    data = json.loads(Path(path).read_text())
    n = 0
    for rec in data[list_key]:
        pos = positions.get(rec.get(id_key))
        if pos and (rec.get("x"), rec.get("y")) != tuple(pos):
            rec["x"], rec["y"] = pos
            if "home_x" in rec and rec.get("home_town") == rec.get("zone"):
                rec["home_x"], rec["home_y"] = pos
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return n


def main():
    npcs, recruits = {}, {}
    forges = []
    for name in MODULES:
        M = importlib.import_module(name)
        npcs.update(M.NPC_POSITIONS)
        recruits.update(getattr(M, "RECRUITS", {}))
        if name in FORGES and hasattr(M, "FORGE"):
            forges.append((FORGES[name], M.FORGE))
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id", npcs)
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id", npcs)
    total += _patch("data/npcs/recruits.json", "recruits", "recruit_id", recruits)
    fp = Path("data/npcs/forges.json")
    data = json.loads(fp.read_text())
    for (fid, fname, zone), (x, y) in forges:
        rec = next((f for f in data["forges"] if f["forge_id"] == fid), None)
        if rec is None:
            data["forges"].append({"forge_id": fid, "name": fname, "zone": zone, "x": x, "y": y})
            total += 1
        elif (rec["x"], rec["y"]) != (x, y):
            rec["x"], rec["y"] = x, y
            total += 1
    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"moved/added {total} records")


if __name__ == "__main__":
    main()
