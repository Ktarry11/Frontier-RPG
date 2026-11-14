"""T0 set tokens: what a boss drops, and what an Artifact Keeper gives you for one.

Kyle, 13 Nov 2026. Thirty classes means ninety different bracers, belts and legs; a boss that
dropped "the Warlock bracers" would be handing a party of five something none of them can wear
five times in six. So a boss drops a TOKEN for a slot and an armour type ("Bindings of the Black
Hollow (Plate)"), and an Artifact Keeper trades it for that slot's piece of the set of any class
in your party that wears that armour. "20% token drop. with one guaranteed from the last boss."

Data: data/items/set_tokens.json, built by tools/build_tempest_loot.py.
  roll(boss)                 what the boss drops this kill: [] or one drop definition
  redeemable(player, party)  every trade a keeper can offer right now
  redeem(player, token, m)   do one: the token leaves the bag, the set piece goes in
"""
import json
import random
from pathlib import Path

_PATH = Path(__file__).parent.parent / "data" / "items" / "set_tokens.json"
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        try:
            _DATA = json.loads(_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _DATA = {"chance": 0.0, "tokens": {}, "bosses": {}}
    return _DATA


def token(token_id):
    return data()["tokens"].get(token_id)


def roll(boss_name, rng=random):
    """The token this boss drops on this kill, as a list of loot-item drop definitions (empty, or
    one). A boss marked guaranteed always drops one; any other rolls the shared chance. Which
    armour type it is, is picked evenly from the types that boss carries."""
    spec = data()["bosses"].get(boss_name)
    if not spec or not spec.get("types"):
        return []
    if not spec.get("guaranteed") and rng.random() >= data().get("chance", 0.0):
        return []
    token_id = f"t0_token_{spec['slot']}_{rng.choice(spec['types'])}"
    t = token(token_id)
    if t is None:
        return []
    # category "material": it stacks, it is not tied to a quest, and it drops whether or not
    # anything "needs" it. Rarity epic so it stands out in the bag and on the victory screen.
    return [{"item_id": token_id, "name": t["name"], "category": "material", "chance": 1.0,
             "description": t["description"], "icon_id": t.get("icon_id"), "rarity": "epic",
             "sell_price": 0}]


def _set_for(member):
    """(set_id, definition) of the T0 set for this character's class, or (None, None)."""
    from world import gear_sets
    cls = (getattr(member, "char_class", "") or "").lower()
    for set_id, definition in gear_sets.all_sets().items():
        if definition.get("tier") == "T0" and definition.get("class", "").lower() == cls:
            return set_id, definition
    return None, None


def redeemable(player, party):
    """[(token_id, token name, member, set_id, slot, piece name)] - one row for every token in
    the player's bag and every party member whose class set is made of that armour."""
    from entities.loot_item import count_loot_items
    members = list(getattr(party, "members", []) or []) or [player]
    out = []
    for token_id, t in data()["tokens"].items():
        if count_loot_items(player, token_id) <= 0:
            continue
        for member in members:
            set_id, definition = _set_for(member)
            if not definition or definition.get("armor_type") != t["armor_type"]:
                continue
            versions = definition.get("variants") or {}
            first = next(iter(versions), None)
            piece = ((versions.get(first) or {}).get("pieces") or {}).get(t["slot"])
            if piece:
                out.append((token_id, t["name"], member, set_id, t["slot"], piece["name"]))
    return out


def redeem(player, token_id, member):
    """Trade one token for `member`'s class piece. Returns (ok, message). The piece goes into the
    player's bag (the party shares one), in the set's first version; the keeper swaps versions
    for free afterwards, as with any set piece."""
    from entities.loot_item import count_loot_items, remove_loot_items
    from world import gear_sets
    t = token(token_id)
    set_id, definition = _set_for(member)
    if t is None or count_loot_items(player, token_id) <= 0:
        return False, "You are not carrying that token."
    if not definition or definition.get("armor_type") != t["armor_type"]:
        return False, f"{member.name} does not wear {t['armor_type']}."
    piece = gear_sets.make_piece(set_id, t["slot"])
    if piece is None:
        return False, "That set has no piece for this slot."
    if not player.add_to_inventory(piece):
        return False, "Your bags are full."
    remove_loot_items(player, token_id, 1)
    return True, f"{t['name']} traded for {piece.name}."
