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

    # Five authored off-hand items declare no weapon_type; a held oddment is
    # closest to a tome, and anything is closer than a coloured box.
    ("off_hand", None): ["gear_inv_tome_", "gear_inv_idol_"],
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
    # RELICS. These three weapon_types had no entry at all, so 28 hand-authored
    # boss drops - tomes, librams and idols - came back with icon_id None and
    # rendered as a flat rarity-coloured box with the name written on it. The
    # art existed the whole time in assets/icons/coa, which get_icon_surface
    # does not search; copied into the gear pack under the naming this picker
    # globs for rather than widening the search path, since one pipeline that
    # works beats two that disagree.
    "tome": ["gear_inv_tome_"],
    "libram": ["gear_inv_libram_"],
    "idol": ["gear_inv_idol_"],
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


# EPICS GET THEIR OWN ART. Kyle, 7 Nov: "for unique purples I can start to
# use prompts to get about 48 x 2 icons for epic items. They should be unique
# looking compared to current gear."
#
# An epic drew from the same pool as a quest green, so the only thing marking
# it out was the border tint. These prefixes name a parallel family -
# gear_epic_<key>_N.png, dropped into the same assets/icons/gear directory so
# the existing resolver finds them with no new search path. They are invisible
# to the ordinary pools because every ordinary prefix starts "gear_inv_", so a
# rare can never roll an epic icon by accident.
#
# Empty is safe: pick_* falls back to the ordinary pool for any family with no
# epic art yet, so this can be filled in one sheet at a time.
EPIC_PREFIX = "gear_epic_"


def _epic_keys(slot, armor_type=None, weapon_type=None):
    """The gear_epic_ family keys to try for an item, best first.

    ARMOUR ALWAYS TRIES ITS MATERIAL FIRST, which is where this differs from
    the ordinary table. That table does not split shoulders, gloves, belts and
    the rest by armour type, because the source WoW pack genuinely does not -
    one inv_shoulder icon serves cloth and plate alike. The epic sheet DOES
    draw them separately: spiked plate pauldrons, ringed mail spaulders,
    studded leather, a gem-clasped cloth mantle. Keying those on the slot
    alone would have handed a mage the spiked plate pauldrons, which is worse
    than the shared icon it replaced.

    The bare slot stays as the fallback so a future sheet that does not split
    a slot by material still works.
    """
    if weapon_type:
        return [weapon_type]
    keys = []
    if armor_type:
        keys.append(f"{slot}_{armor_type}")
    keys.append(slot)
    return keys


def _epic_candidates_for(slot=None, armor_type=None, weapon_type=None):
    for key in _epic_keys(slot, armor_type, weapon_type):
        found = _epic_candidates(key)
        if found:
            return found
    return []


def _epic_candidates(key):
    return _icons_for_prefixes([f"{EPIC_PREFIX}{key}_"]) if key else []


def icon_exists(icon_id):
    """True if this icon_id actually has a file in the gear pack.

    A stamped-but-dangling icon_id is WORSE than none: a caller that honours
    an explicit icon_id will prefer the dead string over a perfectly good
    seeded pick, and the item renders as a coloured box anyway. data/items/
    weapon_types.json and armor_types.json carry "rarity_common" on 26
    entries as a placeholder, and no rarity_*.png has ever existed, so that
    is not hypothetical.
    """
    return bool(icon_id) and icon_id in set(_all_gear_files())


def resolve_icon(slot=None, armor_type=None, weapon_type=None,
                 rarity=None, seed=None, explicit=None):
    """THE one place that decides a hand-authored item's icon.

    boss_loot and quest.py both had to make this call and were drifting
    apart on it within an hour of each other, which in this codebase is the
    oldest bug shape there is - two implementations of one rule.

    The order:

    1. An explicit icon_id, IF the file exists and it is not an ordinary-pool
       id on an epic. That second clause matters: 35 of the 36 authored epics
       carry a stamped gear_inv_* id from before the epic family existed, so
       honouring it blindly meant the epic art never appeared on the exact
       items it was drawn for. A gear_inv_ id cannot express authored intent
       about art that did not exist when it was written; a gear_epic_ one can,
       and still wins.
    2. The epic pool, for epic and legendary.
    3. The ordinary pool.

    Seeded throughout, so a fixed item keeps one icon across drops.
    """
    is_epic = rarity in ("epic", "legendary")
    if icon_exists(explicit) and not (is_epic and not explicit.startswith(EPIC_PREFIX)):
        return explicit
    if weapon_type:
        return pick_weapon_icon(weapon_type, seed=seed, rarity=rarity)
    return pick_armor_icon(slot, armor_type, seed=seed, rarity=rarity)


def pick_armor_icon(slot, armor_type, seed=None, rarity=None):
    """Random icon_id for an armor slot, or None if nothing matches
    (caller falls back to the existing rarity-colored-box rendering -
    see icon_migration_and_ui.py's get_item_icon_surface).

    `seed` makes the pick DETERMINISTIC for callers whose item is supposed to be a fixed piece of
    authored kit rather than a roll - pass any stable string and that string always yields the
    same icon. Added for Asher Coleman, whose loadout is documented as fixed and unalterable but
    whose armour icons re-rolled on every build, so his breastplate was plate11 one call and
    plate14 the next. Kyle had already asked for exactly this on his mace ("the icon should be
    equally fixed, not re-rolled"); the armour simply never got the same treatment. Seeded off a
    local Random so it cannot disturb the global stream every other roll in the game shares.
    """
    candidates = []
    if rarity in ("epic", "legendary"):
        candidates = _epic_candidates_for(slot=slot, armor_type=armor_type)
    if not candidates:
        prefixes = (ARMOR_ICON_PREFIXES.get((slot, armor_type))
                   or ARMOR_ICON_PREFIXES.get((slot, None)))
        if not prefixes:
            return None
        candidates = _icons_for_prefixes(prefixes)
    if not candidates:
        return None
    if seed is not None:
        # Sorted first: _all_gear_files() comes from a directory glob, whose order is whatever
        # the filesystem hands back. Seeding a pick over an unordered list is deterministic per
        # process and nothing more, which is the same trap hash() set for the creature variants.
        return random.Random(seed).choice(sorted(candidates))
    return random.choice(candidates)


def pick_weapon_icon(weapon_type, seed=None, rarity=None):
    """Random icon_id for a weapon_type, or None if nothing matches.

    `seed` does the same job it does in pick_armor_icon above: pass a stable
    string and that string always yields the same icon. Armour got this
    treatment when Asher Coleman's breastplate kept re-rolling; weapons never
    did, so every hand-authored boss weapon re-rolled its icon on each drop
    and one named sword could sit in the bag three times wearing three
    different pictures.

    Sorted before seeding, for the same reason: _all_gear_files() is a
    directory glob and its order is whatever the filesystem hands back, so
    seeding a pick over it would be deterministic within one process and
    nothing more.
    """
    candidates = []
    if rarity in ("epic", "legendary"):
        candidates = _epic_candidates_for(weapon_type=weapon_type)
    if not candidates:
        prefixes = WEAPON_ICON_PREFIXES.get(weapon_type)
        if not prefixes:
            return None
        candidates = _icons_for_prefixes(prefixes)
    if not candidates:
        return None
    if seed is not None:
        return random.Random(seed).choice(sorted(candidates))
    return random.choice(candidates)
