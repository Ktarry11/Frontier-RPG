"""
QuestDialogScreen - the actual conversation UI when the player talks to
a quest-giving NPC. Handles three real cases, checked in this priority
order (matches QuestManager.get_indicator_for_npc's same priority -
collect what's ready before offering something new):

1. A quest is READY_TO_TURN_IN at this NPC -> show turn_in_text, the
   reward summary (XP/gold, scaled XP shown for real), and if the quest
   has a gear reward, a fixed 4-way choice (see world/quest.py
   build_reward_gear_set). Turning in immediately unlocks the next
   quest in the chain (if any), which then shows as a fresh "new quest"
   screen in the SAME dialog session - matches Kyle's "kill vile
   familiars, then kill the boss" chain reading as one continuous
   conversation with the guard, not two separate menu trips.
2. Otherwise, a new quest is offerable -> show accept_text, description,
   level requirement (greyed out with a clear reason if the player is
   under level_min), and Accept/Decline.
3. Otherwise -> the NPC's plain greeting (ambient NPCs) or a generic
   line (vendors), same text the old toast-only interaction showed -
   this screen is a strict superset of that behavior, not a replacement
   that loses the plain-greeting case.
"""
import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_GOLD
from core.game_states import GameState
from entities.coins import coins
from ui.screens.base_screen import BaseScreen
from world.quest import QuestStatus
from world.travel_manager import get_travel_manager, services_for_npc


class QuestDialogScreen(BaseScreen):
    def __init__(self, state_manager, npc):
        super().__init__(state_manager)
        self.npc = npc
        self.npc_id = getattr(npc, "vendor_id", None) or getattr(npc, "npc_id", None)
        # Vendors get a Shop/Leave choice in greeting mode instead of just
        # Close - detected via vendor_id rather than isinstance so this
        # doesn't need to import VendorNPC (keeps this screen decoupled
        # from world/vendor_manager.py the same way it already is from
        # AmbientNPC/RecruitNPC).
        self.is_vendor = hasattr(npc, "vendor_id")
        self.is_banker = bool(getattr(npc, "is_banker", False))
        # Travel services this NPC offers (innkeeper bind, flight master, riding trainer, mount vendor) -
        # see world/travel_manager.py. Shown as extra buttons in greeting mode.
        self.services = services_for_npc(npc)

        # Which "mode" this screen is currently showing - recomputed in
        # _refresh() rather than decided once in __init__, since turning
        # a quest in can immediately reveal a next-chain quest to offer
        # within the same NPC conversation (see module docstring).
        self.mode = None       # "turn_in" | "offer" | "greeting" | "dialogue"
        self.active_quest = None
        self.gear_choice_stage = False  # True = showing the 4-way gear picker instead of the summary
        self.selected_gear_index = None
        self.result_message = None  # transient confirmation text ("You received...")

        # DIALOGUE-mode state (see world/quest_dialogue.py). selected_topic
        # is which topic's response is currently being shown, or None for
        # the topic-picker list itself; topic_button_rects is rebuilt each
        # render, index-aligned to the topic list for click hit-testing,
        # same pattern quest_row_rects uses elsewhere.
        self.selected_topic = None
        self.topic_button_rects = []

        self.close_button = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 70, 110, 40)
        self.accept_button = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 90, 200, 50)
        self.decline_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 90, 200, 50)
        self.turn_in_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 90, 200, 50)
        self.gear_choice_rects = []  # built in _build_gear_choice_rects, 4 slots
        self.dialogue_back_button = pygame.Rect(40, SCREEN_HEIGHT - 90, 160, 44)
        # Same size/position as accept/decline - greeting mode never shows
        # both the quest pair and the shop pair at once (a vendor with
        # quest business shows "offer"/"turn_in" mode instead, same as
        # any other quest giver), so reusing the layout is safe.
        self.shop_button = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT - 90, 200, 50)
        self.leave_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 90, 200, 50)

        self._refresh()

    @property
    def quest_mgr(self):
        """Always resolves the LIVE singleton rather than caching a
        reference - see QuestJournalScreen.quest_mgr's docstring for the
        full real bug this pattern fixes (the manager gets REPLACED, not
        mutated, by character creation and load_game). Lower risk here
        since this screen is rebuilt per NPC interaction anyway, but the
        cost of using a live property instead of a cached attribute is
        zero, so there's no reason to leave this one exposed to the same
        class of bug."""
        from world.quest_manager import get_quest_manager
        return get_quest_manager()

    def _refresh(self):
        """Recompute what this screen should be showing right now. Called
        on init and after every accept/turn-in action, so the dialog
        always reflects live quest state rather than a snapshot taken
        when the player first walked up."""
        self.gear_choice_stage = False
        self.selected_gear_index = None

        # FETCH / DELIVER progress is read off the bag; bring it up to date so a quest whose items the player
        # just collected (or was just handed on accept) is turn-in-ready the moment we look.
        player = getattr(self.state_manager, "player", None)
        if player is not None:
            self.quest_mgr.refresh_gather_progress(player)

        turn_ins = self.quest_mgr.get_turn_in_ready_quests(self.npc_id)
        if turn_ins:
            self.mode = "turn_in"
            self.active_quest = turn_ins[0]
            return

        # DIALOGUE quests need their own mode on a return visit - see
        # get_in_progress_dialogue_quests's docstring for why this can't
        # just fall through to "greeting" the way every other in-progress
        # quest type correctly does.
        in_progress_dialogue = self.quest_mgr.get_in_progress_dialogue_quests(self.npc_id)
        if in_progress_dialogue:
            self.mode = "dialogue"
            self.active_quest = in_progress_dialogue[0]
            return

        offerable = self.quest_mgr.get_offerable_quests(self.npc_id)
        if offerable:
            self.mode = "offer"
            self.active_quest = offerable[0]
            return

        self.mode = "greeting"
        self.active_quest = None

    def _build_gear_choice_rects(self, count):
        """Lay out `count` reward cards - single row for up to 4 (fits
        comfortably at 220px cards), wraps to two rows above that so a
        6-option set (Kyle: "It can be 2, 3, 4, upwards of 6") never
        overflows the 1280px screen width (4*220+3*20=940 fits fine;
        6*220+5*20=1420 would not)."""
        self.gear_choice_rects = []
        card_w, card_h = 220, 260
        gap = 20
        max_per_row = 4
        row_count = (count + max_per_row - 1) // max_per_row
        for i in range(count):
            row = i // max_per_row
            col = i % max_per_row
            items_in_this_row = min(max_per_row, count - row * max_per_row)
            total_w = items_in_this_row * card_w + (items_in_this_row - 1) * gap
            start_x = (SCREEN_WIDTH - total_w) // 2
            y = 180 + row * (card_h + 20)
            self.gear_choice_rects.append(
                pygame.Rect(start_x + col * (card_w + gap), y, card_w, card_h))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Mirrors clicking Close - drawn and clickable in every mode
            # of this screen (greeting/offer/turn-in/gear-choice), so Esc
            # is safe to wire the same way everywhere rather than only in
            # some modes (Kyle: "Esc to work when looking at quest screen
            # to exit it... when accepting quests, after accepting
            # quests, and also when opening quest journal").
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        mouse_pos = event.pos

        if self.close_button.collidepoint(mouse_pos):
            self.state_manager.transition_to(GameState.OVERWORLD)
            return

        # Shop / Bank / services, reachable from any mode. Checked before the
        # per-mode handlers so a quest offer cannot swallow the click, which is
        # the whole point - see _side_service_buttons.
        for _label, action, rect in self._side_service_buttons():
            if rect.collidepoint(mouse_pos):
                self._do_greeting_action(action)
                return

        if self.mode == "turn_in" and self.gear_choice_stage:
            for i, rect in enumerate(self.gear_choice_rects):
                if rect.collidepoint(mouse_pos):
                    player = self.state_manager.player
                    fit = self.quest_mgr.grant_gear_choice(self.active_quest, i, player)
                    self.result_message = (
                        "Received!" if fit else "Your bag is full - couldn't take that item.")
                    self.gear_choice_stage = False
                    self._refresh()
                    return
            return

        if self.mode == "turn_in" and self.turn_in_button.collidepoint(mouse_pos):
            player = self.state_manager.player
            party = self.state_manager.get_party()
            quest = self.active_quest
            ok = self.quest_mgr.turn_in_quest(quest.quest_id, player, party)
            if ok and quest.gear_reward_gear_level is not None:
                from entities.loot_generator import LootGenerator
                quest.get_gear_choices(LootGenerator(), player.char_class)
                self._build_gear_choice_rects(len(quest.gear_choices))
                self.gear_choice_stage = True
                # Stay on this quest's turn-in mode long enough to show
                # the gear picker - _refresh() would otherwise immediately
                # move on to the next offerable/turn-in quest and the
                # gear choice would be lost.
                self.active_quest = quest
                return
            self.result_message = "Quest complete!" if ok else "Something went wrong."
            # Faction standing, set by QuestManager.turn_in_quest. Appended rather than replacing, so the
            # player still sees the completion line - and a tier change gets its own sentence, because
            # crossing into Honored is the kind of thing that should not scroll past as a number.
            if ok:
                fid, gained, tier_up = getattr(self.quest_mgr, "faction_gain", (None, 0, None))
                if fid and gained:
                    from world.faction_manager import get_faction_manager
                    fm = get_faction_manager()
                    name = fm.get(fid).name
                    self.result_message += f"\n+{gained} reputation with {name}."
                    if tier_up:
                        self.result_message += f"\nYou are now {tier_up['name']} with {name}."
                self.quest_mgr.faction_gain = (None, 0, None)
            # Asher's scripted departure (see QuestManager.turn_in_quest)
            # overrides the generic "Quest complete!" line with his actual
            # farewell, when this was the quest that triggers it.
            if ok and getattr(self.quest_mgr, "departure_message", None):
                self.result_message = self.quest_mgr.departure_message
                self.quest_mgr.departure_message = None
            self._refresh()
            return

        if self.mode == "offer":
            player_level = self.state_manager.player.level
            available = self.quest_mgr.is_quest_available_to_player(self.active_quest, player_level)
            if available and self.accept_button.collidepoint(mouse_pos):
                ok = self.quest_mgr.accept_quest(self.active_quest.quest_id, player_level=player_level,
                                                 player=self.state_manager.player)
                if not ok and getattr(self.quest_mgr, "last_error", None):
                    self.result_message = self.quest_mgr.last_error
                    return
                self._refresh()
                return
            if self.decline_button.collidepoint(mouse_pos):
                self.state_manager.transition_to(GameState.OVERWORLD)
                return

        if self.mode == "dialogue":
            if self.selected_topic is not None:
                if self.dialogue_back_button.collidepoint(mouse_pos):
                    self.selected_topic = None
                return

            for topic_id, rect in self.topic_button_rects:
                if not rect.collidepoint(mouse_pos):
                    continue
                quest = self.active_quest
                objective = next(
                    (o for o in quest.objectives if o.objective_type.value == "dialogue"),
                    None)
                if objective is not None:
                    objective.ask_topic(topic_id)
                    # Mirrors turn_in_quest's own completion transition
                    # (world/quest_manager.py) - a DIALOGUE quest has no
                    # separate "kill counter reached, mark ready" event
                    # to hook, since asking the last topic IS the moment
                    # completion happens. Checked right here rather than
                    # inside QuestObjective.ask_topic() so the objective
                    # class stays a plain data/state object with no
                    # knowledge of Quest-level status transitions.
                    if quest.is_complete() and quest.status == QuestStatus.ACTIVE:
                        quest.status = QuestStatus.READY_TO_TURN_IN
                self.selected_topic = topic_id
                return
            return

        if self.mode == "greeting" and self._has_action_row():
            for label, action, rect in self._greeting_buttons():
                if rect.collidepoint(mouse_pos):
                    self._do_greeting_action(action)
                    return
            return

    # ------------------------------------------------------------------ greeting action row
    SERVICE_LABELS = {"inn": "Bind Hearthstone", "flight": "Fly", "riding": "Train Riding", "mounts": "Buy Mounts",
                      "train_class": "Train Skills", "train_prof": "Train Profession"}

    def _has_action_row(self):
        """Vendors (Shop/Leave) and travel-service NPCs get a row of action buttons instead of a lone Close."""
        return self.is_vendor or self.is_banker or bool(self.services)

    def _side_service_buttons(self):
        """Shop / Bank / services, available in EVERY mode - not just greeting.

        Kyle, 2 Nov 2026: "vendors who are also quest givers need a quick
        overhaul. Right now we can't use a shop keeper unless we accept all
        their quests."

        _refresh() puts the screen in "offer" mode whenever the NPC has a quest
        the player has not taken, and Shop was only drawn in "greeting" mode -
        which a quest-giving vendor only reaches once nothing is offerable. So
        the shop was gated behind accepting (or exhausting) every quest they
        had, and declining does not clear the offer, so accepting was the only
        way through. The quartermasters at Hammerfall and Refuge Pointe both
        sell AND give quests, so this was about to get worse.

        Drawn as a compact column on the left rather than folded into the
        accept/decline row: that row is the quest decision and stays exactly as
        it was, so nothing about taking a quest changes shape. Shopping is a
        separate errand and now reads as one.
        """
        if self.mode == "greeting":
            return []           # greeting already lays these out across the bottom
        entries = [(self.SERVICE_LABELS[s], s) for s in self.services
                   if s in self.SERVICE_LABELS]
        if self.is_vendor:
            entries.insert(0, ("Shop", "shop"))
        if self.is_banker:
            entries.append(("Bank", "bank"))
        if not entries:
            return []
        # Stacked UPWARD from above the bottom row. Sitting at SCREEN_HEIGHT-90
        # put the first button exactly on top of dialogue mode's Back button,
        # which lives at (40, SCREEN_HEIGHT-90, 160, 44) - two buttons on the
        # same pixels, with whichever drew last winning the click.
        w, h, gap = 150, 36, 8
        x = 40
        y = SCREEN_HEIGHT - 150 - (len(entries) - 1) * (h + gap)
        out = []
        for label, action in entries:
            out.append((label, action, pygame.Rect(x, y, w, h)))
            y += h + gap
        return out

    def _greeting_buttons(self):
        """[(label, action, rect)] - service buttons, then Shop for vendors, then Leave; centred in one row."""
        entries = [(self.SERVICE_LABELS[s], s) for s in self.services if s in self.SERVICE_LABELS]
        if self.is_vendor:
            entries.append(("Shop", "shop"))
        if self.is_banker:
            entries.append(("Bank", "bank"))
        entries.append(("Leave", "leave"))
        w, h, gap = 200, 50, 16
        total = len(entries) * w + (len(entries) - 1) * gap
        x = SCREEN_WIDTH // 2 - total // 2
        y = SCREEN_HEIGHT - 90
        out = []
        for label, action in entries:
            out.append((label, action, pygame.Rect(x, y, w, h)))
            x += w + gap
        return out

    def _do_greeting_action(self, action):
        travel = get_travel_manager()
        sm = self.state_manager
        if action == "leave":
            sm.transition_to(GameState.OVERWORLD)
        elif action == "bank":
            sm.transition_to(GameState.BANK, current_banker=self.npc)
        elif action == "shop":
            # Vendor with nothing quest-related right now: talk, then choose to shop or walk away.
            sm.transition_to(GameState.VENDOR, current_vendor=self.npc)
        elif action == "inn":
            zm = sm._live_zone_manager()
            zone = zm.current_zone
            travel.set_bind(zone.name, zm.player_x, zm.player_y, zone.name)
            self.result_message = f"Your hearthstone is now bound to {zone.name}."
        elif action in ("flight", "riding", "mounts", "train_class", "train_prof"):
            screen = sm.states.get(GameState.TRAVEL)
            screen.open_service(action, self.npc)
            sm.transition_to(GameState.TRAVEL)

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((10, 10, 15))

        # NPC name banner
        self.renderer.draw_text(screen, self.npc.name, (40, 30), size="large", color=COLOR_GOLD)

        if self.mode == "turn_in" and self.gear_choice_stage:
            self._render_gear_choice(screen)
        elif self.mode == "turn_in":
            self._render_turn_in(screen)
        elif self.mode == "offer":
            self._render_offer(screen)
        elif self.mode == "dialogue":
            self._render_dialogue(screen)
        else:
            self._render_greeting(screen)

        # Vendor greeting mode shows Shop/Leave instead of the generic
        # Close button - Leave already covers "back to overworld", so
        # drawing Close too would be a redundant third exit option.
        if not (self.mode == "greeting" and self._has_action_row()):
            self.renderer.draw_button(screen, self.close_button, "Close")

        # Shop / Bank / services alongside the quest, in every non-greeting
        # mode. Drawn last so nothing a mode renderer draws can cover them.
        for label, _action, rect in self._side_service_buttons():
            self.renderer.draw_button(screen, rect, label)

    def _render_greeting(self, screen):
        greeting = getattr(self.npc, "greeting", "") or f"{self.npc.name} has nothing more to say right now."
        self._draw_wrapped_text(screen, greeting, (40, 100), max_width=SCREEN_WIDTH - 80)

        if self._has_action_row():
            for label, _action, rect in self._greeting_buttons():
                self.renderer.draw_button(screen, rect, label)
            if self.result_message:
                # SPLIT ON THE NEWLINE. This message is assembled with "\n" between its
                # sentences and draw_text draws a single line, so the newline came out as a
                # missing-glyph box: "Quest complete!<box>+165 reputation with Orgrimmar."
                for i, line in enumerate(str(self.result_message).split("\n")):
                    self.renderer.draw_text(screen, line,
                                            (40, SCREEN_HEIGHT - 130 + i * 22),
                                            color=(120, 220, 140))

    def _render_offer(self, screen):
        quest = self.active_quest
        player_level = self.state_manager.player.level
        available = self.quest_mgr.is_quest_available_to_player(quest, player_level)

        self.renderer.draw_text(screen, quest.title, (40, 90), color=COLOR_WHITE)
        self._draw_wrapped_text(screen, quest.accept_text, (40, 130), max_width=SCREEN_WIDTH - 80)
        self._draw_wrapped_text(screen, quest.description, (40, 260), max_width=SCREEN_WIDTH - 80,
                                 color=(170, 170, 170))

        level_text = f"Requires level {quest.level_min}"
        if quest.level_max:
            level_text += f" (recommended through {quest.level_max})"
        level_color = COLOR_WHITE if available else (200, 90, 90)
        self.renderer.draw_text(screen, level_text, (40, 380), color=level_color)

        reward_lines = [f"Reward: {quest.reward_exp} XP"]
        if quest.reward_gold:
            reward_lines.append(coins(quest.reward_gold))
        # REPUTATION IS A REWARD AND BELONGS HERE. It was only ever mentioned after the fact, in
        # the green confirmation line, so you could not see it while deciding whether the quest
        # was worth doing - Kyle: "It should fall under the 'reward' section if we can. So we can
        # see like 'x exp, x money, x rep'". faction_manager.quest_reward reads it off the
        # quest's zone, so it is known here, before turn-in, without the quest carrying a field.
        try:
            from world.faction_manager import get_faction_manager
            fm = get_faction_manager()
            fid, amt = fm.quest_reward(quest)
            if fid and amt > 0:
                reward_lines.append(f"+{amt} {fm.get(fid).name}")
        except Exception:
            pass        # a reward preview must never be what stops a quest being readable
        self.renderer.draw_text(screen, "   ".join(reward_lines), (40, 410), color=COLOR_GOLD)

        # Real reward preview instead of a vague "+ choice of gear" line
        # (Kyle: "let's have the rewards previewed when the quest is
        # given, rather than 'choice of reward' as this will let us see
        # if we even care about the quest lol"). Built once and cached
        # on the Quest itself via get_gear_choices, so viewing the
        # preview doesn't roll anything different from what turn-in
        # will actually offer - same fixed set, just shown earlier.
        if quest.gear_reward_gear_level is not None:
            from entities.loot_generator import LootGenerator
            choices = quest.get_gear_choices(LootGenerator(), self.state_manager.player.char_class)
            self._render_reward_preview_row(screen, choices, y=440)

        # What this quest hands you / where it is handed in (deliver and "report to" quests).
        info_y = 410 + 28
        grants = (quest.grant_items or {}).get("on_accept") or []
        if grants:
            names = ", ".join(g["name"] for g in grants)
            self.renderer.draw_text(screen, f"You will receive: {names}", (40, info_y),
                                    color=(120, 170, 230), font_size=16)
            info_y += 22
        if quest.turn_in_npc_id:
            from world.quest_locator import npc_place
            where = npc_place(quest.turn_in_npc_id)
            if where:
                self.renderer.draw_text(screen, f"Hand in to: {where}", (40, info_y),
                                        color=(120, 170, 230), font_size=16)
        if self.result_message:
            self.renderer.draw_text(screen, self.result_message, (40, SCREEN_HEIGHT - 130), color=(220, 120, 110))

        if available:
            self.renderer.draw_button(screen, self.accept_button, "Accept")
        else:
            self.renderer.draw_button(screen, self.accept_button, "Accept", color=(50, 50, 50))
            self.renderer.draw_text(screen, "Too low level", (self.accept_button.x, self.accept_button.y - 24),
                                    color=(200, 90, 90), font_size=16)
        self.renderer.draw_button(screen, self.decline_button, "Not Now")

    def _render_reward_preview_row(self, screen, choices, y):
        """Compact single-row preview of a quest's gear reward options -
        smaller and less detailed than the real turn-in gear-choice cards
        (see _render_gear_choice), just enough to see what's on offer
        before committing to the quest. Card width shrinks as count
        grows so 2-6 options always fit one row without wrapping, unlike
        the full turn-in screen which wraps to a second row instead."""
        count = len(choices)
        if count == 0:
            return
        available_w = SCREEN_WIDTH - 80
        gap = 12
        card_w = min(180, (available_w - (count - 1) * gap) // count)
        card_h = 130
        total_w = count * card_w + (count - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2

        for i, choice in enumerate(choices):
            item = choice.item
            rect = pygame.Rect(start_x + i * (card_w + gap), y, card_w, card_h)
            pygame.draw.rect(screen, (26, 26, 32), rect)
            pygame.draw.rect(screen, item.get_rarity_color(), rect, 2)
            self._draw_wrapped_text(screen, item.name, (rect.x + 6, rect.y + 8),
                                    max_width=card_w - 12, color=item.get_rarity_color(),
                                    line_height=16)
            # armor_type_label ("Dagger (Agi)") reads as a mechanical tag,
            # not a title - it used to sit ABOVE the item name in its own
            # slightly-brighter line, which made two things look like
            # they were both trying to be the card's title (Kyle: "this
            # is the Dagger (Agi) box i was talking about that looks
            # weird"). Demoted below the name, smaller and dimmer, same
            # subtitle treatment a tooltip gives an item's type line.
            self.renderer.draw_text(screen, choice.armor_type_label, (rect.x + 6, rect.y + 46),
                                    color=(120, 120, 130), font_size=12)
            stat_y = rect.y + 70
            if item.armor_value:
                self.renderer.draw_text(screen, f"Armor {item.armor_value}", (rect.x + 6, stat_y), font_size=14)
                stat_y += 18
            if getattr(item, "weapon_damage_max", None):
                self.renderer.draw_text(
                    screen, f"Dmg {item.weapon_damage_min}-{item.weapon_damage_max}",
                    (rect.x + 6, stat_y), font_size=14)
                stat_y += 18
            for stat, value in list(item.primary_stats.items())[:2]:  # first 2 fit the compact card
                self.renderer.draw_text(screen, f"+{value} {stat[:3].title()}",
                                        (rect.x + 6, stat_y), font_size=14)
                stat_y += 18

    def _render_dialogue(self, screen):
        """DIALOGUE-quest topic picker + response view (Kyle, 2026-09-10:
        turn "A Real Town" into "ask about Durotar, then Razor Hill, then
        Orgrimmar, then it completes"). Two states within this one mode:
        - self.selected_topic is None: show the list of topic buttons,
          each marked whether it's already been asked.
        - self.selected_topic is set: show that topic's response text and
          a Back button to return to the list.
        Completion (objective.is_complete() -> True -> quest auto-
        transitions to READY_TO_TURN_IN) is checked in handle_event right
        after ask_topic() records a new topic, not here - render methods
        in this screen are pure display, they never mutate quest state.
        """
        from world.quest_dialogue import get_topic, get_all_topics

        quest = self.active_quest
        self.renderer.draw_text(screen, quest.title, (40, 90), color=COLOR_WHITE)

        objective = next(
            (o for o in quest.objectives if o.objective_type.value == "dialogue"),
            None)
        if objective is None:
            # Shouldn't happen - get_in_progress_dialogue_quests only
            # returns quests that have one - but fails soft to the plain
            # accept_text rather than a blank screen if data ever drifts.
            self._draw_wrapped_text(screen, quest.accept_text, (40, 130), max_width=SCREEN_WIDTH - 80)
            return

        if self.selected_topic is not None:
            topic_data = get_topic(quest.quest_id, self.selected_topic)
            response = topic_data["response"] if topic_data else "..."
            self._draw_wrapped_text(screen, response, (40, 140), max_width=SCREEN_WIDTH - 80)
            self.renderer.draw_button(screen, self.dialogue_back_button, "Back")
            return

        self._draw_wrapped_text(screen, quest.accept_text, (40, 130), max_width=SCREEN_WIDTH - 80,
                                line_height=22)

        self.topic_button_rects = []
        topics = get_all_topics(quest.quest_id)
        y = 230
        for topic_id, label in topics:
            already_asked = topic_id in objective.topics_asked
            rect = pygame.Rect(40, y, 420, 44)
            self.topic_button_rects.append((topic_id, rect))
            color = (40, 60, 40) if already_asked else (40, 40, 55)
            button_label = f"\u2713 {label}" if already_asked else label
            self.renderer.draw_button(screen, rect, button_label, color=color)
            y += 54

        remaining = [t for t, _ in topics if t not in objective.topics_asked]
        if remaining:
            hint = f"{len(remaining)} more to ask before you're done here."
        else:
            hint = "That's everything - come back and talk to finish up."
        self.renderer.draw_text(screen, hint, (40, y + 10), font_size=16, color=(160, 160, 170))

    def _render_turn_in(self, screen):
        quest = self.active_quest
        player_level = self.state_manager.player.level

        self.renderer.draw_text(screen, quest.title, (40, 90), color=COLOR_WHITE)
        self._draw_wrapped_text(screen, quest.turn_in_text, (40, 130), max_width=SCREEN_WIDTH - 80)

        scaled_exp = quest.get_scaled_exp_reward(player_level)
        reward_lines = [f"Reward: {scaled_exp} XP"]
        if scaled_exp != quest.reward_exp:
            # Real, visible confirmation that level scaling happened -
            # Kyle's spec that a big level gap should NOT read as "same
            # reward regardless of level" needs to be legible in the UI,
            # not just correct under the hood.
            reward_lines.append(f"(base {quest.reward_exp}, scaled for your level)")
        if quest.reward_gold:
            reward_lines.append(f"+ {coins(quest.reward_gold)}")
        if quest.gear_reward_gear_level is not None:
            reward_lines.append("+ choice of gear")
        for i, line in enumerate(reward_lines):
            self.renderer.draw_text(screen, line, (40, 260 + i * 26), color=COLOR_GOLD)

        if self.result_message:
            self.renderer.draw_text(screen, self.result_message, (40, 380), color=(120, 220, 140))

        self.renderer.draw_button(screen, self.turn_in_button, "Turn In")

    def _render_gear_choice(self, screen):
        quest = self.active_quest
        self.renderer.draw_text(screen, "Choose your reward:", (40, 90), color=COLOR_WHITE)

        for i, rect in enumerate(self.gear_choice_rects):
            if i >= len(quest.gear_choices):
                continue
            choice = quest.gear_choices[i]
            item = choice.item
            pygame.draw.rect(screen, (30, 30, 38), rect)
            pygame.draw.rect(screen, item.get_rarity_color(), rect, 2)
            self._draw_wrapped_text(screen, item.name, (rect.x + 10, rect.y + 10),
                                    max_width=rect.width - 20, color=item.get_rarity_color())
            # armor_type_label ("Dagger (Agi)") is a mechanical tag, not a
            # title - see the identical fix + rationale in
            # _render_reward_preview_row just above. Same demotion here:
            # moved below the item name, smaller and dimmer.
            self.renderer.draw_text(screen, choice.armor_type_label, (rect.x + 10, rect.y + 58),
                                    color=(130, 130, 140), font_size=13)
            y = rect.y + 90
            if item.armor_value:
                self.renderer.draw_text(screen, f"Armor: {item.armor_value}", (rect.x + 10, y), font_size=16)
                y += 22
            if getattr(item, "weapon_damage_max", None):
                self.renderer.draw_text(
                    screen, f"Damage: {item.weapon_damage_min}-{item.weapon_damage_max}",
                    (rect.x + 10, y), font_size=16)
                y += 22
            for stat, value in item.primary_stats.items():
                self.renderer.draw_text(screen, f"+{value} {stat.replace('_', ' ').title()}",
                                        (rect.x + 10, y), font_size=16)
                y += 22

            # Real flavor text (Kyle's weapon one-liners + any
            # hand-authored unique item flavor - see
            # data/items/weapon_flavor_text.json / build_unique_reward_set)
            # shown at the bottom of the card, muted so it reads as
            # flavor rather than another stat line. Was written but never
            # actually displayed anywhere until this pass.
            if getattr(item, "flavor_text", ""):
                self._draw_wrapped_text(
                    screen, item.flavor_text, (rect.x + 10, rect.bottom - 60),
                    max_width=rect.width - 20, color=(140, 140, 150), line_height=16)

        if self.result_message:
            self.renderer.draw_text(screen, self.result_message, (40, SCREEN_HEIGHT - 120), color=(120, 220, 140))

    def _draw_wrapped_text(self, screen, text, pos, max_width, color=COLOR_WHITE, line_height=26):
        """Simple word-wrap for dialog text - the renderer has no built-in
        multi-line text helper, and quest accept/turn-in lines run well
        past a single line at any reasonable font size."""
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
