#!/usr/bin/env python3
"""The game starts on a machine whose default text encoding is not UTF-8 (Windows).

    PYTHONPATH=. python3 tools/qa_text_encoding.py

Kyle, 13 Nov 2026: the game would not start on his Windows machine. A data file with accented
names in it was read without naming an encoding, Windows read it as cp1252, and it hit a byte
cp1252 has no character for. Every check ran on Linux, where the default is UTF-8, so none of
them could see it. TWO CLAIMS:

  1. No Python file in the repo reads or writes a text file without naming its encoding
     (tools/fix_text_encoding.py --check).
  2. The game BOOTS, builds every zone, draws a frame, and loads the data the menus read, in a
     child process whose default encoding is ASCII - stricter than Windows, so anything that
     would break there breaks here first.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BOOT = r'''
import locale, os, sys
sys.path.insert(0, ".")
enc = locale.getpreferredencoding(False)
import codecs
assert codecs.lookup(enc).name == "ascii", "default encoding is " + enc
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
pygame.init()
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
from core.game_state import GameStateManager, GameState
sm = GameStateManager(surface)
from entities.character import Character
from entities.party import Party
sm.player = Character("Tester", "Warrior", 40)
sm.party = Party(sm.player)
ow = sm.states[GameState.OVERWORLD]
ow.update(0.016)
ow.render(surface)
from world.fast_travel import destinations
assert len(destinations(ow.zone_manager)) > 20
from world import set_tokens, gear_sets
assert set_tokens.data()["tokens"] and gear_sets.all_sets()
from world.recruit_manager import get_recruit_manager
names = [r.name for r in get_recruit_manager().recruits.values()] if hasattr(get_recruit_manager(), "recruits") else []
from world.quest_manager import get_quest_manager
get_quest_manager()
from world.banter_manager import get_banter_manager
get_banter_manager()
print("BOOT OK", len(ow.zone_manager.zones), "zones", len(names), "recruits")
'''


def main():
    bad = []
    r = subprocess.run([sys.executable, str(ROOT / "tools/fix_text_encoding.py"), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        bad.append("text files opened without an encoding:\n" + r.stdout[-1500:])

    env = dict(os.environ, LC_ALL="C", LANG="C", PYTHONCOERCECLOCALE="0", PYTHONUTF8="0",
               SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", PYTHONPATH=str(ROOT))
    env.pop("PYTHONIOENCODING", None)
    r = subprocess.run([sys.executable, "-X", "utf8=0", "-c", BOOT], capture_output=True, cwd=ROOT, env=env)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    if r.returncode != 0 or "BOOT OK" not in out:
        tail = "\n".join(l for l in err.splitlines() if "ALSA" not in l)[-2500:]
        bad.append("the game does not boot under an ASCII default encoding:\n" + tail)
    else:
        print(out.strip().splitlines()[-1])

    for b in bad:
        print("  FAIL", b)
    print("\ntext encoding OK - nothing depends on the machine's default encoding."
          if not bad else f"\n{len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
