#!/usr/bin/env python3
"""Gate the Rogue abilities that are real WotLK talents.

    PYTHONPATH=. python3 tools/gate_rogue_talent_abilities.py [--dry-run]

THE SAME HALF-FINISHED CHANGE FOUND ON THE DRUID FORMS. Three Rogue
abilities had an unlock_ability node sitting in a talent tree while the
ability itself was NOT requires_talent:

    rogue_blade_flurry      rogue_combat / blade_flurry
    rogue_killing_spree     rogue_combat / killing_spree
    rogue_preparation       rogue_subtlety / preparation

So each ability was trainable by level anyway, and each of those talent
points bought nothing at all. The engine ANDs level and talent only when
requires_talent is set (abilities.py, is_learned), so without the flag the
unlock node is a no-op - exactly as Moonkin Form, Tree of Life and Dire
Bear Form were.

All three ARE real talents in 3.3.5a - Blade Flurry at Combat row 2,
Killing Spree the Combat capstone at row 10, Preparation at Subtlety row 4
- so gating them is faithful, not an invention.

Note what this does NOT do: for a requires_talent ability, is_learned is
`bool(talent_unlocked)` ALONE, with no level check ("the talent IS the
lesson", abilities.py). That is a deliberate project decision affecting all
130-odd talent-gated abilities, so these three now behave like every other
one rather than specially.
"""

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PATH = ROOT / "data/abilities/rogue.json"

GATE = {
    "rogue_blade_flurry":
        "Gated 5 Nov 2026. rogue_combat has carried a blade_flurry "
        "unlock_ability node all along while this ability was NOT "
        "requires_talent, so the ability was trainable by level and the "
        "talent point bought nothing - the same half-finished change found "
        "on the Druid forms. Blade Flurry is a real 3.3.5a Combat talent "
        "(row 2), so the gate is faithful.",
    "rogue_killing_spree":
        "Gated 5 Nov 2026, same reason as Blade Flurry: a real unlock node "
        "in rogue_combat against an ungated ability. Killing Spree is the "
        "real Combat CAPSTONE in 3.3.5a (row 10).",
    "rogue_preparation":
        "Gated 5 Nov 2026, same reason: rogue_subtlety's preparation node "
        "was a no-op. Preparation is a real 3.3.5a Subtlety talent (row 4).",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads(PATH.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
    changed = []
    seen = set()
    for a in data["abilities"]:
        aid = a["ability_id"]
        if aid not in GATE:
            continue
        seen.add(aid)
        if not a.get("requires_talent"):
            a["requires_talent"] = True
            a["_source"] = (a.get("_source", "").rstrip() + " "
                            + GATE[aid]).strip()
            changed.append(aid)

    missing = set(GATE) - seen
    if missing:
        print(f"  ERROR: not in the ability file: {sorted(missing)}")
        return 1

    if not changed:
        print("  nothing to change - all three already gated")
        return 0

    print(f"  gated {len(changed)}:")
    for aid in changed:
        print(f"    {aid}")

    if args.dry_run:
        print("\n  --dry-run, nothing written")
        return 0

    PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"\n  wrote {PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
