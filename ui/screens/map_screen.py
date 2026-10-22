"""
Map screen - full-zone overview, opened with M.

Renders the current map scaled to fit the window, with the player position,
portals, subzone regions and points of interest marked. Zones are up to
200x160 tiles, far larger than the ~40x22 tile viewport the overworld
renders, so without this there was no way to see the shape of a zone or
where its exits were.
"""
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from core.game_states import GameState
from ui.screens.base_screen import BaseScreen
from ui.renderer import Renderer
from boss_icons import get_boss_icon_path


class MapScreen(BaseScreen):
    """Scaled overview of the current zone."""

    # Base terrain colours. Deliberately muted so the markers drawn on top
    # (player, portals, POIs) read clearly against them.
    TERRAIN_COLORS = {
        "grass": (58, 92, 50),
        "grass_tuft": (58, 92, 50),
        "flowers": (68, 100, 56),
        "dirt": (104, 82, 56),
        "sand": (150, 118, 74),
        "stone": (104, 104, 112),
        "small_rocks": (104, 104, 112),
        "shallow_water": (60, 106, 150),
        "deep_water": (34, 66, 116),
        "ice": (168, 200, 216),
        "lava": (168, 62, 30),
        "wood": (96, 70, 44),
    }
    COLLISION_COLORS = {
        "tree": (32, 62, 34),
        "deep_forest": (24, 48, 26),
        "bushes": (44, 74, 40),
        "rock": (86, 76, 68),
        "cliff": (70, 62, 56),
        "wall": (60, 56, 60),
        "ore": (120, 100, 60),
    }
    UNKNOWN = (44, 44, 52)

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.renderer = Renderer()
        self.close_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)

        # Cached render of the terrain. Rebuilding a 200x160 map every frame
        # is wasteful when it only changes on zone transition, so the surface
        # is cached and keyed by zone name.
        self._cached_surface = None
        self._cached_zone = None

        # Boss portrait icons (see boss_icons.py), keyed by the resolved
        # filename - loaded from disk once and reused, same reasoning as
        # the terrain cache above. A plain dict rather than clearing per
        # zone: there are only 12 distinct files total (one per creature
        # template), so nothing is gained by ever evicting entries.
        self._boss_icon_cache = {}

    # ------------------------------------------------------------------

    def _zone_manager(self):
        return getattr(self.state_manager, "zone_manager", None)

    def _build_terrain_surface(self, tilemap):
        """Render the whole map to a 1px-per-tile surface, once."""
        surf = pygame.Surface((tilemap.width, tilemap.height))
        for y in range(tilemap.height):
            row_base = tilemap.base_layer[y]
            row_coll = tilemap.collision_layer[y]
            for x in range(tilemap.width):
                coll = row_coll[x]
                if coll:
                    color = self.COLLISION_COLORS.get(coll, (72, 68, 66))
                else:
                    color = self.TERRAIN_COLORS.get(row_base[x], self.UNKNOWN)
                surf.set_at((x, y), color)
        return surf

    def _map_rect(self, tilemap):
        """Where the scaled map is drawn, preserving aspect ratio.

        Durotar is 110x240 (tall) while the Barrens is 200x160 (wide), so a
        fixed draw rect would distort one or the other badly. Scale is chosen
        from whichever axis is tighter.
        """
        avail_w = SCREEN_WIDTH - 340   # leave a legend column on the right
        avail_h = SCREEN_HEIGHT - 150  # leave room for title and footer
        scale = min(avail_w / tilemap.width, avail_h / tilemap.height)
        w = int(tilemap.width * scale)
        h = int(tilemap.height * scale)
        x = 30 + (avail_w - w) // 2
        y = 100 + (avail_h - h) // 2
        return pygame.Rect(x, y, w, h)

    def _tile_to_screen(self, tilemap, rect, tx, ty):
        return (rect.x + int(tx / tilemap.width * rect.width),
                rect.y + int(ty / tilemap.height * rect.height))

    # ------------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_m):
                self.state_manager.transition_to(GameState.OVERWORLD)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button.collidepoint(event.pos):
                self.state_manager.transition_to(GameState.OVERWORLD)

    def render(self, screen):
        screen.fill((18, 18, 26))
        zm = self._zone_manager()
        if not zm or not zm.current_zone:
            self.renderer.draw_text(screen, "No map available", (40, 40),
                                    size="large", color=(200, 200, 100))
            return

        tilemap = zm.current_zone

        # Title: zone name, plus the specific subzone/cave you're standing in
        location = zm.get_location_name() if hasattr(zm, "get_location_name") else tilemap.name
        title = tilemap.name
        self.renderer.draw_text(screen, title, (30, 22), size="large",
                                color=(220, 200, 120))
        sub = location if location != tilemap.name else (tilemap.region or "")
        if sub:
            self.renderer.draw_text(screen, sub, (30, 56), color=(170, 170, 190))

        # Close button
        pygame.draw.rect(screen, (70, 60, 40), self.close_button)
        pygame.draw.rect(screen, (200, 180, 120), self.close_button, 2)
        ct = self.renderer.font_normal.render("Close", True, (255, 240, 200))
        screen.blit(ct, ct.get_rect(center=self.close_button.center))

        # Terrain (cached per zone)
        if self._cached_zone != tilemap.name or self._cached_surface is None:
            self._cached_surface = self._build_terrain_surface(tilemap)
            self._cached_zone = tilemap.name

        rect = self._map_rect(tilemap)
        screen.blit(pygame.transform.scale(self._cached_surface, (rect.width, rect.height)),
                    (rect.x, rect.y))
        pygame.draw.rect(screen, (120, 110, 90), rect, 2)

        # Subzone region outlines + labels. Every subzone gets a visible
        # name - previously any region under 60x20 screen px, or whose
        # rendered name didn't fit inside its own rect at the default
        # font size, silently got NO label at all (Kyle: "only some are
        # [labeled]. players need to be able to see what each subzone is
        # called"). Dungeon chambers, small landmarks and cave nooks are
        # routinely smaller than that threshold, so this wasn't a rare
        # edge case - it was most of a typical dungeon's subzones.
        #
        # Fixed by never skipping a label outright: shrink the font
        # first (tries progressively smaller sizes until the name fits
        # the region's width, floor 10px - still legible at the map's
        # zoomed-out scale), and if even the smallest size can't fit
        # inside a genuinely tiny region, place the label just above the
        # region instead of inside it, rather than dropping it.
        #
        # Adjacent subzones (sharing a long edge, both wide enough to
        # qualify for a label) can have their centered text strings
        # visually collide even though the RECTS themselves don't overlap
        # - each label used to be positioned with zero awareness of its
        # neighbors. Confirmed in Durotar: "Thunder Ridge" and "Skull Rock
        # Approach" sit side by side and their names ran into each other.
        # Stable per-name vertical stagger (hash-based, not random per
        # frame) still spreads same-row neighbors across a couple of rows.
        # A subzone authored as a CHAIN of rectangles (e.g. Southern Barrens' winding Rift canyon) is one region:
        # group by name, outline only the outer boundary (no seams between chain links) and label it ONCE.
        groups = {}
        for sz in tilemap.subzones:
            sx, sy = self._tile_to_screen(tilemap, rect, sz["x"], sz["y"])
            ex, ey = self._tile_to_screen(tilemap, rect,
                                          sz["x"] + sz["w"], sz["y"] + sz["h"])
            region = pygame.Rect(sx, sy, max(2, ex - sx), max(2, ey - sy))
            groups.setdefault(sz["name"], []).append(region)

        def _free_spans(lo, hi, covered):
            """Pieces of [lo, hi] not inside any (a, b) interval in `covered`."""
            spans = [(lo, hi)]
            for a_, b_ in covered:
                nxt = []
                for l, h in spans:
                    if b_ <= l or a_ >= h:
                        nxt.append((l, h))
                        continue
                    if a_ > l:
                        nxt.append((l, a_))
                    if b_ < h:
                        nxt.append((b_, h))
                spans = nxt
            return spans

        outline = (170, 160, 110)
        for name, regions in groups.items():
            for r in regions:
                pygame.draw.line(screen, outline, (r.left, r.top), (r.right, r.top))
                pygame.draw.line(screen, outline, (r.left, r.bottom), (r.right, r.bottom))
                # side edges: skip the stretch shared with a same-name neighbour (the chain's internal seams)
                for edge_x, other_edge in ((r.left, "right"), (r.right, "left")):
                    covered = [(o.top, o.bottom) for o in regions
                               if o is not r and abs(getattr(o, other_edge) - edge_x) <= 1]
                    for lo, hi in _free_spans(r.top, r.bottom, covered):
                        pygame.draw.line(screen, outline, (edge_x, lo), (edge_x, hi))

            # label once: on the link that holds the group's horizontal centre (single-rect groups: itself)
            cx = (min(r.left for r in regions) + max(r.right for r in regions)) // 2
            region = min(regions, key=lambda r: abs(r.centerx - cx)) if len(regions) > 1 else regions[0]
            max_label_width = max(1, (max(r.right for r in regions) - min(r.left for r in regions)) - 8
                                  if len(regions) > 1 else region.width - 8)
            label = None
            for font_size in (16, 14, 12, 10):
                candidate = self.renderer._get_font(font_size=font_size).render(
                    name, True, (200, 190, 140))
                if candidate.get_width() <= max_label_width:
                    label = candidate
                    break
            if label is None:
                # Even the smallest size doesn't fit the region's width -
                # region is too narrow to ever hold this name inline, so
                # place it just above instead of shrinking further into
                # illegibility.
                label = self.renderer._get_font(font_size=10).render(
                    name, True, (200, 190, 140))
                lrect = label.get_rect(midbottom=(region.centerx, region.y - 2))
                screen.blit(label, lrect)
                continue

            row_offset = (hash(name) % 3) * 14
            label_y = region.y + 12 + row_offset
            # If the staggered row would push the label below the
            # region's own bottom edge (small/short regions), clamp back
            # to vertically centered instead - better than drifting the
            # name out of its own box.
            if label_y + label.get_height() > region.bottom:
                label_y = region.centery - label.get_height() // 2
            lrect = label.get_rect(center=((cx if len(regions) > 1 else region.centerx),
                                           label_y + label.get_height() // 2))
            screen.blit(label, lrect)

        # Points of interest from the interaction layer
        poi_colors = {
            "portal": (170, 90, 230),
            "npc": (230, 200, 90),
            "chest": (230, 150, 60),
            "quest_marker": (110, 210, 230),
        }
        for y in range(tilemap.height):
            row = tilemap.interaction_layer[y]
            for x in range(tilemap.width):
                kind = row[x]
                if kind in poi_colors:
                    px, py = self._tile_to_screen(tilemap, rect, x, y)
                    pygame.draw.circle(screen, poi_colors[kind], (px, py), 4)
                    pygame.draw.circle(screen, (20, 20, 20), (px, py), 4, 1)

        # Boss portraits. boss_marker interaction tiles carry no creature
        # identity of their own (they're just a red ground tile - see
        # world/tiles.py) - the actual boss NAME for a given chamber only
        # exists on CaveSpawnManager's live SpawnPoint list, built by
        # ZoneManager.transition_to_zone() -> cave_spawns.populate() on
        # entry (world/zone_manager.py). That's why this reads
        # zm.cave_spawns.spawns instead of scanning the interaction layer
        # like the poi_colors loop above - it only has real data while
        # you're actually inside the dungeon/cave the spawns were
        # populated for, which is exactly when a boss map is useful.
        # Each boss's template (humanoid_caster, beast_large, ...) maps to
        # a themed portrait icon via boss_icons.py - see that module for
        # why this is template-level, not one bespoke icon per boss name.
        cave_spawns = getattr(zm, "cave_spawns", None)
        if cave_spawns:
            for spawn in cave_spawns.spawns:
                if not spawn.is_boss or spawn.defeated:
                    continue
                creature = zm.creature_manager.creatures.get(spawn.creature_name, {})
                template = creature.get("template")
                icon = self._get_boss_icon(template)
                px, py = self._tile_to_screen(tilemap, rect, spawn.x, spawn.y)
                if icon:
                    icon_rect = icon.get_rect(center=(px, py))
                    screen.blit(icon, icon_rect)
                else:
                    # Icon file failed to load (shouldn't happen with the
                    # full template table, but fails soft rather than
                    # silently drawing nothing where a boss actually is).
                    pygame.draw.circle(screen, (255, 0, 0), (px, py), 6)
                    pygame.draw.circle(screen, (20, 20, 20), (px, py), 6, 1)

        # Player marker, drawn last so it is never hidden
        px, py = self._tile_to_screen(tilemap, rect, zm.player_x, zm.player_y)
        pygame.draw.circle(screen, (255, 255, 255), (px, py), 7)
        pygame.draw.circle(screen, (220, 40, 40), (px, py), 5)

        # Legend
        lx = SCREEN_WIDTH - 290
        ly = 110
        self.renderer.draw_text(screen, "Legend", (lx, ly), size="large",
                                color=(220, 200, 120))
        ly += 36
        legend = [
            ((220, 40, 40), "You are here"),
            (poi_colors["portal"], "Portal / cave entrance"),
            (poi_colors["npc"], "NPC / vendor"),
            (poi_colors["chest"], "Treasure"),
            (poi_colors["quest_marker"], "Point of interest"),
        ]
        for color, text in legend:
            pygame.draw.circle(screen, color, (lx + 7, ly + 7), 6)
            self.renderer.draw_text(screen, text, (lx + 22, ly), color=(200, 200, 210))
            ly += 26
        # Boss portrait swatch drawn separately from the plain-circle
        # legend loop above since it's an icon, not a flat color.
        boss_sample = self._get_boss_icon(None, size=20)  # "_default" template
        if boss_sample:
            screen.blit(boss_sample, (lx - 3, ly - 2))
        else:
            pygame.draw.circle(screen, (255, 0, 0), (lx + 7, ly + 7), 6)
        self.renderer.draw_text(screen, "Boss", (lx + 22, ly), color=(200, 200, 210))

    def _get_boss_icon(self, template, size=18):
        """Loaded-and-scaled boss portrait Surface for a creature template,
        cached by (template, size). Returns None if the file can't be
        loaded (missing/corrupt PNG) so callers can fall back to the old
        plain-dot marker instead of crashing the whole map render."""
        cache_key = (template, size)
        if cache_key in self._boss_icon_cache:
            return self._boss_icon_cache[cache_key]
        try:
            path = get_boss_icon_path(template)
            raw = pygame.image.load(str(path)).convert_alpha()
            icon = pygame.transform.smoothscale(raw, (size, size))
        except (pygame.error, FileNotFoundError):
            icon = None
        self._boss_icon_cache[cache_key] = icon
        return icon

        ly += 14
        self.renderer.draw_text(screen, f"Size: {tilemap.width} x {tilemap.height}",
                                (lx, ly), color=(150, 150, 165))
        ly += 24
        self.renderer.draw_text(screen, f"Position: {zm.player_x}, {zm.player_y}",
                                (lx, ly), color=(150, 150, 165))

        footer = "M or ESC: close map"
        fw = self.renderer.font_normal.size(footer)[0]
        self.renderer.draw_text(screen, footer,
                                (SCREEN_WIDTH // 2 - fw // 2, SCREEN_HEIGHT - 34),
                                color=(150, 150, 150))
