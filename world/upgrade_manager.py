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

  CORRECTION 1 (Kyle, after the first version tied kits to a fixed
  rarity jump - "one kit per jump, 2 kits to max out"): "You use the same
  kit twice. Like copper kit only upgrades copper stuff. If I make armor
  with a certain type of cloth, we use that kit to upgrade it." A kit is
  tied to the MATERIAL an item was crafted from (Item.crafting_material,
  e.g. "copper", "bronze"), not to a specific rarity transition.

  CORRECTION 2 (Kyle, after correction 1 implied the same kit could be
  applied indefinitely to keep climbing the ladder): "Yes ONE rank jump,
  but two improvements." A material's kit only ever moves an item ONE
  rarity rank total, no matter how many times it's applied - but getting
  there takes exactly TWO applications, each with a different effect:
    1st application: rarity moves up one rank AND every existing stat
    gets the normal ratio-based bump (same math as before).
    2nd application: rarity does NOT move again - it's already at its
    one-and-only rank - but stats bump AGAIN, by 1.5x the exact amount
    the FIRST application added (not 1.5x the current stat value).
    Kyle's own example: "if first upgrade...gives +1 stam and +1
    str...goes white to green. Then the next upgrade would be 1.5 stam
    and 1.5 str and green stays green." A 3rd application is simply not
    possible - Item.upgrade_count caps at 2.
  This is why the first application's per-stat delta is recorded on the
  item (Item.upgrade_deltas) rather than only mutating the stat in
  place: the second application needs that original delta to compute
  1.5x of it, and re-deriving a fresh ratio bump a second time would
  double-count the rarity jump that already happened once and for all
  on application 1.

  "Stats are just improved, usually by 1 to 2 at lower levels and more at
  higher. I want crafting to be viable for end game" + "Boost every
  existing stat" - every stat the item ALREADY has goes up together on
  the first application (no new stat lines, no player choice of which to
  boost). That bump reuses rarity.json's own stat_budget_multiplier RATIO
  between the item's current tier and the next one up (e.g. uncommon/
  common = 1.3) rather than a new hand-picked number - this guarantees
  "more at higher item level" for free (a bigger base stat produces a
  bigger absolute bump from the same percentage) without inventing a
  second balance curve alongside the one LootGenerator already tunes.

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


#: Maximum times any kit can ever be applied to one item - exactly 2 per
#: Kyle's "ONE rank jump, but two improvements": application 1 does the
#: rank+stat bump, application 2 does a stats-only bump, and that's the
#: end of the line for that item, permanently.
MAX_UPGRADE_COUNT = 2


def get_kit_for_item(item):
    """The one upgrade kit material_id that matches this item's
    crafting_material tag, or None if the item isn't crafted, has no
    tag, or has already used up both its upgrade applications
    (Item.upgrade_count >= MAX_UPGRADE_COUNT - the material's single
    rank jump is already fully realized, whatever kit you hold)."""
    if not item.is_crafted or not item.crafting_material:
        return None
    if item.upgrade_count >= MAX_UPGRADE_COUNT:
        return None
    for kit_id, material_tier in MATERIAL_KITS.items():
        if material_tier == item.crafting_material:
            return kit_id
    return None


def can_upgrade(character, item, kit_material_id):
    """True only if: the kit is a real, known kit; the item was crafted
    from the material that kit targets (Kyle: "copper kit only upgrades
    copper stuff"); the item was produced by a real crafting profession
    (is_crafted - Kyle: "Only crafted"); the item hasn't already used
    both its upgrade applications; and the character actually holds the
    kit."""
    material_tier = MATERIAL_KITS.get(kit_material_id)
    if material_tier is None:
        return False
    if not item.is_crafted:
        return False
    if item.crafting_material != material_tier:
        return False
    if item.upgrade_count >= MAX_UPGRADE_COUNT:
        return False
    return character.get_material_quantity(kit_material_id) >= 1


def _stat_dict_delta(old_stats, bump_ratio):
    """{stat: new_value} and {stat: delta} for applying bump_ratio to
    every entry in old_stats via math.ceil (see upgrade_item's docstring
    for why ceil, not round/int)."""
    new_stats = {}
    deltas = {}
    for stat, value in old_stats.items():
        new_value = math.ceil(value * bump_ratio)
        new_stats[stat] = new_value
        deltas[stat] = new_value - value
    return new_stats, deltas


def upgrade_item(character, item, kit_material_id):
    """Consume one kit and apply ONE of the item's two possible upgrade
    applications (mutates and returns it - there's no reason to
    construct a new Item identity for what is conceptually the same
    physical sword getting better, and mutating in place means every
    existing reference to this item - equipped slot, inventory list -
    automatically sees the upgrade with no swap-out step needed anywhere
    else in the codebase).

    1ST application (item.upgrade_count == 0 going in): rarity moves up
    exactly one rank, AND every existing stat gets the normal
    ratio-based bump (rarity.json's stat_budget_multiplier ratio between
    the old and new tier). The exact per-stat delta this produces is
    recorded on item.upgrade_deltas.

    2ND application (item.upgrade_count == 1 going in): rarity does NOT
    move again - Kyle: "green stays green" - but every stat that got a
    delta on the first application bumps AGAIN, by 1.5x that SAME
    original delta (not 1.5x the current value, and not a fresh ratio
    bump - Kyle's own example: first +1 stam/+1 str, second +1.5
    stam/+1.5 str). math.ceil is applied to the 1.5x delta itself so a
    +1 delta's 1.5x (=1.5) always becomes a real +2, never silently
    rounding back down to +1.

    Returns the same `item` on success, or None on failure (can_upgrade's
    checks re-run here rather than trusted from the caller, same
    defensive convention as SmeltingManager.smelt/BlacksmithingManager.craft -
    guarantees the kit is never consumed on a failed upgrade attempt).
    """
    if not can_upgrade(character, item, kit_material_id):
        return None

    if not character.consume_material(kit_material_id, 1):
        return None

    if item.upgrade_count == 0:
        from_rarity = item.rarity
        to_rarity = _next_rarity(from_rarity)
        if to_rarity is None:
            # No real crafted recipe currently outputs anything high
            # enough on the ladder to hit this - defensive only.
            return None

        rarity_file = Path(__file__).parent.parent / "data" / "items" / "rarity.json"
        with open(rarity_file, 'r') as f:
            rarity_tiers = json.load(f)["rarity_tiers"]

        old_mult = rarity_tiers[from_rarity]["stat_budget_multiplier"]
        new_mult = rarity_tiers[to_rarity]["stat_budget_multiplier"]
        # old_mult is never 0 for any tier a crafted item can actually
        # start at (poor/common/uncommon/rare/epic all have real nonzero
        # multipliers in rarity.json) - the only 0-multiplier tier is
        # "quest", which _rarity_order() already excludes.
        bump_ratio = new_mult / old_mult

        item.rarity = to_rarity

        # Every stat the item ALREADY has goes up by bump_ratio - no new
        # stat lines added, no player choice of which to boost (Kyle:
        # "Boost every existing stat"). math.ceil rather than int/round
        # so even a tiny stat (e.g. a single +1) always goes up by AT
        # LEAST 1 - a straight int() truncation would let 1 * 1.3 = 1.3
        # round back down to 1, silently failing the entire point of an
        # "upgrade" kit on exactly the low-level gear Kyle called out
        # ("1 to 2 at lower levels"). A stat that is legitimately 0
        # (most slots roll zero primary/secondary stats at low
        # rarity/item_level - see LootGenerator) correctly stays 0:
        # there is nothing to "boost by at least 1" on a stat the item
        # never had in the first place, since this only touches stats
        # already present in the dict.
        new_primary, primary_deltas = _stat_dict_delta(item.primary_stats, bump_ratio)
        new_secondary, secondary_deltas = _stat_dict_delta(item.secondary_stats, bump_ratio)
        item.primary_stats = new_primary
        item.secondary_stats = new_secondary

        deltas = {"primary_stats": primary_deltas, "secondary_stats": secondary_deltas}
        for field in ("armor_value", "weapon_damage_min", "weapon_damage_max", "block_value"):
            old_value = getattr(item, field)
            if old_value:
                new_value = math.ceil(old_value * bump_ratio)
                setattr(item, field, new_value)
                deltas[field] = new_value - old_value
            else:
                deltas[field] = 0

        item.upgrade_deltas = deltas
        item.upgrade_count = 1

    else:
        # Second (and final) application - rarity frozen, stats bump
        # again by exactly 1.5x the deltas the FIRST application
        # recorded. item.upgrade_deltas is guaranteed set here since
        # upgrade_count can only reach 1 via the branch above.
        deltas = item.upgrade_deltas or {}

        for stat, delta in deltas.get("primary_stats", {}).items():
            if stat in item.primary_stats:
                item.primary_stats[stat] += math.ceil(delta * 1.5)
        for stat, delta in deltas.get("secondary_stats", {}).items():
            if stat in item.secondary_stats:
                item.secondary_stats[stat] += math.ceil(delta * 1.5)
        for field in ("armor_value", "weapon_damage_min", "weapon_damage_max", "block_value"):
            delta = deltas.get(field, 0)
            if delta:
                setattr(item, field, getattr(item, field) + math.ceil(delta * 1.5))

        item.upgrade_count = 2
        # upgrade_deltas has done its job - clear it so nothing could
        # ever read it for a (nonexistent) 3rd application.
        item.upgrade_deltas = None

    return item
