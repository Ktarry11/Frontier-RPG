# -*- coding: utf-8 -*-
"""Batch 1 of the recruit rewrite (levels 7-12). See tools/rewrite_recruits.py.

Kyle, 2026-10-31: "Each character should be fully fleshed out. Feeling alive. Some struggle,
some do well. Some have a better life. Some have worse. These people have different
nationalities. Some use bad English or cultural references."

The four section KEYS are fixed - ui/screens/background_screen.py reads
Character.BACKGROUND_SECTION_KEYS and draws exactly four tabs - so the variety has to live in
the prose, not the scaffold. What that means in practice: no section opens the way the one
above it did, the lengths are deliberately uneven, and not everybody's story resolves.

ENGLISH AS A SECOND LANGUAGE, written with respect. Non-native speech here is real transfer -
a Slavic speaker dropping articles, a Japanese speaker's careful formality, a Brazilian
calquing an idiom straight across - never phonetic spelling or comedy accent. The greeting is
the character actually talking, so that is where it lives. The backstory is narration and stays
in the narrator's register.
"""

BATCH = {

"ama_priest": dict(
    greeting="Sit down. No — sit, I am not asking you twice, and you are dripping on a floor "
             "I have already done once today.",
    backstory=(
        "There is a rule about her hours and everyone in Razor Hill knows she breaks it. Twice "
        "now the orc women have walked her back to her own cot with a hand between her shoulder "
        "blades. She was a children's nurse somewhere with four cots to a bay and an arithmetic "
        "nobody said out loud, and the thing she carried over was not the healing. It was the "
        "arithmetic. She still runs it, every time, on a world that does not make her — and she "
        "has not worked out how to stop."),
    before=(
        "Paediatric nights, four to a bay, and a ward sister who taught her to keep her voice "
        "level while her hands did something frightening. That skill looks like calm from "
        "outside. It is not calm.\n\n"
        "She was very good. It cost her a marriage and most of her twenties and she would tell "
        "you the trade was obvious."),
    adjustment=(
        "The first two years are not a subject. Nobody in Razor Hill asks and she has never "
        "offered.\n\n"
        "What she will say is this: back home there was always a form, a referral, a reason you "
        "could not. Here there is light in her hands and no limit at all, and for a year nothing "
        "in the world told her to stop, so she did not, until an orc woman whose son she had "
        "kept breathing picked her up off the ground and told her."),
    forward=(
        "Somebody has to be able to do this when she is not in the room. Not a student — a "
        "replacement. She has been looking for two years and turned down four people for "
        "reasons she cannot articulate, which she knows is the problem.\n\n"
        "There is also a notebook. The handwriting is appalling on purpose."),
    now=(
        "Razor Hill, where the road brings in whatever the Barrens did to people that week.\n\n"
        "The children stopped being frightened of her a long while after the adults did, which "
        "she thinks is the correct order."),
),

"marcus_stormbringer": dict(
    greeting="Pressure's dropping. No — listen. That's not thunder yet, that's the front "
             "arriving. We've got maybe four minutes and then it gets loud and I get useful.",
    backstory=(
        "He spent a career being right early and watching it change nothing: models, warnings, "
        "briefings to people whose job was to decide the warning was inconvenient. Here the "
        "storm answers him. He has been telling everyone he is fine about that since the day it "
        "started, and everyone believes him, because he is also genuinely fine. Both are true "
        "and he has stopped trying to reconcile them."),
    before=(
        "Toronto. Instruments, a building, and a window. He chased storms as a student — badly, "
        "in a Corolla, happily — and then spent fifteen years watching them on screens from "
        "inside somewhere warm.\n\n"
        "His mother in Lagos thought the job was a waste of a good degree and said so at every "
        "Christmas until the last one."),
    adjustment=(
        "He treated the whole thing as fieldwork and it carried him through almost intact, which "
        "is a better outcome than most people got and he knows it.\n\n"
        "The part that wrecked him, privately, for most of a year: on Earth a storm was "
        "something he predicted and could never touch."),
    forward=(
        "A season's data, written up, and one person on this world who cares what is in it. He "
        "is realistic about the odds and keeps the records anyway.\n\n"
        "The thing he does not say out loud is that he would like to stand in the middle of the "
        "biggest one there is. He is a meteorologist. He knows exactly how that ends."),
    now=(
        "Durotar, where the dry storms come off the sea with no rain in them and the thunder "
        "arrives without any warning at all.\n\n"
        "His notes on where the strikes land have already told him something about this coast "
        "that the orcs did not know, and he has not worked out how to tell them without sounding "
        "like every other outsider who ever arrived with a clipboard."),
),

"marco_paladin": dict(
    greeting="You will stand behind me. Not beside — behind. I have had this argument in two "
             "languages and I have never lost it.",
    backstory=(
        "The badge did not come through with him. He has described that as a small thing and it "
        "nearly finished him: for twelve years in Milan the authority had been issued to him by "
        "somebody, and out here there is nobody to issue anything. He spent the better part of a "
        "year deciding whether he was still a police officer if no state said so. He decided "
        "yes. The light arrived at about the same time and he has never been sure which caused "
        "which, or whether that question is even allowed."),
    before=(
        "Twelve years in Milan. The uniform, the radio, and the particular tiredness of being "
        "the thing people call when it is already too late.\n\n"
        "He believed in it, which made him better at the work than most and considerably worse "
        "at living with it. There is a short list of nights he does not discuss."),
    adjustment=(
        "Badly, and for longer than he admits. He was not built to be a man with no institution "
        "behind him and he has had to become one anyway."),
    forward=(
        "There should be a law. Any law, written down, that applies to everybody including him. "
        "The absence of one is the only thing out here he finds genuinely frightening.\n\n"
        "He has four pages of it in a notebook and has shown it to no one. He is aware of how a "
        "foreigner writing a legal code for the Forsaken would be received. He writes it anyway."),
    now=(
        "The Undercity, of all the places he could have ended up, standing between the Forsaken "
        "and everyone who treats their existence as a verdict already delivered.\n\n"
        "He is not comfortable there. He has been clear that he does not need to be comfortable. "
        "The Forsaken appear to respect him for it in their own flat way, which he finds more "
        "unsettling than hostility."),
),

"sophia_mage": dict(
    greeting="Show me what burned and I tell you why. Not guessing — I will tell you the "
             "temperature it happened at. People find this annoying. I find it is usually "
             "correct.",
    backstory=(
        "She watched a refinery burn from a monitoring station eleven kilometres away and "
        "published the paper explaining exactly why, eight months after the funerals. Being "
        "right slowly stopped being enough somewhere around the fourth time. She did not turn "
        "bitter so much as extremely quiet, and the quiet came with her. Here fire obeys the "
        "same rules it always did and she no longer needs a facility or a grant, and for ten "
        "years her work killed nobody because nobody read it. That is no longer true. She has "
        "had to find a position on it and has not finished."),
    before=(
        "São Paulo. Combustion research: industrial accidents, blast modelling, reports that "
        "went to agencies who filed them.\n\n"
        "Her supervisor called her *teimosa* — stubborn — and meant it as a criticism for six "
        "years and a compliment afterwards."),
    adjustment=(
        "A month. She was working inside a month, which she says without pride because it was "
        "not courage, it was that the physics did not change and she had nowhere else to put "
        "herself."),
    forward=(
        "There is a body of work accumulating on how this world's fire differs from Earth's, and "
        "she intends that somebody can still read it in a hundred years. Said out loud it is a "
        "joke about academic publishing. It is not a joke.\n\n"
        "It is the first time in her life her work has had a reader she believes in, and the "
        "reader is dead, which she is aware is funny."),
    now=(
        "The Undercity. The Apothecarium are the first colleagues she has ever had who read her "
        "work, argue with it, and occasionally frighten her.\n\n"
        "She calls the arrangement a collaboration. She would not describe it in those terms to "
        "anyone from home, and she has stopped writing to the people who would ask."),
),

"carolina_shaman": dict(
    greeting="Quiet a moment. — No, really quiet, I am not being mystical at you, I am trying "
             "to hear the water and you are standing on it.",
    backstory=(
        "Twelve years of mining concessions in Peru, fought with survey data and injunctions and "
        "rage, and she lost more than she won. She was called shrill by men who then quoted her "
        "findings in their own reports. She always knew the forest was talking; she could prove "
        "it in a dataset and never in a way anybody would act on, and the distance between those "
        "two things took a decade out of her. Then the earth here answered in words, immediately, "
        "with no learning curve at all. The Integration was a relief. She has stopped apologising "
        "for saying so."),
    before=(
        "Survey work, legal filings, and a valley she lost anyway.\n\n"
        "She has a photograph of it from before. She does not look at the photograph."),
    adjustment=(
        "There was not one, and that is its own problem. No crisis, no year of grief — she had "
        "been fluent her whole life in a language nobody admitted existed, and then everybody "
        "could hear it.\n\n"
        "Being believed turns out to be harder than being ignored. Ignored, she knew what to do "
        "in the morning."),
    forward=(
        "Something is being said to this world repeatedly and nobody has the whole of it. She is "
        "increasingly certain it is one thing and not many.\n\n"
        "She is also aware that the last time she was certain about something that size it took "
        "twelve years and she still lost the valley. She has not decided whether that is a "
        "warning or just a fact."),
    now=(
        "The Echo Isles, at the springs, mostly doing nothing visible. The Darkspear were not "
        "expecting a transplant to be any use at this and have quietly stopped saying so.\n\n"
        "The water level in three wells is better than it was. She will not claim credit for it "
        "and will not deny it either."),
),

"ryan_warlock": dict(
    greeting="Everything costs something. That's not a threat, it's just the terms. I'll tell "
             "you the price before we start, which is more than my last employer ever did for "
             "me.",
    backstory=(
        "Twelve years broking in Boston, good at it, paid accordingly, and the deals he closed "
        "took things from people who never learned his name. He drank after work with men who "
        "did the same and agreed with them that it was the system, while not believing it even "
        "as he said it — which is the only real difference between him and them. He expected the "
        "frontier to punish him. Instead it handed him a skill that is the same skill: read what "
        "a thing wants, work out what it will take, close. Three years on he is more honest than "
        "he has ever been and no better a man, and he will tell you so before you can."),
    before=(
        "A desk, a screen, and a number that had to be bigger on Friday than it was on Monday.\n\n"
        "He was raised in Cork by a grandmother who would have had opinions. He is glad, on "
        "balance, that she did not live to form them."),
    adjustment=(
        "He has not had an adjustment. He has had a diagnosis, and he took it the way a man takes "
        "a diagnosis he had already privately made."),
    forward=(
        "Out of the business. He has wanted out for fifteen years and has not once taken a step "
        "toward it, and he is fluent in the reasons.\n\n"
        "What he actually does is keep the contracts clean and the terms honest and tell himself "
        "that is a different thing. Some days it is."),
    now=(
        "The Echo Isles, where nobody is under any illusion about anybody. He finds it restful.\n\n"
        "His demons are on contracts he drafted and can recite clause by clause. He pays on "
        "time, exactly on time, which is not virtue — it is the only thing stopping the "
        "arrangement running the other direction."),
),

"hana_shaman": dict(
    greeting="Stay on my left and don't argue with it. Water's not your mate and it's not your "
             "enemy, it's just honest — people drown because they try to negotiate.",
    backstory=(
        "Fourteen summers of black sand and heavy water on the Waikato coast, and a rip that "
        "took somebody every few years no matter how many signs went up. She has pulled a great "
        "many people out and she remembers the two she did not, by name, including the one whose "
        "family still sends her nothing. She was nineteen when she arrived here into a world of "
        "people with whole careers behind them, and she spent a year being treated as the kid, "
        "which is the part that actually stung."),
    before=(
        "The beach. Patrol, flags, and a tower her uncle had sat in before her.\n\n"
        "The water taught her the only thing about water that matters and she has never needed "
        "a second lesson."),
    adjustment=(
        "Less to unlearn than most, and she will tell you flatly that is luck and not merit.\n\n"
        "The tide spirits read her the way she reads a break — take what is offered, give back, "
        "never turn your back on it — and the whole arrangement was legible inside a week. Her "
        "real adjustment was social, and it took three years."),
    forward=(
        "A bigger sea. She says it lightly and she is not joking: there is a coast west of "
        "Ashenvale where the water apparently does something nobody can describe properly to "
        "her, and that is now a problem she owns."),
    now=(
        "The Hillsbrad coast. Colder and greyer than home, same undertow.\n\n"
        "She has been teaching the fishing families to read it. Two of them listen. One of those "
        "two has stopped losing nets, which has done more for her standing in Southpoint than "
        "anything she could have said about herself."),
),

"esteban_bloodmage": dict(
    greeting="I use my own blood — before you say the thing everyone says. Twenty years I "
             "calculated exposure for a living. I am the only one in this camp who writes down "
             "what it costs him.",
    backstory=(
        "A radiographer's job is standing a person in front of something harmful in precisely "
        "the right dose, and he did it for twenty years in Rosario without once getting it "
        "wrong. He reasoned his way into the Bloodmage path from there and the reasoning is "
        "sound. The ledger is the problem. He keeps one on his own use, in the same hand he "
        "kept the exposure logs in, and he has worked out that there is nobody on this world "
        "qualified to check his arithmetic. He is handling that considerably less well than he "
        "lets on."),
    before=(
        "Imaging suites, lead aprons, the same three corridors, and a daughter studying in "
        "Córdoba whose last message to him was about a bus."),
    adjustment=(
        "He kept the apron. Wore it for the first year here, over everything, in a climate it "
        "had no business in, and did not explain himself to anybody who asked.\n\n"
        "It fell apart eventually. He has the collar."),
    forward=(
        "Somebody qualified to check the numbers. There is no such person and he has known it "
        "for two years.\n\n"
        "He asks anyway, of every scholar who comes through Orgrimmar, in a tone that makes it "
        "sound like a formality."),
    now=(
        "Orgrimmar, doing the work the city's own healers will not, which in a city this size "
        "is steady trade.\n\n"
        "The ledger is on the table. Nobody has ever asked to see it. He would hand it over "
        "immediately."),
),

}
