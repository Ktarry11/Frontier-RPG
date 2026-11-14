#!/usr/bin/env python3
"""Every class spelling that reaches the icon loader must resolve to a file.

    PYTHONPATH=. python3 tools/qa_class_icons.py

Kyle, 2026-10-31: "yeah, check the CoA icons"

The icons were never missing. The LOOKUP was: recruits store a display name
("Sun Cleric") and the files are named after the id ("sun_cleric.png"), so the
four two-word classes silently resolved to nothing. One-word classes matched by
accident, which is why it took this long to notice.

This checks both spellings of every class that exists, so a new class or a new
recruit cannot reintroduce the gap quietly. The negative control at the bottom
matters: a check that passes on a deliberately bogus class is not checking.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.class_portrait import _ICON_DIR, _icon_key  # noqa: E402

# Not selectable classes - the shared pool and Asher's hand-authored kit.
NOT_A_CLASS = {"_universal", "asher_unique"}


def main():
    files = {os.path.basename(p)[:-4] for p in glob.glob(f"{_ICON_DIR}/*.png")}
    problems = []

    # 1. every class with an ability file
    ids = {os.path.basename(p)[:-5] for p in glob.glob("data/abilities/*.json")} - NOT_A_CLASS
    for cid in sorted(ids):
        if _icon_key(cid) not in files:
            problems.append(f"class id {cid!r} -> no {_icon_key(cid)}.png")
        # the display spelling of the same class must resolve too
        display = cid.replace("_", " ").title()
        if _icon_key(display) not in files:
            problems.append(f"display name {display!r} -> no {_icon_key(display)}.png")

    # 2. every spelling actually stored on a recruit
    d = json.load(open("data/npcs/recruits.json", encoding="utf-8"))
    block = d.get("recruits", d)
    recs = block if isinstance(block, list) else list(block.values())
    for r in recs:
        cc = r.get("char_class")
        if not cc:
            problems.append(f"{r.get('recruit_id')} has no char_class")
        elif _icon_key(cc) not in files:
            problems.append(f"{r.get('recruit_id')}: {cc!r} -> no {_icon_key(cc)}.png")

    # 3. negative control - the check must be able to fail
    if _icon_key("Hearthsteel Invoker") in files:
        problems.append("negative control resolved; this check cannot fail")

    for p in sorted(set(problems)):
        print(f"  !! {p}")
    print(f"\n{len(files)} icons, {len(ids)} classes, {len(recs)} recruits")
    if problems:
        print(f"{len(set(problems))} unresolved")
        return 1
    print("every class spelling resolves to an icon")
    return 0


if __name__ == "__main__":
    sys.exit(main())
