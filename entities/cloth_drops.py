"""Cloth for Tailoring: humanoid-shaped creatures drop cloth by level.

WoW anchor cloths (recognizable milestone tiers) woven throughout the ladder:
    cloth_linen      → mob levels  4-17   (WoW: Linen Cloth)
    cloth_wool       → mob levels 14-27   (WoW: Wool Cloth)
    cloth_silk       → mob levels 25-38   (WoW: Silk Cloth)
    cloth_mageweave  → mob levels 40-52   (WoW: Mageweave Cloth)
    cloth_runecloth  → mob levels 51-60+  (WoW: Runecloth)
    cloth_felcloth   → mob levels 53-60   (WoW: Felcloth — rare, zone-locked)

Frontier cloths weave in throughout — Cotton and Hempen slide between Linen
and Wool, Spidersilk and Dusk Velvet fill between Silk and Mageweave, etc.
Tiers 20-40 extend into pure Frontier endgame (levels 60-99).

Only sentient, clothed humanoids drop cloth — gnolls, quilboar, cultists,
bandits, trolls, ogres, forsaken, etc. Murlocs excluded (no clothes).
Beasts, elementals, insects, undead husks never drop cloth.
"""
import random
import re

from entities.vendor_trash import classify

NO_CLOTH = re.compile(r"murloc", re.I)

# ──────────────────────────────────────────────────────────────────────────────
# Each entry: (min_level, max_level, {material_id: weight})
# ──────────────────────────────────────────────────────────────────────────────
BANDS = [
    # ── Very early — Linen only ────────────────────────────────────────────────
    (1,   8,  {"cloth_linen": 4}),
    (4,  14,  {"cloth_linen": 3, "cloth_cotton": 1}),        # Cotton (T4) weaves in early — Frontier
    # ── Early — Linen fades, Cotton rises, Wool enters ────────────────────────
    (8,  18,  {"cloth_linen": 2, "cloth_cotton": 2, "cloth_wool": 1}),   # Wool (T2) first appears
    (12, 22,  {"cloth_cotton": 2, "cloth_wool": 2, "cloth_hempen": 1}),  # Hempen (T5) — Frontier filler
    (14, 24,  {"cloth_wool": 3, "cloth_hempen": 2}),
    # ── Early-mid — Wool dominant, Hempen and Silk mixing in ──────────────────
    (18, 28,  {"cloth_wool": 2, "cloth_hempen": 2, "cloth_silk": 1}),    # Silk (T3) first appears
    (22, 32,  {"cloth_hempen": 1, "cloth_silk": 2, "cloth_mageweave": 1}), # Mageweave (T6) early hint
    (25, 35,  {"cloth_silk": 3, "cloth_mageweave": 1, "cloth_spidersilk": 1}), # Spidersilk (T7) — Frontier
    # ── Mid — Silk fades, Mageweave and Frontier tiers dominant ───────────────
    (30, 40,  {"cloth_silk": 2, "cloth_mageweave": 2, "cloth_spidersilk": 2}),
    (34, 44,  {"cloth_mageweave": 3, "cloth_spidersilk": 2, "cloth_dusk_velvet": 1}), # Dusk Velvet (T8)
    (38, 48,  {"cloth_mageweave": 2, "cloth_spidersilk": 1, "cloth_dusk_velvet": 2, "cloth_gossamer": 1}), # Gossamer (T9)
    # ── Mid-late — Mageweave fades, Runecloth era begins ──────────────────────
    (42, 52,  {"cloth_mageweave": 1, "cloth_dusk_velvet": 2, "cloth_gossamer": 2, "cloth_thistledown": 1}), # Thistledown (T10)
    (46, 56,  {"cloth_gossamer": 2, "cloth_thistledown": 2, "cloth_runecloth": 1}),   # Runecloth (T11) first appears
    (50, 60,  {"cloth_thistledown": 1, "cloth_runecloth": 3, "cloth_netherweave": 1}), # Netherweave (T12)
    # ── Late — Runecloth dominant, Felcloth rare, Frontier extending ───────────
    (51, 62,  {"cloth_runecloth": 3, "cloth_netherweave": 2, "cloth_frostweave": 1}),  # Frostweave (T13)
    (53, 60,  {"cloth_felcloth": 1}),   # Felcloth (T19 WoW) — rare zone-locked drop alongside runecloth
    (55, 65,  {"cloth_runecloth": 2, "cloth_frostweave": 2, "cloth_emberweave": 1}),   # Emberweave (T14)
    (58, 68,  {"cloth_netherweave": 1, "cloth_frostweave": 2, "cloth_emberweave": 2, "cloth_moonsilk": 1}), # Moonsilk (T15)
    # ── Late-endgame — WoW tiers fade, Frontier tiers 16-20 dominant ──────────
    (62, 72,  {"cloth_frostweave": 1, "cloth_emberweave": 1, "cloth_moonsilk": 2, "cloth_shadowsilk": 2}), # Shadowsilk (T16)
    (65, 75,  {"cloth_moonsilk": 1, "cloth_shadowsilk": 2, "cloth_starweave": 2, "cloth_bloodsilk": 1}),   # Starweave (T17), Bloodsilk (T18)
    (68, 78,  {"cloth_shadowsilk": 1, "cloth_starweave": 2, "cloth_bloodsilk": 2, "cloth_soulcloth": 1}),  # Soulcloth (T20)
    (70, 80,  {"cloth_starweave": 1, "cloth_bloodsilk": 2, "cloth_soulcloth": 2, "cloth_felcloth": 1}),    # Felcloth rare again at endgame
    # ── Endgame — Frontier tiers 20-28 ────────────────────────────────────────
    (72, 82,  {"cloth_soulcloth": 2, "cloth_windwool": 2, "cloth_imperial_silk": 1}),  # T21/T22
    (76, 86,  {"cloth_windwool": 1, "cloth_imperial_silk": 2, "cloth_voidweave": 2, "cloth_sunthread": 1}),
    (80, 90,  {"cloth_imperial_silk": 1, "cloth_voidweave": 2, "cloth_sunthread": 2, "cloth_dreamsilk": 1}),
    (84, 94,  {"cloth_dreamsilk": 2, "cloth_chronoweave": 2, "cloth_abyssal_velvet": 1}),
    (88, 98,  {"cloth_chronoweave": 1, "cloth_abyssal_velvet": 2, "cloth_stormweave": 2}),
    # ── Pure endgame — Frontier tiers 29-40 ────────────────────────────────────
    (92, 99,  {"cloth_stormweave": 1, "cloth_lightwoven": 2, "cloth_wyrmsilk": 2, "cloth_phoenix_cloth": 1}),
    (95, 99,  {"cloth_lightwoven": 1, "cloth_phoenix_cloth": 2, "cloth_arcanoweave": 2, "cloth_titanweave": 1}),
    (97, 99,  {"cloth_arcanoweave": 1, "cloth_titanweave": 2, "cloth_spiritwoven": 2, "cloth_nightmare_lace": 1}),
    (98, 99,  {"cloth_spiritwoven": 1, "cloth_nightmare_lace": 2, "cloth_ghostgauze": 2, "cloth_starsilk": 1,
               "cloth_worldweave": 1, "cloth_genesis_cloth": 1, "cloth_primordial_weave": 1}),
]

CHANCE   = {"open_zone": 0.35, "cave": 0.50}
BOSS_QTY = (2, 4)


def _pick_material(level: int, rng) -> str:
    pool: dict[str, float] = {}
    for lo, hi, weights in BANDS:
        if lo <= level <= hi:
            for mid, w in weights.items():
                pool[mid] = pool.get(mid, 0.0) + w
    if not pool:
        return "cloth_primordial_weave" if level >= 95 else "cloth_linen"
    return rng.choices(list(pool), weights=list(pool.values()), k=1)[0]


def roll_cloth(enemy, rng=random):
    """Return [(material_id, quantity)] dropped by one defeated humanoid enemy.

    Cloth drops WITHOUT a Tailoring profession gate — any player can pick it up.
    The quantity is 1-3 raw cloth per kill (bosses get the full 2-4 range).
    Players need to craft raw cloth into bolts at the Tailoring bench before
    the cloth is useful, which is the in-game reason to learn Tailoring.

    Drop chance: 35% in open zones, 50% in caves (cloth-wearers congregate
    indoors in WoW and Frontier uses the same intuition).
    """
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
        # 1-3 cloth per kill: ~50% chance of 1, ~35% chance of 2, ~15% chance of 3
        roll = rng.random()
        qty = 1 if roll < 0.50 else (2 if roll < 0.85 else 3)
        return [(_pick_material(level, rng), qty)]
    return []
