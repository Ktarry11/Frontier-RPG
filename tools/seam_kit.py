"""
The seam archetype, shared by the two halves of the Glittervein dungeon.

    tools/handbuilt_mother_vein.py   the upper half, three bosses and a shaft
    tools/handbuilt_cistern.py       the lower half, four bosses and the outflow

A seam is a fracture network, and the one thing fracture networks do that neither a corridor nor a
warren does is ANASTOMOSE: split around whatever would not break and rejoin on the far side. So the
galleries always come in pairs, and this module is the one place that decides where a pair runs.

ONE IMPLEMENTATION, DELIBERATELY. The verifier severs a gallery by rebuilding the map without it,
and both maps and the verifier all read the paths from here. The first version of that test kept
its own copy of the corridor walk, landed on slightly different tiles, and let every negative
control pass through the slivers it missed - which is the same failure as tile_kind disagreeing
with fields, and the same failure as a lane drawn in one radius over a cliff cut in another. Two
implementations of one rule is the recurring bug in this codebase.
"""


def bow_paths(nodes, bows):
    """[(segment, bow, points)] - the pairs of galleries between consecutive nodes.

    FOUR POINTS, NOT THREE. A single waypoint at mid-height is not a bow, it is a zigzag: the
    second leg of the left gallery sweeps all the way back across the segment and straight through
    where the right one is, so the pair merges into one wide ribbon and the map has a third route
    everywhere. Offsetting at BOTH the one-third and two-thirds heights keeps each gallery on its
    own side, and the two meet only at the vugs they join.

    The bends are CORNERS. A fracture turns sharply or not at all; a smooth curve is a thing water
    cut, and the water arrived long after the crack did.
    """
    out = []
    for i in range(len(nodes) - 1):
        (ax, ay), (bx, by) = nodes[i], nodes[i + 1]
        y1 = ay + (by - ay) // 3
        y2 = ay + 2 * (by - ay) // 3
        for bow in bows[i]:
            out.append((i, bow, [(ax, ay), (ax + bow, y1), (bx + bow, y2), (bx, by)]))
    return out


def clearances(nodes, vugs, rooms=()):
    """[(label, gap)] - vertical gap between each chamber and the next one up.

    THIS IS THE THING THAT ACTUALLY HAS TO BE LAID OUT, and it was twice patched instead. If two
    chambers touch, the player walks from one to the other and the galleries between them carry
    nothing - the map still looks like a seam, and the single-gallery severing test still passes
    every time, because with a gallery gone you simply go the short way. Both halves of this
    dungeon had that bug and only the negative control found it.

    `rooms` takes extra (label, y0, y1) boxes that are not vugs - a rect gallery, an entry hall.
    """
    spans = [(f"vug@{nodes[i][1]}", nodes[i][1] - ry, nodes[i][1] + ry) for (i, _rx, ry) in vugs]
    spans += [(lab, y0, y1) for (lab, y0, y1) in rooms]
    spans.sort(key=lambda s: -s[1])
    out = []
    for lower, upper in zip(spans, spans[1:]):
        out.append((f"{lower[0]} -> {upper[0]}", lower[1] - upper[2]))
    return out
