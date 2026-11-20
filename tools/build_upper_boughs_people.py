#!/usr/bin/env python3
"""The Upper Boughs' people: Highrest, the Windwardens' camp on the last shelf of wood below the cloud, and the few
trolls out on the high boughs. Idempotent.

    PYTHONPATH=. python3 tools/build_upper_boughs_people.py

docs/worldtree_brief.md. A camp, not a town: two traders, no inn, no flight path (the wind up here would take a bat
off the tree). Kyle, 14 Nov 2026: "we should start having more earth people throughout zones", more of them the
higher the zone; here, a mountaineer and meteorologist from Tromso who came up to read the weather from the top.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_upper_boughs as UB  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

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
    if mine != set(UB.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ set(UB.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    zone = zone_key(UB.NAME)
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = UB.NPC_POSITIONS[vid]
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
        x, y = UB.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    print(f"The Upper Boughs: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
