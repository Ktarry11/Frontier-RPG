#!/usr/bin/env python3
"""The Sunward Crown's people and Lenswatch's: the first place the ground, the sky and the Earth people stand together
(docs/worldtree_brief.md, "Twenty questions"). Idempotent.

    PYTHONPATH=. python3 tools/build_sunward_crown_people.py

Kyle, 20 Nov 2026: the Ascendancy crashed the parley and each side thinks the other set it up; the trolls want war and
Orgrimmar's envoy is trying to stop it; the scholar houses are split, and the House of the Patient Lens (the survey)
is the one that respects the ground; the Earth people the Aetherians found on the sky islands are the survey's guests,
"something to study, smart", and most of them respect the Aetherians for something; the player rests in the survey's
camp; and the player's allies through the whole sky are a pair who don't fully trust each other, a scholar of the
Patient Lens (Ilaren Vey, at the Parley Stones) and an Earthborn who's lived three years with the Aetherians (Matias
Arrieta, at the Annex).

THE RULES IT KEEPS. Transplants are factionless. The Aetherians hunt for what the Integration was and never get close to
its cause: nobody here says anything about it but that they don't know. Lenswatch is a town, so it has the inn and the
Crown's one flight path; the Crown itself has camps. Aetherian NPCs are men for now (only the men are drawn: P6).

Every person stands where their map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_lenswatch as LW  # noqa: E402
from tools import handbuilt_worldtree_sunward_crown as SC  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"
MAPS = {"crown": SC, "lens": LW}

SERVICES = {"lw_innkeeper": ["inn"], "lw_skiffmaster": ["flight"]}
FLIGHT_NODES = [
    ("lenswatch", {"name": "Lenswatch", "zone": LW.NAME, "master": "lw_skiffmaster", "pos": [-30, 140],
                   "continent": "eastern_kingdoms"}),
]

FOOD = ["meal_saltback_roast", "hunters_brace_platter", "drink_deepwell_cordial", "cook_flour", "cook_spice",
        "cook_fruit", "cook_roots"]
GOODS = ["healing_potion_mega", "mana_potion_mega", "kit_field_repair", "broadhead_arrows", "quarrel_bolts",
         "shot_mithril", "parchment", "beast_lure", "vial_crystal"]
SMITHING = ["whetstone", "flux_strong", "coal", "kit_field_repair"]

#: vendor_id -> (map, name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "sc_spear_provisioner": ("crown", "Provisioner Juzzi", "troll", F, 7, "right", 49, False, FOOD,
                             "Everything here came up the tree on somebody's back, so eat slowly. The sky people "
                             "offered us their food at the parley, and the war-leader threw it over the edge."),
    "sc_spear_trader": ("crown", "Trader Ko'rin", "troll", M, 14, "left", 49, False, GOODS,
                        "Arrows, potions and rope, and I'll buy anything you pull off a dead soldier. Their crystal "
                        "fetches a good price down at the Settlement, so don't leave it lying on the cloud."),
    "sc_annex_trader": ("crown", "Beatriz Lobo", "human", F, 9, "down", 49, False, FOOD[:4] + ["parchment", "vial_crystal"],
                        "I ran a cafe in Porto, and now I make soap, candles and something close to coffee out of "
                        "what the scholars throw away. They think I'm a genius. I trade it all for whatever I can't "
                        "make myself."),
    "lw_provisioner": ("lens", "Provisioner Bryn Aster", "aetherian", M, 1, "right", 49, False, FOOD,
                       "The survey eats well, because the House believes a hungry scholar makes mistakes. You're a "
                       "guest of the House, so the bread's free. Everything else, I'm afraid, costs the same as it "
                       "does for us."),
    "lw_supplier": ("lens", "Quartermaster Daveth Ryne", "aetherian", M, 3, "left", 49, False, GOODS,
                    "Reagents, powder and anything else a survey runs through faster than it planned. I'll also buy "
                    "what you salvage off the Ascendancy, and I won't ask how you came by it."),
    "lw_smith": ("lens", "Crystalsmith Ondrel Vask", "aetherian", M, 4, "down", 49, True, SMITHING,
                 "I mend crystal and I mend steel, though I'll admit your steel surprised me. It's heavy and crude, "
                 "and it doesn't break when I hit it. Put whatever's damaged on the bench."),
}

#: npc_id -> (map, name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Crown: the Mural Gate and the Lookdown
    "sc_gatewatch": ("crown", "Gatewatcher Zul'mo", "troll", M, 15, "left",
                     "Everybody who comes up through the old wall stops right where you're standing and stares. Take "
                     "your time. Then go west to Spearhold, because the war-leader wants every spear he can get."),
    "sc_lookdown": ("crown", "Old Ranjo", "troll", M, 1, "down",
                    "Look straight down the Hollow, past the trunk. The green smudge down there, ringed with water, "
                    "is Stranglethorn, and the village I was born in is somewhere in it. I come out here every morning "
                    "to make sure it's still there."),
    # ---- Spearhold
    "sc_warleader": ("crown", "War-Leader Rakkuzi", "troll", M, 11, "right",
                     "The sky people walked onto our tree and called it a meeting. Then their soldiers fell on the "
                     "meeting, and now they hold the north arm. Zan'kaji sent me up here to throw them off it, and "
                     "I'm going to, whatever Orgrimmar's envoy has to say about it."),
    "sc_envoy": ("crown", "Envoy Garrok Blackmane", "orc", M, 6, "left",
                 "The Warchief sent me to keep the Horde out of a war it doesn't understand. The trolls want blood, the "
                 "scholars want to talk, and the soldiers who hit the parley want the whole tree. I'm trying to work "
                 "out which of them is lying to me, and so far it looks like all three."),
    "sc_witchdoctor": ("crown", "Witch Doctor Zanshi", "troll", F, 6, "right",
                       "There's light coming up through the cloud east of here, where the old stones sink into it. "
                       "It isn't sunlight, and it gets stronger every time the sky ships fire their guns. The loa "
                       "won't tell me what it is, and that scares me more than the soldiers do."),
    "sc_spear_scout": ("crown", "Scout Jinra", "troll", F, 13, "down",
                       "The soldiers dug in across the north arm in a single night. They've got poles that hum and "
                       "throw up a shield, and guns that throw lightning. I counted their lancers twice, and both "
                       "times I came back with a bigger number."),
    "sc_wyvern_rider": ("crown", "Rider Taz'kal", "troll", M, 9, "left",
                        "My wyverns won't fly anywhere near the beasts on the islets. They've never been scared of "
                        "anything in their lives, and now they shake in their roosts at night. Something up here is "
                        "bigger than they are, and they know it."),
    # ---- the Parley Stones
    "sc_parley_scholar": ("crown", "Ilaren Vey", "aetherian", M, 2, "right",
                          "I came down here to talk, and I was halfway through my first sentence when the "
                          "Ascendancy's ship came down on the stones. They're my own people, and they fired on me "
                          "without a word. My house says the ground is primitive. I'm starting to think the ground's "
                          "the only one up here being reasonable."),
    "sc_parley_troll": ("crown", "Speaker Hezza", "troll", F, 3, "left",
                        "I stood on these stones for the Highbough. The pale one across from me was talking about "
                        "trade when the sky ship came down, and I saw his face. He was as surprised as I was. The "
                        "war-leader won't believe that, but I was there and he wasn't."),
    # ---- the Sunken Seal
    "sc_seal_watcher": ("crown", "Archivist Elyon Sarre", "aetherian", M, 5, "down",
                        "This ring was old before the first of our cities ever left the ground. The Kharad built it, "
                        "the giants, and they cut warnings into every stone. I can read about one word in three, and "
                        "every word I can read means keep it shut."),
    # ---- the Annex
    "sc_annex_lead": ("crown", "Matias Arrieta", "human", M, 15, "down",
                      "I was a paragliding instructor in Bariloche, and I woke up on a rock in the sky with my wing in "
                      "shreds. The scholars found me two weeks later. I've lived with them for three years now. "
                      "They're good people, mostly, but not one of them has ever asked me if I want to go home."),
    "sc_annex_doctor": ("crown", "Dr. Rania Azar", "human", F, 6, "left",
                        "I was a doctor in Beirut, and now I'm the only doctor for thirty people on a cloud. The "
                        "scholars stand behind me while I work and write down everything I do. Yesterday one of them "
                        "asked me why we bother to set a broken bone. I'm still working out how to answer him."),
    "sc_annex_engineer": ("crown", "Pavel Novak", "human", M, 16, "right",
                          "The survey wants me to look at their engines, the ones that hold whole cities up in the "
                          "sky, and they want my opinion. I designed bridges in Brno. I said yes before anyone could "
                          "change their mind."),
    "sc_climber": ("crown", "Ewan Docherty", "human", M, 17, "left",
                   "I climbed that tree from the roots, every branch of it, and I thought I'd be the first one to the "
                   "top. It turns out there were thirty people already living on a cloud up here, and not one of them "
                   "had to climb."),
    # ---- the Falls of Light, the Survey Dock, the Taken Crown's edge
    "sc_falls_hunter": ("crown", "Hunter Dak'zin", "troll", M, 10, "down",
                        "The sky beasts come down to drink where the falls go over. Some of them are the size of a "
                        "hut and float like they're full of air. I've hunted everything Stranglethorn has, and I still "
                        "don't know where to put the spear in one of these."),
    "sc_dockhand": ("crown", "Dockmaster Saren Holt", "aetherian", M, 3, "right",
                    "The gangway's open, and Lenswatch is across it. Mind your feet at the far end, because the "
                    "island drifts a hand's width on its chains and nobody's got round to fixing it."),
    "sc_line_scout": ("crown", "Scout Muzza", "troll", M, 12, "right",
                      "This is as close as you get without a shield of your own. Past those humming poles the lancers "
                      "see you before you see them. I lost two brothers learning that."),
    # ---- Lenswatch
    "lw_gangway_guard": ("lens", "Survey Guard Orrin Talvas", "aetherian", M, 5, "right",
                         "Welcome to Lenswatch. Keep your weapons sheathed on the stone, and please don't touch the "
                         "lens. The surveyor will want to meet you, because he wants to meet everyone who comes up."),
    "lw_innkeeper": ("lens", "Keeper Aurel Quan", "aetherian", M, 2, "down",
                     "The House built this guesthouse for visitors from the ground, and you're the first ones who've "
                     "actually slept in it. The beds are soft, the food is strange, and the wind can't get in. If you "
                     "want to come back here quickly, I'll mark your hearthstone."),
    "lw_skiffmaster": ("lens", "Skiffmaster Toren Valdis", "aetherian", M, 4, "left",
                       "The skiffs fly down to the troll city and back. They'll go further once the council lets us, "
                       "but for now the sky past the shelf belongs to the Ascendancy's patrols."),
    "lw_surveyor": ("lens", "Surveyor-Captain Ilvaro Destren", "aetherian", M, 1, "down",
                    "The House of the Patient Lens sent me to study the tree and the people on it. I've spent my whole "
                    "life measuring things, and I can't measure this. The tree's still growing, the trolls want us "
                    "gone, and our own soldiers are shooting at my camp. Sit down and tell me what the ground thinks "
                    "of us."),
    "lw_lensmaster": ("lens", "Lensmaster Coryn Aldaer", "aetherian", M, 3, "right",
                      "On a clear day the great lens can see a coin on the ground from up here. I've watched your "
                      "cities for a year. Your Orgrimmar has very loud markets, and I mean that as a compliment."),
    "lw_warden": ("lens", "Warden Sellis Varn", "aetherian", M, 5, "right",
                  "The Earth people are guests of the House. We found them on islands nobody lives on, starving and "
                  "frightened, and we took them in. Some of them call that a kindness and some of them call it a "
                  "cage. I'm honestly not sure which of them is right."),
    "lw_archivist": ("lens", "Archivist Tavian Rell", "aetherian", M, 4, "down",
                     "Everything the survey learns comes through this hall, and we write it all down twice. The "
                     "Ascendancy took our first copy when they came down on the stones. We think they wanted what "
                     "we'd learned about the old ring in the cloud."),
    "lw_shipwright": ("lens", "Shipmaster Corin Haldane", "aetherian", M, 2, "left",
                      "She's the oldest hull in the House's fleet, and she's flown further than any of the new ones. "
                      "She's got one more long flight in her, and the surveyor's saving it for getting everyone home, "
                      "if it ever comes to that."),
}


#: npc_id -> (map, name, prop image, cutscene, greeting): things, not people (drawn as a prop, like a mailbox)
PROPS = {
    "sc_mural_piece": ("crown", "A Fallen Piece of the Mural", "assets/tiles/sky/props/sk_mosaic_fragment.png", "crown",
                       "A slab of painted stone from the old wall lies face up in the moss, and a little of the golden "
                       "sun is still on it."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    for key, mod in MAPS.items():
        mine = {k for k, v in list(VENDORS.items()) + list(AMBIENT.items()) + list(PROPS.items()) if v[0] == key}
        if mine != set(mod.NPC_POSITIONS):
            bad.append(f"{mod.NAME}: roster and layout disagree: {sorted(mine ^ set(mod.NPC_POSITIONS))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
    # every item a shelf here sells must already be sold somewhere else (so it exists and is priced)
    sold = {i for r in load("data/npcs/vendors.json")["vendors"] if r["vendor_id"] not in VENDORS
            for i in r.get("sells", [])}
    for k, v in VENDORS.items():
        bad += [f"{k}: nobody else sells {i}" for i in v[8] if i not in sold]
    return bad


def main():
    bad = check()
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    vd, ad = load("data/npcs/vendors.json"), load("data/npcs/ambient_npcs.json")
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (mk, name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        mod = MAPS[mk]
        x, y = mod.NPC_POSITIONS[vid]
        rec = dict(vendor_id=vid, name=name, zone=zone_key(mod.NAME), x=x, y=y, tile_sprite="npc",
                   buys_from_player=True, faction="neutral", gear_level=gl, sells_gear=gear, race=race,
                   gender=gender, appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    for nid, (mk, name, race, gender, var, facing, greet) in AMBIENT.items():
        mod = MAPS[mk]
        x, y = mod.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone_key(mod.NAME), x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
        else:
            ad["npcs"].append(rec)
            made += 1
    for nid, (mk, name, prop, cutscene, greet) in PROPS.items():
        mod = MAPS[mk]
        x, y = mod.NPC_POSITIONS[nid]
        rec = dict(npc_id=nid, name=name, zone=zone_key(mod.NAME), x=x, y=y, greeting=greet, prop=prop,
                   plays_cutscene=cutscene, facing="down")
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
    print(f"The Sunward Crown and Lenswatch: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
