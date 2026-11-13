#!/usr/bin/env python3
"""A quest item you need several of drops three times in four.

    PYTHONPATH=. python3 tools/set_quest_drop_rates.py

Kyle, 12 Nov 2026: "For drop rates of quest items, we should have them around 75% (when
multiple drops are needed). This should save a lot of headache." Playtest, the same day:
Building Something Permanent wants six coral at 50% off a crab that barely spawns.

332 of the 383 quest drops were under 75%, most of them 40-50%, on quests asking for 5 to 12.
Every drop whose item a quest asks for MORE THAN ONE of is raised to FLOOR; anything already
higher is left alone, and single-item drops (a key, a letter, a head) keep their own number.
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOOR = 0.75


def wanted():
    """item_id -> the most any quest asks for."""
    most = {}
    for path in glob.glob(str(ROOT / "data/quests/*.json")):
        data = json.loads(Path(path).read_text())
        quests = data.get("quests", data) if isinstance(data, dict) else data
        quests = quests if isinstance(quests, list) else list(quests.values())
        for q in quests:
            if not isinstance(q, dict):
                continue
            for o in q.get("objectives", []):
                if o.get("type") in ("fetch", "gather", "deliver") and o.get("target"):
                    most[o["target"]] = max(most.get(o["target"], 0), int(o.get("count", 1) or 1))
    return most


def main():
    path = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(path.read_text())
    most = wanted()
    raised = 0
    for _creature, drops in data["drops"].items():
        for d in drops:
            if most.get(d.get("item_id"), 0) > 1 and d.get("chance", 1) < FLOOR:
                d["chance"] = FLOOR
                raised += 1
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"{raised} quest drops raised to {FLOOR:.0%}")


if __name__ == "__main__":
    sys.exit(main())
