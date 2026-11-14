"""
Write the hand-chosen Orgrimmar NPC / vendor / recruit positions (and the city
forge) from tools/handbuilt_orgrimmar into data/npcs/*.json.  Idempotent.

    python3 tools/sync_orgrimmar_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_orgrimmar import NPC_POSITIONS, RECRUITS, FORGE   # noqa: E402


def _patch(path, list_key, id_key, table):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    n = 0
    for rec in data[list_key]:
        pos = table.get(rec.get(id_key))
        if pos and (rec.get("x"), rec.get("y")) != tuple(pos):
            rec["x"], rec["y"] = pos
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return n


def main():
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id", NPC_POSITIONS)
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id", NPC_POSITIONS)
    total += _patch("data/npcs/recruits.json", "recruits", "recruit_id", RECRUITS)
    fp = Path("data/npcs/forges.json")
    data = json.loads(fp.read_text(encoding="utf-8"))
    rec = next((f for f in data["forges"] if f["forge_id"] == "orgrimmar_forge"), None)
    if rec is None:
        data["forges"].append({"forge_id": "orgrimmar_forge", "name": "Orgrimmar Forge",
                               "zone": "orgrimmar", "x": FORGE[0], "y": FORGE[1]})
        total += 1
    elif (rec["x"], rec["y"]) != tuple(FORGE):
        rec["x"], rec["y"] = FORGE
        total += 1
    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"moved/added {total} records")


if __name__ == "__main__":
    main()
