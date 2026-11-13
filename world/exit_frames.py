"""Every way out of a map is framed by something that looks like a way out.

Kyle, 10 Nov 2026: entrance art is MISSING for most exits. Measured 12 Nov: 183 of them were a
glowing tile in open ground - 95 road links, 66 ways out of a cave seen from inside, 22 doors
into the newer dungeons. The hand-built zones each place their own cave mouths, and that is the
reason so many were bare: a link added to world/portal_manager.py later had nobody to draw it.

So this is a PASS OVER THE FINISHED WORLD, like world/portal_art.clear_exits and for the same
reason - a rule taught to one generator is forgotten by the next. It runs once, after every map
exists, finds each (map -> destination) link with no entrance art on it, picks the piece that
belongs there and stands it over the portal tile with the tile in its opening.

WHAT IT WILL NOT DO:
  * touch a link that already has entrance art - hand placement always wins;
  * block anything. A frame is drawn, not solid: these go onto finished maps with roads, NPCs
    and arrival tiles already where they are, and a gatepost that seals a road is a worse bug
    than a gatepost you can clip the corner of;
  * cover another door, or another frame.

Which piece goes where is the three tables below. They are data, on purpose: when a sheet of
better art arrives, a line changes here and nothing else does.
"""
import os
import re

from world.npc_clearance import covered
from world.portal_art import is_entrance_art

ART = "assets/tiles/cave_entrances/"

#: THE WAY OUT of a dungeon, by which dungeon. First match wins; each entry may list several
#: looks, and a dungeon with more than one exit takes them in turn.
OUT_OF = [
    (r"Crypt|Barrow|Shadowpine Altar", ["ent_exit_crypt_stairs", "ent_exit_crypt_stairs_b"]),
    (r"Night Web|Widow|Broodspiral", ["ent_exit_spider_web", "ent_exit_spider_web_b"]),
    (r"Zalazane|Drowned Shrine|Gurbashi|Gurubashi|Sunken Temple", ["ent_exit_troll_temple_b", "ent_exit_troll_temple"]),
    (r"Ragefire|Emberdeep|Burning Blade", ["ent_exit_lava_fissure_b", "ent_exit_lava_fissure"]),
    (r"Boulderfist|Boulder'gor", ["ent_exit_ogre_hall_b", "ent_exit_ogre_hall"]),
    (r"Drywhisker", ["ent_exit_kobold_tunnel_b", "ent_exit_kobold_tunnel"]),
    (r"Khaz Varun|Dun Garok", ["ent_exit_dwarven_vault_b", "ent_exit_dwarven_vault"]),
    (r"Stromgarde|Durnholde|Shadowfang|Wrackline", ["ent_exit_keep_gate_b", "ent_exit_keep_gate"]),
    (r"Ambermill", ["ent_exit_tower_door_b", "ent_exit_tower_door"]),
    (r"Moonwell|Grom's Rest|Rotvine|Veilfall", ["ent_exit_root_hollow_b", "ent_exit_root_hollow"]),
    (r"Plague|Scourge", ["ent_exit_sewer_grate_b", "ent_exit_sewer_grate"]),
    (r"Undercrust|Drowning Floor", ["ent_exit_salt_shaft_b", "ent_exit_salt_shaft"]),
    (r"Razorfen", ["ent_exit_bramble_b", "ent_exit_bramble"]),
    (r"Tidewrack|Lashings", ["ent_exit_wreck_hull_b", "ent_exit_wreck_hull"]),
    (r"Drownbell", ["ent_exit_bell_window_b", "ent_exit_bell_window"]),
    (r"Skull Rock|Thunder Ridge|Dustwind|Drygulch", ["ent_exit_slot_canyon_b", "ent_exit_slot_canyon"]),
    (r"Wailing|Serena", ["ent_exit_fern_cavern_b", "ent_exit_fern_cavern"]),
    (r"Blackfathom|Sunken Grotto", ["ent_exit_coral_arch_b", "ent_exit_coral_arch"]),
    (r"Weeping Ice|Frostward", ["ent_exit_ice_tunnel"]),
    (r"Hollow Geode|Deep Bloom|Cistern", ["ent_exit_crystal"]),
    (r"Mine|Mother Vein|Lode", ["ent_exit_mine_adit"]),
    (r"Raider's Hold|Galleon's Hold|Captain's Cabin", ["ent_exit_ship_hatch"]),
    (r"Bloodsail Raider|Weather Deck", ["ent_exit_gangplank"]),
    (r"Rocky Pass", ["ent_exit_cave_daylight"]),
    (r"", ["ent_exit_cave_daylight", "ent_exit_stone_stairs"]),
]

#: THE WAY IN, by which dungeon it leads to.
INTO = [
    (r"Boulderfist|Boulder'gor", ["ent_ogre_mound"]),
    (r"Drywhisker", ["ent_kobold_dig"]),
    (r"Tidewrack|Lashings", ["ent_shipwreck_hull"]),
    (r"Khaz Varun|Dun Garok", ["ent_dwarven_vault"]),
    (r"Undercrust|Drowning Floor", ["ent_salt_sinkhole"]),
    (r"Drownbell", ["ent_sunken_belltower"]),
    (r"Drowned Barrow", ["ent_burial_barrow"]),
    (r"Wrackline|Durnholde|Stromgarde", ["ent_castle_portcullis"]),
    (r"Frostward", ["ent_door_ice_steps"]),
    (r"Weeping Ice", ["ent_door_ice_steps_b"]),
    (r"Hollow Geode", ["ent_door_crystal_rift"]),
    (r"Deep Bloom", ["ent_door_crystal_rift_b"]),
    (r"Mother Vein", ["ent_door_bronze_pipe"]),
    (r"Cistern", ["ent_door_bronze_pipe_b"]),
    (r"Mine|Lode", ["ent_collapsed_mine"]),
    (r"Rocky Pass", ["ent_cliff_road_tunnel"]),
    (r"Captain's Cabin", ["ent_door_ship_cabin", "ent_door_ship_cabin_b"]),
    (r"Hold$", ["ent_door_ship_hatch_down", "ent_door_ship_hatch_down_b"]),
    (r"Bloodsail Raider|Weather Deck", ["ent_exit_gangplank"]),
    (r"", ["ent_door_stairs_down", "ent_door_stairs_down_b"]),
]

#: A TOWN'S OWN GATE - used on the road into it and on the road out of it.
TOWN = [
    (r"Taurajo|Freewind", ["ent_town_tauren_totems"]),
    (r"Astranaar", ["ent_town_nightelf_bridge"]),
    (r"Zoram", ["ent_moonlit_arch"]),
    (r"Tarren Mill", ["ent_town_forsaken_gate"]),
    (r"Sepulcher|Deathknell|Brill", ["ent_gate_lychgate"]),     # stone and iron, like the town
    (r"Echo Isles", ["ent_town_troll_gate"]),
    (r"Saltwheel", ["ent_town_wheel_arch"]),
    (r"Kael's Bastion", ["ent_town_highelf_gate"]),
    (r"Glittervein", ["ent_town_headframe_gate"]),
    (r"Cinderwharf", ["ent_town_charred_gate"]),
    (r"Saltspur", ["ent_town_whalerib_gate"]),
    (r"Booty Bay|Anchorage", ["ent_town_pirate_gate"]),
    (r"Steamwheedle|Ratchet", ["ent_gate_goblin_port"]),
    (r"Crossroads|Razor Hill|Splintertree|Hammerfall|Grom'gol", ["ent_orc_palisade_gate"]),
    (r"Orgrimmar", ["entrance_orgrimmar_gate"]),
]

#: A ROAD between two open zones, by the country it runs through. Several looks per region so
#: a zone with four roads out does not have the same arch four times.
REGION = [
    (r"Barrens|Durotar|Valley of Trials|Crossroads|Razor Hill|Taurajo",
     ["ent_gate_kodo_tusks", "ent_gate_tusk_banners"]),
    (r"Tirisfal|Silverpine|Fenris|Deathknell|Sepulcher|Undercity|Brill",
     ["ent_gate_lychgate", "ent_gate_stone_pillars"]),
    (r"Hillsbrad|Tarren", ["ent_gate_tollgate", "ent_gate_logs"]),
    (r"Arathi|Hammerfall", ["ent_gate_standing_stones", "ent_gate_wall_breach"]),
    (r"Tanaris|Abyssal|Steamwheedle", ["ent_gate_sand_pylons", "ent_gate_sandstone"]),
    (r"Shimmering|Saltwheel", ["ent_gate_sandstone", "ent_town_wheel_arch"]),
    (r"Thousand Needles|Freewind", ["ent_gate_rope_bridge", "ent_gate_tusk_banners"]),
    (r"Aspen|Rocky Pass", ["ent_gate_snow_logs", "ent_gate_snowpine", "ent_gate_pass_cairns"]),
    (r"Tempest|Ashen Reach|Saltspur|Cinderwharf", ["ent_gate_basalt_storm", "ent_town_whalerib_gate"]),
    (r"Stranglethorn|Grom'gol|Booty Bay|Echo Isles", ["ent_gate_bamboo", "ent_town_troll_gate"]),
    (r"Ashenvale|Astranaar|Zoram|Splintertree", ["ent_moonlit_arch", "ent_elven_ruin_arch"]),
    (r"Underdark|Kael", ["ent_gate_crystal_arch"]),
    (r"Glittervein", ["ent_town_headframe_gate"]),
    (r"", ["ent_gate_logs", "ent_gate_stone_pillars"]),
]

#: A BOAT LANDING, by whose water it is.
DOCK = [
    (r"Echo Isles|Stranglethorn|Grom'gol", ["ent_dock_troll"]),
    (r"Booty Bay|Ratchet|Steamwheedle|Saltwheel", ["ent_dock_goblin"]),
    (r"Silverpine|Fenris|Tirisfal", ["ent_dock_forsaken"]),
    (r"Ashenvale|Zoram", ["ent_dock_nightelf"]),
    (r"Tempest|Saltspur|Arathi|Ashen|Cinderwharf", ["ent_dock_slipway"]),
    (r"", ["ent_dock_pier"]),
]

#: Footprints tried, biggest first: (width, height) in tiles. The art is about 220px and a tile
#: is 32, so 7x6 is the art at its native size; the smaller ones are for tight corners.
SIZES_OPEN = [(7, 6), (5, 5), (3, 3)]
SIZES_CAVE = [(5, 5), (3, 3)]

#: A prop this small (in tiles) standing where a frame goes is scatter - a bush, a rock, a
#: stalagmite - and gives way. Anything bigger is a building or a set piece and the frame
#: shrinks or goes on top instead.
SCATTER_AREA = 16


def _first(table, name):
    for pattern, looks in table:
        if re.search(pattern, name):
            return looks
    return table[-1][1]


def choose(src, dest, src_cave, dest_cave, boat, src_town, dest_town, src_region, turn=0,
           going_up=False):
    """The sprite (no folder, no extension) for the link src -> dest.

    going_up: a link between two dungeon maps that leads back TOWARD the surface (hold to
    deck). It is a way out and is drawn as one, not as a door leading deeper.
    """
    if src_cave and (not dest_cave or going_up):
        looks = _first(OUT_OF, src)
    elif dest_cave:
        looks = _first(INTO, dest)
    elif boat or "The Crossing" in (src, dest):
        looks = _first(DOCK, f"{src} {src_region}")
    elif dest_town and any(re.search(p, dest) for p, _l in TOWN):
        looks = _first(TOWN, dest)
    elif src_town and any(re.search(p, src) for p, _l in TOWN):
        looks = _first(TOWN, src)
    else:
        looks = _first(REGION, f"{src} {src_region}")
    return looks[turn % len(looks)]


def _rect_hits(ax, ay, w, h, lm):
    return not (ax + w <= lm["anchor_x"] or lm["anchor_x"] + lm["width_tiles"] <= ax
                or ay + h <= lm["anchor_y"] or lm["anchor_y"] + lm["height_tiles"] <= ay)


def _rooted_in(lm, ax, ay, w, h):
    """True if the prop's FOOT - the bottom-centre tile it grows or stands from - is inside the
    frame. A tree rooted three tiles away whose canopy reaches over is not in the way."""
    fx = lm["anchor_x"] + lm["width_tiles"] // 2
    fy = lm["anchor_y"] + lm["height_tiles"] - 1
    return ax <= fx < ax + w and ay <= fy < ay + h


def _gives_way(lm, ax, ay, w, h):
    """A prop the frame may replace: scatter of any kind, or a tree/rock of any size that is
    rooted where the gate goes. Never a building."""
    if "assets/buildings" in str(lm["sprite_key"]):
        return False
    if lm["width_tiles"] * lm["height_tiles"] <= SCATTER_AREA:
        return True
    return _rooted_in(lm, ax, ay, w, h) and "/props/" in str(lm["sprite_key"])


def _is_a_gate(sprite_key):
    """Entrance art, or anything a zone's own builder placed AS a gate. A hand-built town
    names its gate for what it is (br_kodo_tusk_gate, palisade_gatehouse, stv_liana_arch)
    rather than with the ent_ prefix, and this pass then stood a second gate on top of it -
    Camp Taurajo's north road had a tusk gate with a totem gate drawn through it."""
    name = os.path.basename(str(sprite_key)).lower()
    return is_entrance_art(sprite_key) or any(word in name for word in ("_gate", "gatehouse", "_arch"))


def _framed(tilemap, tiles):
    for lm in getattr(tilemap, "landmarks", []) or []:
        if not _is_a_gate(lm["sprite_key"]):
            continue
        for (x, y) in tiles:
            if (lm["anchor_x"] - 1 <= x <= lm["anchor_x"] + lm["width_tiles"]
                    and lm["anchor_y"] - 1 <= y <= lm["anchor_y"] + lm["height_tiles"]):
                return True
    return False


def _place(tilemap, tiles, others, sprite, sizes):
    """Stand `sprite` over the middle tile of `tiles`. Returns the landmark dict or None."""
    tiles = sorted(tiles)
    x, y = tiles[len(tiles) // 2]
    landmarks = tilemap.landmarks
    chosen = None
    for (w, h) in sizes:
        ax = min(max(0, x - w // 2), max(0, tilemap.width - w))
        ay = min(max(0, y - (h - 1)), max(0, tilemap.height - h))
        if any(ax <= ox < ax + w and ay <= oy < ay + h for (ox, oy) in others):
            continue                                   # would sit on somebody else's door
        probe = {"sprite_key": f"{ART}{sprite}.png", "anchor_x": ax, "anchor_y": ay,
                 "width_tiles": w, "height_tiles": h}
        if any(tilemap.interaction_layer[ty][tx] == "npc" and covered(probe, tx, ty) > 0.5
               for ty in range(max(0, ay), min(tilemap.height, ay + h))
               for tx in range(max(0, ax), min(tilemap.width, ax + w))):
            continue                                   # the art would be drawn over somebody
        hits = [lm for lm in landmarks if _rect_hits(ax, ay, w, h, lm)]
        if any(is_entrance_art(lm["sprite_key"]) for lm in hits):
            continue                                   # would overlap another frame
        big = [lm for lm in hits if not _gives_way(lm, ax, ay, w, h)]
        rooted = [lm for lm in big if _rooted_in(lm, ax, ay, w, h)]
        if rooted and (w, h) != sizes[-1]:
            continue                                   # a building stands here: try smaller
        chosen = (ax, ay, w, h, [lm for lm in hits if lm not in big])
        break
    if chosen is None:
        return None
    ax, ay, w, h, scatter = chosen
    for lm in scatter:                                 # bushes and rocks give way
        landmarks.remove(lm)
        for ty in range(lm["anchor_y"], lm["anchor_y"] + lm["height_tiles"]):
            for tx in range(lm["anchor_x"], lm["anchor_x"] + lm["width_tiles"]):
                if not (0 <= tx < tilemap.width and 0 <= ty < tilemap.height):
                    continue
                if tilemap.collision_layer[ty][tx] == "landmark" and not any(
                        _rect_hits(tx, ty, 1, 1, k) for k in landmarks):
                    tilemap.collision_layer[ty][tx] = None
    tilemap.add_landmark(f"{ART}{sprite}.png", ax, ay, w, h, solid=False)
    landmarks[-1]["exit_frame"] = True
    # Inside a dungeon the art is a piece of the room - its timber should be the room's
    # timber. Out of doors a gate is its own object and keeps its own colours.
    landmarks[-1]["match_ground"] = bool(getattr(tilemap, "is_cave", False))
    return landmarks[-1]


def frame_exits(zones, portal_manager, cave_names):
    """Frame every bare exit on every map. `zones` is {name: tilemap}. Returns
    {"placed": n, "skipped": [(src, dest, why), ...]}."""
    placed, skipped = 0, []
    by_src = {}
    for (src, x, y), dest in portal_manager._lookup.items():
        by_src.setdefault(src, {}).setdefault(dest[0], []).append((x, y))

    # A dungeon map you can walk into from the open world is the dungeon's top level.
    surface = {dest for src, dests in by_src.items() if src not in cave_names for dest in dests}

    for src in sorted(by_src):
        tilemap = zones.get(src)
        if tilemap is None or not hasattr(tilemap, "landmarks"):
            continue
        src_cave = src in cave_names
        src_region = getattr(tilemap, "region", "") or ""
        all_tiles = {t for tiles in by_src[src].values() for t in tiles}
        turn = {}
        for dest in sorted(by_src[src]):
            tiles = by_src[src][dest]
            if _framed(tilemap, tiles):
                continue
            dest_map = zones.get(dest)
            boat = any(tilemap.get_interaction(x, y) == "boat" for (x, y) in tiles)
            sprite = None
            for attempt in range(3):
                look_key = (src_cave, dest in cave_names)
                sprite = choose(src, dest, src_cave, dest in cave_names, boat,
                                getattr(tilemap, "is_town", False),
                                getattr(dest_map, "is_town", False), src_region,
                                turn.get(look_key, 0),
                                going_up=(src_cave and dest in cave_names
                                          and dest in surface and src not in surface))
                turn[look_key] = turn.get(look_key, 0) + 1
                if os.path.exists(f"{ART}{sprite}.png"):
                    break
                sprite = None
            if sprite is None:
                skipped.append((src, dest, "no art on disk for any look"))
                continue
            sizes = SIZES_CAVE if src_cave else SIZES_OPEN
            got = _place(tilemap, tiles, all_tiles - set(tiles), sprite, sizes)
            if got is None and not src_cave and dest not in cave_names:
                # The piece that belongs here does not fit - usually a guard standing where a
                # gatepost would go. A plainer gate from the same country often does.
                for other in _first(REGION, f"{src} {src_region}"):
                    if other != sprite and os.path.exists(f"{ART}{other}.png"):
                        got = _place(tilemap, tiles, all_tiles - set(tiles), other, sizes)
                        if got is not None:
                            break
            if got is None:
                skipped.append((src, dest, "no room without covering another door, frame or NPC"))
            else:
                placed += 1
    return {"placed": placed, "skipped": skipped}
