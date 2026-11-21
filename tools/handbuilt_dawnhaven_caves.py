"""
Hand-built Dawnhaven's four caves (docs/dawnhaven_brief.md), two in each zone. Caves, not dungeons: one or two bosses
pinned by the map, trash rolled from the cave's own table (zone.fixed_spawns = False).

Kyle, 21 Nov 2026: "2 caves in each zone", and on picking them, "You pick, I'll review". The standing rules: rooms with
loops, no hallway simulators, no blobs, and no shape the game already has.

  BRINECOIL GROTTO     off Amberleaf Glade (126,94), 3-5. THE INLET. The naga's landing cave: a long jagged arm of the
                       sea running up the cave on a slant, a rock ledge along each bank, a rock bridge over it halfway
                       and a high crossing under the altar, so the banks make one long loop. Tidecaller Sszelith
                       keeps her scouts' rites at the altar at the inlet's head.
  THE QUIET VAULT      off Amberleaf Glade (34,20), 5-6. THE CLOISTER. The outpost's garrison crypt under the Silent
                       Barrow, built square by masons: a stair down into a long nave, a cloister of four straight walks
                       round the ossuary (walk it either way), long burial halls off either side, and the warden's tomb
                       at the head. Warden
                       Isilien, who sealed the vault and never left it, won't let anyone disturb the dead.
  SALTSPINE HOLLOW     off Duskfall Woods (20,32), 7-9. THE TERRACES. The naga's main hold: wide chambers stepping down
                       into the sea, each one flooded a little deeper than the last, joined by two ramps, one on each
                       side, so every tier is a loop; the throne pool at the bottom. Sea-Witch Ilthessa holds the
                       throne; Old Saltspine, the great crab the naga feed, lies in a side pool off the second tier.
  THE LIGHTWELL DEEP   off Duskfall Woods (124,44), 8-9. THE UNDERWORKS. The outpost's machinery under the well,
                       built square by elven masons: an undercroft, a cistern gallery and an archive off it, both
                       climbing to the long conduit hall across the works (a loop), and the font chamber above, where
                       the well's root comes down. The Starved Light, the well's hunger woken and given a shape, holds
                       the font; Archivist Lorethas, the outpost's last magister, still keeps the archive.

Every cave's way in and out is its one portal at the bottom; you arrive two tiles inside it.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

DP = "assets/tiles/dungeon_props/"
AZP = "assets/tiles/azshara/props/"
BLD = "assets/buildings/"

GROTTO, VAULT, HOLLOW, DEEP = "Brinecoil Grotto", "The Quiet Vault", "Saltspine Hollow", "The Lightwell Deep"
CAVES = (GROTTO, VAULT, HOLLOW, DEEP)
SLUG = {GROTTO: "brinecoil_grotto", VAULT: "quiet_vault", HOLLOW: "saltspine_hollow", DEEP: "lightwell_deep"}
BAKED = {n: f"assets/tiles/dawnhaven/baked_{SLUG[n]}" for n in CAVES}
PARENT = {GROTTO: "Amberleaf Glade", VAULT: "Amberleaf Glade", HOLLOW: "Duskfall Woods", DEEP: "Duskfall Woods"}
DESC = {
    GROTTO: "The naga's landing cave on Brinecoil Cove: a ring of galleries round a pool the sea fills, and the tide "
            "altar on the far side.",
    VAULT: "The outpost's garrison crypt under the Silent Barrow, a nave and a cloister round the bones of everyone who "
           "held Dawnhaven the first time.",
    HOLLOW: "The naga's hold under Saltspine Shore, terraces stepping down into the sea to the sea-witch's throne.",
    DEEP: "The root of the Lightwell, deep under the court: the font's chamber, its four conduits and the nodes they "
          "fed, all of it dark and hungry.",
}
SIZE = {GROTTO: (80, 84), VAULT: (80, 90), HOLLOW: (92, 96), DEEP: (92, 92)}
PORTAL = {GROTTO: (40, 81), VAULT: (40, 87), HOLLOW: (46, 93), DEEP: (46, 89)}
BOSSES = {n: {} for n in CAVES}
CHESTS = {n: [] for n in CAVES}
ROOM_NAMES = {n: {} for n in CAVES}
POOLS = {n: [] for n in CAVES}


def _near_walkable(zone, x, y, rad=5, dry=True):
    best = None
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            xx, yy = int(x) + dx, int(y) + dy
            if not zone.is_walkable(xx, yy):
                continue
            if dry and zone.base_layer[yy][xx] in ("shallow_water", "deep_water"):
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, xx, yy)
    return None if best is None else (best[1], best[2])


def _snapped(zone, L):
    def P(name, x, y, h, **kw):
        p = _near_walkable(zone, x, y, rad=3)
        return L.prop(name, p[0], p[1], h, **kw) if p else L.skipped.append((name, x, y, "no floor near"))
    return P


def _room(b, x0, y0, x1, y1):
    """A built room: square corners, every tile from (x0, y0) to (x1, y1) open."""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            b._open(x, y, None)


def _new(name):
    W, H = SIZE[name]
    zone = Tilemap(name, W, H, DESC[name])
    zone.is_cave = True
    zone.region = PARENT[name]
    zone.fixed_spawns = False
    px, py = PORTAL[name]
    return zone, CaveLayout(zone, (px, py - 2))


def _place(zone, L, name, bosses, chests, rooms):
    px, py = PORTAL[name]
    zone.collision_layer[py][px] = None
    L.mark("portal", px, py)
    fixed = []
    for (x, y, n) in bosses:
        p = _near_walkable(zone, x, y)
        assert p, (name, n, x, y)
        fixed.append((p[0], p[1], n))
        L.mark("boss_marker", p[0], p[1])
    BOSSES[name].clear()
    BOSSES[name].update({n: (x, y) for (x, y, n) in fixed})
    zone.boss_position = (fixed[0][0], fixed[0][1])
    zone.boss_positions = list(fixed)
    CHESTS[name][:] = []
    for (x, y) in chests:
        p = _near_walkable(zone, x, y)
        assert p, (name, x, y)
        CHESTS[name].append(p)
        L.mark("chest", *p)
    W, H = SIZE[name]
    zone.add_subzone(name, 0, 0, W, H)
    ROOM_NAMES[name].clear()
    for rname, (x, y, w, h) in rooms.items():
        zone.add_subzone(rname, x, y, w, h)
        ROOM_NAMES[name][rname] = (x, y, w, h)


# ============================================================================================ BRINECOIL GROTTO
#: THE INLET (Kyle, 21 Nov 2026: "Stop making every cave a circle"). A long jagged arm of the sea runs up the cave on a
#: slant from the mouth to the altar. You climb its east bank, cross a rock bridge over it halfway, go on up the
#: west bank's kelp shelf, and a second, higher crossing joins the banks again under the altar, so the two banks and
#: the two crossings make one long loop.
INLET = [(46, 76), (42, 64), (40, 52), (34, 40), (30, 28), (24, 16)]


def build_grotto():
    name = GROTTO
    zone, L = _new(name)
    b = L.b
    tube(b, [PORTAL[name], (52, 74)], 5.0, 6.0, ph=0.2)
    cavern(b, 52, 72, 10, 6, 15, 0.4)                       # the tide mouth
    # the inlet itself is cut wide, then flooded down its middle
    tube(b, INLET, 9.0, 7.0, ph=0.6)
    # the east ledges: a bank of rock above the water on the inlet's right, wider in two places
    east = [(58, 66), (56, 54), (52, 42), (46, 30), (40, 18)]
    tube(b, east, 6.0, 5.4, ph=1.1)
    cavern(b, 58, 54, 7, 6, -20, 1.6)
    cavern(b, 50, 34, 6.5, 5.5, -30, 2.2)
    # the west shelf: the kelp shelf on the left, from the rock bridge up to the altar
    west = [(30, 54), (24, 44), (18, 32), (14, 20)]
    tube(b, west, 6.0, 5.4, ph=1.9)
    cavern(b, 22, 40, 7, 6.5, 25, 2.8)
    # the two crossings: the rock bridge halfway, and the high crossing under the altar
    tube(b, [(54, 52), (40, 51), (28, 54)], 6.4, 6.4, ph=0.8)
    tube(b, [(42, 22), (28, 19), (14, 22)], 6.4, 6.4, ph=1.3)
    # the tide altar at the head of the inlet, top left
    cavern(b, 22, 10, 12, 6, -10, 2.6)
    pools = [(44, 69, 2.4, 3.4, 0.5), (41, 61, 2.2, 3.4, 0.9), (36, 42, 2.2, 3.4, 1.3), (31, 31, 2.2, 3.2, 1.7),
             (52, 76, 3.2, 2.0, 2.1)]
    POOLS[name][:] = pools
    _apply_pools(zone, pools)
    _place(zone, L, name, [(22, 8, "Tidecaller Sszelith")],
           [(60, 56), (20, 42), (50, 32)],
           {"The Tide Mouth": (42, 64, 24, 20), "The East Ledges": (40, 24, 26, 42), "The Rock Bridge": (28, 46, 28, 12),
            "The Kelp Shelf": (6, 16, 26, 44), "The Tide Altar": (8, 2, 30, 16)})
    return zone, L


def dress_grotto(zone, L):
    P = _snapped(zone, L)
    P("az_tide_altar", 22, 5, 4, where=AZP, solid="core")
    P("az_naga_banner", 14, 8, 4, where=AZP, solid="core")
    P("az_naga_banner", 30, 8, 4, where=AZP, solid="core")
    P("grotto_kelp_stalks", 16, 30, 3, solid="core")
    P("grotto_kelp_stalks", 26, 46, 3, solid="core")
    P("az_coral_cluster", 60, 50, 3, where=AZP, solid="core")
    P("az_giant_clam", 54, 38, 3, where=AZP, solid="core")
    P("grotto_shell_altar", 52, 30, 3, solid=False)
    P("grotto_crab_nest", 60, 74, 3, solid=False)
    P("az_wreck_prow", 44, 76, 4, where=AZP, solid=False)
    return zone, L


# ============================================================================================ THE QUIET VAULT
def build_vault():
    """Built, not dug: the garrison's crypt is masons' work with square corners, a long nave and a cloister of four
    straight walks round the ossuary, so you can go round it either way (Kyle: "Stop making every cave a circle")."""
    name = VAULT
    zone, L = _new(name)
    b = L.b
    _room(b, 37, 70, 43, 87)                    # the stair down
    _room(b, 33, 58, 47, 70)                    # the nave's foot
    # the cloister: four straight walks round the ossuary
    _room(b, 22, 30, 58, 35)                    # north walk
    _room(b, 22, 53, 58, 58)                    # south walk
    _room(b, 22, 30, 27, 58)                    # west walk
    _room(b, 53, 30, 58, 58)                    # east walk
    _room(b, 34, 40, 46, 48)                    # the ossuary, reached from north and south
    _room(b, 38, 35, 42, 40)
    _room(b, 38, 48, 42, 53)
    # the burial halls off either side, long and narrow, with the niches down their walls
    _room(b, 6, 36, 18, 56)
    _room(b, 18, 42, 22, 47)
    _room(b, 62, 32, 74, 52)
    _room(b, 58, 40, 62, 45)
    # the warden's tomb at the head, up a short stair
    _room(b, 37, 22, 43, 30)
    _room(b, 28, 8, 52, 22)
    _place(zone, L, name, [(40, 12, "Warden Isilien")],
           [(8, 40), (72, 48), (36, 46)],
           {"The Nave": (33, 58, 15, 30), "The Cloister": (22, 30, 37, 29), "The Ossuary": (34, 40, 13, 9),
            "The West Niches": (6, 36, 13, 21), "The East Niches": (62, 32, 13, 21),
            "The Warden's Tomb": (28, 8, 25, 15)})
    return zone, L


def dress_vault(zone, L):
    P = _snapped(zone, L)
    P("sarcophagus", 40, 11, 3, solid="core")
    P("grotto_blue_brazier", 33, 12, 2, solid="core")
    P("grotto_blue_brazier", 47, 12, 2, solid="core")
    P("broken_column", 30, 19, 3, solid="core")
    P("broken_column", 50, 19, 3, solid="core")
    P("skull_pile", 44, 44, 3, solid="core")
    # the niches: a stone coffin against each long wall of both burial halls
    for (x, y) in [(8, 50), (16, 38), (64, 36), (72, 44)]:
        P("sarcophagus", x, y, 3, solid="core")
    P("grotto_blue_brazier", 24, 32, 2, solid="core")
    P("grotto_blue_brazier", 56, 56, 2, solid="core")
    return zone, L


# ============================================================================================ SALTSPINE HOLLOW
#: the terraces, top (the way in) to bottom (the throne pool): (cx, cy, rx, ry)
TIERS = [(46, 76, 16, 7), (46, 56, 20, 7), (46, 36, 22, 7), (46, 16, 16, 9)]
CRAB_POOL = (80, 50)


def build_hollow():
    name = HOLLOW
    zone, L = _new(name)
    b = L.b
    tube(b, [PORTAL[name], (46, 80)], 5.0, 6.0, ph=0.2)
    for i, (cx, cy, rx, ry) in enumerate(TIERS):
        cavern(b, cx, cy, rx, ry, 0, 0.5 + i)
    # the two ramps, one down each side, joining every tier to the next: every tier is a loop
    for i in range(len(TIERS) - 1):
        (ax, ay, arx, _ary), (bx, by, brx, _bry) = TIERS[i], TIERS[i + 1]
        tube(b, [(ax - arx + 4, ay), (bx - brx + 4, by)], 5.0, 5.0, ph=1.0 + i)
        tube(b, [(ax + arx - 4, ay), (bx + brx - 4, by)], 5.0, 5.0, ph=1.6 + i)
    # Old Saltspine's side pool off the second tier, east
    tube(b, [(64, 56), (74, 52)], 4.6, 4.6, ph=2.4)
    cavern(b, CRAB_POOL[0], CRAB_POOL[1], 8, 7, 0, 3.0)
    # the sea in every tier, deeper the lower you go, always toward the middle so the ramps stay dry
    pools = [(46, 58, 6.0, 2.4, 0.3), (46, 38, 9.0, 3.0, 0.8), (46, 10, 6.0, 2.4, 1.4),
             (83, 50, 4.4, 3.6, 1.9)]
    POOLS[name][:] = pools
    _apply_pools(zone, pools)
    hb = _near_walkable(zone, CRAB_POOL[0] - 4, CRAB_POOL[1], rad=6)
    _place(zone, L, name, [(46, 21, "Sea-Witch Ilthessa"), (hb[0], hb[1], "Old Saltspine")],
           [(28, 76), (68, 36), (26, 36)],
           {"The Upper Terrace": (28, 68, 36, 16), "The Second Terrace": (24, 48, 44, 16),
            "The Third Terrace": (22, 28, 48, 16), "The Throne Pool": (30, 6, 32, 18),
            "Saltspine's Pool": (70, 42, 20, 16)})
    return zone, L


def dress_hollow(zone, L):
    P = _snapped(zone, L)
    P("vz_coral_throne", 46, 9, 4, solid="core")
    P("grotto_naga_priestess_statue", 38, 12, 4, solid="core")
    P("grotto_naga_warrior_statue", 54, 12, 4, solid="core")
    P("grotto_blue_brazier", 34, 20, 3, solid="core")
    P("grotto_blue_brazier", 58, 20, 3, solid="core")
    P("az_naga_banner", 32, 74, 4, where=AZP, solid="core")
    P("az_naga_banner", 60, 74, 4, where=AZP, solid="core")
    P("az_scale_pile", 30, 56, 3, where=AZP, solid=False)
    P("grotto_glow_coral", 64, 34, 3, solid="core")
    P("grotto_crab_nest", 86, 44, 3, solid="core")
    P("az_coral_cluster", 28, 36, 3, where=AZP, solid="core")
    return zone, L


# ============================================================================================ THE LIGHTWELL DEEP
#: THE UNDERWORKS (Kyle, 21 Nov 2026: "Stop making every cave a circle"). Not a cave at all but the outpost's own
#: machinery under the well, built square by elven masons: the stair down into the undercroft, two halls off it (the
#: cistern gallery west, the archive east, set lower), both climbing to the long conduit hall that runs across the
#: whole works, so the four make a loop, and from the conduit hall's middle the last stair up into the font chamber
#: where the well's root comes down. A sealed side vault opens off the archive.


def build_deep():
    name = DEEP
    zone, L = _new(name)
    b = L.b
    _room(b, 43, 80, 49, 88)                    # the stair down
    _room(b, 32, 68, 60, 79)                    # the undercroft
    _room(b, 8, 50, 30, 64)                     # the cistern gallery, west
    _room(b, 62, 56, 84, 70)                    # the archive, east and lower
    _room(b, 70, 72, 84, 82)                    # the sealed vault off the archive
    _room(b, 10, 30, 82, 40)                    # the conduit hall, right across the works
    _room(b, 40, 22, 52, 29)                    # the last stair up
    _room(b, 28, 6, 64, 21)                     # the font chamber
    # the ways between them, each a short built passage five wide
    _room(b, 24, 64, 34, 70)                    # undercroft to cistern
    _room(b, 58, 64, 64, 72)                    # undercroft to archive
    _room(b, 14, 40, 20, 50)                    # cistern up to the conduit hall
    _room(b, 72, 40, 78, 56)                    # archive up to the conduit hall
    _room(b, 75, 70, 80, 72)                    # archive to the vault
    pools = [(46, 12, 4.4, 3.0, 0.6), (19, 57, 5.0, 2.6, 1.2)]      # the root's pool, and the cistern
    POOLS[name][:] = pools
    _apply_pools(zone, pools)
    _place(zone, L, name, [(46, 17, "The Starved Light"), (74, 62, "Archivist Lorethas")],
           [(78, 78), (10, 52), (80, 32)],
           {"The Undercroft": (32, 68, 29, 12), "The Cistern Gallery": (8, 50, 23, 15), "The Archive": (62, 56, 23, 15),
            "The Sealed Vault": (70, 72, 15, 11), "The Conduit Hall": (10, 30, 73, 11), "The Font": (28, 6, 37, 16)})
    return zone, L


def dress_deep(zone, L):
    P = _snapped(zone, L)
    P("az_arcane_crystal", 34, 10, 4, where=AZP, solid="core")
    P("az_arcane_crystal", 58, 10, 4, where=AZP, solid="core")
    P("az_leyline_node", 36, 19, 3, where=AZP, solid="core")
    P("az_leyline_node", 56, 19, 3, where=AZP, solid="core")
    for x in (22, 34, 58, 70):
        P("az_containment_pylon", x, 32, 4, where=AZP, solid="core")
    P("az_relic_crate", 80, 60, 3, where=AZP, solid="core")
    P("az_relic_crate", 66, 66, 3, where=AZP, solid="core")
    P("broken_column", 40, 77, 3, solid="core")
    P("broken_column", 52, 77, 3, solid="core")
    return zone, L


BUILD = {GROTTO: (build_grotto, dress_grotto), VAULT: (build_vault, dress_vault),
         HOLLOW: (build_hollow, dress_hollow), DEEP: (build_deep, dress_deep)}


def build(name):
    zone, L = BUILD[name][0]()
    BUILD[name][1](zone, L)
    L.finish([PORTAL[name]] + list(BOSSES[name].values()) + CHESTS[name])
    return zone, L


#: each cave's air (docs/environment_effects_art_prompts.md): shade, light and what drifts in it
EFFECTS = {
    GROTTO: dict(shade={"layer": "shade_cave_vignette", "strength": 0.45},
                 light={"layer": "light_cave_skylight", "strength": 0.30, "breathe": 0.2},
                 particles={"sprites": ["p_bubbles", "p_bubble"], "count": 6, "size": 0.4, "fall": -14, "wind": 0,
                            "sway": 10, "spin": 0}),
    VAULT: dict(shade={"layer": "shade_haunted", "strength": 0.45},
                light={"layer": "light_cave_skylight", "strength": 0.24, "breathe": 0.25},
                particles={"sprites": ["p_wisp_light"], "count": 5, "size": 0.45, "fall": -8, "wind": 3,
                           "sway": 14, "spin": 0}),
    HOLLOW: dict(shade={"layer": "shade_underwater", "strength": 0.32},
                 light={"layer": "light_crystal_cave", "strength": 0.34, "breathe": 0.2},
                 particles={"sprites": ["p_bubbles", "p_bubble"], "count": 8, "size": 0.4, "fall": -16, "wind": 0,
                            "sway": 10, "spin": 0}),
    DEEP: dict(shade={"layer": "shade_cave_vignette", "strength": 0.5},
               light={"layer": "light_arcane_shimmer", "strength": 0.45, "breathe": 0.25},
               particles={"sprites": ["p_mote_arcane", "p_mana_spark"], "count": 7, "size": 0.4, "fall": -10,
                          "wind": 2, "sway": 12, "spin": 30}),
}


def generate(name):
    zone, _L = build(name)
    register_baked(zone, BAKED[name])
    for k, v in EFFECTS.get(name, {}).items():
        setattr(zone, k, dict(v))
    return zone


def build_grotto_baked():
    return build(GROTTO)


def build_vault_baked():
    return build(VAULT)


def build_hollow_baked():
    return build(HOLLOW)


def build_deep_baked():
    return build(DEEP)


if __name__ == "__main__":
    for n in CAVES:
        z, L = build(n)
        walk = sum(1 for y in range(z.height) for x in range(z.width) if z.is_walkable(x, y))
        print(n, z.width, "x", z.height, "| walkable", walk, "| bosses", BOSSES[n], "| skipped", L.skipped)
