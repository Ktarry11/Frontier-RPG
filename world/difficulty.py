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
  boss   anything flagged is_boss, wherever it stands
  tuned_boss  a boss whose kit was already tuned by hand against the sim (the Tempest Isle
         dungeons and the Royal Hive), named in the table's "tuned_bosses" list

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


def kind_of(monster):
    if getattr(monster, "is_boss", False):
        if getattr(monster, "name", None) in _tuned():
            return "tuned_boss"
        return "boss"
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
