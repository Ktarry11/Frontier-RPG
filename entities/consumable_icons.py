"""consumable_id -> icon file, for the potion/elixir art.

Same job gear_icons.py does for procedural gear: keep the art mapping in ONE
module instead of hand-stamping an icon_id into 68 JSON entries, where it
would drift the moment a consumable is renamed or a tier is added.

WHY 48 FILES FOR 68 CONSUMABLES
-------------------------------
The 60 elixirs are 20 effect FAMILIES (strength, dodge, fire ward, ...) that
each exist in two or three power tiers. Drawing 60 near-identical bottles
would be waste and would read as noise in the bag, so the art sheet
(claude/alchemy_art_prompts.md) gives each family a LESSER and a GREATER
bottle - same liquid colour, different glass - and the middle tier reuses its
family's lesser art. The 8 potions get one icon each.

    8 potions + (20 families x 2 tiers) = 48 files

The size difference between lesser and greater is real art, not a UI trick:
tools/slice_icon_sheet.py keeps this sheet's icons at their relative scale
(PRESERVE_SCALE) precisely so a greater bottle still looks bigger in the bag.

Food and ammo are deliberately absent - they have no art on this sheet yet,
and icon_for returns None for them, which the UI already handles by falling
back to its text rendering.
"""

#: family stem -> (ids using the LESSER bottle, ids using the GREATER bottle)
_FAMILIES = {
    # ---- battle elixirs ------------------------------------------------
    "elixir_strength": (
        ["battle_elixir_minor", "elixir_of_strength", "battle_elixir_standard"],
        ["battle_elixir_superior", "elixir_of_greater_strength"],
    ),
    "elixir_agility": (
        ["elixir_of_lesser_agility", "elixir_of_agility"],
        ["elixir_of_greater_agility"],
    ),
    "elixir_intellect": (
        ["elixir_of_lesser_intellect", "arcane_elixir"],
        ["greater_arcane_elixir"],
    ),
    "elixir_spellpower": (
        ["elixir_of_lesser_firepower", "elixir_of_firepower"],
        ["elixir_of_greater_firepower"],
    ),
    "elixir_attackpower": (
        ["elixir_of_brutality", "elixir_of_the_mongoose"],
        ["elixir_of_greater_mongoose"],
    ),
    "elixir_crit_physical": (
        ["elixir_of_precision", "elixir_of_greater_precision"],
        ["elixir_of_deadly_strikes"],
    ),
    "elixir_crit_spell": (
        ["elixir_of_insight", "elixir_of_greater_insight"],
        ["elixir_of_arcane_fury"],
    ),
    "elixir_haste": (
        ["elixir_of_swiftness", "elixir_of_greater_swiftness"],
        ["elixir_of_the_wind"],
    ),
    "elixir_str_int": (
        ["elixir_of_devotion", "elixir_of_holy_fury"],
        ["elixir_of_the_crusader"],
    ),
    "elixir_agi_int": (
        ["elixir_of_cunning", "elixir_of_the_trickster"],
        ["elixir_of_shadow_cunning"],
    ),
    # ---- guardian elixirs ----------------------------------------------
    "elixir_stamina": (
        ["guardian_elixir_minor", "elixir_of_endurance", "guardian_elixir_standard"],
        ["guardian_elixir_superior", "elixir_of_greater_endurance"],
    ),
    "elixir_spirit": (
        ["elixir_of_minor_warding", "elixir_of_warding"],
        ["elixir_of_greater_warding"],
    ),
    "elixir_fortitude": (
        ["elixir_of_minor_fortitude", "elixir_of_fortitude"],
        ["elixir_of_greater_fortitude"],
    ),
    "elixir_armor": (
        ["elixir_of_toughness", "elixir_of_greater_toughness"],
        ["elixir_of_ironskin"],
    ),
    "elixir_mana_regen": (
        ["elixir_of_wisdom", "elixir_of_greater_wisdom"],
        ["elixir_of_the_sage"],
    ),
    "elixir_dodge": (
        ["elixir_of_evasion", "elixir_of_greater_evasion"],
        ["elixir_of_the_mongoose_guard"],
    ),
    "elixir_ward_fire": (
        ["elixir_of_fire_ward"], ["elixir_of_greater_fire_ward"],
    ),
    "elixir_ward_frost": (
        ["elixir_of_frost_ward"], ["elixir_of_greater_frost_ward"],
    ),
    "elixir_ward_nature": (
        ["elixir_of_nature_ward"], ["elixir_of_greater_nature_ward"],
    ),
    "elixir_ward_shadow": (
        ["elixir_of_shadow_ward"], ["elixir_of_greater_shadow_ward"],
    ),
}

#: consumable_id -> icon file stem (no extension, no directory).
CONSUMABLE_ICONS = {
    # Potions are 1:1 - the file is named after the consumable itself.
    "healing_potion_minor": "healing_potion_minor",
    "healing_potion_standard": "healing_potion_standard",
    "healing_potion_superior": "healing_potion_superior",
    "healing_potion_mega": "healing_potion_mega",
    "mana_potion_minor": "mana_potion_minor",
    "mana_potion_standard": "mana_potion_standard",
    "mana_potion_superior": "mana_potion_superior",
    "mana_potion_mega": "mana_potion_mega",
}

for _stem, (_lesser, _greater) in _FAMILIES.items():
    for _cid in _lesser:
        CONSUMABLE_ICONS[_cid] = f"{_stem}_lesser"
    for _cid in _greater:
        CONSUMABLE_ICONS[_cid] = f"{_stem}_greater"
del _stem, _lesser, _greater, _cid


def icon_for(consumable_id):
    """The icon file stem for a consumable, or None if it has no art yet.

    None is a normal answer, not an error - food and ammo have no icons on
    the alchemy sheet, and the UI already falls back to text for anything
    without art.
    """
    return CONSUMABLE_ICONS.get(consumable_id)
