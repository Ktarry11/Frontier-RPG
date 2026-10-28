"""
Zone manager. Manages all zones, tilemaps, and player movement.
"""
import random
from entities.monster import Monster
from world.zone_generator import create_all_zones
from world.creature_manager import CreatureManager
from world.cave_spawns import CaveSpawnManager
from world.portal_manager import PortalManager
from world.vendor_manager import get_vendor_manager
from world.gathering_manager import get_gathering_node_manager
from world.forge_manager import get_forge_manager
from world.sawmill_manager import get_sawmill_manager
from world.chest_manager import get_chest_manager
from ui.sprite_loader import prewarm_chunk_sprites
from world.tile_textures import TILE_SIZE


class ZoneManager:
    """Manages all zones and player movement."""
    
    def __init__(self):
        self.zones = {}
        self.current_zone = None
        self.player_x = 0
        self.player_y = 0
        self.player_facing = "down"  # last movement direction - "down"/"up"/"left"/"right",
        # used only for sprite selection (see tilemap_renderer.py). Not a gameplay-affecting
        # value, purely which way the player's sprite faces when standing still.

        self.creature_manager = CreatureManager()

        # Fixed cave spawns. Caves do NOT use the random encounter roll -
        # you see the mob, you fight the mob, and nothing respawns until you
        # leave and come back (bestiary design rule).
        self.cave_spawns = CaveSpawnManager(self.creature_manager)
        self.pending_spawn = None  # SpawnPoint the player just walked into
        self.portal_manager = PortalManager()
        self.vendor_manager = get_vendor_manager()  # Phase 6: vendor NPCs
        self.gathering_manager = get_gathering_node_manager()
        self.forge_manager = get_forge_manager()
        self.sawmill_manager = get_sawmill_manager()
        self.chest_manager = get_chest_manager()
        self._initialize_zones()
    
    def _initialize_zones(self):
        """Create all zones with tilemaps."""
        all_zones = create_all_zones()
        
        for zone_name, tilemap in all_zones.items():
            self.zones[zone_name] = {
                "tilemap": tilemap,
            }

        # Caves declare a parent zone in .region; overworld zones don't point
        # at another map. Used to tag encounters as location_type="cave".
        self.cave_names = {
            name for name, tm in all_zones.items() if getattr(tm, "is_cave", False)
        }
        
        # Carve every tile a recruit could ever stand on, in any zone, from
        # recruits.json - both their wild spawn AND their home town. Zones
        # are generated once at launch but a dismissal can happen at any
        # time, so the home tile has to be walkable up front.
        self._place_recruit_tiles()

        # Same carve-on-load treatment for ambient flavor NPCs (guards,
        # townsfolk, etc from ambient_npcs.json) - previously MISSING
        # entirely, meaning any ambient NPC whose hand-picked coordinate
        # happened to land on terrain-scatter rock/wall/water was
        # silently unreachable forever (get_npc_at_location is a pure
        # coordinate match with no walkability dependency, so this bug
        # would never surface as a crash, only as "I walked there and
        # nothing happened"). Added alongside the Durotar-cluster NPC
        # population expansion since that's ~30 new hand-placed
        # coordinates at once - exactly the scenario that bit vendors
        # before this pattern existed for them.
        self._place_ambient_npc_tiles()

        # Start player in the default start zone (world/start_zones.py). ZoneManager is built once per
        # process, before any character exists, so there is nothing to ask here - the real choice is
        # applied by reset_to_start() when a character is created.
        from world.start_zones import get_start, DEFAULT_START_ID
        _start = get_start(DEFAULT_START_ID)
        self.start_id = _start.start_id
        self.current_zone = self.zones[_start.zone_name]["tilemap"]
        self.player_x = _start.x
        self.player_y = _start.y  # Near the zone's level-1 quest giver
        # Pre-scale every chunk sprite for the starting zone up front -
        # see prewarm_chunk_sprites' docstring for why (fixes "I step
        # once and a chunk just pops into existence", a cold
        # smoothscale happening inside the render loop instead of here).
        prewarm_chunk_sprites(self.current_zone, TILE_SIZE)

        # Roll the initial gathering node layout for the starting zone -
        # transition_to_zone() handles every LATER zone entry, but the
        # very first zone is set directly above rather than via a
        # transition, so it needs its own populate() call here or the
        # player would start in a zone with zero nodes until they left
        # and came back once.
        self.gathering_manager.populate(self.current_zone, self.current_zone.name)
    
    def reset_to_start(self, start_id=None):
        """Snap back to the real starting position - Valley of Trials,
        the same spot __init__ sets up. Real bug this fixes: OverworldScreen
        (and this ZoneManager) is constructed ONCE at GameStateManager
        startup and lives for the whole process (see
        core/game_state.py's eager `states` dict), not rebuilt per
        character. So starting a brand NEW character after already
        having played and moved around in the same running session
        silently carried the OLD character's last position into the new
        character's save file the moment CharacterCreationScreen called
        save_game() - "new level 1 character starts exactly where the
        old one left off", reported live. Called from
        CharacterCreationScreen._create_character right before saving, so
        a genuinely new character always saves with a genuinely fresh
        starting position, regardless of where the previous character
        left the world.

        start_id picks WHICH start (world/start_zones.py). Omitted, it keeps the default, so every
        existing caller behaves exactly as it did before start zones existed."""
        from world.start_zones import get_start
        start = get_start(start_id or getattr(self, "start_id", None))
        self.start_id = start.start_id
        self.current_zone = self.zones[start.zone_name]["tilemap"]
        self.player_x = start.x
        self.player_y = start.y
        self.player_facing = "down"
        prewarm_chunk_sprites(self.current_zone, TILE_SIZE)
        # The new zone needs its own node roll for the same reason __init__ does: this is a direct
        # assignment, not a transition, so nothing else will populate it. Without this a character
        # starting in Deathknell saw zero gathering nodes until they left the zone and came back.
        self.gathering_manager.populate(self.current_zone, self.current_zone.name)

    def _place_recruit_tiles(self):
        """
        Mark and carve recruit tiles from the single source of truth.

        Every hand-placed feature that must be reachable gets a carved
        landing first - vendors once shipped standing on tiles that terrain
        scatter had sealed off, and the entire vendor system silently did
        nothing as a result.
        """
        from world.zone_generator import ZoneGenerator
        from world.recruit_manager import get_recruit_manager

        manager = get_recruit_manager()
        lookup = {self._normalize_zone_key(name): data["tilemap"]
                  for name, data in self.zones.items()}

        for zone_name, x, y in manager.all_world_positions():
            tilemap = lookup.get(self._normalize_zone_key(zone_name))
            if tilemap is None:
                print(f"Recruit tile references unknown zone '{zone_name}'; skipped.")
                continue
            if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
                print(f"Recruit tile ({x},{y}) is outside '{zone_name}'; skipped.")
                continue
            ZoneGenerator._carve_landing(tilemap, x, y, radius=1)
            tilemap.set_tile(x, y, "npc", "interaction")

    def _place_ambient_npc_tiles(self):
        """
        Mark and carve ambient NPC tiles from the single source of truth,
        identical pattern to _place_recruit_tiles above - see
        AmbientNPCManager.all_world_positions' docstring for why this was
        a real gap, not a defensive no-op.
        """
        from world.zone_generator import ZoneGenerator
        from world.ambient_npc_manager import get_ambient_npc_manager

        manager = get_ambient_npc_manager()
        lookup = {self._normalize_zone_key(name): data["tilemap"]
                  for name, data in self.zones.items()}

        for zone_name, x, y in manager.all_world_positions():
            tilemap = lookup.get(self._normalize_zone_key(zone_name))
            if tilemap is None:
                print(f"Ambient NPC tile references unknown zone '{zone_name}'; skipped.")
                continue
            if not (0 <= x < tilemap.width and 0 <= y < tilemap.height):
                print(f"Ambient NPC tile ({x},{y}) is outside '{zone_name}'; skipped.")
                continue
            ZoneGenerator._carve_landing(tilemap, x, y, radius=1)
            tilemap.set_tile(x, y, "npc", "interaction")

    @staticmethod
    def _normalize_zone_key(zone):
        """Match RecruitManager's normalization ("Valley of Trials" -> valley_of_trials)."""
        key = str(zone).lower().replace(" ", "_").replace("'", "")
        # "The Sepulcher" (zone) vs "sepulcher" (NPC data): a leading article never distinguishes zones
        return key[4:] if key.startswith("the_") else key

    def get_current_zone(self):
        """Get current zone tilemap."""
        return self.current_zone
    
    def get_zone_by_name(self, zone_name):
        """Get a zone by name."""
        if zone_name in self.zones:
            return self.zones[zone_name]["tilemap"]
        return None
    
    def move_player(self, dx, dy):
        """Try to move player. Returns True if successful."""
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # Facing updates on any directional input, even if the move itself
        # gets blocked below (bounds/walkability/collision) - real games
        # let you turn to face a wall without needing to actually step
        # into it, and it costs nothing to set here regardless of outcome.
        if dx > 0:
            self.player_facing = "right"
        elif dx < 0:
            self.player_facing = "left"
        elif dy > 0:
            self.player_facing = "down"
        elif dy < 0:
            self.player_facing = "up"
        
        # Check bounds
        if not (0 <= new_x < self.current_zone.width and 0 <= new_y < self.current_zone.height):
            return False
        
        # Check walkability
        if not self.current_zone.is_walkable(new_x, new_y):
            return False
        
        # Check collision layer
        collision = self.current_zone.get_tile(new_x, new_y, "collision")
        if collision:
            return False
        
        self.player_x = new_x
        self.player_y = new_y

        # Hearthstone cooldown is counted in overworld steps.
        from world.travel_manager import get_travel_manager
        get_travel_manager().on_step()

        # Position-gated EXPLORE quest objectives (e.g. "reach the
        # hallway", not just "enter the cave") - see
        # QuestManager.record_position_reached. Cheap no-op for the
        # common case (no active quest has a position gate).
        if self.current_zone:
            from world.quest_manager import get_quest_manager
            zone_key = self.current_zone.name.lower().replace(" ", "_").replace("'", "")
            get_quest_manager().record_position_reached(zone_key, new_x, new_y)

        return True
    
    def get_player_pos(self):
        """Get player position."""
        return (self.player_x, self.player_y)
    
    def check_interaction(self):
        """Check if player is on an interaction tile."""
        interaction = self.current_zone.get_interaction(self.player_x, self.player_y)
        return interaction
    
    def trigger_encounter(self, player_level=1):
        """Trigger a random encounter scaled to player level.
        
        Args:
            player_level: Current player level
        
        Returns:
            Monster object (enemy) or None
        """
        # Caves are their own map, but their encounter table lives under the
        # PARENT zone in encounters.json (Durotar -> caves -> Skull Rock), so
        # the lookup must use the parent name, not the cave's own name.
        location_type, subzone_key = self.get_location_context()
        zone_name = (self.current_zone.region if self.is_in_cave()
                     else self.current_zone.name)
        targets = self.active_kill_targets()
        enemy = self.creature_manager.get_random_creature(
            zone_name, location_type=location_type, subzone_name=subzone_key, quest_targets=targets)

        # Fall back to the open-zone table if a subzone has no table entry,
        # so a geographic region without encounter data never yields None.
        if enemy is None and location_type != "open_zone":
            enemy = self.creature_manager.get_random_creature(
                zone_name, location_type="open_zone")
        return enemy

    #: Per-step chance of a random encounter, by where you are standing.  Subzones are the themed hunting
    #: grounds quests send you to, so they roll much more often than the open zone (2% per step meant
    #: ~170 steps per Marsh Skimmer - quest targets simply never seemed to spawn).
    ENCOUNTER_CHANCE = {"open_zone": 0.02, "subzone": 0.05, "cave": 0.03}

    def encounter_chance(self):
        """Per-step random-encounter chance for the player's current tile."""
        location_type, _ = self.get_location_context()
        chance = self.ENCOUNTER_CHANCE.get(location_type, 0.02)
        # Riding shaves the ambush rate (TravelManager.encounter_mult is 1.0 on foot). Caves never see a mounted player.
        from world.travel_manager import get_travel_manager
        return chance * get_travel_manager().encounter_mult()

    def active_kill_targets(self):
        """Names of creatures an active, unfinished quest still needs killed (incl. alternates)."""
        from world.quest_manager import get_quest_manager
        from world.quest import ObjectiveType
        names = set()
        for quest in get_quest_manager().get_active_quests():
            for o in quest.objectives:
                if o.objective_type in (ObjectiveType.KILL, ObjectiveType.KILL_BOSS) and o.progress < o.count:
                    if o.target:
                        names.add(o.target)
                    names.update(getattr(o, "alt_targets", None) or [])
        return names

    def trigger_encounter_group(self, player_level=1, party_size=1):
        """
        Roll a GROUP of enemies scaled to how many people are in the party.

        A five-person party against a single boar is not a fight, it's an
        execution - so encounter size tracks party size. Caves and subzones
        add an extra body on top of that, which is the difficulty lever that
        makes those tiers actually feel more dangerous rather than just
        higher-level.

        Returns a list of Monsters (never empty unless the zone has no
        encounter data at all).
        """
        location_type, _subzone = self.get_location_context()

        # Roughly one enemy per two party members, so a full party of 5 faces
        # 3 enemies rather than 5 - the party should still have the edge in
        # an open-zone trash pull.
        count = max(1, (party_size + 1) // 2)
        if location_type == "cave":
            count += 1
        elif location_type == "subzone":
            count += 1 if party_size >= 4 else 0

        enemies = []
        for _ in range(count):
            enemy = self.trigger_encounter(player_level)
            if enemy:
                enemies.append(enemy)
        return enemies

    def get_location_context(self):
        """Return (location_type, subzone_key) for the player's current tile.

        This is the missing link that makes the subzone/cave XP multipliers
        real. They were built, tested and correct, but trigger_encounter()
        hardcoded location_type="open_zone" because nothing could tell what
        region the player was standing in - so cave and subzone bonuses have
        never once fired in actual play.
        """
        if not self.current_zone:
            return ("open_zone", None)

        # A cave is its own map. generate_cave() registers one subzone
        # covering the whole map, keyed to the cave's encounter table.
        if self.is_in_cave():
            return ("cave", self.current_zone.name)

        sz = self.current_zone.get_subzone_at(self.player_x, self.player_y)
        if sz:
            return ("subzone", sz["table_key"])
        return ("open_zone", None)

    def is_in_cave(self):
        """True if the current map is a cave rather than an overworld zone."""
        return self.current_zone.name in self.cave_names

    def has_fixed_spawns(self):
        """True if the current cave should use fixed spawn points (a real
        dungeon/mini-dungeon) rather than random per-tile encounter rolls
        (a cave-like pocket - Skull Rock, Dustwind Cave, etc). Only
        meaningful when is_in_cave() is True; overworld zones always roll
        random regardless of this.
        """
        return self.is_in_cave() and getattr(self.current_zone, "fixed_spawns", True)

    def get_location_name(self):
        """Human-readable current location, for the map screen and HUD."""
        if not self.current_zone:
            return ""
        if self.is_in_cave():
            return self.current_zone.name
        sz = self.current_zone.get_subzone_at(self.player_x, self.player_y)
        return sz["name"] if sz else self.current_zone.name
    
    def transition_to_zone(self, zone_name, spawn_x=None, spawn_y=None):
        """
        Move player to a new zone. If spawn_x/spawn_y are given, the player
        lands there; otherwise falls back to zone center (used only when no
        portal data specifies an exact arrival point).
        """
        new_zone = self.get_zone_by_name(zone_name)
        if new_zone:
            # Cave exits register their arrival point as the exact overworld
            # entrance tile (portal_manager.py's coordinate for "walk out of
            # the cave" and "walk into the cave" is the same tile, since it's
            # the cave-mouth mouth_offset spot - see zone_generator.py). The
            # mouth landmark's footprint extends NORTH from that tile (the
            # opening faces south, per mouth_offset=(1,2)), so landing
            # exactly on it puts the player pressed up against the cave
            # structure instead of a step clear of it. Nudge one tile south
            # only when leaving a cave into the overworld - entering a cave
            # should still land on its own authored entrance chamber
            # unchanged, and non-cave portals (boats, town gates) aren't
            # cave mouths and shouldn't be shifted.
            leaving_cave = (self.current_zone is not None
                             and getattr(self.current_zone, "is_cave", False)
                             and not getattr(new_zone, "is_cave", False)
                             and spawn_x is not None and spawn_y is not None)

            self.current_zone = new_zone
            if new_zone.name in self.cave_names:
                from world.travel_manager import get_travel_manager
                get_travel_manager().force_dismount()   # no riding in caves/dungeons
            # Same prewarm as __init__/reset_to_start - see that call's
            # comment. This is the path that actually matters most in
            # practice (every portal/cave transition during real play),
            # not just the one-time game start.
            prewarm_chunk_sprites(self.current_zone, TILE_SIZE)
            target_x = spawn_x if spawn_x is not None else new_zone.width // 2
            target_y = spawn_y if spawn_y is not None else new_zone.height // 2

            if leaving_cave:
                # portal_manager offsets the spawn 2 tiles NORTH of the
                # portal tile (the right call when entering a cave), which
                # on the overworld side is up inside the cave-mouth
                # landmark - the walkability net below then snapped the
                # player ONTO the portal tile itself. Land one tile
                # SOUTH of the portal tile instead (spawn_y + 3), clear of
                # the mouth and of the trigger.
                target_y += 3

            # Safety net: portal_manager.py's coordinates are static data
            # authored against a generator's output at some point in time.
            # Every time a zone/cave generator changes shape (a resize, a
            # re-carved entrance, ...), any registry entry pointing at it
            # can go stale and land the player on solid rock or off in an
            # unrelated pocket of the map - exactly what was happening in
            # several caves after their resize pass. Rather than trusting
            # the static coordinate blindly, verify it's actually walkable
            # and, if not, search outward for the nearest walkable tile
            # instead of teleporting the player into a wall.
            if not new_zone.is_walkable(target_x, target_y):
                found = self._find_nearest_walkable(new_zone, target_x, target_y)
                if found:
                    target_x, target_y = found

            self.player_x = target_x
            self.player_y = target_y

            # Advance any active EXPLORE quest objective targeting this
            # zone - same slug normalization every other zone-keyed
            # lookup uses (VendorManager._zone_key, combat_screen.py's
            # combat_zone_key, race_registry.get_zone_default_race).
            # Fires on every successful transition, including re-entering
            # a zone already explored - record_zone_entered is itself
            # idempotent (is_complete() guards it), so this is safe to
            # call unconditionally rather than needing a "have I already
            # told the quest system about this zone" check here too.
            from world.quest_manager import get_quest_manager
            zone_key = new_zone.name.lower().replace(" ", "_").replace("'", "")
            get_quest_manager().record_zone_entered(zone_key)

            # Entering a cave lays out a fresh set of fixed spawns; leaving
            # clears them. Because populate() wipes the previous layout, this
            # single call is what implements "no respawns until you exit and
            # re-enter" - the layout only ever regenerates on entry.
            # place_trash follows the zone's own fixed_spawns flag: real
            # dungeons get full fixed trash (place_trash=True), cave-like
            # pockets get ONLY their boss chamber(s) placed here and rely
            # on the random per-tile roll (trigger_encounter_group) for
            # trash instead - see has_fixed_spawns()/OverworldScreen.
            if self.is_in_cave():
                self.cave_spawns.populate(
                    new_zone,
                    new_zone.region,
                    boss_position=getattr(new_zone, "boss_position", None),
                    boss_positions=getattr(new_zone, "boss_positions", None),
                    place_trash=self.has_fixed_spawns(),
                )
            else:
                self.cave_spawns.clear()

            # Gathering nodes: always call populate(), overworld or cave -
            # populate() itself now decides what a zone gets (real ore
            # table for overworld zones, a synthesized ore-only table for
            # mining caves via CAVE_TO_PARENT_ZONE, a hard no-op for any
            # real Dungeon or any zone with no pool entry at all - see
            # GatheringNodeManager.populate()'s is_dungeon() guard and
            # world/zone_classification.py for the confirmed Dungeon
            # list). Kyle, 2026-09-12: "caves (and keeps) are fine, just
            # not dungeons" - so the old blanket "clear in every cave"
            # branch this replaced was actually wrong once ore-in-caves
            # became a real ask, not just an oversimplification that
            # happened to work before dungeons and mining caves needed
            # different treatment. populate() unconditionally wipes and
            # re-rolls first regardless of outcome, which is itself the
            # "reroll a % of nodes every time you leave and come back"
            # behavior Kyle asked for originally.
            self.gathering_manager.populate(new_zone, new_zone.name)

            self.pending_spawn = None
            return True
        return False

    @staticmethod
    def _find_nearest_walkable(zone, x, y, max_radius=15):
        """Spiral outward from (x, y) and return the nearest walkable tile,
        or None if nothing within max_radius is walkable (a genuinely
        malformed map, at which point there's nothing safe left to do)."""
        if zone.is_walkable(x, y):
            return (x, y)
        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Only check the ring at exactly this radius, so closer
                    # tiles are always tried (and found) before farther ones.
                    if max(abs(dx), abs(dy)) != radius:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < zone.width and 0 <= ny < zone.height:
                        if zone.is_walkable(nx, ny):
                            return (nx, ny)
        return None

    def check_fixed_spawn(self):
        """In a cave, return the Monster for a spawn point the player has
        stepped onto (and consume it), else None.

        OverworldScreen calls this INSTEAD of the random encounter roll when
        in a cave - that's what makes caves finite mini-dungeons rather than
        infinite grind spots.
        """
        if not self.is_in_cave():
            return None
        sp = self.cave_spawns.spawn_at(self.player_x, self.player_y)
        if not sp:
            return None
        monster = self.cave_spawns.build_monster(sp)
        self.cave_spawns.consume(sp)
        self.pending_spawn = sp
        return monster

    def check_fixed_spawn_group(self):
        """Like check_fixed_spawn but returns the WHOLE pack (list of Monsters) - dungeon pulls of 3-4 fight together."""
        if not self.is_in_cave():
            return []
        sp = self.cave_spawns.spawn_at(self.player_x, self.player_y)
        if not sp:
            return []
        monsters = self.cave_spawns.build_monsters(sp)
        self.cave_spawns.consume(sp)
        self.pending_spawn = sp
        return monsters

    def try_use_portal(self):
        """
        Check if the player is standing on a portal or boat tile and, if so,
        use the PortalManager registry to find exactly where it leads.
        Returns True if a transition happened, False otherwise (not on a
        portal/boat, or this tile has no registered link).

        "boat" is a real interaction type (Silverpine South <-> Fenris Isle,
        Ratchet's dock, ...) registered in portal_manager.py exactly like a
        portal - it was being silently ignored here, so every boat crossing
        in the game failed outright despite being fully wired up everywhere
        else (the tile existed, the registry had the link, only this check
        never looked for it).
        """
        interaction = self.current_zone.get_interaction(self.player_x, self.player_y)
        if interaction not in ("portal", "boat"):
            return False

        destination = self.portal_manager.get_destination(
            self.current_zone.name, self.player_x, self.player_y
        )
        if destination is None:
            # Portal tile exists but has no registered destination - fail safe
            # rather than teleporting somewhere undefined.
            return False

        dest_zone, spawn_x, spawn_y = destination
        return self.transition_to_zone(dest_zone, spawn_x, spawn_y)

    def get_vendor_at_location(self):
        """Check if there's a vendor NPC at the player's current location."""
        if not self.current_zone:
            return None
        return self.vendor_manager.get_vendor_at_location(
            self.current_zone.name, self.player_x, self.player_y
        )

    def get_forge_at_location(self):
        """Check if there's a Forge at the player's current location -
        same coordinate-only lookup pattern as get_vendor_at_location,
        no tilemap layer involved (see forge_manager.py's docstring)."""
        if not self.current_zone:
            return None
        return self.forge_manager.get_forge_at_location(
            self.current_zone.name, self.player_x, self.player_y
        )

    def get_sawmill_at_location(self):
        """Sawmill within reach of the player (same lookup as the Forge)."""
        if not self.current_zone:
            return None
        return self.sawmill_manager.get_forge_at_location(
            self.current_zone.name, self.player_x, self.player_y
        )

    def get_recruit_at_location(self):
        """Check for a recruitable companion at the player's current tile."""
        if not self.current_zone:
            return None
        from world.recruit_manager import get_recruit_manager
        return get_recruit_manager().get_recruit_at_location(
            self.current_zone.name, self.player_x, self.player_y
        )

    def get_ambient_npc_at_location(self):
        """Check for a flavor/ambient NPC at the player's current tile -
        same lookup pattern as vendor/recruit. Ambient NPCs only ever
        show a greeting (see AmbientNPC), never open a shop or recruit
        screen, so callers just need to know one exists to print its line."""
        if not self.current_zone:
            return None
        from world.ambient_npc_manager import get_ambient_npc_manager
        return get_ambient_npc_manager().get_npc_at_location(
            self.current_zone.name, self.player_x, self.player_y
        )

    def get_gathering_node_at_location(self):
        """Check for an active, ungathered node at the player's current
        tile - same lookup pattern as vendor/recruit/ambient NPC."""
        if not self.current_zone:
            return None
        return self.gathering_manager.get_node_at(self.player_x, self.player_y)

    def gather_node(self, node):
        """Gather the given node, returning the material_id it dropped
        (or None if it was already gathered). Clears its interaction tile
        via GatheringNodeManager.gather so the player can't double-dip."""
        if not self.current_zone:
            return None
        return self.gathering_manager.gather(node, self.current_zone)

    #: How close (in tiles) a chest must be to the zone's own
    #: boss_position to count as a "boss chest" (floored rarity,
    #: guaranteed drop) rather than a regular side-room chest. Loose
    #: enough to cover every existing generator's chest offset (all
    #: currently place it within 2-7 tiles of boss_position - e.g.
    #: Skull Rock's boss[1]-3, Tiragarde's great_hall[1]-5) without
    #: needing every generator's exact offset hardcoded here.
    BOSS_CHEST_RADIUS = 8

    def get_chest_at_location(self):
        """Check for a real, unlooted chest tile at the player's current
        location - same lookup pattern as vendor/recruit/gathering node."""
        if not self.current_zone:
            return None
        if self.chest_manager.get_chest_at_location(self.current_zone, self.player_x, self.player_y):
            return (self.player_x, self.player_y)
        return None

    def _is_boss_chest(self, x, y):
        boss_pos = getattr(self.current_zone, "boss_position", None)
        if boss_pos is None:
            return False
        dx, dy = x - boss_pos[0], y - boss_pos[1]
        return (dx * dx + dy * dy) ** 0.5 <= self.BOSS_CHEST_RADIUS

    def open_chest(self, chest_pos, player_level):
        """Open the chest at chest_pos (from get_chest_at_location),
        returning an Item or None (empty chest - a real, intended
        outcome, see chest_manager.py's docstring)."""
        if not self.current_zone:
            return None
        x, y = chest_pos
        is_boss = self._is_boss_chest(x, y)
        return self.chest_manager.open_chest(
            self.current_zone, x, y, player_level, is_boss_chest=is_boss
        )

    def handle_portal(self, zone_name):
        """Legacy entry point - kept for backward compatibility, but prefer
        try_use_portal() which reads the actual portal tile you're standing
        on instead of trusting a caller-provided zone_name."""
        return self.transition_to_zone(zone_name)
