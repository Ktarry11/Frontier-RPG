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
        self._dragging_scrollbar = False
        self._scroll_track = pygame.Rect(0, 0, 0, 0)  # set each render (scrollbar hit area)

        # Abandon-quest button (detail view only, active quests only) with a
        # two-step confirm so a stray click cannot wipe a quest's progress.
        self.abandon_button = pygame.Rect(20, SCREEN_HEIGHT - 70, 200, 44)
        self.abandon_yes_button = pygame.Rect(20, SCREEN_HEIGHT - 70, 200, 44)
        self.abandon_no_button = pygame.Rect(230, SCREEN_HEIGHT - 70, 120, 44)
        self.abandon_confirm_pending = False
        self.notice = ""

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
            # back to the list first (cancelling a pending abandon first);
            # from the list, Esc closes the journal entirely.
            if self.abandon_confirm_pending:
                self.abandon_confirm_pending = False
            elif self.selected_quest_id is not None:
                self.selected_quest_id = None
            else:
                self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if event.type == pygame.KEYDOWN and self.selected_quest_id is None:
            # Keyboard scrolling: always works, even when a mouse wheel / trackpad
            # does not deliver usable wheel events.
            key_steps = {pygame.K_UP: -self.SCROLL_STEP_PX, pygame.K_DOWN: self.SCROLL_STEP_PX,
                         pygame.K_PAGEUP: -8 * self.SCROLL_STEP_PX, pygame.K_PAGEDOWN: 8 * self.SCROLL_STEP_PX}
            if event.key in key_steps:
                self.scroll_offset += key_steps[event.key]
                return
            if event.key == pygame.K_HOME:
                self.scroll_offset = 0
                return
            if event.key == pygame.K_END:
                self.scroll_offset = 10 ** 6  # clamped to the true bottom on the next render
                return

        if event.type == pygame.MOUSEWHEEL:
            # Scrolls the quest LIST (the detail panel never needs it). Uses
            # precise_y when present - precision touchpads report fractional
            # deltas and an integer .y of 0 for most small swipes, which made
            # scrolling look dead. No viewport hit-test on the mouse position:
            # the list is the only scrollable thing on this screen, and the raw
            # pygame.mouse.get_pos() is in window (not logical) coordinates when
            # the window is scaled, so that test used to fail there.
            if self.selected_quest_id is None:
                delta = getattr(event, "precise_y", None)
                if delta is None or delta == 0:
                    delta = event.y
                self.scroll_offset -= delta * self.SCROLL_STEP_PX
            return

        if event.type == pygame.MOUSEMOTION and self._dragging_scrollbar:
            self._drag_scrollbar_to(event.pos[1])
            return
        if event.type == pygame.MOUSEBUTTONUP:
            self._dragging_scrollbar = False
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
                self.abandon_confirm_pending = False
                return
            quest = self.quest_mgr.quests.get(self.selected_quest_id)
            can_abandon = quest is not None and quest.status in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN)
            if can_abandon and not self.abandon_confirm_pending and self.abandon_button.collidepoint(mouse_pos):
                self.abandon_confirm_pending = True
            elif can_abandon and self.abandon_confirm_pending:
                if self.abandon_yes_button.collidepoint(mouse_pos):
                    title = quest.title
                    if self.quest_mgr.abandon_quest(self.selected_quest_id):
                        self.notice = f'Abandoned "{title}".'
                    self.abandon_confirm_pending = False
                    self.selected_quest_id = None
                    self.scroll_offset = 0
                elif self.abandon_no_button.collidepoint(mouse_pos):
                    self.abandon_confirm_pending = False
            return

        # Scrollbar: click the track to jump, drag the thumb to scroll.
        if self._scroll_track.width and self._scroll_track.inflate(14, 0).collidepoint(mouse_pos):
            self._dragging_scrollbar = True
            self._drag_scrollbar_to(mouse_pos[1])
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

    def _drag_scrollbar_to(self, mouse_y):
        track = self._scroll_track
        max_scroll = max(0, self._list_content_height - self._list_viewport.height)
        if track.height <= 0 or max_scroll <= 0:
            return
        frac = (mouse_y - track.top) / track.height
        self.scroll_offset = int(max(0.0, min(1.0, frac)) * max_scroll)

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
                self.renderer.draw_text(screen, "Scroll for more (wheel, Up/Down, PgUp/PgDn, or drag the bar)",
                                        (SCREEN_WIDTH - 540, SCREEN_HEIGHT - 34),
                                        font_size=14, color=(130, 130, 140))
            if self.notice and self.selected_quest_id is None:
                self.renderer.draw_text(screen, self.notice, (20, SCREEN_HEIGHT - 34),
                                        font_size=16, color=(240, 200, 140))

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
            self._scroll_track = pygame.Rect(0, 0, 0, 0)
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
            self._scroll_track = pygame.Rect(0, 0, 0, 0)
            return  # everything fits - no scrollbar needed, matches how a real scrollbar hides itself

        track_x = viewport.right - 6
        track = pygame.Rect(track_x, viewport.top, 4, viewport.height)
        self._scroll_track = track
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

    #: Detail layout: objectives/story on the left, rewards (with the gear choices) on the right, so the gear you can
    #: pick stays visible while you read the quest instead of only appearing on the accept/turn-in dialogs.
    LEFT_W = 600
    RIGHT_X = 660

    def _where_to_find(self, objective):
        """Quest helper: 'where do I find this' line for a kill/explore objective, or ''."""
        from world.quest_locator import locate
        if objective.objective_type in (ObjectiveType.KILL, ObjectiveType.KILL_BOSS):
            zm = getattr(self.state_manager, "zone_manager", None)
            zones = getattr(zm, "zones", None) or None
            names = [objective.target] + list(getattr(objective, "alt_targets", None) or [])
            places = []
            for n in names:
                for place in locate(n, zones):
                    if place not in places:
                        places.append(place)
            if not places:
                return ""
            shown = places[:3]
            more = f"  (+{len(places) - 3} more)" if len(places) > 3 else ""
            return "Find them: " + "  /  ".join(shown) + more
        if objective.objective_type in (ObjectiveType.FETCH, ObjectiveType.GATHER) and objective.target:
            from world.quest_locator import locate_item
            zm = getattr(self.state_manager, "zone_manager", None)
            zones = getattr(zm, "zones", None) or None
            sources = locate_item(str(objective.target), zones)
            if not sources:
                return ""
            more = f"  (+{len(sources) - 3} more)" if len(sources) > 3 else ""
            return "Dropped by: " + "  /  ".join(sources[:3]) + more
        if objective.objective_type == ObjectiveType.EXPLORE and objective.target:
            return f"Go to: {str(objective.target).replace('_', ' ').title()}"
        return ""

    def _render_detail(self, screen):
        quest = self.quest_mgr.quests.get(self.selected_quest_id)
        self.renderer.draw_button(screen, self.back_button, "Back")
        if quest is None:
            return

        self.renderer.draw_text(screen, quest.title, (20, 130), color=COLOR_WHITE, size="large")
        y = self._draw_wrapped_text(screen, quest.description, (20, 175), max_width=self.LEFT_W,
                                    color=(180, 180, 180), line_height=22)

        y += 14
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
                # progress/count are meaningless here, real progress is topics_asked vs topics.
                progress_text = f"{len(o.topics_asked)}/{len(o.topics)}"
            else:
                progress_text = f"{o.progress}/{o.count}"
            self.renderer.draw_text(screen, f"{check} {label}: {progress_text}", (36, y), color=color)
            y += 26
            if not done:
                where = self._where_to_find(o)
                if where:
                    y = self._draw_wrapped_text(screen, where, (56, y), max_width=self.LEFT_W - 40,
                                                color=(120, 170, 230), line_height=20, font_size=15)
                    y += 6

        y += 14
        level_text = f"Level range: {quest.level_min}"
        if quest.level_max:
            level_text += f" - {quest.level_max}"
        self.renderer.draw_text(screen, level_text, (20, y), color=(150, 150, 150), font_size=16)

        if quest.status == QuestStatus.READY_TO_TURN_IN:
            y += 40
            self.renderer.draw_text(screen, "Ready to turn in - return to the quest giver.",
                                    (20, y), color=COLOR_GOLD)

        self._render_rewards(screen, quest)

        if quest.status in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN):
            if self.abandon_confirm_pending:
                self.renderer.draw_text(screen, "Abandon this quest? All progress will be lost.",
                                        (20, SCREEN_HEIGHT - 105), color=(240, 140, 140))
                self.renderer.draw_button(screen, self.abandon_yes_button, "Yes, abandon", color=(120, 40, 40))
                self.renderer.draw_button(screen, self.abandon_no_button, "Keep it")
            else:
                self.renderer.draw_button(screen, self.abandon_button, "Abandon Quest", color=(110, 40, 40))

    def _render_rewards(self, screen, quest):
        """Right column: XP/gold, then the real gear choices (same fixed set the turn-in screen will offer)."""
        x = self.RIGHT_X
        y = 130
        player = self.state_manager.player
        player_level = player.level if player else 1
        self.renderer.draw_text(screen, "Rewards:", (x, y), color=COLOR_GOLD, size="large")
        y += 36
        line = f"{quest.get_scaled_exp_reward(player_level)} XP"
        if quest.reward_gold:
            line += f"     {quest.reward_gold // 10000}g {(quest.reward_gold % 10000) // 100}s"
        self.renderer.draw_text(screen, line, (x, y))
        y += 34

        if quest.gear_reward_gear_level is None and not quest.unique_item_defs:
            return
        choices = []
        if player and quest.status != QuestStatus.COMPLETED:
            try:
                from entities.loot_generator import LootGenerator
                choices = quest.get_gear_choices(LootGenerator(), player.char_class)
            except Exception:
                choices = []
        if not choices:
            self.renderer.draw_text(screen, "Choice of gear on completion", (x, y), color=(170, 170, 170))
            return
        self.renderer.draw_text(screen, "Choose one on turn-in:", (x, y), color=(170, 170, 170), font_size=16)
        y += 26
        gap = 10
        card_w = (SCREEN_WIDTH - x - 20 - gap) // 2
        card_h = 150
        for i, choice in enumerate(choices[:6]):
            rect = pygame.Rect(x + (i % 2) * (card_w + gap), y + (i // 2) * (card_h + gap), card_w, card_h)
            if rect.bottom > SCREEN_HEIGHT - 10:
                break
            self._render_gear_card(screen, choice, rect)

    def _render_gear_card(self, screen, choice, rect):
        item = choice.item
        pygame.draw.rect(screen, (26, 26, 32), rect)
        pygame.draw.rect(screen, item.get_rarity_color(), rect, 2)
        y = self._draw_wrapped_text(screen, item.name, (rect.x + 8, rect.y + 7), max_width=rect.width - 16,
                                    color=item.get_rarity_color(), line_height=20)
        self.renderer.draw_text(screen, choice.armor_type_label, (rect.x + 8, y), color=(120, 120, 130), font_size=12)
        y += 20
        parts = []
        if item.armor_value:
            parts.append(f"Armor {item.armor_value}")
        if getattr(item, "weapon_damage_max", None):
            parts.append(f"Dmg {item.weapon_damage_min}-{item.weapon_damage_max}")
        if parts:
            self.renderer.draw_text(screen, "   ".join(parts), (rect.x + 8, y), font_size=15)
            y += 20
        stat_names = {"strength": "Str", "agility": "Agi", "intellect": "Int", "stamina": "Sta", "spirit": "Spi"}
        stats = [f"+{v} {stat_names.get(k, k.replace('_', ' ').title())}" for k, v in item.primary_stats.items()]
        for k, v in (getattr(item, "secondary_stats", None) or {}).items():
            stats.append(f"+{v} {k.replace('_', ' ').title()}")
        if stats:
            self._draw_wrapped_text(screen, "  ".join(stats), (rect.x + 8, y), max_width=rect.width - 16,
                                    line_height=19, font_size=15)

    def _draw_wrapped_text(self, screen, text, pos, max_width, color=COLOR_WHITE, line_height=24, font_size=None):
        """Word-wrap text at pos; returns the y just below the last line (pos[1] if text is empty)."""
        x, y = pos
        if not text:
            return y
        font = self.renderer.font_normal
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            width = font.size(test)[0]
            if font_size:
                width = int(width * font_size / 20)
            if width > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)

        for line in lines:
            if font_size:
                self.renderer.draw_text(screen, line, (x, y), color=color, font_size=font_size)
            else:
                self.renderer.draw_text(screen, line, (x, y), color=color)
            y += line_height
        return y
