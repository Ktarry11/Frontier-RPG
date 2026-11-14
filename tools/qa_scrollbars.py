#!/usr/bin/env python3
"""Scrollbars sit clear of the rows and can be dragged.

    PYTHONPATH=. python3 tools/qa_scrollbars.py

Kyle, 14 Nov 2026: "for a lot of the menus, where there is a slider to drag down, it overlaps with
the right side of the item so you can't actually use it... I notice it in shops when buying etc."

CLAIMS, for the shop (both lists), the bags (gear and materials), the crafting list, the quest
log, the enchanting screen and the sockets screen:
  1. With more than fits, a bar is drawn, and no row it scrolls overlaps it.
  2. Dragging the thumb to the bottom scrolls to the end; clicking the top of the track goes back
     to the start. Neither click selects a row.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    def ev(kind, pos):
        if kind == "down":
            return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
        if kind == "up":
            return pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1)
        return pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(1, 0, 0))

    def drag(name, scr, bar, rows, get_scroll, render, max_scroll):
        """Drag bar's thumb to the bottom, then click the top of its track."""
        render()
        check(bar.max_scroll > 0 and bar.track.height > 0, f"{name}: no scrollbar with a long list")
        for r in rows():
            if r.colliderect(bar.track):
                check(False, f"{name}: a row {r} overlaps the scrollbar {bar.track}")
                break
        scr.handle_event(ev("down", bar.thumb.center))
        scr.handle_event(ev("move", (bar.thumb.centerx, bar.track.bottom + 50)))
        scr.handle_event(ev("up", (bar.thumb.centerx, bar.track.bottom + 50)))
        render()
        check(get_scroll() == max_scroll(), f"{name}: dragging to the bottom scrolled to {get_scroll()}, not {max_scroll()}")
        scr.handle_event(ev("down", (bar.track.centerx, bar.track.top + 1)))
        scr.handle_event(ev("up", (bar.track.centerx, bar.track.top + 1)))
        render()
        check(get_scroll() == 0, f"{name}: clicking the top of the track left it at {get_scroll()}")

    with contextlib.redirect_stdout(io.StringIO()):
        from core.game_state import GameStateManager
        from core.game_states import GameState
        from entities.character import Character
        from entities.party import Party
        from entities.loot_generator import LootGenerator
        from world.gathering_manager import get_gathering_node_manager
        from world.vendor_manager import get_vendor_manager
        from ui.screens.vendor_screen import VendorScreen
        gsm = GameStateManager(screen)
        hero = Character(name="Scroll", char_class="Paladin", level=60)
        party = Party(hero)
        gsm.player = hero
        gsm.get_party = lambda: party
        gm = get_gathering_node_manager()
        gen = LootGenerator()

    # the shop: the biggest one, and a bag full enough to scroll the sell side
    vm = get_vendor_manager()
    vendor = max(vm.vendors.values(), key=lambda v: len(getattr(v, "sells", []) or []))
    for _ in range(30):
        hero.inventory.append(gen.generate_armor_piece("chest", "plate", "str_physical", 40, "uncommon"))
    with contextlib.redirect_stdout(io.StringIO()):
        vs = VendorScreen(gsm, vendor)
    vs.render(screen)
    vbar, pbar = vs._bars()
    check(len(vs.vendor_inventory) > vs.VISIBLE_ROWS, f"the biggest shop has only {len(vs.vendor_inventory)} things")
    drag("shop stock", vs, vbar, lambda: [vs._row_rect(vs.VENDOR_PANEL_X, i) for i in range(vs.VISIBLE_ROWS)],
         lambda: vs.scroll_vendor, lambda: vs.render(screen), lambda: vs._max_scroll(len(vs.vendor_inventory)))
    check(vs.selected_vendor_item is None, "a click on the shop's scrollbar picked an item")
    drag("your items (shop)", vs, pbar, lambda: [vs._row_rect(vs.PLAYER_PANEL_X, i) for i in range(vs.VISIBLE_ROWS)],
         lambda: vs.scroll_player, lambda: vs.render(screen), lambda: vs._max_scroll(len(vs._player_stock())))
    check(vs.selected_player_item is None, "a click on the sell side's scrollbar picked an item")

    # the bags: materials
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    for mid in list(mats)[:90]:
        m = gm.make_material_instance(mid)
        m.quantity = 1
        hero.add_material(m)
    inv = gsm.states[GameState.INVENTORY]
    inv.active_tab = "materials"
    inv.material_subtab = "all"
    inv.grid_scroll = 0

    def inv_render():
        screen.fill((0, 0, 0))
        inv.render(screen)
    inv_render()
    drag("materials", inv, inv.grid_bar, lambda: [r for r in inv.materials_rects if r.y > -1000],
         lambda: inv.grid_scroll, inv_render, lambda: inv.grid_rows_hidden)

    # the crafting list
    hero.learn_profession("enchanting")
    hero.profession_skills["enchanting"] = 300
    ps = gsm.states[GameState.PROFESSIONS]
    ps.active_tab = "enchanting"
    ps.craft_scroll = 0

    def ps_render():
        screen.fill((0, 0, 0))
        ps.render(screen)
    ps_render()
    n = len(ps._craft_recipes("enchanting"))
    drag("crafting list", ps, ps.craft_bar, lambda: [r for _rid, r in ps.craft_recipe_rects],
         lambda: ps.craft_scroll, ps_render, lambda: ps.craft_bar.max_scroll)

    # the enchanting screen's gear list
    for _ in range(20):
        hero.inventory.append(gen.generate_armor_piece("wrist", "plate", "str_physical", 40, "uncommon"))
    es = gsm.states[GameState.ENCHANTING]
    es.start("enchant")

    def es_render():
        screen.fill((0, 0, 0))
        es.render(screen)
    es_render()
    drag("enchanting gear list", es, es.gear_bar, lambda: [r for _i, r in es.item_rects],
         lambda: es.scroll, es_render, lambda: es.gear_bar.max_scroll)
    check(es.selected_item is None, "a click on the enchanting scrollbar picked an item")

    # the quest log: rows stop short of the bar
    qj = gsm.states.get(GameState.QUEST_JOURNAL) if hasattr(GameState, "QUEST_JOURNAL") else None
    if qj is not None:
        from ui.scrollbar import GUTTER
        src = (ROOT / "ui/screens/quest_journal_screen.py").read_text(encoding="utf-8")
        check(src.count("SCREEN_WIDTH - 40 - GUTTER") >= 2, "the quest log's rows still run under its scrollbar")

    print(f"shop {len(vs.vendor_inventory)} items, materials {len(hero.materials)}, crafting list {n}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("scrollbars OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
