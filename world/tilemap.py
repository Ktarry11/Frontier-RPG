"""
Tilemap system. Handles zone tilemaps with 4 layers (base, visual, collision, interaction).
"""
from world.tiles import get_tile, is_walkable


class Tilemap:
    """A tilemap for a zone with 4 layers."""
    
    def __init__(self, name, width, height, description=""):
        self.name = name
        self.width = width
        self.height = height
        self.description = description
        
        # 4 layers: base, visual, collision, interaction
        self.base_layer = [[None for _ in range(width)] for _ in range(height)]
        self.visual_layer = [[None for _ in range(width)] for _ in range(height)]
        self.collision_layer = [[None for _ in range(width)] for _ in range(height)]
        self.interaction_layer = [[None for _ in range(width)] for _ in range(height)]

        # Named subzone regions within this map.
        # Until now "subzones" existed ONLY as encounter-table keys in
        # encounters.json - there was no way to be standing IN one, so
        # ZoneManager always reported location_type="open_zone" and the
        # subzone/cave XP multipliers (built and tested long ago) were
        # permanently inert. Each entry is a rect + the encounter-table key.
        self.subzones = []  # list of dicts: {name, table_key, x, y, w, h}

        # Large decorative objects that span MULTIPLE tiles as one image
        # (cave-mouth entrance art, landmark statues, etc.) instead of
        # being forced through the per-tile 32x32 texture pipeline every
        # other prop uses. Kyle confirmed entrances (and zone transitions
        # generally) are allowed to be genuinely bigger than 1 tile - so
        # this is real multi-tile terrain, not a decorative overlay hack:
        # the footprint gets real collision, and the portal/interaction
        # trigger is just a normal tile placed somewhere inside it (usually
        # the dark "mouth" opening). Each entry: {sprite_key, anchor_x,
        # anchor_y, width_tiles, height_tiles} - anchor is the top-left
        # tile coordinate, sizes are in TILES not pixels so the renderer
        # can scale the source image to exactly cover that many tiles.
        self.landmarks = []

        # Large GROUND textures spanning multiple tiles as one image -
        # the walkable-floor BASELINE layer. Kyle: "we need to have the
        # second tile layer... third layer on top of that as roads and
        # water" - this is layer 2 of that 3-layer model (1: collision/
        # pass-block, 2: baseline ground chunks, 3: roads/water
        # override). Built as the real fix for tiles reading "nauseating"
        # /diagonally-banded once actually rendered - the root cause was
        # source ground art being cropped to tiny rects and stamped per-
        # 32px-tile, throwing away most of each texture's real detail.
        #
        # This used to be a single self.ground_chunks list carrying a
        # "kind" tag ("ground" vs "water"), disambiguated per-tile by
        # matching kind against base_tile at render time. That broke
        # for real: a water chunk's RECTANGLE doesn't match the pond's
        # actual round shape, so nearby sand tiles inside that rectangle
        # got no ground chunk at all (their _chunk_lookup slot was
        # occupied by the wrong-kind water chunk with no fallback).
        # Fully separated into 3 independent structures instead - no
        # kind-matching, no shared lookup, no ambiguity by construction:
        #   ground_chunks / _ground_chunk_lookup - layer 2, baseline
        #   water_chunks / _water_chunk_lookup - layer 3a, water only
        #   road_segments - layer 3b, linear paths (see add_road_segment)
        # Each entry: {sprite_key, anchor_x, anchor_y, width_tiles,
        # height_tiles}. anchor is top-left tile coordinate, sizes in
        # TILES so the renderer scales the source image to cover exactly
        # that many tiles, matching the landmarks convention.
        self.ground_chunks = []
        self._ground_chunk_lookup = {}  # (x,y) -> chunk dict

        # Layer 3a: water override chunks. Only ever checked against
        # tiles whose base_layer tile_id is actually shallow_water/
        # deep_water (see get_water_chunk_at) - a water chunk registered
        # over a rectangle that happens to include some dry sand tiles
        # (rendering art is rectangular even when the pond is round)
        # simply never gets consulted for those sand tiles, which fall
        # through to ground_chunks normally. No kind-tag, no ambiguity -
        # this list ONLY ever contains water chunks.
        self.water_chunks = []
        self._water_chunk_lookup = {}  # (x,y) -> chunk dict

        # Layer 3b: road segments - linear paths, not rectangular fills.
        # See add_road_segment for the real shape (a start/end tile pair
        # + width, not an anchor+w+h rectangle like the other two layers)
        # and how horizontal vs vertical auto-rotation works.
        self.road_segments = []

        # Obstacle chunks - large IMPASSABLE terrain art (mountains/
        # cliffs) spanning multiple tiles, same rectangle-plus-per-tile-
        # clip technique as water_chunks. Kyle: "mountain tiles should
        # also be in the third layer with water and roads... since
        # they're still read as movement=false, right?" - confirmed
        # ("cliff"/"wall" are both walkable=False, collision layer, per
        # tiles.py) and real, but NOT literally merged into water_chunks/
        # road_segments: those two replace/overlay WALKABLE ground: this
        # replaces the visual for IMPASSABLE collision tiles instead -
        # different axis (base layer vs collision layer), so it gets its
        # own list rather than forcing a genuinely different kind of
        # thing into the ground-override layer's shape. Clipped the same
        # way water_chunks is (get_obstacle_chunk_at is only ever
        # consulted for tiles whose collision_layer tile_id is actually
        # "cliff"/"wall") so a mountain chunk's rectangle can't paint
        # over real walkable ground the way the unclipped water chunk
        # briefly did before that bug was caught and fixed this session.
        self.obstacle_chunks = []
        self._obstacle_chunk_lookup = {}  # (x,y) -> chunk dict

        # Where this map sits relative to the world, purely for the map
        # screen's "you are here" labelling. Optional.
        self.region = ""

        # True only for cave maps. Previously ZoneManager inferred "is a cave"
        # from whether .region named another map - but town hubs legitimately
        # name their parent zone too, so Ratchet, Orgrimmar and the zeppelin
        # tower were all being treated as caves (fixed spawns, cave XP bonus,
        # cave encounter lookups). An explicit flag removes the ambiguity.
        self.is_cave = False

        # Within is_cave zones, this further distinguishes DUNGEONS from
        # small "cave-like" pockets (Kyle's split): dungeons/mini-dungeons
        # get fully fixed trash + boss placement (no respawns until you
        # leave and re-enter, matching a real WoW instance). Cave-like
        # zones (Skull Rock, Dustwind Cave, ...) instead roll random trash
        # per-tile like the open world, but still pin exactly one mini-
        # boss chamber via boss_position/boss_positions - random trash,
        # fixed boss, per Kyle's rule. True is the existing/default
        # behaviour so every generator written before this split (all of
        # them, as of this flag's introduction) keeps working unchanged;
        # new cave-like generators must set this to False explicitly.
        self.fixed_spawns = True

    def add_landmark(self, sprite_key, anchor_x, anchor_y, width_tiles, height_tiles,
                     mouth_offset=None, solid=True, rotation=0):
        """Place a multi-tile decorative structure (cave-mouth entrance
        art, statues, etc.) spanning width_tiles x height_tiles starting
        at (anchor_x, anchor_y), top-left. Real terrain, not a visual-only
        overlay: by default every tile in the footprint gets a "landmark"
        collision blocker EXCEPT the mouth tile (if given), which stays
        walkable so a portal/interaction tile can sit there.

        mouth_offset: (dx, dy) relative to anchor - the walkable opening
        tile, usually bottom-center of the structure. Pass None for a
        purely decorative landmark with no walkable interior (e.g. a
        statue with no interaction).

        rotation: degrees to rotate the source art before scaling into
        the footprint (0/90/180/270). Landmarks (unlike add_road_segment)
        have no auto-orientation - the source art's own baked-in direction
        may not match the footprint it's being stamped into (e.g. a
        horizontally-drawn bridge sprite placed over a north-south water
        crossing). Real bug found + fixed this way (Kyle: "the bridges in
        echo isles are turned the wrong way") - all 3 Echo Isles bridge
        sprites are natively wide/horizontal art (checked directly:
        aspect ratios 5.22/3.0/4.71), but the Troll Camp<->Hollow Isle
        crossing runs NORTH-SOUTH (dx=2, dy=24), so that one bridge needed
        rotation=90 while the other two (genuinely east-west crossings)
        don't.
        """
        self.landmarks.append({
            "sprite_key": sprite_key,
            "anchor_x": anchor_x, "anchor_y": anchor_y,
            "width_tiles": width_tiles, "height_tiles": height_tiles,
            "rotation": rotation,
        })
        if solid:
            for dy in range(height_tiles):
                for dx in range(width_tiles):
                    if mouth_offset and (dx, dy) == mouth_offset:
                        continue
                    x, y = anchor_x + dx, anchor_y + dy
                    if 0 <= x < self.width and 0 <= y < self.height:
                        self.collision_layer[y][x] = "landmark"

    def add_ground_chunk(self, sprite_key, anchor_x, anchor_y, width_tiles, height_tiles):
        """Register a large BASELINE ground texture (layer 2) covering
        width_tiles x height_tiles starting at (anchor_x, anchor_y),
        top-left. Does not touch any per-tile layer; collision/visual/
        interaction for tiles in this footprint are set exactly as
        normal via set_tile, independent of this call.

        This list only ever contains ground chunks - use add_water_chunk
        for water and add_road_segment for paths, which are checked
        independently by the renderer (layer 3, always wins over this
        layer where they apply). See the ground_chunks attribute comment
        in __init__ for why this used to be one shared list with a
        "kind" tag, and why that broke.
        """
        chunk = {
            "sprite_key": sprite_key,
            "anchor_x": anchor_x, "anchor_y": anchor_y,
            "width_tiles": width_tiles, "height_tiles": height_tiles,
        }
        self.ground_chunks.append(chunk)
        for dy in range(height_tiles):
            for dx in range(width_tiles):
                x, y = anchor_x + dx, anchor_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self._ground_chunk_lookup[(x, y)] = chunk

    def get_ground_chunk_at(self, x, y):
        """Return the ground chunk covering this tile, or None."""
        return self._ground_chunk_lookup.get((x, y))

    def add_water_chunk(self, sprite_key, anchor_x, anchor_y, width_tiles, height_tiles):
        """Register a large WATER texture (layer 3a) covering
        width_tiles x height_tiles starting at (anchor_x, anchor_y),
        top-left. Same rectangle-covers-an-area shape as add_ground_chunk,
        but tracked in a completely separate list/lookup - the renderer
        (get_water_chunk_at) only ever consults this for a tile whose
        base_layer is actually shallow_water/deep_water, so a water
        chunk's rectangle can safely overlap dry ground at its corners
        (a round pond's bounding box always includes some dry corners)
        without stealing those tiles from the ground chunk underneath -
        they simply fall through to ground_chunks normally, since this
        lookup is never even checked for a non-water tile.
        """
        chunk = {
            "sprite_key": sprite_key,
            "anchor_x": anchor_x, "anchor_y": anchor_y,
            "width_tiles": width_tiles, "height_tiles": height_tiles,
        }
        self.water_chunks.append(chunk)
        for dy in range(height_tiles):
            for dx in range(width_tiles):
                x, y = anchor_x + dx, anchor_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self._water_chunk_lookup[(x, y)] = chunk

    def get_water_chunk_at(self, x, y):
        """Return the water chunk covering this tile, or None. Callers
        should only trust this for tiles whose base_layer tile_id is
        actually shallow_water/deep_water - see add_water_chunk."""
        return self._water_chunk_lookup.get((x, y))

    def add_road_segment(self, sprite_key, x0, y0, x1, y1, width_tiles=1):
        """Register a linear road/path (layer 3b) from (x0,y0) to
        (x1,y1) - a straight run, not a filled rectangle like the other
        two chunk types. Real WoW-style roads are line segments with a
        direction, and the source art this session's road textures use
        has a baked-in orientation (a worn strip running one way through
        the image, not a generic direction-agnostic ground material) -
        so a road needs to know which way it's running, not just what
        area it covers.

        width_tiles: how many tiles wide the visible road is (independent
        of the 1-tile-wide "path" tiles _paint_road already sets on the
        base layer for walkability/movement speed - this is purely the
        VISUAL width, matched loosely to that but not required to be
        identical).

        The renderer resolves horizontal vs vertical automatically from
        (x0,y0)-(x1,y1) and rotates the source sprite 90 degrees for
        whichever orientation the art doesn't already natively match -
        see ui/tilemap_renderer.py's road-drawing pass for exactly how
        "does the art already run this way" is decided.

        IMPORTANT: (x0,y0)-(x1,y1) should be purely horizontal OR purely
        vertical (one of dx/dy should be 0). A genuinely diagonal
        endpoint pair still "works" (the renderer interpolates a line
        between them) but looks like a jagged staircase once actually
        rendered - Kyle: "we don't need this weird angled shit, we can
        do straight lines, Ts and crossroads" after a real screenshot
        showed exactly that stair-step artifact on VoT's diagonal spur
        roads. Use add_road_path (below) for a diagonal-looking
        start/end pair - it auto-decomposes into two straight legs
        meeting at a right-angle bend instead of calling this directly
        with mismatched x/y.
        """
        self.road_segments.append({
            "sprite_key": sprite_key,
            "x0": x0, "y0": y0, "x1": x1, "y1": y1,
            "width_tiles": width_tiles,
        })

    def add_road_path(self, sprite_key, x0, y0, x1, y1, width_tiles=1, bend="auto"):
        """Register a road from (x0,y0) to (x1,y1) as one or two STRAIGHT
        add_road_segment legs, never a raw diagonal - see add_road_segment's
        docstring for why a diagonal endpoint pair looks wrong once
        rendered (a 1-tile-wide art strip stamped along a 45-degree-ish
        line is an inherent staircase, not a real diagonal road).

        If x0==x1 or y0==y1 already (a straight shot), this is just one
        segment, identical to calling add_road_segment directly. Otherwise
        it's an L-shaped bend: one horizontal leg + one vertical leg,
        meeting at a corner tile. bend picks which axis moves first:
          "auto" (default) - horizontal leg first if abs(dx) >= abs(dy),
                              vertical leg first otherwise
          "horizontal_first" - always go horizontal from (x0,y0), then
                                vertical to (x1,y1)
          "vertical_first" - always go vertical from (x0,y0), then
                              horizontal to (x1,y1)
        This is a real T/crossroad-friendly primitive: a road network
        built from add_road_path calls only ever has straight legs and
        right-angle corners, matching Kyle's "straight lines, Ts and
        crossroads" - never an angled cut across open ground.
        """
        if x0 == x1 or y0 == y1:
            self.add_road_segment(sprite_key, x0, y0, x1, y1, width_tiles)
            return
        go_horizontal_first = (
            abs(x1 - x0) >= abs(y1 - y0) if bend == "auto"
            else bend == "horizontal_first"
        )
        if go_horizontal_first:
            corner_x, corner_y = x1, y0
        else:
            corner_x, corner_y = x0, y1
        self.add_road_segment(sprite_key, x0, y0, corner_x, corner_y, width_tiles)
        self.add_road_segment(sprite_key, corner_x, corner_y, x1, y1, width_tiles)

    def add_obstacle_chunk(self, sprite_key, anchor_x, anchor_y, width_tiles, height_tiles):
        """Register a large IMPASSABLE terrain texture (mountain/cliff
        face) covering width_tiles x height_tiles starting at
        (anchor_x, anchor_y), top-left. Same rectangle-plus-per-tile-
        clip shape as add_water_chunk, but for the collision layer
        instead of the base layer - see the obstacle_chunks attribute
        comment in __init__ for why this isn't just folded into
        water_chunks/road_segments despite Kyle's "third layer" framing
        (different axis: this replaces impassable-collision-tile art,
        not walkable-ground art).

        Does not touch collision_layer itself - the actual "cliff"/
        "wall" tile_ids must still be set via set_tile as normal
        (_carve_irregular_boundary etc. already do this); this only
        controls how those tiles are VISUALLY drawn once they exist.
        """
        chunk = {
            "sprite_key": sprite_key,
            "anchor_x": anchor_x, "anchor_y": anchor_y,
            "width_tiles": width_tiles, "height_tiles": height_tiles,
        }
        self.obstacle_chunks.append(chunk)
        for dy in range(height_tiles):
            for dx in range(width_tiles):
                x, y = anchor_x + dx, anchor_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self._obstacle_chunk_lookup[(x, y)] = chunk

    def get_obstacle_chunk_at(self, x, y):
        """Return the obstacle chunk covering this tile, or None.
        Callers should only trust this for tiles whose collision_layer
        tile_id is actually "cliff"/"wall" - see add_obstacle_chunk."""
        return self._obstacle_chunk_lookup.get((x, y))

    def add_subzone(self, table_key, x, y, w, h, display_name=None):
        """Register a rectangular named region inside this map.

        table_key must match a key under this zone's "subzones" entry in
        data/creatures/encounters.json, otherwise the region will exist
        geographically but fall back to the open-zone encounter table.
        """
        self.subzones.append({
            "name": display_name or table_key,
            "table_key": table_key,
            "x": x, "y": y, "w": w, "h": h,
        })

    def get_subzone_at(self, x, y):
        """Return the subzone dict containing this tile, or None.

        Later-registered subzones win on overlap, so a small pocket declared
        after a large one takes precedence inside its bounds.
        """
        found = None
        for sz in self.subzones:
            if sz["x"] <= x < sz["x"] + sz["w"] and sz["y"] <= y < sz["y"] + sz["h"]:
                found = sz
        return found

    
    def set_tile(self, x, y, tile_id, layer="base"):
        """Set a tile at position on a specific layer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if layer == "base":
                self.base_layer[y][x] = tile_id
            elif layer == "visual":
                self.visual_layer[y][x] = tile_id
            elif layer == "collision":
                self.collision_layer[y][x] = tile_id
            elif layer == "interaction":
                self.interaction_layer[y][x] = tile_id
    
    def get_tile(self, x, y, layer="base"):
        """Get tile ID at position on a specific layer."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if layer == "base":
                return self.base_layer[y][x]
            elif layer == "visual":
                return self.visual_layer[y][x]
            elif layer == "collision":
                return self.collision_layer[y][x]
            elif layer == "interaction":
                return self.interaction_layer[y][x]
        return None
    
    def is_walkable(self, x, y):
        """Check if a position is walkable (no collision tile)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check collision layer first.
        # This previously returned `not is_walkable(collision_tile)`, which
        # inverted the result: "wall"/"tree"/"rock"/"cliff" are all flagged
        # walkable=False in tiles.py, so `not False` made every one of them
        # PASSABLE, while "bushes" (walkable=True) became a solid wall.
        # Every collision tile in the game did the opposite of its job.
        # A tile on the collision layer blocks unless its own flag says it
        # can be walked through (bushes = passable undergrowth).
        collision_tile = self.collision_layer[y][x]
        if collision_tile:
            return is_walkable(collision_tile)
        
        # Check base layer
        base_tile = self.base_layer[y][x]
        if base_tile:
            return is_walkable(base_tile)
        
        return False
    
    def get_interaction(self, x, y):
        """Get interaction at position (if any)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.interaction_layer[y][x]
        return None
    
    def fill(self, tile_id, layer="base"):
        """Fill entire layer with a tile."""
        for y in range(self.height):
            for x in range(self.width):
                self.set_tile(x, y, tile_id, layer)
    
    def to_dict(self):
        """Serialize tilemap to dictionary."""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "description": self.description,
            "base_layer": self.base_layer,
            "visual_layer": self.visual_layer,
            "collision_layer": self.collision_layer,
            "interaction_layer": self.interaction_layer,
            # Zones are regenerated fresh from their generator function on
            # load (see world/zone_manager.py), not reconstructed purely
            # from this dict in practice - these 3 are included for
            # completeness/future-proofing the same way landmarks already
            # was, rather than leaving a Tilemap attribute silently
            # unserialized.
            "ground_chunks": self.ground_chunks,
            "water_chunks": self.water_chunks,
            "road_segments": self.road_segments,
            "obstacle_chunks": self.obstacle_chunks,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize tilemap from dictionary."""
        tilemap = cls(data["name"], data["width"], data["height"], data.get("description", ""))
        tilemap.base_layer = data["base_layer"]
        tilemap.visual_layer = data["visual_layer"]
        tilemap.collision_layer = data["collision_layer"]
        tilemap.interaction_layer = data["interaction_layer"]
        # .get() default - old saves predate these and won't have the
        # keys; falling back to [] rather than KeyError keeps old saves
        # loading exactly as before (zones are regenerated from their
        # generator function anyway, so this mostly matters for forward-
        # compatibility, not real save-load correctness today).
        for chunk in data.get("ground_chunks", []):
            tilemap.add_ground_chunk(chunk["sprite_key"], chunk["anchor_x"],
                                      chunk["anchor_y"], chunk["width_tiles"],
                                      chunk["height_tiles"])
        for chunk in data.get("water_chunks", []):
            tilemap.add_water_chunk(chunk["sprite_key"], chunk["anchor_x"],
                                     chunk["anchor_y"], chunk["width_tiles"],
                                     chunk["height_tiles"])
        for seg in data.get("road_segments", []):
            tilemap.add_road_segment(seg["sprite_key"], seg["x0"], seg["y0"],
                                      seg["x1"], seg["y1"],
                                      seg.get("width_tiles", 1))
        for chunk in data.get("obstacle_chunks", []):
            tilemap.add_obstacle_chunk(chunk["sprite_key"], chunk["anchor_x"],
                                        chunk["anchor_y"], chunk["width_tiles"],
                                        chunk["height_tiles"])
        return tilemap
