#!/usr/bin/env python3
"""Spread a talent node over several ranks without changing its ceiling.

    from tools.talent_ranks import spread

WHY THIS EXISTS. Rebuilding a spec from the CoA reference replaces multi-rank
scalars ("+2% armour per rank, 5 ranks") with single-rank mechanics (a proc, a
conditional, a stat conversion). That is the point - Kyle, 5 Nov 2026, on the
old trees: the flat scalars are the problem. But it also shrinks the tree's
POINT CAPACITY, because a proc is one point where the scalar it replaced was
five, and the first seven rebuilt trees came out holding 31-39 points against
a project median of 71.

That is not cosmetic. A character earns 1 talent point per level from level 5,
so 56 by level 60, and a pure-spec player or a spec-locked recruit must be
able to spend all of them in ONE tree. A 31-point tree strands 25 points.
It surfaced as "Imelda Salonga at level 47 joins with 9 unspent talent
point(s)" in qa_recruit_talents, two steps from the cause.

Kyle's call, asked directly rather than guessed: multi-rank the real
mechanics rather than padding the trees back out with flat scalars.

WHAT THIS DOES, and the two conventions it exists to get right:

  1. EFFECTS ARE AUTHORED PER RANK. TalentNode.get_effective_effects()
     multiplies numeric effects by points spent, so a node written as
     {"ability_x_damage": 0.30} at 1 rank must become 0.10 at 3 ranks to
     land on the same 30%. Dividing is the whole job.

  2. PROC CHANCE IS ALSO PER RANK. Character._sync_talent_procs does
     chance = min(100, proc["chance"] * points_spent) - so a proc authored
     at 100 does NOT become 33% at rank 1 of 3, it stays 100%, granting the
     full value for one point. A 3-rank proc that should be reliable at full
     investment is authored at 34, giving 34/68/100.

Getting either backwards is silent: the tree looks ranked and either pays
out triple or pays out in full for one point.

WHAT IT REFUSES TO TOUCH:
  - unlock_ability nodes. You cannot learn an ability one third of the way,
    and these are the nodes qa_abilities_obtainable exists to protect.
  - small integer effects (a duration or a flat turn count). 1 turn over 3
    ranks is 0.33 turns per rank, which reads as 0 until the third point.
    Those stay at 1 rank, or take 2 at most, chosen by the caller.
  - apply_effect payload magnitudes. Those are NOT rank-scaled by the
    engine - only chance is - so a stacking buff's stat_mods are the same
    at every rank by design, and dividing them would quietly weaken the
    node at full investment.
"""


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

#: Imported from the engine rather than re-listed here, so this module and
#: TalentNode.get_effective_effects() can never disagree about which keys
#: are thresholds (passed through raw) rather than quantities (multiplied
#: by points spent). See the note in spread().
from entities.talent_node import UNSCALED_EFFECT_KEYS  # noqa: E402


def _tidy(value):
    """Keep the per-rank number readable rather than 0.09999999999999999."""
    if isinstance(value, float):
        rounded = round(value, 4)
        return int(rounded) if rounded == int(rounded) else rounded
    return value


def rankable(entry):
    """False for nodes that must stay at the rank count they were written with.

    Two kinds:

      - unlock nodes, since an ability cannot be learned a third of the way;
      - nodes carrying a small integer effect - a duration or a flat turn
        count. Those cannot be divided across ranks (0.33 turns per rank
        reads as nothing until the third point), so re-ranking them leaves
        the per-rank value untouched and MULTIPLIES the ceiling: Macro
        Designer's "+1 turn to Med Pack" became +3 turns, and Everlasting
        Rage's +2 became +3. Caught by comparing full-investment totals
        against the previous version rather than by reading the output.
    """
    if "unlock_ability" in (entry.get("effects") or {}):
        return False
    for value in (entry.get("effects") or {}).values():
        if isinstance(value, bool):
            continue
        if isinstance(value, int) and abs(value) <= 3:
            return False
    return True


def spread(entry, ranks):
    """Give `entry` `ranks` ranks, preserving its full-investment ceiling.

    Mutates and returns the entry. A `ranks` of 1 or less is a no-op, so a
    caller can pass a rank table that simply omits most nodes.
    """
    if ranks is None or ranks <= 1:
        return entry
    if not rankable(entry):
        raise ValueError(
            f"{entry.get('talent_id')} grants an ability and cannot be ranked")

    # SCALE FROM THE CURRENT RANK COUNT, not from 1. A node already written
    # with 2 ranks carries a value that is per-rank FOR TWO, so going to 3
    # multiplies by 2/3 - dividing by 3 outright would quietly halve the
    # ceiling of every node CoA itself ranked, or that an earlier pass split
    # to make a tier reachable. Factor is current/new, which is 1/3 for the
    # common 1 -> 3 case and reduces to the simple division there.
    current = max(1, int(entry.get("max_points") or 1))
    if current == ranks:
        return entry
    factor = current / ranks

    entry["max_points"] = ranks

    effects = entry.get("effects") or {}
    for key, value in list(effects.items()):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        # A flat integer of 1-3 is a turn count or a resource amount, and
        # dividing it gives a per-rank value that floors to nothing. Left
        # alone: the node gets more ranks and that effect simply accumulates
        # beyond its original value, which for a duration is a real and
        # intended rank curve ("+1 turn per rank").
        if isinstance(value, int) and abs(value) <= 3:
            continue
        # UNSCALED_EFFECT_KEYS are NOT multiplied back by points spent
        # (talent_node.py:149 passes them through at their raw value), so
        # dividing one here is a silent nerf of exactly 1/ranks that
        # nothing restores. Reaper Harvest's Executioner shipped a 35%
        # execute window as 11.67% that way, which made the whole tree's
        # conditional damage dead against any target above 11% health - it
        # looked correct in the data and only showed up when a live
        # character read the threshold back. These keys are THRESHOLDS, not
        # quantities: a rank curve on one is meaningless anyway.
        #
        # Imported rather than re-listed so the two cannot drift apart.
        if key in UNSCALED_EFFECT_KEYS:
            continue
        effects[key] = _tidy(value * factor)

    proc = entry.get("proc")
    if proc and "chance" in proc:
        # Ceil-ish, so full ranks reach at least the authored chance rather
        # than landing at 99 from integer truncation.
        # NEAREST, not ceiling. A chance is uniform per rank, so a total
        # that does not divide evenly cannot be preserved exactly - 10%
        # over 3 ranks is 3/rank (9 at full ranks) or 4/rank (12). Ceiling
        # pushed every such proc UP, which on a 10% proc is a 20% buff;
        # nearest keeps the drift under one rank's worth either way.
        total = proc["chance"] * current
        proc["chance"] = max(1, min(100, int(round(total / ranks))))
    return entry
