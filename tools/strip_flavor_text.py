#!/usr/bin/env python3
"""Strip flavour text from everything that has not earned it.

    PYTHONPATH=. python3 tools/strip_flavor_text.py [--check]

Kyle, 5 Nov 2026: "remove flavor text from most things. Having 1% items
having flavor text is fine. Having 100% Having lackluster flavor text isn't."

He is describing an inflation problem rather than a quality one. 98% of the
4,603 hand-authored items carry a line - 100% of uncommons - so the text has
stopped meaning anything. A flavour line should say "this one is special",
and when nearly every item has one it says nothing at all, however well each
individual line is written.

THE RULE: epic and legendary keep theirs, everything else loses it.

That is 36 items, 0.78% of the set, which is as near to Kyle's "1% is fine"
as the data allows without hand-picking favourites. Rarity is also the right
axis: it is the game's own existing statement about which items are meant to
be remarkable, so the flavour text now agrees with the colour of the name
instead of contradicting it.

Nothing is invented and nothing is rewritten - lines are removed, and the
epics keep theirs exactly as authored. The generated-loot path already
passes flavor_text="" (entities/loot_generator.py), so procedural drops were
never part of the problem.

Idempotent, and reversible from git if Kyle wants a different cut.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Rarities allowed to keep a flavour line.
KEEP = {"epic", "legendary"}


def _strip(item, stats):
    """Drop flavor_text unless the item's rarity earns it. True if changed."""
    text = (item.get("flavor_text") or "").strip()
    if not text:
        return False
    rarity = item.get("rarity")
    if rarity in KEEP:
        stats["kept"] += 1
        return False
    # Removed outright rather than set to "": a key holding an empty string
    # reads to the next author as "this item's line is missing", which is an
    # invitation to write one and undo this.
    item.pop("flavor_text", None)
    stats["stripped"] += 1
    stats["by_rarity"][rarity] = stats["by_rarity"].get(rarity, 0) + 1
    return True


def main():
    check = "--check" in sys.argv
    stats = {"kept": 0, "stripped": 0, "by_rarity": {}}
    written = 0

    for path in sorted((ROOT / "data/quests").glob("*.json")):
        doc = json.loads(path.read_text())
        dirty = False
        for quest in doc.get("quests", []):
            for item in (quest.get("unique_item_defs") or []) + (quest.get("rewards") or []):
                if isinstance(item, dict):
                    dirty |= _strip(item, stats)
        if dirty and not check:
            path.write_text(json.dumps(doc, indent=2) + "\n")
            written += 1

    for path in sorted((ROOT / "data/loot").glob("*.json")):
        doc = json.loads(path.read_text())
        rows = doc.get("bosses", doc)
        if not isinstance(rows, dict):
            continue
        dirty = False
        for owner, items in rows.items():
            if owner.startswith("_") or not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict):
                    dirty |= _strip(item, stats)
        if dirty and not check:
            path.write_text(json.dumps(doc, indent=2) + "\n")
            written += 1

    print(f"flavour text stripped: {stats['stripped']}")
    print(f"flavour text kept    : {stats['kept']}  ({sorted(KEEP)})")
    for rarity, n in sorted(stats["by_rarity"].items(), key=lambda kv: -kv[1]):
        print(f"   {rarity:<10} {n}")
    print(f"files written        : {written}{'  (--check: none)' if check else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
