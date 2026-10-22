"""
Race/appearance registry - maps a playable race + gender to the pool of
sprite variant folders under assets/npcs/, and back out to the actual
per-direction frame files.

Deliberately separate from Character itself: Character just stores
race/gender/variant as plain strings/ints, this module is the only place
that knows how those map to real files on disk. That split means adding a
new race later (say, Tauren or Troll once art exists) is purely additive
here - a new RACE_OPTIONS entry - and never touches Character, the
creation screen's rendering loop, or the sprite loader.

Kyle's ask: "Human, Orc, plus placeholder slots for more races later" and
"race + gender + [variant] options which we can expand later" - so this
is built as a real registry from the start, not two hardcoded strings.
"""
from dataclasses import dataclass, field


@dataclass
class GenderOption:
    """One gender's sprite pool for a race - a list of variant folder
    names under assets/npcs/<race>/<gender_dir>/. variant_count is
    derived from this list's length, not hardcoded, so re-running the
    crop pipeline with more source sheets just needs this list extended."""
    gender_id: str          # "male" / "female" / "unisex"
    label: str               # display label in the creation UI
    sprite_dir: str          # subfolder under assets/npcs/<race_folder>/
    variants: list = field(default_factory=list)  # folder names, e.g. ["male_1", "maleA_3"]


@dataclass
class RaceOption:
    """One playable race - its display name, folder on disk, and the
    genders it offers. `available` gates whether it's selectable yet
    (placeholder races can exist here with available=False and simply
    won't render as a button, rather than needing a separate "coming
    soon" list maintained in parallel)."""
    race_id: str
    label: str
    race_folder: str         # subfolder under assets/npcs/
    genders: list            # list of GenderOption
    available: bool = True


# Real, on-disk variant folders - built from the AI-generated contact-sheet
# pack (10 sheets, cropped + individually verified for clean alpha/no
# label-ghost artifacts - see the session that ran that crop pipeline).
# All variants currently ship as a single front-facing pose duplicated
# across down/left/right/up.png (Kyle's explicit call: ship front-only
# now, a real per-direction walk-cycle pass is separate future work -
# get_npc_sprite()'s height-anchored scaling doesn't care that all four
# files are identical, it'll just always show the front pose).
_HUMAN_MALE_VARIANTS = [f"male_{i}" for i in range(1, 15)]
_HUMAN_FEMALE_VARIANTS = [f"female_{i}" for i in range(1, 15)]
_ORC_VARIANTS = [f"orc_{i}" for i in range(1, 23)]

# Goblin variants (Durotar has real WoW goblin presence - Ratchet, trade
# outposts). 24 variants (12 male + 12 female) from the AI-generated
# goblin contact sheet.
_GOBLIN_VARIANTS = [f"goblin_{i}" for i in range(1, 25)]

# Blood Elf - Horde-aligned in real WoW (since TBC), fits the current
# all-Horde zone roster with no lore justification needed.
_BLOOD_ELF_VARIANTS = [f"blood_elf_{i}" for i in range(1, 12)]

# Night Elf - Alliance-only in real WoW. Kept in the registry now so the
# art is ready, but not placed in any zone yet since every zone built so
# far is Horde/Forsaken - Night Elves belong in Alliance territory
# (Ashenvale, Darnassus) that doesn't exist as playable content yet.
# Kyle's call: build both now, hold Night Elf in reserve for when
# Alliance zones land.
_NIGHT_ELF_VARIANTS = [f"night_elf_{i}" for i in range(1, 12)]

# Troll - 20 variants (Male/Female mix) from the AI-generated troll
# contact sheet, replacing the old 6-variant WC2-recolor rough stand-in.
_TROLL_VARIANTS = [f"troll_{i}" for i in range(1, 21)]

# Forsaken - replaces Skeleton AND Zombie entirely as the Undead-flavor
# race (Kyle's call: "forsaken are currently garbage zombies and
# skeletons" - one real, well-drawn undead race beats two rough salvage
# jobs coexisting). 16 variants (8 male + 8 female) from the
# AI-generated forsaken contact sheet - genuine WoW-style gaunt/decayed
# Undead, not a reused human palette-swap.
_FORSAKEN_VARIANTS = [f"forsaken_{i}" for i in range(1, 17)]

# Tauren - new race, no prior art existed (zone comments in
# ZONE_POPULATION_MIX previously noted "tauren in real WoW, no tauren
# art yet" at camp_taurajo - this closes that gap). 20 variants from the
# AI-generated tauren contact sheet. NPC-only for now (available=False)
# per Kyle's call - flip on when ready for player-facing use.
_TAUREN_VARIANTS = [f"tauren_{i}" for i in range(1, 21)]

# Dwarf and Gnome - new races, no prior art existed. Both come from one
# combined contact sheet (dwarf rows + gnome rows) but are split into
# separate races/folders since they're distinct playable races in WoW,
# not a unisex pool like orc/goblin. 12 variants each. NPC-only for now
# (available=False) per Kyle's call.
_DWARF_VARIANTS = [f"dwarf_{i}" for i in range(1, 13)]
_GNOME_VARIANTS = [f"gnome_{i}" for i in range(1, 13)]


RACE_OPTIONS = [
    RaceOption(
        race_id="human",
        label="Human",
        race_folder="human",
        genders=[
            GenderOption("male", "Male", "male", _HUMAN_MALE_VARIANTS),
            GenderOption("female", "Female", "female", _HUMAN_FEMALE_VARIANTS),
        ],
    ),
    RaceOption(
        race_id="orc",
        label="Orc",
        race_folder="orc",
        genders=[
            # The source art doesn't visually distinguish orc genders (see
            # session notes - all variants read as unisex at this pixel
            # scale), so both gender picks share the same variant pool
            # rather than faking a split with no real art difference.
            GenderOption("male", "Male", "", _ORC_VARIANTS),
            GenderOption("female", "Female", "", _ORC_VARIANTS),
        ],
    ),
    RaceOption(
        race_id="goblin",
        label="Goblin",
        race_folder="goblin",
        genders=[
            GenderOption("male", "Male", "", _GOBLIN_VARIANTS),
            GenderOption("female", "Female", "", _GOBLIN_VARIANTS),
        ],
        # NPC-only for now (Kyle's ask was goblin NPCs in Durotar, not a
        # player-creation option) - full art support exists if this
        # changes later, just flip available=True.
        available=False,
    ),
    RaceOption(
        race_id="blood_elf",
        label="Blood Elf",
        race_folder="blood_elf",
        genders=[
            # Source art doesn't split by gender - same unisex-pool
            # pattern as orc/goblin.
            GenderOption("male", "Male", "", _BLOOD_ELF_VARIANTS),
            GenderOption("female", "Female", "", _BLOOD_ELF_VARIANTS),
        ],
        # Horde-aligned, fits current zone roster - NPC-only for now
        # (no Blood Elf zones/quest content authored yet), flip
        # available=True whenever player-facing use makes sense.
        available=False,
    ),
    RaceOption(
        race_id="night_elf",
        label="Night Elf",
        race_folder="night_elf",
        genders=[
            GenderOption("male", "Male", "", _NIGHT_ELF_VARIANTS),
            GenderOption("female", "Female", "", _NIGHT_ELF_VARIANTS),
        ],
        # Alliance-only - held in reserve until Alliance zones exist (see
        # _NIGHT_ELF_VARIANTS docstring). Resolvable via get_race() for
        # testing/preview purposes, just not placed in any real zone or
        # offered at character creation yet.
        available=False,
    ),
    RaceOption(
        race_id="troll",
        label="Troll",
        race_folder="troll",
        genders=[
            # Source art splits Male Troll / Female Troll sections on the
            # sheet, but reads unisex-safe at this pixel scale like the
            # other races here - shared pool rather than a forced split.
            GenderOption("male", "Male", "", _TROLL_VARIANTS),
            GenderOption("female", "Female", "", _TROLL_VARIANTS),
        ],
        # NPC-only (Kyle's ask was troll NPCs for Durotar-region flavor,
        # not a player-creation option). Real AI-generated art now (see
        # _TROLL_VARIANTS), replacing the old WC2-recolor rough
        # stand-in - flip available=True later if this should become a
        # playable race.
        available=False,
    ),
    RaceOption(
        race_id="forsaken",
        label="Forsaken",
        race_folder="forsaken",
        genders=[
            GenderOption("male", "Male", "", _FORSAKEN_VARIANTS),
            GenderOption("female", "Female", "", _FORSAKEN_VARIANTS),
        ],
        # Replaces Skeleton + Zombie entirely as the Undead-flavor race
        # (Kyle's call - see _FORSAKEN_VARIANTS docstring). Available
        # immediately since it's taking over a role two already-available
        # races previously filled; Kyle's "no true Horde/Alliance" ruling
        # means Undead-flavor races aren't zone-locked either.
        available=True,
    ),
    RaceOption(
        race_id="tauren",
        label="Tauren",
        race_folder="tauren",
        genders=[
            GenderOption("male", "Male", "", _TAUREN_VARIANTS),
            GenderOption("female", "Female", "", _TAUREN_VARIANTS),
        ],
        # New race, no prior art (see _TAUREN_VARIANTS docstring).
        # NPC-only for now per Kyle's call - flip available=True later.
        available=False,
    ),
    RaceOption(
        race_id="dwarf",
        label="Dwarf",
        race_folder="dwarf",
        genders=[
            GenderOption("male", "Male", "", _DWARF_VARIANTS),
            GenderOption("female", "Female", "", _DWARF_VARIANTS),
        ],
        # New race, no prior art. NPC-only for now per Kyle's call.
        available=False,
    ),
    RaceOption(
        race_id="gnome",
        label="Gnome",
        race_folder="gnome",
        genders=[
            GenderOption("male", "Male", "", _GNOME_VARIANTS),
            GenderOption("female", "Female", "", _GNOME_VARIANTS),
        ],
        # New race, no prior art. NPC-only for now per Kyle's call.
        available=False,
    ),
]


def get_race(race_id):
    """RaceOption for a race_id, or None if unknown."""
    for race in RACE_OPTIONS:
        if race.race_id == race_id:
            return race
    return None


def get_available_races():
    """Races actually selectable at character creation right now."""
    return [r for r in RACE_OPTIONS if r.available]


def get_gender(race_id, gender_id):
    """GenderOption for a race+gender pair, or None if either is unknown."""
    race = get_race(race_id)
    if race is None:
        return None
    for gender in race.genders:
        if gender.gender_id == gender_id:
            return gender
    return None


def get_variant_folder(race_id, gender_id, variant_index):
    """The on-disk folder name for one specific appearance pick, e.g.
    ("human", "male", 2) -> "male_3". Clamps variant_index into range
    rather than raising, so a stale save with an out-of-range index (say,
    the variant pool shrank) degrades to the last valid variant instead
    of crashing character load."""
    gender = get_gender(race_id, gender_id)
    if gender is None or not gender.variants:
        return None
    index = max(0, min(variant_index, len(gender.variants) - 1))
    return gender.variants[index]


def sprite_base_path(race_id, gender_id, variant_index):
    """Full relative path (from project root) to the folder containing
    this appearance's down/left/right/up.png frames."""
    race = get_race(race_id)
    variant_folder = get_variant_folder(race_id, gender_id, variant_index)
    if race is None or variant_folder is None:
        return None
    gender = get_gender(race_id, gender_id)
    # Orc variants sit directly under assets/npcs/orc/<variant>/ (no
    # gender subfolder, since orc genders share one pool - see
    # _ORC_VARIANTS above); human variants sit under
    # assets/npcs/human/<male|female>/<variant>/.
    if gender.sprite_dir:
        return f"assets/npcs/{race.race_folder}/{gender.sprite_dir}/{variant_folder}"
    return f"assets/npcs/{race.race_folder}/{variant_folder}"


# Zone -> population mix for environmental/vendor NPCs (not recruits,
# which are always human companions regardless of zone - see Kyle's
# explicit call on that). Each zone maps to a list of (race_id, weight)
# pairs rather than one single race - Kyle's ruling: "there is no 'true'
# Alliance and Horde... Undercity is 90% undead but some orcs and high
# elves. Durotar is mostly orc, goblin, troll. But some undead, blood
# elves and even 'alliance' races." A single dominant-race-per-zone model
# can't express that, so this is a real weighted mix per zone - the
# dominant race gets most of the weight, minorities get a real but small
# slice. Weights don't need to sum to any particular total; they're
# relative to each other within a zone.
#
# Keyed the same slug form VendorManager._zone_key normalizes to
# (lowercase, underscored) so this can be looked up with whatever zone
# string a caller already has, display name or slug.
ZONE_POPULATION_MIX = {
    "valley_of_trials": [("orc", 85), ("goblin", 10), ("forsaken", 5)],
    "durotar": [("orc", 75), ("goblin", 10), ("forsaken", 5), ("blood_elf", 5), ("human", 5)],
    "razor_hill": [("orc", 80), ("goblin", 10), ("blood_elf", 5), ("human", 5)],
    "echo_isles": [("orc", 75), ("troll", 15), ("goblin", 5), ("forsaken", 5)],  # trolls now have real art - see _TROLL_VARIANTS
    "northern_barrens": [("orc", 80), ("goblin", 10), ("forsaken", 5), ("human", 5)],
    "central_barrens": [("orc", 80), ("goblin", 10), ("forsaken", 5), ("human", 5)],
    "southern_barrens": [("orc", 80), ("goblin", 10), ("forsaken", 5), ("human", 5)],
    "crossroads": [("orc", 70), ("goblin", 15), ("human", 10), ("blood_elf", 5)],
    "camp_taurajo": [("tauren", 70), ("orc", 15), ("goblin", 5), ("forsaken", 5), ("human", 5)],  # tauren now have real art - see _TAUREN_VARIANTS
    "orgrimmar": [("orc", 70), ("goblin", 15), ("blood_elf", 8), ("human", 5), ("forsaken", 2)],
    "ragefire_chasm": [("orc", 60), ("forsaken", 40)],
    "burning_blade_coven": [("orc", 50), ("forsaken", 50)],
    "ratchet": [("goblin", 75), ("orc", 15), ("human", 10)],
    "zeppelin_tower": [("goblin", 80), ("orc", 20)],
    "undercity_zeppelin_tower": [("goblin", 60), ("forsaken", 30), ("orc", 10)],
    "undercity": [("forsaken", 90), ("orc", 5), ("blood_elf", 5)],
    "eastern_tirisfal": [("forsaken", 90), ("orc", 5), ("blood_elf", 5)],
    "western_tirisfal": [("forsaken", 90), ("orc", 5), ("blood_elf", 5)],
    "brill": [("forsaken", 80), ("human", 10), ("orc", 5), ("blood_elf", 5)],
    "deathknell": [("forsaken", 95), ("blood_elf", 5)],
    "silverpine_north": [("forsaken", 85), ("human", 10), ("orc", 5)],
    "silverpine_south": [("forsaken", 85), ("human", 10), ("orc", 5)],
}


def get_zone_default_race(zone_key):
    """Single most-likely race for a zone - the dominant entry in
    get_zone_population_mix. Kept as the simple default for any caller
    that just wants one sensible race (e.g. a hand-placed NPC that didn't
    specify race explicitly) without dealing with weighted picks."""
    mix = get_zone_population_mix(zone_key)
    if not mix:
        return "human"
    return max(mix, key=lambda pair: pair[1])[0]


def get_zone_population_mix(zone_key):
    """The full (race_id, weight) list for a zone, or [] if unmapped.
    Normalized the same way VendorManager._zone_key does (lowercase,
    spaces->underscores) so callers can pass either the Tilemap display
    name or the slug."""
    normalized = zone_key.lower().replace(" ", "_").replace("'", "")
    return ZONE_POPULATION_MIX.get(normalized, [])


def pick_random_race_for_zone(zone_key, rng=None):
    """Weighted-random race pick for a zone, honoring the real population
    mix (e.g. an Undercity NPC is likely skeleton/zombie but has a real,
    small chance of being orc or blood_elf). Falls back to "human" for
    any zone with no mix defined, same as get_zone_default_race.

    rng: optional random.Random instance for deterministic testing;
    defaults to the module-level random functions.
    """
    import random as _random
    mix = get_zone_population_mix(zone_key)
    if not mix:
        return "human"
    races = [r for r, w in mix]
    weights = [w for r, w in mix]
    if rng is not None:
        return rng.choices(races, weights=weights, k=1)[0]
    return _random.choices(races, weights=weights, k=1)[0]
