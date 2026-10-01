"""
One-time content-addition script (Kyle's ask, 2026-09-05): expands ambient
NPC population in the Durotar starter cluster (Valley of Trials, Durotar,
Razor Hill, Echo Isles) roughly 3x - from 12 total across the 4 zones to
~40. Race distribution follows the EXISTING ZONE_POPULATION_MIX proportions
in world/race_registry.py (orc-dominant, goblin secondary, small blood_elf/
human presence, skeleton flavor in Echo Isles) rather than inventing new
ratios - this is filling out an already-designed population mix, not
redesigning it.

Coordinates were chosen to spread across each zone's real named
areas/subzones from zone_generator.py (Thunder Ridge, Skull Rock Approach,
Rocktusk Farm-adjacent, the Razor Hill town square, etc.) rather than
randomly scattered, so NPCs cluster where the geography/lore suggests
people would actually be. All positions get carved walkable automatically
by ZoneManager._place_ambient_npc_tiles (added alongside this script -
see its docstring for why that carving didn't exist before and was a
real gap, not a defensive no-op).

Run once. Appends to the existing "npcs" list in ambient_npcs.json rather
than replacing it - safe to inspect the diff before running if unsure.
"""
import json

NEW_NPCS = [
    # ================= VALLEY OF TRIALS =================
    # Existing: vot_greeter (60,25), vot_guard_1 (55,30), vot_elder (65,35)
    # Mix: orc 85%, goblin 10%, skeleton 5%
    {"npc_id": "vot_recruit_watcher", "name": "Grulnok", "zone": "valley_of_trials",
     "x": 58, "y": 40, "race": "orc", "gender": "male", "appearance_variant": 1, "facing": "down",
     "greeting": "You'll want to keep an eye on the ridge line. Boars don't usually wander this close to the fire."},
    {"npc_id": "vot_goblin_tinkerer", "name": "Fizzcrank Sprocketspin", "zone": "valley_of_trials",
     "x": 63, "y": 42, "race": "goblin", "gender": "male", "appearance_variant": 0, "facing": "left",
     "greeting": "Don't touch that. It's not finished. It also might be a little bit on fire."},
    {"npc_id": "vot_orc_mother", "name": "Rhaka", "zone": "valley_of_trials",
     "x": 50, "y": 45, "race": "orc", "gender": "female", "appearance_variant": 3, "facing": "right",
     "greeting": "My son went up the ridge to prove himself last week. He came back. That's all I ask of this place."},
    {"npc_id": "vot_wounded_grunt", "name": "Torgak", "zone": "valley_of_trials",
     "x": 70, "y": 38, "race": "orc", "gender": "male", "appearance_variant": 5, "facing": "down",
     "greeting": "Scorpid got me good before I put it down. Nakhtar says I'll live. I believe her more than I believe my leg."},
    {"npc_id": "vot_skeleton_curiosity", "name": "Unmoving Remains", "zone": "valley_of_trials",
     "x": 72, "y": 50, "race": "skeleton", "gender": "male", "appearance_variant": 0, "facing": "up",
     "greeting": "It doesn't move. It doesn't speak. Someone should probably ask the Farseer why it's just... standing there."},
    {"npc_id": "vot_young_orc", "name": "Grosk the Younger", "zone": "valley_of_trials",
     "x": 55, "y": 48, "race": "orc", "gender": "male", "appearance_variant": 2, "facing": "left",
     "greeting": "Someday I'm going to walk out of this valley and never look back at the boars again."},

    # ================= RAZOR HILL =================
    # Existing: guard_1 (37,20), smith (39,20), trainer (35,20), innkeep (36,27)
    # Mix: orc 80%, goblin 10%, blood_elf 5%, human 5%
    {"npc_id": "razorhill_guard_2", "name": "Razor Hill Sentry", "zone": "razor_hill",
     "x": 30, "y": 18, "race": "orc", "gender": "male", "appearance_variant": 4, "facing": "left",
     "greeting": "Watch the north road. That's where trouble comes from, when it comes at all."},
    {"npc_id": "razorhill_guard_3", "name": "Razor Hill Sentry", "zone": "razor_hill",
     "x": 45, "y": 22, "race": "orc", "gender": "female", "appearance_variant": 9, "facing": "right",
     "greeting": "You've got the look of someone fresh out of the Valley. Try not to die on your first walk through town."},
    {"npc_id": "razorhill_goblin_trader", "name": "Kravel Coinsnatch", "zone": "razor_hill",
     "x": 42, "y": 25, "race": "goblin", "gender": "male", "appearance_variant": 1, "facing": "down",
     "greeting": "Everything has a price, friend. Even the conversation. Just kidding. Mostly."},
    {"npc_id": "razorhill_beltelf_scribe", "name": "Aendel Duskrunner", "zone": "razor_hill",
     "x": 33, "y": 30, "race": "blood_elf", "gender": "male", "appearance_variant": 2, "facing": "up",
     "greeting": "I keep the Horde's ledgers here. Someone has to. It certainly isn't going to be the orcs."},
    {"npc_id": "razorhill_human_defector", "name": "Corlan Ashe", "zone": "razor_hill",
     "x": 40, "y": 33, "race": "human", "gender": "male", "appearance_variant": 3, "facing": "left",
     "greeting": "I stopped believing in the Alliance's version of things a long time ago. The Horde took me in when nobody else would."},
    {"npc_id": "razorhill_orc_farmer", "name": "Kagra", "zone": "razor_hill",
     "x": 26, "y": 38, "race": "orc", "gender": "female", "appearance_variant": 6, "facing": "down",
     "greeting": "The soil out here fights you for every root vegetable. I've learned to fight back harder."},
    {"npc_id": "razorhill_child", "name": "Little Snarl", "zone": "razor_hill",
     "x": 37, "y": 29, "race": "orc", "gender": "male", "appearance_variant": 8, "facing": "right",
     "greeting": "When I grow up I'm going to kill a whole cave full of demons by myself. Just watch."},
    {"npc_id": "razorhill_elder_orc", "name": "Grandmother Ulaka", "zone": "razor_hill",
     "x": 48, "y": 32, "race": "orc", "gender": "female", "appearance_variant": 7, "facing": "left",
     "greeting": "I remember when this hill had nothing on it but wind and bones. Look at it now. We built something."},
    {"npc_id": "razorhill_goblin_engineer", "name": "Prizzle Boltwrench", "zone": "razor_hill",
     "x": 44, "y": 19, "race": "goblin", "gender": "female", "appearance_variant": 2, "facing": "down",
     "greeting": "I've got seven inventions in various states of exploding. Statistically, one of them will work eventually."},

    # ================= DUROTAR (open zone) =================
    # Existing: patrol_1 (80,45), traveler (75,55), kid (85,60)
    # Mix: orc 75%, goblin 10%, skeleton 5%, blood_elf 5%, human 5%
    # Spread across the real named layout: Orgrimmar approach (~65,18),
    # Thunder Ridge subzone (55-95,30-60), Skull Rock Approach (96-130,30-76),
    # VoT entrance clearing (~28,145), Razor Hill clearing (~65,100)
    {"npc_id": "durotar_orgrimmar_gate_guard", "name": "Orgrimmar Outrider", "zone": "durotar",
     "x": 65, "y": 22, "race": "orc", "gender": "male", "appearance_variant": 3, "facing": "down",
     "greeting": "The gates of Orgrimmar are close now. Prove yourself worthy before you reach them."},
    {"npc_id": "durotar_thunder_ridge_scout", "name": "Ridgewatch Kurr", "zone": "durotar",
     "x": 58, "y": 35, "race": "orc", "gender": "male", "appearance_variant": 5, "facing": "left",
     "greeting": "Thunder lizards up on the ridge. Slow, but they hit like the ground opening up under you."},
    {"npc_id": "durotar_skull_rock_patrol", "name": "Skull Rock Watcher", "zone": "durotar",
     "x": 100, "y": 40, "race": "orc", "gender": "female", "appearance_variant": 6, "facing": "right",
     "greeting": "Something's wrong out past those rocks. Been wrong for longer than I've been posted here."},
    {"npc_id": "durotar_goblin_prospector", "name": "Gazlowe's Cousin Fitz", "zone": "durotar",
     "x": 90, "y": 50, "race": "goblin", "gender": "male", "appearance_variant": 3, "facing": "down",
     "greeting": "There's a fortune in this dirt somewhere. I just haven't found the exact spot yet. Or any spot, honestly."},
    {"npc_id": "durotar_rocktusk_scout", "name": "Borka the Watchful", "zone": "durotar",
     "x": 45, "y": 70, "race": "orc", "gender": "male", "appearance_variant": 2, "facing": "up",
     "greeting": "The quilboar camp's grown bigger since the thaw. Someone ought to do something about that. Maybe you."},
    {"npc_id": "durotar_skeleton_marker", "name": "Sunbleached Remains", "zone": "durotar",
     "x": 110, "y": 55, "race": "skeleton", "gender": "male", "appearance_variant": 1, "facing": "left",
     "greeting": "Whoever this was, the desert took the rest of the story with them."},
    {"npc_id": "durotar_beltelf_merchant", "name": "Sylthressa Windmourne", "zone": "durotar",
     "x": 72, "y": 60, "race": "blood_elf", "gender": "female", "appearance_variant": 1, "facing": "down",
     "greeting": "I travel between Razor Hill and the coast. Durotar's rough country, but the profit margins are excellent."},
    {"npc_id": "durotar_human_prisoner_convert", "name": "Wyll Marrow", "zone": "durotar",
     "x": 62, "y": 65, "race": "human", "gender": "male", "appearance_variant": 4, "facing": "right",
     "greeting": "I was Alliance once. Then I was a prisoner. Now I'm just someone who chose to stay. Funny how that happens."},
    {"npc_id": "durotar_vot_road_traveler", "name": "Southbound Grekka", "zone": "durotar",
     "x": 32, "y": 130, "race": "orc", "gender": "female", "appearance_variant": 8, "facing": "up",
     "greeting": "Heading down to the Valley to see my nephew off. First trial. Nervous doesn't cover it."},
    {"npc_id": "durotar_razorhill_road_merchant", "name": "Wandering Bok", "zone": "durotar",
     "x": 68, "y": 95, "race": "goblin", "gender": "male", "appearance_variant": 4, "facing": "left",
     "greeting": "Road's clear between here and Razor Hill. Mostly. There was a thing with a vulture yesterday. Don't ask."},

    # ================= ECHO ISLES =================
    # Existing: fisher (50,48), shaman (45,55)
    # Mix: orc 90%, goblin 5%, skeleton 5% (trolls in real WoW but no asset yet)
    {"npc_id": "echo_isles_net_mender", "name": "Talra Saltbraid", "zone": "echo_isles",
     "x": 55, "y": 45, "race": "orc", "gender": "female", "appearance_variant": 4, "facing": "down",
     "greeting": "The nets don't mend themselves, and the sea doesn't care that my hands ache."},
    {"npc_id": "echo_isles_young_diver", "name": "Kelp-Diver Muzka", "zone": "echo_isles",
     "x": 40, "y": 50, "race": "orc", "gender": "male", "appearance_variant": 1, "facing": "right",
     "greeting": "I can hold my breath longer than anyone on this isle. Ask anyone. Well - ask anyone who's still speaking to me."},
    {"npc_id": "echo_isles_goblin_salvager", "name": "Reef Wrangler Dritt", "zone": "echo_isles",
     "x": 60, "y": 60, "race": "goblin", "gender": "male", "appearance_variant": 5, "facing": "left",
     "greeting": "There's a wreck off the north shore worth more than this whole island. I just need a boat. And a crew. And a plan."},
    {"npc_id": "echo_isles_spirit_elder", "name": "Elder Tidecaller Vashj", "zone": "echo_isles",
     "x": 48, "y": 62, "race": "orc", "gender": "female", "appearance_variant": 9, "facing": "up",
     "greeting": "The spirits of this isle remember when it belonged to no one and everyone. Walk gently."},
    {"npc_id": "echo_isles_shipwreck_bones", "name": "Drowned Remains", "zone": "echo_isles",
     "x": 65, "y": 65, "race": "skeleton", "gender": "male", "appearance_variant": 2, "facing": "down",
     "greeting": "Whatever ship this washed off of, it isn't coming back for the rest."},
]


def main():
    path = "data/npcs/ambient_npcs.json"
    d = json.load(open(path))
    before = len(d["npcs"])
    d["npcs"].extend(NEW_NPCS)
    after = len(d["npcs"])
    json.dump(d, open(path, "w"), indent=2)
    print(f"Added {after - before} ambient NPCs ({before} -> {after} total).")

    from collections import Counter
    zone_counts = Counter(n["zone"] for n in NEW_NPCS)
    for zone, count in zone_counts.items():
        print(f"  {zone}: +{count}")


if __name__ == "__main__":
    main()
