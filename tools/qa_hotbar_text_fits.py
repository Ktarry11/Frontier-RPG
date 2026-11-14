"""
Every line of text on a combat hotbar button fits inside the button.

Kyle, 10 Nov: "we need to fix wrap around text for skills as they STILL go off the side of the
box." - "Clasp of Infinity / Cost: 35 Ma", "Decompositi", "Cost: 167 Ma".

For every ability name in the game (class files, personal kits) and every consumable, with the
longest cost line each resource can produce and the widest hotkey label, lay the button out
with the real CombatScreen method and measure every line with the font it is drawn in:

  - no line wider than the button's inner width
  - nothing below the button's bottom edge
  - the cost line and the hotkey never overlap each other, nor the name
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def names():
    out = set()

    def walk(node):
        if isinstance(node, dict):
            if node.get("ability_id") and node.get("name"):
                out.add(node["name"])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    for path in list((ROOT / "data/abilities").glob("*.json")) + [ROOT / "data/npcs/personal_kits.json"]:
        walk(json.loads(path.read_text(encoding="utf-8")))
    for path in (ROOT / "data").rglob("*consumable*.json"):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        stack = [blob]
        while stack:
            n = stack.pop()
            if isinstance(n, dict):
                if n.get("name") and ("consumable_id" in n or "effect" in n or "restore" in str(n.keys())):
                    out.add(n["name"])
                stack.extend(n.values())
            elif isinstance(n, list):
                stack.extend(n)
    return sorted(out)


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from ui.renderer import Renderer
    from ui.screens.combat_screen import CombatScreen

    scr = CombatScreen.__new__(CombatScreen)
    scr.renderer = Renderer()
    size = CombatScreen.HOTBAR_BUTTON_SIZE
    rect = pygame.Rect(100, 100, size, size)
    inner = rect.width - 2 * CombatScreen.SLOT_TEXT_PAD
    fonts = {"normal": scr.renderer.font_normal, "small": scr.renderer.font_small}

    all_names = names()
    if len(all_names) < 800:
        print(f"FAIL only {len(all_names)} ability names found - the rig is not seeing them")
        return 1
    subs = [f"999 {label}" for label in CombatScreen.RESOURCE_DISPLAY_NAMES.values()]
    subs += ["12 turns", "Wrong form", "x200"]
    widest_sub = max(subs, key=lambda t: fonts["small"].size(t)[0])

    bad, shrunk, cut = [], 0, 0
    for name in all_names:
        for sub in (widest_sub, None):
            placed = scr._fit_slot_label(rect, name, sub, "Shift+0")
            boxes = []
            for text, (x, y), fsize in placed:
                # Width as rendered; height as the glyphs' own (ascent + descent) - size()
                # adds a pixel of line gap that is not ink and would report touching lines
                # as overlapping.
                w = fonts[fsize].size(text)[0]
                h = fonts[fsize].get_ascent() - fonts[fsize].get_descent()
                boxes.append(pygame.Rect(x, y, w, h))
                if w > inner or x < rect.x:
                    bad.append(f"{name!r}: line {text!r} is {w}px in a {inner}px button")
                if y + h > rect.bottom:
                    bad.append(f"{name!r}: line {text!r} hangs below the button")
            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    if boxes[i].colliderect(boxes[j]):
                        bad.append(f"{name!r}: {placed[i][0]!r} overlaps {placed[j][0]!r}")
            if sub is None:
                shown = " ".join(t for t, _, _ in placed[:-1])
                if any(f == "small" for _, _, f in placed[:-1]):
                    shrunk += 1
                if ".." in shown:
                    cut += 1
    print(f"{len(all_names)} names laid out in an {size}px button: "
          f"{shrunk} drawn smaller to fit, {cut} truncated")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad[:15]:
            print("  ", b)
        return 1
    print("hotbar text OK - every line fits inside its button.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
