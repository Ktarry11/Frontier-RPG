#!/usr/bin/env python3
"""
Glittervein + The Mother Vein + The Cistern quest pass. Idempotent. 46-52.

    PYTHONPATH=. python3 tools/build_glittervein_quests.py
    PYTHONPATH=. python3 tools/audit_quests.py
    PYTHONPATH=. python3 tools/qa_quest_lore.py --zone glittervein --show

THIRTY-FOUR quests, and they are the last ones in a conversation that has been running across five
zones without anybody in any of them knowing it was one conversation.

=========================================================================================================
THE CHAIN, AND WHY THIS IS WHERE IT ENDS
=========================================================================================================
  THE ASPEN WILDERNESS       somebody is watching the melt get bigger every spring and cannot say why
  SOUTHERN THOUSAND NEEDLES  somebody is asking where all that water goes and getting no answer
  THE SHIMMERING FLATS       the answer: it arrives, it always has, it goes under, it goes east
  NORTHERN TANARIS           a walled city died of thirst with a well in the middle of it
  THE ABYSSAL SANDS          and then the floor fell in
  GLITTERVEIN                the water is HERE, and it did not come here on its own

Every one of those five was written as a local problem with a local cause, and at every one of them
an NPC says so. Ulla Stormhollow has walked all five in the same order as the player, four years
ahead of them, for a different reason - and she is the only person in the game who has the whole
sentence. The water in that pool did not gather. It was PULLED, by something that has been drinking
since the Integration, and it is at the top of the dungeon.

That is also why the zone's out-chain goes BACKWARD. Gadgetzan's survivors are four days west in
Steamwheedle and have spent three years being told their city died of bad luck. gv_tell_them_why
carries the arithmetic to Old Mazzic, who was carried out of that city on a door.

=========================================================================================================
THREADS
=========================================================================================================
  THE RIM AND THE WAY DOWN (5)  Arriving, descending, and the first green anybody has seen in Tanaris.
  THE DEADLOCK (6)              The Company want the dig reopened, the Survey want it understood
                                first, and neither can move without the other. Resolves in a WORKS
                                ORDER and a measurement, not a fight.
  THE WATER CHAIN (6)           Ulla's thread, gated on the Gadgetzan answer three zones back. Ends
                                by opening the dig.
  THE SEAMS (5)                 The crystal, the cutter, and why magic resistance exists at all.
  THE MOTHER VEIN (5)           The dungeon's upper half. Three pinned bosses.
  THE CISTERN (5)               The lower half, four pinned bosses, and the thing at the top of it.
  OUT OF THE ZONE (2)           East to Steamwheedle, to tell them what killed Gadgetzan.

NO ESCORTS. NO QUEST TARGETS A NAMED RARE - Thirstjaw, Old Riser, Shatterlight, Rootbound and
Stillwater are lore and loot and nothing else. The seven dungeon bosses are PINNED by
boss_positions, so kill_boss on them is legitimate.

MAGIC RESISTANCE IS A QUEST REWARD HERE AND NOWHERE EARLIER. The rule is 45+; this band is 46-52,
and the Abyssal Sands declined it at 44-47 on purpose so that this zone could have it as a theme.
Kyle: most of it goes on TANK gear, which the loot pass already enforces.
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

OUT = ROOT / "data/quests/glittervein.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

GV = "glittervein"
MV = "the_mother_vein"
CI = "the_cistern"

#: Extrapolated at the same +80 XP and +300 gold per level the bands below this one use.
XP = {46: 3320, 47: 3400, 48: 3480, 49: 3560, 50: 3640, 51: 3720, 52: 3800}
GOLD = {46: 13200, 47: 13500, 48: 13800, 49: 14100, 50: 14400, 51: 14700, 52: 15000}

tirisfal_gear.THEMES.update({
    "lastwater": (["Lastwater", "Bedroll", "Eleven-Month", "Camp-Issue", "Still-Here"],
                  ["Camp kit off a rock nobody can leave quickly.",
                   "Provisioned for ninety and issued to ten.",
                   "It has been at the bottom of a hole long enough to stop smelling of anything.",
                   "Somebody carried this down the spiral and never carried it back up."]),
    "seam": (["Vein-Cut", "Glass-Backed", "Seam-Set", "Cutter's", "Shrug-Off"],
             ["Backed with vein glass, which is the only stone in the world that ignores a spell.",
              "Cut, backed and set by somebody who has four months of stock left.",
              "There is one seam like this anywhere and you are standing in the hole it came from.",
              "Cold to the touch and it has never been near water."]),
    "cenote": (["Terrace", "Green-Shelf", "Waterline", "Spiral-Walked", "Rim-Dry"],
               ["Damp, in a desert, which is the whole argument of this place.",
                "Ferns got at it. Nothing in Tanaris has fern on it.",
                "Carried down forty-six feet of cut road.",
                "The only thing growing for a hundred miles grew on this."]),
    "deepvein": (["Dig-Head", "Pitboss's", "Drowned-Gallery", "Shift-Worn", "Four-Hundred-Foot"],
                 ["Company issue, and the company stopped issuing a year ago.",
                  "It was four hundred feet down when the water came up to meet it.",
                  "Goblin work, and the last of it anybody did down there.",
                  "Still on shift, in the sense that nobody ever called the shift."]),
    "cistern": (["Cistern", "Outflow", "Thirst-Denying", "Drawn-Dry", "Water-Table"],
                ["It came out of the room the whole region's water is in.",
                 "Five zones went into making this wet.",
                 "The seam gave up trying to grow through it.",
                 "Carried up the channel the water takes, which is how anybody gets out."]),
})


def k(target, n, zone=GV):
    return kill(target, n, zone=zone)


def boss(target, zone):
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
    """The item the giver hands you, for a deliver objective.

    PASSED AS grant_items=carry(...), never splatted. Splatting it puts an "on_accept" key at the
    top level of the quest, which the engine does not read and which looks exactly like a working
    grant - two Shimmering Flats quests shipped uncompletable that way and the audit waved them
    through, because the audit was checking a hardcoded list instead of the quest's own data."""
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


# ---- givers. Every id is already in tools/glittervein_npc_roster.py; this pass invents nobody.
MARN = "gv_dig_boss"            # Dig-Boss Marn Cobble - eleven months of nothing, and a figure
PUMP = "gv_pump_chief"          # Pump-Chief Grizzik Thane - nine days, for eleven months
CLERK = "gv_tally_clerk"        # Tally-Clerk Oss Pinch - the same book proves both things
ULLA = "gv_surveyor"            # Ulla Stormhollow - started at the Aspen melt four years ago
DIVER = "gv_diver"              # Diver Sanna Creel - nine times in, nine times out
COOK = "gv_innkeeper"           # Cook Brodd Kettlewick - eleven bedrolls and a memorandum
QUART = "gv_quartermaster"      # Quartermaster Dez Hobbin - provisioned for ninety
CUTTER = "gv_crystal_cutter"    # Cutter Vessa Quill - four months of stock left
BREW = "gv_reagents"            # Brewer Nix Pallow - stands in what they sell at four silver
SMITH = "gv_smith"              # Smith Harla Benttooth - pumps for two years, weapons for one

#: THE FAR GATE. A finished quest two zones and five levels back, in Northern Tanaris: the one
#: where the player finds out Gadgetzan's wells went dry because the water table tipped. Ulla's
#: thread is gated on it because her whole argument is the next sentence after that one, and a
#: player who has not had the Gadgetzan answer has no idea why a tauren with a notebook matters.
TANARIS_WATER = "tan_gad_the_answer"

#: Delivered to Old Mazzic in Steamwheedle - the goblin who did not leave Gadgetzan, he was carried
#: out of it on a door by two people whose names he never got.
MAZZIC = "stw_old_gadgetzan"

FETCH_DROPS = {
    "Shardback Crawler": [("gv_salvaged_iron", "Salvaged Housing Iron",
                           "Chewed off a pump casing on the spoil heap and not improved by it.",
                           0.40),
                          ("gv_rough_seam_glass", "Rough Vein Glass",
                           "Broken off the exposed face. Cold the moment anything is cast near it.",
                           0.34)],
    "Sunbleached Stalker": [("gv_scav_tally", "Scavenger's Scratch-Tally",
                             "Notches for everything that came up the road and did not go back down.",
                             0.34)],
    "Lattice-Grown": [("gv_lattice_core", "Lattice Core",
                       "The piece in the middle that the rest of it grew out from.", 0.32),
                      ("gv_rough_seam_glass", "Rough Vein Glass",
                       "Broken off the exposed face. Cold the moment anything is cast near it.",
                       0.36)],
    "Vein-Lit Wisp": [("gv_settled_light", "Settled Vein-Light",
                       "It keeps shining after the thing that was carrying it has stopped.", 0.36)],
    "Pool Horror": [("gv_sealed_deepwater", "Sealed Deepwater Flask",
                     "Water from the bottom of the only pool in Tanaris, in Nix's leaded glass.",
                     0.40)],
    "Sodden Digger": [("gv_shift_token", "Shift Token",
                       "Brass, stamped with a number, and the number is still on the board.", 0.38)],
    "Glass Weaver": [("gv_spun_glass", "Spun Vein-Glass",
                      "Drawn out into a thread by something that had a reason to.", 0.34)],
    "Shelf Prowler": [("gv_shelf_blindweed", "Blindweed Cutting",
                       "Pulled out of the bed the prowler had flattened to sleep in.", 0.42)],
    "Waterline Serpent": [("gv_tideglass_core", "Tideglass Core",
                           "Grown in moving water, and it has a grain that says which way.",
                           0.38)],
    "Seam Singer": [("gv_struck_shard", "Struck Shard",
                     "It is still ringing. It has been out of the Choir for a day.", 0.36)],
}

STARTER_DROPS = {
    "Terrace Basilisk": [("gv_bench_marker", "Survey Marker, Bent",
                          "Driven into the second terrace by somebody methodical, and chewed.",
                          0.22)],
    "Cistern Lurker": [("gv_drowned_ledger", "Waterlogged Ledger",
                        "Company accounts, four hundred feet down, and the last entry is a date.",
                        0.24)],
}
STARTER_IDS = {"gv_bench_marker": "gv_who_drove_this", "gv_drowned_ledger": "gv_last_entry"}


def build():
    q = []

    # ================= THE RIM AND THE WAY DOWN (5) =================
    q.append(Q("gv_the_lip", "The Lip of It", QUART, GV, 46, 46, "cenote",
               "Stand on the rim and look in before you start down. Everybody does it once.",
               [explore(GV, 86, 30, 10), talk("gv_the_hole", "gv_lastwater")],
               "You came down the pass from the Sands, so you have already seen what a hole in "
               "limestone looks like when the water has gone. Walk to the edge of this one and "
               "look at what it looks like when the water has NOT.\n\nThere is green down there. "
               "Four days in any direction from here there is no green at all.",
               "It stops people. It has stopped every single person who has come over that rim "
               "since I have been here, and I have watched a lot of them do it.\n\nThe ones who came through with the change stop longest. I think it is because they have somewhere to compare it to and the rest of us do not.",
               nxt="gv_jackals_at_the_lip"))

    q.append(Q("gv_jackals_at_the_lip", "What Waits at the Top", COOK, GV, 46, 46, "cenote",
               "The jackals have learned where the tired come up.",
               [k("Rimfall Jackal", 8)],
               "Nothing on that rim lives off the rim. There is nothing up there to live off. They "
               "are up there because everything that comes OUT of the hole comes out slowly, and "
               "they have had three years to work that out.\n\nThin them where the road crests. "
               "That is where they sit.",
               "Better. A cart gets up that last stretch at walking pace with everyone pushing, "
               "and that is not a moment you want to be fighting."))

    q.append(Q("gv_what_climbs_out", "What Comes Up the Road", QUART, GV, 46, 47, "cenote",
               "Someone has been working the top of the haul road, and it is not jackals.",
               [k("Sunbleached Stalker", 6), fetch("gv_scav_tally", 4)],
               "We have lost three loads off the top of the road this season and jackals do not "
               "take crates.\n\nThey keep a tally. I want to see it, because I would like to know "
               "whether they have been counting OUR carts or everybody's.",
               "Everybody's. Four years of notches and a third of them are older than this camp.\n\n"
               "So they were up there before the dig was, waiting on a road that did not exist "
               "yet. That is patience, and I do not like what it says about them.",
               salt="b"))

    q.append(Q("gv_the_long_way_down", "One Lap", COOK, GV, 46, 47, "cenote",
               "Walk the haul road to the bottom. All of it, once, on foot.",
               [explore(GV, 58, 94, 8), talk("gv_the_road", "gv_the_water")],
               "There is one road down and it goes round the hole once. Goblins cut it wide "
               "enough to turn a cart on and then spent four years arguing about whether that was "
               "worth it.\n\nWalk it to the shore. Do not take the short way; there is no short "
               "way, and the people who have gone looking for one are a story I tell at the fire.",
               "Forty-six feet of cut road and the air changes about two thirds of the way down. "
               "Everyone notices and nobody expects to."))

    q.append(Q("gv_first_green", "The Only Green in Tanaris", BREW, GV, 47, 47, "cenote",
               "The shelf above the waterline is the only living ground in the region.",
               [k("Shelf Prowler", 7), fetch("gv_shelf_blindweed", 5)],
               "I brew with the only clean water for a hundred miles, which makes me either the "
               "luckiest brewer alive or the one with the shortest supply line, and I have not "
               "decided.\n\nThe shelf has blindweed on it. Nothing else in Tanaris does. Bring me "
               "some, and clear the prowlers off it while you are there - they have had three "
               "years of nothing competing with them and it has made them bold.",
               "Three years ago this hole had a dozen things living in it. Now it has everything "
               "that could find it. The green is not getting bigger; the crowd is.",
               salt="c"))

    # ================= THE DEADLOCK (6) =================
    q.append(Q("gv_eleven_months", "Eleven Months", MARN, GV, 47, 47, "lastwater",
               "The Dig-Boss would like somebody new to hear his side of it.",
               [talk("gv_the_company", "gv_the_flood"), explore(GV, 86, 100, 6)],
               "Eleven months. Eleven months of paying ninety people's wages out of a hole that "
               "has produced nothing, and the ledger in Steamwheedle calls that MY fault.\n\nIt "
               "was not my fault. We were four hundred feet down a clean seam when the water came "
               "up to meet us, and water does not come UP. Not here. Not in a desert.\n\nGo and "
               "stand at the mouth. Then come back and tell me whether a man should be closing "
               "that or opening it.",
               "You looked a long time. Everybody does.\n\nShe will tell you it was pulled. I have "
               "been told a lot of things by a lot of people in three years and most of them "
               "started with the world changing and ended with me owing somebody money.",
               nxt="gv_the_other_two_pumps"))

    q.append(Q("gv_the_other_two_pumps", "Four of Mine and Two of Hers", PUMP, GV, 47, 48,
               "lastwater",
               "Six pumps. Two of them work, and they are not the Company's two.",
               [k("Shardback Crawler", 8), fetch("gv_salvaged_iron", 6)],
               "I can clear the first gallery in nine days. I have been able to clear the first "
               "gallery in nine days for eleven months.\n\nWhat I cannot do is cast new housings "
               "out of nothing, and the crawlers have been eating the iron off the spoil heap "
               "faster than I can pick it over. Get me the iron and get them off it.",
               "Nine days. That is all it has ever been. Nine days and two people saying the same "
               "sentence on the same afternoon, and I have had neither for a year.\n\nI built pumps for twenty years before the world changed and I was good at it, and now I am a man with four broken housings on a rock.",
               nxt="gv_the_book"))

    q.append(Q("gv_the_book", "The Same Book", CLERK, GV, 48, 48, "lastwater",
               "Nine hundred and forty-one days of water level, and both sides read it their way.",
               [deliver("gv_tally_book", "Oss Pinch's water-level book, to Ulla Stormhollow"),
                talk("gv_the_book_topic")],
               "Nine hundred and forty-one days of water level, taken at dawn, written down "
               "whether anybody wanted it or not.\n\nThe Boss says my book proves the flood is "
               "seasonal. Ulla says my book proves it is not. It is the SAME BOOK.\n\nTake it to "
               "her. I would like to watch somebody else carry it across the camp for once.",
               "She did not argue with it. That is the part that worries me - she read it for an "
               "hour and then asked what the weather had been doing four days WEST.",
               nxt="gv_same_book", grant_items=carry("gv_tally_book", "Oss Pinch's Water-Level Book",
                                           "Nine hundred and forty-one dawns, in a very small hand.")))

    q.append(Q("gv_same_book", "Both of Them Are Reading It Right", CLERK, GV, 48, 48, "lastwater",
               "Get the argument stated plainly by both sides, in order, in one afternoon.",
               [talk("gv_the_company", "gv_the_survey", "gv_the_book_topic")],
               "I have started to suspect a number is only ever worth what the person reading it "
               "already believed, which is a terrible thing for a clerk to work out about "
               "herself.\n\nGo and get it said. Him first, her second, and come back and tell me "
               "if I am wrong.",
               "You are not going to tell me I am wrong, are you.\n\nThen I will keep taking it at "
               "dawn, and one of them will be right eventually, and my book will have been right "
               "the whole time without ever helping anybody."))

    q.append(Q("gv_the_wet_test", "Where It Is Coldest", ULLA, GV, 48, 49, "lastwater",
               "Water from the deep end of the pool, sealed, where nobody has stirred it.",
               [k("Pool Horror", 7), fetch("gv_sealed_deepwater", 5)],
               "I need water from the bottom of that pool and I need it SEALED, because the "
               "argument I am about to make rests on how cold it is and air ruins that in "
               "minutes.\n\nThere is something in the deep end that objects. It has objected to "
               "Sanna nine times.",
               "Colder than the pool it came out of. Four degrees colder, consistently, from the "
               "deep end - and the Flats have been saying the water goes east for longer than any of us have been here, since well before the change.\n\n\n\nWater does not refrigerate itself. That water has come a very long "
               "way underground and it has come FAST, and I can now say so with a figure attached."))

    q.append(Q("gv_who_drove_this", "Somebody Methodical", "item:gv_bench_marker", GV, 47, 48,
               "cenote",
               "A survey marker, bent, driven into the second terrace by somebody who knew how.",
               [deliver("gv_bench_marker", "the bent marker, to Ulla Stormhollow"),
                k("Terrace Basilisk", 6)],
               "It is a surveyor's marker, driven properly, into a bench of a hole four days from "
               "the nearest road. Somebody has been doing this work down here before, and doing it "
               "well.",
               "That is mine. Third season, before the camp existed.\n\nI have driven forty of "
               "those between the Aspen and here and I have never once come back and found one. "
               "You have no idea what it is like to be handed proof that you were somewhere.",
               salt="d"))

    q.append(Q("gv_works_order", "A Works Order, Not a Fight", MARN, GV, 49, 49, "lastwater",
               "Both halves of the camp sign the same piece of paper, finally.",
               [talk("gv_the_works_order"),
                deliver("gv_works_order_paper", "the countersigned works order, to Pump-Chief Thane")],
               "She has a figure. I have hated that woman for eleven months and she has a figure "
               "and I can do arithmetic.\n\nSo: nine days of pumping on the first gallery, her two "
               "housings and my four, and she gets a man on the face the whole time writing down "
               "what we find. I will sign that. I am not going to enjoy signing that.\n\nTake it "
               "to Thane before I read it again.",
               "He signed it. He SIGNED it.\n\nNine days. Tell everybody. Tell the cook first, he "
               "is the one who has had to seat them.",
               grant_items=carry("gv_works_order_paper", "Countersigned Works Order",
                       "Two signatures, eleven months apart in temperament and four inches apart "
                       "on the page.")))

    # ================= THE WATER CHAIN (6) =================
    q.append(Q("gv_five_places", "Five Places, In Order", ULLA, GV, 48, 49, "cenote",
               "The tauren with the notebook has walked where you have walked, four years ahead.",
               [talk("gv_the_chain", "gv_the_melt")],
               "You came here through the Sands. Before that, Tanaris. Before that the pan, and "
               "the Needles, and if you have been at this long enough, the Aspen.\n\nI have walked "
               "all five. In that order. Starting four years ago, because the thaw was coming "
               "early and nobody could tell me why.\n\nSit down. You already know four sixths of "
               "this and nobody has ever put it in front of you in one piece.",
               "At every one of those places somebody told me it was a local problem with a local "
               "cause. Five times. Five different people, all of them careful, none of them "
               "wrong about their own valley.\n\nIt is one problem. You are standing in it.",
               nxt="gv_the_marks", requires_quests=[TANARIS_WATER]))

    q.append(Q("gv_the_marks", "Nine Hundred and Forty-One Dawns", ULLA, GV, 49, 49, "cenote",
               "Read the old waterlines off the rock, where nobody has written anything down.",
               [explore(GV, 56, 94, 7), explore(GV, 112, 96, 7), k("Waterline Serpent", 8)],
               "Oss's book goes back nine hundred and forty-one days. The ROCK goes back further "
               "and it has been keeping the same record for nothing.\n\nFind me the old marks on "
               "the west shore and the east. I want to know what this pool did before anybody was "
               "here to have an opinion about it.",
               "It was lower. Three years ago that pool was eleven feet lower than it is now, and "
               "it has come up steadily since.\n\nThree years. You will have noticed that number "
               "before. Everyone who came across has.",
               nxt="gv_does_not_choose"))

    q.append(Q("gv_does_not_choose", "Water Does Not Choose", ULLA, GV, 49, 50, "cenote",
               "Prove the pool is being fed rather than filling.",
               [k("Waterline Serpent", 7), fetch("gv_tideglass_core", 4)],
               "A pool that is filling is a pool with a level. A pool that is being FED has a "
               "current, and a current leaves a grain in anything that grows in it.\n\nGet me "
               "tideglass off the waterline and cores out of the lattice above it. The crystal "
               "grows toward what feeds it. If I am right, every one of those will point the same "
               "way, and the way will be DOWN.",
               "Every single one. Down and slightly east, all of them, without exception.\n\nThe "
               "water in this pool is not sitting here. It is passing through on its way somewhere "
               "and coming back up, and something at the far end of that is doing the work.",
               nxt="gv_a_well_in_the_middle"))

    q.append(Q("gv_a_well_in_the_middle", "A Well in the Middle of It", ULLA, GV, 50, 50, "cenote",
               "The arithmetic that kills a walled city, written out once.",
               [talk("gv_gadgetzan"), fetch("gv_settled_light", 5), k("Vein-Lit Wisp", 6)],
               "You have stood in Gadgetzan. There is a well in the middle of that city and it is "
               "dry and the city is dead, and every goblin in Steamwheedle will tell you the range "
               "came down three years ago and tipped the table.\n\nThat is true and it is not an "
               "explanation. A table does not tip and then keep tipping for three years.\n\nBring "
               "me residue off the wisps on the seam. They settle where the draw is strongest, and "
               "I want to know whether the draw is still increasing.",
               "Still increasing. Not slowing, not settling - increasing, in the fourth year.\n\n"
               "Whatever took that city's water is still thirsty. That is what I could not say "
               "last week and can say now.",
               nxt="gv_it_is_being_pulled"))

    q.append(Q("gv_it_is_being_pulled", "It Is Being Pulled", ULLA, GV, 50, 50, "cenote",
               "Say the sentence out loud, to the man who has to act on it.",
               [talk("gv_the_argument"),
                deliver("gv_ullas_finding", "Ulla's finding, to Dig-Boss Marn Cobble")],
               "I have a figure, a direction, and a rate. I have had the first two for a year and "
               "the third since this morning, and the third is the one that matters.\n\nThe water "
               "under this region is being drawn down a shaft four hundred feet below us, by "
               "something that started doing it about the time the sky changed.\n\nTake that to "
               "Cobble. He will not like it and he will not argue with it, which are different "
               "things and he is better than he looks at keeping them apart.",
               "He read it twice and asked one question: whether it would stop if somebody made it "
               "stop.\n\nI did not have an answer. I think we are about to get one.",
               nxt="gv_mv_open_the_door",
               grant_items=carry("gv_ullas_finding", "Ulla's Finding",
                       "A figure, a direction and a rate, on one sheet, in a very steady hand.")))

    q.append(Q("gv_last_entry", "The Last Entry", "item:gv_drowned_ledger", CI, 51, 52, "deepvein",
               "Company accounts, four hundred feet down, ending on a date.",
               [deliver("gv_drowned_ledger", "the waterlogged ledger, to Tally-Clerk Oss Pinch")],
               "It is a ledger, and it is a proper one - ruled, dated, double-entered. The last "
               "line is a date and nothing after it.",
               "That is Hallick's hand. He kept the face accounts and he went down with the "
               "shift.\n\nHe balanced it. Look at the bottom of the column - he was four hundred "
               "feet under a desert with the water coming up and he BALANCED IT first.\n\nI am "
               "going to put this in the box with mine.",
               salt="e"))

    # ================= THE SEAMS (5) =================
    q.append(Q("gv_the_cutters_stock", "Four Months of Stock", CUTTER, GV, 47, 48, "seam",
               "The only stone in the world that ignores a spell, and the supply has a date on it.",
               [k("Shardback Crawler", 7), fetch("gv_rough_seam_glass", 6)],
               "There is a single seam in the world that shrugs off a spell and you are standing in "
               "the "
               "hole it came out of - and it was not here three years ago either, before you ask. Nobody cut this stone before the change because nobody had found the hole.\n\nI have about four months of cut stock left. After that I "
               "am a very skilled woman sitting on a rock. Get me rough off the wall - the seams "
               "run up the inside, you cannot miss them, they are the only thing down here that "
               "glows.",
               "Rough, but it is the real thing. You can tell because it goes COLD when you hold "
               "it near anything cast, and nothing else does that.",
               nxt="gv_four_months_left"))

    q.append(Q("gv_four_months_left", "What Grows Over It", CUTTER, GV, 48, 48, "seam",
               "The lattice is eating the exposed face faster than anybody can cut it.",
               [k("Lattice-Grown", 9), fetch("gv_lattice_core", 4)],
               "The problem is not finding the seam. The problem is that something has worked out "
               "the seam is worth having.\n\nThe lattice grows over an exposed face in a season "
               "and once it has, the stone underneath is no good - whatever it does to the "
               "crystal, it does it all the way through. Cut it back and bring me the cores.",
               "These are growing TOWARD the seam. Not over it, toward it.\n\nI have been calling "
               "it a weed for two years. It is not a weed. It is something that wants what I want.",
               salt="f"))

    q.append(Q("gv_what_shrugs_off_a_spell", "Why It Works", CUTTER, GV, 48, 49, "seam",
               "Test the glass against something that actually casts.",
               [k("Vein-Lit Wisp", 8), talk("gv_resistance")],
               "I can tell you vein glass shrugs off a spell. I cannot tell you WHY, and neither "
               "can anybody in Steamwheedle, and I have stopped pretending that is fine.\n\nTake a "
               "backed plate up the galleries and let the wisps hit it. They are the only thing "
               "down here that throws anything worth measuring.",
               "It does not block. That is the thing nobody says properly. It does not block - it "
               "takes the shape of the spell and then it will not hold it, the way water will not "
               "hold a fist.\n\nSo you want it where you are going to be HIT. Breastplate, shield, "
               "greaves. Not a hat.",
               nxt="gv_backed_and_set"))

    q.append(Q("gv_backed_and_set", "Backed, and Set", CUTTER, GV, 49, 50, "seam",
               "She will set the glass into something you already wear.",
               [fetch("gv_spun_glass", 4), deliver("gv_cut_plate", "the cut plate, back to Vessa Quill")],
               "The weavers in the dig spin it into thread. I have never worked out how and I "
               "would very much like a length of it, because thread takes a curve and a plate does "
               "not.\n\nBring me spun glass out of the vein and I will back something of yours "
               "properly. Tank kit, mind. There is no point in this on somebody standing at the "
               "back.",
               "There. Now when something down there decides to be clever at you, it will find "
               "out that you are wearing the one stone in the world that does not care.",
               grant_items=carry("gv_cut_plate", "Vessa's Cut Plate",
                       "Vein glass, cut and backed, waiting for somebody to set it into.")))

    q.append(Q("gv_the_seam_is_the_zone", "Follow One Down", CUTTER, GV, 48, 49, "seam",
               "Pick a seam out from the rim and walk the length of it.",
               [explore(GV, 108, 60, 8), explore(GV, 50, 126, 8)],
               "Here is a thing nobody tells newcomers and everybody works out: you can see the "
               "seams from the top. They are the only lit thing in the hole.\n\nStand on the rim, "
               "pick one, and follow it all the way down. Everybody who works this wall knows "
               "their own seam by sight and that is how you start."
               "",
               "Now you can find your way down there in the dark, which you will need to, because "
               "the lamps on that road have been out since the works stopped.",
               salt="g"))

    # ================= THE MOTHER VEIN (5) =================
    q.append(Q("gv_mv_open_the_door", "Nine Days", PUMP, GV, 50, 50, "deepvein",
               "The first gallery is clear. Somebody has to walk into it.",
               [explore(MV, 60, 100, 8), k("Sodden Digger", 8, zone=MV)],
               "Nine days, like I said. The first gallery is dry and the dig head is standing "
               "open for the first time in a year.\n\nAnd there are people in it. That is the part "
               "I have not told the Boss yet. They are still on shift, in the sense that nobody "
               "ever called the shift, and they do not want anybody down there with them.",
               "Forty of them. We signed off forty missing and there are forty down there.\n\nHalf of them came through with everybody else and took the first wage anybody offered. They were not from here. Nobody is going to come looking.\n\nI am going to have to be the one who tells him that, aren't I.",
               nxt="gv_mv_still_on_shift"))

    q.append(Q("gv_mv_still_on_shift", "Still On Shift", CLERK, GV, 50, 51, "deepvein",
               "Every one of them had a number, and the numbers are still on the board.",
               [fetch("gv_shift_token", 6), k("Vein Crawler", 8, zone=MV)],
               "Each of them carried a brass token with a number on it. You hang it on the board "
               "going in and you take it off coming out, and that is how a dig knows who is "
               "below.\n\nThere are forty tokens still hanging on that board. Bring me what you "
               "can off them and I will take the numbers down properly, which is a thing somebody "
               "should have done eleven months ago.",
               "Six. I will do the rest myself over time.\n\nHesper Dunn keeps a book like mine out "
               "in the port and she told me once she keeps hers so that in four years nobody can "
               "claim the town was always like this. Mine is so that in four years somebody can "
               "still say their names.",
               nxt="gv_mv_the_foreman", salt="h"))

    q.append(Q("gv_mv_the_foreman", "The Wage Bill", MARN, MV, 51, 51, "deepvein",
               "The pitboss who would not call the evacuation is at the head of the gallery.",
               [boss("Pitboss Grebble Vask", MV)],
               "Grebble Vask was my pitboss and he was the best I ever had, and he did not call "
               "the evacuation because calling it cost eleven thousand and not calling it cost "
               "nothing until it cost everything.\n\nHe is still down there. He is still shouting "
               "figures. I have heard him from the mouth and I would like that to stop.",
               "Thank you.\n\nI signed that order. He read it out to me and I signed it and the "
               "thing that has been eating me for a year is that I would sign it again, because "
               "from where I stood on the Tuesday it was the right number.",
               nxt="gv_mv_what_the_pumps"))

    q.append(Q("gv_mv_what_the_pumps", "What the Pumps Could Not Hold", PUMP, MV, 51, 51,
               "deepvein",
               "The pump chamber, and the thing the water left in it.",
               [boss("The Sump", MV)],
               "Four of those six housings are down there in the sump chamber and they are MINE, "
               "and I have wanted them back for a year.\n\nThere is something in that chamber "
               "now. Sanna has seen it from the gallery mouth and she will not go past the arch, "
               "and Sanna has gone into that water nine times.",
               "You got them out. Look at the face on that casing - the water did not do that, "
               "something SAT on it.\n\nI can run four more pumps off these. Not that it matters "
               "any more. We are not here for the crystal now, are we."))

    q.append(Q("gv_mv_glassmaw", "The Glass Rooms", DIVER, MV, 51, 52, "deepvein",
               "The vugs are rooms made of knives, and something lives in them.",
               [boss("Glassmaw", MV), fetch("gv_spun_glass", 4)],
               "Forty feet in on a lungful, tie off, forty feet back. That was the job before the "
               "gallery dried.\n\nNow I can walk it, and I have walked it, and past the pump "
               "chamber the seam opens into rooms that are made entirely of crystal faces. "
               "Beautiful. Also every surface in there will open you up, and one of them MOVES.",
               "Nine times I went in on a lungful and I never once got as far as that room.\n\n"
               "There is a hole in the floor at the back of it. It goes down. I looked at it for a "
               "long time and then I came back up here and had a drink.",
               nxt="gv_ci_further_down", salt="i"))

    # ================= THE CISTERN (5) =================
    q.append(Q("gv_ci_further_down", "The Hole in the Floor", ULLA, MV, 51, 52, "cistern",
               "Down the shaft at the back of the glass rooms, into whatever is below it.",
               [explore(CI, 46, 118, 8), k("Seam Singer", 8, zone=CI)],
               "Sanna has described the shaft to me three times and each time she has described "
               "it as going DOWN, which is a thing shafts do and not worth saying three "
               "times.\n\nShe means it is going down past where the water is. Nothing drains "
               "below the water table. Something is holding that shaft dry, and I would like to "
               "know what and I am not able to go myself.",
               "Singing. You said singing and I wrote down singing and I want to be clear that I "
               "do not know what that means.\n\nWhatever is down there arrived when everything arrived. Three years, and it has been doing this the whole time under a desert nobody walks.\n\nGo carefully. I have spent four years wanting to "
               "be right about this and I find I would rather you came back."))

    q.append(Q("gv_ci_the_choir", "The Whole Seam Answers", CUTTER, CI, 52, 52, "cistern",
               "The lattice down here grows in exact repeating geometry, and it resonates.",
               [boss("Resonance", CI), fetch("gv_struck_shard", 4)],
               "Sanna brought up a shard and it has been ringing on my bench for a day. A day. I "
               "have put it in sand, I have put it in water, I have put it in a lead box.\n\nThere "
               "is something down there that strikes the seam and the whole seam answers. That is "
               "not crystal doing what crystal does. Somebody is PLAYING it.",
               "It stopped. The one on my bench stopped the moment you came up the spiral, and I "
               "did not need telling what that meant.\n\nI have been cutting this stone for eleven "
               "years. I did not know it could be asked to do anything.",
               nxt="gv_ci_the_siphon"))

    q.append(Q("gv_ci_the_siphon", "The Proof", ULLA, CI, 52, 52, "cistern",
               "The thing that lifts the water, which is the whole argument made of metal and ice.",
               [boss("The Siphon", CI)],
               "You have found the works. Sanna's description is the first thing anybody has told "
               "me in four years that I could not have predicted.\n\nWater does not rise. I have "
               "built an argument on that sentence across five zones and a thousand miles and I "
               "have never once been able to show anybody the thing that breaks it.\n\nGo and "
               "break it.",
               "So it is real.\n\nFour years. Five places. Every one of them a local problem with a "
               "local cause and every single one of those people was looking at the same "
               "machine.\n\nI would like a moment, if you do not mind. I will have the rest of it "
               "written up by the time you have climbed back down."))

    q.append(Q("gv_ci_standing_water", "Water Does Not Do This", DIVER, CI, 52, 52, "cistern",
               "Past the works, the water is standing up.",
               [boss("The Standing Wave", CI), k("Cistern Lurker", 8, zone=CI)],
               "I have been in water my whole life. Harbour water, cave water, the pool out there "
               "that nobody else will swim in.\n\nI went to the lip of that chamber and the water "
               "in it is standing UP. Not a wave. Not moving at all. Standing, held, like "
               "something is holding it, and the lattice goes all the way through it.\n\nI came "
               "back. You will notice I came back.",
               "Nine times into that gallery on a lungful and I thought I had seen the worst thing "
               "down here on about the fourth.\n\nI was nowhere near it."))

    q.append(Q("gv_ci_the_thirst", "Three Years of Drinking", ULLA, CI, 52, 52, "cistern",
               "The top of the shaft, and the end of five zones.",
               [boss("The Thirst", CI), talk("gv_the_end")],
               "Everything in that place is downstream of one room and I can tell you exactly "
               "where it is, because I have been drawing this map for four years without knowing "
               "what I was drawing.\n\nWhatever is in there arrived when everything else arrived. "
               "It has been drinking a region since, and it has not slowed down once, and the "
               "fourth year is faster than the third.\n\nI am not going to tell you to be careful. "
               "You have walked the same five places I have. You know what it has cost already.",
               "It let go.\n\nYou came out of the outflow, did you? Everybody does - there is only "
               "the one channel and it is the channel the water takes. You followed it home.\n\n"
               "Oss took the level at dawn. It is down four inches. Four inches is nothing. Four "
               "inches is the first time that number has gone the right way in nine hundred and "
               "forty-two days.",
               nxt="gv_tell_them_why"))

    # ================= OUT OF THE ZONE (2) =================
    q.append(Q("gv_tell_them_why", "Somebody Should Tell Them", ULLA, GV, 52, 52, "cistern",
               "Four days east, to the goblins who were told their city died of bad luck.",
               [deliver("gv_ullas_account", "Ulla's account, to Old Mazzic in Steamwheedle"),
                talk("gv_the_road_east")],
               "There is a man in Steamwheedle who did not leave Gadgetzan. He was carried out of "
               "it on a door by two people whose names he never got, and he has spent three years "
               "listening to people say his town had bad luck.\n\nIt did not have bad luck. It had "
               "a cause, the cause had a location, and the location is four hundred feet under my "
               "feet.\n\nTake him the account. He is owed the sentence and I am not able to make "
               "the walk any more.",
               "[Mazzic reads it twice, slowly, and then puts it down flat on the counter and "
               "smooths it with his hand.]\n\nI knew it was not us. Three years of goblins telling "
               "me the desert turned and I knew it was not US.\n\nThat is not better. I want to be "
               "honest with you - it is not better at all. But it is TRUE, and I have not had one "
               "of those about my own town since the day I came out of it on a door.",
               nxt="gv_the_book_goes_east",
               grant_items=carry("gv_ullas_account", "Ulla Stormhollow's Account",
                       "Four years, five places, one cause, in the handwriting of somebody who "
                       "walked all of it.")))

    q.append(Q("gv_the_book_goes_east", "The Column Nobody Wanted", CLERK, GV, 52, 52, "lastwater",
               "The whole column out of Oss's book, written out again for the port's own clerk.",
               [deliver("gv_copied_column", "the copied column, to Tally-Clerk Hesper Dunn"),
                talk("gv_two_clerks")],
               "Hesper Dunn out in the port keeps a book like mine. She keeps hers so that in four "
               "years nobody can claim the town was always like this.\n\nMine is nine hundred and "
               "forty-two dawns of a number that nobody wanted and that turned out to be the only "
               "record anybody had of the thing happening. Copy it and take it to her. A pair of books "
               "four days apart are harder to lose than one.",
               "She will keep it. She will keep it in the same box and she will date the box, "
               "because that is what we are like.\n\nSomebody in forty years is going to open that "
               "and find out exactly when a region stopped drying out. Not from a speech. From two "
               "clerks nobody listened to.",
               grant_items=carry("gv_copied_column", "The Copied Column",
                       "Nine hundred and forty-two dawns in a very small hand, copied twice over "
                       "by lamplight.")))

    return q


def audit(quests):
    bad = []
    ids = {q["quest_id"] for q in quests}

    # NO ESCORTS, EVER. Kyle, standing.
    for q in quests:
        blob = " ".join(str(q.get(k) or "") for k in ("title", "description", "accept_text",
                                                      "turn_in_text"))
        if "escort" in blob.lower() or any(o["type"] == "escort" for o in q["objectives"]):
            bad.append(f"{q['quest_id']}: escort")

    # NO QUEST TARGETS A NAMED RARE. The five surface rares are lore and loot and nothing else;
    # the seven dungeon bosses are PINNED, so kill_boss on them is legitimate.
    rares = {"Thirstjaw", "Old Riser", "Shatterlight", "Rootbound", "Stillwater"}
    pinned = {"Pitboss Grebble Vask", "The Sump", "Glassmaw",
              "Resonance", "The Siphon", "The Standing Wave", "The Thirst"}
    for q in quests:
        for o in q["objectives"]:
            t = o.get("target")
            if t in rares:
                bad.append(f"{q['quest_id']}: targets the rare {t}")
            if o["type"] == "kill_boss" and t not in pinned:
                bad.append(f"{q['quest_id']}: kill_boss on {t}, which is not a pinned boss")

    # EVERY DELIVER MUST HAVE THE ITEM IN HAND. Two Shimmering Flats quests shipped uncompletable
    # because the audit assumed the giver handed the item over and the quest granted nothing. It
    # reads grant_items now, and a deliver target must be granted on accept OR be a fetch drop.
    droppable = {iid for rows in list(FETCH_DROPS.values()) + list(STARTER_DROPS.values())
                 for (iid, _n, _d, _c) in rows}
    for q in quests:
        # READ WHERE THE ENGINE READS: grant_items.on_accept. Checking a different key is how
        # two Flats quests shipped uncompletable with the audit reporting them fine.
        granted = {g["item_id"]
                   for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            if o["type"] == "deliver" and o["target"] not in granted | droppable:
                bad.append(f"{q['quest_id']}: delivers {o['target']}, which nothing grants or drops")

    # A GATHER OBJECTIVE MUST NOT TARGET A WORLD-NODE MATERIAL. Every other zone's gather
    # objectives point at bespoke quest items that DROP; pointing one at herb_/ore_/crystal_/wood_
    # means the only way to finish it is to have that gathering profession, at the right skill,
    # with the right node up - so a warrior with no herbalism can never complete it and nothing
    # about the quest says so. Five of these shipped into the first draft of this file.
    for q in quests:
        for o in q["objectives"]:
            if o["type"] in ("gather", "fetch") and str(o.get("target", "")).startswith(
                    ("herb_", "ore_", "crystal_", "wood_", "essence_")):
                bad.append(f"{q['quest_id']}: {o['type']}es the node material {o['target']}, "
                           f"which gates the quest behind a gathering profession")

    # chains must land somewhere real
    for q in quests:
        nx = q.get("next_quest_id")
        if nx and nx not in ids:
            bad.append(f"{q['quest_id']}: chains to {nx}, which this pass does not define")

    # COUNTS IN PROSE BIND TO THE WRONG OBJECTIVE when an item id shares a word with a creature
    # name - eight on the Flats and seven on Tanaris, both after the guide warned about it. Check
    # it here rather than rediscovering it in the audit.
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

    # the far gate has to be live, or Ulla's whole thread is unreachable
    tan = json.loads((ROOT / "data/quests/tanaris.json").read_text(encoding="utf-8"))
    if TANARIS_WATER not in {q["quest_id"] for q in tan["quests"]}:
        print(f"FAILED: the water gate requires {TANARIS_WATER}, not in tanaris.json")
        return 1
    print(f"water gate: {TANARIS_WATER}, live in Northern Tanaris")

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
    inzone = sum(1 for q in quests if q["zone"] == GV)
    print(f"{len(quests)} quests -> {OUT.name}: {inzone} in the zone, "
          f"{len(quests) - inzone} in the dungeon maps")
    print(f"  {chains} chained, {gated} gated on another zone, {starters} item-started")
    return 0


if __name__ == "__main__":
    sys.exit(main())
