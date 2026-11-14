#!/usr/bin/env python3
"""
The Black Strand and Onyxhollow quest pass. Idempotent. 50-53.

    PYTHONPATH=. python3 tools/build_black_strand_quests.py

Kyle, 13 Nov 2026: "we need some good high quality quests around here", "Aim for 30 quests per zone
if you can", and "Don't forget trash can start quests."

THIRTY-THREE QUESTS. Twenty-five are given in Onyxhollow, so the town is somewhere you keep coming
back to; four come from the three people outside the gate; two start from something a monster
drops; two are the chain out of the zone.

WHAT THE ZONE IS ABOUT. A mining town with a gate shut on a beach it never wanted. The quests are
the town's ordinary business - keep the road clear, keep the braziers lit, feed the furnace - and
three things under that:

  THE CASTOUTS (6)     A gallery came down and the Thane put out the whole shift, because nobody
                       would say who gave the order. One of them sits at the gate's brazier. The
                       vault-keeper never struck their names. This is the chain that ends with a
                       decision, and it is the one a player should remember.
  THE HIVE (7)         It is digging toward the wall and eating the wood. Ends in the Royal Cell.
  WHOSE SHORE (5)      It was a sea. The loremaster in town and a geologist from Earth at the foot
                       of the stair are asking the same question and have never met.
  THE WOOD AND THE WATER (6), THE TOWN'S WORK (5), TWO DROPS (2), OUT OF THE ZONE (2).

THE WAY OUT IS UP. The geomancer has been listening to the roof for the Thane. Peska Vane at Fourth
Peg has been surveying the same roof from above (the Dry Deep quests end with her asking how long
it will last). The last two quests carry one's answer to the other.

VOICE. Kyle, same day: "Don't use weird AI tics." People talking to someone they want a job done
by: contractions, the place and the creature named plainly, a reason, and no little sayings to
close on. No counts in the prose - the objective line carries the number.

RULES KEPT: no escorts; quest items drop three times in four; nobody stands at the place their
quest sends you; the two kill_boss quests are on rares, which the engine makes likelier to appear
while the quest is held (CreatureManager.QUEST_RARE_SPAWN_CHANCE).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/black_strand.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

BS = "the_black_strand"
AB = "the_abyssal_sands"

XP = {50: 3640, 51: 3720, 52: 3800, 53: 3880}
GOLD = {50: 14400, 51: 14700, 52: 15000, 53: 15300}

tirisfal_gear.THEMES.update({
    "onyxhollow": (["Onyxhollow", "Forge-Row", "Anvil-Road", "Banked-Fire", "Gatewarden's"],
                   ["Dark Iron work. Heavier than it looks and built to be repaired.",
                    "Stamped with the Onyxhollow vault's weight mark.",
                    "Issued at the gate, and they'll want to know where it went.",
                    "Made on Forge Row by someone who signed it underneath."]),
    "strand": (["Blacksand", "Ashdune", "Strandwalker's", "Tide-Mark", "Bottom-Step"],
               ["There's black sand in every seam and there always will be.",
                "Worn smooth by something. The dwarves say sand; the geologist says water.",
                "It was pale once. Nothing stays pale down here.",
                "Carried down a very long stair by somebody who meant to stay."]),
    "lantern": (["Lantern-Wood", "Gloomcap", "Sporelit", "Lastwater", "Capcutter's"],
                ["It glows a little in the dark. That wears off in a week or so.",
                 "Smells of the Lantern Wood, which is to say of wet cellar.",
                 "Sigrun says the stain is harmless. She says that about a lot of things.",
                 "Cut and stitched by lamplight that wasn't a lamp."]),
    "hive": (["Chitin-Reach", "Resin-Set", "Reaver's", "Hivebreaker's", "Royal-Cell"],
             ["Hive carapace, trimmed and riveted. Lighter than plate and nearly as hard.",
              "The amber in it was soft when it was fitted and isn't now.",
              "Taken off something that was digging toward the wall.",
              "It still hums faintly near the Reach."]),
    "castout": (["Castout's", "Old-Diggings", "Tally-Marked", "Second-Shift", "Struck-Name"],
                ["The maker's mark has been filed off. You can still feel where it was.",
                 "Company issue from before the gallery came down.",
                 "Mended many times by someone with no forge to mend it at.",
                 "There's a shift tally scratched inside, in a careful hand."]),
})


def k(target, n, zone=BS):
    return kill(target, n, zone=zone)


def boss(target, zone=BS):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, radius=7, zone=BS):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    return dict(type="dialogue", topics=list(topics))


def craft(recipe, n, label):
    return dict(type="craft", target=recipe, count=n, label=label)


def carry(item_id, name, desc, count=1):
    """What the giver hands you. Pass as grant_items=carry(...)."""
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=count)]}


def Q(qid, title, giver, lo, hi, theme, desc, objs, accept, done, nxt=None, zone=BS, **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = hi + 2 if is_boss else hi + 1
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=int(XP[hi] * mult), reward_gold=int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             unique_item_defs=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ---- givers. Onyxhollow's are in tools/onyxhollow_npc_roster.py, and so are the three outside.
THANE = "oh_thane"
YRSA = "oh_gate_captain"
DUNMAR = "oh_gate_guard_w"
ODA = "oh_gate_guard_e"
RURIK = "oh_wall_sentry"
ALDIS = "oh_vault_keeper"
TORVALD = "oh_shrine_keeper"
HALD = "oh_stoker"
INGRID = "oh_loremaster"
VIGDIS = "oh_geomancer"
GARRUN = "oh_forgemaster"
BRENNA = "oh_innkeeper"
HULDA = "oh_smith"
THRAIN = "oh_armorer"
KELDA = "oh_mining_supplier"
SIGRUN = "oh_reagents"
BROKK = "oh_powder"
HERVI = "bs_lookout"
NOOR = "bs_geologist"
BRANNOC = "bs_castout"
PESKA = "ab_surveyor"          # Chief Surveyor Peska Vane, at Fourth Peg in the Abyssal Sands

#: Quest items. Three in four, Kyle's rate for a quest that wants several.
RATE = 0.75
FETCH_DROPS = {
    "Ashdune Basilisk": [
        ("bst_basilisk_fat", "Basilisk Fat", "Burns slow and hot. The gate braziers run on it."),
        ("bst_stone_pick", "Petrified Pick",
         "A miner's pick turned to grey stone, haft and all. There's a name cut in the haft."),
    ],
    "Lantern Sporeling": [
        ("bst_young_cap", "Unopened Lantern Cap", "Picked before it opened. Still faintly blue."),
    ],
    "Gloomcap Trampler": [
        ("bst_trampler_gill", "Trampler Gill", "Thick as a hand and damp. It smells of cellar."),
    ],
    "Blindwater Lurker": [
        ("bst_worked_shell", "Worked Shell",
         "A shell with a hole drilled through it and a pattern scratched round the hole."),
        ("bst_water_bladder", "Lurker's Water Bladder",
         "Full of water from the Last Water. Very cold and slightly bitter."),
    ],
    "Castout Digger": [
        ("bst_tally_stick", "Shift Tally Stick",
         "Notched for every cart a miner filled, with the gallery's mark burned in the end."),
    ],
    "Castout Slagcaller": [
        ("bst_shrine_ember", "Shrine Ember", "Still burning in its clay pot. It doesn't go out."),
    ],
    "Hive Resinspitter": [
        ("bst_amber_resin", "Clear Amber Resin", "Soft while it's warm. Sets harder than glass."),
    ],
    "Hive Reaver": [
        ("bst_reaver_plate", "Reaver Carapace", "A back-plate the size of a shield, and lighter."),
    ],
}
STARTER_DROPS = {
    "Hive Swarmer": [("bst_half_eaten_cap", "Half-Eaten Lantern Cap",
                      "A mushroom cap with neat scythe-cuts through it. Something was carrying "
                      "it, not eating it.", 0.22)],
    "Castout Cutthroat": [("bst_unsent_letter", "Unsent Letter",
                           "Folded small and worn at the creases. It's addressed to Brenna "
                           "Coalcask at the Banked Fire.", 0.22)],
}
STARTER_IDS = {"bst_half_eaten_cap": "bst_what_they_carry",
               "bst_unsent_letter": "bst_unsent_letter"}


def build():
    q = []

    # ================= ARRIVING, AND THE TOWN'S WORK =================
    q.append(Q("bst_long_way_down", "The Long Way Down", HERVI, 50, 50, "strand",
               "Follow the slag road to the gate of Onyxhollow and report to the Gate-Captain.",
               [explore(84, 58, "the gate of Onyxhollow"),
                deliver("bst_lookout_token", "Hervi's tally token, to Gate-Captain Yrsa")],
               "You'll want the town. There's an inn, and you look like you could use one.\n\n"
               "Take this token to Gate-Captain Yrsa. It tells her I've seen you and you came "
               "down the stair, not up out of the sand. She likes to know.\n\nThe slag road "
               "starts right here and runs south-east. Stay on it and follow the braziers. The "
               "gate's at the end, between the two watchtowers.",
               "One of Hervi's tokens. All right, you came down the stair.\n\nYou're welcome in "
               "Onyxhollow as long as you're here to trade or to work. The inn's up the road on "
               "the left. If it's work you want, most of the town has something that needs "
               "doing outside this gate, and I'm short of people to send.",
               turn_in_npc_id=YRSA,
               grant_items=carry("bst_lookout_token", "Hervi's Tally Token",
                                 "An iron token with a notch filed in it. The lookout at the "
                                 "Bottom Step hands one to everybody who comes down.")))

    q.append(Q("bst_clear_the_slag_road", "Sand on the Road", DUNMAR, 50, 50, "onyxhollow",
               "Kill Blacksand Scorpions and Strand Bats along the slag road across the Ash Dunes.",
               [k("Blacksand Scorpion", 10), k("Strand Bat", 8)],
               "You walked in on the slag road, so you'll have seen what's on it.\n\nThe "
               "scorpions bury themselves in the black sand beside the paving and the bats come "
               "down off the roof at anything carrying a lamp. We lose a carter to them every "
               "couple of months.\n\nThey're thickest out on the Ash Dunes, north-west of the "
               "gate, the way you came. Kill what you find near the road. I'd do it myself but "
               "I'm not allowed off this gate.",
               "That'll keep the carts moving for a while. Thanks.\n\nTake something from the "
               "gate stores. The Captain signs for it, so don't feel bad."))

    q.append(Q("bst_keep_them_lit", "Keep Them Lit", ODA, 50, 50, "onyxhollow",
               "Collect Basilisk Fat from Ashdune Basilisks on the Ash Dunes for the gate braziers.",
               [fetch("bst_basilisk_fat", 8)],
               "See the braziers? The hive won't come past them. I don't know why and I don't "
               "much care, as long as they stay lit.\n\nThey burn basilisk fat. Coal smokes too "
               "much in a cave and lamp oil comes down a rope, so it's fat or nothing. We're "
               "nearly out.\n\nThe Ashdune Basilisks are out on the Ash Dunes, north-west of "
               "the gate. Don't look them in the eye for long. Bring me the fat and I'll render "
               "it tonight.",
               "That's plenty. That's a month of nights.\n\nYou didn't stare at one, did you? "
               "No, you'd be greyer. Here, this is for the trouble."))

    q.append(Q("bst_sign_the_board", "Three Names, One Mark", KELDA, 50, 50, "strand",
               "Find the miners who went to dig on the Ash Dunes and bring back their picks.",
               [explore(56, 44, "the sand diggings on the Ash Dunes"), fetch("bst_stone_pick", 3)],
               "Three of mine signed out to dig dark iron in the sand, out on the Ash Dunes. "
               "That was five shifts ago and none of them has signed back in.\n\nI've a fair "
               "idea what happened. The basilisks out there turn a body to stone if it stands "
               "still long enough, and miners stand still a lot.\n\nThe sand diggings are "
               "north-west of the gate, off the south side of the slag road. Go and look. If "
               "I'm right, the Ashdune Basilisks will have what's left. Bring me the picks. "
               "Each one has a name on the haft and I need to know which names.",
               "Stone, all three. Haft and head.\n\nThat's Orm's, and that's Sifa's. I don't "
               "recognise the third hand. It'll be in the book.\n\nI'll tell their people. "
               "Thank you for bringing them back. Most wouldn't have carried the weight."))

    q.append(Q("bst_bats_in_the_flue", "Bats in the Flue", HALD, 50, 50, "onyxhollow",
               "Kill Strand Bats on the Ash Dunes, where the furnace flue comes out.",
               [k("Strand Bat", 12)],
               "The furnace has been drawing badly all week. I went up the flue with a lamp and "
               "it's full of bats.\n\nThe flue comes out through the rock onto the Ash Dunes, "
               "north-west of the gate. It's warm, so they roost in it. Every time I clear them "
               "out, more come in from the dunes.\n\nThin out the Strand Bats out there and "
               "I'll have a chance of keeping it clear. Garrun's blaming my shovelling and I'd "
               "like him to stop.",
               "It's drawing properly again. Listen to that.\n\nI told Garrun it was bats. He "
               "said he'd believe it when the furnace did. Well, the furnace does."))

    q.append(Q("bst_forgemasters_test", "The Forgemaster's Test", GARRUN, 51, 51, "onyxhollow",
               "Smelt Dark Iron Bars to show Forgemaster Garrun you can work the ore.",
               [craft("bar_dark_iron", 4, "Dark Iron Bar")],
               "Anybody can swing a pick. I want to see what you do with what comes out.\n\n"
               "There's dark iron ore in the sand all over the Strand, and in our own rock if "
               "Kelda lets you down the head. Mine some and smelt it into bars. You'll need "
               "the skill for it. If you haven't got it yet, come back when you have.\n\nDark "
               "iron's fussy. Too cold and it won't flow, too hot and it goes brittle. Bring me "
               "the bars and I'll tell you which you did.",
               "Let me see. That one's a touch hot. The rest are good.\n\nBetter than most of "
               "my apprentices manage in their first year. Don't tell them I said so. Take "
               "this, you've earned it."))

    q.append(Q("bst_a_keg_for_the_stair", "A Keg for the Stair", BRENNA, 51, 51, "onyxhollow",
               "Carry a keg of Banked Fire ale to Lookout Hervi at the Bottom Step.",
               [deliver("bst_ale_keg", "the keg of Banked Fire ale, to Lookout Hervi")],
               "Hervi's been on the stair post for three weeks without relief. Nobody's sent "
               "him anything but bread.\n\nTake him this keg, would you? He's at the Bottom "
               "Step, at the far north-west end of the slag road, where you came down. It's "
               "heavy but it's a straight road.\n\nTell him it's from Brenna and he still owes "
               "me for the last one.",
               "From Brenna? Oh, that's good of her.\n\nShe says I owe her for the last one. "
               "I do. Tell her I'll settle when I'm relieved, which at this rate is never.\n\n"
               "Here, take this for the carrying. It's a long road with a keg.",
               turn_in_npc_id=HERVI,
               grant_items=carry("bst_ale_keg", "Keg of Banked Fire Ale",
                                 "A small iron-hooped keg. It sloshes. It's brewed from "
                                 "mushrooms and tastes better than that sounds.")))

    # ================= WHOSE SHORE =================
    q.append(Q("bst_tide_marks", "Tide Marks", NOOR, 50, 50, "strand",
               "Look at the cavern wall on the west and east sides of the Ash Dunes.",
               [explore(34, 26, "the west wall of the Ash Dunes"),
                explore(68, 28, "the east wall of the Ash Dunes")],
               "Can I ask you something? You'll be walking across the dunes anyway.\n\nThere "
               "are lines on the cavern walls out there, high up. Pale bands, dead level, one "
               "above another. I think they're tide marks. If they are, they should be at the "
               "same height on both sides of the cavern.\n\nI can't get to the far wall. "
               "There's too much out there that wants to eat me. The Ash Dunes are just "
               "south-east of here. Have a look at the west wall and then the east one, and "
               "tell me whether the lines match.",
               "They match? Same height, both sides?\n\nThen it was water, standing water, and "
               "a lot of it. This whole cavern was a sea.\n\nI used to take students to the "
               "Dead Sea to look at lines exactly like these. That was before the change, and I "
               "didn't think I'd ever see them again. Thank you. Really."))

    q.append(Q("bst_black_sand", "Why It's Black", NOOR, 51, 51, "strand",
               "Kill Blacksand Scorpions on the Ash Dunes and visit the miners' sand diggings.",
               [k("Blacksand Scorpion", 10), explore(56, 44, "the sand diggings on the Ash Dunes")],
               "The sand's bothering me. Beach sand is pale. This is black and it's heavy, and "
               "the dwarves dig iron out of it.\n\nI'd like to see a fresh cut, somewhere it's "
               "been dug deep. The miners have a diggings on the Ash Dunes, south-east of here "
               "on the south side of the slag road. Go and look at how the sand lies in the "
               "sides of the pit.\n\nThe Blacksand Scorpions nest in the loose spoil round it. "
               "You'll have to clear them before you can see anything.",
               "Layers? Black, then a thin pale one, then black again?\n\nThen the iron washed "
               "in. Something up above was wearing away and the sea was carrying it down here, "
               "season after season.\n\nThe dwarves think the iron was always in the sand. It "
               "wasn't. It came from somewhere, and I'd love to know where."))

    q.append(Q("bst_whose_shore", "Made, Not Grown", INGRID, 51, 51, "lantern",
               "Collect Worked Shells from Blindwater Lurkers at the Last Water.",
               [fetch("bst_worked_shell", 6)],
               "A carter brought me a shell last month. It had a hole drilled in it, clean "
               "through, and a pattern scratched round the hole. Shells don't grow like that. "
               "Somebody made it.\n\nHe got it out of a Blindwater Lurker. They swallow "
               "anything on the bottom and it sits in the gut for years.\n\nThe Lurkers are at "
               "the Last Water. Go out of the gate and south, past the big rock, until you "
               "reach the lake. If you find any more shells like it, I want them.",
               "They're all drilled, and the patterns are all different.\n\nLook, this one's a string of "
               "little marks, and this one's a spiral. I think they were worn. On a cord, "
               "round the neck.\n\nSomebody lived on this shore and made jewellery. The Thane "
               "says it's only rock down here. I'm going to enjoy showing him these.",
               nxt="bst_standing_stones"))

    q.append(Q("bst_standing_stones", "The Three Stones", INGRID, 52, 52, "lantern",
               "Find the three stones the carters mention: two in the Lantern Wood, one at the "
               "Last Water.",
               [explore(22, 90, "the stone at the west end of the Lantern Wood"),
                explore(46, 72, "the stone at the north edge of the Lantern Wood"),
                explore(62, 104, "the stone on the west shore of the Last Water")],
               "If they wore shells, they'll have left more than shells.\n\nThe carters talk "
               "about three stones. They call them the Old Men. Two are in the Lantern Wood "
               "and one's by the Last Water. I'd always assumed they were stalagmites. Now I'm "
               "not so sure.\n\nThe Lantern Wood is south-west of the gate. One stone is at "
               "its far west end and one at its north edge. The third is on the west shore of "
               "the Last Water, south of the gate. Go and look at each of them closely. I want "
               "to know if they've been shaped.",
               "Flat on one side, all three, and the flat side faces the water?\n\nThen they "
               "were set there. They're markers. Maybe for a landing, maybe for graves. Either "
               "way somebody stood them up.\n\nI've made rubbings from your description as "
               "best I can. There's one more thing I'd like you to do with them.",
               nxt="bst_two_notebooks"))

    q.append(Q("bst_two_notebooks", "Two Notebooks", INGRID, 52, 52, "strand",
               "Take Ingrid's notes to the topside woman camped at the Bottom Step.",
               [deliver("bst_ingrids_notes", "Ingrid's notes, to Noor Haddad at the Bottom Step")],
               "Hervi tells me there's a topside woman camped at the Bottom Step who measures "
               "the walls. He thinks she's cracked. I think she might be asking the same thing "
               "I am.\n\nI can't leave the town. The Thane's made that clear. So would you "
               "take her my notes? The shells, the stones, all of it.\n\nThe Bottom Step is at "
               "the far north-west end of the slag road. I don't know her name. She'll be the "
               "only person there who isn't a dwarf.",
               "From the loremaster? I didn't know they had one.\n\nShells with holes drilled "
               "in them. Marker stones facing the water. And I've got tide marks and layered "
               "sand.\n\nShe's got the people and I've got the sea. Put the two together and "
               "you've got a whole coast, with somebody living on it.\n\nI need to talk to "
               "her. They won't let me through the gate, but they can't stop me writing. Thank "
               "you for carrying this. You've no idea how long I've been working on my own.",
               turn_in_npc_id=NOOR,
               grant_items=carry("bst_ingrids_notes", "Ingrid's Notes",
                                 "A sheaf of careful drawings: shells with holes in them, and "
                                 "three stones, each with one flat face.")))

    # ================= THE WOOD AND THE WATER =================
    q.append(Q("bst_young_caps", "Young Caps", SIGRUN, 51, 51, "lantern",
               "Collect Unopened Lantern Caps from Lantern Sporelings in the Lantern Wood.",
               [fetch("bst_young_cap", 10)],
               "I'm down to my last jar of caps and I've orders to fill.\n\nI need young ones, "
               "picked before they open. Once they open the good part's gone into the air. The "
               "trouble is the young caps walk about. We call them Lantern Sporelings, and "
               "they don't like being picked.\n\nThe Lantern Wood is south-west of the gate. "
               "You'll see the glow well before you get there. Kill the Sporelings and cut the "
               "caps off before they open.",
               "These are lovely. Look how tight they are.\n\nThat's a month of healing "
               "draughts for the whole town. I'll put a few bottles aside for you. And take "
               "this as well. It's been in my store cupboard for years and it ought to be "
               "used."))

    q.append(Q("bst_trampler_gills", "Something for the Lungs", SIGRUN, 51, 51, "lantern",
               "Kill Gloomcap Tramplers in the Lantern Wood and collect their gills.",
               [k("Gloomcap Trampler", 8), fetch("bst_trampler_gill", 6)],
               "Half the furnace crew has a cough that won't shift. It's the smoke. I can make "
               "something for it, but I need gills from the big mushrooms.\n\nGloomcap "
               "Tramplers, we call them. They're slow, but they're the size of a cart and "
               "they'll walk straight over you. They're in the Lantern Wood, south-west of the "
               "gate, further in than the Sporelings.\n\nCut the gills from under the cap. "
               "Wear something over your mouth while you do it.",
               "Good thick ones. These'll do nicely.\n\nI'll have a syrup ready by tomorrow. "
               "Hald's going to complain about the taste and then ask for more. Thank you for "
               "going in there. I know it isn't pleasant."))

    q.append(Q("bst_the_last_water", "The Last Water", VIGDIS, 51, 51, "lantern",
               "Visit the north and south shores of the Last Water and kill Blindwater Lurkers.",
               [explore(79, 92, "the north shore of the Last Water"),
                explore(70, 108, "the south shore of the Last Water"),
                k("Blindwater Lurker", 8)],
               "There's a lake south of here. It's the only standing water left in this whole "
               "cavern, so we call it the Last Water.\n\nI need to know if it's rising or "
               "falling. If it's falling, the rock above us is drying out and it'll crack. If "
               "it's rising, something's leaking in from above, and that's worse.\n\nGo out of "
               "the gate and south. Look at the shoreline on the north side and then on the "
               "south. Wet rock above the waterline means it's dropped. The Blindwater Lurkers "
               "will come at you the moment you're near the edge, so deal with them first.",
               "Wet rock a hand's width above the water, all the way round?\n\nSo it's "
               "falling. Slowly, but it's falling.\n\nThat's what I was afraid of. The roof "
               "over this town is the floor of those dry caves you came through, and it's been "
               "drying for three years, ever since the ground shook. I need to think about what to tell "
               "the Thane."))

    q.append(Q("bst_water_for_the_quench", "Water for the Quench", HULDA, 51, 51, "onyxhollow",
               "Collect Lurker's Water Bladders from Blindwater Lurkers at the Last Water.",
               [fetch("bst_water_bladder", 6)],
               "Our well water's too soft. Dark iron quenched in it comes out with a skin like "
               "an eggshell.\n\nThe Last Water's hard and bitter and very cold, and blades "
               "quenched in it hold an edge twice as long. I'd send an apprentice with "
               "buckets, but the Blindwater Lurkers take apprentices.\n\nThe Lurkers carry "
               "water in a bladder under the jaw. Kill them and bring me the bladders, full. "
               "The lake's south of the gate.",
               "Still cold. Good.\n\nThat's enough for a dozen blades. You'll see the "
               "difference if you buy one. Here, this was quenched in the last lot. Take it."))

    q.append(Q("bst_the_lights_go_out", "The Lights Are Going Out", SIGRUN, 52, 52, "lantern",
               "Go to the east side of the Lantern Wood and kill the Hive Swarmers there.",
               [explore(52, 80, "the east side of the Lantern Wood"), k("Hive Swarmer", 12)],
               "The east side of the wood's gone dark. I noticed when I was out for caps. A "
               "whole stretch that used to glow has nothing growing in it now.\n\nMushrooms "
               "don't just stop. Something's taking them.\n\nGo and look, would you? The "
               "Lantern Wood is south-west of the gate, and the dark part is on its east side, "
               "nearest the lake. If it's what I think it is, you'll find Hive Swarmers there. "
               "Kill them.",
               "Swarmers, in the wood. I thought so.\n\nThe hive used to stay on its own side. "
               "If they're coming this far for mushrooms, they're short of food, or there are "
               "more of them than there were.\n\nI'll tell Captain Yrsa. She won't be "
               "pleased."))

    q.append(Q("bst_what_they_carry", "What They Carry", "item:bst_half_eaten_cap", 52, 52, "lantern",
               "A Hive Swarmer was carrying a cut mushroom cap. Show it to Alchemist Sigrun.",
               [deliver("bst_half_eaten_cap", "the half-eaten cap, to Alchemist Sigrun in Onyxhollow")],
               "The Swarmer had a piece of mushroom cap held in its jaws. It's been cut, not "
               "bitten. The edges are straight and clean.\n\nAlchemist Sigrun in Onyxhollow "
               "knows the Lantern Wood's mushrooms better than anyone. She'd want to see this.",
               "Where did you get this? Off a Swarmer?\n\nThey're not eating them. Look at the "
               "cuts. They're harvesting. They're carrying the caps back to the hive whole.\n\n"
               "You only do that if you're growing something. They're farming, in there, and "
               "they're using my wood for seed. Thank you for bringing it. I'd never have "
               "known.",
               turn_in_npc_id=SIGRUN))

    # ================= THE CASTOUTS =================
    q.append(Q("bst_names_in_the_book", "Names in the Book", ALDIS, 51, 51, "castout",
               "Ask Vault-Keeper Aldis about the people who were put out, then go and look at "
               "the old diggings.",
               [talk("bst_who_was_put_out", "bst_the_gallery"),
                explore(100, 31, "the entrance to the Castout Diggings")],
               "You've heard people here go quiet about the old diggings. I'll tell you why, "
               "since nobody else will.\n\nAsk me what you like. Then go and see the place for "
               "yourself. It's north-east of the gate, where the slag road ends. You'll know "
               "it by the broken gate arch. Don't go in further than that unless you mean to "
               "fight.",
               "You saw it, then. There are lamps lit in there. They're still working the "
               "seam.\n\nForty people, living in a mine with no forge and no gate. Some of "
               "them I've known since they were children.\n\nI've said for three years that the "
               "Thane put out too many. I couldn't prove who should have gone and who "
               "shouldn't. If you ever find something that does, bring it to me."))

    q.append(Q("bst_the_old_diggings", "The Old Diggings", YRSA, 51, 51, "castout",
               "Kill Castout Diggers and Castout Cutthroats raiding from the Castout Diggings.",
               [k("Castout Digger", 10), k("Castout Cutthroat", 8)],
               "I'll say this plainly. The people in the old diggings were ours, and I don't "
               "enjoy this.\n\nBut they've started raiding the slag road. Two carts last "
               "month, and a carter with his arm broken. They've no forge and no stores, so "
               "they take ours.\n\nThe Castout Diggings are north-east of the gate, at the end "
               "of the road. Go up there and push them back. The Castout Diggers and the "
               "Cutthroats are the ones doing the raiding. Leave anyone who doesn't raise a "
               "hand to you.",
               "It's done? All right.\n\nI knew some of them. I'm not going to ask you which "
               "ones you met.\n\nThe road's safe for now. That's what I'm paid for. Take "
               "this."))

    q.append(Q("bst_brannocs_shift", "Brannoc's Shift", BRANNOC, 52, 52, "castout",
               "Hear Brannoc out, then recover Shift Tally Sticks from Castout Diggers.",
               [talk("bst_brannocs_side"), fetch("bst_tally_stick", 8)],
               "You've been in and out of that gate. You'll have heard their side. I've had three "
               "years in the old diggings to think about mine.\n\nI'd like "
               "you to hear mine. It won't take long. After that there's something I need, "
               "and I can't get it myself.\n\nEvery miner on my shift kept a tally stick. It's "
               "notched for each cart, and it's branded with the gallery you were working. The "
               "Diggers still carry theirs. They're up in the Castout Diggings, north-east of "
               "here. They won't hand them over. Most of them think I'm a traitor for sitting "
               "this close to the gate.",
               "Let me see the brands. North drift. North drift. West heading. North "
               "drift.\n\nNot one of these is branded for the low gallery. We weren't in "
               "it.\n\nMost of the shift was nowhere near that gallery when it came down. The "
               "Thane never asked, and we were too frightened of the Foreman to say.\n\nI "
               "can't take these in. You can.",
               nxt="bst_weights_still_true"))

    q.append(Q("bst_weights_still_true", "The Weights Are Still True", BRANNOC, 52, 52, "castout",
               "Take the bundle of tally sticks to Vault-Keeper Aldis in Onyxhollow.",
               [deliver("bst_tally_bundle", "the bundle of tally sticks, to Vault-Keeper Aldis")],
               "Aldis keeps the weigh-books. Every cart that came out of every gallery is "
               "written down in them, with the name of whoever filled it.\n\nIf she sets these "
               "sticks against her books, she can show where each of us was working that "
               "shift. That's all I want. I'm not asking to be forgiven.\n\nShe's at the vault "
               "in the north-east corner of the town. Tell her they came from me.",
               "From Brannoc? Give them here.\n\nNorth drift, cart by cart. It matches. Every "
               "notch is in my book under the right name, on the right shift.\n\nThey weren't "
               "in the low gallery. Nine of them were, with the Foreman. The other thirty were "
               "half a mile away, filling carts.\n\nThree years they've been out there. I'm taking this to the Thane "
               "now, and he's going to listen this time.",
               turn_in_npc_id=ALDIS, nxt="bst_the_thanes_answer",
               grant_items=carry("bst_tally_bundle", "Bundle of Tally Sticks",
                                 "Eight notched sticks tied with a bootlace. Each one is "
                                 "branded with the gallery its owner was working.")))

    q.append(Q("bst_the_thanes_answer", "The Thane's Answer", THANE, 53, 53, "castout",
               "Kill Foreman Durn the Castout in the Castout Diggings.",
               [boss("Foreman Durn the Castout")],
               "Aldis has shown me her books. I've spent all night with them.\n\nThree years ago, "
               "the day the ground shook, a gallery came down and killed eleven of my people.\n\nI put out "
               "forty people for what nine of them did. I did it because nobody would give me "
               "a name, and I took that for guilt. It was fear. I should have known the "
               "difference.\n\nThey can come home, all of them who want to. But Durn won't "
               "let them. He was Foreman of that shift, he ordered them into a gallery he'd "
               "been told was unsafe, and he's run the old diggings ever since. Anyone who "
               "tries to leave, he kills.\n\nHe's in the Castout Diggings, north-east of the "
               "gate. I'm not asking you to bring him back.",
               "Durn's dead. Good.\n\nI've told Yrsa to open the gate to anyone from the old "
               "diggings who comes with empty hands. Brannoc walked through an hour ago. He "
               "didn't say anything to me and I didn't expect him to.\n\nThis doesn't put it "
               "right. But it's a start, and it wouldn't have happened without you. The vault "
               "has something set aside. Take it.",
               requires_quests=["bst_weights_still_true"]))

    q.append(Q("bst_the_shrine_fire", "The Shrine Fire", TORVALD, 52, 52, "castout",
               "Kill Castout Slagcallers in the Castout Diggings and bring back their Shrine "
               "Embers.",
               [k("Castout Slagcaller", 8), fetch("bst_shrine_ember", 5)],
               "When they were put out, some of them took fire from this bowl with them. I "
               "let them. It seemed wrong to send people into the dark without it.\n\nI "
               "shouldn't have. The ones we call Slagcallers have done something to it. They "
               "feed it things that aren't coal, and it burns the wrong colour now.\n\nIt's "
               "still our fire. I want it back before they do worse with it. The Slagcallers "
               "are in the Castout Diggings, north-east of the gate. They each carry some of "
               "it in a clay pot.",
               "Give them here. Carefully.\n\nYes, that's ours. You can see it trying to burn "
               "clean again now it's near the bowl.\n\nI'll put them back in, one at a time. "
               "Thank you. I've been ashamed of that for three years."))

    q.append(Q("bst_unsent_letter", "An Unsent Letter", "item:bst_unsent_letter", 52, 52, "castout",
               "A Castout was carrying a letter addressed to Innkeeper Brenna. Take it to her.",
               [deliver("bst_unsent_letter", "the unsent letter, to Innkeeper Brenna in Onyxhollow")],
               "The Cutthroat had a letter folded inside his jerkin. It's worn soft, as if "
               "it's been carried a long time. The outside reads: Brenna Coalcask, the Banked "
               "Fire.\n\nIt was never sent. Brenna keeps the inn in Onyxhollow.",
               "Where did you get this?\n\nThat's Hakon's hand. That's my brother.\n\nHe was "
               "on the shift that got put out. I haven't heard a word in three years. I thought "
               "he hated me for staying.\n\nHe says he's sorry he didn't write. He says he "
               "kept meaning to send it.\n\nHe's dead, isn't he? You wouldn't have this if he "
               "wasn't.\n\nNo, don't say anything. Thank you for bringing it. I'd sooner "
               "know.",
               turn_in_npc_id=BRENNA))

    # ================= THE HIVE =================
    q.append(Q("bst_listening_at_the_wall", "Listening at the Wall", RURIK, 52, 52, "hive",
               "Check the north side of the Chitin Reach in two places and kill Hive "
               "Sandburrowers.",
               [explore(108, 63, "the north-west edge of the Chitin Reach"),
                explore(126, 62, "the north-east edge of the Chitin Reach"),
                k("Hive Sandburrower", 8)],
               "I can hear digging through the wall. I've heard it every night this month, and "
               "it's getting closer. They never dug this way before the change.\n\nIt's the big ones, the Sandburrowers. They tunnel, and "
               "the rest of the hive follows down the tunnel after them.\n\nThe Chitin Reach "
               "is south-east of the gate. I want to know how far north they've dug. Look "
               "along the north edge of the Reach, the side nearest the town, at the west end "
               "and the east end. Kill any Hive Sandburrowers you find working there.",
               "Fresh tunnels at both ends, heading north. That's what I've been hearing.\n\n"
               "They're maybe a month from the wall at that rate. Less, if there are more of "
               "them than you saw.\n\nI'll take it to the Captain. And I'll tell Brokk to "
               "start making charges."))

    q.append(Q("bst_a_charge_down_the_hole", "A Charge Down the Hole", BROKK, 52, 52, "hive",
               "Set blasting charges at three burrow mouths in the Chitin Reach.",
               [explore(112, 78, "the western burrow mouth"),
                explore(128, 74, "the northern burrow mouth"),
                explore(124, 94, "the southern burrow mouth")],
               "Rurik says they're tunnelling at the wall. Right. I've got just the thing.\n\n"
               "These are slow charges. You set one at the mouth of a burrow, light the fuse "
               "and walk away. Don't run. It looks bad and you've plenty of time.\n\nThere are "
               "three big burrows in the Chitin Reach, south-east of the gate. One's on the "
               "west side, one's up at the north and one's down at the south. Drop a charge at "
               "each. The hive won't thank you, so expect company.",
               "All three? I felt them go. The whole Row did.\n\nThat's bought us a few "
               "months. They'll dig new ones, they always do, but they'll have to start from "
               "further back.\n\nYou kept your fingers, I see. Take this. I made it between "
               "batches.",
               grant_items=carry("bst_slow_charges", "Slow Charges",
                                 "Three iron canisters with long fuses. Brokk says they're "
                                 "perfectly safe. He was sitting on one when he said it.", 3)))

    q.append(Q("bst_amber_for_runes", "Amber for the Runes", THRAIN, 52, 52, "hive",
               "Collect Clear Amber Resin from Hive Resinspitters in the Chitin Reach.",
               [fetch("bst_amber_resin", 8)],
               "I fill my runes with silver. It works, but it's soft and it wears out.\n\nThe "
               "hive makes a resin that sets clear and hard as glass. If I can inlay a rune "
               "with that, it should last as long as the plate does. I've only ever had a "
               "thumb's worth to try.\n\nThe Resinspitters make it. They're in the Chitin "
               "Reach, south-east of the gate. They'll spit it at you, which is unpleasant, "
               "but what I need is the clear stuff they carry inside.",
               "That's ten times what I've ever had. And it's clean.\n\nGive me a day. If this "
               "works I'll never buy silver again.\n\nHere. It's one of my older pieces, but "
               "the rune's good. If the amber works I'll redo it for you."))

    q.append(Q("bst_reaver_plate", "Lighter Than Plate", HULDA, 52, 52, "hive",
               "Kill Hive Reavers in the Chitin Reach and collect their carapaces.",
               [k("Hive Reaver", 8), fetch("bst_reaver_plate", 5)],
               "One of the gate guards came back with a Reaver's back-plate strapped on as a "
               "shield. It turned a pick. I tried it myself.\n\nIt's lighter than dark iron "
               "and nearly as hard. I want to know if it can be riveted. If it can, I can "
               "make armour for the carters that they'll actually wear.\n\nThe Hive Reavers "
               "are in the Chitin Reach, south-east of the gate. They're the ones that walk "
               "upright. I need the back-plates whole, so try not to crack them.",
               "Whole, and hardly scratched. Well done.\n\nIt takes a rivet. I just tried. It "
               "takes a rivet and it doesn't split.\n\nThe carters are getting new jerkins. "
               "You're getting the first thing I made from the last piece I had."))

    q.append(Q("bst_toward_the_wood", "Between the Wood and the Wall", YRSA, 53, 53, "hive",
               "Kill Hive Reavers and Hive Swarmers in the Chitin Reach.",
               [k("Hive Reaver", 12), k("Hive Swarmer", 12)],
               "Sigrun says the hive's in her wood. Rurik says it's under my wall. They're "
               "both right, and I haven't the guards to hold both.\n\nSo I'm not going to "
               "hold either. I want the hive hurt badly enough at home that it pulls its "
               "raiders back.\n\nGo into the Chitin Reach, south-east of the gate, and kill "
               "Reavers and Swarmers until they stop coming out to meet you. Then come and "
               "tell me how deep the place goes.",
               "It goes down, at the back? Into a smaller chamber?\n\nThen that's where she "
               "is. Every hive has a queen. I've been hoping this one's had died.\n\nGo and "
               "see the Thane. This is past what a gate-captain decides.",
               nxt="bst_the_royal_cell"))

    q.append(Q("bst_the_royal_cell", "The Royal Cell", THANE, 53, 53, "hive",
               "Kill Hive Queen Zil'kesh in the Royal Cell, beyond the Chitin Reach.",
               [boss("Hive Queen Zil'kesh")],
               "Yrsa's told me. There's a queen.\n\nWe've lived beside that hive since we "
               "opened the gate. We burned its tunnels and it took our carters, and both "
               "sides could bear that. A hive that's farming and digging at my wall is a "
               "different matter. It means to grow.\n\nIt stops growing if the queen dies. "
               "The Royal Cell is at the far south-east corner of the cavern, through the "
               "back of the Chitin Reach. Her name, if the old tablets are right, is "
               "Zil'kesh.\n\nI can't spare guards for this. I'm asking you.",
               "She's dead. You're certain?\n\nThen the hive will fall apart. It may take a "
               "year, but it will.\n\nYou've done more for this town than most people born "
               "in it. I don't say that easily. The vault's open to you. Take what Aldis has "
               "set aside, and know that the gate's open to you for as long as I'm Thane."))

    # ================= OUT OF THE ZONE =================
    q.append(Q("bst_the_roof_report", "The Roof Report", VIGDIS, 53, 53, "strand",
               "Carry Vigdis's soundings up to Chief Surveyor Peska Vane at Fourth Peg, in the "
               "Abyssal Sands.",
               [deliver("bst_soundings", "Vigdis's soundings, to Chief Surveyor Peska Vane at Fourth Peg")],
               "I've told the Thane the lake's falling and the roof's drying. He asked me how "
               "long we have. I couldn't tell him.\n\nI can hear the roof from underneath. I "
               "can't see the top of it. Somebody up there must be able to.\n\nYou came down "
               "through the desert. Is there anyone up there who measures the ground? If "
               "there is, take them these. They're my soundings, three years of them, from the "
               "day the ground shook to now.\n\nThe "
               "only way up is the way you came: the stair at the Bottom Step, through the "
               "dry caves, and up one of the pits. Fourth Peg is the camp in the north-east "
               "of the Abyssal Sands.",
               "Soundings? From underneath?\n\nShe's been listening to the same roof I've "
               "been walking on. For three years.\n\nI've got how fast the pillars are being "
               "eaten. She's got how thick the rock is. I've never had the thickness. With "
               "both, I can work out how long it'll stand.\n\nGive me an hour with these. "
               "Then I'll have something for you to take back down.",
               turn_in_npc_id=PESKA, nxt="bst_what_peska_sent_back",
               requires_quests=["bst_the_last_water"],
               grant_items=carry("bst_soundings", "Vigdis's Soundings",
                                 "A thick roll of rubbings and figures. Three years of a "
                                 "geomancer listening to the roof of Onyxhollow.")))

    q.append(Q("bst_what_peska_sent_back", "What Peska Sent Back", PESKA, 53, 53, "onyxhollow",
               "Carry Peska's survey down to Thane Morgrim in Onyxhollow.",
               [deliver("bst_pillar_survey", "Peska's survey, to Thane Morgrim in Onyxhollow")],
               "Right. I've put her numbers and mine together.\n\nIt isn't good, but it's "
               "better than not knowing. The roof over that town will stand for about forty "
               "years if nothing changes. If somebody kills what's eating the pillars and "
               "keeps killing it, it'll stand a good deal longer.\n\nTake this to whoever "
               "runs the place. Tell them I'll send my crew down to shore the worst pillars "
               "if they'll send miners up to help. They know rock better than we do.\n\nBack "
               "the way you came: down a pit, through the Dry Deep to its east end, and down "
               "the stair. Onyxhollow's gate is at the end of the slag road.",
               "Forty years.\n\nI was expecting to hear five.\n\nAnd she'll shore the pillars "
               "if I send miners up. A goblin surveyor. My grandfather would have shut the "
               "gate on her.\n\nI'm not my grandfather. Tell Vigdis she has her answer, and "
               "tell Kelda to pick me twenty miners who don't mind daylight. We're going to "
               "go and look after our roof.",
               zone=AB, turn_in_npc_id=THANE,
               grant_items=carry("bst_pillar_survey", "Peska's Pillar Survey",
                                 "Four pages of figures in a very small hand, and a sketch of "
                                 "the Dry Deep with eleven pillars circled.")))

    return q


def audit(quests):
    bad = []
    ids = {q["quest_id"] for q in quests}
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        import tools.handbuilt_black_strand as M
        zone, L = M.build_black_strand_baked()
    seen = L._reach()
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"][M.NAME]
    spawns = set(enc["open_zone"]["creatures"])
    for s in enc["subzones"].values():
        spawns |= set(s["creatures"])
    droppable = {iid for rows in FETCH_DROPS.values() for (iid, _n, _d) in rows}
    droppable |= {iid for rows in STARTER_DROPS.values() for (iid, _n, _d, _c) in rows}
    for q in quests:
        text = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text",
                                                         "turn_in_text"))
        if not text.isascii():
            bad.append(f"{q['quest_id']}: non-ASCII text")
        granted = {g["item_id"] for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            if o["type"] in ("kill", "kill_boss"):
                if o["target"] not in spawns:
                    bad.append(f"{q['quest_id']}: {o['target']} does not spawn in the zone")
                if o["target"] not in text:
                    bad.append(f"{q['quest_id']}: never names {o['target']}")
            if o["type"] == "fetch" and o["target"] not in droppable:
                bad.append(f"{q['quest_id']}: fetches {o['target']}, which nothing drops")
            if o["type"] == "deliver" and o["target"] not in granted | droppable:
                bad.append(f"{q['quest_id']}: delivers {o['target']}, which nothing grants or drops")
            if o["type"] == "explore" and o["target"] == BS:
                if (o["target_x"], o["target_y"]) not in seen:
                    bad.append(f"{q['quest_id']}: {o['label']} is not a tile you can stand on")
        for nx in [q.get("next_quest_id")] + list(q.get("requires_quests") or []):
            if nx and nx not in ids:
                bad.append(f"{q['quest_id']}: refers to {nx}, which this pass does not define")
        # a number in the prose beside an objective's word reads as that objective's count
        if re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+"
                     r"(scorpion|bat|basilisk|sporeling|trampler|lurker|digger|cutthroat|"
                     r"slagcaller|swarmer|reaver|sandburrower|resinspitter|cap|gill|shell|"
                     r"bladder|stick|ember|resin|carapace|bar)s?\b", text, re.I):
            bad.append(f"{q['quest_id']}: a count in the prose beside an objective word")
    return bad


def main():
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
    rows = [(c, iid, nm, desc, RATE) for c, rr in FETCH_DROPS.items() for (iid, nm, desc) in rr]
    rows += [(c, iid, nm, desc, ch) for c, rr in STARTER_DROPS.items() for (iid, nm, desc, ch) in rr]
    for cre, iid, nm, desc, ch in rows:
        have = {r["item_id"]: r for r in drops.get(cre, [])}
        rec = {"item_id": iid, "name": nm, "category": "quest", "description": desc, "chance": ch}
        if iid in STARTER_IDS:
            rec["starts_quest_id"] = STARTER_IDS[iid]
        have[iid] = rec
        drops[cre] = list(have.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # reward_pack budgets in fractions; stored gear is whole numbers (qa_whole_number_gear)
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True,
                   stdout=subprocess.DEVNULL)

    town = sum(1 for q in quests if str(q["giver_npc_id"]).startswith("oh_"))
    starters = sum(1 for q in quests if str(q["giver_npc_id"]).startswith("item:"))
    chains = sum(1 for q in quests if q.get("next_quest_id"))
    print(f"{len(quests)} quests -> {OUT.name}: {town} given in Onyxhollow, {starters} started by "
          f"a drop, {chains} chained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
