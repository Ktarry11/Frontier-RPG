#!/usr/bin/env python3
"""Rewrite the Stranglethorn talk-quest topics (world/quest_dialogue_stranglethorn_*.py) in plain voice.

    PYTHONPATH=. python3 tools/stv_topic_voice.py            # check only
    PYTHONPATH=. python3 tools/stv_topic_voice.py --write    # check, then rewrite the three topic tables

Part of the Stranglethorn writing pass (Kyle, 17 Nov 2026), the same bar as tools/stv_quest_voice.py. The quest
and topic ids are unchanged, because a talk quest completes on its topic ids; only labels and responses change.
The notes above QUEST_TOPICS in each file are kept; the table below them is rewritten from TOPICS here.
"""
import contextlib
import importlib
import io
import os
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

#: {zone file suffix: [(quest_id, who (a comment), {topic_id: (label, response)})]}
TOPICS = {
    "central": [
        ("stvc_zultamo_courses", "Gatehouse Broker Zul'tamo, Gurbashi Arena. Old, formal, light troll speech.", {
            "the_one_way": (
                "Why does the ring only run one way?",
                "You're standin' where every visitor stands, and seein' what every visitor sees, which looks like a "
                "choice. Look at da sand at your feet. Da ring opens left and right, but one of dose ways ends forty "
                "paces along at a rock face nobody ever cut. People say walkin' it anticlockwise is tradition, but "
                "it's really just masonry. You can't go da other way because it was never built, and somebody "
                "decided dat with a chisel before my grandfather was born."),
            "the_uncut_faces": (
                "Who left the two faces uncut?",
                "A mason, not a priest or a chief. Da gatehouse keeps da old course records, and dey show a mason's "
                "mark with no name. Da ring was laid out with eight openings, and two were never cut. Think what dat "
                "cost. You've dug da ring, you've got da stone out and da men standin' dere, and you stop two "
                "openings short, so every fighter after you comes down da stair with no choice of direction. Why a "
                "man would work dat hard to take a choice away from strangers, I don't know, and I won't make "
                "somethin' up for you."),
            "the_word_for_sand": (
                "Your word for the sand is their word for the river.",
                "Say dat again. You're right, and da attache is right, and I've been signin' dat word on paper since "
                "I was nine without ever hearin' it. It ain't a word for sand or for water. It's a word for what a "
                "thing gets poured into, a bed dat holds somethin' while it passes through. Their river has one, and "
                "my arena floor is one. Da same people cut a stair you can only climb one way, a terrace you can only "
                "enter from below, and a ring you can only walk one way round, and dey called da middle of all three "
                "by da same word. Dat's as far as I can take you. Da rest is south, under da water, in a hall my "
                "family stopped visitin'."),
        }),
        ("stvc_sluice_book", "Sluice-Keeper Pate, Tarren Mill. Careful, plain, a man who checks.", {
            "the_board_and_the_book": (
                "What's in the book?",
                "Water heights, one a day and more during a melt, with the date beside each. That's all of it, and "
                "it's taken three men's working lives. I've got twenty-two years in there, and the front pages are "
                "in the hand of the man who had the crank before me and taught me to read the boards. People think "
                "the skill is knowing when to drop the gate, but any fool can drop a gate. The skill is writing down "
                "a number every day for twenty-two years when nothing happens, so that when something does, you can "
                "say how far off normal it's gone instead of just having an opinion."),
            "what_the_knots_say": (
                "What do the jungle's cords say?",
                "They say a waterfall rose and stayed up, and I believe it for one reason. Whoever knotted these "
                "wasn't trying to prove anything. A man faking readings makes a clean line. These wander by a knot "
                "or so from day to day, the way real water does, and then in one month they all step up together and "
                "never come back down. A river rises with more rain and falls when the rain stops. If it rises and "
                "stays up, something new is feeding it. In twenty-two years I've never found a third answer."),
            "the_other_book": (
                "Why do you keep a second book?",
                "Because the first one stopped working, and I'll be plain about when. Three years ago the sky "
                "changed. After that my old book couldn't predict the race any more. The melt came at the wrong "
                "time, the dry month came twice, and a man who'd been right about his own water for nineteen years "
                "was suddenly guessing. So I started a second book, dated from the change, and I keep the two apart. "
                "Here's the rest, because you'll hear it worse from someone else. I don't trust any measurement "
                "taken in the last three years, mine or the ones you brought, because I can't check them against "
                "anything. That's not an accusation. It bothers me as much as it should bother you."),
        }),
        ("stvc_scrip_second", "Scrip, Booty Bay. Nine years old, quick, stubborn.", {
            "the_crocolisk_theory": (
                "So you still think it's gorilla?",
                "I think it CAN'T be croc, which isn't the same thing. Bexx says it's not the same. Look, a croc is "
                "long and a drum is round. You can't get a round thing out of a long thing without wasting most of "
                "it, and nobody down here wastes anything. Have you MET the Bay? A gorilla's chest is round already. "
                "That's not me wanting to be right, that's just the shape it is."),
            "who_told_you_that": (
                "Who told you about the drums in the first place?",
                "It was Hobb. He's nine and a half and he says it like it's a rank. But I've been thinking, and Hobb's "
                "never been up the road either. Bruiser Kolk counts us at the gate, and it's the same four of us "
                "every day, so none of us has ever been a mile out of this cove. So where did Hobb get it? Off a "
                "sailor, who got it off another sailor. That's just a story with extra sailors in it. And mine's the "
                "same, isn't it? Mine's just got one less sailor."),
            "what_he_would_do": (
                "What would you do if you could get up the road?",
                "I'd measure it properly, with a string, and bring the string back so I wasn't just saying a number. "
                "Then I'd ask the drum crew what they oil it with. Leather needs oil, like boots, so a drum that big "
                "must drink loads of it, and whoever sells them the oil has a book that says how much. A book "
                "doesn't care who's asking. That's the bit nobody does. Everyone argues about what the drums are "
                "made of, and the oil seller already knows and would tell you for nothing."),
        }),
    ],
    "north": [
        ("stn_nothing_they_have_fought_climbs", "Drillmaster Ukko, Grom'gol. Orc, gruff and fair; the camp isn't.", {
            "what_climbs": (
                "What out here climbs?",
                "Everything worth worrying about. Thornback apes come down a trunk faster than you can climb a "
                "ladder. Coilvine pythons live in the canopy and drop the last few feet. A greenpelt runs up a "
                "buttress root like it's a staircase. You were taught a fight has a front, two flanks and a back. "
                "This jungle has a roof as well, and nobody on that airship was given a word for it."),
            "what_the_drill_is_for": (
                "What's the drill actually for, then?",
                "Looking up, and that's all I added. I used to drill a battle line: shields even, spears level, hold "
                "your ground and let them break on you. A line is for open fields, and there are no fields in "
                "Stranglethorn. So now I drill the glance upward, twice a minute, every minute, until a recruit does "
                "it in his sleep and resents me for it. The ones who resent me live, and I've made peace with that."),
            "who_you_get": (
                "Who does the airship give you?",
                "Whoever's standing on the berth stair when it leaves. I had a sergeant who said your sort couldn't "
                "be taught the canopy. He was wrong, but he wasn't stupid, and that's the uncomfortable part. You "
                "can be taught anything, but nobody can assume what you know. I don't ask a recruit where he's from. "
                "I ask what he's stood under, and most of you have stood under nothing but open sky, and sky doesn't "
                "drop on a man. Half this camp says that a lot less kindly than I just did. I used to correct them, "
                "but I got tired."),
        }),
        ("stn_what_the_pens_know", "Beast-Handler Kozza, Grom'gol. Troll, full dialect, unsentimental.", {
            "the_difference": (
                "Tame and fed. What's the difference?",
                "Tame is a promise you made up and told yourself da animal agreed to. Fed is a trade, and da animal "
                "knows it. She knows what she gets and when, and as long as dat holds, she'll let you stand in da "
                "pen with her and won't open you up. Da day it stops holdin', she ain't betrayin' you, mon. She's "
                "just done tradin'. Every handler who ever got torn open thought he had a promise."),
            "the_raptors_on_the_road": (
                "What do your birds hear out on the road?",
                "Dey go quiet, da same day every week, from mid-mornin', and dey all face da same way, up da road "
                "toward da crag. Quiet ain't fear. A predator makes dem loud and sends dem at da rail. Quiet is what "
                "dey do for somethin' dey've looked at and decided ain't theirs to fight. Somethin' with a lot of "
                "feet, movin' slow, goin' uphill at da same hour every week, like it has a man with a book countin' "
                "it out. Dat's all I've got."),
            "what_she_will_not_do": (
                "What won't you do?",
                "Dere's three tings. I won't name one of dose birds. I won't put a bird's opinion in front of da overseer as "
                "fact, because she'll ask for a number and den I'm on paper bein' wrong. And I won't let dis camp "
                "use my pens as a watchtower. Da day dey do, da feed stops bein' feed and becomes a line in a "
                "ledger, and somebody upstairs can always cut a line. Den I've got hungry raptors and a camp dat's "
                "surprised about it."),
        }),
        ("stn_two_roosts_one_ledger", "Wind-Rider Ghulrak, Tarren Mill. Orc, dry, flown everything twice.", {
            "fences_from_the_air": (
                "What does Hillsbrad look like from up there?",
                "Fences, all of it. You don't see how much of a country is fences until you're above it with nothing "
                "else to look at. Every one of them was argued over. Men have been buried over which side of a fence "
                "a cow was standing on, and the fence is still up and the men aren't. Your goblin's route crosses "
                "hundreds of them in the last hour of the flight, and not one will be moved for him."),
            "why_not_bats": (
                "Why not fly bats the whole way?",
                "Because a bat doesn't need to see the tower and a wyvern does. A bat comes in by ear, through cloud "
                "and rain and dark, and doesn't care whether anyone lit anything. A wyvern won't land on a roost it "
                "can't see, and over that middle stretch there's nothing to see, so the bird keeps flying. A bird "
                "that keeps flying after it's spent ends up in the water. That's why I want the Forsaken tower lit. "
                "Not for the route, for the bird."),
            "what_the_jungle_sends_north": (
                "Who comes north on your tower?",
                "Couriers, mostly, and lately you lot. You come up out of that jungle asking for places by names "
                "that aren't on any map I own, and I set you down at the mill, and you stand in the yard staring at "
                "a waterwheel like somebody's moved your house. Three years, and you still ask. Half the garrison "
                "here will tell you the fences came down the year the sky changed, but they didn't. They came down the "
                "year the Syndicate worked out nobody was watching. But a man would rather blame the sky than a "
                "neighbour he has to keep living beside. I charge you all the same rate, if that's any comfort."),
        }),
    ],
    "south": [
        ("bb_kundaraz_means", "Pilot Zan'rek, Booty Bay. Troll, proud, has carried this alone a long time.", {
            "the_name": (
                "What does Kundaraz mean?",
                "Da water comin' up. Not da sea, because da sea has its own word and it ain't a nice one. Kundaraz is "
                "water risin' to where you put it, because you put it dere. Everyone in dat port calls it da ruin, "
                "and when dey want to be polite dey call it da drowned place, which is da same insult in a nicer "
                "hat. A drowned place is somewhere somethin' happened to. Zul'Kundaraz is named for da thing "
                "happenin'. Da masons signed dere work in da name, and den da water rose over da signature. I think "
                "dey'd have found dat funny."),
            "three_cities": (
                "Three cities, one way of building. What does that mean?",
                "It means all three were cut by people taught da same way, who didn't argue with it. Da courts in da "
                "north nobody can read, da arena in da middle still full of shoutin', and ours. Three sets of hands, "
                "hundreds of years apart, and one measure through all of dem. Da rule you carried north would fit "
                "any of da three. Da newest is da biggest, and it's da one under salt water, and everybody gets dat "
                "backwards. Dey didn't get worse at buildin'. Dey got bolder, and den dey were done."),
            "what_the_sluice_got": (
                "What has Pate actually got, then?",
                "A set of decisions. Dat's all a weir pin is. Long ago somebody stood in a junction, worked out how "
                "fast da hall should fill, and cut da answer in stone so da next crew wouldn't have to guess. Your "
                "sluice-keeper has been guessin' for nine years with a wooden wedge and a bad temper, and now he "
                "doesn't have to. Dat's a big gift. And here's what I didn't say in front of him. I've carried dis "
                "my whole life and offered it to dat port whenever anyone would listen, and nobody ever did. Da "
                "first person who wanted it runs a mill in Hillsbrad and has never seen da place. I've decided to be "
                "pleased about dat. It took me a week."),
        }),
        ("bb_quiet_mans_ledger", "The Quiet Man, Booty Bay. The fence. Careful, exact, not kind and says so.", {
            "the_book": (
                "What's actually in the book?",
                "Boats and years, nothing else, and I want you to understand how little that is. Which ship came "
                "in, on what tide, who walked off it, and when. I started it because a man in my trade who can't say "
                "where a thing came from is handling stolen goods, and one who can is handling goods with a history, "
                "and that's worth money. Then the world changed and the boats stopped being boats I knew, and I kept "
                "writing, because stopping would have been a decision and writing was a habit. So yes, you're in "
                "it. Ship, tide and year, three lines, the same as everybody."),
            "who_comes_asking": (
                "Who comes asking after it?",
                "Three kinds, and I can tell which before they finish their first sentence. Insurers, who want a "
                "ship. Families, who want a name, usually get one, and almost never thank me. And then the third "
                "kind, who ask very politely for everybody who arrived in a particular season. Not a name, a season. "
                "I've been asked that four times, and every one of them had a good reason ready before I opened my "
                "mouth. That's how I knew. A man with a good reason to want a list of strangers has already thought "
                "about what he'll do with it."),
            "what_it_is_worth": (
                "What's it worth, and why do you still have it?",
                "More than this shop, and the offers go up every year, which tells you why. Nizzik won't keep a list "
                "like that. She says it's something somebody uses later, and she's right. I started mine years "
                "before any of it mattered, and the only honest thing left to me is to be the one holding it. That "
                "isn't kindness. If I sell it, it gets used, and I'll be the man who sold it. I've been a lot of "
                "things in this cove, but never that, and at my age a man is mostly the things he's refused to be."),
        }),
        ("bb_marlas_question", "Keeper Marla, Booty Bay tavern. From Lakeshire, warm, blunt.", {
            "lakeshire": (
                "Why did you leave Lakeshire?",
                "Because a cook in Lakeshire feeds people who are going home afterwards, and I found I didn't like "
                "that as much as I'd thought. Eleven years ago a goblin came up the lake buying salt pork and told me "
                "about a harbour in the south where nobody ever sat down to eat. He meant it as a complaint, and I "
                "heard it as a job opening. My sister still writes to ask when I'm coming back. I've stopped telling "
                "her it's warm, because she thinks that's the reason. The reason is that down here, when someone "
                "sits down to eat, it means something."),
            "the_boards": (
                "What's it like, cooking for this town?",
                "Nobody here eats. They refuel standing up, with one eye on their crates, and go back out, and a "
                "quarter of them won't be in the cove next week. So I make one pot properly and make them sit for "
                "it. That's my whole trade, and it took me three years to stop apologising for it. And since you've "
                "been in and out all season and heard them all talk: half this town is carrying something it won't "
                "put down, and the other half is charging it rent. Nizzik is kinder than she sounds, the Baron is "
                "exactly what he sounds like, and the pilot is the only one who ever asks me a question back."),
            "the_hot_water": (
                "Your question about the hot water. What did you decide?",
                "That it's true, and worse than I thought, and I was right to keep chewing on it. It's not the water. "
                "Anyone can carry water, and I've carried plenty. What I couldn't get past is that nobody thinks about "
                "it. A whole world of people were given something so good they stopped noticing they had it, then "
                "had it taken away all at once, and came ashore here and started paying a landing fee. So you've all "
                "come a long way down in the world. I've been saying that to the stew pot for a month, and somebody "
                "on these boards should have said it to you long ago. Sit down and finish that. It isn't hot water, "
                "but it's hot."),
        }),
    ],
}


def render(zone):
    lines = ["QUEST_TOPICS = {"]
    for qid, who, topics in TOPICS[zone]:
        lines.append("    # " + "-" * 95)
        lines += ["    # " + w for w in textwrap.wrap(who, 95)]
        lines.append("    # Plain-voice rewrite, 17 Nov 2026 (tools/stv_topic_voice.py).")
        lines.append("    # " + "-" * 95)
        lines.append(f"    {qid!r}: {{")
        for tid, (label, response) in topics.items():
            lines.append(f"        {tid!r}: {{")
            lines.append(f"            \"label\": {label!r},")
            lines.append("            \"response\": (")
            for chunk in textwrap.wrap(response, 96, drop_whitespace=False):
                lines.append(f"                {chunk!r}")
            lines.append("            ),")
            lines.append("        },")
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from build_tempest_quests import voice_problems
    problems = []
    for zone, quests in TOPICS.items():
        mod = importlib.import_module(f"world.quest_dialogue_stranglethorn_{zone}")
        old = mod.QUEST_TOPICS
        for qid, _who, topics in quests:
            if set(topics) != set(old.get(qid, {})):
                problems.append(f"{zone} {qid}: topic ids differ from the live ones {sorted(old.get(qid, {}))}")
            for tid, (label, response) in topics.items():
                for p in voice_problems(label) + voice_problems(response):
                    problems.append(f"{zone} {qid}.{tid}: {p}")
        if set(old) != {q for q, _w, _t in quests}:
            problems.append(f"{zone}: quest ids differ from the live ones")
    print(f"  {sum(len(t) for qs in TOPICS.values() for _q, _w, t in qs)} topics, {len(problems)} problem(s)")
    for p in problems:
        print("  PROBLEM " + p)
    if "--write" in sys.argv:
        if problems:
            print("  REFUSING TO WRITE")
            return 1
        for zone in TOPICS:
            path = ROOT / f"world/quest_dialogue_stranglethorn_{zone}.py"
            src = path.read_text(encoding="utf-8")
            head = src[:src.index("QUEST_TOPICS = {")]
            path.write_text(head + render(zone), encoding="utf-8")
            importlib.reload(importlib.import_module(f"world.quest_dialogue_stranglethorn_{zone}"))
        print("  written: the three topic tables")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
