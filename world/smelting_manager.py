"""
Smelting - the Mining profession's crafting sub-skill (turns ore into
bars, and some bars into alloy bars like Bronze/Steel).

WHY SMELTING IS ITS OWN MODULE, NOT PART OF GatheringNodeManager
-------------------------------------------------------------------
Gathering (GatheringNodeManager) is about the WORLD: where nodes spawn,
what's in them, rolling a skill-up chance. Smelting is about the
PLAYER'S INVENTORY: consuming materials they already have, producing a
new one, with the character's mining skill gating access but never
introducing randomness (Kyle, 2026-09-12: "guaranteed success always").
These are different enough mechanics - one touches the world/tilemap,
the other only touches Character.materials - that folding them into one
manager would blur what each one is actually responsible for.

WHY SMELTING SHARES MINING'S SKILL NUMBER
---------------------------------------------
Confirmed via web search (2026-09-12): in real WoW, Smelting is NOT a
separate profession or skill track - "Your Smelting skill is the same
as your overall Mining skill" (Warcraft Tavern). So SmeltingManager reads
Character.profession_skills["mining"] directly rather than tracking its
own number, matching real WoW rather than inventing a parallel skill.
"""
import json
from pathlib import Path


class SmeltingManager:
    def __init__(self):
        self.recipes = {}  # output material_id -> recipe dict
        self._load_data()

    def _load_data(self):
        data_dir = Path(__file__).parent.parent / "data" / "gathering"
        recipes_file = data_dir / "smelting_recipes.json"
        if recipes_file.exists():
            with open(recipes_file, 'r') as f:
                self.recipes = json.load(f).get("recipes", {})

    def available_recipes(self, character):
        """Recipes the character's current Mining skill permits, in the
        order they appear in the data file. Does NOT check whether the
        character currently HAS the materials - that's a separate
        concern (can_craft below), since a recipe should still be listed
        and viewable/plannable even when the player is temporarily out
        of ore, same as a WoW spellbook still shows a recipe you're out
        of reagents for rather than hiding it entirely."""
        skill = character.profession_skills.get("mining", 0)
        return {
            output_id: recipe
            for output_id, recipe in self.recipes.items()
            if skill >= recipe.get("skill_required", 0)
        }

    def can_craft(self, character, output_id):
        """True if the character both knows this recipe (skill-gated)
        AND currently holds every required input at the needed
        quantity."""
        recipe = self.recipes.get(output_id)
        if recipe is None:
            return False
        skill = character.profession_skills.get("mining", 0)
        if skill < recipe.get("skill_required", 0):
            return False
        return character.has_materials(recipe["inputs"])

    def smelt(self, character, output_id, gathering_manager):
        """Attempt to craft one unit of output_id. Returns the produced
        Material on success, or None on failure (unknown recipe, skill
        too low, or missing materials - can_craft() already covers all
        three, called here again rather than trusted from the caller so
        this method is safe to call directly without a separate
        validation step first).

        No RNG, no partial failure - either every input is consumed and
        exactly one output is produced, or nothing happens at all. This
        needs gathering_manager only to build the output Material
        instance via make_material_instance() (the same factory gathering
        nodes use), not because smelting touches the world in any way -
        keeping material CONSTRUCTION in one place (materials.json's
        data, read by GatheringNodeManager) rather than duplicating that
        lookup/instantiation logic here.
        """
        if not self.can_craft(character, output_id):
            return None

        recipe = self.recipes[output_id]
        # has_materials() in can_craft already confirmed every input is
        # available, so this consume loop should never fail - but each
        # consume_material call is still individually all-or-nothing
        # (see its own docstring), so if something changed between the
        # can_craft check and here (shouldn't happen in a single-threaded
        # turn-based flow, but defensive rather than assumed), a failed
        # consume simply aborts here rather than leaving a half-consumed
        # recipe - at worst some earlier inputs in this same call were
        # already removed with no output produced, which is a real but
        # narrow edge case worth flagging rather than silently accepting.
        for input_id, qty in recipe["inputs"].items():
            if not character.consume_material(input_id, qty):
                return None

        output_material = gathering_manager.make_material_instance(output_id)
        if output_material is None:
            return None
        character.add_material(output_material)

        # Smelting grants Mining skill-ups too, same orange/yellow/green/
        # grey roll gathering uses (confirmed real WoW behavior via web
        # search: "Smelting gives skill-ups until 185 Mining, making it
        # useful for early leveling") - NOT the same thing as smelting's
        # own guaranteed-success rule. Those are two different questions:
        # "does the craft succeed" (always yes, Kyle's rule) vs "does
        # doing it teach you anything more" (rolls against the bar's own
        # skill_range, tapering off exactly like a gathered material
        # does). A bar with no skill_range fails open (roll_skill_up's
        # documented fallback), same safe default as gathering.
        current_skill = character.profession_skills.get("mining", 0)
        if gathering_manager.roll_skill_up(output_id, current_skill):
            from world.gathering_manager import TIER_SKILL_CAPS
            output_def = gathering_manager.get_material_def(output_id)
            tier_cap = TIER_SKILL_CAPS.get(output_def.get("tier")) if output_def else None
            cumulative_cap = sum(TIER_SKILL_CAPS.values()) if tier_cap is not None else None
            character.gain_profession_skill("mining", 1, cap=cumulative_cap)

        from world.quest_manager import get_quest_manager
        get_quest_manager().record_craft(output_id)
        return output_material


_smelting_manager = None


def get_smelting_manager():
    """Module-level singleton, same access pattern as
    world.gathering_manager.get_gathering_node_manager()."""
    global _smelting_manager
    if _smelting_manager is None:
        _smelting_manager = SmeltingManager()
    return _smelting_manager
