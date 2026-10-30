#!/usr/bin/env python3
"""Every item in a boss's pool should be equally likely. Measures it.

    PYTHONPATH=. python3 tools/audit_boss_drop_odds.py
    PYTHONPATH=. python3 tools/audit_boss_drop_odds.py --samples 20000

Kyle, 2026-10-29: "I'm fine with randomness. This should be how it is for the
bosses, right? Can you ensure things like (for example) if a boss drops 4
items, each item has a weight of 25%"

Yes, and this is the check rather than the claim. Boss pools go through
random.choice (or random.sample for the multi-drop bosses), which is uniform -
but "the code calls random.choice" is an argument about the code, and the
thing Kyle asked about is the observed odds. A duplicated entry in a pool, a
boss whose name appears in two data files, or a pool that is a dict rather
than a list would all break uniformity while leaving random.choice in place.

WHY THIS IS A SEPARATE CHECK FROM audit_loot. audit_loot asks whether the
items are any good. This asks whether you can get them.

ONE TEST PER POOL, NOT ONE PER ITEM. The first version put a +/-3 standard
error band around each item's share and flagged anything outside it, which
reported two findings on a data set that is uniform by construction - one of
them a share sitting exactly ON the boundary. Over 44 bosses and ~150 items
some share will always land outside any fixed band, so that design generates
a finding or two every run whatever the data says, and a check that always
finds something teaches people to ignore it. Chi-square asks the question
that was actually asked - "is this pool uniform?" - once per boss, and at
p < 0.001 a flag means something.

The duplicate-entry check is separate and stays, because that is the
structural way a pool stops being uniform while random.choice is still
being called on it, and it needs no statistics at all.
"""
import argparse
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: These are top-level keys in data/loot/epic_drops.json, which the boss-loot
#: loader globs along with every real boss table, so it believes there are
#: bosses called "world" and "dungeon". audit_loot reports that as a finding
#: of its own; this tool just must not measure them as bosses.
NOT_BOSSES = {"world", "dungeon"}


def chi_square_p(chi2, df):
    """Upper-tail probability of chi2 with df degrees of freedom.

    Written out rather than imported because scipy is not a dependency of
    this game and adding one for a survival function would be absurd. For
    even df the series is exact; for odd df it goes through the error
    function, which math provides.
    """
    if df <= 0 or chi2 <= 0:
        return 1.0
    if df % 2 == 0:
        # p = exp(-x) * sum_{k=0}^{df/2 - 1} x^k / k!   where x = chi2/2
        x = chi2 / 2.0
        term = 1.0
        total = 1.0
        for k in range(1, df // 2):
            term *= x / k
            total += term
        return min(1.0, math.exp(-x) * total)
    # Odd df: p = erfc(sqrt(chi2/2)) + the same series shifted, built up
    # from the two base cases df=1 and df=2 by the recurrence
    #   Q(x, df+2) = Q(x, df) + x^(df/2) e^(-x/2) / (2^(df/2) Gamma(df/2 + 1))
    p = math.erfc(math.sqrt(chi2 / 2.0))
    k = 1
    while k < df:
        p += (chi2 ** (k / 2.0) * math.exp(-chi2 / 2.0)
              / (2 ** (k / 2.0) * math.gamma(k / 2.0 + 1)))
        k += 2
    return min(1.0, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=6000,
                    help="draws per boss (default 6000)")
    ap.add_argument("--p", type=float, default=0.001,
                    help="chi-square p below which a pool is called non-uniform "
                         "(default 0.001)")
    ap.add_argument("--self-test", action="store_true",
                    help="rig one pool to be lopsided and confirm this tool "
                         "notices - a check with no negative control has only "
                         "ever been observed passing")
    args = ap.parse_args()

    from entities.boss_loot import (
        _load_boss_loot_tables, get_fixed_boss_loot, get_fixed_boss_loot_all,
        MULTI_DROP, SHARED_HOARD, shares_hoard,
    )

    tables = {k: v for k, v in _load_boss_loot_tables().items() if k not in NOT_BOSSES}

    if args.self_test:
        # A LOPSIDED POOL THIS TOOL MUST CATCH. The last time I shipped a
        # geometry check it passed on a map I had deliberately broken,
        # because sealing a full-width band on a one-line map always cuts.
        # The only way to know a check can fail is to make it fail.
        victim = sorted(tables)[0]
        pool = list(tables[victim])
        # Mutate the loader's own cache, or get_fixed_boss_loot would keep
        # sampling the real pool and the "rigged" run would pass for the
        # most boring possible reason.
        _load_boss_loot_tables()[victim] = pool + [pool[0]] * 4
        tables = {victim: _load_boss_loot_tables()[victim]}
        print(f"SELF TEST: {victim}'s pool rigged with 4 extra copies of "
              f"{pool[0]['name']}\n")

    print(f"{len(tables)} bosses with hand-authored pools, {args.samples} draws each\n")

    findings = []
    for boss in sorted(tables):
        pool = tables[boss]
        names = [d["name"] for d in pool]
        n = len(pool)

        dupes = [nm for nm, c in Counter(names).items() if c > 1]
        if dupes:
            findings.append(f"{boss}: pool lists {', '.join(dupes)} more than once, "
                            f"so that item is likelier than the rest")

        if shares_hoard(boss):
            drops = get_fixed_boss_loot_all(boss)
            if drops:
                findings.append(f"{boss} shares {SHARED_HOARD[boss]}'s hoard but still "
                                f"dropped {len(drops)} item(s) of his own")
            print(f"  {boss:34} shares {SHARED_HOARD[boss]}'s hoard - drops nothing itself")
            continue

        per_kill = MULTI_DROP.get(boss, 1)
        seen = Counter()
        for _ in range(args.samples):
            if per_kill > 1:
                got = get_fixed_boss_loot_all(boss)
                if len(set(i.name for i in got)) != len(got):
                    findings.append(f"{boss}: a kill dropped the same item twice")
                for it in got:
                    seen[it.name] += 1
            else:
                it = get_fixed_boss_loot(boss)
                seen[it.name] += 1

        draws = args.samples * min(per_kill, n)
        expected_share = 1.0 / n
        expected_count = draws / n

        missing = [nm for nm in names if nm not in seen]
        if missing:
            findings.append(f"{boss}: {len(missing)} pool item(s) never dropped in "
                            f"{draws} draws - {', '.join(missing[:3])}")

        # Chi-square goodness of fit against a flat distribution.
        chi2 = sum((seen[nm] - expected_count) ** 2 / expected_count for nm in names)
        p = chi_square_p(chi2, n - 1) if n > 1 else 1.0
        worst = max(names, key=lambda nm: abs(seen[nm] / draws - expected_share))
        drop_note = f"{per_kill} at once" if per_kill > 1 else "1 at a time"
        flag = p < args.p
        print(f"  {boss:34} {n:2} items, {drop_note}, each {expected_share:.1%} "
              f"(widest {seen[worst] / draws:.1%}, p={p:.2f})"
              f"{'  <-- NOT uniform' if flag else ''}")
        if flag:
            findings.append(f"{boss}: pool is not uniform (chi2={chi2:.1f}, "
                            f"df={n - 1}, p={p:.4f}); widest is {worst} at "
                            f"{seen[worst] / draws:.1%} against {expected_share:.1%}")

    print()
    if not findings:
        print("every pool is uniform within sampling noise")
        return 0
    print(f"{len(findings)} FINDING(S)")
    for f in findings:
        print(f"  * {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
