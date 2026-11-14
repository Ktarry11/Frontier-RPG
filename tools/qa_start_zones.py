#!/usr/bin/env python3
"""Every start zone is somewhere a level 1 character can actually begin.

    PYTHONPATH=. python3 tools/qa_start_zones.py

A START ZONE FAILS QUIETLY OR NOT AT ALL. It never crashes - a bad coordinate puts a new character in a
field, a zone with no level-1 quests puts them somewhere with nothing to do, and a hearth bound to the
wrong continent only shows up the first time somebody uses it an hour in. None of that raises. So this
checks the things that would otherwise be discovered by a player:

  * the zone name resolves against the real generated world, not just the registry
  * the spawn tile is WALKABLE on the generated map
  * there is a level-1 quest giver within sight of it, and the giver is a real NPC standing nearby
  * the hearth binds to the start the character actually chose
  * the creation screen's buttons fit on screen, which is the one thing here that is a layout problem
    and not a data problem - the appearance row is full at five races and two starts
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import json  # noqa: E402

from world.start_zones import get_available_starts, get_start, suggested_start_for_race  # noqa: E402
from world.race_registry import get_available_races  # noqa: E402

#: How far from the spawn a level-1 quest giver may stand before a new character is just lost.
NEAR = 14


def main():
    from world.zone_generator import create_all_zones
    Z = create_all_zones()
    npcs = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]
    quests = []
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        qs = json.loads(f.read_text(encoding="utf-8")).get("quests", [])
        quests += qs if isinstance(qs, list) else list(qs.values())

    fails = []
    print("== starts")
    for sz in get_available_starts():
        z = Z.get(sz.zone_name)
        if z is None:
            fails.append(f"{sz.start_id}: zone '{sz.zone_name}' does not exist in the generated world")
            continue
        ok = z.is_walkable(sz.x, sz.y)
        zkey = sz.zone_name.lower().replace(" ", "_").replace("'", "")
        here = [n for n in npcs if n.get("zone") == zkey]
        l1 = {q["giver_npc_id"] for q in quests
              if q.get("zone") == zkey and q.get("level_min", 99) <= 1}
        near = [n for n in here if n["npc_id"] in l1
                and abs(n["x"] - sz.x) + abs(n["y"] - sz.y) <= NEAR]
        print(f"  {sz.label:<18} {sz.zone_name:<18} ({sz.x},{sz.y}) walkable={ok}  "
              f"level-1 givers within {NEAR}: {[n['npc_id'] for n in near] or 'NONE'}")
        if not ok:
            fails.append(f"{sz.start_id}: spawn ({sz.x},{sz.y}) is not walkable")
        if not l1:
            fails.append(f"{sz.start_id}: {sz.zone_name} has no level-1 quests at all")
        elif not near:
            fails.append(f"{sz.start_id}: no level-1 quest giver within {NEAR} tiles of the spawn - a "
                         f"new character starts with nothing to do")

    print("\n== every race suggests a real start, and none is locked out")
    for r in get_available_races():
        sid = suggested_start_for_race(r.race_id)
        got = get_start(sid)
        print(f"  {r.label:<12} -> {got.label}")
        if got.start_id != sid:
            fails.append(f"{r.race_id} suggests '{sid}', which is not a real start")

    print("\n== the hearth binds where the character started")
    from world.travel_manager import reset_travel_manager
    for sz in get_available_starts():
        t = reset_travel_manager(sz.start_id)
        print(f"  {sz.label:<18} -> {t.bind['zone']} ({t.bind['x']},{t.bind['y']})")
        if t.bind["zone"] != sz.zone_name:
            fails.append(f"{sz.start_id}: hearth binds to {t.bind['zone']}, not {sz.zone_name}")

    print("\n== reset_to_start actually lands there")
    from world.zone_manager import ZoneManager
    zm = ZoneManager()
    for sz in get_available_starts():
        zm.reset_to_start(sz.start_id)
        landed = (zm.current_zone.name, zm.player_x, zm.player_y)
        print(f"  {sz.label:<18} -> {landed}  nodes={len(zm.gathering_manager.active_nodes)}")
        if landed != (sz.zone_name, sz.x, sz.y):
            fails.append(f"{sz.start_id}: reset_to_start landed at {landed}")
    zm.reset_to_start("a_start_that_does_not_exist")
    if zm.current_zone.name != get_start(None).zone_name:
        fails.append("an unknown start id must fall back to the default, not strand the character")

    print("\n== the creation screen still fits on screen")
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from ui.screens.character_screen import CharacterCreationScreen
    sc = CharacterCreationScreen(type("S", (), {})())
    right = max([b.right for b in sc.start_buttons] + [b.right for b in sc.race_buttons])
    print(f"  {len(sc.available_races)} races + {len(sc.available_starts)} starts, "
          f"rightmost control ends at {right} of 1280")
    if right > 1268:
        fails.append(f"appearance row overflows: {right} > 1268")

    print()
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails:
            print("  -", f)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
