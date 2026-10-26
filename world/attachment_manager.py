"""Weapon attachments - a permanent, one-time boost fitted to a ranged weapon.

Kyle, 2026-10-26: "We can build scopes as a permanent gun boost. We can build
crossbow and bow equivalent in woodworking too."

HOW THIS DIFFERS FROM UPGRADE KITS (world/upgrade_manager.py)
-------------------------------------------------------------
Both are consumables applied to an item to improve it permanently, and both
are deliberately kept as separate systems because the rules differ on every
axis that matters:

                        upgrade kit              attachment
    eligible items      crafted gear only        ANY ranged weapon, dropped
                        (is_crafted)             or crafted - a scope does not
                                                 care who made the rifle
    matched by          crafting_material        weapon_type
                        ("copper" kit on
                         copper gear)
    applications        exactly 2                exactly 1
    effect              rarity +1 rank, then     flat weapon damage, and
                        stats +10%/+20%          nothing else
    stacks with         the other                the other

An item can carry BOTH: a crafted rifle can be kit-upgraded twice AND scoped.
They never read or write each other's fields.

WHY FLAT DAMAGE
---------------
A scope in Classic adds flat damage to the weapon rather than a percentage or
a stat line, and flat damage is the one thing this engine's ranged weapons
already have that nothing else modifies - Item.weapon_damage_min/max, which
combat reads directly. A percentage would compound with the kit's own stat
bump and make a double-improved weapon swing wildly; flat is predictable and
is what the source convention does.

WHO MAKES WHAT
--------------
    Engineering  -> SCOPES, fitted to guns and crossbows (mechanical sights)
    Woodworking  -> LIMBS AND NOCKS, fitted to bows and crossbows (worked wood)

Crossbows accept either, which is deliberate: it is the one ranged weapon both
professions can serve, so neither profession fully locks a player out of the
other's line.
"""
import json
from pathlib import Path


#: attachment material_id -> what it fits and what it gives.
#:
#: weapon_types is checked against Item.weapon_type, NOT against the slot -
#: every ranged weapon sits in the "ranged" slot, so the slot cannot tell a
#: bow from a gun.
ATTACHMENTS = {
    # ── Engineering: scopes (guns + crossbows) ───────────────────────────
    "scope_crude": {
        "name": "Crude Scope",
        "weapon_types": ("gun", "crossbow"),
        "damage": 2,
        "profession": "engineering",
    },
    "scope_standard": {
        "name": "Standard Scope",
        "weapon_types": ("gun", "crossbow"),
        "damage": 4,
        "profession": "engineering",
    },
    "scope_precision": {
        "name": "Precision Scope",
        "weapon_types": ("gun", "crossbow"),
        "damage": 7,
        "profession": "engineering",
    },
    "scope_resonant": {
        "name": "Resonant Scope",
        "weapon_types": ("gun", "crossbow"),
        "damage": 11,
        "profession": "engineering",
    },
    # ── Woodworking: limbs and nocks (bows + crossbows) ──────────────────
    "nock_horn": {
        "name": "Horn Nock",
        "weapon_types": ("bow", "crossbow"),
        "damage": 2,
        "profession": "woodworking",
    },
    "limbs_laminated": {
        "name": "Laminated Limbs",
        "weapon_types": ("bow", "crossbow"),
        "damage": 4,
        "profession": "woodworking",
    },
    "pin_truesight": {
        "name": "Truesight Pin",
        "weapon_types": ("bow", "crossbow"),
        "damage": 7,
        "profession": "woodworking",
    },
    "limbs_heartwood": {
        "name": "Heartwood Limbs",
        "weapon_types": ("bow", "crossbow"),
        "damage": 11,
        "profession": "woodworking",
    },
}


def is_attachable(item):
    """True if this item is a weapon any attachment could ever fit.

    Checked separately from can_attach so the UI can say "nothing fits this"
    about a sword (never attachable) differently from "you already scoped
    this rifle" (attachable, but done).
    """
    wtype = getattr(item, "weapon_type", None)
    if not wtype:
        return False
    return any(wtype in a["weapon_types"] for a in ATTACHMENTS.values())


def attachment_on(item):
    """The attachment fitted to this item, as its spec dict, or None."""
    aid = getattr(item, "attachment", None)
    return ATTACHMENTS.get(aid) if aid else None


def attachments_for_item(item):
    """Every attachment material_id that would fit this weapon.

    Empty if the weapon already has one - an attachment is permanent and
    single, so a scoped rifle is finished. Returning [] rather than the full
    list keeps the UI from offering a second one it would then refuse.
    """
    if getattr(item, "attachment", None):
        return []
    wtype = getattr(item, "weapon_type", None)
    if not wtype:
        return []
    return [aid for aid, spec in ATTACHMENTS.items() if wtype in spec["weapon_types"]]


def can_attach(character, item, attachment_id):
    """True only if: the id is a real attachment; it fits this weapon's
    weapon_type; the weapon has no attachment already; and the character
    actually holds one.

    Deliberately does NOT check is_crafted. Unlike an upgrade kit, a scope
    works on a weapon that dropped off a boss - that is the whole point of
    it being a separate system.
    """
    spec = ATTACHMENTS.get(attachment_id)
    if spec is None:
        return False
    wtype = getattr(item, "weapon_type", None)
    if not wtype or wtype not in spec["weapon_types"]:
        return False
    if getattr(item, "attachment", None):
        return False
    return character.get_material_quantity(attachment_id) >= 1


def attach(character, item, attachment_id):
    """Consume one attachment and fit it permanently to `item`.

    Mutates and returns the item (same reasoning as upgrade_item: this is
    conceptually the same physical rifle with a sight on it, and mutating in
    place means every existing reference - equipped slot, inventory list -
    sees it without a swap-out step).

    Returns the item on success, or None on failure. can_attach's checks
    re-run here rather than being trusted from the caller, the same defensive
    convention upgrade_item and every crafting manager use, so the
    attachment is never consumed on a failed fit.
    """
    if not can_attach(character, item, attachment_id):
        return None
    if not character.consume_material(attachment_id, 1):
        return None

    spec = ATTACHMENTS[attachment_id]
    bonus = spec["damage"]

    # Flat damage to both ends of the roll, so average and spread both move
    # and the weapon never ends up with min > max.
    item.weapon_damage_min = (item.weapon_damage_min or 0) + bonus
    item.weapon_damage_max = (item.weapon_damage_max or 0) + bonus
    item.attachment = attachment_id
    # Worth a little more second-hand, same gesture upgrade_item makes.
    item.sell_price = max(item.sell_price, int(item.sell_price * 1.1))
    return item


def attachment_label(item):
    """'Crude Scope' / 'Heartwood Limbs' / None - for the item card.

    Like upgrade_tag, this is display only: fitting a scope never renames the
    weapon. A scoped Iron Rifle is still an Iron Rifle.
    """
    spec = attachment_on(item)
    return spec["name"] if spec else None
