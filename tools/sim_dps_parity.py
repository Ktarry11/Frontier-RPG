#!/usr/bin/env python3
"""Sustained damage per turn of every damage spec, on the same target, at the same level and gear.

    PYTHONPATH=. python3 tools/sim_dps_parity.py [--levels 20,40,60] [--turns 15] [--passes 3] [--class Mage]

Kyle, 15 Nov 2026: "Each class should bring something unique. But I don't want classes to be wildly different.
Like a balance druid spamming wrath or starfire shouldn't absolutely blow past an elemental shaman spamming
lightning bolt or a stormbringer spamming shock." He picked: damage specs within ~10% of each other; uniqueness
comes from utility, procs, AoE, DoTs and cooldowns.

The measurement: every damage spec built geared with its talents (tools/sim_matrix.build), its stances up, then
TURNS of its own rotation (sim_class_balance.plan: the hardest-hitting thing that works, cooldowns, resources and
forms enforced by the engine) into the SAME real creature at the same level - a huge health pool, and it never
acts, so the number is damage dealt and nothing else. Repeated --passes times; the median is reported, with a
"~" where the standard error of that mean is above 5% (a re-run would likely move it).

It prints each spec's damage per turn as a ratio of the median across all specs at that level, and flags
anything outside the +/-10% band.
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


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def target_name(cm, level):
    import sim_matrix as M
    return sorted(M.pool(cm, level))[0]


def damage_per_turn(spec, level, turns, gen, cm, fight_seed=0, gear_seed=0):
    import sim_matrix as M
    import sim_role_balance as R
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from tools.sim_class_balance import plan
    # NEW GEAR EVERY PASS, AVERAGED. Rolled gear swings a spec's damage a lot (Destruction at 60 read 846, 705
    # and 473 on three different sets), so one fixed set measures that set. Each pass rolls its own gear and
    # its own dice, the mean is reported, and --seed runs the whole thing again independently to check it.
    random.seed(gear_seed)
    char = M.build(spec, "dps", level, "geared", gen)
    with quiet():
        foe = cm.spawn_creature(target_name(cm, level), level=level)
    random.seed(fight_seed)
    foe.max_health = foe.current_health = 10 ** 8
    with quiet():
        engine = CombatEngine(char, foe, party=Party(char))
        R.precast_stances(char, engine)
    _h, attacks, _s, _d = plan(char)
    # A melee spec swings rather than shooting: the universal Shoot and Wand out-sort its rage builders on raw
    # value, and a rage class that shoots never builds rage (Knight of Xoroth fired Shoot 75 times in 90 turns).
    if M.real_role(spec, "dps") == "melee_dps":
        attacks = [a for a in attacks if not getattr(a, "requires_ranged_weapon", None)]
    # A SHAPESHIFTED SPEC FIGHTS IN ITS FORM. A caster spell ranks above Shred on raw value, and casting it drops
    # Cat Form - the Feral then spent the fight as a caster casting Wrath. In a form: only what that form uses.
    form = getattr(char, "current_form", None)
    if form:
        def in_form(a):
            rf = getattr(a, "requires_form", None)
            rf = rf if isinstance(rf, (list, tuple)) else ([rf] if rf else [])
            return form in rf or a.ability_id.endswith("_attack")
        attacks = [a for a in attacks if in_form(a)] or attacks
    start = foe.current_health
    # THE ENGINE'S OWN LOOP, so pets take their turns and DoTs tick on the target's. The target's turn is
    # ended without it acting: the number is damage dealt and nothing else.
    done = 0
    for _ in range(40000):
        with quiet():
            engine.update(0.25)
        if not engine.is_active:
            break
        actor = engine.current_actor
        if actor is None:
            continue
        if actor is foe:
            # THE TARGET HITS BACK, and the hit is then undone: rage builds from being struck, traps trigger,
            # "when struck" procs fire - a dummy that never acts read every trap as 0 damage - and the character
            # is put back to full, so the number is still damage dealt and nothing else.
            with quiet():
                engine.execute_monster_action()
            char.current_health = char.health
            continue
        if actor is not char:
            with quiet():
                if hasattr(engine, "execute_pet_action"):
                    engine.execute_pet_action()
                else:
                    engine._end_turn(actor)
            continue
        if done >= turns:
            break
        done += 1
        acted = False
        with quiet():
            for a in attacks:
                ok, _ = engine.execute_ability(char, a.ability_id, foe)
                if ok:
                    acted = True
                    break
            if not acted:
                engine.execute_defend(char)
    return (start - foe.current_health) / turns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="20,40,60")
    ap.add_argument("--turns", type=int, default=30)
    ap.add_argument("--passes", type=int, default=7)
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--seed", type=int, default=1, help="run again with another seed to check the result holds")
    ap.add_argument("--json", help="write {spec: {level: [mean, se]}} here")
    args = ap.parse_args()
    import sim_matrix as M
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
    specs = [s for s, r in M.specs_for(["dps"], args.only_class)]
    levels = [int(x) for x in args.levels.split(",")]
    table = {}
    for lv in levels:
        for spec in specs:
            vals = []
            for p in range(args.passes):
                try:
                    vals.append(damage_per_turn(spec, lv, args.turns, LootGenerator(), cm,
                                                fight_seed=hash((args.seed, "fight", spec, lv, p)) & 0xFFFFFFFF,
                                                gear_seed=hash((args.seed, "gear", spec, lv, p)) & 0xFFFFFFFF))
                except Exception as e:                          # noqa: BLE001
                    print(f"  {spec} L{lv}: {type(e).__name__}: {e}")
                    break
            if vals:
                mean = statistics.mean(vals)
                # standard error of the mean, as a share of it: how far another run would likely land
                se = (statistics.stdev(vals) / len(vals) ** 0.5 / mean) if len(vals) > 1 and mean else 0
                table[(spec, lv)] = (mean, se)
    print(f"\n{'spec':<30}" + "".join(f"{'L' + str(lv):>16}" for lv in levels))
    medians = {lv: statistics.median([v[0] for (s, l), v in table.items() if l == lv]) for lv in levels}
    print(f"{'(median of all specs)':<30}" + "".join(f"{medians[lv]:>16.0f}" for lv in levels))
    out = []
    for spec in specs:
        cells = []
        for lv in levels:
            if (spec, lv) not in table:
                cells.append(f"{'-':>16}")
                continue
            med, spread = table[(spec, lv)]
            ratio = med / medians[lv]
            flag = "!" if abs(ratio - 1) > BAND else " "
            if flag == "!":
                out.append((spec, lv, ratio))
            cells.append(f"{med:>7.0f} {ratio:>5.2f}{'~' if spread > 0.05 else ' '}{flag}")
        print(f"{spec:<30}" + "".join(cells))
    print(f"\n{len(out)} spec-levels outside +/-{BAND:.0%} of the median")
    if args.json:
        import json
        Path(args.json).write_text(json.dumps({f"{s}|{lv}": v for (s, lv), v in table.items()}), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
