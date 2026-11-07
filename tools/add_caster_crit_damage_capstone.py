#!/usr/bin/env python3
"""Every caster tree gets a 5-point talent worth +100% spell crit damage.

    PYTHONPATH=. python3 tools/add_caster_crit_damage_capstone.py [--apply]

Kyle, 6 Nov: "all caster classes should have a 5 point talent that increases
their spell crit damage by 100%."

The model already exists in three trees and two of them are WoW-accurate:

    priest_shadow     Shadow Power     5 x 20%   (WotLK row 4, verbatim)
    shaman_elemental  Elemental Fury   5 x 20%
    felsworn_infernal Man'ari Teachings  1 x 100%

...and nowhere else. Of 37 caster specs (stat_template int_caster or
spi_healer), 17 carry some crit-damage node at 20-60% on 1-5 points, and
20 have nothing at all.

WHAT THIS TOOL DOES: the 17 upgrades only. Each keeps its name, hex
position, tier and connections - only max_points, effects and description
change. Inserting the 20 missing nodes is a LAYOUT job (hex coordinates,
tier placement, connection edges, and a tree point budget that shifts) and
is deliberately left for a deliberate pass rather than generated.

THE KEY IS crit_damage_spell, which combat/abilities.py::_crit_damage_bonus
reads and stacks additively with ability_<id>_crit_damage and
<school>_crit_damage_pct. Verified before authoring, because this session
has already turned up two stat keys that were authored and never read
(pushback_reduction_pct among them). A fraction: 0.2 means crits land for
2.2x instead of 2.0x, which is how that function already reads the data.

SCOPE WIDENS SLIGHTLY AND ON PURPOSE. Several of the 17 were scoped to
named abilities (Mage Fire's Burnout, Necromancer's Fiend). Kyle asked for
"spell crit damage", not "crit damage on two spells", so they convert to
the general key. Their old ability-scoped entries are dropped rather than
left alongside, or the talent would pay twice on those abilities.

HEALERS ARE INCLUDED because spi_healer is a caster template, and
_crit_damage_bonus applies to any non-physical school. A healer's crits
getting 2.2x instead of 2.0x is a real throughput gain - flagged for Kyle
rather than silently excluded, since "all caster classes" is what was
asked for.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALENTS = ROOT / "data/talents"
SPEC_GEAR = ROOT / "data/items/spec_gear.json"

#: stat_template values that mean "this spec casts".
CASTER_TEMPLATES = {"int_caster", "spi_healer"}

KEY = "crit_damage_spell"
RANKS = 5
PER_RANK = 0.2


def caster_specs():
    doc = json.loads(SPEC_GEAR.read_text())
    specs = doc.get("specs", doc)
    return {k for k, v in specs.items()
            if isinstance(v, dict) and v.get("stat_template") in CASTER_TEMPLATES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    casters = caster_specs()
    upgraded, missing = [], []

    for path in sorted(TALENTS.glob("*.json")):
        tree = path.stem
        if tree not in casters:
            continue
        doc = json.loads(path.read_text())

        best = None
        for node in doc.get("nodes", []):
            if not isinstance(node, dict):
                continue
            effects = node.get("effects") or {}
            crit_keys = [k for k in effects if "crit_damage" in k]
            if not crit_keys:
                continue
            ranks = node.get("max_points") or 1
            total = max(abs(effects[k]) * ranks for k in crit_keys)
            if best is None or total > best[1]:
                best = (node, total, crit_keys)

        if best is None:
            missing.append(tree)
            continue

        node, old_total, crit_keys = best
        old_ranks = node.get("max_points") or 1
        for key in crit_keys:
            node["effects"].pop(key, None)
        node["effects"][KEY] = PER_RANK
        node["max_points"] = RANKS
        node["description"] = (
            f"Increases the critical strike damage of your spells by "
            f"{PER_RANK * 100:g}% per rank.")
        node["_source"] = (
            "Standardised 6 Nov: every caster tree carries one 5-point "
            "spell-crit-damage talent worth +100% at full rank, matching "
            "priest_shadow's Shadow Power and shaman_elemental's Elemental "
            "Fury (both WoW-accurate). Kyle: 'all caster classes should have "
            "a 5 point talent that increases their spell crit damage by "
            "100%.'")
        upgraded.append((tree, node.get("name"), old_ranks, old_total))
        if args.apply:
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    print(f"caster specs: {len(casters)}\n")
    print(f"upgraded to {RANKS} x {PER_RANK * 100:g}% = "
          f"{RANKS * PER_RANK * 100:g}%: {len(upgraded)}\n")
    print(f"{'tree':30}{'talent':26}{'was':>14}")
    for tree, name, ranks, total in upgraded:
        print(f"  {tree:28}{str(name)[:24]:26}{ranks}pt {total * 100:>4.0f}%")

    print(f"\nNO crit-damage node to upgrade - need one authored "
          f"(hex position, tier, connections): {len(missing)}")
    for tree in missing:
        print(f"  {tree}")

    if not args.apply:
        print("\n(report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
