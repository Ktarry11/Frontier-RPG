"""
Add Tirisfal Glades creature and encounter data, plus town encounter stubs.

Run from project root:   python3 tools/add_tirisfal.py

Idempotent - re-running overwrites the same entries.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CREATURES_PATH = ROOT / "data" / "creatures" / "creatures.json"
ENCOUNTERS_PATH = ROOT / "data" / "creatures" / "encounters.json"

NEW_CREATURES = {
    # --- Deathknell / open glades (1-6) ---
    "Mangy Duskbat": {
        "template": "beast_fast", "level_range": [1, 2], "is_boss": False},
    "Ragged Scavenger": {
        "template": "beast_fast", "level_range": [1, 3], "is_boss": False},
    "Rattlecage Skeleton": {
        "template": "undead_basic", "level_range": [2, 4], "is_boss": False},
    "Wretched Zombie": {
        "template": "undead_basic", "level_range": [3, 5], "is_boss": False},
    "Young Nightcrawler": {
        "template": "vermin_sneaky", "level_range": [2, 4], "is_boss": False},
    "Scarlet Convert": {
        "template": "humanoid_warrior", "level_range": [4, 6], "is_boss": False},
    "Darkeye Bonecaster": {
        "template": "humanoid_caster", "level_range": [4, 6], "is_boss": False},

    # --- Solliden Farmstead (4-8) ---
    "Rotting Dead": {
        "template": "undead_basic", "level_range": [5, 7], "is_boss": False},
    "Blighted Grain Thresher": {
        "template": "vermin_swarm", "level_range": [4, 6], "is_boss": False},
    "Solliden Farmhand": {
        "template": "undead_basic", "level_range": [6, 8], "is_boss": False},

    # --- Agamand Mills (6-10) ---
    "Agamand Servant": {
        "template": "undead_basic", "level_range": [6, 8], "is_boss": False},
    "Agamand Family Ghoul": {
        "template": "undead_basic", "level_range": [7, 9],
        "hp_mult": 1.15, "is_boss": False},
    "Thurman Agamand": {
        "template": "undead_basic", "level_range": [9, 9],
        "is_boss": True, "boss_multiplier": 2.2},
    "Captured Farmer": {
        "template": "humanoid_warrior", "level_range": [7, 9], "is_boss": False},

    # --- Balnir Farmstead (7-10) ---
    "Bleak Worg": {
        "template": "beast_fast", "level_range": [7, 9], "is_boss": False},
    "Vicious Night Web Spider": {
        "template": "vermin_sneaky", "level_range": [8, 10], "is_boss": False},
    "Balnir Stableboy": {
        "template": "undead_basic", "level_range": [8, 10], "is_boss": False},

    # --- Whispering Shore (5-9) ---
    "Vile Fin Murloc": {
        "template": "aquatic_basic", "level_range": [5, 7], "is_boss": False},
    "Vile Fin Tidehunter": {
        "template": "aquatic_basic", "level_range": [7, 9],
        "hp_mult": 1.15, "is_boss": False},
    "Drowned Fisherman": {
        "template": "undead_basic", "level_range": [6, 8], "is_boss": False},

    # --- The Scarlet Watch (9-12) ---
    "Scarlet Zealot": {
        "template": "humanoid_warrior", "level_range": [9, 11], "is_boss": False},
    "Scarlet Preacher": {
        "template": "humanoid_caster", "level_range": [10, 12], "is_boss": False},
    "Scarlet Bowman": {
        "template": "humanoid_ranged", "level_range": [9, 11], "is_boss": False},
    "Interrogator Vishas": {
        "template": "humanoid_warrior", "level_range": [13, 13],
        "is_boss": True, "boss_multiplier": 2.4},

    # --- Night Web's Hollow cave (6-10) ---
    "Night Web Spider": {
        "template": "vermin_sneaky", "level_range": [6, 8], "is_boss": False},
    "Night Web Matriarch": {
        "template": "vermin_sneaky", "level_range": [8, 10],
        "hp_mult": 1.2, "atk_mult": 1.15, "is_boss": False},
    "Web Wrapped Corpse": {
        "template": "undead_basic", "level_range": [7, 9], "is_boss": False},
    "Ravenclaw Drudger": {
        "template": "undead_basic", "level_range": [8, 10], "is_boss": False},
    "Broodmother Nesh'ka": {
        "template": "vermin_sneaky", "level_range": [11, 11],
        "is_boss": True, "boss_multiplier": 2.3},

    # --- Scarlet Crypt cave (10-14) ---
    "Crypt Crawler": {
        "template": "vermin_swarm", "level_range": [10, 12], "is_boss": False},
    "Scarlet Initiate": {
        "template": "humanoid_warrior", "level_range": [11, 13], "is_boss": False},
    "Scarlet Chaplain": {
        "template": "humanoid_caster", "level_range": [11, 13], "is_boss": False},
    "Restless Crypt Fiend": {
        "template": "undead_basic", "level_range": [12, 14], "is_boss": False},
    "High Inquisitor Fairbanks": {
        "template": "humanoid_caster", "level_range": [15, 15],
        "is_boss": True, "boss_multiplier": 2.5},
}

TIRISFAL = {
    "open_zone": {
        "name": "The Glades",
        "creatures": {
            "Mangy Duskbat": 2.0,
            "Ragged Scavenger": 1.8,
            "Rattlecage Skeleton": 1.5,
            "Young Nightcrawler": 1.3,
            "Wretched Zombie": 1.2,
            "Scarlet Convert": 0.8,
            "Darkeye Bonecaster": 0.7,
        },
    },
    "subzones": {
        "Solliden Farmstead": {
            "name": "Solliden Farmstead",
            "creatures": {
                "Rotting Dead": 2.0,
                "Blighted Grain Thresher": 1.5,
                "Solliden Farmhand": 1.3,
            },
        },
        "Agamand Mills": {
            "name": "Agamand Mills",
            "creatures": {
                "Agamand Servant": 2.0,
                "Agamand Family Ghoul": 1.4,
                "Captured Farmer": 1.0,
                "Thurman Agamand": 0.3,
            },
        },
        "Balnir Farmstead": {
            "name": "Balnir Farmstead",
            "creatures": {
                "Bleak Worg": 2.0,
                "Vicious Night Web Spider": 1.4,
                "Balnir Stableboy": 1.2,
            },
        },
        "Whispering Shore": {
            "name": "Whispering Shore",
            "creatures": {
                "Vile Fin Murloc": 2.0,
                "Vile Fin Tidehunter": 1.3,
                "Drowned Fisherman": 1.2,
            },
        },
        "The Scarlet Watch": {
            "name": "The Scarlet Watch",
            "creatures": {
                "Scarlet Zealot": 2.0,
                "Scarlet Bowman": 1.5,
                "Scarlet Preacher": 1.2,
                "Interrogator Vishas": 0.25,
            },
        },
    },
    "caves": {
        "Night Web's Hollow": {
            "name": "Night Web's Hollow",
            "creatures": {
                "Night Web Spider": 2.0,
                "Night Web Matriarch": 1.2,
                "Web Wrapped Corpse": 1.3,
                "Ravenclaw Drudger": 1.1,
                "Broodmother Nesh'ka": 0.3,
            },
        },
        "Scarlet Crypt": {
            "name": "Scarlet Crypt",
            "creatures": {
                "Crypt Crawler": 1.8,
                "Scarlet Initiate": 1.6,
                "Scarlet Chaplain": 1.3,
                "Restless Crypt Fiend": 1.2,
                "High Inquisitor Fairbanks": 0.3,
            },
        },
    },
}

# Town hubs are safe: no open_zone creatures at all. Explicit empty tables so
# trigger_encounter() returns None rather than falling through to a parent
# zone's table and spawning quilboar inside a tavern.
SAFE_TOWNS = ["Ratchet", "Camp Taurajo", "Orgrimmar", "Zeppelin Tower"]


def main():
    creatures_doc = json.loads(CREATURES_PATH.read_text())
    encounters_doc = json.loads(ENCOUNTERS_PATH.read_text())
    creatures = creatures_doc["creatures"]
    zones = encounters_doc["zones"]

    added = sum(1 for k in NEW_CREATURES if k not in creatures)
    creatures.update(NEW_CREATURES)
    zones["Tirisfal Glades"] = TIRISFAL
    for town in SAFE_TOWNS:
        zones[town] = {"open_zone": {"name": town, "creatures": {}},
                       "subzones": {}, "caves": {}}

    problems = []
    for zone_name, zone in zones.items():
        tables = [("open_zone", zone.get("open_zone", {}))]
        tables += [(f"subzone/{k}", v) for k, v in zone.get("subzones", {}).items()]
        tables += [(f"cave/{k}", v) for k, v in zone.get("caves", {}).items()]
        for label, table in tables:
            for cname in table.get("creatures", {}):
                if cname not in creatures:
                    problems.append(f"{zone_name}/{label}: unknown creature '{cname}'")

    if problems:
        print(f"!! {len(problems)} PROBLEMS - nothing written:")
        for p in problems:
            print("   -", p)
        return 1

    CREATURES_PATH.write_text(json.dumps(creatures_doc, indent=2))
    ENCOUNTERS_PATH.write_text(json.dumps(encounters_doc, indent=2))
    print(f"Creatures: {len(creatures)} total ({added} new)")
    print(f"Zones with tables: {len(zones)}")
    print(f"  Tirisfal Glades: {len(TIRISFAL['subzones'])} subzones, "
          f"{len(TIRISFAL['caves'])} caves")
    print(f"  Safe towns (no encounters): {', '.join(SAFE_TOWNS)}")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
