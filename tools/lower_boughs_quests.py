"""
The Lower Boughs' quests (44-45), the World Tree's first lived-on tier, and the Knothollow's (the cave into the trunk).
Read by tools/build_lower_boughs_quests.py, which holds them to every rule before anything is written. The brief is
docs/worldtree_brief.md.

THE THREADS:
  Climbers from below: the Bloodscalp come up ropes at the end of the Great Bough. Elder Tal'vani and the south scout
    against them, ending at Ropemaster Vaz'jin; a knotted cord off a ropecutter tells where they'll climb next.
  The apes: the sap's made the west bough's apes big and mean. The bough-hunter's chain ends at Old Goldtooth.
  The Silkwood: the spiders web the east bridge. Bridgekeeper Ozzu's chain ends at Mother Lattice.
  The river: Rivercaller Jinda hears the sap in it. Her chain runs from the oozes to Sunscale, and into the trunk to the
    Amber Glut at the bottom of the Knothollow.
  The borers: they've eaten into a knot under the village. Tal'vani sends you in after Gnawmother Ixx.
  Sky-bones: the falling-sky thread from Rootwater. Scholar Vel'jani buys every piece that falls into the branches, and
    sends one down to Fizzle at Rootwater, who can't place it either.
  Aroha Tane, the transplant: an arborist from New Zealand who climbed for the view.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. Earth comes up more than it did
on the island (Aroha, and the trolls' word for transplants).
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

LB = "lower_boughs"
KH = "knothollow"
RW = "rootwater_isle"

# ---- Mossroof
ELDER, RAKAZ, JINDA, OZZU = "lb_elder", "lb_hunter", "lb_shaman", "lb_ropemaster"
VELJANI, AROHA = "lb_scholar", "lb_transplant"
# ---- out on the tier
MOZU, GRIZZIK, HALAJA, TIKORA = "lb_stairwarden", "lb_liftkeeper", "lb_scout_west", "lb_scout_south"
# ---- elsewhere (turn-ins only)
FIZZLE = "rw_dockhand"

HUB_GIVERS = {ELDER, RAKAZ, JINDA, OZZU, VELJANI, AROHA}
TRIBE_GIVERS = HUB_GIVERS - {AROHA} | {MOZU, GRIZZIK, HALAJA, TIKORA}


def k(target, n, zone=LB):
    return kill(target, n, zone=zone)


def boss(target, zone=LB):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=LB, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Bough Python": [("lb_q_python_skin", "Bough Python Skin", "A long green-gold skin, supple and strong. The "
                      "trolls wrap their ladder rungs in it so wet hands don't slip.")],
    "Silkwood Weaver": [("lb_q_silk", "Spool of Silkwood Silk", "A spool of web silk, thick as twine and stronger "
                         "than rope."),
                        ("lb_q_wrapped_bronze", "Silk-Wrapped Bronze", "A piece of engraved bronze the spiders "
                         "wrapped up like prey. It hums faintly through the silk.")],
    "Amberdrip Ooze": [("lb_q_amber_clot", "Clot of Amber Sap", "A clot of the ooze that's set hard as amber, with "
                        "a gnat caught in it.")],
    "Canopy Howler": [("lb_q_hoarded_crystal", "Ape-Hoarded Crystal", "A chip of blue crystal, worn smooth by an ape "
                       "turning it over in its hands.")],
    "Mossback Skink": [("lb_q_skink_hide", "Mossback Skink Hide", "A soft hide with a mossy green back. It makes "
                        "good harness leather.")],
}
#: a knotted cord a Bloodscalp ropecutter carries starts a quest
STARTER_DROPS = {
    "Bloodscalp Ropecutter": [("lb_q_knotted_cord", "Knotted Climbing Cord", "A short cord tied in a row of knots, "
                               "each a different kind. Bloodscalp climbers use them to tell each other where the next "
                               "ropes will go up.", 0.12)],
}
STARTER_IDS = {"lb_q_knotted_cord": "lbq_the_knotted_cord"}

_cyc = [23]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=LB, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
WEST_TIP = (24, 132)          # the end of the west bough
EAST_TIP = (166, 126)         # the end of the east bough
WEST_BRIDGE = (38, 105)       # the plank bridge from the west fork
EAST_BRIDGE = (146, 96)       # the plank bridge to the east bough
OLD_SHRINE = (27, 90)         # the troll shrine the apes have taken
ROPE_HOOKS = (86, 140)        # where the Bloodscalp ropes come up over the edge
SKYBONE_W = (59, 98)          # bronze caught on the west fork
SKYBONE_E = (126, 93)         # an engine housing on the east fork
FALLS = (92, 140)             # where the river falls off the Great Bough
SAPWELL = (52, 68)            # inside the Knothollow: the vein of sap


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE STAIR AND THE LIFT
    A(Q("lbq_moths_on_the_stair", "Moths on the Stair", MOZU, 44, 44, "Stairwarden's",
        "Stairwarden Mozu keeps the top of the Root Stair, and the Glimmerwing Moths come to its lanterns in clouds. "
        "Their dust makes the steps as slick as ice.",
        [k("Glimmerwing Moth", 8)],
        "The Glimmerwing Moths come for the stair's lanterns every night, and their dust makes the steps slick. "
        "Somebody's going to go down the stair the fast way if it keeps up. Knock them out of the air along the ledge.",
        "That's much better, and I'll sweep the steps in the morning so nobody slides.\n\nYou'd think a stair this old "
        "would be safe by now. It's three years old, which is old for anything up here."))
    A(Q("lbq_skinks_in_the_steps", "Skinks in the Steps", MOZU, 44, 45, "Stepwarden",
        "The Mossback Skinks have started nesting in the cracks of the Root Stair, and they bite anybody who steps on "
        "one in the dark.",
        [k("Mossback Skink", 8)],
        "The Mossback Skinks nest in the cracks of the stair and the ledge, and they'll bite at ankles in the dark. "
        "Clear them off the ledge before somebody kicks one and goes over the edge after it.",
        "My ankles thank you, and so will everybody who climbs tonight.\n\nThe newcomers who come up the stair always ask why it's so far down. I tell "
        "them it's farther up, and that usually ends the conversation."))
    A(Q("lbq_counterweights", "Counterweights", GRIZZIK, 44, 45, "Liftkeeper's",
        "Liftkeeper Grizzik built the Great Lift up to the Settlement, and its counterweights are wearing down. "
        "There's mithril in the stones caught in the boughs' forks.",
        [gather("ore_mithril", 6, "Gather Mithril Ore")],
        "A lift's only as good as its counterweights, and mine are wearing thin. There's mithril in the stones "
        "that got caught in the forks when the tree grew up through the jungle. Bring me some and I'll recast them.",
        "That's good honest metal. I'll have the new weights hung by the end of the week.\n\nFizzle laughs at me "
        "for using mithril on a lift. Fizzle's lifts only go up as far as a house."))
    A(Q("lbq_pythons_on_the_cable", "Pythons on the Cable", GRIZZIK, 44, 45, "Cable-Clearer's",
        "The Bough Pythons climb the lift's cables to sun themselves, and one of them nearly stopped the lift halfway "
        "up last week.",
        [k("Bough Python", 7)],
        "The Bough Pythons climb the cables to lie in the sun, and one of them wrapped round the drum last week and "
        "stopped the lift dead, which isn't good for business. Thin them out on the ledge and down the Great Bough.",
        "That should keep the cables clear for a while.\n\nThe passengers who were stuck halfway up that day still "
        "won't look at me. Three hours, swinging over the drop, with a python for company."))

    # =================================================================================== 2. CLIMBERS FROM BELOW
    A(Q("lbq_who_climbs_up", "Who Climbs Up", TIKORA, 44, 44, "Lookout's",
        "The Bloodscalp have started coming up the tree on ropes, over the end of the Great Bough where it hangs "
        "above the jungle. Scout Tiko'ra wants them driven back down.",
        [k("Bloodscalp Ropecutter", 6), k("Bloodscalp Skull-Taker", 6)],
        "The Bloodscalp have found a way up that doesn't go past the landing. They throw ropes up from the jungle and "
        "climb onto the end of the Great Bough. Kill their Bloodscalp Ropecutters and the Bloodscalp Skull-Takers "
        "who come up behind them.",
        "That's a few less ropes on the Great Bough tonight.\n\nMy grandmother was Bloodscalp, and so were half the elders. We climbed this "
        "tree to get away from them, and now they've followed us up it.",
        nxt="lbq_ropemaster_vazjin"))
    A(Q("lbq_ropemaster_vazjin", "Ropemaster Vaz'jin", TIKORA, 45, 45, "Ropemaster's",
        "The climbs are led by Vaz'jin, who's the best climber the Bloodscalp have. As long as he's tying the ropes, "
        "they'll keep coming up.",
        [boss("Ropemaster Vaz'jin")],
        "Ropemaster Vaz'jin ties every rope the Bloodscalp climb, and he climbs first on every one. Without him "
        "they'll be throwing ropes at the bark for a year. Find him at the Climbers' Cut and end him.",
        "Vaz'jin's dead, and his ropes go with him.\n\nThey'll find another climber, they always do, but not one "
        "like him. Tell the elder you've bought Mossroof a quiet season."))
    A(Q("lbq_cut_their_ropes", "Cut Their Ropes", TIKORA, 44, 45, "Ropecutter's",
        "Scout Tiko'ra watches for climbers at the end of the Great Bough. He wants the Bloodscalp ropes cut where "
        "they come up over the edge, and the warriors who guard them killed.",
        [explore(*ROPE_HOOKS, "Cut the Bloodscalp ropes at the end of the Great Bough"),
         k("Bloodscalp Spear-Hurler", 5), k("Bloodscalp Reaver", 5)],
        "The Bloodscalp ropes come up over the edge at the very end of the Great Bough, and they're tied off on iron hooks. "
        "The Bloodscalp Spear-Hurlers and the Bloodscalp Reavers guard them. Kill them and cut every rope you find.",
        "I heard them hit the jungle from here. That's a long way to fall for a rope.\n\nThey'll tie new ones. "
        "They always do. But every rope we cut is a night they don't come up."))
    A(Q("lbq_the_knotted_cord", "The Knotted Cord", "item:lb_q_knotted_cord", 44, 45, "Knot-Reader's",
        "A Bloodscalp ropecutter was carrying a short cord tied in a row of different knots. The climbers use them to "
        "tell each other where the next ropes go up, and Scout Tiko'ra can read them.",
        [deliver("lb_q_knotted_cord", "Bring the knotted cord to Scout Tiko'ra on the Great Bough")],
        "The cord's tied in a row of different knots, the kind climbers use to pass a message. Scout Tiko'ra's "
        "been watching the Bloodscalp longer than anyone, and he'll be able to read it.",
        "Three knots, a hitch and a double loop. That means the east bough, at night, when the moon's down.\n\nThey "
        "wanted to come up behind us through the Silkwood. We'll have people waiting there now.",
        turn_in_npc_id=TIKORA))

    # =================================================================================== 3. THE APES
    A(Q("lbq_howlers_on_the_west_bough", "Howlers on the West Bough", RAKAZ, 44, 44, "Bough-Hunter's",
        "The Canopy Howlers on the west bough have gone mean since they started drinking the sap, and they've been "
        "coming onto the ledge to steal from Mossroof.",
        [k("Canopy Howler", 8)],
        "The Canopy Howlers used to steal fruit and run. Now they steal and stay, and they've started fighting back. "
        "Go out on the Howling Bough and teach them to run again.",
        "They'll think twice before they come onto the ledge.\n\nThe young ones are the worst. The tree came up out of "
        "nowhere three years ago, and they've never known the jungle without it.", nxt="lbq_the_silverbacks"))
    A(Q("lbq_the_silverbacks", "The Silverbacks", RAKAZ, 44, 45, "Silverback",
        "The big Sap-Drunk Silverbacks lead the howlers, and they're the ones drinking the most sap. Rakaz wants them "
        "brought down before they get any bigger.",
        [k("Sap-Drunk Silverback", 6)],
        "The Sap-Drunk Silverbacks lead the troop, and they drink more sap than all the rest put together. Every "
        "week they're bigger. Bring them down on the Howling Bough before they're too big to bring down at all.",
        "That's a quieter bough already. You can hear the birds again.\n\nThere's still one left, though, the "
        "biggest of them, the one with the gold tooth.", nxt="lbq_old_goldtooth"))
    A(Q("lbq_old_goldtooth", "Old Goldtooth", RAKAZ, 45, 45, "Goldtooth",
        "The biggest silverback on the west bough has a tooth stained gold with sap, and he's thrown two trolls off "
        "the bough this season. Rakaz calls him Old Goldtooth.",
        [boss("Old Goldtooth")],
        "Old Goldtooth's the biggest ape on the tree, and he's thrown two of our hunters off the Howling Bough. "
        "Nobody's come back from a fall that long. Find him and finish him.",
        "Old Goldtooth's dead. I'll tell the families of the two he threw.\n\nIt wasn't his fault, not really. "
        "He drank what the tree gave him, and it made him into that."))
    A(Q("lbq_python_skins", "Python Skins", RAKAZ, 44, 45, "Laddergrip",
        "The trolls wrap their ladder rungs in Bough Python skin, so wet hands don't slip. Rakaz needs more for the "
        "new ladders going up in Mossroof.",
        [fetch("lb_q_python_skin", 6)],
        "Every ladder in Mossroof has its rungs wrapped in Bough Python skin. It grips when it's wet, and up here "
        "it's always wet. Bring me skins from the pythons on the Great Bough and the ledge.",
        "These will wrap a whole ladder, maybe two.\n\nThe transplant who climbs, Aroha, says they used to use "
        "something called rubber for this where she's from. I've never seen rubber, but I'd bet it's not as good."))

    # =================================================================================== 4. THE SILKWOOD AND THE BRIDGES
    A(Q("lbq_check_the_bridges", "Check the Bridges", OZZU, 44, 44, "Bridgekeeper's",
        "Bridgekeeper Ozzu keeps the plank bridges that cross the drop between the boughs. He wants someone to walk "
        "both of them and tell him how they're holding.",
        [explore(*WEST_BRIDGE, "Walk the west bridge, from the west fork to the Howling Bough"),
         explore(*EAST_BRIDGE, "Walk the east bridge, from the east fork to the Silkwood")],
        "There are two bridges across the drop, one to the Howling Bough and one to the Silkwood. Walk them both for "
        "me and tell me if anything's moving that shouldn't. Don't look down, and if you do, don't look down for long.",
        "The west one's fine. The east one has web all over its ropes, and that's not mine. Half the people crossing it "
        "these days are newcomers who've never seen a rope bridge, so it had better hold.\n\nThe spiders have "
        "started hanging their webs off my bridge. That's going to stop.", nxt="lbq_web_on_the_ropes"))
    A(Q("lbq_web_on_the_ropes", "Web on the Ropes", OZZU, 44, 45, "Webcutter's",
        "The Silkwood Stalkers have been dropping onto the east bridge from webs hung off its ropes, and taking "
        "whoever's crossing.",
        [k("Silkwood Stalker", 7)],
        "The Silkwood Stalkers hang their webs off the east bridge and drop on whoever's crossing. Two traders went "
        "over the side last month. Clear them out of the Silkwood before I lose anybody else.",
        "I've cut the webs off the ropes, and nothing's dropped on me yet.\n\nThere's something bigger in there, "
        "though, something that spins the webs the stalkers sit in.", nxt="lbq_mother_lattice"))
    A(Q("lbq_mother_lattice", "Mother Lattice", OZZU, 45, 45, "Lattice",
        "At the heart of the Silkwood a spider has spun a lattice of web between the leaf crowns big enough to catch "
        "an ape. Ozzu wants her dead before she spins one across his bridge.",
        [boss("Mother Lattice")],
        "Every web in the Silkwood leads back to one spider, and the trolls call her Mother Lattice. She's spun a web "
        "big enough to catch an ape. Find her in the Silkwood and kill her before she spins one across my bridge.",
        "Mother Lattice is dead, and the Silkwood will be a lot quieter.\n\nI'll take her silk, if you don't mind. "
        "It's the strongest rope there is."))
    A(Q("lbq_silk_for_the_bridges", "Silk for the Bridges", OZZU, 44, 45, "Silkspinner's",
        "Silkwood silk is stronger than rope and doesn't rot. Ozzu wants spools of it from the Silkwood Weavers to "
        "rope his bridges with.",
        [fetch("lb_q_silk", 6)],
        "If the spiders are going to hang off my bridges, they can rope them too. Silkwood silk is stronger than "
        "any rope I can make, and it doesn't rot. Bring me spools of it off the Silkwood Weavers.",
        "That's enough to rope the east bridge twice over.\n\nOne of the newcomers asked me if it was safe to cross a "
        "bridge roped with spider silk. I told her it's safer than one roped with anything else. There's a kind of justice in it. The spiders tried to "
        "take my bridge, and now they're holding it up."))

    # =================================================================================== 5. THE RIVER AND THE SAP
    A(Q("lbq_what_the_river_carries", "What the River Carries", JINDA, 44, 44, "Rivercaller's",
        "Rivercaller Jinda says the fish in the Great Bough's river have started to taste of sap. She wants a catch "
        "to read.",
        [gather("fish_redgill", 6, "Catch Redgill in the Great Bough's river")],
        "A river shouldn't run along a branch, but this one does, and the fish in it have started tasting of sap. "
        "I read the river by what lives in it. Catch me some Redgill from the Great Bough and I'll see what they say.",
        "Sweet, and gold under the scales. The sap's in the river now, all the way down.\n\nThat's new this year. "
        "Something's pushing sap out of the tree faster than it ever used to.", nxt="lbq_amber_in_the_water"))
    A(Q("lbq_amber_in_the_water", "Amber in the Water", JINDA, 44, 45, "Amberbane",
        "The sap's pooling in the bark along the river and coming alive as Amberdrip Oozes. Jinda wants them cleared "
        "out and a clot of their amber brought back.",
        [k("Amberdrip Ooze", 6), fetch("lb_q_amber_clot", 4)],
        "Where the sap pools in the bark it wakes up, and the Amberdrip Oozes slide down into the river and foul it. "
        "Kill them along the Great Bough, and bring me clots of their amber. I'll read those too.",
        "There's a gnat in this one that's never lived anywhere but this tree. It's set in amber, and the amber "
        "isn't a week old.\n\nThe sap's coming from somewhere deeper than the bark. I think it's coming from inside "
        "the trunk.", nxt="lbq_the_amber_glut"))
    A(Q("lbq_sunscale", "Sunscale", JINDA, 45, 45, "Sunscale",
        "A python with gold scales lies in the sun on the Great Bough, as long as three boats, and the trolls who fish "
        "the river have learned to leave when they see it. Jinda calls it Sunscale.",
        [boss("Sunscale")],
        "Sunscale lies in the sun along the Great Bough, and it's been taking the fishers off the river one by one. "
        "It's drunk so much sap its scales have turned gold. Find it on the Greenwater Bough and kill it.",
        "Sunscale's dead, and the fishers can go back to the river.\n\nI'll miss seeing it in the sun, a little. "
        "Since the worlds came together everything up here is beautiful in the way terrible things sometimes are."))
    A(Q("lbq_the_amber_glut", "The Amber Glut", JINDA, 45, 45, "Amber Glut",
        "Jinda's followed the sap back into the trunk, down through the Knothollow to where the bark turns to "
        "heartwood. Something's pooled there and swollen, and the river's sap is coming from it.",
        [explore(*SAPWELL, "Find the Sapwell inside the Knothollow", zone=KH), boss("The Amber Glut", zone=KH)],
        "The sap's coming from inside the trunk, through the Knothollow, the great knot off the ledge. Go in past the "
        "Sapwell to the bottom bore, where the bark turns to heartwood. Whatever's swollen up down there's the "
        "Amber Glut, and it's bleeding the tree into my river.",
        "You went all the way to the heartwood. I've never been that far into the tree.\n\nThe river's running "
        "clear tonight, for the first time this year. The tree will heal what the Glut drank, given time."))

    # =================================================================================== 6. THE BORERS IN THE KNOT
    A(Q("lbq_the_knot_in_the_trunk", "The Knot in the Trunk", ELDER, 44, 45, "Knotwarden's",
        "Elder Tal'vani can hear chewing in the trunk under Mossroof at night. The bark-borers have got into the great "
        "knot off the ledge, and they're eating their way in.",
        [k("Knothollow Borer", 8, zone=KH), k("Borer Grub", 6, zone=KH)],
        "At night I can hear them chewing in the wood under the village. The borers have got into the Knothollow, the "
        "great knot in the trunk off the ledge, and they're eating their way in. Go inside and kill the Knothollow "
        "Borers, and the Borer Grubs they're raising.",
        "It's quieter under the village tonight, but not quiet.\n\nThey've eaten deeper than I thought. There's a "
        "mother in there somewhere, laying them as fast as you kill them.", nxt="lbq_gnawmother_ixx"))
    A(Q("lbq_gnawmother_ixx", "Gnawmother Ixx", ELDER, 45, 45, "Gnawmother's",
        "The borers in the Knothollow all come from one mother, who's made her nest where they broke into a vein of "
        "sap. Tal'vani calls her Gnawmother Ixx.",
        [boss("Gnawmother Ixx", zone=KH)],
        "The borers broke into a vein of sap deep in the Knothollow, and that's where their mother sits, laying them "
        "in the gold. Gnawmother Ixx has to die, or the trunk under Mossroof will be hollow by the rains.",
        "The chewing's stopped. I slept all night for the first time this month.\n\nThe tree carried us up out of "
        "the world when it broke, the year the worlds came together. The least we can do is keep the bugs out of it."))

    # =================================================================================== 7. SKY-BONES
    A(Q("lbq_sky_bones", "Sky-Bones", VELJANI, 44, 44, "Sky-Bone",
        "Pieces of bronze and crystal keep falling out of the clouds and catching in the branches. The trolls call them "
        "sky-bones, and Scholar Vel'jani has come down from the Settlement to find every one.",
        [explore(*SKYBONE_W, "Find the sky-bones caught on the west fork"),
         explore(*SKYBONE_E, "Find the sky-bones caught on the east fork")],
        "Things keep falling out of the clouds onto the tree, bronze and crystal, worked by somebody's hands. The "
        "trolls call them sky-bones. Two have caught on the forks of the Great Bough, one on each side. Go and look "
        "at them for me.",
        "A bronze plate and a whole engine housing, still warm. Nobody on the ground made these.\n\nThe scholars "
        "in the Settlement have a wall of them now. Not one of us can say what they're for.", nxt="lbq_what_apes_hoard"))
    A(Q("lbq_what_apes_hoard", "What Apes Hoard", VELJANI, 44, 45, "Hoardfinder's",
        "The Canopy Howlers collect anything shiny that falls into the boughs, and they've been collecting the crystal "
        "chips off the sky-bones.",
        [fetch("lb_q_hoarded_crystal", 5)],
        "The Canopy Howlers pick up anything that shines, and they've been picking the crystal chips off the sky-bones "
        "and carrying them off. Take them back off the howlers on the Howling Bough.",
        "Every one of these is cut the same way, at the same angles, by the same hand.\n\nThat's not a crystal that "
        "grew. That's a part.", nxt="lbq_bronze_in_the_silk"))
    A(Q("lbq_bronze_in_the_silk", "Bronze in the Silk", VELJANI, 44, 45, "Silkwrapped",
        "The spiders in the Silkwood have been wrapping pieces of fallen bronze in silk the way they wrap their prey. "
        "Vel'jani wants them back.",
        [fetch("lb_q_wrapped_bronze", 3)],
        "The Silkwood Weavers wrap the fallen bronze up in silk like it's food. I don't know if they think it's alive. "
        "Bring me the pieces, silk and all, and I'll cut them out.",
        "Listen to it hum. Whatever this was part of, it was running when it fell.\n\nI want somebody else to see "
        "one of these, somebody who knows machines better than any troll.", nxt="lbq_down_to_fizzle"))
    A(Q("lbq_down_to_fizzle", "Down to Fizzle", VELJANI, 45, 45, "Bronze-Hum",
        "Vel'jani wants a goblin's eye on the humming bronze. Fizzle Brasswinch, who built the lifts down at Rootwater "
        "Landing, has seen a piece like it before.",
        [deliver("lb_q_humming_bronze", "Take the humming bronze to Fizzle Brasswinch at Rootwater Landing")],
        "Fizzle Brasswinch at the landing knows machines better than anybody on this tree. Take him this piece, the "
        "one that hums, and ask him what it is. Go down the Root Stair, it's quicker than you'd think.",
        "Oh, I've seen one of these before. Not this piece, but its cousin, in the sand on the north-west root.\n\n"
        "It's still running. Whatever's up there building these, it's not done falling apart. Tell Vel'jani I "
        "still can't place it, and that worries me more than it worries him.",
        turn_in_npc_id=FIZZLE,
        grant_items=carry("lb_q_humming_bronze", "Humming Bronze", "A piece of engraved bronze cut out of spider silk. "
                          "It hums when you hold it, and the hum gets louder the higher you climb.")))

    # =================================================================================== 8. AROHA
    A(Q("lbq_a_climbers_eye", "A Climber's Eye", AROHA, 44, 45, "Treetop",
        "Aroha Tane climbed trees for a living on Earth before the merge, and she came up this one for the view. She "
        "wants someone to go out to the very tips of the outer boughs and look back at the trunk.",
        [explore(*WEST_TIP, "Go out to the tip of the west bough"),
         explore(*EAST_TIP, "Go out to the tip of the east bough")],
        "I've been out on every bough in Mossroof but the two outer ones, because the apes and the spiders get there "
        "first. Go out to the tips of the west and the east bough for me, turn round and look back at the trunk.",
        "It doesn't end, does it? You look up and it just keeps going into the cloud.\n\nBack home the tallest "
        "kauri I ever climbed was fifty metres. My mates would never believe this."))
    A(Q("lbq_harness_leather", "Harness Leather", AROHA, 44, 45, "Harnessmaker's",
        "Aroha teaches the young trolls to climb with a harness, the way arborists do back on Earth. She needs soft "
        "leather for the straps.",
        [fetch("lb_q_skink_hide", 6)],
        "The young trolls climb like they can't fall, and some of them are about to find out. I'm teaching them to "
        "use a harness. Mossback Skink hide is soft enough for the straps, so bring me some off the ledge.",
        "These will make three harnesses at least.\n\nThe elders laughed at me at first. Then one of the young ones "
        "slipped with a harness on, and swung there, and climbed back up. Nobody's laughing now."))
    A(Q("lbq_hexes_in_the_leaves", "Hexes in the Leaves", AROHA, 44, 45, "Hexwarden's",
        "The Bloodscalp's casters come up with the climbers and hex the trolls on the Great Bough. Aroha was caught by "
        "one last week and couldn't stop shaking for a day.",
        [k("Bloodscalp Hexer", 5), k("Bloodscalp Bough-Shaman", 5)],
        "A Bloodscalp Hexer caught me on the Great Bough last week, and I couldn't stop shaking for a day. The "
        "Bloodscalp Bough-Shamans call lightning down through the leaves. Kill them at the Climbers' Cut.",
        "Thank you. I've been jumping at every shadow on that bough.\n\nI kept thinking, I came up here to climb "
        "trees and look at things. I didn't come up here to be cursed. Then again, none of us asked to come here."))
    A(Q("lbq_bark_samples", "Bark Samples", AROHA, 44, 45, "Barkreader's",
        "Aroha wants to know how fast the tree is growing. She's been measuring the bark, and she needs wood from the "
        "boughs to compare against her notes.",
        [gather("wood_bloodroot_stump", 5, "Gather Bloodroot Wood")],
        "I've been measuring the bark since I got here, and the numbers don't make any sense. No tree grows this "
        "fast. Bring me Bloodroot wood from the boughs, and I'll count the rings against my notes.",
        "There are rings in here for every month, not every year. It's growing like it's in a hurry.\n\nA tree "
        "that grows like this is reaching for something. I'd love to know what's up there."))

    # =================================================================================== 9. THE WEST SCOUT
    A(Q("lbq_the_shrine_on_the_west_bough", "The Shrine on the West Bough", HALAJA, 44, 45, "Loa-Shrine",
        "The trolls built a small shrine to the tree's loa out on the west bough, and the apes have taken it over. "
        "Scout Halaja wants to know what they've done to it.",
        [explore(*OLD_SHRINE, "Find the old shrine on the Howling Bough"), k("Canopy Howler", 5)],
        "We built a shrine to the loa out on the west bough when we first came up, and the apes have moved into it. "
        "Go and see what's left of it. The Canopy Howlers will come at you, so kill them as you go.",
        "They've filled it with fruit pits and shiny bits of bronze. It's almost like they were praying.\n\nMaybe "
        "they were. The tree answered us. Maybe it's been answering them too."))

    # =================================================================================== 10. ON TO THE CITY
    A(Q("lbq_the_great_lift", "The Great Lift", ELDER, 45, 45, "Liftward",
        "Elder Tal'vani says you've earned the city. The Great Lift at the ledge's east end goes up to the Great "
        "Settlement, and Liftkeeper Grizzik will take you up.",
        [deliver("lb_q_elders_word", "Take Elder Tal'vani's word to Liftkeeper Grizzik at the Great Lift")],
        "You've done more for Mossroof than anybody since we built it. The Great Settlement's above us, in the heart "
        "of the tree, and the High Chieftain will want to meet you. Take my word to Grizzik at the Great Lift and "
        "he'll take you up.",
        "Tal'vani's word, eh? Then you go up first, ahead of the crates.\n\nKeep your elbows in and don't look down "
        "until the Settlement's lanterns are all round you. It's worth the wait.",
        turn_in_npc_id=GRIZZIK,
        requires_quests=["lbq_ropemaster_vazjin", "lbq_gnawmother_ixx"],
        grant_items=carry("lb_q_elders_word", "Tal'vani's Word", "A strip of bark painted with Mossroof's moss-green "
                          "mark, saying the bearer has earned the climb to the city.")))
    return out
