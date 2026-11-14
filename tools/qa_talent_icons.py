#!/usr/bin/env python3
"""Every talent in every tree has an icon.

    PYTHONPATH=. python3 tools/qa_talent_icons.py

Kyle, 12 Nov 2026: "give me a list of icons needed for spell crit (as we added them to talent
trees)." Counted that day: 65 of 2,461 talents drew as a blank node - the 28 crit talents added
to the trees, and 37 whose art did not match their id. He generated all 65.

A talent's icon is assets/icons/talents/<talent_id>.png (or an ability icon of the same id, or
whatever its icon_id names). A talent added later with no art fails here instead of shipping
as an empty square.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def main():
    have = {os.path.basename(p)[:-4] for d in ("talents", "abilities")
            for p in glob.glob(f"assets/icons/{d}/*.png")}
    total, missing = 0, []
    for path in sorted(glob.glob("data/talents/*.json")):
        nodes = json.load(open(path, encoding="utf-8"))["nodes"]
        for node in (nodes if isinstance(nodes, list) else nodes.values()):
            total += 1
            if node["talent_id"] not in have and (node.get("icon_id") or "") not in have:
                missing.append(f"{os.path.basename(path)[:-5]}: {node['name']} ({node['talent_id']})")
    if "no_such_talent_icon" in have:
        missing.append("negative control resolved; this check cannot fail")
    print(f"{total} talents, {len(missing)} without an icon")
    for line in missing[:30]:
        print("  -", line)
    if missing:
        return 1
    print("every talent has an icon")
    return 0


if __name__ == "__main__":
    sys.exit(main())
