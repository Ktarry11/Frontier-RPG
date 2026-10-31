#!/usr/bin/env python3
"""Per-creature verdict on every unreachable creature: is it safe to delete?

    PYTHONPATH=. python3 tools/audit_orphan_creatures.py

qa_creature_reachability answers "which creatures can nobody meet". This answers the only
question that follows from it: for each one, is deleting it free, or does something in the game
still depend on it?

"Unreachable" and "unused" are NOT the same claim, and conflating them is how you delete a
quest. A creature nobody placed can still be named by a quest's drop table, a loot file, a
faction's kill list or a sprite rule, and deleting it then turns a reachable-but-broken thing
into a silently missing one.

VERDICTS, strongest first:

  BLOCKS A QUEST   something a player must obtain drops ONLY from this creature. Deleting it
                   deletes that quest. These are not cleanup, they are bugs that need the
                   creature PLACED, and they are the reason this file exists.
  NAMED AT RUNTIME referenced by data the running game reads (loot, factions, abilities).
                   Deleting it needs that reference removed in the same breath.
  SUPERSEDED       nothing reads it, AND a live creature shares a distinctive word with
                   it (Scarlet Marksman / Scarlet Bowman). The look-alike is a HINT, not
                   proof of replacement - "Magma Seeker" and "Bristleback Water Seeker"
                   share only the word. What makes it safe to delete is that nothing reads
                   it, which is equally true of UNREFERENCED below.
  UNREFERENCED     nothing anywhere names it. Safe to delete.

Authoring scripts under tools/ are reported but never block a verdict: they are how content was
written once, not how it is read now.
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

#: Data the RUNNING GAME reads. A reference here is load-bearing; one under tools/ is not.
RUNTIME_DIRS = ["data/quests", "data/loot", "data/factions", "data/abilities", "data/talents",
                "data/items", "data/dungeons", "data/gathering"]


def main():
    from tools.qa_creature_reachability import placed
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    where, _ = placed()
    orphan = sorted(set(cre) - set(where))
    live = set(cre) & set(where)

    # ---- which quest items does each orphan gate, and are they obtainable elsewhere?
    drops = json.loads((ROOT / "data/creatures/quest_drops.json").read_text(encoding="utf-8"))["drops"]
    item_sources = defaultdict(set)
    for creature, entries in drops.items():
        for d in (entries if isinstance(entries, list) else []):
            if d.get("item_id"):
                item_sources[d["item_id"]].add(creature)

    quest_text = "\n".join((ROOT / p).read_text(encoding="utf-8", errors="ignore")
                           for p in ["data/quests"] for p in
                           [str(f.relative_to(ROOT)) for f in (ROOT / "data/quests").rglob("*.json")])

    # ---- every runtime reference to each orphan, by name
    runtime_refs = defaultdict(set)
    tool_refs = defaultdict(set)
    for base, kind in [(d, "runtime") for d in RUNTIME_DIRS] + [("tools", "tool")]:
        root = ROOT / base
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if f.suffix not in (".json", ".py", ".md") or not f.is_file():
                continue
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # In a .json file ONLY the double-quoted form can be a real reference - a single
            # quote cannot delimit a JSON string, so 'Imp' there is always prose. That exact
            # case produced a false positive: "an imp summoning an Imp" inside a _source
            # comment was reported as the ability system depending on the creature Imp, which
            # would have moved it out of the safe-to-delete pile for no reason. In a .py file
            # both quote styles are real.
            for n in orphan:
                forms = [f'"{n}"'] if f.suffix == ".json" else [f'"{n}"', f"'{n}'"]
                if any(form in txt for form in forms):
                    (runtime_refs if kind == "runtime" else tool_refs)[n].add(
                        str(f.relative_to(ROOT)))

    # ---- a live creature covering the same ground: share a distinctive word
    STOP = {"the", "of", "a", "greater", "elder", "ancient", "savage", "dire", "small"}
    live_words = defaultdict(set)
    for n in live:
        for w in re.findall(r"[A-Za-z']+", n.lower()):
            if w not in STOP and len(w) > 3:
                live_words[w].add(n)

    verdict = {}
    for n in orphan:
        blocking = []
        for d in (drops.get(n) or []):
            item = d.get("item_id")
            if not item:
                continue
            others = [c for c in item_sources[item] if c != n and c in where]
            if not others and item in quest_text:
                blocking.append((item, bool(d.get("starts_quest"))))
        if blocking:
            verdict[n] = ("BLOCKS A QUEST", blocking)
            continue
        if runtime_refs.get(n):
            verdict[n] = ("NAMED AT RUNTIME", sorted(runtime_refs[n]))
            continue
        cover = set()
        for w in re.findall(r"[A-Za-z']+", n.lower()):
            if w not in STOP and len(w) > 3:
                cover |= live_words.get(w, set())
        if cover:
            verdict[n] = ("SUPERSEDED", sorted(cover)[:3])
            continue
        verdict[n] = ("UNREFERENCED", [])

    order = ["BLOCKS A QUEST", "NAMED AT RUNTIME", "SUPERSEDED", "UNREFERENCED"]
    counts = {k: sum(1 for v in verdict.values() if v[0] == k) for k in order}
    print(f"{len(orphan)} unreachable creatures")
    for k in order:
        print(f"  {k:17s} {counts[k]:3d}")

    for k in order:
        names = [n for n in orphan if verdict[n][0] == k]
        if not names:
            continue
        print(f"\n=== {k} ({len(names)}) ===")
        for n in names:
            detail = verdict[n][1]
            extra = f" [also named in {len(tool_refs[n])} authoring script(s)]" if tool_refs.get(n) else ""
            if k == "BLOCKS A QUEST":
                for item, starts in detail:
                    print(f"  {n:30s} sole source of {item!r}"
                          f"{' - and it STARTS the quest' if starts else ''}")
            elif k == "SUPERSEDED":
                print(f"  {n:30s} covered by {', '.join(detail)}{extra}")
            elif k == "NAMED AT RUNTIME":
                print(f"  {n:30s} {', '.join(detail)}{extra}")
            else:
                print(f"  {n:30s}{extra}")

    safe = counts["SUPERSEDED"] + counts["UNREFERENCED"]
    print(f"\n{safe} safe to delete outright. {counts['NAMED AT RUNTIME']} need their reference "
          f"removed too. {counts['BLOCKS A QUEST']} must NOT be deleted - they need placing, "
          f"because a player is already expected to find them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
