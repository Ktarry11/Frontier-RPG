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
from world.start_zones import get_available_starts, get_start_cards, suggested_start_for_race


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

        # START ZONE. Kyle, 21 Nov 2026: "instead of clicking on the starting zones. We make a more prominent 'Starting
        # zone' thing you click on to pick it. It has actual lore about the location and an image too." So the free span
        # to the right of the appearance row holds one big card for the chosen start (its painting, name and where it
        # is), and clicking it opens the picker: a card for every start, built or not, with its painting and lore. The
        # vertical budget is the same as before (the preview runs to y=550, the name box starts at 598).
        start_x = self.variant_next_button.right + 28
        self.start_x = start_x
        self.start_cards = get_start_cards()
        self.start_card_rect = pygame.Rect(start_x, appearance_y - 6, SCREEN_WIDTH - 12 - start_x, 140)
        self.start_buttons = [self.start_card_rect]     # qa_start_zones measures the row's right edge from these
        self.start_picker_open = False
        self._start_art = {}
        n = len(self.start_cards)
        gap, margin = 16, 36
        card_w = (SCREEN_WIDTH - 2 * margin - gap * (n - 1)) // n
        self.picker_cards = [pygame.Rect(margin + k * (card_w + gap), 100, card_w, 500) for k in range(n)]
        self.picker_close = pygame.Rect(SCREEN_WIDTH - margin - 110, 52, 110, 40)

        self.create_button = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        
        self.name_box = pygame.Rect(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 122, 340, 38)

        # Back button
        self.back_button = pygame.Rect(20, 20, 100, 50)

    def _picker_event(self, event):
        """The start picker is modal: a card picks its start and closes it; Close, Escape or a click off the cards
        closes it; a locked card does nothing."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.start_picker_open = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.picker_close.collidepoint(event.pos):
                self.start_picker_open = False
                return
            for sz, rect in zip(self.start_cards, self.picker_cards):
                if rect.collidepoint(event.pos):
                    if sz.available:
                        ids = [a.start_id for a in self.available_starts]
                        self.selected_start_index = ids.index(sz.start_id)
                        self._start_touched = True   # race changes stop moving it from here on
                        self.start_picker_open = False
                    return
            self.start_picker_open = False

    def _art(self, sz, size):
        """The start's painting cropped to fill `size`, or a painted stand-in (a dusk gradient and the start's name)
        until its art lands. Cached per start and size."""
        key = (sz.start_id, size)
        if key in self._start_art:
            return self._start_art[key]
        import os
        w, h = size
        surf = None
        if sz.art and os.path.exists(sz.art):
            try:
                img = pygame.image.load(sz.art).convert()
                scale = max(w / img.get_width(), h / img.get_height())
                img = pygame.transform.smoothscale(img, (max(w, int(img.get_width() * scale) + 1),
                                                         max(h, int(img.get_height() * scale) + 1)))
                surf = img.subsurface(pygame.Rect((img.get_width() - w) // 2, (img.get_height() - h) // 2, w, h)).copy()
            except pygame.error:
                surf = None
        if surf is None:
            tones = {"valley_of_trials": ((150, 60, 30), (60, 25, 15)), "deathknell": ((70, 80, 70), (20, 25, 25)),
                     "dawnhaven": ((200, 120, 40), (90, 30, 25)), "white_expanse": ((150, 170, 200), (50, 60, 90))}
            top, bottom = tones.get(sz.start_id, ((90, 90, 110), (30, 30, 40)))
            surf = pygame.Surface((w, h))
            for yy in range(h):
                t = yy / max(1, h - 1)
                surf.fill(tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)), (0, yy, w, 1))
            if sz.available:          # a locked card says "Not yet" over its art instead
                label = self.renderer.font_bold.render(sz.label, True, (240, 230, 210))
                surf.blit(label, label.get_rect(center=(w // 2, h // 2)))
        self._start_art[key] = surf
        return surf

    def _draw_start_card(self, screen):
        """The one big start button: the chosen start's painting, its name, where it is and its levels."""
        r = self.start_card_rect
        hover = r.collidepoint(pygame.mouse.get_pos())
        self.renderer.draw_panel(screen, r, selected=hover)
        sz = self._current_start()
        tw, th = 136, 102
        screen.blit(self._art(sz, (tw, th)), (r.x + 10, r.y + 10))
        pygame.draw.rect(screen, (120, 100, 60), (r.x + 10, r.y + 10, tw, th), 1)
        tx, tw2 = r.x + tw + 20, r.right - (r.x + tw + 20) - 10
        self.renderer.draw_text(screen, "Starting zone", (tx, r.y + 8), color=(170, 160, 140), size="small")
        self.renderer.draw_text(screen, sz.label, (tx, r.y + 26), color=COLOR_GOLD)
        y = r.y + 52
        for line in self.renderer.wrap_text(sz.region, tw2, size="small")[:2]:
            self.renderer.draw_text(screen, line, (tx, y), color=(200, 200, 210), size="small")
            y += 16
        self.renderer.draw_text(screen, sz.levels, (tx, y), color=(160, 160, 170), size="small")
        self.renderer.draw_text(screen, "Click to see every start and choose", (r.x + 10, r.bottom - 22),
                                color=(220, 200, 130) if hover else (150, 140, 120), size="small")

    def _draw_start_picker(self, screen):
        """A card for every start: its painting, name, where it is, its levels and a paragraph of lore. A start that
        isn't built yet is shown locked."""
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((8, 8, 12, 225))
        screen.blit(dim, (0, 0))
        self.renderer.draw_text(screen, "Where do you wake up?", (SCREEN_WIDTH // 2, 40), color=COLOR_GOLD,
                                size="large", center=True)
        self.renderer.draw_button(screen, self.picker_close, "Close")
        mouse = pygame.mouse.get_pos()
        chosen = self._current_start().start_id
        for sz, r in zip(self.start_cards, self.picker_cards):
            hover = r.collidepoint(mouse) and sz.available
            self.renderer.draw_panel(screen, r, selected=(sz.start_id == chosen or hover), disabled=not sz.available)
            aw = r.width - 20
            ah = aw * 3 // 4          # the paintings are 4:3 (docs/start_zone_art_prompts.md)
            art = self._art(sz, (aw, ah))
            screen.blit(art, (r.x + 10, r.y + 10))
            if not sz.available:
                veil = pygame.Surface((aw, ah), pygame.SRCALPHA)
                veil.fill((0, 0, 0, 150))
                screen.blit(veil, (r.x + 10, r.y + 10))
                self.renderer.draw_text(screen, "Not yet", (r.centerx, r.y + 10 + ah // 2 - 10), color=(230, 230, 235),
                                        center=True)
            pygame.draw.rect(screen, (120, 100, 60), (r.x + 10, r.y + 10, aw, ah), 1)
            y = r.y + ah + 20
            self.renderer.draw_text(screen, sz.label, (r.x + 12, y), color=COLOR_GOLD if sz.available else (150, 150, 155))
            y += 26
            for line in self.renderer.wrap_text(sz.region, aw, size="small"):
                self.renderer.draw_text(screen, line, (r.x + 12, y), color=(200, 200, 210), size="small")
                y += 16
            self.renderer.draw_text(screen, sz.levels or sz.locked_note, (r.x + 12, y), color=(160, 160, 170),
                                    size="small")
            y += 24
            for line in self.renderer.wrap_text(sz.lore, aw - 4, size="small"):
                if y > r.bottom - 44:
                    break
                self.renderer.draw_text(screen, line, (r.x + 12, y), color=(215, 210, 200), size="small")
                y += 16

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

    def _looks(self):
        """The places in this race and gender's list the creator offers (world/race_registry.pickable_looks)."""
        from world.race_registry import pickable_looks
        g = self._current_gender_option()
        if g is None:
            return []
        return pickable_looks(self._current_race().race_id, g.gender_id) or list(range(len(g.variants)))

    def _first_look(self):
        looks = self._looks()
        return looks[0] if looks else 0

    def _step_look(self, d):
        looks = self._looks()
        if not looks:
            return
        i = looks.index(self.selected_variant) if self.selected_variant in looks else 0
        self.selected_variant = looks[(i + d) % len(looks)]

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
        self.selected_variant = self._first_look()  # reset variant when race/gender changes - stale index from a
        # different pool would silently pick the wrong appearance rather than erroring, so
        # resetting to a known-good 0 is safer than trying to carry it over.
    
    def handle_event(self, event):
        """Handle class selection and character creation."""
        if self.start_picker_open:
            self._picker_event(event)
            return
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

            # Start zone: the card opens the picker
            if self.start_card_rect.collidepoint(mouse_pos):
                self.start_picker_open = True
                return

            # Gender buttons
            for i, btn in enumerate(self.gender_buttons):
                if btn.collidepoint(mouse_pos):
                    self.selected_gender_index = i
                    self.selected_variant = self._first_look()
                    return

            # Variant cycle arrows
            gender_option = self._current_gender_option()
            if gender_option and gender_option.variants:
                if self.variant_prev_button.collidepoint(mouse_pos):
                    self._step_look(-1)
                    return
                if self.variant_next_button.collidepoint(mouse_pos):
                    self._step_look(1)
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
        # What the character has for being what it is: an Orc's Blood Fury, a Tauren's War
        # Stomp. The race is only known from this line on, so this is the first moment the
        # racial abilities can be given - and nothing gave them, so a new character had its
        # race's passive and none of its abilities.
        from world.personal_kits import grant
        grant(char)
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
        # Recruit and faction state are singletons with exactly the same
        # lifetime hazard as the quest manager above, and they were the two
        # that got missed. An un-reset recruit manager hands the new
        # character the PREVIOUS character's hires, and an IN_PARTY recruit
        # has no world location - so a brand new level 1 walked into a world
        # with the companions already deleted from it. See
        # reset_recruit_manager's docstring.
        from world.recruit_manager import reset_recruit_manager
        from world.faction_manager import reset_faction_manager
        reset_recruit_manager()
        reset_faction_manager()
        
        # Set the player FIRST, then save through the state manager so the
        # (empty) party, recruit state and starting position are all written
        # too. Saving the bare Character here produced a v6 file with no
        # world block, which then loaded you into the default spawn.
        self.state_manager.player = char
        self.state_manager.party = None      # force a fresh Party for this character
        # The Collection's Book of First Steps (world/collection.py): a bag and some gold for every new character.
        try:
            from world.collection import new_character_gifts
            gifts = new_character_gifts()
            if gifts["bag"]:
                from entities.loot_generator import LootGenerator
                bag = LootGenerator().generate_bag(bag_id="worn_leather_satchel")
                if bag is not None:
                    char.inventory.append(bag)
            if gifts["copper"]:
                self.state_manager.get_party().add_currency(gifts["copper"])
        except Exception as exc:
            print(f"Book of First Steps: {exc}")

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

        # Start zone: the card (and, over everything, the picker when it's open)
        self._draw_start_card(screen)

        # Variant cycle + live preview
        gender_option = self._current_gender_option()
        self.renderer.draw_button(screen, self.variant_prev_button, "<")
        self.renderer.draw_button(screen, self.variant_next_button, ">")

        pygame.draw.rect(screen, (30, 30, 35), self.preview_rect)
        pygame.draw.rect(screen, (90, 90, 100), self.preview_rect, 2)
        if gender_option and gender_option.variants:
            base_path = sprite_base_path(self._current_race().race_id, gender_option.gender_id, self.selected_variant)
            # by height, so the taller new looks (docs/player_sprite_prompts.md) fit the box instead of spilling out of it
            sprite = get_npc_sprite(base_path, "down", tile_height=self.preview_rect.height - 12)
            if sprite is not None:
                sx = self.preview_rect.centerx - sprite.get_width() // 2
                sy = self.preview_rect.bottom - sprite.get_height() - 5
                screen.blit(sprite, (sx, sy))
            looks = self._looks()
            pos = looks.index(self.selected_variant) + 1 if self.selected_variant in looks else 1
            variant_label = f"{pos}/{len(looks)}"
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

        if self.start_picker_open:
            self._draw_start_picker(screen)
