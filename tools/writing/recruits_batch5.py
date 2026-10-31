# -*- coding: utf-8 -*-
"""Batch 5, the last of the recruit rewrite (levels 34-48). See tools/rewrite_recruits.py.

ZONE DRIFT FIXED HERE TOO. tools/spread_recruits.py moved thirteen companions earlier today and
nothing updated their prose, so four of these had a `now` section describing a town they no
longer stand in - Stelios writing up the Undercity from Glittervein, Kiet opening Orgrimmar's
locks from the Abyssal Sands. Their `now` matches their zone again.
"""

BATCH = {

"junseo_reaper": dict(
    greeting="People hear the spec and expect something from me. A mood, maybe. I welded ships. "
             "I will stand where the hit lands, you will work behind me, and that is all this "
             "is.",
    backstory=(
        "Nineteen years welding hulls in a Ulsan drydock, mostly night shift because the steel "
        "moves less when it is cool, inside compartments that had not been opened yet — where a "
        "man watches the gas meter and his own two hands and nothing else exists. He is "
        "unbothered by confined dark places and openly puzzled that anybody treats this as a "
        "personality rather than a work history."),
    before=(
        "Two apprentices he liked and one he could not teach.\n\n"
        "He still thinks about the third one. He has never been able to work out whether the "
        "failure was the boy's or his, and he has had nineteen years and a world ending to "
        "consider it."),
    adjustment=(
        "He arrived with the shade down and the arc still burned into his eyes.\n\n"
        "He has said the worst part was how quiet it was."),
    forward=(
        "To teach somebody something properly — start to finish, and have it hold.\n\n"
        "He has not found anyone who will stand still long enough, and he is starting to suspect "
        "the problem is not them."),
    now=(
        "Central Stranglethorn: the arena apron and the Veilfall's dry shoulder, taking the hits "
        "for whoever is working behind him.\n\n"
        "He has no interest in the drums at all and finds the betting faintly embarrassing."),
),

"alonso_pyromancer": dict(
    greeting="Yes, it is fire. It was always fire — twenty years I kept something alive at "
             "eleven hundred degrees. Hold still. It will feel like standing too close to an "
             "oven, and then it will feel like nothing.",
    backstory=(
        "A hot shop off a side street in Guadalajara, his father's before it was his: three "
        "benches and a furnace they fed in shifts so it never once went cold. He made vases "
        "nobody needed and one window for a church that is still standing. Fire was a tool you "
        "respected rather than a thing you feared, so healing with it was not a leap for him at "
        "all. Everybody else finds it a leap, and he has given up on the explanation."),
    before=(
        "The furnace. Twenty years of it, and it never went out, not once, including the week "
        "his father died."),
    adjustment=(
        "He arrived with a blowpipe and a gather still on the end of it, and watched the glass "
        "go solid in the grass because there was no annealer anywhere in the world any more.\n\n"
        "It cracked as it cooled. He kept the pieces for a year and then stopped."),
    forward=(
        "A furnace. He has picked the spot, worked out the clay, and started badgering Booty Bay "
        "about sand, and he is entirely serious about every part of it."),
    now=(
        "The Veilfall basin and the arena apron, where burns come in steadily and most healers "
        "flinch at them.\n\n"
        "He does not flinch at burns. He is also the only source of flat glass within four days' "
        "walk, which he finds extremely funny and nobody else does."),
),

"kesten_the_catalogued": dict(
    greeting="Entry four hundred and six. That is me, not a thing I found. You get used to it.",
    backstory=(
        "Twenty-two years a monumental mason in Aberdeen, cutting letters into granite for "
        "people who had died. It is a trade with one unforgiving rule and he will give it to you "
        "unprompted: the stone does not care how you felt about the deadline. He cut names for "
        "families who could not pay and never mentioned it to anyone. He walked down the Alterac "
        "fissure in the first year, before there was a path worn into the lip, not looking for "
        "safety but for the only people he had met who were also writing things down. The Codex "
        "did not turn him away and did not quite take him in. They gave him a catalogue number — "
        "the most anybody has ever formally given him — and he has never once objected."),
    before=(
        "A yard, a mallet, and a good tradesman's reputation in a city that did not otherwise "
        "notice him. He was, by any measure that matters, fairly lonely.\n\n"
        "He has not described it that way out loud. He would if asked directly."),
    adjustment=(
        "He arrived with his hands and nothing else, which for a man of his trade is the entire "
        "inventory."),
    forward=(
        "He would like to know whether the number is loyalty or the closest thing to a headstone "
        "anyone has ever offered him.\n\n"
        "Three years and he has not decided. He suspects the Codex have not decided either, and "
        "that this makes it the most honest relationship in the cavern."),
    now=(
        "Kael's Bastion. Entry eleven thousand and something, the only line in the whole index "
        "that is a person.\n\n"
        "He cuts their runes now — the deep ones, in the columns, the ones that have to outlast "
        "the people who ordered them. Same trade, same rule, considerably better stone."),
),

"kourosh_mage": dict(
    greeting="I am going to stand back here and be extremely precise. You are welcome to be "
             "brave — somebody in a group should be, and it was never going to be the actuary.",
    backstory=(
        "Twelve years pricing mortality for a Tehran insurer: the work of establishing, very "
        "carefully, how likely a thing is. He finds arcane magic restful by comparison because "
        "for once the numbers hold still. He is the only person on this side of the mountains "
        "who has calculated his own odds and he will not tell anybody the figure, and the "
        "refusal is cheerful rather than grim, which people find worse."),
    before=(
        "Tables, reserving, a good office with a bad view, and a mother he telephoned on Fridays "
        "who thought the job was beneath him.\n\n"
        "She was right that he was capable of more. She was wrong about what more would have "
        "meant."),
    adjustment=(
        "He arrived mid-calculation and the first thing he did on this world was finish the sum.\n\n"
        "He says that was not bravery, it was momentum, and he is irritated that people keep "
        "wanting it to be the other thing."),
    forward=(
        "There is no press, no journal and no readership, and he is writing it anyway — longhand, "
        "in a case he keeps dry.\n\n"
        "He has told two people what is in it. Both changed the subject, and he recorded the "
        "date each time."),
    now=(
        "The Crystalline Underdark, where the lattice does something to arcane magic that nobody "
        "has characterised.\n\n"
        "He is characterising it. The case is nearly full."),
),

"ziad_felsworn": dict(
    greeting="I go in first and I come out fast. Do not follow me in — that is not modesty, you "
             "will genuinely be in my way.",
    backstory=(
        "Nine years behind a desk in rooms with no windows, four nights a week, reading a crowd "
        "in the dark and riding the exact moment it turned. He could tell you what a room was "
        "going to want eight bars before it wanted it. He fights on the same instinct and he is "
        "good enough at it that it has started to worry people who like him. He knows precisely "
        "what bargain he made. He declines to discuss it in a way that is almost charming, and "
        "the almost is doing a great deal of work."),
    before=(
        "A flat above a bakery in Mar Mikhael and a city that had already taught him what it "
        "costs to stay somewhere you love."),
    adjustment=(
        "He arrived at two in the morning with the set still running.\n\n"
        "The silence afterwards is the thing he has never been able to describe properly, and he "
        "has tried, to four people, in two languages."),
    forward=(
        "Whether what he took can be given back.\n\n"
        "He has asked two people. Both laughed. He has stopped asking and has not stopped "
        "wanting to know."),
    now=(
        "The Bloodsail shallows and the wrecks off Jaguero Spit, where he is paid well and asked "
        "nothing.\n\n"
        "The green in his eyes has got stronger this last year. He has started wearing a hood "
        "and has told everybody it is the sun."),
),

"ratih_ranger": dict(
    greeting="I shoot from where the ground tells me to stand. If I say move — move. I have "
             "been right about water for fifteen years and I am right about this.",
    backstory=(
        "Fifteen years measuring rivers for the Indonesian water service, mostly alone, mostly "
        "walking: the job of knowing where water will be next week. A motorbike, a notebook that "
        "was permanently wet, and the habit of being the only person who had walked the whole "
        "catchment. She reads a landscape the same way here, which is why she saw the tide line "
        "move before anybody in Booty Bay did, and why nobody believed her, and why she has "
        "stopped volunteering it."),
    before=(
        "Gauging stations the length of Java, and a succession of officials who wanted the "
        "number to be different.\n\n"
        "It was never different. She has a great deal of practice at this conversation."),
    adjustment=(
        "She has not stopped surveying since the day she arrived, because there is an entire "
        "world of water here that nobody has written down."),
    forward=(
        "Somebody to write it down with her.\n\n"
        "She has begun approaching strangers about this and she knows it is going badly. She "
        "cannot work out how to say *I need a second pair of hands for forty years of work* in a "
        "way that does not frighten people off, so she says it quickly and watches them leave."),
    now=(
        "The Shimmering Flats: a pan that was under water once and is not now, which is a thing "
        "nobody out there has written down and she cannot stop thinking about.\n\n"
        "She is on good terms with exactly one tauren and no goblins at all."),
),

"fiona_witchhunter": dict(
    greeting="Front. Aye. Standing still while something hits me isn't the hard part of my day "
             "and never was.",
    backstory=(
        "She counts the people around her before she moves. She did it in a crane cab a hundred "
        "and twenty miles off Aberdeen, twelve on and twelve off, three weeks on the water and "
        "three at home, and she does it here, and she will do it whether or not anybody has "
        "asked her to. Moving something enormous over the heads of people who trust you, in bad "
        "weather, without ever once being interesting about it. Nobody clapped on the deck "
        "either."),
    before=(
        "The cab. She was good and she was known for it, in the small way a crane operator is "
        "known."),
    adjustment=(
        "A fortnight of looking up for a load that was not there. That passed.\n\n"
        "The counting did not."),
    forward=(
        "A reason to be somewhere specific rather than wherever the work is.\n\n"
        "She has started saying this out loud, which for her is enormous, and she has noticed "
        "that nobody has yet offered her one."),
    now=(
        "The cape road and the drowned terraces below Zul'Kundaraz, where the Saltscale come up "
        "out of water she does not trust an inch.\n\n"
        "She has made herself the person who goes in first. The Bay finds that useful and does "
        "not pay extra for it."),
),

"delroy_witchdoctor": dict(
    greeting="Sit. Drink that. No, I'm not telling you what's in it, you wouldn't thank me. "
             "Thirty-one years I fed a city its breakfast and not one of them ever asked what "
             "was in the bread either.",
    backstory=(
        "Thirty-one years of nights in a bakery on Spanish Town Road, in at eleven and out at "
        "seven, measuring by hand and by feel. He knew the weather by how the dough behaved and "
        "the regulars by what they bought. A brew is a dough with different patience. He treats "
        "a wounded party exactly like an order going out at dawn: everybody gets something, "
        "nobody waits long, and the complaining is part of the process."),
    before=(
        "The night shift. He has never in his life been awake at the same hours as everybody "
        "else and has never regarded that as a sacrifice."),
    adjustment=(
        "He arrived at four in the morning his time, which is the only reason, he says, that he "
        "was not asleep when it happened.\n\n"
        "He says it like a joke. It is not entirely a joke and he knows which parts are which."),
    forward=(
        "An oven, and then an apprentice, in that order, and he has made it clear he will not be "
        "hurried on either count.\n\n"
        "He has been offered a share in a Bay kitchen twice and turned it down twice, for "
        "reasons he gives freely and which nobody finds convincing."),
    now=(
        "Booty Bay, on the lower gallery, where the pier work breaks people steadily and the "
        "Baron does not care.\n\n"
        "He works nights out of habit. He has a following among the bruisers, who pretend not to "
        "be queueing."),
),

"pieter_guardian": dict(
    greeting="I have a shield and I am going to hit you with it. Twenty-two years I watched "
             "other people run onto a field I cut. I am not standing at the back of anything "
             "again.",
    backstory=(
        "Twenty-two years keeping a provincial rugby ground outside Bloemfontein — grass, lines, "
        "drainage, and Saturdays spent watching other people use what he had made. He knew every "
        "soft patch on that pitch and could give you the drainage history of all of it. He is a "
        "tank by trade and refuses to play like one, on the stated grounds that he has done quite "
        "enough standing about, and the heat in his voice when he says it surprises people who "
        "have only met the cheerful version."),
    before=(
        "A mower, a line marker, a shed, and a wife who ran the clubhouse bar and could fill it "
        "on a Tuesday."),
    adjustment=(
        "He arrived on a Saturday morning with the lines half cut.\n\n"
        "He says the worst of it is not knowing whether anybody finished them."),
    forward=(
        "A patch of flat ground and permission to cut it.\n\n"
        "He is aware this is not what anybody expects a man of his size and volume to say, and "
        "he says it anyway, to anybody who asks, immediately."),
    now=(
        "Northern Tanaris, out along the salt road, in the thick of it and loudly.\n\n"
        "He has made himself popular in every camp between here and the coast and mildly "
        "notorious with anybody who has ever tried to organise him."),
),

"kiet_rogue": dict(
    greeting="I am quiet and I am not brave. These are two different things and both are worth "
             "paying for. Point me at what is shut.",
    backstory=(
        "A locksmith's booth off a lane near Tha Phae, a scooter, and a reputation for being "
        "discreet — cutting keys for people who had locked themselves out and, occasionally, for "
        "people who had not. He is incurious about violence and extremely curious about "
        "mechanisms, and he will tell you that combination has kept him alive twice and employed "
        "continuously."),
    before=(
        "Opinions about every lock in the old city, and a favourite he would not name to anyone, "
        "including his wife, including under direct and repeated questioning."),
    adjustment=(
        "He arrived holding a customer's key.\n\n"
        "He has kept it. Uncut, useless, three years, and he does not explain it."),
    forward=(
        "What the old stonework out here is hiding.\n\n"
        "He has worked out that the answer is a very long way south, which has not deterred him "
        "in the slightest and has begun to alarm the two people who like him."),
    now=(
        "The Abyssal Sands, where the buried doors are older than anything in Tanaris and were "
        "built by people who did not expect to be followed.\n\n"
        "He opens them for whoever is paying and occasionally for nobody at all, and has already "
        "got further in than anyone has authorised."),
),

"stelios_necromancer": dict(
    greeting="I keep records. You will find that less sinister than you expect and more useful "
             "than you think. Most of what walks here is only angry about being forgotten.",
    backstory=(
        "Seventeen years running the library in a Corinth prison — a card catalogue he refused "
        "to digitise and a readership of four hundred men who were not supposed to matter. He "
        "knew every one of their borrowing histories and treated all of them as readers, which "
        "is the entire job and was never in the job description. The dead make perfect sense to "
        "him and he makes uncomfortable sense to them."),
    before=(
        "A room with high windows, a stamp, and four hundred men who came in for the warmth and "
        "left with something.\n\n"
        "*Τα βιβλία δεν κρίνουν.* Books do not judge. He put it on the wall in his own hand and "
        "the governor made him take it down twice."),
    adjustment=(
        "He arrived at the issue desk with the stamp in his hand, set it down on nothing, and "
        "picked it back up."),
    forward=(
        "The catalogue finished, and left somewhere it will be read.\n\n"
        "He is aware this is the only ambition he has ever had, and he has stopped apologising "
        "for the size of it."),
    now=(
        "Glittervein, writing down what the dead in the deep workings remember, because nobody "
        "else is bothering and the seam is being cut out from under them.\n\n"
        "The crews treat him as a harmless infestation and let him work, which is the most "
        "comfortable he has been in years."),
),

}
