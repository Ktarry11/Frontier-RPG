"""
Recipe scrolls / pattern items (Oct 2026).

A recipe scroll is a normal Item with recipe_id and recipe_profession set.
It sits in the player's inventory like any other item; right-clicking it
calls character.learn_recipe(). If the player doesn't have the required
skill yet they can still CARRY it — they just can't learn it until they do
(exactly like WoW patterns you loot early but can't use until higher skill).

Sources of recipe scrolls:
  - "trainer"  — taught automatically when visiting a trainer (no scroll item involved;
                  trainer calls character.learn_trainer_recipes directly)
  - "drop"     — world drop from a specific creature or random mob
  - "vendor"   — sold by a specific vendor NPC in a specific town
  - "quest"    — rewarded by completing a specific quest

This module provides:
  make_recipe_scroll()  — build an Item that IS a recipe scroll
  get_recipe_info()     — look up a recipe's metadata across all professions

The loot system, vendor system, and quest system all call make_recipe_scroll()
to produce the Item they then hand to the player.
"""

from pathlib import Path
import json

# All profession recipe sources, lazy-loaded
_RECIPE_SOURCES: dict | None = None


def _load_all_recipes() -> dict:
    """Returns {recipe_id: (profession, recipe_dict)} across all professions."""
    global _RECIPE_SOURCES
    if _RECIPE_SOURCES is not None:
        return _RECIPE_SOURCES

    repo = Path(__file__).parent.parent
    _RECIPE_SOURCES = {}

    # Flat recipe files (one profession per file)
    flat_files = {
        "blacksmithing": repo / "data/blacksmithing/recipes.json",
        "leatherworking": repo / "data/leatherworking/recipes.json",
    }
    for prof, path in flat_files.items():
        if path.exists():
            data = json.loads(path.read_text())
            for rid, recipe in data.get("recipes", {}).items():
                if not rid.startswith("_"):
                    _RECIPE_SOURCES[rid] = (prof, recipe)

    # Nested crafting file (multiple professions)
    crafting_path = repo / "data/crafting/recipes.json"
    if crafting_path.exists():
        data = json.loads(crafting_path.read_text())
        for prof, prof_data in data.get("professions", {}).items():
            for rid, recipe in prof_data.get("recipes", {}).items():
                if not rid.startswith("_"):
                    _RECIPE_SOURCES[rid] = (prof, recipe)

    return _RECIPE_SOURCES


def get_recipe_info(recipe_id: str) -> tuple[str, dict] | tuple[None, None]:
    """Returns (profession, recipe_dict) or (None, None) if not found."""
    all_recipes = _load_all_recipes()
    result = all_recipes.get(recipe_id)
    if result is None:
        return None, None
    return result


def make_recipe_scroll(recipe_id: str) -> "Item | None":
    """Build an Item that represents a learnable recipe scroll.

    The item:
    - slot = "recipe"  (non-equippable, lives in inventory as a usable item)
    - rarity derived from the recipe's output rarity (common recipe → poor scroll,
      uncommon → common, rare → uncommon — the scroll is worth less than the gear)
    - name = "Recipe: <recipe name>" (WoW convention)
    - recipe_id and recipe_profession set (used by UI to call learn_recipe)
    - skill_required stored as required_level proxy so inventory tooltip can show
      "Requires Blacksmithing 75" without the UI needing to look up the recipe

    Returns None if recipe_id is unknown.
    """
    from entities.item import Item

    profession, recipe = get_recipe_info(recipe_id)
    if recipe is None:
        return None

    out = recipe.get("output", {})
    recipe_name = recipe.get("name", recipe_id)
    skill_req = recipe.get("skill_required", 0)

    # Scroll rarity: one step below the gear it teaches (common gear → poor scroll is too harsh,
    # use common for everything up through uncommon gear, uncommon scroll for rare gear).
    output_rarity = out.get("rarity", "common")
    scroll_rarity_map = {
        "poor": "poor",
        "common": "common",
        "uncommon": "common",
        "rare": "uncommon",
        "epic": "uncommon",
    }
    scroll_rarity = scroll_rarity_map.get(output_rarity, "common")

    # item_level proxy: map skill_required to effective ilvl so the scroll
    # appears in appropriately-levelled loot pools / vendor lists.
    item_level = max(1, int(skill_req * 60 / 300) + 1)

    # Sell price: modest — recipe scrolls shouldn't be vendor-fodder but
    # they're not gear either. Roughly 1 silver per 10 skill points.
    sell_price = max(1, skill_req // 10) * 10  # in copper (1s = 100c)

    prefix = _profession_prefix(profession)
    display_name = f"{prefix}: {recipe_name}"

    flavor = (
        f"Teaches you how to craft {recipe_name}. "
        f"Requires {profession.title()} ({skill_req})."
    )

    return Item(
        item_id=f"recipe_scroll_{recipe_id}",
        name=display_name,
        slot="recipe",          # special non-equip slot; inventory screen renders these as usables
        item_level=item_level,
        rarity=scroll_rarity,
        required_level=1,       # character level gate; actual gate is profession skill
        sell_price=sell_price,
        flavor_text=flavor,
        recipe_id=recipe_id,
        recipe_profession=profession,
    )


def _profession_prefix(profession: str) -> str:
    """WoW-style prefix for the recipe scroll name."""
    return {
        "blacksmithing": "Plans",
        "leatherworking": "Pattern",
        "tailoring": "Pattern",
        "alchemy": "Recipe",
        "woodworking": "Schematic",
        "cooking": "Recipe",
        "engineering": "Schematic",
    }.get(profession, "Recipe")


def scrolls_for_source(source: str, profession: str | None = None) -> list[str]:
    """Return all recipe_ids with the given source (and optionally profession).

    Useful for seeding vendor inventories and loot tables:
      vendor_recipes = scrolls_for_source("vendor", "blacksmithing")
      world_drops    = scrolls_for_source("drop")
    """
    all_recipes = _load_all_recipes()
    result = []
    for rid, (prof, recipe) in all_recipes.items():
        if profession and prof != profession:
            continue
        if recipe.get("source") == source:
            result.append(rid)
    return result


_recipe_manager_singleton = None


def get_recipe_manager():
    global _recipe_manager_singleton
    if _recipe_manager_singleton is None:
        _recipe_manager_singleton = _RecipeManagerSingleton()
    return _recipe_manager_singleton


class _RecipeManagerSingleton:
    """Thin wrapper so other modules can call get_recipe_manager().make_recipe_scroll(id)
    without importing the module-level function directly."""
    make_recipe_scroll = staticmethod(make_recipe_scroll)
    get_recipe_info = staticmethod(get_recipe_info)
    scrolls_for_source = staticmethod(scrolls_for_source)
