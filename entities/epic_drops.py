"""Named epics: the rare world drop, and the occasional purple off a dungeon boss.

Kyle, 2026-10-28: "We can get the occasional drops as epic after lvl 30 in Dungeons and also for
world drop after lvl 30. Think of how wow does it with world drops."

WHY THESE ARE A SEPARATE ROLL AND NOT A RARITY TWEAK. LootGenerator.roll_rarity already gates epic
at level 30, so in principle the procedural roller could hand out purples and the job would be
done. It cannot, for two reasons. Hand-authored boss pools bypass rarity entirely -
get_fixed_boss_loot returns a fixed rare before the procedural roll happens, and all 44 bosses above
level 30 have one. And a procedurally generated purple is a stat block, not a thing: WoW's world
epics are memorable because they are specific items with names people recognise, which is the part
you cannot generate. So these are twenty-two authored items rolled on their own.

THE RATES ARE THE DESIGN. A world epic is the drop somebody tells people about: about one in four
hundred kills, rolled ONCE a kill, then one epic picked by the zone's level. A dungeon's final boss
carries a far better chance on epics of its own, because that is the reason to go in rather than grind
a hillside. The 16 Nov rules are set out below and in docs/epic_drops_plan.md.
"""
import json
import random
from pathlib import Path

# ---------------------------------------------------------------------------------------------------------------
# 16 Nov 2026 (docs/epic_drops_plan.md). Kyle: "have the roll first then a second roll to determine the epic based on
# lvl....this will prevent a massive swamp of epics dropping", "not picked by player level! picked by zone level",
# and for dungeons: "Usually epics in dungeons are found on the final boss with a low thing like 4% or 5% chance".
#
#   * ONE roll a kill, never one per epic. A level 30+ kill rolls WORLD_CHANCE once; on a hit, ONE epic is picked
#     from those whose required level fits the zone's band (data/zones/zone_levels.json). A level 60 farming a
#     level 35 zone gets that zone's epics.
#   * Only a dungeon's FINAL boss rolls a dungeon epic (data/loot/epic_drops.json final_bosses): 5% on its own
#     epics from 40 up, 2% from 30 to 39 (its own, or the shared pool). Every other kill, bosses included, takes
#     the world roll.
# ---------------------------------------------------------------------------------------------------------------

#: Level at which epics begin, matching the procedural roller's own gate in data/items/rarity.json.
MIN_LEVEL = 30

#: Per-kill chance for a named world epic, on anything at or above MIN_LEVEL. About 1 in 400 (Kyle kept it).
WORLD_CHANCE = 0.0025

#: A final boss from 40 up; the table carries each boss's own chance (0.05 from 40, 0.02 from 30 to 39).
BOSS_CHANCE = 0.05

#: The window around the zone's band an epic's required level must sit in: a little under the band's floor (so a
#: zone always has a good handful) and one over its top.
BAND_BELOW, BAND_ABOVE = 3, 1

SHARED_30S = "shared_30s"

_POOL = None


def _pool():
    global _POOL
    if _POOL is None:
        path = Path(__file__).parent.parent / "data" / "loot" / "epic_drops.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        _POOL = {"world": data.get("world", []), "dungeon": data.get("dungeon", []),
                 "final_bosses": data.get("final_bosses", {})}
    return _POOL


def zone_band(zone_name):
    """(low, high) for a zone, by display name or key, or None."""
    if not zone_name:
        return None
    from world.zone_levels import band, _load
    b = band(zone_name)
    if not b:
        key = str(zone_name).lower().replace(" ", "_").replace("'", "")
        b = next((v for k, v in _load().items() if k.lower().replace(" ", "_").replace("'", "") == key), None)
    return (int(b[0]), int(b[1])) if b else None


def world_pool(low, high):
    """The world epics a zone banded low-high can drop."""
    return [d for d in _pool()["world"]
            if low - BAND_BELOW <= d.get("required_level", 1) <= high + BAND_ABOVE]


def boss_pool(boss_name):
    """A final boss's epics: its own, or the shared 30-39 pool if it has none."""
    own = [d for d in _pool()["dungeon"] if d.get("boss") == boss_name]
    return own or [d for d in _pool()["dungeon"] if d.get("boss") == SHARED_30S]


def _item(d):
    from entities.item import Item
    from world.jewelcrafting import socket_authored
    # data is already on the current power scale (entities/power_scale.py): say so, or it is lifted twice
    return socket_authored(Item.from_dict({**d, "power_scale": 3}))


def roll_epic(enemy, player_level=None, zone=None, rng=random):
    """An Item for a named epic, or None. Rolled once per defeated enemy.

    `zone` is the zone the fight is in; without one (or for a zone with no band) the enemy's own level stands in
    for the band. `player_level` is accepted for old callers and ignored: the zone decides (Kyle, 16 Nov).
    """
    level = max(1, int(getattr(enemy, "level", 1)))
    if level < MIN_LEVEL:
        return None

    final = _pool()["final_bosses"].get(getattr(enemy, "name", None))
    if final and getattr(enemy, "is_boss", False):
        if rng.random() >= final.get("chance", BOSS_CHANCE):
            return None
        pool = boss_pool(enemy.name)
        return _item(rng.choice(pool)) if pool else None

    if rng.random() >= WORLD_CHANCE:
        return None
    low, high = zone_band(zone) or (level, level)
    pool = world_pool(max(low, MIN_LEVEL), max(high, MIN_LEVEL))
    return _item(rng.choice(pool)) if pool else None
