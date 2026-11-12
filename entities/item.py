"""
Item class. Represents a single equippable item instance.
Items are generated procedurally by loot_generator.py using JSON-defined
armor types, weapon types, stat templates, rarity tiers, and slot weights
(see data/items/*.json and docs/EQUIPMENT_SYSTEM_DESIGN.md).
"""


def whole(value):
    """Round half up to a whole number. Python's round() sends 0.5 to 0 and 2.5 to 2."""
    import math
    return int(math.floor(float(value) + 0.5))


def whole_stats(primary_stats, secondary_stats, armor_value=0):
    """(primary, secondary, armor) with every stat a whole number and bonus armour folded in.

    Kyle, 10 Nov, for the second time: "i asked you to remove these partial values from
    gear....still havent." and "when an item gets +armor - it should not appear as a bonus
    stat but it should just go into the armor."

    - A stat is a whole number. "+0.3% Crit" is not a thing an item says; a stat that rounds
      to nothing is not on the item.
    - "armor" as a stat is added to the item's armour value and removed from the stat list, so
      the card reads one line - "207 Armor" - the way the real one does. Character armour is
      the sum of both either way, so nothing about how hard anyone is to hit changes.

    Non-numbers are passed through untouched (nothing stores one today; it would be a bug
    elsewhere and not this function's to hide).
    """
    armor = armor_value or 0
    out = []
    for group in (primary_stats, secondary_stats):
        clean = {}
        for stat, value in (group or {}).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                clean[stat] = value
                continue
            if stat == "armor":
                armor += value
                continue
            value = whole(value)
            if value != 0:
                clean[stat] = value
        out.append(clean)
    return out[0], out[1], whole(armor)


class Item:
    """A single equippable item instance."""

    def __init__(self, item_id, name, slot, item_level, rarity,
                 armor_type=None, weapon_type=None, stat_template=None,
                 primary_stats=None, secondary_stats=None, armor_value=0,
                 required_level=1, sell_price=0, flavor_text="",
                 set_id=None, sockets=None, enchant_id=None,
                 weapon_damage_min=0, weapon_damage_max=0, attack_speed=0.0,
                 block_value=0, bag_capacity=0, icon_id=None,
                 is_crafted=False, crafting_material=None,
                 upgrade_count=0, upgrade_deltas=None, attachment=None,
                 recipe_id=None, recipe_profession=None, vendor_price=None,
                 proc=None):
        self.item_id = item_id
        self.name = name
        self.slot = slot  # e.g. "chest", "main_hand", "ring1", "bag1"-"bag4"
        self.item_level = item_level
        self.rarity = rarity  # "common", "uncommon", "rare", "epic", (poor/legendary reserved)

        # Armor items carry armor_type; weapons carry weapon_type. One will be None.
        # Bag items use armor_type="bag" - not on ARMOR_LADDER, so
        # can_wear_armor_type() in proficiency.py fails open and any class
        # can equip any bag, same as accessories. See entities/equipment.py
        # BAG_SLOTS docstring for the rest of the bag system.
        self.armor_type = armor_type
        self.weapon_type = weapon_type

        # stat_template determines which core stats this item rolls
        # (e.g. "str_physical", "int_caster") - independent of armor_type/weapon_type
        self.stat_template = stat_template

        # WHOLE NUMBERS, AND ARMOUR IS ARMOUR. Every item in the game is built through here -
        # generated, hand-authored, crafted, loaded from a save - so this is the one place the
        # two rules can be enforced for all of them. See whole_stats below.
        self.primary_stats, self.secondary_stats, self.armor_value = whole_stats(
            primary_stats, secondary_stats, armor_value)

        # Weapon combat stats (0 for non-weapons and shields).
        # weapon_damage_min/max is the per-hit damage roll range at 1.0x speed;
        # attack_speed is seconds-per-hit (WoW convention: lower = faster, e.g. Dagger 1.7, 2H 3.4).
        # DPS = ((min+max)/2) / attack_speed
        self.weapon_damage_min = weapon_damage_min
        self.weapon_damage_max = weapon_damage_max
        self.attack_speed = attack_speed

        # Shields only: contributes directly to Character.block derived stat
        self.block_value = block_value

        # Bags only (armor_type="bag"): how many extra backpack slots this
        # bag adds while equipped. 0 for every non-bag item. See
        # Character.inventory_capacity for how this gets summed.
        self.bag_capacity = bag_capacity
        #: What a SHOP charges for this, when the catalog says so. None means "work it
        #: out from sell_price", which is what every procedurally generated item does.
        #: Bags are hand-authored and priced in data/items/bags.json, and that figure was
        #: being thrown away - generate_bag never passed it, so the shop fell back to
        #: sell_price * 4 and a 6-slot bag cost 60 copper instead of its listed price.
        #: Kyle: "we need to make bags way more expensive....6 slot bags for 60c is fuck
        #: all. a 6 slot bag should start around 10s."
        self.vendor_price = vendor_price

        # Optional: real icon art (assets/icons/bags/<icon_id>.png,
        # IconRenderer.BAG_ICON_DIR). Procedural armor/weapons don't set
        # this - they render as rarity-colored boxes with text (see
        # InventoryScreen). Bags are the one hand-authored item category
        # with real per-item art (Kyle's 13-bag icon sheet), so this field
        # exists specifically for them; None elsewhere is correctly a
        # no-op (nothing else looks it up yet).
        self.icon_id = icon_id

        self.required_level = required_level
        # ONE PRICE CURVE for all gear (entities/pricing.py). Whatever built this item used to
        # hand in its own guess - the generator item_level x 1, boss loot x 1.7, quest rewards
        # nothing at all - which is how a level 58 blue came to sell for 1s 2c.
        #   None      "price me" - quest rewards and anything else with no opinion
        #   0 or 1    deliberately worthless (starting gear, a recruit's own kit) - left alone,
        #             so nobody funds a mount by stripping new recruits
        #   more      at least the curve; a higher figure is kept, which is how an upgraded or
        #             socketed item keeps its premium through a save and load
        # Bags are hand-priced in data/items/bags.json and recipe scrolls by skill; neither is
        # gear in this sense.
        if slot != "recipe" and not recipe_id and armor_type != "bag" and not bag_capacity:
            if sell_price is None or sell_price > 1:
                from entities.pricing import gear_sell_price
                sell_price = max(int(sell_price or 0),
                                 gear_sell_price(item_level, rarity, slot, weapon_type))
        self.sell_price = int(sell_price or 0)
        self.flavor_text = flavor_text

        # Scaffolding for later phases (Section 9/10 of design doc) - unused in Phase 5
        # A StatusEffect proc dict (combat/status_effects.py, fire_proc_trigger) - what makes a
        # trinket DO something rather than sit there as a stat stick. Kyle, 10 Nov: "trinkets
        # over 50+ WILL AND MUST start to actually do stuff." Character._sync_equipment_procs
        # hangs it on the wearer as a synthetic effect while the item is equipped. None for
        # every ordinary item. Copied, so two drops of the same item never share one dict.
        self.proc = dict(proc) if proc else None

        self.set_id = set_id
        self.sockets = sockets or []
        self.enchant_id = enchant_id

        # True only for items produced by a real crafting profession
        # (Blacksmithing, Oct 2026 - Kyle: "I will want to massively
        # expand crafting"). Gates upgrade kits (world/upgrade_manager.py):
        # Kyle's explicit call - "Only crafted" - upgrade kits work on
        # Blacksmithed gear, not procedural drops or quest rewards, even
        # though those can also roll the same rarity tiers. Defaults
        # False so every existing item (procedural loot, hand-authored
        # unique_item_defs, bags) is correctly "not upgradeable" without
        # needing to touch any of those call sites.
        self.is_crafted = is_crafted

        # Which material TIER this item was crafted from (e.g. "copper",
        # "bronze", "silver") - None for anything not crafted. Kyle
        # corrected the upgrade-kit design (Oct 2026) after seeing the
        # first version: "You use the same kit twice. Like copper kit
        # only upgrades copper stuff. If I make armor with a certain
        # type of cloth, we use that kit to upgrade it." - so a kit is
        # tied to the MATERIAL an item was made from, not to a specific
        # rarity jump, and this is the tag that match is made against
        # (world/upgrade_manager.py). Set by each crafting profession's
        # manager at craft time (e.g. BlacksmithingManager reads it off
        # the recipe's own output spec), never inferred from item_level
        # or rarity - a Tailoring "linen" item and a Blacksmithing
        # "copper" item could easily share the same item_level/rarity
        # while needing completely different kits.
        self.crafting_material = crafting_material

        # How many times an upgrade kit has been applied to this item -
        # capped at 2 (world/upgrade_manager.py enforces the cap; this
        # field is just the counter). Kyle, Oct 2026, after first saying
        # a material caps at exactly one rarity rank: "Yes ONE rank
        # jump, but two improvements" - it takes 2 kit applications to
        # reach that one rank: the 1ST bumps both rarity AND stats (the
        # original ratio-based bump), the 2ND bumps stats ONLY (rarity
        # stays put) by 1.5x the first application's own stat increase -
        # "if first upgrade...gives +1 stam and +1 str...goes white to
        # green. Then the next upgrade would be 1.5 stam and 1.5 str and
        # green stays green." A 3rd application is never possible once
        # upgrade_count reaches 2.
        self.upgrade_count = upgrade_count

        # The exact per-stat increase the FIRST kit application granted
        # (e.g. {"primary_stats": {"stamina": 1, "strength": 1}, ...}) -
        # recorded so the second application can compute "1.5x the first
        # one" instead of re-deriving a bump from a ratio a second time
        # (which would double-count the rarity change the first
        # application already banked). None until the first upgrade
        # happens, and never read again after the second.
        self.upgrade_deltas = upgrade_deltas

        # The permanent attachment fitted to this weapon (a scope, a set of
        # limbs) as its material_id, or None. See world/attachment_manager.py -
        # a separate system from upgrade kits on purpose: an attachment goes on
        # ANY ranged weapon including dropped ones, is matched by weapon_type
        # rather than crafting_material, applies exactly once, and gives flat
        # weapon damage. An item can carry both; they never touch each other's
        # fields. The damage is baked into weapon_damage_min/max at fit time,
        # so this field is a record of WHAT was fitted (for the item card and
        # to block a second one), not a modifier anything re-applies on load.
        self.attachment = attachment

        # Recipe scrolls / pattern items (Oct 2026): an item with a recipe_id is a learnable
        # recipe scroll. Right-clicking calls character.learn_recipe(recipe_id, recipe_profession,
        # skill_required). recipe_profession is the profession this recipe belongs to
        # (e.g. "blacksmithing"). Both are None for all normal gear/consumable/material items.
        self.recipe_id = recipe_id
        self.recipe_profession = recipe_profession

    def get_dps(self):
        """Damage per second for weapons. Returns 0 for non-weapons/shields.

        Not currently used anywhere (2026-09-06) - combat is turn-based
        and attack_speed never gates swing frequency, so a real "damage
        per SECOND" figure doesn't correspond to anything that happens in
        actual combat; the inventory tooltip that used to show this was
        removed (see ui/screens/inventory_screen.py) because two items
        dealing IDENTICAL damage (same damage_tier - see
        data/items/weapon_types.json) could still show different "DPS"
        purely from a leftover attack_speed value, which is misleading
        now that speed doesn't affect anything. Kept rather than deleted
        in case a real per-second stat becomes meaningful again later
        (e.g. if auto-attacks ever get real-time pacing).
        """
        if self.attack_speed <= 0:
            return 0.0
        avg_damage = (self.weapon_damage_min + self.weapon_damage_max) / 2
        return round(avg_damage / self.attack_speed, 1)

    def get_all_stat_bonuses(self):
        """Merge primary + secondary stats into a single dict for equip application."""
        merged = dict(self.primary_stats)
        for stat, value in self.secondary_stats.items():
            merged[stat] = merged.get(stat, 0) + value
        return merged

    def get_rarity_color(self):
        """Return the RGB color tuple for this item's rarity (for UI)."""
        from pathlib import Path
        import json
        rarity_file = Path(__file__).parent.parent / "data" / "items" / "rarity.json"
        with open(rarity_file, 'r') as f:
            rarity_data = json.load(f)["rarity_tiers"]
        tier = rarity_data.get(self.rarity, rarity_data["common"])
        return tuple(tier["color"])

    def is_weapon(self):
        return self.weapon_type is not None

    def is_armor(self):
        return self.armor_type is not None and self.armor_type not in ("accessory", "weapon")

    def is_bag(self):
        return self.armor_type == "bag"

    @property
    def is_gear(self):
        """False for a recipe scroll - an Item in the bag that is not something you wear.

        The inventory screen routes every click and tooltip on
        getattr(item, "is_gear", True). Item had no such attribute, so a scroll read as gear,
        went down the equip path, and was DELETED: equip_item took it out of the bag and
        Equipment.equip had no "recipe" slot to put it in. Kyle, 10 Nov: "i can click on it...
        and it vanishes." Every pattern, plan, recipe and schematic in the game.
        """
        return self.slot != "recipe" and not self.recipe_id

    def to_dict(self):
        """Serialize for save system."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "slot": self.slot,
            "item_level": self.item_level,
            "rarity": self.rarity,
            "armor_type": self.armor_type,
            "weapon_type": self.weapon_type,
            "stat_template": self.stat_template,
            "primary_stats": self.primary_stats,
            "secondary_stats": self.secondary_stats,
            "armor_value": self.armor_value,
            "weapon_damage_min": self.weapon_damage_min,
            "weapon_damage_max": self.weapon_damage_max,
            "attack_speed": self.attack_speed,
            "block_value": self.block_value,
            "bag_capacity": self.bag_capacity,
            "icon_id": self.icon_id,
            "required_level": self.required_level,
            "sell_price": self.sell_price,
            "flavor_text": self.flavor_text,
            "set_id": self.set_id,
            "sockets": self.sockets,
            "enchant_id": self.enchant_id,
            "is_crafted": self.is_crafted,
            "crafting_material": self.crafting_material,
            "upgrade_count": self.upgrade_count,
            "upgrade_deltas": self.upgrade_deltas,
            "attachment": self.attachment,
            "recipe_id": self.recipe_id,
            "recipe_profession": self.recipe_profession,
            "proc": self.proc,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from save data."""
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            slot=data["slot"],
            item_level=data["item_level"],
            rarity=data["rarity"],
            armor_type=data.get("armor_type"),
            weapon_type=data.get("weapon_type"),
            stat_template=data.get("stat_template"),
            primary_stats=data.get("primary_stats", {}),
            secondary_stats=data.get("secondary_stats", {}),
            armor_value=data.get("armor_value", 0),
            weapon_damage_min=data.get("weapon_damage_min", 0),
            weapon_damage_max=data.get("weapon_damage_max", 0),
            attack_speed=data.get("attack_speed", 0.0),
            block_value=data.get("block_value", 0),
            bag_capacity=data.get("bag_capacity", 0),
            icon_id=data.get("icon_id"),
            required_level=data.get("required_level", 1),
            sell_price=data.get("sell_price", 0),
            flavor_text=data.get("flavor_text", ""),
            set_id=data.get("set_id"),
            sockets=data.get("sockets", []),
            enchant_id=data.get("enchant_id"),
            is_crafted=data.get("is_crafted", False),
            crafting_material=data.get("crafting_material"),
            upgrade_count=data.get("upgrade_count", 0),
            upgrade_deltas=data.get("upgrade_deltas"),
            attachment=data.get("attachment"),
            recipe_id=data.get("recipe_id"),
            recipe_profession=data.get("recipe_profession"),
            proc=data.get("proc"),
        )

    def __repr__(self):
        return f"<Item {self.name} (ilvl {self.item_level}, {self.rarity}, {self.slot})>"
