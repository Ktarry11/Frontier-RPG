#!/usr/bin/env python3
"""Is every spec of every class viable at every stage of the game? Solo and in a group, through the real engine.

    PYTHONPATH=. python3 tools/sim_viability.py [--mode solo|group|both] [--levels 12,25,38,52,58]
                                               [--fights 4] [--class Rogue] [--role tank|healer|dps]
                                               [--no-talents] [--no-buffs] [--tier geared|under|naked|over]
                                               [--json out.json]

Kyle, 15 Nov 2026: "Are classes viable at each step? 1-15, 16-30, 31-45, and 46-60 ... everything should be
viable. What's the point of 30 classes if 90% of them suck." and "Are fights possible without buffs? Without
professions. How about talents? ... Can every Healer be viable? Every tank? Dps? Is support useful or a waste of
space?"

SOLO   every spec, built for its own role (a healer levels as a healer, a tank as a tank - tools/sim_matrix.build:
       talents for that role, spec gear, its stances and its pet), against 1 and then 2 same-level normal
       creatures from that bracket's open zones. A healer or hybrid heals itself under half health. Reports wins
       and health left. Kyle's open-world target: one monster costs about a third of your health, two is risky.

GROUP  a standard party - Protection Warrior, Holy Priest, Fire Mage, Combat Rogue, Marksmanship Hunter - with the
       spec under test swapped into its role's slot (a tank replaces the Warrior, a healer the Priest, a damage
       or support spec the Hunter), against that bracket's real dungeon bosses at their level. The healer heals
       anyone under 80%, everyone else fights; monsters pick targets off the real threat table, so a tank that
       cannot hold aggro shows up as a dead healer. Reports wins, deaths and turns. A support spec's value is the
       difference it makes: compare its row to a plain damage spec's.

--no-talents builds with no points spent, --no-buffs skips stances, aspects, presences and party buffs.
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

TICK, MAX_TICKS = 0.25, 24000
BASE_PARTY = {"tank": "warrior_protection", "healer": "priest_holy",
              "dps": ["mage_fire", "rogue_combat", "hunter_marksmanship"]}
#: Kyle's brackets, and the bosses a group meets in each (dungeon, boss); the party is the boss's level
BRACKETS = [(1, 15), (16, 30), (31, 45), (46, 60)]
#: (dungeon, boss, the dungeon's level - which bracket it belongs to; the fight is at the boss's own level)
BOSSES = [("Ragefire Chasm", "Taragaman the Hungerer", 15), ("Ragefire Chasm", "Bazzalan", 15),
          ("Wailing Caverns", "Lord Pythas", 20), ("Shadowfang Keep", "Archmage Arugal", 23),
          ("Razorfen Kraul", "Agathelos the Raging", 30), ("The Drowning Floor", "Yearmaw", 35),
          ("The Cistern", "The Thirst", 52), ("Khaz Varun, the Black Hollow", "Thane Morrun the Unmade", 54),
          ("The Royal Hive", "Tunnel-King Ruzzak", 56), ("The Emberdeep", "The Caldera", 58)]

BUFFS = True


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def bracket_of(level):
    for i, (lo, hi) in enumerate(BRACKETS):
        if lo <= level <= hi:
            return i
    return len(BRACKETS) - 1


def make(spec, role, level, tier, gen):
    import sim_matrix as M
    c = M.build(spec, role, level, tier, gen)
    c.name = spec
    return c


def prepull(chars, engine):
    """Stances, aspects, forms, then every long party buff anyone carries, on everyone, before the pull."""
    import sim_role_balance as R
    if not BUFFS:
        return
    with quiet():
        for c in chars:
            R.precast_stances(c, engine)
        for c in chars:
            for a in c.get_learned_abilities():
                if (a.effect_type == "buff" and getattr(a, "target_type", None) in ("party", "ally")
                        and getattr(a, "buff_scope", None) in ("raid", "party")):
                    targets = chars if a.target_type == "ally" else [c]
                    for t in targets:
                        a.turns_remaining = 0
                        engine.execute_ability(c, a.ability_id, t)
                        if a.target_type == "party":
                            break
                    a.turns_remaining = 0
        for c in chars:
            c.current_health = c.health
            if getattr(c, "mana", 0):
                c.current_mana = c.mana


def fight(chars, roles, enemies):
    """One fight to its end -> (won, deaths, turns, {name: hp fraction})."""
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from tools.sim_class_balance import plan
    import sim_matrix as M
    party = Party(chars[0])
    for c in chars[1:]:
        party.add_member(c) if hasattr(party, "add_member") else party.members.append(c)
    with quiet():
        engine = CombatEngine(chars[0], enemies[0], party=party, enemies=enemies)
    prepull(chars, engine)
    plans = {}
    for c in chars:
        h, att, _s, _d = plan(c)
        if M.real_role(getattr(c, "_matrix_spec", ""), roles[id(c)]) in ("melee_dps", "tank"):
            att = [a for a in att if not getattr(a, "requires_ranged_weapon", None)] or att
        form = getattr(c, "current_form", None)
        if form:
            from combat.forms import resource_for_form
            from combat.abilities import ResourceType
            if resource_for_form(form) not in (None, ResourceType.MANA):
                def in_form(a, form=form):
                    rf = getattr(a, "requires_form", None)
                    rf = rf if isinstance(rf, (list, tuple)) else ([rf] if rf else [])
                    return form in rf or a.ability_id.endswith("_attack")
                att = [a for a in att if in_form(a)] or att
                h = [a for a in h if in_form(a)]
        plans[id(c)] = (h, att)
    turns = 0
    for _ in range(MAX_TICKS):
        with quiet():
            engine.update(TICK)
        if not engine.is_active:
            break
        actor = engine.current_actor
        if actor is None:
            continue
        if actor not in chars:
            with quiet():
                if getattr(actor, "is_monster", False) or actor in enemies:
                    engine.execute_monster_action()
                elif hasattr(engine, "execute_pet_action"):
                    engine.execute_pet_action()
                else:
                    engine._end_turn(actor)
            continue
        turns += 1
        heals, attacks = plans[id(actor)]
        living = [c for c in chars if c.current_health > 0]
        if not living:
            break
        hurt = min(living, key=lambda c: c.current_health / max(1, c.health))
        healer = roles[id(actor)] == "healer"
        threshold = 0.8 if healer else 0.45
        acted = False
        with quiet():
            if heals and hurt.current_health / max(1, hurt.health) < threshold and (healer or hurt is actor):
                for h in heals:
                    if engine.execute_ability(actor, h.ability_id, hurt)[0]:
                        acted = True
                        break
            if not acted:
                foes = engine.living_enemies() if hasattr(engine, "living_enemies") else \
                    [e for e in enemies if e.is_alive()]
                foes = sorted(foes, key=lambda e: not getattr(e, "is_boss", False))
                if not foes:
                    break
                for a in attacks:
                    if engine.execute_ability(actor, a.ability_id, foes[0])[0]:
                        acted = True
                        break
            if not acted:
                engine.execute_defend(actor)
    won = bool(getattr(engine, "victory", False))
    deaths = sum(1 for c in chars if c.current_health <= 0)
    return won, deaths, turns, {c.name: max(0.0, c.current_health / max(1, c.health)) for c in chars}


# ----------------------------------------------------------------------------------------------- solo
def solo(specs, levels, fights, tier, gen, cm, rng):
    import sim_matrix as M
    out = {}
    for lv in levels:
        pool = M.pool(cm, lv)
        for spec, role in specs:
            row = {}
            for count in (1, 2):
                wins, left, turns = 0, [], []
                for _ in range(fights):
                    try:
                        c = make(spec, role, lv, tier, gen)
                        with quiet():
                            foes = [cm.spawn_creature(rng.choice(pool), level=lv) for _ in range(count)]
                        won, _d, t, hp = fight([c], {id(c): role}, foes)
                    except Exception as e:                       # noqa: BLE001
                        print(f"  {spec} L{lv}: {type(e).__name__}: {e}")
                        won, t, hp = False, 0, {spec: 0}
                    wins += won
                    left.append(hp.get(spec, 0) if won else 0.0)
                    turns.append(t)
                row[count] = (wins / fights, statistics.mean(left), statistics.mean(turns))
            out[(spec, role, lv)] = row
    return out


# ---------------------------------------------------------------------------------------------- group
def bosses_for(level, cm):
    """This level's bracket's bosses, each with the level the party meets it at."""
    b = bracket_of(level)
    out = []
    for cave, boss, dlv in BOSSES:
        info = cm.creatures.get(boss)
        if not info:
            continue
        blv = info["level_range"][1]
        if bracket_of(dlv) == b:
            out.append((cave, boss, blv))
    return out


def group(specs, levels, fights, tier, gen, cm, rng):
    out = {}
    done_brackets = set()
    for lv in levels:
        b = bracket_of(lv)
        if b in done_brackets:
            continue
        done_brackets.add(b)
        targets = bosses_for(lv, cm)
        if not targets:
            print(f"  bracket {BRACKETS[b]}: no dungeon bosses to fight")
            continue
        for spec, role in specs:
            res = []
            for cave, boss, blv in targets:
                for _ in range(fights):
                    slots = [("tank", BASE_PARTY["tank"]), ("healer", BASE_PARTY["healer"])] + \
                            [("dps", s) for s in BASE_PARTY["dps"]]
                    idx = {"tank": 0, "healer": 1, "dps": 4}[role]
                    slots[idx] = (role, spec)
                    try:
                        chars = [make(s, r, blv, tier, gen) for r, s in slots]
                        for i, c in enumerate(chars):
                            c.name = f"{c.name}#{i}"
                        roles = {id(c): r for c, (r, _s) in zip(chars, slots)}
                        with quiet():
                            foe = cm.spawn_creature(boss, level=blv)
                        foe.location_type = "cave"
                        won, deaths, t, _hp = fight(chars, roles, [foe])
                    except Exception as e:                       # noqa: BLE001
                        print(f"  {spec} vs {boss}: {type(e).__name__}: {e}")
                        won, deaths, t = False, 5, 0
                    res.append((boss, won, deaths, t))
            out[(spec, role, b)] = res
    return out


def main():
    global BUFFS
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="both", choices=("solo", "group", "both"))
    ap.add_argument("--levels", default="12,25,38,52,58")
    ap.add_argument("--fights", type=int, default=4)
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--role", choices=("tank", "healer", "dps"))
    ap.add_argument("--tier", default="geared")
    ap.add_argument("--no-talents", action="store_true")
    ap.add_argument("--no-buffs", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json")
    args = ap.parse_args()
    import sim_matrix as M
    import sim_role_balance as R
    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    if args.no_talents:
        R.SPEND_TALENTS = False
    BUFFS = not args.no_buffs
    random.seed(args.seed)
    rng = random.Random(args.seed)
    gen = LootGenerator()
    with quiet():
        cm = CreatureManager()
    roles = [args.role] if args.role else ["tank", "healer", "dps"]
    specs = M.specs_for(roles, args.only_class)
    levels = [int(x) for x in args.levels.split(",")]
    print(f"{len(specs)} spec-roles, levels {levels}, {args.fights} fights each, tier {args.tier}, "
          f"talents {'off' if args.no_talents else 'on'}, buffs {'off' if args.no_buffs else 'on'}")
    dump = {}
    if args.mode in ("solo", "both"):
        res = solo(specs, levels, args.fights, args.tier, gen, cm, rng)
        print(f"\nSOLO - 1 mob: win% / health left     2 mobs: win% / health left")
        print(f"{'spec':<30}{'role':<7}" + "".join(f"{'L' + str(lv):>22}" for lv in levels))
        weak = []
        for spec, role in specs:
            cells = []
            for lv in levels:
                r = res.get((spec, role, lv))
                if not r:
                    cells.append(f"{'-':>22}")
                    continue
                w1, h1, _ = r[1]
                w2, h2, _ = r[2]
                flag = "!" if w1 < 0.75 else " "
                if w1 < 0.75:
                    weak.append((spec, role, lv, w1))
                cells.append(f"{w1:>5.0%} {h1:>4.0%} | {w2:>4.0%} {h2:>4.0%}{flag}")
            print(f"{spec:<30}{role:<7}" + "".join(cells))
        print(f"\n{len(weak)} spec-levels win under 75% of single same-level fights:")
        for w in weak:
            print(f"   {w[0]} ({w[1]}) L{w[2]}: {w[3]:.0%}")
        dump["solo"] = {f"{s}|{r}|{lv}": v for (s, r, lv), v in res.items()}
    if args.mode in ("group", "both"):
        res = group(specs, levels, args.fights, args.tier, gen, cm, rng)
        print(f"\nGROUP - the spec in its slot of a standard party, against its bracket's bosses: wins, mean deaths")
        weak = []
        for (spec, role, b), rows in sorted(res.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0])):
            wins = sum(1 for r in rows if r[1]) / len(rows)
            deaths = statistics.mean(r[2] for r in rows)
            per = {}
            for boss, won, d, t in rows:
                per.setdefault(boss, []).append(won)
            detail = "  ".join(f"{bo.split()[0]} {sum(v)}/{len(v)}" for bo, v in per.items())
            flag = "!" if wins < 0.6 else " "
            if wins < 0.6:
                weak.append((spec, role, BRACKETS[b], wins))
            print(f"  {str(BRACKETS[b]):<9}{role:<7}{spec:<30}{wins:>5.0%}{flag} deaths {deaths:.1f}   {detail}")
        print(f"\n{len(weak)} spec-brackets win under 60% of their bracket's bosses:")
        for w in weak:
            print(f"   {w[0]} ({w[1]}) {w[2]}: {w[3]:.0%}")
        dump["group"] = {f"{s}|{r}|{b}": v for (s, r, b), v in res.items()}
    if args.json:
        Path(args.json).write_text(json.dumps(dump), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
