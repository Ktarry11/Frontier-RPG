"""
Hand-built layouts for Deathknell's two caves (2026-10-22):

  Night Web's Hollow   90x75   a SPIDER WEB: a spiral strand winds in to the Broodmother, radial threads
                               cut across the turns, a brood chamber hangs in every corner
                               (portal 45,71 / boss Broodmother Nesh'ka 45,34)
  Scarlet Crypt        95x80   a CRUCIFORM crusader crypt: gatehouse, long nave, two ring-shaped catacombs
                               (a bone ossuary west, a candle reliquary east), a chapel crossing with a
                               transept each side, and the Inquisitor's sanctum at the head of the nave
                               (portal 47,76 / boss High Inquisitor Fairbanks 47,11)

Both are CAVES, not dungeons: boss + named rares are pinned (zone.boss_positions), trash comes from the random
per-tile roll (zone.fixed_spawns = False).  Hand-placed mobs are for full multi-boss dungeons only.

Portal contracts (world/portal_manager.py): Deathknell (17,21) <-> Night Web's Hollow (45,71);
Deathknell (83,19) <-> Scarlet Crypt (47,76).

LAYOUT VARIETY: Deathknell's valley is a lobed flower.  Night Web's Hollow is a spiral + radial threads (a web),
Scarlet Crypt a formal cross with two circular catacombs - neither is a spine with symmetric wings, and neither
matches the Den (lake hall), Echo's rotunda / C-warren or Durotar's caves.

Prop rule (Kyle): less is more, props logical for the room, a few centrepieces.
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked, DP     # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, disc, pol          # noqa: F401

DEN = "assets/tiles/the_den/props/"
UC = "assets/tiles/undercity/props/"
EK = "assets/tiles/eastern_kingdoms/props/"
SR = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/deathknell_caves/{}/baked"

# --------------------------------------------------------------------------- shared helpers


def _cave(name, w, h, desc, portal):
    zone = Tilemap(name, w, h, desc)
    zone.is_cave = True
    zone.region = "Deathknell"
    zone.fixed_spawns = False                 # cave rule: random trash, boss + rares pinned
    zone.trash_spawns = None
    return zone, CaveLayout(zone, portal)


def _finish(L, zone, portal, bosses, chests):
    L.mark("portal", *portal)
    for (x, y, _) in bosses:
        L.mark("boss_marker", x, y)
    for c in chests:
        L.mark("chest", *c)
    zone.boss_position = (bosses[0][0], bosses[0][1])
    zone.boss_positions = [(x, y, n) for (x, y, n) in bosses]


def _subzones(zone, rooms, whole):
    for n, x, y, w, h in rooms:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone(whole, 0, 0, zone.width, zone.height)
    zone.subzones.insert(0, zone.subzones.pop())      # whole-map name first, so rooms override it


def disc_exact(b, cx, cy, r):
    """A perfectly round room (formal masonry - no organic wobble)."""
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                b._open(x, y)


def wall_disc(zone, cx, cy, r):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            if (x - cx) ** 2 + (y - cy) ** 2 < r * r and 1 <= x < zone.width - 1 and 1 <= y < zone.height - 1:
                zone.set_tile(x, y, "rock", "collision")


# =================================================================== NIGHT WEB'S HOLLOW
NWH_W, NWH_H = 90, 75
NWH_PORTAL = (45, 71)
NWH_C = (45, 34)
NWH_BOSS = (45, 34)
NWH_RARES = [(12, 12), (79, 58)]            # named rares - NW hatchery, SE brood chamber (named in the content pass)
NWH_CHESTS = [(45, 22), (80, 10), (9, 59)]
RX, RY = 31.0, 25.0
TURNS = 2.0


def _web_s(f):
    return 1.0 - 0.62 * f


def web_pt(f):
    th = math.radians(90 + 360 * TURNS * f)
    s = _web_s(f)
    return (NWH_C[0] + RX * s * math.cos(th), NWH_C[1] + RY * s * math.sin(th))


def web_at(deg, turn):
    """Point on the spiral at compass angle `deg` (y down) on the given turn (0 = outer)."""
    f = ((deg - 90) % 360) / (360 * TURNS) + turn / TURNS
    return web_pt(f)


def build_nwh():
    zone, L = _cave("Night Web's Hollow", NWH_W, NWH_H,
                    "A spider-infested burrow beneath Deathknell: one long silk strand spiralling in to the Broodmother.",
                    NWH_PORTAL)
    b = L.b
    cx, cy = NWH_C

    # the Maw (entrance) and the first throat of the strand
    cavern(b, 45, 67, 11, 5, 0, 0.4)
    tube(b, [(45, 62), (45, 58)], 4)
    # the spiral strand: outer turn -> inner turn -> the nest
    N = 56
    line = [web_pt(i / N) for i in range(N + 1)]
    tube(b, line, 5.2, 4.2, ph=0.7)
    cavern(b, cx, cy, 10, 8, 0, 0.5)                                     # Nesh'ka's Nest
    tube(b, [line[-1], (cx, cy + 4)], 3.4)
    # radial threads: short straight silk lines that cut across the turns and make shortcuts
    for deg in (270, 0):
        a, c = web_at(deg, 0), web_at(deg, 1)
        tube(b, [a, c], 3.0)
    # the direct strand: straight from the Maw to the second ring, so the outer turn (and its four brood chambers)
    # is the optional scenic route and the cave is not a long walk to its heart (Kyle: it is a STARTING cave)
    a, c = web_at(90, 0), web_at(90, 1)
    tube(b, [a, c], 4.2)
    # a brood chamber in every corner, each hung off the outer turn; the south two also loop back to the Maw
    cavern(b, 12, 12, 9, 7, -20, 1.2)                                    # The Hatchery (NW)
    p = web_at(225, 0)
    tube(b, [p, ((p[0] + 19) / 2, (p[1] + 15) / 2), (19, 14)], 3.2, ph=0.3)
    cavern(b, 78, 12, 9, 7, 20, 2.0)                                     # The Silk Larder (NE)
    p = web_at(315, 0)
    tube(b, [p, ((p[0] + 72) / 2, (p[1] + 14) / 2), (72, 14)], 3.2, ph=0.9)
    cavern(b, 11, 58, 8, 6, 10, 0.8)                                     # The Drained Pit (SW)
    p = web_at(135, 0)
    tube(b, [p, ((p[0] + 16) / 2, (p[1] + 56) / 2), (16, 56)], 3.2, ph=0.2)
    tube(b, [(19, 60), (27, 64), (35, 65)], 3.2, ph=1.4)                 # pit -> Maw (loop)
    cavern(b, 79, 58, 8, 6, -10, 1.7)                                    # The Brood Chamber (SE)
    p = web_at(45, 0)
    tube(b, [p, ((p[0] + 74) / 2, (p[1] + 54) / 2), (74, 54)], 3.2, ph=1.1)
    tube(b, [(71, 60), (63, 64), (55, 65)], 3.2, ph=0.6)                 # chamber -> Maw (loop)
    # the nest's back alcove (chest)
    cavern(b, 45, 22, 6, 3, 0, 0.3)
    tube(b, [(45, 27), (45, 24)], 3)

    _subzones(zone, [("The Maw", 33, 61, 24, 13), ("The Outer Strand", 14, 9, 62, 56),
                     ("The Inner Strand", 27, 20, 38, 34), ("Nesh'ka's Nest", 33, 17, 25, 24),
                     ("The Hatchery", 2, 3, 22, 18), ("The Silk Larder", 66, 3, 22, 18),
                     ("The Drained Pit", 2, 50, 20, 16), ("The Brood Chamber", 68, 50, 20, 16)],
              "Night Web's Hollow")

    _finish(L, zone, NWH_PORTAL, [(NWH_BOSS[0], NWH_BOSS[1], "Broodmother Nesh'ka")], NWH_CHESTS)
    L.critical += NWH_RARES                       # keep the named-rare spots clear of props

    p = L.prop
    # the Maw: torches either side of the mouth, a curtain of silk across the throat
    p("den_torch", 38, 69, 4)
    p("den_torch", 52, 69, 4)
    p("den_web_wall", 40, 64, 5)
    p("den_glow_mushrooms", 51, 65, 3)
    # outer strand: just enough to say 'spiders live here'
    for (x, y) in (web_at(180, 0), web_at(270, 0)):
        p("den_web_boulder", round(x) + 3, round(y) + 1, 3, where=DP)
    x, y = web_at(0, 0)
    p("den_glow_mushrooms", round(x) - 2, round(y), 3)
    x, y = web_at(135, 0)
    p("spider_husk", round(x) + 2, round(y) + 1, 3)
    x, y = web_at(270, 1)
    p("web_tangle", round(x) - 7, round(y) + 1, 4)
    x, y = web_at(180, 1)
    p("den_stalagmite_pair", round(x) - 2, round(y) + 3, 4, solid="core")
    x, y = web_at(90, 1)
    p("den_glow_mushrooms", round(x) + 3, round(y) - 1, 3)
    # the Hatchery (NW): the eggs
    p("egg_cluster_a", 6, 13, 4, solid="core", where=DEN)
    p("egg_cluster_b", 16, 15, 4, solid="core", where=DEN)
    p("den_egg_cluster", 8, 16, 4, solid="core")
    p("den_eggshell_pile", 14, 9, 2)
    # the Silk Larder (NE): cocoons of the unlucky
    p("den_web_cocoon", 75, 11, 4)
    p("den_web_cocoon", 82, 14, 4)
    p("cocoon_victim", 75, 8, 4)
    p("den_dead_recruit", 80, 16, 3)
    p("den_backpack", 73, 15, 2)
    # the Drained Pit (SW): husks and bones
    p("den_chitin_husk", 9, 56, 3)
    p("den_leg_bones", 14, 62, 2)
    p("spider_husk", 8, 62, 3)
    p("den_rock_rubble", 13, 55, 2)
    # the Brood Chamber (SE): nests
    p("spider_nest", 84, 55, 4, solid="core")
    p("den_egg_cluster", 74, 60, 4, solid="core")
    p("den_eggshell_pile", 84, 61, 2)
    # Nesh'ka's Nest: the mound behind her, eggs and silk to the sides
    p("den_nest_mound", 45, 29, 6, solid="core", avoid=2)
    p("den_egg_cluster", 37, 31, 4, solid="core")
    p("den_egg_cluster", 53, 31, 4, solid="core")
    p("den_web_wall", 38, 38, 5)
    p("den_web_wall", 52, 38, 5)
    p("spider_nest", 45, 41, 4, solid="core")
    # back alcove
    p("den_eggshell_pile", 41, 21, 2)

    L.finish([NWH_PORTAL, NWH_BOSS] + NWH_CHESTS + NWH_RARES)
    return zone, L


# ======================================================================= SCARLET CRYPT
CR_W, CR_H = 95, 80
CR_PORTAL = (47, 76)
CR_BOSS = (47, 11)
CR_RARES = [(23, 54), (71, 54)]            # named rares - the ossuary vault (W) and the reliquary vault (E)
CR_CHESTS = [(57, 6), (13, 33), (84, 32), (71, 58)]
RING_W = (23, 54)
RING_E = (71, 54)
R_OUT, R_IN, R_VAULT = 13, 7.5, 4


def _ring(b, zone, c, door_side):
    cx, cy = c
    disc_exact(b, cx, cy, R_OUT)
    wall_disc(zone, cx, cy, R_IN)
    disc_exact(b, cx, cy, R_VAULT)                                           # the vault in the core
    dx, dy = {"W": (-1, 0), "E": (1, 0), "N": (0, -1), "S": (0, 1)}[door_side]
    for i in range(R_VAULT - 1, int(R_IN) + 2):                              # its door, through the core wall
        for k in (-1, 0, 1):
            b._open(cx + dx * i + (k if dy else 0), cy + dy * i + (k if dx else 0))


def build_crypt():
    zone, L = _cave("Scarlet Crypt", CR_W, CR_H,
                    "A Scarlet Crusade crypt-fortress: a cross of stone halls around a nave, two catacomb rings, and an inquisitor at the head.",
                    CR_PORTAL)
    b = L.b
    zone_floor = "dirt"
    # gatehouse -> stair of penitents -> nave
    b.rect(36, 68, 58, 77, chamfer=3)
    b.rect(43, 56, 51, 68)
    b.rect(43, 38, 51, 56)
    # the two catacomb rings off the nave
    _ring(b, zone, RING_W, "W")
    _ring(b, zone, RING_E, "N")
    b.rect(35, 52, 43, 56)
    b.rect(51, 52, 59, 56)
    # chapel crossing + transepts
    b.rect(39, 24, 55, 40, chamfer=5)
    b.rect(20, 28, 39, 36, chamfer=2)
    b.rect(55, 28, 74, 36, chamfer=2)
    disc_exact(b, 15, 32, 7)                                                 # the Penitent Cells (round)
    b.rect(74, 26, 87, 38, chamfer=3)                                        # the Armoury (square)
    # the Penitent's Walk and the Inquisitor's Sanctum
    b.rect(44, 17, 50, 24)
    b.rect(30, 3, 64, 17, chamfer=5)
    # flank passages from the transept ends curving up to the sanctum (loop around the cross)
    tube(b, [(13, 26), (11, 18), (16, 11), (25, 9), (31, 9)], 4, ph=0.4)
    tube(b, [(84, 26), (86, 18), (79, 11), (70, 9), (63, 9)], 4, ph=1.3)

    _subzones(zone, [("The Gatehouse", 34, 66, 26, 13), ("The Stair of Penitents", 42, 55, 10, 13),
                     ("The Nave", 42, 38, 10, 19), ("The Ossuary", 9, 40, 28, 28),
                     ("The Reliquary", 57, 40, 28, 28), ("The Chapel Crossing", 38, 22, 18, 20),
                     ("The Penitent Cells", 7, 24, 16, 17), ("The Scarlet Armoury", 73, 25, 16, 15),
                     ("The Penitent's Walk", 43, 16, 9, 9), ("The Inquisitor's Sanctum", 29, 2, 37, 16)],
              "Scarlet Crypt")

    _finish(L, zone, CR_PORTAL, [(CR_BOSS[0], CR_BOSS[1], "High Inquisitor Fairbanks")], CR_CHESTS)
    L.critical += CR_RARES                        # keep the named-rare spots clear of props

    p = L.prop
    # gatehouse: banners flank the door in, lanterns of the Crusade
    p("ek_scarlet_banner", 40, 73, 5, where=EK)
    p("ek_scarlet_banner", 54, 73, 5, where=EK)
    p("candelabra", 39, 70, 4)
    p("candelabra", 55, 70, 4)
    p("ek_scarlet_crates", 55, 76, 3, where=EK)
    # stair + nave: columns in pairs, the odd skull pillar, a coffin stack against the wall
    for y in (60, 48):
        p("temple_column", 44, y, 5, solid="core")
        p("temple_column", 50, y, 5, solid="core")
    p("uc_coffin_stack", 44, 66, 4, where=UC)
    p("skull_pile", 50, 44, 3)
    # the Ossuary (west ring): bones and the dead
    p("skull_pile", 17, 45, 3)
    p("uc_bone_heap", 29, 49, 3, where=UC)
    p("sarcophagus", 16, 62, 4, solid="core")
    p("uc_coffin_stack", 30, 60, 4, where=UC)
    p("ek_open_grave", 23, 66, 3, where=EK)
    p("uc_skull_pillar", 23, 44, 4, where=UC, solid="core")
    p("bone_pile", 14, 53, 3, where=SR)
    # the vault (W): the warden's crypt
    p("sarcophagus", 23, 51, 4, solid="core")
    # the Reliquary (east ring): candles, lecterns, banners
    p("candelabra", 65, 45, 4)
    p("candelabra", 77, 63, 4)
    p("uc_lectern", 78, 49, 3, where=UC, solid="core")
    p("ek_scarlet_banner", 71, 43, 5, where=EK)
    p("ek_scarlet_crates", 64, 62, 3, where=EK)
    p("ek_angel_statue", 71, 50, 5, where=EK, solid="core")
    # the vault (E)
    p("candelabra", 68, 55, 3)
    # chapel crossing: the centre of the cross
    p("candelabra", 43, 28, 4)
    p("candelabra", 51, 28, 4)
    p("broken_column", 42, 36, 3, solid="core")
    p("broken_column", 52, 36, 3, solid="core")
    # transepts: cells in the west (cages and shackles), armoury in the east
    p("rf_prison_cage", 12, 29, 4, solid="core")
    p("rf_shackle_frame", 18, 35, 4, solid="core")
    p("ek_gibbet", 9, 34, 5, where=EK, solid="core")
    p("bone_pile", 13, 36, 3, where=SR)
    p("weapon_rack", 77, 29, 4, solid="core")
    p("weapon_rack", 83, 29, 4, solid="core")
    p("ek_scarlet_crates", 80, 37, 3, where=EK)
    p("ek_scarlet_banner", 85, 36, 5, where=EK)
    p("banquet_table", 60, 32, 3, solid="core")
    # the Penitent's Walk and sanctum: the altar is the centrepiece
    p("candelabra", 45, 21, 4)
    p("candelabra", 49, 21, 4)
    p("bbc_altar", 47, 7, 5, solid="core", avoid=2)
    p("ek_scarlet_banner", 38, 10, 5, where=EK)
    p("ek_scarlet_banner", 56, 10, 5, where=EK)
    p("candelabra", 36, 14, 4)
    p("candelabra", 58, 14, 4)
    p("temple_column", 36, 8, 5, solid="core")
    p("temple_column", 60, 8, 5, solid="core")

    L.finish([CR_PORTAL, CR_BOSS] + CR_CHESTS + CR_RARES)
    return zone, L


# ======================================================== generate_* wrappers
def _gen(build, slug):
    zone, _ = build()
    register_baked(zone, BAKED.format(slug))
    return zone


def generate_night_webs_hollow():
    return _gen(build_nwh, "nwh")


def generate_scarlet_crypt():
    return _gen(build_crypt, "crypt")
