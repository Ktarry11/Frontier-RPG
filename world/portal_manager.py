"""
Portal connection registry. Maps a specific portal tile (zone, x, y) to a
specific destination (zone, spawn_x, spawn_y), so stepping on a portal takes
you to a sensible spot in the destination zone rather than always dropping
you at that zone's center.

REBUILT FROM SCRATCH (post-Haiku-expansion cleanup)
====================================================
The previous version of this file had drifted badly from the actual tile
placements in the zone generators - registry entries pointed at coordinates
that didn't exist, whole zones (Camp Taurajo, Ashenvale, Silverpine, Fenris
Isle, Tirisfal Glades) had no path in from the reachable world at all, two
dungeons (Ragefire Chasm, Plague Depths) had no exit tile whatsoever, and
Python silently dropped half the Silverpine South / Fenris Isle entries
because the dict had each key defined TWICE (second definition wins).

Every (x, y) pair below was verified against the real, currently-generated
tile position by running create_all_zones() and scanning each tilemap's
interaction layer for "portal" tiles - not eyeballed from the generator
source. If a zone's generator changes a portal's position, this file must
be updated to match, or the portal will silently do nothing (get_destination
returns None and try_use_portal() fails safe rather than teleporting
somewhere undefined).

"Walkable" alone is not "correct". The old Drygulch Ravine (26,42) and Skull
Rock (27,44) arrival points were both technically walkable floor tiles - the
_find_nearest_walkable() safety net in zone_manager.py had nothing to fix -
but both sat in a cramped, disconnected pocket on the map's far west edge,
nowhere near the cave's actual entrance mouth (confirmed by ASCII-dumping
each tilemap's walkability grid). That reads to the player as "spawned in
the wrong place" even though no wall-clip occurred. Fixed by spawning one
tile off each cave's own exit portal instead (46,70 for Drygulch, 54,85 for
Skull Rock) - that's the real, generator-confirmed entrance chamber, not
just the nearest technically-open tile.

WORLD GEOGRAPHY (Kalimdor core, per Kyle's map)
================================================
Durotar (rectangular, N-S):
  Orgrimmar (N) - Zeppelin Tower + Skull Rock (NE) - Razor Hill (centre)
  - Valley of Trials (SW) - Echo Isles crossing (SE) - Sen'jin (S)
  - road west of Razor Hill, above the Valley spur, leads to Central Barrens

The Barrens (the dominant landmass - Northern/Central/Southern):
  Central Barrens: Crossroads (own zone, dead centre), oases NW/SW/SE
  (Wailing Caverns sits in the SW oasis), NE road up to Durotar, SE to
  Ratchet, N to Northern Barrens, S to Camp Taurajo.
  Camp Taurajo sits between Central and Southern Barrens.
  Northern Barrens continues north to Ashenvale East (Splintertree Post).
  Southern Barrens holds Bael Modan, Field of Giants, Razorfen Kraul - only
  reachable via Camp Taurajo, not directly from Central Barrens.

Ashenvale (West/East) - Silverpine (North/South) - Fenris Isle chain:
  Ashenvale East <-> Ashenvale West <-> (coast: Zoram Strand, Blackfathom
  Deeps). Ashenvale West also connects north to Silverpine North -> South,
  and Silverpine South's Sepulcher has a boat to Fenris Isle.

DIRECTIONAL LINKS (One-way)
===========================
Links are ONE-WAY ONLY. Two zones that connect both directions get two
separate entries (one under each zone's key), which is more verbose but
never has the "both directions must always agree" ambiguity that a
symmetric-link system runs into with hub tiles.

The Zeppelin Towers are cross-shaped hubs (one beside Orgrimmar, one in Tirisfal). Each arm is its own gate with
one static, correct destination, so no origin-tracking logic is needed: the stair arm leads to the ground and the
north berth leads to the other tower. East/west berths are reserved for future routes.
"""


class PortalManager:
    """Registry of portal tile positions and their destinations (ONE-WAY ONLY)."""

    def __init__(self):
        # One-way directional links only.
        # Format: zone_name -> {(x, y): (dest_zone, dest_x, dest_y)}
        self._links = {
            # ===== VALLEY OF TRIALS (starter zone) =====
            "Valley of Trials": {
                (115, 60): ("Durotar", 28, 150),
                (40, 30): ("The Den", 42, 66),
                (95, 22): ("Burning Blade Coven", 50, 81),
            },
            "The Den": {
                (42, 66): ("Valley of Trials", 40, 30),
            },
            "Burning Blade Coven": {
                (50, 81): ("Valley of Trials", 95, 22),
            },

            # ===== DUROTAR (core hub zone) =====
            "Durotar": {
                # Was (100,192) - that's actually the Zeppelin Tower
                # platform's own portal tile inside Orgrimmar's walls, 4
                # rows north of the real south gate. Walking in from
                # Durotar skipped the gate entirely and dropped the
                # player onto the zeppelin platform (Kyle: "gets the
                # player stuck arriving INSIDE the Org gates"). Repointed
                # at the new dedicated arrival tile just inside the real
                # gate opening - see orgrimmar_undercity_expansion.py's
                # South Gate section.
                (65, 26): ("Orgrimmar", 100, 197),
                (95, 25): ("Drygulch Ravine", 47, 71),
                (112, 35): ("Zeppelin Tower", 32, 57),
                (118, 60): ("Skull Rock", 55, 86),
                (120, 40): ("Sunken Grotto of the Deep", 55, 92),
                (5, 85): ("Central Barrens", 270, 30),
                (65, 108): ("Razor Hill", 30, 55),
                (40, 130): ("Dustwind Cave", 40, 61),
                (28, 150): ("Valley of Trials", 115, 60),
                (110, 150): ("Echo Isles", 80, 8),
                (95, 178): ("Tiragarde Keep", 45, 76),
                (55, 45): ("Thunder Ridge", 45, 86),
            },
            "Razor Hill": {
                (30, 55): ("Durotar", 65, 108),
            },
            "Drygulch Ravine": {
                (47, 71): ("Durotar", 95, 25),
            },
            "Skull Rock": {
                (55, 86): ("Durotar", 118, 60),
            },
            "Thunder Ridge": {
                (45, 86): ("Durotar", 55, 45),
            },
            "Sunken Grotto of the Deep": {
                (55, 92): ("Durotar", 120, 40),
            },
            "Dustwind Cave": {
                (40, 61): ("Durotar", 40, 130),
            },
            "Tiragarde Keep": {
                (45, 76): ("Durotar", 95, 178),
            },
            "Echo Isles": {
                (80, 8): ("Durotar", 110, 150),
                # South dock used to point at the exact same Durotar
                # coordinates as the north dock - two separate landings on
                # the island both dumping you in the identical spot, which
                # is why it felt wrong ("goes back to Durotar" with no
                # distinction). Durotar only has ONE tile that actually
                # leads to Echo Isles (110,150), so rather than inventing a
                # brand new portal tile on Durotar's map, the south dock now
                # arrives at the existing "Scuttle Coast" clearing (105,150)
                # a few tiles south - a real, already-named part of
                # Durotar's SE coast, giving it a genuinely distinct
                # landing instead of a duplicate.
                #
                # All 4 of this zone's own coordinates below rescaled from
                # a 100x100 map to 160x160 (Kyle: "yes, resize bigger...
                # for real breathing room between islands" during this
                # session's full rebuild) - same proportional scale
                # (x1.6) applied to every one, not eyeballed individually.
                (80, 152): ("Durotar", 105, 150),
                (24, 98): ("Sunken Temple Grotto", 60, 92),
                (141, 117): ("Zalazane's Hollow", 14, 74),
            },
            "Sunken Temple Grotto": {
                (60, 92): ("Echo Isles", 24, 98),
            },
            "Zalazane's Hollow": {
                (14, 74): ("Echo Isles", 141, 117),
            },

            # ===== ORGRIMMAR / ZEPPELIN =====
            "Orgrimmar": {
                # Real south gate arrival/exit tile (added this session -
                # see Durotar's own (65,26) entry above for the full
                # story). Replaces the old (100,192) "Zeppelin" tile,
                # which was a mislabeled duplicate exit 4 rows further
                # north with no real distinct destination of its own.
                (100, 197): ("Durotar", 65, 26),
                # Ragefire Chasm: lava-mouth in the south wall of the Cleft of
                # Shadow (tools/handbuilt_orgrimmar.RAGEFIRE).  Arrival is 2
                # tiles north of the registered tile, on the Cleft's main street.
                (34, 184): ("Ragefire Chasm", 120, 214),
            },
            "Ragefire Chasm": {
                (120, 214): ("Orgrimmar", 34, 184),
            },
            # Zeppelin Tower = a 4-arm cross (tools/handbuilt_zeppelin_tower.py). S arm = the stair down to the
            # ground, N arm = airship berth to the twin tower. E (58,32) and W (6,32) berths are reserved for
            # future routes (Grom'gol, Thunder Bluff) - add their links here when those zones exist.
            # Destinations below are written 2 tiles SOUTH of where you land (the transition lands 2 tiles north).
            "Zeppelin Tower": {
                (32, 58): ("Durotar", 112, 35),
                (32, 6): ("Undercity Zeppelin Tower", 32, 11),
            },
            "Undercity Zeppelin Tower": {
                (32, 58): ("Eastern Tirisfal", 21, 97),
                (32, 6): ("Zeppelin Tower", 32, 11),
            },

            # ===== THE BARRENS =====
            "Central Barrens": {
                (150, 4): ("Northern Barrens", 150, 256),
                (270, 30): ("Durotar", 5, 85),
                (150, 150): ("Crossroads", 35, 65),
                (75, 223): ("Wailing Caverns", 120, 210),
                (285, 270): ("Ratchet", 2, 30),
                (150, 296): ("Camp Taurajo", 32, 2),
            },
            "Crossroads": {
                (35, 65): ("Central Barrens", 150, 150),
            },
            "Wailing Caverns": {
                (120, 210): ("Central Barrens", 75, 223),
            },
            "Ratchet": {
                (2, 30): ("Central Barrens", 285, 270),
            },
            "Camp Taurajo": {
                (32, 2): ("Central Barrens", 150, 296),
                (32, 53): ("Southern Barrens", 130, 2),
            },
            "Northern Barrens": {
                (150, 256): ("Central Barrens", 150, 4),
                (150, 4): ("Ashenvale East", 110, 195),
                (255, 45): ("Boulder Lode Mine", 50, 76),
                (60, 150): ("Serena's Hollow", 30, 48),
            },
            "Boulder Lode Mine": {
                (50, 76): ("Northern Barrens", 255, 45),
            },
            "Serena's Hollow": {
                (30, 48): ("Northern Barrens", 60, 150),
            },
            "Southern Barrens": {
                (130, 2): ("Camp Taurajo", 32, 53),
                (55, 175): ("Razorfen Kraul", 120, 208),
                (225, 220): ("The Broodspiral", 152, 220),
            },
            "The Broodspiral": {
                (152, 220): ("Southern Barrens", 225, 220),
            },
            "Razorfen Kraul": {
                (120, 208): ("Southern Barrens", 55, 175),
            },

            # ===== ASHENVALE / SILVERPINE / FENRIS ISLE CHAIN =====
            "Ashenvale East": {
                (4, 100): ("Ashenvale West", 215, 100),
                (165, 175): ("Grom's Rest", 120, 205),
                (110, 195): ("Northern Barrens", 150, 4),
                (200, 40): ("Howling Barrows", 47, 76),
                (110, 160): ("Splintertree Post", 45, 66),
            },
            "Splintertree Post": {
                (45, 66): ("Ashenvale East", 110, 160),
            },
            "Howling Barrows": {
                (47, 76): ("Ashenvale East", 200, 40),
            },
            "Grom's Rest": {
                (120, 205): ("Ashenvale East", 165, 175),
            },
            "Ashenvale West": {
                (215, 100): ("Ashenvale East", 4, 100),
                (30, 20): ("Blackfathom Deeps", 120, 205),
                (110, 82): ("Moonwell Hollow", 42, 66),
                (110, 160): ("Astranaar", 55, 85),
                (15, 30): ("Zoram Strand", 50, 25),
            },
            "Astranaar": {
                (55, 85): ("Ashenvale West", 110, 160),
            },
            "Zoram Strand": {
                (50, 25): ("Ashenvale West", 15, 30),
            },
            "Moonwell Hollow": {
                (42, 66): ("Ashenvale West", 110, 82),
            },
            "Blackfathom Deeps": {
                (120, 205): ("Ashenvale West", 30, 20),
            },
            "Silverpine North": {
                (100, 4): ("Eastern Tirisfal", 16, 132),
                (100, 185): ("Silverpine South", 100, 10),
                (170, 100): ("Widow's Lair", 70, 108),
            },
            "Widow's Lair": {
                (70, 108): ("Silverpine North", 170, 98),
            },
            "Silverpine South": {
                (100, 10): ("Silverpine North", 100, 185),
                (160, 80): ("Ambermill Tower", 75, 128),
                (100, 155): ("Shadowfang Keep", 85, 152),
                (182, 138): ("Fenris Isle", 80, 125),  # boat, east coast dock
                (45, 90): ("The Sepulcher", 35, 55),
            },
            "The Sepulcher": {
                (35, 55): ("Silverpine South", 45, 90),
            },
            "Ambermill Tower": {
                (75, 128): ("Silverpine South", 160, 78),
            },
            "Shadowfang Keep": {
                # Was pointing back to Silverpine North's portal (100,10)
                # instead of the actual Sepulcher-side entrance you walked
                # in from (100,155) - so leaving the dungeon dumped you
                # clear across the map instead of back at the door.
                (85, 152): ("Silverpine South", 100, 155),
            },
            "Fenris Isle": {
                (25, 60): ("Shadowpine Altar", 75, 115),
                (80, 125): ("Silverpine South", 182, 136),  # boat return
            },
            "Shadowpine Altar": {
                (75, 115): ("Fenris Isle", 25, 58),
            },

            # ===== TIRISFAL / UNDERCITY =====
            "Deathknell": {
                # Hand-built valley (tools/handbuilt_deathknell.py): NW goldmine cave, NE Scarlet crypt, east pass out.
                (17, 21): ("Night Web's Hollow", 45, 71),
                (83, 19): ("Scarlet Crypt", 47, 76),
                # Per the real Tirisfal Glades map: Deathknell sits SW of
                # the region, Brill sits central/east near Undercity. This
                # zone's "Western Tirisfal" is the one that actually has
                # Brill on it, so Deathknell - being further southwest -
                # should connect through THIS zone, not Eastern Tirisfal.
                (96, 47): ("Western Tirisfal", 64, 106),
            },
            "Night Web's Hollow": {
                (45, 71): ("Deathknell", 17, 21),
            },
            "Scarlet Crypt": {
                (47, 76): ("Deathknell", 83, 19),
            },
            # Hand-built on the real Tirisfal map (tools/handbuilt_{western,eastern}_tirisfal.py, handbuilt_brill.py):
            # Deathknell -> Western -> Brill's west gate; Brill's east gate -> Eastern; a bypass road joins Western and Eastern
            # north of town; Eastern holds the zeppelin landing, the Undercity gate, the Silverpine road and the Scourge Cave.
            "Eastern Tirisfal": {
                (4, 62): ("Western Tirisfal", 112, 62),
                (6, 86): ("Brill", 87, 44),
                (21, 97): ("Undercity Zeppelin Tower", 32, 57),
                (10, 112): ("Undercity", 100, 17),      # arrive (100,15) at the foot of the Long Descent
                (16, 136): ("Silverpine North", 100, 8),
                (52, 112): ("Scourge Cave", 45, 68),
            },
            "Scourge Cave": {
                (45, 68): ("Eastern Tirisfal", 52, 116),
            },
            "Western Tirisfal": {
                (60, 106): ("Deathknell", 94, 49),
                (113, 84): ("Brill", 9, 44),
                (116, 62): ("Eastern Tirisfal", 8, 62),
            },
            "Brill": {
                (5, 44): ("Western Tirisfal", 110, 88),
                (91, 44): ("Eastern Tirisfal", 10, 88),
            },
            "Undercity": {
                (100, 11): ("Eastern Tirisfal", 10, 108),     # the Ruins elevator (tools/handbuilt_undercity.py)
                (100, 185): ("Plague Depths", 120, 205),      # the Deeps Gate (arrive (120,203))
            },
            "Plague Depths": {
                (120, 205): ("Undercity", 100, 185),        # back up to the Deeps Gate (arrive (100,183))
            },
        }

        # Build fast lookup
        self._lookup = {}
        for zone, portals in self._links.items():
            for (x, y), (dest_zone, dest_x, dest_y) in portals.items():
                self._lookup[(zone, x, y)] = (dest_zone, *self._offset_spawn((dest_x, dest_y)))

    def _offset_spawn(self, pos):
        """Spawn just north of destination portal so player doesn't re-trigger it."""
        return (pos[0], max(0, pos[1] - 2))

    def get_destination(self, zone_name, x, y):
        """Look up portal destination. Returns (dest_zone, spawn_x, spawn_y) or None."""
        return self._lookup.get((zone_name, x, y))

    def get_portal_positions(self, zone_name):
        """Return all (x, y) portal positions in a zone."""
        positions = []
        for (z, x, y) in self._lookup.keys():
            if z == zone_name:
                positions.append((x, y))
        return positions
