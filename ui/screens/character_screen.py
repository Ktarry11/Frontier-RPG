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
        # EVERY CHARACTER USED TO BE CALLED "Hero". The field existed and was
        # never editable, which did not matter with one save slot and matters a
        # lot with fifteen - describe_save already puts the name in the slot
        # picker, so the whole menu read "Hero - Level 12 Warrior" fifteen times
        # over. Kyle: "technically we need to be able to name our characters."
        self.character_name = ""
        self.name_active = True        # the field has focus when the screen opens
        self.NAME_MAX = 18
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
        # THE SCREEN OUTGREW ITS LAYOUT. This grid was laid out for a shorter class list using the
        # global BUTTON_WIDTH/HEIGHT (200x50); at 30 classes that is six rows running y=170 to
        # 520, and the stats preview is drawn at a hard-coded y=350 - straight through rows four,
        # five and six. The preview sat on top of three class buttons, which is what Kyle saw.
        #
        # So the grid uses its OWN button size rather than the global one. The global is right
        # for screens with a handful of buttons and wrong for a 30-cell grid, and bending the
        # global to suit this screen would have shrunk every button in the game.
        self.class_buttons = []
        columns = 5
        grid_start_x = 40
        grid_start_y = 135
        cls_btn_w, cls_btn_h = 170, 42
        col_spacing = cls_btn_w + 8
        row_spacing = cls_btn_h + 6
        self.class_btn_size = (cls_btn_w, cls_btn_h)
        for i, _ in enumerate(self.classes):
            row = i // columns
            col = i % columns
            btn = pygame.Rect(
                grid_start_x + (col * col_spacing),
                grid_start_y + (row * row_spacing),
                cls_btn_w,
                cls_btn_h
            )
            self.class_buttons.append(btn)
        #: Where the stats preview goes: to the RIGHT of the grid, not through it. Computed from
        #: the grid's real right edge so adding a class row can never push the grid under it.
        self.stats_preview_pos = (grid_start_x + columns * col_spacing + 20, grid_start_y)

        # Appearance controls sit in the strip between the class stat
        # preview box (draw_character_box: y=350..550) and the create
        # button - the natural gap there was only 20px (measured: box
        # bottom 550, old create button top 570), nowhere near enough for
        # a real control row, so the create button moves down to make
        # room rather than cramming controls into a gap that doesn't
        # exist. See create_button's own position below, computed to
        # leave appearance_y a genuine ~70px band.
        appearance_x = grid_start_x
        appearance_y = 452
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
        
        self.name_box = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 122, 340, 38)

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
            
            # Clicking the name field focuses it; clicking anywhere else does not.
            self.name_active = self.name_box.collidepoint(mouse_pos)

            # Check create button
            if self.create_button.collidepoint(mouse_pos):
                self._create_character()
        
        if event.type == pygame.KEYDOWN:
            if self.name_active and event.key not in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if event.key == pygame.K_BACKSPACE:
                    self.character_name = self.character_name[:-1]
                elif event.key == pygame.K_TAB:
                    self.name_active = False
                else:
                    ch = event.unicode
                    # Letters, spaces, apostrophes and hyphens only - this ends
                    # up in a filename-adjacent summary and on screen, and a
                    # name full of control characters helps nobody.
                    if ch and (ch.isalpha() or ch in " '-") and len(self.character_name) < self.NAME_MAX:
                        self.character_name += ch
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._create_character()
    
    def _create_character(self):
        """Create character and move to overworld."""
        name = self.character_name.strip() or "Hero"
        char = Character(name, self.classes[self.selected_class])
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

        # THIS LINE USED TO BE `save_game()`, AND IT ATE PEOPLE'S CHARACTERS.
        # With no filename it wrote to state_manager.current_save_file, which
        # still pointed at whatever slot the PREVIOUS character had loaded -
        # so finishing creation silently overwrote a live save before the
        # player ever saw the world. Kyle's tester, 7 Nov: "I just made a
        # shaman and used the +5 level thing and saved it but it over wrote
        # my level 13 druid."
        #
        # A new character owns no slot (begin_new_character cleared it), so
        # there is nothing to write to yet and nothing is written. The player
        # picks the slot first, in the picker the menu already has, which is
        # also the "select WHICH slot to save in" Kyle asked for. The game is
        # only entered once a slot is chosen, so a new character cannot be
        # played unsaved and cannot land anywhere by accident.
        self.state_manager.pending_new_character = True
        self.state_manager.transition_to(GameState.MENU)
    
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
        # What the place actually is, so the choice means something before you take it.
        # WRAPPED, because it did not fit: both blurbs run past the right edge of the screen on
        # one line (Deathknell's by ~190px) and were being drawn straight off it. The width here
        # is the real space between this column and the screen edge rather than a guess, so a
        # longer blurb wraps instead of silently vanishing.
        blurb_w = SCREEN_WIDTH - 12 - self.start_x
        for i, line in enumerate(self.renderer.wrap_text(
                self._current_start().blurb, blurb_w, size="small")):
            self.renderer.draw_text(screen, line,
                                    (self.start_x, self.appearance_y + 42 + i * 16),
                                    color=(150, 150, 160), size="small")

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
            self.renderer.draw_character_box(screen, temp_char, self.stats_preview_pos)
        
        # Name field
        import pygame as _pg
        _pg.draw.rect(screen, (24, 24, 30), self.name_box)
        _pg.draw.rect(screen,
                      (220, 200, 130) if self.name_active else (90, 90, 100),
                      self.name_box, 2)
        self.renderer.draw_text(screen, "Name", (self.name_box.x, self.name_box.y - 22),
                                color=(170, 170, 180))
        shown = self.character_name or "Hero"
        self.renderer.draw_text(
            screen, shown, (self.name_box.x + 10, self.name_box.y + 9),
            color=COLOR_WHITE if self.character_name else (110, 110, 120))
        if self.name_active:
            # A caret that blinks, so an empty box reads as "type here" rather
            # than as a field that is not working.
            if (_pg.time.get_ticks() // 450) % 2 == 0:
                cx = self.name_box.x + 12 + self.renderer.font_normal.size(
                    self.character_name)[0]
                _pg.draw.line(screen, (230, 230, 240), (cx, self.name_box.y + 8),
                              (cx, self.name_box.bottom - 8), 2)

        # Create button
        self.renderer.draw_button(screen, self.create_button, "Create Character")
        
        # Back button
        self.renderer.draw_button(screen, self.back_button, "Back")
