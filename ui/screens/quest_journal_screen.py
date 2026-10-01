"""
QuestJournalScreen - the "L" tab. Lists active quests (with live
objective progress, refreshed on open so gather/fetch counts reflect
current bag contents - see QuestManager.refresh_gather_progress) and
completed quests, grouped separately. Read-only: accepting/turning in
quests only happens through QuestDialogScreen when talking to the actual
giver NPC (see that module's docstring) - this screen is for reviewing
what you're already carrying, not a menu for quest actions.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from world.quest import QuestStatus, ObjectiveType


class QuestJournalScreen(BaseScreen):
    #: Pixels scrolled per mouse-wheel notch. One notch (event.y == 1)
    #: moves a bit less than one row_h, so a single scroll click feels
    #: incremental rather than snapping a whole row at once.
    SCROLL_STEP_PX = 48

    def __init__(self, state_manager):
        super().__init__(state_manager)

        self.selected_quest_id = None  # None = show the list; set = show that quest's detail panel
        self.close_button = pygame.Rect(SCREEN_WIDTH - 140, 20, 110, 40)
        self.back_button = pygame.Rect(20, 20, 110, 40)

        self.active_tab = "active"  # "active" | "completed"
        self.active_tab_button = pygame.Rect(20, 70, 160, 36)
        self.completed_tab_button = pygame.Rect(190, 70, 160, 36)

        self.quest_row_rects = []  # rebuilt each render, index-aligned to the currently listed quests

        # Scroll state for the quest list. Kyle, 2026-09-09: "we need a
        # scroll option for the quests as we get too many" - the list
        # previously just drew every quest starting at y=130 with no
        # bound check against SCREEN_HEIGHT, so with ~9+ quests in one
        # tab (easily reached - 40+ quests are authored across the
        # zones) later rows silently drew off the bottom of the screen:
        # not clickable, not visible, and nothing on screen indicated
        # more existed. scroll_offset is in PIXELS scrolled down from the
        # top of the list; clamped in _render_list to
        # [0, max(0, content_height - viewport_height)] every render, so
        # it can never point past the real content even if the list
        # shrinks out from under a stale offset (e.g. switching from a
        # long Completed tab to a short Active tab).
        self.scroll_offset = 0
        self._list_viewport = pygame.Rect(0, 0, 0, 0)  # set each render, used by handle_event's wheel check
        self._list_content_height = 0  # set each render, used to clamp scroll_offset

    @property
    def quest_mgr(self):
        """Always resolves the LIVE singleton rather than a reference
        cached at __init__ time. Real bug this fixes: QuestJournalScreen
        is constructed once, eagerly, in GameStateManager's static
        states dict - but the quest manager singleton gets REPLACED
        (not mutated) by both CharacterCreationScreen._create_character
        and GameStateManager.load_game (see world/quest_manager.py's
        module-level _quest_manager swap in both places, added to fix
        quest-state leaking between characters/saves). A cached
        self.quest_mgr = get_quest_manager() at __init__ time silently
        kept pointing at the OLD, now-discarded manager after either of
        those ran, so the Journal always showed an empty list even
        though quests were genuinely active on the real, current
        manager - reported live as "I get the info but nothing appears
        in the journal." QuestDialogScreen never hit this because it's
        rebuilt fresh per NPC interaction (see game_state.py's
        _ensure_quest_dialog_screen), but this screen is long-lived, so
        it needs to fetch fresh every time instead of caching once.
        """
        from world.quest_manager import get_quest_manager
        return get_quest_manager()

    def _refresh_progress(self):
        """Gather/fetch objectives track live bag contents rather than an
        incrementing counter (see QuestManager.refresh_gather_progress) -
        called every time this screen opens so displayed progress can't
        go stale between a bag change and the next kill/zone-entry event."""
        player = self.state_manager.player
        if player:
            self.quest_mgr.refresh_gather_progress(player)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Same one-step-back-then-close feel as the back_button already
            # gives with the mouse: from a quest's detail view, Esc steps
            # back to the list first; from the list, Esc closes the
            # journal entirely (Kyle: "when opening quest journal - to hit
            # Esc and close it").
            if self.selected_quest_id is not None:
                self.selected_quest_id = None
            else:
                self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if event.type == pygame.MOUSEWHEEL:
            # Only scrolls the quest LIST (not the detail panel, which
            # doesn't need it - quest descriptions are short enough to
            # fit without scrolling). event.y is +1 per notch up, -1 per
            # notch down; SCROLL_STEP_PX converts that into a pixel
            # delta. Clamping happens in _render_list every frame (the
            # single source of truth for valid range), not here - this
            # just applies the raw delta and lets the next render pull
            # it back in bounds if it overshot.
            if self.selected_quest_id is None and self._list_viewport.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y * self.SCROLL_STEP_PX
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        mouse_pos = event.pos

        if self.close_button.collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if self.selected_quest_id is not None:
            if self.back_button.collidepoint(mouse_pos):
                self.selected_quest_id = None
            return

        if self.active_tab_button.collidepoint(mouse_pos):
            if self.active_tab != "active":
                self.active_tab = "active"
                self.scroll_offset = 0  # switching tabs starts scrolled to top, not carrying over a stale offset from the other tab's list length
            return
        if self.completed_tab_button.collidepoint(mouse_pos):
            if self.active_tab != "completed":
                self.active_tab = "completed"
                self.scroll_offset = 0
            return

        for i, rect in enumerate(self.quest_row_rects):
            # Intersect against the viewport, not just the row's own
            # rect - a row can be scrolled partially behind the tab
            # buttons (or, before this screen existed, the bottom hint
            # bar) and still occupy real on-screen pixel coordinates
            # there even though set_clip() prevented it from actually
            # being drawn. Without this check a click on, say, the tab
            # button area could double as a click on a clipped-but-
            # coordinate-present row underneath it.
            if rect.collidepoint(mouse_pos) and self._list_viewport.collidepoint(mouse_pos):
                quests = self._current_list()
                if i < len(quests):
                    self.selected_quest_id = quests[i].quest_id
                return

    def _current_list(self):
        if self.active_tab == "active":
            return self.quest_mgr.get_active_quests()
        return self.quest_mgr.get_completed_quests()

    def update(self, dt):
        pass

    def render(self, screen):
        self._refresh_progress()
        screen.fill((10, 10, 15))

        self.renderer.draw_text(screen, "QUEST JOURNAL", (SCREEN_WIDTH // 2 - 110, 24),
                                size="large", color=COLOR_GOLD)
        self.renderer.draw_button(screen, self.close_button, "Close")

        if self.selected_quest_id is not None:
            self._render_detail(screen)
        else:
            self._render_list(screen)
            if self._list_content_height > self._list_viewport.height:
                # Only shown when there's actually something to scroll -
                # matches the scrollbar's own "hide when everything fits"
                # rule in _render_scrollbar, so this hint and the visual
                # scrollbar always agree about whether scrolling is
                # relevant right now.
                self.renderer.draw_text(screen, "Scroll for more",
                                        (SCREEN_WIDTH - 160, SCREEN_HEIGHT - 34),
                                        font_size=14, color=(130, 130, 140))

    def _render_list(self, screen):
        active_color = (60, 55, 30) if self.active_tab == "active" else (30, 30, 35)
        completed_color = (60, 55, 30) if self.active_tab == "completed" else (30, 30, 35)
        self.renderer.draw_button(screen, self.active_tab_button, "Active", color=active_color)
        self.renderer.draw_button(screen, self.completed_tab_button, "Completed", color=completed_color)

        quests = self._current_list()
        self.quest_row_rects = []

        if not quests:
            msg = "No active quests." if self.active_tab == "active" else "No completed quests yet."
            self.renderer.draw_text(screen, msg, (20, 140), color=(150, 150, 150))
            self._list_viewport = pygame.Rect(0, 0, 0, 0)
            self._list_content_height = 0
            return

        row_h = 64
        list_top = 130
        # Leave room for the bottom hint bar (drawn by the caller after
        # this method returns) so the scrollable area's own clip rect
        # doesn't paint over/under it.
        list_bottom = SCREEN_HEIGHT - 50
        viewport = pygame.Rect(20, list_top, SCREEN_WIDTH - 40, list_bottom - list_top)
        self._list_viewport = viewport

        content_height = len(quests) * row_h
        self._list_content_height = content_height

        # Clamp AFTER computing content_height for the CURRENT quest list -
        # this is the one place scroll_offset's valid range is enforced,
        # so a stale offset from a longer list (or a list that shrank
        # since last render, e.g. a quest just got completed and moved
        # tabs) always gets pulled back in bounds instead of leaving a
        # dead scroll position pointing at nothing.
        max_scroll = max(0, content_height - viewport.height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        # Clip drawing to the viewport rect so a row that's fully or
        # partially scrolled out of view is actually cut off cleanly
        # (not just "happens to land off the real screen edge", which
        # is what let rows silently disappear past SCREEN_HEIGHT before -
        # this makes the visible boundary explicit and intentional, and
        # also means a row can't visually bleed into the tab buttons or
        # hint bar above/below the list).
        screen.set_clip(viewport)

        y = list_top - self.scroll_offset
        for quest in quests:
            row_rect = pygame.Rect(20, y, SCREEN_WIDTH - 40, row_h - 8)

            # Rows fully above or below the viewport contribute nothing
            # visible - skip drawing them (cheap, and set_clip would hide
            # them anyway) but DO still record a rect for click hit-testing
            # below, at their real (possibly off-viewport) position, so
            # index alignment with quests[] never shifts based on scroll
            # position - handle_event's collidepoint check against a
            # rect outside the viewport simply never matches a real
            # on-screen mouse click, so this is safe without extra
            # bookkeeping.
            self.quest_row_rects.append(row_rect)

            if row_rect.bottom >= viewport.top and row_rect.top <= viewport.bottom:
                pygame.draw.rect(screen, (24, 24, 30), row_rect)
                pygame.draw.rect(screen, (70, 70, 80), row_rect, 1)

                title_color = COLOR_WHITE
                if self.active_tab == "active" and quest.status == QuestStatus.READY_TO_TURN_IN:
                    title_color = COLOR_GOLD
                self.renderer.draw_text(screen, quest.title, (row_rect.x + 12, row_rect.y + 8), color=title_color)

                if self.active_tab == "active":
                    summary = self._objective_summary(quest)
                    status_note = "  (ready to turn in)" if quest.status == QuestStatus.READY_TO_TURN_IN else ""
                    self.renderer.draw_text(screen, summary + status_note, (row_rect.x + 12, row_rect.y + 32),
                                            color=(170, 170, 170), font_size=16)
                else:
                    self.renderer.draw_text(screen, quest.zone.replace("_", " ").title(),
                                            (row_rect.x + 12, row_rect.y + 32), color=(140, 140, 140), font_size=16)

            y += row_h

        screen.set_clip(None)

        self._render_scrollbar(screen, viewport, content_height)

    def _render_scrollbar(self, screen, viewport, content_height):
        """Thin vertical track + thumb along the list's right edge - the
        only on-screen signal that more quests exist below the fold, so
        a long list doesn't just quietly end with no indication there's
        more (which was effectively the old bug's experience even after
        adding scroll input: technically scrollable, but nothing tells
        the player that)."""
        if content_height <= viewport.height:
            return  # everything fits - no scrollbar needed, matches how a real scrollbar hides itself

        track_x = viewport.right - 6
        track = pygame.Rect(track_x, viewport.top, 4, viewport.height)
        pygame.draw.rect(screen, (40, 40, 48), track)

        thumb_h = max(24, int(viewport.height * (viewport.height / content_height)))
        max_scroll = content_height - viewport.height
        scroll_frac = (self.scroll_offset / max_scroll) if max_scroll > 0 else 0
        thumb_y = viewport.top + int((viewport.height - thumb_h) * scroll_frac)
        thumb = pygame.Rect(track_x, thumb_y, 4, thumb_h)
        pygame.draw.rect(screen, (150, 140, 100), thumb)

    def _objective_summary(self, quest):
        """One-line 'N/M target, N/M target' progress string for the list
        row - the detail panel breaks this out per-objective, this is
        just the at-a-glance version."""
        parts = []
        for o in quest.objectives:
            if o.objective_type == ObjectiveType.STORY:
                continue
            if o.objective_type == ObjectiveType.DIALOGUE:
                # progress/count are meaningless for DIALOGUE (never
                # incremented - see QuestObjective.__init__) - real
                # progress lives in topics_asked vs topics instead.
                # Without this branch the summary always showed a static,
                # never-updating "0/1 topics" regardless of how many
                # topics had actually been asked.
                parts.append(f"{len(o.topics_asked)}/{len(o.topics)} topics")
                continue
            label = o.display_label()
            parts.append(f"{o.progress}/{o.count} {label}")
        return "  |  ".join(parts) if parts else "In progress"

    def _render_detail(self, screen):
        quest = self.quest_mgr.quests.get(self.selected_quest_id)
        self.renderer.draw_button(screen, self.back_button, "Back")
        if quest is None:
            return

        self.renderer.draw_text(screen, quest.title, (20, 130), color=COLOR_WHITE, size="large")
        self._draw_wrapped_text(screen, quest.description, (20, 175), max_width=SCREEN_WIDTH - 40,
                                color=(180, 180, 180))

        y = 260
        self.renderer.draw_text(screen, "Objectives:", (20, y), color=COLOR_GOLD)
        y += 30
        for o in quest.objectives:
            if o.objective_type == ObjectiveType.STORY:
                continue
            label = o.display_label()
            done = o.is_complete()
            color = (120, 220, 140) if done else COLOR_WHITE
            check = "[X]" if done else "[ ]"
            if o.objective_type == ObjectiveType.DIALOGUE:
                # Same reasoning as QuestJournalScreen._objective_summary -
                # progress/count are meaningless here, real progress is
                # topics_asked vs topics.
                progress_text = f"{len(o.topics_asked)}/{len(o.topics)}"
            else:
                progress_text = f"{o.progress}/{o.count}"
            self.renderer.draw_text(screen, f"{check} {label}: {progress_text}", (36, y), color=color)
            y += 26

        y += 20
        player_level = self.state_manager.player.level if self.state_manager.player else 1
        scaled_exp = quest.get_scaled_exp_reward(player_level)
        self.renderer.draw_text(screen, "Rewards:", (20, y), color=COLOR_GOLD)
        y += 30
        self.renderer.draw_text(screen, f"{scaled_exp} XP", (36, y))
        y += 26
        if quest.reward_gold:
            self.renderer.draw_text(screen, f"{quest.reward_gold // 10000}g {(quest.reward_gold % 10000) // 100}s",
                                    (36, y))
            y += 26
        if quest.gear_reward_gear_level is not None:
            self.renderer.draw_text(screen, "Choice of gear on completion", (36, y), color=(170, 170, 170))
            y += 26

        y += 20
        level_text = f"Level range: {quest.level_min}"
        if quest.level_max:
            level_text += f" - {quest.level_max}"
        self.renderer.draw_text(screen, level_text, (20, y), color=(150, 150, 150), font_size=16)

        if quest.status == QuestStatus.READY_TO_TURN_IN:
            y += 40
            self.renderer.draw_text(screen, "Ready to turn in - return to the quest giver.",
                                    (20, y), color=COLOR_GOLD)

    def _draw_wrapped_text(self, screen, text, pos, max_width, color=COLOR_WHITE, line_height=24):
        if not text:
            return
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            width = self.renderer.font_normal.size(test)[0]
            if width > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)

        x, y = pos
        for line in lines:
            self.renderer.draw_text(screen, line, (x, y), color=color)
            y += line_height
