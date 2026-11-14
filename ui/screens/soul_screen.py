"""The Soul: imprint runes (Runecrafting) on a party member.

world/runes.py has the rules. Opened from the party screen's "Soul" button for whoever is
selected. Left: the four slots, three runes and the Capstone, with what each does. Right: the runes
in your bags, the ones that fit the chosen slot first. Click a slot, then a rune. A rune already in
that slot is destroyed when you imprint over it, so it asks once first.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.scrollbar import ScrollBar, GUTTER

SLOT_X, SLOT_Y, SLOT_W, SLOT_H = 20, 110, 560, 96
LIST_X = SLOT_X + SLOT_W + 30
LIST_W = SCREEN_WIDTH - LIST_X - 20
ROW_H = 54
ROLE_COLOURS = {"tank": (120, 170, 230), "damage": (230, 120, 110), "healing": (130, 220, 140),
                "any": (200, 190, 150)}
CAPSTONE_COLOUR = (240, 200, 90)


class SoulScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.subject = None
        self.return_state = GameState.PARTY
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.slot = 0
        self.armed = None
        self.scroll = 0
        self.bar = ScrollBar()
        self.message, self.message_ok = "", True
        self.slot_rects, self.rune_rects = [], []

    def start(self, character, return_state=None):
        self.subject = character
        self.return_state = return_state or GameState.PARTY
        self.slot = 0
        self.armed = None
        self.scroll = 0
        self.message = ""

    def _who(self):
        return self.subject or self.state_manager.player

    def _runes(self):
        """[(rune id, count, rune)] in the player's bags; the ones for the chosen slot first."""
        from world import runes as R
        seen = {}
        for m in self.state_manager.player.materials:
            if R.is_rune(m.material_id):
                seen[m.material_id] = seen.get(m.material_id, 0) + m.quantity
        cap = self.slot == R.CAPSTONE_SLOT
        rows = [(rid, n, R.rune(rid)) for rid, n in seen.items()]
        return sorted(rows, key=lambda r: (r[2]["capstone"] != cap, r[2].get("role", ""), r[2]["family"], -r[2]["rank"]))

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        new = self.bar.handle_event(event, self.scroll)
        if new is not None:
            self.scroll = new
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state_manager.transition_to(self.return_state)
            return
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, self.scroll - event.y)
            return
        if event.type != pygame.MOUSEBUTTONDOWN or getattr(event, "button", 1) != 1:
            return
        if self.close_button.collidepoint(event.pos):
            self.state_manager.transition_to(self.return_state)
            return
        for i, rect in self.slot_rects:
            if rect.collidepoint(event.pos):
                self.slot, self.armed, self.scroll = i, None, 0
                self.message = ""
                return
        for rid, rect in self.rune_rects:
            if rect.collidepoint(event.pos):
                self._rune_clicked(rid)
                return

    def _rune_clicked(self, rid):
        from world import runes as R
        who = self._who()
        ok, why = R.can_imprint(who, self.slot, rid)
        if not ok:
            self._say(False, why)
            return
        current = R.rune(R.soul(who)[self.slot])
        if current and self.armed != rid:
            self.armed = rid
            self._say(False, f"That slot holds {current['name']}. Click again to imprint over it. "
                             f"The old rune will be destroyed.")
            return
        self.armed = None
        ok, msg = R.imprint(self.state_manager.player, who, self.slot, rid)
        self._say(ok, msg)

    def _icon(self, rune_id, size):
        """The rune's own icon (tools/slice_rune_sheets.py), or None."""
        from ui.sprite_loader import get_icon_sprite
        from world.gathering_manager import get_gathering_node_manager
        d = get_gathering_node_manager().get_material_def(rune_id) or {}
        if not d.get("icon_id"):
            return None
        return get_icon_sprite(f"assets/gathering_nodes/runes/{d['icon_id']}.png", size)

    def _say(self, ok, msg):
        self.message, self.message_ok = msg, ok

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        from world import runes as R
        who = self._who()
        screen.fill((10, 10, 16))
        self.renderer.draw_text(screen, f"{who.name.upper()}'S SOUL", (20, 20), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(screen, "Three runes and one Capstone. Pick a slot, then a rune from your bags. "
                                        "Imprinting over a rune destroys it.", (20, 66), color=(170, 170, 180))
        self.renderer.draw_button(screen, self.close_button, "Close")

        self.slot_rects = []
        soul = R.soul(who)
        for i in range(R.SLOTS):
            rect = pygame.Rect(SLOT_X, SLOT_Y + i * (SLOT_H + 12), SLOT_W, SLOT_H)
            cap = i == R.CAPSTONE_SLOT
            chosen = i == self.slot
            edge = CAPSTONE_COLOUR if cap else (150, 140, 200)
            self.renderer.draw_rect(screen, rect, (40, 36, 52) if chosen else (24, 24, 32))
            self.renderer.draw_rect(screen, rect, edge if chosen else (70, 70, 85), fill=False)
            rn = R.rune(soul[i])
            label = "Capstone" if cap else f"Rune {i + 1}"
            tx = rect.x + 12
            if rn:
                icon = self._icon(soul[i], 76)
                if icon is not None:
                    screen.blit(icon, (rect.x + 8, rect.y + (rect.height - 76) // 2))
                    tx = rect.x + 92
            self.renderer.draw_text(screen, label, (tx, rect.y + 8), font_size=14, color=edge)
            if rn:
                self.renderer.draw_text(screen, self.renderer.truncate(rn["name"], rect.right - tx - 12),
                                        (tx, rect.y + 28), color=COLOR_WHITE)
                for j, line in enumerate(self.renderer.wrap_text(rn["text"], rect.right - tx - 12, font_size=14)[:2]):
                    self.renderer.draw_text(screen, line, (tx, rect.y + 52 + j * 18), font_size=14,
                                            color=(170, 200, 170))
            else:
                self.renderer.draw_text(screen, "Empty", (tx, rect.y + 34), color=(110, 110, 120))
            self.slot_rects.append((i, rect))

        # the runes in the bags
        cap = self.slot == R.CAPSTONE_SLOT
        self.renderer.draw_text(screen, "Capstone runes in your bags" if cap else "Runes in your bags",
                                (LIST_X, SLOT_Y - 26), color=COLOR_GOLD)
        rows = self._runes()
        self.rune_rects = []
        visible = (SCREEN_HEIGHT - 60 - SLOT_Y) // ROW_H
        self.scroll = max(0, min(self.scroll, max(0, len(rows) - visible)))
        self.bar.draw(screen, ScrollBar.track_for(pygame.Rect(LIST_X, SLOT_Y, LIST_W, visible * ROW_H - 4)),
                      self.scroll, max(0, len(rows) - visible), visible)
        if not rows:
            self.renderer.draw_text(screen, "No runes. A runecrafter writes them from enchanting dust and essence.",
                                    (LIST_X, SLOT_Y), color=(150, 150, 160))
        y = SLOT_Y
        for rid, n, rn in rows[self.scroll:self.scroll + visible]:
            rect = pygame.Rect(LIST_X, y, LIST_W - GUTTER, ROW_H - 6)
            fits, _why = R.can_imprint(who, self.slot, rid)
            armed = rid == self.armed
            colour = CAPSTONE_COLOUR if rn["capstone"] else ROLE_COLOURS.get(rn.get("role", "any"), COLOR_WHITE)
            self.renderer.draw_rect(screen, rect, (44, 36, 30) if armed else ((30, 32, 38) if fits else (22, 22, 26)))
            self.renderer.draw_rect(screen, rect, colour if fits else (60, 60, 70), fill=False)
            icon = self._icon(rid, ROW_H - 10)
            tx = rect.x + 10
            if icon is not None:
                screen.blit(icon, (rect.x + 4, rect.y + 2))
                tx = rect.x + ROW_H
            self.renderer.draw_text(screen, self.renderer.truncate(f"{rn['name']} x{n}   (level {rn['level']})", rect.right - tx - 10),
                                    (tx, rect.y + 4), color=colour if fits else (120, 120, 125))
            self.renderer.draw_text(screen, self.renderer.truncate(rn["text"], rect.right - tx - 10, font_size=13),
                                    (tx, rect.y + 26), font_size=13,
                                    color=(170, 190, 170) if fits else (100, 105, 100))
            self.rune_rects.append((rid, rect))
            y += ROW_H

        if self.message:
            for i, line in enumerate(self.renderer.wrap_text(self.message, SCREEN_WIDTH - 40)[:2]):
                self.renderer.draw_text(screen, line, (20, SCREEN_HEIGHT - 44 + i * 20),
                                        color=(140, 220, 160) if self.message_ok else (240, 180, 120))

        # HOVER FOR THE WHOLE TEXT (Kyle: "rune descriptions that run off, we need to be able to
        # have a way to see them fully")
        mouse = pygame.mouse.get_pos()
        hovered = next((rid for rid, rect in self.rune_rects if rect.collidepoint(mouse)), None)
        if hovered is None:
            hovered = next((soul[i] for i, rect in self.slot_rects if rect.collidepoint(mouse) and soul[i]), None)
        if hovered:
            rn = R.rune(hovered)
            ok, why = R.can_imprint(who, self.slot, hovered)
            role = "Capstone" if rn["capstone"] else {"tank": "Tanking", "damage": "Damage", "healing": "Healing"}.get(rn.get("role"), "Anyone")
            from ui.hover_text import draw_hover
            draw_hover(screen, self.renderer, rn["name"],
                       [f"{role} rune, level {rn['level']}", rn["text"]] + ([] if ok or hovered in soul else [why]), mouse)
