"""
Hand-built The Drownbell (96x80): the pirate cove under Tanaris's southeast range. 43-45.

Kyle: "south east we can have a 'cave' which is the pirate cove (so not an actual dungeon - so no
fixed spawns)" and "The cove will be a small entrance in the south east, it doesn't need to take up
that much space. It'll be a seperate 'cave'."

A CAVE, NOT A DUNGEON, and that is a mechanical contract rather than a label (claude/dungeon_authoring_rules):

  * fixed_spawns = False. Trash comes from the per-step encounter roll; there is no pack list here
    and there should not be one. Kyle, 2026-10-22: "Hand placed mobs are only in full dungeons!"
  * THE BOSS AND THE RARE SIT IN THE SAME TABLE AT WEIGHT 0, placed only via zone.boss_positions.
    A separate "bosses" key is silently ignored by the spawn code, which is the kind of thing that
    looks like it works.
  * Four abilities for a 20+ boss, the first a zero-cooldown damage.

THE SHAPE IS A DROWNED SEA CAVE: a mouth above the waterline, a gallery that steps DOWN, and a
flooded floor at the bottom where the ships are. You walk in at the top and the water comes up to
meet you, which is the one thing a cave under a coast can do that a cave under a desert cannot.

WHY ANYONE IS HERE. The bell is real: a diving bell, goblin-built, sitting on the bottom of the
flooded chamber with its chain still on the winch. Somebody was salvaging something out of this cove
before the pirates took it, and the pirates have not touched the bell because the first two of them
who went down to look at it did not come back up. That is the cove's one piece of furniture and the
reason the deepest chamber has a name.
"""
from world.tilemap import Tilemap
from tools.handbuilt_vot_caves import CaveLayout, register_baked  # noqa: F401

BAKED = "assets/tiles/drownbell/baked"
SFP = "assets/tiles/shimmering_flats/props/"
SNP = "assets/tiles/southern_needles/props/"
STV = "assets/tiles/stranglethorn/props/"

W, H = 96, 80
BAKED_DIR = BAKED
PORTAL = (16, 12)

#: (name, cx, cy, rx, ry). The cave steps down from the mouth in the north-west to the flooded
#: bottom in the south-east - three levels, and the water is only on the last one.
CHAMBERS = [
    ("The Mouth",        16, 14, 9, 7),
    ("The Dry Gallery",  34, 22, 12, 9),
    ("The Stair",        48, 36, 9, 8),
    ("The Wet Gallery",  62, 44, 13, 10),
    ("The Careenage",    44, 58, 12, 9),     # where they haul a hull over to work on it
    ("The Bell",         76, 64, 13, 11),    # the flooded bottom
]

#: (from, to, width). The ring matters: there are two ways down to the bottom, so a fight at the
#: stair is not a wall.
TUNNELS = [
    (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 5, 4),
    (1, 4, 3),            # the back way, down the west side
    (4, 5, 3),            # and along the bottom, which closes the ring
]

#: Pinned, because they are a boss and a rare and this is a cave.
BOSSES = {"Captain Vaile Drownbell": (76, 64), "The Bellwarden": (44, 58)}

#: Named here so build_drownbell_content.py can check itself against the zone rather than retype it.
TRASH = ["Drownbell Cutthroat", "Drownbell Bosun", "Cove Tidecaller", "Bilge Crawler"]


def build_drownbell():
    zone = Tilemap("The Drownbell", W, H,
                   "A sea cave the pirates took off whoever was salvaging it. It steps down, and at "
                   "the bottom there is water, and in the water there is a bell.")
    zone.is_cave = True
    zone.region = "Northern Tanaris"
    zone.fixed_spawns = False
    zone.boss_positions = [(x, y, n) for n, (x, y) in BOSSES.items()]

    L = CaveLayout(zone, (PORTAL[0], PORTAL[1] + 2))
    b = L.b
    # lobes() takes a list of ellipses and unions them - two overlapping lobes per chamber so the
    # rooms are organic rather than six identical ovals on a line.
    for (_n, cx, cy, rx, ry) in CHAMBERS:
        b.lobes([(cx, cy, rx, ry),
                 (cx + rx // 3, cy - ry // 3, int(rx * 0.7), int(ry * 0.7)),
                 (cx - rx // 3, cy + ry // 4, int(rx * 0.6), int(ry * 0.8))])
    for (a, c, wdt) in TUNNELS:
        _n1, ax, ay, _rx, _ry = CHAMBERS[a]
        _n2, bx, by, _rx2, _ry2 = CHAMBERS[c]
        b.corridor([(ax, ay), (bx, by)], width=wdt)

    px, py = PORTAL
    zone.collision_layer[py][px] = None
    zone.set_tile(px, py, "portal", "interaction")
    L.mark("portal", px, py)
    for n, (x, y) in BOSSES.items():
        L.mark("boss", x, y)

    for (name, cx, cy, rx, ry) in CHAMBERS:
        zone.add_subzone(name, max(0, cx - rx), max(0, cy - ry), rx * 2, ry * 2)
    return zone, L


def dress(zone, L):
    P = L.prop
    F = dict(where=SFP)
    N = dict(where=SNP)
    # the dry end: what they carried in
    P("sf_crate_stack", 32, 20, 4, **F)
    P("sf_fuel_drums", 38, 24, 4, **F)
    P("sf_scrap_heap", 30, 26, 4, **F)
    P("sf_signboard", 20, 16, 4, **F)
    # the careenage: a hull on its side and the gear to hold it there
    P("sf_hand_winch", 42, 56, 4, **F)
    P("sf_wheel_stack", 48, 60, 4, **F)
    P("sf_crate_stack", 40, 62, 4, **F)
    # the wet end, and the bell
    P("sf_condenser", 74, 62, 6, **F)       # the bell itself: goblin-built, chain still on the winch
    P("sf_hand_winch", 80, 60, 4, **F)
    P("sn_rib_bones", 70, 68, 3, near_ok=True, **N)
    P("sn_rib_bones", 82, 68, 3, near_ok=True, **N)
    P("sn_driftwood_salt", 64, 48, 3, near_ok=True, **N)
    P("sn_driftwood_salt", 58, 52, 3, near_ok=True, **N)
    return zone, L


def verify(zone):
    """A cave, not a dungeon - and the ring has to be a real bypass."""
    assert zone.is_cave is True
    assert zone.fixed_spawns is False, "a cave rolls its trash; hand-placed mobs are dungeons only"
    assert zone.boss_positions, "the boss and the rare are pinned, not rolled"
    # the ring: sealing the Stair must NOT cut the bottom off from the mouth
    import collections
    blocked = set()
    _n, sx, sy, srx, sry = CHAMBERS[2]
    for y in range(sy - sry - 2, sy + sry + 3):
        for x in range(sx - srx - 2, sx + srx + 3):
            blocked.add((x, y))
    start = (PORTAL[0], PORTAL[1] + 2)
    seen = {start}
    q = collections.deque([start])
    while q:
        x, y = q.popleft()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + d[0], y + d[1])
            if (0 <= n[0] < W and 0 <= n[1] < H and n not in seen and n not in blocked
                    and zone.is_walkable(*n)):
                seen.add(n)
                q.append(n)
    bottom = BOSSES["Captain Vaile Drownbell"]
    assert bottom in seen, ("sealing the Stair cuts the Bell off - the west way down is not a real "
                            "bypass, it is decoration")
    return dict(chambers=len(CHAMBERS), bypass=True)


def finish(zone, L):
    return L.finish([PORTAL] + list(BOSSES.values()))


def build_drownbell_baked():
    zone, L = build_drownbell()
    dress(zone, L)
    finish(zone, L)
    return zone, L


def generate_drownbell():
    zone, L = build_drownbell_baked()
    return zone
