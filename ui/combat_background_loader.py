"""
Combat background loader/cache.

Resolves a zone name to a biome (reusing world.tile_textures's existing
zone->biome table, so backgrounds always agree with what the overworld
tilemap was already showing) then to a background image folder via
world.combat_backgrounds's nearest-match table, picks a random image from
that folder (and time-of-day/mood variant, if the folder has one), scales
it to fill the given viewport, and caches the scaled Surface so repeat
fights in the same zone/variant don't re-load or re-scale the file.

Loading is best-effort: a missing/corrupt file returns None so
combat_screen.py can skip drawing a background and fall back to its
existing flat-color fill exactly as before this system existed.
"""
import os
import random
import pygame

from world.combat_backgrounds import get_variant_options, resolve_place

BACKGROUNDS_ROOT = "assets/backgrounds"

# (folder, variant, size) -> scaled Surface
_scaled_cache = {}
# absolute file path -> raw loaded Surface (pre-scale)
_raw_cache = {}

# zone_name -> chosen file path, so a given zone shows the SAME background
# for the whole play session (picked once, remembered) rather than
# re-rolling a new random image every single fight in that zone.
_zone_choice = {}


def _list_images(folder_path):
    if not os.path.isdir(folder_path):
        return []
    return [f for f in os.listdir(folder_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))]


def _resolve_folder_path(folder_name, variant=None):
    """folder_name + optional variant -> the actual directory to pick an
    image from. Falls back to the flat folder if the requested variant
    doesn't exist for this pack (e.g. asking dark_dungeon for "Night")."""
    base = os.path.join(BACKGROUNDS_ROOT, folder_name)
    options = get_variant_options(folder_name)
    if not options:
        return base
    chosen = variant if variant in options else options[0]
    return os.path.join(base, chosen)


def _load_raw(path):
    if path in _raw_cache:
        return _raw_cache[path]
    try:
        surf = pygame.image.load(path).convert()
    except (pygame.error, FileNotFoundError):
        surf = None
    _raw_cache[path] = surf
    return surf


def get_background_for_zone(zone_name, is_cave=False, variant=None,
                             size=None, reroll=False, subzone_name=None):
    """Main entry point. Returns a pygame.Surface scaled to `size`
    (width, height), or None if nothing could be loaded.

    `variant` is an optional time-of-day/mood hint ("Morning", "Night",
    "Dark", etc) - ignored by packs that don't have variants.
    `reroll` forces picking a new random image for this zone even if one
    was already chosen this session (e.g. if the person wants variety on
    repeat fights rather than the same frozen background every time).
    """
    if size is None:
        from config import SCREEN_WIDTH, SCREEN_HEIGHT
        size = (SCREEN_WIDTH, SCREEN_HEIGHT)

    # A subzone is a different PLACE, so it gets its own frozen pick. Keying
    # the cache on the zone alone would have handed Slug Fens whichever
    # image the open Barrens rolled first, which is the inheritance bug this
    # parameter exists to fix, just moved one layer down.
    place = subzone_name or zone_name
    cache_key = (zone_name, place) if not reroll else None
    if cache_key and cache_key in _zone_choice:
        path = _zone_choice[cache_key]
    else:
        # The per-place override comes first and may pin a variant of its own. Without this the
        # 43 zones and dungeons missing from the biome tables all resolved to the same green
        # forest, and the tables could not simply be filled in because they also choose the
        # FLOOR AND WALL TEXTURES of a zone - see ZONE_BACKGROUND's comment.
        # The whole precedence chain lives in resolve_place() so the QA tool
        # can ask the same question this does and get the same answer.
        folder_name, pinned, _biome = resolve_place(zone_name, subzone_name, is_cave)
        folder_path = _resolve_folder_path(folder_name, pinned or variant)
        images = _list_images(folder_path)
        if not images:
            # Variant subfolder came up empty (e.g. mossy_forest/Dark has
            # fewer entries than Normal) - fall back to the flat base
            # folder for this pack before giving up entirely.
            folder_path = os.path.join(BACKGROUNDS_ROOT, folder_name)
            images = _list_images(folder_path)
        if not images:
            return None
        path = os.path.join(folder_path, random.choice(images))
        if cache_key:
            _zone_choice[cache_key] = path

    scale_key = (path, size)
    if scale_key in _scaled_cache:
        return _scaled_cache[scale_key]

    raw = _load_raw(path)
    if raw is None:
        return None

    # FILL THE SCREEN WITHOUT DISTORTING IT. This was a straight smoothscale to the viewport,
    # which was invisible while every background was a 16:9 landscape painting and stopped being
    # invisible the moment they were not: the current set runs from 0.72 (a tall desert dune) to
    # 1.94 against a 1.78 screen, so the dune was being stretched two and a half times wider than
    # it was drawn. Scale by the LARGER ratio so the image covers the viewport, then take the
    # middle - a backdrop loses its edges off-screen, which nobody notices, instead of its
    # proportions, which everybody does.
    sw, sh = size
    rw, rh = raw.get_width(), raw.get_height()
    if rw and rh:
        k = max(sw / rw, sh / rh)
        full = pygame.transform.smoothscale(raw, (max(1, round(rw * k)), max(1, round(rh * k))))
        scaled = pygame.Surface(size).convert()
        scaled.blit(full, ((sw - full.get_width()) // 2, (sh - full.get_height()) // 2))
    else:
        scaled = pygame.transform.smoothscale(raw, size)
    _scaled_cache[scale_key] = scaled
    return scaled


def clear_zone_choice(zone_name=None):
    """Forget the remembered background pick for a zone (or all zones if
    zone_name is None), so the next get_background_for_zone() call for it
    rolls a fresh image. Useful for a future 'vary backgrounds' setting."""
    if zone_name is None:
        _zone_choice.clear()
        return
    # Keys are (zone, place) since subzones started getting their own pick,
    # so clearing a zone clears its subzones' picks with it - the caller
    # asked to re-roll that whole map, not just the open ground on it.
    for key in [k for k in _zone_choice if k[0] == zone_name]:
        del _zone_choice[key]
