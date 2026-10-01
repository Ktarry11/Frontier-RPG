"""
Zone system. Defines zones, encounters, and connections.
"""
import random
from entities.character import Character


class Zone:
    """Represents a game zone/area."""
    
    def __init__(self, name, description, connected_zones=None):
        self.name = name
        self.description = description
        self.connected_zones = connected_zones or {}  # Dict of {"direction": zone_name}
        self.encounter_table = []  # List of possible enemies
        self.enemy_level_range = (1, 5)
    
    def add_encounter(self, enemy_name, enemy_class, weight=1.0):
        """Add enemy to encounter table."""
        self.encounter_table.append({
            "name": enemy_name,
            "class": enemy_class,
            "weight": weight
        })
    
    def get_random_encounter(self):
        """Get a random enemy from encounter table."""
        if not self.encounter_table:
            return None
        
        # Weighted random selection
        choices = [e["name"] for e in self.encounter_table]
        weights = [e["weight"] for e in self.encounter_table]
        chosen_name = random.choices(choices, weights=weights, k=1)[0]
        
        # Find the full encounter data
        encounter = next(e for e in self.encounter_table if e["name"] == chosen_name)
        
        # Create enemy with random level in range
        level = random.randint(*self.enemy_level_range)
        enemy = Character(encounter["name"], encounter["class"], level)
        
        return enemy


class ZoneManager:
    """Manages all zones and player movement."""
    
    def __init__(self):
        self.zones = {}
        self.current_zone = None
        self._initialize_zones()
    
    def _initialize_zones(self):
        """Create test zones for Phase 0."""
        # Zone 1: Starter meadow
        zone1 = Zone(
            "Starter Meadow",
            "A peaceful meadow. Looks like trouble might be nearby."
        )
        zone1.add_encounter("Goblin Scout", "Rogue", weight=2.0)
        zone1.add_encounter("Forest Spider", "Rogue", weight=1.0)
        zone1.enemy_level_range = (1, 3)
        zone1.connected_zones = {"east": "Dark Forest"}
        
        # Zone 2: Dark forest
        zone2 = Zone(
            "Dark Forest",
            "A dense, dark forest. You hear ominous sounds."
        )
        zone2.add_encounter("Dire Wolf", "Warrior", weight=2.0)
        zone2.add_encounter("Forest Troll", "Warrior", weight=1.0)
        zone2.enemy_level_range = (3, 6)
        zone2.connected_zones = {"west": "Starter Meadow"}
        
        self.zones["Starter Meadow"] = zone1
        self.zones["Dark Forest"] = zone2
        self.current_zone = zone1
    
    def move_to_zone(self, zone_name):
        """Move player to a zone."""
        if zone_name in self.zones:
            self.current_zone = self.zones[zone_name]
            return True
        return False
    
    def get_current_zone(self):
        """Get current zone."""
        return self.current_zone
    
    def trigger_encounter(self):
        """Trigger a random encounter in current zone."""
        if self.current_zone:
            return self.current_zone.get_random_encounter()
        return None
