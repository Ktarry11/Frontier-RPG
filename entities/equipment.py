"""
Equipment manager. Owns the character's 16 gear slots and aggregates
equipped items' stat bonuses for Character to apply on top of base stats.
"""

_weapon_hand_cache = None


def _load_weapon_type_hand(weapon_type):
    """The "hand" field (e.g. "one_hand", "two_hand", "ranged") for a
    weapon_type from data/items/weapon_types.json, cached after first
    load since this file is static content. Returns None for an unknown
    weapon_type rather than raising, so a data typo fails soft (treated
    as not two-handed) instead of crashing every equip call."""
    global _weapon_hand_cache
    if _weapon_hand_cache is None:
        import json
        from pathlib import Path
        path = Path(__file__).parent.parent / "data" / "items" / "weapon_types.json"
        try:
            with open(path, "r") as f:
                data = json.load(f).get("weapon_types", {})
            _weapon_hand_cache = {k: v.get("hand") for k, v in data.items()}
        except Exception:
            _weapon_hand_cache = {}
    return _weapon_hand_cache.get(weapon_type)


EQUIPMENT_SLOTS = [
    "head", "neck", "shoulder", "back", "chest", "wrist", "hands",
    "waist", "legs", "feet", "ring1", "ring2", "trinket1", "trinket2",
    "main_hand", "off_hand", "ranged",
    "bag1", "bag2", "bag3", "bag4",
]

#: The 4 bag slots specifically, for callers that need to sum bag capacity
#: or render just the bag row without walking all 21 EQUIPMENT_SLOTS.
BAG_SLOTS = ["bag1", "bag2", "bag3", "bag4"]

#: Base backpack size before any bags are equipped - Kyle's spec: "Start
#: 24 spots with 4 additional bag spots" (WoW-style: a base bag everyone
#: has, plus 4 equippable bag slots that each add their own capacity on
#: top). See Character.inventory_capacity for how bag_capacity gets summed
#: on top of this.
BASE_INVENTORY_CAPACITY = 24

#: Paired slots that share one generic identity on the item itself. Loot
#: generation stamps a ring item's slot as the generic "ring" (not "ring1"
#: or "ring2" specifically) so a dropped ring can go into WHICHEVER of the
#: two ring slots is open - previously each ring was generated already
#: hardcoded to ring1 or ring2, so a ring1-flavored drop could never fill
#: an empty ring2 (or vice versa), which is exactly the "can only equip
#: one" bug: two ring1 items would just keep overwriting each other while
#: ring2 sat permanently empty.
PAIRED_SLOTS = {
    "ring": ["ring1", "ring2"],
    "trinket": ["trinket1", "trinket2"],
    "bag": BAG_SLOTS,
}


class Equipment:
    """Tracks equipped items across all 16 slots for a character."""

    def __init__(self):
        self.slots = {slot: None for slot in EQUIPMENT_SLOTS}

    def _resolve_slot(self, item):
        """Map a generic paired-slot item (ring/trinket) to a concrete slot.

        Prefers an empty slot in the pair; if both are already filled,
        falls back to the first slot in the pair (so equipping still
        succeeds and displaces whatever was there, rather than silently
        failing). Non-paired items (everything else) pass through
        unchanged.
        """
        pair = PAIRED_SLOTS.get(item.slot)
        if not pair:
            return item.slot
        for slot in pair:
            if self.slots.get(slot) is None:
                return slot
        return pair[0]

    def equip(self, item):
        """
        Equip an item into its slot. Returns (previous_item_in_slot,
        displaced_item_or_None) - the second element is only ever
        non-None when equipping displaces a DIFFERENT slot's item (the
        2H-weapon-vs-offhand interaction below), not the normal
        same-slot swap already covered by the first element.

        Two-handed weapons clear the off_hand slot when equipped into
        main_hand. The REVERSE direction also has to be enforced -
        equipping something into off_hand while a two-handed weapon is
        already sitting in main_hand - or a staff/polearm/2H weapon and
        a separate off-hand item could sit equipped simultaneously,
        which real WoW never allows and which silently doubles that
        item's stat contribution. This was a real, reproducible bug
        (Kyle, 2026-09-06): a staff (two_hand) plus an off_hand item
        could both be equipped at once, since only the main_hand-equip
        direction was ever guarded.
        """
        target_slot = self._resolve_slot(item)
        if target_slot not in self.slots:
            return None

        # Equipping INTO off_hand while a 2H weapon already occupies
        # main_hand: the 2H weapon has to go, since it can't coexist
        # with anything in off_hand. Mirrors the main_hand-clears-
        # off_hand direction below, just the other way around.
        if target_slot == "off_hand":
            current_main = self.slots.get("main_hand")
            if current_main is not None and self._is_two_handed(current_main):
                self.slots["main_hand"] = None
                previous = self.slots[target_slot]
                self.slots[target_slot] = item
                return previous, current_main

        previous = self.slots[target_slot]
        self.slots[target_slot] = item

        # 2H weapons: clear off_hand since it can't be used alongside a 2H main hand
        if target_slot == "main_hand" and item.weapon_type and self._is_two_handed(item):
            displaced_offhand = self.slots["off_hand"]
            self.slots["off_hand"] = None
            return previous, displaced_offhand

        return previous, None

    def unequip(self, slot):
        """Remove and return the item in a slot (or None)."""
        if slot not in self.slots:
            return None
        item = self.slots[slot]
        self.slots[slot] = None
        return item

    def get_equipped(self, slot):
        return self.slots.get(slot)

    def get_all_equipped(self):
        """Return list of all non-empty equipped items."""
        return [item for item in self.slots.values() if item is not None]

    def get_total_stat_bonuses(self):
        """Sum all primary + secondary stat bonuses across every equipped item."""
        totals = {}
        for item in self.get_all_equipped():
            for stat, value in item.get_all_stat_bonuses().items():
                totals[stat] = totals.get(stat, 0) + value
        return totals

    def get_total_armor(self):
        """Sum armor_value across all equipped items."""
        return sum(item.armor_value for item in self.get_all_equipped())

    def get_shield_armor(self):
        """Armor value contributed by the equipped shield specifically (0 if
        no shield equipped). A shield is identified as the off_hand item
        having a nonzero block_value - this engine has no dedicated
        item_type="shield" field, but block_value only ever comes from
        shields by convention (see get_total_block_value), so an off_hand
        item with block_value > 0 IS a shield. Needed for Shield
        Specialization (Shaman Tank: "+10% Armor from your equipped Shield
        per rank") which must scale ONLY the shield's own armor contribution,
        not a player's full armor total from chest/legs/etc - get_total_armor()
        can't isolate that.
        """
        item = self.slots.get("off_hand")
        if item is not None and getattr(item, "block_value", 0) > 0:
            return item.armor_value
        return 0

    def get_total_block_value(self):
        """Sum block_value across all equipped items (shields)."""
        return sum(item.block_value for item in self.get_all_equipped())

    def get_bag_capacity(self):
        """Sum bag_capacity across all 4 equipped bags. 0 if no bags
        equipped - Character.inventory_capacity adds this on top of
        BASE_INVENTORY_CAPACITY."""
        return sum(getattr(self.slots.get(slot), "bag_capacity", 0) or 0
                   for slot in BAG_SLOTS)

    def get_main_hand_weapon(self):
        """Return the equipped main_hand Item, or None if unarmed."""
        return self.slots.get("main_hand")

    def get_ranged_weapon(self):
        """Return the equipped ranged Item (wand/totem), or None."""
        return self.slots.get("ranged")

    def _is_two_handed(self, item):
        """True if item.weapon_type is registered as hand="two_hand" in
        data/items/weapon_types.json - reads the real data-driven flag
        instead of a hardcoded string list, which had already drifted
        stale once (missing "polearm" the moment it was added as a new
        2H type this session - exactly the kind of silent gap a manually
        maintained list is guaranteed to hit again as more weapon types
        get added)."""
        wtype = getattr(item, "weapon_type", None)
        if not wtype:
            return False
        return _load_weapon_type_hand(wtype) == "two_hand"

    def to_dict(self):
        """Serialize equipped items for saving."""
        return {
            slot: (item.to_dict() if item else None)
            for slot, item in self.slots.items()
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize equipped items from save data."""
        from entities.item import Item
        equipment = cls()
        for slot, item_data in (data or {}).items():
            if slot in equipment.slots and item_data:
                equipment.slots[slot] = Item.from_dict(item_data)
        return equipment
