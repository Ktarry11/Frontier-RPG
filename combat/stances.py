"""
Warrior stance system.

Real WOTLK 3.3.5 mechanics (Warrior stances - Wowpedia, Icy Veins spell
summaries, verified against multiple sources):
  Battle Stance:     +10% Armor Penetration. Gates Charge, Overpower,
                      Mocking Blow.
  Defensive Stance:  -10% damage taken, -5% damage dealt, +45% threat
                      generation. Gates Disarm, Revenge, Shield Block,
                      Shield Slam, Shield Bash, Intervene.
  Berserker Stance:  +3% critical strike chance, +5% damage taken. Gates
                      Intercept, Whirlwind, Recklessness, Berserker Rage.

Simplifications, documented rather than silently guessed:
  - No stance-dance quest chain (real WOTLK: Defensive Stance from a
    level-10 quest, Berserker Stance from a level-30 quest chain). Gated
    by character level alone instead - matches how every other ability
    in this engine unlocks.
  - Armor Penetration doesn't exist as a real mechanic here (no gear
    system models it, and combat has no "ignore X% of target's armor"
    hook). Battle Stance's +10% Armor Pen is approximated as a flat
    physical-damage bonus instead - the real gameplay effect of armor
    pen (more damage against armored targets) without needing to build
    the underlying stat.
  - Threat/aggro has no representation in this engine at all (no
    positioning/targeting-priority system for monster AI to read).
    Defensive Stance's +45% threat is dropped entirely rather than faked
    with an unread stat - there's nothing for it to meaningfully affect.
"""

# Which stat_mods key(s) each stance contributes to the same bonus pool
# gear/talents/status-effects already share (see
# Character._recalculate_derived_stats). Values use the same 0-100 scale
# as everywhere else in this codebase (e.g. crit_chance_physical: 3.0
# means "+3%"), NOT a 0.0-1.0 fraction.
STANCES = {
    "battle": {
        "name": "Battle Stance",
        "level_req": 1,
        "description": (
            "Increases physical damage dealt. Real WOTLK grants +10% Armor "
            "Penetration - approximated here as a flat physical-damage bonus "
            "since no armor-penetration mechanic exists to model the real "
            "effect directly."
        ),
        "stat_mods": {
            "physical_damage": 0.05,
        },
        # Ability IDs only usable while in this stance. Empty for now -
        # Charge/Overpower/Mocking Blow aren't in this engine's Warrior kit
        # yet; populated once those are added in the full-kit pass.
        "gated_abilities": [],
    },
    "defensive": {
        "name": "Defensive Stance",
        "level_req": 10,
        "description": (
            "Reduces damage taken by 10% and damage dealt by 5%. Real WOTLK "
            "also grants +45% threat generation - dropped entirely since "
            "this engine has no threat/aggro system for it to affect."
        ),
        "stat_mods": {
            "damage_taken_pct": -0.10,
            "all_damage": -0.05,
        },
        "gated_abilities": [],
    },
    "berserker": {
        "name": "Berserker Stance",
        "level_req": 30,
        "description": (
            "Increases critical strike chance by 3%, but increases damage "
            "taken by 5%."
        ),
        "stat_mods": {
            "crit_chance_physical": 3.0,
            "damage_taken_pct": 0.05,
        },
        "gated_abilities": [],
    },
}

#: Real WOTLK charges 10 Rage to switch stances (reduced/refunded by the
#: Tactical Mastery talent, not modeled here - see docstring above).
STANCE_SWITCH_COST = 10


def get_stance(stance_id):
    return STANCES.get(stance_id)


def available_stances(level):
    """Every stance this level already qualifies for, in a stable order."""
    return [sid for sid, s in STANCES.items() if level >= s["level_req"]]
