"""
Equip proficiency rules.

WoW's model: armor types form a ladder, and a class can wear its own type
plus everything lighter. A Paladin (plate) may wear cloth, leather, mail and
plate; a Priest (cloth) may wear only cloth. Wearing below your type is legal
but a downgrade, because the lighter piece carries a much lower armor
multiplier - the item is equippable, just bad for you.

This matters now that loot rolls across the whole class pool rather than
being tailored to the player (see LootGenerator._roll_target_class). Without
a restriction layer a Priest could equip a plate chest and out-tank a
Warrior; without allowing *lighter* armor, most drops would be dead weight.

WEAPON PROFICIENCY
-------------------
Weapons previously had NO restriction at all - every weapon_type sat in
UNRESTRICTED_ARMOR_TYPES, so a Druid could equip a two-handed axe and a
Priest could equip a shield. Unlike armor, weapon proficiency is NOT a
ladder (there's no "lighter weapon" concept) - it's a fixed per-class list
of weapon_type ids from data/items/weapon_types.json's class_weapon_map.
An unlisted weapon_type is simply not equippable by that class, full stop.
"""

#: Light to heavy. Index position is the proficiency level.
ARMOR_LADDER = ["cloth", "leather", "mail", "plate"]

#: Armor types that carry no restriction at all - anyone can equip them.
#: NOTE: "weapon" no longer means "unrestricted" - weapon_type restriction
#: is handled separately by can_wear_weapon_type() below. This set only
#: covers non-weapon slots that have no armor-ladder concept (accessories).
UNRESTRICTED_ARMOR_TYPES = {"accessory", None, ""}


def _load_class_armor_map():
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent / "data" / "items" / "armor_types.json"
    try:
        with open(path, "r") as f:
            return json.load(f).get("class_armor_map", {})
    except Exception:
        return {}


def _load_class_weapon_map():
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent / "data" / "items" / "weapon_types.json"
    try:
        with open(path, "r") as f:
            return json.load(f).get("class_weapon_map", {})
    except Exception:
        return {}


def get_class_armor_type(char_class):
    """The heaviest armor type a class is proficient in (e.g. Paladin -> plate)."""
    return _load_class_armor_map().get(char_class, "cloth")


def can_wear_armor_type(char_class, armor_type):
    """True if `char_class` may equip an item of `armor_type`."""
    if armor_type in UNRESTRICTED_ARMOR_TYPES:
        return True

    armor_type = str(armor_type).lower()
    if armor_type not in ARMOR_LADDER:
        # Unknown//custom armor type - don't block on data we don't understand.
        return True

    class_type = str(get_class_armor_type(char_class)).lower()
    if class_type not in ARMOR_LADDER:
        return True

    return ARMOR_LADDER.index(armor_type) <= ARMOR_LADDER.index(class_type)


def can_wear_weapon_type(char_class, weapon_type):
    """True if `char_class` may equip a weapon of `weapon_type`.

    Unlike armor, this is a flat allow-list per class (data/items/
    weapon_types.json's class_weapon_map), not a ladder - there's no
    "lighter weapon" fallback the way cloth is a legal downgrade from
    plate. A class simply can or can't use a given weapon_type.

    A class missing from class_weapon_map (data gap, not a design choice)
    fails open rather than silently blocking every weapon - a data key
    that hasn't been authored yet shouldn't brick equipping for that class.
    """
    if weapon_type in (None, ""):
        return True
    class_map = _load_class_weapon_map()
    if char_class not in class_map:
        return True
    return weapon_type in class_map[char_class]


def can_equip(character, item):
    """
    Full equip check. Returns (allowed: bool, reason: str).

    `reason` is empty when allowed, and otherwise a short player-facing string
    the inventory UI can surface in the tooltip.
    """
    armor_type = getattr(item, "armor_type", None)
    if not can_wear_armor_type(character.char_class, armor_type):
        display = str(armor_type).capitalize()
        return False, f"{character.char_class} cannot equip {display}"

    weapon_type = getattr(item, "weapon_type", None)
    if not can_wear_weapon_type(character.char_class, weapon_type):
        display = weapon_type
        try:
            import json
            from pathlib import Path
            path = Path(__file__).parent.parent / "data" / "items" / "weapon_types.json"
            with open(path, "r") as f:
                wt_data = json.load(f)["weapon_types"]
            display = wt_data.get(weapon_type, {}).get("display_name", weapon_type)
        except Exception:
            pass
        return False, f"{character.char_class} cannot equip {display}"

    required_level = getattr(item, "required_level", 0) or 0
    if character.level < required_level:
        return False, f"Requires level {required_level}"

    return True, ""


def is_suboptimal(character, item):
    """
    True if the item is equippable but below the character's armor class -
    e.g. a Warrior in leather. Used to grey out / warn in tooltips rather
    than to block.
    """
    armor_type = str(getattr(item, "armor_type", None) or "").lower()
    if armor_type not in ARMOR_LADDER:
        return False
    class_type = str(get_class_armor_type(character.char_class)).lower()
    if class_type not in ARMOR_LADDER:
        return False
    return ARMOR_LADDER.index(armor_type) < ARMOR_LADDER.index(class_type)
