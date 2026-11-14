#!/usr/bin/env python3
"""Dump everything needed to redesign one class's talent trees.

    python3 tools/dump_class.py druid

Prints the class's real abilities (id, cooldown, school, resource cost) and
every talent node in its trees with its current effects, so a redesign works
from what the engine actually has rather than from guessed ability_ids. An
ability_<id>_<suffix> talent key naming an id that isn't in the first list
is a dead talent - that mistake is the single most common one in this data,
so the list is the point.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAGGY = re.compile(r"(_proc|^unlock_|_unlock$|^ability_)", re.I)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cls = sys.argv[1].lower()

    ab_path = ROOT / f"data/abilities/{cls}.json"
    if ab_path.exists():
        doc = json.loads(ab_path.read_text(encoding="utf-8"))
        abilities = doc if isinstance(doc, list) else doc.get("abilities", [])
        print(f"=== {cls.upper()} ABILITIES ({len(abilities)}) ===")
        for a in abilities:
            bits = [f"cd={a.get('cooldown', 0)}", f"cost={a.get('cost', 0)}"]
            if a.get("school"):
                bits.append(a["school"])
            if a.get("duration"):
                bits.append(f"dur={a['duration']}")
            print(f"  {a.get('ability_id', '?'):42} {a.get('name', '?'):26} {' '.join(bits)}")
    else:
        print(f"!! no data/abilities/{cls}.json")

    for p in sorted(glob.glob(str(ROOT / f"data/talents/{cls}_*.json"))):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        nodes = d["nodes"]
        flat = sum(1 for n in nodes
                   if (n.get("effects") and not n.get("proc")
                       and not any(FLAGGY.search(k) for k in n["effects"])))
        print(f"\n=== {os.path.basename(p)}  ({len(nodes)} nodes, {flat} flat) ===")
        for n in sorted(nodes, key=lambda n: (n["tier"], n["talent_id"])):
            tag = "PROC" if n.get("proc") else "    "
            eff = json.dumps(n.get("effects") or {}, separators=(",", ":"))
            print(f"  t{n['tier']} {tag} {n['talent_id']:46} {n['name']:28} "
                  f"{n['max_points']}pt {eff}")
            if n.get("proc"):
                print(f"           proc={json.dumps(n['proc'], separators=(',', ':'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
