"""Front and back rows: who can reach whom.

Kyle, 6 Nov: "melee mobs will be stuck hitting front line, tank can still
taunt ranged, but they can go and attack back row if theyre not taunted...
we will only put ranged / casters in the back. so this way it feels more
like we have to go through the front line to get to the back."

THE RULE, in full:

  - Melee can only reach the enemy FRONT row. Once every front-row enemy is
    dead, the back row becomes the front row and melee reaches it.
  - Ranged and casters reach either row, always.
  - A taunt overrides reach: a taunted combatant attacks its taunter even
    across rows. This is deliberate - it is what lets a tank peel an enemy
    caster off the party's back line, and it is why a tank wants a ranged
    tool (Shoot, Faerie Fire) to put threat on something it cannot walk to.
  - The rule is SYMMETRIC. Enemy melee is stuck on the party's front row on
    exactly the same terms.

ROWS DO NOT CHANGE DAMAGE. Kyle: "no, enemies dont get damage modifiers or
take more/less damage. they are just how you reach them (not to dissimilar
to wow)." A row is a position, not a multiplier.

REACH IS A PROPERTY OF THE ABILITY, NOT THE ACTOR, and this is the part
that cannot be inferred from anything already in the data. Measured across
the 18 creature templates:

    humanoid_ranged  (marksman)   schools {physical: 3}
    vermin_sneaky    (scorpid)    schools {physical: 1, nature: 1}

A marksman is entirely physical and belongs at the back; a scorpion has a
nature poison and belongs at the front. School says nothing about reach, so
`reach_of` reads an explicit field first and falls back to effect_type,
which is right for player abilities and leaves creature kits melee unless
their template says otherwise.
"""

from entities.party import FRONT_ROW, BACK_ROW

MELEE = "melee"
RANGED = "ranged"

#: effect_type values that reach the back row on their own. Everything else
#: is melee unless the ability says `"reach": "ranged"`.
_RANGED_EFFECTS = frozenset({
    "ranged_damage", "spell_damage", "spell_dot", "heal", "hot",
    "buff", "debuff", "dispel", "restore_resource", "damage_and_heal",
    "damage_and_restore_mana", "revive", "summon_pet",
})


def row_of(combatant):
    """A combatant's row, defaulting to front.

    Characters carry `row` already (entities/party.py sets it from
    DEFAULT_ROW_BY_CLASS). Monsters get theirs from their template.
    """
    # forced_front (Giorgi Beridze, "Bringing the Herd Down"): driven out of the back row for
    # as long as the effect lasts, where melee can reach. The combatant's own row is untouched,
    # so it goes back by itself when the effect ends.
    mod = getattr(combatant, "get_status_stat_mod", None)
    if mod is not None and mod("forced_front") > 0:
        return FRONT_ROW
    return getattr(combatant, "row", None) or FRONT_ROW


def reach_of(ability):
    """MELEE or RANGED for one ability.

    An explicit `reach` wins. Otherwise effect_type decides: a spell, a
    shot or anything that is not a swing reaches the back row.
    """
    explicit = getattr(ability, "reach", None)
    if explicit in (MELEE, RANGED):
        return explicit
    if getattr(ability, "effect_type", None) in _RANGED_EFFECTS:
        return RANGED
    return MELEE


def front_rank(candidates):
    """The row that currently counts as the front among `candidates`.

    Once every front-row combatant is dead the back row IS the front row,
    which is what lets melee cleave into it. Returns None when nothing is
    left alive.
    """
    alive = [c for c in candidates if c.is_alive()]
    if not alive:
        return None
    if any(row_of(c) == FRONT_ROW for c in alive):
        return FRONT_ROW
    return BACK_ROW


def reachable(attacker, ability, candidates, taunted_by=None):
    """The subset of `candidates` this attacker may target with this ability.

    `taunted_by` is the combatant forcing the attacker's target, if any - a
    taunt ignores rows entirely, by design.
    """
    alive = [c for c in candidates if c.is_alive()]
    if not alive:
        return []
    if taunted_by is not None and taunted_by in alive:
        return [taunted_by]
    if reach_of(ability) == RANGED:
        return alive
    front = front_rank(alive)
    return [c for c in alive if row_of(c) == front]


def targetable_rows(attacker, ability, candidates):
    """Which rows an area ability may be aimed at - the player picks one.

    Kyle: "a warrior cleave only hits the front row when other front liners
    are up, but a mage can pick an aoe on front or back row. Then when front
    row is destroyed then the melee can cleave the back row."
    """
    alive = [c for c in candidates if c.is_alive()]
    if not alive:
        return []
    occupied = [r for r in (FRONT_ROW, BACK_ROW)
                if any(row_of(c) == r for c in alive)]
    if reach_of(ability) == RANGED:
        return occupied
    front = front_rank(alive)
    return [front] if front in occupied else []


def in_row(candidates, row):
    """Living members of `candidates` standing in `row`."""
    return [c for c in candidates if c.is_alive() and row_of(c) == row]
