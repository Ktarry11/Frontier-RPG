"""Nobody stands with a prop drawn over them.

Kyle, 10 Nov 2026: "NPCs on props." Nobody stands on a BLOCKING tile - what he was seeing is
art. A tree's or a banner's picture is far bigger than the tile it grows from, so an NPC placed
a few tiles behind it is drawn in the canopy or wearing the banner. Measured 12 Nov: 105 of 777.

An NPC's position lives in whichever of four places put it there (vendors, ambient NPCs,
recruits, literals in the zone generators); a prop's lives in one list on the map. So the PROP
gives way: one pass over each finished map, like world/portal_art.clear_exits and for the same
reason - the rule is enforced where no generator can get round it.

Only scatter and scenery are removed - trees, banners, crates, signposts. A BUILDING is never
removed: an NPC drawn on a roof is a mis-placed NPC, not a mis-placed inn, and those are left
for the per-town pass and listed by tools/audit_npcs_on_props.py.
"""
import pygame

from world.portal_art import is_entrance_art

#: How much of the NPC's tile the prop's solid pixels must cover before the prop goes.
COVER = 0.5

_masks = {}


def _mask(path, w, h):
    """Alpha mask of the sprite at 16px per tile, or None if it cannot be read."""
    key = (path, w, h)
    if key not in _masks:
        try:
            img = pygame.image.load(path)
            img = pygame.transform.scale(img, (w * 16, h * 16))
            _masks[key] = pygame.mask.from_surface(img, 128) if img.get_masks()[3] else None
        except (pygame.error, FileNotFoundError, OSError):
            _masks[key] = None
    return _masks[key]


def covered(lm, x, y):
    """Share of tile (x, y) hidden by this landmark's solid pixels, 0..1."""
    ax, ay, w, h = lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]
    if not (ax <= x < ax + w and ay <= y < ay + h) or lm.get("rotation"):
        return 0.0
    mask = _mask(lm["sprite_key"], w, h)
    if mask is None:
        return 0.0
    probe = pygame.mask.Mask((16, 16), fill=True)
    return mask.overlap_area(probe, ((x - ax) * 16, (y - ay) * 16)) / 256.0


def is_building(lm):
    return "assets/buildings" in str(lm["sprite_key"])


def clear_props_over_npcs(tilemap):
    """Remove every non-building, non-entrance prop drawn over an NPC's tile. Returns the
    number removed."""
    landmarks = getattr(tilemap, "landmarks", None)
    if not landmarks:
        return 0
    npcs = [(x, y) for y, row in enumerate(tilemap.interaction_layer)
            for x, kind in enumerate(row) if kind == "npc"]
    if not npcs:
        return 0
    doomed = []
    for lm in landmarks:
        if is_building(lm) or is_entrance_art(lm["sprite_key"]):
            continue
        if any(covered(lm, x, y) > COVER for (x, y) in npcs):
            doomed.append(lm)
    return remove_landmarks(tilemap, doomed)


def remove_landmarks(tilemap, doomed):
    """Take these landmarks off the map and free the tiles only they were blocking."""
    landmarks = tilemap.landmarks
    if not doomed:
        return 0
    keep = [lm for lm in landmarks if not any(lm is d for d in doomed)]

    def over(lm, x, y):
        return (lm["anchor_x"] <= x < lm["anchor_x"] + lm["width_tiles"]
                and lm["anchor_y"] <= y < lm["anchor_y"] + lm["height_tiles"])

    for lm in doomed:
        for y in range(lm["anchor_y"], lm["anchor_y"] + lm["height_tiles"]):
            for x in range(lm["anchor_x"], lm["anchor_x"] + lm["width_tiles"]):
                if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
                    continue
                if tilemap.collision_layer[y][x] == "landmark" and not any(over(k, x, y) for k in keep):
                    tilemap.collision_layer[y][x] = None
    landmarks[:] = keep
    return len(doomed)
