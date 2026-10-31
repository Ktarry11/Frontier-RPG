#!/usr/bin/env python3
"""
Northern Tanaris + Steamwheedle Port + The Drownbell quest pass. Idempotent. 41-44.

    PYTHONPATH=. python3 tools/build_tanaris_quests.py
    PYTHONPATH=. python3 tools/audit_quests.py
    PYTHONPATH=. python3 tools/qa_quest_lore.py --zone tanaris --show

THIRTY-TWO quests. The game's first content above 40 - audit_quests has been reporting "NOTHING TO
DO at level(s): 43-60" since the ladder was built.

=========================================================================================================
WHY GADGETZAN DIED, WHICH IS THE ZONE'S SPINE AND WAS ALREADY WRITTEN IN TWO OTHER ZONES
=========================================================================================================
A desert city lives on its wells. The Aspen Wilderness has somebody watching the melt get bigger
every spring (asp_higher_every_spring); Southern Thousand Needles has somebody asking where all that
water goes and getting no answer (fw_where_the_water_goes); the Shimmering Flats has the answer -
it arrives, it always has, it goes under, and it ends up beneath the oldest hive on the pan
(swf_water_answer).

WHAT NOBODY IN ANY OF THOSE THREE ZONES KNOWS is what that did to the far end. A range came down on
one side of this region three years ago and the water table tipped. Gadgetzan's wells went dry over
two seasons and a walled city with a wall and no water is a siege it is holding against itself.
Steamwheedle survived the same event untouched, because a port does not drink from a well - it has
the sea and it has ships, and one of those two towns was depending on the desert working.

SO THE GOBLINS BLAME YOU, AND THIS TIME THEY ARE RIGHT. Kyle, on the Flats: "Make the goblins blame
'players' a bit that the integration changed everything and It's ruining profits etc." Saltwheel's
goblins blame the newcomers for a racetrack nobody drives, which is true and self-serving. Tanaris's
goblins blame the newcomers for a city that died of thirst, and the arithmetic holds all the way
down. That is a harder thing for a player to shrug off, and it should be - this is a higher zone and
the lore band is wider here for exactly this reason.

It is still not the whole zone. Steamwheedle is LOUD, BUSY AND DOING WELL, which is the opposite of
Saltwheel, and a player walking in off the pan should notice the noise before they notice the
grievance.

=========================================================================================================
THREADS
=========================================================================================================
  THE TWO TOWNS (6)   The quay and the yard, and the two berths that would fix the harbour and that
                      neither half can cut alone. Resolves in a WORKS ORDER, not a fight.
  GADGETZAN (6)       Back to the dead city, to find out what actually happened to it. Ends on a
                      gate, below, and the answer is the water.
  ZUL'FARRAK (5)      The Sandfury are still at their own ruin. They did not leave either, and they
                      have a different reason, and it is worse.
  THE DROWNBELL (5)   The cove, ending underground with Captain Vaile.
  THE ROAD (4)        Why no cart runs west, which is the other end of a conversation Saltwheel and
                      Freewind Post have both already had.
  STANDALONES (4) + TWO ITEM-STARTERS

NO ESCORTS. NO QUEST TARGETS A NAMED RARE - the six surface rares and the Bellwarden are lore and
loot; Captain Vaile is a PINNED cave boss, so kill_boss on her is legitimate.
NO MAGIC RESISTANCE: the rule is 45+ and this band tops out at 44.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/tanaris.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

NT = "northern_tanaris"
SP = "steamwheedle_port"
DB = "the_drownbell"
SW = "saltwheel"

XP = {41: 2920, 42: 3000, 43: 3080, 44: 3160}
GOLD = {41: 11700, 42: 12000, 43: 12300, 44: 12600}

tirisfal_gear.THEMES.update({
    "quay": (["Harbourmaster's", "Four-Berth", "Old-Quay", "Keelmaker's", "Tide-Worn"],
             ["Four generations of the same hands have worn this to the shape of them.",
              "Harbour kit. Salt has been at it and salt has lost.",
              "Cut for a dock that was big enough once.",
              "It smells of pitch, which out here is the smell of somebody still working."]),
    "yard": (["Upper-Yard", "Goat-Field", "Three-Year", "Throughput", "Hack's"],
             ["Made fast rather than made well, and it has outlasted things made well.",
              "Yard kit, three years old and already mended twice.",
              "Hot metal got at this and the mark never came out.",
              "Everything here was built on ground that was a goat field."]),
    "dustdead": (["Dry-Well", "Lintel-Cut", "Gadgetzan", "Walled", "Last-Season"],
                 ["Carried four days east by somebody who did not look back.",
                  "Goblin work, from a shop with a name cut into the lintel.",
                  "There is a town's worth of this and nobody to want it.",
                  "Dust got into it in a city that has not had rain in three years."]),
    "sandfury": (["Sandfury", "Step-Pyramid", "Unburied", "Hexxer's", "Broken-Face"],
                 ["Troll iron, and troll patience, and neither has gone anywhere.",
                  "Taken off the steps of a thing that is still standing.",
                  "Old before the sky changed and unbothered by the sky changing.",
                  "Something was done with this and nobody left is saying what."]),
    "cove": (["Drownbell", "Careenage", "Cove-Taken", "Bell-Chain", "Below-Water"],
             ["Dry on the inside, which down there is a kind of wealth.",
              "Pirate kit - which is to say somebody else's kit, once.",
              "Rope and brine and a long time without daylight.",
              "It came up out of the cove and it did not come up alone."]),
    "roadwest": (["Nineteen-Mile", "Axle-Broke", "Westbound", "Dry-Crossing", "Agent's"],
                 ["It has done the crossing more often than anything riding in it.",
                  "Road kit, and the road it was made for does not run any more.",
                  "Dust from two deserts in the same seam.",
                  "Freight-grade, which means heavier than it looks and worth the weight."]),
})


def k(target, n, zone=NT):
    return kill(target, n, zone=zone)


def boss(target, zone=DB):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def gather(item, n):
    return dict(type="gather", target=item, count=n)


def explore(zone, x, y, radius=9):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    return dict(type="dialogue", topics=list(topics))


def carry(item_id, name, desc, count=1):
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


# ---- givers. Every id is already in a roster; this pass invents nobody. ---------------------------
HARBOUR = "stw_harbourmaster"     # Senna Coil - four berths and turning ships away since year two
KEEL = "stw_shipwright"           # Hald Keelmaker - more work in three years than in twenty
CHANDLER = "stw_chandler"         # Vex Tarrow - nothing has changed at this counter
INNKEEP = "stw_innkeeper"         # Mirabel Sump - forty beds and twice the town
FISH = "stw_fishmonger"           # Oda Brack - buys her salt off a woman on the pan
BANKER = "stw_banker"             # Strongbox-Keeper Pell
YARDBOSS = "stw_yard_boss"        # Grizzel Hack - this was a goat field
SMITH = "stw_smith"               # Dorga Ironside - salt air or dry sand, pick one
ENGINEER = "stw_engineer"         # Faz Quill - his press is still in Gadgetzan
BROKER = "stw_salvage_broker"     # Nim Catchpenny - half of it came out of Gadgetzan
AGENT = "stw_caravan_agent"       # Rullo Tack - nothing coming back worth the axle
GOODS = "stw_general_goods"       # Bix Rannow - the shed makes more than the lintel did
CLERK = "stw_tally_clerk"         # Hesper Dunn - keeps the last two columns for a reason
SURGEON = "stw_doctor"            # Wick Ambrose - crush injuries, mostly
MAZZIC = "stw_old_gadgetzan"      # Old Mazzic - carried out on a door
KEZZIK = "stw_flight_master"      # Wind-Rider Kezzik - bring me the town that makes me wrong

#: The far-zone gate. A finished quest, three zones and six levels below this one.
FLATS_WATER = "swf_water_answer"

FETCH_DROPS = {
    "Sandfury Scavenger": [
        ("tan_pried_fitting", "Pried Fitting", "Goblin brass, levered off something that was not theirs.", 0.45),
        ("tan_sandfury_charm", "Sandfury Charm", "Bone and wire. It means something to somebody.", 0.40)],
    "Sandfury Axethrower": [
        ("tan_throwing_axe", "Notched Throwing Axe", "Thrown a great many times and sharpened fewer.", 0.45)],
    "Sandfury Hexxer": [
        ("tan_hex_fetish", "Hex Fetish", "Still warm, which it should not be.", 0.42)],
    "Gadgetzan Scrapjaw": [
        ("tan_chewed_ledger", "Chewed Ledger", "A page and a half legible. Both of them are figures.", 0.45)],
    "Dunecrest Raptor": [
        ("tan_raptor_claw", "Dunecrest Claw", "Sand-polished to a shine along one edge.", 0.50)],
    "Thornback Scorpid": [
        ("tan_scorpid_barb", "Thornback Barb", "The venom stays wet out here and nobody knows why.", 0.48)],
    "Bonefield Hyena": [
        ("tan_hyena_jaw", "Hyena Jaw", "Everything that stops on that road is theirs by morning.", 0.48)],
    "Carrion Vulture of Tanaris": [
        ("tan_vulture_quill", "Sun-Stiff Quill", "It does not bend any more and it never will.", 0.50)],
    "Sunbleached Basilisk": [
        ("tan_basilisk_eye", "Bleached Basilisk Eye", "Clouded right through, like the air at noon.", 0.40)],
    "Sunstone Elemental": [
        ("tan_sunstone_core", "Sunstone Core", "Too hot to hold and it has been out of the sun for a day.", 0.42)],
    "Drownbell Deckhand": [
        ("tan_cove_tally", "Cove Tally-Stick", "Notched, and the notches are not days.", 0.45)],
    "Drownbell Bosun": [
        ("tan_bosun_whistle", "Bosun's Whistle", "Brass, green with salt, and still loud.", 0.42)],
    "Cove Tidecaller": [
        ("tan_tide_focus", "Tidecaller's Focus", "Cold in a cave that is not cold.", 0.42)],
    "Bilge Crawler": [
        ("tan_crawler_shell", "Crawler Shell", "Thin, curved, and sharper than it has any right to be.", 0.50)],
}

STARTER_DROPS = {
    "Gadgetzan Scrapjaw": [
        ("tan_well_token", "Well-Token", "A stamped brass token from Gadgetzan's public well. The "
         "date on the back is three years old and the number on the front is very high.", 0.09)],
    "Drownbell Cutthroat": [
        ("tan_salvage_claim", "Water-Stained Salvage Claim", "A salvage claim on something in the "
         "cove, filed by a company nobody in Steamwheedle has heard of, and countersigned twice.",
         0.09)],
}

STARTER_IDS = {"tan_well_token": "tan_item_well_token",
               "tan_salvage_claim": "tan_item_salvage_claim"}


def build():
    A = []

    # ===============================================================================================
    # THREAD 1 - THE TWO TOWNS (6). Resolves in a works order, not a fight.
    # ===============================================================================================
    A.append(Q("tan_berth_turned_away", "Four Berths and a Queue", HARBOUR, SP, 41, 41, "quay",
        "Harbourmaster Senna Coil has four berths and has been turning ships away since the second "
        "winter.\n\nShe can tell you to the day when the queue started, because she started the "
        "queue, and she has never once got to the bottom of it.",
        [k("Drownbell Deckhand", 9), gather("tan_cove_tally", 6)],
        "A ship waiting outside the heads is a ship somebody can board, and twice this season "
        "somebody has.\n\nNine of them off the shore road and bring me their tally sticks. The "
        "notches are not days - I have looked at two of these and they are a count of something, and "
        "I would like to know whether my queue is on that list.",
        "It is a list of hulls. Nine sticks, and between them they have counted more ships than I "
        "have berthed this year.\n\nSo they are not raiding my queue at random. They are WORKING it, "
        "the way I work a tide table.\n\nI need two more berths cut and I needed them a year ago. "
        "Go and see Hack, and do not tell her I sent you in those words.",
        nxt="tan_berth_the_yard"))

    A.append(Q("tan_berth_the_yard", "What the Yard Would Want For It", YARDBOSS, SP, 41, 42, "yard",
        "Yard-Boss Grizzel Hack has the crews, the gear and the appetite to cut two berths out of "
        "that rock.\n\nWhat she does not have is any reason to do the quay a favour, and she is "
        "going to say so before she says yes.",
        [k("Thornback Scorpid", 10), gather("tan_scorpid_barb", 6), gather("tan_sunstone_core", 4)],
        "Senna wants rock cut. Senna has wanted rock cut for a year and has not once walked up this "
        "hill to say so.\n\nFine. Here is my price, and it is not money. My powder crews work the "
        "stone out past the yard and the scorpids are in there with them. Ten of them, six barbs, "
        "and four sunstone cores off the elementals, because the cores run hot enough to set a "
        "charge and I would rather not buy fuse.",
        "Good. Tell her yes.\n\nTell her it was always going to be yes. I grew up in a town with a "
        "wall round it and I watched what happens when the people who could fix a thing are waiting "
        "to be ASKED properly.\n\nShe can have her berths. She is going to have to sign for them in "
        "front of Hesper, though, because I am not doing this on a handshake with the quay.",
        nxt="tan_berth_signed"))

    A.append(Q("tan_berth_signed", "In Front of the Clerk", CLERK, SP, 42, 42, "quay",
        "Tally-Clerk Hesper Dunn keeps every crate in and out and which side of town it came from.\n\n"
        "She has been waiting three years for the two halves of this town to need a document.",
        [gather("tan_chewed_ledger", 6), talk("tan_topic_columns", "tan_topic_both_sides")],
        "They want it written down. Of course they want it written down, they are goblins, and this "
        "is the first time either of them has wanted the same piece of paper.\n\nI need six pages to "
        "copy the form onto and there is no clean paper in this town, so you are going to the dead "
        "city for it - the scrapjaws nest in the counting houses and they have chewed three years of "
        "Gadgetzan's books into bedding.\n\nThen come back and ask me what I keep those last two "
        "columns for. I will tell you properly.",
        "Signed by both. It will outlive everybody who signed it, which is the only thing I have "
        "ever actually wanted out of this job.\n\nAnd you asked. Nobody asks.\n\nGo and tell "
        "Keelmaker the rock is coming out. He has been pricing a dry dock in his head since the wet "
        "and he thinks nobody has noticed.",
        nxt="tan_berth_keelmaker"))

    A.append(Q("tan_berth_keelmaker", "What Keelmaker Has Been Pricing", KEEL, SP, 42, 43, "quay",
        "Shipwright Hald Keelmaker has had more work in three years than in the twenty before them, "
        "and every job of it came off the yard.\n\nHe is not bitter about that. He is the only one "
        "on the quay who is not, and it has cost him friends.",
        [k("Sunbleached Basilisk", 8), gather("tan_basilisk_eye", 5), gather("tan_sunstone_core", 5)],
        "Two berths is a hole in the rock. A dry dock is a hole in the rock with a gate on it, and "
        "while they are cutting I would rather they cut the second thing.\n\nThe gate wants glass "
        "and it wants heat. Five eyes - they take the sun and hold it, and set into a "
        "sight-glass they will tell me my water level in the dark - and five sunstone cores for the "
        "forge. Eight of them to get there.",
        "Enough for the sight-glass and enough for the forge.\n\nI have been on this quay sixty "
        "years and I have never built anything that was not a repair. This is going to be a dry "
        "dock. Mine.\n\nThe yard will cut it and the quay will own it and in ten years nobody will "
        "remember which half did which, and that is the point of building something.",
        nxt="tan_berth_the_noise"))

    A.append(Q("tan_berth_the_noise", "The Whole Town Hears It", SURGEON, SP, 43, 43, "yard",
        "They start cutting rock at first light and they do not stop.\n\nSurgeon Wick Ambrose has "
        "been expecting the casualties and is getting a different kind than he planned for.",
        [k("Drownbell Powdermonkey", 9), gather("tan_hyena_jaw", 5), k("Bonefield Hyena", 8)],
        "Powder work. I have been setting hands for a fortnight and they are all yard hands, and "
        "before you say it - no, they are not careless, they are the ones doing the lifting.\n\nThe "
        "cove crews have worked out that a town making that much noise is a town not listening. Nine "
        "of their powdermonkeys off the shore. And the hyenas have come in close for the spoil "
        "tip - eight of them, and bring the jaws, I am sick of guessing which bite I am looking at.",
        "That is the last of them off the tip.\n\nTwo things nobody expected from cutting a hole in "
        "a rock: the yard and the quay are drinking in the same half of the room now, and I have "
        "treated more quay hands this fortnight than in the last two years, because they came up the "
        "hill to help and they are sixty and they do not lift like they think they do.\n\nI am not "
        "complaining. I want that on a record somewhere.",
        nxt="tan_berth_done"))

    A.append(Q("tan_berth_done", "Five and Six", HARBOUR, SP, 43, 44, "quay",
        "Berth five took eleven days. Berth six took nine, because by then the quay crews had "
        "stopped standing at the top of the hill watching.\n\nSenna Coil has got to the bottom of "
        "her queue for the first time since the second winter and does not know what to do with the "
        "afternoon.",
        [explore(SP, 24, 26, 8), k("Drownbell Deckhand", 10), gather("tan_bosun_whistle", 4)],
        "Walk the new front, end to end, and tell me if it reads as one quay or as two.\n\nThen go "
        "and finish what started this. Ten more off the shore and four of the bosuns' whistles - "
        "they signal with them and I would like to know the calls, because a harbour that can read "
        "the signals outside the heads is a harbour that gets a night's sleep.",
        "One quay. You said one quay.\n\nI will take it. Ask me in ten years and I will tell you it "
        "was always one quay and I will have forgotten this conversation, and Hesper will have the "
        "document, and she will be insufferable about it and she will be right."))

    # ===============================================================================================
    # THREAD 2 - GADGETZAN (6). Back to the dead city, and the answer is the water.
    # ===============================================================================================
    A.append(Q("tan_gad_the_press", "There Is a Press in That Town", ENGINEER, NT, 41, 41, "dustdead",
        "Engineer Faz Quill's whole workshop came out of Gadgetzan on three carts. Everything "
        "heavier than a cart is still in it.\n\nHe talks about a particular press more than he talks "
        "about most people, and he is aware of that.",
        [explore(NT, 97, 44, 10), k("Gadgetzan Scrapjaw", 10), gather("tan_pried_fitting", 5)],
        "Four days west, through the wall, second street off the east gate. It is a drop press and "
        "it weighs more than this shed.\n\nI am not asking you to bring it. I am asking you to go "
        "and tell me it is still there, because the Sandfury have been coming down off the pyramid "
        "and prying the brass off everything that has any, and five of those fittings will tell me "
        "how far in they have got.",
        "Still there. Of course it is still there, nobody can move it, that is the whole reason I "
        "could not.\n\nThe fittings are from the second street. So they have got that far in.\n\nGo "
        "and see Mazzic. He will not ask you to go back, he will just want to know what the street "
        "looked like.", nxt="tan_gad_mazzic"))

    A.append(Q("tan_gad_mazzic", "Carried Out on a Door", MAZZIC, SP, 41, 42, "dustdead",
        "Old Mazzic did not leave Gadgetzan. He was carried out on a door by two people whose names "
        "he never got.\n\nHe would like that distinction kept, and he is the only one in this town "
        "who insists on it.",
        [talk("tan_topic_carried", "tan_topic_the_wells"), gather("tan_chewed_ledger", 5)],
        "Everybody says we LEFT. Like it was a Tuesday and a decision.\n\nAsk me about it properly "
        "and I will tell you, and then ask me about the wells, because that is the part the quay "
        "crowd have never once asked me about in three years.\n\nAnd bring me whatever the scrapjaws "
        "have not finished chewing out of the counting houses. Five will do. I want to see a figure "
        "in my own town's hand.",
        "Those are water rates.\n\nFive pages and they are all water rates, and the number goes up "
        "in the third one and up again in the fourth and then the fifth one is a different hand "
        "entirely, because whoever was writing them stopped.\n\nI knew the wells went. Everybody "
        "knows the wells went. I have never had it in a column before.",
        nxt="tan_gad_the_wells"))

    A.append(Q("tan_gad_the_wells", "What a Walled Town Drinks", MAZZIC, NT, 42, 42, "dustdead",
        "A desert city lives on its wells. Gadgetzan had nine of them and a wall round the lot.\n\n"
        "Mazzic can name all nine. He grew up drinking from four.",
        [explore(NT, 84, 50, 8), k("Sandfury Scavenger", 9), gather("tan_sandfury_charm", 5)],
        "The deep well is in the west quarter, under the broken wall. Go and look down it.\n\nThe "
        "Sandfury will be there, because the Sandfury are everywhere in that town now, and five of "
        "their charms would tell me whether they are living in it or just working it. There is a "
        "difference and it decides what I think of them.\n\nLook down the well. That is the job. The "
        "rest is me being curious in my old age.",
        "Dry. Dry all the way down, and you could see the bottom, which from that well you never "
        "could.\n\nAnd the charms are grave charms. They are not living in my town, they are "
        "BURYING in it, which is either an insult or the most respect anybody has shown the place in "
        "three years and I genuinely cannot decide which.\n\nThere is a woman on the pan north of "
        "here who worked out where the water in this region goes. Hesper has the name.",
        nxt="tan_gad_the_answer"))

    # THE GATE. Three zones and six levels below: the Flats' water chain. A player who did not finish
    # it never sees this offered, and is told nothing about it.
    A.append(Q("tan_gad_the_answer", "The Far End of Somebody Else's Question", CLERK, NT, 43, 44,
        "dustdead",
        "A mountain came down in the north three years ago and the water under this region tipped "
        "with it. On the pan they worked out where it all goes.\n\nNobody on the pan worked out what "
        "it stopped doing on the way.",
        [explore(NT, 97, 36, 9), k("Sandfury Hexxer", 8), gather("tan_hex_fetish", 5),
         gather("tan_chewed_ledger", 6)],
        "You have stood where that water ends up. I have the figures for where it used to start.\n\n"
        "Go back into the city and read me the north quarter - the shallow wells, the ones that went "
        "first - eight of the hexxers, six more pages, and five of their fetishes. The trolls were "
        "watching that water table longer than any of us and they marked what they saw.\n\nI want to "
        "put a goblin column and a troll fetish on the same bench and see if they agree.",
        "They agree.\n\nThe shallow wells went in the first season and the deep well went in the "
        "second, which is a water table dropping, not a drought. The trolls marked it the same way "
        "and started marking it a season before we noticed, because they were LOOKING and we were "
        "selling each other water rates.\n\nSo: a range arrived, the water went under and east, and "
        "four days west of here a walled city died of thirst with its gates open.\n\nNobody did that "
        "on purpose. I am going to write it down anyway, in both columns, and in a hundred years "
        "somebody can be angry about it with the facts in front of them.",
        requires_quests=[FLATS_WATER], nxt="tan_gad_the_press_again"))

    A.append(Q("tan_gad_the_press_again", "Three Carts and a Fourth", ENGINEER, NT, 44, 44,
        "dustdead",
        "Faz Quill has known for three years that the press is immovable.\n\nHe has just been told "
        "why the town died, and has spent one evening with that and come out the other side wanting "
        "to try the press again.",
        [k("Sandfury Axethrower", 10), gather("tan_throwing_axe", 6), gather("tan_pried_fitting", 6)],
        "Here is what I have worked out, and I want to say it once and then not again.\n\nIf the "
        "wells had held, I would still be in that town with that press and a lintel with my name on "
        "it, and I would be poorer and I would be happier. Both of those. I have stopped trying to "
        "pick one.\n\nThe Sandfury have the east gate and I need it clear for a hoist. Ten of the "
        "axethrowers, six axes so I can see what they are using, and six more fittings.",
        "The gate is clear and I have a hoist in my head that will work.\n\nIt will take four carts "
        "and most of a season and Hack will laugh at me for a week.\n\nI am going to do it anyway. "
        "Not because the press is worth it - it is not, I can buy two. Because I would like to take "
        "ONE thing out of that town on purpose instead of being carried out of it."))

    A.append(Q("tan_gad_salvage", "Half of It Came Out of There", BROKER, SP, 42, 43, "dustdead",
        "Broker Nim Catchpenny buys what came off something and sells it to whoever needs it on "
        "something else.\n\nHalf of what crosses her counter came out of Gadgetzan and she will not "
        "pretend otherwise. If that bothers you, it is still for sale.",
        [k("Gadgetzan Scrapjaw", 11), gather("tan_pried_fitting", 7), gather("tan_chewed_ledger", 4)],
        "The scrapjaws nest in the good buildings, which is also where the good brass is, which "
        "means my suppliers and my competition are the same animal.\n\nEleven of them, seven "
        "fittings, four pages. The pages are for Hesper - she pays better for paper than I do for "
        "brass, which tells you something about this town that I find hard to look at directly.",
        "Good brass.\n\nI will tell you the thing I do not say at the counter. Every piece of this I "
        "can name the street for. Not the building - the STREET. I grew up on two of them.\n\nAnd I "
        "still sell it, and I would still sell it tomorrow, because the alternative is that it sits "
        "in a dead town under a bird's nest and nobody gets anything."))

    # ===============================================================================================
    # THREAD 3 - ZUL'FARRAK (5). They did not leave either, and their reason is worse.
    # ===============================================================================================
    A.append(Q("tan_zf_still_there", "Nobody Took the Pyramid", GOODS, NT, 41, 42, "sandfury",
        "Trader Bix Rannow had a shop with a stone front and a name cut into the lintel. It is "
        "standing in a walled town with nobody in it.\n\nFour days further west there is a troll "
        "ruin with a great many people in it, and he thinks about that more than he lets on.",
        [explore(NT, 36, 58, 10), k("Sandfury Scavenger", 10), gather("tan_sandfury_charm", 6)],
        "Everybody calls it the ruins. I have been out there. It is not ruins, it is a BROKEN "
        "BUILDING WITH PEOPLE IN IT, which is a completely different thing and I would like somebody "
        "else to go and confirm it so I can stop sounding mad about it at the bar.\n\nWalk up to the "
        "broken face. Ten of the scavengers on the way and six charms.",
        "People in it. Thank you.\n\nThey did not leave. We left, they did not, and their roof is "
        "off and ours was fine.\n\nI have turned that over for three years and I have never once got "
        "it to come out in our favour.", nxt="tan_zf_what_happened"))

    A.append(Q("tan_zf_what_happened", "What Took the Roof Off", MAZZIC, NT, 42, 43, "sandfury",
        "Something happened at Zul'Farrak and it was not three years ago - the break in that pyramid "
        "is older than anybody in Steamwheedle.\n\nOld Mazzic has heard four versions and believes "
        "none of them, which he considers the correct number.",
        [k("Sandfury Hexxer", 9), gather("tan_hex_fetish", 6), gather("tan_throwing_axe", 5)],
        "Four stories. A flood, a god, a war, and a thing they let out and put back. You will hear "
        "all four in one evening at the bar and every one of them is told by a goblin who has never "
        "been within a mile of it.\n\nNine of the hexxers and six fetishes. The fetishes are the "
        "only thing out there anybody has ever written anything ON. Five of their axes as well, "
        "because an axe tells you who somebody expects to fight.",
        "The fetishes are marked for WATER. All six. Levels, seasons, and a line that is clearly a "
        "low mark because it has been cut over three times.\n\nAnd the axes are made for throwing "
        "at something taller than a troll.\n\nSo they were watching the water long before we were, "
        "and they were expecting something, and neither of those is any of the four stories.",
        nxt="tan_zf_the_marks"))

    A.append(Q("tan_zf_the_marks", "Three Cuts in the Same Stone", CLERK, NT, 43, 43, "sandfury",
        "A low-water mark cut three times is a record. Hesper Dunn knows a record when she sees one "
        "and she wants the rest of it.",
        [explore(NT, 24, 66, 9), k("Sandfury Axethrower", 9), gather("tan_sandfury_charm", 7)],
        "If they cut a mark three times they cut it somewhere permanent, and a fetish is not "
        "permanent. It will be on the pyramid.\n\nThe south face, where the steps are still whole. "
        "Nine of the axethrowers to get a look at it and seven charms - they are grave charms and "
        "the graves are a date, and a date is the thing I am short of.",
        "The marks are on the third step and there are not three. There are eleven.\n\nEleven low "
        "marks, cut over what the grave charms put at about four hundred years, and the last one is "
        "three years old and it is a foot and a half below the one before it.\n\nThey have been "
        "writing down this region's water since before there was a Gadgetzan to die of it. We had "
        "nine wells and a rates ledger. They have eleven marks and a stone.",
        nxt="tan_zf_the_offer"))

    A.append(Q("tan_zf_the_offer", "Somebody Should Go and Ask Them", SURGEON, NT, 43, 44, "sandfury",
        "Nobody in Steamwheedle has ever gone to Zul'Farrak to ask a question. Three years, four "
        "stories, eleven marks, and not one conversation.\n\nSurgeon Wick Ambrose points this out at "
        "the bar and is told he does not understand trolls, by people who have never met one.",
        [k("Sandfury Hexxer", 10), gather("tan_hex_fetish", 7), talk("tan_topic_ask_them")],
        "I am not going to pretend this is a peace mission. You are going to have to go through a "
        "great many of them to stand anywhere a hexxer will hear you, and ten is my estimate and I "
        "am probably low.\n\nSeven fetishes. And come back and tell me what you make of it, because "
        "I would like one person in this town to have an opinion they arrived at by looking.",
        "Seven, and every one of them marked, and you stood on the step and read them.\n\nThat is "
        "more than anyone here has done. It is not a conversation and I am not going to call it "
        "one.\n\nBut the next person who tells me nobody can talk to the Sandfury is going to be "
        "told that somebody walked up their steps and read their water marks and walked back down, "
        "and that we have had three years to do it and did not.",
        nxt="tan_zf_the_axe"))

    A.append(Q("tan_zf_the_axe", "What the Axes Are For", SMITH, SP, 44, 44, "sandfury",
        "Smith Dorga Ironside has been looking at a Sandfury throwing axe on her bench for a "
        "fortnight.\n\nIt is made for throwing at something considerably taller than a troll, and she "
        "has worked out what, and she does not like it.",
        [k("Sandfury Axethrower", 11), gather("tan_throwing_axe", 8), gather("tan_sunstone_core", 5)],
        "The balance is wrong for a person. The haft is short and the head is heavy and it wants to "
        "go up.\n\nEleven of them and eight more axes, and five sunstone cores so I can get my forge "
        "hot enough to test what the heads are tempered for.\n\nI have a guess. I would like to be "
        "wrong and I have not been wrong about a piece of steel in twenty years.",
        "Tempered against heat.\n\nNot against armour, not against hide - against HEAT, the way you "
        "temper a tool that is going to be used near a forge or in a fire.\n\nThey have four hundred "
        "years of water marks and a quarry of axes balanced to throw upward at something that is "
        "hot. I am going to stop being curious about Zul'Farrak now and I would recommend it."))

    # ===============================================================================================
    # THREAD 4 - THE DROWNBELL (5). Ends underground.
    # ===============================================================================================
    A.append(Q("tan_cove_whose_claim", "Filed by a Company Nobody Knows", BANKER, SP, 42, 42, "cove",
        "Strongbox-Keeper Pell holds what people do not want to carry and writes down what they do "
        "not want to forget.\n\nSomebody filed a salvage claim on that cove before the pirates took "
        "it, and the company that filed it does not appear in any book she has.",
        [k("Drownbell Deckhand", 10), gather("tan_cove_tally", 6), gather("tan_crawler_shell", 5)],
        "Before Vaile's crew there was a working party in that cove with a diving bell and a winch "
        "and a claim in order. Then there was not.\n\nTen off the shore, six tallies, and five of "
        "the crawler shells - the crawlers are all over the lower cove and they are eating something "
        "down there, and I would like to know whether it is fish.",
        "Not fish.\n\nThose shells are growing on something metal - you can see the line of it in "
        "the curve. There is a great deal of worked metal on the floor of that cove and somebody was "
        "lifting it before Vaile arrived.\n\nKeep going. I will pay for the answer and I will pay "
        "better than the brokers.", nxt="tan_cove_the_bell"))

    A.append(Q("tan_cove_the_bell", "The Bell Is Real", ENGINEER, NT, 43, 43, "cove",
        "A diving bell, goblin-built, on the floor of a flooded chamber with its chain still on the "
        "winch.\n\nFaz Quill has heard it described three times and has drawn it from the "
        "descriptions and would now like to see it.",
        [explore(DB, 62, 44, 9), k("Drownbell Cutthroat", 10, DB), gather("tan_tide_focus", 5)],
        "In at the mouth, down the dry gallery, and as far as the wet end. Do not go to the bottom.\n\n"
        "Ten of the cutthroats on the way and five of the tidecallers' focuses - they keep the water "
        "moving down there and if I know how, I know whether the bell can still be raised.\n\nI have "
        "wanted to see a working bell since I was eleven years old. This is the closest I have been "
        "and I am sending somebody else, which I am aware of.",
        "It can be raised. The winch is seized and the chain is sound, and seized is a morning's "
        "work with the right bar.\n\nAnd the focuses are keeping a CURRENT in a cave with no tide "
        "in it, which is not weather, that is somebody's doing.\n\nVaile has a reason to keep that "
        "water moving and I would very much like to know what it is.",
        nxt="tan_cove_two_went_down"))

    A.append(Q("tan_cove_two_went_down", "Two of Them Went to Look", BROKER, DB, 43, 44, "cove",
        "The pirates have not touched the bell. Two of them went down to look at it in the first "
        "season and neither came back up.\n\nThat is the only fact about the Drownbell that every "
        "version of the story agrees on.",
        [k("Bilge Crawler", 12, DB), gather("tan_crawler_shell", 7), gather("tan_bosun_whistle", 5)],
        "I buy off Vaile's people. I am not proud of it and I am not going to lie about it to you of "
        "all people.\n\nWhat I will tell you is that the ones who come up to trade will haggle about "
        "anything in that cove except the bottom chamber, and they do not refuse, they just go "
        "quiet.\n\nTwelve of them, seven shells, five whistles. The whistles are how they "
        "call each other down there and I want to know if there is a call for the bottom.",
        "There is a call for the bottom and it is the same call as abandon ship.\n\nI have been "
        "buying off these people for two years and I did not know that, and now I do, and I am going "
        "to have to decide what I think about a crew that keeps working a hole they have a retreat "
        "signal for.", nxt="tan_cove_the_warden"))

    A.append(Q("tan_cove_the_warden", "Something Is Still Guarding It", KEEL, DB, 44, 44, "cove",
        "Shipwright Hald Keelmaker has worked out what is between the pirates and the bell, and it "
        "is not the water.\n\nSomebody left a watch on that salvage and the watch has not been told "
        "to stop.",
        [k("Drownbell Bosun", 10, DB), gather("tan_bosun_whistle", 6), gather("tan_tide_focus", 6)],
        "A careenage. They haul a hull over on that ground to work the bottom of it, which means "
        "that cove was a WORKING YARD before it was a pirate hole, and a working yard has a "
        "watchman.\n\nTen of them, six whistles, six focuses. I am not asking you to go to the "
        "careenage yet. I am asking you to take the cove's middle off its feet first, because "
        "whatever is on that ground, you do not want it and Vaile's crew behind you at once.",
        "That is the middle of the cove cleared and the way to the careenage open.\n\nWhatever is "
        "standing on that ground has been standing on it since before Vaile, and it is not hers, and "
        "it is not going to care which of you it is looking at.\n\nGo carefully. And when you have "
        "done it, there is still a captain at the bottom.", nxt="tan_cove_vaile"))

    A.append(Q("tan_cove_vaile", "Captain Vaile Drownbell", HARBOUR, DB, 44, 44, "cove",
        "She took this cove off people who were only trying to lift something out of it, and she has "
        "held it for two years without once going to the bottom of her own cave.\n\nSenna Coil wants "
        "the cove because a harbourmaster with pirates a mile down the coast is not a harbourmaster, "
        "she is a hostage with a ledger.",
        [boss("Captain Vaile Drownbell"), k("Cove Tidecaller", 9, DB), gather("tan_tide_focus", 7)],
        "The bottom chamber. Through the wet gallery and down.\n\nNine of the tidecallers first - "
        "they are the ones keeping that water moving and I would rather you fought her in still "
        "water than in her own current. Seven focuses, which Quill wants and which I am going to let "
        "him have because he has earned it.\n\nAnd Vaile. I have six berths now and I would like to "
        "use all six.",
        "She is down. And she never went to the bottom of her own cove in two years, which I have "
        "now had confirmed by somebody who has.\n\nThe bell is still there. The claim Pell found is "
        "still unanswered. Whoever filed it is still not in any book.\n\nI have a cove I can police "
        "and a harbour I can run and a hole in my own records, and I will take two out of three."))

    # ===============================================================================================
    # THREAD 5 - THE ROAD (4). The other end of a conversation two zones have already had.
    # ===============================================================================================
    A.append(Q("tan_road_nothing_back", "Nothing Coming Back Worth the Axle", AGENT, NT, 41, 42,
        "roadwest",
        "Agent Rullo Tack could run a cart north onto the pan tomorrow. He has not, and the reason "
        "is not the hives.\n\nThe reason is that a cart goes out full and comes back empty, and an "
        "empty cart is a wage with no freight under it.",
        [k("Dunecrest Raptor", 11), gather("tan_raptor_claw", 6), explore(NT, 140, 62, 10)],
        "Everybody assumes it is danger. It is arithmetic.\n\nThe raptors have the middle of the "
        "road and eleven of them would make the crossing a proposition rather than a gamble - six "
        "claws so I can price the guard hire properly.\n\nAnd walk the nineteen-mile stretch while you "
        "are out. That is where the axles go and I want to know if it is the surface or the load.",
        "The surface. It is the surface, it has always been the surface, and a season of cart "
        "traffic would pack it flat and then it would stop being the surface.\n\nWhich is a thing I "
        "cannot fix by not running carts on it. I have been standing on the wrong side of that for "
        "a year.", nxt="tan_road_the_bones"))

    A.append(Q("tan_road_the_bones", "Everything That Stops Is Theirs", SURGEON, NT, 42, 43,
        "roadwest",
        "The bonefields either side of the caravan road are not a graveyard. They are a feeding "
        "ground with a very long history and a very regular supply.\n\nWick Ambrose would like to "
        "know what the supply was before there were carts.",
        [k("Bonefield Hyena", 11), gather("tan_hyena_jaw", 7), gather("tan_vulture_quill", 5)],
        "Bone out there goes down four feet and the top foot is kodo and cart ox and the rest is "
        "not.\n\nEleven of them, seven jaws, five quills. The jaws will tell me what has been "
        "eating out there this century. The quills are for me - a sun-stiff quill makes the best "
        "splint-splice I have ever used and I will not apologise for the detour.",
        "The jaws are all one animal and the animal has not changed. Whatever has been dying on that "
        "road has been dying on it for a very long time, in roughly the same numbers, through a "
        "goblin city rising and falling and a mountain arriving.\n\nThe road is older than any of "
        "us. We have been using somebody else's road and calling it ours.",
        nxt="tan_road_the_salt"))

    A.append(Q("tan_road_the_salt", "The Woman on the Pan", FISH, SP, 43, 43, "roadwest",
        "Fishmonger Oda Brack buys her salt off a woman on the pan who has never once been late in "
        "eleven years.\n\nShe has never met her, and until this season she had never thought that "
        "was strange.",
        [k("Thornback Scorpid", 10), gather("tan_scorpid_barb", 7),
         deliver("tan_fish_order", "Jixa Brinecount, Saltwheel")],
        "Her town is dying and my town is not and she still gets the cart out. That is the whole "
        "trade, really - somebody keeps turning up.\n\nTake her this. It is an order for next season "
        "and it is bigger than last season, which I would like her to hear from a person rather than "
        "read off a slip.\n\nTen of them off the dry crossing and seven barbs on the way - "
        "the crossing is the worst of it and I would rather you did it light.",
        "[Jixa Brinecount reads the order twice and then puts it down and does not pick it up "
        "again.]\n\nBigger than last season.\n\nEleven years she has been buying off me and not one "
        "of those years did the number go up. It went DOWN in the second one and I did not say "
        "anything and neither did she.\n\nTell her yes. Tell her the cart will be there. Tell her "
        "it was always going to be there, which she knows, and tell her anyway.",
        turn_in_npc_id="sw_salt_buyer",
        grant_items=carry("tan_fish_order", "Oda's Standing Order",
                          "Next season's salt, and the number is bigger than last season's."),
        nxt="tan_road_the_cart"))

    A.append(Q("tan_road_the_cart", "A Cart Both Ways", AGENT, NT, 44, 44, "roadwest",
        "An order going north and salt coming south is freight in both directions, which is the one "
        "thing Rullo Tack has been waiting for.\n\nHe is going to be unbearable about having been "
        "right that it was arithmetic.",
        [k("Sunstone Elemental", 9), gather("tan_sunstone_core", 6), gather("tan_raptor_claw", 6),
         explore(NT, 112, 72, 9)],
        "Freight both ways. That is a route. That has always been the only thing standing between "
        "this and a route.\n\nThe elementals are sitting on the dry crossing where the surface is "
        "worst and nine of them clears the worst mile. Six cores and six claws - the cores go to "
        "Hack for the road crew and the claws price the guard hire.\n\nAnd walk the crossing one more "
        "time. If it is still the surface I will say so in writing and eat it.",
        "First cart goes in eleven days.\n\nI will tell you what I have not told Oda. The order "
        "going north is not what makes this work - it is small, it is fish money. What makes it work "
        "is that somebody on that pan now believes a cart is coming, and a town that believes a cart "
        "is coming starts getting freight ready for it.\n\nThat is the whole trade. Somebody has to "
        "go first and be slightly wrong about the numbers."))

    # ===============================================================================================
    # STANDALONES (4) + TWO ITEM-STARTERS
    # ===============================================================================================
    A.append(Q("tan_solo_beds", "Forty Beds", INNKEEP, SP, 41, 41, "quay",
        "Innkeeper Mirabel Sump has forty beds and has had forty beds since her mother ran the "
        "house.\n\nThe town has twice the people it did three years ago.",
        [k("Carrion Vulture of Tanaris", 10), gather("tan_vulture_quill", 6)],
        "I could put twenty more upstairs and I am not going to, and the reason is that the day I do "
        "it the yard crowd stop sleeping in their own sheds and start sleeping in my house, and then "
        "I am running a barracks.\n\nThe vultures have found the kitchen midden. Ten of them and six "
        "quills - I sell the quills and the quills are most of what I make on a bad week, which is a "
        "thing I would rather you did not repeat.",
        "Off the midden and off my roof.\n\nForty beds. My mother had forty beds in a town of three "
        "hundred and she turned nobody away, and I have forty beds in a town of nine hundred and I "
        "turn people away every night.\n\nThat is not a complaint about the newcomers. That is a "
        "complaint about me, and I know the difference, and I am working on it."))

    A.append(Q("tan_solo_salt_air", "Salt Air or Dry Sand", SMITH, SP, 42, 42, "yard",
        "Smith Dorga Ironside tempers for one or the other and cannot temper for both.\n\nEverything "
        "she makes goes onto a ship or into the desert, and the two of them want opposite things "
        "from a piece of steel.",
        [k("Sunstone Elemental", 10), gather("tan_sunstone_core", 7)],
        "Hot work, and it is hot already, so I am at the anvil before the sun and done when it is "
        "overhead.\n\nTen of the elementals and seven cores. A core holds a working heat for half a "
        "day without a bellows, which in this climate is the difference between a trade and a "
        "punishment.",
        "Seven cores is a season of mornings I do not have to pump for.\n\nAnd before you ask - no, "
        "I will not temper you something that does both. Anybody who tells you they can is selling "
        "you a story. Pick the sea or pick the sand and I will do it properly."))

    A.append(Q("tan_solo_bird", "Bring Me the Town That Makes Me Wrong", KEZZIK, NT, 42, 43,
        "roadwest",
        "Wind-Rider Kezzik is the only flight master for a very long way and prices like it.\n\nHe "
        "gets asked about the pan north of here at least once a week, always by somebody who has "
        "just walked off it.",
        [explore(NT, 92, 20, 9), k("Carrion Vulture of Tanaris", 11), gather("tan_vulture_quill", 7)],
        "There is a post out on that pan. There is no BIRD on it, because a bird needs feeding and a "
        "feeding needs somebody paying, and six customers do not pay for a wyvern.\n\nI am not being "
        "hard about it. I would love to be wrong.\n\nThe carrion birds nest in the pass and they "
        "harry my runs - eleven of them and seven quills, and the quills are for fletching, which is "
        "a wyvern-keeper's problem nobody expects.",
        "The pass is clear and I will take the run lower through it from now on.\n\nAnd I meant it. "
        "Bring me the town that makes me wrong. If there is ever freight on that pan going both ways "
        "I will put a bird out there myself and charge them half what I charge you, and I will enjoy "
        "being told I was wrong about it more than I will enjoy the money."))

    A.append(Q("tan_solo_counter", "Nothing Has Changed at This Counter", CHANDLER, SP, 43, 44,
        "quay",
        "Chandler Vex Tarrow's grandfather chandlered this quay and his father before him.\n\nHe "
        "will tell you what has changed: nothing, at this counter. Everything, forty yards that way.",
        [k("Drownbell Powdermonkey", 11), gather("tan_cove_tally", 7), gather("tan_crawler_shell", 6)],
        "Rope, pitch, canvas, lamp oil. Same four things, same prices adjusted for the same reasons, "
        "same counter.\n\nThe cove crews have been taking pitch off the quay at night and pitch is "
        "the one thing I cannot make and cannot replace inside a season. Eleven of them, seven "
        "tallies, six shells.\n\nI am aware that forty yards that way they have invented three new "
        "trades since the wet. I am not competing with that. I am selling rope.",
        "That is my pitch back and then some.\n\nI will tell you the thing I have never said out "
        "loud in this shop. The yard is the best thing that has happened to this quay in a hundred "
        "years. Every one of those new trades needs rope.\n\nMy grandfather would have hated them "
        "and he would have sold to them and he would have been rude about it for forty years, and I "
        "have decided to skip the rude part."))

    A.append(Q("tan_item_well_token", "A Number Too High for Three Years",
        "item:tan_well_token", NT, 42, 43, "dustdead",
        "You turn the token over. Stamped brass from Gadgetzan's public well, dated three years ago "
        "and numbered in the eleven thousands.\n\nEleven thousand draws from a public well in a town "
        "of four hundred, in one season. Somebody was drawing and drawing and the well was giving "
        "less every week.",
        [deliver("tan_well_token", "Old Mazzic, Steamwheedle Port"), k("Gadgetzan Scrapjaw", 9)],
        "Four days east, to the port, and into the hand of the only person there who will know what "
        "the number means.\n\nNine of the scrapjaws on your way out of the city. They nest where the "
        "tokens are, which is to say where the queue was.",
        "[Old Mazzic turns it over and reads the number and does not say anything for a while.]\n\n"
        "Eleven thousand four hundred and six.\n\nThat is the season I was carried out. I stood in "
        "that queue. Not at the end of it - I was somewhere around nine thousand, which means I got "
        "water, which means somebody behind me did not.\n\nI have spent three years telling this "
        "town I was carried out of a city. I was carried out of a QUEUE. That is a different "
        "sentence and I have not been saying it.", salt="b"))

    A.append(Q("tan_item_salvage_claim", "Countersigned Twice",
        "item:tan_salvage_claim", DB, 43, 44, "cove",
        "You turn the claim over. Salvage rights on something in the Drownbell, filed in order and "
        "countersigned twice - once by a company nobody in Steamwheedle has heard of, and once by a "
        "hand that did not write its name, only a mark.\n\nWhoever held this was lifting something "
        "out of that cove and had every right to.",
        [explore(DB, 44, 58, 8), k("Drownbell Bosun", 8, DB),
         deliver("tan_salvage_claim", "Strongbox-Keeper Pell, Steamwheedle Port")],
        "The careenage first - whoever filed this worked that ground, and a working party leaves "
        "more behind than a crew does.\n\nEight of the bosuns to get there and back. Then take it to "
        "the only person in the port who keeps a book of who is allowed to own what.",
        "[Pell lays it flat and goes through four ledgers without finding the company, which takes "
        "a long time, and she does not hurry it.]\n\nNot in any book I hold. Not in any book the "
        "harbourmaster holds either, I checked those last winter.\n\nThe mark, though. The mark I "
        "have seen. It is on two deposits in my own strongroom, both of them unclaimed, both of them "
        "lodged the season before Vaile took that cove.\n\nSomebody is still owed something down "
        "there, and they are not coming for it, and I am going to have to work out why.", salt="c"))

    return A


CASTER_WEAPONS = {"staff", "wand", "tome", "idol", "libram", "totem", "mace_1h"}
RARES = {"Thaka the Unburied", "The Last Tenant", "Nineteen Mile", "Marrowmaw", "Saltjaw",
         "The Drowned Purser", "The Bellwarden"}


def audit(quests):
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
    sourced = {i for rows in FETCH_DROPS.values() for (i, *_r) in rows}
    sourced |= {i for rows in STARTER_DROPS.values() for (i, *_r) in rows}
    for q in quests:
        granted = {g["item_id"] for g in (q.get("grant_items") or {}).get("on_accept", [])}
        granted |= {g["item_id"] for g in (q.get("grant_items") or {}).get("on_turn_in", [])}
        for o in q["objectives"]:
            if o.get("target") in RARES:
                bad.append(f"{q['quest_id']}: objective targets the named rare {o['target']}")
            if o["type"] in ("fetch", "gather", "deliver"):
                t = o.get("target")
                if t not in sourced | granted | set(STARTER_IDS):
                    bad.append(f"{q['quest_id']}: {o['type']} '{t}' has no drop source and the quest "
                               f"does not grant it - uncompletable")
        for it in q.get("unique_item_defs", []):
            res = [kk for kk in (it.get("secondary_stats") or {}) if "resistance" in kk]
            if res:
                bad.append(f"{q['quest_id']}: {it.get('name')} has resistance stats below 45")
        for f in ("description", "accept_text", "turn_in_text"):
            if "escort" in q[f].lower():
                bad.append(f"{q['quest_id']}: the word 'escort' in {f}")
            if len(q[f]) > 760:
                bad.append(f"{q['quest_id']}: {f} is {len(q[f])} chars (hard cap 760)")
            if not q[f].isascii():
                bad.append(f"{q['quest_id']}: {f} is not ASCII")
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    quests = build()
    ids = [q["quest_id"] for q in quests]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids")
        return 1
    here = set(ids)
    for q in quests:
        nx = q.get("next_quest_id")
        if nx and nx not in here:
            print(f"FAILED: {q['quest_id']} chains to {nx}, which this pass does not define")
            return 1
    d = json.loads((ROOT / "data/quests/shimmering_flats.json").read_text(encoding="utf-8"))
    have = {q["quest_id"] for q in d["quests"]}
    if FLATS_WATER not in have:
        print(f"FAILED: the water gate requires {FLATS_WATER}, not in shimmering_flats.json")
        return 1
    print(f"water gate: {FLATS_WATER}, live in the Shimmering Flats")

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
    gated = sum(1 for q in quests if q.get("requires_quests"))
    starters = sum(1 for q in quests if str(q["giver_npc_id"]).startswith("item:"))
    hist = {}
    for q in quests:
        for o in q["objectives"]:
            hist[o["type"]] = hist.get(o["type"], 0) + 1
    print(f"Tanaris quests: {len(quests)} total, {chains} chained, {gated} gated, "
          f"{starters} item-starters")
    print("  objectives: " + ", ".join(f"{k_} {v}" for k_, v in
                                       sorted(hist.items(), key=lambda kv: -kv[1])))
    print("  zones touched: " + ", ".join(sorted({q["zone"] for q in quests})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
