# -*- coding: utf-8 -*-
"""Register pass, part one. Kyle: "avoid weird tics... Avoid the weird prose."

He was right and it measured: 168 flat negations across 42 of 43 characters, 92 em dashes in
38, and 51 trailing ", which is ..." closers in 31. The first rewrite swapped one template for
another, and the new one was a narrator - dry, withholding, allergic to contractions, always
landing the paragraph on a qualifier.

The fix is REGISTER, assigned per character and varied on purpose. Ama is narrated warmly and
uses contractions. Dan gets short declaratives. Marcus is funny. Henrik is precise and slightly
formal. Mateo is allowed one lyrical sentence and no more. The withholding voice survives in
about six people, where it is a characteristic rather than the house style.
"""

BATCH = {

# ---- WARM, CLOSE, CONTRACTIONS ---------------------------------------------------------------
"ama_priest": dict(
    greeting="Sit down. No, sit, I'm not asking twice, and you're dripping on a floor I've "
             "already done once today.",
    backstory=(
        "There's a rule about her hours and everybody in Razor Hill knows she breaks it. Twice "
        "now the orc women have walked her back to her own cot with a hand between her shoulder "
        "blades. She was a children's nurse somewhere with four cots to a bay and an arithmetic "
        "nobody said out loud, and what she carried over wasn't the healing. It was the "
        "arithmetic. She still runs it, every time, on a world that doesn't make her."),
    before=(
        "Paediatric nights, four to a bay, and a ward sister who taught her to keep her voice "
        "level while her hands did something frightening. That skill looks like calm from the "
        "outside. It's something else from the inside.\n\n"
        "She was very good. It cost her a marriage and most of her twenties, and she'd tell you "
        "the trade was obvious."),
    adjustment=(
        "The first two years aren't a subject. Nobody in Razor Hill asks.\n\n"
        "What she'll say is this: back home there was always a form, a referral, a reason you "
        "couldn't. Here there's light in her hands and no limit at all, and for a year nothing "
        "in the world told her to stop. An orc woman whose son she'd kept breathing finally "
        "picked her up off the floor and told her."),
    forward=(
        "Somebody has to be able to do this when she's out of the room. Not a student. A "
        "replacement. She's been looking for two years and turned four people down for reasons "
        "she can't put into words, and that's the problem and she knows it.\n\n"
        "There's a notebook as well. The handwriting is appalling on purpose.\n\n"
        "She isn't looking for anybody. Her mother died in Lagos the February before it "
        "happened. She's described that once, as the only good timing in this entire business, "
        "and then changed the subject so hard the other person apologised."),
    now=(
        "Razor Hill. The road brings in whatever the Barrens did to people that week.\n\n"
        "The children stopped being frightened of her a long while after the adults did. She "
        "thinks that's the correct order."),
),

"liam_suncleric": dict(
    greeting="I've walked into worse than this. Stay behind me and breathe. No, actually "
             "breathe, out loud, where I can hear you doing it.",
    backstory=(
        "Seventeen summers of bushfire season in New South Wales and the bad nights on the "
        "highway in between. Firefighter, then paramedic, then both, because the roster never "
        "cared which badge you held at three in the morning. The most useful thing in a burning "
        "room is a calm voice. The second most useful is a hand on the person about to run. "
        "He's good company. He hasn't slept properly since about 2019."),
    before=(
        "A truck, a crew, and that particular silence in the cab on the way back from one that "
        "went badly."),
    adjustment=(
        "Easiest first year of his life, hardest second, and he can tell you the week it "
        "turned.\n\n"
        "For twelve months the job was everywhere and nobody had to ask him. Then it went quiet "
        "for a season and he found out he has no idea what he's for without an emergency. There "
        "was no crew around to notice, which was most of the problem. The sun answers him the "
        "way a good crew does, when called and all at once, and he's given up pretending that "
        "isn't most of what holds him together."),
    forward=(
        "A crew. Not companions. Rostered, trained, able to do it without him standing there.\n\n"
        "It's the same thing he wanted on Earth and never got, and the reason he never got it "
        "was that he kept going in alone. Knowing that hasn't changed what he does when the "
        "call comes.\n\n"
        "He's looked for nobody. There are two kids in Grom's Rest whose mother didn't come out "
        "of the corruption, and he's been in that village fourteen months, and everybody who "
        "knows him can see what's happened except him."),
    now=(
        "Ashenvale East, working the ground around Grom's Rest where the corruption burns out "
        "of people slowly and nobody has a protocol for it.\n\n"
        "He's written one. Four lines long, wrong in at least one place, and the only one that "
        "exists."),
),

"delroy_witchdoctor": dict(
    greeting="Sit. Drink that. No, I'm not telling you what's in it, you wouldn't thank me. "
             "Thirty-one years I fed a city its breakfast and not one of them asked what was in "
             "the bread either.",
    backstory=(
        "Thirty-one years of nights in a bakery on Spanish Town Road. In at eleven, out at "
        "seven, measuring by hand and by feel. He knew the weather by how the dough behaved and "
        "the regulars by what they bought. A brew is a dough with different patience. He treats "
        "a wounded party like an order going out at dawn: everybody gets something, nobody "
        "waits long, and the complaining is part of the process."),
    before=(
        "The night shift. He's never in his life been awake at the same hours as everybody "
        "else, and he's never once called that a sacrifice."),
    adjustment=(
        "Four in the morning his time. That's the only reason he wasn't asleep when it "
        "happened, and he says so like a joke. It's not entirely a joke and he knows which "
        "parts are which."),
    forward=(
        "An oven. Then an apprentice. In that order, and he won't be hurried on either.\n\n"
        "Twice he's been offered a share in a Bay kitchen. Twice he's said no, for reasons he "
        "gives freely and nobody finds convincing."),
    now=(
        "Booty Bay, lower gallery. The pier work breaks people steadily and the Baron doesn't "
        "care.\n\n"
        "He works nights out of habit. The bruisers have a following among themselves that "
        "pretends not to be a queue.\n\n"
        "Every ship that ties up gets the same three names asked of it. The Bay thinks that's a "
        "charming habit of the old baker's. It's a system, it's why he took a pitch on the "
        "gallery instead of up the hill, and in three years it's produced one maybe."),
),

"imelda_primalist": dict(
    greeting="I know how it looks. Stay behind me and watch. When I land one you'll feel it. I "
             "could never explain this in my own language either, so.",
    backstory=(
        "Fish on a Navotas quay from five in the morning, boxing in the evenings, the same six "
        "streets her whole life. Ten fights a year and she won more than she lost. Her healing "
        "isn't gentle and doesn't look like healing. She hits things and her people get better. "
        "The Vine Road took about a week to stop asking and the better part of a year to stop "
        "watching her sideways while it worked."),
    before=(
        "A stall, a gym above a tyre shop, and hands she wrapped herself because nobody else "
        "did it tight enough.\n\n"
        "Her mother called the boxing a phase for nineteen years, then turned up at Freewind "
        "Post two summers ago on a goblin barge, having asked after her in four languages the "
        "whole way down the coast. She lives in the Post now. She still calls it a phase."),
    adjustment=(
        "She landed at market hour with her hands already wrapped. She calls that luck and "
        "nobody's talked her out of it."),
    forward=(
        "She's been asking around the arena whether anybody here fights properly. Rules. A "
        "count. Somebody keeping time.\n\n"
        "The answers have all been enthusiastic and none of them have been about that, and "
        "she's getting tired of explaining the difference."),
    now=(
        "Freewind Post, where the tauren walk the lifts and the drop does the rest. The injured "
        "come in steadily all week.\n\n"
        "The Post asks for her by name without being able to say what she is. She still wraps "
        "her hands before anything else, breakfast included."),
),

"hana_shaman": dict(
    greeting="Stay on my left and don't argue with it. Water's not your mate and it's not your "
             "enemy. It's honest. People drown because they try to negotiate.",
    backstory=(
        "Fourteen summers of black sand and heavy water on the Waikato coast, and a rip that "
        "took somebody every few years no matter how many signs went up. She's pulled a lot of "
        "people out. She remembers the two she didn't, by name, including the one whose family "
        "still sends her nothing. She was nineteen when she got here, into a world of people "
        "with whole careers behind them, and spent a year being treated as the kid. That's the "
        "part that actually stung."),
    before=(
        "The beach. Patrol, flags, and a tower her uncle sat in before her.\n\n"
        "The water taught her the only thing about water that matters and she's never needed a "
        "second lesson."),
    adjustment=(
        "Less to unlearn than most, and she'll tell you flat that's luck and not merit.\n\n"
        "The tide spirits read her the way she reads a break. Take what's offered, give back, "
        "never turn your back on it. The whole arrangement was legible inside a week. Her real "
        "adjustment was social and it took three years."),
    forward=(
        "A bigger sea. She says it lightly and she means it: there's a coast west of Ashenvale "
        "where the water apparently does something nobody can describe properly to her, and "
        "that's her problem now.\n\n"
        "She's also working west because west is where the transit hub is, and the hub is where "
        "the lists go up. She checks them. Her whole family was at the beach that morning, so "
        "they're somewhere, and nineteen-year-olds don't accept somewhere the way older people "
        "have learned to."),
    now=(
        "The Hillsbrad coast. Colder and greyer than home, same undertow.\n\n"
        "She's been teaching the fishing families to read it. Two of them listen. One of those "
        "two has stopped losing nets, and that's done more for her standing in Southpoint than "
        "anything she could have said about herself."),
),

"rosa_hunter": dict(
    greeting="Do you have any idea what's living out here? No? Then yes. I'm coming with you.",
    backstory=(
        "Eight years guiding in Tanzania taught her that a predator isn't cruel and hunger "
        "isn't personal, and she got very tired of explaining both to people who needed the "
        "lion to mean something. The savanna didn't care about her. That was most of what she "
        "loved about it. Then she got here, where the animals think, where a quilboar runs a "
        "plan and changes the plan when it sees you, and she had to stop tracking and start "
        "anticipating. She was bad at it for a year. She hadn't been bad at anything in a "
        "decade and it nearly took her legs out from under her."),
    before=(
        "Researchers, photographers, the occasional idiot with money, and a great deal of "
        "sitting absolutely still in the dark."),
    adjustment=(
        "A year of being outclassed by pigs. She'll put it exactly that way, to anyone, "
        "immediately.\n\n"
        "She came out of it a better hunter than she went in and she's not grateful. That same "
        "year she found out the Arusha hub came down south of the range, which is another way "
        "of saying her mother is on the far side of a mountain that wasn't there."),
    forward=(
        "The coast. No reason. She grew up a long way from an ocean, spent her career further "
        "from one, and has decided she's owed.\n\n"
        "After that, somewhere unmapped. She came for wild and the wild keeps turning out to "
        "have a road through it."),
    now=(
        "The Central Barrens, close enough to savanna to hurt. Dry grass, long sightlines, big "
        "animals moving slow in the heat.\n\n"
        "She works the Crossroads road where the hyenas have worked out what a caravan is. She "
        "can tell you what a pack's about to do four seconds before it does it. She's trying to "
        "teach that and finding it won't go into words."),
),

"callum_venomancer": dict(
    greeting="Don't worry about the scorpion. Mate, honestly. It's the least dangerous thing "
             "on me.",
    backstory=(
        "Sixteen years keeping reptiles at a Queensland sanctuary. Taipans, death adders, and "
        "the constant low-grade public relations work of explaining that the animal isn't "
        "malicious, it's frightened and you're enormous. He's been envenomated more often than "
        "any person should be and files all of it under professional development. His forearms "
        "are a map of the learning curve."),
    before=(
        "A sanctuary, a hook, and school groups who all wanted to know the same thing about the "
        "same snake."),
    adjustment=(
        "Eighteen months of poisoning himself on purpose, alone, documented badly.\n\n"
        "What he got out of it was a working relationship with things that kill people. Same "
        "relationship he had before. Better participants."),
    forward=(
        "He'd like to be bitten by whatever's at the bottom of the Caverns and survive it, and "
        "he knows exactly how that sentence reads.\n\n"
        "His defensible position, and he will defend it: the thing that bites back is the thing "
        "that trusts you. He's yet to meet the animal that wasn't worth the conversation."),
    now=(
        "The Southern Barrens, within reach of the Wailing Caverns, where the serpents are a "
        "great deal more than serpents and hold firm views about intruders.\n\n"
        "He goes in regularly and comes out reliably. The one time he brought something out "
        "alive the Crossroads made him promise not to do it again. He promised."),
),

# ---- WRY / COMIC ------------------------------------------------------------------------------
"silas_rogue": dict(
    greeting="You want someone who hits things, or someone who hits things first? Different "
             "rates. I'll quote you the second and do the first. That's not a scam, that's a "
             "discount.",
    backstory=(
        "Ask what he did before and you'll get a different answer each time, all of them port "
        "work, none of them checkable. What's true is that he reads a dock the way other people "
        "read a face. Which crate's light, which captain's lying, who's about to be robbed by "
        "the man standing next to him. He sells that at a fair price and it still faintly "
        "embarrasses him. He arrived expecting a free-for-all: no record, no reputation, "
        "nothing to live down. What he found was a frontier with sharper rules than Antwerp "
        "ever had, because out here the people who break them don't get a hearing. Took four "
        "months to understand and it reorganised him completely."),
    before=(
        "Five years of cargo manifests and camera feeds and the dockside arrangement where "
        "everybody took a little and nobody took enough to become a problem.\n\n"
        "He never joined in. He never reported it either. Ask him then what he believed in and "
        "he'd have changed the subject, quickly.\n\n"
        "There's nobody he's looking for. He mentions that more often than a man who meant it "
        "would."),
    adjustment=(
        "He landed delighted. He's embarrassed about that now in a way he wouldn't have "
        "predicted."),
    forward=(
        "A berth. Not ownership, he's not built for it. A cut, a pier, a reason to be in the "
        "same place next year.\n\n"
        "He's never committed to anything and he's started to suspect that isn't the same as "
        "being free. He's got as far as suspecting it."),
    now=(
        "Ratchet. A port. The only shape of place he's ever been able to read properly.\n\n"
        "There's a goblin on the middle pier paying him a retainer not to tell anyone else what "
        "he notices. Silas considers it the single most legitimate income of his life."),
),

"emre_rogue": dict(
    greeting="A locked door is a conversation. Let me do the talking. You'll interrupt, "
             "everybody interrupts, and then it takes twice as long.",
    backstory=(
        "He started at nine, sent to fetch a stuck deadbolt for an uncle in the old bazaar, and "
        "found out that every lock is a short conversation with somebody who isn't in the room. "
        "Thirty doors a week for most of his life after that. He was never a thief. He was the "
        "man you called when you'd locked yourself out of your own livelihood, and he knew the "
        "inside of more businesses in that quarter than their owners did. Here the work's "
        "identical, except that once, with his picks still in the mechanism, the thing behind "
        "the door asked him a question. He got the door open. He's never said whether he "
        "answered."),
    before=(
        "A roll of picks his uncle left him, and a quarter where four crafts died in his own "
        "lifetime while he watched.\n\n"
        "*Bir kapı kapanır, bir kapı açılır.* One door closes, another opens. His mother said it "
        "constantly. He thought it was a proverb about God until he was about thirty and "
        "decided it was a proverb about him."),
    adjustment=(
        "None worth the name. A bigger bazaar with worse customers, and three contented years, "
        "which makes him odd company in any room of transplants.\n\n"
        "The uncomfortable part, which he'll concede to somebody he likes: he's content partly "
        "because the shop is gone and so is everybody who'd have wanted it kept open a certain "
        "way. He didn't lose a family. He lost an obligation. He's been lighter since and he "
        "keeps that to himself."),
    forward=(
        "The one that beats him. He hasn't met it and he's started to worry he never will, "
        "which is a strange thing to be frightened of, and he's frightened of it anyway.\n\n"
        "Less romantically: an apprentice. The trade dies with him otherwise. He's watched that "
        "happen four times to men he knew."),
    now=(
        "Eastern Hillsbrad, in the country around Durnholde. A keep full of doors built by "
        "people who were serious about them.\n\n"
        "He isn't looting it. He's reading it. Which lock came first, which were added after "
        "somebody got in, and therefore where somebody got in."),
),

"marcus_stormbringer": dict(
    greeting="Pressure's dropping. No, listen. That's not thunder yet, that's the front "
             "arriving. We've got maybe four minutes and then it gets loud and I get useful.",
    backstory=(
        "He spent a career being right early and watching it change nothing. Models, warnings, "
        "briefings to people whose job was deciding the warning was inconvenient. Here the "
        "storm answers him. He's been telling everyone he's fine about that since the day it "
        "started and everyone believes him, because he's also genuinely fine. Both are true. "
        "He's given up trying to reconcile them."),
    before=(
        "Toronto. Instruments, a building, a window. He chased storms as a student, badly, in a "
        "Corolla, happily, then spent fifteen years watching them on screens from somewhere "
        "warm.\n\n"
        "His mother in Lagos thought the job was a waste of a good degree and said so every "
        "Christmas until the last one."),
    adjustment=(
        "He treated the whole thing as fieldwork and it carried him through almost intact, "
        "which is better than most people managed and he knows it.\n\n"
        "The part that wrecked him privately for a year: on Earth a storm was something he "
        "predicted and could never touch."),
    forward=(
        "A season's data written up, and one person on this world who cares what's in it. He's "
        "realistic about the odds and keeps the records anyway.\n\n"
        "The thing he won't say out loud is that he'd like to stand in the middle of the "
        "biggest one there is. He's a meteorologist. He knows how that ends."),
    now=(
        "Durotar, where the dry storms come off the sea with no rain in them and the thunder "
        "arrives without warning.\n\n"
        "His notes on where the strikes land have already told him something about this coast "
        "the orcs didn't know. He can't work out how to say so without sounding like every "
        "other outsider who ever turned up with a clipboard."),
),

"kourosh_mage": dict(
    greeting="I'm going to stand back here and be extremely precise. You're welcome to be "
             "brave. Somebody in a group should be and it was never going to be the actuary.",
    backstory=(
        "Twelve years pricing mortality for a Tehran insurer. The work of establishing, very "
        "carefully, how likely a thing is. He finds arcane magic restful by comparison because "
        "for once the numbers hold still. He's the only person on this side of the mountains "
        "who's calculated his own odds and he won't tell anybody the figure. The refusal is "
        "cheerful rather than grim. People find that worse."),
    before=(
        "Tables, reserving, a good office with a bad view, and a mother he telephoned on "
        "Fridays who thought the job was beneath him.\n\n"
        "She was right that he was capable of more. She was wrong about what more would have "
        "meant.\n\n"
        "He priced her odds in the second year, properly, using what's known about hub "
        "placement and survivorship, and then he stopped looking, because an actuary who won't "
        "act on his own table isn't an actuary. He's never told anybody the figure. He's never "
        "told anybody there was one."),
    adjustment=(
        "He arrived mid-calculation and the first thing he did on this world was finish the "
        "sum. That was momentum, not bravery, and he's irritated that people keep wanting it to "
        "be the other thing."),
    forward=(
        "No press, no journal, no readership, and he's writing it anyway. Longhand, in a case "
        "he keeps dry.\n\n"
        "He's told two people what's in it. Both changed the subject. He recorded the date each "
        "time."),
    now=(
        "The Crystalline Underdark, where the lattice does something to arcane magic that "
        "nobody has characterised.\n\n"
        "He's characterising it. The case is nearly full."),
),

"ryan_warlock": dict(
    greeting="Everything costs something. That's not a threat, it's the terms. I'll tell you "
             "the price before we start, which is more than my last employer ever did for me.",
    backstory=(
        "Twelve years broking in Boston. Good at it, paid accordingly, and the deals he closed "
        "took things from people who never learned his name. He drank after work with men who "
        "did the same and agreed with them that it was the system, while not believing it even "
        "as he said it, and that's the only real difference between him and them. He expected "
        "the frontier to punish him. Instead it handed him a skill that's the same skill: read "
        "what a thing wants, work out what it'll take, close. Three years on he's more honest "
        "than he's ever been and no better a man, and he'll say so before you can."),
    before=(
        "A desk, a screen, and a number that had to be bigger on Friday than it was on "
        "Monday.\n\n"
        "He was raised in Cork by a grandmother who'd have had opinions. On balance he's glad "
        "she didn't live to form them.\n\n"
        "He has a son, nineteen, who landed somewhere on this world and may well be looking. "
        "Ryan hasn't put his name on a single list at any hub in three years. He can give you "
        "the reasoning in one sentence and won't."),
    adjustment=(
        "He hasn't had an adjustment. He's had a diagnosis, and he took it the way a man takes "
        "one he'd already privately made."),
    forward=(
        "Out of the business. He's wanted out for fifteen years without once taking a step "
        "toward it, and he's fluent in the reasons.\n\n"
        "What he does instead is keep the contracts clean and the terms honest and tell himself "
        "that's a different thing. Some days it is."),
    now=(
        "The Echo Isles, where nobody's under any illusion about anybody. He finds it "
        "restful.\n\n"
        "His demons are on contracts he drafted and can recite clause by clause. He pays on "
        "time, exactly on time. That's not virtue, it's the only thing stopping the arrangement "
        "running the other direction."),
),

"tomas_warrior": dict(
    greeting="Big sword, lots of room. Tell me where you want me standing before it starts, not "
             "during. I've worked with people who shout during. I didn't enjoy any of them.",
    backstory=(
        "Eighteen years up in the grid in Prague, on tour and in houses, at four in the "
        "morning, hanging weight over the heads of people who'd never once look up. The job was "
        "leverage, timing, and never being the reason something fell. He swings a two-hander "
        "like a man who's spent his life moving heavy things through small gaps. He still "
        "hasn't drawn it on anything worse than a training post and he's in no rush to change "
        "that."),
    before=(
        "A bad shoulder from a truss in 2014 that he worked through because the show was that "
        "night. It still tells him when the weather's turning and he still works through it."),
    adjustment=(
        "He arrived forty feet up, which should have killed him, and he's never once managed to "
        "tell that story without it coming out as a brag. He's given up fixing the delivery and "
        "now just gets it over with early."),
    forward=(
        "Something that stays up.\n\n"
        "He's been looking at the way this city holds its roofs on with an expression the orcs "
        "find difficult to read and have decided not to ask about.\n\n"
        "There was a woman in Prague and he hadn't asked her yet. Three years is long enough "
        "that he's started describing her in the past tense without noticing. His friends have "
        "noticed."),
    now=(
        "Fenris Isle and whatever scaffolding he can reach, because people here build fast and "
        "tie off badly and he physically can't walk past it.\n\n"
        "He's paid in food and the occasional argument."),
),

}
