#!/usr/bin/env python3
"""Give healing abilities the same rank cadence damage already has.

    PYTHONPATH=. python3 tools/regrade_heal_ranks.py --check
    PYTHONPATH=. python3 tools/regrade_heal_ranks.py

Kyle, 2026-10-31: "i think we need to expand out skills as a lot of healer
skills are not getting that many ranks and they fall behind hard in terms of
what they can do" - and when I hedged, "its systemic with heals bro".

He was right and my first measurement was the wrong instrument. Averaged over
all 133 healing abilities the numbers look level with damage: same median top
rank (56), same lifetime growth (2.54x vs 2.58x), same mean gap between ranks
(9.6 vs 9.1). What that average hides is the SPREAD. A handful of deep heal
tables pull the mean up while 53 of the 133 gain a rank only every 11 to 18
levels. Damage is tight around 6.9. So the healer spends most of the game on a
spell that last improved ten levels ago while the DPS beside them has upgraded
twice, which is exactly what "falls behind hard" feels like from the inside.

Worst cases, all on the classic trinity healers:
    Priest  Heal           5 ranks over 50 levels   next to Smite's 9
    Shaman  Healing Wave   5 ranks over 50 levels   next to Lightning Bolt's 9
    Druid   Healing Touch  3 ranks, last at 29      next to Wrath's 9

WHAT THIS DOES, per Kyle's choice of "keep the endpoints, fill the gaps":

    Rank 1 and the max rank are COPIED THROUGH UNTOUCHED - same level, same
    cost, same value. Everything between them is re-spaced to a ~7 level
    cadence and the values interpolated. So mid-level healing rises and the
    endgame balance that tools/sim_role_balance.py tuned on 28 Oct is
    arithmetically unchanged: the level-56 number is the same number.

THE EIGHT EXCEPTIONS, called out because they are the one place a ceiling
moves. Eight heals stop improving before level 50 - Healing Touch is dead from
29 to 60. For those, "keep the max rank" and "fix the dead stretch" are the
same sentence contradicting itself: holding Healing Touch's endpoint means
holding it at 134 healing at level 29 and leaving the next 31 levels empty.
They get their ladder EXTENDED to the field norm instead, continuing each
ability's own existing per-rank step rather than inventing a new slope. That is
a real power increase at 60 for those eight and nothing else, and --check
prints them so the decision stays visible.
"""
import argparse
import collections
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

HEAL_TYPES = {"heal", "hot", "damage_and_heal"}

#: The cadence damage already runs at, measured not chosen: the mean gap between
#: ranks across all 448 multi-rank damage abilities is 9.1 and the deep nukes
#: that set the felt standard (Wrath, Smite, Fireball, Lightning Bolt) are all
#: on 6.9. Seven is that standard.
TARGET_GAP = 7

#: No table grows past this. Nine is the deepest any ability in the game has.
MAX_RANKS = 9

#: A heal whose top rank lands below this never finishes - see the module note.
DEAD_BEFORE = 50
#: Where an extended ladder tops out. 56 is the median top-rank level in the game.
NORM_TOP = 56

#: Numeric per-rank fields that scale with power and get interpolated. Anything
#: else on a rank is carried from the nearest original rank rather than invented.
SCALED_FIELDS = ("cost", "effect_value", "heal_value", "mana_restore_pct")


def _lerp(a, b, t):
    return a + (b - a) * t


def _levels(first, top, n):
    """n strictly increasing integer levels from first to top inclusive."""
    if n < 2:
        return [first]
    out = [int(round(_lerp(first, top, i / (n - 1)))) for i in range(n)]
    out[0], out[-1] = first, top
    for i in range(1, n):
        if out[i] <= out[i - 1]:
            out[i] = out[i - 1] + 1
    out[-1] = top
    # A forced bump can overshoot the top; pull the interior back under it.
    for i in range(n - 2, 0, -1):
        if out[i] >= out[i + 1]:
            out[i] = out[i + 1] - 1
    return out


def regrade(ability):
    """New rank list for one ability, or None if it is already fine.

    Returns (ranks, extended) - extended is True when the ceiling moved.
    """
    ranks = sorted(ability.get("ranks") or [], key=lambda r: r.get("level_req", 1))
    if not ranks:
        return None
    first = ranks[0]["level_req"]
    top = ranks[-1]["level_req"]
    extended = False

    if top < DEAD_BEFORE:
        # The ladder was never finished. Extend it, continuing this ability's own
        # per-rank step rather than inventing one.
        extended = True
        top = NORM_TOP

    span = top - first
    want = min(MAX_RANKS, max(len(ranks), int(round(span / TARGET_GAP)) + 1))
    if want <= len(ranks) and not extended:
        return None
    if span <= 0:
        return None

    levels = _levels(first, top, want)
    lo, hi = ranks[0], ranks[-1]

    if extended:
        # Keep the real slope. Per original rank-step, projected out to the new top.
        steps = max(1, len(ranks) - 1)
        per = {f: ((hi.get(f) or 0) - (lo.get(f) or 0)) / steps
               for f in SCALED_FIELDS if lo.get(f) is not None}
        orig_span = max(1, ranks[-1]["level_req"] - first)
        hi = dict(hi)
        for f, step in per.items():
            # how many ORIGINAL-sized rank steps the new ladder covers
            projected = (lo.get(f) or 0) + step * steps * (span / orig_span)
            hi[f] = int(round(projected)) if isinstance(lo.get(f), int) else round(projected, 3)

    out = []
    for i, lvl in enumerate(levels):
        t = i / (want - 1)
        src = lo if t < 0.5 else ranks[-1]
        new = collections.OrderedDict()
        new["rank"] = i + 1
        new["level_req"] = lvl
        for f in SCALED_FIELDS:
            a, b = lo.get(f), hi.get(f)
            if a is None and b is None:
                continue
            a = a if a is not None else b
            b = b if b is not None else a
            v = _lerp(a, b, t)
            new[f] = int(round(v)) if isinstance(a, int) and isinstance(b, int) else round(v, 3)
        for k, v in src.items():
            if k not in new:
                new[k] = v
        out.append(new)

    # The endpoints are copied through verbatim, not re-derived, so "unchanged"
    # means byte-identical rather than "rounds to the same thing".
    out[0] = collections.OrderedDict(ranks[0]); out[0]["rank"] = 1
    if not extended:
        out[-1] = collections.OrderedDict(ranks[-1])
    out[-1]["rank"] = len(out)
    return out, extended


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report, write nothing")
    args = ap.parse_args()

    changed = []
    extended = []
    for path in sorted(Path("data/abilities").glob("*.json")):
        cid = path.stem
        if cid.startswith("_") or cid == "asher_unique":
            continue
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=collections.OrderedDict)
        dirty = False
        for ability in data.get("abilities", []):
            if ability.get("effect_type") not in HEAL_TYPES:
                continue
            res = regrade(ability)
            if not res:
                continue
            new_ranks, was_extended = res
            old = ability["ranks"]
            rec = (cid, ability["name"], len(old), len(new_ranks),
                   old[0]["level_req"], old[-1]["level_req"], new_ranks[-1]["level_req"])
            changed.append(rec)
            if was_extended:
                extended.append(rec)
            if not args.check:
                ability["ranks"] = new_ranks
                dirty = True
        if dirty:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{len(changed)} heal tables regraded\n")
    for c in sorted(changed):
        mark = "  CEILING EXTENDED" if c in extended else ""
        print(f"  {c[0]:16s} {c[1]:26s} {c[2]} -> {c[3]} ranks, "
              f"lvl {c[4]}-{c[5]} -> {c[4]}-{c[6]}{mark}")
    if extended:
        print(f"\n{len(extended)} of those had their ceiling moved "
              f"(they stopped improving before level {DEAD_BEFORE}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
