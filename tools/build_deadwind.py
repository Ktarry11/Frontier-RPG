#!/usr/bin/env python3
"""Deadwind Pass's people: Ariden's Watch (its inn, its bats, its shop and its liquidators) and the few who live out in
the pass. Idempotent.

    PYTHONPATH=. python3 tools/build_deadwind.py

The vision is docs/deadwind_brief.md and the story docs/deadwind_quest_plan.md. The maps are
tools/handbuilt_ariden_watch.py, tools/handbuilt_deadwind_west.py and tools/handbuilt_deadwind_east.py, and every
person here stands where its NPC_POSITIONS says; a person in one and not the other stops the script.

THE LIQUIDATORS are Earth transplants who've lived next to a fallout zone, or cleaned one up, and came to this one on
purpose. They took the Soviet word for the people who went into Chernobyl in 1986. Each of them came from somewhere
real: Slavutych, Fukushima, St. George in Utah, Semey by the Polygon, Goiania, the farms under Windscale, Rongelap,
Hanford. The Forsaken apothecaries work beside them because the Seep barely touches the dead.

The four sheet-5 recruits who live in the camp (Taras, Wes, Mariana, Neil) are placed by
tools/build_sheet5_recruits.py, not here.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_ariden_watch as AW  # noqa: E402
from tools import handbuilt_deadwind_west as DWW  # noqa: E402
from tools import handbuilt_deadwind_east as DWE  # noqa: E402
from tools.npc_data_guard import safe_update  # noqa: E402
from world.zone_keys import zone_key  # noqa: E402

SERVICES = {"dw_innkeeper": ["inn"], "dw_bat_handler": ["flight"]}
FLIGHT_NODES = [
    ("ariden_watch", {"name": "Ariden's Watch", "zone": AW.NAME, "master": "dw_bat_handler",
                      "pos": [8, 142], "continent": "eastern_kingdoms"}),
]
M, F = "male", "female"

#: vendor_id -> (name, race, gender, variant, facing, gear_level, sells_gear, stock, greeting)
VENDORS = {
    "dw_peg": ("Peg Thwaite", "human", F, 5, "down", 56, False,
               ["meal_ember_glazed_ribs", "drink_starfall_wine", "high_table_feast", "cook_flour",
                "cook_spice", "cook_water", "cook_mushroom"],
               "We kept a dairy in Cumbria, under Windscale. When the pile caught fire in fifty-seven, they poured "
               "away every drop of milk from two hundred square miles for a month, ours with it. I feed this camp "
               "now, and I check every barrel twice before it goes on a table."),
    "dw_quartermaster": ("Quartermaster Dale Henning", "human", M, 4, "down", 56, True,
                         ["kit_field_repair", "healing_potion_masterwork", "mana_potion_masterwork", "parchment"],
                         "I spent thirty years cleaning up Hanford, in Washington, where they made the plutonium. "
                         "The paperwork alone could have shielded a reactor. The Liquidators pay in what we've got, "
                         "and what we've got goes to the people who've earned it. Do the work and my shelf opens up."),
    "dw_smith": ("Ironmonger Edric Vail", "forsaken", M, 3, "left", 56, True,
                 ["kit_field_repair", "whetstone", "flux_strong"],
                 "The Seep gets into steel the way it gets into everything else, from the inside, where you can't "
                 "see it until the blade snaps. Let me look at your gear before you trust your life to it out there."),
}
#: npc_id -> (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- Ariden's Watch
    "dw_halyna": ("Chief Liquidator Halyna Bondar", "human", F, 4, "down",
                  "My father kept his dosimeter on the kitchen shelf in Slavutych, next to the salt. He said it was "
                  "so he'd remember. I didn't understand what he meant until I came over that last rise and saw the "
                  "wheel standing in the middle of this pass."),
    "dw_kenji": ("Kenji Watanabe", "human", M, 3, "left",
                 "At Fukushima we wrote our names and our readings on a sheet at the end of every shift. Here I "
                 "write them on the board by the pyre, and the readings are worse and the list of names is shorter. "
                 "Has anyone checked your dosimeter today?"),
    "dw_harrow": ("Deathguard Harrow", "forsaken", M, 2, "down",
                  "I used to count the living who came through this gate and the dead who didn't come back. I "
                  "stopped when the second number caught up with the first. Scrub at the troughs, and then you can "
                  "go wherever you like."),
    "dw_tobiah": ("Old Tobiah", "forsaken", M, 5, "left",
                  "Anything that dies too near the wheel gets up again unless it's burned, so I burn it, and I talk "
                  "to it while it goes because somebody ought to. Mind the smoke. It burns green for a reason."),
    "dw_aigerim": ("Dr. Aigerim Seitkali", "human", F, 3, "right",
                   "I grew up in Semey, beside the Polygon, where the Soviets tested their bombs for forty years and "
                   "told nobody downwind. Half my patients were born with those tests in their blood. I came here "
                   "because I know what this looks like long before anyone admits it."),
    "dw_morwen": ("Master Apothecary Morwen Ashgrave", "forsaken", F, 4, "down",
                  "The Seep barely troubles the dead, which makes my people the only ones who can walk out there for "
                  "long. The Undercity wants to know what it is. So do I, for reasons of my own, and you'll find I "
                  "pay very well for samples."),
    "dw_lisbeth": ("Apothecary Lisbeth Vane", "forsaken", F, 2, "right",
                   "Master Ashgrave writes down everything the Seep does. I write down everything Master Ashgrave "
                   "does. Somebody in the Undercity reads both, and I'd like it to be the right somebody."),
    "dw_luiz": ("Luiz Ferreira", "human", M, 4, "down",
                "In Goiania in 1987, two scrap men opened an old hospital machine and found a powder inside that "
                "glowed blue in the dark. People took it home because it was beautiful. My uncle rubbed it on his "
                "arms at a party. So when somebody here picks up a piece of glowing glass and smiles at it, I take it "
                "off them."),
    "dw_rine": ("Rine Lajuon", "human", F, 3, "down",
                "My grandmother was a girl on Rongelap in 1954, when ash from the Bravo test came down like snow and "
                "the children played in it. They moved our people off the island, then back, then off again. I "
                "build the things that keep people away from places now, and the spire is the biggest one I've "
                "ever built."),
    # Sela Crowe keeps the inn (Kyle, 18 Nov 2026: "We never loose an innkeeper though for our hearth")
    "dw_innkeeper": ("Innkeeper Sela Crowe", "forsaken", F, 3, "down",
                     "Every town keeps a fire and a bed, even this one. The living sleep badly here and the dead "
                     "don't sleep at all, so I'm up either way. I'll bind your hearth here if you want it."),
    "dw_bat_handler": ("Bat Handler Ossian Reed", "forsaken", M, 2, "down",
                       "The bats won't fly over the middle of the pass. Something about the wheel turns their ears "
                       "inside out, and I've stopped trying to make them. I'll take you anywhere else they know."),
    # ---- out in the pass
    "dw_delgado": ("Corporal Ray Delgado", "human", M, 5, "down",
                   "Welcome to the fence. My grandmother grew up in St. George, Utah, downwind of the Nevada tests, "
                   "and the government told her those clouds were nothing to worry about. So I never tell anybody "
                   "anything's nothing to worry about. Scrub at the Watch before you hug anyone."),
    "dw_mourner": ("Agatha Morgan", "forsaken", F, 4, "left",
                   "This was my family's ground long before anybody called it a plot. I was buried in it once, in "
                   "that crypt there, and I dug my own way out. Now the ground keeps changing its mind about what it "
                   "holds."),
    "dw_hanna": ("Baba Hanna", "human", F, 5, "down",
                 "They moved us out of Kupuvate in 1986 and told us three days. I walked back in the next spring "
                 "with my sister, and I stayed thirty years. A pass full of ghosts doesn't frighten me. I've buried "
                 "worse than ghosts."),
    "dw_vessa": ("Deathstalker Vessa Morrow", "forsaken", F, 3, "left",
                 "The Dark Lady wants eyes on the middle of the pass, and the living don't last out here. I don't "
                 "have that problem. The things out there are older and younger than they should be, sometimes both "
                 "at once."),
    "dw_grull": ("Grull the Younger", "ogre", M, 1, "right",
                 "The little one in me remembers when the clan used to sing. The big one remembers what the clan did "
                 "after the singing stopped. Both of us want it finished."),
    "dw_ariden": ("Ariden", "human", M, 5, "right",
                  "I've watched that tower every evening for forty years, and every evening the light in the high "
                  "window goes out at the same moment. It's this evening again, isn't it? It's always this evening."),
    "dw_bridge_echo": ("The Bridge Echo", "echo", M, 1, "right",
                       "...I can see the far side from here. Halya, tell them the readings are wrong. Tell them it "
                       "isn't a hole at all, it's a..."),
}

WHERE = {}
WHERE.update({k: (AW.NAME, xy) for k, xy in AW.NPC_POSITIONS.items()})
WHERE.update({k: (DWW.NAME, xy) for k, xy in DWW.NPC_POSITIONS.items()})
WHERE.update({k: (DWE.NAME, xy) for k, xy in DWE.NPC_POSITIONS.items()})


def main():
    roster = set(VENDORS) | set(AMBIENT)
    if roster != set(WHERE):
        raise SystemExit(f"roster and layouts disagree: {sorted(roster ^ set(WHERE))}")
    from tools.build_tempest_quests import voice_problems
    bad = [f"{k}: {p}" for k, v in list(VENDORS.items()) + list(AMBIENT.items()) for p in voice_problems(v[-1])]
    if bad:
        raise SystemExit("FAILED - fix the greetings:\n  " + "\n  ".join(bad))

    vp, ap = ROOT / "data/npcs/vendors.json", ROOT / "data/npcs/ambient_npcs.json"
    vd, ad = json.loads(vp.read_text(encoding="utf-8")), json.loads(ap.read_text(encoding="utf-8"))
    vby = {r["vendor_id"]: r for r in vd["vendors"]}
    aby = {r["npc_id"]: r for r in ad["npcs"]}
    made = moved = 0
    for vid, (name, race, gender, var, facing, gl, gear, stock, greet) in VENDORS.items():
        zname, (x, y) = WHERE[vid]
        rec = dict(vendor_id=vid, name=name, zone=zone_key(zname), x=x, y=y, tile_sprite="npc", buys_from_player=True,
                   faction="neutral", gear_level=gl, sells_gear=gear, race=race, gender=gender,
                   appearance_variant=var, facing=facing, greeting=greet)
        if vid in vby:
            moved += bool(safe_update(vby[vid], rec))
            vby[vid]["zone"] = zone_key(zname)
        else:
            rec["sells"] = list(stock)
            vd["vendors"].append(rec)
            made += 1
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        zname, (x, y) = WHERE[nid]
        rec = dict(npc_id=nid, name=name, zone=zone_key(zname), x=x, y=y, greeting=greet, gender=gender, race=race,
                   appearance_variant=var, facing=facing)
        if nid in aby:
            moved += bool(safe_update(aby[nid], rec))
            aby[nid]["zone"] = zone_key(zname)
        else:
            ad["npcs"].append(rec)
            made += 1
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ap.write_text(json.dumps(ad, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = ROOT / "data/travel/travel_data.json"
    td = json.loads(tp.read_text(encoding="utf-8"))
    for k, v in SERVICES.items():
        td["services"][k] = sorted(set(td["services"].get(k, [])) | set(v))
    for key, node in FLIGHT_NODES:
        td["flight_nodes"][key] = node
    tp.write_text(json.dumps(td, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Deadwind: {made} created, {moved} moved ({len(roster)} people)")


if __name__ == "__main__":
    main()
