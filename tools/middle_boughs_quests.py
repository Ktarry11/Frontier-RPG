"""
The Middle Boughs' quests (45-47), the tree's heart above the Great Settlement, and Shriekhollow's (the harpies' hollow
in the trunk). Read by tools/build_middle_boughs_quests.py, which holds them to every rule before anything is written.
The brief is docs/worldtree_brief.md; the map is tools/handbuilt_worldtree_middle_boughs.py.

THE THREADS (the brief: "The tree is hungry: bark rot, sap blight, things living in the rot; harpies nesting in the
hollows", and on the ascent, "a crashed scout construct, still twitching"):
  The watch: Shadow Hunter Vokra holds Heartwatch because of the Heartwood Hollow at its back. The rot climbs out of it
    along the Rotting Bough; her chain pushes it back to Old Barkrot, and ends listening at the sealed split.
  The tree's voice: Loa-Speaker Ganjo hears the tree groaning, and listens at the first climbers' stones.
  The cure: Bark-Doctor Ezzi cuts the rot out where she can, and Dr. Priya Raman, a plant pathologist from Bengaluru,
    works out what it is. It behaves like a fungus she knows from home, except that it's hungry. Her chain goes into
    Shriekhollow, to what the harpies feed at the bottom of it.
  The harpies: Huntmaster Raz'gul's chain on the Hollow Bough, Old Raggedwing, and into Shriekhollow after Matron Vyssa.
  The fallen construct: the falling-sky thread. Scholar Nyara studies the thing that fell on the Lichen Reach, and the
    core of the Wakened Surveyor goes down to Tel'zan's record in the Settlement: everything it measured was the tree.
  The first climbers: Stonekeeper Jo'than keeps their terraces and their names, and the old owl that hunts them.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. Earth comes up more again (Priya,
and the trolls' word for what happened, "the merge").
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

MB = "middle_boughs"
SH = "shriekhollow"

# ---- Heartwatch
VOKRA, GANJO, EZZI, RAZGUL = "mb_shadowhunter", "mb_loa_speaker", "mb_bark_doctor", "mb_huntmaster"
JOTHAN, NYARA, PRIYA = "mb_stonekeeper", "mb_scholar", "mb_transplant"
# ---- out on the tier
DEZZA, MAHU, REENA = "mb_liftkeeper", "mb_scout_reach", "mb_scout_hollows"
# ---- elsewhere (turn-ins only)
TELZAN = "gs_scholar_hall"

HUB_GIVERS = {VOKRA, GANJO, EZZI, RAZGUL, JOTHAN, NYARA, PRIYA}
TRIBE_GIVERS = HUB_GIVERS - {PRIYA} | {DEZZA, MAHU, REENA}


def k(target, n, zone=MB):
    return kill(target, n, zone=zone)


def boss(target, zone=MB):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=MB, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Lichenwing Moth": [("mb_q_pale_dust", "Pinch of Pale Dust", "Wing dust from a Lichenwing Moth, grey-green and "
                         "fine as ash. Burned on a coal, it smells of rain.")],
    "Scuttling Gear-Drone": [("mb_q_bronze_cog", "Bronze Drone-Cog", "A small toothed wheel of bronze, still warm. "
                              "Every tooth is cut exactly the same.")],
    "Rotheart Treant": [("mb_q_rot_splinter", "Rotted Heartwood Splinter", "A splinter of heartwood gone soft and "
                         "dark, threaded through with pale white strands.")],
    "Rotspore Cloud": [("mb_q_spore_sac", "Rotspore Sac", "A papery sac of spores from the heart of a Rotspore Cloud. "
                        "It puffs grey when it's squeezed.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [9]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=MB, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
CONSTRUCT = (148, 20)         # the construct that fell on the Lichen Reach
REACH_SHRINE = (62, 24)       # the first climbers' shrine out on the Reach
LOOKOUT = (98, 20)            # the old lookout on the Reach
ROT_HEART = (118, 72)         # where the rot is worst on the Rotting Bough
ROT_END = (146, 80)           # the rot's far end, where it's spreading
GREAT_HOLLOW = (128, 108)     # the harpies' great hollow on the fork
ROOSTS = (88, 132)            # the harpies' roosts on the Hollow Bough
HEARTWOOD_DOOR = (20, 46)     # before the Heartwood Hollow, behind Heartwatch
STAIR_TOP = (20, 18)          # the Root Stair on up the trunk
TERRACE_TOWER = (26, 100)     # the first climbers' tower on the south terraces
NORTH_CAIRN = (30, 32)        # the cairn on the north terraces
EYRIE = (46, 66)              # inside Shriekhollow: the matron's eyrie


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE WATCH
    A(Q("mbq_what_comes_up", "What Comes Up", VOKRA, 45, 46, "Heartwatch",
        "Shadow Hunter Vokra holds Heartwatch because of the Heartwood Hollow behind it. The rot climbs up out of the "
        "heartwood and along the Rotting Bough, and the Blightgrubs come up with it.",
        [k("Blightgrub", 8)],
        "The rot comes up out of the heartwood and spreads along the Rotting Bough, and the Blightgrubs ride it like a "
        "tide. They eat the soft wood and leave the rot room to grow, so it's spreading faster every week. Go out on the bough and kill them.",
        "Good, that's the first push. They'll come back, but slower.\n\nBefore the merge the shadow hunters didn't "
        "come up here at all. Now we've got a watch, and a door we don't open.", nxt="mbq_the_rots_heart"))
    A(Q("mbq_the_rots_heart", "The Rot's Heart", VOKRA, 46, 46, "Rotwarden's",
        "Vokra wants to know where the rot on the Rotting Bough is worst, and she wants the Rotheart Treants there cut "
        "down before they spread it any further.",
        [explore(*ROT_HEART, "Find where the rot is worst on the Rotting Bough"), k("Rotheart Treant", 5)],
        "Somewhere out along the Rotting Bough the rot's thickest, and the Rotheart Treants stand in it like they're "
        "guarding it. Find the place and cut them down. I need to know how bad it's got.",
        "The bark's gone soft right through, you say, and there's sap coming up black. That's worse than I'd hoped.\n\n"
        "Something down in the heartwood is feeding it. The rot isn't the sickness, it's the sign of it.",
        nxt="mbq_old_barkrot"))
    A(Q("mbq_old_barkrot", "Old Barkrot", VOKRA, 47, 47, "Barkrot",
        "The oldest of the rotting treants has rooted itself in the worst of the rot on the Rotting Bough. The shadow "
        "hunters call it Old Barkrot, and the rot spreads fastest round it.",
        [boss("Old Barkrot")],
        "There's one treant on the Rotting Bough older and bigger than the rest, and the rot spreads fastest round it. "
        "We call it Old Barkrot. It's put down roots in the rot, and it won't move unless something makes it.",
        "Old Barkrot's down, and the bough already smells cleaner.\n\nThat buys us time. Now I want you to see the "
        "door we're watching, so you understand what the time's for.", nxt="mbq_sealed_for_now"))
    A(Q("mbq_sealed_for_now", "Sealed for Now", VOKRA, 47, 47, "Sealwarden's",
        "Vokra wants you to stand at the Heartwood Hollow behind Heartwatch and listen, so you know what the watch is "
        "for. The shadow hunters sealed it, and nobody goes in until the tribes say so.",
        [explore(*HEARTWOOD_DOOR, "Stand at the Heartwood Hollow and listen")],
        "Go and stand at the split behind me and put your ear to the seal. Don't touch it. Just listen, and then come "
        "back and tell me what you heard.",
        "Chewing, slow and steady, and something breathing between the bites. Yes, that's what we hear too.\n\nWe "
        "don't go in until the High Chieftain says we're ready. When he does, I'll want you with us."))

    # =================================================================================== 2. THE TREE'S VOICE
    A(Q("mbq_listening_to_the_tree", "Listening to the Tree", GANJO, 45, 46, "Loa-Listener's",
        "Loa-Speaker Ganjo hears the tree groaning at night, and he wants to know where it hurts. The first climbers "
        "built their shrines where the tree spoke loudest.",
        [explore(*REACH_SHRINE, "Listen at the old shrine on the Lichen Reach"),
         explore(*TERRACE_TOWER, "Listen at the old tower on the south terraces"),
         explore(*ROT_END, "Listen at the far end of the Rotting Bough")],
        "The first climbers put their shrines where the tree's voice was loudest. Go and stand at the old shrine on "
        "the Lichen Reach, the old tower on the south terraces, and the far end of the Rotting Bough, and listen.",
        "Quiet at the shrine, quiet at the tower, and a groan at the end of the Rotting Bough that you felt in your "
        "feet. That's where it hurts.\n\nThe tree's groaned like that every night since the merge, and it's getting "
        "louder.", nxt="mbq_spores_on_the_wind"))
    A(Q("mbq_spores_on_the_wind", "Spores on the Wind", GANJO, 46, 46, "Sporeward",
        "Ganjo says the Rotspore Clouds drifting off the Rotting Bough carry the rot from branch to branch, and the "
        "wind's been blowing them toward the terraces.",
        [k("Rotspore Cloud", 7)],
        "The Rotspore Clouds drift off the Rotting Bough and settle wherever the wind drops them, and that's how the rot "
        "jumps from branch to branch. The wind's been blowing toward Heartwatch all week. Scatter them before they "
        "settle here.",
        "The air's clearer already. I can smell the lichen again instead of the rot.\n\nThe loa don't like the spores "
        "either. They went quiet when the clouds came, and they've started talking again.",
        nxt="mbq_pale_dust"))
    A(Q("mbq_pale_dust", "Pale Dust", GANJO, 46, 46, "Lichenward",
        "Ganjo burns the dust off Lichenwing Moths at the old shrines, because the smoke smells of rain and the loa "
        "like it. He wants enough to burn at every stone on the terraces.",
        [fetch("mb_q_pale_dust", 6)],
        "The Lichenwing Moths along the terraces carry a pale dust on their wings, and when it burns it smells like "
        "rain. The loa like it. Bring me some, and I'll burn it at every stone the first climbers left.",
        "That's plenty, and it smells right.\n\nThe tree likes it too, I think. Last night was the first night in a "
        "month it didn't groan till dawn.", nxt="mbq_lotus_for_the_shrine"))
    A(Q("mbq_lotus_for_the_shrine", "Lotus for the Shrine", GANJO, 46, 47, "Shrinekeeping",
        "Ganjo lays Purple Lotus at the old shrine on the Lichen Reach, as the first climbers did. Since the rot came, "
        "it's the only offering the tree takes.",
        [gather("herb_purple_lotus", 6, "Gather Purple Lotus on the boughs")],
        "The first climbers left Purple Lotus at their shrines, and since the rot came it's the only thing the tree "
        "seems to take. It grows out on the boughs. Bring me what you can and I'll lay it at the shrine on the Reach.",
        "The flowers wilt by morning now, every time. The first climbers wrote that they used to last a week.\n\nThe "
        "tree takes the offering. It's just hungrier than it was."))

    # =================================================================================== 3. THE CURE
    A(Q("mbq_bad_sap", "Bad Sap", EZZI, 45, 46, "Bark-Doctor's",
        "Bark-Doctor Ezzi cuts the rot out of the bark where she can, but the Sap-Blight Oozes on the Rotting Bough "
        "seep back into every cut she makes.",
        [k("Sap-Blight Ooze", 7)],
        "Every time I cut a soft spot out of the bark, the Sap-Blight Oozes on the Rotting Bough seep into the wound "
        "and the rot comes back worse. Clear them out so the cuts can close and the bark's got a chance.",
        "The cuts I made yesterday are still clean this morning, and that's the first time in a month.\n\nIt's not a "
        "cure, but it's a start, and starts are what a doctor lives on.", nxt="mbq_splints_for_the_bark"))
    A(Q("mbq_splints_for_the_bark", "Splints for the Bark", EZZI, 46, 46, "Splintwright's",
        "Ezzi packs the wounds she cuts in the bark with clean wood, so the tree grows over them instead of rotting. "
        "Thornveil from the boughs is the cleanest wood up here.",
        [gather("wood_thornveil_stump", 5, "Gather Thornveil Wood on the boughs")],
        "When I cut the rot out, I pack the hole with clean wood so the tree heals over it. Thornveil's the cleanest "
        "wood on the boughs, and nothing rots it. Bring me some and I'll get to work.",
        "That's good wood, and it'll hold.\n\nThe newcomer doctor says a tree back where she's from heals the same "
        "way, it just doesn't take a whole bough to do it.", nxt="mbq_splinters_for_the_doctor"))
    A(Q("mbq_splinters_for_the_doctor", "Splinters for the Doctor", EZZI, 46, 47, "Heartsplinter",
        "Ezzi wants splinters of rotted heartwood from the Rotheart Treants on the Rotting Bough taken to Dr. Priya "
        "Raman, who's been trying to work out what the rot is.",
        [fetch("mb_q_rot_splinter", 6)],
        "Priya's been asking for proper samples of the rot, deep ones. The Rotheart Treants on the Rotting Bough are "
        "rotten right through, so their splinters will do. Bring them to her, not me, she knows what to look for.",
        "These are perfect, and look at the white threads running through them.\n\nThat's mycelium, all of it. It's a fungus, "
        "or something that grows like one. Ezzi was right to send these to me.",
        turn_in_npc_id=PRIYA))

    # =================================================================================== 4. THE PATHOLOGIST
    A(Q("mbq_spore_samples", "Spore Samples", PRIYA, 46, 46, "Pathologist's",
        "Dr. Priya Raman is a plant pathologist from Bengaluru, and she wants spores from the Rotspore Clouds to see "
        "how the rot travels.",
        [fetch("mb_q_spore_sac", 6)],
        "Back home in Bengaluru I'd culture the spores to find out what I'm dealing with. I haven't got a lab up here, "
        "but I've got eyes and a lot of patience. The Rotspore Clouds on the Rotting Bough carry sacs of them. Bring "
        "me some and don't squeeze them.",
        "Thank you, and you didn't squeeze them, which is more than the last person managed.\n\nOn Earth this would "
        "be a fungus. Here it's a fungus that's hungry, and that's not a thing fungi are supposed to be.",
        nxt="mbq_where_its_spreading"))
    A(Q("mbq_where_its_spreading", "Where It's Spreading", PRIYA, 46, 47, "Fieldwork",
        "Priya wants to see the rot's far end on the Rotting Bough for herself, but she's not a fighter. She'd like "
        "someone to go first and tell her what's there.",
        [explore(*ROT_END, "Look at the rot's far end on the Rotting Bough"), k("Sap-Blight Ooze", 5)],
        "Back home in Bengaluru I'd have a field team for this. Here I've got you, and I need to know if the rot's spreading out along the bough or just deeper into it. I'd go myself, but the "
        "Sap-Blight Oozes out there would have me for lunch. Go to the far end of the Rotting Bough, clear it, and "
        "tell me what the edge of the rot looks like.",
        "Deeper, not wider. It's going straight down into the bough, toward the trunk.\n\nThat's not how a rot "
        "spreads. That's how something feeds.", nxt="mbq_what_the_harpies_feed"))
    A(Q("mbq_what_the_harpies_feed", "What the Harpies Feed", PRIYA, 47, 47, "Rotdark",
        "Priya thinks the rot is coming from somewhere inside the trunk. The harpies in Shriekhollow have been "
        "carrying grubs down into the hollow, and Scout Ree'na says they won't go past the eyrie.",
        [k("Rotdark Crawler", 6, zone=SH), boss("Old Splinterheart", zone=SH)],
        "The harpies carry grubs down into Shriekhollow and drop them past the eyrie, but they never follow. "
        "Something's at the bottom they're feeding. Go down past the eyrie, through the Rotdark Crawlers, and find "
        "out what it is. If it's what I think, Old Splinterheart is what the scouts have been calling it.",
        "A treant that grew inside the trunk, in the dark, on the rot, and the harpies kept it fed.\n\nOn Earth I'd "
        "have called it an opportunist. It wasn't the cause, I don't think. It was a symptom that got big enough to have a name.", nxt="mbq_notes_for_the_watch"))
    A(Q("mbq_notes_for_the_watch", "Notes for the Watch", PRIYA, 47, 47, "Watchkeeper's",
        "Priya has written up everything she knows about the rot, and she wants it in Shadow Hunter Vokra's hands "
        "before the tribes decide what to do about the Heartwood Hollow.",
        [deliver("mb_q_priyas_notes", "Take Priya's notes to Shadow Hunter Vokra at Heartwatch")],
        "I've written down everything, the spores, the splinters, the way it goes down instead of out. Vokra's the one "
        "who'll have to go through that door one day. Take her my notes, she'll want them more than I do.",
        "A fungus that eats like an animal, feeding something under the heartwood. I hoped the newcomer doctor "
        "would tell me I was wrong.\n\nThis goes to the High Chieftain tonight. Thank you for carrying it, and thank her for writing it.",
        turn_in_npc_id=VOKRA, requires_quests=["mbq_what_the_harpies_feed", "mbq_sealed_for_now"],
        grant_items=carry("mb_q_priyas_notes", "Priya's Notes on the Rot", "Pages of small, neat handwriting with "
                          "sketches of spores and splinters, and one line underlined twice: it goes down, not out.")))

    # =================================================================================== 5. THE HARPIES
    A(Q("mbq_talons_on_the_hollow_bough", "Talons on the Hollow Bough", RAZGUL, 46, 46, "Hollowhunter's",
        "Huntmaster Raz'gul says the harpies on the Hollow Bough have got bold since they started eating the rot's "
        "grubs. The Blighted Harpies and the Hollow Screechers lead every raid on the terraces.",
        [k("Blighted Harpy", 7), k("Hollow Screecher", 5)],
        "The harpies came up from the coast after the merge and found the hollows in the south bough. Since they "
        "started eating the rot's grubs, every Blighted Harpy has got big and the Hollow Screechers have got loud. "
        "Thin them out on the Hollow Bough.",
        "That'll teach them the terraces aren't theirs.\n\nThey'll be back, they always are. But they'll come back "
        "fewer, and they'll come back careful.", nxt="mbq_feather_knives"))
    A(Q("mbq_feather_knives", "Feather-Knives", RAZGUL, 46, 47, "Featherbane",
        "The Hollow Talons throw knives of hardened feather from the hollows, and the Hollow Windcallers whip up the "
        "wind to carry them. Raz'gul wants both cut down.",
        [k("Hollow Talon", 6), k("Hollow Windcaller", 4)],
        "The Hollow Talons throw knives cut from their own feathers, hard as bone, and the Hollow Windcallers call up "
        "a gust behind every throw. My scouts can't get near the hollows on the Hollow Bough, south-east of here. Take both down so they can.",
        "Ree'na got close enough to count the nests this morning, and she didn't come back bleeding for once.\n\n"
        "That's the kind of progress I'll take.", nxt="mbq_old_raggedwing"))
    A(Q("mbq_old_raggedwing", "Old Raggedwing", RAZGUL, 47, 47, "Raggedwing",
        "The oldest harpy on the Hollow Bough is half bald and twice as mean, and the flock follows her. Raz'gul calls "
        "her Old Raggedwing.",
        [boss("Old Raggedwing")],
        "There's an old harpy on the Hollow Bough with half her feathers gone, and every raid on the terraces starts "
        "with her screaming. The others call her something we can't say. We call her Old Raggedwing, and I want her dead.",
        "Old Raggedwing's dead. The flock's been circling all afternoon and they can't decide what to do.\n\nThat's what I wanted. "
        "Now we go into the hollow while they're still arguing.", nxt="mbq_into_shriekhollow"))
    A(Q("mbq_into_shriekhollow", "Into Shriekhollow", RAZGUL, 47, 47, "Shriekhollow",
        "The harpies' matron, Matron Vyssa, keeps her eyrie inside the trunk in a hollow the trolls call Shriekhollow. "
        "With Old Raggedwing dead, Raz'gul wants the matron next.",
        [k("Brood-Harpy", 6, zone=SH), boss("Matron Vyssa", zone=SH)],
        "Shriekhollow's in the trunk off the terraces, south of Heartwatch. Every Brood-Harpy roosts on the ledges "
        "inside, and Matron Vyssa keeps the eyrie at the top of the hollow's throat. Kill her and the flock breaks.",
        "Vyssa's dead and the hollow's gone quiet, which is a sound I've never heard from it.\n\nYou've done what we "
        "couldn't in a year. The terraces are ours again, and that's thanks to you."))

    # =================================================================================== 6. THE FALLEN CONSTRUCT
    A(Q("mbq_still_twitching", "Still Twitching", NYARA, 45, 46, "Skyfall",
        "Scholar Nyara came up from the Settlement to study the thing that fell on the Lichen Reach a month ago. It "
        "hasn't stopped moving, and the Scuttling Gear-Drones keep crawling out of it.",
        [explore(*CONSTRUCT, "Find the fallen construct at the end of the Lichen Reach"), k("Scuttling Gear-Drone", 8)],
        "Something fell out of the clouds onto the end of the Lichen Reach, and it's still twitching. Little "
        "Scuttling Gear-Drones keep crawling out of it and going somewhere. Go and look at it for me, and stop the "
        "drones while you're there.",
        "Bronze, crystal and wire, and none of it made by anyone on the ground. It fell, it broke, and it kept "
        "working.\n\nThe drones were carrying pieces of bark back to it. It's been collecting the tree.",
        nxt="mbq_drone_cogs"))
    A(Q("mbq_drone_cogs", "Drone-Cogs", NYARA, 46, 46, "Cogwright's",
        "Nyara wants cogs from the Scuttling Gear-Drones on the Lichen Reach, so she can see how they're made before "
        "the scholars in the Settlement start arguing about it.",
        [fetch("mb_q_bronze_cog", 6)],
        "Tel'zan will want to know how these things are built, and I want to know first. The Scuttling Gear-Drones "
        "on the Lichen Reach are full of little bronze cogs. Bring me some, and try not to bend them.",
        "Every tooth on every cog is cut exactly the same, to the width of a hair. No smith in the Settlement could "
        "do this.\n\nWhoever made these was making them long before any of us climbed this tree.",
        nxt="mbq_scouts_without_masters"))
    A(Q("mbq_scouts_without_masters", "Scouts Without Masters", MAHU, 46, 47, "Arcwarden's",
        "Scout Mahu watches the wreck for Nyara. The bigger constructs on the Lichen Reach walk the bough and spark at anything that comes close. He calls "
        "them Twitching Scouts, and Nyara can't get near the wreck while they're there.",
        [k("Twitching Scout", 6)],
        "The Twitching Scouts walk up and down the Lichen Reach as if somebody told them to guard it and then never "
        "came back. They spark at anything that moves, and they won't let Nyara near it. Bring them down.",
        "Nyara got all the way to the wreck this morning. There's a sort of eye in the middle of it, she says, and it watched her "
        "the whole time.\n\nThe biggest one's still out there, and it's the one doing the watching.",
        nxt="mbq_the_wakened_surveyor"))
    A(Q("mbq_the_wakened_surveyor", "The Wakened Surveyor", NYARA, 47, 47, "Surveyor's",
        "The largest construct on the Lichen Reach woke when the wreck fell and has been walking the bough ever since, "
        "turning a beam of light on the trunk. Nyara calls it the Wakened Surveyor.",
        [boss("The Wakened Surveyor")],
        "The big one on the Reach, the one I call the Wakened Surveyor, turns a beam of light on the trunk and holds "
        "it there, like it's measuring something. Stop it, and bring me back whatever's left of its core.",
        "You've brought its core back, and it's still warm. Hold it up to the light and you can see marks scratched "
        "inside the crystal.\n\nThey're measurements, hundreds of them, and every single one is of the tree.",
        nxt="mbq_the_surveyors_core"))
    A(Q("mbq_the_surveyors_core", "The Surveyor's Core", NYARA, 47, 47, "Record-Keeper's",
        "Nyara wants the Wakened Surveyor's core taken down to Archivist Tel'zan in the scholars' hall in the Great "
        "Settlement, for the record of everything that's fallen from the sky.",
        [deliver("mb_q_surveyors_core", "Take the Surveyor's core to Archivist Tel'zan in the Great Settlement")],
        "Tel'zan keeps the record of everything that's fallen out of the sky, and he's going to want this more than "
        "anything he's got. Take it down the High Lift to the scholars' hall at the Roost.",
        "Measurements of the tree, all of them, and the oldest ones scratched in long before the tree was this "
        "tall.\n\nSomeone up there has been watching it grow. I've never written a worse line in the record.",
        turn_in_npc_id=TELZAN,
        grant_items=carry("mb_q_surveyors_core", "The Surveyor's Core", "A fist of crystal from the Wakened "
                          "Surveyor's chest, still warm. Fine marks are scratched inside it, row after row.")))

    # =================================================================================== 7. THE FIRST CLIMBERS
    A(Q("mbq_owls_on_the_terraces", "Owls on the Terraces", JOTHAN, 45, 45, "Stonekeeper's",
        "Stonekeeper Jo'than keeps the first climbers' terraces swept, and the Mistfeather Owls that nest in the old "
        "towers have started taking the outpost's birds.",
        [k("Mistfeather Owl", 7)],
        "The Mistfeather Owls nest in the old towers along the terraces, and they've started taking Heartwatch's "
        "message birds out of the air. I've got nothing against an owl, but those birds are how we talk to the "
        "city. Thin them out along the terraces.",
        "The birds made it down to the Settlement and back today, both of them.\n\nThe owls are older up here than "
        "we are. I don't like killing them, but I like losing birds less."))
    A(Q("mbq_skinks_in_the_stonework", "Skinks in the Stonework", JOTHAN, 45, 46, "Mason's",
        "The Terrace Skinks dig their nests between the old stones, and every nest loosens a block the first climbers "
        "set by hand.",
        [k("Terrace Skink", 8)],
        "The Terrace Skinks dig in between the stones to nest, and every nest they dig loosens a block. These "
        "terraces were carried up a tree a block at a time, and I won't lose them to lizards. Clear them off.",
        "I've reset four blocks this afternoon and none of them wobbled.\n\nThe first climbers would have sat on that "
        "wall and laughed at me for fussing. I fuss anyway, because they can't.", nxt="mbq_the_climbers_names"))
    A(Q("mbq_the_climbers_names", "The Climbers' Names", JOTHAN, 46, 46, "Namekeeper's",
        "Jo'than keeps the names of the first climbers, cut in the stones they left up and down the terraces. Some of "
        "them are wearing away, and he wants them read while they still can be.",
        [explore(*NORTH_CAIRN, "Read the names on the cairn on the north terraces"),
         explore(*STAIR_TOP, "Read the names at the foot of the Root Stair"),
         explore(*TERRACE_TOWER, "Read the names on the tower on the south terraces")],
        "The first climbers cut their names in the stones they set. There's a cairn on the north terraces, the foot "
        "of the Root Stair going on up the trunk, and the old tower on the south terraces. Read me what's still "
        "there, and I'll cut it fresh.",
        "Some of those names I'd lost already, and you've brought them back. Most of them were cut long before the merge.\n\nThe one at the stair goes on past "
        "where the stair does now. Somebody climbed higher than we've ever been, and cut their name on the way.",
        nxt="mbq_hushwing"))
    A(Q("mbq_hushwing", "Hushwing", JOTHAN, 46, 46, "Hushwing",
        "The oldest owl on the terraces is bigger than a troll and makes no sound at all. The first climbers carved "
        "her on their stones, and she's started hunting the outpost's people.",
        [boss("Hushwing")],
        "There's an owl on the terraces the first climbers carved on their stones, and she's still alive, if you can "
        "believe it. We call her Hushwing. She's never troubled us, but last week she took a hunter off the south "
        "terraces. Whatever's wrong with the tree, it's got into her too. Put her down.",
        "She was old when the first climbers came, and she'd have been old when the tree was small.\n\nI'll cut her "
        "on the cairn beside them. She was one of the terraces, in her way."))

    # =================================================================================== 8. OUT ON THE TIER
    A(Q("mbq_moths_in_the_ropes", "Moths in the Ropes", DEZZA, 45, 45, "Ropehand's",
        "Ropehand Dezza works the top of the High Lift, and the Lichenwing Moths have been laying eggs in its ropes. "
        "The grubs that hatch eat the fibres.",
        [k("Lichenwing Moth", 8)],
        "The Lichenwing Moths lay their eggs in the High Lift's ropes, and the grubs eat the fibres from the inside. "
        "One day a rope's going to go with a full basket on it. Knock the moths out of the air along the terraces.",
        "I've checked every rope from top to bottom, and they're clean.\n\nOne of the newcomers told me there's a "
        "moth back where she's from that eats clothes. I didn't believe her until I saw these."))
    A(Q("mbq_up_the_root_stair", "Up the Root Stair", DEZZA, 47, 47, "Rootstair",
        "Ropehand Dezza hears everything that comes up and down the tree. Windwarden Kazra'jin, who keeps Highrest on "
        "the Upper Boughs, has asked Heartwatch for someone who can fight in the wind.",
        [deliver("mb_q_dezzas_knot", "Climb the Root Stair and give Dezza's knot to Windwarden Kazra'jin at Highrest")],
        "Kazra'jin keeps Highrest, the last camp before the cloud, and he's asked Heartwatch for a fighter. After "
        "what you did at the Hollow there's nobody else I'd send. Take him my knot so he knows it's me who sent you. "
        "The Root Stair climbs the trunk above Heartwatch, and it doesn't stop till Highrest.",
        "That's Dezza's knot, and she only ties that one for people she'd trust with a rope.\n\nWelcome to Highrest. Mind the "
        "wind, because it doesn't care who you are. Sit, eat, and then I'll tell you what we need.",
        turn_in_npc_id="ub_windwarden", requires_quests=["mbq_sealed_for_now"],
        grant_items=carry("mb_q_dezzas_knot", "Dezza's Knot", "A short length of lift rope tied in a knot only Dezza "
                          "uses, three loops and a twist, hard as wood.")))
    A(Q("mbq_pythons_in_the_lichen", "Pythons in the Lichen", MAHU, 45, 46, "Lichenstalker's",
        "Scout Mahu watches the Lichen Reach, and the Mistcoil Pythons lie flat in the lichen where nobody sees them "
        "until they're stepped on.",
        [k("Mistcoil Python", 7)],
        "The Mistcoil Pythons lie flat in the lichen on the Reach, grey on grey, and you don't see one until it's got "
        "your leg. I've been bitten twice this month. Clear them off the Reach so I can watch the wreck in peace.",
        "I walked the whole Reach this morning without looking at my feet once.\n\nNow I can watch the wreck properly. "
        "It's still twitching, if you were wondering."))
    A(Q("mbq_counting_nests", "Counting Nests", REENA, 46, 46, "Nestcounter's",
        "Scout Ree'na counts the harpies' nests for Raz'gul, so he knows how big the flock's got. She needs someone to "
        "look into the great hollow on the fork and the roosts along the Hollow Bough.",
        [explore(*GREAT_HOLLOW, "Look into the harpies' great hollow on the fork"),
         explore(*ROOSTS, "Count the roosts along the Hollow Bough")],
        "Raz'gul wants a count of the nests, and I can't get close without being seen. Look into the great hollow "
        "out east on the fork and walk the roosts along the Hollow Bough, and tell me how many you see.",
        "That's twice what I counted last month. They're breeding on the rot's grubs.\n\nRaz'gul's not going to like "
        "this, and I'm the one who has to tell him."))
    return out
