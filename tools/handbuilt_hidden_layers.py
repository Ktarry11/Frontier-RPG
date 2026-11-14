"""The hidden levels under dungeons (world/hidden_zones.py, kind "layer").

SPOILERS. Kyle, 14 Nov 2026: "I don't want to see as I want these to be secrets." Nothing in this
file says how to find them; the doors that lead here are picked by tools/build_secrets.py.

What Kyle asked for, word for word, is the brief for every one of these:
  "a hidden part in a dungeon can lead to a sub level where instead of... 3x HP and 3x Damage...
   it's 4x HP and 4.5x Damage. But items there are... 4 to 5 ilvl and can have unique epics above
   level 30... It'll only ever be 1 to 2 bosses max and like 5 trash pulls total. Trash gets
   buffed too."  And: "hidden Dungeons can look similar to their base Dungeons."

So each is small: five pulls, one or two bosses, a hoard, painted in its parent's materials but a
shape none of the game's other caves use (playbook section 4, LAYOUT VARIETY):

  The Cinderwell          a SPIRAL round a lava well, ending on an island in the middle
  The Dreaming Root       HUB AND SPOKES round a sleeping pool, the spokes joined in a loop
  The Ossuary Below       one long WINDING GORGE of bone niches climbing to a round charnel
  The Lightless Reach     a FLOODED GALLERY: islands in black water joined by wading paths
  The Blood Pits          a CROSS: a spine of cells with two arms, the pit at the crossing
  The Unwritten Stacks    a GRID of shelf-aisles with a reading-room loop round the outside

Each map's way in is its own portal at the bottom of an entry hall; arriving puts you two tiles
north of it (world/portal_manager._offset_spawn).
"""
import math

from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, _apply_pools, register_baked  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube, disc

BAKED = "assets/tiles/hidden/{}/baked"
STV = "assets/tiles/stranglethorn/props/"
UDP = "assets/tiles/underdark/props/"
ASHX = "assets/tiles/ashenvale_corruption/props/"
HF = "assets/tiles/haunted_forest/props/"
NG = "assets/tiles/naga_dungeon/"
SB = "assets/tiles/seabed/"


def _layer(name, w, h, desc, region, portal):
    zone = Tilemap(name, w, h, desc)
    zone.is_cave = True
    zone.region = region
    zone.fixed_spawns = True
    zone.hidden_layer = True
    return zone, CaveLayout(zone, portal)


def _near_walkable(zone, x, y, taken):
    best = None
    for r in range(0, 6):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                p = (x + dx, y + dy)
                if p in taken or not zone.is_walkable(*p) or zone.get_tile(p[0], p[1], "interaction"):
                    continue
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, p)
        if best:
            return best[1]
    raise AssertionError(f"{zone.name}: no floor near ({x},{y}) for a pull")


def _close(L, zone, portal, bosses, packs, chests, rooms):
    """Markers, rooms as subzones, the five pulls, and the flood-fill check."""
    px, py = portal
    for dy in (0, 1, 2, 3):                 # the way in is open, and so is where you arrive
        L.b._open(px, py - dy)
    L.mark("portal", *portal)
    for (x, y, _n) in bosses:
        L.mark("boss_marker", x, y)
    for c in chests:
        L.mark("chest", *c)
    zone.boss_position = (bosses[0][0], bosses[0][1])
    zone.boss_positions = [(x, y, n) for (x, y, n) in bosses]
    taken = set()
    built = []
    for pack in packs:
        members = []
        for (x, y, mob, lvl) in pack:
            p = _near_walkable(zone, x, y, taken)
            taken |= {(p[0] + dx, p[1] + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
            members.append((p[0], p[1], mob, lvl))
        built.append(members)
    zone.trash_packs = built
    zone.trash_spawns = [m for p in built for m in p]
    for n, x, y, w, h in rooms:
        zone.add_subzone(n, x, y, w, h)
    zone.add_subzone(zone.name, 0, 0, zone.width, zone.height)
    zone.subzones.insert(0, zone.subzones.pop())        # whole map first, so rooms override it
    return built


def _ring(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# =============================================================================== THE CINDERWELL
CW_PORTAL = (55, 86)
CW_WELL = (55, 46)
CW_VORN = (86, 72)
CW_HEART = (55, 46)
CW_CHESTS = [(55, 42), (22, 12)]


def build_cinderwell():
    zone, L = _layer(
        "The Cinderwell", 110, 92,
        "Under the Searing Blade's floor, the cult's true temple: a spiral of kilns cut round a well "
        "of living fire, and something in the well that answers when it's fed.",
        "Orgrimmar", CW_PORTAL)
    b = L.b
    # the spiral, clockwise from the bottom: entry -> slag steps -> kiln shrine -> ash gallery ->
    # pyre walk -> tithe hall -> ember chapel, then in across the lava to the heart
    cavern(b, 55, 82, 9, 4, 0, 0.4)                                    # The Scorched Stair
    tube(b, [(48, 81), (38, 78), (28, 72)], 4, ph=0.6)
    cavern(b, 24, 70, 9, 6, -15, 1.1)                                  # The Slag Steps
    tube(b, [(20, 64), (16, 55), (16, 47)], 4, ph=1.3)
    cavern(b, 16, 41, 8, 8, 10, 2.0)                                   # The Kiln Shrine
    tube(b, [(18, 33), (20, 25), (24, 18)], 4, ph=0.2)
    cavern(b, 29, 13, 12, 6, -10, 0.9)                                 # The Ash Gallery
    tube(b, [(41, 12), (55, 10), (68, 11)], 4, 5, ph=1.7)
    cavern(b, 80, 13, 11, 6, 15, 2.4)                                  # The Pyre Walk
    tube(b, [(88, 18), (93, 27), (94, 36)], 4, ph=0.5)
    cavern(b, 94, 44, 9, 9, 0, 1.4)                                    # The Tithe Hall
    tube(b, [(93, 53), (91, 61), (88, 66)], 4, ph=2.2)
    cavern(b, 84, 73, 10, 7, -20, 0.7)                                 # The Ember Chapel
    # the well: a rim walk round a lake of fire, a stone island in the middle, one causeway
    tube(b, [(76, 70), (70, 64), (66, 59)], 4, ph=1.0)
    disc(b, CW_WELL[0], CW_WELL[1], 17, ph=0.3)              # The Well Rim
    for y in range(CW_WELL[1] - 14, CW_WELL[1] + 15):
        for x in range(CW_WELL[0] - 14, CW_WELL[0] + 15):
            r = math.hypot(x + 0.5 - CW_WELL[0], y + 0.5 - CW_WELL[1])
            a = math.atan2(y - CW_WELL[1], x - CW_WELL[0])
            if r <= 12.5 + 0.8 * math.sin(3 * a + 0.4) + 0.5 * math.sin(5 * a):
                b._open(x, y, "lava")
    disc(b, CW_WELL[0], CW_WELL[1] - 1, 5.5, ph=1.2)                     # The Heart's Isle
    tube(b, [(66, 57), (62, 52), (59, 48)], 3, ph=0.0)                 # the causeway

    rooms = [("The Scorched Stair", 44, 76, 22, 12), ("The Slag Steps", 13, 62, 22, 16),
             ("The Kiln Shrine", 6, 32, 20, 18), ("The Ash Gallery", 15, 5, 28, 16),
             ("The Pyre Walk", 67, 5, 26, 16), ("The Tithe Hall", 84, 34, 20, 20),
             ("The Ember Chapel", 73, 64, 24, 16), ("The Well of Fire", 36, 27, 38, 38)]
    lv = 17
    packs = [
        [(24, 70, "Cinderwell Zealot", lv), (27, 68, "Kiln Hound", lv)],
        [(16, 42, "Cinderwell Pyrecaller", lv), (13, 40, "Cinderwell Zealot", lv)],
        [(30, 13, "Slagborn Elemental", lv + 1), (26, 14, "Kiln Hound", lv), (34, 12, "Kiln Hound", lv)],
        [(80, 13, "Cinderwell Pyrecaller", lv + 1), (84, 14, "Slagborn Elemental", lv + 1)],
        [(94, 44, "Cinderwell Zealot", lv + 1), (91, 41, "Cinderwell Pyrecaller", lv + 1),
         (97, 47, "Kiln Hound", lv + 1)],
    ]
    bosses = [(CW_VORN[0], CW_VORN[1], "Ashcaller Vorn"), (CW_HEART[0], CW_HEART[1], "The Furnace Heart")]
    _close(L, zone, CW_PORTAL, bosses, packs, CW_CHESTS, rooms)

    p = L.prop
    RF = "rf_"
    p("rf_brazier", 49, 82, 4, solid="core")
    p("rf_brazier", 61, 82, 4, solid="core")
    p(RF + "lava_fissure", 30, 74, 3)
    p(RF + "golem_husk", 19, 68, 4, solid="core")
    p(RF + "summoning_circle", 16, 44, 4)
    p(RF + "cult_banner", 11, 37, 5, solid="core")
    p(RF + "cult_banner", 21, 37, 5, solid="core")
    p(RF + "skull_spears", 37, 11, 4, solid="core")
    p(RF + "obsidian_spikes", 21, 10, 4, solid="core")
    p(RF + "steam_vent", 48, 11, 3)
    p(RF + "lava_stalagmite", 74, 9, 6, solid="core")
    p(RF + "fallen_pillar", 86, 16, 3)
    p(RF + "sacrificial_altar", 96, 40, 4, solid="core")
    p(RF + "prison_cage", 89, 47, 4, solid="core")
    p(RF + "shackle_frame", 99, 49, 4, solid="core")
    p(RF + "obsidian_throne", 84, 69, 5, solid="core", avoid=2)
    p(RF + "cult_circle", 80, 76, 3)
    p(RF + "brazier", 90, 76, 4, solid="core")
    p(RF + "void_crystals", 51, 44, 3, near_ok=True)
    L.finish([CW_PORTAL, CW_VORN, CW_HEART] + CW_CHESTS)
    return zone, L


# ============================================================================ THE DREAMING ROOT
DR_PORTAL = (60, 88)
DR_HUB = (60, 50)
DR_BOSS = (60, 12)
DR_CHESTS = [(60, 7), (14, 48)]
DR_POOLS = [(60, 52, 7.5, 5.0, 0.6), (104, 50, 4.0, 3.0, 1.9)]


def build_dreaming_root():
    zone, L = _layer(
        "The Dreaming Root", 120, 94,
        "Below the caverns the druids never mapped, the roots of the Barrens drink from a pool that "
        "dreams. The Fang that came down here stopped waking up, and kept walking.",
        "Central Barrens", DR_PORTAL)
    b = L.b
    cx, cy = DR_HUB
    cavern(b, 60, 84, 8, 4, 0, 0.5)                                    # The Rootfall
    tube(b, [(60, 80), (60, 70), (60, 63)], 4, ph=0.3)
    disc(b, cx, cy, 13, ph=0.9)                                        # The Sleeper's Pool
    # five spokes out to five root chambers
    spokes = [(196, 22, 74), (152, 98, 74), (-20, 104, 50), (-56, 88, 20), (-124, 30, 20)]
    for ang, ex, ey in spokes:
        a = math.radians(ang)
        tube(b, [(cx + 12 * math.cos(a), cy + 12 * math.sin(a)), (ex, ey)], 3, ph=ang * 0.01)
    cavern(b, 22, 74, 9, 6, 15, 1.4)                                   # The Thornbed
    cavern(b, 98, 74, 9, 6, -15, 2.1)                                  # The Withering Hollow
    cavern(b, 104, 50, 9, 8, 0, 0.8)                                   # The Moth Gallery
    cavern(b, 88, 20, 10, 7, 20, 1.1)                                  # The Sap Vault
    cavern(b, 30, 20, 10, 7, -20, 2.6)                                 # The Weeping Bower
    cavern(b, 14, 48, 6, 7, 0, 0.2)                                    # a dead end with a hoard
    tube(b, [(21, 70), (17, 60), (15, 52)], 3, ph=0.4)
    # the loop: the five chambers joined round the outside
    tube(b, [(30, 74), (45, 78), (52, 80)], 3, ph=0.7)
    tube(b, [(68, 80), (80, 78), (90, 74)], 3, ph=1.2)
    tube(b, [(100, 67), (104, 60), (104, 57)], 3, ph=0.1)
    tube(b, [(103, 42), (98, 33), (93, 26)], 3, ph=1.9)
    tube(b, [(38, 18), (48, 15), (54, 14)], 3, ph=0.6)
    tube(b, [(80, 16), (72, 14), (66, 13)], 3, ph=2.0)
    cavern(b, 60, 11, 8, 6, 0, 1.6)                                    # The Dreamer's Bed
    _apply_pools(zone, DR_POOLS, shallow_only=True)

    rooms = [("The Rootfall", 50, 78, 20, 14), ("The Sleeper's Pool", 46, 36, 28, 28),
             ("The Thornbed", 11, 66, 22, 16), ("The Withering Hollow", 87, 66, 22, 16),
             ("The Moth Gallery", 94, 40, 22, 20), ("The Sap Vault", 76, 11, 24, 18),
             ("The Weeping Bower", 18, 11, 24, 18), ("The Dreamer's Bed", 50, 3, 20, 16)]
    lv = 23
    packs = [
        [(22, 74, "Dreamrot Lasher", lv), (25, 72, "Sleepwalking Druid", lv)],
        [(98, 74, "Nightmare Deviate", lv), (95, 72, "Nightmare Deviate", lv)],
        [(104, 46, "Sleepwalking Druid", lv + 1), (100, 50, "Dreamrot Lasher", lv), (108, 52, "Nightmare Deviate", lv)],
        [(88, 20, "Dreamrot Lasher", lv + 1), (92, 22, "Sleepwalking Druid", lv + 1)],
        [(30, 20, "Nightmare Deviate", lv + 1), (27, 22, "Dreamrot Lasher", lv + 1), (34, 18, "Sleepwalking Druid", lv + 1)],
    ]
    bosses = [(DR_BOSS[0], DR_BOSS[1], "Vel'dran the Unwaking")]
    _close(L, zone, DR_PORTAL, bosses, packs, DR_CHESTS, rooms)

    p = L.prop
    p("ashx_nightmare_root_pillar", 52, 86, 6, solid="core", where=ASHX)
    p("ashx_nightmare_root_pillar", 68, 86, 6, solid="core", where=ASHX)
    p("ashx_nightmare_thorns", 48, 44, 3, where=ASHX)
    p("ashx_nightmare_cocoon", 72, 44, 4, solid="core", where=ASHX)
    p("ashx_nightmare_cocoon", 17, 76, 4, solid="core", where=ASHX)
    p("ashx_nightmare_thorns", 27, 77, 3, where=ASHX)
    p("ud_shroom_tall_violet", 102, 77, 5, solid="core", where=UDP)
    p("ashx_nightmare_root_pillar", 110, 47, 6, solid="core", where=ASHX)
    p("ud_shroom_cluster_blue", 99, 45, 3, where=UDP)
    p("den_glow_mushrooms", 84, 22, 3)
    p("ashx_corrupt_moonwell", 90, 18, 4, solid="core", where=ASHX)
    p("ashx_nightmare_cocoon", 25, 17, 4, solid="core", where=ASHX)
    p("ud_moss_curtain", 34, 16, 4, where=UDP)
    p("ashx_corrupt_ancient_tree", 54, 9, 7, solid="core", where=ASHX)
    p("ashx_nightmare_thorns", 66, 14, 3, where=ASHX)
    L.finish([DR_PORTAL, DR_BOSS] + DR_CHESTS)
    return zone, L


# ============================================================================ THE OSSUARY BELOW
OB_PORTAL = (14, 88)
OB_GNASHER = (78, 50)
OB_SHADE = (60, 12)
OB_CHESTS = [(60, 8), (100, 80)]


def build_ossuary():
    zone, L = _layer(
        "The Ossuary Below", 116, 94,
        "The Keep was built on a burial ground older than Gilneas, and Arugal found it. What he "
        "kept down here was never meant to come back up.",
        "Silverpine South", OB_PORTAL)
    b = L.b
    # one long gorge, switching back and forth up the map, niches in its walls
    cavern(b, 14, 84, 7, 5, 0, 0.2)                                    # The Bone Stair
    tube(b, [(18, 80), (30, 78), (44, 80), (60, 82), (76, 80), (92, 76)], 4, 5, ph=0.4)
    cavern(b, 98, 74, 9, 7, -10, 1.0)                                  # The Gnawed Gate
    cavern(b, 104, 82, 5, 4, 0, 0.6)                                   # a niche with a hoard
    tube(b, [(98, 66), (92, 58), (84, 54)], 4, ph=0.9)
    cavern(b, 76, 50, 11, 8, 10, 2.2)                                  # The Kennel of Bones
    tube(b, [(65, 50), (52, 54), (38, 56), (26, 52)], 4, ph=1.5)
    cavern(b, 20, 46, 9, 8, 0, 0.8)                                    # The Weeping Niches
    tube(b, [(20, 40), (24, 30), (32, 24), (42, 21), (52, 18)], 4, ph=0.2)
    cavern(b, 60, 15, 13, 10, 0, 1.3)                                  # The Charnel Throne
    # niches along the gorge: little side pockets, the gorge's walls opened back into bone
    for (nx, ny), (gx, gy) in (((36, 73), (36, 79)), ((52, 88), (52, 81)), ((68, 74), (68, 81)),
                               ((46, 48), (46, 54)), ((34, 62), (34, 56)), ((12, 36), (17, 40)),
                               ((36, 17), (36, 23))):
        cavern(b, nx, ny, 3, 2, 0, nx * 0.1)
        tube(b, [(nx, ny), (gx, gy)], 2)

    rooms = [("The Bone Stair", 6, 78, 18, 14), ("The Long Gorge", 24, 70, 70, 18),
             ("The Gnawed Gate", 88, 66, 22, 16), ("The Kennel of Bones", 64, 41, 26, 18),
             ("The Weeping Niches", 10, 37, 22, 18), ("The Charnel Throne", 46, 4, 28, 22)]
    lv = 26
    packs = [
        [(44, 80, "Ossuary Ghoul", lv), (40, 79, "Ossuary Ghoul", lv)],
        [(98, 74, "Bonewrought Worgen", lv), (95, 72, "Whispering Shade", lv)],
        [(40, 56, "Ossuary Ghoul", lv + 1), (36, 55, "Bonewrought Worgen", lv + 1)],
        [(20, 46, "Whispering Shade", lv + 1), (17, 44, "Whispering Shade", lv + 1), (23, 48, "Ossuary Ghoul", lv + 1)],
        [(42, 22, "Bonewrought Worgen", lv + 1), (46, 20, "Whispering Shade", lv + 1)],
    ]
    bosses = [(OB_GNASHER[0], OB_GNASHER[1], "Gnasher, the Bone-Fed"),
              (OB_SHADE[0], OB_SHADE[1], "The Archmage's Shade")]
    _close(L, zone, OB_PORTAL, bosses, packs, OB_CHESTS, rooms)

    p = L.prop
    p("skull_pile", 10, 82, 3)
    p("sarcophagus", 30, 76, 4, solid="core")
    p("bbc_skull_pile", 58, 79, 3)
    p("sarcophagus", 74, 77, 4, solid="core")
    p("worgen_gargoyle", 93, 70, 5, solid="core")
    p("worgen_gargoyle", 103, 70, 5, solid="core")
    p("kennel_cage_empty", 70, 46, 4, solid="core")
    p("kennel_cage_worg", 85, 46, 4, solid="core")
    p("vot_beast_ribcage", 73, 55, 3)
    p("den_leg_bones", 82, 54, 2)
    p("ashx_burial_niche_wall", 16, 40, 5, solid="core", where=ASHX)
    p("ashx_burial_niche_wall", 25, 41, 5, solid="core", where=ASHX)
    p("candelabra", 20, 52, 3)
    p("bbc_throne", 60, 9, 5, solid="core", avoid=1)
    p("sarcophagus", 51, 16, 4, solid="core")
    p("sarcophagus", 69, 16, 4, solid="core")
    p("spirit_brazier", 50, 11, 4, solid="core")
    p("spirit_brazier", 70, 11, 4, solid="core")
    p("crypt_mausoleum", 54, 23, 6, solid="core", where=HF)
    L.finish([OB_PORTAL, OB_GNASHER, OB_SHADE] + OB_CHESTS)
    return zone, L


# ========================================================================== THE LIGHTLESS REACH
LR_PORTAL = (60, 96)
LR_BOSS = (60, 22)
LR_CHESTS = [(60, 15), (16, 30)]
LR_ISLES = [(60, 84, 9, 5), (30, 70, 8, 6), (90, 66, 8, 6), (58, 52, 8, 6), (24, 34, 9, 7),
            (96, 32, 8, 7), (60, 22, 12, 8)]
LR_WADES = [((60, 79), (36, 72)), ((60, 79), (84, 68)), ((36, 67), (54, 55)), ((84, 63), (63, 54)),
            ((54, 48), (30, 38)), ((63, 48), (90, 36)), ((30, 30), (50, 24)), ((90, 28), (70, 22))]


def build_lightless_reach():
    zone, L = _layer(
        "The Lightless Reach", 120, 102,
        "Under Aku'mai's lair the water goes on in the dark. The Twilight's Hammer drowned a temple "
        "here to wake what sleeps under it, and the islands are all that's left above the water.",
        "Ashenvale West", LR_PORTAL)
    b = L.b
    # the whole gallery is black water; the islands stand up out of it, wading paths between
    for y in range(6, 100):
        for x in range(4, 116):
            dx, dy = (x + 0.5 - 60) / 56, (y + 0.5 - 52) / 47
            if dx * dx + dy * dy <= 1.0 + 0.04 * math.sin(4 * math.atan2(dy, dx)):
                b._open(x, y, "deep_water")          # deep water blocks by its own tile
    for (ix, iy, rx, ry) in LR_ISLES:
        cavern(b, ix, iy, rx, ry, (ix * 7) % 40 - 20, ix * 0.05, base="dirt")
    for (a, c) in LR_WADES:
        tube(b, [a, ((a[0] + c[0]) / 2 + 3, (a[1] + c[1]) / 2), c], 3, ph=a[0] * 0.03, base="shallow_water")
    cavern(b, 60, 94, 6, 3, 0, 0.1, base="dirt")                       # The Drowned Landing
    tube(b, [(60, 92), (60, 88)], 4, base="dirt")
    cavern(b, 16, 30, 4, 4, 0, 0.4, base="dirt")                       # a ledge with a hoard
    tube(b, [(22, 32), (19, 31)], 3, base="shallow_water")

    rooms = [("The Drowned Landing", 50, 78, 20, 22), ("The Sunken Nave", 20, 62, 22, 16),
             ("The Kelp Chancel", 80, 58, 22, 16), ("The Broken Font", 48, 44, 22, 16),
             ("The Drowned Choir", 12, 25, 24, 18), ("The Black Altar", 86, 23, 22, 18),
             ("Ul'gotha's Hollow", 46, 12, 28, 20)]
    lv = 29
    packs = [
        [(30, 70, "Reach Myrmidon", lv), (33, 68, "Twilight Drowner", lv)],
        [(90, 66, "Lightless Lurker", lv), (87, 64, "Reach Myrmidon", lv)],
        [(58, 52, "Twilight Drowner", lv + 1), (55, 50, "Twilight Drowner", lv + 1), (61, 54, "Lightless Lurker", lv)],
        [(24, 34, "Reach Myrmidon", lv + 1), (27, 36, "Lightless Lurker", lv + 1)],
        [(96, 32, "Reach Myrmidon", lv + 1), (93, 30, "Twilight Drowner", lv + 1), (99, 34, "Lightless Lurker", lv + 1)],
    ]
    bosses = [(LR_BOSS[0], LR_BOSS[1], "Ul'gotha, Mother of the Deep")]
    _close(L, zone, LR_PORTAL, bosses, packs, LR_CHESTS, rooms)

    p = L.prop
    p("grotto_naga_column", 55, 93, 5, solid="core")
    p("grotto_naga_column", 65, 93, 5, solid="core")
    p("naga_statue", 26, 68, 5, solid="core", where=NG)
    p("grotto_kelp_stalks", 94, 69, 4)
    p("twilight_altar", 92, 28, 4, solid="core")
    p("grotto_naga_rune_stone", 58, 49, 4, solid="core")
    p("serpent_skeleton", 20, 37, 4, where=NG)
    p("grotto_glow_coral", 99, 36, 3)
    p("grotto_naga_throne", 60, 17, 6, solid="core", avoid=2)
    p("coral_blue", 51, 24, 3, where=SB)
    p("coral_red", 69, 25, 3, where=SB)
    L.finish([LR_PORTAL, LR_BOSS] + LR_CHESTS)
    return zone, L


# ============================================================================== THE BLOOD PITS
BP_PORTAL = (50, 92)
BP_JAKESH = (50, 46)
BP_SKRELL = (50, 10)
BP_CHESTS = [(50, 7), (8, 46)]


def build_blood_pits():
    zone, L = _layer(
        "The Blood Pits", 100, 96,
        "Before the Gurubashi built their arena they fought in the dark, in pits under the stone, "
        "for gods who liked the taste. Some of the fighters were never let out.",
        "Eastern Kingdoms - Stranglethorn", BP_PORTAL)
    b = L.b
    # the spine, south to north, with the pit at the crossing and the two arms of cells
    cavern(b, 50, 88, 8, 4, 0, 0.3, base="sand")                       # The Chain Stair
    tube(b, [(50, 86), (50, 72), (50, 56)], 5, base="sand")
    disc(b, 50, 47, 14, ph=0.8, base="sand")                           # The Old Pit
    tube(b, [(50, 33), (50, 26), (50, 19)], 5, base="sand")
    cavern(b, 50, 11, 12, 7, 0, 1.4, base="sand")                      # The Ravager's Den
    # west arm and east arm of holding cells, each a short corridor with cells off it
    tube(b, [(36, 47), (26, 47), (14, 47)], 4, base="sand")
    tube(b, [(64, 47), (74, 47), (86, 47)], 4, base="sand")
    cavern(b, 8, 47, 4, 5, 0, 0.5, base="sand")
    cavern(b, 90, 47, 6, 6, 0, 1.0, base="sand")                       # The Bloodcaller's Cell
    for (cx, cy) in ((24, 39), (24, 55), (32, 38), (68, 38), (76, 56), (68, 56)):
        cavern(b, cx, cy, 4, 3, 0, cx * 0.07, base="sand")
        tube(b, [(cx, cy), (cx, 47)], 3, base="sand")
    # a back way from the den round to the east arm, so the cross is a loop at the top
    tube(b, [(60, 9), (76, 14), (88, 26), (90, 41)], 3, ph=1.1, base="sand")

    rooms = [("The Chain Stair", 40, 82, 20, 14), ("The Old Pit", 34, 31, 32, 32),
             ("The West Cells", 4, 34, 30, 26), ("The East Cells", 64, 34, 32, 26),
             ("The Ravager's Den", 36, 2, 28, 18)]
    lv = 38
    packs = [
        [(50, 74, "Pit-Bound Gladiator", lv), (48, 70, "Pit-Bound Gladiator", lv)],
        [(24, 47, "Blood Ravager", lv), (21, 46, "Blood Ravager", lv), (28, 48, "Pit Bloodcaller", lv)],
        [(76, 47, "Pit-Bound Gladiator", lv + 1), (79, 46, "Pit Bloodcaller", lv + 1)],
        [(90, 47, "Pit Bloodcaller", lv + 1), (88, 45, "Blood Ravager", lv + 1), (92, 49, "Pit-Bound Gladiator", lv + 1)],
        [(50, 24, "Blood Ravager", lv + 1), (50, 28, "Blood Ravager", lv + 1)],
    ]
    bosses = [(BP_JAKESH[0], BP_JAKESH[1], "Ja'kesh the Unchained"),
              (BP_SKRELL[0], BP_SKRELL[1], "Skrell, Mother of Ravagers")]
    _close(L, zone, BP_PORTAL, bosses, packs, BP_CHESTS, rooms)

    p = L.prop
    p("stv_arena_gate", 50, 66, 5, where=STV, near_ok=True)
    p("rf_skull_spears", 42, 86, 4, solid="core")
    p("rf_skull_spears", 58, 86, 4, solid="core")
    p("stv_bone_arch", 50, 33, 5, where=STV, near_ok=True)
    p("stv_chain_heap", 40, 54, 3, where=STV)
    p("stv_arena_weapon_rack", 60, 40, 4, solid="core", where=STV)
    p("rf_prison_cage", 24, 37, 4, solid="core")
    p("rf_prison_cage", 68, 37, 4, solid="core")
    p("rf_shackle_frame", 32, 37, 4, solid="core")
    p("rf_sacrificial_altar", 92, 44, 4, solid="core")
    p("stv_raptor_nest", 44, 8, 3, where=STV)
    p("stv_raptor_nest", 57, 13, 3, where=STV)
    p("vot_beast_ribcage", 40, 12, 3)
    L.finish([BP_PORTAL, BP_JAKESH, BP_SKRELL] + BP_CHESTS)
    return zone, L


# ========================================================================= THE UNWRITTEN STACKS
US_PORTAL = (56, 90)
US_BOSS = (56, 12)
US_MARGIN = (98, 44)
US_CHESTS = [(56, 7), (14, 13)]


def build_unwritten_stacks():
    zone, L = _layer(
        "The Unwritten Stacks", 112, 96,
        "The Bloom grew a library before it grew anything else: shelf on shelf of fungus pressed into "
        "pages, nobody's knowledge, written down by something that only wanted to be read.",
        "The Crystalline Underdark", US_PORTAL)
    b = L.b
    cavern(b, 56, 86, 8, 4, 0, 0.2, base="stone")                      # The Lending Stair
    tube(b, [(56, 82), (56, 74)], 4, base="stone")
    # the stacks: a block of floor, then shelves stood back into it as walls, leaving aisles
    for y in range(26, 74):
        for x in range(20, 94):
            b._open(x, y, "stone")
    for row, y0 in enumerate(range(30, 70, 8)):
        for x0 in range(24, 90, 12):
            gap = (x0 // 12 + row) % 3 == 0
            if gap:
                continue
            for y in range(y0, y0 + 4):
                for x in range(x0, x0 + 8):
                    zone.collision_layer[y][x] = "rock"
    # the reading-room loop round the outside, and the rooms off it
    tube(b, [(20, 74), (12, 60), (12, 40), (16, 24), (14, 17)], 4, base="stone")
    tube(b, [(94, 74), (100, 60), (100, 40), (96, 24)], 4, base="stone")
    cavern(b, 14, 14, 7, 6, 0, 0.6, base="stone")                      # The Restricted Shelf
    cavern(b, 98, 44, 7, 8, 0, 1.4, base="stone")                      # The Margins
    tube(b, [(20, 22), (36, 20), (46, 16)], 4, base="stone")
    tube(b, [(92, 22), (76, 20), (66, 16)], 4, base="stone")
    tube(b, [(56, 26), (56, 20)], 5, base="stone")
    cavern(b, 56, 12, 12, 7, 0, 1.0, base="stone")                     # The Reading Room

    rooms = [("The Lending Stair", 46, 80, 20, 14), ("The Stacks", 18, 24, 78, 52),
             ("The Restricted Shelf", 5, 6, 18, 16), ("The Margins", 90, 34, 18, 20),
             ("The Reading Room", 42, 3, 28, 18)]
    lv = 40
    packs = [
        [(56, 72, "Unbound Folio", lv), (53, 71, "Unbound Folio", lv)],
        [(30, 62, "Stack-Grown Reader", lv), (33, 62, "Spore Archivist", lv)],
        [(80, 54, "Spore Archivist", lv + 1), (77, 54, "Unbound Folio", lv + 1), (82, 46, "Stack-Grown Reader", lv + 1)],
        [(30, 38, "Stack-Grown Reader", lv + 1), (33, 38, "Stack-Grown Reader", lv + 1)],
        [(56, 22, "Spore Archivist", lv + 1), (53, 23, "Unbound Folio", lv + 1), (59, 23, "Unbound Folio", lv + 1)],
    ]
    bosses = [(US_BOSS[0], US_BOSS[1], "The First Draft"), (US_MARGIN[0], US_MARGIN[1], "Marginalia")]
    _close(L, zone, US_PORTAL, bosses, packs, US_CHESTS, rooms)

    p = L.prop
    p("ud_codex_banner", 50, 87, 5, solid="core", where=UDP)
    p("ud_codex_banner", 62, 87, 5, solid="core", where=UDP)
    p("ud_shelf_fungus", 22, 50, 4, solid="core", where=UDP)
    p("ud_specimen_rack", 92, 64, 4, solid="core", where=UDP)
    p("ud_field_desk", 40, 46, 3, solid="core", where=UDP)
    p("ud_shroom_squat_ochre", 70, 66, 3, where=UDP)
    p("ud_codex_crates", 12, 18, 3, solid="core", where=UDP)
    p("wizard_desk", 98, 40, 4, solid="core", near_ok=True)
    p("bbc_bookshelf", 104, 48, 4, solid="core")
    p("ud_arcane_brazier", 48, 9, 4, solid="core", where=UDP)
    p("ud_arcane_brazier", 64, 9, 4, solid="core", where=UDP)
    p("bbc_bookshelf", 44, 15, 4, solid="core")
    p("bbc_bookshelf", 68, 15, 4, solid="core")
    p("ud_fungal_node", 56, 19, 3, where=UDP, near_ok=True)
    L.finish([US_PORTAL, US_BOSS, US_MARGIN] + US_CHESTS)
    return zone, L


# ======================================================================= THE WORLD-ROOT HOLLOW
# A FRONTIER ZONE (world/hidden_zones.py): a hidden zone inside a hidden zone. Kyle named this one
# and said where its door is ("hidden behind a massive tree (Frontier zone can be called The
# World-Root Hollow)"). Inside the great tree's roots: a ROOT-WEB, the one shape no cave in the game
# has - a knot of tunnels that cross and re-cross between hollows, so there is no single way
# through and every chamber has two or three ways out. The heartwood is in the middle; the
# root-father sleeps at the very bottom of the tree, which is the top of the map.
WR_PORTAL = (56, 94)
WR_SAP = (56, 50)
WR_FATHER = (56, 10)
WR_GNARL = (12, 30)
WR_CHESTS = [(56, 7), (100, 30), (14, 78)]


def build_world_root():
    zone, L = _layer(
        "The World-Root Hollow", 112, 100,
        "Inside the roots of a tree older than the Darkspear: hollows full of amber light, sap that "
        "moves on its own, and something at the bottom that the whole tree is growing round.",
        "The Tanglewood Shoals", WR_PORTAL)
    b = L.b
    cavern(b, 56, 90, 9, 4, 0, 0.3)                                    # The Rootgate
    hollows = [(30, 76, 9, 7), (82, 76, 9, 7), (14, 78, 5, 4), (100, 54, 7, 9), (14, 52, 7, 9),
               (34, 30, 10, 7), (80, 30, 10, 7), (100, 30, 5, 5), (12, 30, 6, 6)]
    for n, (hx, hy, rx, ry) in enumerate(hollows):
        cavern(b, hx, hy, rx, ry, (n * 23) % 50 - 25, n * 0.7)
    disc(b, WR_SAP[0], WR_SAP[1], 12, ph=1.1)                          # The Heartwood
    cavern(b, 56, 12, 14, 8, 0, 2.2)                                   # The Root-Father's Bed
    # the web: every hollow tied to two or three others by roots that cross
    web = [((56, 86), (34, 78)), ((56, 86), (78, 78)), ((30, 72), (16, 58)), ((82, 72), (98, 60)),
           ((24, 78), (16, 78)), ((36, 72), (48, 56)), ((76, 72), (64, 56)), ((16, 46), (28, 34)),
           ((98, 48), (84, 34)), ((44, 46), (38, 36)), ((68, 46), (74, 36)), ((40, 28), (52, 16)),
           ((74, 28), (62, 16)), ((86, 30), (98, 30)), ((24, 30), (16, 30)), ((20, 52), (44, 52)),
           ((92, 54), (68, 52)), ((30, 70), (76, 36)), ((82, 70), (36, 36))]
    for n, (a, c) in enumerate(web):
        mid = ((a[0] + c[0]) / 2 + 4 * math.sin(n), (a[1] + c[1]) / 2 + 3 * math.cos(n))
        tube(b, [a, mid, c], 3, ph=n * 0.4)
    _apply_pools(zone, [(56, 50, 4.5, 3.5, 0.9)], shallow_only=True)

    rooms = [("The Rootgate", 46, 84, 20, 12), ("The Amber Hollows", 18, 68, 76, 18),
             ("The Weeping Roots", 6, 42, 20, 22), ("The Sap Galleries", 92, 42, 18, 24),
             ("The Heartwood", 42, 36, 28, 28), ("The Knotted Deep", 22, 20, 70, 20),
             ("The Root-Father's Bed", 40, 2, 32, 20)]
    lv = 18
    packs = [
        [(30, 76, "Hollow Rootling", lv), (27, 74, "Hollow Rootling", lv), (33, 78, "Sapdrunk Bat", lv)],
        [(82, 76, "Heartwood Spider", lv), (85, 74, "Sapdrunk Bat", lv)],
        [(14, 52, "Lost Rootspeaker", lv + 1), (16, 55, "Hollow Rootling", lv)],
        [(100, 54, "Heartwood Spider", lv + 1), (98, 51, "Heartwood Spider", lv + 1)],
        [(34, 30, "Lost Rootspeaker", lv + 1), (31, 28, "Hollow Rootling", lv + 1), (37, 32, "Sapdrunk Bat", lv + 1)],
        [(80, 30, "Heartwood Spider", lv + 1), (83, 32, "Lost Rootspeaker", lv + 1), (77, 28, "Hollow Rootling", lv + 1)],
    ]
    bosses = [(WR_SAP[0], WR_SAP[1] - 4, "Amberheart, the Sap-Mother"),
              (WR_FATHER[0], WR_FATHER[1], "The Root-Father"),
              (WR_GNARL[0], WR_GNARL[1], "Gnarl the Unburied")]
    _close(L, zone, WR_PORTAL, bosses, packs, WR_CHESTS, rooms)

    p = L.prop
    p("ashx_nightmare_root_pillar", 49, 92, 6, solid="core", where=ASHX)
    p("ashx_nightmare_root_pillar", 63, 92, 6, solid="core", where=ASHX)
    p("ud_shroom_cluster_blue", 26, 80, 3, where=UDP)
    p("ud_glow_pool", 86, 80, 3, where=UDP)
    p("ud_shroom_tall_violet", 10, 56, 5, solid="core", where=UDP)
    p("den_glow_mushrooms", 102, 58, 3)
    p("ashx_corrupt_ancient_tree", 56, 44, 7, solid="core", where=ASHX, near_ok=True)
    p("ud_moss_curtain", 30, 26, 4, where=UDP)
    p("ud_fungal_node", 84, 26, 3, where=UDP)
    p("vot_beast_ribcage", 14, 34, 3)
    p("ashx_nightmare_cocoon", 46, 10, 4, solid="core", where=ASHX)
    p("ashx_nightmare_cocoon", 66, 10, 4, solid="core", where=ASHX)
    L.finish([WR_PORTAL, WR_FATHER, WR_GNARL, (WR_SAP[0], WR_SAP[1] - 4)] + WR_CHESTS)
    return zone, L


# ======================================================================= registry for the world
BUILDS = {
    "The Cinderwell": (build_cinderwell, "cinderwell"),
    "The Dreaming Root": (build_dreaming_root, "dreaming_root"),
    "The Ossuary Below": (build_ossuary, "ossuary_below"),
    "The Lightless Reach": (build_lightless_reach, "lightless_reach"),
    "The Blood Pits": (build_blood_pits, "blood_pits"),
    "The Unwritten Stacks": (build_unwritten_stacks, "unwritten_stacks"),
    "The World-Root Hollow": (build_world_root, "world_root_hollow"),
}

#: the portal tile of each layer (its way in and out)
PORTALS = {"The Cinderwell": CW_PORTAL, "The Dreaming Root": DR_PORTAL, "The Ossuary Below": OB_PORTAL,
           "The Lightless Reach": LR_PORTAL, "The Blood Pits": BP_PORTAL, "The Unwritten Stacks": US_PORTAL,
           "The World-Root Hollow": WR_PORTAL}


def generate_all():
    import os
    out = {}
    for name, (build, slug) in BUILDS.items():
        zone, _ = build()
        baked = BAKED.format(slug)
        if os.path.exists(f"{baked}/ground_0_0.jpg"):
            register_baked(zone, baked)
        out[name] = zone
    return out
