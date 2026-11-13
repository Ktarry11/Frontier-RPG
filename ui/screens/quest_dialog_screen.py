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


_QUEST_ITEM_NAMES = None


def _quest_item_name(item_id):
    """Display name for a quest item id, or None.

    Quest objectives store an item_id ("tan_hex_fetish") while the item is
    really called "Hex Fetish" - printing the raw id slugified produced
    "Collect 5 tan hex fetishes" in the objectives block. The names live
    beside the drop tables in data/creatures/quest_drops.json, keyed by
    item_id, so they are read once and cached here rather than threading an
    item lookup through the UI.
    """
    global _QUEST_ITEM_NAMES
    if _QUEST_ITEM_NAMES is None:
        _QUEST_ITEM_NAMES = {}
        import json as _json
        from pathlib import Path as _Path
        root = _Path(__file__).resolve().parents[2]
        # The drop tables FIRST (setdefault keeps the first name found), then every quest file:
        # an item a quest HANDS you (grant_items) is named there and nowhere else, so every
        # "Deliver" objective was printing its id - "Deliver ab collapse log."
        sources = [root / "data/creatures/quest_drops.json"]
        sources += sorted((root / "data/quests").glob("*.json"))
        for path in sources:
            try:
                blob = _json.loads(path.read_text())
            except Exception:
                continue
            stack = [blob]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    if node.get("item_id") and node.get("name"):
                        _QUEST_ITEM_NAMES.setdefault(node["item_id"], node["name"])
                    stack.extend(node.values())
                elif isinstance(node, list):
                    stack.extend(node)
    name = _QUEST_ITEM_NAMES.get(item_id)
    if name:
        return name
    # A GATHER objective can name a gathered MATERIAL ("herb_bruiseweed") rather than a quest
    # drop, and that id lives in the materials table, not beside the drop tables. Without this
    # the objective printed the id with its underscores swapped for spaces: "herb bruiseweed".
    try:
        from world.gathering_manager import get_gathering_node_manager
        material = get_gathering_node_manager().make_material_instance(item_id)
        if material is not None and getattr(material, "name", None):
            _QUEST_ITEM_NAMES[item_id] = material.name
            return material.name
    except Exception:
        pass
    return None


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
        self.mode = None       # "menu" | "turn_in" | "offer" | "greeting" | "dialogue"
        self.active_quest = None
        # The pick list shown when this NPC has more than one thing to do.
        # menu_entries is [(kind, quest)] with kind "turn_in" or "offer";
        # came_from_menu drives the Back button, so drilling into a quest
        # and backing out returns to the list rather than the overworld.
        self.menu_entries = []
        self.menu_rects = []
        self.menu_visible = []
        self.menu_scroll = 0
        # Offer-panel prose scroll. The reward cards are pinned to the
        # bottom, so a quest whose text is longer than the space above
        # them scrolls rather than pushing the cards off the panel.
        self.offer_scroll = 0
        self.offer_max_scroll = 0
        self.menu_max_scroll = 0
        self.came_from_menu = False
        self.back_button = pygame.Rect(40, SCREEN_HEIGHT - 70, 150, 44)
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
        # A different quest starts at the top of its own text, or the
        # second quest on an NPC opens halfway down the first one's.
        self.offer_scroll = 0

        # FETCH / DELIVER progress is read off the bag; bring it up to date so a quest whose items the player
        # just collected (or was just handed on accept) is turn-in-ready the moment we look.
        player = getattr(self.state_manager, "player", None)
        if player is not None:
            self.quest_mgr.refresh_gather_progress(player)

        turn_ins = self.quest_mgr.get_turn_in_ready_quests(self.npc_id)
        offerable_now = self.quest_mgr.get_offerable_quests(self.npc_id)

        # A GIVER WITH SEVERAL QUESTS USED TO SHOW EXACTLY ONE. This method
        # took turn_ins[0] / offerable[0] and dropped the rest on the floor,
        # so a player had to accept, walk away, and re-open the dialog once
        # per quest to discover there was more. 263 of the game's 450 quest
        # givers offer more than one quest and the worst offer TWELVE, so
        # that is not an edge case - it is most of them.
        #
        # When there is more than one thing to do here, the screen now opens
        # on a pick list instead (Kyle, 6 Nov: "build a UI for when a quest
        # giver offers multiple quests so the player can choose"). Turn-ins
        # are listed above offers, because handing in finished work before
        # taking more is what a player expects and what WoW does.
        self.menu_entries = ([("turn_in", q) for q in turn_ins]
                             + [("offer", q) for q in offerable_now])
        if len(self.menu_entries) > 1:
            self.mode = "menu"
            self.active_quest = None
            self.came_from_menu = False
            return

        # Only one thing left here, so there is no list to go back to -
        # clear the flag or the Back button lingers and does nothing.
        self.came_from_menu = False

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

        # Wheel scrolling for the pick list. pygame sends the wheel as
        # MOUSEBUTTONDOWN buttons 4/5, so this has to run before the
        # button-4/5 events fall through to the click handlers below
        # and get treated as a click on whatever is under the cursor.
        if self.mode == "menu" and event.type == pygame.MOUSEBUTTONDOWN \
                and event.button in (4, 5):
            self.menu_scroll = max(
                0, min(self.menu_max_scroll,
                       self.menu_scroll + (-1 if event.button == 4 else 1)))
            return

        # Same for the offer panel's prose, which scrolls independently of
        # the pinned reward block below it.
        if self.mode == "offer" and event.type == pygame.MOUSEBUTTONDOWN \
                and event.button in (4, 5):
            self.offer_scroll = max(
                0, min(self.offer_max_scroll,
                       self.offer_scroll + (-40 if event.button == 4 else 40)))
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

        # Pick list first: clicking a row drills into that quest, and Back
        # returns here rather than to the overworld.
        if self.mode == "menu":
            for (kind, quest), rect in zip(self.menu_visible, self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.mode = kind
                    self.active_quest = quest
                    self.came_from_menu = True
                    self.gear_choice_stage = False
                    self.result_message = None
                    self.offer_scroll = 0
                    return
            return

        if self.came_from_menu and self.back_button.collidepoint(mouse_pos):
            self._return_to_menu()
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
    SERVICE_LABELS = {"revive": "Revive the Fallen", "inn": "Bind Hearthstone", "flight": "Fly", "riding": "Train Riding", "mounts": "Buy Mounts",
                      "train_class": "Train Skills", "train_prof": "Train Profession",
                      "set_exchange": "Exchange Set Gear"}

    def _offered(self):
        """The services on offer right now. An innkeeper also raises the dead - but only shows
        the button while somebody in the party is actually down.

        Kyle, 12 Nov 2026: "if the only healer is dead lets have it so people can res at an inn
        keeper. This will be more useful in starting game" - where nobody has a res spell yet.
        """
        out = list(self.services)
        if "inn" in out and self.state_manager.get_party().fallen_members():
            out.insert(out.index("inn"), "revive")
        return out

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
        entries = [(self.SERVICE_LABELS[s], s) for s in self._offered()
                   if s in self.SERVICE_LABELS]
        if self.is_vendor:
            entries.insert(0, ("Shop", "shop"))
        if self.is_banker:
            entries.append(("Bank", "bank"))
        if not entries:
            return []
        # A ROW ACROSS THE TOP RIGHT, beside the NPC's name. They used to be a column on the
        # left above the bottom row, which is exactly where a quest's Rewards line and its
        # reward cards are drawn - Kyle's screenshot of Quartermaster Horg had Shop sitting on
        # "Rewards". (Before that they sat on dialogue mode's Back button.) The header band is
        # the one strip of this screen no quest text is ever laid out in.
        w, h, gap = 150, 36, 8
        x = SCREEN_WIDTH - 40 - len(entries) * w - (len(entries) - 1) * gap
        y = self.SERVICE_ROW_Y
        out = []
        for label, action in entries:
            out.append((label, action, pygame.Rect(x, y, w, h)))
            x += w + gap
        return out

    SERVICE_ROW_Y = 28

    def _greeting_buttons(self):
        """[(label, action, rect)] - service buttons, then Shop for vendors, then Leave; centred in one row."""
        entries = [(self.SERVICE_LABELS[s], s) for s in self._offered() if s in self.SERVICE_LABELS]
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
        elif action == "revive":
            raised = sm.get_party().revive_at_inn()
            names = [m.name for m in raised]
            who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
            self.result_message = (f"{who} {'is' if len(names) == 1 else 'are'} back on "
                                   f"their feet, rested and whole.")
        elif action == "inn":
            zm = sm._live_zone_manager()
            zone = zm.current_zone
            travel.set_bind(zone.name, zm.player_x, zm.player_y, zone.name)
            self.result_message = f"Your hearthstone is now bound to {zone.name}."
        elif action in ("flight", "riding", "mounts", "train_class", "train_prof", "set_exchange"):
            screen = sm.states.get(GameState.TRAVEL)
            screen.open_service(action, self.npc)
            sm.transition_to(GameState.TRAVEL)

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((10, 10, 15))

        # NPC name banner
        self.renderer.draw_text(screen, self.npc.name, (40, 30), size="large", color=COLOR_GOLD)

        if self.mode == "menu":
            self._render_menu(screen)
        elif self.mode == "turn_in" and self.gear_choice_stage:
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

        # Back to the pick list, drawn only when there is a list to go back
        # to. Without it the only way out of a quest opened from the list
        # is Close, which drops the player to the overworld and makes them
        # walk back into the NPC to see the other quests.
        if self.came_from_menu and self.mode in ("offer", "turn_in", "dialogue"):
            self.renderer.draw_button(screen, self.back_button, "< Back")

        # Shop / Bank / services alongside the quest, in every non-greeting
        # mode. Drawn last so nothing a mode renderer draws can cover them.
        for label, _action, rect in self._side_service_buttons():
            self.renderer.draw_button(screen, rect, label)

    def _return_to_menu(self):
        """Back out of a quest to the pick list, recomputing it first.

        Recomputed rather than restored, because the list can have changed
        while the player was inside it - accepting a quest removes it from
        the offers, and turning one in can reveal the next link of a chain
        on the same NPC (the reason _refresh exists at all). _refresh falls
        through to a single-quest mode on its own when only one thing is
        left, so backing out of the last entry lands somewhere sensible
        instead of on an empty list.
        """
        self.came_from_menu = False
        self._refresh()

    def _render_menu(self, screen):
        """The pick list for an NPC with several quests.

        Modelled on WoW's gossip window: a line of greeting, then one row
        per quest, each marked with its state. A quest ready to hand in
        gets a gold "?" and a quest on offer a yellow "!", which is the
        marker players already read above an NPC's head, so the list needs
        no legend.
        """
        y = 84
        greeting = (getattr(self.npc, "greeting", "") or "").strip()
        if greeting:
            y = self._draw_wrapped_text(screen, greeting, (40, y),
                                        max_width=SCREEN_WIDTH - 80,
                                        color=(190, 186, 172))
            y += 14

        ready = sum(1 for kind, _ in self.menu_entries if kind == "turn_in")
        header = (f"{len(self.menu_entries)} things to discuss"
                  if not ready else
                  f"{len(self.menu_entries)} things to discuss "
                  f"({ready} ready to hand in)")
        self.renderer.draw_text(screen, header, (40, y), color=COLOR_GOLD,
                                font_size=18)
        y += 30

        # SCROLLED, because the longest list in the game is twelve entries
        # and twelve rows at 46px run off the bottom of a 720px screen -
        # the last two were drawn under the Close button and past the edge.
        ROW_H = 46
        bottom = SCREEN_HEIGHT - 90          # clear of Close / Back
        visible = max(1, (bottom - y) // ROW_H)
        total = len(self.menu_entries)
        self.menu_max_scroll = max(0, total - visible)
        self.menu_scroll = max(0, min(self.menu_scroll, self.menu_max_scroll))
        shown = self.menu_entries[self.menu_scroll:self.menu_scroll + visible]

        self.menu_rects = []
        self.menu_visible = shown
        player = getattr(self.state_manager, "player", None)
        for kind, quest in shown:
            rect = pygame.Rect(40, y, SCREEN_WIDTH - 420, 40)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(screen, (30, 30, 38) if hovered else (20, 20, 26), rect)
            pygame.draw.rect(screen, (90, 82, 60), rect, 1)

            mark, mark_col = ("?", (255, 214, 92)) if kind == "turn_in" else ("!", (240, 196, 48))
            self.renderer.draw_text(screen, mark, (rect.x + 12, rect.y + 8), color=mark_col)

            # Grey the title when the player cannot take it yet, so the
            # list never offers something that will be refused on click.
            too_low = (player is not None
                       and kind == "offer"
                       and getattr(player, "level", 1) < getattr(quest, "level_min", 1))
            title_col = (150, 150, 150) if too_low else COLOR_WHITE
            self.renderer.draw_text(screen, quest.title, (rect.x + 36, rect.y + 8),
                                    color=title_col)

            right = f"lvl {quest.level_min}" if kind == "offer" else "Complete"
            right_col = (200, 90, 90) if too_low else (
                (120, 220, 120) if kind == "turn_in" else (160, 160, 160))
            self.renderer.draw_text(screen, right,
                                    (rect.right - 90, rect.y + 10),
                                    color=right_col, font_size=16)

            self.menu_rects.append(rect)
            y += ROW_H

        if self.menu_max_scroll:
            self.renderer.draw_text(
                screen,
                f"{self.menu_scroll + 1}-{self.menu_scroll + len(shown)} of {total}"
                "   (scroll)",
                (40, y + 4), color=(140, 140, 140), font_size=16)

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

        # LAID OUT BY FLOW, NOT BY FIXED Y. Every section used to be nailed
        # to a constant - accept_text at 130, description at 260, the level
        # line at 380 - so a quest whose prose ran long wrote straight
        # THROUGH the next section. Our best-written quest (Durotar's The
        # Stranded Garrison, 797 characters) already collided with "Requires
        # level 6" before this change, which is what a screenshot showed
        # when Kyle asked for the quests to read like real WoW quests.
        # Sections now stack from the previous one's measured bottom.
        #
        # ONE BODY, NOT TWO. The offer used to print accept_text AND
        # description, which is the same NPC saying the same thing twice in
        # two different voices. WoW's offer window shows a single body, then
        # Quest Objectives, then Rewards - which is the shape of every
        # screenshot Kyle sent. description is the body here because it is
        # the longer, authored prose; accept_text still has its own job on
        # the accept-confirmation path below.
        BODY_W = SCREEN_WIDTH - 80

        # REWARDS ARE PINNED TO THE BOTTOM AND THE PROSE SCROLLS ABOVE
        # THEM. Flowing everything top-down meant a long quest pushed the
        # gear cards off the panel, and the previous attempt at handling
        # that - print the item NAMES on one line instead - threw away the
        # whole reason the preview exists (Kyle: "let's have the rewards
        # previewed when the quest is given... so we can see if we even
        # care about the quest", and then "it doesn't show items? We need
        # to have items shown"). The cards, with their stats, are the
        # point. So the reward block gets its space reserved first and the
        # text region above takes whatever is left, scrolling when the
        # prose is longer than that.
        gear_choices = None
        if quest.gear_reward_gear_level is not None:
            from entities.loot_generator import LootGenerator
            gear_choices = quest.get_gear_choices(
                LootGenerator(), self.state_manager.player.char_class)
        CARD_H = 130
        TEXT_TOP = 84

        # WHAT TO DO AND WHAT YOU GET ARE BOTH PINNED. Only the flavour
        # scrolls. Putting Quest Objectives in the scrolling region meant
        # a long quest hid the one block that tells the player what the
        # quest actually wants, which is the opposite of why that block
        # was added.
        #
        # Both the pinned block and the prose are MEASURED by running
        # their own drawing code against an empty clip, so a measurement
        # can never disagree with the render.
        prev_clip = screen.get_clip()
        screen.set_clip(pygame.Rect(0, 0, 0, 0))
        pinned_h = self._draw_offer_pinned(screen, quest, available, 0,
                                           BODY_W, gear_choices, CARD_H)
        screen.set_clip(prev_clip)
        reward_top = max(TEXT_TOP + 120, self.accept_button.y - 24 - pinned_h)

        screen.set_clip(pygame.Rect(0, 0, 0, 0))
        content_h = self._draw_offer_text(screen, quest, TEXT_TOP, BODY_W) - TEXT_TOP
        screen.set_clip(prev_clip)

        view_h = max(80, reward_top - TEXT_TOP - 8)
        self.offer_max_scroll = max(0, content_h - view_h)
        self.offer_scroll = max(0, min(self.offer_scroll, self.offer_max_scroll))

        screen.set_clip(pygame.Rect(0, TEXT_TOP - 4, SCREEN_WIDTH, view_h + 8))
        self._draw_offer_text(screen, quest, TEXT_TOP - self.offer_scroll, BODY_W)
        screen.set_clip(prev_clip)

        if self.offer_max_scroll:
            self.renderer.draw_text(
                screen, "scroll for more" if self.offer_scroll < self.offer_max_scroll
                else "scroll up", (SCREEN_WIDTH - 200, reward_top - 22),
                color=(130, 126, 114), font_size=14)

        self._offer_flow_y = reward_top
        self._draw_offer_pinned(screen, quest, available, reward_top,
                                BODY_W, gear_choices, CARD_H)

    def _draw_offer_pinned(self, screen, quest, available, y, BODY_W,
                           gear_choices, CARD_H):
        """Quest Objectives, the level line and the whole reward block -
        the parts a player is deciding on, pinned to the bottom of the
        panel so prose length can never push them off it. Returns its own
        height when called from y=0, which is how the pin point is found."""
        top = y
        obj_lines = self._objective_lines(quest)
        if obj_lines:
            self.renderer.draw_text(screen, "Quest Objectives", (40, y),
                                    color=COLOR_GOLD, font_size=18)
            y += 26
            for line in obj_lines:
                y = self._draw_wrapped_text(screen, line, (56, y),
                                            max_width=BODY_W - 16,
                                            color=(190, 190, 190),
                                            line_height=22)
            y += 8

        level_text = f"Requires level {quest.level_min}"
        if quest.level_max:
            level_text += f" (recommended through {quest.level_max})"
        level_color = COLOR_WHITE if available else (200, 90, 90)
        self.renderer.draw_text(screen, level_text, (40, y), color=level_color)
        y += 28

        y = self._render_offer_rewards(screen, quest, gear_choices, y,
                                       CARD_H, available)
        return y - top

    def _draw_offer_text(self, screen, quest, y, BODY_W):
        """Title and prose - the only part that scrolls. Split out of
        _render_offer so the exact same code both measures and draws."""
        self.renderer.draw_text(screen, quest.title, (40, y), color=COLOR_GOLD)
        y += 34

        # WHICH FIELD IS THE BODY DEPENDS ON THE ZONE, and getting this
        # wrong silently guts about a third of the game's quests.
        #
        # Two authoring conventions exist side by side:
        #   OLDER zones (Valley of Trials, Durotar, Tirisfal, Silverpine,
        #   the Barrens hubs) put the prose in `description` and a short
        #   NPC line in `accept_text`.
        #   NEWER zones (Lashings, Glittervein, Abyssal Sands, Tanaris,
        #   Stranglethorn, Underdark, Hillsbrad) put a ONE-LINE TEASER in
        #   `description` - "The nets are not for fish." - and the real
        #   multi-paragraph speech in `accept_text`.
        #
        # Rendering `description` as the body made Lashings, some of the
        # best writing in the game, show up as a single sentence. Taking
        # the longer of the two covers both conventions without rewriting
        # 1087 quests to a single schema, and the short one is kept above
        # it as a framing line when it genuinely differs.
        desc = (quest.description or "").strip()
        speech = (quest.accept_text or "").strip()
        # The lead line is only drawn when `description` is the TEASER -
        # i.e. when accept_text won and is the body. In the other
        # convention accept_text is the short line the NPC says as you
        # take the quest ("Take the west road down to the Vale"), which is
        # a different beat and reads as a duplicate if it is also printed
        # above the body.
        # A THIRD CASE the longer-wins rule got wrong, and it was eating
        # whole speeches. Arathi, both southern Stranglethorns, Southern
        # Needles and Aspen write a real framing PARAGRAPH in `description`
        # (300-470 chars) as well as a real speech in `accept_text`
        # (270-400). Longer-wins picked the framing as the body, and the
        # 160-character cap below then discarded the NPC's own words
        # entirely - 56 quests across those five zones showed the player
        # narration and never printed what the quest giver actually said.
        #
        # So pick by ROLE rather than by length:
        #   both long            -> description is framing, accept_text is
        #                           the speech (the Arathi case)
        #   accept_text longer   -> description is a teaser lead
        #   otherwise            -> description IS the speech and
        #                           accept_text is the short parting
        #                           direction, drawn under it
        # and never drop a field for being too long to be a lead.
        # In the third convention `description` IS the speech and
        # accept_text is a short parting direction, which already has its
        # own job on the accept-confirmation path - printing it here too
        # reads as the NPC repeating himself and pushes the body past the
        # reward row.
        LONG = 200
        if len(speech) > len(desc) or (len(desc) > LONG and len(speech) > LONG):
            lead, body = desc, speech
        else:
            lead, body = "", desc
        if lead and lead != body:
            y = self._draw_wrapped_text(screen, lead, (40, y), max_width=BODY_W,
                                        color=(150, 146, 132), line_height=24)
            y += 8
        y = self._draw_wrapped_text(screen, body, (40, y), max_width=BODY_W,
                                    color=(214, 206, 184))
        y += 10
        return y

    def _render_offer_rewards(self, screen, quest, gear_choices, reward_y,
                              CARD_H, available):
        """The bottom-pinned reward block: XP/gold/rep, then the real gear
        cards. Never clipped and never scrolled - this is the part the
        player is deciding on."""
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
        self.renderer.draw_text(screen, "Rewards", (40, reward_y),
                                color=COLOR_GOLD, font_size=18)
        reward_y += 24
        self.renderer.draw_text(screen, "   ".join(reward_lines), (56, reward_y),
                                color=COLOR_GOLD)
        reward_y += 28

        # Real reward preview instead of a vague "+ choice of gear" line
        # (Kyle: "let's have the rewards previewed when the quest is
        # given, rather than 'choice of reward' as this will let us see
        # if we even care about the quest lol"). Built once and cached
        # on the Quest itself via get_gear_choices, so viewing the
        # preview doesn't roll anything different from what turn-in
        # will actually offer - same fixed set, just shown earlier.
        # The cards always draw, because space for them was reserved
        # before any prose was laid out.
        if gear_choices:
            self._render_reward_preview_row(screen, gear_choices, y=reward_y)
            reward_y += CARD_H

        # What this quest hands you / where it is handed in (deliver and "report to" quests).
        info_y = reward_y
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
                info_y += 22
        if self.result_message:
            self.renderer.draw_text(screen, self.result_message, (40, SCREEN_HEIGHT - 130), color=(220, 120, 110))

        if available:
            self.renderer.draw_button(screen, self.accept_button, "Accept")
        else:
            self.renderer.draw_button(screen, self.accept_button, "Accept", color=(50, 50, 50))
            self.renderer.draw_text(screen, "Too low level", (self.accept_button.x, self.accept_button.y - 24),
                                    color=(200, 90, 90), font_size=16)
        self.renderer.draw_button(screen, self.decline_button, "Not Now")
        return info_y

    @staticmethod
    def _kind_line(choice):
        """The line under a reward's name: what KIND of thing it is.

        A hand-authored reward's label defaults to its own name, so the card read
        "Longwalk Greaves / Longwalk Greaves" - Kyle, 10 Nov: "reward cards show name twice."
        When the label is just the name again, say what the item is instead.
        """
        item = choice.item
        label = getattr(choice, "armor_type_label", "") or ""
        if label and label != item.name:
            return label
        slot = (item.slot or "").rstrip("0123456789").replace("_", " ").title()
        if item.weapon_type:
            return item.weapon_type.replace("_2h", " (Two-Hand)").replace("_1h", " (One-Hand)").replace("_", " ").title()
        if item.armor_type and item.armor_type not in ("none", "bag"):
            return f"{item.armor_type.title()} {slot}"
        return slot

    @staticmethod
    def _stat_lines(item, short=False):
        """Every stat on the item - secondary ones too, which the cards used to leave out, so a
        healer's reward showed its Stamina and not the Healing Power that made it a healer's."""
        from combat.status_effects import StatusEffectMixin
        out = []
        for group in (item.primary_stats, item.secondary_stats):
            for stat, value in group.items():
                if not isinstance(value, (int, float)) or not value:
                    continue
                name = StatusEffectMixin.STAT_LABELS.get(stat, stat.replace("_", " ").title())
                if short and stat in item.primary_stats:
                    name = name[:3]
                out.append(f"+{value} {name}")
        return out

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
            self.renderer.draw_text(screen, self._kind_line(choice), (rect.x + 6, rect.y + 46),
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
            # Every stat, packed two to a line where they fit, down to the foot of the card.
            font = self.renderer._get_font(font_size=13)
            line = ""
            packed = []
            for text in self._stat_lines(item, short=True):
                cand = f"{line}  {text}" if line else text
                if line and font.size(cand)[0] > card_w - 12:
                    packed.append(line)
                    line = text
                else:
                    line = cand
            if line:
                packed.append(line)
            for text in packed:
                if stat_y + 15 > rect.bottom - 2:
                    break
                self.renderer.draw_text(screen, text, (rect.x + 6, stat_y), font_size=13)
                stat_y += 16

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
        from combat.difficulty import party_average_level
        quest = self.active_quest
        # Party average, matching what turn_in will actually pay. Reading
        # player.level here would show one number and award another.
        player_level = party_average_level(
            self.state_manager.get_party(),
            fallback=self.state_manager.player.level)

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
            self.renderer.draw_text(screen, self._kind_line(choice), (rect.x + 10, rect.y + 58),
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
            for text in self._stat_lines(item):
                self.renderer.draw_text(screen, text, (rect.x + 10, y), font_size=16)
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

    def _objective_lines(self, quest):
        """The "Quest Objectives" block, in the player's words.

        WoW states the task plainly under the prose ("Kill 7 Young
        Nightsabers and 4 Young Thistle Boars and return to Conservator
        Ilthalaine"), and this screen had NO objectives section at all -
        the player read a paragraph of flavour and was never told what the
        quest actually wanted. Every screenshot Kyle sent has this block.

        Built from the objective data rather than authored per quest, so
        it cannot drift from what the quest actually tracks - and so 1087
        quests do not each need a hand-written sentence that could lie.
        """
        def field(obj, *names, default=None):
            """Objectives arrive as Objective instances in the live game and
            as raw dicts from some loaders, and the attribute is
            `objective_type` on one and `type` on the other. Reading only
            the attribute form produced "None: the objective." for every
            quest."""
            for n in names:
                if isinstance(obj, dict):
                    if n in obj:
                        return obj[n]
                else:
                    v = getattr(obj, n, None)
                    if v is not None:
                        return v
            return default

        def plural(name, n):
            """"Slay 8 Stranded Marine" reads like a typo. Crude on
            purpose - creature names here are plain English nouns, and a
            real pluraliser would be a dependency for one line of UI."""
            if n <= 1 or not name:
                return name
            low = name.lower()
            if low.endswith(("s", "x", "z", "ch", "sh")):
                return name + "es"
            if low.endswith("y") and len(name) > 1 and low[-2] not in "aeiou":
                return name[:-1] + "ies"
            if low.endswith("f"):
                return name[:-1] + "ves"
            return name + "s"

        out = []
        for obj in (quest.objectives or []):
            kind = field(obj, "objective_type", "type")
            # IN THE LIVE GAME THIS IS AN ENUM, NOT A STRING. Every branch below compares
            # against "kill", "fetch" and so on, so with a real QuestObjective none of them
            # ever matched and every objective in the game fell through to the generic line -
            # which printed the enum itself: "Objectivetype.Kill Boss: Void Handmaiden."
            # (Kyle's screenshots, 10 Nov). The branches were only ever exercised with dicts.
            kind = getattr(kind, "value", kind)
            target = field(obj, "target")
            count = field(obj, "count", default=1) or 1
            alts = list(field(obj, "alt_targets", default=[]) or [])
            # Item objectives carry an ITEM ID, not a display name, so
            # "Collect 5 tan hex fetishes" was shown where the item is
            # really called "Hex Fetish". Creature objectives already carry
            # the display name, so only the item kinds need resolving.
            name = _quest_item_name(target) if kind in ("fetch", "gather", "deliver") \
                else (str(target).replace("_", " ") if target else "the objective")
            if not name:
                name = str(target).replace("_", " ") if target else "the objective"
            if kind == "kill":
                shown = plural(name, count)
                who = shown if not alts else (
                    f"{shown} (or {', '.join(plural(a, count) for a in alts)})")
                out.append(f"Slay {count} {who}." if count > 1 else f"Slay {who}.")
            elif kind == "kill_boss":
                out.append(f"Defeat {name}.")
            elif kind in ("fetch", "gather"):
                out.append(f"Collect {count} {plural(name, count)}." if count > 1
                           else f"Collect {name}.")
            elif kind == "deliver":
                out.append(f"Deliver {name}.")
            elif kind == "craft":
                out.append(f"Craft {count} {name}." if count > 1 else f"Craft {name}.")
            elif kind == "explore":
                where = field(obj, "zone") or name
                # Zones are stored as ids ("northern_tanaris"); title-case
                # them so the line reads as a place, not a database key.
                pretty = str(where).replace("_", " ").strip()
                if pretty and pretty == pretty.lower():
                    pretty = pretty.title()
                # A NAMED PLACE, when the quest has one. Almost every explore objective is a
                # spot inside a zone, and the line named the zone: "Scout Durotar." for a quest
                # given IN Durotar about one den (playtest, 12 Nov: "quest text on Scouting the
                # Prowler Den is messed up").
                spot = field(obj, "label")
                if spot:
                    out.append(f"Find {spot}.")
                elif field(obj, "target_x") is not None:
                    out.append(f"Find the place described, in {pretty}.")
                else:
                    out.append(f"Scout {pretty}.")
            elif kind == "dialogue":
                # EVERY dialogue objective in the game (50 of them) is
                # stored with no target - the conversation is with the
                # quest giver, so the data never bothered to name him.
                # The generic fallback therefore rendered the nonsense
                # line "Speak with the objective." on all 50. Name the
                # NPC whose panel this is instead.
                who = name
                if not target:
                    who = (getattr(getattr(self, "npc", None), "name", None)
                           or "the quest giver")
                out.append(f"Speak with {who}.")
            elif kind == "story":
                # No condition to state - it completes on accept or by a scripted event.
                continue
            else:
                out.append(f"{str(kind).replace('_', ' ').title()}: {name}.")
        return out

    def _draw_wrapped_text(self, screen, text, pos, max_width, color=COLOR_WHITE, line_height=26):
        """Simple word-wrap for dialog text - the renderer has no built-in
        multi-line text helper, and quest accept/turn-in lines run well
        past a single line at any reasonable font size."""
        if not text:
            return pos[1]
        # SPLIT ON NEWLINES FIRST. draw_text draws a single line, so an
        # embedded "\n" came out as missing-glyph boxes in the middle of a
        # sentence - visible in Tanaris as "where it all goes.<box><box>
        # Nobody on the pan...". The greeting path already had this fix
        # (see _render_greeting); the body text never did, and quest prose
        # is exactly where paragraph breaks belong.
        lines = []
        for para in str(text).replace("\r\n", "\n").split("\n"):
            para = para.strip()
            if not para:
                lines.append("")      # keep the blank line between paragraphs
                continue
            current = ""
            for word in para.split(" "):
                test = f"{current} {word}".strip()
                if self.renderer.font_normal.size(test)[0] > max_width and current:
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
        # RETURNS THE BOTTOM so callers can stack the next section under
        # this one instead of guessing a constant. Every caller that does
        # not care can keep ignoring the return value.
        return y
