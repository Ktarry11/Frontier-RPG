"""THE PHYSICAL DAMAGE PIPELINE: how a weapon strike's damage is built, in one place.

Kyle, 27 Nov 2026 (the combat backlog): "Almost all physical abilities appear to scale primarily from Attack
Power while ignoring weapon damage and weapon statistics", "a naked Shaman's Lightning Bolt can scale better than
when equipped with a purple two-handed axe", "Review the underlying damage calculation system rather than
individually adjusting every affected ability."

MEASURED FIRST (level 60): a special was effect_value + AP x coefficient + ONE flat weapon roll. The rank curve
makes effect_value large (Stormstrike 2,243, Heroic Strike 1,110), so a rare one-hander added ~360 and an epic
two-hander ~630 to a 2,000-3,000 hit: going from naked to epic was worth ~25%. Ranged specials that are shots
(Steady Shot, Aimed Shot, Multi-Shot) rolled the MELEE weapon and melee attack power, so the bow did nothing for
them, and a naked hand rolled 0.

THE PIPELINE (Kyle's order):
  1. weapon damage    - the hand(s) the ability uses, rolled (fists when unarmed)
  2. attack power     - melee or ranged, times the ability's coefficient (combat/ability_scaling.py)
  3. hands            - main hand only, both weapons (strikes_both_weapons), or the ranged slot (reach "ranged",
                        ranged_damage). A main-hand special's off hand still takes its own white swing beside it
                        (combat/abilities.py).
  4. coefficients     - the ability's rank value is split into a fixed part and a WEAPON part:
                            strike = (rank value + E) x ((1 - W) + W x roll / E)
                        E is what a level-appropriate rare one-hander (ranged: a rare bow) rolls on average at
                        the caster's level, W the ability's weapon share. At E the strike is exactly what it was
                        before (rank value + one average weapon roll), so the balance passes still hold; the
                        weapon now moves W of the whole hit instead of a small flat add. Naked is ~58% of that,
                        an epic two-hander ~145%.
  5. talents/buffs    - Ability._damage_multiplier, unchanged
  6. hit and crit     - unchanged
  7. procs            - weapon procs fire off the strike (combat/abilities.py: proc eligibility)

WEAPON SHARE (W), unless the ability's data names one ("weapon_share"):
  single-target strikes and shots 0.6, area strikes 0.45, finishers that spend all their points 0.3, a strike in a
  magic school (Searing Blade, Purifier's Edge) 0.4. The basic Attack is pure weapon (W 1, no rank value).
"""

from combat.world_curve import world_scale

RARE_BUDGET = 1.7          # data/items/rarity.json, rare stat_budget_multiplier: the reference weapon
TIER_ONE_HAND = 1.0
TIER_RANGED = 0.85
UNARMED_BUDGET = 0.5       # fists roll like a poor weapon (Classic's unarmed is roughly a grey dagger)
OFFHAND_PENALTY = 0.5

SHARE_SINGLE = 0.6
SHARE_AOE = 0.45
SHARE_FINISHER = 0.3
SHARE_MAGIC_SCHOOL = 0.4


def _raw_avg(item_level, budget, tier):
    """The generator's average hit (entities/loot_generator.generate_weapon), before the world curve."""
    return (max(1, item_level) * 1.1 + 6.4) * budget * tier


def expected_roll(level, ranged=False):
    """E: what a level-appropriate rare weapon rolls on average at this level, after the world curve."""
    lv = max(1, int(level or 1))
    return _raw_avg(lv, RARE_BUDGET, TIER_RANGED if ranged else TIER_ONE_HAND) * world_scale(lv)


def unarmed_range(level):
    """Fists: (min, max) before the world curve."""
    avg = _raw_avg(max(1, int(level or 1)), UNARMED_BUDGET, TIER_ONE_HAND)
    return max(1, int(avg * 0.85)), max(2, int(avg * 1.15))


def _rng(item):
    return (getattr(item, "weapon_damage_min", 0) or 0, getattr(item, "weapon_damage_max", 0) or 0)


def average_roll(caster, mode):
    """The caster's AVERAGE weapon roll for `mode` ("main", "both", "ranged"), after the world curve - what a
    tooltip shows. Mirrors Character.get_weapon_damage_roll without touching the dice."""
    eq = getattr(caster, "equipment", None)
    if eq is None:
        return 0.0
    ws = world_scale(getattr(caster, "level", 1))
    if mode == "ranged":
        w = eq.get_ranged_weapon()
        lo, hi = _rng(w) if w else (0, 0)
        return (lo + hi) / 2.0 * ws if hi > 0 else 0.0
    mh = eq.get_main_hand_weapon()
    lo, hi = _rng(mh) if mh else (0, 0)
    if hi <= 0:
        lo, hi = unarmed_range(getattr(caster, "level", 1))
    total = (lo + hi) / 2.0
    if mode == "both":
        oh = caster._offhand_weapon() if hasattr(caster, "_offhand_weapon") else None
        if oh is not None:
            olo, ohi = _rng(oh)
            bonus = caster._offhand_bonus() if hasattr(caster, "_offhand_bonus") else 1.0
            total += (olo + ohi) / 2.0 * OFFHAND_PENALTY * bonus
    return total * ws


def mode_for(ability, caster):
    """Which hand(s) this physical ability uses: "ranged", "both" or "main"."""
    if ability.effect_type == "ranged_damage" or getattr(ability, "reach", None) == "ranged" \
            or getattr(ability, "requires_ranged_weapon", None):
        return "ranged"
    if ability.is_basic_attack(caster) or getattr(ability, "strikes_both_weapons", False):
        return "both"
    return "main"


def uses_ranged_weapon(ability, caster):
    """A shot rolls the ranged slot - but only if one is equipped; a hunter with no bow still throws a punch's
    worth via the melee roll rather than nothing (Shoot itself is gated on the weapon elsewhere)."""
    if mode_for(ability, caster) != "ranged":
        return False
    eq = getattr(caster, "equipment", None)
    w = eq.get_ranged_weapon() if eq is not None else None
    return bool(w and (getattr(w, "weapon_damage_max", 0) or 0) > 0)


def weapon_share(ability):
    explicit = getattr(ability, "weapon_share", None)
    if isinstance(explicit, (int, float)):
        return max(0.0, min(1.0, float(explicit)))
    if getattr(ability, "spends_all", False) or getattr(ability, "secondary_cost", None):
        return SHARE_FINISHER      # Eviscerate, Envenom...: a finisher spends points, not the blade
    school = getattr(ability, "damage_school", None)
    if school not in (None, "physical") and not isinstance(school, (list, tuple)) and str(school) != "physical":
        return SHARE_MAGIC_SCHOOL
    if isinstance(school, (list, tuple)) and any(str(s) != "physical" for s in school):
        return SHARE_MAGIC_SCHOOL
    if ability.target_type in ("enemy_aoe", "all_enemies") or getattr(ability, "is_aoe", False):
        return SHARE_AOE
    return SHARE_SINGLE


def strike(ability, caster, roll, ranged=False):
    """Steps 1, 2 and 4: the strike before talents, buffs, armour and crit, from a weapon roll.

    The basic Attack is the weapon itself plus attack power. Every other physical ability splits its rank value
    into a fixed part and a weapon part (see the module note)."""
    from combat.abilities import _scaling_coef
    ap = (getattr(caster, "ranged_attack_power", 0) if ranged else getattr(caster, "attack_power", 0)) or 0
    ap_part = ap * _scaling_coef(ability, "ap", caster)
    if ability.is_basic_attack(caster) or not ability.effect_value:
        return ability.effect_value + ap_part + roll
    E = expected_roll(getattr(caster, "level", 1), ranged=ranged)
    if E <= 0:
        return ability.effect_value + ap_part + roll
    W = weapon_share(ability)
    return ap_part + (ability.effect_value + E) * ((1.0 - W) + W * (roll / E))


def is_melee_weapon_strike(ability, caster):
    """Step 7's eligibility: weapon procs (Windfury, Flametongue, Rockbiter, crusader-style enchants) fire off any
    melee strike that uses the weapon - the basic Attack and every physical special - and never off a spell, a
    DoT tick, a heal or a shot."""
    if ability.effect_type != "damage":
        return False
    if ability.is_basic_attack(caster):
        return True
    if mode_for(ability, caster) == "ranged":
        return False
    return weapon_share(ability) > 0
