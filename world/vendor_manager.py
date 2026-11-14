"""
VendorManager - loads and manages vendor NPCs.
Vendors are stationary NPCs in towns that buy/sell consumables AND gear.
"""
import json
import random
from pathlib import Path
from world.zone_keys import zone_key as _zk


#: How many gear items a vendor stocks, and what rarity mix they roll from.
#: WoW's own vendors are overwhelmingly white/grey goods (bags, reagents,
#: basic armor) with the occasional named "quartermaster" selling a green or
#: two for reputation/tokens - actual blues are rare and usually tied to a
#: quest reward or faction vendor, not everyday stock. This mirrors that:
#: mostly Common, a couple of Uncommon rolls, and only a small chance of
#: anything Rare, capped at one per restock.
VENDOR_GEAR_COUNT = 6
#: Kyle, 2026-10-28, playing the Underdark: the shops "are falling back into generic trash". This was
#: 70/25/5, and at that mix a six-slot shelf is four white items - "Plain Wand", "Simple Cloak" - which
#: are strictly worse than any quest green the player already has. The item level was a separate bug;
#: this is the one that made the shelf not worth opening.
#:
#: It is safe to raise globally because EVERY gear vendor is already a specialist: only 19 of 86 vendors
#: set sells_gear, and they are all quartermasters, smiths, weaponsmiths, bowyers and engineers. There is
#: no general store to protect. A shelf of six now averages ~2.7 white, ~2.7 green and a 10% blue, which
#: is a shop worth walking into and still well short of what a dungeon drops.
VENDOR_GEAR_RARITY_WEIGHTS = {
    "common": 45,
    "uncommon": 45,
    "rare": 10,
}
#: Gear item_level is derived from the vendor's zone tier via this vendor
#: field (see vendors.json "gear_level"); falls back to this if absent.
DEFAULT_VENDOR_GEAR_LEVEL = 10

#: One representative class per armor type (cloth/leather/mail/plate), used
#: to roll a genuinely mixed general-goods vendor instead of one class's
#: gear only. THE BUG this replaces: _roll_gear_stock previously hardcoded
#: char_class="Warrior" for every single roll, and Warrior's armor_type is
#: "plate" - so every vendor in the game stocked 100% plate regardless of
#: zone, faction, or vendor identity, useless to 9 of the 10 launch
#: classes. Deliberately the 10 launch/base classes only, not the wider
#: CoA roster (see data/items/armor_types.json's class_armor_map for the
#: full ~30-class list) - those aren't selectable at character creation
#: yet, so a vendor rolling "Runemaster" stock would be confusing dead
#: flavor, not a real option for anyone shopping.
VENDOR_STOCK_CLASSES = [
    "Priest", "Mage", "Warlock",          # cloth
    "Rogue", "Druid",                     # leather
    "Shaman", "Hunter",                   # mail
    "Warrior", "Paladin",                 # plate
]


#: Chance any given vendor-stock roll is a bag instead of armor/weapon
#: gear. Real WoW general-goods vendors reliably stock at least one or two
#: bags among their gear - this mirrors that without dedicating a whole
#: separate stock slot/count just for bags.
VENDOR_BAG_CHANCE = 0.15


class VendorNPC:
    """Represents a vendor NPC."""
    
    def __init__(self, vendor_id, name, zone, x, y, tile_sprite, sells, buys_from_player, faction,
                 gear_level=None, sells_gear=True, race=None, gender="male", appearance_variant=0,
                 facing="down", greeting=""):
        self.vendor_id = vendor_id
        self.name = name
        self.zone = zone
        self.x = x
        self.y = y
        self.tile_sprite = tile_sprite
        self.sells = sells  # List of consumable_ids this vendor sells
        self.buys_from_player = buys_from_player
        self.faction = faction

        # Appearance - defaults to the zone's default race (see
        # world/race_registry.get_zone_default_race) when not given
        # explicitly in vendors.json, so existing vendor entries render
        # with a sensible race for their zone (orcs in Durotar, goblins
        # in Ratchet) with zero JSON changes required. A specific vendor
        # can still override via an explicit "race" key if a named NPC
        # calls for it (e.g. a lone human trader who settled in Durotar).
        # facing is fixed per Kyle's call to skip "turn toward player"
        # logic - a vendor just faces one direction permanently, same as
        # every other static NPC.
        from world.race_registry import get_zone_default_race
        self.race = race or get_zone_default_race(zone)
        self.gender = gender
        self.appearance_variant = appearance_variant
        self.facing = facing

        # Flavor line shown when the player talks to this vendor, same
        # role AmbientNPC.greeting plays - QuestDialogScreen's "greeting"
        # mode reads getattr(npc, "greeting", ...) generically, so this
        # just needs to exist with real text for a vendor to stop showing
        # the "has nothing more to say" fallback. Kyle's call: every
        # vendor should talk before the shop opens, not just the ones
        # with quest business - see overworld_screen.py's vendor
        # interaction handling and QuestDialogScreen's Shop/Leave buttons.
        self.greeting = greeting

        # Gear stock: rolled once and cached (self._gear_stock) so browsing
        # the vendor twice in a session shows the same items, rather than
        # re-rolling (and re-randomizing prices) on every screen open.
        self.gear_level = gear_level or DEFAULT_VENDOR_GEAR_LEVEL
        self.sells_gear = sells_gear
        self._gear_stock = None

    def available_consumables(self):
        """This vendor's `sells` list plus anything the player's faction standing has unlocked.

        Kept as a method rather than mutating `sells` at load time, because standing changes mid-session
        and a shelf that only updates on restart is a shelf the player does not believe in.
        """
        from world.faction_manager import get_faction_manager
        extra = get_faction_manager().vendor_unlocks(self.vendor_id)
        if not extra:
            return list(self.sells)
        seen = list(self.sells)
        for item in extra:
            if item not in seen:
                seen.append(item)
        return seen

    def get_gear_stock(self, loot_generator):
        """
        This vendor's current gear items, generating them on first access.

        Mostly white/grey basics with a couple of green rolls and a rare
        chance of blue - see VENDOR_GEAR_RARITY_WEIGHTS. Cached per vendor
        instance so the stock doesn't reshuffle every time the screen opens.
        """
        if not self.sells_gear:
            return []
        if self._gear_stock is None:
            self._gear_stock = self._roll_gear_stock(loot_generator)
        return self._gear_stock

    def _roll_gear_stock(self, loot_generator):
        items = []
        rarities = list(VENDOR_GEAR_RARITY_WEIGHTS.keys())
        weights = list(VENDOR_GEAR_RARITY_WEIGHTS.values())
        # Roll a genuine class per item so a general-goods vendor's stock
        # spans cloth/leather/mail/plate, not one class's gear only - see
        # VENDOR_STOCK_CLASSES for why (that's the bug this replaces).
        for _ in range(VENDOR_GEAR_COUNT):
            if random.random() < VENDOR_BAG_CHANCE:
                # Bag roll, gated at BOTH ends to this vendor's tier: the ceiling so a low-level town
                # does not sell a level-30 bag, and the floor so a tier-38 quartermaster stops offering
                # starter satchels. The floor is deliberately generous - ten under tier - because the
                # bag catalog is sparse and an exact match would often leave nothing to sell.
                # Floor is PROPORTIONAL, not a flat offset: the catalog is sparse and thins out at
                # the top, so a fixed "tier - 10" collapsed high-tier vendors onto a single bag. Half
                # the tier keeps two or three candidates in play at every level.
                item = loot_generator.generate_bag(player_level=self.gear_level,
                                                   min_level=max(1, self.gear_level // 2),
                                                   max_rarity="rare")
                if item is not None:
                    items.append(item)
                    continue
            rarity = random.choices(rarities, weights=weights, k=1)[0]
            stock_class = random.choice(VENDOR_STOCK_CLASSES)
            item = loot_generator.generate_item_for_class(
                stock_class, self.gear_level, rarity=rarity)
            items.append(item)
        return items


class VendorManager:
    """Manages vendor NPCs across all zones."""
    
    def __init__(self):
        """Load all vendor definitions from JSON."""
        self.vendors = {}  # vendor_id -> VendorNPC
        self.vendors_by_zone = {}  # zone -> list of VendorNPCs
        self._load_vendors()
    
    def _load_vendors(self):
        """Load all vendor definitions from data/npcs/vendors.json."""
        vendors_path = Path(__file__).parent.parent / "data" / "npcs" / "vendors.json"
        
        try:
            with open(vendors_path, 'r', encoding="utf-8") as f:
                data = json.load(f)
            
            for vendor_def in data.get("vendors", []):
                vendor = VendorNPC(
                    vendor_def["vendor_id"],
                    vendor_def["name"],
                    vendor_def["zone"],
                    vendor_def["x"],
                    vendor_def["y"],
                    vendor_def["tile_sprite"],
                    vendor_def["sells"],
                    vendor_def["buys_from_player"],
                    vendor_def["faction"],
                    gear_level=vendor_def.get("gear_level"),
                    sells_gear=vendor_def.get("sells_gear", True),
                    race=vendor_def.get("race"),
                    gender=vendor_def.get("gender", "male"),
                    appearance_variant=vendor_def.get("appearance_variant", 0),
                    facing=vendor_def.get("facing", "down"),
                    greeting=vendor_def.get("greeting", ""),
                )
                # A hidden seller (world/secrets.py) has no map icon and no dot.
                vendor.hidden = bool(vendor_def.get("hidden", False))
                self.vendors[vendor.vendor_id] = vendor
                
                # Index by zone
                key = self._zone_key(vendor.zone)
                if key not in self.vendors_by_zone:
                    self.vendors_by_zone[key] = []
                self.vendors_by_zone[key].append(vendor)

            # Greetings rewritten in the quest overhaul live in data/npcs/vendor_greetings/*.json
            # ({vendor_id: text}) and are laid over vendors.json, which the town tools rewrite.
            for path in sorted((vendors_path.parent / "vendor_greetings").glob("*.json")):
                try:
                    for vendor_id, text in json.loads(path.read_text(encoding="utf-8")).items():
                        if vendor_id in self.vendors and text:
                            self.vendors[vendor_id].greeting = text
                        else:
                            print(f"WARNING: vendor greeting overlay {path.name} names unknown vendor {vendor_id}")
                except (OSError, ValueError) as e:
                    print(f"ERROR: vendor greeting overlay {path.name}: {e}")

        except FileNotFoundError:
            print(f"WARNING: Vendor file not found at {vendors_path}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse vendor JSON: {e}")
    
    def get_vendor(self, vendor_id):
        """Get a vendor by ID."""
        return self.vendors.get(vendor_id)
    
    @staticmethod
    def _zone_key(zone):
        """Normalize a zone name to the slug form used in vendors.json.

        vendors.json keys zones as "valley_of_trials", but ZoneManager passes
        the Tilemap's display name ("Valley of Trials"). Nothing normalized
        between the two, so get_vendor_at_location() never matched anything -
        the entire vendor system was unreachable in every zone. Normalizing
        here fixes all zones at once and accepts either form.

        Moved to the shared helper 29 Oct 2026 - this one stripped apostrophes but not a leading
        article, which is why The Sepulcher's vendors were as unreachable as its ambient NPCs.
        """
        return _zk(zone)

    def get_vendors_in_zone(self, zone):
        """Get all vendors in a specific zone (accepts display name or slug)."""
        return self.vendors_by_zone.get(self._zone_key(zone), [])
    
    def get_vendor_at_location(self, zone, x, y):
        """Get vendor at a specific location (if any)."""
        for vendor in self.get_vendors_in_zone(zone):
            if vendor.x == x and vendor.y == y:
                return vendor
        return None


# Global singleton instance
_vendor_manager = None

def get_vendor_manager():
    """Get or create the global VendorManager instance."""
    global _vendor_manager
    if _vendor_manager is None:
        _vendor_manager = VendorManager()
    return _vendor_manager
