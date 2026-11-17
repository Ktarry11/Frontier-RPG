#!/usr/bin/env python3
"""Write data/balance/heal_reference.json: the tank every heal and every boss hit is sized against.

    PYTHONPATH=. python3 tools/calibrate_heal_reference.py [--seeds 4] [--step 5]

The healing formula (docs/heal_formula.md, Kyle 16 Nov 2026: "20 unspecced is fine. 2 is fine with 40 and 25%")
measures everything against T(L), the max health of a geared Protection Warrior of level L. A heal's base is a share
of it, a healer's gear is sized so it adds a share of the base, and a boss's hits are shares of it.

Per level (every STEP, plus 1 and 60), averaged over SEEDS gear rolls:
  tank      a geared Protection Warrior's max health (tools/sim_matrix.build, "geared": uncommon below 20, rare from)
  power     the median healing power, on the combat scale, of every healer spec built and geared at that level
  authored  the authored rank line for each heal kind (heal, HoT, a damage spell's heal), so a spell keeps its
            character against the formula (combat/heal_formula.rank_size)
Every level is then read off a smooth fit: a straight line through each value's ratio to the world curve
(combat/world_curve.growth), times the curve. So the table grows the way the world does and never dips.

Rerun it when character health or healing-power itemization changes. Nothing else writes this file.
"""
import argparse
import contextlib
import io
import json
import os
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

OUT = ROOT / "data/balance/heal_reference.json"
TANK_SPEC = "warrior_protection"


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def fit(points, top=60):
    """{level: value} at a few levels -> a SMOOTH value for every level 1..top: a straight line fitted to each
    point's ratio to the world curve, times the world curve. Measured tank health is lumpy (gear tables step: the
    level-35 tank came out smaller than the level-30 one), and a reference that dips would make a level-35 heal
    rank smaller than a level-30 one, so the table follows the trend, not each point."""
    from combat.world_curve import growth
    xs = sorted(points)
    ys = [points[x] / growth(x) for x in xs]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    return {L: round((a + b * L) * growth(L), 1) for L in range(1, top + 1)}


def authored_lines():
    """The authored rank line per heal kind: the median, over every rank of every class heal, of its authored size
    over (1 + slope x (level - 1)) x its shape. combat/heal_formula.rank_size measures each spell against this to keep
    its character (a deliberately small or big heal stays a little small or big)."""
    import glob
    from combat import heal_formula as HF
    vals = {"heal": [], "hot": [], "heal_value": []}
    for fn in sorted(glob.glob(str(ROOT / "data/abilities/*.json"))):
        d = json.loads(Path(fn).read_text(encoding="utf-8"))
        rows = d.get("abilities", d) if isinstance(d, dict) else d
        if isinstance(rows, dict):
            rows = list(rows.values())
        for e in rows:
            if not isinstance(e, dict):
                continue
            et = e.get("effect_type")
            sh = HF.shape(e)
            for r in e.get("ranks") or []:
                lv = max(1, r.get("level_req", 1) or 1)
                line = 1 + HF.AUTHORED_SLOPE * (lv - 1)
                if et in ("heal", "hot") and r.get("effect_value"):
                    vals[et].append(r["effect_value"] / (line * sh))
                if r.get("heal_value"):
                    vals["heal_value"].append(r["heal_value"] / (line * sh))
    return {k: round(statistics.median(v), 2) for k, v in vals.items() if v}


def fill(points, top=60):
    """{level: value} at a few levels -> a value for every level 1..top, through the ratio to the world curve."""
    from combat.world_curve import growth
    lv = sorted(points)
    ratio = {L: points[L] / growth(L) for L in lv}
    out = {}
    for L in range(1, top + 1):
        if L <= lv[0]:
            r = ratio[lv[0]]
        elif L >= lv[-1]:
            r = ratio[lv[-1]]
        else:
            a = max(x for x in lv if x <= L)
            b = min(x for x in lv if x >= L)
            r = ratio[a] if a == b else ratio[a] + (ratio[b] - ratio[a]) * (L - a) / (b - a)
        out[L] = round(r * growth(L), 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--step", type=int, default=5)
    ap.add_argument("--refit", action="store_true", help="refit the table from the measured points already saved")
    args = ap.parse_args()
    if args.refit:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        m = data["measured"]
        data["tank"] = {str(k): v for k, v in fit({int(k): v for k, v in m["tank"].items()}).items()}
        data["healing_power"] = {str(k): v for k, v in fit({int(k): v for k, v in m["healing_power"].items()}).items()}
        data["authored"] = authored_lines()
        print("authored lines", data["authored"])
        OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"refit {OUT.relative_to(ROOT)}")
        return 0
    import sim_matrix as M
    from combat.abilities import _heal_power
    from entities.loot_generator import LootGenerator
    with quiet():
        gen = LootGenerator()
    levels = sorted({1, 60, *range(args.step, 60, args.step)})
    healers = [s for s, _ in M.specs_for(["healer"])]
    tank, power = {}, {}
    for L in levels:
        hp = []
        for seed in range(args.seeds):
            random.seed(1000 * L + seed)
            hp.append(M.build(TANK_SPEC, "tank", L, "geared", gen).health)
        tank[L] = statistics.mean(hp)
        pw = []
        random.seed(L)
        for spec in healers:
            try:
                pw.append(_heal_power(M.build(spec, "healer", L, "geared", gen)))
            except Exception:                                   # noqa: BLE001
                continue
        power[L] = statistics.median(pw) if pw else 0.0
        print(f"  level {L:2d}: tank {tank[L]:7.0f} (seeds {min(hp)}-{max(hp)})   healing power {power[L]:6.1f}")
    data = {
        "_about": "T(L): a geared Protection Warrior's max health, and the median geared healer's healing power "
                  "(combat scale), by level. Written by tools/calibrate_heal_reference.py; read by "
                  "combat/heal_formula.py. See docs/heal_formula.md.",
        "measured": {"tank": {str(k): round(v, 1) for k, v in tank.items()},
                     "healing_power": {str(k): round(v, 1) for k, v in power.items()}},
        "tank": {str(k): v for k, v in fit(tank).items()},
        "healing_power": {str(k): v for k, v in fit({k: max(1.0, v) for k, v in power.items()}).items()},
        "authored": authored_lines(),
    }
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
