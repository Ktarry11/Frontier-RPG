"""
Gear icon lookup - maps a generated item's (slot, armor_type, weapon_type)
to a pool of real WoW Classic icon_ids it can randomly draw from at
generation time (see LootGenerator.generate_armor_piece/generate_weapon).

Source art: Kyle's "WoW Vanilla/Classic Icon Pack" upload (2023 icons
across Armor/Weapons/Items/Trade/Abilities/Spells categories). Only
Armor + Weapons were copied into assets/icons/gear/ - Trade/Abilities/
Spells aren't equipment and would just be 966 unused files. Every file
was renamed gear_<slugified_original_name>.png (see the one-off copy
script in project history) so the original WoW filename is still legible
for cross-reference, just lowercased/underscored to match this project's
icon_id convention.

WHY A PREFIX TABLE, NOT A HAND-TYPED PER-ITEM LIST: there are 721 gear
icon files. Hand-mapping each to a specific procedural item would be both
enormous and pointless busywork - the pack's own filenames already group
by real-world slot (inv_helmet, inv_belt, inv_chest_cloth, ...), so this
table matches PREFIXES against that existing structure and lets
_icons_for_prefix() glob the actual files, which stays correct even if
more icons get added to assets/icons/gear/ later.

Some slots don't have an armor-type-specific icon set in this pack (e.g.
"inv_helmet" covers cloth/leather/mail/plate helms alike, unlike chest
pieces which DO split by type) - real WoW's own icon set works the same
way, most slots aren't reskinned per armor type, so this isn't a gap,
it's accurate to the source material.
"""
from pathlib import Path
import random

GEAR_ICON_DIR = Path(__file__).parent / "assets" / "icons" / "gear"

# ------------------------------------------------------------------
# Armor: (slot, armor_type) -> list of filename prefixes to search for.
# Falls back through less-specific prefixes if a type-specific one has no
# matches (e.g. "back" has no armor_type split at all - capes are capes).
# ------------------------------------------------------------------
ARMOR_ICON_PREFIXES = {
    ("head", "cloth"): ["gear_inv_helmet"],
    ("head", "leather"): ["gear_inv_helmet"],
    ("head", "mail"): ["gear_inv_helmet"],
    ("head", "plate"): ["gear_inv_helmet", "gear_inv_crown"],

    ("shoulder", None): ["gear_inv_shoulder"],

    ("back", None): ["gear_inv_misc_cape"],

    ("chest", "cloth"): ["gear_inv_chest_cloth", "gear_inv_shirt"],
    ("chest", "leather"): ["gear_inv_chest_leather"],
    ("chest", "mail"): ["gear_inv_chest_chain"],
    ("chest", "plate"): ["gear_inv_chest_plate"],

    ("wrist", None): ["gear_inv_bracer"],

    ("hands", None): ["gear_inv_gauntlets"],

    ("waist", None): ["gear_inv_belt"],

    ("legs", None): ["gear_inv_pants"],

    ("feet", "plate"): ["gear_inv_boots_plate", "gear_inv_boots"],
    ("feet", None): ["gear_inv_boots"],

    ("ring", None): ["gear_inv_jewelry_ring"],

    ("neck", None): ["gear_inv_jewelry_necklace", "gear_inv_jewelry_amulet"],

    ("trinket", None): ["gear_inv_jewelry_talisman"],

    ("ranged", None): ["gear_inv_misc_quiver"],
}

# ------------------------------------------------------------------
# Weapons: weapon_type -> filename prefixes.
# ------------------------------------------------------------------
WEAPON_ICON_PREFIXES = {
    "sword_1h": ["gear_inv_sword"],
    "sword_2h": ["gear_inv_sword"],
    "axe_1h": ["gear_inv_axe", "gear_inv_throwingaxe"],
    "axe_2h": ["gear_inv_axe"],
    "mace_1h": ["gear_inv_mace"],
    "mace_2h": ["gear_inv_hammer"],
    "dagger": ["gear_inv_weapon_shortblade", "gear_inv_throwingknife"],
    # No fist-weapon-specific icons in this pack - shortblade is the
    # closest visual fit (small, held weapon) rather than leaving fist
    # weapons with no icon at all.
    "fist_weapon": ["gear_inv_weapon_shortblade"],
    "staff": ["gear_inv_staff"],
    "wand": ["gear_inv_wand"],
    "thrown": ["gear_inv_throwingaxe", "gear_inv_throwingknife"],
    "bow": ["gear_inv_weapon_bow"],
    "gun": ["gear_inv_weapon_rifle"],
    "crossbow": ["gear_inv_weapon_crossbow"],
    # No totem-specific icons in this pack either - wand is the closest
    # "small caster implement" silhouette available.
    "totem": ["gear_inv_wand"],
    "shield": ["gear_inv_shield"],
    "polearm": ["gear_inv_weapon_halberd", "gear_inv_spear"],
}

_file_cache = None


def _all_gear_files():
    """All gear icon filenames (no extension), cached after first scan -
    this directory is static content, not something that changes at
    runtime, so re-globbing on every lookup would be wasted work."""
    global _file_cache
    if _file_cache is None:
        _file_cache = [p.stem for p in GEAR_ICON_DIR.glob("*.png")]
    return _file_cache


def _icons_for_prefixes(prefixes):
    """All icon_ids whose filename starts with any of the given prefixes."""
    files = _all_gear_files()
    matches = [f for f in files if any(f.startswith(p) for p in prefixes)]
    return matches


def pick_armor_icon(slot, armor_type):
    """Random icon_id for an armor slot, or None if nothing matches
    (caller falls back to the existing rarity-colored-box rendering -
    see icon_migration_and_ui.py's get_item_icon_surface)."""
    prefixes = (ARMOR_ICON_PREFIXES.get((slot, armor_type))
               or ARMOR_ICON_PREFIXES.get((slot, None)))
    if not prefixes:
        return None
    candidates = _icons_for_prefixes(prefixes)
    return random.choice(candidates) if candidates else None


def pick_weapon_icon(weapon_type):
    """Random icon_id for a weapon_type, or None if nothing matches."""
    prefixes = WEAPON_ICON_PREFIXES.get(weapon_type)
    if not prefixes:
        return None
    candidates = _icons_for_prefixes(prefixes)
    return random.choice(candidates) if candidates else None
