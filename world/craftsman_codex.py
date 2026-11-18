"""The Craftsman Codex: MerchantTusk sells another primary profession slot.

Kyle, 16 Nov 2026: "I want merchant Tusk to sell a 'Craftsman Codex' Which unlocks additional Crafting Slots. First
Codex is 100g, then 200g, then 300g, then 400g, then each additional one is 500g and won't go past that point!"

Each codex read is one more primary profession a character can know (world/profession_manager.max_primary). The
price climbs 100, 200, 300, 400 gold and then stays at 500 for every one after. You can keep buying until every
primary trade in the game has a slot; past that a codex would do nothing, so Tusk stops selling them.

The codex is read on the spot, not carried: it's a slot, the same way a bank tab is a tab. It's paid from the party
purse, like Tusk's bank tabs, and it belongs to the character who bought it (it's saved on them as `codices`).
"""

GOLD = 10000                      # copper in a gold
PRICES_GOLD = (100, 200, 300, 400)
CAP_GOLD = 500

NAME = "Craftsman Codex"
BLURB = "Read on the spot: one more primary profession you can learn."


def owned(character):
    return int(getattr(character, "codices", 0) or 0)


def price(character):
    """Copper for the next codex, or None when every primary trade already has a slot."""
    from world import profession_manager as pm
    n = owned(character)
    if pm.max_primary(character) >= pm.primary_total():
        return None
    gold = PRICES_GOLD[n] if n < len(PRICES_GOLD) else CAP_GOLD
    from world.faction_manager import rep_price
    return rep_price(gold * GOLD)


def buy(character, party):
    """-> (ok, message). Spends from the party purse and gives the character one more slot."""
    from world import profession_manager as pm
    cost = price(character)
    if cost is None:
        return False, "You already have room for every trade there is."
    if party is None or getattr(party, "copper", 0) < cost or not party.remove_currency(cost):
        return False, f"A {NAME} costs {cost // GOLD} gold."
    character.codices = owned(character) + 1
    return True, (f"You read the {NAME}. You can now know {pm.max_primary(character)} professions "
                  f"({cost // GOLD} gold).")
