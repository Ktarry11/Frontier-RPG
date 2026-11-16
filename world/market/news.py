"""Market news: the things that happen out in the world and move prices (docs/auction_house_design.md, section 4).

About once every forty market hours per book, something happens to a family of goods and its price index takes a
shock (still inside the clamp, and it wears off on its own). The auctioneer passes the latest on at the top of the
window, so a player who reads it can buy before a spike or sell into one.

Only open-world places, only things a trader would gossip about. Each row: (family or families, multiplier range,
text). A family is catalog.Entry.family: a material word ("silk", "copper"), a material type ("herb", "fish",
"cut_gem") or a consumable type ("elixir", "meal").
"""
from world.market import catalog as C

UP, DOWN = (1.35, 1.9), (0.55, 0.8)

ROWS = [
    (("silk",), UP, "The spiders of Silverpine have gone to ground, and silk is getting hard to find."),
    (("silk",), DOWN, "A Forsaken tailors' guild sold off its silk stores to pay a debt. There's silk everywhere."),
    (("wool",), UP, "Something's been taking the sheep in Hillsbrad. Wool's gone up."),
    (("linen", "cotton"), DOWN, "Refugees have been bringing bolts of old linen into the cities to sell."),
    (("mageweave", "runecloth"), UP, "The Undercity's apothecaries are wrapping something big. They're buying every bolt of good cloth they can."),
    (("copper", "tin"), DOWN, "A caravan of copper and tin got through from Ratchet. The smiths are swimming in it."),
    (("copper", "tin", "bronze"), UP, "Orgrimmar's armourers have a war order in. Copper and tin are selling as fast as they're mined."),
    (("iron",), UP, "The Venture Company bought up every iron claim in Stonetalon they could find."),
    (("iron",), DOWN, "A new seam opened in the Barrens and iron's flooding the market."),
    (("silver", "gold"), UP, "Goblins are hoarding silver and gold again. Nobody will say why."),
    (("mithril", "thorium"), UP, "Mithril and thorium are scarce. Every deep miner went south for the season."),
    (("herb",), UP, "A blight's in the herb fields of the Barrens. Healers are paying anything for clean leaves."),
    (("herb",), DOWN, "It was a good spring. Herbalists can't give their leaves away."),
    (("peacebloom", "kingsblood"), UP, "Every alchemist in the Horde wants peacebloom and kingsblood this week."),
    (("fish",), DOWN, "The shoals came in thick off Ratchet and Booty Bay. Fish is cheap."),
    (("fish",), UP, "Storms off the coast have kept the fishing boats in harbour."),
    (("meat", "meal"), UP, "A feast's being planned in Thunder Bluff. The cooks are buying everything."),
    (("meal",), DOWN, "Somebody flooded the cities with cheap stew. Good food's going for a song."),
    (("elixir",), UP, "Word is a big push is coming. Elixirs are being bought by the crate."),
    (("elixir",), DOWN, "A Ratchet alchemist overmade by a thousand elixirs. You can guess what happened to the price."),
    (("explosive",), UP, "The Sappers' Guild is short of charges. Anything that goes boom is in demand."),
    (("gadget", "part"), UP, "The Shimmering Flats racers are building again. Gadgets and parts are flying off the shelves."),
    (("leather",), UP, "Kodo herds moved east out of the Barrens, and the leatherworkers are feeling it."),
    (("leather",), DOWN, "The hunting's been good. Hides are piled to the rafters."),
    (("gem", "cut_gem"), UP, "A Steamwheedle baron is getting married. Gems are very expensive this week."),
    (("gem", "cut_gem"), DOWN, "A prospector in Thousand Needles struck it lucky. Gems are cheap for once."),
    (("mob_reagent",), UP, "Collectors are paying silly money for creature parts. Something about a museum."),
    (("wood", "plank"), UP, "Ashenvale's sentinels have shut the logging camps again. Timber's dear."),
    (("wood", "plank"), DOWN, "A lumber barge came down from Stonetalon. Wood's cheap."),
    (("crystal",), UP, "Engineers want crystals for something new. It's probably going to explode."),
    (("upgrade_kit",), DOWN, "The smiths have a surplus of upgrade kits after the season's orders fell through."),
    (("ammo",), UP, "Hunters are stocking up for a hunt in Feralas. Ammunition's short."),
]


def pick(rng):
    """(text, keys, multiplier) for one piece of news, or None."""
    entries = C.entries()
    for _ in range(8):
        fams, (lo, hi), text = rng.choice(ROWS)
        keys = [k for k, e in entries.items() if e.family in fams]
        if keys:
            return text, keys, rng.uniform(lo, hi)
    return None
