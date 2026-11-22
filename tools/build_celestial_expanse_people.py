#!/usr/bin/env python3
"""The Celestial Expanse's people (49-51): the survivors of the council's skiff on Crashfall, the Earthborn of Tethertown,
the Aetherians of Halcyon Rest, and the few out on the islands. Idempotent.

    PYTHONPATH=. python3 tools/build_celestial_expanse_people.py

docs/worldtree_brief.md. The Sunward Crown ends with the council opening Aurelion to the ground and sending its own skiff
down to fetch the survey's guests and the player. The old Kharad wards that woke when the seal cracked brought that skiff
down on Crashfall, at the bottom of the Expanse, and the road from there runs upriver to Aurelion. Ilaren Vey and Leandro
Arrieta, the player's pair of allies, were on it, and they're here now (their own records, ce_ilaren and ce_leandro).

Halcyon Rest is the Expanse's town, on its own map since 22 Nov 2026 (Kyle's town rule; tools/handbuilt_worldtree_halcyon_rest.py):
the inn, the mail and the zone's one flight path (the skiffs). Tethertown's Earthborn live on two rocks tied on below it,
and the people who came up the river from the wreck lodge there. A person stands on whichever map lists them. Aetherian NPCs are men until the women's sheet lands (docs/recruit_art_prompts_sheet6.md, AE-W). The rules
hold: transplants are factionless, and nobody up here knows what the change was.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_celestial_expanse as CE  # noqa: E402
from tools import handbuilt_worldtree_halcyon_rest as HR  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"ce_skiffmaster": ["flight"], "hr_innkeeper": ["inn"]}
FLIGHT_NODES = [
    ("celestial_expanse", {"name": "Halcyon Rest", "zone": HR.NAME, "master": "ce_skiffmaster", "pos": [-24, 132],
                           "continent": "eastern_kingdoms"}),
]

FOOD = ["meal_saltback_roast", "hunters_brace_platter", "drink_deepwell_cordial", "cook_flour", "cook_spice",
        "cook_fruit", "cook_roots"]
GOODS = ["healing_potion_masterwork", "mana_potion_masterwork", "broadhead_arrows", "quarrel_bolts",
         "shot_mithril", "parchment", "beast_lure", "vial_crystal"]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "ce_provisioner": ("Provisioner Mael Corbin", "aetherian", M, 1, "right", 50, False, FOOD,
                       "Halcyon Rest has fed travellers on this river for three hundred years. There aren't many "
                       "travellers any more, so you'll get the good bread and the full bowl."),
    "ce_trader": ("Trader Halric Vane", "aetherian", M, 3, "down", 50, True, GOODS,
                  "I'll sell you what a traveller needs and buy what a traveller finds. If you've been out on the Golem "
                  "Fields, I'll pay well for anything that still hums."),
    "ce_tether_trader": ("Yasmin Darwish", "human", F, 8, "down", 50, False, FOOD[:5] + ["parchment"],
                         "I had a bakery in Tripoli, by the old souk, and now I bake on a rock tied to a bigger rock. "
                         "The flour's from the scholars, the recipe's my grandmother's, and the oven's a Kharad brazier."),
}

#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- Crashfall
    "ce_ilaren": ("Ilaren Vey", "aetherian", M, 2, "right",
                  "The wards were Kharad. They woke when the seal cracked, and they fired on the first Aetherian ship "
                  "they saw, which was ours. We made it this far up the river, and Aurelion is only the rest of the way."),
    "ce_leandro": ("Leandro Arrieta", "human", M, 15, "left",
                   "Three years in the sky and I've never once been in a crash. I've been in a lot of falls, but a crash "
                   "is different. We got everyone up to the Rest without losing one over the edge, and I'll owe you a drink in Aurelion if you help me keep it that way."),
    "ce_pilot": ("Skiff-Pilot Varo Senn", "aetherian", M, 4, "down",
                 "Something on the islands below lit up and the skiff's crystal went dark in my hands. I put her down "
                 "where I could. I'm sorry it wasn't softer, and I'm sorry my leg won't hold me yet."),
    "ce_herald": ("Herald Cassian Orel", "aetherian", M, 1, "left",
                  "The council sent me to bring you to Aurelion with all the courtesy of the High Houses. The courtesy "
                  "is somewhere in that wreck. The invitation still stands, if you'll walk it."),
    "ce_landing_hand": ("Landing Hand Hask Merrow", "aetherian", M, 3, "left",
                        "The survey's skiff comes and goes from here to Lenswatch, and it flies low and slow now that "
                        "the old stones shoot at anything bright. Mind the gangway, it's newer than the rest of us."),
    # ---- the Last Falls and the Golem Fields
    "ce_falls_watcher": ("Elder Merek Vale", "aetherian", M, 4, "down",
                         "I come here to watch the river go over the edge. It's gone over for as long as I've lived, "
                         "but lately I've started counting the islands that go over with it."),
    "ce_golem_scholar": ("Scholar Idris Marrowell", "aetherian", M, 4, "right",
                         "The House of Long Memory says the Kharad were here before we were, and the rest of the "
                         "houses laughed at us for it. Then their war-golems stood up. Nobody's laughing now, and I've "
                         "never been so frightened to be right."),
    # ---- Tethertown
    "ce_tether_lead": ("Kaisa Lehtonen", "human", F, 3, "down",
                       "I ran search and rescue out of Rovaniemi, so I'm good at finding people who don't want to be "
                       "lost. Thirty-one of us woke up on these rocks. We're still finding the last few."),
    "ce_tether_rigger": ("Gustavo Pires", "human", M, 16, "left",
                         "I did rope access on the towers in Rio, hanging off the side of a building with a bucket. "
                         "Tying two rocks together over the sky is the same job, it's just a much longer fall."),
    "ce_tether_farmer": ("Annelies de Vries", "human", F, 5, "right",
                         "I grew tomatoes under glass outside Westland, forty hectares of them. I had a packet of seeds "
                         "in my coat when I woke up here, and the first one came up blue. I'm still deciding if I'd eat "
                         "it."),
    # ---- the Whale Shallows
    "ce_whale_watcher": ("Dr. Ana Kealoha", "human", F, 9, "right",
                         "I spent fifteen years counting humpbacks off Maui, and I thought I'd seen every kind of big "
                         "animal there was. Then one swam past me through a cloud. I've been out here every day since."),
    # ---- Halcyon Rest
    "ce_keeper": ("Keeper Ithren Lorrow", "aetherian", M, 4, "down",
                  "Halcyon Rest has stood on this river since before Aurelion had its outer rings. We feed whoever "
                  "comes down the water, and lately that's mostly people whose homes fell."),
    "ce_skiffmaster": ("Skiffmaster Davin Sorell", "aetherian", M, 2, "left",
                       "The skiffs still fly, low and dark, with the crystals hooded so the old stones don't see us. "
                       "I'll take you down to the tree's city or across to Lenswatch, but not higher, not yet."),
    "ce_refugee": ("Teodric Ashlane", "aetherian", M, 3, "right",
                   "I lived on the Eighth Ring of Aurelion, the outermost, the one that fell. I was at the market when "
                   "it went, and so I lived. My street didn't."),
    "ce_deserter": ("Dace Morrow", "aetherian", M, 4, "down",
                    "I was a sky lancer until they told us to fire on a parley. I put my lance down on the stones and "
                    "walked. Don't thank me for it. I should have put it down years ago."),
    # ---- Halcyon Rest's own (the town map)
    "hr_innkeeper": ("Innkeeper Sela Marrin", "aetherian", F, 10, "down",
                     "The Guest Hall has twelve beds and a roof the wind can't lift, which is more than most of the river "
                     "can offer tonight. The refugees sleep in the pavilions because they'd rather hear the bells. If you "
                     "want to come back here quickly, I'll mark your hearthstone."),
    "hr_gatewarden": ("Gatewarden Orrin Tal", "aetherian", M, 7, "right",
                      "Nobody's turned away from the Rest, and that's been the rule for three hundred years. I just like "
                      "to see who's coming in. Hold the rail when the wind picks up, because it's older than I am."),
    # ---- the Spillway and the Aurelion Approach
    "ce_spill_tender": ("Aqueduct-Warden Lorne Ishay", "aetherian", M, 1, "right",
                        "That's Aurelion's water coming down, through what's left of the Fourth Aqueduct. It's meant to "
                        "turn back into the city. Instead it spills, and the whole Expanse drinks it."),
    "ce_bridgewarden": ("Bridgewarden Caldus Rhee", "aetherian", M, 2, "down",
                        "The sky-bridge is Aurelion's door, and it stays shut until the council sends word. I know "
                        "they invited you. I've also seen what's come up that bridge lately, so I'll wait for word."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    both = set(CE.NPC_POSITIONS) & set(HR.NPC_POSITIONS)
    if both:
        bad.append(f"on both maps: {sorted(both)}")
    if mine != set(CE.NPC_POSITIONS) | set(HR.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ (set(CE.NPC_POSITIONS) | set(HR.NPC_POSITIONS)))}")
    for k, v in list(VENDORS.items()) + list(AMBIENT.items()):
        bad += [f"{k}: {p}" for p in voice_problems(v[-1])]
        if not v[-1].isascii():
            bad.append(f"{k}: non-ASCII")
    sold = {i for r in load("data/npcs/vendors.json")["vendors"] if r["vendor_id"] not in VENDORS
            for i in r.get("sells", [])}
    for k, v in VENDORS.items():
        bad += [f"{k}: nobody else sells {i}" for i in v[7] if i not in sold]
    return bad


def where(nid):
    """(zone key, x, y) for a person, from whichever map lists them."""
    mod = HR if nid in HR.NPC_POSITIONS else CE
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
    # the Guest Hall keeps the mail, like every inn (qa_auction_house: a mailbox by every inn)
    box = next((r for r in ad["npcs"] if r["npc_id"] == "mailbox_hr_innkeeper"), None)
    if box is None:
        box = {"npc_id": "mailbox_hr_innkeeper"}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=zone_key(HR.NAME), x=41, y=36, facing="down", race="aetherian",
               appearance_variant=0, is_mailbox=True, prop="assets/buildings/ae_mail_pylon.png",
               greeting="The Rest's mail pylon by the Guest Hall. Letters go up to Aurelion on the evening skiff, "
                        "whenever one's flying.")
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    save("data/travel/travel_data.json", td)
    print(f"The Celestial Expanse: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
