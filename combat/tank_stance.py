"""
Tank postures: the one rule every tank class shares (Kyle, 27 Nov 2026).

    "Tanks should do less damage. Also make stances have more threat or eternal form, bear form etc. Or paladin
    righteous fury....all tank classes should get a 'stance' which reduces damage but improving threat"

A tank posture is whatever a class tanks in. Some classes already had one, and those keep it:
    Warrior        Defensive Stance (combat/stances.py)
    Druid          Bear Form and Dire Bear Form (combat/forms.py)
    Venomancer     Beetle Form
    Bloodmage      Eternal Curse
    Cultist        Void Monstrosity, and Twilight Domain below
    Shaman         Earthen Guardian (combat/guardian_stance.py, its own 3x threat_multiplier, untouched)
The rest get a toggle here (TANK_STANCES), cast from the hotbar like a shapeshift (effect_type "tank_stance") and
persistent across fights like a form: Righteous Fury for the Paladin, and one each for the other tank classes.

EVERY POSTURE IS THE SAME TRADE, so no tank is better at holding threat by accident: threat x3 (TANK_THREAT_PCT
+200, the percent-point convention the threat buffs use) and damage dealt -15% (TANK_DAMAGE, an all_damage fraction).
Postures do not stack: posture_threat_pct is the largest posture active, not a sum, so a Cultist in Void
Monstrosity with Twilight Domain up is still x3.

Threat from a posture is read ONLY through posture_threat_pct, never as a threat_generation_pct stat_mod. Forms and
stances are folded into Character.get_talent_effects, where threat_generation_pct means a talent FRACTION
(Defiance's 0.08 a rank), so a posture that put its percent points there was counted twice: Eternal Curse's 60
became 1.6 x 61, about 97x threat, from 26 to 27 Nov 2026.
"""

#: a tank posture's threat, percent points MORE (200 -> x3)
TANK_THREAT_PCT = 200.0
#: a tank posture's damage dealt, as an all_damage fraction (-0.15 -> 15% less)
TANK_DAMAGE = -0.15

#: the shapeshift forms that are tank postures
TANK_FORMS = frozenset({"bear", "dire_bear", "beetle", "eternal", "void_monstrosity"})
#: the Warrior stance that is a tank posture
TANK_WARRIOR_STANCE = "defensive"

#: the toggle each remaining tank class gets, keyed by class. stat_mods fold into get_talent_effects while it's on.
TANK_STANCES = {
    "Paladin": {
        "id": "righteous_fury", "name": "Righteous Fury", "level_req": 10,
        "description": "Holy fury draws every enemy's eye. Threat generated x3, damage dealt -15%. Stays on until "
                       "you cast it again.",
    },
    "Cultist": {
        "id": "twilight_domain", "name": "Twilight Domain", "level_req": 10,
        "description": "Wrap yourself in twilight that enemies can't look away from. Threat generated x3, damage "
                       "dealt -15%. Stays on until you cast it again.",
    },
    "Starcaller": {
        "id": "lunar_authority", "name": "Lunar Authority", "level_req": 10,
        "description": "Your presence under the moon commands attention. Threat generated x3, damage dealt -15%. "
                       "Stays on until you cast it again.",
    },
    "Felsworn": {
        "id": "tyrants_mantle", "name": "Tyrant's Mantle", "level_req": 10,
        "description": "Take up the mantle of a fel tyrant, and dare them to come at you. Threat generated x3, "
                       "damage dealt -15%. Stays on until you cast it again.",
    },
    "Guardian": {
        "id": "bulwark_stance", "name": "Bulwark Stance", "level_req": 10,
        "description": "Plant your feet behind the shield and hold the line. Threat generated x3, damage dealt "
                       "-15%. Stays on until you cast it again.",
    },
    "Knight of Xoroth": {
        "id": "aura_of_dread", "name": "Aura of Dread", "level_req": 10,
        "description": "Let dread pour off you until nothing else on the field matters. Threat generated x3, "
                       "damage dealt -15%. Stays on until you cast it again.",
    },
    "Primalist": {
        "id": "stoneheart", "name": "Stoneheart", "level_req": 10,
        "description": "Take the mountain's patience into your chest. Threat generated x3, damage dealt -15%. "
                       "Stays on until you cast it again.",
    },
    "Reaper": {
        "id": "dominion", "name": "Dominion", "level_req": 10,
        "description": "Claim every soul on the field as yours to collect. Threat generated x3, damage dealt -15%. "
                       "Stays on until you cast it again.",
    },
    "Sun Cleric": {
        "id": "seraphs_vigil", "name": "Seraph's Vigil", "level_req": 10,
        "description": "Burn like a beacon in front of your allies. Threat generated x3, damage dealt -15%. Stays "
                       "on until you cast it again.",
    },
    "Templar": {
        "id": "oath_of_the_wall", "name": "Oath of the Wall", "level_req": 10,
        "description": "Swear to stand between them and harm. Threat generated x3, damage dealt -15%. Stays on "
                       "until you cast it again.",
    },
    "Witch Hunter": {
        "id": "black_knights_vigil", "name": "Black Knight's Vigil", "level_req": 10,
        "description": "Mark yourself as the one they have to kill first. Threat generated x3, damage dealt -15%. "
                       "Stays on until you cast it again.",
    },
}
for _s in TANK_STANCES.values():
    _s["stat_mods"] = {"all_damage": TANK_DAMAGE}


def stance_for_class(char_class):
    return TANK_STANCES.get(char_class)


def stance_by_id(stance_id):
    return next((s for s in TANK_STANCES.values() if s["id"] == stance_id), None)


def in_tank_posture(actor):
    """Is this character tanking: a tank stance, a tank form, Defensive Stance, or Earthen Guardian?"""
    return bool(
        getattr(actor, "tank_stance", None)
        or getattr(actor, "current_form", None) in TANK_FORMS
        or getattr(actor, "current_stance", None) == TANK_WARRIOR_STANCE
        or getattr(actor, "guardian_stance_active", False))


def posture_threat_pct(actor):
    """Percent points of extra threat from this character's tank posture (0 or TANK_THREAT_PCT). Earthen Guardian is
    not counted: it carries its own x3 as threat_multiplier, read separately."""
    if (getattr(actor, "tank_stance", None)
            or getattr(actor, "current_form", None) in TANK_FORMS
            or getattr(actor, "current_stance", None) == TANK_WARRIOR_STANCE):
        return TANK_THREAT_PCT
    return 0.0


def posture_name(actor):
    """What the tank posture is called, for the UI, or None."""
    sid = getattr(actor, "tank_stance", None)
    if sid:
        s = stance_by_id(sid)
        return s["name"] if s else sid
    form = getattr(actor, "current_form", None)
    if form in TANK_FORMS:
        from combat.forms import get_form
        return (get_form(form) or {}).get("name", form)
    if getattr(actor, "current_stance", None) == TANK_WARRIOR_STANCE:
        return "Defensive Stance"
    if getattr(actor, "guardian_stance_active", False):
        return "Earthen Guardian"
    return None
