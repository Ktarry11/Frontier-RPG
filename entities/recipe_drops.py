"""Recipe scrolls as rare drops.

Kyle, 2026-10-28: "ensure there are nice rare drops of useful recipies to learn etc. or still reward
some through quests."

THE SYSTEM WAS ALREADY BUILT AND NOBODY CALLED IT. world/recipe_manager.make_recipe_scroll() turns a
recipe id into a proper scroll Item, the inventory screen already learns from one on click, and
Character.learn_recipe already gates on skill and profession. Its own module docstring says "the loot
system, vendor system, and quest system all call make_recipe_scroll()". None of them did - it had zero
callers anywhere in the codebase. Meanwhile 135 recipes carried source "drop" and 57 carried "vendor",
so 192 recipes were labelled as things you find in the world and not one of them could be found. This
module is the loot half of that wiring.

NO PER-CREATURE AUTHORING, ON PURPOSE. The obvious shape is a table keyed by creature name, like
quest_drops.json. With 871 creatures and more arriving with every zone, that table would be wrong the
day after it was written and it would quietly stop covering new content. Instead the pool is derived:
a mob of level N can drop any drop-source recipe whose skill requirement a player at level N could
plausibly have, which means every new zone is covered the moment its creatures exist, and every new
drop-source recipe starts dropping the moment it is authored.

THE SKILL-TO-LEVEL BRIDGE is the one real assumption here. Professions run 1-225 and characters run
1-60, and the game has no formal link between them, so this uses the same relationship the material
ladders already imply: roughly five skill per level. A level 20 mob carries recipes around skill 100.
The window is generous on the low side (you can find a recipe you have long outgrown) and tight on the
high side (never more than a little above you), because finding a scroll you cannot read yet for
another ten levels is a worse feeling than finding one you could have made anyway.
"""
import random

#: Skill a character of this level is assumed to be able to reach.
SKILL_PER_LEVEL = 5

#: How far above that assumed skill a dropped recipe may sit. Small - a scroll you cannot use for
#: another ten levels reads as a tease rather than a reward.
SKILL_OVERSHOOT = 15

#: Chance any single kill yields a scroll. Deliberately low: this is the "oh nice" drop, and a
#: profession you can fill from grinding is a profession with no reason to visit a trainer.
CHANCE = {"normal": 0.004, "elite": 0.02, "boss": 0.06}

_POOL = None


def _pool():
    """[(skill_required, recipe_id)] for every recipe the world is supposed to hand out, sorted."""
    global _POOL
    if _POOL is None:
        from world.recipe_manager import all_recipes_by_source
        _POOL = sorted((r.get("skill_required", 0), rid)
                       for rid, (_prof, r) in all_recipes_by_source("drop").items())
    return _POOL


def eligible(level):
    """Recipe ids a mob of this level may drop."""
    ceiling = level * SKILL_PER_LEVEL + SKILL_OVERSHOOT
    return [rid for skill, rid in _pool() if skill <= ceiling]


def roll_recipe(enemy, rng=random):
    """A recipe id to hand over, or None. Caller turns it into a scroll via make_recipe_scroll."""
    if getattr(enemy, "is_boss", False):
        band = "boss"
    elif getattr(enemy, "is_elite", False):
        band = "elite"
    else:
        band = "normal"
    if rng.random() > CHANCE[band]:
        return None
    pool = eligible(max(1, int(getattr(enemy, "level", 1))))
    if not pool:
        return None
    # Weighted toward the top of what this mob can give, so a level 38 kill mostly hands out things
    # worth having rather than a Linen Belt pattern from the bottom of a 200-entry list.
    cut = pool[max(0, len(pool) - max(8, len(pool) // 4)):]
    return rng.choice(cut)
