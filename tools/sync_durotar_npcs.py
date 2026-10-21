"""
Write the hand-chosen Durotar NPC / vendor / forge positions from
tools/handbuilt_durotar.NPC_POSITIONS into data/npcs/*.json.

Idempotent.  Quests reference npc ids only, so moving them is safe.

    python3 tools/sync_durotar_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_durotar import NPC_POSITIONS   # noqa: E402


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
    total = 0
    total += _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id")
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id")
    total += _patch("data/npcs/forges.json", "forges", "forge_id")
    print(f"moved {total} records")


if __name__ == "__main__":
    main()
