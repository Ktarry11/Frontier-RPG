"""
Echo Isles quest pass (2026-10-21).  Idempotent: rewrites data/quests/echo_isles.json.

    python3 tools/build_echo_isles_quests.py

MAP (160x160 archipelago)
  Echo Landing village ....... (80,50) centre-north of the main island; piers N (80,8) and S (80,152)
  Troll island (east) ........ reached by the short bridge at (95-113, y59). Kang'ari/Zathra/Jin'zil live in the
                               friendly village at (116-125, 54-60); the hostile Zalazane camps sit on the north
                               trail (134,42) and the south trail (128,69).  Subzone "Troll Camps".
  Wreck Shallows ............. (127-147, 26-46) wading flats between the troll island and the Lost Fleet (NE)
  The Lost Fleet ............. (133-161, 9-35) the dead ships (Captain Morrow)
  Drowned Causeway ........... (120-140, 62-98) a ford running south from the troll island to the Hollow island
  Zalazane's Hollow .......... SE island, cave mouth (141,117); Reef Wrangler Dritt camps at (130,105)
  Naga Ruins ................. (10-42, 36-62) NW island (Warden Ssaleth); Sunken Steps (18-38, 56-82) ford below it
  Sunken Temple Grotto ....... W island, cave mouth (24,98), reached by the bridge at y90; Kesh (36,87), Muzka (32,93)
  Razorjaw Reef / Shallows ... SW (31-64,128-150) and (55-77,112-142) (The Razorjaw)
  Tidal Flats ................ (90-120, 114-138) south-east of the Landing, cay chain; Shellcrusher Kragg
Rewards are hand-crafted with the real stat formulas (secondary stats, ilvl >= 10).
Each giver has ONE chain; rares are paired with trash so the ~6 % roll never stalls a quest.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import item, kill, fetch   # noqa: E402

OUT = ROOT / "data/quests/echo_isles.json"


def boss(target, zone=None):
    o = dict(type="kill_boss", target=target, count=1)
    if zone:
        o["zone"] = zone
    return o


def explore(x, y, radius=8):
    return dict(type="explore", target="echo_isles", target_x=x, target_y=y, radius=radius)


def gather(target, count):
    return dict(type="gather", target=target, count=count)


def quests():
    Q = []
    A = Q.append

    # ============================== RASK'JIN (quartermaster) ==============================
    A(dict(
        quest_id="echo_isles_camp_supplies", title="Building Something Permanent",
        giver_npc_id="echo_isles_camp_quartermaster", zone="echo_isles", level_min=10, level_max=12,
        description=("Rask'jin is trying to turn a landing spot into a camp, and a camp wants a palisade. Sand does not "
                     "hold a post. Reef coral does - the deep-red kind that grows where the current is strongest, "
                     "not the pretty kind in the shallows. The coconut crabs along the beaches drag it up the sand to "
                     "line their burrows, so the quickest way to get it is to get it back off them."),
        objectives=[fetch("sturdy_reef_coral", 6)],
        reward_exp=500, reward_gold=1500,
        accept_text=("Da crabs on da beaches are hoardin' it - big as a kodo's head, shell like a shield. "
                     "Six pieces, mon. Dey'll fight you for it. Dey'll lose."),
        turn_in_text=("Dis is good stock! Palisade goes up by week's end. You didn't have to help build "
                      "somethin' dat's not your home. Dat you did anyway - I notice dat."),
        rewards=[
            item("Reef-Binder's Buckler", "off_hand", "of Stamina", 13,
                 "Two coral slabs bound in sinew. Heavier than it looks and prouder than it is.",
                 "Shield (Sta/Block)", weapon="shield", req=10),
            item("Palisade-Builder's Mallet", "main_hand", "of Striking", 13,
                 "A mallet for driving posts. It also drives opinions.", "Mace (Str/Agi/Sta)", weapon="mace_1h", req=10),
            item("Coralstitch Sandals", "feet", "of the Eagle", 13,
                 "Cloth wrapped on a coral sole. The sea-spirits like them, says Rask'jin, and he is usually right.",
                 "Cloth Boots (Int/Sta)", armor="cloth", req=10),
        ]))

    # ============================== VESSA PALEWIND (lookout) ==============================
    A(dict(
        quest_id="echo_isles_scout_camps", title="Eyes on the Cultists",
        giver_npc_id="echo_isles_camp_lookout", zone="echo_isles", level_min=10, level_max=12,
        next_quest_id="echo_isles_screecher_wings",
        description=("Vessa watches the tree line for a living, and for a week the smoke over the troll island has been "
                     "the wrong colour. The east bridge at the Landing leads to Kang'ari's village, and past it the "
                     "north trail runs to the old Darkspear camps - now Zalazane's. She wants a pair of eyes on the "
                     "north camp before anyone commits to a fight."),
        objectives=[explore(134, 42, 9)],
        reward_exp=430, reward_gold=1100,
        accept_text=("Cross da east bridge, take da trail past Kang'ari's village and keep goin' north to da camp. "
                     "Don't engage. Look, remember, come back. We fight smart on dis one, not angry."),
        turn_in_text=("Dat many? ... Good. Now we know what we're walkin' into. Most people who die out dere die "
                      "because dey walked in blind. Next job's closer to home, and louder."),
        rewards=[
            item("Lookout's Windcloak", "back", "of the Monkey", 13,
                 "Dyed the grey of an overcast sky. You can stand in it for an hour and no one blinks.",
                 "Cloak (Agi/Sta)", armor="cloth", req=10),
            item("Watcher's Spyglass-Bow", "ranged", "of the Marksman", 13,
                 "A short bow with a brass sight she added herself. It is, apparently, not for sale.",
                 "Bow (Agi/Sta/Hit)", weapon="bow", req=10),
            item("Tree-Line Vest", "chest", "of the Seer", 13,
                 "Woven leaf-cloth. It hums faintly when the wind turns.", "Cloth Chest (Int/Sta/MP5)",
                 armor="cloth", req=10),
        ]))
    A(dict(
        quest_id="echo_isles_screecher_wings", title="Wings Over the Tree Line",
        giver_npc_id="echo_isles_camp_lookout", zone="echo_isles", level_min=11, level_max=13,
        description=("Vessa's signal fires keep going out. Isle screechers - green-and-red jungle birds with a voice like "
                     "a knife on a whetstone - nest in the canopy right above her watch-post and mob anything that "
                     "moves. A raptor or two has learned to follow the birds. She is tired of shouting over them."),
        objectives=[kill("Isle Screecher", 6), kill("Bloodtalon Raptor", 3)],
        reward_exp=620, reward_gold=1800,
        accept_text=("Dey nest in da canopy all around da Landing, and da raptors trail dem like dogs. "
                     "Eight birds, four raptors. I want to hear da wind again."),
        turn_in_text="Quiet. Actually quiet. I forgot what dat sounded like. Take one of dese - I made dem for myself.",
        rewards=[
            item("Screecher-Plume Cowl", "head", "of the Wolf", 14,
                 "Bright feathers over supple hide. Birdwatchers call it tasteless. Birds disagree.",
                 "Leather Helm (Agi/Spi)", armor="leather", req=11),
            item("Talon-Wrapped Spear", "main_hand", "of the Tiger", 14,
                 "Raptor talons lashed under the head. It tears as it goes in.", "Polearm (Str/Agi)",
                 weapon="polearm", req=11),
            item("Signal-Fire Amulet", "neck", "of the Invoker", 14,
                 "A charred bead on a thong. Warm when something is coming.", "Necklace (Int/SP/Crit)", req=11),
        ]))

    # ============================== TARNA SWIFTWAVE (fisher) ==============================
    A(dict(
        quest_id="echo_tarna_nets", title="Nets Full of Teeth",
        giver_npc_id="echo_isles_fisher", zone="echo_isles", level_min=10, level_max=12,
        next_quest_id="echo_tarna_kragg",
        description=("The Tidal Flats - the cays south-east of the Landing, where the tide leaves a mile of sand and the "
                     "sea leaves its worst behind - used to be Tarna's best fishing. Now every net comes back torn and every "
                     "ankle comes back stung. Flatfin stingers and burrowing crabs have moved in, and they are not "
                     "interested in sharing."),
        objectives=[kill("Flatfin Stinger", 6), kill("Sand Burrower", 5)],
        reward_exp=600, reward_gold=1700,
        accept_text=("Walk south from da Landing till da sand goes grey and da water goes to your shins. "
                     "Stingers first - dey hide under da silt. Den da burrowers. Watch your feet, hear?"),
        turn_in_text=("Dat's two good tides of fishing I got back. Not safe yet - da big one's still out dere - "
                      "but you've earned a pick off my best work."),
        rewards=[
            item("Stingray-Barb Dirk", "main_hand", "of the Bandit", 13,
                 "A stingray's barb on a bone grip. It is nasty and it knows it.", "Dagger (Agi/Sta/AP)",
                 weapon="dagger", req=10),
            item("Tarna's Tideproof Waders", "legs", "of the Whale", 13,
                 "Oiled hide that has never once been dry on the inside. Strangely, that is the point.",
                 "Leather Legs (Sta/Spi)", armor="leather", req=10),
            item("Net-Weaver's Wrist-Cords", "wrist", "of the Owl", 13,
                 "Knotted by a woman who has had a lot of time to practise.", "Cloth Bracers (Int/Spi)",
                 armor="cloth", req=10),
        ]))
    A(dict(
        quest_id="echo_tarna_kragg", title="The Shell That Ate the Skiff",
        giver_npc_id="echo_isles_fisher", zone="echo_isles", level_min=11, level_max=13,
        description=("Tarna lost a skiff last month, and she is certain it was not the tide. Something the size of a "
                     "hut lives under the cays - a crab, she says, grown for forty years on the flats' leavings. "
                     "Shellcrusher Kragg takes the whole boat when it's feeling hungry and lets the fisherman swim. "
                     "Tarna wants a trophy. And her skiff's anchor."),
        objectives=[kill("Sand Burrower", 5), boss("Shellcrusher Kragg")],
        reward_exp=860, reward_gold=2500,
        accept_text=("He comes up when da trailing crabs go quiet. Kill his courtiers and he'll come lookin'. "
                     "Don't try to out-wait him - he's patient. Hit him from da side, mon, not da front."),
        turn_in_text=("Ha! Forty years of crab, and he went down like a bad knot. My anchor?! Oh, you found it. "
                      "Take whatever you like off his shell, I got what I wanted."),
        rewards=[
            item("Kragg-Shell Greathelm", "head", "of the Defender", 15,
                 "The carapace is half an inch thick and still not yielding.", "Plate Helm (Sta/Def/Dodge)",
                 armor="plate", req=11, rarity="rare"),
            item("Flatwalker's Harpoon", "ranged", "of the Hunt", 15,
                 "A long barbed harpoon that throws like a spear and reels in like a promise.",
                 "Thrown (Agi/Int/AP)", weapon="thrown", req=11, rarity="rare"),
            item("Brinebound Prayer-Beads", "neck", "of the Restorer", 15,
                 "Shell beads strung by the sea. Tarna says every one of them is a drowned name.",
                 "Necklace (Healing/MP5)", req=11, rarity="rare"),
        ]))

    # ============================== TALRA SALTBRAID (net mender) ===========================
    A(dict(
        quest_id="echo_talra_cord", title="Good Cord Is Hard to Find",
        giver_npc_id="echo_isles_net_mender", zone="echo_isles", level_min=11, level_max=13,
        description=("Hemp rots, sinew snaps, and the sea does not care. The only cord that has ever outlasted a Darkspear "
                     "storm is cured eel-hide, and the best eels on the archipelago are the bilge eels of Wreck "
                     "Shallows - the knee-deep flats between the troll island and the Lost Fleet, in the far "
                     "north-east. Talra's hands ache, and she is out."),
        objectives=[fetch("eel_hide_cord", 6)],
        reward_exp=670, reward_gold=1900,
        accept_text=("Take da east bridge, go through da troll village, past da north camp, and wade north-east till da water "
                     "goes to your knees. Da wreck crabs will pester you. Da eels will shock you. "
                     "Six good lengths of cord. I'll know if you cheat."),
        turn_in_text=("Oh, that's lovely. Smooth as silk and mean as a snake. I'll mend every net on the Landing with "
                      "this. And I'll make you something with what's left over."),
        rewards=[
            item("Eel-Hide Jerkin", "chest", "of the Monkey", 14,
                 "Supple, slick, and surprisingly warm. The eels would be upset.", "Leather Chest (Agi/Sta)",
                 armor="leather", req=11),
            item("Saltbraid Fishing-Knife", "main_hand", "of the Duelist", 14,
                 "A stout little blade for cutting line. Also for cutting other things.",
                 "Dagger (Dodge/Parry)", weapon="dagger", req=11),
            item("Mender's Lucky Coin-Charm", "neck", "of the Physician", 14,
                 "A pierced coin on a braided cord. It was never spent. It was loved.", "Necklace (Sta/Int/Healing)",
                 req=11),
        ]))

    # ============================== ELDER TIDECALLER VASHJ (spirit elder) ==================
    A(dict(
        quest_id="echo_vashj_stones", title="Voices in the Drowned Stone",
        giver_npc_id="echo_isles_spirit_elder", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_vashj_scales",
        description=("The spirits of the Landing have been restless for a month. Vashj hears them every night from the "
                     "north-west: low, rhythmic, not unfriendly - the voices of something standing guard over "
                     "something old. The Naga Ruins, on the north-west island: over the west bridge to the Grotto isle, up its north trail and across the Sunken Steps ford. "
                     "She does not ask you to fight. Just to stand in the old stones and hear what she hears."),
        objectives=[explore(24, 48, 9)],
        reward_exp=770, reward_gold=2100,
        accept_text=("Cross da west bridge to da Grotto isle, follow da north trail and wade da Sunken Steps to da naga isle. "
                     "Stand in da middle of dem and listen. Don't talk. Don't take anything. Just listen."),
        turn_in_text=("So dey spoke to you too. Not in words. In order. Dey're guarding somethin' - and dey are "
                      "afraid of what comes after dem. Let me think about dis. Come back when you're ready for "
                      "da next part."),
        rewards=[
            item("Tidecaller's Spiral-Wand", "ranged", "of the Archmage", 15,
                 "A hand's length of lacquered coral with a spiral cut round it. It sings very softly in the wet.",
                 "Wand (Int/SP/MP5)", weapon="wand", req=12, rarity="rare"),
            item("Vashj's Salt-Cord Belt", "waist", "of the Whale", 15,
                 "Knotted in the Landing's old style. The knots are the prayer.", "Leather Belt (Sta/Spi)",
                 armor="leather", req=12, rarity="rare"),
            item("Echo-Stone Greaves", "legs", "of the Soldier", 15,
                 "Grey stone greaves with a faint ring to them. You can hear the ruins in your steps.",
                 "Mail Legs (Str/Sta/Crit)", armor="mail", req=12, rarity="rare"),
        ]))
    A(dict(
        quest_id="echo_vashj_scales", title="What the Tide Remembers",
        giver_npc_id="echo_isles_spirit_elder", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_vashj_warden",
        description=("Vashj can read the old runes if she has something to read them off. The nagas wear them: tide-etched "
                     "scales, each marked with a spiral that is half writing and half weather. Six of them and she may "
                     "finally understand what the guards are protecting - and what they are afraid of."),
        objectives=[fetch("tide_etched_scale", 6)],
        reward_exp=820, reward_gold=2300,
        accept_text=("Da coastguards and tidecallers wear dem. Take dem from da ones who don't need dem anymore. "
                     "Six scales. And please - wash your hands afterwards."),
        turn_in_text=("... it is a seal. Dey are not guardin' da temple. Dey're guardin' da door under da temple, "
                      "and Ssaleth is da key-keeper. Dat's da name, mon: Warden Ssaleth. End him and da door "
                      "stays shut."),
        rewards=[
            item("Runereader's Sash", "waist", "of the Prophet", 15,
                 "A cloth sash worked with sixty runes. Vashj spent a year on it and gave it away in a minute.",
                 "Cloth Belt (Int/Spi/Healing)", armor="cloth", req=12, rarity="rare"),
            item("Scale-Etched Hauberk", "chest", "of the Beast", 15,
                 "Overlapping scales with tide-runes. It looks borrowed. It acts inherited.",
                 "Mail Chest (Str/Agi/Sta)", armor="mail", req=12, rarity="rare"),
            item("Spiral-Carved Mace", "main_hand", "of the Squire", 15,
                 "A short mace carved with a spiral from end to end. Every blow feels slightly like a wave.",
                 "Mace (Str/Sta/Hit)", weapon="mace_1h", req=12, rarity="rare"),
        ]))
    A(dict(
        quest_id="echo_vashj_warden", title="The Warden's Oath",
        giver_npc_id="echo_isles_spirit_elder", zone="echo_isles", level_min=13, level_max=15,
        description=("Warden Ssaleth keeps the Naga Ruins the way a lock keeps a door: not out of hatred but out of "
                     "oath. Vashj can feel the oath, and she can also feel that it is fraying. If he falls, the door "
                     "stays shut a while longer. If he is ignored, someone with worse manners will come along."),
        objectives=[kill("Naga Coastguard", 5, alt=["Naga Tidecaller"]), boss("Warden Ssaleth")],
        reward_exp=1200, reward_gold=3500,
        accept_text=("Go back to da ruins, thin da guard and find Ssaleth. He stands where da stones are highest. "
                     "His trident cuts, and when you stand still he weakens you. Keep moving, don't stand in da water."),
        turn_in_text=("Da stones are silent. Not gone - silent. I haven't heard dat in years. "
                      "You've bought us a season, at least. Dis is for you, from da Landing."),
        rewards=[
            item("Ssaleth's Warden-Pike", "main_hand", "of the Champion", 16,
                 "A coral pike, spiral-fluted, built for a naga hand and surprisingly well balanced for a human one.",
                 "Polearm (Str/Sta/Defense)", weapon="polearm", req=13, rarity="rare"),
            item("Hood of the Drowned Rites", "head", "of the Mind's Eye", 16,
                 "A cowl embroidered with an old naga rite. It does not itch. It remembers.",
                 "Cloth Helm (Int/SP/Hit)", armor="cloth", req=13, rarity="rare"),
            item("Tide-Warden Spaulders", "shoulder", "of the Hunt", 16,
                 "Scale pauldrons that shed water. Good for hunters in a wet country.", "Mail Shoulders (Agi/Int/AP)",
                 armor="mail", req=13, rarity="rare"),
            item("Oathkeeper's Band", "ring", "of the Defender", 16,
                 "A ring for someone who finishes what they start.", "Ring (Sta/Def/Dodge)", req=13, rarity="rare"),
        ]))

    # ============================== ELDER KANG'ARI (troll elder) - the main chain =========
    A(dict(
        quest_id="echo_isles_beast_cull", title="The Isle Bites Back",
        giver_npc_id="echo_isles_troll_elder", zone="echo_isles", level_min=10, level_max=12,
        next_quest_id="echo_isles_cultist_purge",
        description=("Elder Kang'ari doesn't waste words on the beasts of Echo Isles - raptors, panthers, serpents, "
                     "screechers and coconut crabs as big as a pot, all of them thick in the interior now that "
                     "Zalazane's fires have driven them out of the north. The trail between the Landing and the troll "
                     "village is not safe to walk. Before anything else gets sorted out on this island, the road "
                     "needs clearing."),
        objectives=[kill("Bloodtalon Raptor", 8, alt=["Jungle Panther", "Isle Serpent", "Isle Coconut Crab",
                                                      "Isle Screecher"])],
        reward_exp=670, reward_gold=2000,
        accept_text=("Ten of dem, any mix - raptor, panther, serpent, crab, bird. Da interior's thick with all of dem. "
                     "Nothin' personal in dis one. Just clearin' ground. Come back when da road is walkable."),
        turn_in_text=("Good. Da trail's quieter now. Not safe - dis island hasn't been safe in longer than you'd guess "
                      "- but quieter. Now. About what's really wrong with dis place."),
        rewards=[
            item("Bloodtalon Fang Blade", "main_hand", "of the Assassin", 13,
                 "A raptor's foreclaw, hafted on a bone grip. Faster than it looks.", "Dagger (Agi/Hit/Crit)",
                 weapon="dagger", req=10),
            item("Panther-Hide Wraps", "hands", "of the Falcon", 13,
                 "Soft, quiet, a little snarly around the cuffs.", "Leather Gloves (Agi/Int)", armor="leather",
                 req=10),
            item("Serpent-Scale Waistguard", "waist", "of the Bear", 13,
                 "Small interlocking scales; surprisingly tough, surprisingly light.", "Mail Belt (Str/Sta)",
                 armor="mail", req=10),
        ]))
    A(dict(
        quest_id="echo_isles_cultist_purge", title="The Camps Answer For It",
        giver_npc_id="echo_isles_troll_elder", zone="echo_isles", level_min=12, level_max=13,
        next_quest_id="echo_isles_relic_recovery",
        description=("The hostile Darkspear camps sit north and south of Kang'ari's village, on the troll isle's two "
                     "trails. Voodoo trolls, hex trolls, Zalazane's berserkers, headhunters and fetish-carvers: all "
                     "of them Darkspear once, all of them lost to whatever hold Zalazane has over them now. Kang'ari "
                     "doesn't ask you to feel good about this fight. He asks you to finish it."),
        objectives=[kill("Voodoo Troll", 9, alt=["Hex Troll", "Zalazane Berserker", "Isle Headhunter",
                                                 "Zalazane Fetish-Carver"])],
        reward_exp=860, reward_gold=2600,
        accept_text=("Twelve of dem. I won't lie to you about what dat means - every one of dem used to be someone's "
                     "kin. Do it anyway. Dey're not comin' back from what he did to dem. North trail and south trail - "
                     "start where Vessa's report said."),
        turn_in_text=("It's done. I felt every one of dose losses. Da camps are quiet now. Zalazane still has da Hollow "
                      "in da south-east, and da temple below da west isle's still drowned. But first I need something "
                      "of yours."),
        rewards=[
            item("Hexbreaker's Cleaver", "main_hand", "of the Gladiator", 14,
                 "A cleaver for Zalazane's rank and file. It does not discriminate.", "Axe (Str/Hit/Crit)",
                 weapon="axe_1h", req=12),
            item("Voodoo Adept's Totem-Rod", "main_hand", "of the Tactician", 14,
                 "A fetish-rod taken from a man who deserved better. It hums with a leashed spell.",
                 "Staff (Int/Hit/SP)", weapon="staff", req=12),
            item("Darkspear Hide-Greaves", "legs", "of the Soldier", 14,
                 "Old Darkspear craftwork, retied by someone who remembers how.", "Mail Legs (Str/Sta/Crit)",
                 armor="mail", req=12),
        ]))
    A(dict(
        quest_id="echo_isles_relic_recovery", title="What Zalazane Took",
        giver_npc_id="echo_isles_troll_elder", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_isles_tidelord",
        description=("Before the final push, Kang'ari wants something recovered, not destroyed - hexed Darkspear totems, "
                     "fetishes twisted by Zalazane's magic but not beyond recognizing. The voodoo trolls and hex "
                     "trolls carry them; so do the fetish-carvers who tend the camp fires. He wants to study what was "
                     "done and maybe find a way back for the trolls still lost."),
        objectives=[gather("hexed_darkspear_totem", 5)],
        reward_exp=770, reward_gold=2200,
        accept_text=("Five totems. Bring dem to me, don't touch da magic still on dem if you can help it. "
                     "I've seen what dat kind of hex does to someone who handles it careless."),
        turn_in_text=("Dis tells me more dan I expected. Da hex isn't as permanent as I feared. Dere may be a way back "
                      "for some of dem, someday. Not today. But someday. Keep dat hope wherever you carry hope."),
        rewards=[
            item("Cleansed Totem-Shard Pendant", "neck", "of the Hierophant", 14,
                 "A hexed totem, scrubbed and re-blessed. It smells of smoke and fresh water.",
                 "Necklace (Sta/Spi/Healing)", req=12),
            item("Fetish-Bound Wristguards", "wrist", "of the Beast", 14,
                 "Mail bracers with a small bound fetish. The fetish is polite about it.",
                 "Mail Bracers (Str/Agi/Sta)", armor="mail", req=12),
            item("Darkspear Scribe's Cowl", "head", "of the Sorcerer", 14,
                 "A cloth hood marked with the old Darkspear sigils. Wearing it feels like being remembered.",
                 "Cloth Helm (Int/Sta/SP)", armor="cloth", req=12),
        ]))
    A(dict(
        quest_id="echo_isles_tidelord", title="The Drowned Temple",
        giver_npc_id="echo_isles_troll_elder", zone="echo_isles", level_min=13, level_max=15,
        next_quest_id="echo_isles_zalazane",
        description=("The Sunken Temple Grotto - the western island, cave mouth at the end of the Grotto trail past the "
                     "west bridge - floods with the tide and empties with it, and something ancient has claimed its "
                     "drowned chambers: Tidelord Gharesh, an elemental that Kang'ari suspects Zalazane either "
                     "summoned or simply failed to stop. It guards ground the Darkspear held sacred."),
        objectives=[boss("Tidelord Gharesh", "sunken_temple_grotto")],
        reward_exp=1200, reward_gold=3600,
        accept_text=("Da temple's door is at da end of da west trail, past da bridge. Gharesh moves with da tide - "
                     "strong when da water's high, slower when it's low. Time it right and dis fight is winnable. "
                     "Time it wrong and you're fightin' a flood dat hits back."),
        turn_in_text=("Da temple's quiet. Whatever dat thing was guardin', it's safe now. One name left, mon. "
                      "Da one dat started all of dis."),
        rewards=[
            item("Gharesh's Tidal Core", "off_hand", "of the Archmage", 16,
                 "A fist-sized sphere of moving water. It pulls toward the sea, and so do you.",
                 "Off-hand Orb (Int/SP/MP5)", req=13, rarity="rare"),
            item("Riptide-Forged Bracers", "wrist", "of the Defender", 16,
                 "Plate bracers hammered in a tidal forge. They hold their shape through anything.",
                 "Plate Bracers (Sta/Def/Dodge)", armor="plate", req=13, rarity="rare"),
            item("Spray-Soaked Cloak", "back", "of the Hunt", 16,
                 "A cloak that never quite dries. It makes you feel slightly faster.", "Cloak (Agi/Int/AP)",
                 armor="cloth", req=13, rarity="rare"),
        ]))
    A(dict(
        quest_id="echo_isles_zalazane", title="Zalazane",
        giver_npc_id="echo_isles_troll_elder", zone="echo_isles", level_min=14, level_max=15,
        description=("Zalazane's Hollow is the last of it - the source, the witch doctor who turned his own kin into "
                     "hexed and drowned things rather than lead them honestly. The cave mouth is on the south-east "
                     "island, at the end of the long bridge from the Landing. Kang'ari has waited a long time to say "
                     "this name to someone capable of ending it."),
        objectives=[boss("Zalazane", "zalazanes_hollow")],
        reward_exp=1800, reward_gold=5600,
        accept_text=("He's da strongest hexer I've ever seen, and I've seen a few. He'll try to turn your own party "
                     "against you before he ever raises a weapon himself. Break da hex fast or don't let it land at all. "
                     "Dat's da whole fight, really."),
        turn_in_text=("It's over. Zalazane is finished, and dis island belongs to da livin' again. I've carried dis "
                      "a long time. I don't fully know how to put down a weight dat old, but I suspect I'll figure it "
                      "out startin' today. Take what he had. You've more than earned it."),
        rewards=[
            item("Zalazane's Broken Fetish", "main_hand", "of the Void", 18,
                 "The fetish he channelled his power through, snapped in half. Still warm.",
                 "Staff (SP/Shadow/Arcane)", weapon="staff", req=14, rarity="rare"),
            item("Darkspear Reclamation Circlet", "head", "of the Restorer", 18,
                 "A circlet of beaten bronze with the Darkspear mark. It was returned by the one who earned it.",
                 "Mail Helm (Healing/MP5)", armor="mail", req=14, rarity="rare"),
            item("Witch-Doctor's Bane", "main_hand", "of the Bandit", 18,
                 "A slim curved knife that cuts hexes more than flesh. It does both without complaint.",
                 "Dagger (Agi/Sta/AP)", weapon="dagger", req=14, rarity="rare"),
            item("Hollow-Walker's Bulwark", "off_hand", "of Stamina", 18,
                 "A shield painted in a language only trolls read. The writing says: you shall not pass.",
                 "Shield (Sta/Block)", weapon="shield", req=14, rarity="rare"),
        ]))

    # ============================== ZATHRA VOODOO-EYE (healer) ============================
    A(dict(
        quest_id="echo_zathra_shards", title="A Healer's Debt",
        giver_npc_id="echo_isles_troll_healer", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_zathra_hexweaver",
        description=("Zathra mends what the camps send her: fevers, cuts, curses. The curses are the new part. Every "
                     "victim has the same mark on the skin, a sliver of bone with a Darkspear name carved into it and "
                     "then crossed out. The fetish-carvers make them. If she can see the carving she can find the "
                     "weaver behind it, and if she can find the weaver she can stop treating the symptoms."),
        objectives=[fetch("hex_bone_shard", 6)],
        reward_exp=770, reward_gold=2200,
        accept_text=("Carvers work da camp fires and da deeper dens of da Hollow. Take da shards off dem, don't touch "
                     "da names. Six. I need to read dem together."),
        turn_in_text=("... all one hand. All one rhythm. It's a weaver, mon - someone in da Hollow who stitches dese "
                      "hexes into da bone. I'll tell you where to look. Take dis for da trouble."),
        rewards=[
            item("Zathra's Mending Gloves", "hands", "of the Physician", 14,
                 "Soft, clean, and never quite dry. They remember every fever they have broken.",
                 "Cloth Gloves (Sta/Int/Healing)", armor="cloth", req=12),
            item("Bone-Needle Stiletto", "main_hand", "of the Assassin", 14,
                 "A needle too long for a healer. She uses it for what the needle was meant for.",
                 "Dagger (Agi/Hit/Crit)", weapon="dagger", req=12),
            item("Sunwarden's Totem", "ranged", "of the Restorer", 14,
                 "A palm-sized totem, warm when held. Used to calm the wounded and the nervous.",
                 "Totem (Healing/MP5)", weapon="totem", req=12),
        ]))
    A(dict(
        quest_id="echo_zathra_hexweaver", title="The Weaver Behind the Hex",
        giver_npc_id="echo_isles_troll_healer", zone="echo_isles", level_min=13, level_max=15,
        description=("Mam'toth the Hexweaver sits in his den on the west side of Zalazane's Hollow, below the Sanctum, and ties curses "
                     "into bone. Zathra has treated forty of his victims. She'd like to stop treating them, and the "
                     "only way to do that is to take the loom out of his hands. His adepts will rally round him; "
                     "go through them."),
        objectives=[kill("Voodoo Adept", 5), boss("Mam'toth the Hexweaver", "zalazanes_hollow")],
        reward_exp=1200, reward_gold=3500,
        accept_text=("He's in da west of da Hollow, in a den below Zalazane's own sanctum. Don't let him finish da weave - interrupt him "
                     "if you can, kill him quick if you can't. And bring back what's left of da loom."),
        turn_in_text=("Forty hexes, unmade in one breath. I felt dem go. Dat's da best medicine I've ever tasted. "
                      "Take dis - and remember, mon: da healin' was never da hard part. It's da stoppin'."),
        rewards=[
            item("Hexweaver's Mourning Robe", "chest", "of the Prophet", 16,
                 "A black robe stitched with a hundred names, uncrossed. Zathra personally uncrossed them.",
                 "Cloth Chest (Int/Spi/Healing)", armor="cloth", req=13, rarity="rare"),
            item("Loomcutter's Cleaver", "main_hand", "of the Gladiator", 16,
                 "A heavy cleaver for cutting thread. It cuts other things equally well.",
                 "Axe (Str/Hit/Crit)", weapon="axe_2h", req=13, rarity="rare"),
            item("Spirit-Spun Gauntlets", "hands", "of the Ironfur", 16,
                 "Leather gloves threaded with spirit-silk. They turn blows better than they should.",
                 "Leather Gloves (Sta/Agi/Dodge)", armor="leather", req=13, rarity="rare"),
        ]))

    # ============================== JIN'ZIL (beachcomber) =================================
    A(dict(
        quest_id="echo_jinzil_charts", title="Charts of the Lost Fleet",
        giver_npc_id="echo_isles_troll_beachcomber", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_jinzil_beard",
        description=("Jin'zil walks the beach below the troll village every dawn and has been doing it for thirty years. "
                     "What he found this morning was a chart: drowned, soaked, still legible, washed off one of the dead "
                     "ships of the Lost Fleet in the north-east. He wants the rest of them. Whoever sailed those ships "
                     "knew where the old reefs were, and he suspects the old reefs are where Zalazane's power comes from."),
        objectives=[fetch("waterlogged_chart", 5)],
        reward_exp=770, reward_gold=2200,
        accept_text=("Da Lost Fleet is up north-east, past da shallows. Da drowned crewmen still carry dere charts - "
                     "dey cannot let go of da job. Five. Don't read dem in da rain."),
        turn_in_text=("A ring of islands, and a red cross. It's not a treasure map, mon - it's a warnin'. "
                      "Da man who drew dis was runnin' from somethin'. One of his mates still guards da wreck. "
                      "I'll tell you where."),
        rewards=[
            item("Beachcomber's Weathered Satchel-Cloak", "back", "of the Eagle", 14,
                 "A canvas cloak the colour of sand and seaweed. You are very hard to see.", "Cloak (Int/Sta)",
                 armor="cloth", req=12),
            item("Driftwood Cudgel", "main_hand", "of the Bear", 14,
                 "A length of sea-silvered driftwood with a knot on the end. Honest and heavy.",
                 "Mace (Str/Sta)", weapon="mace_1h", req=12),
            item("Chartreader's Boots", "feet", "of the Falcon", 14,
                 "Light leather boots for someone who has walked a lot of beach.", "Leather Boots (Agi/Int)",
                 armor="leather", req=12),
        ]))
    A(dict(
        quest_id="echo_jinzil_beard", title="Barnacle-Beard's Lantern",
        giver_npc_id="echo_isles_troll_beachcomber", zone="echo_isles", level_min=13, level_max=15,
        description=("The first mate of the Lost Fleet never left his post. Old Barnacle-Beard walks the shallows by the "
                     "wrecks, lantern in one hand, axe in the other, looking for the captain's orders. The crabs "
                     "that infest his flats have gone feral on him. Jin'zil would like the lantern, and the old man "
                     "to rest."),
        objectives=[kill("Wreck Scavenger", 5), boss("Old Barnacle-Beard")],
        reward_exp=1080, reward_gold=3200,
        accept_text=("Wreck Shallows, up north-east. Da crabs gather where he walks. Kill dem and he'll come lookin' for "
                     "da noise. He fights like a man who's already dead. Dat is not a metaphor."),
        turn_in_text=("... He's restin'. I could feel him let go. I'm not a sentimental man, but I'll light dis lantern "
                      "tonight for him, and for da crew. Take whatever you like off his belt."),
        rewards=[
            item("Mate's Boarding Pike", "main_hand", "of the Soldier", 16,
                 "A short boarding pike, hooked at the back to drag a rail. Still tastes of rum.",
                 "Polearm (Str/Sta/Crit)", weapon="polearm", req=13, rarity="rare"),
            item("Lanternbearer's Hood", "head", "of the Hierophant", 16,
                 "A hood with a tiny lantern-hook at the temple. Something warm in the dark.",
                 "Leather Helm (Sta/Spi/Healing)", armor="leather", req=13, rarity="rare"),
            item("Captain's Mate Flintlock", "ranged", "of the Marksman", 16,
                 "An old naval pistol, spotless on the inside. He never did fire it.", "Gun (Agi/Sta/Hit)",
                 weapon="gun", req=13, rarity="rare"),
        ]))

    # ============================== REEF WRANGLER DRITT (goblin salvager) =================
    A(dict(
        quest_id="echo_dritt_salvage", title="Salvage Rights",
        giver_npc_id="echo_isles_goblin_salvager", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_dritt_seer",
        description=("Dritt's plan, as he puts it, is not complicated: get to the Lost Fleet, take what isn't nailed down, "
                     "pay off the creditors. The plan's single flaw is the Drowned Causeway - the knee-deep ford "
                     "that runs north from his camp on the south-east island to the troll isle. Murloc spearfishers "
                     "hold it and sirens sing from the rocks. He cannot cross it. He cannot even look at it."),
        objectives=[kill("Murloc Spearfisher", 6), kill("Causeway Siren", 3)],
        reward_exp=770, reward_gold=2400,
        accept_text=("It's a toll road now, friend, and the toll is MY LIFE. Eight spearfishers, four sirens, "
                     "and I'll make it worth your while. Don't ask where the money's from."),
        turn_in_text=("You, friend, are a miracle. A violent, wet miracle. And a business partner, I hope. "
                      "There's still the seer on the rocks who runs the choir. Come back when you're ready."),
        rewards=[
            item("Dritt's Cutthroat Cutlass", "main_hand", "of the Bandit", 15,
                 "A goblin cutlass. Cheap alloy, expensive attitude.", "Sword (Agi/Sta/AP)", weapon="sword_1h",
                 req=12, rarity="rare"),
            item("Salvager's Rigging Belt", "waist", "of the Monkey", 15,
                 "Pockets on every pocket. A wise goblin carries his own warehouse.", "Leather Belt (Agi/Sta)",
                 armor="leather", req=12, rarity="rare"),
            item("Wrangler's Brass Whistle", "neck", "of the Sorcerer", 15,
                 "A little brass whistle that Dritt promises will call a sea-beast. It calls a bad feeling.",
                 "Necklace (Int/Sta/SP)", req=12, rarity="rare"),
        ]))
    A(dict(
        quest_id="echo_dritt_seer", title="The Seer on the Rocks",
        giver_npc_id="echo_isles_goblin_salvager", zone="echo_isles", level_min=13, level_max=15,
        next_quest_id="echo_dritt_captain",
        description=("Spearfishers are one thing. The thing that sings the sirens into place is another. Seer Sshara "
                     "sits on a rock halfway down the Drowned Causeway and does not let a sailor pass. Dritt says "
                     "she once charmed his entire crew into walking off the end of a pier. He would like to be "
                     "paid back in gold, but will settle for her silence."),
        objectives=[kill("Causeway Siren", 3), boss("Seer Sshara")],
        reward_exp=980, reward_gold=3000,
        accept_text=("Don't listen to her sing. I mean it. Plug your ears. Put wax in your ears. Go deaf. Whatever it "
                     "takes, friend, my crew weren't smart enough and now they're fish."),
        turn_in_text=("Silent! You saved my life and about nine thousand gold in lost cargo. I'll find you a bonus, "
                      "I'm just not quite sure where."),
        rewards=[
            item("Sshara's Siren-Silk Mantle", "shoulder", "of the Elder", 16,
                 "Shimmering silk that sings when it catches the wind. Do not wear in a crowd.",
                 "Cloth Shoulders (Int/Sta/MP5)", armor="cloth", req=13, rarity="rare"),
            item("Seastrand Band", "ring", "of the Gladiator", 16,
                 "A coil of braided brine-pearl. Heavy for a ring and nimble for a weapon.", "Ring (Str/Hit/Crit)",
                 req=13, rarity="rare"),
            item("Causeway Tidewalkers", "feet", "of the Warder", 16,
                 "Studded leather boots that grip wet stone like a crab.", "Leather Boots (Sta/Dodge/Parry)",
                 armor="leather", req=13, rarity="rare"),
        ]))
    A(dict(
        quest_id="echo_dritt_captain", title="The Captain's Strongbox",
        giver_npc_id="echo_isles_goblin_salvager", zone="echo_isles", level_min=13, level_max=15,
        next_quest_id="echo_dritt_hounds",
        description=("With the causeway quiet, Dritt can finally say out loud what the plan was. Captain Morrow went "
                     "down with his ship and his strongbox, and the Lost Fleet's captain still stalks his deck "
                     "in the north-east, dead and unsociable. The strongbox is on his flagship. Dritt wants it. "
                     "Dritt wants it very, very much."),
        objectives=[kill("Drowned Crewman", 5), boss("Captain Morrow")],
        reward_exp=1200, reward_gold=3800,
        accept_text=("North-east, past da troll isle. Da flagship's the big one. He's got a cutlass and a temper "
                     "and probably a grudge. Bring me da strongbox and I'll buy you a drink. Several."),
        turn_in_text=("... it's empty. Is it? No. No, it's not. THERE'S A FALSE BOTTOM! Friend, I'm going to cry "
                      "in a minute. Take your cut, take it all, take the boat."),
        rewards=[
            item("Morrow's Saltstained Epaulets", "shoulder", "of the Juggernaut", 17,
                 "Dress-uniform epaulets, heavy with brass, which has not tarnished. Disgraceful.",
                 "Plate Shoulders (Sta/Armor/Parry)", armor="plate", req=13, rarity="rare"),
            item("Dead Reckoning Compass-Charm", "neck", "of the Mind's Eye", 17,
                 "A brass compass whose needle points at whatever you want to find. The rest is up to you.",
                 "Necklace (Int/SP/Hit)", req=13, rarity="rare"),
            item("Quartermaster's Boarding Axe", "main_hand", "of Striking", 17,
                 "A balanced boarding axe with a hook at the back. It parts a deck rail like paper.",
                 "Axe (Str/Agi/Sta)", weapon="axe_1h", req=13, rarity="rare"),
        ]))
    A(dict(
        quest_id="echo_dritt_hounds", title="A Hound's Worth",
        giver_npc_id="echo_isles_goblin_salvager", zone="echo_isles", level_min=13, level_max=15,
        description=("Dritt's camp sits a stone's throw from Zalazane's Hollow, and every night something in the dark "
                     "whistles up the shadowfang hounds that prowl his perimeter. Houndmaster Gor'tek keeps the kennels "
                     "in the middle of the Hollow, past the Thrall Pens, and the whistle is his. A goblin cannot sleep "
                     "near a whistle like that."),
        objectives=[kill("Shadowfang Guardian", 5), boss("Houndmaster Gor'tek", "zalazanes_hollow")],
        reward_exp=1200, reward_gold=3600,
        accept_text=("Hounds first, so the master comes out. He'll whip his pack into a frenzy - kill him before the "
                     "frenzy sets in, friend, or you'll be buyin' a lot of bandages."),
        turn_in_text=("Dead quiet! The whistle's gone and the hounds are asleep. I haven't slept in two weeks. "
                      "I'm going to sleep for two more. Take dis, with my thanks. And my sympathies for his dogs."),
        rewards=[
            item("Kennelmaster's Chain-Whip", "main_hand", "of the Falcon", 17,
                 "A length of chain and a short grip. The hounds know it by sound alone.", "Fist (Agi/Int)",
                 weapon="fist_weapon", req=13, rarity="rare"),
            item("Hound-Warden's Helm", "head", "of the Squire", 17,
                 "A visored helm with a muzzle-guard. Practical advice from a man who lost his nose.",
                 "Plate Helm (Str/Sta/Hit)", armor="plate", req=13, rarity="rare"),
            item("Shadowfang Pelt Mantle", "shoulder", "of the Wolf", 17,
                 "Hound-pelt, tanned black. It stays dark where the sun does not reach.",
                 "Leather Shoulders (Agi/Spi)", armor="leather", req=13, rarity="rare"),
        ]))

    # ============================== SPIRITWALKER KESH (shaman) ============================
    A(dict(
        quest_id="echo_kesh_pearls", title="Pearls for the Offering",
        giver_npc_id="echo_isles_shaman", zone="echo_isles", level_min=12, level_max=14,
        next_quest_id="echo_kesh_crypt",
        description=("Kesh keeps the spirit-shrine on the Grotto island, a few steps from the temple door, and the tide "
                     "has started leaving things on the shrine step that no one placed there. The old offering was "
                     "always a tide-touched pearl: grey, damp, impossible to dry. The spirits are asking again. "
                     "The murlocs and tide-spirits inside the temple hold the only pearls left."),
        objectives=[fetch("tide_touched_pearl", 5)],
        reward_exp=770, reward_gold=2200,
        accept_text=("Go in at da temple door, mon, at da end of da Grotto trail. Da murlocs hoard dem in da shallows and da "
                     "tidal elementals wear dem like bad jewellery. Five pearls. Keep dem wet."),
        turn_in_text=("Five. Perfect. Da tide is already softer. Dese pearls are why da temple's guardians never left. "
                      "Dey're still lookin' for da last offering. Dere's a drowned warrior down dere who needs rest."),
        rewards=[
            item("Kesh's Spirit-Tide Beads", "neck", "of the Prophet", 14,
                 "Tide-worn beads on a thong. They taste faintly of salt and rain.", "Necklace (Int/Spi/Healing)",
                 req=12),
            item("Spiritwalker's Driftwood Staff", "main_hand", "of Nature's Wrath", 14,
                 "A driftwood staff with a pearl in the crook. Greener than it should be.", "Staff (Nature SP)",
                 weapon="staff", req=12),
            item("Shrine-Keeper's Hide Vest", "chest", "of the Tiger", 14,
                 "Thick hide, sewn tight. It smells of wet fur and woodsmoke.", "Leather Chest (Str/Agi)",
                 armor="leather", req=12),
        ]))
    A(dict(
        quest_id="echo_kesh_crypt", title="The Restless Below",
        giver_npc_id="echo_isles_shaman", zone="echo_isles", level_min=13, level_max=15,
        description=("In the Drowned Crypt, off the west gate of the Sunken Temple Grotto's rotunda, a Darkspear warrior called Moj'bashi "
                     "has been walking the same tide-flooded corridor for forty years. He is not malicious. He is "
                     "not sane either. The drowned trolls with him have followed his example. Kesh's offering does "
                     "not take until the crypt is quiet."),
        objectives=[kill("Drowned Troll", 5, zone="sunken_temple_grotto"),
                    boss("Moj'bashi the Drowned", "sunken_temple_grotto")],
        reward_exp=1080, reward_gold=3200,
        accept_text=("Da crypt is off da west gate of da rotunda. He'll be at da back, mon. Treat him as a "
                     "warrior, not a monster - he'd want dat. And bring him peace as quick as you can."),
        turn_in_text=("He's at rest. I felt it as he went, like a held breath comin' out. Dat's what da pearls were for. "
                      "Take dis - da shrine and I are even."),
        rewards=[
            item("Moj'bashi's Last Brineblade", "main_hand", "of the Duelist", 16,
                 "A Darkspear short sword, tide-polished. It parries as if it remembered something.",
                 "Sword (Dodge/Parry)", weapon="sword_1h", req=13, rarity="rare"),
            item("Crypt-Warden's Mail Coif", "head", "of the Beast", 16,
                 "A coif of tide-rusted rings, mended with kelp-silk. Heavier than it looks.",
                 "Mail Helm (Str/Agi/Sta)", armor="mail", req=13, rarity="rare"),
            item("Tidepool Dreamer's Robes", "chest", "of the Seer", 16,
                 "A robe of sea-dyed cloth. Anyone who sleeps in it dreams of the temple.",
                 "Cloth Chest (Int/Sta/MP5)", armor="cloth", req=13, rarity="rare"),
        ]))

    # ============================== KELP-DIVER MUZKA (young diver) ========================
    A(dict(
        quest_id="echo_muzka_steps", title="A Dare on the Sunken Steps",
        giver_npc_id="echo_isles_young_diver", zone="echo_isles", level_min=11, level_max=13,
        next_quest_id="echo_muzka_razorjaw",
        description=("Muzka says he can hold his breath for four minutes. The Sunken Steps - a stair of old black "
                     "stone that rises from the knee-deep water south of the Naga Ruins, between his island and the "
                     "naga's - are where he has been proving it. The steps are guarded by slab-like sentinels, and "
                     "the murloc spearfishers have taken an interest. He wants a witness."),
        objectives=[explore(28, 69, 8), kill("Stepstone Sentinel", 5)],
        reward_exp=600, reward_gold=1800,
        accept_text=("From da Grotto isle take da north trail into da water. Da steps are right below. Reach da middle "
                     "step, break six sentinels, come back and tell me I'm brave."),
        turn_in_text=("You did it! You actually did it! Now I can say I know someone who did it. "
                      "Which is nearly as good. Okay - I need to tell you about my brother."),
        rewards=[
            item("Diver's Pearl-Knife", "main_hand", "of the Monkey", 13,
                 "A diver's knife with a pearl-inlaid hilt. The edge has never left the water.",
                 "Dagger (Agi/Sta)", weapon="dagger", req=11),
            item("Kelpweave Leggings", "legs", "of the Falcon", 13,
                 "Woven from three kinds of kelp. They stay cool and never tangle.", "Leather Legs (Agi/Int)",
                 armor="leather", req=11),
            item("Steps-Walker's Charm", "neck", "of the Elder", 13,
                 "A black stone from the stair. It makes the water feel a little less deep.",
                 "Necklace (Int/Sta/MP5)", req=11),
        ]))
    A(dict(
        quest_id="echo_muzka_razorjaw", title="What Took My Brother's Leg",
        giver_npc_id="echo_isles_young_diver", zone="echo_isles", level_min=12, level_max=14,
        description=("Muzka's older brother dove the southwestern reef and came back with half a leg. The thing that took "
                     "it is called the Razorjaw: a great reef predator that has ruled the south-west for a decade, "
                     "that circles the shallows below the Razorjaw Reef island when blood is in the water. "
                     "Muzka does not want revenge. He wants it to stop."),
        objectives=[kill("Razorjaw Whelp", 5, alt=["Razorjaw Lurker", "Reef Stalker"]), boss("The Razorjaw")],
        reward_exp=1180, reward_gold=3400,
        accept_text=("Go down the south trail till da water, den west across da shallows. His whelps hunt in packs and "
                     "he comes when dey scream. He hits hard, and he gets angrier as it goes. Hit and move, mon."),
        turn_in_text=("... It's really gone? I didn't think anyone could. Thank you. Thank you from my brother too. "
                      "He's going to be insufferable, now."),
        rewards=[
            item("Razorjaw Tooth Hatchet", "main_hand", "of the Gladiator", 16,
                 "A tooth the size of a hand, hafted. Cuts like it still wants to.", "Axe (Str/Hit/Crit)",
                 weapon="axe_1h", req=12, rarity="rare"),
            item("Reef-Hunter's Scale Shirt", "chest", "of the Hunt", 16,
                 "Scale from a reef predator, stitched to leather. Light, flexible, and quite hard to hit.",
                 "Mail Chest (Agi/Int/AP)", armor="mail", req=12, rarity="rare"),
            item("Brother's Mending Pendant", "neck", "of the Restorer", 16,
                 "A pendant his brother carved while the leg healed. It has a gentle effect.",
                 "Necklace (Healing/MP5)", req=12, rarity="rare"),
        ]))
    return Q


def main():
    Q = quests()
    out = []
    ids = set()
    for q in Q:
        assert q["quest_id"] not in ids, q["quest_id"]
        ids.add(q["quest_id"])
        rewards = q.pop("rewards")
        q["unique_item_defs"] = rewards
        q["gear_reward_gear_level"] = max(r["item_level"] for r in rewards)
        if max(r["item_level"] for r in rewards) >= 15:
            q["gear_reward_rarity"] = "rare"
        q.setdefault("next_quest_id", None)
        out.append(q)
    for q in out:
        n = q["next_quest_id"]
        assert n is None or n in ids, (q["quest_id"], n)
    OUT.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n")
    print("echo quests:", len(out), "items:", sum(len(q["unique_item_defs"]) for q in out))


if __name__ == "__main__":
    main()
