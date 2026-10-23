"""
LootItem - a non-equippable item that lives in the same
Character.inventory list as real gear (Item) and consumables, so it goes
through the exact same bag capacity, loot, and vendor-sell plumbing
without a fourth inventory type. Kyle's call: "Monster drops and quest
items go in inventory. We have a bag system."

Originally built as QuestItem, quest-only. Kyle's follow-up: "we will
eventually need stuff like vendor trash (grey) and crafting materials
too, and quest items etc" - merged into one class with a `category`
field rather than three separate near-duplicate classes, since all
three are the same shape (stackable, non-equippable, non-usable) and
only differ in sellability and rarity color:

- "quest": quest turn-in objectives ("10 Wolf Pelts"), never sellable,
  ruby-red "quest" rarity tier (data/items/rarity.json).
- "material": crafting/profession materials (ore, herbs, etc. - see
  data/items/materials.json), sellable, real rarity tier from that data.
- "trash": pure vendor filler with no other purpose, sellable, always
  "poor" (grey) rarity - the classic "vendor trash" concept.

Distinct from entities.item.Item (equippable gear - has slot/armor_type/
weapon_type) and entities.consumable.Consumable (has an in-combat/
out-of-combat use effect). A LootItem has neither - it can't be equipped
and can't be "used", it exists purely to be carried and either handed to
a quest giver, used at a future crafting station, or sold to a vendor.
"""


class LootItem:
    """A stackable, non-equippable item - quest turn-in objectives,
    crafting materials, or vendor trash, distinguished by `category`."""

    #: Explicit marker so inventory/equip code can distinguish this from
    #: real gear with a single attribute check instead of relying on
    #: missing armor_type/weapon_type to fail closed by accident.
    is_gear = False

    #: Rarity tier per category - quest items never sell (is_sellable
    #: below handles that gate), materials/trash use real tiers from
    #: data/items/rarity.json so they render through the same
    #: get_rarity_color() path as gear.
    _CATEGORY_RARITY = {
        "quest": "quest",
        "material": "common",   # overridden per-item via rarity= if a specific material has a real tier
        "trash": "poor",
    }

    def __init__(self, item_id, name, category="quest", description="", icon_id=None,
                 stack_limit=20, quest_id=None, sell_price=0, rarity=None, starts_quest_id=None):
        if category not in ("quest", "material", "trash"):
            raise ValueError(f"LootItem category must be quest/material/trash, got {category!r}")
        self.item_id = item_id
        self.name = name
        self.category = category
        self.description = description
        self.icon_id = icon_id
        self.stack_limit = stack_limit
        #: Quest items are never sellable (Kyle's explicit ruling) -
        #: materials and trash both are, since selling filler/materials
        #: to vendors is normal. Checked via is_sellable rather than
        #: sell_price == 0, since 0 is also a legitimate (if unusual)
        #: sell price for real gear and shouldn't double as "can't sell".
        self.is_sellable = category != "quest"
        self.sell_price = 0 if category == "quest" else sell_price
        #: rarity is explicit-or-category-default rather than always
        #: forced to the category default, so a real material (e.g. a
        #: rare ore) can carry its actual data/items/materials.json
        #: rarity instead of every material flattening to "common".
        self.rarity = rarity or self._CATEGORY_RARITY[category]
        #: Which quest this item exists for, if any - lets the quest
        #: turn-in flow find and remove the right stack without string-
        #: matching on name. Only meaningful for category="quest"; None
        #: for materials/trash and for generic quest collectibles not
        #: tied to a specific quest.
        self.quest_id = quest_id
        #: A quest-STARTER item (a monster drop that begins a quest): clicking it in the bag opens that quest's
        #: offer dialog (giver id "item:<item_id>").  None for ordinary items.
        self.starts_quest_id = starts_quest_id
        self.quantity = 1

    def get_rarity_color(self):
        """Every real Item in the bag panel is drawn with
        item.get_rarity_color() (see ui/screens/inventory_screen.py) -
        LootItem needs the same method so it renders through the exact
        same loop instead of the UI needing a special case for "items
        with no rarity". Reads the real tier color from
        data/items/rarity.json rather than hardcoding RGB tuples here,
        so a future palette pass only has to touch the JSON."""
        try:
            import json
            from pathlib import Path
            path = Path(__file__).parent.parent / "data" / "items" / "rarity.json"
            with open(path, "r") as f:
                tiers = json.load(f)["rarity_tiers"]
            color = tiers.get(self.rarity, {}).get("color")
            if color:
                return tuple(color)
        except (OSError, KeyError, ValueError):
            pass
        # Fail-soft fallback if the JSON is ever missing/malformed.
        fallback = {"quest": (200, 30, 45), "trash": (150, 150, 150)}
        return fallback.get(self.category, (255, 255, 255))

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "icon_id": self.icon_id,
            "stack_limit": self.stack_limit,
            "quest_id": self.quest_id,
            "sell_price": self.sell_price,
            "rarity": self.rarity,
            "starts_quest_id": self.starts_quest_id,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data):
        obj = cls(
            item_id=data["item_id"],
            name=data["name"],
            category=data.get("category", "quest"),
            description=data.get("description", ""),
            icon_id=data.get("icon_id"),
            stack_limit=data.get("stack_limit", 20),
            quest_id=data.get("quest_id"),
            sell_price=data.get("sell_price", 0),
            rarity=data.get("rarity"),
            starts_quest_id=data.get("starts_quest_id"),
        )
        obj.quantity = data.get("quantity", 1)
        return obj


def count_loot_items(character, item_id):
    """Total quantity of a given loot item across every stack in a
    character's inventory. Items COULD end up split across multiple
    stack entries (e.g. one from a kill, one handed over by another
    party member) rather than always merging into one - this sums all
    of them rather than assuming a single stack, so progress tracking
    can't silently undercount."""
    return sum(
        item.quantity for item in character.inventory
        if isinstance(item, LootItem) and item.item_id == item_id
    )


def remove_loot_items(character, item_id, amount):
    """Remove `amount` of a loot item from a character's inventory,
    across as many stacks as needed. Returns True if the full amount was
    available and removed, False (with NO partial removal) if the
    character didn't have enough - a quest turn-in should never leave
    someone with 3 of 10 wolf pelts still in their bag after "handing
    over" all 10."""
    if count_loot_items(character, item_id) < amount:
        return False

    remaining = amount
    for item in list(character.inventory):
        if remaining <= 0:
            break
        if isinstance(item, LootItem) and item.item_id == item_id:
            take = min(item.quantity, remaining)
            item.quantity -= take
            remaining -= take
            if item.quantity <= 0:
                character.inventory.remove(item)
    return True


def add_loot_item(character, item_id, name, category="quest", amount=1, description="",
                   icon_id=None, quest_id=None, sell_price=0, rarity=None, starts_quest_id=None):
    """Add `amount` of a loot item to a character's inventory, stacking
    onto an existing stack for the same item_id when there's room rather
    than always creating a new bag slot. Returns True if all of it fit,
    False if the bag was full and some/all couldn't be added - mirrors
    Character.add_to_inventory's "caller must check the return value"
    contract, since a full bag during a kill-quest grind or a mining run
    is a completely normal thing to hit, not an edge case."""
    remaining = amount

    # Top up any existing stack(s) for this item_id first.
    for item in character.inventory:
        if remaining <= 0:
            break
        if isinstance(item, LootItem) and item.item_id == item_id:
            room = item.stack_limit - item.quantity
            if room > 0:
                add_here = min(room, remaining)
                item.quantity += add_here
                remaining -= add_here

    # Whatever didn't fit into an existing stack needs new bag slots.
    while remaining > 0:
        if len(character.inventory) >= character.inventory_capacity:
            return False
        new_stack = LootItem(item_id, name, category=category, description=description,
                              icon_id=icon_id, quest_id=quest_id, sell_price=sell_price, rarity=rarity,
                              starts_quest_id=starts_quest_id)
        take = min(new_stack.stack_limit, remaining)
        new_stack.quantity = take
        character.inventory.append(new_stack)
        remaining -= take

    return True


# ---------- Back-compat aliases (Kyle's merge decision, this session) ----------
# QuestItem/add_quest_item/count_quest_items/remove_quest_items were the
# original quest-only names before this class was generalized to also
# cover materials and vendor trash. Every NEW call site should use
# LootItem/add_loot_item/count_loot_items/remove_loot_items directly and
# pass category="quest" explicitly - these aliases exist only so any
# reference elsewhere in the codebase (or a stale save-file code path)
# that still says "QuestItem" keeps working without a hunt-and-fix pass
# blocking this session's other work.
QuestItem = LootItem


def add_quest_item(character, item_id, name, amount=1, description="", icon_id=None, quest_id=None):
    return add_loot_item(character, item_id, name, category="quest", amount=amount,
                          description=description, icon_id=icon_id, quest_id=quest_id)


def count_quest_items(character, item_id):
    return count_loot_items(character, item_id)


def remove_quest_items(character, item_id, amount):
    return remove_loot_items(character, item_id, amount)
