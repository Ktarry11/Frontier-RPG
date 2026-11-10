"""ONE island, defined ONCE, shared by both Tempest Isle zone modules.

=========================================================================================
WHY THIS FILE EXISTS
=========================================================================================

Kyle, 10 Nov: "Bro look at the SHAPE i sent you."

The first build gave each zone its own coastline. That is two islands, not one, and it fails
in two ways at once:

  1. THE SEAM DOES NOT JOIN. The Shallows was 170 wide and the Reach 190, each with its own
     closed lobe, so the land either side of the border had no relationship at all. Walking
     across the seam, the coast would jump.
  2. THE SHAPE WAS WRONG. Kyle's drawing is not a blob. It is deeply lobed - big rounded
     headlands separated by bays that bite most of the way in, a notch on the north-east that
     the town sits inside, and a long tail sweeping away to the south-west. Two independent
     smooth ellipses cannot produce that and did not.

So the island is defined here, in ISLAND SPACE, and each zone samples its own half:

        island y    0 ..170   THE ASHEN REACH     (55-58)   zone y = island y
        island y  170 ..320   TEMPEST SHALLOWS    (52-55)   zone y = island y - 170

Both zones are the SAME WIDTH, which is what makes the border continuous: the land at island
y=170 is one row, read by the Reach as its bottom row and by the Shallows as its top row.

THE VOLCANO SITS EXACTLY ON THE SEAM, at island (100,170) - the drawing has the dashed border
line running straight through the middle of it. That is also why it is defined here rather than
in either zone: a mountain half-owned by two modules drifts the moment one of them is edited.
"""
import numpy as np

from tools.tirisfal_kit import wob

#: Both zones. Equal width is the whole point - see the seam note above.
W = 230
REACH_H = 160
SHALLOWS_H = 140
TOTAL_H = REACH_H + SHALLOWS_H          # 300
SEAM_Y = REACH_H                        # island y of the border

#: Island-space centre. Just below the seam, because the southern half carries the long tail.
#: Tuned so there is OPEN SEA on all four sides of the island: at CY=158 the south coast ran
#: straight off the bottom edge of the Shallows, which would have given that zone a hard map
#: border where it is supposed to have a beach.
CX, CY = 115.0, 165.0
#: The island is much taller than it is wide in island space (230 x 300), so y is squashed
#: before the radius is taken. Without this the coast is an egg instead of a country.
SQUASH = 0.64
#: Horizontal clamp. The radius harmonics below can peak past the map's half-width if several
#: line up; clamping keeps sea on the east and west edges of BOTH zones no matter what they do.
R_MAX = 102.0

VOLCANO = (115.0, float(SEAM_Y))
#: Deliberately modest. At 46 against this island it ate a third of the land and stopped being a
#: feature on a map - it became the map.
VOLCANO_R = 36.0

#: Island-space islets - the cluster off the south, on the Shallows' side. The drawing has a
#: scatter of seven, not a tidy line of four.
ISLETS = [(176.0, 254.0, 9.0, 6.5), (194.0, 244.0, 7.0, 5.0), (186.0, 270.0, 6.5, 5.0),
          (204.0, 262.0, 5.5, 4.5), (166.0, 272.0, 6.0, 4.5), (200.0, 280.0, 5.0, 4.0),
          (180.0, 286.0, 4.5, 3.5)]


def island_field(ix, iy):
    """>0 on land, <0 at sea, in ISLAND space. The one coastline.

    Integer harmonics only, so the curve closes on itself exactly where it wraps. The amplitudes
    are large on purpose: this coast is meant to read as headlands and bays, and a timid wobble
    is what produced the blob Kyle rejected.
    """
    ix = np.asarray(ix, float)
    iy = np.asarray(iy, float)
    dx = ix - CX
    dy = (iy - CY) * SQUASH
    d = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    # THE NORTH HALF MUST BE THE BIGGER ONE. Kyle, 10 Nov: "the top one has more landmass! this
    # is why we added islands in the southern one". The first pass had it backwards - the Shallows
    # carried 21,000 land tiles against the Reach's 13,000, which makes the islets pointless,
    # because they exist precisely to give the SMALLER southern map the area the north gets from
    # open ground. The primary lean below peaks due NORTH for exactly this reason.
    r = (76.0
         + 14.0 * np.sin(th + 3.0)          # fat north, tapering to the southern tail
         + 14.0 * np.sin(2 * th + 0.6)      # the two big bays, biting most of the way in
         + 9.0 * np.sin(3 * th + 1.9)       # the headlands between them
         + 6.0 * np.sin(5 * th - 0.8))      # the notch the town sits inside, and a ragged edge
    r = np.minimum(r, R_MAX)
    return (r - d) + 2.0 * wob(ix * 0.45, iy * 0.45)


def islet_field(ix, iy):
    """>0 on an islet, in ISLAND space."""
    ix = np.asarray(ix, float)
    iy = np.asarray(iy, float)
    p = np.full(np.shape(ix), -99.0)
    for (cx, cy, rx, ry) in ISLETS:
        e = 1.0 - np.sqrt(((ix - cx) / rx) ** 2 + ((iy - cy) / ry) ** 2)
        p = np.maximum(p, e * min(rx, ry) + 0.45 * wob(ix * 1.2, iy * 1.2))
    return p


def volcano_field(ix, iy, door=None):
    """>0 inside the volcano's skirt, in ISLAND space.

    `door` is (x, y, radius) in island space - a bite taken out of the skirt so the forecourt in
    front of the Emberdeep is walkable ground. A portal tile inside solid rock is a player who
    cannot reach their own dungeon.
    """
    ix = np.asarray(ix, float)
    iy = np.asarray(iy, float)
    cx, cy = VOLCANO
    d = np.sqrt((ix - cx) ** 2 + (iy - cy) ** 2)
    band = (VOLCANO_R - d) + 2.6 * wob(ix * 0.55, iy * 0.55) + 1.1 * wob(ix * 1.3, iy * 1.3)
    if door is not None:
        dx, dy, r = door
        cut = r - np.sqrt((ix - dx) ** 2 + (iy - dy) ** 2)
        band = np.where(cut > 0, np.minimum(band, -1.0), band)
    return band


def land(zone_key, gx, gy):
    """Land field for a zone, in that zone's own tile coordinates."""
    return island_field(gx, gy + _offset(zone_key))


def islets(zone_key, gx, gy):
    return islet_field(gx, gy + _offset(zone_key))


def volcano(zone_key, gx, gy, door=None):
    return volcano_field(gx, gy + _offset(zone_key), door)


def _offset(zone_key):
    if zone_key == "ashen_reach":
        return 0.0
    if zone_key == "tempest_shallows":
        return float(SEAM_Y)
    raise KeyError(f"unknown Tempest Isle zone {zone_key!r}")
