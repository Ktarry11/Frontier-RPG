"""
Versioned save/load system. Ensures saves survive feature additions across phases.

A save is a single JSON document:

    {
      "version": 7,
      "character": {...},          # the player
      "party":     {...},          # companions, bench, rows
      "recruits":  {...},          # which recruit NPCs have been taken
      "world":     {...},          # zone name + tile the player is standing on
      "quests":    {...},          # quest progress
      "travel":    {...},          # hearth bind/cooldown, flight nodes, riding + mounts (v7)
      "factions":  {...}           # reputation standing per faction (v9)
    }

Every block except "character" is optional, so a v4/v5 save still loads; the
missing pieces simply fall back to their defaults (empty party, everyone
un-recruited, start of Valley of Trials).
"""
import json
from pathlib import Path
from config import SAVE_VERSION


class SaveSystem:
    """Handles character save/load with versioning."""

    def __init__(self):
        self.save_dir = Path(__file__).parent.parent / "data" / "saves"
        self.save_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def save_character(self, character, filename="character.json",
                       party=None, recruit_manager=None, zone_manager=None,
                       quest_manager=None, travel_manager=None, faction_manager=None):
        """
        Write a full save.

        `party`, `recruit_manager`, `zone_manager`, and `quest_manager`
        are all optional so any older call site still works, but a save
        written without them is lossy: no companions, every recruit
        respawned, the player dropped back at the Valley of Trials start
        tile on load, and - the gap Kyle found live - every quest's
        progress silently reset to not-started on reload, since nothing
        was ever writing it out at all.
        """
        save_data = {
            "version": SAVE_VERSION,
            "character": character.to_dict(),
        }
        if party is not None:
            save_data["party"] = party.to_dict()
        if recruit_manager is not None:
            save_data["recruits"] = recruit_manager.to_dict()
        if zone_manager is not None:
            save_data["world"] = self._world_state(zone_manager)
        if quest_manager is not None:
            save_data["quests"] = quest_manager.to_dict()
        if travel_manager is not None:
            save_data["travel"] = travel_manager.to_dict()
        if faction_manager is not None:
            save_data["factions"] = faction_manager.to_dict()

        save_path = self.save_dir / filename
        with open(save_path, "w") as f:
            json.dump(save_data, f, indent=2)

        return save_path

    @staticmethod
    def _world_state(zone_manager):
        """
        Where the player is standing.

        Only the zone NAME and tile are stored - never the tilemap itself.
        Zones are procedurally regenerated identically on startup, so storing
        them would bloat the save by megabytes and, worse, would pin old
        saves to an outdated terrain layout.
        """
        zone = getattr(zone_manager, "current_zone", None)
        if zone is None:
            return None
        return {
            "zone": zone.name,
            "x": zone_manager.player_x,
            "y": zone_manager.player_y,
        }

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def load_character(self, filename="character.json"):
        """Load just the player's character block from a save."""
        save_data = self.load_full_save(filename)
        if save_data is None:
            return None
        return save_data.get("character")

    def load_full_save(self, filename="character.json"):
        """
        Load the whole save payload (character + party + recruits + world).

        Returns the raw dict, or None if the file is absent or unreadable. A
        corrupt save returns None rather than raising, so a bad file can't
        take the whole game down at the main menu.
        """
        save_path = self.save_dir / filename
        if not save_path.exists():
            return None
        try:
            with open(save_path, "r") as f:
                save_data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Could not read save '{filename}': {exc}")
            return None

        version = save_data.get("version", 1)
        if version > SAVE_VERSION:
            print(f"Warning: save version {version} is NEWER than this build "
                  f"({SAVE_VERSION}); some data may be ignored.")
        elif version < SAVE_VERSION:
            print(f"Note: upgrading save from version {version} to {SAVE_VERSION}.")

        return save_data

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def has_save(self, filename="character.json"):
        """True if a save file exists (used to grey out the Load button)."""
        return (self.save_dir / filename).exists()

    def describe_save(self, filename="character.json"):
        """
        Short one-line summary for the menu ("Kyle - Level 12 Warrior"), or
        None when there's nothing to load.
        """
        data = self.load_full_save(filename)
        if not data:
            return None
        char = data.get("character") or {}
        name = char.get("name", "Unknown")
        level = char.get("level", 1)
        char_class = char.get("class", "?")
        party = data.get("party") or {}
        companions = len(party.get("members", [])) + len(party.get("bench", []))
        summary = f"{name} - Level {level} {char_class}"
        if companions:
            summary += f" (+{companions})"
        return summary

    def get_save_files(self):
        """Return list of available save files."""
        if not self.save_dir.exists():
            return []
        return [f.stem for f in self.save_dir.glob("*.json")]
