"""Harvest finds: the strange things that turn up while you mine, pick herbs, skin and fish (docs/harvest_finds_design.md).

Kyle, 18 Nov 2026: "Why don't we have some quests starting FROM harvesting. Like 'Odd living copper chunk - starts
quest' or 'Mutated silverleaf' --- that'd be cool!" and, for fishing, "the occasional green item and maybe something
unique to fishing! Something fun."

What a gather can turn up, on top of what it always gives (rolled once per gather, after the material is in the bag):
  * A QUEST STARTER (any trade): a rare one-off find for a character in its level band, gathered from its own
    material (or skinned from a beast of the band). Never twice while you hold it, have its quest or have done it.
  * Fishing only:
      - EARTH JUNK now and then from any pool, and every catch from a junk pool (the crates, barrels and floating
        rubbish on the shore are junk pools, world/gathering_manager._populate_fishing);
      - SALVAGE from a salvage pool (the sunken chest, the bottle, the bones, the oil slick): a salvage find worth coin,
        often a green of the zone's level, and now and then a piece of fishing-only gear;
      - a FISHING MOUNT, very rarely, from the ordinary pools of its kind of water;
      - TITLES for fishing milestones (a thousand fish, fifty salvage hauls, the duck, a mount).

Tables are data/gathering/harvest_finds.json, built by tools/build_harvest_finds.py. The counters live on the
character (Character.harvest_log) and save with it.
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "gathering" / "harvest_finds.json"

#: One gather in this many turns up a starter, when one is there to find. With four starters a trade across 1-60, a
#: character who gathers through a band will usually see its starter, and nobody sees it every week.
STARTER_CHANCE = 1 / 60
#: Earth junk from an ordinary pool.
POOL_JUNK_CHANCE = 0.03
#: A salvage haul's green (of the zone's level) and its fishing-only gear.
SALVAGE_GREEN_CHANCE = 0.30
SALVAGE_GEAR_CHANCE = 0.05
#: A fishing mount from an ordinary pool of its kind of water. Very rare, as asked.
MOUNT_CHANCE = 1 / 2000

_data = None
#: the items the last on_gather put in the bag, for a screen that shows loot (the victory panel)
LAST_ITEMS = []


def data():
    global _data
    if _data is None:
        try:
            _data = json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _data = {"starters": [], "earth_junk": [], "salvage": [], "fish_gear": [], "mounts": [], "titles": []}
    return _data


def log(player):
    """The character's harvest counters, made if missing (an older save)."""
    hl = getattr(player, "harvest_log", None)
    if not isinstance(hl, dict):
        hl = {}
        player.harvest_log = hl
    hl.setdefault("fish", 0)
    hl.setdefault("salvage", 0)
    hl.setdefault("mounts", 0)
    hl.setdefault("found", [])
    return hl


def _holds(player, item_id):
    return any(getattr(i, "item_id", None) == item_id for i in getattr(player, "inventory", []))


def _quest_taken(quest_id):
    """True once the quest is active, ready or done: its starter can't be found again."""
    try:
        from world.quest_manager import get_quest_manager
        from world.quest import QuestStatus
        q = get_quest_manager().quests.get(quest_id)
        return q is not None and q.status != QuestStatus.NOT_STARTED
    except Exception:
        return False


def starters_for(player, trade, material_id=None, level=None):
    """The starters this gather could turn up."""
    lvl = level if level is not None else getattr(player, "level", 1)
    out = []
    for s in data()["starters"]:
        if s["trade"] != trade:
            continue
        if s.get("mats") and material_id not in s["mats"]:
            continue
        lo, hi = s["band"]
        if not lo <= lvl <= hi:
            continue
        if _holds(player, s["id"]) or _quest_taken(s["quest"]):
            continue
        out.append(s)
    return out


def _bagged(player, item_id):
    for i in getattr(player, "inventory", []):
        if getattr(i, "item_id", None) == item_id:
            LAST_ITEMS.append(i)
            return


def _give_starter(player, s):
    from entities.loot_item import add_loot_item
    if not add_loot_item(player, s["id"], s["name"], category="quest", description=s["desc"],
                         icon_id=s.get("icon"), starts_quest_id=s["quest"]):
        return None
    _bagged(player, s["id"])
    found = log(player)["found"]
    if s["id"] not in found:
        found.append(s["id"])
    return f"Something odd came up with it: {s['name']}. (It starts a quest.)"


def _give_trash(player, row):
    from entities.loot_item import add_loot_item
    if add_loot_item(player, row["id"], row["name"], category="trash", description=row["desc"],
                     icon_id=row.get("icon"), sell_price=row["price"]):
        return row["name"]
    return None


def _give_collectable(player, cid):
    """A mount or a title's bag item; learning it is the player's own click, as with anything from the Collection."""
    from world import collection as CL
    if CL.learned(cid) or _holds(player, f"collectable_{cid}"):
        return None
    item = CL.make_item(cid)
    if item is None or not player.add_to_inventory(item):
        return None
    return item.name


def _titles(player):
    """Fishing titles whose milestone this character has reached."""
    hl = log(player)
    out = []
    for t in data()["titles"]:
        need = t["needs"]
        if "fish" in need and hl["fish"] < need["fish"]:
            continue
        if "salvage" in need and hl["salvage"] < need["salvage"]:
            continue
        if "mount" in need and hl["mounts"] < need["mount"]:
            continue
        if "found" in need and need["found"] not in hl["found"]:
            continue
        got = _give_collectable(player, t["id"])
        if got:
            out.append(f"You've earned a title: {got}. Learn it from your bags.")
    return out


def _zone_green(player, level, rng):
    """A green of the zone's level for the character's own class, any slot."""
    try:
        from entities.loot_generator import LootGenerator
        gen = LootGenerator()
        return gen.generate_item_for_class(getattr(player, "char_class", None), max(1, level), rarity="uncommon")
    except Exception:
        return None


def _fish_gear(level, rng):
    rows = [g for g in data()["fish_gear"] if g["item_level"] - 8 <= level <= g["item_level"] + 6]
    if not rows:
        return None
    from entities.item import Item
    d = dict(rng.choice(rows))
    return Item.from_dict(d)


def on_gather(player, trade, material_id=None, level=None, node=None, rng=random):
    """Roll the finds for one gather. Returns the lines to tell the player (each already in the bag)."""
    del LAST_ITEMS[:]
    lines = []
    lvl = level if level is not None else getattr(player, "level", 1)
    pool = starters_for(player, trade, material_id, level=lvl)
    if pool and rng.random() < STARTER_CHANCE:
        msg = _give_starter(player, rng.choice(pool))
        if msg:
            lines.append(msg)
    if trade != "fishing":
        return lines

    hl = log(player)
    hl["fish"] += 1
    kind = getattr(node, "find", None)
    d = data()
    if kind == "junk" or (kind is None and rng.random() < POOL_JUNK_CHANCE):
        got = _give_trash(player, rng.choice(d["earth_junk"])) if d["earth_junk"] else None
        if got:
            lines.append(f"Your line also brought up {got}.")
    if kind == "salvage":
        hl["salvage"] += 1
        got = _give_trash(player, rng.choice(d["salvage"])) if d["salvage"] else None
        if got:
            lines.append(f"You haul up salvage: {got}.")
        extra = None
        if rng.random() < SALVAGE_GEAR_CHANCE:
            extra = _fish_gear(lvl, rng)
        if extra is None and rng.random() < SALVAGE_GREEN_CHANCE:
            extra = _zone_green(player, lvl, rng)
        if extra is not None and player.add_to_inventory(extra):
            lines.append(f"Tangled in it: {extra.name}!")
    water = getattr(node, "water", None) or getattr(node, "pool", None)
    if kind is None and water:
        for m in d["mounts"]:
            if water in m["pools"] and rng.random() < MOUNT_CHANCE:
                got = _give_collectable(player, m["id"])
                if got:
                    hl["mounts"] += 1
                    lines.append(f"Something enormous is on the line... {got}!")
                break
    lines += _titles(player)
    return lines
