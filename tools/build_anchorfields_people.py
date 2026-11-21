#!/usr/bin/env python3
"""The Anchorfields' people (51-54): the Anchor-Wardens of Keelstone, the House of Measures at the Observatory, the
Earthborn camped at Tiltside on the Listing Isle, House Vaelith's estate, and the few out on the shards. Idempotent.

    PYTHONPATH=. python3 tools/build_anchorfields_people.py

docs/worldtree_brief.md. Ancient, not new (Kyle, 20 Nov 2026: "aurelion is ancient, we are new"): the wardens have kept
these anchors for a thousand years, the house has measured the shelf's lean for as long, and the failing is a long
decline that's got faster; the player is the newcomer. Keelstone is a hold, not a town: traders and the zone's one
flight path, no inn. Aetherian NPCs are men until the women's sheet lands. Transplants are factionless, and nobody up
here knows what the change was.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_anchorfields as AF  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"af_skiffmaster": ["flight"]}
FLIGHT_NODES = [
    ("anchorfields", {"name": "Keelstone", "zone": AF.NAME, "master": "af_skiffmaster", "pos": [-16, 124],
                      "continent": "eastern_kingdoms"}),
]

FOOD = ["meal_saltback_roast", "hunters_brace_platter", "drink_deepwell_cordial", "cook_flour", "cook_spice",
        "cook_fruit", "cook_roots"]
GOODS = ["healing_potion_masterwork", "mana_potion_masterwork", "broadhead_arrows", "quarrel_bolts",
         "shot_mithril", "parchment", "beast_lure", "vial_crystal"]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "af_provisioner": ("Provisioner Dellan Roe", "aetherian", M, 2, "right", 53, False, FOOD,
                       "The wardens eat what Keelstone has always eaten, and Keelstone has always eaten well. That's "
                       "the one tradition here nobody's ever argued about."),
    "af_trader": ("Trader Ossian Fell", "aetherian", M, 4, "left", 53, True, GOODS,
                  "My family's sold to the wardens since the First Anchor had its second chain. I'll sell to you too, "
                  "and I'll buy anything you bring up out of the Gearwork that still turns."),
    "af_tilt_trader": ("Daisuke Moriyama", "human", M, 11, "down", 53, False, FOOD[:5] + ["parchment"],
                       "I ran a noodle bar in Osaka, nine stools and a counter. Now I run a pot on an island that leans "
                       "a little further every week, so eat it before it slides off the table."),
}

#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the end of the aqueduct arm
    "af_armwarden": ("Armwarden Teska Rell", "aetherian", M, 3, "right",
                     "The arm's carried water and walkers between the shelf and the Spillway for longer than Aurelion's "
                     "had its rings. It's never carried a ground-walker before, but it'll carry you. Mind the cracks."),
    # ---- the Estates
    "af_steward": ("Steward Olin Varrow", "aetherian", M, 4, "down",
                   "House Vaelith has held this estate for eleven hundred years. The family went to Aurelion when the "
                   "shelf began to lean, and I stayed with the house, because somebody has to wind the clocks."),
    "af_house_heir": ("Corwen Vaelith", "aetherian", M, 1, "right",
                      "My grandmother's grandmother planted that orchard. Everyone else left for the city, and I couldn't. "
                      "If the shelf goes, I'd rather be standing on it than reading about it."),
    # ---- Keelstone
    "af_warden_prime": ("Warden-Prime Aldric Sorne", "aetherian", M, 4, "down",
                        "The Anchor-Wardens have kept these three anchors for a thousand years, and we've lost an island "
                        "once. Look south-west at the Dropfield and you'll see what that looks like. I don't mean to see "
                        "it twice."),
    "af_chainwright": ("Chainwright Hollis Venn", "aetherian", M, 3, "left",
                       "Every link in the First Anchor's chains has a name and a wright who forged it. Most of them died "
                       "before my great-grandfather was born, and the links still hold. The Third Anchor's don't."),
    "af_keel_engineer": ("Engineer Pell Oravane", "aetherian", M, 4, "right",
                         "I read the anchors the way a healer reads a pulse. The First is steady, the Second's in the "
                         "Ascendancy's hands so I can't read it at all, and the Third's been slipping for forty years. "
                         "It's slipping faster now."),
    "af_warden_scout": ("Scout Varen Ashby", "aetherian", M, 2, "down",
                        "The Ascendancy took the Second Anchor and said they'd hold it better than we could. They "
                        "don't know the first thing about it, and every day they hold it, it drifts a little more."),
    "af_old_warden": ("Old Warden Ebbe Tharn", "aetherian", M, 4, "left",
                      "My grandfather's grandfather saw the island fall, the one that's the Dropfield now. He told it "
                      "to his son, and it came down to me the same way, word for word. I'd rather not add a new ending."),
    "af_skiffmaster": ("Skiffmaster Jorun Kell", "aetherian", M, 1, "right",
                       "The skiffs fly from Keelstone to Halcyon Rest and down the tree. Not over the Second Anchor, "
                       "though. The Ascendancy shoots at anything that isn't theirs."),
    # ---- the Observatory
    "af_measurer": ("Master of Measures Ivo Kestrel", "aetherian", M, 4, "down",
                    "The House of Measures has written down the shelf's lean every night for a thousand years. For most "
                    "of those years the number barely moved. I'm the first master who's had to buy a bigger ledger."),
    "af_star_reader": ("Star-Reader Caelan Duir", "aetherian", M, 2, "left",
                       "The stars don't move, so when an island moves against them, I see it. The Listing Isle has "
                       "moved more this year than in the last two hundred."),
    "af_obs_archivist": ("Archivist Bram Iselworth", "aetherian", M, 3, "right",
                         "Our oldest records are older than the anchors, and they're in a hand nobody in the house can "
                         "read any more. We copy them anyway. You don't throw away a book because you can't read it."),
    # ---- Tiltside
    "af_tilt_lead": ("Margit Halvorsen", "human", F, 4, "down",
                     "I kept oil rigs standing in the North Sea for twenty years, so a leaning island doesn't scare me "
                     "much. What scares me is that the people who built it have stopped understanding how it works."),
    "af_tilt_surveyor": ("Bartosz Wierzbicki", "human", M, 9, "right",
                         "I was a land surveyor in Krakow, and the first thing I did up here was measure the tilt. It's "
                         "four degrees and climbing. I measure it every morning, because somebody ought to."),
    "af_tilt_medic": ("Dr. Ngozi Eze", "human", F, 7, "left",
                      "I was a doctor in Ibadan, and now I treat sprained ankles on a slope and chest pains from the "
                      "Aetherians who climb over to tell us we're camped in the wrong place."),
    # ---- out on the shards
    "af_gear_tender": ("Engine-Tender Halvard Cree", "aetherian", M, 3, "down",
                       "These engines have fed the anchors since before the houses had names. I know every one of them "
                       "by the sound it makes. Lately they're making sounds I don't know."),
    "af_slip_watcher": ("Warden Siran Holt", "aetherian", M, 2, "right",
                        "I'm posted at the Third Anchor to watch it slip, and to go down to the keel if anyone ever "
                        "finds the nerve. The last wardens who went down never came back up."),
    "af_drop_scavenger": ("Wade Prentiss", "human", M, 12, "left",
                          "I salvaged wrecks off Halifax for a living. A whole island fell here a few hundred years ago, "
                          "and nobody's ever properly picked it over. That's the best wreck I've ever been on."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    if mine != set(AF.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ set(AF.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
        if not v[-1].isascii():
            bad.append(f"{k}: non-ASCII")
    sold = {i for r in load("data/npcs/vendors.json")["vendors"] if r["vendor_id"] not in VENDORS
            for i in r.get("sells", [])}
    for k, v in VENDORS.items():
        bad += [f"{k}: nobody else sells {i}" for i in v[7] if i not in sold]
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    zone = zone_key(AF.NAME)
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = AF.NPC_POSITIONS[vid]
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
        x, y = AF.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    save("data/travel/travel_data.json", td)
    print(f"The Anchorfields: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
