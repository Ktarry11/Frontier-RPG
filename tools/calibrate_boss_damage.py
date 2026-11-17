#!/usr/bin/env python3
"""Write data/balance/boss_damage.json: every boss's damage, put on the healing formula's reference.

    PYTHONPATH=. python3 tools/calibrate_boss_damage.py [--actions 24] [--only NAME]

The healing formula (docs/heal_formula.md, combat/heal_formula.py) sizes heals as shares of T(L), a geared tank's
health. Kyle, 16 Nov 2026: "Yes that's fine to drop bosses a bit to account for it". Before, an average dungeon boss
action at 60 did about three quarters of T and the Plaguelands' last bosses more than all of it, so a heal sized to
the tank could never keep up.

Per boss, at the middle of its level range, against a geared Protection Warrior of that level: the average damage of
one action (its whole kit, through take_damage), with this file's own factors switched off
(FRONTIER_BOSS_DAMAGE=off). Its factor puts that average at:

    TARGET[kind] x T(L) x clamp((its average / the median boss of its level) ^ KEEP, *SPREAD)

  kind     boss (a five-player dungeon's) and tuned_boss 0.35, a run's last boss 0.45, field_boss (the named one in a small cave or the
           open) 0.25. Hidden layers and skull zones aren't touched: brutal on purpose, and qa_hidden_zones holds
           them to their rows
  KEEP     how much of a boss's own weight survives: a boss that hit harder than its peers still hits a bit harder
           (the Baron and Hale stay the hard ones), a soft one a bit softer, but nothing is 3x its peers
  the parts of an average: a normal hit ~20-25%, a big hit 40-45%, a spread 10-12% on each of five

world/difficulty.factor reads it for "damage". Rerun after a boss kit or the reference changes.
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

os.environ["FRONTIER_BOSS_DAMAGE"] = "off"
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

OUT = ROOT / "data/balance/boss_damage.json"
TARGET = {"boss": 0.35, "tuned_boss": 0.35, "field_boss": 0.25}
#: hidden layers and skull zones keep their own rows (world/difficulty.BOSS_DAMAGE_KINDS): brutal on purpose
KEEP = 0.4
#: a run's LAST boss (the one that always drops its T0 token, data/items/set_tokens.json) hits harder: the first sim
#: with every boss at 0.28 had parties of five beating Gandling, the Baron and Hale with four or five still standing,
#: and Kyle wants the end of a run to need the group ("end game has no challenge"). Second pass the same night, at
#: 0.30 / 0.36: still four or five standing at every late boss, so 0.35 for a boss (about a specced normal heal an
#: action, so one healer just keeps pace) and 0.45 for a run's last (more than one healer can put out alone)
FINAL = 0.45
#: bosses only come DOWN (Kyle: "drop bosses a bit"): one already under its target keeps what it hits for
MAX_FACTOR = 1.0
SPREAD = (0.75, 1.35)
BAND = 4            # the "median boss of its level" is the median of every boss within this many levels


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--actions", type=int, default=24)
    ap.add_argument("--only")
    ap.add_argument("--refit", action="store_true", help="recompute the factors from the saved measurements")
    args = ap.parse_args()
    if args.refit:
        data = json.loads(OUT.read_text(encoding="utf-8"))
        data["bosses"] = fit(data["measured"])
        data.update(targets=TARGET, keep=KEEP, spread=list(SPREAD), max_factor=MAX_FACTOR)
        OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"refit {len(data['bosses'])} bosses")
        return 0
    import sim_heal_formula as F
    import sim_matrix as M
    from combat import heal_formula as HF
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    from world import difficulty as D
    with quiet():
        cm = CreatureManager()
        gen = LootGenerator()
    F._CM[0] = cm
    bosses = sorted(n for n, d in cm.creatures.items() if d.get("is_boss"))
    if args.only:
        bosses = [b for b in bosses if b == args.only]
    tanks = {}
    measured = {}
    for i, name in enumerate(bosses):
        lo, hi = (cm.creatures[name].get("level_range") or [1, 1])[:2]
        L = max(1, min(60, (lo + hi) // 2))
        if L not in tanks:
            random.seed(7000 + L)
            tanks[L] = M.build("warrior_protection", "tank", L, "geared", gen)
        with quiet():
            try:
                probe = cm.spawn_creature(name, level=L)
            except Exception:                                   # noqa: BLE001
                continue
        if probe is None:
            continue
        kind = D.kind_of(probe)
        avg = F.hits_on(tanks[L], cm, [name], L, actions=args.actions).get(name)
        if not avg:
            continue
        measured[name] = {"level": L, "kind": kind, "avg": round(avg, 1), "share": round(avg / HF.tank(L), 3)}
        if i % 50 == 0:
            print(f"  {i}/{len(bosses)} {name}: level {L} {kind} {avg:.0f} = {avg / HF.tank(L):.0%} of T")
    old = json.loads(OUT.read_text(encoding="utf-8")) if (OUT.exists() and args.only) else {}
    measured = {**(old.get("measured") or {}), **measured}
    factors = fit(measured)
    data = {
        "_about": "Per-boss damage factor putting a boss's average action at a share of T(L), the healing formula's "
                  "reference tank. Written by tools/calibrate_boss_damage.py; read by world/difficulty.factor.",
        "targets": TARGET, "keep": KEEP, "spread": list(SPREAD), "max_factor": MAX_FACTOR,
        "bosses": factors, "measured": measured,
    }
    OUT.write_text(json.dumps(data, indent=1, sort_keys=False), encoding="utf-8")
    shares = sorted(m["share"] for m in measured.values())
    print(f"{len(factors)} bosses. Before: median action {statistics.median(shares):.0%} of T "
          f"(10th {shares[len(shares) // 10]:.0%}, 90th {shares[9 * len(shares) // 10]:.0%}). Wrote {OUT.relative_to(ROOT)}")


def finals():
    try:
        T = json.loads((ROOT / "data/items/set_tokens.json").read_text(encoding="utf-8"))
        return {n for n, b in (T.get("bosses") or {}).items() if b.get("guaranteed")}
    except (OSError, ValueError):
        return set()


def fit(measured):
    factors = {}
    for name, m in measured.items():
        if m["kind"] not in TARGET:
            continue
        peers = [x["share"] for x in measured.values() if abs(x["level"] - m["level"]) <= BAND and x["kind"] in TARGET]
        med = statistics.median(peers) if peers else m["share"]
        rel = max(SPREAD[0], min(SPREAD[1], (m["share"] / med) ** KEEP)) if med > 0 else 1.0
        base = FINAL if name in finals() else TARGET.get(m["kind"], 0.30)
        want = base * rel
        factors[name] = round(min(MAX_FACTOR, want / m["share"]), 3) if m["share"] > 0 else 1.0
        m["target"] = round(want, 3)
    return factors


if __name__ == "__main__":
    sys.exit(main())
