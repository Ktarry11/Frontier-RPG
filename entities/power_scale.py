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

#: Item.power_scale on anything made after the change. 2: spell power and healing (15 Nov). 3: ratings.
CURRENT = 3

# ---------------------------------------------------------------------------------------------
# RATINGS (Kyle, 15 Nov, picking "WoW-style ratings"). Crit, hit, haste, dodge, parry, block, defense
# and the two penetrations were whole percents on items, and 1% cost 10 Intellect, so a gem's whole
# budget rounded to +1 at every tier and a rating only fitted on a big epic piece. Items now carry
# RATING points, RATING_PER_PCT to the percent: "+20 Crit Rating (2%)". The character turns them
# back into percent where item stats fold in (Character._recalculate_derived_stats), so combat
# reads the same numbers it always did. Talents, buffs and racials still say percent and are
# untouched.
# ---------------------------------------------------------------------------------------------
RATING_PER_PCT = 10
RATING_KEYS = frozenset({"crit_chance_physical", "crit_chance_spell", "hit_rating", "spell_hit_rating", "haste",
                         "dodge_rating", "dodge", "parry_rating", "block_rating", "defense_rating",
                         "armor_penetration_pct", "spell_penetration"})


def lift_rating(stat, value):
    """An old percent amount of a rating stat in rating points; anything else as it came."""
    if stat not in RATING_KEYS or not isinstance(value, (int, float)) or isinstance(value, bool):
        return value
    return whole(value * RATING_PER_PCT)


def ratings_to_percent(stats):
    """An item-sourced stat dict with its ratings turned back into percent (a new dict)."""
    out = dict(stats or {})
    for k in RATING_KEYS:
        if k in out and isinstance(out[k], (int, float)):
            out[k] = out[k] / RATING_PER_PCT
    return out


#: how an item's stat reads on a tooltip, a gem, an elixir or a recipe row
ITEM_LABELS = {
    "strength": "Strength", "agility": "Agility", "stamina": "Stamina", "intellect": "Intellect",
    "spirit": "Spirit", "spell_power": "Spell Power", "healing_power": "Healing Power",
    "attack_power": "Attack Power", "ranged_attack_power": "Ranged Attack Power",
    "fire_spell_power": "Fire Spell Power", "frost_spell_power": "Frost Spell Power",
    "arcane_spell_power": "Arcane Spell Power", "shadow_spell_power": "Shadow Spell Power",
    "nature_spell_power": "Nature Spell Power", "holy_spell_power": "Holy Spell Power",
    "mp5": "Mana per 5", "hp5": "Health per 5", "block_value": "Block Value", "armor": "Armor",
    "crit_chance_physical": "Crit Rating", "crit_chance_spell": "Spell Crit Rating",
    "hit_rating": "Hit Rating", "spell_hit_rating": "Spell Hit Rating", "haste": "Haste Rating", "dodge_rating": "Dodge Rating",
    "dodge": "Dodge Rating", "parry_rating": "Parry Rating", "block_rating": "Block Rating",
    "defense_rating": "Defense Rating", "armor_penetration_pct": "Armor Penetration Rating",
    "spell_penetration": "Spell Penetration",
}


def item_stat_label(stat):
    return ITEM_LABELS.get(stat, stat.replace("_", " ").title())


def item_stat_line(stat, value):
    """'+20 Crit Rating (2%)', '+64 Shadow Spell Power', '+19 Stamina'."""
    v = int(value) if isinstance(value, float) and value == int(value) else value
    line = f"+{v} {item_stat_label(stat)}"
    if stat in RATING_KEYS and stat not in ("spell_penetration", "defense_rating"):
        pct = value / RATING_PER_PCT
        line += f" ({pct:g}%)"
    return line


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
