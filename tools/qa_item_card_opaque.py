"""
An item card is opaque, and says what the item sells for.

Kyle, 10 Nov: item tooltips must be opaque cards; and (confirmed) the vendor sell price goes at
the bottom of the card.

The inventory drew its tooltip and THEN drew the EFFECTIVE STATS block, the equip error and
the Close button, so a card for a piece of equipped gear had the character's stats written
through it.

  1. hover every equipment slot and every bag item: the pixels inside the card are exactly the
     card drawn alone on an empty surface - nothing else shows through or over it
  2. a bag item's card ends with "Sell Price: <coins>"; the price is the item's real sell price
  3. equipped gear shows no sell price; neither does anything unsellable or worth nothing
"""
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pygame  # noqa: E402

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from tools.shot_screen import StubSM, build
    from entities.loot_generator import LootGenerator
    from ui.screens.inventory_screen import InventoryScreen
    from ui.coin_format import format_coins

    random.seed(3)
    player, party = build("Warrior", 40)
    sm = StubSM(player, party)
    gen = LootGenerator()
    for slot in ("head", "chest", "legs", "wrist", "feet", "hands", "waist", "shoulder"):
        it = gen.generate_item_for_class("Warrior", 40, slot=slot, rarity="rare")
        if it is not None:
            player.inventory.append(it)
            player.equip_item(it)
    for _ in range(18):
        it = gen.generate_item_for_class("Warrior", 40, rarity=random.choice(["uncommon", "rare", "epic"]))
        if it is not None:
            player.inventory.append(it)
    worthless = gen.generate_item_for_class("Warrior", 40, rarity="uncommon")
    worthless.sell_price = 0
    player.inventory.append(worthless)

    scr = InventoryScreen(sm)
    scr.set_subject(player)
    scr.equip_error = "You cannot equip that."          # the thing that used to print over the card
    real_mouse = pygame.mouse.get_pos
    texts = []
    real_draw = scr.renderer.draw_text

    def spy(screen, text, *a, **k):
        texts.append(str(text))
        return real_draw(screen, text, *a, **k)
    scr.renderer.draw_text = spy

    def render_at(pos):
        pygame.mouse.get_pos = lambda: pos
        surf.fill((20, 20, 20))
        texts.clear()
        scr.last_tooltip_rect = None
        scr.render(surf)
        return list(texts)

    render_at((-10, -10))
    equipped = [(k, r) for k, r in scr.slot_rects.items() if player.equipment.get_equipped(k)]
    check(len(equipped) >= 6, f"rig: only {len(equipped)} slots equipped")
    check(len(scr.inventory_rects) >= 10, "rig: bag grid has no rects")

    def card_alone(item, pos, sell):
        blank = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        blank.fill((20, 20, 20))
        scr._draw_item_tooltip(blank, item, pos, show_sell_price=sell)
        return blank

    def same_pixels(rect, other):
        a = surf.subsurface(rect).copy()
        b = other.subsurface(rect).copy()
        return pygame.image.tostring(a, "RGB") == pygame.image.tostring(b, "RGB")

    n = 0
    for key, rect in equipped:
        item = player.equipment.get_equipped(key)
        seen = render_at(rect.center)
        card = scr.last_tooltip_rect
        if not check(card is not None, f"hovering equipped {key} draws no card"):
            continue
        n += 1
        check(same_pixels(card, card_alone(item, rect.center, False)),
              f"equipped {key} ({item.name}): something is drawn through or over its card")
        check(not any(t.startswith("Sell Price") for t in seen),
              f"equipped {key} shows a sell price")

    bag = player.inventory
    for i, rect in enumerate(scr.inventory_rects[:len(bag)]):
        item = bag[i]
        seen = render_at(rect.center)
        card = scr.last_tooltip_rect
        if not check(card is not None, f"hovering bag item {item.name} draws no card"):
            continue
        n += 1
        check(same_pixels(card, card_alone(item, rect.center, True)),
              f"bag item {item.name}: something is drawn through or over its card")
        price_lines = [t for t in seen if t.startswith("Sell Price")]
        if item.sell_price > 0:
            want = f"Sell Price: {format_coins(item.sell_price)}"
            check(price_lines == [want], f"{item.name} should end with {want!r}; card shows {price_lines}")
            check(seen and seen[-1] == want or want in seen[-3:],
                  f"{item.name}: the sell price is not at the foot of the card")
        else:
            check(not price_lines, f"{item.name} is worth nothing and still shows {price_lines}")

    pygame.mouse.get_pos = real_mouse
    print(f"{n} item cards checked")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("item cards OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
