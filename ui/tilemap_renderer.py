"""
Tilemap visualizer. Renders zones as textured grids (falling back to flat
colors where no texture is mapped) with camera follow.
"""
import os
import pygame
from world.tiles import get_tile_color
from world.tile_textures import TILE_SIZE, get_biome_for_zone, get_texture_entry, get_subzone_biome
from ui.sprite_loader import get_tile_sprite, get_tile_sprite_smooth, get_landmark_sprite, get_feathered_chunk_sprite, get_npc_sprite, get_mount_sprite
from world.race_registry import sprite_base_path
from world.chest_looks import chest_look, chest_sprite, is_boss_chest
from world.gathering_manager import MATERIAL_TYPE_FOLDERS
from boss_icons import get_boss_icon_path

class TilemapRenderer:
    """Renders tilemaps as textured (or flat-color fallback) grids with camera viewport."""

    def __init__(self, tile_size=TILE_SIZE):
        """Initialize renderer. tile_size = pixels per tile on screen.
        Defaults to world.tile_textures.TILE_SIZE (32) rather than a
        hardcoded literal, so the render scale has one source of truth -
        see tools/tile_mapping/NOTES.md "resolution decision" for why 32."""
        self.tile_size = tile_size
        # Character sprites (player/vendor/recruit/ambient NPC) render
        # larger than their footprint tile - the real Zelda/FF convention
        # Kyle asked for ("we look like ants"). This is now a HEIGHT
        # multiplier (get_npc_sprite's tile_height), not a width one -
        # source art sizes vary wildly across race packs (80x120 human,
        # 48x48 orc, 30x52 goblin), and anchoring by width let each
        # pack's own aspect ratio produce a wildly different on-screen
        # HEIGHT, which is what made the goblin pack render nearly 3
        # tiles tall while orc rendered under 2 (Kyle: "the goblin NPC
        # is fucking massive"). Anchoring by height instead means every
        # race stands the same height on screen - 1.6x was tuned by eye
        # off that fixed height, big enough to read as a real character,
        # not so big that two adjacent NPCs visually collide constantly.
        # 1.6x was the prior tuned baseline (see comment above - height-
        # anchored, big enough to read as a real character without
        # constant visual collision between adjacent NPCs). Kyle then
        # played it in-game and asked to "increase NPC and player size
        # by 1.5x if we can" - applied ON TOP of that baseline (1.6 * 1.5
        # = 2.4), not replacing it, since the ask came from looking at
        # the already-1.6x-scaled result and wanting it bigger still.
        self.npc_sprite_scale = 1.6 * 1.5
        # Per-tilemap biome cache so we don't recompute the zone->biome
        # lookup every single tile every single frame - keyed by the
        # tilemap object itself since a Tilemap's name/is_cave never
        # change after creation.
        self._biome_cache = {}
        # Boss portrait icons for the live overworld/cave view (not the
        # map screen, which has its own identical cache - see
        # ui/screens/map_screen.py's _get_boss_icon). Kept separate rather
        # than shared since the two screens are different Surface
        # consumers with different lifetimes; duplicating a small
        # in-memory image cache is cheap and avoids coupling them.
        self._boss_icon_cache = {}

    def _biome_for(self, tilemap, x=None, y=None):
        """Resolve the biome for a tile. Checks a per-tile subzone override
        first (e.g. Field of Giants inside The Barrens) when x/y are given,
        falling back to the whole-map zone biome otherwise - same as before
        this was subzone-aware. The whole-map biome is still cached since
        it never changes; subzone lookups are cheap per-tile rect checks
        and not worth caching on top of that."""
        biome = self._biome_cache.get(id(tilemap))
        if biome is None:
            biome = get_biome_for_zone(tilemap.name, is_cave=getattr(tilemap, "is_cave", False))
            self._biome_cache[id(tilemap)] = biome
        if x is not None and y is not None:
            override = get_subzone_biome(tilemap, x, y)
            if override:
                return override
        return biome

    #: Overworld/dungeon boss marker size in tiles (it was 1.3, which read as a trash mob).
    BOSS_ICON_TILES = 4.0

    def _get_boss_icon(self, template, size):
        """Loaded-and-scaled boss portrait Surface for a creature template,
        cached by (template, size). Returns None if the file can't be
        loaded so the caller can fall back to a plain marker instead of
        crashing the whole map render. Mirrors
        ui/screens/map_screen.py's _get_boss_icon exactly - see that
        method's docstring for the full reasoning; kept as a separate
        cache here rather than shared, see the cache's own comment in
        __init__."""
        cache_key = (template, size)
        if cache_key in self._boss_icon_cache:
            return self._boss_icon_cache[cache_key]
        try:
            path = get_boss_icon_path(template)
            raw = pygame.image.load(str(path)).convert_alpha()
            icon = pygame.transform.smoothscale(raw, (size, size))
        except (pygame.error, FileNotFoundError):
            icon = None
        self._boss_icon_cache[cache_key] = icon
        return icon

    def _get_sprite_for_tile(self, tilemap, tile_id, x=None, y=None):
        """Look up the textured sprite for a tile_id in this tilemap's
        biome. Returns None if unmapped/unavailable - caller falls back
        to the flat-color rect exactly as before."""
        if not tile_id:
            return None
        biome = self._biome_for(tilemap, x, y)
        # x, y forwarded so get_texture_entry can deterministically pick
        # a variant when a tile_id maps to a LIST of textures rather than
        # one fixed texture (Kyle: "I don't want one uniform tile across
        # the board") - same tile position always renders the same
        # variant, no per-frame flicker.
        entry = get_texture_entry(biome, tile_id, x, y)
        if not entry:
            return None
        sheet_path, rect, smooth = entry
        if smooth:
            return get_tile_sprite_smooth(sheet_path, rect, self.tile_size)
        return get_tile_sprite(sheet_path, rect, self.tile_size)

    def _draw_quest_indicator(self, screen, indicator, sprite_x, sprite_top_y):
        """Draw the gold/grey !/? marker above an NPC's head. indicator
        is one of "gold_exclaim"/"grey_exclaim"/"gold_question"/
        "grey_question"/"green_exclaim" (flight master)/None (see
        QuestManager.get_indicator_for_npc for what each means) - None draws nothing.

        sprite_x/sprite_top_y are the NPC sprite's actual on-screen
        top-left (not the tile's), so the marker sits centered above
        wherever that NPC's real head is, whether the sprite is 32px or
        61px tall - using the tile position instead would put the marker
        at an inconsistent height across different sprite sizes.
        """
        if not indicator:
            return
        is_gold = indicator.startswith("gold")
        glyph = "!" if indicator.endswith("exclaim") else "?"
        # "green_exclaim" = flight master (see OverworldScreen / travel_manager); gold/grey are quest markers.
        color = (80, 220, 100) if indicator.startswith("green") else ((255, 215, 0) if is_gold else (140, 140, 140))

        cx = sprite_x + self.tile_size // 2
        cy = sprite_top_y - 12
        pygame.draw.circle(screen, (20, 20, 20), (cx, cy), 9)
        pygame.draw.circle(screen, color, (cx, cy), 9, 2)
        font = pygame.font.Font(None, 20)
        text_surf = font.render(glyph, True, color)
        text_rect = text_surf.get_rect(center=(cx, cy))
        screen.blit(text_surf, text_rect)

    def _draw_chunk_layer(self, screen, camera, viewport_rect, chunks,
                           tile_left, tile_top, tile_right, tile_bottom, feather_px,
                           tilemap=None, only_base_tiles=None, only_collision_tiles=None):
        """Two-pass opaque+feathered draw for a list of chunk dicts
        (ground_chunks, water_chunks, or obstacle_chunks - same shape,
        same technique). Extracted from the original inline ground-chunk
        drawing code so water/obstacle chunks can reuse it exactly,
        rather than duplicating the two-pass logic. See render_tilemap's
        call site comment for why two passes (not one) are needed.

        only_base_tiles / only_collision_tiles: mutually exclusive
        clipping options - if given (a set of tile_ids), pass 1's opaque
        draw is CLIPPED per-tile to only tiles whose base_layer (or
        collision_layer) value is actually in that set. Real bug this
        fixes: a chunk's rectangle is always bigger than the true shape
        of what it represents (a round pond, an irregular mountain
        range) - an unclipped blit paints real water/mountain pixels
        onto tiles that were never actually water/mountain, and nothing
        downstream expected that leak (caught via a rendered screenshot:
        road art appearing to fail to yield to water, root-caused to the
        water chunk itself painting past its real tiles). Pass 2
        (feathered) is intentionally NOT clipped the same way - the
        feather's job is to soften into neighboring content past the
        chunk's exact edge, which is the desired look for an isolated
        pond/mountain range with no neighboring chunk of the same type
        to conflict with.
        """
        visible_chunks = []
        for chunk in chunks:
            cx0, cy0 = chunk["anchor_x"], chunk["anchor_y"]
            cx1, cy1 = cx0 + chunk["width_tiles"], cy0 + chunk["height_tiles"]
            if cx1 <= tile_left or cx0 >= tile_right or cy1 <= tile_top or cy0 >= tile_bottom:
                continue
            visible_chunks.append(chunk)

        clip_tiles = only_base_tiles or only_collision_tiles
        clip_layer = "base" if only_base_tiles else "collision"

        for chunk in visible_chunks:
            cx0, cy0 = chunk["anchor_x"], chunk["anchor_y"]
            screen_x, screen_y = camera.world_to_screen(cx0, cy0, self.tile_size)
            screen_x += viewport_rect.x
            screen_y += viewport_rect.y
            px_w = chunk["width_tiles"] * self.tile_size
            px_h = chunk["height_tiles"] * self.tile_size
            sprite = get_landmark_sprite(chunk["sprite_key"], px_w, px_h)
            if sprite is None:
                continue
            if clip_tiles is not None and tilemap is not None:
                # Clipped draw: one small blit per tile that actually
                # matches, instead of one big rectangle blit. More calls,
                # but only for a chunk's own footprint intersected with
                # the visible range - affordable for a single pond or
                # mountain range, would need revisiting for a much
                # bigger clipped feature later.
                cw_tiles, ch_tiles = chunk["width_tiles"], chunk["height_tiles"]
                for ty in range(max(cy0, tile_top), min(cy0 + ch_tiles, tile_bottom)):
                    for tx in range(max(cx0, tile_left), min(cx0 + cw_tiles, tile_right)):
                        if tilemap.get_tile(tx, ty, clip_layer) not in clip_tiles:
                            continue
                        tscreen_x, tscreen_y = camera.world_to_screen(tx, ty, self.tile_size)
                        tscreen_x += viewport_rect.x
                        tscreen_y += viewport_rect.y
                        src_x = (tx - cx0) * self.tile_size
                        src_y = (ty - cy0) * self.tile_size
                        screen.blit(sprite, (tscreen_x, tscreen_y),
                                    area=pygame.Rect(src_x, src_y, self.tile_size, self.tile_size))
            else:
                screen.blit(sprite, (screen_x, screen_y))

        for chunk in visible_chunks:
            # Real bug found & fixed here: this feathered pass 2 used to
            # run UNCLIPPED for every chunk type, including water/
            # obstacle chunks - fine for ground_chunks (meant to blend
            # into a neighboring chunk of similar ground), but wrong for
            # a single isolated water/mountain chunk, whose bounding
            # rectangle is always bigger than its real (round/organic)
            # shape. The unclipped redraw painted semi-transparent water
            # pixels over the dry sand/ground fringe inside that
            # rectangle - a real, confirmed checkerboard-looking bug
            # (verified: base_layer water tiles form a clean solid
            # circle with zero gaps, so the visible grid pattern in the
            # rendered pond was 100% a render-time artifact from this
            # unclipped pass, not carve-time data). Clipped chunks
            # (clip_tiles is not None) skip this pass entirely and rely
            # on pass 1's per-tile clipping alone - clean edges without
            # a blended fade are the correct look for an isolated
            # feature with no neighboring same-type chunk to blend into.
            if clip_tiles is not None:
                continue
            # "exact" chunks are one continuous painting (tools/terrain_painter.py):
            # already seamless, and the feather pass draws an OFFSET copy that would
            # misalign them against the exact water/obstacle blits.
            if chunk.get("exact"):
                continue
            cx0, cy0 = chunk["anchor_x"], chunk["anchor_y"]
            screen_x, screen_y = camera.world_to_screen(cx0, cy0, self.tile_size)
            screen_x += viewport_rect.x
            screen_y += viewport_rect.y
            px_w = chunk["width_tiles"] * self.tile_size
            px_h = chunk["height_tiles"] * self.tile_size
            feathered = get_feathered_chunk_sprite(chunk["sprite_key"], px_w, px_h,
                                                    feather_px=feather_px)
            if feathered is not None:
                screen.blit(feathered, (screen_x - feather_px, screen_y - feather_px))
            # No flat-color fallback here deliberately - a chunk with a
            # bad/missing sprite_key falls through to the per-tile base
            # loop drawing each covered tile's OWN base_layer value
            # normally, so a broken chunk degrades to the pre-chunk
            # rendering instead of a blank/black hole.

    def _draw_road_segments(self, screen, camera, viewport_rect, tilemap,
                             tile_left, tile_top, tile_right, tile_bottom):
        """Layer 3b: linear road/path overlays, drawn stamped per-tile
        along each segment's real line (not one big image stretched
        across a bounding rectangle - a road is a 1-to-a-few-tile-wide
        LINE, stretching the source art across its full length would
        smear/distort it).

        Each segment's source image tiles seamlessly (verified via the
        asset pipeline's 3x3 preview before being wired in) and has a
        baked-in orientation - Kyle asked directly whether horizontal
        vs vertical rotation would be handled: a segment's direction is
        computed from (x0,y0)-(x1,y1), and if the segment runs the
        opposite way from the source art's native orientation (roads_
        drawn as VERTICAL strips, per this session's source images),
        the crop is rotated 90 degrees before stamping. Diagonal
        segments are not specially handled (falls back to whichever
        axis has the larger delta) - no VoT road is currently diagonal.
        """
        for seg in getattr(tilemap, "road_segments", []):
            x0, y0, x1, y1 = seg["x0"], seg["y0"], seg["x1"], seg["y1"]
            width_tiles = seg.get("width_tiles", 1)
            dx, dy = x1 - x0, y1 - y0
            is_horizontal = abs(dx) > abs(dy)

            # Bounding box cull, same shape as the chunk visibility check.
            seg_left, seg_right = min(x0, x1) - width_tiles, max(x0, x1) + width_tiles
            seg_top, seg_bottom = min(y0, y1) - width_tiles, max(y0, y1) + width_tiles
            if seg_right < tile_left or seg_left > tile_right or seg_bottom < tile_top or seg_top > tile_bottom:
                continue

            base_sprite = get_landmark_sprite(seg["sprite_key"], self.tile_size, self.tile_size)
            if base_sprite is None:
                continue
            # Source art's worn strip runs VERTICALLY (confirmed against
            # this session's actual road images) - rotate 90 degrees for
            # a horizontal segment so the strip follows the road's real
            # direction instead of cutting across it.
            oriented_sprite = pygame.transform.rotate(base_sprite, 90) if is_horizontal else base_sprite

            steps = max(abs(dx), abs(dy))
            if steps == 0:
                tiles_on_path = [(x0, y0)]
            else:
                tiles_on_path = []
                for i in range(steps + 1):
                    t = i / steps
                    tiles_on_path.append((round(x0 + dx * t), round(y0 + dy * t)))

            half_w = width_tiles // 2
            for (tx, ty) in tiles_on_path:
                for w_off in range(-half_w, width_tiles - half_w):
                    px, py = (tx, ty + w_off) if is_horizontal else (tx + w_off, ty)
                    if not (tile_left <= px < tile_right and tile_top <= py < tile_bottom):
                        continue
                    # Kyle: "roads into the water? Water supersedes
                    # roads." A road segment's WIDTH padding can extend
                    # past its own endpoint into a pond's footprint even
                    # though the road's own tile data (base_layer=="path")
                    # never claims that tile - confirmed via direct
                    # inspection: VoT's north road segment genuinely ends
                    # at y=47 with base_layer=="path", y=48 is "sand", and
                    # the pond doesn't even start until much further in,
                    # yet road art was painting over water anyway purely
                    # because roads drew in a later pass than water,
                    # unconditionally. This checks the REAL tile under
                    # each individual road stamp and skips it if that
                    # tile is actually water, rather than relying on
                    # draw order to keep the two apart - water wins by
                    # construction now, not by which pass happens last.
                    if tilemap.get_tile(px, py, "base") in ("shallow_water", "deep_water"):
                        continue
                    screen_x, screen_y = camera.world_to_screen(px, py, self.tile_size)
                    screen_x += viewport_rect.x
                    screen_y += viewport_rect.y
                    screen.blit(oriented_sprite, (screen_x, screen_y))

    def render_tilemap(self, screen, tilemap, player_pos=None, camera=None, viewport_rect=None,
                        vendors=None, recruits=None, ambient_npcs=None, cave_spawns=None,
                        gathering_nodes=None,
                        player=None, player_facing="down", quest_indicators=None,
                        creature_manager=None):
        """Render tilemap using camera viewport.
        
        Args:
            screen: Pygame surface to render to
            tilemap: Tilemap object
            player_pos: (x, y) player tile coords
            camera: CameraManager object (handles coordinate conversion)
            viewport_rect: Pygame Rect for viewport bounds on screen
            vendors: List of VendorNPC objects to render (Phase 6)
            recruits: List of RecruitNPC objects to render (distinct npc_color)
            ambient_npcs: List of AmbientNPC objects to render - lightweight
                    flavor NPCs (guards, townsfolk) with no shop/recruit
                    behavior, see world/ambient_npc_manager.py.
            cave_spawns: List of (x, y, is_boss, creature_name) tuples from
                    CaveSpawnManager.active_positions() - previously caves
                    and dungeons never rendered their fixed monster spawns
                    at all, so bosses (and trash) were invisible until you
                    walked onto them blind. Bosses render as their real
                    portrait icon (see boss_icons.py) rather than a flat
                    marker, so a boss room reads on sight AND shows what's
                    actually in there - a flat red square with a white X
                    read as a broken/missing texture (Kyle, 2026-09-09:
                    "the Redbox with an X. that needs to be replaced with
                    the actual boss icon"), which is exactly what it looked
                    like even though it was intentional placeholder art,
                    not an error.
            gathering_nodes: List of GatheringNode objects from
                    GatheringNodeManager.active_nodes - herb/ore nodes.
                    Each renders its own hand-authored material icon (see
                    assets/gathering_nodes/) rather than a generic marker,
                    same "show what's actually there" reasoning as
                    cave_spawns above - a player should be able to tell a
                    Peacebloom patch from a Copper vein at a glance, not
                    just "something is gatherable here".
            player: The player Character, for race/gender/appearance_variant -
                    used to pick a real sprite (see world/race_registry.py).
                    Falls back to a flat white square if None or if sprite
                    resolution fails for any reason (missing file, bad
                    race/variant combo), same fail-soft convention every
                    other sprite lookup in this renderer already follows.
            player_facing: "down"/"up"/"left"/"right" - ZoneManager.player_facing,
                    the last direction the player moved (see move_player).
            quest_indicators: dict of npc_id -> one of "gold_exclaim"/
                    "grey_exclaim"/"gold_question"/"grey_question"/None,
                    from QuestManager.get_indicator_for_npc - drawn above
                    vendor/ambient NPCs that have an npc_id matching a key
                    here. None or a missing key draws nothing.
            creature_manager: CreatureManager, needed to resolve a boss's
                    creature_name into its template (see
                    world/creature_manager.py and boss_icons.py's
                    TEMPLATE_ICON) for icon lookup. None falls back to the
                    "_default" boss icon rather than crashing if this is
                    ever omitted by a caller.
        """
        if not camera or not viewport_rect:
            return
        
        # Get viewport bounds in world pixel coords
        cam_left, cam_top, cam_right, cam_bottom = camera.get_viewport_bounds()
        
        # Calculate tile ranges to render (only render what's visible).
        # +1/-1 buffer on ALL FOUR sides (not just right/bottom) - the
        # previous version only buffered tile_right/tile_bottom, leaving
        # tile_left/tile_top with zero margin. Kyle: "some graphic
        # glitches with the outer portion vanishing and reappearing" -
        # reproduced directly: when cam_left/cam_top aren't perfectly
        # tile-aligned (the normal case while walking, not just at rest),
        # int(cam_left/tile_size) truncates toward zero with no margin,
        # so a tile/chunk/wall sprite straddling the left or top edge of
        # the viewport can flicker in and out as the camera's sub-tile
        # position changes by a pixel between frames. The symmetric
        # buffer here costs at most one extra row/column of off-screen
        # tiles rendered - trivial compared to the pop-in bug it fixes.
        tile_left = max(0, int(cam_left / self.tile_size) - 1)
        tile_top = max(0, int(cam_top / self.tile_size) - 1)
        tile_right = min(tilemap.width, int(cam_right / self.tile_size) + 1)
        tile_bottom = min(tilemap.height, int(cam_bottom / self.tile_size) + 1)
        
        # Draw viewport background
        pygame.draw.rect(screen, (20, 20, 20), viewport_rect)

        # Kyle's 3-layer model: (1) collision/pass-block - untouched by
        # any of this, handled per-tile below as always; (2) baseline
        # ground chunks; (3) roads and water, layered ON TOP of the
        # baseline and always winning where they apply. Drawn in that
        # order - ground chunks first, then water chunks, then roads -
        # so water/roads always paint over ground, never under it.
        #
        # Ground and water each use the same two-pass opaque+feathered
        # technique (_draw_chunk_layer helper below) - Kyle: "fix the
        # seams bro" after a visible line where adjacent chunks met; a
        # single feathered pass made it WORSE (thick dark cross-bands)
        # because each chunk's fade-to-transparent edge was blending
        # onto the dark viewport background for whichever neighbor
        # hadn't been drawn yet, not onto real content. Two passes fixes
        # this: pass 1 draws every chunk fully opaque (guarantees full
        # coverage), pass 2 redraws oversized with faded edges so the
        # fade always blends onto real ground from pass 1.
        FEATHER_PX = 48
        self._draw_chunk_layer(screen, camera, viewport_rect, tilemap.ground_chunks,
                                tile_left, tile_top, tile_right, tile_bottom, FEATHER_PX)
        self._draw_chunk_layer(screen, camera, viewport_rect, tilemap.water_chunks,
                                tile_left, tile_top, tile_right, tile_bottom, FEATHER_PX,
                                tilemap=tilemap, only_base_tiles={"shallow_water", "deep_water"})
        # Real bug (finally fully found and fixed this session) - a
        # PARALLEL, separate "cliff"/"wall" tuple to the one already
        # fixed earlier in this file (the per-tile skip-check at the
        # "layer_tile in (...)" line below). THIS is the call site that
        # actually controls whether obstacle_chunks' pixels get drawn
        # at all - only_collision_tiles gates _draw_chunk_layer's
        # per-tile clip loop, and it never included "rock" even after
        # the other check was fixed. Confirmed via a direct call-trace
        # during a real render: get_landmark_sprite was genuinely being
        # called 839 times with the right wall sprite paths (proving
        # the OTHER check's fix was working), but the clipped per-tile
        # blit loop inside _draw_chunk_layer was silently skipping
        # every "rock" tile because "rock" wasn't in THIS set - so the
        # sprite was loaded/cached but never actually blitted anywhere.
        # Both The Den and Burning Blade Coven use "rock" for walls, so
        # this was the true, complete explanation for "walls not
        # loading" in both caves - the earlier fix was real but
        # incomplete, only addressing one of two places this same tuple
        # needed the same addition.
        self._draw_chunk_layer(screen, camera, viewport_rect, tilemap.obstacle_chunks,
                                tile_left, tile_top, tile_right, tile_bottom, FEATHER_PX,
                                tilemap=tilemap, only_base_tiles=None,
                                only_collision_tiles={"cliff", "wall", "rock"})
        self._draw_road_segments(screen, camera, viewport_rect, tilemap,
                                  tile_left, tile_top, tile_right, tile_bottom)

        # Render only visible tiles
        for y in range(tile_top, tile_bottom):
            for x in range(tile_left, tile_right):
                # Same priority order as before (interaction > collision >
                # base) - just resolving to a textured sprite where one is
                # mapped, falling back to the flat color otherwise.
                #
                # IMPORTANT: "visual" tiles (flowers, grass_tuft, small_rocks,
                # bramble/root bushes) are decorative SCATTER meant to sit ON
                # TOP of the ground, not replace it. The old single-"winning
                # tile" model (pick the topmost non-empty layer, draw only
                # that) was correct for collision/interaction (a wall or NPC
                # really does fully occupy the tile) but wrong for visual -
                # it drew the rock/flower sprite's transparent margins over
                # a blank/background-color square instead of the actual
                # ground texture, since the base layer's draw call was
                # skipped entirely whenever a visual tile existed. That's
                # what produced "black box behind the rock" artifacts.
                #
                # Fix: always draw base first (sprite or flat-color fallback
                # if unmapped), THEN blit visual/collision/interaction sprites
                # on top in that priority order if they resolve to a real
                # sprite. A layer with no sprite mapping still falls back to
                # its own flat-color rect on top of base, same as before -
                # only a layer that actually has nothing set is skipped.
                base_tile = tilemap.get_tile(x, y, "base")
                visual_tile = tilemap.get_tile(x, y, "visual")
                collision_tile = tilemap.get_tile(x, y, "collision")
                interaction_tile = tilemap.get_tile(x, y, "interaction")

                # Convert world coords to screen coords (needed before any
                # drawing now that we may draw multiple layers per tile).
                screen_x, screen_y = camera.world_to_screen(x, y, self.tile_size)
                screen_x += viewport_rect.x
                screen_y += viewport_rect.y
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

                # Base layer - always drawn first, sprite or flat color -
                # UNLESS a ground chunk already covers this tile with a
                # sprite that actually loaded (get_chunk_at is O(1), see
                # Tilemap.add_ground_chunk). A chunk whose sprite failed
                # to load (bad path, missing file) is treated as if no
                # chunk existed here at all, so this tile falls back to
                # BASE LAYER: ground and water chunks are fully separate
                # structures now (Tilemap.get_ground_chunk_at /
                # get_water_chunk_at - see that class's comment for why
                # the old single-list "kind"-tagged design broke). A
                # water tile only ever consults water_chunks; everything
                # else only ever consults ground_chunks. No cross-
                # contamination is possible by construction, so no
                # redraw-to-correct-a-wrong-chunk hack is needed anymore
                # - each tile's OWN chunk (if any) was already drawn
                # correctly in the two independent chunk passes above,
                # and this loop just needs to know whether to skip its
                # own base_layer draw or not.
                is_water_tile = base_tile in ("shallow_water", "deep_water")
                if is_water_tile:
                    chunk = tilemap.get_water_chunk_at(x, y)
                else:
                    chunk = tilemap.get_ground_chunk_at(x, y)
                chunk_covers_this_tile = False
                if chunk is not None:
                    px_w = chunk["width_tiles"] * self.tile_size
                    px_h = chunk["height_tiles"] * self.tile_size
                    chunk_covers_this_tile = get_landmark_sprite(chunk["sprite_key"], px_w, px_h) is not None

                if chunk_covers_this_tile:
                    pass  # already drawn by the ground/water chunk pass above
                elif base_tile:
                    base_sprite = self._get_sprite_for_tile(tilemap, base_tile, x, y)
                    if base_sprite is not None:
                        screen.blit(base_sprite, rect)
                    else:
                        pygame.draw.rect(screen, get_tile_color(base_tile), rect)
                        pygame.draw.rect(screen, (100, 100, 100), rect, 1)
                else:
                    pygame.draw.rect(screen, (50, 50, 50), rect)
                    pygame.draw.rect(screen, (100, 100, 100), rect, 1)

                # Higher layers composite on top, in priority order. Each
                # only draws if that layer actually has a tile_id set -
                # otherwise base (already drawn above) shows through
                # untouched, which is the whole point of the fix.
                #
                # "landmark" is a special case: it's the collision tile
                # add_landmark() stamps across a multi-tile structure's
                # footprint, but it has no texture-entry mapping (its
                # visual comes from the separate landmark image drawn
                # after this whole per-tile loop, not from the per-tile
                # pipeline) - so it must NOT fall back to a flat-color
                # rect here, or every tile under the landmark image shows
                # a gray/brown square through the art's transparent
                # corners. Skipping it lets the actual ground texture
                # (already drawn as base, above) show through instead,
                # which is what should be visible at the structure's edges.
                for layer_tile in (visual_tile, collision_tile, interaction_tile):
                    if not layer_tile or layer_tile == "landmark":
                        continue
                    # "npc" is a placement marker only (says "an NPC entity
                    # stands here"), not a texture - real NPCs/vendors/
                    # recruits/ambient townsfolk all render their own sprite
                    # separately, later in this function. Falling back to
                    # this tile's flat gold color when unmapped painted a
                    # gold square under every NPC's feet (Kyle: "ugly yellow
                    # box"), so it's excluded the same way "landmark" is.
                    if layer_tile == "npc":
                        continue
                    # "chest" is the same story: the real chest art is drawn
                    # in its own pass below (world/chest_looks.py).
                    if layer_tile == "chest":
                        continue
                    # "boss_marker" is the same story as "npc" above - a
                    # placement marker, not a texture. The real boss visual
                    # is drawn separately, later in this function, from
                    # cave_spawns (a proper portrait icon - see
                    # boss_icons.py). Without this exclusion, this flat red
                    # tile painted a solid red square UNDER that portrait
                    # icon, which was most of what actually read as
                    # "Redbox with an X" (Kyle, 2026-09-09) - the X came
                    # from the old cave_spawns marker (already fixed
                    # separately), but the red backing square was this
                    # tile bleeding through underneath the fix.
                    if layer_tile == "boss_marker":
                        continue
                    # "gathering_node" is the same story - a placement
                    # marker for GatheringNodeManager, not a texture. The
                    # real material icon (Peacebloom, Copper Ore, ...) is
                    # drawn separately below from the gathering_nodes list,
                    # same pattern as ambient_npcs/cave_spawns.
                    if layer_tile == "gathering_node":
                        continue
                    # "water" is a pure movement-blocker marker (Echo Isles
                    # stamps it across the whole open sea so the player
                    # can't swim off the crossings), not a texture. It has
                    # no tiles.py entry, so it fell back to a flat gray
                    # box + gray grid line on top of the real water art -
                    # the whole ocean read as a gray graph-paper grid
                    # (Kyle: "still fallback tiles"). Skipped like
                    # "landmark" so the base-layer water shows through.
                    if layer_tile == "water":
                        continue
                    # Kyle: "mountain tiles should also be in the third
                    # layer... since they're still read as movement=false,
                    # right?" - confirmed (cliff/wall are both
                    # walkable=False, collision layer, per tiles.py) and
                    # given their own obstacle_chunks structure (see that
                    # attribute's comment on Tilemap for why it's not
                    # merged into water_chunks/road_segments - different
                    # axis, collision not base). When a real obstacle
                    # chunk covers this exact tile, skip the normal per-
                    # tile texture draw here - the obstacle-chunk pass
                    # (drawn before this per-tile loop, same two-pass
                    # opaque+feathered technique as ground/water) already
                    # painted it with real large-format mountain art
                    # instead of a tiny crop repeated per-32px-tile.
                    # Real bug found & fixed here (Kyle: rendering
                    # Burning Blade Coven showed a flat gray grid
                    # instead of the real chunked wall art) - this check
                    # only recognized "cliff"/"wall" as chunk-eligible,
                    # but both The Den and Burning Blade Coven's cave
                    # generators use "rock" for their wall collision
                    # tile_id, not "cliff"/"wall". Confirmed directly:
                    # obstacle_chunks/get_obstacle_chunk_at had entirely
                    # correct data (right sprite key, right chunk
                    # bounds) for a "rock" tile, and the sprite file
                    # itself loaded fine in isolation - the ONLY thing
                    # wrong was this tuple never including "rock", so
                    # every rock-walled cave (both existing dedicated
                    # cave functions this session) was silently falling
                    # through to the old per-tile flat-color fallback
                    # for its entire wall footprint. The Den's own walls
                    # likely have this same bug and were never caught
                    # because those screenshots happened to frame mostly
                    # lake/boss-room close-ups where walls were a small
                    # fraction of the shot, not a wide-open corridor view.
                    if layer_tile in ("cliff", "wall", "rock"):
                        obstacle_chunk = tilemap.get_obstacle_chunk_at(x, y)
                        if obstacle_chunk is not None:
                            px_w = obstacle_chunk["width_tiles"] * self.tile_size
                            px_h = obstacle_chunk["height_tiles"] * self.tile_size
                            if get_landmark_sprite(obstacle_chunk["sprite_key"], px_w, px_h) is not None:
                                continue
                    layer_sprite = self._get_sprite_for_tile(tilemap, layer_tile, x, y)
                    if layer_sprite is not None:
                        screen.blit(layer_sprite, rect)
                    else:
                        pygame.draw.rect(screen, get_tile_color(layer_tile), rect)
                        pygame.draw.rect(screen, (100, 100, 100), rect, 1)

        # Multi-tile landmarks (cave-mouth entrance art, statues, etc.) -
        # drawn as one scaled image spanning their whole footprint, after
        # the per-tile grid above so the landmark art fully covers the
        # "landmark" collision tile's flat-color fallback underneath it.
        # See Tilemap.add_landmark's docstring for why these aren't routed
        # through the normal per-tile texture pipeline.
        for lm in getattr(tilemap, "landmarks", []):
            lm_screen_x, lm_screen_y = camera.world_to_screen(
                lm["anchor_x"], lm["anchor_y"], self.tile_size)
            lm_screen_x += viewport_rect.x
            lm_screen_y += viewport_rect.y
            lm_w = lm["width_tiles"] * self.tile_size
            lm_h = lm["height_tiles"] * self.tile_size

            # Cull landmarks fully outside the viewport - cheap check,
            # avoids scaling/blitting a big image every frame for
            # structures nowhere near the camera.
            if (lm_screen_x + lm_w < viewport_rect.left or lm_screen_x > viewport_rect.right
                    or lm_screen_y + lm_h < viewport_rect.top or lm_screen_y > viewport_rect.bottom):
                continue

            rotation = lm.get("rotation", 0)
            if rotation:
                # Rotated landmarks (see Tilemap.add_landmark's rotation
                # param) need the UNROTATED footprint's dimensions when
                # requesting/scaling the source sprite - a 90/270 rotation
                # swaps which axis is "wide" after the fact, so asking
                # get_landmark_sprite for the already-swapped lm_w/lm_h
                # would scale the source art to the wrong aspect before
                # rotating it, distorting it. Request at the swapped
                # (pre-rotation) box, rotate, then it lands back at
                # lm_w x lm_h.
                if rotation in (90, 270):
                    sprite = get_landmark_sprite(lm["sprite_key"], lm_h, lm_w)
                else:
                    sprite = get_landmark_sprite(lm["sprite_key"], lm_w, lm_h)
                if sprite is not None:
                    sprite = pygame.transform.rotate(sprite, -rotation)
            else:
                sprite = get_landmark_sprite(lm["sprite_key"], lm_w, lm_h)
            if sprite is not None:
                screen.blit(sprite, (lm_screen_x, lm_screen_y))
        
        # Draw chests (unlooted chest tiles keep "chest" on the interaction layer; looting clears it)
        for y in range(tile_top, tile_bottom):
            for x in range(tile_left, tile_right):
                if tilemap.get_tile(x, y, "interaction") != "chest":
                    continue
                look = chest_look(tilemap.name, x, y, is_boss_chest(tilemap, x, y), getattr(tilemap, "is_cave", False))
                csprite = chest_sprite(look, self.tile_size)
                if csprite is None:
                    continue
                cx, cy = camera.world_to_screen(x, y, self.tile_size)
                cx += viewport_rect.x
                cy += viewport_rect.y
                screen.blit(csprite, (cx + (self.tile_size - csprite.get_width()) // 2,
                                      cy + self.tile_size - csprite.get_height() + 4))

        # Draw player position
        if player_pos:
            player_x, player_y = player_pos
            screen_x, screen_y = camera.world_to_screen(player_x, player_y, self.tile_size)
            
            # Offset by viewport position on screen
            screen_x += viewport_rect.x
            screen_y += viewport_rect.y
            
            rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

            sprite = None
            if player is not None:
                base_path = sprite_base_path(
                    getattr(player, "race", None), getattr(player, "gender", None),
                    getattr(player, "appearance_variant", 0))
                if base_path:
                    sprite = get_npc_sprite(base_path, player_facing, tile_height=int(self.tile_size * self.npc_sprite_scale))
            mount_art = None
            try:
                from world.travel_manager import get_travel_manager
                _tm = get_travel_manager()
                if _tm.mounted and _tm.current_mount():
                    mount_art = get_mount_sprite(_tm.current_mount()["id"], player_facing, self.tile_size)
            except Exception:
                mount_art = None
            if sprite is not None and mount_art is not None:
                # Mounted: the mount stands on the tile (bottom-centre), the rider is drawn over its saddle with the
                # legs hidden (cut at the seat) so they read as sitting rather than standing on the animal.
                mount, seat = mount_art
                mx = screen_x + (self.tile_size - mount.get_width()) // 2
                my = screen_y + self.tile_size - mount.get_height() + self.tile_size // 6
                screen.blit(mount, (mx, my))
                seat_y = my + mount.get_height() - int(mount.get_height() * seat)
                vis_h = max(1, int(sprite.get_height() * 0.74))
                sx = screen_x + (self.tile_size - sprite.get_width()) // 2
                screen.blit(sprite, (sx, seat_y - vis_h), pygame.Rect(0, 0, sprite.get_width(), vis_h))
            elif sprite is not None:
                # Anchor at the tile's bottom-center, not top-left - real
                # character art (80x120 human frames) is taller than one
                # tile, so it should stand ON the tile with its head/hair
                # rising above it, the same "sprite taller than its own
                # footprint" convention every tile RPG uses. Blitting at
                # (screen_x, screen_y) unscaled-for-height would instead
                # plant the sprite's HEAD at the tile's top edge, with
                # its feet floating a tile-size below the ground.
                sx = screen_x + (self.tile_size - sprite.get_width()) // 2
                sy = screen_y + self.tile_size - sprite.get_height()
                screen.blit(sprite, (sx, sy))
            else:
                pygame.draw.rect(screen, (255, 255, 255), rect)  # White square fallback
        
        # Draw vendor NPCs (Phase 6)
        if vendors:
            for vendor in vendors:
                screen_x, screen_y = camera.world_to_screen(vendor.x, vendor.y, self.tile_size)
                
                # Offset by viewport position on screen
                screen_x += viewport_rect.x
                screen_y += viewport_rect.y
                
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

                sprite = None
                base_path = sprite_base_path(
                    getattr(vendor, "race", None), getattr(vendor, "gender", "male"),
                    getattr(vendor, "appearance_variant", 0))
                if base_path:
                    sprite = get_npc_sprite(base_path, getattr(vendor, "facing", "down"), tile_height=int(self.tile_size * self.npc_sprite_scale))
                if sprite is not None:
                    sx = screen_x + (self.tile_size - sprite.get_width()) // 2
                    sy = screen_y + self.tile_size - sprite.get_height()
                    screen.blit(sprite, (sx, sy))
                else:
                    pygame.draw.rect(screen, (200, 150, 50), rect)  # Gold square fallback

                if quest_indicators:
                    self._draw_quest_indicator(screen, quest_indicators.get(vendor.vendor_id),
                                                screen_x, sy if sprite is not None else screen_y)
        
        # Draw recruit NPCs (real human sprite, falling back to the
        # distinct npc_color square if sprite resolution fails)
        if recruits:
            for recruit in recruits:
                screen_x, screen_y = camera.world_to_screen(recruit.x, recruit.y, self.tile_size)
                
                # Offset by viewport position on screen
                screen_x += viewport_rect.x
                screen_y += viewport_rect.y
                
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

                sprite = None
                tile_h = int(self.tile_size * self.npc_sprite_scale)
                # Each recruit has their own one-direction (facing down) sprite at
                # assets/npcs/recruits/<recruit_id>/down.png; always drawn facing
                # down. Falls back to the generic human variant if it is missing.
                custom = f"assets/npcs/recruits/{recruit.recruit_id}"
                if os.path.exists(f"{custom}/down.png"):
                    sprite = get_npc_sprite(custom, "down", tile_height=tile_h)
                if sprite is None:
                    base_path = sprite_base_path(
                        getattr(recruit, "race", "human"), getattr(recruit, "gender", "male"),
                        getattr(recruit, "appearance_variant", 0))
                    if base_path:
                        sprite = get_npc_sprite(base_path, getattr(recruit, "facing", "down"), tile_height=tile_h)

                if sprite is not None:
                    sx = screen_x + (self.tile_size - sprite.get_width()) // 2
                    sy = screen_y + self.tile_size - sprite.get_height()
                    screen.blit(sprite, (sx, sy))
                else:
                    # Parse hex color or use default
                    hex_color = recruit.npc_color if hasattr(recruit, 'npc_color') else "#FFFFFF"
                    try:
                        # Convert hex string to RGB tuple
                        hex_color = hex_color.lstrip('#')
                        color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    except (ValueError, TypeError):
                        color = (255, 255, 255)  # Default white
                    
                    pygame.draw.rect(screen, color, rect)  # Bright distinctive color fallback

        # Draw ambient/flavor NPCs (guards, townsfolk) - real sprite only,
        # no colored-square fallback identity since these have no
        # npc_color field (they're not meant to be attention-grabbing the
        # way a recruit is) - a missing sprite just means nothing draws
        # for that one NPC rather than a jarring flat-color square.
        if ambient_npcs:
            for npc in ambient_npcs:
                screen_x, screen_y = camera.world_to_screen(npc.x, npc.y, self.tile_size)
                screen_x += viewport_rect.x
                screen_y += viewport_rect.y

                base_path = sprite_base_path(
                    getattr(npc, "race", "human"), getattr(npc, "gender", "male"),
                    getattr(npc, "appearance_variant", 0))
                sprite = get_npc_sprite(base_path, getattr(npc, "facing", "down"), tile_height=int(self.tile_size * self.npc_sprite_scale)) \
                    if base_path else None
                if sprite is not None:
                    sx = screen_x + (self.tile_size - sprite.get_width()) // 2
                    sy = screen_y + self.tile_size - sprite.get_height()
                    screen.blit(sprite, (sx, sy))

                if quest_indicators:
                    self._draw_quest_indicator(screen, quest_indicators.get(npc.npc_id),
                                                screen_x, sy if sprite is not None else screen_y)

        # Draw cave/dungeon fixed spawns (trash + boss). These were
        # previously invisible - CaveSpawnManager tracked exactly where
        # every monster stood (including is_boss), but nothing ever drew
        # them, so a boss chamber looked identical to an empty room until
        # you walked in blind.
        # Draw gathering nodes (herbs, ore) - real per-material icon, same
        # "show what's actually there" treatment as cave_spawns above.
        # icon_id can be None for a material with no cropped art yet
        # (nothing in Phase 1's material set, but future tiers may add
        # entries before their art is ready) - falls soft to no sprite
        # rather than a placeholder square, matching every other
        # sprite-or-nothing fallback in this renderer.
        #
        # Kyle: "the nodes for plants/ore... are too small and hard to
        # see, I want them to stand out" - 2x taller, 1.5x wider than a
        # normal tile (was a flat 1x1 tile_size box). Anchored at
        # bottom-center of the node's actual world tile rather than
        # top-left, so the enlarged sprite grows up and out from its real
        # ground position instead of drifting off to the tile's
        # bottom-right - same anchoring idea as every multi-tile landmark
        # elsewhere in this renderer.
        if gathering_nodes:
            node_w = int(self.tile_size * 1.5)
            node_h = int(self.tile_size * 2)
            for (nx, ny, material_type, icon_id) in gathering_nodes:
                screen_x, screen_y = camera.world_to_screen(nx, ny, self.tile_size)
                screen_x += viewport_rect.x
                screen_y += viewport_rect.y
                # bottom-center anchor: shift left by the extra width/2,
                # shift up by the extra height (so the sprite's bottom
                # edge still sits on the tile's bottom edge, same as
                # before the resize).
                rect = pygame.Rect(
                    screen_x - (node_w - self.tile_size) // 2,
                    screen_y - (node_h - self.tile_size),
                    node_w, node_h)

                if icon_id:
                    folder = MATERIAL_TYPE_FOLDERS.get(material_type, material_type)
                    sheet_path = f"assets/gathering_nodes/{folder}/{icon_id}.png"
                    sprite = get_tile_sprite(sheet_path, (0, 0, 32, 32), max(node_w, node_h))
                    if sprite is not None:
                        scaled = pygame.transform.smoothscale(sprite, (node_w, node_h))
                        screen.blit(scaled, rect)

        if cave_spawns:
            for (sx, sy, is_boss, creature_name) in cave_spawns:
                screen_x, screen_y = camera.world_to_screen(sx, sy, self.tile_size)
                screen_x += viewport_rect.x
                screen_y += viewport_rect.y

                if is_boss:
                    # Real boss portrait (see boss_icons.py), same system
                    # the map screen uses - was a flat red square with a
                    # white X, which read as a broken/missing texture
                    # rather than deliberate placeholder art (Kyle,
                    # 2026-09-09). Sized a bit larger than a normal tile,
                    # same "unmistakable at a glance" goal the old marker
                    # had, just with a real picture instead of a color.
                    template = None
                    if creature_manager is not None and creature_name:
                        creature = creature_manager.creatures.get(creature_name, {})
                        template = creature.get("template")
                    # Dungeon bosses are BIG (Kyle: "boss sprites in dungeon need to be way bigger"):
                    # ~4 tiles, standing on the spawn tile so the feet sit at its bottom edge.
                    icon_size = int(self.tile_size * self.BOSS_ICON_TILES)
                    icon = self._get_boss_icon(template, icon_size)
                    if icon:
                        icon_rect = icon.get_rect(midbottom=(
                            screen_x + self.tile_size // 2,
                            screen_y + self.tile_size + self.tile_size // 4))
                        screen.blit(icon, icon_rect)
                    else:
                        # Icon file failed to load (shouldn't happen with
                        # the full template table - see boss_icons.py -
                        # but fails soft rather than silently drawing
                        # nothing where a boss actually is).
                        pad = 2
                        rect = pygame.Rect(screen_x - pad, screen_y - pad,
                                           self.tile_size + pad * 2, self.tile_size + pad * 2)
                        pygame.draw.rect(screen, (180, 0, 0), rect)
                        pygame.draw.rect(screen, (255, 60, 60), rect, 2)
                else:
                    rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                    pygame.draw.rect(screen, (200, 60, 60), rect)  # dull red = trash mob

        # Draw viewport border
        pygame.draw.rect(screen, (100, 150, 100), viewport_rect, 2)
    
    def render_legend(self, screen, font, x=20, y=20, max_width=200):
        """Render a compact tile-color legend, wrapped into two columns so
        it reads as a small reference block instead of an 8-row list eating
        the whole right-side panel between the resource bars and the cast
        panel tab (see mockup: 'Silverpine North' HUD screenshot)."""
        legend_items = [
            ("Grass", (34, 139, 34)),
            ("Water", (100, 149, 237)),
            ("Stone", (105, 105, 105)),
            ("Tree/Rock", (70, 70, 70)),
            ("NPC", (255, 215, 0)),
            ("Portal", (138, 43, 226)),
            ("Boss", (180, 0, 0)),
            ("Player", (255, 255, 255)),
        ]

        col_width = max_width // 2
        row_height = 18
        box_size = 12

        for i, (label, color) in enumerate(legend_items):
            col = i // 4
            row = i % 4
            item_x = x + col * col_width
            item_y = y + row * row_height

            rect = pygame.Rect(item_x, item_y, box_size, box_size)
            pygame.draw.rect(screen, color, rect)

            text = font.render(label, True, (255, 255, 255))
            screen.blit(text, (item_x + box_size + 5, item_y - 2))
