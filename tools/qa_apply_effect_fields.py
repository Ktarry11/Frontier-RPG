#!/usr/bin/env python3
"""Every proc apply_effect spec must be constructible as a StatusEffect.

    PYTHONPATH=. python3 tools/qa_apply_effect_fields.py

WHAT THIS CATCHES, and why nothing else in the project could.

A proc's `apply_effect` dict is passed almost verbatim into
StatusEffect(**spec_kwargs) at status_effects.py:1482, with only
`on_target` and `absorb_pct_max_health` stripped out. So ANY key the
constructor does not accept raises TypeError - and it raises AT PROC TIME,
in the middle of a fight, not at load.

That is the worst possible failure shape:
  - the talent loads fine
  - audit_talents passes, because the data is well-formed JSON with
    plausible keys
  - qa_ability_text passes, because the description reads correctly
  - the tree renders, the point spends, the tooltip promises the effect
  - and then the first time the proc fires, combat dies with a TypeError

Six Tinker nodes shipped that way across two trees, each passing `school`
(the field is `damage_school`) and three of them also passing `dot_damage`
(a TALENT key that is not a status-effect field at all - a proc-applied dot
states per-turn damage as `potency` and must declare effect_type "dot").
They were found by tools/sim_class_balance.py, which plays real fights, and
only because the crash happened to land in a sampled rotation.

This checks it statically instead, by introspecting the real
StatusEffect.__init__ signature rather than hard-coding a field list -
so the check cannot drift from the constructor the way a copied list
would.

IT ALSO FLAGS A SILENT COUSIN: a spec that carries `potency` or
`damage_school` but no `effect_type`. Those are accepted by the
constructor, so they never crash - but an effect with a potency and no
type is not a dot, and the tooltip promising "damage over 3 turns" is
simply false. That is how three of the six Tinker nodes read before the
fix, and it would have survived this check if it only looked for
TypeErrors.

VERIFIED AGAINST THE REAL BREAKAGE: run against the six Tinker specs as
they stood on 6 Nov 2026 this reports all six; with the fix applied it
reports none, and the negative control is that it does not simply pass
everything - it still inspects 300+ specs across 97 trees.
"""

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from combat.status_effects import StatusEffect  # noqa: E402

#: Stripped by the proc path before construction (status_effects.py:1451).
STRIPPED = {"on_target", "absorb_pct_max_health"}

#: Introspected, never hard-coded, so this cannot drift from the real
#: constructor. A copied list is how the original mistake survived review.
_SIG = inspect.signature(StatusEffect.__init__)
ACCEPTED = set(_SIG.parameters) - {"self"}

#: Arguments with NO default - omitting one is just as fatal as passing an
#: unaccepted key, and it was the second crash shape found on 6 Nov 2026.
#: The first version of this tool only looked for REJECTED keys and let
#: four more crashing Tinker nodes through, because a spec missing
#: effect_type carries nothing unusual at all - it is a short, tidy,
#: entirely plausible dict. Both directions have to be checked.
REQUIRED = [n for n, p in _SIG.parameters.items()
            if n != "self" and p.default is inspect._empty]


def specs_of(node):
    spec = (node.get("proc") or {}).get("apply_effect")
    if not spec:
        return []
    return spec if isinstance(spec, list) else [spec]


def main():
    crashes, missing, silent = [], [], []
    checked = 0
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        tree = json.loads(path.read_text(encoding="utf-8"))
        for node in tree["nodes"]:
            for spec in specs_of(node):
                checked += 1
                extra = sorted(k for k in spec
                               if k not in ACCEPTED and k not in STRIPPED)
                absent = [r for r in REQUIRED if r not in spec]
                if extra:
                    crashes.append((path.name, node["talent_id"], extra))
                if absent:
                    missing.append((path.name, node["talent_id"], absent))
                # Accepted by the constructor, so no crash - but an effect
                # with damage potency and no type is not a dot, and its
                # tooltip is lying.
                elif (("potency" in spec or "damage_school" in spec)
                        and not spec.get("effect_type")):
                    silent.append((path.name, node["talent_id"],
                                   sorted(k for k in
                                          ("potency", "damage_school")
                                          if k in spec)))

    print(f"  inspected {checked} proc apply_effect specs across "
          f"{len(list((ROOT / 'data/talents').glob('*.json')))} trees")
    print(f"  StatusEffect accepts: {', '.join(sorted(ACCEPTED))}")
    print(f"  StatusEffect REQUIRES: {', '.join(REQUIRED)}")

    if not crashes and not missing and not silent:
        print("\n  0 SPECS WOULD CRASH, 0 ARE SILENTLY TYPELESS\n\nPASS")
        return 0

    if missing:
        print(f"\n  {len(missing)} SPECS OMIT A REQUIRED ARGUMENT")
        print("  Each raises TypeError AT PROC TIME - combat dies "
              "mid-fight.\n")
        for name, talent, absent in missing:
            print(f"    {talent:48s} missing {absent}   ({name})")

    if crashes:
        print(f"\n  {len(crashes)} SPECS PASS A KEY StatusEffect REJECTS")
        print("  Each raises TypeError AT PROC TIME - combat dies mid-fight.\n")
        for name, talent, extra in crashes:
            print(f"    {talent:48s} {extra}   ({name})")
        print("\n  Common causes: `school` should be `damage_school`; "
              "`dot_damage` is a\n  TALENT key, not a status-effect field "
              "(use effect_type 'dot' + potency).")

    if silent:
        print(f"\n  {len(silent)} SPECS CARRY DAMAGE FIELDS BUT NO effect_type")
        print("  These do not crash - they are just not dots, so the "
              "tooltip is false.\n")
        for name, talent, keys in silent:
            print(f"    {talent:48s} has {keys} without effect_type   "
                  f"({name})")

    print("\nFAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
