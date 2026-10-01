"""
Earthen Guardian - Shaman Tank toggle (Phase 6, "Shaman Tank" bolted onto
Enhancement per Kyle).

Modeled as a PERSISTENT on/off toggle, same spirit as Druid's
current_form (combat/forms.py) - stays active across multiple fights
until explicitly turned off, not a per-fight stance and not a
timed buff. Deliberately its OWN small module rather than reusing
forms.py or stances.py directly:
  - forms.py resets current_mana/rage/energy to 0 on every shift (real
    Druid behavior, since forms swap resource pools). Earthen Guardian
    doesn't change resource pool at all - it's still Mana - so wiping a
    Shaman's mana bar every time they toggle a stance would be an
    unrelated, unwanted side effect inherited from a different class's
    mechanic.
  - stances.py (Warrior) hardcodes current_stance=None for every
    non-Warrior class in Character.can_use_stance, and set_stance()
    unconditionally charges Rage to switch - both wrong for a Shaman
    toggle that costs Mana to activate and nothing to maintain or turn
    off.

Per Kyle: cost is intentionally cheap, NOT the 820 Mana shown in his
level-60 reference screenshot (that number was scaled for a max-level
Shaman's huge mana pool, not a sane baseline activation cost).
"""

EARTHEN_GUARDIAN = {
    "name": "Earthen Guardian",
    "class": "Shaman",
    "level_req": 10,
    "activation_cost": 60,  # flat Mana cost to toggle ON; toggling OFF is free
    "description": (
        "Reduces all damage taken by 5% but also reduces damage and "
        "healing done by 20%. In addition, threat generated is increased "
        "by 200% (3x total) and Wind Shear no longer costs threat."
    ),
    "stat_mods": {
        "damage_taken_pct": -0.05,
        "all_damage": -0.20,
        "healing_done": -0.20,
    },
    # Read by CombatEngine._generate_threat_from_ability via
    # Character.get_talent_effect("threat_multiplier") - 200% MORE threat
    # means 3x total, not 2x.
    "threat_multiplier": 3.0,
}


def get_guardian_stance():
    return EARTHEN_GUARDIAN
