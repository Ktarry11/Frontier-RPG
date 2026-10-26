"""Essences for Engineering: elementals yield essence when the killer has
Essence Harvesting.

Mirrors entities/skinning_drops.py exactly in shape and in gating, because
this is the same kind of thing: a kill-based gathering feed for one crafting
profession. Skinning is to beasts and Leatherworking what this is to
elementals and Engineering.

WHY ELEMENTALS
--------------
52 elemental creatures already exist in the world (elemental_bruiser 36,
elemental_caster 16) and fed NO profession - cloth comes off
humanoid/undead/demon, leather off beasts, and elementals dropped only coin
and vendor trash. They are already spread across the zone level bands that
exist, so this needs no new zones and no new creatures.

The other half of Essence Harvesting is node-based: crystal nodes in
node_pools.json, gathered exactly like ore and herbs. One skill covers both
halves, the way Mining covers veins and smelting.

WHICH ESSENCE DROPS
-------------------
Bands overlap deliberately so tiers cross-fade rather than switching over at
a hard level boundary - the same authoring style skinning_drops.py uses. The
elemental's LEVEL picks the band, not the player's skill, matching this
codebase's convention everywhere else that loot is gated on the mob.

Families that yield essence:
    elemental - the only source.
Everything else (beast, humanoid, undead, demon, insect, aquatic, plant)
yields nothing here; beasts go through skinning_drops instead.
"""
import random

from entities.vendor_trash import classify

#: Only elementals. classify() returns the family from the creature's
#: template, so this matches elemental_bruiser and elemental_caster alike
#: without naming either.
HARVESTABLE = {"elemental"}

#: Bosses give a handful rather than one, same convention as skinning.
BOSS_QTY = (2, 4)

# ──────────────────────────────────────────────────────────────────────────
# (min_level, max_level, {material_id: weight})
# ──────────────────────────────────────────────────────────────────────────
BANDS = [
    # ---- early: the four lesser motes, by element ------------------------
    (1,  8,  {"essence_cinder": 2, "essence_runoff": 2, "essence_grit": 2}),
    (4,  12, {"essence_cinder": 2, "essence_runoff": 2, "essence_grit": 2, "essence_draft": 2}),
    (8,  16, {"essence_cinder": 2, "essence_runoff": 2, "essence_grit": 2,
              "essence_draft": 2, "essence_static": 1}),
    # ---- the turn: motes thinning, hearts appearing -----------------------
    (14, 22, {"essence_draft": 2, "essence_static": 2, "essence_grit": 1,
              "essence_ember": 1, "essence_brine": 1}),
    (18, 26, {"essence_static": 1, "essence_ember": 2, "essence_brine": 2,
              "essence_granite": 2, "essence_gale": 1}),
    # ---- mid: hearts, with Umbral only off the deepest things ------------
    (24, 34, {"essence_ember": 2, "essence_brine": 2, "essence_granite": 2,
              "essence_gale": 2, "essence_umbral": 1}),
    (30, 99, {"essence_ember": 1, "essence_brine": 1, "essence_granite": 1,
              "essence_gale": 2, "essence_umbral": 3}),
]


def _pick_material(level, rng):
    """Weighted pick across every band whose range covers `level`.

    Overlapping bands are merged rather than first-match, so a level sitting
    in two bands genuinely blends them - that is what produces the gradual
    cross-fade between tiers instead of a hard switch.
    """
    table = {}
    for lo, hi, weights in BANDS:
        if lo <= level <= hi:
            for mid, w in weights.items():
                table[mid] = table.get(mid, 0) + w
    if not table:
        # Above every authored band (or below band 1, which cannot happen
        # since level is clamped to >= 1): fall back to the highest band
        # rather than returning nothing, so a future level-99 elemental
        # still yields something.
        table = BANDS[-1][2]
    mats = list(table)
    return rng.choices(mats, weights=[table[m] for m in mats], k=1)[0]


def roll_essence(enemy, player=None, rng=random):
    """Return [(material_id, quantity)] from harvesting a defeated elemental.

    Same rule as skinning: every elemental yields exactly 1 essence, 100% of
    the time, no RNG on whether you get one - the only gate is whether the
    player has learned Essence Harvesting. Bosses give 2-4.

    Parameters
    ----------
    enemy  : defeated enemy (needs .name, .level; optionally .is_boss)
    player : Character - must know essence_harvesting. None skips the check
             (for tests), matching roll_leather's signature.
    rng    : RNG instance (defaults to stdlib random).
    """
    if player is not None and not getattr(player, "knows_profession", lambda p: True)("essence_harvesting"):
        return []

    name = getattr(enemy, "name", "")
    family, _coin = classify(name)
    if family not in HARVESTABLE:
        return []

    level = max(1, int(getattr(enemy, "level", 1)))

    if getattr(enemy, "is_boss", False):
        return [(_pick_material(level, rng), rng.randint(*BOSS_QTY))]

    return [(_pick_material(level, rng), 1)]
