"""
Persistent shapeshift forms - Druid Bear/Cat/Dire Bear/Moonkin/Tree of
Life, Priest Shadowform. Distinct from temporary combat-cooldown "forms"
like Warlock Metamorphosis, which are just a buff with a duration (see
combat/abilities.py's existing is_instant/buff mechanism - Metamorphosis
doesn't need anything from this module).

THE KEY MECHANIC THIS MODULE ADDS: forms change which resource pool a
character draws from. Real WOTLK - confirmed via Warcraft Tavern/Wowhead
Druid guides - Bear/Dire Bear use Rage, Cat uses Energy, every other form
(including base Humanoid) uses Mana. "Shifting resets your current
resource unless talented otherwise" is also real and implemented here:
switching forms clears whatever pool you're leaving, matching that.

Per Kyle: these are meant to be PERSISTENT - toggled on and staying on
across multiple fights, not re-entered every combat like Warrior stances
effectively reset to Battle by nothing enforcing otherwise. current_form
lives on Character exactly like current_stance, but nothing auto-resets it
between fights.
"""
from combat.abilities import ResourceType

#: ARMOUR MULTIPLIERS ON THE TANK FORMS, and why they are percentages rather than bigger flat
#: numbers. Kyle, 2026-10-28: "bear form should increase armor from leather, and venomancer
#: increases from mail to balance no shield."
#:
#: A bear and a beetle tank without a shield, and their armour class is below plate - leather gear
#: carries 838 armour at level 60 and mail 1342, against plate's 2040. With only the flat +90/+150
#: these forms used to give, a dire bear sat at 37% physical reduction while the plate tanks sat at
#: 52-55%, so the druid was the worst tank in the game at the one thing a bear is for. Classic
#: solved this the same way - Bear Form multiplied the armour contribution of items rather than
#: adding to it - which is why these are armor_pct and not a larger flat bonus: a flat number that
#: works at 60 is enormous at 15 and irrelevant at 60 once gear moves on.
#:
#: REFITTED 12 Nov 2026, on the player armour curve (Character.PLAYER_MITIGATION_PER_LEVEL).
#: Kyle: "most tanks get DR from abilities and avoidance (block, dodge, parry). The only things
#: that should have high armor (even reaching cap) would be druid bears, venomancer beetles, and
#: bloodmage eternal form (as none of these forms can block OR parry) so they need high armor."
#:
#: So these no longer aim to MATCH a plate tank's armour - they aim well past it, because armour
#: is the only layer they have. Measured on recruits at 56-60 in the gear the game gives them:
#:
#:     plate + shield tank        52%   and blocks, parries and dodges on top
#:     beetle (mail)              66%
#:     eternal curse (Bloodmage)  65%   armor_pct lives on the ability, data/abilities/bloodmage.json
#:     dire bear (leather)        68%   before any Feral armour talents; the cap is 75%
#:
#: Dire Bear's multiplier is the largest because leather starts lowest; Beetle's the smallest
#: because mail starts closest and Fortitude's own talents already add to it.
FORMS = {
    "bear": {
        "name": "Bear Form",
        "class": "Druid",
        "level_req": 10,
        "resource_type": ResourceType.RAGE,
        "description": (
            "Shifts into a bear, trading your normal Mana pool for Rage. "
            "Increases Armor and Stamina."
        ),
        "stat_mods": {"armor": 90, "stamina": 25, "armor_pct": 250},
    },
    "dire_bear": {
        "name": "Dire Bear Form",
        "class": "Druid",
        "level_req": 40,
        "resource_type": ResourceType.RAGE,
        "description": (
            "An improved Bear Form - more Armor, Stamina, and Attack "
            "Power than the base form."
        ),
        "stat_mods": {"armor": 150, "stamina": 40, "attack_power": 60, "armor_pct": 400},
    },
    "cat": {
        "name": "Cat Form",
        "class": "Druid",
        "level_req": 20,
        "resource_type": ResourceType.ENERGY,
        "description": (
            "Shifts into a cat, trading your normal Mana pool for Energy. "
            "Increases Agility and critical strike chance."
        ),
        "stat_mods": {"agility": 20, "crit_chance_physical": 5.0},
    },
    "moonkin": {
        "name": "Moonkin Form",
        "class": "Druid",
        "level_req": 40,  # talent-gated in real WOTLK; matches the Balance tree's Moonkin Form talent already in this engine
        "resource_type": ResourceType.MANA,
        "description": "Increases Armor and spell critical strike chance.",
        "stat_mods": {"armor": 74, "crit_chance_spell": 5.0},
    },
    "tree_of_life": {
        "name": "Tree of Life",
        "class": "Druid",
        "level_req": 50,  # talent-gated capstone in real WOTLK
        "resource_type": ResourceType.MANA,
        "description": "Increases healing done and reduces HoT Mana costs.",
        "stat_mods": {"healing_done": 0.06},
    },
    "shadowform": {
        "name": "Shadowform",
        "class": "Priest",
        "level_req": 40,  # talent-gated in real WOTLK
        "resource_type": ResourceType.MANA,
        "description": "Increases Spell Power against Shadow damage.",
        "stat_mods": {"spell_power": 30},
    },
    # Cultist's Dreadnought capstone, Strength of the Black Empire: "Shed
    # your mortal form into a void monstrosity, reducing damage taken." It
    # was authored as unlock_mechanic: "void_monstrosity_form", a key no
    # engine code read, so the class's only transform did nothing - and
    # Cultist was the one form-flavoured class with no entry here at all,
    # which is why require_form was dead for it.
    #
    # A tank transform, so it keeps Mana (Insanity remains the secondary
    # resource) and trades damage for durability. damage_taken_pct is a
    # FRACTION in a stat_mods dict read through the status path, matching
    # every other ability that uses it.
    "void_monstrosity": {
        "name": "Void Monstrosity",
        "class": "Cultist",
        "level_req": 40,  # talent-gated capstone
        "resource_type": ResourceType.MANA,
        "description": (
            "Sheds your mortal shape for something from the deep. Greatly "
            "increases Armor and Stamina and reduces damage taken."
        ),
        "stat_mods": {"armor": 160, "stamina": 35, "damage_taken_pct": -0.10},
    },
    # Venomancer - Druid-equivalent form system per Kyle ("basically a
    # Druid... Spider is energy, beetle is rage, Rot and Vizier are caster
    # dps and healer... think of it like Cat / Bear / Moonkin / Tree of
    # Life"). Same persistent-shapeshift-swaps-your-resource-pool mechanic,
    # just re-skinned: Stalking spec -> Spider (Cat-equivalent, Energy),
    # Fortitude spec -> Beetle (Bear-equivalent, Rage), Venom/Rot spec ->
    # Weaver (Moonkin-equivalent, Mana caster), Vizier spec -> Vizier Form
    # (Tree of Life-equivalent, Mana healer). CoA screenshot confirmed both
    # Weaver Form and Vizier Form as real "Ability | Shapeshift"-tagged
    # entries; Spider/Beetle aren't explicitly named as forms in the CoA
    # data but are Kyle's direct design instruction, so treated with the
    # same authority as a confirmed screenshot.
    "spider": {
        "name": "Spider Form",
        "class": "Venomancer",
        "level_req": 6,
        "resource_type": ResourceType.ENERGY,
        "description": (
            "Shifts into a spider, trading your normal Mana pool for "
            "Energy. Increases Agility and critical strike chance."
        ),
        "stat_mods": {"agility": 20, "crit_chance_physical": 5.0},
    },
    "beetle": {
        "name": "Beetle Form",
        "class": "Venomancer",
        "level_req": 10,
        "resource_type": ResourceType.RAGE,
        "description": (
            "Shifts into an armored beetle, trading your normal Mana pool "
            "for Rage. Increases Armor and Stamina."
        ),
        "stat_mods": {"armor": 90, "stamina": 25, "armor_pct": 140},
    },
    "weaver": {
        "name": "Weaver Form",
        "class": "Venomancer",
        "level_req": 30,
        "resource_type": ResourceType.MANA,
        "description": (
            "Reduces spell pushback suffered from damaging attacks by "
            "70%, and periodic damage has a chance to restore mana."
        ),
        "stat_mods": {"crit_chance_spell": 5.0},
        "_source": "CoA tooltip: 'reducing spell pushback suffered from damaging attacks by 70%, and giving periodic damage dealt a 15% chance to restore 5% of your base mana. Allows periodic effects to benefit from spell haste and makes you immune to polymorph effects.' Pushback/haste-on-DoTs/polymorph-immunity have no equivalent mechanic in this engine yet (no cast-pushback, no polymorph CC type) - approximated as a spell crit bonus, matching Moonkin Form's role as this class's caster-form stat boost.",
    },
    "vizier_form": {
        "name": "Vizier Form",
        "class": "Venomancer",
        "level_req": 40,
        "resource_type": ResourceType.MANA,
        "description": "Increases healing done and reduces healing ability Mana costs.",
        "stat_mods": {"healing_done": 0.06},
    },
}


def get_form(form_id):
    return FORMS.get(form_id)


def available_forms(char_class, level):
    """Every form this class/level already qualifies for, in a stable
    order - used by the form-selection UI."""
    return [fid for fid, f in FORMS.items() if f["class"] == char_class and level >= f["level_req"]]


def resource_for_form(form_id):
    """The ResourceType a character in this form should draw from, or
    None if form_id doesn't exist (caller should fall back to the
    class's normal resource in that case)."""
    form = FORMS.get(form_id)
    return form["resource_type"] if form else None
