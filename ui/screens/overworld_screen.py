"""
Overworld screen. Tilemap-based exploration with camera follow.
"""
import pygame
import random
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT,
    COLOR_WHITE, COLOR_DARK_GRAY, COLOR_GREEN, COLOR_BLUE, COLOR_RED, COLOR_YELLOW, VIEWPORT_WIDTH, VIEWPORT_HEIGHT, VIEWPORT_X, VIEWPORT_Y
)
from core.game_states import GameState
from world.zone_manager import ZoneManager
from world import zone_levels
from ui.screens.base_screen import BaseScreen
from ui.tilemap_renderer import TilemapRenderer
from ui.camera import CameraManager

#: Show the "TEST: +5 Levels" button in the right-hand tab column (play-testing aid; set False to hide).
DEBUG_LEVEL_BUTTON = True


class OverworldScreen(BaseScreen):
    """Overworld with tilemap visualization and camera follow."""
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.zone_manager = ZoneManager()
        self.tilemap_renderer = TilemapRenderer()  # tile_size defaults to world.tile_textures.TILE_SIZE (32px) - one source of truth, see tools/tile_mapping/NOTES.md
        self.camera = CameraManager(viewport_width=VIEWPORT_WIDTH, viewport_height=VIEWPORT_HEIGHT)
        self.viewport_rect = pygame.Rect(VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT)

        # Transient on-screen notice (e.g. "X joins your party!", "Game saved.")
        self.recruit_message = None
        self.recruit_message_timer = 0.0
        self.recruit_message_color = (120, 240, 140)
        
        # Right-edge vertical tab column - replaces the old 3 flat top-row
        # buttons (Inventory/Character/Menu) per Kyle's mockup: one stacked
        # column covering every overworld action, each labeled with its
        # keybind so the redundant bottom hint-bar text isn't the only
        # place that information lives.
        self.tab_column_x = SCREEN_WIDTH - 190
        self.tab_column_y = 20
        self.tab_w = 170
        self.tab_h = 48
        self.tab_gap = 8
        self.tab_rects = {}  # action -> rect, built in render()
        
        # Encounter toggle
        self.encounters_enabled = True

        # Cast is now a full-screen menu (GameState.CAST, see
        # cast_screen.py) opened via the "Cast (N)" tab or the N key -
        # no panel instance lives on this screen any more.
        
        # Continuous movement tracking (WSAD)
        self.keys_pressed = {
            'W': False,  # Up
            'S': False,  # Down
            'A': False,  # Left
            'D': False,  # Right
        }
        self.movement_cooldown = 0.0  # Cooldown between tile movements

        # Real seconds since the player's last completed tile step - the
        # "standing still" signal for tick_out_of_combat_regen, DISTINCT
        # from movement_cooldown (which is tuned for ~100ms tile-step
        # throttling, not a genuine standing-still detector - using it
        # directly would make regen flicker between rates constantly
        # during ordinary walking). Starts high so a fresh overworld
        # entry counts as "standing still" until the player actually
        # takes a step, matching how they'd have been stationary while
        # the previous screen was open.
        self.seconds_since_last_move = 999.0

        # THE TELEPORT MENU. Kyle, 13 Nov 2026: "change that 'stuck' option into a fast teleport.
        # Basically you open it and it lets me teleport to any town. So I don't need to run. Make
        # it a separate menu that replaces the stuck. Remove the hotkey from it." It was an
        # Unstuck button that only went to Razor Hill, on U. Now a button with no hotkey that
        # opens a list of every town with an inn (world/fast_travel.py).
        self.teleport_menu_open = False
        self.teleport_rects = []          # [(rect, destination)] built each frame while open
        self.teleport_close_rect = None
    
    def handle_event(self, event):
        """Handle input."""
        # The teleport menu takes over ALL input while it is open, so a click on a town can never
        # also be a movement key or a tab click underneath it.
        if self.teleport_menu_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, dest in self.teleport_rects:
                    if rect.collidepoint(event.pos):
                        self._teleport_to(dest)
                        break
                else:
                    if self.teleport_close_rect is None or self.teleport_close_rect.collidepoint(event.pos):
                        self.teleport_menu_open = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.teleport_menu_open = False
            return

        if event.type == pygame.KEYDOWN:
            # Toggle encounters with E key
            if event.key == pygame.K_e:
                self.encounters_enabled = not self.encounters_enabled
            
            # WSAD for continuous movement
            if event.key == pygame.K_w:
                self.keys_pressed['W'] = True
            elif event.key == pygame.K_s:
                self.keys_pressed['S'] = True
            elif event.key == pygame.K_a:
                self.keys_pressed['A'] = True
            elif event.key == pygame.K_d:
                self.keys_pressed['D'] = True
            
            # Open the zone map. Zones run up to 200x160 tiles against a
            # ~40x22 tile viewport, so without this there is no way to see a
            # zone's shape or find its exits.
            if event.key == pygame.K_m:
                # Opening the map hands event handling to MapScreen entirely,
                # so any WSAD key held down right now will never get its
                # KEYUP delivered here - it was landing back in OVERWORLD
                # still marked "held" and walking the player with zero input
                # the instant the map closed. Release everything on open.
                for k in self.keys_pressed:
                    self.keys_pressed[k] = False
                self.state_manager.zone_manager = self.zone_manager
                self.state_manager.transition_to(GameState.MAP)
                return

            # Inventory / character sheet keybinds. Matches WoW's real
            # convention now: B opens bags, not I - I used to be inventory
            # here, which is backwards from what anyone with WoW muscle
            # memory would expect (and part of why the old "B: Cast"
            # binding was never found either - B already meant something
            # else in the player's head, just not the right something).
            if event.key == pygame.K_b:
                self._open_inventory()
                return
            if event.key == pygame.K_c:
                self.state_manager.transition_to(GameState.CHARACTER_SHEET)
                return

            # Party management. The hint line advertised "P: Party" long
            # before there was a screen or a handler behind it.
            if event.key == pygame.K_p:
                self.state_manager.transition_to(GameState.PARTY)
                return

            # Quest Journal - was a dead placeholder tab ("L" advertised
            # since early on with no screen behind it, see
            # _render_tab_column's old disabled-quest-tab comment) until
            # the real quest system landed.
            if event.key == pygame.K_l:
                self.state_manager.transition_to(GameState.QUEST_JOURNAL)
                return

            # Professions - Herbalism/Mining skill overview (Gathering
            # Phase 1). Bound for real, unlike Skills' still-dangling "(J)"
            # label above (see the Quest Journal comment right above this
            # one for the exact failure mode - a tab advertising a key
            # with nothing behind it) - not fixing that pre-existing gap
            # here since Kyle didn't ask for it, but not repeating it for
            # a brand new tab either.
            if event.key == pygame.K_k:
                self.state_manager.transition_to(GameState.PROFESSIONS)
                return

                return

            # Cast screen - N opens the full-screen buff/heal menu (see
            # cast_screen.py; replaced the old collapsible cast_panel
            # sidebar, which was too short - 190px, ~2-3 visible rows even
            # with scrolling - for any class with more than a handful of
            # out-of-combat spells). Release held WSAD keys on open, same
            # reasoning as the Map transition above - a key held down when
            # the screen opens would otherwise never get its KEYUP
            # delivered here while the new screen owns input.
            if event.key == pygame.K_n:
                for k in self.keys_pressed:
                    self.keys_pressed[k] = False
                cast_screen = self.state_manager.states.get(GameState.CAST)
                if cast_screen is not None:
                    cast_screen.set_subject(return_state=GameState.OVERWORLD)
                self.state_manager.transition_to(GameState.CAST)
                return

            # Pet summon screen - Hunter (tame) and Warlock (summon) only.
            # Non-pet classes get a friendly no-op rather than silently
            # doing nothing, since a keybind that does nothing with zero
            # feedback looks like a bug rather than "not applicable to you".
            if event.key == pygame.K_g:
                target_char = self.state_manager.player
                if target_char.char_class in ("Hunter", "Warlock"):
                    self.state_manager.states[GameState.PET].character = target_char
                    self.state_manager.transition_to(GameState.PET)
                elif target_char.char_class == "Shaman":
                    self.state_manager.states[GameState.TOTEM].character = target_char
                    self.state_manager.transition_to(GameState.TOTEM)
                else:
                    self._notify(f"{target_char.char_class}s cannot summon pets or totems.", (240, 140, 140))
                return

            # Shapeshifting is now a real castable ability (see
            # effect_type="shapeshift" in combat/abilities.py) - Bear Form,
            # Spider Form, etc. are cast from the hotbar/spellbook like any
            # other spell, exactly like Kyle asked. The standalone
            # form_screen.py menu + this H-keybind are retired; casting a
            # shapeshift ability calls Character.shift_form() the same way
            # form_screen.py used to, just through the normal ability-use
            # path instead of a separate screen.

            # Earthen Guardian toggle (Shaman Tank) - see guardian_screen.py.
            # T for "Tank/sTance" - G/H/N already taken by pets/forms/cast.
            if event.key == pygame.K_t:
                target_char = self.state_manager.player
                if target_char.char_class == "Shaman":
                    self.state_manager.states[GameState.GUARDIAN].character = target_char
                    self.state_manager.transition_to(GameState.GUARDIAN)
                else:
                    self._notify(f"{target_char.char_class}s cannot use Earthen Guardian.", (240, 140, 140))
                return

            # R = ride/dismount, H = hearthstone (world/travel_manager.py).
            if event.key == pygame.K_r:
                self._toggle_mount()
                return
            if event.key == pygame.K_h:
                self._use_hearth()
                return
            if event.key == pygame.K_f:
                self._rest("meal")
                return
            if event.key == pygame.K_q:
                self._rest("drink")
                return

            # F10: the Testing menu (ui/screens/testing_screen.py), test only
            if event.key == pygame.K_F10 and DEBUG_LEVEL_BUTTON:
                self._open_testing()
                return

            # F5 quicksave. Until now the game saved exactly once, at
            # character creation, and never again - so a recruited party,
            # every level gained and all loot found was lost on exit.
            if event.key == pygame.K_F5:
                if self.state_manager.save_game():
                    self._notify("Game saved.", (140, 240, 160))
                elif self.state_manager.needs_save_slot:
                    # Not a failure - the game is refusing to guess which of
                    # 15 slots this character belongs in. Saying "Save
                    # failed" here would be both wrong and alarming.
                    self._notify("No save slot chosen - pick one from the menu (ESC).",
                                 (240, 210, 140))
                else:
                    self._notify("Save failed.", (240, 140, 140))
                return

            # Check for interaction (spacebar) - vendor NPC, recruit,
            # ambient flavor NPC, gathering node, chest, or portal
            if event.key == pygame.K_SPACE:
                # Vendor, then recruitable companion, then ambient flavor
                # NPC, then gathering node, then forge, then chest, then
                # portal. All six live on interaction tiles, so order
                # only matters where two could occupy the same tile -
                # which they never should. Chest sits after forge/before
                # portal here for the same reason gathering_node does:
                # it's an instant one-shot action, not a screen
                # transition, so it's grouped with the other "resolve
                # immediately" interactions rather than the dialog-based
                # ones above it.
                vendor = self.zone_manager.get_vendor_at_location()
                recruit = None if vendor else self.zone_manager.get_recruit_at_location()
                ambient_npc = None if (vendor or recruit) else self.zone_manager.get_ambient_npc_at_location()
                gathering_node = None if (vendor or recruit or ambient_npc) else self.zone_manager.get_gathering_node_at_location()
                forge = None if (vendor or recruit or ambient_npc or gathering_node) else self.zone_manager.get_forge_at_location()
                sawmill = None if (vendor or recruit or ambient_npc or gathering_node or forge) else self.zone_manager.get_sawmill_at_location()
                chest = None if (vendor or recruit or ambient_npc or gathering_node or forge or sawmill) else self.zone_manager.get_chest_at_location()

                if sawmill:
                    professions_screen = self.state_manager.states.get(GameState.PROFESSIONS)
                    if professions_screen is not None:
                        professions_screen.set_subject(None, return_state=GameState.OVERWORLD)
                        professions_screen.active_tab = "sawmill"
                    self.state_manager.transition_to(GameState.PROFESSIONS)
                elif forge:
                    # Walking onto a Forge and pressing space jumps
                    # straight to the Professions screen's Smelting tab -
                    # same "the interaction IS the shortcut to the
                    # relevant screen" pattern as a vendor opening the
                    # shop dialog, rather than making the player
                    # separately walk to the Forge AND remember to press
                    # K afterward.
                    professions_screen = self.state_manager.states.get(GameState.PROFESSIONS)
                    if professions_screen is not None:
                        professions_screen.set_subject(None, return_state=GameState.OVERWORLD)
                        professions_screen.active_tab = "smelting"
                    self.state_manager.transition_to(GameState.PROFESSIONS)
                elif gathering_node:
                    # Gathering is instant - no dialog screen, unlike NPCs
                    # which always talk first. Walk up, press space, get
                    # the material. Matches WoW's "no cast bar on basic
                    # gathering" feel closely enough for Phase 1; a real
                    # cast-time/interrupt system can come later if Kyle
                    # wants it.
                    if getattr(gathering_node, "pool_tile", None):
                        self._start_cast(gathering_node)
                    else:
                        self._gather_node(gathering_node)
                elif chest:
                    # Also instant, same reasoning as gathering nodes -
                    # no cast bar, no confirm dialog, walk up and press
                    # space.
                    self._open_chest(chest)
                elif vendor:
                    # Every vendor talks first, same as any other NPC -
                    # Kyle's call: a shopkeeper should greet the player
                    # and let them choose Shop/Leave, not skip straight
                    # to the shop screen just because they have nothing
                    # quest-related today. QuestDialogScreen's greeting
                    # mode renders those two buttons for vendor NPCs (see
                    # its is_vendor check) instead of a lone Close button.
                    self.state_manager.transition_to(GameState.QUEST_DIALOG, current_quest_npc=vendor)
                elif recruit:
                    self.state_manager.transition_to(GameState.RECRUIT_DIALOG, current_recruit_npc=recruit)
                elif ambient_npc:
                    self.state_manager.transition_to(GameState.QUEST_DIALOG, current_quest_npc=ambient_npc)
                else:
                    # Fall back to portal if nothing else is here
                    self.zone_manager.try_use_portal()
        
        if event.type == pygame.KEYUP:
            # Release keys for continuous movement
            if event.key == pygame.K_w:
                self.keys_pressed['W'] = False
            elif event.key == pygame.K_s:
                self.keys_pressed['S'] = False
            elif event.key == pygame.K_a:
                self.keys_pressed['A'] = False
            elif event.key == pygame.K_d:
                self.keys_pressed['D'] = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if getattr(self, "mount_button_rect", None) and self.mount_button_rect.collidepoint(mouse_pos):
                self._toggle_mount()
                return
            if getattr(self, "hearth_button_rect", None) and self.hearth_button_rect.collidepoint(mouse_pos):
                self._use_hearth()
                return
            if getattr(self, "eat_button_rect", None) and self.eat_button_rect.collidepoint(mouse_pos):
                self._rest("meal")
                return
            if getattr(self, "cast_button_rect", None) and self.cast_button_rect.collidepoint(mouse_pos):
                node = self.zone_manager.gathering_manager.fishing_node_near(
                    self.zone_manager.player_x, self.zone_manager.player_y)
                if node is not None:
                    self._start_cast(node)
                return
            if getattr(self, "drink_button_rect", None) and self.drink_button_rect.collidepoint(mouse_pos):
                self._rest("drink")
                return
            self._handle_tab_click(mouse_pos)
    
    def _release_movement_keys(self):
        for k in self.keys_pressed:
            self.keys_pressed[k] = False

    def _toggle_mount(self):
        from world.travel_manager import get_travel_manager
        mounted, message = get_travel_manager().toggle_mount(self.zone_manager.is_in_cave())
        self._notify(message, (140, 220, 160) if mounted or message == "You dismount." else (240, 140, 140))

    def _use_hearth(self):
        """Teleport to the innkeeper bind. Works anywhere off cooldown, caves and dungeons too."""
        from world.travel_manager import get_travel_manager
        travel = get_travel_manager()
        reason = travel.hearth_block_reason()
        if reason:
            self._notify(reason, (240, 140, 140))
            return
        bind = travel.use_hearth()
        self._release_movement_keys()
        if not self.zone_manager.transition_to_zone(bind["zone"], bind["x"], bind["y"],
                                                   via_portal=False):
            self._notify("Your hearth bind no longer exists. Visit an innkeeper.", (240, 140, 140))
            return
        self._notify(f"You return to {bind['name']}.", (140, 220, 160))

    # ---------------------------------------------------------------- eat / drink
    #
    # Kyle, 12 Nov: food and water on the combat hotbar "isnt useable in combat (correct) but
    # clicking it removes it... can we bind food/drink to another use tab somehow?"
    #
    # So: two buttons beside Mount and Hearth. One press sits the WHOLE party down - everyone
    # who is hurt eats, everyone short of mana drinks - each taking the best thing in the bags
    # they are high enough level for. With five companions, feeding them one at a time through
    # the inventory is the chore this replaces.

    def _rest_party(self):
        party = self.state_manager.get_party()
        seen, out = set(), []
        for m in [self.state_manager.player] + list(getattr(party, "members", []) or []):
            if m is not None and id(m) not in seen and getattr(m, "current_health", 1) > 0:
                seen.add(id(m))
                out.append(m)
        return out

    def _rest_stock(self, kind):
        """Meals or drinks in the bags, best first. Consumables all live in the player's list."""
        pool = getattr(self.state_manager.player, "consumables", None) or []
        stock = [c for c in pool if c.consumable_type == kind and c.quantity > 0]
        return sorted(stock, key=lambda c: -c.effect_value)

    @staticmethod
    def _rest_needs(member, kind):
        if any(k == kind for k, _n, _left in member.consumable_regen_active()):
            return False                                   # already eating / drinking
        if kind == "meal":
            return member.current_health < member.health
        return getattr(member, "mana", 0) > 0 and member.current_mana < member.mana

    def _rest(self, kind):
        """Everyone who needs it eats (kind='meal') or drinks (kind='drink')."""
        verb, noun, bar = (("eat", "food", "health") if kind == "meal" else ("drink", "water", "mana"))
        red, green = (240, 140, 140), (140, 220, 160)
        stock = self._rest_stock(kind)
        if not stock:
            self._notify(f"You have no {noun}.", red)
            return 0
        pool = self.state_manager.player.consumables
        fed, used = 0, {}
        needy = [m for m in self._rest_party() if self._rest_needs(m, kind)]
        if not needy:
            self._notify(f"Everyone is at full {bar}.", green)
            return 0
        for member in needy:
            choice = next((c for c in stock if c.quantity > 0 and c.can_use(member)), None)
            if choice is None:
                continue
            if choice.use(member):
                fed += 1
                used[choice.name] = used.get(choice.name, 0) + 1
                if choice.quantity <= 0 and choice in pool:
                    pool.remove(choice)
        if not fed:
            self._notify(f"Nothing in your bags that anyone can {verb} yet.", red)
            return 0
        what = ", ".join(f"{n} x{q}" if q > 1 else n for n, q in used.items())
        short = len(needy) - fed
        who = "You sit down" if len(self._rest_party()) == 1 else f"{fed} of you sit down"
        self._notify(f"{who} to {verb}: {what}." + (f" Not enough for {short} more." if short else ""), green)
        return fed

    def _render_travel_hud(self, screen):
        """Small ride/hearth strip under the viewport (click or press R / H)."""
        from world.travel_manager import get_travel_manager
        travel = get_travel_manager()
        mount = travel.current_mount()
        if travel.mounted and mount:
            mlabel, mcolor = f"Dismount (R): {mount['name']}", (60, 120, 70)
        elif mount:
            mlabel, mcolor = f"Mount (R): {mount['name']}", (30, 90, 110)
        else:
            mlabel, mcolor = "Mount (R): none", (50, 50, 56)
        self.mount_button_rect = pygame.Rect(20, 630, 235, 28)
        self.renderer.draw_button(screen, self.mount_button_rect, mlabel, color=mcolor)

        if travel.hearth_ready():
            hlabel, hcolor = f"Hearth (H): {travel.bind['name']}", (30, 90, 110)
        else:
            hlabel, hcolor = f"Hearth (H): {travel.hearth_steps_left} steps", (50, 50, 56)
        self.hearth_button_rect = pygame.Rect(265, 630, 235, 28)
        self.renderer.draw_button(screen, self.hearth_button_rect, hlabel, color=hcolor)

        # Eat / Drink: how many are in the bags, lit when someone needs it.
        party = self._rest_party()
        for kind, label, key, x, attr in (("meal", "Eat", "F", 510, "eat_button_rect"),
                                          ("drink", "Drink", "Q", 668, "drink_button_rect")):
            count = sum(c.quantity for c in self._rest_stock(kind))
            wanted = any(self._rest_needs(m, kind) for m in party)
            busy = any(k == kind for m in party for k, _n, _l in m.consumable_regen_active())
            color = (50, 50, 56) if not count else (60, 120, 70) if busy else (30, 90, 110) if wanted else (40, 60, 70)
            rect = pygame.Rect(x, 630, 150, 28)
            setattr(self, attr, rect)
            self.renderer.draw_button(screen, rect, f"{label} ({key}): {count}", color=color)

    def _handle_tab_click(self, mouse_pos):
        """Dispatch a click against the right-edge tab column built in
        _render_tab_column(). "quest" has no rect (disabled/unbuilt), so
        it's simply absent from self.tab_rects and can never match here."""
        for action, rect in self.tab_rects.items():
            if not rect.collidepoint(mouse_pos):
                continue
            if action == "character":
                self.state_manager.transition_to(GameState.CHARACTER_SHEET)
            elif action == "inventory":
                self._open_inventory()
            elif action == "cast":
                for k in self.keys_pressed:
                    self.keys_pressed[k] = False
                cast_screen = self.state_manager.states.get(GameState.CAST)
                if cast_screen is not None:
                    cast_screen.set_subject(return_state=GameState.OVERWORLD)
                self.state_manager.transition_to(GameState.CAST)
            elif action == "map":
                self.state_manager.transition_to(GameState.MAP)
            elif action == "party":
                self.state_manager.transition_to(GameState.PARTY)
            elif action == "quest":
                self.state_manager.transition_to(GameState.QUEST_JOURNAL)
            elif action == "skills":
                self.state_manager.transition_to(GameState.SKILLS)
            elif action == "professions":
                self.state_manager.transition_to(GameState.PROFESSIONS)
            elif action == "menu":
                self.state_manager.transition_to(GameState.MENU)
            elif action == "teleport":
                self._release_movement_keys()
                self.teleport_menu_open = True
            elif action == "test_levels":
                self._open_testing()
            return

    def _render_tab_column(self, screen):
        """Right-edge vertical tab stack - see mockup Kyle provided. Menu
        sits alone above the stack (not part of the blue column in the
        mockup); everything else is one consistent labeled tab."""
        self.tab_rects = {}

        menu_rect = pygame.Rect(self.tab_column_x, self.tab_column_y, self.tab_w, 40)
        self.renderer.draw_button(screen, menu_rect, "Menu")
        self.tab_rects["menu"] = menu_rect

        entries = [
            ("character", "Character (C)"),
            ("inventory", "Inventory (B)"),
            ("cast", "Cast (N)"),
            ("map", "Map (M)"),
            ("party", "Party (P)"),
            ("quest", "Quest Journal (L)"),
            ("skills", "Skills (J)"),
            ("professions", "Professions (K)"),
        ]

        y = menu_rect.bottom + 14
        tab_blue = (30, 90, 110)
        for action, label in entries:
            rect = pygame.Rect(self.tab_column_x, y, self.tab_w, self.tab_h)
            # No "active" highlight needed any more - Cast (like Map,
            # Party, Inventory, and now Quest Journal) is a real
            # full-screen transition, not an overlay that can be open
            # while this tab column is still visible underneath it.
            self.renderer.draw_button(screen, rect, label, color=tab_blue)
            self.tab_rects[action] = rect
            y += self.tab_h + self.tab_gap

        # Teleport sits apart from the main action stack (a gap below, its own colour): it is
        # a convenience for getting around, not a screen. No hotkey, on purpose.
        y += self.tab_gap
        teleport_rect = pygame.Rect(self.tab_column_x, y, self.tab_w, self.tab_h)
        self.renderer.draw_button(screen, teleport_rect, "Teleport", color=(70, 50, 110))
        self.tab_rects["teleport"] = teleport_rect

        # TEST BUTTON (Kyle): +5 levels for the whole party, so every zone can be
        # play-tested without grinding. Flip DEBUG_LEVEL_BUTTON off before release.
        if DEBUG_LEVEL_BUTTON:
            y += self.tab_h + self.tab_gap
            test_rect = pygame.Rect(self.tab_column_x, y, self.tab_w, self.tab_h)
            # the Testing menu (Kyle, 14 Nov 2026): travel, recruits, gold and levels,
            # professions, materials. +5 levels lives on in its Gold & Levels tab.
            self.renderer.draw_button(screen, test_rect, "TEST (F10)", color=(90, 60, 130))
            self.tab_rects["test_levels"] = test_rect
    
    def _open_testing(self):
        self._release_movement_keys()
        screen_ = self.state_manager.states.get(GameState.TESTING)
        if screen_ is not None:
            screen_.start(return_state=GameState.OVERWORLD)
            self.state_manager.transition_to(GameState.TESTING)

    def _debug_level_party(self, levels=5):
        """TEST ONLY: raise every party member (active + bench) by `levels`, capped at
        MAX_LEVEL, through the real Character.level_up() so stats, ability ranks, talent
        points and HP/mana all update exactly as a natural level-up would."""
        from config import MAX_LEVEL
        party = self.state_manager.get_party()
        members = list(party.members) + list(getattr(party, "bench", [])) if party else [self.state_manager.player]
        gained_total = 0
        for member in members:
            for _ in range(levels):
                if member.level >= MAX_LEVEL:
                    break
                member.level_up()
                gained_total += 1
            member.experience = 0
            # all_pets, not active_pet: Tinker and Necromancer now field
            # several at once (Character.extra_pets), and syncing only the
            # primary would leave every additional construct frozen at the
            # level it was summoned at.
            pets = getattr(member, "all_pets", None)
            if pets is None:
                pet = getattr(member, "active_pet", None)
                pets = [pet] if pet is not None else []
            for pet in pets:
                if pet is not None and hasattr(pet, "sync_to_owner_level"):
                    pet.sync_to_owner_level()
        player = self.state_manager.player
        if gained_total:
            self._notify(f"TEST: party +{levels} levels (you are now level {player.level}).", (200, 170, 255))
        else:
            self._notify(f"Everyone is already at the level cap ({MAX_LEVEL}).", (240, 200, 140))

    def _open_inventory(self):
        """
        Open the bag on the PLAYER. The inventory screen is shared with the
        party screen's "Gear" button, so the subject is reset explicitly -
        otherwise opening it from the overworld could still be pointed at
        whichever companion was geared last.
        """
        inventory = self.state_manager.states.get(GameState.INVENTORY)
        if inventory is not None and hasattr(inventory, "set_subject"):
            inventory.set_subject(None, return_state=GameState.OVERWORLD)
        self.state_manager.transition_to(GameState.INVENTORY)

    # ---- TRACKING, AND THE CAST BUTTON ------------------------------------------------------
    #: material_type -> (the trade that tracks it, marker colour). Same colours as the map.
    TRACKING = {"ore": ("mining", (235, 150, 60)), "herb": ("herbalism", (110, 220, 90)),
                "wood": ("woodcutting", (170, 120, 70)), "fish": ("fishing", (90, 190, 235))}
    #: An off-screen node is pointed at from this far away, in tiles.
    TRACK_RANGE = 28

    def tracked_nodes(self):
        """[(kind, colour, x, y)] for every unharvested node of a trade THE PLAYER HAS LEARNED.

        Kyle, 13 Nov: "We need fish tracking. Also for each tracking you ONLY learn it if you
        have the profession!!!" So this is the only gate there is: a miner tracks veins, a
        fisher tracks pools, and somebody with neither trade gets no markers at all. A fishing
        pool is tracked at the pool on the water, which is where it is drawn.
        """
        player = getattr(self.state_manager, "player", None)
        known = set(getattr(player, "known_professions", []) or []) if player is not None else set()
        gm = self.zone_manager.gathering_manager
        out = []
        for node in getattr(gm, "active_nodes", []) or []:
            if node.gathered:
                continue
            kind = (gm.materials.get(node.material_id) or {}).get("material_type")
            trade, colour = self.TRACKING.get(kind, (None, None))
            if trade is None or trade not in known:
                continue
            x, y = node.pool_tile if (kind == "fish" and node.pool_tile) else (node.x, node.y)
            out.append((kind, colour, x, y))
        return out

    def _render_tracking(self, screen):
        """A pulsing marker over each tracked node in view, and an arrow at the edge of the view
        toward the nearest one of each kind that is not."""
        nodes = self.tracked_nodes()
        if not nodes:
            return
        import math
        ts = self.tilemap_renderer.tile_size
        vr = self.viewport_rect
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 260.0)
        px, py = self.zone_manager.player_x, self.zone_manager.player_y
        nearest_off = {}
        for kind, colour, x, y in nodes:
            sx, sy = self.camera.world_to_screen(x, y, ts)
            cx, cy = sx + vr.x + ts // 2, sy + vr.y + ts // 2
            if vr.collidepoint(cx, cy):
                if kind == "fish":
                    r = int(ts * (1.25 + 0.2 * pulse))
                    pygame.draw.circle(screen, (10, 20, 30), (cx, cy), r + 1, 4)
                    pygame.draw.circle(screen, colour, (cx, cy), r, 2)
                top = cy - ts - int(4 * pulse) - (ts // 2 if kind == "fish" else ts)
                pts = [(cx, top - 6), (cx + 6, top), (cx, top + 6), (cx - 6, top)]
                pygame.draw.polygon(screen, (10, 10, 12), [(a + (2 if a > cx else -2 if a < cx else 0),
                                                            b + (2 if b > top else -2 if b < top else 0)) for a, b in pts])
                pygame.draw.polygon(screen, colour, pts)
            else:
                d = max(abs(x - px), abs(y - py))
                if d <= self.TRACK_RANGE and (kind not in nearest_off or d < nearest_off[kind][0]):
                    nearest_off[kind] = (d, colour, cx, cy)
        mx, my = vr.centerx, vr.centery
        for kind, (d, colour, cx, cy) in nearest_off.items():
            ang = math.atan2(cy - my, cx - mx)
            # walk out from the centre to just inside the frame
            k = min((vr.width / 2 - 18) / max(1e-6, abs(math.cos(ang))),
                    (vr.height / 2 - 18) / max(1e-6, abs(math.sin(ang))))
            ax, ay = mx + math.cos(ang) * k, my + math.sin(ang) * k
            tip = (ax + math.cos(ang) * 9, ay + math.sin(ang) * 9)
            left = (ax + math.cos(ang + 2.5) * 9, ay + math.sin(ang + 2.5) * 9)
            right = (ax + math.cos(ang - 2.5) * 9, ay + math.sin(ang - 2.5) * 9)
            pygame.draw.polygon(screen, (10, 10, 12), [tip, left, right], 0)
            pygame.draw.polygon(screen, colour, [tip, left, right], 0)
            pygame.draw.polygon(screen, (10, 10, 12), [tip, left, right], 2)

    # ---- THE CAST ------------------------------------------------------------------------------
    #: Seconds from throwing the line to the fish coming out.
    CAST_SECONDS = 1.8

    def _start_cast(self, node):
        """Throw a line at a pool. The fish arrives when the animation ends (_update_cast)."""
        if getattr(self, "_cast", None):
            return
        player = self.state_manager.player
        if not player.knows_profession("fishing"):
            self._gather_node(node)          # says "you need to learn Fishing first"
            return
        zm = self.zone_manager
        self._cast = {"node": node, "t": 0.0, "at": (zm.player_x, zm.player_y)}

    def _update_cast(self, dt):
        cast = getattr(self, "_cast", None)
        if not cast:
            return
        zm = self.zone_manager
        if (zm.player_x, zm.player_y) != cast["at"] or cast["node"].gathered:
            self._cast = None                # walked off: the line comes in with nothing on it
            return
        cast["t"] += dt
        if cast["t"] < self.CAST_SECONDS:
            return
        node = cast["node"]
        self._cast = None
        self._gather_node(node)
        if self.recruit_message and self.recruit_message.startswith("Gathered"):
            self.recruit_message += (" The pool is fished out." if node.gathered
                                     else " Something is still moving in the pool.")

    def _render_cast(self, screen):
        """The line, the bobber and the splash. Thrown in an arc over the first fifth of the cast,
        bobbing on the pool in the middle, pulled under with a ring of splash at the end."""
        cast = getattr(self, "_cast", None)
        if not cast or not cast["node"].pool_tile:
            return
        import math
        ts = self.tilemap_renderer.tile_size
        vr = self.viewport_rect
        f = min(1.0, cast["t"] / self.CAST_SECONDS)
        sx, sy = self.camera.world_to_screen(cast["at"][0], cast["at"][1], ts)
        hand = (sx + vr.x + ts // 2, sy + vr.y - ts // 3)
        wx, wy = self.camera.world_to_screen(cast["node"].pool_tile[0], cast["node"].pool_tile[1], ts)
        pool = (wx + vr.x + ts // 2, wy + vr.y + ts // 2)
        # the rod: a short pole from the hand toward the pool, tipped up
        ang = math.atan2(pool[1] - hand[1], pool[0] - hand[0])
        tip = (hand[0] + math.cos(ang) * ts * 0.9, hand[1] + math.sin(ang) * ts * 0.9 - ts * 0.6)
        pygame.draw.line(screen, (30, 20, 12), hand, tip, 5)
        pygame.draw.line(screen, (150, 105, 60), hand, tip, 3)
        throw = min(1.0, f / 0.2)
        bx = tip[0] + (pool[0] - tip[0]) * throw
        by = tip[1] + (pool[1] - tip[1]) * throw - math.sin(throw * math.pi) * ts * 1.4
        bite = max(0.0, (f - 0.82) / 0.18)
        if throw >= 1.0:
            by += math.sin(cast["t"] * 7.0) * 2.0 + bite * 7.0
        # the line sags between the rod tip and the bobber
        mid = ((tip[0] + bx) / 2, (tip[1] + by) / 2 + ts * 0.35 * throw)
        pts = [((1 - u) ** 2 * tip[0] + 2 * (1 - u) * u * mid[0] + u * u * bx,
                (1 - u) ** 2 * tip[1] + 2 * (1 - u) * u * mid[1] + u * u * by) for u in (i / 12 for i in range(13))]
        pygame.draw.lines(screen, (235, 235, 225), False, pts, 1)
        if throw >= 1.0:
            ring = int(6 + 5 * (0.5 + 0.5 * math.sin(cast["t"] * 5.0)))
            pygame.draw.ellipse(screen, (220, 240, 250), (bx - ring, by + 2 - ring // 3, ring * 2, ring * 2 // 3), 1)
        if bite > 0:
            for k in range(3):
                r = int(ts * (0.25 + 0.5 * bite) + k * 5)
                pygame.draw.ellipse(screen, (235, 248, 255), (pool[0] - r, pool[1] - r // 2, r * 2, r), 2)
            for k in range(6):
                a = k * math.pi / 3
                pygame.draw.circle(screen, (235, 248, 255),
                                   (int(pool[0] + math.cos(a) * ts * 0.5 * bite),
                                    int(pool[1] - abs(math.sin(a)) * ts * 0.7 * bite - 4)), 2)
        else:
            pygame.draw.circle(screen, (20, 20, 24), (int(bx), int(by)), 5)
            pygame.draw.circle(screen, (225, 60, 50), (int(bx), int(by)), 4)
            pygame.draw.circle(screen, (245, 245, 240), (int(bx), int(by) - 2), 2)

    def _render_cast_button(self, screen):
        """"Cast line (Space)" at the foot of the view whenever a pool is in reach. Click it or
        press Space. Shown to everyone: without Fishing it tells you to find a trainer."""
        self.cast_button_rect = None
        node = self.zone_manager.gathering_manager.fishing_node_near(
            self.zone_manager.player_x, self.zone_manager.player_y)
        if node is None or getattr(self, "_cast", None):
            return
        vr = self.viewport_rect
        rect = pygame.Rect(0, 0, 210, 34)
        rect.midbottom = (vr.centerx, vr.bottom - 14)
        pygame.draw.rect(screen, (18, 34, 48), rect, border_radius=6)
        pygame.draw.rect(screen, (90, 190, 235), rect, 2, border_radius=6)
        self.renderer.draw_text(screen, "Cast line (Space)", (rect.centerx, rect.y + 7), color=(220, 240, 250), center=True)
        self.cast_button_rect = rect

    def _notify(self, text, color=(120, 240, 140), duration=3.0):
        """Show a transient message over the viewport."""
        self.recruit_message = text
        self.recruit_message_color = color
        self.recruit_message_timer = duration

    def _gather_node(self, node):
        """Gather a node the player is standing on: consume it, award the
        material to the player character, roll a real WoW-style skill-up
        (orange/yellow/green/grey against the material's skill_range,
        capped at the material's tier cap), and toast a confirmation.
        Materials go on the PLAYER specifically (not a party-shared pool)
        - matches how consumables/inventory are already per-character
        rather than shared like currency (see Character.add_consumable's
        Phase 6 comment above)."""
        # Check profession before consuming the node - if the player hasn't
        # learned this gathering profession, block the gather entirely and
        # leave the node on the ground so they can come back after training.
        gathering_manager = self.zone_manager.gathering_manager
        mat_def = gathering_manager.get_material_def(node.material_id)
        if mat_def is not None:
            prof = mat_def.get("profession", "")
            player = self.state_manager.player
            if prof and not player.knows_profession(prof):
                label = prof.title()
                self._notify(f"You need to learn {label} first - find a trainer.", (220, 160, 80))
                return

        material_id = self.zone_manager.gather_node(node)
        if material_id is None:
            return

        material = gathering_manager.make_material_instance(material_id)
        if material is None:
            return

        player = self.state_manager.player
        added = player.add_material(material)
        if not added:
            self._notify(f"Bag full - couldn't gather {material.name}.", (240, 140, 140))
            return

        from world.gathering_manager import TIER_SKILL_CAPS
        current_skill = player.profession_skills.get(material.profession, 0)
        skilled_up = gathering_manager.roll_skill_up(material_id, current_skill)
        label = material.profession.title()
        if skilled_up and current_skill >= player.profession_cap(material.profession):
            self._notify(f"Gathered {material.name}. ({label} is at its cap - visit your trainer to advance.)", (220, 190, 120))
        elif skilled_up:
            cap = TIER_SKILL_CAPS.get(material.tier)
            player.gain_profession_skill(material.profession, 1, cap=cap)
            self._notify(f"Gathered {material.name}. ({material.profession.title()} skill up!)", (140, 220, 160))
        else:
            self._notify(f"Gathered {material.name}.", (140, 220, 160))

        # A vein sometimes has a crystal in it. Kyle, 2026-10-31: "Crystals can be
        # found in ore veins." roll_vein_crystal returns None for everything that
        # is not ore, so this needs no ore-only guard of its own. The crystal is a
        # bonus on top of the ore, grants no extra skill-up, and is skipped
        # silently if the bag is full - the ore was already collected and the
        # player has been told about it.
        crystal_id = gathering_manager.roll_vein_crystal(material_id)
        if crystal_id:
            crystal = gathering_manager.make_material_instance(crystal_id)
            if crystal is not None and player.add_material(crystal):
                self._notify(f"The vein also held {crystal.name}.", (170, 200, 240))

        # ...and, more rarely, a gemstone (world/gathering_manager.roll_vein_gem). Same rules
        # as the crystal: a bonus, no skill-up, skipped quietly if the bags are full.
        gem_id = gathering_manager.roll_vein_gem(material_id)
        if gem_id:
            gem = gathering_manager.make_material_instance(gem_id)
            if gem is not None and player.add_material(gem):
                self._notify(f"You prise a {gem.name} out of the vein!", (230, 200, 120))

        # Award a small amount of character XP for gathering.
        # Calibration: ~1% of the XP needed to level at the material's
        # effective level (half the skill cap of this material tier, mapped
        # linearly to level 1-60 against a 300-skill max cap).
        try:
            from config import get_exp_needed_for_level
            mat_skill_range = material.skill_range
            if mat_skill_range:
                skill_mid = (mat_skill_range[0] + mat_skill_range[-1]) / 2
            else:
                skill_mid = current_skill
            eff_level = max(1, int(skill_mid * 60 / 300) + 1)
            xp = max(3, int(get_exp_needed_for_level(eff_level) * 0.01))
            player.gain_experience(xp)
        except Exception:
            pass

    def _open_chest(self, chest_pos):
        """Open a chest the player is standing on - roll loot (or empty,
        a real outcome, see chest_manager.py), add it to the player's
        own inventory (matches combat loot's per-character convention,
        not a party-shared pickup), and toast the result. Mirrors
        _gather_node's shape directly - one-shot consume, notify,
        return."""
        player = self.state_manager.player
        item = self.zone_manager.open_chest(chest_pos, player.level)

        if item is None:
            self._notify("The chest is empty.", (170, 170, 170))
            return

        added = player.add_to_inventory(item)
        if not added:
            self._notify(f"Bag full - couldn't loot {item.name}.", (240, 140, 140))
            return

        self._notify(f"Looted: {item.name}!", (140, 220, 160))

    def update(self, dt):
        """Update state."""
        # Banter ticks out here because it is ambience that lives in the overworld - it has no input,
        # pauses nothing, and fades on its own.
        # Eating and drinking tick out here, where resting happens.
        party = self.state_manager.get_party()
        for member in ([self.state_manager.player] + list(getattr(party, "members", []))):
            if member is not None and hasattr(member, "tick_consumable_regen"):
                member.tick_consumable_regen(dt)

        from world.banter_manager import get_banter_manager
        get_banter_manager().update(dt)
        # ZoneManager does not own the party, so hand it the live one - arrivals fire from inside the
        # transition and need it there before the player walks through a door.
        self.zone_manager.set_banter_party(self.state_manager.get_party())

        if self.recruit_message_timer > 0:
            self.recruit_message_timer -= dt
            if self.recruit_message_timer <= 0:
                self.recruit_message = None
        self._update_cast(dt)

        # Buffs (Fortitude, Battle Shout, Mark of the Wild, ...) run on a
        # real-time 30-minute clock, so they have to keep ticking down out
        # here in the overworld too - not just while a fight is happening.
        # Real out-of-combat HP/Mana regen (tick_out_of_combat_regen) rides
        # the same per-frame loop, applied to the whole party - Spirit-based
        # regen isn't just a player perk, every party member benefits while
        # out of combat, same as buffs already do.
        self.seconds_since_last_move += dt
        from combat.status_effects import StatusEffectMixin
        is_standing_still = self.seconds_since_last_move >= StatusEffectMixin.STANDING_STILL_THRESHOLD
        party = self.state_manager.get_party()
        if party:
            # one lure burning anywhere in the party covers everyone; the strongest counts
            self.zone_manager.beast_lure_pct = max(
                [getattr(m, "beast_lure_pct", 0) for m in party.members
                 if getattr(m, "beast_lure_seconds", 0) > 0] or [0])
            for member in party.members:
                if member.consumable_cooldown > 0:
                    member.consumable_cooldown -= dt
                member.update_buff_timers(dt)
                if hasattr(member, "tick_seconds"):
                    member.tick_seconds(dt)
                # Ability cooldowns drain out here too, which is what makes
                # it safe for an out-of-combat cast to SET one - see
                # Ability.tick_cooldown_seconds. Without this, cooldowns only
                # ever moved at the end of a combat turn.
                book = getattr(member, "ability_book", None)
                if book is not None and hasattr(book, "tick_all_cooldowns_seconds"):
                    book.tick_all_cooldowns_seconds(dt)
                if hasattr(member, "tick_out_of_combat_regen"):
                    member.tick_out_of_combat_regen(dt, is_moving=not is_standing_still)

        player = self.state_manager.player
        zone = self.zone_manager.current_zone
        player_pos = self.zone_manager.get_player_pos()
        
        # Continuous movement (WSAD with cooldown between tiles). No longer
        # needs a "cast panel expanded" guard here - Cast is a real
        # full-screen transition now (see cast_screen.py), so this update()
        # simply doesn't run at all while it's open, the same way it
        # doesn't run while Inventory/Party/Map are open.
        self.movement_cooldown -= dt
        if self.movement_cooldown <= 0:
            moved = False
            if self.keys_pressed['W']:
                if self.zone_manager.move_player(0, -1):
                    moved = True
            elif self.keys_pressed['S']:
                if self.zone_manager.move_player(0, 1):
                    moved = True
            elif self.keys_pressed['A']:
                if self.zone_manager.move_player(-1, 0):
                    moved = True
            elif self.keys_pressed['D']:
                if self.zone_manager.move_player(1, 0):
                    moved = True
            
            if moved:
                from world.travel_manager import get_travel_manager
                self.movement_cooldown = 0.1 / get_travel_manager().speed_mult()  # 100ms/tile on foot, faster mounted
                found = getattr(self.zone_manager, "last_secret_found", None)
                if found:
                    self.zone_manager.last_secret_found = None
                    self._notify(found, (230, 200, 120))
                self.seconds_since_last_move = 0.0

                # Out-of-combat resource regen/decay, once per tile actually
                # stepped (not time-based) - Energy/Rage only now (see
                # restore_resources_out_of_combat_step's docstring - Mana
                # moved to the real per-second tick_out_of_combat_regen
                # above, which also runs while standing still).
                if hasattr(player, "restore_resources_out_of_combat_step"):
                    player.restore_resources_out_of_combat_step()
                
                # Encounter trigger. Real dungeons/mini-dungeons use FIXED
                # spawn points throughout (you see the mob, you fight the
                # mob, it never comes back). Cave-like pockets (Skull Rock,
                # Dustwind Cave, ...) instead roll random trash per-tile
                # like the open world, but still have exactly one fixed
                # boss chamber - so the boss check always runs first in a
                # cave, and only cave-like ones fall through to the random
                # roll when no boss spawn is standing on this tile.
                if self.encounters_enabled:
                    party = self.state_manager.get_party()
                    party_size = len(party.members) if party else 1
                    enemies = []
                    if self.zone_manager.is_in_cave():
                        # Fixed cave spawns: the mobs you see are the mobs you
                        # fight - a lone boss/rare, or a PACK of 3-4 that pulls
                        # together (dungeon trash). This also catches the one
                        # pinned boss chamber in a random-roll cave.
                        spawn = self.zone_manager.check_fixed_spawn_group()
                        if spawn:
                            enemies = spawn
                        elif (not self.zone_manager.has_fixed_spawns()
                              and random.random() < self.zone_manager.encounter_chance()):
                            enemies = self.zone_manager.trigger_encounter_group(
                                player.level, party_size=party_size)
                    elif random.random() < self.zone_manager.encounter_chance():  # 2% open zone, 5% subzone
                        enemies = self.zone_manager.trigger_encounter_group(
                            player.level, party_size=party_size)
                    if enemies:
                        self.state_manager.current_enemy = enemies[0]
                        self.state_manager.current_enemies = enemies
                        self.state_manager.transition_to(GameState.COMBAT)
        
        # Update camera to follow player
        player_pos = self.zone_manager.get_player_pos()
        self.camera.update(player_pos[0], player_pos[1], zone.width, zone.height, self.tilemap_renderer.tile_size)
    
    def _render_banter(self, screen):
        from world.banter_manager import get_banter_manager
        if not hasattr(self, "_banter_panel"):
            from ui.banter_panel import BanterPanel
            self._banter_panel = BanterPanel(self.renderer)
        self._banter_panel.render(screen, get_banter_manager().current)

    def render(self, screen):
        """Draw overworld."""
        player = self.state_manager.player
        zone = self.zone_manager.current_zone
        player_pos = self.zone_manager.get_player_pos()
        
        # Get vendors, recruits, and ambient flavor NPCs in current zone
        vendors_in_zone = self.zone_manager.vendor_manager.get_vendors_in_zone(zone.name)
        
        # Get recruits via module function (not stored as zone_manager attribute)
        from world.recruit_manager import get_recruit_manager
        recruits_in_zone = get_recruit_manager().get_recruits_in_zone(zone.name)

        from world.ambient_npc_manager import get_ambient_npc_manager
        ambient_npcs_in_zone = get_ambient_npc_manager().get_npcs_in_zone(zone.name)

        # Quest indicators (gold/grey !/?) for every vendor and ambient
        # NPC in this zone who's a real quest giver - built fresh each
        # frame rather than cached, since a kill/turn-in mid-zone should
        # flip an NPC's marker immediately (e.g. finishing the last kill
        # for a quest turns its giver's "!" into "?" without needing to
        # leave and re-enter the zone).
        from world.quest_manager import get_quest_manager
        from world.travel_manager import services_for_npc
        quest_mgr = get_quest_manager()
        quest_mgr.refresh_gather_progress(player)       # FETCH / DELIVER quests flip to "?" as soon as the bag is full enough
        quest_indicators = {}
        for npc in list(vendors_in_zone) + list(ambient_npcs_in_zone):
            npc_id = getattr(npc, "vendor_id", None) or getattr(npc, "npc_id", None)
            if npc_id:
                indicator = quest_mgr.get_indicator_for_npc(npc_id, player.level)
                if indicator:
                    quest_indicators[npc_id] = indicator
                elif "flight" in services_for_npc(npc):
                    quest_indicators[npc_id] = "green_exclaim"   # flight masters wear a green "!"
        
        # Draw tilemap with camera follow (includes vendors and recruits with npc_color)
        cave_spawn_positions = None
        if self.zone_manager.is_in_cave():
            cave_spawn_positions = self.zone_manager.cave_spawns.active_positions()
        gathering_node_positions = self.zone_manager.gathering_manager.active_nodes_render_data()
# THE WORLD IS DRAWN INSIDE ITS FRAME AND NOWHERE ELSE. Nothing clipped it, so a tall
        # building or an NPC near the edge of the view was painted across the player frame, the
        # buttons under the map and the black margin - visible in every screenshot as a figure
        # standing on the health bar. Seen 12 Nov while checking NPC placement.
        _old_clip = screen.get_clip()
        screen.set_clip(self.viewport_rect)
        try:
                    self.tilemap_renderer.render_tilemap(screen, zone, player_pos, camera=self.camera, viewport_rect=self.viewport_rect, vendors=vendors_in_zone, recruits=recruits_in_zone, ambient_npcs=ambient_npcs_in_zone, cave_spawns=cave_spawn_positions, gathering_nodes=gathering_node_positions, creature_manager=self.zone_manager.creature_manager, player=player, player_facing=self.zone_manager.player_facing, quest_indicators=quest_indicators)
                    self._render_tracking(screen)
                    self._render_cast(screen)
        finally:
            screen.set_clip(_old_clip)
        self._render_cast_button(screen)
        
        # Draw large zone indicator at top center, with the zone's level band.
        #
        # CENTRED PROPERLY, not offset by a guessed 80px. The old position assumed a short name;
        # adding "- Level 44-47" to it made every long zone name run off toward the tab column.
        # draw_text already takes center=True, which measures the surface.
        self.renderer.draw_text(screen, zone_levels.banner(zone.name),
                                (SCREEN_WIDTH // 2, 10), size="large", color=(200, 200, 100),
                                center=True)
        # A HIDDEN ZONE WEARS A SKULL beside its name (world/hidden_zones.py). Kyle, 14 Nov:
        # "These new zones will still have the level range but maybe a skull next to them."
        # A FRONTIER ZONE (a hidden zone inside a hidden zone) wears two on each side.
        from world.hidden_zones import skulls
        n_sk = skulls(zone.name)
        if n_sk:
            from ui.skull_mark import skull
            w = self.renderer._get_font("large", None).size(zone_levels.banner(zone.name))[0]
            mark = skull(28)
            mw = mark.get_width()
            for i in range(n_sk):
                screen.blit(mark, (SCREEN_WIDTH // 2 - w // 2 - (mw + 8) * (i + 1), 12))
                screen.blit(mark, (SCREEN_WIDTH // 2 + w // 2 + 8 + (mw + 8) * i, 12))
        
        # Draw encounter status (top left)
        encounter_status = "ON" if self.encounters_enabled else "OFF"
        status_color = (100, 200, 100) if self.encounters_enabled else (200, 100, 100)
        self.renderer.draw_text(screen, f"Encounters: {encounter_status}", (20, 10), color=status_color)
        self._render_travel_hud(screen)
        
        # Right-edge tab column - replaces the old flat Inventory/Character/
        # Menu buttons. Cast is included here too (transitions to
        # GameState.CAST, see cast_screen.py) since its own self-drawn edge
        # tab was removed in favor of this single consistent column.
        self._render_tab_column(screen)
        
        # Draw info panel (right side). Portrait (class icon in a round
        # frame) sits top-left of the panel; name/level and the bars shift
        # right to sit beside it, WoW-unit-frame style. Bars themselves are
        # unchanged - Kyle asked to keep them as-is, just add the portrait.
        info_x = VIEWPORT_X + VIEWPORT_WIDTH + 20
        info_y = VIEWPORT_Y + 40

        portrait_radius = 28
        portrait_center = (info_x + portrait_radius, info_y + portrait_radius)
        from ui.class_portrait import get_class_icon
        icon = get_class_icon(player.char_class, size=portrait_radius * 2)
        self.renderer.draw_class_portrait(screen, portrait_center, portrait_radius, icon)

        bars_x = info_x + portrait_radius * 2 + 14
        text_y = info_y
        self.renderer.draw_text(screen, f"{player.name}", (bars_x, text_y), size="large")
        text_y += 28
        self.renderer.draw_text(screen, f"Level {player.level}  |  Prestige {player.prestige_level}", (bars_x, text_y))

        # Bars start below the portrait once the portrait is taller than the
        # name/level text block, so nothing overlaps regardless of which is
        # taller at this width.
        info_y = max(text_y + 28, portrait_center[1] + portrait_radius + 10)

        # HP plus the class's actual resource, so you can see whether you're
        # ready for a fight without opening the character sheet. Resource is
        # driven by CLASS_RESOURCE_MAP rather than hardcoded class checks.
        self.renderer.draw_text(screen, f"HP: {player.display_health}/{round(player.health)}", (info_x, info_y))
        info_y += 22
        self.renderer.draw_health_bar(screen, (info_x, info_y),
                                      player.current_health, player.health,
                                      width=160, height=14, bar_color=COLOR_GREEN)
        info_y += 26

        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(player.char_class)
        resource_row = [
            (ResourceType.MANA, "Mana", player.current_mana, player.mana, COLOR_BLUE),
            (ResourceType.RAGE, "Rage", player.current_rage, player.max_rage, COLOR_RED),
            (ResourceType.ENERGY, "Energy", player.current_energy, player.max_energy, COLOR_YELLOW),
        ]
        for res_type, label, current, maximum, color in resource_row:
            if resource == res_type and maximum:
                self.renderer.draw_text(
                    screen, f"{label}: {round(current)}/{round(maximum)}",
                    (info_x, info_y))
                info_y += 22
                self.renderer.draw_health_bar(screen, (info_x, info_y),
                                              current, maximum,
                                              width=160, height=14, bar_color=color)
                info_y += 26
                break

        # NO TILE-COLOUR LEGEND HERE ANY MORE. Grass/Water/Stone/NPC/Portal/Boss swatches were a
        # key to the placeholder colours from before the world had art. Kyle, 10 Nov: "I think
        # its time to remove THESE blocks from the UI screen." The map screen keeps its own
        # legend, which is where one belongs.
        
        # NO CONTROLS LINE EITHER. "WSAD: Move | Space: Interact | ... R: Ride | H: Hearth" sat
        # directly under the Mount (R) and Hearth (H) buttons, which already say their keys.
        # Kyle, 10 Nov: "we don't need BOTH of these here. people know how to move...."

        if self.recruit_message:
            self.renderer.draw_text(screen, self.recruit_message,
                                    (VIEWPORT_X + 20, VIEWPORT_Y + 20),
                                    color=self.recruit_message_color)

        # Drawn last so it always sits on top of everything else on this
        # screen, same "modal is always the topmost thing" convention as
        # inventory_screen.py's destroy-confirmation.
        if self.teleport_menu_open:
            self._render_teleport_menu(screen)

        # Last, so nothing in the HUD draws over it.
        self._render_banter(screen)

    def _teleport_to(self, dest):
        """Put the party in front of that town's innkeeper. A teleport, not a walk through a door
        (via_portal=False), and it goes through transition_to_zone's own nearest-walkable net."""
        self.teleport_menu_open = False
        self._cast = None
        self.zone_manager.transition_to_zone(dest["zone"], dest["x"], dest["y"], via_portal=False)
        self._notify(f"Teleported to {dest['label']}.", (140, 210, 230))

    def _render_teleport_menu(self, screen):
        """Every town with an inn, in two columns by continent. Click one to go; Esc or Close to
        stay where you are."""
        from world.fast_travel import destinations, CONTINENT_TITLES
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        dests = destinations(self.zone_manager)
        groups = {}
        for d in dests:
            groups.setdefault(d["continent"], []).append(d)
        rows = max((len(v) for v in groups.values()), default=1)
        col_w, row_h, gap = 300, 30, 6
        box_w = len(groups) * (col_w + 24) + 24
        box_h = 96 + rows * (row_h + gap) + 60
        box = pygame.Rect((SCREEN_WIDTH - box_w) // 2, max(8, (SCREEN_HEIGHT - box_h) // 2), box_w, box_h)
        self.renderer.draw_rect(screen, box, (25, 25, 30))
        self.renderer.draw_rect(screen, box, (130, 110, 180), fill=False)
        self.renderer.draw_text(screen, "Teleport to a town", (box.x + 24, box.y + 14),
                                color=(210, 195, 240), size="large")

        here = self.zone_manager.current_zone.name if self.zone_manager.current_zone else None
        self.teleport_rects = []
        for c, (continent, towns) in enumerate(groups.items()):
            x = box.x + 24 + c * (col_w + 24)
            self.renderer.draw_text(screen, CONTINENT_TITLES.get(continent, continent),
                                    (x, box.y + 60), color=(200, 200, 100))
            y = box.y + 90
            for d in towns:
                rect = pygame.Rect(x, y, col_w, row_h)
                colour = (60, 90, 60) if d["zone"] == here else (45, 45, 70)
                self.renderer.draw_button(screen, rect, d["label"], color=colour)
                self.teleport_rects.append((rect, d))
                y += row_h + gap
        self.teleport_close_rect = pygame.Rect(0, 0, 140, 36)
        self.teleport_close_rect.midbottom = (box.centerx, box.bottom - 14)
        self.renderer.draw_button(screen, self.teleport_close_rect, "Close")
