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

        # Unstuck confirmation modal. A tester stuck in a broken/unwalkable
        # cave layout (Kyle, 2026-09-06: "I know caves are still broken...
        # so I need an 'unstuck' button that force teleports you to Razor
        # Hill") needs a way out that doesn't depend on the very navigation
        # that's currently broken. Fires immediately on confirm - no
        # multi-step wizard - since the whole point is getting a stuck
        # player moving again as fast as possible. Gated behind one Yes/No
        # confirm (Kyle's explicit ask) so a stray misclick mid-dungeon-run
        # doesn't yank a NOT-stuck player away from wherever they actually
        # are.
        self.unstuck_confirm_pending = False
        self.unstuck_yes_button = pygame.Rect(0, 0, 140, 44)
        self.unstuck_no_button = pygame.Rect(0, 0, 140, 44)
    
    def handle_event(self, event):
        """Handle input."""
        # Unstuck confirmation takes over ALL input while pending - same
        # modal convention as inventory_screen.py's destroy-confirmation
        # (see _render_destroy_confirmation there) - so a click meant for
        # the Yes/No box can never also register as a movement key or a
        # tab click underneath it.
        if self.unstuck_confirm_pending:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.unstuck_yes_button.collidepoint(event.pos):
                    self._do_unstuck()
                    self.unstuck_confirm_pending = False
                elif self.unstuck_no_button.collidepoint(event.pos):
                    self.unstuck_confirm_pending = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.unstuck_confirm_pending = False
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

            # Unstuck - force-teleport to Razor Hill, for testers who hit
            # a broken/unwalkable cave layout and have no other way out.
            # Opens the confirm modal rather than firing immediately (see
            # constructor comment) - actual teleport happens in
            # _do_unstuck() once confirmed.
            if event.key == pygame.K_u:
                self.unstuck_confirm_pending = True
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

            # F5 quicksave. Until now the game saved exactly once, at
            # character creation, and never again - so a recruited party,
            # every level gained and all loot found was lost on exit.
            if event.key == pygame.K_F5:
                if self.state_manager.save_game():
                    self._notify("Game saved.", (140, 240, 160))
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
                chest = None if (vendor or recruit or ambient_npc or gathering_node or forge) else self.zone_manager.get_chest_at_location()

                if forge:
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
            self._handle_tab_click(mouse_pos)
    
    def _release_movement_keys(self):
        for k in self.keys_pressed:
            self.keys_pressed[k] = False

    def _toggle_mount(self):
        from world.travel_manager import get_travel_manager
        mounted, message = get_travel_manager().toggle_mount(self.zone_manager.is_in_cave())
        self._notify(message, (140, 220, 160) if mounted or message == "You dismount." else (240, 140, 140))

    def _use_hearth(self):
        """Teleport to the innkeeper bind (outside caves/dungeons, off cooldown)."""
        from world.travel_manager import get_travel_manager
        travel = get_travel_manager()
        reason = travel.hearth_block_reason(self.zone_manager.is_in_cave())
        if reason:
            self._notify(reason, (240, 140, 140))
            return
        bind = travel.use_hearth()
        self._release_movement_keys()
        if not self.zone_manager.transition_to_zone(bind["zone"], bind["x"], bind["y"]):
            self._notify("Your hearth bind no longer exists. Visit an innkeeper.", (240, 140, 140))
            return
        self._notify(f"You return to {bind['name']}.", (140, 220, 160))

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
            elif action == "unstuck":
                self.unstuck_confirm_pending = True
            elif action == "test_levels":
                self._debug_level_party(5)
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

        # Unstuck sits apart from the main action stack (a gap below,
        # warning-red rather than the tab blue) - it's an emergency/testing
        # tool, not a normal navigation action, and shouldn't visually
        # blend into "just another tab" next to Map/Party/Inventory.
        y += self.tab_gap
        unstuck_rect = pygame.Rect(self.tab_column_x, y, self.tab_w, self.tab_h)
        self.renderer.draw_button(screen, unstuck_rect, "Unstuck (U)", color=(110, 40, 40))
        self.tab_rects["unstuck"] = unstuck_rect

        # TEST BUTTON (Kyle): +5 levels for the whole party, so every zone can be
        # play-tested without grinding. Flip DEBUG_LEVEL_BUTTON off before release.
        if DEBUG_LEVEL_BUTTON:
            y += self.tab_h + self.tab_gap
            test_rect = pygame.Rect(self.tab_column_x, y, self.tab_w, self.tab_h)
            self.renderer.draw_button(screen, test_rect, "TEST: +5 Levels", color=(90, 60, 130))
            self.tab_rects["test_levels"] = test_rect
    
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
            pet = getattr(member, "active_pet", None)
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
        material_id = self.zone_manager.gather_node(node)
        if material_id is None:
            return

        gathering_manager = self.zone_manager.gathering_manager
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
        if skilled_up:
            cap = TIER_SKILL_CAPS.get(material.tier)
            player.gain_profession_skill(material.profession, 1, cap=cap)
            self._notify(f"Gathered {material.name}. ({material.profession.title()} skill up!)", (140, 220, 160))
        else:
            self._notify(f"Gathered {material.name}.", (140, 220, 160))

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
        if self.recruit_message_timer > 0:
            self.recruit_message_timer -= dt
            if self.recruit_message_timer <= 0:
                self.recruit_message = None

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
            for member in party.members:
                if member.consumable_cooldown > 0:
                    member.consumable_cooldown -= dt
                member.update_buff_timers(dt)
                if hasattr(member, "tick_seconds"):
                    member.tick_seconds(dt)
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
                        # Fixed cave spawns stay single-mob; the mob you see
                        # is the mob you fight, by design. This also catches
                        # the one pinned boss chamber in a random-roll cave.
                        spawn = self.zone_manager.check_fixed_spawn()
                        if spawn:
                            enemies = [spawn]
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
        self.tilemap_renderer.render_tilemap(screen, zone, player_pos, camera=self.camera, viewport_rect=self.viewport_rect, vendors=vendors_in_zone, recruits=recruits_in_zone, ambient_npcs=ambient_npcs_in_zone, cave_spawns=cave_spawn_positions, gathering_nodes=gathering_node_positions, creature_manager=self.zone_manager.creature_manager, player=player, player_facing=self.zone_manager.player_facing, quest_indicators=quest_indicators)
        
        # Draw large zone indicator at top center
        self.renderer.draw_text(screen, f"~ {zone.name} ~", (SCREEN_WIDTH // 2 - 80, 10), size="large", color=(200, 200, 100))
        
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

        # Compact two-column legend, sitting just under the resource bars.
        info_y += 14
        self.tilemap_renderer.render_legend(screen, self.renderer.font_normal, x=info_x, y=info_y)
        
        # Instructions - shrunk to just the keys with no tab-column
        # equivalent (movement/interact/encounters). Everything else now
        # has its own labeled tab in the right-edge column, so repeating
        # the full keybind list here was redundant and was also the thing
        # running off the window edge.
        self.renderer.draw_text(
            screen, "WSAD: Move | Space: Interact | E: Encounters | R: Ride | H: Hearth",
            (20, SCREEN_HEIGHT - 30), size="small")

        if self.recruit_message:
            self.renderer.draw_text(screen, self.recruit_message,
                                    (VIEWPORT_X + 20, VIEWPORT_Y + 20),
                                    color=self.recruit_message_color)

        # Drawn last so it always sits on top of everything else on this
        # screen, same "modal is always the topmost thing" convention as
        # inventory_screen.py's destroy-confirmation.
        if self.unstuck_confirm_pending:
            self._render_unstuck_confirmation(screen)

    def _do_unstuck(self):
        """Force-teleport the player to Razor Hill. Reuses
        ZoneManager.transition_to_zone with no explicit spawn_x/spawn_y,
        so it falls back to Razor Hill's zone center and goes through the
        SAME walkable-tile safety net every normal portal/cave-exit
        transition already relies on (transition_to_zone's
        _find_nearest_walkable spiral-search) - no separate teleport
        logic to keep in sync with that.

        Also correctly clears cave-spawn state on the way out (is_in_cave()
        is checked against self.current_zone AFTER transition_to_zone has
        already swapped it to Razor Hill, so it always resolves to "not a
        cave" here and calls cave_spawns.clear() - see
        ZoneManager.transition_to_zone), so a player unstuck-ing out of a
        cave doesn't drag that cave's fixed-spawn bookkeeping along with
        them into Razor Hill.
        """
        self.zone_manager.transition_to_zone("Razor Hill")
        self._notify("Teleported to Razor Hill.", (140, 210, 230))

    def _render_unstuck_confirmation(self, screen):
        """Modal Yes/No confirmation before force-teleporting - Kyle's
        explicit ask ("Give it confirmation option too") so a misclick
        doesn't yank a player away from wherever they actually are,
        mid-dungeon-run or otherwise. Same visual convention as
        inventory_screen.py's _render_destroy_confirmation (dim overlay,
        centered box, Yes/No pair)."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        box_w, box_h = 420, 190
        box = pygame.Rect((SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2 - 20, box_w, box_h)
        self.renderer.draw_rect(screen, box, (25, 25, 30))
        self.renderer.draw_rect(screen, box, (170, 70, 70), fill=False)

        self.renderer.draw_text(screen, "Teleport to Razor Hill?", (box.x + 20, box.y + 16),
                                color=(220, 140, 140), size="large")
        self.renderer.draw_text(
            screen, "Use this if you're stuck in a broken area.",
            (box.x + 20, box.y + 60), color=(200, 200, 205), size="small")
        self.renderer.draw_text(
            screen, "Any unsaved zone progress this session stays as-is.",
            (box.x + 20, box.y + 84), color=(160, 160, 168), size="small")

        self.unstuck_yes_button.center = (box.centerx - 80, box.bottom - 40)
        self.unstuck_no_button.center = (box.centerx + 80, box.bottom - 40)
        self.renderer.draw_button(screen, self.unstuck_yes_button, "Teleport", color=(110, 40, 40))
        self.renderer.draw_button(screen, self.unstuck_no_button, "Cancel")
