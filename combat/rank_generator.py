"""
Rank level generator for ability ranks.

Design (per Kyle's direction):
- Abilities rank up like classic WoW (Rank 1/2/3/...), NOT auto-scaling with
  character level and NOT independent skill points.
- Skills are only learned/ranked up every 2 levels, just like a WoW trainer
  visit - so every level_req must be even (level 1 is the sole exception,
  since starting abilities are known at character creation, not learned from
  a trainer).
- Spacing is FRONT-LOADED: gaps between ranks start small and grow larger,
  matching how vanilla WoW itself paced spell ranks (frequent early upgrades,
  rarer/bigger jumps later).
- Starting kit abilities should reach max rank around level ~48-54, not much
  earlier - the level 60 cap means capping out at ~38 leaves a long dead
  stretch with zero power growth. Landing near the top of the range keeps
  the ability feeling alive most of the way to endgame.
- Abilities learned later in the leveling curve get fewer ranks, since
  there's less room left before level 60. This falls naturally out of the
  same spacing table, just truncated by the level cap.
"""

MAX_LEVEL = 60

# Gap sequences by table size. Each list is the number of levels between
# consecutive ranks, in order, already front-loaded (small gaps first, big
# gaps last). Chosen so a 5-rank starting ability lands its final rank
# around level ~50, and a 4-rank starting ability lands around ~46.
#
#   9 ranks: 1 -> 6 -> 12 -> 18 -> 24 -> 32 -> 40 -> 48 -> 56
#            (gaps: 5, 6, 6, 6, 8, 8, 8, 8) - Kyle's balance pass
#            (2026-09-05): OG9 spam-cost skills (Fireball, Lightning
#            Bolt, Sinister Strike, etc.) now use 8-9 ranks like the
#            CoA classes' progression convention, instead of capping at
#            5. Tighter early gaps than the 5-rank table below since
#            twice as many rungs need to fit in the same ~1-55 span.
#   8 ranks: 1 -> 6 -> 12 -> 20 -> 28 -> 36 -> 44 -> 54
#            (gaps: 5, 6, 8, 8, 8, 8, 10)
#   5 ranks: 1 -> 10 -> 22 -> 36 -> 50   (gaps: 9, 12, 14, 14)
#   4 ranks: 1 -> 12 -> 28 -> 46         (gaps: 11, 16, 18)
#   3 ranks: 1 -> 16 -> 36               (gaps: 15, 20)
#   2 ranks: 1 -> 14                     (gap: 13) - e.g. Tranquility-style,
#            learned ~40 lands its 2nd rank ~52-54, still well before cap
#   1 rank:  1                           (no gaps)
_GAP_SEQUENCES = {
    9: [5, 6, 6, 6, 8, 8, 8, 8],
    8: [5, 6, 8, 8, 8, 8, 10],
    5: [9, 12, 14, 14],
    4: [11, 16, 18],
    3: [15, 20],
    2: [13],
    1: [],
}


def _snap_even(level):
    """Round a level to the nearest even number (trainer visits are every 2
    levels). Level 1 is left alone since that's character creation, not a
    trainer visit."""
    if level <= 1:
        return 1
    if level % 2 != 0:
        level += 1
    return level


def generate_rank_levels(level_learned, num_ranks):
    """
    Generate the level requirement for each rank of an ability.

    level_learned: the level at which the ability is first known (1 for
        starting-kit abilities, an even number for trainer-learned ones).
    num_ranks: how many ranks this ability *would* have if there were
        unlimited room before the level cap. The actual number returned
        may be fewer, since ranks that would land past MAX_LEVEL are
        dropped (this is how "learned late = fewer ranks" falls out
        automatically).

    Returns: list of ints, one level requirement per rank, ascending,
        always starting with level_learned itself as rank 1.
    """
    if num_ranks < 1:
        raise ValueError("num_ranks must be >= 1")
    if num_ranks > 9:
        raise ValueError("num_ranks > 9 not supported by the gap table")

    level_learned = 1 if level_learned <= 1 else _snap_even(level_learned)
    gaps = _GAP_SEQUENCES[num_ranks]

    levels = [level_learned]
    current = level_learned
    for gap in gaps:
        current = _snap_even(current + gap)
        if current > MAX_LEVEL:
            break
        levels.append(current)

    return levels


def generate_ranks(level_learned, base_ranks_wanted, rank_value_fn):
    """
    Convenience wrapper: generates the level list AND calls rank_value_fn(i)
    for each rank index (0-based) to build a list of rank dicts.

    rank_value_fn(rank_index) -> dict of rank-specific fields (cost, damage,
        etc.) NOT including level_req/rank number, which this function fills
        in automatically.

    Returns: list of dicts, each with "rank" (1-based) and "level_req" keys
        merged in front of whatever rank_value_fn returned.
    """
    levels = generate_rank_levels(level_learned, base_ranks_wanted)
    ranks = []
    for i, lvl in enumerate(levels):
        rank_num = i + 1
        values = rank_value_fn(i)
        rank_dict = {"rank": rank_num, "level_req": lvl}
        rank_dict.update(values)
        ranks.append(rank_dict)
    return ranks
