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
# THE RULES (Kyle, 12 Nov 2026: "No bro, we wont mix and match. A shaman who uses 5 enhancement
# and 3 elemental gets 2 and 4 piece enhancement bonus and 2 piece elemental."):
#   * each version is counted ON ITS OWN - five Enhancement pieces and three Elemental pieces
#     are a five-piece set and a three-piece set, never an eight-piece one;
#   * each version pays its own bonuses for its own count, so both can be running at once;
#   * an exchange changes the piece's name, stats and version and nothing else - same slot,
#     same item level, same rarity, same set. It is free, at the exchange NPCs.

def variants(definition):
    """{key: variant} for a set, or {} for a set with one version."""
    return (definition or {}).get("variants") or {}


def version_counts(character, set_id):
    """{version key: pieces worn} for one set. A set with no versions is {None: n}."""
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    order = list(variants(get(set_id)))
    out = {}
    for item in slots.values():
        if item is not None and getattr(item, "set_id", None) == set_id:
            key = getattr(item, "set_variant", None) if order else None
            if order and key not in order:
                continue              # a piece of no known version belongs to no version's count
            out[key] = out.get(key, 0) + 1
    return out


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
    """{stat: total} from every set bonus this character has earned - each version of each
    set paying for its own piece count."""
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    set_ids = {getattr(item, "set_id", None) for item in slots.values() if item is not None}
    out = {}
    for sid in set_ids:
        definition = get(sid)
        if not definition:
            continue
        for version, n in version_counts(character, sid).items():
            for need, bonus in bonuses_for(definition, version):
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
    # The card is about THIS piece's version: its pieces, its count, its bonuses.
    shown = getattr(item, "set_variant", None) if kinds else None
    if kinds and shown not in kinds:
        shown = next(iter(kinds))
    if kinds:
        pieces = {slot: spec.get("name", slot) for slot, spec in (kinds[shown].get("pieces") or {}).items()}
    else:
        pieces = definition.get("pieces") or {}
    slots = getattr(getattr(character, "equipment", None), "slots", None) or {}
    worn = set()
    if character is not None:
        worn = {slot for slot in worn_slots(character, item.set_id)
                if not kinds or getattr(slots[slot], "set_variant", None) == shown}
    title = definition.get("name", item.set_id)
    if len(kinds) > 1:              # a set with one version needs no version in its title
        title += f" - {kinds[shown].get('label', shown.title())}"
    lines = [(f"{title} ({len(worn)}/{len(pieces)})", "title")]
    for slot, name in pieces.items():
        lines.append((f"  {name}", "have" if slot in worn else "missing"))
    for need, bonus in bonuses_for(definition, shown):
        lines.append((f"({need}) Set: {describe(bonus)}", "active" if len(worn) >= need else "inactive"))
    options = exchange_options(item)
    if options:
        lines.append(("Exchange for: " + ", ".join(f"{name} ({label})" for _k, label, name in options), "missing"))
    return lines


# ----------------------------------------------------------------------
# Making a piece
# ----------------------------------------------------------------------

def make_piece(set_id, slot, variant=None):
    """A new Item: the named version's piece for that slot (the set's first version if none
    is named). None if the set, the version or the slot does not exist.

    THE ONE PLACE A SET PIECE IS MADE - a boss table, a quest reward and a test all call this,
    so a piece cannot exist with a level, armour or name the set does not give it.
    """
    from entities.item import Item
    definition = get(set_id)
    kinds = variants(definition)
    if not definition or not kinds:
        return None
    variant = variant or next(iter(kinds))
    spec = ((kinds.get(variant) or {}).get("pieces") or {}).get(slot)
    frame = (definition.get("slots") or {}).get(slot)
    if not spec or not frame:
        return None
    item = Item(f"{set_id}_{slot}", spec["name"], slot, frame["item_level"],
                definition.get("rarity", "rare"), armor_type=definition.get("armor_type"),
                primary_stats=dict(spec.get("primary_stats") or {}),
                secondary_stats=dict(spec.get("secondary_stats") or {}),
                armor_value=frame.get("armor", 0), required_level=frame.get("required_level", 1),
                sell_price=None,            # None = priced by the gear curve like any other blue
                set_id=set_id)
    item.set_variant = variant
    return item


# ----------------------------------------------------------------------
# The exchange
# ----------------------------------------------------------------------

def exchangeable(party):
    """[(member, item, where, version key, label, new name)] - every exchange on offer to a
    party: each set piece worn or carried by an active member, once per other version."""
    out = []
    for member in getattr(party, "members", []) or []:
        slots = getattr(getattr(member, "equipment", None), "slots", None) or {}
        held = [(it, "worn") for it in slots.values() if it is not None]
        held += [(it, "in bags") for it in getattr(member, "inventory", []) or []]
        for it, where in held:
            for key, label, name in exchange_options(it):
                out.append((member, it, where, key, label, name))
    return out
