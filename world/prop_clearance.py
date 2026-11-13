"""No two props stand on the same ground.

Kyle, 10 Nov 2026 ([83]): "Randomly dropped overlapping props" - ruined pillars dropped on a tent.

A prop's position lives in whichever zone module, scatter loop or set-piece list put it there, and
120 maps have been dressed by a dozen different passes. So, like world/npc_clearance.py and
world/portal_art.clear_exits, the rule is enforced once, on each finished map, where no generator
can get round it: where two props share a FOOTPRINT, the lesser one goes.

FOOTPRINT, NOT PICTURE. A crate in front of a tent is drawn over the tent's wall, and that is just
how a top-down scene looks. What is wrong is two things on the same ground, so only the bottom of
each sprite - where it meets the floor - is compared.

WHAT IS LEFT ALONE: anything that grows (a thicket overlaps on purpose), rock against rock (that
is a rock pile), entrance art, and a pair of buildings (tools/qa_building_overlap.py owns those
and they are fixed by moving one, not deleting it).

WHICH ONE GOES: never a building; otherwise the one with fewer solid pixels.
"""
import re

import pygame

from world.npc_clearance import is_building, remove_landmarks
from world.portal_art import is_entrance_art

#: A pair counts when the shared footprint is more than this share of the smaller one.
OVER = 0.40
#: How much of a sprite, from the bottom up, is where it stands.
BASE = 0.35

#: Things that grow, lie flat, or are meant to stand in a run.
SOFT = re.compile(
    r"tree|palm|pine|aspen|oak|acacia|willow|birch|bamboo|shroom|mushroom|fung|fern|grass|bush|"
    r"shrub|scrub|thorn|vine|moss|lily|cattail|reed|flower|weed|kelp|coral|cactus|saguaro|sage|"
    r"root|stump|log|deadfall|snag|sapling|canopy|frond|ivy|lichen|web|mangrove|hibiscus|banana|"
    r"huckleberry|fireweed|thicket|tussock|krummholz|"
    r"puddle|pool|crack|fissure|rug|circle|rune_floor|shadow|glow|light|ember|smoke|"
    r"streamers|banner|rope_railing|fence|wall_section|palisade|bridge|plank|deck|stair|ramp", re.I)
#: Rock on rock is a rock pile. Only compared against something made.
ROCK = re.compile(r"rock|boulder|spire|stone|stack|stalag|crystal|rubble|slag|cairn|bramble|"
                  r"obelisk|bones|skull|rib", re.I)

_feet = {}


def _name(lm):
    return str(lm["sprite_key"]).split("/")[-1]


def footprint(lm):
    """(mask of the sprite's bottom band at 16px a tile, solid pixels in the whole sprite)."""
    key = (lm["sprite_key"], lm["width_tiles"], lm["height_tiles"])
    if key not in _feet:
        try:
            img = pygame.image.load(lm["sprite_key"])
            img = pygame.transform.scale(img, (lm["width_tiles"] * 16, lm["height_tiles"] * 16))
            if not img.get_masks()[3]:
                raise ValueError("no alpha")
            whole = pygame.mask.from_surface(img, 128)
            w, h = whole.get_size()
            band = max(8, int(h * BASE))
            strip = pygame.mask.Mask((w, h))
            strip.draw(pygame.mask.Mask((w, band), fill=True), (0, h - band))
            _feet[key] = (whole.overlap_mask(strip, (0, 0)), whole.count())
        except (pygame.error, FileNotFoundError, OSError, ValueError):
            _feet[key] = (None, 0)
    return _feet[key]


def considered(lm):
    return (not SOFT.search(_name(lm)) and not lm.get("rotation")
            and not is_entrance_art(lm["sprite_key"]))


def shared_ground(tilemap):
    """[(share, a, b)] for every pair of props standing on the same ground."""
    lms = [lm for lm in (getattr(tilemap, "landmarks", None) or []) if considered(lm)]
    out = []
    for i, a in enumerate(lms):
        fa, _na = footprint(a)
        if fa is None:
            continue
        for b in lms[i + 1:]:
            if (a["anchor_x"] >= b["anchor_x"] + b["width_tiles"]
                    or b["anchor_x"] >= a["anchor_x"] + a["width_tiles"]
                    or a["anchor_y"] >= b["anchor_y"] + b["height_tiles"]
                    or b["anchor_y"] >= a["anchor_y"] + a["height_tiles"]):
                continue
            if ROCK.search(_name(a)) and ROCK.search(_name(b)):
                continue
            if is_building(a) and is_building(b):
                continue
            fb, _nb = footprint(b)
            if fb is None:
                continue
            shared = fa.overlap_area(fb, ((b["anchor_x"] - a["anchor_x"]) * 16,
                                          (b["anchor_y"] - a["anchor_y"]) * 16))
            small = min(fa.count(), fb.count())
            if small and shared / small > OVER:
                out.append((shared / small, a, b))
    return out


def clear_props_through_props(tilemap):
    """Remove the lesser prop of every pair sharing ground. Returns the number removed."""
    doomed = []
    for (_share, a, b) in shared_ground(tilemap):
        if any(a is d or b is d for d in doomed):
            continue                      # one of them is already going; the pair is settled
        if is_building(a):
            loser = b
        elif is_building(b):
            loser = a
        else:
            loser = a if footprint(a)[1] <= footprint(b)[1] else b
        doomed.append(loser)
    return remove_landmarks(tilemap, doomed)
