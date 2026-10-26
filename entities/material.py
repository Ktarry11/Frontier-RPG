"""
Material class - raw gathered goods (ore, herbs, wood, hides, ...) that
feed future crafting professions. Deliberately separate from Consumable:
a Consumable has a use() effect on the character (heal, buff, ...) - a
raw material has NO effect until crafting turns it into something else.
Giving materials a use() would either be a silent no-op (confusing) or
force fake effects onto inert items. Keeping the type separate keeps
each class honest about what it actually does, same reasoning that
already split Consumable off from Item.

Mirrors Consumable's stacking shape (stack_limit, quantity, to_dict/
from_dict) since that's exactly the behavior a material stack needs -
just without use()/cooldown/buff_category, none of which apply.
"""


class Material:
    """A stackable raw gathering material (ore, herb, etc)."""

    def __init__(self, material_id, name, material_type, profession,
                 tier, description="", stack_limit=20, sell_price=0,
                 icon_id=None, skill_range=None, vendor_price=0):
        """
        Args:
            material_id: unique identifier (e.g., "ore_copper", "herb_peacebloom")
            name: display name (e.g., "Copper Ore", "Peacebloom")
            material_type: "ore" | "herb" (future: "wood", "hide", "essence", ...)
            profession: the gathering profession that produces this
                        ("mining", "herbalism", future "woodcutting",
                        "skinning", "essence_harvesting")
            tier: profession skill tier this belongs to - "early", "mid",
                  "late", "endgame" - matches the tiering Kyle's source
                  art sheets already use. Gates which nodes can drop it
                  once node skill-gating is wired.
            description: flavor text / tooltip
            stack_limit: max quantity per stack (WoW convention: 20 for
                         most tradeskill mats, matches Consumable default)
            sell_price: copper refund if sold to a vendor
            icon_id: filename (no extension) under
                     assets/gathering_nodes/<material_type>s/<icon_id>.png
                     Defaults to material_id's suffix if not given by
                     caller - see MaterialManager._load_data.
            skill_range: [orange_ends, yellow_ends, green_ends, grey_at] -
                         WoW's real profession skill-up convention (see
                         data/gathering/materials.json's _comment for the
                         full explanation). None means "always guaranteed
                         skill-up, never greys out" - a safe default for
                         any material authored without an explicit range
                         rather than silently blocking all skill gain.
        """
        self.material_id = material_id
        self.name = name
        self.material_type = material_type
        self.profession = profession
        self.tier = tier
        self.description = description
        self.stack_limit = stack_limit
        self.sell_price = sell_price
        self.icon_id = icon_id
        self.skill_range = skill_range
        self.vendor_price = vendor_price  # copper cost to buy from a vendor (0 = not sold by vendors)

        self.quantity = 1  # number in this stack

    def to_dict(self):
        """Serialize for save/load."""
        return {
            "material_id": self.material_id,
            "name": self.name,
            "material_type": self.material_type,
            "profession": self.profession,
            "tier": self.tier,
            "description": self.description,
            "stack_limit": self.stack_limit,
            "sell_price": self.sell_price,
            "vendor_price": self.vendor_price,
            "icon_id": self.icon_id,
            "skill_range": self.skill_range,
            "quantity": self.quantity,
        }

    @staticmethod
    def from_dict(data):
        """Deserialize from save data."""
        m = Material(
            data["material_id"],
            data["name"],
            data["material_type"],
            data["profession"],
            data["tier"],
            data.get("description", ""),
            data.get("stack_limit", 20),
            data.get("sell_price", 0),
            data.get("icon_id"),
            data.get("skill_range"),
            data.get("vendor_price", 0),
        )
        m.quantity = data.get("quantity", 1)
        return m

    def __repr__(self):
        return f"<Material {self.name} x{self.quantity}>"
