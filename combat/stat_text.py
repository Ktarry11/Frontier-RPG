"""How one stat modifier reads, everywhere it is shown.

Kyle, of *Hasten*: "Haste +15%" on the spell and "Haste +15" on the buff. There were THREE
formatters - the ability tooltip, the buff/debuff hover and the combat log - each with its own
idea of which stats are percentages, so the same +5 crit read "Crit Chance Physical +5" on the
spell and "+5% Physical Crit" on the buff it applied, and a -0.4 damage-taken fraction read
"-40%" in one place and "-0.4" in another. Measured: 8 of the 64 stat keys in the game
disagreed about the % sign alone.

One function decides the LABEL, the UNIT and the NUMBER. The callers still choose the order
("Haste +15%" in a sentence, "+15% Haste" in a list) because that is layout, not meaning.
"""

#: Names a player would recognise. Anything not here is the key with its underscores removed.
LABELS = {
    "attack_power": "Attack Power", "ranged_attack_power": "Ranged Attack Power",
    "spell_power": "Spell Power", "healing_power": "Healing Power", "armor": "Armor",
    "magic_resistance": "Magic Resistance", "strength": "Strength", "stamina": "Stamina",
    "intellect": "Intellect", "spirit": "Spirit", "agility": "Agility",
    "crit_chance_physical": "Physical Crit", "crit_chance_spell": "Spell Crit",
    "crit_chance": "Crit", "hit_rating": "Hit Chance", "hit_chance_physical": "Physical Hit",
    "hit_chance_spell": "Spell Hit", "parry": "Parry", "dodge": "Dodge", "block": "Block",
    "haste": "Haste", "max_health_pct": "Maximum health", "max_mana_pct": "Maximum mana",
    "damage_taken_pct": "Damage taken", "physical_damage_taken_pct": "Physical damage taken",
    "magic_damage_taken_pct": "Magic damage taken", "damage_dealt_pct": "Damage dealt",
    "healing_done_pct": "Healing done", "healing_taken_pct": "Healing received",
    "threat_generation_pct": "Threat", "all_ability_cost_pct": "Ability costs",
    "mp5": "Mana per turn", "hp5": "Health per turn",
    "cc_immune": "Immune to crowd control", "forced_front": "Dragged into the front row",
    "forced_back": "Standing in the back row",
    "taunt": "Forces the target to attack you",
}

#: States, not magnitudes: the number is always 1 and printing it says nothing.
FLAGS = ("cc_immune", "taunt", "forced_front", "forced_back")

#: A stat whose number is a percentage even though its name does not end _pct.
_PERCENT_WORDS = ("crit", "dodge", "parry", "haste", "hit")


def label_for(key):
    return LABELS.get(key) or key.replace("_pct", "").replace("_", " ").title()


def is_percent(key):
    """True if this stat's number is a percentage."""
    if key.endswith("_pct"):
        return True
    if key.endswith("_value") or key.endswith("_rating") and key != "hit_rating":
        return False                       # block_value is points; so is defense_rating
    return key == "block" or any(word in key for word in _PERCENT_WORDS)


def amount(key, value):
    """(sign, number as text, unit) for a stat value.

    *_pct keys carry both conventions in this game's data - a fraction below 1, a whole
    percentage at or above it - so the magnitude decides which, the same test the engine uses.
    all_ability_cost_pct is the one key whose POSITIVE value is a REDUCTION, so its sign is
    turned round for the reader: a 30% discount must not read as a 30% surcharge.
    """
    mag = abs(value)
    if key.endswith("_pct") and (mag < 1 or (key == "all_ability_cost_pct" and mag <= 1)):
        mag *= 100
    negative = value < 0
    if key == "all_ability_cost_pct":
        negative = not negative
    number = f"{round(mag, 1):g}"
    return ("-" if negative else "+"), number, ("%" if is_percent(key) else "")


def stat_text(key, value, value_first=False):
    """'Haste +15%' - or '+15% Haste' with value_first."""
    label = label_for(key)
    if key in FLAGS:
        return label
    sign, number, unit = amount(key, value)
    return f"{sign}{number}{unit} {label}" if value_first else f"{label} {sign}{number}{unit}"
