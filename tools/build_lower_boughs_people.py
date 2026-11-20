#!/usr/bin/env python3
"""The Lower Boughs' people: Mossroof, the trolls' village at the foot of the Great Bough, and the trolls out on the
boughs. Idempotent.

    PYTHONPATH=. python3 tools/build_lower_boughs_people.py

docs/worldtree_brief.md. The Lower Boughs get a small group of quest givers, not a town (Kyle, 19 Nov 2026: "Great
settlement will be large but not capital city large"; the city is the next stop up): two traders, no inn, no flight
path. "Transplants live here too ... a handful in the Lower Boughs who climbed for the view and stayed."

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_lower_boughs as LB  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "lb_provisioner": ("Cook Ma'tuka", "troll", F, 8, "down", 45, False,
                       ["meal_kodo_ribs", "meal_saltback_roast", "hunters_brace_platter", "drink_birch_wine",
                        "drink_deepwell_cordial", "cook_flour", "cook_spice", "cook_fruit", "cook_roots"],
                       "River fish, fruit off the boughs and a pot that's never been empty since Mossroof was built. "
                       "Eat before you go out on the branches, they're longer than they look."),
    "lb_trader": ("Trader Zekk", "goblin", M, 4, "down", 45, False,
                  ["healing_potion_mega", "mana_potion_mega", "kit_field_repair", "broadhead_arrows", "quarrel_bolts",
                   "shot_mithril", "parchment", "beast_lure", "vial_crystal"],
                  "Everything up here came up the Root Stair on somebody's back, so the prices are fair, considering. "
                  "Rope's free if you've got the nerve to use it."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "lb_elder": ("Elder Tal'vani", "troll", F, 10, "down",
                 "Mossroof was the first village we built on the tree, before anybody dreamed of a city in its heart. "
                 "The young ones go up, and I stay here, where the boughs are wide and the falls are short."),
    "lb_hunter": ("Bough-Hunter Rakaz", "troll", M, 5, "right",
                  "The apes on the west bough have been drinking the sap, and the spiders on the east have been eating "
                  "the apes. I hunt both, and I never run on a branch I haven't walked first."),
    "lb_shaman": ("Rivercaller Jinda", "troll", F, 13, "left",
                  "A river shouldn't run along a branch, but this one does, and it's never once run dry. I listen to it. "
                  "Lately it's been saying the Bloodscalp are climbing again."),
    "lb_ropemaster": ("Bridgekeeper Ozzu", "troll", M, 2, "down",
                      "Every rope and every plank between the boughs is mine to keep. If a bridge sways, that's the "
                      "wind. If it creaks, come and tell me."),
    "lb_scholar": ("Scholar Vel'jani", "troll", M, 14, "right",
                   "The scholars in the Settlement pay good silver for sky-bones, the bronze and crystal pieces that fall "
                   "out of the clouds and catch in the branches. I'm here to buy every one I can find."),
    "lb_transplant": ("Aroha Tane", "human", F, 3, "left",
                      "I climbed trees for a living back home, big kauri in the north of New Zealand. Then I heard about "
                      "this one. I came up for the view, and I'm still here."),
    "lb_stairwarden": ("Stairwarden Mozu", "troll", M, 7, "down",
                       "The Root Stair goes all the way down to the landing on Rootwater, and every step of it's been "
                       "worn smooth by somebody's feet. Mind the bottom ones, they're wet."),
    "lb_liftkeeper": ("Liftkeeper Grizzik", "goblin", M, 9, "down",
                      "Fizzle down at the landing built the little lifts. I built this one, and it goes all the way up "
                      "to the Settlement. Step on when you're ready and keep your elbows in."),
    "lb_scout_west": ("Scout Halaja", "troll", F, 11, "left",
                      "I watch the Howling Bough from here. The apes used to throw fruit at us. Now they throw each "
                      "other, and the big silverback with the gold tooth throws anything he likes."),
    "lb_scout_south": ("Scout Tiko'ra", "troll", M, 12, "down",
                       "The Bloodscalp come up the ropes at the end of the Great Bough. I've cut their ropes twice this "
                       "month, and they've tied new ones twice."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    if mine != set(LB.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ set(LB.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    zone = zone_key(LB.NAME)
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = LB.NPC_POSITIONS[vid]
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
        x, y = LB.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    print(f"The Lower Boughs: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
