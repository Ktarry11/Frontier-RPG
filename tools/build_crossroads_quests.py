#!/usr/bin/env python3
"""The Crossroads gets quests. It had none.

    PYTHONPATH=. python3 tools/build_crossroads_quests.py

Kyle, 13 Nov 2026: "Don't forget about the countless NPCs in cross roads that just have no
quest markers or purpose." Measured the day before: 21 NPCs in the town, every one a greeter,
trainer or vendor, and every Barrens quest given by somebody standing in the field - the
opposite of his rule that about 70% of a zone's quests come from town.

WHAT THIS DOES

1. MOVES six quests that were written for a Barrens that no longer exists. Five were given
   from Camp Taurajo and sent you to Far Watch Post and Mor'shan Base Camp, two maps north of
   the camp; one was given in Ratchet for the Raptor Grounds, which are next door to Camp
   Taurajo. Objectives and rewards are untouched; the giver changes, and the text is rewritten
   in the new giver's voice with directions that are true from where they stand.

2. ADDS twelve quests (data/quests/crossroads.json), across nine NPCs who had nothing:

     the roads out     five errands, each handed in to the warden who holds that piece of the
                       Barrens - so the town points you at the field instead of leaving you to
                       stumble on it (deliver objectives; no kill counts)
     leaving the zone  a dispatch to Orgrimmar, a letter to Ratchet, an old soldier's tag to
                       the Mor'shan Rampart
     the survey        Envoy Thaelis's report: three places, on foot
     the capstone      "The Crossroads Holds" - opens only when the Kolkar warbringer, the
                       Bramblescar wardchief and the Lushwater queen are all dead (three
                       separate field chains), and ends by carrying Sergra's report to the
                       tauren at Camp Taurajo. Kyle: "I love multichain quests or ones that
                       build to something important."

Idempotent: crossroads.json is written whole, moved quests are matched by id, and the
dialogue topics live in world/quest_dialogue_crossroads.py.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_deathknell_quests import pack        # noqa: E402

CR = "crossroads"
SERGRA, RUKA, BOORKA, GRUKAN = "crossroads_sergra", "crossroads_quartermaster", "crossroads_innkeeper", "crossroads_bounty_reader"
DRESK, THOKK, KOL, HALE, THAELIS, SNIX = ("crossroads_caravan_guard", "crossroads_retired_warrior", "crossroads_runner",
                                         "crossroads_human_traveler", "crossroads_beltelf_envoy", "crossroads_goblin_peddler")


def deliver(item_id, name, desc, label):
    """(objective, grant) for something the giver hands you to carry to somebody."""
    return (dict(type="deliver", target=item_id, count=1, label=label),
            dict(on_accept=[dict(item_id=item_id, name=name, description=desc, count=1)]))


def Q(qid, title, giver, lo, hi, desc, accept, done, objs, xp, gold, turn_in=None, grant=None,
      nxt=None, requires=None, rewards=None):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=CR, level_min=lo, level_max=hi,
             description=desc, accept_text=accept, turn_in_text=done, objectives=objs,
             reward_exp=xp, reward_gold=gold, next_quest_id=nxt)
    if turn_in:
        q["turn_in_npc_id"] = turn_in
    if grant:
        q["grant_items"] = grant
    if requires:
        q["requires_quests"] = requires
    if rewards:
        q["unique_item_defs"] = rewards
    return q


def new_quests():
    out = []
    A = out.append

    # ---------------------------------------------------------------- the roads out
    o, g = deliver("cr_sealed_orders", "Sergra's Sealed Orders", "Folded twice and sealed with a thumb. For the Plainswatcher.",
                   "Sergra's orders, to Plainswatcher Dorn")
    A(Q("cr_orders_east", "Orders for the Plainswatcher", SERGRA, 13, 16,
        "Sergra Darkthorn. I command here, and you'll forgive me if I get to it.\n\n"
        "The Kolkar hold the plains east of this town. They've had an outpost on the east road for years; "
        "now there's a war camp behind it, and a war camp means somebody has decided to stop raiding and start taking.\n\n"
        "I have one watcher on that road - Dorn, on the rise where the grass gives out. He's been asking me for soldiers. "
        "I don't have soldiers. I have these orders, which tell him to hold where he is and use whoever I send.\n\n"
        "That's you. Take them to him. If he has work, it's my work.",
        "Out the south gate - it's the only one - then east along the road. Dorn keeps his watch on the rise before the Kolkar "
        "Outpost. If you can see their tents, you've passed him.",
        "From Sergra? Give it here.\n\n'Hold where you are and use whoever I send.' That's it? That's the whole - no. No, that's fair. "
        "That's exactly what I'd have written.\n\nRight. You're who she sent. Let me show you what I've been looking at.",
        [o], 360, 1400, turn_in="barrens_scout_2", grant=g))

    o, g = deliver("cr_arrow_bundle", "Bundle of Crossroads Arrows", "Forty shafts, fletched in a hurry. For the south road.",
                   "the arrow bundle, to Ranger Kishi Plainstalker")
    A(Q("cr_arrows_south", "Arrows for the South Road", RUKA, 15, 18,
        "Ruka, quartermaster. You're not in my ledger, which means you're free, which means you can carry.\n\n"
        "The road south to Camp Taurajo runs between two quilboar holds - Bramblescar on one side, Agama'gor on the other. "
        "There is one ranger on it, a tauren called Kishi, and she has been holding that road with a bow and a bad temper "
        "since the season turned.\n\n"
        "She sent word she's down to her last quiver. I can't send a patrol. I can send arrows.\n\n"
        "Don't tell her they're from me. She'll want to argue about the fletching.",
        "South gate, then straight down the Taurajo road - a long walk, most of the way to the camp. Kishi stands on the road "
        "itself, where the thorn closes in on both sides.",
        "Arrows. From the Crossroads. Let me guess - Ruka, and she told you not to say.\n\n"
        "The fletching's crooked. It always is. I'll use every one.\n\nSince you've walked this far: the thorn on both sides of "
        "this road is full of quilboar, and I've got a list.",
        [o], 420, 1650, turn_in="cb_quilboar_ranger", grant=g))

    o, g = deliver("cr_stew_crock", "Crock of Crossroads Stew", "Sealed with wax and still warm. It weighs more than it should.",
                   "the crock of stew, to Waterkeeper Sanu Goldenhoof")
    A(Q("cr_stew_for_sanu", "Stew for the Waterkeeper", BOORKA, 14, 17,
        "Boorka. Sit - no, don't sit, I need you standing.\n\n"
        "There's a tauren at Lushwater Oasis, Sanu, who keeps the springs. She used to come up to town once a month for a "
        "proper meal and the gossip. She hasn't come in two. The caravan drivers say she won't leave the water now - that "
        "something's wrong with it and she's sitting up nights watching it.\n\n"
        "Nobody who sits up nights is eating. I've made her a crock.\n\n"
        "Take it down to her. And look at that water while you're there, because if the oases are going bad, this town is "
        "the next thing that does.",
        "South gate, then south-west across the plain to Lushwater Oasis - the big green one, you can't miss the trees. "
        "Sanu sits on the east bank.",
        "Boorka sent this? Earth Mother keep her. I had not noticed I was hungry until I smelled it.\n\n"
        "Sit a moment. You have walked a long way to bring an old cow her supper, and I have something to show you that I "
        "would rather not look at alone.",
        [o], 390, 1500, turn_in="cb_waterkeeper", grant=g))

    o, g = deliver("cr_bounty_notice", "Torn Bounty Notice", "'The Dreadmist cult. Reward on proof.' The corner is brown with age.",
                   "the bounty notice, to Scout Zarla Blackthorn")
    A(Q("cr_board_dreadmist", "The Bounty Nobody Takes", GRUKAN, 15, 18,
        "Grukan. I keep the board. You're looking at the bottom of it, which is where the old ones go.\n\n"
        "That one's been up since before the last rains. The Burning Blade has a den on Dreadmist Peak, north-west of here, "
        "and somebody posted coin for it. Others have taken the notice down before you. None of them put it back, and none of them collected.\n\n"
        "There's a scout up there now - Zarla Blackthorn. She went to find out what happened to them. She's still "
        "reporting, so she's still alive, which makes her the only one who knows the ground.\n\n"
        "Take her the notice. If the bounty's ever going to be paid, it'll be on her say.",
        "South gate, then north-west - a long way, past the Forgotten Pools, to where the ground climbs toward Dreadmist Peak. "
        "Zarla's camp is in the rocks below the canyon mouth. Keep your voice down when you get there.",
        "Quiet. Quieter than that.\n\nLet me see - oh, that old thing. Grukan still has it up? There are names on the back. I found "
        "most of them.\n\nYou want to collect on this, you do it my way, and my way starts with not being heard.",
        [o], 420, 1650, turn_in="cb_dreadmist_scout", grant=g))

    o, g = deliver("cr_axle_pins", "Sack of Axle Pins", "Iron pins, greased and wrapped. Heavy for their size.",
                   "the axle pins, to Caravan-Master Dogan Ironcart")
    A(Q("cr_wheels_for_dogan", "Wheels for Dogan", DRESK, 16, 19,
        "Dresk. Caravan guard. I'm meant to be on the Ratchet run today and I'm not, because the Ratchet run isn't running.\n\n"
        "Dogan Ironcart's wagons are stopped at Raider's Rest Oasis, on the road south-east. Three of them, axles gone. "
        "Not broken - gone. Somebody pulled the pins in the night, which is a thing bandits do when they'd like you to "
        "stay put while they fetch their friends.\n\n"
        "I've got spare pins. I've also got orders not to leave the gate. You haven't.",
        "South gate, then south-east along the Ratchet road until you see water and wagons. That's Raider's Rest. Dogan is the "
        "goblin shouting at the wagons.",
        "Pins! Finally! Do you know what it costs me per day to sit here? I do, I've been counting, it's the only thing "
        "keeping me warm.\n\nDresk sent you? Then you can fight. Good. Because the people who took these are still here, and I "
        "would like to discuss it with them.",
        [o], 450, 1800, turn_in="cb_caravan_master", grant=g))

    # ---------------------------------------------------------------- leaving the zone
    o, g = deliver("cr_dispatch_case", "Sealed Dispatch Case", "Crossroads to Orgrimmar. The seal is Sergra's.",
                   "the dispatch case, to Scout Windrider in Orgrimmar")
    A(Q("cr_dispatch_orgrimmar", "By Nightfall", KOL, 13, 16,
        "Kol. Runner. I've got a problem and it's got two legs, both mine.\n\n"
        "This goes to Orgrimmar - Sergra's count of what the Crossroads is holding and what it can't. It's meant to be "
        "there by nightfall. I've already run it from the south road this morning, and my left knee has made its position clear.\n\n"
        "You're going that way sooner or later; everyone does. Take it. Scout Windrider at the city takes the Barrens "
        "reports - he'll want to hear how the road looked, too, so keep your eyes open on the way.",
        "North-east from the south gate to the Southfury bridge, across into Durotar, then north up the highway to Orgrimmar. "
        "Scout Windrider takes the reports in the city. Don't open the case.",
        "From the Crossroads? You're not Kol.\n\nNo - don't explain, I can guess, it's the knee. Let me see the seal. Good.\n\n"
        "Sergra says she's holding. She always says she's holding. Tell me what the road actually looked like, and then "
        "I've got work for someone who's just walked it.",
        [o], 520, 2100, turn_in="org_scout", grant=g))

    o, g = deliver("cr_hale_letter", "Corwin Hale's Letter", "Addressed in a careful hand: 'Delia Thorne, Ratchet. By hand, please.'",
                   "Corwin's letter, to Delia Thorne in Ratchet")
    A(Q("cr_hale_letter", "By Hand, Please", HALE, 14, 17,
        "Corwin Hale. I drive for the caravans. You'll have noticed I'm not an orc.\n\n"
        "There's a woman in Ratchet called Delia Thorne. Stormwind, like me, and left it, like me. We came over on the same "
        "boat and agreed we'd never speak of home again, and we've kept to that for years by not speaking at all.\n\n"
        "I've written to her. I've written to her eleven times, as it happens, and this is the first one I haven't burned.\n\n"
        "The Ratchet run's stopped. I'd take it myself, but I think if I had the whole road to think about it I'd turn round. "
        "Would you? By hand. She won't take it from a goblin.",
        "South gate, then the Ratchet road south-east, all the way to the coast. Delia keeps to the south end of town, away "
        "from the docks.",
        "From Corwin? Corwin Hale?\n\n...He wrote 'by hand'. Of course he did. Twelve years and he still thinks I'd lose a "
        "letter.\n\nGive me a moment. No - stay. If you're going back that way, I may need you to carry something that isn't "
        "a letter, and isn't short.",
        [o], 520, 2100, turn_in="ratchet_human_expat", grant=g))

    o, g = deliver("cr_warsong_tag", "Thokk's Warsong Tag", "A lumber-camp tally tag, punched with an eye and nine notches.",
                   "Thokk's Warsong tag, to Captain Korvash at the Mor'shan Rampart")
    A(Q("cr_what_it_costs", "What It Costs", THOKK, 17, 20,
        "Thokk. Sit down, you make the gate look untidy.\n\n"
        "You're going north eventually. They all do - up the Gold Road, through the Rampart, into Ashenvale to cut trees "
        "the night elves would rather keep. I did it for six years.\n\n"
        "There's a captain on the Rampart now, Korvash. Gatebreaker, they call him, which tells you he's young. He sends "
        "recruits past that wall every week and I don't believe anyone has told him what's on the other side of it.\n\n"
        "Ask me about it first. Then take him my tag. He'll know the notches.",
        "Ask me what you want to know. Then it's north: out the gate, up the Gold Road the whole length of the Northern "
        "Barrens, to the Mor'shan Rampart at the very top. Korvash stands in front of the wall.",
        "Where did you get - this is a Warsong tally tag. Nine notches. An eye punched through it.\n\n"
        "One-Eye Thokk. He's alive? They told us the whole first line went down at the river.\n\n"
        "Nine seasons. Nobody does nine seasons. Tell me what he said to you. All of it - and then I'm going to change "
        "some orders.",
        [dict(type="dialogue", topics=["cr_thokk_eye", "cr_thokk_line"]), o], 650, 2500,
        turn_in="nb_rampart_captain", grant=g))

    # ---------------------------------------------------------------- the survey
    A(Q("cr_envoys_report", "The Envoy's Report", THAELIS, 14, 17,
        "Envoy Thaelis, of Silvermoon. You will do.\n\n"
        "I am to report on the Horde's holdings in the Barrens. I have so far reported on this town, which took a paragraph. "
        "Silvermoon will want more than a paragraph, and I am told the rest of it is outdoors.\n\n"
        "Three places. The Sentinel Rocks, north of here, which the herders say something has nested in. The Kodo "
        "Graveyard beyond them, where the great beasts go to die - I am assured this is a real place and not an orcish "
        "joke. And the Forgotten Pools to the north-west, where pilgrims went to pray and did not come back.\n\n"
        "Walk to each. Look at it. Tell me what the Horde is actually holding.",
        "South gate, then north. The Sentinel Rocks are the red stones just north of town; the Kodo Graveyard is the bowl "
        "east of them; the Forgotten Pools lie north-west, a longer walk. I shall wait here, in the shade.",
        "Scorpids in the rocks. A valley of bones with something walking in it. And a pool full of the drowned.\n\n"
        "I see. So the Horde holds a town, three roads, and a great deal of ground it has not yet asked for permission to stand on.\n\n"
        "That is, in fact, more honest than I expected, and I shall report it as such. Silvermoon thanks you. Take something "
        "from the envoy's chest.",
        [dict(type="explore", target="central_barrens", target_x=146, target_y=98, radius=12, label="the Sentinel Rocks, north of the Crossroads"),
         dict(type="explore", target="central_barrens", target_x=205, target_y=120, radius=12, label="the Kodo Graveyard, east of the Sentinel Rocks"),
         dict(type="explore", target="central_barrens", target_x=81, target_y=86, radius=12, label="the Forgotten Pools, north-west of the Crossroads")],
        850, 3300,
        rewards=pack(16, 14, "uncommon", [
            ("Envoy's Dust Veil", "head", "of the Seer", "", "cloth"),
            ("Silvermoon Surveyor's Bracers", "wrist", "of the Bandit", "", "leather"),
            ("Thaelis's Measuring Rod", "main_hand", "of the Invoker", "", "staff")])))

    A(Q("cr_one_careful_owner", "One Careful Owner", SNIX, 13, 15,
        "Snix Cogsworth! Purveyor! You look like someone with legs.\n\n"
        "Here's the thing. I sell luck. Charms, mostly - a plainstrider feather on a bit of cord, blessed by a shaman, or "
        "by somebody standing near a shaman. Used to be I couldn't keep them on the table. A caravan driver would buy three.\n\n"
        "Then your lot showed up. People who get killed on Tuesday and are back complaining about it on Wednesday. Nobody "
        "buys luck from me any more, friend. Why would they? You've made dying look like a bad night's sleep.\n\n"
        "So I'm doing hats. Feathers in hats. Bring me the feathers and I'll cut you in.",
        "The big plainstriders, out the south gate on the Central Barrens plain - any direction, they're everywhere. Unbroken feathers. "
        "The broken ones look like bad luck, and I've got enough of that.",
        "Unbroken! Every one! Look at the barbs on that.\n\nYou know, I hold your whole kind responsible for my margins, and I "
        "want that understood. But you personally I've got no quarrel with. Here. First hat's on the house. The second "
        "one I'm charging you double.",
        [dict(type="fetch", target="cr_plainstrider_feather", count=6, label="Unbroken Plainstrider Feather")], 800, 3100,
        rewards=pack(15, 13, "uncommon", [
            ("Cogsworth's Lucky Hat", "head", "of the Bandit", "", "leather"),
            ("Caravan Driver's Charm", "neck", "of the Bear", "", None),
            ("Peddler's Road Boots", "feet", "of the Soldier", "", "mail")])))

    # ---------------------------------------------------------------- the capstone
    A(Q("cr_crossroads_holds", "The Crossroads Holds", SERGRA, 18, 22,
        "You. Come here. I've been counting.\n\n"
        "When you first walked through my gate I had the Kolkar building a war camp east of me, quilboar closing the "
        "Taurajo road to the south, and the oases going bad to the south-west. Three fires, and one town in the middle with "
        "no soldiers to send to any of them.\n\n"
        "Dorn's last report says the warbringer is dead. Kishi's says the wardchief of Bramblescar is dead. And Sanu sent "
        "a runner - Sanu, who never sends anyone - to say the queen under Lushwater is dead and the springs are running clean.\n\n"
        "I did not do that. I sat behind this wall and wrote orders. Sit down and tell me how it was done, because I have "
        "to put it in a report and I intend to get it right.",
        "Tell me about each of them. The east first.",
        "East, south and water. All three, and I never left the wall.\n\n"
        "I'm going to write it exactly as you told it, and I'm going to write that the Crossroads holds - which I have "
        "written every month for three years, and this is the first time I've believed it.\n\n"
        "Take your pick of the armoury. Then I've one more thing to ask, and it isn't an order.",
        [dict(type="dialogue", topics=["cr_hold_east", "cr_hold_south", "cr_hold_water"])], 1700, 6000,
        nxt="cr_word_for_the_tribes",
        requires=["cr_orders_east", "cb_warbringer_gorrak", "cb_wardchief_thulg", "cb_queen_skitterwing"],
        rewards=pack(22, 18, "rare", [
            ("Crossroads Warden's Breastplate", "chest", "of the Champion", "", "plate"),
            ("Darkthorn's Dispatch Mantle", "shoulder", "of the Archmage", "", "cloth"),
            ("Three Fires Longbow", "ranged", "of the Hunt", "", "bow"),
            ("Gatekeeper's Linked Coif", "head", "of the Hierophant", "", "mail")])))

    o, g = deliver("cr_sergra_report", "Sergra Darkthorn's Report", "'The Crossroads holds.' Underlined once, hard enough to tear the page.",
                   "Sergra's report, to Elder Longtread at Camp Taurajo")
    A(Q("cr_word_for_the_tribes", "Word for the Tribes", SERGRA, 18, 22,
        "Orgrimmar gets a copy of this. Orgrimmar gets a copy of everything.\n\n"
        "The other copy is for Camp Taurajo. The tauren lost their city and they lost Cairne, and since then every piece "
        "of news that's gone down that road has been bad - another herd gone, another well soured, another camp that "
        "stopped answering. Elder Longtread carries all of it. I've met him. He doesn't complain, which is how you know.\n\n"
        "I want him to hear this from someone who was there. Not a runner. You.\n\n"
        "And when you've told him, ask him what the south looks like. The road's open now. I expect that means I'm about "
        "to find out what was on the other end of it.",
        "South gate, then straight down the Taurajo road, past Kishi, all the way to the camp. Longtread sits on the "
        "north-west side, by the carvers.",
        "From Sergra Darkthorn. Read it to me - my eyes are not what they were.\n\n"
        "...'The Crossroads holds.'\n\n"
        "I have not had a letter that began well since the bluffs fell. I am going to have it read out at the fire tonight, "
        "and I am going to have it read twice.\n\n"
        "You were there. Then sit, and eat, and afterwards I will tell you what lies south of this camp - because the "
        "road you opened does not end here.",
        [o], 700, 2600, turn_in="taurajo_elder", grant=g))
    return out


TOPICS = {
    "cr_what_it_costs": {
        "cr_thokk_eye": {
            "label": "Ask how he lost the eye.",
            "response": (
                "Arrow. Night elf arrow, from a tree I'd walked under an hour before and looked straight up into.\n\n"
                "That's the thing nobody tells the recruits. You don't see them. You're not meant to. The first you know of "
                "a sentinel is somebody next to you sitting down, and they don't get up.\n\n"
                "I was lucky. It went in at an angle. The orc beside me took the one that was aimed properly.")},
        "cr_thokk_line": {
            "label": "Ask what's on the other side of the Rampart.",
            "response": (
                "Trees. You'll think I'm being short with you. I'm not.\n\n"
                "Trees older than Orgrimmar, older than the Horde, and every one of them belongs to somebody who has been "
                "defending it since before your grandmother's grandmother. We go in to cut them because the city needs "
                "timber, and we call it the Warsong line as if it were a line. It isn't. It's wherever the last orc is standing.\n\n"
                "I'm not saying don't go. The city does need the timber. I'm saying the captain up there should know what "
                "he's spending. Take him the tag. Nine notches is nine seasons, and I'm the only one from my camp who cut all nine.")},
    },
    "cr_crossroads_holds": {
        "cr_hold_east": {
            "label": "Tell her about the Kolkar war camp.",
            "response": (
                "A drum. Dorn wrote that there was a drum, and I thought he was being poetic, which isn't like him.\n\n"
                "So the taskmasters kept the warriors in line and the warbringer kept the taskmasters, and when he went down "
                "the whole camp stopped being an army and went back to being a clan with a grudge. Good. A grudge I can live "
                "next to. I've lived next to that one for years.\n\nThe south, now.")},
        "cr_hold_south": {
            "label": "Tell her about the wardchief of Bramblescar.",
            "response": (
                "Kishi's report was four words long. 'Thulg is dead. Arrows.'\n\n"
                "I take it that means the road to Taurajo is open and she'd like more arrows. I'll send both.\n\n"
                "You understand what that road is? It's the only way the tauren have to reach us that doesn't go through "
                "somebody's spears. With Bramblescar leaderless, a calf could walk it. That matters more than the war camp did.\n\n"
                "And the water.")},
        "cr_hold_water": {
            "label": "Tell her about the queen under Lushwater.",
            "response": (
                "Under it. Silithid, under the oasis, and I've been watering my kodo there since I took this post.\n\n"
                "Sanu says the springs are clean. She also says the thing that soured them didn't start at Lushwater - that "
                "it comes up out of the Wailing Caverns and the queen was only feeding on it. So that isn't finished. I'm "
                "aware it isn't finished.\n\n"
                "But the water's clean today, and a week ago it wasn't, and I know who to thank.")},
    },
}

#: quest id -> (file stem, new giver, new zone slug, text fields)
MOVED = {
    "taurajo_centaur_wind": ("northern_barrens", RUKA, CR, dict(
        description="Ruka, quartermaster. I've sent three warbands north this season and had two come back.\n\n"
                    "The Kolkar are raiding the Northern Barrens road - not the war camp out east, a different clan, and "
                    "faster. They hit Far Watch Post, where the road bends toward Durotar, and they're gone before the "
                    "garrison is off the wall.\n\n"
                    "I can't spare another warband. I can spare you.\n\n"
                    "Kill their raiders where you find them, and do it where the garrison can see. Half of holding a "
                    "post is the post believing somebody's coming.",
        accept_text="South gate, then north up the Gold Road until the Barrens changes its name. Far Watch Post is on the "
                    "east side of the Northern Barrens, where the road bends toward Durotar. The raiders work the ground "
                    "round its palisade.",
        turn_in_text="Good. Kelsara will have counted from the wall, and she'll write to say so, and that's one "
                     "letter this month I'll enjoy reading.\n\nDon't put your pack down. I want to know what that post "
                     "actually looks like.")),
    "taurajo_scout_outposts": ("northern_barrens", RUKA, CR, dict(
        description="Outrider Kelsara's reports say Far Watch holds. Her requisitions say she's going through arrows "
                    "like a siege.\n\nBoth of those can't be true, and I have to decide which one to supply.\n\n"
                    "Go and look at the post itself. Not the raiders - the wall. Count the gaps in it and the faces on "
                    "it, and come back and tell me what I'm paying for.",
        accept_text="Far Watch Post again - the east side of the Northern Barrens, where the road bends toward Durotar. "
                    "Walk right up to the palisade.",
        turn_in_text="Holding, but holding thin. Patched in three places and the patches are newer than the wall.\n\n"
                     "That's what I thought. She gets the arrows, and she gets them today.")),
    "taurajo_outriders_warning": ("northern_barrens", RUKA, CR, dict(
        description="The outriders came in overnight, and I don't like what they brought.\n\n"
                    "The raiders you thinned at Far Watch were a screen. The clan itself is massing at Mor'shan Base Camp, "
                    "in the north of the Northern Barrens, below the Rampart.\n\n"
                    "If they take the base camp they cut the Gold Road, and then nothing reaches Ashenvale and nothing "
                    "comes back from it. The Warsong up there are fighting on what we send them.\n\n"
                    "Hit the raiders where they're gathering, before they've finished gathering.",
        accept_text="Mor'shan Base Camp - north up the Gold Road, most of the length of the Northern Barrens, just short of "
                    "the Rampart. They're massing round it. Their marauders on the Kolkar Plains, east of this town, are "
                    "the same clan and count the same.",
        turn_in_text="Broken up at the base camp. Then the road's open for another month.\n\n"
                     "I'd promote you if you were mine. Since you're not, take what a warband would have drawn.")),
    "taurajo_salvage_wagons": ("northern_barrens", DRESK, CR, dict(
        description="Dresk. Caravan guard. You want to know what I guard? Grain. Three wagons of it left here for Far "
                    "Watch Post and none of them got there.\n\n"
                    "The Kolkar raiders hit the wagons and ran them down. They don't even want the grain. They want the "
                    "post hungry. But a raider's a raider, and a sack is worth carrying, so they'll have taken what "
                    "they could sling over a saddle.\n\n"
                    "Get it back off them. Trampled is fine. Trampled grain still makes bread.",
        accept_text="North up the Gold Road into the Northern Barrens. The Kolkar raiders round Far Watch Post, on the "
                    "east side, and round Mor'shan Base Camp are carrying the sacks.",
        turn_in_text="Trampled, split, and one of them's been bled on.\n\n"
                     "It'll do. Sift it and it's bread. Far Watch eats this week because of you - I'll make sure Kelsara knows whose name to curse less.")),
    "taurajo_windhoofs_ledger": ("northern_barrens", GRUKAN, CR, dict(
        title="Bounty: Kolkar Raiders",
        description="Grukan. The board. This one's fresh - Sergra put it up herself, and Sergra doesn't post bounties, "
                    "she posts orders, so you know she's run out of people to order.\n\n"
                    "Kolkar raiders, in the Northern Barrens. A full count of them, proof on the hoof. They're the ones cutting "
                    "the road to Far Watch and massing at Mor'shan.\n\n"
                    "No name on it. No khan, no chieftain. Just a number. That's the kind of bounty you post when you're "
                    "not trying to win, you're trying not to lose.",
        accept_text="The Northern Barrens - north up the Gold Road. They raid round Far Watch Post in the east and mass at "
                    "Mor'shan Base Camp in the north. The marauders and drudges on the Kolkar Plains, east of town, count too.",
        turn_in_text="That's the count. I'll mark it paid.\n\nFirst one off this board in a month. I'm going to leave the nail in, "
                     "so people can see there used to be something there.")),
    "ratchet_thinning_the_grounds": ("southern_barrens", "taurajo_hunter_1", "camp_taurajo", dict(
        description="Kala. I hunt for the camp. Walk with me a moment.\n\n"
                    "The kodo moved south early this year, and I have been finding out why. It is the raptors. The "
                    "Sunscale on the Raptor Grounds have bred past what the ground can feed, and the lashtails - the "
                    "young hunters, the bold ones - have started running the herds instead of the strays.\n\n"
                    "A herd that is run does not graze. A herd that does not graze does not calve. I will not have this "
                    "camp go hungry in spring for the sake of a raptor's good year.\n\n"
                    "Thin the lashtails. Not all of them. The Grounds are theirs. Only enough that they remember it.",
        accept_text="Out the south gate into the Southern Barrens, then south-east, below the Hoodoo Spires. The Raptor "
                    "Grounds are the red flats there. The lashtails are the ones with the banded tails.",
        turn_in_text="That is enough. Leave the rest.\n\nThe herds will come back up by the next moon. You will not "
                     "see it, I think - you have the look of someone going south. But the calves will, and that is who it was for.")),
}

#: Text only: the giver stays, the directions become true.
RETEXT = {
    "taurajo_carvers_materials": dict(
        accept_text="Off the Kolkar marauders - not the raiders, their horn is too young. The marauders keep to the Kolkar "
                    "Plains: out the north gate, up past the Crossroads, then east."),
}


def main():
    quests = new_quests()
    (ROOT / "data/quests/crossroads.json").write_text(json.dumps(
        {"_note": "Built by tools/build_crossroads_quests.py - do not hand-edit.", "quests": quests},
        indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    overlay = {}
    for qid, (stem, giver, zone, text) in MOVED.items():
        path = ROOT / f"data/quests/{stem}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        q = next(x for x in data["quests"] if x["quest_id"] == qid)
        q["giver_npc_id"], q["zone"] = giver, zone
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        overlay[qid] = text
    overlay.update(RETEXT)
    for qid, fields in overlay.items():
        for k, v in fields.items():
            assert v.isascii() and len(v) <= 760, (qid, k, len(v))
    for q in quests:
        for k in ("description", "accept_text", "turn_in_text"):
            assert q[k].isascii() and len(q[k]) <= 760, (q["quest_id"], k, len(q[k]))
    (ROOT / "data/quests/text/zz_overhaul_crossroads.json").write_text(json.dumps(overlay, indent=1) + "\n", encoding="utf-8")

    # the one new drop
    dp = ROOT / "data/creatures/quest_drops.json"
    drops = json.loads(dp.read_text(encoding="utf-8"))
    rows = drops["drops"].setdefault("Greater Plainstrider", [])
    if not any(r["item_id"] == "cr_plainstrider_feather" for r in rows):
        rows.append({"item_id": "cr_plainstrider_feather", "name": "Unbroken Plainstrider Feather",
                     "description": "Long, grey, and every barb still zipped. Snix will know.", "chance": 0.75})
    dp.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    body = ('"""Dialogue topics for the Crossroads quests. Written by tools/build_crossroads_quests.py.\n\n'
            'EVERY TOPIC A QUEST NAMES MUST BE IN HERE - see world/quest_dialogue_shimmering_flats.py.\n"""\n\n'
            "QUEST_TOPICS = " + json.dumps(TOPICS, indent=4) + "\n")
    (ROOT / "world/quest_dialogue_crossroads.py").write_text(body, encoding="utf-8")
    # Reward items come out of pack() with fractional stats; the files must hold whole numbers.
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], cwd=ROOT, check=True)
    print(f"crossroads: {len(quests)} new quests, {len(MOVED)} moved, {len(RETEXT)} re-worded")


if __name__ == "__main__":
    main()
