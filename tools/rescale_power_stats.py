#!/usr/bin/env python3
"""ONE-SHOT: lift every authored spell power and healing number in data/ onto the new item scale.

    PYTHONPATH=. python3 tools/rescale_power_stats.py

Kyle, 14 Nov 2026: "1 int = 1.5 sp =2 Healing" (see entities/power_scale.py). The costs changed in
data/items/gear_suffixes.json, so anything rolled from now on comes out on the new scale by itself.
This lifts what was already written: item stats everywhere (boss loot, quest rewards, sets, crafted
items), cut gems, enchants, set bonuses and elixirs. It leaves alone the suffix weights (shares, not
amounts), the cost table, and every ability, talent and creature stat_mods: those are class tuning and
are lifted at runtime where they fold into a character (entities/character.py).

Run once. data/items/power_scale.json records that it ran, and a second run does nothing.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from entities.power_scale import LIFT, lift, CURRENT  # noqa: E402

MARK = ROOT / "data/items/power_scale.json"
#: keys whose dict holds real amounts on an item, in any file
ITEM_KEYS = {"secondary_stats", "primary_stats", "socket_bonus"}
#: keys that hold real amounts only in these files
FILE_KEYS = {
    "data/jewelcrafting/gems.json": {"stats"},
    "data/enchanting/enchants.json": {"stats"},
    "data/items/gear_sets.json": {"stats"},
    "data/consumables/consumable_types.json": {"stat_bonuses"},
}


def walk(o, keys, n):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in keys and isinstance(v, dict):
                for s in list(v):
                    if s in LIFT:
                        new = lift(s, v[s])
                        if new != v[s]:
                            v[s] = new
                            n[0] += 1
            else:
                walk(v, keys, n)
    elif isinstance(o, list):
        for x in o:
            walk(x, keys, n)


def main():
    if MARK.exists() and json.loads(MARK.read_text(encoding="utf-8")).get("applied", 1) >= CURRENT:
        print("already applied")
        return 0
    total = 0
    for root, _dirs, files in os.walk(ROOT / "data"):
        if "saves" in Path(root).parts:
            continue
        for fn in files:
            if not fn.endswith(".json"):
                continue
            p = Path(root) / fn
            rel = p.relative_to(ROOT).as_posix()
            raw = p.read_text(encoding="utf-8")
            if not any(s in raw for s in LIFT):
                continue
            d = json.loads(raw)
            n = [0]
            walk(d, ITEM_KEYS | FILE_KEYS.get(rel, set()), n)
            if n[0]:
                indent = 2 if raw.startswith("{\n  ") or raw.startswith("[\n  ") else (1 if raw.startswith("{\n ") else None)
                p.write_text(json.dumps(d, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"  {rel}: {n[0]}")
                total += n[0]
    MARK.write_text(json.dumps({
        "_comment": "tools/rescale_power_stats.py lifted every authored spell power and healing number "
                    "onto the 15 Nov 2026 item scale (entities/power_scale.py). Don't run it again.",
        "applied": CURRENT}, indent=2) + "\n", encoding="utf-8")
    print(f"{total} numbers lifted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
