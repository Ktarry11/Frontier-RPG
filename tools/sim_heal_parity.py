#!/usr/bin/env python3
"""Sustained healing per turn of every healer spec, the same way, so healers sit near each other.

    PYTHONPATH=. python3 tools/sim_heal_parity.py [--levels 20,40,60] [--turns 30] [--passes 7] [--class Priest]
                                                  [--seed 1] [--json out.json]

The healer twin of tools/sim_dps_parity.py (Kyle, 15 Nov 2026: classes "not wildly different", "within ~10%").
Every healer spec, built geared with its talents (tools/sim_matrix.build), casts its own heal rotation for TURNS
turns onto a target held at 30% health - itself, so its HoTs tick at the end of its own turn through the engine's
turn end, regen and the five-second rule included. What lands is counted: the direct heal plus every tick.

ITS MANA IS REFILLED EACH TURN. This measures what a healer puts out when it heals, and the mana economy is
measured separately (tools/sim_matrix.py --endurance-only, ~20 turns of the main heal by design). Without the
refill a cheaper-healing spec would read as stronger here simply for lasting longer.

The rotation: the strongest heal that works, with HoTs kept rolling (a HoT already ticking on the target is not
recast), the same shape as sim_class_balance.plan's heal list.
"""
import argparse
import contextlib
import io
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

BAND = 0.10
HEALS = {"heal", "hot", "damage_and_heal"}

#: Damage dealers that heal, and the share of a dedicated healer's output they're held to. Kyle, 15 Nov 2026:
#: "For groovekeeper since it's a dps Healer bring it to 75% of Healer (cryotherapist should be around 75% too)".
#: Cryotherapist is the healing path inside the Frost Mage tree - its Frostbolt and Ice Lance heal the neediest ally
#: as they hit - so it is measured FIGHTING: its damage rotation into the target, the healing it spills counted.
HYBRID_HEALERS = {"primalist_grovekeeper": 0.75, "mage_frost": 0.75}
HEALS_BY_FIGHTING = {"mage_frost"}


def healer_specs(only_class=None):
    """Every healer spec, plus the damage dealers that heal (HYBRID_HEALERS)."""
    import sim_matrix as M
    import sim_role_balance as R
    specs = [s for s, _ in M.specs_for(["healer"], only_class)]
    for s in HEALS_BY_FIGHTING:
        if s not in specs and (not only_class or R.class_of(s).lower() == only_class.lower()):
            specs.append(s)
    return sorted(specs)


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def healing_per_turn(spec, level, turns, gen, cm, fight_seed=0, gear_seed=0):
    import sim_matrix as M
    import sim_role_balance as R
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    random.seed(gear_seed)
    char = M.build(spec, "healer", level, "geared", gen)
    with quiet():
        foe = cm.spawn_creature(sorted(M.pool(cm, level))[0], level=level)
        engine = CombatEngine(char, foe, party=Party(char))
        R.precast_stances(char, engine)
    random.seed(fight_seed)
    learned = char.get_learned_abilities()
    # COUNT EVERY HEAL IN FULL, overheal included. The target sits at 30%, so measuring the health bar caps a
    # turn at 70% of it - and once the world curve (15 Nov) made heals world-sized, every healer hit that cap
    # and read the same. heal() is where every heal, tick and smart-heal lands.
    landed = [0.0]
    _orig_heal = char.heal

    def counted_heal(amount, *a, **k):
        landed[0] += max(0, amount or 0)
        return _orig_heal(amount, *a, **k)
    char.heal = counted_heal
    if spec in HEALS_BY_FIGHTING:
        # heals by fighting: its damage rotation goes into the target, and what it heals the target-at-30% for counts
        from tools.sim_class_balance import plan
        _h, attacks, _s, _d = plan(char)
        # it fights with what heals: the converted nukes and the damage-and-heal spells lead (a raw-value sort put
        # Fireball, which heals nothing, ahead of Frostbolt)
        attacks = sorted(attacks, key=lambda a: 0 if (getattr(a, "cryo_converted", False)
                                                       or a.effect_type == "damage_and_heal") else 1)
        foe.max_health = foe.current_health = 10 ** 8

        for _ in range(turns):
            char.current_mana = char.mana
            char.current_health = max(1, int(char.health * 0.3))
            with quiet():
                for a in attacks:
                    engine.current_actor = char
                    engine.combat_phase = "action"
                    ok, _ = engine.execute_ability(char, a.ability_id, foe)
                    if ok:
                        break
                if engine.current_actor is char:
                    engine._end_turn(char)
        return landed[0] / turns
    heals = [a for a in learned if a.effect_type in HEALS and getattr(a, "target_type", None) != "enemy"]
    heals.sort(key=lambda a: -((getattr(a, "heal_value", 0) or 0) or (a.effect_value or 0)))
    for _ in range(turns):
        char.current_mana = char.mana
        char.current_health = max(1, int(char.health * 0.3))
        live = {getattr(fx, "effect_id", None) for fx in char._effects()}
        with quiet():
            for a in heals:
                if a.effect_type == "hot" and a.ability_id in live:
                    continue
                engine.current_actor = char
                engine.combat_phase = "action"
                ok, _ = engine.execute_ability(char, a.ability_id, char)
                if ok:
                    break
            if engine.current_actor is char:
                engine._end_turn(char)
    return landed[0] / turns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="20,40,60")
    ap.add_argument("--turns", type=int, default=30)
    ap.add_argument("--passes", type=int, default=7)
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json")
    args = ap.parse_args()
    import sim_matrix as M
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
    specs = healer_specs(args.only_class)
    levels = [int(x) for x in args.levels.split(",")]
    table = {}
    for lv in levels:
        for spec in specs:
            vals = []
            for p in range(args.passes):
                try:
                    vals.append(healing_per_turn(spec, lv, args.turns, LootGenerator(), cm,
                                                 fight_seed=hash((args.seed, "f", spec, lv, p)) & 0xFFFFFFFF,
                                                 gear_seed=hash((args.seed, "g", spec, lv, p)) & 0xFFFFFFFF))
                except Exception as e:                          # noqa: BLE001
                    print(f"  {spec} L{lv}: {type(e).__name__}: {e}")
                    break
            if vals:
                mean = statistics.mean(vals)
                se = (statistics.stdev(vals) / len(vals) ** 0.5 / mean) if len(vals) > 1 and mean else 0
                table[(spec, lv)] = (mean, se)
    # the median of DEDICATED healers; a hybrid is judged against its own share of it (HYBRID_HEALERS)
    medians = {}
    for lv in levels:
        pure = [v[0] for (s, l), v in table.items() if l == lv and s not in HYBRID_HEALERS]
        # a one-class run may hold no dedicated healer (--class Mage): judge against its own spread then
        medians[lv] = statistics.median(pure or [v[0] for (s, l), v in table.items() if l == lv] or [1])
    print(f"\n{'spec':<30}" + "".join(f"{'L' + str(lv):>16}" for lv in levels))
    print(f"{'(median of all healers)':<30}" + "".join(f"{medians[lv]:>16.0f}" for lv in levels))
    out = 0
    for spec in specs:
        cells = []
        for lv in levels:
            if (spec, lv) not in table:
                cells.append(f"{'-':>16}")
                continue
            m, se = table[(spec, lv)]
            r = m / (medians[lv] * HYBRID_HEALERS.get(spec, 1.0)) if medians[lv] else 0
            bad = abs(r - 1) > BAND
            out += bad
            cells.append(f"{m:>7.0f} {r:>5.2f}{'~' if se > 0.05 else ' '}{'!' if bad else ' '}")
        print(f"{spec:<30}" + "".join(cells))
    print(f"\n{out} spec-levels outside +/-{BAND:.0%} of the median")
    if args.json:
        import json
        Path(args.json).write_text(json.dumps({f"{s}|{lv}": v for (s, lv), v in table.items()}), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
