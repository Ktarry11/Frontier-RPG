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


FLIGHT_GREEN = (80, 220, 100)
INN_AMBER = (240, 170, 60)
MOUNT_BLUE = (100, 170, 245)
HEARTH_GOLD = (255, 215, 70)
CLASS_VIOLET = (190, 130, 240)
PROF_TEAL = (90, 210, 205)
FORGE_ORANGE = (255, 125, 45)
SAW_TAN = (210, 170, 105)
#: Shop vendors. Kyle, 2026-10-31: "Can we get a map icon indicating vendors?
#: Since I can't find vendors in towns without clicking on every single person."
#: Deliberately a warm yellow, distinct from INN_AMBER and FORGE_ORANGE, because
#: all three cluster in the same few tiles of a town square.
SHOP_YELLOW = (255, 215, 90)


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
        "tropical_shallow": (72, 158, 154),
        "tropical_water": (20, 96, 110),
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
            # A boat crossing is a way out of the zone like any portal, and was missing from
            # the map entirely - only tiles typed "portal" were marked.
            "boat": (170, 90, 230),
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
                icon = self._get_boss_icon(template, name=spawn.creature_name)
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

        # Travel services: inns, riding trainers / mount vendors and flight masters. These NPCs live in two
        # places (ambient NPCs and vendors), so both are scanned. Flight masters go on top.
        from world.ambient_npc_manager import get_ambient_npc_manager
        from world.travel_manager import services_for_npc, get_travel_manager
        service_npcs = list(get_ambient_npc_manager().get_npcs_in_zone(tilemap.name))
        vendor_mgr = getattr(zm, "vendor_manager", None)
        if vendor_mgr is not None:
            service_npcs += list(vendor_mgr.get_vendors_in_zone(tilemap.name))
        markers = {"inn": set(), "ride": set(), "flight": set(), "class": set(), "prof": set(),
                   "forge": set(), "sawmill": set(), "shop": set()}
        for npc in service_npcs:
            svcs = services_for_npc(npc)
            for svc in svcs:
                kind = {"inn": "inn", "riding": "ride", "mounts": "ride", "flight": "flight",
                        "train_class": "class", "train_prof": "prof"}.get(svc)
                if kind:
                    markers[kind].add((npc.x, npc.y))
            # PLAIN SHOPS. Kyle: "I can't find vendors in towns without clicking
            # on every single person." Trainers, innkeepers and flight masters
            # already had their own glyph; the NPC who simply sells you things
            # had nothing but the same grey dot every other person in town gets,
            # which made the actual shop the one thing on the map you could not
            # find. Only tagged when the NPC has stock and no service glyph of
            # its own, so an innkeeper who also sells food stays an innkeeper
            # rather than collecting a second marker on the same tile.
            if svcs:
                continue
            sells = (list(getattr(npc, "sells", None) or [])
                     or bool(getattr(npc, "sells_gear", False)))
            if sells:
                markers["shop"].add((npc.x, npc.y))
        # Crafting stations: forges (ore -> bars) and sawmills (logs -> planks)
        for forge in getattr(zm, "forge_manager", None) and zm.forge_manager.get_forges_in_zone(tilemap.name) or []:
            markers["forge"].add((forge.x, forge.y))
        for mill in getattr(zm, "sawmill_manager", None) and zm.sawmill_manager.get_forges_in_zone(tilemap.name) or []:
            markers["sawmill"].add((mill.x, mill.y))
        # Hearthstone: a gold star behind the innkeeper icon (only when the bind is in this zone)
        bind = get_travel_manager().bind
        if bind and bind.get("zone") == tilemap.name:
            hx, hy = self._tile_to_screen(tilemap, rect, bind["x"], bind["y"])
            self._draw_service_icon(screen, "hearth", hx, hy)

        for kind in ("shop", "forge", "sawmill", "prof", "class", "inn", "ride", "flight"):
            for tx, ty in sorted(markers[kind]):
                fx, fy = self._tile_to_screen(tilemap, rect, tx, ty)
                self._draw_service_icon(screen, kind, fx, fy)

        # GATHERING TRACKING. Kyle, 10 Nov: WoW-style Find Minerals / Find Herbs on the map.
        # Every node in this zone that has not been gathered, for a gathering trade the player
        # has LEARNED - a miner sees veins, a herbalist sees herbs, someone with neither sees
        # nothing new. Drawn under the player marker and the service icons, so a node never
        # hides a flight master.
        self._tracked_nodes = []
        known = self._tracked_professions()
        if known:
            gm = zm.gathering_manager
            for node in getattr(gm, "active_nodes", []) or []:
                if node.gathered:
                    continue
                data = gm.materials.get(node.material_id) or {}
                if data.get("profession") not in known:
                    continue
                kind = data.get("material_type")
                if kind not in self.TRACK_COLORS:
                    continue
                nx, ny = self._tile_to_screen(tilemap, rect, node.x, node.y)
                self._draw_track_dot(screen, kind, nx, ny)
                self._tracked_nodes.append((kind, node.x, node.y))

        # Player marker. It used to be drawn last, as a solid disc, "so it is never hidden" -
        # and so it hid whatever was under it. Open the map while talking to the flight
        # master, which is exactly when anyone looks for the flight master, and the disc sat
        # on his icon: Kyle, 10 Nov, "some flight masters not showing on map (like zoram
        # strand)". The icon was drawn; it was underneath.
        #
        # The disc still goes down, and then any service icon it would cover is drawn again
        # ON TOP of it. The player is never where an NPC is (they stand beside them), so the
        # disc stays readable next to the icon instead of over it.
        px, py = self._tile_to_screen(tilemap, rect, zm.player_x, zm.player_y)
        pygame.draw.circle(screen, (255, 255, 255), (px, py), 7)
        pygame.draw.circle(screen, (220, 40, 40), (px, py), 5)
        self._icons_over_player = 0
        for kind in ("shop", "forge", "sawmill", "prof", "class", "inn", "ride", "flight"):
            for tx, ty in sorted(markers[kind]):
                fx, fy = self._tile_to_screen(tilemap, rect, tx, ty)
                if abs(fx - px) < 18 and abs(fy - py) < 18:
                    self._draw_service_icon(screen, kind, fx, fy)
                    self._icons_over_player += 1

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
        # Tracked gathering nodes - only the kinds this player can actually see.
        # No crystal row: there are no crystal nodes to mine (Kyle, 12 Nov: "there is no crystal
        # mining. Delete crystals."). Crystals only ever come out of an ore vein as a bonus.
        for kind, text in (("ore", "Ore vein (Mining)"),
                           ("herb", "Herb (Herbalism)"), ("wood", "Tree (Woodcutting)")):
            if self.TRACK_PROFESSION[kind] in known:
                self._draw_track_dot(screen, kind, lx + 7, ly + 7)
                self.renderer.draw_text(screen, text, (lx + 22, ly), color=(200, 200, 210))
                ly += 26
        # Service icons are glyphs, so the legend uses the same drawing code as the map.
        for kind, text in (("shop", "Vendor (buy / sell)"),
                           ("flight", "Flight master"), ("inn", "Innkeeper (bind hearth)"),
                           ("ride", "Riding trainer / mounts"), ("hearth", "Your hearth is bound here"),
                           ("class", "Class trainer"), ("prof", "Profession trainers"),
                           ("forge", "Forge (ore to bars)"), ("sawmill", "Sawmill (logs to planks)")):
            self._draw_service_icon(screen, kind, lx + 7, ly + 7, scale=0.7)
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
        ly += 26        # the Boss row's own height - without it "Size:" printed on top of it

        # These three were UNREACHABLE: at some point a method got spliced into the middle of
        # this one and they ended up below `return icon` inside _get_boss_icon, where they also
        # referenced four locals (tilemap, zm, lx, ly) that only exist here. Python never
        # complained because dead code is not checked, so the map has quietly had no size
        # readout, no position readout and no "close map" hint for however long that has been
        # true. Moved back where they belong.
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

    #: Tracked node colours: a small diamond, so it cannot be mistaken for the round NPC and
    #: portal dots.
    TRACK_COLORS = {"ore": (235, 150, 60), "herb": (110, 220, 90), "wood": (170, 120, 70)}
    TRACK_PROFESSION = {"ore": "mining", "herb": "herbalism", "wood": "woodcutting"}

    def _tracked_professions(self):
        """The gathering trades the player has learned."""
        player = getattr(self.state_manager, "player", None)
        if player is None:
            return set()
        known = set(getattr(player, "known_professions", []) or [])
        return known & set(self.TRACK_PROFESSION.values())

    def _draw_track_dot(self, screen, kind, cx, cy):
        color = self.TRACK_COLORS[kind]
        pts = [(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)]
        pygame.draw.polygon(screen, (10, 10, 12), [(x + (1 if x > cx else -1 if x < cx else 0),
                                                    y + (1 if y > cy else -1 if y < cy else 0)) for x, y in pts])
        pygame.draw.polygon(screen, color, pts)

    def _draw_service_icon(self, screen, kind, cx, cy, scale=1.0):
        """Small procedural map glyphs: flight '!' / inn house / horseshoe / hearth star."""
        dark = (20, 20, 20)
        if kind == "flight":
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, FLIGHT_GREEN, (cx, cy), 8, 2)
            font = self.renderer._get_font(font_size=14)
            glyph = font.render("!", True, FLIGHT_GREEN)
            screen.blit(glyph, glyph.get_rect(center=(cx, cy)))
        elif kind == "inn":
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, INN_AMBER, (cx, cy), 8, 2)
            pygame.draw.polygon(screen, INN_AMBER, [(cx - 5, cy), (cx, cy - 5), (cx + 5, cy)])
            pygame.draw.rect(screen, INN_AMBER, (cx - 3, cy, 6, 4))
            pygame.draw.rect(screen, dark, (cx - 1, cy + 1, 2, 3))
        elif kind == "ride":
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, MOUNT_BLUE, (cx, cy), 8, 2)
            pygame.draw.arc(screen, MOUNT_BLUE, (cx - 4, cy - 4, 8, 8), 3.14159, 6.28318, 2)
            pygame.draw.line(screen, MOUNT_BLUE, (cx - 4, cy), (cx - 4, cy - 3), 2)
            pygame.draw.line(screen, MOUNT_BLUE, (cx + 3, cy), (cx + 3, cy - 3), 2)
        elif kind == "class":
            # sword: diagonal blade, crossguard, pommel
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, CLASS_VIOLET, (cx, cy), 8, 2)
            pygame.draw.line(screen, CLASS_VIOLET, (cx - 4, cy + 4), (cx + 4, cy - 4), 2)
            pygame.draw.line(screen, CLASS_VIOLET, (cx - 4, cy - 1), (cx + 1, cy + 4), 2)
        elif kind == "prof":
            # hammer: handle + head
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, PROF_TEAL, (cx, cy), 8, 2)
            pygame.draw.line(screen, PROF_TEAL, (cx - 3, cy + 4), (cx + 2, cy - 2), 2)
            pygame.draw.rect(screen, PROF_TEAL, (cx - 1, cy - 5, 6, 4))
        elif kind == "forge":
            # flame over an anvil base
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, FORGE_ORANGE, (cx, cy), 8, 2)
            pygame.draw.polygon(screen, FORGE_ORANGE, [(cx, cy - 5), (cx + 3, cy), (cx + 2, cy + 3), (cx - 2, cy + 3), (cx - 3, cy)])
            pygame.draw.rect(screen, dark, (cx - 1, cy - 1, 2, 3))
        elif kind == "sawmill":
            # circular saw blade
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, SAW_TAN, (cx, cy), 8, 2)
            pygame.draw.circle(screen, SAW_TAN, (cx, cy), 4)
            pygame.draw.circle(screen, dark, (cx, cy), 1)
            for dx, dy in ((0, -5), (0, 5), (-5, 0), (5, 0)):
                pygame.draw.rect(screen, SAW_TAN, (cx + dx - 1, cy + dy - 1, 2, 2))
        elif kind == "shop":
            # a coin: filled disc with a rim and a slot, which reads at 8px where
            # a coin-purse outline just turns into a blob
            pygame.draw.circle(screen, dark, (cx, cy), 8)
            pygame.draw.circle(screen, SHOP_YELLOW, (cx, cy), 8, 2)
            pygame.draw.circle(screen, SHOP_YELLOW, (cx, cy), 4)
            pygame.draw.line(screen, dark, (cx, cy - 3), (cx, cy + 3), 2)
        elif kind == "hearth":
            import math
            pts = []
            for i in range(10):
                ang = -math.pi / 2 + i * math.pi / 5
                r = (14 if i % 2 == 0 else 6.5) * scale
                pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
            pygame.draw.polygon(screen, dark, [(x + (x - cx) * 0.2, y + (y - cy) * 0.2) for x, y in pts])
            pygame.draw.polygon(screen, HEARTH_GOLD, pts)

    def _get_boss_icon(self, template, size=18, name=None):
        """Map marker for a boss, cached by (name, template, size).

        THE REAL CREATURE FIRST. boss_icons.py maps a stat template to one of eight themed
        portraits, which was the best available when nothing had art; now that every creature
        resolves to its own sprite, the map can show the thing the player is about to fight
        instead of a category. Compared side by side at 18px the sprite also simply reads
        better - the portraits are dark and low-contrast and half vanish against the map, while
        the sprites keep their colour and silhouette - so this is not consistency bought at the
        cost of legibility.

        Falls back to the old portrait, and then to None so callers can draw the plain dot,
        rather than letting a missing PNG crash the map's render loop."""
        cache_key = (name, template, size)
        if cache_key in self._boss_icon_cache:
            return self._boss_icon_cache[cache_key]
        if name:
            try:
                from ui.sprite_loader import get_creature_sprite
                # Asked for at a tile size that makes the 4.0 boss multiplier land on `size`,
                # so this marker and the dungeon floor are driven by the same scale table
                # rather than by a second opinion about how big a boss is.
                art = get_creature_sprite(name, template, max(1, round(size / 4.0)), boss=True)
                if art is not None and art.get_height():
                    k = size / art.get_height()
                    art = pygame.transform.smoothscale(
                        art, (max(1, round(art.get_width() * k)), size))
                    self._boss_icon_cache[cache_key] = art
                    return art
            except Exception:
                pass
        try:
            path = get_boss_icon_path(template)
            raw = pygame.image.load(str(path)).convert_alpha()
            icon = pygame.transform.smoothscale(raw, (size, size))
        except (pygame.error, FileNotFoundError):
            icon = None
        self._boss_icon_cache[cache_key] = icon
        return icon
