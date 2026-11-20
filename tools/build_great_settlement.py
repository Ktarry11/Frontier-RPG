#!/usr/bin/env python3
"""The Great Settlement's people and services: the Highbough Tribes' city in the heart of the World Tree. Idempotent.

    PYTHONPATH=. python3 tools/build_great_settlement.py

docs/worldtree_brief.md. Kyle, 19 Nov 2026: the tree's town is the trolls', "a massive central city in the middle of
it", and "Great settlement will be large but not capital city large". So it has what a town needs and what a city has
(the brief's checklist): an inn, a flight path (the bat roost), a bank, an auction house and mail together (Kyle, 17 Nov:
"an auction house, a bank, and a mailbox close together"), one class trainer, the trades in their pairs, level-right
shops that fit who's selling, the Highbough quartermaster, and High Chieftain Zan'kaji. Transplants trade in the
market ("more in the city's markets").

THE QUARTERMASTER CAN MOVE. gs_quartermaster gives and takes no quests, so the shelf can be moved without touching a
quest. Its shelf is tools/build_highbough_tribes.py.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_great_settlement as GS  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"gs_innkeeper": ["inn"], "gs_flight_master": ["flight"], "gs_auctioneer": ["auction"]}
FLIGHT_NODE = ("great_settlement", {"name": "The Great Settlement", "zone": GS.NAME, "master": "gs_flight_master",
                                    "pos": [-34, 146], "continent": "eastern_kingdoms"})
CLASS_TRAINER = "ct_great_settlement"
TRAINERS = {
    "pt_gs_forge": ["mining", "blacksmithing"],
    "pt_gs_gems": ["jewelcrafting", "engineering"],
    "pt_gs_hide": ["skinning", "leatherworking"],
    "pt_gs_herbs": ["herbalism", "alchemy"],
    "pt_gs_cloth": ["tailoring", "enchanting"],
    "pt_gs_wood": ["woodcutting", "woodworking"],
    "pt_gs_cook": ["cooking", "fishing"],
}
FLAGS = {"gs_banker": {"is_banker": True, "sprite_scale": 2.0}}
MAILBOX = ("mailbox_gs_innkeeper", (95, 85), "assets/tiles/market/props/mailbox_troll.png")
MOVABLE = ("gs_quartermaster",)

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "gs_quartermaster": ("Quartermaster Rak'tala", "troll", F, 6, "down", 46, True,
                         ["kit_field_repair", "healing_potion_mega", "mana_potion_mega", "shot_mithril"],
                         "The tribes' stores. What's on the front shelf is for anybody, and what's behind me is for "
                         "the ones the tribes call friend. Help us keep the tree and we'll talk."),
    "gs_provisioner": ("Provisioner Juno'ka", "troll", F, 3, "down", 46, False,
                       ["meal_kodo_ribs", "meal_saltback_roast", "hunters_brace_platter", "drink_birch_wine",
                        "drink_deepwell_cordial", "cook_flour", "cook_spice", "cook_fruit", "cook_roots"],
                       "Fish from the falls pool, fruit from every tier and bread from ovens that never go out. "
                       "Nobody in the Settlement goes hungry, mon, not while I'm here."),
    "gs_trader": ("Trader Nizzle", "goblin", M, 7, "down", 46, False,
                  ["parchment", "beast_lure", "vial_crystal", "broadhead_arrows", "quarrel_bolts", "shot_mithril",
                   "kit_field_repair"],
                  "Everything in this city came up a lift, so everything in this city costs a little more. That's "
                  "not greed, friend, that's gravity."),
    "gs_smith": ("Forgemaster Togar", "troll", M, 8, "down", 46, True,
                 ["whetstone", "flux_strong", "coal", "kit_field_repair", "bs_mithril_shield"],
                 "The forge burns hotter up here, closer to the sky. Bring me what's broken, or buy what isn't, "
                 "and don't touch the anvil while it's ringing."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Chieftain's Rise
    "gs_zankaji": ("High Chieftain Zan'kaji", "troll", M, 14, "down",
                   "The tree answered us when the world broke. We climbed it, and we'll keep it. Help us and you're "
                   "one of the tribes, whatever you were born."),
    "gs_loa_priest": ("Loa-Speaker Vashi", "troll", F, 9, "down",
                      "This temple is the loa's ear. Every tribe that climbed the tree left something at its feet, and "
                      "the tree remembers every one of them."),
    "gs_orc_envoy": ("Envoy Grukk Ironjaw", "orc", M, 5, "left",
                     "Orgrimmar sent me to ask the High Chieftain to call the tree Horde ground. He gave me a room, a "
                     "view and a very long wait. I'm starting to like the view."),
    # ---- the Liftfoot and the High Lift
    "gs_liftkeeper": ("Liftwarden Ozenna", "troll", F, 4, "down",
                      "The Great Lift goes down to Mossroof and the Lower Boughs. Grizzik built it and I keep it, which "
                      "means I'm the one he shouts at when it squeaks."),
    "gs_gate_guard": ("Gatewarden Krosh'ta", "troll", M, 11, "down",
                      "Welcome to the Great Settlement. Keep your weapons sheathed, keep to the bridges, and don't lean "
                      "over the rails, it's a long way down to Mossroof."),
    "gs_highlift_keeper": ("Liftwarden Tagu", "troll", M, 6, "down",
                           "The High Lift goes on up to the Middle Boughs, where the old shrines are. The air's colder "
                           "up there, and the bark isn't as healthy as it ought to be."),
    # ---- the Market
    "gs_innkeeper": ("Innkeeper Ma'kali", "troll", F, 2, "down",
                     "Beds upstairs, stew down here, and the best view in the tree from the back balcony. Rest a while "
                     "and I'll mark you as one of mine."),
    "gs_banker": ("MerchantTusk", "troll", M, 3, "down",
                  "Dere is only one bank, mon, and dere is only one me, even way up in a tree. Do not ask how dat works. "
                  "Hand me ya things and go be a hero."),
    "gs_auctioneer": ("Auctioneer Kezzik Boltbelly", "goblin", M, 5, "down",
                      "Put it on the block and the whole Horde can bid, even from down on the ground. The house takes "
                      "its cut, the lift takes its cut, and you get what's left."),
    "gs_scholar": ("Scholar Yenvaa", "troll", F, 12, "right",
                   "Every piece on this wall fell out of the clouds. Bronze, crystal, gears finer than any goblin "
                   "makes. Somebody up there's losing a great deal of something."),
    "gs_transplant_a": ("Kofi Mensah", "human", M, 2, "down",
                        "I ran a stall at Makola Market in Accra, back home, before the merge. A market's a market, "
                        "whether the customers have tusks or not. These ones haggle better."),
    "gs_transplant_b": ("Hana Sato", "human", F, 1, "down",
                        "My family kept a tea house in Kyoto for four generations. The trolls had never had green tea "
                        "until I came. Now half the Settlement starts the day here."),
    # ---- the Trades Terrace
    "ct_great_settlement": ("Trainer Zal'jin", "troll", M, 10, "down",
                            "Warrior, healer, hunter or something stranger, the tribes take everybody. Tell me what "
                            "you are and I'll show you what comes next."),
    "pt_gs_forge": ("Forgehand Bok'ra", "troll", M, 13, "down",
                    "Mining and the forge. The ore comes up from the stones caught in the boughs, and I teach you to "
                    "find it and to make it into something."),
    "pt_gs_gems": ("Tinkerer Sprazzle", "goblin", F, 3, "down",
                   "Gems and gadgets, jewelcrafting and engineering. The sky keeps dropping parts on us, and somebody "
                   "has to learn what to do with them."),
    "pt_gs_hide": ("Hidewright Sen'jo", "troll", M, 7, "down",
                   "Skinning and leatherworking. Python skin, ape hide and the odd spider's carapace, it all comes "
                   "through my hands before it goes on somebody's back."),
    "pt_gs_herbs": ("Brewer Ya'tali", "troll", F, 5, "down",
                    "Herbalism and alchemy. Half of what grows on the tree doesn't grow anywhere else, and the other "
                    "half grows faster here than it should."),
    "pt_gs_cloth": ("Weaver Mazala", "troll", F, 8, "down",
                    "Tailoring and enchanting. The silk from the Silkwood takes an enchantment better than any cloth "
                    "I've ever worked."),
    "pt_gs_wood": ("Carver Hekta", "troll", M, 4, "down",
                   "Woodcutting and woodworking. We never cut the living tree, only what it drops, and it drops a "
                   "great deal."),
    "pt_gs_cook": ("Cook Tum'bo", "troll", M, 9, "down",
                   "Cooking and fishing. The falls pool has fish nobody can name, and every one of them is good in a "
                   "stew."),
    # ---- the Lantern Ward
    "gs_ward_elder": ("Grandmother Ozai", "troll", F, 15, "down",
                      "I was the first to sleep in this ward, when it was three huts and a rope. Now look at it. The "
                      "young ones don't remember the jungle, and I'm glad."),
    "gs_ward_child": ("Lamplighter Jinto", "troll", M, 1, "down",
                      "I light every lantern in the ward at dusk, and I've never missed one. Grandmother Ozai says if "
                      "one goes out, the loa can't find its way home."),
    "gs_ward_weaver": ("Weaver Kesha", "troll", F, 6, "right",
                       "The streamers on the Rise are mine, every one, and so are half the awnings in the market. "
                       "Red for the tribes, teal for the tree, gold for the loa."),
    # ---- the Roost
    "gs_flight_master": ("Bat Handler Ruzkah", "troll", F, 7, "down",
                         "The bats fly down to Grom'gol and out across the Horde's roads. They don't like the dark "
                         "under the tree, so they fly fast, and you'll want to hold on."),
    "gs_scholar_hall": ("Archivist Tel'zan", "troll", M, 12, "down",
                        "The scholars' hall keeps a record of everything that's fallen from the sky. The record gets "
                        "longer every week, and the pieces get bigger."),
    # ---- the Falls
    "gs_falls_keeper": ("Watersinger Ya'nela", "troll", F, 10, "right",
                        "The water falls from a branch so high nobody's climbed to it. It's never stopped, not once, "
                        "and it tastes a little sweet, like sap."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    if mine != set(GS.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ set(GS.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        if k == "gs_banker":
            continue            # MerchantTusk's patois is his own (the same line at every bank)
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    for sid in list(TRAINERS) + [CLASS_TRAINER] + list(SERVICES):
        if sid not in AMBIENT:
            bad.append(f"{sid} has no record")
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    zone = zone_key(GS.NAME)
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = GS.NPC_POSITIONS[vid]
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
        x, y = GS.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone, x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        rec.update(FLAGS.get(nid, {}))
        if nid == CLASS_TRAINER:
            rec["trains_class"] = "*"
        if nid in TRAINERS:
            rec["trains_profession"] = list(TRAINERS[nid])
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    mid, (mx, my), prop = MAILBOX
    box = next((r for r in ad["npcs"] if r["npc_id"] == mid), None)
    if box is None:
        box = {"npc_id": mid}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=zone, x=mx, y=my, facing="down", race="troll", appearance_variant=0,
               is_mailbox=True, prop=prop,
               greeting="The Settlement's mailbox, between the bank and the auction hall. Innkeeper Ma'kali sorts "
                        "the letters, the parcels and whatever the auction hall owes you.")
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)

    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    td["flight_nodes"][FLIGHT_NODE[0]] = FLIGHT_NODE[1]
    save("data/travel/travel_data.json", td)
    tr = load("data/training/trainers.json")
    tr["class_trainers"].setdefault(CLASS_TRAINER, "*")
    for k, v in TRAINERS.items():
        tr["profession_trainers"][k] = list(v)
    (ROOT / "data/training/trainers.json").write_text(json.dumps(tr, indent=2) + "\n", encoding="utf-8")

    # the leader is a person now
    fd = load("data/factions/factions.json")
    hb = fd["factions"].get("highbough_tribes")
    if hb:
        hb["leader"]["npc_id"] = "gs_zankaji"
        hb["leader"]["location"] = "The Heart Palace, on the Chieftain's Rise in the Great Settlement"
        save("data/factions/factions.json", fd)

    tied = []
    for qf in sorted((ROOT / "data/quests").glob("*.json")):
        d = json.loads(qf.read_text(encoding="utf-8"))
        for q in d.get("quests", []) if isinstance(d, dict) else []:
            for k in ("giver_npc_id", "turn_in_npc_id"):
                if q.get(k) in MOVABLE:
                    tied.append(f"{qf.name}: {q.get('quest_id')} {k}={q.get(k)}")
    if tied:
        raise SystemExit("the movable quartermaster is tied to quests:\n  " + "\n  ".join(tied))
    print(f"The Great Settlement: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people), the mailbox, "
          f"the inn, the bat roost, the auction hall, the bank, a class trainer and {len(TRAINERS)} trade trainers")


if __name__ == "__main__":
    main()
