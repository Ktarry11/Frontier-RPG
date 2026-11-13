#!/usr/bin/env python3
"""Subzone names on the map never print over each other (backlog D [13], O [86]).

    PYTHONPATH=. python3 tools/qa_map_labels_clear.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from ui.screens.map_screen import clear_label_rect
    bad = []
    placed = []
    bounds = pygame.Rect(0, 0, 800, 600)
    # ten names all asked for the same spot
    for _ in range(10):
        r = clear_label_rect(pygame.Rect(300, 300, 120, 14), placed, bounds)
        if any(r.colliderect(o) for o in placed):
            bad.append(f"label at {r} overlaps one already placed")
        placed.append(r)
    if len({(r.x, r.y) for r in placed}) != 10:
        bad.append("labels were not moved apart")
    if not all(bounds.contains(r) for r in placed):
        bad.append("a label was pushed off the map")
    # a label with free space is left exactly where it was asked for
    if clear_label_rect(pygame.Rect(10, 10, 50, 14), placed, bounds) != pygame.Rect(10, 10, 50, 14):
        bad.append("a label with nothing near it was moved")
    # the map screen still draws the worst maps
    import inspect
    from ui.screens import map_screen
    src = inspect.getsource(map_screen)
    if src.count("clear_label_rect(lrect, placed, rect)") < 2:
        bad.append("the map screen does not route both label placements through clear_label_rect")
    if "hash(name)" in src.replace("not hash()", ""):
        bad.append("label rows still use hash(), which changes every run")
    if bad:
        for b in bad:
            print("  -", b)
        return 1
    print("map labels OK - overlapping subzones no longer print their names on top of each other.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
