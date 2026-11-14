"""Hidden zones: the maps you only reach through a secret.

Kyle, 14 Nov 2026: "a hidden part in a dungeon can lead to a sub level where instead of... 3x HP and
3x Damage... it's 4x HP and 4.5x Damage... they drop at 4 to 5 ilvl and can have unique epics above
level 30... only ever be 1 to 2 bosses max and like 5 trash pulls total. Trash gets buffed too."
And: "For hidden zones, they can be new NEW transition zones too. These new zones will still have
the level range but maybe a skull next to them", "Open world will be 2.5x hp and 2.5x damage",
"when I say new zones. I mean actually new maps", "Quests can be in the zone, but max of like 3 or
4....they're not quest hubs but they CAN have elite quests. I want the wonder of exploring....and
for good measure....I WANT to be rewarded for exploring." And: "I don't want to see as I want these
to be secrets." So no doc lists where they are; the data says only what the engine needs.

TWO KINDS (data/world/hidden_zones.json, "kind"):
  layer   a hidden level under a dungeon. Every monster in it is the "hidden_layer" row of
          data/balance/monster_difficulty.json (4x health, 4.5x damage) and drops gear 4-5 item
          levels above itself.
  skull   a hidden open-world map. Every monster in it is the "skull_zone" row (2.5x health,
          2.5x damage), same loot lift.
Both show a skull beside their name in the overworld banner.

THE WAY IN is a secret door (world/secrets.py, "door"): a portal tile inside a room in the wall of
the parent map, reached by a path that looks like solid rock. tools/build_secrets.py picks the
room; world/portal_manager.py links the door both ways from secrets.json. The way out, from inside
the hidden zone, is an ordinary visible exit.

WHICH MONSTERS a kind applies to is read off the encounter tables: a creature named in a hidden
zone's table (data/creatures/encounters.json) is a creature of that kind. Every hidden zone has
its own creatures, so a name never means two places.
"""
import json
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_PATH = _ROOT / "data" / "world" / "hidden_zones.json"

#: kind in hidden_zones.json -> the difficulty row (world/difficulty.py) its monsters use
DIFFICULTY_KIND = {"layer": "hidden_layer", "skull": "skull_zone"}

# FRONTIER ZONES. Kyle, 14 Nov 2026: "double skull zones. Hidden zones WITHIN hidden zones... let's
# Call these ones Frontier Zones. They can be in open world, Dungeons, or caves. But they are hidden
# zones FROM hidden zones. They will only be in 10% of the skull zones", "They will drop higher epics
# and ilvl about 8 over the regular stuff", and "I'll let you deal with the math". So a frontier is
# a step above whatever it would otherwise be: a frontier cave or dungeon ("frontier_type": "deep")
# is harder than a hidden layer, a frontier open map ("open") harder than a skull zone. Two skulls
# on the banner.
FRONTIER_KIND = {"deep": "frontier_deep", "open": "frontier_open"}


def difficulty_kind(info):
    if info.get("kind") == "frontier":
        return FRONTIER_KIND.get(info.get("frontier_type", "deep"))
    return DIFFICULTY_KIND.get(info.get("kind"))


def skulls(zone_name):
    """How many skulls the banner shows: 2 for a frontier, 1 for any other hidden zone, else 0."""
    k = kind(zone_name)
    return 2 if k == "frontier" else (1 if k else 0)


@lru_cache(maxsize=1)
def registry():
    try:
        return json.loads(_PATH.read_text(encoding="utf-8")).get("zones", {})
    except (OSError, ValueError):
        return {}


def is_hidden(zone_name):
    return zone_name in registry()


def kind(zone_name):
    return (registry().get(zone_name) or {}).get("kind")


def parent(zone_name):
    return (registry().get(zone_name) or {}).get("parent")


@lru_cache(maxsize=1)
def creature_kinds():
    """creature name -> difficulty kind, for every creature in a hidden zone's encounter table."""
    try:
        enc = json.loads((_ROOT / "data" / "creatures" / "encounters.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}

    def names(node):
        found = set()
        if isinstance(node, dict):
            if isinstance(node.get("creatures"), dict):
                found |= set(node["creatures"])
            for v in node.values():
                found |= names(v)
        elif isinstance(node, list):
            for v in node:
                found |= names(v)
        return found
    # A cave's table sits under its parent zone's "caves"; an open zone's is top level. Either way
    # it is keyed by the map's name, so look for the key anywhere.
    tables = {}

    def find(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in registry() and isinstance(v, dict):
                    tables.setdefault(k, []).append(v)
                find(v)
    find(enc)
    for zone, info in registry().items():
        dk = difficulty_kind(info)
        if not dk:
            continue
        for t in tables.get(zone, []):
            for n in names(t):
                out[n] = dk
        for n in info.get("creatures") or []:      # pinned bosses and anything not in a table
            out[n] = dk
    return out


def reset_caches():
    registry.cache_clear()
    creature_kinds.cache_clear()
