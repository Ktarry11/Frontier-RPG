"""Enchanting: enchantments on gear, and disenchanting gear into materials.

Data: data/enchanting/enchants.json, written by tools/build_enchanting.py (which explains the
numbers). Kyle, 14 Nov 2026: WoW classic materials from disenchanting, the town enchanters teach
it, a handful of proc weapon enchants, wands and weapon oils, and hybrid enchants beside the
classic ones.

ENCHANTING. A formula makes a scroll holding one enchantment (material_type "enchant_scroll").
apply() reads a scroll onto a piece of gear: it sets item.enchant_id and uses up the scroll. One
enchantment per item; a new one replaces the old. The enchantment's stats reach the wearer through
Item.get_all_stat_bonuses, the same road a socketed gem takes, and a proc enchantment hangs its
proc on the wearer through Character._sync_equipment_procs beside the item's own.

WHAT GOES WHERE. Bracers, boots, gloves, cloaks and chests take their own enchantments, a shield
takes shield enchantments, any weapon takes weapon enchantments, and a two-hander also takes 2H
ones. Rings, trinkets, helms, legs and shoulders take none, as in classic.

DISENCHANTING. A green, blue or purple item breaks down into materials by its level, from classic's
table: greens mostly give dust (weapons mostly essence), blues give a shard, epics give shards or a
Nexus Crystal at the top. The item is destroyed. It needs the enchanting skill for its level.
"""
import json
import random
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: equipment slot -> enchantment group
SLOT_GROUPS = {"wrist": "bracer", "feet": "boots", "hands": "gloves", "back": "cloak", "chest": "chest"}
DISENCHANTABLE = ("uncommon", "rare", "epic")


@lru_cache(maxsize=1)
def data():
    path = ROOT / "data/enchanting/enchants.json"
    if not path.exists():
        return {"enchants": {}, "disenchant": [], "groups": {}, "rods": []}
    return json.loads(path.read_text(encoding="utf-8"))


def enchant(enchant_id):
    return data()["enchants"].get(enchant_id) if enchant_id else None


def is_scroll(material_id):
    return material_id in data()["enchants"]


def _hand(weapon_type):
    try:
        from entities.equipment import _load_weapon_type_hand
        return _load_weapon_type_hand(weapon_type)
    except Exception:
        return None


def groups_for(item):
    """The enchantment groups this item takes (empty if none)."""
    if item is None:
        return set()
    wt = getattr(item, "weapon_type", None)
    if wt == "shield":
        return {"shield"}
    if wt:
        hand = _hand(wt)
        if hand == "two_hand":
            return {"weapon", "2h"}
        if hand in ("main_or_off", "main_hand", "one_hand"):
            return {"weapon"}
        return set()            # wands, bows, librams, tomes: no enchantments
    if getattr(item, "armor_type", None) in (None, "bag", "accessory") and getattr(item, "slot", None) not in SLOT_GROUPS:
        return set()
    group = SLOT_GROUPS.get(getattr(item, "slot", None))
    return {group} if group else set()


def fits(item, enchant_id):
    e = enchant(enchant_id)
    return bool(e) and e["group"] in groups_for(item)


def group_label(group):
    return data()["groups"].get(group, {}).get("label", group.title())


def stats(item):
    """The stats the item's enchantment adds."""
    e = enchant(getattr(item, "enchant_id", None))
    return dict(e["stats"]) if e else {}


def proc(item):
    e = enchant(getattr(item, "enchant_id", None))
    return e.get("proc") if e else None


def label(enchant_id):
    """How the enchantment reads on an item: its stats, or a proc's name."""
    e = enchant(enchant_id)
    if not e:
        return ""
    if e.get("proc"):
        return e["title"]
    from world.jewelcrafting import stat_text
    return stat_text(e["stats"])


def tooltip_lines(item):
    """['Enchanted: +8 Strength'] or ['Enchanted: Crusader', '<what it does>'] or []."""
    e = enchant(getattr(item, "enchant_id", None))
    if not e:
        return []
    out = [f"Enchanted: {label(item.enchant_id)}"]
    if e.get("proc"):
        out.append(e["proc"].get("describe", ""))
    return out


def apply(player, item, scroll_id):
    """Read an enchantment scroll from the player's bags onto the item. -> (ok, message)."""
    e = enchant(scroll_id)
    if e is None:
        return False, "That isn't an enchantment."
    if player.get_material_quantity(scroll_id) < 1:
        return False, f"You don't have {e['name']}."
    if e["group"] not in groups_for(item):
        return False, f"{e['name']} only goes on {_where(e['group'])}."
    player.consume_material(scroll_id, 1)
    old = enchant(getattr(item, "enchant_id", None))
    item.enchant_id = scroll_id
    msg = f"{item.name} is enchanted: {label(scroll_id)}."
    if old:
        msg += f" The old enchantment ({label_of(old)}) is gone."
    return True, msg


def label_of(e):
    if e.get("proc"):
        return e["title"]
    from world.jewelcrafting import stat_text
    return stat_text(e["stats"])


def _where(group):
    return {"bracer": "bracers", "boots": "boots", "gloves": "gloves", "cloak": "cloaks",
            "chest": "chest armour", "shield": "shields", "weapon": "weapons",
            "2h": "two-handed weapons"}.get(group, group)


def refresh(owner):
    """Re-derive the wearer's stats after an enchantment changed on something they wear."""
    try:
        owner._recalculate_derived_stats()
    except Exception:
        pass


# ------------------------------------------------------------------ disenchanting
def item_level(item):
    return int(getattr(item, "required_level", 0) or getattr(item, "item_level", 1) or 1)


def band(item):
    lvl = item_level(item)
    for row in data()["disenchant"]:
        if lvl <= row["max_level"]:
            return row
    return data()["disenchant"][-1]


def skill_needed(item):
    row = band(item)
    # blues and epics need a little more, as in classic
    return row["skill"] + (25 if getattr(item, "rarity", "") in ("rare", "epic") and row["skill"] > 1 else 0)


def can_disenchant(character, item):
    """-> (ok, reason)."""
    if item is None:
        return False, ""
    if not character.knows_profession("enchanting"):
        return False, "You need to learn Enchanting first."
    if getattr(item, "rarity", "") not in DISENCHANTABLE:
        return False, "Only green, blue and purple gear can be disenchanted."
    if getattr(item, "recipe_id", None) or getattr(item, "bag_capacity", 0) or getattr(item, "armor_type", None) == "bag":
        return False, "That can't be disenchanted."
    if not (getattr(item, "weapon_type", None) or getattr(item, "slot", None)):
        return False, "That can't be disenchanted."
    need = skill_needed(item)
    if character.profession_skills.get("enchanting", 0) < need:
        return False, f"Disenchanting this needs Enchanting {need}."
    return True, ""


def is_weapon(item):
    wt = getattr(item, "weapon_type", None)
    return bool(wt) and wt != "shield"


def outcomes(item):
    """[(material id, low, high, chance)] for what the item can break into."""
    row = band(item)
    rarity = getattr(item, "rarity", "uncommon")
    lvl = item_level(item)
    if rarity == "uncommon":
        dust = (row["dust"], *row["dust_count"])
        ess = (row["essence"], *row["essence_count"])
        main, other = (ess, dust) if is_weapon(item) else (dust, ess)
        out = [(*main, 0.75), (*other, 0.20)]
        if lvl > 15:
            small = row["shard"].replace("large_", "small_")
            out.append((small, 1, 1, 0.05))
        return out
    if rarity == "rare":
        if lvl >= 56:
            return [(row["shard"], 1, 1, 0.995), ("nexus_crystal", 1, 1, 0.005)]
        return [(row["shard"], 1, 1, 1.0)]
    # epic
    if lvl >= 61:
        return [("nexus_crystal", 1, 2, 1.0)]
    if lvl >= 56:
        return [("nexus_crystal", 1, 1, 1.0)]
    return [(row["shard"], 2, 4, 1.0)]


def disenchant(character, item, rng=None):
    """Break an item from the character's bags into materials. -> (ok, message, [Material])."""
    ok, why = can_disenchant(character, item)
    if not ok:
        return False, why, []
    if item not in character.inventory:
        return False, "Only items in your bags can be disenchanted.", []
    rng = rng or random
    rows = outcomes(item)
    roll, acc = rng.random(), 0.0
    pick = rows[-1]
    for row in rows:
        acc += row[3]
        if roll < acc:
            pick = row
            break
    mid, lo, hi, _c = pick
    from world.gathering_manager import get_gathering_node_manager
    m = get_gathering_node_manager().make_material_instance(mid)
    if m is None:
        return False, "Nothing came of it.", []
    m.quantity = rng.randint(lo, hi)
    character.inventory.remove(item)
    character.add_material(m)
    got = f"{m.name}" + (f" x{m.quantity}" if m.quantity > 1 else "")
    return True, f"Disenchanted {item.name}: {got}.", [m]


def outcome_text(item):
    """'Strange Dust 1-2 (75%), Lesser Magic Essence 1 (20%), ...' for the screen."""
    from world.gathering_manager import get_gathering_node_manager
    gm = get_gathering_node_manager()
    parts = []
    for mid, lo, hi, chance in outcomes(item):
        name = (gm.get_material_def(mid) or {}).get("name", mid)
        n = f"{lo}" if lo == hi else f"{lo}-{hi}"
        pct = f"{chance * 100:.1f}".rstrip("0").rstrip(".")
        parts.append(f"{name} {n}" + ("" if chance >= 1 else f" ({pct}%)"))
    return ", ".join(parts)


def rods():
    return list(data().get("rods", []))
