"""
Where a new character begins.

Kyle, 2026-10-28: "Make starting in undead zone an option."

Built as a registry for the same reason race_registry is one: the thing being added is DATA, and the
second entry should not require touching ZoneManager, the creation screen's click handling, or the save
format. Adding a third start - Echo Isles for a troll, Mulgore if it ever stops being a level 60
nightmare - is an entry below and nothing else.

WHY THIS IS NOT KEYED TO RACE. It would be tidy to say forsaken start in Deathknell and everyone else
starts in the Valley, and it would be wrong for this game. Kyle's standing ruling is that there is no
true Horde/Alliance here, and the premise is that players are Earth transplants who arrived in a world
that was already mid-catastrophe - nobody was BORN into these starting zones, they woke up in one. So
race SUGGESTS a start (`suggested_for`) and never locks it, and the creation screen pre-selects on race
change while leaving every option clickable.

THE COORDINATES ARE THE CONTRACT. Each start must be a walkable tile within sight of the zone's level-1
quest giver, or a new character stands in an empty field with nothing to do. Both entries below are
verified against the generated map by tools/qa_start_zones.py, which also checks that the zone actually
has level-1 quests in it - a start zone whose lowest quest is level 6 is a worse bug than a start zone
that crashes, because it only shows up as a player wandering.
"""
from dataclasses import dataclass, field


@dataclass
class StartZone:
    start_id: str
    label: str              # the button in character creation
    zone_name: str          # must match a key in ZoneManager.zones exactly
    x: int
    y: int
    blurb: str              # one line under the buttons, so the choice means something before you take it
    suggested_for: list = field(default_factory=list)   # race_ids this pre-selects for
    available: bool = True


START_ZONES = [
    StartZone(
        start_id="valley_of_trials",
        label="Valley of Trials",
        zone_name="Valley of Trials",
        x=60, y=40,                      # the original hardcoded start, unchanged
        blurb="Durotar. Hot, orderly, and full of people who will give you a job.",
        suggested_for=["orc", "tauren", "troll", "goblin"],
    ),
    StartZone(
        start_id="deathknell",
        label="Deathknell",
        zone_name="Deathknell",
        # Four tiles below dk_quest_overseer at (50, 38), who gives dk_first_steps at level 1 - the
        # Deathknell equivalent of the Valley's greeter. Verified walkable on the generated map.
        x=50, y=42,
        blurb="Tirisfal. You wake in a graveyard with your mind intact, which is the whole problem.",
        suggested_for=["forsaken"],
    ),
]

#: What ZoneManager falls back to with no character or no stored choice. Keeping the Valley as the
#: default means every existing save, and every code path that never passes a start id, behaves exactly
#: as it did before this module existed.
DEFAULT_START_ID = "valley_of_trials"


def get_available_starts():
    return [s for s in START_ZONES if s.available]


def get_start(start_id):
    """The StartZone for an id, falling back to the default rather than returning None.

    A bad id here would otherwise strand a character in no zone at all, and the id can come out of a
    save file written by an older build. Falling back is the safe failure.
    """
    for s in START_ZONES:
        if s.start_id == start_id:
            return s
    return get_start(DEFAULT_START_ID) if start_id != DEFAULT_START_ID else START_ZONES[0]


def suggested_start_for_race(race_id):
    """The start a race pre-selects to. Never a restriction - see the module docstring."""
    for s in get_available_starts():
        if race_id in s.suggested_for:
            return s.start_id
    return DEFAULT_START_ID
