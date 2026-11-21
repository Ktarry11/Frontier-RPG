"""Goods: one way to carry any item through an auction or a letter, and back into somebody's bags.

The game keeps three kinds of thing in three places on a Character:

    inventory     Item (gear, bags, recipe scrolls) and LootItem (quest items, vendor trash)
    consumables   Consumable (potions, elixirs, food, ammo, bombs, gadgets)
    materials     Material (ore, herbs, cloth, gems, enchant scrolls, runes, creature parts)

An auction or a letter has to hold any of them, survive a save, and put the thing back where it belongs when it's
taken. A good is a plain dict, {"kind": ..., "data": obj.to_dict()}, built with each class's own to_dict, so a new
field on an item travels through the auction house without this file knowing about it (the bank stores items the
same way, for the same reason).

Nothing here owns money or knows about markets. It packs, unpacks, describes, gives and takes.
"""

GEAR, LOOT, CONSUMABLE, MATERIAL = "gear", "loot", "consumable", "material"

#: Things that can't go on the auction house or in a letter. Quest items are Kyle's long-standing ruling (they never
#: sell); a set token is worth a set piece at an Artifact Keeper and nothing anywhere else.
def can_trade(obj):
    """(ok, reason). Reason is a sentence the screen can show."""
    if obj is None:
        return False, "There's nothing there."
    if getattr(obj, "category", None) == "quest" or getattr(obj, "quest_id", None):
        return False, "Quest items can't be sold or sent."
    if not getattr(obj, "is_sellable", True):
        return False, "That can't be sold or sent."
    iid = str(getattr(obj, "item_id", "") or "")
    if iid.startswith("t0_token_"):
        return False, "Set tokens can't be sold or sent."
    if getattr(obj, "market_locked", False):
        return False, "That can't be sold or sent."
    # Kyle, 16 Nov 2026: "neeever allow rep items to be sold! ever!" (world/rep_items.py)
    from world.rep_items import is_rep_item
    if is_rep_item(obj):
        return False, "Reputation rewards can't be sold or sent."
    if kind_of(obj) == GEAR and getattr(obj, "name", None) in _secret_names():
        # a hidden place's loot, or a hidden seller's: it stays a secret, so it doesn't go on the open market
        return False, "That can't go on the auction house."
    return True, ""


_SECRET = None


def _secret_names():
    """Names of every item a hidden place or a hidden seller hands out (docs/auction_house_design.md, section
    10). Built once: the hidden bosses' loot (every loot file, keyed by a creature that lives in a hidden zone),
    the secret sellers' uniques and the ???? faction's rewards."""
    global _SECRET
    if _SECRET is not None:
        return _SECRET
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent
    out = set()
    try:
        from world.hidden_zones import creature_kinds
        hidden = set(creature_kinds())
    except Exception:
        hidden = set()
    for path in sorted((root / "data/loot").glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for boss, rows in doc.items():
            if boss.startswith("_") or not isinstance(rows, list):
                continue
            if "hidden" in path.name or boss in hidden:
                out.update(r.get("name") for r in rows if isinstance(r, dict))
    # and the Frontier Quartermasters' gear and the heroic-only drops (tools/build_heroic_rewards.py): bound to
    # whoever earned them
    for name in ("secret_uniques.json", "unnamed_rewards.json", "heroic_rewards.json"):
        try:
            doc = json.loads((root / "data/items" / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        out.update(r.get("name") for r in (doc.get("items") or {}).values() if isinstance(r, dict))
    out.discard(None)
    _SECRET = out
    return out


def kind_of(obj):
    from entities.consumable import Consumable
    from entities.loot_item import LootItem
    from entities.material import Material
    if isinstance(obj, Material):
        return MATERIAL
    if isinstance(obj, Consumable):
        return CONSUMABLE
    if isinstance(obj, LootItem):
        return LOOT
    return GEAR


def pack(obj, quantity=None):
    """A good for this object. quantity overrides the stack size (for splitting a stack)."""
    k = kind_of(obj)
    data = obj.to_dict()
    if k != GEAR:
        data["quantity"] = int(quantity if quantity is not None else getattr(obj, "quantity", 1) or 1)
    return {"kind": k, "data": data}


def unpack(good):
    """A fresh object from a good. Never the same object twice: every call builds a new one."""
    k, data = good["kind"], dict(good["data"])
    if k == MATERIAL:
        from entities.material import Material
        return Material.from_dict(data)
    if k == CONSUMABLE:
        from entities.consumable import Consumable
        return Consumable.from_dict(data)
    if k == LOOT:
        from entities.loot_item import LootItem
        return LootItem.from_dict(data)
    from entities.item import Item
    return Item.from_dict(data)


def quantity(good):
    if good["kind"] == GEAR:
        return 1
    return int(good["data"].get("quantity", 1) or 1)


def with_quantity(good, n):
    out = {"kind": good["kind"], "data": dict(good["data"])}
    if out["kind"] != GEAR:
        out["data"]["quantity"] = int(n)
    return out


def item_id(good):
    d = good["data"]
    return d.get("material_id") or d.get("consumable_id") or d.get("item_id")


def market_key(good):
    """What counts as 'the same thing' for prices and undercuts.

    Stackables are the same thing when their ids match. Gear is the same thing only when it's the very same named
    item (a crafted piece, a named epic): a procedurally rolled piece is unique, and its id says so.
    """
    k = good["kind"]
    return {MATERIAL: "m:", CONSUMABLE: "c:", LOOT: "l:", GEAR: "g:"}[k] + str(item_id(good))


def name(good):
    return good["data"].get("name", "?")


def rarity(good):
    d = good["data"]
    if good["kind"] == MATERIAL:
        return d.get("rarity") or "common"
    if good["kind"] == CONSUMABLE:
        return "common"
    return d.get("rarity") or "common"


def sell_price(good):
    """What a vendor pays for ONE of it, in copper (the deposit is worked from this)."""
    return int(good["data"].get("sell_price", 0) or 0)


def required_level(good):
    d = good["data"]
    return int(d.get("required_level") or 0)


def give(character, good):
    """Put a good into this character's bags. True if it all fit, False if nothing was moved.

    Gear and loot take a bag slot each and the bags can be full; materials and consumables stack in their own
    pouches, which have no limit in this game.
    """
    obj = unpack(good)
    k = good["kind"]
    if k == MATERIAL:
        character.add_material(obj)
        return True
    if k == CONSUMABLE:
        character.add_consumable(obj)
        return True
    if k == LOOT:
        from entities.loot_item import add_loot_item
        free = character.inventory_capacity - len(character.inventory)
        stack = max(1, int(getattr(obj, "stack_limit", 20) or 20))
        have_room = sum(max(0, stack - i.quantity) for i in character.inventory
                        if getattr(i, "item_id", None) == obj.item_id and hasattr(i, "category"))
        if have_room + free * stack < obj.quantity:
            return False
        return add_loot_item(character, obj.item_id, obj.name, category=obj.category, amount=obj.quantity,
                             description=obj.description, icon_id=obj.icon_id, quest_id=obj.quest_id,
                             sell_price=obj.sell_price, rarity=obj.rarity, starts_quest_id=obj.starts_quest_id)
    return bool(character.add_to_inventory(obj))


def room_for(character, goods):
    """Whether every good in the list would fit, worked out before anything moves."""
    slots = 0
    for g in goods:
        if g["kind"] == GEAR:
            slots += 1
        elif g["kind"] == LOOT:
            slots += 1
    return len(character.inventory) + slots <= character.inventory_capacity


def take(character, obj, n=None):
    """Remove n of obj (all of it when n is None) from this character's bags and return the good, or None.

    obj is the very object in the bags. A stack is split when n is less than the stack; the rest stays where it was.
    """
    ok, _why = can_trade(obj)
    if not ok:
        return None
    k = kind_of(obj)
    have = 1 if k == GEAR else int(getattr(obj, "quantity", 1) or 1)
    n = have if n is None else max(1, min(int(n), have))
    if k == GEAR:
        if obj not in character.inventory:
            return None
        character.inventory.remove(obj)
        return pack(obj)
    pouch = {MATERIAL: character.materials, CONSUMABLE: character.consumables, LOOT: character.inventory}[k]
    if obj not in pouch:
        return None
    good = pack(obj, n)
    if n >= have:
        pouch.remove(obj)
    else:
        obj.quantity = have - n
    return good


def tradeable_goods(character):
    """Every stack and piece in this character's bags that could be listed or sent: (obj, kind)."""
    out = []
    for obj in list(character.inventory):
        if can_trade(obj)[0]:
            out.append(obj)
    for obj in list(getattr(character, "materials", []) or []):
        if can_trade(obj)[0]:
            out.append(obj)
    for obj in list(getattr(character, "consumables", []) or []):
        if can_trade(obj)[0]:
            out.append(obj)
    return out
