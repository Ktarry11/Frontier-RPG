#!/usr/bin/env python3
"""Every ability must cost a resource its class can actually hold.

    PYTHONPATH=. python3 tools/qa_ability_resources.py

WHY THIS EXISTS. An ability declares resource_type and a cost. The engine
pays it through Character.get_resource / spend_resource, which resolves a
name either to a dedicated attribute pair (_RESOURCE_ATTRS: rage, energy,
mana, health) or to the dict-backed secondary_resources pool. A dict-backed
pool STARTS AT ZERO, so an ability costing one is uncastable until something
fills it - and if nothing in the game fills it, it is uncastable forever.

Found 5 Nov 2026 while starting the Bloodmage rebuild.
bloodmage_vampiric_fang costs 30 Vitality. Vitality is dict-backed, starts
at 0, and NOTHING in the game grants it: no ability, no talent proc, no
level-up. One ability in 1,274 permanently uncastable, and the same cause
puts a Vitality bar on every Bloodmage's combat screen that is pinned at
0/100 forever, because the UI draws whatever
get_class_secondary_resource() returns.

Nothing complained because every piece is individually valid - the ability
is well-formed, the resource name is spelled correctly, the class really
does declare that secondary. What was missing is anything checking that the
resource has a SOURCE.

THIS CHECK IS DELIBERATELY NARROW. It does not try to judge whether a
resource is generated FAST enough, or whether a rotation works. It asks one
question: for every resource some ability spends, is there any way to get
it? A resource backed by a real attribute (health, mana, rage, energy)
always passes, because those are filled at level-up and by regeneration. A
dict-backed one has to be granted by something.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    from entities.character import Character

    #: Resources backed by a real attribute pair, so they are always filled
    #: by level-up and regeneration rather than needing a grant.
    backed = set(Character._RESOURCE_ATTRS)

    # Who spends what.
    spenders = defaultdict(list)
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        doc = json.loads(path.read_text())
        block = doc.get("abilities", doc)
        rows = (list(block.values()) if isinstance(block, dict)
                else block if isinstance(block, list) else [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            res = row.get("resource_type")
            costs = [r.get("cost") for r in (row.get("ranks") or [])
                     if isinstance(r, dict)]
            if res and any(c for c in costs):
                spenders[res].append(row.get("ability_id"))

    # Who grants what: a talent proc's grant_resource, or an ability whose
    # whole job is restoring one (restore_resource / a scale_talent_key).
    granted = set()
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        text = path.read_text()
        for res in re.findall(r'"resource"\s*:\s*"([a-z_]+)"', text):
            granted.add(res)
        for res in re.findall(r'"gain_(\w+?)"', text):
            granted.add(res)
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        doc = json.loads(path.read_text())
        block = doc.get("abilities", doc)
        rows = (list(block.values()) if isinstance(block, dict)
                else block if isinstance(block, list) else [])
        for row in rows:
            if not isinstance(row, dict):
                continue
            if row.get("effect_type") == "restore_resource":
                # A restore ability names its target either explicitly or by
                # its own resource_type.
                granted.add(row.get("restores") or row.get("resource_type"))
            for res in re.findall(r'"resource"\s*:\s*"([a-z_]+)"',
                                  json.dumps(row)):
                granted.add(res)

    problems = []
    for res, abilities in sorted(spenders.items()):
        if res in backed or res in granted:
            continue
        problems.append((res, abilities))

    print(f"  {len(spenders):5d} resources are spent by at least one ability")
    print(f"  {len(backed):5d} of them are backed by a real attribute "
          f"({', '.join(sorted(backed))})")
    print(f"  {len(problems):5d} are spent but NEVER GRANTED by anything")
    for res, abilities in problems:
        print(f"      {res!r}: nothing in the game produces it, so these "
              f"{len(abilities)} abilities can never be cast")
        for aid in abilities:
            print(f"          {aid}")

    ok = not problems
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
