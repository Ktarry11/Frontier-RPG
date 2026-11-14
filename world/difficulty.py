"""Global monster difficulty: one table, three kinds of place (data/balance/monster_difficulty.json).

Kyle, 14 Nov 2026: "I want Dungeons to NEED a group of 5 and open world should still have danger to
it.....not tank and spanking Everything mindlessly."

WHY ONE TABLE AND NOT 1,200 KITS. Measured with tools/sim_difficulty.py the same evening: a geared
player lost about a fifth of their health to a same-level creature in every band from 10 to 54,
and a party of three beat most dungeon bosses with nobody dying. That is not one creature tuned
wrong, it is the whole curve sitting low, so it is corrected where the curve is applied rather
than in every kit, and it can be turned back by editing three pairs of numbers.

  open   anything met in the open world
  cave   trash in a cave or dungeon (cave_spawns tags it)
  boss   a boss of a real five-player dungeon (world/zone_classification.DUNGEONS)
  field_boss  every other boss: the named one at the back of a small cave, a named rare in the
         open. Kyle, 14 Nov, after a friend at level 17 met Tidelord Gharesh in the Echo Isles grotto
         with 5,700 health: "it shouldn't be that high." Then: "keep Dungeons around 3x health and
         3x damage... He did it with 2 people. So why the fuck not." Both kinds are 3x/3x today;
         they are separate keys so they can be split again.
  tuned_boss  a boss whose kit was already tuned by hand against the sim (the Tempest Isle
         dungeons and the Royal Hive), named in the table's "tuned_bosses" list
  hidden_layer / skull_zone  every monster, trash and boss alike, in a hidden level under a dungeon
         or a hidden open-world map (world/hidden_zones.py). These rows also carry
         loot_ilvl_bonus: what they drop sits that many item levels above them.

Damage is a multiplier on what the monster deals (Monster.damage_output_multiplier); health is
applied once, when the creature is made.
"""
import json
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "balance" / "monster_difficulty.json"


@lru_cache(maxsize=1)
def table():
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=1)
def _tuned():
    return frozenset(table().get("tuned_bosses") or ())


@lru_cache(maxsize=1)
def dungeon_bosses():
    """The bosses that appear in a real dungeon's encounter table (data/creatures/encounters.json)."""
    from world.zone_classification import DUNGEONS
    root = Path(__file__).resolve().parent.parent / "data" / "creatures"
    try:
        enc = json.loads((root / "encounters.json").read_text(encoding="utf-8"))
        cre = json.loads((root / "creatures.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return frozenset()
    cre = cre.get("creatures", cre)
    found = {}

    def walk(node, key):
        if isinstance(node, dict):
            if isinstance(node.get("creatures"), dict):
                found.setdefault(node.get("name") or key, set()).update(node["creatures"])
            for k, v in node.items():
                walk(v, k)
    walk(enc, None)
    wanted = set(DUNGEONS)
    return frozenset(c for zone, names in found.items() if zone in wanted
                     for c in names if (cre.get(c) or {}).get("is_boss"))


def kind_of(monster):
    from world.hidden_zones import creature_kinds
    hidden = creature_kinds().get(getattr(monster, "name", None))
    if hidden:
        return hidden
    if getattr(monster, "is_boss", False):
        name = getattr(monster, "name", None)
        if name in _tuned():
            return "tuned_boss"
        return "boss" if name in dungeon_bosses() else "field_boss"
    return "cave" if getattr(monster, "location_type", None) == "cave" else "open"


def factor(monster, what):
    return float((table().get(kind_of(monster)) or {}).get(what, 1.0))


def apply_health(monster):
    """Scale a freshly made monster's health for where it stands. Idempotent per monster."""
    if getattr(monster, "_difficulty_kind", None) == kind_of(monster):
        return
    old = getattr(monster, "_difficulty_health", 1.0)
    new = factor(monster, "health")
    monster.max_health = max(1, int(monster.max_health / old * new))
    monster.current_health = monster.max_health
    monster._difficulty_health = new
    monster._difficulty_kind = kind_of(monster)
    row = table().get(monster._difficulty_kind) or {}
    monster.loot_ilvl_bonus = int(row.get("loot_ilvl_bonus", 0))
    monster.loot_epic_chance = float(row.get("trash_epic_chance", 0.0))
