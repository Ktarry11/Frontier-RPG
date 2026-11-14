"""Create / reposition the Central Barrens quest givers from tools/handbuilt_central_barrens.NPC_POSITIONS.
Idempotent.

    python3 tools/sync_central_barrens_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_central_barrens import NPC_POSITIONS   # noqa: E402

NEW_NPCS = [
    dict(npc_id="cb_waterkeeper", name="Waterkeeper Sanu Goldenhoof", race="tauren", gender="male",
         appearance_variant=3, facing="left",
         greeting="The water remembers every traveller. I only try to keep it from remembering the wrong ones."),
    dict(npc_id="cb_pools_warden", name="Pilgrim-Warden Torga", race="orc", gender="female",
         appearance_variant=9, facing="down",
         greeting="They came to pray and they never went home. Someone should still be here to hear them."),
    dict(npc_id="cb_caravan_master", name="Caravan-Master Dogan Ironcart", race="goblin", gender="male",
         appearance_variant=7, facing="right",
         greeting="Raider's Rest has water, shade and a fair price on everything. The bandits do not like the third one."),
    dict(npc_id="cb_shrine_keeper", name="Keeper Ahnmar Stonetotem", race="tauren", gender="male",
         appearance_variant=9, facing="down",
         greeting="Quiet, friend. The stone is listening, and so, I think, is the one who fell."),
    dict(npc_id="cb_dreadmist_scout", name="Scout Zarla Blackthorn", race="orc", gender="female",
         appearance_variant=12, facing="up",
         greeting="Keep your voice down. The cult has ears in the rocks, and I'd like to keep the one I have left."),
    dict(npc_id="cb_quilboar_ranger", name="Ranger Kishi Plainstalker", race="tauren", gender="female",
         appearance_variant=4, facing="down",
         greeting="Boars to the left, boars to the right, and a road down the middle. It's a pleasant walk, if you like arguing."),
    dict(npc_id="cb_bridgewarden", name="Bridgewarden Karga Redfang", race="orc", gender="female",
         appearance_variant=2, facing="left",
         greeting="Southfury bridge, Barrens end. Every plank paid for in blood and bad weather. Mind your step."),
]
RENAMES = {"barrens_herder_1": "Herder Magra Dustwalker"}


def main():
    path = ROOT / "data/npcs/ambient_npcs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {r["npc_id"]: r for r in data["npcs"]}
    for n in NEW_NPCS:
        rec = by_id.get(n["npc_id"])
        if rec is None:
            rec = {"zone": "central_barrens"}
            data["npcs"].append(rec)
            by_id[n["npc_id"]] = rec
        rec.update(n)
        rec["zone"] = "central_barrens"
    for nid, name in RENAMES.items():
        by_id[nid]["name"] = name
    moved = 0
    for nid, (x, y) in NPC_POSITIONS.items():
        rec = by_id[nid]
        if (rec.get("x"), rec.get("y")) != (x, y):
            rec["x"], rec["y"] = x, y
            moved += 1
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"npcs: {len(NEW_NPCS)} created/updated, {moved} positioned")


if __name__ == "__main__":
    main()
