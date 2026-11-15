"""THE WORLD CURVE: how much bigger everything is at each level. Monsters, characters, ranks and consumables
all read it, so a level-60 fight is the same shape as a level-10 one with much bigger numbers.

Kyle, 15 Nov 2026: "The lack of character progression is a very real problem. I know in wow each spell rank you
could FEEL like 'Oh shit! Now we're talking' - then it'd slowly taper off until the next one and you'd feel it
again....here it's piddly shit" and "Each spell rank or ability rank should FEEL like an actual step". He showed
Classic's Healing Touch: 40-55 at rank 1, 2,267-2,677 at 60 (and 25 mana -> 800). He picked "Steeper world".

Before this, a monster's health grew in a straight line, 1 + 0.15 per level: x10 from 1 to 60, and only +1.5% a
level at 60, so a rank learned six levels later could only be ~+13% and still keep fights 3-4 casts. Classic's
world grows fast early and keeps compounding: its ranks double early and land +20-25% late.

GROWTH(level): x1 at level 1, compounding by a per-level rate that eases from 13% at level 1 to 3.5% at 30 and
holds there. x2.2 at 8, x6 at 20, x10 at 30, x15 at 40, x20 at 50, x29 at 60 (Classic: Lightning Bolt 28x to 56,
Healing Touch ~50x to 60, a monster's health ~80x). A rank six levels on is +23% late, about +100% early.

WORLD_SCALE(level) = growth / the old straight line: what to multiply anything that was tuned on the old line by.
x1.0 at 1, x1.6 at 20, x2.1 at 40, x2.9 at 60. Applied to:
  - monsters and free-standing pets: health, attack and spell power, mana, and their kits' damage/heal/DoT amounts
    (entities/monster.py, entities/pet.py). Armour and resistances stay on the old line: they are mitigation, and
    a share should not change with the size of the numbers.
  - characters: max health and mana, attack/spell/healing power where combat reads them, the weapon roll, and
    regen (entities/character.py, combat/status_effects.py). So a monster's hit is the same share of your health,
    and your gear keeps its share of your damage.
  - ranks, at the level the rank is LEARNED (combat/ability_scaling.rank_multiplier): that is the step you feel when
    you train it, which then tapers as the monsters grow until the next rank.
  - potions, meals and drinks (entities/consumable.py).

FRONTIER_WORLD_CURVE=off puts everything back on the old straight line (for before/after sims).
"""
import os

R_START = 0.13          # growth per level at level 1
R_LATE = 0.035          # growth per level from KNEE on
KNEE = 30
OLD_SLOPE = 0.15        # the old straight line: 1 + 0.15 per level
MAX_LEVEL = 80

ENABLED = os.environ.get("FRONTIER_WORLD_CURVE", "").lower() != "off"


def _build():
    g = [1.0, 1.0]                       # index = level; level 0 reads as 1
    for lv in range(1, MAX_LEVEL):
        r = R_START + (R_LATE - R_START) * min(1.0, (lv - 1) / (KNEE - 1))
        g.append(g[-1] * (1 + r))
    return g


_G = _build()


def _lv(level):
    try:
        lv = int(level or 1)
    except (TypeError, ValueError):
        lv = 1
    return max(1, min(MAX_LEVEL, lv))


def old_line(level):
    return 1.0 + (_lv(level) - 1) * OLD_SLOPE


def growth(level):
    """How much bigger the world is at this level than at level 1."""
    if not ENABLED:
        return old_line(level)
    return _G[_lv(level)]


def world_scale(level):
    """Multiply anything tuned on the old straight line by this: x1 at level 1, x2.9 at 60."""
    if not ENABLED:
        return 1.0
    return _G[_lv(level)] / old_line(level)


def scale_of(entity):
    """world_scale at an entity's level (a character, monster or pet)."""
    return world_scale(getattr(entity, "level", 1))
