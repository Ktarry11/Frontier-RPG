"""What gear is worth to a vendor - one curve for every item in the game.

Kyle, 10 Nov: "Sell prices of gear is way too low...lvl 58 blues selling for 1 silver 2
copper?" and "1000% we need to revamp buy/sell price of gear."

A piece of gear sold for roughly its item level in COPPER (item_level x 1 to 1.7), so the best
blue in the game was worth less than the reward for a level 1 quest (18 silver). Vendors
charge four times the sell price, so their shelves were just as flat: a level 30 plate
legging for under 2 silver.

This is the WoW shape: value climbs a little faster than the square of the item's level, a
better rarity is worth more, and a chest or a two-hander is worth more than a ring.

    level  green chest   blue chest   epic chest
      10        2s 90c       4s 34c       7s 53c
      20       12s 41c      18s 62c      32s 27c
      40       53s 22c      79s 83c   1g 38s 37c
      58    1g 16s 13c   1g 74s 19c    3g 1s 93c

Quest money for scale (median reward_gold in data/quests): level 10 quests pay 42s, level 40
pay 1g 29s. So a drop is worth selling and a quest is still worth more than the green it
hands you.

A vendor's BUY price is still 4x this (ui/screens/vendor_screen.py), unless the item states
its own vendor_price - bags do, and are not priced here at all.
"""

#: copper = BASE * item_level ** POWER, before rarity and slot.
BASE = 2.3
POWER = 2.1

RARITY_MULT = {
    "poor": 0.35, "common": 0.6, "uncommon": 1.0, "rare": 1.5, "epic": 2.6, "legendary": 4.0,
}

#: Share of a full-price piece (a chest) each slot is worth. Numbered ring/trinket slots are
#: looked up without their digit.
SLOT_MULT = {
    "chest": 1.0, "legs": 1.0, "head": 0.8, "shoulder": 0.8, "hands": 0.65, "feet": 0.65,
    "waist": 0.55, "back": 0.55, "wrist": 0.5,
    "neck": 0.6, "ring": 0.6, "trinket": 0.7,
    "main_hand": 0.95, "off_hand": 0.6, "ranged": 0.8,
}
TWO_HANDED = {"sword_2h", "axe_2h", "mace_2h", "staff", "polearm"}
TWO_HAND_MULT = 1.25
SHIELD_MULT = 0.8


def slot_weight(slot, weapon_type=None):
    if weapon_type in TWO_HANDED:
        return TWO_HAND_MULT
    if weapon_type == "shield":
        return SHIELD_MULT
    key = (slot or "").rstrip("0123456789")
    return SLOT_MULT.get(key, 0.6)


def gear_sell_price(item_level, rarity, slot, weapon_type=None):
    """Copper a vendor pays for a piece of gear."""
    level = max(1, int(item_level or 1))
    value = BASE * (level ** POWER) * RARITY_MULT.get(rarity, 1.0) * slot_weight(slot, weapon_type)
    return max(1, int(round(value)))
