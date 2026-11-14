"""
Write the hand-chosen Deathknell NPC / vendor positions from tools/handbuilt_deathknell into data/npcs/*.json
and the creature spawn points into data/creatures/spawn_points.json.  Idempotent.

    python3 tools/sync_deathknell_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_deathknell import NPC_POSITIONS, SPAWNS   # noqa: E402


def _patch(path, list_key, id_key):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    n = 0
    for rec in data[list_key]:
        pos = NPC_POSITIONS.get(rec.get(id_key))
        if pos and (rec.get("x"), rec.get("y")) != tuple(pos):
            rec["x"], rec["y"] = pos
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return n


def main():
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id")
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id")
    fp = Path("data/creatures/spawn_points.json")
    data = json.loads(fp.read_text(encoding="utf-8"))
    new = [{"creature": c, "x": x, "y": y} for (c, x, y) in SPAWNS]
    if data.get("Deathknell", {}).get("spawns") != new:
        data["Deathknell"] = {"spawns": new}
        total += 1
    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"moved/added {total} records")


if __name__ == "__main__":
    main()
