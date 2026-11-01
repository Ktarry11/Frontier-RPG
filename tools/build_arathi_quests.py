#!/usr/bin/env python3
"""
Arathi Highlands quest pass - three zones, two dungeons, five caves. Idempotent.

    PYTHONPATH=. python3 tools/build_arathi_quests.py

Writes data/quests/arathi.json, adds fetch and starter drops to data/creatures/quest_drops.json,
and splices three inbound quests into their own zones' files (Tarren Mill, Eastern Hillsbrad,
Orgrimmar).

NO ESCORTS. Kyle's standing rule and the only hard "never" in quest design here.

NO QUEST OBJECTIVE ON AN OPEN-WORLD RARE. Gruln Stonejaw, Overseer Mull, Harbinger Veska, The
Ring Warden, Silt-Mother Ooga, Old Bonepicker and The Saltquern are lore and loot and are never
a kill objective - the house rule the Southern Needles pass set, for the reason it set it: a
quest you cannot finish because the thing is not up is a quest that reads as broken. Where one
of them is the point of a place, the quest EXPLORES the place instead, which is the Panglass
answer. Cave and dungeon bosses are fair game and carry most of the kill_boss objectives.

THE REGION'S ONE IDEA, AND EVERY QUEST SERVES IT:

              EVERYONE HERE IS HOLDING GROUND THAT IS NOT THEIRS,
              AND THE GROUND IS OLDER THAN ALL OF THEM.

Arathor raised the first human empire on this moor and it has been three thousand years dead.
The stone rings in the basin are older than Arathor and nobody knows who set them. On top of
that: the Syndicate squatting in Stromgarde with a claim they invented; orcs holding Hammerfall
because they took it; the Horde camped in a human ruin at Refuge Pointe and keeping the ruin's
name because it was already painted on the gate; Boulderfist ogres pulling the standing stones
down for wall rock; kobolds in Drywhisker who dug past the ore into something that was there
first; and in the Drowned Barrow, Arathor's own dead still standing a watch for an empire that
does not exist. Nobody on this moor is from here. Everybody on it is holding.

So the quests are not "clear the ogre camp". They are:
  * the wall is open after three years and nobody on either side knows what is through it
  * Go'Shek Farm is still bringing in a harvest, which means somebody is buying the grain
  * the tauren want you to ASK the ogres to stop taking the rings apart, and you do ask, and
    the asking is a real quest with a real answer before anyone draws anything
  * the Drowned Barrow's revenants are not evil and are not stoppable, and the quest chain down
    there ends with putting a three-thousand-year-old officer off a watch nobody relieved him of
  * the Bloodsail at Wrackline are not raiding. They are holding. That is the East's whole hook.

USES THE WHOLE TOOLKIT (Kyle: "keep in mind all quest options"):
  inbound     three, from three places - Tarren Mill wants to know what is through the wall it
              has stared at for three years, a Forsaken field apothecary wants to know what
              killed her scout, and Orgrimmar has two years of Hammerfall requisitions it has
              never answered.
  deliver     three, including the parley to Boulderfist Hall and the runner's road report.
  gather      two, on real gatherables - the herbalist's liferoot and the prospector's iron,
              which is the one quest type that pays a player for the profession they already
              have (GATHER holds, it does not consume).
  starter     two begin as loot: a Syndicate grain contract and an Arathor watch-token.
  requires    eight gates, so both dungeons and the barrow run as ordered chains rather than a
              pile of parallel errands.
  explore     eight, because this is a region of places - four stone rings, a drowned barrow, a
              gap in a wall, and tidal flats you can only reach at low water.
  kill_boss   seventeen, across both dungeons and all five caves.

WRITING STANDARD (Kyle): no "kill X of Y down by the Z". The accept line is a PERSON TALKING
and the numbers live inside what they say.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/arathi.json"

AW, AC, AE = "arathi_west", "arathi_central", "arathi_east"
STRO, DRY = "stromgarde_keep", "drywhisker_deeps"
BGOR, BHALL = "bouldergor", "boulderfist_hall"
BARROW, WRACK, TIDE = "the_drowned_barrow", "wrackline_hold", "the_tidewrack"
TM, HBE, ORG = "tarren_mill", "eastern_hillsbrad", "orgrimmar"

#: Straight off the game's own curve - these are the medians of every existing non-boss quest at
#: each level, so Arathi pays what the rest of the world pays rather than a table I invented.
XP = {28: 1920, 29: 1960, 30: 2040, 31: 2120, 32: 2200, 33: 2280, 34: 2360, 35: 2440,
      36: 2520, 37: 2600, 38: 2680, 39: 2760, 40: 2840}
GOLD = {28: 7800, 29: 8100, 30: 8400, 31: 8700, 32: 9000, 33: 9300, 34: 9600, 35: 9900,
        36: 10200, 37: 10500, 38: 10800, 39: 11100, 40: 11400}

# The region's gear flavour. Stone, salt, old iron and older masonry. NOTHING EARTH-MADE appears
# as an object anywhere in here - the Integration is in what people say, never in what they hold.
tirisfal_gear.THEMES.update({
    "moor": (["Highland", "Wide-Country", "Moorfast", "Kite-Watched", "Longwalk"],
             ["Three thousand years of weather and the moor has not finished with any of it.",
              "Everything on this moor is further away than it looks, including the weather.",
              "Camp issue, mended twice by whoever was holding it at the time.",
              "The grass up here lies the same way all year. It tells you which way the wind lives."]),
    "syndicate": (["Syndicate", "Claimant's", "Alterac", "Boarded", "Rent-Taker's"],
                  ["Good work, stolen, and put to a second use by people who knew how.",
                   "The crest has been filed off and nothing has been put in its place.",
                   "Dispossessed nobility keep their tailoring long after they lose everything else.",
                   "Taken off somebody who was taking something off somebody else."]),
    "witherbark": (["Witherbark", "Hollow-Drum", "Hexthread", "Turned-Ear", "Bark-Cut"],
                   ["Trolls carve the outside and mean the inside.",
                    "Six colours of thread and the sixth is not a dye anyone sells.",
                    "It was hung at the edge of a camp to hear what was coming.",
                    "Older than the village it came out of, and the village is not new."]),
    "ogre": (["Boulderfist", "Crag-Walker's", "Maulhide", "Ringbreaker's", "Hold-Chief's"],
             ["Sized for an ogre and cut down for a hand, which is how the Syndicate used them.",
              "Not forged. Found, and then argued with for a long time.",
              "An ogre's belt makes a human's chest-piece. Nobody enjoys knowing that.",
              "Cured in the hold's own runoff, which is why nobody else wanted it."]),
    "rings": (["Fourth-Circle", "Lodestone", "Plumbline", "Sighting", "Standing-Stone"],
              ["The rings were here before Arathor and nobody has ever claimed them.",
               "Stand in the circle wearing this and you can feel which way the stones face.",
               "Four circles on one line, and the line is the road.",
               "Quiet in three of the rings. Not quiet in the fourth."]),
    "mere": (["Mireclutch", "Silt-Set", "Brood-Slick", "Standing-Water", "Drowned-Mere"],
             ["It drains for about an hour after you take it out of the water.",
              "The mere is shallow, warm and full, and those are the same fact.",
              "The grip is better wet, which is not how grips usually work.",
              "Freshwater. Something in there is making pearls anyway."]),
    "mine": (["Drywhisker", "Tallow-Lit", "Spoil-Heap", "Shift-Ending", "Deep-Gallery"],
             ["Mine spoil is loose, sharp and moves under you.",
              "Kobolds are frightened of the dark in a way that is not a joke to them.",
              "The marks scratched inside are a count of days. They stop, then start again lower.",
              "A mine floor is spoil and a mine fills from underneath."]),
    "barrow": (["Barrow", "Long-Watch", "Cerement", "March-Lord's", "Grave-Marble"],
               ["Arathor work. There is no smith alive who could repair it.",
                "Buried under four feet of standing water, facing the door.",
                "Three thousand years and nobody ever came to relieve the watch.",
                "The upper floor of the barrow is marble. Below the stair it is wet limestone."]),
    "bloodsail": (["Bloodsail", "Boarding", "Storm-Cut", "Purser's", "Wrackline"],
                  ["Cut short at the knee for going up a wet rock face in the dark.",
                   "A pirate crew that keeps books keeps them somewhere dry and high up.",
                   "Three years of salt and the ink in the breast pocket has never run.",
                   "They are not raiding. They are holding, and that is worse."]),
    "tide": (["Tidewrack", "Spindrift", "Low-Water", "Reefmaw", "Saltquern"],
             ["The flats are only ground for four hours a day and nobody agrees which four.",
              "Salt has set into the weave and gone hard.",
              "Something down on the pearl floor is arranging them. In rows.",
              "Brought up out of a sump that goes deeper than the cave does."]),
})


# ------------------------------------------------------------------------------- objective sugar
def k(target, n, zone=AW):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x, y, radius=8):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(item, n, label):
    """HOLD n of a real gatherable - it is not consumed on turn-in, which is the point of using
    GATHER over FETCH for herbs and ore. Argument order matches kill/fetch: target, count, then
    the label. Getting it the other way round wrote a string into `count` and only surfaced as a
    TypeError deep in audit_quests' playthrough, not as a bad-looking line in the data."""
    return dict(type="gather", target=item, count=int(n), label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None,
      gold=None, **engine):
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


# Refuge Pointe / the moor
RASKAL, GRIM, ROOK = "arathi_refuge_commander", "arathi_refuge_scout", "arathi_wall_warden"
VESH, OGRIN, NALLA = "arathi_stromgarde_antiquarian", "arathi_moor_shepherd", "arathi_goshek_informant"
HORG = "arathi_refuge_quartermaster"
# Hammerfall
GATHROK, MOK, VOSS = "hammerfall_commander", "hammerfall_sergeant", "hammerfall_apothecary"
OLEN, TAMKA, NAHTO = "hammerfall_deathguard", "hammerfall_tauren_envoy", "hammerfall_tauren_herbalist"
INNIK, THUGG, KESKA = "arathi_ring_scholar", "arathi_gorge_prospector", "arathi_refuge_runner"
# Saltspur / the coast
KAZ, OONA, VEL = "saltspur_bosun", "saltspur_shipwright", "saltspur_scout"
YELZA, PIK, HERMIT = "arathi_barrow_warden", "arathi_wreck_salvager", "arathi_bothy_hermit"
# elsewhere
THORNE = "tarren_mill_commander"      # Commander Vellis Thorne
WREN = "hbe_mill_apothecary"          # Field Apothecary Wren
TORGUN = "org_elder_2"                # Elder Torgun, Orgrimmar


# =================================================================================================
# INBOUND - three places, three reasons. The region should not be a thing you only find by
# walking into it, and the wall has been shut for the whole game until now.
# =================================================================================================
def inbound():
    A = []
    A.append(Q("arw_through_the_wall", "What Is Through the Wall", THORNE, TM, 28, 29, "moor",
        "Thoradin's Wall runs along the top of Hillsbrad and it has been a closed thing for as "
        "long as anyone at Tarren Mill has been posted here. You can see the gap in it from the "
        "mill roof on a clear day.\n\nIt is open. Commander Thorne has had that confirmed twice "
        "and does not believe either of them, because what is on the far side of a wall nobody "
        "has crossed in three years is a question with no safe answer.",
        [explore(AW, 20, 118, 10), explore(AW, 62, 100, 10)],
        "I am not sending a column through a gap I know nothing about. I am sending one person, "
        "and one person is you.\n\nGet to the gap, get through it, and keep going until you find "
        "whoever is holding the other side. Then come back and tell me whether they are holding "
        "it against us.",
        "A Horde camp, in a human ruin, flying our colours and using the ruin's own name for "
        "itself.\n\nThat is not what I expected and it is better than what I expected. Go back "
        "and tell their commander the wall works both ways now.",
        turn_in_npc_id=RASKAL))

    A.append(Q("arw_what_killed_the_scout", "What Killed Pria's Runner", WREN, HBE, 29, 30, "moor",
        "Field Apothecary Wren has a body and no answer. One of Scout Halm's runners went north "
        "to look at the wall and came back over a horse, and the wounds on him are from an "
        "animal she cannot name.\n\nShe has a professional objection to not being able to name "
        "things.",
        [k("Highland Fleshripper", 8), fetch("fleshripper_dewclaw", 5)],
        "Four punctures in an arc, and the arc is wider than a wolf's. Whatever did this is "
        "standing on that moor right now being perfectly ordinary to everyone who lives there.\n\n"
        "Bring me the dewclaws. Five will do - I want to see whether the spacing is consistent "
        "or whether I am looking at one very large individual.",
        "Consistent. So it is a species and not a monster, which is the better of the two "
        "answers and the one that means there are a great many of them.\n\nI will write it up. "
        "Highland fleshripper. Somebody has probably named it already and I do not care.",
        gear_reward_slot="trinket"))

    A.append(Q("arc_two_years_of_paper", "Two Years of Paper", TORGUN, ORG, 33, 34, "moor",
        "Elder Torgun has found a file. It is a hold called Hammerfall, somewhere in the Arathi "
        "Highlands, and it has filed a requisition every quarter for two years and received "
        "nothing, because the road to it ran through a wall that was shut.\n\nThe wall is open. "
        "The file is now a problem rather than a curiosity.",
        [deliver("orgrimmar_writ_hammerfall", "Put Orgrimmar's writ in Overlord Gath'rok's hand")],
        "Eight requisitions. Powder, iron, two smiths and a healer, and the last one just says "
        "'anything'.\n\nI cannot send a column up a road we have not walked. I can send this, "
        "and this says the city knows they are there. Do not tell me that is nothing. For two "
        "years it has been nothing, and now it is not.",
        "Two years.\n\nI am going to read this properly, and then I am going to put it on the "
        "wall of the longhouse where everyone who is still angry about it can see the date on "
        "it. Thank you for carrying it. Go and see the Quartermaster.",
        turn_in_npc_id=GATHROK,
        grant_items=carry("orgrimmar_writ_hammerfall", "Orgrimmar's Writ",
                          "Heavy paper, the Warchief's seal, and eight quarters of requisitions "
                          "bound into the back of it. None of them answered.")))
    return A


# =================================================================================================
# ARATHI WEST - Refuge Pointe, the moor, the wall. 28-33.
# =================================================================================================
def west():
    A = []
    A.append(Q("arw_hold_the_road", "The Road Is the Camp", RASKAL, AW, 28, 29, "moor",
        "Refuge Pointe holds a road. That is the whole of it - there is no fort here, there is a "
        "human ruin with tents in it and a road running past, and the road is the reason anyone "
        "is standing in the ruin.\n\nThe Syndicate works the road. Not a raid, not a war: a "
        "steady, patient skim off everything that moves along it.",
        [k("Syndicate Footpad", 10), k("Moor Adder", 6)],
        "You will not find a camp to burn. They do not have one on the road - they come down "
        "off the high ground, take what is loose, and go back up.\n\nSo you do it the slow way. "
        "Walk the road, and every time one of them comes down off the grass, make it the last "
        "time. Ten should get the message to whoever is counting on the other end.",
        "Ten, and the adders, which nobody asked you for and everybody will thank you for.\n\n"
        "The road will stay quiet for about nine days. I have measured it. That is not cynicism, "
        "that is a supply schedule.",
        nxt="arw_wide_country"))

    A.append(Q("arw_wide_country", "Wide Country", GRIM, AW, 28, 29, "moor",
        "Scout Hollowfoot's standing complaint about this moor is that it looks empty and is "
        "not. It is simply very good at being wide: everything on it is further away than it "
        "appears, and a thing that is two hours away looks like a thing that is twenty minutes "
        "away right up until you have walked for two hours.\n\nHe wants a second pair of feet "
        "to agree with him about the distances.",
        [explore(AW, 62, 56, 9), explore(AW, 88, 142, 9), explore(AW, 20, 118, 9)],
        "The High Moor, the Lowland Oaks, and the gap in the wall. Walk all three and do not "
        "ride.\n\nI am not asking you to find anything. I am asking you to find out how long it "
        "takes, because every man I have lost up here was lost to thinking he could get "
        "somewhere before dark.",
        "Now you know. The oaks are further than they look and the wall is further than that.\n\n"
        "That is the single most useful thing anyone learns on this moor, and it cannot be told. "
        "It has to be walked.",
        nxt="arw_the_gap"))

    A.append(Q("arw_the_gap", "The Gap", ROOK, AW, 29, 30, "moor",
        "Warden Ada Rook has stood at the gap in Thoradin's Wall for a year and a half. The "
        "arch above her is Arathor stonework three thousand years old and the thing she has "
        "actually been doing is counting: how many came through, from which side, and what they "
        "were carrying.\n\nThe number for the first year was zero. It is not zero any more, and "
        "a good deal of what comes through now is Syndicate.",
        [k("Syndicate Footpad", 8), fetch("syndicate_wall_tally", 4)],
        "They cross at night and they cross in threes, and every one of them is carrying a slip "
        "with a number on it.\n\nI want four of those slips. Not because I think they will tell "
        "me anything - because I have been counting for eighteen months and I would like, just "
        "once, to see somebody else's count.",
        "Four slips and all four agree with my book.\n\nEighteen months I have been doing this "
        "and it turns out I have been doing it correctly. I did not expect that to feel like "
        "anything. It does."))

    A.append(Q("arw_what_the_kites_find", "What the Kites Find", OGRIN, AW, 29, 30, "moor",
        "Shepherd Ogrin was an axethrower and is now the man who keeps the highland stag herd "
        "off the road, which he will explain to you at length if you let him.\n\nHis actual "
        "problem is the carrion kites. They have learned that the road produces bodies, and a "
        "kite that has learned that stops waiting for one.",
        [k("Carrion Kite", 10), k("Highland Fleshripper", 5)],
        "A kite is a carrion bird. It is supposed to turn up second. These ones have started "
        "turning up first and that is a thing a bird should not be able to decide to do.\n\n"
        "Thin them. And the fleshrippers while you are out there, because the rippers are the "
        "reason the kites learned.",
        "The herd came down to the low grass on its own this morning. First time since spring.\n\n"
        "They know. People think a stag is stupid. A stag is not stupid, a stag is busy."))

    A.append(Q("arw_adder_season", "Adder Season", HORG, AW, 30, 31, "moor",
        "Quartermaster Horg requisitions for a garrison of forty and is supplied for a garrison "
        "of twelve, and the gap between those two numbers is filled by whatever he can make "
        "here.\n\nAntivenin is top of the list. Moor adders come up out of the grass onto warm "
        "road stone at dusk and the camp has had four bites this month.",
        [fetch("moor_adder_gland", 8), gather("herb_bruiseweed", 6, "Bruiseweed off the moor")],
        "Eight glands and whatever bruiseweed you can pull on the way. The weed grows along the "
        "road cuts - you will walk past it whether you are looking or not.\n\nAnd keep the "
        "bruiseweed. I need to see it, not take it off you. I am not robbing people who do me "
        "favours, that is the Syndicate's business model.",
        "That is the camp covered until the weather turns.\n\nFour bites this month and nobody "
        "died, and the reason nobody died is a shelf. People think a quartermaster is a clerk. "
        "A quartermaster is a shelf with opinions."))

    A.append(Q("arw_goshek_harvest", "Go'Shek Still Brings It In", NALLA, AW, 30, 31, "syndicate",
        "Nalla Deeps has been looking at Go'Shek Farm for a month and the thing that interests "
        "her is not that the Syndicate took it. It is that the farm is still working.\n\nThe "
        "fields are cut on time. The barns are not empty. Somebody is doing the farming, and "
        "somebody else is buying what comes off it, and neither of those people is a bandit.",
        [k("Syndicate Watchman", 9), fetch("goshek_field_tally", 5)],
        "Every watchman on that farm carries a field tally, because a man guarding a harvest has "
        "to know how much harvest there is.\n\nGet me five. I want to see the yield. A yield "
        "tells you the acreage, the acreage tells you the labour, and the labour will tell me "
        "something I have been wrong about.",
        "Four hundred bushels off ground that size needs thirty people working it, and the "
        "Syndicate has nine men on that farm.\n\nSo the farmers are still there. They never left. "
        "They are working for whoever is standing in the house, which is what farmers have always "
        "done, and I owe them a better question than the one I came with.",
        nxt="arw_who_buys_the_grain"))

    A.append(Q("arw_who_buys_the_grain", "Who Buys the Grain", NALLA, AW, 31, 32, "syndicate",
        "The farm works. The farmers stayed. That leaves the part Nalla actually cares about, "
        "which is the money: four hundred bushels a season does not get eaten by nine bandits "
        "in a farmhouse.\n\nIt is going somewhere. It is being paid for. And whoever is paying "
        "for it is doing business with the Syndicate in quantity, on paper, from somewhere with "
        "a market.",
        [k("Syndicate Prowler", 8), k("Syndicate Shadowmage", 6),
         fetch("goshek_grain_contract", 1)],
        "The prowlers run the roads and the shadowmages run the house, and the paper will be on "
        "one of the two. My money is the house.\n\nBring me a contract. One is enough. I do not "
        "need the whole ledger, I need one name at the bottom of one page.",
        "Signed, countersigned, and the buyer's mark is a Hillsbrad merchant house with a "
        "charter older than the Syndicate.\n\nThey are not fencing it. They are not laundering "
        "it. They are buying grain from the people holding the farm, at a fair price, because "
        "grain is grain. I have been chasing a crime and I have found a supply chain.",
        requires_quests=["arw_goshek_harvest"], nxt="arw_the_overseer"))

    A.append(Q("arw_the_overseer", "The Overseer's Books", NALLA, AW, 32, 33, "syndicate",
        "There is one more thing on that farm that Nalla wants and cannot get at: the overseer's "
        "own room, in the main house, where the books that are not field tallies are kept.\n\n"
        "She is not asking you to kill the man. She is asking you to be in that room for long "
        "enough that the Syndicate has to move its paper somewhere else, which is the only kind "
        "of damage that lasts.",
        [explore(AW, 134, 108, 7), k("Syndicate Shadowmage", 8),
         fetch("goshek_overseer_leaf", 3)],
        "Get inside the house and be seen doing it. Take three leaves out of whatever is on that "
        "desk - any three - and leave the rest on the floor.\n\nThey will move everything within "
        "a week and moving a ledger is when a ledger gets lost. I have waited a month for one "
        "page. I can wait a week for the rest of it to fall out of a cart.",
        "Three leaves and the house in uproar. Good.\n\nThe farmers get to keep farming either "
        "way, which was never going to change and was never the point. The point is that "
        "somebody in Alterac now has to explain a gap in the accounts. Let them.",
        requires_quests=["arw_who_buys_the_grain"]))

    A.append(Q("arw_witherbark_hollow", "The Hollow", GRIM, AW, 31, 32, "witherbark",
        "There are Witherbark in a fold of ground on the west side of the moor, and Scout "
        "Hollowfoot's report on them is one line long: they were here first and they are not "
        "going anywhere.\n\nWhat has changed is that they have started coming out, which they "
        "did not do for the first eighteen months, and a troll village that changes its habits "
        "is a village that has had something happen to it.",
        [k("Witherbark Headhunter", 10), k("Witherbark Shadowcaster", 6)],
        "I want to know what changed and I am not going to find out by asking, because the last "
        "two people who tried are part of the reason I am asking you.\n\nGo in far enough that "
        "they commit to defending it. What they defend hardest tells you what they are worried "
        "about, and that is the report I actually need.",
        "The hollow, not the village. They gave up the outer camps and went hard for the hollow "
        "itself.\n\nSo there is something in the fold of that ground that matters more than their "
        "own houses, and now I know where to look.",
        nxt="arw_what_veska_hears"))

    A.append(Q("arw_what_veska_hears", "What the Harbinger Hears", GRIM, AW, 32, 33, "witherbark",
        "The thing the Witherbark are defending is in the deepest part of the hollow, and the "
        "Witherbark have a harbinger standing over it.\n\nHollowfoot has one piece of hard "
        "information: trolls bury a listening charm at the edge of a camp, facing out, to hear "
        "what is coming. Every charm in that hollow is facing IN.",
        [explore(AW, 36, 72, 7), fetch("witherbark_turned_charm", 6)],
        "Six charms, and I want them lifted where they lie so I can see which way each one "
        "faced. Do not go for the harbinger. She is not the question.\n\nThe question is why a "
        "village would spend a year listening to itself.",
        "All six facing in. Every one.\n\nThey are not watching the moor. They are watching "
        "something that is already inside the hollow with them, and they have been doing it "
        "since about the time we arrived. I am going to need to think about whether those two "
        "facts are related.",
        requires_quests=["arw_witherbark_hollow"]))

    A.append(Q("arw_the_crags", "The Crags", RASKAL, AW, 31, 32, "ogre",
        "Boulder'gor sits in the crags north of the camp and is the near end of an ogre problem "
        "that gets worse the further east you go. Commander Raskal does not have the people to "
        "deal with it and says so without apology.\n\nWhat she needs is a count, and a count "
        "means going up there.",
        [explore(AW, 100, 44, 9), k("Boulderfist Ogre", 8), k("Boulderfist Brute", 5)],
        "Get up into the crags and come back able to tell me how many. Not an impression - a "
        "number, or the closest thing to one you can stand behind.\n\nKill what comes at you on "
        "the way. That is not the task, that is the weather.",
        "More than I hoped and fewer than I feared, which is the answer I get to every question "
        "on this moor.\n\nThey are not massing. They are living there. That is a thing we can "
        "leave alone for another season and I intend to.",
        nxt="arw_the_pit_chief"))

    A.append(Q("arw_the_pit_chief", "The Pit", RASKAL, AW, 32, 33, "ogre",
        "There is a hole in the floor of the Boulder'gor cave with a lip built around it, and "
        "the ogres fight in it. The one who has never lost calls himself the Pit Chief.\n\nRaskal "
        "would happily leave the crags alone for a season. She cannot leave this alone, because "
        "two of the bodies the kites found on the road last month had been in that pit first.",
        [boss("Gor'mok the Pit Chief", BGOR)],
        "He counts out loud. Our scouts have heard him from outside the cave mouth.\n\nThe "
        "number he shouts is much higher than the number of ogres in that hold, and the "
        "difference is people off my road. Go down there and make the counting stop.",
        "Then that is finished.\n\nI am not going to pretend it was strategy. There are forty "
        "things on this moor more dangerous than one ogre in a hole, and I sent you after the "
        "one that had our people's names in his mouth.",
        requires_quests=["arw_the_crags"]))

    return A


# =================================================================================================
# STROMGARDE KEEP - the dungeon, 31-34. Givers at Refuge Pointe.
# A ruin with a ruin under it, squatted by people with an invented claim.
# =================================================================================================
def stromgarde():
    A = []
    A.append(Q("arw_stro_the_claim", "The Claim", VESH, AW, 31, 32, "syndicate",
        "Antiquarian Vesh wants to be clear about something before you go anywhere near "
        "Stromgarde: the Syndicate's claim to that keep is not a weak claim or a disputed claim. "
        "It is an invented one.\n\nThey are Alterac nobility who lost Alterac. Stromgarde was "
        "never theirs. They walked into an empty ruin three years ago and started issuing "
        "writs about it, and the writs are beautifully done.",
        [explore(AW, 46, 140, 8), fetch("stromgarde_forged_writ", 4)],
        "Get inside the outer ward and bring me four of their writs. They post them. On walls. "
        "In a keep nobody else lives in.\n\nI want them for the archive and I want them because "
        "a forgery that good is a historical document in its own right, and in two hundred years "
        "somebody is going to believe it.",
        "Look at the seal work. Look at the HAND. Whoever is doing these was trained properly in "
        "a chancery that no longer exists.\n\nThat is the saddest thing on this moor and I "
        "include the barrow.",
        nxt="arw_stro_the_gate"))

    A.append(Q("arw_stro_the_gate", "The Gate That Has Not Opened", RASKAL, AW, 31, 32, "syndicate",
        "The outer gate of Stromgarde Keep has not been opened in three years. There is a man "
        "behind it whose entire function is to not open it, and he is still being paid.\n\n"
        "Commander Raskal's interest is simpler than the Antiquarian's. The keep overlooks her "
        "road, and she would like to know what is in it.",
        [k("Syndicate Watchman", 8, STRO), k("Syndicate Footpad", 8, STRO),
         boss("Grevan the Gatekeeper", STRO)],
        "There is one way in and it is through him. I have had two scouts look at that wall and "
        "both came back with the same word, which was 'no'.\n\nSo go through the gate. Take the "
        "ward with it - the watch on that outer yard is thick and you will not get a second "
        "approach once they know you can get in.",
        "Open. Three years and it is open, and the hinge did not even complain much.\n\nEleven "
        "keys on his belt, and four of the doors they open are not standing any more. He was "
        "guarding a building that has mostly fallen down. I have no idea what to do with that.",
        requires_quests=["arw_stro_the_claim"], nxt="arw_stro_the_chapel"))

    A.append(Q("arw_stro_the_chapel", "The Evening Office", VESH, AW, 32, 33, "syndicate",
        "There is a chapel in Stromgarde Keep with no roof on it, and somebody has read the "
        "evening office in it every evening for three years.\n\nVesh has had this from two "
        "separate scouts and does not know what to do with it either. The Syndicate is a "
        "protection racket with good handwriting. It is not a thing that holds vigils.",
        [boss("Sister Mollis", STRO), fetch("mollis_office_book", 1)],
        "I want her book. Not her - her book, and if there is a way to come back with the one "
        "and not the other I would take it, and there will not be.\n\nShe is in a roofless room "
        "reading to nobody in a keep full of thieves, and whatever else that is, it is the only "
        "honest thing left in that building.",
        "Every evening. Three years. The last entry is this week.\n\nShe was not keeping it for "
        "the Syndicate. She was keeping it for Stromgarde, and Stromgarde has been dead longer "
        "than she was alive. Put that on the shelf next to the forgeries. They belong together.",
        requires_quests=["arw_stro_the_gate"], nxt="arw_stro_the_claimant"))

    A.append(Q("arw_stro_the_claimant", "The Third Claimant", RASKAL, AW, 33, 34, "syndicate",
        "The man sitting in Stromgarde's hall styles himself Lord Falconcrest and has had the "
        "keep's arms re-engraved with his own, badly, by his own hand.\n\nTwo others claimed "
        "that hall before him. He does not mention them by name and neither does anybody else, "
        "which tells you what happened to them.",
        [boss("Lord Falconcrest", STRO)],
        "He has a duelling sword and a court to use it in, except there is no court, there are "
        "nine bandits and a woman reading in the rain.\n\nHe is the one giving the orders that "
        "put bodies on my road. Everything else in that keep is furniture. Go and finish it.",
        "Third claimant, third ending. Somebody will be fourth inside a month - that keep makes "
        "the offer to whoever walks in.\n\nBut the writs stop, the road quiets, and I get to stop "
        "writing letters about it. I will take the month.",
        requires_quests=["arw_stro_the_chapel"], nxt="arw_stro_the_undercroft"))

    A.append(Q("arw_stro_the_undercroft", "The Stair Under the Keep", VESH, AW, 33, 34, "barrow",
        "This is the thing Antiquarian Vesh has wanted since the day she arrived.\n\nStromgarde "
        "is a ruin with a ruin under it. There is an undercroft beneath the throne apse that is "
        "older than the keep standing on top of it - marble where everything above is dressed "
        "stone - and the Syndicate has been living over it for three years without ever finding "
        "the stair.",
        [boss("The Vault-Thing", STRO), fetch("arathor_coffer_seal", 1)],
        "The knock-through is behind the throne. You will not find it from the hall, you will "
        "find it from the apse, and you will find it because the floor sounds wrong.\n\nThere is "
        "something down there and it has been down there the entire time. I want the coffer seal "
        "and I want to know what Arathor thought was worth sealing, and I am aware those are two "
        "questions and that I am only going to get one of them answered.",
        "Arathor's own seal on a coffer, and no record anywhere of what went into it.\n\nThey "
        "sealed it and then did not write down why, which is not carelessness - that is a "
        "decision. Somebody three thousand years ago decided the safest record was no record.\n\n"
        "I have the seal. I am going to stop there, and I would like it noted that stopping is "
        "not something I do.",
        requires_quests=["arw_stro_the_claimant"]))
    return A


# =================================================================================================
# ARATHI CENTRAL - Hammerfall, the basin, the four rings. 33-37.
# =================================================================================================
def central():
    A = []
    A.append(Q("arc_the_refuge_road", "The Refuge Road", KESKA, AC, 33, 34, "moor",
        "Runner Keska does Refuge Pointe to Hammerfall and back twice a week on foot, because "
        "wyverns are for officers. She is the only person in the region who has walked the whole "
        "road in both directions this month.\n\nIt has got worse. She wants that written down by "
        "somebody who is not her, because she has reported it twice and been told she is tired.",
        [k("Boulderfist Mauler", 10, AC), k("Bound Sentinel", 6, AC)],
        "The maulers have come down off the north shelf onto the road itself, which they did not "
        "do in spring. And there are the stone things - the sentinels - standing on the verge "
        "where they used to stand in the circles.\n\nWalk it with me in mind. Clear what is on "
        "it. Then they can tell YOU that you are tired.",
        "Ten maulers and six of the stone ones, and the road is a road again for about a "
        "fortnight.\n\nI am not going to say I told them so. I am going to carry this report "
        "myself and put it in the Overlord's hand and stand there while he reads it.",
        nxt="arc_road_report"))

    A.append(Q("arc_road_report", "Carry It to the Pointe", KESKA, AC, 33, 34, "moor",
        "Keska's road report is written and she cannot deliver it, because delivering it means "
        "two days she does not have and the next supply run leaves in the morning.\n\nRefuge "
        "Pointe needs to know what is on the road before they send anything down it.",
        [deliver("keska_road_report", "Put Keska's road report in Commander Raskal's hand")],
        "Everything on that road, where it is, and what time of day it moves. Two years of it, "
        "in one page, because one page is what a commander reads.\n\nGive it to Raskal herself. "
        "Not the quartermaster - she will file it, and it has been filed enough.",
        "Hour by hour. Two years of a woman walking the same road paying attention.\n\nI have "
        "had staff officers hand me less than this. Tell her the Pointe owes her a wyvern seat "
        "and that I will be the one arguing for it.",
        requires_quests=["arc_the_refuge_road"], turn_in_npc_id=RASKAL,
        grant_items=carry("keska_road_report", "Keska's Road Report",
                          "One page. Everything on that road, where it is and what time of day "
                          "it moves, two years of it, in a hand that has been writing on her "
                          "knee at the side of it.")))

    A.append(Q("arc_good_growing", "Good Growing", NAHTO, AC, 33, 34, "rings",
        "Herbalist Nahto Greenhoof's complaint about Hammerfall is that everyone in it is "
        "looking at the ogres.\n\nThe ogres will still be there next season. So will the basin, "
        "which has the best growing ground in the region running down its middle, and which "
        "nobody has surveyed because it is not a threat.",
        [gather("herb_liferoot", 8, "Liferoot out of the basin"),
         gather("herb_kingsblood", 6, "Kingsblood off the shelf"),
         k("Highland Elk", 6, AC)],
        "Liferoot in the wet ground down the middle, kingsblood up where it is dry. Pull both "
        "and keep both - I want to see what the basin gives, not take it off you.\n\nAnd the "
        "elk. I am sorry about the elk. They have found the liferoot too and there is not enough "
        "of it for both of us this year.",
        "Liferoot that size, this far north, in this soil.\n\nThe basin is better ground than "
        "Hillsbrad and nobody in this hold knows it. I am going to tell them. They are going to "
        "be looking at the ogres."))

    A.append(Q("arc_four_circles", "Four Circles, One Line", INNIK, AC, 34, 35, "rings",
        "Scholar Innik Barrowmouth has a map of the basin with four stone circles on it and a "
        "line drawn through all four.\n\nThe line is the trunk road. Which means either somebody "
        "built a road through four ancient monuments by coincidence, or the road is older than "
        "anyone who has ever walked it. He would like to stop being the only person who finds "
        "this interesting.",
        [explore(AC, 42, 86, 7), explore(AC, 78, 82, 7), explore(AC, 114, 78, 7),
         explore(AC, 150, 74, 7)],
        "Stand in all four. In order, west to east, and in each one look back the way you "
        "came.\n\nYou will see it on the third. On the fourth you will not be able to stop "
        "seeing it, and then you will understand why I have been in this basin for a year.",
        "You saw it. Everyone sees it on the third.\n\nFour circles on one sightline, and the "
        "sightline is a road that Arathor paved and did not lay out. They inherited it. The "
        "first human empire in the world built its highway on top of somebody else's survey and "
        "there is no record of whose.",
        nxt="arc_the_bound"))

    A.append(Q("arc_the_bound", "The Bound Ones", INNIK, AC, 35, 36, "rings",
        "There are stone figures standing in and around the circles. They do not move while you "
        "watch them and they are not in the same place twice.\n\nInnik calls them Bound "
        "Sentinels because that is what the Arathor inscription calls them, and the inscription "
        "is the only thing anyone has that was written by somebody who knew.",
        [k("Bound Sentinel", 12, AC), fetch("sentinel_core_fragment", 5),
         explore(AC, 150, 74, 7)],
        "Five cores. They have a stone at the centre and it is not the same stone as the rest of "
        "them - it is ring stone, off the circles, and that is a fact I would like five of "
        "rather than one.\n\nAnd go back to the fourth ring afterwards. Three of those circles "
        "are quiet. The fourth is not, and I want you to have the cores in your hand when you "
        "stand in it.",
        "Ring stone. All five. They are made OF the circles - somebody took the monuments apart "
        "to make the guards that stand around the monuments.\n\nThat is a closed loop and I do "
        "not like it. It means whoever did it was not protecting the rings. They were feeding "
        "them.",
        requires_quests=["arc_four_circles"]))

    A.append(Q("arc_ask_them", "Ask Them First", TAMKA, AC, 34, 35, "rings",
        "High Envoy Tamka Stillwater has asked the Boulderfist twice to stop taking the standing "
        "stones down for wall rock. Twice is not enough times to have asked.\n\nEverybody in "
        "Hammerfall thinks this is a waste of a third ask. The Envoy's position is that the "
        "third ask is the one that makes the fourth thing legitimate, and that she is not going "
        "to be the tauren who skipped it.",
        [deliver("tamka_parley_stone", "Carry the Envoy's word to Boulderfist Hall"),
         explore(AC, 162, 56, 8)],
        "A carved stone. They will not read a letter and they will not take a messenger "
        "seriously, but a thing with work in it, put down at the mouth of their hold, is "
        "understood by everyone who has ever been handed one.\n\nSet it down where it will be "
        "seen. Do not go in. Do not start anything. Walk out the way you came in and let it sit "
        "there.",
        "Then it is asked, properly, three times, and anybody who wants to say we did not try "
        "can be shown the record.\n\nI do not expect an answer. That is not the same as not "
        "expecting one, and the difference between those two things is the whole of my office.",
        nxt="arc_the_answer",
        grant_items=carry("tamka_parley_stone", "The Envoy's Parley Stone",
                          "Slate, a hand's width across, carved on both faces. The work in it is "
                          "the message - nobody is meant to read it, they are meant to see how "
                          "long it took.")))

    A.append(Q("arc_the_answer", "The Answer", TAMKA, AC, 35, 36, "ogre",
        "The parley stone came back. It was returned to Hammerfall's gate in four pieces, "
        "during the night, by somebody who got close enough to put it down and leave.\n\nHigh "
        "Envoy Stillwater has not raised her voice about it. She has asked for the pieces to be "
        "kept, and she has asked for one more thing to be confirmed before anyone does anything "
        "else.",
        [explore(AC, 170, 50, 8), k("Boulderfist Mauler", 10, AC),
         k("Boulderfist Shaman", 6, AC)],
        "Go and look at the North Shelf circle. The one closest to their hold.\n\nI want to know "
        "how much of it is still standing. Not an estimate - I want somebody who has walked the "
        "ring and counted what is left, because if there is enough of it left then this is still "
        "a conversation, and if there is not then it stopped being one before I ever arrived.",
        "Nine stones out of thirty-one.\n\nThen it was never a conversation. I have been asking "
        "politely for a year to a people who finished answering before I got here.\n\nThank you "
        "for counting. Go and tell the Overlord that the Envoy withdraws her objection to his "
        "plan. He will know which plan.",
        requires_quests=["arc_ask_them"]))

    A.append(Q("arc_the_mere", "What Is in the Water", VOSS, AC, 34, 35, "mere",
        "Apothecary Dellwyn Voss has written four reports about the Sunken Mere and Undercity "
        "has acknowledged receipt of three.\n\nThe mere is shallow, warm and standing, which is "
        "ordinary. What is not ordinary is that it is full, in a basin with no inflow worth the "
        "name, and that the things coming out of it are getting larger.",
        [k("Mere Crawler", 10, AC), fetch("mere_crawler_bladder", 6)],
        "Six bladders, intact, and intact is the word that matters - they rupture if you are "
        "careless and what is inside them is the entire sample.\n\nI am not asking you to be "
        "brave. I am asking you to be slow. Bravery has cost me two couriers and no data.",
        "Freshwater organisms with a salt-gland. In a basin eighty miles from the sea.\n\nThat is "
        "not adaptation, that is the wrong animal in the wrong water, and there is only one "
        "thing in the last three years that moves animals into water they did not evolve in. I "
        "am going to write a fifth report.",
        nxt="arc_the_silt_mother"))

    A.append(Q("arc_the_silt_mother", "The Shallow Warm Full Place", VOSS, AC, 35, 36, "mere",
        "The fifth report needs the middle of the mere, and the middle of the mere is where "
        "whatever is doing the breeding sits.\n\nVoss is explicit that he does not want it "
        "killed. He wants it LOOKED at, from close enough to count, which he concedes is a "
        "harder thing to ask of a person than killing it would be.",
        [explore(AC, 96, 118, 7), fetch("mere_pearl_freshwater", 4),
         k("Mere Crawler", 8, AC)],
        "Four pearls off the bed and a good look at what is in the middle.\n\nFreshwater pearls. "
        "In a mere. Something down there is making them and making them in rows, and I would "
        "like very much to know whether the rows mean anything or whether I am a man who has "
        "been alone with a pond for too long.",
        "Rows. Four to a row, consistently, over an area the size of this longhouse.\n\nI am not "
        "going to speculate in writing. I am going to send Undercity the pearls and the "
        "measurements and let somebody senior to me be the one who says it out loud.",
        requires_quests=["arc_the_mere"]))

    A.append(Q("arc_witherbark_village", "The Village in the Basin", OLEN, AC, 35, 36, "witherbark",
        "Deathguard Olen watches Hammerfall's east gate. Everything that has come through it in "
        "two years has been kobold, ogre, or a man with a very good reason.\n\nSince the spring "
        "it has also been Witherbark, in numbers, from a village up the basin that had been "
        "keeping to itself since before the hold was built.",
        [k("Witherbark Berserker", 10, AC), k("Witherbark Venomweaver", 7, AC)],
        "They were quiet for two years and now they are not, and nobody in this hold can tell me "
        "what changed.\n\nI am not interested in why today. Today I am interested in fewer of "
        "them arriving at my gate at four in the morning. Go up the basin and make that happen, "
        "and then we can both be curious at a reasonable hour.",
        "Quieter. Not quiet.\n\nThere is a hollow on the far side of this region where the same "
        "thing is happening to the same people, and sooner or later somebody is going to put "
        "those two reports side by side. It is not going to be me. I watch a gate."))

    A.append(Q("arc_the_hall", "Boulderfist Hall", GATHROK, AC, 36, 37, "ogre",
        "The Envoy has withdrawn her objection. Overlord Gath'rok's plan was never complicated: "
        "the Boulderfist hold a stone circle as their outer wall, they are taking the rest of "
        "the circles apart to thicken it, and they have now answered three asks with a broken "
        "stone at his gate.\n\nHe has waited a year to be allowed to do this properly.",
        [boss("Mauler Krakk", BHALL), boss("Boulderfist Hal'dun", BHALL),
         k("Boulderfist Shaman", 8, BHALL)],
        "Krakk first - he is in the long hall and he is the one the rest of them watch. Then "
        "Hal'dun, who is the hold chief and who will not come out from behind the ring wall for "
        "anything.\n\nI am not sending the garrison. A garrison takes the hold and then has to "
        "hold the hold. You go in, you end the two of them, and the rest of it stops being a "
        "problem without Hammerfall acquiring a second place to defend.",
        "Both. Good.\n\nThe Envoy wants the stones put back. I have told her that is forty men "
        "for a season and she has told me she will take forty men for a season, and I find I "
        "do not have an argument. She asked three times. I am going to say yes.",
        requires_quests=["arc_the_answer"]))

    A.append(Q("arc_the_gorge", "Drywhisker Gorge", THUGG, AC, 36, 37, "mine",
        "Prospector Thugg's position on Drywhisker is that it was a mine before the kobolds got "
        "it and it is a mine now, and the only difference is that the kobolds dug past the "
        "ore.\n\nHe wants to reopen it. Before anyone will listen to him he has to show that "
        "the seam is still there, which means samples, which means the gorge.",
        [gather("ore_iron", 8, "Iron out of the Drywhisker seam"),
         k("Drywhisker Digger", 10, AC), explore(AC, 160, 108, 8)],
        "Eight of iron off the gorge face, and keep it - I want to see the grade, not own it.\n\n"
        "The diggers work the open cut and they will come at you in threes. They are not "
        "soldiers. I want that said plainly before you go: they are miners, and we are about to "
        "argue with them about a hole.",
        "That is good iron and there is a lot of it and it is eleven feet from the surface.\n\n"
        "They walked past this. Every day for three years, carrying spoil over a seam that would "
        "keep Hammerfall in nails for a decade, to get at something deeper. I want to know what.",
        nxt="arc_dry_the_candles"))
    return A


# =================================================================================================
# DRYWHISKER DEEPS - the dungeon, 37-40, reached from Central. Four stacked galleries.
# The kobolds dug past the ore. The chain is about finding out what they were digging toward.
# =================================================================================================
def drywhisker():
    A = []
    A.append(Q("arc_dry_the_candles", "Every Candle in the Deeps", THUGG, AC, 37, 38, "mine",
        "There is a kobold in the first gallery of Drywhisker who has never let his candle go "
        "out, and who will not let anyone else carry it.\n\nThugg has been told this by two "
        "different scouts and finds it the single most useful fact he has about the place. A "
        "mine run by somebody who is that frightened of the dark is a mine with a reason.",
        [boss("Grubbis Tallow", DRY), k("Drywhisker Tunneler", 10, DRY)],
        "Tallow runs the upper gallery and he runs it on wax. Every lamp hook, every niche, "
        "every stub in that level goes back to him.\n\nTake the gallery and take him. Not "
        "because he is dangerous - because while he is lighting that level, nobody below him "
        "has to explain why they will not come up.",
        "Dipped, not woven. He had been dipping those robes his whole life.\n\nAnd the upper "
        "gallery is lit by his wax and nothing else, which means when it goes out we are going "
        "to find out what the second gallery has been doing in the dark.",
        requires_quests=["arc_the_gorge"], nxt="arc_dry_the_shift"))

    A.append(Q("arc_dry_the_shift", "The Shift Does Not End", OLEN, AC, 38, 39, "mine",
        "Deathguard Olen has read Thugg's report and found the part Thugg skipped over.\n\nThe "
        "kobold shift in Drywhisker is still being worked. There is an overseer down there "
        "blowing a whistle and diggers are still coming when it blows, three years into a mine "
        "that stopped producing anything anyone wanted.",
        [boss("Overseer Ratch", DRY), fetch("ratch_shift_whistle", 1),
         k("Brine-Choked Digger", 8, DRY)],
        "I have watched a gate for two years and the thing I have learned is that people do not "
        "keep doing a job for no reason. They keep doing it because stopping is worse.\n\nBring "
        "me the whistle. I want to hold the object that nine hundred creatures have been obeying "
        "since before we got here.",
        "Bone, drilled, and the mouthpiece is worn through to a different colour.\n\nThey still "
        "came when it blew. I had your account of it before you handed me this and I did not "
        "believe it. They still came.",
        requires_quests=["arc_dry_the_candles"], nxt="arc_dry_the_brood"))

    A.append(Q("arc_dry_the_brood", "The Warm Gallery", VOSS, AC, 39, 40, "mine",
        "Apothecary Voss has gone through the Deathguard's notes and found one line that stops "
        "him: the deepest gallery is the warm one.\n\nA mine gets colder as it goes down. "
        "Drywhisker does not. Something at the bottom of that mine is producing heat, and the "
        "kobolds have put their nursery next to it.",
        [boss("The Pick-Mother", DRY), fetch("picked_brood_shell", 5),
         explore(DRY, 70, 24, 8)],
        "Five shells and a look at the sump. I want the shells because a shell tells you the "
        "temperature it was laid at, and I want the sump because the sump is where the heat is "
        "coming from.\n\nThe Pick-Mother will be between you and both. I am sorry about that "
        "and I am going to ask you to do it anyway.",
        "Laid at blood heat. Eleven degrees above the rock around them.\n\nThey did not nest "
        "down there because it was safe. They nested down there because it was warm, and "
        "something has been keeping it warm since before there were kobolds in this mine.",
        requires_quests=["arc_dry_the_shift"], nxt="arc_dry_below"))

    A.append(Q("arc_dry_below", "What They Dug Into", GATHROK, AC, 40, 40, "mine",
        "Overlord Gath'rok has the prospector's seam report, the Deathguard's whistle and the "
        "apothecary's shell temperatures on the same table, and the three of them say one "
        "thing.\n\nThe kobolds of Drywhisker walked past a decade of iron, every day, for three "
        "years, to keep digging toward something below the sump. They found it. Nothing that has "
        "come up out of that mine since is behaving like a kobold.",
        [boss("What They Dug Into", DRY), k("Deep Seep", 8, DRY),
         fetch("sump_floor_offering", 3)],
        "I am not going to dress this up. Three of my people have been down to the sump and one "
        "came back, and what he said when he got here was that the water is not the bottom.\n\n"
        "Go down. End it. And bring up whatever they were leaving on the floor down there, "
        "because they were leaving things on the floor, and a creature that leaves things on a "
        "floor is not mining any more.",
        "Offerings. Three of them, arranged, and arranged is a word I have been avoiding since "
        "the Envoy first used it about the pearls in the mere.\n\nThat is Drywhisker finished "
        "and it is not Arathi finished. Rest. Eat something. Then go east, and when you get to "
        "the coast find a bosun called Tidewright and tell him Hammerfall sent you.",
        requires_quests=["arc_dry_the_brood"]))
    return A


# =================================================================================================
# ARATHI EAST - Saltspur Landing, the archipelago, the barrow. 37-40.
# =================================================================================================
def east():
    A = []
    A.append(Q("are_the_beachhead", "Four Boats and No Officer", KAZ, AE, 37, 38, "bloodsail",
        "Bosun Kaz Tidewright is a bosun running a shore camp, which is not a job that exists. "
        "Orgrimmar sent four boats and nobody to command them, so he took the beach and has been "
        "holding it on the assumption that somebody will eventually turn up and either promote "
        "or arrest him.\n\nIn the meantime the Bloodsail are on his shoreline.",
        [k("Wrackline Cutter", 12, AE), k("Tidecrawler", 8, AE)],
        "The cutters come along the tideline at low water, which is the only time the flats are "
        "ground at all. Four hours a day, and nobody agrees which four.\n\nBe on the shore when "
        "they are. Twelve of them and whatever crawls up with them, and we get to keep calling "
        "this a landing instead of a mistake.",
        "Then we hold the beach for another week.\n\nI have been writing that sentence in the "
        "log for two years. One of these days I am going to write a different one.",
        nxt="are_they_are_holding"))

    A.append(Q("are_six_wrecks", "Two Tides a Day", PIK, AE, 37, 38, "tide",
        "Salvager Pik Bronzewhistle can see wreck after wreck from where he is standing and the tide "
        "only lets you at them twice a day.\n\nHe knows which two are worth the walk. That "
        "knowledge is the entire business, and the reason he will tell you is that he has run "
        "out of days he can physically do it in.",
        [explore(AE, 82, 108, 8), explore(AE, 122, 107, 8), explore(AE, 58, 86, 8),
         fetch("wreck_manifest_tin", 4)],
        "The flats, at low water, and do not be clever about the timing. The water comes back "
        "across the Spindrift faster than a person walks and I have watched it happen to "
        "somebody.\n\nEvery hull has a manifest tin bolted inside the stern post. Bring me what "
        "you can reach. I want to know what these ships were carrying, because this many wrecks "
        "on one archipelago is not weather.",
        "Four tins, four manifests, and three of them are the same cargo consigned to the same "
        "buyer.\n\nThese ships were not blown onto these rocks. They were coming here. Somebody "
        "was running a route into this archipelago and the route ate them."))

    A.append(Q("are_the_hermit", "My Rock Now", HERMIT, AE, 37, 38, "tide",
        "There is a man living on Bothy Rock who was on a ferry three years ago. Then the water "
        "was a different water and the ferry was on a rock.\n\nHe has not asked anybody for "
        "anything in three years. He is asking now, and what he is asking for is small enough "
        "that it took him a while to work out how to say it.",
        [k("Storm Petrel Swarm", 8, AE), k("Reefmaw", 6, AE),
         fetch("petrel_down_bundle", 5)],
        "The petrels have the lee side. That was my side. I had it for two years and then there "
        "were more of them than there were of me, which is how most things end.\n\nAnd bring me "
        "the down. Five bundles. It is for a mattress. I am fifty-eight years old and I have "
        "been sleeping on a folded sail since before any of you got here.",
        "That is a mattress.\n\nI want to be clear that I am not coming in to your camp and I am "
        "not being rescued. This is my rock. I simply intend to sleep on it properly."))

    A.append(Q("are_they_are_holding", "They Are Not Raiding", VEL, AE, 38, 39, "bloodsail",
        "Scout Vel Ashgrave's report is one sentence and the Bosun has read it four times.\n\n"
        "The Bloodsail on this archipelago are not raiding. They are holding. A raider takes "
        "and leaves; these ones have fortified a sea cave, posted a watch on three islands and "
        "put a purser in charge of a shelf of cargo. You do not do that unless you want "
        "something that is already here.",
        [k("Wrackline Bosun", 8, AE), k("Wrackline Gunner", 8, AE),
         fetch("wrackline_watch_order", 3)],
        "Three watch orders, off three different islands. I want to see whether the same hand "
        "wrote them.\n\nIf it is three captains improvising, they are squatters and we can wait "
        "them out. If it is one hand, there is a plan, and a plan has an object.",
        "One hand. All three.\n\nSo there is a plan and somebody is running it from inside that "
        "cave, and the object of it is on this archipelago somewhere. We are not the ones who "
        "turned up uninvited. We are the ones who turned up second.",
        requires_quests=["are_the_beachhead"], nxt="are_gallowmast"))

    A.append(Q("are_gallowmast", "Gallowmast", VEL, AE, 39, 40, "bloodsail",
        "Gallowmast Isle is the furthest out and the only one with a standing watch on open "
        "ground rather than in a hull.\n\nVel wants eyes on it before anyone goes into the "
        "Wrackline cave, on the grounds that walking into a held position without knowing what "
        "is behind you is how the four boats become three.",
        [explore(AE, 157, 136, 9), k("Wrackline Wrecklamp", 8, AE),
         k("Wrackline Cutter", 8, AE)],
        "The wrecklamps are the part I do not like. A lamp crew on a rock in a shipping lane is "
        "not a watch, it is a lure, and we already have six hulls on these flats to prove it "
        "works.\n\nGet out to Gallowmast, see what they are lighting, and put the lamps out "
        "while you are there.",
        "A lure. They have been wrecking ships onto this archipelago deliberately for three "
        "years and salvaging them at leisure.\n\nWhich answers the Bosun's question and asks a "
        "worse one, because you do not run a wrecking operation this patient for cargo. You run "
        "it to stop anyone leaving.",
        requires_quests=["are_they_are_holding"], nxt="are_the_ledger_keeper"))

    A.append(Q("are_a_hull_that_floats", "One That Floats", OONA, AE, 38, 39, "tide",
        "Shipwright Oona Keelsplice has been looking at a shoreline of broken hulls for two years with nothing to "
        "fix them with. Hammerfall has timber and no reason to send it; Saltspur has reason and "
        "no timber.\n\nWhat she can get is what is already out there, if somebody will go and "
        "cut it off a hull at low water without drowning.",
        [gather("wood_driftwood_stump", 10, "Sound timber off the wrecks"),
         k("Tidecrawler", 10, AE), fetch("wreck_bronze_fitting", 6)],
        "Ten of sound timber and six fittings - bronze, off the rails and the cleats, and bronze "
        "because three years of salt has not touched it and iron is a brown stain.\n\nKeep the "
        "timber. I need to see the grade before I plan around it. If it is all rot I would "
        "rather know now than halfway through a keel.",
        "Not rot. Two hulls' worth of sound timber lying on the flats where I could see it from "
        "the jetty the whole time.\n\nGive me a crew and a tide and I will give you a boat. A "
        "small one. But a boat that goes where it is pointed, which is more than this landing "
        "has had since it was a landing."))

    A.append(Q("are_the_barrow_door", "Nobody Told Them", YELZA, AE, 38, 39, "barrow",
        "Barrow-Watcher Yelza stands outside the Drowned Barrow and does not go in.\n\nArathor "
        "buried its eastern march in there three thousand years ago and the march is still "
        "standing its watch. They are not cursed, they are not raised, and as far as she can "
        "tell they are not angry. Nobody ever came to relieve them, so they are still on duty.",
        [k("Barrow Shade", 10, AE), k("Arathor Revenant", 8, AE),
         explore(AE, 38, 50, 8)],
        "Dey not comin' out to hunt. Dey comin' out because you on de road an' de road is deir "
        "post, an' dat is all it ever been.\n\nI not askin' you to go in. Go up to de door an' "
        "stand where dey can see you, an' put down de ones dat come. Dat way I know how far out "
        "de post reaches, an' how many we talkin' about.",
        "Two hundred paces from de door, an' not one step past it.\n\nDey holdin' a line. Still. "
        "Three t'ousand years after de last person who could tell dem to stop was put in de "
        "ground behind dem.",
        nxt="are_the_barrow_warden"))

    return A


# =================================================================================================
# THE EAST'S INTERIORS - Wrackline Hold, The Tidewrack, The Drowned Barrow. 39-40.
# The barrow chain is the region's finale, and it ends by relieving a watch.
# =================================================================================================
def east_interiors():
    A = []
    A.append(Q("are_the_ledger_keeper", "The Purser", KAZ, AE, 39, 40, "bloodsail",
        "The Bloodsail in Wrackline Hold keep books. There is a man on a dry shelf above the "
        "tideline who writes down every bolt they spend and what it was spent on, and the Bosun "
        "has decided that is the thread to pull.\n\nA crew with a purser has an owner. Find the "
        "purser and you find out who the owner is.",
        [boss("Ledger-Keeper Ashkin", WRACK), fetch("ashkin_consignment_book", 1),
         k("Wrackline Gunner", 8, WRACK)],
        "Everything they have taken off six ships went across his shelf and into his book.\n\nI "
        "want that book more than I want him, and I am aware I am going to get both. Bring it "
        "out dry. He keeps it high up for a reason and the reason is the only thing in that cave "
        "with any sense in it.",
        "Three years of consignments and every one of them goes to the same mark.\n\nThe "
        "Bloodsail are not freelancing out here. Somebody is paying them to close this "
        "archipelago, and when I send this to Orgrimmar they are going to have to send an "
        "officer, which means I am about to be either promoted or arrested.",
        requires_quests=["are_gallowmast"], nxt="are_mory_vane"))

    A.append(Q("are_mory_vane", "She Took It From the Sea Side", KAZ, AE, 39, 40, "bloodsail",
        "Captain Mory Vane took Wrackline Hold from the sea side, which nobody had thought was a "
        "side.\n\nThe Bloodsail gave her a ring instead of a ship. She took a cave instead of a "
        "command, fortified it, and has held the best anchorage on the archipelago for three "
        "years with a crew who were not given anything either.",
        [boss("Captain Mory Vane", WRACK), k("Wrackline Bosun", 8, WRACK)],
        "I have no quarrel with how she got there. I have a quarrel with the fact that she is "
        "there, and that six hulls are on these flats because of a lamp crew taking her "
        "orders.\n\nGo in off the shelf, not the water. The water is how she expects it and she "
        "has had three years to think about that.",
        "Then the hold is ours, the lamps are out, and the lane is open for the first time since "
        "any of us got here.\n\nI have written a different sentence in the log. It took two "
        "years. I am going to leave the page open on the table for a while.",
        requires_quests=["are_the_ledger_keeper"]))

    A.append(Q("are_the_tidewrack", "Nothing Built At All", OONA, AE, 39, 40, "tide",
        "The Tidewrack is the only place on this archipelago with nothing built in it. No "
        "shelf, no planking, no lamp. Sand, pearl floor and an open sump that goes down further "
        "than the cave does.\n\nOona wants it cleared because it is the one sheltered water on "
        "the whole coast and she cannot build a boat on a beach the tide takes twice a day.",
        [boss("Brinemaw", TIDE), k("Reefmaw", 10, TIDE), fetch("brinemaw_barbed_tooth", 4)],
        "It grows them back. That is the thing about Brinemaw that everyone gets wrong - they "
        "think the teeth on the tideline mean something died.\n\nFour barbed ones and the "
        "animal itself. I need that sump clear and I need it clear before the weather turns, and "
        "I am not going to be precious about how.",
        "Four teeth, all barbed, and no animal grows a barbed tooth to eat with.\n\nI am going "
        "to build a boat in there and I am going to try not to think about what that means. "
        "Shipwrights are very good at not thinking about the bottom.",
        nxt="are_wrack_drowned"))

    A.append(Q("are_wrack_drowned", "Who Went Looking", YELZA, AE, 39, 40, "tide",
        "There is something standing in the Tidewrack's sump holding a lantern pole.\n\nYelza "
        "has the history. Three years ago, when the water came up in the night and the first "
        "hulls went onto the flats, people went out to the tideline with poles and lamps to look "
        "for survivors. Some of them did not come back. The poles did.",
        [boss("The Wrack-Drowned", TIDE), fetch("drowned_keepsake", 4),
         explore(AE, 118, 92, 8)],
        "Everybody who drown out dere was carryin' one of somet'ing. A ring, a coin, a lock of "
        "hair. People do dat when dey goin' out on water dey not sure of.\n\nBring me four. I "
        "goin' to put dem on de cairn with a name on each one if I can find de name, an' dat is "
        "de only t'ing anybody has done for dem in t'ree years.",
        "Four keepsakes an' t'ree of dem I can name.\n\nDey went out to look for people. Dat is "
        "all dey did wrong. Go an' rest, an' den come back, because dere is one more watch on "
        "dis coast dat nobody relieved an' it is older dan dis one by a long way.",
        requires_quests=["are_the_tidewrack"]))

    A.append(Q("are_the_barrow_warden", "The Door-Shield", YELZA, AE, 39, 40, "barrow",
        "The Drowned Barrow has a warden at the top of the stair carrying a shield that was a "
        "door before it was a shield.\n\nIt is not going to let anyone past and it has not let "
        "anyone past in three thousand years. Yelza has stopped calling that a haunting. She "
        "calls it a post, because that is what it is.",
        [boss("The Barrow Warden", BARROW), k("Arathor Revenant", 10, BARROW),
         k("Barrow Shade", 8, BARROW)],
        "You go in now. I already told you what dey are an' I not goin' to pretend dis is "
        "somet'ing else.\n\nDe warden on de stair first. Everyt'ing below it is holdin' a line "
        "dat warden is holdin' de top of, an' until dat shield come down, de rest of dem not "
        "goin' to even see you properly.",
        "De stair is open.\n\nMarble above, limestone an' standin' water below. De empire put "
        "its best people in de dry part an' de water come up anyway, over t'ree t'ousand years, "
        "one winter at a time. Nobody plan for dat. Nobody could.",
        requires_quests=["are_the_barrow_door"], nxt="are_thane_aldric"))

    A.append(Q("are_thane_aldric", "Relieve the Watch", YELZA, AE, 40, 40, "barrow",
        "At the bottom of the Drowned Barrow, under four feet of standing water, facing the "
        "door, is the Thane of Arathor's eastern march.\n\nHe swore to hold it. The march is a "
        "drowned field with ogres walking over it, the empire that took his oath has been gone "
        "for three thousand years, and he is still at his post because nobody with the authority "
        "to relieve him has existed since before there was a Horde.",
        [boss("Thane Aldric's Shade", BARROW), fetch("aldric_march_signet", 1)],
        "Dere is no trick to dis an' I not goin' to invent one. He not a monster, he not cursed, "
        "an' he not goin' to listen to a troll who show up t'ree t'ousand years late wit' no "
        "standin'.\n\nSo you do it de only way it can be done. You go down dere an' you end de "
        "watch, an' you bring me his signet so dat somebody, somewhere, has de name.",
        "Aldric. Dat is de name. Dat is de whole name an' de office an' de march it was de "
        "office of.\n\nEverybody in dis region is holdin' ground dat not deirs. De ogres, de "
        "Syndicate, your Horde, me. He de only one who was actually from here, an' he de one dey "
        "forgot to tell.\n\nGo on. Tell your Overlord de east is quiet. It not true, but it de "
        "first time in t'ree t'ousand years it been close.",
        requires_quests=["are_the_barrow_warden"]))
    return A


# =================================================================================================
# DROPS
# =================================================================================================
FETCH_DROPS = {
    "Highland Fleshripper": [("fleshripper_dewclaw", "Fleshripper Dewclaw",
                              "Four punctures in an arc, and the arc is wider than a wolf's.", 0.46)],
    "Moor Adder": [("moor_adder_gland", "Moor Adder Gland",
                    "They come up onto warm road stone at dusk. That is when the camp gets bitten.",
                    0.48)],
    "Syndicate Footpad": [("syndicate_wall_tally", "Syndicate Wall Tally",
                           "A slip with a number on it. Everyone crossing that gap is carrying one.",
                           0.46)],
    "Syndicate Watchman": [("goshek_field_tally", "Go'Shek Field Tally",
                            "A man guarding a harvest has to know how much harvest there is.", 0.46)],
    "Syndicate Shadowmage": [("goshek_grain_contract", "Go'Shek Grain Contract",
                              "Signed, countersigned, and the buyer's mark is older than the "
                              "Syndicate.", 0.30),
                             ("goshek_overseer_leaf", "Overseer's Ledger Leaf",
                              "Off the desk in the main house. Any three will do the damage.", 0.44)],
    "Syndicate Prowler": [("stromgarde_forged_writ", "Forged Stromgarde Writ",
                           "The seal work is immaculate. Whoever does these trained in a chancery "
                           "that no longer exists.", 0.42)],
    "Witherbark Shadowcaster": [("witherbark_turned_charm", "Turned Listening Charm",
                                 "Trolls bury these facing out. This one faced in.", 0.46)],
    "Bound Sentinel": [("sentinel_core_fragment", "Sentinel Core Fragment",
                        "Ring stone. They are made of the circles they stand around.", 0.44)],
    "Mere Crawler": [("mere_crawler_bladder", "Mere Crawler Bladder",
                      "Freshwater organism with a salt-gland, eighty miles from the sea.", 0.46),
                     ("mere_pearl_freshwater", "Freshwater Mere Pearl",
                      "Something down there is making them. In rows, four to a row.", 0.26)],
    "Brine-Choked Digger": [("sump_floor_offering", "Sump-Floor Offering",
                             "Left on the floor, arranged. A creature that arranges things is not "
                             "mining any more.", 0.40)],
    "The Pick-Mother": [("picked_brood_shell", "Brood Shell",
                         "Laid at blood heat, eleven degrees above the rock around it.", 1.0)],
    "Wrackline Cutter": [("wreck_manifest_tin", "Wreck Manifest Tin",
                          "Bolted inside the stern post. Three of the four name the same buyer.",
                          0.44),
                         ("wreck_bronze_fitting", "Bronze Wreck Fitting",
                          "Three years of salt has not touched it. The iron beside it is a brown "
                          "stain.", 0.42)],
    "Wrackline Bosun": [("wrackline_watch_order", "Wrackline Watch Order",
                         "Three islands, three orders, one hand.", 0.46)],
    "Storm Petrel Swarm": [("petrel_down_bundle", "Petrel Down Bundle",
                            "They took the lee side of Bothy Rock by weight of numbers.", 0.50)],
    "Reefmaw": [("brinemaw_barbed_tooth", "Barbed Tooth",
                 "No animal grows a barbed tooth to eat with.", 0.42)],
    # BOSS-CARRIED QUEST ITEMS, AT 1.0. A boss is killed once in a run and the objective asks for
    # exactly one of these, so anything under certainty means re-running a dungeon for a drop the
    # quest text promises is on the body.
    "Overseer Ratch": [("ratch_shift_whistle", "Ratch's Shift Whistle",
                        "Bone, drilled, and the mouthpiece worn through to a different colour. "
                        "They still came when it blew.", 1.0)],
    "Ledger-Keeper Ashkin": [("ashkin_consignment_book", "Ashkin's Consignment Book",
                              "Three years of consignments and every one of them goes to the "
                              "same mark. He kept it high up and dry, which is the only sense in "
                              "that cave.", 1.0)],
    "Sister Mollis": [("mollis_office_book", "The Evening Office",
                       "Every evening for three years, in a roofless chapel, to nobody. The last "
                       "entry is this week.", 1.0)],
    "The Vault-Thing": [("arathor_coffer_seal", "Arathor Coffer-Seal",
                         "The empire that sealed this did not write down what it was sealing. "
                         "That is a decision, not carelessness.", 1.0)],
    "Thane Aldric's Shade": [("aldric_march_signet", "March-Lord's Signet",
                              "The name, the office, and the march it was an office of. Nobody "
                              "has read it in three thousand years.", 1.0)],
    "Barrow Shade": [("drowned_keepsake", "Drowned Keepsake",
                      "A ring, a coin, a lock of hair. People carry one when they go out on water "
                      "they are not sure of.", 0.44)],
}

#: Quest-STARTER drops. The engine only offers these while the quest is unstarted and unlocked
#: and the item unheld, so there are no dead stacks in anybody's bags.
STARTER_DROPS = {
    "Syndicate Prowler": [("goshek_sealed_consignment", "Sealed Consignment",
                           "Wax, intact, and the mark on it is a Hillsbrad merchant house. A road "
                           "bandit should not be carrying a sealed anything.",
                           0.15, "arw_goshek_harvest")],
    "Arathor Revenant": [("arathor_watch_token", "Arathor Watch-Token",
                          "Bronze, worn smooth, stamped with a march that has been under water for "
                          "three thousand years. It was being carried, not worn.",
                          0.16, "are_the_barrow_door")],
}


def main():
    quests = (inbound() + west() + stromgarde() + central() + drywhisker()
              + east() + east_interiors())

    seen = {}
    for q in quests:
        if q["quest_id"] in seen:
            raise SystemExit(f"duplicate quest_id {q['quest_id']}")
        seen[q["quest_id"]] = q
    # Every requires_quests / next_quest_id must point at a quest that exists, or the chain
    # silently dead-ends and the player never sees the rest of it.
    for q in quests:
        for ref in (q.get("requires_quests") or []) + ([q["next_quest_id"]]
                                                       if q.get("next_quest_id") else []):
            if ref not in seen:
                raise SystemExit(f"{q['quest_id']}: points at missing quest {ref}")

    by_file = {}
    for q in quests:
        f = {TM: "hillsbrad", HBE: "hillsbrad", ORG: "orgrimmar"}.get(q["zone"], "arathi")
        by_file.setdefault(f, []).append(q)

    for fname, qs in by_file.items():
        path = ROOT / f"data/quests/{fname}.json"
        if path.exists() and fname != "arathi":
            data = json.loads(path.read_text())
            existing = data["quests"]
            if isinstance(existing, dict):
                for q in qs:
                    existing[q["quest_id"]] = q
            else:
                ids = {q["quest_id"] for q in qs}
                data["quests"] = [e for e in existing if e.get("quest_id") not in ids] + qs
        else:
            data = {"_notes": "Arathi Highlands quest pass (2026-11-01). Generated by "
                              "tools/build_arathi_quests.py - do not hand-edit text here.",
                    "quests": qs}
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    dp = ROOT / "data/creatures/quest_drops.json"
    drops = json.loads(dp.read_text())
    # THE LOADERS READ data["drops"], NOT THE TOP LEVEL - combat_engine._get_loot_item_drops and
    # quest_locator.item_sources both do json.load(f).get("drops", {}), so a creature key written
    # beside "drops" instead of inside it is read by nothing and the item never drops. That
    # shipped once and cost 23 un-droppable quest items. Write inside "drops".
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
    dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n")

    kinds = {}
    for q in quests:
        for o in q["objectives"]:
            kinds[o["type"]] = kinds.get(o["type"], 0) + 1
    print(f"Arathi quests: {len(quests)} total ({len(inbound())} inbound), "
          f"{len(by_file)} files touched")
    print(f"  objectives: {', '.join(f'{k} x{v}' for k, v in sorted(kinds.items()))}")
    print(f"  {len(FETCH_DROPS)} fetch sources, "
          f"{sum(len(v) for v in STARTER_DROPS.values())} starters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
