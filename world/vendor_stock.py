"""The one place a vendor `sells` id becomes a real item.

WHY THIS FILE EXISTS, AND IT IS THE FOURTH TIME. A vendor's `sells` list
holds bare ids and four different kinds of thing answer to them:
consumables, gathered materials and reagents, recipe scrolls, and bags.
The resolution order lived only inside
ui/screens/vendor_screen.py::_build_vendor_stock, and every verifier that
needed the same answer rebuilt it by hand from whichever data files its
author remembered. tools/qa_factions.py's own comments record the score:

    "Checking consumables alone would have called most of the game broken."
    "57 recipes carry source 'vendor' ... so a check that knows only about
     consumables and materials calls all 57 of them ghosts. This verifier
     was wrong before the data was - again."

Bags were the fourth category, and the fourth time the verifier was wrong
rather than the data: all 21 bags in data/items/bags.json are real,
buyable and on the right shelves, and qa_factions reported 13 of them as
items that "do not exist" across roughly 200 vendors.

So the order lives here, the screen calls it, and anything asking "can a
vendor sell this?" asks the same function the game uses to put it on the
shelf. A fifth category added to the screen and not to this file is the
same bug again; added here, it is right everywhere at once.
"""


_UNIQUES = None


def make_unique(unique_id):
    """A fresh copy of one hand-made item from data/items/secret_uniques.json, or None."""
    global _UNIQUES
    if _UNIQUES is None:
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent / "data" / "items" / "secret_uniques.json"
        try:
            _UNIQUES = json.loads(path.read_text(encoding="utf-8")).get("items", {})
        except (OSError, ValueError):
            _UNIQUES = {}
    d = _UNIQUES.get(unique_id)
    if d is None:
        return None
    from entities.boss_loot import _item_from_def
    item = _item_from_def(d)
    item.vendor_price = d.get("price")
    return item


def resolve_vendor_item(item_id, consumable_manager=None, gathering_manager=None,
                        loot_generator=None):
    """Turn one `sells` id into a real item, or None if nothing answers to it.

    The managers are optional so a tool can call this without assembling
    the world; passing them in is strongly preferred in the game, where
    they already exist and constructing a second GatheringNodeManager per
    item would be absurd.
    """
    if consumable_manager is None:
        from entities.consumable_manager import get_consumable_manager
        consumable_manager = get_consumable_manager()
    if gathering_manager is None:
        from world.gathering_manager import GatheringNodeManager
        gathering_manager = GatheringNodeManager()
    if loot_generator is None:
        from entities.loot_generator import LootGenerator
        loot_generator = LootGenerator()

    # Membership test BEFORE get_consumable, not a get-and-check:
    # get_consumable logs a WARNING for an unknown id, and an id that is a
    # crafting reagent rather than a consumable is the normal case here,
    # not an error. Probing with get_consumable printed one false warning
    # per reagent (~190 per vendor open).
    # ONE OF A KIND (world/secrets.py's hidden sellers): a hand-made item from
    # data/items/secret_uniques.json, the same shape as a boss's fixed drop.
    if isinstance(item_id, str) and item_id.startswith("unique:"):
        return make_unique(item_id[len("unique:"):])

    if consumable_manager.has_consumable(item_id):
        return consumable_manager.get_consumable(item_id, quantity=1)

    # Crafting reagent or gathered material
    mat = gathering_manager.make_material_instance(item_id)
    if mat:
        return mat

    # RECIPE SCROLLS. A vendor's sells list may name a recipe id directly,
    # and 57 recipes carry source "vendor" expecting exactly that.
    from world.recipe_manager import make_recipe_scroll
    scroll = make_recipe_scroll(item_id)
    if scroll is not None:
        return scroll

    # BAGS. Kyle, 2026-10-31: "We need to ensure bags can be made through
    # tailoring or sold via some vendors." Vendors already offered bags
    # through the random gear roll, but that roll has a deliberate LEVEL
    # FLOOR on it, so the starter bags were the one thing it never
    # produced - the players with 24 slots and no bag could not buy one
    # anywhere. Naming a bag in a vendor's sells list puts it on the shelf
    # permanently instead of hoping the roll offers it.
    #
    # The buy path needs nothing extra for either of the last two: a
    # scroll and a bag Item both carry slot and armor_value, so the vendor
    # screen's _is_gear routes them to add_to_inventory, and a bag's price
    # falls back to sell_price * 4, which is what the catalog's
    # vendor_price says.
    bag = loot_generator.generate_bag(bag_id=item_id)
    if bag is not None:
        return bag

    return None
