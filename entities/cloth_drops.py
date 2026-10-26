"""Cloth for Tailoring: humanoid-shaped creatures drop cloth by level.

WoW logic: only sentient, clothed things (gnolls, quilboar, Forsaken, bandits, cultists,
pirates, trolls, ogres, etc.) carry cloth.  Beasts, elementals, insects, and undead husks
do not.  Murlocs are excluded per the vendor-trash design note (no clothes).

The 40-cloth ladder is split into four bands that overlap so the changeover is gradual:

    Early  (cloth_linen, wool, cotton, hempen)       levels  1-25
    Mid    (cloth_silk .. thistledown)               levels 18-50
    Late   (cloth_runecloth .. bloodsilk)            levels 40-70
    Endgame (cloth_felcloth .. primordial_weave)     levels 60+

Within each band the weight of newer cloths ramps up as level rises so players
naturally graduate from Linen to Wool to Cotton etc. without hard cut-offs.
"""
import random
import re

from entities.vendor_trash import classify

NO_CLOTH = re.compile(r"murloc", re.I)

# ──────────────────────────────────────────────────────────────────────────────
# Each entry: (min_level, max_level, {material_id: base_weight})
# Overlapping bands produce the gradual cross-fade.  Within a single band the
# weight of each cloth can be 1-3 (higher = more common within that window).
# ──────────────────────────────────────────────────────────────────────────────
BANDS = [
    # ── Early ──────────────────────────────────────────────────────────────────
    (1,  12,  {"cloth_linen": 3}),
    (8,  18,  {"cloth_linen": 2, "cloth_wool": 2}),
    (14, 22,  {"cloth_wool": 3, "cloth_cotton": 1}),
    (18, 28,  {"cloth_wool": 2, "cloth_cotton": 2, "cloth_hempen": 1}),
    (22, 30,  {"cloth_cotton": 2, "cloth_hempen": 2}),
    # ── Mid ────────────────────────────────────────────────────────────────────
    (18, 28,  {"cloth_silk": 1}),
    (24, 34,  {"cloth_hempen": 1, "cloth_silk": 2, "cloth_mageweave": 1}),
    (30, 40,  {"cloth_silk": 2, "cloth_mageweave": 2, "cloth_spidersilk": 1}),
    (36, 46,  {"cloth_mageweave": 2, "cloth_spidersilk": 2, "cloth_dusk_velvet": 1}),
    (42, 52,  {"cloth_spidersilk": 1, "cloth_dusk_velvet": 2, "cloth_gossamer": 2}),
    (48, 58,  {"cloth_dusk_velvet": 1, "cloth_gossamer": 2, "cloth_thistledown": 2}),
    # ── Late ───────────────────────────────────────────────────────────────────
    (40, 50,  {"cloth_runecloth": 1}),
    (46, 56,  {"cloth_thistledown": 1, "cloth_runecloth": 2, "cloth_netherweave": 1}),
    (52, 62,  {"cloth_runecloth": 2, "cloth_netherweave": 2, "cloth_frostweave": 1}),
    (58, 68,  {"cloth_netherweave": 1, "cloth_frostweave": 2, "cloth_emberweave": 2}),
    (62, 72,  {"cloth_frostweave": 1, "cloth_emberweave": 2, "cloth_moonsilk": 2, "cloth_shadowsilk": 1}),
    (66, 76,  {"cloth_moonsilk": 2, "cloth_shadowsilk": 2, "cloth_starweave": 1}),
    (70, 80,  {"cloth_shadowsilk": 1, "cloth_starweave": 2, "cloth_bloodsilk": 2}),
    # ── Endgame ────────────────────────────────────────────────────────────────
    (60, 70,  {"cloth_felcloth": 1}),
    (64, 74,  {"cloth_felcloth": 2, "cloth_soulcloth": 1}),
    (68, 78,  {"cloth_felcloth": 1, "cloth_soulcloth": 2, "cloth_windwool": 1}),
    (72, 82,  {"cloth_soulcloth": 1, "cloth_windwool": 2, "cloth_imperial_silk": 1}),
    (76, 86,  {"cloth_windwool": 1, "cloth_imperial_silk": 2, "cloth_voidweave": 1, "cloth_sunthread": 1}),
    (80, 90,  {"cloth_imperial_silk": 1, "cloth_voidweave": 2, "cloth_sunthread": 2, "cloth_dreamsilk": 1}),
    (84, 94,  {"cloth_dreamsilk": 2, "cloth_chronoweave": 2, "cloth_abyssal_velvet": 1}),
    (88, 98,  {"cloth_chronoweave": 1, "cloth_abyssal_velvet": 2, "cloth_stormweave": 2}),
    (92, 99,  {"cloth_stormweave": 1, "cloth_lightwoven": 2, "cloth_wyrmsilk": 2, "cloth_phoenix_cloth": 1}),
    (95, 99,  {"cloth_lightwoven": 1, "cloth_phoenix_cloth": 2, "cloth_arcanoweave": 2, "cloth_titanweave": 1}),
    (97, 99,  {"cloth_arcanoweave": 1, "cloth_titanweave": 2, "cloth_spiritwoven": 2, "cloth_nightmare_lace": 1}),
    (98, 99,  {"cloth_spiritwoven": 1, "cloth_nightmare_lace": 2, "cloth_ghostgauze": 2, "cloth_starsilk": 1,
                "cloth_worldweave": 1, "cloth_genesis_cloth": 1, "cloth_primordial_weave": 1}),
]

CHANCE = {"open_zone": 0.35, "cave": 0.50}
BOSS_QTY = (2, 4)


def _pick_material(level: int, rng) -> str:
    """Return a cloth material_id appropriate for `level`."""
    pool: dict[str, float] = {}
    for lo, hi, weights in BANDS:
        if lo <= level <= hi:
            for mid, w in weights.items():
                pool[mid] = pool.get(mid, 0.0) + w
    if not pool:
        # Fallback: lowest or highest depending on level
        return "cloth_primordial_weave" if level >= 95 else "cloth_linen"
    return rng.choices(list(pool), weights=list(pool.values()), k=1)[0]


def roll_cloth(enemy, rng=random):
    """Return [(material_id, quantity)] dropped by one defeated enemy (usually [])."""
    name = getattr(enemy, "name", "")
    if NO_CLOTH.search(name):
        return []
    family, _coin = classify(name)
    if family != "humanoid":
        return []
    level = max(1, int(getattr(enemy, "level", 1)))
    if getattr(enemy, "is_boss", False):
        return [(_pick_material(level, rng), rng.randint(*BOSS_QTY))]
    location_type = getattr(enemy, "location_type", "open_zone")
    place = "cave" if location_type == "cave" else "open_zone"
    if rng.random() < CHANCE[place]:
        qty = 1 if rng.random() < 0.75 else 2
        return [(_pick_material(level, rng), qty)]
    return []
