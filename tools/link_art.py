"""Draw a map's links (world/links.py) with Kyle's LK1 sheet (docs/caelora_link_art_prompts.md).

    from tools.link_art import dress_links
    dress_links(L.z, LINKS, pads={"skipstone": "lk_skipstone_failing"})

Each pad gets its pad art centred on the pad tile (a flat thing you stand on: every character draws over it), and a
current gets its ribbon laid over the gap between its two pads, turned to the nearest 30 degrees (the turned ribbons are
made by tools/slice_building_sheet.mirror_link_ribbons). The art is drawn, not walked: the drop under a ribbon stays a
drop, and the link itself is what carries you.
"""
import math

from PIL import Image

SKP = "assets/tiles/sky/props/"

#: the default pad art for each kind
PADS = {"skipstone": "lk_skipstone", "wind": "lk_updraft", "dusk_wind": "lk_updraft"}
#: the ribbon each current lays over its gap (None: nothing over the gap)
RIBBONS = {"skipstone": None, "wind": "lk_wind", "dusk_wind": "lk_dusk_wind"}
#: pad width in tiles; a ribbon stops this far short of each pad
PAD_W = 5


def _size(name):
    return Image.open(f"{SKP}{name}.png").size


def _ribbon(base, ang):
    """The file for a ribbon running at `ang` degrees (counter-clockwise from right), to the nearest 30."""
    a = int(round(ang / 30.0)) * 30 % 180
    return f"{base}_h" if a == 0 else f"{base}_{a}"


def dress_links(z, links, pads=None, ribbons=None):
    pads = {**PADS, **(pads or {})}
    ribbons = {**RIBBONS, **(ribbons or {})}
    for kind, a, b in links:
        art = pads[kind]
        iw, ih = _size(art)
        w = PAD_W
        h = max(1, round(w * ih / iw))
        for (x, y) in (a, b):
            z.add_landmark(f"{SKP}{art}.png", x - w // 2, y - h + 2, w, h, solid=False)
        base = ribbons.get(kind)
        if not base:
            continue
        dx, dy = b[0] - a[0], b[1] - a[1]
        dist = math.hypot(dx, dy)
        ang = math.degrees(math.atan2(-dy, dx)) % 180
        name = _ribbon(base, ang)
        rw, rh = _size(name)
        span = max(4.0, dist - PAD_W)
        # scale so the ribbon's long axis covers the span: for a turned ribbon that's its bounding box's diagonal run
        run = abs(math.cos(math.radians(ang))) * rw + abs(math.sin(math.radians(ang))) * rh
        k = span / max(run, 1.0)
        tw, th = max(2, round(rw * k)), max(2, round(rh * k))
        mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
        z.add_landmark(f"{SKP}{name}.png", int(round(mx - tw / 2)), int(round(my - th / 2)), tw, th, solid=False)
