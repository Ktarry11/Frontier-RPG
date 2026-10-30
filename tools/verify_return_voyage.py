#!/usr/bin/env python3
"""Everything about the Return Voyage that can be checked by measuring it.

    PYTHONPATH=. python3 tools/verify_return_voyage.py

Run this after any layout change to the crossing or the two Bloodsail ships. Seven zones, and
every one of the checks below exists because the thing it checks went wrong once.

  THE ARRIVAL TILE. PortalManager._offset_spawn silently puts an arriving player TWO TILES NORTH
  of the destination portal, and nothing anywhere writes that tile down - so a portal can be
  perfectly placed on a deck and still drop the player in the sea. Every portal is checked three
  ways: the source tile, the destination tile, and the tile the player will actually stand on.

  SKIPPABILITY IS REPORTED, NOT ENFORCED. Kyle first wanted no boss skippable; on seeing what that
  took he changed his mind - "in all honesty, if people want to skip bosses they can. just need to
  make sure that we have trash mobs too... we have optional bosses in dungeons already" - and he
  is right, because a boss you cannot decline is a toll rather than an encounter. So this prints
  which bosses are on the only route and which can be run past, and fails on neither. What it DOES
  fail on is a zone with no trash in it, which is the part he actually asked for.

  BULKHEADS AND NECKS ARE REAL CUTS. Connectivity passing proves a dungeon is walkable and proves
  nothing about whether it has any structure: a bulkhead whose doorway is as wide as the hull at
  that station is a wall with a hole in it, and every flood fill passes it happily. So each one is
  sealed in turn and the far side must become unreachable.

  NO ISOLATED POCKETS. Shrinking the sand bar once detached its mooring lobe and stranded 73 tiles;
  making the anchorage's pools block stranded its whole east shore. Neither was visible in a render.

  NOTHING STANDS ON A SHIP. Kyle: "i literally see some blue thing ON the galleon ship." Props are
  compared by sprite box, because by eye every prop at that end of the map looks like deck gear.

  THE ASYMMETRY, both directions. Ratchet -> Booty Bay must stay a direct boat and Booty Bay ->
  Ratchet must land on The Crossing. This is the entire point of the content and it is one line in
  a dict that a tidy-up would happily "fix".
"""
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TRIGGER_RADIUS = 1
#: Kyle: "roughly 3-4 trash packs before each boss, for smaller dungeons this can be reduced to
#: like 2 or so. it's not set in stone."
MIN_PULLS, MAX_PULLS = 2, 4


def flood(zone, start, blocked=frozenset()):
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and n not in blocked and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def _dist(zone, src):
    """Path distance from src over walkable tiles - how dungeon_packs assigns a pack to a boss."""
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


def main():
    import tools.handbuilt_return_voyage as RV
    import tools.handbuilt_bloodsail_raider as R
    import tools.handbuilt_bloodsail_galleon as G
    from world.portal_manager import PortalManager

    problems = []

    # Each zone: (builder, dresser, finisher, entrance, exit). The entrance is where a player
    # actually arrives, which is the portal's offset tile, not the portal.
    specs = [
        ("The Crossing", RV.build_the_crossing, RV.dress, RV.finish, None, None),
        ("The Bloodsail Raider", R.build_raider_deck, R.dress_raider_deck,
         R.finish_raider_deck, R.D_IN, R.D_HATCH),
        ("The Raider's Hold", R.build_raider_hold, R.dress_raider_hold,
         R.finish_raider_hold, R.H_IN, R.H_OUT),
        ("The Bloodsail Anchorage", G.build_anchorage, G.dress_anchorage,
         G.finish_anchorage, G.A_IN, G.A_OUT),
        ("The Galleon's Weather Deck", G.build_galleon_deck, G.dress_galleon_deck,
         G.finish_galleon_deck, G.D_IN, G.D_HATCH),
        ("The Galleon's Hold", G.build_galleon_hold, G.dress_galleon_hold,
         G.finish_galleon_hold, G.H_IN, G.H_OUT),
        ("The Captain's Cabin", G.build_cabin, G.dress_cabin,
         G.finish_cabin, G.C_IN, G.C_OUT),
    ]

    zones = {}
    print("ZONES")
    for name, bld, dress, finish, entry, exit_ in specs:
        res = bld()
        zone, L = res[0], res[1]
        dress(zone, L)
        try:
            reach = finish(zone, L)
        except AssertionError as e:
            problems.append(f"{name}: {e}")
            continue
        zones[name] = (zone, L, entry, exit_)
        total = sum(zone.is_walkable(x, y)
                    for y in range(zone.height) for x in range(zone.width))
        if total != reach:
            problems.append(f"{name}: {total - reach} walkable tiles isolated")
        if L.skipped:
            problems.append(f"{name}: {len(L.skipped)} props skipped - {L.skipped}")
        print(f"  {name:30} {zone.width:3}x{zone.height:<3} {reach:5} walkable, "
              f"{L.placed:2} props")

    # ---- portals, including the tile the player actually lands on
    print("\nPORTALS (source tile / destination tile / ARRIVAL tile)")
    pm = PortalManager()
    ours = {n for n in zones}
    checked = 0
    for (zname, sx, sy), (dzone, ax, ay) in pm._lookup.items():
        if zname not in ours and dzone not in ours:
            continue
        checked += 1
        if zname in zones:
            z = zones[zname][0]
            if not z.is_walkable(sx, sy):
                problems.append(f"{zname}: portal source ({sx},{sy}) is not walkable")
            if z.interaction_layer[sy][sx] != "portal":
                problems.append(f"{zname}: ({sx},{sy}) is a portal in portal_manager but carries "
                                f"no portal tile in the zone - it will look like plain deck")
        if dzone in zones:
            dz = zones[dzone][0]
            # (ax, ay) is already the OFFSET arrival from _offset_spawn.
            if not dz.is_walkable(ax, ay):
                problems.append(f"{zname} ({sx},{sy}) -> {dzone}: the player lands on ({ax},{ay}), "
                                f"which is not walkable - _offset_spawn moved them two north of "
                                f"the portal and that is open water")
    print(f"  {checked} portal links touch these zones, all source and arrival tiles checked")

    # ---- every zone's portal tiles must exist in portal_manager
    for name, (zone, _L, _e, _x) in zones.items():
        declared = {(x, y) for y in range(zone.height) for x in range(zone.width)
                    if zone.interaction_layer[y][x] == "portal"}
        wired = set(pm.get_portal_positions(name))
        orphan = declared - wired
        if orphan:
            problems.append(f"{name}: portal tiles with no destination: {sorted(orphan)} - "
                            f"the player will walk onto them and nothing will happen")

    # ---- bosses, and whether anyone can walk past one
    print("\nBOSSES (can the exit be reached without triggering them?)")
    for name, (zone, _L, entry, exit_) in zones.items():
        if entry is None:
            continue
        bosses = list(getattr(zone, "boss_positions", None) or [])
        pack = [(m[0], m[1]) for v in (getattr(zone, "boss_pack", None) or {}).values()
                for m in v]
        for (bx, by, bname) in bosses:
            # A pack is ONE encounter - walking near any member starts it - so the whole pack's
            # trigger band counts, not just the lead's tile.
            tiles = [(bx, by)] + pack
            band = {(x + dx, y + dy) for (x, y) in tiles
                    for dx in range(-TRIGGER_RADIUS, TRIGGER_RADIUS + 1)
                    for dy in range(-TRIGGER_RADIUS, TRIGGER_RADIUS + 1)}
            held = exit_ not in flood(zone, entry, frozenset(band))
            print(f"  {name[:26]:26} {bname:28} "
                  f"{'on the only route' if held else 'optional - can be run past'}")

    # ---- TRASH. The thing Kyle does require: "just need to make sure that we have trash mobs
    # too". A zone whose pulls failed to place, or that has them as a flat list instead of packs,
    # is a zone of solo fights - CaveSpawnManager.populate takes the trash_packs branch only if
    # that attribute is set, and a flat trash_spawns makes every mob its own encounter.
    print("\nTRASH")
    for name, (zone, _L, _e, _x) in zones.items():
        if name == "The Crossing":
            continue
        packs = list(getattr(zone, "trash_packs", None) or [])
        flat = list(getattr(zone, "trash_spawns", None) or [])
        if name == "The Captain's Cabin":
            if packs or flat:
                problems.append(f"{name}: has trash, and the double boss is meant to be alone")
            print(f"  {name:30} no trash, by design")
            continue
        if not packs:
            problems.append(f"{name}: no trash packs - the zone is bosses and empty deck")
        elif any(len(p) < 2 for p in packs):
            problems.append(f"{name}: a pack has fewer than 2 mobs, so it is a solo fight")
        if len(flat) != sum(len(p) for p in packs):
            problems.append(f"{name}: trash_spawns and trash_packs disagree "
                            f"({len(flat)} vs {sum(len(p) for p in packs)})")
        # PULLS PER BOSS, which is the number Kyle actually specifies: "For a dungeon we want
        # roughly 3-4 trash packs before each boss, for smaller dungeons this can be reduced to
        # like 2 or so. it's not set in stone." So the bound is 2-4 and a miss is reported rather
        # than fatal. A pack belongs to the boss it leads to by PATH DISTANCE, the same rule
        # world/dungeon_packs uses - which on a hull, one long line, is why packs have to be
        # placed either side of the midpoint between two bosses rather than "on the way to" one.
        bosses = {bn: (bx, by) for (bx, by, bn) in (getattr(zone, "boss_positions", None) or [])}
        if bosses:
            dmaps = {bn: _dist(zone, pos) for bn, pos in bosses.items()}
            per = {bn: 0 for bn in bosses}
            for pack in packs:
                lx, ly = pack[0][0], pack[0][1]
                per[min(bosses, key=lambda bn: dmaps[bn].get((lx, ly), 10 ** 6))] += 1
            for bn, c in per.items():
                if not (MIN_PULLS <= c <= MAX_PULLS):
                    problems.append(f"{name}: {bn} has {c} pull(s) leading to it, outside the "
                                    f"{MIN_PULLS}-{MAX_PULLS} Kyle asked for")
            detail = ", ".join(f"{bn.split()[-1]} {c}" for bn, c in per.items())
        else:
            detail = ""
        print(f"  {name:30} {len(packs)} pulls, {len(flat)} mobs, "
              f"sizes {sorted({len(p) for p in packs})}   {detail}")

    # ---- bulkheads and necks are real cuts
    print("\nBULKHEADS AND NECKS (does sealing the doorway actually divide the space?)")
    cuts = [("The Raider's Hold", R.BULKHEADS, "x", R.H_IN, R.H_OUT),
            ("The Galleon's Hold", G.GBULKHEADS, "x", G.H_IN, G.H_OUT),
            ("The Bloodsail Raider", [(s, lo, hi) for (s, lo, hi) in R.DECK_BARRICADES],
             "x", R.D_IN, R.D_HATCH),
            ("The Galleon's Weather Deck", [(s, lo, hi) for (s, lo, hi) in G.GDECK_BARRICADES],
             "x", G.D_IN, G.D_HATCH)]
    for name, lines, axis, entry, exit_ in cuts:
        if name not in zones:
            continue
        zone = zones[name][0]
        real = 0
        for (line, lo, hi) in lines:
            door = {(line, v) for v in range(lo, hi + 1)}
            if exit_ not in flood(zone, entry, frozenset(door)):
                real += 1
            else:
                problems.append(f"{name}: sealing the doorway at {axis}={line} does not cut the "
                                f"space - it is a wall with a hole in it, not a compartment")
        print(f"  {name:30} {real}/{len(lines)} genuine cuts")
    # the anchorage's two tidal necks
    if "The Bloodsail Anchorage" in zones:
        zone = zones["The Bloodsail Anchorage"][0]
        real = 0
        for (y0, y1, lo, hi) in G.NECKS:
            door = {(x, y) for x in range(lo, hi + 1) for y in range(y0, y1 + 1)}
            if G.A_OUT not in flood(zone, G.A_IN, frozenset(door)):
                real += 1
            else:
                problems.append(f"The Bloodsail Anchorage: the neck at y{y0}-{y1} does not cut "
                                f"the beach")
        print(f"  {'The Bloodsail Anchorage':30} {real}/{len(G.NECKS)} genuine necks")

    # ---- nothing stands on a ship
    print("\nPROPS ON SHIPS")
    on_ship = 0
    for name, (zone, _L, _e, _x) in zones.items():
        marks = list(getattr(zone, "landmarks", []) or [])
        ships = [m for m in marks if "bloodsail_raider" in m["sprite_key"]
                 or "bloodsail_galleon" in m["sprite_key"]]

        def box(m):
            return (m["anchor_x"], m["anchor_y"],
                    m["anchor_x"] + m["width_tiles"], m["anchor_y"] + m["height_tiles"])
        for sh in ships:
            a, b, c, d = box(sh)
            for o in marks:
                if o is sh:
                    continue
                e, f, g, h = box(o)
                if e < c and g > a and f < d and h > b:
                    on_ship += 1
                    problems.append(f"{name}: {Path(o['sprite_key']).stem} is standing on "
                                    f"{Path(sh['sprite_key']).stem}")
    print(f"  {on_ship} props overlapping a ship sprite")

    # ---- the asymmetry
    print("\nTHE ASYMMETRY")
    south = pm.get_destination("Ratchet", 64, 30)
    north = pm.get_destination("Booty Bay", 64, 34)
    if not south or south[0] != "Booty Bay":
        problems.append(f"Ratchet -> Booty Bay is no longer the direct boat (got {south})")
    else:
        print(f"  Ratchet -> Booty Bay   direct, unchanged")
    if not north or north[0] != "The Crossing":
        problems.append(f"Booty Bay -> Ratchet no longer lands on The Crossing (got {north}) - "
                        f"the whole dungeon is unreachable")
    else:
        print(f"  Booty Bay -> Ratchet   lands on The Crossing at {north[1:]}")

    print("\n" + "=" * 78)
    if problems:
        print(f"{len(problems)} PROBLEM(S)")
        for p in problems:
            print(f"  * {p}")
        return 1
    print("all clear")
    return 0


if __name__ == "__main__":
    sys.exit(main())
