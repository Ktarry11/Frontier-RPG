"""
Add two zones to the world: Southern Durotar and The Barrens.

Run from project root:   python3 tools/add_zones.py

WHY
---
Durotar was a single 150x100 map covering the whole 4-13 level band, but the
bestiary design doc splits it into North/Central (4-10) and South (8-13) with
different creature tables. The southern creatures already existed in
creatures.json and were already grouped into Durotar's subzones - they just
had nowhere to actually live on the map.

The Barrens is new: the classic 10-25 zone that bridges the starter cluster
to mid-game content. It roughly doubles the level ceiling of the playable
world (was 10-16, now 10-25).

This script is idempotent - re-running it overwrites the same entries rather
than duplicating them, so it is safe to run again after editing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CREATURES_PATH = ROOT / "data" / "creatures" / "creatures.json"
ENCOUNTERS_PATH = ROOT / "data" / "creatures" / "encounters.json"

# ------------------------------------------------------------------
# NEW CREATURES - The Barrens
# ------------------------------------------------------------------
# Template + level range + deltas only, never full stat blocks, per the
# bestiary doc's "template plus delta" rule. hp_mult/atk_mult are optional
# overrides on the template baseline.

NEW_CREATURES = {
    # --- Barrens open zone (10-16) ---
    "Plainstrider": {
        "template": "beast_fast", "level_range": [10, 12], "is_boss": False},
    "Greater Plainstrider": {
        "template": "beast_fast", "level_range": [13, 15],
        "hp_mult": 1.15, "atk_mult": 1.1, "is_boss": False},
    "Zhevra Runner": {
        "template": "beast_fast", "level_range": [11, 13], "is_boss": False},
    "Zhevra Courser": {
        "template": "beast_fast", "level_range": [14, 16],
        "hp_mult": 1.2, "atk_mult": 1.15, "is_boss": False},
    "Savannah Prowler": {
        "template": "beast_fast", "level_range": [12, 14], "is_boss": False},
    "Savannah Huntress": {
        "template": "beast_fast", "level_range": [15, 17],
        "hp_mult": 1.2, "atk_mult": 1.2, "is_boss": False},
    "Savannah Patriarch": {
        "template": "beast_large", "level_range": [17, 19],
        "hp_mult": 1.15, "is_boss": False},
    "Barrens Giraffe": {
        "template": "beast_large", "level_range": [13, 15], "is_boss": False},
    "Sunscale Screecher": {
        "template": "beast_fast", "level_range": [11, 13], "is_boss": False},
    "Silithid Swarmer": {
        "template": "vermin_swarm", "level_range": [12, 14], "is_boss": False},
    "Silithid Creeper": {
        "template": "vermin_sneaky", "level_range": [14, 16], "is_boss": False},

    # --- Bristleback quilboar (Razorfen approach, 14-19) ---
    "Bristleback Quilboar": {
        "template": "humanoid_warrior", "level_range": [14, 16], "is_boss": False},
    "Bristleback Shaman": {
        "template": "humanoid_caster", "level_range": [15, 17], "is_boss": False},
    "Bristleback Thornweaver": {
        "template": "humanoid_caster", "level_range": [16, 18], "is_boss": False},
    "Bristleback Geomancer": {
        "template": "humanoid_caster", "level_range": [17, 19], "is_boss": False},
    "Bristleback Water Seeker": {
        "template": "humanoid_ranged", "level_range": [14, 16], "is_boss": False},
    "Charlga's Enforcer": {
        "template": "humanoid_warrior", "level_range": [18, 20],
        "hp_mult": 1.2, "atk_mult": 1.15, "is_boss": False},

    # --- Kolkar centaur (Barrens plains, 15-20) ---
    "Kolkar Stormer": {
        "template": "humanoid_caster", "level_range": [15, 17], "is_boss": False},
    "Kolkar Drudge": {
        "template": "humanoid_warrior", "level_range": [16, 18], "is_boss": False},
    "Verog the Dervish": {
        "template": "humanoid_warrior", "level_range": [21, 21],
        "is_boss": True, "boss_multiplier": 1.0},

    # --- Wailing Caverns (18-24) ---
    "Deviate Adder": {
        "template": "vermin_sneaky", "level_range": [18, 20], "is_boss": False},
    "Deviate Lasher": {
        "template": "beast_fast", "level_range": [19, 21], "is_boss": False},
    "Deviate Crocolisk": {
        "template": "beast_large", "level_range": [19, 21], "is_boss": False},
    "Deviate Ravager": {
        "template": "beast_fast", "level_range": [20, 22],
        "hp_mult": 1.15, "atk_mult": 1.2, "is_boss": False},
    "Druid of the Fang": {
        "template": "humanoid_caster", "level_range": [21, 23], "is_boss": False},
    "Nightmare Ectoplasm": {
        "template": "elemental_caster", "level_range": [20, 22], "is_boss": False},
    "Skum": {
        "template": "beast_large", "level_range": [24, 24],
        "is_boss": True, "boss_multiplier": 1.0},

    # --- Boulder Lode Mine (16-21) ---
    "Venture Co. Miner": {
        "template": "humanoid_warrior", "level_range": [16, 18], "is_boss": False},
    "Venture Co. Overseer": {
        "template": "humanoid_warrior", "level_range": [18, 20],
        "hp_mult": 1.15, "is_boss": False},
    "Venture Co. Tinkerer": {
        "template": "humanoid_ranged", "level_range": [17, 19], "is_boss": False},
    "Cavern Rock Elemental": {
        "template": "elemental_bruiser", "level_range": [19, 21], "is_boss": False},
    "Foreman Grills": {
        "template": "humanoid_warrior", "level_range": [22, 22],
        "is_boss": True, "boss_multiplier": 1.0},

    # --- Field of Giants / Southern Barrens (20-25) ---
    "Barrens Kodo": {
        "template": "beast_large", "level_range": [20, 22], "is_boss": False},
    "Aged Kodo": {
        "template": "beast_large", "level_range": [22, 24],
        "hp_mult": 1.2, "is_boss": False},
    "Sunscale Lashtail": {
        "template": "beast_fast", "level_range": [21, 23], "is_boss": False},
    "Witchwing Harpy": {
        "template": "beast_fast", "level_range": [20, 22], "is_boss": False},
    "Witchwing Windcaller": {
        "template": "humanoid_caster", "level_range": [21, 23], "is_boss": False},
    "Hezrul Bloodmark": {
        "template": "humanoid_warrior", "level_range": [25, 25],
        "is_boss": True, "boss_multiplier": 1.0},

    # --- Forgotten Pools (17-21) ---
    "Pool Murloc": {
        "template": "aquatic_basic", "level_range": [17, 19], "is_boss": False},
    "Murloc Flesheater": {
        "template": "aquatic_basic", "level_range": [19, 21],
        "hp_mult": 1.15, "atk_mult": 1.15, "is_boss": False},
    "Water Elemental": {
        "template": "elemental_bruiser", "level_range": [20, 22], "is_boss": False},
    "Gaharrz the Drowned": {
        "template": "aquatic_basic", "level_range": [22, 22],
        "is_boss": True, "boss_multiplier": 1.0},
}

# ------------------------------------------------------------------
# ENCOUNTER TABLES
# ------------------------------------------------------------------
# Weights are relative, not percentages - a 2.0 is twice as likely as a 1.0.
# Bosses get low weights so they read as rare spawns rather than routine.

SOUTHERN_DUROTAR = {
    "open_zone": {
        "name": "The Southern Reach",
        "creatures": {
            "Elder Mottled Boar": 2.0,
            "Bloodtalon Scythemaw": 1.5,
            "Southfury Crocolisk": 1.0,
        },
    },
    "subzones": {
        "Kolkar Crag": {
            "name": "Kolkar Crag",
            "creatures": {
                "Kolkar Outrunner": 1.5,
                "Kolkar Marauder": 2.0,
                "Kolkar Wrangler": 1.2,
                "Kolkar Pack Runner": 1.2,
                "Kolkar Windchaser": 1.0,
                "Warlord Krellian": 0.3,
            },
        },
        "Scuttle Coast": {
            "name": "Scuttle Coast",
            "creatures": {
                "Coastal Murloc": 2.0,
                "Murloc Tidehunter": 1.5,
                "Murloc Oracle": 1.0,
                "Drowned Deckhand": 1.2,
            },
        },
    },
    "caves": {
        "Drygulch Ravine": {
            "name": "Drygulch Ravine",
            "creatures": {
                "Dustwind Harpy": 2.0,
                "Dustwind Savage": 1.5,
                "Dustwind Storm-Witch": 1.2,
                "Matriarch Vess'ra": 0.4,
            },
        },
        "Dustwind Cave": {
            "name": "Dustwind Cave",
            "creatures": {
                "Cave Scorpid": 2.0,
                "Sand Skitterling": 1.5,
                "Gorge the Corpsegrinder": 0.4,
            },
        },
    },
}

THE_BARRENS = {
    "open_zone": {
        "name": "The Golden Plains",
        "creatures": {
            "Plainstrider": 2.0,
            "Zhevra Runner": 1.8,
            "Savannah Prowler": 1.5,
            "Sunscale Screecher": 1.2,
            "Barrens Giraffe": 1.0,
            "Greater Plainstrider": 0.8,
            "Zhevra Courser": 0.8,
            "Savannah Huntress": 0.6,
        },
    },
    "subzones": {
        "Lushwater Oasis": {
            "name": "Lushwater Oasis",
            "creatures": {
                "Silithid Swarmer": 2.0,
                "Silithid Creeper": 1.5,
                "Savannah Prowler": 1.2,
                "Water Elemental": 0.8,
            },
        },
        "The Forgotten Pools": {
            "name": "The Forgotten Pools",
            "creatures": {
                "Pool Murloc": 2.0,
                "Murloc Flesheater": 1.5,
                "Water Elemental": 1.0,
                "Gaharrz the Drowned": 0.3,
            },
        },
        "Razorfen Approach": {
            "name": "Razorfen Approach",
            "creatures": {
                "Bristleback Quilboar": 2.0,
                "Bristleback Water Seeker": 1.5,
                "Bristleback Shaman": 1.2,
                "Bristleback Thornweaver": 1.0,
                "Bristleback Geomancer": 0.8,
                "Charlga's Enforcer": 0.5,
            },
        },
        "Kolkar Plains": {
            "name": "Kolkar Plains",
            "creatures": {
                "Kolkar Stormer": 1.5,
                "Kolkar Drudge": 2.0,
                "Kolkar Marauder": 1.2,
                "Verog the Dervish": 0.3,
            },
        },
        "Field of Giants": {
            "name": "Field of Giants",
            "creatures": {
                "Barrens Kodo": 2.0,
                "Aged Kodo": 1.3,
                "Sunscale Lashtail": 1.2,
                "Savannah Patriarch": 1.0,
            },
        },
        "Witchwing Terrace": {
            "name": "Witchwing Terrace",
            "creatures": {
                "Witchwing Harpy": 2.0,
                "Witchwing Windcaller": 1.4,
                "Hezrul Bloodmark": 0.25,
            },
        },
    },
    "caves": {
        "Boulder Lode Mine": {
            "name": "Boulder Lode Mine",
            "creatures": {
                "Venture Co. Miner": 2.0,
                "Venture Co. Tinkerer": 1.5,
                "Venture Co. Overseer": 1.2,
                "Cavern Rock Elemental": 1.0,
                "Foreman Grills": 0.4,
            },
        },
        "Wailing Caverns": {
            "name": "Wailing Caverns",
            "creatures": {
                "Deviate Adder": 2.0,
                "Deviate Lasher": 1.6,
                "Deviate Crocolisk": 1.3,
                "Deviate Ravager": 1.1,
                "Nightmare Ectoplasm": 1.0,
                "Druid of the Fang": 0.9,
                "Skum": 0.3,
            },
        },
    },
}


def main():
    creatures_doc = json.loads(CREATURES_PATH.read_text())
    encounters_doc = json.loads(ENCOUNTERS_PATH.read_text())

    creatures = creatures_doc["creatures"]
    zones = encounters_doc["zones"]

    added = sum(1 for k in NEW_CREATURES if k not in creatures)
    creatures.update(NEW_CREATURES)

    zones["Southern Durotar"] = SOUTHERN_DUROTAR
    zones["The Barrens"] = THE_BARRENS

    # Validate every referenced creature actually exists - a typo here would
    # otherwise produce a zone that silently never spawns that creature.
    problems = []
    for zone_name, zone in zones.items():
        tables = [("open_zone", zone.get("open_zone", {}))]
        tables += [(f"subzone/{k}", v) for k, v in zone.get("subzones", {}).items()]
        tables += [(f"cave/{k}", v) for k, v in zone.get("caves", {}).items()]
        for label, table in tables:
            for creature_name in table.get("creatures", {}):
                if creature_name not in creatures:
                    problems.append(f"{zone_name}/{label}: unknown creature '{creature_name}'")

    if problems:
        print(f"!! {len(problems)} PROBLEMS - nothing written:")
        for p in problems:
            print("   -", p)
        return 1

    CREATURES_PATH.write_text(json.dumps(creatures_doc, indent=2))
    ENCOUNTERS_PATH.write_text(json.dumps(encounters_doc, indent=2))

    print(f"Creatures: {len(creatures)} total ({added} new)")
    print(f"Zones with encounter tables: {len(zones)}")
    for name in ("Southern Durotar", "The Barrens"):
        z = zones[name]
        n_sub = len(z.get("subzones", {}))
        n_cave = len(z.get("caves", {}))
        print(f"  {name:<20} {n_sub} subzones, {n_cave} caves")
    print("Validation passed: every referenced creature exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
