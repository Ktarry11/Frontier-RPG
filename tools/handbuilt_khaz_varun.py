"""
Hand-built Khaz Varun, the Black Hollow (190x200): the dead Dark Iron city. TWELVE BOSSES, two floors.

Kyle, 10 Nov: "the old dark iron city will have 12 bosses over 2 floors ... very rectangular with
lots of optional off-rooms."

ARCHETYPE: A CITY, NOT A CAVE. This is the Blackrock Depths slot, and the entire point of the
archetype is that it is BUILT - squared halls, dressed stone, a street you walk down. Every room
here is b.rect() masonry; the only carved space in the whole dungeon is the Ash Pits, which were a
natural fissure the dwarves dug into and then stopped using.

THE SHAPE: A SPINE AND ITS OFF-ROOMS, on each of two floors.

    FLOOR 1 - THE UPPER WORKS (south half). The Ember Road runs the full width of the map, and
    everything hangs off it. You can walk it end to end and fight four bosses; turn aside twice
    more and you fight six.
    FLOOR 2 - THE DEEPS (north half). The Deep Way does the same thing one level down, and ends at
    the Hall of Ashhold, where the thane's ancestor is.

FOUR OF THE TWELVE ARE OPTIONAL and sit in the off-rooms - Kyle's "lots of optional off-rooms", and
the standing rule that bosses are allowed to be skippable. A group taking the short run fights
eight; a group that wants everything fights twelve. Nothing on the spine can be skipped, so the
dungeon always has a shape.

EVERY BOSS TEACHES SOMETHING, and they are ordered so the lesson lands before it is needed:
    1  Gatewarden Hrun      dodge/parry wall        -> bring EXPERTISE
    3  Smelter-Master Vaud  damage sharing with adds -> kill the adds first
    5  Overseer Grall       a second actor holds his buff -> dispel or steal
    6  Forge-Lord Darrok    magic becomes his armour -> the casters have to stop
    9  Rock-Borer Queen     armour wall             -> bring ARMOUR PENETRATION
    10 Flamespeaker Maud    60 fire resist AND heals off fire -> spell pen, or change school
    12 Thane Morrun         all of it at once

Multi-boss, so trash is HAND-PLACED (TRASH -> zone.trash_spawns), which is the one place the
standing rule allows it. Roughly 3-4 pulls between bosses, flexible.

DRESS IT AS IT IS BUILT. The measured prop density across 58 existing interiors is 3.7-22.5 per
1,000 walkable tiles; the one hand-dressed interior is 135. A city dungeon that reads as a cave has
failed at the one thing the archetype is for. Still "less is more; logical for the room; a few
centrepieces".

HARD CONTRACTS (world/portal_manager.py)
  (95, 194) <-> Tempest Shallows (102, 76)   the collapsed gate, in the Shallows' south-west
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, disc

RU = "assets/tiles/ruins/"
BAKED = "assets/tiles/khaz_varun/baked"
W, H = 190, 200
PORTAL = (95, 194)

#: (x0, y0, x1, y1, chamfer, name). CHAMFERS ARE SMALL ON PURPOSE - Kyle asked for "very
#: rectangular", and at 4-6 the painter's blending rounded every hall into a lobe and the city
#: came out looking like more caves. Squared masonry: a Dark Iron hold is cut stone and right
#: angles, and the right angles are the whole visual argument against this being another cave.
ROOMS = {
    # ---- FLOOR 1: THE UPPER WORKS ----------------------------------------------------------
    "gate":     (78, 180, 112, 196, 1, "The Collapsed Gate"),
    "road":     (14, 158, 176, 176, 2, "The Ember Road"),
    "gatehall": (58, 136, 118, 156, 2, "The Gatehouse Hall"),
    "workshop": (14, 130, 52, 154, 1, "The Workshop"),
    "smelter":  (124, 130, 174, 156, 2, "The Smelter"),
    "magazine": (16, 106, 50, 126, 1, "The Powder Magazine"),
    "counting": (62, 108, 114, 130, 2, "The Counting Hall"),
    "forge":    (122, 100, 176, 126, 2, "The Great Forge"),
    # ---- FLOOR 2: THE DEEPS ----------------------------------------------------------------
    "deepway":  (14, 72, 176, 90, 2, "The Deep Way"),
    "cells":    (16, 48, 56, 68, 1, "The Cells"),
    "borer":    (120, 46, 174, 68, 2, "The Borer Workings"),
    "shrine":   (24, 20, 72, 44, 2, "The Shrine of Cinders"),
    "gallery":  (86, 20, 130, 44, 2, "The Shadow Gallery"),
    "hall":     (52, 4, 140, 18, 2, "The Hall of Ashhold"),
}

#: THE ASH PITS - the one CARVED space in the dungeon. A natural fissure the dwarves dug into and
#: then walled off, which is why it is the only room here with no right angle in it.
PITS = (78, 58, 18.0, 9.0, 0, 1.1)
PIT_BAYS = ((64, 52, 6.0, 4.5, 0, 2.3), (94, 52, 6.0, 4.5, 0, 0.7))

PATHS = {
    # EVERY END OF EVERY LINK SITS INSIDE THE SPACE IT JOINS, not on its rim. Drywhisker shipped
    # with all four on the edge and eleven markers - four bosses among them - came back
    # unreachable. A room's real extent is its rect; read it, do not eyeball it.
    "in":        ([(95, 190), (95, 182), (95, 170)], 6.0, 6.0),
    # floor 1: the spine's three doors north
    "hall_up":   ([(88, 162), (88, 152), (88, 146)], 5.4, 5.4),
    "shop_in":   ([(40, 162), (36, 152), (34, 144)], 4.6, 4.6),
    "smelt_in":  ([(148, 162), (150, 152), (150, 144)], 4.8, 4.8),
    "count_up":  ([(88, 140), (88, 128), (88, 120)], 5.0, 5.0),
    "mag_in":    ([(40, 140), (34, 130), (32, 118)], 4.4, 4.4),
    "forge_in":  ([(150, 134), (150, 126), (150, 114)], 5.0, 5.0),
    # THE GREAT STAIR, floor 1 to floor 2. It comes down at the forge end, so the whole of the
    # upper works sits between the door and the way down.
    "stair":     ([(150, 102), (152, 94), (150, 84)], 5.2, 5.2),
    # floor 2: the Deep Way and its doors
    "cells_in":  ([(38, 76), (36, 70), (36, 62)], 4.6, 4.6),
    "pits_in":   ([(78, 76), (78, 68), (78, 62)], 4.4, 4.4),
    "borer_in":  ([(148, 76), (148, 70), (148, 60)], 4.8, 4.8),
    "shrine_up": ([(48, 74), (48, 56), (48, 40)], 4.8, 4.8),
    "gall_up":   ([(108, 74), (108, 56), (108, 40)], 4.8, 4.8),
    "hall_in":   ([(96, 20), (96, 14), (96, 11)], 5.4, 5.4),
    "hall_w":    ([(48, 24), (56, 16), (64, 12)], 4.2, 4.2),
}

#: Rubble and furnaces: what turns two very long halls into a street with lanes rather than a
#: bowling alley. A Dark Iron road has stuff ON it.
BLOCKS = [
    (48, 166, 5, 3, 0), (96, 166, 4, 3, 0), (134, 166, 5, 3, 0), (168, 168, 4, 3, 0),
    (30, 168, 4, 3, 0), (116, 170, 4, 3, 0),
    (40, 80, 5, 3, 0), (92, 80, 4, 3, 0), (130, 80, 5, 3, 0), (166, 82, 4, 3, 0),
    (64, 82, 4, 3, 0),
    (76, 146, 3, 3, 0), (100, 146, 3, 3, 0),
    (142, 140, 3.2, 3.2, 0), (158, 140, 3.2, 3.2, 0),
    (70, 118, 3, 3, 0), (106, 118, 3, 3, 0),
    (136, 110, 3.4, 3.4, 0), (162, 110, 3.4, 3.4, 0),
    (40, 32, 3, 3, 0), (58, 32, 3, 3, 0), (98, 32, 3, 3, 0), (118, 32, 3, 3, 0),
]
#: Colonnades down the two spines - a hold's road is a vaulted gallery, not a trench.
COLONNADES = [((28, 44, 60, 76, 92, 108, 124, 140, 156, 170), (162, 172)),
              ((28, 44, 60, 76, 92, 108, 124, 140, 156, 170), (76, 86))]

BOSSES = {}
CHESTS = []
TRASH = []

#: (x, y, name, required). FOUR are optional and every one of them sits in an off-room.
BOSS_LIST = [
    # floor 1
    (88, 146, "Gatewarden Hrun", True),
    (32, 140, "The Crusher", False),
    (150, 142, "Smelter-Master Vaud", True),
    (32, 114, "Powderkeg Nix", False),
    (88, 118, "Overseer Grall", True),
    (150, 112, "Forge-Lord Darrok", True),
    # floor 2
    (36, 58, "The Iron Mask", True),
    (78, 58, "The Ashwretch Brood", False),
    (148, 56, "The Rock-Borer Queen", False),
    (48, 32, "Flamespeaker Maud", True),
    (108, 32, "The Shadow of the Forge", True),
    (96, 11, "Thane Morrun the Unmade", True),
]


def build_khaz_varun():
    zone = Tilemap("Khaz Varun, the Black Hollow", W, H,
                   "The old Dark Iron city under Tempest Isle: two floors of dressed stone, a "
                   "forge nobody banked, and whatever has been living in it.")
    zone.is_cave = True
    #: The PARENT OPEN ZONE, which is also the encounter-table key. "Tempest Isle" is prose and
    #: names no zone, so a dungeon keyed to it would resolve no table at all.
    zone.region = "Tempest Shallows"
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b

    for (x0, y0, x1, y1, ch, _n) in ROOMS.values():
        b.rect(x0, y0, x1, y1, chamfer=ch)
    # the one carved room
    cavern(b, *PITS)
    for bay in PIT_BAYS:
        cavern(b, *bay)
    # the forge's own apse, behind the anvil
    disc(b, 150, 104, 8, 0.4)
    for i, (pts, w0, w1) in enumerate(PATHS.values()):
        tube(b, pts, w0, w1, ph=0.3 + i * 0.6)

    import math as _m
    for (cx, cy, rx, ry, rot) in BLOCKS:
        c, s_ = _m.cos(_m.radians(rot)), _m.sin(_m.radians(rot))
        R = int(max(rx, ry)) + 2
        for yy in range(int(cy) - R, int(cy) + R + 1):
            for xx in range(int(cx) - R, int(cx) + R + 1):
                if not (0 <= xx < W and 0 <= yy < H):
                    continue
                dx, dy = xx - cx, yy - cy
                u, v = (c * dx + s_ * dy) / rx, (-s_ * dx + c * dy) / ry
                if u * u + v * v <= 1.0:
                    zone.collision_layer[yy][xx] = "wall"
                    zone.set_tile(xx, yy, "rock", "collision")
    for (xs, ys) in COLONNADES:
        for x in xs:
            for y in ys:
                if 0 <= x < W and 0 <= y < H:
                    zone.collision_layer[y][x] = "wall"
                    zone.set_tile(x, y, "rock", "collision")

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)

    fixed = []
    for (x, y, n, _req) in BOSS_LIST:
        if not zone.is_walkable(x, y):
            raise AssertionError(("boss in solid rock", n, x, y))
        L.mark("boss_marker", x, y)
        fixed.append((x, y, n))
    BOSSES.clear()
    BOSSES.update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (96, 11)
    zone.boss_positions = list(fixed)

    chests = [(24, 140), (166, 148), (24, 112), (166, 108), (70, 150),
              (24, 60), (164, 58), (30, 26), (122, 26), (64, 10), (128, 10)]
    for c in chests:
        if not zone.is_walkable(*c):
            raise AssertionError(("chest in solid rock", c))
        L.mark("chest", *c)
    CHESTS[:] = chests

    zone.add_subzone("Khaz Varun", 0, 0, W, H)
    for (x0, y0, x1, y1, _ch, name) in ROOMS.values():
        zone.add_subzone(name, x0 - 2, y0 - 2, (x1 - x0) + 4, (y1 - y0) + 4)
    zone.add_subzone("The Ash Pits", 56, 46, 44, 26)
    return zone, L


def _trash():
    """Hand-placed, three to four pulls between bosses."""
    T = []

    def pack(lvl, *spots):
        for (x, y, m) in spots:
            T.append((x, y, m, lvl))

    # ---- the Ember Road, in from the gate -------------------------------------------------
    pack(51, (95, 176, "Ashclaim Trespasser"), (90, 172, "Crazed Miner"), (100, 172, "Crazed Miner"))
    pack(51, (60, 168, "Crazed Miner"), (54, 165, "Masked Zealot"), (66, 165, "Crazed Miner"))
    pack(51, (130, 168, "Crazed Miner"), (136, 165, "Masked Zealot"), (124, 165, "Crazed Miner"))
    # ---- to Gatewarden Hrun ----------------------------------------------------------------
    pack(52, (88, 158, "Iron Golem"), (82, 155, "Masked Zealot"), (94, 155, "Masked Zealot"))
    # ---- the Workshop (optional) -----------------------------------------------------------
    pack(52, (40, 150, "Clockwork Sentry"), (34, 148, "Steam Automaton"), (46, 147, "Clockwork Sentry"))
    # ---- the Smelter -----------------------------------------------------------------------
    pack(52, (140, 150, "Slag Ooze"), (152, 150, "Slag Ooze"), (146, 146, "Ash-Wretch"))
    pack(52, (160, 152, "Chained Berserker"), (166, 148, "Ash-Wretch"))
    # ---- the Counting Hall ------------------------------------------------------------------
    pack(53, (76, 126, "Masked Zealot"), (88, 126, "Iron Hound"), (100, 126, "Masked Zealot"))
    pack(53, (70, 114, "Iron Golem"), (106, 114, "Iron Golem"))
    # ---- the Powder Magazine (optional) -----------------------------------------------------
    pack(53, (30, 122, "Chained Berserker"), (24, 118, "Ash-Wretch"), (38, 118, "Ash-Wretch"))
    # ---- the Great Forge --------------------------------------------------------------------
    pack(53, (138, 120, "Stone Golem"), (150, 122, "Forge Titan"), (162, 120, "Stone Golem"))
    pack(54, (144, 108, "Shadow of the Forge"), (158, 108, "Molten Thane"))
    # ---- the Great Stair, and the Deep Way ---------------------------------------------------
    pack(54, (150, 94, "Iron Hound"), (144, 88, "Deep Spider"), (156, 88, "Deep Spider"))
    pack(54, (120, 82, "Rock Borer"), (112, 80, "Rock Borer"), (128, 80, "Deep Spider"))
    pack(54, (70, 82, "Ash-Wretch"), (62, 80, "Crazed Miner"), (78, 80, "Ash-Wretch"))
    pack(54, (28, 82, "Masked Zealot"), (22, 80, "Fire-Worshipper"), (34, 80, "Masked Zealot"))
    # ---- the Cells ----------------------------------------------------------------------------
    pack(54, (44, 64, "Chained Berserker"), (28, 62, "Ash-Wretch"), (50, 60, "Ash-Wretch"))
    # ---- the Borer Workings (optional) --------------------------------------------------------
    pack(54, (136, 62, "Rock Borer"), (160, 62, "Rock Borer"), (148, 66, "Deep Spider"))
    # ---- up to the Shrine ----------------------------------------------------------------------
    pack(55, (48, 62, "Fire-Worshipper"), (42, 54, "Fire-Worshipper"), (54, 54, "Masked Zealot"))
    pack(55, (36, 38, "Fire-Worshipper"), (60, 38, "Fire-Worshipper"), (48, 42, "Molten Thane"))
    # ---- up to the Shadow Gallery ---------------------------------------------------------------
    pack(55, (108, 62, "Shadow of the Forge"), (102, 54, "Deep Spider"), (114, 54, "Deep Spider"))
    pack(55, (96, 38, "Shadow of the Forge"), (120, 38, "Iron Hound"))
    # ---- the Hall of Ashhold ----------------------------------------------------------------------
    pack(56, (80, 14, "Molten Thane"), (112, 14, "Molten Thane"), (96, 18, "Forge Titan"))
    return T


def _snap(zone, spots, rad=5):
    """Pull any trash spot that landed in masonry out to the nearest open floor.

    Bosses and chests are asserted walkable and must be fixed by hand - they are placed
    deliberately. Trash is a scatter, and a pack member a tile inside a pillar is not worth a
    hand edit; what matters is that every mob in a pull can actually be fought. Same helper
    Stromgarde uses, and for the same reason.
    """
    out = []
    for (x, y, m, lvl) in spots:
        if zone.is_walkable(x, y):
            out.append((x, y, m, lvl)); continue
        best = None
        for r in range(1, rad + 1):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height and zone.is_walkable(nx, ny):
                        d = dx * dx + dy * dy
                        if best is None or d < best[0]:
                            best = (d, nx, ny)
            if best:
                break
        if best is None:
            raise AssertionError(("trash with no open floor within reach", m, x, y))
        out.append((best[1], best[2], m, lvl))
    return out


def build_khaz_varun_baked():
    """The map WITHOUT register_baked, for the baker to paint from.

    tools/bake_tempest_dungeons.py calls this; generate_khaz_varun() is what the game calls, and
    it registers the baked chunks that this function's output was used to produce. Calling the
    registering one from the baker is a chicken-and-egg - it refuses to build until the art it is
    about to make already exists.
    """
    # bake_spec unpacks (zone, layout), so hand back both rather than just the map.
    return build_khaz_varun()


def generate_khaz_varun():
    zone, L = build_khaz_varun()
    TRASH[:] = _snap(zone, _trash())
    zone.trash_spawns = list(TRASH)
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z = generate_khaz_varun()
    print(z.name, z.width, "x", z.height, "| bosses", len(z.boss_positions),
          "| trash", len(z.trash_spawns))
