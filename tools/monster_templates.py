"""
Monster template data — the SINGLE source of truth for creature stat blocks.

WHY THIS FILE EXISTS
--------------------
There used to be two template tables that had drifted apart and nothing
connected them:

  * data/creatures/templates.json  — 15 templates, stats + archetype.
    Loaded by nothing. Completely dead data.
  * entities/monster.py MONSTER_TEMPLATES — 6 templates, hp/armor/attack/
    abilities. The only one the game actually read.

`Monster.__init__` did `MONSTER_TEMPLATES.get(type, MONSTER_TEMPLATES
["beast_basic"])`, so the 9 templates that existed only in JSON silently
became boars. 58 of 143 creatures — every centaur archer, harpy, murloc,
rogue, hound and undead in the game — were rolling Gore and Charge off a
beast stat block.

Now there is one table, it lives here, and it emits templates.json which
the runtime actually loads. Adding a template without combat stats is a
hard error, so this cannot silently regress.

FIELDS
------
  hp/armor/mres/atk/spell/mana   level-1 base values
  speed                          turn-meter rate
  crit                           crit %
  exp                            level-1 exp reward
  resource                       "rage" | "energy" | "mana"
  stats / scaling                the RPG stat block (kept from the old
                                 templates.json; used by loot and any
                                 future stat-driven damage formula)
  default_kit                    which moveset a creature of this template
                                 gets when creatures.json doesn't name one
"""

# (hp, armor, mres, atk, spell, mana, speed, crit, exp, resource, default_kit)
COMBAT = {
    "beast_basic":       (130,  8,  4, 18,  0,   0, 1.0,  5.0, 40, "rage",   "boar"),
    "beast_fast":        (100,  5,  4, 16,  0,   0, 1.4, 10.0, 45, "energy", "prowler"),
    "beast_large":       (190, 13,  6, 24,  0,   0, 0.8,  5.0, 60, "rage",   "large_beast"),
    "vermin_sneaky":     ( 95,  4,  6, 15,  0,   0, 1.2, 12.0, 40, "energy", "scorpid"),
    "vermin_swarm":      ( 60,  3,  3, 11,  0,   0, 1.5,  8.0, 25, "energy", "swarm"),
    "elemental_caster":  (110,  6, 14,  8, 20, 120, 0.9,  6.0, 55, "mana",   "elemental_fire"),
    "elemental_bruiser": (165, 16, 12, 20, 12, 100, 0.7,  5.0, 65, "mana",   "elemental_earth"),
    "humanoid_caster":   (105,  6, 12, 10, 18, 110, 1.0,  6.0, 55, "mana",   "cultist_shadow"),
    "humanoid_warrior":  (140, 12,  6, 20,  0,   0, 1.0,  7.0, 50, "rage",   "soldier"),
    "humanoid_ranged":   (110,  7,  6, 17,  0,   0, 1.1, 10.0, 50, "energy", "marksman"),
    "humanoid_rogue":    (105,  7,  6, 19,  0,   0, 1.3, 14.0, 50, "energy", "rogue"),
    "demon_hound":       (125,  8,  8, 21,  0,   0, 1.3,  9.0, 58, "energy", "demon_hound"),
    "demon_caster":      (115,  6, 12, 12, 19, 115, 1.0,  6.0, 58, "mana",   "demon_imp"),
    "aquatic_basic":     (115,  7,  8, 16,  8,  90, 1.0,  6.0, 48, "mana",   "murloc_hunter"),
    "undead_basic":      (120,  9, 10, 17,  0,   0, 0.9,  6.0, 50, "rage",   "undead_ghoul"),
}

# The RPG stat block, carried over unchanged from the old templates.json.
# (str, sta, int, spi, agi) then the per-level scaling of each.
STATS = {
    "beast_basic":       ((12, 11,  5,  5,  8), (0.90, 0.80, 0.20, 0.20, 0.40)),
    "beast_fast":        ((10,  7,  4,  4, 15), (0.70, 0.30, 0.10, 0.10, 1.00)),
    "beast_large":       ((16, 14,  5,  5,  5), (1.10, 0.90, 0.20, 0.20, 0.20)),
    "vermin_sneaky":     (( 9,  7,  6,  4, 13), (0.60, 0.30, 0.40, 0.20, 0.90)),
    "vermin_swarm":      (( 7,  5,  4,  3, 11), (0.40, 0.20, 0.10, 0.10, 0.80)),
    "elemental_caster":  (( 6,  9, 14,  9,  7), (0.20, 0.40, 0.90, 0.60, 0.20)),
    "elemental_bruiser": ((14, 12, 11,  9,  5), (0.90, 0.80, 0.70, 0.50, 0.20)),
    "humanoid_caster":   (( 7,  9, 15, 11,  8), (0.30, 0.40, 1.00, 0.70, 0.30)),
    "humanoid_warrior":  ((13, 12,  7,  7,  9), (0.95, 0.85, 0.20, 0.20, 0.30)),
    "humanoid_ranged":   ((11, 10,  8,  7, 14), (0.60, 0.40, 0.20, 0.20, 0.95)),
    "humanoid_rogue":    ((11,  9,  9,  7, 16), (0.80, 0.30, 0.30, 0.20, 1.00)),
    "demon_hound":       ((14, 10,  7,  8, 12), (0.95, 0.40, 0.30, 0.40, 0.85)),
    "demon_caster":      (( 8,  9, 14, 10,  9), (0.30, 0.40, 0.90, 0.60, 0.30)),
    "aquatic_basic":     ((11, 10,  9,  7,  9), (0.80, 0.60, 0.40, 0.30, 0.40)),
    "undead_basic":      ((12, 11,  7,  9,  8), (0.85, 0.75, 0.20, 0.50, 0.30)),
}

_STAT_KEYS = ("strength", "stamina", "intellect", "spirit", "agility")


def build():
    missing = set(STATS) ^ set(COMBAT)
    if missing:
        raise ValueError(
            f"Template tables disagree — this is exactly the drift that "
            f"turned 58 creatures into boars. Mismatched: {sorted(missing)}")

    out = {}
    for key, (hp, armor, mres, atk, spell, mana,
              speed, crit, exp, resource, kit) in COMBAT.items():
        base, scale = STATS[key]
        out[key] = {
            "name": key.replace("_", " ").title(),
            "base_hp": hp,
            "base_armor": armor,
            "base_magic_resist": mres,
            "base_attack": atk,
            "base_spell_power": spell,
            "base_mana": mana,
            "speed": speed,
            "crit_chance": crit,
            "exp_reward": exp,
            "resource_type": resource,
            "default_kit": kit,
            "base_stats": dict(zip(_STAT_KEYS, base)),
            "level_scaling": dict(zip(_STAT_KEYS, scale)),
        }
    return {"templates": out}
