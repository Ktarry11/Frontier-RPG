"""Furniture for dungeon interiors, applied at load the way trash packs are.

tools/dress_dungeons.py writes data/dungeons/dressing.json; create_all_zones()
calls apply_dressing() to attach it.

WHY A DATA FILE AND NOT THE ZONE MODULES. Fifty-eight interiors are built by
fifty-eight different modules, most of them generated rather than hand-written,
and the dressing is a density pass over all of them at once - something you want
to re-run and re-tune as a whole, not re-type in fifty-eight places. Same
argument that put trash packs in a file, and it is the same seam, so a dungeon
that has neither still loads.

EVERY PIECE IS NON-SOLID. A dressing pass that can block a corridor is a dressing
pass that can make a boss unreachable, and the thing being fixed here is how the
rooms LOOK. Collision stays the business of the module that built the room.
"""
import json
import os

DRESSING_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "dungeons", "dressing.json")


def load_dressing():
    try:
        with open(DRESSING_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def apply_dressing(zones):
    """Attach generated furniture. Idempotent: a zone already dressed is skipped,
    so calling this twice cannot double a room's props."""
    data = load_dressing()
    applied = 0
    for name, pieces in data.items():
        zone = zones.get(name)
        if zone is None or getattr(zone, "_dressed", False):
            continue
        for p in pieces:
            try:
                zone.add_landmark(p["sprite"], p["x"], p["y"], p["w"], p["h"], solid=False)
            except Exception:
                continue
        zone._dressed = True
        applied += len(pieces)
    return applied
