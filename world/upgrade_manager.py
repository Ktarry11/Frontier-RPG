"""
Upgrade kits - Blacksmithing's own gear-improvement mechanic (Oct 2026).
No real WoW precedent exists for this (WoW has no "upgrade kit" item that
bumps an item's rarity in place) - this is an original Frontier mechanic,
confirmed directly with Kyle rather than guessed at, and corrected once
after the first version was built:

  "white will improve to green with kits, green to blue"  - moves an item
  UP the EXISTING rarity ladder (poor/common/uncommon/rare/epic/legendary,
  data/items/rarity.json), not a separate parallel tier system.

  "Only crafted" - gated to Item.is_crafted=True. A procedural drop or
  quest reward at the exact same rarity cannot be upgraded, even though
  nothing about rarity itself distinguishes them - is_crafted is the only
  signal that makes an item eligible.

  CORRECTION (Kyle, after the first version tied kits to a fixed rarity
  jump - "one kit per jump, 2 kits to max out"): "You use the same kit
  twice. Like copper kit only upgrades copper stuff. If I make armor with
  a certain type of cloth, we use that kit to upgrade it." A kit is tied
  to the MATERIAL an item was crafted from (Item.crafting_material, e.g.
  "copper", "bronze"), not to a specific rarity transition - the SAME
  Copper kit is used again and again on a Copper item as it keeps moving
  up the ladder, one rank at a time: "Even after two upgrades the item
  will only go up one rank. Like an uncommon will only go to rare" - i.e.
  one kit APPLICATION is always exactly one rank, computed from whatever
  rarity the item currently sits at, not a fixed from->to pair.

  "Stats are just improved, usually by 1 to 2 at lower levels and more at
  higher. I want crafting to be viable for end game" + "Boost every
  existing stat" - every stat the item ALREADY has goes up together (no
  new stat lines, no player choice of which to boost). The bump reuses
  rarity.json's own stat_budget_multiplier RATIO between the item's
  current tier and the next one up (e.g. uncommon/common = 1.3) rather
  than a new hand-picked number - this guarantees "more at higher item
  level" for free (a bigger base stat produces a bigger absolute bump
  from the same percentage) without inventing a second balance curve
  alongside the one LootGenerator already tunes.

  "let's just start with copper and bronze to lvl 75 to test the system"
  - only Copper and Bronze material tiers have real kits/gear right now
  (40 total ores/herbs exist - more tiers are coming once crafting
  expands further; MATERIAL_KITS below is deliberately just these two).
"""
import json
import math
from pathlib import Path


#: material_id (the upgrade kit consumed) -> the Item.crafting_material
#: tag it applies to. Kyle: "copper kit only upgrades copper stuff" - a
#: kit never cares what rarity the item is currently at, only what
#: material it was made from. Adding a new material tier later (Silver
#: gear, a Tailoring cloth tier, etc.) is just one more entry here plus a
#: matching recipe that crafts the kit and tags its gear with that same
#: tier string - nothing else in this module needs to change.
MATERIAL_KITS = {
    "upgrade_kit_copper": "copper",
    "upgrade_kit_bronze": "bronze",
}


def _rarity_order():
    """The real rarity ladder, in real low->high order, read directly
    from data/items/rarity.json's own key order rather than a second
    hardcoded list that could drift out of sync with it ("quest" is
    excluded - it's not a point on the upgrade ladder, real items never
    sit at quest-item rarity)."""
    rarity_file = Path(__file__).parent.parent / "data" / "items" / "rarity.json"
    with open(rarity_file, 'r') as f:
        tiers = json.load(f)["rarity_tiers"]
    return [name for name in tiers.keys() if name != "quest"]


def _next_rarity(current_rarity):
    """The one rarity rank above current_rarity, or None if current_rarity
    is already the top of the ladder (or isn't a recognized rarity at
    all)."""
    order = _rarity_order()
    if current_rarity not in order:
        return None
    idx = order.index(current_rarity)
    if idx + 1 >= len(order):
        return None
    return order[idx + 1]


def next_rarity_for(current_rarity):
    """Public wrapper around _next_rarity - the UI needs to display what
    rank a kit would move an item TO before the player applies it (e.g.
    "Common -> Uncommon"), without reaching into a private-named
    helper."""
    return _next_rarity(current_rarity)


def get_kit_for_item(item):
    """The one upgrade kit material_id that matches this item's
    crafting_material tag, or None if the item isn't crafted, has no
    tag, or is already at the very top of the rarity ladder (nothing
    left to upgrade INTO, whatever kit you hold)."""
    if not item.is_crafted or not item.crafting_material:
        return None
    if _next_rarity(item.rarity) is None:
        return None
    for kit_id, material_tier in MATERIAL_KITS.items():
        if material_tier == item.crafting_material:
            return kit_id
    return None


def can_upgrade(character, item, kit_material_id):
    """True only if: the kit is a real, known kit; the item was crafted
    from the material that kit targets (Kyle: "copper kit only upgrades
    copper stuff"); the item was produced by a real crafting profession
    (is_crafted - Kyle: "Only crafted"); the item isn't already at the
    top of the rarity ladder; and the character actually holds the
    kit."""
    material_tier = MATERIAL_KITS.get(kit_material_id)
    if material_tier is None:
        return False
    if not item.is_crafted:
        return False
    if item.crafting_material != material_tier:
        return False
    if _next_rarity(item.rarity) is None:
        return False
    return character.get_material_quantity(kit_material_id) >= 1


def upgrade_item(character, item, kit_material_id):
    """Consume one kit and upgrade `item` in place by exactly one rarity
    rank, from wherever it currently sits (mutates and returns it -
    there's no reason to construct a new Item identity for what is
    conceptually the same physical sword getting better, and mutating in
    place means every existing reference to this item - equipped slot,
    inventory list - automatically sees the upgrade with no swap-out
    step needed anywhere else in the codebase).

    Returns the same `item` on success, or None on failure (can_upgrade's
    checks re-run here rather than trusted from the caller, same
    defensive convention as SmeltingManager.smelt/BlacksmithingManager.craft -
    guarantees the kit is never consumed on a failed upgrade attempt).
    """
    if not can_upgrade(character, item, kit_material_id):
        return None

    from_rarity = item.rarity
    to_rarity = _next_rarity(from_rarity)
    if to_rarity is None:
        return None  # pragma: no cover - can_upgrade already checked this

    if not character.consume_material(kit_material_id, 1):
        return None

    rarity_file = Path(__file__).parent.parent / "data" / "items" / "rarity.json"
    with open(rarity_file, 'r') as f:
        rarity_tiers = json.load(f)["rarity_tiers"]

    old_mult = rarity_tiers[from_rarity]["stat_budget_multiplier"]
    new_mult = rarity_tiers[to_rarity]["stat_budget_multiplier"]
    # old_mult is never 0 for any tier an item can actually start at
    # (poor/common/uncommon/rare/epic all have real nonzero multipliers
    # in rarity.json) - the only 0-multiplier tier is "quest", which
    # _rarity_order() already excludes and no crafted item would ever be
    # tagged with anyway.
    bump_ratio = new_mult / old_mult

    item.rarity = to_rarity

    # Every stat the item ALREADY has goes up by bump_ratio - no new
    # stat lines added, no player choice of which to boost (Kyle: "Boost
    # every existing stat"). math.ceil rather than int/round so even a
    # tiny stat (e.g. a single +1) always goes up by AT LEAST 1 - a
    # straight int() truncation would let 1 * 1.3 = 1.3 round back down
    # to 1, silently failing the entire point of an "upgrade" kit on
    # exactly the low-level gear Kyle called out ("1 to 2 at lower
    # levels"). A stat that is legitimately 0 (most slots roll zero
    # primary/secondary stats at low rarity/item_level - see
    # LootGenerator) correctly stays 0: there is nothing to "boost by at
    # least 1" on a stat the item never had in the first place, since
    # this only touches stats already present in the dict.
    item.primary_stats = {
        stat: math.ceil(value * bump_ratio)
        for stat, value in item.primary_stats.items()
    }
    item.secondary_stats = {
        stat: math.ceil(value * bump_ratio)
        for stat, value in item.secondary_stats.items()
    }
    if item.armor_value:
        item.armor_value = math.ceil(item.armor_value * bump_ratio)
    if item.weapon_damage_min:
        item.weapon_damage_min = math.ceil(item.weapon_damage_min * bump_ratio)
    if item.weapon_damage_max:
        item.weapon_damage_max = math.ceil(item.weapon_damage_max * bump_ratio)
    if item.block_value:
        item.block_value = math.ceil(item.block_value * bump_ratio)

    return item
