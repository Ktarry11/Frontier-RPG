"""
Character sheet screen. Stats, leveling, prestige only - WoW-style split
from equipment per Kyle: this screen used to also embed a full equipment
grid + backpack (merged in from InventoryScreen's slot grid), which made
it and InventoryScreen (the "B: Bags" screen) near-duplicates of each
other. Equipment now lives ONLY in InventoryScreen; this screen's "Gear"
button opens that screen the same way PartyScreen's Gear button already
does (InventoryScreen.set_subject() + transition, return_state brings you
back here instead of the overworld).

The hotbar editor that used to live at the bottom of this screen has been
removed - the Skills screen (GameState.SKILLS) already has a full ability
book + hotbar editor and having two places to do the same thing was the
redundancy called out directly in the mockup notes ("This is not needed!
Since we have the Skills Tab!").
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING
from config import COLOR_WHITE, COLOR_DARK_GRAY, COLOR_GOLD, COLOR_LIGHT_GRAY, get_exp_needed_for_level, PRESTIGE_LEVEL
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen


class CharacterSheetScreen(BaseScreen):
    """Character sheet: stats, leveling, prestige. Equipment lives in
    InventoryScreen (GameState.INVENTORY) - see module docstring."""

    def __init__(self, state_manager):
        super().__init__(state_manager)

        # Buttons
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.skills_button = pygame.Rect(SCREEN_WIDTH - 240, 20, 110, 50)
        self.talents_button = pygame.Rect(SCREEN_WIDTH - 370, 20, 110, 50)
        self.gear_button = pygame.Rect(SCREEN_WIDTH - 500, 20, 110, 50)
        self.prestige_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)

        self.core_stat_rects = []      # (stat_name, rect), for the hover tooltip

    def handle_event(self, event):
        """Handle button clicks and ESC."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state_manager.transition_to(GameState.OVERWORLD)
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            player = self.state_manager.player

            if self.close_button.collidepoint(mouse_pos):
                self.state_manager.transition_to(GameState.OVERWORLD)
                return

            if self.skills_button.collidepoint(mouse_pos):
                self.state_manager.transition_to(GameState.SKILLS)
                return

            if self.talents_button.collidepoint(mouse_pos):
                # Set player and open talents screen
                talent_screen = self.state_manager.states[GameState.TALENTS]
                talent_screen.character = player
                # Default to first tree if available
                if player.talent_trees:
                    first_tree_id = list(player.talent_trees.keys())[0]
                    talent_screen.set_current_tree(first_tree_id)
                self.state_manager.transition_to(GameState.TALENTS)
                return

            if self.gear_button.collidepoint(mouse_pos):
                # Same handoff pattern PartyScreen's Gear button uses -
                # set_subject() to the player, return here on Close instead
                # of the overworld default.
                inventory = self.state_manager.states.get(GameState.INVENTORY)
                if inventory is not None:
                    inventory.set_subject(player, return_state=GameState.CHARACTER_SHEET)
                    self.state_manager.transition_to(GameState.INVENTORY)
                return

            if self.prestige_button.collidepoint(mouse_pos):
                if player.prestige():
                    print(f"Prestige! Now level {player.prestige_level}, back to level 1")
                return

    def render(self, screen):
        """Draw character sheet."""
        player = self.state_manager.player
        stats = player.get_stat_sheet()

        # Three-column layout: identity/core/defense (left), resistances/
        # offense/procs (middle), portrait (right). Was one long left-hand
        # stack that clipped off the bottom of a 720px-tall screen once
        # RESISTANCES was added (Kyle's screenshot) - a real content-growth
        # problem, not a one-off bug, so this splits into columns instead
        # of just shaving pixels off row spacing.
        col_w = 280
        left_x = 20
        mid_x = left_x + col_w + 30
        right_x = mid_x + col_w + 30

        self._draw_panel_bg(screen, left_x, 20, col_w, SCREEN_HEIGHT - 40)
        self._draw_panel_bg(screen, mid_x, 20, col_w, SCREEN_HEIGHT - 40)

        # ===== LEFT COLUMN: identity, core stats, defense =====
        y_pos = 36

        self.renderer.draw_text(screen, "CHARACTER SHEET", (left_x, 20), size="large")
        y_pos = 76

        self.renderer.draw_text(screen, f"{stats['name']}", (left_x, y_pos))
        y_pos += 30
        self.renderer.draw_text(screen, f"Class: {stats['class']}", (left_x, y_pos))
        y_pos += 25
        self.renderer.draw_text(screen, f"Level: {stats['level']} (Prestige: {stats['prestige']})", (left_x, y_pos))
        y_pos += 25

        # Experience bar - label stacked above the bar rather than beside it
        # (the old side-by-side layout assumed a wide single-column sheet;
        # at the new 280px column width there's no room next to the bar
        # without it overlapping the panel edge or the row above).
        exp_needed = get_exp_needed_for_level(stats['level'])  # Single source of truth (config.py)
        self.renderer.draw_text(screen, f"EXP: {stats['experience']}/{exp_needed}", (left_x, y_pos))
        y_pos += 22
        self.renderer.draw_health_bar(screen, (left_x, y_pos), stats['experience'], exp_needed, width=col_w)
        y_pos += 40

        # Core Stats
        self.renderer.draw_text(screen, "CORE STATS", (left_x, y_pos), color=COLOR_GOLD)
        y_pos += 30

        # Rects are recorded each frame so hovering a core stat can show what
        # that stat actually feeds into (see _draw_stat_tooltip).
        self.core_stat_rects = []
        for stat_name, value in stats['core_stats'].items():
            base_value = stats['base_stats'][stat_name]
            gear_bonus = value - base_value
            if gear_bonus > 0:
                self.renderer.draw_text(screen, f"{stat_name.capitalize()}: {int(value)} (+{int(gear_bonus)} gear)", (left_x, y_pos), color=(120, 220, 120))
            else:
                self.renderer.draw_text(screen, f"{stat_name.capitalize()}: {int(value)}", (left_x, y_pos))
            self.core_stat_rects.append((stat_name, pygame.Rect(left_x, y_pos - 2, 260, 24)))
            y_pos += 22

        y_pos += 15

        # Defense Stats
        self.renderer.draw_text(screen, "DEFENSE", (left_x, y_pos), color=COLOR_GOLD)
        y_pos += 28

        def_stats = stats['defense']
        self.renderer.draw_text(screen, f"Health: {def_stats['health']}/{def_stats['health_max']}", (left_x, y_pos))
        y_pos += 22
        self.renderer.draw_health_bar(screen, (left_x, y_pos), def_stats['health'], def_stats['health_max'], width=200)
        y_pos += 28

        # Resource bar - driven by CLASS_RESOURCE_MAP (combat/abilities.py),
        # same fix as combat_screen.py's resource bar. See that file for the
        # full explanation of why the old hardcoded per-class checks broke
        # once the roster expanded past the original 4 launch classes.
        from combat.abilities import get_class_resource, ResourceType
        resource = get_class_resource(player.char_class)

        if resource == ResourceType.MANA:
            self.renderer.draw_text(screen, f"Mana: {def_stats['mana']}/{def_stats['mana_max']}", (left_x, y_pos))
            y_pos += 22
            self.renderer.draw_health_bar(screen, (left_x, y_pos), def_stats['mana'], def_stats['mana_max'], width=200, height=15, bar_color=(50, 150, 220))
            y_pos += 28
        elif resource == ResourceType.RAGE:
            self.renderer.draw_text(screen, f"Rage: {player.display_rage}/{round(player.max_rage)}", (left_x, y_pos))
            y_pos += 22
            self.renderer.draw_health_bar(screen, (left_x, y_pos), player.current_rage, player.max_rage, width=200, height=15, bar_color=(220, 50, 50))
            y_pos += 28
        elif resource == ResourceType.ENERGY:
            self.renderer.draw_text(screen, f"Energy: {player.display_energy}/{round(player.max_energy)}", (left_x, y_pos))
            y_pos += 22
            self.renderer.draw_health_bar(screen, (left_x, y_pos), player.current_energy, player.max_energy, width=200, height=15, bar_color=(220, 220, 50))
            y_pos += 28

        # Show the actual mitigation these ratings buy, not just the raw
        # number - armor has diminishing returns so the rating alone is
        # meaningless without the percentage next to it.
        self.renderer.draw_text(
            screen,
            f"Armor: {def_stats['armor']}  ({player.get_physical_reduction_percent():.1f}% phys)",
            (left_x, y_pos))
        y_pos += 22
        self.renderer.draw_text(
            screen,
            f"Magic Resistance: {def_stats['magic_resistance']}  ({player.get_magic_reduction_percent():.1f}% magic)",
            (left_x, y_pos))
        y_pos += 32

        # Real per-school resistances (Fire/Frost/Nature/Shadow/Arcane/
        # Holy - see Character.get_resistance/get_resistance_percent).
        # Always shows all 6 schools now, including zeroes (Kyle: "I still
        # would like it to show if anything is there, even a box that says
        # Shadow Resistance: 0") - reversed from the earlier nonzero-only
        # filter, which was matching real WoW's clutter-avoidance
        # convention but hid the section entirely for any character with
        # no resistance sources yet, which reads as "broken" rather than
        # "correctly empty" mid-development.
        # ===== MIDDLE COLUMN: resistances, offense, procs =====
        # Own column now (was the tail of the left stack) - a full 6-school
        # RESISTANCES block plus OFFENSIVE plus PROCS never fit under
        # CORE STATS + DEFENSE in one 720px-tall column, which is exactly
        # what pushed OFFENSIVE off-screen in Kyle's screenshot.
        mid_y = 36
        self.renderer.draw_text(screen, "COMBAT STATS", (mid_x, mid_y), size="large", font_size=26)
        mid_y += 46
        self._draw_divider(screen, mid_x, mid_y, col_w)
        mid_y += 14

        from combat.status_effects import DamageSchool
        school_labels = [
            (DamageSchool.FIRE, "Fire Resistance"),
            (DamageSchool.FROST, "Frost Resistance"),
            (DamageSchool.NATURE, "Nature Resistance"),
            (DamageSchool.SHADOW, "Shadow Resistance"),
            (DamageSchool.ARCANE, "Arcane Resistance"),
            (DamageSchool.HOLY, "Holy Resistance"),
        ]
        self.renderer.draw_text(screen, "RESISTANCES", (mid_x, mid_y), color=COLOR_GOLD)
        mid_y += 26
        for school, label in school_labels:
            value = player.get_resistance(school)
            pct = player.get_resistance_percent(school)
            self.renderer.draw_text(
                screen, f"{label}: {value}  ({pct:.1f}%)",
                (mid_x, mid_y), font_size=16)
            mid_y += 21
        mid_y += 10
        self._draw_divider(screen, mid_x, mid_y, col_w)
        mid_y += 20

        # Offensive stats
        self.renderer.draw_text(screen, "OFFENSIVE", (mid_x, mid_y), color=COLOR_GOLD)
        mid_y += 28

        derived = stats['derived_stats']
        self.renderer.draw_text(screen, f"Attack Power: {derived['attack_power']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Spell Power: {derived['spell_power']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Ranged Power: {derived['ranged_attack_power']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Healing Power: {derived['healing_power']}", (mid_x, mid_y))
        mid_y += 30
        self._draw_divider(screen, mid_x, mid_y, col_w)
        mid_y += 20

        self.renderer.draw_text(screen, "PROCS & UTILITY", (mid_x, mid_y), color=COLOR_GOLD)
        mid_y += 28
        self.renderer.draw_text(screen, f"Crit (Phys): {derived['crit_physical']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Crit (Spell): {derived['crit_spell']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Haste: {derived['haste']}", (mid_x, mid_y))
        mid_y += 28
        # HIT, four ways. A dual-wielder, a caster and an archer face
        # completely different miss chances off the same hit rating, so one
        # number could not tell any of them what they needed - Kyle: "we
        # need to show hit % for spells, mainhand and offhand too. WoW has
        # this." Ranged joined them on 6 Nov: "if a hunter is using 2
        # weapons and shoots a gun, the gun should be impacted by hit chance
        # associated with the gun and not with the fact it has two weapons."
        # The off-hand figure is the WHITE swing's, and it is the only
        # attack in the game that pays the dual-wield penalty.
        self.renderer.draw_text(
            screen, f"Hit Rating: {derived['hit_rating']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(
            screen, f"Hit (Spell): {derived['hit_spell']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(
            screen, f"Hit (Main Hand): {derived['hit_main_hand']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(
            screen, f"Hit (Off Hand): {derived['hit_off_hand']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(
            screen, f"Hit (Ranged): {derived['hit_ranged']}", (mid_x, mid_y))
        mid_y += 28
        self.renderer.draw_text(screen, f"Dodge: {derived['dodge']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Block: {derived['block']}", (mid_x, mid_y))
        mid_y += 22
        self.renderer.draw_text(screen, f"Parry: {derived['parry']}", (mid_x, mid_y))

        # ===== RIGHT COLUMN: identity =====
        # There was an empty 220x260 frame here labelled "Portrait WIP"
        # (Kyle: "remove WIP thing"). No portrait art exists, so the frame
        # was a box reserving space for nothing while announcing to the
        # player that the game was unfinished. Gone - the name and level now
        # start at the top of the column where the frame used to begin.
        self.renderer.draw_text(
            screen, f"{stats['name']}", (right_x, 40), size="large", color=COLOR_GOLD)
        self.renderer.draw_text(
            screen, f"Level {stats['level']} {stats['class']}",
            (right_x, 76), color=COLOR_LIGHT_GRAY)

        # Quick equipped-item count + a nudge toward the Gear screen, so the
        # sheet still shows *something* about gear without re-embedding the
        # whole equipment grid InventoryScreen already owns.
        equipped = sum(1 for slot in player.equipment.to_dict().values() if slot)
        gear_y = 112
        self.renderer.draw_text(
            screen, f"Equipped items: {equipped}/17", (right_x, gear_y),
            color=COLOR_LIGHT_GRAY)
        self.renderer.draw_text(
            screen, "See Gear for equipment & backpack",
            (right_x, gear_y + 24), font_size=16, color=(140, 140, 160))

        # Prestige button - shown ONLY once eligible. The old "available at
        # Level 100" line was both wrong (the cap is PRESTIGE_LEVEL, 60) and
        # unwanted clutter on the sheet at every level below the cap.
        if player.level >= PRESTIGE_LEVEL:
            self.renderer.draw_button(screen, self.prestige_button, "PRESTIGE!", color=(100, 150, 100))
            self.renderer.draw_text(screen, "Gain +1 Prestige Level & talent point!", (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 120))

        # Top-right buttons
        self.renderer.draw_button(screen, self.gear_button, "Gear")
        self.renderer.draw_button(screen, self.skills_button, "Skills")
        self.renderer.draw_button(screen, self.talents_button, "Talents")
        self.renderer.draw_button(screen, self.close_button, "Close")

        # Core stat hover tooltip - drawn last so it sits above everything.
        mouse_pos = pygame.mouse.get_pos()
        self._draw_stat_tooltip(screen, player, mouse_pos)


    def _draw_panel_bg(self, screen, x, y, w, h):
        """Subtle panel background + border so each column reads as a
        distinct card instead of three blocks of text floating on the
        same background - cheap visual polish, no new assets needed."""
        rect = pygame.Rect(x - 12, y, w + 24, h)
        self.renderer.draw_rect(screen, rect, (22, 22, 28))
        self.renderer.draw_rect(screen, rect, (70, 70, 80), fill=False)

    def _draw_divider(self, screen, x, y, w):
        """Thin gold-tinted rule between sections within a column."""
        pygame.draw.line(screen, (90, 75, 40), (x, y), (x + w, y), 1)

    def _draw_stat_tooltip(self, screen, player, mouse_pos):
        """Explain what a hovered core stat actually does for this character."""
        hovered = None
        for stat_name, rect in self.core_stat_rects:
            if rect.collidepoint(mouse_pos):
                hovered = stat_name
                break
        if not hovered:
            return

        lines = player.get_stat_contributions(hovered)
        if not lines:
            return
        lines = [hovered.capitalize()] + lines

        box_w = 320
        box_h = 20 * len(lines) + 16
        x = min(mouse_pos[0] + 16, SCREEN_WIDTH - box_w - 10)
        y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - box_h - 10)
        rect = pygame.Rect(x, y, box_w, box_h)

        self.renderer.draw_rect(screen, rect, (15, 15, 20))
        self.renderer.draw_rect(screen, rect, COLOR_GOLD, fill=False)

        ty = y + 8
        for i, line in enumerate(lines):
            self.renderer.draw_text(screen, line, (x + 10, ty),
                                    color=COLOR_GOLD if i == 0 else COLOR_WHITE)
            ty += 20
