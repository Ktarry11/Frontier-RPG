"""
WoW-style con colours: grey / green / yellow / orange / red.

Kyle, 4 Nov 2026: "We also need the quest and mob kill system (wow style)
where you have grey, green, yellow, orange, and red based on level difference
and how much exp you get. Like a grey mob gets you 0 exp and a grey quest is
almost fuck all for exp... Also this should be based on the average party level
to simplify stuff."

THIS MODULE IS THE ONLY PLACE THE FORMULA LIVES. Combat XP, quest XP and every
piece of UI that draws a colour all call in here. The engine previously carried
its own level-difference scaling in two places - combat/combat_engine.py's
_calculate_exp_reward and world/quest.py's get_scaled_exp_reward - which were
written to mirror each other by hand and said so in their own docstrings. Both
now defer to this module. A difficulty rule that exists twice is a difficulty
rule that will disagree with itself, and this project has lost a lot of hours
to exactly that shape.

EVERYTHING IS MEASURED AGAINST THE PARTY AVERAGE, not the player's own level,
per Kyle's instruction above. party_average_level() is the single accessor; do
not reach for player.level when colouring or awarding.

=== The real Classic formulas, and why they are what they are ===

**Grey level.** The level at or below which a kill is worth nothing. Not a flat
offset - the gap widens as you climb, which is why a level 10 character still
earns from level 5 mobs but a level 50 does not earn from level 39:

    <= 5    nothing is ever grey
    <= 39   level - 5 - floor(level / 10)
    <= 59   level - 1 - floor(level / 5)
    60+     level - 9

Continuous across the 39/40 seam by design: both give 31.

**Zero difference (ZD).** How many levels below you a mob has to be before its
XP reaches zero, used to interpolate the fade from green down to grey. Table
rather than formula because that is what Classic actually uses.

**The XP curve itself.**
    mob at or above you:  1 + 0.05 * (mob - party), capped at +4 levels
    mob below you:        1 - (party - mob) / ZD
    mob at or below grey: 0

The cap matters: without it a red mob five levels up would pay more than the
risk justifies, and the +5-and-above band is already where players die.
"""
import math

#: Band ids, lowest difficulty first. The ORDER is meaningful - UI that sorts or
#: compares difficulty should use index(), not string comparison.
BANDS = ("grey", "green", "yellow", "orange", "red")

#: Display colours, chosen to match WoW's own con colours closely enough that
#: anyone who has played it reads them without a legend. Kept here rather than
#: in a UI file so the quest journal, the enemy nameplate and anything added
#: later cannot drift apart.
BAND_COLORS = {
    "grey":   (150, 150, 150),
    "green":  (100, 200, 100),
    "yellow": (255, 221, 68),
    "orange": (255, 150, 50),
    "red":    (255, 80, 80),
}

#: Human-readable, for tooltips and the quest journal.
BAND_LABELS = {
    "grey":   "Trivial",
    "green":  "Easy",
    "yellow": "Normal",
    "orange": "Hard",
    "red":    "Very Hard",
}

#: Zero-difference table - see module docstring. (max_level, zd).
_ZERO_DIFFERENCE = (
    (7, 5), (9, 6), (11, 7), (15, 8), (19, 9), (29, 11),
    (39, 12), (44, 13), (49, 14), (54, 15), (59, 16),
)
_ZERO_DIFFERENCE_CAP = 17

#: A grey quest is NOT worth zero, unlike a grey kill. Kyle: "a grey quest is
#: almost fuck all for exp" - almost, not nothing. Turning in a quest you
#: outlevelled should still clear it off the log with a token payout rather
#: than feeling like the game took it off you.
GREY_QUEST_MULTIPLIER = 0.10

#: Bonus for fighting above the party's level caps here. Four levels up is
#: already deep in orange; beyond that the danger rises much faster than any
#: XP bonus could fairly pay for, and uncapping it would make suicide pulls
#: the optimal strategy.
MAX_LEVEL_BONUS_DIFF = 4


def grey_level(level):
    """Highest level that is worth NO experience to a character of `level`."""
    level = int(level)
    if level <= 5:
        return 0
    if level <= 39:
        return level - 5 - math.floor(level / 10)
    if level <= 59:
        return level - 1 - math.floor(level / 5)
    return level - 9


def zero_difference(level):
    """Levels below `level` at which XP reaches zero - the fade's denominator."""
    level = int(level)
    for max_level, zd in _ZERO_DIFFERENCE:
        if level <= max_level:
            return zd
    return _ZERO_DIFFERENCE_CAP


def party_average_level(party, fallback=1):
    """The level everything is measured against.

    Kyle's explicit simplification: one number for the whole group rather
    than per-member difficulty, so a level 30 carrying a level 12 recruit
    gets one honest answer instead of five contradictory ones.

    Rounded rather than truncated - a party averaging 19.5 is much closer to
    20 than to 19, and truncation would quietly bias every band downward.
    Benched members do not count; only who is actually standing there.
    """
    members = list(getattr(party, "members", None) or [])
    if not members:
        return fallback
    levels = [getattr(m, "level", fallback) for m in members]
    return max(1, int(round(sum(levels) / len(levels))))


def band_for(target_level, party_level):
    """Which con colour `target_level` shows at, to a party of `party_level`.

    The bands, by difference (target minus party):
        +5 or more ......... red
        +3 to +4 ........... orange
        -2 to +2 ........... yellow
        -3 down to grey .... green
        at or below grey ... grey
    """
    target_level = int(target_level)
    party_level = int(party_level)
    diff = target_level - party_level

    if target_level <= grey_level(party_level):
        return "grey"
    if diff >= 5:
        return "red"
    if diff >= 3:
        return "orange"
    if diff >= -2:
        return "yellow"
    return "green"


def color_for(target_level, party_level):
    """RGB for the band, ready to hand to a renderer."""
    return BAND_COLORS[band_for(target_level, party_level)]


def kill_xp_multiplier(mob_level, party_level):
    """Multiplier on a kill's base XP. 0.0 for anything grey.

    Returns a float, deliberately un-rounded - the caller does the int()
    once at the end, so a chain of bonuses does not lose a point per step.
    """
    mob_level = int(mob_level)
    party_level = int(party_level)

    if mob_level <= grey_level(party_level):
        return 0.0

    diff = mob_level - party_level
    if diff >= 0:
        return 1.0 + 0.05 * min(diff, MAX_LEVEL_BONUS_DIFF)

    zd = zero_difference(party_level)
    return max(0.0, 1.0 - (party_level - mob_level) / float(zd))


def quest_xp_multiplier(quest_level, party_level):
    """Multiplier on a quest's reward_exp.

    Same bands as kills so the colours mean the same thing in both places,
    with ONE deliberate difference: a grey quest pays
    GREY_QUEST_MULTIPLIER rather than zero. A quest is a thing you
    committed to and walked across a zone for; paying literally nothing for
    finishing one punishes the player for having picked it up before they
    outlevelled it, which is not what a trivial tag is meant to say.
    """
    quest_level = int(quest_level)
    party_level = int(party_level)

    if quest_level <= grey_level(party_level):
        return GREY_QUEST_MULTIPLIER

    diff = quest_level - party_level
    if diff >= 0:
        return 1.0 + 0.05 * min(diff, MAX_LEVEL_BONUS_DIFF)

    zd = zero_difference(party_level)
    # Floored at the grey rate rather than at zero: the fade may mathematically
    # reach 0 a level or two before the grey threshold does, and a green quest
    # paying less than a grey one would invert the whole scale.
    return max(GREY_QUEST_MULTIPLIER, 1.0 - (party_level - quest_level) / float(zd))
