"""The Sepulcher in the plain voice (17 Nov 2026). D is the speech and A the parting line. The old briefings were
stacks of one-line paragraphs and one-word sentences, with dashes, capitals and bracketed narration. Same stories,
same directions."""

VOICE = {
    "sep_keep_tour": (
        "I'm Commander Vane. Before we go any further, can you find the latrines?\n\nI'm not joking, and I'm not testing your sense of humour. I don't give orders to people who can't find the latrines, because an order is a place and a time, and somebody who doesn't know this keep will give me neither.\n\nSo walk it. There are three stops: the lower court, inside the gate, the Keep Hall, here at my back, and the Raven Hill Terrace, to the west. It takes twenty minutes, and every soldier who's refused has cost me more than that later.\n\nThen come back and tell me what you saw. And don't touch anything that isn't yours in the graveyard wing. Half of what's lying out there was laid down on purpose.",
        "There are three stops. The Lower Court, inside the gate at the south end. The Keep Hall, here at my back. And the Raven Hill Terrace, on the west side.",
        "You didn't fall off anything.\n\nThat's a better start than most. I've lost two down the terrace steps, and neither of them was being careless.",
    ),
    "sep_woods_cull": (
        "Now something simple, and I'd like it kept simple.\n\nThis keep sits above the pines, and that's the whole of its value. Everything that comes up this hill has to come up one road, and I can see all of it. The pines are full of worg, and the leavings of the plague.\n\nI'm not asking you to clear the forest. People get ambitious about forests, and forests don't care. I want the approach to the gate kept clear of anything with teeth. A courier coming up that road at dusk should be able to see the gate before something decides about him. \n\nThey're in the woods south of here, along the road you walked in on. Take the worgs and the ghouls both. I don't rank them, because they're equally bad at the same distance.",
        None,
        "There are fewer teeth on the approach now.\n\nI'll note it in the ledger, which is where things go to be true.",
    ),
    "sep_dispatch": (
        "This is a dispatch for Captain Vesk at the Rear Guard, and it's three lines long.\n\nI want you to know that before you carry it, because people assume a sealed dispatch is substantial and then feel cheated, and a man who feels cheated talks. Three lines is all the situation warrants, and Vesk would resent more.\n\nI'd like it delivered by somebody who won't read it. Failing that, and I've been at this long enough to know which way that generally goes, I'd like it delivered by somebody who won't remember it. The second one is the one I actually rely on.\n\nGo north along the road. Vesk is at the gate. He's always at the gate. In two years I've never once had word from him that wasn't sent from a gate.",
        None,
        "It's three lines, of course. It's rude, and exactly right.",
    ),
    "sep_relic_shards": (
        "I'm Relic Hunter Darne. Don't crowd the table.\n\nI pay for grave-goods. That's the trade, it's legal enough for this valley, and I'd rather you heard my version than Molsen's.\n\nThe skeletal groundskeepers at Raven Hill carry the best of it: ring-shards, buckle-bone, whatever a person was buried with. They've been picking it up out of the plots for years and putting it in their pockets. They aren't robbing anybody, and I'd want that said. They're tidying, in the only way that's left to them. So I'm taking it off something that tidied it off somebody else, and I've made my peace with that.\n\nGo north of our gate, to Raven Hill. Bring them intact, and don't chip them. A chipped shard is worth a quarter and tells you nothing about who it belonged to.",
        None,
        "These are good, old and honest.\n\nThe collectors in the Undercity will weep, and then they'll haggle, and then they'll weep again.",
    ),
    "sep_wasp_stings": (
        "I'm Wrenn, and I sell reagents. Be quick, before Darne makes it a negotiation.\n\nThe windfall wasps in Malden's Orchard are full of a venom I've been trying to buy for years. I've written to the orchard. I've gone in person, twice, and stood at the gate like a fool. The orchard won't sell it.\n\nI'd understand that if they were using it, but they aren't. Nobody at Malden's has any interest in the wasps at all. They simply won't have anyone in among the trees, and they've never once given me a reason. The wasps won't sell it either, which is the only part of this I can respect.\n\nSo I'd like it taken. It's south of our gate, the other way from Raven Hill. The stings are on the abdomen. Handle them with tongs, mine if you've none, and bring them back.",
        "Go to Malden's Orchard, south of the Sepulcher's gate, the other way from Raven Hill. Handle them with tongs.",
        "You got the stings and didn't get stung.\n\nYou've got steadier hands than most, and most of the people I send have been dead long enough to stop shaking.",
    ),
    "sep_stone_names": (
        "I'm Reader Cass. Keep your voice ordinary, because it carries better than whispering out here.\n\nI read the stones in the Raven Hill wing. That's my whole office, and nobody assigned it to me. Most of them are blank. Rain does that, over long enough, and I'd accepted rain for the first year.\n\nThen I noticed the smooth ones aren't the oldest. They're scattered, a blank stone between two legible ones cut the same season by the same mason, and rain doesn't choose. Something out there rubs back.\n\nSo I'd like three clusters visited and the weeds pulled away from them, while there's still something under the weeds. All three are on this terrace, within a shout of where I stand. And read the names aloud, because it helps. I can't tell you how I know that.",
        None,
        "That's three more names.\n\nI'll write them on the wall, so they stay. The wall's the only thing out here that hasn't been rubbed at.",
    ),
    "sep_ellowyn_sleepers": (
        "I count the sleepers each dusk.\n\nI'm the tomb-keeper, and the counting is the whole of the post. I go along the chapel yard at the same hour and count, and the number has been the same for a long time. Some of them have stopped lying down.\n\nI want to be precise about what's bothering me, because it isn't that they're up. Things get up in this valley. It's where they go. They wander off the Raven Hill plots looking for a bed, going from plot to plot, settling in one, and being moved on by whatever's already in it.\n\nThey're trying to lie down somewhere, and they can't find the right one. So send them back where they belong. Take the groundskeepers and husks both, north of the Keep, on Raven Hill.",
        "Go to Raven Hill Cemetery, north of the Keep once you're out of the gate. Take the groundskeepers and husks both.",
        "There are fewer wanderers now.\n\nI'll sleep better, metaphorically. The joke's worn thin, but it's the only one this post has got.",
    ),
    "sep_gate_crows": (
        "I'm Crypt Guard Molsen. Don't laugh at this one. Everybody laughs at this one.\n\nI'm tired of the crows. They pick at the Keep's banners, which is a supply problem, because a banner's a month's work and we've replaced three. They steal buttons off my coat. I've got hardly any buttons left.\n\nAnd one of them has learned to open the gate-latch. It doesn't knock it loose, it opens it, from the top, with the beak, in the correct direction, which took it some working out and which it now does reliably. A bird has solved the gate of a keep, and nobody above me will put that in a report.\n\nThey're out in the Dead Field, east of the road. The harrowers feed them. I've watched it, and it's why the crows are here and why they're clever. Thin out both.",
        None,
        "And the latch-crow is dead too? I'm glad of that.\n\nI'd started talking to it, which is the point a man should stop and ask for help.\n\nI owe you a drink I can't taste.",
    ),
    "sep_hermit_oil": (
        "The hermit doesn't come out of the lean-to. He hasn't come out of it since the Plague.\n\nMy lamp is nearly dry, and that's the request. I'd make it shorter if I could.\n\nSpider-fat burns clean, with no smoke worth the name and no smell, and it lasts. I came round to it years ago.\n\nI can't hunt it myself, and I don't mean I won't. Spiders have opinions about hermits, they've had three years to form them, and I haven't got further than the trees since before the Keep had a garrison.\n\nGo to the Skittering Dark for Silverpine spiders. Bring clean glands, because a torn one leaks all the way home. And tell no one I asked. Nobody at that keep knows I'm still here, and I've put a great deal of effort into that.",
        "Hunt the Silverpine spiders. The woods have them, and the Skittering Dark, east across the forest, has little else. Bring the glands back clean.",
        "I can read again.\n\nNot that there's much I wish to read. But choosing not to and not being able to are different things, and I've missed being able to choose.",
    ),
    "sep_osk_road": (
        "My name's Osk. Pilgrim is what they put on the roster, and I've never corrected it.\n\nI walk between this Keep and Tirisfal every autumn, to pray. That's what I say, and it's what I've said for eleven years, and everyone accepts it because nobody asks a pilgrim a follow-up question.\n\nI've no idea who I'm praying to. I want that said once, to somebody, before I go again. I knew, at the start. Somewhere in the eleven years the walking stayed and the rest of it went, and I kept walking because the walking was the part I could still do.\n\nSo I'd like the road made less murderous. It doesn't need to be safe, because it's never been safe. Try the woods north and east, spiders mainly, and the treants that have gone wrong.",
        None,
        "It's a quieter road now.\n\nI'll walk it once more before the snow. And I'll think about your question, which you were polite enough not to ask.",
    ),
    "sep_cracked_locket": (
        "This was taken from inside a skeletal groundskeeper's rib-cage. It wasn't in a pocket. It was inside the ribs, where something would have had to put it deliberately.\n\nIt's a cracked silver locket. The crack runs across the face rather than the hinge, so it was dropped or struck and not forced open. There's a single pressed flower inside, flat and colourless now, and whole. Whoever closed this closed it carefully. The silver is worn smooth at one edge, the way a thing goes when it's been held in the same hand, the same way, for years.\n\nThere's a figure at the Keep who wanders the lower court and answers to nothing in particular. Nobody at the Sepulcher has ever managed a name. It's worth showing to that one.",
        "Take it to the lower court of the Sepulcher, to the one who answers to nothing in particular.",
        "Yes, that's the one.\n\nThank you.\n\nI think I had a daughter.",
    ),
    "sep_wreaths": (
        "I'm the Mourner. You can call me that, because it's what everyone calls me, and I stopped minding.\n\nI weave wreaths out of what the dead leave behind, though there hasn't been a ceremony here since the Plague.\n\nThe risen farmhands at Olsen's Farthing carry wilted sprays in their pockets. They're last year's offerings, picked, bound, put in a coat, and never delivered, because the delivering is the part that stopped. There's a field full of people walking about with flowers in their pockets for graves they were going to visit.\n\nSo I'd like them brought in. It's north of the Keep, past Raven Hill. Wilted is fine. Wilted is what I work with, and I've never once had anything else.",
        "The risen farmhands of Olsen's Farthing have them. It's a long walk north of the Keep, past Raven Hill, where the fields begin.",
        None,
    ),
}
