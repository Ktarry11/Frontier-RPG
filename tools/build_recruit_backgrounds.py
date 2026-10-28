#!/usr/bin/env python3
"""Four background sections for every recruit. Idempotent.

  PYTHONPATH=. python3 tools/build_recruit_backgrounds.py

Kyle, 2026-10-28: "Can we expand each characters backstory and current story perhaps? We have the tabs
for them."

The tabs already existed and were empty - BackgroundScreen has read Character.background_sections since
it was built, with "now" quietly falling back to the flat one-paragraph backstory so nothing looked
broken. All 25 recruits had zero authored sections. This writes them.

THE REFRAIN IS THE SPINE. Every original backstory ends the same way: "He is not adapting." "She is not
adapting." That is not a tic, it is the whole character design - these are people whose Earth skill
transferred so exactly that becoming someone new was never required of them. So ADJUSTMENT is the tab
that has to earn it: not "how they coped", but what they refused to stop being, and what that cost.
A few of them genuinely struggled, and those are the ones worth reading.

NOW IS TIED TO THE MAP. Each one names the zone they actually stand in and what they are doing there,
so the lore agrees with the placement pass rather than floating free of it.

LENGTH IS A HARD CONSTRAINT, not a style note. BackgroundScreen has NO SCROLLING: panel is
SCREEN_HEIGHT-260 tall with a 26px line height, so about sixteen lines, and anything past that is drawn
off the bottom of the panel and silently lost. Sections are kept near 700 characters and the builder
refuses to write anything that would overflow.

The Integration was THREE years ago (claude/integration_timeline.md). Nothing from Earth exists here as
an object - no phones, no photographs, no kit. What these people brought is in their hands and their
heads, which is why the trades carried and the possessions did not.

WHAT THE FIRST DRAFT GOT WRONG, because it is worth not repeating. Kyle, on reading it: "Don't make
them sound fake or AI though." Grepping the finished text for tells found one systemic problem and two
habits:

  * THE NARRATOR WAS RANKING THEM AGAINST EACH OTHER - "the hardest three years of anyone on this
    list", "the only person here for whom", "the youngest of them". Seven sections, SIX of them in
    Adjustment, because all 25 Adjustments got written in one sitting with the other 24 in view. It is
    the single loudest tell in the set: nobody reading Ama's file has read Owen's, and "on this list"
    is the prose admitting out loud that it is a list. All seven rewritten to stand alone.
  * EMPTY INTENSIFIERS - exactly, entirely, genuinely, considerably, perfectly. Twenty-five of them,
    every one making a sentence sound weighed rather than making it mean more. Cut to fifteen, kept
    only where the word does work.
  * ONE CLOSING MOVE USED FIVE TIMES - set a line up, undercut it in the next sentence ("He means it
    as a joke about retirement. It is not clear he is joking."). Good once. A formula at five. Three
    rewritten; the two that are earned by their section stayed.

The fix for all three was the same: write what the person did, not what it signifies. A concrete
closing detail - a standing argument with three quartermasters about rope, the water level in three
wells - never reads as generated. A neat reversal always might.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Measured against BackgroundScreen: ~1072px of line at font 17 is roughly 115 characters, and the
#: panel fits ~16 lines. 1100 leaves room for a paragraph break without ever reaching the bottom edge.
MAX_CHARS = 1100

B = {}   # recruit_id -> {before, adjustment, now, forward}

B["dan_warrior"] = dict(
    before="Twelve-hour days on a site in Lagos, hard hat, clipboard, and the particular exhaustion of "
           "being the only person on a job who would say no. He ran crews of forty. He got two of them "
           "out from under a slab in his second year and he has never once described that as heroism - "
           "he describes it as the day the scaffolding inspection he had signed off on turned out to "
           "have been worth the argument.\n\n"
           "He was good at the part nobody thanks you for: standing in front of the money and the "
           "deadline and the man with the envelope, and not moving.",
    adjustment="Three years ago he came through with his boots on and his hands empty, and his first "
               "clear thought was that somebody was going to get hurt if nobody organised this.\n\n"
               "So he organised it. He has never had the crisis everybody kept waiting for him to "
               "have. People read that as strength and he lets them, because the honest version is "
               "less flattering: he was never attached to the clipboard. He was attached to the crew, "
               "and there was a crew here immediately.",
    now="Orgrimmar, mostly, where there is always another group of people about to walk into something "
        "they have not scouted. He stands at the front and he takes the first hit and he is extremely "
        "boring about it, which is the point.\n\n"
        "He has a standing argument with three different quartermasters about rope.",
    forward="He wants a permanent crew and he wants them to outlive him, in that order. He has started "
            "teaching the shield work to anyone who stands still, badly at first, and he is getting "
            "better at teaching than he is at fighting.\n\n"
            "Privately he would like one season where nobody needs him to stand in front of anything.")

B["ama_priest"] = dict(
    before="Eleven years of paediatric nights in Lagos. Cots instead of beds, four to a bay, and the "
           "arithmetic nobody says out loud about which child gets the last of something.\n\n"
           "She was very good and it cost her. She learned to keep her voice level while her hands did "
           "something frightening, which is a skill that looks like calm from the outside and is not. "
           "She rolled a healer in every game she ever played. Nobody in her life read that as a tell.",
    adjustment="She does not talk about the first two years and the people who were there do not "
               "either. On Earth there was always a form, a referral, a reason you could not. Here "
               "there is "
               "light in her hands and no limit at all, and for the first year she worked until she "
               "fell over because nothing was telling her to stop.\n\n"
               "Somebody eventually did. She has a rule now about hours, and she mostly keeps it.",
    now="Razor Hill, where the road brings in whatever the Barrens did to people that week. She has "
        "made herself the thing that town did not have: somebody who is reliably in one place.\n\n"
        "The orc children have stopped being frightened of her, which took far longer than "
        "the healing did.",
    forward="She wants to train somebody. Not a student - a replacement, so the room is still staffed "
            "when she is not in it.\n\n"
            "She has also started writing down what works, in a hand nobody else can read yet, because "
            "eleven years taught her that knowledge which lives in one person dies with them.")

B["silas_rogue"] = dict(
    before="Five years of port security in Antwerp: cargo manifests, camera feeds, and the dockside "
           "arrangement where everybody took a little and nobody took enough to be a problem.\n\n"
           "He never joined in and he never reported it either. He got paid, kept his head down, and "
           "went home clean, and if you had asked him what he believed in he would have changed the "
           "subject. He was waiting for something without knowing it.",
    adjustment="He came through delighted. A new world meant no record, no reputation, nothing to live "
               "down - he genuinely expected a free-for-all and he intended to enjoy it.\n\n"
               "What he found instead was a frontier with sharper rules than Antwerp ever had, because "
               "out here the people who break them do not get a hearing. That took about four months "
               "to understand and it reorganised him completely. He is not disappointed. He is relieved.",
    now="Ratchet, which is a port, which is the only shape of place he has ever been able to read "
        "properly. He knows which crates are light, which captains are lying, and which goblin is "
        "about to be robbed by the man standing next to him.\n\n"
        "He sells that information at a fair price, which still surprises him.",
    forward="He wants a stake in something. Not ownership - he is not built for it - but a berth, a "
            "cut, a reason to be at the same pier next year.\n\n"
            "He has never committed to anything in his life and he has started to suspect that is not "
            "the same thing as being free.")

B["rosa_hunter"] = dict(
    before="Eight years guiding in Tanzania. Researchers, photographers, the occasional idiot with "
           "money, and a great deal of sitting absolutely still in the dark.\n\n"
           "She learned that a predator is not cruel and hunger is not personal, and she got very tired "
           "of explaining both to people who wanted the lion to mean something. The savanna did not "
           "care about her. That was most of what she loved about it.",
    adjustment="The animals here think. That was the whole adjustment and it took her a year.\n\n"
               "A lion runs a calculation you can learn; a quilboar runs a plan, and it changes the "
               "plan when it sees you. She had to stop tracking and start anticipating, and she was "
               "genuinely bad at it for a while, which she had not been bad at anything in a decade.",
    now="The Central Barrens, which is close enough to savanna to hurt. Dry grass, long sightlines, "
        "big animals moving in the heat.\n\n"
        "She works the Crossroads road where the hyenas have learned what a caravan is, and she has "
        "started being able to tell you what a given pack will do before it does it.",
    forward="She wants to see the coast. Not for a reason - she grew up a long way from an ocean and "
            "then spent her career further from one, and she has decided she is owed.\n\n"
            "After that, somewhere nobody has mapped. She came here for wild and the wild keeps "
            "turning out to have a road through it.")

B["marco_paladin"] = dict(
    before="Twelve years policing Milan. The uniform, the radio, the specific tiredness of being the "
           "thing people call when it is already too late.\n\n"
           "He believed in it, which made him both better at the job than most and much worse at "
           "living with it. He has a short list of nights he does not discuss. He left the force "
           "exactly never - the world ended first.",
    adjustment="The badge did not come through. That sounds small and it nearly finished him: for "
               "twelve years the authority had been issued to him, and here there was nobody to issue "
               "anything.\n\n"
               "He spent most of a year deciding whether he was still a police officer if no state "
               "said so. He decided yes. The light arrived at roughly the same time and he has never "
               "been entirely sure which caused which.",
    now="The Undercity, of all places, standing between the Forsaken and everyone who thinks their "
        "existence is a verdict waiting to be delivered.\n\n"
        "He is not comfortable there. He has been clear that he does not need to be comfortable, and "
        "the Forsaken appear to respect him for it in their own flat way.",
    forward="He wants a law - any law, written down, that applies to everyone including him. The "
            "absence of one is the only thing out here he finds genuinely frightening.\n\n"
            "He has four pages of it and has shown them to nobody.")

B["sophia_mage"] = dict(
    before="Ten years of combustion research in São Paulo: industrial accidents, blast modelling, and "
           "reports that went to agencies who filed them.\n\n"
           "She watched a refinery burn from a monitoring station eleven kilometres away and wrote the "
           "paper that explained precisely why it had, eight months after the funerals. Being right "
           "slowly stopped being enough. She did not get bitter so much as very, very quiet.",
    adjustment="She was working inside a month. Fire here obeys the same rules it always did; she "
               "simply stopped needing a facility and a grant.\n\n"
               "What took longer was the part she will not discuss: for ten years her work killed "
               "nobody because nobody read it. That is no longer true, and she has had to find a "
               "position on that.",
    now="The Undercity, where the Apothecarium are the first colleagues she has had who actually read "
        "her work, argue with it, and occasionally frighten her.\n\n"
        "She has an arrangement with them that she describes as collaboration and would not describe "
        "to anyone from home.",
    forward="She wants to publish. Out loud, that is a joke. Underneath it she is entirely serious: "
            "she is assembling a body of work on how this world's fire differs from Earth's, and she "
            "intends somebody to be able to read it in a hundred years.\n\n"
            "It is the first time her work has had a reader she believes in.")

B["ryan_warlock"] = dict(
    before="Twelve years broking in Boston. He was good, he was paid accordingly, and the deals he cut "
           "took things from people who never learned his name.\n\n"
           "He drank after work with people who did the same thing and they all agreed it was the "
           "system. He did not believe that even while he was saying it, which is the difference "
           "between him and the men he drank with.",
    adjustment="He expected to be punished and was braced for it, and instead the frontier handed him "
               "a skill that is the same skill: read what a thing wants, work out what it will take, "
               "close.\n\n"
               "He has not had an adjustment so much as a diagnosis. Three years on he is more honest "
               "than he has ever been and no better a man, and he will say so before you can.",
    now="The Undercity, where nobody is under any illusions about anybody. He finds it restful.\n\n"
        "His demons are on contracts he wrote himself, every clause of which he can recite. He is "
        "meticulous about paying on time, which is not virtue - it is the only thing keeping the "
        "arrangement from going the other way.",
    forward="He wants out of the business. He has wanted out for fifteen years and has never once "
            "taken a step toward it.\n\n"
            "What he actually does is keep the contracts clean and the terms honest, and tell himself "
            "that is different. Some days it is.")

B["carolina_shaman"] = dict(
    before="Twelve years fighting mining concessions in Peru with survey data, injunctions and rage. "
           "She lost more than she won. She was told she was shrill by men who then quoted her "
           "findings.\n\n"
           "She knew the forest was talking. She could prove it in a dataset and not in a way anybody "
           "would act on, and the gap between those two things took a decade out of her.",
    adjustment="The Integration was a relief and she has stopped apologising for saying so.\n\n"
               "The earth answered immediately and in words. There was no learning curve, no crisis, "
               "no year of grief - she had been fluent her whole life in a language nobody else "
               "admitted existed. What she has had to adjust to is being believed, which turns out to "
               "be harder than being ignored.",
    now="The Echo Isles, at the springs, listening. The Darkspear were not expecting a transplant to "
        "be any use at this and have quietly stopped saying so.\n\n"
        "She spends a great deal of time doing nothing visible, and the water level in three wells is "
        "better than it was.",
    forward="She wants to be told what the frontier is trying to say. She is increasingly sure it is "
            "one thing, repeated, and that nobody has the whole of it.\n\n"
            "She is also aware that the last time she was sure about something that large, it took "
            "twelve years and she still lost the valley.")

B["amber_druid"] = dict(
    before="Fifteen years of forestry in Alberta: timber allocations, fire seasons, caribou counts, and "
           "a long slow education in watching a decision get made two provinces away by somebody who "
           "had never stood in the stand it concerned.\n\n"
           "She did not burn out. She calcified. By the end she was documenting losses with the same "
           "steady hand she had once used for recovery plans.",
    adjustment="Druidry made sense in about a week and the week was not the hard part.\n\n"
               "The hard part was the first time the land did something back - she had spent a career "
               "advocating for ground that could not advocate for itself, and the entire moral "
               "architecture of that job assumed a silent client. Three years on she has mostly "
               "rebuilt it. She is still working out who she is when the forest can speak for itself.",
    now="The Central Barrens, which is not forest and is exactly the kind of marginal, overgrazed, "
        "fought-over ground she spent fifteen years on.\n\n"
        "She is working the water courses. Progress is measurable in weeks here instead of decades, "
        "and she has not got used to that and does not intend to.",
    forward="She wants to see the Barrens hold a wet season without losing topsoil to the wash. It is "
            "a deeply unglamorous ambition and she is at peace with that.\n\n"
            "Further out: somewhere old. She has heard what the north is now and she wants to stand "
            "in it.")

B["marcus_stormbringer"] = dict(
    before="A meteorologist in Toronto who spent his career being right early. Models, warnings, "
           "briefings to people whose job was to decide the warning was inconvenient.\n\n"
           "Storms were the obsession before they were the career. He chased them as a student, badly "
           "and happily, and then spent fifteen years watching them on instruments from inside a "
           "building.",
    adjustment="He treated the whole thing as fieldwork and it carried him through almost "
               "intact.\n\n"
               "The one genuine adjustment: on Earth a storm was something he predicted and could "
               "never touch. Here it answers. He spent most of the first year being quietly, "
               "privately wrecked by that and telling everyone he was fine, which they believed, "
               "because he was also fine.",
    now="Durotar, where the dry storms come off the sea with no rain in them and the thunder arrives "
        "without warning.\n\n"
        "He has started keeping records again - wind, pressure, where the strikes land - which nobody "
        "asked for and which has already told him something about this coast that the orcs did not "
        "know.",
    forward="He wants to publish a season's data and he wants someone here to care about it. He is "
            "realistic about the odds.\n\n"
            "What he will not say out loud: he wants to stand in the middle of the biggest one there "
            "is, and he knows exactly how that ends for people who want that.")

B["ivan_warrior"] = dict(
    before="Twenty years boxing out of St Petersburg. Not a champion - a professional, which is "
           "different and harder. He took fights he should not have and won most of them.\n\n"
           "Violence was the only language he was ever fluent in and it worked, right up until the "
           "point where it was the only one he had. He does not talk about his family. He does not "
           "talk about the last two years of the career either.",
    adjustment="He did not adjust. He arrived somewhere that made more sense than where he came from "
               "and he simply stopped looking back, which everybody around him finds unsettling and "
               "he finds restful.\n\n"
               "No judges. No promoters. No disappointed face in the third row. The violence out here "
               "is clean in a way he could not have explained to anyone on Earth without sounding "
               "like a monster.",
    now="Ragefire Chasm, where it is too hot for most people to work and he has never once mentioned "
        "the heat.\n\n"
        "He takes contracts nobody else wants, comes out, and goes back in. The people who hire him "
        "have noticed he never asks what a thing has done to deserve it.",
    forward="He does not have a plan and does not want one. Asked directly, he says he would like to "
            "keep going until something is better than him.\n\n"
            "He says it like a joke about retiring. Nobody who has trained with him takes it as one.")

B["asher_coleman"] = dict(
    before="Deep South, Bible Belt, and you can hear it inside three words. He will tell you about the "
           "place and not about himself, and he is so warm about it that you get most of the way home "
           "before you notice.\n\n"
           "What anyone actually knows: he came through like everybody else, and he says the fall felt "
           "less like falling than like being carried. He laughs that off before it turns into a "
           "sermon. He always laughs it off.",
    adjustment="There is no record of Asher having an adjustment, and that is the strangest thing "
               "about him.\n\n"
               "Everyone else can name their bad year. He was camped outside the Burning Blade Coven "
               "within days, alone, waiting for nobody in particular, on the grounds that somebody "
               "ought to be and it might as well be him. He asked no questions about where he was. He "
               "has still not asked any.",
    now="Wherever you are. He does not take contracts and he does not go home, and the one time "
        "somebody tried to send him back he was simply there the next morning, perfectly friendly "
        "about it.\n\n"
        "He never asks why you are doing something. He asks if you could use the help, like it is the "
        "easiest question in the world, and it is very difficult to say no to.",
    forward="He has never stated a want. Not once, to anyone, in three years.\n\n"
            "Asked, he turns it around and asks about yours, and he is so interested that "
            "it works every time. Somebody has started keeping a count of how often it works. The "
            "count is now quite long.")

B["owen_cultist"] = dict(
    before="Twenty-two years of mine rescue in the South Wales valleys. He went down when everyone "
           "else was coming up, which is the entire job description and sounds like bravery only to "
           "people who have not done it.\n\n"
           "He knows the sound a roof makes a second before it goes. He has brought men out and he has "
           "left men in, and he can tell you the difference between those two decisions in about four "
           "words, none of them comfortable.",
    adjustment="He will not discuss those three years in order, and gets quiet if you try.\n\n"
               "He always knew the dark under the ground was not as empty as the surveyors claimed - "
               "every rescue man does, and every rescue man keeps it to himself. Here it answered. It "
               "offered him strength he had not asked for and did not want, and he took it, because "
               "there were people down there. He has not forgiven himself and does not consider that "
               "the point.",
    now="Azurelode Mine, which flooded, and which has things in it that were not in the survey.\n\n"
        "He is the last man out of that place every single time, and the crews working the Hillsbrad "
        "shafts have started treating his presence as a safety feature. He is aware that is not what "
        "he is.",
    forward="He wants to know what it is that answered him. Not to defeat it - he is not built for "
            "that story - but because twenty-two years taught him that you do not work under "
            "something you have not surveyed.\n\n"
            "He expects the answer to be bad. He is going down anyway.")

B["mateo_starcaller"] = dict(
    before="Fourteen years of night shifts at a radio array in the Atacama, listening to a sky that "
           "never once answered.\n\n"
           "That is not a tragic job if you are built for it, and he was. He kept notebooks - every "
           "pulse, every candidate signal, every eventual boring explanation - in Spanish and English "
           "depending on how tired he was. He slept through the days. He has still never properly "
           "adjusted to daylight and sees no reason to start.",
    adjustment="The sky answered, in moonlight, and it knew his name.\n\n"
               "He did not have a crisis. He had the opposite, and the people around him in that first "
               "year found it more alarming than a breakdown: a man who has waited "
               "fourteen years for a reply, getting one, and calmly reaching for a notebook. He is not "
               "adapting. He is in correspondence.",
    now="The Windward Road under Freewind Post, where the mesas run out and the sky gets very large. "
        "He has found the only other people in this world who watch it professionally.\n\n"
        "Freewind's skywatchers were polite about him for about a month and are now arguing with him "
        "nightly, which he calls the warmest welcome of his life.",
    forward="He wants to know whether what speaks to him is one voice or many, and he has designed a "
            "way to find out that requires him to be in three places on the same night.\n\n"
            "He is recruiting for that, gently, and has not yet told anyone what the third place is.")

B["pasang_primalist"] = dict(
    before="Thirty seasons guiding in the Khumbu. He roped strangers to a mountain that had no opinion "
           "about them and got most of them down.\n\n"
           "He has carried people off a slope who would not have seen morning, and he has left people "
           "who were already gone, and he is one of the very few who can describe both without "
           "performing either. The mountain never owed anybody anything. He found that restful and "
           "most of his clients found it unbearable.",
    adjustment="A mountain is a mountain. That is the whole of his adjustment and he has "
               "said it, in those words, to three different people who wanted a longer answer.\n\n"
               "The earth answers him here slowly and with weight, which is how it always answered - "
               "the difference is only that now the reply arrives in the same lifetime. He treats this "
               "as a scheduling improvement.",
    now="The Aspen Wilderness, which is a mountain range that was not on this world four years ago, "
        "with a pass through it that people are already dying on.\n\n"
        "He has walked every chute off the Rim and is building, in his head and nowhere else yet, the "
        "first honest route description this range has ever had.",
    forward="He wants the route written down and he wants it in somebody else's hands, because a route "
            "that lives in one guide is not a route, it is a dependency.\n\n"
            "After that he would like to go up something nobody has been up. He is sixty-one. He has "
            "done the arithmetic and he is not concerned.")

B["haruto_runemaster"] = dict(
    before="Eleven years of hand-poked irezumi in Osaka. Needle, ink, no machine, and the long patient "
           "argument with a client about what they will still want on their body in forty years.\n\n"
           "He learned the rule that governs everything he does now: a line in the wrong place does not "
           "wash off. You can cover it, you can work it into something larger, you can spend a decade "
           "making it mean something else. You cannot remove it.",
    adjustment="He arrived and found a world where the rule was literal, and he says - without any "
               "apparent distress - that the ink simply moved into the steel.\n\n"
               "His three years have been almost entirely technical. What did unsettle him, badly and "
               "briefly, was discovering that a rune cut wrong does not merely look wrong. It does "
               "something. He has a scar from that and he does not show anybody where.",
    now="Silverpine South, near Ambermill, where the magisters cut letters into things and will "
        "occasionally let him watch.\n\n"
        "He carries a blade whose edge changes with the line he draws on it, and he will not tell you "
        "which line he is carrying until it is already out. He thinks that is funny. He is correct.",
    forward="He wants to cut one rune that outlasts everybody who sees it made. That was the whole "
            "ambition of the Osaka work too, and skin was always going to lose.\n\n"
            "Stone is available here, and he has been told there is something in the "
            "Underdark that is harder than stone. He has not gone to look yet.")

B["liam_suncleric"] = dict(
    before="Seventeen summers of bushfire season in New South Wales and the bad nights on the highway "
           "in between. Firefighter, then paramedic, then both, because the roster never cared which "
           "badge you held at three in the morning.\n\n"
           "He learned that the most useful thing in a burning room is a calm voice and the second is "
           "a hand on the person who is about to run. He is good company and has not slept "
           "properly since roughly 2019.",
    adjustment="Easiest first year, hardest second. For twelve months he simply did the job, because "
               "the job was everywhere and nobody had to ask.\n\n"
               "Then it got quiet for a season and he discovered he had no idea what he was for "
               "without an emergency. That was a bad few months and the people who were there do not "
               "bring it up. The sun answers him the way a good crew does - when called, and all at "
               "once - and he has stopped pretending that is not most of what holds him together.",
    now="Ashenvale East, working the ground around Grom's Rest where the corruption burns out of "
        "people slowly and nobody has a protocol for it.\n\n"
        "He has written one. It is four lines long, it is wrong in at least one place, and it is the "
        "only one that exists.",
    forward="He wants a crew. Not companions - a crew, rostered, trained, who can do it without him "
            "there.\n\n"
            "He is aware that this is the same thing he wanted on Earth and never got, and that the "
            "reason he never got it was that he kept going in alone.")

B["marta_tinker"] = dict(
    before="Nineteen years blasting in the Sudbury basin. Drill the pattern, charge it, wire it, walk "
           "a long way back, and then the part everybody else finds interesting and she finds "
           "arithmetic.\n\n"
           "She has never once been surprised by a bang and she has a low opinion of people who are. "
           "Being surprised means somebody measured wrong, and somebody measuring wrong is how you "
           "lose a hand.",
    adjustment="She considers the Integration an inconvenience that improved her supply situation and "
               "will not be moved off this position.\n\n"
               "Pressed, she concedes one difficulty: the charges here come with intent. A fuse that "
               "wants something is not a fuse, it is a colleague, and she had nineteen years of "
               "habits built on materials that had no opinions. She has rebuilt the habits. She is "
               "still annoyed about it.",
    now="Boulder Lode Mine, a Venture Co. claim that was dug badly by people in a hurry, which she "
        "describes as the most natural working environment she has ever been in.\n\n"
        "She is re-shoring the sections the goblins left, mostly so she can get at the back of it, "
        "and partly because it offends her.",
    forward="She wants a face nobody has shot before, and the time to open it properly instead of "
            "fast.\n\n"
            "She also wants one of the goblin engineers to admit, out loud, in front of someone, that "
            "her pattern is better than theirs. She has been waiting two years and is prepared to "
            "wait longer.")

B["callum_venomancer"] = dict(
    before="Sixteen years keeping reptiles at a Queensland sanctuary. Taipans, death adders, and the "
           "constant low-grade public relations work of explaining that the animal is not malicious, "
           "it is frightened and you are enormous.\n\n"
           "He has been envenomated more often than any person should be and files all of it under "
           "professional development. His forearms are a map of the learning curve.",
    adjustment="The venom here is older and cleverer, and so, he says, is he.\n\n"
               "His adjustment was almost entirely physical and took about eighteen months of being "
               "very unwell on purpose. He does not recommend the method and will not describe it in "
               "detail to anyone who might copy him. What he got out of it is a working relationship "
               "with things that kill people, which is the same relationship he had before, with "
               "better participants.",
    now="The Central Barrens, within reach of the Wailing Caverns, where the serpents are a great deal "
        "more than serpents and have a clear view about intruders.\n\n"
        "He goes in regularly and comes out reliably, and the one time he brought something out alive "
        "the Crossroads made him promise not to do it again.",
    forward="He wants to be bitten by whatever is at the bottom of that place and survive it, and he "
            "knows how that sentence reads.\n\n"
            "His actual position, which he can defend: the thing that bites back is the thing that "
            "trusts you, and he has never yet met the animal that was not worth the conversation.")

B["emre_rogue"] = dict(
    before="Thirty doors a week in the old bazaar in Istanbul. He started at nine, sent to fetch a "
           "stuck deadbolt for an uncle, and discovered that every lock is a short conversation with "
           "somebody who is not in the room.\n\n"
           "He was never a thief. He was the man you called when you had locked yourself out of your "
           "own livelihood, and he knew the inside of more businesses in that quarter than their "
           "owners did.",
    adjustment="He arrived and found a bigger bazaar with worse customers, and he has been perfectly "
               "happy for three years.\n\n"
               "The only real adjustment: on Earth, what was behind the door was a stockroom. Here it "
               "occasionally talks, and once it asked him a question while he was still working the "
               "mechanism. He got the door open. He has never said whether he answered.",
    now="Eastern Hillsbrad, in the country around Durnholde, which is a keep full of doors built by "
        "people who were serious about them.\n\n"
        "He is not looting it. He is reading it - which lock came first, which were added after "
        "somebody got in, and therefore where somebody got in.",
    forward="He wants the one that beats him. He has not met it yet and has begun to worry that he "
            "will not.\n\n"
            "Less romantically, he would like an apprentice, because the trade dies with him "
            "otherwise and he has watched that happen to four crafts in his own quarter already.")

B["bakyt_hunter"] = dict(
    before="Third generation, forty winters with a golden eagle on his arm in the mountains of "
           "Kyrgyzstan. He has never owned an animal in his life. He has been trusted by one, which he "
           "will tell you is an entirely different arrangement and a much more demanding one.\n\n"
           "He buried his father's bird and his own first bird on the same ridge. He goes up there in "
           "spring. He does not explain why and nobody has ever needed him to.",
    adjustment="His eagle did not come through. That is the whole of the first year and he has said "
               "perhaps six sentences about it in three years.\n\n"
               "What he did instead of grieving in any way anyone recognised was go up into the "
               "nearest high country and sit, for most of a season, until something came down to look "
               "at him. He has not named it. He says naming it would be presumptuous, which is the "
               "closest thing to a religious statement he has ever made.",
    now="The Hillsbrad foothills, which are not his mountains and are near enough to work with. He "
        "hunts the high ground above Tarren Mill where the ridges run the right way.\n\n"
        "A bird and a man still hunt the same ridge, and the bird is still in charge. That part "
        "survived the crossing intact.",
    forward="He wants to get a young one through its first winter. Everything else is detail.\n\n"
            "He has also started watching the Aspen Wilderness on the horizon, because it is tall and "
            "cold and the right shape, and a man who has spent forty winters on a mountain can tell "
            "from a long way off whether a mountain is any good.")

B["henrik_mage"] = dict(
    before="Twenty years of ice cores out of Tromsø. Drill, extract, log, and read ten thousand years "
           "of weather out of a tube of frozen water.\n\n"
           "He has stood on a plateau at forty below and recorded in his notes that it was a good day, "
           "and he meant it without irony. Ice is the most honest archive there is: it cannot be "
           "edited, only lost.",
    adjustment="Frost answers him here as a colleague rather than a subject, and he found that "
               "professionally awkward for most of a year.\n\n"
               "Twenty years of method assume the thing you are studying is not studying you. He has "
               "rewritten his own protocols three times and is not satisfied with the third. In every "
               "other respect he is exactly who he was, which his colleagues on Earth would not find "
               "surprising.",
    now="The Frostward Descent, under Hillsbrad, where there is ice that is older than anything on the "
        "surface and it has begun giving things back.\n\n"
        "He is reading it the only way he knows: layer by layer, slowly, writing everything down. He "
        "has found four things in it so far and has reported two of them.",
    forward="He wants to reach the bottom of that ice and read the oldest layer in it, and he believes "
            "it is older than this world's own account of itself.\n\n"
            "He has not told anybody that last part. He is a careful man and he would like more "
            "evidence before he says something that large out loud.")

B["anjali_druid"] = dict(
    before="Nineteen years as an agronomist in Kerala, teaching smallholders to keep a field alive "
           "through a monsoon that had stopped keeping the old calendar.\n\n"
           "Her career was mostly patience and arithmetic: this much mulch, that much shade, wait. She "
           "coaxed poor soil into giving for two decades and the thanks, when it came, usually came "
           "from somebody's mother rather than anybody official.",
    adjustment="Here the soil gives back with interest and she did not trust it for a year.\n\n"
               "That was the adjustment, and it was a professional one rather than a spiritual crisis: "
               "nineteen years had taught her that fast growth is a loan. She has now watched a "
               "full cycle complete without collapsing and she has revised the model. Carefully. With "
               "a note about sample size.",
    now="Ashenvale West, among people who have been tending this forest for longer than her country "
        "has had that name, and who were not expecting to be taught anything by a transplant.\n\n"
        "They were right. She is not teaching. She is doing what she did in Kerala - sitting with the "
        "people who actually work the ground and asking what has stopped working.",
    forward="She wants to see one bad season handled well. Not a good season - anyone can grow things "
            "in a good season.\n\n"
            "Her healing is mostly patience and she is increasingly aware that this is also her entire "
            "personality, and that she does not intend to do anything about it.")

B["hana_shaman"] = dict(
    before="Fourteen years of surf lifesaving on the Waikato coast. Black sand, heavy water, and a rip "
           "that takes somebody every few summers no matter how many signs you put up.\n\n"
           "She learned the only thing about water that matters: it is never your enemy and never your "
           "friend, only honest. People drown because they argue with it. She has pulled a great many "
           "people out and she remembers the two she did not.",
    adjustment="She had less to unlearn than most, and she knows that is luck rather than "
               "merit.\n\n"
               "The tide spirits read her the way she reads a break - take what is offered, give back, "
               "never turn your back on it - and the arrangement was legible to her within days. Her "
               "actual adjustment was social. She arrived at nineteen into a world of people with "
               "whole careers behind them, and she spent a year being treated as the kid.",
    now="The Hillsbrad coast, which is colder and greyer than home and has the same undertow. She has "
        "been teaching the fishing families to read it.\n\n"
        "Two of them have started listening. One of those two has stopped losing nets, which has done "
        "more for her standing in Southpoint than anything she could have said.",
    forward="She wants a bigger sea. She says it lightly and she is not joking - she has heard there "
            "is a coast west of Ashenvale where the water does something she cannot get anyone to "
            "describe properly.\n\n"
            "She is still on the beach. She just wants a better one.")

B["kesten_the_catalogued"] = dict(
    before="Twenty-two years a monumental mason in Aberdeen, cutting letters into granite for people "
           "who had died.\n\n"
           "It is a trade with one unforgiving rule and he will give it to you unprompted: the stone "
           "does not care how you felt about the deadline. He cut names for families who could not "
           "afford them and did not mention it. He was, by any measure that matters, a good tradesman "
           "and a fairly lonely man.",
    adjustment="He came through with his hands and nothing else and went down the Alterac fissure in "
               "the first year, before there was a path worn into the lip.\n\n"
               "He did not go looking for safety. He went looking for the only people he had met who "
               "were also writing things down. The Codex did not turn him away and did not quite take "
               "him in. They gave him a catalogue number, which is the most anyone has formally given "
               "him in his life, and he has never once objected.",
    now="Kael's Bastion, entry eleven thousand and something, the only line in the index that is a "
        "person.\n\n"
        "He cuts their runes now - the deep ones, in the columns, that have to outlast the people who "
        "ordered them. It is the same trade with the same rule and a far better class of stone.",
    forward="He would like to know whether the number is loyalty or the closest thing to a headstone "
            "anyone has ever offered him. He has had three years to decide and has not.\n\n"
            "He suspects the Codex have not decided either, and that this is the most honest "
            "relationship in the cavern.")


def main():
    p = ROOT / "data/npcs/recruits.json"
    data = json.loads(p.read_text())
    ids = {r["recruit_id"] for r in data["recruits"]}

    missing = ids - set(B)
    extra = set(B) - ids
    if extra:
        raise SystemExit(f"background written for recruits that do not exist: {sorted(extra)}")

    over = []
    for rid, sections in B.items():
        for key in ("before", "adjustment", "now", "forward"):
            if key not in sections or not sections[key].strip():
                raise SystemExit(f"{rid}: section {key!r} is missing or empty")
            if len(sections[key]) > MAX_CHARS:
                over.append((rid, key, len(sections[key])))
    if over:
        # BackgroundScreen does not scroll - anything past the panel is drawn off the bottom and lost
        # without a warning, so this is a build failure rather than a style note.
        raise SystemExit("sections would overflow the panel:\n  " +
                         "\n  ".join(f"{r} / {k}: {n} chars (max {MAX_CHARS})" for r, k, n in over))

    for r in data["recruits"]:
        if r["recruit_id"] in B:
            r["background_sections"] = B[r["recruit_id"]]
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    n = sum(len(v) for v in B.values())
    chars = sum(len(t) for v in B.values() for t in v.values())
    print(f"wrote {n} sections across {len(B)} recruits ({chars:,} characters)")
    if missing:
        print(f"  still unwritten: {sorted(missing)}")


if __name__ == "__main__":
    main()
