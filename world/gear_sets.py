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


# ----------------------------------------------------------------------
# One set, a version per spec
# ----------------------------------------------------------------------
#
# Kyle, 12 Nov 2026: "we have hybrid classes too... We can keep the SET name, but change the
# stuff inside." A Shaman's chest drops as Rainspeaker's Hauberk (Enhancement) and can be
# EXCHANGED for Rainspeaker's Vestments (Elemental). So a set may carry `variants`:
#
#   "variants": {"enhancement": {"label": "Enhancement",
#                                "pieces": {"chest": {"name": "Rainspeaker's Hauberk",
#                                                     "primary_stats": {...},
#                                                     "secondary_stats": {...}}, ...},
#                                "bonuses": {"2": {...}, "4": {...}}},
#                "elemental": {...}}
#
# THE RULES:
#   * every version of every piece counts toward the ONE set - mixing never costs you a piece;
#   * the BONUSES you get are those of the version you wear most of (a tie goes to whichever
#     the set lists first), so a 5 Enhancement / 3 Elemental shaman has eight pieces and
#     Enhancement's bonuses;
#   * an exchange changes the piece's name, stats and version and nothing else - same slot,
#     same item level, same rarity, same set.

def variants(definition):
    """{key: variant} for a set, or {} for a set with one version."""
    return (definition or {}).get("variants") or {}


def leading_variant(character, set_id):
    """The version this character wears most of, or None (no versions / none worn)."""
    definition = get(set_id)
    order = list(variants(definition))
    if not order:
        return None
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    tally = {}
    for item in slots.values():
        if item is not None and getattr(item, "set_id", None) == set_id:
            key = getattr(item, "set_variant", None)
            if key in order:
                tally[key] = tally.get(key, 0) + 1
    if not tally:
        return None
    return max(order, key=lambda k: (tally.get(k, 0), -order.index(k)))


def bonuses_for(definition, variant=None):
    """[(pieces, bonus)] ascending - the named version's, else the set's own."""
    source = variants(definition).get(variant) if variant else None
    table = (source or {}).get("bonuses") or definition.get("bonuses") or {}
    return sorted(((int(n), b) for n, b in table.items()), key=lambda pair: pair[0])


def exchange_options(item):
    """[(key, label, piece name)] this piece could be exchanged for - every OTHER version of
    the set that has a piece for this slot. [] if there is nothing to exchange for."""
    definition = get(getattr(item, "set_id", None))
    out = []
    for key, variant in variants(definition).items():
        spec = (variant.get("pieces") or {}).get(item.slot)
        if spec and key != getattr(item, "set_variant", None):
            out.append((key, variant.get("label", key.title()), spec.get("name", item.name)))
    return out


def exchange(item, variant):
    """Turn this piece into another spec's version of itself. Returns True if it changed.

    Only the name, the stats and the version move. Refused (False) for a piece of no set, a
    version the set does not have, or a slot that version has no piece for.
    """
    definition = get(getattr(item, "set_id", None))
    spec = ((variants(definition).get(variant) or {}).get("pieces") or {}).get(item.slot)
    if not spec or variant == getattr(item, "set_variant", None):
        return False
    item.name = spec.get("name", item.name)
    if "primary_stats" in spec:
        item.primary_stats = dict(spec["primary_stats"])
    if "secondary_stats" in spec:
        item.secondary_stats = dict(spec["secondary_stats"])
    item.set_variant = variant
    return True


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
        for need, bonus in bonuses_for(definition, leading_variant(character, sid)):
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
    kinds = variants(definition)
    lead = leading_variant(character, item.set_id) if character is not None else None
    shown = lead or getattr(item, "set_variant", None) or (next(iter(kinds)) if kinds else None)
    if kinds:
        pieces = {slot: spec.get("name", slot) for slot, spec in (kinds[shown].get("pieces") or {}).items()}
    else:
        pieces = definition.get("pieces") or {}
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    worn = set(worn_slots(character, item.set_id)) if character is not None else set()
    title = definition.get("name", item.set_id)
    if kinds:
        title += f" - {kinds[shown].get('label', shown.title())}"
    lines = [(f"{title} ({len(worn)}/{len(pieces)})", "title")]
    for slot, name in pieces.items():
        # a worn piece is listed under the name it actually has, whichever version it is
        lines.append((f"  {slots[slot].name if slot in worn else name}", "have" if slot in worn else "missing"))
    for need, bonus in bonuses_for(definition, shown):
        lines.append((f"({need}) Set: {describe(bonus)}", "active" if len(worn) >= need else "inactive"))
    options = exchange_options(item)
    if options:
        lines.append(("Exchange for: " + ", ".join(f"{name} ({label})" for _k, label, name in options), "missing"))
    return lines
