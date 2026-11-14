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

THE RATES ARE THE DESIGN. A world epic is meant to be the drop somebody tells people about, so it
sits at roughly one in four hundred kills. A level 30+ boss carries a far better chance, because
that is the reason to go into a dungeon rather than grind a hillside. Alongside this, the procedural
epic weight came down from 3 to 1: leaving it where it was meant random purples would have
outnumbered the designed ones, and then naming them would have been pointless.

LEVEL, NOT JUST CHANCE. An epic you cannot equip for ten levels is a tease rather than a reward, so
the pool is filtered to what the player can nearly use - the same two-level lead the procedural
roller allows itself. At level 30 that means one item is eligible; the pool opens as they climb.
"""
import json
import random
from pathlib import Path

#: Level at which epics begin, matching the procedural roller's own gate in data/items/rarity.json.
MIN_LEVEL = 30

#: Per-kill chance for a named world epic, on anything at or above MIN_LEVEL.
WORLD_CHANCE = 0.0025

#: Chance on a boss at or above MIN_LEVEL. This is the reason to run the dungeon.
BOSS_CHANCE = 0.06

#: How far above the player's level a dropped epic may require, same as ITEM_LEVEL_LEAD_CAP.
LEVEL_LEAD = 2

_POOL = None


def _pool():
    global _POOL
    if _POOL is None:
        path = Path(__file__).parent.parent / "data" / "loot" / "epic_drops.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        _POOL = {"world": data.get("world", []), "dungeon": data.get("dungeon", [])}
    return _POOL


def _eligible(bucket, player_level):
    return [d for d in _pool()[bucket]
            if d.get("required_level", 1) <= player_level + LEVEL_LEAD]


def roll_epic(enemy, player_level, in_dungeon=False, rng=random):
    """An Item for a named epic, or None. Rolled once per defeated enemy.

    A boss at or above MIN_LEVEL rolls the dungeon pool; anything else rolls the world pool. The
    `in_dungeon` flag is accepted but not required to be true for the boss roll, because a boss is
    a boss whether or not the zone is flagged as a dungeon - several of the level 30+ ones stand in
    caves and open zones.
    """
    level = max(1, int(getattr(enemy, "level", 1)))
    if level < MIN_LEVEL or player_level < MIN_LEVEL:
        return None

    is_boss = bool(getattr(enemy, "is_boss", False))
    bucket = "dungeon" if is_boss else "world"
    chance = BOSS_CHANCE if is_boss else WORLD_CHANCE
    if rng.random() > chance:
        return None

    pool = _eligible(bucket, player_level)
    if not pool:
        return None

    from entities.item import Item
    from world.jewelcrafting import socket_authored
    return socket_authored(Item.from_dict(dict(rng.choice(pool))))
