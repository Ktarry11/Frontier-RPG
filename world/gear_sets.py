"""Gear sets: wear enough pieces of one set and it gives you more than the pieces do.

Kyle, [95]: "We NEED to start working on getting gear sets." The model is WoW's dungeon sets -
eight pieces, bonuses at 2 / 4 / 6 / 8. `Item.set_id` has existed (and been saved) since the
item class was written, and until this module nothing read it.

THIS IS THE ENGINE, and it is deliberately small:

  * a set is data (data/items/gear_sets.json): a name, the class it is for, its pieces by
    slot, and its bonuses by piece count;
  * a bonus is a dict of stats, in the SAME vocabulary gear and talents use, and it is folded
    into the same pool they are (Character._recalculate_derived_stats) - so a set bonus of
    +40 attack power and a ring with +40 attack power cannot behave differently;
  * a piece counts once per SLOT it is worn in, so two copies of a set ring count twice only
    if the set really has two ring pieces.

A proc-style bonus ("your heals have a chance to...") is not built yet. When it is, it rides
the bridge trinket procs use (Character._sync_equipment_procs) rather than a second system.
"""
import json
from pathlib import Path

_PATH = Path(__file__).parent.parent / "data" / "items" / "gear_sets.json"
_SETS = None


def all_sets():
    """{set_id: definition}. {} if the file is missing or unreadable - a broken data file must
    not stop a character existing."""
    global _SETS
    if _SETS is None:
        try:
            _SETS = json.loads(_PATH.read_text(encoding="utf-8")).get("sets", {})
        except (OSError, json.JSONDecodeError):
            _SETS = {}
    return _SETS


def register(set_id, definition):
    """Add or replace a set at run time (tests, and generators that build sets)."""
    all_sets()[set_id] = definition


def get(set_id):
    return all_sets().get(set_id) if set_id else None


def worn_slots(character, set_id):
    """The slots in which this character is wearing a piece of the set."""
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    return [slot for slot, item in slots.items()
            if item is not None and getattr(item, "set_id", None) == set_id]


def count(character, set_id):
    return len(worn_slots(character, set_id))


def thresholds(definition):
    """[(pieces, bonus dict), ...] in ascending order of pieces."""
    return sorted(((int(n), b) for n, b in (definition.get("bonuses") or {}).items()),
                  key=lambda pair: pair[0])


def active_bonuses(character):
    """{stat: total} from every set bonus this character has earned."""
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    worn = {}
    for item in slots.values():
        sid = getattr(item, "set_id", None) if item is not None else None
        if sid:
            worn[sid] = worn.get(sid, 0) + 1
    out = {}
    for sid, n in worn.items():
        definition = get(sid)
        if not definition:
            continue
        for need, bonus in thresholds(definition):
            if n >= need:
                for stat, value in (bonus.get("stats") or {}).items():
                    out[stat] = out.get(stat, 0) + value
    return out


_PRETTY = {"crit_chance": "Critical Strike", "crit_chance_spell": "Spell Critical Strike",
           "hp5": "Health per turn", "mp5": "Mana per turn"}
_PERCENT = ("crit_chance", "crit_chance_spell", "dodge", "parry", "haste", "block_chance")


def describe(bonus):
    """The line a player reads for one bonus. Authored text wins; otherwise it is built from
    the stats, so a bonus can never grant something its line does not say."""
    if bonus.get("text"):
        return bonus["text"]
    parts = []
    for stat, value in (bonus.get("stats") or {}).items():
        label = _PRETTY.get(stat, stat.replace("_pct", "").replace("_", " ").title())
        pct = "%" if (stat in _PERCENT or stat.endswith("_pct")) else ""
        parts.append(f"+{value:g}{pct} {label}")
    return ", ".join(parts)


def tooltip_lines(item, character=None):
    """[(text, kind)] for an item card. kind: 'title', 'have', 'missing', 'active', 'inactive'.
    [] for an item in no set."""
    definition = get(getattr(item, "set_id", None))
    if not definition:
        return []
    pieces = definition.get("pieces") or {}
    worn = set(worn_slots(character, item.set_id)) if character is not None else set()
    lines = [(f"{definition.get('name', item.set_id)} ({len(worn)}/{len(pieces)})", "title")]
    for slot, name in pieces.items():
        lines.append((f"  {name}", "have" if slot in worn else "missing"))
    for need, bonus in thresholds(definition):
        lines.append((f"({need}) Set: {describe(bonus)}", "active" if len(worn) >= need else "inactive"))
    return lines
