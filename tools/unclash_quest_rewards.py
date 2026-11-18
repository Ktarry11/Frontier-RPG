"""
Give every quest reward that drew an epic's icon another one (Kyle, 16 Nov 2026: "every unique item in the game can
only have ONE icon"). Idempotent; touches only the icon_id of non-epic reward items in data/quests/*.json.

    PYTHONPATH=. python3 tools/unclash_quest_rewards.py [--check]

Why it exists: the quest builders author rewards through build_crafted_gear's colour picker, which knows nothing about
the named epics, so a reward can land on an epic's icon. Some builders call tools/reward_icons.unclash themselves;
this sweeps the quest files that were built before they did (Azshara, Deadwind, an old Razor Hill reward), without
re-running their builders.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from tools.reward_icons import unclash, epic_icons  # noqa: E402


def _items(o):
    if isinstance(o, dict):
        if isinstance(o.get("icon_id"), str) and o.get("name") and o.get("slot"):
            yield o
        for v in o.values():
            yield from _items(v)
    elif isinstance(o, list):
        for v in o:
            yield from _items(v)


def main():
    check = "--check" in sys.argv
    epics = epic_icons()
    total = 0
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        hits = [it for it in _items(data) if it.get("rarity") not in ("epic", "legendary") and it["icon_id"] in epics]
        if not hits:
            continue
        total += len(hits)
        if check:
            print(f"{path.name}: {[h['name'] for h in hits]}")
            continue
        changed = [h["name"] for h in hits if unclash(h)]
        indent = 2 if raw.lstrip("{").startswith("\n  ") else None
        path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if raw.endswith("\n") else ""),
                        encoding="utf-8")
        print(f"{path.name}: new icons for {changed}")
    print(f"{total} quest rewards on an epic's icon" + (" (check only)" if check else ", fixed"))
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main())
