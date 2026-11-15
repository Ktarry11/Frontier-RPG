"""The socket screen's gem list stays on the screen and scrolls.

Kyle, 14 Nov 2026, with a screenshot of the list running off the bottom: "gems run off the screen".
It drew twelve rows whatever room there was. Now it draws what fits, with its own scrollbar and the
wheel, and every gem can be reached.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from config import SCREEN_HEIGHT
    from shot_screen import build, StubSM
    from ui.screens.socket_screen import SocketScreen
    from world.gathering_manager import get_gathering_node_manager
    gm = get_gathering_node_manager()
    from world import jewelcrafting as J

    player, party = build("Mage", 40)
    cuts = list(J.data()["cut_gems"])[:40]
    for cid in cuts:
        m = gm.make_material_instance(cid)
        m.quantity = 3
        player.materials.append(m)
    scr = SocketScreen(StubSM(player, party))
    scr.start("socket")
    bad = []

    def visible():
        scr.render(screen)
        return [cid for cid, r in scr.gem_rects]

    first = visible()
    rects = [r for _c, r in scr.gem_rects]
    if any(r.bottom > SCREEN_HEIGHT for r in rects):
        bad.append("a gem row is drawn past the bottom of the screen")
    if len(first) >= len(cuts):
        bad.append("40 gems fit without scrolling?")
    seen = set(first)
    mid = scr.gem_area.center
    pygame.mouse.set_pos(mid)
    for _ in range(60):
        scr.gem_scroll += 1      # the wheel's effect (the dummy video driver can't place the pointer)
        seen.update(visible())
    if seen != set(cuts):
        bad.append(f"{len(set(cuts) - seen)} gems can never be scrolled into view")
    if bad:
        print("FAIL")
        for b in bad:
            print("  -", b)
        return 1
    print(f"socket gem list OK - {len(cuts)} gems, {len(first)} on screen at once, all reachable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
