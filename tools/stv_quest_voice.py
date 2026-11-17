"""Stranglethorn quest text, rewritten in plain voice (Kyle, 17 Nov 2026: "I'm seeing issues in STV with writing too").

{quest_id: (description, accept_text, turn_in_text)}, compiled into an overlay by tools/build_stv_voice.py.

What was wrong with the old text, so this doesn't repeat it: aphorisms ("a river with ambitions"), characters
narrating their own mood, riddle lines that hold back what's going on, no contractions, dashes, one-word
sentences, and sentences an earlier count-stripping pass broke ("If you can manage ten, and look...", "Them
between my rack and the notch"). The bar is claude/quest_writing_guide.md: who this is, what's wrong, why it
matters to them, what to do and where, in their own voice. Directions are true to the live map
(tools/quest_targets.py). No objective counts in prose; the tracker shows them.

Voices: Gurbashi and jungle trolls use da/dis/dem, lightly for the older and more formal ones (Zul'tamo,
Zul'jana) and fully for the road gang. Goblins talk money. Orcs are plain.
"""

CENTRAL = {
    "stvc_no_bed_between": (
        "Sentry Vrak keeps Grom'gol's south gate, and she counts everyone who heads down the Vine Road toward "
        "Booty Bay. Two travellers who went south this month never came back past her. Bloodvine raptors have been "
        "hunting the road where it fords the Veilfall, and she wants to know if that's where they ended up.",
        "Head down the Vine Road to the ford where it crosses the Veilfall. The Bloodvine raptors wait there because "
        "it's the one spot where you have to slow down. Thin them out, and while you're standing in the ford, look "
        "at the stones and the water around them. If somebody went into that river, I'd rather hear it from you "
        "than from their family.",
        "Nothing in the ford? I wanted there to be. A body in the water is something I could write down and send "
        "home. Instead I've got two names on my list and no idea where they went, so their lines stay open. You "
        "walked it properly, and that's more than the garrison would spare me.",
    ),
    "stvc_ganger_cut": (
        "Road-Ganger Dubo runs the troll gang that keeps the Vine Road clear of bloodvine. The Gurbashi pay him for "
        "it, since nobody walks to their arena through raw jungle. Bloodvine grows back over a cut road in about "
        "nine days, and his gang has been short of hands since the rains.",
        "Dis road got a crown in da middle so da rain runs off, and da kerb stones hold it up. Da bloodvine comes "
        "right through da kerb. Bring me lengths of cut vine from along it, mon, and kill dem greenwater adders "
        "while you're down dere. Dey nest in da drains and bite my boys when dey reach in.",
        "Da drains are runnin' again. I only told you about 'em, I never asked you to clear 'em, but I ain't "
        "complainin'. Tout Bexxil, da goblin up on da arena apron, been askin' for a fighter nobody's seen yet. I "
        "gave her your name. You can thank me or curse me after.",
    ),
    "stvc_tout_entry": (
        "Tout Bexxil takes bets on the Gurbashi Arena from a board in Booty Bay's tavern, and she's already "
        "entered you in the fights without asking. She needs the card to be worth watching. Right now the Gurbashi "
        "drovers are sending underweight beasts into the pens and signing them in at full weight, and thin fights "
        "mean thin betting.",
        "The beast-drovers are working the crates right here on the Gurbashi Flats. Put some of them down and "
        "bring me their stock tallies, the papers where they sign in the weights. And yes, I bet on you without "
        "ever seeing you fight, and that's exactly why. Nobody down here has seen you lose, so the odds on you are generous, "
        "and I like generous odds.",
        "You did it out in the open where the bettors could see, and now your odds have dropped. That's bad for "
        "me, since I was going to collect on those odds. I've had to put my own money behind you to keep the price "
        "steady. So now we're partners, whether either of us wanted that or not.",
    ),
    "stvc_tout_staked": (
        "With her own money riding on you, Bexxil can't walk away from a bad afternoon any more. Your entry chit "
        "has to reach the arena gatehouse before you can fight, and the Gurbashi gate crew don't take a goblin's "
        "word for anything.",
        "Take this chit north up the apron to Gatehouse Broker Zul'tamo and put it in his hand yourself. The "
        "Gurbashi gatekeepers will try to stop you, because that's what they're paid for. Fight through them, and "
        "get a look at the way into Gurbashi Arena while you're up there. Don't dawdle, the drums start at dusk.",
        "Bexxil filled dis out herself: name, weight, reach. Where it asks for your home, she wrote 'outsider.' "
        "Don't take offence, mon. We had a box for fighters from far away long before your kind came through, and "
        "da bettors like it. You're on da list. Come down when you hear da drums.",
    ),
    "stvc_fenn_weather": (
        "Ordek Fenn dries herbs on a rack at the edge of the Veilfall Basin and sells them to Grom'gol. He's glad "
        "to see a new face, and he has a question for you that has nothing to do with the jungle.",
        "There's a moss that grows along the lip of the falls, only where the spray reaches. Gather me a good batch, "
        "and clear the snapjaw leechswarms out of the slack water below the pool while you're there. And think "
        "about this on the way: where you come from, does the rain come in a season, or all year round? Everything "
        "I know about plants assumes a wet season and a dry one.",
        "Rain comes in a season where you're from? Good, then half of what I know still holds. Now look at this "
        "moss. It only grows where the spray of the falls reaches, and there's only one waterfall. I've been "
        "selling it to Grom'gol as a common herb for two years. I should have been charging three times as much.",
    ),
    "stvc_fenn_lit_fall": (
        "At night the curtain of the Veilfall glows. Ordek told himself it was moonlight on the water. Water "
        "doesn't glow like that, but lamps do. If someone's lighting lamps behind the falls, then somebody has been "
        "living in that cave the whole time he's been camped outside it.",
        "Nightpelt panthers prowl the edge of the basin at dusk, and they're the real reason I've never gone round "
        "to look. Deal with them, then walk round to the mouth of the Veilfall Cave, just south of my rack, and "
        "tell me if there's a door. I've spent two years telling myself there isn't.",
        "Carved steps and a lamp bracket with oil still in it? Then I've been camped on someone's doorstep for two "
        "years, selling their moss, and I never once knocked. I should have looked. Leave me be for a while, would "
        "you? I need to work out what I'm going to say to them.",
    ),
    "stvc_zuljana_names": (
        "Mapmaker Ashi has the cave behind the Veilfall on her map as 'the waterfall cave', because that's what "
        "the garrison calls it. The Zul'Rath trolls who keep it have a name for it carved on each of its terraces, "
        "and Zul'jana has asked Ashi to get every one of them onto the map before the garrison's name is the only "
        "one left.",
        "Each terrace in the Veilfall Cave has a name stone set in its edge. Bring me those stones. The Zul'Rath "
        "mistcallers won't let you stand on a terrace long enough to read one, so you'll have to go through them "
        "first. Zul'jana doesn't like asking that, and neither do I, but otherwise the map gets a garrison name by "
        "spring.",
        "Zul'jana read them for me. The last name on these stones isn't for the cave at all. It's for the water, "
        "and it's the same word the Gurbashi use for the sand on their arena floor. One means a river and one "
        "means a killing ground. Take that question to the arena gatehouse. They keep the oldest records in this "
        "jungle.",
    ),
    "stvc_zuljana_font": (
        "Deep in the Veilfall Cave, at a pool called the Font, the Zul'Rath measure the falls every morning with a "
        "knotted cord and keep the old cords to compare. Three years ago the water rose in the wrong season, and it "
        "hasn't gone back down. Zul'jana wants those cords to see how far it's changed.",
        "Go down into da Veilfall Cave to da Font and bring me da tally cords. Spraywater elementals rise out of "
        "dat pool, so expect a fight while you're gatherin'. Leave da shrine alone, it ain't ours. And don't try to "
        "read da knots, just carry dem back and I'll do da readin'.",
        "Every one of dese says da water's been high for three years and never come down once. A river only does "
        "dat if somethin' new is feedin' it, and nobody's gone to see what. I ain't takin' dis to Overseer Mokra "
        "yet. She writes down everything, and once it's written she has to act on it.",
    ),
    "stvc_veilspeaker": (
        "The Veilspeaker who leads the Zul'Rath has decided Ordek's camp is why the falls changed. His shrinekeepers "
        "came up and took Ordek's drying rack apart without a word. Ordek tried to make peace and went in with a "
        "gift of lamp oil. He came back out with nothing settled, and now he's run out of options.",
        "I've thought about this for four days before asking. The Veilspeaker is down in the Veilfall Cave on the "
        "south shore of the plunge pool. He's sure my camp is what's wrong with his water, and I can't talk him out "
        "of it. He's right that the ground is his, and I'm right that I've got nowhere else to go. Go down and end "
        "it. Just don't tell me it was quick.",
        "Not quick, then. I'm glad you didn't lie to me. I've got his lamp bracket, the one from the cave mouth, "
        "and I'll hang it on my rack, since nobody else is going to make him a memorial. I still have to decide "
        "whether to stay. Killing him didn't change whose ground this is.",
    ),
    "stvc_garza_report": (
        "Watcher Garza was posted from Grom'gol to watch the only road up onto the Mosh'Ogg Shelf. In her second "
        "week she dropped her spyglass into the notch, and it was signed for and stamped with her number. Every "
        "report she's sent since has been guesswork.",
        "The Mosh'Ogg rockthrowers grab anything shiny and pile it on the midden behind their camp up here on the "
        "shelf. Put them down and bring me the made things off that pile, not the bones. If my spyglass is in "
        "there, it'll have a brass collar with my number stamped on it. If it isn't, my next report has to say "
        "something different from the last nine.",
        "There it is, brass collar and all. I've felt sick about that for eleven weeks. Now look at what was lying "
        "next to it. That's a stamped crate nail from the Gurbashi arena stores, and arena stock has no business up "
        "this road. The ogres have been trading with the arena gate. That's a real report, and I'll have to own up "
        "to the spyglass in it.",
    ),
    "stvc_shelf_road": (
        "The Mosh'Ogg hold this shelf because there's only one notch up through the mesas, and they were standing "
        "nearest to it when it mattered. Garza's next report will admit to the lost spyglass, and she'd like some "
        "good news in it too.",
        "Clear the maulers off the approach and the spellgorgers out of their clearing at the top. Then walk into "
        "the clearing on the Mosh'Ogg Shelf, so that someone from this post has actually stood in it this season. "
        "I've spent eleven weeks reporting on a camp I've never set foot in, and I'm done guessing.",
        "They moved their whole camp a few feet west, built the fire back up, and sat down again. That's them "
        "settling in, not running. They've held this rock for generations by shuffling around on it, because nobody "
        "else has ever wanted the notch badly enough. I've been calling them a garrison in my reports. I'll correct "
        "that.",
    ),
    "stvc_ulua_netsetter": (
        "Netsetter Ulua has fished the Snapjaw Marsh all her life, off the same landing her mother used. Her hands "
        "have been stiff since the cold month and she can barely close them. She won't ask for help outright, but "
        "she needs someone to pull her lines this week.",
        "My lines are out past the gangplank where the water goes still. Pull them, bring in the catch, and reset "
        "them exactly the way you found them. The snapjaw crocolisks have been tearing the nets to get at the fish, "
        "so deal with them too. And don't tell anyone in Booty Bay you did this. I sell there.",
        "You reset them right, which I didn't expect. Let me ask you something, and then we'll leave it. Where you're "
        "from, is there water like this, slow and brackish? Does anybody fish it? I'd like to know whether my "
        "trade exists anywhere else, in case it stops existing here.",
    ),
    "stvc_wager_slip": (
        "You cut it out of a crocolisk's stomach, which isn't where paper belongs. It's a betting slip, stiff with "
        "salt and brown at the folds but still readable: a fighter's name, a round, and the odds. The odds are good "
        "enough that whoever held it must have known something. And someone carried it out into the marsh.",
        "The handwriting is small, quick and neat, and Tout Bexxil up on the arena apron writes exactly like that. "
        "Before you take it to her, go back through the Snapjaw Marsh and look along the water by the gangplank. "
        "Kill the snapjaw crocolisks on the way, in case whatever else went into that water ended up inside one of "
        "them.",
        "She knows the handwriting before she's turned the slip the right way up, because it's hers. 'That fight "
        "never happened. I wrote this and priced it, then the house cancelled the round and I bought every slip "
        "back.' She turns it over twice. 'Where in the marsh, exactly? There's only one reason to carry a dead slip "
        "out into the water, and that's so nobody ever finds you holding it.'",
    ),
    "stvc_arena_first_four": (
        "Gatehouse Broker Zul'tamo keeps the arena's fight list, as his father did before him. He doesn't care who "
        "wins, only that the list is right. Before you go down, he'll tell you what nobody in Booty Bay can: how "
        "the arena is built, and how its first two fighters fight.",
        "Go down da stair into Gurbashi Arena. You can only walk da ring one way round, because da mason never cut "
        "da other passages. First is Vek'tar da Unbeaten. Keep da pressure on him, because once he's worn down he "
        "starts drainin' da fight back out of you. Then Grateward Mok'tal. He keeps a fire burnin' under da grate "
        "and shuts down whatever you answer it with. Nobody beats Mok'tal by bein' patient.",
        "Two names off da list. Da drum crew had you down for a slow fight and lost money on it, and I enjoyed dat "
        "more than I should. Da drums are how da bettors time each round, and a good crew can call how a fighter "
        "will open. Dey'll still have you on da slow count tomorrow. Bein' wrong once is cheaper than learnin' a "
        "new rhythm.",
    ),
    "stvc_arena_pair": (
        "Now that the bettors know whose money is on you, the arena has changed your next fight. The handlers have "
        "put Jin'sha in the pit with Rakjan, which they only do when the house wants a round to stop being "
        "predictable. Zul'tamo tells you plainly. It isn't his decision, but it's on his list.",
        "Rakjan da Ribcracker is loud, but he ain't da danger. His handler Jin'sha is. Spend da fight on da big one "
        "and you'll die to da small one. After him comes Zul'gar Hammerfall, who guards da passage to da hall. "
        "Somebody from his family has stood in dat doorway for three generations. He swings three times, all of "
        "dem huge, and one strips your armour off. Hittin' him harder won't change dat, so plan for it.",
        "Four names crossed off. I'll tell you somethin' I shouldn't. Da house almost never opens da centre gate "
        "more than once a season, but it's opened twice dis year. Da first fighter went through eleven days ago "
        "and nobody's said his name since. I've started to wonder if dat gate is a prize or a way of gettin' rid "
        "of people.",
    ),
    "stvc_arena_favourite": (
        "Your wins have made Bexxil's bet on you worth far more than she paid, so she's sold most of it on. What's "
        "left of her stake pays best if you last a long time against Jen'shala and then lose. She's decided to "
        "tell you that to your face.",
        "I'll be straight with you. I sold most of my stake this morning, and the part I kept pays best if you last "
        "eleven minutes and then fall. I'm telling you because you'd have found out anyway, and I'd rather it came "
        "from me. Jen'shala drains the fight out of you and strips your armour, and the house has never once put "
        "her on the sand to lose. Go down, do what you're going to do, and collect your winnings in Booty Bay.",
        "The Quiet Man counts out your winnings without looking up. 'Bexxil isn't ruined, just annoyed, and with "
        "her that's close enough. Our betting sheet has a column for where each fighter comes from. Since you lot "
        "started walking down that stair, it's the only column anyone argues about, and tonight I've got to work out "
        "the odds on it again.' He finally looks up. 'Stay away for a season. Let the numbers settle.'",
    ),
    "stvc_scrip_drums": (
        "Scrip is a boy in Booty Bay who has never been more than a mile from the cove. He's heard the arena drums "
        "carry down the coast on still nights, and he's convinced they're made of gorilla hide. He'll pay you in "
        "the only thing he's got: knowing which crates on the pier aren't nailed down.",
        "Go up the road to the arena and look at the drums for me. How many, how big, and what they're made of. "
        "And kill some of the big drumhide gorillas, because that's a clue, they're named after the drums! Bring me "
        "bits of their hide so I can feel it. Oh, and stand on the Gurbashi Flats in front of the gate so you can "
        "tell me how many people fit.",
        "No, you looked at the wrong ones! The big drums are crocolisk belly, and the gorilla ones are only the "
        "little ones? That can't be right. He folds the scrap of hide and tucks it in his shirt anyway. 'Was anyone "
        "down there from another world, like you? Hobb says the ones who came through always lose their first "
        "fight. I said that can't be true, and he said to ask someone who'd know.'",
    ),
    "stvc_crate_nail": (
        "You turn it over in your hand. It's a crate nail, square cut and flat headed, the kind used in shipping "
        "timber, and it's stamped with a run number. You found it on the Mosh'Ogg Shelf, up a road that only leads "
        "up. Numbered nails come in runs, and a run means a clerk somewhere wrote down where the crate went.",
        "Only one man in Stranglethorn would know a run number on sight: Clerk Bexx, behind his desk in Booty Bay, "
        "and he'll be insufferable about being asked. Before you head down off the shelf, deal with some of the "
        "Mosh'Ogg brutes. They hold the notch and the nailed timber is in their camp, so you'll want to be sure of "
        "that before you tell a clerk.",
        "Clerk Bexx looks at it for less time than it takes to read the number. 'That one's mine. That run left this "
        "office for the arena gate, weighed and signed. It should be in a pit of broken crates behind the arena, "
        "not on an ogre's rubbish pile. Someone is opening my crates before the gate counts them. And what bothers "
        "me most is that the stamp is still readable, which means someone could audit me with it.'",
    ),
    "stvc_cord_sealed": (
        "Zul'jana has the Font's readings, but she won't give them to Overseer Mokra. Anything written down in a "
        "garrison has to be acted on by the end of the week. What these readings need is someone whose whole trade "
        "is measuring water, and who answers to nobody. There's no one like that in this jungle.",
        "Bring me more cords from da Font, fresh ones, so nobody can say my numbers are a season old. Then go up to "
        "da Plunge, da lamp gallery above da pool in da Veilfall Cave, and stand behind da brackets. Dere's an old "
        "waterline on da stone and a newer one above it. Look at it yourself. I won't send word about somethin' "
        "you ain't seen.",
        "Sealed, and my name's on da wrap. Far to da north, in Tarren Mill, one family has written down da height "
        "of da same river for sixty years, and a man at da sluice has worked it for twenty-two. Neither of dem "
        "answers to a commander. Dat's who gets dis. I'm goin' round my own camp to send it, and I'd rather do dat "
        "than hand Mokra somethin' she has to act on by week's end.",
    ),
    "stvc_north_leg": (
        "Windrider-Keeper Pazzik has flown freight out of Grom'gol since the camp was one post and a rope. His route "
        "north used to cross the Veilfall Basin, where warm air lifted his wyverns over the trees. Since the falls "
        "rose three years ago, the air there has turned cold, and the long way round costs him a day he doesn't get paid for. "
        "Limewing bats from the cave have taken over the old perches.",
        "Kill the limewing bats, in the cave where they sleep, not on the perches where I've got beasts on the "
        "ground. Then stand on the old perch at the edge of the Veilfall Basin and feel the air coming off that "
        "water. You'll see why I won't land there. Last thing: this bundle from Zul'jana goes north to Ghulrak at "
        "Tarren Mill. I'm not flying the basin and he's not coming south for one package, so put it in his hands "
        "yourself.",
        "No cargo number, no weight, no seal, only a troll's name in her own hand. That's not freight, that's a "
        "favour, and I'll carry it anyway. Sluice-Keeper Pate is up at the weir. He's been waiting for somebody "
        "with more learning than him to look at those cords. You're not that, but you've carried the water this "
        "far, and that'll do.",
    ),
    "stvc_sluice_book": (
        "Sluice-Keeper Pate works the gate on the Tarren Mill race. When he lowers it the mill wheel stops, and the "
        "whole valley knows his name within the hour. He's done the job for twenty-two years. He has Zul'jana's "
        "cords flat on his bench and has read them twice, and what he thinks of them he'd rather say at the weir.",
        "Come up to the weir with me and ask what you came to ask. I'd rather do this with the water loud beside "
        "us, because I trust what I say more when I'm standing next to the river. Mind the walkway. A few of those "
        "boards are new, and a few are ones I keep meaning to replace.",
        "There, you've heard it from me with the river right beside us. Take the cords down to Aldous Reed at the "
        "mill. His family has sixty years of this water in one ledger, and he can tell you whether a river has ever "
        "done this before and come back down. I'm not saying the numbers are wrong. I'm saying I can't check them, "
        "and I'm a man who checks.",
    ),
    "stvc_reed_verdict": (
        "Aldous Reed's family has milled the Tarren Mill race for sixty years and written its height down every "
        "week in one ledger. He's laid the jungle's cords against his own records and found the same pattern twice, "
        "but never a third time. He wants a proper marker set at the falls, so somebody can measure it again.",
        "This is a gauge board. Oak, numbered, cut by my father for a weir that silted up years ago. Take it to the "
        "Veilfall Basin in Stranglethorn and set it in sound stone above the falls, low enough for a short person to "
        "read. The spraywater elementals will come up out of the water while you work, so be ready to fight them "
        "off.",
        "Zul'jana reads Reed's note twice, then rests her hand on it. 'He's seen a river do dis twice in sixty "
        "years, once in a big melt and once when a lake upstream gave way. Both times it came back down. Ours has "
        "been up three years. He says he's started datin' his ledger from da change, because da old dates stopped "
        "meanin' anything. So I'll be tellin' Mokra after all.'",
    ),
    "stvc_zultamo_courses": (
        "Zul'jana sent you to ask the gatehouse why the Zul'Rath word for the Veilfall's water is the same as the "
        "Gurbashi word for the arena's sand. Gatehouse Broker Zul'tamo is the third of his family to keep the fight "
        "list, and nobody has ever asked him that. He puts down his pen, which for him is a big event.",
        "Come down da stair with me and we'll talk standin' in it, because half of what I'll tell you, you need to "
        "see. Wait at da Sand Gate, at da foot of da stair, where da ring looks like it opens both ways. Den ask "
        "your questions. I'll answer what I can and be honest about what I can't.",
        "Dat's everything da gatehouse knows. Da rest is south, under da sea, in a hall my family stopped visitin' "
        "before my grandfather was born. I'm sixty-one and I run a gate, so I've never been. If you go and come "
        "back, come here first. I'd like to hear about it from somebody who's stood in it.",
    ),
    "stvc_centre_gate": (
        "The first fighter through the centre gate this season never came back. His kit came back up, and the "
        "gatehouse hung it on a peg and counted it, but there's no name to write on his line. Zul'tamo has kept the "
        "fight list his whole life, and this is its first gap in three generations.",
        "Take his kitbag down past da gatekeepers to da Hard Round, da dead end in front of da centre gate. Dey'll "
        "try to stop you, because guardin' dat spot is older than my family. Stand where he stood, den bring da bag "
        "back up and hang it on its peg in da gatehouse. Da board never printed his name, because he came from "
        "somewhere else and da column stayed blank.",
        "Back on its peg. Here's what I'm writin' on his line: a fighter of no recorded house, won his way round da "
        "ring, went into da hall, and never came out. He came from another world, won four fights nobody wrote down "
        "properly, and dat's all dat's left of him. I never knew a man could be on my list and still not be on it.",
    ),
    "stvc_drum_callers": (
        "The arena drums aren't just music. They're how the bettors time each round, and a round lasts as long as "
        "the drum crew says it does. Bexxil has several afternoons of fights that ran long by exactly the same amount, "
        "and she's worked out that the drum-callers are being paid off.",
        "The drum-callers are out on the Gurbashi Flats by the gate. Take them down where the crowd can see, then "
        "get me more of the stock tallies from the crates. Signed-in weight is worth more than coin down here, "
        "because nobody has to count it. Bring me the paper, because if I'm wrong about this I've just had "
        "musicians killed over nothing.",
        "Same handwriting on every one, and it matches the drovers' tallies. So the underweight stock and the slow "
        "drums are one scheme. I'm not taking this to the house, since the house takes a cut of both. I'll just set "
        "my odds by it from now on. It isn't honest, I know, but I paid for this information.",
    ),
    "stvc_limeback_lamps": (
        "The glow behind the Veilfall went out four nights after the Veilspeaker died, and Ordek has sat watching "
        "the dark water ever since. For two years he told himself nobody lived behind the falls. Now it's true, "
        "and he knows why.",
        "With nobody keeping them down, the limebacks have climbed up off the lowest terrace. Stop them before they "
        "find the ramp out. Gather me more spray moss while you're at it, since I haven't stopped selling it. Then "
        "go into the Veilfall Cave, just south of here, and down to the lowest terrace. There's a jar of lamp oil "
        "under the bracket. The Veilspeaker told me where it was, the day I brought him a gift.",
        "You lit them? I only asked you to look. Now the falls glow again, and every trader on the north road will "
        "go on thinking it's moonlight. I'm going to keep those lamps trimmed. Not to make up for anything, because "
        "he knew I didn't share his faith. But lamps that somebody kept burning for generations shouldn't go out "
        "over a tarp and a patch of dry rock.",
    ),
    "stvc_ulua_cold_month": (
        "Ulua's marsh is brackish, and her whole trade depends on that. Her nets are cut for fish that live where "
        "salt water and river meet. For about three years now, fresh water has been pushing down into the Snapjaw "
        "Marsh, and her catch has started coming up wrong.",
        "Pull the far lines this time, out where the marsh stops being mine. Clear the snapjaw leechswarms out of "
        "the slack water first, or you'll lose fingers. Then walk south-west to the far edge of the Snapjaw Marsh, "
        "past the last stake, where the grey reeds turn green. That line has moved in my lifetime, and I want "
        "someone besides me to have stood on it.",
        "Green reeds in nearly every net. My mother would have thrown the whole lot back. So the line has moved, "
        "and now two of us have seen it. I'll keep fishing until it stops paying, and then I'll be a woman of sixty "
        "with one trade and no marsh to practise it in. My hands were going to make that choice soon anyway. The "
        "water just got there first.",
    ),
    "stvc_ganger_milepost": (
        "Dubo's gang is paid by the furlong, and the mileposts along the Vine Road decide how many furlongs "
        "they've cut. The stones have stood at the kerb with their carved faces pointing north since his father's "
        "day. Now some of them have been dug up and reset facing the wrong way, by somebody who knew exactly what "
        "they were doing.",
        "Bloodvine raptors come down on da road south of here, and dey go for a man when he's kneelin', which is "
        "all dis job is. Kill dem and bring me more cut vine from da kerb. Den walk south along da Vine Road to da "
        "long milepost where it bends, and tell me which way da carved face is pointin'. North is Grom'gol. I never "
        "seen one turned in my life.",
        "Turned south, all of dem, and packed in with fresh gravel. Dat took tools and a whole afternoon. South is "
        "Booty Bay, so dat stretch of road pays out from da Bay now instead of da Gurbashi. Somebody made my gang "
        "da Bay's gang for a mile and a half without tellin' me. I ain't movin' dem back yet. First I want to know "
        "who's gettin' da bill.",
    ),
    "stvc_notch_tithe": (
        "Garza's report now has the crate nail in it, proof that the Mosh'Ogg and the arena gate have been "
        "trading. A tribunal won't settle for a nail, though. They'll want the goods from the midden, the drovers "
        "who signed for the weights, and a witness they can question.",
        "Bring me more stamped goods off the Mosh'Ogg midden, same as before. Then head south-west down the Vine "
        "Road to the crates and thin out the Gurbashi beast-drovers, so that end of the trade is short of hands "
        "when my report gets read. I'll be straight with you. A tribunal wants a witness with a village and a "
        "commander behind them, so I can't name you. You'll be 'the unnamed party who recovered the items.' That's "
        "the form, not my opinion of you.",
        "Stamped goods, and a drover line that'll be thin for a week. Here's the report. You're in it as the "
        "unnamed party, and I've signed underneath that the items came to me just as described. That puts my own "
        "post behind your word. It's one line of small writing on page three, and it's the biggest thing I can "
        "give. Eleven weeks ago I wouldn't have signed it.",
    ),
    "stvc_scrip_second": (
        "Scrip didn't take it well when you told him the big drums are crocolisk belly. Four days later he still "
        "hasn't come round, but he hasn't let it go either. He's worked out a way to settle it, which is more than "
        "most people in Booty Bay ever manage.",
        "I've got questions and I wrote them on my hand, so don't go anywhere. And I need you to kill some of the "
        "crocs in the Snapjaw Marsh. Not for the hide, for how big the biggest one is. If none of them is as wide "
        "across the belly as a drum is across the top, it can't be croc, so I'm right and Hobb's wrong. That's "
        "called a test. Clerk Bexx told me about tests.",
        "All right, it's croc. I've had it wrong for two years and I told six people. He sits on the crate he isn't "
        "supposed to sit on. 'Here's what I don't get. Everyone down here knows what the drums are made of, and "
        "nobody told me. Not the harbourmaster, not Bexx, not one sailor. They let me say gorilla for two years. "
        "Was it funny? Because I'd have told me.'",
    ),
}

SOUTH = {
    "bb_landing_fee": (
        "Tollkeeper Nizzik sits halfway down the only ramp into Booty Bay, so she never has to chase anyone. The "
        "landing fee is four silver, or an afternoon's work, and she'll take either. The work is real: capecrest "
        "raptors have learned that a crate means food, and the carters have started dumping their loads at the "
        "treeline above the gate.",
        "You've already landed, so we're only arguing about how you pay. If you've got no coin, go back up the ramp and "
        "clear the capecrest raptors off the cart track. Walk the whole apron above the way into Booty Bay, not "
        "just the first stretch. I'll mark you paid when the carters stop leaving loads in the trees.",
        "You're paid up, and nobody can put you off these boards now. That's what you bought. And no, I don't keep "
        "a book of who comes up this ramp. The Baron's never asked me to, and I've never offered. The fee's the "
        "same for everyone. You won't get even that much fairness in Ratchet.",
    ),
    "bb_barons_name": (
        "Baron Revilgaz doesn't rule Booty Bay. He just decides which ships leave on which tide, and in a port "
        "that comes to the same thing. There's a Bloodsail camp on the beach at the far end of the shallows, and "
        "he wants to know how big it is. Four people have already given him four different numbers, each with a "
        "reason to bend it.",
        "Let me explain, because most people get this wrong. A ship that doesn't arrive costs me the cargo, the "
        "berth, and the next few captains who hear about it. Pirates aren't romantic down here, they're a cost. "
        "Go out to the camp in the Bloodsail Shallows, deal with the swabs, and count what's still standing. Then "
        "tell me the number you counted, not the number you think I want.",
        "The harbourmaster said forty-one, and everyone else said thirty or sixty or a hundred because "
        "they wanted something. So you can count, and you won't flatter anybody. That's rarer on these boards than "
        "courage, and I pay better for it. Go and see Factor Weezel. He's been waiting a long time for someone to "
        "listen to him.",
    ),
    "bb_weezels_paperwork": (
        "Factor Weezel has an office on the upper gallery, a seal, a ledger, and the Steamwheedle Cartel's "
        "authority over this harbour, and he'll tell you at length that none of it has ever been formally "
        "withdrawn. He wants a complaint carried to Ratchet by someone who isn't on the Baron's payroll, and a "
        "countersigned copy brought back.",
        "This is my forty-first weekly complaint. The harbour book the Baron's clerk keeps isn't a legal record, "
        "it's a diary, and I've said so in writing every week since the road closed. Take this to Customs Officer "
        "Prynn in Ratchet. Once customs countersigns it, the port is ours again on paper. And you can't read a "
        "Cartel seal, which makes you perfect. Nobody searches a courier who doesn't know what they're carrying.",
        "Prynn turns it over, finds the seal, and drops it in a drawer without opening it. 'I countersign every one "
        "of these, because signing costs me nothing and refusing would cost me an afternoon. Take a look at that "
        "seal, though. The Cartel retired that design two years ago. Weezel knows it, and he keeps using it "
        "because a retired seal still looks official to anyone who doesn't check.'",
    ),
    "bb_what_actually_sails": (
        "Gazlowe signs every manifest that leaves Ratchet. The ones bound for Booty Bay are the only papers in his "
        "drawer that have never come back stamped by anyone. He doesn't care who runs Booty Bay. He wants this "
        "season's manifest stamped by whoever's actually in charge, because he can't bill for an unstamped season.",
        "Six hundred and twelve tons went from Ratchet to the cove this season. I signed for every ton, and nobody "
        "at the other end has acknowledged a single one. Take this down to Baron Revilgaz and get it stamped. I "
        "don't care whose stamp, just that there's one in the box with a date beside it. When someone finally asks "
        "who's been running that harbour, I want the answer written in somebody else's hand.",
        "The Baron reads the whole manifest, which takes a while, and then stamps it. 'Look at the box. It says "
        "received, not approved or cleared. Gazlowe will understand that word perfectly, and he won't be able to "
        "write one angry letter about it, because it doesn't promise him anything.'",
    ),
    "bb_the_fee_explained": (
        "Nizzik has been ordered to raise the landing fee on the Ratchet boat, and the small ships have already "
        "started beaching on the sand east of the cape to avoid it. Bloodsail bosuns are taking a cut from every "
        "ship that lands there. So the dodgers end up paying a worse toll to worse people, and Nizzik finds that "
        "funnier than she should.",
        "The fee on the Ratchet run goes up a silver next month. It wasn't my call, but I'd have made the same one. "
        "The ones dodging it are landing in the Bloodsail Shallows, east along the south shore, and paying the "
        "difference to a bosun with a knife. Go and break that up. Walk the beach track while you're down there, so "
        "the carters can see it's safe.",
        "That's done, and now they'll come back up the ramp and complain to me about the silver. Your four silver paid for "
        "the bruisers, that's all. Two captains who hate each other can tie up at the same pier and nothing "
        "happens, and that peace gets paid for one week at a time. That's also why I never write down where anyone "
        "comes from. A list like that only gets used later.",
    ),
    "bb_fipples_decision": (
        "Aide Fipple has told hundreds of people that the Baron is reviewing it. Grom'gol's berth grant has sat on "
        "the Baron's desk for eleven weeks, and the camp needs it to land a second airship. So Fipple has dated the "
        "Baron's stamp himself and is sending the grant north, and he'd like it to arrive before anyone notices.",
        "It's been eleven weeks, and I've been counting the days on my wall, which I know is a bad sign. It's his stamp. I didn't "
        "forge it, I only dated it, and the date's the one he should have put on it. Take it up the Cape Road to "
        "Berth-Master Zekka at Grom'gol. If anyone down here asks what you're carrying, you're carrying nothing and "
        "you've never met me.",
        "Zekka reads it twice, then takes another grant out of a box and lays the two side by side. 'This came three "
        "weeks ago by wind-rider. Different hand, same stamp, same grant. Your clerk thinks his Baron is slow, but "
        "he isn't. He sent this weeks ago and let the boy keep counting on his wall, and he'll have had a reason. Tell "
        "him or don't. I've got my berth either way.'",
    ),
    "bb_three_wrecks": (
        "Harbourmaster Sprocket keeps track of tides, berths, weather, and who's lying about which. Three wrecks sit "
        "on the sandbars off the south coast where every ship coming in can see them. Two are his, lost to the "
        "Bloodsail this season. The third bothers him more. It's older, and it's stuck on a sandbar that wasn't "
        "there three years ago.",
        "Walk out on the bars at low water in the Bloodsail Shallows. The Bloodsail cannoneers will shoot at you "
        "the whole way, so thin them out first or move fast. Skip the two fresh wrecks, I know what's in those. I "
        "want someone who's never had a reason to lie to me to look at the old one on the east bar.",
        "Cartel colours under the barnacles. I thought so, and I hoped I was wrong. That ship left this cove for "
        "the north with company money aboard three years ago and never arrived, and the sandbar it's sitting on "
        "didn't exist when it sailed. Either it hit something that wasn't there yet, or somebody put it there "
        "afterwards. And Factor Weezel has never once asked me about it.",
    ),
    "bb_oonas_name": (
        "Dagger-Hand Oona has been locked in the holding cage on the lower gallery for most of a year. They haven't "
        "hanged her and they haven't freed her, because the Baron hasn't decided which is worth more. She isn't "
        "asking to be let out. She wants revenge on one man, and she'll pay for it with what she knows about these "
        "waters.",
        "One of the Bloodsail bosuns in the Shallows sold me to these people for a boat and a share. I won't tell "
        "you which. Kill the bosuns, one of them will be him, and I'll sleep. Walk through their camp while you're "
        "at it. And don't look at me like that. You lot came here on a ship that fell out of the sky, and mine came "
        "out of a yard in Kul Tiras. We're both a long way from home, and only one of us is in a cage.",
        "Now listen, because I pay what I owe. The Bloodsail don't hold that beach, they hold the water. The camp "
        "on the sand is bait. It's pitched where the harbour tower can see it so it gets counted. Everything that "
        "matters to them is afloat off the sandbars, and the Baron has been paying for headcounts of a decoy for "
        "years. Sell him that, don't give it away.",
    ),
    "bb_cannon_count": (
        "Crane-Hand Durgo works the hoist at the foot of the ramp. In the spring he dropped a crate through the "
        "rail into the lagoon. It was gunpowder, consigned to nobody, and the Baron's clerk will be checking the "
        "season's books soon. Durgo has a theory about where that powder ended up, and he'd rather bet on it than "
        "say it out loud.",
        "Twenty silver says the Bloodsail are shooting at this harbour with powder that came out of this harbour. "
        "Whatever falls off my crane washes up east, on the ground west of the Drowned Coast. Go and look at the "
        "rocks there, and take out the Bloodsail cannoneers while you're at it. If those kegs are Booty Bay kegs, "
        "you win, I pay up, and you tell nobody.",
        "He pays before you finish your sentence, in coin, off his own belt. 'You won, fair and square. The sensible thing would be "
        "to tell the clerk, because a hole in the books is a hole in the books. I'm asking you not to. The clerk "
        "balances the books at the end of the season, and I've got until then to make it right.'",
    ),
    "bb_hold_the_water": (
        "Dockmaster Brek has three piers, one crane, and everyone wanting the middle pier. What he really sells is "
        "a berth where two captains who hate each other can tie up on the same tide without trouble. A convoy is "
        "due to wait off the sandbars for a tide before it comes in. Oona says the Bloodsail hold the water and not "
        "the beach, and Brek has decided to act on that.",
        "Four ships will wait off the east bar on the next ebb tide, and they're coming in without guards, because "
        "a gunship costs more than the cargo's worth. Out in the Bloodsail Shallows, thin the bosuns and the gun "
        "crews on the water side, not the camp. Let the camp sit there and be counted. I want that tide quiet, and "
        "I want the beach track walked so the carters will use it after dark.",
        "All four ships in and nobody hurt. Don't expect thanks, because that's not what this was. That tide was "
        "bought, and it's paid up for about a week, and then someone has to buy it again. People come down that "
        "ramp furious about four silver, and then they want the harbour to be safe. The four silver pays for a "
        "bruiser, and the bruiser is what keeps it safe.",
    ),
    "bb_kundaraz_road": (
        "Pilot Zan'rek guides ships past a reef that moves, using landmarks instead of a chart, since every chart "
        "of this coast has been wrong since the day the ground changed. One of his landmarks is a standing stone in the "
        "upper court of the troll ruin inland. The vines are pulling it down, and if it goes, the reef will start "
        "taking a ship every season.",
        "Da ruin has a name, Zul'Kundaraz, and it had dat name before dere was ever a cove here. Say it back to me. One "
        "road climbs up into it, and da Kundaraz vinecutters sit on dat road. Clear dem out and climb to da top, "
        "where da upper court opens up. My landmark is da standin' stone on da side facin' da sea. Tell me how much "
        "of it da vine still has.",
        "Still standin', and you cut da vine off da seaward face, which is da one I need. Dat'll save ships whose "
        "crews you'll never meet. And you said da name right. Kundaraz means da water comin' up. Not da sea, da "
        "water risin'. Da builders named dat city for a flood, on purpose. Nobody in dat port has ever asked me "
        "what it means.",
    ),
    "bb_stoneshapers": (
        "Scrip carries crates, watches crates, and rides out on the carters' wagons up the Cape Road, which is "
        "where he picks up his real trade: news. He's seen the Kundaraz trolls working stone in the great court of "
        "their ruin. They aren't clearing it or knocking it down. They're cutting new blocks, with a crew and a "
        "measuring rule. He knows that's worth money, but not why.",
        "Two silver for where to look, and you pay first, because I'm young, not stupid. Zul'Kundaraz, up in the "
        "hills, in the great court with the steps. There's a crew of Kundaraz stoneshapers cutting stone, and one "
        "of them calls out a number and the rest cut to it. Get past them, look at what they're cutting, and come "
        "back. If it's true I'm selling it to the Baron, and I need a grown-up to have seen it.",
        "They're cutting fresh blocks to a measure, in a city everybody here calls empty? That's four silver from "
        "the Baron, maybe five, and you get a cut for the walking. Before you go, is it true carts where you're "
        "from move without animals? The cart boys say nothing pulls them and they go anyway. I told them that's a "
        "lie, and they won't say how.",
    ),
    "bb_three_generations": (
        "Wind-Rider Zekki has flown over all three of the jungle's troll cities in one afternoon: the abandoned one "
        "in the north, the arena in the middle, and Zul'Kundaraz here. From the air, the drowned terrace below "
        "Zul'Kundaraz is laid out on the same grid as the arena floor and the northern courts. She needs someone on "
        "the ground to measure it, because from four hundred feet she can't tell a pattern from a coincidence.",
        "First thin out da Kundaraz terrace-watch on da shelf at Zul'Kundaraz. Den go down into da Drowned Shrine "
        "and out along da wall-tops, since da halls are flooded. Where two walls cross, dere's a plaza, da Pillar "
        "Court. Stand on it and look at how da blocks are cut. You've walked da arena, so you'll know if dey match "
        "its floor.",
        "It's da same measure. Three cities, three builders, one way of building, and da newest of dem is da biggest and "
        "it's under salt water. Dat bottom terrace was cut for da tide. Da halls have overflow channels and weirs "
        "at da junctions. Nobody builds dat into a hall dey mean to keep dry. Da sea didn't take Zul'Kundaraz, it "
        "was let in. But now it's risin' further than da builders planned, and dat part's new.",
    ),
    "bb_what_the_vine_keeps": (
        "The Quiet Man's whole trade depends on him never seeing who walks in. Two seasons ago he sold a Gurbashi "
        "buyer a stack of cut stones from Zul'Kundaraz and took the money, but the stones never left the ruin. A "
        "troop of gorillas moved onto them and won't budge, and the buyer has started telling people. That's the "
        "only part that costs him.",
        "I sold something before I'd picked it up. Everyone in my line does it, and most of us get away with it. "
        "The stack of dressed blocks is on the east side of Zul'Kundaraz, up high, past where the courts end. A "
        "troop of stonecourt gorillas has claimed the warm stone. Clear them off and look at the stack long enough "
        "to describe it, and I'll have a carter up there within the week.",
        "Then I can give him a date, and a date fixes everything. Thank you. I don't say that often, because it's "
        "not usually true. One more thing, and then I never saw you. I don't know where you're from, but I know "
        "which boat and which year, because I keep both. So does every third person on these boards who lost "
        "something when the world changed. They just don't say it where the Baron can hear.",
    ),
    "bb_the_salvage": (
        "Shipwright Vella can float almost anything, but she can't make fittings, because fittings come up the "
        "coast by ship and ships are what she's trying to fix. The drowned courts on the Drowned Coast are full of "
        "fittings from every ship the Saltscale naga have taken in three years. She has all the timber she needs. "
        "What she wants is the metal.",
        "Fittings: rings, pins, braces, anything forged. Not planks, I've got a whole jungle of planks and nothing "
        "to hold them together. The Saltscale salvagers carry it on a line, like keys. Take it off them on the "
        "Drowned Coast, then walk down to the way into the Drowned Shrine where the water starts standing. Bring me "
        "anything that rings when you drop it.",
        "That'll put two ships back on the water. And here's something you saw without noticing. The pile they're "
        "guarding is sorted: rings together, pins together, braces by length, in rows on a terrace. Naga don't "
        "guard salvage. They sort it. Something down there keeps stores, and you only keep stores when you've "
        "got a plan.",
    ),
    "bb_the_water_came_further": (
        "Lookout Minzi keeps the tide board at the clifftop gate. By her numbers, high water on the Drowned Coast "
        "now comes up past the mark the old troll masons cut for it. Not by much, about a hand and a half. She wants "
        "it measured against the masons' own mark rather than her board, because her board is only three years "
        "old and theirs is ancient.",
        "There's a mark cut into the lower wall of the ruin on the Drowned Coast, a line with a notch under it. "
        "Whoever cut it expected the water to come up exactly that far. Find it, wait for high tide, and see where "
        "the water really reaches. Clear out the Saltscale reavers first. They come up out of water you've already "
        "walked through, and that's worth knowing before you're standing in it.",
        "A hand and a half over a line somebody cut in stone, expecting it to hold for a thousand years, and it's "
        "all happened in three years. I'll put it on the board with the date beside it, because that's what a board "
        "is for. Working out what it means is someone else's job. The cape looks clear, by the way, which only "
        "means I can't see them yet.",
    ),
    "bb_tidecallers": (
        "Gurgle sells fish caught that morning, and he works the Drowned Coast because that's where the fish are. "
        "He won't go into the sea cave and has never pretended he would. Lately the shoals have been swimming into "
        "the cave against the ebbing tide and not coming out, down into the flooded halls. Fish don't do that on "
        "their own.",
        "For days now the shoals have gone in through that cave mouth on a falling tide. Fish don't swim uphill "
        "into a hole. Something's calling the water in, and the fish are following it. The ones doing it are "
        "down in the halls of the Drowned Shrine, and they aren't the naga. The Saltscale myrmidons will be in your way. "
        "The Kundaraz tidecallers are the ones you're after.",
        "Trolls down in the halls, with naga all around them and nobody fighting? Then they're not hiding, and "
        "they're not prisoners either. They're down there working. They're calling water into halls built to hold it, which is what "
        "they were always for, and the naga let them be because flooded halls suit naga fine. So my fish are "
        "somebody's job. I'd rather it had been a current.",
    ),
    "bb_myzrai": (
        "Baron Revilgaz has wanted the drowned terraces for three years. A terrace under four feet of water, piled "
        "with ship fittings, is the cheapest salvage on this coast. But nobody will lease a salvage site with a "
        "naga priestess in the middle of it. Tide-Priestess Myzrai holds the sanctum at the deep end of the flooded "
        "halls, and she's the only reason the Baron cares about her at all.",
        "I won't dress this up. I don't care what she is, what she sings to, or that the trolls down there were "
        "there first. I care that nobody will lease a site with her on it. Her sanctum is at the far end of the "
        "Drowned Shrine, past the second crossing, where the floor rises above the water. She'll use the whole hall "
        "against you. Get her out of the middle of my salvage.",
        "Read this line before I roll it up. The lease was drawn before you took the job, it's dated last "
        "week, and it's got my name on it, not the Cartel's. A hundred years on a terrace a troll cut for the tide a "
        "thousand years before anyone here was born. Weezel will file a complaint about it within the week. I'll "
        "have the first stone off it by then.",
    ),
    "bb_pit_stock": (
        "Bruiser Kolk keeps trouble off the quay, and anything above the gate is somebody else's problem. Four "
        "years ago he helped walk a shipment of raptors off a ship and onto Jaguero Spit, to be fed and kept until "
        "the Gurbashi sent for them for the arena. The Gurbashi never sent, nobody fed them, and they're still out "
        "there.",
        "Raptors, bought for the arena pits, landed on the spit and left there. Yes, I walked them off the boat "
        "myself and got paid for it. Go out along Jaguero Spit and put the pit-stock raptors down, all the way to "
        "the end. Take water, because the walk back is just as long. And they've survived four years out there with "
        "nothing coming in, so they won't fight like the ones on the Cape Road.",
        "How many did you see out there, not how many you killed? I counted thirty-one off that ship, because I was "
        "paid by the head. Two carters, four years apart, have told me the spit never held more than twenty-eight. "
        "You've walked the whole thing, and it's sand and palms with nowhere to hide. So three of them never made "
        "it onto the sand. Go and eat something. I'm going to stand here a while.",
    ),
    "bb_marlas_pot": (
        "Keeper Marla came down from Lakeshire eleven years ago to cook for a harbour that eats standing up. Her "
        "stock pot needs crab from Jaguero Spit, but nobody's checked the crab pots out there in a fortnight, "
        "because the boy who used to do it found better pay on the cart run. She's embarrassed about what she can "
        "pay, and she tells you so first.",
        "I can pay you badly and feed you well, and I want to be honest about which comes first. Go out to the "
        "head of Jaguero Spit and bring back spit scavenger crabs, as many as your arms can carry. Check the crab "
        "pots while you're there, so I know if the boy left them set or open. When you get back, sit at a table "
        "inside like a person, not at the rail.",
        "Look at the size of them! The boy left the pots set, so he meant to come back. I'll stop saying what I've "
        "been saying about him. Sit, eat that. Someone in here told me that where you're from, hot water comes "
        "right into your house through a pipe, whenever you like, and nobody thinks twice about it. Is that true? "
        "Don't tell me how. If it is, you've all come a long way down in the world.",
    ),
    "bb_weir_pins": (
        "Wind-Rider Zekki sent in her report about the drowned terrace and expected it to gather dust. Instead, a "
        "question came back down the wind-rider relay from Hillsbrad, asked for a man who keeps a sluice on a mill "
        "race there. He doesn't want to know how the trolls flooded the halls. Anyone can flood a hall. He wants "
        "to know how they controlled how fast the water came in.",
        "Ghulrak flies Hillsbrad and I fly the jungle, and we've been passing notes down the relay for years. He "
        "asked me something for his sluice-keeper that I can't answer from a drawing. The Kundaraz tidecallers set "
        "cut stone pins into the junctions of the walls. Go down into the Drowned Shrine, take the weir pins off "
        "them, then stand at the Pillar Court and see whether every junction has one.",
        "Tapered, every one of them, and no two to the same taper. That's not a plug, because you'd cut a plug one "
        "shape. That's a set. Somebody down there chooses which pin goes in which junction, depending on how fast "
        "they want the hall to fill. The clever part was never the water, it was the rate. Leave them with me, "
        "somewhere they'll be seen by someone who cares.",
    ),
    "bb_northern_sluice": (
        "Zekki will tell anyone who asks that nobody flies out of this jungle. There's no northern route because "
        "nobody's ever had a reason for one, and a crate of stone pins and a stranger's question is a thin reason. "
        "She's sending it anyway: north to Grom'gol, over the water, and up the relay to the roost above Tarren "
        "Mill, a route her birds have never flown.",
        "Grom'gol first, then over the water, then you're somebody else's weather. Ghulrak will have a bird waiting "
        "because I asked, and because he's wanted an excuse to prove this route flies. The pins go to Sluice-Keeper "
        "Pate at Tarren Mill and nobody else. Not the miller, not the commander, not whoever's closest to the gate. "
        "And keep the crate dry. They've been in water, but not that water.",
        "Pate carries the crate to the window, turns a pin against the light, and goes quiet long enough that you "
        "wonder if you've offended him. 'Every one of these is tapered. I've been cutting wooden wedges for this race for nine years and "
        "cursing them every spring. These are stone, and they're a set. I've been judging the rate by ear my whole "
        "life, and somebody worked it out properly and then let the sea have it.'",
    ),
    "bb_pates_measure": (
        "Sluice-Keeper Pate has a set of stone pins on his windowsill and no idea what measure they were cut to, so "
        "for now they're just ornaments. He wants the measure itself. There's a crew of Kundaraz stoneshapers still "
        "cutting stone in the great court above the drowned terrace, and their caller holds a notched rule that "
        "the others cut to. That rule is what Pate's after.",
        "Bring back the notched rules the Kundaraz stoneshapers use, and hold on to them. I don't want them sitting "
        "on a shelf in Hillsbrad where they mean nothing. Take them to Pilot Zan'rek in Booty Bay, the troll who "
        "guides ships past the reef. But first go down to the Flooded Halls in the Drowned Shrine, where the walls "
        "cross, and check how far apart the junctions are against the rule.",
        "Zan'rek lays the rule across his knee and counts along it with his thumbnail, twice. 'Same measure as da "
        "arena floor, and da northern courts. And every junction you walked is a whole number of dese apart, so da "
        "weirs went where da measure said, not where da water wanted. Tell your miller a troll worked out da rate "
        "before dere was ever a wheel on his river. And tell him I said it kindly.'",
    ),
    "bb_kundaraz_means": (
        "Pilot Zan'rek has watched a man in Hillsbrad put a thousand-year-old troll answer to work on a mill race, "
        "which is more than Booty Bay has ever done with anything he's told it. He's in a mood to talk, though he'd "
        "deny it. There's room beside him on the pier, and he's carried all of this alone for a long time.",
        "Dis ain't a job, so sit down. I gave dat port landmarks, safe passage past da reef, and da true name of da "
        "city up da road, and all it ever took was da landmarks. You carried da rest north to a miller. So ask me "
        "about da name, about da three cities, and about what your sluice-keeper is really holdin'. I'll answer it "
        "all once, properly, and den I'm goin' back to work.",
        "Dat's all of it, every piece I have, out loud in one afternoon. I didn't plan to do dat. I'd rather a "
        "troll had asked, or at least someone from dese boards. It was neither. By spring dose pins will be in a "
        "Hillsbrad mill race doin' da work dey were cut for, and I've decided dat's better than a box. Go on, da "
        "reef moves.",
    ),
    "bb_pins_not_planking": (
        "Shipwright Vella got two ships back on the water from the last batch, then had to stop. What came off the "
        "salvagers was a jumble, and a ship needs forged fittings in a full run of sizes. The Saltscale carry theirs "
        "sorted on lines. She's stopped finding that creepy and started finding it handy, and she knows that's the "
        "wrong way round.",
        "Whole lines of fittings, still strung, off the Saltscale salvagers on the Drowned Coast. A sorted line is a "
        "full set of sizes, and a full set is a ship. Loose pins are just a tin of loose pins, and I've got three "
        "of those. Work your way down toward the way into the Drowned Shrine. The ones up on dry stone carry what "
        "they found this morning. The ones in the water carry what they've been keeping.",
        "Every size, in order, nothing doubled and nothing missing. Somebody down there isn't just stacking "
        "whatever floats by. They're making up sets, and a set means they've decided what they're going to build. "
        "I'm going to put that out of my head and plank a hull, because I've got four captains shouting at me and "
        "no stomach for what it means.",
    ),
    "bb_the_hole_in_the_manifest": (
        "Aide Fipple balances the Baron's books at the end of the season, and this season has a crate of gunpowder "
        "in it that went over the crane rail, consigned to nobody. He knows whose problem a hole in the books "
        "becomes: the clerk's. But the Bloodsail bosuns keep tallies of what each beached ship paid them, and a bad "
        "tally next to a good one is still evidence.",
        "I'm not trying to catch Durgo. I like Durgo. I just need my numbers to add up when the Baron runs his "
        "thumb down the page, and for that I need someone else's numbers beside mine. Take the landing tallies off "
        "the Bloodsail bosuns in the Shallows, and deal with the swabs on your way in. A bosun with his crew around "
        "him is trouble, and a bosun on his own is just paperwork.",
        "Fipple lays the tallies along the gallery rail and goes very quiet. 'It adds up, to the crate. Every ounce "
        "that went over that rail came ashore on the beach and got paid for twice. I'm putting this in the Baron's "
        "box myself, with my own name on top. Eleven weeks of counting on a wall has cured me of waiting to be "
        "asked.'",
    ),
    "bb_thirty_one": (
        "Bruiser Kolk was paid by the head to walk raptors off a ship onto Jaguero Spit, and he counted thirty-one. "
        "The spit has never held more than twenty-eight. Every one of those raptors had a numbered brass tag "
        "punched through its shoulder. The tags are still out there, and so is the gap in his count.",
        "Bring me their brass tags, numbered and punched at the shoulder. It was a goblin shipment, so every raptor "
        "was a line in somebody's book. Walk out to the far end of Jaguero Spit for them. The ones near the water "
        "were picked over years ago, and the ones at the end are the ones nobody's bothered to reach. Take water, "
        "because the walk back is just as long.",
        "He lays the tags along the gate rail and reads the numbers without saying them. 'They run in a block, like "
        "mine always did, and then there's a gap where three numbers should be. Those three never went onto the "
        "sand. I was paid for thirty-one, and somebody got paid twice for three. Four years I've been counting the "
        "wrong thing. I won't do anything about it. I just wanted someone else to know.'",
    ),
    "bb_the_third_wreck": (
        "The old wreck on the east bar has Cartel colours under its barnacles. It left this cove with company money "
        "aboard and now sits on a sandbar that didn't exist when it sailed, and the Cartel's own factor has never "
        "asked Harbourmaster Sprocket a single question about it. Every Cartel ship has a builder's plate riveted to "
        "its frame, stamped with a shipyard, a year, and a number.",
        "Go out to the east bar in the Bloodsail Shallows at low water. The Bloodsail cannoneers will be on you the "
        "whole time, so give them something closer to worry about first. The builder's plates are on the frames "
        "inside the hull, where the barnacles haven't reached. Bring them up the gallery to Factor Weezel and put "
        "them in his hands. Watch his face. That's what I'm paying for.",
        "Weezel reads every plate, sets them down, and squares their edges before he speaks. 'That ship was "
        "written off the week the road closed, and I signed the write-off. Anything lost that week was lost to the "
        "weather. A ship lost the week before would have been lost by me. So no, I won't be filing this. Keep the "
        "plates. Sell them to the Quiet Man if you like. He'll know the year.'",
    ),
    "bb_quiet_mans_ledger": (
        "The Quiet Man once told you he knows which boat and which year, and in the same breath said he'd never "
        "seen you. He's decided to explain himself. Not to apologise, but because in his line of work a man who's "
        "understood is safer than a man people guess about, and they've been guessing about him all season.",
        "You've been carrying that question since the stones. Sit where I can see the stair and ask it properly, "
        "and I'll answer properly, which I do about once a year. Ask about the book, who comes asking after it, and "
        "what it's worth. That's everything I have, and it's more than I've given anyone. Don't expect to feel "
        "better afterwards.",
        "Now you know what's in the book and what it's for, and you'll notice I still have it. I'm not sorry "
        "I keep it. I'm careful about what I sell out of it, and that's the only virtue I've ever claimed. I didn't "
        "see you come in, and I won't see you leave. That was never a joke. It's the only protection either of us "
        "has.",
    ),
    "bb_marlas_question": (
        "Keeper Marla asked you a question over a bowl of crab, then let you leave without answering it, and she's "
        "been annoyed with herself about it for a fortnight. She won't let it happen twice. There's a table inside, "
        "away from the rail, with food already on it. She wants an hour of talk: about Lakeshire, about this "
        "harbour, and about what she's been turning over since you first walked in.",
        "Inside, at the table, not the rail. I've got three things to ask and I'll ask them in the order I thought "
        "of them, sensible or not: where I came from, where you've ended up, and the one I've been chewing on for a "
        "month. Eat while I talk. You won't get another sit-down meal in this town.",
        "She clears the bowls before answering her own question, so she's rehearsed it at the stove. "
        "'There, I've said it out loud to somebody, and now I can stop going over it at the pot. Come back in when "
        "it rains. Not for work, I won't have anything for you to kill. I'll just want the company, and I'd rather "
        "tell you that straight than have you work it out by accident.'",
    ),
}

NORTH = {
    "stn_the_weekly_shortfall": (
        "Storesman Pell counts every crate into Grom'gol and every crate out, and for eleven weeks the numbers have "
        "come up short by the same amount. He's written it off as spoilage twice and didn't believe it either time.",
        "My tally says crates go missing on the Vine Road between our south gate and the first bend. Vinecrest "
        "raptors work that stretch, and raptors chew things. Walk the road back the other way, kill the raptors you "
        "find, and if you come across a chewed crate, bring me its staves.",
        "These are cut, not chewed. Look at the ends. A raptor leaves splinters, and every one of these is sawn "
        "flat. I've spent eleven weeks writing 'spoilage' in my own hand while somebody walked off with my boards. "
        "I'd rather have been robbed loudly. At least then my book would be right.",
    ),
    "stn_cut_not_chewed": (
        "Overseer Mokra has Pell's sawn stave on her table and a camp that's losing crates every week. She's had it "
        "in her hand since dawn. She wants to know who's taking her timber, and where it's going.",
        "The Zul'Marosh stonehands, the stone-armed trolls off the crag, have been working my road. I want fewer of "
        "them on it. Then go and look at the Green Cut, where the road splits. That's where it stops being my road "
        "and starts being theirs. Don't bring me anything back, just tell me what you saw.",
        "You're telling me they stacked it? Not broken open, not eaten, not burned for warmth, but stacked "
        "and squared with the lids still on. That's worse than thieves. I can post a sentry against thieves. "
        "Somebody out there has a use for my timber, and a number in their head for when they'll have enough.",
    ),
    "stn_what_the_wood_is_for": (
        "Smith Dorgun has been rebuilding the same three things for three years, because nothing in this jungle "
        "dries out and every board in Grom'gol came off an airship. He's heard what Mokra found at the Green Cut, "
        "and he already knows what the trolls are doing with the wood.",
        "Bring me the battens they're cutting, the thin boards dressed to one length. You'll find them on the "
        "Zul'Marosh stonehands and the thornback apes. If they're dressing boards, they aren't burning them. Watch "
        "out for the apes on the Green Cut, east of the gate. They come for anything that smells of the camp, and "
        "my lumber smells of the camp all the way through.",
        "There's a dressed edge, and there's a lashing notch. Put them together and you've got a scaffold batten. "
        "They're standing on my lumber to reach something higher than they can climb. Three years I've been short "
        "of boards, and those trolls on the crag have been building with them.",
    ),
    "stn_one_road_four_names": (
        "Mapmaker Ashi has the road on her map as the Vine Road, because that's what a camp full of orcs has called "
        "it for three years. Zul'jana tells her that's the road's fourth name, and the shortest. Ashi wants the "
        "whole road walked from top to bottom, which nobody in Grom'gol has ever done, so the map can carry an "
        "older name too.",
        "Start with the road under your feet. Walk it from the ground west of the Green Cut all the way south to "
        "where it runs into Central Stranglethorn, and mind the coilvine pythons where the canopy comes down low. "
        "Come back and tell me what you saw, and I'll take it to Zul'jana. She's promised me one of the older "
        "names, and only one.",
        "Zul'jana gave me the name. Zul'marosh Dakka, the stair road. It never ran south to anywhere. It ran up, "
        "and the camp put a gate on the wrong end of it and called the rest of it vines. I've drawn it wrong for "
        "three years, then. It's less wrong now, which is the job.",
    ),
    "stn_the_other_half": (
        "Herbalist Mossa sells the half of the jungle that won't kill you. She buys her bark from a Darkspear "
        "supplier in Booty Bay who has started charging her a tariff. The same bark grows a couple of hours' walk "
        "south of the gate, around Mistvale Lagoon.",
        "I need mangrove bark, stripped off the roots on the water side, not off the trunk. The camp calls it "
        "mistvale bark, which is wrong but shorter. Go south to Mistvale Lagoon. The bloatspawn toads and the "
        "mangrove stiltstalkers pick the strips up when they root about, so take it off them. The stiltstalkers "
        "don't rush, but they don't stop either.",
        "Some of this is trunk bark. It'll do for a wash, but not for a draught, so I'll sell it as a wash and "
        "nobody will die of it. Two hours from the gate! I've paid a goblin's tariff for three years to have this "
        "same bark shipped round by sea.",
    ),
    "stn_standing_water": (
        "Field-Medic Sulaa has a ward full of men with rotting feet and a year of her own reports blaming the "
        "lagoon. She asks you quietly, at the back of her tent, and she'd rather you didn't mention it to anyone.",
        "I need to know what that water does to a foot. Go south to Mistvale Lagoon and walk the shore. Kill enough "
        "of the mistvale crocolisks that you can stand in the water for a while. I'm not asking you to be careless. "
        "I need somebody who isn't one of my patients to tell me whether that water rots a foot in a week.",
        "So it doesn't rot a foot? Then it's the boots. Every pair in this camp came off the airship in one batch three years ago, "
        "and it was a bad batch. The quartermaster who signed for them is still signing for things, and I've "
        "written four reports blaming a lagoon. Leave that out of anything you say in the hall. I'll tell him "
        "myself.",
    ),
    "stn_including_me": (
        "Berth-Master Zekka tells anyone who'll listen that everything in Grom'gol came off that airship, "
        "including him. A crate went over the side of the berth stair into the lagoon in the camp's first season. "
        "He wants it back, and he calls it 'stores' a little too often.",
        "They're camp stores, and they went into the water at Mistvale Lagoon, south of the gate, back when the mangroves still "
        "grew right up to the wall. The mistvale crocolisks moved in after, and they've dragged the bundles about. "
        "Bring them back. Watch the bloatspawn toads more than the crocs. Out there a toad looks like nothing at "
        "all until it's on you.",
        "That's not stores. That's a mask, a cord, and a drum skin that's been wet for three years, and my name's "
        "on the side of the crate in the cargo column, because that's how I came here, listed between the salt and "
        "the rope. I packed my own tribe's things into a camp requisition so nobody would read them out at the "
        "foot of the stair. Keep the cord out of sight.",
    ),
    "stn_less_wrong_than_it_was": (
        "Mapmaker Ashi has drawn the Zul'Marosh crag three times, and each sheet has more stair on it than the "
        "last. She's assumed she miscounted, because the other explanation is a ruin that's getting bigger.",
        "Go east to the Zul'Marosh Steps and stand in the lower court, then go on to the way into Rotvine Hollow "
        "above it. Count the courses of stone in both. I don't want a rough guess, I want a number, because I've "
        "got three sheets with three different numbers on them and every one of them is mine.",
        "More than the last sheet. Then it isn't a ruin. I've drawn it as a ruin for two years, with the cross "
        "hatching we use for something abandoned, and no chart I own has a mark for something people are still "
        "building. I'll have to invent one, and then argue about it with Orgrimmar for a year.",
    ),
    "stn_the_stair_ends_in_a_socket": (
        "Scout Hanzo has climbed to the top of the Zul'Marosh Steps, and nobody in Grom'gol has asked him about "
        "it, because nobody believed the stair went anywhere. It leads to a flat court with a socket cut in the "
        "middle and nothing standing in it.",
        "The stair is east of Grom'gol, past the Green Cut. The Zul'Marosh stairwardens hold the middle flights, "
        "and they hold them properly, which I've never seen jungle trolls bother to do. Fight past the second "
        "landing and bring me loose course stone off the stair itself. The old grey stuff, from where it's fallen, "
        "not from where it's still laid.",
        "Look at the faces. The old stone is dressed on every side but one, and you only leave a side rough if you know what's going on top of it. The new work is left rough in the wrong places, and whoever's laying the new courses has never seen "
        "the stair finished. They're copying the outside of something. Three years of careful work by people who "
        "don't know what it was for.",
    ),
    "stn_nobody_left_who_built_it": (
        "Zul'Marosh is the oldest troll work in this jungle. Zul'jana's own tribe has no story about building it "
        "and no story about leaving it, and she says a tribe with no story about a place was never there.",
        "Da Rotvine call demselves keepers of dat stair. But dey ain't, dey're sittin' in someone else's house callin' "
        "demselves family. Dere vinespeakers carry knot-cords, which are records, and I want dem. Dey're on da "
        "Zul'Marosh Steps, east of here, above da stairwardens. I want you to hear me say it plain: I'm askin' you "
        "to take a people's writin' off their bodies.",
        "Dese are all new. Every cord here was tied in da last three years. Dey kept no records before dat, and "
        "den somethin' started dem all at once, da way a camp starts a ledger when it decides it owns somethin'. "
        "Don't ask me what. I've got a guess, and it belongs further south, with trolls who never stopped keepin' "
        "theirs.",
    ),
    "stn_the_long_way_round": (
        "Runner Teza came back around Rotvine Fen instead of through it, and says she'd do it again. What she "
        "hasn't told anyone is that she came back without her courier pouch, and the fen has had it for three "
        "weeks.",
        "This is a favour, and I'm asking it as one. My pouch is out on the causeway near the landing in Rotvine "
        "Fen, east of here, in the rot where the fenrot creepers sit. Get out there, kill the creepers, and look "
        "where the gangplank meets the bank. I haven't reported it, and I'd like to keep not reporting it.",
        "It was six jars of lamp oil and a requisition number for the stores tent I walk past every morning? I "
        "went round a fen in the dark and worried for three weeks over lamp oil. What I can't get out of my head is "
        "that nobody's come asking about the lamp oil either.",
    ),
    "stn_three_flags": (
        "Signalman Grut raises two flags for an airship coming in and three for one that should keep flying. Three "
        "flags have gone up four times this season, each time with smoke rising over the fen, and the camp has "
        "gone a month short of supplies because of it.",
        "Smoke over the fen means fire, and fire in a jungle means a mooring nobody will risk, so up go three "
        "flags. Go east to Rotvine Fen and find out what's burning. The sourwater oozes are thick on that ground. "
        "Bring me the gas bladders you find on them and on the bloatspawn toads. If they're what's burning, I'll "
        "take the blame myself.",
        "It's gas, not fire. Those bladders come up out of the rot, and the oozes burst them, and this camp has gone hungry "
        "four times over a smell. Nobody ordered those flags. I read the smoke and raised them on my own judgement, "
        "every time. I'm going to write that down before somebody upstairs writes a kinder version for me.",
    ),
    "stn_the_hill_runs_warm": (
        "The water flowing out from under Rotvine Hollow is what rots the fen. Hanzo has put his hand in it twice "
        "to be sure of one odd thing: it runs warm. Caves don't run warm, and less water is coming out of that hill "
        "than is standing inside it.",
        "Go into Rotvine Hollow as far as the first standing water and look at the waterline on the wall above it. "
        "Rotvine stranglers hold the entry galleries, and they drop out of the roof, so keep your head up and your "
        "back to the stone. I just need a yes or a no: is there more water in that hill than is coming out of it?",
        "Then something's holding it back. A hill that fills and doesn't empty has a plug in it. Either it's "
        "stone, which doesn't move by itself, or it's alive, which does. I've been reporting that outflow as "
        "weather for two years. That's what you call something you haven't walked into yet.",
    ),
    "stn_what_was_holding_it_back": (
        "Zul'jana heard Hanzo's answer and didn't need the second half. The Rotvine didn't name their hill after "
        "the rot, she says. They named the rot after the hill, and they were right to.",
        "Somethin' called Rootmaw is growin' across da throat of da lower gallery in Rotvine Hollow, a mass of "
        "roots with a mouth, and it's been drinkin' dat cistern since before anyone alive started countin'. Kill "
        "dat thing, and deal with da Zul'Marosh drowned down dere. Look at da marks on dem before you take anything, "
        "because da drowned in dat hill ain't Rotvine, and dey never were.",
        "Dese were stairkeepers. Dese tokens are a count of stone courses. Dat's how a keeper signed for da stair he kept, "
        "and da number cut into dese is bigger than da stair is now. Da stair used to be taller. Somebody took da "
        "top off it and left no story about doin' it, and da Rotvine up dere are buildin' back toward a number "
        "dey found written on a dead man.",
    ),
    "stn_hapka_still_counting": (
        "Overseer Mokra has four turned-away supply ships, a fen that stinks when it rains, and a cistern in the "
        "hill above it that has just started draining into her water. She doesn't care about the stair. She cares "
        "about the smell.",
        "Whatever's at the bottom of Rotvine Hollow is in my water now, and no berth-master will bring an airship "
        "down into that stink. The Rotvine sent one of their own, Hap'ka, to keep the stair for them, and he "
        "drowned doing it. By every account, that hasn't stopped him. Go down to the sump and finish him, and bring "
        "me whatever he's carrying.",
        "Knotted cord, soaked through, and three years of it by the length. I gave it to the attache. She read it "
        "in front of me, rolled it up, and told me it wasn't for me. Three years I've held this camp, and I've just "
        "been told politely, in my own hall, that what I paid for isn't mine to read. Ask her about it when you're "
        "further south. She won't tell me twice.",
    ),
    "stn_keep_to_it": (
        "Sentry Vrak holds Grom'gol's south gate. The greenpelt panthers have started waiting right outside it, in "
        "broad daylight, and she's kept the reason out of her reports. The reason is in the ground outside the west "
        "wall.",
        "Greenpelt panthers are sitting right outside the gate. They aren't hunting the wall, they're waiting at "
        "it. Thin them out around the gate and along the first bend of the road. Stay on the road while you do it. "
        "There's nothing worth seeing off it on the west side, and I'd take it as a kindness if you didn't go "
        "looking.",
        "That's clear for about a week. For three years we've buried our dead outside the wall, because the ground "
        "inside the palisade is rock a spade bounces off, and the panthers have learned which day we do it. Are you "
        "staying? I'm not making conversation. I'm counting what I've got, and you're either in the count or "
        "passing through.",
    ),
    "stn_twelve_bunks_and_a_fire": (
        "Innkeeper Rukha has twelve bunks, a hearth, and the only dry wood in Grom'gol, which isn't dry. She needs "
        "resin to keep the fire going, and she's the only person in this camp who'll say out loud that she doesn't "
        "care where anybody came from.",
        "I need resin from the buttress trees. It burns even when it's wet, which is a small miracle. The "
        "rootgrubber boars dig it out of the bark and tread it into the mud, so you'll be taking it off them. And "
        "before you go: I don't care where you're from. Nobody behind this fence is from here, me included. Nobody "
        "else will tell you that, so I tell everyone early.",
        "That'll keep the fire going for a month. Your name's on a bunk now, chalked on the post like everyone "
        "else's. The ones who've been here since the camp landed still wander past every few weeks to check theirs "
        "is still up. None of them has ever asked why I'd rub it off. I've never rubbed one off in my life.",
    ),
    "stn_the_baron_charges_me_to_land": (
        "Windrider-Keeper Pazzik pays Baron Revilgaz to land in Booty Bay, and he's paid it every week since the "
        "camp arrived. He wants a second roost that isn't Booty Bay, and he's already picked the coast north of the "
        "camp, without having been to see it.",
        "Go up the coast trail past the ford, to the ground north-west of the Green Cut, and tell me if there's "
        "open sky over it. A wyvern wants water on one side and nothing overhead. The vinecrest raptors work that "
        "trail hard, so you'll earn the look. Count how many there are while you're at it. I price a route by what "
        "eats the courier, not by how far it is.",
        "Canopy right down to the waterline? Then no roost, and the Baron keeps his landing fee another year. Your "
        "lot gave me a word for what I run off that tower, you know: timetable. I used to call it a schedule, but a "
        "schedule is what you hope for. A timetable is what you're late against. Best word anybody ever gave me, "
        "and it didn't cost a copper.",
    ),
    "stn_the_long_haul": (
        "Windrider-Keeper Pazzik has learned, at some cost to his dignity, that there's no open sky on the coast "
        "north of Grom'gol. So he's given up on a near roost. His new plan is the longest route on any flight "
        "ledger in the Horde, and he's already pricing it.",
        "No roost within a morning's flight? Fine, then we go in one long hop: over the water and up the whole "
        "coast to Tarren Mill in Hillsbrad. A wyvern that flies that far can't eat on the way, so it needs pressed "
        "feed blocks. Get me boar fat and grain off the rootgrubber boars and thornback apes on the Green Cut, east "
        "of the gate. The apes have been raiding my feed store since the day it existed.",
        "That's enough for one bird to make one crossing, one way. I can reach the Baron's roost twice before noon, "
        "and this one only once, but then I'm sitting in Hillsbrad with a hungry wyvern and a landing fee of "
        "nothing at all. I've been saying that number to myself for a week, and it's still my favourite.",
    ),
    "stn_a_name_at_the_other_end": (
        "A route isn't a route until somebody at the far end agrees to catch it. Pazzik has written his proposal "
        "out on both sides of a card, and he's heard there's an orc on a tower in Hillsbrad who flies wyverns too "
        "and has nobody to fly them to.",
        "Take this to Wind-Rider Ghulrak at Tarren Mill. Read it if you like, it's a timetable and a price, and the "
        "price is what he'll argue about. Fly up on the Baron's route and change at the mill. Yes, that means "
        "you're paying the fee I'm trying to stop paying. Think about that for the whole flight, and you'll "
        "understand my position.",
        "A jungle goblin wants to put a wyvern over open water for most of a day on the strength of a feed block. "
        "Sit down a moment. I'm not saying no. I've flown that coast, and there's a stretch in the middle with nothing below "
        "you but water and nothing above but weather. A bird that tires there doesn't get to tire anywhere else.",
    ),
    "stn_two_roosts_one_ledger": (
        "Wind-Rider Ghulrak knows exactly what the middle of Pazzik's route is: open water with nowhere to land. "
        "He'll endorse it if somebody can cover that middle stretch, and the only ones who fly it at night are the "
        "Forsaken.",
        "There are things you should ask me before you fly anywhere, and I'll answer them, because a courier who "
        "doesn't know the route is just cargo. Then take my endorsement west to Bat Handler Odo at the Sepulcher. "
        "His bats cross that water every night of the year. If he'll let a wyvern land on his tower in bad weather, "
        "the route stands. If not, your goblin keeps paying his Baron.",
        "An orc's endorsement and a goblin's arithmetic, and the orc was honest enough to write down the part he "
        "can't solve. It's there at the bottom of the page in his own hand: the middle. He's flown it. I've hung "
        "upside down in it. Those aren't the same thing, and mine is the one that counts here.",
    ),
    "stn_the_relay_signed": (
        "Bat Handler Odo has read a goblin's route, an orc's endorsement, and a note about weather in a jungle he "
        "will never see. He's signed it, and he's added a line at the bottom in his own hand. That line is the part "
        "that matters.",
        "I'll light the tower. Not for the goblin or the orc, but for the bird, which has no say in any of this and "
        "is the one that'll hit the water. Take this back to Pazzik at Grom'gol, and tell him the line at the "
        "bottom is mine and isn't up for discussion: in bad weather, the wyvern lands on my tower and the mail goes "
        "on by bat. He'll hate it. He'll sign it.",
        "He lit the tower and then put his hand in my pocket. In bad weather the mail goes by bat: his bat, his "
        "route, his cut. He knew exactly what he was doing when he wrote it under his signature instead of above "
        "it. Go on and stamp it. Three years I've paid the Baron to land, and now I'll pay a dead man to keep my bird out of "
        "the sea. It's still cheaper, and I'm going to tell the Baron so to his face.",
    ),
    "stn_nothing_they_have_fought_climbs": (
        "Drillmaster Ukko has a drill ground, a palisade, and a training plan he's rewritten exactly once in his "
        "life, three years ago. He'll tell you why if you ask, and he'd much rather you asked here than worked it "
        "out the hard way on the Green Cut.",
        "Ask me whatever you like. Then go and fight something that climbs. The thornback apes on the Green Cut, "
        "east of the gate, come down hand over hand, and they don't come at your front, they drop on your head. A "
        "recruit who's only ever been hit from the front dies looking at the ground. I want you to have been hit "
        "from above before I put anybody behind you.",
        "You've been watching the canopy since you came back through that gate, and you haven't even noticed. "
        "That's the whole lesson, and the jungle taught it to you in one afternoon. I've been shouting it across "
        "this drill ground for three years and it's never sunk in that fast.",
    ),
    "stn_the_third_direction": (
        "Ukko wants a climbing frame on his drill ground, but every length of rope in Grom'gol has already been "
        "spliced twice. There's plenty of vine in this jungle, though, and the vine is wrapped around something that "
        "doesn't like being shortened.",
        "Bring me coils of strangler vine, cut long and fresh off the wet ground where it's still green and hasn't "
        "gone woody. Clear the coilvine pythons off it first. Up in the canopy a python is exactly the colour of "
        "the vine you're reaching for, and you only make that mistake once.",
        "Down is the ground, forward is the gate, and up is the direction nobody ever drills. Now there's a frame "
        "on my ground to drill it on. The first one over the top was a storesman's clerk with a bad leg, which is "
        "the only part of today I didn't plan. Nobody laughed, and if they had, I'd have had words.",
    ),
    "stn_not_tame_fed": (
        "Beast-Handler Kozza keeps the camp's raptor pens and wyvern lines, and she has one rule she repeats to "
        "everyone: the animals aren't tame, they're fed. Feed ran short the week the supply ship turned away, and "
        "now the panthers have taken an interest in her pens.",
        "Boar haunch, mon, not offal and not slop. A raptor dat gets slop remembers it, and den she bites da hand "
        "dat brought it. Get me good haunches off da rootgrubber boars, off da leg. And da greenpelt panthers have "
        "found my pens. Dey sit in da green by da line and wait for feedin' time same as da birds. Chase dem off "
        "before one works out which end has da gate.",
        "Dey eat, dey settle, and dey let me walk between dem. Dat's all of it. Nobody in dis camp has named one "
        "of dose birds, and nobody's goin' to, because da day you name a ting you start expectin' it to be "
        "grateful. One mornin' it ain't, and you're surprised, and bein' surprised is how a handler loses an arm.",
    ),
    "stn_what_the_pens_know": (
        "Kozza's raptors have gone off their feed on the same day every week since the dry season turned, and "
        "she's stopped believing it's the feed. A penned bird knows what's moving on the road outside better than "
        "the sentry does, and Kozza has been reading hers for three seasons.",
        "Sit up on da rail and ask me. Dis ain't somethin' I can hand you in a sack, and it ain't somethin' I'll "
        "carry to da overseer's table on my own. What I've got is a shape in my head, and a shape in one head is "
        "worth nothin' until someone else has heard it out loud and not laughed.",
        "Dere, now it's said, and now two of us know it. If I fall off dis rail tomorrow, da camp still has it. "
        "Tell da overseer if you like. She'll want a number, and I ain't got one. I got birds, and birds don't "
        "count. Dey just stop eatin'.",
    ),
    "stn_signed_for_twice": (
        "Berth-Master Zekka has a grant from Booty Bay with the Baron's stamp on it and a date written small "
        "underneath. He's read it four times. He wants someone else to carry it across the camp to Overseer Mokra, "
        "because he knows what it means and doesn't want to be holding it when she finds out.",
        "It's a berth in the Baron's own harbour, granted to this camp for our airship, forever, at a price. Read "
        "the price. Then read the little date under the stamp. That's not the day he signed it, it's the day he "
        "decided we'd one day have to come and ask. Take it to the overseer. I've signed for everything that came "
        "off that stair, but I'm not signing for this.",
        "A goblin has granted me, forever, the right to keep paying him for the one thing this camp can't "
        "do without, and he dated the decision to the season we landed. He's been sitting on it for three years, "
        "waiting for me to need it badly enough to ask. Put it on the table, not in the chest. I want to look at it "
        "for a while.",
    ),
    "stn_four_reports_and_a_boot": (
        "Field-Medic Sulaa told the quartermaster to his face that the boots were bad. He wrote it down and nothing "
        "happened, because the only man who can condemn that batch is the one who signed for it. So she's given up "
        "on the boots and started working on the feet instead.",
        "There's a pale tuber in the rot of Rotvine Fen, as far east as the jungle goes before it turns to water. "
        "It pulls the wet out of anything you pack it against. The fenrot creepers and sourwater oozes carry them, "
        "and the bloatspawn toads sit in the standing water, so watch where you step. I can't condemn a boot, but "
        "I can keep a foot dry inside one.",
        "A cloth, a tuber, and a foot stays dry for a day and a half. That's not a cure, it's a delay, and in a "
        "place like this a delay is most of medicine. He's still signing, by the way. Boots, rope, salt, bandages. "
        "Every requisition that comes off that stair has his name at the bottom, and nobody in this camp has ever "
        "asked him to stop.",
    ),
    "stn_in_the_count": (
        "Sentry Vrak once asked you, as a courtesy, not to look at the ground outside the west wall. Now she's done "
        "asking for courtesies. She's asking for the thing she should have put in a report two years ago.",
        "The greenpelt panthers know which day we carry our dead out. Thinning them buys a week, and then it's the "
        "same week again, so kill a few more for me. Then take this to Innkeeper Rukha. She keeps a post with "
        "every name in this camp chalked on it, the only honest list of us there is. I want the ones outside the "
        "wall on it too. You're not on that post, and nobody who is would carry this.",
        "She wants them chalked on the same post as the living, under a line, in the same chalk. She's carried that "
        "for two years and walked past this door every day of it. Well, I've got the chalk and the post, and I'm "
        "not the one who has to explain it to the overseer, so it goes up tonight. You know the part that got me? "
        "She asked if she was allowed to be on both.",
    ),
    "stn_a_mark_for_a_thing_still_being_made": (
        "Mapmaker Ashi invented a chart mark for a ruin that people are still building. That took her an "
        "afternoon. Defending it will take a year, because a mark with only one site under it looks like a "
        "mistake with a symbol on top.",
        "I've got to have two sites, or the survey office will file it as a special case and bury it. So bring me chips off "
        "the new carved stone the Zul'Marosh stonehands and stairwardens are working, the four-faced stuff, not "
        "the old grey. Then go and stand at the Green Cut, where somebody's been stacking our timber into something "
        "with a shape to it. If it has a shape, it's a site, and then I've got two.",
        "That makes two sites, so it's a real mark. I'll send it north and it'll come back corrected, because there's a "
        "clerk in the survey office who's been correcting my sheets for a year and a half and has never been "
        "further south than the Barrens. He learned this jungle off sheets I drew, and now he knows it better than "
        "I do, on paper. I'm going to win this one, even if it takes until the dry season.",
    ),
}

VOICE = {}
VOICE.update(CENTRAL)
VOICE.update(SOUTH)
VOICE.update(NORTH)
