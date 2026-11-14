#!/usr/bin/env python3
"""Bring every hand-authored two-hander onto the corrected stat budget.

    PYTHONPATH=. python3 tools/rebudget_two_handers.py [--check]

Kyle, 5 Nov 2026: "Go through the existing 2H weapons to fix them."

These were all solved from the OLD formula, which charged for two-handedness
twice - slot weight 1.5 multiplied by budget_multiplier 2.24, on top of the
damage a two-hander already gets from its damage tier. That was fixed in
data/items/{slots,weapon_types}.json, which corrected every generated item
instantly and left 203 hand-authored two-handers sitting at a median 2.47x
their own budget, plus 115 staves at 1.38x.

CHANGE THE NUMBERS, NEVER THE IDENTITY - the rule tools/fix_item_budgets.py
set for the same job at smaller scale, and the reason this does not need the
gear profile sheet first. An item that was strength-and-stamina stays
strength-and-stamina in the same proportion; only the magnitude moves. WHICH
stats an item carries is the gear sheet's question and is left entirely
alone here.

That file hand-curates a replacement stat block per item NAME, which is right
for eight items and impossible for 203. This scales proportionally instead,
against audit_item_budgets.spend() rather than a raw sum, so stats that cost
more than a point each (healing_power at 1.25) are priced the way the
generator prices them.

ROUNDING IS PART OF THE FIX, not a cosmetic afterthought - backlog item 7,
Kyle: "I'm tired of seeing +0.82% crit or +13.22 sp. We should use round
integers when possible, rounded to .25% or whole numbers." Scaling by a
fraction is exactly what produces 13.22, so rounding happens here, inside the
solve, and the result is re-priced afterwards so the printed total is the real
one.

Idempotent: anything already within tolerance is skipped, so this can be run
again after the next formula change without churning the files.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("_aib", ROOT / "tools/audit_item_budgets.py")
_aib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_aib)

TOLERANCE = 0.12          # how close to 1.0x counts as already correct
MIN_STAT = 1              # never round a real stat away to nothing

#: Stats written as percentages, rounded to 0.25 rather than to whole numbers.
PERCENT_STATS = {
    "crit_chance_physical", "crit_chance_spell", "dodge_chance", "parry_chance",
    "block_chance", "haste", "spell_pen_pct", "hit_chance",
}


def _round_stat(stat, value):
    """Whole numbers, or quarters for percentages. Never below MIN_STAT."""
    if stat in PERCENT_STATS:
        return max(0.25, round(value * 4.0) / 4.0)
    return max(MIN_STAT, int(round(value)))


#: A secondary costing more than this share of the whole budget for ONE point
#: cannot be carried at all, and is dropped rather than kept at 1.
UNAFFORDABLE_SHARE = 0.5


def _drop_unaffordable(item, budget):
    """Remove secondaries the item cannot afford a single point of.

    Twenty-five low-level two-handers could not be brought onto budget by
    scaling, because scaling cannot go below one point and one point of some
    stats costs more than the item's entire budget. The worst, an ilvl 10
    uncommon polearm with a budget of 5.1, carried dodge_rating AND
    parry_rating - priced at 7.5 and 10 a point, so 17.5 of a 5.1 budget, and
    stuck at 3.43x however hard it was scaled.

    Dropping the stat is the honest fix, not a violation of
    change-the-numbers-never-the-identity. An item that cannot afford a point
    of parry has no parry identity to protect; what it has is an authoring
    mistake, parry rating on a level 10 weapon. The budget freed goes back
    into whatever the item already leads with, so it keeps its character and
    gets more of it.
    """
    dropped = False
    out = dict(item)
    secondaries = dict(item.get("secondary_stats") or {})
    for stat in list(secondaries):
        if _aib._COSTS.get(stat, 1.0) > budget * UNAFFORDABLE_SHARE:
            del secondaries[stat]
            dropped = True
    if not dropped:
        return item

    out["secondary_stats"] = secondaries
    # Nothing left to scale: give it the plainest stat there is, sized to
    # budget, rather than leaving a weapon with no stats at all.
    if not secondaries and not (item.get("primary_stats") or {}):
        out["primary_stats"] = {"stamina": max(MIN_STAT, int(round(budget)))}
    return out


def rescale(item, budget):
    """New stat blocks for `item`, same shape and proportions, sized to budget.

    Returns None when nothing would change.

    Scales every stat by one factor so the item's character survives - the
    biggest stat stays the biggest, the hybrid stays a hybrid. Rounding is
    applied per stat afterwards, which is why the result is re-priced and the
    factor nudged once: rounding 9 stats up can push a tight item back over
    budget, and an item that lands at 1.14x after a fix that was supposed to
    bring it to 1.0x is not fixed.
    """
    original = item
    item = _drop_unaffordable(item, budget)
    spent = _aib.spend(item)
    if spent <= 0:
        return None

    factor = budget / spent
    best = None
    # A couple of passes: scale, round, re-price, correct the factor for what
    # rounding cost or gained. Converges immediately in practice.
    for _ in range(6):
        blocks = {}
        for block in ("primary_stats", "secondary_stats"):
            src = item.get(block) or {}
            # Emitted even when empty, so a block emptied by _drop_unaffordable
            # is actually written back as {} rather than silently left as it
            # was on the original item.
            blocks[block] = {s: _round_stat(s, v * factor) for s, v in src.items()}

        probe = dict(item)
        probe.update(blocks)
        got = _aib.spend(probe)
        if got <= 0:
            return None
        ratio = got / budget
        if best is None or abs(ratio - 1.0) < abs(best[1] - 1.0):
            best = (blocks, ratio)
        if abs(ratio - 1.0) <= 0.02:
            break
        factor *= budget / got

    blocks, _ratio = best
    # Compared against the ORIGINAL item, not the pruned copy. `item` was
    # rebound by _drop_unaffordable above, so comparing to it asked "did
    # scaling change the pruned version" - and for an item fixed purely BY
    # the pruning the answer is no. Those returned None and were counted as
    # "already on budget", which is how eight quest two-handers sat at
    # 2.4-2.55x through a run that reported a maximum of 1.28x. A reporting
    # bug that hid the very items it was meant to find.
    if all(blocks.get(b) == (original.get(b) or {}) for b in blocks):
        return None
    return blocks


def main():
    check = "--check" in sys.argv
    weapons = _aib._WEAPONS["weapon_types"]

    touched_files = {}
    changed = skipped = 0
    worst = []

    for src, owner, item in _aib.collect():
        wtype = item.get("weapon_type")
        if not wtype or wtype not in weapons:
            continue
        if weapons[wtype].get("hand") != "two_hand":
            continue

        budget, _a, _d = _aib.budget_for(item)
        if not budget:
            continue
        before = _aib.spend(item) / budget
        if abs(before - 1.0) <= TOLERANCE:
            skipped += 1
            continue

        blocks = rescale(item, budget)
        if blocks is None:
            skipped += 1
            continue

        probe = dict(item)
        probe.update(blocks)
        after = _aib.spend(probe) / budget
        worst.append((before, after, item["name"], wtype, owner))
        if not check:
            item.update(blocks)
            touched_files[owner.split("/")[0]] = True
        changed += 1

    worst.sort(reverse=True)
    print(f"two-handers rescaled: {changed}   already on budget: {skipped}")
    if worst:
        print(f"\n{'before':>7} {'after':>7}  {'type':<10} name")
        for before, after, name, wtype, _owner in worst[:12]:
            print(f"{before:6.2f}x {after:6.2f}x  {wtype:<10} {name}")
        if len(worst) > 12:
            print(f"   ... and {len(worst) - 12} more")
        ratios = [a for _b, a, _n, _w, _o in worst]
        print(f"\nafter: min {min(ratios):.2f}x  max {max(ratios):.2f}x  "
              f"median {sorted(ratios)[len(ratios) // 2]:.2f}x")

    if check:
        print("\n--check: nothing written")
        return 0 if changed == 0 else 1

    # Write back. collect() hands out live dicts from documents it parsed, so
    # the files are re-read, re-walked and re-written here rather than trying
    # to hold every parsed document in memory across the pass.
    written = _write_back()
    print(f"\nfiles written: {written}")
    return 0


def _write_back():
    """Re-apply the in-memory edits by re-walking the same files collect() read.

    collect() parses each file into throwaway dicts, so mutating the items it
    yields does NOT touch anything on disk. Rather than rewrite collect() and
    risk changing what the audit sees, this re-runs the same scan with the
    documents held open, applies the same rule, and writes.
    """
    weapons = _aib._WEAPONS["weapon_types"]
    written = 0

    def handle(item):
        wtype = item.get("weapon_type")
        if not wtype or wtype not in weapons:
            return False
        if weapons[wtype].get("hand") != "two_hand":
            return False
        budget, _a, _d = _aib.budget_for(item)
        if not budget:
            return False
        if abs(_aib.spend(item) / budget - 1.0) <= TOLERANCE:
            return False
        blocks = rescale(item, budget)
        if blocks is None:
            return False
        item.update(blocks)
        return True

    for path in sorted((ROOT / "data/quests").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        dirty = False
        for quest in doc.get("quests", []):
            for item in (quest.get("unique_item_defs") or []) + (quest.get("rewards") or []):
                dirty |= handle(item)
        if dirty:
            path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            written += 1

    for path in sorted((ROOT / "data/loot").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        rows = doc.get("bosses", doc)
        if not isinstance(rows, dict):
            continue
        dirty = False
        for owner, items in rows.items():
            if owner.startswith("_") or not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and item.get("item_level"):
                    dirty |= handle(item)
        if dirty:
            path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
            written += 1

    return written


if __name__ == "__main__":
    sys.exit(main())
