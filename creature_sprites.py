"""Which sprite a creature draws, for dungeon floors and combat.

Kyle: "Currently trash mobs are red boxes and dungeon and cave bosses are generic things. We can
afford up to 5 sprite prompts. So about 36 sprites per sheet... Not every trash needs to be unique,
not every boss needs to be unique sprite. But we can get a lot of them."

WHY THIS IS KEYED ON THE NAME AND NOT ON `template`. boss_icons.py maps the 12 stat templates to 8
tinted portraits, which is why every boss in the game looks like one of eight things: `template` is
a COMBAT archetype (how it fights) and the player reads a SPECIES (what it is). "Hexxer Vul'jin"
and "Searing Flamecaller" are both humanoid_caster and should not be the same picture. 439 creatures
appear in caves and 343 of them are bosses, so template-level art was always going to be generic.

So: first match wins, patterns run against the creature's NAME, and the stat template is only the
fallback when nothing matches. One sprite serves many creatures on purpose - every gnoll in the
game is the gnoll sprite, which is exactly the "not every trash needs to be unique" Kyle asked for.

THE SPRITE LIST IS THE ART ORDER. SHEETS below is the thing the prompts in
claude/dungeon_sprite_prompts.md generate, 36 to a sheet, and tools/qa_creature_sprites.py checks
that every cave creature lands on a sprite that some sheet actually produces. A pattern pointing at
a sprite nobody drew is a red box in a dungeon, found by a player rather than by us.
"""
import re
from pathlib import Path

SPRITE_DIR = Path(__file__).parent / "assets" / "creatures"

#: sheet name -> the sprite ids it draws, 36 each. Order inside a sheet is the grid order the
#: prompt asks for (6 columns x 6 rows, reading left to right, top to bottom).
SHEETS = {
    # ---- 1. the people of the dungeons. 208 cave creatures run on humanoid_* templates,
    #    which is why this sheet is the biggest.
    'humanoids': [
        'archmage_robed', 'bandit_human_1', 'bandit_human_2', 'bandit_human_3',
        'centaur', 'champion_plate', 'cult_overseer', 'cultist_acolyte',
        'cultist_robed_1', 'cultist_robed_2', 'cultist_robed_3', 'dwarf_excavator',
        'executioner_hooded', 'fel_cultist', 'forsaken_apothecary', 'forsaken_soldier',
        'furbolg', 'gnoll', 'goblin_overseer', 'goblin_sapper',
        'harpy', 'harpy_matriarch', 'hunter_ranger', 'kobold',
        'matriarch_brood', 'noble_armoured', 'ogre', 'orc_deserter',
        'pirate_bosun', 'pirate_captain', 'pirate_cutthroat', 'priest_hooded',
        'quilboar', 'quilboar_geomancer', 'satyr', 'syndicate_rogue_1',
        'syndicate_rogue_2', 'trogg', 'troll_axe', 'troll_witchdoctor',
        'warden_armoured',
    ],
    # ---- 2. beasts.
    'beasts': [
        'basilisk', 'bat', 'bear_1', 'bear_2',
        'bear_3', 'boar_1', 'boar_2', 'boar_3',
        'crocolisk_1', 'crocolisk_2', 'gorilla_1', 'gorilla_2',
        'hyena_1', 'hyena_2', 'kodo_1', 'kodo_2',
        'lizard_rock', 'mutated_thing_1', 'mutated_thing_2', 'panther_1',
        'panther_2', 'ram', 'raptor_1', 'raptor_2',
        'saber_cat', 'scorpion', 'serpent_1', 'serpent_2',
        'stag', 'thresher', 'toad_giant', 'turtle_snapping',
        'vulture_1', 'vulture_2', 'worg_1', 'worg_2',
        'worg_3',
    ],
    # ---- 3. vermin, swarms and the wet things.
    'vermin_aquatic': [
        'crab_giant_1', 'crab_giant_2', 'crawler_shell_1', 'crawler_shell_2',
        'drowned_sailor_1', 'drowned_sailor_2', 'eel_electric_1', 'eel_electric_2',
        'maggot', 'murloc_1', 'murloc_2', 'naga_myrmidon_1',
        'naga_myrmidon_2', 'naga_warrior', 'ooze_acid_1', 'ooze_acid_2',
        'rat_plague_1', 'rat_plague_2', 'reefcrawler', 'sea_witch',
        'silithid_worker_1', 'silithid_worker_2', 'slime_green_1', 'slime_green_2',
        'spider_1', 'spider_2', 'spider_3', 'spider_broodmother_1',
        'spider_broodmother_2', 'spider_hatchling', 'tentacle_horror_1', 'tentacle_horror_2',
        'tide_lurker_1', 'tide_lurker_2', 'wasp',
    ],
    # ---- 4. undead and demons.
    'undead_demon': [
        'abomination_1', 'abomination_2', 'banshee', 'crypt_fiend_1',
        'crypt_fiend_2', 'demon_brute_1', 'demon_brute_2', 'doomguard_1',
        'doomguard_2', 'felhound_1', 'felhound_2', 'ghoul_1',
        'ghoul_2', 'imp_1', 'imp_2', 'necromancer',
        'revenant_1', 'revenant_2', 'skeleton_archer_1', 'skeleton_archer_2',
        'skeleton_archer_3', 'skeleton_warrior_1', 'skeleton_warrior_2', 'spectre_1',
        'spectre_2', 'voidwalker_1', 'voidwalker_2', 'wraith_1',
        'wraith_2', 'wraith_3', 'zombie_1', 'zombie_2',
        'zombie_3', 'zombie_4',
    ],
    # ---- 5. elementals, plants and constructs.
    'elemental_plant': [
        'bog_lord_1', 'bog_lord_2', 'crystal_sentinel', 'crystal_shardling_1',
        'crystal_shardling_2', 'elemental_air_1', 'elemental_air_2', 'elemental_air_3',
        'elemental_arcane', 'elemental_earth_1', 'elemental_earth_2', 'elemental_fire_1',
        'elemental_fire_2', 'elemental_fire_3', 'elemental_fire_4', 'elemental_water',
        'golem_stone_1', 'golem_stone_2', 'golem_stone_3', 'golem_stone_4',
        'lattice_grown_1', 'lattice_grown_2', 'sapling_thorn', 'spore_cap_1',
        'spore_cap_2', 'spore_cap_3', 'treant_1', 'treant_2',
        'vine_strangler_1', 'vine_strangler_2', 'vine_strangler_3', 'wisp_1',
        'wisp_2',
    ],
}

#: sprite id -> how many different looks of it the sheets draw, as <id>_1 .. <id>_n.
#: DERIVED FROM USE, not chosen: 78 creatures land on bandit_human and 62 on worg, so those
#: get four looks each, while a sprite one creature uses gets one. The variant is picked by
#: hashing the creature's NAME, so no rule has to know about them and the same creature is
#: always the same picture - the point is that a room of gnolls is not one gnoll stamped out
#: eight times, which is what Kyle means by "not every trash needs to be unique" still
#: leaving room for "but we can get a lot of them".
VARIANTS = {
    'abomination': 2,
    'bandit_human': 3,
    'bear': 3,
    'boar': 3,
    'bog_lord': 2,
    'crab_giant': 2,
    'crawler_shell': 2,
    'crocolisk': 2,
    'crypt_fiend': 2,
    'crystal_shardling': 2,
    'cultist_robed': 3,
    'demon_brute': 2,
    'doomguard': 2,
    'drowned_sailor': 2,
    'eel_electric': 2,
    'elemental_air': 3,
    'elemental_earth': 2,
    'elemental_fire': 4,
    'felhound': 2,
    'ghoul': 2,
    'golem_stone': 4,
    'gorilla': 2,
    'hyena': 2,
    'imp': 2,
    'kodo': 2,
    'lattice_grown': 2,
    'murloc': 2,
    'mutated_thing': 2,
    'naga_myrmidon': 2,
    'ooze_acid': 2,
    'panther': 2,
    'raptor': 2,
    'rat_plague': 2,
    'revenant': 2,
    'serpent': 2,
    'silithid_worker': 2,
    'skeleton_archer': 3,
    'skeleton_warrior': 2,
    'slime_green': 2,
    'spectre': 2,
    'spider': 3,
    'spider_broodmother': 2,
    'spore_cap': 3,
    'syndicate_rogue': 2,
    'tentacle_horror': 2,
    'tide_lurker': 2,
    'treant': 2,
    'vine_strangler': 3,
    'voidwalker': 2,
    'vulture': 2,
    'wisp': 2,
    'worg': 3,
    'wraith': 3,
    'zombie': 4,
}

#: sprite id -> set of every sprite the art actually produces.
ALL_SPRITES = {s for v in SHEETS.values() for s in v}

#: FIRST MATCH WINS, so order matters - the specific sits above the general. Each entry is
#: (compiled pattern on the creature NAME, sprite id).
_RULES = [
    # --- named species that would otherwise be caught by a weaker rule
    (r"broodmother|brood tender|brood queen", "spider_broodmother"),
    (r"hatchling|spiderling", "spider_hatchling"),
    (r"spider|weaver|webspinner|arachn", "spider"),
    (r"silithid.*warrior|hive.*warrior", "silithid_worker"),
    (r"silithid|hive", "silithid_worker"),
    (r"scarab|beetle", "silithid_worker"),
    (r"wasp.*queen|queen.*wasp", "wasp"),
    (r"wasp|hornet|stinger", "wasp"),
    (r"centipede", "maggot"),
    (r"maggot|grub", "maggot"),
    (r"\brats?\b|vermin", "rat_plague"),
    (r"ooze|acid", "ooze_acid"),
    (r"slime|sludge|muck", "slime_green"),
    (r"carapace|shardback|crawler", "crawler_shell"),

    # --- aquatic
    (r"naga.*(myrmidon|warrior|guard)", "naga_myrmidon"),
    (r"naga.*(siren|witch|sorcer)|sea witch", "sea_witch"),
    (r"\bnaga\b", "naga_warrior"),
    (r"drowned.*(captain|bosun|officer)", "pirate_captain"),
    (r"drowned|waterlogged|sodden", "drowned_sailor"),
    (r"murloc|makrura", "murloc"),
    (r"tidecaller|tide|lurker", "tide_lurker"),
    (r"eel", "eel_electric"),
    (r"jellyfish", "tentacle_horror"),
    (r"thresher", "thresher"),
    (r"crab", "crab_giant"),
    (r"turtle|snapper", "turtle_snapping"),
    (r"coral", "golem_stone"),
    (r"reef|siltfin|brinescale|brine", "reefcrawler"),
    (r"tentacl|horror", "tentacle_horror"),

    # --- undead
    (r"abomination|stitch", "abomination"),
    (r"skeleton.*(archer|bowman)|bone.*archer", "skeleton_archer"),
    (r"skeleton.*(mage|caster)|bone.*mage", "skeleton_archer"),
    (r"skeleton|bonewarden|bone ", "skeleton_warrior"),
    (r"ghoul", "ghoul"),
    (r"zombie|shambler|risen", "zombie"),
    (r"banshee", "banshee"),
    (r"wraith|spectre|specter|shade", "wraith"),
    (r"\bghost\b|apparition|phantom", "spectre"),
    (r"necromancer|animator", "necromancer"),
    (r"lich", "necromancer"),
    (r"gargoyle", "crypt_fiend"),
    (r"crypt", "crypt_fiend"),
    (r"mummy|bound dead", "zombie"),
    (r"revenant", "revenant"),

    # --- demons
    (r"\bimps?\b", "imp"),
    (r"felhound|felstalker|hound of|doomhound", "felhound"),
    (r"voidwalker|void ", "voidwalker"),
    (r"succubus", "fel_cultist"),
    (r"doomguard", "doomguard"),
    (r"infernal", "demon_brute"),
    (r"satyr", "satyr"),
    (r"felsworn|fel |demon", "demon_brute"),

    # --- elementals, plants, constructs
    (r"(fire|flame|ember|magma|molten|lava|cinder|searing|smolder).*(elemental|spirit|guardian|caller|lord)",
     "elemental_fire"),
    (r"(water|tide|wave|naiad).*(elemental|spirit|lord)", "elemental_water"),
    (r"(earth|stone|rock|granite|crag).*(elemental|spirit|lord)", "elemental_earth"),
    (r"(air|wind|storm|gale|thunder).*(elemental|spirit|lord|caller)", "elemental_air"),
    (r"(ice|frost|rime|winter).*(elemental|spirit|lord)", "elemental_water"),
    (r"(arcane|mana|spell|vein-lit|veinlit).*(elemental|spirit|wisp)", "elemental_arcane"),
    (r"(shadow|void|dark|umbral).*(elemental|spirit|lord)", "elemental_arcane"),
    (r"\bmote\b", "wisp"),
    (r"lattice", "lattice_grown"),
    (r"crystal.*(sentinel|guardian|warden)|amber sentinel", "crystal_sentinel"),
    (r"crystal|shardling|geode|glitter", "crystal_shardling"),
    (r"construct|golem|sentinel", "golem_stone"),
    (r"\bwisp\b", "wisp"),
    (r"treant|ancient|bark|timber", "treant"),
    (r"sapling|sprout", "sapling_thorn"),
    (r"spore|gloomcap|fungal|mushroom|myconid", "spore_cap"),
    (r"vine|strangler|thorn|creeper", "vine_strangler"),
    (r"bog|peat|marsh|mire", "bog_lord"),
    (r"dryad", "sapling_thorn"),

    # --- beasts
    (r"worg|wolf|lupine|howler", "worg"),
    (r"raptor|velocir", "raptor"),
    (r"\bbats?\b|nightwing", "bat"),
    (r"bear|ursa", "bear"),
    (r"boar|battleboar|tusker", "boar"),
    (r"hyena|jackal", "hyena"),
    (r"panther|stalker|prowler", "panther"),
    (r"saber|sabre|\bcat\b|lynx", "saber_cat"),
    (r"basilisk", "basilisk"),
    (r"serpent|snake|cobra|adder|viper", "serpent"),
    (r"crocolisk|crocodile|gator", "crocolisk"),
    (r"kodo", "kodo"),
    (r"scorpion|scorpid", "scorpion"),
    (r"\bram\b|goat", "ram"),
    (r"stag|deer|elk", "stag"),
    (r"owlbeast|owlkin", "bear"),
    (r"gorilla|ape", "gorilla"),
    (r"tiger", "saber_cat"),
    (r"vulture|buzzard|carrion bird", "vulture"),
    (r"toad|frog|hopper", "toad_giant"),
    (r"lizard|strider|monitor", "lizard_rock"),
    (r"plainstrider|strider", "vulture"),

    # --- humanoids (broadest, so last)
    (r"gnoll.*(shaman|mystic|caster)", "gnoll"),
    (r"gnoll", "gnoll"),
    (r"kobold.*(taskmaster|foreman|overseer)", "kobold"),
    (r"kobold", "kobold"),
    (r"harpy.*(matriarch|queen)", "harpy_matriarch"),
    (r"harpy|windcaller", "harpy"),
    (r"quilboar.*(geomancer|shaman|mystic)|razorfen.*(geomancer|shaman)", "quilboar_geomancer"),
    (r"quilboar|razorfen|bristleback", "quilboar"),
    (r"centaur|kolkar|galak", "centaur"),
    (r"ogre.*(mage|magus)", "ogre"),
    (r"ogre", "ogre"),
    (r"troll.*(witch|hex|shadow|priest)", "troll_witchdoctor"),
    (r"troll|zul'|vilebranch", "troll_axe"),
    (r"trogg", "trogg"),
    (r"furbolg", "furbolg"),
    (r"(bloodsail|southsea|pirate).*(captain|lord)", "pirate_captain"),
    (r"bosun|swabbie|deckhand|gaffer", "pirate_bosun"),
    (r"bloodsail|southsea|pirate|buccaneer|corsair|cutthroat|wrecker", "pirate_cutthroat"),
    (r"syndicate|thug|bandit|brigand|highwayman", "syndicate_rogue"),
    (r"cultist.*(overseer|master|high)", "cult_overseer"),
    (r"acolyte|initiate|novice", "cultist_acolyte"),
    (r"cultist|zealot|twilight", "cultist_robed"),
    (r"apothecary|chemist|plaguebringer", "forsaken_apothecary"),
    (r"forsaken|deathguard", "forsaken_soldier"),
    (r"(venture|goblin).*(overseer|foreman|boss)", "goblin_overseer"),
    (r"goblin|venture|sapper|tinker", "goblin_sapper"),
    (r"dwarf|excavator|prospector|dark iron", "dwarf_excavator"),
    (r"deserter|grunt|orc\b", "orc_deserter"),

    # --- TITLES, last of all and above only the stat template.
    # 122 of the creatures reaching this point are BOSSES WITH PERSONAL NAMES - "Archmage Arugal",
    # "Baron Silverlaine", "Aku'mai" - which carry no species at all. Their stat template is the
    # only thing left, and a template is how every boss ended up looking like one of eight things
    # in the first place. A title is weak evidence but it is real evidence: an Archmage is robed
    # and a Captain is armoured, and matching that beats drawing both as the same hooded figure.
    (r"\b(archmage|magus|sorcer\w*|conjur\w*|arcanist|spellbinder)\b", "archmage_robed"),
    (r"\b(baron|baroness|lord|lady|duke|count|prince)\b", "noble_armoured"),
    (r"\b(captain|admiral|commodore|skipper)\b", "pirate_captain"),
    (r"\b(warden|keeper|guardian|sentinel|custodian)\b", "warden_armoured"),
    (r"\b(matriarch|queen|broodmother|dam)\b", "matriarch_brood"),
    (r"\b(overseer|foreman|taskmaster|master|boss)\b", "cult_overseer"),
    (r"\b(priest|prophet|oracle|seer|hierophant|bishop|brother|sister)\b", "priest_hooded"),
    (r"\b(hunter|tracker|stalker|ranger|marksman|archer)\b", "hunter_ranger"),
    (r"\b(champion|warlord|general|commander|marshal|knight)\b", "champion_plate"),
    (r"\b(butcher|executioner|headsman|reaper|slayer)\b", "executioner_hooded"),
    (r"\b(apothecary|alchemist|chemist|surgeon)\b", "forsaken_apothecary"),
    (r"\b(shaman|witchdoctor|hexxer|voodoo|totem)\b", "troll_witchdoctor"),
    (r"\b(blade|swordsman|duelist|bladedancer)\b", "champion_plate"),
    (r"\b(searing|burning|flame\w*|ember\w*|cinder\w*)\b", "elemental_fire"),
    (r"\b(deviate|mutated|corrupted|twisted|warped)\b", "mutated_thing"),
    (r"\b(hollow|husk|withered|desiccated)\b", "wraith"),
    (r"\b(hound|fang|maw|howl\w*)\b", "worg"),
]

RULES = [(re.compile(p, re.I), s) for p, s in _RULES]

#: Last resort when no name pattern matches: the stat template. Deliberately a small, obvious set -
#: anything landing here is a creature the name rules should probably learn about.
TEMPLATE_FALLBACK = {
    "humanoid_warrior": "bandit_human",
    "humanoid_caster": "cultist_robed",
    "humanoid_ranged": "skeleton_archer",
    "humanoid_rogue": "syndicate_rogue",
    "beast_large": "bear",
    "beast_fast": "worg",
    "beast_basic": "boar",
    "vermin_sneaky": "spider",
    "vermin_swarm": "rat_plague",
    "undead_basic": "zombie",
    "elemental_bruiser": "golem_stone",
    "elemental_caster": "elemental_fire",
    "demon_caster": "fel_cultist",
    "demon_hound": "felhound",
    "aquatic_basic": "murloc",
}

DEFAULT = "bandit_human"

#: 23 rules used to name species no creature in the game actually has - gargoyle, dryad, tiger,
#: lich. They were written from imagination while the sprite list was, and when SHEETS was rebuilt
#: from real usage their art was correctly dropped, leaving the rules pointing at nothing. Rather
#: than delete them or spend scarce cells on monsters that do not exist, each now resolves to its
#: nearest drawn neighbour: add a gargoyle later and it draws the crypt fiend until it earns art.


def sprite_for(name, template=None):
    """-> sprite id for a creature. Never None, so nothing ever renders as a red box again."""
    for rx, sprite in RULES:
        if rx.search(name or ""):
            return sprite
    return TEMPLATE_FALLBACK.get(template, DEFAULT)


def sprite_file(name, template=None):
    """-> the sprite id to actually draw for this creature, variant included.

    The variant is chosen by hashing the creature's name, which keeps it stable across sessions
    and across machines without storing anything: the same gnoll is always the same gnoll.
    """
    base = sprite_for(name, template)
    n = VARIANTS.get(base)
    if not n:
        return base
    # zlib.crc32 rather than hash(): Python's hash is randomised per process, so a creature would
    # change its appearance every time the game restarted.
    import zlib
    return f"{base}_{zlib.crc32((name or '').encode('utf-8')) % n + 1}"


def sprite_path(sprite_id):
    return SPRITE_DIR / f"{sprite_id}.png"
