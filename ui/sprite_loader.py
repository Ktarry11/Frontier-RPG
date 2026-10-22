"""
Sprite sheet loader/cache for tile textures.

Loads each source PNG sheet exactly once (keyed by path) and caches
individually-cropped, tile-size-scaled Surfaces so the renderer never
re-decodes or re-scales the same rect twice. All texture data flows
through this module - nothing else touches raw sheet files directly.

Usage:
    from ui.sprite_loader import get_tile_sprite
    surf = get_tile_sprite("assets/tiles/undead/Ground_rocks.png",
                            rect=(24, 24, 32, 32), tile_size=32)

If the source file is missing or the crop fails, returns None so callers
(tilemap_renderer.py) can fall back to the flat-color rect rendering that
already exists - texturing a tile is additive, never a hard requirement.
"""
import os
import pygame

# sheet path -> loaded pygame.Surface (raw, unscaled, convert_alpha'd)
_sheet_cache = {}

# (sheet path, rect tuple, output tile_size) -> final scaled Surface
_sprite_cache = {}


def _load_sheet(path):
    """Load and cache a full sheet. Returns None if the file is missing
    or fails to load, rather than raising - a missing texture pack should
    degrade to flat colors, not crash the game."""
    if path in _sheet_cache:
        return _sheet_cache[path]

    if not os.path.isfile(path):
        _sheet_cache[path] = None
        return None

    try:
        surf = pygame.image.load(path)
        # convert_alpha requires a display to be initialized; guard for
        # headless/test contexts where it isn't.
        if pygame.display.get_surface() is not None:
            surf = surf.convert_alpha()
    except pygame.error:
        surf = None

    _sheet_cache[path] = surf
    return surf


def get_tile_sprite(sheet_path, rect, tile_size):
    """
    Get a cropped-and-scaled sprite ready to blit at (0,0) of a tile cell.

    sheet_path: path to the source PNG, relative to the project root
                (e.g. "assets/tiles/undead/Ground_rocks.png").
    rect: (x, y, w, h) source pixel rect within the sheet to crop.
    tile_size: final on-screen pixel size to scale to (square). Scaling
               uses nearest-neighbor for pixel-art sheets so edges stay
               crisp; sheets wanting smooth scaling (e.g. the high-res
               Forgotten Memories pack) should pre-scale via
               get_tile_sprite_smooth instead.

    Returns a pygame.Surface, or None if the sheet/crop is unavailable -
    callers must handle None by falling back to flat-color rendering.
    """
    return _get_tile_sprite_impl(sheet_path, rect, tile_size, smooth=False)


def get_tile_sprite_smooth(sheet_path, rect, tile_size):
    """
    Same as get_tile_sprite, but uses smoothscale (bilinear) instead of
    nearest-neighbor. Use this for high-res painterly source art (e.g.
    Forgotten Memories' ~170px tiles) being downscaled to a much smaller
    on-screen tile_size - nearest-neighbor on a large downscale produces
    aliasing/moire on soft art; smoothscale reads much cleaner.
    Pixel-art sheets (16px-native packs) should keep using the crisp
    get_tile_sprite instead - smoothing those blurs deliberate hard edges.
    """
    return _get_tile_sprite_impl(sheet_path, rect, tile_size, smooth=True)


def _get_tile_sprite_impl(sheet_path, rect, tile_size, smooth):
    cache_key = (sheet_path, tuple(rect), tile_size, smooth)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    sheet = _load_sheet(sheet_path)
    if sheet is None:
        _sprite_cache[cache_key] = None
        return None

    x, y, w, h = rect
    sheet_w, sheet_h = sheet.get_size()
    if x < 0 or y < 0 or x + w > sheet_w or y + h > sheet_h:
        # Rect falls outside the sheet bounds - a bad mapping entry.
        # Fail soft (None -> flat-color fallback) rather than crash,
        # since a single bad rect shouldn't take down the whole renderer.
        _sprite_cache[cache_key] = None
        return None

    try:
        cropped = sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
        if smooth:
            scaled = pygame.transform.smoothscale(cropped, (tile_size, tile_size))
        else:
            scaled = pygame.transform.scale(cropped, (tile_size, tile_size))
    except (pygame.error, ValueError):
        scaled = None

    _sprite_cache[cache_key] = scaled
    return scaled


def get_feathered_chunk_sprite(sheet_path, target_width, target_height, feather_px=48):
    """
    Same scaling as get_landmark_sprite, but with a soft alpha gradient
    baked into all 4 edges (fully opaque center fading to transparent at
    the border). Built for Tilemap.ground_chunks - Kyle: "fix the seams
    bro" after a real rendered screenshot showed a visible hard line
    where adjacent 20x20-tile ground chunks met (each chunk was a clean
    rectangle with zero blend into its neighbor, confirmed by directly
    sampling collision/base/chunk data at the seam - NOT the initial
    wrong diagnosis of "the old per-tile grid is back", which turned out
    to be the zone's boundary wall/cliff collision tiles rendering
    correctly on top of a chunk that WAS working).

    The renderer draws each chunk oversized by feather_px on every side
    (so chunks overlap their neighbors) and relies on later-drawn chunks'
    faded edges blending into earlier-drawn chunks showing through -
    same alpha-blended-edge-overlay principle as the tiling article Kyle
    found, adapted to not require a second logic-vs-visual grid: chunks
    still snap to the same 32px logic grid, only the DRAWN rectangle is
    oversized, purely a render-time effect.

    feather_px is in SOURCE-SCALED pixels (i.e. relative to
    target_width/height, after scaling) - 48px default blends over
    ~1.5 tiles at TILE_SIZE=32, enough to hide the seam without eating
    a large fraction of a 640px chunk's real detail.
    """
    cache_key = ("feathered", sheet_path, target_width, target_height, feather_px)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    base = get_landmark_sprite(sheet_path, target_width, target_height)
    if base is None:
        _sprite_cache[cache_key] = None
        return None

    try:
        w, h = base.get_size()
        f = min(feather_px, w // 2, h // 2)
        if f < 2:
            _sprite_cache[cache_key] = base
            return base

        import numpy as np
        # Alpha ramp per axis via numpy instead of a per-pixel PixelArray
        # loop (an earlier draft did a plain Python double-loop over
        # every pixel - correct but slow, ~260ms per unique 640x640
        # chunk image on a cache miss; harmless today with only 3 unique
        # source images, but not something to leave in a "1000s of
        # zones" system where a much bigger/more numerous chunk image
        # set is a real possibility later). Same min-of-4-edges logic,
        # vectorized: alpha ramps linearly from 0 at the very edge to
        # 255 at f pixels in, on all 4 sides, taking the min so corners
        # fade in both axes at once.
        x_idx = np.arange(w)
        y_idx = np.arange(h)
        ramp_x = np.minimum(np.minimum(x_idx, w - 1 - x_idx) / f, 1.0)
        ramp_y = np.minimum(np.minimum(y_idx, h - 1 - y_idx) / f, 1.0)
        alpha_2d = np.minimum(ramp_x[None, :], ramp_y[:, None])
        alpha_2d = np.clip(alpha_2d * 255, 0, 255).astype(np.uint8)

        feathered = base.copy().convert_alpha()
        # pygame.surfarray.pixels_alpha gives a (width, height) view
        # directly into the surface's alpha channel - alpha_2d was built
        # as (height, width) (row=y, col=x, the natural numpy/image
        # convention), so .T aligns it to pygame's (width, height) axis
        # order. Writing through this view mutates the surface itself.
        alpha_view = pygame.surfarray.pixels_alpha(feathered)
        alpha_view[:, :] = alpha_2d.T
        del alpha_view  # release the array's lock on the surface
    except (pygame.error, ValueError, ImportError):
        feathered = base

    _sprite_cache[cache_key] = feathered
    return feathered


def get_landmark_sprite(sheet_path, target_width, target_height):
    """
    Load a full source image (landmarks are stored as standalone PNGs, not
    cropped from a shared sheet) and scale it to an arbitrary WxH pixel
    size - unlike get_tile_sprite/_smooth, which always force a square
    tile_size x tile_size output. Multi-tile landmarks (Tilemap.landmarks)
    need rectangular scaling since their tile footprint usually isn't
    square (e.g. a wide cave-mouth arch spanning 5x4 tiles).

    Uses smoothscale since landmark source art (stock cave-entrance
    illustrations, etc.) is painterly/high-res, not native pixel-art -
    same reasoning as get_tile_sprite_smooth.
    """
    cache_key = (sheet_path, target_width, target_height)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    sheet = _load_sheet(sheet_path)
    if sheet is None:
        _sprite_cache[cache_key] = None
        return None

    try:
        scaled = pygame.transform.smoothscale(sheet, (target_width, target_height))
    except (pygame.error, ValueError):
        scaled = None

    _sprite_cache[cache_key] = scaled
    return scaled


def get_npc_sprite(base_path, direction, tile_width=None, tile_height=None):
    """
    Load a pre-cropped NPC/player directional frame (see
    world/race_registry.py for how race+gender+variant resolves to
    base_path) and scale it, preserving the source's aspect ratio.

    HEIGHT-anchored, not width-anchored: pass tile_height and the width
    is derived from the source aspect ratio. Source art sizes vary wildly
    across packs (80x120 human, 48x48 orc, 33x44 orc_pack2, 30x52
    goblin) - anchoring to a fixed WIDTH let each pack's differing aspect
    ratio produce a wildly different on-screen HEIGHT, which is what made
    the goblin pack (tall/narrow source, 30x52) render nearly 3 tiles
    tall while orc (square, 48x48) rendered under 2 (Kyle: "the goblin
    NPC is fucking massive"). Anchoring to height instead means every
    race stands the same height on screen regardless of its source art's
    native proportions, which is what actually matters for a top-down
    tile grid - width can vary (a stockier build reads fine narrower or
    wider), height is what has to line up with everything else standing
    on the same size tile.

    tile_width is still accepted (and still anchors if provided instead
    of tile_height) for any caller not yet migrated, but new callers
    should pass tile_height.

    base_path: folder containing down.png/left.png/right.png/up.png
               (no trailing slash), e.g. "assets/npcs/orc/orc_3".
    direction: "down" | "left" | "right" | "up".

    Returns None on any failure (missing folder, bad direction, corrupt
    file) so callers fall back to the flat-color square every NPC/player
    tile rendered with until now - never a hard crash from a missing
    sprite.
    """
    if not base_path or direction not in ("down", "left", "right", "up"):
        return None
    if tile_width is None and tile_height is None:
        return None

    sheet_path = f"{base_path}/{direction}.png"
    cache_key = ("npc", sheet_path, tile_width, tile_height)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]

    sheet = _load_sheet(sheet_path)
    if sheet is None:
        _sprite_cache[cache_key] = None
        return None

    try:
        src_w, src_h = sheet.get_size()
        if tile_height is not None:
            # Height-anchored (preferred): derive width from aspect ratio.
            out_h = tile_height
            out_w = round(src_w * (tile_height / src_h))
        else:
            # Legacy width-anchored path, kept for any unmigrated caller.
            out_w = tile_width
            out_h = round(src_h * (tile_width / src_w))
        scaled = pygame.transform.scale(sheet, (out_w, out_h))
    except (pygame.error, ValueError, ZeroDivisionError):
        scaled = None

    _sprite_cache[cache_key] = scaled
    return scaled


# Side-view length of each mount in TILES.  The four facings of one mount share one pixel scale (derived from its
# left/right art) so turning on the spot never makes the animal grow or shrink.
MOUNT_LENGTH_TILES = {
    "timber_wolf": 3.8, "dire_wolf": 4.1, "brown_kodo": 4.9, "war_kodo": 5.6,
    "razormane_raptor": 3.9, "swift_raptor": 4.2,
}
# Where the saddle seat sits, as a fraction of the sprite's height up from its feet, per view.
MOUNT_SEAT = {"down": 0.56, "up": 0.56, "left": 0.52, "right": 0.52}


def get_mount_sprite(mount_id, direction, tile_size):
    """Scaled mount sprite (assets/mounts/<id>_<dir>.png) or None.  Returns (surface, seat_fraction)."""
    if direction not in MOUNT_SEAT:
        return None
    cache_key = ("mount", mount_id, direction, tile_size)
    if cache_key in _sprite_cache:
        return _sprite_cache[cache_key]
    result = None
    try:
        sheet = _load_sheet(f"assets/mounts/{mount_id}_{direction}.png")
        sides = [_load_sheet(f"assets/mounts/{mount_id}_{d}.png") for d in ("left", "right")]
        sides = [x for x in sides if x is not None]
        if sheet is not None and sides:
            avg_w = sum(x.get_width() for x in sides) / len(sides)
            k = MOUNT_LENGTH_TILES.get(mount_id, 2.8) * tile_size / avg_w
            scaled = pygame.transform.smoothscale(
                sheet, (max(1, round(sheet.get_width() * k)), max(1, round(sheet.get_height() * k))))
            result = (scaled, MOUNT_SEAT[direction])
    except (pygame.error, ValueError, ZeroDivisionError):
        result = None
    _sprite_cache[cache_key] = result
    return result


def prewarm_chunk_sprites(tilemap, tile_size, feather_px=48):
    """Pre-scale every ground/water/obstacle chunk sprite for a zone,
    once, right when the zone is entered - rather than lazily on first
    draw. Fixes Kyle's "I step once and a whole new chunk just pops into
    existence" bug: get_landmark_sprite/get_feathered_chunk_sprite cache
    by (sheet_path, width, height), but that cache is only populated on
    first call, which happens inside the per-frame render loop the first
    time a chunk's footprint scrolls into the buffered tile range. A
    cold pygame.transform.smoothscale of a 512-627px source chunk image
    is slow enough to show up as a single dropped/late frame - visually
    identical to the chunk having not been there the frame before. Since
    chunk dicts (ground_chunks/water_chunks/obstacle_chunks) are fully
    known the moment a zone is built, every chunk's sprite - both the
    plain get_landmark_sprite and the feathered variant the renderer
    also draws for every chunk - can be warmed into _sprite_cache up
    front instead, so the render loop only ever hits a cache HIT.

    Call this once per zone, right when ZoneManager switches
    current_zone to it (both the initial zone and every
    transition_to_zone) - not every frame, this does real image scaling
    work.
    """
    for chunks in (getattr(tilemap, "ground_chunks", []),
                   getattr(tilemap, "water_chunks", []),
                   getattr(tilemap, "obstacle_chunks", [])):
        for chunk in chunks:
            px_w = chunk["width_tiles"] * tile_size
            px_h = chunk["height_tiles"] * tile_size
            get_landmark_sprite(chunk["sprite_key"], px_w, px_h)
            get_feathered_chunk_sprite(chunk["sprite_key"], px_w, px_h, feather_px=feather_px)


def clear_cache():
    """Drop all cached sheets/sprites. Useful for hot-reloading art during
    development without restarting the game."""
    _sheet_cache.clear()
    _sprite_cache.clear()


def cache_stats():
    """Debug helper: how many sheets/sprites are currently cached."""
    return {
        "sheets_loaded": sum(1 for v in _sheet_cache.values() if v is not None),
        "sheets_failed": sum(1 for v in _sheet_cache.values() if v is None),
        "sprites_cached": sum(1 for v in _sprite_cache.values() if v is not None),
        "sprites_failed": sum(1 for v in _sprite_cache.values() if v is None),
    }
