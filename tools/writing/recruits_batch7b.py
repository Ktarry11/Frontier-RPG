# -*- coding: utf-8 -*-
"""Register pass, part two: the plain/clipped voices and the formal/precise ones.

Two registers, deliberately unlike each other and unlike part one. The plain group speaks in
short declaratives and almost never qualifies. The formal group is careful, slightly stiff,
chooses its words - and is allowed subordinate clauses, because precision is the characteristic
and the dry voice belongs in SOME mouths. The error the first draft made was giving it to all
forty-three.
"""

BATCH = {

# ---- PLAIN / CLIPPED -------------------------------------------------------------------------
"dan_warrior": dict(
    greeting="I'll go first. Don't thank me. It's the job and somebody has to have it.",
    backstory=(
        "Twenty-two years on a Sheffield steel floor. Heat, noise, a four-man crew and the kind "
        "of trust you can't talk about without sounding daft. Then the plant shut. Then the "
        "world ended, which he'll tell you came as less of a shock than the first one. He's a "
        "shield. That's the whole arrangement. He stands in front and the rest of you get on "
        "with it."),
    before=(
        "The floor. Shift work. A crew that went for a pint on Fridays for nine years "
        "straight.\n\n"
        "The plant closed in 2019. He was out of work for four years and most of that is a "
        "subject he'll walk away from."),
    adjustment=(
        "He stopped being idle. He'd call that the entire adjustment and he's wrong, but he's "
        "wrong in a direction that works."),
    forward=(
        "A crew. Four men, long shifts, a Friday.\n\n"
        "He's been assembling one out of whoever's in the tavern and it isn't the same and he "
        "won't say so.\n\n"
        "His daughter was in Leeds. The lists at the hub are alphabetical and he's got to the "
        "D's about forty times."),
    now=(
        "Southpoint, on the Hillsbrad coast. A working town. He understands working towns.\n\n"
        "He takes the front of whatever goes out and he's never once asked to be paid "
        "differently for it."),
),

"fiona_witchhunter": dict(
    greeting="I've read your file. Not yours, obviously. I'm saying that's the habit and you'll "
             "want to know about it before we work together.",
    backstory=(
        "Nine years in fraud investigation in Dublin. The whole trade is noticing the one entry "
        "that doesn't fit and then being unbearable about it until somebody checks. She was very "
        "unpopular and quite often right. The thing that hunts people here leaves a trail of "
        "the same shape as a cooked ledger: too neat, and neat in the places nobody looks."),
    before=(
        "Spreadsheets, interviews, and a reputation among colleagues that she earned and never "
        "enjoyed."),
    adjustment=(
        "Her first year was a filing exercise. She catalogued every corrupted thing she met and "
        "the notebook is now more use than she is.\n\n"
        "Somewhere in the second year she worked out she'd been treating a war as a casework "
        "backlog. That one landed hard."),
    forward=(
        "Finish the catalogue. Hand it to somebody who'll act on it. Both halves matter and the "
        "second is the one she keeps failing at.\n\n"
        "She's had the same conversation with the Argent Dawn four times. She takes minutes of "
        "those too."),
    now=(
        "Western Plaguelands. The corruption's patterned here and nobody's mapped the "
        "pattern.\n\n"
        "She's mapping it. Three hundred pages, cross-referenced, and she carries the whole "
        "thing on her back because she won't leave a copy anywhere she can't see."),
),

"eino_barbarian": dict(
    greeting="Cold doesn't bother me. Go on. Say something about the sauna. Everybody does and "
             "I've stopped minding.",
    backstory=(
        "Twenty-six years felling timber in Lapland. Six months of dark a year, machinery, and "
        "nobody to talk to for days at a stretch. The axe is the same axe. The cold's the same cold. He "
        "talks about as much as the work required. People read that as unfriendliness for the "
        "first month and then stop."),
    before=(
        "Timber, a machine, and a stretch of forest the size of a county."),
    adjustment=("Nothing to speak of. The trees here are bigger."),
    forward=(
        "He'd like to see the north of this world. Not for any reason he can give. He's been "
        "told Northrend's worse than Lapland and that's done nothing to put him off.\n\n"
        "His brother worked the same ground and they haven't spoken since before. Eino's "
        "mentioned this twice in three years, both times in passing, both times to nobody in "
        "particular."),
    now=(
        "Winterspring. Snow, dark, and timber the size of towers.\n\n"
        "The Everlook crews hire him by the season and have given up trying to make "
        "conversation. He prefers the arrangement and thinks they do too."),
),

"junseo_reaper": dict(
    greeting="Twelve hours a day for nine years, standing up, in the same two square metres. "
             "Whatever this is, it's easier.",
    backstory=(
        "Nine years on a Busan line, night shift mostly, the same two motions ten thousand "
        "times a day. His body learned things his mind never had a say in. Here that's a "
        "weapon: he moves without deciding to and it's fast, and the only thing that frightens "
        "him about it is how little of it he chooses."),
    before=(
        "A line, a shift bell, and two square metres of floor he could draw from memory.\n\n"
        "He sent money home every month for nine years. His parents are in Busan or they're "
        "not. The hub for that city came down in the far north, past the ice, and the "
        "arithmetic of that is not something he's prepared to do out loud."),
    adjustment=(
        "The first year he worked. Anything, for anyone, as many hours as there were.\n\n"
        "The second year somebody made him sit down and he found out he had no idea what to do "
        "with a day. He'd be the first to say that's a worse problem than the first year's."),
    forward=(
        "He wants to be slow at something. Not good. Slow. He's picked woodcarving because it "
        "can't be hurried and he's catastrophically bad at it.\n\n"
        "That's the point. He's explained this twice and neither person understood."),
    now=(
        "Thousand Needles, the high mesas, where the only way up is a lift and the lift takes "
        "its time.\n\n"
        "He runs the baskets. It's two motions, ten thousand times. He's aware of the joke and "
        "he keeps the job anyway."),
),

"ivan_warrior": dict(
    greeting="Stand where I can see you. If you're behind me I'll assume you're the enemy and I "
             "move faster than I apologise.",
    backstory=(
        "Eleven years a tram driver in Novosibirsk. It is nobody's idea of a story and it is "
        "the whole reason he's good at this. Eleven years of a heavy thing on rails with other "
        "people's children stepping off kerbs. He never hit one. He maintains a two-handed "
        "weapon the same way: slow start, committed middle, and knowing exactly how long it "
        "takes to stop."),
    before=(
        "A cab, a route, and the same four stops in the dark every winter morning for eleven "
        "years."),
    adjustment=(
        "He expected to be useless. He's a tram driver. What he found was that nobody here "
        "knows how to commit to a movement and then stop it, and that it's apparently a rare "
        "skill, and he's said out loud more than once that this world has very low standards."),
    forward=(
        "A route. He's asked three separate caravan masters whether anybody runs a fixed "
        "schedule and all three laughed.\n\n"
        "He's going to keep asking. He thinks they're the ones being unreasonable and he may "
        "well be right."),
    now=(
        "Orgrimmar's Valley of Strength, where the traffic's worse than anything Novosibirsk "
        "managed and nobody's in charge of it.\n\n"
        "He's begun directing it, unasked, at the worst hour. The orcs have started doing what "
        "he says."),
),

"marta_tinker": dict(
    greeting="Give it here. No, give it here. You've been hitting it, haven't you. People always "
             "hit it.",
    backstory=(
        "Nineteen years of industrial sewing machines in a Łódź plant, which means nineteen "
        "years of being the only person in the building who could tell what was wrong from the "
        "sound. Management called her when a line stopped. They never once called her anything "
        "but by her first name. Goblin engineering is the same noise with more smoke, and she "
        "loves it in a way she'd be embarrassed to have written down."),
    before=(
        "Forty machines, one toolkit, and a plant floor she could diagnose from the "
        "doorway.\n\n"
        "Her husband worked the other shift for fifteen years so one of them was always home "
        "with the boys. The boys are grown. The husband was on his way to work."),
    adjustment=(
        "Three weeks, and she'd argue the three weeks were mostly about the language.\n\n"
        "A machine's a machine. She was repairing goblin gear for money before she could ask "
        "where the toilet was."),
    forward=(
        "Her own bench, her own sign, and nobody above her on a floor plan.\n\n"
        "She's been quoted a price for a Ratchet pitch. She can afford it. She's found four "
        "reasons to wait and knows all four are the same reason."),
    now=(
        "Ratchet, where everything is broken and the goblins charge for the privilege.\n\n"
        "She undercuts them by a third and fixes it properly. There's a goblin on the south "
        "pier who's threatened her twice and sent her work three times."),
),

"pavlo_knight": dict(
    greeting="Give me the line and I'll hold it. Tell me how long. I'd rather know.",
    backstory=(
        "Sixteen years a Lviv schoolteacher, history, fourteen-year-olds. The work is standing "
        "in front of a room that would rather be anywhere else and keeping it together by "
        "presence alone. He does the same thing in a shield wall and finds it considerably "
        "easier, because a gnoll at least wants something comprehensible."),
    before=(
        "A classroom, a curriculum he disagreed with, and thirty children a year he mostly "
        "managed to reach.\n\n"
        "He taught the same four wars every spring. He's noticed nobody here needs a history "
        "teacher and it's taken most of three years to stop being wounded by that."),
    adjustment=(
        "Badly, and he's open about it. For a year he looked for a school.\n\n"
        "There isn't one. There's a lot of work for a man who'll stand still while something "
        "comes at him, and he took it, and the taking was a small grief he's never dressed up "
        "as a calling."),
    forward=(
        "He's still going to teach. Six children in Southshore, twice a week, whatever he can "
        "remember of a world that isn't coming back.\n\n"
        "Two of them have stopped attending. He's decided not to ask why."),
    now=(
        "Southshore, holding the line against whatever walks down from the Plaguelands.\n\n"
        "It's steady work and he's good at it and he'd swap it tomorrow."),
),

"pieter_guardian": dict(
    greeting="I'll take the hits. That's not courage, it's arithmetic: I'm the one wearing the "
             "armour.",
    backstory=(
        "Twenty-eight years in Rotterdam port safety. Harnesses, exclusion zones, and the "
        "deeply unglamorous business of nobody dying today. He's been shouted at by thousands "
        "of men in a hurry and outlasted all of them. He stands in front of a party now and "
        "runs the same arithmetic he always has. A precaution costs less than the thing it "
        "prevents, every time, on any world."),
    before=(
        "A clipboard, a hard hat, and a reputation as the most tedious man on the dock."),
    adjustment=(
        "Instant, and he's slightly ashamed of how instant. His entire profession turned out to "
        "be directly applicable to a world with monsters in it, and his colleagues on Earth "
        "would have found that hilarious."),
    forward=(
        "Rules that outlive him. He's written a set for the Bay's pier work and the Baron has "
        "ignored all of them.\n\n"
        "He submits them again every season. Four seasons now."),
    now=(
        "Booty Bay, the piers, where men work above water with no harness and the Baron's "
        "position on this is that they chose the job.\n\n"
        "Pieter has pulled nine men out in three years. He keeps the number because somebody "
        "should."),
),

# ---- FORMAL / PRECISE ------------------------------------------------------------------------
"henrik_mage": dict(
    greeting="Before we begin: what is the actual objective? I have found that parties rarely "
             "agree, and discover it halfway through.",
    backstory=(
        "Twenty-one years a structural engineer in Copenhagen. The discipline is being certain "
        "that a thing will hold before anybody stands on it. Arcane magic "
        "rewards that temperament more than it rewards boldness, a fact he regards as the "
        "single most underappreciated feature of this world. He is precise in conversation to "
        "a degree people find either restful or maddening, and he has never managed to predict "
        "which."),
    before=(
        "Load calculations, tolerances, and a career of being the person who said no to "
        "architects.\n\n"
        "His wife taught at the university. She had a nine o'clock lecture and the Integration "
        "arrived at ten past. He has worked out, with some care, that she would therefore have "
        "been in a lecture theatre, and he has stopped the calculation precisely there, every "
        "time, for three years."),
    adjustment=(
        "Twenty months, documented. He treated himself as a structure under an unfamiliar load "
        "and tested accordingly.\n\n"
        "The resulting notes are the most useful document on arcane tolerance anyone has "
        "produced here, and he regards them as preliminary, and he will argue the point."),
    forward=(
        "A standard. Not a spell and not a discovery: a published figure that other casters "
        "can work to, so that the next person who tries this does not have to find the limit "
        "with their own body.\n\n"
        "He has calculated his own limits to four significant figures and he does not "
        "approach them, which is the whole of his method and the reason he is still alive."),
    now=(
        "Dalaran's outskirts, as close to the shattered workings as the wards permit, where "
        "the arcane behaves in ways that would be unreproducible anywhere else.\n\n"
        "He measures. He has filled eleven books and will tell you the eleventh is the only "
        "one worth reading."),
),

"esteban_bloodmage": dict(
    greeting="There is a price. I will name it before we proceed, and I would ask you not to "
             "pretend afterwards that I did not.",
    backstory=(
        "Nineteen years a Valparaíso surgeon. The trade consists of doing a violent thing for a "
        "good reason, with absolute precision, while the person on the table trusts you "
        "entirely. Blood magic is the identical proposition with the formalities removed. He "
        "finds the honesty of it a relief and the company it attracts a continual "
        "disappointment."),
    before=(
        "Theatre lists, a scalpel, and twenty years of consent forms he insisted on explaining "
        "properly even when nobody wanted him to."),
    adjustment=(
        "He had no crisis. He had an inventory, and he conducted it in the first month, and "
        "found the skill transferred entire.\n\n"
        "What he underestimated was how much of his old restraint had been supplied by the "
        "hospital rather than by him. He discovered this in year two and did not enjoy the "
        "discovery."),
    forward=(
        "A standard of practice, written down, binding on anyone who claims the discipline. "
        "There is nothing of the kind on this world and the absence appals him.\n\n"
        "He has drafted eleven clauses. He expects no one to adopt them and continues to "
        "draft."),
    now=(
        "Stranglethorn's interior, where the Bloodsail will pay anything for a man who can keep "
        "the injured alive and who does not ask about the injuries.\n\n"
        "He asks. Every time, on the record, and then treats them anyway."),
),

"minh_chronomancer": dict(
    greeting="A moment. I would like to establish the sequence of events before we add to it.",
    backstory=(
        "Twenty-three years of air traffic control at Tân Sơn Nhất. The profession is holding "
        "forty futures in your head simultaneously and choosing the one in which nobody dies. "
        "Time magic asked him for exactly that and nothing he had not already done for two "
        "decades on three hours of sleep. He is the calmest person in most rooms and it is "
        "entirely professional conditioning rather than temperament."),
    before=(
        "A dark room, a scope, and the discipline of never once letting your voice carry what "
        "your pulse is doing.\n\n"
        "He has a daughter who was studying in Melbourne. Two hubs, two continents, and a "
        "survivable set of assumptions. He has permitted himself the survivable set."),
    adjustment=(
        "He was on shift, and he has said that the handover was the hardest part, and the "
        "people who hear that assume he means the Integration. He means the handover."),
    forward=(
        "He would like one hour in which nothing is his responsibility. He has not had one "
        "since 2003 and he is beginning to suspect the problem is not the schedule.\n\n"
        "In the meantime he keeps the gate, because nobody else will, which is precisely the "
        "reasoning that got him here."),
    now=(
        "The Caverns of Time approach, where the sequence of events is negotiable and almost "
        "nobody understands how dangerous that is.\n\n"
        "He has appointed himself to the approach. No one asked him to. He has made a rota of "
        "one."),
),

"haruto_runemaster": dict(
    greeting="The form matters. Not for ceremony. A rune cut carelessly fails carelessly, and "
             "it fails on whoever is standing closest.",
    backstory=(
        "Thirty-one years of calligraphy in Kanazawa. The discipline is a single stroke, studied "
        "until the hand no longer requires the mind. He trained under a man who corrected him "
        "for eleven years before offering praise. Runework on this world responds to exactly "
        "that discipline and he was the only person who already had it, a circumstance he "
        "describes as luck and nobody who has watched him work believes."),
    before=(
        "Ink, paper, a master who died in 2017, and a studio with four students in it.\n\n"
        "He never married. He has said that the work was a full occupation and he has said it "
        "in a tone that closes the subject."),
    adjustment=(
        "He asked to be taught. That was the whole of it, and it worked, and he is aware that "
        "almost no transplant tried it.\n\n"
        "The tauren who agreed is dead now. Haruto finished the curriculum alone, from notes, "
        "and considers the result incomplete in ways he can specify."),
    forward=(
        "Students. Four would be correct. He has two and is not inclined to lower the "
        "standard to reach four.\n\n"
        "He is also assembling a reference of every rune form he has recorded, in the hope "
        "that the discipline outlasts the shortage of teachers. The hope is thin and he keeps "
        "working."),
    now=(
        "Felwood, where the corruption has put something into the old rune-stones that nobody "
        "can read.\n\n"
        "He is copying them before they finish degrading. It is slow, unrewarded, and the only "
        "record that will exist."),
),

"tarek_templar": dict(
    greeting="I will go where I am needed and I would prefer you tell me plainly where that is. "
             "I have little patience left for the other kind of instruction.",
    backstory=(
        "Fourteen years a civil engineer in Aleppo, then four years of watching the work "
        "undone, and then a long time in places that were not home. He built water systems. He "
        "watched them shelled. He rebuilt two of them. The faith he carries is not comfortable "
        "and he does not present it as comfort: it is the position he arrived at after the "
        "evidence was in, and he will discuss it, at length, with anyone prepared to be "
        "serious."),
    before=(
        "Pipes, pumps, pressure, and a city he can still draw from memory in a way he has "
        "stopped doing on purpose.\n\n"
        "His brother's family reached Germany in 2016. The Integration found them there, which "
        "means a different hub, a different continent, and a set of lists he has walked to "
        "four times."),
    adjustment=(
        "He is the rare case for whom this world was an improvement, and he states it plainly, "
        "and it silences rooms.\n\n"
        "Here the thing destroying the water is a visible enemy that can be fought. He has "
        "said that he waited twenty years for an enemy that simple."),
    forward=(
        "A well that is still standing in ten years. He has sunk three. One has failed "
        "already.\n\n"
        "He has stopped describing this as rebuilding. He calls it building, which is a "
        "distinction he arrived at slowly and holds firmly."),
    now=(
        "The Barrens, where the water is the whole argument and the quilboar know it as well "
        "as anyone.\n\n"
        "He works the wells on the Crossroads road. The orcs have offered him a title twice. "
        "He has declined twice, politely, and given no reason either time."),
),

"kesten_the_catalogued": dict(
    greeting="Kesten. Formerly a serial number. I have selected the name and I would ask you to "
             "use it.",
    backstory=(
        "He was an archivist in Tallinn for twenty-six years, and then he was a number in a "
        "Scourge ledger, and then he was neither. What came back has the archivist's habits and "
        "none of the archivist's warmth, and he is the first to say so. He catalogues. It is "
        "the only continuity he has and he defends it the way other people defend a family."),
    before=(
        "Stacks, acid-free boxes, and the quiet conviction that a thing unrecorded has not "
        "quite happened.\n\n"
        "There was a wife. He has her name written down because he no longer trusts himself to "
        "hold it, and he regards the written record as sufficient, and nobody who hears him say "
        "so finds it sufficient at all."),
    adjustment=(
        "The question does not apply in the usual form. He did not adjust to this world. He "
        "returned to it, partially, and has been taking inventory of what came back ever "
        "since.\n\n"
        "The inventory is the document he values most and he will not show it to anyone."),
    forward=(
        "A complete record of the Scourge's working, written by something that was inside it. "
        "He is aware of what he is for. He has decided to be for that deliberately rather than "
        "by default.\n\n"
        "He expects to finish nothing. The expectation has never once slowed him."),
    now=(
        "Tirisfal, close to the ground he was processed on, where the ledgers are still legible "
        "if you know the hand.\n\n"
        "He knows the hand. He has been reading his own entry for two years and has never told "
        "anyone what it says."),
),

"stelios_necromancer": dict(
    greeting="I handled the dead for nineteen years before any of this. The difference now is "
             "that they occasionally have something to add.",
    backstory=(
        "Nineteen years a Thessaloniki funeral director. The trade is composure, paperwork, and "
        "being the steadiest person in the worst room of somebody's life. He is unshockable in "
        "a way that has nothing to do with callousness, and his profession prepared him for "
        "this world considerably better than anybody's did who arrived with a weapon."),
    before=(
        "Arrangements, families, and the particular courtesy of a man who has told four "
        "thousand people the worst thing they will hear that year.\n\n"
        "The business was his father's. He has said that inheriting it was not a choice and "
        "that he would have chosen it, and that both of those are true, and that people find "
        "the combination difficult."),
    adjustment=(
        "He was calm throughout and he is tired of being praised for it. Composure was his "
        "occupation for nineteen years. Praising him for it is like praising a baker for being "
        "awake."),
    forward=(
        "Rites. Proper ones, for the transplants who die here with nobody who knows their "
        "language.\n\n"
        "He has conducted one hundred and forty. He keeps a register, and he has written to "
        "every hub he can reach asking that the names be posted, and three have replied."),
    now=(
        "The Undercity, where the dead are a civil service and somebody with his background is "
        "either a gift or an affront depending on who is asking.\n\n"
        "He does the paperwork. He is extremely good at the paperwork, and he has used it four "
        "times now to find out who a body was before it stopped being anyone."),
),

}
