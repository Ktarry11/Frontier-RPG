"""
Maps world biome_ids (world.tile_textures.ZONE_BIOME / CAVE_BIOME) to combat
background asset folders under assets/backgrounds/. The background pack only
covers 7 folders (desert, jungle, mountain, mossy_forest, dark_dungeon,
fire_dungeon, ice_dungeon) while the world defines ~19 biome tags, so every
biome not covered directly is nearest-matched onto one of the 7 rather than
falling back to one single generic image everywhere.

Three of the seven folders have Morning/Afternoon/Night or Dark/Normal
sub-variants; the other three (dark/fire/ice dungeon) are flat. Callers pass
a variant hint and get silently routed to the flat folder if the biome has
no variants.
"""

# Folders that have time-of-day (or Dark/Normal) subfolders vs. flat ones.
VARIANT_FOLDERS = {
    # The Morning/Afternoon/Night split on desert, jungle, mountain and mossy_forest went away
    # with the art it was built for: those packs held ~30 images each, enough to fill three times
    # of day. The replacement set is 2-8 per pack, and splitting 2 desert images across 3 folders
    # left two of them empty - which is not a thin pack, it is ELEVEN PLACES WITH NO BACKGROUND,
    # because the loader resolves into a variant folder and only falls back to a flat base that
    # by then held no files either. Found by qa_combat_backgrounds, not by playing.
    #
    # nautical's variants are not times of day, they are three different PLACES a sea fight
    # happens: an open weather deck, below decks, and standing water underground. A caller must
    # pin one - the default-to-first behaviour that suits Morning/Afternoon/Night would put a
    # drowned mine on a sunlit quarterdeck. ZONE_BACKGROUND pins every nautical place.
    "nautical": ("Deck", "Hold", "Flooded"),
}
FLAT_FOLDERS = ("dark_dungeon", "fire_dungeon", "ice_dungeon", "desert", "savanna", "savanna_oasis", "jungle", "mountain",
                "mossy_forest", "fantasy_forest", "blighted", "crystal", "fungal", "sky", "hive", "salt_flat",
                "keep", "arena")

# Nearest-match: every ZONE_BIOME / CAVE_BIOME tag in world/tile_textures.py
# routed to whichever of the 7 available packs reads closest. Chosen by eye
# from the biome's actual visual character (see tile_textures.py's own
# comments on each), not just name similarity.
BIOME_TO_BACKGROUND = {
    # Direct/near-direct matches
    "desert": "desert",
    "desert_oasis": "desert",
    "tropical": "jungle",
    # Ashenvale, Astranaar, Zoram Strand, Splintertree Post. Routed to jungle when jungle was the
    # only pack with big trees in it, so they drew the same overgrown stepped temple as Booty
    # Bay, a continent away - Kyle: "Ashenvale is a forest not troll ruins". Moving them to
    # mossy_forest was not enough either, because that pack also holds a farm cottage and a barn,
    # which is Hillsbrad. fantasy_forest is woodland only: the glowing-motes forest and the
    # autumn lakeshore, matching tile_textures' own description of these zones ("teal/gold
    # fantasy trees... the sparkle/beauty read").
    "mythical_forest": "fantasy_forest",
    # The undead belt - Silverpine, Tirisfal, the Sepulcher, Fenris Isle, Deathknell, Brill and
    # Undercity itself - fought in a healthy green forest and a generic stone dungeon until the
    # blighted pack existed. Nine zones, all of them explicitly written as dead country.
    "decayed_forest": "blighted",
    "undead": "blighted",
    "orgrimmar": "desert",          # red-rock urban stone, closest to desert set
    "bael_modan": "mountain",

    # Savanna variants. These pointed at "desert" because no savanna pack
    # existed - Kyle, 7 Nov: "We need to fix up barrens background, its a
    # savanna, not a desert." He was right twice over: the Barrens is dry
    # grassland, AND the desert pack it borrowed from is Tanaris art -
    # pyramids, dunes and a sun-bleached kodo skeleton on cracked hardpan.
    # Every fight in the Crossroads was happening in Egypt.
    #
    # THE ART ALREADY EXISTED, FILED WRONG. desert/ held five images and
    # two of them were not deserts: s2_01 is an acacia against golden grass
    # at sunset, which is the Barrens exactly, and s7_02 is a palm-ringed
    # pool, which is Lushwater. Both moved to assets/backgrounds/savanna/
    # rather than copied - desert keeps the three that really are desert
    # (bone field, open dunes, sandstone ruins) and is no longer carrying
    # art that contradicts it.
    #
    # They are two SEPARATE packs, not one pack of two. Open scrub and a
    # palm-ringed pool are different places, and a single savanna/ folder
    # holding both would have put the oasis on screen for half the fights
    # in the open Crossroads - the same category of wrongness as the desert
    # it replaced, just prettier. One image each for now, which is thin but
    # honest; prompts for more are in docs/background_prompts.md.
    "savanna": "savanna",
    "savanna_bones": "savanna",
    "savanna_thornscrub": "savanna",
    # The three Central Barrens oases. savanna_oasis was in SUBZONE_BIOME
    # but NEVER IN THIS TABLE, so it fell through get_background_folder's
    # default and Lushwater fought in a mossy forest.
    "savanna_oasis": "savanna_oasis",
    # Orphaned by the oasis remap (see SUBZONE_BIOME) but still routed, so
    # it degrades to savanna rather than a rainforest if anything revives it.
    "savanna_pond": "savanna_oasis",
    "savanna_cliff": "mountain",
    # Slug Fens - waterlogged bog. jungle is right for this one: standing
    # water and dense green, not open grass.
    "barrens_fen": "jungle",

    # Cave variants -> the three dungeon packs by color temperature, per
    # tile_textures.py's own warm/cold/sick/dark/mossy descriptions.
    "cave_warm": "fire_dungeon",
    "cave_cold": "ice_dungeon",
    "cave_sick": "dark_dungeon",    # purple/wine reads closest to dark, not fire or ice
    "cave_dark": "dark_dungeon",
    "cave_mossy": "dark_dungeon",   # DampDungeons warm stone, but no green-cave pack exists
    "cave_swamp": "dark_dungeon",
    "cave_thornscrub": "dark_dungeon",

    # Cave biomes added after this table was first written, each of which defines its own
    # BIOME_TILES palette at the bottom of tile_textures.py but was never routed to a pack. All
    # ten silently became mossy_forest, which is how Ragefire Chasm, Shadowfang Keep and
    # Blackfathom Deeps ended up fighting in a sunny green forest.
    "cave_ragefire": "fire_dungeon",     # basalt, ash, molten floor
    "cave_sunken": "ice_dungeon",        # built from cave_cold; kelp and tidepool blues
    "cave_grotto": "ice_dungeon",        # built from cave_naga; same cold water read
    "cave_webbed": "dark_dungeon",
    "cave_keep": "dark_dungeon",         # dressed stone, not rock
    "cave_demonic": "fire_dungeon",      # Burning Blade Coven, Skull Rock
    "cave_canyon": "mountain",           # Drygulch Ravine - open-air cut, not a roofed cave
    "cave_dustwind": "desert",
    "cave_flooded_ruins": "dark_dungeon",
    "cave_troll_ruins": "jungle",        # Zalazane's Hollow, in the Echo Isles

    # Fallback used by get_biome_for_zone() itself when a zone has no entry.
    "grassland": "mossy_forest",
}


# ---------------------------------------------------------------------------
# PER-PLACE BACKGROUND OVERRIDE.
#
# Deliberately NOT done by adding entries to ZONE_BIOME / CAVE_BIOME, even though that is where
# a biome "belongs". Those tables are read by ui/tilemap_renderer.py to choose the actual FLOOR
# AND WALL TEXTURES of a zone, so adding 43 entries to fix 43 backdrops would have quietly
# repainted 43 hand-built zones. The backdrop behind a fight and the palette of the ground you
# walk on are two different questions that happened to share one answer; this is the seam.
#
# Checked before the biome path, so a place listed here needs no biome entry at all and nothing
# about its tiles moves. Value is a pack folder name, or (folder, variant) to pin a variant.
#
# Everything here was read off the zone's own tools/handbuilt_*.py docstring rather than guessed
# from its name - those docstrings state the visual character outright ("A salt pan is dead
# flat", "the whole lower half is one great SUMP of standing water").
ZONE_BACKGROUND = {
    # --- open country ------------------------------------------------------
    "Eastern Hillsbrad": "mossy_forest",          # "the first HEALTHY country"
    "Western Hillsbrad": "mossy_forest",          # worked green fields, farm country
    "Eastern Kingdoms - Stranglethorn": "jungle",  # region label over the tropical zones

    # --- desert and salt ---------------------------------------------------
    "Northern Tanaris": "desert",
    "The Abyssal Sands": "desert",                # collapse pits across open desert
    # "The Shimmering Flats" is set in the .update() below, to salt_flat. The salt pack DOES
    # exist (assets/backgrounds/salt_flat); the note that once sat here saying otherwise was
    # stale, and the dead "desert" entry it justified has been removed.
    "Glittervein": "desert",                      # dead desert rim; the lake is the floor, not the backdrop

    # --- rock, canyon, highland. The mountain pack has 30 images and until
    #     now served nothing at all.
    "Southern Thousand Needles": "mountain",      # mesas and sheer rims
    "The Aspen Wilderness": "mountain",           # real elevation, headwalls, glacial benches
    "Rocky Pass": "mountain",                     # "an alpine dungeon above the treeline... outside"
    "Serena's Hollow": "mountain",                # "THE CLIFF GORGE"
    "Thunder Ridge": "mountain",                  # canyon rooms in red-rock Durotar
    "Boulder Lode Mine": "mountain",              # switchback terraces cut into cliffs

    # --- roofed stone ------------------------------------------------------
    # A stepped pit with barred gates, which is what it is. It will not actually be seen until
    # the arena has fighters in it - it currently has no encounter table at all - but the wiring
    # should be right before the roster lands, not after.
    "Gurbashi Arena": "arena",
    "Dun Garok": "dark_dungeon",                  # "the dwarves cut it square"
    "Durnholde Keep": "dark_dungeon",             # curtain wall, dead keep, collapsed undercroft
    "The Broodspiral": "dark_dungeon",            # silithid hive spiralling into the earth
    "The Undercrust": "dark_dungeon",             # the hive under the salt pan
    "The Deep Bloom": "dark_dungeon",             # grown tissue imitating architecture; nearest fit

    # --- ice ---------------------------------------------------------------
    "The Weeping Ice": "ice_dungeon",             # "a dying glacier's plumbing"
}

ZONE_BACKGROUND.update({
    # --- at sea and on deck, variant pinned (see VARIANT_FOLDERS["nautical"]) -------------
    "Ratchet": ("nautical", "Deck"),                     # crescent harbour, the only waterfront
    "The Crossing": ("nautical", "Deck"),                # the boat home from Booty Bay
    "The Bloodsail Anchorage": ("nautical", "Deck"),     # a cove, not a ship at all
    "The Bloodsail Raider": ("nautical", "Deck"),        # weather deck, stern to bow
    "The Galleon's Weather Deck": ("nautical", "Deck"),
    "The Lashings": ("nautical", "Deck"),                # nine hulls lashed together

    # --- below decks ----------------------------------------------------------------------
    "The Captain's Cabin": ("nautical", "Hold"),
    "The Galleon's Hold": ("nautical", "Hold"),
    "The Raider's Hold": ("nautical", "Hold"),

    # --- standing water underground ---------------------------------------------------------
    "Azurelode Mine": ("nautical", "Flooded"),           # "one great SUMP of standing water"
    "Rotvine Hollow": ("nautical", "Flooded"),           # flooded root cavern
    "The Cistern": ("nautical", "Flooded"),              # the outflow, pulled down and pushed up
    "The Drownbell": ("nautical", "Flooded"),            # pirate cove under the Tanaris range
    "The Drowned Shrine": ("nautical", "Flooded"),       # flooded colonnade
    "The Drowning Floor": ("nautical", "Flooded"),       # "where the year's flood goes"
    "Veilfall Cave": ("nautical", "Flooded"),            # ring terraces round a plunge pool

    # --- crystal and arcane -----------------------------------------------------------------
    "The Crystalline Underdark": "crystal",              # "IT MUST NOT READ AS A CAVE"
    "The Hollow Geode": "crystal",                       # the druse gallery
    "The Mother Vein": "crystal",                        # walking inside the ore shoot
    "The Frostward Descent": "crystal",                  # ice into seam into arcane

    # --- grown, not built -------------------------------------------------------------------
    "The Deep Bloom": "fungal",                          # "FROM ARCHITECTURE INTO TISSUE"

    # --- hives ------------------------------------------------------------------------------
    "The Broodspiral": "hive",                           # the silithid hive spiralling down
    "The Undercrust": "hive",                            # the hive under the salt pan

    # --- a salt pan is not a desert ----------------------------------------------------------
    "The Shimmering Flats": "salt_flat",                 # "A salt pan is dead flat"

    # --- dressed stone, not rock --------------------------------------------------------------
    "Dun Garok": "keep",                                 # "the dwarves cut it square"
    "Durnholde Keep": "keep",                            # curtain wall and a dead keep

    # --- timber deck over open sky ------------------------------------------------------------
    "Zeppelin Tower": "sky",
    "Undercity Zeppelin Tower": "sky",
    "Grom'gol Zeppelin Tower": "sky",            # its Stranglethorn twin, missed when the pair was set

    # --- fel corruption is not a magma cave -----------------------------------------------------
    # Kyle, 2026-10-31: "grom's rest is a fel dungeon and it just has standard RFC background."
    # Exactly right, and the cause was structural rather than a typo: Grom's Rest is built on the
    # cave_warm biome, cave_warm routes to fire_dungeon, and fire_dungeon is the Ragefire pack. For
    # a Burning Blade magma cave that mapping is correct; for a demon-corrupted forest dungeon it
    # is the wrong colour entirely. blighted is the purple-and-fel-green corruption set.
    "Grom's Rest": "blighted",

    # --- built, not dug -------------------------------------------------------------------------
    # Ambermill is a mage tower with a library and a lab in it - "THE STACKED OCTAGONS", dressed
    # stone floor by floor. It was on cave_warm too, so it was fighting in Ragefire's magma as well.
    "Ambermill Tower": "keep",
    # Kael's Bastion is the Codex's index-town: "every line of it was decided in advance". A built
    # place of galleries and dressed stone, not the green field mossy_forest gave it.
    "Kael's Bastion": "keep",

    # --- height is the whole point --------------------------------------------------------------
    # Freewind Post's own builder says the job is "SELLING HEIGHT" in "the 'high in the air' style
    # that you did with the zepplin towers" - so it belongs in the same pack they use, not in a
    # forest it sits a thousand feet above.
    "Freewind Post": "sky",

    # --- salt, and a desert port ----------------------------------------------------------------
    "Saltwheel": "salt_flat",                    # a town ON the salt pan; it had a green forest
    "Steamwheedle Port": "desert",               # the Tanaris town that won; it had a green forest
})


def get_background_for_place(place_name, biome_id):
    """-> (folder, variant_or_None) for a named zone/cave, falling back to its biome.

    The override wins because it is about this specific place, while the biome is about the
    palette of a whole family of places.
    """
    entry = ZONE_BACKGROUND.get(place_name)
    if isinstance(entry, tuple):
        return entry[0], entry[1]
    if entry:
        return entry, None
    return get_background_folder(biome_id), None


def get_background_folder(biome_id):
    """Biome tag -> background folder name. Always returns something valid
    (falls back to mossy_forest, the least visually-specific pack, for any
    biome tag this table hasn't seen yet - new zones/biomes shouldn't have
    to touch this file just to get *a* background)."""
    return BIOME_TO_BACKGROUND.get(biome_id, "mossy_forest")


def get_variant_options(folder_name):
    """Return the sub-variant folder names for a background folder, or None
    if that folder is flat (no sub-variants)."""
    return VARIANT_FOLDERS.get(folder_name)


def resolve_place(zone_name, subzone_name=None, is_cave=False):
    """-> (folder, variant_or_None, biome) for wherever a fight is happening.

    THE ONE PLACE this decision is made. It used to live inline in
    ui/combat_background_loader.py, which meant qa_combat_combat_backgrounds
    could only approximate it - and an audit that approximates the thing it
    is auditing reports bugs that are its own. Precedence, most specific
    first: a ZONE_BACKGROUND override on the subzone, the subzone's own
    SUBZONE_BIOME entry, an override on the parent zone, the parent's biome.
    """
    from world.tile_textures import get_biome_for_zone, get_subzone_biome_by_name

    own = get_subzone_biome_by_name(subzone_name)
    biome = own or get_biome_for_zone(zone_name, is_cave=is_cave)
    if subzone_name and subzone_name in ZONE_BACKGROUND:
        folder, variant = get_background_for_place(subzone_name, biome)
        return folder, variant, biome
    if own:
        return get_background_folder(own), None, biome
    folder, variant = get_background_for_place(zone_name, biome)
    return folder, variant, biome
