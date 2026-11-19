"""Heroic dungeons (docs/heroic_design.md).

Kyle, 18 Nov 2026: every dungeon gets a level-60 heroic. His answers:
  * you pick Normal or Heroic at the dungeon's door, at level 60;
  * each heroic once per market day;
  * level-60 elites, one heroic-only trick per boss, and now and then a heroic-only boss (stage 3);
  * the same loot as normal with better stats, item level 66 (the level-60 ladder: Revered rep 66, Exalted 68,
    T1 68, Cairne 71), plus a heroic-only item per dungeon and badges for a vendor (stage 2);
  * rep past Revered, and a faction's tabard takes the kill rep (world/faction_manager.award_for_kill).
  * The two special kinds of place get their own, higher heroics: skull zones 68 and frontier zones 69 (Kyle: "skull
    zones and frontier zones can be 68 and 69 heroics...so different"). Not built yet; SPECIAL_ITEM_LEVEL holds the
    numbers so they're here when they are.

A heroic RUN starts at a dungeon's door and lasts until the party walks back out of the dungeons: the floors and
wings reached from inside are the same run. The run and the day's lockouts ride in the character's TravelManager.
"""
import copy

#: what every heroic monster is, whatever the dungeon's normal level
MONSTER_LEVEL = 60
#: the character level a heroic opens at
OPEN_LEVEL = 60
#: what heroic loot is: the normal drop, rebuilt at this level, worn at 60, on the item curve
ITEM_LEVEL = 66
WORN_AT = 60
#: Kyle, 18 Nov 2026: "Ensure vendor trash Is also appropriately improved in heroics as are chests drops."
#: A heroic's trash gear and side chests roll at this level (above a normal level-60 dungeon's 60-63), its boss
#: chests at ITEM_LEVEL, and its coin and vendor trash pay this much more than a normal level-60 kill.
TRASH_ITEM_LEVEL = 63
COIN_MULT = 1.5
#: the heroics of the two special kinds of place, for when they're built (Kyle, 18 Nov 2026)
SPECIAL_ITEM_LEVEL = {"skull": 68, "frontier": 69}
#: a market day is 24 market hours (world/market/market.py's clock)
DAY_HOURS = 24.0


def _tm():
    from world.travel_manager import get_travel_manager
    return get_travel_manager()


def is_heroic_dungeon(zone_name):
    """A real dungeon that has a heroic: every dungeon in world/zone_classification.DUNGEONS. The hidden levels
    under dungeons are dungeons too but aren't heroic (their own heroics are the special kind, not built yet)."""
    if not zone_name:
        return False
    from world.zone_classification import dungeon_name
    return dungeon_name(zone_name) is not None        # a display name, or the key combat uses


def day_of(clock):
    return int(float(clock or 0.0) // DAY_HOURS)


def market_clock(party=None):
    try:
        from world.market.market import market_of
        return market_of(party).clock
    except Exception:
        return 0.0


def offers_choice(dest_zone, from_zone, leader):
    """True when walking from `from_zone` into `dest_zone` should ask Normal or Heroic: into a dungeon from
    outside the dungeons, with a level-60 leader."""
    from world.zone_classification import is_dungeon
    return (is_heroic_dungeon(dest_zone) and not is_dungeon(from_zone or "")
            and (getattr(leader, "level", 0) or 0) >= OPEN_LEVEL)


def locked_today(run, clock, tm=None):
    tm = tm or _tm()
    return tm.heroic_locks.get(run) == day_of(clock)


def start(run, clock, tm=None):
    """Begin a heroic run of `run` (the dungeon entered from outside). -> (ok, message). Locks it for the day."""
    tm = tm or _tm()
    if locked_today(run, clock, tm):
        return False, f"You've already run heroic {run} today. It opens again at the next market day."
    tm.heroic_locks[run] = day_of(clock)
    tm.heroic_run = run
    return True, f"Heroic {run}: everything inside is level 60 and elite. Good luck."


def leave(tm=None):
    (tm or _tm()).heroic_run = None


def on_zone_change(from_zone, to_zone, tm=None):
    """Called on every zone change (world/zone_manager.transition_to_zone): walking out of the dungeons ends the
    run. The day's lockout stays."""
    from world.zone_classification import is_dungeon
    tm = tm or _tm()
    if tm.heroic_run and not is_dungeon(to_zone or ""):
        tm.heroic_run = None


def active(zone_name=None):
    """True when the party is on a heroic run and standing in one of its dungeons."""
    try:
        tm = _tm()
    except Exception:
        return False
    if not getattr(tm, "heroic_run", None):
        return False
    if zone_name is None:
        try:
            from world.zone_manager import LIVE
            zone_name = LIVE.current_zone.name
        except Exception:
            return False
    return is_heroic_dungeon(zone_name)


# ----------------------------------------------------------------------------------------------- materials
#: Kyle, 18 Nov 2026: the two lowest top-tier ores, woods and gems come from "Heroic bosses, chests and eventually the
#: lvl 60 zones" (entities/material_tiers.LEVEL60_TOP). (kind, weight, quantity range) for one find.
MATERIAL_FINDS = (("ore", 2, (2, 4)), ("wood", 2, (2, 4)), ("gem", 1, (1, 1)))
#: a heroic side chest holds one of these finds instead of gear this often
CHEST_MATERIAL_CHANCE = 0.4


def roll_materials(rng=None):
    """One find of the first top-tier ore, wood or gem: [(material_id, quantity)]."""
    import random as _r
    from entities.material_tiers import LEVEL60_TOP, HEROIC_TOP_WEIGHTS
    rng = rng or _r
    kind, _w, (lo, hi) = rng.choices(MATERIAL_FINDS, weights=[w for _k, w, _q in MATERIAL_FINDS], k=1)[0]
    mats = LEVEL60_TOP[kind]
    mid = rng.choices(mats, weights=list(HEROIC_TOP_WEIGHTS[:len(mats)]), k=1)[0]
    return [(mid, rng.randint(lo, hi))]


#: a heroic boss drops one of the Master epic patterns this often (tools/build_master_crafting.py, source "heroic")
PATTERN_CHANCE = 0.15


def roll_pattern(rng=None):
    """A Master epic pattern's recipe id for a heroic boss to drop, or None."""
    import random as _r
    rng = rng or _r
    if rng.random() >= PATTERN_CHANCE:
        return None
    from world.recipe_manager import all_recipes_by_source
    pool = sorted(all_recipes_by_source("heroic"))
    return rng.choice(pool) if pool else None


# ---------------------------------------------------------------------------------------------------------- loot
def _weapon_hit(level):
    """The generator's average weapon hit for an item level (entities/loot_generator: item_level * 1.1 + 6.4)."""
    return level * 1.1 + 6.4


def heroic_def(item_def, item_level=ITEM_LEVEL):
    """The heroic version of one authored drop: the same item, rebuilt at `item_level`, worn at 60, with its stat mix
    kept and its stats put on the item curve. Its weapon damage and armour grow with the level as the loot
    generator's do. Already at or above the level (a hidden boss's epic), it's left alone."""
    from entities.item_budget import fit_to_curve
    d = copy.deepcopy(item_def)
    old = d.get("item_level") or 1
    if old >= item_level:
        return d
    d["item_level"] = item_level
    d["required_level"] = WORN_AT
    if d.get("rarity") in (None, "common", "uncommon"):
        d["rarity"] = "rare"                 # heroic loot is blue at the least
    fit_to_curve(d, target=1.0)
    k = _weapon_hit(item_level) / _weapon_hit(old)
    for key in ("weapon_damage_min", "weapon_damage_max"):
        if d.get(key):
            d[key] = max(1, int(round(d[key] * k)))
    if d.get("armor_value"):
        d["armor_value"] = max(1, int(round(d["armor_value"] * item_level / old)))
    if d.get("sell_price"):
        d["sell_price"] = max(d["sell_price"], int(item_level * 1.7 * 30))
    d["heroic"] = True
    return d
