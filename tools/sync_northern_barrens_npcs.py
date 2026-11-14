"""Create / reposition the Northern Barrens quest givers + Base Camp vendor from
tools/handbuilt_northern_barrens.NPC_POSITIONS.  Idempotent.

    python3 tools/sync_northern_barrens_npcs.py

(farwatch_officer = Outrider Kelsara and morshan_outrider = Warsong Outrider Dask already exist; they are only
repositioned and given quest chains by tools/build_northern_barrens_quests.py.)
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_northern_barrens import NPC_POSITIONS   # noqa: E402

ZONE = "northern_barrens"
NEW_NPCS = [
    dict(npc_id="nb_road_warden", name="Road-Warden Hargak Ironvein", race="orc", gender="male",
         appearance_variant=9, facing="down",
         greeting="Gold Road, my road, my rules. Pay the toll, or don't. Bandits do the second one and I'd rather you didn't."),
    dict(npc_id="nb_coast_sergeant", name="Beachmaster Kizzle Fuseblast", race="goblin", gender="female",
         appearance_variant=3, facing="left",
         greeting="Welcome to the Merchant Coast! Mind the crabs, the pirates and the cannon. In that order."),
    dict(npc_id="nb_oasis_scout", name="Scout Mahri Dustwalker", race="tauren", gender="female",
         appearance_variant=4, facing="down",
         greeting="Don't drink the water. I wish I were joking. The hounds don't care, but they're not as picky as you."),
    dict(npc_id="nb_rampart_captain", name="Captain Korvash Gatebreaker", race="orc", gender="male",
         appearance_variant=13, facing="up",
         greeting="Behind me, the Rampart. In front of me, the Kaldorei. Between us, you. Choose a side quickly."),
    dict(npc_id="nb_dryhills_huntress", name="Huntress Zan'ula Skyshard", race="troll", gender="female",
         appearance_variant=6, facing="right",
         greeting="Hush, mon. The hills have ears and the Witchwings have eyes. Mostly eyes. Mostly hungry."),
    dict(npc_id="nb_hollow_shaman", name="Earthcaller Rohna Skyhorn", race="tauren", gender="female",
         appearance_variant=7, facing="up",
         greeting="The earth is crying out, child. It isn't a happy cry. I'd like you to make it stop."),
    dict(npc_id="nb_fen_warden", name="Fenwarden Dugmok Mudhoof", race="tauren", gender="male",
         appearance_variant=10, facing="left",
         greeting="Everything in the fen is slow, wet and hungry. Welcome. You'll fit right in."),
    dict(npc_id="nb_sludge_inspector", name="Salvager Nix Cogsprocket", race="goblin", gender="male",
         appearance_variant=5, facing="down",
         greeting="I used to work for the Venture Company. Used to. Now I watch them work, from a safe distance. With a very large wrench."),
    dict(npc_id="nb_lode_surveyor", name="Claim-Surveyor Gruda Deepdelve", race="orc", gender="female",
         appearance_variant=12, facing="up",
         greeting="The Lode's ours by right and by paperwork. The Company has the pickaxes. I have the stubborn."),
]
VENDOR = dict(vendor_id="nb_basecamp_vendor", name="Quartermaster Gruzk Ironhide", zone=ZONE, tile_sprite="npc",
              sells=["healing_potion_minor", "healing_potion_standard", "mana_potion_minor", "mana_potion_standard",
                     "bread_and_cheese", "roasted_meat", "guardian_elixir_standard", "battle_elixir_standard"],
              buys_from_player=True, faction="neutral", gear_level=20, sells_gear=True, race="orc",
              appearance_variant=8, gender="male",
              greeting="Base Camp stores. Heavy on the jerky, light on the courtesy. What do you need?")


def main():
    path = ROOT / "data/npcs/ambient_npcs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {r["npc_id"]: r for r in data["npcs"]}
    for n in NEW_NPCS:
        rec = by_id.get(n["npc_id"])
        if rec is None:
            rec = {}
            data["npcs"].append(rec)
        rec.update(n)
        rec["zone"] = ZONE
        rec["x"], rec["y"] = NPC_POSITIONS[n["npc_id"]]
    for nid in ("farwatch_officer", "morshan_outrider"):
        by_id[nid]["x"], by_id[nid]["y"] = NPC_POSITIONS[nid]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    vpath = ROOT / "data/npcs/vendors.json"
    vd = json.loads(vpath.read_text(encoding="utf-8"))
    rec = next((v for v in vd["vendors"] if v["vendor_id"] == VENDOR["vendor_id"]), None)
    if rec is None:
        rec = {}
        vd["vendors"].append(rec)
    rec.update(VENDOR)
    rec["x"], rec["y"] = NPC_POSITIONS["nb_basecamp_vendor"]
    vpath.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"npcs: {len(NEW_NPCS)} placed + 2 repositioned, 1 vendor")


if __name__ == "__main__":
    main()
