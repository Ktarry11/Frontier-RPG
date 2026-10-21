"""Write the hand-chosen Echo Isles NPC / vendor / recruit positions from
tools/handbuilt_echo_isles into data/npcs/*.json.  Idempotent.

    python3 tools/sync_echo_isles_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_echo_isles import NPC_POSITIONS, RECRUITS   # noqa: E402


def _patch(path, list_key, id_key, table):
    data = json.loads(Path(path).read_text())
    n = 0
    for rec in data[list_key]:
        pos = table.get(rec.get(id_key))
        if pos and (rec.get("x"), rec.get("y")) != tuple(pos):
            rec["x"], rec["y"] = pos
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return n


def main():
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id", NPC_POSITIONS)
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id", NPC_POSITIONS)
    total += _patch("data/npcs/recruits.json", "recruits", "recruit_id", RECRUITS)
    print(f"moved {total} records")


if __name__ == "__main__":
    main()
