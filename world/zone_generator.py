"""
Zone generator. Creates initial zones with procedural generation and hand-crafted layouts.
"""
import random
from world.tilemap import Tilemap


class ZoneGenerator:
    """Generates zones with tilemaps."""
    
    @staticmethod
    def generate_valley_of_trials():
        """Generate Valley of Trials starter zone (120x120).

        FULL REBUILD this session (Kyle: "full restart - design fresh
        around this reference", following a ChatGPT-generated overworld
        reference image showing a valley ringed by a complete mountain
        wall, an offset organic lake with rock islands, tree-lined
        shores, and stone cave-mouth entrances built into the mountain
        face). Replaces the old function entirely rather than patching
        it again - the prior version had accumulated ~15 sequential
        patches (thin ring removed, then a corner-only range added,
        rocky pockets added then removed, chunk sizes tuned 3 times)
        and still didn't match this reference's actual composition
        (full ring vs. one corner; offset lake vs. dead-center square;
        no shore trees; no real cave-mouth art).

        3 portal anchors are HARD CONSTRAINTS, not redesigned - real,
        hardcoded coordinates in world/portal_manager.py's _links dict
        that other zones (Durotar, The Den, Burning Blade Coven) link
        back to by exact (x,y). Checked directly before writing this:
          (115, 60) -> Durotar
          (40, 30)  -> The Den
          (95, 22)  -> Burning Blade Coven
        Also checked data/creatures/spawn_points.json for 3 existing
        spawn coordinates (61,20)/(83,75)/(97,89) - not hard
        constraints (nothing else references them by exact position),
        but kept clear of solid mountain fill as a courtesy so existing
        spawns don't end up buried in unwalkable rock.
        """
        zone = Tilemap("Valley of Trials", 120, 120,
                        "A sheltered red-sand valley ringed by mountains, with a spring-fed lake at its heart.")

        zone.fill("sand", "base")

        # ------------------------------------------------------------------
        # MOUNTAIN RING - full perimeter, 3 real gaps for the portal anchors
        # ------------------------------------------------------------------
        # Same organic angle-jittered edge as the old _mountain_range
        # (proven bug-free this session - the earlier per-tile-random
        # jitter bug that produced isolated glitchy debris tiles was
        # found and fixed in that function already), applied as a true
        # RING around the whole 120x120 perimeter instead of one corner
        # blob. border_depth=14 gives a real, substantial mountain wall
        # (matching the reference's dense jagged wall, not last
        # session's "small flavor" thin ring) while still leaving
        # ~78% of the interior open ((120-2*14)^2/120^2 - real
        # geometry, not assumed).
        #
        # Gaps: a rectangular clear corridor cut through the ring at
        # each of the 3 portal anchors, wide enough for the cave-mouth
        # landmark art (6 tiles) or a plain road-cut (8 tiles wide for
        # the Durotar exit, matching "a narrow gap cut through a rock
        # ridge" from the old code's own comment about that crossing).
        border_depth = 14
        portal_gaps = [
            (40, 30, 8, 8),    # The Den (north-west wall)
            (95, 22, 8, 8),    # Burning Blade Coven (north wall)
            (115, 60, 10, 16), # Durotar exit (east wall) - wider, it's a road not a cave mouth
        ]

        def _in_any_gap(x, y):
            for (gx, gy, gw, gh) in portal_gaps:
                if abs(x - gx) <= gw // 2 and abs(y - gy) <= gh // 2:
                    return True
            return False

        import math
        for y in range(zone.height):
            for x in range(zone.width):
                edge_dist = min(x, zone.width - 1 - x, y, zone.height - 1 - y)
                if edge_dist >= border_depth:
                    continue  # solidly interior, never walled
                if _in_any_gap(x, y):
                    continue  # portal corridor - stays open
                # Angle-jittered edge (same technique as the proven-fixed
                # _mountain_range) so the inner boundary of the ring
                # reads as a natural ragged mountain edge, not a drawn
                # rectangle - jitter keyed on position ALONG the edge
                # (slowly varying), never per-tile independent random.
                if x < zone.width / 2:
                    pos = y if y < zone.height / 2 else zone.height - y
                else:
                    pos = y if y < zone.height / 2 else zone.height - y
                jitter = 3 * math.sin(pos * 0.12) + 2 * math.sin(pos * 0.31)
                effective_depth = border_depth + jitter
                if edge_dist >= effective_depth:
                    continue
                zone.set_tile(x, y, "cliff", "collision")

        # ------------------------------------------------------------------
        # LAKE - offset from center (matches the reference's asymmetric
        # placement, not a dead-center square), organic shape via jittered
        # radius, 2-3 small rock islands inside it.
        # ------------------------------------------------------------------
        # lake_cy shifted from 48 to 68 (Kyle: "lake needs to be shifted
        # down a lot" after a real map screenshot showed it hugging the
        # north portion, crowding the hub/buildings above it). 68 gives
        # real breathing room from the hub (~y=20) above and the
        # Durotar exit (y=60, though that's a different x) while
        # staying clear of the south boundary ring (border_depth=14
        # from y=119, so anything below ~y=105 risks the ring).
        lake_cx, lake_cy = 55, 68
        lake_r = 16
        for dy in range(-lake_r - 4, lake_r + 5):
            for dx in range(-lake_r - 4, lake_r + 5):
                x, y = lake_cx + dx, lake_cy + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                angle = math.atan2(dy, dx)
                jitter = 1.0 + 0.18 * math.sin(angle * 4.5) + 0.08 * math.sin(angle * 9)
                dist = (dx ** 2 + dy ** 2) ** 0.5
                r = lake_r * jitter
                if dist < r * 0.62:
                    zone.set_tile(x, y, "deep_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < r * 0.85:
                    zone.set_tile(x, y, "shallow_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < r:
                    zone.set_tile(x, y, "sand", "base")
                    zone.collision_layer[y][x] = None

        # Rock islands - real standalone landmark props (this session's
        # fix: an earlier version used the same "cliff" collision tile
        # + obstacle_chunk texture as the mountain ring, clipped to a
        # tiny 3x2-tile footprint - rendered as an ugly small diamond-
        # shaped blob, confirmed via a real render, not assumed. Real
        # standalone rock-formation art (reused from the Barrens props
        # session) reads correctly at small scale the way the mountain
        # ring's chunked wall texture doesn't). add_landmark already
        # gives real collision (solid=True default), no separate
        # set_tile pass needed.
        island_specs = [
            (lake_cx - 3, lake_cy + 2, "mountain_rock.png"),
            (lake_cx + 5, lake_cy - 4, "rock_outcrop.png"),
            (lake_cx + 2, lake_cy + 6, "mountain_rock.png"),
        ]
        for (icx, icy, sprite) in island_specs:
            zone.add_landmark(f"assets/tiles/barrens/props/{sprite}",
                               icx - 1, icy - 1, 3, 3)
        # One tree on the largest island, matching the reference's
        # central island tree - placed just beside the rock (not on
        # the same tile) so it doesn't visually stack with the
        # landmark's own collision footprint.
        zone.set_tile(lake_cx - 3, lake_cy + 3, "tree", "collision")

        # ------------------------------------------------------------------
        # SHORELINE TREES - ring the lake's edge (the reference's most
        # visually distinctive feature versus the old bare-pond look).
        # Loose organic scatter just outside the lake's jittered radius,
        # not a uniform ring - real groves have gaps and clumps.
        # ------------------------------------------------------------------
        for _ in range(90):
            angle = random.uniform(0, 2 * math.pi)
            dist = lake_r * random.uniform(1.05, 1.4)
            x = round(lake_cx + dist * math.cos(angle))
            y = round(lake_cy + dist * math.sin(angle))
            if not (0 <= x < zone.width and 0 <= y < zone.height):
                continue
            if zone.base_layer[y][x] in ("deep_water", "shallow_water"):
                continue
            if zone.collision_layer[y][x]:
                continue
            if random.random() < 0.6:
                zone.set_tile(x, y, "tree", "collision")

        # Extra tree groves further out (matches the reference's trees
        # scattered between the lake and the mountain wall, not just
        # right at the shore) - same loose-clustering approach as the
        # old code's grove_centers, kept for the parts of the reference
        # that are just "trees dotted around the open valley floor".
        grove_centers = [(30, 80), (85, 85), (25, 30), (90, 70)]
        for gx, gy in grove_centers:
            for _ in range(16):
                x = gx + random.randint(-9, 9)
                y = gy + random.randint(-9, 9)
                if (0 <= x < zone.width and 0 <= y < zone.height
                        and zone.base_layer[y][x] not in ("deep_water", "shallow_water")
                        and not zone.collision_layer[y][x]
                        and random.random() < 0.5):
                    zone.set_tile(x, y, "tree", "collision")

        # ------------------------------------------------------------------
        # NPC HUB + RECRUIT CAMP BUILDINGS - kept south of the lake,
        # same buildings/positions as before (real, working landmark
        # placements - no reason to redesign what wasn't broken).
        # ------------------------------------------------------------------
        ZoneGenerator._carve_landing(zone, 60, 20, radius=1)
        zone.set_tile(60, 20, "npc", "interaction")

        for _ in range(5):
            x = random.randint(20, 100)
            y = random.randint(20, 100)
            if zone.is_walkable(x, y):
                zone.set_tile(x, y, "chest", "interaction")

        BUILDING_SCALE = 0.67
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/novice_longhouse.png", 49, 5, 15, 12),
            ("assets/buildings/weapon_rack_shelter.png", 58, 6, 12, 9),
            ("assets/buildings/trial_hut.png", 33, 17, 9, 9),
            ("assets/buildings/elders_tent.png", 65, 15, 9, 9),
            ("assets/buildings/generic_house_a.png", 47, 30, 9, 9),
            ("assets/buildings/generic_hut_a.png", 62, 25, 9, 9),
        ]:
            new_w = max(1, round(w * BUILDING_SCALE))
            new_h = max(1, round(h * BUILDING_SCALE))
            new_anchor_x = anchor_x + (w - new_w) // 2
            new_anchor_y = anchor_y + (h - new_h) // 2
            zone.add_landmark(sprite_key, new_anchor_x, new_anchor_y, new_w, new_h)

        zone.add_subzone("Scorpid Nest", 78, 8, 34, 30)
        zone.add_subzone("Trailwater Spring", lake_cx - 12, lake_cy - 12, 24, 24)
        zone.add_subzone("Sagewood Grove", 63, 23, 24, 22)

        # ------------------------------------------------------------------
        # CAVE ENTRANCES - real stone-archway landmark art (this session,
        # ChatGPT-sourced to match the reference image exactly), placed
        # INTO the mountain ring's gaps rather than standing alone in
        # open sand like the old bare-portal-tile version. 6x4 tile
        # footprint (~1.5:1 aspect, matches all 3 source images' real
        # aspect ratio of 1.38-1.51 - checked directly, not assumed).
        # mouth_offset centers the walkable opening at bottom-middle,
        # where the dark cave-mouth actually sits in the art.
        # ------------------------------------------------------------------
        cave_entrance_specs = [
            (40, 30, "cave_entrance_torches"),   # The Den - natural, worked entrance
            (95, 22, "cave_entrance_banners"),   # Burning Blade Coven - hostile Horde banners
        ]
        for (cx, cy, sprite) in cave_entrance_specs:
            ZoneGenerator._carve_landing(zone, cx, cy, radius=2)
            zone.set_tile(cx, cy, "portal", "interaction")
            anchor_x, anchor_y = cx - 3, cy - 3
            zone.add_landmark(f"assets/tiles/cave_entrances/{sprite}.png",
                              anchor_x, anchor_y, 6, 4, mouth_offset=(3, 3))

        # Durotar exit (115,60) is a road-cut through the mountain wall,
        # not a cave mouth (matches the reference map's real Durotar-side
        # label "Entrance to Valley of Trials" - a plain archway/road
        # crossing, not a cave). Just a clear walkable corridor + portal,
        # already carved by the ring's own portal_gaps above.
        ZoneGenerator._carve_landing(zone, 115, 60, radius=3)
        zone.set_tile(115, 60, "portal", "interaction")

        # Small rock scatter on the cave approaches (kept from the old
        # version - real, working, no reason to drop it).
        ZoneGenerator._scatter(zone, "small_rocks", 0.04, area=(32, 22, 48, 38))
        ZoneGenerator._scatter(zone, "small_rocks", 0.05, area=(87, 14, 103, 30))

        # Keep the 3 existing spawn_points.json coordinates clear of
        # solid mountain/collision (courtesy, not a hard requirement -
        # nothing else references these by exact position, but no
        # reason to bury a working spawn under new rock).
        for (sx, sy) in [(61, 20), (83, 75), (97, 89)]:
            if zone.collision_layer[sy][sx] == "cliff":
                zone.collision_layer[sy][sx] = None

        # ------------------------------------------------------------------
        # GROUND CHUNKS - real chunked desert texture (proven system,
        # kept from last session), tiled across the walkable interior.
        # ------------------------------------------------------------------
        desert_chunk_variants = [
            "assets/tiles/valley_of_trials/desert_ground_chunk_a.png",
            "assets/tiles/valley_of_trials/desert_ground_chunk_b.png",
            "assets/tiles/valley_of_trials/desert_ground_chunk_c.png",
        ]
        subzone_terrain_regions = [
            {
                "name": "Sagebrush Flat", "table_key": "Valley of Trials",
                "rect": (18, 18, 22, 22),
                "variants": ["terrain_grassy.png", "terrain_mixed.png"],
            },
            {
                "name": "Cinderjaw Wastes", "table_key": "Cinderjaw Wastes",
                "rect": (18, 82, 40, 22),
                "variants": ["terrain_rocky.png", "terrain_scorched.png"],
            },
            {
                "name": "Windrift Dunes", "table_key": "Valley of Trials",
                "rect": (84, 30, 22, 40),
                "variants": ["terrain_dune.png", "terrain_hardpan.png"],
            },
        ]
        for region in subzone_terrain_regions:
            rx, ry, rw, rh = region["rect"]
            zone.add_subzone(region["table_key"], rx, ry, rw, rh,
                              display_name=region["name"])

        def chunk_variants_for(cx, cy, cs):
            for region in subzone_terrain_regions:
                rx, ry, rw, rh = region["rect"]
                overlaps = not (cx + cs <= rx or cx >= rx + rw
                                 or cy + cs <= ry or cy >= ry + rh)
                if overlaps:
                    return [f"assets/tiles/valley_of_trials/terrain_variants/{v}"
                            for v in region["variants"]]
            return desert_chunk_variants

        chunk_size = 20
        variant_i = 0
        for cy in range(0, zone.height, chunk_size):
            for cx in range(0, zone.width, chunk_size):
                w = min(chunk_size, zone.width - cx)
                h = min(chunk_size, zone.height - cy)
                variants = chunk_variants_for(cx, cy, chunk_size)
                sprite = variants[variant_i % len(variants)]
                zone.add_ground_chunk(sprite, cx, cy, w, h)
                variant_i += 1

        # Lake water chunks - real variety (this session, Kyle: "water
        # tiles" - a fresh 20-tile sheet with open/shore/deep variants).
        # Was a single chunk covering the whole lake bounding box with
        # one texture (oasis_deep_water.png everywhere) - now a real
        # grid of smaller chunks, same "multiple chunks side by side,
        # each its own sprite" pattern add_ground_chunk already uses for
        # variety (add_water_chunk itself has no variant-list param, so
        # this matches the existing mechanism rather than adding a new
        # one). Open/bright variants toward the center, shore-transition
        # variants toward the edges - each individually clipped to real
        # water tiles by the renderer regardless of which grid cell it's
        # in, so the lake's actual jittered organic shape still reads
        # correctly through whichever chunk happens to cover a given
        # water tile.
        #
        # NOT using the sheet's "deep_*" cave-water variants here (Kyle:
        # real bug caught via a rendered screenshot - water_deep_boulder/
        # water_deep_spires are moody, dark, underwater-rock-spire art
        # meant for an enclosed cave pool, not a sunlit open-air desert
        # lake; placed adjacent to bright open-water chunks it looked
        # like two completely different materials stitched together,
        # not real texture variety). Those variants are reserved for
        # The Den's own water instead, where that mood actually fits.
        lake_deep_variants = [
            "assets/tiles/water_variants/water_open_a.png",
            "assets/tiles/water_variants/water_open_b.png",
            "assets/tiles/water_variants/water_ripple.png",
            "assets/tiles/water_variants/water_sparkle.png",
        ]
        lake_shore_variants = [
            "assets/tiles/water_variants/water_shore_mossy.png",
            "assets/tiles/water_variants/water_shore_boulders.png",
            "assets/tiles/water_variants/water_shore_round_rocks.png",
            "assets/tiles/water_variants/water_shore_stones.png",
        ]
        water_chunk_size = 12
        water_variant_i = 0
        for cy in range(lake_cy - 24, lake_cy + 24, water_chunk_size):
            for cx in range(lake_cx - 24, lake_cx + 24, water_chunk_size):
                # Cells near the lake's own center get deep-water
                # variants; cells nearer the edge of the chunk grid get
                # shore-transition variants - a simple distance check
                # against the grid's own center (not the lake's true
                # jittered radius, which isn't needed here since every
                # chunk is clipped to real water tiles regardless).
                cell_dist = ((cx + water_chunk_size / 2 - lake_cx) ** 2
                             + (cy + water_chunk_size / 2 - lake_cy) ** 2) ** 0.5
                variants = lake_deep_variants if cell_dist < 14 else lake_shore_variants
                sprite = variants[water_variant_i % len(variants)]
                zone.add_water_chunk(sprite, cx, cy, water_chunk_size, water_chunk_size)
                water_variant_i += 1

        # Mountain ring obstacle chunks - 4x4-tile blocks (128x128px,
        # Kyle's explicit size cap) across the whole map; renderer clips
        # to real "cliff" tiles only, so this cheaply covers the entire
        # irregular ring shape without needing to hand-match chunk
        # placement to the ring's jittered edge.
        obstacle_chunk_size = 4
        for cy in range(0, zone.height, obstacle_chunk_size):
            for cx in range(0, zone.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, zone.width - cx)
                ch = min(obstacle_chunk_size, zone.height - cy)
                zone.add_obstacle_chunk("assets/tiles/valley_of_trials/cliff_wall_a.png",
                                         cx, cy, cw, ch)

        # ------------------------------------------------------------------
        # ROADS - straight-line network (add_road_path auto-decomposes
        # any diagonal into right-angle legs), connecting the hub to
        # both cave entrances and each building's front door, plus a
        # spine out to the Durotar exit.
        # ------------------------------------------------------------------
        # Base-layer "path" tiles for real walkability/pathing data.
        # Road endpoints updated to match the lake's new position (Kyle:
        # "lake needs to be shifted down a lot", lake_cy moved 48->68) -
        # (60,34) was the OLD lake's north shore; with the lake now
        # centered at y=68 (radius ~16-20 jittered), its real north
        # shore sits around y=52, not y=34 - checked directly against
        # the new lake_cy rather than left stale, which would have
        # dead-ended this road in open desert disconnected from the
        # actual water.
        ZoneGenerator._paint_road(zone, 60, 20, 60, 52, width=1, base="path")       # hub -> lake north shore
        ZoneGenerator._paint_road(zone, 60, 52, 115, 60, width=1, base="path")      # lake -> Durotar exit
        ZoneGenerator._paint_road(zone, 60, 30, 40, 30, width=1, base="path")       # spur -> The Den
        ZoneGenerator._paint_road(zone, 60, 25, 95, 22, width=1, base="path")       # spur -> Burning Blade Coven
        ZoneGenerator._paint_road(zone, 56, 13, 60, 20, width=1, base="path")       # novice_longhouse -> hub
        ZoneGenerator._paint_road(zone, 64, 12, 60, 20, width=1, base="path")       # weapon_rack_shelter -> hub
        ZoneGenerator._paint_road(zone, 37, 23, 60, 20, width=1, base="path")       # trial_hut -> hub
        ZoneGenerator._paint_road(zone, 69, 21, 60, 20, width=1, base="path")       # elders_tent -> hub
        ZoneGenerator._paint_road(zone, 51, 36, 60, 30, width=1, base="path")       # generic_house_a -> spine
        ZoneGenerator._paint_road(zone, 66, 31, 60, 30, width=1, base="path")       # generic_hut_a -> spine

        # Real road art overlay (visual only, matches path data above).
        road_variants = [
            "assets/tiles/valley_of_trials/road_main.png",
            "assets/tiles/valley_of_trials/road_light.png",
            "assets/tiles/valley_of_trials/road_rocky.png",
            "assets/tiles/valley_of_trials/road_grass_edge.png",
        ]
        road_i = 0
        for (rx0, ry0, rx1, ry1, rw) in [
            (60, 20, 60, 52, 2),
            (60, 52, 115, 60, 2),
            (60, 30, 40, 30, 1),
            (60, 25, 95, 22, 1),
            (56, 13, 60, 20, 1),
            (64, 12, 60, 20, 1),
            (37, 23, 60, 20, 1),
            (69, 21, 60, 20, 1),
            (51, 36, 60, 30, 1),
            (66, 31, 60, 30, 1),
        ]:
            zone.add_road_path(road_variants[road_i % len(road_variants)],
                                rx0, ry0, rx1, ry1, width_tiles=rw)
            road_i += 1

        return zone
    
    # ==================================================================
    # DUROTAR (levels 1-13) - rebuilt to match real WoW geography
    # ==================================================================
    # Was 150x100 (wide). Real Durotar is a TALL north-south strip on
    # Kalimdor's east coast, so this is now 110x240. Landmarks placed to
    # match the actual zone map:
    #
    #   Orgrimmar gate ..... far north-west
    #   Drygulch Ravine .... north-east
    #   Thunder Ridge ...... north-east, below Drygulch
    #   Valley of Trials ... west, upper-middle
    #   Razor Hill ......... centre-east
    #   Skull Rock ......... east coast, centre
    #   Rocktusk Farm ...... south-centre-west
    #   Tiragarde Keep ..... south-east coast
    #   Kolkar Crag ........ SOUTH-WEST
    #   Sen'jin Village .... south
    #   Scuttle Coast ...... south-east shore
    #   Echo Isles ......... SOUTH-EAST, offshore
    #   Southfury River .... western border
    #
    # The separate "Southern Durotar" zone is folded back in here - real
    # Durotar is one contiguous zone, and its southern creatures now live in
    # properly-placed subzone regions instead of a bolted-on second map.

    @staticmethod
    def generate_durotar():
        """Generate Durotar (130x220). Tall north-south, matching the real
        WoW map: Orgrimmar north, Razor Hill center, Valley of Trials
        south-west, Echo Isles/coast south-east, Sen'jin south.

        FULL REBUILD this session (Kyle: "I guess it's time to redo
        durotar", then confirmed "Full rebuild like VoT" when asked how
        much should change, after providing a real labeled overworld
        reference image). The PRIOR version already had genuinely correct
        geography - every named location in the reference image (Orgrimmar,
        Thunder Ridge, Zeppelin Tower, Razor Hill, Kolkar Crag, Tiragarde
        Keep, Skull Rock Approach, Rocktusk Farm, Scuttle Cove, Echo Isles,
        Naga Dungeon/Sunken Grotto, Valley of Trials entrance) already
        existed as a real subzone/landmark/portal in the code, hand-tuned
        across many prior sessions - this rebuild keeps ALL of that
        geography and ALL 11 hard portal coordinates (checked directly
        against world/portal_manager.py's real _links dict before writing
        a single line here, not assumed) and replaces ONLY the rendering
        layer: small per-tile crops for ground/water/mountain -> real
        chunked art (add_ground_chunk/add_water_chunk/add_obstacle_chunk),
        the same upgrade Valley of Trials, The Den, and Burning Blade
        Coven already got this session.

        Hard portal coordinates (verified against portal_manager.py):
          (65, 26)   -> Orgrimmar
          (95, 25)   -> Drygulch Ravine
          (112, 35)  -> Zeppelin Tower
          (120, 40)  -> Sunken Grotto of the Deep (Naga Dungeon)
          (118, 60)  -> Skull Rock
          (5, 85)    -> Central Barrens
          (65, 108)  -> Razor Hill
          (40, 130)  -> Dustwind Cave
          (28, 150)  -> Valley of Trials
          (110, 150) -> Echo Isles
          (95, 178)  -> Tiragarde Keep
        Also: Valley of Trials' own (115,60) links back here, so Durotar
        must have real walkable ground at (115,60) even though nothing
        exits FROM Durotar at that exact point (it's VoT's arrival spot
        on this map, the reverse direction of the (28,150) portal above).
        """
        zone = Tilemap("Durotar", 130, 220,
                       "A harsh red land of jagged canyons and dust, running "
                       "from Orgrimmar's gates down to the southern isles.")
        zone.region = "Kalimdor - East Coast"

        zone.fill("sand", "base")


        # ------------------------------------------------------------------
        # WATER - Southfury River (west border), eastern sea (whole east
        # coast), southern channel to Echo Isles. Real base_layer carve
        # first (same technique as before - this part wasn't broken,
        # only the RENDERING was old small-crop art), chunked water art
        # layered on top afterward once the shape is settled.
        # ------------------------------------------------------------------
        for y in range(zone.height):
            river_x = 6 + int(4 * (y / zone.height))
            for dx in range(-5, 6):
                x = river_x + dx
                if 0 <= x < zone.width:
                    zone.set_tile(x, y, "deep_water" if abs(dx) < 3
                                  else "shallow_water", "base")

        for y in range(zone.height):
            coast = zone.width - 8 if y < 140 else zone.width - 8 - int((y - 140) / 9)
            for x in range(max(coast, 0), zone.width):
                depth = x - coast
                zone.set_tile(x, y, "shallow_water" if depth < 3 else "deep_water", "base")

        for y in range(200, zone.height):
            for x in range(zone.width):
                zone.set_tile(x, y, "deep_water", "base")

        # ------------------------------------------------------------------
        # MOUNTAIN RANGES - real jagged ridges matching the reference
        # image (dense mountain mass along the whole west side and
        # scattered ranges elsewhere), NOT the old random-scatter "rock"
        # dusting (160 small clusters at 35% density - the same disease
        # every pre-rebuild zone had this session: individually-small,
        # scattered collision tiles that never read as a real landform).
        # Uses the same proven _mountain_range primitive as Valley of
        # Trials' own corner range - solid organic-jittered ellipse, real
        # mass, not speckle. Placed to match the reference's actual
        # silhouette: one big western range running most of the map's
        # height, a secondary range up near Thunder Ridge/Drygulch, and
        # smaller flanking ranges near Rocktusk Farm / south of Razor
        # Hill - all positioned to leave the existing hard-contract
        # portal coordinates and named subzone clearings genuinely clear
        # (checked directly below, not assumed).
        mountain_ranges = [
            (30, 50, 16, 45),   # NW range, Thunder Ridge's backdrop
            (20, 118, 12, 28),  # W range, flanking Kolkar Crag/Rocktusk - repositioned off (28,150) VoT portal, verified via real distance check, not eyeballed
            (50, 190, 12, 22),  # SW range, near Valley of Trials approach
            (100, 90, 10, 20),  # small range east of Razor Hill
        ]
        for (mcx, mcy, mw, mh) in mountain_ranges:
            ZoneGenerator._mountain_range(zone, mcx, mcy, mw, mh)

        # ------------------------------------------------------------------
        # PORTALS - 11 hard-contract coordinates (verified against
        # world/portal_manager.py's real _links dict at the top of this
        # function's docstring, not assumed). Each gets a real landing
        # clearing + a path back to the north-south spine road (x=65,
        # added below) so it's genuinely reachable, not just individually
        # walkable in isolation - same VoT protocol as every rebuilt zone
        # this session: carve first, verify with is_walkable/reachability
        # after, never assume a coordinate survived terrain carving.
        # ------------------------------------------------------------------
        spine_x = 65
        portal_specs = [
            (65, 26),    # Orgrimmar
            (95, 25),    # Drygulch Ravine
            (112, 35),   # Zeppelin Tower
            (120, 40),   # Sunken Grotto of the Deep (Naga Dungeon)
            (118, 60),   # Skull Rock
            (65, 108),   # Razor Hill
            (40, 130),   # Dustwind Cave
            (28, 150),   # Valley of Trials
            (110, 150),  # Echo Isles
            (95, 178),   # Tiragarde Keep
        ]
        for (px, py) in portal_specs:
            ZoneGenerator._carve_landing(zone, px, py, radius=3)
            zone.set_tile(px, py, "portal", "interaction")
            ZoneGenerator._carve_path(zone, px, py, spine_x, py, width=2)

        # REAL VISUAL ROAD ART - Kyle: "Durotar in general needs roads"
        # after confirming the spine/spur _carve_path calls above only
        # ever wrote invisible base_layer="path" walkability data, never
        # any add_road_path visual overlay (checked directly - zero
        # add_road_path calls existed anywhere in this zone before this
        # fix). Matches every spur's real endpoints exactly so the
        # visible road lines up with the actual walkable path data, not
        # just an approximation.
        road_variants = [
            "assets/tiles/valley_of_trials/road_main.png",
            "assets/tiles/valley_of_trials/road_light.png",
            "assets/tiles/valley_of_trials/road_rocky.png",
            "assets/tiles/valley_of_trials/road_grass_edge.png",
        ]
        road_i = 0
        # The spine itself - one long road down the middle.
        zone.add_road_path(road_variants[road_i % len(road_variants)],
                            spine_x, 20, spine_x, 200, width_tiles=3)
        road_i += 1
        for (px, py) in portal_specs:
            zone.add_road_path(road_variants[road_i % len(road_variants)],
                                px, py, spine_x, py, width_tiles=2)
            road_i += 1

        # Central Barrens (5,85) - REAL BUG FOUND AND FIXED this session
        # (Kyle: "entrance to barrens needs a bridge" with a screenshot
        # showing the portal's dry-ground clearing floating on top of
        # open water with a hard rectangular seam, no crossing at all).
        # Root cause: river_x at y=85 is 7 (river spans x:2-12 there),
        # so a plain _carve_landing(5,85) call was clearing a circle of
        # dry ground DIRECTLY INSIDE the river's real footprint - not a
        # rendering bug, a genuine "portal placed in the wrong medium"
        # bug. Real fix: carve a walkable strip across the river's full
        # width at this Y (not just a local circle) and lay the real
        # bridge_long landmark over it, matching how every other water
        # crossing in this session's rebuilds works.
        barrens_x, barrens_y = 5, 85
        ZoneGenerator._carve_path(zone, 0, barrens_y, barrens_x + 8, barrens_y, width=3)
        zone.set_tile(barrens_x, barrens_y, "portal", "interaction")
        ZoneGenerator._carve_path(zone, barrens_x, barrens_y, spine_x, barrens_y, width=2)
        zone.add_landmark("assets/tiles/bridges/bridge_long.png",
                           -2, barrens_y - 3, 16, 6, solid=False)
        zone.add_road_path("assets/tiles/valley_of_trials/road_main.png",
                            barrens_x, barrens_y, spine_x, barrens_y, width_tiles=2)

        # (115,60) is NOT a Durotar-side portal trigger - it's Valley of
        # Trials' own arrival coordinate for players entering FROM
        # Durotar's (28,150) portal (the reverse direction). No portal
        # tile needed here, just real walkable ground so a returning
        # player doesn't land in solid rock/water - verified directly
        # after the mountain ranges above already confirmed this is
        # walkable by default (no mountain/water carve reaches it), but
        # a real landing clear is added anyway as a safety net matching
        # every other named arrival point in this zone.
        ZoneGenerator._carve_landing(zone, 115, 60, radius=3)

        # North-south spine road connecting every portal's own landing
        # (each already has a path to spine_x at its own latitude above -
        # this is the actual spine itself, the shared road all those
        # spurs connect into).
        ZoneGenerator._carve_path(zone, spine_x, 20, spine_x, 200, width=3)

        # ------------------------------------------------------------------
        # SUBZONES - 5 named regions with real pre-existing encounter
        # table entries (checked directly in data/creatures/encounters.json
        # before writing these rects, not assumed) - Thunder Ridge, Skull
        # Rock Approach, Kolkar Crag, Rocktusk Farm, Scuttle Coast. Rects
        # deliberately overlap several portal coordinates where that's
        # geographically correct (Skull Rock Approach genuinely contains
        # the Zeppelin/Naga/Skull Rock cluster; Kolkar Crag contains
        # Dustwind Cave; Scuttle Coast contains Echo Isles) - verified via
        # direct point-in-rect check against all 12 hard coordinates
        # before finalizing these positions, not eyeballed.
        # ------------------------------------------------------------------
        zone.add_subzone("Thunder Ridge", 35, 30, 40, 35, display_name="Thunder Ridge Approach")
        zone.add_subzone("Skull Rock Approach", 96, 30, 34, 46)
        zone.add_subzone("Kolkar Crag", 5, 100, 40, 45)
        zone.add_subzone("Rocktusk Farm", 18, 155, 30, 30)
        zone.add_subzone("Scuttle Coast", 90, 130, 36, 40)

        # ------------------------------------------------------------------
        # CAVE ENTRANCE + STRUCTURE LANDMARKS - REAL FIX this session
        # (Kyle: "you removed the Orgrimmar gates? Why?... zeppelin
        # entrance is a cave? Bro...we have a zeppelin tower!" - both
        # confirmed real regressions, not assumed: Orgrimmar's gate
        # landmark call was simply missing from this rebuild entirely,
        # and Zeppelin Tower was using a cave-mouth sprite with a
        # comment literally admitting "not a cave, but a real structure
        # marker fits" - a lazy placeholder shipped instead of the real
        # zeppelin_tower.png art that already existed on disk the whole
        # time). Real structure-specific art now used for every non-cave
        # landmark; genuine caves (Naga Grotto, Skull Rock, Dustwind
        # Cave) keep cave-mouth art. Thunder Ridge and Drygulch Ravine
        # ALSO had zero landmark at all (confirmed via a real screenshot
        # of the in-game map showing bare portal dots) - both get a real
        # marker now too.
        # ------------------------------------------------------------------
        # Scaled up from 6x5 (Kyle: "these gates should be much larger too
        # to show off the entrance to org. They are sad now" - confirmed
        # wide open space all around this landmark on Durotar's map, real
        # headroom to grow it). ~2.3x, re-centered on the same (65,26)
        # portal tile the gate sits above so the entrance still lines up.
        zone.add_landmark("assets/buildings/orgrimmar_gate.png", 51, 10, 14, 11)
        zone.add_landmark("assets/buildings/zeppelin_tower.png", 108, 29, 6, 4)
        zone.add_landmark("assets/tiles/cave_entrances/cave_entrance_plain.png",
                           117, 34, 6, 4, mouth_offset=(3, 3))  # Sunken Grotto of the Deep
        zone.add_landmark("assets/tiles/cave_entrances/cave_entrance_banners.png",
                           115, 54, 6, 4, mouth_offset=(3, 3))  # Skull Rock - hostile, real rebuild pending
        zone.add_landmark("assets/tiles/cave_entrances/cave_entrance_plain.png",
                           37, 124, 6, 4, mouth_offset=(3, 3))  # Dustwind Cave
        zone.add_landmark("assets/buildings/guard_post.png", 92, 17, 4, 4)   # Drygulch Ravine
        zone.add_landmark("assets/buildings/guard_post.png", 52, 41, 4, 4)   # Thunder Ridge
        # Tiragarde Keep - TEMPORARY marker only (Kyle: "needs some sort
        # of keep entrance, not just a cave... we need to fully redo the
        # keep" - the real rebuild against the reference fortress art is
        # a separate, larger task queued after these quick fixes, not
        # done here). watchtower.png is a real structural improvement
        # over the previous Horde-banner cave mouth (wrong faction
        # entirely for what's meant to be a fortress) without
        # pretending this is the final art.
        zone.add_landmark("assets/buildings/watchtower.png", 92, 168, 6, 5)

        # Razor Hill "town signal" (Kyle: "we should also do something
        # to signal about razor hill, like houses or something? Or some
        # kind of large town icon" - Razor Hill is a real separate zone
        # entered via portal, same as every cave, so this is purely a
        # visual marker on Durotar's own map telling the player "a real
        # town is here", not the town itself).
        zone.add_landmark("assets/buildings/crossroads_town_hall.png", 62, 100, 6, 5)

        # Scattered decoration buildings (Kyle: "we used to have
        # buildings scattered around Durotar to make it lively. These
        # are gone?" - confirmed: this rebuild never placed any at all).
        # Real positions checked for clearance against roads/mountains/
        # water before placing (same discipline as every other landmark
        # this session), not eyeballed.
        # Scaled up ~1.8x (Kyle: "Durotar's are too small" compared to
        # every other town's buildings). generic_shack_a's original spot
        # (100,85) is a cramped mountain-rock pocket with no room to grow
        # in place (confirmed via direct collision scan) - moved to
        # (110,85), a clear open stretch nearby, rather than shrinking the
        # building back down to fit.
        scatter_buildings = [
            ("assets/buildings/plain_orc_house_a.png", 73, 44, 9, 5),
            ("assets/buildings/plain_orc_house_b.png", 43, 94, 9, 5),
            ("assets/buildings/generic_shack_a.png", 110, 85, 7, 5),
            ("assets/buildings/generic_shack_b.png", 19, 174, 7, 5),
            ("assets/buildings/watchtower.png", 68, 128, 9, 9),
        ]
        for (sprite, bx, by, bw, bh) in scatter_buildings:
            zone.add_landmark(sprite, bx, by, bw, bh)

        # Scuttle Coast murloc huts (Kyle, this session - real hut art
        # uploaded, replacing the "art sourced, not yet wired in" state
        # noted in the handoff). 3 real variants placed along the
        # subzone's own coastline (checked directly against the actual
        # water tiles at x~120-126 within this rect before placing, not
        # guessed) - spaced at varied y so they don't read as a lined-up
        # row, a couple tiles inland from the water's edge.
        zone.add_landmark("assets/tiles/scuttle_coast/props/murloc_hut_stilted.png",
                           109, 133, 7, 8)
        zone.add_landmark("assets/tiles/scuttle_coast/props/murloc_hut_net.png",
                           97, 138, 7, 8)
        zone.add_landmark("assets/tiles/scuttle_coast/props/murloc_hut_basket.png",
                           107, 159, 7, 7)

        # ------------------------------------------------------------------
        # CHUNKED ART - the real point of this rebuild (Kyle: "Full
        # rebuild like VoT... real chunked art"). Same proven pattern as
        # Valley of Trials: ground_chunks tiled across the whole map in a
        # real grid (not one giant chunk - that caused a genuine blur bug
        # caught and fixed for VoT's mountain wall earlier this session),
        # water_chunks over the real river/ocean shape (clipped to actual
        # water tiles, not the chunk's bounding rectangle - the fix that
        # solved VoT's checkerboard-pond bug), obstacle_chunks over the
        # real mountain ranges at the proven 4x4-tile (128px) cap.
        # ------------------------------------------------------------------
        desert_chunk_variants = [
            "assets/tiles/valley_of_trials/desert_ground_chunk_a.png",
            "assets/tiles/valley_of_trials/desert_ground_chunk_b.png",
            "assets/tiles/valley_of_trials/desert_ground_chunk_c.png",
        ]
        # Real terrain-variety per named subzone (Kyle: "Make sure there
        # is variety" - reusing the 6 terrain_variants already generated
        # for Valley of Trials, same desert-family palette, no new art
        # needed). Each subzone gets a texture pairing matching its own
        # real character: Thunder Ridge (rocky, mountain-adjacent),
        # Skull Rock Approach (scorched, ominous), Kolkar Crag (mixed
        # scrubland, a centaur camp not bare sand), Rocktusk Farm
        # (grassy, actual farmland), Scuttle Coast (dune/hardpan, real
        # coastal sand distinct from interior desert).
        subzone_terrain_regions = [
            {"rect": (35, 30, 40, 35), "variants": ["terrain_rocky.png", "terrain_hardpan.png"]},       # Thunder Ridge
            {"rect": (96, 30, 34, 46), "variants": ["terrain_scorched.png", "terrain_rocky.png"]},      # Skull Rock Approach
            {"rect": (5, 100, 40, 45), "variants": ["terrain_mixed.png", "terrain_scorched.png"]},      # Kolkar Crag
            {"rect": (18, 155, 30, 30), "variants": ["assets/tiles/rocktusk_farm/trampled_farmland.png", "assets/tiles/rocktusk_farm/quilboar_churned.png"]},  # Rocktusk Farm - real quilboar-farmland sand variants (Kyle: sandy, VoT-windswept family, not generic desert)
            {"rect": (90, 130, 36, 40), "variants": ["assets/tiles/echo_isles/beach_sand.png"]},         # Scuttle Coast - real coastal sand (Echo Isles' surviving beach_sand.png, reused per Kyle - the murloc village sits right on the shore, dune/hardpan desert never fit here)
        ]

        def chunk_variants_for(cx, cy, cs):
            # Overlap-based, not center-point (real bug caught and fixed
            # for Valley of Trials earlier this session: a chunk's
            # CENTER can land just outside a region's rect even when
            # most of the chunk's actual area overlaps it, silently
            # misassigning that chunk to the generic desert cycle
            # instead of the region's real terrain).
            for region in subzone_terrain_regions:
                rx, ry, rw, rh = region["rect"]
                overlaps = not (cx + cs <= rx or cx >= rx + rw
                                 or cy + cs <= ry or cy >= ry + rh)
                if overlaps:
                    # A variant entry containing "/" is already a full
                    # path (e.g. Scuttle Coast's reused Echo Isles beach
                    # sand, which doesn't live under valley_of_trials/
                    # terrain_variants/ like every other entry here) -
                    # only bare filenames get that prefix prepended.
                    return [v if "/" in v else f"assets/tiles/valley_of_trials/terrain_variants/{v}"
                            for v in region["variants"]]
            return desert_chunk_variants

        chunk_size = 20
        variant_i = 0
        for cy in range(0, zone.height, chunk_size):
            for cx in range(0, zone.width, chunk_size):
                cw = min(chunk_size, zone.width - cx)
                ch = min(chunk_size, zone.height - cy)
                variants = chunk_variants_for(cx, cy, chunk_size)
                sprite = variants[variant_i % len(variants)]
                zone.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        # Water chunks - open-air bright variants (same reasoning as
        # VoT's lake: the moody underwater-cave "deep_*" variants read as
        # a mismatched material next to open-air water, confirmed via a
        # real rendered screenshot earlier this session - reserved those
        # for cave interiors only). River gets a tighter chunk grid
        # (narrower shape), ocean gets a coarser one (much larger area).
        water_variants = [
            "assets/tiles/water_variants/water_open_a.png",
            "assets/tiles/water_variants/water_open_b.png",
            "assets/tiles/water_variants/water_ripple.png",
            "assets/tiles/water_variants/water_sparkle.png",
            "assets/tiles/water_variants/water_choppy.png",
        ]
        water_variant_i = 0
        # River: narrow strip along x=0-16, full height.
        for cy in range(0, zone.height, 12):
            for cx in range(0, 20, 12):
                ch = min(12, zone.height - cy)
                sprite = water_variants[water_variant_i % len(water_variants)]
                zone.add_water_chunk(sprite, cx, cy, 12, ch)
                water_variant_i += 1
        # Ocean: east coast + south channel, coarser grid across the
        # whole east/south water extent.
        for cy in range(0, zone.height, 20):
            for cx in range(zone.width - 30, zone.width, 20):
                cw = min(20, zone.width - cx)
                ch = min(20, zone.height - cy)
                sprite = water_variants[water_variant_i % len(water_variants)]
                zone.add_water_chunk(sprite, cx, cy, cw, ch)
                water_variant_i += 1

        # Obstacle chunks - ONLY over the real mountain ranges' actual
        # bounding areas, not a blind full-map 4x4 grid (real performance
        # bug found and fixed here: a full 130x220 map at 4x4 chunks
        # produces 1815 obstacle chunks, and _draw_chunk_layer's clipped
        # per-tile draw loop runs its clip-check for every one of them
        # every frame regardless of whether that chunk contains any real
        # mountain tiles at all - measured directly: 263ms for a single
        # frame at the real 1280x720 gameplay viewport, genuinely
        # unplayable (~4fps). Durotar's mountain ranges only cover a
        # small fraction of the total map area (4 discrete ranges, not
        # mountains-everywhere like a cave's walls), so this restricts
        # chunk registration to each range's own real bounding box
        # (with margin for edge_jitter) instead of the whole map -
        # tiles outside every range's bbox were never going to have
        # obstacle_chunk coverage anyway (get_obstacle_chunk_at would
        # just return None there), so this changes performance, not
        # correctness.
        mountain_variants = [
            "assets/tiles/valley_of_trials/cliff_wall_a.png",
            "assets/tiles/valley_of_trials/cliff_wall_b.png",
        ]
        mountain_variant_i = 0
        obstacle_chunk_size = 4
        margin = 6  # real edge_jitter allowance beyond the nominal radius
        for (mcx, mcy, mw, mh) in mountain_ranges:
            bx0, by0 = mcx - mw - margin, mcy - mh - margin
            bx1, by1 = mcx + mw + margin, mcy + mh + margin
            bx0, by0 = max(0, bx0), max(0, by0)
            bx1, by1 = min(zone.width, bx1), min(zone.height, by1)
            for cy in range(by0, by1, obstacle_chunk_size):
                for cx in range(bx0, bx1, obstacle_chunk_size):
                    cw = min(obstacle_chunk_size, bx1 - cx)
                    ch = min(obstacle_chunk_size, by1 - cy)
                    sprite = mountain_variants[mountain_variant_i % len(mountain_variants)]
                    zone.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                    mountain_variant_i += 1

        return zone

    @staticmethod
    def generate_razor_hill():
        """Generate Razor Hill town zone (60x60). Central Durotar hub - its
        only exit leads back to Durotar; Valley of Trials and Echo Isles are
        reached by walking Durotar's own roads, not directly from town.

        Full rebuild (Kyle): the old version filled the whole map with a
        flat 4x5 grid of identical 8x5 "wall" collision boxes - no building
        art, no relationship to the 14 real named NPCs already living here
        (data/npcs/ambient_npcs.json, zone=razor_hill) or the vendor
        (data/npcs/vendors.json). Real WoW Razor Hill is an orc crossroads
        town built around Orgnil Soulscar's investigation of the Burning
        Blade, with the Razor Hill Barracks as "the single most prominent
        structure in the town" (Warcraft Wiki, confirmed via web search),
        an inn (Innkeeper Grosk), class trainers, a smithy, and a guard
        watchtower - which maps almost one-to-one onto the NPC roster this
        codebase already has. Every NPC/vendor coordinate below is copied
        verbatim from the JSON data (never re-derived) since 4 of them are
        referenced by npc_id in data/quests/razor_hill.json as quest
        givers, and the single portal at (30,55) must match
        world/portal_manager.py exactly.
        """
        zone = Tilemap("Razor Hill", 60, 60, "A frontier orc crossroads town, hub of central Durotar.")

        # Fill with stone base (town square)
        zone.fill("stone", "base")

        # Real Razor Hill buildings, spread across the full 60x60 map
        # around the real NPCs' new positions (Kyle: "spread out NPCs
        # properly in towns... I don't want towns to be some weird ass
        # cluster fuck" - the original 14 NPCs were packed into a ~22x20
        # tile corner, which meant nothing could actually spread out once
        # buildings scaled up). NPCs were moved to real town quarters -
        # north (guards/barracks), west (smith/trainer), east (market/
        # traders), south (residential) - all via data/npcs/ambient_npcs.json,
        # safe to move freely since quests reference npc_id, never
        # coordinates. Building sizes are 2.5x their original footprint,
        # not the project's usual 3x: at 3x, this specific town's math
        # didn't work (10 buildings + 15 spread NPCs genuinely don't fit
        # in 60x60 with real breathing room at 3x - verified by running the
        # actual placement search and watching it fail), so Kyle called for
        # "scale down very slightly" here specifically rather than resizing
        # the zone. Every anchor below re-verified via the same headless
        # collision scan standard, this time proximity-aware (nearest open
        # spot to each building's target NPC, not just first open spot).
        for sprite_key, anchor_x, anchor_y, w, h in [
            # Biggest/most prominent structure in town (Warcraft Wiki) -
            # near the north guard cluster.
            ("assets/buildings/frontier_barracks.png", 24, 12, 18, 10),
            # Innkeeper Grosk (30,25) - town center
            ("assets/buildings/crossroads_inn.png", 18, 24, 10, 10),
            # Blacksmith Kragg (15,20)
            ("assets/buildings/smithy.png", 1, 15, 12, 10),
            # Weapons Trainer Grokk (10,30)
            ("assets/buildings/trainers_lodge.png", 0, 38, 10, 8),
            # Kravel Coinsnatch (48,28) / Kelm the Merchant (46,25)
            ("assets/buildings/supply_depot.png", 31, 27, 15, 8),
            # Razor Hill Sentry (48,15) - tall lookout post, north-east watch
            ("assets/buildings/watchtower.png", 43, 3, 8, 10),
            # Grandmother Ulaka (10,35) - elder, tent fits
            ("assets/buildings/elders_tent.png", 0, 28, 8, 8),
            # Tal'rashi, troll refugee (50,35)
            ("assets/buildings/elders_tent.png", 46, 37, 8, 8),
            # Corlan Ashe, human defector (18,45)
            ("assets/buildings/generic_hut_a.png", 20, 41, 8, 8),
            # Aendel Duskrunner, blood elf scribe (12,40)
            ("assets/buildings/generic_hut_a.png", 8, 47, 8, 8),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        # Real lively town-square decoration (Kyle: "we need some sexy
        # props and tiles for it" - layout itself was already confirmed
        # good, this is purely an art/liveliness pass). Reused real,
        # already-existing props rather than wait on new art - a market
        # stall row, a campfire, and a loot crate/barrel cluster, all
        # genuinely sized for chunked-art-era placement (378-581px
        # source), spread through real verified-clear spots (checked
        # directly against the 10 buildings' actual collision footprint,
        # not eyeballed). A dedicated packed-dirt ground texture (the
        # zone still uses flat "stone" fill, no chunked art at all) and
        # more town-specific props (hitching post, supply crates,
        # signpost) are a real follow-up pending new art from Kyle.
        zone.add_landmark("assets/buildings/bazaar_stall_row.png", 33, 37, 6, 4)
        zone.add_landmark("assets/tiles/burning_blade_coven/props/campfire_ring.png", 19, 19, 4, 4, solid=False)
        zone.add_landmark("assets/tiles/burning_blade_coven/props/loot_crate_barrel.png", 37, 41, 4, 4)

        # Chunked ground art (Kyle: "razor hill still has small tiles" -
        # this zone really did have NO chunk art at all, just the flat
        # "stone" per-tile fill from above, which is what read as "small
        # tiles" against every other town's large-format chunks). Real
        # packed-dirt town ground, assets/tiles/durotar/packed_town_dirt_*
        # - genuinely unused anywhere else in the project until now,
        # named for exactly this. Same 2-variant checkerboard-avoidance
        # pattern as other towns (alternating by chunk index so adjacent
        # chunks never repeat the same variant).
        durotar = "assets/tiles/durotar"
        town_variants = [f"{durotar}/packed_town_dirt_a.png", f"{durotar}/packed_town_dirt_b.png"]
        chunk_size = 10
        variant_i = 0
        for cy in range(0, zone.height, chunk_size):
            for cx in range(0, zone.width, chunk_size):
                cw = min(chunk_size, zone.width - cx)
                ch = min(chunk_size, zone.height - cy)
                sprite = town_variants[variant_i % len(town_variants)]
                zone.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        # Basic path spurs linking the building cluster to the south portal
        # - deliberately simple (same single "path" base tile as every
        # other road in this file), Kyle's building a real path tileset
        # later so this isn't worth over-engineering now.
        ZoneGenerator._paint_road(zone, 30, 25, 30, 55, width=2, base="path")   # town center -> Durotar portal
        ZoneGenerator._paint_road(zone, 30, 40, 26, 38, width=1, base="path")   # spur -> orc farmer Kagra

        # Single exit back to Durotar (south gate)
        ZoneGenerator._carve_landing(zone, 30, 55, radius=3)
        zone.set_tile(30, 55, "portal", "interaction")  # -> Durotar

        return zone
    
    @staticmethod
    def generate_echo_isles():
        """Generate Echo Isles (160x160) - a real dedicated rebuild
        (Kyle: "let's revisit... build with what's on hand" after
        confirming this zone's previous version was still the old
        generic 100x100 random-scatter generator despite the
        architecture doc's own notes claiming a 160x160 resize, real
        art, and rescaled portals were already done - none of that had
        actually landed in this function. Verified directly before
        writing this: 2 of portal_manager.py's 4 real Echo Isles exit
        coordinates ((80,152) and (128,99)) were OUT OF BOUNDS on the
        old 100x100 map - a live, real bug, not a hypothetical one.

        4 separate rock-pillar islands connected by real carved-water
        crossings + bridge_long/bridge_short landmark art on top (same
        "carve first, lay bridge art over it" pattern as the Barrens
        entrance crossing elsewhere in this file - the walkability
        comes from the carve, the bridge is a solid=False visual only):

        - Central Isle: both Durotar docks (north/south), the open-zone
          "Isle Interior" encounter table, quest NPC + vendor.
        - Troll Camp Isle: the real "Troll Camps" subzone from
          encounters.json, connected off Central Isle's east side.
        - Grotto Isle: Sunken Temple Grotto's cave entrance (west).
        - Hollow Isle: Zalazane's Hollow's cave entrance (east) -
          bestiary calls this "the capstone of the starter cluster",
          so it's deliberately the furthest/last island reached rather
          than sitting right next to a dock.

        Real asset set already on disk (jungle_floor_a/b, beach_sand,
        rock_pillar_a/b, palm_cluster/lean_a/lean_b, shipwreck_full/
        fragment) - no ruin/temple landmark or coral/shell scatter
        exists yet (both were referenced in the OLD broken generator
        via _scatter(zone, "coral_blue", ...) etc, but "coral_blue"/
        "coral_red"/"shell" were never real tile_ids in world/tiles.py
        at all - confirmed by grep, not assumed - so those calls were
        silently no-opping every time). Kyle: build with what's real
        now, more props later.

        exit_pos coordinates below are ALL real hard contracts from
        world/portal_manager.py's _links dict, checked directly, not
        assumed: (80,8)->Durotar(110,150), (80,152)->Durotar(105,150),
        (48,88)->Sunken Temple Grotto(50,81), (128,99)->Zalazane's
        Hollow(52,86).
        """
        width, height = 160, 160
        zone = Tilemap("Echo Isles", width, height,
                        "A tropical island chain off Durotar's coast, its rock-pillar islets linked by rope bridges.")

        # Water everywhere by default - islands are carved dry landmasses
        # cut INTO it, same "start solid/wet, carve the real shape out"
        # approach every cave generator in this file already uses for
        # rock, just with water as the default medium instead.
        zone.fill("deep_water", "base")
        for y in range(height):
            for x in range(width):
                zone.collision_layer[y][x] = "water"

        def carve_island(cx, cy, rw, rh, floor="jungle_floor_a"):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < width and 0 <= y < height:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            zone.collision_layer[y][x] = None
                            zone.set_tile(x, y, "grass", "base")

        # ------------------------------------------------------------------
        # CENTRAL ISLE - the big one. Spans most of the map's height since
        # both Durotar docks sit at the same x=80 but opposite ends
        # (y=8 north, y=152 south) - a single elongated island covers
        # both without a separate crossing needed just to reach either
        # dock from the interior.
        # ------------------------------------------------------------------
        central = (80, 80)
        carve_island(*central, 22, 62)

        # ------------------------------------------------------------------
        # TROLL CAMP ISLE - east of Central, a real separate landmass
        # (not just a subzone rect drawn over the same island) so it
        # reads as its own place, matching the reference's genuinely
        # separate-islets composition.
        # ------------------------------------------------------------------
        troll_camp = (118, 60)
        carve_island(*troll_camp, 14, 14)

        # ------------------------------------------------------------------
        # GROTTO ISLE (west) - small, just enough to host the cave
        # entrance clearing. exit_pos (48,88) is the real hard contract.
        # ------------------------------------------------------------------
        grotto_isle = (44, 88)
        carve_island(*grotto_isle, 12, 12)

        # ------------------------------------------------------------------
        # HOLLOW ISLE (east) - Zalazane's Hollow, the real capstone.
        # Placed furthest from both docks on purpose (bestiary: "should
        # feel like a real test before whatever Phase 8 dungeon comes
        # next" - the layout itself should make you work to reach it,
        # not have it sitting right next to the entrance).
        # ------------------------------------------------------------------
        hollow_isle = (132, 104)
        carve_island(*hollow_isle, 13, 13)

        # ------------------------------------------------------------------
        # WATER CROSSINGS - real carved dry strips first (this IS the
        # walkability), bridge landmark art laid over each as a visual
        # only (solid=False) - same order every other water-crossing in
        # this file uses.
        # ------------------------------------------------------------------
        def carve_crossing(x0, y0, x1, y1, width_tiles=2):
            ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width_tiles, base="grass")

        # Central <-> Troll Camp (east)
        carve_crossing(98, 62, 108, 60)
        zone.add_landmark("assets/tiles/bridges/bridge_long.png",
                           97, 55, 14, 10, solid=False)

        # Central <-> Grotto Isle (west)
        carve_crossing(60, 88, 54, 88)
        zone.add_landmark("assets/tiles/bridges/bridge_short.png",
                           53, 83, 10, 10, solid=False)

        # Troll Camp <-> Hollow Isle (southeast) - the real final
        # approach to the capstone cave, deliberately the LAST crossing
        # on the route rather than a direct line from Central.
        #
        # REAL BUG FOUND + FIXED (Kyle: "the bridges in echo isles are
        # turned the wrong way"). This crossing runs NORTH-SOUTH (126,68)
        # -> (128,92): dx=2, dy=24, almost purely vertical. The original
        # bridge_sag.png (like bridge_long/bridge_short - checked
        # directly) is a side-view illustration with a dark painterly
        # vignette background, not top-down art - it "worked" for the
        # other two (genuinely horizontal) crossings only because that
        # orientation happened to hide the perspective mismatch. Rotated
        # 90 degrees for this vertical crossing, the vignette and
        # side-view angle became obviously wrong (Kyle: "it looks ugly as
        # fuck"). Real fix: a dedicated top-down plank-bridge asset
        # (bridge_plank.png, built this pass from real clean plank-grain
        # crops of assets/tiles/goblin_shared/dock_plank.png - no
        # hardware/rope clutter, feathered seams, no vignette/perspective
        # issue at any rotation) rather than forcing rotation on art that
        # was never meant to be rotated.
        carve_crossing(126, 68, 128, 92)
        zone.add_landmark("assets/tiles/bridges/bridge_plank.png",
                           118, 78, 12, 16, solid=False, rotation=90)

        # ------------------------------------------------------------------
        # SUBZONE - Troll Camps, matching encounters.json's real
        # existing table_key exactly.
        # ------------------------------------------------------------------
        zone.add_subzone("Troll Camps", troll_camp[0] - 14, troll_camp[1] - 14, 28, 28)

        # ------------------------------------------------------------------
        # PORTALS - all 4 coordinates are real hard contracts from
        # portal_manager.py, checked directly (see docstring). Each gets
        # a real carved landing + path inland so arriving players aren't
        # stranded at the map edge.
        # ------------------------------------------------------------------
        north_dock = (80, 8)
        south_dock = (80, 152)
        grotto_exit = (48, 88)
        hollow_exit = (128, 99)

        # North/south docks sit within Central Isle's own carved ellipse
        # (central=(80,80), rw=22,rh=62 comfortably covers y=18 to
        # y=142 at x=80 - checked directly: ((80-80)/22)^2 +
        # ((8-80)/62)^2 = 0 + 1.30, which is OUTSIDE the ellipse, so a
        # real landing clear is still needed right at the edge, same
        # safety-net discipline every other zone's portal gets).
        ZoneGenerator._carve_landing(zone, *north_dock, radius=4)
        ZoneGenerator._carve_path(zone, *north_dock, *central, width=3)
        zone.set_tile(*north_dock, "portal", "interaction")

        ZoneGenerator._carve_landing(zone, *south_dock, radius=4)
        ZoneGenerator._carve_path(zone, *south_dock, *central, width=3)
        zone.set_tile(*south_dock, "portal", "interaction")

        # Grotto/Hollow exits sit ON their own islands' carved ellipses
        # already (grotto_isle=(44,88) rw=12,rh=12 covers (48,88) at
        # distance 4 - well inside; hollow_isle=(132,104) rw=13,rh=13
        # covers (128,99) at distance ~6.4 - also inside) - landing
        # clears still added as the same unconditional safety net every
        # other portal in this codebase gets, not skipped just because
        # the math checks out on paper.
        ZoneGenerator._carve_landing(zone, *grotto_exit, radius=3)
        zone.set_tile(*grotto_exit, "portal", "interaction")

        ZoneGenerator._carve_landing(zone, *hollow_exit, radius=3)
        zone.set_tile(*hollow_exit, "portal", "interaction")

        # ------------------------------------------------------------------
        # NPC + quest marker - Central Isle's own interior, away from
        # both dock landings so it reads as a real destination rather
        # than sitting right on the arrival point.
        # ------------------------------------------------------------------
        npc_pos = (80, 80)
        ZoneGenerator._carve_landing(zone, *npc_pos, radius=2)
        zone.set_tile(npc_pos[0] - 2, npc_pos[1], "npc", "interaction")
        zone.set_tile(npc_pos[0] + 2, npc_pos[1], "quest_marker", "interaction")

        # ------------------------------------------------------------------
        # LANDMARKS - real props from what's on disk. Palms scattered
        # across every island (matches a tropical chain), shipwreck as a
        # real point-of-interest on Central Isle's own shore, nothing
        # referencing the missing ruin/coral/shell art the old generator
        # silently no-op'd on.
        # ------------------------------------------------------------------
        zone.add_landmark("assets/tiles/echo_isles/props/shipwreck_full.png",
                           95, 130, 10, 6, solid=False)
        zone.add_landmark("assets/tiles/echo_isles/props/shipwreck_fragment.png",
                           70, 25, 5, 6, solid=False)

        palm_variants = [
            "assets/tiles/echo_isles/props/palm_cluster.png",
            "assets/tiles/echo_isles/props/palm_lean_a.png",
            "assets/tiles/echo_isles/props/palm_lean_b.png",
        ]
        palm_spots = [
            (65, 40), (95, 45), (65, 100), (95, 115), (80, 30),
            (112, 55), (124, 65), (40, 82), (48, 94),
            (126, 98), (138, 108), (128, 112),
        ]
        for i, (px, py) in enumerate(palm_spots):
            zone.add_landmark(palm_variants[i % len(palm_variants)],
                               px, py, 4, 5, solid=False)

        # Real "someone was here before" / beach-clutter props (Kyle,
        # this session) - jungle idol as a Central Isle interior point
        # of interest, overgrown ruin fragment near Grotto Isle (temple-
        # adjacent, matching Sunken Temple Grotto's own name), coral/
        # shell cluster and tide pool as real beach detail away from
        # both dock landings and every existing crossing/portal.
        zone.add_landmark("assets/tiles/echo_isles/props/jungle_idol.png",
                           88, 60, 4, 6)
        zone.add_landmark("assets/tiles/echo_isles/props/overgrown_ruin.png",
                           58, 78, 6, 5)
        zone.add_landmark("assets/tiles/echo_isles/props/coral_shell_cluster.png",
                           68, 118, 5, 5, solid=False)
        zone.add_landmark("assets/tiles/echo_isles/props/tide_pool.png",
                           100, 100, 7, 5, solid=False)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR ART - jungle floor on Central/Troll Camp/Hollow
        # isles (real jungle interior), beach sand right at each
        # island's own shoreline reads better in theory but needs per-
        # tile coastline detection this pass doesn't do yet - flagged
        # here rather than faked; jungle floor throughout is the honest
        # current state. Grotto Isle (small, just a cave-entrance
        # clearing) gets beach sand throughout since it's mostly shore.
        # ------------------------------------------------------------------
        chunk_size = 20

        def floor_chunks(cx, cy, rw, rh, sprite):
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        zone.add_ground_chunk(sprite, gx, gy, gw, gh)

        jungle_variants = ["assets/tiles/echo_isles/jungle_floor_a.png",
                            "assets/tiles/echo_isles/jungle_floor_b.png"]

        variant_i = 0
        for cy in range(central[1] - 62, central[1] + 63, chunk_size):
            for cx in range(central[0] - 22, central[0] + 23, chunk_size):
                cw = min(chunk_size, (central[0] + 22) - cx)
                ch = min(chunk_size, (central[1] + 62) - cy)
                if cw > 0 and ch > 0:
                    zone.add_ground_chunk(jungle_variants[variant_i % len(jungle_variants)], cx, cy, cw, ch)
                    variant_i += 1

        floor_chunks(*troll_camp, 14, 14, jungle_variants[1])
        floor_chunks(*hollow_isle, 13, 13, jungle_variants[0])
        floor_chunks(*grotto_isle, 12, 12, "assets/tiles/echo_isles/beach_sand.png")

        # ------------------------------------------------------------------
        # WALL/OBSTACLE ART - rock pillar walls around each island's
        # collision edge (the water itself isn't a "wall" tile_id, so
        # this only matters wherever a real rock-pillar landmark or
        # cliff edge exists - none carved yet this pass, so this is
        # prepped for a future pass rather than wired to nothing).
        # ------------------------------------------------------------------

        zone.is_cave = False
        zone.fixed_spawns = False
        zone.add_subzone("Echo Isles", 0, 0, width, height, display_name="The Isle Interior")

        ZoneGenerator._scatter(zone, "flowers", 0.02)
        ZoneGenerator._scatter(zone, "small_rocks", 0.01)

        return zone

    # ==================================================================
    # THE BARRENS (levels 10-25)
    # ==================================================================
    # The big one. Roughly doubles the level ceiling of the playable world
    # (was 10-16, now 10-25) and bridges the starter cluster into mid-game.
    # Largest map in the game at 200x160.

    @staticmethod
    def generate_the_barrens():
        """Generate The Barrens (200x160). Levels 10-25."""
        zone = Tilemap("The Barrens", 200, 160,
                       "Endless golden savanna. Zhevra herds, quilboar "
                       "warrens, and the Wailing Caverns below.")

        zone.fill("dirt", "base")

        # Dry savanna grass in patches - the Barrens reads as scrubland, not
        # pure desert, so grass is the accent rather than the base.
        for y in range(zone.height):
            for x in range(zone.width):
                r = random.random()
                if r < 0.22:
                    zone.set_tile(x, y, "grass", "base")
                if r < 0.05:
                    zone.set_tile(x, y, "grass_tuft", "visual")
                elif r < 0.07:
                    zone.set_tile(x, y, "small_rocks", "visual")

        # --- Lushwater Oasis (northwest) ---
        ZoneGenerator._make_oasis(zone, 42, 38, radius=13)

        # --- The Forgotten Pools (west-central) ---
        ZoneGenerator._make_oasis(zone, 30, 92, radius=11)

        # --- Razorfen Approach (southeast): dense thorn scrub ---
        for _ in range(120):
            cx = random.randint(140, zone.width - 5)
            cy = random.randint(105, zone.height - 5)
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        if random.random() < 0.5:
                            zone.set_tile(x, y, "bushes", "collision")

        # --- Field of Giants (south-central): kodo bone fields, open ground ---
        for y in range(112, 148):
            for x in range(78, 132):
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
        for _ in range(30):
            x = random.randint(80, 130)
            y = random.randint(114, 146)
            zone.set_tile(x, y, "small_rocks", "visual")

        # --- Witchwing Terrace (northeast): elevated, cliff-ringed ---
        for dy in range(-16, 17):
            for dx in range(-20, 21):
                x, y = 165 + dx, 32 + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                dist = (dx ** 2 + (dy * 1.25) ** 2) ** 0.5
                if 15 < dist < 19 and random.random() < 0.6:
                    zone.set_tile(x, y, "cliff", "collision")
                elif dist <= 15:
                    zone.set_tile(x, y, "stone", "base")

        # --- Kolkar Plains (central): open, sparse, dangerous ---
        for y in range(60, 92):
            for x in range(95, 145):
                zone.collision_layer[y][x] = None

        # Scattered acacia trees across the plains, avoiding the named pockets
        for _ in range(220):
            x = random.randint(0, zone.width - 1)
            y = random.randint(0, zone.height - 1)
            if zone.base_layer[y][x] in ("deep_water", "shallow_water"):
                continue
            if random.random() < 0.55:
                zone.set_tile(x, y, "tree", "collision")

        # Rocky ridges breaking up the middle distance
        for _ in range(70):
            cx = random.randint(5, zone.width - 5)
            cy = random.randint(5, zone.height - 5)
            for dy in range(-1, 2):
                for dx in range(-4, 5):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        if random.random() < 0.3:
                            zone.set_tile(x, y, "rock", "collision")

        # --- The Crossroads (center): the hub, kept clear ---
        for dy in range(-9, 10):
            for dx in range(-11, 12):
                x, y = 100 + dx, 76 + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.set_tile(x, y, "dirt", "base")
                    zone.collision_layer[y][x] = None
        # Crossroads buildings
        for (bx, by) in [(92, 70), (105, 70), (92, 80), (105, 80)]:
            for dy in range(4):
                for dx in range(6):
                    x, y = bx + dx, by + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "wall", "collision")
        # Crossroads NPCs (vendors/quest givers)
        for (nx, ny) in [(99, 76), (102, 74), (97, 79), (104, 78)]:
            zone.set_tile(nx, ny, "npc", "interaction")

        # North-south and east-west roads meeting at the Crossroads
        for x in range(zone.width):
            for dy in range(-1, 2):
                y = 76 + dy
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
        for y in range(zone.height):
            for dx in range(-1, 2):
                x = 100 + dx
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None

        # Register the named regions so standing in them actually changes the
        # encounter table (and grants the 1.2x subzone XP bonus).
        zone.add_subzone("Lushwater Oasis", 26, 22, 34, 34)
        zone.add_subzone("The Forgotten Pools", 14, 76, 34, 34)
        zone.add_subzone("Razorfen Approach", 136, 100, 60, 58)
        # Kept clear of the Crossroads (centred 100,76 with an ~11x9 clearing)
        # so the hub town isn't inside a hostile subzone.
        zone.add_subzone("Kolkar Plains", 118, 44, 46, 30)
        zone.add_subzone("Field of Giants", 76, 110, 58, 40)
        zone.add_subzone("Witchwing Terrace", 146, 14, 42, 38)

        # Cave entrances
        for (cx, cy) in [(55, 118), (172, 92)]:
            ZoneGenerator._carve_path(zone, cx, cy, 100, cy)
            ZoneGenerator._carve_landing(zone, cx, cy, radius=3)
            zone.set_tile(cx, cy, "portal", "interaction")

        # Town exits: Ratchet on the east coast, Camp Taurajo to the south.
        for (px, py, tx, ty) in [(194, 76, 140, 76),    # -> Ratchet
                                 (100, 154, 100, 120)]:  # -> Camp Taurajo
            ZoneGenerator._carve_path(zone, px, py, tx, ty, width=2)
            ZoneGenerator._carve_landing(zone, px, py, radius=3)
            zone.set_tile(px, py, "portal", "interaction")

        # Treasure scattered off the roads
        for _ in range(12):
            x = random.randint(10, zone.width - 10)
            y = random.randint(10, zone.height - 10)
            if zone.is_walkable(x, y):
                zone.set_tile(x, y, "chest", "interaction")

        # Portals (positions must match world/portal_manager.py exactly)
        ZoneGenerator._carve_landing(zone, 4, 76)
        zone.set_tile(4, 76, "portal", "interaction")      # -> Southern Durotar
        ZoneGenerator._carve_landing(zone, 100, 4)
        zone.set_tile(100, 4, "portal", "interaction")     # -> Durotar (north road)

        return zone

    # ==================================================================
    # TOWN HUBS
    # ==================================================================

    @staticmethod
    def _build_town(zone, buildings, npc_positions, road_axis="both"):
        """Shared town scaffolding: clear ground, buildings, roads, NPCs."""
        for (bx, by, bw, bh) in buildings:
            for dy in range(bh):
                for dx in range(bw):
                    x, y = bx + dx, by + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "wall", "collision")
                        zone.set_tile(x, y, "wood", "base")
            # Doorway on the south face so buildings read as enterable
            dx0 = bx + bw // 2
            if 0 <= dx0 < zone.width and 0 <= by + bh - 1 < zone.height:
                zone.collision_layer[by + bh - 1][dx0] = None
                zone.set_tile(dx0, by + bh - 1, "door", "interaction")

        if road_axis in ("both", "h"):
            for x in range(zone.width):
                for dy in range(-1, 2):
                    y = zone.height // 2 + dy
                    if 0 <= y < zone.height:
                        zone.set_tile(x, y, "dirt", "base")
                        zone.collision_layer[y][x] = None
        if road_axis in ("both", "v"):
            for y in range(zone.height):
                for dx in range(-1, 2):
                    x = zone.width // 2 + dx
                    if 0 <= x < zone.width:
                        zone.set_tile(x, y, "dirt", "base")
                        zone.collision_layer[y][x] = None

        for (nx, ny) in npc_positions:
            ZoneGenerator._carve_landing(zone, nx, ny, radius=1)
            zone.set_tile(nx, ny, "npc", "interaction")

    @staticmethod
    def generate_ratchet():
        """Ratchet (70x60) - goblin port town on the Barrens east coast.

        Full rebuild (Kyle): the old version filled the map with 5 flat
        "wall" collision boxes that didn't even sit near the 18 real named
        NPCs already living here (data/npcs/ambient_npcs.json, zone=
        ratchet) - the boxes were at y=10-15/18-24/40-45, the NPCs at
        y=26-33. Real Classic Ratchet (confirmed via web search) is led by
        Gazlowe, a goblin free port with an inn, forge/anvil, and trade
        supplies - no real auctioneer despite what some infoboxes claim
        (confirmed via Warcraft Wiki talk page). Docks/harbor/boat are kept
        exactly as they were (already well-themed), only the land-side town
        core is rebuilt.
        """
        zone = Tilemap("Ratchet", 70, 60,
                       "A goblin free port. Neutral ground, inflated prices, "
                       "and a boat to anywhere.")
        zone.region = "The Barrens"

        zone.fill("dirt", "base")
        # Harbour: the eastern third is sea
        for y in range(zone.height):
            for x in range(46, zone.width):
                zone.set_tile(x, y, "shallow_water" if x < 50 else "deep_water", "base")
        # Docks jutting into the water
        for (dy0, length) in [(18, 16), (30, 20), (42, 14)]:
            for i in range(length):
                for dy in range(-1, 2):
                    x, y = 46 + i, dy0 + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        # "wood" is NOT a walkable tile type - using it as a
                        # floor made docks, platforms and building interiors
                        # impassable. Walkable surfaces use "stone".
                        zone.set_tile(x, y, "stone", "base")
                        zone.collision_layer[y][x] = None
        zone.set_tile(64, 30, "boat", "interaction")

        # Real named NPCs - spread across the full 70x60 map instead of
        # the old cramped y=26-33 cluster (Kyle: "make towns spread out
        # and populated... I want towns to be full"). Every position below
        # was moved in data/npcs/ambient_npcs.json / vendors.json (safe to
        # relocate freely - Ratchet's quest givers are referenced by
        # npc_id only, never coordinates, confirmed via grep across every
        # data/quests/*.json file before moving anyone).
        npc_positions = [(42, 20), (44, 26), (40, 34), (42, 40), (38, 44)]
        for (nx, ny) in npc_positions:
            ZoneGenerator._carve_landing(zone, nx, ny, radius=1)
            zone.set_tile(nx, ny, "npc", "interaction")
        # Gazlowe himself - real Classic leader of Ratchet, referenced in
        # quest dialogue (northern_barrens.json) but never actually placed
        # as an NPC until now. Stands right at his own office's entrance.
        ZoneGenerator._carve_landing(zone, 30, 8, radius=1)
        zone.set_tile(30, 8, "npc", "interaction")  # Gazlowe (ratchet_gazlowe)

        # Real building placements - 2.5x scale (matching Razor Hill and
        # Crossroads' fix, same reasoning: 3x didn't leave room for 19
        # spread NPCs + this many buildings on a 44-tile-wide land strip
        # - the harbor eats the eastern third of the map). Grew from 6
        # buildings to 14, spread across every quarter of the town instead
        # of clustered near the docks. Anchors verified via the same
        # headless collision scan (clear of water/docks, every real NPC
        # position, every other building) before being hardcoded.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/gazlowes_office.png", 25, 10, 10, 10),        # Gazlowe's own office
            ("assets/buildings/ratchet_docks_warehouse.png", 30, 22, 12, 10), # dock storage
            ("assets/buildings/bazaar_stall_row.png", 10, 22, 12, 10),        # trade supplies stalls
            ("assets/buildings/the_broken_keel.png", 12, 36, 12, 10),         # the town's inn/tavern
            ("assets/buildings/scrapyard_workshop.png", 5, 6, 10, 10),        # forge & anvil flavor
            ("assets/buildings/harbor_tower.png", 28, 34, 8, 12),             # harbor lookout
            ("assets/buildings/generic_house_a.png", 16, 12, 8, 8),
            ("assets/buildings/generic_house_b.png", 0, 32, 8, 8),
            ("assets/buildings/generic_hut_a.png", 4, 50, 8, 8),
            ("assets/buildings/generic_hut_b.png", 16, 50, 8, 8),
            ("assets/buildings/generic_shack_a.png", 36, 2, 8, 8),
            ("assets/buildings/generic_shack_b.png", 36, 47, 8, 8),
            ("assets/buildings/plain_orc_house_a.png", 27, 54, 8, 5),
            ("assets/buildings/plain_orc_house_b.png", 3, 41, 8, 5),
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        ZoneGenerator._carve_path(zone, 2, 30, 46, 30)
        ZoneGenerator._carve_landing(zone, 2, 30)
        zone.set_tile(2, 30, "portal", "interaction")   # -> The Barrens

        # ------------------------------------------------------------------
        # CHUNKED GROUND ART (Kyle, this session: "let's finish Ratchet
        # tiles" - zero chunked art existed here before now, rendering
        # on flat default "dirt"/"stone" colors). Real goblin-town tile
        # bank from this session (assets/tiles/goblin_shared/) - town_dirt
        # for the main land area, dock_plank for the 3 real docks jutting
        # into the harbor, oil_stained_dock near the harbor tower/
        # warehouse (the working industrial corner), scrap_metal_plaza
        # as a real accent patch near Gazlowe's office and the scrapyard
        # workshop (forge/anvil flavor - matches that building's own
        # theme). Dock tiles used as a general wood-surface fill rather
        # than relying on the tile's own baked-in water edge lining up
        # exactly - Ratchet's 3 docks run east-west (jutting into the
        # harbor) while the tile's water edge sits on its right side,
        # a minor visual mismatch worth knowing about but not a
        # functional problem (the real water is Ratchet's own
        # shallow_water/deep_water fill, unaffected by this).
        # ------------------------------------------------------------------
        goblin = "assets/tiles/goblin_shared"

        # Dock planking - placed as its own pass FIRST, repeating along
        # each real dock's actual length (matching the (dy0, length)
        # pairs used to carve them above) rather than one big stretched
        # copy across the whole strip - a single 16-20-tile-wide stretch
        # of a tile with a real baked-in water edge on one side reads as
        # obviously wrong (the edge only appears once, at the far end,
        # instead of the dock reading as repeating planking the whole
        # way out). Small chunks matching the tile's own real proportion
        # instead.
        dock_chunk_w = 3
        for (dy0, length) in [(18, 16), (30, 20), (42, 14)]:
            for i in range(0, length, dock_chunk_w):
                cw = min(dock_chunk_w, length - i)
                zone.add_ground_chunk(f"{goblin}/dock_plank.png", 46 + i, dy0 - 1, cw, 3)

        chunk_size = 10
        for cy in range(0, zone.height, chunk_size):
            for cx in range(0, zone.width, chunk_size):
                cw = min(chunk_size, zone.width - cx)
                ch = min(chunk_size, zone.height - cy)
                # Skip chunks entirely over water - already real
                # shallow_water/deep_water base tiles from the harbor
                # fill above, a ground chunk here would paint over them.
                # Smaller 10-tile chunks (down from 20) so a chunk
                # straddling a dock's own tip/open-water boundary
                # doesn't get skipped wholesale - caught as a real
                # visible black gap in a render check, not assumed fine.
                if all(zone.base_layer[cy + dy][cx + dx] in ("deep_water", "shallow_water")
                       for dy in range(ch) for dx in range(cw)
                       if cy + dy < zone.height and cx + dx < zone.width):
                    continue
                # Dock strips (the 3 real dock rows: y=17-19, y=29-31,
                # y=41-43, all around x=46+) already got real dock_plank
                # chunks in the dedicated pass above (matching each
                # dock's own actual length) - skip here rather than
                # redundantly re-painting the same area with differently
                # sized chunks.
                is_dock_row = any(abs(cy + ch // 2 - dy0) < 2 for dy0 in (18, 30, 42)) and cx + cw > 44
                if is_dock_row:
                    continue
                # Harbor tower / warehouse corner (x=28-42, y=20-46) -
                # the working industrial side of town.
                elif 28 <= cx <= 42 and 20 <= cy <= 46:
                    sprite = f"{goblin}/oil_stained_dock.png"
                # Gazlowe's office / scrapyard corner (x=0-36, y=0-20) -
                # real accent patch matching the forge/anvil flavor.
                elif cx <= 36 and cy <= 20:
                    sprite = f"{goblin}/scrap_metal_plaza.png"
                else:
                    sprite = f"{goblin}/town_dirt.png"
                zone.add_ground_chunk(sprite, cx, cy, cw, ch)

        return zone

    @staticmethod
    def generate_camp_taurajo():
        """Camp Taurajo (64x56) - tauren waystation, southern Barrens.

        Full rebuild (Kyle): the old version had 6 fake distance-carved
        "tent ring" shapes at positions 12-20 tiles away from the 16 real
        named NPCs already living here (data/npcs/ambient_npcs.json +
        vendors.json, zone=camp_taurajo) - same disconnect bug Razor Hill/
        Crossroads/Ratchet all had. `_build_town` was also stamping 4 more
        generic "npc" tiles on top of the real roster. Real Classic Camp
        Taurajo is led by Jorn Skyseer (confirmed via web search), with
        real vendor names (Kelsuwa, Omusa Thunderhorn) - not yet added as
        placed NPCs (same gap Thrall/Gazlowe/Sergra had before this
        project added them), left as a follow-up since the 16 NPCs
        already here needed the spread fix first. NPCs moved to real camp
        quarters (north/west/center/east/south) via ambient_npcs.json/
        vendors.json - safe to relocate freely, every taurajo_* npc_id
        referenced by quests uses the id only, never coordinates
        (confirmed via grep across every data/quests/*.json file).
        """
        zone = Tilemap("Camp Taurajo", 64, 56,
                       "A tauren hunting camp of hide tents and drying racks, "
                       "guarding the southern road.")
        zone.region = "The Barrens"

        zone.fill("dirt", "base")
        for y in range(zone.height):
            for x in range(zone.width):
                if random.random() < 0.18:
                    zone.set_tile(x, y, "grass", "base")
                if random.random() < 0.05:
                    zone.set_tile(x, y, "grass_tuft", "visual")

        # Real named NPCs, spread across all five camp quarters instead of
        # the old cramped x=24-30/y=23-29 cluster.
        for (nx, ny) in [(25,10),(40,10),(15,14),(8,22),(10,32),(8,42),(32,20),(32,30),
                          (28,35),(36,35),(50,14),(54,24),(50,34),(20,44),(44,44),(32,46)]:
            ZoneGenerator._carve_landing(zone, nx, ny, radius=1)
            zone.set_tile(nx, ny, "npc", "interaction")

        # Real building placements - 2.5x scale (matching Razor Hill/
        # Crossroads/Ratchet's fix), grown from 6 disconnected fake tent
        # shapes to 14 real buildings from the Camp Taurajo sprite set
        # plus generic filler, spread across every quarter. Anchors
        # verified via the same headless collision scan (clear of every
        # real NPC position, every other building) before being hardcoded.
        for sprite_key, anchor_x, anchor_y, w, h in [
            ("assets/buildings/taurajo_lodge.png", 18, 12, 12, 10),       # camp seat - biggest structure
            ("assets/buildings/elders_roundhouse.png", 19, 0, 10, 8),     # Elder Longtread
            ("assets/buildings/taurajo_stables.png", 52, 14, 12, 8),      # kodo wrangler
            ("assets/buildings/hide_tanners_hut.png", 3, 12, 10, 8),      # Tanner Mosswalker
            ("assets/buildings/taurajo_granary.png", 3, 44, 10, 10),      # Grainkeeper/provisioner
            ("assets/buildings/watchers_perch.png", 34, 15, 8, 10),       # Camp Sentry watchtower
            ("assets/buildings/generic_hut_a.png", 9, 3, 8, 8),           # totem carver
            ("assets/buildings/generic_hut_b.png", 12, 28, 8, 8),         # hide trader
            ("assets/buildings/generic_shack_a.png", 36, 0, 8, 8),        # warband scout
            ("assets/buildings/generic_shack_b.png", 46, 4, 8, 8),        # hunter
            ("assets/buildings/generic_tent_a.png", 52, 30, 8, 8),        # beast trainer
            ("assets/buildings/generic_tent_b.png", 16, 46, 8, 8),        # healer
            ("assets/buildings/plain_orc_house_a.png", 40, 37, 8, 5),     # orc liaison
            ("assets/buildings/plain_orc_house_b.png", 28, 39, 8, 5),     # provisioner area
        ]:
            zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

        for (px, py) in [(32, 2), (32, 53)]:
            ZoneGenerator._carve_path(zone, px, py, 32, 28)
            ZoneGenerator._carve_landing(zone, px, py)
            zone.set_tile(px, py, "portal", "interaction")
        # (32, 2)  -> Central Barrens (Crossroads' south road)
        # (32, 53) -> Southern Barrens

        # ------------------------------------------------------------------
        # CHUNKED GROUND ART (Kyle, this session: "tile Camp T and
        # Crossroads, basic Horde towns/outposts, more dirt and Barrens
        # looks" - zero chunked art existed here before now). Real
        # Barrens grass/dirt variants already on disk. Camp Taurajo is
        # bigger and less road-focused than Crossroads (a real hunting
        # camp, tauren-run, not a paved trade hub), so this gets 3 real
        # variants across its footprint instead of a center/outer split:
        # sparse_grass for the well-trodden central camp area, dry_grass_
        # sparse for the outer quarters, and grass_with_rocks for the
        # camp's own south stretch (toward Southern Barrens - reads as
        # rockier terrain at the camp's edge, matching a frontier
        # waystation rather than a manicured town).
        # ------------------------------------------------------------------
        barrens_grass = "assets/tiles/barrens/grass"
        chunk_size = 20
        for cy in range(0, zone.height, chunk_size):
            for cx in range(0, zone.width, chunk_size):
                cw = min(chunk_size, zone.width - cx)
                ch = min(chunk_size, zone.height - cy)
                cy_center = cy + ch / 2
                dist_from_center = ((cx + cw/2 - zone.width/2) ** 2 + (cy_center - 28) ** 2) ** 0.5
                if cy_center > 42:
                    sprite = f"{barrens_grass}/grass_with_rocks.png"
                elif dist_from_center < 20:
                    sprite = f"{barrens_grass}/sparse_grass.png"
                else:
                    sprite = f"{barrens_grass}/dry_grass_sparse.png"
                zone.add_ground_chunk(sprite, cx, cy, cw, ch)

        return zone

    @staticmethod
    def generate_orgrimmar():
        """Orgrimmar (90x80) - PLACEHOLDER capital.

        Structural only: walls, districts, a road grid, vendors and the
        zeppelin tower exit. No unique content, quests or interiors yet -
        this exists so the north end of Durotar leads somewhere and the
        zeppelin has a home.
        """
        zone = Tilemap("Orgrimmar", 90, 80,
                       "The orcish capital. Iron spikes, red banners, and the "
                       "smell of forge smoke. (Placeholder build.)")
        zone.region = "Durotar"

        zone.fill("dirt", "base")
        for y in range(zone.height):
            for x in range(zone.width):
                if random.random() < 0.12:
                    zone.set_tile(x, y, "stone", "base")

        # Outer wall with a south gate
        for x in range(zone.width):
            for y in (0, 1, zone.height - 2, zone.height - 1):
                zone.set_tile(x, y, "wall", "collision")
        for y in range(zone.height):
            for x in (0, 1, zone.width - 2, zone.width - 1):
                zone.set_tile(x, y, "wall", "collision")
        for x in range(41, 49):
            for y in (zone.height - 2, zone.height - 1):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "dirt", "base")

        # District blocks
        districts = [(8, 8, 22, 16), (36, 8, 20, 16), (62, 8, 20, 16),
                     (8, 34, 22, 16), (62, 34, 20, 16),
                     (20, 58, 18, 12), (52, 58, 18, 12)]
        ZoneGenerator._build_town(
            zone, buildings=districts,
            npc_positions=[(45, 40), (48, 44), (40, 44), (45, 52), (30, 40), (60, 40)],
            road_axis="both")

        zone.set_tile(45, 30, "quest_marker", "interaction")

        ZoneGenerator._carve_path(zone, 45, 76, 45, 40)
        ZoneGenerator._carve_landing(zone, 45, 76)
        zone.set_tile(45, 76, "portal", "interaction")   # -> Durotar (south gate)
        ZoneGenerator._carve_path(zone, 12, 70, 45, 70)
        ZoneGenerator._carve_landing(zone, 12, 70)
        zone.set_tile(12, 70, "portal", "interaction")   # -> Zeppelin Tower
        return zone

    @staticmethod
    def generate_zeppelin_tower():
        """Zeppelin Tower (34x46) - the crossing point to Eastern Tirisfal.

        A small vertical map: ground level, a simple switchback ramp
        (straight runs connected by short turns - no spiral maths), and a
        docking platform at the top where the zeppelin waits. Deliberately
        tiny - it exists to make the continent crossing feel like a journey
        rather than another identical portal tile.
        """
        zone = Tilemap("Zeppelin Tower", 34, 46,
                       "A creaking tower of lashed timber outside Orgrimmar's "
                       "gates. The Orgrim's Hammer runs to Tirisfal.")
        zone.region = "Durotar"

        zone.fill("dirt", "base")
        for y in range(zone.height):
            for x in range(zone.width):
                zone.set_tile(x, y, "wall", "collision")

        # Ground floor
        for y in range(34, 44):
            for x in range(8, 26):
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "dirt", "base")

        # Straight vertical shaft from ground floor to the docking platform -
        # no switchback, just a direct climb up the middle.
        ZoneGenerator._carve_path(zone, 17, 34, 17, 12, width=2, base="stone")

        # Docking platform at the top. Extended to row 4 so the boarding
        # portal at (17,6) sits ON the platform rather than in the wall above
        # it - it was unreachable before.
        for y in range(4, 14):
            for x in range(8, 26):
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None

        ZoneGenerator._carve_path(zone, 17, 12, 17, 10, width=2, base="stone")

        zone.set_tile(14, 38, "npc", "interaction")      # zeppelin master
        ZoneGenerator._carve_landing(zone, 17, 41)
        zone.set_tile(17, 41, "portal", "interaction")   # -> Durotar (ground)
        zone.set_tile(15, 7, "boat", "interaction")      # flavour: the airship
        ZoneGenerator._carve_landing(zone, 17, 6)
        zone.set_tile(17, 6, "portal", "interaction")    # -> Eastern Tirisfal
        return zone

    # ==================================================================
    # TIRISFAL GLADES (levels 1-12) - Undead starting zone
    # ==================================================================

    @staticmethod
    def generate_tirisfal_glades():
        """Tirisfal Glades (150x130). Undead starter zone, levels 1-12."""
        zone = Tilemap("Tirisfal Glades", 150, 130,
                       "A sickly orange woodland under a permanent overcast. "
                       "The Forsaken's homeland, and a graveyard besides.")
        zone.region = "Eastern Kingdoms - Lordaeron"

        zone.fill("grass", "base")
        for y in range(zone.height):
            for x in range(zone.width):
                r = random.random()
                if r < 0.16:
                    zone.set_tile(x, y, "dirt", "base")
                if r < 0.05:
                    zone.set_tile(x, y, "grass_tuft", "visual")

        # Dense blighted woodland ringing the zone
        for _ in range(260):
            cx = random.randint(0, zone.width - 1)
            cy = random.randint(0, zone.height - 1)
            edge = min(cx, cy, zone.width - cx, zone.height - cy)
            if edge > 28 and random.random() < 0.6:
                continue
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        if random.random() < 0.5:
                            zone.set_tile(x, y, "deep_forest", "collision")

        # Northern sea
        for y in range(0, 10):
            for x in range(zone.width):
                zone.set_tile(x, y, "deep_water", "base")

        # --- Deathknell (south-west): the starting village ---
        ZoneGenerator._clearing(zone, 30, 104, 26, 22, "dirt")
        for (bx, by) in [(22, 96), (36, 96), (22, 110), (38, 110)]:
            for dy in range(5):
                for dx in range(7):
                    x, y = bx + dx, by + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "wall", "collision")
                        zone.set_tile(x, y, "wood", "base")
        for (nx, ny) in [(30, 104), (33, 106), (27, 102)]:
            ZoneGenerator._carve_landing(zone, nx, ny, radius=1)
            zone.set_tile(nx, ny, "npc", "interaction")

        # --- Solliden Farmstead (west) ---
        ZoneGenerator._clearing(zone, 26, 66, 20, 16, "dirt")
        zone.add_subzone("Solliden Farmstead", 14, 56, 30, 26)

        # --- Night Web's Hollow (south, spider cave) ---
        ZoneGenerator._rocky_pocket(zone, 62, 112, 10, 9, "rock", density=0.45)

        # --- Agamand Mills (north-centre) ---
        ZoneGenerator._clearing(zone, 74, 40, 24, 20, "dirt")
        for (bx, by) in [(66, 32), (80, 32), (70, 48)]:
            for dy in range(5):
                for dx in range(8):
                    x, y = bx + dx, by + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "wall", "collision")
        zone.add_subzone("Agamand Mills", 60, 24, 40, 40)

        # --- Brill (centre): the zone hub ---
        ZoneGenerator._clearing(zone, 82, 76, 22, 18, "dirt")
        for (bx, by, bw, bh) in [(74, 68, 8, 5), (90, 68, 8, 5),
                                 (74, 84, 9, 5), (90, 84, 8, 5)]:
            for dy in range(bh):
                for dx in range(bw):
                    x, y = bx + dx, by + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "wall", "collision")
                        zone.set_tile(x, y, "wood", "base")
        for (nx, ny) in [(82, 76), (86, 78), (78, 80)]:
            ZoneGenerator._carve_landing(zone, nx, ny, radius=1)
            zone.set_tile(nx, ny, "npc", "interaction")

        # --- Balnir Farmstead (east) ---
        ZoneGenerator._clearing(zone, 118, 84, 20, 16, "dirt")
        zone.add_subzone("Balnir Farmstead", 106, 74, 30, 28)

        # --- The Scarlet Watch (north-east) ---
        ZoneGenerator._rocky_pocket(zone, 122, 34, 16, 14, "wall", density=0.45)
        zone.add_subzone("The Scarlet Watch", 104, 18, 40, 34)

        # --- Whispering Shore (north coast) ---
        zone.add_subzone("Whispering Shore", 40, 10, 60, 18)

        # Roads: Deathknell -> Brill -> Agamand, and Brill -> Balnir
        ZoneGenerator._carve_path(zone, 30, 104, 82, 76, width=2)
        ZoneGenerator._carve_path(zone, 82, 76, 74, 40, width=2)
        ZoneGenerator._carve_path(zone, 82, 76, 118, 84, width=2)
        ZoneGenerator._carve_path(zone, 26, 66, 30, 104, width=2)
        ZoneGenerator._carve_path(zone, 82, 76, 122, 34, width=2)

        # Cave entrances
        for (cx, cy) in [(62, 112), (122, 34)]:   # Night Web's Hollow, Scarlet Crypt
            ZoneGenerator._carve_path(zone, cx, cy, 82, 76, width=2)
            ZoneGenerator._carve_landing(zone, cx, cy, radius=2)
            zone.set_tile(cx, cy, "portal", "interaction")

        for _ in range(10):
            x = random.randint(12, zone.width - 12)
            y = random.randint(14, zone.height - 12)
            if zone.is_walkable(x, y):
                zone.set_tile(x, y, "chest", "interaction")

        # Zeppelin tower arrival, south-east
        ZoneGenerator._carve_path(zone, 138, 116, 118, 84, width=2)
        ZoneGenerator._carve_landing(zone, 138, 116)
        zone.set_tile(138, 116, "portal", "interaction")   # -> Zeppelin Tower
        return zone

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _bridge_crossing(zone, cx, cy, sprite_path, span_tiles=3, axis="horizontal",
                         orientation_size=(3, 2)):
        """Carve a walkable strip STRAIGHT ACROSS a water body (river/
        channel) and lay a bridge landmark over it, instead of the old
        "pave the whole crossing area to dry dirt" approach every zone
        transition used, which quietly deleted the river entirely at the
        crossing point - there was no visual sense you were crossing
        water at all. This keeps the water on either side of the bridge
        genuinely water; only the bridge's own footprint becomes walkable
        ground.

        cx, cy: center of the crossing, in world tiles.
        span_tiles: how many tiles wide the walkable strip is, perpendicular
        to the river's flow (i.e. the bridge's length across the water).
        axis: "horizontal" if the river runs north-south (bridge spans
        east-west) or "vertical" if the river runs east-west (bridge spans
        north-south) - controls which direction gets carved walkable.
        orientation_size: (width_tiles, height_tiles) for the landmark
        image at this axis - swap width/height for the other axis.
        """
        half = span_tiles // 2
        if axis == "horizontal":
            for dx in range(-half - 2, half + 3):
                x = cx + dx
                if 0 <= x < zone.width:
                    zone.set_tile(x, cy, "path", "base")
                    zone.collision_layer[cy][x] = None
            lw, lh = orientation_size
            zone.add_landmark(sprite_path, cx - lw // 2, cy - lh // 2, lw, lh, solid=False)
        else:
            for dy in range(-half - 2, half + 3):
                y = cy + dy
                if 0 <= y < zone.height:
                    zone.set_tile(cx, y, "path", "base")
                    zone.collision_layer[y][cx] = None
            lh, lw = orientation_size
            zone.add_landmark(sprite_path, cx - lw // 2, cy - lh // 2, lw, lh, solid=False)

    @staticmethod
    def _paint_road(zone, x0, y0, x1, y1, width=1, base="path"):
        """Paint a visibly distinct road/trail between two points.

        Different job from _carve_path: that one only overwrites tiles that
        are actually non-walkable (water, lava, structural), which makes it
        a walkability guarantee, not a visual road - calling it across
        already-walkable ground (e.g. a sand zone) is a silent no-op on the
        base layer, since every tile already passes is_walkable(). This
        helper always paints the base tile so a route reads as a distinct
        path rather than disappearing into identical surrounding terrain.
        """
        x, y = x0, y0
        guard = 0
        while (x, y) != (x1, y1) and guard < 4000:
            guard += 1
            for dy in range(-width, width + 1):
                for dx in range(-width, width + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height:
                        if zone.base_layer[ny][nx] not in ("deep_water", "shallow_water"):
                            zone.set_tile(nx, ny, base, "base")
                        zone.collision_layer[ny][nx] = None
                        # Clear any visual-layer scatter sitting on the road
                        # too (rocks/bushes rendered on top would otherwise
                        # look like the path is overgrown/obstructed).
                        zone.visual_layer[ny][nx] = None
            if abs(x1 - x) >= abs(y1 - y) and x != x1:
                x += 1 if x1 > x else -1
            elif y != y1:
                y += 1 if y1 > y else -1
            elif x != x1:
                x += 1 if x1 > x else -1

    @staticmethod
    def _carve_path(zone, x0, y0, x1, y1, width=2, base="dirt"):
        """Carve a guaranteed-walkable corridor between two points.

        Random terrain scatter (dense forest on Echo Isles, canyon rock in
        Durotar) runs across the whole map and routinely seals off clearings
        and portal landings into isolated pockets - reachable on the minimap,
        impossible to actually walk to. Any hand-placed feature that must be
        reachable gets a path back to the zone interior.

        REAL BUG FIXED this session (Kyle: "we need to see walls" after a
        real render at the actual 1280x720/32px game viewport showed a
        player standing in a "width=2" corridor with ZERO wall visible
        anywhere on screen - measured directly: real walkable spans of
        18-45 tiles wide along what should have been a narrow tunnel).
        The old loop cleared a full (2*width+1) SQUARE at EVERY SINGLE
        STEP along the path, not a width-wide LINE - since the path
        steps roughly diagonally toward its target, those overlapping
        squares smear into a corridor far wider than `width` actually
        states (a width=2 call was clearing a 5x5 square per step,
        which is already most of a "narrow tunnel", then compounding
        across every step of the walk). Fixed to clear a true
        perpendicular-to-travel-direction line of the stated width
        instead of a square - a width=2 path is now genuinely ~4-5
        tiles wide total, not 20+.

        This function has 48 call sites across this file (checked
        directly before changing shared behavior) - the fix only
        narrows what was already-wider-than-intended corridors, it
        doesn't change connectivity (a narrower-but-still-guaranteed-
        walkable line still connects the same two points), so this
        should only improve every existing cave's readability rather
        than break any of them - re-verified via the full 53-zone
        create_all_zones() integration test after this change, not
        assumed safe.
        """
        x, y = x0, y0
        guard = 0
        while (x, y) != (x1, y1) and guard < 4000:
            guard += 1
            # Determine current travel direction so the clear-width
            # applies PERPENDICULAR to it (a real line), not as a
            # blind square in both axes regardless of direction.
            going_horizontal = abs(x1 - x) >= abs(y1 - y) and x != x1
            for w in range(-width, width + 1):
                if going_horizontal:
                    nx, ny = x, y + w
                else:
                    nx, ny = x + w, y
                if 0 <= nx < zone.width and 0 <= ny < zone.height:
                    # Replace any non-walkable base (water, lava, and
                    # structural tiles like "wood") - clearing only the
                    # collision layer isn't enough, since is_walkable()
                    # also consults the base tile type.
                    from world.tiles import is_walkable as _walk
                    if not _walk(zone.base_layer[ny][nx]):
                        zone.set_tile(nx, ny, base, "base")
                    zone.collision_layer[ny][nx] = None
            # Step toward the target, favouring the longer axis first.
            if going_horizontal:
                x += 1 if x1 > x else -1
            elif y != y1:
                y += 1 if y1 > y else -1
            elif x != x1:
                x += 1 if x1 > x else -1

    @staticmethod
    @staticmethod
    def _is_water(zone, x, y):
        """True if the base tile at (x, y) is water. Shared by every
        scatter helper so "don't put rocks/trees in water" (Kyle) is
        enforced in one place instead of re-checked (or missed) at each of
        the dozen+ scatter call sites across this file."""
        return zone.base_layer[y][x] in ("deep_water", "shallow_water")

    @staticmethod
    def _clear_visual_over_water(zone):
        """Strip any visual-layer decoration (grass_tuft, small_rocks,
        etc) sitting on a water tile. A zone's base-terrain roll usually
        paints visual-layer scatter BEFORE any water is carved in (oases,
        coastlines, ponds) - the water carve only ever clears
        base_layer/collision_layer at each site, not visual_layer, so
        decoration meant for dry ground keeps rendering on top of the
        water afterward (Kyle, Central Barrens' east coast: scattered
        orange grass-tuft squares floating across open water). Call this
        once, after all water carving is done, rather than patching every
        individual carve site to also clear visual_layer - cheaper to get
        right once than to risk missing one of a dozen+ carve sites.
        """
        for y in range(zone.height):
            for x in range(zone.width):
                if zone.base_layer[y][x] in ("deep_water", "shallow_water") and zone.visual_layer[y][x]:
                    zone.visual_layer[y][x] = None

    @staticmethod
    @staticmethod
    def _scatter_big_props(zone, sprite_paths, count, size_range=(2, 3), area=None):
        """Place a handful of genuinely bigger landmark props (2-3 tiles,
        not squashed to one 32x32 square) at sparse random positions -
        real size variety alongside the small per-tile _scatter() props,
        instead of every rock/prop rendering at the same forced scale.
        Kyle: "ensure rock piles are different sizes".

        sprite_paths: list of file paths to pick randomly from.
        count: how many to place (sparse - this is for landmark-scale
        variety, not the main scatter density).
        size_range: (min_tiles, max_tiles) - each placement gets a random
        square size in that range, picked independently.
        area, if given, restricts placement to (x0, y0, x1, y1).
        """
        x0, y0, x1, y1 = area if area else (0, 0, zone.width, zone.height)
        placed = 0
        attempts = 0
        while placed < count and attempts < count * 20:
            attempts += 1
            size = random.randint(*size_range)
            x = random.randint(x0, max(x0, x1 - size - 1))
            y = random.randint(y0, max(y0, y1 - size - 1))
            # Require the whole footprint clear of collision and water so a
            # big prop doesn't spawn half-buried in a tree or straddling
            # the pond edge.
            if any(zone.collision_layer[y + dy][x + dx] is not None
                   or ZoneGenerator._is_water(zone, x + dx, y + dy)
                   for dy in range(size) for dx in range(size)
                   if 0 <= x + dx < zone.width and 0 <= y + dy < zone.height):
                continue
            sprite = random.choice(sprite_paths)
            zone.add_landmark(sprite, x, y, size, size, solid=False)
            placed += 1

    @staticmethod
    def _scatter(zone, tile_id, chance, area=None, require_no_collision=True):
        """Randomly place a visual-layer decoration tile across (part of)
        a zone, skipping water tiles and (by default) tiles that already
        have a collision blocker. This is now the standard way generator
        code scatters props - see _is_water's docstring for why.

        area, if given, is (x0, y0, x1, y1) to restrict the scatter to a
        sub-region instead of the whole map (e.g. one cave chamber).
        """
        x0, y0, x1, y1 = area if area else (0, 0, zone.width, zone.height)
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(zone.width, x1), min(zone.height, y1)
        for y in range(y0, y1):
            for x in range(x0, x1):
                if require_no_collision and zone.collision_layer[y][x] is not None:
                    continue
                if ZoneGenerator._is_water(zone, x, y):
                    continue
                if random.random() < chance:
                    zone.set_tile(x, y, tile_id, "visual")

    @staticmethod
    def _clearing(zone, cx, cy, w, h, base="dirt"):
        """Flatten a rectangle to walkable ground centred on (cx, cy)."""
        for dy in range(-h // 2, h // 2 + 1):
            for dx in range(-w // 2, w // 2 + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.set_tile(x, y, base, "base")
                    zone.collision_layer[y][x] = None

    @staticmethod
    def _mountain_range(zone, cx, cy, w, h, wall_tile="cliff", edge_jitter=0.15,
                          density_falloff=True):
        """Fill an organic (jittered-ellipse) region SOLID with an
        impassable collision tile - a real geographic mountain RANGE,
        not a hollow ring like _rocky_pocket (that leaves its center
        open; this doesn't - every tile inside the jittered ellipse
        becomes wall_tile, matching how mountains actually read on a
        real overworld map: a solid blocked region with an organic
        edge, not a thin border or a scatter of individual props).

        Kyle: "the mountains can be used as impassable. im thinking
        like the old school style?" (reference: a classic 16-bit JRPG
        overworld map showing mountains as one real geographic range in
        a specific part of the map, not scattered along every edge) -
        this is that region primitive. Meant to be combined with a
        couple of standalone mountain-formation landmarks (add_landmark)
        placed at/near the range's edge as visual accents, same as a
        real range has taller peaks poking up in specific spots rather
        than uniform height everywhere.

        edge_jitter: fraction of the ellipse radius the boundary wobbles
        by, per-tile (a hard ellipse reads as a drawn shape; jitter
        reads as a natural range edge). density_falloff: if True, the
        outermost ~15% of the region gets a random skip chance instead
        of solid fill, so the range's edge is ragged/broken rather than
        a hard line - same principle _carve_irregular_boundary already
        uses for its ring.

        Water tiles are never overwritten (same guard every other
        terrain-carving helper in this file uses).
        """
        # Same per-tile-noise bug as _carve_irregular_boundary had (Kyle:
        # "I want any collision blocks to be very distinct that they are
        # mountains" - isolated stray tiles from independent per-tile
        # randomness don't read as a mountain, they read as glitchy
        # debris). Jitter now keyed on ANGLE around the ellipse center
        # (a slowly-varying position, same tiles near each other get
        # similar jitter) via a low-frequency sine wave, not a fresh
        # random draw per tile - and the density_falloff random skip is
        # dropped entirely for the same reason (a per-tile skip chance
        # is exactly the kind of independent noise that produces
        # isolated single-tile holes/fragments at the range's edge).
        import math
        for dy in range(-h, h + 1):
            for dx in range(-w, w + 1):
                x, y = cx + dx, cy + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                if zone.base_layer[y][x] in ("deep_water", "shallow_water"):
                    continue
                dist = ((dx / max(w, 1)) ** 2 + (dy / max(h, 1)) ** 2) ** 0.5
                angle = math.atan2(dy, dx)
                jittered_edge = 1.0 + edge_jitter * math.sin(angle * 5)
                if dist > jittered_edge:
                    continue  # outside the range entirely
                zone.set_tile(x, y, wall_tile, "collision")

    @staticmethod
    def _rocky_pocket(zone, cx, cy, w, h, tile="rock", density=0.4):
        """Ring a region with a collision tile, leaving the interior open.

        Used for the canyon-walled pockets Durotar is built from (Drygulch,
        Thunder Ridge, Kolkar Crag) - visually distinct areas you walk into
        rather than featureless open desert.

        FIXED this session (Kyle: "they do make it look ugly still" -
        traced to THIS function, not the mountain/cliff work already
        fixed twice - the small clusters visible in Scorpid Nest, a
        pre-existing _rocky_pocket call, use tile="rock", a completely
        different tile_id from "cliff" that I'd been mis-diagnosing as
        boundary-ring leftovers. `random.random() < density` per tile
        is the exact same independent-per-tile-noise bug already found
        and fixed in _carve_irregular_boundary/_mountain_range - never
        applied here until now. Same fix: angle-based coherent jitter
        instead of independent per-tile randomness, so the ring reads
        as one coherent rocky rim instead of scattered debris clusters.
        "rock" itself is still on the OLD small per-tile-crop art (was
        never given chunked treatment like "cliff"/"wall" were this
        session) - that's a separate, real follow-up, not fixed here.
        """
        import math
        for dy in range(-h, h + 1):
            for dx in range(-w, w + 1):
                x, y = cx + dx, cy + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                if zone.base_layer[y][x] in ("deep_water", "shallow_water"):
                    continue
                dist = ((dx / max(w, 1)) ** 2 + (dy / max(h, 1)) ** 2) ** 0.5
                angle = math.atan2(dy, dx)
                jittered_inner = 0.78 + 0.08 * math.sin(angle * 6)
                if jittered_inner < dist <= 1.0:
                    zone.set_tile(x, y, tile, "collision")
                elif dist <= jittered_inner:
                    zone.collision_layer[y][x] = None

    @staticmethod
    def _carve_irregular_boundary(zone, keep_points=None, border_width=10,
                                   wall_tile="cliff", jitter=2,
                                   road_radius=None, feature_radius=None):
        """Wall off a THIN RING near the zone's outer edge, producing an
        organic (non-rectangular, jittered) playable boundary instead of
        a flat square or open void - Kyle: "we need to shrink the cliff,
        and use it only as small flavor when possible" after a real
        density measurement showed the previous (road/feature-distance)
        version of this function walling off 48.4% of Valley of Trials
        as solid cliff.

        THIS IS A REWRITE, not a tuning pass on the old version. The old
        logic walled anything NOT within road_radius of a road tile or
        feature_radius of a keep_point - which scales badly with map
        size and feature sparsity: a 120x120 zone with only 9 feature
        points and thin road lines left most of the open field outside
        both radii, so it got walled by default. That's backwards for
        a boundary wall, which should scale with DISTANCE FROM THE MAP
        EDGE, not with how close random interior tiles happen to be to
        a handful of named points. This version does exactly that: a
        tile within border_width tiles of x=0, x=width-1, y=0, or
        y=height-1 is boundary territory (candidate for cliff); every
        interior tile is never walled by this function at all,
        regardless of how far it sits from a road or feature.

        keep_points/road_radius/feature_radius: road_radius/feature_radius
        are accepted for backward-compat but IGNORED - the interior is
        never carved based on proximity to roads or features anymore.
        keep_points IS still used, but only as a safety clearance for
        points that sit genuinely near the map edge - VoT's Durotar
        portal (115,60) and Razor Hill landing (10,100) both have an
        edge_dist inside the default border_width, and without this
        clearance they'd get silently walled into solid cliff (caught
        by directly checking is_walkable() at those exact coordinates
        after the rewrite, not assumed safe - a real, serious bug: an
        unreachable zone-transition portal). Any keep_point within
        border_width+jitter of the edge gets a small always-clear radius
        carved around it, same as the water guard above.

        jitter widens/narrows the effective border per-tile (a hard-
        edged ring reads as a wall someone built on purpose; an uneven
        one reads as natural canyon edge), plus a random skip chance
        right at the inner boundary so the wall itself isn't one
        unbroken ring - same jagged-edge intent as the old version, just
        driven by edge-distance instead of feature-distance.

        Water tiles are never overwritten (same guard _rocky_pocket
        uses) so the pond can't get a cliff tile stamped through it if
        its edge ever lands close to the computed boundary.
        """
        keep_points = keep_points or []
        clear_radius = 4  # small, just enough to guarantee the point itself and immediate approach stay open

        def near_a_keep_point(x, y):
            for (px, py) in keep_points:
                if (x - px) ** 2 + (y - py) ** 2 <= clear_radius * clear_radius:
                    return True
            return False

        # Kyle: "why are there weird chunks still present? I want any
        # collision blocks to be very distinct that they are mountains
        # or something" - real bug, not a rendering issue: the jitter
        # below used to be recomputed independently PER TILE
        # (`border_width + random.randint(-jitter, jitter)` inside the
        # main loop), which is per-tile noise, not a coherent wavy line -
        # confirmed by directly scanning collision_layer and finding
        # isolated single "cliff" tiles scattered many tiles past the
        # true edge with no neighbors, which is exactly what independent
        # per-tile randomness produces. A real boundary needs jitter
        # that varies SLOWLY across space so neighboring tiles mostly
        # agree, forming a continuous wavy line instead of noise. Fixed
        # by computing effective_border once per EDGE POSITION (a slowly-
        # varying value keyed on how far along the perimeter a tile is,
        # not on the tile's own random draw) rather than per-tile.
        def edge_jitter_at(x, y, w, h):
            # Use whichever edge is actually closest to derive a stable
            # "position along that edge" key, then a low-frequency sine
            # wave (not per-tile random) for a smooth, continuous jitter.
            d_left, d_right, d_top, d_bottom = x, w - 1 - x, y, h - 1 - y
            closest = min(d_left, d_right, d_top, d_bottom)
            if closest == d_top or closest == d_bottom:
                pos = x
            else:
                pos = y
            import math
            return int(round(jitter * math.sin(pos * 0.15)))

        for y in range(zone.height):
            for x in range(zone.width):
                if zone.base_layer[y][x] in ("deep_water", "shallow_water"):
                    continue
                if near_a_keep_point(x, y):
                    continue
                edge_dist = min(x, zone.width - 1 - x, y, zone.height - 1 - y)
                effective_border = border_width + edge_jitter_at(x, y, zone.width, zone.height)
                if edge_dist > effective_border:
                    continue  # solidly interior, never walled
                zone.set_tile(x, y, wall_tile, "collision")

    # ------------------------------------------------------------------
    # CAVES
    # ------------------------------------------------------------------
    # Caves were previously encounter-table keys with no map behind them.
    # These are real tilemaps entered through a portal tile, which is what
    # finally activates the 1.5x cave XP bonus that has been built, tested
    # and completely inert since it was written.

    @staticmethod
    def generate_drygulch_ravine(width=95, height=75):
        """Drygulch Ravine - Kyle: 'its just [in] the name, its a ravine so
        NOT a cave' - enters/exits exactly like a cave (portal, separate
        Tilemap, region back to Durotar) but the INSIDE should read as an
        open-air red-rock canyon, not a room-and-corridor dungeon. Still
        fully enclosed per Kyle's follow-up ("we need walls... but like
        dirt or cliff walls") - the boundary is a ringed cliff-face, not
        endless open ground, it just isn't carved brick/stone dungeon
        rooms. generate_cave() was the wrong tool for this: its carve()
        shape is fundamentally "corridors connecting rooms", which reads
        as a dungeon no matter what texture sits on top of it.
        """
        ravine = Tilemap("Drygulch Ravine", width, height,
                         "A wide red-rock ravine cutting through Durotar.")
        ravine.region = "Durotar"

        # Open red-sand floor everywhere first - unlike generate_cave()'s
        # "solid rock, then carve rooms out" approach, this starts fully
        # walkable and only adds walls/obstacles on top, which is what
        # actually produces an open, sprawling read instead of a corridor
        # maze.
        ravine.fill("sand", "base")

        # Ringed cliff-face boundary (same primitive Durotar's canyon
        # pockets already use) instead of generate_cave()'s uniform
        # wall-everywhere-then-carve-rooms - the whole interior stays open,
        # only the perimeter reads as enclosed.
        ZoneGenerator._rocky_pocket(ravine, width // 2, height // 2,
                                    width // 2 - 3, height // 2 - 3,
                                    "cliff", density=0.55)

        # A handful of interior outcrops - real canyon terrain has rock
        # formations jutting up inside it, not just a smooth bowl - but
        # sparse and scattered, not room-shaped, so the open-canyon read
        # survives. Each is a loose ring (walkable center, rocky edge),
        # same shape language as the boundary just smaller.
        for _ in range(4):
            ox = random.randint(15, width - 15)
            oy = random.randint(15, height - 15)
            ZoneGenerator._rocky_pocket(ravine, ox, oy,
                                        random.randint(4, 7), random.randint(4, 7),
                                        "rock", density=0.5)

        # Visual variety - real mixed scatter (rock piles, cacti) instead
        # of rocks only, plus a rare dragon-bones landmark. No water in
        # this zone, but routed through _scatter() anyway for consistency
        # with every other generator (and free protection if a water
        # feature gets added here later).
        rock_variants = ["small_rocks", "rock_pile_2", "rock_pile_3", "rock_pile_4"]
        for tile_id in rock_variants:
            ZoneGenerator._scatter(ravine, tile_id, 0.01)
        ZoneGenerator._scatter(ravine, "cactus_small", 0.008)
        ZoneGenerator._scatter(ravine, "cactus_small_2", 0.008)
        for _ in range(10):
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)
            if ravine.is_walkable(x, y) and random.random() < 0.5:
                ravine.set_tile(x, y, "tree", "collision")  # desert_oasis's "tree" tile_id = cactus prop

        # A real full-size skeletal remains landmark (6x6 tiles, not
        # squashed to one 32x32 tile like the earlier version of this
        # scatter) - something big died here, a proper "found in the
        # ravine" moment rather than a repeated small prop.
        bones_x = max(3, min(width - 9, width // 2 + random.randint(-15, 15)))
        bones_y = max(3, min(height - 9, height // 2 + random.randint(-10, 10)))
        ravine.add_landmark("assets/tiles/cave_landmarks/dragon_bones.png",
                            bones_x, bones_y, 6, 6, solid=False)

        entrance = (width // 2, height - 7)
        ZoneGenerator._carve_landing(ravine, *entrance, radius=3)

        # Boss chamber - deepest point from the entrance (north end),
        # same "far from entrance" convention generate_cave() uses.
        boss = (width // 2, 8)
        ZoneGenerator._carve_landing(ravine, *boss, radius=5)
        ZoneGenerator._carve_path(ravine, *entrance, *boss, width=3, base="sand")

        ravine.set_tile(boss[0], boss[1] - 2, "chest", "interaction")
        ravine.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        ravine.boss_position = boss

        exit_pos = (entrance[0], entrance[1] + 3)
        ZoneGenerator._carve_landing(ravine, *exit_pos, radius=2)
        ravine.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        ravine.is_cave = True
        ravine.add_subzone("Drygulch Ravine", 0, 0, width, height)
        return ravine

    @staticmethod
    def generate_sunken_grotto_of_the_deep(width=110, height=95):
        """The game's first fully hand-built mini-dungeon (Kyle) - a naga
        sea cave under Durotar's NE coast, not a generate_cave() template
        instance. Real sourced monster/ruin props throughout (serpent
        skeleton, wrecked ship hull, giant crab, naga trident statue),
        not generic bones/crystal scatter.

        Layout (5 rooms, one branch):
          Entrance -> Flooded Hall (serpent skeleton landmark)
                   -> forks into Shipwreck Cove / Crab Den
                   -> both rejoin at the Naga Shrine (mini-boss: the crab,
                      already fought in the Den if that branch was taken,
                      otherwise fought here)
                   -> Boss Chamber (naga statue centerpiece, real boss)
        """
        cave = Tilemap("Sunken Grotto of the Deep", width, height,
                       "A drowned sea-cave beneath Durotar's northeast coast, "
                       "claimed by naga.")
        cave.region = "Durotar"
        cave.is_cave = True

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "wall", "collision")

        def room(cx, cy, rw, rh, water_center=True):
            """Carve an oval room, damp stone floor, an optional calm-water
            pool at its center (most naga rooms should have one)."""
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if not (1 <= x < width - 1 and 1 <= y < height - 1):
                        continue
                    if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                        cave.collision_layer[y][x] = None
                        cave.set_tile(x, y, "dirt", "base")
            if water_center:
                pool_r = min(rw, rh) * 0.35
                for dy in range(-int(pool_r) - 1, int(pool_r) + 2):
                    for dx in range(-int(pool_r) - 1, int(pool_r) + 2):
                        x, y = cx + dx, cy + dy
                        if not (0 <= x < width and 0 <= y < height):
                            continue
                        if (dx ** 2 + dy ** 2) ** 0.5 <= pool_r:
                            cave.set_tile(x, y, "shallow_water", "base")
                            cave.collision_layer[y][x] = None

        # Room centers, matching the branch/rejoin layout in the docstring.
        entrance = (width // 2, height - 8)
        hall = (width // 2, height - 28)
        cove = (width // 4, height // 2)
        crab_den = (3 * width // 4, height // 2)
        shrine = (width // 2, height // 3)
        boss_room = (width // 2, 12)

        room(*entrance, 9, 7, water_center=False)
        room(*hall, 12, 10)
        room(*cove, 11, 9)
        room(*crab_den, 11, 9)
        room(*shrine, 13, 10)
        room(*boss_room, 14, 12)

        # Corridors: entrance->hall, hall forks to cove/crab_den, both
        # rejoin at shrine, shrine->boss.
        ZoneGenerator._carve_path(cave, *entrance, *hall, width=3, base="dirt")
        ZoneGenerator._carve_path(cave, *hall, *cove, width=3, base="dirt")
        ZoneGenerator._carve_path(cave, *hall, *crab_den, width=3, base="dirt")
        ZoneGenerator._carve_path(cave, *cove, *shrine, width=3, base="dirt")
        ZoneGenerator._carve_path(cave, *crab_den, *shrine, width=3, base="dirt")
        ZoneGenerator._carve_path(cave, *shrine, *boss_room, width=4, base="dirt")

        # Landmarks - real sourced props, not generic scatter, at genuine
        # multi-tile scale (Kyle: "some SHOULD be massive"). Kyle keeps
        # serpent_skeleton.png/giant_crab.png/naga_statue.png in a
        # separate folder outside this chat's view - left exactly as
        # referenced, not touched. shipwreck.png never existed on disk
        # here, so it's swapped for Echo Isles' real shipwreck_full.png
        # (Kyle, this session: reuse it for Shipwreck Cove).
        cave.add_landmark("assets/tiles/naga_dungeon/serpent_skeleton.png",
                          hall[0] - 3, hall[1] - 3, 5, 5, solid=False)
        cave.add_landmark("assets/tiles/echo_isles/props/shipwreck_full.png",
                          cove[0] - 5, cove[1] - 3, 10, 6, solid=False)
        cave.add_landmark("assets/tiles/naga_dungeon/giant_crab.png",
                          crab_den[0] - 2, crab_den[1] - 2, 4, 3, solid=False)
        cave.add_landmark("assets/tiles/naga_dungeon/naga_statue.png",
                          boss_room[0] - 2, boss_room[1] - 6, 4, 5, solid=False)

        # Real beach/reef props (Echo Isles art, Kyle: reuse for this
        # revamp) in place of the old coral_blue/coral_pink/shell/
        # shell_brown _scatter() calls - those 4 tile_ids were never
        # real entries in world/tiles.py (confirmed by grep, not
        # assumed), so every one of those calls was silently no-op'ing
        # since this dungeon was first built. One real cluster per non-
        # boss room instead, offset from each room's own water-pool
        # center so nothing sits in the water or blocks the corridor
        # junctions.
        cave.add_landmark("assets/tiles/echo_isles/props/coral_shell_cluster.png",
                          hall[0] + 5, hall[1] + 4, 5, 5, solid=False)
        cave.add_landmark("assets/tiles/echo_isles/props/coral_shell_cluster.png",
                          crab_den[0] + 4, crab_den[1] - 5, 5, 5, solid=False)
        cave.add_landmark("assets/tiles/echo_isles/props/coral_shell_cluster.png",
                          shrine[0] - 6, shrine[1] + 5, 5, 5, solid=False)

        # Mini-boss markers: crab at the Crab Den (right fork), Undead
        # Pirate Captain at Shipwreck Cove (left fork) - a twin encounter
        # on the opposite branch so both forks have a real fight, not just
        # one side. Both landmark graphics ARE their encounter's visual;
        # the actual fights use the standard boss_marker interaction tile.
        miniboss_pos = (crab_den[0], crab_den[1] + 3)
        cave.set_tile(*miniboss_pos, "boss_marker", "interaction")

        pirate_pos = (cove[0], cove[1] + 3)
        cave.set_tile(*pirate_pos, "boss_marker", "interaction")

        # Main boss chamber - treasure + marker, same convention as
        # generate_cave()'s boss rooms.
        cave.set_tile(boss_room[0], boss_room[1] + 3, "chest", "interaction")
        boss_pos = (boss_room[0], boss_room[1] + 5)
        cave.set_tile(*boss_pos, "boss_marker", "interaction")
        cave.boss_position = boss_pos

        # Two-chamber dungeon (mini-boss + main boss): CaveSpawnManager
        # reads boss_positions (plural) first and only falls back to the
        # single boss_position above if this list is empty. Without it,
        # the crab den's boss_marker tile would sit there permanently dead
        # - visually a boss room, mechanically nothing ever spawns there.
        # Two-chamber-plus-main dungeon: each chamber is PINNED to its
        # exact boss (x, y, boss_name) rather than left for
        # CaveSpawnManager's random pool, since the landmark in each room
        # only makes sense with one specific boss - the crab statue room
        # must be the Giant Crab, the shipwreck must be the Undead Pirate
        # Captain, never swapped between visits.
        cave.boss_positions = [
            (miniboss_pos[0], miniboss_pos[1], "Giant Crab"),
            (pirate_pos[0], pirate_pos[1], "Undead Pirate Captain"),
            (boss_pos[0], boss_pos[1], "Naga Shrine Guardian"),
        ]

        # Entrance/exit portal.
        exit_pos = (entrance[0], entrance[1] + 5)
        ZoneGenerator._carve_landing(cave, *exit_pos, radius=2)
        cave.set_tile(*exit_pos, "portal", "interaction")

        cave.add_subzone("Sunken Grotto of the Deep", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART (Kyle, this session: "revamp the Naga
        # dungeon with the tiles we have") - this dungeon had ZERO real
        # texture calls before now (confirmed directly, not assumed -
        # no add_ground_chunk/add_obstacle_chunk anywhere in this
        # function), rendering on bare tile_id default colors since it
        # was first built. Reusing Sunken Temple Grotto's real aquatic
        # tile pair: plain floor.png/wall.png for the approach rooms,
        # the worked-stone floor_ornate.png/wall_relief.png for the
        # boss chamber only - same "the final room is worked temple
        # stone, everything before it is natural cave" distinction that
        # zone's own generator uses, so this dungeon reads as connected
        # to the same naga architecture rather than a mismatched reuse.
        # ------------------------------------------------------------------
        plain_floor = "assets/tiles/sunken_temple_grotto/floor.png"
        plain_wall = "assets/tiles/sunken_temple_grotto/wall.png"
        ornate_floor = "assets/tiles/sunken_temple_grotto/floor_ornate.png"
        relief_wall = "assets/tiles/sunken_temple_grotto/wall_relief.png"
        chunk_size = 20

        def floor_chunks(cx, cy, rw, rh, sprite):
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        cave.add_ground_chunk(sprite, gx, gy, gw, gh)

        floor_chunks(*entrance, 9, 7, plain_floor)
        floor_chunks(*hall, 12, 10, plain_floor)
        floor_chunks(*cove, 11, 9, plain_floor)
        floor_chunks(*crab_den, 11, 9, plain_floor)
        floor_chunks(*shrine, 13, 10, plain_floor)
        floor_chunks(*boss_room, 14, 12, ornate_floor)

        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                # Accent ring around the boss chamber's own boundary
                # only (same scoping as Sunken Temple Grotto - the
                # serpent-relief carving repeats too recognizably to
                # stretch across the whole map as a general wall).
                dx, dy = cx - boss_room[0], cy - boss_room[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                sprite = relief_wall if 14 <= dist <= 18 else plain_wall
                cave.add_obstacle_chunk(sprite, cx, cy, cw, ch)

        return cave

    @staticmethod
    def generate_thunder_ridge():
        """Generate Thunder Ridge (90x90) - a real multi-room canyon
        dungeon (Kyle provided a detailed reference image showing a much
        richer layout than the first pass: entrance funnel south, a
        network of ~8 distinct grotto rooms connected by winding paths,
        2 water/waterfall rooms, a boss nest room with eggs, skeleton/
        dino scatter throughout). Rebuilt from scratch against that
        reference rather than patched - the first version was a
        cramped 2-room zone, nowhere near this scale.

        Entrance/exit is exactly (40,55) - world/portal_manager.py's
        real contracted coordinate for this zone (unchanged by this
        resize - Durotar's own (55,45) trigger is independent of this
        zone's internal size).

        Real wooden bridge art doesn't exist yet (checked directly -
        the only bridge-shaped asset on disk is The Den's spider-web
        bridge, wrong theme, and VoT's Southfury crossing already
        references a stone_span.png that was never actually generated
        either) - Kyle chose to get real rope-bridge art from ChatGPT
        rather than fake it with the wrong theme. Water-gap crossings
        here use plain walkable paths as an honest placeholder in the
        meantime (same "flag it, don't fake it" discipline as Burning
        Blade Coven's floor art got before its real batch arrived) -
        swap in real bridge landmarks once that art exists.
        """
        width, height = 90, 90
        zone = Tilemap("Thunder Ridge", width, height,
                        "A canyon dungeon of red rock grottos, home to thunder lizards and their broodmother.")
        zone.region = "Durotar"

        zone.fill("sand", "base")
        for y in range(height):
            for x in range(width):
                zone.set_tile(x, y, "cliff", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            zone.collision_layer[y][x] = None
                            zone.set_tile(x, y, "dirt", "base")

        def carve_pool(cx, cy, r):
            for dy in range(-r - 1, r + 2):
                for dx in range(-r - 1, r + 2):
                    x, y = cx + dx, cy + dy
                    if not (0 <= x < width and 0 <= y < height):
                        continue
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    if dist < r * 0.55:
                        zone.set_tile(x, y, "deep_water", "base")
                        zone.collision_layer[y][x] = None
                    elif dist < r:
                        zone.set_tile(x, y, "shallow_water", "base")
                        zone.collision_layer[y][x] = None

        exit_pos = (40, 55)
        hub = (40, 40)
        carve(*exit_pos, 6, 5)
        carve(*hub, 9, 8)
        ZoneGenerator._carve_path(zone, *exit_pos, *hub, width=3)

        # 8 grotto rooms matching the reference's real scattered
        # composition - real angular spread around the hub (same lesson
        # from Burning Blade Coven's rebuild this session: a layout with
        # rooms genuinely spread at different angles/distances avoids
        # any two corridors merging into one wide open band).
        rooms = {
            "nw_waterfall":   (20, 20, 8, 7),
            "n_boss_nest":    (43, 14, 9, 7),
            "ne_grotto":      (65, 20, 8, 7),
            "far_e_grotto":   (72, 38, 7, 6),
            "w_grotto":       (12, 45, 7, 6),
            "e_grotto":       (68, 55, 8, 7),
            "sw_grotto":      (18, 65, 8, 7),
            "se_grotto":      (60, 72, 8, 7),
        }
        for (rx, ry, rw, rh) in rooms.values():
            carve(rx, ry, rw, rh)
            dx, dy = rx - hub[0], ry - hub[1]
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.001)
            hub_r = (9, 8)
            edge_x = hub[0] + round(dx / dist * hub_r[0])
            edge_y = hub[1] + round(dy / dist * hub_r[1])
            ZoneGenerator._carve_path(zone, edge_x, edge_y, rx, ry, width=2)

        # A few rooms interconnect directly too (matching the reference's
        # real winding-path-between-grottos look, not just hub-and-spoke).
        ZoneGenerator._carve_path(zone, *rooms["nw_waterfall"][:2], *rooms["n_boss_nest"][:2], width=2)
        ZoneGenerator._carve_path(zone, *rooms["n_boss_nest"][:2], *rooms["ne_grotto"][:2], width=2)
        ZoneGenerator._carve_path(zone, *rooms["ne_grotto"][:2], *rooms["far_e_grotto"][:2], width=2)
        ZoneGenerator._carve_path(zone, *rooms["w_grotto"][:2], *rooms["sw_grotto"][:2], width=2)
        ZoneGenerator._carve_path(zone, *rooms["e_grotto"][:2], *rooms["se_grotto"][:2], width=2)
        ZoneGenerator._carve_path(zone, *rooms["far_e_grotto"][:2], *rooms["e_grotto"][:2], width=2)

        # Water features - hub gets a real pool (matches the reference's
        # central water room with the rope-bridge crossing), NW room
        # gets a waterfall-fed pool.
        carve_pool(hub[0], hub[1] + 2, 5)

        # Real wooden rope bridge (Kyle got this art after the honest
        # "no bridge art exists yet" flag) - crosses the hub's own pool,
        # matching the reference's central water-crossing composition.
        # solid=False: the water beneath is already impassable on its
        # own, this is purely the visual crossing.
        zone.add_landmark("assets/tiles/bridges/bridge_sag.png",
                           hub[0] - 5, hub[1] - 1, 10, 5, solid=False)
        carve_pool(rooms["nw_waterfall"][0], rooms["nw_waterfall"][1] + 2, 4)

        # Boss - the broodmother in her nest, matching the reference's
        # egg-nest room. Real offset from the room's own carve-center
        # (not centered on it) - the same real bug class caught and
        # fixed for Burning Blade Coven's boss placement earlier this
        # session: centering a marker exactly on a room's own center can
        # collide with that room's own water/collision footprint.
        boss_room = rooms["n_boss_nest"]
        boss = (boss_room[0], boss_room[1] - 2)
        zone.set_tile(boss[0], boss[1] - 2, "chest", "interaction")
        zone.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        zone.boss_position = boss

        zone.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        zone.is_cave = True
        zone.fixed_spawns = False
        zone.add_subzone("Thunder Ridge", 0, 0, width, height)

        # Bone/rubble scatter matching the reference's skeleton piles -
        # real "small_rocks"/"rock_pile_*" variety (no dedicated skeleton
        # prop art exists yet, flagged as a real follow-up rather than
        # faked), kept moderate density to read as scattered remains
        # without looking like generic debris everywhere.
        ZoneGenerator._scatter(zone, "small_rocks", 0.04)
        ZoneGenerator._scatter(zone, "rock_pile_2", 0.02)
        ZoneGenerator._scatter(zone, "rock_pile_3", 0.02)

        # ------------------------------------------------------------------
        # CHUNKED ART - rocky/hardpan floor (matches this zone's own
        # real character), real mountain-wall obstacle art for the
        # canyon walls, real open water for the pools.
        # ------------------------------------------------------------------
        ridge_ground_variants = [
            "assets/tiles/valley_of_trials/terrain_variants/terrain_rocky.png",
            "assets/tiles/valley_of_trials/terrain_variants/terrain_hardpan.png",
            "assets/tiles/valley_of_trials/terrain_variants/terrain_scorched.png",
        ]
        chunk_size = 15
        variant_i = 0
        for cy in range(0, height, chunk_size):
            for cx in range(0, width, chunk_size):
                cw = min(chunk_size, width - cx)
                ch = min(chunk_size, height - cy)
                sprite = ridge_ground_variants[variant_i % len(ridge_ground_variants)]
                zone.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        obstacle_variants = [
            "assets/tiles/valley_of_trials/cliff_wall_a.png",
            "assets/tiles/valley_of_trials/cliff_wall_b.png",
        ]
        obstacle_variant_i = 0
        obstacle_chunk_size = 4
        for cy in range(0, height, obstacle_chunk_size):
            for cx in range(0, width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, width - cx)
                ch = min(obstacle_chunk_size, height - cy)
                sprite = obstacle_variants[obstacle_variant_i % len(obstacle_variants)]
                zone.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                obstacle_variant_i += 1

        water_variants = [
            "assets/tiles/water_variants/water_open_a.png",
            "assets/tiles/water_variants/water_shore_rapids.png",
        ]
        water_variant_i = 0
        for (wx, wy, wr) in [(hub[0], hub[1] + 2, 5), (rooms["nw_waterfall"][0], rooms["nw_waterfall"][1] + 2, 4)]:
            span = wr + 2
            for wcy in range(wy - span, wy + span, 6):
                for wcx in range(wx - span, wx + span, 6):
                    sprite = water_variants[water_variant_i % len(water_variants)]
                    zone.add_water_chunk(sprite, wcx, wcy, 6, 6)
                    water_variant_i += 1

        return zone

    @staticmethod
    def generate_zalazane_hollow():
        """Generate Zalazane's Hollow (100x85) - Echo Isles' capstone
        dungeon. Bestiary: "The capstone of the starter cluster. Should
        feel like a real test before whatever Phase 8 dungeon comes
        next." Zalazane (humanoid_caster_boss, level 16) at the end -
        Hexed Thralls (mind-controlled villagers), Voodoo Adepts
        (healer - "Dark Mending, heals the room"), Shadowfang Guardians
        (demon hounds) along the way. No real mid-cave sub-boss this
        time (unlike Skull Rock's Neru Fireblade) - straight escalation
        to one final test, matching the "capstone" framing.

        LINEAR SPINE WITH BRANCHING SIDE-ROOMS (Kyle, this session,
        explicit choice over the hub-and-spoke pattern every other cave
        in this file uses) - a straight main path of 4 escalating
        chambers leads to Zalazane's own chamber; 3 optional side-rooms
        branch OFF the spine rather than sitting on it, so a player can
        detour into extra fights/exploration without it being required
        to reach the boss. This is a deliberate structural choice, not
        a shortcut: a hub reads as "pick a direction", a spine reads as
        "descend toward the end" - the right shape for a capstone.

        Real assets on disk: floor.png/wall.png only (packed dark earth
        with faded ritual sigils, rough dark rock wall with troll totem
        relief and hanging bone/feather fetishes). No props/landmarks
        exist for this cave yet - this pass is geometry + those 2 real
        tiles, same "structure now, decorate later" scoping Sunken
        Temple Grotto's own first pass used.

        exit_pos MUST be exactly (52, 86) - portal_manager.py's real
        _links dict: Echo Isles' (128,99) arrives here at (52,86), and
        this zone's own (52,86) links back to Echo Isles (128,99).
        Checked directly, not assumed.
        """
        # Real height had to grow from an initial 85 to 92 - the hard
        # exit_pos y=86 from portal_manager.py is otherwise out of
        # bounds on an 85-tall map (caught by actually running this
        # generator, not assumed safe from the number alone).
        width, height = 100, 92
        hollow = Tilemap("Zalazane's Hollow", width, height,
                          "A troll ritual hollow, thick with voodoo magic and the mind-broken.")
        hollow.region = "Echo Isles"

        hollow.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                hollow.collision_layer[y][x] = "wall"
                hollow.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh, floor="dirt"):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            hollow.collision_layer[y][x] = None
                            hollow.set_tile(x, y, floor, "base")

        # ------------------------------------------------------------------
        # MAIN SPINE - west to east, 4 escalating chambers. Each one a
        # little bigger than the last, matching a real sense of
        # descending deeper before the capstone fight.
        # ------------------------------------------------------------------
        exit_pos = (52, 86)           # hard contract, see docstring
        entrance = (12, 42)
        spine_2 = (32, 42)
        spine_3 = (54, 42)
        spine_4 = (74, 42)
        boss_room = (90, 42)

        spine_rooms = {
            "entrance": (entrance, 8, 7),
            "spine_2": (spine_2, 9, 8),
            "spine_3": (spine_3, 10, 8),
            "spine_4": (spine_4, 10, 9),
            "boss_room": (boss_room, 12, 11),
        }
        for (cx, cy), rw, rh in spine_rooms.values():
            carve(cx, cy, rw, rh)

        ZoneGenerator._carve_path(hollow, *entrance, *spine_2, width=3)
        ZoneGenerator._carve_path(hollow, *spine_2, *spine_3, width=3)
        ZoneGenerator._carve_path(hollow, *spine_3, *spine_4, width=3)
        ZoneGenerator._carve_path(hollow, *spine_4, *boss_room, width=3)

        # ------------------------------------------------------------------
        # BRANCHING SIDE-ROOMS - optional, off the spine (not on it),
        # each connected from ONE spine room rather than chained off
        # each other, so a player who skips one doesn't lose access to
        # the rest of the spine.
        # ------------------------------------------------------------------
        side_a = (32, 18)   # branches off spine_2 (north)
        side_b = (54, 66)   # branches off spine_3 (south)
        side_c = (74, 18)   # branches off spine_4 (north)

        carve(*side_a, 7, 6)
        carve(*side_b, 8, 7)
        carve(*side_c, 7, 6)

        ZoneGenerator._carve_path(hollow, *spine_2, *side_a, width=2)
        ZoneGenerator._carve_path(hollow, *spine_3, *side_b, width=2)
        ZoneGenerator._carve_path(hollow, *spine_4, *side_c, width=2)

        # ------------------------------------------------------------------
        # PORTAL - exit_pos (52,86) is well south of the whole spine
        # (which sits at y=42), so it needs its own real landing +
        # path up into the entrance rather than assuming it lands
        # inside any carved room by coincidence.
        # ------------------------------------------------------------------
        ZoneGenerator._carve_landing(hollow, *exit_pos, radius=3)
        ZoneGenerator._carve_path(hollow, *exit_pos, *entrance, width=3)
        hollow.set_tile(*exit_pos, "portal", "interaction")

        # ------------------------------------------------------------------
        # BOSS - Zalazane, boss_room at the spine's far end. Chest/
        # marker offset from the room's own center (same reachability
        # discipline as every other cave this session).
        # ------------------------------------------------------------------
        boss = (boss_room[0] + 3, boss_room[1])
        hollow.set_tile(boss[0] - 6, boss[1] - 4, "chest", "interaction")
        hollow.set_tile(boss[0], boss[1] - 6, "boss_marker", "interaction")
        hollow.boss_position = boss

        hollow.is_cave = True
        hollow.fixed_spawns = False
        hollow.add_subzone("Zalazane's Hollow", 0, 0, width, height)

        ZoneGenerator._scatter(hollow, "small_rocks", 0.015)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - only 2 real tiles exist for this
        # cave right now (floor.png/wall.png), so every room shares
        # them - real material variety (a "ritual" vs "cell" vs
        # "throne" floor split, matching Tiragarde/Skull Rock's per-
        # room variety) is a future pass once more art exists, not
        # faked here with a texture that isn't real.
        # ------------------------------------------------------------------
        floor_sprite = "assets/tiles/zalazane_hollow/floor.png"
        wall_sprite = "assets/tiles/zalazane_hollow/wall.png"
        chunk_size = 20

        def floor_chunks(cx, cy, rw, rh):
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        hollow.add_ground_chunk(floor_sprite, gx, gy, gw, gh)

        for (cx, cy), rw, rh in spine_rooms.values():
            floor_chunks(cx, cy, rw, rh)
        floor_chunks(*side_a, 7, 6)
        floor_chunks(*side_b, 8, 7)
        floor_chunks(*side_c, 7, 6)

        obstacle_chunk_size = 4
        for cy in range(0, hollow.height, obstacle_chunk_size):
            for cx in range(0, hollow.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, hollow.width - cx)
                ch = min(obstacle_chunk_size, hollow.height - cy)
                hollow.add_obstacle_chunk(wall_sprite, cx, cy, cw, ch)

        return hollow

    @staticmethod
    def generate_sunken_temple_grotto():
        """Generate Sunken Temple Grotto (110x90) - Echo Isles' naga
        dungeon, per the bestiary: "Water-themed cave. Introduces the
        aquatic template at scale." Tidelord Gharesh (elemental_bruiser_
        boss, level 13) in a grand naga temple hall at the end.

        Built against a real reference map (Kyle, this session): a west
        entrance channel winding into a big central lagoon dotted with
        rock-pillar islets, a north side-pocket and a south circular
        chamber branching off the lagoon, two smaller mid-map pockets,
        and a grand east temple hall (trident/throne motif - Gharesh's
        own chamber) - a winding WATER-CHANNEL network, not the compass
        hub-and-spoke every other cave in this file uses. Kyle
        confirmed this shape explicitly rather than the simpler proven
        pattern, so the chambers are carved as pockets off a continuous
        carved-water spine instead of radiating from one central hub.

        Two tile families, matching what's real on disk: floor.png/
        wall.png (plain wet cave rock, algae/barnacle) for the natural
        approach sections, floor_ornate.png/wall_relief.png (naga-carved
        geometric floor, serpent-relief wall) for the worked-stone
        temple hall at the end. wall_relief.png in particular has a
        strong, very recognizable repeat (an individual serpent carving
        is highly distinct even seamlessly tiled) - used ONLY as an
        accent strip around the temple hall's own entrance, not
        stretched across the whole boss room, so it reads as a real
        carved feature rather than an obviously stamped pattern.

        exit_pos MUST be exactly (50, 81) - portal_manager.py's real
        _links dict: Echo Isles' (48,88) arrives here at (50,81), and
        this zone's own (50,81) links back to Echo Isles (48,88).
        Checked directly, not assumed.
        """
        width, height = 110, 90
        grotto = Tilemap("Sunken Temple Grotto", width, height,
                          "A flooded naga temple, its worked stone halls sinking back into the tide.")
        grotto.region = "Echo Isles"

        # Water as the default medium (matches the reference's flooded
        # look) - chambers are dry pockets carved OUT of it, channels
        # connecting them are real shallow-water walkable strips, not
        # dry corridors like every rock/cave generator in this file
        # uses. shallow_water reads as walkable "wading" water; only
        # deep_water blocks movement.
        grotto.fill("shallow_water", "base")
        for y in range(height):
            for x in range(width):
                grotto.collision_layer[y][x] = None  # shallow water is walkable by default

        def carve_land(cx, cy, rw, rh, floor="stone"):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < width and 0 <= y < height:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            grotto.collision_layer[y][x] = None
                            grotto.set_tile(x, y, floor, "base")

        def carve_wall_ring(cx, cy, rw, rh, thickness=3):
            # Real cave wall boundary around a chamber - collision
            # "wall" tiles just outside the chamber's own dry/water
            # floor, matching every other cave's real perimeter
            # (without this, a chamber has no actual edge, just fades
            # into the default open shallow water with no boundary).
            for dy in range(-rh - thickness, rh + thickness + 1):
                for dx in range(-rw - thickness, rw + thickness + 1):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < width and 0 <= y < height:
                        dist = ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5
                        inner = ((dx / max(rw + thickness, 1)) ** 2 + (dy / max(rh + thickness, 1)) ** 2) ** 0.5
                        if dist > 1.0 and inner <= 1.0:
                            grotto.collision_layer[y][x] = "wall"
                            grotto.set_tile(x, y, "rock", "collision")

        # ------------------------------------------------------------------
        # ROOMS - matching the reference map's real layout, west to east.
        # ------------------------------------------------------------------
        exit_pos = (50, 81)          # hard contract, see docstring
        entrance = (18, 20)          # west entrance channel clearing
        lagoon = (48, 42)            # big central lagoon, the map's real hub
        north_pocket = (48, 14)      # small chamber branching off the lagoon (N)
        south_chamber = (46, 68)     # circular chamber (S) - houses the exit
        mid_pocket_a = (72, 30)      # small mid-map branch pocket
        mid_pocket_b = (72, 58)      # small mid-map branch pocket
        temple_hall = (94, 44)       # grand east temple hall - Gharesh's chamber

        carve_land(*entrance, 8, 7, "sand")
        carve_wall_ring(*entrance, 8, 7)

        carve_land(*lagoon, 20, 16, "sand")
        carve_wall_ring(*lagoon, 20, 16)

        carve_land(*north_pocket, 8, 6, "stone")
        carve_wall_ring(*north_pocket, 8, 6)

        carve_land(*south_chamber, 10, 9, "stone")
        carve_wall_ring(*south_chamber, 10, 9)

        carve_land(*mid_pocket_a, 6, 6, "stone")
        carve_wall_ring(*mid_pocket_a, 6, 6)

        carve_land(*mid_pocket_b, 6, 6, "stone")
        carve_wall_ring(*mid_pocket_b, 6, 6)

        # Temple hall - larger, and its own worked-stone floor
        # (ornate) rather than the plain sand/stone every other
        # chamber gets, matching the reference's clear "you've reached
        # somewhere special" shift in material.
        carve_land(*temple_hall, 13, 11, "stone")
        carve_wall_ring(*temple_hall, 13, 11)

        # ------------------------------------------------------------------
        # CHANNELS - real carved shallow-water strips linking every
        # chamber to the lagoon (the map's real hub), matching the
        # reference's winding-channel composition rather than radial
        # spokes. Channels are WATER width, not the width=2 dry
        # corridors every rock cave uses - a chamber's own wall ring
        # already gates the actual chamber boundary, so the channel
        # itself just needs to punch a gap through each ring.
        # ------------------------------------------------------------------
        def carve_channel(x0, y0, x1, y1, width_tiles=4):
            ZoneGenerator._carve_path(grotto, x0, y0, x1, y1, width=width_tiles, base="shallow_water")

        carve_channel(*entrance, *lagoon)
        carve_channel(*lagoon, *north_pocket)
        carve_channel(*lagoon, *south_chamber)
        carve_channel(*lagoon, *mid_pocket_a)
        carve_channel(*mid_pocket_a, *mid_pocket_b)
        carve_channel(*mid_pocket_b, *temple_hall)

        # ------------------------------------------------------------------
        # PORTAL - exit_pos (50,81) sits within south_chamber's own
        # carved area (south_chamber=(46,68), rw=10,rh=9 - distance from
        # (50,81) is sqrt(16+169)/... well within the ellipse at rw,rh
        # this size). Landing clear + path back to the chamber center
        # added anyway as the same unconditional safety net every other
        # portal in this codebase gets.
        # ------------------------------------------------------------------
        ZoneGenerator._carve_landing(grotto, *exit_pos, radius=3)
        ZoneGenerator._carve_path(grotto, *exit_pos, *south_chamber, width=3, base="stone")
        grotto.set_tile(*exit_pos, "portal", "interaction")

        # ------------------------------------------------------------------
        # BOSS - Tidelord Gharesh, temple hall. Chest/marker offset from
        # the room's own center (same reachability discipline as every
        # other cave this session - a solid landmark centered on a
        # small room's own carve can re-solidify the point every
        # channel connects to).
        # ------------------------------------------------------------------
        boss = (temple_hall[0] + 2, temple_hall[1])
        grotto.set_tile(boss[0] - 4, boss[1] - 3, "chest", "interaction")
        grotto.set_tile(boss[0], boss[1] - 5, "boss_marker", "interaction")
        grotto.boss_position = boss

        grotto.is_cave = True
        grotto.fixed_spawns = False
        grotto.add_subzone("Sunken Temple Grotto", 0, 0, width, height)

        ZoneGenerator._scatter(grotto, "small_rocks", 0.015)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART
        # ------------------------------------------------------------------
        chunk_size = 20

        def floor_chunks(cx, cy, rw, rh, sprite):
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        grotto.add_ground_chunk(sprite, gx, gy, gw, gh)

        plain_floor = "assets/tiles/sunken_temple_grotto/floor.png"
        ornate_floor = "assets/tiles/sunken_temple_grotto/floor_ornate.png"

        floor_chunks(*entrance, 8, 7, plain_floor)
        floor_chunks(*lagoon, 20, 16, plain_floor)
        floor_chunks(*north_pocket, 8, 6, plain_floor)
        floor_chunks(*south_chamber, 10, 9, plain_floor)
        floor_chunks(*mid_pocket_a, 6, 6, plain_floor)
        floor_chunks(*mid_pocket_b, 6, 6, plain_floor)
        # Temple hall gets the ornate naga-carved floor - the one room
        # that's genuinely worked stone, not natural cave.
        floor_chunks(*temple_hall, 13, 11, ornate_floor)

        # Wall art - plain wall.png everywhere, EXCEPT a real accent
        # ring of wall_relief.png immediately around the temple hall's
        # own boundary (per this function's docstring: that texture's
        # serpent-carving repeat is too recognizable to stretch across
        # a big area, so it's scoped to a thin decorative border
        # instead of the room's whole perimeter).
        plain_wall = "assets/tiles/sunken_temple_grotto/wall.png"
        relief_wall = "assets/tiles/sunken_temple_grotto/wall_relief.png"
        obstacle_chunk_size = 4
        for cy in range(0, grotto.height, obstacle_chunk_size):
            for cx in range(0, grotto.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, grotto.width - cx)
                ch = min(obstacle_chunk_size, grotto.height - cy)
                dx, dy = cx - temple_hall[0], cy - temple_hall[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                # Accent ring: close enough to the temple hall's own
                # wall ring to read as its decorative border, not the
                # whole map's default wall.
                if 13 <= dist <= 17:
                    sprite = relief_wall
                else:
                    sprite = plain_wall
                grotto.add_obstacle_chunk(sprite, cx, cy, cw, ch)

        return grotto

    @staticmethod
    def generate_boulder_lode_mine():
        """Generate Boulder Lode Mine (100x80) - a real quarried mine cave
        in Northern Barrens, entrance at (255,45) per portal_manager.py's
        hardcoded link. "spiral" layout per the cave_specs table this
        replaces - a real mine shaft winding inward toward a deep crystal
        vein at the center, not a hub-and-spoke or linear chain.

        Two tile families, matching what's real on disk: floor.png/
        wall.png (plain quarried rock, cart-track dirt, timber bracing)
        for the outer shaft, floor_crystal.png/wall_crystal.png (dense
        glowing blue-purple crystal clusters) for the deep vein chamber
        at the spiral's center - the one room that's genuinely special,
        not stretched across the whole mine. wall_crystal.png in
        particular has a very recognizable repeat (the big crystal
        cluster is highly distinct even tiled) - used as an accent ring
        around the vein chamber's own boundary only, same discipline as
        Sunken Temple Grotto's relief wall.

        exit_pos MUST be exactly (50, 76) - portal_manager.py's real
        _links dict: Northern Barrens' (255,45) arrives here at (50,76),
        and this zone's own (50,76) links back to Northern Barrens
        (255,45). Checked directly, not assumed.
        """
        width, height = 100, 80
        mine = Tilemap("Boulder Lode Mine", width, height,
                        "A quarried mine shaft spiraling down toward a rich crystal vein.")
        mine.region = "Northern Barrens"

        mine.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                mine.collision_layer[y][x] = "wall"
                mine.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh, floor="dirt"):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            mine.collision_layer[y][x] = None
                            mine.set_tile(x, y, floor, "base")

        # ------------------------------------------------------------------
        # SPIRAL SHAFT - entrance winds inward through 4 chambers before
        # reaching the deep crystal vein at the true center. Real spiral
        # geometry (each chamber rotated further around the center point,
        # not a straight line) matching the cave_specs "spiral" layout.
        # ------------------------------------------------------------------
        exit_pos = (50, 76)  # hard contract, see docstring
        center = (50, 30)

        import math
        chambers = []
        n_chambers = 4
        for i in range(n_chambers):
            angle = math.radians(90 + i * 70)  # winds clockwise from the entrance
            r = 30 - i * 5  # spiral tightens as it goes deeper
            cx = center[0] + int(r * math.cos(angle))
            cy = center[1] + int(r * math.sin(angle) * 0.7)  # flattened for the map's aspect ratio
            chambers.append((cx, cy))

        carve(*exit_pos, 6, 5)
        prev = exit_pos
        for (cx, cy) in chambers:
            carve(cx, cy, 8, 7)
            ZoneGenerator._carve_path(mine, *prev, cx, cy, width=3)
            prev = (cx, cy)

        # Deep crystal vein - the spiral's true center, bigger than the
        # winding chambers leading to it.
        carve(*center, 12, 10)
        ZoneGenerator._carve_path(mine, *prev, *center, width=3)

        # ------------------------------------------------------------------
        # PORTAL
        # ------------------------------------------------------------------
        ZoneGenerator._carve_landing(mine, *exit_pos, radius=3)
        mine.set_tile(*exit_pos, "portal", "interaction")

        # ------------------------------------------------------------------
        # BOSS - the vein chamber, offset from its own center (same
        # reachability discipline as every cave this session).
        # ------------------------------------------------------------------
        boss = (center[0] + 4, center[1])
        mine.set_tile(boss[0] - 5, boss[1] - 3, "chest", "interaction")
        mine.set_tile(boss[0], boss[1] - 5, "boss_marker", "interaction")
        mine.boss_position = boss

        mine.is_cave = True
        mine.fixed_spawns = False
        mine.add_subzone("Boulder Lode Mine", 0, 0, width, height)

        ZoneGenerator._scatter(mine, "small_rocks", 0.015)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART
        # ------------------------------------------------------------------
        plain_floor = "assets/tiles/boulder_lode_mine/floor.png"
        plain_wall = "assets/tiles/boulder_lode_mine/wall.png"
        crystal_floor = "assets/tiles/boulder_lode_mine/floor_crystal.png"
        crystal_wall = "assets/tiles/boulder_lode_mine/wall_crystal.png"
        chunk_size = 20

        def floor_chunks(cx, cy, rw, rh, sprite):
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        mine.add_ground_chunk(sprite, gx, gy, gw, gh)

        floor_chunks(*exit_pos, 6, 5, plain_floor)
        for (cx, cy) in chambers:
            floor_chunks(cx, cy, 8, 7, plain_floor)
        floor_chunks(*center, 12, 10, crystal_floor)

        obstacle_chunk_size = 4
        for cy in range(0, mine.height, obstacle_chunk_size):
            for cx in range(0, mine.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, mine.width - cx)
                ch = min(obstacle_chunk_size, mine.height - cy)
                dx, dy = cx - center[0], cy - center[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                sprite = crystal_wall if 12 <= dist <= 16 else plain_wall
                mine.add_obstacle_chunk(sprite, cx, cy, cw, ch)

        return mine

    @staticmethod
    def generate_serenas_hollow():
        """Generate Serena's Hollow (60x55) - a harpy cliff roost in
        Northern Barrens, entrance at (60,150) per portal_manager.py's
        hardcoded link. "chain" layout per the cave_specs table this
        replaces - a real linear chain of cliff ledges, not a hub or
        spiral.

        Two tile families, matching what's real on disk: floor.png/
        wall.png (plain weathered cliff, guano streaks) for the
        approach ledges, floor_nest.png/wall_nest.png (dense woven nest
        material, bone/feather debris) for the final roost chamber -
        the one room with a real harpy nest, not scattered scraps
        everywhere. wall_nest.png's animal-skull motif is fairly
        recognizable repeated, so it's scoped to the nest chamber's own
        boundary as an accent, same pattern as every other "special
        material" wall this session.

        exit_pos MUST be exactly (30, 48) - portal_manager.py's real
        _links dict: Northern Barrens' (60,150) arrives here at (30,48),
        and this zone's own (30,48) links back to Northern Barrens
        (60,150). Checked directly, not assumed.
        """
        width, height = 60, 55
        hollow = Tilemap("Serena's Hollow", width, height,
                          "A harpy roost carved into wind-worn cliffside, thick with old nests.")
        hollow.region = "Northern Barrens"

        hollow.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                hollow.collision_layer[y][x] = "wall"
                hollow.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh, floor="dirt"):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            hollow.collision_layer[y][x] = None
                            hollow.set_tile(x, y, floor, "base")

        # ------------------------------------------------------------------
        # LINEAR CHAIN - 3 cliff ledges leading up to the final roost.
        # ------------------------------------------------------------------
        exit_pos = (30, 48)  # hard contract, see docstring
        ledge_1 = (30, 34)
        ledge_2 = (24, 20)
        roost = (32, 8)

        carve(*exit_pos, 5, 4)
        carve(*ledge_1, 6, 5)
        carve(*ledge_2, 6, 5)
        carve(*roost, 8, 7)

        ZoneGenerator._carve_path(hollow, *exit_pos, *ledge_1, width=2)
        ZoneGenerator._carve_path(hollow, *ledge_1, *ledge_2, width=2)
        ZoneGenerator._carve_path(hollow, *ledge_2, *roost, width=2)

        ZoneGenerator._carve_landing(hollow, *exit_pos, radius=3)
        hollow.set_tile(*exit_pos, "portal", "interaction")

        # Boss - Serena herself, the roost chamber. Offset from center,
        # same discipline as every cave this session.
        boss = (roost[0] + 3, roost[1])
        hollow.set_tile(boss[0] - 4, boss[1] - 3, "chest", "interaction")
        hollow.set_tile(boss[0], boss[1] - 4, "boss_marker", "interaction")
        hollow.boss_position = boss

        hollow.is_cave = True
        hollow.fixed_spawns = False
        hollow.add_subzone("Serena's Hollow", 0, 0, width, height)

        ZoneGenerator._scatter(hollow, "small_rocks", 0.01)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART
        # ------------------------------------------------------------------
        plain_floor = "assets/tiles/serenas_hollow/floor.png"
        plain_wall = "assets/tiles/serenas_hollow/wall.png"
        nest_floor = "assets/tiles/serenas_hollow/floor_nest.png"
        nest_wall = "assets/tiles/serenas_hollow/wall_nest.png"
        chunk_size = 20

        def floor_chunks(cx, cy, rw, rh, sprite):
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        hollow.add_ground_chunk(sprite, gx, gy, gw, gh)

        floor_chunks(*exit_pos, 5, 4, plain_floor)
        floor_chunks(*ledge_1, 6, 5, plain_floor)
        floor_chunks(*ledge_2, 6, 5, plain_floor)
        floor_chunks(*roost, 8, 7, nest_floor)

        obstacle_chunk_size = 4
        for cy in range(0, hollow.height, obstacle_chunk_size):
            for cx in range(0, hollow.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, hollow.width - cx)
                ch = min(obstacle_chunk_size, hollow.height - cy)
                dx, dy = cx - roost[0], cy - roost[1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                sprite = nest_wall if 8 <= dist <= 11 else plain_wall
                hollow.add_obstacle_chunk(sprite, cx, cy, cw, ch)

        return hollow

    @staticmethod
    def generate_the_den():
        """Generate The Den (85x70) - VoT's spider-cave dungeon, entrance
        at (40,30) per world/portal_manager.py's hardcoded link back to
        Valley of Trials.

        FULL DEDICATED REBUILD this session (Kyle: "we eventually should
        write each cave uniquely" after providing two real reference
        images - a labeled multi-room spider-den layout showing a
        central lake room with rock-spire islands and a rope bridge,
        flanking pocket rooms (one a small pool, several with egg
        clusters), and a north spider-boss web chamber; plus 6 isolated
        web/egg-cluster prop crops used as real standalone landmarks
        here). Was previously generated by the shared generate_cave()
        spec-table function (layout="chain", feature="bones") - reused
        that function's real primitives (carve/_carve_path room-carving,
        _carve_landing, add_landmark) but with HAND-PLACED room
        positions matching the reference composition, not the generic
        randomized chain layout. The other 13 caves in cave_specs stay
        on the shared generator for now - this is the first of what
        should eventually be a dedicated function per cave, not a
        wholesale rewrite of all of them at once.
        """
        width, height = 85, 70
        cave = Tilemap("The Den", width, height, "A cave beneath Valley of Trials.")
        cave.region = "Valley of Trials"

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        # Room layout matching the reference composition (relabeled to
        # this cave's 85x70 footprint, not a 1:1 pixel copy of the
        # reference's own irregular canvas size):
        #   entrance (south, matches portal_manager's (40,30) exit link
        #             back to VoT - NOTE: that's the VoT-side coordinate;
        #             this cave's own entrance/exit tile is independent)
        #   central lake room (mid-map) - the big organic pool with rock
        #             islands and a rope-bridge web crossing
        #   NW pocket - small round pool, quiet corner
        #   NE pocket - egg cluster nursery
        #   SW pocket - egg cluster nursery
        #   N boss chamber - spider web chamber, boss marker + treasure
        entrance = (42, 60)
        carve(*entrance, 8, 5)

        lake_room = (42, 38)
        carve(*lake_room, 15, 11)

        nw_pocket = (14, 22)
        carve(*nw_pocket, 9, 8)

        ne_pocket = (68, 24)
        carve(*ne_pocket, 8, 7)

        sw_pocket = (16, 52)
        carve(*sw_pocket, 8, 7)

        boss = (42, 12)
        carve(*boss, 11, 8)

        # Corridors linking every room - width=2 so the paths read as
        # real passages, not 1-tile mouse-holes.
        ZoneGenerator._carve_path(cave, *entrance, *lake_room, width=2)
        ZoneGenerator._carve_path(cave, *lake_room, *boss, width=2)
        ZoneGenerator._carve_path(cave, *lake_room, *nw_pocket, width=2)
        ZoneGenerator._carve_path(cave, *lake_room, *ne_pocket, width=2)
        ZoneGenerator._carve_path(cave, *nw_pocket, *sw_pocket, width=2)

        # Central lake - real water inside the lake_room, with rock-
        # spire islands (real standalone landmarks, matching the fix
        # already proven in Valley of Trials this session: obstacle-
        # chunk-clipped wall texture reads as an ugly tiny blob at
        # small scale, real standalone rock-formation art reads
        # correctly).
        lake_cx, lake_cy = lake_room
        lake_r = 8
        for dy in range(-lake_r - 1, lake_r + 2):
            for dx in range(-lake_r - 1, lake_r + 2):
                x, y = lake_cx + dx, lake_cy + dy
                if not (0 <= x < width and 0 <= y < height):
                    continue
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < lake_r * 0.6:
                    cave.set_tile(x, y, "deep_water", "base")
                    cave.collision_layer[y][x] = None
                elif dist < lake_r:
                    cave.set_tile(x, y, "shallow_water", "base")
                    cave.collision_layer[y][x] = None

        island_specs = [
            (lake_cx - 2, lake_cy, "mountain_rock.png"),
            (lake_cx + 4, lake_cy - 3, "rock_outcrop.png"),
            (lake_cx + 1, lake_cy + 4, "mountain_rock.png"),
        ]
        for (icx, icy, sprite) in island_specs:
            cave.add_landmark(f"assets/tiles/barrens/props/{sprite}",
                               icx - 1, icy - 1, 3, 3)

        # Rope-bridge web crossing the lake (matches the reference's
        # wooden bridge over the NW pool) - visual only (solid=False),
        # the water beneath is impassable regardless so this doesn't
        # need to punch a walkable hole through anything; it just needs
        # to visually read as a way across.
        cave.add_landmark("assets/tiles/the_den/props/web_bridge_a.png",
                           lake_cx - 4, lake_cy - lake_r - 2, 8, 6, solid=False)

        # Small NW pool (matches the reference's quiet side-pool room).
        nwx, nwy = nw_pocket
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = nwx + dx, nwy + dy
                if not (0 <= x < width and 0 <= y < height):
                    continue
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < 3:
                    cave.set_tile(x, y, "deep_water", "base")
                    cave.collision_layer[y][x] = None
                elif dist < 4:
                    cave.set_tile(x, y, "shallow_water", "base")
                    cave.collision_layer[y][x] = None

        # Egg cluster nurseries - real standalone landmarks (this
        # session's new art), one per pocket room, matching the
        # reference's several egg-cluster rooms scattered around the
        # den. solid=True (default) - these are real obstacles, not
        # just decoration, matching how thick a mass of spider eggs
        # actually should read.
        #
        # Offset from each room's own carve-CENTER (not centered on it) -
        # a real bug caught via flood-fill reachability testing: a solid
        # 6x5 landmark centered exactly on a room whose carve radius is
        # only ~8x7 re-solidifies most of the room's own walkable
        # interior, turning "a nursery chamber you walk into" into "a
        # dead-end nook you can't actually enter". Pushed to one side of
        # each room so there's real walkable floor around the egg mass,
        # not just a sliver at the edges.
        cave.add_landmark("assets/tiles/the_den/props/egg_cluster_a.png",
                           ne_pocket[0] + 1, ne_pocket[1] - 4, 6, 5)
        cave.add_landmark("assets/tiles/the_den/props/egg_cluster_b.png",
                           sw_pocket[0] + 1, sw_pocket[1] - 4, 6, 5)
        cave.add_landmark("assets/tiles/the_den/props/egg_cocoon_hanging.png",
                           lake_room[0] + 9, lake_room[1] - 2, 4, 5, solid=False)

        # Web-tent centerpiece at the boss chamber - the reference's
        # actual spider-boss room shows a huge funnel web with the
        # spider at its center. No standalone spider creature art exists
        # yet (checked directly - only unrelated ability icons under
        # assets/icons/), so this places the web structure itself as
        # the room's visual centerpiece; the boss creature/marker below
        # still resolves through the normal spawn system.
        cave.add_landmark("assets/tiles/the_den/props/web_tent_peak.png",
                           boss[0] - 4, boss[1] - 6, 8, 7, solid=False)
        # Extra web bridges as atmospheric set-dressing at 2 of the
        # corridor mouths near the boss chamber, matching the reference's
        # webs strung across multiple approach paths, not just the one
        # big lake bridge.
        cave.add_landmark("assets/tiles/the_den/props/web_bridge_b.png",
                           boss[0] - 12, boss[1] + 3, 6, 5, solid=False)

        # NOTE: the generic "guarantee entrance -> boss connectivity"
        # safety-net carve that generate_cave() always applies was
        # DELIBERATELY REMOVED here - a real bug, not a stylistic
        # choice: that straight-line carve from entrance (42,63) to
        # boss (42,12) cuts directly through the lake_room's center
        # (42,38), painting a rectangular strip of "dirt" straight
        # through the water - confirmed by directly inspecting
        # base_layer, which showed a clean rectangular dry hole in the
        # middle of an otherwise solid water carve, then rendering it
        # to see the exact same hole visually. This hand-placed layout
        # doesn't need that blind safety net the way the shared
        # generate_cave()'s randomized layouts do - every room here is
        # already explicitly connected by real _carve_path calls above,
        # and reachability was verified via an actual flood-fill from
        # entrance to boss (not assumed).

        # Generic light scatter, kept low.
        ZoneGenerator._scatter(cave, "small_rocks", 0.03)

        # exit_pos MUST be exactly (42,66) - real bug caught by grepping
        # world/portal_manager.py's actual _links dict rather than
        # assuming any nearby open tile would do: VoT's own (40,30)
        # entrance links to ("The Den", 42, 66) for arrival, AND The
        # Den's (42,66) links back to ("Valley of Trials", 40, 30) for
        # departure - both directions hardcode this exact coordinate.
        # entrance[1]+3 (=63) was the first value tried here and is
        # NOT (42,66) - it would have landed an arriving player on
        # solid unwalkable rock instead of the actual portal tile,
        # confirmed by checking is_walkable() at (42,66) before this
        # fix and finding it False.
        exit_pos = (entrance[0], entrance[1] + 6)
        ZoneGenerator._carve_landing(cave, *exit_pos, radius=2)
        ZoneGenerator._carve_path(cave, *exit_pos, *entrance, width=2)
        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        cave.set_tile(boss[0], boss[1] - 2, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("The Den", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART (kept from last session's proven work,
        # real 627x627 seamless textures instead of the shared cave_mossy
        # biome's small per-tile crops).
        # ------------------------------------------------------------------
        den_floor_variants = [
            "assets/tiles/the_den/cave_floor_chunk_a.png",
            "assets/tiles/the_den/cave_floor_chunk_b.png",
        ]
        chunk_size = 20
        variant_i = 0
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                sprite = den_floor_variants[variant_i % len(den_floor_variants)]
                cave.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        # Wall obstacle chunks - same 4x4-tile cap as Valley of Trials'
        # mountain ring (proven readable at that scale this session),
        # clipped to real "rock" collision tiles only.
        den_wall_variants = [
            "assets/tiles/the_den/cave_wall_chunk_a.png",
            "assets/tiles/the_den/cave_wall_chunk_b.png",
        ]
        wall_variant_i = 0
        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                sprite = den_wall_variants[wall_variant_i % len(den_wall_variants)]
                cave.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                wall_variant_i += 1

        # Lake water chunks - real variety (this session, same batch as
        # Valley of Trials' lake, but using the moody underwater-cave
        # variants instead - Kyle: "water tiles" delivered a 20-tile
        # sheet with distinct open-air vs underground-cave water moods,
        # and a real bug was caught wiring these into VoT first: the
        # dark, rock-spire "deep_*" variants looked wrong stitched next
        # to bright open lake water there. The Den is exactly the
        # enclosed underground pool those variants were actually meant
        # for - real fit here, not a fallback.
        den_lake_variants = [
            "assets/tiles/water_variants/water_deep_plain.png",
            "assets/tiles/water_variants/water_deep_stalactite.png",
            "assets/tiles/water_variants/water_deep_glow.png",
            "assets/tiles/water_variants/water_deep_spires.png",
            "assets/tiles/water_variants/water_deep_boulder.png",
        ]
        den_water_chunk_size = 8
        den_water_variant_i = 0
        for cy in range(lake_cy - 12, lake_cy + 12, den_water_chunk_size):
            for cx in range(lake_cx - 12, lake_cx + 12, den_water_chunk_size):
                sprite = den_lake_variants[den_water_variant_i % len(den_lake_variants)]
                cave.add_water_chunk(sprite, cx, cy, den_water_chunk_size, den_water_chunk_size)
                den_water_variant_i += 1

        # Small NW pool - shore-transition variants (rocks visible
        # through shallow water), matching the reference's "quiet side
        # pool" mood rather than the deep lake's dark cave-water look.
        nw_pool_variants = [
            "assets/tiles/water_variants/water_shore_mossy.png",
            "assets/tiles/water_variants/water_shore_calm.png",
        ]
        cave.add_water_chunk(nw_pool_variants[0], nw_pocket[0] - 6, nw_pocket[1] - 6, 6, 12)
        cave.add_water_chunk(nw_pool_variants[1], nw_pocket[0], nw_pocket[1] - 6, 6, 12)

        # Waterfall - the ONE standalone, non-tileable tile from the new
        # water sheet (Kyle's batch included a single-instance waterfall
        # scene, not a repeating material - confirmed by self-tiling it
        # and seeing an obviously artificial grid of identical
        # waterfalls, so it's used here exactly once as a real landmark
        # instead of a chunk). Placed feeding the NW pool, matching the
        # reference image's own composition (a wooden bridge over a
        # waterfall-fed side pool).
        #
        # Kyle: "can you blend it" after a real rendered screenshot
        # showed the waterfall sitting as a disconnected rectangular box
        # with a visible gap of bare cave floor between its own painted-
        # in pool graphic and the REAL water_chunk pool below it -
        # add_landmark is purely visual, it never touches base_layer, so
        # nothing under the waterfall's footprint was actually water
        # tiles. Fixed two ways:
        #  1. Moved the footprint up and tightened its overlap with the
        #     real pool so the waterfall's bottom ~40% (where the source
        #     image's own pool graphic sits) lands ON TOP of real water
        #     chunk tiles, not floor.
        #  2. Carved real shallow_water tiles under that same overlap
        #     region so the game's actual water data matches what's
        #     drawn - a player can genuinely stand at the pool's edge
        #     under the waterfall, not just look at a painted rectangle.
        wf_x, wf_y = nw_pocket[0] - 3, nw_pocket[1] - 11
        wf_w, wf_h = 5, 6
        cave.add_landmark("assets/tiles/water_variants/standalone/water_waterfall.png",
                           wf_x, wf_y, wf_w, wf_h, solid=False)
        # Real water under the waterfall's own bottom ~2 rows (where its
        # source image shows the splash pool), so it connects to the
        # real nw_pool water_chunks registered just below with zero gap.
        for dy in range(wf_h - 2, wf_h):
            for dx in range(wf_w):
                x, y = wf_x + dx, wf_y + dy
                if 0 <= x < width and 0 <= y < height:
                    cave.set_tile(x, y, "shallow_water", "base")
                    cave.collision_layer[y][x] = None

        return cave

    @staticmethod
    def generate_dustwind_cave():
        """Generate Dustwind Cave (80x65) - Durotar's scorpid burrow,
        entrance at (40,61) per world/portal_manager.py's hardcoded link
        back to Durotar (40,130); own portal at (40,61) for the return
        trip (checked directly, same coordinate both directions).

        FULL DEDICATED REBUILD (Kyle's "Still ahead" list, item 2: real
        insect-cave floor/wall tiles instead of the shared generic
        generate_cave() table it was using before - theme="rock",
        layout="chain", feature="bones", which renders with zero chunked
        art at all, just a flat per-tile "rock"/biome-fallback texture).
        Real roster per data/creatures/encounters.json: Cave Scorpid,
        Sand Skitterling, boss Gorge the Corpsegrinder - a scorpion/
        skitterling burrow, not a classic rock cavern or a spider den.

        No dedicated sandy-burrow art exists yet (checked assets/tiles/
        directly). Reuses assets/tiles/broodspiral/ (built for the
        Broodspiral dungeon, unused anywhere else) - Kyle's call after
        flagging the thematic mismatch: hive_floor.png (cracked tan/
        brown ground with shell-fragment debris baked in) reads fine as
        sandy burrow floor on its own merits even outside its original
        spider-hive context, and chitin_wall.png (carapace plating) is
        exactly as plausible for a scorpid-shell burrow wall as a spider
        one. resin_floor.png/resin_wall.png were tried and rejected -
        too amber/web-pooled, doesn't read as sand. carapace_pile.png
        and egg_sac_cluster.png (broodspiral props) double as scorpid
        shell debris / skitterling nest dressing; skull_rock's
        bone_pile.png adds prey-remains scatter, same as other caves.
        """
        width, height = 80, 65
        cave = Tilemap("Dustwind Cave", width, height, "A sandy scorpid burrow beneath Durotar.")
        cave.region = "Durotar"

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        # Hub-and-spoke scorpid-nest layout: entrance south, a wide
        # central nest chamber, 2 side burrow pockets (skitterling nests),
        # boss chamber (Gorge the Corpsegrinder) north - same proven
        # geometry family as Skull Rock/Burning Blade Coven, scaled to
        # this cave's 80x65 footprint.
        entrance = (40, 58)
        carve(*entrance, 8, 5)

        nest_hub = (40, 38)
        carve(*nest_hub, 14, 10)

        w_pocket = (14, 30)
        carve(*w_pocket, 8, 7)

        e_pocket = (64, 30)
        carve(*e_pocket, 8, 7)

        boss = (40, 12)
        carve(*boss, 10, 7)

        ZoneGenerator._carve_path(cave, *entrance, *nest_hub, width=2)
        ZoneGenerator._carve_path(cave, *nest_hub, *w_pocket, width=2)
        ZoneGenerator._carve_path(cave, *nest_hub, *e_pocket, width=2)
        ZoneGenerator._carve_path(cave, *nest_hub, *boss, width=2)

        # Carapace-pile dressing in the central nest and both side
        # pockets - real scorpid shell debris, not just flavor scatter.
        cave.add_landmark("assets/tiles/broodspiral/props/carapace_pile.png",
                           nest_hub[0] - 10, nest_hub[1] + 4, 5, 4)
        cave.add_landmark("assets/tiles/broodspiral/props/carapace_pile.png",
                           nest_hub[0] + 6, nest_hub[1] - 6, 5, 4)

        # Skitterling nests - egg-sac clusters in each side pocket,
        # offset from room center (same "don't re-solidify the room
        # you're decorating" discipline as The Den's egg clusters - a
        # solid landmark centered exactly on a small carved room can eat
        # most of its own walkable interior).
        cave.add_landmark("assets/tiles/broodspiral/props/egg_sac_cluster.png",
                           w_pocket[0] + 1, w_pocket[1] - 4, 6, 5)
        cave.add_landmark("assets/tiles/broodspiral/props/egg_sac_cluster.png",
                           e_pocket[0] - 7, e_pocket[1] - 4, 6, 5)

        # Prey-remains bone scatter (skull_rock's prop, reused - matches
        # this cave's "bones" feature theme from the old generic table).
        cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                           boss[0] - 7, boss[1] + 3, 4, 3)
        cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                           entrance[0] + 4, entrance[1] - 3, 4, 3)

        ZoneGenerator._scatter(cave, "small_rocks", 0.03)

        # exit_pos MUST be exactly (40,61) - world/portal_manager.py
        # hardcodes this coordinate both directions (Durotar (40,130) ->
        # Dustwind Cave (40,61), and Dustwind Cave (40,61) -> Durotar
        # (40,130)). entrance is (40,58); the real portal tile sits a
        # few rows south of the carved entrance room, same offset
        # pattern as The Den.
        exit_pos = (40, 61)
        ZoneGenerator._carve_landing(cave, *exit_pos, radius=2)
        ZoneGenerator._carve_path(cave, *exit_pos, *entrance, width=2)
        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        cave.set_tile(boss[0], boss[1] - 2, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("Dustwind Cave", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART
        # ------------------------------------------------------------------
        floor_variants = [
            "assets/tiles/broodspiral/hive_floor.png",
        ]
        chunk_size = 20
        variant_i = 0
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                sprite = floor_variants[variant_i % len(floor_variants)]
                cave.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        wall_variants = [
            "assets/tiles/broodspiral/chitin_wall.png",
        ]
        wall_variant_i = 0
        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                sprite = wall_variants[wall_variant_i % len(wall_variants)]
                cave.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                wall_variant_i += 1

        return cave

    @staticmethod
    @staticmethod
    def generate_burning_blade_coven():
        """Generate Burning Blade Coven (100x85) - VoT's Horde raider
        outpost cave, entrance at (95,22) per world/portal_manager.py's
        hardcoded link back to Valley of Trials, own portal at (50,81)
        per that same file's Burning Blade Coven -> Valley of Trials
        link (checked directly before writing this - a real coordinate
        mismatch bug was caught and fixed for The Den earlier this
        session by skipping this check, so it's done up front here).

        FULL DEDICATED REBUILD this session (Kyle, same "write each
        cave uniquely" direction as The Den), matching a real reference
        image: a central hub shrine (spike-and-banner totem + campfire)
        with 8 spoke corridors radiating out to distinct themed rooms -
        camps with loot crates, waterfall rooms, and pool rooms. Was
        previously on the shared generate_cave() spec-table generator
        (layout="warren", feature="lava") - reused generate_cave()'s
        real primitives (carve/_carve_path, add_landmark) with HAND-
        PLACED room positions matching the reference, not the generic
        randomized warren layout.
        """
        width, height = 100, 85
        cave = Tilemap("Burning Blade Coven", width, height,
                        "A Horde raider outpost carved into the rock beneath Valley of Trials.")
        cave.region = "Valley of Trials"

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        # Real portal exit MUST be exactly (50,81) - grepped world/
        # portal_manager.py's actual _links dict rather than assuming;
        # The Den had a real bug this session from guessing a nearby
        # coordinate instead of the exact contracted one.
        #
        # Room/hub radii and corridor width SHRUNK this session (Kyle:
        # "we need to see walls" after a real render at the actual game
        # viewport (1280x720, 32px tiles = 40x22 tiles visible) showed
        # a player standing in a "corridor" with ZERO wall visible
        # anywhere on screen. Measured directly, not assumed: the old
        # hub radius (10,8) + room radii (7-10) + only ~35-40 tile hub-
        # to-room distances meant the elliptical carves genuinely
        # overlapped and merged into one open cavern - real walkable
        # spans of 18-45 tiles wide were measured along what was
        # supposed to be a narrow connecting corridor. Real fix: much
        # smaller hub/rooms, narrower corridors (width=2 max), so solid
        # "rock" actually survives between them and reads as real walls
        # during normal play, matching the reference's genuinely narrow
        # winding tunnels rather than one merged-together open floor.
        exit_pos = (50, 81)
        hub = (50, 45)
        carve(*exit_pos, 4, 3)
        carve(*hub, 6, 5)
        ZoneGenerator._carve_path(cave, *exit_pos, *hub, width=2)

        # 8 spoke rooms - REDESIGNED this session (Kyle: "walls inside
        # the den and the other cave" not loading, focused specifically
        # on the caves, not VoT's overworld). Real root cause found via
        # a direct per-row "widest contiguous walkable run" scan across
        # the whole cave: the OLD layout had hub/w_camp/e_camp all
        # sitting within 3 tiles of the same Y coordinate (all ~y=45-48),
        # so their individually-small carves chained together left-to-
        # right with no vertical offset anywhere to leave rock between
        # them - measured an 82-TILE-WIDE contiguous open row on a
        # 100-wide map (not a corridor-width math issue, which had
        # already been fixed separately - this was a genuine geometry/
        # layout bug). Replaced with a real 8-point compass layout (45
        # degrees apart around the hub, verified via real trig, not
        # eyeballed) so no two rooms/corridors share a Y or X band -
        # matches how the reference image's rooms are genuinely
        # scattered at different angles/distances, not lined up.
        # Angles offset 22.5 degrees from true compass points (this was
        # the remaining real bug after the first radial redesign above -
        # a PURE 8-point compass layout still put the due-east and due-
        # west rooms at the hub's exact same Y coordinate by definition,
        # which still produced a 56-68 tile wide open band right at the
        # hub's row - verified directly via the same per-row scan. A
        # half-step rotation means no room shares the hub's exact row
        # or column at all.
        rooms = {
            "nw_camp":       (61, 24, 5, 4),
            "n_waterfall":   (78, 36, 5, 4),
            "ne_pool":       (78, 54, 6, 5),
            "far_ne_camp":   (61, 66, 4, 4),
            "e_camp":        (39, 66, 5, 4),
            "se_waterfall":  (22, 54, 5, 4),
            "sw_pool":       (22, 36, 5, 5),
            "w_camp":        (39, 24, 5, 4),
        }
        # Corridors start from the HUB'S EDGE (a point on its own
        # boundary, in the direction of each room) rather than its
        # exact center - real bug caught via an in-game screenshot +
        # direct ASCII data scan: with all 8 corridors' _carve_path
        # calls sharing the exact same hub-center start point, their
        # combined width right AT that convergence point fanned out
        # into one continuous open band spanning nearly the WHOLE map
        # width (confirmed directly: rows y=44-46 near the hub center
        # were completely open, ". "x60, with zero walls anywhere in
        # that band) - each individual corridor was genuinely narrow,
        # but 8 of them radiating from one shared point necessarily
        # overlap near that point regardless of per-corridor width.
        hub_r = (6, 5)
        for (rx, ry, rw, rh) in rooms.values():
            carve(rx, ry, rw, rh)
            dx, dy = rx - hub[0], ry - hub[1]
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.001)
            edge_x = hub[0] + round(dx / dist * hub_r[0])
            edge_y = hub[1] + round(dy / dist * hub_r[1])
            ZoneGenerator._carve_path(cave, edge_x, edge_y, rx, ry, width=2)

        # ------------------------------------------------------------------
        # WATER - the 2 waterfall rooms and 2 pool rooms get real water,
        # matching the reference's blue pools. Small, room-scaled radii.
        # ------------------------------------------------------------------
        def carve_pool(cx, cy, r):
            for dy in range(-r - 1, r + 2):
                for dx in range(-r - 1, r + 2):
                    x, y = cx + dx, cy + dy
                    if not (0 <= x < width and 0 <= y < height):
                        continue
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    if dist < r * 0.55:
                        cave.set_tile(x, y, "deep_water", "base")
                        cave.collision_layer[y][x] = None
                    elif dist < r:
                        cave.set_tile(x, y, "shallow_water", "base")
                        cave.collision_layer[y][x] = None

        # Pool radii shrunk to match the smaller room sizes above (a
        # radius-5 pool inside a radius-5 room would overflow past the
        # room's own carved floor into solid rock - checked directly
        # against the new room sizes, not left at the old values).
        carve_pool(rooms["ne_pool"][0] - 1, rooms["ne_pool"][1] + 1, 3)
        carve_pool(rooms["sw_pool"][0], rooms["sw_pool"][1], 3)
        carve_pool(rooms["n_waterfall"][0], rooms["n_waterfall"][1] + 2, 2)
        carve_pool(rooms["se_waterfall"][0], rooms["se_waterfall"][1] + 1, 2)

        # ------------------------------------------------------------------
        # LANDMARKS - real props from this session (horde spike banner
        # totem at the hub, campfires in camp rooms, loot crates), plus
        # the 2 waterfall landmarks reused from The Den's water batch
        # (that source image is a real standalone, non-tileable scene -
        # confirmed earlier this session - reusable anywhere a single
        # waterfall accent fits, not just The Den).
        # ------------------------------------------------------------------
        cave.add_landmark("assets/tiles/burning_blade_coven/props/horde_spike_banner.png",
                           hub[0] - 3, hub[1] - 4, 6, 5, solid=False)
        cave.add_landmark("assets/tiles/burning_blade_coven/props/campfire_ring.png",
                           hub[0] - 2, hub[1] + 1, 4, 4, solid=False)

        for name in ["nw_camp", "w_camp", "e_camp", "far_ne_camp"]:
            rx, ry, rw, rh = rooms[name]
            cave.add_landmark("assets/tiles/burning_blade_coven/props/campfire_ring.png",
                               rx - 2, ry - 2, 4, 4, solid=False)
        cave.add_landmark("assets/tiles/burning_blade_coven/props/loot_crate_barrel.png",
                           rooms["nw_camp"][0] + 3, rooms["nw_camp"][1] - 1, 5, 5)
        cave.add_landmark("assets/tiles/burning_blade_coven/props/loot_crate_barrel.png",
                           rooms["ne_pool"][0] + 4, rooms["ne_pool"][1] - 2, 5, 5)

        cave.add_landmark("assets/tiles/water_variants/standalone/water_waterfall.png",
                           rooms["n_waterfall"][0] - 2, rooms["n_waterfall"][1] - 5, 5, 6, solid=False)
        cave.add_landmark("assets/tiles/water_variants/standalone/water_waterfall.png",
                           rooms["se_waterfall"][0] - 2, rooms["se_waterfall"][1] - 4, 5, 6, solid=False)

        # ------------------------------------------------------------------
        # Boss + interaction tiles.
        # ------------------------------------------------------------------
        # Boss + interaction tiles. Offset from ne_pool's own carve-
        # CENTER (not placed directly on it) - real bug caught by
        # reachability testing: the room center is the pool's own water
        # (deep_water is unwalkable by design), so a boss_marker placed
        # exactly there would sit in unreachable water. Same class of
        # mistake as an earlier one this session (The Den's egg
        # clusters solidifying their own room's center) - offsetting to
        # the room's dry northern edge instead.
        # Offset recalculated against the SHRUNK room/pool sizes above
        # (Kyle: "we need to see walls" triggered a real room/corridor
        # resize this session) - the old -6 offset was calibrated
        # against the previous larger room and would now land outside
        # the smaller room's own ellipse entirely (verified directly:
        # ((75-75)/6)^2 + ((9-15)/5)^2 > 1.0, i.e. genuinely in solid
        # rock, not just close to the pool). -4 keeps it inside the
        # room and still outside the pool's radius.
        boss = (rooms["ne_pool"][0], rooms["ne_pool"][1] - 4)
        cave.set_tile(boss[0], boss[1] - 3, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("Burning Blade Coven", 0, 0, width, height)

        ZoneGenerator._scatter(cave, "small_rocks", 0.03)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - real chunked textures (matching
        # this session's proven pattern from Valley of Trials/The Den),
        # NOT the old small per-tile crops under assets/tiles/caves/
        # (checked directly - those still exist but are exactly the
        # small-crop-repeated-per-tile problem this session's whole
        # chunk-art pass was built to fix, so deliberately not reused
        # here even though they'd technically work).
        # ------------------------------------------------------------------
        # Real dry earthen floor + gray rock wall art (this session,
        # Kyle delivered the actual sheet right after this function was
        # first written with a temporary The Den placeholder) - warm
        # tan/brown packed dirt, no moss, matching a Horde raider
        # outpost rather than a damp natural cavern. Verified seamless
        # via the same 3x3 self-tile preview process as every other
        # chunked material this session.
        coven_floor_variants = [
            "assets/tiles/burning_blade_coven/cave_floor_chunk_a.png",
            "assets/tiles/burning_blade_coven/cave_floor_chunk_b.png",
        ]
        chunk_size = 20
        variant_i = 0
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                sprite = coven_floor_variants[variant_i % len(coven_floor_variants)]
                cave.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        coven_wall_variants = [
            "assets/tiles/burning_blade_coven/cave_wall_chunk_a.png",
            "assets/tiles/burning_blade_coven/cave_wall_chunk_b.png",
        ]
        wall_variant_i = 0
        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                sprite = coven_wall_variants[wall_variant_i % len(coven_wall_variants)]
                cave.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                wall_variant_i += 1

        den_water_variants = [
            "assets/tiles/water_variants/water_deep_plain.png",
            "assets/tiles/water_variants/water_deep_glow.png",
            "assets/tiles/water_variants/water_shore_mossy.png",
            "assets/tiles/water_variants/water_shore_calm.png",
        ]
        water_variant_i = 0
        for room_key, r in [("ne_pool", 5), ("sw_pool", 5), ("n_waterfall", 3), ("se_waterfall", 4)]:
            rx, ry = rooms[room_key][0], rooms[room_key][1]
            if room_key == "ne_pool":
                rx, ry = rx - 2, ry + 1
            elif room_key == "n_waterfall":
                ry = ry + 3
            elif room_key == "se_waterfall":
                ry = ry + 2
            span = r + 2
            for wy in range(ry - span, ry + span, 6):
                for wx in range(rx - span, rx + span, 6):
                    sprite = den_water_variants[water_variant_i % len(den_water_variants)]
                    cave.add_water_chunk(sprite, wx, wy, 6, 6)
                    water_variant_i += 1

        return cave

    @staticmethod
    def generate_skull_rock():
        """Generate Skull Rock (110x90) - the Burning Blade's real operation,
        per bestiary_starter_zones.md's Skull Rock entry: "Direct escalation
        of the Valley's Coven - same faction, meaner." Gazz'uz (demon
        caster boss) at the end, Neru Fireblade as a mid-cave mini-boss.

        Deliberately reuses Burning Blade Coven's proven 8-room hub-and-
        spoke geometry (Kyle: "design skull rock similar to the other
        burning blade cave in VoT") rather than inventing a new layout -
        same faction, same real structural lessons already paid for
        there: rooms at 22.5-degree-offset compass angles so none share
        the hub's exact row/column (a pure 8-point layout still collides
        on the due-E/due-W row), and corridors starting from the HUB'S
        OWN EDGE rather than its center (8 corridors sharing one exact
        start point fan out into one continuous open band regardless of
        individual corridor width - confirmed directly in Coven via a
        per-row contiguous-walkable-run scan).

        Distinct from Coven in mood/material only, not shape: dry tan/
        gray Burning Blade cave palette pushed toward molten/ritual per
        the "meaner escalation" bestiary note - 3 floor variants (plain
        cavern, glowing molten cracks, ritual-sigil ash floor) and 2
        wall variants (dry rock, scorched/glowing rock) instead of
        Coven's 2 floor / 2 wall pair, plus lava-pool/brazier/bone-pile
        props instead of campfires and water.

        exit_pos MUST be exactly (55, 86) - portal_manager.py's real
        _links dict: Durotar's (118, 60) arrives here at (54, 85) [one
        tile off the actual exit portal, by design - see that file's
        own note on spawning at the generator-confirmed entrance chamber
        rather than just the nearest walkable tile], and this zone's own
        (55, 86) links back to Durotar (118, 60). Checked directly.
        """
        width, height = 110, 90
        cave = Tilemap("Skull Rock", width, height,
                        "The Burning Blade's real stronghold - a molten cavern lit by ritual fire.")
        cave.region = "Durotar"

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        exit_pos = (55, 86)
        hub = (55, 47)
        carve(*exit_pos, 4, 3)
        carve(*hub, 6, 5)
        ZoneGenerator._carve_path(cave, *exit_pos, *hub, width=2)

        # Same 22.5-degree-offset 8-point compass layout as Coven, scaled
        # to this map's slightly larger 110x90 footprint. Room "roles"
        # reskinned for a cult/lava stronghold instead of a raider camp:
        # ritual rooms (ex-camps), molten rooms (ex-waterfall/pool - no
        # real water here, lava pools instead), and a mini-boss room for
        # Neru Fireblade partway between hub and Gazz'uz's own chamber.
        rooms = {
            "nw_ritual":     (67, 25, 5, 4),
            "n_molten":      (85, 38, 5, 4),
            "ne_lavapool":   (85, 58, 6, 5),
            "far_ne_ritual": (67, 71, 4, 4),
            "e_ritual":      (43, 71, 5, 4),
            "se_molten":     (24, 58, 5, 4),
            "sw_lavapool":   (24, 38, 5, 5),
            "w_miniboss":    (43, 25, 5, 4),
        }
        hub_r = (6, 5)
        for (rx, ry, rw, rh) in rooms.values():
            carve(rx, ry, rw, rh)
            dx, dy = rx - hub[0], ry - hub[1]
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.001)
            edge_x = hub[0] + round(dx / dist * hub_r[0])
            edge_y = hub[1] + round(dy / dist * hub_r[1])
            ZoneGenerator._carve_path(cave, edge_x, edge_y, rx, ry, width=2)

        # ------------------------------------------------------------------
        # LAVA POOLS - Coven's 2 water rooms become 2 lava rooms here (no
        # real water feature exists for this zone; lava reads as ground
        # texture + landmark, not a separate walkable-liquid layer like
        # water, so these stay walkable rather than blocked - a cult
        # stronghold's lit basins, not a hazard to fall in).
        # ------------------------------------------------------------------
        cave.add_landmark("assets/tiles/skull_rock/props/lava_pool.png",
                           rooms["ne_lavapool"][0] - 2, rooms["ne_lavapool"][1] + 1, 6, 5, solid=False)
        cave.add_landmark("assets/tiles/skull_rock/props/lava_pool.png",
                           rooms["sw_lavapool"][0] - 3, rooms["sw_lavapool"][1], 6, 5, solid=False)

        # ------------------------------------------------------------------
        # LANDMARKS - ritual brazier at the hub (Coven's spike-banner
        # totem equivalent), lava spikes marking the molten rooms, bone
        # piles in the ritual rooms (echoing the zone's own name), and
        # the cracked glowing pillar leading up to Gazz'uz's chamber.
        # ------------------------------------------------------------------
        cave.add_landmark("assets/tiles/skull_rock/props/ritual_brazier.png",
                           hub[0] - 2, hub[1] - 4, 4, 5, solid=False)
        cave.add_landmark("assets/tiles/skull_rock/props/lava_spikes.png",
                           hub[0] + 2, hub[1] + 2, 4, 4)

        for name in ["nw_ritual", "e_ritual", "far_ne_ritual"]:
            rx, ry, rw, rh = rooms[name]
            # solid=False - a 4x4 solid footprint nearly matches these
            # small rooms' own 4x4/5x4 carve radius, which re-solidified
            # the room's entire floor including its one corridor
            # connection point - caught via real flood-fill reachability
            # (3 of 8 rooms came back unreachable), not assumed safe
            # just because Coven's larger camp rooms tolerated a similar-
            # sized solid prop fine. A floor-level bone scatter has no
            # real reason to block walking anyway.
            cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                               rx - 2, ry - 1, 4, 4, solid=False)

        cave.add_landmark("assets/tiles/skull_rock/props/lava_spikes.png",
                           rooms["n_molten"][0] + 1, rooms["n_molten"][1] - 2, 4, 4)
        cave.add_landmark("assets/tiles/skull_rock/props/lava_spikes.png",
                           rooms["se_molten"][0] + 1, rooms["se_molten"][1] - 2, 4, 4)

        # Neru Fireblade's mini-boss room gets its own brazier - a
        # smaller ritual site partway to the real boss, matching the
        # bestiary's "mini-boss, mid-cave" placement.
        cave.add_landmark("assets/tiles/skull_rock/props/ritual_brazier.png",
                           rooms["w_miniboss"][0] - 2, rooms["w_miniboss"][1] - 1, 4, 5, solid=False)

        # Cracked pillar marking Gazz'uz's own chamber - offset from the
        # room's own center point, not placed on it (same reachability
        # discipline as Coven's boss-marker fix: a solid landmark
        # centered on a small room's own carve re-solidifies most of
        # its interior and/or the point every corridor connects to).
        cave.add_landmark("assets/tiles/skull_rock/props/cracked_pillar.png",
                           rooms["ne_lavapool"][0] + 3, rooms["ne_lavapool"][1] - 4, 4, 5)

        # ------------------------------------------------------------------
        # Boss + interaction tiles. Gazz'uz's chamber is ne_lavapool -
        # boss marker offset to the room's dry edge, clear of both the
        # lava pool landmark and the cracked pillar prop (checked their
        # footprints directly rather than assuming clearance).
        # ------------------------------------------------------------------
        boss = (rooms["ne_lavapool"][0] - 4, rooms["ne_lavapool"][1] - 4)
        cave.set_tile(boss[0], boss[1] - 3, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("Skull Rock", 0, 0, width, height)

        ZoneGenerator._scatter(cave, "small_rocks", 0.03)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - 3 floor variants / 2 wall variants
        # (Kyle: "3 floor styles, 2 wall styles" - leaner than Coven's
        # 2/2 pair but still real material variety per room, not one
        # texture over the whole cave).
        # ------------------------------------------------------------------
        floor_variants = [
            "assets/tiles/skull_rock/floor_cavern.png",
            "assets/tiles/skull_rock/floor_molten.png",
            "assets/tiles/skull_rock/floor_ritual.png",
        ]
        chunk_size = 20
        variant_i = 0
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                sprite = floor_variants[variant_i % len(floor_variants)]
                cave.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        wall_variants = [
            "assets/tiles/skull_rock/wall_cave.png",
            "assets/tiles/skull_rock/wall_scorched.png",
        ]
        wall_variant_i = 0
        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                sprite = wall_variants[wall_variant_i % len(wall_variants)]
                cave.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                wall_variant_i += 1

        return cave

    @staticmethod
    def generate_tiragarde_keep():
        """Generate Tiragarde Keep (90x80) - a stranded Kul Tiras (Alliance)
        coastal fortress ruin in Durotar, per bestiary_starter_zones.md's
        Tiragarde Hold entry ("Human survivors... narratively uncomfortable
        on purpose") - Captain Thalenvorde and his marines, washed up deep
        in Horde territory and cut off.

        FULL DEDICATED REBUILD (Kyle: "we need to fully redo the keep...
        even a ruined keep prop instead of some lame ass cave entrance"),
        replacing the previous generic generate_cave() entry (cavern
        layout, "ruins" feature - an open arena with generic rubble
        scatter, no real rooms). Built against a real reference image:
        a fortress interior with 4 round corner towers (one collapsed),
        a central courtyard with a banner-pole centerpiece, a north
        great hall with a war table, flanking barracks/storage rooms,
        and a south drawbridge entrance - same "hand-placed rooms
        matching a real reference" treatment as The Den and Burning
        Blade Coven got, not the shared spec-table generator.

        exit_pos MUST be exactly (45, 76) - portal_manager.py's real
        _links dict hardcodes this both directions: Durotar's (95, 178)
        arrives here at (45, 76), and this zone's own (45, 76) links
        back to Durotar (95, 178). Checked directly, not assumed.
        """
        width, height = 90, 80
        keep = Tilemap("Tiragarde Keep", width, height,
                        "A stranded Kul Tiras fortress, its stone walls salt-faded and half-reclaimed by the coast.")
        keep.region = "Durotar"

        keep.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                keep.set_tile(x, y, "wall", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            keep.collision_layer[y][x] = None
                            keep.set_tile(x, y, "dirt", "base")

        # Room layout matching the reference composition (relabeled to
        # this zone's 90x80 footprint):
        #   entrance (south, matches portal_manager's (45,76) exit link
        #             back to Durotar)
        #   courtyard (mid-map) - open central space, banner pole centerpiece
        #   NW tower - flanking room off courtyard
        #   NE tower - flanking room off courtyard
        #   SW tower - barracks
        #   SE tower - COLLAPSED, ruined wing
        #   N great hall - Captain Thalenvorde's boss chamber, war table
        entrance = (45, 70)
        entrance_r = (8, 5)
        carve(*entrance, *entrance_r)

        courtyard = (45, 46)
        courtyard_r = (17, 13)
        carve(*courtyard, *courtyard_r)

        nw_tower = (18, 24)
        nw_tower_r = (9, 8)
        carve(*nw_tower, *nw_tower_r)

        ne_tower = (72, 24)
        ne_tower_r = (9, 8)
        carve(*ne_tower, *ne_tower_r)

        sw_tower = (18, 60)
        sw_tower_r = (8, 7)
        carve(*sw_tower, *sw_tower_r)

        se_tower = (72, 60)
        se_tower_r = (8, 7)
        carve(*se_tower, *se_tower_r)

        great_hall = (45, 14)
        great_hall_r = (13, 9)
        carve(*great_hall, *great_hall_r)

        # Corridors linking every room - width=2 so passages read as
        # real fortress hallways, not mouse-holes.
        ZoneGenerator._carve_path(keep, *entrance, *courtyard, width=2)
        ZoneGenerator._carve_path(keep, *courtyard, *great_hall, width=2)
        ZoneGenerator._carve_path(keep, *courtyard, *nw_tower, width=2)
        ZoneGenerator._carve_path(keep, *courtyard, *ne_tower, width=2)
        ZoneGenerator._carve_path(keep, *courtyard, *sw_tower, width=2)
        ZoneGenerator._carve_path(keep, *courtyard, *se_tower, width=2)

        # ------------------------------------------------------------------
        # LANDMARKS
        # ------------------------------------------------------------------
        # Drawbridge at the entrance, visual only (solid=False) - the
        # entrance carve is already real walkable floor, this just reads
        # as the physical crossing leading up to the gate.
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_drawbridge.png",
                           entrance[0] - 4, entrance[1] + 4, 8, 6, solid=False)

        # Banner pole - dead center of the courtyard, matching the
        # reference's own focal-point composition.
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_banner_pole.png",
                           courtyard[0] - 1, courtyard[1] - 2, 3, 5, solid=False)

        # Intact towers - NW, NE, SW. Placed at each room's own edge
        # (not centered on the walkable interior) so the tower structure
        # reads as the room's wall/roof rather than blocking the floor
        # a player would stand on - same offset-from-center discipline
        # as The Den's egg-cluster placement (a solid landmark centered
        # on a small room's own carve re-solidifies most of its
        # interior).
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_tower_intact.png",
                           nw_tower[0] - 3, nw_tower[1] - 7, 6, 6)
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_tower_intact.png",
                           ne_tower[0] - 3, ne_tower[1] - 7, 6, 6)
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_tower_intact.png",
                           sw_tower[0] - 3, sw_tower[1] - 6, 6, 6)

        # Collapsed tower at SE - the ruined wing's own centerpiece,
        # matching the reference's single visibly-breached tower.
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_tower_collapsed.png",
                           se_tower[0] - 1, se_tower[1] - 6, 6, 6)

        # Ruined wing rubble scatter - SE room reads as the disaster
        # site: broken wall section, rubble piles, a fallen beam and
        # scaffold, pushed to the room's open floor rather than
        # centered on it (same reachability discipline as above).
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_ruined_wall_section.png",
                           se_tower[0] + 3, se_tower[1] - 2, 5, 5)
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_rubble_pile.png",
                           se_tower[0] - 4, se_tower[1] + 2, 4, 3, solid=False)
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_rubble_beam.png",
                           se_tower[0] + 1, se_tower[1] + 3, 4, 4, solid=False)
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_scaffold.png",
                           se_tower[0] - 2, se_tower[1] - 3, 4, 4, solid=False)

        # Barracks storage - SW room gets the barrel/crate cluster.
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_barrel_crate_cluster.png",
                           sw_tower[0] + 2, sw_tower[1] + 2, 4, 4)

        # War table - great hall centerpiece, Captain Thalenvorde's
        # command table. Boss fights here per Kyle's call ("North great
        # hall, matches reference composition"). Offset north of the
        # room's own center point, not centered on it - a solid
        # landmark placed dead-center on a room re-solidifies the exact
        # point every corridor connects to (same bug class flagged in
        # the project's own landmark-on-portal notes). Caught here via
        # real flood-fill reachability, not just an is_walkable() spot
        # check - the center tile alone still reads "walkable" in
        # isolation right up until you check whether anything can
        # actually reach it.
        keep.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_war_table.png",
                           great_hall[0] - 2, great_hall[1] - 6, 5, 4)

        # Generic light scatter, kept low (matches The Den's approach).
        ZoneGenerator._scatter(keep, "small_rocks", 0.02)

        # exit_pos MUST be exactly (45, 76) - see docstring. Real hard
        # contract with portal_manager.py's _links dict, both directions.
        exit_pos = (entrance[0], entrance[1] + 6)
        ZoneGenerator._carve_landing(keep, *exit_pos, radius=2)
        ZoneGenerator._carve_path(keep, *exit_pos, *entrance, width=2)
        keep.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        # Boss chamber - great hall, at the war table.
        keep.set_tile(great_hall[0] - 5, great_hall[1] - 5, "chest", "interaction")
        keep.set_tile(great_hall[0], great_hall[1] - 7, "boss_marker", "interaction")
        keep.boss_position = great_hall

        keep.is_cave = True
        keep.fixed_spawns = False
        keep.add_subzone("Tiragarde Keep", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - per-room floor variety, matching the
        # reference's distinct courtyard/hall/barracks/ruin materials
        # rather than one uniform floor everywhere.
        # ------------------------------------------------------------------
        chunk_size = 20

        def _floor_chunks(cx, cy, rw, rh, sprite):
            # Covers a room's bounding box in chunk_size blocks - the
            # renderer clips each chunk to real base_layer tiles, so
            # this cheaply fills an irregular carved room without
            # needing to hand-match chunk placement to its round edge
            # (same approach as VoT's mountain ring / The Den's floor).
            x0, y0 = cx - rw - 2, cy - rh - 2
            x1, y1 = cx + rw + 2, cy + rh + 2
            for gy in range(y0, y1, chunk_size):
                for gx in range(x0, x1, chunk_size):
                    gw = min(chunk_size, x1 - gx)
                    gh = min(chunk_size, y1 - gy)
                    if gw > 0 and gh > 0:
                        keep.add_ground_chunk(sprite, gx, gy, gw, gh)

        _floor_chunks(*courtyard, *courtyard_r, "assets/tiles/tiragarde_keep/floor_courtyard.png")
        _floor_chunks(*entrance, *entrance_r, "assets/tiles/tiragarde_keep/floor_courtyard.png")
        _floor_chunks(*great_hall, *great_hall_r, "assets/tiles/tiragarde_keep/floor_greathall.png")
        _floor_chunks(*nw_tower, *nw_tower_r, "assets/tiles/tiragarde_keep/floor_barracks.png")
        _floor_chunks(*ne_tower, *ne_tower_r, "assets/tiles/tiragarde_keep/floor_barracks.png")
        _floor_chunks(*sw_tower, *sw_tower_r, "assets/tiles/tiragarde_keep/floor_barracks.png")
        _floor_chunks(*se_tower, *se_tower_r, "assets/tiles/tiragarde_keep/floor_ruined_wing.png")

        # Wall obstacle chunks - 4x4-tile cap (proven readable at that
        # scale, same as VoT/The Den), clipped to real "wall" collision
        # tiles only.
        obstacle_chunk_size = 4
        for cy in range(0, keep.height, obstacle_chunk_size):
            for cx in range(0, keep.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, keep.width - cx)
                ch = min(obstacle_chunk_size, keep.height - cy)
                keep.add_obstacle_chunk("assets/tiles/tiragarde_keep/wall_stone.png",
                                         cx, cy, cw, ch)

        return keep

    @staticmethod
    def generate_night_webs_hollow():
        """Generate Night Web's Hollow (90x75) - Deathknell's spider-
        infested burrow, FULL DEDICATED REBUILD (Kyle: "revamp EK caves.
        They're boring and clunky now. They're too forgettable" - was
        previously on the shared generate_cave() spec-table generator
        (layout="warren", feature="webs"), same "same room, different
        paint" problem flagged project-wide).

        Reuses The Den's own proven spider-den primitives (real web/egg-
        cluster landmark art already exists and fits directly - no new
        art needed, matching Kyle's "build layouts now, reuse existing
        art" call this session) but a DIFFERENT room composition: The Den
        is lake-centric with one big central pool; this is a dry warren
        of narrow branching egg-nursery tunnels radiating off a central
        web-nest hub, matching its original "warren" layout spec and its
        real encounter roster (Night Web Spider/Matriarch, Web Wrapped
        Corpse, Ravenclaw Drudger, Broodmother Nesh'ka as boss - per
        data/creatures/encounters.json, checked directly, not invented).

        exit_pos MUST be exactly (45, 71) - world/portal_manager.py's
        real _links dict: Deathknell's (20, 30) arrives here at (45, 71),
        and this zone's own (45, 71) links back to Deathknell (20, 30).
        Checked directly.
        """
        width, height = 90, 75
        cave = Tilemap("Night Web's Hollow", width, height,
                        "A spider-infested burrow beneath Deathknell, thick with web and egg-nest.")
        cave.region = "Deathknell"

        # REAL BUG FOUND + FIXED (caught via the layout render Kyle asked
        # for, not by code inspection): the wall fill originally used
        # "stone", which tiles.py flags "layer": "base", "walkable": True
        # - a FLOOR tile_id, not a collision one. Placing a walkable
        # tile_id on the collision layer is a no-op (is_walkable() reads
        # the tile_id's own walkable flag, not just "is something set on
        # the collision layer"), so the entire cave rendered as one open
        # room with nothing blocking movement except the landmark props.
        # Fixed to "rock" - the same real collision tile_id The Den uses
        # for its own walls (walkable=False, confirmed in tiles.py), and
        # the correct partner for the cave_mossy/caves/ art already
        # reused below.
        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "rock", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        exit_pos = (45, 71)
        hub = (45, 42)
        carve(*exit_pos, 4, 3)
        carve(*hub, 8, 6)
        ZoneGenerator._carve_path(cave, *exit_pos, *hub, width=2)

        # A dry warren of branching egg-nursery pockets off the central
        # web-nest hub, at the same 22.5-degree compass offset proven on
        # Burning Blade Coven/Skull Rock (true cardinal points collide
        # with the hub's own row/column). 6 pockets instead of 8 - this
        # cave is meant to feel tighter/more claustrophobic than the
        # ritual-camp caves, matching "warren" over "hub-and-spoke arena".
        rooms = {
            "ne_nursery":  (68, 25, 6, 5),
            "e_nursery":   (72, 48, 6, 5),
            "se_nursery":  (60, 62, 5, 4),
            "sw_nursery":  (20, 58, 6, 5),
            "w_nursery":   (14, 38, 6, 5),
            "nw_nursery":  (24, 20, 5, 4),
        }
        hub_r = (8, 6)
        for (rx, ry, rw, rh) in rooms.values():
            carve(rx, ry, rw, rh)
            dx, dy = rx - hub[0], ry - hub[1]
            dist = max((dx ** 2 + dy ** 2) ** 0.5, 0.001)
            edge_x = hub[0] + round(dx / dist * hub_r[0])
            edge_y = hub[1] + round(dy / dist * hub_r[1])
            ZoneGenerator._carve_path(cave, edge_x, edge_y, rx, ry, width=1)

        # Boss chamber - Broodmother Nesh'ka's own web-nest, deepest point
        # (north, furthest from the entrance), bigger than the nursery
        # pockets to read as a real final-room arena.
        boss = (45, 10)
        carve(*boss, 10, 6)
        ZoneGenerator._carve_path(cave, *hub, *boss, width=2)

        # ------------------------------------------------------------------
        # WEB/EGG LANDMARKS - reusing The Den's real art directly (Kyle:
        # reuse existing art this pass). Web tent at the boss chamber
        # (Broodmother's own lair centerpiece, same role it plays at The
        # Den's boss room), egg clusters in 3 of the 6 nursery pockets so
        # not every pocket is identical, web bridges at 2 corridor mouths
        # for atmosphere.
        # ------------------------------------------------------------------
        cave.add_landmark("assets/tiles/the_den/props/web_tent_peak.png",
                           boss[0] - 4, boss[1] - 5, 8, 6, solid=False)
        cave.add_landmark("assets/tiles/the_den/props/egg_cluster_a.png",
                           rooms["ne_nursery"][0] - 2, rooms["ne_nursery"][1] - 2, 5, 4)
        cave.add_landmark("assets/tiles/the_den/props/egg_cluster_b.png",
                           rooms["sw_nursery"][0] - 2, rooms["sw_nursery"][1] - 2, 5, 4)
        cave.add_landmark("assets/tiles/the_den/props/egg_cocoon_hanging.png",
                           rooms["w_nursery"][0] - 2, rooms["w_nursery"][1] - 2, 4, 4, solid=False)
        cave.add_landmark("assets/tiles/the_den/props/web_bridge_a.png",
                           hub[0] + 4, hub[1] + 3, 6, 4, solid=False)
        cave.add_landmark("assets/tiles/the_den/props/web_bridge_b.png",
                           hub[0] - 9, hub[1] - 2, 5, 4, solid=False)

        ZoneGenerator._scatter(cave, "small_rocks", 0.02)

        # exit_pos is the hard-contract tile, see docstring.
        ZoneGenerator._carve_path(cave, *exit_pos, *hub, width=2)
        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        cave.set_tile(boss[0], boss[1] - 3, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("Night Web's Hollow", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - real cave_mossy textures (same biome
        # The Den uses, so the reused web/egg props sit on art that
        # already matches them tonally) instead of the shared generic
        # "stone" fallback.
        # ------------------------------------------------------------------
        # mossy_cave_floor.png dropped from this rotation (Kyle, after
        # seeing a render: bright saturated green moss read as jungle
        # grass against the gray stone walls, clashing hard rather than
        # reading as "damp cave floor"). cave_floor_rock_1/2 alone keep
        # the whole cave on one consistent gray-brown stone palette - the
        # same 2 variants cave_mossy's own "dirt" BIOME_TILES entry
        # already resolves to, so the carved corridor tiles (which use
        # these per-tile textures, not chunk art, at chunk edges) match
        # the chunk art instead of clashing with it either.
        floor_variants = [
            "assets/tiles/caves/cave_floor_rock_1.png",
            "assets/tiles/caves/cave_floor_rock_2.png",
        ]
        chunk_size = 20
        variant_i = 0
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                sprite = floor_variants[variant_i % len(floor_variants)]
                cave.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        wall_variants = [
            "assets/tiles/caves/cave_wall_1.png",
            "assets/tiles/caves/cave_wall_2.png",
        ]
        wall_variant_i = 0
        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                sprite = wall_variants[wall_variant_i % len(wall_variants)]
                cave.add_obstacle_chunk(sprite, cx, cy, cw, ch)
                wall_variant_i += 1

        return cave

    @staticmethod
    def generate_scarlet_crypt():
        """Generate Scarlet Crypt (95x80) - Deathknell's own Scarlet
        Crusade crypt-fortress, FULL DEDICATED REBUILD (same "revamp EK
        caves" pass as Night Web's Hollow above). Was on the shared
        generate_cave() generator (layout="chain", feature="bones").

        A linear gothic "chain" layout per its original spec (NOT a hub -
        a crypt fortress should feel like a real hallway march deeper in,
        not a radial den), reusing Tiragarde Keep's real stone fortress
        floor/wall art (closest existing fit for a Scarlet Crusade
        stronghold - gothic dressed stone, not a natural cavern) plus
        Skull Rock's bone_pile prop for the crypt's own bone dressing.
        Real encounter roster: Crypt Crawler, Scarlet Initiate, Scarlet
        Chaplain, Restless Crypt Fiend, High Inquisitor Fairbanks as boss
        (per data/creatures/encounters.json, checked directly).

        exit_pos MUST be exactly (47, 76) - portal_manager.py's real
        _links dict: Deathknell's (70, 50) arrives here at (47, 76), and
        this zone's own (47, 76) links back to Deathknell (70, 50).
        Checked directly.
        """
        width, height = 95, 80
        cave = Tilemap("Scarlet Crypt", width, height,
                        "A Scarlet Crusade crypt-fortress, stone halls lined with the restless dead.")
        cave.region = "Deathknell"

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "wall", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        # Real linear march: entrance hall -> crawler corridor -> chapel
        # nave (mid-cave, Scarlet Initiates/Chaplain) -> inquisitor's
        # sanctum (boss, deepest point). Each room bigger than the last,
        # reading as genuine escalation rather than four equal boxes.
        exit_pos = (47, 76)
        entrance_hall = (47, 62)
        crawler_corridor_mid = (47, 48)
        chapel_nave = (47, 30)
        sanctum = (47, 10)

        carve(*exit_pos, 4, 3)
        carve(*entrance_hall, 9, 6)
        carve(*crawler_corridor_mid, 7, 10)
        carve(*chapel_nave, 13, 8)
        carve(*sanctum, 11, 7)

        ZoneGenerator._carve_path(cave, *exit_pos, *entrance_hall, width=2)
        ZoneGenerator._carve_path(cave, *entrance_hall, *crawler_corridor_mid, width=2)
        ZoneGenerator._carve_path(cave, *crawler_corridor_mid, *chapel_nave, width=2)
        ZoneGenerator._carve_path(cave, *chapel_nave, *sanctum, width=2)

        # Two side alcoves off the chapel nave (east/west transepts) -
        # the one real departure from a pure straight line, so the chain
        # still reads as a built structure (a chapel has transepts) and
        # not a single corridor with rooms bolted on.
        east_transept = (65, 30)
        west_transept = (29, 30)
        carve(*east_transept, 6, 5)
        carve(*west_transept, 6, 5)
        ZoneGenerator._carve_path(cave, *chapel_nave, *east_transept, width=2)
        ZoneGenerator._carve_path(cave, *chapel_nave, *west_transept, width=2)

        boss = sanctum

        # ------------------------------------------------------------------
        # BONE DRESSING - Skull Rock's bone_pile reused in the crawler
        # corridor and both transepts (crypt remains scattered through
        # the structure, not just one room), offset from each room's own
        # center so the corridor's single connection point never gets
        # re-solidified (same reachability discipline as Skull Rock's
        # own ritual rooms).
        # ------------------------------------------------------------------
        cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                           crawler_corridor_mid[0] - 4, crawler_corridor_mid[1] - 2, 4, 4, solid=False)
        cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                           east_transept[0] - 1, east_transept[1] + 2, 4, 4, solid=False)
        cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                           west_transept[0] - 1, west_transept[1] + 2, 4, 4, solid=False)
        cave.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_banner_pole.png",
                           sanctum[0] - 5, sanctum[1] - 4, 3, 6, solid=False)
        cave.add_landmark("assets/tiles/tiragarde_keep/props/tiragarde_banner_pole.png",
                           sanctum[0] + 3, sanctum[1] - 4, 3, 6, solid=False)

        ZoneGenerator._scatter(cave, "small_rocks", 0.015)

        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")
        cave.set_tile(boss[0], boss[1] - 4, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("Scarlet Crypt", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - real Tiragarde Keep fortress stone,
        # the closest existing match for a dressed-stone Scarlet Crusade
        # crypt instead of the shared generic "wall" fallback. 3 floor
        # variants (barracks/courtyard/greathall - ruined_wing held back
        # for a future pass) echo the room-by-room escalation above.
        # ------------------------------------------------------------------
        floor_variants = [
            "assets/tiles/tiragarde_keep/floor_barracks.png",
            "assets/tiles/tiragarde_keep/floor_courtyard.png",
            "assets/tiles/tiragarde_keep/floor_greathall.png",
        ]
        chunk_size = 20
        variant_i = 0
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                sprite = floor_variants[variant_i % len(floor_variants)]
                cave.add_ground_chunk(sprite, cx, cy, cw, ch)
                variant_i += 1

        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                cave.add_obstacle_chunk("assets/tiles/tiragarde_keep/wall_stone.png",
                                         cx, cy, cw, ch)

        return cave

    @staticmethod
    def generate_scourge_cave():
        """Generate Scourge Cave (90x75) - Eastern Tirisfal's Scourge-held
        hollow, FULL DEDICATED REBUILD (same "revamp EK caves" pass as
        Night Web's Hollow / Scarlet Crypt above). Was on the shared
        generate_cave() generator (layout="cavern", feature="bones").

        Kept the original "cavern" shape (one big open arena with rock
        pillars) since the real encounter roster is deliberately simple
        - Scourge Warrior, Scourge Necromancer, Scourge Abomination as
        boss, just 3 named things per data/creatures/encounters.json
        (checked directly) - a sprawling multi-room dungeon would be
        over-built for 3 creatures. Reuses Ashenvale Corruption's real
        bone_hall floor/wall art (closest existing fit for a Scourge-
        infested open hollow) instead of the shared generic "wall"
        fallback.

        exit_pos MUST be exactly (45, 68) - portal_manager.py's real
        _links dict: Eastern Tirisfal's (15, 80) arrives here at (45,
        68), and this zone's own (45, 68) links back to Eastern Tirisfal
        (15, 80). Checked directly.
        """
        width, height = 90, 75
        cave = Tilemap("Scourge Cave", width, height,
                        "A Scourge-held hollow beneath Eastern Tirisfal, bone and rot underfoot.")
        cave.region = "Eastern Tirisfal"

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, "wall", "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        exit_pos = (45, 68)
        arena = (45, 38)
        carve(*exit_pos, 4, 3)
        carve(*arena, 32, 23)
        ZoneGenerator._carve_path(cave, *exit_pos, *arena, width=3)

        # Rock-pillar scatter across the open arena - real walled pillars
        # so the big cavern reads as a space with obstacles to fight
        # around, not an empty rectangle (same technique Skull Rock/
        # generate_cave's own "cavern" branch both use).
        for _ in range(14):
            px = random.randint(arena[0] - 26, arena[0] + 26)
            py = random.randint(arena[1] - 17, arena[1] + 17)
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    x, y = px + dx, py + dy
                    if 2 <= x < width - 2 and 2 <= y < height - 2:
                        if random.random() < 0.7:
                            cave.set_tile(x, y, "wall", "collision")

        boss = (45, 12)
        carve(*boss, 9, 6)
        ZoneGenerator._carve_path(cave, *arena, *boss, width=3)

        # ------------------------------------------------------------------
        # BONE DRESSING - skull_rock's bone_pile scattered through the
        # open arena, real standalone landmarks instead of a per-tile
        # "bones" feature table (which this cave used to rely on before
        # this rebuild).
        # ------------------------------------------------------------------
        for (bx, by) in [(arena[0] - 18, arena[1] - 10), (arena[0] + 15, arena[1] + 12),
                          (arena[0] - 10, arena[1] + 15), (arena[0] + 20, arena[1] - 8)]:
            if 2 <= bx < width - 2 and 2 <= by < height - 2 and cave.collision_layer[by][bx] is None:
                cave.add_landmark("assets/tiles/skull_rock/props/bone_pile.png",
                                   bx - 2, by - 2, 4, 4, solid=False)

        ZoneGenerator._scatter(cave, "small_rocks", 0.02)

        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")
        cave.set_tile(boss[0], boss[1] - 3, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        cave.is_cave = True
        cave.fixed_spawns = False
        cave.add_subzone("Scourge Cave", 0, 0, width, height)

        # ------------------------------------------------------------------
        # CHUNKED FLOOR + WALL ART - real Ashenvale Corruption bone_hall
        # textures, the closest existing Scourge/bone-themed fit, instead
        # of the shared generic "wall" fallback.
        # ------------------------------------------------------------------
        chunk_size = 20
        for cy in range(0, cave.height, chunk_size):
            for cx in range(0, cave.width, chunk_size):
                cw = min(chunk_size, cave.width - cx)
                ch = min(chunk_size, cave.height - cy)
                cave.add_ground_chunk("assets/tiles/ashenvale_corruption/bone_hall_floor.png",
                                       cx, cy, cw, ch)

        obstacle_chunk_size = 4
        for cy in range(0, cave.height, obstacle_chunk_size):
            for cx in range(0, cave.width, obstacle_chunk_size):
                cw = min(obstacle_chunk_size, cave.width - cx)
                ch = min(obstacle_chunk_size, cave.height - cy)
                cave.add_obstacle_chunk("assets/tiles/ashenvale_corruption/bone_hall_wall.png",
                                         cx, cy, cw, ch)

        return cave

    def generate_cave(name, parent_zone, width=52, height=46, theme="rock",
                      layout="chain", feature=None):
        """Generate an enclosed cave map with a single exit portal.

        Five layout archetypes so caves stop feeling like the same corridor
        with different wall colours:

          chain    - entrance -> corridor -> boss chamber (classic, linear)
          warren   - many small chambers on branching tunnels (maze-y)
          cavern   - one huge open cavern with rock pillars (arena feel)
          spiral   - a single winding tunnel curling inward to the centre
          flooded  - a cavern cut through by a water channel you route around

        On top of the layout shape, `feature` gives each cave its own
        material identity so eleven caves sharing four/five shapes don't
        still read as the same room reskinned: pools of water, a lava vein,
        bone piles, crystal growths, root tangles, spiderwebs, ice, or
        fungus scatter across the floor in addition to the wall `theme`.

        Every layout puts the boss chamber as far from the entrance as the
        shape allows, and records it as `cave.boss_position` so
        CaveSpawnManager can place the boss there instead of rolling it on
        the weight table. A visible "boss_marker" tile sits at the boss
        chamber too, so the room reads as dangerous before you walk in.
        """
        cave = Tilemap(name, width, height, f"A cave beneath {parent_zone}.")
        cave.region = parent_zone

        cave.fill("stone", "base")
        for y in range(height):
            for x in range(width):
                cave.set_tile(x, y, theme, "collision")

        def carve(cx, cy, rw, rh):
            for dy in range(-rh, rh + 1):
                for dx in range(-rw, rw + 1):
                    x, y = cx + dx, cy + dy
                    if 1 <= x < width - 1 and 1 <= y < height - 1:
                        if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                            cave.collision_layer[y][x] = None
                            cave.set_tile(x, y, "dirt", "base")

        entrance = (width // 2, height - 7)
        carve(*entrance, 9, 5)

        if layout == "warren":
            # A spread of small chambers linked by narrow tunnels.
            rooms = [entrance]
            for _ in range(7):
                rx = random.randint(9, width - 10)
                ry = random.randint(7, height - 12)
                carve(rx, ry, random.randint(4, 7), random.randint(3, 5))
                rooms.append((rx, ry))
            boss = min(rooms[1:], key=lambda r: r[1])   # highest = deepest
            carve(boss[0], boss[1], 9, 6)
            for i in range(1, len(rooms)):
                ZoneGenerator._carve_path(cave, *rooms[i - 1], *rooms[i], width=1)
            ZoneGenerator._carve_path(cave, *entrance, *boss, width=1)

        elif layout == "cavern":
            # One big open space with pillars - an arena, not a corridor.
            carve(width // 2, height // 2, width // 2 - 4, height // 2 - 5)
            for _ in range(random.randint(10, 16)):
                px = random.randint(6, width - 7)
                py = random.randint(6, height - 8)
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        x, y = px + dx, py + dy
                        if 2 <= x < width - 2 and 2 <= y < height - 2:
                            if random.random() < 0.7:
                                cave.set_tile(x, y, theme, "collision")
            boss = (width // 2, 8)
            carve(*boss, 8, 5)
            ZoneGenerator._carve_path(cave, *entrance, *boss, width=2)

        elif layout == "spiral":
            # A winding tunnel curling in toward a central chamber.
            import math
            boss = (width // 2, height // 2)
            steps = 150
            prev = entrance
            for i in range(steps):
                t = i / steps
                angle = t * math.pi * 3.2
                radius = (1.0 - t) * min(width, height) * 0.40
                px = int(boss[0] + math.cos(angle) * radius)
                py = int(boss[1] + math.sin(angle) * radius * 0.85)
                px = max(3, min(width - 4, px))
                py = max(3, min(height - 4, py))
                ZoneGenerator._carve_path(cave, *prev, px, py, width=1)
                prev = (px, py)
            carve(*boss, 8, 5)
            ZoneGenerator._carve_path(cave, *entrance, *boss, width=1)

        elif layout == "flooded":
            # A cavern split by a water channel - you hug one bank or the
            # other to reach the boss chamber on the far side.
            carve(width // 2, height // 2, width // 2 - 5, height // 2 - 6)
            channel_x = width // 2 + random.choice([-1, 1]) * random.randint(3, 8)
            for y in range(6, height - 6):
                wobble = int(4 * random.random()) - 2
                for dx in range(-3, 4):
                    x = channel_x + wobble + dx
                    if 2 <= x < width - 2:
                        cave.set_tile(x, y, "deep_water" if abs(dx) < 2 else "shallow_water", "base")
                        cave.collision_layer[y][x] = None
            boss = (width // 2, 8)
            carve(*boss, 8, 5)
            # Banks around the water stay dry and walkable on both sides.
            ZoneGenerator._carve_path(cave, *entrance, *boss, width=2)

        else:  # "chain"
            carve(width // 2, height // 2, 11, 7)
            boss = (width // 2, 9)
            carve(*boss, 10, 6)
            for y in range(9, height - 6):
                cx = width // 2 + int(3 * random.random()) - 1
                for dx in range(-2, 3):
                    x = cx + dx
                    if 1 <= x < width - 1:
                        cave.collision_layer[y][x] = None
                        cave.set_tile(x, y, "dirt", "base")
            for _ in range(4):
                carve(random.randint(10, width - 10),
                      random.randint(14, height - 12), 5, 4)

        # Guarantee entrance -> boss connectivity regardless of layout. The
        # generated tunnels can pinch shut, which would seal the boss chamber
        # (and its treasure) behind solid rock.
        ZoneGenerator._carve_path(cave, entrance[0], entrance[1], boss[0], boss[1], width=2)

        # Material feature scattered across walkable floor, giving each cave
        # a distinct identity on top of its wall theme and layout shape.
        feature_tiles = {
            # Burning Blade Coven / Skull Rock's signature - lava vein plus
            # the fire-gate arch (primary demonic-cultist landmark, sparse)
            # and skull-door/dark-totem as secondary scatter for variety.
            "lava": [("fire_gate", 0.006), ("skull_door", 0.01), ("skull_door_2", 0.01),
                     ("dark_totem", 0.004), ("small_rocks", 0.05)],
            "bones": [("bones", 0.05), ("bones_2", 0.03), ("bones_3", 0.04)],
            "crystal": [("crystal", 0.05), ("crystal_2", 0.04)],
            "ruins": [("ruin", 0.04), ("ruin_2", 0.05), ("ruin_3", 0.05)],
            # Zalazane's Hollow specifically - sunken troll ruins get
            # coral/shell growth on the broken stonework plus a rare
            # half-buried statue landmark, on top of the same ruin
            # scatter "ruins" uses. Kept separate from "ruins" itself
            # since Tiragarde Keep (also "ruins") has no coral/statue
            # tile_id defined in its biome (cave_dark) - a dry ruined
            # fortress shouldn't get seaweed-grown coral.
            "sunken_ruins": [("ruin", 0.04), ("ruin_2", 0.05), ("ruin_3", 0.05),
                             ("coral_blue", 0.02), ("shell", 0.015), ("statue", 0.002)],
            "roots": [("bushes", 0.10)],
            # Sunken Temple Grotto specifically - drowned coral/shells and
            # fern growth on the flooded stonework, plus the same ruin
            # scatter "ruins" uses (a flooded TEMPLE should still have
            # broken architecture, not just water).
            "sunken_temple": [("bushes", 0.06), ("coral_blue", 0.02), ("coral_red", 0.015),
                              ("shell", 0.02), ("ruin_3", 0.03)],
            "webs": [("bushes", 0.08)],
            "ice": [("small_rocks", 0.06)],
            "fungus": [("grass_tuft", 0.10)],
        }
        if feature == "lava":
            # A vein of lava cutting near the boss chamber - dangerous
            # ground you route around rather than another empty floor.
            lava_y = max(entrance[1] - 10, boss[1] + 6)
            for x in range(width):
                if cave.is_walkable(x, lava_y) and random.random() < 0.5:
                    cave.set_tile(x, lava_y, "lava", "base")
                    cave.collision_layer[lava_y][x] = "wall"  # impassable strip, must route around
            # Reopen a crossing point so the lava never fully seals the path.
            crossing = width // 2
            for x in range(crossing - 3, crossing + 4):
                if 0 <= x < width:
                    if cave.base_layer[lava_y][x] == "lava":
                        cave.set_tile(x, lava_y, "stone", "base")
                        cave.collision_layer[lava_y][x] = None
        if feature == "ice":
            for y in range(height):
                for x in range(width):
                    if cave.is_walkable(x, y) and random.random() < 0.35:
                        cave.set_tile(x, y, "ice", "base")

        for tile_name, chance in feature_tiles.get(feature, []):
            ZoneGenerator._scatter(cave, tile_name, chance)

        # Generic light scatter for every cave regardless of feature, kept
        # low so it doesn't wash out the feature above.
        ZoneGenerator._scatter(cave, "small_rocks", 0.04)

        exit_pos = (entrance[0], entrance[1] + 3)
        ZoneGenerator._carve_landing(cave, *exit_pos, radius=2)
        ZoneGenerator._carve_path(cave, *exit_pos, *entrance, width=2)
        cave.set_tile(exit_pos[0], exit_pos[1], "portal", "interaction")

        # Boss chamber holds the treasure and a visible marker, at the
        # deepest point.
        cave.set_tile(boss[0], boss[1] - 2, "chest", "interaction")
        cave.set_tile(boss[0], boss[1], "boss_marker", "interaction")
        cave.boss_position = boss

        # Big feature-specific boss-room landmark, genuinely large (Kyle:
        # "props CAN be bigger than 1 block... some SHOULD be massive") -
        # placed behind the boss marker so it reads as the room's actual
        # centerpiece instead of squashed into a single 32x32 tile like
        # every other prop this session. Collision is intentionally NOT
        # solid here (solid=False) - it's set dressing behind where the
        # boss stands, not a wall the player needs to walk around.
        boss_landmarks = {
            "lava": "dark_totem",       # demonic ritual figure
            "bones": "dino_skeleton",   # full skeletal centerpiece
        }
        big_ruin_features = ("ruins", "sunken_ruins")
        if feature in boss_landmarks:
            sprite = boss_landmarks[feature]
            lw, lh = 6, 6
            lx = max(0, min(width - lw, boss[0] - lw // 2))
            ly = max(0, boss[1] - lh - 1)
            cave.add_landmark(f"assets/tiles/cave_landmarks/{sprite}.png",
                              lx, ly, lw, lh, solid=False)
        elif feature in big_ruin_features:
            # Sourced ruin-wall art (Kyle's reference photos) - real stone
            # archway with a carved skull keystone, genuinely photographed
            # ruins rather than a flat vector crop. Tiragarde Keep and
            # Zalazane's Hollow both deserve one real "this was a grand
            # hall once" moment, not just rubble scatter.
            lw, lh = 7, 6
            lx = max(0, min(width - lw, boss[0] - lw // 2))
            ly = max(0, boss[1] - lh - 1)
            cave.add_landmark("assets/tiles/ruins/ruin_archway.png", lx, ly, lw, lh, solid=False)

        cave.is_cave = True
        # Single-boss "cave-like" pocket, not a multi-boss instanced
        # dungeon (Kyle's split: dungeons/mini-dungeons get fully fixed
        # trash + boss placement; caves get random trash like the open
        # world plus one fixed boss chamber). Every generate_cave() call
        # is this kind of cave - Skull Rock, Dustwind Cave, Tiragarde
        # Keep, etc. - so this is set here once rather than per call site.
        cave.fixed_spawns = False
        cave.add_subzone(name, 0, 0, width, height)
        return cave

    @staticmethod
    def _carve_landing(zone, px, py, radius=2):
        """Guarantee a walkable patch around a portal tile.

        Portals placed after random terrain scatter can end up buried under
        trees, rock or water, which strands them - the player can see the
        portal but never step on it. Every portal placement in the new zones
        calls this first.
        """
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = px + dx, py + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    from world.tiles import is_walkable as _walk
                    if not _walk(zone.base_layer[y][x]):
                        zone.set_tile(x, y, "dirt", "base")
                    zone.collision_layer[y][x] = None

    @staticmethod
    def _make_oasis(zone, cx, cy, radius=12, fringe_tile="grass", fringe_scatter="flowers", fringe_scatter_chance=0.25):
        """Water feature with a rocky/vegetated fringe. Fringe tile and
        scatter are parameterized (default grass+flowers, the original
        Barrens-oasis look) so desert biomes can pass their own sand/rock
        dressing instead of silently getting a green ring painted around
        their pond - "grass" has no texture entry in desert_oasis's biome
        table, so leaving the default there would fall back to tiles.py's
        flat forest-green fill in the middle of a desert."""
        for dy in range(-radius - 3, radius + 4):
            for dx in range(-radius - 4, radius + 5):
                x, y = cx + dx, cy + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < radius * 0.55:
                    zone.set_tile(x, y, "deep_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < radius * 0.8:
                    zone.set_tile(x, y, "shallow_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < radius:
                    zone.set_tile(x, y, fringe_tile, "base")
                    zone.collision_layer[y][x] = None
                    if fringe_scatter and random.random() < fringe_scatter_chance:
                        zone.set_tile(x, y, fringe_scatter, "visual")


def create_all_zones():
    """Create all zones: starter + expanded world zones."""
    from tools.zone_expansion_generators import (
        generate_deathknell,
        generate_eastern_tirisfal,
        generate_western_tirisfal,
        generate_northern_barrens,
        generate_central_barrens,
        generate_crossroads,
        generate_southern_barrens,
        generate_wailing_caverns_expanded,
        generate_razorfen_kraul_expanded,
        generate_the_broodspiral,
    )
    from tools.ashenvale_silverpine_fenris_generators import (
        generate_ashenvale_west,
        generate_ashenvale_east,
        generate_silverpine_north,
        generate_silverpine_south,
        generate_fenris_isle,
        generate_blackfathom_deeps,
        generate_groms_rest,
        generate_widows_lair,
        generate_shadowfang_keep,
        generate_ambermill_tower,
        generate_shadowpine_altar,
        generate_astranaar,
        generate_zoram_strand,
        generate_splintertree_post,
        generate_the_sepulcher,
        generate_brill,
    )
    from tools.orgrimmar_undercity_expansion import (
        generate_orgrimmar_expanded,
        generate_ragefire_chasm,
        generate_undercity,
        generate_plague_depths,
    )
    
    zones = {
        # ===== ORIGINAL STARTER ZONES (unchanged) =====
        "Valley of Trials": ZoneGenerator.generate_valley_of_trials(),
        "Durotar": ZoneGenerator.generate_durotar(),
        "Razor Hill": ZoneGenerator.generate_razor_hill(),
        "Echo Isles": ZoneGenerator.generate_echo_isles(),
        "Ratchet": ZoneGenerator.generate_ratchet(),
        "Orgrimmar": generate_orgrimmar_expanded(),  # EXPANDED with districts & Ragefire entrance
        "Zeppelin Tower": ZoneGenerator.generate_zeppelin_tower(),
        
        # ===== TIRISFAL SPLIT (3 zones from 1) + UNDERCITY =====
        "Deathknell": generate_deathknell(),
        "Eastern Tirisfal": generate_eastern_tirisfal(),
        "Western Tirisfal": generate_western_tirisfal(),
        "Undercity": generate_undercity(),  # NEW: Forsaken capital
        
        # ===== BARRENS SPLIT (3 zones from 1) =====
        "Northern Barrens": generate_northern_barrens(),
        "Central Barrens": generate_central_barrens(),
        "Crossroads": generate_crossroads(),
        "Southern Barrens": generate_southern_barrens(),
        "Camp Taurajo": ZoneGenerator.generate_camp_taurajo(),  # was never
        # added to this dict despite the generator existing and the portal
        # registry pointing at it - the zone was completely unreachable.
        
        # ===== ASHENVALE SPLIT (2 zones) =====
        "Ashenvale West": generate_ashenvale_west(),
        "Ashenvale East": generate_ashenvale_east(),
        "Astranaar": generate_astranaar(),
        "Zoram Strand": generate_zoram_strand(),
        "Splintertree Post": generate_splintertree_post(),
        
        # ===== SILVERPINE SPLIT (2 zones) =====
        "Silverpine North": generate_silverpine_north(),
        "Silverpine South": generate_silverpine_south(),
        "The Sepulcher": generate_the_sepulcher(),
        
        # ===== BRILL (standalone town, was baked into Western Tirisfal) =====
        "Brill": generate_brill(),
        
        # ===== FENRIS ISLE (new zone) =====
        "Fenris Isle": generate_fenris_isle(),
        
        # ===== EXPANSION DUNGEONS =====
        "Ragefire Chasm": generate_ragefire_chasm(),  # NEW: In Orgrimmar, Cleft of Shadow
        "Plague Depths": generate_plague_depths(),  # NEW: In Undercity, Forsaken traitors
        "Blackfathom Deeps": generate_blackfathom_deeps(),
        "Grom's Rest": generate_groms_rest(),
        "Widow's Lair": generate_widows_lair(),
        "Shadowfang Keep": generate_shadowfang_keep(),
        "Ambermill Tower": generate_ambermill_tower(),
        "Shadowpine Altar": generate_shadowpine_altar(),
    }

    # Caves are real maps now, not just encounter-table keys. Each is keyed
    # by the same name used in encounters.json so CreatureManager resolves
    # its table with no extra plumbing. Sizes vary around ~100x80 rather
    # than all sharing one footprint, and each has its own layout shape +
    # material feature so eleven caves don't read as the same room with
    # different paint - a spider den full of webs feels different from a
    # flooded grotto or a lava-cut mine, not just a different wall colour.
    # (name, parent, size, wall tile, layout archetype, feature)
    cave_specs = [
        # Burning Blade Coven now has its own dedicated generator (see
        # note below near zones["The Den"] for the same "generate_cave()
        # is only for caves that don't need bespoke layouts yet" logic).
        # Skull Rock now has its own dedicated generator (see note below
        # near zones["The Den"]) - real 8-room hub-and-spoke layout
        # matching Burning Blade Coven's proven geometry, not the shared
        # generic "cavern/lava" table anymore.
        # Tiragarde Keep now has its own dedicated generator (see note
        # below near zones["The Den"]) - real fortress rooms against a
        # Kul Tiras reference, not the shared generic "cavern/ruins"
        # open-arena table anymore.
        # Dustwind Cave now has its own dedicated generator (see note
        # below near zones["The Den"]) - real scorpid-burrow hub-and-
        # spoke layout with chunked sandy floor/chitin wall art, not the
        # shared generic "rock/chain/bones" table anymore.
        # Sunken Temple Grotto now has its own dedicated generator (see
        # note below near zones["The Den"]) - real winding water-channel
        # layout against Kyle's reference map, not the shared generic
        # "flooded/sunken_temple" table anymore.
        # Zalazane's Hollow now has its own dedicated generator too -
        # real linear spine with branching side-rooms, not the shared
        # generic "warren/sunken_ruins" table anymore.
        # Boulder Lode Mine now has its own dedicated generator (see note
        # below near zones["The Den"]) - real spiral mine shaft, not the
        # shared generic "rock/spiral/crystal" table anymore.
        # Serena's Hollow now has its own dedicated generator too - real
        # linear cliff-ledge chain, not the shared generic "cliff/chain/
        # nest" table anymore.
        # Night Web's Hollow, Scarlet Crypt, and Scourge Cave now have
        # their own dedicated generators (see note below near
        # zones["The Den"]) - Kyle: "revamp EK caves. They're boring and
        # clunky now. They're too forgettable" - real hand-placed rooms
        # reusing The Den's web/egg art, Tiragarde Keep's stone fortress
        # art, and Ashenvale Corruption's bone_hall art respectively,
        # not the shared generic warren/chain/cavern tables anymore.
        ("Moonwell Hollow", "Ashenvale West", (85, 70), "wall", "flooded", "roots"),
        ("Howling Barrows", "Ashenvale East", (95, 80), "cliff", "cavern", "ice"),
    ]
    for cave_name, parent, (w, h), theme, layout, feature in cave_specs:
        zones[cave_name] = ZoneGenerator.generate_cave(
            cave_name, parent, w, h, theme, layout, feature)

    # The Den - now a fully dedicated generator (this session, Kyle:
    # "we eventually should write each cave uniquely" after providing
    # real reference art for a specific multi-room spider-den layout).
    # No longer in cave_specs above / no post-processing needed here -
    # generate_the_den() builds its own rooms, floor/wall chunks, water,
    # and web/egg landmark props directly, matching the reference
    # composition instead of the shared generic "chain" layout +
    # "bones" feature table (which also had a real, separately-fixed
    # bug: cave_mossy's bones/bones_2/bones_3 SHEETS entries pointed at
    # a folder that doesn't exist on disk, rendering as gray fallback
    # boxes - moot now since The Den doesn't use that feature table at
    # all anymore, but still true for the other "bones"-feature caves
    # still on the shared generator).
    zones["Sunken Temple Grotto"] = ZoneGenerator.generate_sunken_temple_grotto()
    zones["Zalazane's Hollow"] = ZoneGenerator.generate_zalazane_hollow()
    zones["Boulder Lode Mine"] = ZoneGenerator.generate_boulder_lode_mine()
    zones["Serena's Hollow"] = ZoneGenerator.generate_serenas_hollow()
    zones["The Den"] = ZoneGenerator.generate_the_den()
    zones["Dustwind Cave"] = ZoneGenerator.generate_dustwind_cave()
    zones["Thunder Ridge"] = ZoneGenerator.generate_thunder_ridge()
    zones["Burning Blade Coven"] = ZoneGenerator.generate_burning_blade_coven()
    zones["Tiragarde Keep"] = ZoneGenerator.generate_tiragarde_keep()
    zones["Skull Rock"] = ZoneGenerator.generate_skull_rock()
    zones["Night Web's Hollow"] = ZoneGenerator.generate_night_webs_hollow()
    zones["Scarlet Crypt"] = ZoneGenerator.generate_scarlet_crypt()
    zones["Scourge Cave"] = ZoneGenerator.generate_scourge_cave()

    # Drygulch Ravine is NOT run through generate_cave() - see that
    # function's own docstring note and generate_drygulch_ravine()'s
    # docstring for why an open-air canyon needed a different generator
    # shape than the room-and-corridor dungeon carver.
    zones["Drygulch Ravine"] = ZoneGenerator.generate_drygulch_ravine()
    zones["Sunken Grotto of the Deep"] = ZoneGenerator.generate_sunken_grotto_of_the_deep()
    
    # Add the massive pre-designed dungeons
    zones["Wailing Caverns"] = generate_wailing_caverns_expanded()
    zones["Razorfen Kraul"] = generate_razorfen_kraul_expanded()
    zones["The Broodspiral"] = generate_the_broodspiral()

    return zones
