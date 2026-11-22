#!/usr/bin/env python3
"""Aurelion's people and services: the Aetherian capital. Idempotent.

    PYTHONPATH=. python3 tools/build_aurelion.py

docs/worldtree_brief.md. Kyle, 20 Nov 2026: "Aurelion must look PERFECT and grand", and "aurelion is ancient, we are
new". A capital has everything (the brief's checklist): an inn, a flight path, a bank, an auction house and mail
together at the Bridgefoot where the sky-bridge lands (Kyle, 17 Nov: "an auction house, a bank, and a mailbox close
together"), every class trained and every trade in its pair in the Trainers' Ring, shops that fit who's selling, the
Aetherians' quartermaster (its shelf is tools/build_aetherians_shelf.py), and First Speaker Aldren Sorvaine, who leads
the council of the High Houses. Ilaren Vey and Leandro Arrieta, the player's pair of allies, are waiting at the Grand
Plaza. The Aetherians wear the AE-M and AE-W sheets' looks, each picked for the job (world/race_registry.py). Transplants are factionless.

THE QUARTERMASTER CAN MOVE: au_quartermaster gives and takes no quests.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_aurelion as AU  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"au_innkeeper": ["inn"], "au_flight_master": ["flight"], "au_auctioneer": ["auction"]}
FLIGHT_NODE = ("aurelion", {"name": "Aurelion", "zone": AU.NAME, "master": "au_flight_master", "pos": [-20, 120],
                            "continent": "eastern_kingdoms"})
CLASS_TRAINER = "ct_aurelion"
TRAINERS = {
    "pt_au_forge": ["mining", "blacksmithing"],
    "pt_au_gems": ["jewelcrafting", "engineering"],
    "pt_au_hide": ["skinning", "leatherworking"],
    "pt_au_herbs": ["herbalism", "alchemy"],
    "pt_au_cloth": ["tailoring", "enchanting"],
    "pt_au_wood": ["woodcutting", "woodworking"],
    "pt_au_cook": ["cooking", "fishing"],
}
FLAGS = {"au_banker": {"is_banker": True, "sprite_scale": 2.0, "art_of": "org_banker"}}
MAILBOX = ("mailbox_au_innkeeper", (140, 220), "assets/buildings/ae_mail_pylon.png")
MOVABLE = ("au_quartermaster",)

FOOD = ["meal_saltback_roast", "hunters_brace_platter", "drink_deepwell_cordial", "cook_flour", "cook_spice",
        "cook_fruit", "cook_roots"]
GOODS = ["healing_potion_masterwork", "mana_potion_masterwork", "broadhead_arrows", "quarrel_bolts",
         "shot_mithril", "parchment", "beast_lure", "vial_crystal"]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "au_quartermaster": ("Quartermaster Bertil Arn", "aetherian", M, 28, "down", 58, True,
                         ["healing_potion_masterwork", "mana_potion_masterwork", "shot_mithril"],
                         "The council's stores. The front shelf is for any guest of the city, and what's behind me is "
                         "for the ones the High Houses have come to call friend. That takes longer than you'd think."),
    "au_provisioner": ("Provisioner Kazimir Laed", "aetherian", M, 15, "down", 58, False, FOOD,
                       "The Bridgefoot has fed everyone who's ever crossed the sky-bridge, and for most of a thousand "
                       "years that was only Aetherians. You're the first who's asked what the bread's made of."),
    "au_trader": ("Trader Stellan Varr", "aetherian", M, 11, "down", 58, True, GOODS,
                  "My family's kept this stall since the Fifth Ring had its gate. I'll sell to a ground-walker as "
                  "gladly as anyone, and I'll charge you the same as I'd charge a councillor, and that's too much."),
    "au_smith": ("Forgemaster Aurek Dannor", "aetherian", M, 10, "down", 58, True,
                 ["whetstone", "flux_strong", "coal", "kit_field_repair"],
                 "Aurelion's smiths have worked the same anvils for six hundred years. Bring me what's broken. If it's "
                 "ground steel, I'll mend it, and I'll try not to say what I think of it."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Bridgefoot
    "au_gate_warden": ("Gatewarden Tessa Vell", "aetherian", F, 2, "down",
                       "Welcome to Aurelion. The rings are older than any house in the city, so walk them gently, keep "
                       "to the bridges, and don't lean over the rails. The fall goes on longer than you'd like."),
    "au_innkeeper": ("Innkeeper Sela Arro", "aetherian", F, 10, "down",
                     "The Arro guesthouse has kept rooms on the Bridgefoot for four hundred years, and we've never had "
                     "a ground-walker sleep in one. Rest here, and I'll mark you as one of ours."),
    "au_banker": ("MerchantTusk", "troll", M, 3, "down",
                  "Dere is only one bank, mon, and dere is only one me, even way up in de sky. Do not ask how dat works. "
                  "Hand me ya things and go be a hero."),
    "au_auctioneer": ("Auctioneer Mira Dorne", "aetherian", F, 6, "down",
                      "The Exchange has set the price of crystal for a thousand years. Put your goods on the block and "
                      "the whole Horde can bid from the ground. The council takes its share, as it always has."),
    "au_flight_master": ("Skiffmaster Elian Vos", "aetherian", M, 8, "down",
                         "The skiffs fly from the Bridgefoot to every island the city still trades with, and down the "
                         "tree to the ground. They're the oldest service in Aurelion, older than the Exchange."),
    # ---- the Grand Plaza
    "au_plaza_herald": ("Herald Odric Fane", "aetherian", M, 24, "down",
                        "Every proclamation of the council for nine hundred years was first read from this plaza. The "
                        "one that opened the gates to the ground was the shortest in the record."),
    "au_ilaren": ("Ilaren Vey", "aetherian", M, 2, "left",
                  "We made it, and by the long way round, which my house will say was always the proper way. Stand "
                  "here a moment and look at it. I've lived here all my life and I still stop on this plaza."),
    "au_leandro": ("Leandro Arrieta", "human", M, 15, "right",
                   "Three years I heard about this place, and they never let us past Lenswatch. Now I'm standing in it "
                   "and the herald just bowed to me. My mother in Buenos Aires would never believe a word."),
    # ---- the Spire Palace
    "au_palace_keeper": ("Keeper of the Spire Ulmar Seyth", "aetherian", M, 26, "down",
                         "The Spire is the city's first stone. The rings were built round it, one by one, over a "
                         "thousand years. The keepers have tended it all that time, and we still don't know who raised "
                         "it."),
    # ---- the Council Ring
    "au_first_speaker": ("First Speaker Aldren Sorvaine", "aetherian", M, 12, "down",
                         "The council has argued about the ground for a hundred years. Then the seal cracked, and an "
                         "argument became a door. You're the first to walk through it, and the houses are watching to "
                         "see what we let in."),
    "au_councillor_lens": ("Councillor Thalos Wren", "aetherian", M, 17, "right",
                           "I speak for the House of the Patient Lens, the house that sent the survey down your tree. "
                           "Half the council called it a waste of crystal. They're quieter this season."),
    "au_councillor_memory": ("Councillor Idrel Marrowell", "aetherian", F, 1, "left",
                             "The House of Long Memory has always said there was more to the sky's past than the other "
                             "houses like to teach. My granddaughter found it standing up on the Golem Fields."),
    # ---- the Academies and the Gardens
    "au_academy_master": ("Master of the Academy Halvric Oune", "aetherian", M, 21, "down",
                          "The Academy has taught every magister in Aurelion for eight centuries. This year it has "
                          "students asking whether the ground has scholars, and nobody on the faculty knows the "
                          "answer."),
    "au_gardener": ("Gardener Tamsin Ashgrove", "aetherian", F, 13, "right",
                    "The Gardens were planted when the Inner Ring was laid, and some of these trees are older than the "
                    "Academy. Walk the lawns, but please don't pick the gold apples, because every one of them is counted."),
    # ---- the Ground Embassy
    "au_ambassador": ("Ambassador Tavia Morrane", "aetherian", F, 23, "down",
                      "The council opened this hall for the ground the week the seal cracked. It's the newest building "
                      "in Aurelion by about three hundred years, and you can still smell the mortar."),
    "au_embassy_aide": ("Hamid Sadeghi", "human", M, 6, "right",
                        "I was an interpreter in Tehran for twenty years, and now I interpret for the Ground Embassy. "
                        "The Aetherians have eleven words for respect and none of them mean quite the same thing."),
    # ---- the Skydocks and the North Gate
    "au_dockmaster": ("Dockmaster Garret Lune", "aetherian", M, 25, "down",
                      "The great airships put in here, the long-haulers that cross the whole sky. Fewer of them every "
                      "year, and none at all from some of the old routes."),
    "au_north_warden": ("Warden of the North Gate Orsk Talmar", "aetherian", M, 7, "down",
                        "The north gate opens on the road to the low country, the islands where the young ones learn "
                        "the sky. It's quiet out there, and the road is long."),
    # ---- the Eighth's Rest
    "au_eighth_elder": ("Elder Corrin Ashlane", "aetherian", M, 19, "down",
                        "The Eighth Ring fell in my lifetime. We were the outermost ring for nine hundred years, and "
                        "then we weren't. My nephew Teodric walked down the river to Halcyon Rest. I stayed here, with "
                        "what's left of us."),
    "au_soup_cook": ("Mother Ysolde Marsh", "aetherian", F, 14, "right",
                     "The council sends bread and the houses send coin, and the Eighth's Rest makes soup out of both. "
                     "Nobody here goes hungry, even if nobody here goes home."),
    # ---- the Trainers' Ring
    "ct_aurelion": ("Trainer Kestrin Dorrow", "aetherian", M, 22, "down",
                    "The Trainers' Ring has taught every discipline the sky knows, and now it'll teach the ground's. "
                    "Tell me what you are, and I'll show you what comes next."),
    "pt_au_forge": ("Forgewright Brannoc Dray", "aetherian", M, 9, "down",
                    "Mining and the forge. Sky-ore runs through the rings' stone, and I'll teach you to find it and to "
                    "make it into something that deserves the name."),
    "pt_au_gems": ("Crystalwright Amma Fesk", "aetherian", F, 5, "down",
                   "Jewelcrafting and engineering, which up here are nearly the same trade. Everything in this city "
                   "that moves, moves on crystal."),
    "pt_au_hide": ("Tanner Rusk Odell", "aetherian", M, 14, "down",
                   "Skinning and leatherworking. Sky-beast hide is lighter than anything on the ground and tougher "
                   "than you'd guess."),
    "pt_au_herbs": ("Herbalist Lioren Paske", "aetherian", F, 8, "down",
                    "Herbalism and alchemy. The Gardens' herbs have been grown for the Academy's alchemists for eight "
                    "hundred years, and they're very particular about who picks them."),
    "pt_au_cloth": ("Weaver Sennet Clay", "aetherian", F, 9, "down",
                    "Tailoring and enchanting. Aetherian cloth takes an enchantment the way still water takes light."),
    "pt_au_wood": ("Woodwright Garan Hesk", "aetherian", M, 27, "down",
                   "Woodcutting and woodworking. Wood is rare in the sky, so every plank in Aurelion has a history, "
                   "and I can tell you most of them."),
    "pt_au_cook": ("Cook Hamar Quill", "aetherian", M, 18, "down",
                   "Cooking and fishing. The Gardens' pool has fish that were brought up from the islands six hundred "
                   "years ago, and they've been very well fed since."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    if mine != set(AU.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ set(AU.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        if k == "au_banker":
            continue            # MerchantTusk's patois is his own (the same line at every bank)
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
        if not v[-1].isascii():
            bad.append(f"{k}: non-ASCII")
    for sid in list(TRAINERS) + [CLASS_TRAINER] + list(SERVICES):
        if sid not in AMBIENT:
            bad.append(f"{sid} has no record")
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    zone = zone_key(AU.NAME)
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        x, y = AU.NPC_POSITIONS[vid]
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
        x, y = AU.NPC_POSITIONS[nid]
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
    box.update(name="Mailbox", zone=zone, x=mx, y=my, facing="down", race="aetherian", appearance_variant=0,
               is_mailbox=True, prop=prop,
               greeting="Aurelion's mail pylon, between the inn, the bank and the Exchange. Innkeeper Sela Arro sorts "
                        "the letters, the parcels and whatever the Exchange owes you.")
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
    ae = fd["factions"].get("aetherians")
    if ae:
        ae["leader"]["npc_id"] = "au_first_speaker"
        ae["leader"]["location"] = "The Council Hall of the High Houses, on Aurelion's Council Ring"
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
    print(f"Aurelion: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people), the mail pylon, the inn, "
          f"the skiffs, the Exchange, the bank, a class trainer and {len(TRAINERS)} trade trainers")


if __name__ == "__main__":
    main()
