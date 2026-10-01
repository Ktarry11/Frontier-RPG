"""
Quest variety pass for Durotar/Razor Hill (Kyle: "ensure quest variation
in durotar" - both quest files were 11/12 kill or kill_boss objectives)
plus a new troll refugee NPC in Razor Hill sending the player to Echo
Isles (Kyle: "troll refuge in razor-hill to echo isles giving a quest to
help his people").

Kyle's explicit rule this pass: no quests built around rare (count:0)
spawns - Bloodtalon Scythemaw and Southfury Crocolisk (Durotar's Red
Wastes rares) are deliberately NOT used anywhere below, only the common
(count>=1) creatures.

NEW QUESTS (all genuinely non-kill-count, added rather than retrofitted
onto existing chains per Kyle's "just add additional quests" call):
1. durotar_vulture_feathers (GATHER) - open Red Wastes, goblin-flavored
   trade-goods framing via Gazlowe's Cousin Fitz (already placed,
   durotar_goblin_prospector).
2. durotar_prowler_den (EXPLORE, position-gated) - scouting a prowler
   den before Razor Hill sends fighters after it, via Borka the
   Watchful (already placed, durotar_rocktusk_scout).
3. razorhill_supply_run (FETCH) - recovering salvage from Kravel's own
   caravan losses, tying back into his established Kolkar Crag
   storyline without repeating it.
4. razorhill_troll_refuge (EXPLORE bridge quest) - new NPC Tal'rashi, a
   Darkspear refugee who reached Razor Hill before the camp at Echo
   Isles fully formed, sends the player to check on his people (Elder
   Kang'ari specifically, position-gated).

Run once. Adds 1 NPC to ambient_npcs.json, registers 2 new quest drops,
adds 2 quests to durotar.json and 2 to razor_hill.json.
"""
import json

NEW_NPC = {
    "npc_id": "razorhill_troll_refugee", "name": "Tal'rashi", "zone": "razor_hill",
    "x": 42, "y": 28, "race": "troll", "gender": "male", "appearance_variant": 6, "facing": "down",
    "greeting": "I made it dis far. Not everyone did. Not everyone still trapped out dere will, either."
}

DUROTAR_QUESTS = [
    {
        "quest_id": "durotar_vulture_feathers",
        "title": "Feathers for the Ledger",
        "description": (
            "Gazlowe's Cousin Fitz has a buyer back in Orgrimmar who "
            "pays well for sunbaked vulture feathers - something about "
            "fletching contracts, though Fitz admits he's never actually "
            "asked what they're for. He just knows the going rate, and "
            "the going rate is good enough that he's willing to pay a "
            "finder's cut to anyone willing to brave the Red Wastes and "
            "actually collect them."
        ),
        "giver_npc_id": "durotar_goblin_prospector",
        "zone": "durotar",
        "objectives": [
            {
                "type": "gather",
                "target": "sunbaked_vulture_feather",
                "count": 8
            }
        ],
        "reward_exp": 340,
        "reward_gold": 1400,
        "accept_text": (
            "Eight feathers, good condition, no scorch marks - the "
            "buyer's picky about scorch marks for some reason I've "
            "genuinely never asked about. Just bring me eight and I'll "
            "cut you in fair."
        ),
        "turn_in_text": (
            "Perfect condition, all eight. I don't know what a fletcher "
            "in Orgrimmar wants with this many vulture feathers and "
            "honestly at this point I've stopped wondering. Here's your "
            "cut."
        ),
        "next_quest_id": None,
        "level_min": 5,
        "level_max": 8
    },
    {
        "quest_id": "durotar_prowler_den",
        "title": "Scouting the Prowler Den",
        "description": (
            "Borka the Watchful has noticed the Durotar prowlers "
            "denning closer to the road than usual, and he'd rather know "
            "exactly where before Razor Hill sends anyone in after them "
            "properly. He's not asking for a fight yet - just eyes on "
            "the den itself, confirmed and reported back."
        ),
        "giver_npc_id": "durotar_rocktusk_scout",
        "zone": "durotar",
        "objectives": [
            {
                "type": "explore",
                "target": "durotar",
                "target_x": 48,
                "target_y": 72,
                "radius": 8
            }
        ],
        "reward_exp": 260,
        "reward_gold": 850,
        "accept_text": (
            "Southwest of here, past the ridge. Get close enough to "
            "confirm the den and get out. I'd rather have a live scout "
            "with an answer than a dead hero with a guess."
        ),
        "turn_in_text": (
            "Good. Now we actually know where they've dug in instead of "
            "guessing from droppings and torn-up ground. That's worth "
            "more to me than another dead prowler would've been."
        ),
        "next_quest_id": None,
        "level_min": 5,
        "level_max": 8
    }
]

RAZOR_HILL_QUESTS = [
    {
        "quest_id": "razorhill_supply_run",
        "title": "What the Kolkar Left Behind",
        "description": (
            "Kravel Coinsnatch is still tallying losses from before the "
            "Kolkar centaur got dealt with, and there's salvageable cargo "
            "scattered along the old caravan route that never got "
            "recovered - crates, bolts of cloth, the kind of thing that's "
            "worth real money if someone bothers to go collect it before "
            "it rots or gets picked over by scavengers."
        ),
        "giver_npc_id": "razorhill_goblin_trader",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "fetch",
                "target": "salvaged_caravan_crate",
                "count": 5
            }
        ],
        "reward_exp": 300,
        "reward_gold": 1600,
        "accept_text": (
            "Five crates, wherever you find them along the western "
            "route. I'm not proud of how long I let this sit unclaimed - "
            "let's just say I've been busy - but money left on the "
            "ground is still money, and I'd rather it be mine."
        ),
        "turn_in_text": (
            "Five crates of pure profit I'd already written off. This is "
            "exactly the kind of margin that makes a bad week into a "
            "good one. Pleasure doing business, genuinely."
        ),
        "next_quest_id": None,
        "level_min": 6,
        "level_max": 9
    },
    {
        "quest_id": "razorhill_troll_refuge",
        "title": "Word From the Isles",
        "description": (
            "Tal'rashi reached Razor Hill before the Darkspear camp at "
            "Echo Isles had fully taken shape, and he's carried the guilt "
            "of that timing ever since - kin still lost to Zalazane's "
            "hex while he found relatively safe ground on the mainland. "
            "He can't go back himself; an old injury from the crossing "
            "never healed right. But he can point someone capable toward "
            "the isles, and ask them to check on his people the way he "
            "no longer can himself."
        ),
        "giver_npc_id": "razorhill_troll_refugee",
        "zone": "razor_hill",
        "objectives": [
            {
                "type": "explore",
                "target": "echo_isles",
                "target_x": 70,
                "target_y": 52,
                "radius": 8
            }
        ],
        "reward_exp": 320,
        "reward_gold": 1000,
        "accept_text": (
            "Find Elder Kang'ari at da camp on Echo Isles. Tell him "
            "Tal'rashi still thinks about dem every day. Dat's all I "
            "can send in my place - words, and hope dey're worth "
            "somethin' when dey arrive."
        ),
        "turn_in_text": (
            "You found dem. You actually found dem, and dey're still "
            "standin'. I don't got da words for what dat means to hear, "
            "mon. Whatever's happenin' out dere now, at least I know "
            "dey're not alone in it anymore."
        ),
        "next_quest_id": None,
        "level_min": 5,
        "level_max": 9
    }
]


def main():
    npc_path = "data/npcs/ambient_npcs.json"
    npc_data = json.load(open(npc_path))
    if not any(n["npc_id"] == NEW_NPC["npc_id"] for n in npc_data["npcs"]):
        npc_data["npcs"].append(NEW_NPC)
        json.dump(npc_data, open(npc_path, "w"), indent=2)
        print(f"Added NPC: {NEW_NPC['name']} ({NEW_NPC['npc_id']})")

    qd_path = "data/creatures/quest_drops.json"
    qd_data = json.load(open(qd_path))
    if "Sunbaked Vulture" not in qd_data["drops"]:
        qd_data["drops"]["Sunbaked Vulture"] = []
    qd_data["drops"]["Sunbaked Vulture"].append({
        "item_id": "sunbaked_vulture_feather",
        "name": "Sunbaked Vulture Feather",
        "category": "quest",
        "description": "A long, sun-bleached feather, remarkably free of scorch marks.",
        "chance": 0.55
    })
    if "Kolkar Raider" not in qd_data["drops"]:
        qd_data["drops"]["Kolkar Raider"] = []
    qd_data["drops"]["Kolkar Raider"].append({
        "item_id": "salvaged_caravan_crate",
        "name": "Salvaged Caravan Crate",
        "category": "quest",
        "description": "A battered supply crate, contents mostly intact despite everything.",
        "chance": 0.4
    })
    json.dump(qd_data, open(qd_path, "w"), indent=2)
    print("Registered sunbaked_vulture_feather and salvaged_caravan_crate quest drops")

    dur_path = "data/quests/durotar.json"
    dur_data = json.load(open(dur_path))
    existing = {q["quest_id"] for q in dur_data["quests"]}
    added_dur = []
    for q in DUROTAR_QUESTS:
        if q["quest_id"] in existing:
            continue
        dur_data["quests"].append(q)
        added_dur.append(q["quest_id"])
    json.dump(dur_data, open(dur_path, "w"), indent=2)
    print(f"Added {len(added_dur)} quests to durotar.json: {added_dur}")

    rh_path = "data/quests/razor_hill.json"
    rh_data = json.load(open(rh_path))
    existing2 = {q["quest_id"] for q in rh_data["quests"]}
    added_rh = []
    for q in RAZOR_HILL_QUESTS:
        if q["quest_id"] in existing2:
            continue
        rh_data["quests"].append(q)
        added_rh.append(q["quest_id"])
    json.dump(rh_data, open(rh_path, "w"), indent=2)
    print(f"Added {len(added_rh)} quests to razor_hill.json: {added_rh}")


if __name__ == "__main__":
    main()
