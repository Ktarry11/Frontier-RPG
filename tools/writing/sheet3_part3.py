# -*- coding: utf-8 -*-
"""Sheet 3 recruits, part three of three: characters 17-24.

The older end of the intake, and three of the five Middle Eastern men sit here, so the English
is varied deliberately across them rather than given one shared "accent". Nizar learned his
from books and is more formal than any native speaker; Yusuf is warm and fluent with his own
grammar; Bashir is clipped and exact; Khalid went to an English-language school and is simply
fluent. Treating those four as one voice would have been the costume problem again.

Same rules as parts one and two: accent lives in the spoken greeting and never the narration,
no em dashes, no ", which ..." closers, the Integration was THREE years ago.
"""

BATCH = {

# 17 ---- GIANLUCA, Italian, late 30s. STEADY. Wry, warm, talks constantly.
"gianluca_guardian": dict(
    greeting="You want to go in there? Fine, fine. But we go slow, and you let me go first, and "
             "afterwards you buy me something hot. This is the arrangement.",
    backstory=(
        "He ran a bar in Bologna that his parents ran before him, opening at six for the people "
        "going to work and closing late for the people avoiding going home. Thirty years of "
        "standing behind a counter reading a room. He talks without stopping, he remembers what "
        "everybody drinks, and he has defused more fights with a joke than most soldiers have "
        "with a weapon. Behind the shield he is immovable and nobody expected that from the man "
        "who will not shut up."),
    before=(
        "A counter, a machine he rebuilt himself twice, and the six o'clock crowd who never "
        "ordered because he already knew.\n\n"
        "A wife, Ornella, who ran the kitchen and the money and most of him. Two sons, both "
        "grown and both in Milan, who rang on Sundays."),
    adjustment=(
        "He built a bar. Not a real one. A spot by a fire where he stood and people came to "
        "him, and he turned that into a job inside four months.\n\n"
        "He has said that he did not know what else to do with himself, and that the thing he "
        "actually missed was not the bar, it was being the person everyone passes in the "
        "morning."),
    forward=(
        "A real one. A room, a door, a machine. He describes it constantly and in enormous "
        "detail and has done nothing concrete about it in three years.\n\n"
        "He walks to the hubs every few months. He reads the Bologna list and the Milan list, "
        "in that order, and he reads the Milan list twice."),
    now=(
        "At the front of the party with a shield, where he keeps up a running commentary that "
        "the enemy finds as unsettling as everyone else does.\n\n"
        "The brass tamper hangs at his belt. He has no coffee and no machine. He has been "
        "offered a dozen local substitutes and has tried all of them and rated every single one "
        "out of ten, unkindly."),
),

# 18 ---- ELIAS, Dominican, early 30s. STEADY, quietly thriving. Serene, bilingual, kind.
"elias_suncleric": dict(
    greeting="Take your time. I've got this side. Nothing's getting past me while you sort "
             "yourself out, hermano.",
    backstory=(
        "A motorcycle mechanic in Santo Domingo who went to church on Sundays because his "
        "grandmother expected it and stayed in the habit after she stopped being able to ask. "
        "He is the calmest person in most rooms. The Light arrived in his second year, during "
        "nothing in particular, while he was fixing a cart, and he has never once presented it "
        "as a sign. He treats it as a tool that showed up and he has been learning its tolerances "
        "ever since."),
    before=(
        "A workshop with a tin roof, four bikes in pieces at any time, and a radio he and his "
        "cousin argued over.\n\n"
        "An enormous family in the capital and a girlfriend, Yamila, who he had been seeing for "
        "two years and had not told his mother about, for reasons that seemed important at the "
        "time."),
    adjustment=(
        "Slow and undramatic. He fixed things for about eighteen months and let everything else "
        "wait.\n\n"
        "He will tell you he coped well and the people around him agree, and he has also said, "
        "once, that he thinks he simply has not got to it yet, and that it is still sitting "
        "somewhere waiting for him."),
    forward=(
        "He wants to build something that will outlast him, and he means a building, not a "
        "legacy.\n\n"
        "He has drawn up a shelter for a crossing where travellers get caught out by weather. "
        "Four walls and a roof and a stove. He has shown the drawing to nobody, because he knows "
        "the first question will be who it is for and he does not have an answer that will "
        "satisfy anybody."),
    now=(
        "At the front, taking what is aimed at other people with an air of mild apology.\n\n"
        "The inspection mirror lives in his gauntlet. He uses it to see round corners and, more "
        "often, to check on people behind him without turning round."),
),

# 19 ---- RUI, Portuguese, mid 30s. STUMBLED HARD. Frightened, gentle, ashamed.
"rui_cultist": dict(
    greeting="Please don't ask me what it is. I will tell you what it does and that has to be "
             "enough, because the rest I cannot say out loud.",
    backstory=(
        "He crewed a sardine boat out of Peniche from the age of sixteen, in a family trade that "
        "was collapsing under him the whole time he was in it. He is soft-spoken, apologetic and "
        "almost unbearably gentle, and he carries something that frightens him badly. He took it "
        "in his first year when the alternative was dying, and he has been paying for it since, "
        "and he has never once tried to make it sound like a good decision."),
    before=(
        "Nights out and mornings in, a hold full of fish, and a co-operative that had gone from "
        "forty boats to nine in his working life.\n\n"
        "His mother and his two sisters are in Peniche and he was the one who sent money. He "
        "thinks about that more than he thinks about them, and he knows that is a strange thing "
        "to be ashamed of, and he is ashamed of it anyway."),
    adjustment=(
        "Catastrophic. He was alone, he was hurt, and something offered.\n\n"
        "He said yes. He has not defended that choice to anybody in three years. When people "
        "assume the obvious about him he lets them, because arguing would mean explaining, and "
        "explaining is the part he cannot do."),
    forward=(
        "Out. Quietly, without anybody making a fuss about it.\n\n"
        "He has asked three priests and two shamans, carefully and in general terms, and nobody "
        "has given him an answer he believes. He keeps asking. It is the only thing he is "
        "stubborn about."),
    now=(
        "Behind the party, where he is extremely effective and visibly uncomfortable about it.\n\n"
        "He sleeps nearest the fire. He has never said why and nobody has worked out that it is "
        "not the cold."),
),

# 20 ---- NIZAR, Syrian, early 40s. LOST SOMEONE. Formal, gracious, book-learned English.
"nizar_chronomancer": dict(
    greeting="A moment, if you would permit me. I should like to understand the sequence before "
             "we add ourselves to it.",
    backstory=(
        "He taught secondary-school mathematics in Homs for eleven years, then in Beirut for "
        "six, then in a language he was still learning for four more. He has rebuilt his life "
        "three times and this is simply the fourth, a fact he states without self-pity and which "
        "makes most transplants go quiet. His English is careful and faintly old-fashioned, "
        "learned from books and the BBC, and he is more precise in it than almost anybody born "
        "to it."),
    before=(
        "A blackboard, forty students, and the particular patience of a man explaining the same "
        "proof for the ninth time without letting it show.\n\n"
        "His wife Lamia died in 2016, before any of the rest of it. His daughter Hala was "
        "twenty-two and studying in Amman and they spoke every single day, and he can tell you "
        "the time of the last call."),
    adjustment=(
        "Better than almost anyone, because he had done it before and knew the shape of it.\n\n"
        "He has said that the first time you lose everything it destroys you, the second time it "
        "is merely very hard, and the third time you find you have a method. He does not offer "
        "this as wisdom. He offers it as information, to people who look like they need it."),
    forward=(
        "Hala. He is systematic about it in a way that is painful to watch: hub by hub, list by "
        "list, in a notebook, with dates.\n\n"
        "He has also started teaching again, four children in a trade post, mathematics, in the "
        "evenings, for nothing. He says it is to keep his hand in."),
    now=(
        "At the back, holding the order of things together while the front rank does its work.\n\n"
        "The broken watch runs backwards on its chain. He has never had it mended. He winds it "
        "every morning regardless and has not explained that to anybody."),
),

# 21 ---- YUSUF, Iraqi, early 40s. STEADY. Warm, funny, enormously kind. Fluent L2.
"yusuf_venomancer": dict(
    greeting="Sit, sit. You are not dying, I can see this from here. But you will sit anyway, "
             "because I am older than you and this is how it works.",
    backstory=(
        "A pharmacist in Basra for nineteen years, in a shop where half the job was medicine and "
        "the other half was listening to people with no money for a doctor. He knows doses, "
        "he knows poisons, and he knows exactly how much of the truth a frightened person can "
        "take at once. He is enormously warm and completely unsentimental, and those two things "
        "together are rarer than either."),
    before=(
        "A counter, a wall of drawers, and a queue that was also a social occasion.\n\n"
        "A wife, Suhad, three sons and a daughter, and a house with too many people in it and "
        "a roof they sat on in the summer. He talks about them easily and often, in the present "
        "tense, and has never once been heard to speculate about where they are."),
    adjustment=(
        "Unhurried. He found the work and did it, the way he had found work in two other "
        "countries already.\n\n"
        "He is one of the very few here who has said plainly that he expects to see his family "
        "again, and he says it so calmly that people believe him for as long as he is in the "
        "room."),
    forward=(
        "A dispensary. Shelves, drawers, labels, and somebody he has trained to run it when he "
        "is out.\n\n"
        "He is also quietly teaching two people to read the labels he writes, because he has "
        "noticed that a dispensary nobody else can read is a dispensary that dies with him."),
    now=(
        "At the back with a bandolier of vials, dosing by eye and never once by guess.\n\n"
        "The brass counting tray is strapped flat on his back. He uses it constantly. He is the "
        "only person in the party whose numbers are always right."),
),

# 22 ---- BASHIR, Palestinian, early 40s. LOST SOMEONE. Severe, exact, not cruel.
"bashir_witchhunter": dict(
    greeting="I will tell you what I find. All of it, including the parts you would rather I "
             "kept to myself. If that is a problem, say so now.",
    backstory=(
        "A stonemason in Nablus for twenty-two years, in a trade of taking something apart "
        "correctly before you rebuild it. He is severe, literal and entirely without small talk, "
        "and people read that as coldness for about a week. He hunts corrupted things the way he "
        "cut stone: slowly, along the grain, with no interest at all in how long it takes."),
    before=(
        "A yard, a chisel, and walls that his grandfather had worked on before him.\n\n"
        "A daughter, Rana, nineteen, who had just started at the university in Birzeit and had "
        "told him the week before that she intended to study engineering rather than anything he "
        "had suggested. He had been pleased and had not said so yet."),
    adjustment=(
        "He went looking immediately and did not stop for eleven months.\n\n"
        "He walked to four hubs in that time, on foot, through country that kills people. He "
        "found nothing. He came back, said nothing about it to anybody, and started doing the "
        "work he does now."),
    forward=(
        "He has never said. The closest anybody has got is that he keeps a list of places he has "
        "not searched, and the list is getting shorter, and he has begun to look at what is at "
        "the end of it.\n\n"
        "He has told one person that he intends to be useful until then. That is the whole of "
        "the plan."),
    now=(
        "Out at the edge of the corruption with a lantern, where the work is slow and almost "
        "nobody volunteers.\n\n"
        "He snaps the chalk line before he goes in anywhere. He has done it at every doorway for "
        "three years and he does it without appearing to notice he is doing it."),
),

# 23 ---- OSVALDO, Cuban, late 30s. STUMBLED. Closed, blunt, dry. Limited English.
"osvaldo_warlock": dict(
    greeting="You want fire, I give you fire. You want conversation, is the wrong man. Ask the "
             "Italian, he never stops.",
    backstory=(
        "He played trumpet in a Havana hotel band for sixteen years, six nights a week, for "
        "tourists who talked through all of it. He is enormously talented at a thing nobody here "
        "has any use for, and that is most of what is wrong with him. He speaks little English "
        "and has made no particular effort to improve it, and he is blunt to the point of rude "
        "and has never once been unkind about anything that mattered."),
    before=(
        "A bandstand, a residency, and a brother on piano who was better than him and knew it.\n\n"
        "His mother was ninety-one and lived three streets from the hotel. He went every "
        "afternoon before the set. He has said one sentence about her in three years."),
    adjustment=(
        "He stopped playing. There was nothing to play and nobody to play with, and he put it "
        "down, and it stayed down.\n\n"
        "The fire came after that, and he will tell you the order matters. He was already empty "
        "when he went looking, and he thinks that is the only reason it took."),
    forward=(
        "Nothing he will admit to.\n\n"
        "What is observable: he has twice stayed up all night with people who were in a bad way, "
        "saying almost nothing, just sitting there. Both of them have told somebody about it. "
        "He has denied it both times."),
    now=(
        "At the back, doing the loud part, with a flat expression that unsettles people until "
        "they get used to it.\n\n"
        "The mouthpiece hangs at his throat. He has never been seen to use it. Somebody heard "
        "him humming once, badly, and had the sense to say nothing."),
),

# 24 ---- KHALID, Emirati, mid 30s. THRIVED. Dry, funny, fluent, quietly content.
"khalid_hunter": dict(
    greeting="Walk where I walk and we will have a very boring day. That is the aim. Boring is "
             "the aim, I cannot stress this enough.",
    backstory=(
        "He kept falcons outside Al Ain, in a family that had done it for longer than anybody "
        "had written down, and he worked in logistics at the airport to pay for it. The hunting "
        "is the part of his old life that transferred whole: the waiting, the reading of ground, "
        "and the particular relationship with an animal that is choosing to come back to you. He "
        "is dry, extremely funny once you know him, and more at home here than he ever admits "
        "in company."),
    before=(
        "A mews, a glove, and a bird called Hurra who was eleven years old and who he had flown "
        "since she was a fledgling.\n\n"
        "A large family, all nearby, all of whom thought the falcons were an expensive "
        "eccentricity and all of whom came out to watch anyway."),
    adjustment=(
        "Three months, and he has the grace to find it funny.\n\n"
        "He came through into open country with weather and birds in it and no airport, and he "
        "says that if he is honest the first year was the best he had had in a decade. He says "
        "this quietly and only to people he has decided will not misunderstand it."),
    forward=(
        "A bird. Properly trained, properly flown, not a summoned thing.\n\n"
        "He has been working on a nest of something enormous in the hills for two seasons, "
        "patiently, badly, and it has twice taken food from his hand and twice tried to remove "
        "it."),
    now=(
        "Out ahead of the party, usually invisible, always exactly where he said he would be.\n\n"
        "The falconer's hood still hangs at his belt. It is sized for a bird that has been dead "
        "or alive for three years without him knowing which, and he will not be getting another "
        "one that size."),
),

}
