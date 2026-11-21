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
    #: what the wipe message calls the camp, when a party wakes there (ZoneManager.respawn_point)
    camp: str = ""
    #: the start's card in character creation (Kyle, 21 Nov 2026: "a more prominent 'Starting zone' thing you click on
    #: to pick it. It has actual lore about the location and an image too"): where it is, its levels, a paragraph of
    #: lore, and its painting (docs/start_zone_art_prompts.md; a painted stand-in until the art lands)
    region: str = ""
    levels: str = ""
    lore: str = ""
    art: str = ""
    #: a start that isn't built yet still gets a card, shown locked, with this instead of a level range
    locked_note: str = ""


START_ZONES = [
    StartZone(
        start_id="valley_of_trials",
        label="Valley of Trials",
        zone_name="Valley of Trials",
        x=60, y=40,                      # the original hardcoded start, unchanged
        blurb="Durotar. Hot, orderly, and full of people who will give you a job.",
        suggested_for=["orc", "tauren", "troll"],          # never goblins (Kyle: not a playable race, ever)
        camp="the Valley camp",
        region="Durotar, Kalimdor",
        levels="Levels 1 to 10",
        lore=("The orcs have tested their young in this red valley for as long as there's been an Orgrimmar, and when "
              "the worlds came together it's where the first strangers started waking up among the cactus and the "
              "boars. The Horde never asked where any of them came from. It asked whether they'd work. Prove yourself "
              "in the Valley, and Razor Hill, the Barrens and the gates of Orgrimmar open up beyond it."),
        art="assets/ui/start_zones/valley_of_trials.png",
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
        camp="the graves at Deathknell",
        region="Tirisfal Glades, the Eastern Kingdoms",
        levels="Levels 1 to 10",
        lore=("The Forsaken raise their dead in Deathknell's graveyard, under a sky that never quite clears, and some of "
              "the bodies that climb out of its earth were never from this world at all. You wake in a grave with your "
              "mind intact, which is the whole problem. The Forsaken will put you to work all the same, and the road "
              "runs on through the plague fields to Brill and the Undercity."),
        art="assets/ui/start_zones/deathknell.png",
    ),
    StartZone(
        start_id="dawnhaven",
        label="Dawnhaven",
        zone_name="Amberleaf Glade",
        # the Waking Shore, two tiles from Ranger-Captain Saelis Dawnbrook (78,108), who gives the first quest
        # (docs/dawnhaven_brief.md, 21 Nov 2026)
        x=75, y=110,
        blurb="An island off Azshara. You wake on a gold shore, and the elves who found you are building a home.",
        suggested_for=["blood_elf"],
        camp="Amberwatch",
        region="Off the coast of Azshara, Kalimdor",
        levels="Levels 1 to 9",
        lore=("When the sea rose over the last of Quel'Thalas, the Sunreach Conclave sailed south and found an island "
              "no map had shown for a thousand years: an old high elf outpost hidden behind wardstones, its spire dark "
              "and its people long dead. They took it back and called it Dawnhaven. The sea keeps giving up strangers "
              "on its gold shore, and the Conclave takes in every one. Help them make it a home, then take the "
              "Spire's boat to Durotar."),
        art="assets/ui/start_zones/dawnhaven.png",
    ),
    StartZone(
        start_id="white_expanse",
        label="The White Expanse",
        zone_name="The White Expanse",
        x=0, y=0,                        # not built: the Aetherian start zone (docs/worldtree_brief.md) is parked
        blurb="Caelora, above the clouds. The sky-folk found you, and they haven't decided what you are yet.",
        suggested_for=["aetherian"],
        available=False,
        region="Caelora, above the World Tree",
        levels="",
        lore=("Far above the World Tree, the Aetherians' cities float on a sea of cloud, and for a thousand years they "
              "never once looked down. Then the tree grew tall enough to touch their sky, and the first people from "
              "the ground came climbing up it. You wake on the White Expanse, a cold shelf of cloud and stone at "
              "Caelora's edge, where the Aetherians keep the Earthborn they find. First contact is still happening, "
              "and nobody up here is sure yet whether it's going well."),
        art="assets/ui/start_zones/white_expanse.png",
        locked_note="Opens with the Aetherian start zone",
    ),
]

#: What ZoneManager falls back to with no character or no stored choice. Keeping the Valley as the
#: default means every existing save, and every code path that never passes a start id, behaves exactly
#: as it did before this module existed.
DEFAULT_START_ID = "valley_of_trials"


def get_available_starts():
    return [s for s in START_ZONES if s.available]


def get_start_cards():
    """Every start, built or not, in order: the creator shows a card for each and locks the ones not built yet."""
    return list(START_ZONES)


def get_start(start_id):
    """The StartZone for an id, falling back to the default rather than returning None.

    A bad id here would otherwise strand a character in no zone at all, and the id can come out of a
    save file written by an older build. Falling back is the safe failure.
    """
    for s in START_ZONES:
        if s.start_id == start_id and s.available:
            return s
    return get_start(DEFAULT_START_ID) if start_id != DEFAULT_START_ID else START_ZONES[0]


def suggested_start_for_race(race_id):
    """The start a race pre-selects to. Never a restriction - see the module docstring."""
    for s in get_available_starts():
        if race_id in s.suggested_for:
            return s.start_id
    return DEFAULT_START_ID
