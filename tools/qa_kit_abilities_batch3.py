"""
Seven more recruit signature abilities, each held to its own text.

Kyle, 12 Nov: "For dead keys (character recruit abilities) we should ensure they do what they
say."

Five did nothing beyond a plain hit or heal and now have the mechanic they describe:
  Ama Boateng      The Arithmetic                   heals more the lower the target, to double
  Bashir Khalidi   Taking Something Apart Correctly +20% per 25% of health the target is missing
  Tomas Havel      Heavy Things Through Small Gaps  ignores 60% of the target's armour
  Imelda Salonga   She Hits Things and Her People Get Better   heals the most wounded ally for 80%
  Giorgi Beridze   Bringing the Herd Down           every enemy counts as front row for 2 turns

Two were marked broken and are not:
  Pavlo Hryn       By Presence Alone                the party cannot be stunned for 3 turns
  Freja Lindqvist  The First Ninety Seconds         raises a fallen ally at 25% (the "within two
                                                    turns" clause is gone from its text)
"""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recruit_manager import get_recruit_manager
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    from combat import rows
    from combat.status_effects import StatusEffect, EffectType
    rm = get_recruit_manager()
    built = {}
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=60)
        if c is not None:
            built[c.name] = c
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
    by_name = {a["name"]: a for k in kits.values() if isinstance(k, dict) for a in (k.get("abilities") or [])}

    def kit(who, title):
        c = built.get(who)
        entry = by_name.get(title)
        if not check(c is not None and entry is not None, f"rig: no {who} / {title}"):
            return None, None
        ab = c.ability_book.get_ability(entry["ability_id"])
        if not check(ab is not None, f"rig: {who} does not have {title}"):
            return c, None
        ab.is_learned = True
        ab.turns_remaining = 0
        c.current_health = c.health
        for attr in ("current_mana", "current_energy", "current_rage", "current_focus"):
            if hasattr(c, attr):
                setattr(c, attr, 10 ** 5)
        check(not str(entry.get("engine", "")).startswith("needs"), f"{title} is still marked {entry.get('engine')!r}")
        return c, ab

    def mob(row="front", armor=None):
        m = Monster("Mottled Boar", "beast_basic", level=60)
        m.row = row
        m.health = m.current_health = 10 ** 6
        if armor is not None:
            m.armor = armor
        return m

    def average(fn, n=60):
        random.seed(11)
        return sum(fn() for _ in range(n)) / n

    def hit(c, ab, m):
        before = m.current_health
        ab.turns_remaining = 0
        ab.use(c, m, party=[c], free=True)
        return before - m.current_health

    # --- Ama: the heal grows as the target sinks ------------------------------------------
    c, ab = kit("Ama Boateng", "The Arithmetic")
    friend = built.get("Tomas Havel")
    if ab and friend:
        def healed(at):
            friend.current_health = max(1, int(friend.health * at))
            before = friend.current_health
            ab.turns_remaining = 0
            ab.use(c, friend, party=[c, friend], free=True)
            return friend.current_health - before
        # measured on a target with room to take the whole heal either way
        friend.health = max(friend.health, 10 ** 5)
        high = average(lambda: healed(0.90))
        low = average(lambda: healed(0.05))
        check(low > high * 1.6, f"The Arithmetic healed {low:.0f} at 5% health and {high:.0f} at 90% - "
                                f"it should be close to double")
        check(low < high * 2.2, f"The Arithmetic healed {low:.0f} at 5% against {high:.0f} at 90% - more than double")
        check(not any(e.effect_id == "_cast_rider" for e in c._effects()),
              "The Arithmetic left its one-cast bonus on Ama after the cast")
        friend._recalculate_derived_stats()

    # --- Bashir: +20% per quarter missing -------------------------------------------------
    c, ab = kit("Bashir Khalidi", "Taking Something Apart Correctly")
    if ab:
        m = mob()

        def at(frac):
            m.current_health = int(m.health * frac)
            return hit(c, ab, m)
        full = average(lambda: at(1.0))
        half = average(lambda: at(0.5))
        check(1.25 < half / max(1, full) < 1.55,
              f"Taking Something Apart: {half:.0f} at half health against {full:.0f} at full - expected about +40%")

    # --- Tomas: ignores 60% of armour -----------------------------------------------------
    c, ab = kit("Tomas Havel", "Heavy Things Through Small Gaps")
    if ab:
        pen = c.armor_penetration_pct
        bare, plated = mob(armor=0), mob(armor=6000)
        through = average(lambda: hit(c, ab, plated))
        clean = average(lambda: hit(c, ab, bare))
        ab.armor_ignore_pct = 0
        blocked = average(lambda: hit(c, ab, plated))
        ab.armor_ignore_pct = 60
        check(blocked < clean * 0.9, "rig: 6000 armour did not reduce Tomas's swing, so nothing is measured")
        check(through > blocked * 1.15, f"Heavy Things did {through:.0f} through armour with the rider and "
                                        f"{blocked:.0f} without - it is not ignoring armour")
        check(through <= clean * 1.02, "Heavy Things did more through armour than against none")
        check(c.armor_penetration_pct == pen, "Heavy Things left Tomas's armour penetration raised after the swing")

    # --- Imelda: 80% of the damage heals the most wounded ally ----------------------------
    c, ab = kit("Imelda Salonga", "She Hits Things and Her People Get Better")
    a1, a2 = built.get("Ama Boateng"), built.get("Pavlo Hryn")
    if ab and a1 and a2:
        m = mob()
        a1.current_health = int(a1.health * 0.9)
        a2.current_health = max(1, int(a2.health * 0.2))
        h1, h2 = a1.current_health, a2.current_health
        before = m.current_health
        ok, msg = ab.use(c, m, party=[c, a1, a2], free=True)
        dealt = before - m.current_health
        got = a2.current_health - h2
        check(ok and dealt > 0, f"She Hits Things did no damage ({msg})")
        room = a2.health - h2
        check(abs(got - min(room, dealt * 0.8)) <= max(2, dealt * 0.05),
              f"She Hits Things dealt {dealt:.0f} and healed the most wounded ally for {got:.0f}; 80% is {dealt * 0.8:.0f}")
        check(a1.current_health == h1, "She Hits Things healed the wrong ally")
        a2.current_health = 0
        ab.turns_remaining = 0
        ab.use(c, m, party=[c, a1, a2], free=True)
        check(a2.current_health == 0, "She Hits Things raised the dead")
        a1.current_health, a2.current_health = a1.health, a2.health

    # --- Giorgi: everyone into the front row ----------------------------------------------
    c, ab = kit("Giorgi Beridze", "Bringing the Herd Down")
    if ab:
        back, front = mob(row="back"), mob(row="front")
        eng = CombatEngine(c, front, party=Party(c), enemies=[front, back])
        eng.current_actor = c
        check(rows.row_of(back) == "back", "rig: the back-row boar is not in the back row")
        ok, msg = eng.execute_ability(c, ab.ability_id, front)
        check(ok, f"Bringing the Herd Down would not cast ({msg})")
        check(rows.row_of(back) == "front", "Bringing the Herd Down left a back-row enemy in the back row")
        check(back.row == "back", "Bringing the Herd Down rewrote the enemy's own row, so it will never go back")
        for _ in range(4):
            back.tick_status_effects()
        check(rows.row_of(back) == "back", "the enemy did not return to the back row when the effect ended")

    # --- Pavlo: the party cannot be stunned ------------------------------------------------
    c, ab = kit("Pavlo Hryn", "By Presence Alone")
    if ab and a1:
        ab.use(c, [c, a1], party=[c, a1], free=True)
        a1.apply_status_effect(StatusEffect("t_stun", "Stun", EffectType.DEBUFF, 2, is_stun=True,
                                            real_time_seconds=None))
        check(not a1.is_stunned, "By Presence Alone: an ally was stunned while it held")
        a1.clear_combat_effects()
        c.clear_combat_effects()

    # --- Freja: raises the fallen at a quarter health -------------------------------------
    c, ab = kit("Freja Lindqvist", "The First Ninety Seconds")
    if ab and a1:
        a1.current_health = 0
        ok, msg = ab.use(c, a1, party=[c], free=True)
        check(ok and a1.is_alive(), f"The First Ninety Seconds did not raise the fallen ({msg})")
        check(abs(a1.current_health - a1.health * 0.25) <= 2,
              f"The First Ninety Seconds raised at {a1.current_health}/{a1.health}, not 25%")
        check("two turns" not in by_name["The First Ninety Seconds"]["description"],
              "The First Ninety Seconds still promises a two-turn window that nothing enforces")
        a1.current_health = a1.health

    if fails:
        print(f"{len(fails)} problem(s):")
        for f in fails:
            print("  -", f)
        return 1
    print("kit abilities batch 3 OK - seven more recruit abilities do what they say.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
