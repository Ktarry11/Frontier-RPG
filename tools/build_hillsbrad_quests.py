"""
Hillsbrad quest pass.  Idempotent.

    PYTHONPATH=. python3 tools/build_hillsbrad_quests.py && python3 tools/build_quest_text.py hillsbrad

Writes data/quests/hillsbrad.json (Western 23, Eastern 19, Tarren Mill 14) and
data/quests/hillsbrad_dungeons.json (Azurelode 6, Dun Garok 5, Durnholde 6), adds the fetch and starter drops to
data/creatures/quest_drops.json, and appends the INBOUND bridge quests to their own zones' files so other parts of
the world start pointing at Hillsbrad.

NO ESCORTS (Kyle's standing rule, and the only hard "never" in the quest design).

USES THE WHOLE TOOLKIT, not just kill/fetch. The engine grew deliver / craft / requires_quests / starter-drop
support in commit e033a45 and Hillsbrad is the first zone built with all of it from the start:

  deliver        Ovid Thane's flour consignment rides from the Eastern gate to the Western fields - a real
                 cross-zone walk, hand-in on a different NPC.
  craft          Azurelode is a SILVER mine, so the mine's own quest is to smelt what you dug out of it. The
                 farrier wants shoes forged, the poacher wants arrows fletched.
  starter drops  A Drowned Castaway's swollen signet, a Syndicate courier's sealed orders, a Shadowfang
                 moonwalker's annotated page. You pick up the quest by looting it, from a mob in the quest's
                 own level band.
  Linken gate    dh_perenolde opens ONLY if you have done hbe_gavin (Eastern Hillsbrad), dh_yvaine (Durnholde)
                 and sps_godfrey (Silverpine South). Three zones, two of them optional on their own. Skip any
                 one and the Baron is never offered - which is the point of the pattern.
  inbound        Five quests in OTHER zones now send you here: two from Silverpine South, one from Silverpine
                 North, one started by a Shadowfang drop, one from the Undercity.

LEVEL BAND. Hillsbrad is the bridge between Silverpine (ends 20) and the Plague Depths (32-34): west 20-25,
east 23-29, Tarren Mill 23-28, Azurelode 23-26, Dun Garok 26-29, Durnholde 27-31.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/hillsbrad.json"
OUT_D = ROOT / "data/quests/hillsbrad_dungeons.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

HBW, HBE, TM = "western_hillsbrad", "eastern_hillsbrad", "tarren_mill"
AZ, DG, DH = "azurelode_mine", "dun_garok", "durnholde_keep"

XP = {19: 1240, 20: 1320, 21: 1400, 22: 1480, 23: 1560, 24: 1640, 25: 1720, 26: 1800,
      27: 1880, 28: 1960, 29: 2040, 30: 2120, 31: 2200}
GOLD = {19: 5400, 20: 5700, 21: 6000, 22: 6300, 23: 6600, 24: 6900, 25: 7200, 26: 7500,
        27: 7800, 28: 8100, 29: 8400, 30: 8700, 31: 9000}

# Hillsbrad's own gear flavour. Green farm country over the top of a war nobody has declared.
tirisfal_gear.THEMES.update({
    "southpoint": (["Southpoint", "Tower-Watch", "Signal-Fire", "Picket's", "Garrison-Grey"],
                   ["One tower, and a whole valley watching it.", "Issued at the tower and never handed back.",
                    "Smells of woodsmoke and wet stone.", "Worn by someone who slept in shifts."]),
    "fields": (["Hillsbrad", "Furrow-Worn", "Harvest", "Sheaf-and-Sickle", "Militia"],
               ["Good barley country, and everyone in it is armed.", "Soil in the seams that will not wash out.",
                "A farmhand's, until the farmhand picked up a billhook.", "Honest cloth, badly used."]),
    "pastures": (["Highland", "Ram-Horn", "Snowline", "Yeti-Torn", "Shepherd's"],
                 ["Carried up past the snowline and back down again.", "Ram's wool, greased against the rain.",
                  "Something with very long arms has been at it.", "The high pasture wind gets into everything."]),
    "strand": (["Daggerspine", "Tidewrack", "Brine-Bitten", "Harpooner's", "Undertow"],
               ["Still damp. It is always still damp.", "Scaled, and the scales are not fish.",
                "Dragged out of the shallows with the owner still in it.", "Salt has eaten half the fittings."]),
    "orchard": (["Orchard", "Windfall", "Wasp-Stung", "Cider-Press", "Thistlewing"],
                ["Sticky with something that is not sap.", "Smells of bruised apples and wet grass.",
                 "The hive took the orchard. This came back out of it.", "Lacquer-hard and apple-dark."]),
    "southshore": (["Southshore", "Marine's", "Harbour-Watch", "Press-Gang", "Blunderbuss"],
                   ["Taken off a marine who will not need it.", "Harbour issue, and used well outside the harbour.",
                    "Three sets of initials scratched inside.", "Powder-burned at one shoulder."]),
    "purgation": (["Purgation", "Drowned", "Castaway's", "Saltrot", "Deep-Mourning"],
                  ["Everything that comes up off that shore comes up wrong.", "Weed still knotted in the buckles.",
                   "It belonged to a ship. The ship is on the bottom.", "Cold in a way the sun does not fix."]),
    "azurelode": (["Azurelode", "Silver-Seam", "Sump-Drowned", "Lamp-Lit", "Pump-House"],
                  ["Silver dust worked into the grain, blue in lamplight.", "Pulled out of water that should not be there.",
                   "The lower works are flooded. This was not.", "Kobold-chewed at one corner."]),
    "millrace": (["Mill-Race", "Sluice-Gate", "Tarren", "Flour-Pale", "Two-Bank"],
                 ["Flour-dust in every seam, and it never comes out.", "Damp from the race, dried by the wheel.",
                  "Made on one bank and worn on the other.", "The wheel has turned past this for sixty years."]),
    "hollow": (["Mudsnout", "Snare-Cut", "Hollow-Run", "Gnoll-Chewed", "Trapper's"],
               ["Dog-teeth marks along one edge.", "Stolen from a trapline, badly worn since.",
                "It stinks of wet gnoll. It also works.", "Patched with somebody else's leather."]),
    "naze": (["Naze", "Fence's", "Stolen", "Dalaran-Marked", "Cutpurse"],
             ["No maker's mark, which is the selling point.", "Someone filed the old owner's crest off.",
              "It passed through three hands this month.", "Worth more than it looks. That is deliberate."]),
    "nethander": (["Nethander", "Stead-Breaker", "Ogre-Hide", "Millstone", "Thick-Skull"],
                  ["Cut down from something made for much longer arms.", "A human could make a cloak from the offcut.",
                   "Dented outward, which takes some doing.", "The stead built it. The ogres kept it."]),
    "dungarok": (["Dun Garok", "Stormpike", "Mountaineer's", "Gate-Warden's", "Hold-Cut"],
                 ["Dwarven make, and it shows in the balance.", "Cut square, like everything in that hold.",
                  "Stormpike grey, with the fort's mark at the collar.", "Heavier than it has any right to be."]),
    "durnholde": (["Durnholde", "Keep-Warden's", "Syndicate", "Alterac", "Undercroft"],
                  ["Grey beneath the violet paint, if you scratch it.", "Alterac work, re-cut by someone with less patience.",
                   "The keep held a Warchief once. It holds less now.", "Damp from the undercroft, and always will be."]),
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


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None, **engine):
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


# WRITING STANDARD (Kyle, this pass): no "kill X of Y down by the Z". The accept line is a PERSON TALKING and
# the numbers live inside what they say, not instead of it. Every quest carries a piece of why Hillsbrad is
# what it is - Alterac sold the Alliance out in the Second War and its nobility became the Syndicate; Lordaeron
# fell and this valley is the farmland that did not; Thoradin's Wall was raised by the first human empire and
# has outlived every kingdom since; Thrall was a boy in Durnholde. The player-is-not-from-here tension appears
# in FOUR of the forty-five, never as the default tone (see claude/quest_writing_guide.md).

# =========================================================================================================
# WESTERN HILLSBRAD - 20-25. Green country after the blight, and still worked by living people.
# =========================================================================================================
CMDR, QM, APOTH, DG_W = ("hbw_southpoint_commander", "hbw_southpoint_quartermaster",
                         "hbw_southpoint_apothecary", "hbw_southpoint_deathguard")
PASS, OUTRIDER, AGENT, POACHER = "hbw_pass_scout", "hbw_road_outrider", "hbw_fields_agent", "hbw_fields_poacher"
FSCOUT, HERDER, TIDE_W, FORAGER = "hbw_fields_scout", "hbw_pasture_herder", "hbw_strand_tidewatcher", "hbw_orchard_forager"
CASTAWAY, SPY, SABO = "hbw_purgation_castaway", "hbw_southshore_spy", "hbw_southshore_saboteur"
OVERSEER, SURVEYOR = "hbw_mine_overseer", "hbw_mine_surveyor"


def western():
    A = []
    A.append(Q("hbw_green_country", "Green Country", PASS, HBW, 20, 21, "southpoint",
        "Silverpine ends at a line you can see from the saddle: pine and blight on one side, barley on the "
        "other. Lordaeron fell and took its farmland with it, all but this valley. Aelin Frost has held the pass "
        "for two years and watched every courier stop dead at the top of the road to look at the colour of it.",
        [explore(HBW, 48, 24, 7)],
        "Everyone stops. I did. Two years dead and the first green I'd seen since, and I stood there like a "
        "fool.\n\nGo down and get it over with. The square tower with our banner is Southpoint - Commander "
        "Rethven holds it, and she'll want to know what the pass road looks like behind you.",
        "You stopped. Don't apologise for it. The day I meet someone who walks past that view without pausing "
        "is the day I stop trusting my own eyes.", "hbw_worgs"))
    A.append(Q("hbw_worgs", "What Walks the Milestones", DG_W, HBW, 20, 22, "southpoint",
        "Worgs on the pass road are ordinary. Worgs that work the same stretch at the same hour are not. Orlin "
        "has lost two couriers in a month, both on the run between the pass and the tower, both within an hour "
        "of dusk, and he has stopped calling it bad luck.",
        [k("Worg Prowler", 8, HBW)],
        "They hunt the verges, so take the crown of the road and make them come out to you. Eight should do it - "
        "I'm not standing here counting for you.\n\nAnd mark where they've been bedding. A worg that beds within "
        "sight of a road has stopped being a wolf. It's become a picket, and pickets get posted by something.",
        "Bedded in sight of the milestones, all of them. So somebody's feeding them, or somebody's training "
        "them. Neither answer lets me sleep, and I don't sleep anyway."))
    A.append(Q("hbw_ram_horns", "Horn and Hoof", QM, HBW, 20, 22, "pastures",
        "Southpoint's glue, lamp-oil, buttons and bowstring nocks come off the same animal. Dreng could "
        "requisition them through the Undercity, and the requisition would come back in the spring, correctly "
        "stamped, for half what he asked.",
        [fetch("highland_ram_horn", 8)],
        "Eight horns off the foothill rams and I'll have oil in the lamps by Thursday.\n\nUnderstand what you're "
        "doing for me: I can write to Lordaeron and be answered in April, or I can send you up a hill. The "
        "Dark Lady gave us our freedom. Nobody thought to give us a supply line.",
        "Eight, and two matched. Signed for and counted twice, which means you're in my ledger now. That's a "
        "better place to be than most places in this valley."))
    A.append(Q("hbw_living_soil", "Something Living", APOTH, HBW, 21, 22, "fields",
        "Four years Jessel Vane has worked blighted earth, because blighted earth is what Tirisfal has. Then he "
        "crossed a ridge and found soil with roots in it. He has not said so to the Commander, but he has begun "
        "taking samples before anyone upriver decides green farmland is a problem that needs solving.",
        [fetch("hillsbrad_loam", 6)],
        "Six jars, six different fields, kept apart - the difference between them is the entire point, so don't "
        "fill all six from the nearest ditch. I'll know.\n\nAnd since you're not from here: what does soil smell "
        "like where you're from? Not a joke. I've been trying to remember what it's supposed to smell like and I "
        "find I can't, and I'd rather ask someone who hasn't had the chance to forget.",
        "Living. All six. Roots, mites, the lot.\n\nYou said yours smelled like rain on stone. I'm going to "
        "think about that for a while."))
    A.append(Q("hbw_militia", "The Militia Question", CMDR, HBW, 21, 23, "fields",
        "Twice a week Hillsbrad's militia walk up the tower road, stand at a respectful distance, look at "
        "Southpoint, and walk away. Rethven's orders say hold the tower. They say nothing about men who come to "
        "count her walls and never once draw.",
        [k("Hillsbrad Militiaman", 10, HBW)],
        "Ten of them, in the fields, and I want you to understand I've thought about this longer than it sounds.\n\n"
        "They're farmers with billhooks and a grievance, and the grievance is fair - we are standing in their "
        "valley. But they've been measuring my gate for a month, and men who measure a gate are deciding "
        "something. I'd rather they decided it with ten fewer.",
        "They'll send twenty next time. I know that. I'd rather have this conversation twice than have it once, "
        "at night, with the gate open."))
    A.append(Q("hbw_farmhands", "Billhook and Halberd", AGENT, HBW, 21, 22, "fields",
        "Sarra Dunwick's whole trade is knowing what a valley is doing before the valley announces it. What this "
        "one is doing is arming the people who bring in the barley, and calling it a harvest watch.",
        [k("Hillsbrad Farmhand", 10, HBW)],
        "Ten, out in the rows. But I don't want the count - I want what's in their hands when they go down.\n\n"
        "A billhook is a tool a frightened man picks up. A halberd is a thing somebody made, carried to a field, "
        "and put into his hands on purpose. If you find halberds out there, this stopped being a harvest watch "
        "before either of us arrived.",
        "Halberds. Six of ten.\n\nSomeone is arming this valley and it isn't Southshore's garrison - they'd keep "
        "the good steel for marines. That leaves a quartermaster with a grudge, or Alterac money. I'll find out."))
    A.append(Q("hbw_arrows", "Fletch Your Own", POACHER, HBW, 21, 23, "fields",
        "Tam Hollis takes a ram off the high pasture now and again, which the Marshal calls theft and Tam calls "
        "older than the Marshal. What he cannot do is make arrows fast enough to stay ahead of the wasps, the "
        "worgs and the patrols at once.",
        [craft("ww_rough_arrows", "Fletch rough arrows", 5)],
        "You've got hands and you've got a bench. Five batches of rough shafts and we'll call the ram I owe you "
        "square.\n\nI'll tell you what I tell the Marshal: my grandfather took rams off that hill when Alterac "
        "still had a king, and nobody's shown me the paper that changed it. They dissolved a whole kingdom up "
        "there and never once came down here to say who owns the sheep.",
        "That's my month. And you're a better fletcher than you are a liar - I watched you count the feathers."))
    A.append(Q("hbw_yeti", "Off the Snowline", HERDER, HBW, 21, 23, "pastures",
        "Maud Kellen has read weather off her animals for thirty years. Her rams have been bunching at the low "
        "fence for a week and refusing the top pasture, which means the yetis have come down early, which means "
        "the snowline has moved and the winter is going to be a bad one.",
        [k("Mountain Yeti", 6, HBW)],
        "Six, up where the grass goes thin, and go in daylight.\n\nI'll say this plain, because I've been told "
        "what you are: they tell me you get back up. If that's true then you can walk a gully I'd not send my "
        "own son up, and I'd be a liar if I said that didn't sit strange with me. Take the work anyway. I need "
        "the pasture more than I need to be comfortable about it.",
        "Rams spread back out by evening. That's how I know you did it, not because you said so.\n\nAnd you came "
        "back down the gully on your own feet. I notice that too."))
    A.append(Q("hbw_icehide", "Old Icehide", HERDER, HBW, 23, 24, "pastures",
        "One yeti has used the same gully for eleven years. It has cost Maud lambs, two dogs, a fence and most "
        "of her patience, and it is old enough now to be white around the muzzle. She has driven it off four "
        "times. She would like this to be the last conversation about it.",
        [boss("Old Icehide", HBW)],
        "Top gully, where the stream comes out of the rock. He won't run - he has never once run, and that's the "
        "thing I've never been able to explain to anyone. Eleven years and he has never run.\n\nTake the cloak "
        "off the peg by the door before you go. It was my husband's and it's seen that gully before.",
        "Eleven years.\n\nI thought I'd feel lighter. Keep the cloak - it's been up that hill twice now and come "
        "back down once with the business finished. It's earned a better owner than a peg.",
        exp=2200, gold=9000))
    A.append(Q("hbw_calder", "Field Marshal Calder", CMDR, HBW, 23, 24, "fields",
        "A farming valley with a Field Marshal is either a joke or a warning. Calder drills the militia in the "
        "barley with a real officer's sabre and a real officer's manner, and somewhere in the last month the "
        "farmhands stopped standing in a crowd and started standing in ranks.",
        [boss("Field Marshal Calder", HBW)],
        "He drills them in open ground where anyone can see, which is arrogance. He won't break and run, which "
        "isn't.\n\nI'd rather fight one officer than the hundred farmers he's six months from making. That's the "
        "whole of my reasoning and I'd say it to his face.",
        "He swore on the soil, they tell me. That's the oath the militia take here - not to a king, there isn't "
        "one left, but to the ground.\n\nThe ground kept its half. It usually does.",
        exp=2200, gold=9000))
    A.append(Q("hbw_murlocs", "The Count Keeps Rising", TIDE_W, HBW, 22, 23, "strand",
        "Nols has counted the Daggerspine on the western strand for three weeks. The count goes up every week. "
        "Murlocs do not breed that fast, which means they are not breeding - they are arriving, and he would "
        "like to know what from.",
        [k("Daggerspine Murloc", 10, HBW)],
        "Ten off the shingle, and while you're down there keep half an eye on the water behind them.\n\nThey "
        "come up the beach facing inland. Every one of them. Whatever they're running from is seaward, and I've "
        "been watching that water for three weeks and it has never once looked back at me.",
        "Ten down, and the count's still rising.\n\nThat's the answer, and it's the one I didn't want. They "
        "aren't taking the strand. They're being pushed onto it."))
    A.append(Q("hbw_harpooner", "Barbed Line", TIDE_W, HBW, 23, 24, "strand",
        "The Daggerspine work the shallows with a barbed harpoon on a line, and the barb is the whole problem - "
        "it does not come back out. Three of Nols's watch have gone off the shingle in a month and the line went "
        "with them each time.",
        [boss("Bloodtide Harpooner", HBW)],
        "North end of the strand, in the shallows where the shelf drops.\n\nDon't let it land. That's the only "
        "advice worth giving - a barbed head cannot be drawn back out, so whoever takes the first throw is "
        "fighting the rest of it anchored. Close the distance or stay well off it.",
        "You cut the line rather than pull it. Good. Three men's worth of sense, that, and it only cost us the "
        "three men to learn it.",
        exp=2200, gold=9000))
    A.append(Q("hbw_signet", "The Swollen Signet", "item:swollen_signet_ring", HBW, 23, 24, "purgation",
        "You turn the ring over in your palm. A good signet, silver, and it has been in salt water long enough "
        "that the finger it came off swelled around it before anything let go. The crest is a ship under three "
        "stars - a merchantman's mark, not a navy's. Someone on this coast will know it, and will wish they did "
        "not.",
        [deliver("swollen_signet_ring", "Bring the signet to Castaway Ilsa Roane on Purgation Shore")],
        "There is a woman camped above the tideline on Purgation Shore who came ashore off a wreck and never "
        "went inland. Start with her.",
        "A ship under three stars.\n\nThat's the Maiden's Grace. That's my ship, and that's Harl's hand it came "
        "off, because he was the only one of us with fingers fat enough to need it cut.\n\nKeep it. I've looked "
        "at that water for a month. I don't need something to hold while I do it.",
        turn_in_npc_id=CASTAWAY))
    A.append(Q("hbw_drowned", "They Came Up Wrong", CASTAWAY, HBW, 23, 25, "purgation",
        "Ilsa Roane swam ashore from the Maiden's Grace and sat on the shingle all night waiting for the rest of "
        "the crew. They did come up. Over the following week, one at a time, with the tide - and not one of them "
        "came up as themselves.",
        [k("Drowned Castaway", 10, HBW)],
        "Ten of them, along the tideline.\n\nSome will have faces I know. Do it anyway. And when you come back, "
        "don't tell me which ones - I've spent a month deciding not to find out and I'd like to keep the "
        "decision.",
        "You didn't tell me.\n\nI'll be honest, I half wanted you to. Thank you for being better at this than I "
        "was going to be.",
        requires_quests=["hbw_signet"]))
    A.append(Q("hbw_tidewrack", "The Tidewrack", CASTAWAY, HBW, 24, 25, "purgation",
        "Something is holding the Maiden's Grace on the bottom. Ilsa has seen it twice from the shingle: a mass "
        "of anchor chain, spar and hull moving under its own weight, dragging what is left of her ship further "
        "out with every tide.",
        [boss("The Tidewrack", HBW)],
        "High water, south end. You'll hear the chain before you see it.\n\nIt isn't a ghost and it isn't a "
        "beast. It's wreckage that got given a purpose by something, and it has been collecting my ship a piece "
        "at a time for a month. Take the purpose out of it.",
        "She can go down properly now. So can they.\n\nI'm walking inland in the morning. Thirty-one years at "
        "sea and I'm going to go and look at a field. Don't follow me and don't wave.",
        exp=2300, gold=9400, requires_quests=["hbw_drowned"]))
    A.append(Q("hbw_wasps", "Windfall", FORAGER, HBW, 22, 24, "orchard",
        "The Hillsbrad orchard still fruits, which after the last five years is very close to a miracle, and the "
        "wasps that have taken it are the size of a man's hand. Ned Quill would like the apples. Ned Quill would "
        "also like to keep his face.",
        [k("Orchard Wasp", 10, HBW)],
        "Ten in among the rows, and keep your chin tucked - they go for the eyes and they're clever about it.\n\n"
        "Every orchard between here and Lordaeron is ash or worse. This one came through. I'm not losing it to "
        "insects after it survived the end of a kingdom.",
        "Ten. I can get a ladder into the north rows for the first time since spring, which is the best news "
        "this orchard has had in a year."))
    A.append(Q("hbw_thistlewing", "Queen Thistlewing", FORAGER, HBW, 24, 25, "orchard",
        "A hive this size has a queen, and she is why the orchard has wasps the size of a hand instead of wasps "
        "the size of wasps. She has taken the old cider press at the orchard's heart and built into it.",
        [boss("Queen Thistlewing", HBW)],
        "Press house, dead centre of the rows. Her sting puts a grown man down for a slow count of ten, so be "
        "sure you're not standing anywhere stupid when it lands.\n\nMy father pressed in that building. I'd "
        "rather have it back than be sensible about this.",
        "Hive'll scatter inside the week. There'll be cider by autumn - first barrel's yours, and I'll not hear "
        "otherwise.",
        exp=2300, gold=9400))
    A.append(Q("hbw_southshore_watch", "Count the Hulls", SPY, HBW, 23, 24, "southshore",
        "Lia Marrow has watched Southshore from the treeline for a year and never once walked into it. It is one "
        "of the last living human towns left standing in the north, it knows it, and it has three hundred "
        "marines who know it too.",
        [explore(HBW, 96, 128, 8)],
        "Round the east side through the apple rows and get eyes on the dock itself. Not the wall - I can see "
        "the wall from here. The dock.\n\nGo unarmed and look poor. And be clear with yourself before you set "
        "off: if they take you, nobody is coming. I'll write it up as a loss and move my camp.",
        "How many hulls? ... That many.\n\nThen we aren't taking Southshore this year, nor next. I'll send that "
        "north and someone in the Undercity will be disappointed in a way that doesn't reach us. Good."))
    A.append(Q("hbw_harlow", "Bosun Harlow", SABO, HBW, 24, 25, "southshore",
        "Henk has burned the Southshore dock twice. Both times it was standing again inside a month, and both "
        "times the man who filled the work gangs that rebuilt it was a bosun called Harlow, who does not ask who "
        "wants the job.",
        [boss("Bosun Harlow", HBW)],
        "Harbour end, by da sheds. Cutlass and a blunderbuss, and he uses da blunderbuss first - so you close "
        "fast or you don't close at all.\n\nI burn da dock, dey build it. I burn it again, dey build it again. "
        "Dis time I take away da man who finds da hands.",
        "Hah! Now dey rebuild it a third time. Slower. Much slower, and dey pay more for it.",
        exp=2300, gold=9400))
    A.append(Q("hbw_east_road", "The Road East", OUTRIDER, HBW, 24, 25, "southpoint",
        "Kess has ridden the east road since Southpoint was taken and has reached the point of describing Tarren "
        "Mill from memory. Memory is not a report, and the stretch past the Foothills is long enough that a lone "
        "rider stops being a courier and starts being an opportunity.",
        [explore(HBE, 62, 32, 8)],
        "East, the whole length of it. You'll know Tarren Mill when you see the wheel - there's a mill on a "
        "diverted race and the race cuts the town clean in two. Report to Magistrate Pell at the gate.\n\nSixty "
        "years that wheel's turned. Lordaeron fell, the Scourge came through, the valley changed hands twice, "
        "and nobody on either side ever thought to stop the wheel.",
        "You saw it turning. Then you've been further east than most of this garrison, and you can stop taking "
        "my word for what's out there."))
    return A


# =========================================================================================================
# AZURELODE MINE - 23-26. A silver mine that drowned, and the only craft chain in the valley.
# =========================================================================================================
def azurelode():
    A = []
    A.append(Q("az_kobolds", "The Lower Works", OVERSEER, HBW, 23, 24, "azurelode",
        "Azurelode was the richest silver seam in the valley until the pumps stopped and the lower galleries "
        "went under in a night. The kobolds were in it inside the week. Grint Halloway has never been able to "
        "explain how a creature that cannot read a pump roster knew the pumps had failed.",
        [k("Azurelode Kobold", 10, AZ)],
        "In through the adit in the western rock, and mind the standing water - it's deeper than the light makes "
        "it look and it does not drain anywhere.\n\nTen should clear the upper galleries. They'll be back. "
        "They're always back. I'd settle for walking my own mine without a torch in one hand and an axe in the "
        "other.",
        "Ten, and I got as far as the second landing without stopping. That's further than I've managed since "
        "midsummer."))
    A.append(Q("az_survey", "What the Water Took", SURVEYOR, HBW, 23, 25, "azurelode",
        "Pell Iversen surveyed Azurelode the year before it flooded. His chart is now the only record of what "
        "lies under the sump, which makes it worth rather more than the mine and a good deal more than Pell.",
        [explore(AZ, 56, 24, 7)],
        "The Silver Face, at the top of the workings - you'll know it, the rock goes blue-violet the moment a "
        "lamp touches it.\n\nWhat I need is whether the causeway still stands. My chart says there's a spine of "
        "dry rock running to the Face. If the chart's right, the seam is reachable and this is a mine again. If "
        "it's wrong, it's a lake with a door.",
        "Still standing. Then the chart holds and the Face can be worked.\n\nDon't tell the Overseer yet. He'll "
        "put men down there tomorrow and I'd like to know what else is down there first."))
    A.append(Q("az_prospectors", "Measuring a Drowned Mine", SURVEYOR, HBW, 24, 25, "azurelode",
        "There are Syndicate men in the flooded galleries and they are not digging. They are measuring - "
        "sounding the depth, chalking the walls, running chain along the sump. There is exactly one reason to "
        "measure a drowned mine that carefully, and it is to work out what draining it would cost.",
        [k("Syndicate Prospector", 8, AZ)],
        "Eight, below the causeway. You'll hear the chain before you see the lamps - they sound the depth every "
        "ten paces and log it.\n\nAlterac sold the pass to the Horde in the Second War and the Alliance "
        "dissolved the kingdom for it. The lords scattered into these hills with nothing. This is what nothing "
        "looks like when it finds a silver seam it used to own.",
        "They were chalking depths on the wall in a hand I recognise from estate maps. That's not a bandit "
        "camp's work. Somebody up there still thinks of this valley as property."))
    A.append(Q("az_silver", "Smelt It Yourself", OVERSEER, HBW, 24, 25, "azurelode",
        "There is no sense hauling ore to Tarren Mill when the mine's own furnace sits a full six feet above "
        "the waterline and has done all along. Halloway wants bars, not baskets, and he would like to know the "
        "person bringing them can tell silver from tin.",
        [craft("bar_silver", "Smelt silver bars", 5)],
        "Cut it off the Face and smelt it - my furnace, or any forge in the valley, I don't care whose.\n\nFive "
        "bars. Silver, mind. I've had three men bring me tin this season with a straight face, and tin out of a "
        "mine called Azurelode is a special sort of insult.",
        "Five, and all five silver.\n\nYou'd be amazed how rarely that sentence gets said down here.",
        requires_quests=["az_survey"]))
    A.append(Q("az_grimewick", "Grimewick the Drowned", OVERSEER, HBW, 25, 26, "azurelode",
        "The pump house has a kobold foreman in it. He had a hammer he used to beat the pumps back into working "
        "whenever they seized, and he was still beating them when the water came over the sill. He has not "
        "stopped since, and the pumps have not started.",
        [boss("Grimewick the Drowned", AZ)],
        "Pump house, west of the sump.\n\nHe took a candle down into a gallery full of pump gas, which is how "
        "the whole thing started, and the gas is what killed the shift. Thirty years I've blamed the engineers. "
        "Turns out it was one kobold and a candle, and he's still holding the candle.",
        "He was still hammering. I could hear it from the second landing and I'd convinced myself it was the "
        "water in the pipes.\n\nIt was never the water.",
        exp=2340, gold=9750))
    A.append(Q("az_ashlan", "Overseer Ashlan Silvervein", OVERSEER, HBW, 25, 26, "azurelode",
        "Halloway has a predecessor. Ashlan Silvervein ran Azurelode the night the pumps failed, ordered the "
        "lower galleries worked through it, and went down with the shift he refused to call back. He is at the "
        "Silver Face. He is still overseeing. Even the kobolds will not go near him.",
        [boss("Overseer Ashlan Silvervein", AZ)],
        "The Face itself. He carries a mattock with silver worked into the head - a waste of good silver, and he "
        "knew it, and he had it made anyway.\n\nI've had his job two years. I'd rather not have it this "
        "literally, and I'd rather the men stopped asking me whether he'd have called them back.",
        "Would he have called them back? I've been asked that question in every tavern between here and the "
        "pass.\n\nHe was still standing at the Face with the water up to his chest. I think that's the answer.",
        exp=2340, gold=9750, requires_quests=["az_silver"]))
    return A


# =========================================================================================================
# EASTERN HILLSBRAD - 23-29. Held outright, and every road out of it was somebody's kingdom once.
# =========================================================================================================
MAG, WREN, QM_E, KOLT = "hbe_mill_magistrate", "hbe_mill_apothecary", "hbe_mill_quartermaster", "hbe_mill_deathguard"
CARAVAN, HUNTER, GATE_SCOUT = "hbe_mill_caravan_master", "hbe_mill_hunter", "hbe_west_gate_scout"
TRAPPER, E_OUTRIDER, VESS = "hbe_hollow_trapper", "hbe_west_outrider", "hbe_naze_infiltrator"
FALK, VASK, STEAD = "hbe_durnholde_watcher", "hbe_durnholde_scholar", "hbe_stead_outrider"
SAPPER, TIDE_E, SENTRY = "hbe_garok_sapper", "hbe_strand_tidewatcher", "hbe_wall_sentry"


def eastern():
    A = []
    A.append(Q("hbe_the_gate", "The Gate at Tarren Mill", GATE_SCOUT, HBE, 23, 24, "millrace",
        "Pria Halm holds the west end of the trunk road. Everything that reaches the east half of Hillsbrad "
        "passes her first, and she has got it down to about four seconds - a look at the boots, a look at the "
        "eyes - whether a traveller is going to make the gate or be found on the verge.",
        [explore(HBE, 62, 30, 7)],
        "East along the trunk road to the mill square. Magistrate Pell holds the gate; through it is the town "
        "itself.\n\nWhen you get there, mind the race. It's a cut channel, it's deep the whole way, and there "
        "are three bridges and no fourth. People try the water about twice a year and the wheel gives them back "
        "about a week later.",
        "You made it. I had you as a maker - boots were right and you looked at the treeline instead of the "
        "road.\n\nFour seconds. I'm rarely wrong and I'd rather not start now.", "hbe_bandits"))
    A.append(Q("hbe_bandits", "A Toll, Not a Robbery", KOLT, HBE, 23, 24, "naze",
        "The Syndicate have stopped robbing the eastern roads and started owning them. Kolt does not much mind "
        "robbery - robbery is weather. What he minds is that the same three bends have been manned at the same "
        "hours for a fortnight, because that is not banditry. That is a toll, and a toll means administration.",
        [k("Syndicate Bandit", 10, HBE)],
        "Ten, off the eastern roads. Violet sashes, and nothing they carry has a maker's mark on it - they file "
        "them off, every piece.\n\nTake the sashes if you want my thanks in writing. The colour's Alterac's. "
        "They've no kingdom to wear it for and they've kept wearing it anyway, which tells you what we're "
        "dealing with better than I can.",
        "Ten, and the bends are clear.\n\nThey'll be manned again by the new moon. Somebody is paying wages, and "
        "men who draw wages come back."))
    A.append(Q("hbe_consignment", "The Flour Consignment", CARAVAN, HBE, 23, 25, "millrace",
        "Ovid Thane runs the carts - flour west out of Tarren Mill, reagents back east - twice a month without "
        "fail for six years. The last two runs west did not arrive. He has worked out that the Syndicate have "
        "learned what a cart looks like, and he would like to try something that does not look like one.",
        [deliver("mill_flour_consignment", "Carry the consignment to Quartermaster Ivek in the Hillsbrad Fields")],
        "Four sacks, sealed with my mark, and they go on your back rather than on an axle. West road all the "
        "way to the forward post in the fields - ask for Ivek, he's expecting a cart and he'll be delighted.\n\n"
        "Don't set it down. Not to rest, not to fight, not for anything. A sealed consignment that touches the "
        "ground is a consignment somebody can swear was opened.",
        "My mark, unbroken, and Ivek's countersign. First flour to reach the fields in two months.\n\nI'm going "
        "to send the next one the same way and let the carts go out empty as bait.",
        grant_items=carry("mill_flour_consignment", "Sealed Flour Consignment",
                          "Four sacks of Tarren Mill flour under Ovid Thane's seal. Heavier than it looks, and "
                          "the seal is the point."),
        turn_in_npc_id="hbw_fields_quartermaster"))
    A.append(Q("hbe_worgs", "Hedgerow Work", HUNTER, HBE, 23, 25, "hollow",
        "Dell Varrow was gamekeeper on this land when it had a lord worth keeping game for. He knows every "
        "hedgerow between the mill and the hollow, which is how he knows that every one of them currently has "
        "something living in it that did not use to.",
        [k("Worg Prowler", 8, HBE)],
        "Eight, in the hedges between the road and the hollow.\n\nThey run in threes. That's not a rule of "
        "thumb, it's how they're built - one shows itself, one circles, one waits. If you've found one you've "
        "found three, and the third is behind you. Count to three before you swing and you'll be fine.",
        "Eight. And you counted before you swung - I could tell from how few of them got round you.\n\nMost "
        "people don't. Most people learn on the second worg, if they get one."))
    A.append(Q("hbe_ditch_samples", "Uphill of the Vats", WREN, HBE, 24, 25, "millrace",
        "Field Apothecary Wren samples the ditches east of the mill so the apothecaries inside the walls do not "
        "have to. For a month the ditches have been running with something that is not runoff, and the stretch "
        "it is worst in lies uphill of the vats - which rules out the one explanation everybody had ready.",
        [fetch("east_ditch_sample", 6)],
        "Six samples - and not jars of ditchwater, I can fill those myself. Take them off the worgs that drink "
        "there. Whatever is in that water is in their coats and their gut, and a creature that has been "
        "drinking it for a month is a better record of it than anything I could dip.\n\nAnd before you "
        "ask: yes, I know what we do here. That's exactly why I want to be certain it isn't us. If it is, I'd "
        "rather find it than have a farmer find it.",
        "Uphill. All six, and the worst of them a half mile above the vats.\n\nSo it isn't us. Which means I "
        "have to go and tell the Society that something else is in this water, and they are going to be very "
        "disappointed in me for being right."))
    A.append(Q("hbe_gnolls", "They Left Me the Stakes", TRAPPER, HBE, 23, 25, "hollow",
        "Gus Mirren has run a trapline in Mudsnout Hollow for eleven years. Last month the gnolls took the "
        "whole of it - snares, wire, bait, the lot - and left the stakes standing in the ground in a neat row, "
        "which he has chosen to take personally and is entirely right to.",
        [k("Mudsnout Gnoll", 10, HBE)],
        "Ten, in the hollow proper. They den in the low wet ground, so go in from the high side and let them "
        "come up to you.\n\nThey left the STAKES. Do you understand what that means? They didn't miss them. "
        "They pulled the line, coiled the wire, and left me the bits I'd have to dig out. That's not scavenging.",
        "Ten. Good.\n\nI've been doing this eleven years and I've never once been mocked by the wildlife. I'd "
        "like it on record that I'm handling it well."))
    A.append(Q("hbe_snares", "Eleven Years of Wire", TRAPPER, HBE, 24, 25, "hollow",
        "The snares the gnolls took were made by hand, one at a time, over eleven winters. Gus is realistic "
        "about how many will have survived a month in a gnoll den, and would like whatever is left.",
        [fetch("stolen_snare", 8)],
        "Eight would do me. They hang them up in the dens, which is insulting but at least it's tidy - you'll "
        "find them in bunches rather than scattered.\n\nThe wire's the thing. I can cut new stakes in an "
        "afternoon. Good wire comes up from Southshore twice a year if the road's open, and the road has not "
        "been open.",
        "Eight, and six still true. Better than I'd let myself hope for.\n\nThe wire alone is a season's work. "
        "I'll have a line in the ground by the week's end."))
    A.append(Q("hbe_shamans", "Rattle and Rain", TRAPPER, HBE, 24, 26, "hollow",
        "The Mudsnout have shamans now, which they did not have a year ago. Gus has watched them work from "
        "cover and is clear it is not posturing - the weather follows them down the hollow, and the worgs "
        "follow the weather.",
        [k("Mudsnout Shaman", 6, HBE)],
        "Six. You'll hear the rattles long before you see them - and so will everything else in the hollow, so "
        "once you start, don't stop to think about it.\n\nA year ago they were dogs with knives. Something has "
        "taught them, and taught them quickly, and I would dearly like to know what a gnoll pack had to trade "
        "for lessons.",
        "Six, and the hollow's drier today than it was yesterday.\n\nI'm not saying that proves anything. I'm "
        "saying I've lived here eleven years and I noticed."))
    A.append(Q("hbe_grik", "Chief Grik", MAG, HBE, 25, 26, "hollow",
        "A gnoll pack is weather. A gnoll pack with a chief is politics, and politics is the Magistrate's "
        "department. Grik has taken the Mudsnout from a nuisance that raids barns to a force that picks which "
        "barns, and in which order.",
        [boss("Chief Grik", HBE)],
        "Deep in the hollow, at the den mouth.\n\nHe carries a cleaver with a notch filed in it for every "
        "farmstead between the hollow and the road. I'm told he adds them himself, afterwards, in front of the "
        "pack. Count them when he's down - I need the number for the ledger and I don't want it secondhand.",
        "How many? ... Say it once more and then we'll neither of us repeat it.\n\nI'll enter it in the ledger "
        "and I'll make sure the ledger is somewhere the farm families never find it.",
        exp=2340, gold=9750))
    A.append(Q("hbe_spellbinders", "Wizards for a Scrap Camp", VESS, HBE, 25, 26, "naze",
        "Gavin's Naze is a fence's camp with delusions of being a guild. Vess has been inside it twice. The "
        "bandits do not trouble her - what troubles her is that the camp keeps spellbinders, and no fence "
        "anywhere needs a spellbinder unless somebody else is paying to put one there.",
        [k("Syndicate Spellbinder", 8, HBE)],
        "Eight. They hold the inner ring and they bind you in place before they do anything else, so go in fast "
        "and go in with someone.\n\nThink about the cost of this. A trained binder could sell his talent in any "
        "city still standing. Instead he is stood in a scrap camp in the Hillsbrad hills. Somebody is paying "
        "him enough to make that the better offer.",
        "Eight down, and that's the report: somebody in Alterac is funding wizards for a camp that fences "
        "stolen cutlery.\n\nThat's not a gang any more. That's a government with no country."))
    A.append(Q("hbe_gavin", "Gavin the Fence", VESS, HBE, 26, 27, "naze",
        "Everything stolen in this valley passes through Gavin's hands, and Gavin keeps a ledger - names, "
        "dates, and what was paid. Vess does not particularly want Gavin dead. Vess wants the ledger, and Gavin "
        "has made it clear those are the same errand.",
        [boss("Gavin the Fence", HBE)],
        "Centre of the camp. He's quick, he's quiet, and everything he owns opens without a sound - including "
        "the ground under his tent, so don't assume he's run if he vanishes.\n\nThe ledger will be on him. He "
        "doesn't let it out of reach and he never has, which is the single most useful thing about him.",
        "Names, dates, and what the Syndicate paid for each.\n\nThis is worth more than the camp, more than "
        "Gavin, and more than the last year of my work. Half these entries are paid out of an Alterac treasury "
        "that officially stopped existing fifteen years ago.",
        exp=2440, gold=10140))
    A.append(Q("hbe_ogres", "The Nethander Stead", STEAD, HBE, 26, 27, "nethander",
        "Four generations of Nethanders worked that stead, and they raised the barn in a single season with "
        "their own hands. The ogres took the whole holding in an afternoon and are now living in the barn, "
        "which Brann Odgar finds considerably more offensive than the taking.",
        [k("Nethander Ogre", 8, HBE)],
        "Eight, round da stead. Dey are slow and dey hit like a wall coming down, so keep moving and never let "
        "dem put you against da fences.\n\nI have no love for human farms. But dey built dat barn in a season "
        "and da ogres are using it as a privy, and dere is a difference between taking a ting and ruining it.",
        "Eight down, and dey are still in da barn.\n\nBut dere is more room in it now, and dey have started "
        "arguing about who sleeps where. Dat is how dis ends - not wit us."))
    A.append(Q("hbe_gorbash", "Gorbash the Thick", STEAD, HBE, 27, 28, "nethander",
        "The ogres have a leader, and at some point he took the stead's own millstone off its spindle to use as "
        "a thrown weapon. Brann has watched him do it. Brann would like it clearly understood that he has "
        "watched him do it, with his own eyes, more than once.",
        [boss("Gorbash the Thick", HBE)],
        "In da barn. He throws da millstone.\n\nI know how dat sounds. I have said it four times now and every "
        "time da face is da same. Watch his shoulders - dey drop before he lifts, and dat is all da warning "
        "anyone gets.",
        "Da millstone is back on its spindle. Took four of us to lift what he was throwing wit one hand.\n\n"
        "Nobody is going to believe dis report. I have stopped caring.",
        exp=2550, gold=10530))
    A.append(Q("hbe_riflemen", "The Road Below the Fort", SAPPER, HBE, 26, 27, "dungarok",
        "The Stormpike cut a fort square into the southern ridge and put riflemen on the road beneath it. Niall "
        "Crag's orders are to find a way into that fort that is not the front door, and he has found it "
        "difficult to survey a road he keeps being shot on.",
        [k("Dun Garok Rifleman", 10, HBE)],
        "Ten, along the south road.\n\nHere's the trick, and it cost me a hat to learn it: they sight for the "
        "length of the road and not one pace further. Get inside that and a rifle is an expensive club. The "
        "danger is the hundred yards before you're inside it.",
        "Ten, and I got a measuring chain out on that road this morning for the first time since I was posted "
        "here.\n\nThat's the whole of what I wanted. The fort can wait; the chain couldn't."))
    A.append(Q("hbe_ironbeard", "Sergeant Ironbeard", SAPPER, HBE, 27, 28, "dungarok",
        "The road patrol has a sergeant, and the sergeant is the reason ten riflemen volley instead of firing. "
        "Dwarven discipline is the only thing turning a picket into a problem, and discipline has a name and "
        "stands at the end of the line.",
        [boss("Sergeant Ironbeard", HBE)],
        "He calls the volley - you'll hear him before the first shot.\n\nBreak him and the rest shoot like men "
        "who are frightened, which they are. They're a garrison a very long way from Dun Morogh holding a ridge "
        "nobody in Ironforge has thought about in a decade.",
        "Dwarven make, that hammer, and it shows in the balance - you can feel where they put the weight.\n\n"
        "Keep it. I measure things. I've never once had cause to swing one.",
        exp=2550, gold=10530))
    A.append(Q("hbe_wall_watch", "Thoradin's Wall", SENTRY, HBE, 27, 28, "dungarok",
        "Thoradin's Wall was raised by Arathor - the first human empire, the one every kingdom since was carved "
        "out of - and it still closes the road into Arathi. Ada Rook watches the near face. She has never seen "
        "the far side and has never met anyone who has.",
        [explore(HBE, 138, 144, 8)],
        "South-east, and walk the near face end to end. Don't try the gap - there are ogres in it and they've "
        "been in it longer than I've been posted here.\n\nYou'll have seen a lot of new things since you came "
        "to this world. That wall was old when Lordaeron was founded. It was old when Alterac was founded. "
        "Everything you've watched fall this year was built in its shadow.",
        "Still shut.\n\nAn empire falls, then the kingdoms it made fall, and the wall outlives all of them "
        "without a garrison. There's a lesson in that and I have never once enjoyed it."))
    A.append(Q("hbe_teague", "Wall-Watcher Teague", SENTRY, HBE, 28, 29, "dungarok",
        "Somebody else watches the wall. Thirty years by the state of his gear, on a stretch of stone no army "
        "has come near in living memory, and he will not let anyone approach the gap - including, Ada has "
        "noticed, anyone who might be going there to open it.",
        [boss("Wall-Watcher Teague", HBE)],
        "At the gap. A border pike, long enough to keep Arathi on the far side of the stone, and he will not "
        "step back from it.\n\nThirty years is a long time to practise not stepping back. I've four years on "
        "this wall and I already understand him, which is the part that worries me.",
        "Thirty years on a wall nobody attacks, for a kingdom that doesn't exist, at a gap nobody wanted.\n\nI "
        "want it written down that I understood him. I don't want anyone writing down that I agreed.",
        exp=2650, gold=10920))
    A.append(Q("hbe_durnholde_watch", "Grey Beneath the Violet", FALK, HBE, 26, 27, "durnholde",
        "Durnholde Keep has now been held by the Syndicate for longer than it was ever held by Lordaeron, and "
        "Odrin Falk would like that said out loud more often than it is. Its watchmen patrol the bluff in "
        "Durnholde grey plate with Syndicate violet painted over the top of it.",
        [k("Durnholde Watchman", 10, HBE)],
        "Ten, on the bluff outside the walls. And scratch the paint on one before you come back.\n\nGrey "
        "underneath. Every single one. They haven't forged a breastplate in fifteen years - they're wearing a "
        "dead kingdom's kit with a dead kingdom's colours brushed over it, and they've been doing it so long "
        "the paint has worn through at the shoulders.",
        "Grey underneath. I know. I've known for two years.\n\nI keep sending people up there half hoping "
        "somebody will come back and tell me I'm wrong about it."))
    A.append(Q("hbe_thrall_cell", "Where the Warchief Was Kept", VASK, HBE, 27, 28, "durnholde",
        "Emeline Vask is a scholar in a garrison with no use for one. Her interest in Durnholde is not "
        "military. Thrall was held in that keep as a boy by the man who raised him to fight in a pit, and a "
        "fair share of everything the Horde has since become started inside those walls.",
        [explore(DH, 70, 72, 8)],
        "Through the fallen archway into the courtyard, and stand in the middle of it. That's the whole task.\n\n"
        "I'm aware how it sounds. You weren't here for any of it - you've no reason to care whose childhood "
        "happened in a ruin. But you can walk in there and come back out, and I can't, and I would like someone "
        "to tell me what the ground feels like.",
        "Smaller than you expected. Everyone says that, and everyone is surprised to be saying it.\n\nA war that "
        "crossed a world started in a yard you can cross in twenty paces. I'll be thinking about that tonight "
        "instead of sleeping, which is a shorter walk than it used to be."))
    A.append(Q("hbe_stillwater", "Warden Stillwater", FALK, HBE, 27, 28, "durnholde",
        "The Syndicate keep a warden on Durnholde's outer ground who wears a keep-guard's greatsword and a "
        "keep-guard's rank, both taken off the men who held the place before him, and uses the title as though "
        "it had been given rather than collected.",
        [boss("Warden Stillwater", HBE)],
        "Outer bailey, and he'll meet you in the open - he thinks of it as his ground and he's not entirely "
        "wrong.\n\nThe blade is a Durnholde greatsword, kept long after Durnholde fell. Bring it back when "
        "you're done. I'd like it to stop being his, and there's no one left alive it can be returned to.",
        "Grey beneath the violet, same as all of them.\n\nI'll hang it in the watch post. Not as a trophy - as "
        "a reminder that this keep had a garrison once, and they lost it, and nobody came.",
        exp=2550, gold=10530))
    return A


# =========================================================================================================
# TARREN MILL - 23-28. The hub. Every quest here points OUT of the town, because a town has no spawns -
# and because the point of Tarren Mill is that the two banks need things from a valley neither controls.
# =========================================================================================================
TM_GUARD, TM_INN, TM_STABLE, TM_FARRIER = ("tarren_mill_gate_guard", "tarren_mill_innkeeper",
                                           "tarren_mill_stablemaster", "tarren_mill_farrier")
TM_MILLER, TM_TRADER, TM_SMITH = "tarren_mill_miller", "tarren_mill_trader", "tarren_mill_smith"
TM_REAGENT, TM_BOWYER, TM_CHAPLAIN = "tarren_mill_reagent_seller", "tarren_mill_bowyer", "tarren_mill_chaplain"
TM_SLUICE, TM_FARMHAND, TM_APOTH = "tarren_mill_sluice_keeper", "tarren_mill_farmhand", "tarren_mill_apothecary"
TM_APPR, TM_VAT, TM_CMDR = "tarren_mill_apprentice", "tarren_mill_vat_tender", "tarren_mill_commander"
TM_SCOUT, TM_WATCH = "tarren_mill_scout", "tarren_mill_watchman"


def tarren_mill():
    A = []
    A.append(Q("tm_two_banks", "Three Bridges and No Fourth", TM_GUARD, TM, 23, 24, "millrace",
        "Hollis has the south gate, which means he gives the same speech eight or nine times a day and has "
        "pared it down to its working parts. The town is cut in half by a millrace. The west bank is the "
        "village. The east bank is the Royal Apothecary Society. People manage this badly.",
        [explore(TM, 35, 50, 7)],
        "Walk up to the market bridge and look at both banks before you do anything else. That's the whole "
        "errand and it saves me a conversation later.\n\nWest side is the old village - inn, forge, chapel, the "
        "mill. East side is the Society and their vats. Three bridges join them. There is no fourth, the water "
        "is deep the whole way, and the wheel does not care who you were.",
        "Now you've seen it you'll not need telling twice.\n\nThe ones who drown are never the ones who can't "
        "swim. They're the ones in a hurry who thought it looked narrow."))
    A.append(Q("tm_sluice", "What Fouled the Race", TM_SLUICE, TM, 24, 25, "millrace",
        "Pate's crank raises the sluice. Drop the gate and the wheel stops, the mill stops, the Society's vats "
        "go cold and every person on both banks remembers his name within the hour. For a week the race has "
        "been running slow and he has not dropped the gate, because he would like to know why first.",
        [fetch("race_fouling", 5)],
        "Something's choking the intake above the weir and it isn't weed. Bring me five of whatever you pull "
        "out of the grating.\n\nI've been doing this twenty-two years. I know what weed feels like on the rake "
        "and this isn't it, and I'd rather be the man who asked than the man who dropped the gate on a "
        "guess.",
        "That's not weed. That's not anything that grew in this valley.\n\nI'm keeping these. And I'm keeping "
        "my hand off that crank until somebody with more letters after their name tells me what they are."))
    A.append(Q("tm_miller_bands", "Iron for the Spindle", TM_MILLER, TM, 24, 25, "millrace",
        "Aldous Reed's family has milled here sixty years. In that time Lordaeron fell, the valley changed "
        "hands twice, and the dead took the east bank - and the wheel has not stopped for any of it. The "
        "spindle bands have, however, started to go, and a spindle band is not something you improvise.",
        [craft("bar_iron", "Smelt iron bars for the spindle bands", 4)],
        "Four bars of iron, smelted proper. Not bronze - I know what bronze does in a wet bearing and so will "
        "you after one winter.\n\nSixty years that wheel's turned. My grandfather kept it going through the "
        "Second War by swapping the bands out himself. I'd not like to be the Reed who let it stop over four "
        "bars of iron.",
        "Four, and good ones.\n\nShe'll turn another sixty on these. I'll not be here for it, but she will, and "
        "that's the arrangement we've always had."))
    A.append(Q("tm_innkeeper_pot", "Something for the Pot", TM_INN, TM, 23, 25, "pastures",
        "Mallory Dunn feeds both banks, which is a diplomatic position she never asked for and handles by not "
        "asking anybody which side they came off. The problem with feeding both banks is that one half of her "
        "custom eats and the other half watches, and the half that eats has opinions about mutton.",
        [fetch("highland_ram_haunch", 6)],
        "Six good haunches off the foothill rams, west past the Foothills. Ram, mind, not sheep - there's a "
        "difference and this room will tell me about it for a week.\n\nAnd take the west road, not the hollow. "
        "I've lost two suppliers to that hollow and I'd rather keep the one who can carry six.",
        "Six, and hung properly. You've done this before.\n\nRoom's yours tonight and I'll not ask which bank "
        "you'd rather drink on. Nobody asks that in my house."))
    A.append(Q("tm_smith_charcoal", "Charcoal, Not Coal", TM_SMITH, TM, 24, 25, "millrace",
        "Odrin Vance shoes the Society's horses and mends their cart axles and takes their money, and has "
        "stopped apologising for it to anyone who asks. A trade is a trade. What he will not do is burn the "
        "coal they keep offering him, because coal is wrong for fine work and always has been.",
        [craft("plank_oakheart", "Cut and season oakheart planks", 6)],
        "Six oakheart planks, cut and seasoned at a sawmill. I'll burn my own charcoal from them - it's the "
        "only way I'll know what went into it.\n\nThey keep sending me coal from Dun Garok's old workings. "
        "Cheaper, hotter, and it ruins a weld - you get a seam that looks perfect and opens in a year. I'll not "
        "put my mark on that for anybody's convenience.",
        "Oakheart, properly seasoned. I can tell by the weight before I've even split one.\n\nThat's a season "
        "of good work in the stack. And when the next cart of coal turns up, I'll have somewhere to point."))
    A.append(Q("tm_bowyer_yew", "Yew from the River Stand", TM_BOWYER, TM, 24, 26, "hollow",
        "Tess Aldren strings bows the way her father strung them, which means yew off the river stand and "
        "nothing else. The river stand is three miles out past the hedgerows and the hedgerows currently have "
        "worgs in them, which has made a familiar errand into an annual one.",
        [fetch("river_yew_stave", 6)],
        "The gnolls have been felling the river stand for den stakes. Six staves back off them - and look at "
        "the cut before you pick one up. Heartwood and sapwood both, or it's firewood and I'll say so.\n\n"
        "My father cut there, and his father. There's a mark on one of those trunks that's four generations of "
        "us deep. They're burning it to hold up a roof made of my snare wire.",
        "All six true, and every one of them off the right side of the trunk.\n\nFour generations of doing it "
        "one way, and a gnoll nearly ended it for kindling. I'll string the first tonight."))
    A.append(Q("tm_apprentice_jars", "Label Everything", TM_APPR, TM, 24, 25, "millrace",
        "Nilla Stitch labels every jar in the apothecarium, which is not the junior work it sounds like. A "
        "consignment came in from Gavin's Naze last month with half the labels soaked off in transit, and "
        "nobody in the building is willing to open an unmarked jar to find out what is in it.",
        [fetch("unmarked_society_jar", 7)],
        "Seven unmarked jars went out with the Naze consignment before anyone noticed. I need them back, and I "
        "need them back closed.\n\nI'm aware how this sounds. But the whole discipline is that you know what "
        "you're holding. An unlabelled jar in a Syndicate camp is somebody's accident waiting to be somebody "
        "else's epidemic.",
        "Seven, all closed, none of them opened.\n\nYou've no idea what a good day this is. I'll have them "
        "catalogued by morning and nobody will ever know they left."))
    A.append(Q("tm_chaplain", "The Chapel on the West Bank", TM_CHAPLAIN, TM, 24, 26, "millrace",
        "There is a chapel on the west bank and a living chaplain in it, in a town held by the Forsaken. Ewen "
        "Blackwood has never been told to stop and has never asked why. He buries the village's dead in ground "
        "the Society could want, and so far nobody has wanted it.",
        [fetch("chapel_grave_marker", 6)],
        "Six markers went missing out of the yard - stone ones, with names cut in them. Syndicate, most "
        "likely; cut stone sells.\n\nI'll say the thing nobody here says to you. You die and you get up again, "
        "and the people in my yard do not. I've no quarrel with you for it. But you'll understand why a man in "
        "my trade thinks about it when you walk past.",
        "Six names back in the ground where they were put.\n\nThat's all a marker is - a promise that somebody "
        "stays where they were laid. It's the only promise I've got left to keep and I'd rather keep it."))
    A.append(Q("tm_apothecary_reagents", "Reagents from the Hollow", TM_APOTH, TM, 25, 26, "hollow",
        "Lysbet Crane's vats run on things that have to be gathered rather than bought, and the Mudsnout gnolls "
        "have taken the hollow where most of them grow. She would rather send someone than explain to the "
        "Society why a quarter's work stalled over fungus.",
        [fetch("hollow_bloodcap", 8)],
        "Eight bloodcaps, out of the wet ground in Mudsnout Hollow. They grow where the water sits.\n\nCut "
        "them, don't pull them - the whole value is in the stem and you'll crush it if you're rough. And don't "
        "eat one on a dare. I've had that conversation twice and one of those people is still here, after a "
        "fashion.",
        "Eight, cut clean. That's a quarter's work secured and one fewer letter I have to write.\n\nMind the "
        "vats on your way out. What's in them isn't finished and it doesn't like being looked at."))
    A.append(Q("tm_vat_tender", "Stir It, Skim It, Log It", TM_VAT, TM, 25, 26, "durnholde",
        "Grusk tends the vats on the east bank and considers it the best thing to have happened to him since "
        "dying. The work needs a reagent the Society sources from Durnholde's undercroft, which has become "
        "difficult since the Syndicate started keeping the keep properly.",
        [k("Syndicate Spellbinder", 8, DH)],
        "Eight of their binders, inside the keep.\n\nThe Society used to send a cart to the undercroft twice a "
        "year and nobody minded. Now there are wizards on the gate. Twelve years dead and I've got a trade "
        "again - stir it, skim it, log it - and I'm not losing it because Alterac's leftovers found religion.",
        "Eight. The cart can go out again.\n\nYou'll not understand what that's worth. I was a cooper before. "
        "I'm a vat-tender now. It's near enough the same job and it's the only thing that is."))
    A.append(Q("tm_stable_worgs", "Horses Won't Cross at Night", TM_STABLE, TM, 24, 25, "hollow",
        "Brann Teague's horses will not cross the bridges after dark. He has tried leading them, blindfolding "
        "them and bribing them. They cross all day without complaint and refuse from dusk, and the only thing "
        "that has changed is the number of worgs working the hedgerows on the far side.",
        [k("Worg Prowler", 8, HBE)],
        "Eight out of the hedges east of the race. Then I'll try the bridge at dusk again and we'll see.\n\n"
        "Horses are clever animals and they're not clever in the way people think. They don't reason it out. "
        "They just know, and they're right more often than the men leading them.",
        "Led a pair across at last light with no trouble at all.\n\nSo it was the worgs. I'd rather it was the "
        "worgs than the other thing I'd started wondering about."))
    A.append(Q("tm_farrier", "Shoes for the Carts", TM_FARRIER, TM, 24, 25, "millrace",
        "Nell Marsh keeps half the town moving - hooves and hinges, as she puts it. The caravan runs west twice "
        "a month and the last two came back with the draught team lame, which she traced to shoes cut from the "
        "cheap bronze stock the Society bought in bulk.",
        [craft("bs_bronze_plate_boots", "Forge a set of heavy bronze plate", 2)],
        "Two sets of heavy bronze at the forge, and I'll cut the shoe stock off them myself - the plate's the "
        "right thickness and the Society's bar stock isn't.\n\nI know it's a strange way round. I'd rather "
        "ruin good plate than put another cart team lame on the west road.",
        "Right thickness, right temper. I'll have the team shod by the week's end.\n\nAnd next time somebody "
        "buys bar stock by weight instead of by trade, I'll be shown the invoice first."))
    A.append(Q("tm_commander_syndicate", "A Government With No Country", TM_CMDR, TM, 26, 27, "naze",
        "Vellis Thorne holds the middle of a valley with Alterac at her back and Southshore at her front, and "
        "of the two she loses more sleep over Alterac. Southshore is a garrison and behaves like one. The "
        "Syndicate is a dissolved kingdom's nobility with money, grudges and fifteen years of practice.",
        [k("Syndicate Spellbinder", 10, HBE)],
        "Ten of their binders, wherever you find them east of the mill.\n\nUnderstand what they are. Alterac "
        "let the Horde through the pass in the Second War and the Alliance dissolved the kingdom for it. The "
        "lords went into these hills with their titles and no land. They are not bandits. They're a court in "
        "exile, and courts in exile want their country back.",
        "Ten.\n\nThey'll replace them. That's the thing about a court - there's always another son. But it buys "
        "me a season, and a season in this valley is a long time.",
        exp=2440, gold=10140))
    A.append(Q("tm_scout_keep", "Eyes on Durnholde", TM_SCOUT, TM, 27, 28, "durnholde",
        "Mirren Vask walks the roads so the garrison does not have to guess. Durnholde is the one place he has "
        "never been able to report on properly, because the Syndicate hold the walls and he has only ever seen "
        "the keep from the bluff.",
        [explore(DH, 70, 100, 8)],
        "Through the fallen archway and into the gatehouse ground. Far enough to count what's standing. Not far "
        "enough to be counted yourself.\n\nThe keep is a ring - outer wall, inner keep, and a courtyard between "
        "them. If the inner keep is still sealed, they're holding it properly and we need a plan. If it's open, "
        "they're squatting and we need a day.",
        "Sealed. Of course it's sealed.\n\nThey've been in there fifteen years and they've kept the inner keep "
        "shut the whole time. That's not squatting. That's a garrison, and I'll report it as one."))
    return A


# =========================================================================================================
# DUN GAROK - 26-29. A Stormpike hold cut square into the ridge, and a crypt they will not discuss.
# =========================================================================================================
def dun_garok():
    A = []
    A.append(Q("dg_mountaineers", "Cut Square", SAPPER, HBE, 26, 27, "dungarok",
        "Niall Crag has his measuring chain on the road and has finally got close enough to look at the fort "
        "itself. His professional opinion, delivered with some bitterness, is that there is no weak point - the "
        "dwarves cut every room in that hold square and put a gate at every narrowing.",
        [k("Dun Garok Mountaineer", 8, DG)],
        "Eight of their mountaineers, inside the outer gate. I need the muster yard quiet long enough to "
        "measure it.\n\nAnd look at the walls while you're in there. No chamfer anywhere, no rubble fill, every "
        "corner a true corner. That's not a cave they tidied up. They cut a hold out of a mountain, square, on "
        "purpose, and I'd admire it more if I weren't trying to get into it.",
        "Measured. Twenty-two paces by sixty, and the gates line up to the inch.\n\nI've surveyed six keeps. "
        "This is the only one where I could find no mistake to work with."))
    A.append(Q("dg_brannic", "Gatewarden Brannic", SAPPER, HBE, 26, 27, "dungarok",
        "The outer gate has a warden and the warden is the reason the outer gate is a gate rather than a "
        "doorway. Brannic has held the threshold long enough that the Stormpike stopped posting a second man "
        "on it.",
        [boss("Gatewarden Brannic", DG)],
        "The outer gate. Bearded axe, a shield scarred in a band at exactly shoulder height, and in fifteen "
        "years that axe has only ever swung in one doorway.\n\nHe will not come out to you. He has never once "
        "come out. You'll have to go to him, in the one place he's had fifteen years to practise standing.",
        "He held the threshold until he didn't.\n\nThere's a measurement in that too, if you want it: a hold "
        "is only as deep as the man at its door is stubborn.",
        exp=2440, gold=10140))
    A.append(Q("dg_dunmar", "Rifle-Sergeant Dunmar", MAG, HBE, 27, 28, "dungarok",
        "The riflemen on the south road are trained, and the training has a name. Dunmar runs the barracks off "
        "the muster yard, and Magistrate Pell has worked out that killing riflemen on a road is a tax while "
        "killing the man who makes them is a solution.",
        [boss("Rifle-Sergeant Dunmar", DG)],
        "The barracks, east off the muster yard - there's a sally port up the east wall that reaches it "
        "without going through the inner gate.\n\nHe sights for the length of that yard and no further, same as "
        "his men, because he taught them. Inside that distance he's a man with an empty rifle and a sergeant's "
        "temper.",
        "Then the road patrol is a dozen frightened dwarves with guns and nobody to tell them when to fire.\n\n"
        "I'll take frightened. Frightened goes home eventually.",
        exp=2550, gold=10530))
    A.append(Q("dg_morgrin", "The Vault Door", MAG, HBE, 27, 28, "dungarok",
        "There is a door at the back of the Great Hall that the Stormpike keep shut, and a shrine-keeper "
        "standing in front of it who has made it his life's work. Nobody in the garrison will say what is "
        "behind it. Pell has decided that is itself the answer.",
        [boss("Shrine-Keeper Morgrin", DG)],
        "Past the Great Hall, at the vault door.\n\nA smith's hammer, blessed until it stopped being one, and "
        "a man who has stood in a doorway so long the dwarves have stopped mentioning him in dispatches. When "
        "a garrison stops writing a man down, it's because writing him down means explaining him.",
        "Open, then.\n\nAnd now we have to decide whether we want to know, which is a different question from "
        "whether we wanted it open.",
        exp=2550, gold=10530, requires_quests=["dg_brannic"]))
    A.append(Q("dg_korrin", "Thane Korrin Stonewatch", MAG, HBE, 28, 29, "dungarok",
        "Behind the vault door is a crypt, and in the crypt is a thane. He was buried in Dun Garok in an iron "
        "circlet by dwarves who swore to hold the ridge, and he did not stay buried, and the garrison above "
        "has spent a great many years not discussing the noise.",
        [boss("Thane Korrin Stonewatch", DG)],
        "The Crypt of Dun Garok, past the vault.\n\nStonewatch Greataxe, and a circlet of iron he was buried "
        "in. The oath was to hold the ridge - he is technically still holding it, and that is the single most "
        "dwarven sentence I have ever had cause to write in a dispatch.",
        "The Stormpike will not thank us and will not admit it happened.\n\nThey'll bury him again, deeper, "
        "and the next garrison will be told the noise is the wind. That's how a hold keeps a secret: badly, "
        "and for centuries.",
        exp=2650, gold=10920, requires_quests=["dg_morgrin"]))
    return A


# =========================================================================================================
# DURNHOLDE KEEP - 27-31. Where Thrall was kept, and where Alterac's last lord is squatting in the ruins.
# =========================================================================================================
def durnholde():
    A = []
    A.append(Q("dh_revenants", "The Undercroft Is Not Empty", VASK, HBE, 27, 28, "durnholde",
        "The Syndicate hold Durnholde's walls and courtyard. They do not go into the undercroft, and Emeline "
        "Vask finds that more interesting than anything else about the keep: a garrison with a cellar it will "
        "not use has a reason, and reasons are what she is for.",
        [k("Keep Revenant", 8, DH)],
        "Eight of whatever is down there. The stair is behind the Lord's Hall.\n\nThese were the keep's own "
        "garrison - Lordaeron's men, the ones who were here when it fell. They didn't leave. The Syndicate have "
        "simply built their camp on top of them and agreed not to go downstairs, which is the most honest thing "
        "I know about the Syndicate.",
        "Lordaeron livery under the rot on all eight. I thought so.\n\nThey held this keep, they lost it, and "
        "they have been underneath everyone who's held it since."))
    A.append(Q("dh_varth", "Sergeant-at-Arms Varth", FALK, HBE, 27, 28, "durnholde",
        "The gatehouse has a sergeant-at-arms with a gate-warden's halberd and an alarm bell, and the bell is "
        "the problem. Odrin Falk has lost two scouting parties to the keep and both of them to the same bell.",
        [boss("Sergeant-at-Arms Varth", DH)],
        "The gatehouse, first thing through the archway.\n\nHe'll sound the alarm before he fights - that's "
        "his whole function and he's good at it. If you want to get further into that keep than the bailey, "
        "the bell has to stop before the shouting starts.",
        "Quiet, then. For the first time in two years, quiet at the gate.\n\nGo further in while it lasts.",
        exp=2550, gold=10530))
    A.append(Q("dh_sable", "Houndmaster Sable", FALK, HBE, 28, 29, "durnholde",
        "The kennels on the keep's east side are the reason nobody has ever got across the bailey unseen. "
        "Sable's hounds learned the work faster than her recruits did, which she says to recruits, in front of "
        "the hounds.",
        [boss("Houndmaster Sable", DH)],
        "The kennels, east bailey, through the breach.\n\nShe sets the pack on first and fights second. Kill "
        "the handler and the pack is a dozen dogs with nobody shouting at them - they'll scatter inside a "
        "minute. Try it the other way round and you'll be fighting dogs until there are no more dogs.",
        "The pack went over the wall and didn't come back. Dogs are sensible.\n\nThat's the bailey crossable "
        "now, which is two years of my reports made obsolete in an afternoon. I'm delighted.",
        exp=2650, gold=10920))
    A.append(Q("dh_yvaine", "Magister Yvaine", TM_CMDR, TM, 28, 29, "durnholde",
        "The Syndicate's binders are trained, and training needs a trainer. Yvaine holds the west tower with a "
        "staff of Alterac work that somebody re-cut with less patience than the original maker had, and she is "
        "the reason a scrap camp in the hills can field wizards at all.",
        [boss("Magister Yvaine", DH)],
        "West tower, off the ring. One door, no other way out, which cuts both ways.\n\nShe's Alterac court - "
        "properly trained, properly taught, and reduced to teaching hedge-binders in a ruin. There'll be a "
        "ledger of names on her. Bring it. I want to know who she's been training and where they went.",
        "Names and postings, in a court hand.\n\nShe was training them and sending them out, and about half "
        "these postings aren't in Hillsbrad at all. This goes north tonight.",
        exp=2650, gold=10920))
    A.append(Q("dh_turnkey", "The Turnkey", VASK, HBE, 29, 30, "durnholde",
        "There was a gaoler in Durnholde, and a gaoler in Durnholde in those years means one thing. Emeline "
        "Vask would like him dealt with, and she has not entirely separated the scholarship from the rest of "
        "it, and she knows that about herself.",
        [boss("The Turnkey", DH)],
        "The undercroft, past the revenants. Thirty keys on a chain and he swings the lot as one.\n\nHe kept "
        "the cells. In this keep, in those years, there was one prisoner worth keeping and a boy doesn't hold "
        "his own keys. I'm aware that's not a military reason. I'm asking anyway.",
        "Thirty keys, and not one lock left in that cellar worth turning.\n\nIt isn't scholarship and I'll not "
        "pretend it was. Thank you for not making me explain it.",
        exp=2760, gold=11310, requires_quests=["dh_revenants"]))
    # ---- THE LINKEN GATE. Three quests, three different zones, and two of them are entirely optional on
    # their own - the Naze fence in Eastern Hillsbrad, the magister inside the keep, and Godfrey's remnant all
    # the way back in Silverpine South. Miss any one and the Baron is never offered at all.
    A.append(Q("dh_perenolde", "Baron Aliden Perenolde", TM_CMDR, TM, 30, 31, "durnholde",
        "Gavin's ledger named who paid. Yvaine's postings named who was sent. Godfrey's remnant, two zones "
        "back in Silverpine, named what a dispossessed noble will do to get a country back. All three threads "
        "run to one man sitting in the Lord's Hall of a keep his family never owned, holding a court for a "
        "kingdom that was dissolved fifteen years ago.",
        [boss("Baron Aliden Perenolde", DH)],
        "The Lord's Hall, at the heart of the ring. You've done the work that makes this possible and I'd "
        "rather you knew it: without the fence's ledger and the magister's postings I'd have sent you in to "
        "kill a squatter.\n\nAlterac sold the Alliance to the Horde and his father signed it. The Alliance "
        "dissolved the kingdom and left the family their titles, because titles cost nothing. This is what "
        "fifteen years of carrying a title and no country does to a man.",
        "It's finished.\n\nThe Syndicate won't end - there's always another cousin with a sash. But the man "
        "who could pay wizards and buy a valley's thieves is on the floor of a hall his family had no claim "
        "to, and the ledger, the postings and the name all go north together.\n\nYou walked three roads for "
        "this. I'll see every one of them is in the dispatch.",
        exp=3000, gold=12000,
        requires_quests=["hbe_gavin", "dh_yvaine", "sps_godfrey"]))
    return A


# =========================================================================================================
# INBOUND - five quests in OTHER zones that now point at Hillsbrad. Kyle: "we can also build quests to send
# people to Hillsbrad from other parts of the world." Each is appended to its own zone's file.
# =========================================================================================================
XP.update({17: 1080, 18: 1160})
GOLD.update({17: 4800, 18: 5100})

INBOUND = {
    "silverpine_south": lambda: [
        Q("sps_road_south", "The Road South", "sp_pyre_hearthwarden", "silverpine_south", 19, 20, "southpoint",
          "Godfrey's remnant is dealt with and the Hearthwarden has run out of reasons to keep anyone in "
          "Silverpine. South of the pyre the pines thin out, the blight stops at a line you can stand on, and "
          "the road goes down into a valley that still grows things.",
          [explore(HBW, 48, 24, 7)],
          "Go south. Down the pass, past the last of the pines, and keep going until the ground changes "
          "colour.\n\nThere is a tower called Southpoint at the bottom of it with our banner on it, and a "
          "commander in it who is short of everything including people. You have done what there is to do "
          "here. Hillsbrad has not run out of work in living memory.",
          "You saw it, then. The green.\n\nEveryone comes back up this road eventually and nobody ever "
          "describes it the same way twice. Go on - she needs you more than I do.",
          requires_quests=["sps_godfrey"]),
        Q("sps_ashes_south", "Ashes to the Apothecary", "sp_pyre_hearthwarden", "silverpine_south", 19, 20, "fields",
          "The Ashen Cult burned something in that hall that did not burn like wood, and the Hearthwarden has "
          "a phial of what was left. There is nobody in Silverpine qualified to tell her what it is. There is "
          "an apothecary at Southpoint Tower who has spent four years with nothing to work on but blight and "
          "would very likely open the phial in the road.",
          [deliver("pyre_ash_phial", "Carry the phial to Apothecary Jessel Vane at Southpoint Tower")],
          "Sealed, and it stays sealed. South to Southpoint Tower in Hillsbrad - ask for Vane.\n\nI will be "
          "plain: I do not know what is in it, which is precisely why it is going to someone who does. Do not "
          "open it to satisfy yourself on the road. People have.",
          "Silverpine pyre ash. In a sealed phial. For ME.\n\nYou have no idea how long it has been since "
          "anyone sent me a question instead of an order. Tell her it will take a week and that it will be "
          "worth the week.",
          grant_items=carry("pyre_ash_phial", "Sealed Phial of Pyre Ash",
                            "Grey ash from the Ashen Cult's hall, sealed under wax. It is faintly warm, which "
                            "ash a month old should not be."),
          turn_in_npc_id=APOTH, requires_quests=["sps_pyre_hall"]),
    ],
    "silverpine_north": lambda: [
        Q("spn_orchard_graft", "Grafts for a Living Orchard", "sp_orchard_warden", "silverpine_north", 17, 18, "orchard",
          "Every tree in the Silverpine orchard is rotted through at the root and the Warden has spent two "
          "seasons proving it cannot be reversed. What can be done is to take cuttings from the last clean "
          "wood and put them into stock that is still alive - and the nearest living orchard is a valley and "
          "a mountain range away, in Hillsbrad.",
          [deliver("orchard_graft_cuttings", "Carry the cuttings to Forager Ned Quill in the Hillsbrad Orchard")],
          "Wrapped in damp sacking, and keep them damp. South, past the Sepulcher road, down into Hillsbrad "
          "and east to the orchard there. A man called Quill works it.\n\nThey will not take in this soil. "
          "They might take in his. That is the entire plan and I am aware of how thin it is.",
          "Cuttings? From Silverpine?\n\nI'll be honest with you, half of these are dead already. But half of "
          "them aren't, and I've got rootstock that came through the end of a kingdom. We'll see what takes.",
          grant_items=carry("orchard_graft_cuttings", "Bundle of Orchard Cuttings",
                            "Green wood from the last clean trees in Silverpine, wrapped in damp sacking. They "
                            "must not be allowed to dry."),
          turn_in_npc_id=FORAGER),
    ],
    "silverpine_dungeons": lambda: [
        Q("sfk_annotated_page", "A Page Out of Shadowfang", "item:annotated_keep_page", "silverpine_south", 24, 25, "durnholde",
          "The page came off a Moonwalker and it is not Arugal's work. It is a survey - a keep, drawn in a "
          "neat court hand, with the inner ward measured and the garrison strength noted in the margin. The "
          "keep is not Shadowfang. Somebody in Alterac is paying for surveys of somebody else's walls, and "
          "somebody in Shadowfang was carrying one.",
          [deliver("annotated_keep_page", "Bring the page to Scholar Emeline Vask near Durnholde Keep")],
          "The hand is a court hand and the subject is a keep in Hillsbrad. There is a Forsaken scholar "
          "watching that keep from the bluff above it who will know exactly what she is looking at.",
          "Where did you - Shadowfang? A worgen was carrying THIS?\n\nThis is Durnholde. Measured, inner ward "
          "and all, in an Alterac hand. They have been surveying their own keep for someone else, or someone "
          "else has been surveying it for them, and I do not know which answer I like less.\n\nStay in this "
          "valley. There is work here now, and you have just made some of it.",
          turn_in_npc_id=VASK),
    ],
    "undercity": lambda: [
        Q("ucq_hillsbrad_writ", "A Writ for the Frontier", "uc_executor", "undercity", 24, 25, "millrace",
          "The Undercity signs writs and the frontier receives them, usually late and usually about something "
          "the frontier has already dealt with. This one is different: it is a standing authority for the "
          "commander at Tarren Mill to act in the valley without referring north, and the Executor has had it "
          "sitting on his desk for a month because signing it means admitting he cannot run Hillsbrad from "
          "here.",
          [deliver("royal_writ_hillsbrad", "Deliver the writ to Commander Vellis Thorne in Tarren Mill")],
          "South. Through Silverpine, down into Hillsbrad, east to a mill town cut in half by a water "
          "channel. Thorne holds it.\n\nThe writ gives her authority I would rather keep. I am sending it "
          "anyway, because the alternative is losing the valley by post.",
          "He signed it.\n\nI have been asking for this for two years and I had stopped expecting it. Do you "
          "know what this is? It is permission to stop waiting.\n\nThere is Alterac money in these hills, "
          "there are wizards in a scrap camp, and there is a man in Durnholde keeping a court. I can go after "
          "all three now without writing north first.",
          grant_items=carry("royal_writ_hillsbrad", "Royal Writ of the Frontier",
                            "A standing authority for the Tarren Mill garrison to act in Hillsbrad without "
                            "referring to the Undercity. Sealed, and heavier than paper should be."),
          turn_in_npc_id=TM_CMDR),
    ],
}

# ---- fetch and starter drops -----------------------------------------------------------------------------
# Every fetch target has to come off a creature (data/creatures/quest_drops.json is keyed by creature name),
# and every starter drop names the quest it begins. Starter drops only roll while that quest is unstarted and
# unlocked, so there are no dead stacks.
DROPS = {
    "Highland Ram": [
        ("highland_ram_horn", "Highland Ram Horn", "Heavy, ridged, and still warm at the base. Southpoint "
         "renders these for lamp-oil, glue and buttons.", 0.55),
        ("highland_ram_haunch", "Highland Ram Haunch", "Hill-fed mutton, dark and close-grained. The Tarren "
         "Mill common room can tell this from sheep at forty paces.", 0.5),
    ],
    "Hillsbrad Farmhand": [
        ("hillsbrad_loam", "Jar of Hillsbrad Loam", "A handful of field soil out of a seed bag, roots and "
         "mites and all. In Tirisfal this would be a miracle in a jar.", 0.5),
    ],
    "Worg Prowler": [
        ("east_ditch_sample", "Ditchwater Sample", "Scraped from the coat and gut of something that has been "
         "drinking the eastern ditches for a month. Cloudy, and it should not be.", 0.5),
    ],
    "Mudsnout Gnoll": [
        ("stolen_snare", "Stolen Snare", "Hand-twisted wire on a cut stake. Eleven winters of a trapper's "
         "work, hung up in a den as a trophy.", 0.5),
        ("river_yew_stave", "River Yew Stave", "Cut from the river stand for den stakes. Heartwood and "
         "sapwood both - whoever felled it did not know what they had.", 0.45),
        ("hollow_bloodcap", "Hollow Bloodcap", "A deep red fungus from the wet ground of the hollow. The "
         "value is all in the stem, so it has to be cut rather than pulled.", 0.5),
    ],
    "Mudsnout Shaman": [
        ("race_fouling", "Fouling from the Grating", "Pulled off the millrace intake above the weir. It is "
         "not weed, and it did not grow anywhere in this valley.", 0.6),
    ],
    "Syndicate Bandit": [
        ("unmarked_society_jar", "Unmarked Society Jar", "A sealed apothecary's jar with the label soaked "
         "clean off. Nobody in Tarren Mill is willing to open it to find out.", 0.45),
        ("chapel_grave_marker", "Chapel Grave Marker", "Cut stone with a name on it, taken out of the west "
         "bank chapel yard. Cut stone sells; names do not.", 0.4),
    ],
    # ---- starter drops: looting one of these begins the quest
    "Drowned Castaway": [
        ("swollen_signet_ring", "Swollen Signet Ring", "Silver, crested with a ship under three stars, and "
         "cut from a finger that had swollen around it.", 0.14, "hbw_signet"),
    ],
    "Shadowfang Moonwalker": [
        ("annotated_keep_page", "Annotated Keep Page", "A survey of a keep in a neat court hand, with the "
         "inner ward measured and the garrison strength noted in the margin. The keep is not this one.", 0.12,
         "sfk_annotated_page"),
    ],
}


# =========================================================================================================
def _write(path, quests, label):
    path.write_text(json.dumps({"quests": quests}, indent=2, ensure_ascii=False) + "\n")
    print(f"  {label:26} {len(quests):3} quests -> {path.relative_to(ROOT)}")


def _splice(zone_file, new_quests):
    """Drop any previous version of these quests from another zone's file, then append. Idempotent."""
    p = ROOT / f"data/quests/{zone_file}.json"
    d = json.loads(p.read_text())
    key = "quests" if "quests" in d else None
    rows = d[key] if key else d
    ids = {q["quest_id"] for q in new_quests}
    kept = [q for q in rows if q["quest_id"] not in ids]
    rows[:] = kept + new_quests
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
            item_id, name, desc, chance = it[0], it[1], it[2], it[3]
            rec = {"item_id": item_id, "name": name, "category": "quest",
                   "description": desc, "chance": chance}
            if len(it) > 4:
                rec["starts_quest"] = it[4]
            existing = next((x for x in bucket if x["item_id"] == item_id), None)
            if existing is None:
                bucket.append(rec)
                added += 1
            else:
                existing.update(rec)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"  quest_drops                +{added} new drops across {len(DROPS)} creatures")


def main():
    open_world = western() + eastern() + tarren_mill()
    interiors = azurelode() + dun_garok() + durnholde()
    print("Hillsbrad quests:")
    _write(OUT, open_world, "hillsbrad.json")
    _write(OUT_D, interiors, "hillsbrad_dungeons.json")
    for zone_file, fn in INBOUND.items():
        _splice(zone_file, fn())
    _drops()
    inbound = sum(len(fn()) for fn in INBOUND.values())
    print(f"\n{len(open_world) + len(interiors)} Hillsbrad quests + {inbound} inbound from other zones")


if __name__ == "__main__":
    main()
