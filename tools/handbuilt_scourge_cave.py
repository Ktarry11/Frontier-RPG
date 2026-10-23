"""
Hand-built layout for Eastern Tirisfal's Scourge Cave (2026-10-23, replaces the old generated "cavern" in zone_generator):

  Scourge Cave   90x75   THE RIBCAGE.  The Cult of the Damned's cellar opens onto the bones of something that was far
                         too big to have been alive: a SPINE corridor runs north from the Charnel Maw, four pairs of RIB
                         tunnels loop off it and back (leaving islands of rock between them), and the spine ends in the
                         SKULL THRONE where the Scourge Abomination waits, an eye-socket alcove on each side.
                         Two optional chambers hang off the rib tips: the Bone Pit (west) and the Plague Lab (east).
                         (portal 45,68 / boss Scourge Abomination 45,12)

A CAVE, not a dungeon: boss + the two named rares are pinned (zone.boss_positions), trash comes from the random per-tile
roll (zone.fixed_spawns = False).  Hand-placed mobs are for full multi-boss dungeons only.

Portal contract (world/portal_manager.py): Eastern Tirisfal (52,112) <-> Scourge Cave (45,68); the exit lands at Eastern (52,116).

LAYOUT VARIETY: a spine with looping ribs and a round skull - not a web spiral (Night Web's Hollow), not a cross (Scarlet
Crypt), not a lake hall (the Den), rotunda (Echo) or Durotar's cave shapes.
Prop rule (Kyle): less is more, props logical for the room, a few centrepieces.
"""
from tools.handbuilt_deathknell_caves import _cave, _finish, _subzones          # noqa: F401
from tools.handbuilt_vot_caves import register_baked, DP                        # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube                              # noqa: F401

UC = "assets/tiles/undercity/props/"
EK = "assets/tiles/eastern_kingdoms/props/"
SR = "assets/tiles/skull_rock/props/"
BAKED = "assets/tiles/scourge_cave/baked"

W, H = 90, 75
PORTAL = (45, 68)
BOSS = (45, 12)
RARES = [(11, 40), (79, 28)]          # Ghoulmaster Krag (the Bone Pit, W) and Plaguemaster Orvyn (the Plague Lab, E)
CHESTS = [(34, 9), (56, 9), (9, 46), (84, 33)]
RIB_Y = (56, 45, 34, 23)              # where each rib pair leaves the spine (south to north)
RIB_OUT = (16, 21, 21, 15)            # how far each pair bulges out - widest at mid-ribcage, like the real thing
RIB_LEN = 9                           # a rib re-joins the spine this many tiles further north


def rib(side, k):
    """Control points of rib `k` on `side` (-1 west, +1 east): out from the spine, round the bulge, back in."""
    y0, out = RIB_Y[k], RIB_OUT[k]
    cx = 45
    return [(cx, y0), (cx + side * out * 0.55, y0 - 1), (cx + side * out, y0 - RIB_LEN * 0.5),
            (cx + side * out * 0.55, y0 - RIB_LEN + 1), (cx, y0 - RIB_LEN)]


def build_scourge():
    zone, L = _cave("Scourge Cave", W, H,
                    "The Cult of the Damned dug into the bones of something huge: a spine of tunnels, ribs looping off it, "
                    "and a skull at the far end.", PORTAL)
    zone.region = "Eastern Tirisfal"
    b = L.b

    # the Charnel Maw (entrance) and the spine
    cavern(b, 45, 64, 13, 6, 0, 0.5)
    tube(b, [(45, 60), (45, 48), (45, 36), (45, 24)], 5.0, 5.0, ph=0.4)
    # four pairs of ribs: leave the spine, bulge out, come back in
    for k in range(4):
        for side in (-1, 1):
            tube(b, rib(side, k), 3.8, 3.8, ph=0.5 * k + (0.3 if side > 0 else 0.0))
    # the Skull Throne: a round cranium, a jaw of tunnel into the spine, an eye-socket alcove either side
    cavern(b, 45, 13, 15, 9, 0, 0.8)
    tube(b, [(45, 24), (45, 20)], 5.0)
    cavern(b, 34, 9, 3.4, 3.2, 0, 0.2)
    cavern(b, 56, 9, 3.4, 3.2, 0, 1.1)
    cavern(b, 45, 4, 5, 2.2, 0, 0.6)                                   # behind the skull (the cranium's back wall)
    # optional chambers off the rib tips
    cavern(b, 11, 41, 9, 7, -15, 1.0)                                  # the Bone Pit (W), off the second pair's bulge
    tube(b, [(24, 41), (18, 41), (14, 41)], 3.4, ph=0.2)
    cavern(b, 79, 29, 9, 7, 15, 1.9)                                   # the Plague Lab (E), off the third pair's bulge
    tube(b, [(66, 30), (73, 29), (76, 29)], 3.4, ph=0.9)
    # a pocket where the first west rib meets the Maw: the chest alcove SW
    cavern(b, 19, 63, 5, 4, 10, 0.4)
    tube(b, [(36, 62), (24, 63)], 3.2, ph=0.6)

    _subzones(zone, [("The Charnel Maw", 31, 56, 28, 17), ("The Ribways", 18, 22, 54, 38),
                     ("The Spine", 40, 20, 10, 40), ("The Bone Pit", 1, 33, 21, 17),
                     ("The Plague Lab", 68, 21, 21, 17), ("The Skull Throne", 28, 1, 35, 22),
                     ("The Hollow Alcove", 12, 58, 14, 11)],
              "Scourge Cave")

    _finish(L, zone, PORTAL, [(BOSS[0], BOSS[1], "Scourge Abomination"),
                              (RARES[0][0], RARES[0][1], "Ghoulmaster Krag"),
                              (RARES[1][0], RARES[1][1], "Plaguemaster Orvyn")], CHESTS)
    L.critical += RARES

    p = L.prop
    # the Maw: braziers at the mouth, a grave-hand in the soil
    p("spirit_brazier", 39, 66, 4)
    p("spirit_brazier", 51, 66, 4)
    p("ek_grave_hand", 40, 62, 3, where=EK)
    p("skull_pile", 53, 62, 3)
    # the spine: just a few bones
    p("uc_bone_heap", 43, 53, 3, where=UC)
    p("skull_pile", 47, 41, 3)
    p("den_leg_bones", 47, 31, 2)
    # the hollow alcove (SW chest)
    p("uc_coffin_stack", 17, 62, 4, where=UC)
    p("ek_open_grave", 21, 65, 3, where=EK)
    # the Bone Pit (W): the giant's own ribs, heaped bone, a rare to find
    p("vot_beast_ribcage", 8, 38, 6, solid="core")
    p("skull_pile", 14, 45, 3)
    p("uc_bone_heap", 6, 45, 3, where=UC)
    p("ek_open_grave", 15, 37, 3, where=EK)
    p("den_leg_bones", 12, 44, 2)
    # the Plague Lab (E): the cult's work-benches
    p("uc_alchemy_table", 74, 25, 3, where=UC, solid="core")
    p("uc_plague_vat", 83, 24, 4, where=UC, solid="core")
    p("uc_plague_vat", 84, 28, 4, where=UC, solid="core")
    p("uc_operating_table", 74, 33, 4, where=UC, solid="core")
    p("uc_jar_shelf", 79, 24, 4, where=UC, solid="core")
    p("uc_cage_cell", 87, 32, 4, where=UC, solid="core")
    # the Skull Throne: runed pillars at the jaw, the altar behind the Abomination, a summoning circle at its feet
    p("bbc_rune_pillar", 38, 20, 5, solid="core")
    p("bbc_rune_pillar", 52, 20, 5, solid="core")
    p("rf_sacrificial_altar", 45, 6, 4, solid="core", avoid=2)
    p("rf_skull_spears", 41, 17, 4)
    p("rf_skull_spears", 49, 17, 4)
    p("spirit_brazier", 33, 12, 4)
    p("spirit_brazier", 57, 12, 4)
    p("uc_bone_heap", 38, 6, 3, where=UC)
    p("skull_pile", 53, 7, 3)

    L.finish([PORTAL, BOSS] + CHESTS + RARES)
    return zone, L


def generate_scourge_cave():
    zone, _ = build_scourge()
    register_baked(zone, BAKED)
    return zone
