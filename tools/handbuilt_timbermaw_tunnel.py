"""
Hand-built Timbermaw Tunnel (180x200): the furbolgs' tunnel through the mountain above North Felwood, levels 53-56.

Kyle, 17 Nov 2026: "add timbermaw hold? We have the art for it and we can add the reputation. And since it won't have
mobs it'll be an easy build!", then "So timbermaw is a tunnel bro! You know this", "It'll eventually go to winterspring
and moonglade", "Timbermaw hold will be in Azshara!" and "Make the tunnel massive bro!" So this is the TUNNEL, the way
Classic has it, and big: a long climb through the mountain with the Timbermaw camped along it, the south mouth open
onto Felwood and the two far ends built and shut. Timbermaw Hold itself, the town, is the furbolgs' home in Azshara
and comes with Azshara (52-59).

Nothing hostile lives here. The Timbermaw keep the tunnel, and they've set up a waystation in it to deal with Felwood.

ARCHETYPE: THE LONG CLIMB.  One road winds up the mountain's inside and opens into a run of halls on the way. It
forks twice: west from the Waystation to Selva's spring and on toward Moonglade, and round the east side through the
Honey Galleries, which loops back to the Root Hall so the climb has two ways up its middle.

    the south mouth (90,196) <- North Felwood (94,4), the top of its spine road
      |  the switchbacks (and a dead end west to the Storeroom)
    THE LOWER GALLERIES: Pathfinder Grosk, watching the climb from Felwood
      |
    THE WAYSTATION: the fire, the provisioner, the featherkeeper (the quartermaster went home to the Hold)
      |------- west: the Long Gallery -> SELVA'S SPRING (the lake) -> the Moonglade passage (shut: the roof's down)
      |------- east: THE HONEY GALLERIES (Honeykeeper Tova) -> round and back up to the Root Hall
      |              and on: THE EAST PASSAGE -> the door to Timbermaw Hold in Azshara (open since 17 Nov 2026)
      |
    THE ROOT HALL: the mountain's oldest roots, hanging through the roof
      |
    THE ELDERS' REST: where the Elders sat while the tunnel was the only way out. Kyle, 17 Nov 2026: the leader and
      the quartermaster "will be in timbermaw hold and not in the tunnel", so Elder Haldor and Bruna Honeyhide have
      gone home up the East Passage; the tunnel's other seven stay
      |
    the Winterspring passage (shut: the roof's down), Warden Durn Rockpelt

Painted by tools/bake_ashenvale_dungeons.py timbermaw_tunnel (Moonwell Hollow's root-earth floor and rock walls).

HARD CONTRACTS (world/portal_manager.py)
  portal   (90,196) <-> North Felwood (94,4): you arrive at (90,194) coming in and (94,7) going out
  portal   (177,152) <-> Timbermaw Hold (1,108), the end of the East Passage: you arrive at (174,152) coming in and
           (4,108) going out
  portal   (12,34) <-> Moonglade (156,169), the Moonglade passage's end (opened 18 Nov 2026, when Moonglade was built):
           you arrive at (12,36) coming back and (156,165) going in
  later    the Winterspring passage's end (146,8) becomes a door when Winterspring exists; its rockfall comes out then
  NPC ids  tm_*, written by tools/build_timbermaw_hold.py from NPC_POSITIONS
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, DP, register_baked, _apply_pools  # noqa: F401
from tools.handbuilt_echo_caves import cavern, tube

NAME = "Timbermaw Tunnel"
KEY = "timbermaw_tunnel"
BAKED = "assets/tiles/timbermaw_tunnel/baked"
W, H = 180, 200
PORTAL = (90, 196)
#: the east passage's end (17 Nov 2026): the door through to Timbermaw Hold in Azshara
EAST_PORTAL = (177, 152)
START = (90, 192)
#: the Moonglade passage's end (18 Nov 2026): the way up into Moonglade
MOON_PORTAL = (12, 34)
#: where the shut passage ends; a door when Winterspring exists
LATER_DOORS = {(146, 8): "Winterspring"}

PATHS = {   # (points, width at start, width at end)
    # the switchbacks up from Felwood
    "climb":   ([(90, 197), (90, 186), (78, 176), (94, 164), (80, 152), (72, 144)], 6.0, 6.5),
    # the Lower Galleries up to the Waystation
    "lower":   ([(72, 136), (80, 126), (88, 118)], 6.5, 7.0),
    # the Waystation up to the Root Hall: the main road
    "main":    ([(94, 98), (102, 88), (112, 78), (118, 70)], 6.0, 6.0),
    # west: the Long Gallery to Selva's spring, and on toward Moonglade
    "gallery": ([(70, 106), (56, 100), (44, 92), (36, 82)], 5.5, 5.5),
    "moon":    ([(26, 66), (20, 54), (14, 42), (12, 34)], 5.0, 4.4),
    # east, and on: the long East Passage out of the Honey Galleries, down and round to the door to Timbermaw Hold
    "east":    ([(158, 100), (168, 114), (162, 128), (170, 142), (178, 152)], 5.0, 5.0),
    # east: round through the Honey Galleries and back up to the Root Hall
    "honey":   ([(110, 110), (128, 116), (142, 108)], 5.5, 5.5),
    "honeyup": ([(150, 86), (146, 74), (134, 68)], 5.0, 5.0),
    # the Root Hall up to the Elders' Rest, and on to the Winterspring passage
    "upper":   ([(122, 58), (126, 48), (124, 40)], 5.5, 5.5),
    "winter":  ([(132, 26), (140, 18), (146, 8)], 5.0, 4.4),
    # a dead end off the switchbacks, where the Timbermaw store what they don't need yet
    "store":   ([(80, 152), (62, 160), (46, 164)], 4.6, 4.2),
}
ROOMS = {   # (cx, cy, rx, ry, rot, phase, name)
    "mouth":      (90, 190, 10, 6, 0, 0.4, "The South Mouth"),
    "lower":      (70, 140, 14, 8, 10, 0.9, "The Lower Galleries"),
    "store":      (42, 164, 9, 6, 0, 1.2, "The Storeroom"),
    "waystation": (90, 106, 24, 13, 0, 1.5, "The Waystation"),
    "spring":     (30, 76, 14, 10, 0, 1.9, "Selva's Spring"),
    "moon":       (12, 36, 7, 6, 0, 2.3, "The Moonglade Passage"),
    "honey":      (148, 98, 12, 12, 0, 2.6, "The Honey Galleries"),
    "roots":      (122, 66, 16, 9, 0, 2.9, "The Root Hall"),
    "elders":     (122, 32, 17, 10, 0, 3.3, "The Elders' Rest"),
    "winter":     (146, 10, 8, 5, 0, 3.7, "The Winterspring Passage"),
    "eastgate":   (171, 150, 7, 6, 0, 4.1, "The East Passage"),
}
#: Selva's spring, a lake in the mountain; and the drip pools in the Lower Galleries and the Root Hall
POOLS = [(28, 74, 7.5, 4.6, 0.3), (64, 142, 3.0, 2.0, 0.6), (130, 66, 3.2, 2.2, 1.1)]

NPC_POSITIONS = {
    "tm_south_warden":  (85, 188),    # Warden Bramblecoat, at the south mouth
    "tm_pathfinder":    (76, 138),    # Pathfinder Grosk, the Lower Galleries, watching the climb from Felwood
    "tm_provisioner":   (76, 104),    # Provisioner Orbo, the Waystation's west side
    "tm_featherkeeper": (86, 100),    # Featherkeeper Imna, by the fire
    "tm_honeykeeper":   (146, 102),   # Honeykeeper Tova, the Honey Galleries
    "tm_windtalker":    (38, 80),     # Windtalker Selva Brightpelt, on the spring's shore
    "tm_north_warden":  (143, 14),    # Warden Durn Rockpelt, at the Winterspring rockfall
}


def build_tunnel():
    zone = Tilemap(NAME, W, H,
                   "The Timbermaw's tunnel through the mountain above Felwood: a long climb past its halls, a fire "
                   "at the waystation, a lake in the dark, and two passages the roof came down on.")
    # a town under the mountain, like Onyxhollow: not a cave, so nothing spawns and you can ride the climb
    zone.is_cave = False
    zone.is_town = True
    zone.region = "Kalimdor - Felwood"
    zone.fixed_spawns = True
    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] - 2))
    b = L.b
    for i, (key, (pts, w0, w1)) in enumerate(PATHS.items()):
        tube(b, pts, w0, w1, ph=0.5 + i * 0.9)
    for key, (cx, cy, rx, ry, rot, ph, _n) in ROOMS.items():
        cavern(b, cx, cy, rx, ry, rot, ph)
    # the joins between the paths and the halls they open into
    for pts in (((88, 118), (89, 112)), ((94, 98), (93, 95)), ((70, 106), (74, 106)), ((36, 82), (34, 80)),
                ((26, 66), (28, 68)), ((110, 110), (106, 109)), ((142, 108), (145, 104)), ((150, 86), (149, 90)),
                ((134, 68), (130, 67)), ((118, 70), (116, 68)), ((122, 58), (122, 60)), ((124, 40), (123, 38)),
                ((132, 26), (128, 28)), ((72, 144), (71, 142)), ((46, 164), (48, 164)), ((158, 100), (156, 100))):
        tube(b, list(pts), 5.0, 5.0)
    _apply_pools(zone, POOLS, shallow_only=True)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.collision_layer[py - 1][px] = None
    L.mark("portal", px, py)
    ex, ey = EAST_PORTAL
    for dx in range(0, 4):
        zone.collision_layer[ey][ex - dx] = None
    L.mark("portal", ex, ey)
    mx, my = MOON_PORTAL
    for dy in range(0, 3):
        zone.collision_layer[my + dy][mx] = None
    L.mark("portal", mx, my)
    for npc_id, (x, y) in NPC_POSITIONS.items():
        if not zone.is_walkable(x, y):
            raise AssertionError(f"{NAME}: {npc_id} at ({x},{y}) is not on walkable ground")
        zone.set_tile(x, y, "npc", "interaction")
        L.critical.append((x, y))

    zone.add_subzone(NAME, 0, 0, W, H)
    for key, (cx, cy, rx, ry, rot, ph, name) in ROOMS.items():
        zone.add_subzone(name, int(cx - rx - 2), int(cy - ry - 2), int(2 * rx + 4), int(2 * ry + 4))
    return zone, L


def dress(zone, L):
    from tools.ashenvale_town_kit import INDEX

    def P(name, cx, by, h, **kw):
        kw.setdefault("where", INDEX.get(name, DP))
        return L.prop(name, cx, by, h, **kw)
    # ---- the south mouth: the Timbermaw's totems either side of the way in
    P("furbolg_totem", 83, 193, 5)
    P("furbolg_totem", 97, 193, 5)
    P("den_glow_mushrooms", 95, 186, 3)
    # ---- the switchbacks: stalagmites at the turns, mushrooms in the dark
    for (name, x, y, h) in [("den_stalagmites", 83, 178, 4), ("den_glow_mushrooms", 90, 168, 3),
                            ("den_stalagmite_pair", 88, 158, 4), ("den_glow_mushrooms", 79, 150, 3),
                            ("ash_blue_stalagmite", 96, 162, 6)]:
        P(name, x, y, h)
    # ---- the Lower Galleries
    P("ash_mossy_spire", 62, 136, 7, solid="core")
    P("den_glow_mushrooms", 78, 144, 3)
    P("fern_cluster", 66, 146, 3)
    P("furbolg_totem", 78, 132, 5)
    # ---- the Storeroom: what the Timbermaw don't need yet
    P("ash_supply_crates", 38, 162, 3, solid="core")
    P("ash_supply_crates", 46, 166, 3, solid="core")
    P("ash_log_pile", 40, 168, 3, solid="core")
    P("ash_moon_barrels", 47, 160, 3, solid="core")
    # ---- the Waystation: the fire, the totems, the lodges, the stores
    P("ash_furbolg_bonfire", 90, 104, 5, solid="core")
    P("fw_timbermaw_totem", 80, 96, 7, solid="core")
    P("fw_timbermaw_totem", 100, 96, 7, solid="core")
    P("ash_furbolg_lodge", 110, 102, 8, solid="core")
    P("ash_furbolg_lodge", 70, 100, 8, solid="core")
    P("ash_supply_crates", 108, 112, 3, solid="core")
    P("ash_supply_crates", 72, 112, 3, solid="core")
    P("ash_log_pile", 82, 114, 3, solid="core")
    P("ash_herb_rack", 74, 108, 4, solid="core")
    P("den_glow_mushrooms", 98, 114, 3)
    P("ash_root_curtain", 92, 96, 6)
    # ---- the Long Gallery and Selva's spring
    for (name, x, y, h) in [("den_glow_mushrooms", 58, 98, 3), ("den_stalagmites", 48, 96, 4),
                            ("ash_blue_stalagmite", 42, 88, 6)]:
        P(name, x, y, h)
    P("ash_moonstone_crystals", 18, 70, 5, solid="core")
    P("ash_moonstone_crystals", 40, 72, 4, solid="core")
    P("ash_glow_mushroom_ring", 22, 82, 3)
    P("furbolg_totem", 40, 86, 5)
    P("ash_mossy_spire", 17, 79, 7, solid="core")
    # ---- the Moonglade passage: the rockfall's cleared to the sides, and the moon rune by the way up
    for (x, y, h, name) in [(7, 38, 5, "asp_boulder_lichen"), (17, 37, 5, "asp_boulder")]:
        P(name, x, y, h, solid="core", near_ok=True)
    P("ash_moon_rune_stone", 14, 42, 5)
    # ---- the Honey Galleries
    P("fw_timbermaw_totem", 140, 94, 6, solid="core")
    P("ash_supply_crates", 152, 92, 3, solid="core")
    P("ash_moon_barrels", 154, 104, 3, solid="core")
    P("ash_supply_crates", 142, 106, 3, solid="core")
    P("den_glow_mushrooms", 150, 108, 3)
    # ---- the Root Hall: the mountain's oldest roots, hanging through the roof
    P("ash_root_arch", 114, 66, 8)
    P("twisted_root_arch", 132, 62, 7)
    P("ash_root_curtain", 122, 60, 6)
    P("den_glow_mushrooms", 126, 72, 3)
    # ---- the Elders' Rest
    P("fw_timbermaw_lodge", 122, 30, 11, solid="core", where="assets/buildings/")
    P("fw_timbermaw_totem", 110, 34, 7, solid="core")
    P("fw_timbermaw_totem", 134, 34, 7, solid="core")
    P("ash_glow_mushroom_ring", 128, 39, 3)
    P("ash_furbolg_lodge", 111, 28, 7, solid="core")
    # ---- the Winterspring passage: the roof came down here too, and the cold still comes through it
    for (x, y, h, name) in [(142, 9, 5, "asp_boulder"), (146, 7, 6, "asp_boulder_split"),
                            (150, 9, 5, "asp_boulder_lichen")]:
        P(name, x, y, h, solid=True, near_ok=True)
    P("ashx_ice_stalagmites", 138, 18, 4)
    return zone, L


def finish(zone, L):
    return L.finish([PORTAL, EAST_PORTAL, MOON_PORTAL] + list(NPC_POSITIONS.values()))


def build_tunnel_baked():
    zone, L = build_tunnel()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_timbermaw_tunnel():
    zone, L = build_tunnel_baked()
    register_baked(zone, BAKED)
    return zone


if __name__ == "__main__":
    z, L = build_tunnel_baked()
    print("props", L.placed, "skipped", L.skipped)
