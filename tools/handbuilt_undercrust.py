"""
The Undercrust (120x110): the hive under the salt pan. Levels 39-41. The Shimmering Flats' one cave.

TWO ENTRANCES, AND THEY DO NOT ARRIVE IN THE SAME PLACE.

Kyle: "the cave will have two entrances in the overworld and each entrance will take us to a different
part in the cave. A lot of wow silithid things do this already and we dont have this yet where we have
two entrances in the real world into the same cave."

He is right that nothing in this game does it. Every cave, keep and dungeon built so far is a pocket with
one mouth, and the only thing you can do with one mouth is go in and come back out of it. A hive is not
shaped like that - it is a warren with holes wherever the roof gave way, and in WoW you learn a silithid
hive by discovering that the hole on the far side of the map comes out somewhere you have already been.

    THE CRUSTFALL   (Flats 92, 140)  -> arrives WEST, at the shallow end, near Crustbreak
    THE DEEP SHAFT  (Flats 172, 116) -> arrives EAST, at the deep end, under the Deep Mound

THE TWO ENDS ARE NOT EQUIVALENT, which is what makes it worth building. The Crustfall is a roof collapse
on the near pan and drops you in the shallow galleries. The Deep Shaft is a hole at the foot of the
oldest hive on the map, most of the way across the pan, and drops you straight into the deep end. A
player who finds the shaft first gets dropped next to things that will kill them - which is correct, and
is gated the right way: by how far out onto the pan they were willing to walk, not by a wall.

ONE BOSS, SHARED, AND A RARE AT EACH END. This is the structure the two entrances buy. Each mouth has its
own named rare between it and the middle, and both halves converge on the Hollow Queen - so the cave runs
in either direction, and whichever way you came in, the other rare is the thing you have not done yet.

IT IS A CAVE, NOT A DUNGEON. Standing rule, Kyle 2026-10-22: "Hand placed mobs are only in full
dungeons!" So fixed_spawns is False and the trash comes from the per-step encounter roll; the boss and
both rares are pinned via boss_positions and sit in the cave's table at weight 0.

THE LOOP IS THE POINT. The two tunnels are joined partway by a lower gallery, so the cave is a ring
rather than a line with a lump in the middle. A hive that is one corridor is a corridor; a hive you can
go round is a hive.

HARD CONTRACT (world/portal_manager.py):
    The Shimmering Flats (92, 140)  <-> The Undercrust (16, 66)    the Crustfall
    The Shimmering Flats (172, 116) <-> The Undercrust (104, 54)   the Deep Shaft
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401

BAKED = "assets/tiles/undercrust/baked"
BS = "assets/tiles/broodspiral/props/"
SN = "assets/tiles/southern_needles/props/"

W, H = 120, 110

#: The two mouths. West is the shallow end; east is the deep end.
CRUSTFALL = (16, 66)
DEEP_SHAFT = (104, 54)

#: (cx, cy, rx, ry). Chambers. The two arrival halls, the Queen's chamber between them, and the
#: pockets that hang off the ring.
CHAMBERS = {
    "crustfall_hall": (18, 62, 12, 10),      # under the collapse. Daylight comes down here.
    "west_gallery":   (38, 44, 13, 10),
    "nursery":        (34, 84, 11, 9),       # off the lower gallery. Optional.
    "queens_chamber": (62, 60, 16, 13),      # the middle, and the only thing both halves share
    "east_gallery":   (86, 72, 13, 10),
    "shaft_hall":     (102, 50, 12, 10),     # under the Deep Mound
    "spoil_pocket":   (92, 24, 10, 8),       # optional, off the east tunnel
}

#: (polyline, width). The ring: west tunnel over the top, east tunnel over the top, and the lower
#: gallery closing it underneath. Every one starts and ends WELL INSIDE the chambers it joins -
#: specifying a tunnel by the distance it has to cover is how Rocky Pass stranded 163 tiles.
TUNNELS = [
    ([(18, 58), (26, 50), (36, 46)], 2),              # crustfall hall -> west gallery
    ([(42, 42), (52, 48), (60, 56)], 2),              # west gallery -> queen's
    ([(70, 62), (80, 68), (86, 70)], 2),              # queen's -> east gallery
    ([(90, 66), (98, 58), (102, 52)], 2),             # east gallery -> shaft hall
    # THE LOWER GALLERY, which closes the ring. Without it this is a line.
    ([(22, 70), (30, 82), (44, 88), (60, 86), (76, 82), (86, 76)], 2),
    # the pockets
    ([(36, 80), (34, 84)], 2),                        # nursery
    ([(96, 44), (94, 32), (92, 26)], 2),              # spoil pocket
]

BOSSES = {
    "The Hollow Queen": (62, 60),        # the middle. Both halves lead here.
    "Saltback": (38, 44),                # the west rare, between the Crustfall and the Queen
    "Riftjaw": (86, 72),                 # the east rare, between the Deep Shaft and the Queen
}
CHESTS = [(34, 84), (92, 24), (62, 60)]

#: Trash. Random roll, per the cave rule - these are the table, not placements.
TRASH = ["Undercrust Swarmer", "Undercrust Ripper", "Hive Excavator", "Salt-Crusted Drone"]


def build_undercrust():
    zone = Tilemap("The Undercrust", W, H,
                   "A hive eating the underside of the salt pan. Two holes in the crust let you in, "
                   "at opposite ends and very different depths.")
    zone.is_cave = True
    #: .region declares the PARENT ZONE - the encounter lookup keys off it.
    zone.region = "The Shimmering Flats"
    #: A CAVE, so random trash. Kyle: "Hand placed mobs are only in full dungeons!"
    zone.fixed_spawns = False

    L = CaveLayout(zone, (CRUSTFALL[0], CRUSTFALL[1] - 2))
    b = L.b
    b.wall_id = "rock"
    b.floor_id = "dirt"

    b.lobes(list(CHAMBERS.values()))
    for (pts, wdt) in TUNNELS:
        b.corridor(pts, width=wdt)

    # the two shafts down from the pan
    b.corridor([(16, 70), (16, 64)], width=1)
    b.corridor([(104, 58), (104, 50)], width=1)

    for (px, py) in (CRUSTFALL, DEEP_SHAFT):
        zone.collision_layer[py][px] = None
        zone.set_tile(px, py, "dirt", "base")
        L.mark("portal", px, py)

    zone.boss_positions = [(x, y, n) for n, (x, y) in BOSSES.items()]
    zone.boss_position = zone.boss_positions[0][:2]
    for (x, y, n) in zone.boss_positions:
        L.mark("boss_marker", x, y)
    for (cx, cy) in CHESTS:
        if zone.is_walkable(cx, cy):
            L.mark("chest", cx, cy)

    zone.add_subzone("The Undercrust", 0, 0, W, H)      # the table applies map-wide
    zone.add_subzone("The Crustfall", 4, 48, 40, 36)
    zone.add_subzone("The Queen's Chamber", 44, 44, 36, 34)
    zone.add_subzone("The Deep Shaft", 82, 36, 36, 34)
    zone.add_subzone("The Lower Gallery", 16, 70, 80, 28)
    return zone, L


def verify_two_mouths(zone):
    """The two entrances must arrive in genuinely DIFFERENT parts of the cave.

    This is the whole premise, and it is the kind of thing that quietly stops being true: move a chamber
    twenty tiles and the two arrivals end up round the corner from each other, the cave still builds, the
    flood fill still passes, and the feature is gone with nothing to show it. So it is measured.

      * both arrivals reachable from each other - two mouths into the SAME cave, not two caves
      * they are far apart by path, not by straight line, because a hive is a warren
      * each arrival is nearer its OWN rare than the other one's, which is what makes the halves halves
    """
    from collections import deque

    def dist(src):
        d = {src: 0}
        q = deque([src])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in d and zone.is_walkable(*n):
                    d[n] = d[(x, y)] + 1
                    q.append(n)
        return d

    a = (CRUSTFALL[0], CRUSTFALL[1] - 2)
    b = (DEEP_SHAFT[0], DEEP_SHAFT[1] - 2)
    problems = []
    da = dist(a)
    if b not in da:
        problems.append("the two mouths are not connected - this is two caves, not one")
        return {}, problems
    db = dist(b)

    apart = da[b]
    if apart < 60:
        problems.append(f"the two arrivals are only {apart} tiles apart by path - they are supposed to "
                        f"be opposite ends of the cave, and at this distance the second mouth is a "
                        f"back door rather than a different part of it")

    west, east = BOSSES["Saltback"], BOSSES["Riftjaw"]
    if da.get(west, 10 ** 6) >= da.get(east, 10 ** 6):
        problems.append("the Crustfall is not nearer its own rare (Saltback) than the far one")
    if db.get(east, 10 ** 6) >= db.get(west, 10 ** 6):
        problems.append("the Deep Shaft is not nearer its own rare (Riftjaw) than the far one")

    queen = BOSSES["The Hollow Queen"]
    report = {
        "mouths apart": apart,
        "Crustfall -> Saltback": da.get(west),
        "Crustfall -> Queen": da.get(queen),
        "Deep Shaft -> Riftjaw": db.get(east),
        "Deep Shaft -> Queen": db.get(queen),
    }
    return report, problems


def dress(zone, L):
    P = L.prop
    B = dict(where=BS)
    S = dict(where=SN)
    # the shallow end: salt coming through the roof, and what fell in with it
    P("sn_driftwood_salt", 22, 58, 3, near_ok=True, **S)
    P("sn_rib_bones", 14, 70, 3, near_ok=True, **S)
    P("sn_stone_pile", 26, 66, 4, **S)
    P("carapace_pile", 34, 48, 4, **B)
    P("resin_pillar", 44, 40, 6, **B)
    # the lower gallery and the nursery
    P("egg_sac_cluster", 28, 88, 4, **B)
    P("egg_sac_cluster", 38, 82, 4, **B)
    P("carapace_pile", 56, 88, 4, **B)
    P("resin_pillar", 74, 84, 6, **B)
    # the queen's chamber
    P("resin_pillar", 52, 56, 7, **B)
    P("resin_pillar", 72, 64, 7, **B)
    P("egg_sac_cluster", 60, 70, 4, **B)
    # the deep end
    P("carapace_pile", 88, 68, 4, **B)
    P("resin_pillar", 96, 48, 6, **B)
    P("sn_rib_bones", 100, 56, 3, near_ok=True, **S)
    P("carapace_pile", 92, 28, 4, **B)
    return zone, L


def finish(zone, L):
    targets = [CRUSTFALL, DEEP_SHAFT] + [(x, y) for (x, y, _n) in zone.boss_positions] + list(CHESTS)
    return L.finish(targets)


def build_undercrust_baked():
    zone, L = build_undercrust()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_undercrust():
    zone, L = build_undercrust_baked()
    # The painted ground (tools/bake_small_caves.py undercrust). This cave declared BAKED from the
    # day it was written and never had a bake, so it drew in fallback tiles.
    import os
    if os.path.exists(f"{BAKED}/ground_0_0.jpg"):
        register_baked(zone, BAKED)
    return zone
