#!/usr/bin/env python3
"""What dodge, parry, block and crit does a real character actually have?

    PYTHONPATH=. python3 tools/audit_avoidance_and_crit.py

Kyle, 7 Nov, with a screenshot of Tarek Mansour - a melee DPS recruit, level
26, in greens - reading Dodge 32.25%, Parry 29.25%, Crit (phys) 42.5%:

    "we need to turn down avoidance. a tank should struggle to reach 40%
     avoidance before lvl 60 bro! This fucker has so much"
    "more block chance, lower dodge and parry unless you stack agi then you
     can have higher dodge."
    "crit is quite high as crit shouldnt go over 50% even on a really geared
     character"
    "these guys are lvl 26 in greens."

THE SHAPE OF THE BUG IS THE ONE THIS CODEBASE KEEPS HAVING: a scale moved and
the numbers authored against the old one stayed. Every primary-stat conversion
in _recalculate_derived_stats is a FLAT per-point rate with no level term:

    crit_physical = agility * 0.5
    dodge         = 5 + agility * 0.25
    parry         = (strength + agility) / 2 * 0.2

85 Agility is therefore 42.5% crit on its own, which is exactly the number on
Kyle's screen - the gear and the talents contributed nothing to it. There is
no cap anywhere on crit, and the dodge/parry caps that do exist (60% combined)
sit so far above where a level-26 character lands that they never engage.

Flat conversion is also what WoW does NOT do, and for this reason: a primary
stat is the thing that grows fastest with level and with gear, so pinning a
percentage to it with a constant makes the percentage grow without limit. In
Classic the Agility needed per 1% crit RISES with level - roughly 12 per point
at 20, roughly 20 at 60 - so the same item is strong when you find it and
ordinary later, and 60 is where the numbers are tuned.

This tool measures, it does not fix. It builds real Characters through the
same path the game does, at the levels that matter, with and without gear, and
prints what each conversion is actually paying.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

LEVELS = (10, 26, 40, 60)

#: One per archetype, chosen for what they stack rather than for lore.
#: shield=True forces an off-hand shield, because block chance is zero
#: without one and the first run of this tool reported 0.0% block for both
#: tanks purely because the random generator handed them a second weapon.
SUBJECTS = [
    ("Warrior", True, "plate tank, stacks Strength and Stamina"),
    ("Paladin", True, "plate tank with a shield"),
    ("Rogue", False, "leather, stacks Agility - the dodge case Kyle wants rewarded"),
    ("Hunter", False, "mail, stacks Agility"),
    ("Mage", False, "cloth, stacks Intellect - the spell-crit case"),
]


def _build(char_class, level):
    from entities.character import Character
    return Character(name="Subject", char_class=char_class, level=level)


def _gear_up(actor, rarity="uncommon", shield=False):
    """Fill every slot with generated gear of the character's own level.

    'greens' in Kyle's message means uncommon, which is what the world
    actually drops while levelling - the audit has to measure the same thing
    he was looking at, not a naked character.
    """
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    filled = 0
    for slot in list(actor.equipment.slots or {}):
        try:
            item = gen.generate_item_for_class(actor.char_class, actor.level,
                                               slot=slot, rarity=rarity)
        except Exception:
            item = None
        if item is None:
            continue
        # equip_item requires the item to be IN INVENTORY first and returns
        # False rather than raising if it is not - which is how the first
        # run of this tool reported a naked level-60 Rogue and called it
        # "in greens". An audit that silently measures nothing is worse than
        # no audit, so the count is returned and asserted by the caller.
        actor.inventory.append(item)
        if actor.equip_item(item):
            filled += 1
        else:
            actor.inventory.remove(item)
    if shield:
        try:
            sh = gen.generate_item_for_class(actor.char_class, actor.level,
                                             slot="off_hand", rarity=rarity,
                                             weapon_type="shield")
            actor.inventory.append(sh)
            if not actor.equip_item(sh):
                actor.inventory.remove(sh)
        except Exception:
            pass
    return filled


def _row(actor):
    return dict(
        agi=round(getattr(actor, "agility", 0)),
        str_=round(getattr(actor, "strength", 0)),
        int_=round(getattr(actor, "intellect", 0)),
        dodge=getattr(actor, "dodge", 0.0),
        parry=getattr(actor, "parry", 0.0),
        block=getattr(actor, "block_chance", 0.0),
        critp=getattr(actor, "crit_chance_physical", 0.0),
        crits=getattr(actor, "crit_chance_spell", 0.0),
        armor=getattr(actor, "armor", 0),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rarity", default="uncommon",
                    help="gear rarity to equip (default uncommon, i.e. greens)")
    args = ap.parse_args()

    print(__doc__.split("This tool measures")[0].strip()[:0] or "", end="")
    print(f"  Every slot filled with generated {args.rarity} gear of the "
          f"character's own level.\n")

    header = (f"  {'class':10}{'lvl':>4}{'agi':>5}{'str':>5}{'int':>5}"
              f"{'dodge':>8}{'parry':>8}{'avoid':>8}{'block':>8}"
              f"{'crit-p':>8}{'crit-s':>8}")
    worst = {"avoid": (0, ""), "critp": (0, ""), "crits": (0, "")}

    for char_class, shield, why in SUBJECTS:
        print(f"  -- {char_class}  ({why})")
        print(header)
        for level in LEVELS:
            actor = _build(char_class, level)
            worn = _gear_up(actor, args.rarity, shield=shield)
            if worn < 8:
                print(f"  {'':10}{level:>4}  only {worn} slots equipped - "
                      f"this row is not measuring geared stats")
            r = _row(actor)
            avoid = r["dodge"] + r["parry"]
            tag = f"{char_class} {level}"
            if avoid > worst["avoid"][0]:
                worst["avoid"] = (avoid, tag)
            if r["critp"] > worst["critp"][0]:
                worst["critp"] = (r["critp"], tag)
            if r["crits"] > worst["crits"][0]:
                worst["crits"] = (r["crits"], tag)
            print(f"  {'':10}{level:>4}{r['agi']:>5}{r['str_']:>5}{r['int_']:>5}"
                  f"{r['dodge']:>7.1f}%{r['parry']:>7.1f}%{avoid:>7.1f}%"
                  f"{r['block']:>7.1f}%{r['critp']:>7.1f}%{r['crits']:>7.1f}%")
        print()

    print("  -- against Kyle's targets ----------------------------------")
    a, who = worst["avoid"]
    print(f"  highest dodge+parry   {a:5.1f}%  ({who})"
          f"   target: under 40% before 60")
    c, who = worst["critp"]
    print(f"  highest physical crit {c:5.1f}%  ({who})"
          f"   target: never over 50%")
    c, who = worst["crits"]
    print(f"  highest spell crit    {c:5.1f}%  ({who})"
          f"   target: never over 50%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
