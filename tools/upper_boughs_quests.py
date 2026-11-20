"""
The Upper Boughs' quests (47-48), the last tier of the World Tree you can live on, and the Stormsplit's (the lightning
crack in the trunk). Read by tools/build_upper_boughs_quests.py, which holds them to every rule before anything is
written. The brief is docs/worldtree_brief.md; the map is tools/handbuilt_worldtree_upper_boughs.py.

THE THREADS (the brief: "Thin air and wind: wind-bent branches, wyvern roosts, and the first wreckage falling out of
the clouds"; "storms and elementals; wyverns and harpies; something from above"):
  The ascent: Windwarden Kazra'jin keeps Highrest, the last camp, and the way up. His chain clears the gusts that throw
    climbers off, sends rope up to Ladderkeeper Vosh at the foot of the Cloud Way, and ends at the top of the Cloudbreak,
    at the old wall in the cloud. It stops at the wall: what happens there is the cutscene's (docs/crown_cutscene.md).
  The wyverns: Wyvern-Tamer Gu'lok and the wild flock on the Wyvern Roosts, their crested queen Stormcrest, and the
    old wyvern that nested in the Stormsplit and was struck with it.
  The storm: Stormcaller Ixi and the lightning. Storm-glass, the Lightning-Eater on the Storm Bough, and the storm
    trapped at the bottom of the Stormsplit.
  The boat with no water: Skywatcher Tal'mae and the Fallen Skiff. Its guardians, its warden, and its logbook, which
    goes down to Tel'zan's record in the Settlement. Nobody knows who sailed it, and nothing here says.
  The climbers: Old Muzzi climbed with Ruk'tan and Zel'ji. The thunderhawks, the old one that took his fingers, and a
    charm for Zel'ji tied on the Charm-Tree in the Cloudbreak, where the places are named for them.
  The weather: Ingrid Haugen, a mountaineer and meteorologist from Tromso, reads the weather the tree makes, and the
    harpies of the Gale who ride it.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. Earth comes up more again this
high (Ingrid, and the trolls' word for what happened, "the merge"), and the mural says nothing about why.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

UB = "upper_boughs"
SS = "stormsplit"
CB = "cloudbreak"

# ---- Highrest
KAZ, GULOK, IXI, TALMAE = "ub_windwarden", "ub_wyvern_tamer", "ub_storm_shaman", "ub_skywatcher"
MUZZI, INGRID = "ub_old_climber", "ub_transplant"
# ---- out on the tier
RHOKA, VOSH, TAZZO, NEEMA = "ub_stairwarden", "ub_ladderkeeper", "ub_scout_roosts", "ub_scout_wreck"
# ---- elsewhere (turn-ins only)
TELZAN = "gs_scholar_hall"

HUB_GIVERS = {KAZ, GULOK, IXI, TALMAE, MUZZI, INGRID}
TRIBE_GIVERS = HUB_GIVERS - {INGRID} | {RHOKA, VOSH, TAZZO, NEEMA}


def k(target, n, zone=UB):
    return kill(target, n, zone=zone)


def boss(target, zone=UB):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=UB, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Cloudtop Wyvern": [("ub_q_crest_feather", "Cloudtop Crest-Feather", "A long blue-grey feather from a Cloudtop "
                         "Wyvern's crest, stiff as a quill. It hums faintly when the wind crosses it.")],
    "Crackling Wisp": [("ub_q_storm_glass", "Shard of Storm-Glass", "A twist of dark glass that forms where a "
                        "Crackling Wisp spends itself against the bark. It's still warm, and it makes your hair "
                        "stand up.")],
    "Thunderhawk": [("ub_q_thunderhawk_quill", "Thunderhawk Quill", "A heavy flight quill from a Thunderhawk, banded "
                     "dark and pale like a storm sky.")],
    "Skiff Sentinel": [("ub_q_humming_crystal", "Humming Crystal", "A pale crystal from a Skiff Sentinel's chest. It "
                        "hums one low note that never changes, and it's cold to touch.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [17]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=UB, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
SKIFF = (146, 40)             # the Fallen Skiff, across two branch tips
ROOST_END = (166, 100)        # the far end of the Wyvern Roosts
GALE_TIP = (16, 108)          # the end of the Gale's lower branch
GALE_TOP = (16, 28)           # the end of the Gale's upper branch
ROPE_WALK = (22, 70)          # the middle of the old rope walk
THUNDER_TIP = (112, 8)        # the end of the Thunderhawk Reach
STORM_TIP = (98, 140)         # the end of the Storm Bough
CB_FOOT = (32, 104)           # the Cloudbreak: where Ruk'tan turned back
CB_CHARMS = (28, 68)          # the Cloudbreak: the Charm-Tree
CB_TOP = (32, 21)             # the Cloudbreak: the platform at the top, before the wall


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE ASCENT
    A(Q("ubq_gusts_on_the_storm_bough", "Gusts on the Storm Bough", KAZ, 47, 47, "Windwarden's",
        "Windwarden Kazra'jin keeps Highrest and the way up. The Galebound Gusts on the Storm Bough have started "
        "coming up the trunk, and they throw anyone they catch off the tree.",
        [k("Galebound Gust", 7)],
        "The Galebound Gusts live out on the Storm Bough, and lately they've been drifting up round the trunk. One "
        "picked a climber off the ring last week and dropped him into the cloud. Break them up before they do it again.",
        "That's quieter, and you can hear the wind again instead of the gusts howling in it.\n\nBefore the merge nobody "
        "lived this high, so the tree had nobody to throw off. I think it's still getting used to us.",
        nxt="ubq_rope_for_the_ladder"))
    A(Q("ubq_rope_for_the_ladder", "Rope for the Ladder", KAZ, 47, 47, "Ropewarden's",
        "Kazra'jin sends new rope up to Ladderkeeper Vosh at the foot of the Cloud Way every month, because the wind "
        "frays the old knots faster than anyone can tie them.",
        [deliver("ub_q_highrest_rope", "Take the coil of rope to Ladderkeeper Vosh at the foot of the Cloud Way")],
        "Vosh keeps the bottom of the ladders on the Cloud Way, and his grandfather hung the top ones. He's due fresh "
        "rope, and I'd rather it went up with someone who can fight. Take this coil to him at the foot of the Cloud Way.",
        "Good rope, and it's dry. Kazra'jin always sends the good rope.\n\nIf he's sending it with you, he's thinking "
        "of sending you up. He's only done that twice before, and only one of them came back.",
        turn_in_npc_id=VOSH, nxt="ubq_where_ruktan_turned_back",
        grant_items=carry("ub_q_highrest_rope", "Coil of Highrest Rope", "A heavy coil of tarred rope, plaited from "
                          "wyvern sinew and bark fibre, for the ladders on the Cloud Way.")))
    A(Q("ubq_where_ruktan_turned_back", "Where Ruk'tan Turned Back", KAZ, 48, 48, "Cloudwalker's",
        "Kazra'jin wants to know if you can stand the cloud before he lets you climb it. The Cloud Way goes up into "
        "the Cloudbreak, and there's a cairn at the foot of it where Ruk'tan turned back.",
        [explore(*CB_FOOT, "Climb the Cloud Way into the Cloudbreak and find Ruk'tan's cairn", zone=CB)],
        "Climb the Cloud Way and walk into the Cloudbreak, as far as Ruk'tan's cairn. You won't see the drop in the "
        "cloud, and that's the hard part, because your feet stop believing in the branch. Come back and tell me how "
        "it felt.",
        "You came back, and you came back walking. Ruk'tan didn't, he came back crawling.\n\nHe was the best climber "
        "of his age, and the cloud beat him. It doesn't seem to have beaten you.",
        nxt="ubq_the_wall_in_the_cloud"))
    A(Q("ubq_the_wall_in_the_cloud", "The Wall in the Cloud", KAZ, 48, 48, "Cloudbreaker's",
        "Kazra'jin has climbed into the cloud three times and come back down three times. He wants someone to go all "
        "the way to the top of the Cloudbreak, to the old stone wall the climbers talk about.",
        [explore(*CB_TOP, "Climb to the top of the Cloudbreak, where the branches meet below the old wall", zone=CB)],
        "Above the cloud the branches meet, and there's a wall up there older than the tree. I've seen it three times, "
        "and three times I couldn't make myself walk up to it. I'm too old to be ashamed of that. You're not, so go "
        "all the way up and stand where I couldn't.",
        "So it's still there, and you've stood in front of it.\n\nSomebody had to go and stand where I couldn't, "
        "and I'm glad it was somebody I sent. I've carried that wall around long enough."))

    # =================================================================================== 2. THE WYVERNS
    A(Q("ubq_wild_wyverns", "Wild Wyverns", GULOK, 47, 47, "Wyvernhand's",
        "Wyvern-Tamer Gu'lok wants a mount from the Wyvern Roosts, and the wild Cloudtop Wyverns won't let anyone "
        "near the flock until it's been thinned.",
        [k("Cloudtop Wyvern", 7)],
        "The Cloudtop Wyverns roost all along the bough past the ring, and they're mean the way only wild things are. "
        "A flock that big doesn't let you near the young. Thin it, and the rest will start to watch me instead of "
        "chasing me off.",
        "They're watching me now, and that's how it starts.\n\nI've lost two fingers learning this. The wyverns "
        "back in the Barrens were gentler, but they'd been tamed for a hundred years.",
        nxt="ubq_crest_feathers"))
    A(Q("ubq_crest_feathers", "Crest-Feathers", GULOK, 47, 48, "Crestbearer's",
        "Gu'lok says a wild wyvern will follow the smell of its own flock's crest-feathers, and he wants a harness "
        "woven with them.",
        [fetch("ub_q_crest_feather", 6)],
        "A wild wyvern trusts what smells like its flock. If I weave Cloudtop Crest-Feathers into the harness, the "
        "young ones won't fight it as hard. The Cloudtop Wyverns on the roosts carry them, so bring me what you can "
        "pull off them.",
        "These are good, they're long and stiff and they've still got the oil in them.\n\nOne harness, and then the "
        "only thing between me and a mount is the queen of that flock.",
        nxt="ubq_stormcrest"))
    A(Q("ubq_stormcrest", "Stormcrest", GULOK, 48, 48, "Stormcrest",
        "The Cloudtop flock follows a great crested female Gu'lok calls Stormcrest. While she flies, no wyvern on the "
        "roosts will take a rider.",
        [boss("Stormcrest")],
        "There's a queen on the roosts with a crest like a thundercloud, and the flock goes where she goes. I've "
        "named her Stormcrest, because that's all I've ever seen of her, flying over. She won't let one of hers be "
        "ridden. Bring her down, and the flock is mine to tame.",
        "The whole flock was in the air when she fell, and then they came down, one by one, and sat.\n\nI'll have a "
        "wyvern under a saddle before the month's out. You'll ride the first one, if you want it.",
        nxt="ubq_old_charwing"))
    A(Q("ubq_old_charwing", "Old Charwing", GULOK, 48, 48, "Charwing",
        "An old wyvern nested in the Stormsplit's crack before the lightning came back for it. Gu'lok says it's still "
        "down there, burned and mad, and the Stormstruck Wyverns that followed it in are no better.",
        [k("Stormstruck Wyvern", 5, zone=SS), boss("Old Charwing", zone=SS)],
        "The oldest wyvern I ever saw nested in the Stormsplit, right in the crack. Then the lightning hit the same "
        "place twice, and it came out burned and wrong. Old Charwing still nests down the side split, and the "
        "Stormstruck Wyverns followed it in. Go into the Stormsplit and end it, because it's suffering.",
        "It's done, and it's resting. That's kinder than what the lightning left it.\n\nI'll name the first wyvern "
        "I tame after it. That seems right."))

    # =================================================================================== 3. THE STORM
    A(Q("ubq_crackling_wisps", "Crackling Wisps", IXI, 47, 47, "Stormcaller's",
        "Stormcaller Ixi says the Crackling Wisps on the Storm Bough are pieces of lightning that never reached the "
        "ground, and they're building into something bigger.",
        [k("Crackling Wisp", 8)],
        "The Crackling Wisps are lightning that didn't finish striking. They drift out on the Storm Bough, and every "
        "week there are more and they're brighter. Break them before they find each other.",
        "Good, they've gone dim. The bough's quiet for a while.\n\nThe tree pulls lightning in like it's thirsty for "
        "it. Ingrid says the mountains on Earth do that too.",
        nxt="ubq_storm_glass"))
    A(Q("ubq_storm_glass", "Storm-Glass", IXI, 47, 48, "Glasscaller's",
        "Where a Crackling Wisp spends itself against the bark, it leaves a twist of dark glass. Ixi reads the storm "
        "in it.",
        [fetch("ub_q_storm_glass", 6)],
        "When a Crackling Wisp breaks, it leaves Storm-Glass behind. It's a twist of dark glass with the storm still "
        "in it, and I read the weather in it the way Ganjo reads the tree. Bring me the shards from the wisps on the Storm "
        "Bough.",
        "Hold one up to the light and you'll see it, a little fork of lightning frozen in the middle.\n\nThey're all "
        "pointing the same way. Something on the bough is eating the storm, and getting fat on it.",
        nxt="ubq_the_lightning_eater"))
    A(Q("ubq_the_lightning_eater", "The Lightning-Eater", IXI, 48, 48, "Lightning-Eater's",
        "The Storm-Glass points to the end of the Storm Bough, where something has been swallowing the lightning "
        "before the wisps can form. Ixi calls it the Lightning-Eater.",
        [explore(*STORM_TIP, "Find where the storm is going at the end of the Storm Bough"), boss("The Lightning-Eater")],
        "Every shard points to the end of the Storm Bough. Something at the end of it swallows lightning as fast as "
        "the sky throws it, and it's getting bigger. Go out to the end of the bough, find the Lightning-Eater, and "
        "let the storm out of it.",
        "The sky over the Storm Bough lit up like noon when it broke.\n\nThat was one. There's a bigger one in the "
        "trunk, and that one's been trapped for longer than I've been alive.",
        nxt="ubq_the_caught_storm"))
    A(Q("ubq_the_caught_storm", "The Caught Storm", IXI, 48, 48, "Caught Storm",
        "Lightning split the trunk open and the storm crawled into the crack. Ixi has heard it thinking down there for "
        "years, and the Split Wisps that leak out of it are getting stronger.",
        [k("Split Wisp", 6, zone=SS), boss("The Caught Storm", zone=SS)],
        "The bolt that made the Stormsplit didn't leave. It's down at the bottom in Thunder Hall, and I can hear it "
        "at night, turning over and over. The Split Wisps leaking out of the crack are pieces of it. Go down through "
        "the Stormsplit and set the Caught Storm free.",
        "I felt it go. Everyone at Highrest felt it, the hair on their arms stood up and then lay down.\n\nThe tree's "
        "quieter. I didn't know it could be."))

    # =================================================================================== 4. THE BOAT WITH NO WATER
    A(Q("ubq_a_boat_with_no_water", "A Boat with No Water", TALMAE, 47, 47, "Skywatcher's",
        "Something fell out of the sky onto the high boughs a season ago: a boat, lying across two branch tips with no "
        "water under it. Skywatcher Tal'mae wants someone to walk its deck.",
        [explore(*SKIFF, "Walk the deck of the Fallen Skiff")],
        "There's a boat lying across two branch tips past the ring. A boat, up here, with no water under it. Tel'zan "
        "calls it the Fallen Skiff. I've only seen it from the trunk, so walk its deck for me and tell me what it's "
        "made of.",
        "No nails, no tar, and the wood's grown into shape rather than cut? I don't know any shipwright who works "
        "like that, and I've met a few since the merge.\n\nSomebody built that to sail the sky, and that means "
        "somebody's up there."))
    A(Q("ubq_the_skiffs_guards", "The Skiff's Guards", TALMAE, 47, 48, "Wreckwarden's",
        "The Fallen Skiff came down with guardians, Skiff Sentinels of crystal and metal, and the Wreck Drones that "
        "crawl over the deck. They keep anyone from boarding.",
        [k("Skiff Sentinel", 5), k("Wreck Drone", 6)],
        "The Skiff Sentinels walk the deck and the Wreck Drones crawl over the hull, mending it, I think. Neither of "
        "them lets anyone near. Clear enough of them that I can climb aboard and look for the boat's log.",
        "The drones were mending a ship that's never going to sail again. They didn't know how to stop.\n\nThere's "
        "one guardian left, and it's the one that matters.",
        requires_quests=["ubq_a_boat_with_no_water"], nxt="ubq_the_skiff_warden"))
    A(Q("ubq_the_skiff_warden", "The Skiff Warden", TALMAE, 48, 48, "Skiffwarden",
        "One guardian stands at the Fallen Skiff's helm and hasn't moved since the boat came down. Tal'mae calls it "
        "the Skiff Warden, and the log is under its feet.",
        [boss("The Skiff Warden")],
        "The Skiff Warden stands at the helm of the Fallen Skiff, and it's standing on a box I'd give a lot to open. "
        "It hasn't moved since the boat came down, not once, not in the worst storm. Go and move it off that box.",
        "It fell over like a statue, and the box was right where I hoped. The log's inside.\n\nI can't read a word "
        "of it. Tel'zan might, down in the Settlement.",
        nxt="ubq_the_skiffs_log"))
    A(Q("ubq_the_skiffs_log", "The Skiff's Log", TALMAE, 48, 48, "Logkeeper's",
        "The Fallen Skiff's log is written in a script nobody at Highrest can read. Tal'mae wants it in Archivist "
        "Tel'zan's hands in the Great Settlement.",
        [deliver("ub_q_skiffs_log", "Take the Skiff's log down to Archivist Tel'zan in the Great Settlement")],
        "Tel'zan keeps the record of everything that's fallen on the tree since the merge, and this belongs in it. "
        "It's a long way down, and I'm not leaving my post. Take the log to the Great Settlement and put it in his "
        "hands, nobody else's.",
        "A ship's log, from the sky. And the Surveyor's core before it, and both of them came down on this tree.\n\n"
        "I can read a little of this. They were sailing toward the tree, not past it. They meant to come here.",
        turn_in_npc_id=TELZAN,
        grant_items=carry("ub_q_skiffs_log", "The Skiff's Log", "A slim book bound in something like pale leather, "
                          "its pages covered in a looping script. The ink shines when it's tilted.")))

    # =================================================================================== 5. THE CLIMBERS
    A(Q("ubq_thunderhawks", "Thunderhawks", MUZZI, 47, 47, "Hawkcatcher's",
        "Old Muzzi climbed with Ruk'tan and Zel'ji when they were young. He says the Thunderhawks on the Thunderhawk "
        "Reach have got bolder every year since, and now they take people off the branches.",
        [k("Thunderhawk", 7)],
        "The Thunderhawks nest on the Reach, and when I was young they'd only take a climber who'd fallen asleep. "
        "Now they'll come for anyone on the branch. Go out on the Thunderhawk Reach and knock them down.",
        "They'll remember that. Hawks have long memories, and so do I.\n\nWhen I was a boy this was just a tree. "
        "Then the merge came, and the sky came closer."))
    A(Q("ubq_old_thunderbeak", "Old Thunderbeak", MUZZI, 48, 48, "Thunderbeak",
        "The biggest of the Thunderhawks nests at the end of the Thunderhawk Reach. Old Muzzi calls it Old Thunderbeak, "
        "and it took two of his fingers sixty years ago.",
        [explore(*THUNDER_TIP, "Climb to the end of the Thunderhawk Reach"), boss("Old Thunderbeak")],
        "Old Thunderbeak took two fingers off this hand when I was younger than you. It's still out at the end of "
        "the Reach, bigger than ever and twice as mean. I can't climb out there anymore, so go out to the end of the "
        "Reach and bring it down for me.",
        "Sixty years, and it's done. I thought I'd feel something bigger.\n\nI just feel old. That's all right, I've "
        "earned it.", requires_quests=["ubq_thunderhawks"]))
    A(Q("ubq_quills_for_a_charm", "Quills for a Charm", MUZZI, 47, 48, "Quillwright's",
        "Old Muzzi is making a wind charm for Zel'ji, who climbed into the cloud and never came back down. A climber's "
        "charm is tied with Thunderhawk quills, for luck.",
        [fetch("ub_q_thunderhawk_quill", 5)],
        "Zel'ji went up into the cloud with her rope and didn't come back. Every climber who's gone up since has "
        "tied a charm for her on the way. I never did, because I was angry with her. I'm not angry anymore. Bring "
        "me Thunderhawk Quills from the Reach, and I'll make her one.",
        "These will do. They're strong, they'll ring in the wind.\n\nGive me a night to tie it. I've forgotten how, "
        "and my fingers are slower than they were.", requires_quests=["ubq_thunderhawks"],
        nxt="ubq_a_charm_for_zelji"))
    A(Q("ubq_a_charm_for_zelji", "A Charm for Zel'ji", MUZZI, 48, 48, "Charm-Tree",
        "Old Muzzi has tied a wind charm for Zel'ji, and it belongs on the Charm-Tree in the Cloudbreak with all the "
        "others. He can't climb that far now.",
        [explore(*CB_CHARMS, "Tie Muzzi's charm on the Charm-Tree in the Cloudbreak", zone=CB)],
        "Here's the charm. There's a bent branch halfway up the Cloudbreak, past Zel'ji's rope, and every climber "
        "who's gone up has tied something to it. Tie this one there for me. You'll hear it, because they all ring "
        "together.",
        "You heard them? That's every climber who went up. They're all still ringing.\n\nThank you. I'll sleep "
        "tonight, and that's not happened in a long time.",
        grant_items=carry("ub_q_muzzis_charm", "Muzzi's Charm", "A wind charm of bone beads and banded Thunderhawk "
                          "quills, tied with an old climber's knot. It rings when you move.")))

    # =================================================================================== 6. THE WEATHER
    A(Q("ubq_reading_the_wind", "Reading the Wind", INGRID, 47, 47, "Windreader's",
        "Ingrid Haugen is a mountaineer and a meteorologist from Tromso, and she's measuring the weather the tree "
        "makes. She needs readings from the ends of the Gale's two branches, where the wind comes in first.",
        [explore(*GALE_TOP, "Take a reading at the end of the Gale's upper branch"),
         explore(*GALE_TIP, "Take a reading at the end of the Gale's lower branch")],
        "Back home in Tromso I'd put an anemometer on a peak and leave it for a season. I can't do that here, "
        "because the harpies steal them. The wind hits the Gale first, so go out to the end of each of its branches "
        "and tell me how it feels on your face.",
        "Cold on the upper branch, warm and wet on the lower one? Then the tree's pulling air up its own trunk like "
        "a chimney.\n\nIt makes its own weather. I knew it did. I just needed someone to stand out there and feel it.",
        nxt="ubq_the_gale_riders"))
    A(Q("ubq_the_gale_riders", "The Gale-Riders", INGRID, 47, 48, "Galebreaker's",
        "The harpies of the Gale ride the wind the tree makes. The Gale-Rider Harpies dive on anyone on the branches, "
        "and the Gale Windcallers whip the wind up for them.",
        [k("Gale-Rider Harpy", 7), k("Gale Windcaller", 4)],
        "Every Gale-Rider Harpy rides the updraught off the trunk, and the Gale Windcallers make it stronger when they "
        "want to hunt. They've stolen every instrument I've put out. Break their flight so I can get some numbers "
        "that last longer than an afternoon.",
        "My barometer's been on that branch since morning, and it's still there.\n\nOn Earth I chased storms for a "
        "living. Here the storms chase me, and it's a nice change to win one.",
        nxt="ubq_gale_queen_skirra"))
    A(Q("ubq_gale_queen_skirra", "Gale Queen Skirra", INGRID, 48, 48, "Skirra's",
        "The Gale's harpies follow a queen who calls the wind down like a hammer. Ingrid has watched her flatten a "
        "branch's worth of lichen in one stroke.",
        [boss("Gale Queen Skirra")],
        "Gale Queen Skirra rules the Gale, and when she's angry she pulls the wind down out of the sky and drops it "
        "on you. I watched her strip a branch bare with one stroke. She's the reason the harpies are bold. Bring her "
        "down.",
        "The wind dropped the moment she fell. My instruments all went still at once.\n\nThat's the strangest "
        "reading I've ever taken, here or on Earth. The weather up here has a will, or it did."))

    # =================================================================================== 7. OUT ON THE TIER
    A(Q("ubq_moths_on_the_stair", "Moths on the Stair", RHOKA, 47, 47, "Stairwarden's",
        "Stairwarden Rhoka keeps the root stair down to Heartwatch, and the Gale Moths cluster on it where it's out of "
        "the wind. They panic in swarms when anyone climbs past.",
        [k("Gale Moth", 8)],
        "The Gale Moths shelter on the root stair and round the trunk ring, out of the wind. When somebody climbs "
        "past they all go up at once, right in your face, and twice now somebody's lost their footing. Clear them "
        "off the ring.",
        "I counted everybody up and everybody down today, and the numbers matched.\n\nThat hasn't happened since "
        "the newcomers started coming up."))
    A(Q("ubq_skinks_at_the_knots", "Skinks at the Knots", VOSH, 47, 47, "Knotkeeper's",
        "Ladderkeeper Vosh keeps the foot of the ladders on the Cloud Way. The Windscour Skinks on the trunk ring like "
        "the salt in the tarred rope, and they chew the knots.",
        [k("Windscour Skink", 8)],
        "The Windscour Skinks love the salt in tarred rope, and they've been chewing my knots at night. If a knot "
        "goes on the Cloud Way, somebody goes with it. Clear them off the trunk ring for me.",
        "Every knot's whole this morning. Grandfather would've been pleased.\n\nHe hung the last ladder, you know, "
        "the one at the very top. Nobody's climbed past it since the merge but him."))
    A(Q("ubq_counting_the_flock", "Counting the Flock", TAZZO, 47, 48, "Flockwatcher's",
        "Scout Tazzo watches the Wyvern Roosts for Gu'lok. The flock has spread to the far end of the bough, and he "
        "needs someone to go and see how far.",
        [explore(*ROOST_END, "Walk to the far end of the Wyvern Roosts")],
        "The roosts go further than anyone thinks, and Gu'lok wants to know how many there are. I can't go out there "
        "without the big one with the crest seeing me. Walk out to the far end of the roosts and count what you see "
        "on the way.",
        "That's more than I've ever counted, so the flock's been breeding up there all season.\n\nGu'lok's going to want every one of "
        "them, and he's going to need a bigger camp."))
    A(Q("ubq_humming_crystals", "Humming Crystals", NEEMA, 47, 48, "Crystalwatcher's",
        "Scout Neema has watched the Skiff Sentinels for nine days. Each one hums one low note, and she thinks the "
        "note comes from the crystal in its chest.",
        [fetch("ub_q_humming_crystal", 5)],
        "Every Skiff Sentinel hums one low note, and they all hum it together. I think it's the crystal in their "
        "chests, and I think it's how they talk. Bring me the Humming Crystals out of the sentinels on the wreck, "
        "and we'll see if they stop singing.",
        "Hold one to your ear. It's the same note, even out of the sentinel.\n\nTal'mae will want to hear this. So "
        "will Tel'zan, down in the Settlement."))
    return out
