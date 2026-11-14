"""Enchanting: read enchantment scrolls onto gear, and disenchant gear into materials.

world/enchanting.py has the rules. Opened from the inventory's Enchant button. Two tabs:

  Enchant     pick a piece of gear (from your bags or anything the party is wearing), then click
              one of your enchantment scrolls that fits it. Gear that already carries an
              enchantment asks once before the old one is replaced.
  Disenchant  pick a green, blue or purple item from your bags; the panel says what it can break
              into and the skill it needs. The Disenchant button destroys it for the materials.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.scrollbar import ScrollBar, GUTTER

LIST_X, LIST_Y, LIST_W, ROW_H = 20, 100, 430, 50
PANEL_X = LIST_X + LIST_W + 30
PANEL_W = SCREEN_WIDTH - PANEL_X - 20
GREEN = (30, 255, 0)


class EnchantScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.mode = "enchant"
        self.return_state = GameState.INVENTORY
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.tab_rects = {"enchant": pygame.Rect(PANEL_X, 20, 130, 36),
                          "disenchant": pygame.Rect(PANEL_X + 140, 20, 150, 36)}
        self.action_button = pygame.Rect(PANEL_X, 0, 200, 40)
        self.selected_item = None
        self.armed_scroll = None
        self.message, self.message_ok = "", True
        self.item_rects, self.scroll_rects = [], []
        self.scroll = 0
        self.scroll_list_offset = 0
        self.gear_bar, self.scrolls_bar = ScrollBar(), ScrollBar()

    def start(self, mode="enchant", return_state=None):
        self.mode = mode
        self.return_state = return_state or GameState.INVENTORY
        self.selected_item = self.armed_scroll = None
        self.message = ""
        self.scroll = self.scroll_list_offset = 0

    # ------------------------------------------------------------ data
    def _gear(self):
        """[(owner, item, where)] for every enchantable item in reach (enchant tab), or every
        disenchantable item in the bags (disenchant tab)."""
        from world import enchanting as E
        sm = self.state_manager
        player = sm.player
        out = []
        if self.mode == "disenchant":
            for it in getattr(player, "inventory", []):
                if getattr(it, "rarity", "") in E.DISENCHANTABLE and (getattr(it, "weapon_type", None) or getattr(it, "slot", None)) \
                        and not getattr(it, "recipe_id", None) and getattr(it, "armor_type", None) != "bag":
                    out.append((player, it, "in your bags"))
            return out
        for it in getattr(player, "inventory", []):
            if E.groups_for(it):
                out.append((player, it, "in your bags"))
        party = sm.get_party()
        members = list(getattr(party, "members", []) or [player]) + list(getattr(party, "bench", []) or [])
        for m in members:
            for it in m.equipment.get_all_equipped():
                if E.groups_for(it):
                    out.append((m, it, f"worn by {m.name}" if m is not player else "worn"))
        return out

    def _scrolls(self):
        """[(scroll id, count, enchant)] in the player's bags, the ones that fit the selected item
        first."""
        from world import enchanting as E
        p = self.state_manager.player
        seen = {}
        for m in p.materials:
            if E.is_scroll(m.material_id):
                seen[m.material_id] = seen.get(m.material_id, 0) + m.quantity
        rows = [(sid, n, E.enchant(sid)) for sid, n in seen.items()]
        item = self.selected_item
        return sorted(rows, key=lambda r: (not (item is not None and E.fits(item, r[0])), r[2]["group"],
                                           -r[2]["level"], r[2]["name"]))

    def _owner_of(self, item):
        for owner, it, _w in self._gear():
            if it is item:
                return owner
        return self.state_manager.player

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        for bar, attr in ((self.gear_bar, "scroll"), (self.scrolls_bar, "scroll_list_offset")):
            new = bar.handle_event(event, getattr(self, attr))
            if new is not None:
                setattr(self, attr, new)
                return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state_manager.transition_to(self.return_state)
            return
        if event.type == pygame.MOUSEWHEEL:
            mx, _my = pygame.mouse.get_pos()
            if mx >= PANEL_X:
                self.scroll_list_offset = max(0, self.scroll_list_offset - event.y)
            else:
                self.scroll = max(0, self.scroll - event.y)
            return
        if event.type != pygame.MOUSEBUTTONDOWN or getattr(event, "button", 1) != 1:
            return
        pos = event.pos
        if self.close_button.collidepoint(pos):
            self.state_manager.transition_to(self.return_state)
            return
        for mode, rect in self.tab_rects.items():
            if rect.collidepoint(pos) and mode != self.mode:
                self.start(mode, self.return_state)
                return
        for item, rect in self.item_rects:
            if rect.collidepoint(pos):
                self.selected_item = item
                self.armed_scroll = None
                self.scroll_list_offset = 0
                self.message = ""
                return
        if self.mode == "enchant":
            for sid, rect in self.scroll_rects:
                if rect.collidepoint(pos):
                    self._scroll_clicked(sid)
                    return
        elif self.selected_item is not None and self.action_button.collidepoint(pos):
            self._disenchant()

    def _scroll_clicked(self, sid):
        from world import enchanting as E
        item = self.selected_item
        if item is None:
            self._say(False, "Pick a piece of gear first.")
            return
        if not E.fits(item, sid):
            e = E.enchant(sid)
            self._say(False, f"{e['name']} doesn't go on {item.name}.")
            return
        if getattr(item, "enchant_id", None) and self.armed_scroll != sid:
            self.armed_scroll = sid
            self._say(False, f"{item.name} is already enchanted ({E.label(item.enchant_id)}). "
                             f"Click the scroll again to replace it.")
            return
        self.armed_scroll = None
        ok, msg = E.apply(self.state_manager.player, item, sid)
        if ok:
            E.refresh(self._owner_of(item))
        self._say(ok, msg)

    def _disenchant(self):
        from world import enchanting as E
        ok, msg, _got = E.disenchant(self.state_manager.player, self.selected_item)
        if ok:
            self.selected_item = None
        self._say(ok, msg)

    def _say(self, ok, msg):
        self.message, self.message_ok = msg, ok

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        from world import enchanting as E
        screen.fill((12, 12, 18))
        self.renderer.draw_text(screen, "ENCHANTING", (20, 20), size="large", color=COLOR_GOLD)
        for mode, rect in self.tab_rects.items():
            on = mode == self.mode
            self.renderer.draw_rect(screen, rect, (45, 40, 60) if on else (30, 30, 36))
            self.renderer.draw_rect(screen, rect, COLOR_GOLD if on else (90, 90, 100), fill=False)
            self.renderer.draw_text(screen, mode.capitalize(), (rect.x + 16, rect.y + 9),
                                    color=COLOR_GOLD if on else (170, 170, 180))
        hint = ("Pick a piece of gear, then click an enchantment scroll that fits it." if self.mode == "enchant"
                else "Pick a green, blue or purple item from your bags. Disenchanting destroys it.")
        self.renderer.draw_text(screen, hint, (20, 66), color=(170, 170, 180))
        self.renderer.draw_button(screen, self.close_button, "Close")

        gear = self._gear()
        if self.selected_item is not None and not any(it is self.selected_item for _o, it, _w in gear):
            self.selected_item = None
        self.item_rects = []
        y = LIST_Y
        visible = (SCREEN_HEIGHT - 60 - LIST_Y) // ROW_H
        self.scroll = max(0, min(self.scroll, max(0, len(gear) - visible)))
        self.gear_bar.draw(screen, ScrollBar.track_for(pygame.Rect(LIST_X, LIST_Y, LIST_W, visible * ROW_H - 4)),
                           self.scroll, max(0, len(gear) - visible), visible)
        if not gear:
            msg = ("Nothing in reach takes an enchantment." if self.mode == "enchant"
                   else "Nothing in your bags can be disenchanted.")
            self.renderer.draw_text(screen, msg, (LIST_X, y), color=(200, 160, 120))
        for owner, it, where in gear[self.scroll:self.scroll + visible]:
            rect = pygame.Rect(LIST_X, y, LIST_W - GUTTER, ROW_H - 4)
            chosen = it is self.selected_item
            self.renderer.draw_rect(screen, rect, (40, 40, 52) if chosen else (26, 26, 32))
            self.renderer.draw_rect(screen, rect, it.get_rarity_color() if chosen else (70, 70, 80), fill=False)
            self.renderer.draw_text(screen, self._fit(it.name, rect.width - 16), (rect.x + 8, rect.y + 3),
                                    color=it.get_rarity_color())
            if self.mode == "enchant":
                ench = E.label(getattr(it, "enchant_id", None))
                sub = f"{where}, " + (f"enchanted: {ench}" if ench else "not enchanted")
            else:
                sub = f"level {E.item_level(it)}, needs Enchanting {E.skill_needed(it)}"
            self.renderer.draw_text(screen, self._fit(sub, rect.width - 16, 13), (rect.x + 8, rect.y + 25),
                                    font_size=13, color=(160, 160, 170))
            self.item_rects.append((it, rect))
            y += ROW_H
        if len(gear) > visible:
            self.renderer.draw_text(screen, f"{self.scroll + 1}-{min(len(gear), self.scroll + visible)} of {len(gear)}, scroll for more",
                                    (LIST_X, SCREEN_HEIGHT - 58), font_size=13, color=(150, 150, 150))

        if self.mode == "enchant":
            self._render_enchant_panel(screen)
        else:
            self._render_disenchant_panel(screen)

        if self.message:
            for i, line in enumerate(self.renderer.wrap_text(self.message, SCREEN_WIDTH - 40)[:2]):
                self.renderer.draw_text(screen, line, (20, SCREEN_HEIGHT - 36 + i * 18 - (18 if len(self.message) > 140 else 0)),
                                        color=(140, 220, 160) if self.message_ok else (240, 180, 120))

    def _fit(self, text, width, font_size=None):
        """Cut a line to the width, so nothing runs out of its box."""
        return self.renderer.truncate(text, width, font_size=font_size)

    def _render_enchant_panel(self, screen):
        from world import enchanting as E
        from world.jewelcrafting import stat_text
        py = LIST_Y
        item = self.selected_item
        if item is not None:
            self.renderer.draw_text(screen, self._fit(item.name, PANEL_W), (PANEL_X, py), color=item.get_rarity_color())
            py += 26
            groups = ", ".join(sorted(E.group_label(g) for g in E.groups_for(item)))
            self.renderer.draw_text(screen, f"Takes {groups} enchantments.", (PANEL_X, py), font_size=14,
                                    color=(170, 170, 180))
            py += 22
            for line in E.tooltip_lines(item) or ["Not enchanted."]:
                for w in self.renderer.wrap_text(line, PANEL_W):
                    self.renderer.draw_text(screen, w, (PANEL_X, py), color=GREEN if item.enchant_id else (150, 150, 150))
                    py += 22
            py += 10
        self.renderer.draw_text(screen, "Your enchantment scrolls", (PANEL_X, py), color=COLOR_GOLD)
        py += 26
        scrolls = self._scrolls()
        self.scroll_rects = []
        if not scrolls:
            self.renderer.draw_text(screen, "You don't have any. An enchanter makes them from formulas.",
                                    (PANEL_X, py), color=(160, 160, 170))
            return
        visible = max(1, (SCREEN_HEIGHT - 70 - py) // 40)
        self.scroll_list_offset = max(0, min(self.scroll_list_offset, max(0, len(scrolls) - visible)))
        self.scrolls_bar.draw(screen, ScrollBar.track_for(pygame.Rect(PANEL_X, py, PANEL_W, visible * 40 - 4)),
                              self.scroll_list_offset, max(0, len(scrolls) - visible), visible)
        for sid, n, e in scrolls[self.scroll_list_offset:self.scroll_list_offset + visible]:
            rect = pygame.Rect(PANEL_X, py, PANEL_W - GUTTER, 36)
            fits = item is not None and E.fits(item, sid)
            armed = sid == self.armed_scroll
            self.renderer.draw_rect(screen, rect, (40, 34, 30) if armed else ((30, 34, 30) if fits else (24, 24, 30)))
            self.renderer.draw_rect(screen, rect, GREEN if fits else (60, 60, 70), fill=False)
            what = e["proc"]["describe"] if e.get("proc") else stat_text(e["stats"])
            self.renderer.draw_text(screen, self._fit(f"{e['name']} x{n}", PANEL_W // 2 - 10), (rect.x + 10, rect.y + 9),
                                    color=COLOR_WHITE if fits or item is None else (130, 130, 135))
            self.renderer.draw_text(screen, self._fit(what, PANEL_W // 2 - 14 - GUTTER, 14), (rect.x + PANEL_W // 2, rect.y + 10),
                                    font_size=14, color=(140, 220, 160) if fits else (110, 130, 115))
            self.scroll_rects.append((sid, rect))
            py += 40
        if len(scrolls) > visible:
            self.renderer.draw_text(screen, f"{len(scrolls)} scrolls, scroll for more", (PANEL_X, py), font_size=13,
                                    color=(150, 150, 150))
        # hover a scroll for its whole text (Kyle, 14 Nov: descriptions that run off)
        mouse = pygame.mouse.get_pos()
        for sid, rect in self.scroll_rects:
            if rect.collidepoint(mouse):
                e = E.enchant(sid)
                from ui.hover_text import draw_hover
                lines = [f"Goes on: {E.group_label(e['group'])}" + (" (any weapon)" if e["group"] == "weapon" else ""),
                         e["proc"]["describe"] if e.get("proc") else stat_text(e["stats"])]
                draw_hover(screen, self.renderer, e["name"], lines, mouse)
                break

    def _render_disenchant_panel(self, screen):
        from world import enchanting as E
        item = self.selected_item
        py = LIST_Y
        if item is None:
            skill = self.state_manager.player.profession_skills.get("enchanting", 0)
            self.renderer.draw_text(screen, f"Your Enchanting skill: {skill}", (PANEL_X, py), color=COLOR_WHITE)
            return
        self.renderer.draw_text(screen, self._fit(item.name, PANEL_W), (PANEL_X, py), color=item.get_rarity_color())
        py += 30
        self.renderer.draw_text(screen, "Can break into:", (PANEL_X, py), color=COLOR_GOLD)
        py += 26
        for w in self.renderer.wrap_text(E.outcome_text(item), PANEL_W):
            self.renderer.draw_text(screen, w, (PANEL_X, py), color=COLOR_WHITE)
            py += 22
        py += 10
        ok, why = E.can_disenchant(self.state_manager.player, item)
        if not ok:
            for w in self.renderer.wrap_text(why, PANEL_W):
                self.renderer.draw_text(screen, w, (PANEL_X, py), color=(240, 160, 120))
                py += 22
            py += 6
        self.action_button.topleft = (PANEL_X, py)
        self.renderer.draw_rect(screen, self.action_button, (40, 30, 50) if ok else (28, 28, 32))
        self.renderer.draw_rect(screen, self.action_button, (180, 120, 230) if ok else (70, 70, 80), fill=False)
        self.renderer.draw_text(screen, "Disenchant", (self.action_button.x + 52, self.action_button.y + 11),
                                color=(220, 190, 250) if ok else (110, 110, 115))
