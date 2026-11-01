# -*- coding: utf-8 -*-
"""Sheet 3 recruits, part one of three: characters 1-8.

Kyle, 31 Oct 2026: "Make them feel human, make everyone a REAL PERSON and not weird sounding
bro." And: "People can be nice, or rude, or scared. Also don't forget to keep in mind people's
nationality! Not everyone has perfect English. Some people took to the new world better than
others! Some stumbled..Some lost people. Some had no one to lose. Some thrived in it."

RULES THIS FILE WORKS UNDER, carried from the batch7 register pass:
  - no em dashes, few flat negations, no trailing ", which ..." qualifiers
  - register assigned PER CHARACTER, not one house voice in 24 mouths
  - the Integration was THREE years ago
  - nothing from Earth physically appears here; Earth is a thing people TALK about

ACCENT AND GRAMMAR LIVE IN THE GREETING, which is the line they actually speak. The narration
stays in plain English. A man whose English is working-level sounds like it when he talks and
is still described with full dignity, which is the difference between writing a person and
writing a costume.
"""

BATCH = {

# 1 ---- DIEGO, Venezuelan, mid 20s. THRIVED. Funny, fast, kind. English good, Spanish-shaped.
"diego_tinker": dict(
    greeting="Ah, you have a broken thing! Give it, give it. No, I am not guessing, I can hear "
             "it. Is the same sound every time, my friend.",
    backstory=(
        "He fixed phones in a kiosk in Maracaibo from the age of fifteen, in a mall where the "
        "power went off twice a day and everybody had learned to keep working in the dark. He "
        "can take a thing apart faster than he can explain why. Of everyone who came through, "
        "he is one of the few who will say plainly that this world has been good to him, and he "
        "says it without apology, because the one he left had already stopped having anything "
        "for him."),
    before=(
        "A folding table, a tray of screws, and a queue.\n\n"
        "Four older sisters, all of whom left the country in different years and different "
        "directions. He was the last one home and the one who stayed to look after their "
        "mother, and he was twenty-two when she died, eight months before the Integration.\n\n"
        "So when it happened, he had nobody to lose. He has said that out loud exactly once, "
        "and then changed the subject to a gearbox."),
    adjustment=(
        "Three weeks, and he spent two of them delighted.\n\n"
        "A goblin handed him a broken pressure valve to see what he would do with it. That is "
        "how a goblin asks a question. He had it working before the goblin finished the "
        "sentence and has been paid in parts ever since."),
    forward=(
        "A workshop with his name over the door, and he will tell you the exact sign he wants, "
        "in two colours, with the lettering slightly crooked because he likes it that way.\n\n"
        "He is twenty-five and has never once been talked out of anything."),
    now=(
        "Wherever there is a pile of broken machinery and somebody willing to let him near it.\n\n"
        "He has a half-built clockwork beetle that has been nearly finished for eleven months. "
        "Everybody who travels with him has been shown it. Nobody has seen it move."),
),

# 2 ---- FREJA, Danish, late 20s. COPING. Warm, direct, near-native English.
"freja_priest": dict(
    greeting="Sit. You're bleeding and you're talking, and you can only do one of those well at "
             "a time. I'll tell you when you can start again.",
    backstory=(
        "A midwife in Aarhus for six years. The job is being the calmest person in a room where "
        "something enormous is happening. She is matter-of-fact to the point of "
        "bluntness and people find it a relief inside about a minute. The Light came to her "
        "easily and she regards that as a tool rather than a calling, and she is careful to say "
        "so, because she has met two people here who got the other idea about themselves and "
        "she did not care for either of them."),
    before=(
        "Night shifts, a bicycle, and a flat with too many plants in it.\n\n"
        "Her parents are alive and were in Aarhus. She has not found them. She has found the "
        "Danish lists at two hubs and neither one is complete, and she has decided to treat "
        "that as good news for as long as she can stand to."),
    adjustment=(
        "Steady, on the outside, from the first week.\n\n"
        "What she had was a working pair of hands and a world full of people who needed them, "
        "and she used that the way you use a railing. She knows exactly what she was doing. She "
        "would do it again and recommends it to nobody."),
    forward=(
        "She wants to deliver a baby here. She has said this to three people and watched all "
        "three of them fail to understand why it matters to her.\n\n"
        "Six years of her life were about the first ninety seconds of somebody else's. She would "
        "like to find out whether that still works in a place with this much dying in it."),
    now=(
        "Walking a circuit of the farms and camps, because the fighting gets a healer and the "
        "births get whoever is nearest.\n\n"
        "She has taught four women to do what she does with their hands when she is not there. "
        "That is the part of the work she is proudest of and the part nobody asks her about."),
),

# 3 ---- SONDRE, Norwegian, late 20s. STUMBLED BADLY. Frightened under a calm surface.
"sondre_stormbringer": dict(
    greeting="If I say get down, get down. Don't ask. The asking is the part that kills people, "
             "I have seen it.",
    backstory=(
        "He taught sailing to teenagers on the Hardangerfjord for four summers and expected to "
        "do a fifth. He is good with weather, good with boats, and he was twenty-four and had "
        "never had anything bad happen to him. Then the sky here started answering when he "
        "spoke to it, and the first time it went wrong it went very wrong, and he has been "
        "frightened of himself ever since. He is polite about it. You can still see it."),
    before=(
        "A dinghy, a whistle, a clipboard, and a season that ended in August.\n\n"
        "His family are in Bergen and he has no idea whether that means anything now. He "
        "describes them in the present tense, deliberately, every time, like a man holding a "
        "door open with his foot."),
    adjustment=(
        "He will say the first year was fine. Anybody who was there will tell you it was not.\n\n"
        "There was an afternoon in the second year when the wind did something he had not asked "
        "for and a barn went over with people inside it. Nobody died. He has not been the same "
        "since and he has never been able to explain why, given that nobody died."),
    forward=(
        "Control. Not power. He has plenty of power and it is the whole problem.\n\n"
        "He has started going out alone to practise where there is nothing to break. The "
        "people who care about him regard that as the worst possible way to handle this, and they "
        "are probably right."),
    now=(
        "The high open ground, where he can see weather coming for an hour before it arrives.\n\n"
        "He sleeps badly. He is first awake every morning and has made the fire before anybody "
        "else is up. He offers this as proof that he is fine."),
),

# 4 ---- BERAT, Turkish, late 20s. THRIVED. Warm, funny, fluent L2 with his own grammar.
"berat_tinker": dict(
    greeting="Open your mouth. No no, I am joking, I am joking! Old habit. Sit down, let me see "
             "the arm.",
    backstory=(
        "A dentist in Izmir, newly qualified, still paying for the chair when the world changed "
        "under him. The job is small careful work inside a space the size of a fist, on a person "
        "who would rather be anywhere else. That turns out to be most of what field medicine "
        "asks for. He is enormously good company and he knows it and he uses it, because a "
        "frightened patient is a patient who moves."),
    before=(
        "A surgery with his name on the door for eleven months, and a loan with thirty years "
        "left on it.\n\n"
        "An enormous family, all of them in Izmir, all of them loud. He says he will find them. "
        "He says it the way you say a thing you have decided to believe, and he says it still, "
        "three years on."),
    adjustment=(
        "Two months, and most of that was the language.\n\n"
        "He arrived with better hands than almost anybody and no idea what to do with the rest "
        "of himself, so he started asking everyone he met what they used to be. He now knows "
        "the former profession of roughly four hundred transplants and will introduce any two "
        "of them who ought to meet."),
    forward=(
        "A proper surgery again, with a door and his name on it, and an apprentice who is "
        "frightened of nothing.\n\n"
        "He is also quietly assembling a list of every transplant with medical training, "
        "because he noticed early that nobody was keeping one, and it is now the only such list "
        "that exists."),
    now=(
        "Wherever the road is busiest, because that is where the broken arms are.\n\n"
        "He still carries the mouth mirror behind his ear. He has used it twice for its actual "
        "purpose and perhaps forty times to see round a corner."),
),

# 5 ---- MATÍAS, Chilean, late 20s. STUMBLED. Withholding, flat, limited English, not rude.
"matias_reaper": dict(
    greeting="I go in front. Is better. You talk to me after, if you want. Now is not the time "
             "for talking.",
    backstory=(
        "He worked the Santiago buses from nineteen, punching tickets on a route he could have "
        "driven blindfolded, in a job his father had before him and thought was beneath him. "
        "What he is good at is standing still in a crowd of strangers for nine hours and "
        "watching all of them at once. He speaks carefully and not much, in an English he is "
        "still building, and people mistake that for stupidity about twice before they stop."),
    before=(
        "A route, a fare box, and the same forty faces every morning.\n\n"
        "His father died in 2019 and they had not spoken in two years. His mother and his "
        "brother were in Santiago. He does not talk about any of this and has told exactly one "
        "person, at night, while on watch."),
    adjustment=(
        "Bad. Very bad, and he will say so plainly if asked directly. Almost nobody "
        "asks.\n\n"
        "He stopped speaking for most of the first year. Not deliberately. He simply ran out of "
        "things that were worth the effort of translating, and the quiet got comfortable, and "
        "then it got difficult to leave."),
    forward=(
        "He is learning to read this world's script, slowly, from a woman in a trade post who "
        "charges him nothing and corrects him constantly.\n\n"
        "He has not told anybody why. The reason is that he wants to write a letter, and he "
        "knows there is nowhere to send it, and he wants to write it anyway."),
    now=(
        "At the front, because that is where you can see everybody.\n\n"
        "He carries the ticket punch and clicks it twice before a fight, every time. Somebody "
        "asked him once whether it was for luck. He said no and did not explain."),
),

# 6 ---- GIORGI, Georgian, mid 30s. STEADY, became more himself here. Warm, limited English.
"giorgi_primalist": dict(
    greeting="You walk too fast for the ground. Slow. The mountain will wait and so will "
             "you, if you listen.",
    backstory=(
        "Twenty years of high summer pasture above Kazbegi, moving sheep up and down a mountain "
        "on a calendar his family never wrote down because nobody needed to. He is physically "
        "enormous and completely unhurried. His English is small and he uses every word of it "
        "deliberately, and what comes out is often better than what a fluent man would have "
        "said, because he has no spare words to hide behind."),
    before=(
        "A dog, a herd, a wooden hut, and six months a year without a road.\n\n"
        "A wife, Nino, and two daughters in the village below, who he came down to every autumn "
        "and who thought the mountain was an eccentricity he would grow out of."),
    adjustment=(
        "Two seasons, and he counts in seasons.\n\n"
        "The land here needed reading and he reads land. What took longer was people: on the "
        "mountain he spoke to nobody for weeks and that was normal, and here being alone is "
        "something others worry about on your behalf. He finds that exhausting and touching at "
        "the same time."),
    forward=(
        "A herd. He is serious and nobody takes him seriously. It irritates him more than he "
        "lets on.\n\n"
        "He has found grazing he says is as good as anything at home, and a tauren who has "
        "begun to argue with him about it. He enjoys this enormously."),
    now=(
        "The high country, where the air is right and the ground tells the truth.\n\n"
        "Every autumn, on roughly the right day, he walks down to lower ground for no reason "
        "anyone can see. He has never explained it. He is bringing the herd down. There is no "
        "herd."),
),

# 7 ---- CAMILLE, French, early 30s. LOST SOMEONE. Rude, funny, excellent English.
"camille_ranger": dict(
    greeting="You want me to come. Fine. But I don't do the thing where we all talk about our "
             "feelings at the fire, yes? Good. We understand each other.",
    backstory=(
        "She was a bike courier in Lyon for nine years and a bicycle mechanic for all of them. The job is "
        "knowing exactly how much space you have and taking all of it. She is "
        "abrasive on purpose, fast, extremely funny when she decides to be, and almost nobody "
        "gets past the first layer. The ones who do find out that she is loyal to a degree she "
        "would deny under torture."),
    before=(
        "A fixed-gear frame she built twice, a radio in one ear, and a city she could cross in "
        "twenty-two minutes.\n\n"
        "Her brother Théo rode for the same company. He was on the Part-Dieu road that morning "
        "and she was not, because she had swapped a shift. She has said this out loud twice and "
        "regretted it both times."),
    adjustment=(
        "She made herself useful immediately and let nobody near her for two years.\n\n"
        "It worked, in the sense that she survived it. She is aware it was not the only option. "
        "She says the other options were for people with more patience than her."),
    forward=(
        "She has been mapping the roads between the camps, every one of them, by hand, by "
        "riding them.\n\n"
        "Ask why and she says somebody should. The real answer is that it is the only thing she "
        "has found here that feels the same as the job did, and the job was the last part of "
        "her life that worked."),
    now=(
        "On the roads, carrying things between places faster than they have any right to arrive.\n\n"
        "She will not take a message she has not read. She found that out the hard way in her "
        "second month and has been insufferable about it ever since."),
),

# 8 ---- ORLANDO, Puerto Rican, early 30s. THRIVED. Talkative, warm, very funny.
"orlando_witchdoctor": dict(
    greeting="Siéntate, siéntate. Okay, English. SIT. You look terrible and I say that with "
             "love, my friend, with love.",
    backstory=(
        "He cut hair in Santurce for eleven years in a shop that was really a front for the "
        "neighbourhood's entire social life, where everybody told him everything because a "
        "barber is a priest with better gossip. He talks constantly and listens harder than "
        "anybody notices. The spirits took to him immediately and he treats them the way he "
        "treated his chair: sit down, tell me what is wrong, I am going to fix it and we are "
        "going to talk the whole time."),
    before=(
        "Two chairs, a radio always on, and a Tuesday regular called Don Beni who came in for "
        "nineteen years and never once needed a haircut.\n\n"
        "His whole family were on the island. He says they are fine. He has a reason he believes "
        "this and he will tell you the reason and the reason is thin, and everybody "
        "lets him have it."),
    adjustment=(
        "He was running a chair inside a month, in a tent, with a borrowed blade.\n\n"
        "It is the single most effective adjustment anybody made, and the reason is simple: he "
        "rebuilt the room. Everything he had on Earth came from having a place where people sat "
        "down and talked, so he made one here before he worried about anything else."),
    forward=(
        "A shop. Properly, with a floor and a mirror.\n\n"
        "He has the blade. He has had three offers of a building. He has turned all three down "
        "and cannot explain why to anybody including himself, and his hands shook on the last "
        "one."),
    now=(
        "Wherever the party stops. That place becomes a shop for as long as they are there.\n\n"
        "He will cut anybody's hair, any race, free, and he has never been refused twice by the "
        "same person."),
),

}
