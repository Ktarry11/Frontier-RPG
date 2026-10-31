"""THE ONE PLACE THE COIN SPLIT IS WRITTEN. 100 copper = 1 silver, 100 silver = 1 gold.

Imports nothing, so anything in the game can import it without a cycle, which is the whole
reason it sits here rather than in ui/ or world/.

It exists because the split had been written FIVE times - ui/coin_format.format_coins,
world/travel_manager.format_copper, entities/bank.gold_str, Party.get_currency_string, and a
hand-rolled f-string in the quest screens - and the five did not agree:

  - the three quest-screen copies printed `g` and `s` and NOTHING ELSE, so 178 quests in the
    game understated their own reward by up to 99 copper and every sub-gold quest in the game
    read "0g 33s" with a leading zero nobody would ever write by hand.
  - format_copper always printed all three parts ("200g 0s 0c"), format_coins skipped the empty
    ones ("200g"), so the mount vendor and the riding trainer disagreed about how money looks
    while sitting in the same shop.

Two shapes, and the difference is whether the width is allowed to move:

  coins(c)              -> "200g", "33s 60c", "45c", "0c"       prices, rewards, messages
  coins(c, full=True)   -> "200g 0s 0c", "0g 33s 60c"           the purse in the HUD, which
                                                                should not twitch as you spend
"""


def coins(copper, full=False):
    """Copper as gold/silver/copper. `full` keeps all three parts so the width is stable."""
    g, rem = divmod(max(0, int(copper)), 10000)
    s, c = divmod(rem, 100)
    if full:
        return f"{g}g {s}s {c}c"
    parts = ([f"{g}g"] if g else []) + ([f"{s}s"] if s else []) + ([f"{c}c"] if c else [])
    return " ".join(parts) or "0c"
