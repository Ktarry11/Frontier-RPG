#!/usr/bin/env python3
"""Ashenvale open-world quest pass -> data/quests/ashenvale.json (+ Blackfathom into ashenvale_dungeons.json via the dungeon
builder) and the NPCs / quest drops they need.  Idempotent.

    python3 tools/build_ashenvale_openworld_quests.py

What it does
  1. REWRITES the text of the 18 original Ashenvale quests (same quest_ids, so saves keep working) and wires them into chains.
  2. ADDS new quests: Astranaar / Maestra's Post (West), Zoram Strand, Splintertree Post, Warsong Lumber Camp and Raynewood Retreat (East).
  3. Adds the two East camp NPCs and the four quest-item drops the new fetch quests need.

Kyle's rules: NO escorts, kill / fetch / gather / explore / boss only.  Every giver is a person with their own mind (the Earth-meets-WoW
vision): speech is specific to the NPC, not "kill X, doesn't matter how".  Reward XP/gold follow tools/relevel_ashenvale tables.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.relevel_ashenvale import _XP, _GOLD, _base  # noqa: E402

QP = ROOT / "data/quests/ashenvale.json"
WEST, EAST = "Ashenvale West", "Ashenvale East"

# ===================================================================== 1. REWRITES of the original 18 (text + chain links only)
REWRITE = {
    # ---- Maestra's Post
    "ashenvale_grizzly_problem": dict(
        description="Sentinel Maestra has watched the grizzlies around the lake come closer every week. Bears do not do that on their own. "
                    "She wants the boldest of them put down before one walks into Astranaar's market.",
        accept_text="Bears keep to the trees. These ones come down to the water and stand there, watching the post. "
                    "I don't like being watched by anything that can't tell me why.",
        turn_in_text="Eight. Good. The lake path is quiet again, and I'll take quiet, even if it's borrowed. "
                     "Mind the Highlands, though. Whatever is pushing them out of there hasn't stopped."),
    "ashenvale_timberling_bark": dict(
        description="The wards on Maestra's Post are carved from timberling heartwood, and the old ones are splitting. "
                    "She needs five fresh lengths, taken from the timberlings in Silverwind Vale.",
        accept_text="Heartwood holds a ward the way nothing I can buy does, and the old posts are cracking. "
                    "The timberlings wear it in their chests. Don't ask me to be gentle about it, they weren't gentle with my last fence.",
        turn_in_text="Warm still. Good, that means it's alive enough to hold. These will see us through the winter. "
                     "You'd make a decent carpenter, which is not an insult."),
    "ashenvale_ursal_the_mauler": dict(
        description="Ursal the Mauler is the biggest of the Highland bears and the one herding the rest toward the lake. "
                    "With the furbolg shamans' totems dealt with, the Sentinels finally know where he lairs.",
        accept_text="Shalasyr tells me the totems are done. Then Ursal has nothing left feeding him but his own temper. "
                    "Go and finish it, and take a good look at his eyes before you do. Tell me if they were the bear's.",
        turn_in_text="You looked? ... Black all through, you said. Then he never chose any of it. "
                     "Take his claw. It's the one thing of his I'd be glad to see leave the forest."),
    # ---- Astranaar: Sentinel Shalasyr (liaison)
    "ashenvale_sentinel_scouts_report": dict(
        description="Two Sentinel scouts sent toward the Ragged Highlands never reported back. "
                    "Shalasyr wants their patrol route retraced as far as the Highlands themselves.",
        accept_text="Two of mine went up the ridge road nine days ago. They're good, and careful, and I'd have heard by now. "
                    "Walk their route. I don't need heroics, I need to know where the road stops being safe.",
        turn_in_text="The road stops at the furbolg line, then. Not a bandit camp and not a patrol. That narrows it. "
                     "I'm sorry about the scouts. I'd hoped for a worse story and a living one."),
    "ashenvale_furbolg_ravagers": dict(
        description="The furbolg of the Ragged Highlands have gone from wary to savage. Shalasyr wants the ravagers who "
                    "hold the ridge thinned so her scouts can find out why.",
        accept_text="Furbolg and Sentinels have shared this forest for a long time without a drop of blood. "
                    "Now the ravagers attack anything that crosses the ridge. Something has changed them. Thin them, and look closely.",
        turn_in_text="You say their fur was matted with something black? I was afraid of that. "
                     "It isn't hunger, or territory. It's something done to them."),
    "ashenvale_furbolg_shaman_totems": dict(
        description="The ravagers are being driven from behind. Shalasyr thinks the Highland shamans' totems carry the corruption, "
                    "and wants four of them brought out of the den.",
        accept_text="The shamans plant totems in the dens, and the dens are where the madness is worst. "
                    "Bring me four, and carry them in cloth. I won't have you holding them bare.",
        turn_in_text="It hums. Stop, don't hold it near your ear. We'll study them where nobody sleeps. "
                     "Now we know where the rot enters. Maestra will want to hear it was a bear that led the herding."),
    # ---- Astranaar: Grove Warden Pennarin
    "ashenvale_wisp_lights": dict(
        description="The wisps in the Moonwhisper Grove are the grove's own lanterns, and Pennarin has seen them dimming. "
                    "She wants six motes of their light drawn into vials so the healers can learn why.",
        accept_text="They are old, the wisps. They remember who planted the Grove, or they did. "
                    "Now they flicker. Bring me what falls from them when they fade, and don't take a mote that doesn't fall.",
        turn_in_text="Cold at the center, see? A light should never be cold. Thank you, truly. "
                     "I know what that costs when it's your own grove's lanterns."),
    "ashenvale_keeper_rustveil": dict(
        description="Keeper Rustveil was the Grove's guardian spirit for longer than Astranaar has stood. "
                    "Something has turned him against the forest he watched. Pennarin cannot ask anyone to do this lightly.",
        accept_text="Rustveil taught me my first song. I am asking you to put him down, and I'm asking knowing what I ask. "
                    "Do it quickly. If he can know, I don't want him to know long.",
        turn_in_text="It is done, then. Thank you. He would have thanked you too, before. "
                     "Take what he left, and let this ring remember him for me."),
    # ---- Astranaar: Thessaly Windrunner
    "ashenvale_refugees_belongings": dict(
        description="Thessaly Windrunner fled the east coast with almost nothing. The one thing she wants back is her family's locket, "
                    "taken by a nightsaber when her wagon was overturned on the Night Run.",
        accept_text="It's only silver. It's only a painted picture, really. But it's the only picture of my sister, "
                    "and a cat in the Night Run has had it since the wagon went over. I won't ask you to bring all of it back. Just the locket.",
        turn_in_text="Oh. It's dented. Of course it's dented. ... It's perfect, thank you. "
                     "I didn't think anyone would go looking for something so small."),
    "ashenvale_nightsaber_thinning": dict(
        description="The same nightsabers that carried off Thessaly's locket are still hunting the Night Run. "
                    "She wants seven of them gone before the next wagon tries it.",
        accept_text="I keep seeing the cats' eyes when I close mine. There'll be other families on that road. "
                    "Please, seven. I'll sleep better. I think a lot of people will.",
        turn_in_text="Seven. I'll tell the next wagon driver. He will pretend not to cry, and then he'll buy you a drink."),
    # ---- Splintertree Post
    "splintertree_burning_blade_scouts": dict(
        description="War Mage Grimtotem wants the Burning Blade cultist scouts working the edge of the Wastes cleared out, "
                    "so he can finish mapping where the ritual circles are going up.",
        accept_text="Cultists poke around the Wastes like rats in a cellar. I'll know where the circles are by what they guard. "
                    "Kill their scouts and the circles can't hide. Eight should do it.",
        turn_in_text="Eight. They guard more than I thought. I'll mark it on the map and show Vashj. "
                     "You have the hands for this. I hope you have the stomach, too."),
    "splintertree_charred_wolves": dict(
        description="Wolves from the burned stretch of forest have been hunting the outpost's livestock and its patrols. "
                    "Grunt Bloodfang wants the pack thinned, and wants whatever is making them burn-mad found.",
        accept_text="Used to be, a wolf ran from a fire. These come out of the burn like they're from it. "
                    "My patrols are bleeding for it. Nine of them. I won't make you count the teeth.",
        turn_in_text="Nine, and not a wolf among them behaved like a wolf. I owe you a drink and an apology to the dead ones. "
                     "Nothing in the world should look at fire and stay."),
    "splintertree_fel_imp_cache": dict(
        description="The imps of the Demon Wastes have been carrying off outpost scraps and hoarding them. "
                    "Grunt Bloodfang wants five scraps recovered. Whatever the imps are building with them, he wants it gone.",
        accept_text="Hinges. Buckles. A strip of my own mess-tent canvas. They carry off the dumbest things and stack them in the dirt. "
                    "I don't think it's a nest. I think it's a message nobody told us how to read.",
        turn_in_text="That's the hinge off my own tent flap. Right. The mess-tent has to stay up and the imps have to stay out. "
                     "Thank you. Don't tell Sergeant Krull it was imps. He'll ask me why we couldn't stop them."),
    "splintertree_satyr_ritual": dict(
        description="Interrogator Vashj has learned the satyrs at Satyr's Throne are preparing a ritual. "
                    "She wants the tricksters leading it cut down before it begins.",
        accept_text="The satyrs have been singing for three nights. That is not a song of welcome. "
                    "The tricksters lead it. Remove them, ten, and the chant has nothing to carry it.",
        turn_in_text="The chant has stopped. For tonight, anyway. You did well. "
                     "Whoever commands them will be furious. I'd like to meet him on my terms."),
    "splintertree_lord_malgan": dict(
        description="With the ritual broken, Lord Malgan holds Satyr's Throne by fear more than strength. "
                    "Vashj wants him removed before he can rally the satyrs for another try.",
        accept_text="A tyrant who loses a ritual has two choices: try again or die trying. I prefer to make the choice for him. "
                    "Malgan sits at the Throne. Go and take it away from him.",
        turn_in_text="The Throne is quiet. Good. Malgan's pelt on the wall would have been worth the walk. "
                     "His dagger will do. Take it, and don't let it hum you to sleep."),
    "splintertree_twilight_acolytes": dict(
        description="Twilight acolytes at the Barrow have been whispering to the buried dead at night. "
                    "War Mage Grimtotem wants nine of them silenced before the dead start answering.",
        accept_text="Something under the Barrow is listening, and the acolytes are the ones talking to it. "
                    "I don't know what's down there and I don't plan to find out by letting the conversation go on. Nine of them.",
        turn_in_text="Quiet. Good. I felt it go quiet from the walls. Whatever was down there has lost its mouthpieces, for now."),
    "splintertree_twilight_overseer": dict(
        description="The Twilight Overseer is the voice the acolytes were whispering for. "
                    "Grimtotem wants him ended before whatever is under the Barrow learns to speak for itself.",
        accept_text="Every cult has someone who is not a believer, only a boss. He is the overseer. "
                    "Kill him and the rest will scatter. Or they'll come for you, which is a better fight than what's waiting under them.",
        turn_in_text="I can feel the Barrow settling. Well done. Now we only have to worry about everything else."),
    "splintertree_pit_lord_emissary": dict(
        description="A pit lord's emissary has come to the Demon Wastes with demands. "
                    "Grimtotem has never wanted to hear them, and wants it dead before it finishes speaking.",
        accept_text="The emissary arrived with terms. I don't read the terms of things that stand in the fire. "
                    "Cut it off before it finishes a sentence.",
        turn_in_text="It was still talking when you reached it? Of course. They always are. "
                     "I'll burn what's left of the terms. Thank you."),
}
# chains: quest_id -> next_quest_id
CHAIN = {
    "ashenvale_sentinel_scouts_report": "ashenvale_furbolg_ravagers",
    "ashenvale_furbolg_ravagers": "ashenvale_furbolg_shaman_totems",
    "ashenvale_furbolg_shaman_totems": "ashenvale_ursal_the_mauler",      # hands off to Maestra
    "ashenvale_wisp_lights": "ashenvale_dryads_gone_quiet",
    "ashenvale_dryads_gone_quiet": "ashenvale_keeper_rustveil",
    "ashenvale_refugees_belongings": "ashenvale_nightsaber_thinning",
    "splintertree_satyr_ritual": "splintertree_lord_malgan",
    "splintertree_twilight_acolytes": "splintertree_twilight_overseer",
    "ashenvale_night_run_watch": "ashenvale_wraith_toll",
    "zoram_murloc_nets": "zoram_crab_traps",
    "zoram_naga_coastguard": "zoram_tidecaller_pearls",
    "splintertree_demon_wastes_watch": "splintertree_voidwalkers",
    "lumber_felling_season": "lumber_elder_stump",
    "raynewood_cats": "raynewood_vigil_lights",
    "raynewood_vigil_lights": "raynewood_dryads",
}

# ===================================================================== 2. NEW QUESTS
NEW = []


def item(name, slot, ilvl, flavor, stats, rarity="uncommon", armor_type=None, weapon_type=None):
    d = {"name": name, "slot": slot, "item_level": ilvl, "rarity": rarity, "flavor_text": flavor, "primary_stats": stats}
    if armor_type:
        d["armor_type"] = armor_type
    if weapon_type:
        d["weapon_type"] = weapon_type
    return d


def Q(qid, title, giver, zone, lo, hi, desc, objectives, accept, turn_in, items=(), mult=1.0, boss=False):
    q = {"quest_id": qid, "title": title, "giver_npc_id": giver, "zone": zone, "level_min": lo, "level_max": hi,
         "description": desc, "objectives": objectives,
         "reward_exp": int(round(_base(_XP, lo, 100) * mult / 50.0) * 50),
         "reward_gold": int(round(_base(_GOLD, lo, 270) * mult / 100.0) * 100),
         "accept_text": accept, "turn_in_text": turn_in}
    if items:
        ilvl = hi if boss else max(lo, hi - 1)
        q["gear_reward_gear_level"] = ilvl
        q["unique_item_defs"] = [dict(i, item_level=ilvl) for i in items]
    NEW.append(q)


def kill(t, n, zone):
    return {"type": "kill", "target": t, "count": n, "zone": zone}


def boss(t, zone):
    return {"type": "kill_boss", "target": t, "count": 1, "zone": zone}


def fetch(t, n):
    return {"type": "fetch", "target": t, "count": n}


def explore(zone):
    return {"type": "explore", "target": None, "zone": zone}


# ---------------------------------------------------------------- WEST: Maestra's Post
Q("ashenvale_lake_naiads", "Troubled Water", "maestras_post_sentinel", "ashenvale_west", 23, 25,
  "The lake naiads of Elune'ara have turned on the Sentinels' fishing parties. Maestra wants seven of them calmed, by the only means they respect.",
  [kill("Lake Naiad", 5, WEST)],
  "They've always sung to us from the water. Lately they sing and drag. I won't say the lake is a danger, Elune help me, "
  "but I'll say seven of its daughters are. Settle them.",
  "Seven, and the water calmed. I never thought I'd be grateful to see a naiad go quiet. Remind me to pour one out for them.")
Q("ashenvale_night_run_watch", "Eyes on the Night Run", "maestras_post_sentinel", "ashenvale_west", 22, 24,
  "The Night Run is where the wagons die. Maestra wants someone to walk it end to end and report what they see.",
  [explore("The Night Run")],
  "Eltharaen keeps asking me what's on the Run and I keep telling him I don't know. I'm tired of not knowing. "
  "Walk it. All of it. Tell me what the road looks like to someone who isn't afraid of it.",
  "Wraith-light on the old tree line, you say? Then it's worse than the cats. I'll send for Eltharaen. And I'll find you more work.")
Q("ashenvale_wraith_toll", "The Wraith's Toll", "maestras_post_sentinel", "ashenvale_west", 24, 26,
  "The Night Run's wraiths take a toll from every passing wagon. Maestra wants eight of them ended, and the road reopened.",
  [kill("Ashenvale Wraith", 6, WEST)],
  "The dead of the Run don't want revenge. They want company. Eight of them in the ground and the rest might remember they were people.",
  "The road is open, and we owe it to a stranger. The Sentinels will remember that, even if we say it badly.",
  items=[item("Maestra's Wardstitch Belt", "waist", 25, "She stitched the ward-sigils herself, and she did not do it gently.",
              {"agility": 5, "stamina": 3}, armor_type="leather")])
# ---------------------------------------------------------------- WEST: Astranaar
Q("ashenvale_commander_spiders", "Webs on the Trade Road", "astranaar_sentinel_commander", "astranaar", 22, 24,
  "Sentinel Eltharaen is losing supply wagons to forest spiders along the trade road. He distrusts asking the Horde for help, but he is not a fool.",
  [kill("Forest Spider", 7, WEST)],
  "I do not enjoy asking this of you. My people are stretched, and you are here, and the spiders do not care whose wagons they take. "
  "Nine, from the road. I will remember that it was asked and answered.",
  "Nine. The road is clear. I will say this plainly: I did not expect to thank a Horde blade today. I find that I do.")
Q("ashenvale_dryads_gone_quiet", "A Quiet Grove", "astranaar_grove_warden", "astranaar", 24, 26,
  "The dryad sentinels of the Moonwhisper Grove have stopped answering Pennarin's calls. Whatever has them is not letting them go. She asks that six be released.",
  [kill("Dryad Sentinel", 5, WEST)],
  "The dryads answer when I sing. They have not answered in a week. I think the grove's corruption is in them now, and it will not leave "
  "unless it is made to. I am sorry to ask for six of them.",
  "The grove is a little less loud. I hope they're at peace. I hope the grove forgives me. Rustveil is next, I'm afraid.")
Q("ashenvale_lake_survey", "Marks on the Water", "astranaar_moon_guard", "astranaar", 22, 24,
  "Moon Guard Talonar Swiftmoon keeps a ledger of the lake's moods. He wants someone to walk the shoreline of Elune'ara and confirm what he's already seen from the wall.",
  [explore("Lake Elune'ara")],
  "I have counted the ripples from the tower for eleven nights. They do not follow the wind. I would like a second pair of eyes on the shore. "
  "Preferably ones that aren't mine, because I've started to doubt them.",
  "As I thought. Thank you for confirming what I'd begun to fear. I'll tell Maestra, and I'll sleep.")
# ---------------------------------------------------------------- WEST: Zoram Strand
Q("zoram_murloc_nets", "Nets Full of Teeth", "zoram_fisher", "zoram_strand", 24, 26,
  "Old Maelis' nets come up shredded, and the culprits are the murloc spearfishers working the coast. He wants ten of them dealt with.",
  [kill("Murloc Spearfisher", 8, WEST)],
  "Forty years I've fished this strand and the murlocs never touched a line. Now they cut my nets with bone knives. "
  "Ten of them, and I'll tell you the story of the big silverfin. It's a very good story.",
  "Ten! My boy, my nets will live. Now sit, sit, about the silverfin. It was longer than a dock and it winked.")
Q("zoram_crab_traps", "Cracked Traps", "zoram_fisher", "zoram_strand", 25, 27,
  "The big shore crabs have been crushing Maelis' traps against the rocks. He wants eight of them gone before he has to give up crab for good.",
  [kill("Tide-Wrecker Crab", 6, WEST)],
  "The crabs got bold when the naga started wandering the shallows. Nothing's afraid of old Maelis anymore. "
  "Eight of the big ones, and I'll be able to eat dinner like a free man.",
  "Eight. I can already smell the pot. You've done an old man a kindness, and kindness is rare on this coast.")
Q("zoram_naga_coastguard", "Splinters", "zoram_boatwright", "zoram_strand", 25, 27,
  "Boatwright Illyen has lost three boats this month to naga raiders. She wants eight coastguards driven back before she finishes the fourth.",
  [kill("Naga Coastguard", 6, WEST)],
  "I build a boat in a week and they sink it in a night. I'm not asking you to be brave, I'm asking you to be efficient. Eight of them.",
  "Eight. Hm. I'll build the fourth boat a little faster. You'll forgive me if I name it after you, I name them all after people who've been useful.")
Q("zoram_tidecaller_pearls", "Pearls of the Tide", "zoram_boatwright", "zoram_strand", 26, 28,
  "The naga tidecallers wear pearls that seem to summon the surf. Illyen wants five of them, so she can learn what they're made of.",
  [fetch("tidecaller_pearl", 5)],
  "The tidecallers don't carry weapons. They carry pearls, and the water answers them. Bring me five and I'll find out why a pearl should be able to do that.",
  "These are not pearls. Nothing pearl-like should hum. I'm going to find out what they are, and I'm going to be very quiet about it.",
  items=[item("Illyen's Tarred Gloves", "hands", 27, "Tarred against the water. Tarred against everything, really.",
              {"stamina": 5, "strength": 4}, armor_type="mail")])
Q("zoram_lookout_bluffs", "The Long Watch", "zoram_sentinel", "zoram_strand", 24, 26,
  "Lookout Taelanor watches the water so the others can sleep. She hasn't slept in days. She wants someone to walk the Coast Bluffs and tell her what the water isn't telling her.",
  [explore("Coast Bluffs")],
  "I watch the water and the water watches back. I can't see the bluffs from here, and I think that's where the problem is. "
  "Go there. Tell me it's nothing, and let me sleep.",
  "It isn't nothing. I'm grateful you told me anyway. Sit a while. The water will keep.")
# ---------------------------------------------------------------- EAST: Splintertree Post
Q("splintertree_timber_quota", "The Quota", "splintertree_commander", "splintertree_post", 20, 22,
  "Overseer Gorada has a lumber quota, a post to feed and grizzlies eating the loggers. He wants eight of the biggest bears dealt with.",
  [kill("Ashenvale Grizzly", 6, EAST)],
  "Orgrimmar wants timber and I want my loggers alive. The bears have decided otherwise. Eight of them. "
  "I'm told the Warchief is very reasonable about this sort of thing, which is why I'm not asking him.",
  "Eight, and the quota's back on track. You're hired. Not formally. I don't do paperwork, but I'll remember your name.")
Q("splintertree_blood_orders", "Orders in Blood", "splintertree_scout", "splintertree_post", 20, 22,
  "Scout Veyra suspects the Burning Blade cultists in the Wastes carry written orders. She wants five of them lifted before the ink dries.",
  [fetch("burning_blade_orders", 5)],
  "Cultists carry orders. Cultists never carry anything they can't hide behind a knife. Bring me five scraps and I'll know who is giving them.",
  "Hm. Written in blood, signed in ash. Whoever's behind this wants to be found, eventually. I'd rather be ready.")
Q("splintertree_wraiths", "Wraiths in the Timber", "splintertree_barracks_sergeant", "splintertree_post", 22, 24,
  "Sergeant Krull is tired of burying scouts. The wraiths haunting the timber east of the post have to be ended.",
  [kill("Ashenvale Wraith", 5, EAST)],
  "I've buried four recruits this week, and they were four that I trained! There are wraiths in the timber and I want them back in the dirt. "
  "Seven. DON'T TELL ME THEY'RE ALREADY DEAD.",
  "Seven? SEVEN. I can't say good job in front of the recruits so I'll say it here. Good job.")
Q("splintertree_demon_wastes_watch", "Eyes on the Wastes", "splintertree_watch_sentry", "splintertree_post", 22, 24,
  "Watch Sentry Mokka can see smoke from the Demon Wastes, but not what makes it. He wants someone to walk its edge and report.",
  [explore("The Demon Wastes")],
  "From the wall, I see smoke. From the ground, you see who lit it. Walk the Wastes and tell me. I'll keep the wall warm.",
  "Hm. Smoke without a fire, you say? Some things burn the other way. I'll tell Gorada. He'll curse a lot.")
Q("splintertree_voidwalkers", "Remnants", "splintertree_watch_sentry", "splintertree_post", 24, 25,
  "Voidwalker remnants drift through the Wastes at night. Mokka wants six of them dispersed before they find the wall.",
  [kill("Voidwalker Remnant", 5, EAST)],
  "They're not alive, and not dead, and not made for the world. Six of them, before they find how thin the wall is.",
  "Six. The wall is quiet. I'll sleep tonight, which is more than I can say for the Wastes.",
  items=[item("Mokka's Watchcord", "neck", 24, "Knotted for every night that nothing came over the wall.",
              {"agility": 4, "stamina": 3})])
# ---------------------------------------------------------------- EAST: Warsong Lumber Camp (new NPC Foreman Gruzak)
Q("lumber_felling_season", "Felling Season", "warsong_foreman", "ashenvale_east", 20, 23,
  "Foreman Gruzak's crews can't fell a tree without a timberling guarding it. He wants eight of them cleared from the stand east of the camp.",
  [kill("Timberling", 6, EAST)],
  "A good tree dies in four swings. These walkers take it back with a root in the ear. Clear eight so my boys can work, and don't leave any standing.",
  "Eight. I owe you a few logs' worth of thanks. Take your pick of the leftover axes. They're not good, but they're mine.")
Q("lumber_elder_stump", "The Elder Stump", "warsong_foreman", "ashenvale_east", 23, 25,
  "An elder timberling the size of a house guards the last good stand. Gruzak wants it felled, and says the camp will drink to it.",
  [boss("Elder Timberling", EAST)],
  "There's a stump out there that walks. It's the oldest thing in the forest. I've cut forty years of trees and I've never wanted one gone so badly. Fell it.",
  "It fell? It FELL! Hah! The whole camp will hear about this. Take the sap, it's good for something, I'm sure.",
  items=[item("Gruzak's Splitting Maul", "main_hand", 24, "Heavy as a stump and smells like one.",
              {"strength": 6, "stamina": 3}, weapon_type="mace_2h")], boss=True)
Q("lumber_silk_slings", "Silk for the Slings", "warsong_foreman", "ashenvale_east", 21, 23,
  "Gruzak wants spider silk to weave log-slings stronger than rope. Six bundles from the forest spiders will do.",
  [fetch("forest_spider_silk", 6)],
  "Rope breaks. Silk doesn't. The spiders are bigger than they ought to be, and so is their silk. Six bundles, and I'll lift a whole oak.",
  "Six, and clean. Look at that, it doesn't even stretch. I'll make you a sling of your own. For a bear. Or a friend you hate.")
# ---------------------------------------------------------------- EAST: Raynewood Retreat (new NPC Warden Aelyndra)
Q("raynewood_cats", "Cats at the Door", "raynewood_warden", "ashenvale_east", 21, 24,
  "Warden Aelyndra keeps the quiet at Raynewood Retreat, and the nightsabers have stopped respecting it. She wants seven driven off.",
  [kill("Nightsaber Stalker", 5, EAST)],
  "I do not generally welcome strangers, and I certainly do not generally welcome the Horde. But the cats don't distinguish. "
  "Seven of them, and the retreat can go back to being quiet.",
  "Seven. The retreat is quiet. I will say a thing I haven't said to a stranger in years: thank you.")
Q("raynewood_vigil_lights", "Vigil Lights", "raynewood_warden", "ashenvale_east", 21, 23,
  "Raynewood keeps a vigil for those lost to the corruption, lit with wisp-light. Aelyndra needs six more motes for the next night.",
  [fetch("wisp_light_essence", 6)],
  "We light a vigil for the ones the forest lost. The wisps give the light freely, if you ask them. Ask. Six, please.",
  "Six. That will see us through the new moon. Walk carefully out there. I'd rather not add you to the vigil.")
Q("raynewood_dryads", "The Dryads Sleep", "raynewood_warden", "ashenvale_east", 22, 24,
  "The dryads of Raynewood have gone to sleep and wake angry. Aelyndra asks that five be put to rest rather than left to suffer.",
  [kill("Dryad Sentinel", 4, EAST)],
  "They sleep, and what wakes in them is not them. I'd do it myself if my hands were what they used to be. Five. Quickly, please.",
  "I will light a candle for each. Thank you for doing what I could not. It will be remembered at Raynewood.",
  items=[item("Aelyndra's Vigil Wrap", "wrist", 23, "Woven for a night that never ends, and carried through it.",
              {"intellect": 4, "spirit": 3}, armor_type="cloth")])

# ===================================================================== 3. NPCs + QUEST DROPS
NEW_NPCS = [
    {"npc_id": "warsong_foreman", "name": "Foreman Gruzak", "zone": "ashenvale_east", "x": 45, "y": 52,
     "greeting": "Axes up, you lot! ... Oh. You're not one of mine. Well, don't just stand there, there's wood to cut.",
     "race": "orc", "gender": "male", "appearance_variant": 5, "facing": "down"},
    {"npc_id": "raynewood_warden", "name": "Warden Aelyndra", "zone": "ashenvale_east", "x": 32, "y": 150,
     "greeting": "Quiet, please. This is a place for grief, and you are not the first to bring noise.",
     "race": "night_elf", "gender": "female", "appearance_variant": 6, "facing": "down"},
]


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


DROPS = {
    "Burning Blade Cultist": [qd("burning_blade_orders", "Blood-Written Orders",
                                 "A scrap of hide with a few lines of crabbed script, written in something that is not ink. The lines don't agree with each other.", 0.4)],
    "Forest Spider": [qd("forest_spider_silk", "Heavy Spider Silk",
                         "A skein of silk as thick as a bowstring, tacky and strong. It would hold a grown bear.", 0.45)],
    "Naga Tidecaller": [qd("tidecaller_pearl", "Hummingtide Pearl",
                           "A grey-green pearl that hums when you stop looking at it. The air around it smells like low tide.", 0.5)],
    "Murloc Hydra": [qd("hydra_fang", "Hydra Fang",
                        "A curved fang as long as your hand, still wet. Whatever it bit had it twice.", 0.4)],
}


def main():
    data = json.loads(QP.read_text(encoding="utf-8"))
    qs = {q["quest_id"]: q for q in data["quests"]}
    for qid, rw in REWRITE.items():
        qs[qid].update(rw)
    for q in NEW:
        qs[q["quest_id"]] = q
    for qid, nxt in CHAIN.items():
        qs[qid]["next_quest_id"] = nxt
    order = [q["quest_id"] for q in data["quests"]] + [q["quest_id"] for q in NEW if q["quest_id"] not in {x["quest_id"] for x in data["quests"]}]
    data["quests"] = [qs[i] for i in dict.fromkeys(order)]
    QP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # NPCs
    NP = ROOT / "data/npcs/ambient_npcs.json"
    nd = json.loads(NP.read_text(encoding="utf-8"))
    have = {n["npc_id"] for n in nd["npcs"]}
    for n in NEW_NPCS:
        if n["npc_id"] not in have:
            nd["npcs"].append(n)
    NP.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # drops
    DP = ROOT / "data/creatures/quest_drops.json"
    dd = json.loads(DP.read_text(encoding="utf-8"))
    for creature, drops in DROPS.items():
        ids = {x["item_id"] for x in drops}
        dd["drops"][creature] = [x for x in dd["drops"].get(creature, []) if x["item_id"] not in ids] + drops
    DP.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(data['quests'])} Ashenvale open-world quests ({len(NEW)} new)")


if __name__ == "__main__":
    main()
