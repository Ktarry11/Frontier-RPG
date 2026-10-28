"""
Aspen Wilderness quest pass.  Idempotent.

    PYTHONPATH=. python3 tools/build_aspen_quests.py

Writes data/quests/aspen.json, adds fetch and starter drops to data/creatures/quest_drops.json, and
splices the three inbound quests into their own zones' files (Camp Taurajo, Orgrimmar, Eastern Hillsbrad).

NO ESCORTS (Kyle's standing rule, and the only hard "never" in quest design).
NO QUESTS BUILT AROUND RARES - the five named rares here are lore and loot, never an objective.

THE ZONE'S ONE IDEA, AND EVERY QUEST SERVES IT: THE ROAD SOUTH IS CUT, AND EVERYTHING IN THE WAY IS NEW.

The Great Lift carried people down off the Barrens plateau into Thousand Needles. It is gone, and a
mountain range nobody has a name for is standing where the drop used to be. So every quest in this zone is
some version of the same problem - getting down, or working out what you are getting down THROUGH.

Three populations are trying to answer that at once and none of them are from here:
  * The TAUREN at Longstand Camp came south after Thunder Bluff fell and stopped at the first country with
    timber in it. They are learning to log aspen and they hate how good they are getting at it, because
    competence here is proof they are not going home.
  * The QUILBOAR and HARPIES were pushed UP out of the Barrens when the mountain took their ground. They
    are not here because they like it.
  * The YETIS came across inside the glacier and are cornered at the one end of it still frozen.

USES THE WHOLE TOOLKIT (Kyle: "keep in mind all quest options"):
  inbound      three quests from three different places send a player here, so the zone is not a thing you
               only find by walking into it: Camp Taurajo wants the road south, Orgrimmar wants to know
               what the Warchief now borders, and an apothecary in Tarren Mill has heard there are yetis
               in Kalimdor, which is not possible.
  deliver      the Tarren Mill query walks across an ocean and hands in at Longstand Camp.
  craft        Longstand mills its own planks. The whole camp's trade in one objective.
  starter      two quests begin as loot - a cable-end off a harpy nest, and a surveyor's pin off the
               quilboar who took it.
  requires     one Linken-style gate: the last quest needs a Camp Taurajo quest AND the cave boss, and
               hands in back at Camp Taurajo. Skip either and it never opens.
  explore      four, because this zone is a descent and knowing where the ways down ARE is content.

WRITING STANDARD (Kyle): no "kill X of Y down by the Z, # of them if you will". The accept line is a
PERSON TALKING and the numbers live inside what they say.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/aspen.json"
ASP = "the_aspen_wilderness"
ICE = "the_weeping_ice"
TAU, ORG, HBE = "camp_taurajo", "orgrimmar", "eastern_hillsbrad"

XP = {25: 1640, 26: 1720, 27: 1800, 28: 1880, 29: 1960, 30: 2040, 31: 2120, 32: 2200}
GOLD = {25: 6900, 26: 7200, 27: 7500, 28: 7800, 29: 8100, 30: 8400, 31: 8700, 32: 9000}

# The zone's gear flavour. Aspen and altitude at the top, the Seam's red dust, and ice at the bottom of
# the cave. Nothing here is Earth-made; the mountain is the only thing that came across.
tirisfal_gear.THEMES.update({
    "aspen": (["Aspen", "Goldwood", "Pale-Bark", "Quaking", "Stand-Cut"],
              ["Cut from wood that was not on this continent four years ago.",
               "White bark takes a mark and keeps it forever.",
               "Light in the hand, the way seasoned aspen goes.",
               "The whole stand is one tree. Nobody here knew that."]),
    "seam": (["Seam", "Redscrub", "Wrong-Side", "Dust-Caught", "Line-Walker's"],
             ["Red dust in the seams that will not wash out.",
              "Found with one half in leaf mould and one half in Barrens clay.",
              "It came across. Nobody asked it to.",
              "Two kinds of dirt on it and no ground that makes both."]),
    "rim": (["Rim", "Chute-Run", "Long-Drop", "Escarpment", "Winch-House"],
            ["Carried down a cliff by somebody in a hurry.",
             "Scoured clean by whatever comes down that gully every spring.",
             "Lift-house issue, and the lift is at the bottom.",
             "Everything up here is roped to something."]),
    "glacier": (["Glacier", "Meltwater", "Weeping-Ice", "Old-Cold", "Moulin"],
                ["Wet when you pick it up and wet an hour later.",
                 "Frozen into a wall that has started letting go of things.",
                 "Cold the way very old ice is cold.",
                 "It came out of the ice this spring. It had been in there a while."]),
    "quilboar": (["Thornhide", "Bristle-Cut", "Uphill", "Wintered", "Den-Carved"],
                 ["Desert work, and it was never meant to be wet.",
                  "They dug in when the cold came. Nobody taught them to.",
                  "Thorn and sinew, and the thorn is not from any plant up here.",
                  "Carried uphill by somebody who did not want to come."]),
})


def k(target, n, zone=ASP):
    return kill(target, n, zone=zone)


def boss(target, zone=ICE):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x, y, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def craft(recipe, label, n=1):
    return dict(type="craft", target=recipe, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None,
      **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             rewards=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3))
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# NPC shorthands
GATE, LIFT, SEAM = "asp_gate_scout", "asp_lift_keeper", "asp_seam_watcher"
ROPE, RUNNER, CAVE = "asp_rope_master", "asp_rim_runner", "asp_cave_watch"
ELDER, LOGGER, HUNTER = "asp_camp_elder", "asp_logger", "asp_camp_hunter"
MEADOW, BENCH = "asp_meadow_scout", "asp_bench_warden"
T_WRANGLER, T_SCOUT, T_LIAISON = "taurajo_kodo_wrangler", "taurajo_warband_scout", "taurajo_orc_liaison"
O_ELDER = "org_elder_2"
H_APOTH = "hbe_mill_apothecary"


# =========================================================================================================
# INBOUND - three places, three reasons. A zone nobody is sent to is a zone most players never open.
# =========================================================================================================
def inbound():
    A = []
    A.append(Q("tau_road_south", "The Road South", T_WRANGLER, TAU, 25, 26, "seam",
        "Wrangler Tull drove kodo down the Great Lift twice a year for most of his life. The Lift is gone "
        "and so is the cliff it hung on, and in their place is a mountain that has been there four years "
        "and will not be explained.\n\nTaurajo has had no word from anything south of it since. Not from "
        "Freewind, not from the flats, not from the salt crews. Somebody has to walk up and look.",
        [explore(ASP, 105, 14, 8)],
        "Go up past where the Lift used to stand. You will know the spot - the winch house is still "
        "bolted to the rock and the cable runs out thirty feet and straight into granite.\n\nPast that "
        "there is a seam in the ground where red dust stops and leaf mould starts, sharp as a knife cut. "
        "Stand on it and tell me what is on the far side. That is all. Do not go down anything yet.",
        "Trees. You are telling me there are trees.\n\nI drove that road for twenty years. There was "
        "nothing up there but sky and a very long drop, and now you are telling me there are trees on it."))

    A.append(Q("org_new_border", "What We Border Now", O_ELDER, ORG, 25, 27, "rim",
        "Elder Torgun's job is knowing where the Horde's edges are. For four years the southern edge of "
        "the Barrens has been a mountain range, and the best report Orgrimmar has on it was written by a "
        "scout who went up to the treeline and came back down the same afternoon.\n\nThe Warchief does "
        "not need poetry about it. He needs to know whether anything is coming through.",
        [explore(ASP, 103, 44, 8), k("Rimcliff Harpy", 8)],
        "Get to the escarpment - the long drop where the Lift's cliff used to be. Garuk Emberhide is up "
        "there already and has been for a season, so find him if you want the short version.\n\nThe "
        "harpies on that rim are the part I care about. Barrens harpies, up a mountain, nesting on rock "
        "instead of in the crags they were born in. Thin them where you find them and count what you see.",
        "Pushed up, not moved in. That is a different report and a worse one.\n\nIf the mountain took "
        "their ground then it took somebody else's too, and whatever that was has gone somewhere."))

    A.append(Q("hbe_impossible_yetis", "A Matter of Impossibility", H_APOTH, HBE, 27, 29, "glacier",
        "Apothecary Lydon has spent eleven years on Alterac yeti and considers himself the authority, "
        "which he is, because nobody else wanted it.\n\nA caravan master came through Tarren Mill with a "
        "story about yeti on the other side of the world, in a desert province of Kalimdor, and Lydon has "
        "been unable to put it down. Yeti do not cross oceans. The caravan master was very sure.",
        [deliver("sealed_yeti_query", "Deliver the sealed query to Elder Mura Longstand")],
        "I am not asking you to believe it. I am asking you to carry this across an ocean and put it in "
        "the hand of whoever is senior at that camp, and let them tell me I am wasting my time.\n\nIt is "
        "sealed. Do not open it. The questions in it are embarrassing and I would like them answered "
        "before they are laughed at.",
        "He writes a very careful letter for a man who has already decided.\n\nTell him yes. Tell him "
        "there are yeti in this mountain and we would all be happier if there were not.",
        turn_in_npc_id=ELDER,
        grant_items=carry("sealed_yeti_query", "Sealed Query",
                          "Apothecary Lydon's questions, sealed with wax and a thumbprint. It is heavier "
                          "than a letter has any business being.")))
    return A


# =========================================================================================================
# THE HIGH BASIN - the gate, the Lift, and the Seam. Levels 25-26.
# =========================================================================================================
def basin():
    A = []
    A.append(Q("asp_winch_house", "What the Winch House Kept", LIFT, ASP, 25, 25, "rim",
        "Keeper Nalu worked the north winch for eleven years and was off shift the day the ground "
        "changed. She has been back up to the platform most weeks since.\n\nThe house is still standing. "
        "The ledgers are still in it, and so is a season of mail that was waiting to go down and never "
        "did. She has not been able to make herself go through it.",
        [fetch("lift_ledger", 3), fetch("undelivered_mail", 5)],
        "The ledgers will be in the iron box under the drum. Three of them, if the damp has not taken "
        "more.\n\nThe mail is loose in the sorting rack and some of it will have blown. Bring what is "
        "still readable. I know what is in most of it and I would still rather read it than not.",
        "This one is from a girl in Freewind to her brother on the top side. Dated the week before.\n\nI "
        "am not going to be able to deliver it. I would like to keep it anyway.", nxt="asp_cable_run"))

    A.append(Q("asp_cable_run", "Thirty Feet and Into Rock", LIFT, ASP, 25, 26, "rim",
        "The main cable still comes out of the drum, runs the thirty feet it always ran, and goes into "
        "the granite as though the granite had grown round it. Which, Nalu points out quietly, is "
        "approximately what happened.\n\nShe wants to know how much of it is in there.",
        [explore(ASP, 104, 30, 6), fetch("severed_cable_end", 4)],
        "Follow it down to where the rock takes it and look at the face there. Harpies have been at the "
        "ends - they like the wire for their nests and they have cut what they could reach.\n\nBring me "
        "the pieces back. Four would tell me what I want to know. Mind the rim while you are at it; there "
        "is a long way down and only a few places to do it on purpose.",
        "Clean cut on two of these and sheared on the others. So it was still under load when the ground "
        "came.\n\nSomething was on the cable. I have been avoiding that thought for four years."))

    A.append(Q("asp_wrong_side", "The Wrong Side of the Line", SEAM, ASP, 25, 26, "seam",
        "Watcher Tomak keeps the Seam, which mostly means watching things die slowly on the wrong side "
        "of it.\n\nThe kodo are the worst of it. Barrens animals, standing in snow, four years into a "
        "winter their kind has no word for. They do not graze. They do not go back. They stand at the "
        "line and they are not going to stop standing there on their own.",
        [k("Seam-Struck Kodo", 10)],
        "I will not dress this up. They are suffering and they are going to keep suffering, and the only "
        "thing anybody can do for them is the thing nobody wants to do.\n\nTen of them. Do it clean and "
        "do it from the front, because they will not run and it is worse if you make them try.",
        "My grandmother drove kodo. I grew up with them under the tent flap.\n\nThank you for doing it "
        "properly. Most people do not."))

    A.append(Q("asp_red_ground", "A Handful of Home", SEAM, ASP, 26, 26, "seam",
        "The camp downslope has been under trees for four years and has not once stood on its own "
        "ground. Tomak has been quietly collecting Barrens soil off the Seam and sending it down.\n\nIt "
        "is not for growing anything. It is for the floor of the elder's lodge, so there is red dirt "
        "under somebody's feet when it matters.",
        [fetch("seam_red_earth", 8), k("Redscrub Scavenger", 8)],
        "Take it off the dust side of the line, not the mould side. It has to be the real thing or there "
        "is no point.\n\nThe scavengers will be on you the whole time. They nest in the dead scrub and "
        "they have worked out that anybody crouching is not watching. Deal with them first if you have "
        "sense, which I am told is not guaranteed.",
        "It goes under the lodge floor tonight.\n\nMura will stand on it and say nothing about it, and everyone will know, and that is how it should be done."))

    A.append(Q("asp_rope_trade", "An Honest Opportunity", ROPE, ASP, 26, 27, "rim",
        "Fizzik Quickline arrived on the rim with forty coils of rope and a conviction that a cliff with "
        "no road down it is the finest business proposition in Kalimdor.\n\nHe is right. He is also "
        "running out of rope, and the only thing up here strong enough to replace it is harpy sinew, "
        "which is a sentence he says far too cheerfully.",
        [k("Rimcliff Harpy Windcaller", 6), fetch("harpy_sinew_coil", 10)],
        "Windcallers first. The plain ones will mob you but the callers are what makes a mob a problem, "
        "and I would rather you came back.\n\nTen coils of sinew gets me through the season. I pay fair, "
        "which in my family is a serious admission.",
        "Fair's fair. And listen - the ways down are free. I am not charging anybody for knowing where a "
        "gully is. Rope is a product. Knowledge is advertising."))
    return A


# =========================================================================================================
# THE RIM - the descent itself, and the two starter drops. Levels 26-28.
# =========================================================================================================
def rim():
    A = []
    A.append(Q("asp_ways_down", "Four Ways Down", RUNNER, ASP, 26, 27, "rim",
        "Ash Winterfall runs the chutes, which everybody tells him not to do. A chute is an avalanche "
        "path - swept clean every few winters by something enormous coming down it - and that scouring is "
        "exactly what makes it the only walkable line on a face of loose rock.\n\nDangerous ground and "
        "the only route are the same ground. He finds this funnier than the elders do.",
        [explore(ASP, 104, 40, 6), explore(ASP, 50, 44, 7), explore(ASP, 154, 42, 7)],
        "Three of the four. Take the middle one first, under the Lift - it is the widest and if you "
        "cannot do that one you should not do the others.\n\nThen the west gully and the east. Walk them, "
        "do not run them, and do not do it in the afternoon when the sun has been on the snowfield all "
        "day. That is when they go.",
        "You have them. That is the zone, then - everything below the rim is reachable and everything "
        "above it is the Barrens.\n\nI have been trying to get the elders to send a proper trail crew for "
        "two winters. Maybe they listen to somebody who has actually been down."))

    A.append(Q("asp_rim_harpies", "Nesting Where They Should Not", GATE, ASP, 27, 28, "rim",
        "Garuk has been counting harpies since the thaw and does not like the number. They nest on the "
        "escarpment now, which is at least rock and at least a cliff.\n\nIt is the ones further down that "
        "bother him - harpies roosting in aspen crowns, in trees, which is not a thing harpies do. "
        "Something has taught them to and he would like it to stop.",
        [k("Rimcliff Harpy", 12), k("Rimcliff Harpy Windcaller", 6)],
        "Work the rim first and then the stands below it. The tree-roosters are the dangerous ones - you "
        "cannot see them until they are already coming and they have learned to wait.\n\nI am not asking "
        "for a cull. I am asking for enough of a dent that I can tell Orgrimmar the number went down "
        "once.",
        "Good. Write it in your own hand on the tally and I will send it with mine.\n\nTwo witnesses is "
        "the difference between a report and a rumour, and the Warchief has had enough rumours about this "
        "mountain."))

    # ---- STARTER DROP 1: the cable end
    A.append(Q("asp_the_load", "What Was On The Cable", "item:wound_cable_end", ASP, 27, 28, "rim",
        "You turn the wire over. It is Lift cable, the heavy stuff, and it has been wound into the base "
        "of a harpy nest with the patience of something that liked the shape of it.\n\nThe end is not "
        "cut. It is stretched - drawn out thin and snapped, the way wire goes when it has been pulled "
        "past what it can hold. Something was hanging on this when the ground changed.",
        [fetch("wound_cable_end", 1), explore(ASP, 104, 34, 6)],
        "Nalu kept the winch for eleven years. She will know what a load looks like on a cable end and "
        "she will know what no load looks like.\n\nTake it to her. Look at the cliff face under the Lift "
        "on the way, where the main line goes into the rock, and see whether there is anything below it.",
        "She does not say anything for a while.\n\n'Full car,' she says. 'Going down.' Then she puts it "
        "in the iron box with the ledgers and closes the lid, and that is the end of the conversation.",
        turn_in_npc_id=LIFT))
    return A


# =========================================================================================================
# LONGSTAND CAMP - the tauren, and learning a tree. Levels 27-29.
# =========================================================================================================
def camp():
    A = []
    A.append(Q("asp_green_wood", "Green Wood, Dry Wood", LOGGER, ASP, 27, 28, "aspen",
        "Hateg Barkhand has been told aspen is a poor timber by three different people who had never "
        "touched it. Green it is heavy and soaking and splits like wet rope. Seasoned it goes light as "
        "nothing and takes a nail without complaint.\n\nThe camp has been seasoning it wrong for two "
        "winters because everything they knew was about a different wood.",
        [fetch("sound_aspen_bolt", 12), k("Goldwood Lynx", 6)],
        "Standing dead, not fallen. Fallen has been in the wet and it is no use to me whatever it looks "
        "like.\n\nTwelve bolts will tell me whether the rot runs up from the root or down from the crown. "
        "And watch the lynx - they lie up in the deadfall and you will be bent over with an axe.",
        "Down from the crown. Every one of them.\n\nSo we have been stacking it upside down for two "
        "winters. Two winters. Do not tell Mura; I would like to tell her myself.", nxt="asp_first_planks"))

    A.append(Q("asp_first_planks", "The First Good Planks", LOGGER, ASP, 28, 29, "aspen",
        "Knowing which way the rot runs is not the same as having a floor. Longstand has a mill, a pile "
        "of bolts stacked the right way up at last, and nobody who has cut a plank that came out true.\n"
        "\nHateg would like the first honest stack of boards this camp has ever produced, and he would "
        "like somebody else's hands on the saw while he watches what they do wrong.",
        [craft("plank_ironbark", "Mill planks at the camp saw", 6)],
        "Six boards. Not six attempts - six that I would put in a wall.\n\nThe trick is the first cut. "
        "Get that off true and every board after it is off true and you will not see it until the wall "
        "is up and the door does not close. Take your time on the first one and the rest follow.",
        "That is a stack of boards. That is an actual stack of boards.\n\nMy father built a tent frame "
        "every spring of his life and never once needed a plank. I am going to think about that later, "
        "when I am less pleased."))

    A.append(Q("asp_winter_meat", "Meat for a Winter We Do Not Know", HUNTER, ASP, 27, 28, "aspen",
        "Sani Quietstep hunted open plain her whole life, where you see a herd at dawn and you have it by "
        "noon. Up here the elk go into timber and simply stop existing.\n\nShe has got better. She is not "
        "good yet, and the camp has to eat through a winter nobody has measured.",
        [k("Aspen Elk", 12), fetch("thick_elk_haunch", 8)],
        "Work the edges of the stands, not the middle. They cross between cover at the same places every "
        "day and that is the only predictable thing about them up here.\n\nEight good haunches. Leave the "
        "thin ones - we are not so short that we take a poor animal, and I would rather not start.",
        "Eight, and not a thin one among them. You hunted the edges.\n\nI will be good at this in another two winters. I would rather be bad at it on open ground, but nobody asked me."))

    A.append(Q("asp_wolf_nights", "The Nights Are Loud", ELDER, ASP, 28, 29, "aspen",
        "Mura Longstand will tell you the wolves are not the problem, and she is right. The wolves have "
        "been here longer than the camp and they have taken nothing but offal.\n\nThe problem is that "
        "nobody in the camp sleeps, because the pack works the dark timber behind the sheds and every "
        "person in this place grew up where you could see what was coming.",
        [k("Blackneedle Wolf", 14), k("Timber Bear", 5)],
        "Thin the pack on the north side where the lodgepole starts. Not all of them. I will not have it "
        "said we came into a country and emptied it.\n\nThe bears are a separate matter. One has been "
        "coming to the smokehouse and it has stopped being frightened of people, which is the point after "
        "which it stops being a bear and starts being a problem.",
        "The camp will sleep. That is worth more than people who have always slept would guess.\n\nYou "
        "left some. Good. A place with nothing in the dark is not a safer place, only an emptier one."))
    return A


# =========================================================================================================
# THE QUILBOAR AND THE DOWNSLOPE - levels 28-30.
# =========================================================================================================
def downslope():
    A = []
    A.append(Q("asp_uphill_boar", "They Did Not Want To Come Either", MEADOW, ASP, 28, 29, "quilboar",
        "Owen Tallgrass watches Elkhorn because it is the only place in the zone you can see anything. "
        "What he has been watching is quilboar, coming up out of the Barrens in numbers, into a cold they "
        "have no clothing for and no word for.\n\nThey were pushed. The mountain took their ground the "
        "same week it took the Lift. He points this out to people and it does not make them friendlier.",
        [k("Quilboar Highrunner", 12), k("Quilboar Frostspeaker", 6)],
        "The highrunners work the meadow edges at first light. They are fast and they are desperate and "
        "those are different problems arriving together.\n\nThe frostspeakers are the ones to drop first. "
        "They have been trying to pray the cold down for four years and whatever they are actually doing "
        "is keeping the rest of them upright.",
        "That will hold them off the meadow until the thaw.\n\nAnd then they will come back, because they still have nowhere else, and we will do this again. I would like somebody cleverer than me to think about that part."))

    A.append(Q("asp_broken_dams", "The Benches Are Flooding", BENCH, ASP, 29, 30, "quilboar",
        "Gelt Rivermane's benches are a stair of beaver ponds, and the dams have held every spring "
        "without anybody's help. This year three have gone in a month.\n\nThe quilboar have been cutting "
        "them. Not for the wood - for the water, because a drained pond is dry ground to den in, and a "
        "dencarver would rather flood a valley than spend another winter wet.",
        [k("Quilboar Dencarver", 10), fetch("stolen_dam_timber", 6)],
        "The dencarvers are down at the third pond and they have got good at it, which is the part I "
        "mind.\n\nBring the timber back up. The beavers will rebuild - they always do - but they will "
        "rebuild faster with their own sticks than with new ones, and I am past caring whether that is "
        "sentimental.",
        "They were back on it before you were out of the water. Did you see?\n\nFour years I have watched them put this valley together again every spring. There is a lesson in it and I am too tired to say what it is."))

    # ---- STARTER DROP 2: the surveyor's pin
    A.append(Q("asp_surveyors_pin", "Somebody Measured This", "item:brass_survey_pin", ASP, 29, 30, "seam",
        "You turn it over. It is a surveyor's pin, brass, stamped with a number and a mark you do not "
        "recognise - and it was in a quilboar den, wrapped in hide, kept.\n\nThe number is the part that "
        "stops you. Numbered pins come in a sequence, and a sequence means somebody walked this ground "
        "with a chain and a book and wrote down what they found, before any of this was here.",
        [fetch("brass_survey_pin", 1), k("Quilboar Dencarver", 6)],
        "Hesta Coldshoulder keeps the watch near the ice and she has an eye for things that do not add "
        "up. She will know whether that mark is Horde, Alliance, or neither.\n\nThe dencarvers will have "
        "more. They have been digging up this whole valley and keeping what shines.",
        "She holds it to the light a long time.\n\n'Not ours. Not theirs either.' She gives it back. "
        "'Keep it. And if you find the one numbered before it, I want to know where.'",
        turn_in_npc_id=CAVE))
    return A


# =========================================================================================================
# THE WEEPING ICE - levels 29-31, and the gate at the end.
# =========================================================================================================
def ice():
    A = []
    A.append(Q("asp_higher_every_spring", "Higher Every Spring", CAVE, ASP, 29, 30, "glacier",
        "Hesta Coldshoulder has been measuring the creek on the benches for three years with a stick and "
        "a notch, which she is aware is not science.\n\nIt is higher every spring. Not by much. By enough "
        "that she has stopped being able to explain it with snowfall, and the water is coming out of a "
        "hole in the rim that was not a hole when she started.",
        [explore(ASP, 145, 48, 6), explore(ICE, 48, 112, 8)],
        "The mouth is on the east side of the rim, above the old slide. You will feel it before you see "
        "it - the air coming out is wrong for this mountain.\n\nGo in as far as the shaft where the light "
        "comes down and no further on this trip. I want to know what the floor is. If it is wet rock then "
        "I am right about where the water is going.",
        "Wet rock. Four years ago that was ice, and in four more years it will be a room.\n\nThe mountain "
        "brought a glacier with it and the glacier is dying. That is what is in my creek.", nxt="asp_the_thaw"))

    A.append(Q("asp_the_thaw", "What the Thaw Lets Go", CAVE, ASP, 29, 30, "glacier",
        "A glacier holds everything it ever picked up, and a melting one gives it back in the order it "
        "took it. Hesta wants what the ice has been letting go of this spring, before the meltwater "
        "carries it down the creek and into the ponds.\n\nShe would also like fewer bears in there. The "
        "bears denned in that cave when it was only a cave and they are not pleased about the company.",
        [fetch("thaw_meltwater_find", 10), k("Winterhide Bear", 8, zone=ICE)],
        "Work the wet end, near the shaft. That is where the ice is going fastest and that is where "
        "things are coming out of the wall.\n\nThe bears are nearest the door for the same reason you "
        "will be - it is the only warm part of that cave. Mind that you are between them and the only "
        "way out.",
        "A bone pin, a button, and something I am not going to guess at. None of it is tauren work "
        "and none of it is orcish.\n\nThe ice took these somewhere else and put them down here. That is twice now I have had to write that sentence."))

    A.append(Q("asp_cornered_cold", "Cornered in the Cold", ELDER, ASP, 30, 31, "glacier",
        "The query from Tarren Mill asked whether there are yeti in Kalimdor. Mura Longstand's answer is "
        "that there are, that they are at the frozen end of a cave that is getting smaller every year, "
        "and that she does not enjoy either half of that sentence.\n\nThey came across inside the ice. "
        "Nobody brought them. They are refugees of the same accident that moved her people, and she has "
        "noticed, and it has not changed what has to be done about them.",
        [k("Meltwater Yeti", 10, zone=ICE), k("Rimefist Yeti", 8, zone=ICE)],
        "They are pressed into the deep end, where the ice still holds, and they come out as far as the "
        "pooled water to feed.\n\nGo in by the shaft and work inward. It gets colder and it gets older "
        "and they get worse the further you go, and if you meet the big one before you are ready, come "
        "back out. He will still be there.",
        "You went in further than I asked. You usually do.\n\nI will write to the apothecary. I will "
        "tell him his impossible thing is real, and it is cornered, and it is running out of cave.",
        nxt="asp_rimehowl"))

    A.append(Q("asp_rimehowl", "The Last Cold Place", ELDER, ASP, 30, 31, "glacier",
        "At the far end of the Weeping Ice, past the braided passages and the standing meltwater, the "
        "glacier is still a glacier. The water drains into it and does not come back out.\n\nThat is "
        "where Rimehowl is, and he is there because it is the only ground left that is what he was made "
        "for. He will not leave it. There is nowhere to leave it to.",
        [boss("Rimehowl")],
        "The Sink. Follow the water down and it will take you there, because that is the one thing water "
        "does reliably in that cave.\n\nHe is bigger than the others and he is not stupid - he will give "
        "ground and let the cold do the work, so do not let a long fight become his fight. And bring "
        "people. I am not sending you in alone and I would not go alone.",
        "It is done, then.\n\nI am not going to pretend I am glad. He was the last of something, standing "
        "in the last of somewhere, and the only reason he was a danger is that his country melted. Ours "
        "went too. We walked. He could not."))

    # ---- THE LINKEN GATE. Needs the Camp Taurajo opener AND the cave boss. Hands in back at Taurajo.
    A.append(Q("asp_what_came_across", "What Else Came Across", ELDER, ASP, 31, 32, "glacier",
        "Mura Longstand has put two things side by side and does not like the shape they make.\n\nA "
        "mountain arrived. Inside it was a glacier, and inside the glacier were animals that have no "
        "business on this continent and did not walk here. The range did not arrive empty. It arrived "
        "with its own country inside it, and nobody has asked how much of that country is still alive.\n"
        "\nTaurajo should hear this from somebody who has been in the ice.",
        [fetch("glacier_proof_bundle", 1), deliver("glacier_proof_bundle",
                                                             "Carry the bundle to Wrangler Tull at Camp Taurajo")],
        "I have put the hide, the hair and the apothecary's own letter in one bundle, with my mark on "
        "it.\n\nTake it down to Tull. He asked four years ago whether there was a road south; the honest "
        "answer is that there is no road, there is a mountain, and the mountain has things living in it "
        "that came from somewhere else. He will want to sit down for the second part.",
        "Tull reads it twice and then puts his hand flat on the table.\n\n'So it is not a wall,' he says. "
        "'It is a country. Somebody else's country, dropped on ours, and we have been treating it like "
        "weather.'\n\nHe does not say anything after that for a long time.",
        requires_quests=["tau_road_south", "asp_rimehowl"],
        turn_in_npc_id=T_WRANGLER,
        grant_items=carry("glacier_proof_bundle", "Longstand's Bundle",
                          "Hide, hair, a letter from an apothecary in Tarren Mill, and Mura Longstand's "
                          "mark burned into the wrap.")))
    return A


# =========================================================================================================
# DROPS - fetch items and the two starters
# =========================================================================================================
FETCH_DROPS = {
    "Redscrub Scavenger": [("seam_red_earth", "Seam Red Earth",
                            "Barrens dust off the dry side of the line. It does not mix with what is "
                            "beside it.", 0.45),
                           ("lift_ledger", "Lift Ledger",
                            "Damp, swollen, and still legible where it matters.", 0.22)],
    "Seam-Struck Kodo": [("undelivered_mail", "Undelivered Mail",
                          "A season of letters that were waiting to go down.", 0.40)],
    "Rimcliff Harpy": [("severed_cable_end", "Severed Cable End",
                        "Lift wire, cut short for a nest.", 0.42),
                       ("harpy_sinew_coil", "Harpy Sinew Coil",
                        "Stronger than rope and considerably less pleasant.", 0.38)],
    "Rimcliff Harpy Windcaller": [("harpy_sinew_coil", "Harpy Sinew Coil",
                             "Stronger than rope and considerably less pleasant.", 0.50)],
    "Goldwood Lynx": [("sound_aspen_bolt", "Sound Aspen Bolt",
                       "Standing dead, cut to length, dry all the way through.", 0.46)],
    "Aspen Elk": [("thick_elk_haunch", "Thick Elk Haunch",
                   "Heavier than anything that came off the plain.", 0.44)],
    "Quilboar Dencarver": [("stolen_dam_timber", "Stolen Dam Timber",
                            "Chewed at one end, cut square at the other.", 0.48)],
    "Winterhide Bear": [("thaw_meltwater_find", "Meltwater Find",
                         "Something the ice picked up a long time ago and has just put down.", 0.42)],
    "Glacier Bear": [("thaw_meltwater_find", "Meltwater Find",
                      "Something the ice picked up a long time ago and has just put down.", 0.42)],
    "Rimehowl": [("glacier_proof_bundle", "Glacier Hide and Hair",
                  "Proof, for somebody across an ocean who asked a careful question.", 1.0)],
}

#: Quest-STARTER drops. Per the engine notes these only drop while the quest is not started, unlocked, and
#: the item is not held - so no dead stacks. Both come from creatures in the quest's own band.
STARTER_DROPS = {
    "Rimcliff Harpy": [("wound_cable_end", "Wound Cable End",
                        "Lift cable, wound into a nest base. The end is stretched, not cut.",
                        0.14, "asp_the_load")],
    "Quilboar Dencarver": [("brass_survey_pin", "Brass Survey Pin",
                            "Numbered, stamped with a mark you do not recognise, and kept wrapped in "
                            "hide by something that could not read it.",
                            0.16, "asp_surveyors_pin")],
}


def main():
    quests = inbound() + basin() + rim() + camp() + downslope() + ice()

    # Inbound quests live in their own zones' files so the giver's town offers them.
    by_file = {}
    for q in quests:
        z = q["zone"]
        f = {TAU: "southern_barrens_hub", ORG: "orgrimmar", HBE: "hillsbrad"}.get(z, "aspen")
        by_file.setdefault(f, []).append(q)

    for fname, qs in by_file.items():
        path = ROOT / f"data/quests/{fname}.json"
        if path.exists() and fname != "aspen":
            data = json.loads(path.read_text())
            existing = data["quests"]
            if isinstance(existing, dict):
                for q in qs:
                    existing[q["quest_id"]] = q
            else:
                ids = {q["quest_id"] for q in qs}
                data["quests"] = [e for e in existing if e.get("quest_id") not in ids] + qs
        else:
            data = {"_notes": "Aspen Wilderness quest pass (2026-10-27). Generated by "
                              "tools/build_aspen_quests.py - do not hand-edit. Text overlay lives in "
                              "data/quests/text/aspen.json.",
                    "quests": {q["quest_id"]: q for q in qs}}
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    # drops
    dp = ROOT / "data/creatures/quest_drops.json"
    drops = json.loads(dp.read_text())
    for cre, rows in FETCH_DROPS.items():
        cur = [d for d in drops.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
        for (iid, nm, desc, ch) in rows:
            cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch})
        drops[cre] = cur
    for cre, rows in STARTER_DROPS.items():
        cur = [d for d in drops.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
        for (iid, nm, desc, ch, qid) in rows:
            cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch, "starts_quest": qid})
        drops[cre] = cur
    dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n")

    n_in = len(inbound())
    print(f"Aspen quests: {len(quests)} total ({n_in} inbound from Taurajo/Orgrimmar/Hillsbrad), "
          f"{len(by_file)} files touched, {len(FETCH_DROPS)} fetch sources, "
          f"{sum(len(v) for v in STARTER_DROPS.values())} starters")


if __name__ == "__main__":
    main()
