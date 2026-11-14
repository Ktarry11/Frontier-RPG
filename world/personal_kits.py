"""Personal kits and racials - the two authored systems nothing was loading.

Both data files were written, committed and complete. Neither had a single
reader anywhere in the codebase, so every recruit played exactly like a stock
character of their class and spec, which is the one thing the kits exist to
prevent.

    data/npcs/personal_kits.json   67 recruits, 201 abilities, 67 named passives
    data/races/racials.json         5 races, 10 abilities, 12 passives

Kyle, 6 Nov 2026, on why the kits exist: "Give each human about 4 UNIQUE
abilities that are based on who they are as people. So that way even if they
are a specific class/spec they still are unique from each other. it'll let me
build more people of same class/spec."

=============================================================================
WHERE THEY LAND
=============================================================================

ABILITIES go into the character's own ability_book, and show in the spellbook's
CORE tab. That is the right home and it needs no new tab: Core is "things you
have regardless of class or spec" - the basic attack, Shoot, Wand - and a
personal kit is precisely that for the person who has it. ui/screens/
skills_screen.py's _is_universal already routes anything matching the
UNIVERSAL_SUFFIXES or flagged racial into Core; personal_* and racial_* ids are
added to that rule rather than given a tab of their own.

PASSIVES are scalar stat lines, so they go through the same bonus pool as gear,
talents and stances - entities/character.py's `bonuses` dict - which means they
need no new maths. They are applied by Character._recalculate_derived_stats via
get_personal_passives(), the same way get_talent_effects() already feeds it.

INNATE. No ranks, no talent gate, no level requirement, per the data's own
docstring. You have them because you are you.

=============================================================================
ASHER COLEMAN IS EXCLUDED, DELIBERATELY
=============================================================================

Kyle, 6 Nov: "dont touch Asher, he is a going to be a raid boss and religious
family annihilator. we can leave him as a treat later." He has no entry in
personal_kits.json and must not gain one here: his ability book is exactly his
two unique abilities (world/recruit_manager.build_asher_ability_book) and
tools/qa_asher_locked.py hash-locks his record. Keyed by recruit_id, this file
never touches him - but the guard below is explicit rather than incidental,
because "he happens to have no entry" is not the same promise as "he is
excluded".

=============================================================================
ABILITIES THAT NEED ENGINE WORK THEY DO NOT HAVE
=============================================================================

Many kit entries carry an "engine" note saying what the combat engine would
need - "redirect a queued attack", "swap row position mid-combat", "cooldown
that starts on expiry". Those notes were written honestly at authoring time and
are still true. An ability whose mechanic the engine cannot express is still
LOADED here: it appears, it is castable, and it does whatever its effect_type
and stat_mods already support, which for most is the useful part. What it will
not do is the bespoke half.

tools/qa_personal_kits.py reports how many sit in that state so the number is
visible rather than discovered in a fight.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS_PATH = ROOT / "data" / "npcs" / "personal_kits.json"
RACIALS_PATH = ROOT / "data" / "races" / "racials.json"

#: Never gains a personal kit. See the module docstring.
EXCLUDED_RECRUIT_IDS = {"asher_paladin", "asher_coleman", "asher"}

_kits = None
_racials = None


def _load(path, cache_name):
    global _kits, _racials
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return {k: v for k, v in data.items() if not k.startswith("_")}


def kits():
    global _kits
    if _kits is None:
        _kits = _load(KITS_PATH, "_kits")
    return _kits


def racials():
    global _racials
    if _racials is None:
        _racials = _load(RACIALS_PATH, "_racials")
    return _racials


def get_kit(recruit_id):
    """The personal kit for this recruit_id, or None."""
    if not recruit_id or recruit_id in EXCLUDED_RECRUIT_IDS:
        return None
    return kits().get(recruit_id)


def racial_of(character):
    """The racial block this character carries, or None.

    A COMPANION HAS NONE. All 68 are drawn as humans, so each was handed the Azerothian Human
    racial - the same "Every Man for Himself", "Perception" and "The Human Spirit" on 67 Core
    tabs. They are people from Earth, not natives (Kyle's standing rule, and the note at the
    top of racials.json says exactly this: "RECRUITS GET NOTHING FROM THIS FILE"); what makes
    each of them different is their personal kit. Kyle, [10]: "Recruits need to feel unique -
    not all the same human racials."
    """
    if getattr(character, "recruit_id", None):
        return None
    return get_racial(getattr(character, "race", None))


def get_racial(race):
    """The racial block for this race, or None."""
    if not race:
        return None
    return racials().get(str(race).lower().replace(" ", "_"))


#: Keys the bonus pool reads as a FRACTION, while these data files author
#: every passive in PERCENT POINTS. 10 means +10% in the JSON and +1000% to
#: the engine, so these are divided by 100 on the way in.
#:
#: This is not a guess. claude/value_conventions_and_dead_data_2026_10_29.md
#: has the table, and names this exact trap as the cause of "thirteen bugs in
#: one session, including two permanent damage immunities and a +800% health
#: buff". Measured here before converting: Dan's max_health_pct of 10 took his
#: health from 388 to 5236 - 13.49x - because entities/character.py line 1549
#: computes (1.0 + value) while line 1625 computes (1.0 + value / 100.0) for
#: armor_pct. Same suffix, opposite meaning, 76 lines apart.
#:
#: Only the talent-channel fraction keys from that table appear here, because
#: that is the channel these passives feed. Everything else in the kits -
#: armor_pct, dodge, haste, crit_chance*, the resistances - is already percent
#: points and passes through untouched.
FRACTION_KEYS = {
    "max_health_pct", "max_mana_pct", "threat_generation_pct",
    "damage_taken_pct", "physical_damage_taken_pct", "magic_damage_taken_pct",
    "fire_damage_taken_pct", "frost_damage_taken_pct", "nature_damage_taken_pct",
    "shadow_damage_taken_pct", "arcane_damage_taken_pct", "holy_damage_taken_pct",
    "all_ability_cost_pct",
}


#: Passive keys the COMBAT code looks up by name (get_talent_effect) rather than reading off the
#: stat sheet. Measured 13 Nov 2026: a kit passive only ever reached the stat-sheet pool, so
#: every one of these did nothing - "+7% healing done" on fifteen healers, every school damage
#: bonus, pet damage and health, crit damage, shorter stuns. They are written in the kit as
#: whole percents and the combat code wants fractions, so they are converted here.
COMBAT_KEYS = {
    "healing_done", "crit_damage_physical", "crit_damage_spell", "pet_damage", "pet_health",
    "stun_duration_reduction_pct", "threat_generation_pct", "healing_received_pct",
    "gold_find_pct",
}


def is_combat_key(key):
    """True for a passive the combat code reads by name: the set above, any school's damage
    (fire_damage_pct) and any creature type's (beast_damage_pct)."""
    return key in COMBAT_KEYS or (key.endswith("_damage_pct") and not key.endswith("_crit_damage_pct"))


def combat_passives_for(character):
    """This character's kit and racial passives that combat reads by name, as fractions.
    Character.get_talent_effects adds these to what talents, stances and forms give."""
    total = {}
    for block in ((get_kit(getattr(character, "recruit_id", None)) or {}).get("passives"),
                  (racial_of(character) or {}).get("passives")):
        if not isinstance(block, dict):
            continue
        for k, v in block.items():
            if k.startswith("_") or not isinstance(v, (int, float)) or not is_combat_key(k):
                continue
            total[k] = total.get(k, 0) + v / 100.0
    return total


def _scalars(block):
    """Numeric entries only, converted to the unit the engine reads.

    The _from/_name/_wow keys are documentation and are dropped.
    """
    if not isinstance(block, dict):
        return {}
    out = {}
    for k, v in block.items():
        if k.startswith("_") or not isinstance(v, (int, float)) or is_combat_key(k):
            continue      # combat keys go through combat_passives_for, never both
        out[k] = v / 100.0 if k in FRACTION_KEYS else v
    return out


#: Plain words for the passives the stat-label table does not know.
PASSIVE_LABELS = {
    "healing_done": "Healing Done", "healing_received_pct": "Healing Received",
    "stun_duration_reduction_pct": "Shorter Stuns and Silences",
    "threat_generation_pct": "Threat", "gold_find_pct": "Coin from Kills",
    "crit_damage_physical": "Physical Crit Damage", "crit_damage_spell": "Spell Crit Damage",
    "pet_damage": "Pet Damage", "pet_health": "Pet Health",
    "beast_damage_pct": "Damage to Beasts",
}


def passive_entries_for(character):
    """[(name, source, [text line, ...]), ...] - the character's passives, for display.

    Kyle, 10 Nov: "show passives under Core." A recruit's kit passive and a race's passive
    are always on and were listed nowhere: the only trace of Kiet's "-30% threat, +8% haste"
    was the numbers on his sheet being different.
    """
    from combat.status_effects import StatusEffectMixin
    out = []
    for source, block, fallback in (
            ("Personal", (get_kit(getattr(character, "recruit_id", None)) or {}).get("passives"), "Personal Trait"),
            ("Racial", (racial_of(character) or {}).get("passives"),
             f"{str(getattr(character, 'race', '') or '').replace('_', ' ').title()} Heritage")):
        if not isinstance(block, dict):
            continue
        lines = []
        for key, value in block.items():
            if key.startswith("_") or not isinstance(value, (int, float)) or not value:
                continue
            label = StatusEffectMixin.STAT_LABELS.get(key)
            pct = key.endswith("_pct") or key in ("haste", "dodge", "parry", "crit_chance_physical", "crit_chance_spell",
                                                  "pet_damage", "pet_health", "healing_done",
                                                  "crit_damage_physical", "crit_damage_spell")
            label = label or PASSIVE_LABELS.get(key)
            if label is None:
                label = key[:-4].replace("_", " ").title() if key.endswith("_pct") else key.replace("_", " ").title()
            label = label.replace(" %", "").replace(" Pct", "").strip()     # "+10% Max Health", not "+10% Max Health %"
            lines.append(f"{'+' if value > 0 else ''}{value:g}{'%' if pct else ''} {label}")
        if lines:
            out.append((block.get("_name") or fallback, source, lines))
    return out


def passives_for(character):
    """Summed scalar passives this character has from their kit and race.

    Returned in the same key space as talent effects, so the caller folds it
    into `bonuses` with no translation.
    """
    total = {}
    kit = get_kit(getattr(character, "recruit_id", None))
    if kit:
        for k, v in _scalars(kit.get("passives")).items():
            total[k] = total.get(k, 0) + v
    racial = racial_of(character)
    if racial:
        for k, v in _scalars(racial.get("passives")).items():
            total[k] = total.get(k, 0) + v
    return total


def ability_entries_for(character):
    """Raw ability dicts this character should know, kit then racial."""
    out = []
    kit = get_kit(getattr(character, "recruit_id", None))
    if kit:
        out.extend(a for a in (kit.get("abilities") or []) if isinstance(a, dict))
    racial = racial_of(character)
    if racial:
        out.extend(a for a in (racial.get("abilities") or []) if isinstance(a, dict))
    return out


def grant(character):
    """Put this character's kit and racial abilities into their ability_book.

    Idempotent - add_ability replaces by id, and the passive half is read
    fresh on every recalc rather than accumulated, so calling this twice
    cannot double anything. Returns the number of abilities added.

    Fails soft: a malformed entry is skipped rather than taking recruitment
    down with it. A companion who joins missing one ability is a bug; a
    companion who cannot be recruited at all is a worse one.
    """
    book = getattr(character, "ability_book", None)
    if book is None:
        return 0
    from combat.abilities import _ability_from_data
    added = 0
    # A companion saved before racials came off them still has the two in their book.
    if getattr(character, "recruit_id", None):
        for ability_id in [a for a in list(book.abilities) if str(a).startswith("racial_")]:
            del book.abilities[ability_id]
    for entry in ability_entries_for(character):
        try:
            book.add_ability(_ability_from_data(entry))
            added += 1
        except Exception:
            continue
    return added
