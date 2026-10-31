# -*- coding: utf-8 -*-
"""Register pass, part three: the lyrical voices, the urgent ones, and the genuinely withholding.

Written under a hard local rule, because the measurement said the house voice was built out of
four habits: no flat negations, no trailing ", which ..." qualifiers, no "has stopped", no
"never once". Withholding is achieved by omission and short sentences instead of by saying what
a person does not do. That is the distinction the first draft missed - it kept describing people
by their absences, in the same construction, forty-three times.

Also fixes the "[job] in [City] for N years" opener that crept back into Kesten in part two.
"""

BATCH = {

"kesten_the_catalogued": dict(
    backstory=(
        "Tallinn, the city archive, twenty-six years among acid-free boxes. Then a serial "
        "number in a Scourge ledger. Then neither. What came back has the archivist's habits "
        "and little of his warmth, and he is the first to say so. He catalogues. It is the only "
        "continuity he has and he defends it the way other people defend a family."),
),

# ---- LYRICAL, SPARINGLY ----------------------------------------------------------------------
"mateo_starcaller": dict(
    greeting="Look up. Go on. Three years and I still have to make people look up.",
    backstory=(
        "Seventeen years of keeping the lights on at a mountaintop observatory above the Elqui "
        "valley. "
        "Technician, not astronomer, and he will correct you on that immediately and then talk "
        "for an hour anyway. Up there the sky is so clear it stops being scenery and becomes a "
        "place. He arrived on a world with the wrong stars in it and spent his first winter "
        "learning them from scratch, alone, on his back in the grass, happier than he had been "
        "in a decade."),
    before=(
        "Cold domes, cable runs, and the four hours before dawn when the astronomers slept and "
        "the mountain belonged to him.\n\n"
        "He had a wife in La Serena and two girls who thought the mountain was boring. He "
        "agreed with them. He went anyway, every month, for seventeen years."),
    adjustment=(
        "He found the sky first and everything else second, in that order, and for a long while "
        "that worked.\n\n"
        "The reckoning came in the second winter, when he had finished naming the constellations "
        "and had to go back down the mountain and be a person."),
    forward=(
        "A map of this sky, drawn properly, by somebody who understands that a sky is also a "
        "calendar and a clock and a promise. He is eleven months in.\n\n"
        "He walks to the Tanaris hub twice a year with two names folded in his pocket, reads the "
        "whole list, and walks back. He talks about the stars on the way out and says very "
        "little on the way home."),
    now=(
        "Tanaris, at the dark edge of the desert, where the air is dry and the nights go on "
        "forever.\n\n"
        "The goblins think he is harmless and let him climb their towers. From the top of one of "
        "them he can see most of the sky at once, and he has begun to suspect it is the finest "
        "observing site on this world."),
),

"carolina_shaman": dict(
    greeting="Everything here has a current. Rivers, weather, people. Learn to feel it and you "
             "will stop fighting things that were already carrying you.",
    backstory=(
        "Twelve years a river pilot on the Amazon, which means twelve years of reading a water "
        "that redraws itself every season. A channel that was deep in March will ground you in "
        "September. She learned to feel the bottom through the hull. On this world the spirits "
        "of water hold a conversation with her that she describes as the same conversation, in "
        "an accent she had to work at."),
    before=(
        "A boat, a cargo, and a river two kilometres wide that her grandfather had read before "
        "her."),
    adjustment=(
        "Three gentle years, and she is clear-eyed about why: she arrived already believing the "
        "water was somebody.\n\n"
        "Half the transplants she meets had to dismantle a whole worldview to get here. She "
        "walked in and recognised the place."),
    forward=(
        "She wants a river of her own on this world. A long one, with seasons, that she can "
        "learn for twenty years and still be surprised by.\n\n"
        "She has been told there is one in Feralas. She has been told a great many things about "
        "Feralas."),
    now=(
        "The Wetlands, where the water moves through the marsh in channels that shift with the "
        "rains and the local boatmen lose craft every spring.\n\n"
        "She has been teaching two of them to read a bottom by feel. One of them is getting "
        "it, and watching that happen has done more for her than three years of being "
        "useful."),
),

"anjali_druid": dict(
    greeting="Gently. Gently, now. Whatever is wrong here, shouting at it will make it worse. I "
             "have thirty years of evidence.",
    backstory=(
        "Thirty-one years teaching botany in Pune. Three decades of patience with slow things, "
        "and with students who wanted results by Friday. A plant will tell you "
        "what it needs if you are willing to wait several seasons for the sentence to finish. "
        "Druidry asked her for the same patience and gave her, for the first time in her life, "
        "the ability to answer back."),
    before=(
        "A department, a herbarium, and four decades of pressed specimens she labelled in her "
        "own hand.\n\n"
        "Her husband retired in 2018 and spent two years teaching himself to cook. She had one "
        "year of that. She describes the year as the best of her marriage and she says it in a "
        "voice that invites no follow-up."),
    adjustment=(
        "Slowly, which suited her. She treated the whole first year as a field season and kept "
        "a notebook in the way she had kept forty of them.\n\n"
        "The notebook is now the only systematic record of Ashenvale's understory that exists "
        "in any language, and she regards it as a draft."),
    forward=(
        "She would like to be read in two hundred years. She says this cheerfully and she is "
        "entirely serious.\n\n"
        "Which means a copy somewhere safe, in a language that will survive, and a student who "
        "cares. She has the first. She is working on the third."),
    now=(
        "Ashenvale, where the forest is sick in a patterned way and the night elves know it in "
        "their bones without having ever written it down.\n\n"
        "She is writing it down. The Sentinels were suspicious for two years and now bring her "
        "specimens."),
),

"bakyt_hunter": dict(
    greeting="Walk behind me and step where I step. The ground lies. It lied at home too and I "
             "have forty years of practice.",
    backstory=(
        "Forty years of high pasture in the Tian Shan, moving a herd up in spring and down in "
        "autumn along a route his family has walked for six generations. He reads weather in a "
        "sky other people call clear and finds water where there is apparently none. The eagle "
        "he hunts with here is not the eagle he hunted with there, and he will tell you that "
        "the difference is less than you would think, and that he grieved the first one "
        "properly."),
    before=(
        "A yurt, a herd, a route, and a father who taught him the route before he could "
        "ride.\n\n"
        "Three sons, all of whom went to Bishkek for work. He understood why. It was still the "
        "end of six generations and both of those things sat in him at once for twenty years."),
    adjustment=(
        "He had the easiest first year of anyone and the quietest grief underneath it.\n\n"
        "Nomads adjust. That is the whole profession. What he had to absorb was that this world "
        "has pasture his family will never walk, and he put a year of long evenings into "
        "getting comfortable with that."),
    forward=(
        "A route of his own. Mapped, seasonal, defensible, and walked often enough that somebody "
        "else could follow it after him.\n\n"
        "He has two legs of it. He is fifty-eight and he has started to think about who gets it, "
        "and the thought has made him friendlier to strangers than he used to be."),
    now=(
        "The high country above Stonetalon, grass and wind and a long way between people.\n\n"
        "The tauren there move herds on a cycle he recognised in about a week. They have begun "
        "asking his opinion on the cycle, which is the only honour he has ever visibly cared "
        "about."),
),

# ---- URGENT / PRESENT TENSE ------------------------------------------------------------------
"owen_cultist": dict(
    greeting="You hear that? No. Of course you do not. Stay close anyway.",
    backstory=(
        "Eight years a long-haul driver out of Cardiff, alone in a cab through the small hours, "
        "and the radio for company. He talked to himself for a living. Then he got here and "
        "something in the dark answered him, and the terrible part is that he was glad. He is "
        "aware of how that sounds. He says it anyway, early, so nobody can accuse him of hiding "
        "it later."),
    before=(
        "Motorways, laybys, and a flat in Cardiff he barely lived in.\n\n"
        "His mother was in a home in Barry and he visited every second Sunday for six years. "
        "She had forgotten who he was by the end. He says that makes this easier and the people "
        "who hear it understand that it does not."),
    adjustment=(
        "He fell straight in. There was no moment of resistance and he has examined that "
        "honestly and found it worse than the falling.\n\n"
        "What he will say, when pressed: eight years of talking to nobody is good preparation "
        "for talking to something."),
    forward=(
        "He wants to know what it wants. Properly. He has been given hints for three years and "
        "he is tired of hints.\n\n"
        "He has also begun writing down what he hears, on the grounds that if he ever goes "
        "wrong, somebody will want a record of the route."),
    now=(
        "The Blasted Lands, where the air is thin with something and most people get headaches "
        "and leave.\n\n"
        "He gets sentences. He stays."),
),

"ziad_felsworn": dict(
    greeting="Keep moving. I am serious. Everything bad that happened to me happened while I "
             "was standing still.",
    backstory=(
        "Six years a paramedic in Beirut, a city that taught him triage as a reflex and the "
        "bitter arithmetic of a van with four spaces. He made those choices for six years and "
        "every one of them was correct and every one of them cost him something. Fel magic put "
        "a terrible, obvious power in reach and he took it, and his reasoning is the same "
        "reasoning that let him choose the fourth patient."),
    before=(
        "A van, a radio, and a city where the road you took mattered more than the medicine you "
        "carried."),
    adjustment=(
        "Twelve months of saying yes to things he should have slept on.\n\n"
        "He will own all of it. What he refuses is the suggestion that it was weakness. He was "
        "offered the ability to save more people and he took it, and three years on he is still "
        "doing the arithmetic in public, out loud, for anyone who wants to argue."),
    forward=(
        "Out. He wants out of it, and he has looked into what that costs, and the figure is the "
        "reason he is still in.\n\n"
        "In the meantime he works. The people he pulls out of the Scar are alive either way, "
        "and that is the whole of his defence and he knows how thin it is."),
    now=(
        "Desolace, around the Scar, where the gnolls and the satyr trade the ground back and "
        "forth and the casualties are constant.\n\n"
        "He is first on scene. Always. The centaur have a word for him and he has asked three "
        "times what it means and been told three different things."),
),

"alonso_pyromancer": dict(
    greeting="Give me room. More than that. Honestly, more than that, I have burnt three "
             "people's eyebrows off being polite about it.",
    backstory=(
        "Twenty-two years running a kiln in Talavera de la Reina. Glaze, temperature, timing: a "
        "trade where the whole year's work turns on four hours of heat going exactly right. He "
        "feels a fire the way other people feel a draught. On this world fire answers him and "
        "the first thing he did with that was make a cup, badly, and he keeps it on a shelf."),
    before=(
        "A kiln, a wheel, and a workshop his grandfather fired for forty years before him."),
    adjustment=(
        "Ten weeks. He treated it as a new kiln with an unfamiliar character and learned it the "
        "way he had learned four others.\n\n"
        "His wife in Talavera was at the market when it happened. He has said the word market "
        "perhaps twice in three years and each time changed the subject so quickly that whoever "
        "he was talking to apologised."),
    forward=(
        "A kiln. His own, built right, with somebody to teach.\n\n"
        "He has the clay. He has the site. He has been putting it off for two years and the "
        "reason he gives is money, and the reason is not money."),
    now=(
        "The Searing Gorge. It is the hottest place anybody has told him about, so it is the only "
        "place he wants to be.\n\n"
        "The Thorium Brotherhood use him and underpay him. He has a pot going in a crack in the "
        "rock face that nobody is supposed to know about."),
),

"marisol_priest": dict(
    greeting="Talk to me while I work. Anything. I do better with a voice in the room and so do "
             "you.",
    backstory=(
        "Nine years in a Bogotá emergency department, three of them on nights, all of them "
        "short-staffed. She learned to keep a frightened person talking while her hands did "
        "something they would rather not watch. The Light moves through her easily and she "
        "treats it as one more instrument on a tray. The habit of narrating came with her and "
        "half the party finds it steadying and half find it maddening."),
    before=(
        "Trolleys in a corridor, a triage board, and a city that produced a steady supply.\n\n"
        "Her brother was a motorcycle courier in the same city. She patched him up twice. The "
        "second time she shouted at him in the corridor for ten minutes and she would give "
        "anything to have that back."),
    adjustment=(
        "Eighteen months of working flat out, and she will tell you honestly that she did it to "
        "stay out of her own head.\n\n"
        "It worked. She would do it again. She is also aware of what it is."),
    forward=(
        "A ward. Four beds, a roof, and a place where somebody injured can lie down for a week "
        "instead of being patched up in a field.\n\n"
        "She has found a building in Theramore and she has been negotiating for eleven months "
        "with a quartermaster who keeps asking whose authority she is under."),
    now=(
        "Dustwallow, out of Theramore, working the swamp road where the raptors take travellers "
        "and the garrison gets to them slowly.\n\n"
        "She reaches them faster. The garrison has noticed and the quartermaster, apparently, "
        "has not."),
),

# ---- WITHHOLDING, BY OMISSION ----------------------------------------------------------------
"pasang_primalist": dict(
    greeting="Slowly. The altitude here is nothing. Your pace is still wrong.",
    backstory=(
        "Nineteen expeditions above eight thousand metres as a Solukhumbu climbing guide. He "
        "carried loads for people who went home famous. He has seen what high ground does to a "
        "body and to a personality, and he judges strangers by how they behave on day four. "
        "The spirits of stone and cold hold a conversation with him that he regards as a work "
        "arrangement rather than a mystery."),
    before=(
        "A load, a rope, and nineteen seasons of other people's ambition.\n\n"
        "Four of his cousins did the same work. Two of them died on it. He has the names and he "
        "keeps them to himself."),
    adjustment=(
        "He said very little for the first year. He worked, ate, slept, and watched.\n\n"
        "In the second year he began to speak and people discovered he had formed complete "
        "opinions about all of them."),
    forward=(
        "A summit nobody has stood on. He has heard there is one in Winterspring and he has "
        "heard a great deal of talk from people who have been halfway.\n\n"
        "He would like to go alone. He is aware this is exactly what he spent nineteen years "
        "telling clients to stop wanting."),
    now=(
        "Alterac's high valleys. Thin air, bad weather, and routes that were never written "
        "down.\n\n"
        "He has written four of them down. He has shown them to one person."),
),

"driss_shaman": dict(
    greeting="Water first. Then we talk about whatever you came here to say.",
    backstory=(
        "Twenty-eight years guiding caravans out of Zagora, across ground where a wrong turn "
        "costs a camel and a second wrong turn costs a man. He reads sand the way a sailor "
        "reads water. The desert spirits here required an introduction and then settled into "
        "something he finds entirely familiar: a long relationship with a landscape that would "
        "kill him on a technicality."),
    before=(
        "Camels, tourists, and a route his father and his father's father had walked.\n\n"
        "He raised four children on it. Three are grown. The fourth was nine."),
    adjustment=(
        "He asked the land for permission in his own language and something answered. He "
        "mentions this rarely.\n\n"
        "The rest of the adjustment was practical: new stars, new seasons, and a year of "
        "getting the distances right."),
    forward=(
        "A route across Tanaris that a caravan can use in summer. There is a way through and he "
        "has most of it.\n\n"
        "Finishing it means four more seasons of walking and he has the seasons."),
    now=(
        "Tanaris, out of Gadgetzan, where the goblins pay for a man who gets cargo across "
        "intact.\n\n"
        "He gets it across. He has refused two contracts over the water allowance and both "
        "parties came back with a better one."),
),

"kiet_rogue": dict(
    greeting="Keep your voice down. Half of what I know, I learned from people who thought "
             "nobody was listening.",
    backstory=(
        "Eleven years a Bangkok motorcycle courier, which means eleven years of being invisible "
        "in traffic and arriving before anyone expected. He went into offices, kitchens, and "
        "back rooms all day long and nobody ever looked at him twice. He kept a great deal of "
        "what he overheard. Here the skill transfers whole and he has been careful to let very "
        "few people work out that it is a skill."),
    before=(
        "A bike, a bag, and a city where the fastest route changed hourly.\n\n"
        "He lived with his grandmother in Khlong Toei. She was eighty-four and she could not "
        "manage the stairs."),
    adjustment=(
        "Six weeks. He had a route in Orgrimmar before he had a bed.\n\n"
        "He says the hard part was the quiet. Eleven years of engine noise and then a world "
        "where he can hear people breathing two rooms away."),
    forward=(
        "A standing arrangement with somebody who pays for information and asks for it "
        "politely. He has had three offers and all three were from people he would rather owe "
        "nothing to.\n\n"
        "He would also like to stop flinching at silence. Three years in, it is slower going "
        "than the rest of it."),
    now=(
        "Orgrimmar, the Drag, where everybody talks and nobody watches the person carrying "
        "something.\n\n"
        "He carries something. He has mapped the whole city by how long each route takes at "
        "each hour, which is the first thing he does anywhere, and he has stopped being "
        "surprised that nobody else does it."),
),

"sophia_mage": dict(
    greeting="Let me think for a moment. You will get a better answer and I will get less "
             "shouting.",
    backstory=(
        "Fourteen years a translator at the European Parliament. Simultaneous, four languages: "
        "you hold a sentence in one tongue while it finishes in another, and you get the "
        "register right as well as the words. Arcane work asks for precisely "
        "that kind of attention held precisely that long. She was better prepared for this than "
        "almost anybody and it took her two years to believe it."),
    before=(
        "A booth, a headset, and a career of being the invisible reason a room understood "
        "itself.\n\n"
        "She is from Thessaloniki and had been in Brussels for eleven years. Her parents were "
        "at home. Greece and Belgium came down on different sides of a mountain range and she "
        "has worked out the implications more carefully than she has admitted to anyone."),
    adjustment=(
        "Two quiet years of being competent and assuming she was not.\n\n"
        "What broke it was a goblin who asked her to interpret a contract dispute and then paid "
        "her properly and then came back."),
    forward=(
        "A grammar of this world's arcane. She is convinced the thing has a syntax and that "
        "every mage here is speaking it by ear.\n\n"
        "Forty pages in. She has shown it to two people. One of them laughed and the other asked "
        "for a copy."),
    now=(
        "Theramore, where four languages and two factions arrive on the same dock and nobody is "
        "being paid to make that work.\n\n"
        "She makes it work, for money, and she has been in the room for three negotiations that "
        "would have gone badly without her."),
),

"marco_paladin": dict(
    greeting="I will stand here. You do what you came to do.",
    backstory=(
        "Thirty-one years a Naples locksmith, and for twenty of those the man the neighbourhood "
        "sent for when something was wrong and the authorities were worse than the problem. He "
        "settled disputes because somebody had to and because he was the only one everybody "
        "owed a favour. The Light found him already doing the work and he regards the whole "
        "business as a formality that arrived late."),
    before=(
        "A shop, a quarter, and a reputation he spent thirty years being careful with.\n\n"
        "A wife, two daughters, and a grandson born in the February. He had held him four times."),
    adjustment=(
        "He looked for people to be useful to and found them in a fortnight.\n\n"
        "Everything else he put off, and he is still putting it off, and at sixty-three he has "
        "decided that is a legitimate way to handle it."),
    forward=(
        "A quarter again. A few streets where people know to come to him.\n\n"
        "He has about half of one in Southshore. He is counting."),
    now=(
        "Southshore, in the lanes behind the inn, where the town has quietly worked out who to "
        "fetch.\n\n"
        "He fixes locks. He also fixes other things and nobody has ever asked him to."),
),

"amber_druid": dict(
    greeting="Give it a season. Everything here gives you an answer if you let it finish.",
    backstory=(
        "Twenty-three years restoring wetland on the Oregon coast. It is a profession of doing "
        "something slow and correct and having nothing to show anybody for a decade. She planted sedge and waited. She pulled invasive grass for nine years in one "
        "basin. Druidry gave her the ability to make a thing grow in an afternoon, and the first "
        "year she used it constantly and the second year she mostly stopped."),
    before=(
        "Waders, a seed bank, and a grant cycle that funded three years of a thirty-year "
        "job.\n\n"
        "She was divorced in 2016 and had made a reasonable peace with living alone. She says "
        "that peace is the single most useful thing she brought with her."),
    adjustment=(
        "Eight months, and she describes them as the easiest of her life, and she notices that "
        "this makes her poor company among transplants.\n\n"
        "Her whole career had been patience without authority. Here she has both."),
    forward=(
        "One basin, fully recovered, by her own hand, start to finish. She never got one on "
        "Earth. Three years in she is further along than twenty-three years of grant cycles "
        "took her.\n\n"
        "She is also trying to work out how to teach restraint to people who can make a tree in "
        "an afternoon. So far she has one student and a lot of opinions."),
    now=(
        "Feralas, in the wet country, where the growth is so fast that a mistake corrects itself "
        "in a season and a bad habit never gets caught.\n\n"
        "She works the rot where the corruption has reached in. Slowly. The night elves have "
        "watched her for two years and she is aware that watching is how they decide."),
),

"ratih_ranger": dict(
    greeting="Walk quieter. I can hear you from the other end of the valley and so can "
             "everything else.",
    backstory=(
        "Fifteen years a Sumatran forest ranger, which meant long patrols, poachers, and a "
        "government that funded the uniforms and little else. She learned to read a forest for "
        "the one wrong thing in it: a snare, a path, a silence where there should be birds. "
        "Here the forests are stranger and the method is identical, and she has found the one "
        "wrong thing four times in three years."),
    before=(
        "A patrol route, a rifle she rarely carried, and the particular loneliness of being the "
        "only person in the province who cared.\n\n"
        "She has a sister in Medan and a nephew she had promised to visit."),
    adjustment=(
        "She went to work. Within a month she had a patrol route of her own invention and "
        "nobody's permission.\n\n"
        "The second year was harder, and it was harder for a reason she finds absurd: out here "
        "people thank her."),
    forward=(
        "She wants the Sentinels to take her on properly. Rostered, briefed, part of a line "
        "instead of a woman in the woods.\n\n"
        "She has asked twice. The answers were polite. She is going to ask a third time and she "
        "has decided what she will say if the answer is the same."),
    now=(
        "Northern Ashenvale, walking a route she drew herself, looking for the one wrong "
        "thing.\n\n"
        "She has reported every find to the Sentinels and signed none of the reports."),
),

}
