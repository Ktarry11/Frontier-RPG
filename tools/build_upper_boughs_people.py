#!/usr/bin/env python3
"""The Upper Boughs' people: Highrest, the Windwardens' camp on the last shelf of wood below the cloud, and the few
trolls out on the high boughs. Idempotent.

    PYTHONPATH=. python3 tools/build_upper_boughs_people.py

docs/worldtree_brief.md. Highrest was a camp on the ring's platform with no inn and no flight path; since 22 Nov 2026
it's its own map and the tier's hub (Kyle: "we do need hubs in the boughs"), with an inn, the mail and a flight path
(tools/handbuilt_worldtree_highrest.py). Still no bats (the wind up here would take a bat off the tree): the flight path
is the wyverns, who ride it. The stair, the ladder and the two scouts stay out where their work is. Kyle, 14 Nov 2026: "we should start having more earth people throughout zones", more of them the
higher the zone; here, a mountaineer and meteorologist from Tromso who came up to read the weather from the top.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_upper_boughs as LB  # noqa: E402
from tools import handbuilt_worldtree_highrest as HI  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"hr_wyvern_handler": ["flight"], "hr_innkeeper": ["inn"]}
FLIGHT_NODES = [
    ("upper_boughs", {"name": HI.NAME, "zone": HI.NAME, "master": "hr_wyvern_handler", "pos": [-34, 139],
                      "continent": "eastern_kingdoms"}),
]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "ub_provisioner": ("Provisioner Hakka", "troll", M, 2, "right", 48, False,
                       ["meal_saltback_roast", "hunters_brace_platter", "drink_deepwell_cordial", "cook_flour", "cook_spice", "cook_fruit", "cook_roots"],
                       "It's a long haul up from Heartwatch with a sack on your back, so nothing up here is cheap. "
                       "Eat it hot, though, because the wind takes the heat out of you faster than you'd think."),
    "ub_trader": ("Trader Sel'ma", "troll", F, 5, "left", 48, False,
                  ["healing_potion_mega", "mana_potion_mega", "kit_field_repair", "broadhead_arrows", "quarrel_bolts",
                   "shot_mithril", "parchment", "beast_lure", "vial_crystal"],
                  "Rope, arrows, potions, and I'll buy anything you pull off that wreck. Tie down whatever you put "
                  "on my counter, or the wind will have it before I've paid you."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "hr_innkeeper": ("Innkeeper Lo'mai", "troll", F, 6, "down",
                     "The Cloudside Rest is the last bed on the tree, and the wind rocks it all night long. Sleep here "
                     "and I'll mark you as one of mine, so you'll wake up in Highrest wherever you wander."),
    "hr_wyvern_handler": ("Wyvern Rider Zakko", "troll", M, 8, "down",
                          "No bat could fly this high, the wind would tear it off the tree. Wyverns ride the wind instead "
                          "of fighting it, so mine will carry you down to the Settlement or out to any roost the Horde "
                          "keeps."),
    "ub_windwarden": ("Windwarden Kazra'jin", "troll", M, 11, "down",
                      "Highrest is as far as anyone lives. Above us the branches get too thin to build on, and then "
                      "there's only cloud. I've climbed into it three times, and three times I came back down."),
    "ub_wyvern_tamer": ("Wyvern-Tamer Gu'lok", "troll", M, 9, "left",
                        "The wild wyverns roost on the east boughs, and some of them will take a rider if you're "
                        "patient and you don't mind losing a finger. I've lost two, and I'm still patient."),
    "ub_storm_shaman": ("Stormcaller Ixi", "troll", F, 6, "right",
                        "Lightning hits this tree more than anything else in the world, because it's the tallest "
                        "thing in the world. One bolt split the trunk open and the storm crawled inside. It's still "
                        "down there, and I can hear it thinking."),
    "ub_skywatcher": ("Skywatcher Tal'mae", "troll", F, 3, "down",
                      "A boat fell out of the sky onto the north bough, a boat with no water under it. Tel'zan wants "
                      "to know who sailed it, and so do I. Its guardians don't want us to know at all."),
    "ub_old_climber": ("Old Muzzi", "troll", M, 1, "right",
                       "I climbed with Ruk'tan and Zel'ji when we were young and stupid. Ruk'tan turned back, and "
                       "Zel'ji didn't come back. I've got one more climb left in these knees, maybe."),
    "ub_transplant": ("Ingrid Haugen", "human", F, 4, "left",
                      "I'm a mountaineer and a meteorologist from Tromso, so I've spent my life where the weather "
                      "is worst. This tree makes its own. It pulls storms in like a mountain does, and I've never "
                      "seen anything like it."),
    "ub_stairwarden": ("Stairwarden Rhoka", "troll", F, 8, "down",
                       "The root stair goes back down to Heartwatch, and I count everyone who comes up it. I count "
                       "them going down again too, and the numbers don't always match."),
    "ub_ladderkeeper": ("Ladderkeeper Vosh", "troll", M, 12, "down",
                        "My grandfather hung the last ladder up there, above the cloud. I keep the knots on this end, "
                        "and I check them every morning, because he'd climb down and kill me if I didn't."),
    "ub_scout_roosts": ("Scout Tazzo", "troll", M, 10, "left",
                        "The roosts go on further than you'd think, and every one has a wyvern in it. I watch the big "
                        "one with the crest, because when she flies, the whole flock flies with her."),
    "ub_scout_wreck": ("Scout Neema", "troll", F, 13, "down",
                       "The wreck's guards don't sleep and they don't eat. I've watched them for nine days. They walk "
                       "the same circle round the boat, and they've never once stepped off it."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    placed = set(LB.NPC_POSITIONS) | set(HI.NPC_POSITIONS)
    if set(LB.NPC_POSITIONS) & set(HI.NPC_POSITIONS):
        bad.append(f"on both maps: {sorted(set(LB.NPC_POSITIONS) & set(HI.NPC_POSITIONS))}")
    if mine != placed:
        bad.append(f"roster and layout disagree: {sorted(mine ^ placed)}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    return bad


def where(nid):
    """(zone key, x, y) for a person, from whichever map lists them."""
    mod = HI if nid in HI.NPC_POSITIONS else LB
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
    # the inn keeps the mail, like every inn (qa_auction_house: a mailbox by every inn)
    box = next((r for r in ad["npcs"] if r["npc_id"] == "mailbox_hr_innkeeper"), None)
    if box is None:
        box = {"npc_id": "mailbox_hr_innkeeper"}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=zone_key(HI.NAME), x=HI.MAILBOX[0], y=HI.MAILBOX[1], facing="down",
               race="troll", appearance_variant=0, is_mailbox=True, prop="assets/tiles/market/props/mailbox_troll.png",
               greeting="Highrest's mailbox by the Cloudside Rest. Zakko's wyverns carry the letters down, and the ones that come up Lo'mai weighs down with a stone so the wind doesn't read them first.")
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    save("data/travel/travel_data.json", td)
    # safe_update only moves people, so the ones who moved maps get their zone here
    for rows, idk in ((vd["vendors"], "vendor_id"), (ad["npcs"], "npc_id")):
        for r in rows:
            if r[idk] in HI.NPC_POSITIONS:
                r["zone"] = zone_key(HI.NAME)
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    print(f"The Upper Boughs: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
