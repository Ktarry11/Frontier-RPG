#!/usr/bin/env python3
"""Ashenvale dungeon content pass (Moonwell Hollow, Howling Barrows, Grom's Rest).  Idempotent.

  PYTHONPATH=. python3 tools/build_ashenvale_dungeon_content.py && python3 tools/generate_creatures.py

Ladder (Kyle's confirmed table, claude/dungeon_levels_and_loot_plan.md):
  Moonwell Hollow  22-25  boss Maelwyn Blightbloom 25          (rare: Mosshide the Gloomcap Elder 24)   [West zone 22-28]
  Howling Barrows  21-24  boss 24                                                                      [East zone 20-25]
  Grom's Rest      26-30  Satyr Warlord 29 | Dread Mage Malik 30 | Possessed Oracle 31 | Lord Nightmare 32
LOOT: ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas (build_durotar_content.make).
Ability kits live in tools/monster_kits.py (ASHENVALE_DUNGEON_KITS); sub-20 bosses have 3 abilities, 20+ have 4.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

DUNGEONS = {}          # key -> dict(region, cave, creatures{}, fixes{}, table{}, pools{}, quest_drops{})


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


# ================================================================================================== MOONWELL HOLLOW
MOONWELL = dict(
    region="Ashenvale West", cave="Moonwell Hollow",
    creatures={
        "Hollow Rotlasher": C("elemental_bruiser", 22, 24, "hollow_rotlasher"),
        "Gloomcap Sporeling": C("vermin_swarm", 22, 23, "gloomcap_sporeling"),
        "Moonwell Mothwing": C("beast_fast", 22, 24, "moonwell_mothwing"),
        "Corrupted Moon Guard": C("humanoid_warrior", 23, 25, "corrupted_moon_guard"),
        "Twilight Rootbinder": C("humanoid_caster", 23, 25, "twilight_rootbinder"),
        "Mosshide the Gloomcap Elder": C("elemental_bruiser", 24, 24, "mosshide_elder", True, 1.7),
        "Maelwyn Blightbloom": C("humanoid_caster", 25, 25, "maelwyn_blightbloom", True, 2.2),
    },
    table={
        "Hollow Rotlasher": 3, "Gloomcap Sporeling": 3, "Moonwell Mothwing": 2, "Corrupted Moon Guard": 2,
        "Twilight Rootbinder": 2, "Twilight Adept": 2, "Satyr Soulstealer": 1,
        "Maelwyn Blightbloom": 0, "Mosshide the Gloomcap Elder": 0,
    },
    quest_drops={
        "Twilight Rootbinder": [qd("moonwell_root_sample", "Blighted Root Sample",
                                   "A fist-sized knot of root, black at the core and still faintly warm. The Moonwell's sap runs "
                                   "through it, and it is wrong.", 0.45)],
        "Gloomcap Sporeling": [qd("gloomcap_spore_sac", "Gloomcap Spore Sac",
                                  "A swollen sac that smells of old cellars. Handle it gently, and then don't.", 0.4)],
    },
)


def moonwell_pools():
    P = {}
    P["Maelwyn Blightbloom"] = [      # L25 -> 28: nature caster staff / cloth chest / leather boots / ring
        make("Blightbloom Staff", "main_hand", "of the Prophet", 28,
             "A staff of root-wood, split at the head where a flower should be. The flower is elsewhere.",
             weapon_type="staff"),
        make("Moonwell-Stained Robes", "chest", "of the Sorcerer", 28,
             "Cloth that went through the Moonwell and came out a different shade of silver.", armor_type="cloth"),
        make("Hollow-Walker's Boots", "feet", "of the Falcon", 28,
             "Soft leather soled in root-fibre. They know where the floor is, even where you don't.",
             armor_type="leather"),
        make("Signet of the Withered Grove", "ring", "of the Restorer", 28,
             "A ring of petrified bark. It does not remember being alive, which may be a mercy.")]
    P["Mosshide the Gloomcap Elder"] = [    # L24 -> 27: shield / mail wrist / neck
        make("Mosshide Bulwark", "off_hand", "of Stamina", 27,
             "A slab of living moss over a stone core. It's damp, and it is very hard to move.", weapon_type="shield"),
        make("Gloomcap Bracers", "wrist", "of the Wolf", 27,
             "Mail bracers with a pale fungus growing between the links. It is, somehow, load-bearing.",
             armor_type="mail"),
        make("Elder's Spore Pendant", "neck", "of the Whale",
             27, "A dried gloomcap on a leather cord. It smells like a cellar and hums like a hive.")]
    return P


MOONWELL["pools"] = moonwell_pools()
DUNGEONS["moonwell"] = MOONWELL
# ===================================================================================================================


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())
    qp = ROOT / "data/creatures/quest_drops.json"
    qdata = json.loads(qp.read_text())
    for key, D in DUNGEONS.items():
        if only and key not in only:
            continue
        cdata["creatures"].update(D["creatures"])
        for n, patch in D.get("fixes", {}).items():
            cdata["creatures"].setdefault(n, {}).update(patch)
        z = edata["zones"][D["region"]]
        z.setdefault("caves", {})[D["cave"]] = {"name": D["cave"], "creatures": D["table"]}
        for creature, drops in D.get("quest_drops", {}).items():
            qdata["drops"].setdefault(creature, [])
            keep = [d for d in qdata["drops"][creature] if d["item_id"] not in {x["item_id"] for x in drops}]
            qdata["drops"][creature] = keep + drops
        out = {"_notes": f"{D['cave']} boss + rare loot (2026-10-22). ONE item drops per kill from the pool. "
                         "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
        out.update(D["pools"])
        fn = D["cave"].lower().replace("'", "").replace(" ", "_") + "_boss_loot.json"
        (ROOT / "data/loot" / fn).write_text(json.dumps(out, indent=2) + "\n")
        n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
        print(f"{D['cave']}: creatures +{len(D['creatures'])}, pools {len(out) - 1}, items {n} -> {fn}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")
    qp.write_text(json.dumps(qdata, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
