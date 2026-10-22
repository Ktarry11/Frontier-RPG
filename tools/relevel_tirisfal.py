#!/usr/bin/env python3
"""Apply Kyle's Tirisfal level decisions (2026-10-22): Western Tirisfal 4-10, Eastern Tirisfal 6-12.  Idempotent (absolute values).

    python3 tools/relevel_tirisfal.py && python3 tools/retier_quest_rewards.py

Deathknell (1-6) and Silverpine keep their own levels, so creatures shared with them get per-zone ``level_overrides``
(world/creature_manager.spawn_creature).  Ability kits scale with level at spawn, so nothing else needs touching.
Quest XP/gold are left alone (they already sit in the right neighbourhood for these low levels); reward item levels
follow the quest (level_max - 1, boss kill = level_max) and retier_quest_rewards re-derives the stats.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BASE = {                                        # creatures only these two zones use
    "Manor Reaper": [5, 9], "Bulwark Sentinel": [9, 10],
    "Young Nightcrawler": [6, 8], "Scarlet Convert": [6, 9], "Darkeye Bonecaster": [7, 9],
    "Agamand Family Ghoul": [7, 10], "Agamand Servant": [7, 10], "Captured Farmer": [7, 10], "Thurman Agamand": [10, 10],
    "Solliden Farmhand": [6, 9], "Blighted Grain Thresher": [6, 9],
    "Scarlet Zealot": [9, 12], "Scarlet Bowman": [9, 12], "Scarlet Preacher": [9, 12], "Interrogator Vishas": [12, 12],
    "Scourge Warrior": [9, 12], "Scourge Necromancer": [9, 12],
}
OVERRIDES = {                                   # shared with Deathknell / each other / Silverpine -> per zone
    "Western Tirisfal": {"Mangy Duskbat": [4, 7], "Wretched Zombie": [5, 8], "Rotting Dead": [6, 9],
                         "Forsaken Deserter": [8, 10]},
    "Eastern Tirisfal": {"Mangy Duskbat": [6, 8], "Wretched Zombie": [6, 9], "Rotting Dead": [7, 10],
                         "Ragged Scavenger": [6, 8], "Rattlecage Skeleton": [7, 9]},
}
QUESTS = {
    "et_solliden_rot": (6, 9), "et_solliden_farmhands": (6, 9), "et_agamand_servants": (7, 10), "et_captured_farmers": (7, 10),
    "et_thurman_agamand": (10, 11), "et_scarlet_zealots": (9, 12), "et_scarlet_preacher_sermons": (10, 12),
    "et_interrogator_vishas": (12, 12),
    "wt_bulwark_deserters": (8, 10), "wt_bulwark_sentinels": (9, 10), "wt_couriers_route": (7, 10),
}


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    for n, rng in BASE.items():
        cdata["creatures"][n]["level_range"] = list(rng)
    cp.write_text(json.dumps(cdata, indent=2) + "\n")

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())
    for z, ov in OVERRIDES.items():
        edata["zones"][z]["level_overrides"] = {k: list(v) for k, v in ov.items()}
    ep.write_text(json.dumps(edata, indent=2) + "\n")

    qp = ROOT / "data/quests/forsaken_lands.json"
    qdata = json.loads(qp.read_text())
    boss_names = {n for n, c in cdata["creatures"].items() if c.get("is_boss")}
    for q in qdata["quests"]:
        if q["quest_id"] not in QUESTS:
            continue
        lo, hi = QUESTS[q["quest_id"]]
        q["level_min"], q["level_max"] = lo, hi
        boss = any(o["type"] == "kill_boss" or (o["type"] == "kill" and o.get("target") in boss_names) for o in q["objectives"])
        ilvl = hi if boss else max(1, hi - 1)
        for it in q.get("unique_item_defs") or []:
            it["item_level"] = ilvl
        if q.get("gear_reward_gear_level"):
            q["gear_reward_gear_level"] = ilvl
    qp.write_text(json.dumps(qdata, indent=2, ensure_ascii=False) + "\n")
    print("Tirisfal: creatures", len(BASE), "| overrides", {z: len(v) for z, v in OVERRIDES.items()}, "| quests", len(QUESTS))


if __name__ == "__main__":
    main()
