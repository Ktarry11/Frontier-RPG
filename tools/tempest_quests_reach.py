"""
The Ashen Reach (55-58), Cinderwharf and the Emberdeep. Thirty-two quests.

Read by tools/build_tempest_quests.py. See that file for the rules these are held to.

WHAT THIS HALF OF THE ISLAND IS ABOUT. The working side. A smelter yard with sixty people in it, a
town where dwarves drink on the left and goblins on the right, and a mountain that is doing
something no mountain should. Three threads:

  THE FOUR BARGES (4)   Carried over from the landing. The harbourmaster has lost four hulls; an
                        adjuster from Singapore is deciding whether it was the sea. It was not.
  THE WORKS (11)        The foreman's ore road, the enginewright's gaskets, an assayer whose number
                        nobody wants, and a lantern that came out of a fire elemental.
  THE MOUNTAIN (9)      Dr. Arakawa watched Sakurajima for twenty years and says this volcano has a
                        pulse. His three quests end at the thing that is beating. The Emberdeep's
                        other work is given in Cinderwharf, and the last of it is the deep claim.

ONE CHAIN LEAVES THE ISLAND: when the old Thane is dead, Keeper Morn sends word to the Dark Irons
of Onyxhollow under the Black Strand that a second hold has its hall back.
"""
from tools.tempest_quest_kit import (  # noqa: F401
    AR, CW, ED, Q, k, boss, explore, deliver, talk, carry, fetch,
    BRAKKA, TOBBLE, KETTIL, MIZZI, VARGA, GRIB, RUDDI, ORRIN, KENJI,
    VELA, HOGAR, MORN, DOLLA, NIX, GEX, PELL, SKEZZ, THORA, PRIYA, MORGRIM)

FETCH_DROPS = {
    "Stormscale Naga Raider": [
        ("tmp_nameboard", "Barge Nameboard", "A plank with a barge's name burned into it and "
                                             "a Cinderwharf berth number underneath."),
        ("tmp_boarding_hook", "Naga Boarding Hook", "A barbed iron hook on a length of kelp "
                                                    "rope. The barbs are full of pine "
                                                    "splinters."),
    ],
    "Scourcoast Crab": [
        ("tmp_scourcoast_meat", "Scourcoast Crab Meat", "Dark, firm and faintly smoky, as if "
                                                        "it had been cooked already."),
        ("tmp_brass_fitting", "Barnacled Brass Fitting", "A ship's fitting gone green under "
                                                         "its barnacles. The casting's too "
                                                         "fine for goblin work."),
    ],
    "Steamvent Ooze": [
        ("tmp_ooze_membrane", "Ooze Membrane", "A sheet of clear rubbery skin. Acid beads on "
                                               "it and runs off."),
    ],
    "Ashplain Basilisk": [
        ("tmp_basilisk_hide", "Ashplain Basilisk Hide", "Thick, pebbled and almost "
                                                        "impossible to tear."),
    ],
    "Ventborn Flame Spirit": [
        ("tmp_fissure_crust", "Yellow Fissure Crust", "A brittle yellow crust that stinks of "
                                                      "eggs. It leaves gold dust on your "
                                                      "fingers."),
    ],
    "Tarfoot Gorilla": [
        ("tmp_tar_ball", "Ball of Vent Tar", "Black, soft and warm. It came off a gorilla's "
                                             "foot and it'll stick to anything."),
    ],
    "Calderaborn Drake": [
        ("tmp_caldera_glass", "Fresh Caldera Glass", "Black glass with a skin of bubbles. "
                                                     "It's still warm in the middle."),
    ],
    # ---- inside the Emberdeep
    "Sulphur Crawler": [
        ("tmp_crawler_gland", "Sulphur Crawler Gland", "A fat yellow sac that hisses when "
                                                       "you squeeze it."),
    ],
    "The Molten Serpent": [
        ("tmp_serpent_scale", "Molten Serpent Scale", "A scale the size of a shield. It "
                                                      "glows dull red and it hasn't cooled "
                                                      "at all.", 1.0),
    ],
}
STARTER_DROPS = {
    "Stormscale Naga Raider": [("tmp_tide_chart", "Naga Tide-Chart",
                                "A sheet of sharkskin pricked with holes. Held to the light it "
                                "shows a coastline and a line running through the reefs.", 0.22)],
    "Scoria Fire Elemental": [("tmp_melted_lantern", "Half-Melted Works Lantern",
                               "An Ashclaim carter's lantern, slumped down one side. The brass "
                               "number plate has survived.", 0.22)],
}
STARTER_IDS = {"tmp_tide_chart": "tmp_the_tide_chart",
               "tmp_melted_lantern": "tmp_lantern_nineteen"}


def build():
    q = []

    # ================= THE FOUR BARGES =================
    q.append(Q("tmp_four_barges", "Four Barges", SKEZZ, 55, 55, "wreck",
               "Kill Stormscale Naga Raiders on the Scoured Coast and recover the Barge "
               "Nameboards they've taken.",
               [k("Stormscale Naga Raider", 10, AR), fetch("tmp_nameboard", 4)],
               "A barge doesn't vanish, so those four are somewhere, and I think I know "
               "where.\n\nThe current off the landing sets north along the west shore. "
               "Anything that sinks in the bay washes up on the Scoured Coast, and the "
               "Stormscale Naga Raiders have been thick on that coast since the sea route "
               "opened three years ago. They take trophies. If they've had my barges, "
               "they'll have kept the nameboards.\n\nGo out of the town gate and cross "
               "the Ashen Reach to its far west shore, past the Cinder Flats. Kill the "
               "Raiders you find and bring me any nameboard they're carrying.",
               "The Ruby Ledger, the Second Mortgage, the Honest Mistake and the "
               "Durgan's Patience are all here.\n\nSo the naga had them, but that "
               "doesn't tell me how. A raider can loot a wreck or it can make one, and "
               "those cost the Underwriter very different amounts.\n\nTake these boards "
               "to Adjuster Raman at the Merchant House, because working that out is "
               "her job. Tell her I said it wasn't my pilots.",
               nxt="tmp_bad_luck_or_bad_seamanship", zone=CW))

    q.append(Q("tmp_bad_luck_or_bad_seamanship", "Bad Luck or Bad Seamanship", PRIYA, 56, 56,
               "wreck",
               "Examine the two barge wrecks on the Scoured Coast and collect Naga Boarding "
               "Hooks from the Stormscale Naga Raiders.",
               [explore(46, 64, "the northern barge wreck on the Scoured Coast", AR),
                explore(50, 108, "the southern barge wreck on the Scoured Coast", AR),
                fetch("tmp_boarding_hook", 5)],
               "The Harbourmaster says it was naga and the Underwriter says it was her "
               "pilots, and I'm paid to find out which.\n\nI did this for nine years in Singapore, before I came through. A hull tells you how it died if you look at it properly. A "
               "barge that ran aground is holed from below, and a barge that was boarded "
               "is damaged along the rail, where the hooks went in.\n\nTwo of the wrecks "
               "are lying on the Scoured Coast, on the far west shore of the Reach. One's "
               "at the north end and the other's at the south. Look at where each hull's "
               "broken. I'd also like some of the hooks the Raiders carry, so I can match "
               "the barbs to the marks.",
               "Both hulls are sound below the waterline, and both rails are torn to "
               "splinters.\n\nThese hooks have pine in the barbs. The barges were pine "
               "and the old wrecks out there are oak. I'd have paid that claim in "
               "Singapore without a second look.\n\nThe barges were boarded while they "
               "were afloat. Somebody on that coast is organising it, because raiders "
               "who only scavenge don't carry tools for the job.",
               nxt="tmp_the_wreck_captain", zone=CW,
               requires_quests=["tmp_four_barges"]))

    q.append(Q("tmp_the_wreck_captain", "The Wreck-Captain", SKEZZ, 57, 57, "wreck",
               "Kill Wreck-Captain Vess'ira on the Scoured Coast.",
               [boss("Wreck-Captain Vess'ira", AR)],
               "The Adjuster's report's on my desk, and it has a name in it that I've "
               "heard before.\n\nThe coast surveyor's been telling me for months about a "
               "naga who gives orders from the old wrecks. I thought she was making "
               "excuses for her charts. She calls it Wreck-Captain Vess'ira, and says "
               "the raiders bring everything they take to it.\n\nIt keeps to the Scoured "
               "Coast on the west shore of the Reach, and it doesn't show itself to "
               "everyone. It'll come out for somebody who's hunting it. I've got crews "
               "who won't sail until it's dead, so I'm asking you.",
               "That's its helm, and it's wearing one of my berth tags as an "
               "earring.\n\nI'll post the news on the wharf tonight and I'll have "
               "pilots signing on again by morning. The Underwriter's already sent word that he's pleased, and he's putting the berth fees up as well.\n\n"
               "This is from the harbour office, with my thanks and my pilots'.",
               zone=CW, requires_quests=["tmp_bad_luck_or_bad_seamanship"]))

    q.append(Q("tmp_a_harbour_chart", "A Harbour Chart", MIZZI, 56, 56, "wreck",
               "Carry Mizzi's coast chart to Harbourmaster Skezz in Cinderwharf.",
               [deliver("tmp_coast_chart", "the coast chart, to Harbourmaster Skezz in "
                                           "Cinderwharf")],
               "I've finished the chart of this coast, and I'd like it to reach the "
               "wharf without me.\n\nThe last two times I tried to carry it across the "
               "Reach I lost a boat and a boot. You look like you'd get there. "
               "Harbourmaster Skezz needs it before she sends another barge round the "
               "west side.\n\nCinderwharf's on the north-east shore. Head east across "
               "the Cinder Flats until you reach the town gate, and she's on the wharf "
               "at the north end of town.",
               "Every reef's marked on here, and so is every wreck.\n\nNobody's had a chart of this island since the sea route opened three years ago, and I've been sending pilots down that shore with a sketch and a prayer. I owe that "
               "surveyor an apology, and I'll send it with a bottle.\n\nYou crossed "
               "the Flats with this under your arm and it isn't even singed. Take "
               "something from the harbour office for that.",
               turn_in_npc_id=SKEZZ,
               grant_items=carry("tmp_coast_chart", "Mizzi's Coast Chart",
                                 "A long roll of waxed canvas inked with soundings, reefs and "
                                 "eleven small drawings of sunk ships.")))

    q.append(Q("tmp_older_than_the_ashclaim", "Older Than the Ashclaim", MIZZI, 55, 55, "wreck",
               "Collect Barnacled Brass Fittings from the Scourcoast Crabs on the Scoured "
               "Coast.",
               [fetch("tmp_brass_fitting", 6)],
               "Somebody was sailing to this island a long time before the goblins "
               "found it on a map, and I'd like to know who.\n\nThe old wrecks along "
               "this shore are oak and brass, and the brass is finer than anything my "
               "people cast. The Scourcoast Crabs pick the fittings off and wear them, "
               "the way a hermit crab wears a shell.\n\nThey're all along the waterline, "
               "north and south of where we're standing. Get me a handful of those "
               "fittings and I'll see if there's a maker's mark under the barnacles.",
               "I've scraped one clean while you were getting your breath back, and "
               "there's a mark on it.\n\nIt's a hammer over a flame. That's the old "
               "seal of Khaz Varun. The dwarves under the mountain had ships, and "
               "they traded off this coast before their city went dark.\n\nThe Thane's "
               "going to want to see this. The Underwriter's going to want it even "
               "more, because a city with a harbour's worth twice as much."))

    q.append(Q("tmp_pitch_for_two_boats", "Pitch for Two Boats", MIZZI, 55, 55, "landing",
               "Collect Balls of Vent Tar from the Tarfoot Gorillas in the open ash country of "
               "the Ashen Reach.",
               [fetch("tmp_tar_ball", 8)],
               "I've got two boats left and they both leak, and there isn't a barrel of "
               "pitch between here and the wharf.\n\nThere's tar on this island, though. "
               "It seeps up warm round the vents, and the Tarfoot Gorillas walk through "
               "it until their feet are caked. That's how they got the name.\n\nYou'll "
               "find them in the open ash country east of this coast, between here and "
               "the Works. I need the tar off their feet, and I'm sorry, but there's "
               "no gentle way to ask a gorilla for it.",
               "That's good black tar, and it's soft enough to work.\n\nI'll have "
               "both hulls sealed by tomorrow. I'm still going to sink, because this "
               "coast sinks everything, but it'll take longer and I'll get more "
               "soundings done first.\n\nHere, this washed up last week and it's too "
               "big for me."))

    # ================= THE GATE AND THE WORKS =================
    q.append(Q("tmp_weighed_at_the_gate", "Weighed at the Gate", GRIB, 55, 55, "ashclaim",
               "Carry the gate's weigh book to Assayer Ruddi at the Ashclaim Works.",
               [deliver("tmp_weigh_book", "the gate weigh book, to Assayer Ruddi at the "
                                          "Ashclaim Works")],
               "If you're heading out to the Works, you can take the weigh book with "
               "you and save my runner a pair of boots.\n\nI weigh every cart of ore "
               "that comes through this gate. Assayer Ruddi weighs the same carts when "
               "they leave the Works. If his book and hers don't match, somebody's been "
               "stealing on the road, and she likes to know before the dwarves blame "
               "her for it.\n\nThe Works is a long walk west of here, on the far side "
               "of the Cinder Flats. Follow the cart ruts and you can't miss the "
               "smelter smoke.",
               "Give me a minute to run my finger down his column against mine.\n\n"
               "They match to the pound, every cart for a month. That's a relief, and "
               "it's also a problem, because it means the ore we're short isn't going "
               "missing on the road.\n\nIt's going missing before it gets to my "
               "scales. Come back and see me when you've had a look round the yard.",
               turn_in_npc_id=RUDDI,
               grant_items=carry("tmp_weigh_book", "Gate Weigh Book",
                                 "A greasy ledger with a column of cart numbers and a column "
                                 "of weights, initialled by Grib on every line.")))

    q.append(Q("tmp_the_ore_road", "Sixty People", BRAKKA, 55, 56, "cinderflat",
               "Kill Sulphur Raptors and Ashplain Basilisks on the Cinder Flats, along the ore "
               "road.",
               [k("Sulphur Raptor", 10, AR), k("Ashplain Basilisk", 8, AR)],
               "I've got sixty people in this yard, and I'd like to have sixty at the "
               "end of the week.\n\nThe ore goes out by cart across the Cinder Flats to "
               "the town gate. The Sulphur Raptors run the carts down for the mules. "
               "The Ashplain Basilisks lie in the ruts and look like rock until a "
               "carter steps on one. I've had two carters carried back stiff this "
               "month.\n\nThe Flats are north-east of the yard. Walk the cart road and "
               "kill what's on it. You'll be doing more for this island than anyone "
               "in the Merchant House.",
               "The afternoon carts got through to the gate without stopping "
               "once.\n\nThe carters came back singing, which I didn't enjoy, but "
               "I'll take it over the alternative. I've told the paymaster you're on "
               "the books for today.\n\nThis is Works issue, and it's the good "
               "stuff from the back of the store."))

    q.append(Q("tmp_things_that_walk_through_fire", "Things That Walk Through Fire", BRAKKA,
               56, 57, "cinderflat",
               "Kill Scoria Fire Elementals on the Cinder Flats.",
               [k("Scoria Fire Elemental", 12, AR)],
               "The animals on the Flats I can live with, but the fire that walks is "
               "another matter.\n\nThe Scoria Fire Elementals come up out of the vents "
               "and wander. They aren't hunting anything. They walk in a straight line "
               "until they meet something, and then it burns. Last week one walked "
               "through the tool store.\n\nThere weren't any on this island when the "
               "dwarves left it, according to the Deedkeeper. They've come since the "
               "day the world changed, and there are more every month. They're out on "
               "the Cinder Flats, north-east of here. Put out as many as you can.",
               "The lookout counted the glows on the Flats at dusk and came down "
               "to tell me there were fewer.\n\nThat's the first time the number's "
               "gone the right way since I took this job. I don't know how long "
               "it'll last, and Dr. Arakawa won't tell me, which worries me more "
               "than if he would.\n\nTake this from the yard stores, and my thanks "
               "with it.",
               nxt="tmp_old_scoria"))

    q.append(Q("tmp_old_scoria", "Old Scoria", BRAKKA, 57, 57, "cinderflat",
               "Kill Old Scoria on the Cinder Flats.",
               [boss("Old Scoria", AR)],
               "There's one out there that's bigger than the rest, and it doesn't "
               "wander like they do.\n\nThe carters call it Old Scoria. It stands in "
               "the middle of the Cinder Flats for days at a time, and the small ones "
               "come up out of the ground around it. My scout thinks it's calling "
               "them, and she isn't given to fancies.\n\nIt's north-east of the yard, "
               "out where the crust's blackest. It isn't always there, but it seems "
               "to come up when somebody goes looking. If you can break it, we might "
               "get a season's peace.",
               "The whole yard felt it go, because the ground gave a kick and "
               "every lamp in the smelter jumped.\n\nThen it went quiet, and it's "
               "stayed quiet. Varga came in off the Flats an hour ago and said she "
               "hadn't seen a single glow on her whole round.\n\nYou've given me a "
               "season. Take whichever of these suits you, with the thanks of "
               "sixty people.",
               requires_quests=["tmp_things_that_walk_through_fire"]))

    q.append(Q("tmp_brass_in_a_month", "Brass in a Month", TOBBLE, 55, 55, "cinderflat",
               "Collect Ooze Membranes from the Steamvent Oozes on the Scoured Coast.",
               [fetch("tmp_ooze_membrane", 6)],
               "The dwarves say the vents were gentle before the day the world changed, but now the air off them eats my gaskets faster than I can cut them, "
               "and I've found something it doesn't eat.\n\nThere are oozes living in "
               "the steam vents on the coast. A Steamvent Ooze sits in acid all day "
               "and its skin doesn't mind at all. I cut a strip off a dead one and "
               "left it in the worst flue I've got, and a month later it's still "
               "good.\n\nThey're on the Scoured Coast, north-west of the Works, "
               "wherever there's steam coming out of the rocks. Bring me their "
               "membranes and I'll regasket the whole pump engine.",
               "These are perfect, and they're even the right thickness.\n\nI'm "
               "going to cut forty gaskets tonight and sleep through a whole shift "
               "tomorrow for the first time since I landed. The engine can hate me "
               "all it likes.\n\nHave this, because I made it for myself and then "
               "never had a free hand to use it."))

    q.append(Q("tmp_drive_belts", "Drive Belts", TOBBLE, 56, 56, "cinderflat",
               "Collect Ashplain Basilisk Hides on the Cinder Flats for the winding gear.",
               [fetch("tmp_basilisk_hide", 6)],
               "The winding gear at the mine head runs on leather belts, and the heat "
               "down the shaft cooks them in a week.\n\nI've tried ox hide and I've "
               "tried kodo. I even tried a canvas one, and we don't talk about that. "
               "The only skin I've seen that doesn't care about heat is on an Ashplain "
               "Basilisk, and it lies about on hot rock all day for pleasure.\n\nThey're "
               "out on the Cinder Flats, north-east of here. I need whole hides, so "
               "try not to put too many holes in them.",
               "That's a proper hide, thick as my thumb and not a scorch on it.\n\n"
               "I'll have it cut and stitched onto the drum by the end of the "
               "shift. If these last a month I'll write to the mainland and tell "
               "them to stop sending me cows.\n\nThis is for you, from the mine "
               "head stores."))

    q.append(Q("tmp_the_number_he_wont_like", "The Number He Won't Like", RUDDI, 56, 56,
               "ashclaim",
               "Carry Assayer Ruddi's report to Underwriter Nix Brackwhistle in Cinderwharf.",
               [deliver("tmp_assay_report", "the assay report, to Underwriter Nix in "
                                            "Cinderwharf")],
               "I've worked out why we're short of ore, and the Underwriter isn't going "
               "to enjoy reading it.\n\nNobody's stealing it, because the seam's thinning. Every "
               "cart that comes up is a little poorer than the one before, and at this "
               "rate the upper workings are finished in a year. The rich ore's all "
               "deeper, under the Emberdeep, where nobody can dig.\n\nI can't leave "
               "the scales, so I need this carried to Underwriter Nix in Cinderwharf. "
               "He's in the Merchant House in the middle of town. Head east across "
               "the Flats to the town gate. Don't let him talk you into telling him "
               "it's wrong.",
               "I've read it twice, and I didn't like it better the second "
               "time.\n\nShe's right, of course. Ruddi's never been wrong by so much "
               "as a copper, which is exactly why I hired her and exactly why I "
               "wish I hadn't.\n\nSo the venture needs the deep ore, and the deep "
               "ore's under a lake of fire. That changes what I'm willing to pay "
               "for, and who I'm willing to pay.",
               turn_in_npc_id=NIX, requires_quests=["tmp_weighed_at_the_gate"],
               grant_items=carry("tmp_assay_report", "Ruddi's Assay Report",
                                 "Three pages of figures, each one a little smaller than the "
                                 "last, and a single line of conclusion underlined twice.")))

    q.append(Q("tmp_yellow_crust", "Yellow Crust", RUDDI, 57, 57, "cinderflat",
               "Collect Yellow Fissure Crust from the Ventborn Flame Spirits on the Emberdeep "
               "Approach.",
               [fetch("tmp_fissure_crust", 8)],
               "The alchemist in town's been buying something off the carters for "
               "pennies, and I want to know what it's really worth.\n\nIt's a yellow "
               "crust that forms round the fissures. The Ventborn Flame Spirits are "
               "born in those fissures and they come out coated in it. If I'm right "
               "about the colour, there's gold in it, and the Works has been walking "
               "past a second income every day.\n\nThe fissures are on the Emberdeep "
               "Approach, east of the yard on the way to the big door. Knock the "
               "crust off the Flame Spirits and bring it to my scales.",
               "It's come out at one part in forty, and I ran it twice to be "
               "sure.\n\nThat's richer than any gold mine I ever weighed for. Pell's "
               "been paying the carters a copper a pound and selling it on for "
               "silver. I've got to admire that, and I'm also going to end it.\n\n"
               "The dwarves get paid by what I weigh. From tomorrow I'm weighing "
               "this as well."))

    q.append(Q("tmp_walking_into_the_face", "Walking Into the Face", ORRIN, 57, 57,
               "cinderflat",
               "Kill Crag Earth Elementals on the Emberdeep Approach.",
               [k("Crag Earth Elemental", 10, AR)],
               "I can't fire a charge while there's something standing in front of "
               "it, and lately there's always something.\n\nThe Crag Earth Elementals "
               "walk up out of the Emberdeep Approach and straight into my blast "
               "faces. I think the drilling draws them. They stand there in the rock "
               "with my powder packed all round them, and I've got to pull every "
               "charge by hand before I can try again.\n\nThe Approach is east of "
               "the red shed, on the way to the big door. Break up the ones you "
               "find before they get as far as my faces.",
               "I fired three faces this afternoon and there was nothing in any "
               "of them but rock.\n\nYou don't know how good that feels. Pulling "
               "a live charge is the part of this job that took the last "
               "blaster's hands.\n\nI've still got both of mine, so here's "
               "something they made on a quiet day."))

    q.append(Q("tmp_a_pulse", "A Pulse", KENJI, 56, 56, "cinderflat",
               "Set Dr. Arakawa's instruments at three vents: on the Cinder Flats, on the "
               "Scoured Coast and on the Emberdeep Approach.",
               [explore(120, 72, "the vent on the Cinder Flats", AR),
                explore(60, 70, "the steam vent on the Scoured Coast", AR),
                explore(120, 136, "the fissure on the Emberdeep Approach", AR)],
               "I told the Foreman that this mountain has a pulse, and she asked me to "
               "prove it.\n\nBefore the change I had forty instruments at Sakurajima and a room full of "
               "students. Here I've got three tiltmeters I built from clock parts. If "
               "I put them at three vents a long way apart and they all jump at the "
               "same moment, then one thing's moving under the whole island.\n\nThe "
               "first goes on the Cinder Flats, north-east of here. The second goes "
               "at the steam vent on the Scoured Coast, to the north-west. The third "
               "goes at the big fissure on the Emberdeep Approach, south-east of "
               "the yard. Set each one level on bare rock and come back.",
               "I watched all three needles from the hut, and they moved together "
               "to the second.\n\nIt beats once every nine minutes, at every vent, "
               "at the same instant. A magma chamber doesn't do that. Nothing I "
               "studied for twenty years does that.\n\nI'm not frightened of "
               "volcanoes, and I'd like you to know that so you understand what "
               "I mean when I say this one frightens me.",
               nxt="tmp_what_the_drakes_carry",
               grant_items=carry("tmp_tiltmeters", "Dr. Arakawa's Tiltmeters",
                                 "Three brass boxes with a needle under glass in each. They "
                                 "tick, very faintly, like a watch.", 3)))

    q.append(Q("tmp_what_the_drakes_carry", "What the Drakes Carry", KENJI, 57, 57,
               "cinderflat",
               "Kill Calderaborn Drakes on the Emberdeep Approach and collect Fresh Caldera "
               "Glass from them.",
               [k("Calderaborn Drake", 8, AR), fetch("tmp_caldera_glass", 5)],
               "I need to know what's in the lake under this mountain, and I can't "
               "get a sample without being cooked.\n\nThe Calderaborn Drakes can. They "
               "roost inside the crater and they swallow hot glass from the lake's "
               "edge, the way a hen swallows grit. Before I came through I'd have sent a drone over "
               "the rim. Here I'm asking you to open up a drake.\n\nThey hunt over "
               "the Emberdeep Approach, south-east of the yard. Bring me the glass "
               "while it's fresh, because the chemistry changes as it cools.",
               "It's still warm, and that's exactly what I needed.\n\nI've had a "
               "piece under the lens. There are threads running through the glass, "
               "like the grain in wood. Molten rock doesn't have a grain. "
               "Something's been growing in that lake.\n\nI think the pulse and "
               "the threads are the same thing. I think I know where it is, too, "
               "and it isn't somewhere I can go.",
               nxt="tmp_the_mountains_heart", requires_quests=["tmp_a_pulse"]))

    q.append(Q("tmp_the_mountains_heart", "The Mountain's Heart", KENJI, 58, 58, "emberdeep",
               "Enter the Emberdeep and kill The Mountain's Heart.",
               [boss("The Mountain's Heart", ED)],
               "Everything I've measured points at one chamber on the west side of "
               "the lake, and the Doorwarden says there's something in it.\n\nHis "
               "people call it The Mountain's Heart. I laughed when he told me, "
               "because that's the sort of name a miner gives to a hot rock. I've "
               "stopped laughing. It beats every nine minutes, and every fire "
               "elemental on this island comes up on the beat.\n\nThe door to the "
               "Emberdeep's east of the yard, at the end of the Approach. The "
               "chamber's deep in, on the western shore of the lake. I spent my "
               "life warning people away from craters, and I'm sorry to be the one "
               "who's sending you into this one.",
               "All three needles stopped at once, and I've been sitting here "
               "watching them ever since.\n\nThe ground's still warm and the vents "
               "still smoke. It's an ordinary volcano now. I can read an ordinary "
               "volcano, and so the Foreman can have her warnings again.\n\nWhen the bay at Kagoshima vanished three years ago I thought I'd never be useful to "
               "anyone again. You've given me my trade back.",
               requires_quests=["tmp_what_the_drakes_carry"]))

    q.append(Q("tmp_where_the_vents_moved", "Where the Vents Moved", VARGA, 56, 56,
               "cinderflat",
               "Check Scout Varga's three marker posts at the far edges of the Cinder Flats.",
               [explore(106, 66, "the north-west marker post on the Cinder Flats", AR),
                explore(158, 73, "the north-east marker post on the Cinder Flats", AR),
                explore(150, 96, "the south-east marker post on the Cinder Flats", AR)],
               "I've got three marker posts out at the edges of the Flats, and I "
               "haven't been able to get round them this week.\n\nEach post has a "
               "rope pegged out from it to the nearest vent. If the vent's moved, "
               "the rope's slack or it's burned through. That's how I know where "
               "to send the carts. I turned my ankle on the crust two days ago, so "
               "I can't walk the long round.\n\nOne post's to the north-west, one's "
               "to the north-east, and the third's south-east of here toward the "
               "town gate. Look at the rope at each one and tell me what you see.",
               "So the north-west rope's burned through and the other two are "
               "tight.\n\nThat means the western vent's moved toward the cart "
               "road by a rope's length. I'll shift the road markers east in the "
               "morning, ankle or no ankle.\n\nYou may have saved a cart today, "
               "and the carter on it. Take this, because I won't be needing it "
               "until I can walk properly."))

    q.append(Q("tmp_the_ventlord", "The Ventlord", VARGA, 58, 58, "emberdeep",
               "Kill Karrath the Ventlord on the Emberdeep Approach.",
               [boss("Karrath the Ventlord", AR)],
               "There's something on the Emberdeep Approach that opens vents where "
               "it walks, and I've seen it do it.\n\nI was on the south edge of the "
               "Flats at dawn. It came up the slope from the big door, as tall as "
               "the winding tower, and wherever it put its foot down the ground "
               "split and steamed. The Doorwarden's people have a name for it. "
               "They call it Karrath the Ventlord.\n\nIt walks the Approach, south "
               "of here. It doesn't come out every day, but it seems to know when "
               "it's being hunted, and it comes to meet whoever's hunting. If it "
               "ever walks as far as the Works, there won't be a Works.",
               "I saw the steam stop from here, all along the Approach at the "
               "same moment.\n\nI've walked this ground for two years and I've "
               "never seen it lie still. I'm going to sit down and look at it "
               "for a while.\n\nThe Foreman told me to give you this if you "
               "came back. She was sure you'd be back, and I'm glad she was right."))

    q.append(Q("tmp_the_door_was_sealed", "The Door Was Sealed", KETTIL, 57, 57, "emberdeep",
               "Hear what Doorwarden Kettil knows about the Emberdeep, then carry his door "
               "book to Keeper Morn Ashhold in Cinderwharf.",
               [talk("tmp_kettil_the_seal", "tmp_kettil_the_day"),
                deliver("tmp_door_book", "the door book, to Keeper Morn in Cinderwharf")],
               "You've got the look of someone who's going down there, so you'd "
               "better hear what I know first.\n\nAsk me about the seal and about "
               "the day it broke. When you've heard it, I'd like you to carry my "
               "door book to Keeper Morn in Cinderwharf. He keeps the old rites, "
               "and the seal on this door was one of them.\n\nThe town's north-east "
               "of here, across the Cinder Flats. Morn's on the Shrine Terrace at "
               "the south-west corner of the hold.",
               "Kettil's written down every time the door's breathed, and there "
               "are a great many entries.\n\nThe seal was an Ashhold rite. My "
               "grandfather knew the words and my father knew half of them. I "
               "know that there were words.\n\nSo I can't close that door "
               "again. All I can do is tell you that whatever broke it was "
               "stronger than nine generations of my family, and ask you to be "
               "careful.",
               turn_in_npc_id=MORN,
               grant_items=carry("tmp_door_book", "Kettil's Door Book",
                                 "A soot-stained notebook. Every line is a date, a time and "
                                 "the words 'it breathed'.")))

    # ================= CINDERWHARF'S ERRANDS =================
    q.append(Q("tmp_whatever_came_off_the_boat", "Whatever Came Off the Boat", DOLLA, 55, 55,
               "ashclaim",
               "Collect Scourcoast Crab Meat from the Scourcoast Crabs on the Scoured Coast "
               "for the Tapped Vein's stew.",
               [fetch("tmp_scourcoast_meat", 8)],
               "I tell everyone the stew's whatever came off the boat, and this "
               "week nothing came off the boat.\n\nI've got dwarves on the left "
               "and goblins on the right, and the one thing they agree on is "
               "that they want feeding. The carters say the Scourcoast Crabs on "
               "the west shore taste as if they've been smoked already, on "
               "account of the vents.\n\nGo out of the town gate and west across "
               "the Reach to the Scoured Coast. Bring me the meat and I'll put "
               "your name on the board as the reason anyone ate tonight.",
               "Smell that, would you? It really is smoked already.\n\nThe "
               "dwarves had three bowls each and the goblins tried to buy the "
               "recipe. I told them it's a secret, and the secret's that you "
               "walked across a volcano for it.\n\nYour name's on the board, "
               "and this is for you from behind the bar."))

    q.append(Q("tmp_no_questions_about_the_powder", "No Questions About the Powder", GEX,
               56, 56, "ashclaim",
               "Carry Trader Gex's unmarked keg to Blaster Orrin at the Ashclaim Works.",
               [deliver("tmp_unmarked_keg", "the unmarked keg, to Blaster Orrin at the "
                                            "Ashclaim Works")],
               "I need a keg carried to the Works, and I need whoever carries it "
               "not to be curious.\n\nIt goes to Blaster Orrin, at the red shed on "
               "the south side of the yard. He's expecting it. You don't need to "
               "know what's in it, and if anyone at the gate asks, it's pickled "
               "fish.\n\nThe Works is west of town across the Cinder Flats. "
               "Carry it level and don't drop it, and I'd also keep it away from "
               "anything that's on fire, and out there that means most things.",
               "That'll be the pickled fish, then, and it's the best powder "
               "I'll see all month.\n\nYou may as well know what you carried. "
               "The Works powder comes over on the boat, and half of it's damp "
               "by the time it lands. Gex buys the damp kegs off the Ashclaim "
               "as scrap, dries them out and sells them back to me at twice "
               "the price.\n\nI ought to report him. I won't, because his "
               "powder fires every time, and the official stuff doesn't.",
               turn_in_npc_id=ORRIN,
               grant_items=carry("tmp_unmarked_keg", "Unmarked Keg",
                                 "A small keg with the stencil scraped off. It's much "
                                 "heavier than pickled fish.")))

    # ================= THE EMBERDEEP, GIVEN IN CINDERWHARF =================
    q.append(Q("tmp_the_landing_shelf", "The Landing Shelf", NIX, 56, 56, "emberdeep",
               "Enter the Emberdeep and kill Pack-Alpha Cinderhound on the Landing Shelf.",
               [boss("Pack-Alpha Cinderhound", ED)],
               "The venture needs the deep ore now, and the deep ore's on the far "
               "side of a door I can't get a survey party through.\n\nThere's a "
               "shelf of rock just inside the Emberdeep where a party could set "
               "up. The Doorwarden says it's held by a pack of hounds made of "
               "cinders, and that the pack follows one animal. He calls it "
               "Pack-Alpha Cinderhound, and I didn't ask him why.\n\nGo out of the town gate "
               "and south-west across the Reach. The door's at the end of the "
               "Emberdeep Approach, east of the Works. Kill the alpha and the "
               "pack should scatter.",
               "So the shelf's clear, and I can put surveyors on it by the end "
               "of the week.\n\nI'll be honest, I expected to be writing you "
               "off as a loss. I had the form half filled in. It's a pleasure "
               "to tear it up.\n\nHere's what the Ashclaim owes you for it.",
               nxt="tmp_geyser_rights", zone=CW,
               requires_quests=["tmp_the_number_he_wont_like"]))

    q.append(Q("tmp_geyser_rights", "Geyser Rights", NIX, 57, 57, "emberdeep",
               "Kill Thrass, the Geyser Spirit, in the Emberdeep.",
               [boss("Thrass, the Geyser Spirit", ED)],
               "My surveyors are on the shelf, and they've sent back a note about "
               "steam.\n\nThere's a field of geysers on the west side of the lake "
               "that would drive every engine the Works will ever need, free, for "
               "ever. There's also something living in it. The note says it's a "
               "spirit made of scalding water and that it boiled a surveyor's "
               "boots with the surveyor still in them. The Doorwarden knows it as "
               "Thrass.\n\nThe field's a short way in from the Landing Shelf, to "
               "the west. I want Thrass, the Geyser Spirit, out of my steam. "
               "The door's at the end of the Emberdeep Approach, south-west of "
               "town.",
               "The surveyors say the geysers are still running and nothing's "
               "shouting at them.\n\nThat's free power for a foundry. Three "
               "years ago I was selling shares in a deed nobody could reach, "
               "and now I'm standing on the best industrial site in the "
               "world.\n\nThank you for doing that, and here's your pay.",
               zone=CW, requires_quests=["tmp_the_landing_shelf"]))

    q.append(Q("tmp_a_scale_that_stays_hot", "A Scale That Stays Hot", HOGAR, 57, 57,
               "emberdeep",
               "Take a Molten Serpent Scale from The Molten Serpent in the Emberdeep.",
               [fetch("tmp_serpent_scale", 1)],
               "I've been told there's a serpent in the Emberdeep whose scales "
               "never cool, and I want one for the forge.\n\nA smith spends half "
               "his life waiting for metal to come back up to heat. If I had a "
               "plate that stayed red on its own, I could lay work on it and "
               "never lose the colour. The Doorwarden's people have seen the "
               "thing swimming in the lake, and they call it The Molten "
               "Serpent.\n\nIt coils in the middle of the Emberdeep, past the "
               "geysers. The door's south-west of town at the end of the "
               "Emberdeep Approach. I only need the one scale, but I don't "
               "expect it'll part with it.",
               "Set it down on the anvil and stand back, because I can feel "
               "it from here.\n\nIt hasn't lost a shade of colour since you "
               "took it. That's going into the bed of my forge tonight. Every "
               "blade I make from now on will be drawn on the back of a "
               "serpent.\n\nThe first thing off it's yours, and I finished it "
               "while you were telling me the story.",
               zone=CW))

    q.append(Q("tmp_what_the_vents_cough_up", "What the Vents Cough Up", PELL, 57, 57,
               "emberdeep",
               "Collect Sulphur Crawler Glands from the Sulphur Crawlers in the Emberdeep.",
               [fetch("tmp_crawler_gland", 6)],
               "The Assayer's worked out what my yellow crust is, so I need a "
               "new secret, and I think I've found one.\n\nThere are crawlers in "
               "the Emberdeep that live on raw sulphur. Each Sulphur Crawler has "
               "a gland where it stores the stuff, purer than anything I can "
               "refine. With that I can make an acid that'll take the mask "
               "rivets off without taking the face.\n\nThat last part's between "
               "us. The door's south-west of town, at the end of the Emberdeep "
               "Approach, and the Crawlers are on the Basalt Shelf east of the "
               "lake. Bring me the glands whole.",
               "They're whole, and they're hissing nicely.\n\nI tried a drop "
               "on one of the Broker's masks while he wasn't looking. The "
               "rivets went soft in a minute and the iron under them wasn't "
               "marked. If any of the masked ones can be brought out alive, "
               "there's a way to get them free now.\n\nI'll tell the Keeper. "
               "I won't be charging for it, and you can tell people I said "
               "that.",
               zone=CW))

    q.append(Q("tmp_the_oracle", "The Seer Who Went In", THORA, 58, 58, "emberdeep",
               "Kill Flame Oracle Ysmel in the Oracle's Ring of the Emberdeep.",
               [boss("Flame Oracle Ysmel", ED)],
               "There's a name in my rolls with no death written beside it, and "
               "I think I've found out why.\n\nYsmel Ashhold was the city's "
               "seer. The roll says she walked into the mountain to ask it a "
               "question, in the year before Khaz Varun went dark, and that "
               "she didn't come back. The Doorwarden tells me there's something "
               "in the Emberdeep that speaks, and that it calls itself Flame "
               "Oracle Ysmel.\n\nShe's in a ring of standing stones on the east "
               "side of the lake. The door's south-west of town at the end of "
               "the Emberdeep Approach. I'd like to be able to close her line "
               "in the roll, and I'd like her to be at rest.",
               "Then I can write the date beside her name, and I'll do it "
               "now while you're here to see it.\n\nYsmel Ashhold, seer of "
               "Khaz Varun, died this day under the mountain. I'll leave out "
               "the hundred years between. She asked the mountain a question, "
               "and I think the answer was the dark.\n\nThis was kept with "
               "her roll, and I think she'd want it carried.",
               zone=CW))

    q.append(Q("tmp_the_deep_claim", "The Deep Claim", VELA, 58, 58, "emberdeep",
               "Kill The Caldera at the bottom of the Emberdeep.",
               [boss("The Caldera", ED)],
               "You've asked what's behind me, so I'll tell you what the last "
               "thing on the shelf is.\n\nIt's a claim marker, a stake of Dark "
               "Iron with the Thane's seal on one face and the Underwriter's "
               "on the other. It's the only thing those two have ever signed "
               "together without arguing. It's meant to be driven into the "
               "floor of the caldera, at the very bottom of the Emberdeep, on "
               "the day somebody kills what lives there.\n\nThe Doorwarden "
               "only calls it The Caldera, as if it and the crater were the "
               "same thing. The door's south-west of town, at the end of the "
               "Emberdeep Approach, and the caldera floor's as far down as "
               "the Emberdeep goes. Nobody's taken the stake off my shelf "
               "yet.",
               "The stake's gone from your pack, so you've left it where it "
               "was meant to go.\n\nI've kept these stores since the wharf "
               "was a row of tents, and I never thought I'd hand that marker "
               "over. The whole mountain belongs to the Ashclaim now, from "
               "the gate of Khaz Varun to the bottom of the fire.\n\nThere's "
               "nothing behind me that you haven't earned, so take what you "
               "like, and take this first.",
               zone=CW, requires_quests=["tmp_geyser_rights", "tmp_the_mountains_heart"]))

    # ================= OUT OF THE ZONE =================
    q.append(Q("tmp_kin_under_another_roof", "Kin Under Another Roof", MORN, 58, 58,
               "khazvarun",
               "Carry Keeper Morn's letter to Thane Morgrim in Onyxhollow, under the Black "
               "Strand.",
               [deliver("tmp_morns_letter", "Morn's letter, to Thane Morgrim in Onyxhollow")],
               "The old Thane's at rest and the hall's quiet, and there are "
               "people who ought to be told.\n\nWe aren't the only Dark Irons "
               "who lost a home and found it again. There's a hold called "
               "Onyxhollow under the Black Strand, far to the west across the "
               "sea, and its Thane's a dwarf named Morgrim. Our families "
               "traded before either city went quiet. He ought to hear from "
               "one of us that Khaz Varun has a living thane.\n\nIt's a long "
               "way. Take the bird from the pad to Saltspur, cross to "
               "Kalimdor, and go down through the Abyssal Sands to the Black "
               "Strand. Onyxhollow's gate is at the end of the slag road.",
               "This is from Khaz Varun, and I'd been told that city was a "
               "grave.\n\nMy grandmother spoke of the Ashholds. She said they "
               "made the best plate in the world and drove the worst "
               "bargains. So one of them's sitting in his own hall again, "
               "and he's sent a priest's letter to tell me so.\n\nI've had "
               "a hard few years down here and so has he, by the sound of "
               "it. I'll write back. Tell the Keeper that Onyxhollow keeps "
               "a flame as well, and that we'll light one for his dead.",
               zone=CW, turn_in_npc_id=MORGRIM, requires_quests=["tmp_thane_morrun"],
               grant_items=carry("tmp_morns_letter", "Keeper Morn's Letter",
                                 "Sealed with shrine wax and addressed in an old formal hand "
                                 "to the Thane of Onyxhollow.")))

    # ================= TWO THINGS A MONSTER DROPS =================
    q.append(Q("tmp_the_tide_chart", "The Tide-Chart", "item:tmp_tide_chart", 55, 55, "wreck",
               "A Stormscale Naga Raider was carrying a chart of the coast. Take it to "
               "Coast-Surveyor Mizzi on the Scoured Coast.",
               [deliver("tmp_tide_chart", "the naga tide-chart, to Coast-Surveyor Mizzi on "
                                          "the Scoured Coast")],
               "The Raider had a sheet of sharkskin rolled in its belt. It's "
               "pricked all over with small holes, and when it's held up to the "
               "light the holes make the shape of this coast, with a line "
               "threading between the reefs.\n\nCoast-Surveyor Mizzi has been "
               "trying to chart these waters from a leaking boat. She's camped "
               "on the Scoured Coast, and she'd know what the line means.",
               "Hold it up to the lamp for me, and keep it still.\n\nThat's "
               "a channel. That's a deep-water channel straight through the "
               "reefs, and I've been looking for it for a year. The naga "
               "have known where it was all along.\n\nI've lost two boats "
               "finding out where it isn't. You've just handed me the answer "
               "off a dead raider's belt, and I don't know whether to laugh "
               "or cry about it.",
               turn_in_npc_id=MIZZI))

    q.append(Q("tmp_lantern_nineteen", "Lantern Nineteen", "item:tmp_melted_lantern", 56, 56,
               "cinderflat",
               "A Scoria Fire Elemental had an Ashclaim carter's lantern fused into it. Take "
               "it to Foreman Brakka at the Ashclaim Works.",
               [deliver("tmp_melted_lantern", "the melted lantern, to Foreman Brakka at the "
                                              "Ashclaim Works")],
               "There was a lantern stuck in the elemental's side, half melted "
               "into the slag. It's the kind the Ashclaim issues to its "
               "carters. The brass plate on the base came through the fire, and "
               "it's stamped with the number nineteen.\n\nForeman Brakka at the "
               "Ashclaim Works signs those lanterns out. She said she had sixty "
               "people and meant to keep them.",
               "Let me see the plate, because I know every one of those "
               "numbers.\n\nNineteen's Olla Burrfoot. She took a cart out "
               "four days ago and the mule came back alone. I've had people "
               "looking for her on the Flats ever since.\n\nSo I've got "
               "fifty-nine, and I've got to write to her brother. I'd been "
               "hoping for a different answer, but I'd sooner have this "
               "one than none. It was good of you to carry it in.",
               turn_in_npc_id=BRAKKA))

    return q
