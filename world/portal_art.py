"""Which sprites are ENTRANCE ART - allowed to stand over a portal or boat tile.

A way out of a zone should be framed by something that looks like a way out: a cave mouth, a
gate, an arch, a zeppelin tower, a moored boat. Anything else drawn over the tile - a tree, a
watchtower, a tide pool - is a prop that landed on a door.

One definition, used by the layout kit (which refuses to place a non-entrance prop over an
exit) and by tools/qa_portals.py (which fails the build if one is there anyway), so the two
cannot disagree about what counts.
"""
import os
import re

_ENTRANCE = re.compile(
    r"^(ent_|entrance_|cave_entrance|zeppelin|"
    r"uc_skull_arch|uc_portcullis|uc_elevator|"
    r"palisade_gatehouse|orc_great_gatehouse|"
    r"vot_rock_arch|gob_mine_frame|ruin_wall_arch|ruin_archway|"
    r"stv_liana_arch|stv_bone_arch|tiragarde_drawbridge|sf_start_gantry|bridge_plank|"
    # a boat is the entrance art for a boat crossing
    r"boat_|ash_orc_skiff|bloodsail_galleon)"
)


def is_entrance_art(sprite_key):
    """True if this sprite may legitimately cover a portal / boat tile."""
    return bool(_ENTRANCE.match(os.path.basename(str(sprite_key)).lower()))


def clear_exits(tilemap):
    """Remove every non-entrance sprite drawn over a portal or boat tile. Returns the number
    removed.

    THE SAFETY NET, run once on every map as it is created. The game has at least four
    different layout kits and each decides for itself where a prop may go - most by testing
    the sprite's solid base, none by testing the whole rectangle it is DRAWN in. So a tree
    rooted three tiles from a zone's edge hangs its canopy across the gate, a randomly dressed
    dungeon drops a broken column on its own exit, and the door is walkable and invisible.
    Rather than teach every kit the same rule (and the next kit after them), the rule is
    enforced here, on the finished map, where no generator can get round it.

    A removed sprite's "landmark" collision tiles are cleared too, unless another sprite
    still stands on them - otherwise the prop would be gone and its invisible wall left
    behind.
    """
    landmarks = getattr(tilemap, "landmarks", None)
    if not landmarks:
        return 0
    exits = [(x, y) for y, row in enumerate(tilemap.interaction_layer)
             for x, kind in enumerate(row) if kind in ("portal", "boat")]
    if not exits:
        return 0

    def covers(lm, x, y):
        return (lm["anchor_x"] <= x < lm["anchor_x"] + lm["width_tiles"]
                and lm["anchor_y"] <= y < lm["anchor_y"] + lm["height_tiles"])

    doomed = [lm for lm in landmarks
              if not is_entrance_art(lm["sprite_key"]) and any(covers(lm, x, y) for x, y in exits)]
    if not doomed:
        return 0
    keep = [lm for lm in landmarks if not any(lm is d for d in doomed)]
    for lm in doomed:
        for y in range(lm["anchor_y"], lm["anchor_y"] + lm["height_tiles"]):
            for x in range(lm["anchor_x"], lm["anchor_x"] + lm["width_tiles"]):
                if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
                    continue
                if tilemap.collision_layer[y][x] == "landmark" and not any(covers(k, x, y) for k in keep):
                    tilemap.collision_layer[y][x] = None
    landmarks[:] = keep
    return len(doomed)
