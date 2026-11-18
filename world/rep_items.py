"""Reputation items: what they are, what standing they need, and that they never go on the auction house.

Kyle, 16 Nov 2026: "neeever allow rep items to be sold! ever! They should have a rep requirement! never ever ever
ever allow rep items to be sold."

WHAT COUNTS. Everything a faction quartermaster sells for standing (data/factions/factions.json, rewards.vendor_stock),
from Honored up:
  * a quartermaster's own gear ("unique:<id>", data/items/faction_rewards.json);
  * the Plaguelands' shoulder inscriptions (tools/plaguelands_inscriptions.py);
  * a recipe sold on a rep shelf, and the gear that recipe makes (its scroll, and anything crafted from it).
The Friendly shelves are potions and food anyone can buy or brew, so they aren't rep items. Neither is a consumable
or material a rep recipe makes (a flask is a flask): only gear.

WHAT IT MEANS.
  * requirement(item) -> (faction_id, tier_id) for a quartermaster's gear and the inscriptions: you need that
    standing to wear it (entities/proficiency.can_equip) or read it on (world/enchanting.apply), and the tooltip
    says so. Gear you crafted from a rep recipe needs none: you earned the recipe, and the crafting is yours.
  * is_rep_item(obj) is True for all of the above, and world/market/goods.can_trade refuses it: no listing, no
    mail. The auction house's own sellers never list one either (world/market/catalog.py).
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_RANK = ("honored", "revered", "exalted")


def _load(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=1)
def _table():
    """({name or id: (faction, tier)} needing standing, {name or id} that's a rep item but needs none)."""
    uniques = dict(_load("data/items/faction_rewards.json").get("items") or {})
    uniques.update(_load("data/items/tabards.json").get("items") or {})     # a tabard needs Friendly
    from world.recipe_manager import _load_all_recipes
    recipes = _load_all_recipes()
    need, rep = {}, set()
    for fid, f in (_load("data/factions/factions.json").get("factions") or {}).items():
        for tiers in ((f.get("rewards") or {}).get("vendor_stock") or {}).values():
            for tier, items in tiers.items():
                if tier not in _RANK and tier != "friendly":
                    continue
                for entry in items:
                    if not isinstance(entry, str):
                        continue
                    if tier == "friendly" and not entry.startswith("unique:"):
                        continue        # Friendly stock is everyday food and potions, except a quartermaster's own
                                        # hand-made item (a tabard), which is never sold anywhere else
                    if entry.startswith("unique:"):
                        uid = entry[len("unique:"):]
                        d = uniques.get(uid) or {}
                        for key in (uid, d.get("name")):
                            if key:
                                need[key] = (fid, tier)
                    elif entry.startswith("inscription_"):
                        need[entry] = (fid, tier)
                    elif entry in recipes:
                        _prof, r = recipes[entry]
                        rep.add(entry)
                        o = r.get("output") or {}
                        if o.get("kind") in ("armor", "weapon", "fixed"):
                            name = (o.get("item") or {}).get("name") or r.get("name")
                            if name:
                                rep.add(name)
                            rep.add("crafted_" + entry)
    return need, frozenset(rep)


def _keys(obj):
    for attr in ("name", "item_id", "material_id", "recipe_id", "id"):
        v = getattr(obj, attr, None)
        if v:
            yield str(v)


def requirement(obj):
    """(faction_id, tier_id) the item needs, or None."""
    need, _rep = _table()
    for k in _keys(obj):
        if k in need:
            return need[k]
    return None


def is_rep_item(obj):
    need, rep = _table()
    return any(k in need or k in rep for k in _keys(obj))


def is_rep_key(key):
    """For the catalog, which works in ids and names rather than objects."""
    need, rep = _table()
    return key in need or key in rep


def meets(character, obj):
    """(ok, reason). Standing belongs to the party (world/faction_manager), so any member who wears it needs the
    party to have earned it."""
    req = requirement(obj)
    if req is None:
        return True, ""
    from world.faction_manager import get_faction_manager
    fm = get_faction_manager()
    if fm.at_least(*req):
        return True, ""
    return False, requirement_text(obj)


def requirement_text(obj):
    """'Requires The Argent Dawn - Revered', or ''."""
    req = requirement(obj)
    if req is None:
        return ""
    from world.faction_manager import get_faction_manager
    f = get_faction_manager().get(req[0])
    name = getattr(f, "name", None) or req[0].replace("_", " ").title()
    return f"Requires {name} - {req[1].title()}"
