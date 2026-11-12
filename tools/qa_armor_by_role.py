"""
Armour: ordinary gear gives modest reduction; only the three form tanks get a lot.

Kyle, 10 Nov: "DPS or healer shouldn't go over 40%" (mail DPS were at 52-53%). And 12 Nov, on
the measured table: "most tanks get DR from abilities and avoidance (block, dodge, parry). The
only things that should have high armor (even reaching cap) would be druid bears, venomancer
beetles, and bloodmage eternal form (as none of these forms can block OR parry)."

Every recruit, built as the game builds them, at 56-60:
  1. nobody in cloth, leather or mail without a shield is over 40% from their gear; armour
     TALENTS they spent points on can take them higher, but never past 55%
  2. the armour classes are in order: cloth < leather < mail < plate
  3. a plate tank with a shield is over 45% and under 60%: ahead of everyone in ordinary gear,
     and not living on armour
  4. the three form tanks, in form, are between 60% and the 75% cap - and above every
     shield tank
  5. nothing is over the cap, and the cap really is applied to damage taken
  6. monsters are on their old curve: the same armour mitigates exactly what it did
  7. the stat sheet's number is the number damage uses
"""
import os
import random
import statistics
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []
FORM_TANK_SPECS = {"venomancer_fortitude", "bloodmage_eternal", "druid_feral"}


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recruit_manager import get_recruit_manager
    from entities.character import Character
    random.seed(60)
    rm = get_recruit_manager()
    groups, by_name, shield_tanks = {}, {}, []
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=60)
        if c is None or c.armor < 300:
            continue
        by_name[c.name] = c
        chest = c.equipment.get_equipped("chest")
        off = c.equipment.get_equipped("off_hand")
        shield = bool(off and off.weapon_type == "shield")
        kind = chest.armor_type if chest else None
        red = c.get_physical_reduction_percent()
        spec = getattr(rec, "spec", "") or ""
        groups.setdefault((kind, shield), []).append(red)
        if kind in ("cloth", "leather", "mail") and not shield and spec not in FORM_TANK_SPECS:
            # "They CAN go higher if they deliberately stack armour, but it must not happen by
            # accident from normal gear." So the 40% line is drawn on what the GEAR gives; armour
            # talents the character spent points on are counted separately and held under 55%.
            spent = float((c.get_talent_effects() or {}).get("armor_pct", 0) or 0)
            from_gear = Character.armor_mitigation_from(c.armor / (1.0 + spent / 100.0), c.level) * 100.0
            check(from_gear <= 40.0, f"{c.name} ({c.char_class}, {kind}, {spec}): {from_gear:.0f}% from gear alone")
            check(red <= 55.0, f"{c.name} ({c.char_class}, {kind}, {spec}): {red:.0f}% with +{spent:.0f}% armour talents")
        if kind == "plate" and shield:
            shield_tanks.append(red)
            check(45.0 <= red <= 60.0, f"{c.name} (plate + shield): {red:.0f}% - want 45-60%")
        check(red <= 75.0 + 1e-6, f"{c.name}: {red:.1f}% is over the cap")
    check(len(by_name) >= 40, f"rig: only {len(by_name)} recruits")

    med = {k: statistics.median(v) for k, v in groups.items()}
    order = [med.get((k, False)) for k in ("cloth", "leather", "mail", "plate")]
    check(all(o is not None for o in order) and order == sorted(order) and len(set(order)) == 4,
          f"armour classes out of order: cloth/leather/mail/plate = {order}")

    # 4. form tanks, in form
    def in_form(name, how):
        c = by_name.get(name)
        if not check(c is not None, f"rig: no recruit called {name}"):
            return None
        how(c)
        c._recalculate_derived_stats()
        return c.get_physical_reduction_percent()

    def curse(c):
        ab = c.ability_book.get_ability("bloodmage_eternal_curse")
        ab.is_learned = True
        c.current_health = c.health
        ok, msg = ab.use(c, c)
        check(ok, f"rig: Eternal Curse would not cast ({msg})")

    forms = {
        "beetle (Callum Reid)": in_form("Callum Reid", lambda c: c.shift_form("beetle")),
        "eternal curse (Nicolás Arce)": in_form("Nicolás Arce", curse),
        "dire bear (a druid in leather)": in_form("Amber Whitehorse", lambda c: c.shift_form("dire_bear")),
    }
    top_shield = max(shield_tanks) if shield_tanks else 0
    for label, red in forms.items():
        if red is None:
            continue
        check(60.0 <= red <= 75.0, f"{label}: {red:.0f}% - a form tank should be 60-75%")
        check(red > top_shield, f"{label}: {red:.0f}% is not above the best shield tank ({top_shield:.0f}%)")

    # 5. the cap is applied to damage
    t = Character("T", "Warrior", 60)
    check(Character.armor_mitigation_from(10 ** 6, 60) == Character.ARMOR_REDUCTION_CAP, "the armour cap is not applied")
    # 6. monsters untouched
    check(abs(Character.mitigation_from(2300, 60) - 0.5) < 1e-9,
          "the shared (monster) curve moved: 2300 armour vs level 60 should still be 50%")
    check(Character.armor_mitigation_from(2300, 60) < 0.36, "players are not on their own curve")
    # 7. sheet == damage
    t.armor = 3000
    sheet = t.get_physical_reduction_percent() / 100.0
    check(abs(sheet - Character.armor_mitigation_from(3000, 60)) < 1e-9, "the stat sheet and the damage curve disagree")

    for (kind, shield), v in sorted(groups.items(), key=lambda kv: -statistics.median(kv[1])):
        print(f"   {str(kind):8} {'shield' if shield else '      '}  n={len(v):2}  {min(v):.0f}-{max(v):.0f}%  median {statistics.median(v):.0f}%")
    for label, red in forms.items():
        if red is not None:
            print(f"   {label}: {red:.0f}%")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:30]:
            print("  ", f)
        return 1
    print("armour by role OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
