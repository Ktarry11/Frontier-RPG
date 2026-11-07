# ============================================
# GAME CONFIGURATION
# ============================================

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Viewport (game world visible area, centered on player)
VIEWPORT_WIDTH = 800
VIEWPORT_HEIGHT = 600
VIEWPORT_X = 20  # Screen position of viewport
VIEWPORT_Y = 20

# Colors (RGB)
COLOR_BLACK = (20, 20, 20)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_GRAY = (50, 50, 50)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_RED = (220, 50, 50)
COLOR_GREEN = (50, 220, 50)
COLOR_BLUE = (50, 150, 220)
COLOR_YELLOW = (220, 220, 50)
COLOR_GOLD = (200, 150, 50)

# Combat
BASE_TURN_METER_MAX = 100.0
TURN_THRESHOLD = 100.0  # When meter hits this, character gets a turn
AGI_TO_TURN_SPEED = 1.0  # AGI * this = turn speed multiplier

# UI
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_PADDING = 10
FONT_SIZE_LARGE = 40
FONT_SIZE_NORMAL = 20
FONT_SIZE_SMALL = 14

# Gameplay
BASE_LEVEL = 1
MAX_LEVEL = 60  # Base game level cap
PRESTIGE_LEVEL = 60  # Prestige trigger: reset to level 1 and increment prestige_level

# Save system
SAVE_VERSION = 9  # v9: adds faction reputation standing. v7: adds travel state (hearth bind/cooldown, flight nodes, riding + mounts). v6: adds world position (zone/x/y) + per-character row & spec lock. v5 added the party roster; v4 added talent spend.

#: Number of save slots shown in the menu (Kyle, 2026-09-06: "improve save
#: slots from 1 to 5" for external playtesting - multiple testers/characters
#: need to coexist without overwriting each other; raised to 15 on 2026-10-31,
#: "Make it 3x5 layout"; raised to 20 on 2026-11-07, "Ok let's only do 20
#: slots"). Slot filenames are "save_slot_1.json".."save_slot_20.json" (see
#: save_slot_filename() just below). Slot 1 is special-cased to read/write
#: the original single-slot "character.json" so saves made before this
#: change keep working without a migration step - see save_slot_filename()'s
#: docstring.
#:
#: Raising this number is safe and needs no migration: slots that have never
#: been written simply have no file and read as Empty.
SAVE_SLOT_COUNT = 20

#: The slot picker's grid, 5 columns x 4 rows. Twenty slots stacked in the
#: original single column would be 1,340px tall on a 720px screen, so the
#: shape is part of the setting rather than something the menu guesses.
#: At five columns a slot is 226px wide, which is why the picker truncates
#: a long summary rather than letting it run into its neighbour.
SAVE_SLOT_COLUMNS = 5


def save_slot_filename(slot_number):
    """Map a 1-indexed save slot number to its save file name.

    Slot 1 is special-cased to the original single-slot filename
    ("character.json") rather than "save_slot_1.json" - this is what
    lets every save made before multi-slot support keep working with
    zero migration: an existing character.json is simply "already in
    slot 1" the first time the new 5-slot menu loads, no file rename or
    data conversion needed. Slots 2-5 are new files that never existed
    before, so they need no such compatibility shim.

    Lives in config.py rather than core/game_state.py (where the
    save/load methods that call it live) specifically to avoid a
    circular import - ui/screens/menu_screen.py needs this function to
    render slot filenames, but core/game_state.py already imports
    MenuScreen, so menu_screen.py importing back from game_state.py
    would be circular. config.py has no game-logic imports of its own,
    so it's safe for both sides to depend on.
    """
    if slot_number == 1:
        return "character.json"
    return f"save_slot_{slot_number}.json"

# ---------------------------------------------------------------------------
# Experience curve (base game caps at level 60)
# ---------------------------------------------------------------------------
# Calibrated to real-fight targets (assuming ~average same-level monster kills,
# not accounting for quests/dungeon bonuses which reduce this further):
#   Level  1 ->  2:  ~5 fights
#   Level 40 -> 41:  ~40 fights (real grind, not a light tax)
#   Level 59 -> 60:  ~150-175 fights (the big final push)
# Shape: gentle power curve for most of the range, with an accelerating
# multiplier kicking in past level 35 so the last ~20 levels ramp up hard
# without the early/mid game turning into a slog. Reduced by a flat 10%
# from the originally modeled curve per design discussion - quests (Phase 7)
# are expected to make up part of the difference once built.
EXP_CURVE_BASE_MULT = 280
EXP_CURVE_BASE_POWER = 1.35
EXP_CURVE_ACCEL_START = 35
EXP_CURVE_ACCEL_POWER = 2.6
EXP_CURVE_ACCEL_MULT = 2.6
EXP_CURVE_REDUCTION = 0.10  # flat 10% reduction, confirmed in design discussion
EXP_CURVE_ACCEL_SPAN_TOP = 59  # accel ramps fully in by level 59 (base game level cap = 60)

#: HOW MUCH XP THE WORLD ACTUALLY HANDS OUT, as a multiplier on the calculated
#: reward. These are levelling-SPEED dials and are deliberately separate from
#: the EXP_CURVE_* values above, which set how much XP a level COSTS.
#:
#: Two knobs for the same outcome, and they are not interchangeable: changing
#: the curve re-prices every level the player has already earned, so a character
#: mid-game can find their bar has moved. Changing these only affects XP earned
#: from here on, which is what "levelling is too fast" actually asks for.
#:
#: Kyle, 4 Nov 2026, relaying his friend's playtest: "exp rate is too high. Let's
#: drop kill exp by 60% and quest exp by 50%."
#:
#: Applied ONCE, at the end of each source's own calculation, so every bonus
#: that feeds into them (level difference, boss, cave/subzone) is scaled with
#: them rather than around them.
KILL_EXP_MULTIPLIER = 0.40    # -60% from kills
QUEST_EXP_MULTIPLIER = 0.50   # -50% from quest turn-ins


# Consumables (Phase 6)
POTION_COOLDOWN_SECONDS = 5.0  # Shared potion cooldown (WoW-style)
CONSUMABLE_VENDOR_MARKUP = 1.0  # Vendor sells at base price (no markup for now)

def get_exp_needed_for_level(level):
    """
    XP required to advance from `level` to `level + 1`. Single source of
    truth for this formula - character.py's leveling logic and any UI that
    displays an EXP bar/threshold must both call this function rather than
    hardcoding the formula themselves, to avoid the display/logic mismatch
    bug that caused confusing multi-level jumps in earlier testing.
    """
    base = EXP_CURVE_BASE_MULT * (level ** EXP_CURVE_BASE_POWER)
    if level > EXP_CURVE_ACCEL_START:
        span = EXP_CURVE_ACCEL_SPAN_TOP - EXP_CURVE_ACCEL_START
        accel = 1.0 + ((level - EXP_CURVE_ACCEL_START) / span) ** EXP_CURVE_ACCEL_POWER * EXP_CURVE_ACCEL_MULT
        base *= accel
    return int(base * (1.0 - EXP_CURVE_REDUCTION))
