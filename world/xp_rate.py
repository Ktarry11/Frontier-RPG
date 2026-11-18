"""The player's own experience rate: 0.5x to 3x, for quests and kills.

Kyle, 18 Nov 2026: "a toggle tab in the bottom of the screen where it looks nice. IT will be a EXP toggle for
players. So it can be set as 0.5x, 1x, 1.5x, 2x, 2.5x, or 3x EXP which will be for quests and kills. So people can
pick their own level of fun."

It belongs to the save (Party.xp_rate, written with the party), so each character keeps its own pace. It's applied
last, on top of everything else a kill or a quest pays (combat/combat_engine.py's kill reward and world/quest.py's
quest reward), the same place the global rates are, so the quest card shows what you'll actually get.
"""
RATES = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
DEFAULT = 1.0

_PARTY = None


def bind(party):
    """The party whose rate counts (entities/party.py binds itself when it's made)."""
    global _PARTY
    _PARTY = party


def current():
    rate = getattr(_PARTY, "xp_rate", DEFAULT) if _PARTY is not None else DEFAULT
    return rate if rate in RATES else DEFAULT


def set_rate(party, rate):
    if rate not in RATES:
        return False
    party.xp_rate = rate
    return True


def label(rate):
    return f"{rate:g}x"
