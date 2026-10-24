"""Cloth for Tailoring (Oct 2026): humanoid-shaped creatures drop Linen / Wool / Silk Cloth by level.

WoW logic, same as coin: only sentient, clothed things (gnolls, quilboar, Forsaken, bandits...) carry cloth - beasts,
elementals, insects and undead husks do not, and murlocs (no clothes) are left out per the vendor-trash design note.
Linen is the early cloth, Wool the mid cloth, Silk the late-mid cloth, with overlapping level bands so the changeover is
gradual.  Bosses always drop a handful.
"""
import random
import re

from entities.vendor_trash import classify

NO_CLOTH = re.compile(r"murloc", re.I)

#: (min_level, max_level, {material: weight})
BANDS = [
    (1, 15, {"cloth_linen": 1.0}),
    (10, 26, {"cloth_linen": 1.0, "cloth_wool": 2.0}),
    (18, 36, {"cloth_wool": 2.0, "cloth_silk": 1.0}),
    (30, 99, {"cloth_wool": 1.0, "cloth_silk": 2.0}),
]
CHANCE = {"open_zone": 0.35, "cave": 0.5}
BOSS_QTY = (2, 4)


def _pick_material(level, rng):
    pool = {}
    for lo, hi, weights in BANDS:
        if lo <= level <= hi:
            for mid, w in weights.items():
                pool[mid] = pool.get(mid, 0) + w
    if not pool:
        return "cloth_silk" if level > 36 else "cloth_linen"
    return rng.choices(list(pool), weights=list(pool.values()), k=1)[0]


def roll_cloth(enemy, rng=random):
    """-> [(material_id, quantity)] dropped by one defeated enemy (usually empty)."""
    name = getattr(enemy, "name", "")
    if NO_CLOTH.search(name):
        return []
    family, _coin = classify(name)
    if family != "humanoid":
        return []
    level = max(1, int(getattr(enemy, "level", 1)))
    if getattr(enemy, "is_boss", False):
        return [(_pick_material(level, rng), rng.randint(*BOSS_QTY))]
    place = "cave" if getattr(enemy, "location_type", "open_zone") == "cave" else "open_zone"
    if rng.random() < CHANCE[place]:
        return [(_pick_material(level, rng), 1 if rng.random() < 0.75 else 2)]
    return []
