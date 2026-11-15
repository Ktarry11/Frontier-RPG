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
CONSUMABLES = False
#: what each role wants from an elixir, food or oil (--consumables: "what do professions add?")
ROLE_STATS = {"tank": ("stamina", "armor", "defense", "dodge", "parry", "block", "strength", "agility"),
              "healer": ("healing_power", "intellect", "spirit", "mp5", "spell_power"),
              "melee": ("attack_power", "strength", "agility", "crit_chance_physical", "hit_rating"),
              "caster": ("spell_power", "intellect", "crit_chance_spell", "fire_spell_power",
                         "frost_spell_power", "shadow_spell_power", "nature_spell_power", "arcane_spell_power",
                         "holy_spell_power")}


def use_consumables(c, role):
    """The best elixir in each slot, food and a weapon oil for this character's role and level."""
    from entities.consumable_manager import get_consumable_manager
    import sim_matrix as M
    cm = get_consumable_manager()
    real = M.real_role(getattr(c, "_matrix_spec", ""), role)
    want = ROLE_STATS["tank" if real == "tank" else "healer" if real == "healer"
                      else "melee" if real == "melee_dps" else "caster"]
    best = {}
    for cid in cm.get_all_consumable_ids():
        cons = cm.get_consumable(cid)
        cat = getattr(cons, "buff_category", None)
        if cons is None or cons.consumable_type not in ("elixir", "food") or not cat:
            continue
        if (cons.required_level or 1) > c.level:
            continue
        score = sum(v for k, v in (cons.stat_bonuses or {}).items() if k in want and isinstance(v, (int, float)))
        if score > best.get(cat, (0, None))[0]:
            best[cat] = (score, cons)
    for cat, (_sc, cons) in best.items():
        try:
            c.apply_consumable_buff(cat, cons)
        except Exception:                                       # noqa: BLE001
            pass
    c._recalculate_derived_stats()


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
    c._sim_role = role
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
        if CONSUMABLES:
            for c in chars:
                use_consumables(c, getattr(c, "_sim_role", "dps"))
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
                live = {getattr(fx, "effect_id", None) for fx in foes[0]._effects()} if hasattr(foes[0], "_effects") else set()
                for a in attacks:
                    if a.effect_type in ("dot", "spell_dot") and a.ability_id in live:
                        continue
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


# --------------------------------------------------------------------------------------------- hidden
def hidden(fights, tier, gen, cm, rng):
    """Skull zones, hidden layers and frontier zones: a standard party of 5 and of 3 (tank, healer, mage - a
    friend's group, 15 Nov 2026: "no way an at level group can take on the shoals area") against two of the
    zone's normal creatures and against each of its bosses, at the creature's own level. Reported by KIND -
    never by place (Kyle's standing rule: the game and the reports never say where a hidden zone is)."""
    from world.hidden_zones import creature_kinds
    kinds = {}
    for name, k in creature_kinds().items():
        info = cm.creatures.get(name)
        if info:
            kinds.setdefault(k, []).append((name, info))
    party5 = [("tank", BASE_PARTY["tank"]), ("healer", BASE_PARTY["healer"])] + [("dps", s) for s in BASE_PARTY["dps"]]
    party3 = party5[:3]
    out = {}
    for k in sorted(kinds):
        trash = [(n, i) for n, i in kinds[k] if not i.get("is_boss")]
        bosses = [(n, i) for n, i in kinds[k] if i.get("is_boss")]
        for label, comp in (("party of 5", party5), ("party of 3", party3)):
            for what, pool, count in (("2 trash", trash, 2), ("boss", bosses, 1)):
                if not pool:
                    continue
                wins, deaths = 0, []
                for _ in range(fights):
                    name, info = rng.choice(pool)
                    lv = info["level_range"][1]
                    try:
                        chars = [make(sp, r, lv, tier, gen) for r, sp in comp]
                        for i, c in enumerate(chars):
                            c.name = f"{c.name}#{i}"
                        roles = {id(c): r for c, (r, _s) in zip(chars, comp)}
                        with quiet():
                            foes = [cm.spawn_creature(name if what == "boss" else rng.choice(pool)[0], level=lv)
                                    for _ in range(count)]
                        won, d, _t, _hp = fight(chars, roles, foes)
                    except Exception as e:                       # noqa: BLE001
                        print(f"  {k} {what}: {type(e).__name__}: {e}")
                        won, d = False, len(comp)
                    wins += won
                    deaths.append(d)
                out[(k, label, what)] = (wins / fights, statistics.mean(deaths), len(pool))
    return out


# -------------------------------------------------------------------------------------------- content
#: Kyle, 15 Nov 2026: "We need to test in open world, Dungeons, skull zones (open and dungeon) and frontier zone
#: (open and dungeon) as well. I want this to be exhaustive."
CONTENT = ("dungeon", "skull_open", "skull_dungeon", "frontier_open", "frontier_deep")
HIDDEN_KIND = {"skull_open": "skull_zone", "skull_dungeon": "hidden_layer",
               "frontier_open": "frontier_open", "frontier_deep": "frontier_deep"}
PULL = {"dungeon": 3, "skull_open": 2, "skull_dungeon": 3, "frontier_open": 2, "frontier_deep": 3}


def content_pools(cm):
    """{content: {bracket: {"trash": [...], "boss": [...]}}} from the real tables. Hidden places by kind only."""
    from world.hidden_zones import creature_kinds
    from world.zone_classification import DUNGEONS
    hidden = creature_kinds()
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))
    in_dungeon = set()

    def walk(node, key):
        if isinstance(node, dict):
            if isinstance(node.get("creatures"), dict) and (node.get("name") or key) in set(DUNGEONS):
                in_dungeon.update(node["creatures"])
            for k, v in node.items():
                walk(v, k)
    walk(enc, None)
    pools = {}

    def add(content, name):
        info = cm.creatures.get(name)
        if not info or not info.get("level_range"):
            return
        b = bracket_of(info["level_range"][1])
        kind = "boss" if info.get("is_boss") else "trash"
        pools.setdefault(content, {}).setdefault(b, {"trash": [], "boss": []})[kind].append(name)
    for name in in_dungeon:
        if name not in hidden:
            add("dungeon", name)
    for name, k in hidden.items():
        for content, hk in HIDDEN_KIND.items():
            if k == hk:
                add(content, name)
    return pools


def content(specs, fights, tier, gen, cm, rng, only=None):
    """Every spec in its slot of the standard party, against trash pulls and bosses of every content kind in
    every bracket that has it. -> {(spec, role, content, bracket): {"trash": [won...], "boss": [won...]}}"""
    pools = content_pools(cm)
    out = {}
    for spec, role in specs:
        slots = [("tank", BASE_PARTY["tank"]), ("healer", BASE_PARTY["healer"])] + \
                [("dps", s) for s in BASE_PARTY["dps"]]
        slots[{"tank": 0, "healer": 1, "dps": 4}[role]] = (role, spec)
        for c_kind in CONTENT:
            if only and c_kind not in only:
                continue
            for b, pool in sorted((pools.get(c_kind) or {}).items()):
                cell = {"trash": [], "boss": []}
                for what in ("trash", "boss"):
                    names = pool[what]
                    if not names:
                        continue
                    for _ in range(fights):
                        lead = rng.choice(names)
                        lv = cm.creatures[lead]["level_range"][1]
                        try:
                            chars = [make(sp, r, lv, tier, gen) for r, sp in slots]
                            for i, c in enumerate(chars):
                                c.name = f"{c.name}#{i}"
                            roles = {id(c): r for c, (r, _s) in zip(chars, slots)}
                            picks = [lead] if what == "boss" else [lead] + [rng.choice(names) for _ in range(PULL[c_kind] - 1)]
                            with quiet():
                                foes = [cm.spawn_creature(n, level=cm.creatures[n]["level_range"][1]) for n in picks]
                            for f in foes:
                                if c_kind in ("dungeon", "skull_dungeon", "frontier_deep"):
                                    f.location_type = "cave"
                            won, d, t, _hp = fight(chars, roles, foes)
                        except Exception as e:                   # noqa: BLE001
                            print(f"  {spec} {c_kind} {what}: {type(e).__name__}: {e}")
                            won, d, t = False, 5, 0
                        cell[what].append((won, d, t))
                out[(spec, role, c_kind, b)] = cell
    return out


def trio(specs, fights, tier, gen, cm, rng):
    """A tank, a healer and ONE damage spec - the spec under test in its slot - against its bracket's dungeon
    bosses. In a party of five the other four carry a weak spec; with three, its own output decides the kill.
    -> {(spec, role, bracket): [(boss, won, deaths, turns)]}"""
    pools = content_pools(cm)
    base = [("tank", BASE_PARTY["tank"]), ("healer", BASE_PARTY["healer"]), ("dps", "mage_fire")]
    out = {}
    for spec, role in specs:
        slots = list(base)
        slots[{"tank": 0, "healer": 1, "dps": 2}[role]] = (role, spec)
        for b, pool in sorted((pools.get("dungeon") or {}).items()):
            rows = []
            for boss in sorted(pool["boss"])[:6]:
                lv = cm.creatures[boss]["level_range"][1]
                for _ in range(fights):
                    try:
                        chars = [make(sp, r, lv, tier, gen) for r, sp in slots]
                        for i, c in enumerate(chars):
                            c.name = f"{c.name}#{i}"
                        roles = {id(c): r for c, (r, _s) in zip(chars, slots)}
                        with quiet():
                            foe = cm.spawn_creature(boss, level=lv)
                        foe.location_type = "cave"
                        won, d, t, _hp = fight(chars, roles, [foe])
                    except Exception as e:                       # noqa: BLE001
                        print(f"  {spec} vs {boss}: {type(e).__name__}: {e}")
                        won, d, t = False, 3, 0
                    rows.append((boss, won, d, t))
            out[(spec, role, b)] = rows
    return out


def report_trio(res):
    print("\nTRIO - tank, healer and one damage spec (the one under test in its slot) vs its bracket's bosses")
    by = {}
    for (spec, role, b), rows in res.items():
        wins = sum(1 for r in rows if r[1]) / len(rows)
        won_t = [r[3] for r in rows if r[1]]
        by.setdefault((role, b), []).append((spec, wins, statistics.mean(won_t) if won_t else 0))
    for (role, b), rows in sorted(by.items()):
        med_w = statistics.median(r[1] for r in rows)
        med_t = statistics.median(r[2] for r in rows if r[2]) if any(r[2] for r in rows) else 0
        print(f"\n  {role} {BRACKETS[b]}: median win {med_w:.0%}, median turns to kill {med_t:.0f}")
        for spec, w, t in sorted(rows, key=lambda r: (r[1], -r[2])):
            flag = "  <- behind" if (w < med_w - 0.2 or (t and med_t and t > med_t * 1.35)) else ""
            print(f"     {spec:<30} win {w:>4.0%}  turns {t:>5.1f}{flag}")


def report_content(res):
    """Win rates per spec, and the specs well below their own role on the same content and bracket."""
    by_cell = {}
    for (spec, role, ck, b), cell in res.items():
        for what in ("trash", "boss"):
            if cell[what]:
                w = sum(1 for x in cell[what] if x[0]) / len(cell[what])
                by_cell.setdefault((role, ck, b, what), []).append((spec, w))
    print("\nCONTENT - the standard party's win rate with each spec in its slot (trash pulls / bosses)")
    for (role, ck, b, what), rows in sorted(by_cell.items()):
        ws = [w for _s, w in rows]
        med = statistics.median(ws)
        low = [f"{s} {w:.0%}" for s, w in sorted(rows, key=lambda r: r[1]) if w < med - 0.34]
        print(f"  {ck:<14}{str(BRACKETS[b]):<9}{what:<6}{role:<7} median {med:>4.0%}  range {min(ws):.0%}-{max(ws):.0%}"
              + (f"   BEHIND: {', '.join(low)}" if low else ""))


def main():
    global BUFFS, CONSUMABLES
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="both", choices=("solo", "group", "both", "hidden", "content", "trio"))
    ap.add_argument("--content", help="comma list of: " + ",".join(CONTENT))
    ap.add_argument("--levels", default="12,25,38,52,58")
    ap.add_argument("--fights", type=int, default=4)
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--role", choices=("tank", "healer", "dps"))
    ap.add_argument("--tier", default="geared")
    ap.add_argument("--no-talents", action="store_true")
    ap.add_argument("--no-buffs", action="store_true")
    ap.add_argument("--consumables", action="store_true", help="best elixirs, food and oil for the role")
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
    CONSUMABLES = args.consumables
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
    if args.mode == "trio":
        res = trio(specs, args.fights, args.tier, gen, cm, rng)
        report_trio(res)
        if args.json:
            Path(args.json).write_text(json.dumps({"|".join(map(str, k)): v for k, v in res.items()}), encoding="utf-8")
        return 0
    if args.mode == "content":
        res = content(specs, args.fights, args.tier, gen, cm, rng,
                      only=set(args.content.split(",")) if args.content else None)
        report_content(res)
        if args.json:
            Path(args.json).write_text(json.dumps({"|".join(map(str, k)): v for k, v in res.items()}), encoding="utf-8")
        return 0
    if args.mode == "hidden":
        res = hidden(args.fights, args.tier, gen, cm, rng)
        print(f"\nHIDDEN ZONES - by kind (at the creature's level): wins, mean deaths")
        for (k, label, what), (w, d, n) in sorted(res.items()):
            print(f"  {k:<14}{label:<12}{what:<9}{w:>5.0%}  deaths {d:.1f}   ({n} creatures of this sort)")
        return 0
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
