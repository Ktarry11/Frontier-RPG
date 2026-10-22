#!/usr/bin/env python3
"""Give every fetch/gather quest item a creature that drops it.  Idempotent.

Seven quests (5 Ashenvale, 2 Forsaken Lands) asked for items that no creature dropped, so they could never be finished
(and the quest helper had nothing to point at).  Drop chances are tuned so the usual kill count is ~2x the item count.

    python3 tools/fix_orphan_quest_items.py          # add the drops
    python3 tools/fix_orphan_quest_items.py --check  # list any fetch/gather target that still has no drop source
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QP = ROOT / "data/creatures/quest_drops.json"


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


DROPS = {
    "Timberling": [qd("timberling_heartwood", "Timberling Heartwood",
                      "A hand-length of dense, red-gold heartwood, still faintly warm. The wards at Maestra's Post are carved "
                      "from exactly this.", 0.5)],
    "Elder Timberling": [qd("timberling_heartwood", "Timberling Heartwood",
                            "A hand-length of dense, red-gold heartwood, still faintly warm. The wards at Maestra's Post are "
                            "carved from exactly this.", 1.0)],
    "Furbolg Shaman": [qd("corrupted_furbolg_totem", "Corrupted Furbolg Totem",
                          "A bone-and-sinew totem with something black seeping through the carving. It hums when you stop "
                          "paying attention to it.", 0.55)],
    "Wisp": [qd("wisp_light_essence", "Wisp-Light Essence",
                "A pale mote of light in a pinch of dew. It does not burn, and it will not stay in a closed fist.", 0.6)],
    "Nightsaber Stalker": [qd("windrunner_family_locket", "Windrunner Family Locket",
                              "A small silver locket, dented by teeth, with a painted portrait of a family inside. Thessaly "
                              "will know it.", 0.25)],
    "Fel Imp": [qd("fel_imp_hoard_scrap", "Scavenged Outpost Scrap",
                   "A bent hinge, a strap buckle, a scrap of Horde canvas. Carried off and hoarded by something that can't "
                   "possibly have a use for any of it.", 0.5)],
    "Ragged Scavenger": [qd("stolen_village_scrap", "Stolen Village Scrap",
                            "Supplies pulled out of Deathknell's stores: a tin of salt, a bundle of rope. They were counted "
                            "carefully the day before they went missing.", 0.5)],
    "Agamand Servant": [qd("captured_farmer_shackle_key", "Shackle Key",
                           "A heavy iron key, cold as a grave. It fits the locks on the farmers' shackles.", 0.35)],
}


def main():
    data = json.loads(QP.read_text())
    D = data["drops"]
    if "--check" not in sys.argv:
        for creature, drops in DROPS.items():
            D.setdefault(creature, [])
            ids = {x["item_id"] for x in drops}
            D[creature] = [d for d in D[creature] if d["item_id"] not in ids] + drops
        QP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    have = {x["item_id"] for v in D.values() for x in v}
    missing = []
    for f in sorted(glob.glob(str(ROOT / "data/quests/*.json"))):
        d = json.load(open(f))
        for q in (d["quests"] if isinstance(d, dict) else d):
            for o in q.get("objectives", []):
                if o["type"] in ("fetch", "gather") and o["target"] not in have:
                    missing.append((Path(f).stem, q["quest_id"], o["target"]))
    print("fetch/gather items with no drop source:", missing or "none")


if __name__ == "__main__":
    main()
