"""
TalentScreen - display and interact with talent trees.
Shows hex grid, tier requirements, spendable points, and tooltips.
"""
import pygame
from enum import Enum
from math import sqrt, cos, sin, pi


class TalentTreeScreen:
    """Display a talent tree with hex grid rendering and point spending."""
    
    def __init__(self, screen_width, screen_height, character, state_manager=None):
        """
        Args:
            screen_width, screen_height: pygame surface dimensions
            character: Character object with talent_trees dict
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.character = character
        # Needed so ESC / the Back button can transition. Previously this was
        # never passed in, so the ESC handler always found None and did
        # nothing - there was literally no way out of this screen.
        self.state_manager = state_manager
        # Themed fonts, not pygame's default - this screen builds its own
        # rather than using Renderer, so it would otherwise have been the one
        # screen the font swap missed. Sizes use the theme's width-matched
        # mapping (old default 20/24/28 -> Lora 14/17/20).
        from ui import theme
        self.font_small = pygame.font.Font(theme.FONT_REGULAR, 14)
        self.font_medium = pygame.font.Font(theme.FONT_REGULAR, 17)
        self.font_large = pygame.font.Font(theme.FONT_BOLD, 20)
        
        # UI state
        self.current_tree_id = None  # Which tree we're viewing (e.g., "warrior_arms")
        self.selected_node = None  # Last clicked node
        self.hovered_node = None   # Node under the mouse right now
        self.scroll_offset_y = 0  # For scrolling the tree if needed
        
        # Hex grid rendering.
        # These are RECOMPUTED per-tree by _fit_layout() so the whole tree
        # always fits on screen. The old fixed values (radius 30, spacing 45,
        # center_y 150) placed tier 0 at y = 150 - 234 = -84, i.e. entirely
        # above the top of the window - that is why the tree looked cut off.
        self.hex_radius = 30
        self.hex_spacing = self.hex_radius * 1.5
        self.hex_spacing_x = self.hex_spacing
        self.hex_spacing_y = self.hex_spacing
        self.center_x = screen_width // 2
        self.center_y = 150

        # Layout margins for the fitted tree
        self.top_margin = 150     # room for title, points, tier reqs, tabs
        self.bottom_margin = 45   # room for the footer hint line

        # Spec tabs (one per tree the character owns) and Back button.
        self.tab_rects = []       # [(tree_id, rect), ...] rebuilt each render
        # Where ESC/Back returns to. The party screen overrides this when it
        # opens the screen for a companion.
        self.return_state = None
        # Transient "this tree is locked" notice.
        self.lock_message = None
        self.lock_message_timer = 0.0
        self.back_button = pygame.Rect(screen_width - 110, 12, 95, 30)
        # FREE FOR NOW, deliberately. Kyle: "We can start this as free so it's
        # easy to test combinations." When it stops being free this is where
        # the cost goes - the reset itself is already one call, so pricing it
        # later is a guard in _reset_all_talents and nothing else.
        self.reset_button = pygame.Rect(screen_width - 250, 12, 130, 30)
        
        # Colors
        self.color_bg = (20, 20, 30)
        self.color_hex_available = (70, 120, 180)  # Blue - can spend points
        self.color_hex_maxed = (100, 100, 100)  # Gray - already maxed
        self.color_hex_locked = (40, 40, 60)  # Dark - locked by tier
        self.color_hex_border = (150, 150, 150)
        self.color_connection = (100, 150, 200)
        self.color_text = (255, 255, 255)
        self.color_text_cost = (200, 200, 100)
    
    def set_current_tree(self, tree_id):
        """Switch to a different talent tree."""
        if self.character and tree_id in self.character.talent_trees:
            self.current_tree_id = tree_id
            self.selected_node = None
            self.hovered_node = None
            self._fit_layout()
    
    def is_tree_locked(self, tree_id):
        """
        True if this character may NOT spend points in `tree_id`.

        Companions are spec-locked: class and spec are fixed at recruitment
        and are their identity. Character.locked_spec held the tree_id all
        along, but nothing ever consulted it, so a Holy Priest companion
        could happily be respecced into Shadow. The player has no
        locked_spec and keeps all three trees.

        Asher Coleman is locked out of EVERY tree, including his own
        nominal locked_spec ("paladin_retribution") - unlike a normal
        recruit, his kit isn't "one tree's worth of normal Paladin
        talents", it's exactly two fixed, hand-authored abilities that
        never rank up and were never meant to interact with the talent
        system at all (see world/recruit_manager.py's _build_asher_kit).
        Kyle's spec was explicit: "You won't be able to change his
        equipment or his skills" - a spendable Retribution tree would
        still let a player boost his stats/passives even though his two
        abilities themselves can't change, which isn't what "can't
        change his skills" means here.
        """
        if not self.character:
            return False
        if getattr(self.character, "recruit_id", None) == "asher_coleman":
            return True
        locked = getattr(self.character, "locked_spec", None)
        if not locked:
            return False
        # A locked_spec naming a tree the character doesn't own would lock
        # them out of everything, so treat that as no lock at all.
        if locked not in getattr(self.character, "talent_trees", {}):
            return False
        return tree_id != locked

    def get_current_tree(self):
        """Get the currently displayed talent tree."""
        if not self.current_tree_id:
            return None
        return self.character.talent_trees.get(self.current_tree_id)
    
    def _fit_layout(self):
        """Scale and centre the hex grid so the entire tree fits on screen.

        Trees are 7 tiers deep and 4 columns wide. Rather than hardcoding a
        radius/spacing that only happens to fit one tree shape, this measures
        the actual hex coordinate extents of the current tree and derives the
        spacing that fills the available area, then centres it.

        This is what fixes the "talent tree is cut off" problem, and it keeps
        working if trees ever grow deeper or wider.
        """
        tree = self.get_current_tree()
        if not tree or not tree.nodes:
            return

        xs = [n.hex_x for n in tree.nodes.values()]
        ys = [n.hex_y for n in tree.nodes.values()]
        span_x = (max(xs) - min(xs)) or 1
        span_y = (max(ys) - min(ys)) or 1

        avail_w = self.screen_width - 340   # leave room for the tooltip panel
        avail_h = self.screen_height - self.top_margin - self.bottom_margin

        # Horizontal and vertical spacing are fitted INDEPENDENTLY. Using a
        # single uniform spacing meant the tighter axis (vertical, since trees
        # are 7 tiers deep but only 4 columns wide) clamped both, leaving the
        # tree squeezed into a narrow column with most of the screen width
        # unused. Separate spacings let it fill the available area properly.
        self.hex_spacing_x = max(40, avail_w / (span_x + 1.6))
        self.hex_spacing_y = max(30, avail_h / ((span_y + 1.6) * 0.866))

        # Node radius is bounded by BOTH spacings so hexes never overlap on
        # either axis, with a floor that keeps the rank text legible.
        self.hex_radius = max(18, int(min(self.hex_spacing_x * 0.46,
                                          self.hex_spacing_y * 0.80)))

        # Kept in sync for any older code path still reading hex_spacing.
        self.hex_spacing = self.hex_spacing_x

        # Centre the actual coordinate range rather than assuming it is
        # symmetric around zero.
        mid_x = (max(xs) + min(xs)) / 2
        mid_y = (max(ys) + min(ys)) / 2
        self.center_x = (self.screen_width - 320) // 2 - int(mid_x * self.hex_spacing_x)
        self.center_y = (self.top_margin + (self.screen_height - self.bottom_margin)) // 2 \
            - int(mid_y * self.hex_spacing_y * 0.866)

    def _hex_to_screen(self, hex_x, hex_y):
        """Convert hex grid coordinates to screen pixels."""
        # Offset-coordinate system for hex grids
        x = self.center_x + hex_x * getattr(self, "hex_spacing_x", self.hex_spacing)
        y = self.center_y + hex_y * getattr(self, "hex_spacing_y", self.hex_spacing) * 0.866
        return int(x), int(y)
    
    def _screen_to_hex(self, screen_x, screen_y):
        """Convert screen pixels to nearest hex grid coordinates (approximate).

        Kept for backward compatibility only. Click hit-testing now uses
        _node_at_pixel() instead - see that method for why.
        """
        x = (screen_x - self.center_x) / self.hex_spacing
        y = (screen_y - self.center_y) / (self.hex_spacing * 0.866)
        return round(x), round(y)

    def _node_at_pixel(self, tree, mouse_x, mouse_y):
        """Return the talent node whose rendered hex contains this pixel, or None.

        Replaces the old approach of rounding the mouse position to integer
        hex coordinates and requiring an exact == match against node.hex_x /
        node.hex_y. That forced every talent onto a tight integer lattice
        (any fractional or widely-spaced coordinate became unclickable),
        which is the real reason the trees had to be authored so cramped.

        Measuring actual pixel distance to each node's rendered centre lifts
        that restriction entirely - hex_x/hex_y can now be any value, so
        trees can be laid out with as much breathing room as the screen
        allows.
        """
        best = None
        best_dist_sq = self.hex_radius * self.hex_radius
        for node in tree.nodes.values():
            nx, ny = self._hex_to_screen(node.hex_x, node.hex_y)
            dist_sq = (mouse_x - nx) ** 2 + (mouse_y - ny) ** 2
            if dist_sq <= best_dist_sq:
                best_dist_sq = dist_sq
                best = node
        return best
    
    def _draw_hex(self, surface, center_x, center_y, radius, color, border_color, border_width=2):
        """Draw a single hexagon."""
        points = []
        for i in range(6):
            angle = pi / 3 * i  # 60 degrees
            px = center_x + radius * cos(angle)
            py = center_y + radius * sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, border_color, points, border_width)
    
    def _get_node_color(self, node, tree, available_points):
        """Determine hex color based on node state."""
        total_spent = tree.total_points_spent()
        can_spend_in_tier = tree.can_spend_in_tier(node.tier, total_spent)
        
        if node.points_spent >= node.max_points:
            # Maxed out
            return self.color_hex_maxed
        elif not can_spend_in_tier:
            # Locked by tier requirement
            return self.color_hex_locked
        elif available_points > 0:
            # Can spend points
            return self.color_hex_available
        else:
            # No points available but not maxed
            return self.color_hex_locked
    
    def handle_click(self, mouse_x, mouse_y):
        """Handle mouse click on hex grid, spec tabs, or the Back button."""
        # Back button first - it sits above everything else.
        if self.back_button.collidepoint(mouse_x, mouse_y):
            self._close()
            return

        if self.reset_button.collidepoint(mouse_x, mouse_y):
            self._reset_all_talents()
            return

        # Spec tabs: switching trees is how a Shaman gets from Elemental to
        # Enhancement/Restoration. Previously the screen opened on whichever
        # tree happened to be first in the dict and there was no way to
        # change it, so every class was locked to one spec's tree.
        for tree_id, rect in self.tab_rects:
            if rect.collidepoint(mouse_x, mouse_y):
                self.set_current_tree(tree_id)
                return

        tree = self.get_current_tree()
        if not tree:
            return
        
        # Find which hex was clicked (pixel-accurate, see _node_at_pixel)
        clicked_node = self._node_at_pixel(tree, mouse_x, mouse_y)
        
        if not clicked_node:
            self.selected_node = None
            return
        
        self.selected_node = clicked_node
        
        # Try to spend a point
        total_spent = tree.total_points_spent()
        can_spend_in_tier = tree.can_spend_in_tier(clicked_node.tier, total_spent)
        available_points = self.character.talent_points_available
        
        if self.is_tree_locked(self.current_tree_id):
            self.lock_message = (
                f"{self.character.name} is locked to "
                f"{self._locked_spec_label()} and cannot spend here.")
            self.lock_message_timer = 3.0
            return

        # Character.spend_talent_point owns the rule now - the rank, the point, the stat
        # recalculation and the two talent syncs have to happen together, and when that was
        # written out here it was only true for a human clicking. It re-checks the tier gate and
        # the max rank itself, so the checks above remain only to decide what to print.
        if self.character.spend_talent_point(self.current_tree_id, clicked_node.talent_id):
            print(f"✅ Spent point in {clicked_node.name}. Points available: {available_points - 1}")
        else:
            print(f"❌ Cannot spend point: tier_locked={not can_spend_in_tier}, maxed={not clicked_node.can_spend_point()}, points={available_points}")
    
    def handle_right_click(self, mouse_x, mouse_y):
        """Handle right-click to refund a point."""
        tree = self.get_current_tree()
        if not tree:
            return
        
        if self.is_tree_locked(self.current_tree_id):
            # Refunds are blocked too. Allowing them would let you drain a
            # companion's locked tree into a pool spendable nowhere, which is
            # strictly worse than not touching it.
            return

        clicked_node = self._node_at_pixel(tree, mouse_x, mouse_y)

        if clicked_node and clicked_node.points_spent > 0:
            clicked_node.refund_point()
            self.character.talent_points_available += 1
            self.character._recalculate_derived_stats()  # FIX: talent effects not applying without this
            # Refunding may take away a talent-granted ability the player
            # currently has queued on their hotbar - resync immediately,
            # same reasoning as the spend path above.
            self.character._sync_talent_unlocked_abilities()
            self.character._sync_talent_procs()
            print(f"✅ Refunded point from {clicked_node.name}. Points available: {self.character.talent_points_available}")
    
    def _reset_all_talents(self):
        """Refund every point this character has spent, across every tree.

        THIS GOES THROUGH THE SAME refund_point() AND RESYNC THE RIGHT-CLICK
        PATH USES, one node at a time, rather than zeroing points_spent and
        recomputing a total. A talent can grant an ability, place something on
        the hotbar, or register a proc, and a reset that only moved numbers
        would leave all of that behind - the character would keep abilities
        from talents they no longer have. _grant_talent_points is what decides
        the final pool, so the count cannot drift either.

        Locked trees are included ON PURPOSE, unlike a right-click refund. A
        companion's points were spent in their locked tree, so a reset that
        skipped locked trees could not reset a companion at all - which is
        most of what this button is for, now that a caught-up rehire arrives
        with forty of them.
        """
        refunded = 0
        for tree in self.character.talent_trees.values():
            for node in tree.nodes.values():
                while node.points_spent > 0:
                    node.refund_point()
                    refunded += 1
        self.character._grant_talent_points()      # single source of truth for the pool
        self.character._recalculate_derived_stats()
        self.character._sync_talent_unlocked_abilities()
        self.character._sync_talent_procs()
        self.lock_message = (f"Refunded {refunded} talent point{'s' if refunded != 1 else ''}."
                             if refunded else "No talent points spent.")
        self.lock_message_timer = 3.0      # seconds, matching the spend path above
        return refunded

    def handle_event(self, event):
        """Handle user input."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos[0], event.pos[1])
            elif event.button == 3:  # Right click
                self.handle_right_click(event.pos[0], event.pos[1])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._close()

    def _close(self):
        """
        Return wherever we were opened from - the character sheet for the
        player, the party screen when inspecting a companion. Hardcoding the
        character sheet dumped you onto the PLAYER's sheet after editing a
        companion's talents, which is disorienting.
        """
        from core.game_states import GameState
        destination = getattr(self, "return_state", None) or GameState.CHARACTER_SHEET
        self.return_state = GameState.CHARACTER_SHEET
        if self.state_manager:
            self.state_manager.transition_to(destination)

    def _locked_spec_label(self):
        """Display name of the character's locked spec ('Holy')."""
        locked = getattr(self.character, "locked_spec", None)
        tree = self.character.talent_trees.get(locked) if locked else None
        if tree is not None:
            parts = tree.spec_name.split(" ", 1)
            return parts[1] if len(parts) > 1 else tree.spec_name
        return str(locked)
    
    def update(self, dt):
        """Track which talent the mouse is over so render() can tooltip it."""
        if self.lock_message_timer > 0:
            self.lock_message_timer -= dt
            if self.lock_message_timer <= 0:
                self.lock_message = None

        tree = self.get_current_tree()
        if not tree:
            self.hovered_node = None
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered_node = self._node_at_pixel(tree, mouse_x, mouse_y)
    
    def render(self, surface):
        """Draw the talent tree screen."""
        tree = self.get_current_tree()
        if not tree:
            text = self.font_large.render("No talent tree loaded", True, self.color_text)
            surface.blit(text, (50, 50))
            return
        
        # Draw background
        surface.fill(self.color_bg)

        # Recompute layout if it has not been fitted for this tree yet
        # (e.g. the tree was set directly rather than via set_current_tree).
        if not getattr(self, "_fitted_for", None) == self.current_tree_id:
            self._fit_layout()
            self._fitted_for = self.current_tree_id

        # Draw title
        # Name the character in the title. When this screen can be opened for
        # any party member, "Priest Holy Talent Tree" alone doesn't tell you
        # whose points you're about to spend.
        title_text = f"{tree.spec_name} Talent Tree"
        if getattr(self.character, "locked_spec", None):
            title_text = f"{self.character.name} - {title_text}"
        title = self.font_large.render(title_text, True, self.color_text)
        surface.blit(title, (20, 10))

        # Back button
        pygame.draw.rect(surface, (60, 40, 40), self.reset_button)
        pygame.draw.rect(surface, (190, 130, 120), self.reset_button, 2)
        reset_text = self.font_medium.render("Reset Talents", True, (250, 220, 210))
        surface.blit(reset_text, reset_text.get_rect(center=self.reset_button.center))

        pygame.draw.rect(surface, (70, 60, 40), self.back_button)
        pygame.draw.rect(surface, (200, 180, 120), self.back_button, 2)
        back_text = self.font_medium.render("Back", True, (255, 240, 200))
        surface.blit(back_text, back_text.get_rect(center=self.back_button.center))
        
        # Draw available points counter
        points_text = self.font_medium.render(
            f"Points Available: {self.character.talent_points_available} / {self.character.level - 4}",
            True, self.color_text_cost
        )
        surface.blit(points_text, (20, 40))
        
        # Draw tier requirements
        tier_text = "Tier Requirements: " + " | ".join(
            f"T{t}:{r}" for t, r in sorted(tree.tier_requirements.items())
        )
        tier_surface = self.font_small.render(tier_text, True, (180, 180, 180))
        surface.blit(tier_surface, (20, 65))

        # Locked-tree notice, and the transient "can't spend here" message.
        if self.is_tree_locked(self.current_tree_id):
            note = self.font_small.render(
                f"Locked to {self._locked_spec_label()} - viewing only.",
                True, (220, 160, 160))
            surface.blit(note, (320, 42))
        if self.lock_message:
            msg = self.font_medium.render(self.lock_message, True, (230, 120, 120))
            surface.blit(msg, (20, self.screen_height - 40))

        # Spec tabs - one per tree this character owns, showing points spent
        # in each so the player can see their build split at a glance.
        self.tab_rects = []
        tab_x = 20
        tab_y = 92
        tab_h = 32
        for tree_id, t in self.character.talent_trees.items():
            label = f"{t.spec_name.split(' ', 1)[-1]} ({t.total_points_spent()})"
            label_surface = self.font_medium.render(label, True, self.color_text)
            tab_w = label_surface.get_width() + 24
            rect = pygame.Rect(tab_x, tab_y, tab_w, tab_h)

            active = (tree_id == self.current_tree_id)
            locked = self.is_tree_locked(tree_id)
            # Locked trees stay VIEWABLE (you should be able to read what a
            # companion gave up) but are visibly greyed so it's obvious why
            # clicking a talent does nothing.
            if locked:
                label = f"{t.spec_name.split(' ', 1)[-1]} (locked)"
                label_surface = self.font_medium.render(label, True, (130, 130, 140))
                rect.width = label_surface.get_width() + 24
                fill = (55, 45, 45) if active else (32, 30, 34)
                border = (120, 100, 100) if active else (70, 65, 70)
            else:
                fill = (60, 90, 130) if active else (40, 40, 55)
                border = (160, 200, 240) if active else (90, 90, 110)
            pygame.draw.rect(surface, fill, rect)
            pygame.draw.rect(surface, border, rect, 2)
            surface.blit(label_surface, label_surface.get_rect(center=rect.center))

            self.tab_rects.append((tree_id, rect))
            # Advance by the rect's ACTUAL width - the locked label is longer
            # than the one tab_w was measured from, so using tab_w here would
            # overlap the next tab.
            tab_x += rect.width + 8
        
        # Draw connections first (so they appear behind hexes)
        for node in tree.nodes.values():
            screen_x, screen_y = self._hex_to_screen(node.hex_x, node.hex_y)
            for connected_id in node.connected_to:
                connected = tree.get_node(connected_id)
                if connected:
                    conn_x, conn_y = self._hex_to_screen(connected.hex_x, connected.hex_y)
                    pygame.draw.line(surface, self.color_connection, (screen_x, screen_y), (conn_x, conn_y), 2)
        
        # Draw hexes and talents
        icon_helper = getattr(self.state_manager, "icon_ui_helper", None) if self.state_manager else None
        for node in tree.nodes.values():
            screen_x, screen_y = self._hex_to_screen(node.hex_x, node.hex_y)
            
            # Get color based on state
            hex_color = self._get_node_color(node, tree, self.character.talent_points_available)
            
            # Draw hex
            self._draw_hex(surface, screen_x, screen_y, self.hex_radius, hex_color, self.color_hex_border)

            # Real talent icon, sized to fit inside the hex, replacing the
            # old truncated name label ("Improved Wr." for "Improved
            # Wrath" - Kyle's "text constantly runs off the screen"
            # complaint applies exactly here). Falls back to the name
            # label only when no icon system or no real art is available,
            # so this degrades gracefully rather than going blank.
            icon_drawn = False
            if icon_helper is not None:
                icon_size = max(16, int(self.hex_radius * 1.3))
                icon_surface = icon_helper.get_ability_icon_surface(
                    {"ability_id": node.talent_id, "effect_type": "buff"},
                    size=icon_size,
                )
                if icon_surface:
                    icon_rect = icon_surface.get_rect(center=(screen_x, screen_y - 3))
                    surface.blit(icon_surface, icon_rect)
                    icon_drawn = True

            if not icon_drawn:
                # Draw talent name (truncated for space)
                name_short = node.name[:12]
                if len(node.name) > 12:
                    name_short += "."
                name_text = self.font_small.render(name_short, True, self.color_text)
                name_rect = name_text.get_rect(center=(screen_x, screen_y - 5))
                surface.blit(name_text, name_rect)
            
            # Draw rank counter
            rank_text = self.font_small.render(f"{node.points_spent}/{node.max_points}", True, self.color_text_cost)
            rank_rect = rank_text.get_rect(center=(screen_x, screen_y + 8))
            surface.blit(rank_text, rank_rect)
        
        # Draw tooltip for selected node
        # Prefer the node under the cursor, falling back to the last clicked
        # one. Previously the tooltip only appeared after clicking, which
        # meant you had to spend a point to find out what a talent did.
        tooltip_node = self.hovered_node or self.selected_node
        if tooltip_node:
            self._draw_tooltip(surface, tooltip_node, tree)
        
        # Draw footer
        footer = ("Left-Click: Spend Point | Right-Click: Refund | "
                  "Click a spec tab to switch trees | ESC or Back: Close")
        footer_text = self.font_small.render(footer, True, (150, 150, 150))
        surface.blit(footer_text, (20, self.screen_height - 30))
    
    def _draw_tooltip(self, surface, node, tree):
        """Draw a tooltip for the selected node."""
        tooltip_lines = [
            f"{node.name}",
            f"Tier {node.tier} | Ranks: {node.points_spent}/{node.max_points}",
            f"Cost: {node.cost_per_point} point per rank",
            "",
            node.description,
        ]
        
        # Add tier requirement info
        required = tree.tier_requirements.get(node.tier, 0)
        current = tree.total_points_spent()
        if current < required:
            tooltip_lines.append(f"[LOCKED] Requires {required} points in tree ({current}/{required})")
        
        # Add effects
        if node.effects:
            tooltip_lines.append("")
            for key, value in node.effects.items():
                if isinstance(value, (int, float)) and value != 0:
                    tooltip_lines.append(f"  {key}: +{value}")
        
        # Render tooltip box
        tooltip_texts = [self.font_small.render(line, True, self.color_text) for line in tooltip_lines]
        max_width = max(t.get_width() for t in tooltip_texts) + 20
        total_height = sum(t.get_height() for t in tooltip_texts) + 20
        
        tooltip_x = min(self.screen_width - max_width - 10, 400)
        tooltip_y = 100
        
        # Draw background box
        pygame.draw.rect(surface, (40, 40, 60), (tooltip_x, tooltip_y, max_width, total_height))
        pygame.draw.rect(surface, self.color_hex_border, (tooltip_x, tooltip_y, max_width, total_height), 2)
        
        # Draw text
        y = tooltip_y + 10
        for text_surface in tooltip_texts:
            surface.blit(text_surface, (tooltip_x + 10, y))
            y += text_surface.get_height()
