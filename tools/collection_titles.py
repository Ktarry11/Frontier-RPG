# -*- coding: utf-8 -*-
"""The Collection's titles (docs/collection_design.md): text shown with the party leader's name.

Kyle, 18 Nov 2026: "Creature forms, Mount colours, Titles", and "Some are dirt cheap. Some are expensive." {name} is
where the character's name goes. Grouped by rarity, which sets the price band in tools/build_collection.py and how
often a title turns up on the auction house. Nothing here names a real person, a brand or a hidden place.
"""

COMMON = [
    "{name} the Wanderer", "{name} the Lost", "{name} the Late", "{name} the Hungry", "{name} the Tourist",
    "{name} the Overpacked", "{name} the Underslept", "{name} of the Long Walk", "{name} the Footsore",
    "{name} the Lightly Singed", "{name} the Mildly Cursed", "{name} the Damp", "{name} the Unwashed",
    "{name} the Easily Distracted", "{name} the Snack Thief", "{name} the Bucket Hero", "{name} the Peckish",
    "{name} the Hopeful", "{name} the Second-Hand", "{name} the Bargain Hunter", "{name} the Window Shopper",
    "{name} the Boar Botherer", "{name} the Kobold Kicker", "{name} the Rat Catcher", "{name} the Mudwalker",
    "{name} of the Crossroads", "{name} the Wayfarer", "{name} the Questing", "{name} the Lost Again",
    "{name} the Well-Meaning", "{name} the Mostly Harmless", "{name} the Polite", "{name} the Chatty",
    "{name} the Grumbler", "{name} the Napper", "{name} the Hearthbound", "{name} the Homesick",
    "{name} the Earthborn", "{name} the Newcomer", "{name} the Transplant", "Apprentice {name}",
    "{name} the Green", "{name} the Fledgling", "{name} the Scrapper", "{name} the Stubborn",
    "{name} the Sandy", "{name} the Sunburnt", "{name} the Frostbitten", "{name} the Seasick",
    "{name} the Saddlesore",
]

UNCOMMON = [
    "{name} the Undercutter", "{name} the Haggler", "{name} the Penny-Pincher", "{name} the Collector",
    "{name} the Hoarder", "{name} the Tinkerer", "{name} the Brewmaster", "{name} the Angler",
    "{name} the Herbwise", "{name} the Ironhanded", "{name} the Loom-Bound", "{name} the Runewright",
    "{name} the Gemcutter", "{name} the Tanner", "{name} the Lumberjack", "{name} the Cook",
    "Murloc Whisperer {name}", "{name} the Raptor Wrangler", "{name} the Kodo Rider", "{name} the Wolf Friend",
    "{name} of Durotar", "{name} of the Barrens", "{name} of Ashenvale", "{name} of Stonetalon",
    "{name} of Stranglethorn", "{name} of Tanaris", "{name} of the Plaguelands", "{name} of Felwood",
    "{name} of Azshara", "{name} of Tirisfal", "{name} of the Silverpine", "{name} of Hillsbrad",
    "{name} the Dungeon Diver", "{name} the Cave Crawler", "{name} the Lootbag", "{name} the Bag Goblin",
    "{name} the Steady", "{name} the Bold", "{name} the Brave", "{name} the Wary", "{name} the Quick",
    "{name} the Patient", "{name} the Lucky", "{name} the Unlucky", "{name} the Unkillable",
    "Sergeant {name}", "Captain {name}", "Lieutenant {name}", "Scout {name}", "Warden {name}",
]

RARE = [
    "{name} the Market Shark", "{name} the Auction Baron", "{name} the Fat Finger", "{name} the Sniper",
    "{name} the Shrewd", "{name} the Silver-Tongued", "{name} the Untouchable", "{name} the Relentless",
    "{name} the Indomitable", "{name} the Lionhearted", "{name} the Stormborn", "{name} the Flamewaker",
    "{name} the Frostsworn", "{name} the Shadowstep", "{name} the Lightbringer", "{name} the Plaguebane",
    "{name} the Scourgebreaker", "{name} the Tidebreaker", "{name} the Dragonfoe", "{name} the Giantslayer",
    "{name} the Kingslayer", "{name} the Oathkeeper", "{name} the Truthseeker", "{name} the Loremaster",
    "{name} the Cartographer", "{name} the Pathfinder", "{name} the Worldwalker", "{name} the Far-Travelled",
    "{name} of Two Worlds", "{name}, Who Came Through", "{name}, Hand of the Horde", "{name} of the Conclave",
    "{name}, Friend of the Timbermaw", "{name}, Keeper of the Inn", "{name} the Undying", "{name}, Bane of Ogres",
    "Champion {name}", "Commander {name}", "Archmage {name}", "High Priest {name}", "Grand Artisan {name}",
    "Battlemaster {name}", "Elder {name}", "Master {name}",
]

EPIC = [
    "{name} the Legend", "{name} the Unbroken", "{name} the Eternal", "{name} the Ascended",
    "{name}, Scourge of Scourges", "{name}, Breaker of the Drowned Court", "{name}, the Integration's Child",
    "{name}, Lord of the Auction House", "{name}, Who Owns Half of Booty Bay", "{name} the Magnificent",
    "{name}, Hero of Azeroth", "{name}, Last of the Earthborn", "{name} the Starborn",
    "{name}, Slayer of a Thousand Boars", "Warlord {name}", "Grand Marshal of Nothing {name}",
    "{name}, Keeper of Every Key", "{name}, the Collector Supreme",
]
