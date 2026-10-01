"""
Shaman totem system. Real WOTLK: 4 elements (Earth/Fire/Water/Air), one
totem active per element at a time, and from level 30+ a "Call of the
Elements/Ancestors/Spirits" ability that casts your entire saved loadout
(up to one totem per element) in a single action - Kyle's original ask,
confirmed against real WOTLK Icy Veins/Warcraft Tavern totem guides rather
than assumed.

TOTEM_ELEMENTS maps each totem ability_id to its element, so the loadout
UI can group choices correctly and the totem_loadout effect_type (see
combat/abilities.py) knows which saved ability_ids to actually cast.
"""

TOTEM_ELEMENTS = {
    "shaman_strength_of_earth_totem": "earth",
    "shaman_searing_totem": "fire",
    "shaman_mana_spring_totem": "water",
    "shaman_windfury_totem": "air",
    "shaman_earth_shield": "earth",       # arguably earth-flavored per real WOTLK's Earth Shield line, though it's not a totem itself
    "shaman_mana_tide_totem": "water",
}

#: Which totem_ids are legal to slot for each element - the loadout screen
#: only offers these, and Character.totem_loadout should never contain
#: anything outside this mapping (enforced in Character.set_totem below).
ELEMENTS = ("earth", "fire", "water", "air")


def element_of(totem_ability_id):
    return TOTEM_ELEMENTS.get(totem_ability_id)


def totems_for_element(element):
    """Every known totem ability_id belonging to one element, in a stable
    order. Used to populate the loadout selection screen."""
    return [tid for tid, el in TOTEM_ELEMENTS.items() if el == element]
