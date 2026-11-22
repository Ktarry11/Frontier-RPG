#!/usr/bin/env python3
"""The Ascendant Bastions' people (54-57): the deserters at Dawnspear Wreck, the Earthborn conscripts in the Yard
Pens, and the two the Ascendancy kept on out on the islands. Idempotent.

    PYTHONPATH=. python3 tools/build_ascendant_bastions_people.py

docs/worldtree_brief.md. This is the enemy's own ground, so nobody here is safe in the open: the wreck is the one place
the free skiffs dare to land, and the pens are where the yard keeps the Earthborn it put to work on the warships.
Dawnspear Wreck is the Bastions' town, on its own map since 22 Nov 2026 (Kyle's town rule;
tools/handbuilt_worldtree_dawnspear_wreck.py): the inn in the stern, the mail and the zone's one flight path. The Yard
Pens stay where they are, because the conscripts are held there (Kyle's call). A person stands on whichever map lists
them. The Aetherians wear the AE-M
and AE-W looks picked for their jobs (world/race_registry.py: men 5+N for m-N, women N-1 for w-N). Transplants are
factionless, and nobody up here knows what the change was.

THE ASCENDANCY'S GENERAL is named here for the first time: Ascendant-General Maelis Ardane, once the brightest student
of the House of the Patient Lens (Kyle's twenty questions, 7: "a scholar gone military: once one of the houses'
brightest, she decided study was too slow and took the army with her"). Her old teacher is at the wreck. She isn't
met on the Bastions; she's the Firmament's.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_ascendant_bastions as AB  # noqa: E402
from tools import handbuilt_worldtree_dawnspear_wreck as DW  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"ab_skiffmaster": ["flight"], "dw_steward": ["inn"]}
FLIGHT_NODES = [
    ("ascendant_bastions", {"name": "Dawnspear Wreck", "zone": DW.NAME, "master": "ab_skiffmaster", "pos": [-12, 112],
                            "continent": "eastern_kingdoms"}),
]

FOOD = ["meal_saltback_roast", "hunters_brace_platter", "drink_deepwell_cordial", "cook_flour", "cook_spice",
        "cook_fruit", "cook_roots"]
GOODS = ["healing_potion_masterwork", "mana_potion_masterwork", "barbed_arrows", "shot_void",
         "parchment", "beast_lure", "vial_crystal"]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "ab_provisioner": ("Provisioner Hanne Stoll", "aetherian", F, 10, "left", 56, False, FOOD,
                       "Everything I sell came off the Dawnspear's stores, or off a skiff that risked the run from "
                       "Aurelion, so eat it slowly. We don't know when the next one's coming."),
    "ab_trader": ("Trader Emric Sallow", "aetherian", M, 11, "left", 56, True, GOODS,
                  "I sold to the Ascendancy for thirty years, and then they stopped paying. I sell to deserters now. "
                  "The coin's worse and the company's a great deal better."),
}

#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- Dawnspear Wreck
    "ab_wreck_captain": ("Captain Isolde Marrane", "aetherian", F, 20, "down",
                         "I was ordered to fire on Tethertown, a camp of Earthborn who'd done nothing but be there. I "
                         "brought my ship down here instead, with everyone aboard who agreed with me. She'll never fly "
                         "again, and I've never been prouder of her."),
    "ab_unsworn_scholar": ("Magister Orla Thessan", "aetherian", F, 16, "right",
                           "I taught Maelis Ardane everything she knows about the sky. She was the brightest student "
                           "the Patient Lens ever had, and she decided we were too slow. I came here to watch what she's "
                           "building, because I think I owe the sky that much."),
    "ab_lancer_deserter": ("Lancer Tavin Roake", "aetherian", M, 22, "left",
                           "I put my lance down at the Proving Grounds in front of my whole wing. Half of them laughed, "
                           "and three of them followed me here that night. I'd like to get the rest out before the "
                           "warships sail."),
    "ab_wreck_surgeon": ("Surgeon Nell Avary", "aetherian", F, 8, "right",
                         "Most of what I treat is burns from the storm guns, and the rest is what the Proving Grounds "
                         "does to young lancers. The Ascendancy calls that training. I call it a waste of good people."),
    "ab_skiffmaster": ("Skiffmaster Pell Daray", "aetherian", M, 8, "right",
                       "The free skiffs land at the wreck and nowhere nearer the fort, because the Gunline shoots at "
                       "anything it doesn't recognise. I can get you to Aurelion or anywhere else that's still friendly."),
    "ab_lookout": ("Lookout Fen Arden", "aetherian", M, 16, "down",
                   "From the bow I can see the whole quay. They've laid three new keels this month, and the yard works "
                   "through the night now. Whatever they're building it for, they're in a hurry."),
    # ---- the Yard Pens
    "ab_pens_foreman": ("Rosa Delgado", "human", F, 4, "down",
                        "I welded pipelines in Monterrey for fifteen years. The Ascendancy found that out, and now I weld "
                        "warships. I'm very good at it, and I'm very careful about which seams I make strong."),
    "ab_pens_medic": ("Siobhan Keane", "human", F, 7, "left",
                      "I was a ward nurse in Galway. Here I've got two hundred patients, one tent and whatever the "
                      "deserters can smuggle in. Ask me how they're doing and I'll tell you the truth."),
    "ab_pens_rigger": ("Tomasz Bielecki", "human", M, 11, "right",
                       "My father made sails in Gdansk, and so did I. The warships take sails of a kind I've never seen, "
                       "but cloth is cloth and a knot is a knot. I remember every ship I've rigged here, every one."),
    "ab_pens_cook": ("Hamza Qureshi", "human", M, 9, "down",
                     "I had a curry house in Bradford with forty covers. Now I feed two hundred people on what the yard "
                     "throws out, and nobody's sent a plate back yet."),
    # ---- out on the islands
    "ab_archive_clerk": ("Clerk Anselm Rook", "aetherian", M, 6, "right",
                         "My job is to read what the Inquisitors bring me and burn what they tell me to burn. I copy "
                         "everything first. I'm not brave, but I can't watch a thousand years go into a brazier."),
    "ab_harvest_keeper": ("Storm-Keeper Edda Quill", "aetherian", F, 1, "left",
                          "I kept these collectors for the old house that owned this rock, before the Ascendancy came. "
                          "They kept me on because nobody else knows how to make the storm behave. Neither do I, most "
                          "days."),
    # ---- Dawnspear Wreck's own (the town map)
    "dw_steward": ("Steward Corla Venn", "aetherian", F, 13, "down",
                   "I ran the Dawnspear's mess for eleven years, and I'm still running it, only now the ship's lying on "
                   "her side. The bunks are in the stern and the stew's always on. If you want to come back here quickly, "
                   "I'll mark your hearthstone."),
    "dw_gatewarden": ("Gate-Keeper Brannoc Hale", "aetherian", M, 22, "right",
                      "I wore the Ascendancy's bronze for nine years before I came down with the captain. Now I keep the "
                      "gangway, and I look hard at everybody who comes down it, because the fort would love to know "
                      "who lives here."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    both = set(AB.NPC_POSITIONS) & set(DW.NPC_POSITIONS)
    if both:
        bad.append(f"on both maps: {sorted(both)}")
    if mine != set(AB.NPC_POSITIONS) | set(DW.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ (set(AB.NPC_POSITIONS) | set(DW.NPC_POSITIONS)))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
        if not v[-1].isascii():
            bad.append(f"{k}: non-ASCII")
    sold = {i for r in load("data/npcs/vendors.json")["vendors"] if r["vendor_id"] not in VENDORS
            for i in r.get("sells", [])}
    for k, v in VENDORS.items():
        bad += [f"{k}: nobody else sells {i}" for i in v[7] if i not in sold]
    return bad


def where(nid):
    """(zone key, x, y) for a person, from whichever map lists them."""
    mod = DW if nid in DW.NPC_POSITIONS else AB
    x, y = mod.NPC_POSITIONS[nid]
    return zone_key(mod.NAME), x, y


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        zone, x, y = where(vid)
        rec = dict(vendor_id=vid, name=name, zone=zone, x=x, y=y, tile_sprite="npc", buys_from_player=True,
                   faction="neutral", gear_level=gl, sells_gear=gear, race=race, gender=gender,
                   appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        zone, x, y = where(nid)
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    # the Stern Mess keeps the mail, like every inn (qa_auction_house: a mailbox by every inn)
    box = next((r for r in ad["npcs"] if r["npc_id"] == "mailbox_dw_steward"), None)
    if box is None:
        box = {"npc_id": "mailbox_dw_steward"}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=zone_key(DW.NAME), x=36, y=38, facing="down", race="aetherian",
               appearance_variant=0, is_mailbox=True, prop="assets/buildings/ae_mail_pylon.png",
               greeting="The wreck's mail goes out with the free skiffs, when they dare to fly. The pylon came off the "
                        "Dawnspear's bridge, and it still has the Ascendancy's mark scratched off it.")
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    save("data/travel/travel_data.json", td)
    print(f"The Ascendant Bastions: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
