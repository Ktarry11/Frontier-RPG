#!/usr/bin/env python3
"""The deep dive: scenarios the class passes never probed.

    PYTHONPATH=. python3 tools/sim_deep.py --scenario levelwalk [--levels 1-60] [--fights 2] [--class Mage]
    PYTHONPATH=. python3 tools/sim_deep.py --scenario tail      [--levels 20,40,60] [--fights 40]
    PYTHONPATH=. python3 tools/sim_deep.py --scenario chain     [--levels 20,40,60] [--fights 3]
    PYTHONPATH=. python3 tools/sim_deep.py --scenario petless   [--levels 20,40,60]
    PYTHONPATH=. python3 tools/sim_deep.py --scenario groups    [--levels 20,40,60]
    PYTHONPATH=. python3 tools/sim_deep.py --scenario wrongstat [--levels 20,40,60]

Kyle, 15 Nov 2026: "one last absolute deep dive. Aim for scenarios you didn't probe!" Built on
tools/sim_viability.py's make/fight (the same engine loop, planner, buffs and pets).

levelwalk  EVERY level, not four brackets: one normal mob of the level, solo. Turns to kill and health left, level by
           level, so the dip before a new rank and any spike stand out. A level is flagged when its turns run 40%
           over the spec's own neighbourhood (+-4 levels) or it loses a fight.
tail       BAD LUCK, NOT AVERAGES: many fights against one mob; the death rate and the 10th-percentile health left.
chain      PULL AFTER PULL WITHOUT DRINKING: health and mana carry over (no rest, no food), until death or 8 pulls.
petless    THE PET IS DEAD: the 13 pet classes' specs with no pet, against one mob, beside the same spec with one.
groups     ODD PARTIES against the bracket's dungeon bosses: no tank, no healer, two healers, all ranged, and the
           standard party with one member 3 levels under.
wrongstat  THE WRONG GEAR: a caster in strength/agility gear, a melee in caster gear, against one mob, beside its
           own gear.
"""
import argparse
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


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def parse_levels(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def one(V, cm, spec, role, lv, foes_n, gen, rng, tier="geared", prep=None):
    import sim_matrix as M
    c = V.make(spec, role, lv, tier, gen)
    if prep:
        prep(c)
    with quiet():
        foes = [cm.spawn_creature(rng.choice(M.pool(cm, lv)), level=lv) for _ in range(foes_n)]
    won, _d, t, hp = V.fight([c], {id(c): role}, foes)
    return won, t, hp.get(spec, 0) if won else 0.0, c


# ---------------------------------------------------------------------------------------------- levelwalk
def levelwalk(V, cm, specs, levels, fights, gen, rng):
    rows = {}
    for spec, role in specs:
        series = {}
        for lv in levels:
            res = []
            for _ in range(fights):
                try:
                    won, t, hp, _c = one(V, cm, spec, role, lv, 1, gen, rng)
                except Exception as e:                           # noqa: BLE001
                    print(f"  {spec} L{lv}: {type(e).__name__}: {e}")
                    won, t, hp = False, 0, 0.0
                res.append((won, t, hp))
            series[lv] = (sum(r[0] for r in res) / len(res), statistics.mean(r[1] for r in res),
                          statistics.mean(r[2] for r in res))
        flags = []
        for lv, (w, t, hp) in series.items():
            near = [series[x][1] for x in series if x != lv and abs(x - lv) <= 4]
            base = statistics.median(near) if near else t
            if w < 1.0 or (base and t > 1.4 * base and t - base >= 1.5):
                flags.append((lv, w, round(t, 1), round(base, 1), round(hp, 2)))
        rows[spec] = {"series": series, "flags": flags}
        worst = min(series.items(), key=lambda kv: (kv[1][0], kv[1][2]))
        print(f"  {spec:<30} turns {min(v[1] for v in series.values()):4.1f}-{max(v[1] for v in series.values()):4.1f}"
              f"  hp left {min(v[2] for v in series.values()):.2f}-{max(v[2] for v in series.values()):.2f}"
              f"  worst L{worst[0]}  flags {[f[0] for f in flags]}")
    return rows


# ---------------------------------------------------------------------------------------------- tail
def tail(V, cm, specs, levels, fights, gen, rng):
    rows = {}
    for lv in levels:
        print(f"\nLEVEL {lv}: {fights} fights each against one mob")
        out = []
        for spec, role in specs:
            res = []
            for _ in range(fights):
                try:
                    won, t, hp, _c = one(V, cm, spec, role, lv, 1, gen, rng)
                except Exception as e:                           # noqa: BLE001
                    won, t, hp = False, 0, 0.0
                res.append((won, hp))
            deaths = sum(not w for w, _ in res) / len(res)
            hps = sorted(h for _, h in res)
            p10 = hps[max(0, int(len(hps) * 0.1) - 1)]
            out.append((deaths, p10, spec))
            rows.setdefault(spec, {})[lv] = {"death_rate": deaths, "p10_hp": p10, "median_hp": statistics.median(hps)}
        for deaths, p10, spec in sorted(out, key=lambda r: (-r[0], r[1]))[:15]:
            print(f"  {spec:<30} deaths {deaths:5.1%}   10th-percentile health left {p10:.2f}")
        print(f"  ... {sum(1 for r in out if r[0] == 0)}/{len(out)} specs never died")
    return rows


# ---------------------------------------------------------------------------------------------- chain
def chain(V, cm, specs, levels, fights, gen, rng, max_pulls=8):
    import sim_matrix as M
    rows = {}
    for lv in levels:
        print(f"\nLEVEL {lv}: pulls in a row with no rest, food or drink (max {max_pulls})")
        out = []
        for spec, role in specs:
            pulls_list = []
            for _ in range(fights):
                try:
                    c = V.make(spec, role, lv, "geared", gen)
                    pulls = 0
                    for _p in range(max_pulls):
                        hp0, mp0 = c.current_health, getattr(c, "current_mana", 0)
                        with quiet():
                            foe = cm.spawn_creature(rng.choice(M.pool(cm, lv)), level=lv)
                        # fight() refills health and mana in prepull: carry what was left instead
                        saved = V.BUFFS
                        V.BUFFS = False
                        try:
                            won, _d, _t, _hp = V.fight([c], {id(c): role}, [foe])
                        finally:
                            V.BUFFS = saved
                        if not won or c.current_health <= 0:
                            break
                        pulls += 1
                except Exception as e:                           # noqa: BLE001
                    print(f"  {spec} L{lv}: {type(e).__name__}: {e}")
                    pulls = 0
                pulls_list.append(pulls)
            med = statistics.median(pulls_list)
            out.append((med, spec))
            rows.setdefault(spec, {})[lv] = {"pulls": pulls_list}
        for med, spec in sorted(out)[:15]:
            print(f"  {spec:<30} pulls survived (median) {med}")
        print(f"  median spec: {statistics.median(m for m, _ in out)} pulls; {sum(1 for m, _ in out if m >= max_pulls)}"
              f"/{len(out)} did all {max_pulls}")
    return rows


# ---------------------------------------------------------------------------------------------- petless
def petless(V, cm, specs, levels, fights, gen, rng):
    rows = {}
    for lv in levels:
        print(f"\nLEVEL {lv}: pet classes with and without their pet, one mob")
        for spec, role in specs:
            probe = V.make(spec, role, lv, "geared", gen)
            if getattr(probe, "active_pet", None) is None:
                continue

            def kill_pet(c):
                with quiet():
                    try:
                        c.dismiss_pet()
                    except Exception:                            # noqa: BLE001
                        c.active_pet = None
            res = {}
            for label, prep in (("pet", None), ("no pet", kill_pet)):
                r = [one(V, cm, spec, role, lv, 1, gen, rng, prep=prep) for _ in range(fights)]
                res[label] = (sum(x[0] for x in r) / len(r), statistics.mean(x[1] for x in r),
                              statistics.mean(x[2] for x in r))
            rows.setdefault(spec, {})[lv] = res
            p, n = res["pet"], res["no pet"]
            flag = "  !" if n[0] < 1.0 or n[2] < 0.25 else ""
            print(f"  {spec:<30} with pet: win {p[0]:.0%} turns {p[1]:4.1f} hp {p[2]:.2f}   "
                  f"no pet: win {n[0]:.0%} turns {n[1]:4.1f} hp {n[2]:.2f}{flag}")
    return rows


# ---------------------------------------------------------------------------------------------- groups
def groups(V, cm, levels, fights, gen, rng):
    BP = V.BASE_PARTY
    comps = {
        "standard": [("tank", BP["tank"]), ("healer", BP["healer"])] + [("dps", s) for s in BP["dps"]],
        "no tank": [("healer", BP["healer"])] + [("dps", s) for s in BP["dps"]] + [("dps", "warlock_destruction")],
        "no healer": [("tank", BP["tank"])] + [("dps", s) for s in BP["dps"]] + [("dps", "warlock_destruction")],
        "two healers": [("tank", BP["tank"]), ("healer", BP["healer"]), ("healer", "shaman_restoration"),
                        ("dps", "mage_fire"), ("dps", "rogue_combat")],
        "all ranged": [("tank", BP["tank"]), ("healer", BP["healer"]), ("dps", "mage_fire"),
                       ("dps", "hunter_marksmanship"), ("dps", "warlock_destruction")],
        "one 3 under": [("tank", BP["tank"]), ("healer", BP["healer"])] + [("dps", s) for s in BP["dps"]],
    }
    rows = {}
    seen = set()
    for lv in levels:
        b = V.bracket_of(lv)
        if b in seen:
            continue
        seen.add(b)
        targets = V.bosses_for(lv, cm)
        print(f"\nBRACKET {V.BRACKETS[b]}: {len(targets)} bosses x {fights}")
        for name, comp in comps.items():
            wins = deaths = n = 0
            turns = []
            for _cave, boss, blv in targets:
                for _ in range(fights):
                    try:
                        chars = []
                        for i, (r, s) in enumerate(comp):
                            lvl = blv - 3 if (name == "one 3 under" and i == len(comp) - 1) else blv
                            c = V.make(s, r, lvl, "geared", gen)
                            c.name = f"{c.name}#{i}"
                            chars.append(c)
                        roles = {id(c): r for c, (r, _s) in zip(chars, comp)}
                        with quiet():
                            foe = cm.spawn_creature(boss, level=blv)
                        foe.location_type = "cave"
                        won, d, t, _hp = V.fight(chars, roles, [foe])
                    except Exception as e:                       # noqa: BLE001
                        print(f"  {name} vs {boss}: {type(e).__name__}: {e}")
                        won, d, t = False, len(comp), 0
                    wins += won
                    deaths += d
                    turns.append(t)
                    n += 1
            rows.setdefault(name, {})[str(V.BRACKETS[b])] = {"win": wins / max(1, n), "deaths": deaths / max(1, n)}
            print(f"  {name:<12} win {wins / max(1, n):5.0%}  deaths/fight {deaths / max(1, n):.2f}  "
                  f"turns {statistics.mean(turns) if turns else 0:.0f}")
    return rows


# ---------------------------------------------------------------------------------------------- wrongstat
def wrongstat(V, cm, specs, levels, fights, gen, rng):
    import sim_matrix as M
    from entities.character import Character
    caster_gear, melee_gear = "warrior_arms", "mage_fire"
    rows = {}
    for lv in levels:
        print(f"\nLEVEL {lv}: own gear vs the wrong gear (casters in Arms gear, melee in Fire Mage gear)")
        for spec, role in specs:
            real = M.real_role(spec, role)
            if role != "dps":
                continue
            wrong = melee_gear if real == "melee_dps" else caster_gear
            res = {}
            for label in ("own", "wrong"):
                r = []
                for _ in range(fights):
                    orig_build = M.build

                    def build_wrong(sp, ro, le, ti, ge, _w=wrong, _orig=orig_build):
                        # dress for another spec: the gear profile is read off Character._matrix_spec
                        import sim_role_balance as R
                        Character._matrix_spec = _w
                        try:
                            with quiet():
                                ch, _ = R.build(sp, le, ge, M.make_dress(ti), role=M.real_role(sp, ro))
                        finally:
                            del Character._matrix_spec
                        ch._matrix_spec = sp
                        if M.real_role(sp, ro) != "tank":
                            M.summon_screen_pet(ch)
                        ch.current_health = ch.health
                        if getattr(ch, "mana", 0):
                            ch.current_mana = ch.mana
                        return ch
                    if label == "wrong":
                        M.build = build_wrong
                    try:
                        r.append(one(V, cm, spec, role, lv, 1, gen, rng))
                    except Exception as e:                       # noqa: BLE001
                        print(f"  {spec} {label}: {type(e).__name__}: {e}")
                        r.append((False, 0, 0.0, None))
                    finally:
                        M.build = orig_build
                res[label] = (sum(x[0] for x in r) / len(r), statistics.mean(x[1] for x in r),
                              statistics.mean(x[2] for x in r))
            rows.setdefault(spec, {})[lv] = res
            o, w = res["own"], res["wrong"]
            print(f"  {spec:<30} own: win {o[0]:.0%} turns {o[1]:4.1f}   wrong: win {w[0]:.0%} turns {w[1]:4.1f}"
                  f"   {'(gear barely matters)' if w[1] <= o[1] * 1.1 and w[0] >= o[0] else ''}")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True,
                    choices=["levelwalk", "tail", "chain", "petless", "groups", "wrongstat"])
    ap.add_argument("--levels", default="20,40,60")
    ap.add_argument("--fights", type=int, default=3)
    ap.add_argument("--class", dest="only")
    ap.add_argument("--roles", default="dps,healer,tank")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--json")
    args = ap.parse_args()
    import sim_matrix as M
    import sim_viability as V
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
    gen = LootGenerator()
    rng = random.Random(args.seed)
    random.seed(args.seed)
    levels = parse_levels(args.levels)
    specs = M.specs_for(args.roles.split(","), only_class=args.only)
    fn = {"levelwalk": lambda: levelwalk(V, cm, specs, levels, args.fights, gen, rng),
          "tail": lambda: tail(V, cm, specs, levels, args.fights, gen, rng),
          "chain": lambda: chain(V, cm, specs, levels, args.fights, gen, rng),
          "petless": lambda: petless(V, cm, specs, levels, args.fights, gen, rng),
          "groups": lambda: groups(V, cm, levels, args.fights, gen, rng),
          "wrongstat": lambda: wrongstat(V, cm, specs, levels, args.fights, gen, rng)}[args.scenario]
    rows = fn()
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
