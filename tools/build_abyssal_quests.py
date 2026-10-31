#!/usr/bin/env python3
"""
The Abyssal Sands quest pass. Idempotent. 44-47.

    PYTHONPATH=. python3 tools/build_abyssal_quests.py
    PYTHONPATH=. python3 tools/audit_quests.py
    PYTHONPATH=. python3 tools/qa_quest_lore.py --zone abyssal --show

THIRTY-TWO quests, all given at Fourth Peg - eight people in tents trying to find out whether a
road across this zone is possible.

=========================================================================================================
THE ZONE'S QUESTION IS NOT "WHAT HAPPENED HERE", IT IS "IS THIS GROUND SAFE"
=========================================================================================================
Everyone already knows what happened. The water went, the limestone that was floating on it came
down, and eleven holes opened in four years in ground that had not moved in ten thousand. Northern
Tanaris has the first half of that and Glittervein has the second, and the Sands are the sentence
in the middle where it is simply TRUE and nobody is arguing about it.

So the quests are not an investigation. They are a SURVEY, which is a different shape: measured,
repetitive on purpose, and about accumulating enough readings to say something careful. Peska Vane
is not trying to build a road. She is trying to find out whether a road is possible, and those are
different jobs with different answers and only one of them has ever been funded.

THE CAMP IS PATIENT, NOT DESPERATE. These are competent people doing a job that may be impossible
who have decided that finding out is itself worth doing. Nobody here is going to be rescued and
nobody here wants to be. That is the tonal difference from Lastwater, where ten people are stuck;
Fourth Peg could strike camp and leave on four carts in a day, and has, three times.

=========================================================================================================
THREADS
=========================================================================================================
  THE LINE (6)          Peska's survey proper. Peg it, read it, wait, read it again.
  WHAT FELL IN (6)      Caravans, their beasts and the people on them. Odd Varrow was on the box
                        at Nineteen Mile and the lead pair went in ahead of him.
  WHAT CAME UP (6)      The holes did not only swallow. Vizzi goes down them on a rope.
  THE GLASSWALL (4)     One face of one pit is fused to glass, and nothing here is hot enough.
  UNDERLIGHT (4)        The eastern pit with light coming UP out of it, which is the wrong
                        direction for a hole - and the direction Glittervein lies in.
  STANDALONES (4)       Including two item-starters out in the sand.
  OUT OF THE ZONE (2)   East, to a tauren with a notebook who has been waiting four years for
                        exactly the readings in Peska's book.

THE OUT-CHAIN IS GLITTERVEIN'S INBOUND HOOK. Peska has four years of collapse dates and no theory;
Ulla Stormhollow has four years of theory and has never had a set of dates from inside the
collapse field. Neither of them knows the other exists. The player is the only thing that connects
them, and after this pass Glittervein's whole water-chain thread has somebody who was expecting it.

NO ESCORTS. NO QUEST TARGETS A NAMED RARE - the seven rares here are lore and loot and nothing else.
NO MAGIC RESISTANCE: the rule is 45+ and three of this band's four levels qualify, and the zone
still stays off it, because Glittervein at 46-52 is where resistance is the theme and a zone that
hands it out first takes that away.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/abyssal_sands.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

AB = "the_abyssal_sands"

XP = {44: 3160, 45: 3240, 46: 3320, 47: 3400}
GOLD = {44: 12600, 45: 12900, 46: 13200, 47: 13500}

tirisfal_gear.THEMES.update({
    "survey": (["Fourth-Peg", "Chainman's", "Peg-Iron", "Level-Run", "Struck-Camp"],
               ["Survey kit, and it has been struck and re-pitched three times.",
                "Everything this camp owns fits on four carts and this was on the second.",
                "Worn where a hand holds it for eight hours at a stretch.",
                "Marked in a very small hand with a date and a bearing."]),
    "fallen": (["Nineteen-Mile", "Lead-Pair", "Off-the-Box", "Cartfall", "Went-With-It"],
               ["It came off the back of a cart that did not stop going down.",
                "Teamster's kit. The teamster is still here; most of them are not.",
                "Four years under sand and the buckles still work, which is the cruel part.",
                "Somebody was wearing this on an ordinary afternoon."]),
    "cameup": (["Rope-Hand's", "No-Bottom", "Up-Through", "Lamplit", "Second-Shelf"],
               ["Taken off something that had no business being at that depth.",
                "Dropped down a hole on a line and brought back up on the same line.",
                "It smells of wet rock in a place with no water.",
                "Whatever wore this came from somewhere that still has a roof."]),
    "glasswall": (["Annealed", "Fused-Face", "Glasswall", "South-Facing", "Heat-Struck"],
                  ["One face of it is glass and will not take a scratch.",
                   "Sand went to glass here and nothing out here is hot enough to do that.",
                   "Warm hours after sundown, in a desert that goes cold.",
                   "It throws the afternoon back at you from forty yards."]),
    "underlight": (["Underlight", "Wrong-Direction", "Lit-From-Below", "Eastward", "No-Bottom"],
                   ["The light comes UP, which is the wrong direction for a hole.",
                    "Carried out of a pit you can read by at night.",
                    "Cold, and it came out of the warmest part of the map.",
                    "Everybody who looks in wants to go in. Nobody says that part."]),
})


def k(target, n, zone=AB):
    return kill(target, n, zone=zone)


def explore(zone, x, y, radius=9):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    return dict(type="dialogue", topics=list(topics))


def carry(item_id, name, desc, count=1):
    """The item the giver hands you. PASSED AS grant_items=carry(...), never splatted - splatting
    puts an on_accept key at the top level that the engine does not read and that looks exactly
    like a working grant."""
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=count)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None,
      gold=None, salt="", **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi + 2 if is_boss else hi + 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             unique_item_defs=reward_pack(qid + salt, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ---- givers. Every id is in tools/abyssal_npc_roster.py; this pass invents nobody.
PESKA = "ab_surveyor"       # Chief Surveyor Peska Vane - finding out whether, not building
HASK = "ab_rodman"          # Rodman Hask Quill - reads the hardpan and cannot write down how
ODD = "ab_teamster"         # Teamster Odd Varrow - was on the box at Nineteen Mile
VIZZI = "ab_digger"         # Rope-Hand Vizzi Trask - nine have floors, two do not
TOBBIT = "ab_quartermaster"  # Quartermaster Tobbit Lund - four carts, strikeable in a day
MARDA = "ab_cook"           # Cook Marda Pell - has fed this camp in four places
GORRA = "ab_smith"          # Smith Gorra Blacktooth - shod kodo for nine years
SEPP = "ab_reagents"        # Brewer Sepp Narrow - a three-month contract, two years ago

#: Glittervein's surveyor, four days east. The out-chain lands on her, and it is the inbound hook
#: that zone's water thread never had.
ULLA = "gv_surveyor"

FETCH_DROPS = {
    "Cartfall Scavenger": [("ab_lifted_brass", "Lifted Brass",
                            "Cart fittings, pried off something that is mostly underground.",
                            0.38)],
    "Sunken Drover": [("ab_drovers_tag", "Drover's Tag",
                       "Stamped with a house mark and a number. The house is in Steamwheedle.",
                       0.36)],
    "Pitfall Kodo": [("ab_kodo_harness", "Fouled Harness Strap",
                      "Cut, not broken. Somebody tried to get it out.", 0.40)],
    "Limestone Crawler": [("ab_crawler_plate", "Crawler Shell-Plate",
                           "Thin, curved and stronger than it looks, like everything down there.",
                           0.38)],
    "Hollowing Ooze": [("ab_ooze_residue", "Settled Residue",
                        "It eats limestone. That is why the holes have the shape they have.",
                        0.36)],
    "Glasswall Elemental": [("ab_fused_shard", "Fused Wall-Shard",
                             "Sand that went to glass, and nothing out here is hot enough.",
                             0.34)],
    "Deepwater Horror": [("ab_wet_scale", "Still-Wet Scale",
                          "Damp. It has been in a bag in a desert for a day and it is damp.",
                          0.34)],
    "Saltbone Revenant": [("ab_salt_knuckle", "Salted Knucklebone",
                           "Brine-cured, four days' walk from the nearest brine.", 0.38)],
    "Sinkhole Lurker": [("ab_lurker_spur", "Lurker's Spur",
                         "For holding on to a wall in the dark, which is a thing nothing up here "
                         "needs.", 0.36)],
    "Pit Shrike": [("ab_shrike_crop", "Shrike's Crop",
                    "What a bird has eaten tells you what is living where you cannot see.", 0.42)],
}

STARTER_DROPS = {
    "Cartfall Scavenger": [("ab_sealed_waybill", "Sealed Waybill",
                            "A cargo manifest, still sealed, for a cart that never arrived.",
                            0.22)],
    "Limestone Crawler": [("ab_second_peg_head", "Peg Head, Snapped",
                           "The top four inches of a survey stake, with a number still legible.",
                           0.24)],
}
STARTER_IDS = {"ab_sealed_waybill": "ab_never_arrived",
               "ab_second_peg_head": "ab_second_peg"}


def build():
    q = []

    # ================= THE LINE (6) =================
    q.append(Q("ab_fourth_peg", "Fourth Peg", PESKA, AB, 44, 44, "survey",
               "The camp is named for the stake it is pitched around. Learn why there are four.",
               [talk("ab_the_pegs", "ab_the_job"), explore(AB, 140, 25, 6)],
               "You came down the north gate, so you have walked about nine miles of this and you "
               "will have noticed there is no road.\n\nThere was one. It is in a hole. I am not "
               "here to build you a new one - I am here to find out whether a new one is POSSIBLE, "
               "which is a different job with a different answer, and only one of those has ever "
               "been funded.\n\nStand by the peg a moment. Everything this camp does is measured "
               "from that stake.",
               "Seven months, that one has stood. The longest any of them has managed.\n\nIf you "
               "are going to be out in it, I can use you. Everything we need is a reading taken "
               "somewhere I would rather not send Hask on his own.",
               nxt="ab_the_level_run"))

    q.append(Q("ab_the_level_run", "The Level Run", HASK, AB, 44, 44, "survey",
               "Run the level west from the peg and come back with the ground under it.",
               [explore(AB, 93, 32, 8), explore(AB, 44, 16, 8), k("Pit Shrike", 8)],
               "A level run is two people and a long walk and it is the dullest work in the world "
               "right up until it is not.\n\nI need the ground between here and Cartfall, in a "
               "straight line, which means walking it rather than going round. Mind the shrikes - "
               "they nest where the ground is thin and they have opinions about company.",
               "Good numbers. Boring numbers, which out here is the only kind worth "
               "having - and three years ago there were no numbers at all, because nobody had thought to take any.\n\nWhat I cannot write down is the other thing. The hardpan RINGS "
               "different over a void. Not much. It is louder in the cold. I have been trying to "
               "put that in a book for two years and it keeps coming out sounding like a man "
               "guessing."))

    q.append(Q("ab_reading_the_pan", "What Hask Hears", HASK, AB, 44, 45, "survey",
               "Test the thing he cannot write down, in the one place it can be checked.",
               [k("Limestone Crawler", 9), fetch("ab_crawler_plate", 5)],
               "There is one way to test me and you are going to hate it: the crawlers come up "
               "through the thin ground. Where they are thickest is where the roof is "
               "worst.\n\nSo. Go where I say the hardpan rings wrong, count what comes out at you, "
               "and bring me the plates. If I am right you will have a bad afternoon and I will "
               "have a method.",
               "Five. You got five off a stretch I called thin, and Peska's rod came back at "
               "eleven on the stretch either side of it.\n\nThat is not proof. It is the first "
               "thing I have had that is even the same SHAPE as proof.",
               salt="b"))

    q.append(Q("ab_wait_and_read", "Come Back in Four Days", PESKA, AB, 45, 45, "survey",
               "A survey is one reading taken twice, and the second reading is the whole job.",
               [explore(AB, 62, 89, 9), explore(AB, 96, 33, 9), k("Hollowing Ooze", 7)],
               "Anybody can take a reading. A reading is a number and a number on its own cannot "
               "tell you whether ground is going anywhere.\n\nTwo readings, four days apart, at "
               "the same stake: THAT tells you. We have been doing it for two years and I have "
               "nine hundred pairs of numbers and about four of them matter.\n\nTake the second "
               "pass on the Wide Sink and Nineteen Mile. And bring me ooze residue - they eat "
               "limestone, and I want to know how fast.",
               "The Wide Sink has moved eleven inches in four days. Eleven inches is nothing to "
               "look at and it is enormous in a column.\n\nThat rim is still going. Four years on, "
               "and the hole we all think of as finished is not finished."))

    q.append(Q("ab_second_peg", "The Second Peg", "item:ab_second_peg_head", AB, 44, 45, "survey",
               "The top of a survey stake, snapped off, with a number still on it.",
               [deliver("ab_second_peg_head", "the snapped peg head, to Chief Surveyor Vane")],
               "It is the top four inches of a proper survey stake, driven and then broken off "
               "about a foot above where it was driven. There is a number burned into it.",
               "Two. That is Second Peg, and Second Peg is sitting on the lip of the Wide Sink "
               "being perfectly accurate about a place that is not there any more.\n\nSomebody "
               "broke the head off it. That was not the ground. Somebody stood out there and "
               "snapped the top off a survey stake, and I have no idea who or why and I think "
               "about it more than I should.",
               salt="c"))

    q.append(Q("ab_is_it_possible", "Whether, Not How", PESKA, AB, 46, 46, "survey",
               "Enough readings to say something careful, finally.",
               [talk("ab_the_answer"), fetch("ab_ooze_residue", 6), k("Saltbone Revenant", 7)],
               "I have two years of pairs and I am close to being able to say a sentence I can "
               "defend. I would like one more set from the south, where the revenants are, and "
               "then I am going to say it whether the port likes it or not.",
               "Here it is, and you may tell Rullo Tack I said it.\n\nA road is possible. A road "
               "is NOT possible on a twenty-year bond, which is the only kind anybody will "
               "finance, because this field is still opening and four of my eleven are still "
               "moving.\n\nSo the honest answer is: ask me again in ten years. Nobody has ever "
               "paid a surveyor to say that and I expect it will cost me the contract."))

    # ================= WHAT FELL IN (6) =================
    q.append(Q("ab_on_the_box", "He Was On the Box", ODD, AB, 44, 44, "fallen",
               "The teamster who came off the back of a cart that kept going down.",
               [talk("ab_nineteen_mile"), k("Cartfall Scavenger", 8)],
               "Nineteen Mile. I was on the box and the lead pair were six lengths ahead of me "
               "when it went.\n\nI did not do anything clever. The cart went down and I came off "
               "the back of it and the ground I landed on held. That is the whole story and I have "
               "told it four hundred times.\n\nWhat I would like is for the scavengers to stop "
               "going through it. They are at the rim of that hole every day and there are people "
               "in it.",
               "Thank you. I know what they are. They came through with everything else and found "
               "a desert full of carts with nobody guarding them, and I would probably be doing "
               "the same.\n\nI would still rather they did it somewhere else."))

    q.append(Q("ab_the_lead_pair", "The Lead Pair", ODD, AB, 44, 45, "fallen",
               "The beasts went in ahead of the cart and some of them came back out.",
               [k("Pitfall Kodo", 8), fetch("ab_kodo_harness", 5)],
               "The kodo that went down are not all dead. Some of them came out the other side of "
               "something down there and they are not right, and they are the ones you see on the "
               "flats with harness still on them.\n\nCut the harness off what you have to put "
               "down. Bring it to me. It is a house mark and somebody should know whose.",
               "[He goes through the straps one at a time without hurrying.]\n\nThis one is "
               "Tarrow's. This one is Tarrow's. This one I do not know.\n\nI will write to "
               "Steamwheedle. It is four years late and I am going to do it anyway.",
               salt="d"))

    q.append(Q("ab_drovers_in_the_sand", "Still Walking the Line", MARDA, AB, 45, 45, "fallen",
               "The drovers are still on the route, in the sense that nobody ever called them off.",
               [k("Sunken Drover", 8), fetch("ab_drovers_tag", 5)],
               "I cooked for caravans for eleven years before this and I will tell you the thing "
               "about drovers: they do not stop. Weather, raiders, a broken axle - the road keeps "
               "going and so do they.\n\nThe ones out there still have not stopped. Bring me their "
               "tags. I want to cook for a camp that has done right by them, and we have "
               "not.",
               "I knew two of these. Not well. Well enough to know how they take their tea, which "
               "is the sort of thing you know about a drover.\n\nPeska will put the numbers in the "
               "book. I am going to do something else about it, and I am not going to tell you "
               "what because it is not your business and it is not hers either.",
               salt="e"))

    q.append(Q("ab_never_arrived", "The Cart That Never Arrived", "item:ab_sealed_waybill", AB,
               45, 45, "fallen",
               "A sealed manifest for freight that is somewhere under the First Hole.",
               [deliver("ab_sealed_waybill", "the sealed waybill, to Quartermaster Lund")],
               "A cargo manifest, still sealed, for a cart that is not going to arrive. The wax is "
               "intact, which after four years in a desert is its own small miracle.",
               "[He breaks the seal, reads it, and sets it down.]\n\nSeed grain. Forty bushels of "
               "seed grain for Gadgetzan, dated the spring the wells went.\n\nSomebody in that "
               "city ordered seed. In the second dry season, with the well dropping, somebody sat "
               "down and ordered next year's seed.\n\nI am going to keep this. I do not entirely "
               "know why."))

    q.append(Q("ab_what_the_birds_know", "What the Birds Know", HASK, AB, 45, 46, "fallen",
               "A shrike's crop is a survey of what is living where nobody can look.",
               [k("Pit Shrike", 9), fetch("ab_shrike_crop", 6)],
               "Here is a free method and it is not mine, it is every rodman's: open the bird.\n\n"
               "A shrike hunts the thin ground and the rim and it will eat anything it can carry. "
               "What is in its crop is a list of what is living in a place you cannot get "
               "to.\n\nSix crops will tell me more about the floor of those holes than Vizzi's "
               "rope has in a year, and I would like that on record before I say it to her face.",
               "Four of six had something in them from below the water line. From a WATER line, in "
               "the Abyssal Sands, where there has not been standing water in living "
               "memory.\n\nShe is going to be insufferable. She has been saying there is water "
               "down there for a year.",
               salt="f"))

    q.append(Q("ab_the_long_collapse", "Twenty-Two Tiles in an Afternoon", PESKA, AB, 46, 46,
               "fallen",
               "The newest hole on the map, and the longest.",
               [explore(AB, 84, 85, 9), k("Sinkhole Lurker", 8), fetch("ab_lurker_spur", 4)],
               "The Long Collapse opened eleven months ago, over about four hours, and it took "
               "twenty-two tiles of ground and a stretch of the old road with it.\n\nIt is the "
               "only one any of us watched happen. I want the rim walked and I want it walked by "
               "somebody who is not me, because I have walked it nine times and I have stopped "
               "seeing it.",
               "You can walk the length of that one and never be more than a step from the "
               "edge, and three years ago it was road.\n\nThat is in my book now, in those words, which is not how I usually write. "
               "Some things want saying plainly."))

    # ================= WHAT CAME UP (6) =================
    q.append(Q("ab_nine_have_floors", "Nine of the Eleven", VIZZI, AB, 44, 45, "cameup",
               "Somebody has to go down them, and she has been doing it alone.",
               [talk("ab_the_rope", "ab_no_bottom"), k("Limestone Crawler", 7)],
               "Somebody has to go down them. Not far - far enough to see whether there is a floor "
               "and whether the floor is going anywhere.\n\nNine of the eleven have floors. Two do "
               "not. I would like a second pair of hands on the line and I would like them "
               "attached to somebody who can fight, because the floors are not empty.",
               "Peska logs the two as 'no bottom observed'. I would log them differently. I would "
               "log them as 'do not'.\n\nNone of the eleven existed three years ago. People forget that, out here, as fast as they can.\n\nShe is being careful and I am being accurate and we have "
               "agreed to disagree about which of those is the job."),
               )

    q.append(Q("ab_up_through_the_floor", "Up Through the Floor", VIZZI, AB, 45, 45, "cameup",
               "The holes did not only swallow.",
               [k("Limestone Crawler", 10), k("Hollowing Ooze", 6)],
               "Everybody out here talks about what went IN. Four years of it. The carts, the "
               "kodo, the road.\n\nNobody wants to talk about what came OUT, and I have been down "
               "nine of these on a rope, and I am telling you that the crawlers and the oozes were "
               "not living on this desert four years ago because this desert could not feed "
               "them.\n\nThe holes opened a way. It goes both directions.",
               "Thin them where they come up and you buy the camp a week. You do not buy it two.\n\nBefore the change there was nothing under this desert that wanted to be above it.\n\n"
               "I have stopped pretending this is a problem that gets solved. It is a problem that "
               "gets managed by people who are still here, and that is me."))

    q.append(Q("ab_what_the_salt_cured", "Four Days From the Nearest Brine", SEPP, AB, 45, 46,
               "cameup",
               "The revenants are salt-cured and there is no salt out here.",
               [k("Saltbone Revenant", 9), fetch("ab_salt_knuckle", 5)],
               "I am a brewer, so I know what brine does to a bone, and the things coming up out "
               "of the southern holes are BRINE-CURED.\n\nThe nearest brine is the Shimmering "
               "Flats and that is four days' walk northwest. Either somebody is carrying salt out "
               "here for a purpose I do not want to think about, or there is brine under us.",
               "Under us. It has to be under us, and it has been coming this way for three years.\n\nThe pan is four days northwest and everybody "
               "there will tell you the water goes under and goes EAST. We are east. We have "
               "always been east. Nobody ever stopped to ask what it was going through on the "
               "way.",
               salt="g"))

    q.append(Q("ab_the_throats", "No Bottom Observed", VIZZI, AB, 46, 46, "cameup",
               "The two holes with no floor, and what comes up them.",
               [explore(AB, 17, 96, 9), k("Deepwater Horror", 7), fetch("ab_wet_scale", 4)],
               "The Throats are the two with no floor and they are the two I will not go down "
               "past forty feet.\n\nThere is something living in them that is WET. I need scale "
               "off whatever you can reach, and somebody else has to be holding the knife, because I "
               "been down that hole nine times and the tenth is where people stop coming back.",
               "Still wet. It has been in a bag, in a desert, for a day, and it is still "
               "wet.\n\nThere is water down there. Not damp - water, enough of it to keep "
               "something that size alive. Everybody in this camp has been walking over it for "
               "two years."))

    q.append(Q("ab_feeding_from_below", "What Is Feeding Them", SEPP, AB, 46, 47, "cameup",
               "Nothing in this zone is native to a desert, which is the point.",
               [k("Hollowing Ooze", 8), fetch("ab_ooze_residue", 5), k("Pit Shrike", 6)],
               "Go through the bestiary of this place with me. Crawlers: cave animal. Oozes: cave "
               "animal. The horrors in the Throats: aquatic. The revenants: brine.\n\nThere is not "
               "one thing on this map that belongs in a desert except the shrikes, and the shrikes "
               "are here because everything ELSE is here.\n\nThe entire population of this zone is "
               "a consequence of the water leaving. Bring me enough residue to say that with a "
               "number on it.",
               "A number. Finally a number.\n\nThat is not a desert bestiary with some cave "
               "animals in it. That is a cave bestiary that has had its roof taken off.",
               salt="h"))

    q.append(Q("ab_managed_not_solved", "Managed, Not Solved", VIZZI, AB, 47, 47, "cameup",
               "Buy the camp another week, properly this time.",
               [k("Sinkhole Lurker", 9), k("Limestone Crawler", 9), fetch("ab_lurker_spur", 5)],
               "Peska wants the readings. Hask wants his method. Odd wants the scavengers off the "
               "rim.\n\nI want the camp to still be here in a month, and that is a different list "
               "and it is mostly killing.\n\nI am not going to dress it up. Go and make the "
               "ground round this peg quiet for a while.",
               "Quiet. For a while.\n\nThat is the whole job and anybody who tells you different "
               "has not been here two years."))

    # ================= THE GLASSWALL (4) =================
    q.append(Q("ab_the_fused_face", "One Face of It Is Glass", HASK, AB, 45, 46, "glasswall",
               "The south face of one pit is fused, and nothing out here is hot enough.",
               [explore(AB, 134, 69, 9), k("Glasswall Elemental", 7)],
               "The Glasswall. South face, about sixty feet of it, fused solid - proper glass, you "
               "can see yourself in it in the afternoon.\n\nSand goes to glass at about three "
               "thousand degrees. There is nothing in this desert that gets to three thousand "
               "degrees, there is no volcanic rock within a hundred miles, and lightning does not "
               "do sixty feet in a line.\n\nGo and look at it and tell me what you think, because "
               "I have run out of things to think.",
               "It is not weathered. That is the part. Three years of sand on glass and the face is "
               "still smooth, which means it happened AFTER the hole opened, not before."))

    q.append(Q("ab_annealed", "Still Warm", SEPP, AB, 46, 46, "glasswall",
               "Shards off the fused face, still warm hours after sundown.",
               [k("Glasswall Elemental", 8), fetch("ab_fused_shard", 5)],
               "I have had a shard of that face on my bench for a month and it is WARM. Not hot. "
               "Warm, at midnight, in a desert that goes to freezing.\n\nBring me five more and I "
               "will find out whether it is the stone or whether it is something in the stone, and "
               "I would like it to be the stone.",
               "It is not the stone.\n\nI have crushed one, dissolved one, and left one in the "
               "dark for a week, and the one in the dark is the warmest of the three. Whatever is "
               "in that glass is not being heated. It is heating.",
               salt="i"))

    q.append(Q("ab_the_south_facing", "It Throws the Afternoon Back", MARDA, AB, 46, 46,
               "glasswall",
               "You can see the Glasswall from the camp at the right hour, and the camp "
               "has opinions.",
               [talk("ab_the_glass"), k("Glasswall Elemental", 7)],
               "Twice a year the sun gets the angle right and that face throws the whole afternoon "
               "back at us, and for about forty minutes this camp is the brightest place in "
               "Tanaris.\n\nTobbit says it is a hazard. Hask says it is beautiful. I say it is the "
               "only thing out here that does anything on a schedule and I will not have it spoken "
               "of badly.",
               "There. Now I can stand and watch it without something coming up the rise at me, "
               "which is all I have ever wanted out of that wall."))

    q.append(Q("ab_nothing_is_hot_enough", "Nothing Out Here Is Hot Enough", PESKA, AB, 47, 47,
               "glasswall",
               "Put the Glasswall in the book properly, with the thing nobody wants to write.",
               [fetch("ab_fused_shard", 6), k("Glasswall Elemental", 9), talk("ab_the_glass")],
               "I have to write up that face and I have been putting it off for seven months, "
               "because the honest entry is 'cause unknown' and I have never written that in a "
               "book with my name on it.\n\nGet me enough of it that 'cause unknown' comes with "
               "six samples and a date, which is the difference between an admission and a "
               "finding.",
               "'Cause unknown. Sixty feet, south-facing, post-collapse, six samples, no local "
               "heat source identified.'\n\nThere. It is in. I feel worse than I expected and "
               "better than I deserve.",
               salt="j"))

    # ================= UNDERLIGHT (4) =================
    q.append(Q("ab_the_wrong_direction", "The Wrong Direction for a Hole", VIZZI, AB, 46, 46,
               "underlight",
               "The easternmost pit has light coming up out of it.",
               [explore(AB, 153, 140, 9), k("Deepwater Horror", 6)],
               "East pit. Underlight, which is what the camp calls it and what Peska has grudgingly "
               "started calling it in the book.\n\nThere is light coming UP out of that hole. Not "
               "much - you cannot see it at noon - but stand on the rim after dark and you can "
               "read by it, and light does not come up out of the ground.\n\nGo and stand on it. "
               "Everybody has to once.",
               "Everybody who looks in wants to go in. That is the part nobody says out loud and "
               "it is true of every single person in this camp including me.\n\nThat light was not there before the change. Nothing here was.",
               nxt="ab_lit_from_below"))

    q.append(Q("ab_lit_from_below", "Lit From Below", HASK, AB, 46, 47, "underlight",
               "Work out what is making the light, which means getting close to it.",
               [k("Glasswall Elemental", 7), k("Hollowing Ooze", 7), fetch("ab_wet_scale", 5)],
               "It is not fire. Fire flickers and that does not. It is not the glass - wrong "
               "colour and wrong place.\n\nWhat it IS doing is getting slightly brighter every "
               "season, which I have measured, and I would like a sample of everything living "
               "within forty feet of it before I say anything about that in front of Peska.",
               "Every single thing within forty feet of that pit is wet, and the further east you "
               "go the wetter they get.\n\nEast. Everything about this zone points east and the "
               "camp is pitched in the northeast corner and I do not think that was an accident on "
               "Peska's part, whatever she says.",
               salt="k"))

    q.append(Q("ab_the_two_without", "The Two Without Floors", VIZZI, AB, 47, 47, "underlight",
               "Both bottomless pits are on the east side, and east is where the ground is worst.",
               [explore(AB, 44, 115, 8), explore(AB, 153, 140, 8), k("Deepwater Horror", 8)],
               "Nine have floors. Two do not. Both of the two are east.\n\nI have been down both "
               "to the end of my line and the line is a hundred and twenty feet and it does not "
               "reach anything.\n\nWalk both rims for me in one day, in order, and tell me whether "
               "you come back thinking what I think.",
               "They are the same hole. That is what I think and I have thought it for a year and "
               "there is no way to prove it from up here.\n\nSomething runs between them. Under "
               "us. East."))

    q.append(Q("ab_everything_points_east", "Everything Points East", PESKA, AB, 47, 47,
               "underlight",
               "Put it together: the brine, the wet scale, the light, the two with no floor.",
               [talk("ab_the_east"), fetch("ab_wet_scale", 6), k("Saltbone Revenant", 8)],
               "Sepp has brine. Hask has four shrike crops with water animals in them. Vizzi has a "
               "hundred and twenty feet of line that does not reach anything, twice, both on the "
               "east side. And there is light coming up out of the ground.\n\nI am a surveyor. I "
               "do not get to say what that MEANS. I do get to say that every single one of those "
               "points the same direction, and I want one more set of readings before I write the "
               "sentence.",
               "East. All of it, east, toward the big hole with the water in it that the goblins "
               "are sitting on - a hole that was not there before the change either, like everything else I have had to measure.\n\nSomebody over there needs to see my book and I am four years "
               "too busy to carry it.",
               nxt="ab_carry_the_book"))

    # ================= STANDALONES (4) =================
    q.append(Q("ab_four_carts", "Four Carts", TOBBIT, AB, 44, 44, "survey",
               "Everything this camp owns has to fit on four carts and be gone in a day.",
               [k("Cartfall Scavenger", 7), fetch("ab_lifted_brass", 5)],
               "Four carts. That is the rule and I did not make it, and we have struck camp in a "
               "day twice and both times I was glad about the rule and nobody else was.\n\nThe "
               "scavengers have been at the spare fittings. Brass, mostly, which they can sell and "
               "I cannot replace. Get it back.",
               "That is a cart's worth of brass. I know exactly what that is worth because I know "
               "exactly what everything here is worth, which is the entire job.\n\nPrices have been mad since the day the ground changed, and brass has been the maddest of them."))

    q.append(Q("ab_a_short_pantry", "A Short Pantry", MARDA, AB, 44, 45, "survey",
               "There is food out here. It is a short list and she knows all of it now.",
               [k("Pitfall Kodo", 7), k("Pit Shrike", 6)],
               "A desert has a pantry. It is short and most of it is unpleasant and after four "
               "camps I know all of it.\n\nKodo is the bulk of it. Shrike, if you are quick and "
               "you do not mind the work. Go and get me enough for a fortnight and I will cook you "
               "something you will be rude about and finish.",
               "There. You were rude about it and you finished it.\n\nSome of what I cook with came through with everybody else, you know. There are things growing in Tanaris now that have no business in a desert and they go in the pot like anything else.\n\nFour camps. The food has got "
               "better every time and nobody expected that, including me."))

    q.append(Q("ab_peg_irons", "Peg Irons", GORRA, AB, 45, 45, "survey",
               "Survey stakes need iron and the crawlers keep eating it.",
               [fetch("ab_crawler_plate", 6), k("Limestone Crawler", 8)],
               "I shod kodo for nine years and now I make peg irons, which is a sentence I try not "
               "to say out loud too often.\n\nThe crawlers go for them. Something in the iron, or "
               "something in the heat of it - Sepp has a theory and I have stopped listening. "
               "Bring me plate and I will line the next batch with it, and we will find out "
               "whether a crawler will chew through its own cousin.",
               "It will not. Six weeks and not a mark on them.\n\nI have lined survey stakes with "
               "the shells of the things that eat survey stakes. I would like somebody to write "
               "that down somewhere it will be found.",
               salt="l"))

    q.append(Q("ab_three_month_contract", "A Three-Month Contract", SEPP, AB, 46, 47, "survey",
               "He came out on a three-month contract two years and two camps ago.",
               [talk("ab_the_contract"), k("Saltbone Revenant", 7), k("Sinkhole Lurker", 7)],
               "I came out with the second camp on a three-month contract.\n\nThat was two years "
               "and two camps ago and nobody has ever mentioned the contract again, including "
               "me.\n\nI am not complaining and I would like that understood before I ask you for "
               "anything. Go south and make the run to the Throats survivable for a woman carrying "
               "glass, and I will tell you why I stayed.",
               "Because somebody has to be the one who is still here when the answer turns "
               "up.\n\nThat is it. That is the whole reason and it took me eight months to work it "
               "out and about four seconds to say.",
               salt="m"))

    # ================= OUT OF THE ZONE (2) =================
    q.append(Q("ab_carry_the_book", "Four Years of Dates", PESKA, AB, 47, 47, "underlight",
               "Her collapse log, east, to somebody who has been waiting four years for it.",
               [deliver("ab_collapse_log", "Peska Vane's collapse log, to the surveyor at Lastwater"),
                talk("ab_the_east")],
               "Through the east gate, down into the hole with the water in it. There is a camp at "
               "the bottom and there is a tauren in it doing the same job I am doing from the "
               "other end.\n\nI have every collapse date since this began and no theory at all. I am told she has "
               "four years of theory and has never once had a set of dates from inside a collapse "
               "field.\n\nNeither of us knew the other existed. That is not a charming "
               "coincidence, it is a disgrace, and it is the ordinary condition of everybody who "
               "has worked on this since the sky changed.",
               "[Ulla Stormhollow reads the first twenty pages standing up, then sits down on a "
               "crate and reads the rest without saying anything.]\n\nShe has dates.\n\nFour "
               "years I have had a shape with no numbers in it, and there is a goblin four days "
               "northwest who has been writing the numbers down the entire time and thought she "
               "was doing something else.\n\nTell her - no. I will write. Some things should not "
               "be carried by somebody else.",
               nxt="ab_the_answer_comes_back",
               grant_items=carry("ab_collapse_log", "Peska Vane's Collapse Log",
                                 "Eleven holes, four years, every date and bearing, in a very "
                                 "small hand.")))

    q.append(Q("ab_the_answer_comes_back", "What She Said Back", ULLA, AB, 47, 47, "underlight",
               "Carry the reply west, and the Sands finally get told what happened to them.",
               [deliver("ab_ullas_reply", "Ulla's reply, to Chief Surveyor Vane"),
                talk("ab_the_reply")],
               "I have written it out. It is four pages and the first three are arithmetic she "
               "will be able to check herself, which is the only kind of letter worth sending to "
               "somebody like her.\n\nThe fourth page is what it means, and she is not going to "
               "like it, because it means her field is going to keep opening until somebody stops "
               "the thing that is doing it.",
               "[Peska reads it twice. Then she goes and stands by the peg for a while.]\n\nIt is "
               "not the ground.\n\nTwo years. Two years of me reading the hardpan and Hask "
               "listening to it and both of us trying to work out what was wrong with the ROCK, "
               "and the rock is fine. The rock has done nothing. The rock has been holding up "
               "exactly as well as rock does when there is water under it.\n\nI am going to have "
               "to tell the camp. And then I am going to have to write to the port and tell them "
               "the answer to 'is a road possible' is 'ask whoever is at the bottom of that "
               "hole'.",
               grant_items=carry("ab_ullas_reply", "Ulla Stormhollow's Reply",
                                 "Four pages. Three of arithmetic and one of what it means.")))

    return q


def audit(quests):
    bad = []
    ids = {q["quest_id"] for q in quests}

    for q in quests:
        blob = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text",
                                                        "turn_in_text"))
        if "escort" in blob.lower() or any(o["type"] == "escort" for o in q["objectives"]):
            bad.append(f"{q['quest_id']}: escort")

    rares = {"The First Down", "Axleback", "The Wide Sink Mother", "Glasswall Warden",
             "The Thing in the Throat", "Longcollapse", "Underlight"}
    for q in quests:
        for o in q["objectives"]:
            if o.get("target") in rares:
                bad.append(f"{q['quest_id']}: targets the rare {o['target']}")
            if o["type"] == "kill_boss":
                bad.append(f"{q['quest_id']}: kill_boss, and this zone has no pinned boss")

    # NO MAGIC RESISTANCE. Three of this band's four levels qualify under the 45+ rule and the
    # zone stays off it anyway, because Glittervein at 46-52 is where resistance is the theme and
    # a zone that hands it out first takes that away.
    for q in quests:
        for it in q.get("unique_item_defs", []):
            stats = dict(it.get("secondary_stats") or {}, **(it.get("primary_stats") or {}))
            if any("resistance" in kk for kk in stats):
                bad.append(f"{q['quest_id']}: {it['name']} carries resistance, which this zone "
                           f"deliberately leaves to Glittervein")

    # A GATHER OR FETCH MUST NOT TARGET A WORLD-NODE MATERIAL - it gates the quest behind having
    # that gathering profession at the right skill, and nothing about the quest says so.
    for q in quests:
        for o in q["objectives"]:
            if o["type"] in ("gather", "fetch") and str(o.get("target", "")).startswith(
                    ("herb_", "ore_", "crystal_", "wood_", "essence_")):
                bad.append(f"{q['quest_id']}: {o['type']}es the node material {o['target']}")

    # AN EXPLORE TARGET MUST BE STANDABLE. Every pit on this map is impassable, so aiming an
    # explore at a landmark means aiming it at the one place in the zone nobody can reach - three
    # of these were pit CENTRES and the quests were uncompletable. Rim coordinates, measured off
    # the built map, not read off the PITS table.
    import os as _os
    _os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import tools.handbuilt_abyssal_sands as _A
    from tools import tirisfal_kit as _T
    _z = _T.build(_A).zone
    for q in quests:
        for o in q["objectives"]:
            if o["type"] != "explore":
                continue
            ox, oy, rad = o["target_x"], o["target_y"], o.get("radius", 9)
            if not any(_z.is_walkable(ox + dx, oy + dy)
                       for dx in range(-rad, rad + 1) for dy in range(-rad, rad + 1)
                       if 0 <= ox + dx < _A.W and 0 <= oy + dy < _A.H):
                bad.append(f"{q['quest_id']}: explores ({ox},{oy}) r={rad}, where nothing is "
                           f"walkable - every pit here is impassable, so a landmark coordinate is "
                           f"the one place nobody can stand")

    # deliver targets must be granted on accept or drop
    droppable = {iid for rows in list(FETCH_DROPS.values()) + list(STARTER_DROPS.values())
                 for (iid, _n, _d, _c) in rows}
    for q in quests:
        granted = {g["item_id"]
                   for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            if o["type"] == "deliver" and o["target"] not in granted | droppable:
                bad.append(f"{q['quest_id']}: delivers {o['target']}, which nothing grants or drops")

    for q in quests:
        nx = q.get("next_quest_id")
        if nx and nx not in ids:
            bad.append(f"{q['quest_id']}: chains to {nx}, which this pass does not define")

    # THE ENGINE'S RULE, not a narrower one. prose_count_mismatches looks for a number within two
    # words of ANY word from an objective's target id and binds it to that objective - so the
    # failure is a number near a target word that is not that objective's count, whether or not
    # two targets share the word. Checking only shared words missed "four years of collapse dates"
    # beside a count-1 ab_collapse_log, which the game's own audit then caught.
    NUMWORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
               "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "dozen": 12}
    for q in quests:
        words = {}
        for o in q["objectives"]:
            for w in str(o.get("target", "")).lower().replace("_", " ").split():
                if len(w) > 3:
                    words.setdefault(w, []).append(o.get("count", 1))
        blob = " ".join(str(q.get(kk) or "") for kk in ("description", "accept_text",
                                                        "turn_in_text"))
        low = [t.lower() for t in re.findall(r"[A-Za-z0-9']+", blob)]
        for i, t in enumerate(low):
            if t not in words:
                continue
            for x in low[max(0, i - 2):i + 3]:
                n = int(x) if x.isdigit() else NUMWORD.get(x)
                if n is not None and n not in words[t]:
                    bad.append(f"{q['quest_id']}: '{x} ... {t}' puts the number {n} beside an "
                               f"objective word whose count is {words[t]} - the prose count will "
                               f"be read as the objective's")
                    break
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    quests = build()
    ids = [q["quest_id"] for q in quests]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids")
        return 1

    bad = audit(quests)
    if bad:
        print("\nFAILED - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    OUT.write_text(json.dumps({"quests": quests}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for cre, rows in list(FETCH_DROPS.items()) + list(STARTER_DROPS.items()):
        have_rows = {r["item_id"]: r for r in drops.get(cre, [])}
        for (iid, nm, desc, ch) in rows:
            rec = {"item_id": iid, "name": nm, "category": "quest", "description": desc,
                   "chance": ch}
            if iid in STARTER_IDS:
                rec["starts_quest_id"] = STARTER_IDS[iid]
            have_rows[iid] = rec
        drops[cre] = list(have_rows.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    chains = sum(1 for q in quests if q.get("next_quest_id"))
    starters = sum(1 for q in quests if str(q["giver_npc_id"]).startswith("item:"))
    print(f"{len(quests)} quests -> {OUT.name}: {chains} chained, {starters} item-started")
    return 0


if __name__ == "__main__":
    sys.exit(main())
