"""
Zone generators for the massive mid-tier expansion.

5 overworld zones:
- Ashenvale West (220x200) — Alliance/Furbolg/Druid territory
- Ashenvale East (220x200) — Demon/Satyr/Twilight stronghold
- Silverpine North (200x190) — Haunted, spiders, eerie
- Silverpine South (200x190) — Forsaken military, organized undeath
- Fenris Isle (160x140) — Isolated island, worgen territory, Rotting Kobolds

6 dungeons embedded in the above.
"""

import random
import math
from world.tilemap import Tilemap
from world.zone_generator import ZoneGenerator


def generate_ashenvale_west():
    """Ashenvale West (220x200) — Alliance/Furbolg territory, WoW vibes."""
    zone = Tilemap("Ashenvale West", 220, 200,
                   "Ancient night elf lands, corrupted slowly. Alliance forward base.")
    zone.region = "Kalimdor - Western Forest"

    # Base: forest
    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.20:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.06:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # WEST COAST — per the real Ashenvale map, water runs the length of
    # the whole western edge (this is the coastline Zoram Strand and
    # Blackfathom Deeps both open onto), not just the small inland lakes
    # this zone already had. Previously there was no water anywhere along
    # x<10 at all - flagged directly by Kyle against the reference map.
    # A ragged/inlet coastline, not a flat sea wall - matches the
    # reference map's irregular shoreline better than a straight edge,
    # and reads as a real coast rather than an invisible wall. Placed
    # BEFORE the forest/rock scatter below so those features don't get
    # stamped on top of it, and routes around the Zoram Strand portal
    # sand patch (~x:5-30, y:22-38) and the Blackfathom Deeps portal
    # (30,20) so neither gets submerged.
    def _near_portal_sand(x, y):
        # Zoram Strand's own beach patch - already sand/portal, leave it
        # alone rather than overwriting with open sea.
        if 0 <= x <= 32 and 18 <= y <= 40:
            return True
        return False

    for y in range(zone.height):
        # Irregular coastline depth: a slow sine-ish wobble plus per-row
        # jitter so the shore isn't a ruler-straight line. Widened
        # substantially this session (Kyle: "the west coast NEEDS water
        # for it... wider/more substantial" - the old 4-12 tile range
        # read as a thin ragged strip, not real open sea matching the
        # reference map's genuinely wide western coastline).
        depth = 22 + int(14 * abs((y % 37) - 18) / 18) + random.randint(-4, 4)
        depth = max(16, min(depth, 40))
        for x in range(0, depth):
            if _near_portal_sand(x, y):
                continue
            zone.set_tile(x, y, "deep_water" if x < depth - 6 else "shallow_water", "base")
            zone.collision_layer[y][x] = None
        # A real sandy fringe between forest and open water so the
        # transition doesn't jump straight from grass to sea - widened
        # from 2 to 4 tiles to match the deeper water proportionally.
        for x in range(depth, depth + 4):
            if _near_portal_sand(x, y) or x >= zone.width:
                continue
            zone.set_tile(x, y, "sand", "base")
            zone.collision_layer[y][x] = None

    # Dense forest coverage
    for _ in range(400):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        if random.random() < 0.45:
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "tree", "collision")

    # WATER — per the real Ashenvale map, this half of the zone (Zoram
    # Strand through Astranaar) has two real lakes: one just north of
    # Astranaar, one further north near Maestra's Post. Neither existed at
    # all before - the whole zone was zero water tiles.
    def _lake(cx, cy, rw, rh):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                if (dx * dx) / (rw * rw) + (dy * dy) / (rh * rh) <= 1.0:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.collision_layer[y][x] = None
                        depth = (dx * dx) / (rw * rw) + (dy * dy) / (rh * rh)
                        zone.set_tile(x, y, "deep_water" if depth < 0.5 else "shallow_water", "base")

    _lake(105, 130, 16, 12)   # lake north of Astranaar
    _lake(70, 55, 12, 10)     # lake near Maestra's Post

    # ASTRANAAR — now a standalone zone (Astranaar), reached via portal.
    # This used to be a full town baked directly into Ashenvale West; every
    # town in the game needs to be its own zone, so it's been pulled out.
    astranaar_cx, astranaar_cy = 110, 160
    for dy in range(-8, 9):
        for dx in range(-10, 11):
            x, y = astranaar_cx + dx, astranaar_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(astranaar_cx, astranaar_cy, "portal", "interaction")  # -> Astranaar

    # ZORAM STRAND — now a standalone zone (Zoram Strand), reached via
    # portal. Per the real map this sits on the far NW coast, so its portal
    # here has moved to the NW corner (was SW before, which didn't match).
    zoram_cx, zoram_cy = 15, 30
    for dy in range(-8, 9):
        for dx in range(-10, 11):
            x, y = zoram_cx + dx, zoram_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "sand", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(zoram_cx, zoram_cy, "portal", "interaction")  # -> Zoram Strand

    # MAESTRA'S POST (northwest, between Zoram Strand and Astranaar) — new
    # subzone matching the real map. A small sentinel watchpost overlooking
    # the lake. Positioned clear of the lake basin itself (lake is centered
    # at 70,55 radius 12x10) so the building doesn't end up underwater.
    # NPC stands just outside the building footprint, not inside it - the
    # building loop fills solid with no door (same "sealed box" pattern
    # fixed earlier for real dungeons; not worth a door-breach helper for
    # one small decorative watchpost, just don't place the NPC inside it).
    for (bx, by) in [(85, 48)]:
        for dy in range(4):
            for dx in range(6):
                x, y = bx + dx, by + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.set_tile(x, y, "wall", "collision")
    zone.set_tile(85, 53, "npc", "interaction")
    # Guard a small clearing (not just the single NPC tile) against the
    # forest scatter above - one lucky tree adjacent to the tile was enough
    # to pinch off the only approach, even with the tile itself guaranteed
    # walkable.
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 85 + dx, 53 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.add_subzone("Maestra's Post", 45, 30, 50, 45)

    # RAGGED HIGHLANDS (northeast) — Furbolg territory
    for y in range(20, 60):
        for x in range(130, 200):
            if random.random() < 0.35:
                zone.set_tile(x, y, "rock", "collision")

    zone.add_subzone("Ragged Highlands", 130, 20, 70, 40)

    # MOONWHISPER GROVE (southeast) — Druid sanctuary, sparse
    zone.add_subzone("Moonwhisper Grove", 160, 100, 50, 60)

    # Portal to Blackfathom (northwest coast)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 30 + dx, 20 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(30, 20, "portal", "interaction")

    # MOONWELL — a real surface moonwell, not just a cave-entrance portal
    # standing in for one. Night elf moonwells are shallow circular pools
    # with a raised altar at the center; built that here, north of
    # Astranaar next to its lake, matching the real map's cluster of small
    # lakes/moonwells in that area. The Moonwell Hollow CAVE entrance
    # (separate zone, already existed) is kept as an adjacent portal at the
    # altar, so the surface feature and the cave both read as the same
    # place instead of the portal floating in an empty clearing.
    moonwell_cx, moonwell_cy = 110, 90
    for dy in range(-7, 8):
        for dx in range(-7, 8):
            if dx * dx + dy * dy <= 49:
                x, y = moonwell_cx + dx, moonwell_cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
                    ring = dx * dx + dy * dy
                    if ring > 25:
                        zone.set_tile(x, y, "stone", "base")   # mossy rim
                    elif ring > 4:
                        zone.set_tile(x, y, "shallow_water", "base")
                    else:
                        zone.set_tile(x, y, "deep_water", "base")  # sacred pool center
    zone.set_tile(moonwell_cx, moonwell_cy - 8, "portal", "interaction")   # -> Moonwell Hollow (cave), on the mossy rim north of the pool
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = moonwell_cx + dx, moonwell_cy - 8 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None  # same approach-pinch guard as Maestra's Post above

    # Exit east to Ashenvale East
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = zone.width - 5 + dx, 100 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(zone.width - 5, 100, "portal", "interaction")  # -> Ashenvale East

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "we need tiles for it... we
    # have nothing" - real Ashenvale-specific art now exists, zero
    # chunked art calls existed anywhere in this function before now).
    # Real per-region texture assignment using the same overlap-matched
    # pattern proven on Durotar/Barrens/Orgrimmar - a chunk's CENTER can
    # land just outside a region's rect even when most of its area
    # overlaps it, so this checks real overlap, not center-point
    # containment.
    # ------------------------------------------------------------------
    ashenvale = "assets/tiles/ashenvale"
    region_terrain = [
        {"rect": (130, 20, 70, 40), "variants": [f"{ashenvale}/rocky_forest_ground.png", f"{ashenvale}/forest_floor_roots.png"]},  # Ragged Highlands - furbolg/hilly
        {"rect": (45, 30, 50, 45), "variants": [f"{ashenvale}/forest_floor_light.png"]},   # Maestra's Post
        {"rect": (160, 100, 50, 60), "variants": [f"{ashenvale}/forest_floor_dense.png"]}, # Moonwhisper Grove - druid sanctuary, denser
    ]
    default_variants = [f"{ashenvale}/forest_floor_light.png", f"{ashenvale}/forest_floor_dense.png", f"{ashenvale}/forest_floor_roots.png"]

    def chunk_variants_for(cx, cy, cs):
        for region in region_terrain:
            rx, ry, rw, rh = region["rect"]
            overlaps = not (cx + cs <= rx or cx >= rx + rw or cy + cs <= ry or cy >= ry + rh)
            if overlaps:
                return region["variants"]
        return default_variants

    chunk_size = 20
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            # Skip chunks entirely over water - already real base tiles
            # from the coastline/lake/moonwell carves above.
            if all(zone.base_layer[cy + dy][cx + dx] in ("deep_water", "shallow_water", "sand")
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Lake water - real tileable, replacing the flat deep_water/
    # shallow_water default color on both lakes.
    for (lcx, lcy, lrw, lrh) in [(105, 130, 16, 12), (70, 55, 12, 10)]:
        x0, y0 = lcx - lrw - 2, lcy - lrh - 2
        x1, y1 = lcx + lrw + 2, lcy + lrh + 2
        for gy in range(y0, y1, chunk_size):
            for gx in range(x0, x1, chunk_size):
                gw = min(chunk_size, x1 - gx)
                gh = min(chunk_size, y1 - gy)
                if gw > 0 and gh > 0:
                    zone.add_ground_chunk(f"{ashenvale}/lake_water.png", gx, gy, gw, gh)

    # Coastline - real sand + shallow water textures along the whole
    # west edge, matching the widened coastline carved above.
    for gy in range(0, zone.height, chunk_size):
        gh = min(chunk_size, zone.height - gy)
        zone.add_ground_chunk(f"{ashenvale}/coastal_sand.png", 0, gy, 44, gh)
    zone.add_ground_chunk(f"{ashenvale}/shallow_coastal_water.png", 0, 0, 20, zone.height)

    # Moonwell - real pool water + mossy rim, replacing the flat
    # default-color rings from the carve above.
    zone.add_ground_chunk(f"{ashenvale}/moonwell_water.png",
                           moonwell_cx - 5, moonwell_cy - 5, 10, 10)
    zone.add_ground_chunk(f"{ashenvale}/moonwell_rim.png",
                           moonwell_cx - 9, moonwell_cy - 9, 18, 18)
    zone.add_landmark(f"{ashenvale}/props/moonwell_altar.png",
                       moonwell_cx - 3, moonwell_cy - 3, 6, 6, solid=False)

    # ------------------------------------------------------------------
    # TREE PROPS - real canopy trees replacing the flat "tree" collision
    # tile scattered across the forest. Kept sparse relative to the
    # existing collision-tile forest (that scatter already reads as
    # dense woodland at the tile-color level; these are real visible
    # landmark trees layered on top at fewer, more deliberate spots so
    # the whole map isn't wall-to-wall tree sprites).
    # ------------------------------------------------------------------
    tree_variants = [f"{ashenvale}/props/large_canopy_tree.png",
                      f"{ashenvale}/props/medium_canopy_tree.png",
                      f"{ashenvale}/props/canopy_tree_cluster.png"]
    tree_i = 0
    for _ in range(70):
        x = random.randint(50, zone.width - 10)
        y = random.randint(10, zone.height - 10)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(tree_variants[tree_i % len(tree_variants)], x, y, 6, 6, solid=False)
            tree_i += 1

    # Ferns and fallen logs scattered lightly through the forest floor -
    # small enough footprint to not need the same restraint as the
    # canopy trees above.
    for _ in range(30):
        x = random.randint(50, zone.width - 10)
        y = random.randint(10, zone.height - 10)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(f"{ashenvale}/props/fern_cluster.png", x, y, 3, 3, solid=False)

    # Rock outcrops + furbolg props in Ragged Highlands specifically.
    for _ in range(10):
        x = random.randint(133, 197)
        y = random.randint(23, 57)
        if zone.base_layer[y][x] not in ("deep_water", "shallow_water") and zone.collision_layer[y][x] is None:
            sprite = f"{ashenvale}/props/rock_outcrop_large.png" if random.random() < 0.5 else f"{ashenvale}/props/rock_outcrop_small.png"
            zone.add_landmark(sprite, x, y, 5, 5)
    zone.add_landmark(f"{ashenvale}/props/furbolg_totem.png", 145, 35, 3, 5, solid=False)
    zone.add_landmark(f"{ashenvale}/props/furbolg_den_entrance.png", 165, 45, 6, 5)

    # Stone archway - a single real "ancient ruin" point of interest in
    # Moonwhisper Grove, matching its own druid-sanctuary flavor.
    zone.add_landmark(f"{ashenvale}/props/stone_archway.png", 175, 120, 5, 5)

    return zone


def generate_ashenvale_east():
    """Ashenvale East (220x200) — mostly healthy forest (Raynewood/Warsong
    Lumber Camp), with the demonic corruption confined to three real
    trouble spots (Satyr's Throne, Twilight Barrow, The Demon Wastes) -
    NOT the whole zone. Was previously "corrupted grass" applied
    uniformly across all 220x200 tiles regardless of proximity to any
    named danger zone, which read as the entire zone being dead - fixed
    per Kyle's correction, see the corruption_factor()/falloff comment
    on the base ground fill below."""
    zone = Tilemap("Ashenvale East", 220, 200,
                   "Mostly healthy Kaldorei forest - Raynewood, Warsong "
                   "Lumber Camp - with real demonic corruption confined to "
                   "Satyr's Throne, Twilight Barrow, and the Demon Wastes.")
    zone.region = "Kalimdor - Eastern Forest"

    # Base: this used to be "corrupted grass" applied UNIFORMLY across the
    # whole 220x200 zone (85% dirt / 15% grass everywhere) even though the
    # zone's own subzones (Satyr's Throne, Twilight Barrow, The Demon
    # Wastes, defined below) clearly mark only SPECIFIC areas as corrupted
    # - the flavour text/docstring calling the whole zone "twilight
    # apocalypse" was the tell that nobody had actually scoped where the
    # corruption should read. Per the real Ashenvale map and Kyle's
    # correction, only the demon-controlled pockets should look dead;
    # Raynewood/Warsong Lumber Camp and the rest of the forest should read
    # the same lush green as Ashenvale West. Fixed by defining the
    # corruption rects FIRST (same coordinates the subzones below use) and
    # making the ground fill check against them per-tile, with a soft
    # falloff band so the transition isn't a hard grass/dirt cliff edge.
    corruption_zones = [
        (100, 40, 80, 60),    # Satyr's Throne
        (160, 80, 50, 60),    # Twilight Barrow
        (140, 150, 60, 45),   # The Demon Wastes
    ]
    falloff = 12  # tiles of blended transition around each corrupted rect

    def _corruption_factor(x, y):
        """1.0 = fully corrupted (inside a zone), 0.0 = fully clean,
        values between = inside the falloff band around a zone's edge."""
        best = 0.0
        for (zx, zy, zw, zh) in corruption_zones:
            # distance outside the rect on each axis (0 if inside)
            dx = max(zx - x, 0, x - (zx + zw))
            dy = max(zy - y, 0, y - (zy + zh))
            dist = max(dx, dy)
            if dist <= 0:
                factor = 1.0
            elif dist >= falloff:
                factor = 0.0
            else:
                factor = 1.0 - (dist / falloff)
            best = max(best, factor)
        return best

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            corruption = _corruption_factor(x, y)
            r = random.random()
            if corruption >= 1.0:
                # Fully inside a corrupted zone - keep the old sparse/
                # scorched dirt read, same ratio as before.
                if r < 0.15:
                    zone.set_tile(x, y, "grass", "base")
                if r < 0.08 and random.random() < 0.5:
                    zone.set_tile(x, y, "rock", "collision")
            elif corruption <= 0.0:
                # Clean forest - same lush grass-majority fill as
                # Ashenvale West, not the old 85%-dirt default.
                if r > 0.12:
                    zone.set_tile(x, y, "grass", "base")
                if r < 0.03:
                    zone.set_tile(x, y, "rock", "collision")
            else:
                # Falloff band - blend the two grass probabilities so the
                # corruption reads as fraying outward, not a hard edge.
                grass_chance = 0.88 - (0.73 * corruption)
                if r < grass_chance:
                    zone.set_tile(x, y, "grass", "base")

    # Demonic forest (sparse, burned) - was scattered across the ENTIRE
    # zone regardless of corruption, same bug as the base ground fill
    # above. Now only spawns inside/near a corruption zone (same
    # corruption_factor check), so dead trees don't show up in the clean
    # forest half.
    for _ in range(250):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        if _corruption_factor(cx, cy) > 0.3 and random.random() < 0.35:
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "dead_tree", "collision")

    # WATER — per the real Ashenvale map, this half (Raynewood Retreat
    # through Warsong Lumber Camp) has a lake near Talondeep Path / south
    # of Satyrnaar. Zero water existed here before. Kept it reading as
    # stagnant/corrupted rather than a pristine lake, matching this half's
    # existing demonic/twilight theme.
    def _corrupted_pool(cx, cy, rw, rh):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                if (dx * dx) / (rw * rw) + (dy * dy) / (rh * rh) <= 1.0:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.collision_layer[y][x] = None
                        depth = (dx * dx) / (rw * rw) + (dy * dy) / (rh * rh)
                        zone.set_tile(x, y, "deep_water" if depth < 0.5 else "shallow_water", "base")

    _corrupted_pool(55, 130, 14, 11)

    # EAST RIVER (Kyle, this session: "the east coast has a river" - per
    # the real Ashenvale map, a real river runs north-south through this
    # half of the zone, roughly through the Raynewood Retreat/Talondeep
    # Path stretch. Zero river existed here before - this half had one
    # small pool and nothing else. Winding path (not a straight cut)
    # threading between the real fixed points on this map: west of
    # Splintertree Post (110,160), east of the Ashenvale-West entry
    # (4,100), feeding into (not overlapping) the existing corrupted
    # pool at (55,130) the way a real river feeds a pond, and staying
    # clear of Satyr's Throne/Twilight Barrow/Demon Wastes (all
    # x>=100) and every portal on this map.
    river_points = [
        (75, 0), (72, 30), (68, 60), (62, 90), (58, 118),
        (55, 130),  # merges into the existing corrupted pool here
        (52, 150), (48, 175), (45, 199),
    ]
    river_width = 5
    for i in range(len(river_points) - 1):
        x0, y0 = river_points[i]
        x1, y1 = river_points[i + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            t = s / steps
            cx = round(x0 + (x1 - x0) * t)
            cy = round(y0 + (y1 - y0) * t)
            for dy in range(-river_width, river_width + 1):
                for dx in range(-river_width, river_width + 1):
                    if dx * dx + dy * dy <= river_width * river_width:
                        x, y = cx + dx, cy + dy
                        if 0 <= x < zone.width and 0 <= y < zone.height:
                            zone.collision_layer[y][x] = None
                            dist = (dx * dx + dy * dy) ** 0.5
                            zone.set_tile(x, y, "deep_water" if dist < river_width - 2 else "shallow_water", "base")

    # A real sandy/dirt bank fringe along the river, same "transition
    # texture, not a hard grass-to-water cliff" approach as the west
    # coastline.
    for i in range(len(river_points) - 1):
        x0, y0 = river_points[i]
        x1, y1 = river_points[i + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            t = s / steps
            cx = round(x0 + (x1 - x0) * t)
            cy = round(y0 + (y1 - y0) * t)
            for dy in range(-river_width - 2, river_width + 3):
                for dx in range(-river_width - 2, river_width + 3):
                    dist = (dx * dx + dy * dy) ** 0.5
                    if river_width < dist <= river_width + 2:
                        x, y = cx + dx, cy + dy
                        if 0 <= x < zone.width and 0 <= y < zone.height:
                            if zone.base_layer[y][x] not in ("deep_water", "shallow_water"):
                                zone.set_tile(x, y, "dirt", "base")
                                zone.collision_layer[y][x] = None

    # SPLINTERTREE POST — now a standalone zone (Splintertree Post),
    # reached via portal. Was a full outpost baked directly into Ashenvale
    # East; every town in the game needs to be its own zone.
    splintertree_cx, splintertree_cy = 110, 160
    for dy in range(-8, 9):
        for dx in range(-10, 11):
            x, y = splintertree_cx + dx, splintertree_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(splintertree_cx, splintertree_cy, "portal", "interaction")  # -> Splintertree Post

    # SATYR'S THRONE (center-north) — Dense satyr stronghold
    zone.add_subzone("Satyr's Throne", 100, 40, 80, 60)

    # TWILIGHT BARROW (east) — Void corruption
    for y in range(80, 140):
        for x in range(160, 210):
            if random.random() < 0.3:
                zone.set_tile(x, y, "rock", "collision")

    zone.add_subzone("Twilight Barrow", 160, 80, 50, 60)

    # THE DEMON WASTES (southeast, near Splintertree) — Scorched earth.
    # Per the real Ashenvale map, the demon-corrupted patch sits southeast
    # of Splintertree Post, not west of it - moved to match.
    for y in range(150, 195):
        for x in range(140, 200):
            if random.random() < 0.25:
                zone.set_tile(x, y, "small_rocks", "visual")

    zone.add_subzone("The Demon Wastes", 140, 150, 60, 45)

    # Portal to Grom's Rest - relocated southeast of Splintertree Post into
    # the Demon Wastes pocket, matching the real map's corrupted area
    # sitting SE of Splintertree/Satyrnaar rather than dead-center north
    # of it.
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 165 + dx, 175 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(165, 175, "portal", "interaction")

    # Howling Barrows entrance - far east, near the Azshara border, north
    # of Grom's Rest. An ancient furbolg burial cavern, tucked deep in the
    # mountains past the Twilight Barrow.
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = 200 + dx, 40 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(200, 40, "portal", "interaction")   # -> Howling Barrows

    # Entry from Ashenvale West (west edge)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = 4 + dx, 100 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(4, 100, "portal", "interaction")   # -> Ashenvale West

    # Portal south to Northern Barrens (Splintertree Post is the gateway
    # from the Barrens up into Ashenvale)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = 110 + dx, zone.height - 5 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(110, zone.height - 5, "portal", "interaction")  # -> Northern Barrens

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "we need tiles for it").
    # Clean forest gets the same real Ashenvale ground set as the West
    # half; the 3 real corruption zones get the demonic-corruption set
    # instead - matching the SAME corruption_factor() rects already
    # used for the base ground fill above, so the chunked art lines up
    # with the falloff that already reads correctly at the tile-color
    # level. satyr_camp_floor.png (Satyr's Throne's own real tile) took
    # 3 attempts to land clean - the first two both had a real seam
    # from a large ritual sigil placed too close to the tile edge,
    # confirmed via measured edge-diff and a 3x3 tiled preview, not
    # just eyeballed. The 3rd attempt, with the sigil dropped entirely
    # per Kyle's "simpler tile" call, passed clean.
    # ------------------------------------------------------------------
    ashenvale = "assets/tiles/ashenvale"
    corruption = "assets/tiles/ashenvale_corruption"

    def chunk_variants_for(cx, cy, cs):
        # Corruption zones use their OWN corruption_factor() at the
        # chunk's center - matches the base ground fill's own per-tile
        # logic closely enough at chunk granularity (20x20) without
        # needing a second overlap-rect system.
        factor = _corruption_factor(cx + cs // 2, cy + cs // 2)
        if factor >= 0.6:
            # Fully corrupted - which specific set depends on which
            # named zone's rect this chunk falls in.
            for (zx, zy, zw, zh), tex in [
                ((100, 40, 80, 60), f"{corruption}/satyr_camp_floor.png"),  # Satyr's Throne - real tile landed (3rd attempt, simplified per Kyle's "simpler tile" call - clean seams verified, no more scorched_floor substitute needed)
                ((160, 80, 50, 60), f"{corruption}/void_floor.png"),        # Twilight Barrow
                ((140, 150, 60, 45), f"{corruption}/scorched_floor.png"),   # The Demon Wastes
            ]:
                if zx <= cx + cs // 2 < zx + zw and zy <= cy + cs // 2 < zy + zh:
                    return [tex]
            return [f"{corruption}/scorched_floor.png"]
        elif factor > 0.15:
            # Falloff band - corrupted_ground.png reads as the "fraying
            # outward" transition texture, matching the base fill's own
            # blended grass-chance logic in spirit.
            return [f"{ashenvale}/corrupted_ground.png"]
        else:
            return [f"{ashenvale}/forest_floor_light.png", f"{ashenvale}/forest_floor_dense.png"]

    chunk_size = 20
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            if all(zone.base_layer[cy + dy][cx + dx] in ("deep_water", "shallow_water")
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # River + corrupted pool water - real tileable, matching the
    # stagnant/corrupted mood already established for this half.
    for gy in range(0, zone.height, chunk_size):
        gh = min(chunk_size, zone.height - gy)
        # River water uses the West half's real lake_water texture -
        # same "natural forest water" material, this river isn't
        # corrupted itself (it feeds the pool, doesn't originate from
        # the demon zones).
        zone.add_ground_chunk(f"{ashenvale}/lake_water.png", 35, gy, 45, gh)
    zone.add_ground_chunk(f"{ashenvale}/lake_water.png", 41, 119, 28, 22)  # corrupted pool itself

    # ------------------------------------------------------------------
    # DEMONIC PROPS - real landmarks in each of the 3 corruption zones,
    # matching their own established flavor (Satyr's Throne = ritual/
    # throne, Twilight Barrow = void crystal, Demon Wastes = fel fire).
    # ------------------------------------------------------------------
    zone.add_landmark(f"{corruption}/props/satyr_throne.png", 135, 65, 6, 7)
    zone.add_landmark(f"{corruption}/props/twisted_dead_tree_cluster.png", 115, 55, 6, 6, solid=False)
    zone.add_landmark(f"{corruption}/props/twisted_dead_tree_cluster.png", 160, 70, 6, 6, solid=False)

    zone.add_landmark(f"{corruption}/props/void_crystal_formation.png", 180, 105, 5, 5)
    zone.add_landmark(f"{corruption}/props/void_crystal_formation.png", 195, 130, 5, 5)

    zone.add_landmark(f"{corruption}/props/fel_fire_brazier.png", 160, 170, 4, 5, solid=False)
    zone.add_landmark(f"{corruption}/props/fel_fire_brazier.png", 175, 185, 4, 5, solid=False)

    # ------------------------------------------------------------------
    # HEALTHY FOREST TREES - same real canopy props as West, scattered
    # through the clean (non-corrupted) portion of this half only.
    # ------------------------------------------------------------------
    tree_variants = [f"{ashenvale}/props/large_canopy_tree.png",
                      f"{ashenvale}/props/medium_canopy_tree.png",
                      f"{ashenvale}/props/canopy_tree_cluster.png"]
    tree_i = 0
    for _ in range(60):
        x = random.randint(10, zone.width - 10)
        y = random.randint(10, zone.height - 10)
        if _corruption_factor(x, y) > 0.15:
            continue
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(tree_variants[tree_i % len(tree_variants)], x, y, 6, 6, solid=False)
            tree_i += 1

    return zone


def generate_silverpine_north():
    """Silverpine North (200x190) — Haunted, spiders, eerie."""
    zone = Tilemap("Silverpine North", 200, 190,
                   "Haunted forests, spider-infested, undead corruption creeping in.")
    zone.region = "Eastern Kingdoms - Lordaeron"

    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.18:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.07:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Thick forest
    for _ in range(350):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        if random.random() < 0.50:
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "tree", "collision")

    # RAVEN HILL CEMETERY (west) — Burial grounds
    zone.add_subzone("Raven Hill Cemetery", 30, 60, 50, 60)

    # SHADOWSPRING POOLS (center) — Marshland
    for y in range(80, 130):
        for x in range(80, 140):
            if random.random() < 0.4:
                zone.set_tile(x, y, "shallow_water", "base")
                zone.collision_layer[y][x] = None

    zone.add_subzone("Shadowspring Pools", 80, 80, 60, 50)

    # PYREWOOD VILLAGE (north) — Burned ruins. small_rocks debris scatter.
    # Was uniform random at 30% density across the whole ~900-tile rect -
    # the real art (a single gray boulder icon, correctly wired, not a
    # bug) tiled edge-to-edge at that density read as solid static noise
    # rather than rubble (Kyle: "wtf happened in pyrewood"). Now scattered
    # in small clumps at a much lower overall rate, so it reads as
    # burn-debris piles here and there instead of a uniform texture.
    for _ in range(14):
        clump_x = random.randint(70, 139)
        clump_y = random.randint(10, 39)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                x, y = clump_x + dx, clump_y + dy
                if 70 <= x < 140 and 10 <= y < 40 and random.random() < 0.5:
                    zone.set_tile(x, y, "small_rocks", "visual")

    zone.add_subzone("Pyrewood Village", 70, 10, 70, 30)

    # NPCs - sp_north_scout already existed in ambient_npcs.json with no
    # matching walkable tile anywhere in this generator (an orphaned
    # entry from an earlier pass); this session adds the real tile for
    # it plus 2 new quest-line givers (sp_north_cemetery_keeper,
    # sp_north_pools_warden). Clear a small radius against the thick
    # forest scatter above.
    for (nx, ny) in [(100, 95), (55, 90), (105, 20)]:
        zone.set_tile(nx, ny, "npc", "interaction")
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = nx + dx, ny + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None

    # Portal to Widow's Lair (east)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 170 + dx, 100 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(170, 100, "portal", "interaction")

    # Entry from Western Tirisfal (north edge). This used to connect to
    # Ashenvale West instead, which was wrong geography entirely - Ashenvale
    # is Kalimdor, Silverpine is Lordaeron, they're on opposite continents
    # with no land bridge. Worse, the old link pointed back at the exact
    # same coordinates on both ends (100,4 -> 100,4), so walking through
    # looped you right back with zero actual movement. The real route into
    # Silverpine is north out of the Undead lands (Western Tirisfal), so
    # this same tile now serves that connection instead.
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = 100 + dx, 4 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(100, 4, "portal", "interaction")   # -> Western Tirisfal

    # Exit south to Silverpine South
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = 100 + dx, zone.height - 5 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(100, zone.height - 5, "portal", "interaction")  # -> Silverpine South

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "tile eastern kingdom too" -
    # real haunted_forest art now exists). Same overlap-matched region
    # pattern proven on Ashenvale/Tirisfal.
    # ------------------------------------------------------------------
    haunted = "assets/tiles/haunted_forest"
    region_terrain = [
        {"rect": (30, 60, 50, 60), "variants": [f"{haunted}/cemetery_grass_dark.png"]},          # Raven Hill Cemetery
        {"rect": (80, 80, 60, 50), "variants": [f"{haunted}/bog_mud.png", f"{haunted}/bog_mud_2.png"]},  # Shadowspring Pools
        {"rect": (70, 10, 70, 30), "variants": [f"{haunted}/burned_village_ground.png"]},        # Pyrewood Village
    ]
    default_variants = [f"{haunted}/haunted_forest_floor.png", f"{haunted}/haunted_forest_floor_2.png",
                         f"{haunted}/forest_floor_mossy_dark.png", f"{haunted}/forest_floor_mossy_dark_2.png"]

    def chunk_variants_for(cx, cy, cs):
        for region in region_terrain:
            rx, ry, rw, rh = region["rect"]
            overlaps = not (cx + cs <= rx or cx >= rx + rw or cy + cs <= ry or cy >= ry + rh)
            if overlaps:
                return region["variants"]
        return default_variants

    chunk_size = 20
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            # Skip chunks entirely over the Shadowspring Pools water -
            # already real base tiles from the shallow_water carve above.
            if all(zone.base_layer[cy + dy][cx + dx] == "shallow_water"
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Shadowspring Pools - real bog water texture over the carved marsh.
    # Was registered via add_ground_chunk, but the renderer only ever
    # consults water_chunks for a tile whose base_layer is actually
    # shallow_water/deep_water (Tilemap.add_water_chunk's own docstring
    # explains why the two lists are kept separate) - so this water never
    # got drawn at all and fell through to decayed_forest's per-tile
    # water fallback instead, which is the striped/noisy mess Kyle
    # reported. add_water_chunk is the fix; the per-tile fallback is also
    # fixed now (see tile_textures.py) as a second line of defense for
    # any water tile outside this chunk's rectangle.
    for gy in range(80, 130, chunk_size):
        for gx in range(80, 140, chunk_size):
            gw = min(chunk_size, 140 - gx)
            gh = min(chunk_size, 130 - gy)
            if gw > 0 and gh > 0:
                zone.add_water_chunk(f"{haunted}/murky_bog_water.png", gx, gy, gw, gh)

    # Props - crypt and reeds dressing around the cemetery/pools.
    zone.add_landmark(f"{haunted}/props/crypt_mausoleum.png", 45, 70, 5, 4)
    zone.add_landmark(f"{haunted}/props/bog_reeds_cluster.png", 90, 100, 3, 3)
    zone.add_landmark(f"{haunted}/props/bog_reeds_cluster.png", 120, 115, 3, 3)
    zone.add_landmark(f"{haunted}/props/burned_house_ruin.png", 90, 20, 6, 5)
    pine_i = 0
    for _ in range(12):
        x = random.randint(5, zone.width - 5)
        y = random.randint(5, zone.height - 5)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(f"{haunted}/props/dead_pine_cluster.png", x, y, 4, 5, solid=False)
            pine_i += 1

    return zone


def generate_silverpine_south():
    """Silverpine South (200x190) — Forsaken military, organized undeath."""
    zone = Tilemap("Silverpine South", 200, 190,
                   "Forsaken military stronghold, organized undead civilization.")
    zone.region = "Eastern Kingdoms - Lordaeron"

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.16:
                zone.set_tile(x, y, "grass", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Forest patches
    for _ in range(250):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        if random.random() < 0.40:
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "tree", "collision")

    # THE SEPULCHER — now a standalone zone, reached via portal. Per the
    # real Silverpine map (reference image), the Sepulcher sits west-center
    # near the coast, not south-center where it was placed before -
    # repositioned to match.
    sepulcher_cx, sepulcher_cy = 45, 90
    for dy in range(-8, 9):
        for dx in range(-10, 11):
            x, y = sepulcher_cx + dx, sepulcher_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(sepulcher_cx, sepulcher_cy, "portal", "interaction")  # -> The Sepulcher

    # AMBERMILL (east) — Mage tower, dungeon entrance
    ambermill_cx, ambermill_cy = 160, 80
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            x, y = ambermill_cx + dx, ambermill_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None

    # Tower building - was a solid FILLED 10x10 wall block stamped right on
    # top of the courtyard center, sealing the portal/NPC tile at (160,80)
    # inside solid stone with no door (same bug pattern as the Undercity/
    # Orgrimmar quarters earlier). Now a hollow ring with a doorway on the
    # south side, so the tower reads as a building you walk into rather
    # than a wall that happens to have collision cleared underneath it.
    for dy in range(10):
        for dx in range(10):
            x, y = ambermill_cx - 5 + dx, ambermill_cy - 5 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                on_ring = dx in (0, 9) or dy in (0, 9)
                is_door = dy == 9 and dx in (4, 5)
                if on_ring and not is_door:
                    zone.set_tile(x, y, "wall", "collision")

    zone.set_tile(160, 80, "npc", "interaction")

    # UNDERCITY PATH (north) — Military checkpoints
    zone.add_subzone("Undercity Path", 80, 10, 60, 40)

    # ROTTING MARSHES (west) — Swampland
    for y in range(80, 150):
        for x in range(20, 60):
            if random.random() < 0.35:
                zone.set_tile(x, y, "shallow_water", "base")
                zone.collision_layer[y][x] = None

    zone.add_subzone("Rotting Marshes", 20, 80, 40, 70)

    # NPCs - sp_south_hunter already existed in ambient_npcs.json with no
    # matching walkable tile (same orphaned-entry situation as Silverpine
    # North's sp_north_scout); adds the real tile for it plus 1 new
    # quest-line giver (sp_south_march_sergeant).
    for (nx, ny) in [(100, 95), (130, 40)]:
        zone.set_tile(nx, ny, "npc", "interaction")
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = nx + dx, ny + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None

    # EAST COAST — the boat to Fenris Isle needs actual water to sit next
    # to. It used to be planted in the middle of the landlocked Sepulcher
    # town square with no water anywhere near that side of the map, which
    # is why it read as "just a random dot" - mechanically it worked, but
    # nothing about the surroundings explained why a boat was there.
    for y in range(zone.height):
        for x in range(185, zone.width):
            zone.set_tile(x, y, "deep_water", "base")
            zone.collision_layer[y][x] = None

    # Dock clearing carved into the coastline, connected back to the
    # Sepulcher by a real path so it's reachable on foot. Uses "sand" as
    # the walkable dock surface - "wood" was tried first but isn't a
    # registered base tile at all in tiles.py, so it silently failed
    # is_walkable() and made the dock (and the boat standing on it)
    # unreachable.
    for dy in range(-6, 7):
        for dx in range(-8, 9):
            x, y = 182 + dx, 138 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "sand", "base")
                zone.collision_layer[y][x] = None
    ZoneGenerator._carve_path(zone, 118, 138, 178, 138, width=4, base="dirt")

    # Portal north to Silverpine North
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 100 + dx, 10 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(100, 10, "portal", "interaction")   # -> Silverpine North

    # Portal to Ambermill dungeon
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 160 + dx, 80 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(160, 80, "portal", "interaction")

    # Portal to Shadowfang Keep (south-center, near "The Forsaken Front"
    # per the real Silverpine map - independent of the Sepulcher's new
    # west-center position above)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 100 + dx, 155 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(100, 155, "portal", "interaction")  # -> Shadowfang Keep

    # Boat at the east coast dock -> Fenris Isle (relocated from the middle
    # of the Sepulcher, see coastline comment above)
    zone.set_tile(182, 138, "boat", "interaction")     # -> Fenris Isle

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real haunted_forest textures, same pattern as
    # Silverpine North above.
    # ------------------------------------------------------------------
    haunted = "assets/tiles/haunted_forest"
    region_terrain = [
        {"rect": (80, 10, 60, 40), "variants": [f"{haunted}/cemetery_grass_dark.png"]},       # Undercity Path
        {"rect": (20, 80, 40, 70), "variants": [f"{haunted}/bog_mud.png", f"{haunted}/bog_mud_2.png"]},  # Rotting Marshes
    ]
    default_variants = [f"{haunted}/haunted_forest_floor.png", f"{haunted}/haunted_forest_floor_2.png",
                         f"{haunted}/forest_floor_mossy_dark.png", f"{haunted}/forest_floor_mossy_dark_2.png"]

    def chunk_variants_for(cx, cy, cs):
        for region in region_terrain:
            rx, ry, rw, rh = region["rect"]
            overlaps = not (cx + cs <= rx or cx >= rx + rw or cy + cs <= ry or cy >= ry + rh)
            if overlaps:
                return region["variants"]
        return default_variants

    chunk_size = 20
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            # Skip chunks entirely over water (Rotting Marshes or the
            # east-coast sea) - already real base tiles from the carves
            # above.
            if all(zone.base_layer[cy + dy][cx + dx] in ("shallow_water", "deep_water", "sand")
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Rotting Marshes - real bog water over the carved swamp. Was
    # add_ground_chunk, which the renderer never checks for a water-base
    # tile (see Tilemap.add_water_chunk's docstring) - fell through to
    # decayed_forest's per-tile water fallback instead, same striped-mess
    # bug as Shadowspring Pools in Silverpine North.
    for gy in range(80, 150, chunk_size):
        for gx in range(20, 60, chunk_size):
            gw = min(chunk_size, 60 - gx)
            gh = min(chunk_size, 150 - gy)
            if gw > 0 and gh > 0:
                zone.add_water_chunk(f"{haunted}/murky_bog_water.png", gx, gy, gw, gh)

    # East-coast sea (the Fenris Isle boat crossing) - had NO chunk art at
    # all, ground or water, despite the base layer being filled solid
    # deep_water for 15 tiles wide by the full zone height. Every one of
    # those tiles was falling through to decayed_forest's per-tile water
    # fallback, which is the striped mess Kyle screenshotted "by the
    # docks." Real choppy open-sea art, distinct from the marsh's murky
    # bog water.
    sea = "assets/tiles/cursed_isle/dark_coastal_water.png"
    for gy in range(0, zone.height, chunk_size):
        gw = zone.width - 185
        gh = min(chunk_size, zone.height - gy)
        if gw > 0 and gh > 0:
            zone.add_water_chunk(sea, 185, gy, gw, gh)

    # Props - reeds in the marshes, a dead pine or two near Ambermill.
    zone.add_landmark(f"{haunted}/props/bog_reeds_cluster.png", 35, 110, 3, 3)
    zone.add_landmark(f"{haunted}/props/bog_reeds_cluster.png", 45, 130, 3, 3)
    zone.add_landmark(f"{haunted}/props/dead_pine_cluster.png", 140, 60, 4, 5, solid=False)

    return zone


def generate_fenris_isle():
    """Fenris Isle (160x140) — Isolated cursed island, worgen territory, FULL COMBAT."""
    zone = Tilemap("Fenris Isle", 160, 140,
                   "Isolated island cursed by ancient magic. Worgen territory. Dangerous.")
    zone.region = "Kalimdor - Isolated"

    # Base: cursed grassland
    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.20:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.08:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Cursed forest (dense, twisted)
    for _ in range(300):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        if random.random() < 0.50:
            for dy in range(-1, 2):
                for dx in range(-2, 3):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < zone.width and 0 <= y < zone.height:
                        zone.set_tile(x, y, "dead_tree", "collision")

    # BLOODMOON VILLAGE (south) — Worgen settlement, minimal threat
    for dy in range(-10, 11):
        for dx in range(-12, 13):
            x, y = 80 + dx, 120 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None

    zone.set_tile(80, 120, "npc", "interaction")

    # Second Bloodmoon Village NPC - this session's new Fenris Isle
    # quest-line giver (fenris_village_elder), alongside the existing
    # unnamed npc tile above (now also given a real ambient_npcs.json
    # entry, bloodmoon_elder, as part of this pass).
    zone.set_tile(85, 122, "npc", "interaction")

    # Boat dock back to Silverpine South (the Sepulcher) - Fenris Isle is
    # otherwise unreachable once here, since it's an isolated island.
    ZoneGenerator._carve_landing(zone, 80, 125, radius=2)
    zone.set_tile(80, 125, "boat", "interaction")   # -> Silverpine South

    # FENRIS PROPER (center-north) — Wild cursed forests, COMBAT HEAVY
    zone.add_subzone("Fenris Proper", 50, 40, 60, 60)

    # THE DROWNED DOCKS (east) — Shipwrecks
    for y in range(60, 110):
        for x in range(120, 155):
            if random.random() < 0.4:
                zone.set_tile(x, y, "shallow_water", "base")
                zone.collision_layer[y][x] = None

    zone.add_subzone("The Drowned Docks", 120, 60, 35, 50)

    # CUR'S GRAVE (west) — Burial site
    for y in range(40, 100):
        for x in range(10, 40):
            if random.random() < 0.3:
                zone.set_tile(x, y, "rock", "collision")

    zone.add_subzone("Cur's Grave", 10, 40, 30, 60)

    # Portal to Shadowpine Altar (west, ritual chamber)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 25 + dx, 60 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(25, 60, "portal", "interaction")

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "tile eastern kingdom too" -
    # real cursed_isle art now exists, zero chunked art calls existed
    # anywhere in this function before now). Same overlap-matched region
    # pattern proven on Ashenvale/Tirisfal/Silverpine.
    # ------------------------------------------------------------------
    cursed = "assets/tiles/cursed_isle"
    region_terrain = [
        {"rect": (80, 110, 25, 20), "variants": [f"{cursed}/graveyard_sand.png"]},                    # Bloodmoon Village
        {"rect": (50, 40, 60, 60), "variants": [f"{cursed}/rocky_cursed_ground.png", f"{cursed}/rocky_cursed_ground_2.png"]},  # Fenris Proper
        {"rect": (120, 60, 35, 50), "variants": [f"{cursed}/shipwreck_deck_planking.png"]},           # The Drowned Docks
        {"rect": (10, 40, 30, 60), "variants": [f"{cursed}/graveyard_sand.png"]},                      # Cur's Grave
    ]
    default_variants = [f"{cursed}/cursed_isle_grassland.png", f"{cursed}/cursed_isle_grassland_2.png"]

    def chunk_variants_for(cx, cy, cs):
        for region in region_terrain:
            rx, ry, rw, rh = region["rect"]
            overlaps = not (cx + cs <= rx or cx >= rx + rw or cy + cs <= ry or cy >= ry + rh)
            if overlaps:
                return region["variants"]
        return default_variants

    chunk_size = 20
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            # Skip chunks entirely over the Drowned Docks water - already
            # real base tiles from the shallow_water carve above.
            if all(zone.base_layer[cy + dy][cx + dx] == "shallow_water"
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Drowned Docks water - real shallow water texture over the carved
    # shipwreck shallows.
    for gy in range(60, 110, chunk_size):
        for gx in range(120, 155, chunk_size):
            gw = min(chunk_size, 155 - gx)
            gh = min(chunk_size, 110 - gy)
            if gw > 0 and gh > 0:
                zone.add_ground_chunk(f"{cursed}/drowned_dock_shallow_water.png", gx, gy, gw, gh)

    # Coastline - dark churning open water around the whole isolated
    # island, matching the "isolated cursed coastal island" brief. A
    # ragged inlet depth, mirroring Ashenvale West's own coastline
    # treatment, rather than a flat sea wall.
    def _coast_depth(i, total):
        return 10 + int(6 * abs((i % 23) - 11) / 11) + (i * 7) % 5

    for y in range(zone.height):
        depth = _coast_depth(y, zone.height)
        for x in range(0, min(depth, zone.width)):
            zone.collision_layer[y][x] = None
    for gy in range(0, zone.height, chunk_size):
        gh = min(chunk_size, zone.height - gy)
        zone.add_ground_chunk(f"{cursed}/dark_coastal_water.png", 0, gy, 18, gh)

    # Props - shipwreck and dead-tree dressing around the Docks and Cur's
    # Grave, tombstones in the burial ground, and a cursed hut near the
    # village.
    zone.add_landmark(f"{cursed}/props/shipwreck_hull.png", 130, 75, 8, 6)
    zone.add_landmark(f"{cursed}/props/worn_tombstone_row.png", 18, 55, 4, 3)
    zone.add_landmark(f"{cursed}/props/worn_tombstone_row.png", 22, 80, 4, 3)
    zone.add_landmark(f"{cursed}/props/cursed_village_hut.png", 65, 115, 5, 4)
    tree_i = 0
    for _ in range(14):
        x = random.randint(20, zone.width - 20)
        y = random.randint(10, zone.height - 10)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(f"{cursed}/props/cursed_dead_tree_cluster.png", x, y, 4, 5, solid=False)
            tree_i += 1

    return zone


# Dungeon generators (simplified, multi-chamber layouts)

def generate_blackfathom_deeps():
    """Blackfathom Deeps (240x220) - real WoW Classic layout: entry
    through a narrow, winding naga-filled cave from the coastal ruins
    down to the Pool of Ask'ar, the dungeon's first major junction - an
    island in the middle of the pool with Ghamoo-ra on it (turtles
    surrounding him are neutral). From the pool, real branches: swim
    northwest underwater to Lady Sarevess' room (mobs cleared first),
    or take the south exit through cross-tunnels to an open pool with
    murlocs and Gelihast. Lorgus Jett sits along a gauntlet of naga/
    murlocs; Old Serra'kis is an extra boss found by swimming under the
    entrance to Kelris's chamber. The path continues to the Drowned
    Sacellum (the main temple) - Twilight Lord Kelris in a summoning
    chamber best pulled one-by-one through its walled entrance - then 4
    braziers around his statue, lit one at a time, open the door to the
    final boss, Aku'mai.

    This had the right bosses already (6 of 8 real ones - only Lorgus
    Jett and Old Serra'kis were missing) but the wrong shape: a radial
    hub of ellipse blobs rather than the real Pool of Ask'ar junction
    with branching paths leading to a temple. Rebuilt around that real
    junction-and-branch structure, added the 2 missing bosses, and gave
    Kelris's chamber the real walled-entrance + brazier-puzzle read
    instead of just being another chamber on the hub.
    """
    zone = Tilemap("Blackfathom Deeps", 240, 220,
                   "Sunken night elf temple. Naga and twilight corruption "
                   "have claimed these ruins; the sea is reclaiming the rest.")
    zone.is_cave = True
    zone.region = "Ashenvale West"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "wall", "collision")

    def _room(cx, cy, w, h, wet_chance=0.0):
        for dy in range(-h // 2, h // 2 + 1):
            for dx in range(-w // 2, w // 2 + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
                    if wet_chance and random.random() < wet_chance:
                        zone.set_tile(x, y, "shallow_water", "base")
                    else:
                        zone.set_tile(x, y, "dirt", "base")

    def _water(x0, y0, x1, y1, width=5):
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="shallow_water")

    def _corridor(x0, y0, x1, y1, width=3):
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="dirt")

    # ===== ENTRANCE - narrow winding naga cave from the coastal ruins =====
    entrance = (120, 205)
    zone.set_tile(*entrance, "portal", "interaction")   # -> Ashenvale West
    _room(120, 195, 16, 10)
    _corridor(120, 205, 120, 195, width=3)
    _corridor(120, 195, 130, 175, width=3)

    # ===== POOL OF ASK'AR - the first major junction, an island in the
    # middle with Ghamoo-ra, surrounded by (neutral) turtles. =====
    _room(130, 155, 55, 40, wet_chance=0.4)
    _corridor(130, 175, 130, 155, width=4)
    ghamoora_pos = (130, 150)
    zone.set_tile(*ghamoora_pos, "boss_marker", "interaction")
    zone.add_subzone("Pool of Ask'ar", 103, 135, 55, 40)

    # ===== NW branch (underwater swim) - Lady Sarevess =====
    _water(130, 155, 65, 120, width=4)
    _room(50, 105, 28, 22)
    sarevess_pos = (45, 98)
    zone.set_tile(*sarevess_pos, "boss_marker", "interaction")
    zone.add_subzone("Sarevess's Grotto", 36, 94, 28, 22)

    # ===== South exit through cross-tunnels - open pool with murlocs,
    # Gelihast =====
    _corridor(130, 175, 130, 195, width=3)
    # Endpoint extended from (175,205) to (185,205) - the room below is
    # centered at (195,200) w=30,h=22, spanning x:180-210, so a corridor
    # ending at x=175 fell 5 tiles short of the room's west wall even
    # with width=3 padding. Caught by flood-fill reachability: Gelihast
    # and everything downstream of this branch were unreachable despite
    # every individual tile along the corridor's own centerline testing
    # walkable - the room and corridor just never actually touched.
    _corridor(130, 195, 185, 205, width=3)
    _room(195, 200, 30, 22, wet_chance=0.3)
    gelihast_pos = (200, 205)
    zone.set_tile(*gelihast_pos, "boss_marker", "interaction")
    zone.add_subzone("Gelihast's Pool", 180, 189, 30, 22)

    # ===== Lorgus Jett - along a gauntlet of naga/murlocs, between the
    # Pool of Ask'ar and the temple approach. Endpoint moved from
    # (155,110) to (165,105) - same "corridor stops short of the room"
    # bug as Gelihast above, fixed the same way: end the corridor
    # somewhere actually inside the destination room's bounds
    # (x:153-177, y:86-104), not just approximately near it. =====
    _corridor(130, 135, 165, 104, width=3)
    _room(165, 95, 24, 18)
    lorgus_pos = (168, 90)
    zone.set_tile(*lorgus_pos, "boss_marker", "interaction")
    zone.add_subzone("Twilight Gauntlet", 153, 86, 24, 18)

    # ===== Old Serra'kis - extra boss found by swimming UNDER the
    # entrance to Kelris's chamber, per every guide. Placed as a
    # submerged side-pocket just south of the temple approach. Endpoint
    # moved from (145,75) to (130,73) - same corridor-falls-short bug,
    # room bounds are x:120-140, y:57-73. =====
    _water(165, 95, 130, 73, width=3)
    _room(130, 65, 20, 16, wet_chance=0.6)
    serrakis_pos = (128, 62)
    zone.set_tile(*serrakis_pos, "boss_marker", "interaction")
    zone.add_subzone("The Sunken Grotto", 120, 57, 20, 16)

    # ===== DROWNED SACELLUM - the main temple, approached from the
    # gauntlet. Kelris's summoning chamber has a real walled entrance
    # (per wowpedia: "use the walled off entrance... pulling the mobs
    # one by one") rather than opening straight into the room. Both
    # corridor endpoints below moved to land genuinely inside their
    # destination rooms - same corridor-falls-short pattern as Gelihast/
    # Lorgus/Serrakis above, found by re-checking every remaining
    # corridor->room pair in this generator after catching the first
    # instance via flood-fill, rather than assuming the rest were fine. =====
    _corridor(165, 86, 120, 44, width=3)
    _room(120, 40, 18, 10)  # walled antechamber - the choke point
    _corridor(120, 40, 120, 22, width=3)
    _room(120, 12, 40, 24)
    kelris_pos = (120, 8)
    zone.set_tile(*kelris_pos, "boss_marker", "interaction")
    zone.add_subzone("Drowned Sacellum", 100, 0, 40, 24)

    # Four braziers ringing Kelris's statue - lit one at a time to open
    # the door behind him to Aku'mai, per every guide.
    brazier_positions = [(108, 4), (132, 4), (108, 16), (132, 16)]
    for bx, by in brazier_positions:
        zone.set_tile(bx, by, "quest_marker", "interaction")

    # ===== AKU'MAI - final boss, behind the door the braziers open,
    # deepest point of the temple. This engine has no lock/unlock-on-
    # event system, so the "opens after lighting all 4 braziers" gating
    # is spatial/implied (reached by its own corridor past the brazier
    # ring) rather than a literal closed door. Kelris's room already
    # sits near the top of the map (y~0-24), so Aku'mai's chamber is
    # placed to the room's WEST rather than further north, avoiding
    # negative/off-map coordinates - an earlier version of this had
    # akumai_cy=2 with rooms placed at cy-12 etc, landing at y=-10 and
    # similar, off the top of the 220-tall map entirely. Caught before
    # testing, not left in.
    _corridor(100, 12, 60, 12, width=3)
    _room(45, 12, 30, 20)
    akumai_pos = (40, 12)
    zone.set_tile(*akumai_pos, "boss_marker", "interaction")
    zone.add_subzone("Aku'mai's Chamber", 30, 2, 30, 20)

    # Naga statuary scattered as visual flavour throughout the flooded
    # areas - unchanged, this part was already correct.
    for y in range(zone.height):
        for x in range(zone.width):
            if zone.base_layer[y][x] in ("shallow_water",) and random.random() < 0.03:
                zone.set_tile(x, y, "small_rocks", "visual")

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)

    zone.boss_positions = [
        (ghamoora_pos[0], ghamoora_pos[1], "Ghamoo-ra"),
        (sarevess_pos[0], sarevess_pos[1], "Lady Sarevess"),
        (gelihast_pos[0], gelihast_pos[1], "Gelihast"),
        (lorgus_pos[0], lorgus_pos[1], "Lorgus Jett"),
        (serrakis_pos[0], serrakis_pos[1], "Old Serra'kis"),
        (kelris_pos[0], kelris_pos[1], "Twilight Lord Kelris"),
        (akumai_pos[0], akumai_pos[1], "Aku'mai"),
    ]
    zone.boss_position = akumai_pos  # legacy single-boss fallback - Aku'mai is BFD's true final boss
    zone.add_subzone("Blackfathom Deeps", 0, 0, zone.width, zone.height)
    return zone


def generate_groms_rest():
    """Grom's Rest (240x220) — FULL REBUILD this session (Kyle: "let's
    treat this like a proper dungeon... the shape is the same but you
    can't just jump to the last boss... 4 mandatory bosses and 2
    optional bosses"). Real reference map provided (a radial/cross
    layout, central hub with 6 themed chambers around it) - the VISUAL
    silhouette matches that reference, but the actual walkable path
    does NOT let you beeline hub-to-any-arm the way a pure radial hub
    would. Real structure:

    Entrance -> Hub (open central room, real demon totem centerpiece) ->
    from the hub, 2 OPTIONAL side chambers branch directly off with no
    gate (Satyr Warlord west, Void Handmaiden east - genuinely
    skippable detour content, matching the reference map's own
    "several rooms visible, not all required" read) -> a SEPARATE
    single corridor north out of the hub leads into a real gated
    sequence: Doomguard Sentinel's chamber -> Corrupted Ancient's
    chamber -> Felguard Overseer's chamber -> the Inner Sanctum (final
    boss, the eldritch horror). Each mandatory chamber's only exit
    forward is through the next one - there is no shortcut corridor
    connecting them to each other or back to the hub, so reaching the
    Inner Sanctum genuinely requires clearing the other 3 first.

    Real art from this session's Ashenvale corruption batch reused
    directly: scorched_floor/demon_wastes_wall for the fire-ritual
    Satyr chamber, void_floor/twilight_stone_wall for the Void
    Handmaiden's purple chamber, satyr_camp_floor for general
    corruption pockets, corrupted_root_wall as the default wall. 2 new
    pieces this session specifically for the 2 real gaps the existing
    set didn't cover: a fel-corrupted pool (Doomguard's chamber, matching
    the reference map's water pools) and a bone/skeleton hall (Felguard's
    chamber, matching the reference's bone-hall room).

    exit_pos MUST be exactly (120, 205) - portal_manager.py's real
    _links dict: Ashenvale East's (165,175) arrives here at (120,205),
    and this zone's own (120,205) links back to Ashenvale East
    (165,175). Checked directly, not assumed.
    """
    zone = Tilemap("Grom's Rest", 240, 220,
                   "Where the forest fell, the demons found a home. And "
                   "Grom's Rest became their throne.")
    zone.is_cave = True
    zone.region = "Ashenvale East"

    zone.fill("rock", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.collision_layer[y][x] = "rock"
            zone.set_tile(x, y, "rock", "collision")

    def _room(cx, cy, rw, rh, floor="dirt"):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                        zone.collision_layer[y][x] = None
                        zone.set_tile(x, y, floor, "base")

    def _corridor(x0, y0, x1, y1, width=4):
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="dirt")

    # ------------------------------------------------------------------
    # ENTRANCE + HUB
    # ------------------------------------------------------------------
    exit_pos = (120, 205)  # hard contract, see docstring
    entrance = exit_pos
    hub = (120, 155)

    _room(*entrance, 20, 14)
    _room(*hub, 34, 26, floor="stone")
    _corridor(*entrance, *hub, width=5)
    zone.set_tile(*exit_pos, "portal", "interaction")

    # ------------------------------------------------------------------
    # OPTIONAL ARM A - Satyr Warlord (west of the hub, genuinely
    # skippable - only connects to the hub, nowhere else).
    # ------------------------------------------------------------------
    satyr_room = (40, 145)
    _room(*satyr_room, 26, 20, floor="dirt")
    _corridor(hub[0] - 20, hub[1] - 4, *satyr_room, width=4)
    satyr_boss = (satyr_room[0], satyr_room[1] - 4)
    zone.set_tile(*satyr_boss, "boss_marker", "interaction")
    zone.add_subzone("Satyr's Ritual Hall", satyr_room[0] - 26, satyr_room[1] - 20, 52, 40)

    # ------------------------------------------------------------------
    # OPTIONAL ARM B - Void Handmaiden (east of the hub, same "hub-
    # only, genuinely skippable" rule).
    # ------------------------------------------------------------------
    void_room = (200, 145)
    _room(*void_room, 26, 20, floor="dirt")
    _corridor(hub[0] + 20, hub[1] - 4, *void_room, width=4)
    void_boss = (void_room[0], void_room[1] - 4)
    zone.set_tile(*void_boss, "boss_marker", "interaction")
    zone.add_subzone("Void Gathering", void_room[0] - 26, void_room[1] - 20, 52, 40)

    # ------------------------------------------------------------------
    # MANDATORY CHAIN - a single corridor leaves the hub's own north
    # edge (NOT the same corridor either optional arm uses) and runs
    # through 4 real chambers in strict sequence. No chamber in this
    # chain connects to anything except the one immediately before and
    # immediately after it - genuinely no way to skip ahead.
    # ------------------------------------------------------------------
    doomguard_room = (120, 105)
    ancient_room = (120, 65)
    felguard_room = (120, 30)
    sanctum_room = (120, 15)

    _room(*doomguard_room, 22, 15, floor="dirt")
    _corridor(hub[0], hub[1] - 22, *doomguard_room, width=5)
    doomguard_boss = (doomguard_room[0], doomguard_room[1] - 5)
    zone.set_tile(*doomguard_boss, "boss_marker", "interaction")
    zone.add_subzone("Doomguard's Approach", doomguard_room[0] - 22, doomguard_room[1] - 15, 44, 30)

    _room(*ancient_room, 18, 13, floor="dirt")
    _corridor(doomguard_room[0], doomguard_room[1] - 15, *ancient_room, width=4)
    ancient_boss = (ancient_room[0], ancient_room[1] - 4)
    zone.set_tile(*ancient_boss, "boss_marker", "interaction")
    zone.add_subzone("The Corrupted Grove", ancient_room[0] - 18, ancient_room[1] - 13, 36, 26)

    _room(*felguard_room, 18, 12, floor="dirt")
    _corridor(ancient_room[0], ancient_room[1] - 13, *felguard_room, width=4)
    felguard_boss = (felguard_room[0], felguard_room[1] - 4)
    zone.set_tile(*felguard_boss, "boss_marker", "interaction")
    zone.add_subzone("The Bone Hall", felguard_room[0] - 18, felguard_room[1] - 12, 36, 24)

    _room(*sanctum_room, 30, 14, floor="stone")
    _corridor(felguard_room[0], felguard_room[1] - 12, *sanctum_room, width=5)
    sanctum_boss = (sanctum_room[0], sanctum_room[1] - 6)
    zone.set_tile(*sanctum_boss, "boss_marker", "interaction")
    zone.add_subzone("Inner Sanctum", sanctum_room[0] - 30, sanctum_room[1] - 14, 60, 28)

    # ------------------------------------------------------------------
    # SCATTER - light rubble/decor throughout, matching the old
    # version's own "empty floor reads as empty" fix.
    # ------------------------------------------------------------------
    for _ in range(50):
        rx = random.randint(10, zone.width - 10)
        ry = random.randint(10, zone.height - 10)
        if zone.collision_layer[ry][rx] is None and random.random() < 0.4:
            zone.set_tile(rx, ry, "rock", "collision")

    ZoneGenerator._carve_landing(zone, *exit_pos, radius=3)

    # ------------------------------------------------------------------
    # CHUNKED FLOOR + WALL ART - real reused Ashenvale corruption tiles
    # plus 2 new pieces (fel pool, bone hall) from this session.
    # ------------------------------------------------------------------
    corruption = "assets/tiles/ashenvale_corruption"
    plain_floor = f"{corruption}/scorched_floor.png"
    plain_wall = f"{corruption}/corrupted_root_wall.png"
    satyr_floor = f"{corruption}/satyr_camp_floor.png"
    satyr_wall = f"{corruption}/demon_wastes_wall.png"
    void_floor_tex = f"{corruption}/void_floor.png"
    void_wall = f"{corruption}/twilight_stone_wall.png"
    fel_pool_floor = f"{corruption}/fel_pool_water.png"
    bone_floor = f"{corruption}/bone_hall_floor.png"
    bone_wall = f"{corruption}/bone_hall_wall.png"
    chunk_size = 20

    def floor_chunks(cx0, cy0, rw, rh, sprite):
        x0, y0 = cx0 - rw - 2, cy0 - rh - 2
        x1, y1 = cx0 + rw + 2, cy0 + rh + 2
        for gy in range(y0, y1, chunk_size):
            for gx in range(x0, x1, chunk_size):
                gw = min(chunk_size, x1 - gx)
                gh = min(chunk_size, y1 - gy)
                if gw > 0 and gh > 0:
                    zone.add_ground_chunk(sprite, gx, gy, gw, gh)

    floor_chunks(*entrance, 20, 14, plain_floor)
    floor_chunks(*hub, 34, 26, plain_floor)
    floor_chunks(*satyr_room, 26, 20, satyr_floor)
    floor_chunks(*void_room, 26, 20, void_floor_tex)
    floor_chunks(*doomguard_room, 22, 17, fel_pool_floor)
    floor_chunks(*ancient_room, 20, 16, plain_floor)
    floor_chunks(*felguard_room, 20, 16, bone_floor)
    floor_chunks(*sanctum_room, 30, 22, void_floor_tex)

    obstacle_chunk_size = 4
    for gy in range(0, zone.height, obstacle_chunk_size):
        for gx in range(0, zone.width, obstacle_chunk_size):
            gw = min(obstacle_chunk_size, zone.width - gx)
            gh = min(obstacle_chunk_size, zone.height - gy)
            dist_satyr = ((gx - satyr_room[0]) ** 2 + (gy - satyr_room[1]) ** 2) ** 0.5
            dist_void1 = ((gx - void_room[0]) ** 2 + (gy - void_room[1]) ** 2) ** 0.5
            dist_void2 = ((gx - sanctum_room[0]) ** 2 + (gy - sanctum_room[1]) ** 2) ** 0.5
            dist_bone = ((gx - felguard_room[0]) ** 2 + (gy - felguard_room[1]) ** 2) ** 0.5
            if dist_satyr < 24:
                sprite = satyr_wall
            elif dist_void1 < 24 or dist_void2 < 28:
                sprite = void_wall
            elif dist_bone < 20:
                sprite = bone_wall
            else:
                sprite = plain_wall
            zone.add_obstacle_chunk(sprite, gx, gy, gw, gh)

    zone.boss_positions = [
        (satyr_boss[0], satyr_boss[1], "Satyr Warlord"),
        (void_boss[0], void_boss[1], "Void Handmaiden"),
        (doomguard_boss[0], doomguard_boss[1], "Doomguard Sentinel"),
        (ancient_boss[0], ancient_boss[1], "Corrupted Ancient"),
        (felguard_boss[0], felguard_boss[1], "Felguard Overseer"),
        (sanctum_boss[0], sanctum_boss[1], "Inner Sanctum Horror"),
    ]
    zone.boss_position = sanctum_boss  # legacy single-boss fallback - the Inner Sanctum is the real final boss

    return zone


def generate_widows_lair():
    """Widow's Lair (140x120) — Mini-dungeon: spider den, dense webs, egg
    sacs. 3 named spider bosses culminating in the matriarch's chamber."""
    zone = Tilemap("Widow's Lair", 140, 120,
                   "Spider-infested cavern, egg chambers, webbed tunnels.")
    zone.is_cave = True
    zone.region = "Silverpine North"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "stone", "collision")

    def carve(cx, cy, rw, rh):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                        zone.collision_layer[y][x] = None
                        zone.set_tile(x, y, "dirt", "base")

    # Entrance web chamber
    carve(70, 100, 32, 16)
    entrance = (70, 108)

    # Egg chamber (west) - Boss 1: Broodmother Silka
    carve(35, 60, 26, 24)
    boss1 = (35, 55)
    zone.set_tile(*boss1, "boss_marker", "interaction")
    # Corridor to the entrance chamber. Was a thin 5-tile-tall strip that
    # only cleared the collision layer (never reset the base tile), and
    # against these big round 24-50 tile chambers it read on the map screen
    # as four disconnected floating rooms with barely a thread between them
    # ("disconnected orbs") even though it was mechanically walkable.
    # Widened and switched to _carve_path so it reads as an actual corridor.
    ZoneGenerator._carve_path(zone, 35, 78, 70, 100, width=6, base="dirt")

    # Silk tunnels (east) - Boss 2: Weaver Skitter
    carve(105, 60, 26, 24)
    boss2 = (105, 55)
    zone.set_tile(*boss2, "boss_marker", "interaction")
    ZoneGenerator._carve_path(zone, 105, 78, 70, 100, width=6, base="dirt")

    # Matriarch's chamber (deepest, north) - Boss 3
    carve(70, 20, 30, 20)
    boss3 = (70, 12)
    zone.set_tile(*boss3, "boss_marker", "interaction")
    ZoneGenerator._carve_path(zone, 70, 40, 70, 84, width=6, base="dirt")

    # Dense web scatter throughout - this cave's signature feature
    for y in range(zone.height):
        for x in range(zone.width):
            if zone.collision_layer[y][x] is None and random.random() < 0.10:
                zone.set_tile(x, y, "bushes", "visual")

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)
    zone.set_tile(*entrance, "portal", "interaction")

    zone.boss_positions = [boss1, boss2, boss3]
    zone.boss_position = boss1
    zone.add_subzone("Widow's Lair", 0, 0, zone.width, zone.height)
    return zone


def generate_shadowfang_keep():
    """Shadowfang Keep (170x160) — Mini-dungeon: Gothic worgen fortress.
    A real linear castle crawl: entrance hall -> Rethilgore -> courtyard
    -> east/west towers -> Arugal's sanctum at the top, 4 named bosses."""
    zone = Tilemap("Shadowfang Keep", 170, 160,
                   "Gothic castle, worgen-infested, Arugal's mad lair.")
    zone.is_cave = True
    zone.region = "Silverpine"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "stone", "collision")

    def carve(cx, cy, rw, rh):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                        zone.collision_layer[y][x] = None
                        zone.set_tile(x, y, "stone", "base")

    # Entrance hall
    carve(85, 145, 20, 12)
    entrance = (85, 152)

    # First boss chamber - Rethilgore
    carve(85, 110, 24, 18)
    boss1 = (85, 105)
    zone.set_tile(*boss1, "boss_marker", "interaction")
    for y in range(122, 127):
        for x in range(78, 93):
            zone.collision_layer[y][x] = None

    # Courtyard area (open square, not another circular chamber - a real
    # castle should have a real courtyard shape)
    for dy in range(-24, 25):
        for dx in range(-28, 29):
            x, y = 85 + dx, 65 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "dirt", "base")
    for y in range(87, 92):
        for x in range(75, 96):
            zone.collision_layer[y][x] = None

    # East tower - Fenrus the Devourer
    carve(135, 55, 22, 20)
    boss2 = (140, 50)
    zone.set_tile(*boss2, "boss_marker", "interaction")
    for x in range(110, 140):
        for y in range(53, 58):
            zone.collision_layer[y][x] = None

    # West tower - Odo the Blindwatcher
    carve(35, 55, 22, 20)
    boss3 = (30, 50)
    zone.set_tile(*boss3, "boss_marker", "interaction")
    for x in range(30, 60):
        for y in range(53, 58):
            zone.collision_layer[y][x] = None

    # Arugal's sanctum, at the top of the keep
    carve(85, 15, 26, 20)
    boss4 = (85, 8)
    zone.set_tile(*boss4, "boss_marker", "interaction")  # Arugal
    for y in range(15, 41):
        for x in range(83, 88):
            zone.collision_layer[y][x] = None

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)
    zone.set_tile(*entrance, "portal", "interaction")

    zone.boss_positions = [boss1, boss2, boss3, boss4]
    zone.boss_position = boss1
    zone.add_subzone("Shadowfang Keep", 0, 0, zone.width, zone.height)
    return zone


def generate_ambermill_tower():
    """Ambermill Tower (150x140) — Mini-dungeon: mage tower turned Kirin
    Tor/Forsaken battleground. Vertical library -> lab -> rooftop climb,
    3 bosses each guarding a floor."""
    zone = Tilemap("Ambermill Tower", 150, 140,
                   "Library and laboratory, magical experimentation, faction clash.")
    zone.is_cave = True
    zone.region = "Silverpine South"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "stone", "collision")

    def carve(cx, cy, rw, rh):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                        zone.collision_layer[y][x] = None
                        zone.set_tile(x, y, "stone", "base")

    # Entrance hall (library) - Boss 1: Rogue Apprentice
    carve(75, 120, 22, 16)
    boss1 = (75, 112)
    zone.set_tile(*boss1, "boss_marker", "interaction")
    entrance = (75, 128)

    # First floor (Magister Hawren area) - Boss 2
    carve(75, 75, 26, 22)
    boss2 = (75, 65)
    zone.set_tile(*boss2, "boss_marker", "interaction")
    for y in range(93, 98):
        for x in range(65, 86):
            zone.collision_layer[y][x] = None
            zone.set_tile(x, y, "stone", "base")

    # Second floor / rooftop (Apothecary Helbrim's experiments) - Boss 3
    carve(75, 30, 24, 20)
    boss3 = (75, 18)
    zone.set_tile(*boss3, "boss_marker", "interaction")
    for y in range(48, 53):
        for x in range(66, 85):
            zone.collision_layer[y][x] = None
            zone.set_tile(x, y, "stone", "base")

    # Bookshelf/lab-equipment scatter for flavour
    for y in range(zone.height):
        for x in range(zone.width):
            if zone.collision_layer[y][x] is None and random.random() < 0.05:
                zone.set_tile(x, y, "small_rocks", "visual")

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)
    zone.set_tile(*entrance, "portal", "interaction")

    zone.boss_positions = [boss1, boss2, boss3]
    zone.boss_position = boss1
    zone.add_subzone("Ambermill Tower", 0, 0, zone.width, zone.height)
    return zone


def generate_shadowpine_altar():
    """Shadowpine Altar (150x130) — Mini-dungeon: moonlit curse-ritual
    chamber on Fenris Isle. Bone altars ring the approach; 3 bosses guard
    the escalating ritual, ending at the altar itself."""
    zone = Tilemap("Shadowpine Altar", 150, 130,
                   "Ancient ritual chamber, moonlit, bone altars, curse energy.")
    zone.is_cave = True
    zone.region = "Fenris Isle"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "stone", "collision")

    def carve(cx, cy, rw, rh):
        for dy in range(-rh, rh + 1):
            for dx in range(-rw, rw + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if ((dx / max(rw, 1)) ** 2 + (dy / max(rh, 1)) ** 2) ** 0.5 <= 1.0:
                        zone.collision_layer[y][x] = None
                        zone.set_tile(x, y, "dirt", "base")

    # Approach, ringed with bone altars
    carve(75, 105, 30, 18)
    entrance = (75, 115)
    for (bx, by) in [(50, 100), (100, 100), (55, 115), (95, 115)]:
        zone.set_tile(bx, by, "small_rocks", "visual")

    # First ritual circle - Boss 1: Bonewarden
    carve(75, 65, 28, 22)
    boss1 = (75, 58)
    zone.set_tile(*boss1, "boss_marker", "interaction")
    for y in range(83, 88):
        for x in range(65, 86):
            zone.collision_layer[y][x] = None
            zone.set_tile(x, y, "dirt", "base")

    # Second ritual circle - Boss 2: Curse-Speaker
    carve(75, 30, 24, 18)
    boss2 = (75, 22)
    zone.set_tile(*boss2, "boss_marker", "interaction")
    for y in range(43, 48):
        for x in range(66, 85):
            zone.collision_layer[y][x] = None
            zone.set_tile(x, y, "dirt", "base")

    # Main altar chamber - Boss 3: the curse made flesh
    carve(75, 8, 26, 8)
    boss3 = (75, 5)
    zone.set_tile(*boss3, "boss_marker", "interaction")
    for y in range(8, 12):
        for x in range(66, 85):
            zone.collision_layer[y][x] = None
            zone.set_tile(x, y, "dirt", "base")

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)
    zone.set_tile(*entrance, "portal", "interaction")

    zone.boss_positions = [boss1, boss2, boss3]
    zone.boss_position = boss1
    zone.add_subzone("Shadowpine Altar", 0, 0, zone.width, zone.height)
    return zone


# ============================================================
# STANDALONE TOWNS
#
# These 5 were previously baked directly into a larger open-world zone
# (Astranaar/Zoram Strand into Ashenvale West, Splintertree Post into
# Ashenvale East, The Sepulcher into Silverpine South, Brill into Western
# Tirisfal). Every town in the game needs to be its own zone, so they've
# been pulled out into dedicated maps here, each with a single exit portal
# back to roughly where it used to sit in its parent zone. The parent
# zone generators have had the town's footprint removed and replaced with
# a portal tile leading here instead.
# ============================================================

def generate_astranaar():
    """Astranaar (110x90) — real night elf settlement, Alliance's forward
    base in Ashenvale. FULL REBUILD this session (Kyle: "make the
    towns... NPCs and quests eventually" - the old version was 4 flat
    "wall" collision boxes with no real building sprites at all and 3
    unnamed generic "npc" tiles, same primitive placeholder state every
    town was in before its own art pass this session).

    Real night elf buildings from this session's batch: a central hall
    (Sentinel Outpost Hall), a moon guard tower, 2 house sizes, a
    druid/priestess hut with its own moonwell-blue glow, and an open
    training pavilion. Widened from the old cramped 70x60 to 110x90 -
    the old footprint genuinely could not fit 6 real building sprites
    without the same overlap problem found and fixed in Orgrimmar
    earlier this session; this build checks real non-overlap directly
    rather than assuming generous spacing is enough.

    Real named NPC roles (no quest content yet, per Kyle's scope for
    this pass) matching Astranaar's actual Classic WoW roster: a druid
    trainer, a sentinel commander, an innkeeper, weapon and armor
    vendors, and a flight master - physically placed at the building
    that matches their role, not floating in the open clearing.
    """
    zone = Tilemap("Astranaar", 110, 90,
                   "Ancient night elf settlement, Alliance's forward base "
                   "in Ashenvale.")
    zone.region = "Kalimdor - Western Forest"
    zone.is_town = True

    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            if random.random() < 0.15:
                zone.set_tile(x, y, "dirt", "base")

    # Town clearing - real central open plaza around the hall.
    town_cx, town_cy = 55, 45
    for dy in range(-32, 33):
        for dx in range(-42, 43):
            x, y = town_cx + dx, town_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
                if random.random() < 0.15:
                    zone.set_tile(x, y, "grass", "base")

    # Buildings - real footprints, non-overlapping (checked directly
    # below, not assumed from generous-looking coordinates - same real
    # bug class Orgrimmar had 52 instances of earlier this session).
    buildings = [
        ("assets/buildings/sentinel_outpost_hall.png", 48, 35, 14, 12),   # central hall - Sentinel Eltharaen
        ("assets/buildings/moon_guard_tower.png", 30, 20, 7, 15),         # moon guard lookout
        ("assets/buildings/nightelf_house_small.png", 75, 22, 10, 13),    # innkeeper Rimble's inn
        ("assets/buildings/nightelf_house_medium.png", 20, 55, 12, 12),   # weapon/armor vendors
        ("assets/buildings/druid_priestess_hut.png", 80, 55, 9, 11),      # druid trainer Kerlonian
        ("assets/buildings/training_pavilion.png", 55, 68, 11, 10),       # sentinel training grounds
    ]

    def overlaps(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw <= bx or ax >= bx + bw or ay + ah <= by or ay >= by + bh)

    placed = []
    for sprite, bx, by, bw, bh in buildings:
        rect = (bx, by, bw, bh)
        for other in placed:
            if overlaps(rect, other):
                raise AssertionError(f"Astranaar building overlap: {sprite} at {rect} overlaps {other}")
        placed.append(rect)
        zone.add_landmark(sprite, bx, by, bw, bh)

    # Real named NPCs, placed just outside each building's own door
    # side (south edge, matching the sprites' own front-facing
    # orientation) rather than inside the solid footprint - same
    # "entrance, not buried" discipline as every building NPC fixed in
    # Orgrimmar earlier this session. Names/roles/greetings registered
    # in data/npcs/ambient_npcs.json (same real mechanism every other
    # town's named NPCs use - npc_id/name/zone/x/y/greeting - not a
    # made-up in-code attribute) under npc_id prefix "astranaar_".
    zone.set_tile(55, 48, "npc", "interaction")   # astranaar_sentinel_commander - hall
    zone.set_tile(33, 36, "npc", "interaction")   # astranaar_moon_guard - tower
    zone.set_tile(79, 36, "npc", "interaction")   # astranaar_innkeeper - inn
    zone.set_tile(25, 68, "npc", "interaction")   # astranaar_weapon_vendor - medium house
    zone.set_tile(26, 68, "npc", "interaction")   # astranaar_armor_vendor - medium house
    zone.set_tile(84, 67, "npc", "interaction")   # astranaar_druid_trainer - druid hut
    zone.set_tile(60, 79, "npc", "interaction")   # astranaar_sentinel_trainer - pavilion

    # Flight master - a real point of interest separate from the
    # building cluster, matching every other town's own flight point.
    zone.set_tile(town_cx, town_cy - 20, "npc", "interaction")  # astranaar_flight_master

    # Quest givers - this session's Ashenvale quest-line pass. Placed in
    # the open plaza clear of every building footprint and existing NPC
    # tile above (checked directly, same non-overlap discipline as the
    # building placement). Real content in data/npcs/ambient_npcs.json
    # and data/quests/ashenvale.json under npc_id prefix "astranaar_".
    zone.set_tile(45, 55, "npc", "interaction")   # astranaar_sentinel_liaison
    zone.set_tile(65, 55, "npc", "interaction")   # astranaar_grove_warden
    zone.set_tile(50, 30, "npc", "interaction")   # astranaar_refugee

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real Ashenvale forest floor across the whole
    # town, matching the zone it sits inside rather than the flat
    # default dirt/grass color this town had before.
    # ------------------------------------------------------------------
    ashenvale = "assets/tiles/ashenvale"
    chunk_size = 20
    variants = [f"{ashenvale}/forest_floor_light.png", f"{ashenvale}/forest_floor_roots.png"]
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            zone.add_ground_chunk(variants[variant_i % len(variants)], cx, cy, cw, ch)
            variant_i += 1

    # A few real canopy trees around the town's own edges, same props
    # as the surrounding Ashenvale West forest.
    tree_variants = [f"{ashenvale}/props/large_canopy_tree.png", f"{ashenvale}/props/medium_canopy_tree.png"]
    tree_i = 0
    for _ in range(14):
        x = random.randint(5, zone.width - 5)
        y = random.randint(5, zone.height - 5)
        # Only at the outer ring, clear of the town clearing/buildings.
        if abs(x - town_cx) > 38 or abs(y - town_cy) > 28:
            if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
                zone.add_landmark(tree_variants[tree_i % len(tree_variants)], x, y, 6, 6, solid=False)
                tree_i += 1

    # Exit back to Ashenvale West
    ZoneGenerator._carve_landing(zone, town_cx, zone.height - 5, radius=3)
    zone.set_tile(town_cx, zone.height - 5, "portal", "interaction")

    return zone


def generate_zoram_strand():
    """Zoram Strand (60x50) — coastal boating outpost, west edge of
    Ashenvale."""
    zone = Tilemap("Zoram Strand", 60, 50,
                   "A rocky coastline on Ashenvale's western edge, boats "
                   "bound for distant shores.")
    zone.region = "Kalimdor - Western Forest"
    zone.is_town = True

    zone.fill("sand", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            if random.random() < 0.2:
                zone.set_tile(x, y, "shallow_water", "base")

    # Open beach clearing
    for dy in range(-18, 19):
        for dx in range(-24, 25):
            x, y = 28 + dx, 25 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "sand", "base")
                zone.collision_layer[y][x] = None
                if random.random() < 0.2:
                    zone.set_tile(x, y, "shallow_water", "base")

    # Deep water to the west (the open sea)
    for y in range(zone.height):
        for x in range(0, 8):
            zone.set_tile(x, y, "deep_water", "base")
            zone.collision_layer[y][x] = None

    # Boating NPC
    zone.set_tile(15, 25, "npc", "interaction")

    # Exit back to Ashenvale West
    ZoneGenerator._carve_landing(zone, 50, 25, radius=3)
    zone.set_tile(50, 25, "portal", "interaction")

    return zone


def generate_splintertree_post():
    """Splintertree Post (90x70) — real Horde military outpost in southern
    Ashenvale, staging ground against the demon incursion. FULL REBUILD
    this session (Kyle: "make the towns... NPCs and quests eventually" -
    the old version was 3 flat "wall" collision boxes with no real
    building sprites and one unnamed generic "npc" tile).

    Mostly reuses existing generic Horde-outpost assets already on disk
    (outpost_barracks, watchtower, guard_post, watchers_perch,
    generic_tent_a/b) plus 2 new pieces from this session's batch
    (command_war_tent, supply_depot) - matching Kyle's explicit call to
    reuse where possible and only generate new pieces where needed,
    rather than a full from-scratch building set like Astranaar got.

    Real named NPC roles (no quest content yet, per Kyle's scope):
    a quartermaster, a flight master, and staging-camp guards/scouts
    tied to the real demon-incursion framing already in this zone's
    own subzone names (Satyr's Throne, Twilight Barrow, Demon Wastes).
    """
    zone = Tilemap("Splintertree Post", 90, 70,
                   "A Horde outpost carved out of Ashenvale's southern "
                   "reaches, staging ground against the demon incursion.")
    zone.region = "Kalimdor - Eastern Forest"
    zone.is_town = True

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            if random.random() < 0.15:
                zone.set_tile(x, y, "grass", "base")

    # Outpost clearing
    town_cx, town_cy = 45, 35
    for dy in range(-26, 27):
        for dx in range(-34, 35):
            x, y = town_cx + dx, town_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None

    # Buildings - real footprints, non-overlapping (checked directly,
    # same discipline as Astranaar above and every Orgrimmar district
    # fixed earlier this session). Mostly existing generic assets, 2 new
    # pieces (command_war_tent, supply_depot) from this session.
    buildings = [
        ("assets/buildings/command_war_tent.png", 35, 20, 13, 12),      # command tent - the outpost's own HQ
        ("assets/buildings/outpost_barracks.png", 15, 15, 15, 9),        # barracks
        ("assets/buildings/watchtower.png", 12, 45, 9, 12),               # watchtower
        ("assets/buildings/guard_post.png", 65, 15, 9, 9),                # east guard post
        ("assets/buildings/supply_depot.png", 60, 40, 12, 9),             # quartermaster's depot
        ("assets/buildings/watchers_perch.png", 30, 50, 9, 12),           # scout's perch
        ("assets/buildings/generic_tent_a.png", 55, 55, 9, 9),            # staging tent
        ("assets/buildings/generic_tent_b.png", 68, 55, 9, 9),            # staging tent
    ]

    def overlaps(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw <= bx or ax >= bx + bw or ay + ah <= by or ay >= by + bh)

    placed = []
    for sprite, bx, by, bw, bh in buildings:
        rect = (bx, by, bw, bh)
        for other in placed:
            if overlaps(rect, other):
                raise AssertionError(f"Splintertree Post building overlap: {sprite} at {rect} overlaps {other}")
        placed.append(rect)
        zone.add_landmark(sprite, bx, by, bw, bh)

    # Real named NPCs, placed just outside each building's own
    # footprint rather than inside it. Names/roles/greetings registered
    # in data/npcs/ambient_npcs.json under npc_id prefix "splintertree_".
    zone.set_tile(41, 34, "npc", "interaction")   # splintertree_commander - command tent
    zone.set_tile(22, 25, "npc", "interaction")   # splintertree_barracks_sergeant - barracks
    zone.set_tile(16, 58, "npc", "interaction")   # splintertree_watch_sentry - watchtower
    zone.set_tile(69, 25, "npc", "interaction")   # splintertree_guard - guard post
    zone.set_tile(66, 50, "npc", "interaction")   # splintertree_quartermaster - supply depot
    zone.set_tile(34, 63, "npc", "interaction")   # splintertree_scout - watcher's perch

    # Flight master, matching every other town's own flight point.
    zone.set_tile(55, 18, "npc", "interaction")  # splintertree_flight_master - moved off (town_cx, town_cy-15)=(45,20), which sat inside command_war_tent's own footprint (unreachable, caught via flood-fill)

    # Quest givers - this session's Ashenvale quest-line pass. Placed in
    # the open clearing clear of every building footprint and existing
    # NPC tile above. Real content in data/npcs/ambient_npcs.json and
    # data/quests/ashenvale.json under npc_id prefix "splintertree_".
    zone.set_tile(45, 45, "npc", "interaction")   # splintertree_war_mage
    zone.set_tile(25, 40, "npc", "interaction")   # splintertree_grunt
    zone.set_tile(55, 30, "npc", "interaction")   # splintertree_interrogator

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real Ashenvale forest floor across the town,
    # rather than the flat default dirt/grass color it had before.
    # ------------------------------------------------------------------
    ashenvale = "assets/tiles/ashenvale"
    chunk_size = 20
    variants = [f"{ashenvale}/forest_floor_dense.png", f"{ashenvale}/forest_floor_roots.png"]
    variant_i = 0
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            zone.add_ground_chunk(variants[variant_i % len(variants)], cx, cy, cw, ch)
            variant_i += 1

    # Exit back to Ashenvale East - MUST be exactly (30, 47), the hard
    # contract in portal_manager.py's real _links dict ("Splintertree
    # Post": {(30, 47): ("Ashenvale East", 110, 160)}). REAL BUG FIXED
    # this session (Kyle: "portal out of splintertree doesn't work") -
    # the generator previously carved its exit portal at
    # (town_cx, zone.height - 5) = (45, 65), a tile portal_manager never
    # checks, while (30, 47) - where the game actually listens for this
    # zone's exit - had no portal tile at all. Verified directly: before
    # this fix, scanning the whole generated zone for "portal" tiles on
    # the interaction layer found exactly one, at (45, 65); (30, 47) was
    # walkable open dirt with nothing on it.
    ZoneGenerator._carve_landing(zone, 30, 47, radius=3)
    zone.set_tile(30, 47, "portal", "interaction")

    return zone


def generate_the_sepulcher():
    """The Sepulcher (70x60) — Forsaken town, southern Silverpine."""
    zone = Tilemap("The Sepulcher", 70, 60,
                   "A Forsaken town built among crumbling tombs in "
                   "southern Silverpine.")
    zone.region = "Eastern Kingdoms - Lordaeron"
    zone.is_town = True

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            if random.random() < 0.12:
                zone.set_tile(x, y, "grass", "base")

    # Town clearing
    for dy in range(-20, 21):
        for dx in range(-27, 28):
            x, y = 35 + dx, 30 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None

    # Forsaken structures - real building sprites (Kyle, this session:
    # "start to tile open world" - replaces the 3 flat "wall" collision
    # boxes The Sepulcher has had until now). Its own flavor text ("a
    # Forsaken town built among crumbling tombs") makes the crypt chapel
    # the natural centerpiece here, not the town hall Brill/Deathknell
    # get - this is a town OF tombs, not a village that happens to have
    # a graveyard nearby.
    buildings = [
        ("assets/buildings/crypt_chapel.png", 16, 12, 8, 11),
        ("assets/buildings/forsaken_house_medium.png", 42, 12, 8, 10),
        ("assets/buildings/forsaken_house_small.png", 17, 37, 7, 9),
    ]

    def _overlaps(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw <= bx or ax >= bx + bw or ay + ah <= by or ay >= by + bh)

    _placed = []
    for sprite, bx, by, bw, bh in buildings:
        rect = (bx, by, bw, bh)
        for other in _placed:
            if _overlaps(rect, other):
                raise AssertionError(f"The Sepulcher building overlap: {sprite} at {rect} overlaps {other}")
        _placed.append(rect)
        zone.add_landmark(sprite, bx, by, bw, bh)

    # NPCs - moved clear of the real building footprints above (checked
    # directly, same discipline as Brill above).
    for (nx, ny) in [(35, 30), (40, 32)]:
        zone.set_tile(nx, ny, "npc", "interaction")

    # Exit back to Silverpine South
    ZoneGenerator._carve_landing(zone, 35, 55, radius=3)
    zone.set_tile(35, 55, "portal", "interaction")

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real haunted_forest packed ground, same
    # pattern as the other Silverpine-cluster zones above.
    # ------------------------------------------------------------------
    haunted = "assets/tiles/haunted_forest"
    chunk_size = 20
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            zone.add_ground_chunk(f"{haunted}/cemetery_grass_dark.png", cx, cy, cw, ch)
    zone.add_landmark(f"{haunted}/props/crypt_mausoleum.png", 50, 20, 5, 4)
    zone.add_landmark(f"{haunted}/props/bog_reeds_cluster.png", 15, 45, 3, 3)
    zone.add_landmark("assets/buildings/gallows_post.png", 55, 42, 4, 7)

    return zone


def generate_brill():
    """Brill (70x60) — the central Forsaken town of Tirisfal Glades."""
    zone = Tilemap("Brill", 70, 60,
                   "The heart of Forsaken lands, a town of the risen dead "
                   "going about undeath as if nothing changed.")
    zone.region = "Eastern Kingdoms - Lordaeron"
    zone.is_town = True

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            if random.random() < 0.12:
                zone.set_tile(x, y, "grass", "base")

    # Town clearing
    for dy in range(-22, 23):
        for dx in range(-27, 28):
            x, y = 35 + dx, 30 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None

    # Buildings - real Forsaken building sprites (Kyle, this session:
    # "start to tile open world" - replaces the 4 flat "wall"/"wood"
    # collision boxes Brill has had until now). Brill is Tirisfal's
    # capital, so it gets the town hall as its real centerpiece, same
    # role the sentinel_outpost_hall plays in Astranaar.
    buildings = [
        ("assets/buildings/forsaken_town_hall.png", 28, 12, 10, 11),
        ("assets/buildings/crypt_chapel.png", 45, 10, 8, 11),
        ("assets/buildings/forsaken_house_medium.png", 12, 36, 8, 10),
        ("assets/buildings/forsaken_house_small.png", 52, 36, 7, 9),
    ]

    def _overlaps(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw <= bx or ax >= bx + bw or ay + ah <= by or ay >= by + bh)

    _placed = []
    for sprite, bx, by, bw, bh in buildings:
        rect = (bx, by, bw, bh)
        for other in _placed:
            if _overlaps(rect, other):
                raise AssertionError(f"Brill building overlap: {sprite} at {rect} overlaps {other}")
        _placed.append(rect)
        zone.add_landmark(sprite, bx, by, bw, bh)

    # NPCs/Vendors - moved clear of the real building footprints above
    # (the old (35,30)/(38,32)/(32,28) trio sat where flat wall boxes
    # used to be; checked directly against the 4 rects above, not
    # assumed clear).
    for (nx, ny) in [(35, 30), (38, 32), (32, 24)]:
        zone.set_tile(nx, ny, "npc", "interaction")

    # Balnir Farmstead subzone, moved here from Western Tirisfal since it
    # was always meant to be Brill's own farmland on the town's outskirts.
    zone.add_subzone("Balnir Farmstead", 45, 40, 22, 18)

    # Exit back to Western Tirisfal
    ZoneGenerator._carve_landing(zone, 35, 55, radius=3)
    zone.set_tile(35, 55, "portal", "interaction")

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real undead_farmland ground, matching Western
    # Tirisfal's own theme (Brill shares its farmland palette, per the
    # original undead_farmland = Deathknell/Tirisfal/Brill assignment).
    # ------------------------------------------------------------------
    farmland = "assets/tiles/undead_farmland"
    chunk_size = 20
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            zone.add_ground_chunk(f"{farmland}/packed_graveyard_dirt.png", cx, cy, cw, ch)

    # Balnir Farmstead - dead crop field texture over its own subzone.
    for gy in range(40, 58, chunk_size):
        for gx in range(45, 67, chunk_size):
            gw = min(chunk_size, 67 - gx)
            gh = min(chunk_size, 58 - gy)
            if gw > 0 and gh > 0:
                zone.add_ground_chunk(f"{farmland}/dead_crop_field.png", gx, gy, gw, gh)

    zone.add_landmark(f"{farmland}/props/scarecrow.png", 50, 45, 2, 3, solid=False)
    zone.add_landmark(f"{farmland}/props/hay_bale_rotted.png", 58, 50, 3, 3)

    return zone
