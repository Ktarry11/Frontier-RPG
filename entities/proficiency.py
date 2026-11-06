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


def _load_weapon_types():
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent / "data" / "items" / "weapon_types.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def is_one_handed_weapon(weapon_type):
    """True for a weapon that can sit in either hand (hand == main_or_off).

    Shields and tomes are hand == "off_hand" and are NOT one-handed weapons
    for dual-wield purposes - holding a shield has never been dual-wielding.
    """
    if weapon_type in (None, ""):
        return False
    types = _load_weapon_types().get("weapon_types", {})
    return types.get(weapon_type, {}).get("hand") == "main_or_off"


def active_spec(character):
    """The spec slug the character has invested most heavily in, or None.

    WoW's own convention: your spec is whichever tree holds the most points.
    Derived rather than stored, because Character has no spec field - it has
    talent_trees keyed by spec slug, each with total_points_spent().

    A LOCKED SPEC IS THE ANSWER OUTRIGHT, points or not. Companions are
    authored as one spec and locked to it (world/recruit_manager.py sets
    locked_spec, and ui/screens/talent_tree_screen.py refuses to spend
    outside it) - "these are real people", so Dan is a Fury Warrior whether
    or not anybody has opened his tree yet. Deriving from points alone meant
    a freshly built companion had NO spec for a moment, and every spec-gated
    rule failed closed on her: a level 38 Felsworn Slayer and a level 41
    Witch Hunter Inquisitor were both refused their off-hand weapon, because
    _equip_starter_gear runs before auto_spend_talents and can_dual_wield
    asked a character with an empty tree what she specced into.
    """
    locked = getattr(character, "locked_spec", None)
    if locked:
        return locked
    trees = getattr(character, "talent_trees", None) or {}
    best, best_points = None, 0
    for slug, tree in trees.items():
        try:
            points = tree.total_points_spent()
        except Exception:                                      # noqa: BLE001
            continue
        if points > best_points:
            best, best_points = slug, points
    return best


def dual_wield_level(character):
    """The level at which this character's class trains dual wield, or 0 if
    the class never can. Lets can_equip say "requires level 20" rather than
    "cannot dual wield" to someone who is simply not there yet."""
    entry = _load_weapon_types().get("dual_wield", {}).get(
        getattr(character, "char_class", None))
    if entry is None:
        return 0
    return entry.get("min_level", 0) if isinstance(entry, dict) else 0


def can_dual_wield(character):
    """True if this character may hold a one-handed weapon in the off-hand.

    Dual-wielding had NO restriction of any kind before 29 Oct 2026. Nothing
    in the game modelled it: can_equip checked the weapon TYPE but never the
    SLOT, so any class with dagger proficiency - eighteen of them - could put
    a dagger in its off-hand, and LootGenerator would roll `main_or_off`
    weapon types into the off_hand slot for anyone, so a Priest could be
    handed an off-hand sword by a normal drop.

    Kyle, 29 Oct: "we ALSO need to restrict dual wielding to the right
    classes." The allow-list lives in data/items/weapon_types.json's
    dual_wield key - vanilla's Rogue, Fury Warrior and Enhancement Shaman,
    plus the CoA classes and specs built for it.

    Spec-gated where the design is spec-gated, because that is how both WoW
    and CoA describe it: Fury dual-wields and Arms does not, Runemaster's
    Engravement "explicitly unlocks dual-wielding", Reaper's Harvest "gains
    the ability to". A character with no talent points spent has no spec yet,
    so a spec-gated class is not permitted until it commits - which matches
    dual wield being a thing you train into rather than start with.

    LEVEL-GATED, because dual wield is trained rather than innate: in Classic
    Warrior, Rogue and Hunter all learn it at 20 (Kyle, 29 Oct: "let hunters
    DW at 20"). Applied uniformly at 20 so a level-10 Brutality Barbarian
    cannot dual-wield while a Warrior waits.

    A class absent from dual_wield cannot dual-wield at all. This one fails
    CLOSED, unlike can_wear_weapon_type: an unauthored key here would
    silently restore the free-for-all this exists to stop.
    """
    table = _load_weapon_types().get("dual_wield", {})
    entry = table.get(getattr(character, "char_class", None))
    if entry is None:
        return False

    # Accepts the older shape ("all" or a bare spec list) as well as the
    # current {"specs": ..., "min_level": N}, so a half-migrated data file
    # degrades to "no level gate" rather than raising mid-equip.
    if isinstance(entry, dict):
        specs, min_level = entry.get("specs", "all"), entry.get("min_level", 0)
    else:
        specs, min_level = entry, 0

    if (getattr(character, "level", 0) or 0) < min_level:
        return False
    if specs == "all":
        return True
    return active_spec(character) in set(specs)


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
    # A NON-WEAPON CARRIES NO PROFICIENCY. Kyle, 29 Oct 2026: "Tome is just
    # offhand right? It's not a 'weapon' think of actual wow." Right - a tome
    # is a Held In Off-hand item, and in WoW those have no class restriction
    # at all; any class can hold one, it is simply useless to a melee. The
    # class_weapon_map entry for a non-weapon is kept as a loot-TARGETING
    # hint (who it should drop for) and does not gate equipping.
    types = _load_weapon_types().get("weapon_types", {})
    if types.get(weapon_type, {}).get("non_weapon"):
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

    # DUAL WIELD. Checked here because this is the only equip gate that sees
    # both the character and the item; Equipment has no owner and derives the
    # slot from item.slot, so it cannot ask who is equipping. A shield or a
    # tome in the off-hand is not dual-wielding - only a one-handed WEAPON is
    # (is_one_handed_weapon keys on hand == "main_or_off").
    if getattr(item, "slot", None) == "off_hand" and is_one_handed_weapon(weapon_type):
        if not can_dual_wield(character):
            # Distinguish "not yet" from "never". A Hunter at 19 is three
            # quests from dual wielding and a Priest never will, and one
            # message for both reads as a bug to the player.
            needed = dual_wield_level(character)
            if needed and (getattr(character, "level", 0) or 0) < needed:
                return False, f"Dual wield requires level {needed}"
            return False, f"{character.char_class} cannot dual wield"

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
