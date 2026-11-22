#!/usr/bin/env python3
"""The Fading Firmament's people (57-60): the last of the Firmament's own at Lastlight, the House of Long Memory's
scholars at Forgewatch, and the few still out on the islands. Idempotent.

    PYTHONPATH=. python3 tools/build_fading_firmament_people.py

docs/worldtree_brief.md. The Firmament's people left in stages over centuries; the ones at Lastlight are the ones who
wouldn't, round the one shrine still lit. Lastlight is the Firmament's town, on its own map since 22 Nov 2026 (Kyle's town rule;
tools/handbuilt_worldtree_lastlight.py): the last inn, the mail, the zone's one flight path, and the House of Long
Memory's rooms, moved in from Forgewatch at the Threefold Forge (the house the others laugh at for saying the Kharad
were here first). A person stands on whichever map lists them. The Aetherians wear the AE-M and AE-W looks picked for their jobs (world/race_registry.py: men
5+N for m-N, women N-1 for w-N). Transplants are factionless, and nobody up here knows what the change was.

Magister Orla Thessan came north after her student (tools/build_ascendant_bastions_people.py); Ascendant-General Maelis
Ardane is beaten and taken alive at the end of the chain (Kyle, 21 Nov 2026), and the quest text says so. The map
doesn't change.

Every person stands where the map's NPC_POSITIONS says; a person in one and not the other stops the script.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_worldtree_fading_firmament as FF  # noqa: E402
from tools import handbuilt_worldtree_lastlight as LL  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

M, F = "male", "female"

SERVICES = {"ff_skiffmaster": ["flight"], "ll_innkeeper": ["inn"]}
FLIGHT_NODES = [
    ("fading_firmament", {"name": "Lastlight", "zone": LL.NAME, "master": "ff_skiffmaster", "pos": [-6, 104],
                          "continent": "eastern_kingdoms"}),
]

FOOD = ["meal_ember_glazed_ribs", "high_table_feast", "drink_starfall_wine", "cook_flour", "cook_spice",
        "cook_fruit", "cook_roots"]
GOODS = ["healing_potion_supreme", "mana_potion_supreme", "barbed_arrows", "shot_void",
         "parchment", "beast_lure", "vial_crystal"]

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "ff_provisioner": ("Provisioner Hesk Amaury", "aetherian", M, 14, "left", 58, False, FOOD,
                       "I keep the camp's stores, and I sell what's left over to anyone who'll carry it out to the "
                       "islands. Most of it came up on the last skiff, so don't waste it."),
    "ff_trader": ("Trader Liss Corvane", "aetherian", F, 12, "left", 58, True, GOODS,
                  "My family traded on the Firmament for six hundred years. I'm the last of us up here, and I'll sell "
                  "you whatever I've got before the ground goes."),
}

#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Road's End
    "ff_road_warden": ("Warden Kael Ostry", "aetherian", M, 18, "down",
                       "I count everyone who comes up the road, and I've counted three columns of soldiers this "
                       "week and one of you. I'll admit I'm gladder to see you than I was to see them."),
    # ---- Lastlight
    "ff_shrine_keeper": ("Keeper Sabine Aldour", "aetherian", F, 21, "down",
                         "This is the last shrine on the Firmament that's still lit. As long as it burns, the people "
                         "here have a reason to stay, and I'll keep it burning as long as they do."),
    "ff_last_magistrate": ("Magistrate Ilse Varrow", "aetherian", F, 4, "right",
                           "I was magistrate of the Firmament when it had nine towns. Now it has one camp, and I'm "
                           "still magistrate, because somebody has to say what happens to the people who stayed."),
    "ff_orla": ("Magister Orla Thessan", "aetherian", F, 16, "left",
                "I followed Maelis north. She's here, at the Moorage, with the fleet that's meant to take the tree. "
                "I taught her to read the sky, and now I've got to watch what she's doing with it."),
    "ff_skiffmaster": ("Skiffmaster Dorran Vale", "aetherian", M, 9, "right",
                       "Mine's the last skiff that still flies out of the Firmament. I can get you to the Bastions, "
                       "to Aurelion or anywhere else that's still friendly."),
    "ff_lamp_cutter": ("Cutter Ansel Fennick", "aetherian", M, 22, "left",
                       "I cut the crystals for the shrine. I'm the last crystal-cutter on the Firmament, and I've "
                       "got nothing left to cut but what you bring me."),
    "ff_salvager": ("Sipho Ndlovu", "human", M, 6, "right",
                    "I ran a scrapyard in Durban for twenty years. Up here the islands drop scrap on you every day, "
                    "and the Aetherians pay me to tell them which bits still work."),
    "ff_child_minder": ("Annika Sjoberg", "human", F, 3, "down",
                        "I taught primary school in Umea before the change. There are eleven children in this camp, "
                        "and somebody has to teach them their letters while the world falls apart round them."),
    # ---- Forgewatch
    "ff_long_memory": ("Archivist Theodora Quell", "aetherian", F, 22, "down",
                       "The House of Long Memory has said for a thousand years that the Kharad were here before us, and "
                       "the other houses have laughed at us for a thousand years. The Threefold Forge is why I'm not "
                       "laughing back."),
    "ff_forge_scholar": ("Scholar Rhun Adaire", "aetherian", M, 12, "right",
                         "I read Kharad runes, which makes me the only person at Forgewatch who can tell you what the "
                         "giants' hearth says. Mostly it tells you to mind your feet."),
    "ff_earthborn_smith": ("Kwabena Osei", "human", M, 8, "left",
                           "I shod horses and mended ploughs in Kumasi. The Archivist brought me up here to tell her "
                           "how a forge works, and this one has three hearths, which no forge I ever saw had."),
    "ff_forgewatch_guard": ("Lens-Warden Corra Hale", "aetherian", F, 7, "right",
                            "The Ascendancy's salvage crews come past the camp every day to get into the Hearthdeep. "
                            "They haven't come into the camp yet, and I'd like to keep it that way."),
    # ---- out on the islands
    "ff_last_resident": ("Old Benedek Saar", "aetherian", M, 26, "right",
                         "Everyone else on this street left forty years ago, and the rest of the Quarter went after "
                         "them. I was born in that house, and I'll go when it does."),
    "ff_gardener": ("Gardener Yllen Moss", "aetherian", F, 18, "left",
                    "Every garden on this island went grey but this one tree. I come out every morning to see if "
                    "it's still green, and so far it always has been."),
    "ff_turncoat": ("Quartermaster Ivo Darrance", "aetherian", M, 15, "down",
                    "I fed the Ascendancy's army for twenty years. I've seen what the general means to do with it, "
                    "and I've stopped wanting to be the one who feeds it."),
    # ---- Lastlight's own (the town map)
    "ll_innkeeper": ("Innkeeper Marit Sollen", "aetherian", F, 10, "down",
                     "There were nine inns on the Firmament when I was a girl, and this is the last of them. I keep the "
                     "beds made because people still come up the road. If you want to come back here quickly, I'll mark "
                     "your hearthstone."),
    "ll_gatewarden": ("Lamplighter Toben Ash", "aetherian", M, 7, "right",
                      "I keep the gate and I light the lamps on the walk, every evening, from the shrine's own crystal. "
                      "There were forty lamps on this walk once. I light the four we've got left very carefully."),
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check():
    from tools.build_tempest_quests import voice_problems
    bad = []
    mine = set(VENDORS) | set(AMBIENT)
    both = set(FF.NPC_POSITIONS) & set(LL.NPC_POSITIONS)
    if both:
        bad.append(f"on both maps: {sorted(both)}")
    if mine != set(FF.NPC_POSITIONS) | set(LL.NPC_POSITIONS):
        bad.append(f"roster and layout disagree: {sorted(mine ^ (set(FF.NPC_POSITIONS) | set(LL.NPC_POSITIONS)))}")
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
    mod = LL if nid in LL.NPC_POSITIONS else FF
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
            vby[vid]["sells"] = list(stock)          # the shelf is this script's: the 57-60 tier (qa_vendor_stock)
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
    box = next((r for r in ad["npcs"] if r["npc_id"] == "mailbox_ll_innkeeper"), None)
    if box is None:
        box = {"npc_id": "mailbox_ll_innkeeper"}
        ad["npcs"].append(box)
    box.update(name="Mailbox", zone=zone_key(LL.NAME), x=32, y=54, facing="down", race="aetherian",
               appearance_variant=0, is_mailbox=True, prop="assets/buildings/ae_mail_pylon.png",
               greeting="Lastlight's mail goes out on the last skiff. Most of the letters are to people who left, and "
                        "most of them never get answered.")
    save("data/npcs/vendors.json", vd)
    save("data/npcs/ambient_npcs.json", ad)
    td = load("data/travel/travel_data.json")
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    save("data/travel/travel_data.json", td)
    print(f"The Fading Firmament: {made} created, {moved} moved ({len(VENDORS) + len(AMBIENT)} people)")


if __name__ == "__main__":
    main()
