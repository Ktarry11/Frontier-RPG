"""
Fixed spawn points for caves.

WHY
---
Caves previously used the same weighted random-encounter roll as open zones,
which meant two things the bestiary design doc explicitly rules out:

  * The cave boss was just another entry on the weight table, so you could
    fight Gazz'uz three times in the entrance chamber and never meet him at
    the back - or clear the whole cave and never see him at all.
  * Encounters respawned forever, making a cave a grind spot rather than a
    finite mini-dungeon.

The doc calls for: "Caves use fixed spawn points, not random encounter rolls.
You see the mob, you fight the mob." and "One Cave Boss at the deepest point"
and "No respawns inside a cave until the player exits and re-enters."

This module implements exactly that. Spawn points are generated once per
cave visit, placed on walkable tiles, and each is consumed when defeated.
Re-entering the cave regenerates them.
"""
import random


class SpawnPoint:
    """A single fixed encounter sitting on a specific tile."""

    def __init__(self, x, y, creature_name, is_boss=False, level=None, members=None):
        self.x = x
        self.y = y
        self.creature_name = creature_name
        self.is_boss = is_boss
        self.level = level
        self.defeated = False
        # A PACK: every member is on its own tile and stepping next to ANY of them pulls them all into one fight
        # (group dungeon pulls of 3-4). members = [(x, y, name, level), ...]; a plain spawn is a pack of one.
        self.members = list(members) if members else [(x, y, creature_name, level)]

    def __repr__(self):
        state = "defeated" if self.defeated else "active"
        return f"<SpawnPoint {self.creature_name} @({self.x},{self.y}) {state}>"


class CaveSpawnManager:
    """Owns the fixed spawn layout for the cave the player is currently in.

    One instance lives on ZoneManager. populate() is called on entering a
    cave and wipes whatever was there before, which is what gives the
    "no respawns until you leave and come back" behaviour for free.
    """

    # How close you must be to a spawn point to trigger it.
    TRIGGER_RADIUS = 1

    def __init__(self, creature_manager):
        self.creature_manager = creature_manager
        self.spawns = []
        self.cave_name = None

    # ------------------------------------------------------------------

    def clear(self):
        self.spawns = []
        self.cave_name = None

    def populate(self, cave_map, parent_zone, boss_position=None, boss_positions=None,
                 place_trash=True):
        """Lay out fixed spawns for a cave.

        Trash is scattered across walkable tiles weighted by the cave's
        encounter table. Bosses are placed at fixed chambers rather than
        rolled, guaranteeing exactly one boss per chamber per visit.

        boss_positions (optional): list of chamber entries for multi-boss
        dungeons (Wailing Caverns, Ragefire Chasm, etc. all advertise 4-5
        named bosses). Each entry is either:
          (x, y)            - unpinned chamber, filled from the shared
                               boss pool (legacy behaviour, random which
                               named boss lands here).
          (x, y, boss_name) - pinned chamber, always spawns exactly
                               boss_name. Landmark-themed rooms (a crab
                               statue, a shipwreck) need this - an
                               unpinned chamber next to crab statuary
                               could roll an undead pirate on some visits
                               and the giant crab on others, which reads
                               as a bug even though every chamber does
                               get *a* boss. Pinned bosses are removed
                               from the shared pool before any unpinned
                               chamber draws from it, so a dungeon mixing
                               pinned and unpinned chambers still can't
                               double up the same boss in two rooms.
        boss_position (optional): single-chamber caves keep the old
        single-position argument for backward compatibility.
        place_trash: True (default) lays out fixed trash spawn points
        alongside any boss chambers - real dungeons/mini-dungeons, no
        respawns until you leave and re-enter. False places ONLY the boss
        chamber(s) and leaves trash to the random per-tile encounter roll
        (trigger_encounter_group) instead - cave-like pockets (Skull
        Rock, Dustwind Cave, ...) that should feel like the open world
        with one fixed mini-boss at the end, not a finite dungeon clear.
        """
        self.clear()
        self.cave_name = cave_map.name

        table = self.creature_manager.get_encounter_table(
            parent_zone, "cave", cave_map.name)
        if not table:
            return

        # Split the table into boss and trash. Bosses are identified from
        # creatures.json rather than by weight, so a rare non-boss stays
        # trash and a boss never ends up as filler.
        bosses, trash = [], {}
        for name, weight in table.items():
            definition = self.creature_manager.creatures.get(name, {})
            if definition.get("is_boss", False):
                bosses.append(name)
            else:
                trash[name] = weight

        walkable = [(x, y) for y in range(cave_map.height)
                    for x in range(cave_map.width) if cave_map.is_walkable(x, y)]
        if not walkable:
            return

        # Keep trash away from the exit portal so you aren't ambushed the
        # instant you walk in, and away from the boss so its chamber reads
        # as its own encounter.
        exits = [(x, y) for y in range(cave_map.height)
                 for x in range(cave_map.width)
                 if cave_map.interaction_layer[y][x] == "portal"]

        def far_enough(pos, others, min_dist):
            return all((pos[0] - o[0]) ** 2 + (pos[1] - o[1]) ** 2 >= min_dist ** 2
                       for o in others)

        # Resolve the working list of boss chambers: prefer the new
        # multi-boss list, fall back to the single legacy position.
        raw_chambers = list(boss_positions) if boss_positions else (
            [boss_position] if boss_position else [])

        # Each entry is (x, y) - unpinned - or (x, y, boss_name) - pinned.
        # Split them apart up front so pinned names can be reserved from
        # the shared pool before any unpinned chamber draws from it.
        pinned_chambers = []   # (x, y, boss_name)
        unpinned_chambers = [] # (x, y)
        for entry in raw_chambers:
            if len(entry) == 3:
                pinned_chambers.append(entry)
            else:
                unpinned_chambers.append(entry)

        boss_positions_placed = []
        if bosses and (pinned_chambers or unpinned_chambers):
            available_bosses = list(bosses)

            # Pinned chambers first: place the named boss exactly where
            # its generator put it, and take it out of the pool so an
            # unpinned chamber elsewhere in the same dungeon can't also
            # roll it.
            for (bx, by, boss_name) in pinned_chambers:
                if not cave_map.is_walkable(bx, by):
                    bx, by = min(walkable, key=lambda p: (p[0] - bx) ** 2 + (p[1] - by) ** 2)
                boss_positions_placed.append((bx, by))
                if boss_name not in self.creature_manager.creatures:
                    raise ValueError(
                        f"{cave_map.name}: pinned boss '{boss_name}' has no "
                        f"entry in creatures.json")
                if boss_name not in table:
                    raise ValueError(
                        f"{cave_map.name}: pinned boss '{boss_name}' is not "
                        f"in this cave's encounter table")
                # A BOSS PACK: two bosses, one fight. Kyle's Return Voyage
                # finale is "a double boss fight of BOTH bloodsail leaders at
                # once", and the leaders are standing in the same cabin - the
                # second one does not have a chamber of his own to be pinned
                # to. Two boss_positions entries would be two chambers, two
                # fights and two loot rolls; folding the extra members into
                # this SpawnPoint's `members` makes it one encounter that
                # happens to have two bosses in it, which is what the pack
                # machinery already does for trash. See zone.boss_pack.
                extra = (getattr(cave_map, "boss_pack", None) or {}).get(boss_name) or []
                members = [(bx, by, boss_name, None)]
                for member in extra:
                    mx, my, mname = member[0], member[1], member[2]
                    if not cave_map.is_walkable(mx, my):
                        mx, my = min(walkable,
                                     key=lambda p: (p[0] - mx) ** 2 + (p[1] - my) ** 2)
                    if mname not in self.creature_manager.creatures:
                        raise ValueError(
                            f"{cave_map.name}: boss-pack member '{mname}' has "
                            f"no entry in creatures.json")
                    members.append((mx, my, mname, member[3] if len(member) > 3 else None))
                    if mname in available_bosses:
                        available_bosses.remove(mname)
                self.spawns.append(SpawnPoint(
                    bx, by, boss_name, is_boss=True,
                    members=members if extra else None))
                if boss_name in available_bosses:
                    available_bosses.remove(boss_name)

            # Unpinned chambers: same pool-and-cycle behaviour as before,
            # just drawing from whatever the pinned pass didn't reserve.
            for (bx, by) in unpinned_chambers:
                if not cave_map.is_walkable(bx, by):
                    bx, by = min(walkable, key=lambda p: (p[0] - bx) ** 2 + (p[1] - by) ** 2)
                boss_positions_placed.append((bx, by))
                # Assign a distinct boss per chamber where the table has
                # enough named bosses; once the pool is exhausted, cycle
                # rather than crash, so a dungeon with 5 chambers but only
                # 3 defined bosses still fills every chamber.
                if not available_bosses:
                    available_bosses = list(bosses)
                chosen = random.choice(available_bosses)
                available_bosses.remove(chosen)
                self.spawns.append(SpawnPoint(bx, by, chosen, is_boss=True))

        boss_pos = boss_positions_placed[0] if boss_positions_placed else None

        # Trash count scales with cave size - a 40x34 cave gets noticeably
        # fewer fights than a 60x54 one. Cap raised for the massive
        # (~240x220) dungeons added post-launch, which are roughly 5x the
        # area of the largest original cave and would otherwise still be
        # stuck at the old 16-trash ceiling and feel empty.
        area = cave_map.width * cave_map.height
        trash_count = max(5, min(40, area // 190))

        # Authored dungeons (multi-boss, e.g. The Broodspiral) carry their own HAND-PLACED trash list:
        #   zone.trash_spawns = [(x, y, "Creature"), (x, y, "Creature", level), ...]
        # Placed exactly where the layout author put them (room by room, level ramping with depth); the
        # random scatter below is only the fallback for dungeons that have not been authored yet.
        hand = getattr(cave_map, "trash_spawns", None)
        packs = getattr(cave_map, "trash_packs", None)
        if place_trash and packs:
            # PACKS (tools/dungeon_pulls.py): each pack is one pull of 3-4 mobs that fight together.
            for pack in packs:
                for (hx, hy, hname, hlevel) in pack:
                    if hname not in self.creature_manager.creatures:
                        raise ValueError(f"{cave_map.name}: trash_packs creature '{hname}' has no entry in creatures.json")
                    if not cave_map.is_walkable(hx, hy):
                        raise ValueError(f"{cave_map.name}: trash_packs '{hname}' at ({hx},{hy}) is not walkable")
                lead = pack[0]
                self.spawns.append(SpawnPoint(lead[0], lead[1], lead[2], level=lead[3], members=pack))
        elif place_trash and hand:
            for entry in hand:
                hx, hy, hname = entry[0], entry[1], entry[2]
                hlevel = entry[3] if len(entry) > 3 else None
                if hname not in self.creature_manager.creatures:
                    raise ValueError(f"{cave_map.name}: trash_spawns creature '{hname}' has no entry in creatures.json")
                if not cave_map.is_walkable(hx, hy):
                    raise ValueError(f"{cave_map.name}: trash_spawns '{hname}' at ({hx},{hy}) is not walkable")
                self.spawns.append(SpawnPoint(hx, hy, hname, level=hlevel))
        elif place_trash and trash:
            names = list(trash.keys())
            weights = list(trash.values())
            blocked = list(exits) + boss_positions_placed
            candidates = [p for p in walkable
                          if far_enough(p, blocked, 7)]
            random.shuffle(candidates)

            placed = []
            for pos in candidates:
                if len(placed) >= trash_count:
                    break
                # Spread trash out so they read as distinct encounters.
                if not far_enough(pos, placed, 5):
                    continue
                placed.append(pos)
                self.spawns.append(
                    SpawnPoint(pos[0], pos[1],
                               random.choices(names, weights=weights, k=1)[0]))

    # ------------------------------------------------------------------

    def spawn_at(self, x, y):
        """Return the first live spawn point within TRIGGER_RADIUS, or None."""
        for sp in self.spawns:
            if sp.defeated:
                continue
            for (mx, my, _n, _l) in sp.members:
                if abs(mx - x) <= self.TRIGGER_RADIUS and abs(my - y) <= self.TRIGGER_RADIUS:
                    return sp
        return None

    def consume(self, spawn_point):
        """Mark a spawn as defeated so it never fires again this visit."""
        spawn_point.defeated = True

    def build_monsters(self, spawn_point):
        """Every Monster of a spawn point (a pack pulls together), tagged as cave kills."""
        out = []
        for (_x, _y, name, level) in spawn_point.members:
            m = self.creature_manager.spawn_creature(name, level)
            if m:
                m.location_type = "cave"
                from world.difficulty import apply_health
                apply_health(m)
                out.append(m)
        return out

    def build_monster(self, spawn_point):
        """Instantiate the Monster for a spawn point, tagged as a cave kill."""
        monster = self.creature_manager.spawn_creature(
            spawn_point.creature_name, spawn_point.level)
        if monster:
            monster.location_type = "cave"
            from world.difficulty import apply_health
            apply_health(monster)
        return monster

    # ------------------------------------------------------------------

    def remaining(self):
        return sum(1 for s in self.spawns if not s.defeated)

    def boss_alive(self):
        return any(s.is_boss and not s.defeated for s in self.spawns)

    def is_cleared(self):
        return self.spawns and self.remaining() == 0

    def active_positions(self):
        """(x, y, is_boss, creature_name) for every live spawn - used by
        the overworld renderer to actually show you the mobs. creature_name
        was added (2026-09-09) so the renderer can resolve a real per-boss
        portrait icon (see boss_icons.py) instead of a flat placeholder -
        the map screen doesn't use this method at all (it reads
        self.spawns directly, see ui/screens/map_screen.py), so extending
        this tuple shape only affects the overworld live-view renderer."""
        return [(mx, my, s.is_boss, mn) for s in self.spawns if not s.defeated
                for (mx, my, mn, _ml) in s.members]
