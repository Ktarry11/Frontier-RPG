"""
Southern Thousand Needles + Freewind Post + The Drowning Floor quest pass.  Idempotent.

    PYTHONPATH=. python3 tools/build_southern_needles_quests.py
    PYTHONPATH=. python3 tools/build_quest_text.py southern_needles

Writes data/quests/southern_needles.json, adds fetch and starter drops to data/creatures/quest_drops.json,
and splices three inbound quests into their own zones' files (Aspen Wilderness, Camp Taurajo, Orgrimmar).

NO ESCORTS (Kyle's standing rule, and the only hard "never" in quest design).
NO QUESTS BUILT AROUND RARES - The Thermal, Oldcrest, Khan Saltmane and Panglass are lore and loot and
are never an objective. Panglass gets an EXPLORE quest pointed at the glass pan it made, which is the
place, not the creature.

THE ZONE'S ONE IDEA, AND EVERY QUEST SERVES IT:
                    WHO DOES THE FLOOR BELONG TO, AND WHAT DOES IT COST TO WALK ON IT?

The Aspen Wilderness above is about a road that is cut. This zone is about what happens AFTER a road is
cut: somebody ends up owning the ground, and it is not the people who need it.

The tauren built Freewind Post on three mesa tops with one ramp. That is not a defensive flourish, it is
an admission. The Great Lift fell, the road north died with it, and the Galak were simply the people
already standing on the only ground that still connected to anywhere. They hold the floor. Freewind lives
in the air because the air is what was left. Every caravan that reaches the city came up a ramp that
starts in somebody else's country, and everybody in that city knows it.

So the quests are not "clear the centaur camp". They are:
  * the caravans keep arriving light, and the shortfall is a TOLL (Bohl)
  * the city wants to TALK to the Galak, and sends you to do it (High Elder Namka) - the quest that makes
    the zone adult, and the one the finale gates on
  * a Galak toll ledger, which turns out to be a careful, literate, itemised document (Nessa)
  * and the quilboar-style answer - thin the Khan's Chosen - is one quest among twenty, not the premise

THE SPILL IS THE ZONE'S OTHER HALF, and the Skywatcher's quest is the one that should hurt. Elk came down
the pass out of the aspen and cannot go back up it, and they are dying on red hardpan in forty degrees.
This is the exact mirror of the Aspen Wilderness's kodo standing in snow. The Integration opened a door
both ways and everything that walked through it is dying of the wrong climate.

USES THE WHOLE TOOLKIT (Kyle: "keep in mind all quest options"):
  inbound      three, from three places, so the zone is not a thing you only find by walking into it:
               Longstand Camp wants to know whether Freewind is real, Wrangler Tull wants to know whether
               kodo can be driven down (paying off tau_road_south from the Aspen pass), and Orgrimmar
               wants a name for whoever holds the ground between the Horde and the Flats.
  deliver      two - Longstand's query hands in at Freewind, and Namka's parley hands in on the floor.
  craft        Freewind mills aspen it carries down a mountain. Gohn's bench, in one objective.
  starter      two begin as loot: a Galak toll ledger, and a salt-set tally stick off the drowned.
  requires     one gate: the finale needs the parley AND the cave boss, and hands in back at Camp Taurajo.
  explore      four, because this is a zone of places you cannot get to - two mesas with no way up, a
               glass pan, and a hole that swallows a wash.
  kill_boss    Yearmaw, in The Drowning Floor.

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

OUT = ROOT / "data/quests/southern_needles.json"
SN = "southern_thousand_needles"
FW = "freewind_post"
DF = "the_drowning_floor"
ASP, TAU, ORG = "the_aspen_wilderness", "camp_taurajo", "orgrimmar"

XP = {29: 1960, 30: 2040, 31: 2120, 32: 2200, 33: 2280, 34: 2360, 35: 2440, 36: 2520}
GOLD = {29: 8100, 30: 8400, 31: 8700, 32: 9000, 33: 9300, 34: 9600, 35: 9900, 36: 10200}

# The zone's gear flavour. Red stone, the Galak's good work, harpy weave, the pans, and the cave.
# Nothing here is Earth-made - the only thing that came across is the timber, and it came down a mountain
# on somebody's back.
tirisfal_gear.THEMES.update({
    "mesa": (["Redhoof", "Broadback", "Needle-Cut", "Rimstone", "Sun-Scoured"],
             ["Red dust in every seam and it is never coming out.",
              "Sandstone grit has taken the shine off it and left something better.",
              "Carried up a ramp, like everything else in this city.",
              "Hot to the touch until about two in the morning."]),
    "galak": (["Galak", "Toll-Taker's", "Barded", "Khan's", "Outrider"],
              ["Galak work, and good. They were never the savages anyone needed them to be.",
               "Made to be worn at a canter for a whole day.",
               "Taken off somebody who was taking something off somebody else.",
               "The stitching is better than the city's and nobody there will say so."]),
    "sheerwing": (["Sheerwing", "Unclimbed", "Updraft", "Rook-Tended", "Stooping"],
                  ["Harpies weave. Nobody who calls them animals has looked at the work.",
                   "It came off a top that has no way up it.",
                   "Light enough to be carried a long way by something with other plans.",
                   "Feather and sinew, laid in courses like thatch."]),
    "saltpan": (["Saltwatch", "Dryhollow", "Evaporite", "Rime-Set", "Panglass"],
                ["Salt has set into the weave and gone hard.",
                 "The oldest, driest ground in the zone, and the furthest from anyone.",
                 "White all the way through, and it rings when you set it down.",
                 "Found on a pan fused to a sheet you can see your own face in."]),
    "drowned": (["High-Water", "Wrackline", "Soak-Found", "Year-Drowned", "Pillar-Shadow"],
                ["The mark on the pillars is above your head. Look up once and then do not.",
                 "Three years in the pile and the grain has gone hard as fired clay.",
                 "It was down there for a year with the water and a year without.",
                 "Brought in by a flood off a mountain that was not here four years ago."]),
})


def k(target, n, zone=SN):
    return kill(target, n, zone=zone)


def boss(target, zone=DF):
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


# Freewind NPC shorthands (tools/freewind_npc_roster.py)
BOHL, PALLA, RETH = "fw_caravan_master", "fw_ramp_guard", "fw_stablemaster"
HESK, NAMKA, SIMA = "fw_gate_warden", "fw_high_elder", "fw_lookout"
RELL, ILNA, TESH = "fw_skywatcher", "fw_healer", "fw_bowyer"
GOHN, HESHA, ENU = "fw_timberwright", "fw_potter", "fw_spirit_walker"
BREN, NESSA, DRAL = "fw_quartermaster", "fw_tally_clerk", "fw_warehouse_keeper"
DUN, REMEMBERER = "fw_market_relics", "fw_rememberer"
# elsewhere
MURA = "asp_camp_elder"            # Elder Mura Longstand, Longstand Camp, Aspen Wilderness
TULL = "taurajo_kodo_wrangler"     # Wrangler Tull - he gave "The Road South" in the Aspen pass
TORGUN = "org_elder_2"             # Elder Torgun, Orgrimmar


# =========================================================================================================
# INBOUND - three places, three reasons.
# =========================================================================================================
def inbound():
    A = []
    A.append(Q("asp_is_freewind_real", "Word From Below", MURA, ASP, 29, 30, "mesa",
        "Elder Mura Longstand has been told, by three separate caravan drivers who did not know each "
        "other, that there is a tauren city south of the pass built on top of three mesas.\n\nShe has "
        "been a long time without good news and has learned not to spend any of it in advance. But the "
        "drivers all described the same ramp, and people inventing a city do not agree about the ramp.",
        [deliver("longstand_query", "Carry Longstand's question to High Elder Namka Windhollow")],
        "Take this down the pass and put it in the hand of whoever speaks for that place.\n\nIt is one "
        "question and it is not a polite one. I want to know if they are holding, or if they are three "
        "rocks with people standing on them waiting for somebody to notice.",
        "She asks the question I would have been too careful to ask. Tell her we are holding.\n\nTell her "
        "we are holding and that the ramp is the problem and always has been.",
        turn_in_npc_id=NAMKA,
        grant_items=carry("longstand_query", "Longstand's Question",
                          "One sheet, folded twice, and the fold is sharp enough to say it was folded "
                          "by somebody who did not want to reread it.")))

    A.append(Q("tau_can_kodo_go_down", "Whether Kodo Can Go Down", TULL, TAU, 30, 31, "mesa",
        "Wrangler Tull sent somebody up to the Lift once already and got back the word that there were "
        "trees on it. He has had three years to make peace with that and about four days to make peace "
        "with the rest.\n\nThere is a way down now. What he needs to know is whether it is a way down a "
        "kodo can take, because a road a kodo cannot walk is not a road, it is a footpath with ambitions.",
        [explore(SN, 110, 30, 9), explore(SN, 128, 92, 9)],
        "Walk the whole thing. Not the look-over-the-edge version - the whole thing, from where the "
        "timber quits down to where the road forks on the floor.\n\nI am not asking about the view. I am "
        "asking about grade, footing and whether there is water in the first two days, and you will "
        "only know that by putting your own feet on it.",
        "Passable. You said passable, not good.\n\nThat is the first honest answer anyone has brought me "
        "about that country, and I have been asking for three years."))

    A.append(Q("org_who_holds_the_floor", "Who Holds the Floor", TORGUN, ORG, 31, 32, "galak",
        "Elder Torgun's report on the southern border now has a second page, and the second page is "
        "worse than the first. There is country beyond the range after all, there are tauren living on "
        "top of it, and between the Horde and the salt flats there is a people holding the only ground "
        "that connects anything to anything.\n\nThe Warchief does not need their history. He needs their "
        "name and their number.",
        [k("Galak Outrider", 10), k("Galak Windcatcher", 6)],
        "Galak. Centaur, and not the Kolkar - different stock, different manners, and by every account "
        "better organised than anything we have fought on this continent.\n\nGo down onto that floor and "
        "find out what they are made of. I want the outriders counted and I want their wind-readers "
        "counted separately, because a people who post weather-watchers are a people with a plan.",
        "Drilled, then. Paced. They do not break and they do not chase.\n\nI will write that down and I "
        "will be unpopular for it. Everyone upstairs wants to hear savages."))
    return A


# =========================================================================================================
# THE LANDING - the ramp, the caravans, and the toll. Levels 29-31.
# =========================================================================================================
def landing():
    A = []
    A.append(Q("fw_light_caravans", "Four a Week, All of Them Light", BOHL, FW, 29, 30, "galak",
        "Caravan-Master Bohl has been complaining about the ramp for three years because the ramp is "
        "safe to complain about.\n\nThe actual problem is on his tally sheet. Four caravans a week come "
        "up and every one of them arrives lighter than it left, by an amount that is too consistent to "
        "be theft and too large to be spillage. Somebody is taking a cut, in the open, and the drivers "
        "have stopped mentioning it.",
        [k("Galak Outrider", 8), fetch("galak_toll_tally", 4)],
        "The road east runs between the Sisters and there is a gap you have to go through. That is where "
        "it happens.\n\nGo and stand in that gap and see what it costs. Bring me their tally slips - "
        "they write it down, which is the part I cannot get past. They are not robbing us. They are "
        "invoicing us.",
        "Itemised. Dated. In a hand better than my clerk's.\n\nI wanted to be angry about this and now I "
        "have to go and think about something else instead.", nxt="fw_toll_ledger"))

    A.append(Q("fw_one_road_in", "One Road In", PALLA, FW, 29, 30, "mesa",
        "Sentry Palla says the single ramp is a better defence than Thunder Bluff ever had, and she "
        "means it, and she also knows exactly what it means to say it.\n\nFor the last two weeks "
        "something has been working the bottom of it after dark. Not attacking. Testing - coming up far "
        "enough to be seen and then going back down, every night, a little further each time.",
        [k("Dustmane Hyena", 10), explore(SN, 166, 102, 8)],
        "Hyena. I am nearly sure it is hyena, and nearly sure is why I am sending somebody instead of "
        "going myself.\n\nWork the bottom of the ramp and the scrub either side of it, and go out as far "
        "as the first bend of the Windward Road. If something is teaching them that this ramp is worth "
        "walking up, I want to know whether it is a pack or a person.",
        "A pack. Good.\n\nI would rather it were hunger than somebody's idea. Hunger I can post a "
        "sentry against."))

    A.append(Q("fw_feed_below", "What the Kodo Will Not Do", RETH, FW, 30, 31, "mesa",
        "Stablemaster Reth keeps every four-legged animal in the city on the Landing, because kodo will "
        "not cross a rope bridge and worked that out faster than the tauren did.\n\nWhich means the pens "
        "are up here and the feed is down there, and twice a season somebody has to go and cut it. It is "
        "nobody's favourite week.",
        [fetch("washbed_fodder", 8)],
        "There is grass in the wash beds that is worth cutting - the only green on the whole floor, and "
        "it is green because that is where the year's water went.\n\nTake a blade down and bring back "
        "what you can carry. Watch for scorpid in the shade of the cut banks. They are in there because "
        "it is cool and they will not move for you.",
        "Smells like the plain. It does not taste like the plain and the kodo know, but they eat it.\n\n"
        "Everything up here is a version of something we used to have."))
    return A


# =========================================================================================================
# THE SPILL - the north, where the timber quits. Levels 29-31. The zone's other half.
# =========================================================================================================
def spill():
    A = []
    A.append(Q("fw_the_spill", "They Came Down and They Cannot Go Up", RELL, FW, 29, 30, "mesa",
        "Skywatcher Rell can see the dark line of the aspen along the north on a clear day, and three "
        "years ago that line was sky.\n\nThings have been coming down it. Elk, mostly - they came off "
        "the mountain into what looked like open country, walked south until the timber ran out, and "
        "found red hardpan and forty degrees. They cannot find the pass again. They are standing on the "
        "Seam in the heat of the day waiting for a weather that is not coming.",
        [k("Sunstruck Elk", 8), k("Downslope Lynx", 5)],
        "I am not asking you to cull them and I would not call it that.\n\nThey are going down on their "
        "feet out there and the cats came after them and are doing no better. Go and finish what the sun "
        "has started, both of them, and do it close enough that it is quick. That is the whole task and "
        "I am sorry it is one.",
        "You will have seen the ribs on them.\n\nWe came down a pass too. The difference is that we "
        "knew what we were walking into and we still argue about whether that was better."))

    A.append(Q("fw_wrong_climate", "The Wrong Climate", ILNA, FW, 30, 31, "mesa",
        "Healer Ilna Softstep treats falls, mostly, and off ladders rather than off edges. Lately she "
        "has been treating something else: drivers coming up the ramp with heat sickness in a season "
        "they have worked their whole lives.\n\nShe thinks the floor is getting hotter. She would like "
        "to be wrong, and she has worked out a way to find out that does not depend on her being right.",
        [fetch("sunstruck_marrow", 6), fetch("seam_ground_sample", 4)],
        "Bring me marrow from the elk dying on the Seam and a scrape of the ground they are dying on.\n\n"
        "An animal that starves and an animal that cooks do not leave the same marrow. If it is the "
        "heat, I will know, and I will have to go and tell Namka that the floor is changing under a city "
        "that cannot move.",
        "Heat. Not hunger.\n\nI wanted hunger. Hunger would have meant they were simply in the wrong "
        "place, and this means the place is going wrong."))
    return A


# =========================================================================================================
# THE SHEERWING - the mesa tops with no way up. Levels 31-32.
# =========================================================================================================
def sheerwing():
    A = []
    A.append(Q("fw_harpies_weave", "Harpies Weave", TESH, FW, 31, 32, "sheerwing",
        "Bowyer Tesh builds better bows than her mother did and has never stopped being annoyed about "
        "why.\n\nShe has been looking at harpy nest-work through a glass from the Windward top for a "
        "season. It is woven. Laid in courses, like thatch, with a turn at the end of each course that "
        "she cannot do and cannot stop thinking about.",
        [k("Sheerwing Harpy", 10), fetch("sheerwing_course_weave", 5)],
        "Bring me the weave. Not a handful of feathers - a piece with the courses still in it, big "
        "enough that I can see where the turn goes.\n\nAnd yes, you will have to kill them to get it, "
        "and no, I have not found a way around that, and I have thought about it more than you have.",
        "There. That is a bowyer's knot or near enough, and it is being tied by something everyone in "
        "this city calls an animal.\n\nI am not going to say that out loud yet. I would like to be sure "
        "first, which is more courtesy than most of them get."))

    A.append(Q("fw_the_anvil", "Nothing Walks Up the Anvil", SIMA, FW, 31, 32, "sheerwing",
        "Lookout Sima has the highest standing ground in Thousand Needles and a list of the four mesas "
        "nobody has ever been on top of. The Anvil is the nearest of them.\n\nFor eleven nights there "
        "has been a light up there. Not a fire - a fire sits still. This moves along the rim and goes "
        "out and comes back, and she has counted the pattern and the pattern does not repeat.",
        [explore(SN, 26, 118, 9), k("Sheerwing Rooktender", 7)],
        "Get round the base of it and as high as the scree will take you. I am not asking you to climb "
        "the unclimbable, I am asking you to get close enough to see what is making that light.\n\nThe "
        "rooktenders come down to hunt at dusk. If you can take a few on the way it will be a quieter "
        "approach, and I will not pretend that is not also useful to me.",
        "Carried. Something is carrying it along the rim and putting it down.\n\nThen they signal. Then "
        "that is a thing they do, and I have been writing them up as weather for three years."))
    return A


# =========================================================================================================
# THE GALAK - the floor, and the heart of the zone. Levels 31-33.
# =========================================================================================================
def galak():
    A = []
    A.append(Q("fw_toll_ledger", "An Itemised Document", NESSA, FW, 31, 32, "galak",
        "Tally-Clerk Nessa writes down everything that crosses this top, and she will tell you it is not "
        "suspicion - it is that the tauren lost a city once without a list of what was in it.\n\nBohl "
        "has brought her four Galak tally slips and she has not slept properly since. They are better "
        "kept than hers. Dated, carried forward, with a running balance and a column she cannot identify.",
        [fetch("galak_toll_ledger_leaf", 5)],
        "I need more of it. Not slips - leaves out of the book the slips come from, and you will find "
        "those on whoever is senior in a toll party.\n\nI want to know what that fourth column is. If "
        "they are keeping a balance against us then they think we owe them something specific, and I "
        "would like to know what before the council decides for me.",
        "It is a running total. Against the road.\n\nThey are not charging us to pass. They are charging "
        "us for the road, and they have been maintaining the road, and there is a column for that too."))

    A.append(Q("fw_at_the_ramp_foot", "At the Foot of the Ramp", HESK, FW, 31, 32, "galak",
        "Warden Hesk Stonefoot watches everything that comes up the ramp because everything that reaches "
        "this city comes up it. He is not a nervous man and he has been nervous for a month.\n\nGalak "
        "outriders have started standing at the bottom. Not blocking it. Standing at it, in daylight, in "
        "numbers, where the whole Landing can look down and count them.",
        [k("Galak Khan's Chosen", 6), k("Galak Wrangler", 6)],
        "The Khan's Chosen are the ones with the standard. Where they stand, the rest form up, and they "
        "have been forming up closer each week.\n\nGo down and make the ground in front of that ramp "
        "expensive. I am not asking for a war. I am asking them to do their standing somewhere I cannot "
        "see it from my own gate.",
        "They have moved back. Half a mile, and in good order, which I notice.\n\nNobody routed. They "
        "decided. That is worse and I am going to say so to the council whether they want it or not."))

    A.append(Q("fw_hollowhorn_wants_less", "What the Quartermaster Wants Less Of", BREN, FW, 32, 33,
        "galak",
        "Quartermaster Bren Hollowhorn prices everything by the back that carried it up the ramp, and "
        "lately every back is costing more because of what is standing at the bottom.\n\nShe is not "
        "interested in the philosophy. She has a column that says what the escort costs and she would "
        "like it to be a smaller number by the end of the season.",
        [k("Galak Khan's Chosen", 10), k("Galak Windcatcher", 8)],
        "The wind-readers are the ones that make a toll party work. They sit high, they see the dust of "
        "a caravan an hour out, and the riders are formed up and waiting before the drivers know they "
        "are seen.\n\nTake the readers out and the riders are guessing. Take enough of them and my "
        "escort column halves. That is the whole of my reasoning and I am not going to dress it up.",
        "Down a third already. I will take a third.\n\nYou will hear Namka say we should be talking to "
        "them. She is probably right. She is also not the one buying rope."))

    A.append(Q("fw_the_parley", "Namka Sends a Word", NAMKA, FW, 32, 33, "galak",
        "High Elder Namka Windhollow built this city and cannot get used to having built something "
        "again. She has listened to the warden, the quartermaster and the clerk, and she has read the "
        "fourth column in the Galak ledger, and she has reached a conclusion the council will hate.\n\n"
        "The Galak are not raiding Freewind. They are charging it for a road they maintain, and nobody "
        "on either side has ever once said so out loud.",
        [deliver("namka_word", "Put Namka's word in the hand of a Galak toll party"),
         explore(SN, 155, 55, 8)],
        "This goes to the Sisters, to whoever is standing in that gap, and it goes into a hand - not "
        "stuck in the ground, not left on a stone.\n\nThey will not kill you for carrying it. They have "
        "never killed a driver who paid and they have never killed one who could not. Walk up with it "
        "held where they can see it and do not draw anything, and if that frightens you then you have "
        "understood the task.",
        "Taken. Read, in front of you, and taken.\n\nThen we are talking. Three years and a dead road "
        "and a city in the air, and all it needed was somebody willing to walk up holding a piece of "
        "paper. I will be a long time forgiving myself for the three years.",
        requires_quests=["fw_toll_ledger"],
        grant_items=carry("namka_word", "Namka's Word",
                          "Not sealed. She was specific about that - a sealed letter is a letter you "
                          "are expected to carry and not read, and she wanted it read by everyone whose "
                          "hands it passed through.")))
    return A


# =========================================================================================================
# THE DRY EAST - Saltwatch and Dryhollow, and the step toward Shimmering Flats. Levels 32-34.
# =========================================================================================================
def dry_east():
    A = []
    A.append(Q("fw_clay_up_the_ramp", "Everything Comes Up the Ramp", HESHA, FW, 32, 33, "saltpan",
        "Potter Hesha will tell you that if you ever want to understand this city, you should stand at "
        "the bottom of the ramp for a day. Her clay comes up it in sacks, from a pit four days west, "
        "and every pot in Freewind is priced accordingly.\n\nThere is clay in the salt pans east of "
        "here, two days closer. Everyone has told her it will not fire. Nobody has tried it.",
        [fetch("saltwatch_pan_clay", 7)],
        "Dig me seven good sacks off the pans at Saltwatch. Below the crust - the crust is salt and salt "
        "is what ruins a pot. Under it there is grey clay and I want to see it.\n\nThe things that live "
        "out on those pans are made of the same salt. Do not let them get close enough to put it on you.",
        "It fires. Pale, and it rings higher than the western clay, and it is going to crack in the cold "
        "if the cold ever comes.\n\nTwo days closer. Two days closer is a different city."))

    A.append(Q("fw_older_than_the_wrong", "Older Than Any of This", ENU, FW, 33, 34, "saltpan",
        "Spirit-Walker Enu has spent three years looking for the dead of Thunder Bluff and not finding "
        "them, and has found the only comfort available in the not-finding.\n\nHe has been out to "
        "Dryhollow twice. He wants it understood, by somebody who will carry it back and repeat it, that "
        "what is wrong with Dryhollow is not the Integration's doing. It was wrong before. It will be "
        "wrong after. Not everything broken in this world was broken by Earth arriving.",
        [k("Dryhollow Basilisk", 8), explore(SN, 150, 172, 9)],
        "Go out to the hollow and stand in the middle of it for as long as you can manage, and then "
        "come back and tell me what you felt.\n\nThe basilisks will not let you stand anywhere for long, "
        "so thin them first. They are old. They are the oldest thing on this map and they were doing "
        "this when the needles were still being cut by water.",
        "Nothing. You felt nothing, and that is the answer.\n\nEverywhere the Integration touched feels "
        "like a held breath. Dryhollow feels like a room nobody has been in. It is simply old, and I "
        "needed one thing in this country to be simply old."))

    A.append(Q("fw_the_glass_pan", "The Pan You Can See Yourself In", DUN, FW, 33, 34, "saltpan",
        "Relic-Keeper Dun can tell you whether a thing came up out of the mesas or down off the "
        "mountain. He cannot always tell you what either one is, and he is honest about the gap, which "
        "is rarer in his trade than it should be.\n\nA salt crew came back from the far side of "
        "Dryhollow talking about a pan fused to glass. A sheet of it, flat, with the sky in it. They "
        "would not go nearer and they would not go back.",
        [explore(SN, 136, 184, 8), fetch("fused_pan_shard", 4)],
        "Go and look at it and bring me pieces off the edge.\n\nI will tell you what the crew told me, "
        "which is that something lives out there and that it is still making the glass. Look at the pan, "
        "take your pieces off the rim of it, and do not go to the middle to find out what is standing "
        "in the middle. Nothing I want is worth that.",
        "Fused all the way through. Not glazed - fused, like it went through a kiln the size of the "
        "hollow.\n\nI am going to put this on the shelf and label it honestly: came up out of the mesas, "
        "cause unknown, do not go to the middle."))
    return A


# =========================================================================================================
# THE BENCH - Freewind's own trade, which is a mountain's timber carried down into a desert.
# =========================================================================================================
def bench():
    A = []
    A.append(Q("fw_pale_wood_wrong_wood", "Pale Wood, Wrong Wood", GOHN, FW, 31, 32, "mesa",
        "Timberwright Gohn has stopped finding it strange that every plank in this city came off a "
        "mountain that was not here three years ago, and he has been told that is the strange part.\n\n"
        "The bridges want relaying before the windy season. Three spans, and the rope gets all the "
        "attention because rope is frightening and decking is not, which is exactly backwards.",
        [craft("plank_ironbark", "Mill decking at Gohn's bench", 6), fetch("sound_aspen_bolt", 4)],
        "Mill me six lengths and bring four sound bolts up from the stacks to replace what you use.\n\n"
        "Aspen takes a bend and holds it, which is why the bowyer is insufferable lately, and it is why "
        "a deck board on a rope span wants to be aspen and not anything that grew down here. Nothing "
        "that grew down here bends. It just goes.",
        "Good work and dull work, and dull work is what a bridge is made of.\n\nWhen somebody walks "
        "across that span and thinks about the rope, they are thinking about the wrong thing, and that "
        "is the compliment."))
    return A


# =========================================================================================================
# THE DROWNING FLOOR - the cave under Broadback. Levels 33-35.
# =========================================================================================================
def cave():
    A = []
    A.append(Q("fw_where_the_water_goes", "Where the Water Goes", DRAL, FW, 33, 34, "drowned",
        "Warehouse-Keeper Dral knows where everything that came up the ramp this season is, and will "
        "tell you to stop asking about anything that did not.\n\nWhat he cannot account for is water. "
        "Thousand Needles floods once a year, hard, and then is dry for twelve months. That much water "
        "does not evaporate. It goes somewhere, and whatever it goes into has been filling and emptying "
        "since before anyone here was born.",
        [explore(SN, 104, 112, 7), k("Saltpan Kodo", 8)],
        "At the foot of Broadback there is a wash that runs in and does not run out. I want you to go "
        "and stand at the mouth of it and look down.\n\nThe kodo shelter in the mouth of it in the heat "
        "and they will not like you there. Clear enough of them that you can get a proper look, and "
        "then come back and tell me how far down you could see before it stopped being down.",
        "No bottom to it that you could see. A year's water, every year, into a hole with no bottom.\n\n"
        "I have a column in my book for things that go out and do not come back. I am going to need a "
        "bigger column.", nxt="fw_the_drowned"))

    A.append(Q("fw_the_drowned", "They Were People", REMEMBERER, FW, 33, 34, "drowned",
        "The Rememberer holds the names of everyone who was in Thunder Bluff when the ground took the "
        "city, in order, and says them through once a season. It takes most of a night and he is not "
        "going to stop.\n\nDral has told him what is down the hole at Broadback. There are things "
        "walking in it with salt set hard over them, and they have hands, and somebody somewhere has a "
        "list with their names on it.",
        [k("Saltbound Shambler", 10), fetch("saltset_tally_stick", 5)],
        "I am not asking you to put them down out of mercy. You can decide that for yourself and I would "
        "not argue with either answer.\n\nI am asking you to bring back anything they are carrying that "
        "was made rather than grown. A stick with notches. A ring. A tally. Something that says a person "
        "kept it, so that I can say what they were before the water, and not only that they drowned.",
        "Tally sticks. Salt crews, then - the ones that work the pans east and come back through the "
        "washes in the wet month.\n\nFive of them. That is five names I can find, and finding five names "
        "is the only work I have ever been good at.", nxt="fw_yearmaw"))

    A.append(Q("fw_yearmaw", "It Feeds Once", DRAL, FW, 34, 35, "drowned",
        "Dral has stopped keeping a column for the hole at Broadback and started keeping a page.\n\n"
        "The salt crews that come back through the washes have a story they tell each other and not "
        "outsiders: that there is something in the standing water at the bottom that does not eat all "
        "year. It waits for the flood. When the cave fills, everything in it drowns at once, and the "
        "thing in the sump has its one meal and then waits another year.",
        [boss("Yearmaw")],
        "The flood is four months out, which means everything down there is alive and the thing in the "
        "sump is as hungry as it ever gets.\n\nThe water never drains out of the lowest bay. Go to it. "
        "Whatever is in there has no eyes and has never needed any, and three of my drivers have told me "
        "the same thing about how it finds you, which is that it waits until you move.",
        "Then the crews were right and I have been filing their story under rumour for two years.\n\n"
        "There is a page in my book for that too. I am going to go and change it, and I am going to make "
        "a note about who told me first."))
    return A


# =========================================================================================================
# THE FINALE - gated on the parley AND the cave boss, hands in back at Camp Taurajo.
# =========================================================================================================
def finale():
    return [Q("fw_the_road_is_open", "The Road Is Open", NAMKA, FW, 34, 35, "galak",
        "Namka has a thing she has not had in three years, which is a road and somebody to talk to at "
        "both ends of it.\n\nThe Galak will let a caravan through and have put a price on it that is "
        "written down. The hole under Broadback has had the thing at the bottom of it taken out of it. "
        "There is nothing left between Camp Taurajo and this city except distance, and distance is a "
        "problem the tauren have solved before.",
        [deliver("freewind_accord", "Carry the accord to Wrangler Tull at Camp Taurajo")],
        "Take this north. All of it - the terms, the toll, the schedule, and the Galak's own hand at the "
        "bottom of it, which took longer to get than any of the rest.\n\nTull asked whether kodo could "
        "go down. Tell him yes. Tell him it costs, tell him who it costs, and tell him we are paying it "
        "and that we think the price is fair, and watch his face while you say that last part.",
        "Signed by a centaur. There is a centaur's mark on a tauren document and somebody expects me to "
        "read it out at the corral gate.\n\nI drove that road for twenty years and I never once paid a "
        "toll on it. I also never once had to ask who kept it up. Fine. Fine, lass. We will pay.",
        requires_quests=["fw_the_parley", "fw_yearmaw"], turn_in_npc_id=TULL,
        grant_items=carry("freewind_accord", "The Freewind Accord",
                          "Two hands at the bottom of it. One of them is not a tauren's and it took "
                          "three years and a city in the air to get it there."))]


# =========================================================================================================
# DROPS
# =========================================================================================================
FETCH_DROPS = {
    "Galak Outrider": [("galak_toll_tally", "Galak Toll Tally",
                        "A slip of hide, itemised, dated and carried forward. That is the part nobody "
                        "in Freewind can get past.", 0.46)],
    "Galak Wrangler": [("galak_toll_tally", "Galak Toll Tally",
                        "A slip of hide, itemised, dated and carried forward.", 0.40)],
    "Galak Khan's Chosen": [("galak_toll_ledger_leaf", "Toll Ledger Leaf",
                             "A page out of the book the slips are torn from. Four columns, and the "
                             "fourth one is not a charge.", 0.44)],
    "Sheerwing Harpy": [("sheerwing_course_weave", "Sheerwing Course-Weave",
                         "Laid in courses like thatch, with a turn at the end of each one.", 0.44)],
    "Sheerwing Rooktender": [("sheerwing_course_weave", "Sheerwing Course-Weave",
                              "Nest-work, and better nest-work than the city will admit.", 0.50)],
    "Sunstruck Elk": [("sunstruck_marrow", "Sunstruck Marrow",
                       "An animal that starves and an animal that cooks do not leave the same marrow.",
                       0.48),
                      ("washbed_fodder", "Wash-Bed Fodder",
                       "The only green on the whole floor, and it is green because that is where the "
                       "year's water went.", 0.30)],
    "Rimstalker Scorpid": [("washbed_fodder", "Wash-Bed Fodder",
                            "Cut from the shade of a cut bank, where it is cool and things do not move "
                            "for you.", 0.46),
                           ("seam_ground_sample", "Seam Ground Sample",
                            "Red hardpan off the line where the timber quits.", 0.38)],
    "Downslope Lynx": [("seam_ground_sample", "Seam Ground Sample",
                        "Scraped off the ground they are dying on.", 0.42)],
    "Saltspite Elemental": [("saltwatch_pan_clay", "Saltwatch Pan Clay",
                             "Grey, from under the crust. Everyone said it would not fire.", 0.48),
                            ("fused_pan_shard", "Fused Pan Shard",
                             "Off the rim of a sheet you can see the sky in.", 0.26)],
    "Dryhollow Basilisk": [("fused_pan_shard", "Fused Pan Shard",
                            "Fused all the way through, not glazed.", 0.40)],
    "Saltbound Shambler": [("saltset_tally_stick", "Salt-Set Tally Stick",
                            "Notched, and the notches are a salt crew's count. Somebody kept this.",
                            0.46)],
    "Sightless Kodo": [("sound_aspen_bolt", "Sound Aspen Bolt",
                        "Standing dead, cut to length, dry all the way through. The flood brought it "
                        "down and the cave kept it.", 0.42)],
}

#: Quest-STARTER drops. The engine only drops these while the quest is unstarted, unlocked and the item
#: unheld, so there are no dead stacks.
STARTER_DROPS = {
    "Galak Windcatcher": [("galak_road_tally", "Galak Road-Tally",
                           "A running balance, kept against something, in a hand better than the city "
                           "clerk's. The fourth column is not a charge and you cannot read what it is.",
                           0.15, "fw_toll_ledger")],
    "Washline Scuttler": [("drowned_crew_token", "Drowned Crew Token",
                           "Bone, drilled once, worn smooth on one face by a thumb. It was carried by "
                           "somebody for a long time before the water got it.",
                           0.16, "fw_the_drowned")],
}


def main():
    quests = (inbound() + landing() + spill() + sheerwing() + galak() + dry_east() + bench()
              + cave() + finale())

    by_file = {}
    for q in quests:
        f = {ASP: "aspen", TAU: "southern_barrens_hub", ORG: "orgrimmar"}.get(q["zone"],
                                                                              "southern_needles")
        by_file.setdefault(f, []).append(q)

    for fname, qs in by_file.items():
        path = ROOT / f"data/quests/{fname}.json"
        if path.exists() and fname != "southern_needles":
            data = json.loads(path.read_text(encoding="utf-8"))
            existing = data["quests"]
            if isinstance(existing, dict):
                for q in qs:
                    existing[q["quest_id"]] = q
            else:
                # A LIST, not a dict - tools/build_quest_text.py iterates `quests` as a list and dies on
                # a dict with "string indices must be integers". Caught on the Aspen pass.
                ids = {q["quest_id"] for q in qs}
                data["quests"] = [e for e in existing if e.get("quest_id") not in ids] + qs
        else:
            data = {"_notes": "Southern Thousand Needles / Freewind Post / The Drowning Floor quest pass "
                              "(2026-10-28). Generated by tools/build_southern_needles_quests.py - do "
                              "not hand-edit text here; the overlay in "
                              "data/quests/text/southern_needles.json wins and its source is "
                              "tools/quest_text_src/southern_needles.txt.",
                    "quests": qs}
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    dp = ROOT / "data/creatures/quest_drops.json"
    drops = json.loads(dp.read_text(encoding="utf-8"))
    # THE LOADERS READ data["drops"], NOT THE TOP LEVEL. Both combat_engine._get_loot_item_drops and
    # quest_locator.item_sources do json.load(f).get("drops", {}) - so a creature key written beside
    # "drops" instead of inside it is read by nothing and the item never drops. This file shipped that
    # way for the whole Aspen pass: 23 quest items were un-droppable, including both of Aspen's
    # quest-STARTER items, which meant two quests could never be started at all. Write inside "drops".
    table = drops.setdefault("drops", drops)
    for cre, rows in FETCH_DROPS.items():
        cur = [d for d in table.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
        for (iid, nm, desc, ch) in rows:
            cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch})
        table[cre] = cur
    for cre, rows in STARTER_DROPS.items():
        cur = [d for d in table.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
        for (iid, nm, desc, ch, qid) in rows:
            cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch, "starts_quest": qid})
        table[cre] = cur
    dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Southern Needles quests: {len(quests)} total ({len(inbound())} inbound from "
          f"Longstand/Taurajo/Orgrimmar), {len(by_file)} files touched, "
          f"{len(FETCH_DROPS)} fetch sources, {sum(len(v) for v in STARTER_DROPS.values())} starters")


if __name__ == "__main__":
    main()
