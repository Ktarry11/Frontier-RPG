"""
Creature manager - loads creature definitions and spawns Monster instances.
"""
import json
import random
from pathlib import Path
from entities.monster import Monster


class CreatureManager:
    """Manages creature definitions and spawning."""
    
    def __init__(self):
        self.creatures = {}
        self.encounters = {}
        self._load_data()
    
    def _load_data(self):
        """Load creature data from JSON files."""
        data_dir = Path(__file__).parent.parent / "data" / "creatures"
        
        # Load creatures
        creatures_file = data_dir / "creatures.json"
        if creatures_file.exists():
            with open(creatures_file, 'r') as f:
                self.creatures = json.load(f).get("creatures", {})
        
        # Load encounters
        encounters_file = data_dir / "encounters.json"
        if encounters_file.exists():
            with open(encounters_file, 'r') as f:
                self.encounters = json.load(f).get("zones", {})
    
    # A subzone roll blends its own table with the parent zone's open_zone
    # table at this fraction of a single open_zone entry's total weight -
    # "raptor grounds" should read as raptor TERRITORY within the Barrens,
    # not a sealed box where nothing else from the zone ever wanders
    # through (Kyle: "the Barrens can have raptors everywhere, but higher
    # chance in raptor grounds"). Caves are NOT blended - a cave is its
    # own separate instanced map with its own theme (Wailing Caverns
    # shouldn't have Barrens surface critters bleeding in), this is only
    # about open-world subzones inside a zone the player is already
    # walking through.
    SUBZONE_OPEN_ZONE_BLEND = 0.35

    def get_encounter_table(self, zone_name, location_type="open_zone", subzone_name=None):
        """Get encounter table for a zone/subzone/cave.

        For a subzone, this BLENDS the subzone's own creatures with the
        parent zone's open_zone table rather than fully replacing it (see
        SUBZONE_OPEN_ZONE_BLEND) - real bug found + fixed this pass: every
        subzone before this was a 100% exclusive pool, so stepping into
        Harpy Roost meant literally nothing but harpies could ever spawn,
        not even a Plainstrider passing through. The subzone's own
        creatures keep their authored weights (so the "this IS harpy
        territory" read stays strong); the zone's open_zone creatures are
        added in at a flat fraction of the zone table's total weight, so
        a zone with many open_zone entries doesn't get diluted more than
        one with few just because it has more distinct species listed.
        """
        if zone_name not in self.encounters:
            return {}

        zone_data = self.encounters[zone_name]

        if location_type == "open_zone":
            return zone_data.get("open_zone", {}).get("creatures", {})
        elif location_type == "subzone" and subzone_name:
            subzone_table = dict(
                zone_data.get("subzones", {}).get(subzone_name, {}).get("creatures", {}))
            open_table = zone_data.get("open_zone", {}).get("creatures", {})
            subzone_total = sum(subzone_table.values())
            if not subzone_table or subzone_total <= 0:
                # A subzone with no roster of its own (or one that's all
                # weight-0 bosses, e.g. Shrine of the Fallen Warrior -
                # deliberately "a quiet, low-combat waypoint" per its own
                # generator comment) isn't a bug to special-case: it just
                # has nothing to blend INTO, so it falls straight through
                # to the parent zone's plain open_zone table instead of
                # returning empty.
                return dict(open_table)
            open_total = sum(open_table.values())
            if open_table and open_total > 0:
                blend_budget = subzone_total * self.SUBZONE_OPEN_ZONE_BLEND
                for name, weight in open_table.items():
                    if name in subzone_table:
                        # Already in the subzone's own table (its own
                        # entry there authoritatively sets how common it
                        # is here) - don't double it up with a second,
                        # separately-weighted open_zone contribution.
                        continue
                    share = blend_budget * (weight / open_total)
                    if share > 0:
                        subzone_table[name] = share
            return subzone_table
        elif location_type == "cave" and subzone_name:
            return zone_data.get("caves", {}).get(subzone_name, {}).get("creatures", {})

        return {}
    
    def spawn_creature(self, creature_name, level=None):
        """Spawn a creature (Monster instance)."""
        if creature_name not in self.creatures:
            return None
        
        creature_def = self.creatures[creature_name]
        template_name = creature_def.get("template")
        
        # Determine level
        if level is None:
            level_range = creature_def.get("level_range", [1, 1])
            level = random.randint(level_range[0], level_range[1])
        
        # Get ability kit if specified, otherwise Monster uses template default
        ability_kit = creature_def.get("ability_kit")
        
        # Create Monster using template + ability kit
        monster = Monster(creature_name, template_name, level, kit=ability_kit)
        
        # Apply boss multiplier if applicable
        if creature_def.get("is_boss", False):
            boss_multiplier = creature_def.get("boss_multiplier", 2.5)
            monster.is_boss = True
            monster.max_health = int(monster.max_health * boss_multiplier)
            monster.current_health = monster.max_health
            monster.attack_power = int(monster.attack_power * boss_multiplier * 0.75)
            if hasattr(monster, 'spell_power'):
                monster.spell_power = int(monster.spell_power * boss_multiplier * 0.75)
        
        return monster
    
    #: Chance per encounter roll, in a subzone with a real named rare in
    #: its table, that the rare appears instead of ordinary trash. Real
    #: WoW rares are an uncommon "oh, it's actually here" moment, not a
    #: guaranteed one-per-visit fixed spawn (subzones are open-world and
    #: always-on, unlike caves - there's no "clear it, it stays cleared"
    #: dungeon semantics to hang a fixed spawn point off of), so this is
    #: a genuine low-probability roll rather than a scaled-up weight.
    RARE_SPAWN_CHANCE = 0.06

    def get_random_creature(self, zone_name, location_type="open_zone", subzone_name=None):
        """Get a random weighted creature from an encounter table."""
        encounter_table = self.get_encounter_table(zone_name, location_type, subzone_name)

        if not encounter_table:
            return None

        # Bosses are excluded from the random roll, not just relied on to
        # carry a weight of 0. Weight-0 entries are effectively excluded
        # by random.choices already, but that's a convention, not a
        # guarantee - a random-roll cave's boss (see CaveSpawnManager's
        # place_trash=False caves) is meant to be encountered exactly
        # once, at its pinned chamber, never from this roll. Filtering by
        # is_boss here makes that a real guarantee instead of "don't
        # forget to set weight 0."
        trash_table = {
            name: weight for name, weight in encounter_table.items()
            if not self.creatures.get(name, {}).get("is_boss", False)
        }

        # Subzone rares: named is_boss creatures in a SUBZONE's table
        # (Verog the Dervish in Kolkar Plains, Supervisor Lugwizzle in
        # Sludge Fen, ...) have no cave-style fixed-chamber mechanism to
        # spawn from - subzones aren't discrete maps CaveSpawnManager can
        # place a marker tile in, they're a rectangle inside a bigger
        # always-on overworld map. Without this, marking them is_boss
        # (correctly, so they're not diluting ordinary trash odds) made
        # them completely unreachable: excluded from trash_table above,
        # and nothing else in the game ever rolls for them. This gives
        # them a real, low, independent chance to appear instead of
        # ordinary trash on any roll in their subzone.
        if location_type == "subzone":
            rare_names = [
                name for name in encounter_table
                if self.creatures.get(name, {}).get("is_boss", False)
            ]
            if rare_names and random.random() < self.RARE_SPAWN_CHANCE:
                chosen_creature = random.choice(rare_names)
                creature = self.spawn_creature(chosen_creature)
                if creature:
                    creature.location_type = location_type
                return creature

        if not trash_table:
            return None

        # Weighted random selection
        creatures = list(trash_table.keys())
        weights = list(trash_table.values())
        chosen_creature = random.choices(creatures, weights=weights, k=1)[0]
        
        # Spawn creature
        creature = self.spawn_creature(chosen_creature)
        if creature:
            # Tag with location_type so combat can apply a dungeon/cave XP
            # bonus (see combat_engine._calculate_exp_reward). ZoneManager.
            # get_location_context() now genuinely detects when the player
            # is standing in a subzone or cave and requests the matching
            # table (see its own docstring for that fix's history) - this
            # location_type tag is live and does fire the bonus in actual
            # play, not just wired-but-dormant plumbing.
            creature.location_type = location_type

        return creature
    
    def get_available_subzones(self, zone_name):
        """Get list of subzone names in a zone."""
        if zone_name not in self.encounters:
            return []
        return list(self.encounters[zone_name].get("subzones", {}).keys())
    
    def get_available_caves(self, zone_name):
        """Get list of cave names in a zone."""
        if zone_name not in self.encounters:
            return []
        return list(self.encounters[zone_name].get("caves", {}).keys())
