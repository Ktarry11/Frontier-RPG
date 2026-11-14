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
            # ground, N arm = airship berth to the twin tower, E arm = the Stranglethorn run to Grom'gol (the
            # berth was reserved for exactly this). W (6,32) is still reserved (Thunder Bluff).
            # Destinations below are written 2 tiles SOUTH of where you land (the transition lands 2 tiles north).
            "Zeppelin Tower": {
                (32, 58): ("Durotar", 112, 35),
                (32, 6): ("Undercity Zeppelin Tower", 32, 11),
                (58, 32): ("Grom'gol Zeppelin Tower", 32, 11),
            },
            "Undercity Zeppelin Tower": {
                (32, 58): ("Eastern Tirisfal", 21, 97),
                (32, 6): ("Zeppelin Tower", 32, 11),
            },

            # ===== THE BARRENS =====
            "Central Barrens": {
                (150, 4): ("Northern Barrens", 150, 256),
                (270, 30): ("Durotar", 5, 86),   # portal is (5,85); arrival = 2 north of this = (5,84) on the road (2 north of the portal is a cliff)
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
                # The dock. (64,30) was a "boat" interaction tile with no registered link since Ratchet was
                # built - flavour only. It is the route south now: claude/integration_geography.md took the
                # land road to Stranglethorn away, so the goblins' shipping IS the road.
                (64, 30): ("Booty Bay", 62, 36),
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
                # South out of Kalimdor's twenties, onto the Barrens floor under the new range. (140, 236)
                # is the one gap in the south edge wide enough to stand in - rows 237+ are solid.
                (140, 236): ("The Aspen Wilderness", 105, 11),
            },

            # ===== NORTHERN THOUSAND NEEDLES =====
            # The Pass at (104, 173) is carved into the headwall but deliberately NOT registered here: it
            # fails safe as dead-end scenery until Southern Thousand Needles exists. Same pattern the Deep
            # Bloom used while the Underdark cluster was half-built.
            "The Aspen Wilderness": {
                (105, 5): ("Southern Barrens", 140, 233),
                (145, 48): ("The Weeping Ice", 48, 124),
                # The pass over the divide. Carved with the zone and left unregistered until there was
                # something on the far side; Southern Thousand Needles now exists.
                (104, 176): ("Southern Thousand Needles", 110, 12),
                (48, 35): ("Rocky Pass", 52, 186),           # the cleft up to the summit
                (204, 150): ("The Shimmering Flats", 6, 40),  # east, where the range bleeds out
            },

            # ===== SOUTHERN THOUSAND NEEDLES =====
            # (168, 88) sits on TOP of Freewind North, at the head of its ramp - the settlement is up
            # there, so the climb is the way in.
            "Southern Thousand Needles": {
                (110, 4): ("The Aspen Wilderness", 104, 172),
                (168, 88): ("Freewind Post", 96, 26),
                # A hole at the foot of Broadback that swallows a wash and gives nothing back. The zone's
                # WASHES are the channels the annual flood cuts on the surface; this is where it goes.
                (104, 112): ("The Drowning Floor", 66, 102),
                # The "flats" road, carved with the zone and left hanging at the map edge for
                # two zones until there was something on the far side of it.
                (214, 150): ("The Shimmering Flats", 6, 132),
            },
            "Freewind Post": {
                (96, 20): ("Southern Thousand Needles", 168, 92),
            },
            "The Weeping Ice": {
                (48, 126): ("The Aspen Wilderness", 145, 51),
            },
            "The Drowning Floor": {
                # Declared y 110: _offset_spawn takes 2 off and transition_to_zone adds 3 back for
                # leaving_cave, so the player lands on (104, 111) - one tile NORTH of the soak at
                # (104, 112), clear of Broadback's rim at y 116-118 and not standing on the portal.
                (66, 104): ("Southern Thousand Needles", 104, 110),
            },
            "The Broodspiral": {
                (152, 220): ("Southern Barrens", 225, 220),
            },
            "Razorfen Kraul": {
                (120, 208): ("Southern Barrens", 55, 175),
            },

            # ===== STRANGLETHORN =====
            # Reached ONLY by transport: the zeppelin into Grom'gol at the top, the Ratchet boat into Booty
            # Bay at the bottom. There is no land route in from anywhere - the north edge of Northern
            # Stranglethorn is the range itself. The three wilderness zones are one road end to end.
            # The tower is OUTSIDE the palisade now (Kyle, 29 Oct). Its N berth is the far end of the
            # Durotar run and its S arm is the stair down into the camp, which is the same shape the
            # Orgrimmar tower has had since it was built.
            "Grom'gol Zeppelin Tower": {
                (32, 6): ("Zeppelin Tower", 55, 34),            # the Durotar E berth: arrival (55,32)
                (32, 58): ("Grom'gol", 32, 8),                  # the stair down: arrival (32,6)
            },
            "Grom'gol": {
                (32, 4): ("Grom'gol Zeppelin Tower", 32, 57),   # up the stair: arrival (32,55)
                (32, 53): ("Northern Stranglethorn", 54, 96),
            },
            "Northern Stranglethorn": {
                (54, 96): ("Grom'gol", 32, 53),
                (150, 40): ("Rotvine Hollow", 32, 10),
                (100, 177): ("Central Stranglethorn", 100, 7),  # seam: land on (100,5), not on the portal
            },
            "Central Stranglethorn": {
                (100, 3): ("Northern Stranglethorn", 100, 177),
                (100, 177): ("Southern Stranglethorn", 100, 7),
                (40, 58): ("Veilfall Cave", 32, 10),
                (150, 100): ("Gurbashi Arena", 52, 12),
            },
            "Southern Stranglethorn": {
                (100, 3): ("Central Stranglethorn", 100, 177),
                (36, 150): ("Booty Bay", 35, 8),
                (170, 116): ("The Drowned Shrine", 32, 10),
            },
            # The caves and the gauntlet. A cave exit declares the OVERWORLD portal tile: _offset_spawn
            # takes 2 off and transition_to_zone adds 3 back for leaving_cave, so the player lands one
            # tile south of the mouth rather than on top of it.
            "Rotvine Hollow": {
                (32, 10): ("Northern Stranglethorn", 150, 40),
            },
            "Veilfall Cave": {
                (32, 10): ("Central Stranglethorn", 40, 58),
            },
            "Gurbashi Arena": {
                (52, 12): ("Central Stranglethorn", 150, 100),
            },
            "The Drowned Shrine": {
                (32, 10): ("Southern Stranglethorn", 170, 116),
            },
            "Booty Bay": {
                (35, 4): ("Southern Stranglethorn", 36, 150),
                # THE ASYMMETRY. Ratchet -> Booty Bay is still the direct boat (see "Ratchet"
                # above, unchanged). Booty Bay -> Ratchet is not: you arrive ON the boat,
                # mid-crossing, with two Bloodsail ships on you. Going south is travel; coming
                # north is an event, and a player who has only ever sailed one way never learns
                # this is here. tools/verify_return_voyage.py asserts BOTH directions, so a later
                # tidy-up cannot quietly make them symmetrical again.
                (64, 34): ("The Crossing", 98, 50),             # arrive aft, the way we came
            },

            # ===== THE SHIMMERING FLATS, and the hive under it =====
            # TWO MOUTHS INTO ONE CAVE, which nothing else in this game does. Kyle: "the cave will
            # have two entrances in the overworld and each entrance will take us to a different part
            # in the cave." The Crustfall drops you in the shallow galleries at the west end; the
            # Deep Shaft, most of the way across the pan under the oldest hive on the map, drops you
            # straight into the deep end. tools/handbuilt_undercrust.verify_two_mouths measures that
            # they really are opposite ends - 132 tiles apart by path - because it is exactly the
            # kind of property that quietly stops being true when a chamber moves.
            "The Shimmering Flats": {
                (6, 40): ("The Aspen Wilderness", 204, 150),
                (6, 132): ("Southern Thousand Needles", 214, 150),
                (92, 140): ("The Undercrust", 16, 66),      # the Crustfall, by Crustbreak
                (172, 113): ("The Undercrust", 104, 54),    # the Deep Shaft, under the Deep Mound
                (104, 56): ("Saltwheel", 16, 50),           # the Raceway spur, into the town
                (120, 176): ("Northern Tanaris", 92, 2),   # THE SOUTH PASS, down into Tanaris
            },
            # The goblin town, off the end of the Raceway spur road. One way in, one way out,
            # and no flight point at either end of it - see tools/sync_saltwheel_npcs.py.
            "Saltwheel": {
                (16, 50): ("The Shimmering Flats", 104, 56),
            },

            # ===== TANARIS. Three zones; this is the first, and the only one built. =====
            # Kyle drew the region: the top strip is the way in, the Abyssal Sands (44-47) are the
            # southwest and Glittervein (46-49) the southeast. The south pass out of this zone is
            # carved and walkable and NOT registered until the Sands exist - exactly what the Flats
            # did with the pass that now points here, for two zones before Tanaris was built.
            "Northern Tanaris": {
                (92, 2): ("The Shimmering Flats", 120, 176),
                (60, 108): ("The Abyssal Sands", 60, 2),   # the one way south, on the west
                (216, 56): ("Steamwheedle Port", 40, 58),
                (200, 88): ("The Drownbell", 16, 12),
                # THE SOUTHSEA COVE, up the coast from the port. Kyle asked for the Southsea's
                # proper home in Tanaris, as against the Drownbell, which is a small sea cave
                # under a headland with an entirely different crew in it.
                (222, 26): ("The Lashings", 68, 112),
            },
            "Steamwheedle Port": {
                (40, 58): ("Northern Tanaris", 216, 56),
            },
            "The Drownbell": {
                (16, 12): ("Northern Tanaris", 200, 88),
            },
            "The Lashings": {
                (68, 112): ("Northern Tanaris", 222, 26),
            },
            # Zone 2. Its SOUTH gate (toward Uldum) is still carved, walkable and deliberately
            # unregistered until that zone exists. The east gate now goes to Glittervein.
            "The Abyssal Sands": {
                (60, 2): ("Northern Tanaris", 60, 108),
                (176, 96): ("Glittervein", 6, 96),
                # SIX SINKHOLES, ONE UNDERGROUND. Kyle, 13 Nov 2026: "another underground layer
                # entered by each sinkhole that links up underground." Each pit's centre goes down
                # to the chamber under it, and each chamber's shaft comes back up the same pit.
                (44, 34): ("The Dry Deep", 26, 20),      # The First Hole
                (104, 48): ("The Dry Deep", 62, 29),      # Nineteen Mile Pit
                (62, 66): ("The Dry Deep", 37, 40),      # The Wide Sink
                (36, 92): ("The Dry Deep", 22, 55),      # The Throat
                (84, 112): ("The Dry Deep", 50, 67),      # The Long Collapse
                (148, 116): ("The Dry Deep", 89, 70),      # Underlight
            },
            "The Dry Deep": {
                (26, 20): ("The Abyssal Sands", 44, 34),      # up The First Hole
                (62, 29): ("The Abyssal Sands", 104, 48),      # up Nineteen Mile Pit
                (37, 40): ("The Abyssal Sands", 62, 66),      # up The Wide Sink
                (22, 55): ("The Abyssal Sands", 36, 92),      # up The Throat
                (50, 67): ("The Abyssal Sands", 84, 112),      # up The Long Collapse
                (89, 70): ("The Abyssal Sands", 148, 116),      # up Underlight
                # "at the end of the descent" (Kyle): the last room, and the stair in it
                (98, 40): ("The Black Strand", 20, 14),
            },
            # Under the Dry Deep, and the town behind its gate.
            "The Black Strand": {
                (20, 11): ("The Dry Deep", 95, 40),
                (84, 52): ("Onyxhollow", 50, 76),
                # the floor of the Royal Cell goes down into the hive the queen came from
                (138, 115): ("The Royal Hive", 70, 9),
            },
            "The Royal Hive": {
                (70, 6): ("The Black Strand", 138, 112),
            },
            "Onyxhollow": {
                (50, 80): ("The Black Strand", 84, 55),
            },
            # Zone 3, the cenote, and the end of the five-zone water chain. Three doors on the
            # surface map: the gate west back to the Sands, the dig mouth on the isle that is the
            # way INTO the dungeon, and THE OUTFLOW, which is the way out of the far end of it.
            #
            # The outflow is not a convenience. The water in the pool was pulled down to the
            # Cistern and pushed back up, and the channel it takes is the one the party walks out
            # through - so a group that fights from the dig head to the heart surfaces beside the
            # camp it started from. Kyle: "at the very end (after the last boss) brings you back
            # out to Lastwater."
            "Glittervein": {
                (6, 96): ("The Abyssal Sands", 176, 96),
                (86, 100): ("The Mother Vein", 60, 104),
                # NO WAY IN AT THE OUTFLOW. The Cistern's far door (60,7) surfaces here at
                # (82,101), and for a while this map linked straight back down it - so a
                # party could walk in at the END of the dungeon, past every boss. Kyle,
                # 10 Nov: "i didnt mean that you can ALSO enter at the END of the dungeon
                # ....the portal outside is one way." The exit is one-way: the Cistern keeps
                # its link out; there is no tile here that leads back.
            },
            "The Mother Vein": {
                (60, 104): ("Glittervein", 86, 100),
                (46, 10): ("The Cistern", 46, 122),
            },
            "The Cistern": {
                (46, 122): ("The Mother Vein", 46, 10),
                (60, 7): ("Glittervein", 82, 101),
            },
            "The Undercrust": {
                (16, 66): ("The Shimmering Flats", 92, 140),
                # Moved off (172,116): a cave exit lands ONE TILE SOUTH of the declared tile
                # (_offset_spawn takes 2, transition_to_zone adds 3 back), and the tile
                # south of the old mouth was the Deep Mound's own wall - so climbing out
                # of the Deep Shaft put the player inside rock. The arrival tile is the
                # one nothing writes down and the only reason this was caught is that the
                # check tests it rather than testing the portal tile.
                (104, 54): ("The Shimmering Flats", 172, 113),
            },

            # ===== ROCKY PASS - the summit of the range above the Aspen Wilderness =====
            # The cleft is in the Rim's WEST escarpment, deliberately the opposite end of the
            # range from the Weeping Ice: a zone's two ways into the mountain should not share a
            # hillside. (tools/handbuilt_rocky_pass.py)
            "Rocky Pass": {
                (52, 186): ("The Aspen Wilderness", 48, 35),
            },

            # ===== THE RETURN VOYAGE =====
            # The hub, and the two Bloodsail ships on it (tools/handbuilt_return_voyage.py,
            # handbuilt_bloodsail_raider.py, handbuilt_bloodsail_galleon.py).
            "The Crossing": {
                (24, 50): ("Ratchet", 62, 32),                  # forward, on to Ratchet
                (98, 50): ("Booty Bay", 64, 34),                # aft, back the way we came
                (58, 32): ("The Bloodsail Raider", 94, 35),     # the north plank
                (60, 80): ("The Bloodsail Anchorage", 54, 112), # off the sand bar
            },
            "The Bloodsail Raider": {
                (94, 35): ("The Crossing", 58, 32),
                (18, 35): ("The Raider's Hold", 18, 35),        # the bow hatch, down
            },
            "The Raider's Hold": {
                (18, 35): ("The Bloodsail Raider", 18, 35),     # back up the hatch
                # THE LAP CLOSES HERE. The cabin is under the quarterdeck you boarded over, so the
                # tile past the Captain comes out on our own deck - Kyle: "another portal right
                # after the last boss that returns us to our ship so we don't back pedal".
                (92, 35): ("The Crossing", 58, 32),
            },
            "The Bloodsail Anchorage": {
                (54, 112): ("The Crossing", 60, 80),
                (48, 30): ("The Galleon's Weather Deck", 52, 56),   # up the ramp, amidships
            },
            "The Galleon's Weather Deck": {
                (52, 56): ("The Bloodsail Anchorage", 48, 30),
                (24, 40): ("The Galleon's Hold", 24, 40),       # the forward hatch
            },
            "The Galleon's Hold": {
                (24, 40): ("The Galleon's Weather Deck", 24, 40),
                (110, 40): ("The Captain's Cabin", 30, 42),     # the cabin door, aft
            },
            "The Captain's Cabin": {
                (30, 42): ("The Galleon's Hold", 110, 40),
                (30, 12): ("The Crossing", 60, 80),             # the stern gallery, home
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
            # Hand-built Silverpine North (tools/handbuilt_silverpine_north.py): Tirisfal border at the top, the Sepulcher's gate on the
            # sea cliffs (west), the spider cave in the east wall, the trunk road out to Silverpine South at the bottom.
            "Silverpine North": {
                (80, 5): ("Eastern Tirisfal", 16, 134),            # arrive (16,132)
                (32, 98): ("The Sepulcher", 44, 65),               # arrive (44,63), inside the south gate
                (150, 84): ("Widow's Lair", 65, 106),               # arrive (65,104)
                (80, 156): ("Silverpine South", 80, 11),               # arrive (80,9)
            },
            "Widow's Lair": {
                (65, 106): ("Silverpine North", 150, 84),          # cave exit: +3 -> arrive (150,85), south of the mouth
            },
            "Silverpine South": {
                # Hand-built (tools/handbuilt_silverpine_south.py): the road in from North at the top, Shadowfang's portcullis under the
                # SW ridge, the Ambermill waygate in the east, the Decrepit Ferry pier into Lordamere.
                (80, 5): ("Silverpine North", 80, 154),            # arrive (80,152)
                (138, 90): ("Ambermill Tower", 75, 128),
                (48, 144): ("Shadowfang Keep", 100, 172),
                (151, 44): ("Fenris Isle", 80, 129),               # the ferry: arrive (80,127) on the pier
                # The south-east pass out of Lordaeron into Hillsbrad. Silverpine borders Hillsbrad's north-WEST, so
                # this lands in the WESTERN half (Kyle: "Players enter from the west bro").
                (138, 155): ("Western Hillsbrad", 40, 11),         # arrive (40,9), clear of the pass portal
            },

            # ===== HILLSBRAD (2 zones) - the first green country after the blight =====
            "Western Hillsbrad": {
                # Hand-built (tools/handbuilt_hillsbrad_west.py): the Silverpine pass at the top, Southpoint Tower just
                # down the road as the player's hub, and the east road on to Tarren Mill.
                (40, 5): ("Silverpine South", 138, 153),           # arrive (138,151), clear of the pass portal
                (155, 86): ("Eastern Hillsbrad", 8, 88),           # arrive (8,86), clear of the west gate
                (33, 60): ("Azurelode Mine", 55, 86),              # the mine mouth in the western rock
            },
            "Azurelode Mine": {
                (55, 86): ("Western Hillsbrad", 33, 63),           # cave exit: +3 -> arrive (33,61), south of the adit
            },
            # ===== ARATHI HIGHLANDS =====
            # Thoradin's Wall was built, dressed and SHUT in Eastern Hillsbrad long before there was
            # anything behind it - Ada Rook stands at the gap and has never seen the far side. This is
            # the far side. Every pair below is registered BOTH ways; portal_qa checks for that.
            "Arathi West": {
                (4, 118): ("Eastern Hillsbrad", 136, 150),   # back through the wall
                (176, 84): ("Arathi Central", 6, 86),
                (44, 34): ("Boulder'gor", 30, 46),           # the ogre hold on the moor
                (36, 140): ("Stromgarde Keep", 84, 144),     # the ruined archway, 31-34
            },
            "Arathi Central": {
                (4, 84): ("Arathi West", 174, 86),
                (186, 92): ("Arathi East", 6, 94),
                (38, 40): ("Boulderfist Hall", 32, 50),
                (170, 114): ("Drywhisker Deeps", 76, 154),   # the kobold mine, 37-40
                # The Hammerfall gate. The town used to BE this patch of moor; now it is
                # a door in it, which is the whole point of giving it its own zone.
                (138, 62): ("Hammerfall", 52, 85),
            },
            "Arathi East": {
                (4, 92): ("Arathi Central", 184, 94),
                (34, 38): ("The Drowned Barrow", 30, 52),
                (150, 60): ("Wrackline Hold", 28, 48),       # sea cave, under Gallowmast
                (160, 132): ("The Tidewrack", 34, 50),       # sea cave, the southern rocks
                # Saltspur became its own zone on 7 Nov; the beachhead is a door now.
                (50, 96): ("Saltspur Landing", 2, 28),
            },
            # Leaving a cave arrives at the destination tile +3, which is why each of these sits three
            # tiles north of the overworld mouth it came out of.
            "Boulder'gor": {(30, 46): ("Arathi West", 44, 31)},
            # ===== TEMPEST ISLE =====
            # The boat. Saltspur's berth tile (52,28) shipped UNREGISTERED on 7 Nov precisely
            # until there was somewhere to sail to - an unregistered portal tile fails safe,
            # the same property that let Thoradin's Wall stay shut for weeks.
            # The two passes and the dungeon door are deliberately NOT here yet: the Ashen
            # Reach and Khaz Varun do not exist, and a link to a zone that is not built is
            # how you walk in and never walk out. They fail safe until those land.
            "Tempest Shallows": {
                (74, 66): ("Saltspur Landing", 50, 28),
                # The two passes, round the volcano's west and east flanks. The volcano sits ON
                # the border, so these are the only two ways between the halves of the isle.
                (58, 4): ("The Ashen Reach", 58, 154),
                (176, 4): ("The Ashen Reach", 176, 154),
                (102, 76): ("Khaz Varun, the Black Hollow", 95, 192),
            },

            "The Ashen Reach": {
                (58, 156): ("Tempest Shallows", 58, 6),
                (176, 156): ("Tempest Shallows", 176, 6),
                (176, 98): ("Cinderwharf", 5, 44),       # moved inland 14 Nov: the gate stood in the sea
                (115, 132): ("The Emberdeep", 85, 8),
            },

            "The Emberdeep": {
                # The door is on the volcano's NORTH face, so the dungeon's own exit is at the
                # TOP of its map and the run descends south from it.
                (85, 6): ("The Ashen Reach", 115, 134),
            },

            "Khaz Varun, the Black Hollow": {
                (95, 194): ("Tempest Shallows", 102, 78),
            },

            "Cinderwharf": {
                (2, 42): ("The Ashen Reach", 173, 98),
            },

            "Boulderfist Hall": {(32, 50): ("Arathi Central", 38, 37)},
            "The Drowned Barrow": {(30, 52): ("Arathi East", 34, 35)},
            "Wrackline Hold": {(28, 48): ("Arathi East", 150, 57)},
            "The Tidewrack": {(34, 50): ("Arathi East", 160, 129)},
            "Stromgarde Keep": {(84, 144): ("Arathi West", 36, 137)},
            "Drywhisker Deeps": {(76, 154): ("Arathi Central", 170, 111)},

            "Eastern Hillsbrad": {
                # Hand-built (tools/handbuilt_hillsbrad_east.py): Tarren Mill, Durnholde, and the shut Arathi wall.
                (5, 86): ("Western Hillsbrad", 152, 88),           # arrive (152,86), clear of the east gate
                (62, 28): ("Tarren Mill", 34, 82),                 # the town gate off the mill square: arrive (34,80)
                (109, 74): ("Durnholde Keep", 70, 112),            # the keep's fallen archway
                (95, 138): ("Dun Garok", 55, 96),                  # the fort door cut into the southern ridge
                # THORADIN'S WALL, finally open. Shipped shut with the zone and left unregistered
                # until there was something on the far side of it - an unregistered portal tile fails
                # safe, which is why Ada Rook could stand there for weeks without a bug.
                (136, 148): ("Arathi West", 6, 120),
                (116, 7): ("The Frostward Descent", 60, 134),       # arrive (60,132), inside the entry hall
            },
            "Dun Garok": {
                # The fort door faces NORTH - the ridge rock it is cut into starts at y=139 - so the usual
                # "+3, arrive just south of the door" does not work here; south of this door is solid rock.
                (55, 96): ("Eastern Hillsbrad", 95, 138),           # arrive (95,136), on the road side
            },
            "Durnholde Keep": {
                (70, 112): ("Eastern Hillsbrad", 109, 77),         # dungeon exit: +3 -> arrive (109,75)
            },
            "The Frostward Descent": {
                # Out, back up to Hillsbrad: +3 so the player lands one tile south of the fissure.
                (60, 134): ("Eastern Hillsbrad", 116, 10),          # arrive (116,11), clear below the mouth
                (58, 8): ("The Crystalline Underdark", 85, 12),     # out onto the shelf above the cavern floor
            },
            "The Crystalline Underdark": {
                (150, 62): ("The Hollow Geode", 55, 102),          # arrive (55,100), inside the crack
                (85, 12): ("The Frostward Descent", 58, 11),        # arrive just inside the threshold
                (72, 80): ("Kael's Bastion", 48, 84),               # arrive (48,82), inside the gate
                (34, 142): ("The Deep Bloom", 65, 142),           # arrive (65,140), inside the Portico
            },
            "The Deep Bloom": {
                (65, 144): ("The Crystalline Underdark", 34, 146),  # dungeon exit: arrive (34,147), clear of the mouth
            },
            "The Hollow Geode": {
                (55, 104): ("The Crystalline Underdark", 150, 65),  # cave exit: arrive (150,63), below the crack
            },
            "Kael's Bastion": {
                (48, 86): ("The Crystalline Underdark", 72, 84),    # arrive (72,82), on the forecourt
            },
            "Hammerfall": {
                # The one hole in the stockade rim - see handbuilt_hammerfall.cliff_field,
                # which cuts the gate column AFTER forcing the map rim to rock so a later
                # edit cannot reopen the back of the town by accident.
                (52, 85): ("Arathi Central", 138, 62),           # arrive (138,64), on the basin road
            },
            "Saltspur Landing": {
                (52, 28): ("Tempest Shallows", 77, 68),
                # The bluff cut - the one hole in the rim, carved after it is forced.
                (2, 28): ("Arathi East", 50, 96),               # arrive (50,98), on the coast road
            },
            "Tarren Mill": {
                # The town's south gate sits on the WEST bank - the race runs x=43..49 at that latitude, so a
                # gate on the map's centre line would have been underwater.
                (34, 84): ("Eastern Hillsbrad", 62, 32),           # arrive (62,30), on the square's flagstones
            },
            "The Sepulcher": {
                (44, 67): ("Silverpine North", 32, 102),           # arrive (32,100), south of the gate
            },
            "Ambermill Tower": {
                (75, 128): ("Silverpine South", 138, 90),          # cave exit: +3 -> arrive (138,91), south of the waygate
            },
            "Shadowfang Keep": {
                # Was pointing back to Silverpine North's portal (100,10)
                # instead of the actual Sepulcher-side entrance you walked
                # in from (100,155) - so leaving the dungeon dumped you
                # clear across the map instead of back at the door.
                (100, 172): ("Silverpine South", 48, 144),         # cave exit: +3 -> arrive (48,145), south of the gate
            },
            "Fenris Isle": {
                (30, 55): ("Shadowpine Altar", 75, 115),
                (80, 129): ("Silverpine South", 149, 46),   # boat return: arrive (149,44) on the pier
            },
            "Shadowpine Altar": {
                (75, 115): ("Fenris Isle", 30, 55),             # cave exit: +3 -> arrive (30,56), south of the ridge arch
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
                (16, 136): ("Silverpine North", 80, 11),             # arrive (80,9)
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

        # SECRET DOORS to hidden zones (world/secrets.py, world/hidden_zones.py) come from
        # data/world/secrets.json, both ways: the door in the parent map, and the hidden zone's own
        # way out back to it. Kept out of the table above so nothing here says where they are.
        try:
            from world.secrets import get_secrets
            for (zone, x, y, to, tx, ty) in get_secrets().doors():
                self._links.setdefault(zone, {})[(x, y)] = (to, tx, ty)
                self._links.setdefault(to, {})[(tx, ty)] = (zone, x, y)
        except Exception:
            pass

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
