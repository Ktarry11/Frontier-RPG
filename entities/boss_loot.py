"""
Fixed/curated boss loot tables - a boss listed here drops ONE item drawn
from its own hand-authored pool instead of combat/combat_engine.py's
normal generate_boss_loot() fully-procedural roll.

Kyle's ask (2026-09-06): design real loot for Sunken Grotto of the Deep's
three bosses (Giant Crab, Undead Pirate Captain, Naga Shrine Guardian),
with specific stat combos per item ("crab will have int/sp shield, str/sp
boots, and tank trinket", etc). That's an entirely new capability, not a
tweak - previously EVERY boss in the game, dungeon or otherwise, only
ever dropped a fully-random item from generate_boss_loot(), with no way
to say "this exact boss drops this exact themed item." This module adds
that without touching the existing procedural path at all - a boss not
listed in BOSS_LOOT_TABLES (i.e. every boss except these three, for now)
falls through to generate_boss_loot() exactly as before. See
combat/combat_engine.py's post-victory loot roll for the actual call
site and fallback order.

Data lives in data/loot/*.json (currently just
sunken_grotto_boss_loot.json), one file per dungeon/zone so a future
dungeon's fixed loot doesn't turn this into one giant file. All files
matching data/loot/*.json are auto-loaded and merged by boss name at
import time.
"""
import json
import random
import uuid
from pathlib import Path

from entities.item import Item
from gear_icons import resolve_icon


_LOOT_DIR = Path(__file__).parent.parent / "data" / "loot"
_boss_loot_cache = None


def _load_boss_loot_tables():
    """Merge every data/loot/*.json file into one {boss_name: [item_def,
    ...]} dict, cached after first read. A boss name colliding across two
    files (shouldn't happen - each dungeon's bosses are unique) would
    have the later file win; not worth guarding against for a fixed,
    hand-authored data set this small."""
    global _boss_loot_cache
    if _boss_loot_cache is not None:
        return _boss_loot_cache

    tables = {}
    if _LOOT_DIR.exists():
        for path in sorted(_LOOT_DIR.glob("*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            for boss_name, item_defs in data.items():
                if boss_name.startswith("_"):  # "_notes" etc - not a boss
                    continue
                tables[boss_name] = item_defs
    _boss_loot_cache = tables
    return tables


def _item_from_def(item_def):
    """Build a real Item from one hand-authored JSON entry. Mirrors the
    id/icon conventions the procedural generator and starting-gear system
    both already use (entities/loot_generator.py, entities/
    starting_gear.py) so a fixed boss drop is indistinguishable in the UI
    from a procedural one - same item_id slug shape (never displayed),
    same icon-picking calls."""
    weapon_type = item_def.get("weapon_type")
    armor_type = item_def.get("armor_type")
    slug = weapon_type or armor_type or item_def["slot"]
    item_id = f"fixedboss_{slug}_{uuid.uuid4().hex[:6]}"

    # SEEDED ON THE ITEM'S NAME, not rolled. Kyle, 7 Nov: "hand crafted boss
    # items don't always link to the same gear icon. This should be fixed as
    # they're hand crafted. Right now I can have 1 unique shield with 3
    # icons."
    #
    # He is right and the comment above this function was the tell - it says
    # these use "the same icon-picking calls" as the procedural generator,
    # and that was exactly the bug. A procedural drop SHOULD roll its icon:
    # it is a random item and no two copies are the same object. A fixed boss
    # drop is one authored object with one name, so rolling meant the item
    # had no stable identity - kill the boss three times and Stormbreak Aegis
    # came back as three different shields.
    #
    # An explicit icon_id in the JSON wins over both, so a drop that wants a
    # specific picture can simply say so.
    icon_id = resolve_icon(
        slot=item_def["slot"], armor_type=armor_type, weapon_type=weapon_type,
        rarity=item_def.get("rarity"), seed=f"fixedboss:{item_def['name']}",
        explicit=item_def.get("icon_id"))

    return Item(
        item_id=item_id,
        name=item_def["name"],
        slot=item_def["slot"],
        item_level=item_def["item_level"],
        rarity=item_def["rarity"],
        armor_type=armor_type,
        weapon_type=weapon_type,
        stat_template=item_def.get("stat_template"),
        primary_stats=dict(item_def.get("primary_stats", {})),
        secondary_stats=dict(item_def.get("secondary_stats", {})),
        armor_value=item_def.get("armor_value", 0),
        required_level=item_def.get("required_level", max(1, item_def["item_level"] - 2)),
        sell_price=item_def.get("sell_price", max(1, int(item_def["item_level"] * 1.7))),
        flavor_text=item_def.get("flavor_text", ""),
        weapon_damage_min=item_def.get("weapon_damage_min", 0),
        weapon_damage_max=item_def.get("weapon_damage_max", 0),
        attack_speed=item_def.get("attack_speed", 0.0),
        block_value=item_def.get("block_value", 0),
        icon_id=icon_id,
        # A trinket that does something (see Item.proc). Dropping this here would be the
        # project's oldest bug again: authored in the JSON, read by nothing.
        proc=item_def.get("proc"),
    )


def has_fixed_boss_loot(boss_name):
    """True if this boss has a hand-authored drop pool - lets
    combat_engine check without paying for a full Item build just to
    decide which branch to take."""
    return boss_name in _load_boss_loot_tables()


def get_fixed_boss_loot(boss_name):
    """One randomly-chosen Item from boss_name's fixed drop pool, or None
    if this boss isn't in any data/loot/*.json table (caller falls back
    to the normal procedural generate_boss_loot() roll)."""
    tables = _load_boss_loot_tables()
    pool = tables.get(boss_name)
    if not pool:
        return None
    return _item_from_def(random.choice(pool))


#: Bosses that drop more than one item at once. Kyle, on the Return Voyage's
#: finale: "a double boss fight of BOTH bloodsail leaders at once (they can
#: drop 3 pieces of loot at once from a pool of 10)."
MULTI_DROP = {
    "Admiral Hedessa Crane": 3,
}

#: Bosses whose loot IS another boss's loot. The Admiral and the
#: Fleet-Captain are one encounter standing in one cabin, so they share one
#: hoard: three items off her table, and nothing of his own. Without this he
#: would fall through to the procedural roll and add a fourth drop to a
#: fight Kyle specified as three.
SHARED_HOARD = {
    "Fleet-Captain Orin Dace": "Admiral Hedessa Crane",
}


def shares_hoard(boss_name):
    """True if this boss's drops come from another boss's table, so the
    caller must not roll anything for him at all."""
    return boss_name in SHARED_HOARD


def get_fixed_boss_loot_all(boss_name):
    """Every Item this boss drops, as a list - one for an ordinary boss,
    MULTI_DROP[boss_name] for one that drops several, and empty for a boss
    whose hoard belongs to somebody else.

    DISTINCT, via random.sample rather than three independent choices.
    Drawing three times with replacement from a pool of ten collides about
    28% of the time, and "dropped 3 pieces" that turns out to be two of the
    same belt reads as a bug rather than as luck. If the pool is smaller
    than the drop count the sample is capped at the pool size, because
    asking for more distinct items than exist should yield the whole pool
    rather than raise in the middle of a boss kill.
    """
    if shares_hoard(boss_name):
        return []
    pool = _load_boss_loot_tables().get(boss_name)
    if not pool:
        return []
    count = min(MULTI_DROP.get(boss_name, 1), len(pool))
    return [_item_from_def(d) for d in random.sample(pool, count)]
