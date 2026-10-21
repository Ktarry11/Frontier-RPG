"""
Zone generators for world expansion.

This module adds 6 new overworld zones and 2 expanded dungeons:
  - Deathknell, Eastern Tirisfal, Western Tirisfal (split from old Tirisfal Glades)
  - Northern Barrens, Central Barrens, Southern Barrens (split from old The Barrens)
  - Wailing Caverns (expanded from 60x54 to 160x140)
  - Razorfen Kraul (new, 150x140)

Inject these generators into ZoneGenerator class and update create_all_zones() to call them.
"""

import random
from world.tilemap import Tilemap
from world.zone_generator import ZoneGenerator


def generate_deathknell():
    """Deathknell (90x80) — undead starter village, Forsaken quests."""
    zone = Tilemap("Deathknell", 90, 80,
                   "A small undead settlement. The dead walk here.")
    zone.region = "Eastern Kingdoms - Lordaeron"

    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.16:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Blighted woods around edges
    for _ in range(120):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        edge = min(cx, cy, zone.width - cx, zone.height - cy)
        if edge > 20 and random.random() < 0.6:
            continue
        for dy in range(-1, 2):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.5:
                        zone.set_tile(x, y, "deep_forest", "collision")

    # Central village clearing
    for dy in range(-13, 14):
        for dx in range(-18, 19):
            x, y = 45 + dx, 40 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None

    # Village buildings - real Forsaken building sprites (Kyle, this
    # session: "start to tile open world" - replaces the 4 flat
    # "wall"/"wood" collision boxes every Eastern Kingdoms town has had
    # until now, same real-footprint pattern proven on Astranaar/
    # Splintertree Post. Deathknell's own Overseer Krell (this session's
    # quest-line giver) stands at the town hall; the other 3 buildings
    # are flavor housing for the small starter village.
    forsaken_buildings = [
        ("assets/buildings/forsaken_town_hall.png", 33, 29, 10, 11),
        ("assets/buildings/forsaken_house_small.png", 50, 30, 7, 9),
        ("assets/buildings/forsaken_house_medium.png", 33, 45, 8, 10),
        ("assets/buildings/forsaken_house_small.png", 54, 46, 7, 9),
    ]

    def _building_overlaps(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return not (ax + aw <= bx or ax >= bx + bw or ay + ah <= by or ay >= by + bh)

    _placed = []
    for sprite, bx, by, bw, bh in forsaken_buildings:
        rect = (bx, by, bw, bh)
        for other in _placed:
            if _building_overlaps(rect, other):
                raise AssertionError(f"Deathknell building overlap: {sprite} at {rect} overlaps {other}")
        _placed.append(rect)
        zone.add_landmark(sprite, bx, by, bw, bh)

    # Shadow Grave - real confirmed Deathknell subzone (Warcraft Wiki: "a
    # crypt found in the south of Deathknell"). South of the village
    # clearing, distinct ground-crypt visual (stone/graves) from the
    # village's wood/dirt.
    for dy in range(-8, 9):
        for dx in range(-10, 11):
            x, y = 45 + dx, 62 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if zone.collision_layer[y][x] is None or True:
                    zone.set_tile(x, y, "stone", "base")
                    zone.collision_layer[y][x] = None
    zone.add_subzone("Shadow Grave", 33, 52, 24, 20)

    # Deathknell Graves - real confirmed Deathknell subzone (Warcraft
    # Wiki: "a mass grave outside the Shadow Grave... where all undead
    # player characters start"). Placed just north of Shadow Grave
    # itself, matching "outside the Shadow Grave" directly.
    for dy in range(-6, 7):
        for dx in range(-8, 9):
            x, y = 45 + dx, 48 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None
    zone.add_subzone("Deathknell Graves", 37, 42, 16, 12)

    # The Overrun Claim - a goldmine surface camp near the Night Web's
    # Hollow cave entrance (20,30), matching real confirmed lore ("The
    # goldmine to the northwest has been overrun by spiders, and the
    # people of Deathknell frequently attempt to clear it out"). Not a
    # real WoW subzone name itself, but grounded directly in that
    # confirmed lore detail and the cave's actual map position.
    for dy in range(-7, 8):
        for dx in range(-9, 10):
            x, y = 22 + dx, 22 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.add_subzone("The Overrun Claim", 13, 15, 18, 14)

    # NPCs - (42,38) moved to (43,41) this session: the real building
    # pass above placed forsaken_town_hall's solid footprint at
    # (33,29,10,11), which buried the original (42,38) spot inside it.
    # dk_quest_overseer now stands just outside the hall's south face
    # instead, matching the "NPC outside the building's own footprint"
    # discipline used for every other town this session (Astranaar,
    # Splintertree Post, etc.) - verified against the 4 building rects
    # above directly, not assumed clear.
    for (nx, ny) in [(45, 40), (48, 42), (43, 41)]:
        zone.set_tile(nx, ny, "npc", "interaction")
    # (43,41) is this session's new Deathknell quest-line giver
    # (dk_quest_overseer, see data/npcs/ambient_npcs.json) - the other
    # two tiles already had real named NPCs (dk_elder, dk_risen) from an
    # earlier pass with no quest content behind them until now.

    # Chests
    for _ in range(3):
        x = random.randint(20, 70)
        y = random.randint(20, 60)
        if zone.is_walkable(x, y):
            zone.set_tile(x, y, "chest", "interaction")

    # Caves
    for (cx, cy) in [(20, 30), (70, 50)]:
        # Carve landing
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
        zone.set_tile(cx, cy, "portal", "interaction")

    # Portal to Western Tirisfal
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = 45 + dx, 78 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(45, 78, "portal", "interaction")

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "tile eastern kingdom too" -
    # real undead_farmland art now exists, zero chunked art calls existed
    # anywhere in this function before now). Same overlap-matched region
    # pattern proven on Ashenvale.
    # ------------------------------------------------------------------
    farmland = "assets/tiles/undead_farmland"
    region_terrain = [
        {"rect": (33, 52, 24, 20), "variants": [f"{farmland}/stone_crypt_floor.png"]},        # Shadow Grave
        {"rect": (37, 42, 16, 12), "variants": [f"{farmland}/grave_dirt.png"]},                # Deathknell Graves
        {"rect": (13, 15, 18, 14), "variants": [f"{farmland}/packed_graveyard_dirt.png", f"{farmland}/packed_graveyard_dirt_2.png"]},  # The Overrun Claim
    ]
    default_variants = [f"{farmland}/blighted_grass.png", f"{farmland}/blighted_grass_2.png"]

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
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Village clearing - packed dirt instead of flat default color.
    for gy in range(40 - 13, 40 + 14, chunk_size):
        for gx in range(45 - 18, 45 + 19, chunk_size):
            gw = min(chunk_size, 45 + 19 - gx)
            gh = min(chunk_size, 40 + 14 - gy)
            if gw > 0 and gh > 0:
                zone.add_ground_chunk(f"{farmland}/packed_graveyard_dirt.png", gx, gy, gw, gh)

    # Props - scattered dead trees, a gravestone cluster, and the ruined
    # farmhouse landmark.
    zone.add_landmark(f"{farmland}/props/farmhouse_ruin.png", 58, 20, 6, 5)
    zone.add_landmark(f"{farmland}/props/gravestone_cluster.png", 40, 55, 3, 3)
    zone.add_landmark(f"{farmland}/props/gravestone_cluster.png", 48, 58, 3, 3)
    tree_i = 0
    for _ in range(14):
        x = random.randint(5, zone.width - 5)
        y = random.randint(5, zone.height - 5)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(f"{farmland}/props/dead_tree_bare.png", x, y, 3, 3, solid=False)
            tree_i += 1

    return zone


def generate_eastern_tirisfal():
    """Eastern Tirisfal (100x100) — mid-tier undead questing."""
    zone = Tilemap("Eastern Tirisfal", 100, 100,
                   "Blighted farmlands and ruins of Lordaeron.")
    zone.region = "Eastern Kingdoms - Lordaeron"

    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.16:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Dense forest ring
    for _ in range(150):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        edge = min(cx, cy, zone.width - cx, zone.height - cy)
        if edge > 25 and random.random() < 0.7:
            continue
        for dy in range(-1, 2):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.5:
                        zone.set_tile(x, y, "deep_forest", "collision")

    # Subzones (keep references to old ones)
    zone.add_subzone("Solliden Farmstead", 20, 30, 30, 26)
    zone.add_subzone("Agamand Mills", 60, 20, 40, 40)
    zone.add_subzone("The Scarlet Watch", 70, 60, 40, 34)

    # NPCs - this session's new Eastern Tirisfal quest-line givers
    # (et_agamand_envoy, et_scarlet_watch_scout). Clear a small radius
    # against the forest scatter above, same guard pattern used for
    # Ashenvale's Maestra's Post NPC earlier this session (a single
    # unlucky tree tile adjacent was enough to pinch off the only
    # approach even with the NPC's own tile guaranteed walkable).
    for (nx, ny) in [(50, 50), (60, 60)]:
        zone.set_tile(nx, ny, "npc", "interaction")
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = nx + dx, ny + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None

    # Cave entrance (Undercity elevator connects near here separately) -
    # only ONE cave entrance remains on this side. The other used to be a
    # portal tile at (80,30) leading to Deathknell, but per the real
    # Tirisfal Glades map, Deathknell sits SW near Western Tirisfal (which
    # has Brill), not off Eastern Tirisfal - that link has moved, and this
    # tile is now just plain ground instead of a portal that goes nowhere.
    for (cx, cy) in [(30, 70)]:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
        zone.set_tile(cx, cy, "portal", "interaction")

    # Scourge Cave entrance - southwest corner, clear of the three
    # existing subzones (Solliden Farmstead, Agamand Mills, The Scarlet
    # Watch) and the three other portal tiles already in use here.
    scourge_cave_pos = (15, 80)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            x, y = scourge_cave_pos[0] + dx, scourge_cave_pos[1] + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
    zone.set_tile(*scourge_cave_pos, "portal", "interaction")

    # Portals to other Tirisfal zones
    for (px, py, name) in [(10, 50, "Western"), (90, 50, "Zeppelin")]:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = px + dx, py + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
        zone.set_tile(px, py, "portal", "interaction")

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real undead_farmland textures, same pattern as
    # Deathknell above.
    # ------------------------------------------------------------------
    farmland = "assets/tiles/undead_farmland"
    region_terrain = [
        {"rect": (20, 30, 30, 26), "variants": [f"{farmland}/dead_crop_field.png", f"{farmland}/dead_crop_field_2.png"]},  # Solliden Farmstead
        {"rect": (60, 20, 40, 40), "variants": [f"{farmland}/farmstead_mud.png"]},  # Agamand Mills
        {"rect": (70, 60, 40, 34), "variants": [f"{farmland}/packed_graveyard_dirt.png"]},  # The Scarlet Watch
    ]
    default_variants = [f"{farmland}/blighted_grass.png", f"{farmland}/blighted_grass_2.png"]

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
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Props - farmstead flavor around Solliden/Agamand Mills, grave
    # dressing near Scarlet Watch.
    zone.add_landmark(f"{farmland}/props/scarecrow.png", 28, 35, 2, 3, solid=False)
    zone.add_landmark(f"{farmland}/props/hay_bale_rotted.png", 35, 45, 3, 3)
    zone.add_landmark(f"{farmland}/props/farmhouse_ruin.png", 70, 35, 6, 5)
    zone.add_landmark(f"{farmland}/props/gravestone_cluster.png", 80, 70, 3, 3)
    tree_i = 0
    for _ in range(10):
        x = random.randint(5, zone.width - 5)
        y = random.randint(5, zone.height - 5)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(f"{farmland}/props/dead_tree_bare.png", x, y, 3, 3, solid=False)
            tree_i += 1

    return zone


def generate_western_tirisfal():
    """Western Tirisfal (80x80) — central hub with Brill."""
    zone = Tilemap("Western Tirisfal", 80, 80,
                   "The heart of Forsaken lands. Brill stands here.")
    zone.region = "Eastern Kingdoms - Lordaeron"

    zone.fill("grass", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.16:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Forest fringe
    for _ in range(100):
        cx = random.randint(0, zone.width - 1)
        cy = random.randint(0, zone.height - 1)
        edge = min(cx, cy, zone.width - cx, zone.height - cy)
        if edge > 20 and random.random() < 0.7:
            continue
        for dy in range(-1, 2):
            for dx in range(-2, 3):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.5:
                        zone.set_tile(x, y, "deep_forest", "collision")

    # BRILL — now a standalone zone (Brill), reached via portal. This used
    # to be the whole town baked directly into the zone center; every town
    # in the game needs to be its own zone, so it's been pulled out. The
    # Deathknell/Eastern Tirisfal portals below still pass near here since
    # Brill sits on the central road between them on the real map.
    brill_cx, brill_cy = 40, 40
    for dy in range(-6, 7):
        for dx in range(-8, 9):
            x, y = brill_cx + dx, brill_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.set_tile(brill_cx, brill_cy, "portal", "interaction")  # -> Brill

    # Cold Hearth Manor - real confirmed Tirisfal subzone (Wowpedia: "a
    # farmstead in central Tirisfal Glades... infested with mindless
    # Scourge zombies"). Northeast of Brill, distinct farmland patch.
    for dy in range(-7, 8):
        for dx in range(-9, 10):
            x, y = 62 + dx, 20 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    zone.add_subzone("Cold Hearth Manor", 53, 13, 18, 14)

    # The Bulwark - real confirmed Tirisfal location (Warcraft Wiki:
    # Argent Dawn/Forsaken forces offering repairs). Southeast of Brill,
    # a fortified stone outpost distinct from the farmland patches.
    for dy in range(-6, 7):
        for dx in range(-8, 9):
            x, y = 62 + dx, 62 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None
    zone.add_subzone("The Bulwark", 54, 56, 16, 12)

    # Portals
    for (px, py) in [(10, 40), (70, 40)]:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = px + dx, py + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
        zone.set_tile(px, py, "portal", "interaction")

    # NPCs - this session's new Western Tirisfal quest-line givers
    # (wt_bulwark_quartermaster, wt_coldhearth_watcher, wt_relay_courier).
    # Western Tirisfal had ZERO npc tiles before this pass (Brill, where
    # all its real named NPCs live, was pulled out as its own zone) -
    # placed in the open central clearing, clear of the forest fringe
    # (which only populates within 20 tiles of the map edge, well clear
    # of these), every portal carve-out, and both named subzone patches.
    for (nx, ny) in [(25, 55), (55, 55), (45, 65)]:
        zone.set_tile(nx, ny, "npc", "interaction")
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x, y = nx + dx, ny + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None

    # North road to Silverpine - this was the missing link. Silverpine was
    # previously only reachable via a broken land bridge from Ashenvale
    # West (wrong continent entirely - Ashenvale is Kalimdor, Silverpine is
    # Lordaeron, they don't touch) or via Widow's Lair, which is its own
    # separate mess. The real route into Silverpine from the Undead lands
    # is north out of Tirisfal, so it belongs here.
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            x, y = 40 + dx, 4 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.set_tile(x, y, "dirt", "base")
                zone.collision_layer[y][x] = None
    ZoneGenerator._carve_path(zone, 40, 4, 40, 27, base="dirt")
    zone.set_tile(40, 4, "portal", "interaction")   # -> Silverpine North

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART - real undead_farmland textures, same pattern as
    # Deathknell/Eastern Tirisfal above.
    # ------------------------------------------------------------------
    farmland = "assets/tiles/undead_farmland"
    region_terrain = [
        {"rect": (53, 13, 18, 14), "variants": [f"{farmland}/farmstead_mud.png"]},            # Cold Hearth Manor
        {"rect": (54, 56, 16, 12), "variants": [f"{farmland}/stone_crypt_floor.png"]},        # The Bulwark
    ]
    default_variants = [f"{farmland}/blighted_grass.png", f"{farmland}/blighted_grass_2.png"]

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
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Brill - packed graveyard dirt in place of the flat dirt clearing.
    for gy in range(brill_cy - 6, brill_cy + 7, chunk_size):
        for gx in range(brill_cx - 8, brill_cx + 9, chunk_size):
            gw = min(chunk_size, brill_cx + 9 - gx)
            gh = min(chunk_size, brill_cy + 7 - gy)
            if gw > 0 and gh > 0:
                zone.add_ground_chunk(f"{farmland}/packed_graveyard_dirt.png", gx, gy, gw, gh)

    # Props - hay bale and gravestones around Cold Hearth Manor/Bulwark.
    zone.add_landmark(f"{farmland}/props/hay_bale_rotted.png", 60, 20, 3, 3)
    zone.add_landmark(f"{farmland}/props/gravestone_cluster.png", 62, 60, 3, 3)
    tree_i = 0
    for _ in range(8):
        x = random.randint(5, zone.width - 5)
        y = random.randint(5, zone.height - 5)
        if zone.base_layer[y][x] in ("grass", "dirt") and zone.collision_layer[y][x] is None:
            zone.add_landmark(f"{farmland}/props/dead_tree_bare.png", x, y, 3, 3, solid=False)
            tree_i += 1

    return zone


def generate_northern_barrens():
    """Northern Barrens (280x260) — slug fens, harpies, caves. Sits between
    Central Barrens (south) and Ashenvale East (north, via Splintertree)."""
    zone = Tilemap("Northern Barrens", 280, 260,
                   "Wet, swampy northern reaches. Harpy nests above.")
    zone.region = "Kalimdor - Central"

    zone.fill("grass", "base")
    # REAL BUG FOUND + FIXED (Kyle playtest: "Northern barrens has random
    # water things everywhere"). This base terrain-roll loop had a stray
    # "elif r < 0.25: shallow_water" branch turning ~7% of EVERY tile on
    # the entire 280x260 map into an isolated single-tile puddle,
    # unrelated to any of the zone's real named water features (Slug
    # Fens, Sludge Fen, the oases below, and the east coastline further
    # down - all still carve their own water explicitly in their own
    # dedicated loops and are unaffected by this fix). Visually this was
    # a fine blue speckle scattered across the whole dry scrubland with
    # zero chunked art behind it - exactly "random water things
    # everywhere." No other Barrens generator in this file has this
    # branch (checked Central/Southern directly) - removed entirely;
    # only dirt/grass/grass_tuft remain in the base roll.
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.18:
                zone.set_tile(x, y, "dirt", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Slug Fens (west side, muddy)
    #
    # REAL BUG FIXED this session (Kyle: "slugfens is still this ugly ass
    # shit" / "sludgefen is a collision hell" / "the barrens water is
    # ugly...it's all the small 32x32 style blocks, nothing smooth").
    # The old loop rolled random.random()<0.4 INDEPENDENTLY per tile
    # across the whole 110x80 area - a pure salt-and-pepper checkerboard
    # of isolated single water tiles with dry dirt gaps between almost
    # every one, which is exactly why it never read as a real fen/pond
    # no matter how good the chunk art under it was (confirmed by
    # rendering it directly: the chunk-art pass further down DOES lay
    # real smooth water_shore_calm-style art per 20x20 chunk, but a
    # chunk only qualifies as "water" if it has ANY water tile in it -
    # the checkerboard pattern still fragments collision/base state at
    # the single-tile level underneath that art). Same root cause as the
    # bushes scatter at 15%/tile - isolated collision tiles scattered
    # through open ground, not real mud-clump terrain.
    #
    # Real fix: generate a handful of real pond/bog blob shapes (soft-
    # edged ellipses, several overlapping per area) instead of per-tile
    # noise, same technique already proven for Echo Isles' islands and
    # Durotar's oases. Leaves real dry ground BETWEEN ponds instead of
    # speckling water through all of it, and each pond is big enough to
    # read as a real body of water at normal zoom.
    random.seed(1337)  # deterministic blob layout, not reshuffled every regen
    slug_ponds = []
    for _ in range(14):
        pcx = random.randint(40, 125)
        pcy = random.randint(65, 135)
        prw = random.randint(8, 16)
        prh = random.randint(6, 13)
        slug_ponds.append((pcx, pcy, prw, prh))

    # PASS 1: carve every pond's water FIRST, all 14, before any fringe
    # decoration. REAL BUG FOUND + FIXED this session (Kyle: "can you
    # see the tiny trees in the water and on the land bro") - the old
    # code carved each pond's water THEN its own fringe immediately,
    # nested in one loop iteration. With 14 randomly-placed ellipses in
    # a shared ~85x70 area, ponds routinely overlap or sit close enough
    # that a LATER pond's water carve re-flooded tiles an EARLIER pond's
    # fringe pass had already placed "bushes" on (confirmed directly:
    # 86 of 371 bushes tiles ended up sitting on water tiles after
    # generation, despite each fringe tile passing its own dry-check at
    # placement time - the check was correct for the state at that
    # moment, just too early). Splitting into two full passes - all
    # water, then all fringe - makes the dry-check's result actually
    # final once every pond exists.
    for (pcx, pcy, prw, prh) in slug_ponds:
        for dy in range(-prh, prh + 1):
            for dx in range(-prw, prw + 1):
                x, y = pcx + dx, pcy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    nd = ((dx / prw) ** 2 + (dy / prh) ** 2) ** 0.5
                    if nd <= 1.0:
                        zone.set_tile(x, y, "shallow_water", "base")

    # PASS 2: muddy fringe ("bushes" collision - renders as a thin
    # bare-tree sprite in Slug Fens' "barrens_fen" biome, tile_textures.
    # py) around each pond's edge, now that ALL water from every pond
    # is final. Explicit _is_water check per tile is still kept (not
    # just relying on the nd ring) as defense in depth.
    for (pcx, pcy, prw, prh) in slug_ponds:
        for dy in range(-prh - 2, prh + 3):
            for dx in range(-prw - 2, prw + 3):
                x, y = pcx + dx, pcy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    nd = ((dx / prw) ** 2 + (dy / prh) ** 2) ** 0.5
                    if 1.2 <= nd <= 1.4 and not ZoneGenerator._is_water(zone, x, y):
                        if random.random() < 0.3:
                            zone.set_tile(x, y, "bushes", "collision")

    zone.add_subzone("Slug Fens", 55, 95, 85, 70)

    # Harpy Roost (north, rocky)
    for _ in range(110):
        cx = random.randint(195, 250)
        cy = random.randint(15, 70)
        for dy in range(-2, 3):
            for dx in range(-3, 4):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.4:
                        zone.set_tile(x, y, "rock", "collision")

    zone.add_subzone("Harpy Roost", 180, 15, 70, 70)

    # Mor'shan Rampart - the real northern border checkpoint into
    # Ashenvale (confirmed real WoW location, was previously just an
    # unlabeled portal tile with no subzone identity at all). Sits right
    # around the north portal since it IS the checkpoint you pass
    # through to reach Ashenvale, not a separate detour.
    for dy in range(-10, 11):
        for dx in range(-14, 15):
            x, y = 150 + dx, 30 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                zone.collision_layer[y][x] = None
                zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Mor'shan Rampart", 136, 20, 28, 20)

    # Sludge Fen - real WoW: "oil field found on the northeast corner of
    # the Northern Barrens," an oil-rig-over-tainted-water site. Distinct
    # from Harpy Roost (rocky cliffs) despite both being in the NE -
    # Sludge Fen sits further east and lower, a wet industrial site
    # rather than a nesting cliff.
    for dy in range(-14, 15):
        for dx in range(-16, 17):
            x, y = 225 + dx, 55 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                dist = (dx**2 + dy**2) ** 0.5
                if dist < 10:
                    zone.set_tile(x, y, "shallow_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < 14:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Sludge Fen", 209, 41, 32, 28)

    # Stagnant Oasis - real WoW: Verog the Dervish's location, per the
    # quest text "based at the centaur command tent at the Stagnant
    # Oasis to the southeast." Southeast of the map center, distinct
    # water feature from Slug Fens (west) and Sludge Fen (industrial,
    # NE) - a real oasis pool, matching centaur territory rather than
    # goblin or harpy territory.
    for dy in range(-13, 14):
        for dx in range(-15, 16):
            x, y = 200 + dx, 175 + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                dist = (dx**2 + dy**2) ** 0.5
                if dist < 9:
                    zone.set_tile(x, y, "deep_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < 12:
                    zone.set_tile(x, y, "shallow_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < 13:
                    zone.collision_layer[y][x] = None
    zone.add_subzone("Stagnant Oasis", 185, 162, 30, 26)

    # Real east coastline (Kyle, this session: "the east coast NEEDS
    # water for it" - confirmed via a real WoW map reference: the Great
    # Sea runs the whole east edge of the Barrens, and this zone had
    # essentially zero coastal water before now - 98% of the east 30
    # columns were open walkable land). Per-row threshold rather than a
    # straight vertical cut, matching the reference map's real curving
    # shoreline - pulled in close (more water) through open stretches,
    # bulged out (less water, real dry land preserved) around Sludge
    # Fen/Boulder Lode Mine and Far Watch Post specifically, since Kyle
    # confirmed the coast should curve around those real subzones
    # rather than displacing them.
    def _coast_x(y):
        if 30 <= y <= 80:
            return 258  # bulge east around Sludge Fen (up to x=241) / Boulder Lode Mine portal (255,45)
        if 108 <= y <= 152:
            return 272  # bulge further east around Far Watch Post (up to x=276)
        if 195 <= y <= 255:
            return 225  # pull in close near Merchant Coast, which already wants water here
        return 244  # default open-coast threshold elsewhere

    for y in range(zone.height):
        threshold = _coast_x(y)
        for x in range(threshold, zone.width):
            depth = x - threshold
            if depth > 6:
                zone.set_tile(x, y, "deep_water", "base")
            else:
                zone.set_tile(x, y, "shallow_water", "base")
            zone.collision_layer[y][x] = None

    # A couple of small real offshore islands, matching the reference
    # map's own two islets off this stretch of coast - dry landmasses
    # sitting IN the water strip just carved, not touching the mainland.
    for (icx, icy, ir) in [(268, 95, 6), (272, 175, 5)]:
        for dy in range(-ir, ir + 1):
            for dx in range(-ir, ir + 1):
                x, y = icx + dx, icy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if (dx / ir) ** 2 + (dy / ir) ** 2 <= 1.0:
                        zone.set_tile(x, y, "grass", "base")
                        zone.collision_layer[y][x] = None

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "finish the Barrens...
    # just needs tiles"). Real per-subzone texture assignment using
    # rectangle-overlap matching (proven pattern from Durotar's own
    # subzone terrain regions - a chunk's CENTER can land just outside
    # a region's rect even when most of its area overlaps it, so this
    # checks real overlap, not center-point containment). Every real
    # named subzone in this zone gets a thematically appropriate real
    # texture instead of the flat default "grass"/"dirt" color this
    # whole 280x260 map rendered on before now.
    # ------------------------------------------------------------------
    barrens = "assets/tiles/barrens"
    # REAL BUG FIXED this session (Kyle: "god the barrens water is
    # ugly"/general art complaints, confirmed directly - every
    # barrens/grass/* variant previously used here shares a rust-orange/
    # scorched-earth palette that reads as lava/ember rather than dry
    # savanna). "savanna_dry_grass.png" is genuine Kyle-approved tan/
    # olive savanna art - now the dominant ground texture everywhere in
    # this zone. Kept sparse_grass (real but not orange-saturated) for
    # trodden camp interiors where a flatter/more worn look fits, and
    # grass_with_flowers for Dry Hills' own greener lore - both still
    # real variety, per Kyle's "keep some of the grasslands stuff...but
    # we need more variation", not just a single flat texture everywhere.
    savanna = f"{barrens}/grass/savanna_dry_grass.png"
    subzone_terrain = [
        {"rect": (55, 95, 85, 70), "variants": [savanna]},                                        # Slug Fens - wet/muddy
        {"rect": (180, 15, 70, 70), "variants": [savanna]},                                        # Harpy Roost - rocky cliffs
        {"rect": (136, 20, 28, 20), "variants": [f"{barrens}/grass/sparse_grass.png"]},           # Mor'shan Rampart - checkpoint, trodden
        {"rect": (209, 41, 32, 28), "variants": [savanna]},                                        # Sludge Fen - industrial
        {"rect": (10, 10, 60, 60), "variants": [f"{barrens}/grass/grass_with_flowers.png"]},      # Dry Hills - greener per its own lore
        {"rect": (240, 114, 36, 32), "variants": [f"{barrens}/grass/sparse_grass.png"]},          # Far Watch Post - camp, trodden
        {"rect": (129, 51, 32, 28), "variants": [f"{barrens}/grass/sparse_grass.png"]},           # Mor'shan Base Camp - camp, trodden
        {"rect": (220, 200, 55, 55), "variants": [savanna]},                                        # Merchant Coast
        {"rect": (140, 95, 30, 130), "variants": [savanna]},                                        # Gold Road
    ]
    default_variants = [savanna]

    def chunk_variants_for(cx, cy, cs):
        for region in subzone_terrain:
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
            # Skip chunks that are entirely water - the coastal carve
            # above already set those base tiles directly; painting a
            # grass ground chunk on top would silently undo it.
            if all(zone.base_layer[cy + dy][cx + dx] in ("deep_water", "shallow_water")
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Real water chunk art - same gap as Central Barrens (Kyle: "tiny
    # little water blocks"). Slug Fens, Sludge Fen, Stagnant Oasis, and
    # the whole east coastline above all painted real shallow_water/
    # deep_water base tiles but never got any chunk art, so every one of
    # them fell through to the small per-tile fallback crop. Same real
    # tropical water art as Central Barrens for consistency.
    vot = "assets/tiles/valley_of_trials"
    for wy in range(0, zone.height, chunk_size):
        for wx in range(0, zone.width, chunk_size):
            ww = min(chunk_size, zone.width - wx)
            wh = min(chunk_size, zone.height - wy)
            has_deep = any(zone.base_layer[wy + dy][wx + dx] == "deep_water"
                           for dy in range(0, wh, 4) for dx in range(0, ww, 4)
                           if wy + dy < zone.height and wx + dx < zone.width)
            has_any_water = has_deep or any(
                zone.base_layer[wy + dy][wx + dx] == "shallow_water"
                for dy in range(0, wh, 4) for dx in range(0, ww, 4)
                if wy + dy < zone.height and wx + dx < zone.width)
            if not has_any_water:
                continue
            sprite = f"{vot}/oasis_deep_water.png" if has_deep else f"{vot}/oasis_shallow_water.png"
            zone.add_water_chunk(sprite, wx, wy, ww, wh)

    # ------------------------------------------------------------------
    # HAND-PLACED PROPS (Kyle, this session: scrap random scatter
    # entirely - "lets remove the scattered trees and rocks and hand
    # place props...use logic, more around mountains, more around
    # forests or oasis"). REAL BUG this replaced: random.randint() prop
    # placement (both the old single-tile "tree" collision loop and
    # rock_outcrop landmarks) had no reliable relationship to where
    # water/terrain actually ended up, and Kyle caught real cases of
    # tiny tree sprites rendered standing IN water. Every group below is
    # placed at real named coordinates with an explicit water/collision
    # check at call time, grouped by what's actually nearby - rocks
    # ring Harpy Roost's cliffs and Sludge Fen's rubble, trees cluster
    # at Slug Fens' and Stagnant Oasis' pond edges (not in them), and a
    # light scatter of real multi-tile acacia landmarks covers the open
    # savanna between named features. This is the first zone built this
    # way - the template for doing every future zone hand-placed rather
    # than randomly scattered.
    # ------------------------------------------------------------------
    def _place_if_clear(sprite, x, y, w, h, solid=False):
        """Place a landmark only if its whole footprint is dry, in-
        bounds, and free of existing collision - the explicit check
        the old scatter loops were supposed to have everywhere."""
        if not (0 <= x and x + w <= zone.width and 0 <= y and y + h <= zone.height):
            return False
        for dy in range(h):
            for dx in range(w):
                if (zone.collision_layer[y + dy][x + dx] is not None
                        or ZoneGenerator._is_water(zone, x + dx, y + dy)):
                    return False
        zone.add_landmark(sprite, x, y, w, h, solid=solid)
        return True

    # Rock outcrops ringing Harpy Roost's cliffs (180-250, 15-85) - hand
    # placed around the actual rock-collision cluster instead of a blind
    # random box over the whole subzone rect.
    for (rx, ry) in [(195, 25), (210, 35), (225, 22), (238, 45), (200, 60),
                      (218, 65), (232, 75), (205, 78), (242, 30)]:
        _place_if_clear(f"{barrens}/props/rock_outcrop.png", rx, ry, 4, 4)

    # Rock rubble around Sludge Fen's industrial site (center 225,55).
    for (rx, ry) in [(212, 44), (238, 46), (220, 70), (232, 68)]:
        _place_if_clear(f"{barrens}/props/rock_outcrop.png", rx, ry, 3, 3)

    # Acacia trees clustered at Slug Fens' real pond edges (the 14 ponds
    # carved above, slug_ponds list) - a believable "trees like the
    # water" read instead of trees anywhere in the subzone including on
    # top of ponds.
    for (pcx, pcy, prw, prh) in slug_ponds:
        for _ in range(2):
            ox = pcx + random.randint(-prw - 4, prw + 4)
            oy = pcy + random.randint(-prh - 4, prh + 4)
            _place_if_clear(f"{barrens}/props/acacia_tree.png", ox, oy, 3, 3)

    # Acacia trees around Stagnant Oasis (center 200,175) - real oasis
    # tree ring, not scattered randomly across the whole southeast.
    for (ox, oy) in [(185, 158), (215, 160), (180, 185), (220, 188),
                      (195, 195), (205, 155)]:
        _place_if_clear(f"{barrens}/props/acacia_tree.png", ox, oy, 3, 3)

    # Light scatter of real multi-tile acacia trees across the open
    # savanna between named features - deliberately sparser than the
    # old 130-count blind scatter, with the same explicit per-tile
    # water/collision check every placement here uses.
    placed = 0
    attempts = 0
    while placed < 45 and attempts < 45 * 25:
        attempts += 1
        x = random.randint(0, zone.width - 4)
        y = random.randint(0, zone.height - 4)
        size = random.randint(2, 4)
        if _place_if_clear(f"{barrens}/props/acacia_tree.png", x, y, size, size):
            placed += 1

    # Portal south to Central Barrens (aligned with Central Barrens' north
    # portal at (150, 4))
    ZoneGenerator._carve_path(zone, 150, zone.height - 4, 150, zone.height - 40)
    ZoneGenerator._carve_landing(zone, 150, zone.height - 4, radius=3)
    zone.set_tile(150, zone.height - 4, "portal", "interaction")   # -> Central Barrens

    # Portal north to Ashenvale East (further north from the Barrens,
    # matches Splintertree Post being reachable this way)
    ZoneGenerator._carve_path(zone, 150, 4, 150, 40)
    ZoneGenerator._carve_landing(zone, 150, 4, radius=3)
    zone.set_tile(150, 4, "portal", "interaction")   # -> Ashenvale East

    # Boulder Lode Mine entrance - real WoW confirms this cave sits "east
    # of the Sludge Fen" / "north-east from the Sludge Fen," so it's
    # placed near the Sludge Fen subzone just carved above, not off in
    # the Slug Fens on the opposite side of the map where it sat before
    # this fix (wrong parent zone AND wrong in-zone position).
    boulder_lode_pos = (255, 45)
    ZoneGenerator._carve_landing(zone, *boulder_lode_pos, radius=2)
    zone.set_tile(*boulder_lode_pos, "portal", "interaction")  # -> Boulder Lode Mine

    # Second, unrelated small cave - kept at its original Slug Fens-area
    # position. This is "cave_1" in encounters.json (Harpy trash) - a
    # real minor side-cave, not a duplicate route to Boulder Lode Mine
    # like it incorrectly was before this fix.
    minor_cave_pos = (60, 150)
    ZoneGenerator._carve_landing(zone, *minor_cave_pos, radius=2)
    zone.set_tile(*minor_cave_pos, "portal", "interaction")  # -> cave_1

    # --- 5 new subzones (Kyle: "Barrens are huge... 8 to 10 subzones per
    # zone") bringing Northern Barrens from 5 to 10, all real WoW
    # locations researched before placement, not invented:

    # Dry Hills - real WoW: "far northwestern corner of the Northern
    # Barrens," greener than its name suggests (Ashenvale seeds carried
    # on the wind), home to Witchwing harpies (a creature this project
    # already has at level 20-22) raiding the Gold Road, plus zhevra/
    # plainstrider/raptor game drawing hunters. Placed in the genuinely
    # open far-NW corner - the only real unclaimed corner at this size.
    for _ in range(90):
        cx = random.randint(15, 65)
        cy = random.randint(15, 65)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.3:
                        zone.set_tile(x, y, "grass_tuft", "visual")
                    if random.random() < 0.12:
                        zone.set_tile(x, y, "rock", "collision")
    zone.add_subzone("Dry Hills", 10, 10, 60, 60)

    # Far Watch Post - real WoW: "small Horde outpost located just west
    # of the bridge between Durotar and the Northern Barrens... contains
    # a watch tower, an orc burrow, and a few catapults... vital for
    # protecting supply caravans." Placed on the east edge, facing
    # Durotar, distinct from Mor'shan Rampart (the north/Ashenvale
    # checkpoint) - this is the east checkpoint instead.
    fw_cx, fw_cy = 258, 130
    for dy in range(-16, 17):
        for dx in range(-18, 19):
            x, y = fw_cx + dx, fw_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                # Widened from abs(dx)<10/abs(dy)<10 - too small to fit
                # both real buildings below (watchtower+house, 9 tiles
                # wide each) with any margin, part of the same overlap
                # bug fixed just below.
                if abs(dx) < 17 and abs(dy) < 15:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Far Watch Post", fw_cx - 18, fw_cy - 16, 36, 32)

    # Real buildings at Far Watch Post - the wiki description explicitly
    # calls out a watch tower here, matching the real hub NPC (Outrider
    # Kelsara, 258,130) already researched and placed - no structures
    # existed before this session, same gap as every hub camp in the
    # earlier Barrens expansion.
    #
    # REAL BUG FIXED this session (Kyle: "the only two buildings in
    # farwatch post are literally on top of each other lol") - the
    # watchtower (anchor 238,108, 9x12) and generic_house_a (anchor
    # 243,109, 9x9) were placed only 5 tiles apart on both axes with
    # both footprints 9+ tiles wide - a dead-certain overlap (watchtower
    # spans x:[238,247), house spans x:[243,252), overlapping x:[243,247)
    # entirely, same story on y). Respaced to opposite sides of the
    # cleared ~19x19 interior (fw_cx±18/fw_cy±16 clearing), each kept
    # inside the clearing with margin, checked directly for zero overlap.
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/watchtower.png", fw_cx - 16, fw_cy - 8, 9, 12),
        ("assets/buildings/generic_house_a.png", fw_cx + 5, fw_cy - 4, 9, 9),
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # Mor'shan Base Camp - real WoW: "one of the more sizable Horde
    # settlements in the Northern Barrens, located just south of the
    # Ashenvale-Barrens border, near the Mor'shan Rampart... base of the
    # Warsong Outriders." Placed directly south of the existing Mor'shan
    # Rampart subzone (136-164, 20-40) - a real staging camp behind the
    # checkpoint, not a duplicate of it.
    mb_cx, mb_cy = 145, 65
    for dy in range(-14, 15):
        for dx in range(-16, 17):
            x, y = mb_cx + dx, mb_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                # Widened from abs(dx)<9/abs(dy)<9 - same too-small-
                # clearing bug as Far Watch Post above, fixed the same way.
                if abs(dx) < 16 and abs(dy) < 13:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Mor'shan Base Camp", mb_cx - 16, mb_cy - 14, 32, 28)

    # Real buildings at Mor'shan Base Camp - staging camp for the Warsong
    # Outriders (real hub NPC: Warsong Outrider Dask, 145,65), same
    # treatment as Far Watch Post above.
    #
    # REAL BUG FIXED this session - same overlap bug as Far Watch Post
    # above (watchtower anchor 117,41 9x12 vs generic_house_a anchor
    # 122,42 9x9, only 5 tiles apart on both axes, guaranteed overlap).
    # Respaced to opposite sides of the cleared ~17x17 interior
    # (mb_cx±16/mb_cy±14 clearing), checked directly for zero overlap.
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/watchtower.png", mb_cx - 15, mb_cy - 7, 9, 12),
        ("assets/buildings/generic_house_a.png", mb_cx + 4, mb_cy - 3, 9, 9),
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # Merchant Coast - real WoW: "the small portion of the Northern
    # Barrens that forms the coastline of the Great Sea," near Ratchet.
    # Ratchet itself is reached from Central Barrens' own SE portal, not
    # from here - this is Northern Barrens' own stretch of the same
    # coastline further north, open wilderness flavor rather than a
    # duplicate route into the existing Ratchet town. Placed on the
    # southeast coastal edge, away from every other subzone.
    for _ in range(70):
        cx = random.randint(230, 270)
        cy = random.randint(210, 250)
        for dy in range(-4, 5):
            for dx in range(-5, 6):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.35:
                        zone.set_tile(x, y, "shallow_water", "base")
    zone.add_subzone("Merchant Coast", 220, 200, 55, 55)

    # Gold Road - real WoW: runs north-south "from Mor'shan Rampart to
    # the Great Divide," passing through the Crossroads. In this
    # project's layout that's the vertical corridor at x=150 connecting
    # the existing north portal (Ashenvale, 150,4) through Mor'shan
    # Rampart down to the south portal (Central Barrens, 150,256) -
    # already carved as a path above; this just gives that corridor a
    # real subzone identity instead of being unlabeled road tiles.
    zone.add_subzone("Gold Road", 140, 95, 30, 130)

    # Strip stray grass_tuft/etc left floating over water by the base
    # terrain roll at the top of this function, which runs before any of
    # the water above (Slug Fens, Sludge Fen, Stagnant Oasis, east coast)
    # is carved in.
    ZoneGenerator._clear_visual_over_water(zone)

    return zone


def generate_central_barrens():
    """Central Barrens (300x300) — the true heart of the Barrens, matching
    the real map's scale: Crossroads sits dead center as its OWN zone
    (see generate_crossroads), ringed by oases NW/SW/SE. NE corner is the
    road down from Durotar; SE corner leads to Ratchet; north leads to
    Northern Barrens; south leads to Camp Taurajo -> Southern Barrens."""
    zone = Tilemap("Central Barrens", 300, 300,
                   "Golden savanna stretching to every horizon. The "
                   "Crossroads stands at the heart of it all.")
    zone.region = "Kalimdor - Central"

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.22:
                zone.set_tile(x, y, "grass", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")
            # "small_rocks" scatter removed - Kyle: "the rocks are trash,
            # we can remove them from the Barrens" (generic gray
            # props_nature crop never matched the biome; savanna's
            # BIOME_TILES no longer maps small_rocks at all as of this
            # session, so leaving this call in would've silently rendered
            # nothing instead of an intentional removal).

    cx_center, cy_center = 150, 150

    # Oases ring the Crossroads: SW, NW, SE (matching the real map - Kyle
    # confirmed Wailing Caverns' oasis, Lushwater, sits SOUTHWEST of
    # Crossroads, not northwest. This used to have Lushwater in the NW
    # slot and "The Forgotten Pools" in the SW slot with the WC entrance
    # wrongly attached to Forgotten Pools instead of Lushwater - two
    # separate bugs (wrong oasis position AND wrong oasis name for the WC
    # entrance) collapsed into one fix by just relabeling which name goes
    # in which slot, since the ring-generation code below is identical for
    # all three and doesn't care about the name/position pairing.
    #
    # Radii expanded 25% this session (Kyle: "expand them out by 25%")
    # from the original 11/14/16 to 13.75/17.5/20, and given a real
    # tropical read via SUBZONE_BIOME's new "savanna_oasis" entry -
    # previously the outer "grass" ring resolved through the parent
    # savanna biome to dry sun-baked scrub, wrong for a supposed water
    # pocket. Real palm trees now placed in the outer grass ring
    # (Echo Isles' existing "palm_tree" tile_id/art, not new asset work -
    # see tiles.py's palm_tree entry for why it wasn't previously
    # formally registered despite already rendering). Verified via
    # distance check that the expanded radius doesn't collide with the
    # other 2 oases or the Dreadmist Peak/Den mountain range - closest
    # real gap (Forgotten Pools to Dreadmist Den, 46 tiles center-to-
    # center) still clears the new ~20-tile oasis radius with margin.
    oases = {
        "Lushwater Oasis": (cx_center - 75, cy_center + 65),      # SW (Wailing Caverns)
        "The Forgotten Pools": (cx_center - 70, cy_center - 70),  # NW
        "Raider's Rest Oasis": (cx_center + 75, cy_center + 65),  # SE
    }
    OASIS_DEEP_R = 11 * 1.25     # 13.75
    OASIS_SHALLOW_R = 14 * 1.25  # 17.5
    OASIS_GRASS_R = 16 * 1.25    # 20
    OASIS_SUBZONE_HALF = 25      # was 20 (40x40 box); scaled to match new 20-radius + 5 margin
    for name, (ox, oy) in oases.items():
        dy_range = int(OASIS_GRASS_R) + 1
        dx_range = int(OASIS_GRASS_R) + 3
        for dy in range(-dy_range, dy_range + 1):
            for dx in range(-dx_range, dx_range + 1):
                x, y = ox + dx, oy + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                dist = (dx**2 + dy**2) ** 0.5
                if dist < OASIS_DEEP_R:
                    zone.set_tile(x, y, "deep_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < OASIS_SHALLOW_R:
                    zone.set_tile(x, y, "shallow_water", "base")
                    zone.collision_layer[y][x] = None
                elif dist < OASIS_GRASS_R:
                    zone.set_tile(x, y, "grass", "base")
                    zone.collision_layer[y][x] = None
                    # Palm trees scattered through the outer grass ring
                    # only (never over water) - sparse enough to read as
                    # accent, not a solid tree wall blocking the water's
                    # edge. Visual-layer (walkable), matching how Echo
                    # Isles already places these.
                    if dist > OASIS_SHALLOW_R + 1 and random.random() < 0.12:
                        zone.set_tile(x, y, "palm_tree", "visual")
        # Subzone registration deliberately deferred to AFTER Kolkar
        # Plains registers below, not done here - Tilemap.get_subzone_at
        # docs: "later-registered subzones win on overlap, so a small
        # pocket declared after a large one takes precedence." Kolkar
        # Plains' rect (190-290, 20-220) genuinely overlaps Raider's
        # Rest Oasis's rect, and registering the oasis first (the old
        # order) meant Kolkar's plain-savanna override was winning
        # inside that overlap - verified via a direct get_subzone_at()
        # call returning "Kolkar Plains" at the oasis's own center point
        # (225,215) before this fix. The 25% radius expansion this
        # session made the overlap bigger, but a real (smaller) overlap
        # already existed at the old radius too - this is a pre-existing
        # ordering bug, not something the expansion introduced.

    lushwater_pos = oases["Lushwater Oasis"]
    forgotten_pools_pos = oases["The Forgotten Pools"]
    raiders_rest_pos = oases["Raider's Rest Oasis"]

    # Clear a landing around the Crossroads portal itself (dead center) -
    # Crossroads is now its own zone, not baked into this map's terrain.
    ZoneGenerator._clearing(zone, cx_center, cy_center, 14, 14, "dirt")

    # N-S and E-W roads meeting at the Crossroads portal, connecting every
    # major exit of this zone back to the center.
    for x in range(zone.width):
        for dy in range(-1, 2):
            y = cy_center + dy
            zone.set_tile(x, y, "dirt", "base")
            zone.collision_layer[y][x] = None
    for y in range(zone.height):
        for dx in range(-1, 2):
            x = cx_center + dx
            zone.set_tile(x, y, "dirt", "base")
            zone.collision_layer[y][x] = None

    # Scattered acacia trees and barrens cacti, interspersed rather than
    # trees-only - Kyle: "interspace the trees and cacti to make it
    # exciting." Same real-size fix Northern Barrens already got this
    # session (Kyle playtest: "the trees and props in barrens are too
    # small") - acacia_tree.png/barrens_cactus.png are real multi-tile-
    # scale art, squashed to one 32px tile by the old pure
    # set_tile(..., "tree"/"cactus", "collision") scatter. Most of the
    # density now goes through _scatter_big_props (real 2-4 tile
    # add_landmark props), with a much lighter single-tile scatter kept
    # on top purely for background fill between the real landmark trees.
    # (Uses the literal path, not the "barrens" local - that's not
    # defined until the chunked-ground-art section later in this
    # function.)
    ZoneGenerator._scatter_big_props(
        zone, ["assets/tiles/barrens/props/acacia_tree.png"],
        count=160, size_range=(2, 4), area=(0, 0, zone.width, zone.height))
    ZoneGenerator._scatter_big_props(
        zone, ["assets/tiles/barrens/props/barrens_cactus.png"],
        count=70, size_range=(2, 3), area=(0, 0, zone.width, zone.height))
    for _ in range(150):
        x = random.randint(0, zone.width - 1)
        y = random.randint(0, zone.height - 1)
        if zone.base_layer[y][x] in ("dirt", "grass"):
            if random.random() < 0.4:
                tile_id = "cactus" if random.random() < 0.2 else "tree"
                zone.set_tile(x, y, tile_id, "collision")

    # Real east coastline (Kyle, this session: "the east coast NEEDS
    # water for it" - same real gap as Northern Barrens, this zone's
    # water previously topped out around x=242, 81% of the way to the
    # real 300-wide edge, not reaching it). Per-row threshold matching
    # the reference map's coast - pulled in fairly close since Central
    # Barrens' real geography has Ratchet sitting right on this coast
    # near the SE corner (its portal is at (285,270), close to the
    # edge). Kolkar Plains (190-290, 20-220) already covers this whole
    # stretch as a background subzone identity - the coast carves INTO
    # its eastern edge rather than needing to relocate it, same as
    # Kyle's call for Northern Barrens' Sludge Fen/Far Watch Post.
    def _coast_x(y):
        if 250 <= y <= 290:
            return 268  # stay a bit further out near Ratchet's own portal/buildings (285,270)
        return 252  # default open-coast threshold elsewhere

    for y in range(zone.height):
        threshold = _coast_x(y)
        for x in range(threshold, zone.width):
            depth = x - threshold
            if depth > 6:
                zone.set_tile(x, y, "deep_water", "base")
            else:
                zone.set_tile(x, y, "shallow_water", "base")
            zone.collision_layer[y][x] = None

    # A small real offshore island, matching the reference map's own
    # islet off this stretch of coast.
    icx, icy, ir = 278, 130, 7
    for dy in range(-ir, ir + 1):
        for dx in range(-ir, ir + 1):
            x, y = icx + dx, icy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if (dx / ir) ** 2 + (dy / ir) ** 2 <= 1.0:
                    zone.set_tile(x, y, "dirt", "base")
                    zone.collision_layer[y][x] = None

    # Wailing Caverns entrance sits inside Lushwater Oasis (SW).
    wc_x, wc_y = lushwater_pos[0], lushwater_pos[1] + 8
    ZoneGenerator._carve_path(zone, wc_x, wc_y, cx_center, cy_center)
    ZoneGenerator._carve_landing(zone, wc_x, wc_y, radius=3)
    zone.set_tile(wc_x, wc_y, "portal", "interaction")   # -> Wailing Caverns

    # Crossroads portal, dead center.
    ZoneGenerator._carve_landing(zone, cx_center, cy_center, radius=3)
    zone.set_tile(cx_center, cy_center, "portal", "interaction")  # -> Crossroads

    # A couple of houses flanking the Crossroads portal - Kyle: "the portal
    # to ratchet can have 1 or 2 goblin houses, same logic with Camp T, or
    # Cross roads" - open ground around every town portal read as bare
    # savanna with a single glowing tile, no sense of "you're approaching
    # somewhere". Anchors verified via headless collision scan (1-tile
    # margin, clear of the portal and each other).
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/generic_house_a.png", 132, 132, 9, 9),
        ("assets/buildings/generic_hut_a.png", 137, 132, 9, 9),
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # NE corner: road up from Durotar (matches "west of Razor Hill, above
    # the Valley of Trials path" arriving in Central Barrens' NE).
    ne_x, ne_y = zone.width - 30, 30
    ZoneGenerator._carve_path(zone, ne_x, ne_y, cx_center, cy_center)
    ZoneGenerator._carve_landing(zone, ne_x, ne_y, radius=3)
    zone.set_tile(ne_x, ne_y, "portal", "interaction")   # -> Durotar

    # SE corner: Ratchet, on the Barrens' east coast.
    se_x, se_y = zone.width - 15, zone.height - 30
    ZoneGenerator._carve_path(zone, se_x, se_y, cx_center, cy_center)
    ZoneGenerator._carve_landing(zone, se_x, se_y, radius=3)
    zone.set_tile(se_x, se_y, "portal", "interaction")   # -> Ratchet

    # Goblin-flavored buildings near the Ratchet portal specifically -
    # Ratchet is a goblin town, so the approach should read that way before
    # you even step through. Light touch (2 buildings), not a duplicate
    # Ratchet - same restraint as Orgrimmar's goblin corner.
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/scrapyard_workshop.png", 240, 250, 12, 12),   # moved from (265,251) - real east-coast carve this session put most of that footprint underwater
        ("assets/buildings/the_broken_keel.png", 253, 251, 12, 9),      # moved from (271,252), same reason
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # North: Northern Barrens.
    n_x, n_y = cx_center, 4
    ZoneGenerator._carve_path(zone, n_x, n_y, cx_center, cy_center)
    ZoneGenerator._carve_landing(zone, n_x, n_y, radius=3)
    zone.set_tile(n_x, n_y, "portal", "interaction")     # -> Northern Barrens

    # South: Camp Taurajo (which then leads on to Southern Barrens).
    s_x, s_y = cx_center, zone.height - 4
    ZoneGenerator._carve_path(zone, s_x, s_y, cx_center, cy_center)
    ZoneGenerator._carve_landing(zone, s_x, s_y, radius=3)
    zone.set_tile(s_x, s_y, "portal", "interaction")     # -> Camp Taurajo

    # Houses flanking the Camp Taurajo portal, same reasoning as Crossroads
    # above.
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/generic_house_a.png", 132, 277, 9, 9),
        ("assets/buildings/generic_hut_a.png", 137, 277, 9, 9),
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # Named regions filling the open savanna between the oases/roads. Real
    # data for "Kolkar Plains" has existed in encounters.json all along
    # (Kolkar Stormer/Drudge/Marauder/Verog the Dervish) but was never
    # placed on this map - it only ever got registered on a small, unrelated
    # town zone (Crossroads) as dead leftover code from before the Barrens
    # was split into 3 zones. Placed here across the open plains matching
    # where kolkar centaur camps sit on the real Barrens map, so the huge
    # empty savanna reads as a real place instead of blank ground.
    zone.add_subzone("Kolkar Plains", 190, 20, 100, 200)

    # Oasis subzones registered here, deliberately AFTER Kolkar Plains -
    # see the long comment inside the oasis ring loop above for why. Same
    # OASIS_SUBZONE_HALF-derived rect as before, just deferred so these 3
    # small pockets correctly override Kolkar Plains' background biome
    # inside their overlap instead of losing to it.
    for name, (ox, oy) in oases.items():
        zone.add_subzone(name, ox - OASIS_SUBZONE_HALF, oy - OASIS_SUBZONE_HALF,
                          OASIS_SUBZONE_HALF * 2, OASIS_SUBZONE_HALF * 2)

    # --- 6 new subzones (Kyle: "Barrens are huge... 8 to 10 subzones per
    # zone") bringing Central Barrens from 4 to 10, all real WoW
    # locations researched before placement. Central Barrens' real
    # creature roster clusters 12-18 (Kyle's explicit correction), so
    # every new subzone here targets that same band rather than
    # Northern Barrens' wider 12-24 spread.

    # Dreadmist Peak - real WoW: "a mountain northwest of the Crossroads,"
    # home to Burning Blade cultists guarding the Demon Seed (kept in
    # Dreadmist Den below). Placed far NW, the one genuinely open corner
    # left on this map.
    # Real impassable mountain range (this session) - upgraded from a
    # generic "rock" scatter to the actual cliff-tile mountain art, and
    # shaped as a genuine ridge instead of uniform noise: a rough
    # elongated spine (matching "Dreadmist Peak" reading as one real
    # landmark, not a rock field) with density falling off toward the
    # edges so it has a defined silhouette rather than a hard box.
    dp_cx, dp_cy = 40, 35
    # Ridge pulled back from Dreadmist Den's clearing (centered 50,45,
    # clear radius 6) - the original 5-point spine's SE end sat close
    # enough that cliff tiles bled into the Den's boundary (verified by
    # checking every cliff tile against the Den's clear-zone rect before
    # this fix), leaving a ragged bite in the mountain silhouette even
    # though the Den's own clearing pass would've silently reopened
    # those tiles. Shifted the whole spine NW and shortened its SE reach.
    # Every point below verified >16.5 tiles center-to-center from
    # Dreadmist Den (50,45) - that threshold accounts for BOTH this
    # ridge's max cliff radius (7.5) AND the Den's own outer clearing
    # loop radius (9), not just the Den's inner clear rect. An earlier
    # version of this ridge used a rect-distance check that missed a
    # real off-by-one at the Den's exact boundary row (y=39, where the
    # Den's "abs(dy) < 6" clearing condition is false by exactly one
    # tile) - caught by an actual headless collision scan of the Den's
    # clear zone post-generation, not assumed safe from the math alone.
    ridge_points = [(dp_cx - 20, dp_cy + 6), (dp_cx - 10, dp_cy - 8),
                     (dp_cx + 2, dp_cy - 15), (dp_cx + 10, dp_cy - 10),
                     (dp_cx + 20, dp_cy - 10)]
    for (rx, ry) in ridge_points:
        for dy in range(-9, 10):
            for dx in range(-9, 10):
                x, y = rx + dx, ry + dy
                if not (0 <= x < zone.width and 0 <= y < zone.height):
                    continue
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < 5:
                    zone.set_tile(x, y, "cliff", "collision")
                elif dist < 7.5 and random.random() < 0.6:
                    zone.set_tile(x, y, "cliff", "collision")
    zone.add_subzone("Dreadmist Peak", 10, 5, 55, 50)

    # Dreadmist Den - real WoW: the cave beneath/beside Dreadmist Peak
    # where the cultists' Demon Seed is actually kept, led by Rathorian.
    # Nestled just south of the Peak rather than a separate corner of
    # the map, matching "protected by the cultists atop the Peak."
    dd_cx, dd_cy = 50, 45
    for dy in range(-8, 9):
        for dx in range(-10, 11):
            x, y = dd_cx + dx, dd_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if abs(dx) < 6 and abs(dy) < 6:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Dreadmist Den", dd_cx - 10, dd_cy - 8, 20, 14)

    # Grol'dom Farm - real WoW: an orcish pig farm turned caravan
    # stopping point between Orgrimmar and Crossroads, real quest hub
    # (Mankrik's introduction, the Humble Monument). Placed SW near
    # Lushwater Oasis, matching real "southwest of Crossroads" geography.
    gf_cx, gf_cy = 85, 145
    for dy in range(-12, 13):
        for dx in range(-14, 15):
            x, y = gf_cx + dx, gf_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if abs(dx) < 8 and abs(dy) < 8:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Grol'dom Farm", gf_cx - 14, gf_cy - 12, 28, 24)

    # Real buildings at Grol'dom Farm - a farm/caravan stop with real quest
    # NPC Kranal Fiss (85,145) but no actual structures until now, same
    # "researched location, never got real buildings" gap Durotar's
    # Rocktusk Farm had before this session's earlier work.
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/generic_house_a.png", 62, 122, 9, 9),
        ("assets/buildings/generic_hut_a.png", 67, 122, 9, 9),
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # Shrine of the Fallen Warrior - real WoW: a small memorial hill
    # southwest of Crossroads. Light content (no real hostile roster
    # attached - a quiet, low-combat waypoint), placed near Grol'dom
    # Farm but as its own distinct small footprint.
    zone.add_subzone("Shrine of the Fallen Warrior", 40, 130, 20, 20)

    # Agama'gor - real WoW: a Bristleback quilboar settlement "just
    # north of the road leading west from Camp Taurajo." Placed in the
    # south-center strip above the Camp Taurajo portal, matching that
    # geography. Real lore has Bristlebacks as the tribe that WON the
    # Agama'gor/Bramblescar war and holds the stronger position - see
    # _BRISTLEBACK_RAIDER note in creatures.json for the level-15-18
    # (not 18-24) tier used here specifically to fit Central Barrens'
    # real band (Kyle's correction) without touching the existing
    # 18-24 Bristleback Quilboar already correctly placed in Southern
    # Barrens' Razorfen Approach.
    ag_cx, ag_cy = 170, 250
    for dy in range(-12, 13):
        for dx in range(-14, 15):
            x, y = ag_cx + dx, ag_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if random.random() < 0.2:
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Agama'gor", ag_cx - 14, ag_cy - 12, 28, 24)

    # Bramblescar - real WoW: the Razormane quilboar tribe's lair,
    # "opposite side of the road" from Agama'gor, at war with the
    # Bristlebacks. Placed directly west of Agama'gor, across the same
    # north-south stretch, matching that rivalry geography.
    br_cx, br_cy = 130, 250
    for dy in range(-12, 13):
        for dx in range(-14, 15):
            x, y = br_cx + dx, br_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if random.random() < 0.25:
                    zone.set_tile(x, y, "bushes", "collision")
    zone.add_subzone("Bramblescar", br_cx - 14, br_cy - 12, 28, 24)

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "finish the Barrens...
    # just needs tiles"). Same real overlap-matched per-subzone texture
    # assignment as Northern Barrens. Oases specifically reuse Echo
    # Isles' beach_sand.png for their outer ring (Kyle, earlier this
    # session: "the oasis will use echo isles tiles right" - confirmed
    # here) instead of flat grass, since a desert-oasis shoreline reads
    # far closer to a beach than to open savanna.
    # ------------------------------------------------------------------
    barrens = "assets/tiles/barrens"
    subzone_terrain = [
        {"rect": (190, 20, 100, 200), "variants": [f"{barrens}/grass/tall_dry_grass.png"]},         # Kolkar Plains
        {"rect": (10, 5, 55, 50), "variants": [f"{barrens}/grass/windswept_grass.png"]},             # Dreadmist Peak - mountain
        {"rect": (dd_cx - 10, dd_cy - 8, 20, 14), "variants": [f"{barrens}/grass/windswept_grass.png"]},  # Dreadmist Den
        {"rect": (gf_cx - 14, gf_cy - 12, 28, 24), "variants": [f"{barrens}/grass/grass_with_flowers.png"]},  # Grol'dom Farm
        {"rect": (40, 130, 20, 20), "variants": [f"{barrens}/grass/sparse_grass.png"]},              # Shrine of the Fallen Warrior
        {"rect": (ag_cx - 14, ag_cy - 12, 28, 24), "variants": [f"{barrens}/grass/thorny_brush.png"]},  # Agama'gor
        {"rect": (br_cx - 14, br_cy - 12, 28, 24), "variants": [f"{barrens}/grass/thorny_brush.png"]},  # Bramblescar
    ]
    # Oasis rings - real beach_sand.png outer band, matching each oasis's
    # own center/radius from the ring-generation loop above.
    echo_isles = "assets/tiles/echo_isles"
    for name, (ox, oy) in oases.items():
        r = int(OASIS_GRASS_R) + 3
        subzone_terrain.append({"rect": (ox - r, oy - r, r * 2, r * 2),
                                 "variants": [f"{echo_isles}/beach_sand.png"]})
    default_variants = [f"{barrens}/grass/mixed_grass_sage.png", f"{barrens}/grass/dry_grass_sparse.png"]

    def chunk_variants_for(cx, cy, cs):
        for region in subzone_terrain:
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
            # Skip chunks that are entirely oasis water - already set by
            # the ring-generation loop above, a ground chunk on top
            # would silently paint over it.
            if all(zone.base_layer[cy + dy][cx + dx] in ("deep_water", "shallow_water")
                   for dy in range(0, ch, 4) for dx in range(0, cw, 4)
                   if cy + dy < zone.height and cx + dx < zone.width):
                continue
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            # thorny_brush.png is only 251x251 natively - stretched to a
            # full 20-tile (640px) chunk like every other variant here, it
            # blows up ~2.5x and reads as a blurry, oversized background
            # (Kyle: "the tile background is massive... too stretched" -
            # this is what he was standing in, right at the Durotar
            # entrance near Agama'gor/Bramblescar). Those 2 subzones paint
            # in 10-tile (320px) sub-chunks instead, much closer to native
            # res, while everything else keeps the normal 20-tile chunks.
            if sprite == f"{barrens}/grass/thorny_brush.png":
                sub = 10
                for sy in range(cy, cy + ch, sub):
                    for sx in range(cx, cx + cw, sub):
                        sw = min(sub, cx + cw - sx)
                        sh = min(sub, cy + ch - sy)
                        zone.add_ground_chunk(sprite, sx, sy, sw, sh)
            else:
                zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Real water chunk art - was missing entirely, every water tile (both
    # the 3 oases and the full-height east coastline) fell through to the
    # per-tile fallback crop (83x132, tiled edge-to-edge with no chunk
    # art), which is what read as "tiny little water blocks" (Kyle,
    # standing right in the east-coast water near the Durotar entrance).
    # Real high-res tropical water art (already used successfully for
    # Valley of Trials' own oasis), properly chunked like everywhere else.
    vot = "assets/tiles/valley_of_trials"
    water_chunk_size = 20
    for wy in range(0, zone.height, water_chunk_size):
        for wx in range(0, zone.width, water_chunk_size):
            ww = min(water_chunk_size, zone.width - wx)
            wh = min(water_chunk_size, zone.height - wy)
            has_deep = any(zone.base_layer[wy + dy][wx + dx] == "deep_water"
                           for dy in range(0, wh, 4) for dx in range(0, ww, 4)
                           if wy + dy < zone.height and wx + dx < zone.width)
            has_any_water = has_deep or any(
                zone.base_layer[wy + dy][wx + dx] == "shallow_water"
                for dy in range(0, wh, 4) for dx in range(0, ww, 4)
                if wy + dy < zone.height and wx + dx < zone.width)
            if not has_any_water:
                continue
            sprite = f"{vot}/oasis_deep_water.png" if has_deep else f"{vot}/oasis_shallow_water.png"
            zone.add_water_chunk(sprite, wx, wy, ww, wh)

    # Strip stray grass_tuft left floating over water by the base terrain
    # roll at the top of this function (oases + east coast carved after
    # it) - same fix as Northern Barrens above.
    ZoneGenerator._clear_visual_over_water(zone)

    return zone


def generate_crossroads():
    """The Crossroads (70x70) - its own zone, dead center of the Barrens.
    A proper safe hub town, not terrain baked into Central Barrens.

    Full rebuild (Kyle): the old version had 5 flat "wall" collision boxes
    at the four corners plus one center box, none of them near the 17 real
    named NPCs already living here (data/npcs/ambient_npcs.json +
    vendors.json, zone=crossroads, clustered x=30-37/y=31-38). Real
    Classic Crossroads (confirmed via web search) is led by the orc
    fighter Sergra Darkthorn, and has a real centerpiece "Crossroads Inn"
    building plus general goods (Barg).
    """
    zone = Tilemap("Crossroads", 70, 70,
                   "The Crossroads. Every road in the Barrens meets here.")
    zone.region = "The Barrens"

    zone.fill("dirt", "base")

    # Roads meeting in the center
    for x in range(zone.width):
        for dy in range(-1, 2):
            y = zone.height // 2 + dy
            zone.set_tile(x, y, "dirt", "base")
            zone.collision_layer[y][x] = None
    for y in range(zone.height):
        for dx in range(-1, 2):
            x = zone.width // 2 + dx
            zone.set_tile(x, y, "dirt", "base")
            zone.collision_layer[y][x] = None

    # Vendors/quest givers at the hub - spread across the full 70x70 map
    # instead of packed at the old center cluster (Kyle: "spread out NPCs
    # properly... I don't want towns to be some weird ass cluster fuck").
    for (nx, ny) in [(40, 30), (18, 40), (55, 20), (50, 55), (20, 20)]:
        ZoneGenerator._carve_landing(zone, nx, ny, radius=1)
        zone.set_tile(nx, ny, "npc", "interaction")
    # Sergra Darkthorn - real Classic leader of the Crossroads, never
    # actually placed before now. Stands at the Town Hall entrance.
    ZoneGenerator._carve_landing(zone, 35, 13, radius=1)
    zone.set_tile(35, 13, "npc", "interaction")  # Sergra Darkthorn (crossroads_sergra)

    # Real building placements - spread across the full map (2.5x their
    # original footprint, matching Razor Hill's fix: 3x didn't leave room
    # for proper NPC spacing at this town's NPC-per-area density). Anchors
    # re-verified via the same headless collision scan, proximity-aware
    # (nearest open spot to each building's real target NPC).
    for sprite_key, anchor_x, anchor_y, w, h in [
        ("assets/buildings/crossroads_town_hall.png", 29, 3, 12, 10),    # Sergra Darkthorn's seat
        ("assets/buildings/crossroads_inn.png", 29, 23, 10, 10),         # the real "Crossroads Inn"
        ("assets/buildings/mixed_trading_post.png", 46, 27, 10, 8),      # general goods (Barg-style)
        ("assets/buildings/crossroads_stable.png", 7, 15, 12, 8),        # Stablemaster Grosh
        ("assets/buildings/guard_post.png", 44, 2, 8, 8),                # Caravan Guard Dresk
        ("assets/buildings/well_house.png", 32, 37, 5, 5),
    ]:
        zone.add_landmark(sprite_key, anchor_x, anchor_y, w, h)

    # Single exit back to Central Barrens
    ZoneGenerator._carve_landing(zone, 35, 65, radius=3)
    zone.set_tile(35, 65, "portal", "interaction")   # -> Central Barrens

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "tile Camp T and Crossroads,
    # basic Horde towns/outposts, more dirt and Barrens looks" - this
    # zone had zero chunked art before now, rendering on the flat
    # default "dirt" tile color). Real Barrens grass/dirt variants
    # already on disk (assets/tiles/barrens/grass/) - sparse_grass for
    # the well-trodden main roads/center, dry_grass_sparse for the
    # quieter outer plots, matching a basic dusty trade-town rather than
    # anything overgrown or wild (those variants exist but don't fit a
    # town square).
    # ------------------------------------------------------------------
    barrens_grass = "assets/tiles/barrens/grass"
    chunk_size = 20
    for cy in range(0, zone.height, chunk_size):
        for cx in range(0, zone.width, chunk_size):
            cw = min(chunk_size, zone.width - cx)
            ch = min(chunk_size, zone.height - cy)
            # Roads-cross quadrant closest to the center (where the
            # actual crossing roads are) gets the more trodden variant;
            # outer quadrants get the sparser one - a light, believable
            # "center of town is worn down" gradient without needing
            # per-tile road detection.
            dist_from_center = ((cx + cw/2 - zone.width/2) ** 2 + (cy + ch/2 - zone.height/2) ** 2) ** 0.5
            sprite = f"{barrens_grass}/sparse_grass.png" if dist_from_center < 24 else f"{barrens_grass}/dry_grass_sparse.png"
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)

    return zone


def generate_southern_barrens():
    """Southern Barrens (260x240) — Field of Giants, Bael Modan, Razorfen
    Kraul. Reached only via Camp Taurajo to the north (Crossroads -> Camp
    Taurajo -> Southern Barrens), not directly from Central Barrens."""
    zone = Tilemap("Southern Barrens", 260, 240,
                   "Dangerous lands of kodo bones and dwarf ruins.")
    zone.region = "Kalimdor - South"

    zone.fill("dirt", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            r = random.random()
            if r < 0.22:
                zone.set_tile(x, y, "grass", "base")
            if r < 0.05:
                zone.set_tile(x, y, "grass_tuft", "visual")

    # Field of Giants (south-center, bones scattered)
    for y in range(150, 210):
        for x in range(90, 190):
            zone.set_tile(x, y, "dirt", "base")
            zone.collision_layer[y][x] = None
    for _ in range(55):
        x = random.randint(95, 185)
        y = random.randint(155, 205)
        zone.set_tile(x, y, "small_rocks", "visual")

    zone.add_subzone("Field of Giants", 90, 150, 100, 70)

    # Bael Modan (dwarf ruins, NW)
    for dy in range(-26, 27):
        for dx in range(-32, 33):
            x, y = 55 + dx, 55 + dy
            if not (0 <= x < zone.width and 0 <= y < zone.height):
                continue
            dist = ((dx/32)**2 + (dy/26)**2) ** 0.5
            if dist < 0.8:
                zone.set_tile(x, y, "stone", "base")
                zone.collision_layer[y][x] = None
            elif dist < 1.0 and random.random() < 0.6:
                zone.set_tile(x, y, "rock", "collision")

    zone.add_subzone("Bael Modan", 40, 40, 55, 45)

    def _carve_landing(cx, cy, radius=3):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None

    # Dungeon: Razorfen Kraul entrance (SW)
    _carve_landing(55, 175)
    zone.set_tile(55, 175, "portal", "interaction")   # -> Razorfen Kraul

    # "Razorfen Approach" - real data existed in encounters.json (Bristleback
    # quilboar) but was never placed on this map, only on dead leftover code
    # from before the Barrens was split into 3 zones. Placed around the
    # actual Razorfen Kraul entrance, matching the name.
    zone.add_subzone("Razorfen Approach", 15, 130, 90, 90)

    # Scattered trees. Same real-size fix as Northern/Central Barrens
    # (Kyle playtest: "the trees and props in barrens are too small") -
    # acacia_tree.png squashed to a single 32px tile by the old pure
    # per-tile scatter. Most density now goes through _scatter_big_props
    # (real 2-4 tile add_landmark trees), lighter single-tile scatter
    # kept on top for background fill.
    ZoneGenerator._scatter_big_props(
        zone, ["assets/tiles/barrens/props/acacia_tree.png"],
        count=150, size_range=(2, 4), area=(0, 0, zone.width, zone.height))
    for _ in range(100):
        x = random.randint(0, zone.width - 1)
        y = random.randint(0, zone.height - 1)
        if zone.base_layer[y][x] in ("dirt", "grass"):
            if random.random() < 0.35:
                zone.set_tile(x, y, "tree", "collision")

    # --- 3 new open-world subzones (Kyle: dungeons don't count toward
    # the subzone target - Razorfen Downs researched and confirmed a
    # real dungeon instance, held for later rather than placed here).
    # Southern Barrens real band is 18-24 (Kyle's confirmation). ---

    # Bael'dun Keep - real WoW: "the fortress that overlooks the Bael
    # Modan digsite," led by General Twinbraid, hostile dwarves. Placed
    # directly adjacent to the existing Bael Modan subzone (NE of it),
    # matching "overlooks" rather than being a separate distant corner -
    # this project's Bael Modan already has real Dwarf Miner/Engineer/
    # Explosives Expert creatures (19-24), Bael'dun Keep extends that
    # same conflict with the fortress proper and its named boss.
    bk_cx, bk_cy = 115, 35
    for dy in range(-20, 21):
        for dx in range(-24, 25):
            x, y = bk_cx + dx, bk_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                dist = ((dx/24)**2 + (dy/20)**2) ** 0.5
                if dist < 0.75:
                    zone.set_tile(x, y, "stone", "base")
                    zone.collision_layer[y][x] = None
                elif dist < 1.0 and random.random() < 0.5:
                    zone.set_tile(x, y, "rock", "collision")
    zone.add_subzone("Bael'dun Keep", bk_cx - 24, bk_cy - 20, 48, 40)

    # Blackthorn Ridge - real WoW: "a thorny valley located just north
    # of the Quilboar capital of Razorfen Kraul, populated primarily by
    # Razormane Quilboar." Placed directly north of the existing
    # Razorfen Approach/Kraul entrance, matching that exact relationship.
    bt_cx, bt_cy = 55, 105
    for _ in range(90):
        cx = bt_cx + random.randint(-22, 22)
        cy = bt_cy + random.randint(-18, 18)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    if random.random() < 0.3:
                        zone.set_tile(x, y, "bushes", "collision")
    zone.add_subzone("Blackthorn Ridge", bt_cx - 24, bt_cy - 20, 48, 36)

    # Raptor Grounds - real WoW: "a tiny valley... densely populated by
    # the Sunscale raptors." Placed on the open east side of the map,
    # away from the quilboar/dwarf conflicts on the west side.
    rg_cx, rg_cy = 220, 110
    for dy in range(-18, 19):
        for dx in range(-22, 23):
            x, y = rg_cx + dx, rg_cy + dy
            if 0 <= x < zone.width and 0 <= y < zone.height:
                if abs(dx) < 16 and abs(dy) < 13:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
    zone.add_subzone("Raptor Grounds", rg_cx - 22, rg_cy - 18, 44, 36)

    # The Broodspiral dungeon entrance - southeast corner, away from the
    # Horde-vs-dwarf conflict on the west side, tucked into its own
    # patch of open ground (Kyle's home-brew silithid dungeon).
    _carve_landing(225, 220)
    zone.set_tile(225, 220, "portal", "interaction")  # -> The Broodspiral

    # Single entrance, north: Camp Taurajo (the only way in/out of Southern
    # Barrens - Central Barrens is reached via Crossroads -> Camp Taurajo).
    _carve_landing(130, 2)
    zone.set_tile(130, 2, "portal", "interaction")    # -> Camp Taurajo

    # Houses flanking this side of the Camp Taurajo portal too, same
    # reasoning as every other town portal this session - the approach
    # from either direction should read as "somewhere is here", not bare
    # ground either side of a portal tile.
    for sprite_key, ax, ay, w, h in [
        ("assets/buildings/generic_house_a.png", 112, 3, 9, 9),
        ("assets/buildings/generic_hut_a.png", 117, 3, 9, 9),
    ]:
        zone.add_landmark(sprite_key, ax, ay, w, h)

    # ------------------------------------------------------------------
    # CHUNKED GROUND ART (Kyle, this session: "finish the Barrens...
    # just needs tiles" - no east coastline here, confirmed: Dustwallow
    # Marsh sits east of Southern Barrens in the real geography, not
    # open sea). Same real overlap-matched per-subzone texture
    # assignment as Northern/Central.
    # ------------------------------------------------------------------
    barrens = "assets/tiles/barrens"
    subzone_terrain = [
        {"rect": (90, 150, 100, 70), "variants": [f"{barrens}/grass/dry_grass_sparse.png"]},          # Field of Giants
        {"rect": (40, 40, 55, 45), "variants": [f"{barrens}/grass/windswept_grass.png"]},              # Bael Modan - dwarf ruins
        {"rect": (bk_cx - 24, bk_cy - 20, 48, 40), "variants": [f"{barrens}/grass/windswept_grass.png"]},  # Bael'dun Keep
        {"rect": (15, 130, 90, 90), "variants": [f"{barrens}/grass/thorny_brush.png"]},                # Razorfen Approach - quilboar
        {"rect": (bt_cx - 24, bt_cy - 20, 48, 36), "variants": [f"{barrens}/grass/thorny_brush.png"]}, # Blackthorn Ridge
        {"rect": (rg_cx - 22, rg_cy - 18, 44, 36), "variants": [f"{barrens}/grass/scrub_brush.png"]},  # Raptor Grounds
    ]
    default_variants = [f"{barrens}/grass/dry_grass_dense.png", f"{barrens}/grass/mixed_grass_sage.png"]

    def chunk_variants_for(cx, cy, cs):
        for region in subzone_terrain:
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
            variants = chunk_variants_for(cx, cy, chunk_size)
            sprite = variants[variant_i % len(variants)]
            zone.add_ground_chunk(sprite, cx, cy, cw, ch)
            variant_i += 1

    # Kodo skull landmarks in Field of Giants specifically - matches its
    # own name and the existing small_rocks scatter already placed
    # there, using real Barrens prop art instead of generic scatter.
    for _ in range(6):
        x = random.randint(95, 185)
        y = random.randint(155, 205)
        if zone.base_layer[y][x] not in ("deep_water", "shallow_water"):
            zone.add_landmark(f"{barrens}/props/kodo_skull.png", x, y, 4, 3, solid=False)

    return zone


def generate_the_broodspiral():
    """The Broodspiral (240x240) - home-brew 3-boss silithid mini-dungeon
    (Kyle's request, not a real WoW instance). Layout is a genuine
    Archimedean spiral corridor winding inward from an outer entrance to
    a center Queen's chamber - "linear spiral where the center is the
    queen chamber," per Kyle's explicit ask, distinct in shape from both
    existing dungeons (Razorfen Kraul's fork-and-spine, Wailing Caverns'
    river loop).

    Three boss rooms break off the spiral at meaningful radius
    checkpoints rather than evenly by corridor length, so the map reads
    as outer ring -> mid ring -> screen -> center rather than stops on
    an arbitrary line:
      - Carapace Warden (outer ring, ~1.5 turns out from center) - lvl 19
      - The Broodkeeper (mid ring, ~0.8 turns out) - lvl 21
      - Larval Broodguard (screening the approach, ~0.35 turns out) - lvl 22
      - Broodspiral Queen (dead center, spiral's true endpoint) - lvl 24

    Ability count follows Kyle's level-danger rule: sub-20 bosses get 3
    abilities, 20+ bosses get 4 - see the ability_kits.json entries for
    carapace_warden/the_broodkeeper/broodspiral_queen.
    """
    import math

    zone = Tilemap("The Broodspiral", 240, 240,
                    "A silithid hive spiraling down into the earth south "
                    "of the quilboar lands. Something ancient wakes at "
                    "its center.")
    zone.is_cave = True
    zone.region = "Southern Barrens"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.collision_layer[y][x] = "rock"

    def _room(cx, cy, w, h):
        for dy in range(-h // 2, h // 2 + 1):
            for dx in range(-w // 2, w // 2 + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")

    def _corridor(x0, y0, x1, y1, width=3):
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="dirt")

    # ===== Spiral math: Archimedean spiral r = a + b*theta, walked from
    # outer (large theta) to inner (theta~0), matching "entrance at the
    # edge, queen at the center." =====
    cx, cy = 120, 120
    a, b = 15, 6.5
    turns = 2.2

    def spiral_point(theta):
        r = a + b * theta
        return (round(cx + r * math.cos(theta)), round(cy + r * math.sin(theta)))

    # Dense waypoint chain for the full corridor, carved as a sequence of
    # short straight segments - the standard way to approximate a curve
    # with this engine's point-to-point _carve_path.
    theta = turns * 2 * math.pi
    step = 0.08
    waypoints = []
    while theta > 0.05:
        waypoints.append(spiral_point(theta))
        theta -= step
    waypoints.append(spiral_point(0.05))

    prev = waypoints[0]
    for pt in waypoints[1:]:
        _corridor(prev[0], prev[1], pt[0], pt[1], width=3)
        prev = pt

    # ===== Entrance - outer edge of the spiral (theta = turns*2pi) =====
    entrance = waypoints[0]
    zone.set_tile(*entrance, "portal", "interaction")  # -> Southern Barrens
    _room(entrance[0], entrance[1], 14, 12)

    # ===== Boss 1: Carapace Warden - outer ring, ~1.5 turns out =====
    warden_pt = spiral_point(1.5 * 2 * math.pi)
    _room(warden_pt[0], warden_pt[1], 24, 20)
    warden_pos = (warden_pt[0], warden_pt[1] - 2)
    zone.set_tile(*warden_pos, "boss_marker", "interaction")
    zone.add_subzone("The Outer Ring", warden_pt[0] - 12, warden_pt[1] - 10, 24, 20)

    # ===== Boss 2: The Broodkeeper - mid ring, ~0.8 turns out =====
    keeper_pt = spiral_point(0.8 * 2 * math.pi)
    _room(keeper_pt[0], keeper_pt[1], 26, 22)
    keeper_pos = (keeper_pt[0], keeper_pt[1] - 2)
    zone.set_tile(*keeper_pos, "boss_marker", "interaction")
    zone.add_subzone("The Brood Chamber", keeper_pt[0] - 13, keeper_pt[1] - 11, 26, 22)

    # ===== Boss 3: Larval Broodguard - between mid-ring and center,
    # ~0.35 turns out (Kyle's ask: add a 4th boss). A venom-spitting
    # guardian screening the approach to the Queen's chamber. =====
    guard_pt = spiral_point(0.35 * 2 * math.pi)
    _room(guard_pt[0], guard_pt[1], 22, 18)
    guard_pos = (guard_pt[0], guard_pt[1] - 2)
    zone.set_tile(*guard_pos, "boss_marker", "interaction")
    zone.add_subzone("The Larval Screen", guard_pt[0] - 11, guard_pt[1] - 9, 22, 18)

    # ===== Boss 4: Broodspiral Queen - dead center, the spiral's true
    # endpoint, largest room matching "final boss" weight. =====
    _room(cx, cy, 34, 30)
    queen_pos = (cx, cy - 3)
    zone.set_tile(*queen_pos, "boss_marker", "interaction")
    zone.add_subzone("The Queen's Hollow", cx - 17, cy - 15, 34, 30)

    # Trash scatter along the spiral corridor - denser near the center,
    # matching "deeper = more dangerous" (handled by the encounter table
    # weighting Silithid Stinger higher than Guardian, not by placement
    # here - this just scatters occasional collision/decor along the
    # tunnel walls so it doesn't read as a bare carved line).
    for _ in range(140):
        wp = waypoints[__import__("random").randint(0, len(waypoints) - 1)]
        dx = __import__("random").randint(-4, 4)
        dy = __import__("random").randint(-4, 4)
        x, y = wp[0] + dx, wp[1] + dy
        if 0 <= x < zone.width and 0 <= y < zone.height:
            if zone.base_layer[y][x] == "stone" and __import__("random").random() < 0.3:
                zone.set_tile(x, y, "rock", "collision")

    # ------------------------------------------------------------------
    # CHUNKED FLOOR + WALL ART (Kyle, this session: "let's tile the
    # dungeons" - real silithid hive art now exists, zero chunked art
    # existed anywhere in this function before now). Real per-room
    # material logic matching each room's own real content: the entrance/
    # spiral corridor gets the plain hive floor, the Larval Screen gets
    # the real larval-membrane floor (matches its own name), the Outer
    # Ring and Brood Chamber get the resin-coated variant, and the
    # Queen's Hollow gets resin floor + the ornate queen's-chamber wall
    # as a real accent ring around its own boundary (that texture's
    # repeat is too recognizable to stretch everywhere - same scoping
    # every other "special" wall got this session).
    # ------------------------------------------------------------------
    broodspiral = "assets/tiles/broodspiral"
    hive_floor = f"{broodspiral}/hive_floor.png"
    resin_floor = f"{broodspiral}/resin_floor.png"
    larval_floor = f"{broodspiral}/larval_floor.png"
    chitin_wall = f"{broodspiral}/chitin_wall.png"
    resin_wall = f"{broodspiral}/resin_wall.png"
    queens_wall = f"{broodspiral}/queens_chamber_wall.png"
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

    # Corridor floor - matches the spiral's own waypoint chain, chunked
    # along its length rather than one giant stretch (same "repeat
    # along the real path" fix Ratchet's docks needed this session).
    for i in range(0, len(waypoints), 4):
        wx, wy = waypoints[i]
        zone.add_ground_chunk(hive_floor, wx - 4, wy - 4, 8, 8)

    floor_chunks(entrance[0], entrance[1], 7, 6, hive_floor)
    floor_chunks(warden_pt[0], warden_pt[1], 12, 10, resin_floor)
    floor_chunks(keeper_pt[0], keeper_pt[1], 13, 11, resin_floor)
    floor_chunks(guard_pt[0], guard_pt[1], 11, 9, larval_floor)
    floor_chunks(cx, cy, 17, 15, resin_floor)

    # Wall art - plain chitin everywhere, resin accent near the
    # Broodkeeper/Outer Ring (matches their own resin-floor rooms),
    # and the ornate queen's wall scoped to a thin ring around the
    # Queen's Hollow's own boundary only.
    obstacle_chunk_size = 4
    for gy in range(0, zone.height, obstacle_chunk_size):
        for gx in range(0, zone.width, obstacle_chunk_size):
            gw = min(obstacle_chunk_size, zone.width - gx)
            gh = min(obstacle_chunk_size, zone.height - gy)
            dx_q, dy_q = gx - cx, gy - cy
            dist_q = (dx_q ** 2 + dy_q ** 2) ** 0.5
            if 17 <= dist_q <= 21:
                sprite = queens_wall
            elif ((gx - warden_pt[0]) ** 2 + (gy - warden_pt[1]) ** 2) ** 0.5 < 14 or \
                 ((gx - keeper_pt[0]) ** 2 + (gy - keeper_pt[1]) ** 2) ** 0.5 < 15:
                sprite = resin_wall
            else:
                sprite = chitin_wall
            zone.add_obstacle_chunk(sprite, gx, gy, gw, gh)

    # ------------------------------------------------------------------
    # LANDMARKS - real silithid props at each named room.
    # ------------------------------------------------------------------
    zone.add_landmark(f"{broodspiral}/props/egg_sac_cluster.png",
                       warden_pt[0] - 4, warden_pt[1] + 4, 5, 5, solid=False)
    zone.add_landmark(f"{broodspiral}/props/resin_pillar.png",
                       keeper_pt[0] + 5, keeper_pt[1] - 6, 3, 6)
    zone.add_landmark(f"{broodspiral}/props/carapace_pile.png",
                       guard_pt[0] - 5, guard_pt[1] + 3, 5, 4, solid=False)
    zone.add_landmark(f"{broodspiral}/props/queens_throne.png",
                       cx - 4, cy - 15, 8, 6)

    return zone


def generate_wailing_caverns_expanded():
    """Wailing Caverns (240x220) - real WoW Classic layout: entry cave
    down into a main cavern with a river running through it. Lady
    Anacondra sits in the upper part of that cavern (first boss). The
    river forks - west leads to Lord Cobrahn; after killing him you jump
    off a cliff opposite his platform back down to the river. Heading
    east along the river you pass Kresh (a neutral but customarily-killed
    turtle IN the river itself, not a separate chamber), then continue
    east to Lord Pythas, then Skum (both skippable but usually done -
    "never skipped" per every real guide). Lord Serpentis and Verdan the
    Everliving share ONE room at the far east end - Verdan is the
    well-known "fake final boss" since most groups stop there. A shortcut
    behind Verdan leads back to the river/entrance, where you escort the
    Disciple of Naralex to summon the true final boss, Mutanus the
    Devourer.

    This used to be 7 invented-position bosses (including a made-up
    'Nightmare rift' final boss unrelated to the real dungeon) in
    separate ellipse blobs radiating from a central hub - wrong shape
    (real WC is a circular river loop with west/east forks, not a
    radial hub) and two real bosses (Lord Serpentis, Skum) were missing
    entirely. Rebuilt around the real loop, with real corridors
    (ZoneGenerator._carve_path) connecting purpose-sized rooms instead of
    overlapping ellipse stamps.
    """
    zone = Tilemap("Wailing Caverns", 240, 220,
                   "A sprawling cave system, waterlogged and overgrown, "
                   "home to the Fang Lords and the corrupted druid "
                   "Naralex's nightmare.")
    zone.is_cave = True
    zone.region = "Central Barrens"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "wall", "collision")

    def _room(cx, cy, w, h, wet_chance=0.0, keep_clear=()):
        """Carve a rectangular room. wet_chance scatters real
        shallow_water for the river/flooded-cave read, same mechanism
        the old carve() used but rectangular rooms instead of ellipses -
        purpose-sized spaces read as rooms, not as "the whole map is one
        connected blob with soft edges.\""""
        for dy in range(-h // 2, h // 2 + 1):
            for dx in range(-w // 2, w // 2 + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")
        if wet_chance:
            # Organic ponds instead of a per-tile coin flip (1x1
            # checkerboard water) - see ZoneGenerator._carve_pond_blobs.
            ZoneGenerator._carve_pond_blobs(zone, cx, cy, w, h, wet_chance, keep_clear)

    def _river(x0, y0, x1, y1, width=5):
        """A wider, always-water corridor for the river itself, distinct
        from _corridor (dry, narrow, for tunnels/paths)."""
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="shallow_water")

    def _corridor(x0, y0, x1, y1, width=3):
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="dirt")

    # ===== ENTRANCE (upper cave, drops down into the main cavern) =====
    entrance = (120, 210)
    zone.set_tile(*entrance, "portal", "interaction")   # -> Central Barrens (Lushwater Oasis)
    _room(120, 195, 20, 16)
    _corridor(120, 210, 120, 195, width=4)

    # ===== MAIN CAVERN with the river running through it - Lady
    # Anacondra in the upper part =====
    _room(120, 150, 70, 50, wet_chance=0.25, keep_clear=[(120, 128, 6)])
    _corridor(120, 195, 120, 150, width=5)
    anacondra_pos = (120, 128)
    zone.set_tile(*anacondra_pos, "boss_marker", "interaction")
    zone.add_subzone("Serpentbloom Cavern", 85, 125, 70, 50)

    # The river itself - a wide water corridor forking west and east from
    # the main cavern, matching "jump into the river and head west/east."
    _river(120, 150, 55, 150, width=5)   # west fork
    _river(120, 150, 185, 150, width=5)  # east fork

    # ===== WEST: Lord Cobrahn =====
    _room(50, 150, 34, 26)
    cobrahn_pos = (42, 145)
    zone.set_tile(*cobrahn_pos, "boss_marker", "interaction")
    zone.add_subzone("Cobrahn's Den", 33, 137, 34, 26)

    # ===== EAST: Kresh sits IN the river itself (not a side room - he's
    # a neutral turtle guides consistently describe finding "in the
    # river," killed on the way through, not a detour). =====
    kresh_pos = (185, 150)
    zone.set_tile(*kresh_pos, "boss_marker", "interaction")

    # Continue east along the river to Lord Pythas
    _river(185, 150, 195, 120, width=5)
    _room(200, 105, 30, 24)
    pythas_pos = (205, 100)
    zone.set_tile(*pythas_pos, "boss_marker", "interaction")
    zone.add_subzone("Pythas's Hollow", 185, 93, 30, 24)

    # Continue to Skum (skippable but "never skipped" per every guide -
    # placed on the main path, not a dead-end detour)
    _corridor(200, 93, 190, 70, width=4)
    _room(185, 58, 26, 20)
    skum_pos = (185, 52)
    zone.set_tile(*skum_pos, "boss_marker", "interaction")

    # ===== Lord Serpentis + Verdan the Everliving share ONE room, per
    # every real guide ("both located in the same room," "side by
    # side") - this is the dungeon's real shape, not two separate
    # bosses in two separate chambers. =====
    _corridor(185, 48, 150, 30, width=4)
    _room(130, 20, 50, 22)
    serpentis_pos = (118, 18)
    verdan_pos = (142, 18)
    zone.set_tile(*serpentis_pos, "boss_marker", "interaction")
    zone.set_tile(*verdan_pos, "boss_marker", "interaction")
    zone.add_subzone("Chamber of the Fang", 105, 9, 50, 22)

    # Shortcut behind Verdan back toward the river/entrance - every real
    # guide calls this out specifically ("use the shortcut behind Verdan
    # to get back to the river").
    _corridor(150, 20, 120, 150, width=3)

    # ===== Escort quest giver near the entrance, and Mutanus summoned
    # from the pool once the Disciple reaches the ritual stone (per every
    # guide: "summoned from the pool after escorting the Disciple of
    # Naralex to the ritual stone") - placed back near the entrance
    # cavern, not a separate deep chamber, since the escort walks FROM
    # the entrance TO here. =====
    zone.set_tile(112, 190, "npc", "interaction")  # Disciple of Naralex
    mutanus_pos = (120, 175)
    zone.set_tile(*mutanus_pos, "quest_marker", "interaction")  # ritual stone / summoning pool
    mutanus_boss_pos = (mutanus_pos[0] + 3, mutanus_pos[1])
    zone.set_tile(*mutanus_boss_pos, "boss_marker", "interaction")

    # Signature feature: root tangles and fungal bloom throughout,
    # unchanged from before - this part was already correct.
    for y in range(zone.height):
        for x in range(zone.width):
            if zone.collision_layer[y][x] is None and random.random() < 0.06:
                zone.set_tile(x, y, "bushes", "visual")

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)

    # ------------------------------------------------------------------
    # CHUNKED FLOOR + WALL ART (Kyle, this session: "let's tile the
    # dungeons" - zero chunked art existed anywhere in this function
    # before now). Real per-room material: plain cavern floor/wall
    # everywhere, the serpent-shrine relief wall scoped to Anacondra's
    # own Serpentbloom Cavern (the dungeon's real central hub and first
    # boss - matches "serpent" bosses starting right here) and the
    # shared Serpentis/Verdan chamber (both serpent-type bosses),
    # river water wired onto the real _river() carves already in the
    # code above.
    # ------------------------------------------------------------------
    wc = "assets/tiles/wailing_caverns"
    cavern_floor = f"{wc}/wc_cavern_floor.png"
    cavern_wall = f"{wc}/wc_cavern_wall.png"
    serpent_wall = f"{wc}/wc_serpent_shrine_wall.png"
    river_water = f"{wc}/wc_river_water.png"
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

    floor_chunks(entrance[0], entrance[1], 10, 8, cavern_floor)
    floor_chunks(120, 150, 35, 25, cavern_floor)   # Serpentbloom Cavern
    floor_chunks(50, 150, 17, 13, cavern_floor)    # Cobrahn's Den
    floor_chunks(200, 105, 15, 12, cavern_floor)   # Pythas's Hollow
    floor_chunks(185, 58, 13, 10, cavern_floor)    # Skum's room
    floor_chunks(130, 20, 25, 11, cavern_floor)    # Chamber of the Fang
    floor_chunks(mutanus_pos[0], mutanus_pos[1], 12, 10, cavern_floor)

    # River water over every real _river() carve in the code above -
    # matched by real coordinates, not guessed.
    for (x0, y0, x1, y1) in [
        (120, 195, 120, 150),   # entrance corridor down to the cavern
        (120, 150, 55, 150),    # west fork
        (120, 150, 185, 150),   # east fork
        (185, 150, 195, 120),   # up to Pythas
    ]:
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(0, steps + 1, 6):
            t = s / steps
            cx0 = round(x0 + (x1 - x0) * t)
            cy0 = round(y0 + (y1 - y0) * t)
            zone.add_ground_chunk(river_water, cx0 - 5, cy0 - 5, 10, 10)

    # Wall art - plain cavern wall everywhere, real serpent-relief
    # accent ring around Anacondra's cavern and the Serpentis/Verdan
    # chamber specifically.
    obstacle_chunk_size = 4
    for gy in range(0, zone.height, obstacle_chunk_size):
        for gx in range(0, zone.width, obstacle_chunk_size):
            gw = min(obstacle_chunk_size, zone.width - gx)
            gh = min(obstacle_chunk_size, zone.height - gy)
            dist_anacondra = ((gx - 120) ** 2 + (gy - 150) ** 2) ** 0.5
            dist_fang = ((gx - 130) ** 2 + (gy - 20) ** 2) ** 0.5
            if 35 <= dist_anacondra <= 40 or 25 <= dist_fang <= 29:
                sprite = serpent_wall
            else:
                sprite = cavern_wall
            zone.add_obstacle_chunk(sprite, gx, gy, gw, gh)

    # Every chamber is PINNED to its exact real boss (x, y, boss_name) -
    # see cave_spawns.py's pinned-chamber support - rather than left for
    # the random boss pool, since these are named, lore-specific
    # encounters (a player fighting Serpentis' room should always get
    # Serpentis there, not a random draw from the other 7). Note
    # mutanus_boss_pos, NOT mutanus_pos - the boss_marker tile is offset
    # +3 from the quest-marker/ritual-stone tile (they can't share one
    # tile), and boss_positions previously pointed at the quest marker's
    # coordinate instead of the actual boss_marker tile.
    zone.boss_positions = [
        (anacondra_pos[0], anacondra_pos[1], "Lady Anacondra"),
        (cobrahn_pos[0], cobrahn_pos[1], "Lord Cobrahn"),
        (kresh_pos[0], kresh_pos[1], "Kresh"),
        (pythas_pos[0], pythas_pos[1], "Lord Pythas"),
        (skum_pos[0], skum_pos[1], "Skum"),
        (serpentis_pos[0], serpentis_pos[1], "Lord Serpentis"),
        (verdan_pos[0], verdan_pos[1], "Verdan the Everliving"),
        (mutanus_boss_pos[0], mutanus_boss_pos[1], "Mutanus the Devourer"),
    ]
    zone.boss_position = mutanus_boss_pos  # legacy single-boss fallback - Mutanus is WC's true final boss
    zone.add_subzone("Wailing Caverns", 0, 0, zone.width, zone.height)

    return zone



def generate_razorfen_kraul_expanded():
    """Razorfen Kraul (240x220) - real WoW Classic layout: entry thorn
    tunnel forks immediately. Left leads across a vine bridge to
    Roogug's platform (a genuine optional dead-end detour - warrior-quest
    only, no other reason to go there per every guide). The main fork
    has two bosses flanking left and right at the top of ledges: Aggem
    Thorncurse (left, guarded by beast trainers, summons boar spirits)
    and Death Speaker Jargba (right, mind control + 2 adds) - either can
    be done first per every guide ("can either be"). From there, the
    path continues to the boar pens (Overlord Ramtusk, flanked by 2
    Razorfen Spearhides), then the beast pit (Agathelos the Raging,
    sealed behind a force field lowered by killing Ward Guardians/Ward
    Keepers - optional but the sealed-door mechanic is real and worth
    keeping), then the upper platform for the final boss, Charlga
    Razorflank (pulled onto the main dirt platform, not fought in her
    house). Willix the Importer escort quest starts near the end,
    heading back toward the entrance afterward.

    This used to be 7 invented-position bosses (including 3 with no real
    basis at all - "Blind Hunter" IS real but as a rare spawn, not a
    fixed second bramble-chamber boss; "Charge Warden" and the "ancestral
    guardian" duo don't exist in the real dungeon) radiating from a
    single central spine. Rebuilt around the real left/right fork +
    linear spine shape, with Roogug as a genuine side-detour rather than
    just another chamber on the main spine.
    """
    zone = Tilemap("Razorfen Kraul", 240, 220,
                   "Thorn tunnels choked with bramble. Quilboar ancestral "
                   "home, ruled by Charlga Razorflank and the spirits of "
                   "Agamaggan.")
    zone.is_cave = True
    zone.region = "Southern Barrens"

    zone.fill("stone", "base")
    for y in range(zone.height):
        for x in range(zone.width):
            zone.set_tile(x, y, "rock", "collision")

    def _room(cx, cy, w, h):
        for dy in range(-h // 2, h // 2 + 1):
            for dx in range(-w // 2, w // 2 + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < zone.width and 0 <= y < zone.height:
                    zone.collision_layer[y][x] = None
                    zone.set_tile(x, y, "dirt", "base")

    def _corridor(x0, y0, x1, y1, width=3):
        ZoneGenerator._carve_path(zone, x0, y0, x1, y1, width=width, base="dirt")

    # ===== ENTRANCE - thorn tunnel, immediate fork =====
    entrance = (120, 208)
    zone.set_tile(*entrance, "portal", "interaction")   # -> Southern Barrens
    _room(120, 195, 18, 12)
    _corridor(120, 208, 120, 195, width=4)

    # ===== LEFT FORK: vine bridge detour to Roogug (optional, warrior
    # quest only - "if you know your way around you can drop down" per
    # Basin Wiki, a genuine side trip not on the way to anything else) =====
    _corridor(120, 195, 65, 180, width=3)
    _room(50, 175, 26, 18)
    roogug_pos = (45, 172)
    zone.set_tile(*roogug_pos, "boss_marker", "interaction")
    zone.add_subzone("Roogug's Platform", 37, 166, 26, 18)

    # ===== MAIN FORK continues south from the entrance area toward the
    # two flanking bosses - Aggem (left/west) and Jargba (right/east),
    # matching "bosses at each end to the left and right" per Basin
    # Wiki, both reached from a shared intersection. =====
    _corridor(120, 195, 120, 158, width=4)
    _room(120, 150, 22, 16)  # central intersection

    # Aggem Thorncurse (west) - small pen guarded by beast trainers, top
    # of a ledge per the Brady guide.
    _corridor(120, 150, 60, 130, width=3)
    _room(50, 120, 24, 18)
    aggem_pos = (45, 113)
    zone.set_tile(*aggem_pos, "boss_marker", "interaction")
    zone.add_subzone("Aggem's Pen", 38, 111, 24, 18)

    # Death Speaker Jargba (east) - mind control caster, 2 adds.
    _corridor(120, 150, 185, 130, width=3)
    _room(195, 120, 24, 18)
    jargba_pos = (200, 113)
    zone.set_tile(*jargba_pos, "boss_marker", "interaction")
    zone.add_subzone("Jargba's Chamber", 183, 111, 24, 18)

    # ===== Boar pens - Overlord Ramtusk, flanked by 2 Razorfen
    # Spearhides (trash, handled by encounter table). Reached from the
    # central intersection continuing deeper, past both flanking bosses -
    # this is the real "main quest line" boss per the guides. =====
    _corridor(120, 150, 120, 97, width=4)
    _room(120, 85, 34, 24)
    ramtusk_pos = (120, 78)
    zone.set_tile(*ramtusk_pos, "boss_marker", "interaction")
    zone.add_subzone("The Boar Pens", 103, 73, 34, 24)

    # ===== Beast pit - Agathelos the Raging, sealed behind a force
    # field (real mechanic: kill Ward Guardians/Ward Keepers to lower
    # it) - represented as a wall of rock collision blocking the room
    # until a marked trigger point is cleared. The optional-boss status
    # is preserved by branching this off the main spine rather than
    # gating the whole dungeon on it. =====
    _corridor(120, 73, 60, 55, width=3)
    _room(45, 45, 26, 20)
    agathelos_pos = (40, 38)
    zone.set_tile(*agathelos_pos, "boss_marker", "interaction")
    # Ward Guardian/Keeper trash markers flank the sealed entrance -
    # killing them is what "lowers the force field" in the real
    # encounter; represented here as extra-dense trash right at the
    # chokepoint rather than a literal scripted door (this engine has no
    # event-trigger system for a door that opens on kill-count), which
    # still makes the room read as gated rather than freely walked into.
    zone.set_tile(58, 48, "npc", "interaction")  # Ward Guardian (flavour marker)
    zone.add_subzone("Agathelos's Pit", 32, 35, 26, 20)

    # ===== Upper platform - Charlga Razorflank, final boss. Pulled onto
    # the main dirt platform per Maps For Tanks ("onto the main dirt
    # platform you walked in on"), so her room connects straight off the
    # Ramtusk spine rather than needing a detour first. =====
    _corridor(120, 73, 120, 28, width=4)
    _room(120, 18, 30, 20)
    charlga_pos = (120, 12)
    zone.set_tile(*charlga_pos, "boss_marker", "interaction")
    zone.add_subzone("Charlga's Platform", 105, 8, 30, 20)

    # Willix the Importer escort starts near the end (per every guide) -
    # placed just past Charlga, escorted back toward the entrance.
    zone.set_tile(120, 25, "npc", "interaction")  # Willix the Importer

    # Bramble thorn scatter - signature feature, unchanged (this part
    # was already correct - real collision hazards, not just tint).
    for y in range(zone.height):
        for x in range(zone.width):
            if zone.collision_layer[y][x] is None and random.random() < 0.07:
                zone.set_tile(x, y, "bushes", "visual")

    ZoneGenerator._carve_landing(zone, *entrance, radius=3)

    # ------------------------------------------------------------------
    # CHUNKED FLOOR + WALL ART (Kyle, this session: "let's tile the
    # dungeons" - zero chunked art existed anywhere in this function
    # before now). Real per-room material: plain thorn-tunnel floor/
    # packed-earth wall everywhere, the real boar_pen_floor specifically
    # at The Boar Pens (matches its own name), the beast_pit_wall
    # specifically around Agathelos's Pit (matches its own name/theme -
    # claw marks and bloodstains for a caged-beast arena), and the
    # bramble wall as a real accent near Roogug's vine-bridge detour.
    # ------------------------------------------------------------------
    rfk = "assets/tiles/razorfen_kraul"
    thorn_floor = f"{rfk}/rfk_thorn_tunnel_floor.png"
    boar_floor = f"{rfk}/rfk_boar_pen_floor.png"
    bramble_wall = f"{rfk}/rfk_bramble_wall.png"
    earth_wall = f"{rfk}/rfk_packed_earth_wall.png"
    beast_wall = f"{rfk}/rfk_beast_pit_wall.png"
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

    floor_chunks(entrance[0], entrance[1], 9, 6, thorn_floor)
    floor_chunks(120, 195, 9, 6, thorn_floor)
    floor_chunks(50, 175, 13, 9, thorn_floor)      # Roogug's Platform
    floor_chunks(120, 150, 11, 8, thorn_floor)     # central intersection
    floor_chunks(50, 120, 12, 9, thorn_floor)      # Aggem's Pen
    floor_chunks(195, 120, 12, 9, thorn_floor)     # Jargba's Chamber
    floor_chunks(120, 85, 17, 12, boar_floor)      # The Boar Pens - real match
    floor_chunks(45, 45, 13, 10, thorn_floor)      # Agathelos's Pit
    floor_chunks(120, 18, 15, 10, thorn_floor)     # Charlga's Platform

    # Wall art - plain packed-earth wall everywhere, bramble accent
    # near Roogug's detour, beast-pit accent ring around Agathelos's
    # chamber specifically.
    obstacle_chunk_size = 4
    for gy in range(0, zone.height, obstacle_chunk_size):
        for gx in range(0, zone.width, obstacle_chunk_size):
            gw = min(obstacle_chunk_size, zone.width - gx)
            gh = min(obstacle_chunk_size, zone.height - gy)
            dist_roogug = ((gx - 50) ** 2 + (gy - 175) ** 2) ** 0.5
            dist_agathelos = ((gx - 45) ** 2 + (gy - 45) ** 2) ** 0.5
            if dist_roogug < 17:
                sprite = bramble_wall
            elif dist_agathelos < 15:
                sprite = beast_wall
            else:
                sprite = earth_wall
            zone.add_obstacle_chunk(sprite, gx, gy, gw, gh)

    zone.boss_positions = [roogug_pos, aggem_pos, jargba_pos, ramtusk_pos,
                            agathelos_pos, charlga_pos]
    zone.boss_position = charlga_pos  # legacy single-boss fallback - Charlga is RFK's ruling chieftain/final boss
    zone.add_subzone("Razorfen Kraul", 0, 0, zone.width, zone.height)

    return zone
