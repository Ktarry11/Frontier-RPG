#!/usr/bin/env python3
"""
Central Stranglethorn + Veilfall Cave + the Gurbashi Arena quest pass.  Idempotent.

    PYTHONPATH=. python3 tools/build_stranglethorn_central_quests.py
    PYTHONPATH=. python3 tools/build_quest_text.py stranglethorn_central
    PYTHONPATH=. python3 tools/audit_quests.py
    PYTHONPATH=. python3 tools/qa_quest_lore.py --zone stranglethorn_central --show

Writes data/quests/stranglethorn_central.json and the pass's new drop rows to
tools/staging_drops_stranglethorn_central.json.  THIRTY quests across the band 33-38: the first
eighteen (2026-10-30) and twelve more the same day, in knot_cord_line / stonework / basin_more /
road_more / bay_more - each of which has its own block comment.

THE SECOND PASS, IN ONE PARAGRAPH.  Twelve quests, none of which introduces a person or an item: every
giver is already in a roster and every fetch and gather names one of the thirteen quest items the live
drop table already has a source for, because three agents are expanding Stranglethorn at once and
data/npcs/ambient_npcs.json and data/creatures/quest_drops.json belong to all three.  So this pass
writes neither.  It hangs the twelve off loose ends the first eighteen left on the floor - the two
words that turned out to be the same word, the centre gate that opened twice in a season, the lamps
nobody is trimming now, Garza's tenth report, Ulua's hands, and a nine-year-old who was told no - and
it adds the two things the first pass could not: DIALOGUE objectives (world/quest_dialogue.py now
merges a per-zone module, so world/quest_dialogue_stranglethorn_central.py is ours alone) and ONE
CHAIN THAT LEAVES THE ZONE (the knot-cord line, out to Tarren Mill on the windrider run and back).

NO ESCORTS (Kyle's standing rule, and the only hard "never" in quest design).
NO QUESTS BUILT AROUND RARES - Drumhide and Gorbuk the Shelf-King are the zone's two named rares and
Sheetfall is the cave's; all three are lore and loot and none of them is an objective.  The five arena
bosses and Veilspeaker Zul'Rath are PINNED CHAMBER BOSSES, not rares, so kill_boss on those is fine.
NO MAGIC RESISTANCE and NO CRAFTING MATERIAL: every reward is an equippable off tirisfal_gear, the band
tops out at 38, and the floors for those are 45 and 60.

=========================================================================================================
THE PROBLEM THIS ZONE HANDS YOU: THERE IS NO TOWN IN IT
=========================================================================================================
tools/handbuilt_stranglethorn_central.py ships NPC_POSITIONS = {} and a one-line explanation - the
middle third of the jungle is the only STV zone that never offers you a bed.  So the question "who gives
these quests" is the zone's design problem and not an inconvenience, and the answer is FOUR SOURCES, in
deliberately different registers:

  THE TWO TOWNS AT THE ENDS       Grom'gol in the north and Booty Bay in the south both have a reason
                                  to care about the middle, and they are opposite reasons.  Grom'gol
                                  cares because the road is its only route south and the camp counts
                                  people onto it (Sentry Vrak) - the north's interest in Central is
                                  ANXIETY.  The Bay cares because the arena drums carry down the cape
                                  and the Bay takes money on them - the south's interest is APPETITE.
                                  Four quests are given in those towns and worked in the middle, and
                                  one chain runs the whole length: Vrak posts you onto the road at the
                                  north seam and The Quiet Man pays you out in the Bay at the south.
  SIX PEOPLE CAMPED ON THE ROAD   tools/build_stranglethorn_central_npcs.py.  Not a town: no vendor, no
                                  innkeeper, no hearth.  A road-ganger at the fork, a tout and a
                                  gatehouse broker on the arena apron, a herbalist on the dry shoulder
                                  of the Veilfall, a netsetter at the marsh landing, and a scout sitting
                                  on the one road up onto the shelf.  Every one of them is at work, and
                                  three of the zone's five threads belong to people who could not be
                                  found in either town because they do not go to towns.
  TWO QUESTS NOBODY GIVES YOU     item-starters, narrated in the second person, because a zone with no
                                  town should have at least two things that start because you picked
                                  something up and turned it over.  A numbered crate nail out of an ogre
                                  midden, and a salt-stiff betting slip out of a crocolisk.
  ONE GIVEN BY A CHILD            Scrip, the Booty Bay street kid, who has never been a mile out of the
                                  cove and has decided what the arena drums are made of.

=========================================================================================================
THE EARTH-TRANSPLANT UNDERCURRENT - nine of eighteen, and never the subject of any of them
=========================================================================================================
Kyle: "the subtle animosity and lack of trust between 'native' people of Azeroth and the players ... we
need slight tension or even casual and subtle earth references."

claude/quest_writing_guide.md puts it at roughly 10%.  Kyle has said that number is now too low, so this
pass runs it at about half the file and takes the ceiling off a different way: it is never more than one
or two sentences inside a quest that is ABOUT something else.  A player should finish the zone having
noticed a pattern they were never told about.  Plenty of people here just want a job done.

Nine, and what each one is doing:

  THE EXPLAINING                  stvc_ganger_cut.  Dubo explains what a road is - camber, kerb, where
                                  the water is supposed to go - to somebody who has obviously walked on
                                  one.  He is not being cruel.  He assumes you would not know.
  THE MARGIN                      stvc_tout_entry.  THE UGLIEST ONE, and it is the arena's, because the
                                  arena is the sharpest place in the jungle for this.  The rim bets on
                                  outsiders by preference: nobody knows what you can do, and not knowing
                                  is where a bookmaker's money is.
  THE CATEGORY                    stvc_tout_staked.  Bexxil has written "outsider" in the box where a
                                  name goes, and Zul'tamo reads it out without comment, because down
                                  here it is not an insult.  It is a column, and the column prices well.
  THE EXCEPTION                   stvc_fenn_weather.  Ordek Fenn is openly, warmly fine with you, and he
                                  is the reason the other eight read as deliberate rather than as the
                                  writer's mood.  He asks where you are from because he wants to know
                                  whether rain behaves the same there, since his whole trade assumes a
                                  wet month and a dry one.  Real curiosity, no edge, no lesson.
  THE CORRECTION                  stvc_zuljana_names.  Attache Zul'jana is the only person in Grom'gol
                                  who is actually from this jungle and the camp calls the place "the
                                  waterfall cave".  She gives you one of the Zul'Rath's four names for
                                  it and keeps the other three, and she is within her rights.
  THE QUESTION                    stvc_ulua_netsetter.  Ulua asks, carefully and not warmly, whether
                                  there is standing water where you come from and whether anyone fishes
                                  it.  She is not making conversation.  She wants to know whether her
                                  trade exists anywhere else, in case this one stops.
  THE SEPARATE COUNT              stvc_arena_first_four.  The drum crew keep a different count for
                                  fighters who came through from somewhere else, because off-worlders
                                  always open too fast.  It is said as a technical fact about drumming.
  THE COLUMN                      stvc_arena_favourite.  The board in the Bay has a field for where a
                                  fighter came from, and after today somebody has to re-price it.  The
                                  Quiet Man says this the way you would mention weather.
  THE CHILD                       stvc_scrip_drums.  Scrip asks whether anybody at the arena was from
                                  off-world, because he has heard the ones who came through always
                                  lose the first round.  From a nine-year-old, which is worse.

THE 18 -> 30 PASS REVISED THIS DOWNWARD.  Kyle, 2026-10-30: half the file is too much, the target is
about 30% across all thirty, "it must stay a note, never the zone's theme".  So the twelve new quests
carry four (stvc_notch_tithe, stvc_centre_gate, stvc_sluice_book, stvc_reed_verdict - see the block
above the new quest functions) and TWO OF THE ORIGINAL NINE WERE TRIMMED:

  stvc_ganger_cut        lost "where you're from they would have been somebody else's drains, I
                         expect".  It was the flimsiest of the nine: an aside, removable without the
                         quest noticing, which is the definition of tacked on.  What replaced it is
                         about the actual subject - who owns a cut road.
  stvc_arena_first_four  lost the drum crew's separate count for off-worlders.  Good writing, but
                         stvc_tout_entry says the same thing better two quests earlier ("nobody has a
                         form line on you lot"), and a note made twice is a theme.  What replaced it
                         explains what a drum count is FOR, which the quest needed anyway.

That leaves ELEVEN of thirty, 37%, and the honest reading is that 37% is as close to 30% as the two
allowed trims get: nine would need four, and the next two candidates are stvc_zuljana_names's
correction and stvc_fenn_weather's exception, which are respectively the only native who pushes back
about her own language and the only person in the jungle who is warm about you.  Cutting either to hit
a percentage would cost more than the percentage is worth.  They are named here so the choice is
somebody's to make and not invisible.

WHAT tools/qa_quest_lore.py SAYS, AND WHY IT IS HIGHER.  It reports 13 of 30 (43%) and FAILS the file
against its 18% ceiling - which the eighteen-quest version escaped only because the ceiling needs
n >= 20 and the old docstring said in as many words that whoever crossed twenty should look again.
Looked.  Its regex counts three things this file keeps apart:

  7 + 2    the actual Earth notes it can see.  Four more it cannot: stvc_notch_tithe never uses a
           flagged phrase, and stvc_sluice_book's is in a dialogue topic, which lives in
           world/quest_dialogue_stranglethorn_central.py and is not in the text overlay it reads.
  3        "three years" DATING THE VEILFALL'S RISE - stvc_zuljana_font, stvc_north_leg,
           stvc_ulua_cold_month.  Per claude/integration_timeline.md that span is the Integration's
           and these three are the zone's central piece of physical lore, so they are correct and
           cannot be any other number.
  2        "three years" as A PERSON'S TENURE - Vrak on the gate, Zul'jana listening to a garrison.
           The timeline doc's own test says a tenure may be any length, so these two read as
           Integration references by accident.  Changing them to any other number would drop the
           instrument to 37% and cost the prose nothing; it is not done here because the 18 are
           otherwise untouched by this pass, and it is the cheapest available improvement if the
           number matters more than the diff.

=========================================================================================================
THE SHARED SPINE - THREE GENERATIONS OF TROLL STONEWORK, AND THIS IS THE ONE THAT STILL KNOWS
=========================================================================================================
Northern Stranglethorn has Zul'Marosh: a stair-temple whose bottom is drowned, held by a remnant, and
nobody up there can tell you what the work was for.  Southern has Zul'Kundaraz, under the sea, being
cut free of vine by trolls who came back to it.  The middle has the Gurbashi, who never lost anything
because they stopped being a war band and became a business - and the arena is where the knowledge is
kept, because the arena is the only piece of that stonework still being USED for the thing it was built
for.

Gatehouse Broker Zul'tamo answers PART of it and says so: the ring is not a tradition, it is a floor
plan, and the two faces that would let you choose your order were never cut because a mason three
generations back did not want the order to be a choice.  That is the same instinct as a stair you can
only climb one way and a terrace you can only enter from below.  What the instinct was FOR he does not
claim to know, and he points south, under water, and says he has not been.  Northern asks the question;
this zone answers the HOW; Southern keeps the WHY.

Grom'gol's supply line is Northern's and is referenced twice and built on never.  The Bay's tariff war
with Ratchet is Southern's and does not appear - the Bay's APPETITE for the arena does, which is a
different and much better seam.

=========================================================================================================
THE SHAPES, because eighteen quests of one shape is eighteen errands
=========================================================================================================
  a favour, not a job .......... stvc_ulua_netsetter.  She does not want help.  She wants her nets
                                 pulled for a week and she is not saying why, and the reward is that
                                 nobody makes her say it twice.
  a giver covering a mistake ... stvc_garza_report.  Nine identical reports in eleven weeks because she
                                 lost the signed-for glass down the notch in week two.
  the sensible thing and the
  asked-for thing differ ....... also stvc_garza_report.  What she wants is the midden emptied before an
                                 inspection.  What the midden contains is a real report she now has to
                                 file, with the ten weeks attached.
  the reward is information .... stvc_arena_pair.  Two names crossed off a list, and the thing Zul'tamo
                                 says next is worth more than the gear: the house has never opened the
                                 centre gate twice in a season, and it has now.
  a bet, honestly declared ..... stvc_arena_favourite.  Bexxil has sold her stake on at the price your
                                 four rounds made, and what is left of it pays better if you LOSE.  She
                                 tells you.  She tells you because she needs eleven minutes out of you
                                 and cannot buy them from somebody who does not know she wants them.
  a giver embarrassed to ask ... stvc_fenn_lit_fall.  Two years camped at a door with people behind it
                                 and he never knocked.
  the warm giver asking for
  the worst thing .............. stvc_veilspeaker.  The one person in the zone who is glad to see you is
                                 the one who sends you to kill, and he thinks the Zul'Rath are right.
  a child's commission ......... stvc_scrip_drums.  Paid in information, and he argues with the answer.

CHAINS ESCALATE OR REVERSE.  The arena chain is emphatically not "fight boss, fight next boss": you are
ENTERED (the road thread), somebody STAKES you (Bexxil), and that is a relationship with consequences -
the third station gets changed because the rim noticed her money, and the finale is her trying to get
paid for a good loss.  The cave chain goes warm -> curious -> ashamed -> and ends with the warm one
asking for the killing.

TURN-IN IS A REACTION, NEVER A THANK-YOU.  Every accept/turn-in pair in this file disagrees about
something: what the job was, what it meant, or whether it should have been asked for.

PROSE RULE (tools/qa_quest_lore.py, claude/quest_writing_guide.md): no "brave adventurer", no "these
lands", no rhetorical-question openers, no stat numbers, and no "kill ten of X" phrasing - the counts
live inside what a person says, and tools/audit_quests.py prose_count_mismatches checks they agree with
the objectives.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/stranglethorn_central.json"
CS = "central_stranglethorn"
VF = "veilfall_cave"
GA = "gurbashi_arena"
TM = "tarren_mill"                     # the cross-zone thread's far end, a live zone key

XP = {33: 2280, 34: 2360, 35: 2440, 36: 2520, 37: 2600, 38: 2680}
GOLD = {33: 9300, 34: 9600, 35: 9900, 36: 10200, 37: 10500, 38: 10800}

# ---------------------------------------------------------------------------------------------------
# THE ZONE'S GEAR FLAVOUR.  Five themes, one per thread, and nothing in any of them came from Earth -
# the standing rule is that Earth turns up in dialogue and never as an object in the jungle.  What the
# loot is made of here is road, limestone, ogre, brackish water and arena sand.
# ---------------------------------------------------------------------------------------------------
tirisfal_gear.THEMES.update({
    "vineroad": (["Vine-Cut", "Road-Ganger's", "Nine-Day", "Milepost", "Drover's"],
                 ["Bloodvine takes the cut back in nine days. This has been cut back off it twice.",
                  "Road kit. Heavier than it looks and every ounce of it earns the weight.",
                  "Worn by somebody paid by the furlong and not by the hour.",
                  "Green stains in the seams that no amount of river will shift."]),
    "veilfall": (["Veilfall", "Spray-Band", "Limeback", "Shrinekeeper's", "Lip-Stone"],
                 ["Limestone dust has set in the weave and gone faintly hard.",
                  "It was inside the sheet of the fall, where the lamps are.",
                  "Cold, and it stays cold a long way from the water.",
                  "Zul'Rath work, and the stitching argues with the damp and wins."]),
    "moshogg": (["Mosh'Ogg", "Notch-Guard", "Shelf-Held", "Midden-Found", "Rockthrower's"],
                ["Crude, oversized, and cut down by somebody with more patience than tools.",
                 "It came off the one road up, which is the whole of anybody's claim to that rock.",
                 "Ogre-made and ogre-sized. The straps are all new.",
                 "Found in a midden with a great deal of less interesting rubbish."]),
    "snapjaw": (["Snapjaw", "Netsetter's", "Standing-Water", "Mangrove", "Silt-Set"],
                ["Brackish water has been in and out of this more times than anybody counted.",
                 "Net-weave, and laid by hands that have done it for forty years.",
                 "It dries stiff and you work it soft again every morning.",
                 "Crocolisk hide, taken off the one that took the nets."]),
    "arena": (["Gurbashi", "Rim-Bought", "Sand-Floor", "House-Odds", "Anticlockwise"],
              ["Arena sand gets into everything down there and comes out of nothing.",
               "Bought out of a purse the rim paid into and nobody split.",
               "Somebody won this in a round the board had priced the other way.",
               "Three generations of gatehouse have signed something like this in and out again."]),
    # The cross-zone thread's own flavour. The windrider line runs out of this jungle and ends on a
    # millrace in Hillsbrad, so the kit it pays in is flying kit and waterworks kit and nothing that
    # belongs to either end on its own.
    "windline": (["Wind-Rider's", "North-Leg", "Sluice-Keeper's", "Millrace", "Knot-Cord"],
                 ["Jungle damp on one side of the seam and valley frost on the other.",
                  "Line kit. It has been at both ends of a long run and smells of both.",
                  "Pate's bench mended this, and Pate mends things to last longer than he will.",
                  "Wyvern hair in the stitching, worked in so deep that picking it out would be worse."]),
})


# ---------------------------------------------------------------------------------------------------
# objective helpers
# ---------------------------------------------------------------------------------------------------
def k(target, n, zone=CS):
    return kill(target, n, zone=zone)


def boss(target, zone=GA):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def gather(item, n):
    return dict(type="gather", target=item, count=n)


def explore(zone, x, y, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    """A DIALOGUE objective: ask the giver about every topic, in any order.

    The content is NOT here. world/quest.py's QuestObjective.topics is only the completion
    condition; the label and response text live in world/quest_dialogue_stranglethorn_central.py,
    which world/quest_dialogue.py merges in by name. An unauthored topic renders no button and the
    quest cannot be finished, so every id passed here has an entry in that module and
    tools/audit_quests.py checks the pair.
    """
    return dict(type="dialogue", topics=list(topics))


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None,
      salt="", **engine):
    """One quest.

    `salt` changes ONLY the reward seed.  tirisfal_gear.specs seeds its armour-class sample off the id
    it is handed, so two quests whose ids happen to seed the same two classes cannot be separated
    without renaming one - and a quest id is a save-game key.  Salting the reward draw is the honest
    lever: audit() below fails the build on a lopsided spread, and this is what it is adjusted with.
    """
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             # NOT "rewards".  world/quest_manager.py _build_quest reads unique_item_defs and nothing
             # else; a pack authored under "rewards" loads, sits in the json and is never offered, and
             # tools/audit_quests.py resolve_rewards reports it as broken.  The Southern Thousand
             # Needles pass this file is modelled on shipped that way and all nineteen of its quests
             # award no gear - so the template is followed everywhere except here.  The two gear_reward
             # fields match what Northern Stranglethorn writes and are the engine's fallback if the
             # item defs are ever stripped.
             unique_item_defs=reward_pack(qid + salt, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ---- givers ----------------------------------------------------------------------------------------
# Grom'gol and Booty Bay (tools/build_stranglethorn_npcs.py)
VRAK = "gromgol_south_sentry"          # Sentry Vrak - counts people onto the road and off it
ZULJANA = "gromgol_troll_attache"      # Attache Zul'jana - the only person in the camp from here
SCRIP = "bootybay_street_kid"          # Scrip - has never been a mile out of the cove
BEXX = "bootybay_shipping_clerk"       # Clerk Bexx - manifest, weight, destination, in that order
QUIET = "bootybay_fence"               # The Quiet Man - did not see you come in
# Central Stranglethorn wilderness (tools/build_stranglethorn_central_npcs.py)
# The cross-zone thread's far end. Kyle approved windriders out of the jungle up to Hillsbrad, so the
# line is the mechanism and the people at the other end of it are ALREADY IN THE GAME - Pazzik keeps
# the Grom'gol wyverns, Ghulrak keeps Tarren Mill's, and Pate and Reed are the two people in the world
# whose whole working life is writing down how high a river is. data/quests/hillsbrad.json has both of
# them at level 24-25, so this is a visitor arriving with a problem, not a rewrite of their post.
# Deliberately NOT Berth-Master Zekka, Gazlowe or Customs Officer Prynn: the Southern pass has those.
PAZZIK = "gromgol_flight_master"       # Windrider-Keeper Pazzik - flies the jungle leg
GHULRAK = "tarren_mill_flight_master"  # Wind-Rider Ghulrak - flies the valley leg
PATE = "tarren_mill_sluice_keeper"     # Sluice-Keeper Pate - twenty-two years on one crank
REED = "tarren_mill_miller"            # Miller Aldous Reed - sixty years of the same water, written down
DUBO = "stvc_road_ganger"
BEXXIL = "stvc_arena_tout"
ZULTAMO = "stvc_gurbashi_broker"
ORDEK = "stvc_basin_herbalist"
ULUA = "stvc_marsh_fisher"
GARZA = "stvc_shelf_watcher"


# =========================================================================================================
# THE VINE ROAD - the zone's spine, and the four quests that end with your name on a board.
# =========================================================================================================
def vine_road():
    A = []
    A.append(Q("stvc_no_bed_between", "No Bed Between Here and the Bay", VRAK, CS, 33, 34, "vineroad",
        "Sentry Vrak has stood at Grom'gol's south gate for three years telling people that the road "
        "is the whole of the accommodation between here and the harbour. She has stopped enjoying "
        "saying it.\n\nShe keeps a tally because nobody asked her to. Eleven went south this month and "
        "nine came back through her gate, and she does not know which two are still walking.",
        [k("Bloodvine Raptor", 10), explore(CS, 107, 37, 8)],
        "Walk it. Not the first mile - down to the ford where the Veilfall crosses the road, which is "
        "where the raptors have been working, because that is the one place on the road a person has to "
        "slow down.\n\nTen of them, if you can manage ten, and look at the stones in the ford while you "
        "are standing in it. If anyone went into that water I want to know before their mother does.",
        "Nothing in the ford. Good.\n\nNo. Not good. I wanted them in the ford, because a man in a ford "
        "is a man I can account for. Two people walked off the end of my tally and the road has nothing "
        "to say about it, and that is the part of this post nobody warned me about.", nxt="stvc_ganger_cut"))

    A.append(Q("stvc_ganger_cut", "The Road Does Not Keep Itself", DUBO, CS, 33, 34, "vineroad",
        "Road-Ganger Dubo's gang keeps the Vine Road cut, and the Gurbashi pay for it, because the arena "
        "needs a crowd and a crowd needs something to walk on.\n\nBloodvine takes a cut road back in nine "
        "days. He has measured it. He will tell you the number the way other people tell you their "
        "children's names.",
        [k("Greenwater Adder", 8), gather("vine_road_cut_vine", 6)],
        "You will want to know how a road works, so. There is a camber on it - the middle sits high and "
        "the water runs off the sides, and if the water does not run off the sides you have a river with "
        "ambitions. Kerb stone holds the camber. Vine comes through the kerb.\n\nCut me six good lengths "
        "of it out of the kerb line and put eight of the green adders off the verge while you are down "
        "there. They nest in the drainage. They should not be in the drainage.",
        "You cleared the drains.\n\nI did not ask you to clear the drains. I explained the drains. "
        "Those are different and I am aware they are different.\n\nDown here the road is whoever "
        "last cut it, and tonight that was you, and I am not paying you for it.\n\nRight. Bexxil is up on the apron and "
        "she has been wanting a name. I will give her yours, and you can decide afterward whether that "
        "was a kindness.", nxt="stvc_tout_entry"))

    A.append(Q("stvc_tout_entry", "Somebody Has Already Written Your Name", BEXXIL, CS, 34, 35, "arena",
        "Tout Bexxil works the board, and the board is in Booty Bay, nailed up inside the tavern where "
        "the Baron can see it and pretend not to.\n\nShe entered you this morning. She opened you at a "
        "price, the price moved twice before noon, and she is not going to tell you either number. What "
        "she wants now is a card worth watching, and the Gurbashi have been thinning it themselves.",
        [k("Gurbashi Beast-Drover", 9), fetch("undersized_stock_tally", 4)],
        "The drovers are running undersized stock into the crates and signing it in at weight. Thin "
        "card, thin crowd, thin money, and I am the one holding paper on a thin afternoon.\n\nNine of "
        "the drovers and four of their tallies. And before you ask why I bet on somebody I have never "
        "watched fight - that is the entire reason. Nobody down here knows what you people can do. Not "
        "knowing is where my money lives. Nobody has a form line on you lot, and the rim likes "
        "that in a fighter more than it likes a fighter.",
        "You did it where they could see you.\n\nThe price came in. Do you understand what that means? "
        "The price coming in is the money going out, and the money was going to come to me.\n\nI have "
        "had to put my own purse on you to hold the line. That is not a compliment. That is a "
        "relationship, and you did not agree to it, and neither did I.", nxt="stvc_tout_staked"))

    A.append(Q("stvc_tout_staked", "Staked", BEXXIL, CS, 35, 36, "arena",
        "Bexxil's own money is on the board now, which has changed what she is. A tout can walk away "
        "from a bad afternoon. A backer cannot.\n\nThere is one piece of paper left between you and the "
        "sand, and it goes to the Gurbashi gatehouse, and the gate crew do not take a goblin's word for "
        "anything that is not a weight.",
        [k("Gurbashi Gatekeeper", 7), deliver("bexxil_entry_chit", "Put the chit in Zul'tamo's hand"),
         explore(CS, 150, 100, 8)],
        "Take the chit up the apron to the broker and put it in his hand. Not on the table. In the hand, "
        "and stand there while he reads it.\n\nSeven of the gate crew will try to stop you getting that "
        "far, because that is the job they are paid for and they will do it without any feeling about "
        "it. Do not take it personally and do not take it slowly.",
        "She has filled the chit out in her own hand. Name, weight, reach, standing - and in the box "
        "where a house goes she has put outsider.\n\nZul'tamo reads it out flat, the way he would read a "
        "weight.\n\n'Outsider. Good. Not from here is a column on this sheet, not an insult - we have "
        "had it longer than you have been in the world and it prices better than any other line on it. "
        "You are "
        "on the list. Come down when the drums start.'",
        turn_in_npc_id=ZULTAMO, nxt="stvc_arena_first_four",
        grant_items=carry("bexxil_entry_chit", "Bexxil's Entry Chit",
                          "A palm-sized square of card with a goblin's small, fast, extremely legible "
                          "handwriting on both sides of it. Every box is filled in. One of them is "
                          "filled in about you.")))
    return A


# =========================================================================================================
# VEILFALL BASIN - the prettiest corner of the zone, and the one person in it who is glad to see you.
# =========================================================================================================
def basin():
    A = []
    A.append(Q("stvc_fenn_weather", "Ordek Asks About Rain", ORDEK, CS, 34, 35, "veilfall",
        "Ordek Fenn has had a drying rack and a tarp on the dry shoulder of the Veilfall lip for two "
        "years, and he sells to Grom'gol through whoever is walking north.\n\nHe is pleased to see you "
        "in a way nobody else in this jungle has been, and he does not make a performance of it. He has "
        "a question he has been saving and it is not about the jungle.",
        [gather("veilfall_spray_moss", 7), k("Snapjaw Leechswarm", 8)],
        "There is a band of moss along the lip where the spray reaches and nowhere else - seven good "
        "handfuls would do me the season. Mind the leeches in the slack water under the pool. Eight of "
        "them and the shallows are yours.\n\nAnd while you are gone, think about this for me: where "
        "you're from, does the rain come in a season, or does it come all year? Everything I know about a "
        "plant assumes a wet month and a dry month. If it rains all year where you came from then half "
        "of what I know is local, and I would very much like to find out which half.",
        "A season, then. Good. That is one thing I do not have to throw out.\n\nNow the moss. Look at "
        "where you picked it - only the band. Only where the water reaches.\n\nThat is not a jungle "
        "plant. That is a waterfall plant, and there is one waterfall. I have been selling it to the "
        "camp as common for two years and pricing it accordingly, and I have just made myself "
        "considerably poorer by asking you a question.", nxt="stvc_fenn_lit_fall"))

    A.append(Q("stvc_fenn_lit_fall", "Somebody Lights It From Inside", ORDEK, CS, 35, 36, "veilfall",
        "After dark the sheet of the Veilfall glows. Ordek has watched it do that from a camp stool for "
        "two years and told himself it was the water doing something clever with the moonlight.\n\nWater "
        "does not do that. Lamps do that. Lamps mean wicks and oil and somebody trimming them, and that "
        "means the cave behind the fall has had people in it the entire time he has been sitting outside "
        "its door.",
        [k("Nightpelt Panther", 7), explore(CS, 40, 58, 7)],
        "The panthers work the lip at dusk, which is the honest reason I have never walked round to look "
        "- seven of them between my rack and the notch, most evenings, and I am a man with a "
        "trowel.\n\nGo round to the mouth. That is all. Stand at it and come back and tell me whether "
        "there is a door there, because I have spent two years deciding there was not one.",
        "Carved steps. Carved steps and a lamp bracket with oil still in it.\n\nTwo years. Two years I "
        "have been camped at somebody's front door, selling their moss, and I never knocked, and I told "
        "myself a story about moonlight so I would not have to.\n\nYou knocked. I am going to need a "
        "moment about that and I would rather have it alone.", nxt="stvc_zuljana_names", salt="c"))
    return A


# =========================================================================================================
# VEILFALL CAVE - the Zul'Rath, who are not Gurbashi and not Zul'Marosh, and are the only people in any
# of the three jungle caves who are in one because they want to be.
# =========================================================================================================
def cave():
    A = []
    A.append(Q("stvc_zuljana_names", "It Has a Name. Several.", ZULJANA, VF, 35, 36, "veilfall",
        "Attache Zul'jana is the only person inside Grom'gol's fence who is from this jungle, and she "
        "has spent three years listening to a garrison name things.\n\nThe camp calls it the waterfall "
        "cave. The Zul'Rath who keep it have four names for it and which one they use depends on which "
        "terrace they are standing on. She will give you one. She is keeping the others and she does not "
        "feel she owes you an explanation for that.",
        [fetch("zulrath_name_stone", 4), k("Zul'Rath Mistcaller", 8, zone=VF)],
        "Zul'Dakai. That is the one you may have, and it means the stone the water argues with - you can "
        "carry that word north and the camp can put it on a map and be pleased with itself.\n\nEach "
        "terrace has a name stone set into its lip. Bring me four of them. The mistcallers will not let "
        "you stand on a terrace long enough to read one, so you will have to go through eight of them "
        "first, and I am not going to pretend to you that I like asking for that.",
        "Four stones, four names, and the fourth one is not a name for the cave at all.\n\nIt is a name "
        "for the water. And it is the same word the Gurbashi use for the sand on their arena floor - the "
        "exact same word, same two sounds, and one lot means a river and the other lot means a "
        "killing-ground.\n\nI have known both of those words my whole life and never once put them next "
        "to each other. Go and ask the gatehouse what they think they are saying.", nxt="stvc_zuljana_font"))

    A.append(Q("stvc_zuljana_font", "The Font, and the Argument With It", ZULJANA, VF, 36, 37, "veilfall",
        "The shrine terraces are the part a visitor notices. The Font at the east end is where the "
        "Zul'Rath do the actual work, and the work is measurement: a knotted cord let into the water "
        "every morning and read against the one from the morning before.\n\nThree years ago the fall "
        "changed. More water, and in the wrong month. They have been arguing with it since, and the "
        "argument is written down.",
        [fetch("veilfall_tally_cord", 5), k("Spraywater Elemental", 8, zone=VF), explore(VF, 104, 72, 7)],
        "Five cords and the chamber they are read in. Nothing else - leave the shrine alone, it is not "
        "ours and it is not yours.\n\nThe spraywater will come at you in the Font because the Font is "
        "what they are made of; eight of them will clear you a quarter of an hour to work in. Read "
        "nothing. Carry it. I will do the reading.",
        "Up. The fall has been up since the year the sky changed over and it has not come back down "
        "once.\n\nI am not carrying this to Overseer Mokra. She will ask what it means, and the honest "
        "answer is that the river is now draining a country that was not there to drain, and that the "
        "water has to be coming off something, and that nobody has gone to look at what.\n\nShe would "
        "write it down. That is the problem. She writes everything down.", nxt="stvc_veilspeaker"))

    A.append(Q("stvc_veilspeaker", "The Veilspeaker Will Not Be Argued With", ORDEK, VF, 36, 37,
        "veilfall",
        "The Veilspeaker has reached a conclusion about why the fall is wrong, and the conclusion is "
        "that somebody is standing where nobody should stand.\n\nThe somebody is Ordek Fenn. On a "
        "Tuesday, a party of his shrinekeepers came up the shoulder and took the drying rack apart, piece "
        "by piece, without hurrying and without saying one word to him.",
        [boss("Veilspeaker Zul'Rath", zone=VF)],
        "I want you to understand what I am asking and that I have thought about it for four days.\n\nHe "
        "is on the south shore of the plunge, and he has decided my tarp is why his water is wrong, and "
        "he is not going to be talked out of it because I have tried. I went in. I went in on the "
        "Wednesday with a jar of oil as a gift and I came out again without saying a word, and the "
        "difference between us is that he is right about the shoulder being his and I am right about "
        "having nowhere else.\n\nGo down and end it. Please do not tell me it was quick.",
        "It was not quick. Thank you for not saying it was.\n\nI have his bracket. The one from the "
        "mouth, with the oil still in it. I am going to put it on my own rack and that will be the whole "
        "of the monument, because nobody is coming to make him one.\n\nAnd I am still going to have to "
        "decide about the camp. Killing the man did not move the shoulder."))
    return A


# =========================================================================================================
# MOSH'OGG SHELF - raised broken ground, mesas all round it, one road up, and a scout sitting on it who
# has been writing the same report since week two.
# =========================================================================================================
def shelf():
    A = []
    A.append(Q("stvc_garza_report", "What Watcher Garza Has Not Sent", GARZA, CS, 35, 36, "moshogg",
        "Watcher Garza was posted out of Grom'gol to sit on the one road up onto the Mosh'Ogg Shelf and "
        "report what comes down it. She has sent nine reports in eleven weeks.\n\nAll nine say the same "
        "thing, and the reason they say the same thing is that in the second week she put the "
        "spyglass - signed for, numbered, drawn against her name - down the notch, and everything since "
        "has been written from memory and a good imagination.",
        [k("Mosh'Ogg Rockthrower", 8), fetch("moshogg_midden_find", 5)],
        "The rockthrowers pick up anything that catches the light and they put it on the midden behind "
        "the camp, and I have been looking at that midden through nothing at all for nine "
        "weeks.\n\nEight of them, and bring me five things off the pile. Not the bones. The made things. "
        "If the glass is in there it is in there with a brass collar and my number stamped on the "
        "collar, and if it is not in there then I am going to have to write a tenth report that says "
        "something different from the other nine.",
        "Fifth one. There it is, brass collar, number and all, and I have had eleven weeks of being "
        "quietly sick about it.\n\nNow look what it was lying against. That is a crate nail. Square cut, "
        "stamped, Gurbashi arena stock - and arena stock does not come up this road, because this road "
        "goes nowhere but up.\n\nSo the ogres have been trading with the gate, and that is a real "
        "report, and the only way to file it is with the ten weeks attached. I asked you to tidy a "
        "midden and you have handed me a confession.", nxt="stvc_shelf_road"))

    A.append(Q("stvc_shelf_road", "One Road Up, and They Know It", GARZA, CS, 36, 37, "moshogg",
        "The Mosh'Ogg hold the shelf because the shelf has mesas on every side and exactly one notch "
        "through them, and they were the people standing nearest the notch when it mattered. That is the "
        "whole of their claim and they have never pretended otherwise.\n\nGarza's tenth report is going "
        "to be a bad one. She would like at least one number in it to be going the right way before she "
        "attaches the ten weeks to it.",
        [k("Mosh'Ogg Mauler", 10), k("Mosh'Ogg Spellgorger", 6), explore(CS, 164, 40, 8)],
        "This is not strategy and I am not going to dress it as strategy. It is bookkeeping.\n\nTen of "
        "the maulers off the approach and six of the spellgorgers out of the clearing on top, and then "
        "walk into the clearing itself so that somebody has actually stood in it this season. A post "
        "that reports a camp it has never entered is a post that is guessing, and I have done eleven "
        "weeks of guessing and would prefer to stop.",
        "They moved the camp. Six feet.\n\nSix feet, west, and then they stopped and put the fire back "
        "in the middle of it and sat down. That is not a rout. That is a shuffle, and it is the entire "
        "history of that rock in one gesture - they have been shuffling on it for generations and "
        "holding it the whole time, because nobody has ever wanted the notch badly enough.\n\nI have "
        "been watching a people shuffle for eleven weeks and calling it a garrison in writing."))
    return A


# =========================================================================================================
# THE SNAPJAW MARSH - standing brackish water in the south-west, and the only quest in the zone that is
# a favour rather than a job.
# =========================================================================================================
def marsh():
    A = []
    A.append(Q("stvc_ulua_netsetter", "A Week of Ulua's Nets", ULUA, CS, 34, 35, "snapjaw",
        "Netsetter Ulua has set nets in the Snapjaw Marsh her whole life and her mother set them before "
        "her, in the same water, off the same landing.\n\nShe does not want help. She wants somebody to "
        "pull her lines for one week, she is not going to say why, and her hands are shut most of the "
        "way into fists and have been since the cold month.",
        [gather("snapjaw_net_catch", 8), k("Snapjaw Crocolisk", 7)],
        "Eight lines, out past the gangplank where the water stops moving. Pull them, bring the catch "
        "in, and reset them the way you found them and not the way you think would be "
        "better.\n\nSeven of the crocolisks have been taking the nets with the catch still in them, "
        "which is the only part of this I will complain about out loud.\n\nAnd do not tell anyone in the "
        "Bay you did this. I sell into the Bay.",
        "Eight, and you reset them right, which I did not expect.\n\nSomething I will ask you and then "
        "we will not discuss it again. Where you're from - is there standing water? Brackish, slow, "
        "the kind that does not go anywhere?\n\nAnd does anyone fish it.\n\nI am not making "
        "conversation. I would like to know whether this is a trade that exists in more than one place, "
        "in case it stops existing in this one.", nxt="stvc_wager_slip"))

    A.append(Q("stvc_wager_slip", "Somebody Did Not Want To Be Found With This", "item:silt_set_wager_slip",
        CS, 35, 36, "arena",
        "You cut it out of a crocolisk's gut, which is not where paper goes.\n\nIt is a betting slip. "
        "Salt-stiff, gone brown at the folds, and still perfectly readable: a fighter's name, a round, "
        "and a price. You do not know the fighter. You do know that a price that good is a price "
        "somebody was offered because they knew something, and that there is exactly one reason to carry "
        "a slip like this out into standing water and stand in it.",
        [fetch("silt_set_wager_slip", 1), k("Snapjaw Crocolisk", 8), explore(CS, 70, 156, 7)],
        "The handwriting is small, fast and very legible, and there is a goblin up on the arena apron "
        "who writes exactly like that.\n\nTake it to her. Go back along the marsh track to the gangplank "
        "first and look at the water either side of it, and go through eight more of the crocolisks on "
        "the way, because whatever else is in that stretch of marsh is inside one of them.",
        "She knows the hand before she has the slip the right way up, because it is hers.\n\n'That card "
        "was pulled. That fighter never went on the sand - I wrote this, I priced it, and then the house "
        "scratched the round and I bought the paper back in. All of it. I counted it back in.'\n\nShe "
        "turns it over twice.\n\n'Where in the marsh. Exactly where. Because there is one reason to walk "
        "a dead slip out into water, and it is so that nobody ever finds you holding it.'",
        turn_in_npc_id=BEXXIL))
    return A


# =========================================================================================================
# THE GURBASHI ARENA - five bosses, five different kinds of fight, and a chain that is about the person
# who staked you rather than about the five.
# =========================================================================================================
def arena():
    A = []
    A.append(Q("stvc_arena_first_four", "Anticlockwise", ZULTAMO, GA, 36, 37, "arena",
        "Gatehouse Broker Zul'tamo's father kept this list and his grandfather cut part of the wall it "
        "is nailed to. He does not care who wins. He cares that the list is right.\n\nWhat he will give "
        "you before you go down is the one thing nobody in the Bay can sell you: how the place is built, "
        "and why it is built that way.",
        [boss("Vek'tar the Unbeaten"), boss("Grateward Mok'tal")],
        "You come down the stair at the top of the ring and you will see you can only go one way round "
        "it. People tell visitors that is tradition. It is masonry. The two faces that would let you "
        "choose were never cut, three generations back, because the mason did not want the order to be a "
        "choice.\n\nFirst is Vek'tar, and his round is the one the rim likes, because it ends in a "
        "number of minutes everybody can count. Go at him and keep going - under a third he will drink "
        "the fight back out of you.\n\nThen the grate. Mok'tal keeps a fire under that floor and it "
        "never lapses, and he closes off whatever you were going to use to answer it. Nobody has ever "
        "made a patient fight of Mok'tal and come up the stair.",
        "Two off the list.\n\nThe drum crew had you on the long count and they lost money on it, which I "
        "enjoyed more than a man in my position should.\n\nUnderstand what the count is. It is not "
        "music and it is not ceremony - it is the clock the rim prices a round against, and a crew that "
        "has drummed three generations of these fights can tell you to the beat how a fighter will "
        "open. They had you opening fast. You did not.\n\nI will tell them. They will not believe me, "
        "and they will put you back on the long count tomorrow, because being wrong once is cheaper "
        "than re-learning a rhythm.", nxt="stvc_arena_pair"))

    A.append(Q("stvc_arena_pair", "The Handler Is the Fight", ZULTAMO, GA, 37, 37, "arena",
        "The rim has noticed whose money is on you, which means the third station has been changed. The "
        "pair-handlers have put Jin'sha in with Rakjan, and they do that when the house wants a round to "
        "stop being predictable.\n\nZul'tamo tells you this flatly and without apology. It is not his "
        "decision and it is on his list, and both of those things are true at once.",
        [boss("Rakjan the Ribcracker"), boss("Zul'gar Hammerfall")],
        "Rakjan is loud and Rakjan is not the problem. The handler behind him is the problem, and if you "
        "spend the round on the big one you will die to the small one and the rim will say you fought "
        "the wrong man, which you will have.\n\nThen Zul'gar. Understand what he is before you go at "
        "him: he is not a fighter, he is a door. He stands in the mouth of the passage to the hall and "
        "there has been somebody standing in that mouth every day for three generations - the job has a "
        "name and the name is older than the family that holds it. Three swings, all of them enormous, "
        "and one of them takes your armour off you. Hitting him harder does not change that arithmetic.",
        "Four crossed off.\n\nNow a thing I should not tell you and am going to. The house does not open "
        "the centre gate more than once in a season. It has never had to. There is no rule about it - "
        "there has simply never been more than one in a season who got as far as the dead end.\n\nIt has "
        "opened twice this season. The first one was eleven days ago and nobody has said his name since, "
        "and I have begun to wonder whether the gate is a prize or a tidying-up.",
        nxt="stvc_arena_favourite", salt="e"))

    A.append(Q("stvc_arena_favourite", "The House's Own", BEXXIL, GA, 37, 38, "arena",
        "Four rounds have made Bexxil's stake worth a great deal more than she paid for it, and she has "
        "done what anybody holding paper that good does: she sold most of it on.\n\nWhat is left of her "
        "position is the awkward half. It pays if you go the distance with Jen'shala and lose honestly. "
        "It pays very little if you win. She has decided to tell you this to your face, which is not "
        "kindness and is not quite its opposite either.",
        [boss("Jen'shala, the House Favourite")],
        "Here it is, flat. I laid off four fifths of you this morning at a price your rounds made me, "
        "and the fifth I kept pays best on a long loss. Eleven minutes and down. That is my "
        "number.\n\nAnd I am telling you because I cannot buy eleven minutes off somebody who does not "
        "know I want them, and because you would have found out, and because I would rather be the one "
        "who said it.\n\nShe is one and four at once - she drinks the fight back out of you AND she "
        "takes your armour off, and she is the house's own, and the house has never put her on the sand "
        "to lose. Go down. Do what you are going to do. Collect in the Bay, not here.",
        "The Quiet Man counts it out without looking up, which is how you know it is the real number and "
        "not the one Bexxil would have preferred.\n\n'She is not ruined. She is annoyed, which on her is "
        "nearly the same shape.'\n\nHe squares the coin off with one finger.\n\n'The board has a field "
        "for where a fighter came from. It has had that field since before the Baron. Since you lot "
        "started walking down that stair it is the only line on the sheet anybody argues about, and "
        "somebody has to sit down tonight and re-price it, and it will be me.'\n\nHe "
        "finally looks up. 'Do not come back for a season. Let the number settle.'",
        requires_quests=["stvc_arena_pair"], turn_in_npc_id=QUIET))
    return A


# =========================================================================================================
# STANDALONES - the child's commission, and the nail nobody gave you.
# =========================================================================================================
def standalones():
    A = []
    A.append(Q("stvc_scrip_drums", "What Scrip Thinks the Drums Are", SCRIP, CS, 33, 34, "arena",
        "Scrip has never been a mile out of the cove. He has heard the arena drums come down the cape on "
        "a still night - twice, both times in the wet month - and he has built an entire theory out "
        "of it.\n\nThe drums are gorilla hide. One of them is bigger than a boat. He is completely "
        "certain and he is prepared to pay in the only currency he has, which is knowing which crates on "
        "the pier are not nailed down.",
        [k("Drumhide Gorilla", 8), gather("drumhide_hide_scrap", 5), explore(CS, 152, 112, 8)],
        "Right, so you go up the road and you count them. I want how many drums, how wide across the "
        "top, and what they are made of, and do not just say gorilla because I know it is gorilla, I "
        "want it written down by somebody who was there.\n\nEight of the big apes, the ones they call "
        "drumhides - that is a clue, that is practically the answer - and five bits of hide so I can "
        "feel it. And stand on the flat bit in front of the gate so you can tell me how many people "
        "fit.",
        "No.\n\nNo, you have looked at the wrong ones. Crocolisk. You are telling me the big drums are "
        "crocolisk belly off the marsh and the gorillas are the little ones round the edge, and that is "
        "- no.\n\nHe folds the hide scrap up small and puts it in his shirt anyway.\n\n'Was anyone down "
        "there from off-world? Like you? Because Hobb says the ones who came through always "
        "lose the first round, every time, "
        "and I said that can't be right, and he said ask someone who'd know.'\n\nHe is waiting. He is "
        "nine."))

    A.append(Q("stvc_crate_nail", "A Nail With a Number On It", "item:gurbashi_crate_nail", CS, 35, 36,
        "moshogg",
        "You turn it over. It is a crate nail - square cut, flat headed, the kind that goes into shipping "
        "timber and nothing else - and it is stamped with a run number.\n\nYou found it on the Mosh'Ogg "
        "Shelf, up a road that goes nowhere except up. Numbered nails come in runs. A run means a "
        "clerk, and a book, and a line in the book that says where the crate went.",
        [fetch("gurbashi_crate_nail", 1), k("Mosh'Ogg Brute", 8)],
        "There is only one man in this jungle who would recognise a run number on sight, and he is in "
        "Booty Bay behind a desk, and he will be unbearable about being asked.\n\nGo through the brutes "
        "on the way down off the shelf - eight of them hold the notch, and they are the ones with the "
        "nailed timber in their camp, which is the part you want to be sure of before you say any of "
        "this out loud to a clerk.",
        "Clerk Bexx looks at it for less time than it takes to say the number.\n\n'Mine. That run went "
        "out of this office, to the gate, under weight, signed. It should be at the bottom of a pit full "
        "of broken crates behind an arena.'\n\nHe puts it down very precisely on the manifest he was "
        "working on.\n\n'It is not. It is in an ogre midden on a shelf, which means somebody is opening "
        "my crates before the gate counts them. And do you know what I am angry about? The stamp. The "
        "stamp is legible. A legible stamp is a thing a person can audit me with, and I have spent "
        "eleven years making sure nobody could.'",
        turn_in_npc_id=BEXX))
    return A


# =========================================================================================================
# THE KNOT-CORD LINE - the one thread that leaves this jungle (2026-10-30, the 18 -> 30 pass).
#
# Kyle: "zones dont need to be isolated ... we can have a wide variety of quest types connecting the
# world", and he approved windriders out of the jungle up to Silverpine or Tarren Mill.  So this is the
# thread, and it is built on the one loose end the first eighteen deliberately left hanging:
# stvc_zuljana_font ends with Zul'jana refusing to carry the Font's readings to Overseer Mokra, because
# the honest reading is that the Veilfall is draining a country that was not there to drain and Mokra
# writes everything down.
#
# The answer is not another soldier.  It is somebody whose trade is writing down how high a river is and
# who reports to nobody - and there is no such person in Stranglethorn, which is the whole reason the
# thread has to leave.  Tarren Mill has two of them on a millrace, already written, already voiced
# (data/quests/hillsbrad.json: Pate has twenty-two years on the crank and would rather be the man who
# asked; Reed's family has milled the same water for sixty years).  The windrider line is the means:
# Pazzik flies the jungle leg, Ghulrak flies the valley leg, and the bundle goes up in a mail wrap.
#
# It goes OUT and it comes BACK.  The fourth station hands the verdict to Zul'jana in Grom'gol, because
# a thread that ends in another zone is a thread the player stops caring about.
# =========================================================================================================
def knot_cord_line():
    A = []
    A.append(Q("stvc_cord_sealed", "Not to the Overseer", ZULJANA, VF, 36, 37, "veilfall",
        "Zul'jana has the Font's readings and no intention of laying them on Overseer Mokra's table. "
        "Mokra writes everything down, and a thing written down in a garrison has to mean something by "
        "the end of the week.\n\nWhat the readings need is somebody whose whole trade is the height of "
        "water and who answers to nobody about it. There is no such person in this jungle. There is no "
        "such person in Grom'gol either, and she has checked.",
        [fetch("veilfall_tally_cord", 4), explore(VF, 58, 40, 7)],
        "Four more cords off the Font before I seal the bundle. Read this morning, not last month, so "
        "nobody can tell me afterward that my water is a season stale.\n\nThen go up to the lamp "
        "gallery above the plunge and stand on the terrace behind the brackets. There is a waterline on "
        "that stone, and there is a second one above it, and the gap between them is the only part of "
        "this you will be asked about by somebody who matters. Look at it with your own eyes. I am not "
        "sending an account of a thing you have not seen.",
        "Sealed, and my name is on the wrap, which I thought about for longer than I am going to "
        "admit.\n\nThere is a mill in a valley a long way north of here where one family has written "
        "down the height of the same water for sixty years, and a man on the sluice above it who has "
        "had his hand on one crank for twenty-two. Neither of them has a commander.\n\nThat is who gets "
        "this. I am going round my own camp, in writing, with my name on it, and I would rather do that "
        "than hand Mokra a sentence she will have to act on by Thursday.", nxt="stvc_north_leg"))

    A.append(Q("stvc_north_leg", "The Leg Nobody Flies", PAZZIK, CS, 36, 37, "windline",
        "Windrider-Keeper Pazzik has flown freight out of Grom'gol since the camp had one post and a "
        "rope, and the jungle leg used to cross the Veilfall basin because the basin gave his beasts a "
        "lift up out of the trees.\n\nIt does not any more. The fall came up three years ago, the air "
        "over it went cold and wrong, and now the north run goes the long way round and costs him a day "
        "he does not get paid for. The lip perches where his wyverns used to set down have gone to the "
        "bats out of the cave.",
        [k("Limewing Bat", 10, zone=VF), explore(CS, 30, 78, 7),
         deliver("zuljana_knot_bundle", "Put the wrap in Ghulrak's hands at Tarren Mill")],
        "Ten of the limewings, and take them in the cave where they sleep, not on the perch where they "
        "are awake and I have beasts on the ground.\n\nThen stand on the perch itself on the basin lip, "
        "and feel the air coming off that water, and understand why I will not put a wyvern down "
        "there.\n\nLast thing. This wrap goes up the line, and the line is me as far as the valley and "
        "Ghulrak after that. Only I am not flying the basin and Ghulrak is not coming south for one "
        "bundle, so the honest answer is that you are the middle of the line this week. Hand it to him "
        "yourself.",
        "Ghulrak turns the wrap over twice and holds it away from himself like something that has been "
        "in a river.\n\n'No cargo number. No weight. No seal but a troll's name written in her own "
        "hand.'\n\nHe puts it down on the rail anyway.\n\n'That is not freight. That is a favour, and I "
        "have been on this line long enough to know the difference and to do them anyway. Pate is up at "
        "the weir head. He has been waiting on somebody with more letters after their name than he has, "
        "and you are not that, but you are carrying water, and that will do.'",
        turn_in_npc_id=GHULRAK, nxt="stvc_sluice_book", requires_quests=["stvc_cord_sealed"],
        grant_items=carry("zuljana_knot_bundle", "Zul'jana's Knot-Cord Bundle",
                          "Five knotted cords, a folded sheet of readings and an oilcloth wrap, tied "
                          "with a sailor's knot somebody in Grom'gol clearly had to be taught. The "
                          "cords are still faintly damp.")))

    A.append(Q("stvc_sluice_book", "What Pate Keeps In the Other Book", PATE, TM, 37, 38, "windline",
        "Sluice-Keeper Pate raises and drops the gate on the Tarren Mill race, and when the gate goes "
        "down the wheel stops and the whole valley learns his name inside an hour. He has done it for "
        "twenty-two years and his predecessor's hand is in the front of the same book.\n\nHe has the "
        "jungle's cords on the bench in front of him, weighted flat with a spanner, and he has read them "
        "twice. What he has to say about them takes a while, and he would rather say it at the weir.",
        [talk("the_board_and_the_book", "what_the_knots_say", "the_other_book"),
         explore(TM, 40, 22, 7)],
        "Come up to the weir head and ask me whatever you came to ask. I will not do this across a "
        "doorway - I want the water making noise next to us while I say it, because a man can talk "
        "himself into anything in a quiet room.\n\nMind the boards on the walkway. Two of them are new "
        "and four of them are the ones I keep meaning to replace, and I have not yet managed to be the "
        "man who fell in while explaining his own sluice.",
        "There. Now you have had it from me standing next to the thing itself, which is the only way I "
        "trust anything I say.\n\nTake the cords down to Aldous Reed at the mill. He has sixty years of "
        "the same water in a ledger and a grandfather's hand before that, and he will do with these "
        "what I cannot: tell you whether a river has ever behaved this way before and come back "
        "down.\n\nI will say the one thing twice, since you are going to be repeating me. I am not "
        "calling your numbers wrong. I am saying I cannot check them, and I am a man who checks.",
        nxt="stvc_reed_verdict", requires_quests=["stvc_north_leg"]))

    A.append(Q("stvc_reed_verdict", "Sixty Years of the Same Water", REED, CS, 37, 38, "windline",
        "Aldous Reed's family has milled the Tarren Mill race for sixty years and written the height of "
        "it down every week of them, in three hands, in one ledger. He has laid the jungle's cords "
        "across his own columns and found the shape of them twice and not a third time.\n\nWhat he wants "
        "now is a mark set at the far end, cut properly, by somebody who is going back there. A "
        "measurement nobody can repeat is a story, and Reed does not keep stories in that book.",
        [deliver("reed_sluice_board", "Set the marked board in the stone above the fall"),
         explore(CS, 62, 46, 7), k("Spraywater Elemental", 8, zone=VF)],
        "This is a gauge board. Oak, numbered, cut by my father and used for a weir that silted up "
        "before you were born. Set it in the lip above your waterfall where the stone is sound, and set "
        "it where a short person can read it, because the next one who reads it will not be "
        "you.\n\nEight of the spray-things will come up out of the Font while you are working, because "
        "they are made of exactly the water you are trying to measure. That is a sentence I have had to "
        "say out loud to hear how it sounds.",
        "Zul'jana reads Reed's note twice and then puts her hand flat on it.\n\n'Sixty years and the "
        "same shape twice. Once in a melt year and once when a lake gave way upstream of him and "
        "drained in a fortnight.\n\n'And then the third line, which is mine now. The water has been up "
        "three years and has not come down, and the only way a river does that is if something new is "
        "feeding it, and he writes that he has started dating his own book from the change because the "
        "old dates stopped predicting anything.\n\n'He has turned your arrival into a unit of time. He "
        "does not mean it unkindly. It is just the honest way to keep a book now, and I am going to have "
        "to tell Mokra after all.'",
        turn_in_npc_id=ZULJANA, requires_quests=["stvc_sluice_book"],
        grant_items=carry("reed_sluice_board", "Reed's Gauge Board",
                          "A length of numbered oak, the figures cut rather than painted, worn pale "
                          "where sixty years of thumbs have found the same two numbers.")))
    return A


# =========================================================================================================
# THE 18 -> 30 PASS - the rest of it, hung on the loose ends the first eighteen left.
#
# Every one of these answers something an earlier quest asked and did not finish: Zul'jana's two words
# that mean the same thing, the centre gate that has opened twice in a season, the lamps nobody is
# trimming now the Veilspeaker is dead, Garza's tenth report, Ulua's hands, and a nine-year-old who was
# told no and has gone away and had a think about it.
# =========================================================================================================
def stonework():
    A = []
    A.append(Q("stvc_zultamo_courses", "What the Courses Are For", ZULTAMO, GA, 36, 37, "arena",
        "Zul'jana sent you to the gatehouse with a question she had carried her whole life without "
        "noticing: the Zul'Rath word for the Veilfall's water and the Gurbashi word for the arena's "
        "sand are the same word.\n\nGatehouse Broker Zul'tamo's grandfather cut part of the wall this "
        "list is nailed to. He is the third of his family to keep it, he has never been asked this, and "
        "he puts his pen down, which for him is a considerable event.",
        [talk("the_one_way", "the_uncut_faces", "the_word_for_sand"), explore(GA, 52, 26, 7)],
        "Come down the stair with me and we will do this standing in it, because half of what I am "
        "going to say is a thing you have to be looking at.\n\nStand at the foot of the stair first. "
        "Not on it - at the foot, on the sand, where the ring opens both ways in front of you and you "
        "will swear there is a choice.\n\nThen ask me, and I will answer the two of your three questions "
        "I can answer, and be honest with you about the third one.",
        "That is everything the gatehouse knows and I have just told you the end of it, which means "
        "there is now one more person in the world who knows it than there was this morning.\n\nThe "
        "rest is south, under the sea, in a hall my family stopped going to before my grandfather's "
        "time. I have not been. I am sixty-one and I run a gate.\n\nIf you go and you come back, come "
        "back here first. Not for the list. I would like to hear it from somebody who stood in it.",
        requires_quests=["stvc_zuljana_names"]))

    A.append(Q("stvc_centre_gate", "The Line With No Name In It", ZULTAMO, GA, 37, 38, "arena",
        "The house opened the centre gate twice this season. The first one went through eleven days "
        "before you did, and the gatehouse has his kit back - signed in, hung on a peg, counted - and "
        "nothing to write on the line it belongs to.\n\nZul'tamo keeps the list because the list is the "
        "only thing the Gurbashi have never let rot. A line with a kit and no name on it is the first "
        "hole in it in three generations, and he will not leave it open.",
        [k("Gurbashi Gatekeeper", 9), explore(GA, 76, 56, 6),
         deliver("centre_gate_kitbag", "Hang the kitbag back on the gatehouse peg")],
        "Take his bag down to the dead end and walk the gate mouth with it. Nine of the gatekeepers hold "
        "that stretch and they will stop you, because stopping people in that mouth is the whole of "
        "the post and it is older than my family.\n\nI want you to stand where he stood and then bring "
        "the bag back up and hang it where it was. I am not asking you to find anything out. I have "
        "asked, and the answer is that the rim does not remember a name because the board never had "
        "one to print - he came through from somewhere else, there was nothing to put in the column, "
        "and so the column went out blank.",
        "On the peg. Good.\n\nHere is the entry I am going to write, and you are going to hear it "
        "because you are the only person who will ever have stood in that mouth twice.\n\nA fighter of "
        "no recorded house, passed the ring, entered the hall, did not come out. That is all of "
        "it.\n\nA man came through from another world, walked down a stair nobody built for him, won "
        "four rounds that nobody wrote down properly, and the honest entry is eleven words long. I have "
        "kept this list my whole life and I did not know until this week that it was possible to be in "
        "it and not be in it.",
        requires_quests=["stvc_arena_favourite"],
        grant_items=carry("centre_gate_kitbag", "A Signed-In Kitbag",
                          "Canvas, buckled, counted in and tagged by the gate crew in a hand that has "
                          "tagged thousands. Where the owner's house should be written there is a line "
                          "and then nothing.")))

    A.append(Q("stvc_drum_callers", "The Count Is the Clock", BEXXIL, CS, 34, 35, "arena",
        "The drums are not music. The drums are the arena's clock: the rim prices a round in minutes, "
        "and the minutes are whatever the drum crew says they are.\n\nTout Bexxil has three afternoons "
        "of rounds that ran long by exactly the same amount, which is not how long is supposed to work, "
        "and she has worked out what a drum-caller is being paid in. Not coin. Paper.",
        [k("Gurbashi Drum-Caller", 9), fetch("undersized_stock_tally", 3)],
        "Nine of the callers, out on the drum line east of the gate apron, and do it where the rim can "
        "see which of them you are doing it to.\n\nThen three of the stock tallies, and you will have "
        "to go back to the crates for those because that is where the paper comes from. Signed-in "
        "weight is as good as coin down here and better than coin, because coin has to be counted by "
        "somebody and a tally only has to be waved.\n\nIf I am wrong about this I have just had nine "
        "musicians killed over a rounding error, so bring the paper.",
        "Same hand on all three. Same hand as the drovers' book, which means the stock fraud and the "
        "slow count are one scheme with two ends, and I have been pricing them as two different kinds "
        "of bad luck for a season.\n\nI am not taking this to the house. The house takes a cut of both "
        "ends.\n\nI am going to go on pricing it, now that I know which way it leans. That is not "
        "honest and I am not going to pretend it is. It is just what a woman does with information she "
        "paid for.",
        requires_quests=["stvc_tout_entry"], salt="b"))
    return A


def basin_more():
    A = []
    A.append(Q("stvc_limeback_lamps", "Who Trims Them Now", ORDEK, VF, 36, 37, "veilfall",
        "The sheet of the Veilfall went dark four nights after the Veilspeaker died, and Ordek Fenn has "
        "sat on his camp stool and watched it be dark.\n\nHe spent two years telling himself there was "
        "nobody behind the water. Now there is nobody behind the water, and he has worked out that the "
        "difference between those two sentences is the whole of what he has done to this place.",
        [k("Veilfall Limeback", 9, zone=VF), gather("veilfall_spray_moss", 6), explore(VF, 40, 70, 7)],
        "The limebacks have come up off the lowest terrace now that there is nobody keeping them down "
        "there. Nine of them, before they find the ramp. They are not the shrinekeepers and they will "
        "not stop at the lip.\n\nSix more handfuls of the spray moss while you are on the band - I am "
        "not going to pretend I have stopped selling it.\n\nAnd go down to the lowest terrace. The oil "
        "is in a jar under the bracket, if nobody has knocked it over. I know where the jar is because "
        "he told me, on the Wednesday, when I went in with a gift and came out without saying a word.",
        "Lit. You lit them.\n\nI did not ask you to light them. I asked you to go down and look, and "
        "you have gone down and done a dead man's evening chore, and now the water glows again and "
        "every trader on the north road will go on believing it is the moonlight.\n\nI am going to keep "
        "trimming them. That is the decision I have made while you were down there. Not as penance - I "
        "have no faith in his water and he knew it. Because a lamp that somebody has kept lit for "
        "generations should not go out over a tarp and a shoulder of dry rock.",
        requires_quests=["stvc_veilspeaker"], salt="d"))

    A.append(Q("stvc_ulua_cold_month", "The Water Is Going Sweet", ULUA, CS, 35, 36, "snapjaw",
        "Netsetter Ulua's marsh is brackish. That is not an opinion about it; that is what the trade "
        "is. Her nets, her mother's nets and her mother's mother's are all cut for fish that live where "
        "the salt and the river argue.\n\nThe argument is being won. Something has been pushing fresh "
        "water down into the standing marsh for about three years, and the catch has begun to come up "
        "wrong, and she has worked out roughly when it started and has decided not to say so out loud.",
        [gather("snapjaw_net_catch", 9), k("Snapjaw Leechswarm", 7), explore(CS, 34, 168, 7)],
        "Nine lines this time, and not the near ones. The far set, down where the marsh stops being "
        "mine and starts being whatever it is going to be.\n\nSeven of the leechswarms out of the slack "
        "water first or you will lose fingers you have plans for.\n\nThen walk to the end of it. Past "
        "the last stake, where the reeds change over from the grey kind to the green kind. I have known "
        "that line my whole life and it has moved, and I would like somebody else to have stood on it "
        "so that it is not just me saying so.",
        "Green reed in eight of the nine. My mother would have thrown the whole set back.\n\nSo. The "
        "line has moved, and you have stood on it, and now two of us know.\n\nHere is what I am going "
        "to do about it, and I want you to hear it from me rather than from the Bay in a season. I am "
        "going to go on setting nets in it until it stops paying, and then I am going to be a woman of "
        "sixty with one trade and a marsh that does not have it any more.\n\nMy hands were going to "
        "decide that for me anyway. The water has only got there first.",
        requires_quests=["stvc_ulua_netsetter"], salt="f"))
    return A


def road_more():
    A = []
    A.append(Q("stvc_ganger_milepost", "Paid By the Furlong", DUBO, CS, 33, 34, "vineroad",
        "Road-Ganger Dubo's gang is paid by the furlong, and a furlong is whatever the mileposts say it "
        "is. The stones go in at the kerb line, cut faces north, and they have been in since his "
        "father's gang.\n\nThree of them are in the wrong place. Not fallen - moved, reset, packed in "
        "neatly with the cut faces turned, by somebody who knew exactly what the stones are for and "
        "exactly who gets paid off them.",
        [k("Bloodvine Raptor", 12), gather("vine_road_cut_vine", 5), explore(CS, 100, 120, 8)],
        "Twelve of the raptors off the south stretch. They have come down onto the road since the ford "
        "work and they go for a man who is kneeling, which is the whole of this job - kneeling.\n\nFive "
        "good lengths out of the kerb line while you are down there, same as before.\n\nAnd stand at "
        "the long milepost where the road bends south of the fork, and look at which way the cut face "
        "is pointing. North is the camp. I have never in my life seen one of those stones turned, and I "
        "have been looking at them since I was tall enough to read one.",
        "Turned south. All three turned south, and packed in with new gravel, which means a tool and a "
        "day and somebody's afternoon.\n\nSouth is the Bay. A stone turned south is a stretch of road "
        "the Bay is paying for and the Gurbashi are not, and somebody has quietly made my gang the "
        "Bay's gang for a mile and a half without mentioning it to me.\n\nI am not going to move them "
        "back. I am going to find out who gets the invoice first, because if it is me I would like to "
        "be the one asking the question rather than the one answering it.", salt="g"))

    A.append(Q("stvc_notch_tithe", "What Came Up the Road", GARZA, CS, 36, 37, "moshogg",
        "Watcher Garza's tenth report has the crate nail in it, and the crate nail says the Mosh'Ogg "
        "and the arena gate have been trading up a road that goes nowhere but up.\n\nA report like that "
        "goes to a tribunal, and a tribunal does not want a nail. It wants the goods on the midden, the "
        "drovers who signed the weight at the other end, and a witness who can be stood up and asked "
        "questions. She has been working out what she has got, and the arithmetic has not been "
        "comfortable.",
        [fetch("moshogg_midden_find", 4), k("Gurbashi Beast-Drover", 8)],
        "Four more made things off the midden - the stamped ones, not the bones, same as last time. And "
        "eight of the drovers at the crate line, because the trade has an end down there and I would "
        "like the end down there to be short of hands when somebody finally reads my paper.\n\nI will "
        "put it plainly, because you will work it out on the walk and I would rather you heard it from "
        "me. I cannot put you in the report as the witness. A tribunal wants a name with a village "
        "behind it and a commander who will stand up for it, and you have the first of those. You are "
        "going to be the unnamed party who recovered the items. That is not what I think of you. It is "
        "what the form has room for.",
        "Four stamped, one of them twice, and a drover line that is going to be thin for a week. Good.\n\n"
        "Here is the report, and you are in it, and you are in it as the unnamed party, and I have "
        "signed under it that the items came to me in the condition described.\n\nThat sentence is me "
        "staking my own post on your word. It is the largest thing I have got and it is a line of small "
        "handwriting on the third page.\n\nEleven weeks ago I would not have written it. Sitting on one "
        "road teaches you who actually comes up it.",
        requires_quests=["stvc_garza_report"], salt="h"))
    return A


def bay_more():
    A = []
    A.append(Q("stvc_scrip_second", "Scrip Has Had a Think", SCRIP, CS, 33, 34, "arena",
        "Scrip was told the big arena drums are crocolisk belly and the gorillas are the little ones "
        "round the rim. He did not take it well.\n\nHe has had four days to consider it, and he has not "
        "come round, and he has not dropped it either. What he has done is work out what would settle "
        "it, which is more than most people in the Bay manage about anything.",
        [talk("the_crocolisk_theory", "who_told_you_that", "what_he_would_do"),
         k("Snapjaw Crocolisk", 9)],
        "Right. I've got questions and I've written them on my hand, so don't go anywhere.\n\nAnd I "
        "need nine of the marsh crocs done. Not for the hide - for how big the biggest one is. If the "
        "biggest croc in that marsh isn't as wide across the belly as a drum is across the top, then "
        "it can't be croc, can it, and then I'm right and Hobb's wrong and you're wrong too but mostly "
        "Hobb.\n\nThat's called a test. Bexx told me about tests. He said most people don't do one "
        "because they'd rather be right.",
        "...fine.\n\nFine. It's croc. It's croc and I've had it wrong for two years and I told six "
        "people.\n\nHe sits down on the crate he is not supposed to sit on.\n\n'Here's what I don't get "
        "though. Everyone down here knows what the drums are made of. Nobody ever said. Not the "
        "harbourmaster, not Bexx, not one sailor. They all just let me say gorilla for two years.'\n\nHe "
        "looks up.\n\n'Was it funny? Is that it? Because I'd have told me.'",
        requires_quests=["stvc_scrip_drums"], salt="i"))
    return A


# =========================================================================================================
# DROPS
# =========================================================================================================
#: fetch/gather sources. Spread across two or three creatures each wherever the fiction allows it, so a
#: player who is working one corner of a subzone is not locked to a single spawn.
FETCH_DROPS = {
    "Bloodvine Raptor": [("vine_road_cut_vine", "Kerb-Line Bloodvine",
                          "Cut out of the kerb stone the camber depends on. Nine days and it is back.",
                          0.44)],
    "Greenwater Adder": [("vine_road_cut_vine", "Kerb-Line Bloodvine",
                          "Pulled out of a drain the adders had no business nesting in.", 0.48)],
    "Gurbashi Beast-Drover": [("undersized_stock_tally", "Drover's Stock Tally",
                               "Signed in at weight. The weight is not the weight.", 0.46)],
    "Snapjaw Leechswarm": [("veilfall_spray_moss", "Spray-Band Moss",
                            "It only grows where the fall reaches, which is a smaller fact than it "
                            "sounds and a more expensive one.", 0.42),
                           ("snapjaw_net_catch", "Net Line Catch",
                            "Pulled in off a line and reset the way it was found.", 0.30)],
    "Nightpelt Panther": [("veilfall_spray_moss", "Spray-Band Moss",
                           "Taken off the lip at dusk, which is when the lip belongs to something else.",
                           0.40)],
    "Zul'Rath Mistcaller": [("zulrath_name_stone", "Terrace Name Stone",
                             "Set into the lip of a terrace. One of the four names, and not the one you "
                             "were given.", 0.46),
                            ("veilfall_tally_cord", "Veilfall Tally Cord",
                             "Knotted once a morning and read against yesterday's.", 0.34)],
    "Zul'Rath Shrinekeeper": [("zulrath_name_stone", "Terrace Name Stone",
                               "Carried by whoever is senior on a terrace, because the name is the post.",
                               0.42)],
    "Spraywater Elemental": [("veilfall_tally_cord", "Veilfall Tally Cord",
                              "Wet through, and the knots have not slipped in three years of it.", 0.48)],
    "Mosh'Ogg Rockthrower": [("moshogg_midden_find", "Midden Find",
                              "A made thing, off a pile of mostly unmade ones.", 0.46)],
    "Mosh'Ogg Brute": [("moshogg_midden_find", "Midden Find",
                        "They pick up whatever catches the light and they do not look at it twice.",
                        0.40)],
    "Snapjaw Crocolisk": [("snapjaw_net_catch", "Net Line Catch",
                           "Taken back off the one that took it.", 0.50)],
    "Drumhide Gorilla": [("drumhide_hide_scrap", "Drumhide Scrap",
                          "Thick, grey and faintly dusty. It is not what the big drums are made of.",
                          0.48)],
}

#: ADDITIONAL sources for two items the 18 -> 30 pass leans on in corners the original source creature
#: does not stand in. Staged, not merged - see main(). Neither row is anybody's only source.
EXTRA_DROPS = {
    # stvc_drum_callers' whole point is that the drum crew are being PAID in signed-in stock tallies,
    # so a caller carrying one is the quest's thesis rather than a convenience.
    "Gurbashi Drum-Caller": [("undersized_stock_tally", "Drover's Stock Tally",
                              "Taken off a drummer, which is the part that should worry somebody.",
                              0.40)],
    # The bats roost in the Font and go through anything hanging in it. The cords hang in it.
    "Limewing Bat": [("veilfall_tally_cord", "Veilfall Tally Cord",
                      "Chewed at one end. The knots are intact, which is the only part that matters.",
                      0.34)],
}

#: Quest-STARTER drops. The engine only rolls these while the quest is unstarted, unlocked and the item
#: unheld, so there are no dead stacks in a bag.
STARTER_DROPS = {
    "Mosh'Ogg Rockthrower": [("gurbashi_crate_nail", "Stamped Crate Nail",
                              "Square cut, flat headed, shipping timber only - and a run number struck "
                              "into the head clean enough to read in bad light.",
                              0.15, "stvc_crate_nail")],
    "Snapjaw Crocolisk": [("silt_set_wager_slip", "Silt-Set Wager Slip",
                           "Salt-stiff and brown at the folds. A name, a round and a price, and the "
                           "price is far too good.",
                           0.16, "stvc_wager_slip")],
}


# =========================================================================================================
# AUDIT - the build fails rather than shipping a lopsided reward spread.
# =========================================================================================================
#: Share ceilings. tirisfal_gear.specs draws its armour classes from r.sample(..., 4) seeded off the
#: quest id, which is even ON AVERAGE and not necessarily even across eighteen draws - the Aspen pass
#: shipped a melee dump before anybody was checking. These are the bars; `salt` on Q is the lever.
MAX_ARMOUR_SHARE = 0.34
MAX_WEAPON_SHARE = 0.42
MIN_CASTER_WEAPON_SHARE = 0.20

CASTER_WEAPONS = {"wand", "staff", "tome", "libram", "idol", "totem"}


def audit(quests):
    errs = []
    armour, weapons, acc = {}, {}, 0
    for q in quests:
        for it in q["unique_item_defs"]:
            a, w = it.get("armor_type"), it.get("weapon_type")
            if a:
                armour[a] = armour.get(a, 0) + 1
            elif w:
                weapons[w] = weapons.get(w, 0) + 1
            else:
                acc += 1

    for k_, label, table, cap in (("armour", "armour class", armour, MAX_ARMOUR_SHARE),
                                  ("weapon", "weapon family", weapons, MAX_WEAPON_SHARE)):
        tot = sum(table.values())
        for name, n in sorted(table.items()):
            if tot and n / tot > cap:
                errs.append(f"{label} {name!r} is {n}/{tot} ({n / tot:.0%}) of the {k_} rewards, "
                            f"over the {cap:.0%} ceiling")
    for cls in ("cloth", "leather", "mail", "plate"):
        if not armour.get(cls):
            errs.append(f"no {cls} reward anywhere in the pass")

    wtot = sum(weapons.values())
    caster = sum(n for w, n in weapons.items() if w in CASTER_WEAPONS)
    if wtot and caster / wtot < MIN_CASTER_WEAPON_SHARE:
        errs.append(f"only {caster}/{wtot} ({caster / max(wtot, 1):.0%}) of the weapon rewards arm a "
                    f"caster, under the {MIN_CASTER_WEAPON_SHARE:.0%} floor")

    # Standing rules that are cheap to check here and expensive to find in play.
    for q in quests:
        for it in q["unique_item_defs"]:
            for stat in list(it.get("primary_stats", {})) + list(it.get("secondary_stats", {})):
                if "resist" in str(stat).lower():
                    errs.append(f"{q['quest_id']}: {it['name']!r} carries {stat!r} - no "
                                f"magic-resistance gear below level 45")
            if it.get("category") in ("material", "reagent", "trade_good"):
                errs.append(f"{q['quest_id']}: {it['name']!r} is a crafting material")
        if any(o["type"] not in {"kill", "kill_boss", "fetch", "gather", "deliver", "explore", "craft",
                                 "story", "dialogue"} for o in q["objectives"]):
            errs.append(f"{q['quest_id']}: unexpected objective type")

    ids = {q["quest_id"] for q in quests}
    for q in quests:
        nxt = q.get("next_quest_id")
        if nxt and nxt not in ids:
            errs.append(f"{q['quest_id']}: next_quest_id {nxt!r} is not in this pass")
        for r in q.get("requires_quests", []):
            if r not in ids:
                errs.append(f"{q['quest_id']}: requires_quests {r!r} is not in this pass")
    # no chain loops
    nexts = {q["quest_id"]: q.get("next_quest_id") for q in quests}
    for start in nexts:
        seen, cur = set(), start
        while cur:
            if cur in seen:
                errs.append(f"chain loop through {start!r}")
                break
            seen.add(cur)
            cur = nexts.get(cur)

    if errs:
        for e in errs:
            print("  AUDIT FAIL:", e)
        raise SystemExit(f"audit failed ({len(errs)})")

    print(f"  audit ok: {sum(armour.values())} armour "
          f"({', '.join(f'{k_} {v}' for k_, v in sorted(armour.items()))}), "
          f"{sum(weapons.values())} weapons "
          f"({', '.join(f'{k_} {v}' for k_, v in sorted(weapons.items()))}), "
          f"{acc} accessories")


def main():
    quests = (vine_road() + basin() + cave() + shelf() + marsh() + arena() + standalones()
              + knot_cord_line() + stonework() + basin_more() + road_more() + bay_more())
    audit(quests)

    OUT.write_text(json.dumps(
        {"_notes": "Central Stranglethorn / Veilfall Cave / Gurbashi Arena quest pass (2026-10-30). "
                   "Generated by tools/build_stranglethorn_central_quests.py - do not hand-edit text "
                   "here; the overlay in data/quests/text/stranglethorn_central.json wins and its "
                   "source is tools/quest_text_src/stranglethorn_central.txt.",
         "quests": quests}, indent=2, ensure_ascii=False) + "\n")

    # DROPS GO TO STAGING NOW, NOT TO THE SHARED TABLE.
    #
    # FETCH_DROPS and STARTER_DROPS above were merged into data/creatures/quest_drops.json by the first
    # eighteen and are live in it. Three agents are expanding Stranglethorn at once and three
    # read-modify-writes of one json is how a creature's row silently loses an item, so this pass does
    # not touch that file at all: the only NEW rows are EXTRA_DROPS, they go to a staging file, and Kyle
    # merges the three staging files himself.
    #
    # Which is also why the twelve new quests ask for NO new quest item. Every fetch and gather they
    # name is one of the thirteen item ids that is already in the shared table with a source creature,
    # so none of them is waiting on that merge to be finishable - tools/audit_quests.py resolves all of
    # them today. EXTRA_DROPS only widens where two of those items can be found, which is a quality
    # improvement and nothing's blocker. Same reason there are no new item-starter quests in this pass:
    # a starter drop cannot be staged and have the quest be startable.
    sp = ROOT / "tools/staging_drops_stranglethorn_central.json"
    staged = {}
    for cre, rows in EXTRA_DROPS.items():
        staged[cre] = [{"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch} for (iid, nm, desc, ch) in rows]
    sp.write_text(json.dumps(
        {"_notes": "STAGING, not loaded by the game. New Central Stranglethorn drop rows for the "
                   "18 -> 30 pass (2026-10-30), to be merged into data/creatures/quest_drops.json "
                   "under its 'drops' key by whoever merges the three Stranglethorn staging files. "
                   "Merge by (creature, item_id): replace a row with the same item_id, keep the rest. "
                   "Nothing in this file blocks a quest - every item here already has a source "
                   "creature in the live table; these are additional sources in the subzones the new "
                   "quests work in.",
         "drops": staged}, indent=2, ensure_ascii=False) + "\n")

    chains = sum(1 for q in quests if q.get("next_quest_id"))
    starters = sum(1 for q in quests if str(q["giver_npc_id"]).startswith("item:"))
    hist = {}
    for q in quests:
        for o in q["objectives"]:
            hist[o["type"]] = hist.get(o["type"], 0) + 1
    print(f"Central Stranglethorn quests: {len(quests)} total, {chains} chained links, "
          f"{starters} item-starters, {sum(len(v) for v in FETCH_DROPS.values())} live fetch sources, "
          f"{sum(len(v) for v in STARTER_DROPS.values())} live starter drops, "
          f"{sum(len(v) for v in EXTRA_DROPS.values())} staged rows")
    print("  objectives: " + ", ".join(f"{k_} {v}" for k_, v in sorted(hist.items(), key=lambda kv: -kv[1])))
    print("  zones touched: " + ", ".join(sorted({q["zone"] for q in quests})))


if __name__ == "__main__":
    main()
