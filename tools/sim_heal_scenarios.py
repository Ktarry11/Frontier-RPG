#!/usr/bin/env python3
"""Can each healer keep a real party alive - judged on what that healer is built for?

    PYTHONPATH=. python3 tools/sim_heal_scenarios.py [--levels 30,50] [--class Priest] [--seeds 2] [--json out.json]

Kyle, 15 Nov 2026: "We need to account for things like st, hots, aoe heals, cleave heals. Ensure that we take into
account specific healers having specific roles. We can't call a disc priest (bubble priest) weaker than holy if their
spells do less healing by discounting shields ... or a restore shaman and earth shield etc." and "long cast, lower
cost, high heal vs lower heal, faster cast, higher cost ... ensure that they have their places in combat".

tools/sim_heal_parity.py measures one thing - single-target throughput on yourself with nothing hitting you - which
flatters a big single-target heal and hides party heals, chain heals, HoTs rolling on several people, shields that
soak a hit, and heals that fire when someone is struck (Earth Shield). This puts the healer in a party of five under
real damage and lets it play its own kit:

  THE PARTY   the healer under test + Protection Warrior, Fire Mage, Combat Rogue, Marksmanship Hunter, built at the
              same level (tools/sim_matrix.build: talents, spec gear, stances, buffs).
  DAMAGE      per round, a share of each target's max health, x INTENSITY, through take_damage (so shields soak it
              and on-hit procs fire):
                tank    the tank takes 20%
                aoe     everyone takes 7%
                mixed   the tank 12%, everyone 3.5%
                spike   the tank takes 45% every third round, nothing between
  TIME        a round is one turn of time. The healer acts by its spells' cast speed (combat/abilities.CAST_SPEEDS):
              a quick heal spends 0.6 of a turn, a slow one 1.5, so quick healers act more often and slow ones less.
  MANA        real: nothing refills it. The five-second rule and regen run as in a fight.
  THE HEALER  1. anyone under 40%: the fastest big heal on them (a quick heal if it has one)
              2. three or more under 75% and a party/chain heal ready: that
              3. keep its shields, HoTs and Earth-Shield-style buffs on the tank
              4. anyone under 85%: the most efficient heal that will not overheal much
              5. nobody hurt: wait (regen; the five-second rule rewards it)
  SCORE       the highest INTENSITY the party survives 20 rounds at with nobody dying (binary search, every seed must
              survive). Reported per pattern and as a geometric mean. Healers SHOULD differ by pattern; none should
              fail one outright, and the overall should sit within ~10% of the median.
"""
import argparse
import contextlib
import io
import json
import math
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

ROUNDS = 20
PATTERNS = {
    "tank": lambda r: {"tank": 0.20},
    "aoe": lambda r: {"all": 0.07},
    "mixed": lambda r: {"tank": 0.12, "all": 0.035},
    "spike": lambda r: {"tank": 0.45} if r % 3 == 2 else {},
}
PARTY = [("tank", "warrior_protection"), ("dps", "mage_fire"), ("dps", "rogue_combat"),
         ("dps", "hunter_marksmanship")]
HEAL_TYPES = {"heal", "hot", "damage_and_heal"}


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def kit(healer):
    """The healer's tools, sorted into roles."""
    single, party, hots, shields, keepers = [], [], [], [], []
    for a in healer.get_learned_abilities():
        tt = getattr(a, "target_type", None)
        if (getattr(a, "absorb_pct_max_health", 0) or 0) > 0 and tt in (None, "self", "ally", "party"):
            shields.append(a)
        elif a.effect_type == "hot":
            (party if tt == "party" else hots).append(a)
        elif a.effect_type in HEAL_TYPES and tt != "enemy" and (a.cooldown or 0) < 10:
            (party if tt == "party" or getattr(a, "heal_scope", None) == "party" else single).append(a)
        elif a.effect_type == "buff" and tt == "ally" and (getattr(a, "proc", None) or {}):
            keepers.append(a)          # Earth Shield and its kind: a buff on an ally that heals when struck
    return single, party, hots, shields, keepers


def est(a, healer):
    """What a cast heals, near enough: the rank's value plus healing power x the coefficient."""
    from combat.abilities import _heal_power, _scaling_coef
    kind = "hot" if a.effect_type == "hot" else "heal"
    v = (getattr(a, "heal_value", 0) or 0) or (a.effect_value or 0)
    return v + _heal_power(healer) * _scaling_coef(a, kind, healer)


def ready(a, healer):
    try:
        return (a.turns_remaining or 0) <= 0 and a.can_afford(healer) if hasattr(a, "can_afford") else (a.turns_remaining or 0) <= 0
    except Exception:                                           # noqa: BLE001
        return (a.turns_remaining or 0) <= 0


def has_effect(target, aid):
    return any(getattr(fx, "effect_id", None) == aid for fx in target._effects())


def choose(healer, party, tank, tools):
    single, party_heals, hots, shields, keepers = tools
    living = [c for c in party if c.current_health > 0]
    frac = lambda c: c.current_health / max(1, c.health)
    hurt = sorted(living, key=frac)
    low = hurt[0]
    # 1. emergency
    if frac(low) < 0.40:
        opts = [a for a in single + shields if ready(a, healer)]
        if opts:
            opts.sort(key=lambda a: (getattr(a, "cast_speed", 1.0) > 0.95, -est(a, healer)))
            return opts[0], low
    # 2. party / chain heal
    if sum(1 for c in living if frac(c) < 0.75) >= 3:
        opts = [a for a in party_heals if ready(a, healer)]
        if opts:
            return max(opts, key=lambda a: est(a, healer)), healer
    # 3. maintenance on the tank
    if tank.current_health > 0:
        for a in shields + hots + keepers:
            if ready(a, healer) and not has_effect(tank, a.ability_id):
                return a, tank
    # 4. efficient heal
    if frac(low) < 0.85:
        missing = low.health - low.current_health
        opts = [a for a in single + hots if ready(a, healer) and not (a.effect_type == "hot" and has_effect(low, a.ability_id))]
        if opts:
            fits = [a for a in opts if est(a, healer) <= missing * 1.2]
            if fits:
                # most healing per mana among those that fit, bigger first on ties
                return max(fits, key=lambda a: (est(a, healer) / max(1, a.talented_cost(healer) or 1), est(a, healer))), low
            return min(opts, key=lambda a: est(a, healer)), low
    return None, None


def run(spec, level, pattern, intensity, seed, gen, cm):
    import sim_matrix as M
    import sim_role_balance as R
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    random.seed(seed)
    healer = M.build(spec, "healer", level, "geared", gen)
    healer.name = "Healer"
    members = [healer]
    tank = None
    for role, sp in PARTY:
        c = M.build(sp, role, level, "geared", gen)
        c.name = sp
        members.append(c)
        if role == "tank":
            tank = c
    party = Party(members[0])
    for c in members[1:]:
        party.add_member(c) if hasattr(party, "add_member") else party.members.append(c)
    with quiet():
        foe = cm.spawn_creature(sorted(M.pool(cm, level))[0], level=level)
        foe.max_health = foe.current_health = 10 ** 8
        engine = CombatEngine(healer, foe, party=party, enemies=[foe])
        for c in members:
            R.precast_stances(c, engine)
    for c in members:
        c.current_health = c.health
        if getattr(c, "mana", 0):
            c.current_mana = c.mana
    tools = kit(healer)
    t_heal = 0.0
    for r in range(ROUNDS):
        hits = PATTERNS[pattern](r)
        with quiet():
            for c in members:
                if c.current_health <= 0:
                    continue
                share = (hits.get("all", 0) + (hits.get("tank", 0) if c is tank else 0)) * intensity
                if share > 0:
                    c.take_damage(max(1, int(c.health * share)), "shadow", attacker_level=level, attacker=foe)
        if any(c.current_health <= 0 for c in members):
            return False
        # the healer acts until its clock catches up with the round (cast speed)
        while t_heal < r + 1:
            with quiet():
                a, target = choose(healer, members, tank, tools)
                engine.current_actor = healer
                engine.combat_phase = "action"
                spent = 1.0
                if a is not None:
                    ok, _ = engine.execute_ability(healer, a.ability_id, target)
                    if ok:
                        spent = getattr(a, "cast_speed", 1.0) or 1.0
                    else:
                        engine.execute_defend(healer)
                else:
                    engine.execute_defend(healer)
                if engine.current_actor is healer:
                    engine._end_turn(healer)
            t_heal += spent
        # everyone else's turn passes: their HoTs and shields tick and expire
        with quiet():
            for c in members[1:]:
                if c.current_health > 0:
                    engine._end_turn(c)
    return all(c.current_health > 0 for c in members)


def capacity(spec, level, pattern, seeds, gen, cm):
    """Highest intensity every seed survives, by binary search."""
    lo, hi = 0.0, 4.0
    for _ in range(8):
        mid = (lo + hi) / 2
        ok = all(run(spec, level, pattern, mid, 1000 + s, gen, cm) for s in range(seeds))
        lo, hi = (mid, hi) if ok else (lo, mid)
    return lo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="30,50")
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--patterns", default=",".join(PATTERNS))
    ap.add_argument("--json")
    args = ap.parse_args()
    import sim_matrix as M
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
    gen = LootGenerator()
    specs = [s for s, _ in M.specs_for(["healer"], args.only_class)]
    levels = [int(x) for x in args.levels.split(",")]
    patterns = args.patterns.split(",")
    table = {}
    for lv in levels:
        for spec in specs:
            for p in patterns:
                try:
                    table[(spec, lv, p)] = capacity(spec, lv, p, args.seeds, gen, cm)
                except Exception as e:                           # noqa: BLE001
                    print(f"  {spec} L{lv} {p}: {type(e).__name__}: {e}")
    for lv in levels:
        print(f"\nLEVEL {lv} - the most damage each healer keeps a party of five alive through for {ROUNDS} rounds "
              f"(intensity; ratio to the median healer)")
        meds = {p: statistics.median([v for (s, l, pp), v in table.items() if l == lv and pp == p] or [1]) for p in patterns}
        print(f"{'spec':<28}" + "".join(f"{p:>14}" for p in patterns) + f"{'overall':>12}")
        rows = []
        for spec in specs:
            cells, ratios = [], []
            for p in patterns:
                v = table.get((spec, lv, p))
                if v is None:
                    cells.append(f"{'-':>14}")
                    continue
                r = v / meds[p] if meds[p] else 0
                ratios.append(max(r, 0.01))
                cells.append(f"{v:>7.2f} {r:>4.2f}{'!' if r < 0.75 else ' '}")
            overall = math.exp(statistics.mean(math.log(x) for x in ratios)) if ratios else 0
            rows.append((spec, cells, overall))
        for spec, cells, overall in sorted(rows, key=lambda r: -r[2]):
            print(f"{spec:<28}" + "".join(cells) + f"{overall:>10.2f}{' !' if abs(overall - 1) > 0.10 else ''}")
    if args.json:
        Path(args.json).write_text(json.dumps({f"{s}|{l}|{p}": v for (s, l, p), v in table.items()}), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
