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
    "block_rating": 1.9910,     # 19.91 a percent before ratings (15 Nov), / 10
    "block_value": 1.615,
    "crit_chance_physical": 1.5340,     # 15.34 a percent before ratings (15 Nov), / 10
    "crit_chance_spell": 1.3440,     # 13.44 a percent before ratings (15 Nov), / 10
    "defense_rating": 0.8420,     # 8.42 a percent before ratings (15 Nov), / 10
    "dodge_rating": 1.1285,     # 11.285 a percent before ratings (15 Nov), / 10
    "haste": 0.2230,     # 2.23 a percent before ratings (15 Nov), / 10
    "healing_power": 0.690,     # 1.725 before the 15 Nov power rescale (entities/power_scale.py), / 2.5
    "hit_rating": 1.3950,     # 13.95 a percent before ratings (15 Nov), / 10
    "spell_hit_rating": 1.3950,   # the same price: spell hit split from hit (15 Nov 2026)
    "mp5": 4.170,
    "parry_rating": 0.2140,     # 2.14 a percent before ratings (15 Nov), / 10
    "spell_power": 0.717,       # 1.345 before the 15 Nov power rescale, / 1.875
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
    # Kyle, 2026-10-31: "I think we should bump this up roughly. It's too much of a
    # difference." The gap between the best and worst slot was 6.2x (2H 1.232 against a ring
    # 0.198) and is now 3.1x. He set chest/legs, head/shoulder/one-handers, the accessories and
    # ranged; the seven minor slots are mine, placed between his accessory 0.40 and medium 0.55
    # so the ordering he already had is preserved - without them a ring would have been worth
    # more than a pair of gloves.
    #
    # The numbers these replaced, which were FITTED from the game's own items and are what
    # tools/rescale_item_stats.py multiplied every authored item away from:
    #   2H 1.232 | chest .476 legs .473 | shoulder .372 head .370 | main_hand .324
    #   off_hand .290 | wrist .254 feet .251 shield .240 waist .237 hands .233
    #   neck .198 ring .198 trinket .193 back .192 | ranged .172
    "2H": 1.232,
    "chest": 0.650, "legs": 0.650,
    "head": 0.550, "shoulder": 0.550,
    "main_hand_weapon": 0.550, "off_hand_weapon": 0.500,
    "wrist": 0.450, "feet": 0.450, "shield": 0.450, "waist": 0.450, "hands": 0.450,
    "neck": 0.400, "ring": 0.400, "trinket": 0.400, "back": 0.400,
    "ranged_weapon": 0.400,
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


# ---------------------------------------------------------------------------------------------------------
# PRELIMINARY (Kyle, 15 Nov 2026: "Save these numbers as 'preliminary' and we can expand later"). The rate,
# the steepness by rarity and the raid-tier table below are a first pass, to be expanded with the raid tiers.
#
# PAST LEVEL 60 THE LINE BENDS. Kyle, 15 Nov 2026: "Things over lvl 60 and higher ilvl will need a better way
# to measure stats", and "I want past 60, especially with rares, epics and stuff to work towards that the
# linear line changes."
#
# Up to item level 60 a piece's budget is a straight line in its level, as it always was. Past 60 the world
# keeps compounding (combat/world_curve: +3.5% a level from the knee on) while the line only added 1/60th a
# level, so an item level 73 epic was 22% better than a 60 one in a world 56% bigger. Now a rare or better
# spends as if its level were 60 x 1.035^(levels past 60 x STEEPNESS[rarity]): an epic follows the world
# exactly, a rare three quarters of it, a legendary a little faster. Commons and greens stay on the line.
#
#   item level            61     66     73     80     92
#   epic budget level     62.1   73.8   93.8  119.4  180.4   (the line: 61 66 73 80 92)
#   rare budget level     61.6   70.0   83.9  100.5  137.0
#
# What it means for raid tiers (PRELIMINARY): an epic's stats against a level 60 epic's
#   item level   66     70     73     76     80     86     92
#   epic         x1.23  x1.41  x1.56  x1.73  x1.99  x2.45  x3.01
# Rares climb at three quarters of that, so a raid blue never catches the same tier's epic.
#
# Every budget in the game asks this one function: LootGenerator (drops, shops), tools/build_crafted_gear.py
# (crafted, reputation), and expected_budget below (the audits).
# ---------------------------------------------------------------------------------------------------------
BEND_FROM = 60
BEND_RATE = 1.035
STEEPNESS = {"rare": 0.75, "epic": 1.0, "legendary": 1.15}


def budget_level(item_level, rarity):
    """The level an item's stat budget is computed at: its own up to 60, then bending upward for a rare or
    better (see above)."""
    lv = float(item_level or 0)
    k = STEEPNESS.get(rarity)
    if not k or lv <= BEND_FROM:
        return lv
    return max(lv, BEND_FROM * BEND_RATE ** ((lv - BEND_FROM) * k))


def expected_budget(item):
    """What this item's level and rarity entitle it to spend, or None if it is off the table."""
    k = SLOT_K.get(slot_key(item))
    r = RARITY_MULT.get(item.get("rarity"))
    if k is None or r is None or not item.get("item_level"):
        return None
    return k * r * budget_level(item["item_level"], item.get("rarity"))


def budget_ratio(item, mods=None):
    """actual / allowed. 1.0 is exactly on curve; 0.5 is half the item it claims to be."""
    exp = expected_budget(item)
    if not exp:
        return None
    return stat_value(item, mods) / exp
