# -*- coding: utf-8 -*-
"""Sheet 4: sixteen companions for the specs nobody had and the 50+ regions (claude/recruit_art_prompts_sheet4.md).

Kyle, 16 Nov 2026: "we add another 16 to the game to fill in what's missing... Since we added a lot with felwood,
stonetalon, tempeat Isle, and now plaguelands etc". The art landed 17 Nov 2026; "They can be spread out as per our
previous discussions", so they stand where the sheet's roster put them, with the Plaguelands moves since (Sorrow Hill
is gone and its people are in the Bulwark; Crown Guard is inside Light's Hope Chapel).

The recruit-overhaul voice: whole sentences said out loud, no clipped fragments, no "it's not X, it's Y". Every one of
them came through three years ago. The three who serve the Order of the Pale Flame talk about Rory and the Order, and
never about each other (recruits are strangers to each other).
"""

BATCH = {
"rhys_ranger": dict(
    greeting="Keep your voice down near the trees, would you? She hunts better when nobody's chattering at her.",
    backstory=(
        "Rhys flew hawks at weddings in the Brecon Beacons, which paid better than you'd think and was mostly "
        "about keeping a bird calm in front of two hundred people in hats. He had Tegan on his glove the evening "
        "the world changed, and she came through with him. He's quiet, patient and quick to laugh once he's "
        "decided you're all right, and he trusts the hawk's opinion of a stranger more than his own."),
    before=(
        "A falconry centre outside Brecon, weddings in the summer and school visits in the winter.\n\n"
        "His mam ran the café at the centre and called every bird by the wrong name on purpose."),
    adjustment=(
        "Tegan adjusted faster than he did. She found the first hare in Stonetalon inside a week, and he decided "
        "that if she could manage, he could too.\n\n"
        "He still checks the sky for weather the way he did at home, and here it's usually right."),
    forward=(
        "He wants to get word to Brecon, or to find out there's no Brecon to send it to.\n\n"
        "Until then he's teaching a Sun Rock boy how to hold a glove, and the boy is better at it than he was."),
    now=(
        "Out on the western ridges of Stonetalon, where the hunting is good and the road is quiet.\n\n"
        "Tegan sits on his arm while he talks and watches whoever he's talking to."),
    look=("Welsh man, 30, lean and athletic, dark brown wavy hair cut short, light stubble, grey-green eyes. Green and "
          "brown ranger leathers with a short hooded cloak, a longbow, a hunting horn, a hawk on a leather gauntlet, a "
          "falconer's swivel and bell on a cord round his wrist."),
),
"gunnar_barbarian": dict(
    greeting="You look like someone who's had a long road. Sit down, I've got something you should try.",
    backstory=(
        "Gunnar brewed beer in Akureyri, in a shed behind his uncle's garage that grew into a proper brewery with "
        "a queue out the door on Fridays. He's enormous, loud and generous, and he took to the barbarians of the "
        "north the moment he met them, because anyone who toasts their ancestors before a fight has the right "
        "idea about both. He still carries a hydrometer, and he still uses it."),
    before=(
        "A brewery, a dog called Brúnó, and a long-running argument with his sister about whether stout counts as "
        "food.\n\n"
        "He played second row for a rugby club that lost almost every match and celebrated every one anyway."),
    adjustment=(
        "He landed in snow, which helped. A clan took him in after he fixed their mead, and he's been fixing it "
        "since.\n\n"
        "He cried once, the first time he heard their ancestor songs, and he doesn't mind who knows it."),
    forward=(
        "He's after a barley that'll grow on the Arathi moor, because the stuff in Hammerfall's stores isn't fit "
        "for pigs.\n\n"
        "He'd like to brew something good enough that the orcs stop pretending they don't like it."),
    now=(
        "In Hammerfall, by the inn, swapping recipes with Grettha and losing most of the arguments.\n\n"
        "The keg on his back is never quite empty, and nobody has ever seen him fill it."),
    look=("Icelandic man, 37, very big and broad, long dark-blond hair tied back, a thick braided beard, pale blue "
          "eyes. Fur-trimmed barbarian hides over mail, a two-handed axe across his back and a small wooden keg on a "
          "strap, a brass hydrometer in a leather sleeve on his belt."),
),
"reka_necromancer": dict(
    greeting="Don't stare at the crow, it's shy. Well, it was shy. Now it's mostly bones and opinions.",
    backstory=(
        "Réka made stop-motion films in Budapest, moving puppets one frame at a time until they looked alive. "
        "She'd done it for twelve years when the Integration happened, and it turned out to be the best training "
        "for necromancy anyone has ever had. She's sly, funny and very precise, and she treats the dead the way "
        "she treated her puppets, with patience and a lot of small adjustments."),
    before=(
        "A studio above a bakery in the eighth district, and a short film that won a prize in Annecy.\n\n"
        "She lived alone with a cat that hated every puppet she ever made."),
    adjustment=(
        "The first time she raised something, she said she knew exactly where she'd gone wrong with the elbow.\n\n"
        "The people on the Black Strand don't like what she does, but they like that she's tidy about it."),
    forward=(
        "She wants to make something move that's never moved before, and she's careful not to say what.\n\n"
        "She's also looking for a good camera. She knows there isn't one, and she keeps looking anyway."),
    now=(
        "On the Black Strand, in the black sand under the Dry Deep, raising crows out of whatever the beetles "
        "leave.\n\n"
        "The little mannequin on her belt is the last thing she animated at home, and it still has the wire in its "
        "arm."),
    look=("Hungarian woman, 30, slim, glossy dark chestnut hair to her shoulders with a heavy fringe, pale skin, large "
          "dark-hazel eyes. Charcoal and bone-white necromancer robes with a high collar, a staff of bound bone, a "
          "small raised skeletal crow on her shoulder, a tiny wooden artist's mannequin on her belt."),
),
"ramiro_primalist": dict(
    greeting="Listen. No, really, listen. You can hear the rock settling. This town's built on good stone.",
    backstory=(
        "Ramiro mined silver in Potosí, in the Cerro Rico, like his father and his grandfather, and he learned "
        "young that the mountain talks before it moves. He's steady, proud and quietly funny, and the Dark Iron "
        "of Onyxhollow took to him because he hears the rock the way they do. The earth answers him now, which "
        "he says is only fair after all the years he spent listening to it."),
    before=(
        "Twelve-hour shifts, a cooperative that never paid on time, and a wife who ran a juice stall in the "
        "market.\n\n"
        "He has two daughters, and the elder wanted to be a geologist. He was saving for it."),
    adjustment=(
        "He came through underground, which was the one thing that made sense.\n\n"
        "The first stone that lifted itself into his hand frightened him badly. The second one he asked "
        "politely."),
    forward=(
        "He wants to find out whether Potosí came through, and whether anyone is still underneath it.\n\n"
        "He's teaching the Onyxhollow apprentices to timber a drift the way his father did, and they've stopped "
        "laughing at the method."),
    now=(
        "In Onyxhollow, in the mining quarter, mostly listening.\n\n"
        "The carbide lamp on his belt hasn't had fuel in three years. He keeps it polished anyway."),
    look=("Bolivian man, 36, compact and powerful, black hair cropped short, warm brown skin, dark eyes. Primalist "
          "plate studded with raw stone in grey and ochre, a stone-headed stave, pebbles floating above his open "
          "hand, a dented brass carbide headlamp strapped to his belt."),
),
"graham_warlock": dict(
    greeting="Sit down a minute if you need to. Most people who come up this road do, and there's no shame in it.",
    backstory=(
        "Graham was a hospice nurse in Lancashire for nineteen years. He sat with people at the end of their "
        "lives and learned that a slow ending can be a kind one if somebody pays attention. Affliction came to "
        "him easily, which bothered him more than anything else here, until he worked out it's the same "
        "patience pointed the other way. He's gentle, tired and very good company."),
    before=(
        "Night shifts at a hospice outside Preston, and a garden he never had time for.\n\n"
        "His husband Tom taught music at the primary school and sang in the car whether Graham liked it or not."),
    adjustment=(
        "He spent the first year nursing whoever needed it, and the second year learning why the Forsaken "
        "didn't.\n\n"
        "When he found out what he could do with shadow, he sat with that for a long while before he used it."),
    forward=(
        "He's looking for Tom. He goes through the lists at every town he passes and he hasn't missed one yet.\n\n"
        "He'd also like a garden, and the Pale Watch has a corner of ground he's been eyeing."),
    now=(
        "At the Pale Watch, where the plague comes up close and slow, which he understands better than most.\n\n"
        "The watch pinned upside down on his chest still runs. He winds it every morning before anything else."),
    look=("English man, 41, tall and fit, light brown hair going silver at the temples, light beard, blue-grey eyes. "
          "Dark violet and sickly green affliction robes with a long scarf, a staff with a cracked lantern, faint green "
          "motes, a nurse's fob watch pinned upside down on his chest."),
),
"elie_bloodmage": dict(
    greeting="Give me your arm. I promise this is the least frightening thing you'll see in Khaz Varun.",
    backstory=(
        "Elie drew blood for a living in Beirut, at a clinic in Achrafieh, and he was the one the nervous patients "
        "asked for. He came through with a tourniquet in his pocket and found out that blood listens to him now. "
        "He heals with it, which most bloodmages think is a waste and which he thinks is the only sensible use. "
        "He's calm, warm and careful, and very hard to rattle."),
    before=(
        "The clinic, his mother's cooking every Sunday, and a motorbike he kept running on spare parts and "
        "faith.\n\n"
        "He was saving to go to medical school in Montpellier. He'd been saving for six years."),
    adjustment=(
        "The first time he felt someone's blood move under his hand, he finished the job before he let himself "
        "be frightened.\n\n"
        "He says the work is the same as it ever was, he just doesn't need the needle."),
    forward=(
        "He wants to train other people to do it. The Ashclaim's healers keep asking, and he keeps saying yes.\n\n"
        "He'd also like to see the sea again. He grew up beside it."),
    now=(
        "In the upper halls of Khaz Varun, patching up whoever comes out of the dark worse than they went in.\n\n"
        "The blue needle cap clipped to his sleeve is from the last blood draw he did at home. He's never taken "
        "it off."),
    look=("Lebanese man, 33, slim and neat, black hair swept back, close trimmed beard, dark eyes. Crimson and black "
          "bloodmage robes over light mail, a short ritual knife and a slim staff, red threads of light at his "
          "fingers, a tourniquet band and a blue butterfly-needle cap clipped to his sleeve."),
),
"bruno_templar": dict(
    greeting="Rory says I smile too much for a templar. I tell him somebody in the Order has to.",
    backstory=(
        "Bruno fought heavyweight in Curitiba, in small halls with loud crowds, and he was better at it than his "
        "record says. He joined the Scarlet Crusade in the first months because it was the only army winning, "
        "and he walked out of it beside Rory Callahan the night they burned the transplant camp. He's huge, "
        "cheerful and very hard to knock down, and he fights like the bell's about to go."),
    before=(
        "A gym above a tyre shop, a coach called Seu Valdir, and twenty-three fights with eighteen wins.\n\n"
        "His mother came to every fight and covered her eyes for all of them."),
    adjustment=(
        "He says the Crusade took him in and taught him the Light, and that's the part he kept.\n\n"
        "The rest he left on the road out of Hearthglen, and he doesn't talk about that night unless Rory does "
        "first."),
    forward=(
        "He wants the Order to be big enough that nobody has to choose between the Crusade and nothing again.\n\n"
        "He's also teaching the Bulwark's recruits to fight with their hands, and he's delighted with all of "
        "them."),
    now=(
        "In the Order's quarter of the Bulwark, training anyone who'll stand in front of him.\n\n"
        "The roll of black hand-wrap on his belt is from his last fight at home. He won it."),
    look=("Brazilian man, 34, huge through the chest and shoulders, short dark brown hair, light olive skin, short dark "
          "beard, warm brown eyes. Grey steel templar plate with a white tabard bearing a pale flame, a two-handed "
          "warhammer with white holy fire, a roll of black fighter's hand-wrap tucked in his belt."),
),
"joaquin_suncleric": dict(
    greeting="If you've got something heavy to put down, the Order's a good place to do it. I'd know.",
    backstory=(
        "Joaquín taught history at a secondary school in Rosario until the Integration. In the Crusade they made "
        "him an interrogator, because he was patient and he listened, and he was good at it in a way he'll be "
        "sorry for until he dies. He left with Rory Callahan. Now he heals with the same hands, and he fights "
        "with them too, and he carries what he did there without asking anyone to carry it for him."),
    before=(
        "A classroom of fifteen-year-olds, a mate gourd on his desk, and a novel he'd been writing for nine "
        "years.\n\n"
        "He was good with the difficult kids, because he listened to them."),
    adjustment=(
        "He says he adjusted too well, and that's the whole problem.\n\n"
        "Rory found him in a cell in Hearthglen at four in the morning, sitting with a prisoner he'd been told to "
        "break, and they walked out together."),
    forward=(
        "He's writing down the names of everyone he questioned. He wants to find the ones who lived and say he's "
        "sorry to their faces.\n\n"
        "He's found four so far. Two of them hit him, and he says they were right to."),
    now=(
        "At the Bulwark with the Order, healing the hurt that come in from the plaguelands.\n\n"
        "The mate gourd at his hip is the one from his classroom desk, and he still drinks from it every "
        "morning."),
    look=("Argentine man, 38, tall and lean, dark hair a little long and swept back, close dark beard, dark eyes, a "
          "handsome haunted face. Grey mail over a white undercoat with a pale flame on the chest, hands wrapped for "
          "fist-fighting, sun-gold light at his knuckles, a worn leather mate gourd and silver bombilla at his hip."),
),
"astrid_starcaller": dict(
    greeting="Clear nights are the best ones up here. The stars are wrong, but they're very bright.",
    backstory=(
        "Astrid photographed the aurora above Kiruna for tourists and magazines, and spent most of her twenties "
        "lying in snow waiting for the sky to do something. She came through on a clear night with her camera "
        "round her neck, and the stars here answered her within the week. She hunts by starlight in North "
        "Felwood now. She's calm and bright and very good at waiting for the right moment."),
    before=(
        "Kiruna, a cabin with no road to it in winter, and a camera worth more than her car.\n\n"
        "She had a brother in Stockholm who called every Sunday to ask if she was still alive."),
    adjustment=(
        "The camera stopped working, which she found harder than anything else.\n\n"
        "The Sentinels at Talonbranch taught her the bow, and the stars taught her the rest."),
    forward=(
        "She's mapping the new sky, star by star, in a notebook the size of a brick.\n\n"
        "She'd like to find her brother's Sunday call again. She knows it's not likely, and she keeps the habit "
        "anyway."),
    now=(
        "In North Felwood, out near the Talonbranch camp, hunting what comes out of the fel when the light's "
        "low.\n\n"
        "The lens cap round her neck belongs to a camera that hasn't worked in three years."),
    look=("Swedish woman, 32, slim and athletic, long platinum-blonde hair in a loose braid, pale skin, ice-blue eyes. "
          "Silver and midnight-blue sentinel leathers, a tall bow strung with faint starlight, star motes along the "
          "arrows, a small camera lens cap on a cord round her neck."),
),
"luka_stormbringer": dict(
    greeting="Ever seen a squall come in over open water? I have. Stand behind me and you'll be fine.",
    backstory=(
        "Luka captained a car ferry between Split and the islands for fifteen years, and he knows the sea well "
        "enough to be properly afraid of it. The storm found him on the crossing, and it's been following him "
        "since. He calls it up now on Tempest Isle, carefully, the way he used to read the weather off the "
        "Adriatic. He's wry, weathered and the steadiest person in any room."),
    before=(
        "A ferry called the Marjan, a crew of eight, and a wife who ran a konoba on Brač.\n\n"
        "His son played water polo, badly, and Luka never missed a match."),
    adjustment=(
        "He woke up on a beach with the ferry's whistle in his hand and no ferry.\n\n"
        "The first storm he called up nearly drowned him, and he says that's how he knew it was his."),
    forward=(
        "He wants a boat. A small one, sound and his own, and he'd take it home if he knew which way home was.\n\n"
        "Until then he's teaching the Ashclaim's crews to read the weather before it reads them."),
    now=(
        "On the Tempest Shallows, near the landing, watching the sky.\n\n"
        "The brass whistle on his lanyard is from the Marjan's bridge, and he blows it once every evening at "
        "the time the last ferry used to leave."),
    look=("Croatian man, 39, tall and broad-shouldered, short dark hair with some grey, short beard, sea-blue eyes. "
          "Deep sea-green and storm-grey robes with a short cloak that drips water, a driftwood staff bound in silver, "
          "frost and spray at his feet, a brass ship's whistle on a lanyard."),
),
"zofia_cultist": dict(
    greeting="I know what these robes look like. I tore their symbols off myself, so you can stop staring.",
    backstory=(
        "Zofia answered phones for an insurance company in Łódź, eight hours a day of people shouting at her "
        "about things she couldn't fix. The Cult of the Damned found her in the first winter and promised her "
        "that she'd never be powerless again, and for a while they kept the promise. Then she saw what it cost, "
        "and she walked out of Andorhal with what they'd taught her. She's guarded and determined, and nobody "
        "talks down to her twice."),
    before=(
        "A call centre, a flat with her grandmother, and a night course in accounting she was two exams from "
        "finishing.\n\n"
        "Her grandmother taught her to play cards and cheated every single time."),
    adjustment=(
        "She'd rather not talk about the first year, and she'll tell you that plainly.\n\n"
        "She left Andorhal at night, alone, and she took three of the Cult's books with her."),
    forward=(
        "She wants every Cult house in the Plaguelands burned, and she knows where most of them are.\n\n"
        "After that she'd like to finish the accounting course, and she's not joking."),
    now=(
        "In the north of the Western Plaguelands, near Andorhal, hunting the people who recruited her.\n\n"
        "The headset clip pinned to her collar is from her desk at the call centre, and she wears it like a "
        "medal."),
    look=("Polish woman, 29, slender, long dark-brown hair loose past her shoulders, pale skin, dark eyes, a serious "
          "face. Deep violet and black shadow robes with the Cult's symbols torn off and the stitches showing, a thin "
          "dark staff, shadow at her fingertips, a black plastic headset clip pinned to her collar."),
),
"omar_venomancer": dict(
    greeting="Don't swat at them. Things that sting only get worse when you panic, and they can tell.",
    backstory=(
        "Sherif did pest control in Cairo, fumigating apartment blocks and restaurants and once, memorably, a "
        "museum storeroom. He's spent his whole working life very calm around things that sting, and the "
        "Royal Hive is full of them. He came through with his fumigation rig and found out venom listens to him "
        "here. He's unbothered, amused and the only person who walks into the hive without flinching."),
    before=(
        "A van, a fogging machine, and a family business his father started in 1987.\n\n"
        "He was engaged to a pharmacist called Mariam, and the wedding was set for the spring after."),
    adjustment=(
        "He says the bugs here are bigger, and otherwise it's the same job.\n\n"
        "He means it as a joke, and he also means it."),
    forward=(
        "He's studying the hive's poisons, all of them, because a poison you understand is half an antidote.\n\n"
        "He's looking for Mariam. He asks every healer he meets, because she'd have ended up near the sick."),
    now=(
        "Inside the Royal Hive, in the first chambers, cataloguing what lives there.\n\n"
        "The brass nozzle hanging from his belt came off his old fogging rig, and he still checks it for "
        "blockages."),
    look=("Egyptian man, 35, medium build and very fit, short black hair, trimmed beard, dark eyes, a calm face. Dark "
          "green and sand venomancer robes with a hooded mantle, glass vials and spore pods on a bandolier, a staff "
          "with a coiled serpent, a brass fumigation nozzle hanging from his belt."),
),
"santiago_runemaster": dict(
    greeting="Every rune's a line you can't take back. Same as a tattoo, really, just a lot louder.",
    backstory=(
        "Santiago tattooed in Medellín, in a shop in Laureles with a waiting list that ran for months. He came "
        "through with his machine in his pocket and runes started showing up in his work within the month. He "
        "engraves them into his blades now, and into his own arms, and they burn when he fights. He's confident, "
        "bright and a perfectionist about line work in a way that makes the Ashclaim's smiths nervous."),
    before=(
        "A shop with his cousin, three hundred clients' worth of designs in a folder, and a little brother he "
        "was putting through school.\n\n"
        "His mother never approved of the tattoos and had a small one done anyway, by him."),
    adjustment=(
        "The first rune he cut glowed, and he spent a week trying to work out what he'd done right.\n\n"
        "He worked it out, and his arms are proof."),
    forward=(
        "He wants to design a rune nobody's ever cut before, and he's filled three notebooks trying.\n\n"
        "He's also looking for his brother, who was at school in Bogotá that day."),
    now=(
        "On the Ashen Reach, near the works, cutting runes into anything that'll hold still.\n\n"
        "The tattoo machine grip on his hip is from his station at the shop, and he still cleans it every "
        "night."),
    look=("Colombian man, 28, lean and athletic, black hair in a short fade with a longer top, light stubble, dark "
          "eyes, glowing rune tattoos down both forearms. Charcoal and electric-blue battle-wraps, a runed blade in "
          "each hand, a black and steel tattoo machine grip on a cord at his hip."),
),
"emiliano_pyromancer": dict(
    greeting="Want to see a trick? I used to do this for coins at a red light. Now I do it for the Ashclaim.",
    backstory=(
        "Emiliano breathed fire at traffic lights in Oaxaca, two minutes a red light, for coins from the "
        "windows. He was good at it and very good at talking, and he came through with a bottle of lamp oil on "
        "his belt. The fire here took to him at once. Now it comes out of him the colour of a dragon's breath, "
        "and he's cocky about it, and he's earned some of that."),
    before=(
        "A corner by the zócalo, four younger sisters, and a dream of a circus that would take him on.\n\n"
        "He never once burned himself, and he'll show you the hands to prove it."),
    adjustment=(
        "He says the Integration finally gave him the stage he wanted, and he only half means it.\n\n"
        "The Ashclaim hired him the day he lit their forge from across the yard."),
    forward=(
        "He wants a real show, in a real tent, with an audience that paid to get in.\n\n"
        "He's also sending money home on every ship that leaves Cinderwharf, in case one of them finds it."),
    now=(
        "In Cinderwharf, by the forges, showing off to anyone who'll watch.\n\n"
        "The bottle of lamp oil on his belt is the one he carried at home, and the label's nearly gone."),
    look=("Mexican man, 29, slim and wiry, black hair a little wild, thin moustache, dark eyes, a cocky grin. Scarlet "
          "and gold pyromancer robes with dragon-scale trim and a draconic collar, a slim rod, a curl of flame at his "
          "lips, a plastic bottle of lamp oil with a faded label on his belt."),
),
"isla_witchhunter": dict(
    greeting="I don't miss, and I'd rather not have to prove it today. Is there something you need?",
    backstory=(
        "Isla stalked deer in the Highlands for the estates and shot biathlon for Scotland, and she's the "
        "stillest person you'll ever meet with a weapon in her hands. She stayed well clear of the Crusade. She "
        "joined the Order of the Pale Flame after Rory Callahan walked out of it, because she'd watched the Order "
        "do the work cleanly. She's sharp, level and quietly kind once the shooting stops."),
    before=(
        "A cottage above Glen Affric, the estate's deer, and a rifle she'd carried since she was fourteen.\n\n"
        "She'd qualified for the World Cup the month before, and her dad had booked the time off to come."),
    adjustment=(
        "She went a year on her own, hunting what needed hunting in the Plaguelands.\n\n"
        "The Order was the first group of people she met here who didn't waste a shot."),
    forward=(
        "She wants Stratholme cleared, properly, and she'll be there when it is.\n\n"
        "She'd also like to hear her dad laugh again. She keeps that one to herself."),
    now=(
        "At Light's Hope Chapel with the Order's camp, keeping watch over the eastern road.\n\n"
        "The steel buckle on her crossbow strap came off her biathlon rifle sling, and she's never thought about "
        "replacing it."),
    look=("Scottish woman, 31, athletic and strong, long red hair in a thick braid, pale freckled skin, green eyes. A "
          "grey storm-coat over leathers with a white pale-flame pin, a heavy crossbow carried low, bolts at her hip, "
          "a worn steel biathlon rifle-sling buckle on her strap."),
),
"dale_reaper": dict(
    greeting="Bad ground out here, but it's ground. You'd be surprised what comes back if you give it time.",
    backstory=(
        "Dale farmed wheat outside Minot, North Dakota, on land his family had worked for four generations. He's "
        "big, slow-spoken and very hard to hurry, and he knows how to bring a harvest in before the weather "
        "turns. The scythe came naturally. He walks the plagued fields of the east now with it, and he says "
        "he's doing what he always did, which is clearing ground so something better can grow."),
    before=(
        "Two thousand acres, a combine he'd paid off the spring before, and a wife who ran the county co-op.\n\n"
        "His kids were grown and gone to Fargo and Denver, and they called every Sunday after church."),
    adjustment=(
        "He took his time, the way he takes it with everything.\n\n"
        "The first time he swung the scythe at something dead, he said it felt like the last pass of a long "
        "harvest."),
    forward=(
        "He wants to plant the Eastern Plaguelands one day, properly, with wheat that comes up clean.\n\n"
        "He's been testing soil from every field he crosses and writing the results on the back of seed "
        "packets."),
    now=(
        "Out in the Eastern Plaguelands, working the fields one row at a time.\n\n"
        "The seed-company cap tucked in his belt is the one he wore on the combine, and he puts it on when the "
        "work's done."),
    look=("American man, 44, big and broad, sandy-brown hair cut short, short greying beard, blue eyes, a rugged "
          "sun-creased face. Dark brown and iron reaper plate, plain and practical, a huge two-handed scythe carried "
          "low, a seed-company cap folded into his belt."),
),
}
