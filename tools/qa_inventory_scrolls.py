"""The bag scrolls.

Playtest, 12 Nov: "there is no way to scroll down in the inventory so if you have six rows
full you can't see anything else below that." The grid was laid straight down the screen.
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
    from ui.screens.inventory_screen import InventoryScreen, INV_GRID_COLS
    from entities.loot_item import LootItem

    player, party = build("Warrior", 30)
    for i in range(60):
        player.inventory.append(LootItem(f"junk{i}", f"Thing {i}", category="quest", quest_id="q"))
    scr = InventoryScreen(StubSM(player, party))
    scr.set_subject(player)
    bad = []

    def visible():
        scr.render(screen)
        return [i for i, r in enumerate(scr.inventory_rects) if 0 <= r.y and r.bottom <= SCREEN_HEIGHT]

    first = visible()
    if len(scr.inventory_rects) != len(player.inventory):
        bad.append("the grid does not have one slot per item")
    if not first or first[0] != 0:
        bad.append("the bag does not open at the top")
    if any(r.bottom > SCREEN_HEIGHT and r.y < SCREEN_HEIGHT for r in scr.inventory_rects):
        bad.append("a row is drawn across the bottom edge of the screen")
    if not scr.grid_rows_hidden:
        bad.append("60 items fit without scrolling?")

    seen = set(first)
    for _ in range(40):
        scr.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-1))
        seen.update(visible())
    if seen != set(range(len(player.inventory))):
        bad.append(f"{len(player.inventory) - len(seen)} items can never be scrolled into view")
    last = visible()
    if last[-1] != len(player.inventory) - 1:
        bad.append("scrolling to the bottom does not show the last item")
    for _ in range(40):
        scr.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=1))
    if visible() != first:
        bad.append("scrolling back up does not return to the top")
    scr.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN, mod=0, unicode=""))
    if visible() == first:
        bad.append("Page Down does not scroll")
    if len(sys.argv) > 1:
        pygame.image.save(screen, sys.argv[1])

    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print(f"inventory OK - {len(player.inventory)} items, every one reachable with the wheel or Page Down.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
