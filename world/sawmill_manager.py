"""
Sawmill - a fixed world object where logs are sawn into planks (Woodcutting's counterpart to the Forge, Oct 2026).

Exactly the Forge's shape (data/npcs/sawmills.json, reach in tiles, nearest-wins lookup): the Sawmill recipes live in
data/crafting/recipes.json under "woodcutting" and are crafted from the Professions screen's Sawmill tab.
"""
from world.forge_manager import ForgeManager


class SawmillManager(ForgeManager):
    DATA_FILE = "sawmills.json"
    LIST_KEY = "sawmills"
    ID_KEY = "sawmill_id"


_sawmill_manager = None


def get_sawmill_manager():
    global _sawmill_manager
    if _sawmill_manager is None:
        _sawmill_manager = SawmillManager()
    return _sawmill_manager
