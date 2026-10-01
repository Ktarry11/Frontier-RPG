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
from gear_icons import pick_armor_icon, pick_weapon_icon


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
                with open(path, "r") as f:
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

    if weapon_type:
        icon_id = pick_weapon_icon(weapon_type)
    else:
        icon_id = pick_armor_icon(item_def["slot"], armor_type)

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
