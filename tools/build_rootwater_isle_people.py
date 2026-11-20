#!/usr/bin/env python3
"""Rootwater Isle's people, and the Highbough Tribes (the World Tree's faction). Idempotent.

    PYTHONPATH=. python3 tools/build_rootwater_isle_people.py

docs/worldtree_brief.md. Kyle, 19 Nov 2026: the tree's town and faction are the trolls' ("Trolls town"), the island is
42-44, and Rootwater Isle is a landing with quest givers, not a town: no inn or flight path here (the Great Settlement,
up the tree, has those). Two boatmen run the boats, one to Grom'gol and one to Zoram Strand.

THE FACTION comes first, so the island's quests can pay it. Its shelf, quartermaster and leader's NPC come with the
Great Settlement; until then High Chieftain Zan'kaji is named and not linked (tools/qa_factions.py allows that).

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_rootwater_isle as RW  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "rw_provisioner": ("Provisioner Mojo'tu", "troll", M, 6, "down", 43, False,
                       ["meal_kodo_ribs", "meal_saltback_roast", "hunters_brace_platter", "drink_birch_wine",
                        "drink_deepwell_cordial", "cook_flour", "cook_spice", "cook_fruit", "cook_roots"],
                       "Fish from the lagoons, fruit off the low branches, and a stew that's been going since the "
                       "landing was built. Nobody climbs the tree hungry, mon."),
    "rw_outfitter": ("Trader Sen'kaa", "troll", F, 9, "down", 43, False,
                     ["healing_potion_mega", "mana_potion_mega", "kit_field_repair", "broadhead_arrows", "quarrel_bolts",
                      "shot_mithril", "parchment", "beast_lure", "vial_crystal"],
                     "Everything that comes up the boats from Grom'gol or Zoram goes through my hands first. What "
                     "you need for the climb, I've got."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    "rw_chieftain": ("Headwoman Zula Rootcaller", "troll", F, 12, "down",
                     "Welcome to Rootwater, where the tree drinks the sea. The High Chieftain sits up in the "
                     "Settlement, and down here at the roots it's me. If you're going up, I'll want your help first."),
    "rw_witch_doctor": ("Witch Doctor Tazjin", "troll", M, 4, "right",
                        "The loa of this tree never had a name before we gave it one. It answered us when nothing "
                        "else did, and I listen for it every night. Lately it's been hungry."),
    "rw_hunter": ("Huntress Ka'lisa", "troll", F, 7, "left",
                  "Everything that drinks the sap grows. The crocolisks in the lagoons are twice the size they were "
                  "last year, and they've stopped being afraid of us."),
    "rw_dockhand": ("Fizzle Brasswinch", "goblin", M, 11, "down",
                    "I built every lift on this tree, and the trolls paid me in sap. Best deal I ever made, until the "
                    "Bloodsail figured out what it's worth."),
    "rw_herbalist": ("Sapwatcher Uzo", "troll", M, 15, "down",
                     "The sap is the tree's blood. A little heals a cut, a cup makes a man strong, and a barrel makes "
                     "a beast into something else. I measure it, so somebody has to."),
    "rw_settler": ("Marta Kowalczyk", "human", F, 1, "left",
                   "I came over on the Zoram boat to see the tree everyone was talking about, and I never got back on. "
                   "The trolls let me stay if I work, so I work."),
    "rw_ferryman_east": ("Boatman Grik'zul", "troll", M, 3, "right",
                         "Grom'gol's across the water, a short pull with a good tide. Step in when you're ready and "
                         "keep your hands inside, the crocolisks have gotten bold."),
    "rw_ferryman_west": ("Boatwoman Zaela", "troll", F, 5, "left",
                         "This boat goes all the way across to Zoram Strand, on the night elves' coast. It's a long "
                         "row, and the Sentinels there have gotten used to trolls turning up."),
    "rw_scout_lagoons": ("Scout Jinzo", "troll", M, 9, "down",
                         "I watch the lagoons for the Rootmaw. It's the oldest croc on the island, and it's been "
                         "drinking from the roots since the first day. Don't swim out there alone."),
}

FACTION_ID = "highbough_tribes"
FACTION = {
    "name": "The Highbough Tribes",
    "description": "The trolls who climbed the World Tree and made it their home, from the landing at its roots to the "
                   "Great Settlement in its heart.",
    "home_zone": "the_great_settlement",
    "home_name": "The Great Settlement, in the heart of the World Tree",
    "leader": {"title": "High Chieftain", "name": "Zan'kaji",
               "location": "The Great Settlement, in the heart of the World Tree",
               "line": "The tree answered us when the world broke. We climbed it, and we'll keep it. Help us and "
                       "you're one of the tribes."},
    "_lore_note": "Kyle, 19 Nov 2026: the World Tree's town and faction are the trolls'. docs/worldtree_brief.md.",
    "lore": [
        "Three years ago a seed split the reef off Stranglethorn's west coast, and the tree that came out of it has "
        "never stopped growing. Its roots drink the sea, its branches carry whole villages, and its crown has gone "
        "up through the clouds.",
        "Stranglethorn's trolls, squeezed between Grom'gol, the Bloodsail and their own feuding tribes, were the "
        "first to climb it. Darkspear kin and the tribes who'd broken with the Gurubashi feuds, with a few Skullsplitter "
        "and Bloodscalp who turned their backs on their own, built a landing at its roots and a city in its heart.",
        "They call the tree a loa that answered them when nothing else would. The Highbough Tribes hold it now, "
        "allied to the Horde without answering to it, and they remember who helps them keep it.",
    ],
    "quest_rep": {"_comment": "Per quest, paid by giver (tools/build_rootwater_isle_quests.py).", "default": 200,
                  "boss": 250, "capstones": {}, "zones": [], "also": []},
    "rewards": {"vendor_stock": {}, "_comment": "The shelf comes with the Great Settlement's quartermaster.",
                "quests": {}},
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    if mine != set(RW.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ set(RW.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    fd = load("data/factions/factions.json")
    if FACTION_ID in fd["factions"]:
        keep = fd["factions"][FACTION_ID]
        keep.update({k: v for k, v in FACTION.items() if k not in ("quest_rep", "rewards")})
    else:
        fd["factions"][FACTION_ID] = FACTION
    save("data/factions/factions.json", fd)

    zone = zone_key(RW.NAME)
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = RW.NPC_POSITIONS[vid]
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
        x, y = RW.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    print(f"Rootwater Isle: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people); "
          f"faction {FACTION_ID}")


if __name__ == "__main__":
    main()
