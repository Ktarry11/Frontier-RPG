"""
Booty Bay + Southern Stranglethorn + The Drowned Shrine quest pass (2026-10-30).  Idempotent.

    PYTHONPATH=. python3 tools/build_stranglethorn_south_quests.py
    PYTHONPATH=. python3 tools/build_quest_text.py stranglethorn_south
    PYTHONPATH=. python3 tools/audit_quests.py

Writes data/quests/stranglethorn_south.json, regenerates the overlay source at
tools/quest_text_src/stranglethorn_south.txt from the same strings (so the two can never drift), and
fills data/factions/factions.json -> booty_bay_authority -> quest_rep.capstones with the three quests
that actually are capstones.  It touches NOTHING else: not the handbuilt zones, not creatures, not
loot, not quest_drops.json, and it appends no NPCs.  Every giver below already exists with a written
greeting in data/npcs/ambient_npcs.json or data/npcs/vendors.json and is used in character.

NO ESCORTS (Kyle's standing rule, and the only hard "never" in quest design).
NO QUEST BUILT AROUND A NAMED RARE.  Southern Stranglethorn has three - The Cargo on the spit, Ssaren
the Salvage-Taker in the ruin, Captain Orlee Vantch on the beach - and Saltgorge is a fourth, pinned
inside the cave's pillar court.  None of them is an objective.  They are weather.  The only kill_boss
in the pass is Tide-Priestess Myzrai, who is the Drowned Shrine's boss, not a rare.

OBJECTIVE TYPES USED: kill, kill_boss, explore, deliver.  Deliberately NOT used, and why:
  fetch/gather  every fetch item in this band would need a row in data/creatures/quest_drops.json,
                which this pass is not allowed to write (three agents are working Stranglethorn in
                parallel and that file is a read-modify-write).  A fetch objective whose item nothing
                drops is a quest that can never be handed in, so there are none.  FETCH_DROPS at the
                bottom of this file is the table a later pass should splice; --with-drops writes it
                and is OFF by default.
  dialogue      topic text lives in world/quest_dialogue.py, which this pass may not touch, and a
                dialogue objective with no authored topics renders zero buttons.
  craft         no carpentry recipe exists at this band that is not a high-tier bar, and high-tier
                crafting material before 60 is a standing rule.

=========================================================================================================
THE ZONE'S ONE IDEA, AND EVERY QUEST SERVES IT:
            THE HARBOUR SELLS PEACE BY THE WEEK, AND EVERYBODY STANDING ON THE BOARDS IS PAYING.
=========================================================================================================

Booty Bay is not a town with a tariff problem.  It is a tariff with a town built on it.  When the land
road south turned to rock the cove stopped being one of the Steamwheedle Cartel's franchises and became
the only deep-water harbour still joining anything to anything, and a harbour in that position stops
taking instructions.  Gazlowe signs the manifests in Ratchet.  Baron Revilgaz decides what sails.
Factor Weezel files the Cartel's paperwork every week and gets a polite reply that changes nothing.

The player arrives on a goblin boat and owes a landing fee before their boots touch the boards.  By the
fifth quest in that thread they should understand that fee differently: it is not a tax, it is the
bruisers, and the bruisers are the only reason two enemies can tie up at one pier and nothing happens.
What the Authority sells is a pier where nothing happens.  Nizzik takes the money for it at the top of
the ramp and does not care one way or the other who you are, which in this town is a kindness and is
not meant as one.

THE EARTH-TRANSPLANT UNDERCURRENT, AND THE FLAVOUR ONLY THIS TOWN HAS.  Thirteen of the twenty quests
carry it.  Goblins do not care where your money came from - the Authority will take your coin and your
labour without a flicker - and the people who actually lost something to the Integration are standing
on the same boards watching that happen.  Commercial indifference and private grievance in one town is
the version of this that nowhere else can do.  It is never the subject.  It shows up as:
  * Nizzik not writing down where anyone is from, and saying so as a fee schedule
  * Weezel assuming you cannot read a Cartel seal, being from where you are from
  * Sprocket asking where you were when it happened and not waiting for the answer
  * Zan'rek correcting your word for the ruin.  Twice.  He has a name for it.  Several
  * Scrip asking whether it is true that carts move without animals where you come from, flat
  * The Quiet Man, who knew which boat and knew which year
  * Keeper Marla, who is warmly, openly fine with you, and is the exception that makes the rest read
    as deliberate

THE SPINE - THREE GENERATIONS OF TROLL STONEWORK, AND THIS IS THE END OF IT.  Northern raises the
question at Zul'Marosh (abandoned, not understood).  Central answers part of it at the Gurbashi arena
(the living one).  Zul'Kundaraz is the biggest and it is drowned, and the answer is a FACT about the
place rather than a speech: the lowest terrace was CUT FOR THE TIDE.  The halls were built to flood.
The survey grid of the Drowned Shrine's wall-tops is the same module as the arena floor and the same as
Marosh's courts, which is how Wind-Rider Zekki gets at it from the air; and the Tidecallers down there
are not naga hangers-on, they are Kundaraz, still calling the water in because that was always the job.
The sea did not take Zul'Kundaraz.  Zul'Kundaraz was given the sea, and then the sea came a hand and a
half further than it was given, and Lookout Minzi can tell you in what year.

VARIED SHAPES, because twenty quests from one town is exactly how twenty quests end up being one quest:
  a census disguised as a toll (Nizzik), a test of honesty disguised as a headcount (the Baron), a liar
  whose turn-in is in another zone (Weezel, handed in to Ratchet customs), a cross-zone errand given by
  Gazlowe and stamped in the wrong box on purpose, an aide acting without authority (Fipple), a favour
  asked by a woman in a cage whose whole payment is information (Oona), a bet that exists to avoid
  admitting a mistake (Durgo), a street kid selling you something so he can resell it (Scrip), a fence
  buying back his own reputation (The Quiet Man), a measurement that is the lore (Zekki), a date said
  twice (Minzi), and one plain warm favour with nothing under it at all (Marla).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill              # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/stranglethorn_south.json"
TXT = ROOT / "tools/quest_text_src/stranglethorn_south.txt"
FACTIONS = ROOT / "data/factions/factions.json"

#: Quest `zone` values.  These are the keys data/factions/factions.json ->
#: booty_bay_authority -> quest_rep.zones matches on, so a quest that pays the Authority must carry one
#: of these two and nothing else.
BB = "booty_bay"
SS = "stranglethorn_south"
#: EXPLORE targets and kill-zone restrictions are the LIVE ZONE KEY, which is the slug of the map's own
#: NAME (world/zone_manager.py: new_zone.name.lower().replace(" ","_").replace("'","")).  For this zone
#: that is NOT "stranglethorn_south" - the handbuilt file's KEY and the map's name disagree, and writing
#: the KEY here would silently never match record_zone_entered.  Checked by audit() and audit_quests.py.
SSK = "southern_stranglethorn"
DSK = "the_drowned_shrine"

XP = {38: 2830, 39: 2920, 40: 3010, 41: 3100, 42: 3190}
GOLD = {38: 11100, 39: 11400, 40: 11700, 41: 12000, 42: 12300}

#: Named rares in this slice.  Lore and loot, never an objective - and the audit enforces it rather
#: than trusting the twenty quests below to have remembered.
RARES = ("The Cargo", "Ssaren the Salvage-Taker", "Captain Orlee Vantch", "Saltgorge")

# The slice's gear flavour.  Five pools: the boards, the pirates on the water, the ruin in the vine,
# the drowned terraces, and the spit.  Nothing here is Earth-made and nothing here IS from Earth -
# everything that came across came across in somebody's hands, and this is a harbour, so most of it
# came off a boat that was going somewhere else.
tirisfal_gear.THEMES.update({
    "harbour": (["Pierhead", "Tollpost", "Bruiser's", "Piling-Set", "Lagoon-Damp", "Baron's"],
                ["Came off a boat that was going somewhere else. Most things here did.",
                 "Three years of salt in the stitching and a goblin price on the label.",
                 "Mended twice on the boards, both times badly, both times cheap.",
                 "Smells of tar, tide and somebody else's cargo.",
                 "Stamped by the Authority, which here means stamped by one man."]),
    "bloodsail": (["Bloodsail", "Powder-Burned", "Bosun's", "Scuttler's", "Wrackline", "Six-Gun"],
                  ["Powder has gone into the weave and will not come out of it.",
                   "Taken off somebody who was taking something off somebody else.",
                   "Cut for a man who expected to spend his life wet.",
                   "A crew's mark inside the collar, scratched over twice.",
                   "It was on a bar at low water with the owner still in it."]),
    "kundaraz": (["Kundaraz", "Stoneshaper's", "Terrace-Cut", "Vine-Taken", "Course-Set", "Coursework"],
                 ["The vine had it. The vine has had everything here for a long time.",
                  "Troll work, and the courses are laid to a module somebody still remembers.",
                  "Found in a court with a tree growing through the floor of it.",
                  "Cut stone dust in every seam, and the dust is the same grey as the arena's.",
                  "Older than the port and it will outlast the port."]),
    "tidewrack": (["Saltscale", "Tide-Called", "Drowned Court", "Myrmidon's", "Hand-And-A-Half",
                   "Hall-Flooded"],
                  ["It was under salt water long enough to stop minding.",
                   "Salt has set hard across it in a crust that rings when you knock it.",
                   "Off a terrace that was cut to be under water, which is the part nobody believes.",
                   "The naga had it sorted into a pile. They sort everything.",
                   "Dripping when it came up and dripping still, a week later."]),
    "spit": (["Jaguero", "Pit-Stock", "Sandbar", "Spit-Found", "Castaway's", "Palm-Shade"],
             ["Sand in it that no amount of beating gets out.",
              "It went out to the spit with something and the something stayed.",
              "Bleached on the open sand for a season and a half.",
              "Landed off a boat, held, fed, and never sent for.",
              "The walk out there is the same as the walk back. This did neither."]),
})


# --------------------------------------------------------------------------------------- objectives
def k(target, n, zone=SSK):
    """A kill, restricted to a live zone key by default - every one of these creatures is spawned in
    more than one subzone and a couple of them in the cave as well."""
    return kill(target, n, zone=zone)


def boss(target, zone=DSK):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x, y, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None,
      **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    # Four choices on a boss or a capstone, three everywhere else.  The fourth slot is always armour
    # (tirisfal_gear.specs's plan), so this is also the lever the audit's armour-spread check is
    # tuned against - see audit().
    n = 4 if (is_boss or qid in CAPSTONES) else 3
    pack = reward_pack(qid, theme, ilvl, lo, rarity, n)
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             # BOTH KEYS, SAME LIST.  world/quest_manager.py._build_quest reads "unique_item_defs" and
             # nothing reads "rewards" - the Southern Needles pass wrote only "rewards" and shipped
             # twenty quests whose authored gear the engine never saw.  Caught on this pass.
             rewards=pack, unique_item_defs=pack)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# Booty Bay givers (data/npcs/ambient_npcs.json + data/npcs/vendors.json, zone booty_bay).
NIZZIK = "bootybay_toll_collector"      # Tollkeeper Nizzik
BARON = "bootybay_baron"                # Baron Revilgaz
FIPPLE = "bootybay_baron_aide"          # Aide Fipple
WEEZEL = "bootybay_cartel_factor"       # Factor Weezel
SPROCKET = "bootybay_harbourmaster"     # Harbourmaster Sprocket
KOLK = "bootybay_gate_guard"            # Bruiser Kolk
MINZI = "bootybay_lookout"              # Lookout Minzi
BREK = "bootybay_dockmaster"            # Dockmaster Brek
DURGO = "bootybay_crane_hand"           # Crane-Hand Durgo
VELLA = "bootybay_shipwright"           # Shipwright Vella
QUIET = "bootybay_fence"                # The Quiet Man
OONA = "bootybay_bloodsail_captive"     # Dagger-Hand Oona
ZANREK = "bootybay_troll_pilot"         # Pilot Zan'rek
SCRIP = "bootybay_street_kid"           # Scrip
ZEKKI = "bootybay_flight_master"        # Wind-Rider Zekki
MARLA = "bootybay_tavern_keeper"        # Keeper Marla (vendor)
GURGLE = "bootybay_fishmonger"          # Gurgle (vendor)
# the other end of the tariff argument, and the other end of the supply line
GAZLOWE = "ratchet_gazlowe"             # Gazlowe, Ratchet - he signs the manifests
PRYNN = "ratchet_customs_officer"       # Customs Officer Prynn, Ratchet - she has a drawer
ZEKKA = "gromgol_berth_master"          # Berth-Master Zekka, Grom'gol - Northern's zone, not my file


# =========================================================================================================
# THE TARIFF - the landing fee, the Baron, the Cartel, and the argument with Ratchet.  38-42.
# The zone's political spine, and the one chain that has to REVERSE: by the last quest the fee the
# player paid in the first one is a different object.
# =========================================================================================================
def tariff():
    A = []
    A.append(Q("bb_landing_fee", "Landing Fee", NIZZIK, BB, 38, 38, "harbour",
        "Tollkeeper Nizzik sits halfway down the only ramp into Booty Bay, which means she does not "
        "have to chase anybody for anything. Four silver to set foot on the boards, or four hours of "
        "work, and she will take either without preference.\n\nThe four hours are not made up to "
        "punish you. The cart track on the apron above the gate has raptors on it that have learned a "
        "crate means food, and the carters have started leaving loads at the treeline rather than "
        "argue with them.",
        [k("Capecrest Raptor", 8), explore(SSK, 36, 150, 7)],
        "Landing fee. You have already landed, so we are only arguing about the amount, and I will "
        "save you the trouble: it is four silver and it has been four silver since the road closed.\n\n"
        "No coin, then work. Go back up the ramp and clear the apron. Eight of them off the cart track "
        "and walk the whole apron, not the first ten yards of it. I will mark you paid when the carters "
        "stop leaving loads in the trees.",
        "Paid. You are on the boards and nobody can put you off them, which is the whole of what you "
        "bought.\n\nAnd before you ask: no, I did not write down where you came in from. The Baron has "
        "never asked me to and I have never offered. The fee is the same whoever is holding it out. "
        "That is not a courtesy, it is a schedule, but you will not get even the schedule in Ratchet.",
        nxt="bb_barons_name"))

    A.append(Q("bb_barons_name", "Nothing Leaves This Cove", BARON, BB, 38, 39, "harbour",
        "Baron Revilgaz does not rule Booty Bay. He decides which hulls leave on which tide, which "
        "after three years turns out to be the same thing, and he has never once said the word out "
        "loud.\n\nThere is a Bloodsail camp on the south beach and he wants a number off it. He has "
        "already been given four numbers by four people with four reasons to shade them.",
        [explore(SSK, 105, 150, 8), k("Bloodsail Swab", 10)],
        "You will not know how a harbour works, so I will do this slowly. A hull that does not arrive "
        "costs me the cargo, the berth, and the next three captains who hear about it. Pirates are not "
        "a romance down here, they are a column.\n\nThere is a camp on the sand at the far end of the "
        "shallows. Go and stand in it and count what is standing up. Then come back and tell me the "
        "number you counted, not the number you think I want.",
        "Forty-one. I had forty-one from the harbourmaster on Tuesday and I have had thirty, sixty and "
        "a hundred from people who wanted something.\n\nSo you can count and you will say a number that "
        "does not flatter anybody. That is rarer on these boards than courage and I pay better for it. "
        "Go and see Weezel. He has been waiting three years for somebody who will listen.",
        nxt="bb_weezels_paperwork"))

    A.append(Q("bb_weezels_paperwork", "The Company Has Not Lost This Port", WEEZEL, BB, 39, 40,
        "harbour",
        "Factor Weezel has an office on the upper gallery, a seal, a ledger, and the Steamwheedle "
        "Cartel's authority over this harbour, and he will tell you at length that none of those has "
        "been formally withdrawn.\n\nHe is right about the law and he knows exactly what the law is "
        "worth on these boards. What he wants is a complaint carried to Ratchet by somebody who is not "
        "on the Baron's payroll, and a countersigned reply brought back, which he says will settle it.",
        [deliver("weezel_complaint", "Put the Cartel's complaint in Customs Officer Prynn's hand")],
        "Forty-first week. The harbour book that the Baron's clerk keeps is not a legal instrument, it "
        "is a diary, and I have said so in writing every week since the road closed.\n\nTake this to "
        "Ratchet and put it in front of customs. They will countersign it and that countersignature is "
        "the whole port. You would not know a Cartel seal from a wax blot, which is why you are perfect "
        "for the errand: nobody will search a courier who cannot read what they are carrying.",
        "Prynn turns it over, finds the seal, and puts it in the second drawer without opening the "
        "letter.\n\nFortieth. Forty-first. I countersign every one of them, because signing costs me "
        "nothing and refusing would cost me an afternoon.\n\nAnd look at the seal he gave you, since he "
        "told you that you could not. That device was retired two years ago. Weezel knows that. He has "
        "known it longer than I have, and he keeps pressing it because a retired seal is still a seal "
        "to anyone who does not look.",
        turn_in_npc_id=PRYNN, nxt="bb_what_actually_sails",
        grant_items=carry("weezel_complaint", "The Cartel's Complaint",
                          "Sealed, and the seal is the interesting part. Nobody has opened one of "
                          "these in Ratchet for about eight months.")))

    A.append(Q("bb_what_actually_sails", "What Actually Sails", GAZLOWE, "ratchet", 40, 41, "harbour",
        "Gazlowe signs every manifest that leaves Ratchet and has signed the southern ones the whole "
        "three years, and the southern ones are the only paper in the drawer that has never come back "
        "stamped by anybody.\n\nHe is not interested in who owns Booty Bay. He wants a stamp on a "
        "season's manifest from whoever is actually deciding, because an unstamped season is a season "
        "he cannot bill for, and he would like it on the record that he asked.",
        [deliver("ratchet_season_manifest", "Get the season's manifest stamped by Baron Revilgaz")],
        "Six hundred and twelve tons, Ratchet to the cove, this season. Every ton of it signed by me "
        "and not one ton of it acknowledged by anyone at the other end.\n\nCarry it down and get it "
        "stamped. I do not care whose stamp. I care that there is one, in the box, with a date beside "
        "it, because when somebody finally asks which of us has been running that harbour I want the "
        "answer to be in handwriting that is not mine.",
        "The Baron reads the whole manifest, which takes a while, and then stamps it.\n\nReceived. "
        "Look where I put it. The box says received, not approved, not cleared. Received.\n\nSix "
        "hundred and twelve tons received. Say the word back to me so I know you have it, because "
        "Gazlowe will read that box and he will understand it perfectly, and he will not be able to "
        "write a single angry letter about a word that means nothing at all.",
        requires_quests=["bb_weezels_paperwork"], turn_in_npc_id=BARON, nxt="bb_the_fee_explained",
        grant_items=carry("ratchet_season_manifest", "The Season's Manifest",
                          "Six hundred and twelve tons in Gazlowe's own hand, with an empty box at the "
                          "bottom of it that has been empty for three years.")))

    A.append(Q("bb_the_fee_explained", "What the Fee Was For", NIZZIK, BB, 41, 42, "harbour",
        "Nizzik is putting the landing fee up on the Ratchet boat specifically, by order, with a date, "
        "and she has been told to expect the small hulls to start beaching on the sand south of the "
        "cape rather than come up the ramp and pay.\n\nThey already have. Bloodsail bosuns are taking "
        "a cut off every keel that lands there, which means the dodgers are paying a worse toll to a "
        "worse collector, and Nizzik finds that funnier than she should.",
        [k("Bloodsail Bosun", 8), explore(SSK, 56, 141, 8)],
        "Up a silver on the Ratchet run from the first tide of next month. Not my decision and I would "
        "have made the same one.\n\nThe ones dodging it are beaching on the shallows and handing the "
        "difference to a bosun with a knife, which is the market working. Go and break that up anyway. "
        "Walk the beach track while you are down there so the carters can see it being walked.",
        "Done, and they will come back up the ramp and complain to me about the silver.\n\nYou want to "
        "know what you bought with your four. The bruisers. That is all the fee has ever been. Two "
        "enemies tie up at the same pier in this cove and nothing happens to either of them, and the "
        "nothing is bought by the week, and the week is never paid up more than a week.\n\nThat is why "
        "I do not write down where anybody came from. A list like that is a thing somebody uses later.",
        requires_quests=["bb_what_actually_sails"]))

    A.append(Q("bb_fipples_decision", "The Baron Is Reviewing It", FIPPLE, BB, 39, 40, "harbour",
        "Aide Fipple has told four hundred people that the Baron is reviewing it. He has said it so "
        "often that he has stopped hearing it, which is roughly when a clerk starts making "
        "decisions.\n\nGrom'gol's berth grant has been on the Baron's desk eleven weeks. The camp needs "
        "it to land a second airship hull on Authority water. Fipple has dated the Baron's own stamp "
        "and is sending it north himself, and he would like it to arrive before anyone notices.",
        [deliver("fipple_berth_grant", "Carry the berth grant to Berth-Master Zekka at Grom'gol")],
        "Eleven weeks. I have counted. I have counted it on a wall, which I understand is not a good "
        "sign.\n\nIt is his stamp. I did not forge the stamp, I dated the stamp, and the date is the "
        "date he should have put on it. Take it up the Cape Road to the camp and give it to the "
        "berth-master, and if anybody down here asks you what you are carrying, you are carrying "
        "nothing and you have never met me.",
        "Zekka reads it twice, then goes and gets another one out of a box and lays the two side by "
        "side.\n\nThree weeks ago. Came down with a wind-rider, different hand, same stamp, same "
        "grant.\n\nSo your clerk has spent eleven weeks thinking his Baron is slow. He is not slow. He "
        "sent this three weeks ago and let the boy keep counting on his wall, and he will have had a "
        "reason, and the reason will not be a kind one. Do not tell him. Or tell him. I have a berth "
        "either way.",
        turn_in_npc_id=ZEKKA,
        grant_items=carry("fipple_berth_grant", "Grom'gol's Berth Grant",
                          "The Baron's stamp, and a date under it in a much smaller hand than the "
                          "stamp was cut for.")))
    return A


# =========================================================================================================
# THE BLOODSAIL SHALLOWS - pirates cost the harbour money, which is exactly what the Authority pays
# for.  38-42.  Captain Orlee Vantch is out there and is never an objective.
# =========================================================================================================
def bloodsail():
    A = []
    A.append(Q("bb_three_wrecks", "Three Wrecks and Who Put Them There", SPROCKET, BB, 38, 39,
        "bloodsail",
        "Harbourmaster Sprocket's tower keeps tide, berth, weather, and who is lying about which. "
        "Three hulls are sitting on the bars off the south coast where anyone coming into the cove can "
        "see them, which he says is the point of where they are.\n\nTwo of the three are his, lost in "
        "one season to the Bloodsail. The third one is the one that keeps him up. It is older than the "
        "other two and it is aground on a bar that was not there three years ago.",
        [explore(SSK, 68, 161, 8), k("Bloodsail Cannoneer", 6)],
        "Walk out on the bars at low water. You can do it, that is what a bar is, and the cannoneers "
        "will shoot at you the whole way, so thin them first or be fast.\n\nI want the third wreck "
        "looked at. Not the two fresh ones, I know what is in those. The old one, out on the east bar. "
        "Where were you when the ground changed? Never mind. Nobody was anywhere useful. Just go and "
        "look at the hull and come back.",
        "Cartel colours under the barnacle. I thought so and I hoped not.\n\nThat hull went north out "
        "of this cove with company coin in it three years ago and never arrived, and the bar it is "
        "sitting on did not exist when it sailed. So either it hit something that was not there yet or "
        "somebody put it there afterwards.\n\nAnd in three years Factor Weezel, who files a complaint "
        "about a diary every single week, has not once asked me about a missing hull with his own "
        "company's money in it.",
        nxt="bb_oonas_name"))

    A.append(Q("bb_oonas_name", "Dagger-Hand Oona", OONA, BB, 39, 40, "bloodsail",
        "Dagger-Hand Oona has been in the holding cage on the lower gallery for most of a year. They "
        "have not hanged her and they have not let her go, and she has worked out that this is because "
        "the Baron has not yet decided which of those is worth more.\n\nShe is not asking to be let "
        "out. She wants one name off one body, and she is offering to pay in the only currency she has "
        "left, which is what she knows about the water.",
        [k("Bloodsail Bosun", 6), explore(SSK, 94, 151, 8)],
        "There is a bosun on that beach who sold me to these people for a boat and a share. I am not "
        "going to tell you which one he is, because you will take six of them and one of them will be "
        "him and I will sleep.\n\nGo and walk through the camp while you are at it. And do not look at "
        "me like that. You people came in on boats that came out of the sky. Mine came out of a "
        "shipyard in Kul Tiras. We are both standing in a goblin port a long way from where we started "
        "and only one of us is in a cage, so spare me.",
        "Six. Good.\n\nNow listen, because this is what I owe you and I pay what I owe. The Bloodsail "
        "do not hold that beach. They hold the water. The camp on the sand is a lure and it is meant "
        "to be counted - that is why it is pitched where the tower can see it.\n\nEverything that "
        "matters to them is afloat and off the bars, and the Baron has been buying headcounts of a "
        "camp for three years. Sell him that. Do not give it to him.",
        nxt="bb_hold_the_water"))

    A.append(Q("bb_cannon_count", "Durgo Will Bet You", DURGO, BB, 40, 41, "bloodsail",
        "Crane-Hand Durgo works the hoist at the ramp foot and will tell you that standing under it "
        "once is enough to stop you doing it twice.\n\nIn the spring he put a crate through the rail "
        "into the lagoon. The crate was powder, consigned to nobody, and the manifest it was not on is "
        "being reconciled by the Baron's clerk at the end of the season. Durgo has a theory about "
        "where that powder went and he would rather bet on it than say it.",
        [k("Bloodsail Cannoneer", 10), explore(SSK, 136, 150, 8)],
        "Twenty silver says the Bloodsail are shooting at this harbour with powder that came out of "
        "this harbour. Twenty. I will put it on the rail right now.\n\nThe lagoon shelves out east and "
        "whatever goes in off the crane comes up on the rock at the end of the south beach. Go and look "
        "at the rock, and shoot the crews while you are there, and if the kegs down there are Authority "
        "kegs you win and I will pay you and you will say nothing to anyone.",
        "He pays before you finish the sentence, in coin, off his own belt, and does not ask for "
        "detail.\n\nRight. You won. Here.\n\nNow the sensible thing is you go and tell the clerk, "
        "because a hole in a manifest is a hole, and the sensible thing and the thing I am asking are "
        "not the same thing, and I am asking. The clerk reconciles at the end of the season. I have "
        "until then to put twenty silver back on my belt."))

    A.append(Q("bb_hold_the_water", "A Pier Where Nothing Happens", BREK, BB, 41, 42, "bloodsail",
        "Dockmaster Brek has three piers, one crane, and everybody wanting the middle one. What he "
        "sells, and he is clear that it is a thing being sold, is a berth where two captains who hate "
        "each other can tie up on the same tide and nothing happens.\n\nA convoy is due to lie off the "
        "bars for one tide before it comes in. Oona's word was that the Bloodsail hold the water and "
        "not the sand, and Brek has decided to act on the word of a woman in a cage, which he will not "
        "be putting in writing.",
        [k("Bloodsail Bosun", 10), k("Bloodsail Cannoneer", 8), explore(SSK, 81, 149, 8)],
        "Four hulls, nine hundred ton together, standing off the east bar from Thursday's ebb. They "
        "have no escort because an escort costs more than the cargo is worth and the Baron did the "
        "arithmetic himself.\n\nThin the bosuns and the gun crews on the water side, not the camp. The "
        "camp can sit there and be counted. I want the Thursday tide quiet and I want the beach track "
        "walked so the carters will use it in the dark.",
        "Four hulls in, nine hundred ton, nobody hurt, and I will not be thanking you for it because "
        "that is not what this was.\n\nThat tide was bought. It was bought on Thursday and it is paid "
        "up until about Thursday, and next week somebody has to buy it again. People come down that "
        "ramp furious about four silver and then they want the harbour to hold, and it holds because "
        "the four silver buys a bruiser and the bruiser is standing there on Thursday.",
        requires_quests=["bb_oonas_name"]))
    return A


# =========================================================================================================
# ZUL'KUNDARAZ - the biggest of the three troll cities, and the one that answers the question Northern
# asks at Zul'Marosh.  39-42.  Ssaren the Salvage-Taker is in these courts and is never an objective.
# =========================================================================================================
def kundaraz():
    A = []
    A.append(Q("bb_kundaraz_road", "The Road That Climbs In", ZANREK, BB, 39, 40, "kundaraz",
        "Pilot Zan'rek brings hulls in past a reef that moves, and he does it off leading marks rather "
        "than a chart, because a chart of this coast has been wrong since the ground changed.\n\nOne of "
        "his marks is a standing stone on the upper court of the ruin inland, lined against the cape. "
        "The vine is taking it. When that stone goes he loses the only safe line into the cove from the "
        "south and the reef gets a hull a season instead of a hull a decade.",
        [k("Kundaraz Vinecutter", 10), explore(SSK, 149, 86, 8)],
        "Zul'Kundaraz. Not the ruin. It has a name, it has had the name longer than there has been a "
        "cove here, and you will say it before I tell you anything useful. Zul'Kundaraz. Again.\n\n"
        "Good. There is one road that climbs into it and the vinecutters sit on it. Clear the road and "
        "get up to the top of the climb, where the upper court opens out. My mark is the standing stone "
        "on the seaward side and I need to know how much of it the vine still has.",
        "Standing, and you cut the vine off the seaward face, which is the face I need. That is a hull "
        "a decade instead of a hull a season and you will never meet the crews it is for.\n\nAnd you "
        "said it right the second time. Zul'Kundaraz. Kundaraz is the water coming up. Not the sea, the "
        "water coming up. The city is named for the thing you people call a flood and it was named that "
        "on purpose, by the people who built it, and nobody in that port has ever once asked me what it "
        "meant.",
        nxt="bb_stoneshapers"))

    A.append(Q("bb_stoneshapers", "They Are Still Cutting", SCRIP, BB, 40, 41, "kundaraz",
        "Scrip carries crates, watches crates, and sells both services at once at a discount. He also "
        "rides out on the carters' carts up the Cape Road, which is where he gets the things he "
        "actually trades in.\n\nHe has seen the Kundaraz working stone in the great court. Not clearing "
        "it, not knocking it down for the vine. Cutting. New faces, new courses, with a crew and a "
        "rule and somebody calling the measure. He knows that is worth money and he does not know why.",
        [k("Kundaraz Stoneshaper", 8), explore(SSK, 155, 86, 7)],
        "Two silver for where to look, and you pay first, because I am eleven and not stupid.\n\nGreat "
        "court, the big flat one with the steps. There is a crew in there cutting stone and one of them "
        "stands back and says a number and the rest of them cut to it. Go and stand in that court and "
        "look at the faces they are cutting, then come back, because if it is true I am selling it to "
        "the Baron and I need somebody grown to have seen it.",
        "New faces. Fresh. Not patching, not robbing the old stuff for blocks. Cutting new, to a "
        "measure, in a city everybody down here calls empty.\n\nThat is four silver to the Baron. Five. "
        "You get a cut, you did the walking.\n\nHere, before you go. Is it true the carts move without "
        "animals where you come from? Cart boys say that. They say nothing pulls them and they go "
        "anyway. I said that is a lie and they would not say how.",
        nxt="bb_three_generations"))

    A.append(Q("bb_three_generations", "Three Hands, One Grammar", ZEKKI, BB, 41, 42, "kundaraz",
        "Wind-Rider Zekki flies the only other roost worth flying to, which means she has seen all "
        "three of the jungle's troll cities from above in one afternoon: the abandoned one in the north "
        "that nobody can read, the arena in the middle that is still in use, and this one.\n\nFrom the "
        "air the drowned terrace below Zul'Kundaraz is a survey grid, and it is the same grid as the "
        "arena floor and the same as the northern courts. She needs the courses measured by somebody "
        "standing on them, because from four hundred feet she cannot tell a module from a coincidence.",
        [explore(DSK, 46, 48, 7), k("Kundaraz Terrace-Watch", 8)],
        "Go down into the sea cave and out onto the wall-tops. The halls are flooded and the walls are "
        "the road, and where two of them cross there is a plaza wide enough to stand on. Stand on it "
        "and look at the courses. I want to know whether the blocks are cut to the same module as the "
        "arena's floor, and you will know, because you will have walked the arena.\n\nThe watch will be "
        "on you the whole way. Thin them on the shelf before you go down, not after.",
        "Same module. Three cities, three hands, one grammar, and the newest of the three is the "
        "biggest and it is under salt water.\n\nNow the part you walked on. That bottom terrace is cut "
        "for the tide. The sills are chamfered inward, the halls have overflow courses at the top of "
        "the wall, and there are weirs in the junctions. Nobody drains a hall they built to be dry.\n\n"
        "The sea did not take Zul'Kundaraz. Zul'Kundaraz was given the sea. Then the sea came a hand "
        "and a half further than it was given, and that part is new, and that part is not the masons' "
        "doing. I will file it. Mind the step on your way off the platform.",
        requires_quests=["bb_stoneshapers"]))

    A.append(Q("bb_what_the_vine_keeps", "What the Vine Keeps", QUIET, BB, 40, 41, "kundaraz",
        "The Quiet Man does not see you come in and will not see you leave, and the whole of his trade "
        "runs on that being true.\n\nTwo seasons ago he sold a buyer from the Gurbashi a set of cut "
        "stones out of Zul'Kundaraz, took the money, and arranged the carry. The carry never left the "
        "courts. A gorilla troop moved onto the stones and has been living on them since, and the "
        "buyer has been telling people, which is the only part that costs him anything.",
        [k("Stonecourt Gorilla", 8), explore(SSK, 178, 68, 7)],
        "I sold something I had not yet picked up. Everyone in my line does it and most of us get away "
        "with it.\n\nThe east shoulder of the ruin, high side, round past where the courts stop. There "
        "is a stack of dressed blocks "
        "under a troop that has decided the warm stone is theirs. Clear them off it and stand on the "
        "terrace long enough to be able to describe the stack, and I will have a carter up there inside "
        "a week.",
        "Then I can tell him a date, and a date is the whole repair. Thank you. I do not say that "
        "often because it is not usually true.\n\nOne thing, and then I did not see you.\n\nI do not "
        "know where you are from. I know which boat, and I know which year, because I keep both and "
        "that is my trade. So does every third person on these boards who lost something three years "
        "ago. They just do not say it where the Baron can hear, because the Baron does not care and "
        "there is no money in it."))
    return A


# =========================================================================================================
# THE DROWNED COAST AND THE DROWNED SHRINE - the sea standing over cut stone, the naga sitting on the
# salvage, and the Kundaraz still doing the job the terrace was built for.  39-42.
# =========================================================================================================
def drowned():
    A = []
    A.append(Q("bb_the_salvage", "Salt, Worm and Rot", VELLA, BB, 39, 40, "tidewrack",
        "Shipwright Vella will float anything if you only give her two of the three problems. What she "
        "cannot do is make fittings, because fittings come up the coast on a boat and the boats are "
        "what she is fixing.\n\nThe drowned courts east of the cape are full of the fittings off every "
        "hull the Saltscale have taken in three years, and the Saltscale are sitting on all of it, and "
        "she is specific that she does not want the timber. Timber she has. Timber grows here.",
        [k("Saltscale Salvager", 10), explore(SSK, 167, 113, 8)],
        "Fittings. Rings, pins, braces, anything forged. Not planking, I do not want planking, I have "
        "a jungle of planking and no pins to hold it together.\n\nYou will not know what you are "
        "looking at, so: the salvagers carry it on them, on a line, the way you would carry keys. Take "
        "ten of them and walk the drowned courts down to where the water starts standing, and bring me "
        "back anything that rings when you drop it.",
        "That will put two hulls back on the water, which is two more than I had on Tuesday.\n\nAnd "
        "here is the thing you saw and did not see. That pile they are sitting on is sorted. Rings "
        "together, pins together, braces by length, in rows, on a terrace. Naga do not guard salvage. "
        "They sort it.\n\nSomething down there is keeping a store, and a store is not loot, a store is "
        "a plan.",
        nxt="bb_the_water_came_further"))

    A.append(Q("bb_the_water_came_further", "A Hand and a Half", MINZI, BB, 40, 41, "tidewrack",
        "Lookout Minzi keeps the tide board at the clifftop gate, and she keeps it properly, because "
        "the one thing a lookout can do about weather is write it down before it arrives.\n\nHer "
        "numbers say the high water on the drowned coast stands above the mark the troll masons cut for "
        "it. Not a lot. A hand and a half. She would like it measured against the mason's own mark "
        "rather than against her board, because her board is three years old and theirs is not.",
        [explore(SSK, 160, 104, 8), k("Saltscale Reaver", 8)],
        "There is a cut mark on the ruin's lower wall, a line with a notch under it, and whoever cut it "
        "cut it where they expected the water to come to. Find it. Then stand there at the top of the "
        "flood and tell me where the water actually comes to.\n\nTake the reavers off the wall first. "
        "They work that stretch and they come out of standing water you have already walked through, "
        "which is a thing worth knowing before rather than after.",
        "A hand and a half over a line that somebody cut on purpose, in stone, expecting to be right "
        "about it for a thousand years.\n\nIn three years. That is the number. Not since the masons, "
        "not since the trolls left. In three years.\n\nI am going to put it on the board as three years "
        "and let whoever reads the board do the rest of it themselves. Clear to the cape, by the way. "
        "Which only means I cannot see them yet.",
        nxt="bb_tidecallers"))

    A.append(Q("bb_tidecallers", "What the Fish Went In For", GURGLE, BB, 41, 42, "tidewrack",
        "Gurgle sells fish caught this morning, some of which caught itself, and works the drowned "
        "coast because the drowned coast is where the fish are. He will not go into the sea cave and "
        "has never pretended otherwise.\n\nThe fish are going in now and not coming out. Not being "
        "eaten, going in: against the ebb, in numbers, through the mouth and down into the flooded "
        "halls, which is not a thing a fish does on its own.",
        [k("Kundaraz Tidecaller", 8, DSK), k("Saltscale Myrmidon", 6, DSK)],
        "Six days the shoals have gone in through that mouth on a falling tide. Fish do not swim into a "
        "hole uphill. Something is calling the water in and the fish are going where the water goes.\n\n"
        "The ones doing it are in the halls, and they are not the naga, and I will not say more than "
        "that because I have not been down there and you will have. The myrmidons are in your way. The "
        "callers are the job.",
        "Trolls. You are telling me trolls, in the halls, with the naga all round them and not a mark "
        "on either side.\n\nThen they are not hiding and they are not prisoners. They are working. They "
        "are calling the water into a hall that was built to have water in it, which is what they were "
        "always for, and the naga leave them alone because a flooded hall suits a naga down to the "
        "ground.\n\nMy shoals are somebody's job. I would rather it had been a current.",
        nxt="bb_myzrai"))

    A.append(Q("bb_myzrai", "The Lease", BARON, BB, 41, 42, "tidewrack",
        "Baron Revilgaz has wanted the drowned terraces for three years, because a terrace under four "
        "feet of water with a hull's worth of fittings on it is the cheapest salvage on this coast and "
        "he does not have to pay anyone for the ground.\n\nWhat he cannot do is sell a salvage lease on "
        "a site with a priestess standing in the middle of it. Tide-Priestess Myzrai holds the sanctum "
        "at the deep end of the flooded halls, and he is entirely open about the fact that this is the "
        "only reason he is interested in her at all.",
        [boss("Tide-Priestess Myzrai")],
        "I am not going to dress this up for you. I do not care what she is, I do not care what she is "
        "singing to, and I do not care that the trolls down there were there first and are still "
        "working. I care that nobody will take a lease on a site with her on it.\n\nThe sanctum is the "
        "far end, past the second crossing, where the floor comes back up above the water. She will "
        "have the whole hall between you and her and she will use it. Take her out of the middle of my "
        "salvage.",
        "Good. Here, read that line before I roll it up.\n\nThe lease is drawn. It was drawn before you "
        "took the job, it is dated last Tuesday, and the name on it is mine. Not the Cartel's. Mine, "
        "and the Authority's under it, and a hundred years on a terrace that a troll cut for the tide "
        "a thousand years before anybody here was born.\n\nWeezel will file something about it on "
        "Thursday. He always does. I will have the stone off it by then.",
        requires_quests=["bb_tidecallers"]))
    return A


# =========================================================================================================
# JAGUERO SPIT AND THE BOARDS - whatever got out there got out there and stayed, and one warm favour
# with nothing underneath it.  38-41.  The Cargo is out on the spit and is never an objective.
# =========================================================================================================
def spit():
    A = []
    A.append(Q("bb_pit_stock", "Pit-Stock", KOLK, BB, 40, 41, "spit",
        "Bruiser Kolk keeps trouble off the quay and is clear that trouble above the gate is somebody "
        "else's problem. The spit is above the gate and round the cape and about as far from his quay "
        "as this zone goes.\n\nFour years ago he was one of the hands who walked a consignment of "
        "arena stock off a hull and out onto the sand to be held and fed until the Gurbashi sent for "
        "them. The Gurbashi never sent. Nobody fed them either, and they are still out there, and they "
        "are not stock any more.",
        [k("Pit-Stock Raptor", 10), explore(SSK, 22, 162, 8)],
        "Raptors. Bought for the pit, landed on the spit, and left on it, and before you ask, yes, I "
        "walked them off the boat myself and I was paid for it.\n\nGo out the spit and put them down. "
        "All the way out, not the first palm. The walk back is the same walk, so take water. And they "
        "have had four years out there with nothing coming in, so do not expect what you fought on the "
        "cape road. These ones have had to work it out.",
        "How many did you see out there. Not how many you killed. How many were on that sand.\n\nI "
        "counted thirty-one off the hull, because I was paid by the head, and I have never once stopped "
        "being able to tell you the number.\n\nThe spit has never held more than twenty-eight. Two "
        "carters have told me twenty-eight, four years apart, and you have just walked the whole of it, "
        "and it is sand and palms with nothing on it to stand behind.\n\nSo three of them never went "
        "out onto the sand. Go and eat something. I am going to stand here for a while."))

    A.append(Q("bb_marlas_pot", "A Pot of Something Decent", MARLA, BB, 38, 39, "spit",
        "Keeper Marla pours inside and lets the tide keep whatever gets spilled out on the boards. She "
        "came down here from Lakeshire eleven years ago to cook for a harbour that eats standing up and "
        "has never once tried to pretend that is a tragedy.\n\nHer stock pot wants spit crab and the "
        "crab pots at the head of the sand bar have not been lifted in a fortnight, because the boy who "
        "lifted them has taken better money on the cart run. She is embarrassed about what she can pay "
        "and says so before she says anything else.",
        [k("Spit Scavenger Crab", 12), explore(SSK, 30, 155, 7)],
        "I can pay you badly and feed you well, and I want to be honest about the order of those.\n\n"
        "Crab, off the sand at the head of the spit, a dozen if your arms will take a dozen. Lift the "
        "pots while you are down there so I know whether the boy left them set or left them "
        "open.\n\nSit down when you get back. Not at the rail. At a table, inside, like a person.",
        "Look at the size of them. The boy left the pots set, which means he meant to come back, which "
        "means I will stop saying what I have been saying about him.\n\nSit. Eat that.\n\nNow. A "
        "drinker in here told me that where you come from the water arrives in the building, by pipe, "
        "hot, whenever you want it, and that nobody thinks about it at all. I have thought about that "
        "for a month. Is it true? Do not tell me how it works. I only want to know if it is true, "
        "because if it is, then you have all come an extremely long way down in the world and nobody "
        "on these boards has had the manners to say so."))
    return A


# =========================================================================================================
# THE CAPSTONES.  500 is the house rate.  Three, and each one closes a thread the player can feel:
# the fee they paid in the first five minutes, the Thursday tide the harbour is bought by, and the
# lease the Baron had drawn before he hired them.
# =========================================================================================================
CAPSTONES = {
    "bb_the_fee_explained": 500,
    "bb_hold_the_water": 500,
    "bb_myzrai": 500,
}


# =========================================================================================================
# THE DROPS TABLE THIS PASS DOES NOT WRITE.
# Every item below is what a fetch objective in this slice WOULD have wanted.  No quest above uses
# fetch, because data/creatures/quest_drops.json is off limits to this pass (three agents, one
# read-modify-write file) and a fetch item nothing drops is a quest nobody can hand in.  Run with
# --with-drops to splice it, append-only, re-reading the file immediately before the write - and only
# do that when no other Stranglethorn pass is running.
# =========================================================================================================
FETCH_DROPS = {
    "Saltscale Salvager": [("saltscale_fitting_line", "Saltscale Fitting-Line",
                            "Forged rings and pins carried on a line, the way you would carry keys.",
                            0.46)],
    "Kundaraz Stoneshaper": [("stoneshaper_rule", "Stoneshaper's Rule",
                              "A notched rod. The notches are a module and the module is the same one "
                              "the arena floor is laid to.", 0.42)],
    "Bloodsail Bosun": [("bosuns_landing_tally", "Bosun's Landing Tally",
                         "What each beached keel paid, in a worse hand than Nizzik's and for a worse "
                         "toll.", 0.44)],
    "Kundaraz Tidecaller": [("tidecaller_weir_pin", "Weir Pin",
                             "Cut stone, tapered, meant to sit in a junction and let a hall fill at a "
                             "chosen rate.", 0.40)],
}


def _overlay_text(quests):
    """Regenerate tools/quest_text_src/stranglethorn_south.txt from the same strings the JSON carries.

    The overlay WINS at load time (world/quest_manager.py), so a hand-edited overlay and a re-run
    builder drift apart silently and the player reads the stale one.  Generating both from one source
    makes that impossible.  tools/build_quest_text.py joins continuation lines with a space, so the
    paragraph breaks flatten here - that is what every other zone's overlay already does, and the
    limit it checks is 760 characters per field.
    """
    flat = lambda s: " ".join(s.split())
    out = ["# Booty Bay + Southern Stranglethorn + The Drowned Shrine. Generated by",
           "# tools/build_stranglethorn_south_quests.py - edit the builder, not this file.",
           "# The harbour sells peace by the week and everybody on the boards is paying.", ""]
    for q in quests:
        out.append(f"@ {q['quest_id']}")
        out.append(f"Title: {q['title']}")
        out.append(f"D: {flat(q['description'])}")
        out.append(f"A: {flat(q['accept_text'])}")
        out.append(f"T: {flat(q['turn_in_text'])}")
        out.append("")
    return "\n".join(out) + "\n"


def audit(quests):
    """FAIL THE BUILD rather than ship twenty quests nobody can finish or a payout nobody can use.

    Same shape as the Southern Thousand Needles and Southern Stranglethorn loot audits, plus the four
    standing rules that actually bite at this band, plus the structural checks that have each shipped
    broken at least once on a previous pass: a giver id nobody has, a kill target no creature answers
    to, an explore target spelled with the handbuilt KEY instead of the live zone key, and a chain that
    points at itself.
    """
    errs = []
    npcs = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text())["npcs"]
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text())["vendors"]
    known_npcs = {n["npc_id"] for n in npcs} | {v["vendor_id"] for v in vendors}
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]
    ids = {q["quest_id"] for q in quests}

    for q in quests:
        qid = q["quest_id"]
        if q["giver_npc_id"] not in known_npcs:
            errs.append(f"{qid}: giver {q['giver_npc_id']!r} is in no NPC or vendor roster")
        if q.get("turn_in_npc_id") and q["turn_in_npc_id"] not in known_npcs:
            errs.append(f"{qid}: turn-in {q['turn_in_npc_id']!r} is in no NPC or vendor roster")
        if not 38 <= q["level_min"] <= q["level_max"] <= 42:
            errs.append(f"{qid}: level band {q['level_min']}-{q['level_max']} outside 38-42")
        if q.get("next_quest_id") and q["next_quest_id"] not in ids:
            errs.append(f"{qid}: next_quest_id {q['next_quest_id']!r} is not a quest in this pass")
        for req in q.get("requires_quests", []):
            if req not in ids:
                errs.append(f"{qid}: requires {req!r}, which is not a quest in this pass")
        if q["zone"] not in (BB, SS, "ratchet"):
            errs.append(f"{qid}: zone {q['zone']!r} is not a zone this pass may author in")

        for o in q["objectives"]:
            t = o["type"]
            if t not in ("kill", "kill_boss", "explore", "deliver"):
                errs.append(f"{qid}: objective type {t!r} is not one this pass ships")
            if t in ("kill", "kill_boss"):
                name = o["target"]
                if name not in creatures:
                    errs.append(f"{qid}: kills {name!r}, which is not in creatures.json")
                elif t == "kill_boss" and not creatures[name].get("is_boss"):
                    errs.append(f"{qid}: kill_boss {name!r} is not is_boss")
                # STANDING RULE: no quest is ever built around a named rare.
                if name in RARES:
                    errs.append(f"{qid}: objective targets the named rare {name!r}")
                if o.get("zone") not in (SSK, DSK):
                    errs.append(f"{qid}: kill zone {o.get('zone')!r} is not a live zone key")
            if t == "explore":
                if o["target"] not in (SSK, DSK, BB):
                    errs.append(f"{qid}: explores {o['target']!r}, which is not a live zone key "
                                f"(the handbuilt KEY {SS!r} is NOT the map's name slug)")
                if o.get("target_x") is None:
                    errs.append(f"{qid}: explore has no position gate")
            if t == "deliver" and not q.get("turn_in_npc_id"):
                errs.append(f"{qid}: deliver objective with no turn_in_npc_id to deliver TO")
            # NO ESCORTS, EVER.  There is no escort objective type in the engine, so the way one gets
            # in is as prose on a deliver/explore label.  Checked, not assumed.
            blob = " ".join(str(v) for v in o.values()).lower()
            for word in ("escort", "protect him", "protect her", "keep alive", "see her safely",
                         "see him safely", "walk with"):
                if word in blob:
                    errs.append(f"{qid}: objective reads like an escort ({word!r})")

        # NO STAT NUMBERS IN PROSE, and the Integration was THREE years ago.
        prose = " ".join((q["description"], q["accept_text"], q["turn_in_text"]))
        for bad in ("+1 ", "+2 ", "+3 ", "stamina", "intellect", "agility", "spell power",
                    "attack power", "armour value", "armor value"):
            if bad in prose.lower():
                errs.append(f"{qid}: stat language in prose ({bad!r})")
        for bad in ("four years ago the ground", "two years ago the ground", "five years ago the ground"):
            if bad in prose.lower():
                errs.append(f"{qid}: the Integration was three years ago ({bad!r})")
        for ch in prose:
            if not ch.isascii():
                errs.append(f"{qid}: non-ascii character {ch!r} in prose (the game font has none)")
                break
        for key in ("description", "accept_text", "turn_in_text"):
            n = len(" ".join(q[key].split()))
            if n > 760:
                errs.append(f"{qid}: {key} is {n} characters, over the overlay limit of 760")

    # ---- chains: no loops, and every chain actually goes somewhere
    for q in quests:
        seen, cur = [], q["quest_id"]
        while cur:
            if cur in seen:
                errs.append(f"chain loop: {' -> '.join(seen + [cur])}")
                break
            seen.append(cur)
            nxt = next((x.get("next_quest_id") for x in quests if x["quest_id"] == cur), None)
            cur = nxt

    # ---- the payout
    items = [i for q in quests for i in q["unique_item_defs"]]
    wt, ar = {}, {}
    for i in items:
        if i.get("armor_type"):
            ar[i["armor_type"]] = ar.get(i["armor_type"], 0) + 1
        elif i.get("weapon_type"):
            wt[i["weapon_type"]] = wt.get(i["weapon_type"], 0) + 1
    acc = [i for i in items if not i.get("armor_type") and not i.get("weapon_type")]
    casting = sum(1 for i in items if {"intellect", "spirit"} & set(i.get("primary_stats", {})))

    if set(ar) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour classes missing from the payout: {sorted(ar)}")
    elif max(ar.values()) > min(ar.values()) * 1.5:
        errs.append(f"armour spread lopsided across four classes: {ar}")
    if len(wt) < 5:
        errs.append(f"want at least 5 distinct weapon types across the pass, got {sorted(wt)}")
    elif max(wt.values()) > 0.40 * sum(wt.values()):
        errs.append(f"one weapon type is more than 40% of the pass's weapons: {wt}")
    if not 0.33 <= casting / len(items) <= 0.62:
        errs.append(f"casting share {casting}/{len(items)} outside 33-62%")

    # STANDING RULE: no magic-resistance gear below level 45.  This band tops out at 42, so nothing in
    # the pass may carry a resistance stat at all.
    for i in items:
        stats = set(i.get("primary_stats", {})) | set(i.get("secondary_stats", {}))
        res = sorted(s for s in stats if "resist" in s)
        if res:
            errs.append(f"{i['name']}: magic-resistance gear below level 45 ({res})")
    # STANDING RULE: no high-tier crafting material before 60.  Every reward here is an equippable.
    for i in items:
        for key in ("material", "reagent", "stack_size", "tradeskill", "gather_tier"):
            if key in i:
                errs.append(f"{i['name']}: carries crafting/gathering key {key!r}")
        if i.get("required_level", 0) > 42:
            errs.append(f"{i['name']}: required level {i['required_level']} above the band")

    # ---- the capstones have to be real quests in this pass
    for cap in CAPSTONES:
        if cap not in ids:
            errs.append(f"capstone {cap!r} is not a quest in this pass")

    if errs:
        raise SystemExit("STRANGLETHORN SOUTH QUEST BUILD FAILED:\n  " + "\n  ".join(errs))

    earth = sum(1 for q in quests if q["quest_id"] in EARTH)
    print(f"  audit ok: {len(quests)} quests, levels 38-42, {len(ids)} unique ids")
    print(f"    givers       {len({q['giver_npc_id'] for q in quests})} distinct, all resolved")
    print(f"    objectives   " + ", ".join(
        f"{t}={sum(1 for q in quests for o in q['objectives'] if o['type'] == t)}"
        for t in ("kill", "kill_boss", "explore", "deliver")))
    print(f"    rewards      {len(items)} items   armour {ar}   accessories {len(acc)}")
    print(f"    weapons      {wt}")
    print(f"    casting      {casting}/{len(items)} ({casting / len(items):.0%})")
    print(f"    resistance   0 items (rule: none below level 45)")
    print(f"    rares        0 objectives (The Cargo / Ssaren / Orlee Vantch / Saltgorge)")
    print(f"    escorts      0 (rule: never)")
    print(f"    capstones    {', '.join(CAPSTONES)} at 500 each")
    print(f"    earth note   {earth}/{len(quests)} quests carry the transplant undercurrent")


#: The quests that carry the Earth-transplant undercurrent.  Kept as data so the count in the build
#: output is not a thing somebody has to recount by hand later.
EARTH = {
    "bb_landing_fee",            # Nizzik does not write down where anyone is from, and says it as a schedule
    "bb_barons_name",            # the Baron explains what a harbour is, slowly, because of where you are from
    "bb_weezels_paperwork",      # Weezel picks you BECAUSE you cannot read a Cartel seal
    "bb_the_fee_explained",      # a list like that is a thing somebody uses later
    "bb_three_wrecks",           # Sprocket asks where you were when it happened and does not wait
    "bb_oonas_name",            # yours came out of the sky, mine came out of a shipyard
    "bb_kundaraz_road",          # Zan'rek corrects your word for the ruin, twice, and then tells you why
    "bb_stoneshapers",           # Scrip asks whether carts really move without animals. Flat
    "bb_three_generations",      # the hand and a half is not the masons' doing, and Zekki dates it
    "bb_what_the_vine_keeps",    # I know which boat and I know which year, and so does every third person
    "bb_the_salvage",            # Vella explains what a fitting is because you will not know
    "bb_the_water_came_further",  # Minzi says "in three years" and then says it again
    "bb_pit_stock",              # Kolk's four-year-old consignment predates you, and he is precise about it
    "bb_marlas_pot",             # Marla, warmly fine with you, and the one hot-water question
}


def write_capstones():
    """Fill booty_bay_authority -> quest_rep.capstones.  RE-READS THE FILE IMMEDIATELY BEFORE WRITING
    and touches no other faction: data/factions/factions.json is shared, and this pass is one of three
    running over Stranglethorn."""
    data = json.loads(FACTIONS.read_text())
    f = data["factions"]["booty_bay_authority"]
    before = dict(f["quest_rep"].get("capstones") or {})
    f["quest_rep"]["capstones"] = dict(CAPSTONES)
    FACTIONS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return before, dict(CAPSTONES)


def write_drops():
    """OFF BY DEFAULT (--with-drops).  Append-only, my item ids only, re-read immediately before the
    write.  See FETCH_DROPS's comment for why no shipped quest depends on this."""
    dp = ROOT / "data/creatures/quest_drops.json"
    drops = json.loads(dp.read_text())
    # The loaders read data["drops"], NOT the top level - combat_engine._get_loot_item_drops and
    # quest_locator.item_sources both do .get("drops", {}), so a creature key written beside "drops"
    # is read by nothing.
    table = drops.setdefault("drops", drops)
    for cre, rows in FETCH_DROPS.items():
        cur = [d for d in table.get(cre, []) if d["item_id"] not in {r[0] for r in rows}]
        for (iid, nm, desc, ch) in rows:
            cur.append({"item_id": iid, "name": nm, "category": "quest", "description": desc,
                        "chance": ch})
        table[cre] = cur
    dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n")
    return sum(len(v) for v in FETCH_DROPS.values())


def main():
    quests = tariff() + bloodsail() + kundaraz() + drowned() + spit()
    audit(quests)

    OUT.write_text(json.dumps(
        {"_notes": "Booty Bay / Southern Stranglethorn / The Drowned Shrine quest pass (2026-10-30). "
                   "Generated by tools/build_stranglethorn_south_quests.py - do not hand-edit text "
                   "here OR in the overlay; both come from the builder, and the overlay in "
                   "data/quests/text/stranglethorn_south.json wins at load time. Source of truth is "
                   "tools/build_stranglethorn_south_quests.py; "
                   "tools/quest_text_src/stranglethorn_south.txt is regenerated from it.",
         "quests": quests}, indent=2, ensure_ascii=False) + "\n")
    TXT.write_text(_overlay_text(quests))
    before, after = write_capstones()

    n_drops = write_drops() if "--with-drops" in sys.argv else 0
    print(f"Stranglethorn South quests: {len(quests)} written to {OUT.relative_to(ROOT)}")
    print(f"  overlay source           {TXT.relative_to(ROOT)} ({len(quests)} entries)")
    print(f"  booty_bay_authority      capstones {before or '{}'} -> {after}")
    print(f"  quest_drops.json         {'wrote ' + str(n_drops) + ' rows' if n_drops else 'NOT TOUCHED (no quest needs it; --with-drops to splice FETCH_DROPS)'}")


if __name__ == "__main__":
    main()
