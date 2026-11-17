#!/usr/bin/env python3
"""A dungeon pack you flee from or die to is still there, and still has to be killed.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_dungeon_wipe_keeps_enemies.py

Kyle, 16 Nov 2026: "when you die in a dungeon and reset, the boss should not vanish.....same with trash. if you die you
STILL need to kill it....right now fleeing or dying causes the enemy to vanish". A pack was spent the moment it was
pulled. In the Scarlet Monastery's Graveyard, through the combat screen's own end-of-fight path:
  1. flee a pack: it's still there, but doesn't jump you again until you've stepped out of its reach;
  2. kill one of three and wipe: the other two are still there, the one you killed isn't;
  3. win: the pack is gone.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame  # noqa: E402


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from entities.character import Character
    from ui.screens.combat_screen import CombatScreen
    sm = GameStateManager(pygame.display.get_surface())
    sm.player = Character(name="Hero", char_class="Warrior", level=40)
    sm.save_game = lambda *a, **k: None
    zm = sm._live_zone_manager()
    zm.transition_to_zone("Scarlet Monastery: Graveyard")
    bad = []
    packs = [s for s in zm.cave_spawns.spawns if not s.defeated]
    if not packs:
        print("FAIL - no packs in the Graveyard")
        return 1

    def pull(sp):
        zm.player_x, zm.player_y = sp.members[0][0], sp.members[0][1]
        return zm.check_fixed_spawn_group()

    def end(monsters, victory, fled, killed=0):
        scr = CombatScreen(sm)
        sm.current_enemy, sm.current_enemies = monsters[0], monsters
        scr._init_combat()
        eng = scr.combat_engine
        for m in eng.enemies[:killed]:
            m.current_health = 0
        eng.is_active, eng.victory, eng.fled = False, victory, fled
        sm.resolve_wipe = lambda: []
        scr.handle_event(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE, "mod": 0, "unicode": " ",
                                                             "scancode": 0}))

    # 1. flee
    sp = packs[0]
    names = [m[2] for m in sp.members]
    mons = pull(sp)
    end(mons, victory=False, fled=True)
    if sp.defeated or [m[2] for m in sp.members] != names:
        bad.append(f"fleeing {names}: the pack {'vanished' if sp.defeated else 'changed'}")
    if zm.check_fixed_spawn_group():
        bad.append("a pack you just fled jumps you again before you've stepped away")
    zm.player_x, zm.player_y = sp.members[0][0] + 30, sp.members[0][1] + 30
    zm.cave_spawns.spawn_at(zm.player_x, zm.player_y)
    if not pull(sp):
        bad.append("a pack you fled can't be pulled again once you come back")
    # 2. wipe after one kill
    big = next((s for s in packs if len(s.members) >= 2), None)
    if big is not None:
        names = [m[2] for m in big.members]
        mons = pull(big)
        end(mons, victory=False, fled=False, killed=1)
        left = sorted(m[2] for m in big.members)
        if big.defeated or len(left) != len(names) - 1:
            bad.append(f"wiping to {names} after one kill left {left} (defeated={big.defeated})")
    # 3. win
    win = packs[-1]
    zm.player_x, zm.player_y = win.members[0][0] + 30, win.members[0][1] + 30
    zm.cave_spawns.spawn_at(zm.player_x, zm.player_y)
    mons = pull(win)
    if mons:
        end(mons, victory=True, fled=False, killed=len(mons))
        if not win.defeated:
            bad.append("a pack you beat came back")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - fled and wiped-to packs stay (minus what you killed); beaten packs are gone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
