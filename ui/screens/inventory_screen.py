"""
Inventory screen. Shows equipped gear (16 gear slots + 4 bag slots) and
unequipped inventory items.
Click an inventory item to equip it; click an equipped item to unequip it.

The screen has a **subject** - the character whose equipment/bag is shown -
which defaults to the player but can be pointed at a companion by the party
screen. Each character owns their OWN inventory (per Kyle: "make each
character have their own inventory... they're eventually like real people"
- ties into a planned system where companions come and go on their own
whims/goals). Equip/unequip therefore operates entirely on the subject's
own Character.equip_item()/unequip_item() - no cross-character bag
shuffling, no shared player backpack. Currency IS still shared across the
party (Party.copper) - that split is deliberate, see entities/party.py.
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_DARK_GRAY, COLOR_GOLD, COLOR_LIGHT_GRAY
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.sprite_loader import get_tile_sprite
from world.gathering_manager import MATERIAL_TYPE_FOLDERS


SLOT_LAYOUT = [
    # (slot_key, display_label, col, row)
    ("head", "Head", 0, 0),
    ("neck", "Neck", 0, 1),
    ("shoulder", "Shoulder", 0, 2),
    ("back", "Back", 0, 3),
    ("chest", "Chest", 0, 4),
    ("wrist", "Wrist", 0, 5),
    ("hands", "Hands", 1, 0),
    ("waist", "Waist", 1, 1),
    ("legs", "Legs", 1, 2),
    ("feet", "Feet", 1, 3),
    ("ring1", "Ring 1", 1, 4),
    ("ring2", "Ring 2", 1, 5),
    ("trinket1", "Trinket 1", 2, 0),
    ("trinket2", "Trinket 2", 2, 1),
    ("main_hand", "Main Hand", 2, 2),
    ("off_hand", "Off Hand", 2, 3),
    ("ranged", "Ranged", 2, 4),
]

# Bag slots get their own small row rather than living in SLOT_LAYOUT's grid
# - they're conceptually different (containers, not gear) and Kyle's spec
# ("24 spots with 4 additional bag spots") reads as a dedicated bag strip,
# WoW-style, sitting right above the backpack grid it controls the size of.
BAG_SLOT_LAYOUT = [
    ("bag1", "Bag 1"), ("bag2", "Bag 2"), ("bag3", "Bag 3"), ("bag4", "Bag 4"),
]
BAG_SLOT_SIZE = 56
BAG_SLOT_GAP = 8

SLOT_BOX_W = 170
SLOT_BOX_H = 44
SLOT_COL_SPACING = 180
SLOT_ROW_SPACING = 50
SLOT_START_X = 20
SLOT_START_Y = 60

INV_GRID_COLS = 6
INV_SLOT_SIZE = 90
INV_SLOT_SPACING = 8
INV_START_X = 600
INV_START_Y = 100  # pushed down from 60 to leave room for the bag row + capacity readout above the grid

# Materials tab grid (Gathering Phase 1). Separate constants from the gear
# backpack grid above - the materials tab has the full screen to itself
# (no gear panel sharing the view), so it uses more columns and starts
# further left/higher for a roomier layout.
MATERIALS_GRID_COLS = 10
MATERIALS_SLOT_SIZE = 72
MATERIALS_SLOT_SPACING = 10
MATERIALS_START_X = 40
MATERIALS_START_Y = 110


from ui.coin_format import format_coins


class InventoryScreen(BaseScreen):
    """Equipment + inventory management screen."""

    def __init__(self, state_manager, icon_ui_helper=None):
        super().__init__(state_manager)
        self.icon_ui_helper = icon_ui_helper  # For future icon integration
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)
        self.slot_rects = {}  # slot_key -> pygame.Rect
        self.inventory_rects = []  # list of pygame.Rect, index-aligned to player.inventory
        self.selected_item = None  # Item currently shown in detail panel (hover/click)
        # Whose gear we're editing, and where Close returns to. Set via
        # set_subject(); reset to the player whenever opened from the
        # overworld so you never land on a companion's sheet by accident.
        self.subject = None
        self.return_state = GameState.OVERWORLD
        self.equip_error = None
        self.equip_error_timer = 0.0
        # Destroy-confirmation flow for non-equippable items (quest items
        # especially - see Kyle's bug report: quest-category LootItems
        # are never sellable by design, so once the drop-suppression fix
        # in combat_engine/quest_manager stops over-dropping them, the
        # only remaining gap was no way to clear out ones already stuck
        # in the bag, or a quest abandoned mid-way with leftovers). None
        # = no confirmation pending; otherwise the LootItem awaiting a
        # Yes/No click.
        self.pending_destroy_item = None
        self.destroy_yes_button = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 40, 160, 50)
        self.destroy_no_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 40, 160, 50)

        #: DISCARD MODE. Kyle, 4 Nov 2026: "We need a discard button for items
        #: so we can trash them. Like if our bags fill up mid dungeon", and
        #: then: "Allow quest items to be destroyed too."
        #:
        #: A MODE rather than a per-item button, because a plain click on a bag
        #: slot already means four different things depending on what is in it -
        #: equip the gear, learn the recipe scroll, open the quest offer on a
        #: starter item, or confirm-destroy anything else. Hanging discard off
        #: that click would need a fifth special case per type, and the two
        #: types that already steal the click (recipe scrolls and quest
        #: starters) could never be discarded at all - which is exactly the gap
        #: Kyle hit on quest items.
        #:
        #: With a mode, ONE check at the top of the slot handler covers every
        #: item in the bag uniformly, and nothing needs to know what type it is.
        #: It clears itself after a single discard so it cannot be left armed.
        self.discard_mode = False
        self.discard_button = pygame.Rect(INV_START_X, 62, 150, 30)

        # Gear/Materials tab toggle (Gathering Phase 1). Materials get
        # their own tab rather than sharing the gear backpack grid -
        # they're a different List (Character.materials, not .inventory),
        # non-equippable, and the gear grid is already dense (17 gear
        # slots + 4 bag slots + backpack + stats summary). "gear" is the
        # default so nothing about the existing flow changes for anyone
        # who never touches gathering.
        self.active_tab = "gear"
        # Three tabs now, shifted left so the row still clears the Close button
        # at SCREEN_WIDTH-120.
        self.gear_tab_button = pygame.Rect(SCREEN_WIDTH - 560, 20, 100, 36)
        self.materials_tab_button = pygame.Rect(SCREEN_WIDTH - 450, 20, 130, 36)
        self.consumables_tab_button = pygame.Rect(SCREEN_WIDTH - 310, 20, 140, 36)
        self.materials_rects = []  # list of pygame.Rect, index-aligned to subject.materials
        # CONSUMABLES HAD NO HOME IN THE BAG AT ALL. Kyle, 2026-10-31: "i have
        # tough jerky (food) in my inventory but there is no way to use it. I
        # dont see it in my actual inventory unless im trying to sell it."
        # He was right on both counts and they are the same bug: a Character
        # keeps THREE separate lists - .inventory (gear + loot), .materials and
        # .consumables - and this screen only ever rendered the first two. The
        # vendor's _player_stock() merges all three, which is exactly why food
        # was visible when selling and nowhere else. The only path to USING one
        # was Skills -> Core tab -> scroll past every ability -> drag to the
        # hotbar -> trigger it in combat, which is no path at all for a meal
        # you want to eat standing in a field.
        self.consumables_rects = []  # index-aligned to subject.consumables

        self._build_slot_rects()

    def set_subject(self, character, return_state=None):
        """Point the screen at a character (party screen uses this)."""
        self.subject = character
        self.equip_error = None
        self.selected_item = None
        self.pending_destroy_item = None
        self.discard_mode = False
        self.active_tab = "gear"
        if return_state is not None:
            self.return_state = return_state

    def _get_subject(self):
        """The character being geared - the player unless told otherwise."""
        return self.subject or self.state_manager.player

    def _bag_source(self, subject):
        """Whose bag the backpack grid draws from and equips out of.

        Gearing yourself: your own bag, as you'd expect.
        Gearing a companion: still the PLAYER's bag - per Kyle, "we just
        equip the party member from our inventory" for now. Each character
        does own their own persistent inventory (that's the real change
        this session), but the one exception is this equip flow: loot
        always drops into the player's bag (see combat_engine.py), and
        handing a piece to a companion is done by equipping it onto them
        directly from here, same UX as before. A companion's own
        inventory can still hold things by other means (a later "give
        item" trade action, vendor purchases once companions can shop,
        etc) - this screen just doesn't source FROM a companion's own bag
        when gearing them, since nothing currently puts loot there.
        """
        player = self.state_manager.player
        return player if subject is not player else subject

    def _consumable_source(self, subject):
        """Whose consumable list the Consumables tab draws from: ALWAYS the player's.

        Kyle, 2026-10-31: "we cant make party members consume stuff. when i buy
        food, freja cant eat it as its not in her inventory."

        Exactly the same shape as _bag_source above, and for the same reason.
        Every path that acquires a consumable - the vendor, loot, crafting -
        puts it in the PLAYER's list, and nothing anywhere puts one in a
        companion's. So a companion's list is not "empty right now", it is
        empty permanently and by construction; drawing the tab from it meant
        the tab could only ever be blank for five of your six characters.

        Food and potions are party stores, the way currency already is (see the
        note on Character.add_currency about moving gold onto the party for
        this same reason). The subject still has to be ABLE to use the thing -
        level, cooldown and buff-slot checks all run against them, not the
        player - only the stack it comes out of is shared.
        """
        return self.state_manager.player

    def _equip_on_subject(self, subject, item):
        """Equip an item from the bag source (see _bag_source) onto the
        subject. Returns True on success. If the subject isn't the bag's
        owner (gearing a companion from the player's bag), the item is
        handed across first - Character.equip_item() requires the item to
        already be in ITS OWN inventory, so a plain call would silently
        fail for a companion since the item lives in the player's list."""
        # Non-gear items (QuestItem, and any future non-equippable bag
        # object) short-circuit here rather than falling into can_equip,
        # which only knows to check armor_type/weapon_type and would
        # otherwise reject them with a confusing "cannot equip None"
        # message instead of a real explanation.
        if not getattr(item, "is_gear", True):
            self.equip_error = f"{item.name} cannot be equipped."
            self.equip_error_timer = 3.0
            return False

        from entities.proficiency import can_equip

        allowed, reason = can_equip(subject, item)
        if not allowed:
            self.equip_error = reason or f"{subject.name} cannot equip that."
            self.equip_error_timer = 3.0
            return False

        source = self._bag_source(subject)
        if source is subject:
            return subject.equip_item(item)

        # Hand the item from the source (player) to the subject
        # (companion), equip it there, and undo the handoff if it somehow
        # fails after passing can_equip (e.g. a race on inventory state) -
        # the item should never just vanish between the two bags.
        if item not in source.inventory:
            return False
        source.inventory.remove(item)
        subject.inventory.append(item)
        equipped = subject.equip_item(item)
        if not equipped:
            subject.inventory.remove(item)
            source.inventory.append(item)
        return equipped

    def _build_slot_rects(self):
        for slot_key, label, col, row in SLOT_LAYOUT:
            x = SLOT_START_X + col * SLOT_COL_SPACING
            y = SLOT_START_Y + row * SLOT_ROW_SPACING
            self.slot_rects[slot_key] = pygame.Rect(x, y, SLOT_BOX_W, SLOT_BOX_H)

        # Bag row - sits just under the 6-row gear column (ends at
        # SLOT_START_Y + 6*SLOT_ROW_SPACING = 360), its own small square
        # slots rather than the wide label-boxes gear uses, since a bag
        # icon needs no label text next to it the way "Main Hand" does.
        # Merged into the SAME self.slot_rects dict as gear, not a separate
        # one - so the existing equip/unequip click loop in handle_event()
        # (which already iterates self.slot_rects generically) handles bag
        # clicks with zero extra code.
        bag_row_y = SLOT_START_Y + 6 * SLOT_ROW_SPACING
        for i, (slot_key, label) in enumerate(BAG_SLOT_LAYOUT):
            x = SLOT_START_X + i * (BAG_SLOT_SIZE + BAG_SLOT_GAP)
            self.slot_rects[slot_key] = pygame.Rect(x, bag_row_y, BAG_SLOT_SIZE, BAG_SLOT_SIZE)

    #: Where a slot scrolled out of view is parked: it draws nowhere and no click reaches it.
    OFF_SCREEN = -4000

    def _grid(self, count, cols, size, gap, x0, y0):
        """Slot rects for a grid of `count`, scrolled by self.grid_scroll rows.

        THE BAG SCROLLS. The grid was laid straight down the screen with nothing to move it,
        so a seventh row was drawn below the bottom edge (playtest, 12 Nov: "there is no way to
        scroll down in the inventory so if you have six rows full you can't see anything else
        below that"). Mouse wheel or Page Up / Page Down; rows out of view are parked off
        screen rather than dropped, so every rect still lines up with its item by index."""
        step = size + gap
        fit = max(1, (SCREEN_HEIGHT - 8 - y0 + gap) // step)
        rows = (count + cols - 1) // cols
        self.grid_rows_hidden = max(0, rows - fit)
        self.grid_scroll = max(0, min(getattr(self, "grid_scroll", 0), self.grid_rows_hidden))
        rects = []
        for i in range(count):
            row = i // cols - self.grid_scroll
            y = y0 + row * step if 0 <= row < fit else self.OFF_SCREEN
            rects.append(pygame.Rect(x0 + (i % cols) * step, y, size, size))
        return rects

    def _draw_scroll_hint(self, screen, x0, y0, width):
        """A thin bar at the right of the grid, only when there is more than fits."""
        hidden = getattr(self, "grid_rows_hidden", 0)
        if not hidden:
            return
        track = pygame.Rect(x0 + width + 6, y0, 6, SCREEN_HEIGHT - 8 - y0)
        pygame.draw.rect(screen, (40, 40, 48), track, border_radius=3)
        shown = track.height / (track.height + hidden * 98.0)
        knob_h = max(30, int(track.height * shown))
        knob_y = track.y + int((track.height - knob_h) * self.grid_scroll / hidden)
        pygame.draw.rect(screen, COLOR_GOLD, (track.x, knob_y, track.width, knob_h), border_radius=3)

    def _build_inventory_rects(self, count):
        self.inventory_rects = self._grid(count, INV_GRID_COLS, INV_SLOT_SIZE, INV_SLOT_SPACING,
                                          INV_START_X, INV_START_Y)

    def _build_materials_rects(self, count):
        """Grid layout for the Materials tab. Uses a wider column count
        and starts near the top-left, unlike the gear tab's backpack grid
        (INV_START_X=600) which has to squeeze in next to the gear panel
        - the materials tab has the WHOLE screen to itself, no gear grid
        sharing the view, so it gets more breathing room."""
        self.materials_rects = self._grid(count, MATERIALS_GRID_COLS, MATERIALS_SLOT_SIZE,
                                          MATERIALS_SLOT_SPACING, MATERIALS_START_X, MATERIALS_START_Y)

    def _build_consumables_rects(self, count):
        """Grid layout for the Consumables tab - the same geometry as the
        Materials tab, deliberately. Both are full-screen single-grid views of
        a flat stackable list, so giving them different column counts or slot
        sizes would be two layouts for one job and the tabs would jump under
        the cursor as you switched between them."""
        self.consumables_rects = self._grid(count, MATERIALS_GRID_COLS, MATERIALS_SLOT_SIZE,
                                            MATERIALS_SLOT_SPACING, MATERIALS_START_X, MATERIALS_START_Y)

    def _use_consumable(self, subject, consumable):
        """Click-to-use from the bag. Mirrors what the combat hotbar does with
        the same object, minus the combat log - Consumable.use() is the single
        implementation and this is just a second door into it, so an out-of-
        combat meal and an in-combat potion can never diverge on what they do.

        can_use() is asked FIRST and its refusal is surfaced. use() returning
        False silently is how 'I clicked my food and nothing happened' becomes
        a bug report instead of a rule the player can learn."""
        if consumable.required_level > subject.level:
            self.equip_error = f"{consumable.name} requires level {consumable.required_level}."
            self.equip_error_timer = 3.0
            return
        if not consumable.can_use(subject):
            # The three reasons can_use says no, named rather than lumped into
            # "you can't use that" - each one tells the player a different thing
            # to do about it.
            if (subject.consumable_cooldown > 0
                    and consumable.consumable_type not in ("meal", "drink")):
                self.equip_error = f"On cooldown ({subject.consumable_cooldown:.0f}s)."
            elif consumable.buff_category == "guardian" and subject.guardian_buff is not None:
                self.equip_error = "A guardian elixir is already active."
            elif consumable.buff_category == "battle" and subject.battle_buff is not None:
                self.equip_error = "A battle elixir is already active."
            else:
                self.equip_error = f"{subject.name} cannot use {consumable.name} right now."
            self.equip_error_timer = 3.0
            return

        if consumable.use(subject):
            self.equip_error = f"Used {consumable.name}."
            # use() decrements the stack; an empty one leaves a dead slot in the
            # grid that still hovers and still accepts clicks, so it goes here.
            pool = self._consumable_source(subject).consumables
            if consumable.quantity <= 0 and consumable in pool:
                pool.remove(consumable)
        else:
            self.equip_error = f"{consumable.name} had no effect."
        self.equip_error_timer = 3.0

    def handle_event(self, event):
        subject = self._get_subject()

        # Scroll the grid: wheel, or Page Up / Page Down.
        step = 0
        if event.type == pygame.MOUSEWHEEL:
            step = -event.y
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_PAGEDOWN, pygame.K_PAGEUP):
            step = 3 if event.key == pygame.K_PAGEDOWN else -3
        if step:
            self.grid_scroll = max(0, min(getattr(self, "grid_rows_hidden", 0),
                                          getattr(self, "grid_scroll", 0) + step))
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.pending_destroy_item is not None:
                self.pending_destroy_item = None
                return
            if self.discard_mode:
                # Escape disarms rather than closing the bag - leaving the
                # screen with discard still armed is how an accidental
                # destroy happens on the next visit.
                self.discard_mode = False
                return
            self._close()
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Destroy-confirmation takes over all clicks while pending -
            # nothing else in the bag/equipment grid should be
            # clickable until this resolves, same modal convention as
            # the gear-choice picker in QuestDialogScreen.
            if self.pending_destroy_item is not None:
                if self.destroy_yes_button.collidepoint(mouse_pos):
                    item = self.pending_destroy_item
                    # Remove from the bag the GRID DREW FROM, not from
                    # subject.inventory. Gearing a companion draws the PLAYER's
                    # bag (see _bag_source), so removing from the subject found
                    # nothing, left the item sitting in the player's bag, and
                    # still reported "destroyed." A silent no-op with a success
                    # message - the same two-lists-one-job shape as the unequip
                    # void bug on 2 Nov.
                    bag = self._bag_source(subject)
                    if item in bag.inventory:
                        bag.inventory.remove(item)
                    elif item in subject.inventory:
                        subject.inventory.remove(item)
                    self.pending_destroy_item = None
                    self.equip_error = f"{item.name} destroyed."
                    self.equip_error_timer = 2.5
                elif self.destroy_no_button.collidepoint(mouse_pos):
                    self.pending_destroy_item = None
                return

            if self.close_button.collidepoint(mouse_pos):
                self._close()
                return

            if self.discard_button.collidepoint(mouse_pos) and self.active_tab == "gear":
                self.discard_mode = not self.discard_mode
                self.selected_item = None
                return

            # Tab toggle - checked before any gear/bag click handling
            # below, and returns immediately either way so a tab click
            # never also falls through and hits a gear slot underneath it.
            if self.gear_tab_button.collidepoint(mouse_pos):
                self.active_tab = "gear"
                self.grid_scroll = 0
                self.selected_item = None
                self.discard_mode = False
                return
            if self.materials_tab_button.collidepoint(mouse_pos):
                self.active_tab = "materials"
                self.grid_scroll = 0
                self.selected_item = None
                self.discard_mode = False
                return
            if self.consumables_tab_button.collidepoint(mouse_pos):
                self.active_tab = "consumables"
                self.grid_scroll = 0
                self.selected_item = None
                self.discard_mode = False
                return

            # Consumables tab: a click USES the thing, unlike the materials
            # tab's look-but-don't-touch grid. That is the whole point of the
            # tab existing - see _use_consumable.
            if self.active_tab == "consumables":
                for i, rect in enumerate(self.consumables_rects):
                    pool = self._consumable_source(subject).consumables
                    if rect.collidepoint(mouse_pos) and i < len(pool):
                        self._use_consumable(subject, pool[i])
                        return
                return

            # Materials tab has no click actions yet (Phase 1 has no
            # crafting to consume them into, no sell-from-bag flow wired
            # for materials specifically) - clicking a material currently
            # does nothing but is still visible/hoverable for its
            # tooltip, same "look but no action yet" state consumables
            # were already in before this session.
            if self.active_tab == "materials":
                return

            # Click an equipped slot -> unequip, back into the SAME bag this
            # screen equips out of (_bag_source: the player's, when gearing a
            # companion). It used to go into the companion's own inventory,
            # which this screen never draws - Kyle, 2 Nov: "when i unequip
            # party gear its lost in the void." Equip and unequip have to use
            # the same bag or the item makes a one-way trip.
            for slot_key, rect in self.slot_rects.items():
                if rect.collidepoint(mouse_pos):
                    item = subject.equipment.get_equipped(slot_key)
                    if item:
                        subject.last_refusal = None
                        if not subject.unequip_item(slot_key, into=self._bag_source(subject)):
                            # a recruit who won't hand it over says so in their own words
                            refusal = getattr(subject, "last_refusal", None)
                            if refusal:
                                self.equip_error = f"{subject.name}: \"{refusal}\""
                                self.equip_error_timer = 4.0
                                self.selected_item = None
                                return
                            # A refused unequip has to SAY so. The old code
                            # appended past inventory_capacity and silently
                            # overflowed; it refuses now, and a refusal the
                            # player cannot see is the void bug in a new hat.
                            # Reuses the screen's existing error toast rather
                            # than adding a second one beside it.
                            self.equip_error = "Backpack is full - make room first."
                            self.equip_error_timer = 3.0
                        self.selected_item = None
                    return

            # Click a bag item -> equip it onto the subject, sourced from
            # _bag_source (the player's bag when gearing a companion - see
            # that method's docstring for why). Non-gear items (LootItem:
            # quest items, materials, trash) can never be equipped, so
            # clicking one opens the destroy-confirmation instead of the
            # old "cannot be equipped" toast - that toast fired every
            # single click and never gave the player anything useful to
            # DO about an item they can't equip and (for quest items)
            # can't sell either.
            bag = self._bag_source(subject)
            self._build_inventory_rects(len(bag.inventory))
            for i, rect in enumerate(self.inventory_rects):
                if rect.collidepoint(mouse_pos) and i < len(bag.inventory):
                    item = bag.inventory[i]

                    # DISCARD MODE WINS, before any type-specific handling.
                    # This single line is what makes gear, recipe scrolls and
                    # quest-starter items discardable - all three previously
                    # consumed the click for something else and could never be
                    # trashed. Kyle: "Allow quest items to be destroyed too."
                    if self.discard_mode:
                        self.pending_destroy_item = item
                        self.discard_mode = False
                        return

                    if not getattr(item, "is_gear", True):
                        # Recipe scroll: right-click to learn the recipe it contains.
                        if getattr(item, "recipe_id", None):
                            self._use_recipe_scroll(subject, bag, item)
                            return
                        # A quest-STARTER item (a drop that begins a quest) opens its quest offer instead.
                        starts = getattr(item, "starts_quest_id", None)
                        if starts:
                            from world.quest_manager import get_quest_manager
                            from world.quest import QuestStatus, ItemQuestGiver
                            qm = get_quest_manager()
                            q = qm.quests.get(starts)
                            if q is not None and q.status == QuestStatus.NOT_STARTED and qm._is_unlocked(starts):
                                self.state_manager.transition_to(GameState.QUEST_DIALOG,
                                                                 current_quest_npc=ItemQuestGiver(item))
                                return
                        self.pending_destroy_item = item
                        return
                    self._equip_on_subject(subject, item)
                    self.selected_item = None
                    return

    def _use_recipe_scroll(self, character, bag, item):
        """Handle clicking a recipe scroll item in inventory.

        WoW rules:
        - If recipe already known → show error, item stays in bag.
        - If profession not learned → show error, item stays.
        - If skill too low → show greyed error ("Requires Blacksmithing 75"), item stays.
        - If all requirements met → learn recipe, remove scroll from bag, show success.
        """
        recipe_id = item.recipe_id
        profession = item.recipe_profession

        # Pull skill_required from the recipe data
        try:
            from world.recipe_manager import get_recipe_info
            _, recipe_data = get_recipe_info(recipe_id)
            skill_req = recipe_data.get("skill_required", 0) if recipe_data else 0
        except Exception:
            skill_req = 0

        ok, msg = character.learn_recipe(recipe_id, profession, skill_required=skill_req)
        if ok:
            # Remove the scroll from the bag now that it's been learned
            bag.inventory.remove(item)
            self.equip_error = f"Learned: {item.name.replace('Plans: ', '').replace('Pattern: ', '').replace('Recipe: ', '').replace('Schematic: ', '')}"
        else:
            self.equip_error = msg
        self.equip_error_timer = 3.0

    def _close(self):
        """Return where we came from, and always release the subject."""
        destination = self.return_state or GameState.OVERWORLD
        self.subject = None
        self.return_state = GameState.OVERWORLD
        self.equip_error = None
        self.pending_destroy_item = None
        self.state_manager.transition_to(destination)

    def update(self, dt):
        if self.equip_error_timer > 0:
            self.equip_error_timer -= dt
            if self.equip_error_timer <= 0:
                self.equip_error = None

    def _draw_item_icon(self, screen, item, rect, size=None):
        """Blit item.icon_id's real art into rect if the icon system has
        it, sized to fit. Returns True if something was drawn (caller
        skips/adjusts its text fallback), False otherwise - most
        procedural items before this session had no icon_id at all and
        still render as a colored box + name text, which stays correct
        for anything gear_icons.py couldn't match."""
        if not self.icon_ui_helper or not getattr(item, "icon_id", None):
            return False
        size = size or min(rect.width, rect.height) - 4
        try:
            item_data = {"name": item.name, "icon_id": item.icon_id,
                        "rarity": getattr(item, "rarity", "common")}
            surface = self.icon_ui_helper.get_item_icon_surface(item_data, size=size)
            if surface:
                screen.blit(surface, (rect.x + (rect.width - size) // 2,
                                      rect.y + (rect.height - size) // 2))
                return True
        except Exception:
            pass
        return False

    def _draw_material_icon(self, screen, material, rect, size=None):
        """Blit a gathered material's real sprite into rect. Materials
        use their own flat asset files under assets/gathering_nodes/
        (not the gear icon system _draw_item_icon routes through - that
        pipeline is built around gear_icons.py's rarity-tinted item art,
        a different asset shape entirely), so this goes straight through
        get_tile_sprite - the SAME lookup function the overworld renderer
        already uses to draw these exact files on the ground, so there's
        no chance of the bag and the world disagreeing on what a
        material's icon path is. Returns True if something was drawn."""
        if not getattr(material, "icon_id", None):
            return False
        size = size or min(rect.width, rect.height) - 8
        folder = MATERIAL_TYPE_FOLDERS.get(material.material_type, material.material_type)
        sheet_path = f"assets/gathering_nodes/{folder}/{material.icon_id}.png"
        sprite = get_tile_sprite(sheet_path, (0, 0, 32, 32), size)
        if sprite is not None:
            screen.blit(sprite, (rect.x + (rect.width - size) // 2,
                                 rect.y + (rect.height - size) // 2))
            return True
        return False

    def render(self, screen):
        subject = self._get_subject()
        bag = self._bag_source(subject)
        self._build_inventory_rects(len(bag.inventory))
        self._draw_scroll_hint(screen, INV_START_X, INV_START_Y, INV_GRID_COLS * (INV_SLOT_SIZE + INV_SLOT_SPACING))

        # Title names the subject when gearing a companion, so there is no
        # chance of dressing the wrong character without noticing.
        player = self.state_manager.player
        if subject is player:
            title = "INVENTORY & EQUIPMENT" if self.active_tab == "gear" else "MATERIALS"
        else:
            # A COMPANION'S NAME IS THE TITLE. Kyle, 2026-10-31: "there is a lot of weird overlap
            # in the top of the party screen." The old wording was "EINO VIRTANEN'S INVENTORY &
            # EQUIPMENT - Lv 32 Barbarian", drawn at size="large" with no width limit, so it ran
            # straight through the "Backpack 0/24" header at x=600 AND the tab buttons beyond it.
            # The tabs already say which screen this is, so the words that were overflowing were
            # the ones carrying no information.
            title = (f"{subject.name.upper()}  -  Lv {subject.level} {subject.char_class}"
                     if self.active_tab == "gear" else f"{subject.name.upper()} - MATERIALS")
        # Hard-truncated to stop short of the backpack column whatever the name, because a long
        # name is a thing players make and a fixed layout is a thing we chose.
        title = self.renderer.truncate(title, INV_START_X - 40, size="large")
        self.renderer.draw_text(screen, title, (20, 20), size="large", color=COLOR_GOLD)

        # ---- Tab buttons - always visible regardless of active tab ----
        gear_color = COLOR_GOLD if self.active_tab == "gear" else (90, 90, 95)
        materials_color = COLOR_GOLD if self.active_tab == "materials" else (90, 90, 95)
        self.renderer.draw_rect(screen, self.gear_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.gear_tab_button, gear_color, fill=False)
        self.renderer.draw_text(screen, "Gear", (self.gear_tab_button.x + 28, self.gear_tab_button.y + 9), color=gear_color)
        self.renderer.draw_rect(screen, self.materials_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.materials_tab_button, materials_color, fill=False)
        self.renderer.draw_text(screen, "Materials", (self.materials_tab_button.x + 14, self.materials_tab_button.y + 9), color=materials_color)
        cons_color = COLOR_GOLD if self.active_tab == "consumables" else (90, 90, 95)
        self.renderer.draw_rect(screen, self.consumables_tab_button, (35, 35, 40))
        self.renderer.draw_rect(screen, self.consumables_tab_button, cons_color, fill=False)
        self.renderer.draw_text(screen, "Consumables",
                                (self.consumables_tab_button.x + 10, self.consumables_tab_button.y + 9),
                                color=cons_color)

        if self.active_tab == "consumables":
            self._render_consumables_tab(screen, subject)
            return

        if self.active_tab == "materials":
            self._render_materials_tab(screen, subject)
            self.renderer.draw_button(screen, self.close_button, "Close")
            return

        # ---- Equipped slots panel ----
        for slot_key, label, col, row in SLOT_LAYOUT:
            rect = self.slot_rects[slot_key]
            item = subject.equipment.get_equipped(slot_key)

            if item:
                color = item.get_rarity_color()
                self.renderer.draw_rect(screen, rect, (40, 40, 45))
                self.renderer.draw_rect(screen, rect, color, fill=False)
                icon_drawn = self._draw_item_icon(
                    screen, item, pygame.Rect(rect.x + 2, rect.y + 18, 24, 24))
                text_x = rect.x + (32 if icon_drawn else 6)
                self.renderer.draw_text(screen, label, (rect.x + 6, rect.y + 2), color=COLOR_LIGHT_GRAY)
                # Fit to whatever width is left in the slot box after the
                # icon, measured rather than guessed - a long name used to
                # run straight out of the box and over the next column.
                name = self.renderer.truncate(item.name, rect.right - text_x - 6)
                self.renderer.draw_text(screen, name, (text_x, rect.y + 20), color=color)
            else:
                self.renderer.draw_rect(screen, rect, (25, 25, 28))
                self.renderer.draw_rect(screen, rect, (70, 70, 70), fill=False)
                self.renderer.draw_text(screen, label, (rect.x + 6, rect.y + 12), color=(120, 120, 120))

        # ---- Bag row (WoW-style: 4 equippable bag slots that expand
        # capacity) - drawn separately from the gear grid above since these
        # are small square icon slots, not labeled gear rows. Always the
        # SUBJECT's own bag slots (bag capacity belongs to whoever wears
        # the bags), even though the backpack grid below may be showing
        # the player's items when gearing a companion.
        for slot_key, label in BAG_SLOT_LAYOUT:
            rect = self.slot_rects[slot_key]
            item = subject.equipment.get_equipped(slot_key)
            if item:
                color = item.get_rarity_color()
                self.renderer.draw_rect(screen, rect, (40, 40, 45))
                self.renderer.draw_rect(screen, rect, color, fill=False)
                icon_drawn = self._draw_item_icon(screen, item, rect, size=rect.width - 8)
                if not icon_drawn:
                    self.renderer.draw_text(screen, self.renderer.truncate(item.name, rect.width - 8, size="small"),
                                            (rect.x + 4, rect.y + 4),
                                            size="small", color=color)
                self.renderer.draw_text(screen, f"+{item.bag_capacity}",
                                        (rect.x + 4, rect.bottom - 16),
                                        size="small", color=COLOR_WHITE)
            else:
                self.renderer.draw_rect(screen, rect, (25, 25, 28))
                self.renderer.draw_rect(screen, rect, (70, 70, 70), fill=False)
                self.renderer.draw_text(screen, label, (rect.x + 4, rect.y + 4),
                                        size="small", color=(120, 120, 120))

        # ---- Unequipped inventory grid ---- sourced from _bag_source:
        # your own bag normally, the PLAYER's bag when gearing a companion
        # (see _bag_source's docstring). Labeled so it's never ambiguous
        # whose items are on screen.
        used = len(bag.inventory)
        capacity = bag.inventory_capacity
        cap_color = (220, 120, 90) if used >= capacity else COLOR_GOLD
        bag_label = "Backpack" if bag is subject else f"{bag.name}'s Backpack"
        # Truncated to the gap before the Gear tab. Gearing a companion makes
        # this label carry the owner's NAME, and the longer string ran straight
        # under the tab button - "Hero's Backpack (6/24)" already overlapped,
        # and recruits with real names ("Codex-Master Ilarien Duskwaking") are
        # far longer than that. Measured against the tab's actual left edge
        # rather than a guessed width, so moving the tabs cannot re-break it.
        # Sits on the Discard row, not above it. At y=30 there are only ~110px
        # before the Gear tab, which fits "Backpack (6/24)" and nothing longer
        # - and truncating to fit ate the "(6/24)", which is the one number
        # that matters when the bag is filling up mid-dungeon. Beside the
        # Discard button there is three times the room, so the count survives
        # even for a recruit with a long name.
        bag_text = f"{bag_label} ({used}/{capacity})"
        bag_x = self.discard_button.right + 14
        bag_text = self.renderer.truncate(bag_text, max(80, SCREEN_WIDTH - 200 - bag_x))
        self.renderer.draw_text(screen, bag_text, (bag_x, self.discard_button.y + 6),
                                color=cap_color)

        # Discard toggle. Red and obviously armed when active, because the
        # next bag click destroys something and the player must be able to
        # tell at a glance that the bag is in that state.
        if self.discard_mode:
            btn_bg, btn_border, btn_fg = (90, 30, 30), (230, 110, 110), (255, 220, 220)
            btn_label = "Click an item"
        else:
            btn_bg, btn_border, btn_fg = (40, 30, 30), (140, 100, 100), (210, 170, 170)
            btn_label = "Discard"
        pygame.draw.rect(screen, btn_bg, self.discard_button)
        pygame.draw.rect(screen, btn_border, self.discard_button, 2 if self.discard_mode else 1)
        lw = self.renderer._get_font(font_size=16).size(btn_label)[0]
        self.renderer.draw_text(screen, btn_label,
                                (self.discard_button.centerx - lw // 2,
                                 self.discard_button.y + 7),
                                color=btn_fg, font_size=16)

        # MONEY LIVES HERE TOO, NOT ONLY AT A VENDOR. Kyle, 2 Nov: "we need to
        # be able to see our copper, silver, and gold in our inventory
        # (currently its only seen in vendors)." Knowing what you can afford is
        # a thing you want while looking at your bags and deciding what to keep,
        # which is the one place it was not shown.
        #
        # The purse is Party.copper - ONE shared pool, not a wallet per
        # character - so this reads the same number whoever's bag is on screen.
        # Showing a companion's own total here would invent a second wallet
        # that does not exist.
        #
        # format_coins is the UI's shared g/s/c formatter, the one the vendor
        # panel uses. This screen must not grow its own: two formatters is how
        # 300c comes to print as "300c" in one place and "3s" in another.
        from ui.coin_format import format_coins
        party = getattr(self.state_manager, "get_party", lambda: None)()
        purse = getattr(party, "copper", None)
        if purse is None:
            purse = getattr(self.state_manager.player, "copper", 0) or 0
        text = format_coins(purse)
        tw = self.renderer._get_font(font_size=16).size(text)[0]
        # BELOW the tab row, not beside it. The three tabs span y=20..56 from
        # x=SCREEN_WIDTH-560 to -170 and the Close button takes -120 onward, so
        # the whole of that line is already spoken for - drawing the purse at
        # y=30 put "12g 34s 56c" straight through the Consumables tab. The band
        # between the tabs and the item grid (INV_START_Y=100) is empty.
        self.renderer.draw_text(screen, text, (SCREEN_WIDTH - 30 - tw, 66),
                                font_size=16, color=COLOR_GOLD)

        if not bag.inventory:
            self.renderer.draw_text(screen, "No items yet - defeat creatures to find loot.", (INV_START_X, INV_START_Y), color=(150, 150, 150))
        else:
            for i, item in enumerate(bag.inventory):
                rect = self.inventory_rects[i]
                color = item.get_rarity_color()
                self.renderer.draw_rect(screen, rect, (35, 35, 40))
                self.renderer.draw_rect(screen, rect, color, fill=False)

                icon_drawn = self._draw_item_icon(screen, item, rect, size=rect.width - 10)
                # QuestItem has no item_level - shows its stack quantity
                # in that corner instead, which is the more useful readout
                # for a stackable non-gear item anyway.
                corner_text = (f"x{getattr(item, 'quantity', 1)}" if not getattr(item, "is_gear", True)
                               else f"ilvl {item.item_level}")
                if not icon_drawn:
                    # Text fallback for anything without real icon art yet
                    # (procedural gear gear_icons.py couldn't match, or an
                    # older save item generated before this system).
                    display_name = self.renderer.truncate(item.name, rect.width - 8)
                    self.renderer.draw_text(screen, display_name, (rect.x + 4, rect.y + 4), color=color)
                    self.renderer.draw_text(screen, corner_text, (rect.x + 4, rect.y + rect.height - 20), color=(180, 180, 180))
                else:
                    # Icon art shown - ilvl (or quantity) still worth a
                    # small corner readout so browsing doesn't require
                    # hovering every single item.
                    corner_short = (f"x{getattr(item, 'quantity', 1)}" if not getattr(item, "is_gear", True)
                                    else str(item.item_level))
                    self.renderer.draw_text(screen, corner_short,
                                            (rect.x + 3, rect.bottom - 16),
                                            size="small", color=(220, 220, 220))

        # ---- Stat comparison / detail panel (hover-based, simple version) ----
        mouse_pos = pygame.mouse.get_pos()
        hovered_item = self._get_hovered_item(mouse_pos, subject, bag)
        # Drawn at the END of this method, not here. It used to be drawn at this point, and
        # everything after it - the EFFECTIVE STATS block, the equip error, the Close button -
        # was then painted over the top, so hovering a piece of equipped gear gave a card with
        # the character's stats written through it. Kyle, 10 Nov: item cards must be opaque.

        # ---- Current effective stats summary ----
        # Below the bag row now (SLOT_START_Y + 6*SLOT_ROW_SPACING +
        # BAG_SLOT_SIZE), not just below the 6-row gear grid - the bag row
        # sits between them and would otherwise get overdrawn.
        summary_y = SLOT_START_Y + 6 * SLOT_ROW_SPACING + BAG_SLOT_SIZE + 20
        self.renderer.draw_text(screen, "EFFECTIVE STATS", (20, summary_y), color=COLOR_GOLD)
        summary_y += 30
        self.renderer.draw_text(screen, f"STR {int(subject.effective_strength)}  STA {int(subject.effective_stamina)}  INT {int(subject.effective_intellect)}  SPI {int(subject.effective_spirit)}  AGI {int(subject.effective_agility)}", (20, summary_y))
        summary_y += 25
        self.renderer.draw_text(screen, f"Attack Power: {subject.attack_power}   Spell Power: {subject.spell_power}   Armor: {subject.armor}", (20, summary_y))
        summary_y += 25
        self.renderer.draw_text(screen, f"HP: {subject.display_health}/{round(subject.health)}   Mana: {subject.display_mana}/{round(subject.mana)}", (20, summary_y))

        if self.equip_error:
            self.renderer.draw_text(screen, self.equip_error,
                                    (20, summary_y + 30), color=(230, 110, 110))

        self.renderer.draw_button(screen, self.close_button, "Close")

        if hovered_item and self.pending_destroy_item is None:
            in_bag = any(hovered_item is it for it in bag.inventory)
            self._draw_item_tooltip(screen, hovered_item, mouse_pos, show_sell_price=in_bag)

        if self.pending_destroy_item is not None:
            self._render_destroy_confirmation(screen)

    def _render_consumables_tab(self, screen, subject):
        """Potions, elixirs, food and drink - the third of the Character's three
        bag lists, and until now the only one with no UI at all outside the
        Skills screen's hotbar-assignment list.

        Click to use (see _use_consumable). Active buff slots are printed along
        the top, because 'why did my food do nothing' is nearly always 'you
        already have a food buff' and can_use refusing silently was how that
        read as a broken item.
        """
        self._build_consumables_rects(len(self._consumable_source(subject).consumables))
        self._draw_scroll_hint(screen, MATERIALS_START_X, MATERIALS_START_Y, MATERIALS_GRID_COLS * (MATERIALS_SLOT_SIZE + MATERIALS_SLOT_SPACING))

        # What is already running, in the same place the materials tab puts the
        # profession line - these four slots are what can_use() checks against.
        active = []
        for label, slot in (("Guardian", "guardian_buff"), ("Battle", "battle_buff"),
                            ("Food", "food_buff"), ("Ammo", "ammo_buff")):
            entry = getattr(subject, slot, None)
            if entry:
                cons = entry[0] if isinstance(entry, (tuple, list)) else entry
                secs = entry[1] if isinstance(entry, (tuple, list)) and len(entry) > 1 else None
                name = getattr(cons, "name", str(cons))
                active.append(f"{label}: {name}" + (f" ({int(secs)}s)" if secs else ""))
        cd = getattr(subject, "consumable_cooldown", 0) or 0
        if cd > 0:
            active.append(f"Potion cooldown: {cd:.0f}s")
        self.renderer.draw_text(screen,
                                "   ".join(active) if active else "No consumable buffs active.",
                                (20, 60), color=COLOR_LIGHT_GRAY)

        pool = self._consumable_source(subject).consumables
        if not pool:
            self.renderer.draw_text(
                screen, "No consumables - buy food, drink and potions from a vendor.",
                (MATERIALS_START_X, MATERIALS_START_Y), color=(150, 150, 150))
        else:
            for i, cons in enumerate(pool):
                rect = self.consumables_rects[i]
                usable = cons.required_level <= subject.level and cons.can_use(subject)
                self.renderer.draw_rect(screen, rect, (35, 35, 40))
                # Border carries usability, so an unusable stack reads as greyed
                # rather than as a thing that ignores clicks for no reason.
                self.renderer.draw_rect(screen, rect,
                                        (210, 200, 140) if usable else (80, 80, 85),
                                        fill=False)

                if not self._draw_consumable_icon(screen, cons, rect, size=rect.width - 12):
                    display_name = self.renderer.truncate(cons.name, rect.width - 8, size="small")
                    self.renderer.draw_text(screen, display_name, (rect.x + 4, rect.y + 4),
                                            size="small", color=COLOR_LIGHT_GRAY)

                self.renderer.draw_text(screen, f"x{cons.quantity}",
                                        (rect.x + 4, rect.bottom - 16),
                                        size="small", color=(220, 220, 220))

        self.renderer.draw_text(screen, "Click a consumable to use it.",
                                (MATERIALS_START_X, SCREEN_HEIGHT - 60), color=(140, 140, 150))

        # The gear tab draws this and then returns before reaching here, so the
        # message has to be repeated for this view or every refusal from
        # _use_consumable would be silent - which is the exact failure mode this
        # whole tab exists to fix.
        if self.equip_error:
            self.renderer.draw_text(screen, self.equip_error,
                                    (MATERIALS_START_X, SCREEN_HEIGHT - 34),
                                    color=COLOR_GOLD)

        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.consumables_rects):
            pool = self._consumable_source(subject).consumables
            if rect.collidepoint(mouse_pos) and i < len(pool):
                self._draw_consumable_tooltip(screen, pool[i], mouse_pos, subject)
                break

    def _draw_consumable_icon(self, screen, consumable, rect, size=None):
        """Blit a consumable's icon via icon_ui_helper, the same route the
        Skills screen and the combat hotbar use for this exact object - so the
        bag can't disagree with the hotbar about what a potion looks like.
        Returns True if something was drawn."""
        if not self.icon_ui_helper:
            return False
        size = size or min(rect.width, rect.height) - 8
        try:
            surf = self.icon_ui_helper.get_item_icon_surface(
                {"name": consumable.name, "icon_id": getattr(consumable, "icon_id", None)},
                size=size)
        except Exception:
            return False
        if not surf:
            return False
        screen.blit(surf, (rect.x + (rect.width - size) // 2,
                           rect.y + (rect.height - size) // 2))
        return True

    def _draw_consumable_tooltip(self, screen, cons, mouse_pos, subject):
        """What it does, what it costs you, and why you can't use it right now."""
        BODY_W = 300
        lines = [cons.name]
        ctype = str(cons.consumable_type).replace("_", " ").title()
        lines.append(f"{ctype}" + (f"  -  requires level {cons.required_level}"
                                   if cons.required_level else ""))
        if cons.consumable_type in ("health_potion", "mana_potion"):
            bar = "health" if cons.consumable_type == "health_potion" else "mana"
            scaled = int(cons.effect_value * (1.0 + subject.level * cons.level_multiplier))
            lines.append(f"Restores {scaled} {bar} instantly.")
        elif cons.consumable_type in ("meal", "drink"):
            bar = "health" if cons.consumable_type == "meal" else "mana"
            lines.append(f"Restores {cons.effect_value} {bar} over "
                         f"{int(cons.effect_duration)}s while you sit still.")
        if cons.stat_bonuses:
            from entities.consumable import bonus_text, WELL_FED_SECONDS
            if cons.consumable_type == "meal":           # effect_duration is how long it takes to eat
                lines.append(f"Well fed: {bonus_text(cons.stat_bonuses)} for {WELL_FED_SECONDS // 60} minutes")
            else:
                lines.append(bonus_text(cons.stat_bonuses)
                             + (f" for {int(cons.effect_duration)}s" if cons.effect_duration else ""))
        if cons.description:
            lines.extend(self.renderer.wrap_text(cons.description, BODY_W, size="small"))
        lines.append(f"Sell price: {format_coins(cons.sell_price)}")
        if cons.required_level > subject.level:
            lines.append(f"You need level {cons.required_level}.")
        elif not cons.can_use(subject):
            lines.append("Cannot be used right now.")

        padding = 8
        line_height = 20
        font = self.renderer._get_font(size="small")
        width = max(220, max(font.size(line)[0] for line in lines) + padding * 2)
        height = padding * 2 + line_height * len(lines)
        x = min(mouse_pos[0] + 16, SCREEN_WIDTH - width - 10)
        y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - height - 10)
        rect = pygame.Rect(x, y, width, height)
        self.renderer.draw_rect(screen, rect, (20, 20, 24))
        self.renderer.draw_rect(screen, rect, COLOR_GOLD, fill=False)
        for i, line in enumerate(lines):
            color = COLOR_GOLD if i == 0 else COLOR_LIGHT_GRAY
            self.renderer.draw_text(screen, line, (x + padding, y + padding + i * line_height),
                                    size="small", color=color)

    def _render_materials_tab(self, screen, subject):
        """Materials grid + profession skill readout. Kept as its own
        method (rather than inlined in render()) since it's a fully
        separate view, same reasoning _render_destroy_confirmation is
        broken out below - render() dispatches to one or the other, it
        doesn't interleave them."""
        self._build_materials_rects(len(subject.materials))
        self._draw_scroll_hint(screen, MATERIALS_START_X, MATERIALS_START_Y, MATERIALS_GRID_COLS * (MATERIALS_SLOT_SIZE + MATERIALS_SLOT_SPACING))

        # Profession skill line - the only place these numbers are
        # visible anywhere in the game right now (Phase 1 has no
        # trainer/profession-panel UI yet), so surfacing it here means
        # gaining skill from gathering has SOME visible feedback beyond
        # the toast that fires the instant you pick something.
        skills = subject.profession_skills or {}
        skill_parts = [f"{prof.title()}: {level}" for prof, level in skills.items()]
        skill_line = "  ".join(skill_parts) if skill_parts else "No gathering professions learned yet."
        self.renderer.draw_text(screen, skill_line, (20, 60), color=COLOR_LIGHT_GRAY)

        if not subject.materials:
            self.renderer.draw_text(screen, "No materials yet - gather herbs and ore out in the world.",
                                    (MATERIALS_START_X, MATERIALS_START_Y), color=(150, 150, 150))
            return

        for i, material in enumerate(subject.materials):
            rect = self.materials_rects[i]
            self.renderer.draw_rect(screen, rect, (35, 35, 40))
            self.renderer.draw_rect(screen, rect, (150, 150, 150), fill=False)

            icon_drawn = self._draw_material_icon(screen, material, rect, size=rect.width - 12)
            if not icon_drawn:
                display_name = self.renderer.truncate(material.name, rect.width - 8, size="small")
                self.renderer.draw_text(screen, display_name, (rect.x + 4, rect.y + 4),
                                        size="small", color=COLOR_LIGHT_GRAY)

            self.renderer.draw_text(screen, f"x{material.quantity}",
                                    (rect.x + 4, rect.bottom - 16),
                                    size="small", color=(220, 220, 220))

        # Hover tooltip - name, profession/tier, flavor text. Reuses the
        # same mouse-position pattern as the gear tab's item tooltip, just
        # against materials_rects/subject.materials instead of
        # inventory_rects/bag.inventory.
        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.materials_rects):
            if rect.collidepoint(mouse_pos) and i < len(subject.materials):
                self._draw_material_tooltip(screen, subject.materials[i], mouse_pos)
                break

    def _draw_material_tooltip(self, screen, material, mouse_pos):
        """Small hover tooltip for a material - name, profession/tier,
        flavor text, sell price. Deliberately simpler than
        _draw_item_tooltip (no stat comparison - materials have no
        stats), same "just enough info to know what you're looking at"
        scope as the rest of Phase 1."""
        # WRAP THE DESCRIPTION, DON'T GUESS AT IT. Kyle, 2026-10-31: "words are
        # running off." The box used to be sized as `max line length * 7px` with
        # nothing ever wrapped, so a one-word name set a 220px box and then a
        # full sentence of flavour text was drawn straight through its right
        # edge ("Vendor trash. Worth a few coppers to any merchant."). The body
        # is drawn at size="small", so it is wrapped at size="small" too - see
        # the note on Renderer.wrap_text about measuring the font you draw with.
        BODY_W = 300
        lines = [
            material.name,
            # What it is FOR, and nothing about "tiers". Kyle, 10 Nov: the card "dont need to
            # advertise its 'mid-tier'".
            material.profession.replace("_", " ").title(),
        ]
        if material.description:
            lines.extend(self.renderer.wrap_text(material.description, BODY_W, size="small"))
        lines.append(f"Sell price: {format_coins(material.sell_price)}")

        padding = 8
        line_height = 20
        font = self.renderer._get_font(size="small")
        width = max(220, max(font.size(line)[0] for line in lines) + padding * 2)
        height = padding * 2 + line_height * len(lines)
        x = min(mouse_pos[0] + 16, SCREEN_WIDTH - width - 10)
        y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - height - 10)
        rect = pygame.Rect(x, y, width, height)

        self.renderer.draw_rect(screen, rect, (20, 20, 24))
        self.renderer.draw_rect(screen, rect, COLOR_GOLD, fill=False)
        for i, line in enumerate(lines):
            color = COLOR_GOLD if i == 0 else COLOR_LIGHT_GRAY
            self.renderer.draw_text(screen, line, (x + padding, y + padding + i * line_height),
                                    size="small", color=color)

    def _render_destroy_confirmation(self, screen):
        """Modal Yes/No confirmation before actually removing an item -
        destruction is permanent (no undo, no vendor sell-back for a
        quest item), so this always gets an explicit confirm step rather
        than destroying on the first click."""
        item = self.pending_destroy_item
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        box_w, box_h = 420, 200
        box = pygame.Rect((SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2 - 20, box_w, box_h)
        self.renderer.draw_rect(screen, box, (25, 25, 30))
        self.renderer.draw_rect(screen, box, item.get_rarity_color(), fill=False)

        self.renderer.draw_text(screen, "Destroy Item?", (box.x + 20, box.y + 16),
                                color=COLOR_GOLD, size="large")
        qty_note = f" (x{item.quantity})" if getattr(item, "quantity", 1) > 1 else ""
        self.renderer.draw_text(screen, f"{item.name}{qty_note}", (box.x + 20, box.y + 60),
                                color=item.get_rarity_color())
        self.renderer.draw_text(screen, "This cannot be undone.", (box.x + 20, box.y + 90),
                                color=(200, 140, 140), size="small")

        # Quest items ARE destroyable, per Kyle, but silently letting one go
        # can stall a quest the player is carrying - so the warning is shown
        # rather than the action being blocked. Covers both a turn-in
        # objective (quest_id) and a drop that would have STARTED a quest
        # (starts_quest_id), which is the one that cannot be re-offered from
        # the bag once it is gone.
        if getattr(item, "starts_quest_id", None):
            self.renderer.draw_text(screen, "This item would start a quest.",
                                    (box.x + 20, box.y + 112), color=COLOR_GOLD, size="small")
        elif getattr(item, "quest_id", None) or getattr(item, "category", None) == "quest":
            self.renderer.draw_text(screen, "Quest item - you may need to find another.",
                                    (box.x + 20, box.y + 112), color=COLOR_GOLD, size="small")

        self.renderer.draw_button(screen, self.destroy_yes_button, "Destroy")
        self.renderer.draw_button(screen, self.destroy_no_button, "Cancel")

    def _get_hovered_item(self, mouse_pos, subject, bag=None):
        bag = bag or self._bag_source(subject)
        for slot_key, rect in self.slot_rects.items():
            if rect.collidepoint(mouse_pos):
                return subject.equipment.get_equipped(slot_key)
        for i, rect in enumerate(self.inventory_rects):
            if rect.collidepoint(mouse_pos) and i < len(bag.inventory):
                return bag.inventory[i]
        return None

    def _armor_reduction_note(self, item):
        """
        " (+1.8% phys reduction)" for an armor piece - how much this specific
        item is actually worth, computed as the DIFFERENCE the piece makes at
        the player's current armor rather than the piece's value in isolation.
        Armor has diminishing returns, so a flat "12 armor = X%" would be a
        lie that gets worse the more armor you already have.
        """
        if not item.armor_value:
            return ""
        # The "wearer" is the subject, not necessarily the player - otherwise
        # a companion's armor tooltip quotes the player's mitigation curve.
        player = self._get_subject()
        if not player:
            return ""
        from entities.character import Character

        current = player.armor
        equipped = player.equipment.get_equipped(item.slot)
        # Compare like for like: swapping, not stacking.
        base = current - (equipped.armor_value if equipped else 0)
        # Against something the character's own level - the same question the stat sheet's
        # reduction figure answers - on the player armour curve.
        gain = (Character.armor_mitigation_from(base + item.armor_value, player.level)
                - Character.armor_mitigation_from(base, player.level)) * 100.0
        return f"  ({gain:+.1f}% phys reduction)"

    def _draw_recipe_scroll_tooltip(self, screen, item, mouse_pos):
        """WoW-style recipe scroll tooltip. Kyle, 10 Nov: "patterns should show what they
        craft, what is needed to learn them... what level they are."

        Name, then the profession and skill it needs and where this character stands against
        that, then WHAT IT MAKES (slot, type, rarity, item level - the stats are rolled when it
        is crafted, so they cannot be promised here) and the materials one craft takes. No
        "Item Level" for the scroll itself: that number was a proxy derived from the skill.
        """
        subject = self._get_subject()
        recipe_id = item.recipe_id
        profession = item.recipe_profession or ""
        try:
            from world.recipe_manager import get_recipe_info
            _, recipe_data = get_recipe_info(recipe_id)
        except Exception:
            recipe_data = None
        recipe_data = recipe_data or {}
        skill_req = recipe_data.get("skill_required", 0)

        rarity_color = getattr(item, "get_rarity_color", lambda: COLOR_WHITE)()
        GREY, RED, GREEN, BLUE, GOLD = (170, 170, 170), (220, 70, 70), (120, 220, 140), (130, 180, 220), (200, 200, 140)
        box_w = 320
        body_w = box_w - 16
        lines = [(t, rarity_color) for t in self.renderer.wrap_text(item.name, body_w)]

        if profession:
            need = f"Requires {profession.title()} ({skill_req})" if skill_req else f"Requires {profession.title()}"
            met = True
            if subject is not None:
                met = (subject.knows_profession(profession)
                       and subject.profession_skills.get(profession, 0) >= skill_req)
            lines.append((need, GREY if met else RED))
            if subject is not None and not subject.knows_recipe(recipe_id):
                if not subject.knows_profession(profession):
                    lines.append((f"You have not learned {profession.title()}.", RED))
                elif not met:
                    lines.append((f"Your skill: {subject.profession_skills.get(profession, 0)}", (170, 120, 120)))

        out = recipe_data.get("output") or {}
        if recipe_data.get("name"):
            lines.append(("", GREY))
            count = recipe_data.get("count", 1)
            made = recipe_data["name"] + (f" x{count}" if count and count > 1 else "")
            for t in self.renderer.wrap_text(f"Teaches you to make: {made}", body_w):
                lines.append((t, BLUE))
            kind = out.get("kind")
            if kind in ("armor", "weapon"):
                what = [str(out.get("rarity", "")).title()]
                if kind == "armor" and out.get("armor_type") not in (None, "", "accessory"):
                    what.append(str(out["armor_type"]).title())
                if kind == "weapon" and out.get("weapon_type"):
                    what.append(str(out["weapon_type"]).replace("_", " ").title())
                what.append(str(out.get("slot", "")).replace("_", " ").title())
                lines.append((" ".join(w for w in what if w), GOLD))
                if out.get("item_level"):
                    lines.append((f"Item Level {out['item_level']}", GOLD))

        inputs = recipe_data.get("inputs") or {}
        if inputs:
            lines.append(("Materials:", GREY))
            for mat_id, n in inputs.items():
                lines.append((f"  {n} x {self._material_name(mat_id)}", GREY))

        if subject is not None:
            lines.append(("", GREY))
            if subject.knows_recipe(recipe_id):
                lines.append(("Already known.", GREY))
            elif profession and subject.knows_profession(profession) \
                    and subject.profession_skills.get(profession, 0) >= skill_req:
                lines.append(("Click to learn.", GREEN))

        box_h = 20 * len(lines) + 16
        x = min(mouse_pos[0] + 16, SCREEN_WIDTH - box_w - 10)
        y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - box_h - 10)
        box_rect = pygame.Rect(x, y, box_w, box_h)
        pygame.draw.rect(screen, (15, 15, 25), box_rect)
        pygame.draw.rect(screen, rarity_color, box_rect, 1)
        for i, (text, color) in enumerate(lines):
            self.renderer.draw_text(screen, text, (x + 8, y + 8 + i * 20), color=color)

    @staticmethod
    def _material_name(mat_id):
        """A material's display name, never its id - 'Bronze Bar', not 'bar_bronze'."""
        try:
            from world.gathering_manager import get_gathering_node_manager
            m = get_gathering_node_manager().make_material_instance(mat_id)
            if m is not None and getattr(m, "name", None):
                return m.name
        except Exception:
            pass
        return str(mat_id).replace("_", " ").title()

    def _draw_item_tooltip(self, screen, item, mouse_pos, show_sell_price=False):
        if not getattr(item, "is_gear", True):
            # Recipe scrolls get a richer tooltip showing profession, skill gate, and state.
            if getattr(item, "recipe_id", None):
                self._draw_recipe_scroll_tooltip(screen, item, mouse_pos)
                return
            # QuestItem (or any future non-equippable bag object) - a
            # much simpler tooltip, since none of the gear-specific
            # fields below (item_level, rarity, armor_type, weapon
            # damage, primary/secondary stats) exist on these objects.
            # Kyle, 2026-10-31: "words are running off." The box is a FIXED
            # 260px and the description was appended as one unbroken line, so
            # every loot item whose flavour text is a sentence rather than a
            # phrase - which is most vendor trash - drew straight out through
            # the right-hand border. Wrapped at the same size it is drawn in
            # (normal, the draw_text default below), against the box's real
            # inner width, so the box and the text can't disagree.
            box_w = 260
            body_w = box_w - 16
            name_lines = self.renderer.wrap_text(item.name, body_w)
            lines = list(name_lines)
            if getattr(item, "description", ""):
                lines.extend(self.renderer.wrap_text(item.description, body_w))
            if getattr(item, "quantity", 1) > 1:
                lines.append(f"Quantity: {item.quantity}")
            box_h = 20 * len(lines) + 16
            x = min(mouse_pos[0] + 16, SCREEN_WIDTH - box_w - 10)
            y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - box_h - 10)
            box_rect = pygame.Rect(x, y, box_w, box_h)
            pygame.draw.rect(screen, (20, 20, 25), box_rect)
            pygame.draw.rect(screen, (120, 110, 70), box_rect, 1)
            for i, line in enumerate(lines):
                # The NAME may now occupy more than one line, so the white
                # colour follows the name block rather than just line 0.
                color = COLOR_WHITE if i < len(name_lines) else (170, 170, 170)
                self.renderer.draw_text(screen, line, (x + 8, y + 8 + i * 20), color=color)
            return

        # Upgrade-kit state rides on this line as a badge rather than in the
        # item's name - Kyle, 2026-10-26: an upgraded Iron Sword is still
        # called "Iron Sword", with the Refined/Superior state shown on the
        # card. upgrade_tag() returns None for anything never upgraded, so
        # unupgraded and non-crafted gear reads exactly as it did before.
        from world.upgrade_manager import upgrade_tag
        tag = upgrade_tag(item)
        header = f"Item Level {item.item_level}  |  {item.rarity.capitalize()}"
        if tag:
            header += f"  |  {tag}"
        lines = [item.name, header]
        from ui.item_kind import item_kind
        kind = item_kind(item)                           # "Leather Chest", "Two-Hand Axe"
        if kind:
            lines.append(kind)
        # ARMOR IS SHOWN FOR ANYTHING THAT HAS IT, not only things with an
        # armor_type. Kyle, 2 Nov: "also shields need armor." They have it -
        # all 95 hand-authored shields carry an armor_value, the Dun Garok
        # Gate-Shield included - but a shield is weapon_type "shield" with NO
        # armor_type, so this line was gated behind a field shields do not
        # have and the number never reached the screen.
        #
        # The vendor and quest-reward tooltips both already test armor_value
        # directly and showed it correctly. This was the one place out of
        # three doing it the other way.
        # Bag capacity, same as the vendor tooltip. It is the only thing that
        # distinguishes one bag from another, and the grid badge ("+10") is
        # easy to miss and does not say what it counts.
        if getattr(item, "bag_capacity", 0):
            lines.append(f"{item.bag_capacity} Slot Bag")
        if item.armor_value:
            lines.append(f"Armor: {item.armor_value}{self._armor_reduction_note(item)}")
        if item.weapon_damage_max > 0:
            # A fitted attachment's bonus is already baked into these numbers
            # (attachment_manager.attach adds it at fit time), so it is named
            # on the damage line rather than listed as a separate modifier -
            # otherwise it would read as if it applied twice.
            from world.attachment_manager import attachment_label
            fitted = attachment_label(item)
            dmg = f"Damage: {item.weapon_damage_min} - {item.weapon_damage_max}"
            lines.append(f"{dmg}   ({fitted})" if fitted else dmg)
        if item.block_value > 0:
            lines.append(f"Block Value: {item.block_value}")
        for stat, value in item.primary_stats.items():
            lines.append(f"+{value} {stat.replace('_', ' ').title()}")
        for stat, value in item.secondary_stats.items():
            lines.append(f"+{value} {stat.replace('_', ' ').title()}")
        # WHAT THE ITEM DOES, in WoW's green "Equip:" line. A trinket that procs and does not
        # say so is indistinguishable from one that is broken - Kyle, 10 Nov: trinkets "do
        # stuff". Wrapped against the box's real inner width so a sentence cannot run off.
        green_lines = set()
        proc = getattr(item, "proc", None)
        if proc and proc.get("describe"):
            for wrapped in self.renderer.wrap_text(f"Equip: {proc['describe']}", 300 - 20):
                green_lines.add(len(lines))
                lines.append(wrapped)
        # THE SET IT BELONGS TO: every piece (the ones worn lit), then each bonus (the ones
        # earned lit). Counted against whoever the card is being read for.
        set_colors = {}
        if getattr(item, "set_id", None):
            from world.gear_sets import tooltip_lines
            palette = {"title": (255, 209, 0), "have": (255, 255, 160), "missing": (128, 128, 128),
                       "active": (30, 255, 0), "inactive": (128, 128, 128)}
            block = tooltip_lines(item, self._get_subject())
            if block:
                lines.append("")
            for text, kind in block:
                for wrapped in self.renderer.wrap_text(text, 300 - 20):
                    set_colors[len(lines)] = palette[kind]
                    lines.append(wrapped)
        if item.required_level > 1:
            lines.append(f"Requires Level {item.required_level}")

        # Equip eligibility. Without this an item a class can't wear looked
        # completely normal in the tooltip and clicking it simply did nothing,
        # which reads as a broken UI rather than a rule. Checked against the
        # subject so a Priest companion is told plate is off-limits.
        player = self._get_subject()
        warning_lines = []
        if player:
            from entities.proficiency import can_equip, is_suboptimal
            allowed, reason = can_equip(player, item)
            if not allowed:
                warning_lines.append(("blocked", reason))
            elif is_suboptimal(player, item):
                warning_lines.append(
                    ("warn", f"Below your armor class ({item.armor_type.capitalize()})"))
        lines.extend(text for _kind, text in warning_lines)

        # WHAT A VENDOR GIVES FOR IT, at the foot of the card, as coins. Kyle confirmed this
        # one on 10 Nov. Only on things in the bags: not on what you are wearing, and no line at
        # all for something that cannot be sold.
        sell_line = ""
        price = int(getattr(item, "sell_price", 0) or 0)
        if show_sell_price and price > 0 and getattr(item, "is_sellable", True):
            from ui.coin_format import format_coins
            sell_line = f"Sell Price: {format_coins(price)}"

        box_w = 300
        box_h = 20 * (len(lines) + (1 if sell_line else 0)) + 16
        x = min(mouse_pos[0] + 16, SCREEN_WIDTH - box_w - 10)
        y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - box_h - 10)
        rect = pygame.Rect(x, y, box_w, box_h)

        self.renderer.draw_rect(screen, rect, (15, 15, 20))
        self.renderer.draw_rect(screen, rect, item.get_rarity_color(), fill=False)

        ty = y + 8
        first_warning = len(lines) - len(warning_lines)
        for i, line in enumerate(lines):
            if i == 0:
                color = item.get_rarity_color()
            elif i in green_lines:
                color = (30, 255, 0)
            elif i in set_colors:
                color = set_colors[i]
            elif i >= first_warning:
                kind = warning_lines[i - first_warning][0]
                color = (220, 70, 70) if kind == "blocked" else (220, 180, 70)
            else:
                color = COLOR_WHITE
            self.renderer.draw_text(screen, line, (x + 10, ty), color=color)
            ty += 20
        if sell_line:
            self.renderer.draw_text(screen, sell_line, (x + 10, ty), color=COLOR_GOLD)
        self.last_tooltip_rect = rect
