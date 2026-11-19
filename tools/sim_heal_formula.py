#!/usr/bin/env python3
"""What one heal does, next to what a tank has and what hits it: the numbers the heal formula is written against.

    PYTHONPATH=. python3 tools/sim_heal_formula.py [--levels 20,40,60] [--class Priest] [--casts 30] [--json out.json]

Kyle, 16 Nov 2026: "we need to fix the healing end game.....we need an actual formula and do it right.... a spot
heal from a non-spec'd character shouldn't heal 80% tank HP and like 200% boss damage...."

tools/sim_heal_parity.py measures throughput between healers; this measures the SIZE of one heal against the
fight it's in. Per level:

  THE TANK     T(L) from data/balance/heal_reference.json (a geared Protection Warrior, averaged over gear rolls);
               the one built here is shown too
  THE HITS     what one action does to the geared tank, averaged: a normal monster of the level, and every dungeon
               boss within two levels (its whole kit, so big hits and spreads count), through take_damage
  THE HEALS    every healer spec's strongest single-target heal, one cast at a time onto a wounded target, crits
               and variance in (the average of CASTS casts), two ways:
                 bare   no talents, no gear: what any character of the class gets for training the spell
                 built  talents spent for healing, geared at its level
               and the parts of it: the rank's base (after the rank curve), what healing power adds, and the rest
               (spec aura, talents, crit)

Mana is refilled each cast: this is the size of a heal, not how long it lasts.
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

HEAL_TYPES = {"heal"}
TANK_SPEC = "warrior_protection"


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def boss_names(cm, level, spread=2):
    out = []
    for name, d in cm.creatures.items():
        if not d.get("is_boss"):
            continue
        lo, hi = (d.get("level_range") or [0, 0])[:2]
        if lo - spread <= level <= hi + spread:
            out.append(name)
    return sorted(out)


def hits_on(tank, cm, names, level, actions=24, location_type=None):
    """Average damage one monster action does to the tank, per monster name. location_type: where it stands (an
    open-world rare is measured as the field boss it would be in a cave, tools/calibrate_boss_damage.py)."""
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    out = {}
    for name in names:
        with quiet():
            try:
                foe = cm.spawn_creature(name, level=level)
            except Exception:                                   # noqa: BLE001
                continue
            if foe is None:
                continue
            if location_type:
                from world.difficulty import apply_health
                foe.location_type = location_type
                apply_health(foe)
            engine = CombatEngine(tank, foe, party=Party(tank))
        taken = []
        for _ in range(actions):
            tank.current_health = tank.health
            for fx in list(tank._effects()):
                if getattr(fx, "absorb", 0):
                    fx.absorb = 0
            foe.current_health = foe.health
            before = tank.current_health
            with quiet():
                engine.current_actor = foe
                engine.combat_phase = "action"
                try:
                    engine.execute_monster_action()
                except Exception:                               # noqa: BLE001
                    break
            taken.append(max(0, before - tank.current_health))
        if taken:
            out[name] = statistics.mean(taken)
    return out


def heal_casts(char, ability, casts):
    """Average of `casts` casts of this heal onto the caster, held low; crits and variance in."""
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from entities.monster import Monster  # noqa: F401
    landed = []
    orig = char.heal

    def counted(amount, *a, **k):
        landed[-1] += max(0, amount or 0)
        return orig(amount, *a, **k)
    char.heal = counted
    try:
        import sim_matrix as M
        cm = _CM[0]
        with quiet():
            foe = cm.spawn_creature(sorted(M.pool(cm, char.level))[0], level=char.level)
            engine = CombatEngine(char, foe, party=Party(char))
        for _ in range(casts):
            char.current_mana = getattr(char, "mana", 0) or 0
            char.current_health = max(1, int(char.health * 0.05))
            ability.current_cooldown = 0
            landed.append(0)
            with quiet():
                engine.current_actor = char
                engine.combat_phase = "action"
                ok, _ = engine.execute_ability(char, ability.ability_id, char)
                if engine.current_actor is char:
                    engine._end_turn(char)
            if not ok:
                landed.pop()
            ability.current_cooldown = 0
    finally:
        char.heal = orig
    return statistics.mean(landed) if landed else 0.0


_CM = [None]


def parts(char, ability):
    from combat.abilities import _heal_power, _scaling_coef
    base = ability.effect_value or 0
    hp = _heal_power(char)
    coef = _scaling_coef(ability, "heal", char)
    return base, hp * coef, hp, coef


def best_heal(char, casts):
    heals = [a for a in char.get_learned_abilities()
             if a.effect_type in HEAL_TYPES and getattr(a, "target_type", None) not in ("enemy", "enemy_aoe", "party")
             and getattr(a, "heal_scope", None) != "party" and (getattr(a, "cooldown", 0) or 0) <= 3]
    best = None
    for a in heals:
        v = heal_casts(char, a, casts)
        if best is None or v > best[1]:
            best = (a, v)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="20,40,60")
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--casts", type=int, default=30)
    ap.add_argument("--json")
    args = ap.parse_args()
    levels = [int(x) for x in args.levels.split(",")]

    import sim_matrix as M
    import sim_role_balance as R
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
        gen = LootGenerator()
    _CM[0] = cm
    specs = [s for s, _ in M.specs_for(["healer"], args.only_class)]
    rows = []
    for level in levels:
        random.seed(level)
        tank_g = M.build(TANK_SPEC, "tank", level, "geared", gen)
        tank_n = M.build(TANK_SPEC, "tank", level, "naked", gen)
        # T(L), the reference every share is against: the averaged table (combat/heal_formula.tank), not this one
        # gear roll (one roll's tank ran 3,255 to 4,382 at 60)
        from combat import heal_formula as HF
        T = HF.tank(level) or tank_g.health
        mobs = sorted(M.pool(cm, level))[:4]
        mob_hits = hits_on(tank_g, cm, mobs, level)
        boss_hits = hits_on(tank_g, cm, boss_names(cm, level), level)
        mob = statistics.mean(mob_hits.values()) if mob_hits else 0
        boss = statistics.median(boss_hits.values()) if boss_hits else 0
        print(f"\n== level {level}: T {T:.0f} (this roll: tank {tank_n.health} naked / {tank_g.health} geared);"
              f" a normal monster's action {mob:.0f}, a boss's (median of {len(boss_hits)}) {boss:.0f}")
        print(f"   {'spec':28s} {'heal':22s} {'bare':>6s} {'%tank':>6s} {'xboss':>6s}   "
              f"{'built':>6s} {'%tank':>6s} {'xboss':>6s}   base / power (hp x coef)")
        for spec in specs:
            R.SPEND_TALENTS = False
            try:
                bare = M.build(spec, "healer", level, "naked", gen)
            finally:
                R.SPEND_TALENTS = True
            built = M.build(spec, "healer", level, "geared", gen)
            b = best_heal(bare, args.casts)
            g = best_heal(built, args.casts)
            if not b or not g:
                print(f"   {spec:28s} no single-target heal")
                continue
            ba, bv = b
            ga, gv = g
            base, pw, hp, coef = parts(built, ga)
            row = dict(level=level, spec=spec, heal=ga.name, bare=round(bv), built=round(gv),
                       bare_pct_tank=bv / T, built_pct_tank=gv / T,
                       bare_x_boss=bv / boss if boss else None, built_x_boss=gv / boss if boss else None,
                       base=base, power=round(pw), healing_power=round(hp), coef=round(coef, 2),
                       tank_naked=tank_n.health, tank_geared=tank_g.health, T=T, mob_hit=round(mob),
                       boss_hit=round(boss), cast_speed=getattr(ga, "cast_speed", 1.0))
            rows.append(row)
            print(f"   {spec:28s} {ga.name[:22]:22s} {bv:6.0f} {bv / T:6.0%} "
                  f"{(bv / boss if boss else 0):6.1f}   {gv:6.0f} {gv / T:6.0%} "
                  f"{(gv / boss if boss else 0):6.1f}   {base} / {pw:.0f} ({hp:.0f} x {coef:.2f})")
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
