#!/usr/bin/env python3
"""Fit every open-world rare's own damage factor so no class is hard-countered and none walks through it.

    PYTHONPATH=. python3 tools/tune_rares.py [--fights 20] [--jobs 3] [--only NAME] [--write]

Kyle, 19 Nov 2026: "rares should be around 75-90% win rate... Some rares would fucking clap you so hard.... but most
were soloable." 20 Nov 2026, after the census found 36 rares one class won under 60% of the time (and 141 every class
won every time): "Fix that next."

Each rare is fought at its level by a geared, talented Protection Warrior, Holy Priest and Fire Mage (the levelling
run's three, tools/sim_campaign.py), `--fights` times each, with its damage scaled by a factor t (world/difficulty
.rare_tune, data/balance/rare_tune.json). The weakest of the three decides:

  too hard   the weakest wins under 75%: t steps down (0.85, 0.72, 0.6, 0.5) until it wins 75% or more
  too soft   all three win every fight and the weakest ends on more than 55% health: t steps up (1.15 ... 1.8)
             while the weakest still wins 80% or more, and stops once it ends under 45% health
  otherwise  t stays 1.0 and isn't written

Only damage moves: health sets how long a fight is, and the rare row (monster_difficulty.json) already sizes that.
Re-run after the rare row, a rare's kit, or a class's kit changes; --only refits one rare and keeps the rest.
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
os.environ["FRONTIER_RARE_TUNE"] = "off"

OUT = ROOT / "data/balance/rare_tune.json"
SPECS = (("warrior_protection", "tank"), ("priest_holy", "healer"), ("mage_fire", "dps"))
DOWN = (0.85, 0.72, 0.6, 0.5)
UP = (1.15, 1.3, 1.45, 1.6, 1.8)
FLOOR_WIN = 0.75          # the weakest class wins at least this often
SOFT_HP = 0.55            # everyone won every fight with more than this left: too soft
RAISE_WIN = 0.80          # a raise is kept only while the weakest still wins this often...
RAISE_HP = 0.45           # ...and stops once the weakest ends under this much health

_W = {}


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def _init():
    import pygame
    pygame.init()
    import sim_campaign as S
    from entities.loot_generator import LootGenerator
    from world import difficulty as D
    with quiet():
        _W["gen"] = LootGenerator()
        _W["world"] = S.World()
    D._RARE_TUNE = {}


def measure(name, zone, t, fights, seed):
    import sim_viability as V
    from world import difficulty as D
    w, gen = _W["world"], _W["gen"]
    D._RARE_TUNE = {name: t}
    lv = int(sum((w.cm.creatures[name].get("level_range") or [1, 1])[:2]) // 2)
    random.seed(seed)
    out = {}
    for spec, role in SPECS:
        wins, left = 0, []
        for _ in range(fights):
            with quiet():
                c = V.make(spec, role, lv, "geared", gen)
            foe = w.spawn(name, zone, level=lv)
            try:
                won, _d, _t, hp = V.fight([c], {id(c): role}, [foe])
            except Exception:                                   # noqa: BLE001
                won, hp = False, {}
            wins += won
            left.append(hp.get(c.name, 0.0) if won else 0.0)
        out[spec] = (round(wins / fights, 3), round(statistics.mean(left), 3))
    return lv, out


def weakest(res):
    return min(res.values(), key=lambda r: (r[0], r[1]))


def fit_one(args):
    name, zone, fights = args
    seed = abs(hash(name)) % 100000
    lv, base = measure(name, zone, 1.0, fights, seed)
    tried = {1.0: base}
    t = 1.0
    win, hp = weakest(base)
    if win < FLOOR_WIN:
        for cand in DOWN:
            _lv, r = measure(name, zone, cand, fights, seed)
            tried[cand] = r
            t = cand
            if weakest(r)[0] >= FLOOR_WIN:
                break
    elif all(r[0] == 1.0 for r in base.values()) and min(r[1] for r in base.values()) > SOFT_HP:
        for cand in UP:
            _lv, r = measure(name, zone, cand, fights, seed)
            tried[cand] = r
            if weakest(r)[0] < RAISE_WIN:
                break
            t = cand
            if weakest(r)[1] < RAISE_HP:
                break
    return name, {"level": lv, "t": t, "tried": {str(k): v for k, v in tried.items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=20)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    _init()
    rares = {}
    for name, zone, _sz in _W["world"].rares:
        rares.setdefault(name, zone)                   # a rare in two subzones is one creature, fitted once
    if args.only:
        rares = {k: v for k, v in rares.items() if k == args.only}
    jobs = [(n, z, args.fights) for n, z in sorted(rares.items())]
    print(f"{len(jobs)} rares, {args.fights} fights a class at each step", flush=True)
    if args.jobs > 1 and len(jobs) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(args.jobs) as pool:
            results = []
            for i, r in enumerate(pool.imap_unordered(fit_one, jobs)):
                results.append(r)
                if r[1]["t"] != 1.0:
                    print(f"  [{i + 1}/{len(jobs)}] {r[0]}: x{r[1]['t']}", flush=True)
    else:
        results = [fit_one(j) for j in jobs]
    fitted = dict(results)
    if len(fitted) <= 3:
        for n, m in fitted.items():
            print(f"  {n} (level {m['level']}): x{m['t']}")
            for t, r in m["tried"].items():
                print(f"    x{t}: " + "  ".join(f"{s.split('_')[0]} {w:.0%} won, {h:.0%} left" for s, (w, h) in r.items()))
    old = json.loads(OUT.read_text(encoding="utf-8")) if (OUT.exists() and args.only) else {}
    measured = {**(old.get("measured") or {}), **fitted}
    tune = {n: m["t"] for n, m in sorted(measured.items()) if m["t"] != 1.0}
    down = sum(1 for v in tune.values() if v < 1)
    up = sum(1 for v in tune.values() if v > 1)
    print(f"{len(measured)} rares: {down} softened, {up} sharpened, {len(measured) - down - up} left as they were")
    if args.write:
        data = {
            "_about": "Per-rare damage factor on top of the rare row and boss_damage.json, fitted so the weakest of a "
                      "Protection Warrior, a Holy Priest and a Fire Mage wins 75% or more and nobody walks through it. "
                      "Written by tools/tune_rares.py; read by world/difficulty.rare_tune.",
            "rule": {"specs": [s for s, _r in SPECS], "floor_win": FLOOR_WIN, "soft_hp": SOFT_HP,
                     "raise_win": RAISE_WIN, "raise_hp": RAISE_HP, "down": DOWN, "up": UP, "fights": args.fights},
            "rares": tune,
            "measured": measured,
        }
        OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
