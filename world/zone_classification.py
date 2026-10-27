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
]


def is_dungeon(zone_name):
    """True if zone_name is a real Dungeon (see DUNGEONS above), False
    for everything else - plain caves, canyons, overworld zones, towns.
    Case-sensitive exact match against the canonical list on purpose:
    zone names elsewhere in this codebase are always used as exact
    display strings (see ZoneManager.transition_to_zone, cave_specs,
    node_pools.json's zone keys which normalize separately for lookup
    purposes only) - silently fuzzy-matching here would risk a typo'd
    zone name quietly resolving to "not a dungeon" instead of failing
    loudly."""
    return zone_name in DUNGEONS
