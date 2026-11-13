"""What an item IS, in one line: "Leather Chest", "Two-Hand Axe", "One-Hand Sword", "Shield".

Playtest, 12 Nov: "When selling gear (armor) you can't see if it is cloth, leather, etc so you
have to close out of the menu and check your inventory", and "no way to tell if a weapon is 1h
or 2h". The vendor row said only the slot ("Chest", "Main Hand"), and nothing anywhere said how
many hands a weapon takes - a two-hander and a one-hander were both "Main Hand". One function,
used by the bag tooltip, the vendor row and the vendor tooltip, so they cannot disagree.
"""

HANDS = {"two_hand": "Two-Hand", "main_or_off": "One-Hand", "main_hand": "Main Hand",
         "off_hand": "Off Hand", "ranged": "Ranged"}
KINDS = {"sword": "Sword", "axe": "Axe", "mace": "Mace", "fist_weapon": "Fist Weapon"}


def item_kind(item):
    """'' for anything that is not gear."""
    weapon = getattr(item, "weapon_type", None)
    slot = str(getattr(item, "slot", "") or "").replace("_", " ").title()
    if weapon:
        from entities.equipment import _load_weapon_type_hand
        hand = _load_weapon_type_hand(weapon)
        base = str(weapon)
        for suffix in ("_1h", "_2h"):
            if base.endswith(suffix):
                base = base[:-len(suffix)]
        name = KINDS.get(base, base.replace("_", " ").title())
        if hand == "off_hand":                       # Shield, Tome: the name already says it
            return f"{name} (Off Hand)"
        return f"{HANDS.get(hand, '')} {name}".strip()
    armor = getattr(item, "armor_type", None)
    if armor and armor not in ("accessory", "weapon"):
        return f"{str(armor).title()} {slot}".strip()
    return slot
