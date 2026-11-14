"""Make every stored item's stats whole numbers and fold bonus armour into its armour value.

Kyle, 10 Nov: "i asked you to remove these partial values from gear....still havent." and
"when an item gets +armor ... it should just go into the armor."

Item.__init__ enforces both on anything built at runtime (entities.item.whole_stats). This
applies the same function to the DATA, so the files say what the game shows, and a check can
hold them to it. Safe to re-run: a file that is already whole is not rewritten.

    python3 tools/whole_number_gear.py          # rewrite
    python3 tools/whole_number_gear.py --check  # list what would change, exit 1 if anything
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.item import whole_stats  # noqa: E402

#: Item-shaped dicts live under these. gear_suffixes.json is deliberately not here: its
#: numbers are budget WEIGHTS (0.35 of the budget into agility), not stats.
DIRS = ("data/loot", "data/quests", "data/professions", "data/vendors", "data/crafting",
        "data/recruits", "data/starting_gear")
EXTRA = ("data/items/spec_gear.json",)


def fix(node, changed):
    if isinstance(node, dict):
        pri, sec = node.get("primary_stats"), node.get("secondary_stats")
        if isinstance(pri, dict) or isinstance(sec, dict):
            had_armor = "armor_value" in node
            p, s, a = whole_stats(pri if isinstance(pri, dict) else {},
                                  sec if isinstance(sec, dict) else {},
                                  node.get("armor_value", 0) or 0)
            before = (pri, sec, node.get("armor_value"))
            if isinstance(pri, dict):
                node["primary_stats"] = p
            if isinstance(sec, dict):
                node["secondary_stats"] = s
            if had_armor or a:
                node["armor_value"] = a
            if (node.get("primary_stats"), node.get("secondary_stats"), node.get("armor_value")) != before:
                changed.append(node.get("item_id") or node.get("name") or "?")
        for v in node.values():
            fix(v, changed)
    elif isinstance(node, list):
        for v in node:
            fix(v, changed)


def files():
    out = []
    for d in DIRS:
        out.extend(sorted((ROOT / d).rglob("*.json")) if (ROOT / d).exists() else [])
    out.extend(ROOT / e for e in EXTRA if (ROOT / e).exists())
    return out


def main():
    check = "--check" in sys.argv
    total = 0
    for path in files():
        raw = path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        changed = []
        fix(data, changed)
        if not changed:
            continue
        total += len(changed)
        print(f"{path.relative_to(ROOT)}: {len(changed)} item(s)" + (f"  e.g. {changed[0]}" if check else ""))
        if not check:
            # Written back in the file's OWN formatting, so the diff is the numbers and nothing
            # else. The formatting is found by trying each on the untouched data.
            original = json.loads(raw)
            style = next(((i, asc) for i in (2, 4, 1, None) for asc in (True, False)
                          if json.dumps(original, indent=i, ensure_ascii=asc) == raw.rstrip("\n")),
                         (2, True))
            path.write_text(json.dumps(data, indent=style[0], ensure_ascii=style[1])
                            + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    print(f"{total} item(s) {'would change' if check else 'rewritten'}")
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main())
