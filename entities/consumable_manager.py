"""
ConsumableManager - loads consumable definitions from JSON and creates Consumable instances.
Parallel to CreatureManager for creatures/monsters.
"""
import json
from pathlib import Path
from entities.consumable import Consumable


class ConsumableManager:
    """Manages consumable types and instance creation."""
    
    def __init__(self):
        """Load all consumable definitions from JSON."""
        self.consumables_db = {}  # consumable_id -> consumable_data dict
        self._load_consumables()
    
    def _load_consumables(self):
        """Load all consumable types from data/consumables/consumable_types.json."""
        consumables_path = Path(__file__).parent.parent / "data" / "consumables" / "consumable_types.json"
        
        try:
            with open(consumables_path, 'r') as f:
                data = json.load(f)
            
            # Flatten all categories (health_potions, mana_potions, elixirs, food)
            for category in data.values():
                if isinstance(category, list):
                    for consumable_def in category:
                        self.consumables_db[consumable_def["consumable_id"]] = consumable_def
        except FileNotFoundError:
            print(f"WARNING: Consumable types file not found at {consumables_path}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse consumable types JSON: {e}")
    
    def has_consumable(self, consumable_id):
        """True if this id is a known consumable.

        Lets a caller that accepts SEVERAL item kinds (the vendor screen
        resolves a sell-list id as either a consumable or a crafting
        material) test membership without going through get_consumable,
        which logs a WARNING for an unknown id. That warning is right for a
        genuine typo but wrong for an ordinary "is it this kind?" probe - it
        was printing ~190 false warnings on every vendor open, one per
        reagent, which buries the real warnings it exists to surface.
        """
        return consumable_id in self.consumables_db

    def get_consumable(self, consumable_id, quantity=1):
        """
        Create a new Consumable instance from a definition.
        Returns a Consumable with the specified quantity.
        """
        if consumable_id not in self.consumables_db:
            print(f"WARNING: Unknown consumable_id: {consumable_id}")
            return None
        
        data = self.consumables_db[consumable_id]
        c = Consumable(
            data["consumable_id"],
            data["name"],
            data["consumable_type"],
            data["description"],
            data["effect_value"],
            data["effect_duration"],
            data["level_multiplier"],
            data["required_level"],
            data["cooldown_seconds"],
            data["stack_limit"],
            data["vendor_price"],
            data["sell_price"],
            data.get("buff_category"),
            data.get("stat_bonuses"),
        )
        c.quantity = min(quantity, data["stack_limit"])
        return c
    
    def get_all_consumable_ids(self):
        """Return list of all available consumable IDs."""
        return list(self.consumables_db.keys())
    
    def get_consumables_by_category(self, consumable_type):
        """Return all consumables of a specific type (health_potion, mana_potion, elixir, food)."""
        return [c for c in self.consumables_db.values() if c["consumable_type"] == consumable_type]


# Global singleton instance
_consumable_manager = None

def get_consumable_manager():
    """Get or create the global ConsumableManager instance."""
    global _consumable_manager
    if _consumable_manager is None:
        _consumable_manager = ConsumableManager()
    return _consumable_manager
