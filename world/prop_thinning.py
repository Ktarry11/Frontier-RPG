"""Fewer props where a map is swamped with them.

Kyle, 10 Nov 2026: "~30% fewer props in Arathi dungeons and caves" - Boulderfist Hall is
"swamped with props", Drywhisker has too many. "Keep the ones that tell you where you are,
drop filler." Also the Gadgetzan ruins ("a dumping ground of bad props") and the Drownbell.

One pass over the finished map, like world/npc_clearance.py: the hand-built layouts stay as
written and this takes a share of the FILLER out. Filler is a prop whose sprite appears more
than once on the map - the sixth skull pile, the ninth ore cart. A sprite that appears once is
a landmark that tells you where you are and is never removed; nor is a building, entrance art,
or anything standing next to a door.

Which copies go is decided by position, not by chance, so the map is the same every run.
"""
import os

from world.npc_clearance import is_building, remove_landmarks
from world.portal_art import is_entrance_art

#: map name -> share of its repeated props to remove
THIN = {
    "Boulderfist Hall": 0.30, "Boulder'gor": 0.30, "Drywhisker Deeps": 0.30, "Stromgarde Keep": 0.30,
    "The Drowned Barrow": 0.30, "Wrackline Hold": 0.30, "The Tidewrack": 0.30,
    "The Drownbell": 0.30,
}
#: map name -> (subzone, share): only the props inside that subzone are thinned
THIN_SUBZONE = {"Northern Tanaris": ("Gadgetzan Ruins", 0.40)}


def _rank(lm):
    """A stable number per prop: the same copies go every time."""
    return (lm["anchor_x"] * 7919 + lm["anchor_y"] * 104729 + len(os.path.basename(lm["sprite_key"]))) % 1000


def thin_props(tilemap, share, subzone=None):
    """Remove about `share` of the map's props (or of one subzone's), taking only repeated
    filler. Returns the count."""
    landmarks = getattr(tilemap, "landmarks", None)
    if not landmarks or share <= 0:
        return 0
    rects = [s for s in getattr(tilemap, "subzones", []) if s.get("name") == subzone] if subzone else None

    def inside(lm):
        if rects is None:
            return True
        cx, cy = lm["anchor_x"] + lm["width_tiles"] / 2, lm["anchor_y"] + lm["height_tiles"] / 2
        return any(r["x"] <= cx <= r["x"] + r["w"] and r["y"] <= cy <= r["y"] + r["h"] for r in rects)
    doors = [(x, y) for y, row in enumerate(tilemap.interaction_layer)
             for x, kind in enumerate(row) if kind in ("portal", "boat")]
    by_sprite = {}
    for lm in landmarks:
        if is_building(lm) or is_entrance_art(lm["sprite_key"]) or not inside(lm):
            continue
        cx, cy = lm["anchor_x"] + lm["width_tiles"] / 2, lm["anchor_y"] + lm["height_tiles"] / 2
        if any(abs(cx - x) + abs(cy - y) <= 5 for x, y in doors):
            continue                                  # what frames a door stays
        by_sprite.setdefault(lm["sprite_key"], []).append(lm)
    want = round(sum(1 for lm in landmarks if inside(lm)) * share)
    doomed = []
    # take from the most-repeated sprites first, always leaving at least one of each
    groups = sorted(by_sprite.values(), key=len, reverse=True)
    while len(doomed) < want:
        took = False
        for group in groups:
            left = [lm for lm in group if not any(lm is d for d in doomed)]
            if len(left) > 1 and len(doomed) < want:
                doomed.append(min(left, key=_rank))
                took = True
        if not took:
            break
    return remove_landmarks(tilemap, doomed)


def thin_all(zones):
    """Apply THIN to the finished zones. Returns {name: removed}."""
    out = {}
    for name, share in THIN.items():
        entry = zones.get(name)
        if entry is not None:
            out[name] = thin_props(entry["tilemap"], share)
    for name, (subzone, share) in THIN_SUBZONE.items():
        entry = zones.get(name)
        if entry is not None:
            out[name] = thin_props(entry["tilemap"], share, subzone)
    return out
