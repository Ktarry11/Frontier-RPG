"""
Ambient NPC manager - lightweight flavor NPCs that populate towns and
cities without the overhead of a full VendorNPC (shop inventory, gear
stock rolling) or RecruitNPC (a real Character, gear themes, background
sections). Kyle's ask: "cities and towns ACTUALLY populated" - a capital
with 2 vendors and nothing else reads empty regardless of how good those
2 vendors are. These are the "everyone else": guards, citizens, someone
standing by the forge - bodies that make a place feel lived-in.

An ambient NPC has just enough to stand somewhere, look like something
(via the same race_registry sprite system every other NPC uses), and
optionally say one line when interacted with. No shop, no recruitment,
no combat. Mirrors VendorManager/RecruitManager's load-and-index-by-zone
shape so ZoneManager's lookup pattern stays consistent across all three
NPC types.
"""
import json
from pathlib import Path


class AmbientNPC:
    """A non-interactive-or-lightly-interactive flavor NPC - a guard, a
    townsperson, a blacksmith standing at their forge. No inventory, no
    recruitment, no combat stats."""

    def __init__(self, data):
        self.npc_id = data["npc_id"]
        self.name = data["name"]
        self.zone = data["zone"]
        self.x = data["x"]
        self.y = data["y"]
        self.greeting = data.get("greeting", "")

        # Appearance - defaults to the zone's default race the same way
        # VendorNPC does, so a plain {"npc_id":..., "name":..., "zone":...,
        # "x":..., "y":...} entry with nothing else still renders as a
        # sensible race for wherever it's placed.
        from world.race_registry import get_zone_default_race
        self.race = data.get("race") or get_zone_default_race(self.zone)
        self.gender = data.get("gender", "male")
        self.appearance_variant = data.get("appearance_variant", 0)
        self.facing = data.get("facing", "down")
        # Class trainer (data/training/trainers.json lists the same ids): every town defines a trainer for ALL 18 classes on one
        # shared tile, but only the one for the player's own class is shown - see AmbientNPCManager.set_viewer_class.
        self.trains_class = data.get("trains_class")
        self.trains_profession = data.get("trains_profession")


class AmbientNPCManager:
    """Loads and indexes ambient NPCs from data/npcs/ambient_npcs.json,
    same zone-indexing shape as VendorManager/RecruitManager."""

    def __init__(self):
        self.npcs = {}              # npc_id -> AmbientNPC
        self.npcs_by_zone = {}      # normalized zone key -> list of AmbientNPC
        self._load_npcs()

    def _load_npcs(self):
        npcs_path = Path(__file__).parent.parent / "data" / "npcs" / "ambient_npcs.json"
        try:
            with open(npcs_path, 'r') as f:
                data = json.load(f)

            for npc_def in data.get("npcs", []):
                npc = AmbientNPC(npc_def)
                self.npcs[npc.npc_id] = npc

                key = self._zone_key(npc.zone)
                if key not in self.npcs_by_zone:
                    self.npcs_by_zone[key] = []
                self.npcs_by_zone[key].append(npc)

        except FileNotFoundError:
            # No ambient NPCs authored yet is a valid, quiet state (not
            # every zone needs them, and the file may not exist at all
            # until the first batch is added) - degrade to "none loaded"
            # rather than crashing zone load.
            pass
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse ambient NPC JSON: {e}")

    @staticmethod
    def _zone_key(zone):
        """Same normalization VendorManager._zone_key uses - lowercase,
        spaces to underscores - so this file can use either the Tilemap
        display name or the slug form interchangeably."""
        return zone.lower().replace(" ", "_")

    def set_viewer_class(self, char_class):
        """The player's class: class trainers for any OTHER class are hidden (18 trainers per town would bury the plaza)."""
        self.viewer_class = char_class

    def get_npcs_in_zone(self, zone):
        """All ambient NPCs in a zone (accepts display name or slug). Trainers of other classes are not listed."""
        npcs = self.npcs_by_zone.get(self._zone_key(zone), [])
        viewer = getattr(self, "viewer_class", None)
        return [n for n in npcs if not n.trains_class or n.trains_class == viewer]

    def get_npc_at_location(self, zone, x, y):
        """Ambient NPC at a specific tile, if any."""
        for npc in self.get_npcs_in_zone(zone):
            if npc.x == x and npc.y == y:
                return npc
        return None

    def all_world_positions(self):
        """Every (zone, x, y) an ambient NPC stands on - mirrors
        RecruitManager.all_world_positions() so ZoneManager can carve
        landings for ambient NPCs the same way it already does for
        recruits. Added because ambient NPC tiles were never carved at
        all before this - get_npc_at_location works on pure coordinate
        match regardless of terrain, so a hand-placed ambient NPC that
        happened to land on a rock/wall/water tile from terrain scatter
        would be permanently unreachable (same failure mode the vendor
        system hit before recruit/vendor carving existed)."""
        return [(npc.zone, npc.x, npc.y) for npc in self.npcs.values()]


_ambient_npc_manager = None


def get_ambient_npc_manager():
    """Module-level singleton, same access pattern as
    world.recruit_manager.get_recruit_manager()."""
    global _ambient_npc_manager
    if _ambient_npc_manager is None:
        _ambient_npc_manager = AmbientNPCManager()
    return _ambient_npc_manager
