#!/usr/bin/env python3
"""Catch ability-scoped talent keys that name a field their ability HAS NOT GOT.

    PYTHONPATH=. python3 tools/qa_ability_scoped_fields.py
    PYTHONPATH=. python3 tools/qa_ability_scoped_fields.py --all

WHY THIS EXISTS. probe_talent_key.py --audit-all already checks that the
ability half of an `ability_<id>_<field>` key names a REAL ability. That
is necessary and not sufficient: the ability can exist and still have
nothing for that field to scale.

The case that prompted it, found 6 Nov while rebuilding druid_balance:

    Brambles authored ability_druid_thorns_damage
                  and ability_druid_entangling_roots_damage

Both abilities exist, so --audit-all passed them. But druid_thorns is
effect_type 'buff' whose content is stat_mods {'damage_dealt_pct': 3.0},
and druid_entangling_roots is a 'debuff' whose content is stat_mods
{'haste': -18, 'dodge': -12}. NEITHER HAS DAMAGE OF ITS OWN. Both keys
were silent dead data, and the whole node did nothing. The real talent
says the word "damage", which is how it happened - the WotLK text
describes a reflect, and this engine has no reflect mechanic, so Thorns
became an ally damage buff instead. _potency is the key that reaches it.

audit_talents.py does not catch this either: it checks UNIT CONVENTIONS
(is this key a fraction or points), not whether the target can receive
the key at all. So nothing in the chain saw it.

WHAT COUNTS AS A MISMATCH. Conservative on purpose - it only reports a
key when the ability demonstrably cannot carry it:

  _damage / _crit / _crit_damage  need the ability to deal damage:
      effect_type is a damage or dot type, OR any rank carries
      effect_value with a damaging effect_type.
  _healing                         needs a heal or hot effect_type.
  _potency                         needs stat_mods to scale.
  _duration                        needs a duration.
  _cost / _cost_pct                needs a nonzero cost on some rank.
  _cooldown / _cooldown_pct        needs a nonzero cooldown.

Anything it is unsure about it passes. A clean run is therefore weak
evidence; a FAIL is strong evidence.

NOT A LINTER FOR INTENT. It cannot tell you that _potency was the key you
MEANT, only that _damage was a key the ability cannot use.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIELDS = ("crit_damage", "cooldown_pct", "cost_pct", "cooldown",
          "duration", "healing", "potency", "damage", "crit", "cost")

DAMAGE_TYPES = {"damage", "spell_damage", "dot", "spell_dot", "physical",
                "attack", "aoe", "spell_aoe", "bleed", "damage_debuff"}
HEAL_TYPES = {"heal", "hot", "spell_heal", "heal_aoe", "shield", "absorb"}


def load_abilities():
    """ability_id -> the ability dict, across every class file."""
    out = {}
    for path in sorted((ROOT / "data" / "abilities").glob("*.json")):
        raw = json.loads(path.read_text())
        entries = raw if isinstance(raw, list) else raw.get("abilities", raw)
        if isinstance(entries, dict):
            entries = [dict(v, ability_id=k) for k, v in entries.items()]
        for a in entries:
            if isinstance(a, dict) and a.get("ability_id"):
                out[a["ability_id"]] = a
    return out


def split_key(key, abilities):
    """Longest field suffix first, preferring a split whose id is real.

    Same rule as probe_talent_key.split_ability_key - a greedy split once
    read ability_X_crit_damage as id 'X_crit' + field 'damage' and falsely
    accused all 20 legitimate _crit_damage keys in the project.
    """
    if not key.startswith("ability_"):
        return None
    body = key[len("ability_"):]
    best = None
    for field in FIELDS:
        suffix = "_" + field
        if body.endswith(suffix):
            aid = body[: -len(suffix)]
            if aid in abilities:
                return aid, field
            if best is None:
                best = (aid, field)
    return best


def ranks_of(a):
    return a.get("ranks") or []


def deals_damage(a):
    et = (a.get("effect_type") or "").lower()
    if et in DAMAGE_TYPES or "damage" in et or "dot" in et:
        return True
    return False


def heals(a):
    et = (a.get("effect_type") or "").lower()
    return et in HEAL_TYPES or "heal" in et or et == "hot"


def has_stat_mods(a):
    if a.get("stat_mods"):
        return True
    return any(r.get("stat_mods") for r in ranks_of(a))


def has_duration(a):
    if a.get("duration"):
        return True
    return any(r.get("duration") for r in ranks_of(a))


def has_cost(a):
    if a.get("cost") or a.get("secondary_cost"):
        return True
    return any(r.get("cost") for r in ranks_of(a))


def has_cooldown(a):
    return bool(a.get("cooldown")) or any(r.get("cooldown") for r in ranks_of(a))


def check(aid, field, a):
    """Return a reason string if this field cannot land, else None."""
    if field == "damage":
        # _damage is read at abilities.py:1574 for EVERY ability, BEFORE the
        # school=="healing" branch - so it lands on heals too, and a heal
        # carrying _damage is NOT dead. The first draft of this file accused
        # two of them. Only a pure buff/debuff with no damage and no healing
        # has nothing for _damage to scale.
        if not deals_damage(a) and not heals(a):
            what = ("stat_mods " + str(a.get("stat_mods"))
                    if has_stat_mods(a) else "no damage of any kind")
            return (f"{aid} is effect_type '{a.get('effect_type')}' with "
                    f"{what}"
                    + (" (use _potency)" if has_stat_mods(a) else ""))
    elif field in ("crit", "crit_damage"):
        # HEALS DO NOT ROLL CRIT in this engine: _roll_crit is called only
        # from the four damage branches (abilities.py:2597/2656/2748/2799)
        # and nowhere in the healing path, so ability_<heal>_crit is dead.
        # Measured by reading the call sites, not assumed.
        if not deals_damage(a):
            if heals(a):
                return (f"{aid} is effect_type '{a.get('effect_type')}' - it "
                        f"HEALS, and heals never roll crit in this engine")
            what = ("stat_mods " + str(a.get("stat_mods"))
                    if has_stat_mods(a) else "no damage of any kind")
            return (f"{aid} is effect_type '{a.get('effect_type')}' with "
                    f"{what}"
                    + (" (use _potency)" if field == "damage" and
                       has_stat_mods(a) else ""))
    elif field == "healing":
        if not heals(a) and not has_stat_mods(a):
            return (f"{aid} is effect_type '{a.get('effect_type')}' - it does "
                    f"not heal")
    elif field == "potency":
        if not has_stat_mods(a):
            return (f"{aid} carries no stat_mods, so there is no potency to "
                    f"scale")
    elif field == "duration":
        if not has_duration(a):
            return f"{aid} has no duration to extend"
    elif field in ("cost", "cost_pct"):
        if not has_cost(a):
            return f"{aid} is free - there is no cost to reduce"
    elif field in ("cooldown", "cooldown_pct"):
        if not has_cooldown(a):
            return f"{aid} has no cooldown to reduce"
    return None


def walk(node, out):
    for key, val in (node.get("effects") or {}).items():
        out.append(key)
    for key in (node.get("conditional_guardian_effects") or {}):
        out.append(key)


def main():
    show_all = "--all" in sys.argv
    abilities = load_abilities()
    problems = defaultdict(list)
    total = 0

    for path in sorted((ROOT / "data" / "talents").glob("*.json")):
        tree = json.loads(path.read_text())
        for node in tree.get("nodes", []):
            keys = []
            walk(node, keys)
            for key in keys:
                split = split_key(key, abilities)
                if not split:
                    continue
                aid, field = split
                a = abilities.get(aid)
                if a is None:
                    continue  # probe --audit-all owns that case
                total += 1
                reason = check(aid, field, a)
                if reason:
                    problems[path.stem].append(
                        (node.get("talent_id"), node.get("name"), key, reason))

    print()
    print(f"  {total} ability-scoped keys checked against their ability's "
          f"actual shape")
    print(f"  {len(abilities)} abilities loaded")
    print()

    if not problems:
        print("  0 KEYS NAME A FIELD THEIR ABILITY HAS NOT GOT")
        print()
        print("PASS")
        return 0

    count = sum(len(v) for v in problems.values())
    print(f"  {count} KEY(S) CANNOT LAND - silent dead data")
    print()
    shown = 0
    for tree_id in sorted(problems):
        print(f"  {tree_id}")
        for tid, name, key, reason in problems[tree_id]:
            if not show_all and shown >= 40:
                continue
            print(f"      {name} ({tid})")
            print(f"        {key}")
            print(f"        -> {reason}")
            shown += 1
        print()
    if not show_all and count > shown:
        print(f"  ... {count - shown} more, --all to list")
        print()
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
