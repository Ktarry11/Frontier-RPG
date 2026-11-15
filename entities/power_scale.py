"""Spell power and healing on the item scale Kyle set, with combat kept where it was.

Kyle, 14 Nov 2026: "Make AP, sp, healing power cheaper. Should be 2AP is 1 str or 1 agi. 1 int = 1.5 sp
=2 Healing." So an item's budget buys 1.5 spell power or 2 healing for every point of Intellect it could
have had (data/items/gear_suffixes.json stat_budget_costs), and a single school's power about 1.8,
since it only helps one school. The numbers on gear came out bigger, like WoW's: a robe's spell power
is its headline.

He chose to keep combat the same ("Keep combat the same"), so nothing hits harder for it:
  - everything that adds spell power or healing to a character is on the ITEM scale: gear, gems,
    enchants, set bonuses and elixirs carry the bigger numbers, and talents, buffs, forms and racials
    (written on the old scale) are lifted into it where they fold in;
  - combat reads them back through COMBAT (character.get_effective_spell_power, combat_healing_power),
    which divides the lift out again. So a spell does exactly what it did before the change.
Old saves: an item saved before this has its power lifted once, on load (Item.from_dict).
"""
from entities.item import whole

#: what one old point is worth on the item scale: the old cost over the new one
SPELL = 1.25 / (2 / 3)          # 1.875
HEALING = 1.25 / 0.5            # 2.5
SCHOOL = 1.0 / 0.55             # about 1.82
SCHOOLS = ("fire", "frost", "arcane", "shadow", "nature", "holy")

LIFT = {"spell_power": SPELL, "healing_power": HEALING}
LIFT.update({f"{s}_spell_power": SCHOOL for s in SCHOOLS})

#: Item.power_scale on anything made after the change
CURRENT = 2


def lift(stat, value):
    """An old-scale amount of `stat` on the item scale. Anything that isn't spell power or healing is
    returned as it came."""
    k = LIFT.get(stat)
    if k is None or not isinstance(value, (int, float)) or isinstance(value, bool):
        return value
    return whole(value * k)


def lift_all(stats):
    """A stat dict with its spell power and healing lifted (a new dict)."""
    return {s: lift(s, v) for s, v in (stats or {}).items()}


def combat(stat, value):
    """An item-scale amount back on the scale combat's coefficients were tuned for."""
    k = LIFT.get(stat)
    return value / k if k else value
