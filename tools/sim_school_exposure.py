#!/usr/bin/env python3
"""How hard do the world's school resistances hit each damage spec?

    PYTHONPATH=. python3 tools/sim_school_exposure.py [--levels 20,40,60] [--class Stormbringer] [--json out.json]

Deep dive (Kyle, 15 Nov 2026: "one last absolute deep dive. Aim for scenarios you didn't probe!"). 451 of 1,393
creatures resist Nature and 286 of them by 50+; Shadow, Arcane and Frost are close behind. Resistance is on a
flat scale: up to 30 below level 60 (37.5% off) and 60 at 60 (75% off - entities/character.py
RESIST_MAX_PRE_60 / resist_mitigation_from). A Mage switches school; a spec that is one school all the way down
cannot. Parity is measured against a neutral target (tools/sim_dps_parity.neutralize), so this is the missing half.

For every damage spec: its real rotation (sim_dps_parity.damage_per_turn, neutral target) with each hit's school
recorded -> its school mix. Then for every encounter table whose creatures sit within the level band, the damage
it keeps against that table's weighted creature mix, after each creature's resistance (clamped for the level).
Reported per spec: its school mix, the median table it keeps, and the WORST table. Tables are counted, never
named (hidden places stay hidden).
"""
import argparse
import collections
import contextlib
import io
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
SCHOOLS = ("fire", "frost", "nature", "shadow", "arcane", "holy", "magic")


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def school_mix(spec, level, gen, cm, seeds=2):
    import sim_dps_parity as P
    hits = collections.Counter()
    orig = P.neutralize

    def watching(cm_, lv, foe):
        orig(cm_, lv, foe)
        real = foe.take_damage

        def td(amount, damage_type="physical", *a, **k):
            got = real(amount, damage_type, *a, **k)
            hits[(damage_type or "physical").lower()] += max(0, got or 0)
            return got
        foe.take_damage = td
        return foe
    P.neutralize = watching
    try:
        for s in range(seeds):
            with quiet():
                P.damage_per_turn(spec, level, 12, gen, cm, fight_seed=s, gear_seed=50 + s)
    finally:
        P.neutralize = orig
    tot = sum(hits.values()) or 1
    return {k: v / tot for k, v in hits.items()}


def tables(cm, lo, hi):
    """Every encounter table (open zone and subzone) whose weighted creatures mostly sit in lo..hi."""
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    out = []
    for _zone, z in enc.items():
        groups = [z.get("open_zone") or {}] + list((z.get("subzones") or {}).values())
        for g in groups:
            cr = {n: w for n, w in (g.get("creatures") or {}).items() if w and n in cm.creatures}
            if not cr:
                continue
            lvls = [statistics.mean(cm.creatures[n].get("level_range") or [1, 1]) for n in cr]
            if lo <= statistics.median(lvls) <= hi:
                out.append(cr)
    return out


_SPAWNED = {}


def resist_of(cm, name, level, school):
    """A creature's resistance as SPAWNED: its template carries none of it - the six schools are filled in at
    spawn from its type and casting affinity (entities/monster.py), which is why reading the template saw none."""
    key = (name, level)
    if key not in _SPAWNED:
        with quiet():
            _SPAWNED[key] = cm.spawn_creature(name, level=level)
    return getattr(_SPAWNED[key], f"base_{school}_resist", 0) or 0


def kept(mix, table, cm, level):
    from entities.character import Character as C
    num = den = 0.0
    for name, w in table.items():
        keep = 0.0
        for school, share in mix.items():
            if school == "physical" or school not in SCHOOLS:
                keep += share
                continue
            r = C.clamp_resistance_for_level(int(resist_of(cm, name, level, school)), level)
            keep += share * (1 - C.resist_mitigation_from(r))
        num += w * keep
        den += w
    return num / den if den else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="20,40,60")
    ap.add_argument("--class", dest="only")
    ap.add_argument("--json")
    args = ap.parse_args()
    import sim_matrix as M
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
    gen = LootGenerator()
    random.seed(1)
    specs = [s for s, _r in M.specs_for(["dps"], only_class=args.only)]
    result = {}
    for lv in [int(x) for x in args.levels.split(",")]:
        tabs = tables(cm, lv - 7, lv + 2)
        print(f"\nLEVEL {lv}: {len(tabs)} encounter tables in band {lv - 7}-{lv + 2}")
        print(f"  {'spec':<30} {'school mix':<40} {'median kept':>11} {'worst kept':>10} {'tables <70%':>11}")
        rows = []
        for spec in specs:
            try:
                mix = school_mix(spec, lv, gen, cm)
            except Exception as e:                                       # noqa: BLE001
                print(f"  {spec}: {type(e).__name__}: {e}")
                continue
            ks = [kept(mix, t, cm, lv) for t in tabs] or [1.0]
            med, worst = statistics.median(ks), min(ks)
            bad = sum(k < 0.70 for k in ks)
            top = ", ".join(f"{k} {v:.0%}" for k, v in sorted(mix.items(), key=lambda kv: -kv[1])[:3])
            rows.append((med, spec, top, worst, bad, len(ks)))
            result.setdefault(spec, {})[lv] = {"mix": mix, "median_kept": med, "worst_kept": worst,
                                              "tables_below_70": bad, "tables": len(ks)}
        for med, spec, top, worst, bad, n in sorted(rows):
            flag = "  !" if worst < 0.55 or bad > n * 0.15 else ""
            print(f"  {spec:<30} {top:<40} {med:>10.0%} {worst:>10.0%} {bad:>5}/{n:<5}{flag}")
    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
