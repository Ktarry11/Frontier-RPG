#!/usr/bin/env python3
"""Apply Kyle's Ashenvale level ladder (2026-10-22).  Idempotent: every number below is ABSOLUTE.

    python3 tools/relevel_ashenvale.py            # rewrite creatures.json / encounters.json / quests/ashenvale.json
    python3 tools/retier_quest_rewards.py         # then re-derive reward stats for the new item levels

LADDER (Kyle): Ashenvale East 20-25, Ashenvale West 22-28.  A cave/dungeon is never below its open-world zone.
Creatures only Ashenvale uses get a new base level_range; creatures that Ashenvale East AND West share (and a few shared
with other zones) get per-zone ``level_overrides`` in encounters.json (world/creature_manager.spawn_creature reads them).
Ability kits scale with level at spawn (Monster.__init__), so nothing else needs touching.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- creatures only Ashenvale uses (or whose Ashenvale level is the base): name -> [lo, hi]
BASE = {
    # West wildlife / hubs (West base; East overrides below)
    "Ashenvale Grizzly": [22, 25], "Timberling": [22, 25], "Forest Spider": [22, 25], "Nightsaber Stalker": [23, 26],
    "Ashenvale Wraith": [24, 27], "Dryad Sentinel": [24, 26], "Elder Timberling": [26, 26], "Lake Naiad": [22, 25],
    "Sentinel Scout": [22, 24], "Wisp": [22, 24],
    "Furbolg Ravager": [24, 27], "Furbolg Shaman": [24, 27], "Furbolg Den Watcher": [24, 27], "Ursal the Mauler": [28, 28],
    "Ancient Protector": [25, 27], "Keeper Rustveil": [28, 28],
    # Blackfathom (West cave): trash lifted into the zone band; the 26s are bosses (see report)
    "Naga Warrior": [24, 26], "Murloc Hydra": [25, 27],
    # Moonwell Hollow (West cave)
    "Hollow Rotlasher": [22, 24], "Gloomcap Sporeling": [22, 23], "Moonwell Mothwing": [22, 24],
    "Corrupted Moon Guard": [23, 25], "Twilight Rootbinder": [23, 25], "Twilight Adept": [23, 25],
    "Mosshide the Gloomcap Elder": [24, 24], "Maelwyn Blightbloom": [25, 25],
    "Satyr Soulstealer": [22, 25],
    # East
    "Buried Revenant": [22, 24], "Burning Blade Cultist": [21, 24], "Charred Wolf": [20, 23],
    "Satyr Ravager": [22, 25], "Satyr Trickster": [22, 25], "Twilight Acolyte": [21, 24], "Twilight Geomancer": [22, 25],
    "Felstalker": [23, 23], "Lord Malgan": [25, 25], "Twilight Overseer": [25, 25],
    "Fel Imp": [23, 25], "Demonspawn Grunt": [23, 25], "Voidwalker Remnant": [24, 25], "Pit Lord Emissary": [25, 25],
}

# ---- per-zone overrides (creature shared by both Ashenvale halves, or with another zone that keeps its own level)
OVERRIDES = {
    "Ashenvale West": {
        "Murloc Spearfisher": [24, 27], "Naga Coastguard": [25, 28], "Naga Tidecaller": [26, 28],
        "Tide-Wrecker Crab": [25, 27], "Pool Murloc": [23, 26], "Corrupted Treant": [24, 27],
    },
    "Ashenvale East": {
        "Ashenvale Grizzly": [20, 23], "Timberling": [20, 23], "Forest Spider": [20, 23], "Nightsaber Stalker": [21, 24],
        "Ashenvale Wraith": [21, 24], "Dryad Sentinel": [21, 23], "Elder Timberling": [24, 24], "Lake Naiad": [20, 23],
        "Sentinel Scout": [20, 22], "Wisp": [20, 22],
    },
}

# ---- quests: id -> (level_min, level_max).  Reward item level = level_max - 1 (boss kills: level_max).
QUESTS = {
    "ashenvale_grizzly_problem": (22, 25), "ashenvale_timberling_bark": (22, 24), "ashenvale_ursal_the_mauler": (26, 28),
    "ashenvale_sentinel_scouts_report": (22, 25), "ashenvale_furbolg_ravagers": (24, 27),
    "ashenvale_furbolg_shaman_totems": (24, 27), "ashenvale_keeper_rustveil": (27, 28), "ashenvale_wisp_lights": (22, 24),
    "ashenvale_refugees_belongings": (22, 25), "ashenvale_nightsaber_thinning": (23, 26),
    "splintertree_burning_blade_scouts": (20, 23), "splintertree_charred_wolves": (21, 24),
    "splintertree_fel_imp_cache": (23, 25), "splintertree_satyr_ritual": (22, 25), "splintertree_lord_malgan": (24, 25),
    "splintertree_twilight_acolytes": (21, 24), "splintertree_twilight_overseer": (24, 25),
    "splintertree_pit_lord_emissary": (24, 25),
}

# XP / gold medians by quest level (from every other authored zone), used to rescale each quest's reward
_XP = {10: 850, 12: 800, 13: 900, 14: 950, 15: 1010, 16: 1150, 17: 1100, 18: 1100, 19: 1210, 20: 1270, 21: 1490,
       22: 1600, 23: 1670, 24: 1800}
_GOLD = {10: 2950, 12: 2600, 13: 3500, 14: 3600, 15: 3600, 16: 3880, 17: 4080, 18: 4320, 19: 4680, 20: 4800, 21: 5070,
         22: 5280, 23: 6050, 24: 6400}


def _base(table, lv, per):
    if lv in table:
        return table[lv]
    top = max(table)
    return table[top] + per * (lv - top) if lv > top else table[min(table)]


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    miss = [n for n in BASE if n not in cdata["creatures"]]
    assert not miss, miss
    for n, rng in BASE.items():
        cdata["creatures"][n]["level_range"] = list(rng)
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))
    for z, ov in OVERRIDES.items():
        edata["zones"][z]["level_overrides"] = {k: list(v) for k, v in ov.items()}
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")

    qp = ROOT / "data/quests/ashenvale.json"
    qdata = json.loads(qp.read_text(encoding="utf-8"))
    boss_names = {n for n, c in cdata["creatures"].items() if c.get("is_boss")}
    # reference level for each quest's ORIGINAL xp (first run records it so reruns stay stable)
    OLD_MIN = {"ashenvale_grizzly_problem": 10, "ashenvale_timberling_bark": 10, "ashenvale_ursal_the_mauler": 14,
               "ashenvale_sentinel_scouts_report": 10, "ashenvale_furbolg_ravagers": 12, "ashenvale_furbolg_shaman_totems": 13,
               "ashenvale_keeper_rustveil": 15, "ashenvale_wisp_lights": 10, "ashenvale_refugees_belongings": 10,
               "ashenvale_nightsaber_thinning": 11, "splintertree_burning_blade_scouts": 12, "splintertree_charred_wolves": 13,
               "splintertree_fel_imp_cache": 13, "splintertree_satyr_ritual": 14, "splintertree_lord_malgan": 17,
               "splintertree_twilight_acolytes": 15, "splintertree_twilight_overseer": 17, "splintertree_pit_lord_emissary": 23}
    OLD_XP = {}
    for q in qdata["quests"]:
        OLD_XP[q["quest_id"]] = q.get("_xp_factor")
    for q in qdata["quests"]:
        qid = q["quest_id"]
        lo, hi = QUESTS[qid]
        if "_xp_factor" not in q:                       # first run: remember how generous this quest was for its old level
            q["_xp_factor"] = round(q["reward_exp"] / _base(_XP, OLD_MIN[qid], 100), 3)
            q["_gold_factor"] = round(q["reward_gold"] / _base(_GOLD, OLD_MIN[qid], 270), 3)
        q["level_min"], q["level_max"] = lo, hi
        cl = lambda f: max(0.75, min(1.3, f))          # old authored rewards were uneven; keep only a mild per-quest tilt
        q["reward_exp"] = int(round(_base(_XP, lo, 100) * cl(q["_xp_factor"]) / 50.0) * 50)
        q["reward_gold"] = int(round(_base(_GOLD, lo, 270) * cl(q["_gold_factor"]) / 100.0) * 100)
        boss = any(o["type"] == "kill_boss" or (o["type"] == "kill" and o.get("target") in boss_names) for o in q["objectives"])
        ilvl = hi if boss else hi - 1
        for it in q.get("unique_item_defs") or []:
            it["item_level"] = ilvl
        if q.get("gear_reward_gear_level"):
            q["gear_reward_gear_level"] = ilvl
    qp.write_text(json.dumps(qdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("creatures re-levelled:", len(BASE), "| zone overrides:", {z: len(v) for z, v in OVERRIDES.items()},
          "| quests:", len(QUESTS))


if __name__ == "__main__":
    main()
