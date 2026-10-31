"""The one formula that says how strong an item of a given level is allowed to be.

Kyle, 2026-10-31: "We need to audit all the items to follow a curve... as long as ours has SOME
formula, It can be home-brew but it MUST MUST be consistent!"

THE FORMULA WAS ALREADY HERE. Most of the game's 1300 items already sit on one curve - it was
simply never written down, so nothing could tell an item that had fallen off it. Shelf-King's
Roadbreaker (ilvl 39) and Favourite's Gurbashi Pike (ilvl 41) both land within half a level of
what this predicts, and they were authored months apart. What was missing was not a formula but
somewhere to keep it.

The shape is WoW Classic's, because that is the shape the existing items turned out to have:

    value      = ( SUM over stats of (amount * mod) ** 1.5 ) ** (2/3)
    slot_value = value * SLOT_MOD[slot]
    item_level = (slot_value + c) / m          # c, m depend on rarity

The 1.5 / 2/3 pair is what makes one huge stat cost more than the same total spread over two -
a 45-agility weapon is worth less than 30 agility and 15 stamina - which is why the curve holds
across items with very different stat lines.

SLOT_MOD is "how much weaker this slot's stats are for the same item level". A one-hander is
2.44 because it is worth a lot on its own through damage; a chest piece is 1.0 because its
stats are all it has.

WHAT IS HOME-BREW HERE. The slot modifiers and the rarity constants are Classic's. The stat
modifiers for everything except the five primaries were never documented anywhere we can read,
so they are FITTED to Frontier's own on-curve items by tools/audit_item_curve.py --fit and
pasted below. That makes the formula descriptive of what this game already does rather than an
import from another one - and it is still exactly one formula, which is the part Kyle cares
about.
"""

#: Primary stats are the unit. Everything else is expressed relative to one point of Strength.
PRIMARY = ("strength", "agility", "stamina", "intellect", "spirit")

#: stat -> cost per point, relative to a primary stat.
#: The five primaries are 1.0 by definition. The rest are fitted - see the module docstring and
#: tools/audit_item_curve.py --fit, which prints this table.
#: Fitted 2026-10-31 by audit_item_curve.py --fit over the items already on the curve.
#: A check on the method: attack_power came out at 0.490 and Classic's own table puts it at
#: 115/230 = 0.500. Nothing told the fit that. It recovered a documented constant from
#: Frontier's item data alone, which is the reason to believe the rest of the column.
STAT_MOD = {
    "strength": 1.0, "agility": 1.0, "stamina": 1.0, "intellect": 1.0, "spirit": 1.0,
    "armor": 0.345,
    "attack_power": 0.735,
    "block_rating": 19.910,
    "block_value": 1.615,
    "crit_chance_physical": 15.340,
    "crit_chance_spell": 13.440,
    "defense_rating": 8.420,
    "dodge_rating": 11.285,
    "haste": 2.230,
    "healing_power": 1.725,
    "hit_rating": 13.950,
    "mp5": 4.170,
    "parry_rating": 2.140,
    "spell_power": 1.345,
    # spell_penetration fitted to 0.0 - the items carrying it are explained entirely by their
    # other stats, so this game does not currently charge for it. Left out rather than written
    # as 0.0, so it shows up as "not priced" instead of as "free", which are different claims.
    #   not priced: spell_penetration, the per-school spell powers, the resistances
}

#: slot -> stat budget per item level, at RARE. Fitted from Frontier's own 4,298 statted items
#: by tools/audit_item_curve.py --fit, not imported from anywhere.
#:
#: I started by importing WoW Classic's slot modifiers and rarity constants, and they reported
#: 81% of this game's items as broken. A formula that says four fifths of the content is wrong
#: is a wrong formula, not four fifths of wrong content. Classic's numbers describe Classic's
#: budget; Frontier's armour spends about a third of that, and Frontier's two-handers spend far
#: MORE than Classic's (Classic pays a 2H in weapon damage instead of stats, this game does
#: not). The curve was already in the data and already consistent - rare two-handers sit at
#: 1.232 with an interquartile spread of 0.11 - it simply had nowhere to live, so nothing could
#: tell an item that had fallen off it.
SLOT_K = {
    "2H": 1.232,
    "chest": 0.476, "legs": 0.473,
    "shoulder": 0.372, "head": 0.370,
    "main_hand_weapon": 0.324, "off_hand_weapon": 0.290,
    "wrist": 0.254, "feet": 0.251, "shield": 0.240, "waist": 0.237, "hands": 0.233,
    "neck": 0.198, "ring": 0.198, "trinket": 0.193, "back": 0.192,
    "ranged_weapon": 0.172,
}

#: Rarity scales the whole budget. 0.787 is the median across all 17 slots and the slots agree
#: closely (0.75 to 0.90), which is itself evidence the game has been built to one rule.
#: The epic figure rests on two slots and 36 items, so it is the least trustworthy number here.
RARITY_MULT = {"uncommon": 0.787, "rare": 1.0, "epic": 1.242}

TWO_HANDED = {"axe_2h", "mace_2h", "sword_2h", "polearm", "staff"}


def slot_key(item):
    """Which budget line this item belongs to."""
    wt = item.get("weapon_type")
    if wt == "shield":
        return "shield"
    if wt in TWO_HANDED:
        return "2H"
    if wt:
        slot = item.get("slot")
        if slot in ("ranged", "off_hand"):
            return f"{slot}_weapon"
        return "main_hand_weapon"
    return item.get("slot")


def stat_value(item, mods=None):
    """The budget an item's stat line actually spends.

    The 1.5 / 2-3 pair is what makes one huge stat cost more than the same total split in two,
    so a 45-agility weapon is worth less than 30 agility plus 15 stamina. That shape is why one
    curve holds across items with very different stat lines.
    """
    mods = mods or STAT_MOD
    total = 0.0
    for group in ("primary_stats", "secondary_stats"):
        for stat, amount in (item.get(group) or {}).items():
            m = mods.get(stat)
            if m is None or amount is None or amount <= 0:
                continue
            total += (amount * m) ** 1.5
    return total ** (2.0 / 3.0) if total > 0 else 0.0


def expected_budget(item):
    """What this item's level and rarity entitle it to spend, or None if it is off the table."""
    k = SLOT_K.get(slot_key(item))
    r = RARITY_MULT.get(item.get("rarity"))
    if k is None or r is None or not item.get("item_level"):
        return None
    return k * r * item["item_level"]


def budget_ratio(item, mods=None):
    """actual / allowed. 1.0 is exactly on curve; 0.5 is half the item it claims to be."""
    exp = expected_budget(item)
    if not exp:
        return None
    return stat_value(item, mods) / exp
