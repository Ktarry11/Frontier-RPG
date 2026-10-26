"""Leather for Leatherworking: beasts drop leather when the killer has Skinning.

Only characters who know the Skinning profession can skin a defeated beast.
The leather tier tracks the 40-entry ladder in materials.json and mirrors the
cloth_drops.py band structure: overlapping level windows produce a gradual
cross-fade so players see new leathers creeping in rather than hard cut-offs.

Families that can be skinned (open to extension):
    beast – the primary source
Families that CANNOT be skinned:
    humanoid, undead, elemental, demon, insect, aquatic, plant

The 40-leather ladder:
    Early  (scrap, light, medium, heavy)              levels  1-25
    Mid    (thick .. dredged)                         levels 18-50
    Late   (fiendish .. bloodtanned)                  levels 40-70
    Endgame (wyvern .. genesis)                       levels 60+
"""
import random
import re

from entities.vendor_trash import classify

# Only these families yield leather
SKINNABLE = {"beast"}

# ──────────────────────────────────────────────────────────────────────────────
# Each entry: (min_level, max_level, {material_id: weight})
# ──────────────────────────────────────────────────────────────────────────────
BANDS = [
    # ── Early ──────────────────────────────────────────────────────────────────
    (1,  12,  {"leather_scrap": 3}),
    (8,  18,  {"leather_scrap": 2, "leather_light": 2}),
    (14, 22,  {"leather_light": 3, "leather_medium": 1}),
    (18, 28,  {"leather_light": 2, "leather_medium": 2, "leather_heavy": 1}),
    (22, 30,  {"leather_medium": 2, "leather_heavy": 2}),
    # ── Mid ────────────────────────────────────────────────────────────────────
    (18, 28,  {"leather_thick": 1}),
    (24, 34,  {"leather_heavy": 1, "leather_thick": 2, "leather_rugged": 1}),
    (30, 40,  {"leather_thick": 2, "leather_rugged": 2, "leather_cragscale": 1}),
    (36, 46,  {"leather_rugged": 2, "leather_cragscale": 2, "leather_stormscale": 1}),
    (42, 52,  {"leather_cragscale": 1, "leather_stormscale": 2, "leather_stonebound": 2}),
    (48, 58,  {"leather_stormscale": 1, "leather_stonebound": 2, "leather_dredged": 2}),
    # ── Late ───────────────────────────────────────────────────────────────────
    (40, 50,  {"leather_fiendish": 1}),
    (46, 56,  {"leather_dredged": 1, "leather_fiendish": 2, "leather_pristine": 1}),
    (52, 62,  {"leather_fiendish": 2, "leather_pristine": 2, "leather_savage": 1}),
    (58, 68,  {"leather_pristine": 1, "leather_savage": 2, "leather_frostscale": 2}),
    (62, 72,  {"leather_savage": 1, "leather_frostscale": 2, "leather_emberscale": 2, "leather_mossback": 1}),
    (66, 76,  {"leather_emberscale": 2, "leather_mossback": 2, "leather_duskfang": 1}),
    (70, 80,  {"leather_mossback": 1, "leather_duskfang": 2, "leather_bloodtanned": 2}),
    # ── Endgame ────────────────────────────────────────────────────────────────
    (60, 70,  {"leather_wyvern": 1}),
    (64, 74,  {"leather_wyvern": 2, "leather_basilisk": 1}),
    (68, 78,  {"leather_wyvern": 1, "leather_basilisk": 2, "leather_hydra": 1}),
    (72, 82,  {"leather_basilisk": 1, "leather_hydra": 2, "leather_netherdrake": 1}),
    (76, 86,  {"leather_hydra": 1, "leather_netherdrake": 2, "leather_frostwyrm": 1, "leather_behemoth": 1}),
    (80, 90,  {"leather_netherdrake": 1, "leather_frostwyrm": 2, "leather_behemoth": 2, "leather_manticore": 1}),
    (84, 94,  {"leather_manticore": 2, "leather_chimera": 2, "leather_phoenix": 1}),
    (88, 98,  {"leather_chimera": 1, "leather_phoenix": 2, "leather_kraken": 2}),
    (92, 99,  {"leather_kraken": 1, "leather_thunderlizard": 2, "leather_nightsaber": 2, "leather_lavahound": 1}),
    (95, 99,  {"leather_lavahound": 1, "leather_sandwurm": 2, "leather_voidstalker": 2, "leather_dreamstag": 1}),
    (97, 99,  {"leather_voidstalker": 1, "leather_dreamstag": 2, "leather_sunhawk": 2, "leather_chronodrake": 1}),
    (98, 99,  {"leather_chronodrake": 1, "leather_abyssal": 2, "leather_worldserpent": 2,
                "leather_primordial": 1, "leather_genesis": 1}),
]

# Base drop chance and quantity
CHANCE = {"open_zone": 0.70, "cave": 0.80}   # higher than cloth since beasts are the *only* source
NORMAL_QTY = (1, 2)
BOSS_QTY = (3, 5)


def _pick_material(level: int, rng) -> str:
    """Return a leather material_id appropriate for `level`."""
    pool: dict[str, float] = {}
    for lo, hi, weights in BANDS:
        if lo <= level <= hi:
            for mat, w in weights.items():
                pool[mat] = pool.get(mat, 0.0) + w
    if not pool:
        return "leather_genesis" if level >= 95 else "leather_scrap"
    return rng.choices(list(pool), weights=list(pool.values()), k=1)[0]


def roll_leather(enemy, player=None, rng=random):
    """Return [(material_id, quantity)] from skinning a defeated beast.

    Parameters
    ----------
    enemy:
        The defeated enemy object (must have .name, .level, optionally .is_boss
        and .location_type attributes).
    player:
        The player Character.  If None (e.g. during tests), skinning check is
        skipped and leather always drops.  If provided, the player must know the
        Skinning profession.
    rng:
        RNG instance (defaults to stdlib random for easy testing).
    """
    # Profession gate — only skinners get leather
    if player is not None and not getattr(player, "knows_profession", lambda p: True)("skinning"):
        return []

    # Family gate — only skinnable creatures
    name = getattr(enemy, "name", "")
    family, _coin = classify(name)
    if family not in SKINNABLE:
        return []

    level = max(1, int(getattr(enemy, "level", 1)))

    if getattr(enemy, "is_boss", False):
        return [(_pick_material(level, rng), rng.randint(*BOSS_QTY))]

    location_type = getattr(enemy, "location_type", "open_zone")
    place = "cave" if location_type == "cave" else "open_zone"
    if rng.random() < CHANCE[place]:
        qty = rng.randint(*NORMAL_QTY)
        return [(_pick_material(level, rng), qty)]

    return []
