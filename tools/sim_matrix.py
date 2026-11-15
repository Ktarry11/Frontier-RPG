#!/usr/bin/env python3
"""Every spec, under every condition, measured several times over.

    PYTHONPATH=. python3 tools/sim_matrix.py [--levels 20,40,60] [--gear naked,under,geared,over]
                                             [--offsets even,under,over] [--roles dps,tank,healer]
                                             [--class Mage] [--spec mage_fire] [--passes 3] [--fights 6]
                                             [--out data/sim_matrix/<name>.json]

Kyle, 15 Nov 2026: "You'll do multiple passes in a row for consistency. Do it naked, geared, undergeared.
Overgeared. Over leveled. Under leveled. Tanks, healers, dps. We want to check mana levels too. Casters should
oom longer fights. Lots of variables."

THE CONDITIONS
  gear     naked    nothing worn
           under    commons, 8 item levels below the character
           geared   greens below 20, blues from 20, at the character's level (what a player levelling has)
           over     epics, 5 item levels above
           Every piece is itemized for the SPEC (data/items/spec_gear.json): its stat template, its school,
           its weapons. A class-default dress measured an agility bear in intellect gear once (learnings.md).
  offsets  even     the enemy is the character's level
           under    the character is UNDER-leveled: the enemy is 3 levels higher
           over     the character is OVER-leveled: the enemy is 5 levels lower

WHAT EACH ROLE IS MEASURED ON
  dps      against real open-world creatures of that level band (the same pools sim_difficulty.py uses):
             win %, turns, health left, mana spent per turn, and how many such fights one bar of mana lasts.
           mana endurance: casting its rotation into a target that never dies and never hits back, from a
             full bar - the turn it can no longer afford any damaging spell ("never" inside 60 turns).
             Kyle: casters should run dry in long fights.
  tank     sim_role_balance.tank_axes: turns alive and damage taken per turn against the hardest hitter.
  healer   sim_role_balance.healer_axes: healing per turn and turns of mana.

PASSES. The whole matrix runs --passes times with different seeds, and every cell reports its median and
its spread across passes. A cell whose passes disagree by more than 25% is marked "~" - it is not measured
well enough to act on yet.

Talents are spent in the spec's own tree for its role (sim_role_balance.build), forms and stances go up
before the pull, and the character starts every fight full.
"""
import argparse
import contextlib
import io
import json
import os
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

GEAR = {
    "naked": None,
    "under": ("common", -8),
    "geared": ("geared", 0),
    "over": ("epic", +5),
}
OFFSETS = {"even": 0, "under": +3, "over": -5}
#: level band -> an open zone whose creatures sit there
BANDS = [(10, "Durotar"), (17, "Silverpine North"), (25, "Ashenvale West"), (34, "Arathi Central"),
         (45, "The Abyssal Sands"), (54, "Tempest Shallows")]
OFFENSIVE = {"damage", "spell_damage", "spell_dot", "dot", "ranged_damage", "damage_and_heal",
             "damage_and_restore_mana"}
ENDURANCE_TURNS = 60
TICK, MAX_TICKS = 0.25, 16000


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


# ----------------------------------------------------------------------------------- gear
def gear_slots():
    from tools.sim_class_balance import GEAR_SLOTS
    return GEAR_SLOTS


def make_dress(tier):
    """A dress(char, gen, level) for this gear tier, itemized for the character's spec."""
    def dress(char, gen, level):
        if GEAR[tier] is None:
            return 0
        rarity, shift = GEAR[tier]
        if rarity == "geared":
            rarity = "uncommon" if level < 20 else "rare"
        ilvl = max(1, level + shift)
        from entities.spec_gear import profile
        prof = profile(getattr(char, "_matrix_spec", None)) or {}
        itemize = {k: prof.get(k) for k in ("stat_template", "school") if prof.get(k)}
        worn = 0
        for slot in gear_slots():
            wtype = (prof.get("weapons") or {}).get(slot) if slot in ("main_hand", "off_hand", "ranged") else None
            # NOTHING IN THE OFF HAND WHEN THE SPEC HOLDS A TWO-HANDER. An off-hand item equipped after a two-hander
            # takes the two-hander OFF (Equipment.equip), so every two-hand spec - Arms, Retribution, Feral,
            # Barbarian, Knight - was measured unarmed until 15 Nov 2026 (Feral's weapon roll read 0).
            if slot == "off_hand" and prof.get("weapons") and not wtype:
                continue
            try:
                item = gen.generate_item_for_class(char.char_class, ilvl, slot=slot, rarity=rarity,
                                                   player_level=max(level, ilvl), weapon_type=wtype, **itemize)
            except Exception:                                   # noqa: BLE001
                try:
                    item = gen.generate_item_for_class(char.char_class, ilvl, slot=slot, rarity=rarity,
                                                       player_level=max(level, ilvl))
                except Exception:                               # noqa: BLE001
                    continue
            if item is None:
                continue
            char.inventory.append(item)
            if char.equip_item(item):
                worn += 1
            elif item in char.inventory:
                char.inventory.remove(item)
        return worn
    return dress


def real_role(spec, role):
    """"dps" -> this spec's own damage role (melee_dps / ranged_dps), which is what sim_role_balance keys its forms
    (Cat for a Feral) and talent preferences on. Passing "dps" built a Feral that never shifted and cast Wrath."""
    if role != "dps":
        return role
    import sim_role_balance as R
    return next((r for r in R.roles_of(spec) if r in ("melee_dps", "ranged_dps")), "melee_dps")


def build(spec, role, level, tier, gen):
    import sim_role_balance as R
    from entities.character import Character
    role = real_role(spec, role)
    # the spec is needed by dress before build() knows it; build() creates the character, so the
    # dress reads it off a class attribute set for the duration of the call
    Character._matrix_spec = spec
    try:
        with quiet():
            char, _ = R.build(spec, level, gen, make_dress(tier), role=role)
    finally:
        del Character._matrix_spec
    char._matrix_spec = spec
    # not for a tank: the tank measurements hit the tank, and a pet in front of it soaks the hits and makes
    # "turns alive" meaningless (Cultist, Felsworn, Knight of Xoroth, Mountain King, Reaper, Black Knight read
    # 0, thousands or negative)
    if role != "tank":
        summon_screen_pet(char)
    char.current_health = char.health
    if getattr(char, "mana", 0):
        char.current_mana = char.mana
    return char


def summon_screen_pet(char):
    """Summon the newest pet the pet screen offers this class at this level, as a player would.

    15 Nov 2026: thirteen classes get a pet from the pet screen (ui/screens/pet_screen.py - Hunter's is tamed,
    not cast), and every sim fought without one, so Beast Mastery's pet talents measured as nothing and its
    spec aura went to the cap to make up for a pet a real Hunter always has. Cast-summoned pets still come from
    the rotation."""
    from core.class_names import class_key
    from combat.pet_templates import pets_for_class
    if getattr(char, "active_pet", None) is not None:
        return
    try:
        options = pets_for_class(class_key(char.char_class), char.level)
    except Exception:                                          # noqa: BLE001
        return
    if not options:
        return
    with quiet():
        char.summon_pet(options[-1][0])


# ----------------------------------------------------------------------------------- dps
_POOLS = {}


def pool(cm, level):
    if not _POOLS:
        enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
        for lv, zone in BANDS:
            table = enc.get(zone, {}).get("open_zone", {}).get("creatures", {})
            _POOLS[lv] = [n for n, w in table.items()
                          if w and n in cm.creatures and not cm.creatures[n].get("is_boss")]
    lv = min(_POOLS, key=lambda b: abs(b - level))
    return _POOLS[lv]


def mana_of(c):
    return getattr(c, "current_mana", 0) if getattr(c, "mana", 0) else None


def fight(char, foe, rng):
    """One 1v1 to the end. -> (won, health left, turns, mana spent)."""
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from tools.sim_class_balance import plan
    import sim_role_balance as R
    with quiet():
        engine = CombatEngine(char, foe, party=Party(char))
        R.precast_stances(char, engine)
    heals, attacks, _setup, defensives = plan(char)
    m0 = mana_of(char)
    turns, last_heal, last_def = 0, -3, -4
    for _ in range(MAX_TICKS):
        with quiet():
            engine.update(TICK)
        if not engine.is_active:
            break
        actor = engine.current_actor
        if actor is None:
            continue
        if actor is not char:
            with quiet():
                engine.execute_monster_action()
            continue
        turns += 1
        acted = False
        with quiet():
            hp = char.current_health / max(1, char.health)
            if heals and hp < 0.45 and turns - last_heal >= 2:
                for h in heals:
                    if engine.execute_ability(char, h.ability_id, char)[0]:
                        acted, last_heal = True, turns
                        break
            if not acted and defensives and hp < 0.6 and turns - last_def >= 4:
                for d in defensives:
                    if engine.execute_ability(char, d.ability_id, char)[0]:
                        acted, last_def = True, turns
                        break
            if not acted:
                for a in attacks:
                    if engine.execute_ability(char, a.ability_id, foe)[0]:
                        acted = True
                        break
            if not acted:
                engine.execute_defend(char)
    won = bool(getattr(engine, "victory", False))
    m1 = mana_of(char)
    spent = (m0 - m1) if (m0 is not None and m1 is not None) else None
    return won, max(0.0, char.current_health / max(1, char.health)), turns, spent


def endurance(char, cm, level):
    """Turns of casting from a full bar before no damaging spell is affordable. None = no mana pool."""
    if not getattr(char, "mana", 0):
        return None
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from tools.sim_class_balance import plan
    import sim_role_balance as R
    with quiet():
        foe = cm.spawn_creature(pool(cm, level)[0], level=level)
    foe.max_health = foe.current_health = 10 ** 8
    with quiet():
        engine = CombatEngine(char, foe, party=Party(char))
        R.precast_stances(char, engine)
    char.current_mana = char.mana
    _h, attacks, _s, _d = plan(char)
    mana_attacks = [a for a in attacks if (getattr(a, "cost", 0) or 0) > 0
                    and getattr(getattr(a, "resource_type", None), "value", "") == "mana"]
    if not mana_attacks:
        return "no mana spells"
    for turn in range(1, ENDURANCE_TURNS + 1):
        cast = False
        with quiet():
            for a in attacks:
                a.turns_remaining = max(0, a.turns_remaining - 1) if hasattr(a, "turns_remaining") else 0
            for a in mana_attacks:
                if a.is_available() and char.current_mana >= a.talented_cost(char):
                    ok, _ = a.use(char, foe, party=[char])
                    if ok:
                        cast = True
                        break
            # a turn passes through the engine's own turn end: cooldowns, buffs counting down, and regen with the
            # five-second rule. A bare regen call left Clearcasting up forever and read Elemental as never-dry.
            engine._end_turn(char)
        if not cast and all(char.current_mana < a.talented_cost(char) for a in mana_attacks):
            return turn
    return f">{ENDURANCE_TURNS}"


def main_endurance(char, role, cm, level):
    """Turns of casting the class's MAIN spell (calibrate_mana_costs.main_spell) from a full bar, regen and the
    five-second rule included, into a target that never dies (damage) or an ally kept wounded (heals). This is
    what data/balance/mana_costs.json is calibrated to: ~20."""
    if not getattr(char, "mana", 0):
        return None
    from calibrate_mana_costs import main_spell
    a = main_spell(char, role)
    if a is None:
        return None
    with quiet():
        foe = cm.spawn_creature(pool(cm, level)[0], level=level)
    foe.max_health = foe.current_health = 10 ** 8
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    with quiet():
        engine = CombatEngine(char, foe, party=Party(char))
    char.current_mana = char.mana
    for turn in range(1, ENDURANCE_TURNS + 1):
        a.turns_remaining = 0
        if role == "healer":
            char.current_health = max(1, char.health // 3)
        with quiet():
            ok, _ = a.use(char, char if role == "healer" else foe, party=[char])
            engine._end_turn(char)
        if not ok:
            return turn
    return ENDURANCE_TURNS + 1


def dps_cell(spec, level, tier, offset, fights, gen, cm, rng):
    foe_level = max(1, level + OFFSETS[offset])
    wins, left, turns, spent = 0, [], [], []
    for _ in range(fights):
        char = build(spec, "dps", level, tier, gen)
        with quiet():
            foe = cm.spawn_creature(rng.choice(pool(cm, foe_level)), level=foe_level)
        won, hp, t, sp = fight(char, foe, rng)
        wins += won
        left.append(hp if won else 0.0)
        turns.append(t)
        if sp is not None:
            spent.append(sp)
    char = build(spec, "dps", level, tier, gen)
    out = {"win": wins / fights, "hp_left": statistics.mean(left), "turns": statistics.mean(turns)}
    if spent and getattr(char, "mana", 0):
        per_fight = statistics.mean(spent)
        out["mana_per_turn"] = per_fight / max(1, statistics.mean(turns))
        out["fights_per_bar"] = (char.mana / per_fight) if per_fight > 0 else float("inf")
    if offset == "even":
        out["endurance"] = endurance(char, cm, foe_level)
        out["main_endurance"] = main_endurance(char, "dps", cm, foe_level)
    return out


def tank_cell(spec, level, tier, offset, fights, gen):
    import sim_role_balance as R
    char = build(spec, "tank", level, tier, gen)
    with quiet():
        axes = R.tank_axes(char, max(1, level + OFFSETS[offset]), gen, make_dress(tier), fights)
    return {"turns_alive": axes["turns alive"], "dmg_per_turn": axes["net dmg/turn"],
            "phys_reduced": axes["phys reduced"]}


def healer_cell(spec, level, tier, offset, fights, gen, cm=None):
    import sim_role_balance as R
    char = build(spec, "healer", level, tier, gen)
    main = main_endurance(char, "healer", cm, level) if cm is not None else None
    char = build(spec, "healer", level, tier, gen)
    with quiet():
        axes = R.healer_axes(char, max(1, level + OFFSETS[offset]), gen, make_dress(tier), fights)
    return {"heal_per_turn": axes.get("healing/turn"), "turns_of_mana": axes.get("turns of mana"),
            "main_endurance": main}


# ----------------------------------------------------------------------------------- main
def specs_for(roles, only_class=None, only_spec=None):
    import sim_role_balance as R
    out = []
    for spec in sorted(R.SPEC_ROLES):
        if only_spec and spec != only_spec:
            continue
        if only_class and R.class_of(spec).lower() != only_class.lower():
            continue
        rs = R.roles_of(spec)
        if "dps" in roles and any(r in ("melee_dps", "ranged_dps") for r in rs):
            out.append((spec, "dps"))
        if "tank" in roles and "tank" in rs:
            out.append((spec, "tank"))
        if "healer" in roles and "healer" in rs:
            out.append((spec, "healer"))
    return out


def merge(passes):
    """Median and spread of every numeric field across passes."""
    out = {}
    for k in passes[0]:
        vals = [p[k] for p in passes if isinstance(p.get(k), (int, float))]
        if len(vals) == len(passes):
            med = statistics.median(vals)
            spread = (max(vals) - min(vals)) / med if med else 0.0
            out[k] = {"median": med, "spread": spread}
        else:
            out[k] = {"values": [p.get(k) for p in passes]}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="20,40,60")
    ap.add_argument("--gear", default="geared")
    ap.add_argument("--offsets", default="even")
    ap.add_argument("--roles", default="dps,tank,healer")
    ap.add_argument("--class", dest="only_class")
    ap.add_argument("--spec")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--fights", type=int, default=6)
    ap.add_argument("--out")
    ap.add_argument("--endurance-only", action="store_true",
                    help="only the main-spell mana endurance (fast; what calibrate_mana_costs targets)")
    args = ap.parse_args()

    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        cm = CreatureManager()
    levels = [int(x) for x in args.levels.split(",")]
    tiers = args.gear.split(",")
    offsets = args.offsets.split(",")
    roles = args.roles.split(",")
    specs = specs_for(roles, args.only_class, args.spec)
    cells = [(s, r, lv, g, o) for s, r in specs for lv in levels for g in tiers for o in offsets]
    print(f"{len(specs)} spec-roles x {len(levels)} levels x {len(tiers)} gear x {len(offsets)} offsets = "
          f"{len(cells)} cells, {args.passes} passes, {args.fights} fights each", flush=True)
    results = []
    t0 = time.time()
    for i, (spec, role, lv, tier, off) in enumerate(cells):
        runs = []
        for p in range(args.passes):
            seed = hash((spec, role, lv, tier, off, p)) & 0xFFFFFFFF
            random.seed(seed)
            rng = random.Random(seed)
            gen = LootGenerator()
            try:
                if args.endurance_only and role != "tank":
                    char = build(spec, role, lv, tier, gen)
                    runs.append({"main_endurance": main_endurance(char, role, cm, lv)})
                elif role == "dps":
                    runs.append(dps_cell(spec, lv, tier, off, args.fights, gen, cm, rng))
                elif role == "tank":
                    runs.append(tank_cell(spec, lv, tier, off, args.fights, gen))
                elif args.endurance_only:
                    char = build(spec, role, lv, tier, gen)
                    runs.append({"main_endurance": main_endurance(char, role, cm, lv)})
                else:
                    runs.append(healer_cell(spec, lv, tier, off, args.fights, gen, cm))
            except Exception as e:                              # noqa: BLE001
                runs.append({"error": f"{type(e).__name__}: {e}"})
        row = {"spec": spec, "role": role, "level": lv, "gear": tier, "offset": off,
               "passes": runs, "merged": merge(runs) if "error" not in runs[0] else None}
        results.append(row)
        print(f"  [{i + 1}/{len(cells)} {time.time() - t0:.0f}s] {line(row)}", flush=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(results, indent=1), encoding="utf-8")
        print(f"\nwrote {args.out}")
    return 0


def fmt(cell, key, pct=False, digits=1):
    v = (cell or {}).get(key)
    if v is None:
        return "-"
    if "values" in v:
        vals = v["values"]
        return str(vals[0]) if len(set(map(str, vals))) == 1 else "/".join(map(str, vals))
    m = v["median"]
    s = f"{m:.0%}" if pct else (f"{m:.{digits}f}" if m != float("inf") else "inf")
    return s + ("~" if v["spread"] > 0.25 and abs(m) > 0.05 else "")


def line(row):
    m = row["merged"]
    head = f"{row['spec']:<30} {row['role']:<6} L{row['level']:<2} {row['gear']:<6} {row['offset']:<5}"
    if m is None:
        return head + " ERROR " + str(row["passes"][0].get("error"))
    if "turns" not in m and "heal_per_turn" not in m and "turns_alive" not in m:
        return head + f" main-spell endurance {fmt(m, 'main_endurance', digits=0):>5}"
    if row["role"] == "dps":
        return (head + f" win {fmt(m, 'win', True):>5} hp {fmt(m, 'hp_left', True):>5} turns {fmt(m, 'turns'):>5}"
                f" mana/turn {fmt(m, 'mana_per_turn', digits=0):>5} fights/bar {fmt(m, 'fights_per_bar'):>5}"
                f" endurance {fmt(m, 'endurance', digits=0):>5} main {fmt(m, 'main_endurance', digits=0):>4}")
    if row["role"] == "tank":
        return head + f" alive {fmt(m, 'turns_alive'):>6} taken/turn {fmt(m, 'dmg_per_turn', digits=0):>5}"
    return (head + f" heal/turn {fmt(m, 'heal_per_turn', digits=0):>5} mana turns {fmt(m, 'turns_of_mana', digits=0):>4}"
            f" main {fmt(m, 'main_endurance', digits=0):>4}")


if __name__ == "__main__":
    sys.exit(main())
