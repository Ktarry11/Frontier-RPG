"""Keep an epic's icon its own: a quest or reputation reward that drew one gets another (Kyle, 16 Nov 2026: "every
unique item in the game can only have ONE icon"; tools/qa_crafted_icons.py check 5).

Used by the reward builders that author through build_crafted_gear.author (whose colour picker knows nothing about
epics): tools/build_scarlet_monastery_quests.py, tools/build_plaguelands_rewards.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_EPIC = None


def epic_icons():
    """Every icon an epic owns: the named epics, the crafted epics, the reputation epics."""
    global _EPIC
    if _EPIC is not None:
        return _EPIC
    out = set()
    ep = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    out |= {d.get("icon_id") for k in ("world", "dungeon") for d in ep.get(k, [])}
    for path in sorted((ROOT / "data").glob("*/recipes.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        for book in (d["professions"].values() if "professions" in d else [d]):
            for r in (book.get("recipes") or {}).values():
                it = (r.get("output") or {}).get("item") or {}
                if it.get("rarity") in ("epic", "legendary"):
                    out.add(it.get("icon_id"))
    fr = json.loads((ROOT / "data/items/faction_rewards.json").read_text(encoding="utf-8"))["items"]
    out |= {i.get("icon_id") for i in fr.values() if i.get("rarity") == "epic"}
    out.discard(None)
    _EPIC = out
    return out


def unclash(item):
    """Give a non-epic item another icon if the one it drew belongs to an epic. True if it changed."""
    if item.get("rarity") in ("epic", "legendary") or item.get("icon_id") not in epic_icons():
        return False
    from entities.boss_loot import resolve_icon
    for i in range(1, 80):
        ic = resolve_icon(slot=item.get("slot"), armor_type=item.get("armor_type"),
                          weapon_type=item.get("weapon_type"), rarity=item.get("rarity"),
                          seed=f"unclash{i}:{item.get('name')}", explicit=None)
        if ic and ic not in epic_icons():
            item["icon_id"] = ic
            return True
    return False
