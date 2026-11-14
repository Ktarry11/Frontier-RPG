"""The Testing menu. TEST ONLY: everything in it skips the game's rules on purpose.

Kyle, 14 Nov 2026: "I want a testing menu with subtabs" for travel, recruits, gold, professions and
materials, "to be able to agitate the system and check it without spending hours because right now
this game is well over 100+ hours playtime." Opened from the overworld's TEST button (it replaced
the old "+5 Levels" button, which lives on in the Gold & Levels tab) or F10.

The actions live in world/testing.py; this screen only lays them out. Each tab is a list of
buttons; the long lists (towns, zones, recruits) scroll with the shared scrollbar.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.scrollbar import ScrollBar, GUTTER

TABS = [("travel", "Travel"), ("recruits", "Recruits"), ("gold", "Gold & Levels"),
        ("professions", "Professions"), ("materials", "Materials")]
TOP = 124
BTN = (40, 44, 62)
DONE = (140, 220, 160)


class TestingScreen(BaseScreen):
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.tab = "travel"
        self.travel_mode = "towns"
        self.return_state = GameState.OVERWORLD
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.scroll = 0
        self.bar = ScrollBar()
        self.hits = []              # [(rect, callable)] rebuilt every frame
        self.message = ""

    def start(self, return_state=None):
        self.return_state = return_state or GameState.OVERWORLD
        self.message = ""

    # ------------------------------------------------------------ helpers
    def _party(self):
        return self.state_manager.get_party()

    def _player(self):
        return self.state_manager.player

    def _zm(self):
        sm = self.state_manager
        return sm._live_zone_manager() if hasattr(sm, "_live_zone_manager") else getattr(sm, "zone_manager", None)

    def _do(self, fn):
        try:
            self.message = fn() or ""
        except Exception as exc:                       # a test tool must never crash the game
            self.message = f"That didn't work: {exc}"
        for m in (self._party().members if self._party() else [self._player()]):
            fn2 = getattr(m, "_recalculate_derived_stats", None)
            if fn2:
                fn2()

    def _button(self, screen, rect, label, action, colour=BTN):
        self.renderer.draw_button(screen, rect, self.renderer.truncate(label, rect.width - 16), color=colour)
        self.hits.append((rect, action))

    # ------------------------------------------------------------ input
    def handle_event(self, event):
        new = self.bar.handle_event(event, self.scroll)
        if new is not None:
            self.scroll = new
            return
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_F10):
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
        for rect, action in list(self.hits):
            if rect.collidepoint(event.pos):
                action()
                return

    # ------------------------------------------------------------ drawing
    def render(self, screen):
        screen.fill((14, 12, 20))
        self.hits = []
        self.renderer.draw_text(screen, "TESTING", (20, 20), size="large", color=(200, 160, 255))
        self.renderer.draw_text(screen, "Test only. Everything here skips the game's rules.", (20, 58),
                                color=(150, 140, 170))
        self.renderer.draw_button(screen, self.close_button, "Close")
        x = 20
        for key, label in TABS:
            w = self.renderer._get_font("normal").size(label)[0] + 36
            rect = pygame.Rect(x, 80, w, 34)
            on = key == self.tab
            self.renderer.draw_button(screen, rect, label, color=(90, 60, 130) if on else (36, 34, 46))
            self.hits.append((rect, lambda k=key: self._switch(k)))
            x += w + 8
        getattr(self, f"_tab_{self.tab}")(screen)
        if self.message:
            for i, line in enumerate(self.renderer.wrap_text(self.message, SCREEN_WIDTH - 40)[:2]):
                self.renderer.draw_text(screen, line, (20, SCREEN_HEIGHT - 44 + i * 20), color=DONE)

    def _switch(self, key):
        self.tab, self.scroll, self.message = key, 0, ""

    def _list(self, screen, items, top, cols, row_h, label_of, action_of, colour_of=None):
        """A scrolling grid of buttons."""
        area = pygame.Rect(20, top, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 60 - top)
        col_w = (area.width - GUTTER - (cols - 1) * 8) // cols
        rows_fit = max(1, area.height // row_h)
        total_rows = (len(items) + cols - 1) // cols
        self.scroll = max(0, min(self.scroll, max(0, total_rows - rows_fit)))
        self.bar.draw(screen, ScrollBar.track_for(area), self.scroll, max(0, total_rows - rows_fit), rows_fit)
        for i, it in enumerate(items[self.scroll * cols:(self.scroll + rows_fit) * cols]):
            r, c = divmod(i, cols)
            rect = pygame.Rect(area.x + c * (col_w + 8), area.y + r * row_h, col_w, row_h - 6)
            self._button(screen, rect, label_of(it), (lambda it=it: action_of(it)),
                         colour_of(it) if colour_of else BTN)

    # ------------------------------------------------------------ the tabs
    def _tab_travel(self, screen):
        from world import testing as T
        self._button(screen, pygame.Rect(20, TOP, 260, 36), "Unlock every flight path",
                     lambda: self._do(T.unlock_flights), (60, 90, 70))
        for i, (mode, label) in enumerate((("towns", "Towns"), ("zones", "Every zone"))):
            on = self.travel_mode == mode
            self._button(screen, pygame.Rect(300 + i * 150, TOP, 140, 36), label,
                         lambda m=mode: self._set_travel(m), (90, 60, 130) if on else BTN)
        zm = self._zm()
        if zm is None:
            self.renderer.draw_text(screen, "No world loaded.", (20, TOP + 50), color=(220, 160, 120))
            return
        dests = T.towns(zm) if self.travel_mode == "towns" else T.zones(zm)
        here = zm.current_zone.name if getattr(zm, "current_zone", None) else None
        self._list(screen, dests, TOP + 50, 4, 40, lambda d: d["label"], self._teleport,
                   lambda d: (50, 80, 55) if d["zone"] == here else BTN)

    def _set_travel(self, mode):
        self.travel_mode, self.scroll = mode, 0

    def _teleport(self, dest):
        from world import testing as T
        self.message = T.teleport(self._zm(), dest)
        self.state_manager.transition_to(GameState.OVERWORLD)
        ow = self.state_manager.states.get(GameState.OVERWORLD)
        if ow is not None and hasattr(ow, "_notify"):
            ow._notify(self.message, (140, 210, 230))

    def _tab_recruits(self, screen):
        from world import testing as T
        party = self._party()
        members = {getattr(m, "recruit_id", None): m for m in T.everyone(party)} if party else {}
        self.renderer.draw_text(screen, "Click anyone to put them in your party now (no level gate, no "
                                        "friendship). Click someone already with you to send them home.",
                                (20, TOP), color=(170, 170, 185))
        rows = T.recruits()

        def label(kv):
            rid, r = kv
            tag = "with you" if rid in members else f"level {r.level}"
            return f"{r.name}  ({r.char_class}, {tag})"

        def act(kv):
            rid, _r = kv
            if rid in members:
                self._do(lambda: T.send_home(party, members[rid]))
            else:
                self._do(lambda: T.force_recruit(party, rid))

        self._list(screen, rows, TOP + 34, 3, 40, label, act,
                   lambda kv: (50, 80, 55) if kv[0] in members else BTN)

    def _tab_gold(self, screen):
        from world import testing as T
        party = self._party()
        self.renderer.draw_text(screen, f"Party gold: {party.get_currency_string()}", (20, TOP), color=COLOR_GOLD)
        y = TOP + 36
        for i, g in enumerate((100, 1000, 10000, 100000)):
            self._button(screen, pygame.Rect(20 + i * 210, y, 200, 40), f"+{g:,} gold",
                         lambda g=g: self._do(lambda: T.add_gold(party, g)), (90, 80, 40))
        y += 70
        self.renderer.draw_text(screen, f"You're level {self._player().level}. Levels go through the real "
                                        f"level-up for the whole party, bench included.", (20, y), color=(170, 170, 185))
        y += 30
        for i, (label, n) in enumerate((("+1 level", 1), ("+5 levels", 5), ("+10 levels", 10), ("To level 60", 60))):
            self._button(screen, pygame.Rect(20 + i * 210, y, 200, 40), label,
                         lambda n=n: self._do(lambda: T.level_party(party, n)))
        y += 60
        self._button(screen, pygame.Rect(20, y, 200, 40), "Heal everyone", lambda: self._do(lambda: T.heal_party(party)),
                     (60, 90, 70))

    def _tab_professions(self, screen):
        from world import testing as T
        p = self._player()
        y = TOP
        self._button(screen, pygame.Rect(20, y, 300, 40), "Learn every profession",
                     lambda: self._do(lambda: T.learn_all_professions(p)), (60, 90, 70))
        self._button(screen, pygame.Rect(340, y, 300, 40), "Learn every recipe (all sources)",
                     lambda: self._do(lambda: T.learn_every_recipe(p)), (60, 90, 70))
        y += 60
        self.renderer.draw_text(screen, "Set every profession you know to:", (20, y), color=(170, 170, 185))
        y += 28
        for i, s in enumerate((75, 150, 225, 300)):
            self._button(screen, pygame.Rect(20 + i * 160, y, 150, 40), f"Skill {s}",
                         lambda s=s: self._do(lambda: T.set_profession_skill(p, s)))
        y += 64
        known = list(p.known_professions)
        self.renderer.draw_text(screen, f"Known ({len(known)}):", (20, y), color=COLOR_GOLD)
        y += 28
        cols = 4
        for i, prof in enumerate(known):
            r, c = divmod(i, cols)
            self.renderer.draw_text(screen, f"{prof.title()}: {p.profession_skills.get(prof, 0)} / {p.profession_cap(prof)}",
                                    (20 + c * 300, y + r * 24), color=COLOR_WHITE)

    def _tab_materials(self, screen):
        from world import testing as T
        p = self._player()
        self.renderer.draw_text(screen, "Fill your bags with 20 of every material in a group (one of each rod "
                                        "and kit). They land in the bags' Materials tab.", (20, TOP), color=(170, 170, 185))
        y = TOP + 36
        for i, (key, label) in enumerate(T.material_categories()):
            r, c = divmod(i, 4)
            self._button(screen, pygame.Rect(20 + c * 300, y + r * 54, 290, 44),
                         "Everything" if key == "all" else label,
                         lambda k=key: self._do(lambda: T.give_materials(p, k)),
                         (90, 80, 40) if key == "all" else BTN)
