# -*- coding: utf-8 -*-
"""Sheet 5: sixteen companions (claude/recruit_art_prompts_sheet5.md).

Kyle, 18 Nov 2026: "Let's build another 16 recruits. Character sheets and portraits. Keep in mind next zone will be
deadwind pass. And we can have some filler. Also will eventually have moonglade and winterspring." Then "Make 5
characters attractive latino females", "We can put recruits in older zones too! Don't think they ALL have to be end
game", and "ensure they have backstories, and character traits".

The recruit-overhaul voice: whole sentences said out loud, no clipped fragments, no "it's not X, it's Y". Every one of
them came through three years ago, like everyone else. The four liquidators share a camp in Deadwind Pass, and each
one's text talks about the camp, the wheel and the Forsaken, never about another recruit (recruits are strangers to
each other).

TRAITS is the one-line read on who each of them is, for the doc and for whoever writes their banter later.
"""

TRAITS = {
    "taras_witchhunter": "Dry, morbid humour and soft as butter with his dog. A guide to his bones, who counts heads "
                         "without thinking, hates it when someone wanders off and trusts Kashtan's nose over anyone's word.",
    "lucia_suncleric": "Warm, chatty and devout. She's a terrible gossip, but she never repeats anything said in the "
                       "chair, and she can tell how a person's doing from their hair.",
    "wes_warrior": "Slow to speak, impossible to rattle and a stickler for procedure. Underneath, he's soft about his "
                   "daughters and the camp's mule.",
    "mariana_priest": "Calm, precise and kind, with a gallows streak she only shows other medics. She plans everything, "
                      "and she's quietly competitive about it.",
    "neil_felsworn": "Dry, unflappable and pedantic about safety. He makes terrible puns about half-lives, and he takes "
                     "the green fire more seriously than he lets on.",
    "cristobal_knight": "Brave, loud and reckless with himself but never with anyone else. He's a mummy's boy who "
                        "calls everybody 'hermano'.",
    "valentina_starcaller": "Bright, curious and a born teacher. She gets lost in the sky, and she's easily moved, a "
                            "little dreamy and fiercely protective.",
    "faris_shaman": "Gentle, patient and slow to anger. He's a gardener's soul and a good listener who misses home "
                    "with his whole body.",
    "iker_guardian": "Relentlessly upbeat and loud. He's competitive about everything, can't sit still and believes "
                     "anyone can do one more lap.",
    "wade_barbarian": "Laconic, practical and a bit old-fashioned. He respects the animals he hunts, and he likes his "
                      "own company more than he admits.",
    "ximena_primalist": "Stubborn, steady and fearless. She's blunt to the point of rudeness on a mountain and the "
                        "warmest person in the room off it.",
    "hector_witchdoctor": "A showman with a big laugh. He's superstitious, sentimental about his wrestling years and "
                          "much smarter than he plays.",
    "tobias_paladin": "Patient, methodical and quietly devout. He's a perfectionist about joints and mortar and says "
                      "very little, but all of it's true.",
    "camila_venomancer": "Still, watchful and dryly funny. She has nerves of steel, and she's fond of the things "
                         "everyone else is scared of.",
    "sebastian_bloodmage": "Cheerful, sociable and unbothered by gore. He's a born host who'll feed anyone, and the "
                           "Forsaken find him deeply unsettling.",
    "enzo_cultist": "Proud, intense and haunted by coming fourth. He's charming when he wants to be, and he's honest "
                    "with himself about what he traded.",
}

BATCH = {
"taras_witchhunter": dict(
    greeting="Stay on the path, please, and don't touch anything that glows. I've said that to a lot of tourists, "
             "and I've never meant it more.",
    backstory=(
        "Taras took tourists into the Chernobyl Exclusion Zone for nine years. He walked them through Pripyat, past "
        "the school and the swimming pool, and every tour ended under the yellow Ferris wheel that never once "
        "turned. He's dry, morbid and very gentle with animals, and he came through with Kashtan, a Zone stray he'd "
        "been feeding at the checkpoint for years. When the wheel turned up in Deadwind, he was the first to "
        "volunteer, because he's the one person on this world who knows it by heart."),
    before=(
        "A flat in Kyiv with a balcony full of his mother's tomatoes, and a minibus that smelled of instant "
        "coffee.\n\n"
        "He knew every dog at every checkpoint by name, and they all knew his pockets had sausage in them."),
    adjustment=(
        "Kashtan settled in faster than he did. The dog found the first hunting trail in a week, and Taras followed "
        "him onto a witch hunter's road.\n\n"
        "He told himself the wheel was a coincidence for about a day, and then he stopped telling himself that."),
    forward=(
        "He wants to stand under the wheel one more time and work out why it came here and nothing else did.\n\n"
        "Then he'd like to find a quiet village, a lot of dogs and nothing radioactive at all."),
    now=(
        "At the liquidators' camp in Deadwind Pass, checking everyone through the wash troughs at the gate.\n\n"
        "He counts heads when people go out and counts them again when they come back. Kashtan won't set a paw "
        "where the ground's gone bad, and Taras has learned not to either."),
    look=("Ukrainian man, 38, tall and lean, dark-blond hair cut short, light stubble, grey-blue eyes. A long dark grey "
          "witch-hunter coat over leathers, a wide-brimmed hat, a short crossbow and a hunting spear, a brown "
          "shepherd-mix stray at his heel, a yellow and black dosimeter badge on his collar."),
),
"lucia_suncleric": dict(
    greeting="Sit down, sit down, you've got half the Barrens in your hair. I'll fix it while you tell me everything.",
    backstory=(
        "Lúcia ran a salon in Goiânia with two chairs, a radio that only got one station and a queue on Saturdays. "
        "Her grandmother raised her on rosaries and saints' days, and Lúcia still prays the way she was taught, out "
        "loud and with her whole heart. She's warm, chatty and a shameless gossip who never repeats a word said in "
        "her chair. Here the sun answers when she asks, which surprised her a lot less than it surprised the priests."),
    before=(
        "A pink-tiled salon on a busy street, a cat called Dona Flor and a mother who phoned every day at noon.\n\n"
        "Her grandmother lit a candle every Sunday for everybody on their street, by name, and Lúcia kept the list."),
    adjustment=(
        "She came through with her scissors in her apron pocket. The first thing she did on this world was cut a "
        "grunt's hair, and he tipped her a copper.\n\n"
        "She started praying at the Crossroads because she didn't know what else to do, and the light came down on "
        "the second day."),
    forward=(
        "She'd like a proper salon with a door that shuts and a mirror that isn't a bucket of water.\n\n"
        "She also wants to find a church, any church, where someone will sing with her."),
    now=(
        "At the Crossroads, by the inn, with a stool, a bowl of water and a queue of caravan guards.\n\n"
        "She charges a copper and a blessing. Most of them pay the copper and pretend not to want the blessing."),
    look=("Brazilian woman, 33, curvy, long dark-brown curly hair, warm golden-brown skin, large dark eyes. White and "
          "sun-gold cleric robes with a gold sun disc on the chest, a slim golden sceptre, hairdresser's scissors in "
          "a holster on her belt, a silver saint's medal on a chain."),
),
"wes_warrior": dict(
    greeting="Suit check before you go past the fence. I don't care who you are, I check everybody.",
    backstory=(
        "Wes spent twenty years on the Hanford tank farms in Washington, cleaning up waste that'll outlive everybody "
        "who ever made it. He did it in a suit, by the procedure, with a partner, every single day. He's slow to "
        "speak and impossible to rattle, and he's the kind of man who reads the whole manual before he touches "
        "anything. Standing in front of something bad so other people don't have to is the only job he's ever "
        "wanted, so Deadwind suits him fine."),
    before=(
        "A house in Richland with a boat in the driveway that he took out twice a year, and two daughters in "
        "college.\n\n"
        "He coached his younger girl's softball team for six seasons and never once raised his voice."),
    adjustment=(
        "The fighting came easy, because the shield works like the procedure does. You hold it, you don't panic "
        "and you don't step out of line.\n\n"
        "The hard part was never knowing if his girls were all right, and he still doesn't know."),
    forward=(
        "He wants the fallout boxed up, mapped and labelled, the way it should've been done at Hanford.\n\n"
        "After that he'd like a boat again. There's a lake in Mulgore he's had his eye on."),
    now=(
        "At the liquidators' camp in Deadwind Pass, at the quarantine fence, checking suits.\n\n"
        "The camp's mule follows him everywhere. He says he doesn't know why, and he feeds it apples."),
    look=("American man, 46, very big and broad, sandy-brown hair cut short, a short greying beard, blue eyes. Heavy, "
          "scratched dull-steel plate, a big rectangular tower shield and a broad sword, a faded yellow hazmat hood "
          "rolled up through his belt."),
),
"mariana_priest": dict(
    greeting="Come in and sit on the cot. I'll tell you what I'm doing before I do it, so nothing's a surprise.",
    backstory=(
        "Mariana was a radiation therapist at a cancer centre in Monterrey. She spent her days lining up beams to "
        "the millimetre, so the radiation hit the tumour and nothing else. She's calm, precise and kind, with a "
        "gallows humour she only lets other medics see. She heals with the Light now, and she aims it the same way. "
        "When the liquidators asked for someone who wasn't afraid of the word radiation, she packed that night."),
    before=(
        "Ten years on the same treatment floor, a running club that met at five in the morning and a brother who "
        "ran a taco stand by the stadium.\n\n"
        "She remembered every patient's birthday and rang a little bell for them on their last day of treatment."),
    adjustment=(
        "She found the Light the way she'd found the right dose, carefully and with a lot of notes.\n\n"
        "The priests in Orgrimmar said she prayed like an accountant. She took it as a compliment."),
    forward=(
        "She wants to keep a log of everything the fallout does to a body, so whoever comes next has something to "
        "work from.\n\n"
        "She'd also like to run again one day, somewhere that doesn't glow."),
    now=(
        "In the infirmary at the liquidators' camp in Deadwind Pass, with a lamp and a stack of notebooks.\n\n"
        "The Forsaken apothecaries bring her their worst cases, and they've stopped arguing with her charts."),
    look=("Mexican woman, 31, slim, glossy black hair in a high ponytail, light olive-tan skin, warm dark-brown eyes. "
          "White and pale gold priest robes with a long open overcoat, a short staff with a glowing white crystal, a "
          "hospital ID badge on a teal lanyard."),
),
"neil_felsworn": dict(
    greeting="Hard hat's optional, but I'd stand behind me if I were you. The green bit doesn't care whose side "
             "you're on.",
    backstory=(
        "Neil spent twenty years decommissioning the old buildings at Sellafield, on the Cumbrian coast, taking "
        "apart things that were never meant to be taken apart. He's dry, unflappable and pedantic about safety, and "
        "he makes truly awful jokes about half-lives. Fel fire came to him like a bad habit, and he treats it like "
        "everything else that's dangerous, with a lot of respect and a written plan. He's the calmest man in "
        "Deadwind, and he'd like everyone else to calm down as well."),
    before=(
        "A terraced house in Whitehaven, a season ticket for the rugby league and a wife who did the crossword in "
        "pen.\n\n"
        "He walked the fells every Sunday and kept a list of every summit he'd done, in order."),
    adjustment=(
        "The first time fel fire came out of his hands he put it out, filled in a report and then tried again.\n\n"
        "The warlocks found him maddening, because he wanted to know the dose of everything."),
    forward=(
        "He'd like to know what the fallout's made of, because nobody has asked the right questions yet.\n\n"
        "He'd also like a proper cup of tea, and he's given up on that one."),
    now=(
        "At the liquidators' camp in Deadwind Pass, at the sample racks, labelling jars.\n\n"
        "He's put up a sign by the pyre that says how long to stand near it. Nobody reads it, and he updates it "
        "anyway."),
    look=("English man, 44, tall and fit, grey hair with some dark left in it, a neat short beard, green eyes. Black "
          "and iron felsworn robes over light plate with green fel runes, a staff with a caged green flame, a white "
          "hard hat with a reflective stripe hanging from his belt."),
),
"cristobal_knight": dict(
    greeting="Hermano, you smell like smoke, which is good. It means you've been somewhere interesting.",
    backstory=(
        "Cristóbal was a wildfire brigadista in Valparaíso, and in 2024 he spent four days on the hills above his "
        "mother's house while the city burned. The house was still standing when he came down. He's brave, loud and "
        "reckless with himself but never with anybody else, and he calls everyone hermano within a minute of "
        "meeting them. Hellfire found him, which he says is a joke at his expense, and he's decided to laugh at it."),
    before=(
        "A brigade station in the hills, a motorbike that broke down every week and a mother who sent him off with "
        "empanadas.\n\n"
        "He danced cueca at every fiesta and was very bad at it, which he says is the point."),
    adjustment=(
        "He walked out of a grass fire on his first day, and he was the only one who walked out of it.\n\n"
        "The fire inside him scared him for a month, and then he started using it to light other people's camps."),
    forward=(
        "He wants every town in the Barrens to have a fire brigade, and he's started training the first one.\n\n"
        "He'd also like his mother to know he's alive. He writes her a letter every week and keeps them all."),
    now=(
        "At Camp Taurajo, drilling a dozen young tauren on how to cut a firebreak.\n\n"
        "When the grass goes up in the dry season, he's the one Taurajo sends for."),
    look=("Chilean man, 35, athletic and broad-shouldered, thick black hair pushed back, a short dark beard, warm "
          "brown skin, dark eyes, soot on his face. Dark crimson and black knightly plate with orange hellfire in the "
          "seams, a two-handed flamberge, a yellow brigadista's helmet clipped to his belt."),
),
"valentina_starcaller": dict(
    greeting="Look up at it, really look. I've never seen anything like the sky over this lake, and I've seen a "
             "lot of sky.",
    backstory=(
        "Valentina took tourists out into the Atacama desert at night to look at the stars, in Spanish, English and "
        "Portuguese. She always found the Southern Cross first and always cried a little when someone saw the Milky "
        "Way for the first time. She's bright, curious and a born teacher who gets lost in the sky. Here the stars "
        "answer her, and the druids of Moonglade have been teaching her what they mean."),
    before=(
        "A hostel in San Pedro de Atacama with a telescope on the roof and four dogs that belonged to nobody.\n\n"
        "She was studying for an astronomy degree by correspondence, and she was two courses short."),
    adjustment=(
        "The first night she looked up, she didn't recognise a single star. She sat down and cried, and then she "
        "started drawing new charts.\n\n"
        "By the end of the month the stars were answering her, and she's been fighting by their light since."),
    forward=(
        "She wants to finish her chart of this world's sky, all of it, and name the constellations properly.\n\n"
        "She also wants to know if Earth's sun is up there somewhere, and she's afraid of the answer."),
    now=(
        "In Moonglade, out by the lake, where she can see the most sky.\n\n"
        "She carries a little red torch so she doesn't ruin her night eyes, and she makes visitors use it too."),
    look=("Chilean woman, 28, athletic and slim, long straight black hair over one shoulder, warm tan skin, dark almond "
          "eyes. Silver and night-blue warden armour, a long glaive with a crescent blade edged in starlight, a small "
          "red-lens torch on a cord round her neck."),
),
"faris_shaman": dict(
    greeting="Peace be with you. Sit by the water for a while, it's good water. I can tell.",
    backstory=(
        "Faris grew dates on his family's land along the Shatt al-Arab outside Basra, where the Tigris and the "
        "Euphrates meet. His grandfather taught him that you look after the water first and the palms look after "
        "themselves. He's gentle, patient and a very good listener, and he misses home with his whole body. The "
        "water spirits here took to him at once, and Moonglade's lake is the first water since home that he trusts."),
    before=(
        "Ninety palms, a house with a courtyard and a fig tree, and a big family that ate together every Friday.\n\n"
        "He took his nephews out on the river in a flat boat and taught them the names of every bird."),
    adjustment=(
        "He came through into dry country, and for weeks he couldn't sleep without the sound of water.\n\n"
        "A shaman found him at a spring talking to it, and told him the spring was talking back."),
    forward=(
        "He wants to plant something here that'll still be standing in a hundred years.\n\n"
        "He's been trying to grow a date palm from the stone of the last date he had in his pocket."),
    now=(
        "In Moonglade, by the lake, looking after the water and the people who come to it.\n\n"
        "He keeps his grandfather's prayer beads round his wrist, and he turns them when he's thinking."),
    look=("Iraqi man, 36, medium build and very fit, short black wavy hair, a close-trimmed beard, warm brown skin, dark "
          "eyes. River-blue and palm-green shaman mail and leathers, a wooden totem staff carved with fish and reeds, "
          "amber prayer beads round his wrist."),
),
"iker_guardian": dict(
    greeting="Up, up, up! You can rest when you're dead, and you don't look dead to me.",
    backstory=(
        "Iker taught PE and coached pelota in a Basque village, at a school with a fronton wall that was older than "
        "the church. He's never met anyone he couldn't shout into running one more lap, and he's never been tired "
        "in his life. He's loud, upbeat and competitive about absolutely everything. Here the shouting turned into "
        "something real, and when Iker tells a fighter they can keep going, they really can."),
    before=(
        "A school of ninety kids, a fronton wall, a mother who made the best cheesecake in the province and an old "
        "bicycle he rode everywhere.\n\n"
        "His team won the regional schools final twice, and he still talks about the second time."),
    adjustment=(
        "He landed in Arathi in the rain and started a running club for the farmhands within a week.\n\n"
        "The first time his voice actually healed someone, he didn't notice. He just thought they'd been lazy "
        "before."),
    forward=(
        "He wants to build a fronton wall in Arathi and teach somebody here how to play properly.\n\n"
        "He'd like a rematch against Earth's best team one day, and he knows he won't get it."),
    now=(
        "In Arathi West, with a whistle round his neck and a line of tired farmhands behind him.\n\n"
        "They complain about him all day, and they've never been fitter in their lives."),
    look=("Basque man, 33, strong and compact, dark brown hair short at the sides, clean-shaven, a strong nose and jaw, "
          "brown eyes. Bright steel guardian half-plate over a red and white padded coat, a round shield and a short "
          "sword, a coach's silver whistle on a red cord."),
),
"wade_barbarian": dict(
    greeting="Wind's from the north tonight. If you're heading out, wear more than that.",
    backstory=(
        "Wade guided big-game hunters out of Whitehorse for thirty winters, up into the Yukon after moose, sheep "
        "and the odd grizzly. He's laconic, practical and a bit old-fashioned, and he respects every animal he's "
        "ever taken. He keeps a trophy from each hunt, carved from bone, and he can tell you the story of every one. "
        "Winterspring feels like home with yetis, and the barbarians here understood him at once."),
    before=(
        "A log cabin on the edge of town, a truck with three hundred thousand miles on it and a sister in Dawson "
        "City who wrote him actual letters.\n\n"
        "He spent his summers mending gear and his winters out on the land, and he liked it that way."),
    adjustment=(
        "He came through on a hunt, so he had his rifle and a pack. The rifle ran out of bullets in a month, and "
        "the axe never runs out of anything.\n\n"
        "A clan took him on after he dressed a beast faster than any of them, and he's been carving their bone "
        "since."),
    forward=(
        "He wants to take the biggest thing in Winterspring, cleanly, and carve it well.\n\n"
        "He'd also like a cabin up here with a good stove, and nobody knocking at the door."),
    now=(
        "In Winterspring, out on the snow, where the hunting's best and the company's quiet.\n\n"
        "His Yukon hunting licence is still tied to his belt. He says it's because he's honest."),
    look=("Canadian man, 40, big and rangy, long sandy-brown hair under a fur hat, a thick short beard, light blue "
          "eyes. Heavy furs and hides over mail, a two-handed axe on his shoulder, a necklace of carved bone and claw "
          "trophies, an orange laminated hunting licence tied to his belt."),
),
"ximena_primalist": dict(
    greeting="If you want to go up, you go up with me, roped in, and you do what I tell you. Then we'll be friends.",
    backstory=(
        "Ximena guided climbers in the Cordillera Blanca out of Huaraz, and she summited Huascarán eleven times. "
        "She's stubborn, fearless and steady, and she's blunt to the point of rudeness on a mountain, because "
        "politeness gets people killed up there. Off the mountain she's the warmest person in the room. The stone "
        "listens to her here, and she stands in front of people the way a mountain does."),
    before=(
        "A guiding company she ran with her cousin, a little house with a view of the peaks and a big Sunday lunch "
        "at her grandmother's.\n\n"
        "She'd led two rescues on Huascarán and never talked about either of them."),
    adjustment=(
        "She came through on a glacier, which was the one piece of luck she's had here.\n\n"
        "She dug a snow hole, waited out the storm, and walked down into a world she didn't know with her rope "
        "still on her shoulder."),
    forward=(
        "She wants to climb the highest peak in Winterspring, first, and name the route.\n\n"
        "She also wants to teach people here to climb properly, roped and careful, so they stop falling off things."),
    now=(
        "In Winterspring, at the foot of the high peaks, mending her rope and watching the weather.\n\n"
        "The red carabiner on her belt is the one she's clipped to on every summit. She doesn't lend it to anyone."),
    look=("Peruvian woman, 32, strong and athletic, long thick black hair in two braids, warm brown skin with "
          "sun-flushed cheeks, dark eyes. Heavy primalist plate studded with granite and ice crystal, a big "
          "stone-headed hammer, a stone shield, a red carabiner and a coil of rope on her belt."),
),
"hector_witchdoctor": dict(
    greeting="Ah, a fan! Don't be shy. Everybody wants a picture with El Relámpago de Plata, even here.",
    backstory=(
        "Héctor wrestled lucha libre in Mexico City for fifteen years as El Relámpago de Plata, the Silver Lightning, and "
        "nobody outside his family ever saw his face. He's a showman with a huge laugh, superstitious about "
        "everything and much smarter than he lets anyone see. The trolls of Stranglethorn told him a mask is a "
        "spirit's face, and he said he'd known that his whole life. Now the spirits wear his, and the crowds at the "
        "arena love him."),
    before=(
        "Arena México on Friday nights, a gym in Tepito, a wife who sewed every mask he ever wore and two boys who "
        "wanted to be luchadores.\n\n"
        "He retired a year before the Integration with a bad knee and a lot of good stories."),
    adjustment=(
        "He came through with his mask in his bag, and the first troll who saw it bowed to him.\n\n"
        "A witch doctor in Grom'gol took him in, and he learned shadow and spirit the way he'd learned to fall, by "
        "doing it a thousand times."),
    forward=(
        "He wants to put on a real show in the arena, with rules, a ring and a crowd that cheers.\n\n"
        "He'd like to give his mask to his boys one day. He's afraid that he never will."),
    now=(
        "At the arena in Stranglethorn, signing autographs for goblins who can't read and posing for trolls.\n\n"
        "He never takes the mask off his belt. He says a luchador who loses his mask loses his name, and he isn't taking chances."),
    look=("Mexican man, 37, broad and powerful, short black hair and a sharp beard line, warm brown skin, dark eyes. "
          "Dark violet and bone witch-doctor robes with feathers and charms, a gnarled staff topped with a carved "
          "mask, a black luchador mask with silver flame trim on his belt."),
),
"tobias_paladin": dict(
    greeting="Mind the scaffold. That wall's coming along, but I'd rather you didn't lean on it yet.",
    backstory=(
        "Tobias worked on the Cologne Cathedral works crew, the team that's been repairing the cathedral for "
        "seven hundred years and will never finish. He replaced stones carved by men who died in the middle ages, "
        "and he loved it. He's patient, methodical and quietly devout, and he says very little, but all of it's "
        "true. The Light came to him the way good mortar sets, slowly, and it holds."),
    before=(
        "A flat in the Südstadt, a crew of twelve who ate lunch together on the roof and a choir he sang bass "
        "in.\n\n"
        "He carved a little face into every stone he ever replaced, somewhere nobody would ever look."),
    adjustment=(
        "He came through into the Plaguelands, which was very bad luck. The Argent Dawn took him in because he "
        "could fix a wall, and he's been fixing their walls since.\n\n"
        "He found the Light on a scaffold, and he still prays best with a trowel in his hand."),
    forward=(
        "He wants Light's Hope to stand for a thousand years, and he'd like to be the one who made it.\n\n"
        "He'd also like to sing in a choir again. He's started one, and it has three people in it."),
    now=(
        "At Light's Hope Chapel, on the scaffold by the chapel wall, repointing mortar.\n\n"
        "There's a little carved face on one of the new stones already. He won't say which one."),
    look=("German man, 39, tall and broad, short light-brown hair, a neat short beard, grey-blue eyes. Polished silver "
          "paladin plate with a white tabard and a golden sun, a large kite shield and a mace, a stonemason's leather "
          "apron rolled at his waist with a chisel and mallet."),
),
"camila_venomancer": dict(
    greeting="Stand still, please. There's a scorpid under your boot, and it's having a worse day than you.",
    backstory=(
        "Camila worked in a lab in Durango, where the scorpions come into houses every summer, milking them for the "
        "venom that makes antivenom. She's done it ten thousand times, with tweezers and a steady hand. She's "
        "still, watchful and dryly funny, with nerves of steel, and she's fond of the things everyone else is scared "
        "of. Tanaris is full of scorpids, and she thinks it's the best place she's ever been."),
    before=(
        "A lab with a thousand scorpions in jars, a flat over a bakery and a little sister who called her every "
        "night to complain about boys.\n\n"
        "She saved a boy's life once, in the hospital next door, with antivenom she'd made that week."),
    adjustment=(
        "The first time a venomancer showed her what poison could do, she asked for the dose, the timing and the "
        "antidote, in that order.\n\n"
        "She's very good at waiting for something to move, and here that's most of the job."),
    forward=(
        "She wants to make an antivenom for every sting in Tanaris, and she's already got six.\n\n"
        "She'd also like to find out what her sister's doing now. She hopes it's something with boys."),
    now=(
        "In Northern Tanaris, sitting very still on a rock, watching the sand.\n\n"
        "There's always a scorpid on her shoulder. It's never the same one, and it never stings her."),
    look=("Mexican woman, 29, slim and lithe, long wavy dark-brown hair tied back, golden-tan skin, sharp dark eyes. "
          "Close-fitting dark green and black stalker leathers with a short hooded mantle, two curved daggers "
          "dripping green venom, an amber scorpion on her shoulder, lab safety glasses pushed up into her hair."),
),
"sebastian_bloodmage": dict(
    greeting="You look hungry, my friend. I've got something on the coals, and I promise it isn't anyone you know.",
    backstory=(
        "Sebastián ran the grill at a steakhouse in Palermo, in Buenos Aires, for twelve years. He knows meat, "
        "blood and fire better than anyone, and he's cheerful about all three. He's sociable, a born host and "
        "completely unbothered by gore, and he'll feed anybody who sits down. He came through in Tirisfal, among "
        "the Forsaken, and they find his blood magic deeply unsettling, mostly because he's so happy about it."),
    before=(
        "A parrilla with forty tables, a football club he'd die for and a grandmother who ran the kitchen before "
        "him.\n\n"
        "Every Sunday he cooked asado for his whole family, twenty people, and he never once sat down."),
    adjustment=(
        "The Forsaken don't eat much, which was the hardest thing he's ever had to accept.\n\n"
        "Blood magic came easy, because he's been reading blood on a grill his whole life. He knows when it's "
        "ready."),
    forward=(
        "He wants to open a grill in Brill that the living and the dead will both come to.\n\n"
        "He's working on a recipe the Forsaken can actually taste, and he thinks he's close."),
    now=(
        "In Western Tirisfal, by a fire pit he dug himself, with a grill and a very worried farmer.\n\n"
        "He waves at every passing Forsaken, and some of them have started waving back."),
    look=("Argentine man, 34, lean and tall, dark brown hair swept back, a short neat beard, light olive skin, brown "
          "eyes. Deep crimson and black bloodmage robes with a leather apron over them, a slim rod with a blood-red "
          "crystal, a big carving knife in a sheath with a white cloth round the handle."),
),
"enzo_cultist": dict(
    greeting="You're watching my feet. Good, that's where everybody should look. Most people look at the blade.",
    backstory=(
        "Enzo fenced sabre for Naples from the age of eight and came fourth at the Olympic trials, twice. Fourth "
        "is the worst place there is. He's proud, intense and charming when he wants to be, and he's honest with "
        "himself about what he traded. The Scarlets wanted his blade and he turned them down, because he'd seen "
        "what they do. A darker god offered more, and now he's the best swordsman he's ever met, and he's still "
        "deciding if it was worth it."),
    before=(
        "A salle in the Spanish Quarter, a mother who came to every bout and shouted at the referees, and a scooter "
        "that was always parked illegally.\n\n"
        "He coached the little ones on Saturdays, and he was kinder to them than he ever was to himself."),
    adjustment=(
        "He came through with his fencing glove in his kit bag and nothing else. The Scarlets found him first, and "
        "then he found out what they were.\n\n"
        "The voice that offered him more didn't lie to him about the price, and he respects it for that."),
    forward=(
        "He wants to beat the best blade on this world, fairly, in front of witnesses.\n\n"
        "Then he'd like to know if he could've done it without the voice. He's afraid he already knows."),
    now=(
        "On the Scarlet Monastery Grounds, outside the walls, watching the Scarlets drill and finding the holes in "
        "it.\n\n"
        "His white fencing glove is tucked in his belt. He doesn't wear it anymore, and he won't throw it away."),
    look=("Italian man, 34, slim and athletic, short black curly hair, clean-shaven with a sharp jaw, dark eyes. Black "
          "and dark violet cultist battle-robes over close mail, a long single-edged curved blade with purple shadow "
          "along it, a white fencing glove tucked into his belt."),
),
}
