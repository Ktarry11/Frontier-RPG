#!/usr/bin/env python3
"""A secondary_cost must point at a pool its class actually has.

    PYTHONPATH=. python3 tools/qa_secondary_costs.py [--report]

WHAT secondary_cost IS. A flat amount of the CASTER'S secondary resource
spent alongside an ability's ordinary cost, so one ability can pay in two
currencies at once. Added 5 Nov 2026 for the Rogue's combo points: a real
finisher costs Energy AND consumes the points you built, and the single
cost field could express only one of those.

The ability says HOW MUCH; the caster's class says WHICH POOL, via
CLASS_RESOURCE_MAP. That split is what makes the field reusable - any
future builder/spender class gets it for free - and it is also the failure
mode this guards.

THE FAILURE IT CATCHES. An ability carrying a secondary_cost whose class
has no secondary resource is a silent no-op. Ability._has_secondary_resource
deliberately treats a missing pool as FREE rather than uncastable, because
recruits and monsters borrow abilities across classes and bricking a
borrowed finisher would be worse than letting it through. That is the right
runtime behaviour and the wrong thing to ship: the tooltip says it spends
something, the player spends nothing, and no test fails. So the mismatch is
reported statically, here, instead.

It also flags a finisher that costs MORE than the pool can ever hold, which
is simply uncastable, and a cost that is not a whole number of the class's
point size.

WHY 20 IS THE UNIT. Every resource pool in this engine is 0-100. Templar,
the first COMBO class, grants 20 per builder and charges 20/40/60/80, so
the familiar 1-5 combo points read as 20-100. The Rogue follows that rather
than inventing a second scale.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from combat.abilities import (CLASS_RESOURCE_MAP,  # noqa: E402
                              _lookup_class_resource)

#: One "point" on the universal 0-100 pool. See the module docstring.
POINT = 20

#: The engine gives every resource pool this ceiling.
POOL_MAX = 100


def class_of(path):
    """Display-name of the class whose ability file this is."""
    data = json.loads(path.read_text())
    name = data.get("class")
    return name if isinstance(name, str) else None


def main():
    report = "--report" in sys.argv
    no_pool, too_big, off_grid, rows = [], [], [], []
    checked = 0

    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        cls = class_of(path)
        if cls is None:
            continue
        _, secondary = _lookup_class_resource(cls)
        data = json.loads(path.read_text())
        for a in data.get("abilities", []):
            cost = a.get("secondary_cost") or 0
            gen = a.get("generates") or {}
            if not cost and not gen:
                continue
            checked += 1
            rows.append((cls, a["ability_id"], cost, gen.get("resource"),
                         gen.get("amount"), secondary))
            if not cost:
                continue
            if secondary is None:
                no_pool.append((cls, a["ability_id"], cost))
                continue
            if cost > POOL_MAX:
                too_big.append((cls, a["ability_id"], cost))
            if cost % POINT:
                off_grid.append((cls, a["ability_id"], cost))

    with_pool = sum(1 for c in CLASS_RESOURCE_MAP
                    if _lookup_class_resource(c)[1])
    print(f"  {checked} abilities with a secondary_cost or a generates block")
    print(f"  classes with a secondary pool: {with_pool} of "
          f"{len(CLASS_RESOURCE_MAP)}")

    if report:
        print("\n  class        ability                        sec_cost  "
              "generates            pool")
        for cls, aid, cost, res, amt, sec in rows:
            g = f"{res}+{amt}" if res else "-"
            secname = getattr(sec, "value", sec) or "NONE"
            print(f"  {cls:12s} {aid:30s} {cost:>8}  {g:<20} {secname}")

    problems = len(no_pool) + len(too_big) + len(off_grid)
    if not problems:
        print("\n  0 SECONDARY COSTS POINT AT A MISSING POOL\n\nPASS")
        return 0

    if no_pool:
        print(f"\n  {len(no_pool)} ABILITIES SPEND A POOL THEIR CLASS "
              f"DOES NOT HAVE")
        print("  Silent no-op: the tooltip charges, the caster pays "
              "nothing, nothing fails.\n")
        for cls, aid, cost in no_pool:
            print(f"    {aid:34s} costs {cost:>3} but {cls} has no "
                  f"secondary resource")
        print("\n  Fix: give the class a secondary in CLASS_RESOURCE_MAP, "
              "or drop the cost.")

    if too_big:
        print(f"\n  {len(too_big)} COSTS EXCEED THE {POOL_MAX}-POINT POOL "
              f"- never castable")
        for cls, aid, cost in too_big:
            print(f"    {aid:34s} costs {cost}")

    if off_grid:
        print(f"\n  {len(off_grid)} COSTS ARE NOT A WHOLE MULTIPLE OF "
              f"{POINT}")
        print(f"  Builders grant {POINT}, so an off-grid cost can strand "
              f"the player just short.\n")
        for cls, aid, cost in off_grid:
            print(f"    {aid:34s} costs {cost}")

    print("\nFAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
