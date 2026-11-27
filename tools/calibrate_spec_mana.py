#!/usr/bin/env python3
"""Even every spec's mana to the same run-dry targets, not just its class's median.

    PYTHONPATH=. python3 tools/calibrate_spec_mana.py            # print turns to run dry, per spec and level
    PYTHONPATH=. python3 tools/calibrate_spec_mana.py --write    # also fold the correction into the "specs" table

Kyle, 27 Nov 2026: "Is this across all characters now and uniform from 1 to 60? Healers, dps etc. Ensure classes
like hunters and tinkerers (mana for skills) are also appropriate." tools/calibrate_mana_costs.py sizes costs per
CLASS (one row for its damage, one for its heals); a class whose specs spend very differently stays uneven inside
(Fire Mage ran dry in 6 turns at 40-60 against Arcane's 20, Elemental Shaman 19 against Enhancement 9).

MEASURES, geared, at 10-60:
  damage specs   the turns their real rotation (tools/sim_dps_parity.damage_per_turn) lasts from a full bar,
                 regen counted at the casting rate
  healer specs   casts of their biggest spammable heal (calibrate_mana_costs.main_spell), regen counted
and, with --write, multiplies each spec's existing factor by turns / target (damage 14, heals 12, Restoration
Shaman 10 - calibrate_mana_costs' targets), clamped to 0.4-3.0, into data/balance/mana_costs.json "specs", read by
combat/mana_economy.spec_factor on every cast. Run it twice: a spec's rotation can shift when its costs move.
"""
import argparse, contextlib, io, json, os, statistics, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "tools")); os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

LEVELS = [10, 20, 30, 40, 50, 60]
SAMPLES = 2
OUT = ROOT / "data/balance/mana_costs.json"


def measure():
    from calibrate_mana_costs import main_spell
    import sim_matrix as M, sim_dps_parity as P
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    gen = LootGenerator()
    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()
    out = {}
    for spec, role in M.specs_for(["dps", "healer"]):
        row = {}
        for lv in LEVELS:
            t = []
            for i in range(SAMPLES):
                try:
                    if role == "healer":
                        with contextlib.redirect_stdout(io.StringIO()):
                            c = M.build(spec, role, lv, "geared", gen)
                        a = main_spell(c, role) if getattr(c, "mana", 0) else None
                        if a is None:
                            break
                        net = a.talented_cost(c) - c.mana_per_turn(casting=True)
                        t.append(c.mana / net if net > 0 else 99.0)
                    else:
                        st = {}
                        with contextlib.redirect_stdout(io.StringIO()):
                            P.damage_per_turn(spec, lv, 20, gen, cm, fight_seed=i, gear_seed=100 + i, mana_stats=st)
                        if not st.get("pool") or not st.get("spent_per_turn"):
                            break
                        net = st["spent_per_turn"] - st["regen"]
                        t.append(st["pool"] / net if net > 0 else 99.0)
                except Exception:                                   # noqa: BLE001
                    break
            if t:
                row[lv] = statistics.mean(t)
        if row:
            out[spec] = (role, row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    data = measure()
    print(f"{'spec':<34}{'role':<7}" + "".join(f"{lv:>7}" for lv in LEVELS))
    for spec, (role, row) in sorted(data.items()):
        print(f"{spec:<34}{role:<7}" + "".join(f"{(round(row[lv], 1) if lv in row else '-'):>7}" for lv in LEVELS))
    if not args.write:
        return 0
    doc = json.loads(OUT.read_text(encoding="utf-8"))
    specs = doc.setdefault("specs", {})
    for spec, (role, row) in data.items():
        kind = "heal" if role == "healer" else "damage"
        target = (10 if spec == "shaman_restoration" else 12) if kind == "heal" else 14
        old = dict((lv, f) for lv, f in (specs.get(spec, {}).get(kind) or []))
        pts = []
        for lv in LEVELS:
            if lv not in row:
                continue
            f = old.get(lv, 1.0) * row[lv] / target
            pts.append([lv, round(max(0.4, min(3.0, f)), 3)])
        if pts:
            specs.setdefault(spec, {})[kind] = pts
    doc["_specs_about"] = ("Per-spec mana cost factor by level, on top of the class rows: tools/calibrate_spec_mana.py, "
                           "read by combat/mana_economy.spec_factor. Damage specs run dry in ~14 turns of their "
                           "rotation, healers in ~12 casts of their main heal (Restoration Shaman 10).")
    OUT.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
