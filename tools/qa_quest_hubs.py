#!/usr/bin/env python3
"""Quests come from hubs, not from the spot where the work is.

    PYTHONPATH=. python3 tools/qa_quest_hubs.py

Kyle (backlog [69] + [74]): "I want towns to feel more like hubs people bother to return to," and
"a huge issue ... is that NPCs for quests are placed RIGHT at that subzone, this is... lame."

The rule: about 70% of a region's quests are handed out in its towns, so a quest sends you out and
you come back to turn it in. The rest can come from people who belong in the wild (a road
traveller, a ferryman, a gate guard).

WHAT IS CHECKED. For each region below, every quest whose zone is one of the region's quest zones
is counted, by where its giver stands:
  - in town: the giver's zone is one of the region's hub zones (Razor Hill, Brill, the Undercity),
    or the giver stands within the radius of a hub that sits inside a bigger map (the March in
    Silverpine South);
  - in the wild: anywhere else.
Quests that start from an item you loot have no giver and are left out.

A region listed in FLOORS must have at least that share from town. Raise a floor when a region is
moved; never lower one. Every other region is printed so the next one to fix is easy to see.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

#: region -> (quest zones, hub zones, hubs inside a bigger map: {zone: [(x, y, radius)]})
REGIONS = {
    "Durotar": (["durotar", "razor_hill"], ["razor_hill", "orgrimmar"], {}),
    "Tirisfal": (["western_tirisfal", "eastern_tirisfal", "brill"], ["brill", "undercity", "deathknell"], {}),
    "Silverpine": (["silverpine_north", "silverpine_south", "sepulcher"], ["sepulcher"],
                   {"silverpine_south": [(75, 48, 16)], "silverpine_north": [(84, 15, 10)]}),
    # The Barrens: three towns of their own (the Crossroads, Camp Taurajo, Ratchet) and four camps
    # inside the big maps - Mor'shan Base Camp and Far Watch Post in the north, Grol'dom Farm in the
    # middle, the Waystation in the south.
    "Barrens": (["northern_barrens", "central_barrens", "southern_barrens", "crossroads", "camp_taurajo", "ratchet"],
                ["crossroads", "camp_taurajo", "ratchet"],
                {"northern_barrens": [(145, 58, 12), (252, 124, 12)], "central_barrens": [(85, 146, 12)],
                 "southern_barrens": [(137, 116, 12)]}),
    # Hillsbrad: Tarren Mill (its own map, and its grounds at the top of Eastern Hillsbrad) and the
    # Southpoint Tower garrison at the top of Western Hillsbrad.
    "Hillsbrad": (["western_hillsbrad", "eastern_hillsbrad", "tarren_mill"], ["tarren_mill"],
                  {"eastern_hillsbrad": [(62, 32, 12)], "western_hillsbrad": [(45, 22, 10)]}),
    # ---- 17 Nov 2026, the sweep across every zone (Kyle: "around 30% of quest givers are outside of towns and 70%
    # are inside (rough numbers)")
    # Arathi: Hammerfall and Saltspur Landing are town maps; Refuge Pointe is the camp inside Arathi West.
    "Arathi": (["arathi_west", "arathi_central", "arathi_east"], ["hammerfall", "saltspur_landing"],
               {"arathi_west": [(68, 105, 22)]}),
    # Felwood: the Emerald Sanctuary, and the Talonbranch camp up in North Felwood.
    "Felwood": (["emerald_sanctuary", "north_felwood", "timbermaw_tunnel"], ["emerald_sanctuary", "timbermaw_tunnel"],
                {"north_felwood": [(96, 26, 16)]}),
    # Tempest Isle: Cinderwharf, the landing camp on the Shallows and the works camp on the Ashen Reach.
    "Tempest": (["tempest_shallows", "cinderwharf", "the_ashen_reach"], ["cinderwharf"],
                {"tempest_shallows": [(88, 64, 14)], "the_ashen_reach": [(84, 118, 16)]}),
    # The Underdark: Kael's Bastion, and the two survey camps (the dawn camp and the geode camp).
    "Underdark": (["the_crystalline_underdark", "kaels_bastion", "the_deep_bloom", "the_frostward_descent",
                   "the_hollow_geode"], ["kaels_bastion"],
                  {"the_crystalline_underdark": [(83, 22, 8), (146, 58, 8)]}),
    # ---- 17 Nov 2026, Kyle: "keep fixing up the hub issue". Every region now has an entry.
    # Fenris Isle: Bloodmoon Village became its own small map ("Actual map - but small and seperate").
    "Fenris Isle": (["fenris_isle"], ["bloodmoon_village"], {}),
    # Stranglethorn: Grom'gol and Booty Bay. The arena gatehouse, the road gang, the shelf watcher, the marsh
    # fisher and the herbalist at the falls are people who belong where they stand, and they're the wild share.
    "Stranglethorn": (["gromgol", "central_stranglethorn", "gurbashi_arena", "veilfall_cave", "booty_bay"],
                      ["gromgol", "booty_bay"], {}),
    # Stonetalon: Sun Rock Retreat, and the Mistwalker camp in the west.
    "Stonetalon": (["stonetalon_west", "stonetalon_east", "sun_rock_retreat"], ["sun_rock_retreat"],
                   {"stonetalon_west": [(56, 142, 12)]}),
    # Ashenvale: Astranaar and Splintertree; Zoram'gar, Maestra's Post and the Warsong camp are camps.
    "Ashenvale": (["ashenvale_east", "ashenvale_west", "astranaar", "splintertree_post", "zoram_strand"],
                  ["astranaar", "splintertree_post"],
                  {"zoram_strand": [(20, 24, 14)], "ashenvale_west": [(85, 53, 6)], "ashenvale_east": [(44, 51, 6)]}),
    # The Black Strand: Onyxhollow, and the survey camp at the head of the strand.
    "Black Strand": (["the_black_strand", "the_royal_hive"], ["onyxhollow"], {"the_black_strand": [(18, 21, 8)]}),
    # The Plaguelands: the Bulwark, the Pale Watch and Light's Hope, each its own map.
    "Plaguelands": (["western_plaguelands_north", "western_plaguelands_south", "eastern_plaguelands_west",
                     "eastern_plaguelands_east"], ["bulwark", "pale_watch", "lights_hope_chapel"], {}),
    # Thousand Needles: Freewind Post and Saltwheel.
    "Thousand Needles": (["freewind_post", "saltwheel", "the_shimmering_flats", "the_undercrust"],
                         ["freewind_post", "saltwheel"], {}),
    # Tanaris: Steamwheedle Port, the Fourth Peg and Glittervein.
    "Tanaris": (["northern_tanaris", "steamwheedle_port", "the_drownbell", "the_lashings", "the_abyssal_sands",
                 "glittervein", "the_cistern", "the_mother_vein"], ["steamwheedle_port", "fourth_peg", "glittervein"], {}),
    # The Aspen Wilderness: Longstand Camp in the Gold Stands. Its scouts and runners report back to camp (17 Nov
    # 2026); the lift keeper, the rope master and the cave watch stay at the spots that are their whole job.
    "Aspen": (["the_aspen_wilderness"], [], {"the_aspen_wilderness": [(93, 81, 10)]}),
    # The Echo Isles: the Darkspear camp and the troll village. The reef wrangler and the young diver stay out.
    "Echo Isles": (["echo_isles"], [], {"echo_isles": [(80, 50, 9), (122, 57, 9)]}),
    # ---- 22 Nov 2026, Caelora's towns (Kyle: "Lets build the towns, move the NPCs"): each sky map's camp is its own
    # town map now. The Celestial Expanse: Halcyon Rest, with Tethertown tied on below it.
    "Celestial Expanse": (["celestial_expanse"], ["halcyon_rest"], {}),
    # The Anchorfields: Keelstone, with the House of Measures' reading room and Tiltside's Earthborn in it.
    "Anchorfields": (["anchorfields"], ["keelstone"], {}),
    # The Ascendant Bastions: Dawnspear Wreck. The Yard Pens stay a camp of their own because the conscripts are held
    # there (Kyle, 22 Nov 2026: "Keep the pens as is"), so this one floor sits under 70% by his call.
    "Ascendant Bastions": (["ascendant_bastions"], ["dawnspear_wreck"], {}),
    # The Fading Firmament: Lastlight, with the House of Long Memory's rooms moved in from Forgewatch.
    "Fading Firmament": (["fading_firmament"], ["lastlight"], {}),
    # The Sunward Crown: Lenswatch (with the Annex and the survey's scholars) and Spearhold, the trolls' camp on its own
    # small map (Kyle: "Tiny camp, no hearth or flight. But seperate map").
    "Sunward Crown": (["sunward_crown", "lenswatch"], ["lenswatch", "spearhold"], {}),
    # ---- 22 Nov 2026, the World Tree's boughs (Kyle: "Actually, no we do need hubs in the boughs"): each tier's village
    # is its own map. The Lower Boughs: Mossroof, up the ladders off the ledge.
    "Lower Boughs": (["lower_boughs"], ["mossroof"], {}),
    # The Middle Boughs: Heartwatch, the shadow hunters' hold off the outpost platform.
    "Middle Boughs": (["middle_boughs"], ["heartwatch"], {}),
    # The Upper Boughs: Highrest, through the gate on the far side of its platform.
    "Upper Boughs": (["upper_boughs"], ["highrest"], {}),
}
#: the share of a region's quests that must come from town. Never lower one.
FLOORS = {"Durotar": 0.70, "Tirisfal": 0.70, "Silverpine": 0.70, "Barrens": 0.70, "Hillsbrad": 0.70,
          "Arathi": 0.70, "Felwood": 0.70, "Tempest": 0.70, "Underdark": 0.70,
          "Fenris Isle": 0.70, "Stranglethorn": 0.70, "Stonetalon": 0.70, "Ashenvale": 0.70, "Black Strand": 0.70,
          "Plaguelands": 0.70, "Thousand Needles": 0.70, "Tanaris": 0.70, "Aspen": 0.70, "Echo Isles": 0.70,
          "Celestial Expanse": 0.70, "Anchorfields": 0.70,
          "Ascendant Bastions": 0.55, "Fading Firmament": 0.70,
          "Sunward Crown": 0.70, "Lower Boughs": 0.70, "Middle Boughs": 0.70, "Upper Boughs": 0.70}


def norm(s):
    return (s or "").lower().replace(" ", "_").replace("'", "")


def main():
    people = {}
    for n in json.loads(Path("data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]:
        people[n["npc_id"]] = n
    for v in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]:
        people.setdefault(v["vendor_id"], v)
    quests = [q for f in sorted(glob.glob("data/quests/*.json"))
              for q in json.loads(Path(f).read_text(encoding="utf-8"))["quests"]]

    bad = []
    for region, (qzones, hubs, inner) in REGIONS.items():
        town = wild = 0
        wild_givers = Counter()
        for q in quests:
            if norm(q.get("zone")) not in qzones:
                continue
            g = q.get("giver_npc_id") or ""
            if g.startswith("item:"):
                continue
            n = people.get(g)
            if n is None:
                bad.append(f"{region}: {q['quest_id']} is given by {g}, who does not exist")
                continue
            z = norm(n.get("zone"))
            in_town = z in hubs or any(abs(n.get("x", -99) - x) + abs(n.get("y", -99) - y) <= r
                                       for x, y, r in inner.get(z, []))
            if in_town:
                town += 1
            else:
                wild += 1
                wild_givers[f"{g} ({z})"] += 1
        total = town + wild
        share = town / total if total else 1.0
        floor = FLOORS.get(region)
        mark = "" if floor is None else (" ok" if share >= floor else " BELOW FLOOR")
        print(f"{region:11} {town:3}/{total:<3} from town ({share:.0%})"
              + (f", floor {floor:.0%}{mark}" if floor else ""))
        if floor is not None:
            for who, k in wild_givers.most_common():
                print(f"              in the wild: {who} x{k}")
            if share < floor:
                bad.append(f"{region}: only {share:.0%} of quests come from town (floor {floor:.0%})")

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nQuest hubs OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
