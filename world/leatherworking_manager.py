"""
Leatherworking — the second real crafting profession (Oct 2026).

HOW LEATHER DIFFERS FROM BLACKSMITHING
---------------------------------------
Blacksmithing consumes BARS produced by Smelting (a two-step chain: ore ->
smelting -> bar -> blacksmithing -> gear). Leatherworking consumes RAW LEATHER
that drops directly from beasts via Skinning (entities/skinning_drops.py) —
there is no intermediate processing step. Skinning itself is a profession
gate (only characters who know Skinning can skin a beast), but once the
leather is in the bag it is used directly, not refined.

LW crafts LEATHER and MAIL armor (leather for low tiers, mail for mid/high
tiers — same WoW progression where heavy leather gear becomes mail), plus
ARMOR KITS (intermediate materials the player can apply to gear or sell).

UPGRADE KITS
------------
Same as Blacksmithing: every LW material tier has its own upgrade kit recipe
(lw_kit_scrap, lw_kit_light, etc.). world/upgrade_manager.py's MATERIAL_KITS
dict handles the matching — adding a new LW tier is one new entry there and
one kit recipe here.

GUARANTEED SUCCESS
------------------
Same rule as every other crafting profession: skill only gates ACCESS, not
whether the craft succeeds. No RNG on success/failure.

STAT TEMPLATE
-------------
LW gear is agility-physical by default (hunters/shaman). All recipes in
data/leatherworking/recipes.json use "agi_physical" — the same template
BS uses for mail.
"""
import json
from pathlib import Path


class LeatherworkingManager:
    def __init__(self):
        self.recipes = {}
        self._load_data()

    def _load_data(self):
        recipes_file = Path(__file__).parent.parent / "data" / "leatherworking" / "recipes.json"
        if recipes_file.exists():
            with open(recipes_file, 'r', encoding="utf-8") as f:
                raw = json.load(f)
                # Strip _comment keys (documentation-only, not real recipes)
                self.recipes = {k: v for k, v in raw.get("recipes", {}).items()
                                if not k.startswith("_comment")}

    def available_recipes(self, character):
        """Recipes the character may craft: profession learned + skill high enough + recipe known."""
        if not character.knows_profession("leatherworking"):
            return {}
        skill = character.profession_skills.get("leatherworking", 0)
        return {
            rid: recipe
            for rid, recipe in self.recipes.items()
            if skill >= recipe.get("skill_required", 0) and character.knows_recipe(rid)
        }

    def can_craft(self, character, recipe_id):
        """True if the character knows this recipe, has the skill, and holds all materials."""
        recipe = self.recipes.get(recipe_id)
        if recipe is None or not character.knows_profession("leatherworking"):
            return False
        if not character.knows_recipe(recipe_id):
            return False
        skill = character.profession_skills.get("leatherworking", 0)
        if skill < recipe.get("skill_required", 0):
            return False
        return character.has_materials(recipe["inputs"])

    def craft(self, character, recipe_id):
        """Craft one item from recipe_id and add it to the character.

        Returns the produced Item/Material on success, None on failure.
        Mirrors BlacksmithingManager.craft exactly in structure.
        """
        if not self.can_craft(character, recipe_id):
            return None

        recipe = self.recipes[recipe_id]
        if recipe["output"]["kind"] in ("armor", "weapon"):
            if len(character.inventory) >= character.inventory_capacity:
                return None

        for input_id, qty in recipe["inputs"].items():
            if not character.consume_material(input_id, qty):
                return None

        output = self._generate_output(recipe_id, recipe)
        if output is None:
            return None

        from entities.item import Item
        if isinstance(output, Item):
            added = character.add_to_inventory(output)
            if not added:
                return None
        else:
            character.add_material(output)

        self._skill_up(character, recipe)
        self._award_craft_xp(character, recipe)
        from world.quest_manager import get_quest_manager
        get_quest_manager().record_craft(recipe_id)
        return output

    def _skill_up(self, character, recipe):
        """WoW-style color-window skill-up. skill_range = [orange_end, yellow_end, green_end, grey_at]."""
        import random
        skill = character.profession_skills.get("leatherworking", 0)
        req = recipe.get("skill_required", 0)
        orange, yellow, green, grey = recipe.get("skill_range") or (req + 5, req + 15, req + 25, req + 35)
        if skill >= grey:
            return False
        if skill < orange:
            chance = 1.0
        elif skill < yellow:
            chance = 0.75
        elif skill < green:
            chance = 0.35
        else:
            chance = 0.10
        if random.random() < chance:
            return character.gain_profession_skill("leatherworking", 1)
        return False

    def _award_craft_xp(self, character, recipe):
        """Award character XP proportional to the item_level of the crafted gear.
        Same calibration as CraftingManager._award_craft_xp: ~2% of level-up XP."""
        try:
            from config import get_exp_needed_for_level
            out = recipe["output"]
            item_level = out.get("item_level")
            if item_level is None:
                skill = recipe.get("skill_required", 0)
                item_level = max(1, int(skill * 60 / 300) + 1)
            xp = max(5, int(get_exp_needed_for_level(max(1, item_level)) * 0.02))
            character.gain_experience(xp)
        except Exception:
            pass

    def _generate_output(self, recipe_id, recipe):
        """Build the Item or Material this recipe produces."""
        spec = recipe["output"]

        if spec["kind"] == "material":
            from world.gathering_manager import get_gathering_node_manager
            return get_gathering_node_manager().make_material_instance(spec["material_id"])

        from entities.loot_generator import LootGenerator
        gen = LootGenerator()

        if spec["kind"] == "armor":
            item = gen.generate_armor_piece(
                slot=spec["slot"],
                armor_type=spec["armor_type"],
                stat_template=spec["stat_template"],
                item_level=spec["item_level"],
                rarity=spec["rarity"],
            )
        elif spec["kind"] == "weapon":
            item = gen.generate_weapon(
                slot=spec["slot"],
                weapon_type=spec["weapon_type"],
                stat_template=spec["stat_template"],
                item_level=spec["item_level"],
                rarity=spec["rarity"],
            )
        else:
            return None

        item.is_crafted = True
        item.name = recipe["name"]
        item.crafting_material = spec.get("material_tier")
        return item


_leatherworking_manager = None


def get_leatherworking_manager():
    global _leatherworking_manager
    if _leatherworking_manager is None:
        _leatherworking_manager = LeatherworkingManager()
    return _leatherworking_manager
