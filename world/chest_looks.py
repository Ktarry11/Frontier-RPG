"""Which chest sprite a chest tile wears (assets/tiles/chests/ch_<name>.png).

Rows of the art sheet: plain open-world boxes, regional open-world chests, better dungeon chests, boss-reward chests.
The look is a pure function of (zone, tile position, boss?) so it never needs saving and never flickers."""
import os

#: Sheet CH1 (22 Nov 2026, docs/chest_art_prompts.md) redrew the everyday four; the old burlap crate retired with it.
PLAIN = ["plain_box", "rope_crate", "iron_banded", "travel_trunk"]

# zone key -> regional look (used for roughly half the open-world chests there; the rest are plain)
REGIONAL = {
    "valley_of_trials": "orc_hide", "durotar": "orc_hide", "orgrimmar": "orc_hide", "razor_hill": "orc_hide",
    "splintertree_post": "orc_hide", "zeppelin_tower": "orc_hide", "undercity_zeppelin_tower": "undead_rusted",
    "echo_isles": "troll_tiki",
    "central_barrens": "savannah", "northern_barrens": "savannah", "southern_barrens": "savannah", "camp_taurajo": "savannah",
    "crossroads": "savannah",
    "ratchet": "goblin_lockbox",
    "ashenvale_west": "moonwood", "ashenvale_east": "moonwood", "astranaar": "moonwood",
    "south_felwood": "moonwood", "emerald_sanctuary": "moonwood", "north_felwood": "chained_cursed",
    "zoram_strand": "sea_chest", "fenris_isle": "sea_chest",
    "deathknell": "undead_rusted", "western_tirisfal": "undead_rusted", "eastern_tirisfal": "undead_rusted",
    "brill": "undead_rusted", "undercity": "undead_rusted", "the_sepulcher": "undead_rusted", "sepulcher": "undead_rusted",
    "silverpine_north": "undead_rusted", "silverpine_south": "undead_rusted",
    "eastern_hillsbrad": "undead_rusted", "western_hillsbrad": "undead_rusted",
    "western_plaguelands_south": "chained_cursed",       # the Plaguelands (docs/plaguelands_design.md)
    "western_plaguelands_north": "chained_cursed", "eastern_plaguelands_west": "chained_cursed",
    "eastern_plaguelands_east": "chained_cursed",
    # sheet CH1's new regional chests (22 Nov 2026): the desert's sandstone, Feralas' and Stonetalon's living wood
    "northern_tanaris": "sandstone_coffer", "steamwheedle_port": "goblin_lockbox", "the_abyssal_sands": "sandstone_coffer",
    "fourth_peg": "sandstone_coffer", "glittervein": "sandstone_coffer", "the_shimmering_flats": "sandstone_coffer",
    "saltwheel": "goblin_lockbox", "southern_thousand_needles": "savannah", "freewind_post": "savannah",
    "the_forgotten_coast": "wildwood", "the_high_wilderness": "wildwood", "the_twin_colossals": "wildwood",
    "camp_mojache": "wildwood", "feathermoon_stronghold": "moonwood", "stonetalon_west": "wildwood",
    "stonetalon_east": "wildwood", "sun_rock_retreat": "savannah", "the_aspen_wilderness": "wildwood",
    # sheet CH2 (22 Nov 2026): the Eastern Kingdoms' regions and the lands that had no chest of their own
    "central_stranglethorn": "vine_bound", "northern_stranglethorn": "vine_bound", "southern_stranglethorn":
    "vine_bound", "gromgol": "vine_bound", "gurbashi_arena": "vine_bound",
    "arathi_central": "highland", "arathi_east": "highland", "arathi_west": "highland", "hammerfall": "highland",
    "saltspur_landing": "highland",
    "onyxhollow": "dark_iron",
    "amberleaf_glade": "elven_gilded", "duskfall_woods": "elven_gilded", "dawnrest": "elven_gilded",
    "firstlight_spire": "elven_gilded",
    "west_azshara": "highborne_ruin", "central_azshara": "highborne_ruin", "east_azshara": "highborne_ruin",
    "talrendis_landing": "highborne_ruin",
    "rootwater_isle": "bark_hollow", "the_lower_boughs": "bark_hollow", "mossroof": "bark_hollow",
    "the_great_settlement": "bark_hollow", "the_middle_boughs": "bark_hollow", "heartwatch": "bark_hollow",
    "the_upper_boughs": "bark_hollow", "highrest": "bark_hollow", "the_cloudbreak": "bark_hollow", "spearhold":
    "bark_hollow",
    "the_sunward_crown": "aetherian_coffer", "lenswatch": "aetherian_coffer", "the_celestial_expanse":
    "aetherian_coffer", "halcyon_rest": "aetherian_coffer", "the_anchorfields": "aetherian_coffer", "keelstone":
    "aetherian_coffer", "the_ascendant_bastions": "aetherian_coffer", "dawnspear_wreck": "aetherian_coffer",
    "the_fading_firmament": "aetherian_coffer", "lastlight": "aetherian_coffer", "aurelion": "aetherian_coffer",
    "the_crystalline_underdark": "geode", "kaels_bastion": "geode", "the_deep_bloom": "geode",
    "the_frostward_descent": "geode", "the_hollow_geode": "geode",
    "tempest_shallows": "storm_driftwood", "cinderwharf": "storm_driftwood", "the_ashen_reach": "storm_driftwood",
    "deadwind_west": "grave_ward", "deadwind_east": "grave_ward", "aridens_watch": "grave_ward",
}

# dungeon key -> (side-room looks, boss-reward look)
DUNGEONS = {
    "grom's_rest": (["chained_cursed", "steel_strongbox"], "fel_forged"),
    "groms_rest": (["chained_cursed", "steel_strongbox"], "fel_forged"),
    "howling_barrows": (["stone_coffer", "chained_cursed"], "frost_rimed"),
    "moonwell_hollow": (["moonwood", "stone_coffer"], "crystal_reliquary"),
    "blackfathom_deeps": (["sunken_coral", "stone_coffer"], "ornate_gold"),
    "sunken_grotto_of_the_deep": (["sunken_coral"], "ornate_gold"),
    "sunken_temple_grotto": (["sunken_coral", "stone_coffer"], "ornate_gold"),
    "scarlet_crypt": (["chained_cursed", "dark_oak"], "ossuary"),
    "night_webs_hollow": (["undead_rusted", "chained_cursed"], "ossuary"),
    "scourge_cave": (["chained_cursed", "undead_rusted"], "ossuary"),
    "burning_blade_coven": (["steel_strongbox", "dark_oak"], "void_obsidian"),
    "jaedenar": (["chained_cursed", "steel_strongbox"], "void_obsidian"),
    "wailing_caverns": (["stone_coffer", "dark_oak"], "royal_gold"),
    "razorfen_kraul": (["dark_oak", "steel_strongbox"], "royal_gold"),
    "the_broodspiral": (["stone_coffer", "dark_oak"], "royal_gold"),
    # the Scarlet Monastery's wings (tools/handbuilt_scarlet_monastery.py)
    "scarlet_monastery:_graveyard": (["chained_cursed", "stone_coffer"], "ossuary"),
    "scarlet_monastery:_library": (["dark_oak", "steel_strongbox"], "royal_gold"),
    "scarlet_monastery:_armory": (["steel_strongbox", "iron_banded"], "royal_gold"),
    "scarlet_monastery:_cathedral": (["dark_oak", "steel_strongbox"], "ornate_gold"),
    # the Plaguelands' dungeons
    "scholomance": (["chained_cursed", "stone_coffer"], "ossuary"),
    "scholomance:_lower_halls": (["chained_cursed", "stone_coffer"], "ossuary"),
    "stratholme": (["steel_strongbox", "dark_oak"], "royal_gold"),
    "stratholme:_service_entrance": (["chained_cursed", "undead_rusted"], "ossuary"),
    "stratholme:_slaughter_square": (["undead_rusted", "chained_cursed"], "ossuary"),
    "hearthglen": (["dark_oak", "steel_strongbox"], "royal_gold"),
    "hearthglen:_mardenholde_keep": (["steel_strongbox", "iron_banded"], "ornate_gold"),
}
DUNGEON_DEFAULT = (["dark_oak", "steel_strongbox", "dark_oak", "ornate_gold"], "royal_gold")


def zone_key(name):
    return str(name).lower().replace(" ", "_").replace("'", "")


def _pick(options, x, y):
    return options[(x * 73856093 ^ y * 19349663) % len(options)]


def chest_look(zone_name, x, y, is_boss=False, is_cave=False):
    key = zone_key(zone_name)
    if is_cave or key in DUNGEONS:
        side, boss = DUNGEONS.get(key, DUNGEON_DEFAULT)
        return boss if is_boss else _pick(side, x, y)
    regional = REGIONAL.get(key)
    if regional and (x * 31 + y * 17) % 2 == 0:
        return regional
    return _pick(PLAIN, x, y)


_sprite_cache = {}


def chest_sprite(look, tile_size):
    """Scaled pygame Surface for a look (about 1.15 tiles wide), or None if the file is missing."""
    import pygame
    k = (look, tile_size)
    if k not in _sprite_cache:
        path = f"assets/tiles/chests/ch_{look}.png"
        surf = None
        if os.path.isfile(path):
            try:
                img = pygame.image.load(path)
                img = img.convert_alpha() if pygame.display.get_surface() is not None else img
                w = int(tile_size * 1.15)
                surf = pygame.transform.smoothscale(img, (w, round(img.get_height() * w / img.get_width())))
            except pygame.error:
                surf = None
        _sprite_cache[k] = surf
    return _sprite_cache[k]


def is_boss_chest(tilemap, x, y, radius=8):
    """Same rule ZoneManager._is_boss_chest uses (close to the zone's boss position), extended to multi-boss maps."""
    spots = []
    bp = getattr(tilemap, "boss_position", None)
    if bp:
        spots.append(bp)
    spots.extend(getattr(tilemap, "boss_positions", None) or [])
    return any((x - bx) ** 2 + (y - by) ** 2 <= radius * radius for bx, by in (s[:2] for s in spots))
