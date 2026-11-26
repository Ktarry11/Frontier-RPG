import contextlib, io, os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, ".")
import pygame
pygame.init(); screen = pygame.display.set_mode((1280, 720))
from core.game_state import GameStateManager
from entities.character import Character
from ui.screens.inventory_screen import InventoryScreen
from entities.loot_generator import LootGenerator
with contextlib.redirect_stdout(io.StringIO()):
    sm = GameStateManager(screen)
    p = sm.player = Character(name="Hero", char_class="Rogue", level=20)
lg = LootGenerator()
def make(slot):
    for _ in range(400):
        it = lg.generate_item_for_class("Rogue", 20, slot=slot, rarity="uncommon")
        if it and getattr(it, "slot", None) == slot:
            return it
want = sys.argv[2]
with contextlib.redirect_stdout(io.StringIO()):
    worn = [] if want == "trash" else [make(want) for _ in range(2 if want in ("ring", "trinket") else 1)]
    for w in worn: p.equipment.equip(w)
    if want == "trash":
        from entities.loot_item import LootItem
        import inspect
        bagitem = LootItem("vt_worn_venom_gland", "Worn Venom Gland", category="trash", description="Vendor trash. A merchant will give you decent silver for this.", sell_price=125); bagitem.quantity = 3
        worn = []
    else:
        bagitem = make(want)
    p.inventory.append(bagitem)
inv = InventoryScreen(sm)
screen.fill((0,0,0)); inv.render(screen)
bag = inv._bag_source(p)
i = next(k for k, it in enumerate(bag.inventory) if it is bagitem)
shown = inv._shown_inventory(bag)
r = inv.inventory_rects[shown.index(i)]
pygame.mouse.get_pos = lambda: r.center
screen.fill((0,0,0)); inv.render(screen)
pygame.image.save(screen, sys.argv[1]); print("saved", [w.name for w in worn], bagitem.name)
