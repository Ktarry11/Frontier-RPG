#!/usr/bin/env python3
"""
The Shimmering Flats + Saltwheel + the Undercrust quest pass. Idempotent.

    PYTHONPATH=. python3 tools/build_shimmering_flats_quests.py
    PYTHONPATH=. python3 tools/audit_quests.py
    PYTHONPATH=. python3 tools/audit_quest_rewards.py
    PYTHONPATH=. python3 tools/qa_quest_lore.py --zone shimmering_flats --show

THIRTY quests across 35-40. Six threads and seven standalones, all given in Saltwheel except the two
item-starters and the far end of the salt line, which is given in Freewind Post.

=========================================================================================================
WHAT THIS ZONE IS ABOUT, BECAUSE EVERY QUEST IN IT IS ABOUT THE SAME THING FROM A DIFFERENT ANGLE
=========================================================================================================
A goblin town on the start line of a racetrack that does not run, on a salt pan that is being eaten by
a hive that is closer every season, and NOBODY IS LEAVING. Every one of them has a reason, every reason
is true, and not one of them is a reason. That is the zone, and the quests are thirty people explaining
it to you in thirty different tones of voice.

So the threads are not "kill the thing, then kill the bigger thing". They are:

  THE OPEN          Tozzik still posts the times for a race nobody enters, because somebody has to hold
                    the date or the date goes away. The chain is him running it one more time. It ends
                    with a flag, one entrant and a time that is worse than the record - and he writes
                    it down and posts it, which is either the saddest or the most defiant thing in the
                    zone depending on how you read him. It is meant to be both.
  THE DUSTWHEEL     The goblins who stayed out on the track when the money went. Saltwheel will not
                    call them bandits because half of them are somebody's cousin, and the chain's whole
                    movement is the town deciding what word to use. It resolves in a LEDGER, not a
                    fight: Winnow writes them in as customers.
  THE MOUNDS        Brak Kesh counts hives from the east fence and says the number in the inn every
                    evening until they start buying him drinks so he says it quieter. Escalates
                    outward and ends under the ground.
  THE SALT LINE     The one trade that still works, and the chain that LEAVES THE ZONE. It was already
                    seeded: Freewind Post's spice-trader says "Salt from the flats, east of here. It is
                    the one trade the Integration did not touch." She is buying from Jixa Brinecount.
                    This thread is the two of them, two zones apart, finally in the same conversation.
  THE WATER         The Linken's-Sword gate. See below.
  THE INN           Four quiet ones about a building with beds in it and no way out of town.

=========================================================================================================
THE GOBLINS BLAME YOU, AND THEY ARE NOT ENTIRELY WRONG
=========================================================================================================
Kyle, 2026-10-30: *"Make the goblins blame 'players' a bit that the integration changed everything and
It's ruining profits etc"*.

That is the right instinct for goblins specifically, because a goblin's grievance is never abstract -
it is ARITHMETIC. These people do not resent the newcomers for philosophical reasons. They resent them
because the ledger has a line in it that used to be bigger, and the newcomers arrived the same season
it stopped being bigger, and a goblin who can do the sum will do the sum out loud at you.

Nine of the thirty carry it (the guide's ~30%), and the register is DIFFERENT EVERY TIME, because a
zone where every mention is resentment is as flat as one with none:

  MOZZ          openly bitter. Fuel for two hundred racers and six customers, and he has worked out
                who to blame and will tell you, and the number he quotes is real.
  GREBBIT       passive-aggressive pricing. Charges you more, explains why in terms of cartage, and
                both of you know that is not the whole reason.
  WINNOW        pure flat arithmetic, no feeling attached. The town is shrinking by a measurable
                amount and she can tell you the amount. That is the most damning one in the zone and
                she does not editorialise once.
  OYLA          CURIOUS, not angry - she took an Earth machine apart, understands it now, and says so
                is worse. She is the only one who has actually learned something.
  DRAL          grievance as inventory. Eight seasons of raceday stock for a crowd that never came.
  TOZZIK        refuses to blame anybody, which in context reads as a man holding a line.
  FENK          cheerfully mercenary about it - sells you the gear to walk out and mentions there is
                no bird, twice, because he profits from the walk.
  JIXA          THE COUNTER-EXAMPLE, and the zone needs one. Her trade is the one the Integration did
                not touch and she is warm about the whole business, which makes the other eight land
                harder than another resentful goblin would have.
  NAZZIK        holds a course record nobody can take because nobody drives the course, and he knows
                it, and he says so before you can.

Nothing from Earth appears as an object anywhere in this file. It is all in what people say.

=========================================================================================================
THE WATER: A LINKEN'S-SWORD GATE THAT WAS ALREADY IN THE GAME
=========================================================================================================
Kyle asked for multi-zone prerequisite chains - "skip A in Durotar or B in Silverpine and C never opens
in another zone". The gate here was not invented for the purpose; it was sitting in two finished zones
waiting for somebody to notice:

    asp_higher_every_spring    The Aspen Wilderness, 29-30.  "Higher Every Spring."  The melt is
                               bigger every year and the benches are flooding.
    fw_where_the_water_goes    Southern Thousand Needles, 33-34.  "Where the Water Goes."  Somebody
                               asks the obvious question about all that water and gets no answer.

THE ANSWER IS THIS ZONE. It came down the range, crossed the mesas, reached the pan - and the pan is
drier than it was, which is the part that does not add up, and which is why the hives are where they
are. swf_water_answer is gated on BOTH and on nothing else. A player who skipped either one never sees
it offered, exactly as asked, and the two prerequisites are in different zones by different authors
three and four levels below this one.

=========================================================================================================
RULES OBSERVED
=========================================================================================================
NO ESCORTS. Not one, not an escort-shaped objective, not the word.
NO QUESTS BUILT AROUND RARES. Scourbite, Gearjaw, Rustcoat, Hollowcrust and Paneater are the zone's
five named rares and NONE is an objective anywhere in this file. The Hollow Queen, Saltback and Riftjaw
are PINNED Undercrust bosses (boss_positions), not rares, so kill_boss on those is legitimate - the same
distinction the Stranglethorn pass drew for the arena.
NO MAGIC RESISTANCE (that is 45+) and NO HIGH-TIER MATERIAL (that is 60). The band tops out at 40.
NO STAT NUMBERS IN PROSE, and every count a person says out loud agrees with its objective -
tools/audit_quests.py prose_count_mismatches checks the second one.
SEVEN OBJECTIVE TYPES, not four: kill, kill_boss, fetch, gather, deliver, explore and dialogue all
appear. The dialogue topics live in world/quest_dialogue_shimmering_flats.py.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/shimmering_flats.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

SF = "the_shimmering_flats"
SW = "saltwheel"
UC = "the_undercrust"
FW = "freewind_post"

XP = {35: 2440, 36: 2520, 37: 2600, 38: 2680, 39: 2760, 40: 2840}
GOLD = {35: 9900, 36: 10200, 37: 10500, 38: 10800, 39: 11100, 40: 11400}

# ---------------------------------------------------------------------------------------------------
# GEAR FLAVOUR. Six themes, one per thread. What the loot is made of here is salt, track, chitin,
# boiler plate and cartage - nothing that came from Earth, because the standing rule is that Earth
# turns up in dialogue and never as an object on the pan.
# ---------------------------------------------------------------------------------------------------
tirisfal_gear.THEMES.update({
    "raceday": (["Raceday", "Flagfall", "Scrutineer's", "Start-Line", "Course-Record"],
                ["Laid in the season before the track died, and never once worn.",
                 "Pit kit. Built for a sport that stopped and never adapted to anything else.",
                 "Somebody stitched a lap count into the lining and then stopped counting.",
                 "Smells of hot oil, which on this pan it has no business doing any more."]),
    "dustwheel": (["Dustwheel", "Salvage-Rights", "Stripped", "Axle-Found", "Off-Course"],
                  ["Came off the track the day it stopped moving, which makes it salvage.",
                   "Repaired four times by four different hands and none of them matched.",
                   "Track grit worked so far into the weave it is part of the weave now.",
                   "Claimed under a rule that is written down and that nobody enforces."]),
    "hive": (["Mound-Watcher's", "Carapace", "Crust-Breaker's", "Chitin-Set", "Fence-Line"],
             ["Resin set hard in the seams and went on setting for a year after.",
              "Shell plate, cut down and strapped to something it was never grown for.",
              "It smells faintly of the inside of a hive and washing does not help.",
              "Taken off the fence line where the counting gets done."]),
    "saltline": (["Brinecount's", "Pan-Graded", "Cartage", "Salt-Sealed", "Long-Haul"],
                 ["Salt has been through this so many times it has stopped doing damage.",
                  "Haulage kit, and it has done the crossing more often than anyone riding in it.",
                  "Lead-sealed at the seams, which is what you do out here and why.",
                  "Graded, weighed, and written down twice before it was ever worn."]),
    "water": (["Dry-Pan", "Watermark", "Three-Range", "Seep-Line", "Lower-Every-Year"],
              ["The stain on it is a waterline, and the waterline is in the wrong place.",
               "Carried down off a mountain, across the mesas and out onto the pan.",
               "Whatever soaked this has not been anywhere near it in a long time.",
               "Salt-stiff in a pattern that says it dried slowly and only once."]),
    "inn": (["Rimehand's", "Hearth-Bound", "Bedded-Down", "Last-Bed", "Walk-Out"],
            ["Washed in water that was hauled across a pan to wash it.",
             "Inn kit. Mended in the evenings by somebody with better things to do.",
             "It has been slept in by people on their way somewhere, and by people who stopped.",
             "The salt gets into this every night and gets beaten out of it every morning."]),
})


# ---------------------------------------------------------------------------------------------------
# objective helpers
# ---------------------------------------------------------------------------------------------------
def k(target, n, zone=SF):
    return kill(target, n, zone=zone)


def boss(target, zone=UC):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def gather(item, n):
    return dict(type="gather", target=item, count=n)


def explore(zone, x, y, radius=8):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    """A DIALOGUE objective. The content is NOT here: the labels and responses live in
    world/quest_dialogue_shimmering_flats.py, which world/quest_dialogue.py merges by name. An
    unauthored topic renders no button and the quest becomes uncompletable, so every id passed
    here has an entry in that module and tools/audit_quests.py checks the pair."""
    return dict(type="dialogue", topics=list(topics))


def carry(item_id, name, desc, count=1):
    """Items the GIVER hands over on accept.

    A deliver objective for an item the player is never given is a quest that cannot be handed in,
    and it does not look broken from the json - which is exactly what swf_salt_crossing and
    swf_salt_back were until audit_quests reported them blocked. The salt and the reply are carried
    goods: nothing drops them, so the giver has to put them in your hands.
    """
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=count)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None,
      salt="", **engine):
    """One quest. `salt` changes ONLY the reward seed - tirisfal_gear.specs samples armour classes off
    the id it is handed, and a quest id is a save-game key, so salting the draw is the honest lever
    when audit() below reports a lopsided spread."""
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             # unique_item_defs, NOT "rewards" - quest_manager reads the first and a pack authored
             # under the second loads, sits in the json and is never handed to anybody.
             unique_item_defs=reward_pack(qid + salt, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ---- givers. Every id is already in a roster; this pass invents nobody. -----------------------------
# Saltwheel (tools/saltwheel_npc_roster.py)
TOZZIK = "sw_race_marshal"      # Race-Marshal Tozzik Brasswheel - still posts the times
GRIZZIK = "sw_pit_boss"         # Pit-Boss Grizzik Vane - four hands on the payroll for nothing
OYLA = "sw_mechanic"            # Mechanic Oyla Spannerwick - took one apart and understands it now
MOZZ = "sw_fuel_trader"         # Fuel-Trader Mozz - two hundred racers, six customers
PIM = "sw_salvager"             # Salvager Pim Gattle - everything out there is hers when it stops
HETT = "sw_repair"              # Armourer Hett Grindle - can slow salt, cannot stop it
NAZZIK = "sw_old_racer"         # Old Nazzik - course record, uncontested, and he knows why
WINNOW = "sw_tally_clerk"       # Tally-Clerk Winnow - knows exactly how much the town has shrunk
BRAK = "sw_hive_watcher"        # Watcher Brak Kesh - five mounds from the fence
JIXA = "sw_salt_buyer"          # Jixa Brinecount - the one trade that still works
FENK = "sw_road_agent"          # Road-Agent Fenk Dustle - sells you the walk out
DRAL = "sw_quartermaster"       # Quartermaster Dral Wexx - eight seasons of raceday stock
GREBBIT = "sw_general_goods"    # Trader Grebbit Maul - it was always the wheels
NISSA = "sw_reagents"           # Brewer Nissa Tolk - seals everything in lead
VOZZI = "sw_innkeeper"          # Innkeeper Vozzi Rimehand - bed, board and a bind
SNOD = "sw_barkeep"             # Barkeep Snod - has not spoken to Vozzi in two years
PELLIK = "sw_doctor"            # Doc Pellik - salt sores, sun, and what the bugs do to a hand
# Freewind Post (tools/freewind_npc_roster.py) - the far end of the salt line, already in the game
OVI = "fw_market_spices"        # Spice-Trader Ovi - "Salt from the flats, east of here."
BOHL = "fw_caravan_master"      # Caravan-Master Bohl - four caravans a week and none on time

# ---- the two far-zone prerequisites for the water gate. Both are live, finished quests. ------------
ASP_WATER = "asp_higher_every_spring"       # The Aspen Wilderness 29-30
FW_WATER = "fw_where_the_water_goes"        # Southern Thousand Needles 33-34


# ---------------------------------------------------------------------------------------------------
# FETCH AND GATHER SOURCES. A fetch item nothing drops is a quest nobody can hand in, so every id
# below is written into data/creatures/quest_drops.json by main().
# ---------------------------------------------------------------------------------------------------
FETCH_DROPS = {
    "Dustwheel Scrapper": [
        ("sf_pry_bar", "Dustwheel Pry Bar", "Flattened at one end from being used as something else.", 0.45),
        ("sf_salvage_tag", "Salvage Tag", "A numbered tin tag. The rule it refers to is real.", 0.40),
    ],
    "Dustwheel Boilerman": [
        ("sf_boiler_plate", "Scorched Boiler Plate", "Blued through in a ring where it ran too hot.", 0.45),
    ],
    "Dustwheel Wheelman": [
        ("sf_course_wheel", "Course-Worn Wheel", "Flat-spotted on one side. It was driven, not parked.", 0.40),
    ],
    "Saltcrust Skitterer": [
        ("sf_crust_mandible", "Crusted Mandible", "Salt has grown over the edge and not blunted it.", 0.50),
    ],
    "Pan-Crawler Drone": [
        ("sf_drone_resin", "Wet Resin", "Sets hard in an hour and never fully sets.", 0.50),
    ],
    "Hive Spitter": [
        ("sf_spitter_sac", "Spitter's Sac", "Still under pressure. Doc Pellik would like it on a table.", 0.45),
    ],
    "Mound Sentinel": [
        ("sf_sentinel_plate", "Sentinel Shell-Plate", "Plated salt over plated chitin.", 0.40),
    ],
    "Flats Tunneler": [
        ("sf_tunnel_spoil", "Tunnel Spoil", "Pan dug out from underneath and brought up dry.", 0.50),
    ],
    "Crustback Scorpid": [
        ("sf_scorpid_barb", "Crustback Barb", "The salt keeps the venom from drying out. Nobody knows why.", 0.45),
    ],
    "Salt Vulture": [
        ("sf_vulture_quill", "Salt-Stiff Quill", "It does not bend any more. It never will.", 0.50),
    ],
    "Mirage Basilisk": [
        ("sf_basilisk_eye", "Clouded Basilisk Eye", "Looking into it is like looking down the pan at noon.", 0.40),
    ],
}

#: STARTER DROPS. Two quests that nobody gives you - you pick something up and turn it over.
#: Both are low-chance because an item-starter that drops constantly stops being a find.
STARTER_DROPS = {
    "Dustwheel Wheelman": [
        ("sf_entry_slip", "Water-Stained Entry Slip", "An entry slip for the Saltwheel Open. The "
         "season on it is three years old and the name has been scratched out and rewritten twice.",
         0.10)],
    "Flats Tunneler": [
        ("sf_sealed_tin", "Salt-Sealed Tin", "A tin sealed with lead against the salt, dug up out of "
         "the pan. Something is still dry inside it.", 0.09)],
}


def build():
    A = []

    # ===============================================================================================
    # THREAD 1 - THE SALTWHEEL OPEN (6). Tozzik runs the race one more time.
    #
    # The shape is a man assembling a thing that does not want to be assembled, and the chain's
    # movement is NOT "it gets harder" - it is that each station makes it clearer the race cannot
    # really happen, and he proceeds anyway. The finale is a time worse than the record, posted.
    # ===============================================================================================
    A.append(Q("swf_open_date", "Somebody Has to Hold the Date", TOZZIK, SW, 35, 36, "raceday",
        "Race-Marshal Tozzik Brasswheel posts the times for the Saltwheel Open on the first clear day "
        "after the winter wet. Entries at the gantry, scrutineering at noon, flag at two.\n\nNobody "
        "has entered for three seasons. He posts them anyway, in a clean hand, and stands under the "
        "board for an hour afterwards in case somebody comes.",
        [k("Dustwheel Scrapper", 8), gather("sf_salvage_tag", 5)],
        "The start line wants clearing before anything else happens, and the ones clearing it are not "
        "mine. They have been off the course stripping the kerb markers since the wet, and every "
        "marker they take is a yard of the line I cannot certify.\n\nEight of them off the straight, "
        "and bring me the tags. The tags are numbered. I want to know which markers I have lost and "
        "not just how many.",
        "Numbered consecutively, which means one person pulled them in one afternoon and did not "
        "hurry.\n\nI am not angry about it. I am angry that it took me until the tags to work out "
        "nobody had been out to look.\n\nRight. Scrutineering is at noon and I have no scrutineer.",
        nxt="swf_open_scrutineer"))

    A.append(Q("swf_open_scrutineer", "Scrutineering Is at Noon", OYLA, SW, 35, 36, "raceday",
        "Mechanic Oyla Spannerwick has scrutineered every Open since she was old enough to hold the "
        "gauge, and she has not been asked since the track died.\n\nShe says yes before Tozzik finishes the "
        "sentence, which embarrasses them both.",
        [gather("sf_boiler_plate", 4), gather("sf_pry_bar", 3)],
        "If anything runs on that straight it runs on a boiler, and I will not pass a boiler I have "
        "not seen plate from. Four pieces, off the Dustwheel crews - they are running the same "
        "pattern we did and running it badly, which makes their failures useful to me.\n\nAnd three "
        "pry bars. Not for the race. For me.\n\nThree years ago somebody drove a machine down that "
        "straight that had no boiler in it at all. Did the whole run on a thimble of fuel. I have "
        "taken one apart since and I understand it now, and that is worse than not understanding it.",
        "Blued in a ring, every one of them. Same fault we had and never fixed, and they have not "
        "fixed it either.\n\nThere is a comfort in that I am not proud of.\n\nTell Tozzik his "
        "scrutineer is ready. Tell him I said it like it was nothing.",
        nxt="swf_open_entries"))

    A.append(Q("swf_open_entries", "Entries at the Gantry", TOZZIK, SW, 36, 37, "raceday",
        "The board is up, the scrutineer is ready, and the entry column has been blank for three "
        "seasons.\n\nTozzik will not ask anyone directly. He has decided that asking would make it a "
        "favour, and a favour is not an entry.",
        [talk("swf_topic_nazzik", "swf_topic_grizzik", "swf_topic_mozz")],
        "I am not going to go round the town asking. You can. You are not from here and it costs you "
        "nothing, which is the only reason this is not beneath both of us.\n\nNazzik holds the course "
        "record and will tell you so. Grizzik keeps a crew for a race that does not run and pays half "
        "of it herself. Mozz has fuel and no one to sell it to.\n\nAsk all three. Do not persuade "
        "anybody. I want to know what they say when nobody is leaning on them.",
        "One record-holder who will not drive, one pit boss who would crew it tomorrow, and Mozz.\n\n"
        "Mozz said he would supply the fuel at cost on condition somebody tells the newcomers this is "
        "their fault. I am not putting that on a board.\n\nBut he said he would supply it. Write that "
        "down and leave the rest.",
        nxt="swf_open_course"))

    A.append(Q("swf_open_course", "The Course, As It Is Now", TOZZIK, SF, 36, 37, "raceday",
        "The Mirage Raceway is a loop out across the northern pan and back to the straight. It was "
        "surveyed once, eleven years ago, and has not been walked since the hives came up.\n\nTozzik "
        "has been posting a course he has not seen.",
        [explore(SF, 144, 30, 10), k("Glasswing Darter", 7), gather("sf_drone_resin", 5)],
        "Out to the far turn and look at it. That is all I am asking for and it is more than I have "
        "done.\n\nThe darters have taken the north leg and they come off the ground fast enough to "
        "put a driver into the salt. Seven of them, and bring me resin from whatever is laying it, "
        "because I need to know whether the course is fouled or whether it is being BUILT ON.\n\nThere "
        "is a difference and the difference decides whether there is a race.",
        "Built on.\n\nThat resin is structural. They are not crossing my course, they are putting "
        "something down on it, and the far turn is inside whatever they are putting down.\n\nSo the "
        "loop is gone. The straight is not. A race on the straight alone is not an Open and I am going "
        "to call it one, and you are the only person who will ever know that I know.",
        nxt="swf_open_flagfall"))

    A.append(Q("swf_open_flagfall", "Flagfall", GRIZZIK, SW, 37, 38, "raceday",
        "Pit-Boss Grizzik Vane has four hands on the payroll for a race that has not run since the "
        "wet before last. Tozzik pays half and she pays half and neither of them has ever said out loud "
        "what they are paying for.\n\nThis week they find out.",
        [k("Dustwheel Wheelman", 6), k("Dustwheel Boilerman", 5), gather("sf_course_wheel", 4)],
        "Here is the part nobody says in front of Tozzik. The Dustwheel know the date too, and they "
        "have been running the straight themselves since the wet, and they will be on it at two "
        "whether we are or not.\n\nSo the straight gets cleared properly this time. Six of the "
        "wheelmen and five of the boiler crews, and bring the wheels back - flat-spotted ones, off "
        "the ones that were actually driven. I want to see what they have been doing with my course.",
        "Flat-spotted on one side, every one. They have been locking the wheels at the same mark on "
        "every run, which means they are racing each other out there. Properly. Timing it.\n\nThree "
        "years I have been paying half a crew to sit in a shed and the sport never stopped. It just "
        "stopped being ours.\n\nGo and tell Tozzik the flag drops at two.",
        nxt="swf_open_record"))

    A.append(Q("swf_open_record", "What Tozzik Writes Down", TOZZIK, SF, 38, 39, "raceday",
        "The flag dropped at two. One entrant, on the straight alone, because the loop belongs to "
        "something else now.\n\nTozzik timed it himself, because the only other person who knows how "
        "was driving.",
        [explore(SF, 104, 50, 6), k("Mound Sentinel", 8), gather("sf_sentinel_plate", 4)],
        "Before I post it there is a thing I want done and I want it done by somebody who was not "
        "here for the good years.\n\nWalk the straight, end to end, at the pace a person walks. Then "
        "go and put eight of the mound-guards off the eastern mark and bring me four plates off them, because "
        "the eastern mark is where the course used to turn and I want to know what is standing on it "
        "now.\n\nI am going to post the time either way. I would rather post it knowing.",
        "Worse than the record by a margin I am not going to say out loud, on a course that is a "
        "third of the one the record was set on.\n\nI have posted it.\n\nNazzik will tell you his "
        "record stands and he is right, and he will not tell you that he was under the board at six "
        "this morning reading the new time. I saw him. He saw me see him.\n\nThe date held. That is "
        "what I had and I held it."))

    # ===============================================================================================
    # THREAD 2 - THE DUSTWHEEL (5). The town decides what word to use.
    #
    # The movement is a WORD, not a war: bandits -> cousins -> customers. It resolves in Winnow's
    # ledger, which is the most goblin resolution available - the argument ends when somebody writes
    # a line in the right column.
    # ===============================================================================================
    A.append(Q("swf_dust_rights", "Salvage Rights, As Written", PIM, SW, 35, 36, "dustwheel",
        "Salvager Pim Gattle owns everything out on that track the day it stops moving. The rule is "
        "written down, it is older than the track, and she is the richest wreck-picker on a pan "
        "with no wrecks left on it.\n\nThe Dustwheel have been taking things that have not stopped "
        "moving yet.",
        [k("Dustwheel Scrapper", 10), gather("sf_pry_bar", 5)],
        "Read the rule and you will find it says STOPPED. Not slowed, not parked, not abandoned by a "
        "crew that went into town for a season. Stopped.\n\nTen of them off my course and five of "
        "their bars, and before you tell me that is a lot of effort for a rule nobody enforces - yes. "
        "It is. That is what a rule nobody enforces costs, and I have been paying it every season since the wet.",
        "Five bars and every one of them flattened at the business end, because they have been using "
        "them as levers on things that were never meant to come apart.\n\nI would have taught them "
        "that in a morning. Nobody asked me to teach anybody anything.\n\nGrizzik wants a word with "
        "you and she will not enjoy having it.",
        nxt="swf_dust_cousins"))

    A.append(Q("swf_dust_cousins", "Half of Them Are Somebody's Cousin", GRIZZIK, SW, 36, 37,
        "dustwheel",
        "Nobody in Saltwheel calls the Dustwheel bandits. The word has been available since the track died "
        "and not one person has picked it up.\n\nGrizzik Vane knows exactly why and will say it to "
        "you and to nobody else.",
        [k("Dustwheel Boilerman", 8), gather("sf_boiler_plate", 5), talk("swf_topic_word")],
        "Pim has you putting them off the course and she is right to and I want you to understand what "
        "you are doing, because she will not tell you.\n\nHalf of them are somebody's cousin. When the "
        "track died some of us walked into town and some of us walked out onto the pan, and the "
        "difference was mostly which way you were facing that week.\n\nEight of the crews, and five plates off them, and then come back and ask me what we call them. I want to be asked out loud.",
        "Same fault in every plate. Our fault. They learned it from us, and we learned it from "
        "nobody - we worked it out, badly, over eleven years, and then taught it to the people we are "
        "now paying somebody to put off a road.\n\nWe do not call them anything. That is the answer "
        "and you made me say it.",
        nxt="swf_dust_fuel"))

    A.append(Q("swf_dust_fuel", "Two Hundred Racers and Six Customers", MOZZ, SW, 36, 37, "dustwheel",
        "Fuel-Trader Mozz laid in enough to run a full season the year before the track died. He has "
        "been sitting on it since.\n\nHe has done the arithmetic on who is at fault and he will do it "
        "at you, at length, and the frustrating part is that his numbers are correct.",
        [k("Dustwheel Wheelman", 7), gather("sf_course_wheel", 5)],
        "Before the sky changed I had two hundred racers on this pan. I have six customers. Six. And "
        "the same season the mountain turned up in the north, which I am told is a coincidence and "
        "which I am told by people who are not selling fuel.\n\nSeven of the wheelmen. They are "
        "burning something out there and it is not coming from me, and I want a wheel off one so I can "
        "see what it is doing to the rubber.",
        "They are running it dry and lean and they are getting away with it, which means they have "
        "found something cheaper than what I sell.\n\nSo that is the rest of my customers gone, in "
        "front of me, with a wheel in my hand.\n\nYou came through same as the rest of them and I am "
        "not going to pretend I am delighted. But you did the job and the job was the job. Take it.",
        nxt="swf_dust_axle"))

    A.append(Q("swf_dust_axle", "The Axle Nobody Will Claim", PIM, SF, 37, 38, "dustwheel",
        "There is a broken axle out on the far straight that is worth more than anything else left on "
        "the course.\n\nIt has been there two seasons and neither Pim nor the Dustwheel has taken it, "
        "and both of them could have, any day, without being seen.",
        [explore(SF, 128, 70, 9), k("Dustwheel Scrapper", 8), gather("sf_salvage_tag", 6)],
        "Out past the far turn there is an axle. You will know it when you see it, it is the only "
        "thing out there that has not been stripped.\n\nGo and look at it. Do not bring it back, I am "
        "not asking you to bring it back. And put eight of them off it while you are there and bring "
        "me the tags, because if they have tagged it then it is theirs by their rule and I want to "
        "know that for certain rather than suspecting it for another two years.",
        "Not tagged.\n\nTwo seasons and nobody has claimed it, theirs or mine, and now I have to "
        "decide what that means.\n\nIt means we both think the other one is going to need it more. "
        "That is a stupid thing for two businesses to think about each other and I have been thinking "
        "it since the wet.\n\nTake this to Winnow. She keeps the book. Tell her I sent you and do not "
        "tell her why.",
        nxt="swf_dust_ledger"))

    A.append(Q("swf_dust_ledger", "Winnow Writes It Down Twice", WINNOW, SW, 38, 39, "dustwheel",
        "Tally-Clerk Winnow records every cart in and out, every barrel of salt, written down twice. "
        "The town is shrinking and she can tell you by exactly how much, which makes her the least "
        "popular person in it.\n\nShe has been waiting a long time for somebody to ask her a specific "
        "question.",
        [gather("sf_salvage_tag", 8), deliver("sf_pry_bar", "Winnow's bench", 3), talk("swf_topic_ledger")],
        "Pim sent you and did not say why, which means she has finally worked it out and cannot stand "
        "to be the one who says it.\n\nBring me eight of their tags and three of their bars and put "
        "them on this bench. Then ask me what column they go in. Go on. Ask me the actual question "
        "and I will give you the actual answer, which nobody in this town has wanted since the track died.",
        "Customers.\n\nThey go in as customers. They have been buying fuel off somebody, parts off "
        "somebody, and salt off Jixa under a different name since the second winter, and it is in "
        "this book, and it has been in this book the whole time.\n\nThe town is down by a figure I "
        "could say out loud. It is not down by as much as it thinks, and the difference is sitting out "
        "on that pan calling itself something else.\n\nI am going to put this in front of Tozzik and "
        "he is going to have to decide whether they can enter."))

    # ===============================================================================================
    # THREAD 3 - THE MOUNDS (6). Brak Kesh counts, and the count goes up.
    #
    # Escalates OUTWARD and then downward, and ends under the pan in the Undercrust. The Hollow Queen
    # is a pinned chamber boss, not a rare, so kill_boss on her is legitimate.
    # ===============================================================================================
    A.append(Q("swf_mound_five", "Five From the Fence", BRAK, SF, 35, 36, "hive",
        "Watcher Brak Kesh can see five mounds from the east fence. Three years ago there were two, "
        "and the near one was twice as far out as it is now.\n\nHe says the number in the inn every "
        "evening. They have started buying him drinks so that he says it quieter.",
        [k("Saltcrust Skitterer", 12), gather("sf_crust_mandible", 6)],
        "I count mounds. That is the post, that is the whole post, and the post was invented by a man "
        "who expected the number to stay at two.\n\nThe skitterers come off the near one and work "
        "west along the fence line. A dozen of them and six mandibles, and look at the salt on the "
        "mandibles when you take them - it grows over the edge and it does not blunt it. I want to "
        "know if that is true of all of them or just the ones I have seen.",
        "All of them.\n\nSo it is not damage and it is not age, it is how they are made, and a thing "
        "that is made that way on a salt pan was not an accident of where it ended up.\n\nThey belong "
        "here now. That is a worse sentence than the number is.",
        nxt="swf_mound_moved"))

    A.append(Q("swf_mound_moved", "The Near One Moved", BRAK, SF, 36, 37, "hive",
        "The mound Brak calls the near one is not where it was at the start of the wet.\n\nMounds do "
        "not move. He has checked his own sightings four times and they are good sightings, taken off "
        "the same two fence posts since I took the post.",
        [explore(SF, 92, 62, 9), k("Pan-Crawler Drone", 10), gather("sf_drone_resin", 6)],
        "Out to the First Mound and stand at the foot of it. I need somebody who has not been looking "
        "at it every evening since the first winter to tell me what shape it is.\n\nTen of the crawlers while you are there and six of the resin. The resin is the thing. If they are laying fresh on the "
        "west face and the east face is old, then it did not move - it GREW, westward, toward the "
        "fence, and that is a different problem with a different arithmetic attached.",
        "Fresh on the west, old on the east.\n\nIt grew. Toward us, at a rate I can now calculate, and "
        "I am going to calculate it tonight and then I am going to have to decide whether to say the "
        "new number in the inn.\n\nThey will buy me drinks either way. That is what I have learned "
        "about this town.",
        nxt="swf_mound_salt", salt="d"))

    A.append(Q("swf_mound_salt", "What They Are Doing With the Salt", NISSA, SW, 37, 38, "hive",
        "Brewer Nissa Tolk seals everything in lead because salt air takes a cork in a season.\n\nShe "
        "has been reading Brak's notes over his shoulder in the inn and has noticed something he has "
        "not, because she is the only person in Saltwheel who thinks about salt as a substance rather "
        "than as a price.",
        [gather("sf_tunnel_spoil", 8), gather("sf_crust_mandible", 5)],
        "Brak counts the mounds and nobody asks the obvious question, which is what is coming OUT of "
        "them.\n\nThe tunnelers bring spoil up and leave it. Eight loads of it, and five more "
        "mandibles for me to set against the spoil.\n\nThe pan is salt all the way down for as deep as "
        "anybody has ever dug. If what they are bringing up is dry, we have a problem nobody in this "
        "town is equipped to think about.",
        "Dry. Bone dry, all eight, from under a pan that should be wet through at that depth.\n\nThey "
        "are not digging through the salt. They are digging through what is UNDER it, and what is "
        "under it has no water in it any more, and I would very much like to know when it stopped "
        "having water in it.\n\nSomebody has asked this question before. Not here. Go and find out "
        "where.",
        nxt="swf_mound_spitters"))

    A.append(Q("swf_mound_spitters", "Spitters on the Fence Line", PELLIK, SW, 37, 38, "hive",
        "Doc Pellik treats salt sores, sun, and whatever the bugs do to a hand. Three complaints, in "
        "that order, every season.\n\nThe third one has been climbing for two years and he has stopped "
        "pretending it has not.",
        [k("Hive Spitter", 9), fetch("sf_spitter_sac", 4), gather("sf_scorpid_barb", 4)],
        "A spitter gets resin into a wound and the wound sets. Not closes - SETS, with the dirt still "
        "in it, and then I am cutting it open again in a fortnight.\n\nNine of them off the fence "
        "line, and I want four sacs still under pressure and four scorpid barbs to set against them. "
        "The barbs keep their venom wet out here when everything else dries. If I can work out why, I "
        "can work out how to keep a wound open.\n\nIt is not elegant medicine. It is the medicine "
        "available.",
        "Still under pressure, all four. Good.\n\nThe barb keeps wet because of something in the "
        "sheath and the resin sets because of something it is missing, and between the two of them I "
        "have an afternoon's work and possibly a hand saved in the spring.\n\nThat is the best "
        "sentence I have said in this surgery in a year.",
        nxt="swf_mound_mouths", salt="e"))

    A.append(Q("swf_mound_mouths", "Two Mouths, One Hole", BRAK, SF, 38, 39, "hive",
        "There are two ways down into the Undercrust and they are most of the pan apart. The Crustfall "
        "is a shallow slot by Crustbreak. The Deep Shaft is out under the oldest mound on the map.\n\n"
        "Brak has assumed since he took the post that they are two caves.",
        [explore(SF, 92, 140, 7), explore(SF, 172, 113, 7), k("Flats Tunneler", 10)],
        "Both holes. The Crustfall first, then all the way across to the Deep Shaft, and ten of the "
        "tunnelers between them.\n\nI am not asking you to go in. I am asking you to stand at both and "
        "tell me whether the air coming out of them smells the same, because if it does then I have "
        "been counting two caves for four winters and there is one, and it is bigger than the pan it is "
        "under.",
        "The same.\n\nOne hole. Most of this pan is standing on one hole with two mouths, and I have "
        "been writing down two numbers in two columns since the first winter like a man who cannot add "
        "up.\n\nI am going to go and say that in the inn tonight at full volume and they can buy me "
        "whatever they like.",
        nxt="swf_mound_queen"))

    A.append(Q("swf_mound_queen", "The Hollow Queen", BRAK, UC, 39, 40, "hive",
        "One cave, two mouths, and at the heart of it something that has been laying since before "
        "anybody in Saltwheel was born.\n\nBrak has stopped counting mounds. He says there is no point "
        "counting the branches when you have found the root.",
        [boss("The Hollow Queen"), k("Undercrust Ripper", 8, UC), gather("sf_sentinel_plate", 5)],
        "Go in at whichever mouth you like. They both get there, which is the thing I spent three "
        "years not knowing.\n\nShe is at the middle. Eight of the rippers on the way and five plates "
        "off the sentinels, and I want the plates because I want to see whether what guards her is "
        "made the same as what comes out to the fence.\n\nI am not coming. I have one skill and it is "
        "standing on a fence counting, and down there there is nothing to count.",
        "Made the same. Exactly the same, root to branch, and she was the root.\n\nIt does not end it. "
        "You know that and I know that - there are four more mounds out there and a hole under all of "
        "them.\n\nBut the near one has stopped growing west this week. Measured off the same two posts. "
        "First time the number has gone the other way since I took this post, and I am going to enjoy "
        "it for exactly one evening."))

    # ===============================================================================================
    # THREAD 4 - THE SALT LINE (5). The chain that LEAVES THE ZONE.
    #
    # Already seeded: Freewind Post's spice-trader says "Salt from the flats, east of here. It is the
    # one trade the Integration did not touch, and I have never been so glad to be boring." She is
    # buying from Jixa. Two zones apart, never in the same conversation. This is that conversation.
    # Jixa is also the zone's COUNTER-EXAMPLE on the Earth question - warm, not bitter - and the
    # thread needs her to be, or nine resentful goblins become the zone's only note.
    # ===============================================================================================
    A.append(Q("swf_salt_one_trade", "The One Trade That Still Works", JIXA, SW, 35, 36, "saltline",
        "Jixa Brinecount deals in salt. That is the whole business, and everybody laughed at her for "
        "twenty years for it.\n\nThey are not laughing now. They are mostly just gone.",
        [gather("sf_vulture_quill", 6), k("Salt Vulture", 10)],
        "Salt is the only trade on this pan the Integration did not touch, and I will tell you why, "
        "because nobody else here will say a kind word about any of it.\n\nNothing that came through "
        "needed a racetrack. Everything that came through needs to eat.\n\nThe vultures are at the "
        "drying racks on the shore and they have worked out that a rack is a table. Ten of them and "
        "six quills, which I use for marking grades, and which I would buy off you anyway.",
        "Salt-stiff, every one, which is what makes them good for grading - they do not bend and so "
        "they do not lie about the line they drew.\n\nYou will have heard a lot of complaining in this "
        "town and most of it is fair. Mine is the one ledger that went UP, and I am not going to "
        "pretend otherwise just to be sociable.",
        nxt="swf_salt_graded"))

    A.append(Q("swf_salt_graded", "Pan Salt, Graded", JIXA, SF, 36, 37, "saltline",
        "Salt from the shore is clean and salt from the crust is not, and the difference is money.\n\n"
        "Jixa grades it herself, by eye, with a vulture quill, and has never once been wrong in a way "
        "the buyer noticed.",
        [gather("sf_tunnel_spoil", 7), explore(SF, 60, 36, 9), k("Crustback Scorpid", 8)],
        "Out onto the Crust and bring me seven loads of what the tunnelers have thrown up. It is the "
        "deepest salt anybody can get at without digging, and the deepest salt is the cleanest, which "
        "is a thing I have believed for twenty years on no evidence at all.\n\nEight of the scorpids "
        "off the drying ground while you are out. They get into the stacks and they do not come out "
        "and then somebody finds one in a barrel in Freewind Post and I hear about it for a year.",
        "Cleanest I have graded. Twenty years of guessing and it turns out I was right, which is "
        "worth less than being able to prove it but it is not worth nothing.\n\nNow. The problem.\n\n"
        "I have the best salt I have ever had and no way to get it anywhere, because the cart does not "
        "come any more.",
        nxt="swf_salt_cart"))

    A.append(Q("swf_salt_cart", "The Cart Does Not Come Any More", FENK, SW, 37, 38, "saltline",
        "Road-Agent Fenk Dustle sells what a person needs to walk out of Saltwheel, which is a "
        "thriving business, because walking out is the only option available.\n\nHe is extremely "
        "cheerful about this and it takes a while to work out why.",
        [k("Mirage Basilisk", 7), gather("sf_basilisk_eye", 4), gather("sf_scorpid_barb", 5)],
        "Jixa wants her salt in Freewind Post and there is no cart, no bird and no road worth the "
        "word. There is you.\n\nThe west crossing goes past the Brine and the basilisks have the "
        "Brine. Seven of them and four eyes - I sell the eyes to people who think they are lucky, and "
        "before you ask, no, and they buy them anyway.\n\nFive barbs as well. Those actually work for "
        "what I say they do, which makes them the odd item on my table.",
        "Clouded right through. Looking into one is like looking down the pan at noon, which is "
        "exactly what I tell the buyers and exactly why they buy them.\n\nThe crossing is open. Go and "
        "tell Jixa, and then come back to me, because she is going to send you across it and you are "
        "going to want the kit and I am going to sell it to you.\n\nThere is no bird. I have mentioned "
        "that. I will mention it again.",
        nxt="swf_salt_crossing"))

    A.append(Q("swf_salt_crossing", "Across the Pan, On Foot", JIXA, FW, 38, 39, "saltline",
        "Freewind Post sits over a long drop at the far end of the mesas, and between it and Saltwheel "
        "there is a pan, a range, and nothing that flies for hire.\n\nJixa has been shipping to "
        "Spice-Trader Ovi for eleven years and the two of them have never met.",
        [deliver("sf_graded_salt", "Spice-Trader Ovi, Freewind Post", 4), talk("swf_topic_ovi")],
        "Four sacks, graded, sealed. Ovi has been buying off me since before the sky changed and she "
        "has never once haggled, which told me everything I needed to know about her and nothing about "
        "what she looks like.\n\nWhen you get up there, ask her the question I have never been able to "
        "put in a letter. She will know which one. If she does not, she is not the woman I have been "
        "trading with.",
        "[Spice-Trader Ovi turns one of the sacks so the seal faces her, and does not open it.]\n\n"
        "Eleven years. She asks whether I still think it is boring.\n\nTell her yes. Tell her I have "
        "three climates on one table now and the only thing on it that has never caused me a day's "
        "trouble is her salt, and that the mountain can do what it likes as long as the pan keeps "
        "drying.\n\nAnd tell her the caravans will come. Bohl has been saying it for a year. One of "
        "these years he will be right.",
        nxt="swf_salt_back",
        grant_items=carry("sf_graded_salt", "Graded Pan Salt",
                          "Four sacks, graded by eye with a vulture quill and sealed in lead.", 4)))

    A.append(Q("swf_salt_back", "What Bohl Said About the Road", BOHL, FW, 38, 39, "saltline",
        "Caravan-Master Bohl runs four caravans a week up the ramp and not one of them on time.\n\nHe "
        "has been asked about the Saltwheel road every season since the track died and has given the same "
        "answer every time, and this season the answer has changed.",
        [k("Dustwheel Scrapper", 9, SF), gather("sf_salvage_tag", 6), deliver("sf_ovi_reply",
                                                                             "Jixa Brinecount, Saltwheel")],
        "Ovi wants a cart on that pan and I have told her no every season because of what is on the "
        "road. Not the hives. The crews.\n\nNine of them off the west crossing and six tags, and if "
        "the tags are numbered in sequence then it is one outfit working a route and I can negotiate "
        "with an outfit. If they are scattered then it is nobody and I cannot.\n\nAnd take Ovi's reply "
        "back down with you. She wrote it standing up, which from her is a great deal.",
        "In sequence. One outfit, one route, a schedule I can read off six tin tags.\n\nI can work "
        "with that. I have worked with worse and I married one of them.\n\nTell Brinecount the cart "
        "comes in the spring and tell her I said IF, in the voice I use for if. She will know. "
        "Everyone who ships out of a dying town knows that voice.",
        grant_items=carry("sf_ovi_reply", "Ovi's Reply",
                          "Written standing up, which from her is a great deal.")))

    # ===============================================================================================
    # THREAD 5 - THE WATER (3). The Linken's-Sword gate.
    #
    # swf_water_answer is gated on asp_higher_every_spring (Aspen 29-30) and fw_where_the_water_goes
    # (Southern Thousand Needles 33-34) - two finished quests in two other zones, by other authors,
    # three and four levels below this one. Skip either and the last one is never offered.
    # ===============================================================================================
    A.append(Q("swf_water_waterline", "The Watermark Is in the Wrong Place", OYLA, SF, 37, 38, "water",
        "There are shore stacks out on the western pan - lumps of rock the salt has not finished "
        "eating - and every one of them carries a waterline.\n\nOyla noticed it with a gauge in her "
        "hand, looking for something else entirely.",
        [explore(SF, 24, 40, 9), gather("sf_vulture_quill", 5), k("Pan-Crawler Drone", 9)],
        "Out to the stacks on the west shore. There is a stain round every one of them at a height "
        "and the height is the same on all of them, which means it is a waterline and not a "
        "coincidence.\n\nIt is a long way above where any water has been in my lifetime. Mark it for "
        "me - the quills take a mark on wet rock and hold it - and put nine of the drones off the "
        "stacks, because they are working the base of them and I do not want my marks eaten.",
        "Same height on all five, to within a hand.\n\nThis pan was deeper than this. Not in a story, "
        "not in a song - measurably, at a height I can put a gauge on, and recently enough that the "
        "stain has not gone.\n\nSo where did it go. That is not a rhetorical thing. I want the answer "
        "and I do not have the range to go and get it.",
        nxt="swf_water_three"))

    A.append(Q("swf_water_three", "Three Ranges, One Question", NISSA, SF, 38, 39, "water",
        "The tunnelers bring up dry spoil from under a pan that should be wet through.\n\nNissa Tolk "
        "has been holding that fact for a season waiting for somebody to bring her a second one, and "
        "Oyla has just brought her a waterline.",
        [gather("sf_tunnel_spoil", 9), gather("sf_basilisk_eye", 3), k("Flats Tunneler", 9)],
        "Two facts. The pan was deeper and the ground under it is dry. Those do not sit together "
        "without a third thing in between them and I do not have it.\n\nNine more loads of spoil, from "
        "as far east as you are willing to walk, and three basilisk eyes. The eyes cloud by taking up "
        "whatever is in the air around them - I can read a dry season off one the way you read a ring "
        "off a tree, if I have three to argue with each other.",
        "The eastern spoil is drier than the western, and the eyes agree with each other, and none of "
        "this is a Saltwheel-sized question any more.\n\nWater comes off a mountain in the north. It "
        "crosses the mesas. It should arrive HERE. Somebody on that mountain has been watching their "
        "melt get bigger every spring and somebody on those mesas has been asking where it goes, and "
        "if you have stood in front of either of them then you already know more than I do.\n\nCome "
        "back when you have. Not before - I would only be guessing and I am too old to guess in front "
        "of company.",
        nxt="swf_water_answer"))

    # THE GATE. requires_quests, not next_quest_id - both must be COMPLETE, in any order, in two
    # other zones. A player who did neither never sees this offered and is told nothing about it.
    A.append(Q("swf_water_answer", "Lower Every Year", NISSA, SF, 39, 40, "water",
        "The melt is higher every spring on the mountain. Nobody on the mesas can say where that water "
        "goes. The pan it should arrive on is drier than its own waterline and dry underneath.\n\nThe "
        "three of those have never been in one room. You have been in all three.",
        [explore(SF, 160, 118, 10), k("Mound Sentinel", 10), gather("sf_sentinel_plate", 6),
         gather("sf_tunnel_spoil", 6)],
        "You have stood on the mountain and you have stood on the mesas and now you are standing here, "
        "and you are the only person this side of the range who has done all three.\n\nSo: the Deep "
        "Mound, the oldest one on the pan, and the ground around it. Ten of the mound-guards, six plates, "
        "six loads of spoil from the foot of it.\n\nI think the water arrives. I think it has always "
        "arrived. I think something underneath has been drinking it for longer than this town has "
        "existed and the mountain has simply started sending more.",
        "Wet.\n\nSix loads from the foot of the Deep Mound and every one of them damp, out of a pan "
        "that is bone dry four miles west of here.\n\nIt arrives. It has never stopped arriving. It "
        "goes under, and it goes east, and it ends up beneath the oldest hive on this pan - which has "
        "been sitting on the only wet ground in the flats since before the first goblin saw this "
        "place, and which has been getting MORE of it every spring since the range came down.\n\nNobody made "
        "that happen. A mountain arrived and the water it sheds found the lowest thing it could and "
        "the lowest thing was already occupied.\n\nI am going to write this down and I am going to "
        "send a copy up the mesas, and in about forty years somebody will read all three parts "
        "together and understand this pan.",
        requires_quests=[ASP_WATER, FW_WATER]))

    # ===============================================================================================
    # THREAD 6 - THE INN (4). Four quiet ones about a building with beds in it.
    # ===============================================================================================
    A.append(Q("swf_inn_no_bird", "There Has Never Been a Bird On It", VOZZI, SW, 35, 36, "inn",
        "There is a post outside Saltwheel's inn of exactly the kind a wind rider perches on.\n\nThere "
        "has never been a wind rider on it. Innkeeper Vozzi Rimehand has explained this to every "
        "arrival for eleven years and has a particular flatness she keeps for the purpose.",
        [k("Salt Vulture", 9), gather("sf_vulture_quill", 5)],
        "Bed, board and a bind. That is the full list.\n\nBefore you ask: there is no wind rider. "
        "There was never a wind rider. You came in on your feet and that is how you are leaving.\n\n"
        "What there IS is nine birds roosting on the post, because it is the tallest thing in town "
        "and they are not fussy about what it was for. Nine of them and five quills, and then I will "
        "hear no more about birds from anybody.",
        "Off the post and off my roof.\n\nI have had that post taken down twice and put back up twice, "
        "by different people, for different reasons, and neither of them could tell me what the reason "
        "was.\n\nIt stays up. I have stopped asking myself why. Your bed is the one at the end and the "
        "shutter does not latch."))

    A.append(Q("swf_inn_two_years", "Snod and Vozzi Have Not Spoken", SNOD, SW, 36, 37, "inn",
        "Vozzi runs the beds and Snod runs the bar and they have not exchanged a word in two "
        "years.\n\nThe business has never been better and both of them have noticed, which is the "
        "problem.",
        [deliver("sf_crust_mandible", "the bar at Saltwheel", 7),
         talk("swf_topic_snod")],
        "She needs scourers for the pots and will not ask me for them and I am not offering.\n\nSo you "
        "are going to bring me seven mandibles and put them behind this bar, where she will see "
        "them when she comes through for the ice, and she will take them, and she will not say "
        "anything, and that will be that.\n\nThen ask me what we fell out about. Everyone does "
        "eventually.",
        "You want to know what it was.\n\nI do not remember. I have thought about it properly, more "
        "than once, in the quiet hours, and it has gone.\n\nShe remembers. I am certain she remembers. "
        "Which means one of us is carrying it and it is not me, and after two years asking her would "
        "be the cruellest thing in this building.\n\nShe took the mandibles. I watched her take them. "
        "Go on, get out of my bar."))

    A.append(Q("swf_inn_hinges", "Salt Gets Into a Hinge", HETT, SW, 36, 37, "inn",
        "Armourer Hett Grindle can slow salt. He cannot stop it, and anyone who tells you they can "
        "stop it is selling you grease.\n\nThe inn's shutters have not latched properly in a year and "
        "Vozzi has stopped mentioning it.",
        [gather("sf_sentinel_plate", 5), gather("sf_drone_resin", 6)],
        "Here is a thing the hives are better at than we are, which I resent and which is true.\n\nThe "
        "sentinel plate has salt grown THROUGH it and still articulates. Ours seizes in a season. "
        "Bring me five plates and six of the wet resin and let me find out whether it is the plate or "
        "whether it is what they bed it in.\n\nIt is for a shutter. I am aware of the scale of the "
        "ambition.",
        "It is the resin. The plate is ordinary. They bed every joint in something that never fully "
        "sets, so the salt gets in and gets pushed back out every time the joint moves.\n\nA hinge "
        "that cleans itself by being used. Three years that has been walking past my shop on eight "
        "legs.\n\nThe shutter at the end latches now. Do not tell her it was me, she will want the "
        "other eleven doing and I have a trade to run."))

    A.append(Q("swf_inn_stock", "Eight Seasons of Raceday Stock", DRAL, SW, 37, 38, "inn",
        "Quartermaster Dral Wexx laid in eight seasons of stock the year before the track died, for a "
        "crowd that was coming and then did not.\n\nIt is all still in the warehouse, in good order, "
        "because he has kept it in good order, which is either professionalism or something sadder.",
        [k("Dustwheel Boilerman", 8), gather("sf_boiler_plate", 6), gather("sf_pry_bar", 4)],
        "I have shelves built for a raceday crowd and six regulars. You can do that sum as fast as I "
        "can.\n\nThe Dustwheel have been into the back of the warehouse twice this season, and I would "
        "rather deal with that than report it, because reporting it means Winnow writes it down and "
        "once Winnow writes it down it is a fact about this town forever.\n\nEight of the crews, six plates, four bars. That is what they left behind and I want it accounted for.",
        "Accounted for, and I am going to tell you something I have not told Winnow.\n\nThey did not "
        "take anything the second time. They put something back. A crate of plate, our pattern, better "
        "made than ours.\n\nSo either somebody out there is paying a debt nobody recorded, or they are "
        "being polite, and I have no column for either.\n\nTake what you are owed. The stock was never "
        "going to move and at least it is moving."))

    # ===============================================================================================
    # STANDALONES (5) + TWO ITEM-STARTERS. Nobody gives you the last two: you pick something up.
    # ===============================================================================================
    A.append(Q("swf_solo_prices", "It Was Always the Wheels", GREBBIT, SW, 35, 36, "saltline",
        "Everything on Trader Grebbit Maul's table came across the pan on a cart with four bad "
        "wheels.\n\nHe will tell you the price is the wheels. It is partly the wheels.",
        [k("Saltcrust Skitterer", 10), gather("sf_crust_mandible", 5)],
        "You will think my prices are high. They are high. Cartage across a dead pan, and before you "
        "say it - yes, they were lower four years ago, and yes, that is about when the sky "
        "rearranged itself and half my suppliers found more interesting customers.\n\nTen of the "
        "skitterers out of the stock yard and five mandibles. They are in the sacks. They are always "
        "in the sacks.",
        "Out of the sacks, and I will drop what I charge you by a bit and not by as much as you are "
        "hoping.\n\nI am not blaming you personally. I am blaming the general situation, of which you "
        "are a part, and I have found that saying that out loud to one person at a time is the only "
        "satisfaction available to me."))

    A.append(Q("swf_solo_record", "The Record Stands", NAZZIK, SW, 36, 37, "raceday",
        "Old Nazzik holds the course record for the Saltwheel Open. Eleven years and nobody has "
        "touched it.\n\nHe will tell you why before you can work it out and get there first on "
        "purpose.",
        [explore(SF, 120, 34, 9), k("Glasswing Darter", 8)],
        "Course record. Mine. Nobody has touched it in eleven years, and that is because nobody has "
        "driven the course in three, which I am aware of, and which does not take it off me.\n\nGo out "
        "to the north turn. There is a marker stone there with a time cut into it and I want to know "
        "whether it is still legible, because I am not going out to look and I am not going to explain "
        "why.\n\nThe darters are all over that leg. Eight of them while you are up there.",
        "Legible.\n\nGood. That is good.\n\nI will tell you the thing I do not say in the inn. A "
        "record is not a thing you hold, it is a thing people are trying to take, and the day they "
        "stopped trying it stopped being a record and became a number on a rock.\n\nTozzik posted a "
        "new time this week. Worse than mine by a long way. Best morning I have had in a long time.", salt="f"))

    A.append(Q("swf_solo_lead", "Sealed in Lead, and Charged For", NISSA, SW, 35, 36, "inn",
        "Salt air ruins a cork in a season, so Brewer Nissa Tolk seals everything in lead and charges "
        "you for the lead.\n\nShe has heard what they say about lead. She would like you to drink it "
        "fast.",
        [gather("sf_scorpid_barb", 6), k("Crustback Scorpid", 9)],
        "Everything I make dies in a cork out here. Nine of them off the drying ground and six barbs - the sheath keeps the venom wet in air that dries everything else, and if I can get at "
        "what the sheath is doing I can stop sealing in lead and stop charging you for it.\n\nI would "
        "like to stop charging you for it. I would like that on the record.",
        "Whatever is in the sheath, it is not a coating, it is the structure.\n\nWhich means I cannot "
        "copy it with what I have on this bench and I will be sealing in lead for another year at "
        "least.\n\nStill. Knowing I cannot do a thing is worth something. It is worth less than doing "
        "it. I will take it."))

    A.append(Q("swf_solo_crew", "Four Hands and No Race", GRIZZIK, SW, 37, 38, "dustwheel",
        "Pit-Boss Grizzik Vane keeps four hands on the payroll for a race that has not run since the "
        "Integration.\n\nTozzik pays half. She pays half. Neither has said out loud what they are "
        "paying for.",
        [k("Dustwheel Wheelman", 8), gather("sf_course_wheel", 5), gather("sf_salvage_tag", 4)],
        "My crew have not touched a running machine since the track died and two of them have started "
        "forgetting things that cannot be relearned off a book.\n\nSo I am sending you out to bring me "
        "work. Eight of the wheelmen, five wheels, four tags. The wheels go on my benches and my hands "
        "strip them and rebuild them and put them on a shelf, and then I pay them.\n\nIt is not a "
        "race. It is hands staying hands.",
        "They had all five apart before I finished telling them what they were.\n\nOne of them cried "
        "about it, in the shed, where he thought I could not see, and I let him, and then I handed him "
        "the second one.\n\nThat is my whole management philosophy and it has never once failed me."))

    A.append(Q("swf_solo_shrinking", "By How Much, Exactly", WINNOW, SW, 38, 39, "saltline",
        "Every cart in, every cart out, every barrel of salt, written down twice.\n\nTally-Clerk "
        "Winnow is the least popular person in Saltwheel because she is the only one who can answer "
        "the question the town asks itself at night.",
        [gather("sf_tunnel_spoil", 7), gather("sf_vulture_quill", 5), talk("swf_topic_shrinking")],
        "I need spoil and quills - the spoil to weigh against last year's and the quills to write with, "
        "because I have used mine up and the general goods has stopped stocking them.\n\nThat last "
        "part is a data point and I have recorded it.\n\nThen ask me the question. Everyone wants to "
        "and nobody does, and I would like, once, to be asked rather than avoided.",
        "By a quarter, over three years, in bodies. In trade it is worse and I will not say the "
        "figure because the figure is not mine to hand to a stranger.\n\nPeople think I keep this book "
        "to be unpleasant. I keep it because when a place goes, it goes without anybody writing down "
        "what was in it, and I have decided that is not happening here.\n\nThat is all. You asked. "
        "Nobody asks."))

    # ---- ITEM-STARTERS. Second-person narration: you picked it up and turned it over. ---------------
    A.append(Q("swf_item_entry_slip", "The Name Has Been Rewritten Twice", "item:sf_entry_slip", SW,
        36, 37, "raceday",
        "You turn the slip over. An entry for the Saltwheel Open, three seasons out of date, with the "
        "name scratched out and written in again twice - the same hand each time, pressing harder "
        "every go.\n\nSomebody entered, withdrew, entered, withdrew, and entered again, and then the "
        "race did not happen.",
        [deliver("sf_entry_slip", "Race-Marshal Tozzik Brasswheel, Saltwheel"), k("Dustwheel Wheelman", 7)],
        "The gantry is where entries are taken and the man under it takes them whether or not anybody "
        "brings him one.\n\nSeven of the wheelmen on your way in - they are on the straight at this "
        "hour and they will not step aside for somebody carrying paper.",
        "[Tozzik reads it, and reads it again, and does not look up.]\n\nThat is his hand. He entered "
        "the year it died and pulled out, and entered, and pulled out, and entered.\n\nI never "
        "processed the third one. It came in after the date and I am a man who keeps the date, so I "
        "put it in a drawer and I said nothing, and he has spent three winters believing nobody wanted "
        "him on the line.\n\nNazzik is in the inn. I am not going over there tonight. Tomorrow. I will "
        "go tomorrow and that is not a thing I am saying to get out of it.", salt="b"))

    A.append(Q("swf_item_sealed_tin", "Something Is Still Dry Inside", "item:sf_sealed_tin", SF,
        38, 39, "water",
        "You turn the tin over. Lead-sealed at every seam, dug up out of pan that has been bone dry "
        "for longer than anyone has been counting.\n\nIt rattles. Whatever is in it has never once "
        "been wet.",
        [explore(SF, 86, 92, 9), gather("sf_tunnel_spoil", 6), deliver("sf_sealed_tin",
                                                                      "Brewer Nissa Tolk, Saltwheel")],
        "The tunnelers bring these up and leave them, which means there are more, which means somebody "
        "was sealing things in lead on this pan before anybody in Saltwheel was born.\n\nGo back to "
        "where the spoil comes up on the Brine and bring six loads with you, and then put the tin in "
        "front of the only person in town who seals things in lead.",
        "[Nissa holds it up to the lamp and turns it slowly, and does not open it.]\n\nMy seam. Not my "
        "work - my SEAM, the double fold, which my mother taught me and which her people brought here "
        "from somewhere else entirely and which I have never seen on anything I did not make.\n\nIt "
        "came up out of ground that has been dry for a very long time.\n\nI am not opening it in front "
        "of you. I am not opening it tonight. Come back in the spring and I will tell you what my "
        "family was doing under this pan before there was a town on it.", salt="c"))

    return A


# ---------------------------------------------------------------------------------------------------
def audit(quests):
    """The spread checks. A pass that pays out eleven plate chests is a pass thirty classes cannot use."""
    import collections
    bad = []
    arm = collections.Counter()
    wep = collections.Counter()
    for q in quests:
        for it in q.get("unique_item_defs", []):
            if it.get("armor_type"):
                arm[it["armor_type"]] += 1
            if it.get("weapon_type"):
                wep[it["weapon_type"]] += 1
    tot_a = sum(arm.values())
    for t in ("cloth", "leather", "mail", "plate"):
        share = arm[t] / tot_a if tot_a else 0
        if not 0.17 <= share <= 0.33:
            bad.append(f"armour {t} is {share:.0%} of {tot_a} pieces (want 17-33%)")
    tot_w = sum(wep.values())
    for t, n in wep.items():
        if tot_w and n / tot_w > 0.34:
            bad.append(f"weapon type {t} is {n / tot_w:.0%} of {tot_w} weapons (want under 34%)")
    # the level rules, not preferences
    for q in quests:
        for it in q.get("unique_item_defs", []):
            res = [k_ for k_ in (it.get("secondary_stats") or {}) if "resistance" in k_]
            if res:
                bad.append(f"{q['quest_id']}: {it.get('name')} has resistance stats below level 45")
    # the standing rules
    rares = {"Scourbite", "Gearjaw", "Rustcoat", "Hollowcrust", "Paneater"}
    for q in quests:
        for o in q["objectives"]:
            if o.get("target") in rares:
                bad.append(f"{q['quest_id']}: objective targets the named rare {o['target']}")
            if o["type"] == "escort" or "escort" in str(o).lower():
                bad.append(f"{q['quest_id']}: escort objective")
        for f in ("description", "accept_text", "turn_in_text"):
            if "escort" in q[f].lower():
                bad.append(f"{q['quest_id']}: the word 'escort' in {f}")
            if len(q[f]) > 760:
                bad.append(f"{q['quest_id']}: {f} is {len(q[f])} chars (hard cap 760)")
            if not q[f].isascii():
                bad.append(f"{q['quest_id']}: {f} is not ASCII")
    # every fetch/gather/deliver item must have a source or be granted
    sourced = {i for rows in FETCH_DROPS.values() for (i, *_r) in rows}
    sourced |= {i for rows in STARTER_DROPS.values() for (i, *_r) in rows}
    # THE GRANT IS CHECKED, NOT ASSERTED. This used to be a hardcoded set of two item ids declared
    # "handed over by the giver" - and neither of them was, because nothing in main() granted them.
    # Both quests shipped uncompletable and this check waved them through, which is worse than no
    # check: it reported all-clear on the one thing it existed to catch. It now reads the quest's
    # own grant_items.
    for q in quests:
        granted = {g["item_id"] for g in (q.get("grant_items") or {}).get("on_accept", [])}
        granted |= {g["item_id"] for g in (q.get("grant_items") or {}).get("on_turn_in", [])}
        for o in q["objectives"]:
            if o["type"] in ("fetch", "gather", "deliver"):
                t = o.get("target")
                if t not in sourced | granted | set(STARTER_IDS):
                    bad.append(f"{q['quest_id']}: {o['type']} '{t}' has no drop source and the quest "
                               f"does not grant it - uncompletable")
    return bad


def main():
    quests = build()
    ids = [q["quest_id"] for q in quests]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids")
        return 1

    # chain targets and gates must point at something real
    here = set(ids)
    far = {ASP_WATER, FW_WATER}
    for q in quests:
        nx = q.get("next_quest_id")
        if nx and nx not in here:
            print(f"FAILED: {q['quest_id']} chains to {nx}, which this pass does not define")
            return 1
        for r in q.get("requires_quests", []):
            if r not in here | far:
                print(f"FAILED: {q['quest_id']} requires {r}, which is not a known quest")
                return 1
    # and the far ones must actually exist in their own zones' files, or the gate never opens
    for f, qid in (("data/quests/aspen.json", ASP_WATER),
                   ("data/quests/southern_needles.json", FW_WATER)):
        d = json.loads((ROOT / f).read_text(encoding="utf-8"))
        have = {q["quest_id"] for q in (d["quests"] if isinstance(d, dict) else d)}
        if qid not in have:
            print(f"FAILED: the water gate requires {qid}, which is not in {f}")
            return 1
    print(f"water gate: {ASP_WATER} + {FW_WATER}, both live in their own zones")

    bad = audit(quests)
    if bad:
        print("\nFAILED - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    OUT.write_text(json.dumps({"quests": quests}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    # drops: a fetch item nothing drops is a quest nobody can hand in
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for cre, rows in list(FETCH_DROPS.items()) + list(STARTER_DROPS.items()):
        have = {r["item_id"]: r for r in drops.get(cre, [])}
        for row in rows:
            iid, nm, desc, ch = row
            rec = {"item_id": iid, "name": nm, "category": "quest", "description": desc, "chance": ch}
            if iid in STARTER_IDS:
                rec["starts_quest_id"] = STARTER_IDS[iid]
            have[iid] = rec
        drops[cre] = list(have.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    chains = sum(1 for q in quests if q.get("next_quest_id"))
    gated = sum(1 for q in quests if q.get("requires_quests"))
    starters = sum(1 for q in quests if str(q["giver_npc_id"]).startswith("item:"))
    hist = {}
    for q in quests:
        for o in q["objectives"]:
            hist[o["type"]] = hist.get(o["type"], 0) + 1
    print(f"Shimmering Flats quests: {len(quests)} total, {chains} chained links, {gated} gated, "
          f"{starters} item-starters")
    print("  objectives: " + ", ".join(f"{k_} {v}" for k_, v in sorted(hist.items(), key=lambda kv: -kv[1])))
    print("  zones touched: " + ", ".join(sorted({q["zone"] for q in quests})))
    print(f"  drops: {sum(len(v) for v in FETCH_DROPS.values())} fetch sources, "
          f"{sum(len(v) for v in STARTER_DROPS.values())} starters")
    return 0


#: starter item -> the quest it opens
STARTER_IDS = {"sf_entry_slip": "swf_item_entry_slip", "sf_sealed_tin": "swf_item_sealed_tin"}


if __name__ == "__main__":
    sys.exit(main())
