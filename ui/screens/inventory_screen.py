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

        # Gear/Materials tab toggle (Gathering Phase 1). Materials get
        # their own tab rather than sharing the gear backpack grid -
        # they're a different List (Character.materials, not .inventory),
        # non-equippable, and the gear grid is already dense (17 gear
        # slots + 4 bag slots + backpack + stats summary). "gear" is the
        # default so nothing about the existing flow changes for anyone
        # who never touches gathering.
        self.active_tab = "gear"
        self.gear_tab_button = pygame.Rect(SCREEN_WIDTH - 420, 20, 100, 36)
        self.materials_tab_button = pygame.Rect(SCREEN_WIDTH - 310, 20, 130, 36)
        self.materials_rects = []  # list of pygame.Rect, index-aligned to subject.materials

        self._build_slot_rects()

    def set_subject(self, character, return_state=None):
        """Point the screen at a character (party screen uses this)."""
        self.subject = character
        self.equip_error = None
        self.selected_item = None
        self.pending_destroy_item = None
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

    def _build_inventory_rects(self, count):
        self.inventory_rects = []
        for i in range(count):
            col = i % INV_GRID_COLS
            row = i // INV_GRID_COLS
            x = INV_START_X + col * (INV_SLOT_SIZE + INV_SLOT_SPACING)
            y = INV_START_Y + row * (INV_SLOT_SIZE + INV_SLOT_SPACING)
            self.inventory_rects.append(pygame.Rect(x, y, INV_SLOT_SIZE, INV_SLOT_SIZE))

    def _build_materials_rects(self, count):
        """Grid layout for the Materials tab. Uses a wider column count
        and starts near the top-left, unlike the gear tab's backpack grid
        (INV_START_X=600) which has to squeeze in next to the gear panel
        - the materials tab has the WHOLE screen to itself, no gear grid
        sharing the view, so it gets more breathing room."""
        self.materials_rects = []
        for i in range(count):
            col = i % MATERIALS_GRID_COLS
            row = i // MATERIALS_GRID_COLS
            x = MATERIALS_START_X + col * (MATERIALS_SLOT_SIZE + MATERIALS_SLOT_SPACING)
            y = MATERIALS_START_Y + row * (MATERIALS_SLOT_SIZE + MATERIALS_SLOT_SPACING)
            self.materials_rects.append(pygame.Rect(x, y, MATERIALS_SLOT_SIZE, MATERIALS_SLOT_SIZE))

    def handle_event(self, event):
        subject = self._get_subject()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.pending_destroy_item is not None:
                self.pending_destroy_item = None
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
                    if item in subject.inventory:
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

            # Tab toggle - checked before any gear/bag click handling
            # below, and returns immediately either way so a tab click
            # never also falls through and hits a gear slot underneath it.
            if self.gear_tab_button.collidepoint(mouse_pos):
                self.active_tab = "gear"
                self.selected_item = None
                return
            if self.materials_tab_button.collidepoint(mouse_pos):
                self.active_tab = "materials"
                self.selected_item = None
                return

            # Materials tab has no click actions yet (Phase 1 has no
            # crafting to consume them into, no sell-from-bag flow wired
            # for materials specifically) - clicking a material currently
            # does nothing but is still visible/hoverable for its
            # tooltip, same "look but no action yet" state consumables
            # were already in before this session.
            if self.active_tab == "materials":
                return

            # Click an equipped slot -> unequip, back into the SUBJECT's
            # own bag (unequipped gear stays theirs, even if it was
            # originally handed to them from the player's bag).
            for slot_key, rect in self.slot_rects.items():
                if rect.collidepoint(mouse_pos):
                    item = subject.equipment.get_equipped(slot_key)
                    if item:
                        subject.unequip_item(slot_key)
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
                    if not getattr(item, "is_gear", True):
                        self.pending_destroy_item = item
                        return
                    self._equip_on_subject(subject, item)
                    self.selected_item = None
                    return

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

        # Title names the subject when gearing a companion, so there is no
        # chance of dressing the wrong character without noticing.
        player = self.state_manager.player
        if subject is player:
            title = "INVENTORY & EQUIPMENT" if self.active_tab == "gear" else "MATERIALS"
        else:
            title = (f"{subject.name.upper()}'S INVENTORY & EQUIPMENT - Lv {subject.level} {subject.char_class}"
                     if self.active_tab == "gear" else f"{subject.name.upper()}'S MATERIALS")
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
                self.renderer.draw_text(screen, item.name, (text_x, rect.y + 20), color=color)
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
                    self.renderer.draw_text(screen, item.name[:10],
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
        self.renderer.draw_text(screen, f"{bag_label} ({used}/{capacity})",
                                (INV_START_X, 30), color=cap_color)

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
                corner_text = (f"x{item.quantity}" if not getattr(item, "is_gear", True)
                               else f"ilvl {item.item_level}")
                if not icon_drawn:
                    # Text fallback for anything without real icon art yet
                    # (procedural gear gear_icons.py couldn't match, or an
                    # older save item generated before this system).
                    display_name = item.name
                    if len(display_name) > 14:
                        display_name = display_name[:12] + ".."
                    self.renderer.draw_text(screen, display_name, (rect.x + 4, rect.y + 4), color=color)
                    self.renderer.draw_text(screen, corner_text, (rect.x + 4, rect.y + rect.height - 20), color=(180, 180, 180))
                else:
                    # Icon art shown - ilvl (or quantity) still worth a
                    # small corner readout so browsing doesn't require
                    # hovering every single item.
                    corner_short = (f"x{item.quantity}" if not getattr(item, "is_gear", True)
                                    else str(item.item_level))
                    self.renderer.draw_text(screen, corner_short,
                                            (rect.x + 3, rect.bottom - 16),
                                            size="small", color=(220, 220, 220))

        # ---- Stat comparison / detail panel (hover-based, simple version) ----
        mouse_pos = pygame.mouse.get_pos()
        hovered_item = self._get_hovered_item(mouse_pos, subject, bag)
        if hovered_item:
            self._draw_item_tooltip(screen, hovered_item, mouse_pos)

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

        if self.pending_destroy_item is not None:
            self._render_destroy_confirmation(screen)

    def _render_materials_tab(self, screen, subject):
        """Materials grid + profession skill readout. Kept as its own
        method (rather than inlined in render()) since it's a fully
        separate view, same reasoning _render_destroy_confirmation is
        broken out below - render() dispatches to one or the other, it
        doesn't interleave them."""
        self._build_materials_rects(len(subject.materials))

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
                display_name = material.name
                if len(display_name) > 10:
                    display_name = display_name[:8] + ".."
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
        lines = [
            material.name,
            f"{material.profession.title()} - {material.tier.title()} tier",
        ]
        if material.description:
            lines.append(material.description)
        lines.append(f"Sell price: {material.sell_price}c")

        padding = 8
        line_height = 20
        width = max(220, max(len(line) for line in lines) * 7)
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
        gain = (Character.mitigation_from(base + item.armor_value)
                - Character.mitigation_from(base)) * 100.0
        return f"  ({gain:+.1f}% phys reduction)"

    def _draw_item_tooltip(self, screen, item, mouse_pos):
        if not getattr(item, "is_gear", True):
            # QuestItem (or any future non-equippable bag object) - a
            # much simpler tooltip, since none of the gear-specific
            # fields below (item_level, rarity, armor_type, weapon
            # damage, primary/secondary stats) exist on these objects.
            lines = [item.name]
            if getattr(item, "description", ""):
                lines.append(item.description)
            if getattr(item, "quantity", 1) > 1:
                lines.append(f"Quantity: {item.quantity}")
            box_w = 260
            box_h = 20 * len(lines) + 16
            x = min(mouse_pos[0] + 16, SCREEN_WIDTH - box_w - 10)
            y = min(mouse_pos[1] + 16, SCREEN_HEIGHT - box_h - 10)
            box_rect = pygame.Rect(x, y, box_w, box_h)
            pygame.draw.rect(screen, (20, 20, 25), box_rect)
            pygame.draw.rect(screen, (120, 110, 70), box_rect, 1)
            for i, line in enumerate(lines):
                color = COLOR_WHITE if i == 0 else (170, 170, 170)
                self.renderer.draw_text(screen, line, (x + 8, y + 8 + i * 20), color=color)
            return

        lines = [item.name, f"Item Level {item.item_level}  |  {item.rarity.capitalize()}"]
        if item.armor_type and item.armor_type not in ("accessory", "weapon"):
            lines.append(item.armor_type.capitalize())
            lines.append(f"Armor: {item.armor_value}{self._armor_reduction_note(item)}")
        if item.weapon_damage_max > 0:
            lines.append(f"Damage: {item.weapon_damage_min} - {item.weapon_damage_max}")
        if item.block_value > 0:
            lines.append(f"Block Value: {item.block_value}")
        for stat, value in item.primary_stats.items():
            lines.append(f"+{value} {stat.replace('_', ' ').title()}")
        for stat, value in item.secondary_stats.items():
            lines.append(f"+{value} {stat.replace('_', ' ').title()}")
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

        box_w = 300
        box_h = 20 * len(lines) + 16
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
            elif i >= first_warning:
                kind = warning_lines[i - first_warning][0]
                color = (220, 70, 70) if kind == "blocked" else (220, 180, 70)
            else:
                color = COLOR_WHITE
            self.renderer.draw_text(screen, line, (x + 10, ty), color=color)
            ty += 20
