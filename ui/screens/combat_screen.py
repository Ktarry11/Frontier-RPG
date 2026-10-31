"""
Combat screen Phase 4. Redesigned UI with larger hotbar, better text, and combat flow.
"""
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING,
    COLOR_WHITE, COLOR_DARK_GRAY, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_GOLD, COLOR_YELLOW
)
from core.game_states import GameState
from ui.sprite_loader import get_creature_sprite
from combat.combat_engine import CombatEngine
from combat.status_effects import EffectType
from ui.screens.base_screen import BaseScreen


from ui.coin_format import format_coins


class CombatScreen(BaseScreen):
    """Combat screen with redesigned UI layout."""
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.combat_engine = None
        self.combat_background = None  # scaled Surface, set in _init_combat()
        self.message_log = []
        self.selected_target = "enemy"  # "enemy" or "self"
        self.hotbar_positions = []  # Rects for hotbar buttons
        self.extra_slot_positions = []  # Rects for click-only extra ability slots
        self._init_hotbar_positions()
        self.stance_positions = {}  # stance_id -> Rect, Warrior-only selector
        self._init_stance_positions()

        # Manual targeting mode. When a hotbar slot is clicked, we enter
        # targeting mode and let the player pick who the ability lands on.
        self.targeting_mode = None  # (ability_id, slot_index, ability, actor) while active
        self.targeting_valid_targets = []  # all valid recipients for this ability
        self.targeting_hovered = None  # which recipient is under the mouse now

        # Real hover-tooltip state for hotbar abilities (Kyle's ask: hover
        # a hotbar slot mid-combat to see its real pre-modifier info, same
        # as cast_screen.py's tooltip - built off the same shared
        # Ability.get_tooltip_lines() so the wording/numbers are identical
        # wherever they're shown). hovered_ability is the real Ability
        # under the mouse right now (or None); consumables don't get a
        # tooltip here (Consumable has no get_tooltip_lines - only real
        # abilities do).
        self.hovered_ability = None
        self.mouse_pos = (0, 0)
    
    #: Hotbar geometry. Promoted out of _init_hotbar_positions because the enemy strip has to
    #: know where the hotbar starts in order to not push the combat log underneath it, and two
    #: copies of "where the hotbar is" is exactly the kind of split that rots the moment one of
    #: them changes.
    HOTBAR_BUTTON_SIZE = 80
    HOTBAR_SPACING = HOTBAR_BUTTON_SIZE + 5
    HOTBAR_X_START = 40

    @classmethod
    def _hotbar_top(cls):
        """Topmost pixel the hotbar occupies - the ceiling everything above it has to live under."""
        return SCREEN_HEIGHT - cls.HOTBAR_BUTTON_SIZE - 40 - cls.HOTBAR_SPACING

    def _init_hotbar_positions(self):
        """Calculate hotbar button positions (2 rows of 10, larger buttons),
        plus a block of click-only "extra slot" buttons filling the dead
        space that used to sit empty between the last hotbar column and the
        stance buttons on the right (Kyle's screenshot: real wasted real
        estate in the hotbar panel). Extra slots get 2 rows x 4 cols - same
        button size as the hotbar so it reads as one continuous bar, not a
        bolted-on second widget."""
        HOTBAR_BUTTON_SIZE = self.HOTBAR_BUTTON_SIZE
        HOTBAR_SPACING = self.HOTBAR_SPACING
        HOTBAR_X_START = self.HOTBAR_X_START

        # Row 1 (bottom)
        hotbar_y1 = SCREEN_HEIGHT - HOTBAR_BUTTON_SIZE - 40
        for i in range(10):
            rect = pygame.Rect(
                HOTBAR_X_START + (i * HOTBAR_SPACING),
                hotbar_y1,
                HOTBAR_BUTTON_SIZE,
                HOTBAR_BUTTON_SIZE
            )
            self.hotbar_positions.append(rect)
        
        # Row 2 (above row 1)
        hotbar_y2 = hotbar_y1 - HOTBAR_SPACING
        for i in range(10):
            rect = pygame.Rect(
                HOTBAR_X_START + (i * HOTBAR_SPACING),
                hotbar_y2,
                HOTBAR_BUTTON_SIZE,
                HOTBAR_BUTTON_SIZE
            )
            self.hotbar_positions.append(rect)

        # Extra (click-only) slots. Sit in the gap between the last hotbar
        # column (right edge ~885) and the stance buttons (left edge
        # ~1100) - real available width there is ~215px, room for 2
        # columns of 80px buttons with a small gap either side.
        EXTRA_X_START = HOTBAR_X_START + 10 * HOTBAR_SPACING + 20
        self.extra_slot_positions = []
        for row in range(2):
            y = hotbar_y1 if row == 0 else hotbar_y2
            for col in range(2):
                rect = pygame.Rect(
                    EXTRA_X_START + col * HOTBAR_SPACING,
                    y,
                    HOTBAR_BUTTON_SIZE,
                    HOTBAR_BUTTON_SIZE
                )
                self.extra_slot_positions.append(rect)

    def _init_stance_positions(self):
        """Three stacked buttons on the right edge, clear of the hotbar
        (which only spans x=40 to ~890) and the enemy/log area above it.
        Rendered/clickable only when the acting character actually has a
        stance (see _draw_stance_selector) - built once here regardless,
        same as hotbar_positions, since layout math doesn't depend on who's
        acting."""
        from combat.stances import STANCES
        BTN_W, BTN_H = 150, 40
        x = SCREEN_WIDTH - BTN_W - 30
        y0 = SCREEN_HEIGHT - (BTN_H + 8) * len(STANCES) - 40
        for i, stance_id in enumerate(STANCES.keys()):
            self.stance_positions[stance_id] = pygame.Rect(
                x, y0 + i * (BTN_H + 8), BTN_W, BTN_H
            )
    
    def _init_combat(self):
        """Initialize combat when entering screen."""
        # Always create a fresh combat engine (fixes instant loss on new fight bug)
        player = self.state_manager.player
        enemy = self.state_manager.current_enemy
        party = self.state_manager.get_party()
        enemies = getattr(self.state_manager, "current_enemies", None) or [enemy]

        # Resolve a combat background for wherever the fight is actually
        # happening. Zone name comes from the live ZoneManager the overworld
        # owns - is_in_cave() picks the cave-name lookup the same way
        # TilemapRenderer._biome_for() already does, so the combat backdrop
        # always agrees with whatever biome the overworld tiles were showing
        # right before the fight triggered. Best-effort: None here just
        # means render() falls back to its existing flat background.
        self.combat_background = None
        zone_manager = getattr(self.state_manager, "zone_manager", None)
        combat_zone_key = None
        if zone_manager and zone_manager.current_zone:
            from ui.combat_background_loader import get_background_for_zone
            is_cave = zone_manager.is_in_cave()
            zone_name = zone_manager.current_zone.name
            self.combat_background = get_background_for_zone(
                zone_name, is_cave=is_cave, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
            # Same slug normalization every other NPC/quest lookup uses
            # (VendorManager._zone_key, race_registry.get_zone_default_race)
            # - current_zone.name is already the RIGHT specific location
            # whether it's an open zone or a cave (is_in_cave() checks
            # this exact name against the cave-name set), so no separate
            # "which cave am I in" lookup is needed here.
            combat_zone_key = zone_name.lower().replace(" ", "_").replace("'", "")

        self.combat_engine = CombatEngine(player, enemy, party=party,
                                          enemies=enemies, zone=combat_zone_key)  # loot_dropped resets to None here
        self.message_log = []  # Clear old messages

        foes = enemy.name if len(enemies) <= 1 else f"{len(enemies)} enemies ({', '.join(e.name for e in enemies)})"
        if len(party.members) > 1:
            self.message_log.append(
                f"Combat started: {len(party.members)} party members vs {foes}!")
        else:
            self.message_log.append(f"Combat started: {player.name} vs {foes}!")
        self.message_log.append("---")
        
        # Auto-slot abilities if the hotbar is completely empty (first
        # encounter, or a save from before autofill existed).
        #
        # Uses get_learned_abilities() rather than get_all_abilities() - the
        # latter returns the whole class kit regardless of level, so this
        # would happily slot a level 30 ability onto a level 1 character's
        # bar, where it would then refuse to fire. Character._autofill_hotbar()
        # normally handles this already; this stays as a safety net for old
        # saves.
        if all(slot is None for slot in player.hotbar):
            abilities = (player.get_learned_abilities()
                         if hasattr(player, "get_learned_abilities")
                         else player.ability_book.get_all_abilities())
            for i, ability in enumerate(abilities[:10]):
                player.hotbar[i] = ability.ability_id
            self.message_log.append("Auto-slotted abilities! Edit them on the Skills screen.")
        
        # Reset overworld movement keys (prevent continued movement in combat)
        if hasattr(self.state_manager.states[GameState.OVERWORLD], 'keys_pressed'):
            self.state_manager.states[GameState.OVERWORLD].keys_pressed = {
                'W': False, 'S': False, 'A': False, 'D': False
            }
    
    def handle_event(self, event):
        """Handle input."""
        # ALWAYS reinitialize combat on entry (fresh engine each time)
        if self.combat_engine is None or not hasattr(self.combat_engine, 'is_active'):
            self._init_combat()
        
        # Targeting mode takes precedence - mouse clicks and ESC apply to targeting
        if self.targeting_mode:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.targeting_mode = None
                self.targeting_valid_targets = []
                self.targeting_hovered = None
                self.message_log.append("Targeting cancelled.")
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.targeting_hovered:
                    ability_id, slot_index, ability, actor = self.targeting_mode
                    self._execute_ability(actor, ability_id, self.targeting_hovered)
                return
            # Track which target is hovered
            if event.type == pygame.MOUSEMOTION:
                self.targeting_hovered = self._get_hovered_target(event.pos)
            return
        
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self.hovered_ability = None
            player = self.state_manager.player
            for i, rect in enumerate(self.hotbar_positions):
                if rect.collidepoint(event.pos):
                    from entities.consumable import Consumable
                    slot_content = player.hotbar[i] if i < len(player.hotbar) else None
                    if slot_content and not isinstance(slot_content, Consumable):
                        self.hovered_ability = player.ability_book.get_ability(slot_content)
                    break

        if not self.combat_engine.is_active:
            # Combat over - click or Space to return. Space is the natural
            # "continue" key (same finger players are already using for
            # interactions everywhere else), so requiring a mouse click here
            # specifically broke the keyboard-only flow.
            if event.type == pygame.MOUSEBUTTONDOWN or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
            ):
                # Respawn logic: revive the WHOLE party, not just the
                # player - a downed companion must not stay dead forever.
                party = self.state_manager.get_party()
                for member in party.members:
                    if not member.is_alive():
                        member.current_health = member.health
                        member.current_mana = member.mana
                        member.current_rage = 0
                        member.current_energy = 100
                # Clear combat engine so next combat reinitializes
                self.combat_engine = None

                # Autosave on leaving combat. This is the natural checkpoint:
                # XP, loot and levels have all just been awarded, and it means
                # progress survives a crash or an alt-F4 without the player
                # having to remember F5.
                self.state_manager.save_game()

                self.state_manager.transition_to(GameState.OVERWORLD)
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            player = self.state_manager.player
            
            # The player controls EVERY party member (FF-style), so the gate
            # is "is an ally acting", not "is the player acting".
            if not self._acting_member():
                self.message_log.append("It's not your party's turn!")
                return
            
            # Check hotbar clicks
            for i, rect in enumerate(self.hotbar_positions):
                if rect.collidepoint(mouse_pos):
                    self._use_hotbar_slot(i)
                    return

            # Check extra (click-only) slot clicks - same flow as hotbar,
            # just no keybind, so this is mouse-only by design.
            for i, rect in enumerate(self.extra_slot_positions):
                if rect.collidepoint(mouse_pos):
                    self._use_extra_slot(i)
                    return

            # Stance selector - only the acting character can switch, and
            # only if they actually have a stance (non-Warriors have
            # current_stance=None and can_use_stance() correctly refuses
            # everything for them, so this is a safe no-op click for the
            # other 8 classes rather than needing a class check here too).
            actor = self._acting_member()
            if actor is not None:
                for stance_id, rect in self.stance_positions.items():
                    if rect.collidepoint(mouse_pos):
                        success, msg = actor.set_stance(stance_id)
                        self.message_log.append(msg)
                        return

        if event.type == pygame.KEYDOWN:
            player = self.state_manager.player

            # Number-key hotbar shortcuts: 1-0 trigger the lower row (slots 0-9),
            # Shift+1-0 trigger the upper row (slots 10-19). "0" maps to the
            # 10th slot in each row (index 9 / 19), matching standard keyboard
            # number-row convention (1,2,...,9,0).
            slot_index = self._key_to_hotbar_slot(event.key, shift_held=(event.mod & pygame.KMOD_SHIFT))
            if slot_index is not None:
                if not self._acting_member():
                    self.message_log.append("It's not your party's turn!")
                    return
                self._use_hotbar_slot(slot_index)

    def _get_hovered_target(self, mouse_pos):
        """Which target is under the mouse, if any."""
        for combatant in self.targeting_valid_targets:
            # Render is responsible for drawing targets; we need their rects.
            # For now, use a simple heuristic: if this is an ally, it's on
            # the left panel; if an enemy, on the right. Later this should
            # compute actual rects from the render layout.
            is_ally = self.combat_engine.is_ally(combatant)
            # Ally rects are roughly on the left, enemies on the right.
            # This is a placeholder - render() should mark the actual rects.
            if is_ally and mouse_pos[0] < 400:
                if self._rect_for_combatant(combatant).collidepoint(mouse_pos):
                    return combatant
            elif not is_ally and mouse_pos[0] > 600:
                if self._rect_for_combatant(combatant).collidepoint(mouse_pos):
                    return combatant
        return None

    def _rect_for_combatant(self, combatant):
        """Approximate rect for a combatant's healthbar on screen.
        This is a placeholder - render() will need to provide actual rects."""
        is_ally = self.combat_engine.is_ally(combatant)
        index = (self.combat_engine.allies if is_ally else self.combat_engine.enemies).index(combatant)
        if is_ally:
            return pygame.Rect(20, 80 + index * 80, 360, 70)
        else:
            return pygame.Rect(SCREEN_WIDTH - 380, 80 + index * 80, 360, 70)

    def _acting_member(self):
        """
        The party member currently taking their turn, or None if an enemy
        (or a pet - see the pet-routing fix in update()) is.

        The player controls all five party members, so every ally's turn
        is a turn the human takes - EXCEPT pets, which are also allies
        for is_ally()'s purposes but are always AI-controlled (real bug
        fixed alongside execute_pet_action - a pet has no hotbar slot in
        the player's party UI to click, so returning one here would
        stall the turn waiting for input that can never come).
        """
        actor = self.combat_engine.current_actor
        if actor is not None and actor in self.combat_engine.pets:
            return None
        if actor is not None and self.combat_engine.is_ally(actor):
            return actor
        return None

    def _key_to_hotbar_slot(self, key, shift_held):
        """
        Map a pygame key (number row 1-9,0) to a hotbar slot index (0-19).
        Returns None if the key isn't a hotbar shortcut.
        """
        number_keys = [
            pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
            pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
        ]
        if key not in number_keys:
            return None

        row_index = number_keys.index(key)  # 0-9, where "0" key is index 9
        return row_index + 10 if shift_held else row_index

    def _hotbar_slot_to_key_label(self, slot_index):
        """Convert a hotbar slot index (0-19) to its display keybind label,
        e.g. slot 0 -> '1', slot 9 -> '0', slot 10 -> 'Shift+1', slot 19 -> 'Shift+0'."""
        row_index = slot_index % 10
        key_char = str(row_index + 1) if row_index < 9 else "0"
        if slot_index >= 10:
            return f"Shift+{key_char}"
        return key_char
    
    def _use_hotbar_slot(self, hotbar_slot):
        """Attempt to use a hotbar slot. Consumables fire immediately; abilities
        enter targeting mode."""
        if hotbar_slot < 0 or hotbar_slot >= 20:
            return
        
        actor = self._acting_member() or self.state_manager.player
        hotbar_content = actor.hotbar[hotbar_slot]
        
        if not hotbar_content:
            self.message_log.append(f"Slot {hotbar_slot + 1} is empty!")
            return
        
        # Consumables fire immediately without targeting
        from entities.consumable import Consumable
        if isinstance(hotbar_content, Consumable):
            consumable = hotbar_content
            if not consumable.can_use(actor):
                self.message_log.append("Can't use that consumable now!")
                return
            success = consumable.use(actor, self.message_log)
            if success:
                if consumable.quantity <= 0:
                    actor.hotbar[hotbar_slot] = None
                actor.consumable_cooldown = consumable.cooldown_seconds
            return
        
        # Abilities require targeting
        ability_id = hotbar_content
        ability = actor.ability_book.get_ability(ability_id)
        if not ability:
            self.message_log.append("Ability not found!")
            return
        self._enter_targeting_mode(ability_id, hotbar_slot, ability, actor)

    def _use_extra_slot(self, extra_slot):
        """Attempt to use a click-only extra slot. Mirrors _use_hotbar_slot
        exactly except it reads/writes actor.extra_slots instead of
        actor.hotbar - kept as a separate method rather than a shared one
        with a "which list" flag since the two are genuinely different
        arrays on Character (see Character.__init__)."""
        if extra_slot < 0 or extra_slot >= len(self.extra_slot_positions):
            return

        actor = self._acting_member() or self.state_manager.player
        if extra_slot >= len(actor.extra_slots):
            return
        slot_content = actor.extra_slots[extra_slot]

        if not slot_content:
            self.message_log.append("That slot is empty!")
            return

        from entities.consumable import Consumable
        if isinstance(slot_content, Consumable):
            consumable = slot_content
            if not consumable.can_use(actor):
                self.message_log.append("Can't use that consumable now!")
                return
            success = consumable.use(actor, self.message_log)
            if success:
                if consumable.quantity <= 0:
                    actor.extra_slots[extra_slot] = None
                actor.consumable_cooldown = consumable.cooldown_seconds
            return

        ability_id = slot_content
        ability = actor.ability_book.get_ability(ability_id)
        if not ability:
            self.message_log.append("Ability not found!")
            return
        # slot_index is tagged with a "extra:" prefix distinct from the
        # plain int hotbar uses, purely so nothing downstream could ever
        # mistake an extra-slot index for a real hotbar index if this
        # tuple shape gets reused/extended later - _render_targeting and
        # friends only ever read it back for display, never re-index
        # actor.hotbar with it, so this is a safety label, not a
        # functional requirement today.
        self._enter_targeting_mode(ability_id, f"extra:{extra_slot}", ability, actor)

    def _enter_targeting_mode(self, ability_id, slot_index, ability, actor):
        """Switch to manual targeting mode for this ability."""
        # Determine which combatants are valid targets based on target_type
        target_type = getattr(ability, "target_type", "enemy")
        
        if target_type == "self":
            # No choice - cast on self immediately
            self._execute_ability(actor, ability_id, actor)
            return
        
        if target_type == "party":
            # Party-wide - no choice, cast on everyone
            targets = self.combat_engine.living_allies()
            self._execute_ability(actor, ability_id, targets)
            return

        if target_type == "enemy_aoe":
            # Real UX bug fix: this used to fall through to the manual
            # single-enemy click path below, forcing a target pick before
            # casting even though CombatEngine.execute_ability ALREADY
            # unconditionally overrides target to living_enemies() for
            # any enemy_aoe ability (see its own real code - the pick
            # made here was always discarded and replaced). So the actual
            # damage was never wrong, just the UI made you click a
            # meaningless "target" first. Skips straight to casting, same
            # "no choice needed" treatment as "party" just above - the
            # list passed here doesn't even need to be the full enemy
            # list since execute_ability replaces it anyway, but passing
            # it explicitly keeps this branch's intent honest rather than
            # relying on a downstream override to paper over a nonsense
            # single target.
            targets = self.combat_engine.living_enemies()
            if not targets:
                self.message_log.append("No valid targets!")
                return
            self._execute_ability(actor, ability_id, targets)
            return

        # Manually targetable: pick between allies or enemies
        if target_type == "ally":
            valid = self.combat_engine.living_allies()
        else:  # "enemy"
            valid = self.combat_engine.living_enemies()
        
        if not valid:
            self.message_log.append("No valid targets!")
            return
        
        # Only one target — cast immediately without targeting UI
        if len(valid) == 1:
            self._execute_ability(actor, ability_id, valid[0])
            return
        
        self.targeting_mode = (ability_id, slot_index, ability, actor)
        self.targeting_valid_targets = valid
        self.targeting_hovered = valid[0]
        self.message_log.append(f"{ability.name} — click target (ESC to cancel)")

    def _execute_ability(self, actor, ability_id, target):
        """Cast an ability after targeting is done."""
        success, message = self.combat_engine.execute_ability(actor, ability_id, target)
        if success:
            self.message_log.append(message)
            self.targeting_mode = None
            self.targeting_valid_targets = []
            self.targeting_hovered = None
        else:
            self.message_log.append(message)
            # Don't exit targeting mode on failure - let them retry
    
    def _resolve_target(self, actor, ability, default_enemy):
        """
        Pick who an ability should hit, given its target_type.

          self   -> the actor
          party  -> every living ally (returned as a list)
          ally   -> smart pick, see below
          enemy  -> the default enemy

        The "ally" smart pick differs by what the ability does. A heal wants
        whoever is closest to dying. A buff wants whoever does not already
        have it - re-applying Fortitude to the same person while a companion
        stands unbuffed is the more likely misclick, and it also stops a buff
        from being wasted refreshing itself every turn.
        """
        allies = self.combat_engine.living_allies()
        target_type = getattr(ability, "target_type", None)

        if target_type == "self":
            return actor
        if target_type == "party":
            return allies or [actor]
        if target_type == "ally":
            if not allies:
                return actor
            if ability.effect_type in ("heal", "hot"):
                return min(allies,
                           key=lambda a: a.current_health / max(1, a.health))
            # Buff: prefer someone who doesn't already have it.
            unbuffed = [a for a in allies
                        if not self._has_effect(a, ability.ability_id)]
            pool = unbuffed or allies
            # Among equals, put a defensive buff on whoever is worst off.
            return min(pool,
                       key=lambda a: a.current_health / max(1, a.health))
        return default_enemy

    @staticmethod
    def _has_effect(combatant, effect_id):
        """True if this combatant already carries the given status effect."""
        effects = getattr(combatant, "_effects", None)
        if not callable(effects):
            return False
        return any(getattr(e, "effect_id", None) == effect_id
                   for e in effects())

    def update(self, dt):
        """Update combat."""
        if not self.combat_engine:
            self._init_combat()
        
        # Consumable cooldowns and buff timers tick for every party member,
        # not just the player - a companion's elixir has to expire too.
        # Ability-cast buffs (Fortitude, Battle Shout, ...) tick on the same
        # real-time clock via tick_seconds() - they run down at the same
        # rate whether the party is in combat or walking the overworld.
        for member in self.state_manager.get_party().members:
            if member.consumable_cooldown > 0:
                member.consumable_cooldown -= dt
            member.update_buff_timers(dt)
            if hasattr(member, "tick_seconds"):
                member.tick_seconds(dt)

        # Enemy buffs/debuffs (e.g. a boss's self-buff, or a debuff the party
        # landed on an enemy) tick the same way so they expire correctly
        # even across a long fight.
        if self.combat_engine:
            for foe in self.combat_engine.enemies:
                if hasattr(foe, "tick_seconds"):
                    foe.tick_seconds(dt)
        
        # Update combat state. Wrapped with a before/after combat_log
        # diff (same pattern the monster-turn branch below already uses)
        # because THIS is the real, single call site where
        # CombatEngine._check_combat_end()/_resolve_victory() actually
        # fire - not inside execute_ability itself. Victory resolves one
        # frame after the killing blow, once update(dt) notices no
        # living enemies remain, so victory/XP/gold/gear-drop/quest-item
        # lines were never making it into message_log regardless of
        # whether the killing blow was a player action or a monster
        # action - reported live as "quest items land in inventory but
        # no drop notification shows".
        log_before_update = len(self.combat_engine.combat_log)
        self.combat_engine.update(dt)
        new_update_lines = self.combat_engine.combat_log[log_before_update:]
        if new_update_lines:
            self.message_log.extend(new_update_lines)
        
        # If it's an enemy's turn, run their AI. Checks "not an ally" rather
        # than comparing against a single stored enemy, so multi-enemy fights
        # advance correctly.
        #
        # Pets are real bug found here (Kyle, 2026-09-06: "SHOULD have
        # pets"): is_ally(actor) returns True for a Pet (correctly - pets
        # ARE allies for targeting/threat purposes, see CombatEngine.
        # is_ally), which meant a pet's turn fell through to
        # _acting_member()'s "wait for human hotbar input" path below -
        # but pets have their OWN separate hotbar (pet.hotbar), not a
        # slot in the player's party hotbar UI, so a pet's turn had
        # nothing to click and would simply stall forever. Pets must
        # always be AI-controlled like a real hunter/warlock pet, never
        # waiting on human input - checked explicitly here BEFORE the
        # generic is_ally() branch so a pet's turn routes to
        # execute_pet_action() instead of the player's hotbar wait.
        actor = self.combat_engine.current_actor
        if (actor is not None and actor in self.combat_engine.pets
                and self.combat_engine.is_active):
            before = len(self.combat_engine.combat_log)
            self.combat_engine.execute_pet_action()
            new_lines = self.combat_engine.combat_log[before:]
            self.message_log.extend(new_lines)
            return

        if (actor is not None and not self.combat_engine.is_ally(actor)
                and self.combat_engine.is_active):
            before = len(self.combat_engine.combat_log)
            self.combat_engine.execute_monster_action()
            new_lines = self.combat_engine.combat_log[before:]
            self.message_log.extend(new_lines)
    
    # ------------------------------------------------------------------
    # STATUS EFFECT DISPLAY
    # ------------------------------------------------------------------
    # DoTs, HoTs, buffs and debuffs tick correctly and write to the combat
    # log, but until now there was no persistent on-screen indicator - the
    # only way to know a 4-turn Corruption was running was to scroll back
    # through log messages. Character/Monster expose get_effects_summary()
    # returning (name, turns_left, effect_type) tuples; this renders them as
    # a compact colour-coded row under each combatant's health bar.

    EFFECT_COLORS = {
        "dot": (210, 90, 90),      # red - damage over time
        "hot": (90, 200, 120),     # green - heal over time
        "buff": (110, 170, 235),   # blue - beneficial
        "debuff": (200, 150, 60),  # amber - detrimental
    }

    #: Bar colours for secondary resources, keyed by ResourceType.value.
    SECONDARY_RESOURCE_COLORS = {
        "static": (120, 200, 255),
        "insanity": (170, 80, 200),
        "solar_power": (255, 200, 60),
        "deathfire": (230, 90, 40),
        "souls": (150, 220, 200),
        "runes": (100, 180, 255),
        "felfury": (150, 240, 60),
        "combo": (255, 160, 60),
        "archery_points": (200, 180, 120),
        "vitality": (200, 60, 60),
    }

    #: Human-readable resource names for ability-cost display (Kyle: "cost
    #: 20" alone doesn't say which pool - Mana, Rage, Energy, or a
    #: class-specific one like Insanity/Static/Solar Power). Covers every
    #: ResourceType.value in the game; anything missing falls back to a
    #: title-cased version of the raw value in the call site.
    RESOURCE_DISPLAY_NAMES = {
        "mana": "Mana",
        "rage": "Rage",
        "energy": "Energy",
        "health": "Health",
        "static": "Static",
        "insanity": "Insanity",
        "solar_power": "Solar Power",
        "runes": "Runes",
        "rounds": "Rounds",
        "deathfire": "Deathfire",
        "souls": "Souls",
        "felfury": "Felfury",
        "archery_points": "Archery Points",
        "vitality": "Vitality",
    }

    def _draw_secondary_resource(self, screen, player, pos):
        """Draw the class's secondary resource bar. Returns height consumed."""
        from combat.abilities import get_class_secondary_resource
        secondary = get_class_secondary_resource(player.char_class)
        if not secondary or not hasattr(player, "get_resource"):
            return 0

        x, y = pos
        current = player.get_resource(secondary)
        maximum = player.get_resource_max(secondary)
        if not maximum:
            return 0

        label = secondary.value.replace("_", " ").title()
        color = self.SECONDARY_RESOURCE_COLORS.get(secondary.value, (180, 180, 180))
        self.renderer.draw_text(screen, f"{label}:", (x, y))
        self.renderer.draw_health_bar(screen, (x + 60, y), current, maximum,
                                      width=180, height=18, bar_color=color)
        return 35

    def _draw_status_effects(self, screen, combatant, pos, max_width=240):
        """Draw a row of active effect chips. Returns the height consumed so
        the caller can advance its layout cursor."""
        if not hasattr(combatant, "get_effects_summary"):
            return 0
        effects = combatant.get_effects_summary()
        if not effects:
            return 0

        x0, y0 = pos
        x, y = x0, y0
        chip_h = 20
        row_count = 1

        for name, turns, effect_type in effects:
            color = self.EFFECT_COLORS.get(effect_type, (170, 170, 170))

            # Abbreviate long names so chips stay readable - the turn counter
            # is the part that actually matters at a glance.
            short = name if len(name) <= 14 else name[:13] + "."
            label = f"{short} {turns}"
            text_w = self.renderer.font_normal.size(label)[0]
            chip_w = text_w + 10

            # Wrap to a second row rather than running off the panel.
            if x + chip_w > x0 + max_width and x > x0:
                x = x0
                y += chip_h + 3
                row_count += 1

            rect = pygame.Rect(x, y, chip_w, chip_h)
            # Dim fill, bright border/text - readable without dominating.
            pygame.draw.rect(screen, (color[0] // 4, color[1] // 4, color[2] // 4), rect)
            pygame.draw.rect(screen, color, rect, 1)
            self.renderer.draw_text(screen, label, (x + 5, y + 2), color=color)

            x += chip_w + 4

        return row_count * (chip_h + 3) + 4

    #: Tile size the enemy art is scaled against in combat - the same 48 the dungeon floor uses,
    #: so a creature is about the size in a fight that it was on the tile you walked into. This
    #: was 34 while the art could overrun the combat log; now that the clamp below guarantees the
    #: strip stays inside its budget, a boss can ask for its full 4 tiles and simply get trimmed
    #: to whatever is left. Trash goes from 58px to 82px, which is the difference between a
    #: thumbnail and a creature you can actually read.
    #: 40, was 48. Kyle, 2026-10-31: "shift the enemy stuff up... and reduce the sprite size
    #: slightly." Everything below the enemy strip is positioned off its bottom pixel, so this
    #: and the y=8 start below are both really gifts to the combat log.
    ENEMY_ART_TILE = 40

    #: Vertical room the combat log needs before it starts overlapping the hotbar: the gold
    #: "Combat Log" heading plus the MINIMUM three wrapped lines the log will shrink to before
    #: it refuses to shrink further (see the clamp in render()). This used to reserve eight,
    #: which is what the log wanted rather than what it needs, and the difference was being
    #: taken out of the creature art for no gain - the log then drew its eight lines straight
    #: under the party cards anyway.
    LOG_MIN_H = 25 + 3 * 25 + 10 + 20

    def _draw_enemy_strip(self, screen):
        """
        Enemies laid out side by side across the top of the screen, each in
        their own name-plate + bar card (FF Mythic Quest reference layout:
        "Hot Wings" / "Hot Wings" side by side up top). Replaces the old
        stacked right-side column so a multi-enemy pull reads left-to-right
        instead of top-to-bottom.
        """
        enemies = self.combat_engine.enemies
        if not enemies:
            return 190  # nothing to draw - fall back to the old fixed value

        card_w = 260
        card_gap = 20
        total_w = len(enemies) * card_w + (len(enemies) - 1) * card_gap
        start_x = max(20, (SCREEN_WIDTH - total_w) // 2)
        y = 8          # was 20 - "shift the enemy stuff up" (Kyle, 2026-10-31)
        max_bottom = y  # tracks the lowest pixel any card actually reaches

        for i, foe in enumerate(enemies):
            x = start_x + i * (card_w + card_gap)
            alive = foe.is_alive()
            is_acting = self.combat_engine.current_actor is foe

            if not alive:
                name_color = (110, 110, 110)
                suffix = "  (dead)"
            elif is_acting:
                name_color = COLOR_GOLD
                suffix = "  <-"
            else:
                name_color = COLOR_RED
                suffix = ""

            # Name plate, centered over the card.
            #
            # ONE LINE, NOT TWO. Kyle, 2026-10-31: "we could have something like Boss Name (lvl x)
            # which would completely remove an additional layer." The level used to sit on its own
            # line under the name, and everything below this strip - bars, status chips, creature
            # art, the combat log - is positioned off the bottom pixel the card reports, so that
            # line cost 20px to every fight on screen whether or not the fight needed it. A boss
            # with status effects is exactly where the strip runs out of room and the art gets
            # scaled down, so the 20px is worth more there than anywhere else.
            self.renderer.draw_text(screen, f"{foe.name} (Lvl {foe.level}){suffix}",
                                    (x + card_w // 2, y),
                                    size="normal", color=name_color, center=True)

            bar_y = y + 22
            self.renderer.draw_health_bar(screen, (x, bar_y),
                                          max(0, foe.current_health), foe.max_health,
                                          width=card_w, height=16,
                                          bar_color=COLOR_GREEN if alive else (70, 70, 70))

            card_bottom = bar_y + 22

            # Mana bar - only for casters (max_mana > 0). Thinner than the
            # HP bar and no numeric overlay so a row of mixed melee/caster
            # enemies doesn't get visually noisy; the color read (full vs
            # drained blue sliver) is the point, not exact numbers.
            if getattr(foe, "max_mana", 0) > 0:
                mana_y = card_bottom
                self.renderer.draw_health_bar(screen, (x, mana_y),
                                              max(0, foe.current_mana), foe.max_mana,
                                              width=card_w, height=8,
                                              bar_color=COLOR_BLUE if alive else (60, 60, 70),
                                              show_text=False)
                card_bottom = mana_y + 12

            if alive:
                effects_h = self._draw_status_effects(screen, foe, (x, card_bottom), max_width=card_w)
                card_bottom += effects_h

            # THE CREATURE ITSELF. Combat drew no creature art at all - a fight was two name
            # plates and some bars - so this is the first place the player actually sees what
            # they are fighting. Under the card rather than over it, so the bars stay the thing
            # you read at a glance and the art is what you look at between turns. A dead foe is
            # greyed rather than removed, so the strip does not reflow mid-fight.
            #
            # monster_type, NOT "template". Monster.__init__ stores the templates.json key as
            # monster_type; there is no .template. The first version of this line read .template
            # via getattr and so passed None for every enemy in the game - name rules still
            # fired, so most creatures looked right, but anything that resolves by stat template
            # fell through to DEFAULT and drew as a human bandit IN COMBAT ONLY, while the same
            # creature drew correctly on the dungeon floor two seconds earlier. qa_creature_sprites
            # now asserts the attribute exists so renaming it breaks a check instead of the art.
            art = get_creature_sprite(foe.name, getattr(foe, "monster_type", None),
                                      self.ENEMY_ART_TILE, bool(getattr(foe, "is_boss", False)))
            if art is not None:
                # THE ART MUST NOT COST THE COMBAT LOG ITS SPACE. Everything below this strip is
                # positioned off the bottom pixel it reports, and the log is a fixed-height block
                # sitting directly above the hotbar. Before there was any art the strip bottomed
                # out around y=160 and the log cleared the hotbar by ~90px; a 4-tile boss plus two
                # rows of status chips eats all of that and draws the log underneath the buttons.
                # So the art gets whatever room is genuinely left and is scaled down to fit it,
                # rather than a fixed size that happens to fit the cases I looked at.
                # The art must leave the log its MINIMUM. Everything under the enemy strip is
                # positioned off card_bottom, and the log now ends at the party cards rather
                # than running under them, so the real ceiling is the party strip - not the
                # hotbar, which is another card-height further down.
                room = self._party_strip_top() - self.LOG_MIN_H - card_bottom - 10
                if art.get_height() > room:
                    if room < 24:
                        art = None          # no honest room at all - bars beat a smear
                    else:
                        k = room / art.get_height()
                        art = pygame.transform.smoothscale(
                            art, (max(1, round(art.get_width() * k)), max(1, round(room))))
            if art is not None:
                if not alive:
                    # 90 is 35% brightness, which on this screen's near-black panel left a dead
                    # foe as a barely-visible smudge. Dead should read as drained, not deleted.
                    art = art.copy()
                    art.fill((125, 125, 135, 255), special_flags=pygame.BLEND_RGBA_MULT)
                art_rect = art.get_rect(midtop=(x + card_w // 2, card_bottom + 6))
                screen.blit(art, art_rect)
                card_bottom = art_rect.bottom + 4

            max_bottom = max(max_bottom, card_bottom)

        return max_bottom

    def _render_ability_tooltip(self, screen, ability, pos):
        """Hover tooltip for an ability. ONE implementation, in ui/ability_tooltip.py -
        this used to be a 40-line copy of the same box drawn in two other screens.
        """
        from ui.ability_tooltip import draw_ability_tooltip
        draw_ability_tooltip(self.renderer, screen, ability, pos,
                             getattr(self.state_manager, "player", None))

    def _draw_stance_selector(self, screen, player):
        """Warrior-only stance buttons on the right edge (see
        combat/stances.py). player here is whatever _acting_member()
        resolved to in render() - "whoever's turn it is", not necessarily
        the hero, matching how the hotbar above it already works for any
        party member's turn. Draws nothing for the other 8 classes since
        current_stance is None for them.
        """
        if getattr(player, "current_stance", None) is None:
            return

        from combat.stances import STANCES, get_stance
        for stance_id, rect in self.stance_positions.items():
            stance = STANCES[stance_id]
            usable = player.can_use_stance(stance_id)
            is_current = player.current_stance == stance_id

            if is_current:
                bg, border = (60, 50, 20), COLOR_GOLD
            elif usable:
                bg, border = (30, 30, 40), COLOR_WHITE
            else:
                bg, border = (20, 20, 20), (60, 60, 60)  # locked - not this level yet

            pygame.draw.rect(screen, bg, rect)
            pygame.draw.rect(screen, border, rect, 2 if is_current else 1)

            label = stance["name"]
            if not usable:
                label += f" (Lv{stance['level_req']})"
            text_color = COLOR_WHITE if usable else (100, 100, 100)
            self.renderer.draw_text(screen, label, (rect.x + 8, rect.y + 11),
                                    size="normal", color=text_color)

    def _hotbar_panel_top(self):
        """The real top edge of the hotbar panel, computed from the actual
        button rects rather than a guessed constant. Single source of truth
        for anything that needs to sit just above the hotbar (party strip,
        combat log sizing) - was two separate hardcoded numbers (this and
        the old SCREEN_HEIGHT-180 in _draw_party_strip) that drifted apart
        the moment the panel's real height changed, causing the party
        strip to overlap the hotbar (Kyle's screenshot)."""
        if not self.hotbar_positions:
            return SCREEN_HEIGHT - 170
        return min(r.top for r in self.hotbar_positions) - 10

    PARTY_CARD_H = 140

    def _party_strip_top(self):
        """The top edge of the party cards, or the hotbar's top when there are none.

        The combat log is drawn ABOVE this and has to stop here. It used to draw a fixed eight
        lines from wherever the enemy strip ended, with no idea the party cards existed, so a
        full party simply covered the bottom half of the log (Kyle, 2026-10-31: "we loose a lot
        of text when this happens"). Same single-source-of-truth argument as
        _hotbar_panel_top right above - a second hardcoded number here is how those two drifted
        apart last time.
        """
        party = self.state_manager.get_party()
        if not party or not party.members:
            return self._hotbar_panel_top()
        return self._hotbar_panel_top() - 10 - self.PARTY_CARD_H

    def _draw_party_strip(self, screen, acting):
        """
        Party cards laid out horizontally, sitting directly above the
        hotbar - mirrors the "Ryu / Phoebe" name+bar boxes sitting right
        above the command menu in the reference screenshot. Each card shows
        name, HP, resource, and a front/back row indicator so positioning
        is readable at a glance without needing a legend.
        """
        party = self.state_manager.get_party()
        members = party.members
        if not members:
            return

        from entities.party import FRONT_ROW
        from combat.abilities import get_class_resource, get_class_secondary_resource, ResourceType

        strip_bottom = self._hotbar_panel_top() - 10  # clears the real hotbar panel top with a small gap
        card_h = self.PARTY_CARD_H
        card_gap = 12
        card_w = min(240, (SCREEN_WIDTH - 40 - (len(members) - 1) * card_gap) // len(members))
        total_w = len(members) * card_w + (len(members) - 1) * card_gap
        start_x = max(20, (SCREEN_WIDTH - total_w) // 2)
        y = strip_bottom - card_h

        for i, member in enumerate(members):
            x = start_x + i * (card_w + card_gap)
            is_acting = member is acting and self._acting_member() is not None
            is_front = getattr(member, "row", FRONT_ROW) == FRONT_ROW

            card_rect = pygame.Rect(x, y, card_w, card_h)

            # Front/back row visual distinction: front row cards sit flush
            # with a warm/brighter border and a slightly raised look (tanks
            # up close); back row cards get a cooler border and are inset
            # a few px, reading as "standing further back" without needing
            # a legend or text label.
            if is_front:
                border_color = (200, 130, 60) if not is_acting else COLOR_GOLD
                fill = (42, 32, 24)
                inset = 0
            else:
                border_color = (70, 110, 170) if not is_acting else COLOR_GOLD
                fill = (24, 30, 42)
                inset = 6

            card_rect = pygame.Rect(x + inset, y + inset, card_w - inset * 2, card_h - inset * 2)

            if not member.is_alive():
                fill = (30, 30, 30)
                border_color = (90, 90, 90)

            pygame.draw.rect(screen, fill, card_rect)
            pygame.draw.rect(screen, border_color, card_rect, 3 if is_acting else 2)

            tx = card_rect.x + 8
            ty = card_rect.y + 6

            name_color = (120, 120, 120) if not member.is_alive() else (COLOR_GREEN if is_acting else COLOR_WHITE)
            row_tag = "\u25b2 FRONT" if is_front else "\u25bc BACK"
            row_color = (200, 130, 60) if is_front else (110, 150, 210)

            # Name and row tag get their own lines (rather than squeezed
            # side by side) so neither gets clipped or overlaps the next
            # card at small card widths (4-5 person parties).
            self.renderer.draw_text(screen, member.name, (tx, ty), font_size=16, color=name_color)
            ty += 18
            self.renderer.draw_text(screen, row_tag, (tx, ty), font_size=13, color=row_color)
            ty += 16

            bar_w = card_rect.width - 16

            # HP bar - numbers shown (show_text=True) so you can read exact
            # current/max at a glance instead of eyeballing bar length.
            self.renderer.draw_health_bar(screen, (tx, ty), member.current_health,
                                          member.health, width=bar_w, height=16,
                                          bar_color=COLOR_GREEN, show_text=True)
            ty += 19

            resource = get_class_resource(member.char_class, member)
            secondary = get_class_secondary_resource(member.char_class)
            pools = {
                ResourceType.MANA: (member.current_mana, member.mana, COLOR_BLUE, "Mana"),
                ResourceType.RAGE: (member.current_rage, member.max_rage, COLOR_RED, "Rage"),
                ResourceType.ENERGY: (member.current_energy, member.max_energy, COLOR_YELLOW, "Energy"),
            }

            def draw_resource_bar(rtype):
                """Draw one resource's bar with its name labeled on the bar
                itself (Kyle: "it should state WHAT resource is consumed") -
                covers both the primary pool (mana/rage/energy, via the
                fixed dict above) and any secondary/dict-backed pool (e.g.
                Stormbringer's Static, Primalist's Rage-as-secondary) via
                get_resource/get_resource_max, which already handles both
                storage shapes uniformly."""
                nonlocal ty
                if rtype in pools:
                    current, maximum, color, label = pools[rtype]
                else:
                    current = member.get_resource(rtype) if hasattr(member, "get_resource") else 0
                    maximum = member.get_resource_max(rtype) if hasattr(member, "get_resource_max") else 0
                    color = self.SECONDARY_RESOURCE_COLORS.get(
                        getattr(rtype, "value", rtype), COLOR_WHITE)
                    label = getattr(rtype, "value", str(rtype)).replace("_", " ").title()
                if not maximum:
                    return
                self.renderer.draw_text(screen, label, (tx, ty), font_size=11, color=color)
                self.renderer.draw_health_bar(screen, (tx, ty + 12), current, maximum,
                                              width=bar_w, height=14,
                                              bar_color=color, show_text=True)
                ty += 29

            if resource:
                draw_resource_bar(resource)
            if secondary and secondary != resource:
                draw_resource_bar(secondary)

            # Buff/debuff/DoT/HoT row - real dedicated space now (was getting
            # squeezed into leftover px before and had nowhere to actually
            # draw). Wraps to a second row via _draw_buff_icons_mini's own
            # logic if needed; card_h has headroom for ~2 rows of chips.
            if not member.is_alive():
                self.renderer.draw_text(screen, "DOWN", (tx, ty), font_size=13, color=(200, 60, 60))
            else:
                self._draw_buff_icons_mini(screen, member, (tx, ty))

    def render(self, screen):
        """Draw combat screen with redesigned layout."""
        if not self.combat_engine:
            return

        # Targeting mode replaces the whole screen with a dedicated
        # highlight-and-click overlay - this MUST come before anything else
        # or the normal (non-clickable) roster draws on top of it and every
        # click lands on dead space instead of a target.
        if self.targeting_mode:
            self._render_targeting(screen)
            return

        # `player` here means "whoever is acting" - kept for the combat log
        # color-matching below, but the old dedicated left-side panel for
        # them is gone; they're just highlighted within the bottom party strip.
        player = self._acting_member() or self.state_manager.player
        living_enemies = self.combat_engine.living_enemies()
        enemy = living_enemies[0] if living_enemies else self.combat_engine.enemy

        # Background fills the whole screen first, everything else draws on
        # top. Falls back to nothing (default screen fill, whatever that is
        # upstream) if no background resolved - a missing/corrupt art file
        # degrades quietly rather than crashing combat.
        if self.combat_background:
            screen.blit(self.combat_background, (0, 0))

        # ===== TOP: ENEMY STRIP (horizontal, centered - FF Mythic Quest style) =====
        # Enemies sit side by side across the top of the screen instead of
        # stacked in a right-side column, matching the reference layout
        # (name plate + bar above each foe, left to right).
        enemy_strip_bottom = self._draw_enemy_strip(screen)

        # ===== CENTER: COMBAT LOG =====
        # Use the actual available width between the two side panels instead
        # of a fixed 400px box, and word-wrap instead of truncating with "..."
        # so messages don't get cut off mid-sentence.
        log_left_edge = 40
        log_right_edge = SCREEN_WIDTH - 40
        log_width = log_right_edge - log_left_edge
        center_x = log_left_edge
        # The log used to start at a hardcoded y=190, sized for an enemy
        # with zero or one status effect. A heavily-buffed/debuffed foe's
        # effect chips wrap to a 2nd/3rd row and grow well past that fixed
        # point (confirmed: 3+ stacked effects on a 260px-wide card push
        # past y=175), silently drawing "Combat Log" and its first lines
        # underneath the enemy card. _draw_enemy_strip now returns the
        # actual bottom-most pixel it used, across every enemy card, so the
        # log always starts below whatever is really on screen instead of
        # guessing a fixed offset.
        center_y = enemy_strip_bottom + 20

        # Translucent backing panel behind the log text only. Enemy cards and
        # the hotbar already draw their own opaque backgrounds, but the log
        # text itself was drawn directly onto whatever's behind it - fine
        # against a flat fill, unreadable against a busy background image.
        # How many lines genuinely fit between the enemy strip and the party cards. Clamped so
        # a cramped layout still shows a few lines rather than none, and never more than the 8
        # this was always written for.
        LOG_LINE_H = 25
        room = self._party_strip_top() - (center_y + 40) - 6
        max_visible_lines = max(3, min(8, room // LOG_LINE_H))

        if self.combat_background:
            log_panel_h = 25 + max_visible_lines * LOG_LINE_H + 10
            log_panel = pygame.Rect(log_left_edge - 10, center_y - 8, log_width + 20, log_panel_h)
            panel_surf = pygame.Surface(log_panel.size, pygame.SRCALPHA)
            panel_surf.fill((10, 10, 15, 165))
            screen.blit(panel_surf, log_panel.topleft)

        self.renderer.draw_text(screen, "Combat Log", (center_x, center_y), size="large", color=COLOR_GOLD)
        center_y += 40
        
        # Wrap each message to fit the available width, then take the last N
        # wrapped lines so the log still shows recent history even if some
        # messages spanned multiple lines.
        all_wrapped_lines = []
        for msg in self.message_log:
            if msg.startswith(player.name):
                msg_color = COLOR_GREEN
            elif msg.startswith(enemy.name):
                msg_color = COLOR_RED
            else:
                msg_color = COLOR_WHITE

            for line in self.renderer.wrap_text(msg, log_width):
                all_wrapped_lines.append((line, msg_color))

        log_start = max(0, len(all_wrapped_lines) - max_visible_lines)
        for line, msg_color in all_wrapped_lines[log_start:]:
            self.renderer.draw_text(screen, line, (center_x, center_y), size="normal", color=msg_color)
            center_y += 25
        
        # ===== PARTY STRIP: sits directly above the hotbar (Ryu/Phoebe style) =====
        self._draw_party_strip(screen, player)

        # Hotbar background - sized to actually contain the two button rows
        # plus a small margin, rather than the old fixed 160px box. The old
        # box was tall enough that row 2 buttons poked out above its own
        # top edge (real measured overhang: ~35px) while also being wide
        # enough to leave a big dead black strip on the right where nothing
        # was drawn at all (Kyle's screenshot) - this now hugs the real
        # button bounds (hotbar + extra slots + stance buttons) instead.
        panel_top = self._hotbar_panel_top()
        panel_bottom = max(r.bottom for r in self.hotbar_positions) + 10
        panel_right = max(r.right for r in self.stance_positions.values()) + 15 \
            if self.stance_positions else max(r.right for r in self.extra_slot_positions) + 15
        hotbar_bg = pygame.Rect(20, panel_top, panel_right - 20, panel_bottom - panel_top)
        pygame.draw.rect(screen, COLOR_DARK_GRAY, hotbar_bg)
        pygame.draw.rect(screen, COLOR_WHITE, hotbar_bg, 2)

        # Thin divider between the real hotbar and the extra-slot block so
        # the two read as related-but-distinct at a glance, without needing
        # a text label to explain it.
        if self.extra_slot_positions:
            divider_x = min(r.left for r in self.extra_slot_positions) - 12
            pygame.draw.line(screen, (90, 90, 90),
                              (divider_x, panel_top + 5), (divider_x, panel_bottom - 5), 1)
        
        # Hotbar buttons
        from entities.consumable import Consumable
        for i, rect in enumerate(self.hotbar_positions):
            hotbar_content = player.hotbar[i]
            
            if hotbar_content:
                # Check if it's a Consumable or ability
                if isinstance(hotbar_content, Consumable):
                    # It's a consumable
                    consumable = hotbar_content
                    
                    # Button color based on cooldown
                    if player.consumable_cooldown > 0:
                        btn_color = (60, 40, 40)  # Red (on cooldown)
                    else:
                        btn_color = (40, 60, 40)  # Green (ready)
                    
                    pygame.draw.rect(screen, btn_color, rect)
                    pygame.draw.rect(screen, COLOR_WHITE, rect, 1)
                    
                    # Consumable name - wrapped
                    name_lines = self.renderer.wrap_text(consumable.name, rect.width - 10)
                    name_y = rect.y + 5
                    for line in name_lines[:2]:
                        self.renderer.draw_text(screen, line, (rect.x + 5, name_y), size="normal")
                        name_y += 18
                    
                    # Show quantity
                    qty_text = f"x{consumable.quantity}"
                    self.renderer.draw_text(screen, qty_text, (rect.x + 8, rect.y + 35), color=COLOR_GOLD, size="normal")
                    
                    # Hotkey label
                    hotkey = self._hotbar_slot_to_key_label(i)
                    self.renderer.draw_text(screen, hotkey, (rect.x + rect.width - 40, rect.y + rect.height - 25), size="normal", color=COLOR_BLUE)
                else:
                    # It's an ability
                    ability_id = hotbar_content
                    ability = player.ability_book.get_ability(ability_id)
                    if ability is None:
                        # Stale hotbar id (ability no longer in the book - old save, respec, fixed-kit recruit):
                        # draw it as an empty slot instead of crashing the render loop.
                        pygame.draw.rect(screen, (30, 30, 36), rect)
                        pygame.draw.rect(screen, (90, 90, 90), rect, 1)
                        continue

                    # Button color based on availability - is_usable_by()
                    # also checks form-gating (Mangle-style abilities that
                    # require Bear/Cat Form), not just cooldown, so an
                    # out-of-form ability correctly shows red instead of
                    # looking castable and then silently failing on click.
                    if ability.is_usable_by(player):
                        btn_color = (40, 60, 40)  # Dark green
                    else:
                        btn_color = (60, 40, 40)  # Dark red (on cooldown or wrong form)
                    
                    pygame.draw.rect(screen, btn_color, rect)
                    pygame.draw.rect(screen, COLOR_WHITE, rect, 1)
                    
                    # Ability name - wrapped to fit inside the button (80px wide),
                    # since names like "Lightning Bolt" overflow a single line
                    name_lines = self.renderer.wrap_text(ability.name, rect.width - 10)
                    name_y = rect.y + 5
                    for line in name_lines[:2]:  # cap at 2 lines to avoid overflowing into cost/cooldown text
                        self.renderer.draw_text(screen, line, (rect.x + 5, name_y), size="normal")
                        name_y += 18
                    
                    # Show cost or cooldown
                    if not ability.is_available():
                        cooldown_text = f"{ability.turns_remaining} turns"
                        self.renderer.draw_text(screen, cooldown_text, (rect.x + 8, rect.y + 35), color=COLOR_RED, size="normal")
                    elif not ability.is_form_ready(player):
                        self.renderer.draw_text(screen, "Wrong form", (rect.x + 8, rect.y + 35), color=COLOR_RED, size="normal")
                    else:
                        # Resource name shown alongside the number (was just
                        # "Cost: 20" with no indication of which pool -
                        # ambiguous for every dual-resource class, e.g.
                        # Cultist's Wrath of the Black Empire costs Insanity
                        # while Blade of the Empire costs Mana, and both used
                        # to render identically here).
                        #
                        # Uses _effective_resource_type (not the raw static
                        # ability.resource_type) so a multi-form ability like
                        # Druid Swipe correctly shows "Rage" while the caster
                        # is in Bear Form and "Energy" while in Cat Form,
                        # instead of always showing whatever the JSON's
                        # single hardcoded resource_type happens to be - the
                        # same static-label bug that made Swipe uncastable
                        # in Bear Form in the first place (see
                        # combat/abilities.py's _effective_resource_type).
                        effective_rt = ability._effective_resource_type(player)
                        resource_label = self.RESOURCE_DISPLAY_NAMES.get(
                            getattr(effective_rt, "value", effective_rt),
                            str(getattr(effective_rt, "value", effective_rt)).replace("_", " ").title()
                        )
                        # Talented cost, not base - a cost-reduction talent must be
                        # visible here or it looks like it does nothing.
                        _caster = getattr(self.state_manager, "player", None)
                        _cost = ability.talented_cost(_caster) if _caster is not None else ability.cost
                        cost_text = f"Cost: {_cost} {resource_label}"
                        self.renderer.draw_text(screen, cost_text, (rect.x + 8, rect.y + 35), color=COLOR_GOLD, size="normal")
                    
                    # Hotkey label (large in corner) - shows the actual keybind:
                    # 1-9,0 for the bottom row, Shift+1-9,0 for the top row
                    hotkey = self._hotbar_slot_to_key_label(i)
                    self.renderer.draw_text(screen, hotkey, (rect.x + rect.width - 40, rect.y + rect.height - 25), size="normal", color=COLOR_BLUE)
            else:
                # Empty slot
                pygame.draw.rect(screen, (30, 30, 30), rect)
                pygame.draw.rect(screen, (80, 80, 80), rect, 1)
                hotkey = self._hotbar_slot_to_key_label(i)
                self.renderer.draw_text(screen, hotkey, (rect.x + 15, rect.y + 30), size="normal", color=COLOR_BLUE)

        # Extra (click-only) slot buttons - same visuals as the real hotbar
        # minus the keybind label in the corner (there's no key bound to
        # these), filling the space that used to sit empty between the
        # hotbar and the stance buttons.
        from entities.consumable import Consumable as _Consumable
        for i, rect in enumerate(self.extra_slot_positions):
            slot_content = player.extra_slots[i] if i < len(player.extra_slots) else None

            if slot_content:
                if isinstance(slot_content, _Consumable):
                    consumable = slot_content
                    btn_color = (60, 40, 40) if player.consumable_cooldown > 0 else (40, 60, 40)
                    pygame.draw.rect(screen, btn_color, rect)
                    pygame.draw.rect(screen, COLOR_WHITE, rect, 1)
                    name_lines = self.renderer.wrap_text(consumable.name, rect.width - 10)
                    name_y = rect.y + 5
                    for line in name_lines[:2]:
                        self.renderer.draw_text(screen, line, (rect.x + 5, name_y), size="normal")
                        name_y += 18
                    self.renderer.draw_text(screen, f"x{consumable.quantity}",
                                            (rect.x + 8, rect.y + 35), color=COLOR_GOLD, size="normal")
                else:
                    ability_id = slot_content
                    ability = player.ability_book.get_ability(ability_id)
                    if ability:
                        btn_color = (40, 60, 40) if ability.is_usable_by(player) else (60, 40, 40)
                        pygame.draw.rect(screen, btn_color, rect)
                        pygame.draw.rect(screen, COLOR_WHITE, rect, 1)
                        name_lines = self.renderer.wrap_text(ability.name, rect.width - 10)
                        name_y = rect.y + 5
                        for line in name_lines[:2]:
                            self.renderer.draw_text(screen, line, (rect.x + 5, name_y), size="normal")
                            name_y += 18
                        if not ability.is_available():
                            self.renderer.draw_text(screen, f"{ability.turns_remaining} turns",
                                                    (rect.x + 8, rect.y + 35), color=COLOR_RED, size="normal")
                        elif not ability.is_form_ready(player):
                            self.renderer.draw_text(screen, "Wrong form",
                                                    (rect.x + 8, rect.y + 35), color=COLOR_RED, size="normal")
            else:
                # Empty extra slot - slightly different border tint than an
                # empty hotbar slot so it's visually clear this one has no
                # keybind to fall back on.
                pygame.draw.rect(screen, (30, 30, 35), rect)
                pygame.draw.rect(screen, (90, 80, 60), rect, 1)

        self._draw_stance_selector(screen, player)

        # Real hover tooltip for hotbar abilities - per Kyle's ask, same
        # shared Ability.get_tooltip_lines() cast_screen.py's tooltip
        # uses, so the wording/numbers match wherever it's shown. Only
        # drawn while not in targeting mode (that mode's own hover/click
        # UI already owns the screen at that point).
        if self.hovered_ability is not None and not self.targeting_mode:
            self._render_ability_tooltip(screen, self.hovered_ability, self.mouse_pos)
        
        # Combat over overlay. Result text is now measured and truly
        # centered (the old fixed "-80" offset only centered "Victory!" by
        # coincidence and drifted noticeably on "Defeat!"), and EXP/loot each
        # get their own boxed callout side by side, matching the mockup
        # instead of stacking bare text down the middle of the screen.
        if not self.combat_engine.is_active:
            # Dim the whole screen first. This overlay used to draw straight
            # on top of the live combat UI, so the party unit frames, their
            # health/mana/rage bars and the enemy art all showed THROUGH the
            # result text - "Vendor trash: 1" and "Click to return to
            # overworld" landed on top of a unit frame and both became hard
            # to read (Kyle: "victory screen overlaps weirdly"). Nothing
            # behind this is interactive once combat is over, so dimming it
            # costs nothing and makes the result unambiguous.
            scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            scrim.fill((8, 8, 12, 205))
            screen.blit(scrim, (0, 0))

            result = "Victory!" if player.is_alive() else "Defeat!"
            color = COLOR_GREEN if player.is_alive() else COLOR_RED
            result_width = self.renderer.font_large.size(result)[0]
            result_center_y = SCREEN_HEIGHT // 2 - 100

            box_y = result_center_y + 50
            box_w, box_h = 260, 70
            gap = 20
            exp_earned = getattr(self.combat_engine, "exp_earned", 0)
            loot = getattr(self.combat_engine, "loot_dropped", None)
            # Multi-mob pulls roll loot once PER enemy, so show every drop (not just the last).
            loots = list(getattr(self.combat_engine, "loot_gained", None) or ([loot] if loot else []))
            loot_h = box_h if len(loots) <= 1 else 38 + 20 * min(5, len(loots)) + (20 if len(loots) > 5 else 0)

            # Solid panel behind the whole result block. The scrim alone was
            # not enough: a dimmed unit frame still sits directly behind the
            # coin/trash and "click to return" lines, and dim-grey bars under
            # grey text is exactly the tangle this is meant to stop. Sized
            # from the same numbers the content below uses, so it cannot
            # drift out of step with a longer loot list.
            # How many callout boxes will actually be drawn - a defeat rolls
            # no EXP and usually no loot, so reserving a box's worth of
            # height there left a visible hole between "Defeat!" and the
            # prompt.
            boxes_shown = int(bool(player.is_alive())) + int(bool(loots))
            content_h = max(box_h, loot_h) if boxes_shown else 0

            panel_w = max(680, (box_w * 2 + gap) + 120)
            panel_top = result_center_y - 30
            panel_bottom = box_y + content_h + 92
            panel = pygame.Rect(SCREEN_WIDTH // 2 - panel_w // 2, panel_top,
                                panel_w, panel_bottom - panel_top)
            self.renderer.draw_rect(screen, panel, (18, 18, 24))
            self.renderer.draw_rect(screen, panel, color, fill=False)

            self.renderer.draw_text(
                screen, result,
                (SCREEN_WIDTH // 2 - result_width // 2, result_center_y),
                size="large", color=color)

            # Two side-by-side boxes when both exist; a single centered box
            # when only one applies (e.g. a defeat with no loot roll).
            if boxes_shown == 2:
                exp_box = pygame.Rect(SCREEN_WIDTH // 2 - box_w - gap // 2, box_y, box_w, box_h)
                loot_box = pygame.Rect(SCREEN_WIDTH // 2 + gap // 2, box_y, box_w, box_h)
            else:
                exp_box = pygame.Rect(SCREEN_WIDTH // 2 - box_w // 2, box_y, box_w, box_h)
                loot_box = exp_box

            if player.is_alive():
                self.renderer.draw_rect(screen, exp_box, (30, 30, 40))
                self.renderer.draw_rect(screen, exp_box, COLOR_GOLD, fill=False)
                exp_text = f"+{exp_earned} EXP"
                exp_text_w = self.renderer.font_large.size(exp_text)[0]
                self.renderer.draw_text(
                    screen, exp_text,
                    (exp_box.centerx - exp_text_w // 2, exp_box.y + 22),
                    size="large", color=COLOR_GOLD)

            if loots:
                shown = loots[:5]
                if len(loots) > 1:
                    loot_box = pygame.Rect(loot_box.x, loot_box.y, box_w + 60, loot_h)
                self.renderer.draw_rect(screen, loot_box, (30, 30, 40))
                self.renderer.draw_rect(screen, loot_box, shown[-1].get_rarity_color(), fill=False)
                self.renderer.draw_text(
                    screen, "Loot:" if len(loots) == 1 else f"Loot ({len(loots)}):",
                    (loot_box.x + 12, loot_box.y + 10), color=(180, 180, 180))
                ly = loot_box.y + 32
                for it in shown:
                    for line in self.renderer.wrap_text(it.name, loot_box.width - 24)[:1 if len(loots) > 1 else 2]:
                        self.renderer.draw_text(screen, line, (loot_box.x + 12, ly), color=it.get_rarity_color())
                        ly += 20
                if len(loots) > len(shown):
                    self.renderer.draw_text(screen, f"+{len(loots) - len(shown)} more (see log)", (loot_box.x + 12, ly), color=(150, 150, 150))

            if player.is_alive():
                bits = []
                coin = getattr(self.combat_engine, "copper_earned", 0)
                if coin:
                    bits.append(f"Coin: {format_coins(coin)}")
                trash_n = getattr(self.combat_engine, "trash_gained", 0)
                if trash_n:
                    bits.append(f"Vendor trash: {trash_n}")
                if bits:
                    line = "    ".join(bits)
                    lw = self.renderer.font_normal.size(line)[0]
                    self.renderer.draw_text(screen, line, (SCREEN_WIDTH // 2 - lw // 2, box_y + content_h + 18),
                                            color=(190, 190, 150))

            prompt = "Click to return to overworld"
            prompt_width = self.renderer.font_normal.size(prompt)[0]
            self.renderer.draw_text(
                screen, prompt,
                (SCREEN_WIDTH // 2 - prompt_width // 2, box_y + content_h + 56))

    def _draw_buff_icons_mini(self, screen, combatant, pos):
        """
        Tiny single-row buff strip for the persistent left-side party roster
        (as opposed to _draw_buff_icons, used in the bigger targeting-mode
        rows). Same border-color convention (gold=buff, purple=debuff,
        red=DoT, green=HoT), just smaller and single-row since roster space
        is tight.
        """
        effects = [e for e in combatant._effects()
                   if e.effect_type in (EffectType.BUFF, EffectType.DEBUFF,
                                        EffectType.DOT, EffectType.HOT)]
        if not effects:
            return

        icon_size = 12
        gap = 2
        x, y = pos
        for i, effect in enumerate(effects[:8]):
            rect = pygame.Rect(x + i * (icon_size + gap), y, icon_size, icon_size)
            if effect.effect_type == EffectType.BUFF:
                border = COLOR_GOLD
            elif effect.effect_type == EffectType.DEBUFF:
                border = (170, 100, 220)
            elif effect.effect_type == EffectType.DOT:
                border = COLOR_RED
            else:
                border = COLOR_GREEN
            pygame.draw.rect(screen, (30, 30, 30), rect)
            pygame.draw.rect(screen, border, rect, 1)

    def _draw_buff_icons(self, screen, combatant, top_right_pos):
        """
        Small icon strip showing active buffs/debuffs on a combatant, stacked
        under (well, starting at) top_right_pos and growing downward. No
        sprite art yet, so each icon is a colored square with the effect's
        first letter - buffs get a gold border (WoW convention: yellow-bordered
        buff icons), debuffs get a purple border (WoW: purple/red debuff
        icons), matching the visual language players already know.
        """
        effects = [e for e in combatant._effects()
                   if e.effect_type in (EffectType.BUFF, EffectType.DEBUFF,
                                        EffectType.DOT, EffectType.HOT)]
        if not effects:
            return

        icon_size = 22
        gap = 4
        x, y = top_right_pos
        for i, effect in enumerate(effects[:6]):  # cap at 6 so it can't overflow the row
            icon_x = x + (i % 3) * (icon_size + gap)
            icon_y = y + (i // 3) * (icon_size + gap)
            rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)

            if effect.effect_type == EffectType.BUFF:
                fill, border = (50, 45, 20), COLOR_GOLD
            elif effect.effect_type == EffectType.DEBUFF:
                fill, border = (45, 20, 50), (170, 100, 220)
            elif effect.effect_type == EffectType.DOT:
                fill, border = (50, 20, 20), COLOR_RED
            else:  # HOT
                fill, border = (20, 45, 25), COLOR_GREEN

            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, border, rect, 2)
            letter = effect.name[0].upper() if effect.name else "?"
            self.renderer.draw_text(screen, letter, (rect.x + 6, rect.y + 3),
                                    size="small", color=COLOR_WHITE)

    def _render_targeting(self, screen):
        """Render the targeting UI: highlight valid targets, store rects for hit-testing."""
        screen.fill((20, 20, 20))
        self._targeting_rects = []  # Track rects for hit-testing
        
        ability_id, slot_index, ability, actor = self.targeting_mode
        msg = f"◆ {ability.name} ◆  Click a target (ESC to cancel)"
        self.renderer.draw_text(screen, msg, (40, 30),
                                size="large", color=COLOR_GOLD)

        # Draw all combatants with highlighting for valid targets.
        # Row is 80px tall for easy clicking; the HP bar itself is a boxy
        # 26px-tall block (was a thin 20px strip) so it reads as a proper
        # health bar rather than a skinny line, while keeping the same
        # horizontal length. Name text is "small" - the "large" name label
        # was visually dominating a row that's mostly meant to show HP/buffs.
        y = 120
        for ally in self.combat_engine.allies:
            is_valid = ally in self.targeting_valid_targets
            is_hovered = ally is self.targeting_hovered
            color = COLOR_GOLD if is_hovered else (COLOR_GREEN if is_valid else COLOR_DARK_GRAY)
            rect = pygame.Rect(40, y, 400, 80)
            if is_valid:
                pygame.draw.rect(screen, (60, 80, 60), rect)  # green tint
                if is_hovered:
                    pygame.draw.rect(screen, COLOR_GOLD, rect, 3)  # gold border
            self.renderer.draw_text(screen, f"{ally.name}", (rect.x + 10, rect.y + 8),
                                    size="small", color=color)
            self.renderer.draw_text(screen, f"Lv {ally.level} {ally.char_class}",
                                    (rect.x + 10, rect.y + 26), size="small", color=color)
            self.renderer.draw_health_bar(screen, (rect.x + 10, rect.y + 46),
                                          ally.current_health, ally.health,
                                          width=280, height=26, bar_color=COLOR_GREEN)
            self._draw_buff_icons(screen, ally, (rect.x + 300, rect.y + 8))
            self._targeting_rects.append((ally, rect))
            y += 90  # Space for thicker rects

        y_enemies = 120
        for foe in self.combat_engine.enemies:
            is_valid = foe in self.targeting_valid_targets
            is_hovered = foe is self.targeting_hovered
            color = COLOR_GOLD if is_hovered else (COLOR_RED if is_valid else COLOR_DARK_GRAY)
            rect = pygame.Rect(SCREEN_WIDTH - 440, y_enemies, 400, 80)
            if is_valid:
                pygame.draw.rect(screen, (80, 40, 40), rect)  # red tint
                if is_hovered:
                    pygame.draw.rect(screen, COLOR_GOLD, rect, 3)  # gold border
            self.renderer.draw_text(screen, f"{foe.name}",
                                    (rect.x + 10, rect.y + 8), size="small", color=color)
            self.renderer.draw_text(screen, f"Lv {foe.level}",
                                    (rect.x + 10, rect.y + 26), size="small", color=color)
            self.renderer.draw_health_bar(screen, (rect.x + 10, rect.y + 46),
                                          foe.current_health, foe.max_health,
                                          width=280, height=26, bar_color=COLOR_RED)
            self._draw_buff_icons(screen, foe, (rect.x + 300, rect.y + 8))
            self._targeting_rects.append((foe, rect))
            y_enemies += 90  # Space for thicker rects

        # Instructions
        self.renderer.draw_text(screen,
                                "Click highlighted target • ESC to cancel",
                                (40, SCREEN_HEIGHT - 50),
                                size="small", color=COLOR_WHITE)
