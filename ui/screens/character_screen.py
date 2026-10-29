"""
Character creation screen.
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING
from config import COLOR_WHITE, COLOR_DARK_GRAY, COLOR_GOLD
from core.game_states import GameState
from core.save_system import SaveSystem
from entities.character import Character
from ui.screens.base_screen import BaseScreen
from ui.sprite_loader import get_npc_sprite
from world.race_registry import get_available_races, get_gender, sprite_base_path
from world.start_zones import get_available_starts, suggested_start_for_race


class CharacterCreationScreen(BaseScreen):
    """Character creation screen."""
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.save_system = SaveSystem()
        
        self.classes = [
            "Warrior", "Rogue", "Hunter", "Mage", "Warlock",
            "Priest", "Druid", "Shaman", "Paladin",
            # CoA classes with real, authored ability kits + talent trees
            # (see data/abilities/ and data/talents/). Any CoA class without
            # one stays unselectable - picking it would create a character
            # with an empty spellbook. Add a class here only once
            # tools/validate_class.py passes it, which checks that it builds,
            # learns abilities at 1/20/40/60, spends a full talent budget and
            # actually acts in a real fight.
            "Stormbringer", "Tinker", "Venomancer", "Primalist", "Runemaster", "Cultist", "Starcaller", "Sun Cleric",
            "Guardian",
            "Witch Hunter",
            "Templar",
            "Reaper",
            "Witch Doctor",
            "Ranger",
            "Pyromancer",
            "Necromancer",
            "Knight of Xoroth",
            "Felsworn",
            "Chronomancer",
            "Bloodmage",
            "Barbarian",
        ]
        self.selected_class = 0
        self.character_name = "Hero"
        self.created_character = None

        # Appearance selection (Kyle: "race + gender + options which we
        # can expand later"). Purely cosmetic - see Character.race/gender/
        # appearance_variant docstring - selection here just sets those
        # three fields, resolved to a real sprite via race_registry.
        self.available_races = get_available_races()
        self.selected_race_index = 0  # index into self.available_races
        # Where the character wakes up (world/start_zones.py). Race SUGGESTS this and never locks it -
        # see that module's docstring for why, given there is no true Horde/Alliance here.
        self.available_starts = get_available_starts()
        self.selected_start_index = 0
        self._start_touched = False   # once the player picks one, changing race stops overriding it
        self.selected_gender_index = 0  # index into the current race's .genders list
        self.selected_variant = 0  # index into the current gender's .variants list

        # Button positions - 5-column grid so the roster fits within
        # SCREEN_WIDTH without overflowing like a single row would. Rows are
        # derived from the class count, so adding CoA classes just adds rows.
        self.class_buttons = []
        columns = 5
        grid_start_x = 60
        grid_start_y = 170
        col_spacing = BUTTON_WIDTH + BUTTON_PADDING
        row_spacing = BUTTON_HEIGHT + BUTTON_PADDING
        for i, _ in enumerate(self.classes):
            row = i // columns
            col = i % columns
            btn = pygame.Rect(
                grid_start_x + (col * col_spacing),
                grid_start_y + (row * row_spacing),
                BUTTON_WIDTH,
                BUTTON_HEIGHT
            )
            self.class_buttons.append(btn)

        # Appearance controls sit in the strip between the class stat
        # preview box (draw_character_box: y=350..550) and the create
        # button - the natural gap there was only 20px (measured: box
        # bottom 550, old create button top 570), nowhere near enough for
        # a real control row, so the create button moves down to make
        # room rather than cramming controls into a gap that doesn't
        # exist. See create_button's own position below, computed to
        # leave appearance_y a genuine ~70px band.
        appearance_x = grid_start_x
        appearance_y = 560
        self.appearance_x = appearance_x
        self.appearance_y = appearance_y

        self.race_buttons = []
        race_btn_w = 90
        race_btn_h = 36
        for i, race in enumerate(self.available_races):
            self.race_buttons.append(pygame.Rect(
                appearance_x + i * (race_btn_w + 8), appearance_y, race_btn_w, race_btn_h
            ))

        self.gender_buttons = []  # rebuilt in _sync_gender_buttons since it depends on selected race
        self._sync_gender_buttons()

        # Preview + variant arrows sit to the right of race/gender on the
        # same row - preview is small (60x90) specifically so this whole
        # row stays under the ~160px vertical budget available. x position
        # computed from the real gender button count/width (mirrors
        # _sync_gender_buttons' math) rather than a guessed offset, so it
        # can't drift out of sync if a race gets a 3rd gender option later.
        gender_btn_w = 80
        max_genders = max((len(r.genders) for r in self.available_races), default=0)
        gender_block_w = max_genders * (gender_btn_w + 8)
        controls_after_gender_x = appearance_x + len(self.available_races) * (race_btn_w + 8) + 20 + gender_block_w + 20
        self.preview_rect = pygame.Rect(controls_after_gender_x, appearance_y - 10, 60, 90)
        self.variant_prev_button = pygame.Rect(self.preview_rect.right + 8, appearance_y + 20, 30, 30)
        self.variant_next_button = pygame.Rect(self.variant_prev_button.right + 8, appearance_y + 20, 30, 30)

        # START ZONE sits in the free span to the RIGHT of the appearance row rather than under it.
        # The vertical budget here is genuinely spent - the preview box runs to y=550, this row starts
        # at 560, and the Create button is at SCREEN_HEIGHT-70 - so another row would collide. The
        # appearance controls end at variant_next_button.right (902 with five races), which leaves
        # ~358px, and two 120px buttons fit it with room for the label.
        start_x = self.variant_next_button.right + 28
        start_btn_w, start_btn_h = 120, 36
        self.start_x = start_x
        self.start_buttons = [
            pygame.Rect(start_x + i * (start_btn_w + 8), appearance_y, start_btn_w, start_btn_h)
            for i, _ in enumerate(self.available_starts)
        ]
        if self.start_buttons and self.start_buttons[-1].right > SCREEN_WIDTH - 12:
            # Loud rather than clipped. A third start, or a sixth race, pushes this off-screen and the
            # row needs rethinking - silently drawing a button nobody can reach is the worse outcome.
            raise ValueError(
                f"start-zone buttons overflow SCREEN_WIDTH ({self.start_buttons[-1].right} > "
                f"{SCREEN_WIDTH - 12}) - the appearance row is full; wrap it before adding more")

        self.create_button = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        
        # Back button
        self.back_button = pygame.Rect(20, 20, 100, 50)

    def _suggest_start(self):
        """Move the start to the one this race suggests - unless the player has already chosen one.

        A player who deliberately picked Deathknell and then cycled races to look at the sprites should
        not silently end up back in the Valley.
        """
        if self._start_touched:
            return
        want = suggested_start_for_race(self._current_race().race_id)
        for i, s in enumerate(self.available_starts):
            if s.start_id == want:
                self.selected_start_index = i
                return

    def _current_start(self):
        return self.available_starts[self.selected_start_index]

    def _current_race(self):
        return self.available_races[self.selected_race_index]

    def _current_gender_option(self):
        race = self._current_race()
        if not race.genders:
            return None
        idx = min(self.selected_gender_index, len(race.genders) - 1)
        return race.genders[idx]

    def _sync_gender_buttons(self):
        """Rebuild gender button rects for whichever race is currently
        selected - race count of gender options isn't fixed (a future
        race could have just one, or none), so this can't be built once
        in __init__ and forgotten."""
        race = self._current_race()
        self.gender_buttons = []
        gender_btn_w = 80
        gender_btn_h = 36
        race_btn_w = 90
        base_x = self.appearance_x + len(self.available_races) * (race_btn_w + 8) + 20
        for i, gender in enumerate(race.genders):
            self.gender_buttons.append(pygame.Rect(
                base_x + i * (gender_btn_w + 8), self.appearance_y, gender_btn_w, gender_btn_h
            ))
        self.selected_gender_index = min(self.selected_gender_index, max(0, len(race.genders) - 1))
        self.selected_variant = 0  # reset variant when race/gender changes - stale index from a
        # different pool would silently pick the wrong appearance rather than erroring, so
        # resetting to a known-good 0 is safer than trying to carry it over.
    
    def handle_event(self, event):
        """Handle class selection and character creation."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check back button
            if self.back_button.collidepoint(mouse_pos):
                self.state_manager.transition_to(GameState.MENU)
                return
            
            # Check class buttons
            for i, btn in enumerate(self.class_buttons):
                if btn.collidepoint(mouse_pos):
                    self.selected_class = i

            # Race buttons
            for i, btn in enumerate(self.race_buttons):
                if btn.collidepoint(mouse_pos):
                    self.selected_race_index = i
                    self._sync_gender_buttons()
                    self._suggest_start()
                    return

            # Start zone
            for i, btn in enumerate(self.start_buttons):
                if btn.collidepoint(mouse_pos):
                    self.selected_start_index = i
                    self._start_touched = True   # race changes stop moving it from here on
                    return

            # Gender buttons
            for i, btn in enumerate(self.gender_buttons):
                if btn.collidepoint(mouse_pos):
                    self.selected_gender_index = i
                    self.selected_variant = 0
                    return

            # Variant cycle arrows
            gender_option = self._current_gender_option()
            if gender_option and gender_option.variants:
                variant_count = len(gender_option.variants)
                if self.variant_prev_button.collidepoint(mouse_pos):
                    self.selected_variant = (self.selected_variant - 1) % variant_count
                    return
                if self.variant_next_button.collidepoint(mouse_pos):
                    self.selected_variant = (self.selected_variant + 1) % variant_count
                    return
            
            # Check create button
            if self.create_button.collidepoint(mouse_pos):
                self._create_character()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._create_character()
    
    def _create_character(self):
        """Create character and move to overworld."""
        char = Character(self.character_name, self.classes[self.selected_class])
        # Hotbar is now auto-populated in Character.__init__
        char.enable_training()   # abilities above the starter kit are bought from class trainers

        # White starter weapon (+ ranged if that weapon_type occupies the
        # Ranged slot) and chest/legs/feet armor - see
        # entities/starting_gear.py. Only ever called here, on a genuinely
        # new character - never on a loaded one, which would silently
        # overwrite whatever they've since equipped or sold.
        from entities.starting_gear import grant_starting_gear
        grant_starting_gear(char)

        # Appearance - purely cosmetic fields, see Character.__init__.
        race = self._current_race()
        gender_option = self._current_gender_option()
        char.race = race.race_id
        char.gender = gender_option.gender_id if gender_option else "male"
        char.appearance_variant = self.selected_variant

        # Reset shared, process-lifetime world state back to a genuine
        # starting point before saving. OverworldScreen/ZoneManager (and
        # the quest manager singleton) are constructed once per process,
        # not per character - without this reset, a brand new character
        # created after an earlier character had already played and
        # moved around would silently inherit that earlier character's
        # last position AND quest progress into its own save file. Real
        # bug, reported live as "new level 1 character starts exactly
        # where I left off".
        zone_manager = self.state_manager._live_zone_manager()
        if zone_manager:
            zone_manager.reset_to_start(self._current_start().start_id)
        from world.quest_manager import get_quest_manager, QuestManager
        import world.quest_manager as _qm_module
        _qm_module._quest_manager = QuestManager()  # fresh quest state for the new character
        from world.travel_manager import reset_travel_manager
        # Bind the hearth to the start they picked, not to the Valley - see TravelManager.__init__.
        reset_travel_manager(self._current_start().start_id)
        
        # Set the player FIRST, then save through the state manager so the
        # (empty) party, recruit state and starting position are all written
        # too. Saving the bare Character here produced a v6 file with no
        # world block, which then loaded you into the default spawn.
        self.state_manager.player = char
        self.state_manager.party = None      # force a fresh Party for this character
        self.state_manager.save_game()
        self.state_manager.transition_to(GameState.OVERWORLD)
    
    def update(self, dt):
        """No updates needed."""
        pass
    
    def render(self, screen):
        """Draw character creation screen."""
        # Title
        self.renderer.draw_text(
            screen, "Create Character", (SCREEN_WIDTH // 2 - 150, 50),
            color=COLOR_WHITE, size="large"
        )
        
        # Class selection
        self.renderer.draw_text(screen, "Select Class:", (100, 150))
        for i, class_name in enumerate(self.classes):
            color = (150, 200, 150) if i == self.selected_class else COLOR_DARK_GRAY
            self.renderer.draw_button(screen, self.class_buttons[i], class_name, color=color)

        # Appearance section
        self.renderer.draw_text(screen, "Appearance:", (self.appearance_x, self.appearance_y - 24), color=COLOR_GOLD)

        for i, race in enumerate(self.available_races):
            color = (150, 200, 150) if i == self.selected_race_index else COLOR_DARK_GRAY
            self.renderer.draw_button(screen, self.race_buttons[i], race.label, color=color)

        for i, gender in enumerate(self._current_race().genders):
            color = (150, 200, 150) if i == self.selected_gender_index else COLOR_DARK_GRAY
            self.renderer.draw_button(screen, self.gender_buttons[i], gender.label, color=color)

        # Start zone
        self.renderer.draw_text(screen, "Start:", (self.start_x, self.appearance_y - 24),
                                color=COLOR_GOLD)
        for i, sz in enumerate(self.available_starts):
            color = (150, 200, 150) if i == self.selected_start_index else COLOR_DARK_GRAY
            self.renderer.draw_button(screen, self.start_buttons[i], sz.label, color=color)
        # One line of what the place actually is, so the choice means something before you take it.
        self.renderer.draw_text(screen, self._current_start().blurb,
                                (self.start_x, self.appearance_y + 42), color=(150, 150, 160),
                                size="small")

        # Variant cycle + live preview
        gender_option = self._current_gender_option()
        self.renderer.draw_button(screen, self.variant_prev_button, "<")
        self.renderer.draw_button(screen, self.variant_next_button, ">")

        pygame.draw.rect(screen, (30, 30, 35), self.preview_rect)
        pygame.draw.rect(screen, (90, 90, 100), self.preview_rect, 2)
        if gender_option and gender_option.variants:
            base_path = sprite_base_path(self._current_race().race_id, gender_option.gender_id, self.selected_variant)
            sprite = get_npc_sprite(base_path, "down", tile_width=self.preview_rect.width - 20)
            if sprite is not None:
                sx = self.preview_rect.centerx - sprite.get_width() // 2
                sy = self.preview_rect.bottom - sprite.get_height() - 5
                screen.blit(sprite, (sx, sy))
            variant_label = f"{self.selected_variant + 1}/{len(gender_option.variants)}"
            label_w = self.renderer.font_normal.size(variant_label)[0]
            self.renderer.draw_text(
                screen, variant_label,
                (self.preview_rect.centerx - label_w // 2, self.preview_rect.bottom + 8),
                color=(160, 160, 170))
        
        # Display selected class stats
        if 0 <= self.selected_class < len(self.classes):
            temp_char = Character("Preview", self.classes[self.selected_class])
            self.renderer.draw_character_box(screen, temp_char, (SCREEN_WIDTH // 2 - 100, 350))
        
        # Create button
        self.renderer.draw_button(screen, self.create_button, "Create Character")
        
        # Back button
        self.renderer.draw_button(screen, self.back_button, "Back")
