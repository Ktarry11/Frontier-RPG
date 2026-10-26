"""
Blacksmithing - the first real crafting profession (Oct 2026). Turns the
BARS Smelting already produces into real, equippable gear.

WHY THIS IS A SEPARATE PROFESSION, NOT PART OF SMELTING
---------------------------------------------------------
Smelting shares Mining's own skill number because that's real WoW
behavior ("Your Smelting skill is the same as your overall Mining skill" -
see smelting_manager.py's own docstring). Blacksmithing is NOT like that -
it's its own genuine profession in real WoW, with its own skill track, a
character can know without ever mining ore themselves (buying bars from
the market instead). So this reads/writes
Character.profession_skills["blacksmithing"] as its own number, never
touching "mining" - the two professions are related by what materials
flow between them, not by sharing a skill level.

WHY OUTPUT IS A REAL Item, NOT A Material
-------------------------------------------
Smelting's output (a bar) is just another raw material - stackable,
inert, feeds back into other recipes. Blacksmithing's output is
real, equippable GEAR - the same Item class procedural loot and quest
rewards use (entities/item.py). Rather than hand-picking stats for every
recipe (the entities/loot_generator.py docstring already explains why that
drifts out of balance over time), each recipe's output is a fixed spec
(slot, armor_type/weapon_type, stat_template, item_level, rarity) fed
straight into LootGenerator.generate_armor_piece/generate_weapon - the
exact same stat-budget math every procedural drop uses. This mirrors how
a real WoW blacksmithing pattern always produces the same NAMED item, just
without hand-authoring its numbers by hand.

Every crafted Item gets is_crafted=True stamped on after generation
(LootGenerator has no knowledge of this engine's crafting system, so
nothing upstream sets it) - that flag is what makes an item eligible for
upgrade kits later (Kyle, Oct 2026: "Only crafted" items can be upgraded,
not procedural drops or quest rewards even at the same rarity).

Guaranteed success, same as Smelting (Kyle's "guaranteed success always"
rule - skill only gates ACCESS to a recipe, never whether a craft attempt
actually works once you have access).
"""
import json
from pathlib import Path


class BlacksmithingManager:
    def __init__(self):
        self.recipes = {}  # recipe_id -> recipe dict
        self._load_data()

    def _load_data(self):
        recipes_file = Path(__file__).parent.parent / "data" / "blacksmithing" / "recipes.json"
        if recipes_file.exists():
            with open(recipes_file, 'r') as f:
                self.recipes = json.load(f).get("recipes", {})

    def available_recipes(self, character):
        """Recipes the character's current Blacksmithing skill permits, in
        the order they appear in the data file. Does NOT check materials -
        same reasoning as SmeltingManager.available_recipes: a known
        recipe should still be listed even while temporarily out of bars."""
        if not character.knows_profession("blacksmithing"):
            return {}
        skill = character.profession_skills.get("blacksmithing", 0)
        return {
            recipe_id: recipe
            for recipe_id, recipe in self.recipes.items()
            if skill >= recipe.get("skill_required", 0)
        }

    def can_craft(self, character, recipe_id):
        """True if the character both knows this recipe (skill-gated) AND
        currently holds every required bar at the needed quantity."""
        recipe = self.recipes.get(recipe_id)
        if recipe is None or not character.knows_profession("blacksmithing"):
            return False
        skill = character.profession_skills.get("blacksmithing", 0)
        if skill < recipe.get("skill_required", 0):
            return False
        return character.has_materials(recipe["inputs"])

    def craft(self, character, recipe_id):
        """Attempt to craft one output from recipe_id - either a real
        equippable Item (a weapon/armor pattern) or a Material (an
        upgrade kit, Kyle: "All crafters will craft their upgrade kits
        bro") - and ADDS it directly to the character, same convention
        SmeltingManager.smelt() already uses (it calls
        character.add_material itself rather than leaving that to the
        caller). Returns the produced Item/Material on success, or None
        on failure (unknown recipe, skill too low, or missing bars -
        can_craft() already covers all three, re-checked here rather than
        trusted from the caller, same defensive shape as
        SmeltingManager.smelt).

        No RNG on whether the craft succeeds, no partial failure - either
        every bar is consumed and exactly one output is produced, or
        nothing happens at all. An ITEM output's stats still roll some
        variance (same _roll_stats RNG every procedural drop uses) -
        that's intentional, not a bug: "guaranteed success" means the
        recipe never fails to produce its output, not that every craft of
        the same recipe is numerically identical, same as real WoW
        crafted gear before fixed-stat patterns became the norm. A
        MATERIAL output (an upgrade kit) has no such variance - it's
        just another stackable material, identical every time, same as
        any Smelting output.

        REAL BUG AVOIDED HERE: Character.add_to_inventory's own docstring
        is explicit that callers MUST check its return value - a full
        backpack makes it a real possible outcome, not a theoretical one.
        An item-kind recipe's output goes into self.inventory (a capped
        list), unlike a material-kind output (an upgrade kit), which
        stacks into self.materials with no such cap. So for an item
        recipe specifically, inventory space is checked BEFORE bars are
        consumed - crafting a sword with a full bag would otherwise
        silently eat the player's bars and hand back nothing, since the
        generated Item has nowhere to go and would just be discarded
        here. Material-kind outputs need no such check (materials never
        reject an add_material call).
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
                # Shouldn't happen (just checked above), but never claim
                # success and hand back an item that isn't actually in
                # the character's inventory if something changed the
                # capacity/count between the check and here.
                return None
        else:
            character.add_material(output)

        character.gain_profession_skill("blacksmithing", 1)
        self._award_craft_xp(character, recipe)
        from world.quest_manager import get_quest_manager
        get_quest_manager().record_craft(recipe_id)
        return output

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
        """Build the real Item or Material this recipe produces.

        Item outputs go through LootGenerator (the exact same stat-budget
        math every procedural drop uses), then get is_crafted=True
        stamped on (LootGenerator has no idea crafting exists - it's
        shared with procedural loot/quest rewards - so this manager is
        responsible for marking its own output, not the generator) and
        their name overridden to the recipe's real WoW name (real
        patterns always make the SAME named item, not LootGenerator's
        randomized rarity-flavor name meant for procedural drops).

        Material outputs (upgrade kits) go through the same
        make_material_instance() factory gathering nodes and Smelting
        already use, reading from data/gathering/materials.json - an
        upgrade kit is just another stackable material, no different in
        kind from a bar, so it reuses that exact factory rather than
        building a second one.
        """
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
        # Tags which upgrade kit this item matches (world/upgrade_manager.py's
        # MATERIAL_KITS) - Kyle's corrected design: "copper kit only
        # upgrades copper stuff", matched by material, not by rarity.
        item.crafting_material = spec.get("material_tier")
        return item


_blacksmithing_manager = None


def get_blacksmithing_manager():
    """Module-level singleton, same access pattern as
    world.smelting_manager.get_smelting_manager()."""
    global _blacksmithing_manager
    if _blacksmithing_manager is None:
        _blacksmithing_manager = BlacksmithingManager()
    return _blacksmithing_manager
