"""
Starting gear. Grants every new character one white (common-rarity,
armor-only, no-stat - per Kyle's Gear.docx convention) weapon, a ranged
item if their class's weapon is itself ranged, and chest/legs/feet armor
in the correct armor_type for that class.

Kyle's ask (2026-09-06): "This should just be general white weapon,
ranged if needed and a chest piece, pants, and boots." A level-1
character previously started with all 16 equipment slots completely
empty - no weapon, no armor anywhere - which felt bad walking into the
very first fight, especially now that Shoot/Wand are correctly
hard-blocked without a matching weapon equipped (see
combat/combat_engine.py's execute_ability) rather than just greyed out.

Armor type per class and stat_template per class are NOT re-defined here -
data/items/armor_types.json's class_armor_map and
data/items/stat_templates.json's class_stat_template_map already own
that mapping (LootGenerator.generate_item_for_class reads the exact same
two files), so this module reuses them rather than maintaining a second,
inevitably-drifting copy. The only new data this module adds is
CLASS_WEAPON_TYPE - what weapon a class starts with - which isn't
tracked anywhere else.
"""
import json
import uuid
from pathlib import Path

from entities.item import Item
from gear_icons import pick_armor_icon, pick_weapon_icon


_DATA_DIR = Path(__file__).parent.parent / "data" / "items"
_class_maps_cache = None


def _load_class_maps():
    """class_armor_map + class_stat_template_map, cached after first
    read - same static-content-cache convention as
    entities/equipment.py's _load_weapon_type_hand."""
    global _class_maps_cache
    if _class_maps_cache is None:
        try:
            with open(_DATA_DIR / "armor_types.json", "r") as f:
                armor_map = json.load(f).get("class_armor_map", {})
        except Exception:
            armor_map = {}
        try:
            with open(_DATA_DIR / "stat_templates.json", "r") as f:
                stat_map = json.load(f).get("class_stat_template_map", {})
        except Exception:
            stat_map = {}
        _class_maps_cache = (armor_map, stat_map)
    return _class_maps_cache


#: Starting weapon_type per class. Original 9 follow real WoW Classic
#: identity (Warrior=sword, Paladin=mace, Rogue=dagger, Shaman=mace,
#: Hunter=bow, Mage/Warlock/Priest=wand, Druid=mace - Druids are
#: restricted to staves/maces/daggers/fist weapons in Classic). CoA 21
#: are cross-checked against data/items/weapon_types.json's
#: class_weapon_map (the real proficiency allow-list enforced by
#: entities/proficiency.py's can_wear_weapon_type) so starting gear is
#: never something that class can't legally equip. One known gap: that
#: map doesn't list "bow" for Starcaller even though Starcaller Sentinel
#: is a confirmed bow-using Hunter analog per its ability-file docstring
#: - Starcaller gets mace_1h here (its map's own listed default) rather
#: than silently granting an item its own proficiency table would reject;
#: the map itself likely needs a follow-up correction outside this task.
CLASS_WEAPON_TYPE = {
    # Original 9
    "Warrior": "sword_1h", "Paladin": "mace_1h", "Rogue": "dagger",
    "Shaman": "mace_1h", "Hunter": "bow", "Mage": "wand",
    "Warlock": "wand", "Priest": "wand", "Druid": "mace_1h",

    # 21 CoA classes
    "Necromancer": "staff", "Pyromancer": "staff", "Cultist": "mace_1h",
    "Starcaller": "mace_1h", "Sun Cleric": "mace_1h", "Tinker": "gun",
    "Runemaster": "staff", "Primalist": "mace_1h", "Reaper": "mace_2h",
    "Venomancer": "dagger", "Chronomancer": "staff", "Bloodmage": "sword_1h",
    "Guardian": "mace_1h", "Stormbringer": "staff", "Felsworn": "fist_weapon",
    "Barbarian": "axe_1h", "Witch Doctor": "staff", "Witch Hunter": "crossbow",
    "Knight of Xoroth": "sword_1h", "Templar": "sword_1h", "Ranger": "bow",
}

#: weapon_types that occupy the Ranged equipment slot rather than
#: main_hand - if a class's CLASS_WEAPON_TYPE is one of these, their
#: single starting weapon already fills "ranged if needed" (Kyle's
#: phrasing) on its own; nothing extra is generated. Melee classes with
#: no ranged identity (Warrior, Rogue, Shaman, Druid, most melee CoA
#: classes) simply have nothing in that slot, which is correct - not
#: every class needs one.
_RANGED_WEAPON_TYPES = {"wand", "bow", "gun", "crossbow", "thrown", "totem"}

#: Fallback for any class not present in CLASS_WEAPON_TYPE (shouldn't
#: happen with the full 30-class roster covered above, but fails soft
#: rather than crashing character creation).
_DEFAULT_WEAPON_TYPE = "sword_1h"

WEAPON_NAME_NOUNS = {
    "sword_1h": "Sword", "sword_2h": "Greatsword", "axe_1h": "Axe",
    "axe_2h": "Battleaxe", "mace_1h": "Mace", "mace_2h": "Maul",
    "dagger": "Dagger", "fist_weapon": "Knuckles", "staff": "Staff",
    "wand": "Wand", "thrown": "Throwing Knife", "totem": "Totem",
    "shield": "Shield", "bow": "Bow", "gun": "Musket", "crossbow": "Crossbow",
    "polearm": "Polearm",
}

ARMOR_SLOT_NOUNS = {"chest": "Tunic", "legs": "Leggings", "feet": "Boots"}


def _compute_starting_weapon_damage(weapon_type):
    """Damage range for a level-1, common-rarity starting weapon, using
    the exact same damage_tier formula as LootGenerator.generate_weapon
    (entities/loot_generator.py) rather than a flat placeholder. Kept as
    a small local computation instead of calling LootGenerator directly,
    since that would also roll stats/suffixes onto what's meant to stay
    plain white gear (armor-only, no stats) per Kyle's Gear.docx
    convention - only the damage-range piece of that formula is wanted
    here."""
    weapon_types_data = _load_weapon_types_data()
    wtype_info = weapon_types_data["weapon_types"].get(weapon_type, {})
    tier_key = wtype_info.get("damage_tier", "one_hand")
    tier_mult = weapon_types_data["damage_tiers"].get(
        tier_key, {"dps_multiplier": 1.0})["dps_multiplier"]
    # item_level=1, rarity="common" (stat_budget_multiplier 1.0) - matches
    # every other starting-gear field already hardcoded to those values.
    avg = (1 * 1.1 + 6.4) * 1.0 * tier_mult
    dmin = max(1, int(avg * 0.85))
    dmax = max(dmin + 1, int(avg * 1.15))
    return dmin, dmax


_weapon_types_cache = None


def _load_weapon_types_data():
    global _weapon_types_cache
    if _weapon_types_cache is None:
        try:
            with open(_DATA_DIR / "weapon_types.json", "r") as f:
                _weapon_types_cache = json.load(f)
        except Exception:
            _weapon_types_cache = {"weapon_types": {}, "damage_tiers": {}}
    return _weapon_types_cache


def _make_weapon(weapon_type, stat_template):
    """One white (common-rarity), no-stat starting weapon. item_id
    follows the same generated-slug convention as
    LootGenerator.generate_weapon (never displayed to the player - see
    entities/loot_generator.py) so this item is indistinguishable in the
    UI from any other procedural common drop, no special "starter" tag
    that could leak an ugly internal string."""
    slot = "ranged" if weapon_type in _RANGED_WEAPON_TYPES else "main_hand"
    item_id = f"start_{weapon_type}_{uuid.uuid4().hex[:6]}"
    noun = WEAPON_NAME_NOUNS.get(weapon_type, "Weapon")
    dmin, dmax = _compute_starting_weapon_damage(weapon_type)
    return Item(
        item_id=item_id,
        name=f"Worn {noun}",
        slot=slot,
        item_level=1,
        rarity="common",
        armor_type=None,
        weapon_type=weapon_type,
        stat_template=stat_template,
        primary_stats={},
        secondary_stats={},
        armor_value=0,
        required_level=1,
        sell_price=1,
        flavor_text="",
        weapon_damage_min=dmin,
        weapon_damage_max=dmax,
        attack_speed=2.0,
        icon_id=pick_weapon_icon(weapon_type),
    )


def _make_armor(slot, armor_type):
    """One white (common-rarity), no-stat starting armor piece for a
    single slot - armor value only, matching Kyle's "white gear is
    armor-only with no stats" convention."""
    item_id = f"start_{slot}_{armor_type}_{uuid.uuid4().hex[:6]}"
    noun = ARMOR_SLOT_NOUNS.get(slot, "Garment")
    return Item(
        item_id=item_id,
        name=f"Worn {noun}",
        slot=slot,
        item_level=1,
        rarity="common",
        armor_type=armor_type,
        weapon_type=None,
        stat_template=None,
        primary_stats={},
        secondary_stats={},
        armor_value=2,
        required_level=1,
        sell_price=1,
        flavor_text="",
        icon_id=pick_armor_icon(slot, armor_type),
    )


def grant_starting_gear(character):
    """Equip a brand-new character with one weapon (in the Ranged slot
    instead of main_hand if their class's weapon_type is itself ranged),
    plus chest/legs/feet armor - all white, armor-only, item_level 1.

    Call once at character creation only - never on an existing/loaded
    character, which would silently overwrite whatever they've since
    equipped or sold.
    """
    armor_map, stat_map = _load_class_maps()
    char_class = character.char_class

    # Display-name keys against an id, so this missed for all 30 classes and every character
    # in the game started with the fallback weapon instead of their class's. See
    # core/class_names.py.
    from core.class_names import lookup
    weapon_type = lookup(CLASS_WEAPON_TYPE, char_class, _DEFAULT_WEAPON_TYPE)
    armor_type = armor_map.get(char_class, "cloth")
    stat_template = stat_map.get(char_class, "int_caster")

    character.equipment.equip(_make_weapon(weapon_type, stat_template))

    for slot in ("chest", "legs", "feet"):
        character.equipment.equip(_make_armor(slot, armor_type))
