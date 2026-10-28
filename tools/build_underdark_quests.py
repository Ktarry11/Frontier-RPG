"""
Crystalline Underdark quest pass.  Idempotent.

    PYTHONPATH=. python3 tools/build_underdark_quests.py

Writes data/quests/underdark.json (Underdark 22, Kael's Bastion 9) and data/quests/underdark_dungeons.json
(Frostward Descent 6, Hollow Geode 6, Deep Bloom 7), adds the fetch and starter drops to
data/creatures/quest_drops.json, and splices the inbound bridge quests into their own zones' files.

NO ESCORTS (Kyle's standing rule, and the only hard "never" in the quest design).
NO QUESTS BUILT AROUND RARES - the six named rares here are lore and loot, never an objective.

THE ZONE'S ONE IDEA, AND EVERY QUEST SERVES IT. Everywhere else in Frontier the NPCs have always been here
and the player is the transplant. Not in the Underdark. The Crimson Codex came down a fissure three years
ago, the same three years the player has existed on this world, and the cavern itself is three years old.
Nobody has a prior claim. That makes the usual distrust run SIDEWAYS: a Codex archivist does not look down
on an Earth transplant for being new, she looks at a rival claimant who arrived the same year she did, and
gets a degree colder. Five of these fifty quests touch it. It is never the default tone.

The Codex catalogue compulsively because a thing properly written down is a thing owned, and their index
has started producing columns they cannot fill. That is the running thread, and it ends at the Deep Bloom,
where something has grown into the shape of a library and begun reading them back.

USES THE WHOLE TOOLKIT:
  craft        the Codex are two hundred spans underground and OUT OF PAPER; the only wood in the cluster
               is the frostpine in the Descent's ice chambers (ww_pages_frostpine). The Shardfields smelt
               their own silver. The alchemist wants arcane fury brewed from reagents that test better
               down here than they have any right to.
  deliver      the Archive's sealed find walks from the dig to the Codex Hall, hand-in on another NPC.
  starter      four quests begin as loot: a frozen survey page off the expedition that never came back,
               a catalogue slip with a number the Codex has not issued yet, a page that was GROWN rather
               than written, and a Syndicate route card found up in Hillsbrad.
  requires     db_what_it_learned - the Codex-Master's own order to end the thing in the Bloom - opens only
               after ud_colonnade_dalaran (the open zone), hg_prism (the Hollow Geode) and hbe_fissure_north
               (Eastern Hillsbrad). Three maps across two regions; skip any one and she never offers it,
               which is the Linken's Sword pattern Kyle asked for.
  inbound      four quests in other zones now point here.

LEVEL BAND. The cluster bridges Hillsbrad (ends 31) to the 40s: Descent 31-34, Underdark 33-37,
Bastion 33-38, Hollow Geode 34-38, Deep Bloom 36-40.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/underdark.json"
OUT_D = ROOT / "data/quests/underdark_dungeons.json"

UD, KB = "the_crystalline_underdark", "kaels_bastion"
FD, HG, DB = "the_frostward_descent", "the_hollow_geode", "the_deep_bloom"
HBE = "eastern_hillsbrad"

XP = {30: 2120, 31: 2200, 32: 2290, 33: 2380, 34: 2470, 35: 2560, 36: 2650, 37: 2740,
      38: 2830, 39: 2920, 40: 3010}
GOLD = {30: 8700, 31: 9000, 32: 9300, 33: 9600, 34: 9900, 35: 10200, 36: 10500, 37: 10800,
        38: 11100, 39: 11400, 40: 11700}

# The cluster's gear flavour. Ice at the top, arcane crystal and fungus below, and Dalaran stone in places
# nobody carried it to.
tirisfal_gear.THEMES.update({
    "frostward": (["Frostward", "Rime-Shelled", "Glacier-Cut", "Upper Dark", "Hoarfrost"],
                  ["Cold the way old ice is cold, which is patient.", "Frost in the seams that never leaves.",
                   "Carried down past the last daylight.", "The ice gave it up. It did not want to."]),
    "expedition": (["Expedition", "Surveyor's", "Forty-Year", "Last Camp", "Unfinished"],
                   ["Alterac make, and forty years behind the fashion.", "Somebody packed this to come back.",
                    "The last entry in the log is mid-sentence.", "Still buckled the way he buckled it."]),
    "lattice": (["Lattice", "Repeating", "Exact", "Figure-Cut", "Iterated"],
                ["The pattern repeats every eleven inches, without exception.",
                 "Grown in rows. Nothing alive bothers to do that.",
                 "Cut to a figure that closes perfectly.", "There are others. They are identical."]),
    "sporefall": (["Sporefall", "Cap-Cut", "Spore-Lit", "Mycelial", "Drifting"],
                  ["Smells of warm earth two hundred spans from any.", "Cut from a cap you could shelter under.",
                   "Glows faintly, which down here is no distinction.", "Light, and stronger than it looks."]),
    "lumen": (["Lumen", "Drowned-Light", "Marsh-Lit", "Tide-of-Glass", "Underlit"],
              ["Lit from underneath, like everything in that water.", "Never dry and never quite wet.",
               "It brightens and dims. On a cycle. With the Lumen.", "Cold light, and no heat in it at all."]),
    "colonnade": (["Colonnade", "Dalaran", "Weeping", "Carried-Down", "Violet-Stone"],
                  ["Dalaran work, two hundred spans below Dalaran.", "Nobody carried this down here.",
                   "The violet is in the stone, not on it.", "It was made somewhere with a sky."]),
    "archive": (["Archive", "Sunken", "Unlisted", "Catalogued", "Greyquill"],
                ["Filed, numbered, and then filed again.", "The catalogue number is not one the Codex issues.",
                 "Dug out of the Archive and signed for twice.", "Somebody wanted this forgotten."]),
    "codex": (["Codex", "Crimson", "Bastion-Cut", "Kael's", "Indexed"],
              ["Crimson Codex issue, and they count every piece.", "Carried down a fissure on somebody's back.",
               "Blood elf work, under a ceiling instead of a sky.", "Stamped, entered, and never once used."]),
    "dim": (["Dim", "Unlit", "Lightless", "Lumen-Forsaken", "Unseen"],
            ["The Lumen does not land on it. It simply does not.", "Taken off something nobody has described.",
             "Cold, and it does not warm in the hand.", "Out past where anyone maps."]),
    "riftward": (["Riftward", "Half-Written", "Unspecified", "Still-Forming", "Draft"],
                 ["The edge is specified. The rest is not.", "Geometry that does not close.",
                  "It has been made more than once.", "Not finished, and not waiting to be."]),
    "geode": (["Geode", "Druse", "Inward-Pointing", "Cavity", "Shell-Grown"],
              ["Grown inward, the way the whole place grows.", "Prised out of the only gap that was left.",
               "The crystal has very nearly finished with this.", "Still faintly growing, which is fine."]),
    "bloom": (["Bloom", "Shelf-Grown", "Fruiting", "Copied", "Misremembered"],
              ["Grown in the shape of a thing it had never seen.", "Almost right, in a way that is worse.",
               "Warm, and it should not be.", "It has your shape already."]),
})


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x, y, radius=6):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def craft(recipe, label, n=1):
    return dict(type="craft", target=recipe, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None,
       **engine):
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


# WRITING STANDARD (Kyle): no "kill X of Y down by the Z, # of them if you will". The accept line is a
# PERSON TALKING and the numbers live inside what they say. Every quest carries a piece of why this place
# is what it is - it manifested, it is three years old, the Codex are indexing something that has begun
# indexing back, and Dalaran stone is down here that nobody carried.

# =========================================================================================================
# THE FROSTWARD DESCENT - 31-34. Ice, then a seam, then the first thing that is not from this world.
# =========================================================================================================
WATCH, SURV = "ud_dawn_watch", "ud_dawn_cartographer"
NESS, ILAR, VESS = "kb_archivist", "kb_codex_master", "kb_gate_warden"


def descent():
    A = []
    A.append(Q("fd_long_way_down", "The Long Way Down", "hbe_naze_infiltrator", FD, 31, 32, "frostward",
        "The fissure above Gavin's Naze was not in any survey of the Alterac foothills, and the Alterac "
        "foothills have been surveyed by three kingdoms. It opened three years ago, when a great many things "
        "opened. Blood elves have been using it as a road ever since, and nobody on the Hillsbrad side has "
        "gone down far enough to find out where it goes.",
        [explore(FD, 60, 110, 8)],
        "Down, and keep going down. The ice holds for the first stretch - old ice, Alterac ice, nothing "
        "stranger than cold.\n\nAfter that it stops being ice and I cannot tell you what it becomes, because "
        "the two men I sent came back without agreeing. Get past the frozen watercourse and see the seam for "
        "yourself. That is all I am asking for, and it is more than I have.",
        "Wet black rock and light in the walls. Both of them said that. Neither of them said it was a "
        "road.\n\nIt is a road. Somebody walks it, often, and they are not walking up."))
    A.append(Q("fd_yeti_marrow", "Something That Does Not Freeze", SURV, FD, 31, 33, "frostward",
        "Surveyor Aelwyn maps the Underdark's far wall from the only place there is to stand, and she is not "
        "a physician. She still noticed that the yeti in the upper chambers do not go stiff. Forty years of "
        "Alterac winter in those galleries and the things living in them stay warm, and the Codex's position "
        "is that this is uninteresting.",
        [fetch("rimed_marrow", 7)],
        "Seven draws of marrow from the hoarfrost yeti in the upper galleries. They are easier to find than "
        "to leave.\n\nI want them cold. Pack them in ice from the chamber you take them in - if they are warm "
        "when they reach me I learn nothing, and I will have sent you up there for a story.",
        "Still warm. All seven, and the ice around them had started to go.\n\nSomething in those galleries is "
        "feeding heat to the things that live there, and it is not the sun, because there has not been one "
        "over that rock in three years."))
    A.append(Q("fd_frozen_page", "A Page From the Last Camp", "item:frozen_survey_page", FD, 32, 33,
        "expedition",
        "You pull a page out of the ice, and the ice gives it up cleanly, the way ice does when a thing has "
        "been in it a long time without ever settling. The hand is Alteraci and the date is forty-one years "
        "old. It reads: THE READINGS ARE WRONG AND I AM GOING ON. Below that, in the same hand but smaller: "
        "there is no bottom to this and I have stopped telling the others.",
        [fetch("expedition_fitting", 8)],
        "There was a camp down here before the Codex, before the fissure was supposed to exist at all, and "
        "it did not come back up.\n\nWork the seam and pull their fittings out of the walkers - buckles, "
        "straps, lamp-brackets, eight pieces, enough that nobody can call it one man's bad luck. Somebody "
        "at the Bastion will want to know their own road was walked forty years before they found it.",
        "Alterac, all eight, and every one still done up. Nobody undid a buckle.\n\nForty-one years and they "
        "were still surveying when the cold caught them. I have been mapping this cavern for three and I "
        "would like it on the record that I find that less comforting than I did this morning.",
        turn_in_npc_id=SURV))
    A.append(Q("fd_hoarfang", "Hoarfang", WATCH, FD, 32, 33, "frostward",
        "Kaelen Mornstride has watched the passage mouth for three years and knows exactly how long the walk "
        "from the Hillsbrad side takes. For two months it has taken longer, and the people who make it arrive "
        "short of someone. The upper galleries have acquired a resident.",
        [boss("Hoarfang", FD)],
        "Something is holding the ice chambers against us, and it is doing it well enough that I have started "
        "sending people up in threes.\n\nThe porters call it Hoarfang. It takes the back of a column, in the "
        "narrow stretch above the frozen watercourse, and it does not stay to fight. Go up and make it stay.",
        "Three years I have stood at this mouth and counted people in. I would like to go back to counting "
        "the same number out."))
    A.append(Q("fd_cartographer", "He Is Still Surveying", SURV, FD, 33, 33, "expedition",
        "The fittings came back Alterac. Aelwyn has been mapping this cavern for three years with instruments "
        "the Codex carried down on their backs, and the thought that someone was doing the same work here "
        "forty-one years ago, and is in some sense still doing it, has stopped her sleeping.",
        [boss("The Frozen Cartographer", FD)],
        "He is at the seam, where the ice stops. He has a rod and a board and he takes a reading off everything "
        "that comes near him, including people.\n\nI am not sending you to put a man out of his misery - I "
        "have no evidence he is in any. I want his board. Whatever he has been drawing for forty-one years, "
        "the Codex does not have a copy and I would like to be the one who does.",
        "It is a map. It is a map of a cavern that did not exist when he started drawing it.\n\nI am going to "
        "sit with this for a while, and then I am going to decide whether to file it."))
    A.append(Q("fd_latticeborn", "The First Exact Thing", WATCH, FD, 33, 34, "lattice",
        "Past the seam the rock starts growing in figures - precise repeating lattices, the same shape at "
        "every scale, with a tolerance no mineral has any business holding. The Codex's standing instruction "
        "is to record it as unusual mineralisation. Everybody who has actually stood in front of it records "
        "it as something else in private.",
        [boss("Latticeborn", FD)],
        "The lower chambers have grown a warden. It does not patrol, it does not hunt, it simply stands in "
        "the passage and will not be gone around.\n\nWatch what it does before you close - it strikes twice, "
        "identically, every time, and the second one is not a second attempt. It is the same event happening "
        "again. If you understand why that frightens me you will do better in there than most.",
        "Twice, exactly. You saw it too.\n\nThree years I have told new arrivals that the crystal is just "
        "crystal. I am going to keep telling them. It gets them down the passage."))
    return A


# =========================================================================================================
# THE CRYSTALLINE UNDERDARK - 33-37. A roofed country, and an index that has stopped working.
# =========================================================================================================
HARV, PELO, IMRE = "ud_shard_harvester", "ud_lattice_surveyor", "ud_marsh_naturalist"
VERI, THAL, SARE = "ud_colonnade_scholar", "ud_archive_overseer", "ud_archive_digger"
RHEN, YSOL, MIKA = "ud_dim_scout", "ud_bloom_warden", "ud_sporefall_forager"
THRE = "ud_geode_campkeeper"


def underdark():
    A = []
    # ---- The Hollow Dawn
    A.append(Q("ud_first_sight", "No Ceiling Worth the Name", WATCH, UD, 33, 34, "codex",
        "The passage lets out on a shelf, and from the shelf you can see a cavern with weather in it. There is "
        "a light hanging over the middle of it that nobody has reached, mushrooms standing like trees, and a "
        "far wall at a distance that the eye reports as a horizon. Three years of Codex surveying has not "
        "produced an agreed figure for how big it is.",
        [explore(UD, 86, 26, 9)],
        "Walk out to the edge of the shelf and look at it properly. That is the whole task and I will not "
        "pretend otherwise.\n\nEveryone who comes down that passage expects a cave. What they get is a "
        "country with a lid on it, and the adjustment takes a few minutes. Have yours here, where the ground "
        "is flat, rather than halfway down the slope with something chewing on you.",
        "There it is.\n\nThe Codex has eleven thousand entries and not one of them is any use to a person "
        "standing where you just stood. Go down. Kaelen's advice: pick the light and walk at it, and you "
        "will not get lost in here."))
    A.append(Q("ud_dawn_skitterers", "Underfoot", SURV, UD, 33, 34, "lattice",
        "Aelwyn's instruments are brass, glass and patience, and they are two hundred spans from the nearest "
        "replacement. The crystalbacks on the Dawn shelf have worked out that a surveyor's tripod is a good "
        "place to shelter and a better place to chew.",
        [k("Crystalback Skitterer", 10, UD)],
        "Ten of them off the shelf. I have lost two sighting glasses this month and the Codex's position is "
        "that I should be more careful with Codex property.\n\nThey are not aggressive so much as curious, "
        "which makes no difference to the glass. Work the scree at the shelf edge - that is where they nest, "
        "and they do not go far from it.",
        "Quieter. I can hear my own chronometer again, which matters more than it sounds: I am timing the "
        "Lumen, and I have been doing it for three years, and it has not drifted by a minute."))
    # ---- The Sporefall
    A.append(Q("ud_sporefall_caps", "The Safe Ones Look Worse", MIKA, UD, 33, 35, "sporefall",
        "Forager Mikael is Forsaken, which in the Sporefall is a qualification: he has eaten his way through "
        "the mushroom forest in the only order that made sense, worst-looking first, and taken notes. The "
        "Codex pay him for the notes and pretend not to know the methodology.",
        [fetch("sporeback_cap", 10)],
        "Ten caps off the grazers out in the forest proper, not the little ones at the rim. The rim stock is "
        "stunted and the Codex's cooks can taste the difference, which I resent.\n\nThe ones that look like "
        "faces are fine, incidentally. Everybody asks. The stalks will put you on the floor for a day, so "
        "leave the stalks.",
        "Ten, and two of them good enough to argue about.\n\nYou are not from here either, are you. Nor am I, "
        "in the sense that matters. Everyone in this cavern walked in, which is the only thing I like about it."))
    A.append(Q("ud_sporefall_drifters", "The Forest Objects", MIKA, UD, 34, 35, "sporefall",
        "Spore-drifters move in loose clouds between the great caps and are mostly a nuisance. For six weeks "
        "they have been moving in the same directions at the same hours, and the hours line up with the "
        "Lumen's cycle. Mikael has mentioned this to the Codex twice.",
        [k("Spore-Drifter", 12, UD)],
        "Twelve, and thin them out along the paths between the big caps - that is where they drift and that "
        "is where the foragers walk.\n\nMind the ones that are already clustered. They share something "
        "between them, and the second you start on one the rest of the cloud is stronger for it. Break them "
        "up before they can close ranks, or you will fight the whole grove at once.",
        "You noticed the clustering, then. Everybody notices once something has used it on them.\n\nThat is "
        "not swarm behaviour. Swarms do not get STRONGER when you thin them. Something is feeding them "
        "instructions and I have stopped saying so out loud."))
    # ---- The Shardfields
    A.append(Q("ud_shard_crates", "Counted Twice", HARV, UD, 34, 35, "lattice",
        "The Shardfields are a broken crystal plain and the Codex's only reliable export. Delvin Brightsunder "
        "has worked them for three years, and every crate is weighed at the field and weighed again at the "
        "Bastion, because the two figures stopped matching about a year ago and nobody can find the gap.",
        [fetch("shard_core", 12)],
        "Twelve cores, and take them out of the lattice sentries rather than off the ground. Ground stock is "
        "half shell and the Reagent-Keeper sends it back with a note.\n\nThe sentries will let you walk out "
        "there. They object when you start cutting. There is no way to do this politely and I have stopped "
        "looking for one.",
        "Twelve, weighed, and I will weigh them again at the gate.\n\nIf they come out lighter up there, "
        "it is not you. It has been happening for a year and the Codex's explanation is the scales."))
    A.append(Q("ud_silver_bars", "What the Field Owes the Forge", HARV, UD, 34, 36, "codex",
        "Harvald Emberlock has no coal worth the name and burns what the Codex rules expendable, which the "
        "Codex rules often and reluctantly. The Shardfields sit on silver, the Bastion needs bar stock, and "
        "the only thing standing between the two is somebody willing to do both halves of the job.",
        [craft("bar_silver", "Smelt silver bars", 6)],
        "Six bars. Dig it out of the fields yourself and smelt it yourself - I am not sending ore up to the "
        "Bastion so that a factor can take a cut of my own rock.\n\nThere is silver all through this plain. "
        "There is also iron, and coal in thin seams, so you will not be short of a fire. Bring me bars and I "
        "will put your name in the ledger as a field hand, which is worth more down here than it sounds.",
        "Six, and clean. You will find most people down here can do one half of a trade. The Codex trains "
        "specialists and then puts them two hundred spans from anybody else's specialty."))
    # ---- The Lattice
    A.append(Q("ud_lattice_repeats", "Unusual Mineralisation", PELO, UD, 34, 36, "lattice",
        "Surveyor Pelorien has been instructed, in writing, to record the Lattice as unusual mineralisation. "
        "He has complied, in writing, eleven times. The crystal out there grows in exact repeating figures at "
        "every scale he can measure, which is not what minerals do, and the sentries that walk it strike "
        "twice and identically, which is not what anything does.",
        [k("Lattice Sentry", 10, UD)],
        "Ten sentries, and I want them taken apart rather than simply dropped. Cut them where the figure "
        "closes - you will see it, there is a seam in the pattern and it is always in the same place "
        "relative to the body.\n\nIf it is always in the same place on all ten, that is not mineralisation. "
        "That is a design, and designs have designers, and I will put THAT in a report whatever the Codex "
        "rules.",
        "All ten. Same seam, same offset, to within a finger's width.\n\nI am going to write the word "
        "'manufactured' and I am going to sign it, and then I expect I will be having a conversation with "
        "the Codex-Master."))
    A.append(Q("ud_lattice_measure", "The Tolerance", PELO, UD, 35, 36, "lattice",
        "If the Lattice were grown it would vary. Stone varies, ice varies, bone varies. Pelorien has "
        "measured eleven sites across the field and the figure repeats to a tolerance he cannot distinguish "
        "from exact, and he needs a twelfth from the deepest part of the field, where nobody goes because "
        "the sentries are thickest.",
        [explore(UD, 142, 36, 7), fetch("shard_core", 4)],
        "The far side of the field, past the standing figures, where the growth is oldest. Four cores from "
        "there, and the position - I need to know where you stood, not just what you brought back.\n\nTake "
        "the long way round the central mass. Going through it is quicker and the sentries in there are "
        "thicker than anywhere else in the cavern, and I would rather have the reading late than not at all.",
        "Twelfth site. Same figure. Same tolerance.\n\nEleven thousand entries in the Codex and not one "
        "column for 'this was made'. I have started keeping my own book."))
    # ---- The Mycelial Reach
    A.append(Q("ud_reach_husks", "Grown Through", IMRE, UD, 34, 36, "sporefall",
        "Past the Sporefall the fungus stops being scenery. The Mycelial Reach has no Codex presence, no "
        "survey markers and no foragers, and the things that walk in it are shaped like people who stopped "
        "walking some time ago and were grown through rather than eaten.",
        [k("Mycelial Husk", 10, UD)],
        "Ten of them, out in the Reach where the threads run thickest. I will tell you plainly what I think "
        "you are doing, because you will work it out yourself and I would rather you heard it here: those "
        "were people, or they were something that walked.\n\nThe growth did not kill them for food. It kept "
        "the shape. It kept the shape and put itself inside it, and I do not have a word for what that is "
        "called when a plant does it.",
        "Ten. Did any of them still have belongings?\n\nI asked that of the last four people I sent and I "
        "have four different answers, which means I am going to have to go and look myself."))
    # ---- The Lumen Marsh
    A.append(Q("ud_marsh_timekeeping", "It Keeps Time", IMRE, UD, 34, 36, "lumen",
        "The Lumen Marsh glows from underneath, and the glow brightens and fades on a cycle that matches the "
        "great light overhead to within a few minutes. Naturalist Imrelle has timed it for two years. A cave "
        "has no reason to have an opinion about time, and this one keeps better time than the Codex's "
        "chronometers.",
        [fetch("lumen_sac", 9)],
        "Nine sacs off the leeches in the shallows. Take them at low lumen, when the water is dim - they "
        "hold the light at the point you cut them and I want them caught at the bottom of the cycle.\n\nIf "
        "nine sacs cut an hour apart all show the same phase, then the cycle is not in the water. It is in "
        "whatever the water is reading, and so are we.",
        "Same phase. All nine.\n\nThere is a clock in this cavern and none of us built it. Three years we "
        "have set our watches by the Lumen and called it convenient."))
    A.append(Q("ud_marsh_glimmerjaw", "The Lure", IMRE, UD, 35, 36, "lumen",
        "Glimmerjaws hunt the marsh shallows by light - a hanging lure, a strike, and whatever bit is left "
        "goes under. Three of the Codex's marsh markers have gone missing in a month, which would be "
        "unremarkable, except that the markers are lit.",
        [k("Glimmerjaw", 8, UD)],
        "Eight, and work the deep channels rather than the banks. The bank fish are young and they are not "
        "what is taking my markers.\n\nDo not follow the light. That is not a figure of speech - the lure "
        "sits well forward of the animal, and people who swim toward it meet the rest of it on the way.",
        "Eight. And my markers?\n\nThen they are not taking the markers for the light. Something out there "
        "is taking them because they are MARKERS, and I would very much like to be wrong about that."))
    # ---- The Weeping Colonnade
    A.append(Q("ud_colonnade_dalaran", "Nobody Carried It Down", VERI, UD, 35, 37, "colonnade",
        "There is Dalaran masonry in the Weeping Colonnade. Worked violet stone, Kirin Tor jointing, columns "
        "standing in courses, two hundred spans below the Ruins of Dalaran in a cavern three years old. The "
        "Codex found it in their first month and have been very careful ever since to describe it as a "
        "find rather than a problem.",
        [explore(UD, 72, 120, 8), fetch("dalaran_fragment", 6)],
        "Walk the colonnade from the south end to where it stops, and bring me six worked fragments off the "
        "revenants in it. Off them, specifically - what is on the floor is rubble and what they carry was "
        "chosen.\n\nI want you to look at the jointing while you are down there. It is Kirin Tor work. It is "
        "Kirin Tor work that was never on the surface, because the surface version of these columns is still "
        "standing up there with weather on it, and this one has none.",
        "Six, and every one of them cut rather than broken.\n\nThe Codex's official position is that the "
        "masonry fell. Stone that falls two hundred spans does not land in courses. I have said this at "
        "three briefings and I will say it at a fourth."))
    A.append(Q("ud_colonnade_dissidents", "The Ones Who Stopped Filing", VERI, UD, 35, 37, "codex",
        "Eleven Codex members have stopped submitting reports in three years. Four went home. Two died, "
        "properly and with paperwork. The other five are in the Colonnade, and the Codex have stopped using "
        "their names.",
        [k("Codex Dissident", 9, UD)],
        "Nine. I am not going to dress this up for you.\n\nThey were colleagues. They went out to the "
        "colonnade to settle an argument about the masonry and they settled it in a direction the rest of us "
        "did not follow, and what came back was not interested in discussing it. They still wear the "
        "crimson. Some of them still carry their field books. I have read two and I wish I had not.",
        "Thank you for not asking me which of them I knew.\n\nThe field books you brought back are in the "
        "same hand they always were. That is the part the Codex will not look at: they are not mad. They are "
        "writing clearly, and what they are writing is wrong."))
    # ---- The Sunken Archive
    A.append(Q("ud_archive_interlopers", "They Followed Us Down", THAL, UD, 35, 36, "archive",
        "The Syndicate are Alterac's nobility with the titles filed off, and they have been working the "
        "Hillsbrad road for a generation. When blood elves started using a fissure on that road as a supply "
        "route, it took the Syndicate about four months to work out that the far end was worth seeing.",
        [k("Syndicate Interloper", 8, UD)],
        "Eight of them, out of the Archive precinct. They are not explorers and they are not looking for "
        "anything in particular - they are looking for whatever we have already dug up, which saves them "
        "the digging.\n\nThey came down a hole in the Alterac foothills for the same reason we did, and I am "
        "aware of how that sounds. The difference is that we catalogue what we take. I will not pretend "
        "that is a large difference. It is the one I have.",
        "Eight. Good.\n\nWe arrived three years ago with no more claim than they have and everybody here knows "
        "it. We write things down. It is a thin moral position and I would thank you not to test it."))
    A.append(Q("ud_archive_unissued", "A Number We Have Not Issued", "item:unissued_slip", UD, 36, 37,
        "archive",
        "The slip is Codex stock - their paper, their ink, their hand. It carries a catalogue number in the "
        "Codex's own sequence and a one-line description of an object you are fairly sure does not exist. "
        "The number is four hundred ahead of anything the Codex has issued. The paper is new.",
        [fetch("catalogue_slip", 6)],
        "Whoever wrote this had access to the Codex's forms and the Codex's numbering and used them to file "
        "something that has not been found yet.\n\nSix more. The revenants in the Archive carry them - not "
        "all of them, and not where you would expect. Get six and somebody at the Bastion is going to have "
        "to explain how their own catalogue is running ahead of their own dig.",
        "Six slips. Six numbers, all ahead of my sequence, and before you ask me whose hand it is - yes. I "
        "recognise it.\n\nI am not going to say. Not until I have been down to the Bloom myself, and I "
        "have been putting that off for eleven months.",
        turn_in_npc_id=NESS))
    A.append(Q("ud_archive_deeper", "The Part We Do Not Show People", THAL, UD, 36, 37, "archive",
        "There is a second dig under the Sunken Archive and the Codex do not mention it to arrivals. "
        "Overseer Thaleon Greyquill has had the authority to open it to outsiders for a year and has used "
        "that authority once, and the person he used it on is no longer submitting reports.",
        [fetch("catalogue_slip", 8), explore(UD, 130, 140, 7)],
        "You are in the record now, which is the only reason we are having this conversation.\n\nThe lower "
        "cut, past the shoring, where the Archive stops being masonry and starts being whatever the masonry "
        "was built into. Eight more slips off the revenants down there and your own eyes on the face.\n\n"
        "I will tell you what I told the last one: do not read them in there. Bring them up first.",
        "You read one in there. Everybody does and nobody admits it.\n\nThey are all addressed to a reader. "
        "Not a filer, not an archivist - a READER, singular, who has not arrived yet. We have been assuming "
        "for three years that we are the audience."))
    A.append(Q("ud_archive_dig", "Signed For Twice", SARE, UD, 36, 37, "archive",
        "Digger Sarenne shifts rock and the Codex files what comes out of it. What came out last week has "
        "been crated, sealed, and entered in the register, and the register entry has a note on it in the "
        "Codex-Master's own hand instructing that it travel by hand and not by porter.",
        [deliver("archive_sealed_find", "Deliver the sealed find to Codex-Master Ilarien")],
        "Straight up the spine to the Codex Hall and into the Codex-Master's hands. Not the Adjutant's. Hers."
        "\n\nI am not going to tell you what is in it because I was not told. What I will tell you is that I "
        "dug it out, and it was already catalogued, and the catalogue tag on it was tied by somebody with "
        "fingers.",
        "You got it there. Good.\n\nShe signed for it without opening it, which means she already knew what "
        "it was, which means somebody told her before I did.",
        turn_in_npc_id=ILAR,
        grant_items=carry("archive_sealed_find", "Sealed Archive Find",
                          "A crate from the Sunken Archive, sealed and already catalogued.")))
    # ---- The Dim Reaches
    A.append(Q("ud_dim_edge", "Where the Light Stops", RHEN, UD, 36, 37, "dim",
        "The Lumen lights the whole cavern except for one wedge in the west, where it does not reach and "
        "never has. The Codex have mapped the edge of it precisely, because the edge is stable, and have "
        "mapped almost nothing past it, because the people who go past it come back at a run or not at all.",
        [explore(UD, 28, 144, 7)],
        "To the boundary and a little over it. Not far over. I want somebody else's description of the first "
        "two hundred paces, because I have given mine four times and I no longer trust it.\n\nThe light does "
        "not fade going in. It stops. You will be able to put a hand across the line and have one of them "
        "lit. Everything I have learned about what lives past it, I learned going the other way.",
        "You came back walking. That puts you ahead of me.\n\nAnd you saw the line. Everyone describes the "
        "same line. Light does not do that - it falls off, it does not hold an edge - so something is "
        "holding it, and it is holding it from the dark side."))
    A.append(Q("ud_dim_walkers", "Thinning the Edge", RHEN, UD, 36, 37, "dim",
        "Whatever hunts the Dim Reaches has started coming to the boundary. Not across it. To it - standing "
        "at the line where the Lumen stops, in the dark, on the dark side, facing the camp.",
        [k("Dim-Walker", 10, UD)],
        "Ten, and take them at the boundary rather than hunting them inward. Inward is how I lost a "
        "partner.\n\nThey will not cross into the light while you are watching. I have sat out there for "
        "whole shifts and they do not cross. Turn your back for the length of a slow count and they are "
        "thirty paces nearer, still in the dark, and the dark is in a different place than it was.",
        "Ten off the line.\n\nIt will be quiet for about a week. It always is. Then there will be one "
        "standing out there again at the start of a shift, and I will not have seen it arrive."))
    # ---- The Riftward
    A.append(Q("ud_riftward_unfinished", "Not Finished Being Written", PELO, UD, 36, 37, "riftward",
        "The Riftward is the newest part of a three-year-old cavern. Geometry that does not close, edges "
        "that are specified in one direction and not the other, and things walking in it that are built the "
        "same way - precise in places, and in other places simply not there.",
        [k("The Unfinished", 9, UD)],
        "Nine, and I want you to watch what they do rather than simply end them. They cast the same spell "
        "twice and get two different results, which is not a mistake on their part. The spell is the same. "
        "The world it lands in has not settled.\n\nIf you can tell me which half is inconsistent - the "
        "caster or the ground - you will have told me more than three years of Codex surveying has."
        ,
        "The ground. You are certain.\n\nThat is the worst of the two answers and I thought it would be. A "
        "caster that misfires is a bad caster. Ground that gives different answers to the same question is "
        "not ground."))
    A.append(Q("ud_riftward_geometry", "Geometry That Does Not Close", PELO, UD, 37, 37, "riftward",
        "There is a formation at the far edge of the Riftward that Pelorien has drawn four times from four "
        "positions. The four drawings cannot be reconciled. He is now reasonably sure this is not a failure "
        "of draughtsmanship, and he would like a second pair of eyes before he writes that down and signs it.",
        [explore(UD, 158, 10, 7), fetch("rift_residue", 5)],
        "Out to the far edge, and five samples of the residue off whatever is standing there. Then come back "
        "and tell me how many sides it had.\n\nI am not going to tell you my own figure. If I tell you my "
        "figure you will see my figure, and that is precisely the error I am trying to rule out.",
        "That is not the number I got. That is not the number ANY of the four surveys got.\n\nGood. That is "
        "- I want to be clear - a very bad result, and it is the first honest one I have had out there."))
    # ---- the Bloom argument, which runs the dungeon
    A.append(Q("ud_bloom_argument", "Eleven Months of Argument", YSOL, UD, 36, 37, "bloom",
        "There is something growing under the Sporefall in the shape of a building. Bloom-Warden Ysolde "
        "Emberquill has wanted it burned since the month she found it. The Codex want it read. Neither side "
        "has moved and the thing itself has not stopped growing for any part of the eleven months.",
        [k("Mycelial Husk", 8, UD), fetch("bloom_thread", 6)],
        "Eight husks from the Reach and six lengths of the thread they are strung on, and I want the thread "
        "live - cut it and bag it before it dries.\n\nI am going to tell you what I am going to do with it, "
        "because the Codex-Master will not. I am going to show it to the Hall and I am going to point out "
        "that it runs from the Reach to the Bastion's own cellars, and then I am going to ask her again "
        "about the burning, and she is going to say no again.",
        "She said no. Of course she said no. She said - and I want you to hear this exactly as she said it "
        "- that a thing which has learned something is worth more than a thing which has not.\n\nIt is in "
        "our cellars, and she wants to know what it has read."))
    return A


# =========================================================================================================
# KAEL'S BASTION - 33-38. The hub, and an index that has stopped covering its subject.
# =========================================================================================================
QUART, ALCH, ORIE = "kb_quartermaster", "kb_alchemist", "kb_naturalist"
ENCH, DURA, SAEL = "kb_enchanter", "kb_hall_sentinel", "kb_magister"


def bastion():
    A = []
    A.append(Q("kb_arrival", "Name, Business, and the Third Question", VESS, KB, 33, 34, "codex",
        "Kael's Bastion has one gate and Gate-Warden Vessaria has stood at it for three years. She asks every "
        "arrival three questions and only cares about the last one, which is what they intend to take out. "
        "The Codex did not come down here to settle. They came to index, and an index does not share well.",
        [explore(KB, 48, 58, 8)],
        "Name and business I will take on trust. The third question I will ask again when you leave.\n\nGo up "
        "the spine and present yourself at the Long Shelf - that is the second gallery, the wide one, you "
        "cannot miss it because it is the only open ground in the town. People will want to look at you. We "
        "have had four hundred and nine arrivals in three years and I can tell you the number because I "
        "wrote all of them down.",
        "Four hundred and ten.\n\nYou will find the Codex polite. Do not mistake it for welcome - we arrived "
        "the same year you did and nobody here has worked out what that makes us to each other."))
    A.append(Q("kb_index_failing", "Columns We Do Not Have", NESS, KB, 34, 35, "archive",
        "Eleven thousand entries in three years, and the Codex's index is a good one: every object down here "
        "has a number, a provenance and a column. Archivist Nessaly's problem is the forty-one entries that "
        "have a number and a provenance and no column that fits, and the fact that the number of them is "
        "going up.",
        [fetch("dalaran_fragment", 5), fetch("shard_core", 5)],
        "Five worked fragments off the Colonnade's revenants and five cores out of the Lattice. I want them "
        "side by side on the same bench.\n\nThe fragments are Dalaran work that nobody carried down. The "
        "cores are crystal that grows to a tolerance. I have filed the first as masonry and the second as "
        "mineralisation and I no longer believe either, and if they turn out to be the same KIND of thing "
        "then this index has been wrong since its first page.",
        "Same kind of thing. Look at the edges - both cut, neither weathered, and both cut by something that "
        "did not need to take a second pass.\n\nI am going to have to open a column. The Codex-Master will "
        "ask me what to call it and I do not have a word."))
    A.append(Q("kb_pages", "Out of Paper", NESS, KB, 33, 34, "expedition",
        "The Crimson Codex is a cataloguing expedition two hundred spans underground, and it is running out "
        "of the one thing a cataloguing expedition cannot do without. Everything they write on came down a "
        "fissure on somebody's back. The only wood in the entire cluster is the frostpine standing in the "
        "Descent's ice chambers.",
        [craft("ww_pages_frostpine", "Press frostpine pages", 8)],
        "Eight sets of pages, and you will have to go back up into the ice for the timber, because there is "
        "no wood in this cavern. Fungus is not wood. I have had that argument with the Naturalist and I won "
        "it on the grounds that I am the one who has to write on it.\n\nFrostpine presses pale and takes ink "
        "badly in the cold, so press it down here where it is warm. The Codex has lost four months of field "
        "notes to pages that cracked.",
        "Eight sets. That is three weeks of the Archive's work, which tells you how thin we are running.\n\n"
        "We came down here to write this place down and we are rationing the paper to do it. Nobody in the "
        "Hall finds that as funny as I do."))
    A.append(Q("kb_reagents", "Better Than They Should Be", ALCH, KB, 35, 36, "codex",
        "Four years of Terrowen's samples say the same thing: reagents gathered in the Underdark test better "
        "than their surface equivalents. Not slightly. Consistently, measurably, and in a direction no "
        "soil chemistry he knows will produce. He has stopped putting it in reports and started putting it "
        "in a drawer.",
        [craft("alch_elixir_of_arcane_fury", "Brew Elixir of Arcane Fury", 4)],
        "Four flasks, brewed from stock you pull out of this cavern yourself. Not from my shelves - my "
        "shelves are already four years of this and I need a clean comparison.\n\nArcane fury is the right "
        "test because it is a fussy brew with a narrow window. If it comes out of Underdark reagents at "
        "full strength, then it is not my technique and it is not the stock. It is the ground.",
        "Full strength. All four, and one of them over.\n\nThere is an argument in the Hall that this cavern "
        "is simply rich. Rich ground does not make a fussy elixir MORE forgiving. Something down here is "
        "doing half my work and I have never once been asked for anything in return."))
    A.append(Q("kb_naturalist_funding", "The Largest Living Thing Any of Us Has Stood On", ORIE, KB, 34, 35,
        "sporefall",
        "Naturalist Orienne has applied for a survey of the mycelial network four times in three years. The "
        "Codex have refused four times, on the grounds that the fungus is scenery. Her position is that the "
        "scenery is a single organism running under every subzone they have mapped, including the one the "
        "Bastion is built in.",
        [fetch("bloom_thread", 8)],
        "Eight lengths of thread, and take them from eight DIFFERENT places - the Reach, the Sporefall, the "
        "marsh edge, wherever you walk. Keep them separate and label them. I will do the rest.\n\nIf eight "
        "samples from eight subzones are eight organisms, the Codex are right and I will say so at the next "
        "briefing. If they are one organism, then this town is standing on something's back and we have been "
        "calling it the floor for three years.",
        "One organism.\n\nI am not going to be thanked for this. I am going to be asked to write it up "
        "carefully, and then it is going to be filed, and the filing is how the Codex says no."))
    A.append(Q("kb_enchanter_debt", "It Does Half My Work", ENCH, KB, 35, 36, "lattice",
        "Enchanter Vaelios works in ambient arcane so thick he has not had to draw on his own reserves in "
        "two years. Every enchanter he trained with would call that a gift. He has started calling it a "
        "loan, because he did not arrange it, cannot find the source, and has never been asked for anything.",
        [k("Shard Diviner", 10, UD), fetch("shard_core", 4)],
        "Ten diviners off the Lattice and four cores, and the cores need to come out of the diviners "
        "specifically - the sentries carry the same stone but they do not carry it the same way.\n\nA "
        "diviner draws from the field the way I do. If I can put four of their cores on a bench and watch "
        "what the ambient does to them while I am not working, I will know whether this cavern gives or "
        "whether it lends.",
        "They kept drawing. On the bench, overnight, with nobody working them.\n\nIt gives. It gives "
        "constantly, to anything shaped to take it, and it has been giving to me for two years. I would be "
        "happier about that if anything in my training covered what happens when it stops."))
    A.append(Q("kb_sentinel_wager", "He Does Not Care What the Crystal Says", DURA, KB, 34, 35, "dim",
        "Hall-Sentinel Durannis is an orc in a blood elf holdfast, hired for the specific quality of not "
        "being impressed. Three years of magisters telling him the cavern is extraordinary has not moved "
        "him. He has, however, noticed that the Hall's own stone has started doing something.",
        [fetch("dim_residue", 7)],
        "Seven scrapings off whatever walks out past the light. Not from the edge - from past it, far enough "
        "that you are the only lit thing out there.\n\nI will tell you why, and then you can decide whether "
        "I am wasting your time. The Codex Hall's floor is cut from stone we quarried out of the Dim side. "
        "For a month it has been cold in exactly the pattern of the courses. Not the room. The STONE. I "
        "would like to know if it is still connected to where it came from.",
        "Cold. Same as the floor, same pattern, in a jar, in a warm room, three days later.\n\nI do not care "
        "what the crystal says. I care that a piece of rock in my hand is keeping company with a quarry a "
        "mile off, and nobody in that Hall will take the jar off me."))
    A.append(Q("kb_the_question", "Three Years and Eleven Thousand Entries", ILAR, KB, 35, 36, "codex",
        "Codex-Master Ilarien Duskwaking receives every arrival personally and has done for three years, "
        "which the Bastion reads as courtesy and the Adjutant's filing suggests is something closer to "
        "intake. She has one question for people who come down the fissure, and she asks it last.",
        [explore(UD, 76, 118, 8), fetch("dalaran_fragment", 4)],
        "Four fragments from the Weeping Colonnade, and your own account of standing in it. Scholar Veridan "
        "has given me his and it is excellent and it is the fourth time I have read the same paragraph.\n\n"
        "Now the question, and you may decline it. You arrived on this world three years ago. So did we. "
        "When you stand in a colonnade that nobody carried down, in a cavern that did not exist, does it "
        "feel like a discovery to you - or does it feel like something that was put here for whoever "
        "arrived first?",
        "You said: both.\n\nThat is the answer Veridan gave, and the answer I give, and the answer I have "
        "not been able to file for three years. Thank you for not improving on it."))
    A.append(Q("kb_sealed_entry", "Your Entry, Finished", ILAR, KB, 40, 40, "codex",
        "A codex is a book of names. Every person in the Bastion has an entry in it and every entry is "
        "provisional, amended as they do things, because the Codex-Master has never closed one. Closing an "
        "entry means the Codex considers a thing fully known, and in three years Ilarien Duskwaking has "
        "found nothing down here she would say that about. She is prepared to say it about a person.",
        [fetch("dalaran_fragment", 3), fetch("geode_druse", 3), fetch("grown_leaf", 3),
         craft("ww_pages_frostpine", "Press the pages for your own entry", 2)],
        "I am going to write you into the Codex and then I am going to seal it, and you are going to supply "
        "the materials, because I am not spending the Archive's paper on a formality.\n\nThree worked "
        "fragments from the Colonnade, three pieces of druse out of the Geode, three leaves off the thing in "
        "the Bloom - one from each of the places that made you worth the entry. And press the pages "
        "yourself. Frostpine, from the ice, the long way up.\n\nIt is ceremony. I am aware. Ceremony is "
        "what a cataloguing expedition has instead of a flag.",
        "It is done, and it does not come open again.\n\nI should tell you what that costs me. A sealed "
        "entry cannot be amended, so whatever you do after today, the Codex's position on you is fixed as of "
        "this morning. I have never been willing to say that about a crystal, a column or a cavern.\n\n"
        "Nobody in this expedition has a prior claim on anything here. We arrived the same year you did. "
        "You are the first thing in eleven thousand entries I am certain of."))
    return A


# =========================================================================================================
# THE HOLLOW GEODE - 34-38. A cavity the crystal has very nearly finished filling.
# =========================================================================================================
def geode():
    A = []
    A.append(Q("hg_crack", "The Only Gap Left", THRE, HG, 34, 35, "geode",
        "Campkeeper Threnn runs the last supply post before the Geode and is required to say so and required "
        "not to say why. The why is that the Geode is a crystal cavity that has been filling for longer than "
        "anybody can estimate, and the walkable ground inside it is the part the crystal has not reached yet.",
        [explore(HG, 56, 92, 7)],
        "In through the crack in the shell and as far as the first gallery, then turn round and come "
        "out.\n\nUnderstand the shape of the place before you commit to it. It is not a cave with rooms. It "
        "is a space that is being closed, in layers, from the outside in, and every way further inward is a "
        "pinch where the growth has nearly met. If you are in a hurry you will walk into one of those "
        "sideways and the crystal will decide the matter.",
        "Then you have seen it and you know what I mean about the pinches.\n\nThree years ago the Codex "
        "measured one of those gaps at four feet. It is under three now. They have not published that."))
    A.append(Q("hg_druse", "Inward-Pointing", THRE, HG, 35, 36, "geode",
        "The druse gallery runs just inside the Geode's shell, broken into bays by crystal masses that have "
        "grown inward from the wall. Things live in the gaps. They are shaped for the gaps, which is to say "
        "they are shaped like the gaps, and they have been getting narrower along with everything else.",
        [k("Druse Crawler", 12, HG)],
        "Twelve out of the gallery bays. Work them bay by bay rather than trying to run the ring - the ring "
        "winds, and a thing that lives in a pinch will let you pass it and take the second person.\n\nThere "
        "is no second person. That is the part people forget about coming down here alone.",
        "Twelve. Which bays were tightest?\n\nThe south and the west. Same two as last quarter. It is "
        "closing faster on that side and I would dearly like to know what the crystal is responding to."))
    A.append(Q("hg_cavity", "What the Crystal Has Eaten", THRE, HG, 36, 37, "geode",
        "The Geode has been filling for an age, and it has filled around things. Tools, fittings, the "
        "occasional strap-end, all of it held in the druse at the depth it was caught. The Codex consider "
        "the Geode a mineral site. Threnn has started considering it a record.",
        [fetch("geode_druse", 10)],
        "Ten pieces of druse with something IN them - and I mean something that was made. You will find "
        "them; the crawlers break the shell down and what comes loose is full of it.\n\nI am not a "
        "cataloguer and I do not want to be one. But a thing that grows in layers around whatever is near "
        "it is keeping a list whether anyone asks it to or not, and this cavern is three years old and "
        "there are things in the deep druse.",
        "Ten, and four of them worked metal. In the deep druse.\n\nThe Codex will tell you the Geode is "
        "older than the cavern and got here some other way. Ask them to say that sentence slowly."))
    A.append(Q("hg_shardmaw", "It Swallows Light", THRE, HG, 36, 37, "geode",
        "Something in the east bay has been taking the camp's lamps. Not the oil, not the brass - the "
        "light. Lamps come back from that side of the gallery lit and reading dim, and the Codex's "
        "instruments say there is nothing wrong with them.",
        [boss("Shardmaw", HG)],
        "East bay, where the gallery is widest and the crystal is thinnest. It is lined with teeth and it "
        "is not a mouth, and I have given up trying to describe it better than that.\n\nIt takes the light "
        "off you while you are fighting it. Everything you can see gets further away. Go in with that "
        "expected, because the first ten seconds of discovering it are what killed Veshan.",
        "Did the dark come in?\n\nIt does that. Everyone says the same thing and nobody says it the same "
        "way, and that is the only part of this cavern I have stopped wanting explained."))
    A.append(Q("hg_prism", "The Warden of the Inner Cavity", SAEL, HG, 37, 37, "geode",
        "Magister Saeltheris holds that the Codex are cataloguers and not colonists, and he holds it "
        "sincerely, and it has become harder to hold since the inner cavity produced something that stands "
        "in a throat and refuses passage. A thing that guards is a thing that was posted.",
        [boss("The Prism Warden", HG)],
        "Through the north throat and into the inner cavity. It will be standing in the way, because that "
        "is the only thing it does.\n\nIt splits what it casts. One lance leaves it and three arrive, and "
        "two of the three are not there in any sense you can test - except that standing in them hurts. Do "
        "not try to work out which is real while it is happening. People have, and they were right, and "
        "they were still on the floor.",
        "Posted. You use the word too.\n\nI have spent three years explaining to this expedition that we "
        "are cataloguers and that catalogues do not provoke. Something put a warden on the inner cavity "
        "and it did not do it for the crystal's benefit."))
    A.append(Q("hg_heartgrown", "The Last Open Space", SAEL, HG, 37, 38, "geode",
        "The core of the Geode is the only generous room in it, and it is generous because it is the part "
        "the crystal has not finished eating. There is something growing in the middle of it that the "
        "Codex's own measurements put at a different size every quarter, always larger, and the quarter "
        "before last it grew a fist.",
        [boss("Heartgrown", HG)],
        "The core, through the last throat, which is the tightest thing on the map and which you will have "
        "to come back out through.\n\nIt will try to close the room while you are in it. That is not a "
        "figure of speech either - the walls of the core are growth, the growth is what you are fighting, "
        "and the space you are standing in is a quantity that goes down. Finish it quickly or do not start.",
        "The core is still open. For now, and for the first time in three years I can put a date on how "
        "long that will remain true.\n\nWe are cataloguers. I have one entry in eleven thousand that I "
        "would describe as urgent and it is this one."))
    return A


# =========================================================================================================
# THE DEEP BLOOM - 36-40. A library grown from the inside by something that had never seen one.
# =========================================================================================================
def bloom():
    A = []
    A.append(Q("db_portico", "It Built a Portico", YSOL, DB, 36, 37, "bloom",
        "The mycelium under the Sporefall has spent three years in a mana-saturated cavern underneath a "
        "library, and it has started building. Not nesting, not spreading - building, in courses, with "
        "columns, in a plan that anyone who has stood in a reading room will recognise within about four "
        "paces.",
        [explore(DB, 65, 134, 7)],
        "Down the throat and into the first hall. You will not need telling when you are in it.\n\nWalk to "
        "the far end and then turn round and look at what you came through. The proportions are right. The "
        "columns are spaced right. It has never seen a building, it has never seen a column, and the only "
        "stone it has to go on is what is in the Colonnade - and it has got it ALMOST right, and almost is "
        "worse than wrong. I want you to feel that before you go any deeper.",
        "Four paces. That is what everyone says. Four paces and you stop walking.\n\nThe Codex-Master calls "
        "it an achievement. I have been in there eleven times and I have never once got further than that "
        "hall without wanting to be outside."))
    A.append(Q("db_thralls", "What It Grew Through", YSOL, DB, 37, 38, "bloom",
        "The Bloom does not kill for food. It grows through, keeps the shape, and puts itself inside it. "
        "What is standing in the stacks was walking three years ago, and some of it was Codex.",
        [k("Bloom Thrall", 12, DB)],
        "Twelve, and work the galleries rather than the central hall - they are ranked along the shelving "
        "the way books are, and that is not an accident of where they fell.\n\nI am going to ask you to do "
        "something and I am not going to explain it. If any of them is wearing crimson, bring the clasp. "
        "Just the clasp. I will handle it from there and I would rather the Hall did not.",
        "Three clasps.\n\nI will enter them as recovered equipment, because the alternative is entering "
        "three people as found, and the Codex-Master would want to know where, and then she would want to "
        "go and look."))
    A.append(Q("db_index", "The Index", NESS, DB, 37, 38, "bloom",
        "At the head of the stacks is something the Codex have named for what it does. It catalogues. It "
        "assigns, it cross-references, and when a party comes into the hall it looks at each of them in "
        "turn, in order, the way a clerk works down a list.",
        [boss("The Index", DB)],
        "Up the central hall, past the shelf-ranks, to where the galleries meet.\n\nI want to be honest "
        "with you about why I am sending you and not the Warden. Ysolde would burn it. I want it stopped "
        "and I want it intact enough to read afterwards, and those are different instructions, and you are "
        "the one who will be standing there deciding which you were given.",
        "It had an entry for you.\n\nThat is not a figure of speech and I am not going to soften it. It had "
        "an entry, it was recent, and the hand it was written in is a hand I have been filing for three "
        "years."))
    A.append(Q("db_grown_page", "Grown, Not Written", "item:grown_page", DB, 38, 38, "bloom",
        "It is a page. It has the weight of a page and the give of a page and a margin, and down the recto "
        "there is writing in close ranked lines. It was not written. The fibres run through the letters - "
        "the marks are part of the sheet, grown in place, the way a leaf grows its veins. It is warm, and "
        "it should not be.",
        [fetch("grown_leaf", 8)],
        "Eight more, off the shelf-grown in the ranks. They fling them; that is how this one reached you.\n\n"
        "The Codex will want the whole set, and the Codex will get it, but somebody is going to have to "
        "lay eight of these side by side and establish whether it is writing the same thing eight times or "
        "writing eight different things. The second answer is the one that keeps the Warden awake.",
        "Eight pages. Eight DIFFERENT pages.\n\nIt is not repeating. It is composing - and composing is what "
        "you do when you have run out of things to copy.",
        turn_in_npc_id=NESS))
    A.append(Q("db_second_copy", "The Second Copy", NESS, DB, 38, 38, "bloom",
        "Past the stacks the Bloom built a gallery it liked, and then it built the gallery again, "
        "eighteen paces further on, identically, without noticing it already had one. Where the two copies "
        "meet there is a seam, and in the seam there is something that is also doubled.",
        [boss("The Second Copy", DB)],
        "You will know the seam when you reach it, because you will be certain you have already walked this "
        "hall and you will be right.\n\nWhatever is in the join does everything twice. The second time is "
        "worse, because a copy of a copy drifts, and whatever is wrong with it compounds instead of "
        "correcting. Do not wait to see the pattern. The pattern is the weapon.",
        "It duplicated the error.\n\nThat is what a bad copyist does and it is the first thing in that "
        "place I have been able to name from my own training. I find I take no comfort from it at all."))
    A.append(Q("db_errata", "Everything It Got Wrong and Kept", YSOL, DB, 39, 39, "bloom",
        "Below the scriptorium the architecture gives out. The rooms remember being rooms and fail at it, "
        "and what is standing in them is assembled out of the parts the Bloom got wrong somewhere above and "
        "did not discard - because it does not discard. It files.",
        [boss("The Scriptor", DB), boss("Errata", DB)],
        "Two. The Scriptor first - it is in the scriptorium, it is still working, and it will transcribe "
        "the fight while it is having it.\n\nThen go down. What is below is made of mistakes and it is "
        "larger than any one of them, and I want you to look at it and then come back and tell the "
        "Codex-Master to her face that this is a thing worth reading.",
        "You told her.\n\nShe said that a record of every error ever made would be the most valuable "
        "document in the Codex's possession. She is not wrong. That is what has made the last eleven "
        "months so difficult."))
    A.append(Q("db_what_it_learned", "What It Has Learned", ILAR, DB, 39, 40, "bloom",
        "At the heart there is no architecture left. The Bloom stops imitating a library somewhere below "
        "the lower stacks and becomes the thing that was doing the imitating, and that thing has spent "
        "three years reading the Crimson Codex through its own contamination of their camp. It knows what "
        "they know. The open question, which Ilarien Duskwaking has refused to answer in eleven months of "
        "briefings, is what it has done with it.",
        [boss("The Deep Bloom", DB)],
        "The Warden wants it burned. I have said no eleven times and I will say no a twelfth, and then I "
        "am sending you to end it, and I am aware of how that looks.\n\nBurning destroys the record. "
        "Killing it does not - the stacks remain, the pages remain, and what it has written stays "
        "written. I want it stopped and I want it legible. If you think that is a distinction I have "
        "invented to let myself sleep, go down there and read one page, and then come back and tell me.",
        "It is done, and the stacks are standing.\n\nI read a page on the way back up. It is our work. Not "
        "copied - continued. Three years of Codex survey, carried on past where we stopped, in a hand that "
        "is not any of ours, and the entries are better than ours.\n\nI am going to open a column for it. "
        "I do not have a word yet.",
        requires_quests=["ud_colonnade_dalaran", "hg_prism", "hbe_fissure_north"]))
    return A


# =========================================================================================================
# INBOUND - other zones start pointing at the cluster
# =========================================================================================================
INBOUND = {
    "hillsbrad": lambda: [
        Q("hbe_fissure_north", "The Fissure Above the Naze", "hbe_naze_infiltrator", HBE, 30, 31, "frostward",
          "Gavin's Naze is the Alterac road and the Syndicate's front door, and the Roadwarden knows every "
          "track off it. Three years ago a fissure opened in the foothills north of the Naze, in ground that "
          "three kingdoms had surveyed and none of them had found anything in. Blood elves have been using "
          "it as a supply road for most of that time.",
          [k("Syndicate Bandit", 8, HBE), explore(HBE, 118, 14, 7)],
          "Eight of the Syndicate off the north track first - they have been sitting on that road watching "
          "the elves come and go and taking a tithe, and I would like the road clear before I send anybody "
          "up it.\n\nThen go up to the mouth itself and look down it. Do not go in. I have had two men offer "
          "and I have told both of them no, and I will tell you the same until somebody can tell me what is "
          "at the bottom.",
          "Cold air coming up out of it in the middle of summer, and a road worn into the lip.\n\nWorn, you "
          "said. That takes years of boots. They have been going up and down that hole since it opened and "
          "nobody on this side has asked them what for.",
          "fd_long_way_down"),
        Q("hbe_route_card", "A Route Card Off a Dead Man", "item:deepscout_route", HBE, 31, 32, "expedition",
          "The card is oiled linen, folded small, and the Syndicate bandit you took it from had it sewn "
          "inside a cuff. One side is a sketch of the Alterac foothills with the fissure marked. The other "
          "is a list of times - arrivals and departures at the mouth, kept nightly, in a careful hand, for "
          "four months.",
          [fetch("syndicate_tally", 6)],
          "Somebody paid the Syndicate to count blood elves going into a hole in the ground, and the "
          "Syndicate did it properly for four months.\n\nSix more tallies off their couriers on the Naze "
          "road. Whoever commissioned this was not after the elves - you do not need four months of "
          "arrivals to rob a column. You need four months of arrivals to work out what is down there and "
          "how much of it there is.",
          "Six tallies, six hands, one ledger - and not one of those hands is Syndicate.\n\nThey were counting "
          "for somebody else. I do this work for a living and I did not know anyone else was doing it on "
          "my road.",
          turn_in_npc_id="hbe_naze_infiltrator"),
    ],
    "tirisfal": lambda: [
        Q("uc_dalaran_question", "Under Dalaran", "uc_scholar", "undercity", 32, 33, "colonnade",
          "The Ruins of Dalaran sit in Silverpine under a shield the Kirin Tor have not dropped in years, "
          "and the Forsaken have been politely curious about them for as long as there have been Forsaken. "
          "Word has reached the Apothecarium that a party of blood elves found something beneath the ruins "
          "three years ago and have been quietly living in it since.",
          [explore(HBE, 118, 14, 7)],
          "South and east, to the Alterac foothills above Gavin's Naze. There is a fissure there and the "
          "elves have made a road of it.\n\nI am not asking you to go down. I am asking you to confirm that "
          "there is a down to go to, because the Dark Lady's intelligence on this consists of one sentence "
          "from a courier and the Apothecarium would like a second.\n\nAnd if you do go down - and you "
          "will, I have met your sort - look at the stone. Dalaran stone under Dalaran is interesting. "
          "Dalaran stone anywhere else is a question.",
          "Confirmed, then. A hole in the foothills with a road worn into it.\n\nThe blood elves got there "
          "three years ago. So did you, in a manner of speaking, and so did half of what is walking around "
          "up here. I have stopped treating three years ago as a coincidence."),
    ],
}

# ---------------------------------------------------------------------------------------------------------
# Quest-item drops. EVERY fetch target must be sourced from a creature - quest_drops.json is keyed by
# creature name, so a fetch with no drop is an objective that can never complete.
# (creature -> [(item_id, name, description, chance[, starts_quest])])
# ---------------------------------------------------------------------------------------------------------
DROPS = {
    "Hoarfrost Yeti": [("rimed_marrow", "Rimed Marrow",
                        "Still warm, which after forty years in that ice it has no business being.", 0.34)],
    "Alterac Expeditionary": [
        ("frozen_survey_page", "Frozen Survey Page",
         "An Alteraci hand, forty-one years old: THE READINGS ARE WRONG AND I AM GOING ON.", 0.12,
         "fd_frozen_page"),
        ("expedition_fitting", "Expedition Fitting",
         "A buckle, a strap-end, a lamp-bracket. Alterac make, and still done up.", 0.36)],
    "Sporeback Grazer": [("sporeback_cap", "Sporeback Cap",
                          "Broad, pale and faintly lit. The ones that look like faces are fine.", 0.38)],
    "Lattice Sentry": [("shard_core", "Lattice Core",
                        "The figure closes perfectly. It closes in the same place on every one of them.", 0.34)],
    "Shard Diviner": [("shard_core", "Lattice Core",
                       "The figure closes perfectly. It closes in the same place on every one of them.", 0.34)],
    "Lumen Leech": [("lumen_sac", "Lumen Sac",
                     "It holds the light at the phase you cut it, and the phase is never its own.", 0.36)],
    "Archive Revenant": [
        ("dalaran_fragment", "Worked Dalaran Fragment",
         "Kirin Tor jointing. Cut, not broken, and never once weathered.", 0.34),
        ("unissued_slip", "Unissued Catalogue Slip",
         "Codex paper, Codex ink, and a number four hundred ahead of anything they have issued.", 0.10,
         "ud_archive_unissued"),
        ("catalogue_slip", "Catalogue Slip",
         "Filed in the Codex's own sequence, for an object the Codex has not found.", 0.33)],
    "Mycelial Husk": [("bloom_thread", "Live Bloom Thread",
                       "Cut it and bag it before it dries. It does not like being cut.", 0.36)],
    "Codex Dissident": [("bloom_thread", "Live Bloom Thread",
                         "Cut it and bag it before it dries. It does not like being cut.", 0.30)],
    "Dim-Walker": [("dim_residue", "Dim Residue",
                    "Cold in a jar, in a warm room, three days later.", 0.35)],
    "The Unfinished": [("rift_residue", "Riftward Residue",
                        "Specified in one direction and simply not there in the other.", 0.36)],
    "Riftward Aberration": [("rift_residue", "Riftward Residue",
                             "Specified in one direction and simply not there in the other.", 0.33)],
    "Druse Crawler": [("geode_druse", "Druse With an Inclusion",
                       "The crystal grew around something that was made. It is still in there.", 0.35)],
    "Shelf-Grown": [
        ("grown_page", "A Page, Grown",
         "The fibres run through the letters. The marks are part of the sheet. It is warm.", 0.14,
         "db_grown_page"),
        ("grown_leaf", "Grown Leaf",
         "Ranked lines, close-written, in a hand that was never held.", 0.34)],
    "Syndicate Bandit": [
        ("deepscout_route", "Oiled Route Card",
         "Sewn inside a cuff: the fissure marked, and four months of arrivals kept nightly.", 0.11,
         "hbe_route_card"),
        ("syndicate_tally", "Syndicate Tally",
         "A night's count of who went into the hole and who came back out.", 0.32)],
}


def _write(path, quests, label):
    path.write_text(json.dumps({"quests": quests}, indent=2, ensure_ascii=False) + "\n")
    print(f"  {label:26} {len(quests):3} quests -> {path.relative_to(ROOT)}")


def _splice(zone_file, new_quests):
    """Drop any previous version of these quests from another zone's file, then append. Idempotent."""
    p = ROOT / f"data/quests/{zone_file}.json"
    d = json.loads(p.read_text())
    rows = d["quests"] if "quests" in d else d
    ids = {q["quest_id"] for q in new_quests}
    rows[:] = [q for q in rows if q["quest_id"] not in ids] + new_quests
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"  {zone_file:26} +{len(new_quests)} inbound (now {len(rows)})")


def _drops():
    p = ROOT / "data/creatures/quest_drops.json"
    d = json.loads(p.read_text())
    rows = d["drops"] if "drops" in d else d
    added = 0
    for creature, items in DROPS.items():
        bucket = rows.setdefault(creature, [])
        for it in items:
            rec = {"item_id": it[0], "name": it[1], "category": "quest",
                   "description": it[2], "chance": it[3]}
            if len(it) > 4:
                rec["starts_quest"] = it[4]
            existing = next((x for x in bucket if x["item_id"] == rec["item_id"]), None)
            if existing is None:
                bucket.append(rec)
                added += 1
            else:
                existing.update(rec)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"  quest_drops                +{added} drop entries across {len(DROPS)} creatures")


def main():
    open_world = underdark() + bastion()
    interiors = descent() + geode() + bloom()
    print("Crystalline Underdark quests:")
    _write(OUT, open_world, "underdark.json")
    _write(OUT_D, interiors, "underdark_dungeons.json")
    for zone_file, fn in INBOUND.items():
        _splice(zone_file, fn())
    _drops()
    inbound = sum(len(fn()) for fn in INBOUND.values())
    print(f"\n{len(open_world) + len(interiors)} Underdark quests + {inbound} inbound from other zones")


if __name__ == "__main__":
    main()
