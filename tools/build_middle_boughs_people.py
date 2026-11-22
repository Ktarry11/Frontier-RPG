#!/usr/bin/env python3
"""The Middle Boughs' people: Heartwatch, the shadow hunters' stone outpost on the first climbers' terraces, and the
trolls out on the boughs. Idempotent.

    PYTHONPATH=. python3 tools/build_middle_boughs_people.py

docs/worldtree_brief.md. Heartwatch was a handful of givers on the outpost platform; since 22 Nov 2026 it's its own map
and the tier's hub (Kyle: "we do need hubs in the boughs"), with an inn, the mail and the bats
(tools/handbuilt_worldtree_heartwatch.py). The lift and the two scouts stay out where their work is. Kyle, 14 Nov 2026: "we should start having more earth people throughout zones", more of them the higher
the zone; here, a plant pathologist from Bengaluru who came up to study the rot.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_middle_boughs as LB  # noqa: E402
from tools import handbuilt_worldtree_heartwatch as HW  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"hw_bat_handler": ["flight"], "hw_innkeeper": ["inn"]}
FLIGHT_NODES = [
    ("middle_boughs", {"name": HW.NAME, "zone": HW.NAME, "master": "hw_bat_handler", "pos": [-36, 143],
                      "continent": "eastern_kingdoms"}),
]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "mb_provisioner": ("Provisioner Kezza", "troll", F, 6, "down", 46, False,
                       ["meal_kodo_ribs", "meal_saltback_roast", "hunters_brace_platter", "drink_birch_wine",
                        "drink_deepwell_cordial", "cook_flour", "cook_spice", "cook_fruit", "cook_roots"],
                       "Everything I cook came up the High Lift this morning, so it's as fresh as it gets this high. "
                       "Eat something warm before you go out, the wind on the boughs bites."),
    "mb_trader": ("Trader Vin'jo", "troll", M, 9, "down", 46, False,
                  ["healing_potion_mega", "mana_potion_mega", "kit_field_repair", "broadhead_arrows", "quarrel_bolts",
                   "shot_mithril", "parchment", "beast_lure", "vial_crystal"],
                  "Arrows, potions and rope, and I'll buy whatever you drag back off the boughs. Don't bring me "
                  "anything from the rot, though, because it stains everything it touches."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "hw_innkeeper": ("Innkeeper Rozha", "troll", F, 5, "down",
                     "The Lichen Hearth keeps a fire going day and night, because the cold up here gets into the stone. "
                     "Sleep by it and I'll mark you as one of mine, so the tree brings you back to Heartwatch."),
    "hw_bat_handler": ("Bat Handler Tez'ra", "troll", F, 3, "down",
                       "My bats fly down to the Settlement and out to every roost the Horde keeps. They don't like the "
                       "mist under the boughs, so they climb high and fast, and you'll want to hold on."),
    "mb_shadowhunter": ("Shadow Hunter Vokra", "troll", F, 12, "down",
                        "Heartwatch watches one thing, and it's the split in the trunk behind me. Something down in "
                        "the heartwood is eating this tree, and until we know what, nobody goes in and nothing comes "
                        "out."),
    "mb_loa_speaker": ("Loa-Speaker Ganjo", "troll", M, 3, "left",
                       "I listen to the tree for the tribes. It used to sing. Now it groans at night, low and long, the "
                       "way a sick man does when he thinks nobody's listening."),
    "mb_bark_doctor": ("Bark-Doctor Ezzi", "troll", F, 7, "right",
                       "The rot starts as a soft spot you can push your thumb into, and a month later you can push your "
                       "whole arm in. I cut it out where I can. I can't cut out a whole bough."),
    "mb_huntmaster": ("Huntmaster Raz'gul", "troll", M, 11, "down",
                      "The harpies came up from the coast when the world broke and found the hollows in the bark. "
                      "They've been fattening on the rot's grubs ever since, and they've got bold."),
    "mb_stonekeeper": ("Stonekeeper Jo'than", "troll", M, 1, "down",
                       "The first climbers built these terraces, stone carried up a tree, block by block. Nobody "
                       "remembers how. I keep them swept and I keep their names, and that's my whole job."),
    "mb_scholar": ("Scholar Nyara", "troll", F, 4, "left",
                   "Tel'zan sent me up from the Settlement after the thing on the Lichen Reach. It fell out of the "
                   "clouds a month ago and it hasn't stopped moving. I'd like to know what it's for before it "
                   "finishes whatever it's doing."),
    "mb_transplant": ("Dr. Priya Raman", "human", F, 5, "right",
                      "I'm a plant pathologist from Bengaluru, and this is the biggest sick patient I've ever had. The "
                      "rot behaves like a fungus I know from home, except that it's hungry in a way fungi shouldn't be."),
    "mb_liftkeeper": ("Ropehand Dezza", "troll", F, 8, "down",
                      "Tagu works the bottom of the High Lift and I work the top, and we shout at each other all day. "
                      "Step on when you're ready to go back down to the city."),
    "mb_scout_reach": ("Scout Mahu", "troll", M, 10, "right",
                       "Something out at the end of the Reach fell out of the sky, and it's still twitching. Little "
                       "metal things keep crawling out of it. I count them every morning, and there's more every day."),
    "mb_scout_hollows": ("Scout Ree'na", "troll", F, 13, "down",
                         "The harpies roost in the hollows on the south bough, and their matron keeps a nest inside the "
                         "trunk itself. I've heard her screaming from in there, and it carries all the way to Heartwatch."),
}

def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    placed = set(LB.NPC_POSITIONS) | set(HW.NPC_POSITIONS)
    if set(LB.NPC_POSITIONS) & set(HW.NPC_POSITIONS):
        bad.append(f"on both maps: {sorted(set(LB.NPC_POSITIONS) & set(HW.NPC_POSITIONS))}")
    if mine != placed:
        bad.append(f"roster and layout disagree: {sorted(mine ^ placed)}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    return bad


def where(nid):
    """(zone key, x, y) for a person, from whichever map lists them."""
    mod = HW if nid in HW.NPC_POSITIONS else LB
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
    box = next((r for r in ad["npcs"] if r["npc_id"] == "mailbox_hw_innkeeper"), None)
    if box is None:
        box = {"npc_id": "mailbox_hw_innkeeper"}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=zone_key(HW.NAME), x=HW.MAILBOX[0], y=HW.MAILBOX[1], facing="down",
               race="troll", appearance_variant=0, is_mailbox=True, prop="assets/tiles/market/props/mailbox_troll.png",
               greeting="Heartwatch's mailbox by the Lichen Hearth. The bats carry the letters down to the Settlement in the morning, and Rozha keeps what comes back up dry by her fire.")
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
            if r[idk] in HW.NPC_POSITIONS:
                r["zone"] = zone_key(HW.NAME)
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    print(f"The Middle Boughs: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
