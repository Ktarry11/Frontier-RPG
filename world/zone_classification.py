"""
Canonical zone classification - which zones are real Dungeons.

WHY THIS FILE EXISTS
---------------------
"Is this zone a Dungeon?" turned out to be a real, recurring question
that the zone generation code doesn't answer cleanly on its own -
`is_cave` is True for both plain mining caves (The Den, Dustwind Cave)
AND full lore-built dungeons (Wailing Caverns, Shadowfang Keep) alike,
and code comments guessing at the distinction have been wrong before
(zone_generator.py's own comment implied Sunken Grotto of the Deep was
"not a dungeon carver" zone, similar to Drygulch Ravine - Kyle corrected
this directly: Sunken Grotto of the Deep IS a Dungeon, Drygulch Ravine is
NOT). Rather than re-deriving this by inference again the next time a
feature needs it (loot tables, difficulty scaling, fast-travel rules,
gathering-node eligibility, ...), it's recorded here once, confirmed
directly by Kyle, 2026-09-12.

WHAT COUNTS AS A DUNGEON
--------------------------
A lore-built, boss-populated instance with a real encounter table -
distinct from a plain mining/monster cave (cave_specs in
zone_generator.py - The Den, Skull Rock, Tiragarde Keep, Boulder Lode
Mine, etc.) and distinct from open-air non-dungeon zones like Drygulch
Ravine (a canyon, explicitly NOT run through the dungeon carver per its
own generator docstring).

Gathering nodes (see gathering_manager.py's CAVE_TO_PARENT_ZONE / ore
density logic) deliberately never spawn in any zone on this list -
Kyle: "caves (and keeps) are fine, just not dungeons."
"""

#: The complete, Kyle-confirmed list of real Dungeons in Frontier RPG.
#: Update this list directly if a new dungeon is added - don't infer
#: dungeon status from is_cave, zone name patterns, or generator
#: function names elsewhere in the codebase; ask/confirm and add it here.
DUNGEONS = [
    "Ragefire Chasm",
    "Plague Depths",
    "Blackfathom Deeps",
    "Grom's Rest",
    "Widow's Lair",
    "Shadowfang Keep",
    "Ambermill Tower",
    "Shadowpine Altar",
    # Added 2026-10-27 with the Hillsbrad cluster. A lore-built, boss-populated keep, so no ore in it -
    # Azurelode Mine next door is deliberately NOT on this list, because a mine should have ore.
    "Durnholde Keep",
    "Wailing Caverns",
    "Razorfen Kraul",
    "The Broodspiral",
    "Sunken Grotto of the Deep",
    # Added 2026-10-27 with the Crystalline Underdark cluster. The Hollow Geode next door is deliberately NOT
    # on this list - it is a cave, so it keeps the Underdark's ore and herbs. The Deep Bloom is a grown thing
    # with fixed packs and nothing in it worth gathering.
    "The Deep Bloom",
    # Added 2026-10-29 with Stranglethorn. The arena is a five-boss gauntlet, so no gathering in it.
    # Rotvine Hollow, Veilfall Cave and The Drowned Shrine are deliberately NOT on this list - they are
    # caves, so they keep their ore and herbs.
    "Gurbashi Arena",
    # Added 2026-10-30 with Glittervein. Both halves of the cenote dungeon: fixed packs, seven
    # hand-placed bosses and nothing in them worth gathering. The Drownbell next door is
    # deliberately NOT on this list - it is a cave, so it keeps Northern Tanaris's ore.
    #
    # A SEAM FULL OF CRYSTAL IS THE OBVIOUS PLACE TO WANT ORE, and it still gets none: the player
    # mines the seams on the WALL of the cenote, in the open zone, which is where vein_field puts
    # them and where the node pool is. Putting ore down here too would make the dungeon a farm.
    "The Mother Vein",
    "The Cistern",
    # Added 2026-10-30 with the Southsea cove. Nine hulls lashed together with five hand-placed
    # bosses on them. The Drownbell next door is deliberately NOT on this list - it is a cave, so
    # it keeps Northern Tanaris's ore, and a fleet of rotting decks has nothing to mine anyway.
    "The Lashings",
    # Added 2026-11-15, found by the Felwood audit: these were built as dungeons (fixed packs, hand-placed
    # bosses, a T0 token or a trash-pack table) and never listed, so they could grow ore, never fired the
    # dungeon-clear banter, and counted a wipe at their door as an open-world one.
    "Jaedenar",                         # Felwood: eight bosses, the T0 hands
    "Khaz Varun, the Black Hollow",     # Tempest Isle: the T0 bracers and belt
    "The Emberdeep",                    # Tempest Isle: the T0 legs
    "The Royal Hive",                   # Tanaris: the T0 shoulders
    "Stromgarde Keep",                  # Arathi: in data/dungeons/trash_packs.json
    # Added 2026-11-16: the Scarlet Monastery's four wings, each its own dungeon. The grounds are not one.
    "Scarlet Monastery: Graveyard",
    "Scarlet Monastery: Library",
    "Scarlet Monastery: Armory",
    "Scarlet Monastery: Cathedral",
    # Added 2026-11-16: the Plaguelands' dungeons (tools/build_plaguelands_dungeons_content.py)
    "Scholomance", "Scholomance: Lower Halls",
    "Stratholme", "Stratholme: Service Entrance", "Stratholme: Slaughter Square",
    "Hearthglen", "Hearthglen: Mardenholde Keep",
    # Added 2026-11-18: Azshara's first dungeon, under Timbermaw Hold (tools/build_rotroot_deeps_content.py)
    "The Rotroot Deeps",
    "The Drowned Palace", "The Drowned Palace: The Queen's Vault",   # Azshara's last (tools/build_drowned_palace_content.py)
    "The Exclusion Zone", "The Exclusion Zone: The Reactor Hall", "The Exclusion Zone: The Foot",   # Deadwind's,
                                     # under the wheel, three floors: the last T0 token (tools/handbuilt_exclusion_zone.py)
]
# Drywhisker Deeps has fixed packs too, but it's the kobolds' MINE with its own ore pool, so like Azurelode
# Mine it stays off this list and keeps its ore.


def is_dungeon(zone_name):
    """True if zone_name is a real Dungeon (see DUNGEONS above), False
    for everything else - plain caves, canyons, overworld zones, towns.
    Case-sensitive exact match against the canonical list on purpose:
    zone names elsewhere in this codebase are always used as exact
    display strings (see ZoneManager.transition_to_zone, cave_specs,
    node_pools.json's zone keys which normalize separately for lookup
    purposes only) - silently fuzzy-matching here would risk a typo'd
    zone name quietly resolving to "not a dungeon" instead of failing
    loudly.

    The hidden levels under dungeons (world/hidden_zones.py, kind "layer") are dungeons too; they
    are listed in data/world/hidden_zones.json rather than here so this file doesn't name them."""
    if zone_name in DUNGEONS:
        return True
    from world.hidden_zones import kind, registry
    if kind(zone_name) == "layer":
        return True
    info = registry().get(zone_name) or {}
    return info.get("kind") == "frontier" and info.get("frontier_type", "deep") == "deep"
