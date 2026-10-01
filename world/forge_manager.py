"""
Forge - a fixed world-object interaction point where Smelting can be
performed. Real WoW convention (confirmed via web search, 2026-09-12):
"Smelting can only be done at a Forge." Mirrors VendorManager's shape
almost exactly (fixed JSON-authored positions, indexed by zone,
get_X_at_location lookup) since a Forge is really just a vendor-shaped
object with no sprite variants, faction, or dialogue - simpler, not a
different pattern.
"""
import json
from pathlib import Path


class Forge:
    def __init__(self, forge_id, name, zone, x, y):
        self.forge_id = forge_id
        self.name = name
        self.zone = zone
        self.x = x
        self.y = y


class ForgeManager:
    def __init__(self):
        self.forges = {}  # forge_id -> Forge
        self.forges_by_zone = {}  # normalized zone key -> list of Forge
        self._load_forges()

    def _load_forges(self):
        forges_path = Path(__file__).parent.parent / "data" / "npcs" / "forges.json"
        try:
            with open(forges_path, 'r') as f:
                data = json.load(f)
            for forge_def in data.get("forges", []):
                forge = Forge(
                    forge_def["forge_id"],
                    forge_def["name"],
                    forge_def["zone"],
                    forge_def["x"],
                    forge_def["y"],
                )
                self.forges[forge.forge_id] = forge
                key = self._zone_key(forge.zone)
                self.forges_by_zone.setdefault(key, []).append(forge)
        except FileNotFoundError:
            print(f"WARNING: Forge file not found at {forges_path}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse forge JSON: {e}")

    @staticmethod
    def _zone_key(zone):
        """Same normalization as every other zone-keyed lookup in this
        codebase (VendorManager._zone_key, GatheringNodeManager._zone_key,
        race_registry, quest zone_key)."""
        return str(zone).strip().lower().replace(" ", "_").replace("'", "")

    def get_forges_in_zone(self, zone):
        return self.forges_by_zone.get(self._zone_key(zone), [])

    def get_forge_at_location(self, zone, x, y):
        for forge in self.get_forges_in_zone(zone):
            if forge.x == x and forge.y == y:
                return forge
        return None


_forge_manager = None


def get_forge_manager():
    global _forge_manager
    if _forge_manager is None:
        _forge_manager = ForgeManager()
    return _forge_manager
