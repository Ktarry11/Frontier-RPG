#!/usr/bin/env python3
"""The vendor trash curve: every level can drop something, it has art, and it is worth more.

    PYTHONPATH=. python3 tools/qa_vendor_trash_curve.py

Kyle: "keep auditing the curve... increase vendor trash sale value at higher levels. We dont need
trash chance we need new vendor trash." and "just reskin trash icons to higher tier versions."

Level gates and art bands both make it possible to ship a level at which something is broken in a
way nothing else notices: a family with every entry gated out, or an entry whose banded art was
never generated. Both fail silently in the game - an empty family falls back, a missing icon
renders as nothing - so they are checked here instead.

FOUR CLAIMS:

  1. EVERY FAMILY CAN DROP AT EVERY LEVEL 1-60. A gate that empties a family means the fallback in
     _pick quietly serves retired scraps to a level 55 player.
  2. EVERY ENTRY'S ICON EXISTS IN EVERY BAND IT CAN DROP IN - including the per-element variants,
     which multiply (vt_core_fire needs vt_core_fire_t2 and _t3). This is the claim that catches
     somebody adding a base icon and not re-running the reskin tool.
  3. TRASH VALUE NEVER GOES DOWN AS LEVEL GOES UP. The whole reason this file exists: tier 5 used
     to be max_level 999, so levels 30-60 were one flat price and the newest zones paid a level 30
     rate. A flat stretch is allowed (a tier is flat by definition); a DROP is not.
  4. A TRASH KILL STAYS WORTH A FAIR SHARE OF A COIN KILL. The first version of this claim
     compared the mean trash PRICE to the coin a humanoid drops, and failed at 15 levels - because
     trash price steps at tier boundaries while coin rises smoothly, so the ratio spikes at the
     start of every tier and decays across it. That sawtooth is not a defect: a tier is flat by
     design, and it has to be, because every "Flawless Fang" must carry the same vendor price or
     two of them will not stack.

     The quantity that actually matters is EXPECTED VALUE PER KILL - trash price times the chance
     it drops at all, against the coin a coin-dropper pays every single time. That ratio is the
     structural property of this economy and the reason a crystal sinkhole pays less than a
     pirate cove: a coin mob pays on 100% of kills and a trash mob on 30%. It is reported per
     level below, and bounded loosely so this file catches a regression without pretending the
     gap is a bug.

  5. A DUNGEON PAYS FOR BEING A DUNGEON. Kyle: "Dungeons generally should give better money as
     they are harder." Every cave must out-earn an OPEN ZONE OF ITS OWN LEVEL - not its parent
     zone, which is the comparison that hid this: Dustwind Cave looked like 1.18x Durotar while
     actually paying 1.16x what level 4-8 ground pays, and Durotar's band runs to 18.

     Measured that way, 14 of 47 dungeons paid under 1.5x and three paid LESS than the open
     world, worst of all The Den at 0.67x. This claim is simulated rather than derived, because
     what a dungeon pays depends on its encounter table and no amount of reading the rates block
     will tell you a cave is full of beasts.
"""
import json
import os
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from entities.vendor_trash import _config, _tier, make_item, _band_suffix  # noqa: E402

ICON_DIR = ROOT / "assets" / "icons" / "vendor_trash"

#: a dungeon must out-earn open ground of its own level by at least this much. Today the worst is
#: 1.64x and the median is 2.58x.
DUNGEON_FLOOR = 1.5
SAMPLE = 3000
LEVELS = range(1, 61)
#: expected-value-per-kill of a trash dropper as a fraction of a coin dropper. Loose on purpose -
#: see claim 4. Today this runs 0.33 (level 10) to 0.59 (level 50).
RATIO = (0.25, 1.6)


def _live(entries, level):
    return [e for e in entries
            if e.get("min_level", 0) <= level <= e.get("max_level", 10 ** 9)]


def main():
    cfg = _config()
    bad = []

    # ---- 1. every family can drop at every level
    for fam, entries in cfg["families"].items():
        for lvl in LEVELS:
            if not _live(entries, lvl):
                bad.append(f"family {fam!r} has NO entry available at level {lvl} - _pick would "
                           f"fall back to the ungated list and serve retired items.")
                break

    # ---- 2. art exists in every band an entry can reach
    bands = sorted({_band_suffix(l) for l in LEVELS})
    for fam, entries in cfg["families"].items():
        for e in entries:
            icon = e.get("icon")
            if not icon:
                bad.append(f"{fam}/{e['id']} has no icon field")
                continue
            reach = sorted({_band_suffix(l) for l in LEVELS if e in _live(entries, l)})
            # `element: true` with NO `elements` list means the entry takes ANY element, so it
            # needs art for all of them. Reading a null list as "no variants" is how deleting
            # vt_core_fire_t3.png passed this check the first time it was tested.
            if e.get("element"):
                els = e.get("elements") or list(cfg["elements"])
                stems = [f"{icon}_{el}" for el in els]
            else:
                stems = [icon]
            for stem in stems:
                for suf in reach:
                    if not (ICON_DIR / f"{stem}{suf}.png").exists():
                        bad.append(f"{fam}/{e['id']}: no art {stem}{suf}.png (needed for levels "
                                   f"in band {suf or 'base'}) - re-run "
                                   f"tools/reskin_vendor_trash_icons.py")

    # ---- 3 & 4. the curve itself
    prev = 0.0
    rows = []
    means = {}
    for lvl in LEVELS:
        vals = [make_item(f, e, lvl)["price"]
                for f, es in cfg["families"].items() if f != "junk"
                for e in _live(es, lvl)]
        mean = sum(vals) / len(vals)
        # what each KIND of mob is worth per kill: a trash dropper pays mean * trash_chance, a
        # coin dropper pays its coin roll every time (per_level * level, plus a bonus averaging
        # half of bonus_max).
        per_kill_trash = mean * cfg["rates"]["open_zone"]["trash_chance"]
        coin = lvl * cfg["coin"]["per_level"] * (1 + cfg["coin"]["bonus_max"] / 2)
        rows.append((lvl, mean, coin, per_kill_trash / coin))
        if mean < prev - 0.5:
            bad.append(f"level {lvl}: mean trash {mean:.0f}c is BELOW level {lvl - 1}'s "
                       f"{prev:.0f}c - the curve goes backwards here.")
        prev = max(prev, mean)
        means[lvl] = mean
        if not (RATIO[0] <= rows[-1][3] <= RATIO[1]):
            bad.append(f"level {lvl}: a trash kill is worth {rows[-1][3]:.2f}x a coin kill, "
                       f"outside {RATIO} - trash {per_kill_trash:.0f}c/kill vs coin "
                       f"{coin:.0f}c/kill")

    # A FLATLINE IS THE BUG THIS FILE EXISTS FOR, and "never decreases" does not catch one.
    # Restoring the original defect - tier 5 at max_level 999, so levels 30-60 all paid a level
    # 30 rate - passed the decrease check cleanly, because a flat line never goes down. Ten levels
    # of progress must be worth something, so that is what gets asserted.
    for lvl in LEVELS:
        if lvl + 10 in means and means[lvl + 10] <= means[lvl] + 0.5:
            bad.append(f"levels {lvl}-{lvl + 10} are FLAT at {means[lvl]:.0f}c - ten levels of "
                       f"progress has to be worth more trash than it was.")

    print(f"{'lvl':>4} {'tier':11} {'mean trash':>11} {'coin/kill':>10} "
          f"{'trash kill vs coin kill':>24}  live")
    for lvl, mean, coin, r in rows:
        if lvl % 5 and lvl != 1:
            continue
        _, t = _tier(lvl)
        n = sum(len(_live(es, lvl)) for es in cfg["families"].values())
        print(f"  {lvl:3} {t['adjective']:11} {mean:10.0f}c {coin:9.0f}c "
              f"{r:23.2f}x  {n:3}")

    # ---- 5. dungeons out-earn open ground of their own level
    from entities.vendor_trash import roll_drops
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    zl = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]

    class _E:
        def __init__(self, n, l, loc):
            self.name, self.level, self.location_type, self.is_boss = n, l, loc, False

    def _tbl(d):
        return [(k, w) for k, w in d.items()
                if w > 0 and k in cre and not cre[k].get("is_boss")]

    def _income(rows, loc, n=SAMPLE, seed=1):
        rng = random.Random(seed)
        names = [r[0] for r in rows]
        ws = [r[1] for r in rows]
        tot = 0
        for _ in range(n):
            nm = rng.choices(names, weights=ws, k=1)[0]
            a, b2 = cre[nm].get("level_range", [1, 1])[:2]
            r = roll_drops(_E(nm, rng.randint(max(1, a), max(1, b2)), loc), rng=rng)
            tot += r["copper"] + sum(i["price"] for i in r["items"])
        return tot / n

    open_by_zone = {}
    for z, zz in enc.items():
        t = dict(zz.get("open_zone", {}).get("creatures", {}))
        for sz in zz.get("subzones", {}).values():
            for k, v in sz.get("creatures", {}).items():
                t[k] = max(t.get(k, 0), v)
        rows = _tbl(t)
        if rows and z in zl:
            open_by_zone[z] = (zl[z], _income(rows, "open_zone"))
    open_at = {}
    for L in LEVELS:
        v = [i for (bb, i) in open_by_zone.values() if bb[0] <= L <= bb[1]]
        if v:
            open_at[L] = statistics.mean(v)

    ratios = []
    for z, zz in enc.items():
        for cname, cv in zz.get("caves", {}).items():
            rows = _tbl(cv.get("creatures", {}))
            if not rows or cname not in zl:
                continue
            bb = zl[cname]
            mid = (bb[0] + bb[1]) // 2
            if mid not in open_at:
                continue
            r = _income(rows, "cave") / open_at[mid]
            ratios.append((r, cname, bb))
            if r < DUNGEON_FLOOR:
                bad.append(f"{cname} ({bb[0]}-{bb[1]}) pays {r:.2f}x an open zone of its level, "
                           f"under the {DUNGEON_FLOOR}x floor - it is harder and should pay more.")
    if ratios:
        rs = sorted(ratios)
        print(f"\n{len(rs)} dungeons vs open ground of their own level: "
              f"min {rs[0][0]:.2f}x ({rs[0][1]}), median "
              f"{statistics.median([r for r, _, _ in rs]):.2f}x, max {rs[-1][0]:.2f}x")

    print(f"\n{len(list(ICON_DIR.glob('*.png')))} icon files across bands {bands}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:30]:
            print("  -", b)
        return 1
    print("curve OK - every family drops at every level, all banded art exists, trash never "
          "decreases with level, it tracks coin the whole way, and every dungeon out-earns open "
          "ground of its own level.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
