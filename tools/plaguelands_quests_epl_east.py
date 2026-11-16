"""
East Eastern Plaguelands' quests, levels 56-60. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT EAST EPL IS ABOUT (docs/plaguelands_design.md). The far end of the Plaguelands, where the Argent Dawn holds
Light's Hope Chapel on holy ground and a small camp at Crown Guard keeps the road between the chapel and Stratholme
open. Darrowshire's ghosts still fight the battle they lost, the Scarlet Crusade holds Tyr's Hand on the coast, the
Mossflayer trolls of Zul'Mashar raid the roads, Quel'Lithien Lodge's rangers walk their posts long after they died,
and the Scourge is building something out of bones in the Pestilent Scar.

  LIGHT'S HOPE (21)  Commander Eligor Dawnbringer (Tyr's Hand, the Abbot, a word with the Order), Archmage Lysander
                     Hale (the Scar's marrow and the Bone Colossus), Lightwarden Ysolde Carrow (Darrowshire's dead,
                     the Scar, the Mossflayer hexes), Sergeant Marisol Reyes (the Mossflayers and their medicine, and
                     a colleague at Talonbranch), Ranger Faelis Dawnreach (his old lodge), Innkeeper Jessa Moonfield
                     (lamp oil).
  CROWN GUARD (13)   Captain Joss Varden (the road, Darrowshire's ghouls, Tyr's Hand's hounds and archers), Corporal
                     Ines Duarte (Blackwood Lake, and filters for Felwood), Innkeeper Greta Lowe (horse for the pot,
                     a barrel for Sorrow Hill), Bat Handler Gwen Pike (the wild bats, and a young one for Light's
                     Hope).
  DARROWSHIRE (3)    Pamela Redpath, a little girl's ghost who's still waiting for her father.
  OUT                Felwood (Ines's filters to Tomasz Wolny at the Emerald Sanctuary, Marisol's notes to Marcus
                     Oyelaran at Talonbranch), Sorrow Hill (Dawnbringer to Rory, Greta to Priya, Pamela to Odile).
  IN                 Arathi (Overlord Gath'rok's answer to Dawnbringer).
  CAVE               The Bone Mines, under the Scar (Ysolde: the miners; Faelis: the Overseer, then the Ossifier).

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and only
the people at the top know more. The Argent Dawn takes anyone who'll stand on the wall and doesn't ask where they came
from. Its people call the transplants newcomers. Dawnbringer knows more than he says. Ines and Marisol are
transplants and talk about home the way anyone does.

WHO PAYS. Everything here pays the Argent Dawn, the zone's own faction.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

EE = "eastern_plaguelands_east"
BM = "the_bone_mines"

# ---- the people
VARDEN, GRETA, GWEN, INES = "epl_cg_captain", "epl_cg_innkeeper", "epl_cg_flight", "epl_cg_corporal"
DAWN, HALE, JESSA, ALDOUS = "epl_lh_commander", "epl_lh_scourgestones", "epl_lh_innkeeper", "epl_lh_flight"
YSOLDE, MARISOL, FAELIS = "epl_lh_lightwarden", "epl_lh_volunteer", "epl_lh_ranger"
PAMELA = "epl_ds_pamela"
GATHROK = "hammerfall_commander"
RORY, PRIYA, ODILE = "wpl_pf_flamekeeper", "wpl_pf_innkeeper", "wpl_pf_chaplain"
TOMASZ, MARCUS = "es_volunteer_carpenter", "fn_talonbranch_medic"

HUB_GIVERS = {VARDEN, GRETA, GWEN, INES, DAWN, HALE, JESSA, YSOLDE, MARISOL, FAELIS}
#: the people born here, who say newcomers and never Earth
NATIVE_GIVERS = {VARDEN, GRETA, GWEN, DAWN, HALE, JESSA, YSOLDE, FAELIS, PAMELA, GATHROK}
FACTION_BY_GIVER = {}


def k(target, n, zone=EE):
    return kill(target, n, zone=zone)


def boss(target, zone=EE):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=EE, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Blackwood Snapjaw": [("pl_q_gizzard_stone", "Snapjaw Gizzard Stone", "A smooth stone from a snapjaw's gizzard, "
                           "stained green where the lake water's soaked into it.")],
    "Blighted Warhorse": [("pl_q_warhorse_flank", "Warhorse Flank", "A cut from a blighted warhorse's flank. Greta "
                           "says the plague cooks out. Greta says a lot of things.")],
    "Scar Bone Construct": [("pl_q_scar_marrow", "Scar Marrow", "A plug of grey marrow from a bone construct. It's "
                             "cold, and it stays cold however long you hold it.")],
    "Mossflayer Shadowhunter": [("pl_q_hex_fetish", "Mossflayer Hex Fetish", "A bundle of feathers, teeth and "
                                 "string, knotted around a scrap of cloth from the chapel's laundry.")],
    "Mossflayer Scout": [("pl_q_herb_pouch", "Mossflayer Herb Pouch", "A troll's herb pouch, full of dried leaves "
                          "and roots that smell clean, which is rare out here.")],
    "Restless Lodge Ranger": [("pl_q_ranger_token", "Quel'Lithien Ranger's Token", "A silver leaf on a green cord, "
                               "the token every ranger of the lodge carried. It's tarnished but whole.")],
    "Plague-Rotted Bear": [("pl_q_bear_fat", "Rendered Bear Fat", "A lump of fat cut from the parts of a bear the rot "
                            "hadn't reached. It'll burn clean in a lamp, if nothing else.")],
    "Darrowshire Ghoul": [("pl_q_pamelas_doll", "Pamela's Doll", "A rag doll in a blue dress, muddy and missing a "
                           "button eye. Someone loved it very much.", 1.0)],
}

STARTER_DROPS = {}
STARTER_IDS = {}


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=EE, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def build():
    out = []
    A = out.append

    # ======================================================================================== CROWN GUARD
    # ---- Captain Joss Varden
    A(Q("ple_the_road_between", "The Road Between", VARDEN, 56, 57, "Crown Guard",
        "Captain Joss Varden holds the camp at Crown Guard, and the camp holds the road between Light's Hope and "
        "Stratholme. The road's only open while somebody keeps it open.\n\nThe Blighted Warhorses that used to pull "
        "the Crusade's wagons run wild along it now, and the Plague-Rotted Bears come down to the road to eat "
        "whatever the horses leave. He wants both of them thinned.",
        [k("Blighted Warhorse", 8), k("Plague-Rotted Bear", 6)],
        "The horses run the road east and west of the camp. The bears keep to the trees beside it. Don't let a horse "
        "get behind you, because they kick like they mean it.",
        "The road's open again, for a few days anyway.\n\nI'll take a few days. Out here a few days is a long time.",
        [("chest", "armor", "plate", "tank"), ("legs", "armor", "cloth", "caster"),
         ("hands", "armor", "leather", "agility")], nxt="ple_darrowshires_ghouls"))
    A(Q("ple_word_to_lights_hope", "Word to Light's Hope", VARDEN, 56, 56, "Crown Guard",
        "Varden sends a report up the road to Light's Hope every week, and every week he wonders whether it'll get "
        "there. This week's says the Crusade at Tyr's Hand is moving.\n\nHe wants it in Commander Eligor "
        "Dawnbringer's hand.",
        [deliver("pl_q_varden_report", "Bring Varden's report to Commander Eligor Dawnbringer at Light's Hope")],
        "East along the road to the chapel. It's the white building on the hill. You can't miss it, and the dead "
        "won't follow you onto its ground.",
        "Joss writes the way he fights, short and to the point.\n\nTyr's Hand is moving, then. I'll need people who "
        "can walk into it and walk back out. I think you'll do nicely.",
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], turn_in_npc_id=DAWN,
        grant_items=carry("pl_q_varden_report", "Varden's Report", "A folded report in a soldier's square hand, "
                                                                   "sealed with Crown Guard's tower.")))
    A(Q("ple_darrowshires_ghouls", "Darrowshire's Ghouls", VARDEN, 57, 57, "Crown Guard",
        "Darrowshire was a town south of the camp until the Scourge came for it, and the town fought and lost. The "
        "Darrowshire Ghouls that came out of that fight still walk its streets, and on bad nights they walk up the "
        "road to Crown Guard.\n\nVarden wants them put down before the next bad night.",
        [k("Darrowshire Ghoul", 10)],
        "Darrowshire's south and west of the camp, down the old road. The ghouls are in the streets and the yards. "
        "Mind the ghosts, because they're still fighting a battle that ended years ago.",
        "That'll keep them off my road for a while.\n\nThere's a ghost of a little girl in that town who talks to "
        "travellers. If you met her, I hope you were kind.",
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="ple_the_houndmasters"))
    A(Q("ple_the_houndmasters", "The Houndmasters", VARDEN, 58, 58, "Crown Guard",
        "The Crusade at Tyr's Hand sends its hounds up the road at night, and the Tyr's Hand Houndmasters who run "
        "them know exactly where Crown Guard's sentries stand. Varden lost two of his people last week.\n\nHe wants "
        "the houndmasters dead, and he'd like their dogs to have nobody to come home to.",
        [k("Tyr's Hand Houndmaster", 8)],
        "Tyr's Hand is on the coast, south and east of Light's Hope. The houndmasters keep to the kennels at the "
        "north end. Kill the handlers and the hounds won't know what to do.",
        "Then nobody's sending dogs up my road tonight.\n\nThe Crusade calls you lot heretics, you know. I've heard "
        "worse said about better people.",
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")], nxt="ple_arrows_on_the_road"))
    A(Q("ple_arrows_on_the_road", "Arrows on the Road", VARDEN, 58, 59, "Crown Guard",
        "With the hounds gone, the Crusade's sent its archers instead. Every Tyr's Hand Marksman on the walls shoots "
        "at anything on the coast road, and Varden's wagons can't reach Light's Hope that way.\n\nHe wants the walls "
        "cleared.",
        [k("Tyr's Hand Marksman", 8)],
        "The marksmen stand on Tyr's Hand's walls and in its towers. Get close fast, because they won't come down to "
        "you. Don't stop in the open.",
        "My wagons got through this morning. The chapel's eating well tonight.\n\nYou've done more for this road "
        "than half my own people, and I'll say so to anyone.",
        [("head", "armor", "mail", "hunter_precise"), ("waist", "armor", "plate", "crusader"),
         ("back", "armor", None, "physical")]))

    # ---- Corporal Ines Duarte
    A(Q("ple_the_blackwood_shore", "The Blackwood Shore", INES, 56, 57, "Duarte's",
        "Corporal Ines Duarte keeps Crown Guard's water, and Crown Guard's water comes from Blackwood Lake, north of "
        "the camp. The Blackwood Drowned walk out of it every night and foul the shore where she fills the "
        "barrels.\n\nShe wants the shore cleared so she can work.",
        [k("Blackwood Drowned", 10)],
        "North from the camp to the lake. The drowned come up out of the shallows. Stay on the dry ground if you "
        "can, because they're stronger in the water, and they'll try to pull you in.",
        "That's a clean shore, for now.\n\nI ran water treatment for the city of Lisbon, back home. I never thought "
        "I'd be doing it with a sword.",
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")], nxt="ple_whats_in_the_water"))
    A(Q("ple_whats_in_the_water", "What's in the Water", INES, 56, 57, "Duarte's",
        "Ines wants to know how the plague gets into Blackwood Lake, and she thinks the Blackwood Snapjaws can tell "
        "her. They swallow stones to grind their food, and the stones soak up whatever's in the water.\n\nShe wants "
        "their gizzard stones.",
        [fetch("pl_q_gizzard_stone", 6)],
        "The snapjaws sun themselves on the lake shore. The stones are in the gizzard, which is exactly where it "
        "sounds like. I'm sorry, and thank you.",
        "Look at the green on these. It's in the silt, not the water.\n\nSo it's coming from something on the "
        "bottom, and I think I know what.",
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="ple_the_blackwood_drowner"))
    A(Q("ple_the_blackwood_drowner", "The Blackwood Drowner", INES, 57, 57, "Duarte's",
        "Something sits on the bottom of Blackwood Lake and bleeds plague into the silt. The Drowned call it the "
        "Blackwood Drowner, and the Blackwood Snapjaws won't go near the deep water where it lies.\n\nInes wants it "
        "dragged out and ended.",
        [boss("The Blackwood Drowner"), k("Blackwood Snapjaw", 6)],
        "It comes up from the deep end of the lake when it's hungry. Thin the snapjaws on the shore while you wait. "
        "When it pulls you under, don't panic, and fight your way back to the shallows.",
        "The silt's clearing already. You can see the bottom by the reeds.\n\nI've got an idea, and it's bigger "
        "than one lake.",
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="ple_filters_for_felwood"))
    A(Q("ple_filters_for_felwood", "Filters for Felwood", INES, 57, 57, "Duarte's",
        "Ines has drawn up a sand and charcoal filter that takes the plague out of Blackwood's water, and she's "
        "heard there's a forest across the sea, Felwood, where the water's poisoned with something worse. The "
        "Emerald Sanctuary there has a carpenter, Tomasz Wolny, who builds whatever the druids need.\n\nShe wants "
        "her drawings in his hands.",
        [deliver("pl_q_filter_drawings", "Bring Ines's filter drawings to Tomasz Wolny at the Emerald Sanctuary")],
        "Zeppelin from Tirisfal to Orgrimmar, and then north through Ashenvale to Felwood. The Sanctuary's the clean "
        "glade in the middle of it. Tomasz will be the one hammering something.",
        "These are good drawings. She's a proper engineer, this one.\n\nI built houses outside Krakow, back home. I "
        "can build these by the end of the week, and the Sentinels can drink from the stream again.",
        [("legs", "armor", "leather", "bruiser"), ("hands", "armor", "mail", "tide_healer"),
         ("ranged", "weapon", "gun", "hunter_crit")], turn_in_npc_id=TOMASZ,
        grant_items=carry("pl_q_filter_drawings", "Ines's Filter Drawings", "A roll of careful drawings in pencil, "
                                                                           "labelled in Portuguese and then again in "
                                                                           "Common.")))

    # ---- Innkeeper Greta Lowe
    A(Q("ple_horse_for_the_pot", "Horse for the Pot", GRETA, 56, 56, "Hearthside",
        "Innkeeper Greta Lowe feeds Crown Guard, and the wagons from Light's Hope come when they come. She's found "
        "that the Blighted Warhorses on the road are sick on the outside and mostly fine on the inside.\n\nShe wants "
        "the meat, and she doesn't want to hear about it.",
        [fetch("pl_q_warhorse_flank", 6)],
        "The horses run the road on either side of the camp. Cut from the flank, where the meat's thickest. Don't "
        "tell anyone what's in the stew, and I won't either.",
        "That's a week of stew, and nobody needs to know where it came from.\n\nThe newcomers eat anything, have "
        "you noticed? I like cooking for them.",
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")]))
    A(Q("ple_a_barrel_for_sorrow_hill", "A Barrel for Sorrow Hill", GRETA, 56, 57, "Hearthside",
        "Greta brews a dark ale out of whatever the wagons bring, and the innkeeper at Sorrow Hill, Priya Raman, "
        "wrote to say she'd trade a recipe for a barrel. Greta has never been offered a recipe for ale "
        "before.\n\nShe wants the barrel taken west, and the recipe brought back in Priya's head.",
        [deliver("pl_q_ale_barrel", "Bring Greta's barrel of ale to Innkeeper Priya Raman at Sorrow Hill")],
        "West across the Plaguelands to Sorrow Hill, by Uther's Tomb. It's a long way, so fly if you can. Don't "
        "drink it on the way, because I'll know.",
        "Is this Greta's ale? Oh, she actually sent it.\n\nTell her the recipe's my mother's dal, and that it goes with "
        "dark beer better than anything I've ever tasted. I'll write it out for her.",
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "tank"),
         ("main_hand", "weapon", "sword_1h", "caster")], turn_in_npc_id=PRIYA,
        grant_items=carry("pl_q_ale_barrel", "Barrel of Crown Guard Ale", "A small barrel of dark ale, stamped with "
                                                                         "Greta's mark and heavier than it looks.")))

    # ---- Bat Handler Gwen Pike
    A(Q("ple_wild_bats", "Wild Bats", GWEN, 56, 57, "Nightwing",
        "Bat Handler Gwen Pike's riding bats are healthy, and she means to keep them that way. The Carrion Bats "
        "that roost in the trees around the camp carry the plague, and they've started fighting her bats for the "
        "roost.\n\nShe wants the wild ones gone.",
        [k("Carrion Bat", 10)],
        "They roost in the dead trees all around the camp, and they're out every evening. Mine have blue tags on "
        "their legs, so please don't hit those.",
        "My bats slept through the night for the first time in a month.\n\nI've got a young one who's ready for "
        "her own roost, if you're going east.",
        [("legs", "armor", "mail", "earthen"), ("waist", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "high_healer")], nxt="ple_a_bat_for_lights_hope"))
    A(Q("ple_a_bat_for_lights_hope", "A Bat for Light's Hope", GWEN, 57, 57, "Nightwing",
        "Light's Hope's flight master, Aldous Grey, lost two bats to the Mossflayers this month, and Gwen has a "
        "young female ready to fly. She's packed her into a covered basket.\n\nShe wants her taken up the road to "
        "Aldous, gently.",
        [deliver("pl_q_young_bat", "Bring the young bat to Flight Master Aldous Grey at Light's Hope")],
        "East up the road to the chapel. Keep the cover on the basket, because she'll try to fly home if she sees "
        "the sky. Aldous will be at the roost beside the inn.",
        "Oh, she's a lovely one. Look at her ears.\n\nTell Gwen I'll name her after her, and that she'll hate that.",
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")], turn_in_npc_id=ALDOUS,
        grant_items=carry("pl_q_young_bat", "Covered Basket", "A wicker basket under a heavy cloth. Something inside "
                                                              "chirps whenever you stop walking.")))

    # ======================================================================================== LIGHT'S HOPE
    # ---- Commander Eligor Dawnbringer
    A(Q("ple_tyrs_hand", "Tyr's Hand", DAWN, 58, 58, "Dawnbringer's",
        "Commander Eligor Dawnbringer holds Light's Hope for the Argent Dawn, and the Scarlet Crusade holds Tyr's "
        "Hand, a walled town on the coast to the south. The Crusade thinks the Dawn are traitors for taking in "
        "anyone who'll fight.\n\nDawnbringer wants the Tyr's Hand Crusaders on its walls thinned before they come "
        "north.",
        [k("Tyr's Hand Crusader", 10)],
        "Tyr's Hand is south and east of the chapel, on the coast. The crusaders walk its streets and its walls. "
        "They'll fight to the last, so don't expect any of them to run.",
        "Good work, and grim work. I take no joy in killing the living.\n\nBut they'd burn half the people on this "
        "hill for the crime of being newcomers, and I won't allow that.",
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="ple_the_abbots"))
    A(Q("ple_the_abbots", "The Abbots of Tyr's Hand", DAWN, 58, 59, "Dawnbringer's",
        "Tyr's Hand's crusaders fight because the Tyr's Hand Abbots tell them to. The abbots preach in the town's "
        "chapels every morning, and every morning the crusaders come out of those chapels ready to die.\n\n"
        "Dawnbringer wants the preaching stopped.",
        [k("Tyr's Hand Abbot", 8)],
        "The abbots keep to the chapels and the cloister in the middle of Tyr's Hand. They heal each other, so kill "
        "them one at a time and don't let them gather.",
        "The bells didn't ring at Tyr's Hand this morning. I heard the silence from here.\n\nThere's one left who "
        "matters, and he's the worst of them.",
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="ple_abbot_varenne"))
    A(Q("ple_abbot_varenne", "Abbot Varenne", DAWN, 59, 59, "Dawnbringer's",
        "Abbot Varenne rules Tyr's Hand. He was a priest of the Light in Lordaeron before the plague, and he's the "
        "one who decided that anyone who came from somewhere else was a servant of the dead.\n\nDawnbringer knew "
        "him once. He wants it finished.",
        [boss("Abbot Varenne")],
        "He holds the great chapel at the heart of Tyr's Hand, and he doesn't fight alone. Go in with friends, and "
        "watch for the fire when he calls it down.",
        "Then Varenne's gone, and Tyr's Hand will be quieter for a while.\n\nWe studied together at Northshire, a "
        "long time ago. He was kinder then. I'll pray for the man he was.",
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")]))
    A(Q("ple_a_word_with_the_order", "A Word with the Order", DAWN, 58, 58, "Dawnbringer's",
        "Dawnbringer has heard about the Order of the Pale Flame at Sorrow Hill, Scarlets who walked out and kill "
        "only the mindless dead. Some of the Dawn don't trust them. Dawnbringer would like to, and he'd like to "
        "talk to their Flamekeeper, Rory Callahan, about the Crusade.\n\nHe wants his letter carried west.",
        [deliver("pl_q_dawnbringer_letter", "Bring Dawnbringer's letter to Flamekeeper Rory Callahan at Sorrow "
                                            "Hill")],
        "West across the Plaguelands to Sorrow Hill, by Uther's Tomb. It's a long way, so fly. Give it to Rory and "
        "tell him I'd like an answer, not a sermon.",
        "The Argent Dawn wants to talk. Now there's something I didn't think I'd live to see.\n\nTell him yes. Tell "
        "him I'll ride to Light's Hope myself, and that I'm sorry it took the end of the world to get us in one "
        "room.",
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], turn_in_npc_id=RORY,
        grant_items=carry("pl_q_dawnbringer_letter", "Dawnbringer's Letter", "A letter sealed with the Argent "
                                                                             "Dawn's sunburst, addressed in a careful "
                                                                             "hand to the Flamekeeper.")))

    # ---- Archmage Lysander Hale
    A(Q("ple_marrow_of_the_scar", "Marrow of the Scar", HALE, 58, 58, "Hale's",
        "Archmage Lysander Hale breaks down the Scourgestones that come to Light's Hope, and he's noticed something "
        "new in them. It's coming from the Pestilent Scar, where the Scourge is building with bone. The Scar Bone "
        "Constructs that walk there are full of a cold grey marrow.\n\nHe wants some of it, carefully.",
        [fetch("pl_q_scar_marrow", 6)],
        "The Scar's north and west of the chapel, a long gash in the ground full of bones. The constructs walk it. "
        "Cut the marrow from the big bones in their legs, and don't hold it any longer than you have to.",
        "It's cold, isn't it? It's colder than ice and it doesn't melt.\n\nSomething in the Scar is drinking the "
        "warmth out of everything, and now I know what's doing it.",
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")], nxt="ple_the_bone_colossus"))
    A(Q("ple_the_bone_colossus", "The Bone Colossus", HALE, 60, 60, "Hale's",
        "At the bottom of the Pestilent Scar the Scourge has built a giant out of the bones of everyone who died in "
        "the east. Hale calls it the Bone Colossus, and it's what the marrow was for. The Scar Bone Constructs guard "
        "it while it grows.\n\nHale wants it pulled down before it's finished.",
        [boss("The Bone Colossus"), k("Scar Bone Construct", 6)],
        "It stands in the deepest part of the Scar. It's slow, and it's very, very strong. Kill the constructs "
        "first, then take it with every friend you can find.",
        "It's really down? Then the Scar is just a hole in the ground again.\n\nThe Dawn owes you, and so does everyone "
        "who'd have been built into it.",
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))

    # ---- Lightwarden Ysolde Carrow
    A(Q("ple_darrowshires_dead", "Darrowshire's Dead", YSOLDE, 57, 58, "Lightwarden's",
        "Lightwarden Ysolde Carrow keeps the chapel's prayers for the dead, and Darrowshire's dead never got any. "
        "The Darrowshire Spirits are still fighting the battle that killed them, every night, over and over.\n\n"
        "She asks you to set them free.",
        [k("Darrowshire Spirit", 10)],
        "Darrowshire's in the south west, past Crown Guard. The spirits fight in the town square and on the road "
        "in. They won't know the battle's over, so they'll take you for the enemy.",
        "I felt them go. It's quieter in the chapel tonight.\n\nThe newcomers ask me why we pray for the dead here. "
        "I tell them it's because nobody else will.",
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("ring", "armor", None, "hunter_crit")]))
    A(Q("ple_the_pestilent_scar", "The Pestilent Scar", YSOLDE, 57, 57, "Lightwarden's",
        "Ysolde won't send anyone into a place she hasn't seen described, and nobody's come back from the Pestilent "
        "Scar with a straight story. She wants you to walk to its edge and look.\n\nJust look, she says. Don't go "
        "down.",
        [explore(110, 56, "Look into the Pestilent Scar")],
        "North and west of the chapel, past the lake. You'll smell it before you see it. Stand at the edge and look, "
        "and then come straight back here.",
        "Bones, all the way down? Light have mercy on them.\n\nI'll tell the Archmage. He's been waiting for "
        "someone to say it out loud.",
        [("ring", "armor", None, "spirit_caster"), ("feet", "armor", "mail", "hunter_precise"),
         ("wrist", "armor", "plate", "plate_healer")]))
    A(Q("ple_the_shadowhunters", "The Shadowhunters", YSOLDE, 58, 58, "Lightwarden's",
        "Somebody's been hexing the chapel. Ysolde has found little bundles of feathers and teeth under the pews, "
        "and the Mossflayer Shadowhunters of Zul'Mashar are the only ones who'd do that.\n\nShe wants the "
        "shadowhunters dead before they get bolder.",
        [k("Mossflayer Shadowhunter", 8)],
        "Zul'Mashar's in the far north east, past the lodge. The shadowhunters keep to the temple steps. Their hexes "
        "are nasty, so get a priest to look at you when you're back.",
        "There was nothing under the pews this morning. Thank the Light.\n\nI found something odd on one of the "
        "bundles, and I'd like a closer look.",
        [("chest", "armor", "cloth", "caster"), ("legs", "armor", "plate", "strength"),
         ("hands", "armor", "leather", "wildheart")], nxt="ple_hex_fetishes"))
    A(Q("ple_hex_fetishes", "Hex Fetishes", YSOLDE, 58, 59, "Lightwarden's",
        "The hex bundles under the pews were tied around scraps of the chapel's own laundry. Somebody's been "
        "stealing from the chapel for the Mossflayers. Ysolde wants the fetishes the Mossflayer Shadowhunters still "
        "carry, so she can see whose cloth is in them.",
        [fetch("pl_q_hex_fetish", 5)],
        "The shadowhunters at Zul'Mashar carry their fetishes on their belts. Bring them back unopened. I'll know "
        "the cloth when I see it.",
        "That's the infirmary's linen, every scrap.\n\nSomebody's been selling them our sheets. I'll find out who, "
        "and then we'll have a long talk.",
        [("shoulder", "armor", "mail", "earthen"), ("head", "armor", "cloth", "caster_crit"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    # ---- Sergeant Marisol Reyes
    A(Q("ple_troll_medicine", "Troll Medicine", MARISOL, 57, 58, "Reyes's",
        "Sergeant Marisol Reyes runs Light's Hope's infirmary, and she's noticed that the Mossflayer trolls heal "
        "faster than anybody else in the Plaguelands. The Mossflayer Scouts carry herb pouches, and she wants to "
        "know what's in them.\n\nShe isn't too proud to learn from a troll.",
        [fetch("pl_q_herb_pouch", 5)],
        "Zul'Mashar's in the far north east. The scouts range out from the temple in pairs. Bring me the pouches "
        "closed, because I want to see how they pack them.",
        "Kingsblood, and something I don't know, and a lot of salt.\n\nI was a paramedic in Monterrey, back home. "
        "Half of what I know I learned from grandmothers, so I'm not surprised the trolls know a thing or two.",
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "strength")], nxt="ple_mossflayer_raiders"))
    A(Q("ple_mossflayer_raiders", "Mossflayer Raiders", MARISOL, 58, 58, "Reyes's",
        "Marisol's wagons bring the wounded up from Crown Guard, and the Mossflayers have started raiding them. The "
        "Mossflayer Warriors hit the wagons from the trees and the Mossflayer Scouts pick off whoever runs.\n\nShe "
        "wants the road safe for the wounded.",
        [k("Mossflayer Warrior", 8), k("Mossflayer Scout", 6)],
        "They come down from Zul'Mashar to the north road. Go up there and hit them at home. They're fast and "
        "they're angry, so don't fight more than you can handle.",
        "No raids yesterday, and none today. My wounded came in alive.\n\nThere's one more of them I'd like to see "
        "gone, and he's the one giving the orders.",
        [("feet", "armor", "leather", "assassin"), ("head", "armor", "plate", "crusader"),
         ("wrist", "armor", "cloth", "healer")], nxt="ple_zulmashar_the_last"))
    A(Q("ple_zulmashar_the_last", "Zul'Mashar the Last", MARISOL, 59, 59, "Reyes's",
        "The Mossflayers follow a warlord who named himself after their city. Zul'Mashar the Last says he's the "
        "last of the old Amani blood, and he's sworn to drive everyone out of the east who isn't a troll.\n\n"
        "Marisol wants the raids to stop for good.",
        [boss("Zul'Mashar the Last")],
        "He holds the top of the temple at Zul'Mashar. He's big, and he hits like a falling tree. Take friends, and "
        "bring bandages, because you'll need them.",
        "Then it's over. My wagons can run every day now.\n\nI took an oath to look after the sick and the hurt. I "
        "never thought I'd be sending people to kill a warlord to do it.",
        [("hands", "armor", "plate", "strength_crit"), ("shoulder", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "caster")]))
    A(Q("ple_the_medics_network", "The Medics' Network", MARISOL, 58, 58, "Reyes's",
        "The transplant medics keep in touch across the sea as best they can. Marisol has written up what the "
        "Mossflayer herbs do, and she wants her notes in the hands of Marcus Oyelaran, a paramedic at Talonbranch "
        "Glade in Felwood.\n\nThe burns up there are the same kind she's treating here.",
        [deliver("pl_q_medic_notes", "Bring Marisol's notes to Marcus Oyelaran at Talonbranch Glade")],
        "Zeppelin from Tirisfal to Orgrimmar, then north through Ashenvale to Felwood, and up to Talonbranch at the "
        "top. Marcus will be the one with his sleeves rolled up. Don't let the notes get wet.",
        "Marisol from Monterrey? We trained on the same course, years ago, back home in a hotel conference room in "
        "Houston.\n\nThis is going to save people up here. Tell her I owe her a coffee, if anyone ever finds coffee "
        "again.",
        [("chest", "armor", "plate", "strength"), ("waist", "armor", "cloth", "high_healer"),
         ("ranged", "weapon", "bow", "hunter")], turn_in_npc_id=MARCUS,
        grant_items=carry("pl_q_medic_notes", "Marisol's Notes", "A bundle of notes in a quick, slanted hand, with "
                                                                 "pressed leaves taped beside every recipe.")))

    # ---- Ranger Faelis Dawnreach
    A(Q("ple_the_restless_lodge", "The Restless Lodge", FAELIS, 57, 57, "Dawnreach's",
        "Ranger Faelis Dawnreach served at Quel'Lithien Lodge in the north, where the high elves kept watch on "
        "Lordaeron's border. The lodge fell with everything else, and the Restless Lodge Rangers still walk their "
        "posts. He served beside every one of them.\n\nHe asks you to let them rest.",
        [k("Restless Lodge Ranger", 8)],
        "Quel'Lithien Lodge is in the north, past the lake. They'll be on the walls and in the trees, where they "
        "always stood. They still shoot straight, so keep moving.",
        "They're resting now, all of them. I could hear them stop.\n\nThey each carried a token, a silver leaf. I'd like them back, "
        "if you'd go once more.",
        [("chest", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "tank"),
         ("back", "armor", None, "caster")], nxt="ple_the_silver_leaves"))
    A(Q("ple_the_silver_leaves", "The Silver Leaves", FAELIS, 57, 58, "Dawnreach's",
        "Every ranger of Quel'Lithien carried a silver leaf on a green cord, a token from Quel'Thalas. Faelis wants "
        "to send them home, so that somebody there knows their names. The Restless Lodge Rangers still wear them.",
        [fetch("pl_q_ranger_token", 6)],
        "The rangers at the lodge still wear their tokens around their necks. Bring back what you find. Not every "
        "one of them will still have theirs, and I'm sorry for that.",
        "That's Seren's, and Calanor's, and this one was Ilyeth's, who always sang off key.\n\nI'll send these north. The lodge's lord is still out "
        "there, though, and he won't rest until someone makes him.",
        [("legs", "armor", "leather", "bruiser"), ("head", "armor", "plate", "strength"),
         ("ranged", "weapon", "wand", "caster")], nxt="ple_ranger_lord_saelith"))
    A(Q("ple_ranger_lord_saelith", "Ranger-Lord Saelith", FAELIS, 59, 59, "Dawnreach's",
        "Ranger-Lord Saelith commanded Quel'Lithien Lodge. He was Faelis's captain and his friend, and he died "
        "holding the gate. He still holds it, and he still kills anyone who comes through.\n\nFaelis can't do it "
        "himself. He's asking you.",
        [boss("Ranger-Lord Saelith")],
        "He stands at the lodge's inner gate, where he fell. He's fast and he doesn't miss. Go with friends, and "
        "close the distance quickly.",
        "Then the lodge is quiet, and he's free.\n\nHe taught me to shoot. He taught half the lodge. Thank you for "
        "doing what I couldn't.",
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")]))

    # ---- Innkeeper Jessa Moonfield
    A(Q("ple_lamp_oil", "Lamp Oil", JESSA, 56, 57, "Lightwarden's",
        "Innkeeper Jessa Moonfield keeps the chapel's lamps lit all night, because the dead don't like the light, and "
        "she's running out of oil. The Plague-Rotted Bears carry fat under the rot that renders down clean.\n\nShe "
        "wants enough to keep the lamps lit until the wagons come.",
        [fetch("pl_q_bear_fat", 6)],
        "The bears wander the woods all around the chapel. Cut the fat from the back, where the rot's thinnest. It "
        "won't smell nice, and I'm sorry about that.",
        "That'll keep the lamps burning for a fortnight.\n\nThe newcomers say they're used to lights that never go "
        "out. I'd love to see that, one day.",
        [("shoulder", "armor", "leather", "hunter_crit"), ("waist", "armor", "plate", "tank"),
         ("main_hand", "weapon", "polearm", "agility")]))

    # ======================================================================================== DARROWSHIRE
    # ---- Pamela Redpath
    A(Q("ple_pamelas_doll", "Pamela's Doll", PAMELA, 57, 57, "Darrowshire",
        "A little girl's ghost waits in the ruins of Darrowshire. Her name's Pamela Redpath, and she doesn't seem "
        "to know she's dead. She's lost her doll, and she says the Darrowshire Ghouls took it.\n\nShe'd very much "
        "like it back.",
        [fetch("pl_q_pamelas_doll", 1)],
        "The ghouls took her, they did! They're all over the town. She's got a blue dress and one button eye, and "
        "her name's Dolly.",
        "That's Dolly, you found her! She's all muddy, but that's all right.\n\nDaddy's going to be so happy when he gets "
        "home. He's been gone ever so long.",
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")], nxt="ple_a_letter_for_auntie"))
    A(Q("ple_a_letter_for_auntie", "A Letter for Auntie", PAMELA, 57, 57, "Darrowshire",
        "Pamela has written a letter to her Auntie Marlene, who lived out west near Andorhal. She wants it carried "
        "to the people at Sorrow Hill, who she's heard are kind and keep a book of names.\n\nShe doesn't know that "
        "Andorhal is gone.",
        [deliver("pl_q_pamelas_letter", "Bring Pamela's letter to Chaplain Odile Marchand at Sorrow Hill")],
        "Auntie lives near the big town in the west. The lady at the hill will know where. You'll be ever so "
        "careful with it, won't you?",
        "Oh, this is from a child. Darrowshire, she says.\n\nMarlene Redpath's in my book. She died in Andorhal, "
        "with everyone else. I'll write back to Pamela, and I'll tell her that her auntie loved her. That part's "
        "true.",
        [("feet", "armor", "mail", "earthen"), ("wrist", "armor", "leather", "agility"),
         ("back", "armor", None, "caster")], turn_in_npc_id=ODILE, nxt="ple_where_daddy_is",
        grant_items=carry("pl_q_pamelas_letter", "Pamela's Letter", "A letter in a child's big round letters, with a "
                                                                    "drawing of a house and a doll on the back.")))
    A(Q("ple_where_daddy_is", "Where Daddy Is", PAMELA, 58, 58, "Darrowshire",
        "Pamela's father, Captain Joseph Redpath, led Darrowshire's defence and fell in it, and then he got up "
        "again. Captain Redpath's Shade still walks the battlefield south of the town, still fighting, and Pamela "
        "is still waiting for him to come home.\n\nThe only way he'll come home is if someone sets him free.",
        [boss("Captain Redpath's Shade")],
        "Daddy's at the big fight, south of the houses. He's very brave. Tell him I've been good, and that I've got "
        "Dolly back.",
        "You saw him? Is he coming?\n\nHe's here, I can see him, and he's smiling. Thank you, thank you. We're going "
        "home now.",
        [("main_hand", "weapon", "polearm", "strength"), ("head", "armor", "cloth", "high_healer"),
         ("hands", "armor", "leather", "hunter")]))

    # ---- the Bone Mines, under the Pestilent Scar (tools/handbuilt_plaguelands_caves.py)
    A(Q("ple_the_bones_of_the_east", "The Bones of the East", YSOLDE, 58, 59, "Lightwarden's",
        "Lightwarden Ysolde Carrow prays for every dead soul in the east, and she's found out where some of them "
        "went. The Scourge has dug a mine under the Pestilent Scar, and the Bone Miners in it are digging up the "
        "east's dead to build its constructs.\n\nShe wants the digging stopped, and the Scourge Pit Guards who keep "
        "the miners at it.",
        [k("Bone Miner", 10, BM), k("Scourge Pit Guard", 6, BM)],
        "The mine's in the hill under the Pestilent Scar. Every gallery's deeper than the last, so it's a long walk "
        "down. The pit guards keep the miners at their work, and they'll keep you out if they can.",
        "Those were people once, the bones they were digging up. Somebody's grandfather, somebody's child.\n\nI'll "
        "say the prayer for all of them at once. It's not enough, but it's what I've got. Faelis wants a word with "
        "you about whoever's running the place.",
        [("chest", "armor", "leather", "bear"), ("hands", "armor", "cloth", "void"),
         ("feet", "armor", "mail", "earthen")], nxt="ple_the_overseer"))
    A(Q("ple_the_overseer", "The Overseer", FAELIS, 59, 60, "Ranger's",
        "Ranger Faelis Dawnreach watched the Bone Mines from the ridge for three nights, and she's seen who runs "
        "them. Overseer Marrowgrim sits in the pit at the bottom with a meat hook and a cart, and nothing leaves "
        "the mine that he hasn't weighed.\n\nShe wants him dead before the Scourge has bone enough for another "
        "colossus.",
        [boss("Overseer Marrowgrim", BM)],
        "He's in the marrow pit at the end of the deepest gallery. He's big and he's slow until he isn't, so don't "
        "stand where that hook can reach you. And watch out for the cart.",
        "The Scar's quieter already, and the bats have stopped circling it.\n\nAt the lodge we used to say you "
        "don't kill the wolf, you kill whoever keeps it fed. Somebody's still keeping him fed, though.",
        [("legs", "armor", "plate", "strength"), ("shoulder", "armor", "mail", "hunter"),
         ("main_hand", "weapon", "wand", "dark_haste")], nxt="ple_the_ossifier"))
    A(Q("ple_the_ossifier", "The Ossifier", FAELIS, 60, 60, "Ranger's",
        "Faelis has found a workshop off the middle of the Bone Mines, and Marrowgrim's tallies say everything the "
        "mine digs up goes there first. The Ossifier is a necromancer, and he's the one who turns the east's dead "
        "into the Scourge's constructs.\n\nShe wants the workshop closed.",
        [boss("The Ossifier", BM)],
        "The workshop's off the middle gallery, up a short passage. He'll be wearing bone armour, and it's thick, so "
        "be patient with it. Break that first, then break him.",
        "That's the end of the Bone Mines, and the end of the constructs coming out of them.\n\nI couldn't save "
        "anyone at the lodge. I'm glad I could do something for the ones who were already gone.",
        [("head", "armor", "cloth", "fel"), ("waist", "armor", "leather", "blood"),
         ("main_hand", "weapon", "axe_2h", "strength_crit")]))

    # ---- in from Arathi: Hammerfall's answer
    A(Q("ple_hammerfalls_answer", "Hammerfall's Answer", GATHROK, 55, 56, "Overlord's",
        "Overlord Gath'rok holds the middle of Arathi, and everything that crosses it crosses in front of him. "
        "Lately that's been the Argent Dawn's carts heading east, and the Dawn has asked Hammerfall for steel.\n\n"
        "Gath'rok wants his answer carried to Commander Eligor Dawnbringer at Light's Hope Chapel.",
        [deliver("pl_q_gathroks_answer", "Bring Gath'rok's answer to Commander Eligor Dawnbringer at Light's Hope")],
        "Go north to the Plaguelands and take the road east as far as it runs. Light's Hope is at the end of it. "
        "Tell the commander Hammerfall keeps its word, and don't stop to fight anything you can walk past.",
        "Hammerfall's answer, and it's yes. The Overlord doesn't waste words, does he?\n\nWe don't ask the "
        "newcomers where they came from here, and we don't ask anyone else either. We ask whether they'll stand on the wall tonight, so will you?",
        [("wrist", "armor", "leather", "physical"), ("chest", "armor", "mail", "battlemage"),
         ("back", "armor", None, "sturdy_caster")], zone="arathi_central", turn_in_npc_id=DAWN,
        grant_items=carry("pl_q_gathroks_answer", "Gath'rok's Answer", "A strip of hide branded with Hammerfall's "
                          "mark and a few lines in Orcish, rolled tight and tied with sinew.")))
    return out
