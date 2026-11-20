"""
Rootwater Isle's quests (42-44), the World Tree's first map. Read by tools/build_rootwater_quests.py, which holds
them to every rule before anything is written. The brief is docs/worldtree_brief.md.

THE THREADS:
  The hungry tree: the sap makes what drinks it big and wrong (the crocolisks, the murlocs, the Rootmaw), and the
    bark has started to rot (the Rot-Mother). Tazjin hears the loa going hungry; Uzo measures the sap.
  The Bloodsail tap: the pirates hammer spigots into the roots and sell the sap, and they blew up Fizzle's winch.
  The Bloodscalp climb: the trolls who didn't come over want the tree, and they come up the north-west root.
  The falling sky: a bronze wing in the sand that nobody on the ground could have made. Fizzle can't place it; Marta,
    who came over from our world, can't either. It's the first piece of the thread that ends at the Crown.
  Out by both boats: word to Grom'gol's troll attache, and a letter across the sea to Zoram Strand.
  Up: the Root Stair, whose door opens with the Lower Boughs.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. Earth comes up from Marta.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

RW = "rootwater_isle"
GROMGOL, ZORAM = "gromgol", "zoram_strand"

# ---- the people at the landing
ZULA, TAZJIN, KALISA, FIZZLE = "rw_chieftain", "rw_witch_doctor", "rw_hunter", "rw_dockhand"
UZO, MARTA = "rw_herbalist", "rw_settler"
# ---- out on the island
GRIK, ZAELA, JINZO = "rw_ferryman_east", "rw_ferryman_west", "rw_scout_lagoons"
# ---- elsewhere (turn-ins only)
ZULJANA, ILLYEN = "gromgol_troll_attache", "zoram_boatwright"

HUB_GIVERS = {ZULA, TAZJIN, KALISA, FIZZLE, UZO, MARTA}
TRIBE_GIVERS = HUB_GIVERS - {MARTA} | {GRIK, ZAELA, JINZO}


def k(target, n, zone=RW):
    return kill(target, n, zone=zone)


def boss(target, zone=RW):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=RW, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Bark Lizard": [("rw_q_lizard_hide", "Bark Lizard Hide", "A flat, rough hide patterned exactly like the bark the "
                     "lizard lived on. Ka'lisa says it makes the best quiver leather there is.")],
    "Reef Shellcrusher": [("rw_q_rooted_shell", "Root-Threaded Shell", "A crab's shell with fine roots grown through "
                           "it like veins. The scouts use them as bowls.")],
    "Sap-Drunk Crocolisk": [("rw_q_sap_blood", "Sap-Thick Blood", "A stoppered gourd of crocolisk blood, thick and "
                             "faintly gold. It doesn't clot.")],
    "Rootbound Murloc": [("rw_q_root_fin", "Root-Grown Fin", "A murloc's fin with a root grown right through the "
                          "webbing. The root is still alive.")],
    "Goldensap Ooze": [("rw_q_living_sap", "Clot of Living Sap", "A clot of the ooze, still trying to move. Tazjin "
                        "says to carry it in a closed jar and not to look at it too long.")],
    "Bloodsail Sap-Tapper": [("rw_q_tap_ledger", "Bloodsail Tapping Ledger", "A greasy ledger of barrels tapped and "
                              "barrels sold, with prices that make Fizzle whistle.")],
}
#: a page a Bloodscalp war-climber carries starts a quest
STARTER_DROPS = {
    "Bloodscalp War-Climber": [("rw_q_climbing_plan", "Bloodscalp Climbing Plan", "A strip of hide painted with the "
                                "tree's roots and a line of red handprints going up the north-west one. Somebody's "
                                "planning a raid.", 0.12)],
}
STARTER_IDS = {"rw_q_climbing_plan": "rwq_the_plan_to_climb"}

_cyc = [11]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=RW, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, on the roads)
WING_SAND = (62, 36)            # the bronze wing on the north-west root's shoulder
STAIR_FOOT = (114, 48)          # the foot of the Root Stair
LAGOON_HOLE = (46, 107)         # the lagoon's deep hole
SOUTH_TIP = (89, 144)           # the end of the long south root
NE_TIP = (166, 14)              # the end of the north-east root
ROT_HEART = (146, 22)           # the heart of the Saproot Thicket
CAGES = (44, 30)                # the Bloodscalp's cages
TAP_LOOKOUT = (132, 86)         # the road up to the Bloodsail camp


def build():
    out = []
    A = out.append

    # =================================================================================== 1. OFF THE BOATS
    A(Q("rwq_off_the_boat", "Off the Boat", GRIK, 42, 42, "Boatman's",
        "Boatman Grik'zul rows the crossing from Grom'gol, and every passenger he brings over is supposed to report to "
        "Headwoman Zula at the landing. He's given you the manifest to carry up.",
        [deliver("rw_q_manifest", "Take Grik'zul's manifest to Headwoman Zula Rootcaller at Rootwater Landing")],
        "Everybody who comes off my boat goes up to the headwoman first, so she knows who's on her island. Take her "
        "the manifest, she's at the landing under the trunk, and you can't miss the trunk.",
        "You're the one Grik'zul wrote down as \"looks useful\". He doesn't write that often.\n\nWelcome to "
        "Rootwater, where the tree drinks the sea. Since the worlds came together we've had more newcomers off that boat "
        "than we know what to do with, and every one of them's going up eventually. Before you go up, I'll want your "
        "help down here.",
        turn_in_npc_id=ZULA,
        grant_items=carry("rw_q_manifest", "Grik'zul's Manifest", "A list of everyone who crossed from Grom'gol this "
                          "week, in a careful hand, with a remark beside each name.")))
    A(Q("rwq_crocs_at_the_pier", "Crocs at the Pier", GRIK, 42, 43, "Oarsman's",
        "The Sap-Drunk Crocolisks have started coming up under the Grom'gol pier, and one of them took an oar clean "
        "out of Grik'zul's hands last week.",
        [k("Sap-Drunk Crocolisk", 7)],
        "The Sap-Drunk Crocolisks have lost their fear of the boat. One took my oar right out of my hands, and I'd "
        "rather it was the oar than the hands next time. Thin them out round the lagoons.",
        "That's quieter water already. I'll row a little easier tonight.\n\nThey weren't like this before the tree came "
        "up out of nowhere. "
        "A croc used to be a croc. These ones look at you like they're deciding something."))
    A(Q("rwq_from_the_other_coast", "From the Other Coast", ZAELA, 42, 43, "Ferrywoman's",
        "Boatwoman Zaela rows the long crossing to Zoram Strand on Ashenvale's coast. The night elves there want to "
        "know what the tree is, and the headwoman has written them an answer.",
        [deliver("rw_q_letter_to_zoram", "Take Zula's letter to Boatwright Illyen at Zoram Strand")],
        "The night elves at Zoram keep asking my passengers what this tree is, and none of them can say. The headwoman's "
        "written them a proper answer. Take it across with me and give it to Boatwright Illyen on the pier.",
        "A letter from the trolls on the tree. I wondered when they'd write.\n\nWe see it from here on a clear "
        "evening, you know, a dark shape on the sea where the sun goes down. The Sentinels argue about whether it's "
        "a tree at all. I'll tell them it is, and that the people living in it are polite.",
        turn_in_npc_id=ILLYEN,
        grant_items=carry("rw_q_letter_to_zoram", "Zula's Letter to Zoram", "A letter sealed with a smear of gold sap, "
                          "addressed to whoever's in charge on the night elves' pier.")))
    A(Q("rwq_murlocs_under_the_oars", "Murlocs Under the Oars", ZAELA, 42, 43, "Rower's",
        "The Rootbound Murlocs have taken to following Zaela's boat out of the lagoons and grabbing at the oars. They "
        "aren't strong, but there are a lot of them, and the roots in them make them hard to shake off.",
        [k("Rootbound Murloc", 8)],
        "The Rootbound Murlocs follow my boat out and hang off the oars, and they've got roots growing through them "
        "that make them heavy. Clear them out of the lagoons for me before somebody goes over the side.",
        "Good riddance to them. The poor things.\n\nI pulled one off the oar last week and the root in its arm was "
        "still growing. Whatever's in that sap, I'm glad I don't drink it."))

    # =================================================================================== 2. THE HUNGRY TREE
    A(Q("rwq_twice_their_size", "Twice Their Size", KALISA, 42, 42, "Lagoon-Stalker's",
        "Huntress Ka'lisa has watched the lagoon crocolisks double in size since they started drinking the sap that "
        "seeps out of the roots, and they've stopped being afraid of the trolls.",
        [k("Sap-Drunk Crocolisk", 8)],
        "The Sap-Drunk Crocolisks in the lagoons are twice the size they were last year, and they've stopped running "
        "from us. A croc that isn't scared of you is a croc that's going to try something. Teach them to be scared "
        "again.",
        "That'll do for now. They'll keep growing, though, as long as they keep drinking.\n\nI don't blame them, "
        "really. If the sea round you started tasting of gold, you'd drink it too."))
    A(Q("rwq_lizard_hides", "Lizard Hides", KALISA, 42, 43, "Barkskin",
        "Bark Lizards live all over the island, and their hides look exactly like the bark they sleep on. Ka'lisa "
        "wants them for quivers before the climb.",
        [fetch("rw_q_lizard_hide", 8)],
        "Every hunter who goes up the tree needs a quiver that won't slip, and Bark Lizard hide grips like nothing "
        "else. You'll have to look hard for the lizards, because they're the colour of the bark. Bring me their "
        "hides.",
        "These are perfect. Half the climbers these days are newcomers who'd never held a bow before they crossed over, and "
        "nobody's going to drop an arrow off a branch with a quiver like this.\n\nThat matters "
        "more than you'd think. Up there, anything you drop, you don't see again."))
    A(Q("rwq_moths_round_the_lanterns", "Moths Round the Lanterns", KALISA, 42, 43, "Lanternwatch",
        "The Leafwing Moths come to the landing's lanterns at night, and their wing dust makes people itch for days. "
        "They're bigger than they should be too.",
        [k("Leafwing Moth", 8)],
        "The Leafwing Moths come for our lanterns every night, and they're the size of dogs now. Their wing dust gets "
        "into everything. Knock them down wherever you find them on the island.",
        "That's a few nights without the itch, at least.\n\nA moth the size of a dog. I keep thinking I'll get used "
        "to this place, and then something else grows."))
    A(Q("rwq_the_bloodscalp_climb", "The Bloodscalp Climb", KALISA, 43, 44, "Rootclimber's",
        "The Bloodscalp have made a war camp out on the north-west root, and their headhunters and axe-throwers "
        "come down it at night to take trolls off the edge of the landing.",
        [k("Bloodscalp Headhunter", 6), k("Bloodscalp Axe-Thrower", 6)],
        "The Bloodscalp never forgave the tribes who climbed this tree without them, and now they're after it for "
        "themselves. Their Bloodscalp Headhunters and Bloodscalp Axe-Throwers come down the north-west root at "
        "night. Go up the root and break their hunting parties.",
        "They'll think twice before they come down that root again.\n\nSome of the Highbough were Bloodscalp once. "
        "They left to climb the tree, and their old tribe calls them traitors. It's a family fight, which is the "
        "worst kind."))

    A(Q("rwq_measuring_the_sap", "Measuring the Sap", UZO, 42, 43, "Sapwatcher's",
        "Sapwatcher Uzo measures the World Tree's sap the way a healer measures a fever. He needs blood from the "
        "creatures that drink it most, to see how much of it they're carrying.",
        [fetch("rw_q_sap_blood", 6)],
        "The sap's the tree's blood, and I measure it, because somebody has to. The Sap-Drunk Crocolisks drink more "
        "of it than anything. Bring me their blood in gourds and I'll see how much gold's in it.",
        "Look at that. It doesn't clot, and it shouldn't be this colour.\n\nA little sap heals a cut. A cup makes "
        "a man strong. These beasts are drinking it by the barrel, and I don't think anything was meant to.",
        nxt="rwq_rootbound"))
    A(Q("rwq_rootbound", "Rootbound", UZO, 42, 43, "Rootbound",
        "The murlocs in the lagoons have roots growing through them now. Uzo wants to know whether the tree is "
        "feeding them or feeding on them.",
        [fetch("rw_q_root_fin", 6)],
        "The Rootbound Murlocs have roots growing right through their fins. I've got to know whether the tree is "
        "feeding them or feeding on them, and the only way to tell is to look at the roots. Bring me some of their "
        "fins.",
        "The roots are alive, and they're drinking from the murloc, not the other way round.\n\nThat's the first "
        "time I've seen the tree take instead of give. Tazjin will want to hear this, and he won't like it."))
    A(Q("rwq_whiskers_for_the_draught", "Whiskers for the Draught", UZO, 42, 44, "Herbalist's",
        "Uzo cuts the tree's sap with Khadgar's Whisker to make a draught that heals without making anyone grow. "
        "The herb grows on the island's roots and among the jungle.",
        [gather("herb_khadgar", 8, "Gather Khadgar's Whisker")],
        "I cut the sap with Khadgar's Whisker so it heals without doing anything else to you. It grows all over the "
        "island, along the roots and under the jungle. Bring me what you can pick and I'll keep the climbers "
        "supplied.",
        "That's a good pile. I'll have draughts ready by tomorrow.\n\nEvery troll going up takes three. Nobody's ever "
        "needed more than two, but they all want three."))
    A(Q("rwq_what_the_bloodsail_want", "What the Bloodsail Want", UZO, 43, 44, "Sap-Thief's",
        "The Bloodsail aren't tapping the roots for their own use. Uzo wants their ledgers, to find out who's "
        "buying the sap and what they're doing with it.",
        [fetch("rw_q_tap_ledger", 4)],
        "The Bloodsail Sap-Tappers write everything down, every barrel and every buyer. Get me their ledgers. I want "
        "to know who's buying the tree's blood by the barrel, and what they think it's going to do for them.",
        "Booty Bay, Ratchet, and a buyer they only call \"the Doctor\". That last one takes more than the others "
        "together.\n\nNobody needs that much sap for healing. Somebody's growing something, and I'd give a lot to "
        "know what."))

    A(Q("rwq_the_hungry_loa", "The Hungry Loa", TAZJIN, 42, 43, "Loa-Listener's",
        "Witch Doctor Tazjin says the loa of the tree has been hungry since the bark began to rot on the north-east "
        "root. He wants someone to go and see the rot for him.",
        [explore(*ROT_HEART, "See the rot at the heart of the Saproot Thicket")],
        "The loa of this tree answered us when the world broke and nothing else did, and I listen for it every night. Lately it's hungry. "
        "The bark's rotting out on the north-east root, past the Root Stair. Go and look at it for me and tell me "
        "what you see.",
        "Black blossoms and a smell like an old wound. That's what I was afraid of.\n\nA tree this size can lose a "
        "branch and not notice. This isn't a branch. It's starting at the root, and the root is where the tree "
        "drinks.", nxt="rwq_rot_on_the_root"))
    A(Q("rwq_rot_on_the_root", "Rot on the Root", TAZJIN, 43, 44, "Rotbane",
        "Things live in the rot now, eating the bark from the inside. Tazjin wants them cleared before the rot "
        "spreads up the trunk.",
        [k("Rot Crawler", 7), k("Bark-Borer Beetle", 7)],
        "The Rot Crawlers and the Bark-Borer Beetles are eating the tree from the inside where the bark's gone soft. "
        "The rot spreads wherever they chew. Clear them off the north-east root before it reaches the trunk.",
        "That slows it. It doesn't stop it, but it slows it.\n\nThe crawlers and the beetles didn't start the rot. "
        "They're just fat on it. Something else started it, and we'll have to find out what.",
        nxt="rwq_living_sap"))
    A(Q("rwq_living_sap", "Living Sap", TAZJIN, 43, 44, "Goldensap",
        "Out in the rot, the sap has started moving on its own. Tazjin wants a piece of the Goldensap Ooze, to "
        "understand what's waking up in the tree.",
        [fetch("rw_q_living_sap", 4)],
        "The sap in the rot has started crawling about on its own. The Goldensap Oozes are what the tree bleeds when "
        "it's sick, and I need to know what's alive in them. Bring me clots of it in a closed jar, and don't look at "
        "them too long.",
        "It's still moving. I'm going to put it in the dark for now.\n\nThe loa's in there, a little. Something's "
        "feeding on the tree's sickness and growing on it, and I think it's a mother of some kind.",
        nxt="rwq_the_rot_mother"))
    A(Q("rwq_the_rot_mother", "The Rot-Mother", TAZJIN, 44, 44, "Rot-Mother's",
        "At the heart of the rot, something has grown big on the tree's sickness. Tazjin calls it the Rot-Mother, and "
        "he wants it cut out of the tree.",
        [boss("The Rot-Mother")],
        "There's something at the heart of the rot that's grown big on the tree's sickness, and everything else in "
        "there's one of its children. The Rot-Mother has to be cut out. Find her on the north-east root and kill her.",
        "It's done now, and I felt the loa ease when she fell, as clear as a fever breaking.\n\nThe rot will heal now, slowly. "
        "Thank you. The tree will remember it, and so will the tribes."))

    # =================================================================================== 3. THE BLOODSAIL TAP
    A(Q("rwq_the_bloodsail_tap", "The Bloodsail Tap", ZULA, 42, 43, "Rootcaller's",
        "The Bloodsail have set up on the south-east root and hammered spigots into it. They're bleeding the tree for "
        "sap to sell, and Headwoman Zula wants them gone.",
        [k("Bloodsail Sap-Tapper", 7), k("Bloodsail Cutthroat", 5)],
        "The Bloodsail are hammering spigots into the south-east root and selling what runs out. Every barrel they "
        "fill's the tree bleeding. Kill their Bloodsail Sap-Tappers, and the Bloodsail Cutthroats who guard them.",
        "That'll cost them a few barrels. They'll be back, because sap pays, but they'll come back fewer.\n\nThe "
        "tree gave itself to us, and we don't sell it. That's the difference between a tribe and a crew.",
        nxt="rwq_tapmaster_grell"))
    A(Q("rwq_tapmaster_grell", "Tapmaster Grell", ZULA, 44, 44, "Tapmaster's",
        "The Bloodsail's sap camp is run by a man called Grell, who taps the roots himself and knows exactly how deep "
        "to go. As long as he's there, the camp will keep coming back.",
        [boss("Tapmaster Grell")],
        "Tapmaster Grell runs the Bloodsail camp, and he's the one who knows how to bleed a root without killing it. "
        "Without him they'd hit nothing but bark. Find him on the south-east root and end him.",
        "Grell's done, and the camp's going to be a lot less sure of itself.\n\nI'll have the tribes pull the "
        "spigots out tomorrow and seal the holes with clay. The tree heals faster than you'd think."))
    A(Q("rwq_word_to_gromgol", "Word to Grom'gol", ZULA, 42, 43, "Tribal Envoy's",
        "The Highbough Tribes aren't the Horde's, but Grom'gol is across the water and its Darkspear attache is "
        "family to half the landing. Zula wants Grom'gol to know what's happening on the tree.",
        [deliver("rw_q_word_to_gromgol", "Take Zula's word to Attache Zul'jana in Grom'gol")],
        "We don't answer to the Horde, but Grom'gol's across the water and Zul'jana's family to half of us. She "
        "should hear about the Bloodsail and the Bloodscalp from us, not from rumours. Take her this, and take the "
        "boat.",
        "Zula always did write like she was carving it in stone.\n\nThe Bloodsail tapping the tree, and the Bloodscalp "
        "climbing it. Grom'gol will keep an eye on the water between here and there. Tell her the Darkspear haven't "
        "forgotten who went up first, three years back when the tree came out of the reef.",
        turn_in_npc_id=ZULJANA,
        grant_items=carry("rw_q_word_to_gromgol", "Zula's Word to Grom'gol", "A message on a strip of bark, painted in "
                          "the Highbough's teal, for the Darkspear attache in Grom'gol.")))

    # =================================================================================== 4. FIZZLE AND THE FALLING SKY
    A(Q("rwq_paid_in_sap", "Paid in Sap", FIZZLE, 42, 43, "Winchwright's",
        "Fizzle Brasswinch built the tree's lifts and got paid in sap. Then the Bloodsail worked out what the sap is "
        "worth, and their powder monkeys blew up his best winch.",
        [k("Bloodsail Powder Monkey", 8)],
        "I built every lift on this tree, and the trolls paid me in sap. It was the best deal of my life, until the "
        "Bloodsail noticed. Their Bloodsail Powder Monkeys blew my best winch to splinters last night. Go and return the "
        "favour, and I'll owe you one.",
        "Ha, I'd have paid to watch that.\n\nThose monkeys are smarter than half the crews I've hired. Somebody taught "
        "them to light fuses, and I'd love to know who."))
    A(Q("rwq_cable_for_the_winch", "Cable for the Winch", FIZZLE, 42, 44, "Brasswinch",
        "Fizzle needs mithril for a new winch cable, because rope doesn't last on a lift that climbs a tree this "
        "size. There are veins of it in the rock between the roots.",
        [gather("ore_mithril", 6, "Gather Mithril Ore")],
        "Rope rots, and on a lift this high, rotten rope means a long fall. I want mithril for a new cable. There's "
        "ore in the rock between the roots if you've got a pick. Bring me some and I'll have the lift running again.",
        "That's enough for a cable and a spare. I'll have the winch turning by the end of the week. Since the merge, half "
        "my parts come from places I can't pronounce, so it's nice to have good honest mithril.\n\nNobody up there "
        "thinks about the cable until it's gone, and then it's all they think about, for about four seconds."))
    A(Q("rwq_the_wing_in_the_sand", "The Wing in the Sand", FIZZLE, 42, 43, "Skyward",
        "Something fell out of the sky onto the north-west root a few nights ago, a piece of bronze shaped like a "
        "wing, with a blue crystal next to it. Fizzle wants someone to go and look before the Bloodscalp find it.",
        [explore(*WING_SAND, "Find what fell on the north-west root")],
        "Something came down out of the sky a few nights ago, out past where the Zoram road bends north. The trolls "
        "say it's a bronze wing. I say nobody makes wings out of bronze, so go and look at it before the Bloodscalp "
        "do.",
        "So it's a wing after all. Bronze, engraved, and that crystal next to it was still humming when you got there.\n\n"
        "Here's the thing. I'm a goblin, and I know every workshop between Undermine and Gadgetzan. Nobody I know "
        "made that. Nobody I know could.",
        nxt="rwq_not_goblin_work"))
    A(Q("rwq_not_goblin_work", "Not Goblin Work", FIZZLE, 43, 43, "Starfallen",
        "Fizzle can't place the bronze wing. Marta Kowalczyk, who came over on the Zoram boat, built ships in our "
        "world before the merge, and Fizzle wants her opinion.",
        [deliver("rw_q_bronze_scrap", "Show the bronze scrap to Marta Kowalczyk at the landing")],
        "Marta built ships, back where she comes from, real ones with engines. If anybody on this island's seen "
        "something like that wing, it's her. Show her this piece I broke off it.",
        "This isn't from my world either, if that's what Fizzle's hoping.\n\nWe never made anything like it. The "
        "joins are too fine, and there's no seam where the crystal sits. Whoever made this was better than us, and "
        "better than the goblins. And it fell from up there.",
        turn_in_npc_id=MARTA,
        grant_items=carry("rw_q_bronze_scrap", "Engraved Bronze Scrap", "A piece of the fallen wing, engraved with "
                          "lines too fine to have been cut by hand. It's warm.")))

    # =================================================================================== 5. MARTA
    A(Q("rwq_the_view_from_here", "The View from Here", MARTA, 42, 43, "Wanderer's",
        "Marta came over on the Zoram boat to see the tree, and she never got back on. She wants someone to walk out "
        "to the ends of the roots with her, to see how far the tree has reached.",
        [explore(*SOUTH_TIP, "Walk to the end of the long south root"),
         explore(*NE_TIP, "Walk to the end of the north-east root")],
        "I came over to see the tree everybody was talking about, and I never left. I've been all over the landing, "
        "but I've never been out to the ends of the roots. Walk out along the south one and the north-east one for "
        "me, and tell me what you see.",
        "Sea on every side, and the roots still going under it.\n\nWhen I was a girl in Gdansk I used to watch the "
        "cranes at the shipyard and think they were the biggest things in the world. I'd love to bring my father "
        "here. I don't know where he is now, or if he came through at all."))
    A(Q("rwq_cages_on_the_root", "Cages on the Root", MARTA, 43, 44, "Cagebreaker's",
        "The Bloodscalp keep cages on the north-west root, and Marta's sure there's someone in one of them. Their "
        "war-climbers guard the camp from the branches above.",
        [explore(*CAGES, "Look into the Bloodscalp's cages on the north-west root"),
         k("Bloodscalp War-Climber", 6)],
        "There are cages up at the Bloodscalp camp, and last night I swear I heard someone calling for help in "
        "Polish. I know how that sounds. The Bloodscalp War-Climbers watch the camp from above. Go up there, kill "
        "them, and look in the cages. I'll owe you.",
        "The cages were empty, but somebody had scratched words into the bamboo, and they're words I know.\n\nWhoever it was got "
        "out, or got taken somewhere else. I'm not going to stop looking. Somebody from home was on this island, and "
        "I'd like to know who."))
    A(Q("rwq_censers_and_hexes", "Censers and Hexes", MARTA, 43, 44, "Hexbreaker's",
        "The Bloodscalp's witch doctors and shamans burn something in their censers that makes the landing's trolls "
        "sick, and the smoke drifts down the root at night.",
        [k("Bloodscalp Witch Doctor", 5), k("Bloodscalp Shaman", 5)],
        "The Bloodscalp Witch Doctors burn something in their censers that comes down the root on the night wind, and "
        "half the landing's been coughing for a week. Their Bloodscalp Shamans keep the fires going. Put them "
        "out, all of them.",
        "The wind's clean tonight. Everybody's sleeping without coughing for the first time in days.\n\nThe "
        "trolls took me in when I didn't have anything. This is the least I can do for them."))
    A(Q("rwq_zulgash_the_climber", "Zul'gash the Climber", MARTA, 44, 44, "Climber's",
        "The Bloodscalp war camp answers to Zul'gash, who climbed the north-west root first and means to climb the "
        "trunk next. As long as he lives, the Bloodscalp will keep coming up.",
        [boss("Zul'gash the Climber")],
        "Zul'gash the Climber leads the Bloodscalp on the north-west root, and the trolls say he means to go up the "
        "trunk next. If he does, there won't be a landing to come back to. Find him at the war camp and stop him.",
        "Zul'gash is dead, and the Bloodscalp will spend a while arguing about who climbs first now.\n\nThe headwoman "
        "says I can call myself one of the tribes if I want to. I think I might."))
    A(Q("rwq_the_plan_to_climb", "The Plan to Climb", "item:rw_q_climbing_plan", 43, 44, "War-Plan",
        "A Bloodscalp war-climber was carrying a strip of hide painted with the tree's roots and a line of red "
        "handprints going up the north-west one. It's a raid plan, and the headwoman should see it.",
        [deliver("rw_q_climbing_plan", "Bring the Bloodscalp climbing plan to Headwoman Zula at the landing")],
        "The hide shows the north-west root and a line of red handprints climbing it, past the landing and up the "
        "trunk. It's a raid plan, and you'd better get it to the headwoman at the landing.",
        "Up the north-west root, round the landing in the dark, and onto the trunk where the old stair was.\n\nWe'll "
        "put guards where these handprints are. You've just saved a lot of trolls a long fall.",
        turn_in_npc_id=ZULA))

    # =================================================================================== 6. THE LAGOONS
    A(Q("rwq_what_drinks_the_sap", "What Drinks the Sap", JINZO, 42, 43, "Lagoonwatch",
        "Scout Jinzo watches the lagoons from the south-west road. He wants someone to wade out to the deep hole in "
        "the lagoon, where the sap pools, and see what's living there.",
        [explore(*LAGOON_HOLE, "Wade out to the deep hole in the lagoon"),
         k("Reef Shellcrusher", 6)],
        "The sap pools in the deep hole out in the lagoon, and everything that's thirsty comes to drink there. Wade out and look at "
        "it for me. The Reef Shellcrushers will come at you in the shallows, so kill them as you go.",
        "So it's still there, and it's still growing. I can see the gold in the water from here at night.\n\nThe "
        "Rootmaw drinks there. The oldest croc on the island. If you're going to stay, you'll meet him eventually.",
        nxt="rwq_the_rootmaw"))
    A(Q("rwq_shells_for_the_scouts", "Shells for the Scouts", JINZO, 42, 43, "Shellscout's",
        "The scouts eat out of Reef Shellcrusher shells, and the shells out here have roots growing through them. "
        "Jinzo wants a few clean ones for the new scouts.",
        [fetch("rw_q_rooted_shell", 6)],
        "Every scout on the island eats out of a Reef Shellcrusher shell, and we're short of them. The crabs are all "
        "over the lagoon shallows. Bring me their shells, roots and all, and I'll scrape them clean.",
        "These will do. The roots come out with a good knife and some patience.\n\nThe old scouts say a shell with "
        "roots in it's lucky. The new ones say it's creepy. They're both right, and that's the trouble."))
    A(Q("rwq_the_rootmaw", "The Rootmaw", JINZO, 44, 44, "Rootmaw's",
        "The Rootmaw is the oldest crocolisk on the island, and it's been drinking from the roots since the tree first "
        "split the reef. It's covered in barnacles and roots now, and it's started taking trolls.",
        [boss("The Rootmaw")],
        "The Rootmaw was the first thing on this island to drink the sap, and it's been drinking ever since. It took "
        "two of our fishers last month. Find it in the Root Lagoons and kill it, before it gets any bigger.",
        "The Rootmaw's dead. I watched it go under from here, and it didn't come back up.\n\nThree years drinking "
        "from the roots. I almost feel sorry for it, but only almost."))

    # =================================================================================== 7. UP
    A(Q("rwq_the_root_stair", "The Root Stair", ZULA, 44, 44, "Highbough",
        "Headwoman Zula says you've earned the climb. The Root Stair runs up the trunk's east side to the Lower "
        "Boughs, and the first step is to stand at its foot.",
        [explore(*STAIR_FOOT, "Stand at the foot of the Root Stair")],
        "You've done more for this landing than most who come through. The Root Stair goes up the trunk on the east "
        "side, and it's the only way to the Lower Boughs that doesn't need a lift. Go and stand at the foot of it, "
        "and look up.",
        "Now you've seen it. It goes up further than you can see, and then further than that.\n\nThe tribes in the "
        "Lower Boughs will want to meet you, and the High Chieftain after them. When the way up's open, you'll be "
        "one of the first we send.",
        requires_quests=["rwq_the_rot_mother", "rwq_tapmaster_grell"]))
    return out
