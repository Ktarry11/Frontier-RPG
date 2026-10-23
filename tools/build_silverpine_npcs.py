"""
Silverpine cast: ambient NPCs and vendors.  Idempotent - upserts by id.  Sections are added stage by stage.

    python3 tools/build_silverpine_npcs.py

Positions come from tools/handbuilt_silverpine_<zone>.NPC_POSITIONS (so the map and the data cannot drift).
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_silverpine_north import NPC_POSITIONS as NORTH_POS   # noqa: E402

F, M = "female", "male"
# id: (name, zone slug, race, gender, variant, facing, greeting)
NORTH_AMBIENT = {
    "sp_rg_captain": ("Captain Hollin Vesk", "silverpine_north", "forsaken", M, 5, "down",
                      "Welcome to the Rear Guard. We hold the gate so the Sepulcher can pretend the north is quiet."),
    "sp_rg_apothecary": ("Apothecary Pell", "silverpine_north", "forsaken", M, 1, "right",
                         "Don't touch the cauldron. Don't breathe the cauldron. Look at it from a distance, if you must."),
    "sp_rg_cleric": ("Dark Cleric Ravenna", "silverpine_north", "forsaken", F, 2, "down",
                     "The Light never answered us. The Dark has, at least. It prefers prayers in a lower key."),
    "sp_north_scout": ("Silverpine Scout", "silverpine_north", "forsaken", M, 9, "down",
                       "Worgen prowl these woods some nights. Keep to the road after dark."),
    "sp_farthing_gaffer": ("Gaffer Olsen", "silverpine_north", "forsaken", M, 6, "down",
                           "Forty years I kept this farm. Three more since I died. The hounds don't seem to mind either way."),
    "sp_farthing_widow": ("Widow Marta", "silverpine_north", "forsaken", F, 7, "left",
                          "My husband walks past my window every night. He doesn't knock. I leave the lamp on."),
    "sp_north_cemetery_keeper": ("Keeper Oswin", "silverpine_north", "forsaken", M, 9, "down",
                                 "Raven Hill's dead don't always stay that way. I've buried the same corpse three times this month."),
    "sp_rh_acolyte": ("Acolyte Dessa", "silverpine_north", "forsaken", F, 12, "left",
                      "The moss on these stones isn't growing. It's feeding. I'd stay on the path."),
    "sp_df_huntress": ("Huntress Verrel", "silverpine_north", "forsaken", F, 15, "right",
                       "The crows don't die. They only look at you, as if you were the strange one."),
    "sp_df_farmhand": ("Tobb the Farmhand", "silverpine_north", "forsaken", M, 3, "down",
                       "I sleep in the barn. The scarecrows don't climb the ladder, so far."),
    "sp_sep_gatewarden": ("Gatewarden Ilsa", "silverpine_north", "forsaken", F, 8, "down",
                          "The Sepulcher is open to the dead. For everyone else, it is a door with a very bad temper."),
    "sp_orchard_warden": ("Orchard-Warden Malwick", "silverpine_north", "forsaken", M, 4, "left",
                          "Malden grew the sweetest apples in Lordaeron. Now the orchard grows what it likes."),
    "sp_north_pools_warden": ("Warden Yaelis", "silverpine_north", "forsaken", F, 12, "down",
                              "The Shadowspring used to be sweet. Now it runs black, and the things that drink from it run hungry."),
    "sp_sd_webhunter": ("Webhunter Corvane", "silverpine_north", "forsaken", M, 13, "left",
                        "The Skittering Dark is aptly named. Keep your eyes up. The thing that gets you is never on the ground."),
}

# id: (name, zone slug, race, gender, variant, facing, greeting, sells, gear_level, sells_gear)
NORTH_VENDORS = {
    "sp_rg_quartermaster": ("Quartermaster Brask", "silverpine_north", "forsaken", M, 11, "down",
                            "Rear Guard stores, signed for in duplicate. The duplicate is for the dead; the original is for the living.",
                            ["healing_potion_minor", "healing_potion_standard", "mana_potion_minor", "bread_and_cheese",
                             "roasted_meat"], 14, True),
}


def _upsert(data, key, id_key, rec):
    for i, r in enumerate(data[key]):
        if r.get(id_key) == rec[id_key]:
            data[key][i] = {**r, **rec}
            return 0
    data[key].append(rec)
    return 1


def main():
    amb = json.loads(Path("data/npcs/ambient_npcs.json").read_text())
    ven = json.loads(Path("data/npcs/vendors.json").read_text())
    added = 0
    for nid, (name, zone, race, gender, var, facing, greet) in NORTH_AMBIENT.items():
        x, y = NORTH_POS[nid]
        added += _upsert(amb, "npcs", "npc_id", dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet,
                                                      gender=gender, race=race, appearance_variant=var, facing=facing))
    for vid, (name, zone, race, gender, var, facing, greet, sells, gl, sg) in NORTH_VENDORS.items():
        x, y = NORTH_POS[vid]
        added += _upsert(ven, "vendors", "vendor_id", dict(
            vendor_id=vid, name=name, zone=zone, x=x, y=y, tile_sprite="npc", sells=sells, buys_from_player=True,
            faction="forsaken", gear_level=gl, sells_gear=sg, race=race, appearance_variant=var, gender=gender, greeting=greet))
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n")
    Path("data/npcs/vendors.json").write_text(json.dumps(ven, indent=2, ensure_ascii=False) + "\n")
    print(f"ambient {len(NORTH_AMBIENT)}, vendors {len(NORTH_VENDORS)}, +{added} new records")


if __name__ == "__main__":
    main()
