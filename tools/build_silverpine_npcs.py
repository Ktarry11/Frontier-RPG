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
from tools.handbuilt_silverpine_south import NPC_POSITIONS as SOUTH_POS   # noqa: E402
from tools.handbuilt_sepulcher import NPC_POSITIONS as SEP_POS            # noqa: E402

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


SOUTH_AMBIENT = {
    "sp_south_gate_scout": ("Deathguard Lyle", "silverpine_south", "forsaken", M, 2, "down",
                            "The Rear Guard marks the north. Past here the pines belong to whatever has the most teeth."),
    "sp_south_hunter": ("Forsaken Hunter", "silverpine_south", "forsaken", M, 13, "down",
                        "Even death didn't stop me from putting meat on the table. Old habits."),
    "sp_buckle_farmer": ("Farmer Bucklebree", "silverpine_south", "forsaken", M, 6, "down",
                         "Three generations on this farm. I'm the first to work it dead. I'd say the yield hasn't changed."),
    "sp_buckle_goodwife": ("Goodwife Merriam", "silverpine_south", "forsaken", F, 7, "left",
                           "The hogs went first. Then the quilts. I've lost track of what's left to lose."),
    "sp_pond_marshwalker": ("Marshwalker Thorne", "silverpine_south", "forsaken", M, 9, "down",
                            "Olivia's Pond was a pretty spot once. Now the water moves when nothing is stirring it."),
    "sp_elem_foreman": ("Overseer Hobart", "silverpine_south", "forsaken", M, 4, "left",
                        "Deep Elem paid well, until it didn't. The kobolds stayed. So did I. Neither of us got a pension."),
    "sp_south_march_sergeant": ("Sergeant Dallow", "silverpine_south", "forsaken", M, 5, "down",
                                "The March exists to keep the road to Ambermill open. Lately that's a full-time fight."),
    "sp_valgan_surgeon": ("Field Surgeon Ashe", "silverpine_south", "forsaken", F, 3, "down",
                          "I stitch what's torn and I remove what's gone off. The two jobs overlap more than you'd like."),
    "sp_pyre_hearthwarden": ("Hearthwarden Brand", "silverpine_south", "forsaken", M, 8, "down",
                             "Pyrewood burned for a reason. Whatever rose from the ashes didn't read the reasons."),
    "sp_talon_trapper": ("Trapper Hask", "silverpine_south", "forsaken", M, 15, "left",
                         "Traps still work on the dead. They just have to be bigger."),
    "sp_peril_packbreaker": ("Packbreaker Rynn", "silverpine_south", "forsaken", F, 12, "down",
                             "A pack leader is a promise to the pack. I intend to break a few promises."),
    "sp_wall_corporal": ("Corporal Teague", "silverpine_south", "forsaken", M, 0, "down",
                         "The Wall's been shut since the night the gate fell. We don't open it. We don't let anything open it."),
    "sp_amber_millwright": ("Millwright Haskell", "silverpine_south", "forsaken", M, 11, "left",
                            "Ambermill ran on Dalaran gold and Dalaran sawdust. Now it runs on ghosts and spite."),
    "sp_amber_magister": ("Magister Orsolo", "silverpine_south", "forsaken", M, 14, "down",
                          "The waygate was a mill-lift, once. Then someone aimed it somewhere worse."),
    "sp_ferryman": ("Ferryman Gael", "silverpine_south", "forsaken", M, 1, "down",
                    "The boat goes where the lake lets it. Pay up front. The lake keeps a tally."),
    "sp_ferry_dockhand": ("Dockhand Pim", "silverpine_south", "forsaken", F, 10, "down",
                          "Crates wash up all hours. Half of them are empty. The other half I don't open."),
    "sp_sfk_gatekeeper": ("Gatekeeper Marl", "silverpine_south", "forsaken", M, 7, "down",
                          "Behind that portcullis is Shadowfang Keep. If you hear howling, it's the draught. Say it's the draught."),
}

SOUTH_VENDORS = {
    "sp_south_quartermaster": ("Quartermaster Vorn", "silverpine_south", "forsaken", M, 12, "down",
                               "Valgan's Field supply, signed in duplicate. Don't ask where the stock came from. Most of it fought back.",
                               ["healing_potion_minor", "healing_potion_standard", "mana_potion_minor", "mana_potion_standard",
                                "bread_and_cheese", "roasted_meat", "battle_elixir_minor"], 18, True),
}


SEP_AMBIENT = {
    "sepulcher_commander": ("Commander Halvard Vane", "sepulcher", "forsaken", M, 5, "down",
                            "The Sepulcher holds the north-west of Silverpine. The dead have taken to it better than the living ever did."),
    "sepulcher_adjutant": ("Adjutant Kess", "sepulcher", "forsaken", F, 12, "left",
                           "The Commander speaks to you, or he doesn't. Either way, stand up straight. Not that it matters."),
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
    for nid, (name, zone, race, gender, var, facing, greet) in SOUTH_AMBIENT.items():
        x, y = SOUTH_POS[nid]
        added += _upsert(amb, "npcs", "npc_id", dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet,
                                                      gender=gender, race=race, appearance_variant=var, facing=facing))
    for vid, (name, zone, race, gender, var, facing, greet, sells, gl, sg) in SOUTH_VENDORS.items():
        x, y = SOUTH_POS[vid]
        added += _upsert(ven, "vendors", "vendor_id", dict(
            vendor_id=vid, name=name, zone=zone, x=x, y=y, tile_sprite="npc", sells=sells, buys_from_player=True,
            faction="forsaken", gear_level=gl, sells_gear=sg, race=race, appearance_variant=var, gender=gender, greeting=greet))
    for nid, (name, zone, race, gender, var, facing, greet) in SEP_AMBIENT.items():
        x, y = SEP_POS[nid]
        added += _upsert(amb, "npcs", "npc_id", dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet,
                                                      gender=gender, race=race, appearance_variant=var, facing=facing))
    for rec in amb["npcs"]:                      # the nine ambient Sepulcher residents keep their records; the map moves them
        if rec.get("zone") == "sepulcher" and rec["npc_id"] in SEP_POS:
            rec["x"], rec["y"] = SEP_POS[rec["npc_id"]]
    for rec in ven["vendors"]:
        if rec.get("zone") == "sepulcher" and rec["vendor_id"] in SEP_POS:
            rec["x"], rec["y"] = SEP_POS[rec["vendor_id"]]
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n")
    Path("data/npcs/vendors.json").write_text(json.dumps(ven, indent=2, ensure_ascii=False) + "\n")
    print(f"ambient {len(NORTH_AMBIENT) + len(SOUTH_AMBIENT) + len(SEP_AMBIENT)}, vendors {len(NORTH_VENDORS) + len(SOUTH_VENDORS)}, +{added} new records")


if __name__ == "__main__":
    main()
