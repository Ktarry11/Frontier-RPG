#!/usr/bin/env python3
"""Every recruit's passive trait does something.

    python3 tools/qa_kit_passives.py [--list]

Kyle's backlog A [7]: "special traits that don't do what they say". Measured 13 Nov 2026: 44 of
the 67 recruits had at least one passive line that changed nothing. A kit passive only reached
the stat sheet, and half the keys are ones combat looks up by name - healing done, school
damage, pet damage and health, crit damage - so those never arrived. Six more keys had no
reader anywhere (spell pushback in a game with no cast times, coin find, threat, damage to
beasts, healing received).

Two checks, both on a really built character, one passive line at a time:
  * a stat-sheet line must move a number on the sheet;
  * a combat line must arrive in get_talent_effect at the authored size, and its key must be
    one this file proves the engine acts on (the tests at the bottom).
"""
import copy
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

KITS = ROOT / "data" / "npcs" / "personal_kits.json"
SCHOOLS = ("fire", "frost", "nature", "arcane", "shadow", "holy")


def sheet(ch):
    return {k: v for k, v in vars(ch).items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def main():
    import world.personal_kits as pk
    from world.recruit_manager import get_recruit_manager
    from world.creature_types import ALL
    from entities.monster import Monster

    doc = json.loads(KITS.read_text())
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict) else rm.recruits)}
    real_get_kit = pk.get_kit
    bad, lines = [], 0

    # ---- which combat keys the engine is proven to act on (tests below) ----
    proven = set(pk.COMBAT_KEYS) | {f"{s}_damage_pct" for s in SCHOOLS} | {f"{t}_damage_pct" for t in ALL}

    for kid, kit in doc.items():
        if kid.startswith("_"):
            continue
        r = recs.get(kid)
        if r is None:
            bad.append(f"{kit.get('name')}: no recruit {kid!r}")
            continue
        ch = r.build_character()
        passives = {k: v for k, v in kit["passives"].items()
                    if not k.startswith("_") and isinstance(v, (int, float)) and v}
        if not passives:
            bad.append(f"{kit['name']}: no passive at all")
        for key, value in passives.items():
            lines += 1
            def only(rid, _k=key, _v=value, _kid=kid, _kit=kit):
                if rid != _kid:
                    return real_get_kit(rid)
                c = copy.deepcopy(_kit)
                c["passives"] = {_k: _v} if _k else {}
                return c
            def none(rid, _kid=kid, _kit=kit):
                if rid != _kid:
                    return real_get_kit(rid)
                c = copy.deepcopy(_kit); c["passives"] = {}
                return c
            try:
                pk.get_kit = none
                ch._recalculate_derived_stats(); before = sheet(ch); t0 = ch.get_talent_effect(key, 0.0)
                pk.get_kit = only
                ch._recalculate_derived_stats(); after = sheet(ch); t1 = ch.get_talent_effect(key, 0.0)
            finally:
                pk.get_kit = real_get_kit
            if pk.is_combat_key(key):
                if abs((t1 - t0) - value / 100.0) > 1e-9:
                    bad.append(f"{kit['name']}: {key} {value} arrives in combat as {t1 - t0:g}, not {value / 100:g}")
                elif key not in proven:
                    bad.append(f"{kit['name']}: {key} - nothing in the engine is proven to act on it")
            elif before == after:
                bad.append(f"{kit['name']}: {key} {value} changes nothing on the sheet")
            elif "--list" in sys.argv:
                moved = [k for k in after if after[k] != before.get(k)]
                print(f"  {kit['name']:24s}{key:28s}{value:>6}  moves {', '.join(moved[:3])}")
        ch._recalculate_derived_stats()

    # ---- the engine acts on each combat key ----
    from combat.abilities import Ability
    someone = recs["alonso_pyromancer"].build_character()
    effects = {}
    real_effects = type(someone).get_talent_effects
    type(someone).get_talent_effects = lambda self: dict(effects) if self is someone else real_effects(self)
    beast = Monster("Mottled Boar", "beast_fast", 10)
    from world.creature_types import creature_type_of
    if creature_type_of(beast) != "beast":
        bad.append("harness: the boar is not a beast")
    try:
        def spell_school(a):
            try:
                real = a._resolve_damage_school(someone)
            except Exception:
                return None
            return real if isinstance(real, str) and real in SCHOOLS else None
        dmg = [a for a in someone.ability_book.get_all_abilities() if spell_school(a)]
        ab = dmg[0] if dmg else None
        if ab is None:
            bad.append("harness: no damaging ability to measure with")
        else:
            real = spell_school(ab)
            school = "spell"
            base = ab._damage_multiplier(someone, school)
            effects = {f"{real}_damage_pct": 0.10}
            if not ab._damage_multiplier(someone, school) > base:
                bad.append(f"engine: {real}_damage_pct does not raise {ab.name}'s damage")
            if beast is not None:
                effects = {"beast_damage_pct": 0.10}
                if not ab._damage_multiplier(someone, school, beast) > base:
                    bad.append("engine: beast_damage_pct does not raise damage to a beast")
                if ab._damage_multiplier(someone, school, someone) != base:
                    bad.append("engine: beast_damage_pct raises damage to a humanoid")
            effects = {}
            h0 = ab._damage_multiplier(someone, "healing")
            effects = {"healing_done": 0.10}
            if not ab._damage_multiplier(someone, "healing") > h0:
                bad.append("engine: healing_done does not raise healing")
        effects = {}
        someone.current_health = 1; someone.heal(100); plain = someone.current_health - 1
        effects = {"healing_received_pct": 0.25}
        someone.current_health = 1; someone.heal(100); more = someone.current_health - 1
        if not more > plain:
            bad.append(f"engine: healing_received_pct does not raise healing taken ({plain} -> {more})")

        class _E:                       # just enough of a combat engine to ask for its coin rule
            pass
        from combat.combat_engine import CombatEngine
        e = _E(); e.party = _E(); e.party.members = [someone]
        effects = {"gold_find_pct": 0.15}
        if abs(CombatEngine.coin_find_multiplier(e) - 1.15) > 1e-9:
            bad.append("engine: gold_find_pct does not raise coin from kills")
    finally:
        type(someone).get_talent_effects = real_effects
    for key, where in (("stun_duration_reduction_pct", "combat/status_effects.py"),
                       ("threat_generation_pct", "combat/combat_engine.py"),
                       ("pet_damage", "entities/pet.py"), ("pet_health", "entities/pet.py"),
                       ("crit_damage_physical", "combat/abilities.py"),
                       ("crit_damage_spell", "combat/abilities.py")):
        if f'"{key}"' not in (ROOT / where).read_text():
            bad.append(f"engine: {where} no longer reads {key}")

    print(f"{lines} passive lines on {len([k for k in doc if not k.startswith('_')])} recruits")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  " + b)
        return 1
    print("OK: every passive line does something")
    return 0


if __name__ == "__main__":
    sys.exit(main())
