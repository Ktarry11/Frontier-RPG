#!/usr/bin/env python3
"""Merge per-zone staged quest-drop rows into data/creatures/quest_drops.json. Idempotent.

    PYTHONPATH=. python3 tools/merge_staged_quest_drops.py [--check]

WHY STAGING EXISTS. quest_drops.json is one shared file that every quest pass has to append to,
because a `fetch` or `gather` objective whose item nothing drops is a quest nobody can hand in. When
three content passes run at once, three read-modify-write cycles against one JSON file means the last
writer wins and the other two zones' rows are gone - silently, with every quest still loading fine
and only the hand-in failing. That nearly happened: one pass ran `git checkout --` on this file
mid-run to undo its own stray write, which would have taken the other two passes' uncommitted rows
with it had they not already been committed.

So a pass writes tools/staging_drops_<zone>.json in this file's exact shape and never touches the
live file. This merges them, once, under supervision.

WHAT IT REFUSES TO DO. A merge that overwrites is the same silent-loss bug wearing a different hat,
so:
  - A row for the same item on the same creature that DIFFERS from the live row aborts, rather than
    replacing it.
  - An identical row already present is a no-op, which is what makes re-running safe.
  - A second creature dropping an item that already has a source is allowed and REPORTED. The first
    version of this script treated that as fatal, which was wrong twice over: several quests
    deliberately take one item off two creatures so a player is not funnelled into a single pull,
    and the check only fired when the first source was already live, so identical pairs inside one
    staging batch sailed through while the same pattern across two batches aborted. An inconsistent
    guard is worse than none, because it trains you to pass a flag to silence it.
  - A row whose creature does not exist in creatures.json aborts. The drop would never fire.
  - A row no quest asks for aborts. Dead drop data is how this project accumulated 589 unreachable
    reward items; it is not getting a second front.

--check reports what would change and exits non-zero if anything is pending, so CI or a later pass
can tell whether the live file is current.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIVE = ROOT / "data/creatures/quest_drops.json"
CREATURES = ROOT / "data/creatures/creatures.json"


def staged():
    out = {}
    for path in sorted(ROOT.glob("tools/staging_drops_*.json")):
        data = json.loads(path.read_text())
        out[path.name] = data.get("drops", {})
    return out


def wanted_items():
    """Every item_id some quest's fetch/gather objective actually asks for."""
    want = set()
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        for quest in json.loads(path.read_text()).get("quests", []):
            for obj in quest.get("objectives", []):
                if obj.get("type") in ("fetch", "gather") and obj.get("target"):
                    want.add(obj["target"])
            # starter-item quests name their item in the giver field
            giver = str(quest.get("giver_npc_id", ""))
            if giver.startswith("item:"):
                want.add(giver[5:])
    return want


def creature_names():
    data = json.loads(CREATURES.read_text())
    rows = data.get("creatures", data)
    if isinstance(rows, dict):
        return {r.get("name") for r in rows.values()} | set(rows)
    return {r.get("name") for r in rows}


def main():
    check = "--check" in sys.argv

    live_doc = json.loads(LIVE.read_text())
    live = live_doc["drops"]
    stage = staged()
    if not stage:
        print("no staging files found")
        return 0

    known = creature_names()
    want = wanted_items()

    # item_id -> creature, as the live file stands
    owner = {row["item_id"]: cname for cname, rows in live.items() for row in rows}

    adds, noops, problems, second_sources = [], 0, [], []
    for fname, drops in stage.items():
        for cname, rows in drops.items():
            if cname not in known:
                problems.append(f"{fname}: creature {cname!r} is not in creatures.json")
                continue
            for row in rows:
                iid = row.get("item_id")
                if not iid:
                    problems.append(f"{fname}: a row under {cname!r} has no item_id")
                    continue
                if iid not in want:
                    problems.append(
                        f"{fname}: {iid!r} is not asked for by any quest objective or item-starter"
                    )
                    continue
                existing = [r for r in live.get(cname, []) if r.get("item_id") == iid]
                if existing:
                    if existing[0] == row:
                        noops += 1
                    else:
                        problems.append(
                            f"{fname}: {iid!r} on {cname!r} differs from the live row - "
                            f"refusing to overwrite"
                        )
                    continue
                if iid in owner and owner[iid] != cname:
                    second_sources.append((iid, owner[iid], cname))
                adds.append((fname, cname, row))

    print(f"staging files: {len(stage)}   rows to add: {len(adds)}   already present: {noops}")
    for fname, cname, row in adds:
        print(f"  + {row['item_id']:34} on {cname:28} ({fname})")

    if second_sources:
        print(f"\n{len(second_sources)} item(s) gaining a second source (allowed, listed so it is "
              f"a decision and not an accident):")
        for iid, first, also in second_sources:
            print(f"  {iid:34} {first}  +  {also}")

    if problems:
        print(f"\n{len(problems)} problem(s), nothing written:")
        for p in problems:
            print(f"  {p}")
        return 2

    if check:
        if adds:
            print("\npending: run without --check to merge")
            return 1
        print("\nlive file is current")
        return 0

    if not adds:
        print("\nnothing to do")
        return 0

    for _fname, cname, row in adds:
        live.setdefault(cname, []).append(row)
    LIVE.write_text(json.dumps(live_doc, indent=2) + "\n")
    print(f"\nmerged {len(adds)} row(s); quest_drops.json now covers {len(live)} creatures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
