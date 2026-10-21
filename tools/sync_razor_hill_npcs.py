"""
Write the hand-chosen Razor Hill NPC / vendor positions (and the town forge)
from tools/handbuilt_razor_hill into data/npcs/*.json.  Idempotent.

    python3 tools/sync_razor_hill_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_razor_hill import NPC_POSITIONS, FORGE   # noqa: E402


def _patch(path, list_key, id_key):
    data = json.loads(Path(path).read_text())
    n = 0
    for rec in data[list_key]:
        pos = NPC_POSITIONS.get(rec.get(id_key))
        if pos and (rec.get("x"), rec.get("y")) != tuple(pos):
            rec["x"], rec["y"] = pos
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return n


def main():
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id")
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id")
    fp = Path("data/npcs/forges.json")
    data = json.loads(fp.read_text())
    rec = next((f for f in data["forges"] if f["forge_id"] == "razor_hill_forge"), None)
    if rec is None:
        data["forges"].append({"forge_id": "razor_hill_forge", "name": "Razor Hill Forge",
                               "zone": "razor_hill", "x": FORGE[0], "y": FORGE[1]})
        total += 1
    elif (rec["x"], rec["y"]) != tuple(FORGE):
        rec["x"], rec["y"] = FORGE
        total += 1
    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"moved/added {total} records")


if __name__ == "__main__":
    main()
