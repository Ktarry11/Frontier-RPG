"""The Pathfinder's Lantern: carry it and the ground you can walk on lights up for two tiles round you.

Kyle, 27 Nov 2026: "a brand new item sold for about 1500g that, when you own it, it lights up any path within a 2x2
radius of you (to prevent you from needing to walk into every single wall to find hidden secrets)."

It lights every walkable tile within two tiles (a circle, 21 tiles), whatever it's drawn as, so a passage that's drawn
as rock or trees but can be walked (world/secrets.py) glows like the ground beside it. It shows nothing further away
and puts nothing on the map: you still have to walk past the wall to see it. Owned means anywhere the party keeps
things: a member's bags, what they're wearing, or the bank. Sold by Scout Windrider in Orgrimmar.
"""
import time

LANTERN_ID = "pathfinders_lantern"
RADIUS = 2
#: how often ownership is looked up again (a bank search every frame would be wasteful)
RECHECK_SECONDS = 1.0

_cache = {"at": -1e9, "owned": False}


def _party():
    try:
        from world.market.market import _LIVE
        return _LIVE.get("party")
    except Exception:
        return None


def owns_lantern(player=None, party=None, now=None):
    now = time.monotonic() if now is None else now
    if party is None and now - _cache["at"] < RECHECK_SECONDS:
        return _cache["owned"]
    from world.collection import _all_items
    owned = any(getattr(it, "consumable_id", None) == LANTERN_ID or getattr(it, "item_id", None) == LANTERN_ID
                for it in _all_items(party if party is not None else _party(), player))
    if party is None:
        _cache.update(at=now, owned=owned)
    return owned


def forget():
    """Look again next frame (after buying or selling one)."""
    _cache["at"] = -1e9


def lit_tiles(tilemap, px, py, radius=RADIUS):
    """[(x, y, strength)] for every walkable tile within `radius` of (px, py); strength is 1 at your feet, less out
    toward the edge."""
    out = []
    r2 = radius * radius + 1          # a round circle: the 5 by 5 square without its four corners
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            d2 = dx * dx + dy * dy
            if d2 > r2:
                continue
            x, y = px + dx, py + dy
            if tilemap.is_walkable(x, y):
                out.append((x, y, 1.0 - 0.18 * (d2 ** 0.5)))
    return out
