"""Leather for Leatherworking: beasts drop leather when the killer has Skinning.

WoW anchor leathers (recognizable milestone tiers) woven throughout the ladder:
    leather_scrap   → mob levels  5-17   (WoW: Ruined Leather Scraps)
    leather_light   → mob levels  5-27   (WoW: Light Leather)
    leather_medium  → mob levels 15-38   (WoW: Medium Leather)
    leather_heavy   → mob levels 26-46   (WoW: Heavy Leather)
    leather_thick   → mob levels 35-58   (WoW: Thick Leather)
    leather_rugged  → mob levels 45-60   (WoW: Rugged Leather)

Frontier leathers weave in throughout — some appear BEFORE the WoW anchors
(e.g. cragscale creeping in at 28 alongside Heavy), some fill gaps, some
extend past Rugged into pure Frontier endgame (tiers 19-40, levels 60-99).

Families that can be skinned:
    beast – the only source of leather
Everything else (humanoid, undead, elemental, demon, insect, aquatic, plant) cannot.
"""
import random

from entities.material_tiers import HIGH_TIER_FLOOR, in_reach
from entities.vendor_trash import classify

SKINNABLE = {"beast"}

# ──────────────────────────────────────────────────────────────────────────────
# Each entry: (min_level, max_level, {material_id: weight})
# Overlapping bands produce a gradual cross-fade.
# WoW anchors are marked with their tier index for readability.
# ──────────────────────────────────────────────────────────────────────────────
BANDS = [
    # ── Very early — before Light Leather kicks in ─────────────────────────────
    (1,   8,  {"leather_scrap": 4}),                                              # only scraps at the start
    (5,  14,  {"leather_scrap": 3, "leather_light": 1}),                          # Light (T2) creeps in
    (10, 20,  {"leather_scrap": 2, "leather_light": 3}),                          # Light dominant, scraps fade
    # ── Early — Light dominant, Medium and first Frontier tiers mix in ─────────
    (15, 24,  {"leather_light": 3, "leather_medium": 1}),                         # Medium (T3) first appears
    (18, 28,  {"leather_light": 2, "leather_medium": 2, "leather_heavy": 1}),     # Heavy (T4) first appears at 18 — early hint
    (22, 32,  {"leather_medium": 3, "leather_heavy": 1, "leather_cragscale": 1}), # Cragscale (T7) weaves in — Frontier
    # ── Early-mid — Medium/Heavy dominant, Frontier filling gaps ───────────────
    (26, 36,  {"leather_medium": 2, "leather_heavy": 2, "leather_cragscale": 2}),
    (30, 40,  {"leather_heavy": 3, "leather_cragscale": 2, "leather_stormscale": 1}), # Stormscale (T8)
    (34, 44,  {"leather_heavy": 2, "leather_thick": 1, "leather_cragscale": 1, "leather_stormscale": 2}), # Thick (T5) first appears
    # ── Mid — Heavy fades, Thick and Frontier tiers take over ──────────────────
    (38, 48,  {"leather_thick": 2, "leather_stormscale": 2, "leather_stonebound": 1}), # Stonebound (T9)
    (42, 52,  {"leather_thick": 3, "leather_stonebound": 2, "leather_rugged": 1}),     # Rugged (T6) first appears
    (45, 55,  {"leather_thick": 2, "leather_rugged": 2, "leather_stonebound": 1, "leather_dredged": 1}), # Dredged (T10)
    # ── Mid-late — Rugged dominant, Frontier late tiers mixing in ──────────────
    (48, 58,  {"leather_rugged": 3, "leather_dredged": 2, "leather_fiendish": 1}),     # Fiendish (T11)
    (52, 62,  {"leather_rugged": 2, "leather_dredged": 1, "leather_fiendish": 2, "leather_pristine": 1}), # Pristine (T12)
    (56, 66,  {"leather_rugged": 1, "leather_fiendish": 2, "leather_pristine": 2, "leather_savage": 1}),  # Savage (T13)
    # ── Late — Rugged fades, Frontier late tiers dominant ──────────────────────
    (60, 70,  {"leather_fiendish": 1, "leather_pristine": 2, "leather_savage": 2, "leather_frostscale": 1}), # Frostscale (T14)
    (63, 73,  {"leather_savage": 2, "leather_frostscale": 2, "leather_emberscale": 1}),                       # Emberscale (T15)
    (66, 76,  {"leather_frostscale": 1, "leather_emberscale": 2, "leather_mossback": 2, "leather_duskfang": 1}), # Mossback (T16), Duskfang (T17)
    (70, 80,  {"leather_emberscale": 1, "leather_mossback": 2, "leather_duskfang": 2, "leather_bloodtanned": 1}), # Bloodtanned (T18)
    # ── Late-endgame — Frontier tiers 19-28 ────────────────────────────────────
    (65, 75,  {"leather_wyvern": 1}),                                                 # Wyvern (T19) — rare early endgame hint
    (68, 78,  {"leather_wyvern": 2, "leather_basilisk": 1}),                          # Basilisk (T20)
    (72, 82,  {"leather_wyvern": 1, "leather_basilisk": 2, "leather_hydra": 1}),      # Hydra (T21)
    (76, 86,  {"leather_basilisk": 1, "leather_hydra": 2, "leather_netherdrake": 1}), # Netherdrake (T22)
    (80, 90,  {"leather_hydra": 1, "leather_netherdrake": 2, "leather_frostwyrm": 1, "leather_behemoth": 1}), # T23/T24
    (83, 92,  {"leather_netherdrake": 1, "leather_frostwyrm": 2, "leather_behemoth": 2, "leather_manticore": 1}), # T25
    (86, 95,  {"leather_manticore": 2, "leather_chimera": 2, "leather_phoenix": 1}),  # T26/T27
    (89, 97,  {"leather_chimera": 1, "leather_phoenix": 2, "leather_kraken": 2}),     # T28
    # ── Pure endgame — Frontier tiers 29-40 ────────────────────────────────────
    (92, 99,  {"leather_kraken": 1, "leather_thunderlizard": 2, "leather_nightsaber": 2, "leather_lavahound": 1}),
    (95, 99,  {"leather_lavahound": 1, "leather_sandwurm": 2, "leather_voidstalker": 2, "leather_dreamstag": 1}),
    (97, 99,  {"leather_voidstalker": 1, "leather_dreamstag": 2, "leather_sunhawk": 2, "leather_chronodrake": 1}),
    (98, 99,  {"leather_chronodrake": 1, "leather_abyssal": 2, "leather_worldserpent": 2,
               "leather_primordial": 1, "leather_genesis": 1}),
]

BOSS_QTY = (2, 4)   # bosses give a small extra handful


def _pick_material(level: int, rng) -> str:
    pool: dict[str, float] = {}
    for lo, hi, weights in BANDS:
        if lo <= level <= hi:
            for mat, w in in_reach(weights, level).items():
                pool[mat] = pool.get(mat, 0.0) + w
    if not pool:
        # Same boundary case as cloth: see entities/material_tiers.in_reach. Rugged is the top rung
        # a sub-60 skinner is allowed to hold.
        if level < HIGH_TIER_FLOOR:
            return "leather_rugged" if level >= 42 else "leather_scrap"
        return "leather_genesis" if level >= 95 else "leather_scrap"
    return rng.choices(list(pool), weights=list(pool.values()), k=1)[0]


def roll_leather(enemy, player=None, rng=random):
    """Return [(material_id, quantity)] from skinning a defeated beast.

    WoW rule: every beast yields exactly 1 leather when skinned — 100% rate,
    exactly 1 piece, no RNG on whether you get it. The only gate is whether the
    player has learned the Skinning profession. Bosses are generous (2-4 pieces).

    Parameters
    ----------
    enemy  : defeated enemy (needs .name, .level; optionally .is_boss)
    player : Character — must know Skinning.  None skips the check (for tests).
    rng    : RNG instance (defaults to stdlib random).
    """
    if player is not None and not getattr(player, "knows_profession", lambda p: True)("skinning"):
        return []

    name = getattr(enemy, "name", "")
    family, _coin = classify(name)
    if family not in SKINNABLE:
        return []

    level = max(1, int(getattr(enemy, "level", 1)))

    if getattr(enemy, "is_boss", False):
        return [(_pick_material(level, rng), rng.randint(*BOSS_QTY))]

    # Normal beast: always exactly 1 leather — 100% rate, no luck involved.
    return [(_pick_material(level, rng), 1)]
