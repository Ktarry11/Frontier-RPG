"""
Feralas's quests: the High Wilderness and Camp Mojache, the Forgotten Coast with Cedar Hollow and Feathermoon
Stronghold, the Twin Colossals and the Sentinels' Watch, and the Zukk'ash Hive. Levels 44-49. Read by
tools/build_feralas_quests.py, which holds them to every rule before anything is written. The plan is
docs/feralas_quest_plan.md.

THE THEME: everybody's digging. The silithids are digging down and away toward the Dry Deep. The Hatecrest naga are
digging up the Highborne ruins on the coast, and the Gordunni are digging out Isildien's dome. Latronicus Moonspear
puts it together: the naga and the ogres want the same thing, the way into Eldre'Thalas, which the ogres call Dire
Maul. That sets the dungeon up without opening it.

THE THREADS:
  The refugees: who walked out of Mulgore, the nine names, the Grimtotem on the empty ground, Brann's list going north.
  The dig: Orwin's resin, the mounds in a line, the Zukk'ash Hive, the tunnel through to the Dry Deep and Onyxhollow.
  The Gordunni and the Woodpaw: the camp's hunting grounds, and Krueg's question about the gate.
  The Fog Groves: the settlers of Cedar Hollow under trees from their own world, and Kindal deciding about them.
  The Sentinels and the coast: the Hatecrest, Sardor Isle, the Isle of Dread, Isildien, the hippogryphs.
  The north: Ravenwind, the Rage Scar driven out of their hold, the giants walking, and the Dream Bough.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. Earth comes up from the settlers
on the coast, hardly at all on the east arm.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

# ---- the maps (the key the game passes on a kill: tools zone_key of the map's name)
HW, FC, TC = "high_wilderness", "forgotten_coast", "twin_colossals"
MJ, FM, ZH = "camp_mojache", "feathermoon_stronghold", "zukkash_hive"

# ---- the people: Camp Mojache
CHIEF, HADOKEN, NAYELI, KRUEG = "moj_chieftain", "moj_hadoken", "moj_elder_nayeli", "moj_krueg"
BRANN, ORWIN, TAKODA, GREUL = "moj_brann", "moj_orwin", "moj_gate_brave", "moj_innkeeper"
SHYN, ONAWA, KELE, ISHANA = "moj_flight_master", "pt_moj_hide", "pt_moj_herbs", "ct_mojache"
# ---- Feathermoon Stronghold
SHANDRIS, LATRONICUS, SELARIN, KINDAL = "fm_shandris", "fm_latronicus", "fm_selarin", "fm_kindal"
JALARA, AELYRA, SHYRIA, FYLDREN = "fm_jalara", "fm_harbour_sentinel", "fm_innkeeper", "fm_flight_master"
TAELAN, ELYSSA = "pt_fm_herbs", "pt_fm_fish"
# ---- out on the maps
WAPI, MIRAEL = "fe_scout_wapi", "fe_landing_sentinel"
JUNE, WALT, ROSA, SAM = "fe_settler_june", "fe_settler_walt", "fe_settler_rosa", "fe_settler_sam"
AERWYN, TAHU, SYLANNA = "fe_watch_captain", "fe_watch_tahu", "fe_dreamwatcher"
# ---- elsewhere (turn-ins only)
LONGTREAD, LETHIEL, TORGUN, VIGDIS = "taurajo_elder", "mg_arch_watcher", "org_elder_2", "oh_geomancer"

MOJACHE_GIVERS = {CHIEF, HADOKEN, NAYELI, KRUEG, BRANN, ORWIN, TAKODA, GREUL, SHYN, ONAWA, KELE, ISHANA}
SENTINEL_GIVERS = {SHANDRIS, LATRONICUS, SELARIN, KINDAL, JALARA, AELYRA, SHYRIA, FYLDREN, TAELAN, ELYSSA,
                   MIRAEL, AERWYN}
SETTLER_GIVERS = {JUNE, WALT, ROSA, SAM}
FIELD_GIVERS = {WAPI, MIRAEL, JUNE, WALT, ROSA, SAM, AERWYN, TAHU, SYLANNA}
HUB_GIVERS = MOJACHE_GIVERS | (SENTINEL_GIVERS - {MIRAEL, AERWYN})


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Feralas Stag": [("fe_q_stag_haunch", "Feralas Stag Haunch", "A haunch of lean red venison, wrapped in leaves to "
                      "keep the flies off.")],
    "Ironfur Bear": [("fe_q_ironfur_pelt", "Ironfur Pelt", "A thick dark pelt with a silver sheen down the back. It's "
                      "warm enough to sleep under in the rain.")],
    "Woodpaw Trapper": [("fe_q_woodpaw_snare", "Woodpaw Snare", "A loop of greasy rope tied to a bent stick. The knots "
                         "are better than they have any right to be.")],
    "Lower Wilds Crocolisk": [("fe_q_croc_hide", "Crocolisk Belly Hide", "A strip of soft pale hide from a crocolisk's "
                               "belly, the only part of it a tanner wants.")],
    "Gordunni Ogre Mage": [("fe_q_ogre_scroll", "Scorched Gordunni Scroll", "A scroll an ogre mage was carrying. Most "
                            "of it's burned, and what's left is in a hand much older than any ogre's.")],
    "Zukk'ash Tunneler": [("fe_q_raw_resin", "Lump of Raw Resin", "Amber resin, still soft, with grit and broken "
                           "chitin pressed into it. It smells sweet and wrong.")],
    "Fog Grove Elk": [("fe_q_elk_cut", "Cut of Elk", "A heavy cut of elk, dark red and lean. Walt says it's the best "
                       "meat on either side of the world.")],
    "Feralas Stalker": [("fe_q_spore_fur", "Spore-Matted Fur", "A tuft of a stalker's fur, matted with fine grey "
                         "spores that come off on your fingers like ash.")],
    "Hatecrest Ruin-Digger": [("fe_q_dug_relic", "Dug-Up Relic", "A piece of carved Highborne stone with fresh earth "
                               "still packed into the lines, wrapped in kelp like something precious.")],
    "Isildien Ogre Mage": [("fe_q_dome_page", "Page from the Dome", "A page of Highborne script on something that isn't "
                            "paper. It's ten thousand years old and it doesn't tear.")],
    "Dread Chimaera": [("fe_q_chimaera_scale", "Chimaera Scale", "A hard green scale with a ridge of bone along it. The "
                        "Sentinels use them to count kills.")],
    "Hatecrest Makrura": [("fe_q_makrura_tail", "Makrura Tail Meat", "A pale, sweet length of tail meat in its "
                           "shell. The Sentinels pretend they don't like it.")],
    "Rage Scar Yeti": [("fe_q_singed_fur", "Singed Yeti Fur", "A handful of a yeti's fur, burned at the tips as if "
                        "something hot had come very close.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [3]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=HW, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, on the roads)
# the High Wilderness
DESCENT_FOOT, ARM_FORK, GATE_ROAD = (204, 84), (118, 96), (84, 74)
MOUND_A, MOUND_B, HIVE_MOUTH = (162, 104), (168, 120), (176, 136)
WILDS_BANK, COMPOUND_EDGE, WOODPAW_TOP = (114, 124), (112, 50), (172, 46)
# Camp Mojache
MEMORIAL, GREAT_TOTEM, REFUGE = (34, 40), (62, 56), (24, 26)
# the Forgotten Coast
GROVES_ROAD, HOLLOW, GROVE_SOUTH = (152, 128), (150, 148), (150, 136)
DOME_STEPS, SHORE_CAMP, SARDOR_BAR, DREAD_BAR = (118, 66), (70, 56), (48, 61), (68, 164)
HIGHLANDS, LANDING = (156, 74), (70, 118)
# the Twin Colossals
UNDER_ARCHES, RAGE_SCAR, RAVENWIND, BOUGH, WATCH = (96, 120), (150, 122), (62, 36), (144, 36), (110, 188)


def build():
    out = []
    A = out.append

    # =================================================================================== 1. DOWN OFF THE MOUNTAIN
    A(Q("fe_down_off_the_mountain", "Down Off the Mountain", WAPI, 44, 44, "Wayfinder's",
        "Scout Wapi Longstride watches the foot of the pass for Camp Mojache, and he's had a lot of company come "
        "down it these three years. He wants the chieftain to know the trail's still open.",
        [deliver("fe_q_wapi_knot", "Take Wapi's tally cord to Chieftain Ahanu Swiftstrider in Camp Mojache")],
        "Every knot on that cord is somebody who's come down this trail since the last moon. Take it to Chieftain "
        "Ahanu in Camp Mojache, west along the road and inside the totems. She likes to know how many to cook for.",
        "Four knots this moon. Fewer every month, and I can't tell you whether that's good news or the worst news "
        "there is.\n\nWelcome to Mojache. We've got more mouths than we were built for, but there's always room for "
        "somebody who can hold a weapon.",
        turn_in_npc_id=CHIEF,
        grant_items=carry("fe_q_wapi_knot", "Wapi's Tally Cord", "A cord of braided kodo hair with a knot tied in it "
                          "for every traveller who came down the pass.")))
    A(Q("fe_wolves_on_the_trail", "Wolves on the Trail", WAPI, 44, 44, "Trailguard",
        "The Longtooth Runners have learned that the people coming down off the mountain are tired, and they hunt "
        "the bottom of the pass now. Wapi would like them to learn something else.",
        [k("Longtooth Runner", 8, HW)],
        "The Longtooth Runners wait at the bottom of the descent, where people are too tired to fight. I've buried "
        "two travellers this season who made it over the whole range and died a mile from the camp. Thin them out "
        "for me.",
        "That'll keep them off the trail for a while. Wolves aren't stupid, and they'll find easier hunting "
        "somewhere else.\n\nIf you see anyone coming down after you, point them west."))

    # =================================================================================== 2. THE REFUGEES
    A(Q("fe_twice_the_mouths", "Twice the Mouths", CHIEF, 44, 44, "Mojache",
        "Camp Mojache has fed twice as many tauren as it was built for since the day the world changed and the refugees came south out of Mulgore. "
        "Chieftain Ahanu needs meat, and the Feralas Stags in the forest round the camp are the best of it.",
        [fetch("fe_q_stag_haunch", 8)],
        "When the first of them walked in out of the Needles, I didn't count them, I just opened the gate. Now I "
        "count every meal. Hunt the Feralas Stags in the forest and bring the haunches to Wahya at the cook fires.",
        "That's two nights of stew for the whole camp. Thank you.\n\nThe ones who came from Mulgore won't say "
        "they're hungry. They walked for weeks on nothing, and asking for food feels like begging to them. So I "
        "make sure nobody has to ask.", zone=MJ))
    A(Q("fe_more_bedrolls_than_beds", "More Bedrolls Than Beds", GREUL, 44, 45, "Hearthkeeper's",
        "Innkeeper Greul has had people sleeping on the floor of the inn and under bare poles behind it for three years. The Ironfur "
        "Bears in the forest have the warmest hides in Feralas.",
        [fetch("fe_q_ironfur_pelt", 6)],
        "The rain comes through the lean-tos in the refugees' quarter, and the old ones are starting to cough. "
        "An Ironfur Bear's pelt sheds water like a roof. Bring me what you can and I'll get them stitched into "
        "blankets before the next storm.",
        "These'll keep a whole family dry. I'll have them sewn by morning.\n\nThere's an old bull in there who "
        "won't take a blanket because he says the others need it more. He'll take this one, because I'm going to "
        "tell him you hunted it for him personally.", zone=MJ))
    A(Q("fe_the_nine_names", "The Nine Names", NAYELI, 44, 45, "Cloudhoof",
        "Elder Nayeli Cloudhoof walked out of Mulgore with forty others and reached Mojache with thirty-one. She says "
        "the names of the other nine every night, and she wants someone who wasn't there to stand where she does.",
        [explore(*MEMORIAL, "Stand at the memorial pole in the refugees' quarter", MJ),
         explore(*DESCENT_FOOT, "Stand at the foot of the pass, where the refugees came down", HW)],
        "Go and look at the memorial pole first. Every token on that pole is somebody who didn't get here. Then walk out "
        "to the bottom of the pass on the east road and stand where we came down. I'd like you to see both before "
        "I tell you anything.",
        "So you've seen the start of the road and the end of it.\n\nWe lost the nine in the Needles, not in "
        "Mulgore. Mulgore let us go, and that's what I can't forgive it for. It let us think we'd escaped.",
        nxt="fe_what_the_grimtotem_took", zone=MJ))
    A(Q("fe_what_the_grimtotem_took", "What the Grimtotem Took", NAYELI, 45, 45, "Grieving",
        "While the tauren were dying in Mulgore, the Grimtotem moved onto the empty ground in Feralas. They took the "
        "old hunting lodges and the springs, and they turn the refugees away from them at spearpoint.",
        [k("Grimtotem Usurper", 7, HW), k("Grimtotem Bonecaller", 5, HW)],
        "The Grimtotem Compound north of the arm road was Mojache's hunting camp before the merge. The Grimtotem "
        "Usurpers took it while we were burying our dead, and the Grimtotem Bonecallers hex anyone who comes near "
        "the springs. Drive them back from it.",
        "They'll be back. The Grimtotem always come back. But they'll come back knowing the camp has teeth.\n\n"
        "My mother used to say the Grimtotem were tauren who'd forgotten the Earth Mother. I think they remembered "
        "her perfectly well and decided she owed them something.",
        nxt="fe_harroks_totem"))
    A(Q("fe_harroks_totem", "Harrok's Totem", NAYELI, 45, 46, "Spiritwarden's",
        "Pathfinder Harrok leads the Grimtotem at the compound, and he wears a totem that was carried out of "
        "Thunder Bluff on a refugee's back. The refugee didn't survive the Needles. Harrok found her pack.",
        [k("Pathfinder Harrok", 1, HW)],
        "That totem was carved for the Bloodhoof lodge before I was born. Pathfinder Harrok wears it on his belt "
        "like a trophy. He's in the Grimtotem Compound, and he doesn't go far from it. Bring it back to us.",
        "Wood and paint and old feathers, and it weighs more than anything I've ever carried.\n\nWe'll raise it in "
        "the middle of the camp, beside Mojache's own. That's where it should have been all along.",
        nxt="fe_raise_it_here"))
    A(Q("fe_raise_it_here", "Raise It Here", NAYELI, 46, 46, "Homecoming",
        "Elder Nayeli has raised the Bloodhoof totem beside Mojache's great totem. She wants the camp to see "
        "someone from outside it stand there, so they know it isn't only the refugees who mourn.",
        [explore(*GREAT_TOTEM, "Stand with the camp at the great totem", MJ)],
        "Raising it here means we've stopped waiting to go home. I didn't think I'd ever be ready for that, and I'm "
        "still not sure I am. Come and stand with us at the great totem tonight.",
        "Thank you for coming. The young ones will remember that a stranger stood with us, and that matters more "
        "than you'd think.\n\nThunder Bluff's gone, but Mojache is still standing. We'll build from here.", zone=MJ))
    A(Q("fe_the_list", "The List", BRANN, 45, 46, "Tallgrass",
        "Brann Tallgrass keeps the list of everyone who reached Mojache and everyone they're still looking for. "
        "Elder Longtread at Camp Taurajo keeps another, and the two have never been put side by side.",
        [deliver("fe_q_brann_list", "Take Brann's list to Elder Longtread at Camp Taurajo")],
        "Elder Longtread's been keeping his own list at Camp Taurajo since the fall. Some of the names I'm looking "
        "for might be on his, and some of his might be here. Take him my copy. Ride if you can, because some of "
        "these people have waited three years.",
        "This is Brann's list. I knew the boy's father, and he writes the same careful hand.\n\nSeven names on here are on "
        "mine. Seven people who think the others are dead. I'll have runners on the road to Mojache before "
        "nightfall, and I'll owe you for the rest of my life.",
        turn_in_npc_id=LONGTREAD, zone=MJ,
        grant_items=carry("fe_q_brann_list", "Brann's List", "Pages of names in a careful hand: who reached Mojache, "
                          "where they came from, and who they're still looking for.")))
    A(Q("fe_the_crossed_off_names", "The Crossed-Off Names", BRANN, 45, 45, "Listkeeper's",
        "Brann has started a second page, for the names he's crossed off. He wants to know what happened to the "
        "refugees who tried to hunt the Lower Wilds alone in the first winter.",
        [explore(*WILDS_BANK, "Search the riverbank in the Lower Wilds", HW), k("Lower Wilds Crocolisk", 6, HW)],
        "Three hunters went down to the Lower Wilds in the first winter and didn't come back. I put them on the "
        "crossed-off page, but I never found out how. Search the riverbank, and if the Lower Wilds Crocolisks are "
        "what took them, make the river safer for the next ones.",
        "A spear with a Bloodhoof binding on it, sunk in the mud. That's enough for the list.\n\nI'll write it "
        "down properly tonight. People deserve to have it written down, even when there's nobody left to read it.",
        zone=MJ))

    # =================================================================================== 3. THE WOODPAW
    A(Q("fe_woodpaw_in_the_hills", "Woodpaw in the Hills", HADOKEN, 44, 45, "Hunter's",
        "Hadoken Swiftstrider keeps the camp fed, and the Woodpaw gnolls in the hills north-east of Mojache have "
        "been raiding his hunting grounds since the merge doubled the camp.",
        [k("Woodpaw Reaver", 8, HW), k("Woodpaw Hyena", 5, HW)],
        "The Woodpaw Reavers come down out of their hills with their Woodpaw Hyenas and take whatever my hunters bring "
        "down. They've worked out we're feeding more people and they think that makes us soft. Go up into Woodpaw "
        "Hills and show them otherwise.",
        "That's a lesson they'll remember for a season or two.\n\nGnolls aren't brave, they're hungry. When the "
        "hunting gets hard for them, it gets dangerous for us. Hopefully they'll go and be hungry somewhere else.",
        nxt="fe_snares_on_the_trail", zone=MJ))
    A(Q("fe_snares_on_the_trail", "Snares on the Trail", HADOKEN, 45, 45, "Tracker's",
        "The Woodpaw Trappers have been setting snares on the camp's hunting trails, and one of them caught a "
        "refugee child last week. Hadoken wants every snare they carry taken off them.",
        [fetch("fe_q_woodpaw_snare", 8)],
        "The girl's ankle will heal. My temper won't. The Woodpaw Trappers carry their snares on their belts, so "
        "take them off the trappers in Woodpaw Hills and bring them to me. I'll burn every one where the gnolls "
        "can see the smoke.",
        "There's good rope in these, and I'm burning all of it anyway.\n\nSome things you do because they're "
        "useful. Some you do so the other side understands you.", nxt="fe_the_rattles_go_quiet", zone=MJ))
    A(Q("fe_the_rattles_go_quiet", "The Rattles Go Quiet", HADOKEN, 45, 46, "Packbreaker",
        "With their snares gone, the Woodpaw have pulled back to their camps and their Woodpaw Mystics are "
        "shaking their rattles all night. Hadoken knows what that means: they're working themselves up to come back.",
        [k("Woodpaw Mystic", 6, HW), k("Woodpaw Brute", 4, HW)],
        "When the Woodpaw Mystics start rattling, the Woodpaw Brutes come down the hill a night later. I'd rather "
        "we went up first. Break up the camp before they're ready.",
        "Quiet up there tonight. I can hear the wind in the trees again.\n\nThere's one more of them worth "
        "worrying about, the big one with the spiked club. He'll want to know who did this.", zone=MJ))
    A(Q("fe_grimfang", "Grimfang", HADOKEN, 46, 46, "Grimfang's",
        "Grimfang is the Woodpaw's alpha, bigger and older than the others, and he's taken it personally. "
        "He's been seen near the hilltop camps, hunting alone.",
        [k("Grimfang", 1, HW)],
        "Grimfang leads the Woodpaw, and every scar on him is somebody else's dead hunter. He hunts the tops of "
        "Woodpaw Hills alone now, looking for whoever broke up his pack. Let him find you.",
        "That's Grimfang's club. My father would have mounted it over the lodge door.\n\nI'll put it over mine. The "
        "Woodpaw will see it every time they look at the camp, and they'll think twice.", zone=MJ))

    # =================================================================================== 4. THE LOWER WILDS
    A(Q("fe_belly_hides", "Belly Hides", ONAWA, 45, 45, "Riverhide",
        "Hidewright Onawa Redcloud needs soft leather for the refugees' boots, and the Lower Wilds Crocolisks have "
        "the softest belly hide in Feralas.",
        [fetch("fe_q_croc_hide", 6)],
        "Half the refugees walked here in boots that were falling apart before they left Mulgore. The Lower Wilds "
        "Crocolisks have soft pale hide on their bellies that's perfect for it. Bring me the hides and I'll get "
        "everyone shod before the wet season.",
        "Good clean cuts. You've done this before.\n\nI'll have the children's boots done first. They grow out "
        "of them faster than I can make them, but at least they'll grow out of something.", zone=MJ))
    A(Q("fe_old_grizzlegut", "Old Grizzlegut", ONAWA, 46, 46, "Grizzled",
        "Old Grizzlegut is an Ironfur bear the size of a lodge who fishes the Lower Wilds. Onawa wants his pelt, "
        "and Hadoken's hunters would like him gone from the river.",
        [k("Old Grizzlegut", 1, HW)],
        "Old Grizzlegut's been fishing the Lower Wilds since before Mojache had a palisade. He's killed two of our "
        "hunters, and his pelt would keep a family warm for twenty years. He's down in the marsh where the river "
        "pools.",
        "That's the biggest pelt I've ever tanned, and I've tanned a few.\n\nThe river's safer and a family's "
        "warmer. It's a good day's work.", zone=MJ))
    A(Q("fe_khadgars_whisker", "What Grows by the River", KELE, 44, 45, "Riverbank",
        "Herbalist Kele Windsong has a camp full of coughs and not enough herbs to treat them. Khadgar's Whisker "
        "grows along the Lower Wilds and up into the forest.",
        [gather("herb_khadgar", 8, "Gather Khadgar's Whisker")],
        "The refugees brought the coughing sickness out of the Needles, and it's going round the camp. Khadgar's "
        "Whisker settles the lungs. It grows wild along the river in the Lower Wilds and in the clearings of the "
        "forest. Bring me what you can find.",
        "This'll make enough tea for the whole quarter.\n\nI keep finding plants out here I've never seen before, "
        "growing next to plants I've known all my life. Some of them came over from somewhere else. I'm "
        "trying not to use those yet.", zone=MJ))
    A(Q("fe_darters_at_the_roost", "Darters at the Roost", SHYN, 44, 45, "Windrider's",
        "The Feralas Sprite Darters have taken to diving at the wind riders when they land, and Wind Rider "
        "Master Shyn's mounts are starting to refuse the roost.",
        [k("Feralas Sprite Darter", 8, HW)],
        "The Feralas Sprite Darters think the wind riders are rivals, and they dive at their eyes when they're coming "
        "in to land. Two of my riders have already been thrown. Clear the darters out of the forest round the camp.",
        "My wind riders landed clean this morning for the first time in a week.\n\nThe darters will come back, "
        "they always do. But by then the young wind riders will have stopped flinching.", zone=MJ))

    # =================================================================================== 5. THE GORDUNNI
    A(Q("fe_ogres_on_the_arm_road", "Ogres on the Arm Road", KRUEG, 45, 45, "Warsong",
        "Krueg Skullsplitter has kept Orgrimmar's eye on Camp Mojache since the merge, and the Gordunni ogres at their forward outpost "
        "west of the arm road have started stopping caravans.",
        [k("Gordunni Brute", 8, HW), k("Gordunni Shaman", 4, HW)],
        "The Gordunni Outpost sits west of the gate, and the Gordunni Brutes have been stopping anything on the "
        "road to the coast. The Gordunni Shamans with them aren't stupid, either. Break up the outpost and keep the "
        "road open.",
        "That's good work. The coast caravans can move again.\n\nThe ogres don't usually come out this far from Dire Maul. "
        "Something's moved them. I'd like to know what.", nxt="fe_what_the_mages_carry", zone=MJ))
    A(Q("fe_what_the_mages_carry", "What the Mages Carry", KRUEG, 45, 46, "Gatewatcher's",
        "Krueg has noticed that the Gordunni Ogre Mages carry scrolls, and that ogres don't write. He wants to see "
        "what they're reading.",
        [fetch("fe_q_ogre_scroll", 5)],
        "Every Gordunni Ogre Mage I've killed had a scroll on him, half burned. Ogres can barely read their own "
        "names. Kill the mages at the outpost and round the gate, and bring me what they're carrying.",
        "The writing's Highborne. Old Highborne, older than anything in Orgrimmar's archives.\n\nThe ogres are "
        "copying it out of something. They're trying to work out how to open a door, and I'd bet my axe it's a "
        "door inside Dire Maul.", nxt="fe_the_gate", zone=MJ))
    A(Q("fe_the_gate", "The Gate", KRUEG, 46, 46, "Dire Maul",
        "The Gordunni hold the great gate of Dire Maul in the middle of the arm, and they've barricaded it with "
        "tree trunks and chains. Krueg wants to know whether they're keeping people out or keeping something in.",
        [explore(*GATE_ROAD, "Look at the barricade on the gate of Dire Maul", HW),
         k("Gordunni Mauler", 5, HW), k("Gordunni Warlord", 4, HW)],
        "Go and look at the gate of Dire Maul, and get close. The Gordunni Maulers and the Gordunni Warlords guard it "
        "day and night, so you'll have to go through them to see the barricade properly. Tell me which way the "
        "chains face.",
        "The chains face inward, then.\n\nThey're not keeping us out. They're keeping something in, or they "
        "were until they decided they wanted it. Orgrimmar needs to hear this.", nxt="fe_report_to_orgrimmar"))
    A(Q("fe_report_to_orgrimmar", "Report to Orgrimmar", KRUEG, 46, 46, "Skullsplitter's",
        "Krueg has written up everything about the Gordunni and the gate of Dire Maul for Elder Torgun in "
        "Orgrimmar's Valley of Wisdom.",
        [deliver("fe_q_krueg_report", "Take Krueg's report to Elder Torgun in Orgrimmar")],
        "Elder Torgun in the Valley of Wisdom remembers the old stories about the city in Feralas. Take him my "
        "report, and tell him the chains face inward. He'll know what that means better than I do.",
        "Inward, he says. Ancestors preserve us.\n\nThe Highborne who lived in that city didn't all die. Some of them "
        "bound themselves to something to stay alive, and the ogres were set at the gate to keep it shut. If the "
        "ogres are opening it, Orgrimmar needs to be ready.",
        turn_in_npc_id=TORGUN, zone=MJ,
        grant_items=carry("fe_q_krueg_report", "Krueg's Report", "A report on the Gordunni and the gate of Dire "
                          "Maul, written in an orc's square hand and sealed with Orgrimmar's mark.")))
    A(Q("fe_gashtok", "Gash'tok the Gatekeeper", TAKODA, 46, 46, "Gatebreaker's",
        "Gash'tok the Gatekeeper commands the ogres at the gate of Dire Maul. Brave Takoda Mistrunner lost two "
        "friends to him on a scouting run and hasn't stopped thinking about it.",
        [k("Gash'tok the Gatekeeper", 1, HW)],
        "Gash'tok the Gatekeeper wears a bent Highborne circlet and calls himself the lord of the gate. He's huge, "
        "even for an ogre. He killed two of my friends when we went to look at the gate, and he laughed while he "
        "did it. He's somewhere round the gate of Dire Maul.",
        "That's Gash'tok's circlet. It doesn't even fit an ogre, he must have bent it to make it stay on.\n\nI'll take "
        "it to the memorial pole. My friends weren't refugees, but they died for this camp, and that's the same "
        "thing.", zone=MJ))

    # =================================================================================== 6. THE DIG
    A(Q("fe_mounds_in_the_forest", "Mounds in the Forest", TAKODA, 45, 45, "Mound-Watcher's",
        "Mounds of raw earth have been pushing up through the forest floor south of Camp Mojache. Brave Takoda saw "
        "something with too many legs come out of one.",
        [explore(*MOUND_A, "Look at the mounds south of the camp", HW), k("Zukk'ash Swarmer", 6, HW)],
        "The mounds started a few months ago, south of the camp toward the Hive Fields. Last night I saw the "
        "Zukk'ash Swarmers come up out of one and go down into another. Go and look at them, and kill whatever "
        "comes out.",
        "Those are silithids. My grandmother told stories about them from Silithus, and I thought they were stories to keep "
        "children out of the desert.\n\nThey're not in the desert now. They're under our feet.", zone=MJ))
    A(Q("fe_resin_for_sale", "Resin for Sale", ORWIN, 45, 46, "Gizzmick's",
        "Orwin Gizzmick came to Feralas to buy silithid resin, which sells well in Gadgetzan. He's still buying, but "
        "now he wants to know where the Zukk'ash Tunnelers are taking it.",
        [fetch("fe_q_raw_resin", 8)],
        "The Zukk'ash Tunnelers coat their tunnels in resin as they dig, and it sells for a fortune to the "
        "engineers in Gadgetzan, the only thing that still does since you newcomers turned the whole market upside down. I'll pay you for it like always. But I've also started weighing each lump, and "
        "the grit's changing. Bring me a good batch from the Hive Fields.",
        "Feel that grit. It's not forest soil any more, it's dry and black.\n\nForest soil's dark and wet. This "
        "is desert sand, from a long way down. Wherever they're digging, it isn't here.",
        nxt="fe_where_the_line_goes", zone=MJ))
    A(Q("fe_where_the_line_goes", "Where the Line Goes", TAKODA, 46, 46, "Surveyor's",
        "Orwin has marked every mound he knows of on a map, and they run in a straight line. Brave Takoda wants "
        "someone to walk it and see where it ends.",
        [explore(*MOUND_B, "Follow the line of mounds through the Hive Fields", HW),
         explore(*HIVE_MOUTH, "Find where the line of mounds ends", HW)],
        "Orwin put a ruler on his map and every mound falls on the same line. Silithids don't dig in straight lines "
        "unless they're going somewhere. Walk it through the Hive Fields for me and tell me what's at the end.",
        "There's a hive at the end of it. Of course there's a hive.\n\nThe chieftain needs to know. If there's a hive under the forest, "
        "there's a queen in it, and a queen means they're not leaving.", nxt="fe_into_the_hive", zone=MJ))
    A(Q("fe_into_the_hive", "Into the Hive", CHIEF, 47, 47, "Hivebreaker",
        "The line of mounds ends at a hive mouth in the Hive Fields: the Zukk'ash Hive. Chieftain Ahanu won't have "
        "a silithid hive growing under the camp's feet.",
        [k("Zukk'ash Hive Warrior", 8, ZH), k("Zukk'ash Ravager", 5, ZH)],
        "I've had enough of things coming up out of the ground. Go down into the Zukk'ash Hive and kill its Zukk'ash "
        "Hive Warriors and its Zukk'ash Ravagers, and take friends. Hadoken says it goes down a long way.",
        "You're covered in resin, and you're alive. That's more than most could say.\n\nThe hive's still there, "
        "though. Orwin says there's a queen, and something past her that's still digging.",
        nxt="fe_the_deep_mother", zone=MJ))
    A(Q("fe_the_deep_mother", "The Deep Mother", ORWIN, 48, 49, "Brood-Bane",
        "The Zukk'ash Hive's queen is called the Deep Mother by the hunters who've seen her, in a chamber where the "
        "gallery levels out. As long as she lives, the hive grows.",
        [boss("The Deep Mother", ZH)],
        "The Deep Mother's chamber is where the hive's main gallery levels out, a long way down. She lays the eggs "
        "and the hive does whatever she wants. Kill her, and the hive stops growing. I'll still buy the resin, "
        "mind.",
        "The hunters can feel it already. The forest's quieter without her.\n\nThere's still something past her "
        "chamber, though. The tunnel keeps going, and the workers in it never stopped digging.",
        nxt="fe_the_dig_head", zone=MJ))
    A(Q("fe_the_dig_head", "Tunnelmaster Zix'tal", ORWIN, 48, 49, "Tunnelmaster's",
        "Past the Deep Mother's chamber, the Zukk'ash are still digging, driven by a silithid the size of a kodo "
        "that the hunters call Tunnelmaster Zix'tal.",
        [boss("Tunnelmaster Zix'tal", ZH)],
        "Tunnelmaster Zix'tal stands at the head of the dig, past the queen's chamber, and drives the workers on. "
        "The hunters heard it from the far end, and it doesn't sound like the forest any more down there. Kill "
        "it and see where they were digging.",
        "The air down there's dry and it smells of salt, you say? Then they were nearly through.\n\nThere's a "
        "dwarf town under the desert, past the Dry Deep. If the tunnel goes where I think it does, they'll want to "
        "know someone dug a road to their door.", nxt="fe_through_to_the_other_side", zone=MJ))
    A(Q("fe_through_to_the_other_side", "Through to the Other Side", ORWIN, 48, 49, "Deepwalker's",
        "The Zukk'ash tunnel comes out in the Dry Deep under the Abyssal Sands. Orwin wants the Dark Iron of "
        "Onyxhollow warned, and he's written a letter he thinks is polite.",
        [deliver("fe_q_orwin_letter", "Take Orwin's letter to Geomancer Vigdis Stonesong in Onyxhollow")],
        "Walk the tunnel past where Zix'tal was digging and you'll come out in the Dry Deep. Onyxhollow's below "
        "it, at the end of the descent. Give my letter to their geomancer, Vigdis Stonesong. Be polite, she's a "
        "dwarf.",
        "A goblin's letter, carried through a silithid tunnel all the way from Feralas. I've seen everything now.\n\n"
        "He's right, though. If the Zukk'ash dug this far, the ones in the deep sand can follow it back. We'll "
        "watch the Seep.", turn_in_npc_id=VIGDIS, zone=MJ,
        grant_items=carry("fe_q_orwin_letter", "Orwin's Letter", "A letter in a goblin's tidy hand, addressed to "
                          "the geomancer of Onyxhollow, with a price list folded into it by mistake.")))

    # =================================================================================== 7. THE FOG GROVES
    A(Q("fe_which_trees_these_are", "Which Trees These Are", JUNE, 46, 46, "Ranger's",
        "June Nakamura was a ranger in Olympic National Park for sixteen years. She knows the trees of the Fog "
        "Groves by name, and she wants someone to walk the edge of them with her eyes.",
        [explore(*GROVES_ROAD, "Walk the north edge of the Fog Groves", FC),
         explore(*GROVE_SOUTH, "Walk into the heart of the Fog Groves", FC)],
        "The big ones with the soft red bark are coast redwoods, and the dark ones are Sitka spruce. They've only ever grown on "
        "the Pacific coast of North America and nowhere else on Earth. Walk in from the road and then into the "
        "middle of the grove, and look at where they stop and Feralas starts.",
        "You saw it too, didn't you? There's no edge. The redwoods just blend into the giant trees like they've "
        "always been neighbours.\n\nIt's the same fog, the same moss, the same smell after rain. It's the closest "
        "thing to home any of us is going to get.", nxt="fe_stalkers_in_the_fog", zone=FC))
    A(Q("fe_stalkers_in_the_fog", "Stalkers in the Fog", JUNE, 46, 47, "Fogwalker's",
        "The Feralas Stalkers have learned that the settlers walk the groves in the fog, and that they can't see "
        "far in it.",
        [k("Feralas Stalker", 8, FC)],
        "Back home we had cougars, and you learned to make yourself big and loud. The Feralas Stalkers don't care "
        "how big you are. They've taken two of Walt's goats and they followed Rosa home last week. Hunt them out "
        "of the groves.",
        "Thank you. I'll sleep tonight.\n\nI spent sixteen years telling tourists the wildlife was more afraid of "
        "them than they were of it. That isn't true here, and I've had to unlearn it fast.", zone=FC))
    A(Q("fe_old_seven_point", "Old Seven-Point", WALT, 47, 47, "Seven-Point",
        "Old Seven-Point is the bull elk who leads the herd in the Fog Groves, and he's charged three of the "
        "settlers this season. Walt Hollis has had enough.",
        [k("Old Seven-Point", 1, FC)],
        "Old Seven-Point came through with the trees, same as we did. He's a Roosevelt bull, bigger than any I "
        "ever saw in Washington. He's taken to charging anything on two legs, and he put Sam in the creek last "
        "week. He'll be somewhere in the Fog Groves, bugling.",
        "He was a magnificent animal, and I'm sorry it came to that.\n\nThat's a winter's meat for the hollow, "
        "and the antlers are going over my door. A man from Forks doesn't waste an elk.", zone=FC))
    A(Q("fe_meat_for_the_winter", "Meat for the Winter", WALT, 46, 47, "Logger's",
        "Walt Hollis keeps Cedar Hollow fed through the wet season. The Fog Grove Elk came over with the trees, "
        "and there are more of them every year.",
        [fetch("fe_q_elk_cut", 6)],
        "I logged out of Forks for thirty years and hunted elk every fall. I won't cut these trees, but I'll hunt "
        "the elk that came with them. Bring me good cuts from the Fog Grove Elk and the hollow eats this winter.",
        "That's proper meat. I'll get it smoked tonight.\n\nFunny thing, I felt worse about cutting trees than I "
        "ever did about hunting. Took me coming here to work out why.", zone=FC))
    A(Q("fe_what_i_owe_them", "What I Owe Them", WALT, 47, 47, "Hollis",
        "Walt won't cut a single tree in the Fog Groves. He wants you to see the stump of the one he did cut, the "
        "first week he was here, before he understood.",
        [explore(*HOLLOW, "Look at the stump behind Cedar Hollow", FC)],
        "There's a stump behind the hollow. I cut it the first week, for the cabin, before I'd worked out where I "
        "was. It's a redwood, maybe four hundred years old. Go and look at it, and then come and tell me I'm a "
        "sentimental old fool.",
        "No, you didn't say it. Thank you.\n\nI cut down maybe ten thousand trees back home. That's a job, it "
        "fed my family. This one I cut because I didn't know it was the only one of its kind on a whole "
        "continent. That's the one I think about.", zone=FC))
    A(Q("fe_medicine_by_the_creek", "Medicine by the Creek", ROSA, 46, 47, "Nurse's",
        "Rosa Ibarra was an ER nurse in Tacoma. In Cedar Hollow she's the only one there is, and her pharmacy is "
        "whatever grows by the creek.",
        [gather("herb_purple_lotus", 6, "Gather Purple Lotus")],
        "The night elves taught me that Purple Lotus makes a decent painkiller if you boil it right. It grows "
        "along the creeks and the coast. I've got two people with broken bones and a man who won't stop coughing. "
        "Bring me what you can find.",
        "These are perfect. Some of them will go straight into the pot.\n\nI used to have a whole pharmacy two floors "
        "down. Now I've got a pot and a night elf druid who thinks I'm doing it wrong. It's working, though.",
        nxt="fe_bear_trouble", zone=FC))
    A(Q("fe_bear_trouble", "Bear Trouble", ROSA, 47, 47, "Ibarra",
        "The two broken bones in Cedar Hollow came from the same Fog Grove Ironfur, and Rosa would like it to be "
        "the last time she sets one.",
        [k("Fog Grove Ironfur", 7, FC)],
        "Both of my broken bones are from Fog Grove Ironfurs, and that's not a coincidence. They come into the hollow after the smokehouse, and "
        "the settlers try to chase them off with sticks. Please thin them out before somebody tries it again.",
        "I won't have to set any more legs this week. That's a good week.\n\nI'll tell the others to leave the "
        "bears to you. They won't listen, but I'll tell them.", nxt="fe_a_letter_for_feathermoon", zone=FC))
    A(Q("fe_a_letter_for_feathermoon", "A Letter for Feathermoon", ROSA, 47, 47, "Courier's",
        "Rosa has written to the druid at Feathermoon Stronghold, Kindal Moonweaver, asking for help with the "
        "hollow's medicine. She's never met her.",
        [deliver("fe_q_rosa_letter", "Take Rosa's letter to Kindal Moonweaver in Feathermoon Stronghold")],
        "The Sentinels keep their distance from us, and I understand why. But Kindal Moonweaver knows every plant "
        "on this coast, and I'm guessing at half of them. Take her my letter. The boat leaves from Feathermoon "
        "Landing on the shore.",
        "A healer asking another healer for help. I can't think of a better way to begin.\n\nI've watched your "
        "hollow from the walls for two years. I'll go myself, and I'll bring what I know.",
        turn_in_npc_id=KINDAL, zone=FC,
        grant_items=carry("fe_q_rosa_letter", "Rosa's Letter", "A letter in quick, clear handwriting, with a list "
                          "of plants down the side and question marks next to half of them.")))
    A(Q("fe_fungus_that_shouldnt_be_here", "Fungus That Shouldn't Be Here", SAM, 46, 47, "Mycologist's",
        "Sam Okonkwo studied fungus at Portland State. The mushrooms in the Fog Groves came with the trees, and some "
        "of them are spreading into the old forest round them.",
        [explore(*GROVES_ROAD, "Look at the mushrooms at the edge of the groves", FC),
         explore(*SHORE_CAMP, "Look for the same mushrooms on the coast road north", FC)],
        "There's a grey shelf fungus on the redwoods that's native to the Pacific Northwest and nowhere else. It's "
        "showing up on the Feralas trees now, further from the groves every month. Go and look at the edge of the "
        "groves, then up the coast road, and tell me if you see it there too.",
        "It's on the coast road. That's two miles from the nearest redwood.\n\nIt's not dangerous, as far as I "
        "know. But I don't know very far, and that bothers me more than anything else here.",
        nxt="fe_spores_on_the_hides", zone=FC))
    A(Q("fe_spores_on_the_hides", "Spores on the Hides", SAM, 47, 47, "Okonkwo",
        "Sam thinks the animals are carrying the spores. The Feralas Stalkers range furthest of anything in the "
        "groves.",
        [fetch("fe_q_spore_fur", 6)],
        "If the stalkers are carrying spores in their fur, that's how it's spreading so fast. Bring me fur from "
        "the Feralas Stalkers and I'll look at it under the lens. It's the only lens on this side of the world, "
        "so please don't make me ask twice.",
        "Grey spores in every one. That's how it's travelling.\n\nI need to show this to someone who knows what "
        "the old forest can survive. The druid at Feathermoon, maybe.", nxt="fe_show_the_druid", zone=FC))
    A(Q("fe_show_the_druid", "Show the Druid", SAM, 47, 47, "Sporebearer's",
        "Sam has sealed his spore samples in a jar for Kindal Moonweaver at Feathermoon Stronghold.",
        [deliver("fe_q_spore_jar", "Take Sam's sealed jar to Kindal Moonweaver in Feathermoon Stronghold")],
        "I've sealed the samples in wax so nothing gets out. Take the jar to Kindal Moonweaver on the island, and "
        "tell her I'm worried about the old forest, not about the groves. She'll understand the difference.",
        "Fungus from another world, riding on the backs of our own animals.\n\nThe forest has met strange things "
        "before. It'll decide what to do with this one. But I'd like to be there when it does.",
        turn_in_npc_id=KINDAL, zone=FC,
        grant_items=carry("fe_q_spore_jar", "Sam's Sealed Jar", "A small jar sealed with wax, full of grey spores "
                          "and tufts of fur, labelled in tiny careful handwriting.")))

    # =================================================================================== 8. FEATHERMOON AND THE COAST
    A(Q("fe_the_crossing", "The Crossing", MIRAEL, 46, 46, "Crossing",
        "Sentinel Mirael Duskbrook keeps the pier at Feathermoon Landing. The Sentinels let transplants land on the "
        "island, and she sends anyone useful to the General.",
        [deliver("fe_q_mirael_token", "Show Mirael's moon token to Shandris Feathermoon in Feathermoon Stronghold")],
        "Take this token. The crew on the boat will let you aboard with it, and the General will know I sent you. "
        "Shandris Feathermoon stands in front of the great hall. She's busy, so don't waste her time.",
        "That's Mirael's token. She doesn't hand these out to anyone she hasn't watched for a while.\n\nThe sea's been "
        "restless since the merge and so has the coast. If you're here to help, I've got more than enough for "
        "you to do.", turn_in_npc_id=SHANDRIS, zone=FC,
        grant_items=carry("fe_q_mirael_token", "Moon Token", "A disc of pale stone carved with a crescent moon, warm "
                          "from the Sentinel's hand.")))
    A(Q("fe_the_hatecrest_shore", "The Hatecrest Shore", SHANDRIS, 46, 47, "Feathermoon",
        "The Hatecrest naga have come up onto the beaches north of the landing since the merge, and they come at night. "
        "Shandris wants the shore back.",
        [k("Hatecrest Raider", 8, FC), k("Hatecrest Ruin-Digger", 5, FC)],
        "The Hatecrest Raiders hold the beaches north of the landing, and the Hatecrest Ruin-Diggers with them "
        "aren't fighting, they're digging. I want to know why, but first I want them off my coast.",
        "That's good work. Selarin will want to know what they were digging for, and so do I.\n\nThe naga have raided "
        "this coast before. They've never stopped to dig.", zone=FM))
    A(Q("fe_sardor_isle", "Sardor Isle", SHANDRIS, 47, 48, "Sentinel's",
        "The Hatecrest have taken Sardor Isle, off the north-west shore, and turned it into a camp. You can wade "
        "the sandbar to it at low tide.",
        [k("Hatecrest Coral Guardian", 6, FC), k("Hatecrest Tide Priestess", 5, FC)],
        "Sardor Isle's the naga's base on this coast now. The Hatecrest Coral Guardians hold the sandbar, and the "
        "Hatecrest Tide Priestesses keep the camp. Wade across and break it.",
        "The isle's quiet. The Sentinels will hold the sandbar from here.\n\nThe priestesses had maps of the "
        "coast on them, with every Highborne ruin marked. Latronicus is going to be unbearable about this.",
        zone=FM))
    A(Q("fe_orders_for_the_watch", "Orders for the Watch", SHANDRIS, 47, 48, "Northwatch",
        "Shandris wants to know whether the Hatecrest are digging at Ravenwind on the north coast too. The "
        "Sentinels' Watch is as far north as Feathermoon reaches.",
        [deliver("fe_q_shandris_orders", "Take Shandris's orders to Sentinel Aerwyn Starbrook at the Sentinels' "
                 "Watch")],
        "Take my orders north up the coast road to Sentinel Aerwyn Starbrook at the Sentinels' Watch. If the naga "
        "are digging at Ravenwind as well, I need to know before they find what they're looking for.",
        "Orders from the General. It's been a while since we had any.\n\nRavenwind's crawling with Hatecrest, and "
        "yes, they're digging. I'd have sent word sooner if I'd had anyone to send.",
        turn_in_npc_id=AERWYN, zone=FM,
        grant_items=carry("fe_q_shandris_orders", "Shandris's Orders", "Orders sealed with Feathermoon's crescent "
                          "and feather, for the captain of the Sentinels' Watch.")))
    A(Q("fe_night_diggers", "Night Diggers", SELARIN, 46, 47, "Tidewatch",
        "Sentinel Selarin watches the coast from Feathermoon to Sardor Isle. The Hatecrest Ruin-Diggers wrap what they "
        "find in kelp, like it's precious.",
        [fetch("fe_q_dug_relic", 6)],
        "The Hatecrest Ruin-Diggers come up the beaches at night with picks and sacks, and they're careful. Whatever they find, they wrap "
        "in kelp and carry back to the sea. Take it off them on the Hatecrest Shore and bring it to me.",
        "Pieces of the old Highborne road, and a carved door frame, and a key with no lock.\n\nThey're not "
        "taking treasure. They're taking directions.", nxt="fe_the_diggers", zone=FM))
    A(Q("fe_makrura_on_the_beach", "Makrura on the Beach", SELARIN, 46, 47, "Shellbreaker's",
        "The Hatecrest Makrura walk the beaches ahead of the naga, and the Sentinels' fishing boats can't land.",
        [k("Hatecrest Makrura", 8, FC)],
        "The Hatecrest Makrura come up on the shore ahead of the naga, like scouts. They snap at anything that "
        "lands, and our fishing boats can't get ashore at the landing. Clear them off the beaches.",
        "The boats can land again. Elyssa will be pleased.\n\nThey're not as stupid as they look, the makrura. "
        "They were watching the boats come and go, and the naga were watching them.", zone=FM))
    A(Q("fe_tidelord_ssaravel", "Tidelord Ssaravel", SELARIN, 48, 48, "Tidelord's",
        "Tidelord Ssaravel commands the Hatecrest on Sardor Isle, and he's the one with the maps.",
        [k("Tidelord Ssaravel", 1, FC)],
        "Tidelord Ssaravel holds Sardor Isle, and every map we've taken from the priestesses was copied from his. "
        "He calls up the sea when he's cornered, so watch your footing. He'll be on the isle.",
        "These are his maps. Every ruin on this coast, and a line drawn from all of them to the same place, inland.\n\nI "
        "know that place. So does Latronicus.", zone=FM))
    A(Q("fe_hydras_on_sardor", "Hydras on Sardor", SELARIN, 47, 48, "Hydrabane",
        "The Hatecrest keep Sardor Hydras on the isle like hounds, and they've started coming over the sandbar at "
        "night.",
        [k("Sardor Hydra", 5, FC)],
        "The naga keep Sardor Hydras on the isle and loose them at the sandbar. Three heads, and every one of them "
        "bites. The Sentinels can't hold the bar while those things are on it. Kill them on Sardor Isle.",
        "The bar's ours. I'll send two Sentinels to hold it tonight.\n\nI've heard of naga taming hydras before, "
        "but never this far from the deep sea. They've come a long way for whatever this is.", zone=FM))
    A(Q("fe_what_isildien_was", "What Isildien Was", LATRONICUS, 46, 46, "Moonspear",
        "Latronicus Moonspear keeps the record of the Highborne ruins on the coast, and it's been a busy record since the merge. The Ruins of Isildien are the "
        "biggest of them, and the Gordunni are digging out the dome.",
        [explore(*DOME_STEPS, "Look at the dome at the Ruins of Isildien", FC)],
        "Isildien was a Highborne library before the Sundering, the largest outside the capital. The dome's still "
        "standing, just about. Go and look at what the ogres are doing to it, and come back and tell me how bad "
        "it is.",
        "They've dug out the north stair. That's the archive stair, the one that went down to the sealed "
        "rooms.\n\nOgres don't dig down to archives. Somebody's told them what's there.",
        nxt="fe_ogres_in_the_dome", zone=FM))
    A(Q("fe_ogres_in_the_dome", "Ogres in the Dome", LATRONICUS, 46, 47, "Archivist's",
        "The Gordunni digging out Isildien's dome are working in shifts, and the Isildien Brutes guard the "
        "Isildien Diggers while they do.",
        [k("Isildien Brute", 7, FC), k("Isildien Digger", 6, FC)],
        "The Isildien Diggers work the stair and the Isildien Brutes stand over them. Every day they're down there, "
        "they break into another room of the archive, so please stop them.",
        "The stair's quiet. Thank you.\n\nThey took books. Ogres, taking books. I'd laugh if it weren't the "
        "most frightening thing I've seen in a century.", nxt="fe_pages_from_the_dome", zone=FM))
    A(Q("fe_pages_from_the_dome", "Pages from the Dome", LATRONICUS, 47, 47, "Scholar's",
        "The Isildien Ogre Mages are reading the pages they've taken from the archive. Latronicus wants them back "
        "before the ogres understand them.",
        [fetch("fe_q_dome_page", 5)],
        "The Isildien Ogre Mages carry the pages they've taken, and they read them aloud to each other, badly. "
        "Bring me every page you can take off them at the dome.",
        "These are the city's records. Eldre'Thalas, the Highborne city in the forest. The ogres call it Dire "
        "Maul.\n\nThe pages describe its gates, and how they're sealed.", nxt="fe_the_diggers", zone=FM))
    A(Q("fe_the_diggers", "Everybody's Digging", LATRONICUS, 47, 48, "Eldre'Thalas",
        "Latronicus has the naga's relics and the ogres' pages side by side. They point to the same place, and he "
        "wants Mojache's orc to hear it from someone who's seen both.",
        [deliver("fe_q_latronicus_notes", "Take Latronicus's notes to Krueg Skullsplitter in Camp Mojache")],
        "The naga are digging up the old roads and the ogres are digging up the archive, and both of them are "
        "looking for the way into Eldre'Thalas. Your Horde has a man at Camp Mojache who watches the gate. Take "
        "him my notes. For once, the Sentinels and the Horde want the same thing.",
        "So the naga want in, and the ogres want in, and the ogres were the ones set to keep it shut.\n\nI'll "
        "send this to Orgrimmar with my own report. Somebody's going to have to open that gate before they do, "
        "and it's going to take a lot more than me.", turn_in_npc_id=KRUEG, zone=FM,
        grant_items=carry("fe_q_latronicus_notes", "Latronicus's Notes", "Pages of careful night elf script "
                          "comparing a Hatecrest relic and a Highborne archive page, with a map of the forest "
                          "between them.")))
    A(Q("fe_trees_that_dont_answer", "Trees That Don't Answer", KINDAL, 46, 47, "Moonweaver's",
        "Kindal Moonweaver has watched the Fog Groves from the walls for two years. She's tried speaking to the "
        "trees, and they don't answer, and she wants to know how the old forest is taking it.",
        [explore(*GROVE_SOUTH, "Stand among the redwoods of the Fog Groves", FC),
         explore(*HOLLOW, "Visit Cedar Hollow, where the settlers live", FC)],
        "Every tree in Feralas knows its own name and will tell you, if you know how to ask. The trees in the Fog "
        "Groves don't. Go and stand among them, then go and see the people living in the hollow. I've watched "
        "them long enough, and I'd like to hear about them from someone who's been there.",
        "They're kind people, you say, and they don't cut the trees. And the old forest is growing round them, not against them.\n\n"
        "I've been afraid of the wrong thing. The trees don't answer because they've never been asked.",
        nxt="fe_vouching_for_the_hollow", zone=FM))
    A(Q("fe_vouching_for_the_hollow", "Vouching for the Hollow", KINDAL, 47, 47, "Grovewarden's",
        "Kindal has decided to speak for Cedar Hollow to the General. She wants June Nakamura to know it, and to "
        "carry the Sentinels' mark back to the hollow.",
        [deliver("fe_q_kindal_mark", "Take Kindal's mark to June Nakamura in Cedar Hollow")],
        "I'll speak for the hollow to Shandris. Until then, take this mark to June Nakamura. If any Sentinel "
        "troubles the settlers, they show it, and the Sentinel walks away.",
        "The Sentinels' moon. They're telling us we can stay.\n\nI don't know how to thank them. I'll start by "
        "teaching them the names of the trees, I suppose.", turn_in_npc_id=JUNE, zone=FM,
        grant_items=carry("fe_q_kindal_mark", "Kindal's Mark", "A wooden disc carved with a crescent moon over a "
                          "redwood cone, strung on a leather cord.")))
    A(Q("fe_the_hippogryphs_are_restless", "The Hippogryphs Are Restless", KINDAL, 46, 47, "Skystalker's",
        "The wild hippogryphs of the Frayfeather Highlands have turned on the Sentinels' patrols. Kindal thinks "
        "something's driving them, but for now the patrols need the sky clear.",
        [k("Frayfeather Skystalker", 7, FC), k("Frayfeather Windwing", 5, FC)],
        "The Frayfeather Skystalkers and the Frayfeather Windwings are wild, but they've never attacked a Sentinel "
        "before. Now they dive at every patrol on the highlands. Thin them before someone's killed.",
        "The patrols are back on the highlands. Thank you.\n\nThe hippogryphs weren't angry. They were afraid, "
        "and they've been afraid ever since the giants in the north started walking.", zone=FM))
    A(Q("fe_antilus_the_soarer", "Antilus the Soarer", FYLDREN, 48, 48, "Soarer's",
        "Antilus the Soarer is the oldest of the wild hippogryphs, and he's started taking the Sentinels' mounts "
        "out of the sky. Fyldren Moonfeather has lost two.",
        [k("Antilus the Soarer", 1, FC)],
        "Antilus the Soarer is the patriarch of the Frayfeather Highlands. He's older than this roost and he "
        "used to leave our hippogryphs alone. Now he takes them out of the air. I can't fly the highland route "
        "while he's up there.",
        "I'd hoped he'd be the one to calm the others. He was too far gone.\n\nThe highland route's open again. "
        "I'll fly it myself tomorrow, for his sake.", zone=FM))
    A(Q("fe_chimaeras_and_the_boats", "Chimaeras and the Boats", JALARA, 47, 48, "Huntress",
        "The Dread Chimaeras on the Isle of Dread have started going for the Sentinels' boats, which they never did before the merge. Huntress Jalara "
        "Nightwind counts them by their scales.",
        [k("Dread Chimaera", 7, FC), fetch("fe_q_chimaera_scale", 5)],
        "The Dread Chimaeras have nested on the Isle of Dread for as long as I've been alive, and they've never "
        "come out over the water. Now they're attacking the boats to the landing. Wade out over the sandbar and "
        "kill them, and bring me their scales so I know how many are left.",
        "That's most of the young ones. The nests will be quieter.\n\nThey're not hunting the boats. They're "
        "leaving the isle. Something's driven them out of their nests.", nxt="fe_what_drove_them", zone=FM))
    A(Q("fe_what_drove_them", "What Drove Them", JALARA, 48, 48, "Dreadwatch",
        "Jalara wants to know what's driven the chimaeras off the Isle of Dread. Their nests are on the old "
        "Highborne tower at the island's heart.",
        [explore(*DREAD_BAR, "Cross the sandbar to the Isle of Dread", FC),
         k("The Dread Matriarch", 1, FC)],
        "Cross the sandbar to the Isle of Dread and look at the tower. The Dread Matriarch guards the nests, and "
        "she's never left them before. If she's leaving, I want to know why, and I want her gone before she "
        "takes the young ones with her.",
        "Dug earth all round the base of the tower, and naga tracks in it.\n\nThe Hatecrest were digging under the "
        "chimaeras' nests. No wonder they fled. Everyone on this coast is digging, and nobody's asking what lives "
        "on top.", zone=FM))
    A(Q("fe_skull_taker_murg", "Skull-Taker Murg", AELYRA, 47, 47, "Skull-Taker's",
        "Skull-Taker Murg leads the Gordunni at the Ruins of Isildien. He takes a skull from everyone he kills, "
        "and he's taken two Sentinels'.",
        [k("Skull-Taker Murg", 1, FC)],
        "Skull-Taker Murg walks the dome at Isildien with a belt of skulls. Two of them are my sisters'. I've "
        "asked the General to let me go, and she says no, because I'd go alone. So I'm asking you instead.",
        "Their skulls are on his belt. I'll take them home and bury them properly.\n\nThank you. I couldn't have "
        "stood at their graves while he was still walking.", zone=FM))
    A(Q("fe_lotus_for_the_draughts", "Lotus for the Draughts", TAELAN, 46, 47, "Leafsong",
        "Herbalist Taelan Greenleaf brews healing draughts for the Sentinels, and they're going through them faster "
        "than ever. Sungrass grows on the open highlands and the north coast.",
        [gather("herb_sungrass", 6, "Gather Sungrass")],
        "The Sentinels on the walls have gone through my healing draughts faster than I can brew them since the naga came. "
        "Sungrass is the base of every one, and it's growing in the open, on the highlands and up the coast. Bring me "
        "what you can.",
        "That's a week of draughts for the walls.\n\nKindal says the settlers' nurse has worked out a "
        "painkiller from Purple Lotus that I've never thought of. I'm going to have to go and ask her about it, "
        "and I'm not happy about that.", zone=FM))

    # =================================================================================== 9. THE NORTH COAST
    A(Q("fe_ravenwinds_diggers", "Ravenwind's Diggers", AERWYN, 47, 48, "Ravenwind",
        "The Hatecrest who came up with the merge are digging at the Ruins of Ravenwind the same way they did on the south coast. Sentinel "
        "Aerwyn Starbrook wants them stopped before they're finished.",
        [k("Ravenwind Raider", 8, TC), k("Ravenwind Sea Witch", 5, TC)],
        "Ravenwind's ruins are full of Hatecrest, and the Ravenwind Sea Witches are calling up the tide to "
        "wash the earth away from the old stones. The Ravenwind Raiders guard them. Go up the coast and stop the "
        "digging.",
        "The tide's back where it should be.\n\nThey'd dug down to a road under Ravenwind. It runs inland, east, "
        "the same as the ones on the south coast.", nxt="fe_guardians_of_the_ruin", zone=TC))
    A(Q("fe_guardians_of_the_ruin", "Guardians of the Ruin", AERWYN, 48, 49, "Watch-Captain's",
        "The Hatecrest have brought Ravenwind Guardians and Ravenwind Hydras to hold the road they uncovered.",
        [k("Ravenwind Guardian", 6, TC), k("Ravenwind Hydra", 4, TC)],
        "The Ravenwind Guardians hold the old road now, and they've brought Ravenwind Hydras to keep it. My "
        "Sentinels can't get near it. Break their hold on the ruins.",
        "We can bury the road again. It won't stop them, but it'll slow them down.\n\nThere's one more of them. "
        "She gives the orders, and the guardians answer to her.", nxt="fe_lady_szaressa", zone=TC))
    A(Q("fe_lady_szaressa", "Lady Szaressa", AERWYN, 49, 49, "Szaressa's",
        "Lady Szaressa commands the Hatecrest at Ravenwind. Her ward turns blades, and Aerwyn's Sentinels can't "
        "get close to her.",
        [k("Lady Szaressa", 1, TC)],
        "Lady Szaressa leads the Hatecrest at Ravenwind. She wraps herself in a ward of sea water when she's hurt, "
        "and my arrows just bounce off it. Break the ward and finish her.",
        "Her coral scepter. There's a map of the forest carved into the handle.\n\nTake word to Latronicus at "
        "Feathermoon. Everything on this coast points to the same place, and he's the one who'll know what to do "
        "about it.", zone=TC))
    A(Q("fe_down_from_the_hold", "Down From the Hold", TAHU, 47, 48, "Rage Scar",
        "Tahu Swiftrunner was sent north from Mojache after the Rage Scar yetis, who've come down out of their hold "
        "and into the hunting grounds.",
        [k("Rage Scar Yeti", 8, TC), fetch("fe_q_singed_fur", 4)],
        "The Rage Scar Yetis didn't leave their hold even when the worlds came together. Now they're down in the forest, angry "
        "and hungry. Kill them, and bring me their fur. Some of them are singed, and I'd like to know why.",
        "Every one of them is singed at the tips.\n\nSomething hot went into Rage Scar Hold and drove them out. "
        "Yetis don't run from fire easily. Whatever it was, it frightened them badly.",
        nxt="fe_what_drove_them_out", zone=TC))
    A(Q("fe_what_drove_them_out", "What Drove Them Out", TAHU, 48, 48, "Swiftrunner's",
        "Tahu wants someone to look into Rage Scar Hold itself, where the yetis came from.",
        [explore(*RAGE_SCAR, "Look into Rage Scar Hold", TC), k("Rage Scar Matriarch", 4, TC)],
        "Go up to Rage Scar Hold in the east hills and look inside. The Rage Scar Matriarchs are still guarding "
        "the mouth, and they won't let you past easily. Tell me what you see in there.",
        "Burned earth and claw marks, and something big's been digging through the back wall.\n\nIt came up "
        "from underneath. Like the silithids at Mojache. I'm going to have to take this home.",
        nxt="fe_the_old_bull", zone=TC))
    A(Q("fe_the_old_bull", "The Old Bull", TAHU, 49, 49, "Old Bull's",
        "The Rage Scar Old Bull leads what's left of the yetis, and he's stopped running. He's in the forest north "
        "of the hold, and he attacks anything that moves.",
        [k("Rage Scar Old Bull", 1, TC)],
        "The Rage Scar Old Bull stopped running when the others did. Now he attacks anything that moves, and he "
        "threw one of the Sentinels into a tree yesterday. He's somewhere round Rage Scar Hold.",
        "He was old, and frightened, and very angry. I've seen that before.\n\nThe forest will be safer. I wish "
        "it had ended some other way.", zone=TC))
    A(Q("fe_warm_roots", "Warm Roots", SYLANNA, 47, 48, "Dreambough",
        "Dreamwatcher Sylanna came from Moonglade to the Dream Bough, a great tree whose roots reach into the Dream and have been restless since the merge. "
        "The arch at Moonglade is warm at night, and she wants to know whether these roots are too.",
        [explore(*BOUGH, "Lay your hand on the roots of the Dream Bough", TC)],
        "The stones of the Dreaming Arch at Moonglade have been warm at night for months. The Dream Bough's roots "
        "touch the same Dream. Go and lay your hand on them, tonight, and tell me whether they're warm.",
        "So they're warm. It's the same warmth as the arch, then.\n\nWhatever's waking in the Dream is waking under Feralas "
        "too. The Circle will want to know.", nxt="fe_darters_at_the_bough", zone=TC))
    A(Q("fe_darters_at_the_bough", "Darters at the Bough", SYLANNA, 48, 48, "Dreamguard's",
        "The Dream Bough Darters and the Dream-Touched Treants round the tree have turned wild since the roots warmed.",
        [k("Dream Bough Darter", 7, TC), k("Dream-Touched Treant", 5, TC)],
        "The Dream Bough Darters were the tree's guardians, and the Dream-Touched Treants were its gardeners. "
        "Since the roots warmed, they attack anything that comes near, even me. Thin them so I can sit with the "
        "tree.",
        "I can reach the roots again. Thank you.\n\nThey weren't angry. They were dreaming, and whatever they "
        "were dreaming about frightened them.", nxt="fe_walkers_under_the_arches", zone=TC))
    A(Q("fe_walkers_under_the_arches", "Walkers Under the Arches", SYLANNA, 48, 49, "Colossus",
        "The giants of the Twin Colossals have started walking toward the Dream Bough, and they trample everything "
        "in their way.",
        [k("Colossal Land Walker", 6, TC), k("Colossal Sea Walker", 4, TC)],
        "The Colossal Land Walkers and the Colossal Sea Walkers have stood under the Twin Colossals since before "
        "the night elves came. Now they're walking north-east, toward the Bough. I don't know what they mean to do "
        "when they get there, and I'd rather not find out.",
        "They've stopped walking, for now.\n\nThe giants are the oldest things in Feralas. If something's calling "
        "them, it's calling from very deep. I need to take this to Moonglade.", nxt="fe_tell_moonglade", zone=TC))
    A(Q("fe_tell_moonglade", "Tell Moonglade", SYLANNA, 49, 49, "Dreamer's",
        "Dreamwatcher Sylanna has written to Dreamwatcher Lethiel at Moonglade's Dreaming Arch: the roots are warm, "
        "the guardians are dreaming badly, and the giants are walking.",
        [deliver("fe_q_sylanna_letter", "Take Sylanna's letter to Dreamwatcher Lethiel at Moonglade")],
        "Lethiel sits with the Dreaming Arch in Moonglade's north woods. Take her my letter. She'll know what it "
        "means that the Bough is warm too, or she'll know who to ask.",
        "The Bough as well. And the giants walking.\n\nIt isn't only Moonglade, then. Whatever's waking is "
        "under the whole of Kalimdor, and it's turning over in its sleep. Thank you for carrying this so far.",
        turn_in_npc_id=LETHIEL, zone=TC,
        grant_items=carry("fe_q_sylanna_letter", "Sylanna's Letter", "A letter on a pressed leaf, in a night elf's "
                          "hand, addressed to the Dreaming Arch.")))
    A(Q("fe_the_old_walker", "The Old Walker", FYLDREN, 49, 49, "Old Walker's",
        "The Old Walker is the eldest of the Twin Colossals' giants, and since he started walking the hippogryphs "
        "won't fly the north coast at all. Fyldren Moonfeather needs the route back.",
        [k("The Old Walker", 1, TC)],
        "The Old Walker's been standing under the Twin Colossals for longer than Feathermoon's been here. Now he "
        "walks, and the ground shakes under him, and my hippogryphs won't fly within a mile. Please stop him.",
        "I can feel the difference from here. The hippogryphs are calm for the first time in a month.\n\nHe was "
        "older than the Sentinels. I'm sorry it had to be you who stopped him, and I'm glad someone did.",
        zone=FM))

    # =================================================================================== 10. MORE HANDS
    A(Q("fe_a_lesson_in_the_wilds", "A Lesson in the Wilds", ISHANA, 44, 45, "Brightmane",
        "Trainer Ishana Brightmane teaches every young tauren in the camp, and she says the forest teaches better "
        "than she does. She'd like you to show her students how it's done.",
        [k("Ironfur Bear", 6, HW)],
        "The young ones from Mulgore learned to fight in a hurry, three years ago, running. They've never had to stand and hunt. "
        "Go out into the forest and bring down Ironfur Bears where my students can watch from the trees. They'll "
        "learn more from that than from a month of drills.",
        "They watched every one of them. One of them wants to be a hunter now, and the other wants to be a cook.\n\n"
        "That's a good day's teaching, as far as I'm concerned.", zone=MJ))
    A(Q("fe_goldthorn_for_the_fever", "Goldthorn for the Fever", KELE, 45, 46, "Goldthorn",
        "A fever's going round the refugees' quarter, and Kele's out of Goldthorn. It grows on the drier ground "
        "along the arm road.",
        [gather("herb_goldthorn", 6, "Gather Goldthorn")],
        "The fever's in the refugees' quarter now, and it's the children who've got it worst. Goldthorn brings a "
        "fever down. It likes the drier ground along the road west. Bring me what you can, and quickly.",
        "That's enough for every child in the quarter. Thank you.\n\nWe didn't lose anyone to the road this "
        "year. I'm not going to start losing them to a fever.", zone=MJ))
    A(Q("fe_spears_at_the_wind_riders", "Spears at the Wind Riders", SHYN, 45, 46, "Skyward",
        "The Grimtotem at the compound have started throwing spears at the wind riders as they fly over. Wind "
        "Rider Master Shyn has lost a mount to it.",
        [k("Grimtotem Pathfinder", 6, HW), k("Grimtotem Earthbreaker", 4, HW)],
        "The Grimtotem Pathfinders throw their spears at anything in the air over the compound, and the Grimtotem "
        "Earthbreakers cheer them on. They brought down one of my wind riders last week. I'd like it to be the "
        "last.",
        "The route's clear. I'll fly it tonight myself.\n\nThat wind rider carried three refugee children down "
        "out of the Needles. She deserved better than a Grimtotem spear.", zone=MJ))
    A(Q("fe_makrura_for_the_pot", "Makrura for the Pot", ELYSSA, 46, 47, "Gullwind",
        "Fisherwoman Elyssa Gullwind feeds the Sentinels on nightfin and makrura, and the makrura on the beaches "
        "have come up fat and bold since the naga arrived.",
        [fetch("fe_q_makrura_tail", 6)],
        "The Hatecrest Makrura on the beaches are bigger than they've ever been. The naga feed them, I think. "
        "They've got the sweetest tail meat on the coast, and the Sentinels are tired of soup. Bring me some.",
        "These'll do nicely. Grilled in their shells with a little salt.\n\nThe Sentinels will complain about it, "
        "and there won't be a scrap left by morning.", zone=FM))
    A(Q("fe_smoked_elk_for_the_inn", "Smoked Elk for the Inn", SHYRIA, 46, 47, "Innkeeper's",
        "Innkeeper Shyria has heard that the settler Walt Hollis smokes the best elk on the coast, and she'd like "
        "to trade for some. She's never spoken to a settler.",
        [deliver("fe_q_shyria_offer", "Take Shyria's offer to Walt Hollis in Cedar Hollow")],
        "Every Sentinel who's walked past the transplants' hollow comes back talking about the smell from that smokehouse. "
        "I'd like to trade for it, wine for elk. Take my offer to Walt Hollis, and be polite. I'm told he's a "
        "proud man.",
        "Elven wine for my smoked elk? I'd have given her the elk for nothing, just for asking.\n\nTell her yes. "
        "Tell her to send the wine on the next boat, and that she's welcome at the hollow any time.",
        turn_in_npc_id=WALT, zone=FM,
        grant_items=carry("fe_q_shyria_offer", "Shyria's Offer", "A note in a neat night elf hand offering a cask "
                          "of moonberry wine for a side of smoked elk.")))
    A(Q("fe_highland_nests", "Highland Nests", FYLDREN, 46, 47, "Nestwarden's",
        "Fyldren Moonfeather wants to know whether the wild hippogryphs of the Frayfeather Highlands have abandoned "
        "their nests, or only their manners.",
        [explore(*HIGHLANDS, "Look at the nests in the Frayfeather Highlands", FC)],
        "The wild hippogryphs nest on the crags in the Frayfeather Highlands. If they've left the nests, something "
        "big's frightened them, and I'll need to keep my mounts on the island. Go and look, and don't touch the eggs.",
        "Nests full and the parents furious, then. They haven't left, they're defending.\n\nSomething's "
        "frightening them from the north. The giants, I'd guess. Everything on this coast is looking north lately.",
        zone=FM))
    A(Q("fe_watch_fires", "Watch Fires", AELYRA, 47, 48, "Watchfire",
        "Sentinel Aelyra Tidewatch keeps the harbour, and she's the one who lights the signal fire when the Watch "
        "in the north sends word. It hasn't sent word in a month.",
        [explore(*WATCH, "Look in on the Sentinels' Watch", TC), explore(*UNDER_ARCHES, "Look under the Twin "
                                                                                       "Colossals", TC)],
        "The Watch lights a fire on the cliffs when it needs us, and I light ours to answer. It's been dark for a "
        "month. Go up the coast road to the Sentinels' Watch and see they're all right, then look under the "
        "Colossals on the way back. That's where the last fire was.",
        "They're there, and they're busy, and nobody's had a spare hand to light a fire. That's a relief.\n\nI'll "
        "light ours tonight anyway, so they know we haven't forgotten them.", zone=FM))
    A(Q("fe_stalkers_on_the_north_coast", "Stalkers on the North Coast", JALARA, 47, 48, "Northern",
        "Since the merge the Feralas Stalkers have spread up the coast, and now they've followed the yetis' scent north, and they hunt the coast road between the "
        "Forgotten Coast and the Sentinels' Watch.",
        [k("Feralas Stalker", 7, TC)],
        "The Feralas Stalkers have gone north after the yetis, and now they're hunting the coast road up to the "
        "Watch. My runners won't take it alone any more. Clear the road through the Twin Colossals.",
        "My runners can use the road again. They'll still run, but at least they won't have to.\n\nThe forest "
        "has gone strange this year, from one end of the coast to the other.", zone=FM))
    A(Q("fe_windwings_over_the_arches", "Windwings Over the Arches", JALARA, 48, 48, "Archwing",
        "The Frayfeather Windwings have moved north to the Twin Colossals and taken to nesting on the arches, where "
        "they dive at anyone underneath.",
        [k("Frayfeather Windwing", 6, TC)],
        "The Frayfeather Windwings have moved up to the Twin Colossals and they're nesting on top of the arches. "
        "They dive at anything that walks underneath, and our patrols to the Watch go right under them. Drive "
        "them off.",
        "The patrols can walk under the arches again.\n\nKindal says the hippogryphs are running from the giants. "
        "I'd say they've chosen a strange place to run to.", zone=FM))
    A(Q("fe_word_to_hadoken", "Word to Hadoken", TAHU, 48, 48, "Runner's",
        "Tahu Swiftrunner has seen enough at Rage Scar Hold to know Mojache needs to hear it. Something came up "
        "under the hold the way the silithids came up under the forest.",
        [deliver("fe_q_tahu_message", "Take Tahu's message to Hadoken Swiftstrider in Camp Mojache")],
        "Hadoken sent me north, and he'll want to know what I found. It's the strangest thing I've seen since the merge. Tell him something came up from underneath "
        "Rage Scar Hold, the same as at home. He'll know what I mean, and he'll know to watch the ground.",
        "So it came from underneath again. Everything this year is coming from underneath.\n\nI'll put a watch on the Hive Fields and "
        "tell my sister. Tahu's a good runner, and he wouldn't send word if he wasn't worried.",
        turn_in_npc_id=HADOKEN, zone=TC,
        grant_items=carry("fe_q_tahu_message", "Tahu's Message", "A strip of hide knotted in the Mojache hunters' "
                          "code, with a pinch of burned yeti fur tied into it.")))
    A(Q("fe_the_road_under_ravenwind", "The Road Under Ravenwind", AERWYN, 48, 49, "Roadwarden's",
        "Sentinel Aerwyn wants to see where the old Highborne road the naga uncovered at Ravenwind actually runs.",
        [explore(*RAVENWIND, "Find the uncovered road at the Ruins of Ravenwind", TC),
         explore(*UNDER_ARCHES, "Follow the old road inland to the Twin Colossals", TC)],
        "The naga dug down to a road under Ravenwind, and it's running inland. Find it in the ruins and follow it east "
        "as far as the Twin Colossals. If it goes where I think it does, Latronicus needs to know.",
        "Under the arches and on east, toward the middle of the forest. Toward the city.\n\nThe old Highborne "
        "built roads from every port on this coast to Eldre'Thalas. The naga aren't digging at random, they're "
        "following them home.", zone=TC))
    return out
