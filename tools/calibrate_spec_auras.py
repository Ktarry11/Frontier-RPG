#!/usr/bin/env python3
"""Calibrate the hidden per-spec damage (or healing) aura so every spec sits near its peers.

    PYTHONPATH=. python3 tools/calibrate_spec_auras.py [--levels 10,20,30,40,50,60] [--passes 7] [--write]

Kyle, 15 Nov 2026: "I don't want classes to be wildly different. Like a balance druid spamming wrath or starfire
shouldn't absolutely blow past an elemental shaman spamming lightning bolt or a stormbringer spamming shock." He
picked: damage specs within ~10%; uniqueness from utility, procs, AoE, DoTs and cooldowns.

Measures every damage spec with the auras OFF through tools/sim_dps_parity.damage_per_turn (geared, talented,
30 turns of its own rotation into the same creature, new gear and dice each pass), then writes, per spec and
level, median / spec - clamped to combat/ability_scaling.AURA_RANGE. A spec clamped at either end is printed:
it is a broken kit to fix by hand (no combo points, a resource that never comes back...), and the aura only
narrows the gap until it is.
"""
import argparse
import contextlib
import io
import json
import os
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
OUT = ROOT / "data/balance/spec_auras.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="10,20,30,40,50,60")
    ap.add_argument("--passes", type=int, default=7)
    ap.add_argument("--turns", type=int, default=30)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--kind", default="damage", choices=("damage", "healing"),
                    help="damage specs (sim_dps_parity) or healer specs (sim_heal_parity)")
    args = ap.parse_args()
    from combat import ability_scaling as S
    S.USE_SPEC_AURAS = False
    import sim_matrix as M
    import sim_dps_parity as P
    import sim_heal_parity as H
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()
    levels = [int(x) for x in args.levels.split(",")]
    specs = [s for s, _ in M.specs_for(["dps" if args.kind == "damage" else "healer"])]
    measure = P.damage_per_turn if args.kind == "damage" else H.healing_per_turn
    dpt = {}
    for lv in levels:
        for spec in specs:
            vals = []
            for p in range(args.passes):
                try:
                    vals.append(measure(spec, lv, args.turns, LootGenerator(), cm,
                                                  fight_seed=hash(("aura", "fight", spec, lv, p)) & 0xFFFFFFFF,
                                                  gear_seed=hash(("aura", "gear", spec, lv, p)) & 0xFFFFFFFF))
                except Exception as e:                          # noqa: BLE001
                    print(f"  {spec} L{lv}: {type(e).__name__}: {e}", flush=True)
                    break
            if vals:
                dpt[(spec, lv)] = statistics.mean(vals)
        print(f"  level {lv} measured", flush=True)
    lo, hi = S.AURA_RANGE
    table, clamped = {}, []
    for lv in levels:
        med = statistics.median([v for (s, l), v in dpt.items() if l == lv])
        for spec in specs:
            v = dpt.get((spec, lv))
            if not v:
                continue
            raw = med / v
            f = max(lo, min(hi, raw))
            if f != raw:
                clamped.append((spec, lv, round(raw, 2)))
            table.setdefault(spec, []).append([lv, round(f, 3)])
    print(f"\n{'spec':<30}" + "".join(f"{'L' + str(lv):>7}" for lv in levels))
    for spec, pts in sorted(table.items()):
        d = dict(pts)
        print(f"{spec:<30}" + "".join(f"{d.get(lv, ''):>7}" for lv in levels))
    print(f"\nclamped (a kit to fix by hand): {len(clamped)}")
    for c in clamped:
        print("  ", c)
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
        old["_about"] = ("Hidden per-spec multipliers by level, written by tools/calibrate_spec_auras.py so damage "
                         "specs sit within ~10% of each other. Read by combat/ability_scaling.spec_aura.")
        old[args.kind] = table
        OUT.write_text(json.dumps(old, indent=1), encoding="utf-8")
        print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
