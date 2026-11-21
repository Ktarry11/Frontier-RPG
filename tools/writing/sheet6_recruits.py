# -*- coding: utf-8 -*-
"""Sheet 6: sixteen companions (claude/recruit_art_prompts_sheet6.md), twelve of them written here.

Kyle, 20 Nov 2026: "Let's make a batch of 16 recruits... 75% men and 25% women. Good looking", "Since some of these
recruits will be in the 1-24 sky zone too", and "We need to ensure a Healer recruit in the start of the zone too". The
roster filled the gap at 45 to 52 (no tank at all, one melee and two healers): five go up the World Tree, three to the
Sunward Crown and Lenswatch, four to the Celestial Expanse and Aurelion. The four for the Aetherian start zone (Ines,
Lukas, Rafael and Samir) wait for it, and their text is written when its maps are (the start zone is parked).

The recruit-overhaul voice: whole sentences said out loud, no clipped fragments, no "it's not X, it's Y". Every one of
them came through three years ago, like everyone else. The five on the tree came through on the ground and climbed it;
the seven in the sky woke on the sky islands and were found by the Aetherians, who keep the Earthborn as guests (the
twenty questions, docs/worldtree_brief.md). Recruits are strangers to each other, so nobody's text names another.

TRAITS is the one-line read on who each of them is, for the doc and for whoever writes their banter later.
"""

TRAITS = {
    "alvaro_venomancer": "Unhurried, warm and impossible to frighten. He tells long stories about his bees and stands "
                         "very still when everyone else is running.",
    "clara_primalist": "Precise, curious and stubborn about evidence. She talks too fast when she's excited, apologises "
                       "for it and keeps talking.",
    "raul_barbarian": "Cocky, loud and generous. He takes stupid risks with a grin and never once with somebody "
                       "else's neck.",
    "federico_templar": "Formal, patient and utterly reliable. He reads everything twice, keeps every word he gives "
                        "and has a dry wit that sneaks up on people.",
    "connor_shaman": "Cheerful, weatherproof and steady in a crisis. He sings badly in two languages and treats every "
                     "storm like an old friend.",
    "mauricio_reaper": "Warm, unflappable and quietly funny. He's at ease with death, gentle with grief and an "
                       "incorrigible host.",
    "etienne_mage": "Easygoing, friendly and a perfectionist about exactly one thing. He's patient with beginners and "
                    "hopeless at staying angry.",
    "oliver_suncleric": "Kind, careful and a little shy. He notices everything about people and says only the gentle "
                        "half of it.",
    "facundo_chronomancer": "Endlessly patient, gentle and precise. He listens more than he talks, and he never rushes.",
    "renata_rogue": "Fearless, quick and funny, with a professional's respect for safety. She checks everyone's "
                     "straps and then jumps first.",
    "tariq_bloodmage": "Gentle, patient and enormously strong. He's softly spoken, slow to anger and generous to a "
                       "fault.",
    "isabela_mage": "Bright, warm and enchanted by everything. She talks with her hands, touches things she shouldn't "
                    "and is very hard to discourage.",
}

BATCH = {
"alvaro_venomancer": dict(
    greeting="Stand still if something lands on you, that's the whole trick. Nothing on this island has stung me yet, "
             "and I've given it every chance.",
    backstory=(
        "Álvaro kept bees in the hills above Cartagena for twenty years, eighty hives on his uncle's land and honey "
        "sold off the back of a pickup on the coast road. He's been stung more times than he can count, and he's "
        "never once panicked about it. He came through on the ground like everyone else and climbed the tree with "
        "the first troll crews. On Rootwater Isle the swarms and the spiders leave him alone, and the venomancers "
        "took one look at that and taught him the rest."),
    before=(
        "Eighty hives on a green hillside, a pickup with no second gear and a wife who sold the honey better than he "
        "ever did.\n\n"
        "He talked to the bees every morning, because his grandfather told him they leave if you don't tell them "
        "the news."),
    adjustment=(
        "The first wasp he met on this world was the size of his hand. It landed on his arm, walked around for a "
        "while and flew off, and the troll who saw it didn't speak to him for a day.\n\n"
        "The venomancers say the poison likes him. He says he's just calm, and he thinks that's the same thing."),
    forward=(
        "He wants to find a hive on this world that makes real honey, and keep it.\n\n"
        "He'd also like to get word home somehow, the way he gave the bees their news every morning."),
    now=(
        "On Rootwater Isle, out where the swarms are thickest, wading through the reeds as if they were nothing.\n\n"
        "The climbers call him the beekeeper and send for him when something with a stinger blocks the path. He "
        "always goes, and he always walks back."),
    look=("Colombian man, 38, broad and strong, short black hair and beard, warm brown skin, dark eyes. Heavy dark "
          "green and gold beetle-shell armour, a thick wooden staff with a carved beetle head, a beekeeper's "
          "wide-brimmed hat with a mesh veil hanging down his back."),
),
"clara_primalist": dict(
    greeting="This tree has no rings. I've cored it in six places and there isn't a single ring anywhere. Sorry, "
             "hello, I'm Clara.",
    backstory=(
        "Clara read tree rings at the university in Freiburg. Give her a core the width of a pencil and she'll tell "
        "you every dry summer, every fire and every bad winter the tree lived through, four hundred years back. She "
        "came through on the ground and climbed the World Tree on purpose, because it's the biggest tree anyone has "
        "ever seen. It has no rings at all, and it's driving her mad. The grovekeepers say the tree heals people "
        "when it likes them, and it seems to like her."),
    before=(
        "A tiny lab under the forestry building, a wall of cores in labelled straws and a bicycle she rode up into "
        "the Black Forest every weekend.\n\n"
        "She once dated a beam in a farmhouse to a winter three hundred years gone, and the farmer cried."),
    adjustment=(
        "She brought her increment borer through in her bag, which is the only reason anyone at Mossroof believes "
        "she was a scientist.\n\n"
        "The first time she put her hand on the bark to steady herself, the bark warmed under it, and a scratch on "
        "her wrist closed."),
    forward=(
        "She wants to know how old the tree is, and she wants to know it properly, with evidence.\n\n"
        "After that she'd like to tell her old department, just to see their faces."),
    now=(
        "At Mossroof on the Lower Boughs, sitting on the moss with her notebook open and her borer in her lap.\n\n"
        "She patches up climbers between measurements, and she asks every one of them how high they've been."),
    look=("German woman, 30, tall and slender, a honey-blonde braid over one shoulder, fair freckled skin, green eyes. "
          "Moss and woven-wood armour over soft leather, a living branch staff with fresh leaves, a slim metal "
          "tree-core drill in a sleeve on her hip."),
),
"raul_barbarian": dict(
    greeting="Eight seconds is a long time on a bull, friend. Up here, I've learned it's a long time on a raptor too.",
    backstory=(
        "Raúl rode bulls on the rodeo circuit out of Tucson for fifteen years, and he's got a silver buckle for "
        "every one he won and a scar for every one he didn't. He's loud, cocky and better company than he lets on, "
        "and he's never met a horse he couldn't talk round. He came through on the ground and climbed the tree "
        "because someone told him the trolls up there respect a man who keeps his trophies. They do, and the "
        "headhunters of the Great Settlement adopted him in a week."),
    before=(
        "A trailer outside Tucson, a pickup with a hitch, a saddle worth more than the trailer and a mother who "
        "never once watched him ride.\n\n"
        "She kept every buckle on a shelf in her kitchen anyway, polished, with the dates written underneath."),
    adjustment=(
        "He came through wearing his biggest buckle, the national one, and the first troll who saw it tried to buy "
        "it off him.\n\n"
        "He rode a raptor on a dare in his first month and stayed on for nine seconds, and the headhunters still "
        "talk about it."),
    forward=(
        "He wants to ride a wild wyvern off the Upper Boughs and stay on.\n\n"
        "After that he'd like to win something on this world that's worth putting on a shelf."),
    now=(
        "In the Great Settlement, in the middle of the market, polishing his buckle and arguing about technique "
        "with any headhunter who'll stop.\n\n"
        "The headhunters have hung his old rodeo number among their trophies, and he pretends he isn't proud of it."),
    look=("Mexican-American man, 36, broad-shouldered and lean, a short dark beard, warm tan skin, brown eyes, a "
          "battered tan brim hat. Barbarian furs and leathers with bone beads, two short war axes, trophy charms at "
          "his belt, a big polished silver rodeo buckle."),
),
"federico_templar": dict(
    greeting="I've witnessed ten thousand promises, and I've learned to listen for the ones people mean. Tell me what "
             "you need, and I'll tell you whether I can promise it.",
    backstory=(
        "Federico was a notary in Montevideo for nineteen years, in an office on Calle Sarandí with a brass seal, a "
        "fountain pen and a queue of people signing the biggest papers of their lives. He believes a promise is a "
        "contract and a contract is sacred, and he's never once broken his word. He came through on the ground and "
        "climbed the tree with a party that needed someone to hold the line, and he's held it ever since. The "
        "templars of Heartwatch watched the way he swears an oath and gave him a shield."),
    before=(
        "An office with green shutters, a wife who taught piano in the next room and a grandson who played with the "
        "seal on Saturdays.\n\n"
        "He read every contract aloud before anyone signed, all of it, because people deserve to know what they're "
        "promising."),
    adjustment=(
        "He came through with his notary's seal in his pocket. He still stamps the oaths the climbers swear at "
        "Heartwatch, and nobody's told him it doesn't count here.\n\n"
        "The first time he promised to keep a stranger alive, the light came up through his arm, and he kept that "
        "promise."),
    forward=(
        "He'd like to write the tree's first proper contract between the trolls and the climbers, and have both "
        "sides read it aloud.\n\n"
        "He also keeps a list of the promises he made at home and couldn't keep, and he means to work through it."),
    now=(
        "At Heartwatch on the Middle Boughs, standing at the gate with his shield and his seal.\n\n"
        "Every climber who leaves the camp promises to come back. He writes their names in a ledger and crosses "
        "them off when they do."),
    look=("Uruguayan man, 42, tall and solid, dark hair greying at the temples, a trimmed grey-flecked beard, light "
          "olive skin, brown eyes. White and bronze templar plate engraved with oath-script, a tall rectangular "
          "shield and a flanged mace, a brass notary's seal on a chain at his belt."),
),
"connor_shaman": dict(
    greeting="That's a fine breeze up here. Back home we'd have called that a calm day and gone out for the pots.",
    backstory=(
        "Connor fished lobster off Inis Mór from the age of fourteen, in a boat his father built and a jumper his "
        "mother knitted, through every storm the Atlantic sent. He speaks Irish to the wind and English to people, "
        "and he's not sure which one listens better. He came through on the ground and climbed the tree to the top, "
        "because the higher he goes the more the weather feels like home. At Highrest the storm answers him, and "
        "the shamans say they've never seen anyone so happy about lightning."),
    before=(
        "A stone cottage at the end of a lane, a half-decked boat, a dog called Bran and a pub with a fiddle on "
        "Fridays.\n\n"
        "His father taught him to read the sky before he could read a book, and weather has never caught him out."),
    adjustment=(
        "He came through in his oilskins, which was lucky, because it was raining.\n\n"
        "The first storm on the Upper Boughs knocked three climbers flat, and Connor stood in the middle of it "
        "laughing, with sparks running down his arms."),
    forward=(
        "He wants to sail something on this world, a skiff or a cloud or anything at all, out into weather nobody "
        "else will go into.\n\n"
        "He'd also like a pint, and he's told the trolls exactly how to brew one."),
    now=(
        "At Highrest on the Upper Boughs, out on the windward edge where nobody else will stand.\n\n"
        "He watches the storms come across from the Stormsplit and tells the camp which ones to worry about, and "
        "he hasn't been wrong yet."),
    look=("Irish man, 35, broad and strong, windswept red-brown hair and a short beard, fair weathered skin, "
          "blue-grey eyes. Shaman mail over a thick cream knitted jumper, two fist-axes with sparks on the blades, a "
          "yellow oilskin fisherman's hat tied to his belt."),
),
"mauricio_reaper": dict(
    greeting="When I woke up on a cloud, I assumed I was dead and was very pleased with the arrangements. Then a man "
             "with crystal on his face asked me to fill in a form.",
    backstory=(
        "Mauricio ran his family's funeral home in Guadalajara for twenty-two years, and every Day of the Dead he "
        "built the biggest altar in the barrio, with marigolds from the door to the street. He's gentle with the "
        "grieving and funny with everyone else, and death has never frightened him. He woke on a cloud above the "
        "World Tree, decided he'd died, and took it very well. The survey found him and kept him as a guest, and "
        "it turns out the dead still listen to him."),
    before=(
        "A funeral home with blue tiles, a hearse he washed every morning, a wife who sang at the services and three "
        "daughters who wouldn't touch the business.\n\n"
        "Every November he walked the whole barrio with a cart of marigolds and gave them away."),
    adjustment=(
        "The Aetherians wrote him down as a ward and asked him a great many questions about funerals. He answered "
        "every one of them at length, with diagrams.\n\n"
        "The first time something died near him on the cloud, he felt it go. He asked it politely to stay a while, "
        "and it did."),
    forward=(
        "He wants to build an altar on this world, a proper one, for everyone who came through and everyone they "
        "left behind.\n\n"
        "He'd like marigolds for it, and he's asked the survey's gardeners to find him something orange."),
    now=(
        "At the Annex on the Sunward Crown, with the survey's other guests from Earth, keeping the peace between "
        "them.\n\n"
        "He's the one the Earthborn go to when somebody's grieving, and the one the Aetherians go to when they want "
        "to know why."),
    look=("Mexican man, 41, tall and broad, slicked-back black hair, a neat moustache and short beard, warm brown "
          "skin, dark eyes. Heavy black and bone-white reaper armour with silver skulls, a long scythe, an orange "
          "marigold pinned at his collar."),
),
"etienne_mage": dict(
    greeting="Back home I made ice for a living, and I was very good at it. Up here, it turns out, I still am.",
    backstory=(
        "Étienne drove the Zamboni at a hockey rink in Montréal's east end for ten years, and the players said his "
        "ice was like glass. He played in a beer league on Tuesdays, coached a peewee team on Saturdays and never "
        "missed a Canadiens game. He woke on a sky island in a snowdrift, which felt like home until he looked over "
        "the edge. The survey brought him to the Annex, and the cold has come when he calls it ever since."),
    before=(
        "A walk-up in Hochelaga, a rink that smelled of cold and popcorn, a toque his grandmother knitted and a "
        "peewee team that never won a single game.\n\n"
        "He flooded the ice at six every morning, slow and even, and he loved the quiet before anyone came in."),
    adjustment=(
        "The Aetherians thought he was a weather-mage the first time he frosted a cup of water without trying. He "
        "told them he was a Zamboni driver, and it took an hour to explain.\n\n"
        "He practised on a pond by the Annex until he could freeze it flat and clear enough to see the fish."),
    forward=(
        "He wants to make a rink on this world and teach somebody to skate, a troll or an Aetherian or anyone who'll "
        "try.\n\n"
        "Then he'd like to find out whether the peewees ever won a game without him."),
    now=(
        "At the Annex on the Sunward Crown, keeping the survey's water cold and the Earthborn's spirits up.\n\n"
        "He's flooded a corner of the cloud into a little rink, and on quiet evenings the guests go round it in "
        "their boots."),
    look=("French-Canadian man, 32, athletic, dark-blond hair short with a little length on top, light stubble, fair "
          "skin, blue eyes. Ice-blue and white frost-mage robes with a fur collar, a staff topped with a clear ice "
          "crystal, a red and white knitted toque."),
),
"oliver_suncleric": dict(
    greeting="Follow my finger, please. Sorry, it's a habit. The survey has me looking at everyone's eyes, including "
             "their own.",
    backstory=(
        "Oliver ran a small optician's in Clifton for eleven years, with a test chart, a cardigan and a kettle that "
        "never got a rest. He's kind, careful and a little shy, and he can't walk past a pair of glasses that need "
        "adjusting. He woke on a sky island with his spectacles still on, and the House of the Patient Lens has "
        "thought him the most interesting man in the sky ever since. At Lenswatch the light listens to him, and "
        "he's learned to put it where people hurt."),
    before=(
        "A shop with a green door on a steep street, a cat that slept in the frames display and a choir on Thursday "
        "nights.\n\n"
        "He once caught something serious behind a schoolboy's eye during a routine test, and the boy's mother sent "
        "him a card every Christmas after."),
    adjustment=(
        "The lensmaster at Lenswatch sat him down on his first day and asked him about eyes for nine hours straight. "
        "Oliver answered every question and then asked for a cup of tea.\n\n"
        "The light came the first time he held a lens up to a wounded guard, and it went straight through the glass "
        "into the wound."),
    forward=(
        "He wants to make a proper pair of glasses for an Aetherian, whose eyes glow, which nobody's ever tried.\n\n"
        "He'd also like his cardigan back, and he knows that isn't going to happen."),
    now=(
        "At Lenswatch, in the survey's workshop, grinding lenses with the lensmaster and arguing happily about "
        "light.\n\n"
        "He sees the Earthborn wards about their eyes once a week, because nobody else up here knows how."),
    look=("English man, 36, tall and slim, neatly parted light-brown hair, clean-shaven, fair skin, hazel eyes behind "
          "round wire spectacles. White and gold sun-cleric robes with a gold sun disc, a slim staff topped with a "
          "glowing sun, a pen-torch clipped in his breast pocket."),
),
"facundo_chronomancer": dict(
    greeting="Everything runs slow or fast if you listen closely enough. Your heart's a little quick, by the way, so "
             "sit down for a minute.",
    backstory=(
        "Facundo repaired watches in Mendoza for twenty years in his grandfather's shop, under a sign nobody had "
        "repainted in half a century. He can strip a pocket watch to its last screw and put it back together "
        "blindfold, and he's the most patient man anyone in the Expanse has met. He woke on a sky island with his "
        "loupe round his neck and his grandfather's watch still ticking. The Aetherians found him, and up here he "
        "can wind time back a little on a wound."),
    before=(
        "A narrow shop between a bakery and a shoe repairer, a bench by the window and a wall of clocks that all "
        "struck noon a few seconds apart.\n\n"
        "His grandfather taught him that you never force a watch. You listen to it until it tells you what's wrong."),
    adjustment=(
        "His grandfather's watch kept time on this world, which the Aetherian scholars found so interesting they "
        "took it apart. He made them put it back together in front of him.\n\n"
        "The first time he held a bleeding man's wrist, he felt the moment slip. He wound it back a few seconds, and "
        "the cut wasn't there."),
    forward=(
        "He wants to understand the golems' cores, because they're the most beautiful mechanism he's ever seen.\n\n"
        "He'd also like to know whether his grandfather's watch is keeping the same time at home."),
    now=(
        "In the Celestial Expanse, among the golems, sitting cross-legged with his loupe in his eye.\n\n"
        "He tends the wounded who come off the Golem Fields, and he winds his grandfather's watch every morning at "
        "the same minute."),
    look=("Argentine man, 37, medium build and fit, swept-back dark-brown hair, a short neat beard, light olive skin, "
          "brown eyes. Bronze and sand-gold chronomancer robes with clockwork motifs, a staff topped with a glowing "
          "hourglass, a jeweller's loupe on a cord and a gold pocket-watch chain."),
),
"renata_rogue": dict(
    greeting="People keep warning me about the edge. I've jumped off taller things for less money, and I always land.",
    backstory=(
        "Renata was a stunt double in Mexico City for nine years, the woman who fell off buildings, out of cars and "
        "down stairs so the stars didn't have to. She's fearless, funny and very good at falling, and she'll do any "
        "fall twice if the first take wasn't clean. She woke on a sky island right on the edge and nearly went over "
        "before she'd opened her eyes. The Aetherians found her climbing their skiff rigging for fun, and the "
        "Expanse's long drops feel like work to her, in a good way."),
    before=(
        "A rooftop flat in Roma Norte, a crash mat in the living room and a mother who refused to watch a single one "
        "of her films.\n\n"
        "She did the high fall in a telenovela finale off the roof of a hotel, and the director made her do it "
        "twice."),
    adjustment=(
        "The Aetherians wrote her down as a ward who kept escaping, which wasn't fair, because she always came "
        "back.\n\n"
        "She learned the blades from an Earthborn who'd been a chef, and she learned the rest by falling off islands "
        "and catching herself."),
    forward=(
        "She wants to dive off the edge of the Expanse into the cloud and come up somewhere else, just once, on "
        "purpose.\n\n"
        "She'd also like somebody to film it, and she knows that's the hard part."),
    now=(
        "In the Celestial Expanse, out on the edges where the falls pour off, walking the rims like a pavement.\n\n"
        "She runs messages between the islands faster than the skiffs, and she never takes the bridges."),
    look=("Mexican woman, 29, athletic and lithe, long dark-brown hair in a high ponytail, golden-tan skin, dark eyes. "
          "Fitted dark leather rogue armour with a short hooded cape, two short swords, black fingerless stunt "
          "gloves and a red bandana tied round one wrist."),
),
"tariq_bloodmage": dict(
    greeting="I gave blood every eight weeks for twenty years. Now it seems the blood remembers, and it gives a little "
             "back.",
    backstory=(
        "Tariq lifted weights for Iraq at two Asian Games, coached boys at a gym in Karrada after he retired, and "
        "gave blood every eight weeks from the day he turned eighteen. He's enormous, softly spoken and kinder than "
        "anyone expects, and he doesn't like to hurry. He woke on a sky island north of Aurelion and lifted a fallen "
        "cart off an Aetherian child before anyone had asked his name. The houses took him in as a guest, and the "
        "blood he gave all those years seems to know him here."),
    before=(
        "A gym with a tin roof and a bad fan, a wall of photographs of his boys and a wife who made the best kubba "
        "in the street.\n\n"
        "The nurse at the blood bank knew him by name, and she always gave him two biscuits instead of one."),
    adjustment=(
        "The Aetherians had never seen a man lift what he lifts, and the Ascendancy asked him to join within a week. "
        "He said no very politely.\n\n"
        "The first time he was cut in a fight, the blood didn't run. It stopped, and it pulled him back up."),
    forward=(
        "He wants to open a gym on this world for anyone at all, Aetherian or troll or Earthborn, with a fan that "
        "works.\n\n"
        "He'd also like someone to give two biscuits to, the way the nurse did."),
    now=(
        "In Aurelion, at the Ground Embassy, where the council's guests from the ground are housed.\n\n"
        "He carries things for the embassy's staff whether they ask or not, and the houses' guards have started "
        "training with him in the mornings."),
    look=("Iraqi man, 39, very big and powerfully built, short black hair, a full short black beard, warm brown skin, "
          "dark eyes. Heavy crimson and black bloodmage plate with blood-red runes, a rune-marked shield and a broad "
          "sword, a faint red mist round his free hand, a thick worn leather weightlifting belt."),
),
"isabela_mage": dict(
    greeting="The whole city sings when you touch it, did you know that? Put your hand on the wall and try it.",
    backstory=(
        "Isabela blew glass in a workshop on the lagoon at Florianópolis, bowls and lamps and fish for the tourists, "
        "and once a chandelier for a church that took her a whole summer. She's bright, chatty and enchanted by "
        "almost everything, and she's proud of the burn scars on both forearms. She woke on a sky island beside a "
        "crystal that was humming, and when she touched it, it sang. The Aetherians brought her to Aurelion to find "
        "out why, and they're still finding out."),
    before=(
        "A workshop with the doors open to the lagoon, a furnace that never went out and a brother who surfed and "
        "never once helped.\n\n"
        "She could tell the heat of the glass by its colour, to within a few degrees, and she never used a "
        "thermometer."),
    adjustment=(
        "The crystal on the island sang a note when she touched it, and the Aetherian who found her went white and "
        "sent for three scholars.\n\n"
        "The Academy taught her the arcane in a season, because she already knew how to shape something that glows."),
    forward=(
        "She wants to blow a lamp out of Aetherian crystal, which nobody up here has ever managed, because they only "
        "know how to cut it.\n\n"
        "She'd also like her brother to see the city, and she's sure he'd finally be impressed."),
    now=(
        "In Aurelion, by the Academies on the Inner Ring, with her hands on every wall she passes.\n\n"
        "The magisters let her work in a corner of the Academy's workshops, and the crystal hums whenever she walks "
        "in."),
    look=("Brazilian woman, 31, slim and graceful, long loose wavy dark-brown hair, warm light-brown skin, brown eyes. "
          "Violet and white arcane-mage robes with glowing crystal trim, a staff of clear blown glass with violet "
          "light inside, tinted glassblower's glasses pushed up into her hair."),
),
}
