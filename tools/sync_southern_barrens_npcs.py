"""Create / reposition the Southern Barrens quest givers + waystation vendor from
tools/handbuilt_southern_barrens.NPC_POSITIONS.  Idempotent.

    python3 tools/sync_southern_barrens_npcs.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_southern_barrens import NPC_POSITIONS   # noqa: E402

ZONE = "southern_barrens"
NEW_NPCS = [
    dict(npc_id="sb_rift_warden", name="Rift-Warden Brakka Stonehoof", race="tauren", gender="female",
         appearance_variant=5, facing="down",
         greeting="Everything south of here is the Rift's business. Everything north of it is mine. Try to keep them separate."),
    dict(npc_id="sb_bonehunter", name="Bonehunter Rurk Gravetusk", race="orc", gender="male",
         appearance_variant=11, facing="right",
         greeting="Giants walked this plain once. Now it's bones, hyenas and me. I'm the only one who likes the company."),
    dict(npc_id="sb_thornwatch", name="Thornwatch Ranger Oggra", race="orc", gender="female",
         appearance_variant=6, facing="down",
         greeting="Quilboar to the south, quilboar to the north, and one very annoyed ranger in the middle. Don't stand near my fire."),
    dict(npc_id="sb_keep_spy", name="Spy Zhuul Quicksight", race="troll", gender="male",
         appearance_variant=3, facing="left",
         greeting="Keep your voice low, mon. Dem dwarves have good ears and bad tempers."),
    dict(npc_id="sb_modan_scout", name="Dig-Scout Tarrik Ashmane", race="tauren", gender="male",
         appearance_variant=8, facing="down",
         greeting="Quarry's loud, the dwarves are louder, and the pit keeps getting deeper. I don't like it."),
    dict(npc_id="sb_hoodoo_huntress", name="Huntress Alamir Bloodtotem", race="tauren", gender="female",
         appearance_variant=2, facing="down",
         greeting="Stay low in the spires. The wind carries voices out there, and some of them are not the wind's."),
    dict(npc_id="sb_crater_digger", name="Excavator Fizzwick Boltcog", race="goblin", gender="male",
         appearance_variant=4, facing="left",
         greeting="Fizzwick Boltcog, licensed excavator! Okay, not licensed. Okay, not an excavator. But I know a hole when I see one."),
]
VENDOR = dict(vendor_id="sb_waystation_vendor", name="Provisioner Hemma Redbrand", zone=ZONE, tile_sprite="npc",
              sells=["healing_potion_minor", "healing_potion_standard", "mana_potion_minor", "mana_potion_standard",
                     "bread_and_cheese", "roasted_meat", "guardian_elixir_standard", "battle_elixir_standard"],
              buys_from_player=True, faction="neutral", gear_level=22, sells_gear=True, race="orc",
              appearance_variant=14, gender="female",
              greeting="Waystation stores, fresh from Taurajo and only slightly rained on. What'll it be?")


def main():
    path = ROOT / "data/npcs/ambient_npcs.json"
    data = json.loads(path.read_text())
    by_id = {r["npc_id"]: r for r in data["npcs"]}
    for n in NEW_NPCS:
        rec = by_id.get(n["npc_id"])
        if rec is None:
            rec = {}
            data["npcs"].append(rec)
        rec.update(n)
        rec["zone"] = ZONE
        rec["x"], rec["y"] = NPC_POSITIONS[n["npc_id"]]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    vpath = ROOT / "data/npcs/vendors.json"
    vd = json.loads(vpath.read_text())
    rec = next((v for v in vd["vendors"] if v["vendor_id"] == VENDOR["vendor_id"]), None)
    if rec is None:
        rec = {}
        vd["vendors"].append(rec)
    rec.update(VENDOR)
    rec["x"], rec["y"] = NPC_POSITIONS["sb_waystation_vendor"]
    vpath.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n")
    print(f"npcs: {len(NEW_NPCS)} placed, 1 vendor")


if __name__ == "__main__":
    main()
