"""
Opened chests stay opened across a save, and come back by chance.

Kyle, 10 Nov: "chests respawn - very low chance overworld, much higher in dungeons."

Found on the way: opened chests were never saved. The world is rebuilt on startup with every
chest in place, so loading a game put all of them back - a 100% respawn rate by accident.

  1. open a chest, save, load: it is still gone
  2. loading a DIFFERENT save puts back the chests the first one had opened
  3. re-entering the zone straight after opening never brings it back (the wait)
  4. once the wait has passed, entering the zone rolls: about 40% in a dungeon, about 5% in
     the open world (2,000 entries each)
  5. a chest that came back can be opened again, and holds loot the usual way
  6. a failed roll starts the wait again - you cannot re-roll by stepping in and out
  7. the real zone transition makes the roll
"""
import json
import os
import random
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from entities.character import Character
    from world.chest_manager import ChestManager

    random.seed(9)
    sm = GameStateManager(screen)
    sm.player = Character(name="Hero", char_class="Warrior", level=30)
    zm = sm._live_zone_manager()
    cm = zm.chest_manager
    cm.load_dict({})

    def tmap(name):
        e = zm.zones[name]
        return e["tilemap"] if isinstance(e, dict) else e

    from world.secrets import get_secrets
    secrets = get_secrets()

    def chests_in(name):
        # a secret's cache is one-time by design (world/secrets.py), so it is not a respawn test case
        t = tmap(name)
        return [(x, y) for y in range(t.height) for x in range(t.width)
                if t.interaction_layer[y][x] == "chest" and not secrets.is_cache(name, x, y)]

    dungeon = next((n for n in zm.zones if n in zm.cave_names and chests_in(n)), None)
    field = next((n for n in zm.zones if n not in zm.cave_names and chests_in(n)), None)
    if not check(dungeon and field, f"rig: need a dungeon and an overworld zone with chests (got {dungeon}, {field})"):
        print("FAIL", fails)
        return 1
    dt, ft = tmap(dungeon), tmap(field)
    dx, dy = chests_in(dungeon)[0]
    fx, fy = chests_in(field)[0]

    # 1 ------------------------------------------------------------------------------------
    cm.open_chest(dt, dx, dy, 30)
    check(dt.interaction_layer[dy][dx] is None and not cm.get_chest_at_location(dt, dx, dy), "an opened chest is still on the map")
    saves = Path(tempfile.mkdtemp())
    sm._save_system().save_dir = saves
    sm.current_save_file = "a.json"
    check(sm.save_game("a.json"), "rig: save failed")
    saved = json.loads((saves / "a.json").read_text(encoding="utf-8"))
    check([dungeon, dx, dy] in (saved.get("world", {}).get("chests", {}).get("looted") or []),
          "the opened chest is not in the save file")
    dt.set_tile(dx, dy, "chest", "interaction")           # what a fresh world build would hold
    cm._looted.clear()
    check(sm.load_game("a.json"), "rig: load failed")
    check(tmap(dungeon).interaction_layer[dy][dx] is None, "after save and load the opened chest is back")

    # 2 ------------------------------------------------------------------------------------
    blank = dict(saved)
    blank["world"] = dict(saved["world"], chests={"looted": [], "wait": []})
    (saves / "b.json").write_text(json.dumps(blank), encoding="utf-8")
    check(sm.load_game("b.json"), "rig: load of the second save failed")
    check(tmap(dungeon).interaction_layer[dy][dx] == "chest",
          "loading a save that never opened the chest leaves it missing")

    # 3, 4, 6 ------------------------------------------------------------------------------
    clock = [1000.0]
    cm._now = lambda: clock[0]

    def trial(t, x, y, is_dungeon, n):
        back = 0
        for _ in range(n):
            cm.load_dict({})
            t.set_tile(x, y, "chest", "interaction")
            cm.open_chest(t, x, y, 30)
            if cm.on_enter_zone(t, is_dungeon):
                check(False, "a chest came back the moment it was opened")
            clock[0] += cm.RESPAWN_RETRY_SECONDS + 1
            if cm.on_enter_zone(t, is_dungeon):
                back += 1
                check(t.interaction_layer[y][x] == "chest", "a respawned chest is not on the map")
            else:
                check(cm.on_enter_zone(t, is_dungeon) == 0 and t.interaction_layer[y][x] is None,
                      "a failed roll was rolled again straight away")
        return back / n

    rate_d = trial(dt, dx, dy, True, 2000)
    rate_f = trial(ft, fx, fy, False, 2000)
    check(0.36 <= rate_d <= 0.44, f"dungeon respawn rate {rate_d:.1%}, want about 40%")
    check(0.035 <= rate_f <= 0.065, f"overworld respawn rate {rate_f:.1%}, want about 5%")

    # 5 ------------------------------------------------------------------------------------
    cm.load_dict({})
    dt.set_tile(dx, dy, "chest", "interaction")
    got = 0
    for _ in range(300):
        cm.open_chest(dt, dx, dy, 30)
        clock[0] += cm.RESPAWN_RETRY_SECONDS + 1
        cm.RESPAWN_CHANCE_DUNGEON, keep = 1.0, cm.RESPAWN_CHANCE_DUNGEON
        cm.on_enter_zone(dt, True)
        cm.RESPAWN_CHANCE_DUNGEON = keep
        if cm.get_chest_at_location(dt, dx, dy):
            got += 1
    check(got == 300, f"a respawned chest could be opened again only {got} of 300 times")

    # 7 ------------------------------------------------------------------------------------
    cm.load_dict({})
    ft.set_tile(fx, fy, "chest", "interaction")
    cm.open_chest(ft, fx, fy, 30)
    clock[0] += cm.RESPAWN_RETRY_SECONDS + 1
    ChestManager.RESPAWN_CHANCE_OVERWORLD, keep = 1.0, ChestManager.RESPAWN_CHANCE_OVERWORLD
    other = next(n for n in zm.zones if n != field)
    zm.transition_to_zone(other, via_portal=False)
    zm.transition_to_zone(field, via_portal=False)
    ChestManager.RESPAWN_CHANCE_OVERWORLD = keep
    check(tmap(field).interaction_layer[fy][fx] == "chest", "walking back into the zone did not make the respawn roll")

    del cm._now
    cm.load_dict({})
    print(f"respawn per entry: dungeon {rate_d:.1%}, overworld {rate_f:.1%}  ({dungeon} / {field})")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in list(dict.fromkeys(fails))[:20]:
            print("  ", f)
        return 1
    print("chest respawn OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
