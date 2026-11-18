"""Faction tabards (docs/tabards_design.md, tools/build_tabards.py).

Kyle, 18 Nov 2026: wearing a faction's tabard shifts the rep you earn to that faction, Cataclysm style. His answers:
dungeon kills only (quest and zone rep never move) and heroic dungeons only. Normal dungeons stop paying any faction
at Revered, so a heroic in a tabard is the dungeon road to Exalted with whichever faction you pick.
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=1)
def _by_name():
    try:
        items = json.loads((ROOT / "data/items/tabards.json").read_text(encoding="utf-8")).get("items") or {}
    except (OSError, ValueError):
        items = {}
    return {d["name"]: d["tabard_of"] for d in items.values()}


def faction_of(item):
    """The faction a tabard item champions, or None."""
    if item is None or getattr(item, "slot", None) != "tabard":
        return None
    return _by_name().get(getattr(item, "name", None))


def worn_by(character):
    """The faction this character's tabard champions, or None."""
    eq = getattr(character, "equipment", None)
    slots = getattr(eq, "slots", None) or {}
    return faction_of(slots.get("tabard"))
