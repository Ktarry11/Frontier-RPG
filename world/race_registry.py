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

PLAYABLE AS OF 2026-10-28: human, orc, forsaken, blood_elf, tauren. The
rest carry real art and stay available=False because nothing in the world
is theirs yet - race here is purely cosmetic (Character stores three
strings and nothing reads them in combat), so the gate is a CONTENT
judgement, not a balance one. Turning one on is a one-line change plus a
look at CharacterCreationScreen's race row, which is a SINGLE ROW of
90px buttons: five fit inside SCREEN_WIDTH alongside the gender block and
the preview, and eight would not. Count before you flip.
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
    #: the places in `variants` the character creator and the barber offer, or None for all of them. Old looks stay
    #: in `variants` so every save keeps its face (a save stores a place in this list); only the offer changes.
    offer: list = None


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
# The townsfolk (docs/blood_elf_npc_art_prompts.md, sheets BE-M and BE-W, landed 21 Nov 2026): 24 men and 24 women,
# front-only, so NPC looks and never offered at creation or the barber (offer= below keeps those to the eleven). They
# come AFTER every look a save can hold, so every save keeps its face: the men's after the eleven and the five new
# player looks (places 11-15, added by _add_new_male_looks below), the women's after the eleven. The men's places 16-39
# are m1-m24 in the sheet's order (apprentice, elder
# magister, gate guard, ranger, hawk handler, carpenter, stonemason, fisherman, cook, innkeeper, merchant, blacksmith,
# priest, archivist, herbalist, refugee, courier, spellbreaker, boatwright, tailor, lamplighter, veteran, student,
# lord), and place 40 is w4: the women's hooded ranger came back bearded, so he's a man. The women's places 11-33 are
# w1-w24 without w4 (apprentice, elder magistrix, guard captain, hawk handler, carpenter, weaver, fisherwoman, baker,
# innkeeper, merchant, enchanter, priestess, healer, herbalist, refugee, courier, orchard keeper, scribe, tailor,
# lamplighter, matriarch, student, lady).
_BLOOD_ELF_TOWNSMEN = [f"blood_elf_m{i}" for i in range(1, 25)] + ["blood_elf_w4"]
_BLOOD_ELF_WOMEN = _BLOOD_ELF_VARIANTS + [f"blood_elf_w{i}" for i in range(1, 25) if i != 4]

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
# The Emerald Reclamation's Timbermaw furbolgs and forest treants (Felwood, 14 Nov 2026): Kyle's
# Deadwood and corrupted-treant art with the fel taken out (tools/build_reclamation_npc_art.py).
# NPC-only.
_FURBOLG_VARIANTS = [f"furbolg_{i}" for i in range(1, 7)]
_TREANT_VARIANTS = [f"treant_{i}" for i in range(1, 3)]
# Deadwind Pass's two who aren't people any more (18 Nov 2026, tools/build_deadwind.py), from Kyle's Deadwind creature
# sheet: Grull the Younger, the ogre fused with the child he was, and the Bridge Echo, a liquidator caught mid-stride
# on the broken bridge. NPC-only, one each, single-facing like the furbolgs.
_OGRE_VARIANTS = ["ogre_1"]
_ECHO_VARIANTS = ["echo_1"]

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
            GenderOption("female", "Female", "", _BLOOD_ELF_WOMEN, offer=list(range(11))),
        ],
        # PLAYABLE, 2026-10-28 (Kyle: "Make new playable races, we have the sprites... Just add Tauren
        # and blood elf"). The content caught up with the art: the Crystalline Underdark cluster is a
        # blood elf expedition, Kael's Bastion is their camp, and the Crimson Codex - the game's first
        # faction, with the only authored reward gates in it - is a blood elf order. A player who picks
        # this race has somewhere to be from.
        available=True,
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
        race_id="furbolg",
        label="Furbolg",
        race_folder="furbolg",
        genders=[GenderOption("male", "Male", "", _FURBOLG_VARIANTS),
                 GenderOption("female", "Female", "", _FURBOLG_VARIANTS)],
        available=False,      # NPC-only: the Timbermaw of the Emerald Reclamation
    ),
    RaceOption(
        race_id="treant",
        label="Treant",
        race_folder="treant",
        genders=[GenderOption("male", "Male", "", _TREANT_VARIANTS),
                 GenderOption("female", "Female", "", _TREANT_VARIANTS)],
        available=False,      # NPC-only: the forest's own, standing with the Reclamation
    ),
    RaceOption(
        race_id="ogre",
        label="Ogre",
        race_folder="ogre",
        genders=[GenderOption("male", "Male", "", _OGRE_VARIANTS),
                 GenderOption("female", "Female", "", _OGRE_VARIANTS)],
        available=False,      # NPC-only: Grull the Younger, in Deadwind Pass
    ),
    RaceOption(
        race_id="echo",
        label="Echo",
        race_folder="echo",
        genders=[GenderOption("male", "Male", "", _ECHO_VARIANTS),
                 GenderOption("female", "Female", "", _ECHO_VARIANTS)],
        available=False,      # NPC-only: the Bridge Echo, in Deadwind Pass
    ),
    RaceOption(
        race_id="aetherian",
        label="Aetherian",
        race_folder="aetherian",
        # Kyle's P6 sheet (docs/player_sprite_prompts.md): five men, drawn as player looks (indices 0-4). Then the NPC
        # sheets AE-M and AE-W (docs/recruit_art_prompts_sheet6.md, landed 20 Nov 2026): 24 men (indices 5-28, m1-m24
        # in the sheet's order: scholar, archivist, guard, pilot, engineer, crystalsmith, merchant, councillor, healer,
        # dockworker, innkeeper, courier, astronomer, cook, refugee, gardener, magister, Ascendancy officer,
        # cartographer, musician, captain, sun-temple keeper, apprentice, noble) and 24 women (indices 0-23, w1-w24, the
        # same order with a weaver, a botanist, a singer and a scribe in place of the dockworker, gardener, musician and
        # apprentice's neighbours). The AE sheets are front-only, like the furbolgs. NPC-only until the start zone.
        genders=[GenderOption("male", "Male", "", [f"aetherian_p{i}" for i in range(1, 6)]
                              + [f"aetherian_m{i}" for i in range(1, 25)]),
                 GenderOption("female", "Female", "", [f"aetherian_w{i}" for i in range(1, 25)])],
        available=False,      # NPC-only for now: the survey at the Sunward Crown and Lenswatch
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
        # PLAYABLE, 2026-10-28 (Kyle, as above). The best-supported race in the game to pick up now:
        # Camp Taurajo, Longstand Camp, and Freewind Post - which is THE tauren city, 99 quests of
        # Thunder Bluff territory, and a people in exile with a seat nobody will take. There is more
        # authored tauren context than there is human.
        available=True,
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
    # Hillsbrad is contested ground, not Forsaken heartland: Tarren Mill holds the
    # east, but the farms and Southshore are still very much alive and human.
    "eastern_hillsbrad": [("forsaken", 70), ("human", 22), ("orc", 8)],
    "western_hillsbrad": [("human", 60), ("forsaken", 32), ("orc", 8)],
    # The town itself: the Society holds it, but the millers, smith and innkeeper who were here before the
    # Forsaken arrived are still working the west bank.
    "tarren_mill": [("forsaken", 70), ("human", 24), ("orc", 6)],
    # Southshore is the Alliance's own harbour town (its own map since 17 Nov 2026): human, to a person.
    "southshore": [("human", 100)],
    # The Timbermaw Tunnel is the Timbermaw's own (17 Nov 2026).
    "timbermaw_tunnel": [("furbolg", 100)],
    # Azshara (17 Nov 2026): the salvage camp is Orgrimmar's muscle and the Sunreach Conclave's magisters, with the
    # Earth transplants on the crews; out in the forest it's the camp's people and the Timbermaw.
    "talrendis_landing": [("orc", 50), ("blood_elf", 38), ("human", 12)],
    # Kyle, 17 Nov 2026: "It's still going to be furbolgs though like 90%....but some orcs, some humans, some goblins."
    "timbermaw_hold": [("furbolg", 90), ("orc", 4), ("human", 3), ("goblin", 3)],
    # Moonglade (18 Nov 2026): the Circle's night elves and tauren in Nighthaven, the Wakened on the west shore
    "moonglade": [("night_elf", 45), ("tauren", 35), ("human", 20)],
    "west_azshara": [("orc", 50), ("blood_elf", 25), ("furbolg", 15), ("human", 10)],
    # Dawnhaven (21 Nov 2026): the Sunreach Conclave's isle, its people and the transplants it took in
    "amberleaf_glade": [("blood_elf", 80), ("human", 20)],
    "duskfall_woods": [("blood_elf", 80), ("human", 20)],
    "firstlight_spire": [("blood_elf", 82), ("human", 14), ("orc", 4)],
    # Feralas (19 Nov 2026): Mojache is tauren with Orgrimmar's few; Feathermoon is the Sentinels'; the settlers of the
    # Fog Groves are transplants
    # the World Tree (19 Nov 2026): the trolls who climbed it, a goblin or two who built the lifts, a few transplants
    "rootwater_isle": [("troll", 80), ("goblin", 10), ("human", 10)],
    "lower_boughs": [("troll", 85), ("goblin", 5), ("human", 10)],
    "middle_boughs": [("troll", 90), ("human", 10)],
    "upper_boughs": [("troll", 90), ("human", 10)],
    "great_settlement": [("troll", 78), ("goblin", 8), ("human", 8), ("orc", 6)],
    "camp_mojache": [("tauren", 85), ("orc", 10), ("goblin", 5)],
    "feathermoon_stronghold": [("night_elf", 100)],
    "the_high_wilderness": [("tauren", 80), ("orc", 20)],
    "the_forgotten_coast": [("night_elf", 60), ("human", 40)],
    "the_twin_colossals": [("night_elf", 70), ("tauren", 30)],
    # the salvage crews out at Eldarath and the Font, and the odd Timbermaw scout
    "central_azshara": [("orc", 45), ("blood_elf", 35), ("human", 10), ("furbolg", 10)],
    # Stormwatch's grunts and the Conclave's magisters come out to the coast for what the sea gave back
    "east_azshara": [("orc", 45), ("blood_elf", 40), ("human", 15)],
    # The only people down here are the Crimson Codex and the handful of Horde the Codex have hired or
    # tolerated. Nobody is native to a place that is four years old.
    "the_crystalline_underdark": [("blood_elf", 82), ("forsaken", 10), ("orc", 8)],
    # The holdfast itself is the Codex almost to a person; the handful of others are hired hands who
    # came down the Descent with a contract.
    "kaels_bastion": [("blood_elf", 88), ("forsaken", 7), ("orc", 5)],
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


# ------------------------------------------------------------------ the new player looks
# Kyle, 20 Nov 2026: "about 5 sprites from each race the player can pick from", male first, four facings, empty hands
# (docs/player_sprite_prompts.md, sheets P1 to P5; tools/asset_pipeline/slice_player_sheet.py). They go on the END of
# each race's male list, which is its own list now (male and female shared one for every race but humans), and the
# creator and the barber offer only them. Women keep the old looks until theirs are drawn. The Aetherian (P6) and Veyr
# (P7) looks are on disk for when those races are playable.
NEW_MALE_LOOKS = {"human": "male_p", "orc": "orc_p", "blood_elf": "blood_elf_p", "forsaken": "forsaken_p",
                  "tauren": "tauren_p"}


def _add_new_male_looks():
    for race_id, prefix in NEW_MALE_LOOKS.items():
        g = get_gender(race_id, "male")
        if g is None or any(v.startswith(prefix) for v in g.variants):
            continue
        g.variants = list(g.variants) + [f"{prefix}{i}" for i in range(1, 6)]
        g.offer = list(range(len(g.variants) - 5, len(g.variants)))


_add_new_male_looks()


def _add_blood_elf_townsmen():
    """The blood elf townsmen go after the new player looks, never offered (see _BLOOD_ELF_TOWNSMEN)."""
    g = get_gender("blood_elf", "male")
    if g is not None and "blood_elf_m1" not in g.variants:
        g.variants = list(g.variants) + _BLOOD_ELF_TOWNSMEN


_add_blood_elf_townsmen()


# ------------------------------------------------------------------ the barber's chair
# Kyle, 20 Nov 2026: "lets make a barber choice if the sprite is gone". A save stores its look as a place in its race and
# gender's list (Character.appearance_variant), so a look can go two ways: its pictures deleted, or the list shortened
# so the number points past the end (get_variant_folder clamps that to the last look rather than crash). Either way the
# character loads with somebody else's face, or none; ui/screens/barber_screen.py lets them pick a new one once.
def look_is_missing(race_id, gender_id, variant_index):
    """True if this saved look can't be drawn as itself: no such race or gender, a place past the end of the list,
    or no front picture on disk."""
    import os
    gender = get_gender(race_id, gender_id)
    if gender is None or not gender.variants:
        return True
    if not 0 <= int(variant_index or 0) < len(gender.variants):
        return True
    base = sprite_base_path(race_id, gender_id, variant_index)
    return not base or not os.path.exists(os.path.join(base, "down.png"))


def pickable_looks(race_id, gender_id):
    """The places in this race and gender's list a player can pick: every look whose pictures are on disk. (When the
    new player sprites land, the creator and the barber offer only those; see docs/player_sprite_prompts.md.)"""
    gender = get_gender(race_id, gender_id)
    if gender is None:
        return []
    places = gender.offer if gender.offer is not None else range(len(gender.variants))
    return [i for i in places if not look_is_missing(race_id, gender_id, i)]
