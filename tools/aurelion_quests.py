"""
Aurelion's quests (54-55): the Aetherian capital, the sky's first city, opened to the ground because it can't face what
came out of the Crown's seal alone (docs/worldtree_brief.md, question 15: "proud, ugly and desperate"). Read by
tools/build_aurelion_quests.py, which holds them to every rule before anything is written. The map is
tools/handbuilt_worldtree_aurelion.py and the people are tools/build_aurelion.py. You come up the sky-bridge with the
Warden-Prime's report (afq_the_councils_thanks, the Anchorfields' last quest), and Gatewarden Tessa Vell takes it from
there.

A CITY, SO NOTHING SPAWNS: the quests here walk you round the rings and send you back out to the Anchorfields and the
Keel for what the city needs. No quest changes the map.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026: "aurelion is ancient, we are new"): the rings were built round the Spire over a
thousand years, the Eighth Ring fell in an old man's lifetime, and the player is the newcomer, learning it.

THE THREADS:
  The council: up the Grand Avenue to the herald, the proclamation that opened the gates, and the First Speaker, who
    needs proof of how far the Ascendancy has gone and then a voice for the ground in the hall.
  The House of the Patient Lens: Councillor Thalos Wren's survey wants lenses from the Keel, and the Academy wants to
    know whether the ground has scholars.
  The House of Long Memory: Councillor Idrel Marrowell measures the Spire Palace's doors. That's the city's piece of the
    sky's one mystery (docs/worldtree_brief.md): the Spire's oldest hall was built to a Kharad's height, with perches
    at a Veyr's grip, by Aetherian hands. A place built by one people for the other two.
  The allies from the arc (question 19): Ilaren Vey of the split house and Leandro Arrieta, the Earthborn who lived
    three years with the survey, waiting on the plaza. Leandro carries the wards' letters to the embassy; Ilaren takes
    you to the Gardens.
  The Eighth's Rest: the survivors of the fallen ring, their soup and their memorial.
  The Skydocks: fewer long-haulers every year, and the Ascendancy stripping the ones left.

THE RULES IT KEEPS: transplants are factionless; the Aetherians only ever say they don't know what the change was, and
nothing about the three peoples points at it. VOICE (Kyle): whole sentences the way a person says them, contractions,
no dashes, no sentence of one or two words, the useful thing first, every kill target named, no count beside an
objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

AU = "aurelion"
AF = "anchorfields"
KL = "keel"

# ---- the Bridgefoot and the Grand Plaza
TESSA, HERALD, ILAREN, LEANDRO = "au_gate_warden", "au_plaza_herald", "au_ilaren", "au_leandro"
# ---- the Spire and the Council Ring
KEEPER, SPEAKER, THALOS, IDREL = "au_palace_keeper", "au_first_speaker", "au_councillor_lens", "au_councillor_memory"
# ---- the inner and outer rings
ACADEMY, TAMSIN, TAVIA, HAMID = "au_academy_master", "au_gardener", "au_ambassador", "au_embassy_aide"
GARRET, CORRIN, YSOLDE = "au_dockmaster", "au_eighth_elder", "au_soup_cook"

#: the whole city is the hub
HUB_GIVERS = {TESSA, HERALD, ILAREN, LEANDRO, KEEPER, SPEAKER, THALOS, IDREL, ACADEMY, TAMSIN, TAVIA, HAMID, GARRET,
              CORRIN, YSOLDE}
#: the Aetherians pay the Aetherians; Leandro and Hamid are Earthborn and pay nobody
SKY_GIVERS = HUB_GIVERS - {LEANDRO, HAMID}


def k(target, n, zone=AF):
    return kill(target, n, zone=zone)


def explore(x, y, label, zone=AU, radius=3):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Ascendancy Warden": [("au_q_marching_orders", "Ascendancy Marching Orders", "A slate of orders in a clipped "
                           "military hand, sealed with the Ascendancy's mark and not the council's.")],
    "Keel-Crystal Shard": [("au_q_keel_lens", "Keel-Grown Lens", "A disc of crystal that grew in the dark under the "
                            "Third Anchor. Held up to the light, it shows things a little closer than they are.")],
    "Garden Repair-Drone": [("au_q_clean_graft", "Clean Gold Graft", "A cutting of gold-apple wood, wrapped and "
                             "sealed by a Garden Repair-Drone that never stopped doing its job properly.")],
    "Tiltside Goat": [("au_q_goat_shank", "Tiltside Goat Shank", "A lean shank off a Tiltside Goat. It'll take all "
                       "day in the pot, and it'll be worth it.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [97]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=AU, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
GUESTHOUSE = (110, 219)       # the Arro guesthouse's door, on the Bridgefoot square
EXCHANGE = (147, 222)         # the Exchange's steps
SKIFFS = (102, 223)           # the skiff dock
COLOSSI = (130, 186)          # between the colossi, at the plaza's south end
FOUNTAIN = (130, 175)         # the light fountain, from the plaza's south side
SPIRE_DOORS = (130, 134)      # the Spire Palace's great doors, at the top of the stair
WEST_COLUMN = (121, 134)      # the winged column west of the stair
EAST_GUARD = (142, 128)       # the guardian statue on the palace isle's east side
EMBASSY_STEPS = (213, 184)    # the Ground Embassy's steps
CONSERVATORY = (83, 109)      # the great conservatory's doors
ORCHARD = (75, 151)           # the gold orchard
MEMORIAL = (54, 85)           # the crystal memorial at the Eighth's Rest
EIGHTH_STUB = (31, 54)        # the end of the Eighth Ring's last stub, where it broke off
DOCK_RIM = (229, 74)          # the Skydocks' rim, where the long-haulers moor


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE BRIDGEFOOT
    A(Q("auq_where_everything_is", "Where Everything Is", TESSA, 54, 54, "Bridgefoot",
        "Gatewarden Tessa Vell wants the city's first guest from the ground to know where to sleep, where to sell and "
        "where to catch a skiff before anything else happens.",
        [explore(*GUESTHOUSE, "Find the Arro guesthouse"),
         explore(*EXCHANGE, "Find the steps of the Exchange"),
         explore(*SKIFFS, "Find the skiff dock")],
        "Before the council gets hold of you, learn the Bridgefoot. The guesthouse is on the west side of the square, "
        "the Exchange is on the east, and the skiffs go from the dock past the guesthouse. Walk round all three, so "
        "you aren't asking a guard for directions in front of the whole city.",
        "Now you know more of Aurelion than most of the Ascendancy's recruits do.\n\nThe Arros have kept that "
        "guesthouse for four hundred years, and Sela's been fretting since the change about what a ground-walker eats. Go and "
        "let her find out."))
    A(Q("auq_up_the_grand_avenue", "Up the Grand Avenue", TESSA, 54, 54, "Avenue",
        "The Warden-Prime's report says the outer rings are safe because of you. Gatewarden Tessa Vell is sending you up "
        "the Grand Avenue to the herald, who'll take you before the council.",
        [explore(*COLOSSI, "Walk between the colossi into the Grand Plaza"),
         explore(*FOUNTAIN, "Stand at the light fountain")],
        "The Warden-Prime's report has gone up to the council, and the council wants to see the newcomer it's about. Walk "
        "straight up the avenue from the gate, between the colossi, and stand by the light fountain. Herald Odric Fane "
        "will find you. He's been waiting there since dawn.",
        "So you're the one in the Warden-Prime's report. You're smaller than I pictured.\n\nI'm sorry, that was rude. I've read nine "
        "hundred years of proclamations from this plaza, and not one of them was about somebody from the ground. Stay "
        "a moment, because I've got one more to read for you.",
        turn_in_npc_id=HERALD))

    # =================================================================================== 2. THE COUNCIL
    A(Q("auq_the_shortest_proclamation", "The Shortest Proclamation", HERALD, 54, 54, "Herald's",
        "Herald Odric Fane read the proclamation that opened Aurelion to the ground. He wants you to carry his copy of "
        "it to First Speaker Aldren Sorvaine, so the speaker can see who it was for.",
        [deliver("au_q_proclamation", "Take the herald's copy of the proclamation to the First Speaker in the "
                 "Council Hall")],
        "The proclamation that opened our gates was the shortest in the record. The council argued for a hundred years "
        "and then wrote eleven words, because nobody could bear to write any more. Take my copy up past the Spire to "
        "the Council Hall, and give it to the First Speaker. He'll want to look you in the eye.",
        "Eleven words, and the herald's copied them out in his best hand. He was always better at this than we "
        "were.\n\nI'll be honest with you, because the houses won't. We didn't open the gates out of respect. We opened "
        "them because something came out of the Crown's seal that the city can't face alone, and the Ascendancy has "
        "stopped asking us what it's allowed to do. That's a proud admission and an ugly one, and you're owed it.",
        turn_in_npc_id=SPEAKER, requires_quests=["auq_up_the_grand_avenue"],
        grant_items=carry("au_q_proclamation", "The Herald's Copy", "A long strip of white vellum, nearly all of it "
                          "empty, with eleven words in gold ink at the top and the council's seal below.")))
    A(Q("auq_how_far_it_has_gone", "How Far It Has Gone", SPEAKER, 54, 55, "Speaker's",
        "The Ascendancy says it holds the Second Anchor on the council's orders. First Speaker Aldren Sorvaine never "
        "gave them. He wants the orders the Ascendancy Warden there actually carries.",
        [fetch("au_q_marching_orders", 6)],
        "The Ascendancy took the Second Anchor and told the wardens it was on the council's word. I never gave that "
        "word, and neither did any house. Every Ascendancy Warden at that camp carries written orders. Bring me enough "
        "of them that the houses can't call it one captain's mistake.",
        "These are sealed with the Ascendancy's own mark, and not one of them names the council.\n\nShe's stopped "
        "pretending. The houses will read these tonight, and they'll have to admit what I've been saying for a "
        "season. Our army answers to its general now, not to us.",
        requires_quests=["auq_the_shortest_proclamation"]))
    A(Q("auq_a_voice_in_the_hall", "A Voice in the Hall", SPEAKER, 55, 55, "Envoy's",
        "First Speaker Aldren Sorvaine wants the ground heard in the Council Hall, not just looked at. He's sending you "
        "to Ambassador Tavia Morrane at the Ground Embassy to tell her so.",
        [explore(*EMBASSY_STEPS, "Climb the steps of the Ground Embassy")],
        "The houses have looked at the ground and the Earthborn for a hundred years and listened for about a week. I want that to "
        "change before the Ascendancy changes it for us. Go round to the Ground Embassy and tell Ambassador Morrane "
        "that the embassy speaks in the hall from now on, at every sitting. She'll pretend she isn't surprised.",
        "He said every sitting? Not just the ones about the seal?\n\nI've written to him eleven times asking for that. "
        "Eleven letters, and it took a ground-walker standing on my steps. I'm not going to complain. Come in, and "
        "mind the mortar on the doorframe, because it isn't dry.",
        turn_in_npc_id=TAVIA, requires_quests=["auq_how_far_it_has_gone"]))

    # =================================================================================== 3. THE PATIENT LENS
    A(Q("auq_lenses_from_the_keel", "Lenses From the Keel", THALOS, 54, 55, "Lensgrinder's",
        "Councillor Thalos Wren's survey grinds its lenses from crystal that grows in the dark. The Keel-Crystal Shard "
        "under the Third Anchor is made of the best of it.",
        [fetch("au_q_keel_lens", 6)],
        "The survey's lenses are cut from dark-grown crystal, and there's none darker than the crystal under the Third "
        "Anchor. Every Keel-Crystal Shard down in the Keel carries a lens inside it, already ground, if you break it "
        "cleanly. The Warden-Prime will let you in. He owes you that much and more.",
        "Look through that one. You can count the leaves on the tree from here.\n\nThe Patient Lens has watched your "
        "tree for sixty years through glass half this clear. The other houses called it a waste of crystal. I'll grind "
        "these into the survey's new glass, and then I'll invite them to look."))
    A(Q("auq_does_the_ground_have_scholars", "Does the Ground Have Scholars", THALOS, 55, 55, "Scholar's",
        "The Academy's students have been asking whether the ground has scholars. Councillor Thalos Wren has the "
        "survey's notes that answer it, and he wants them in the Master of the Academy's hands.",
        [deliver("au_q_survey_notes", "Take the survey's notes to the Master of the Academy")],
        "Halvric Oune's students keep asking whether the ground has scholars, and Halvric keeps telling them nobody "
        "knows. The survey knows. Take him these notes on the ground's libraries and colleges, and the Earthborn's "
        "universities too. He won't enjoy being wrong in front of his faculty, so be kind about it.",
        "The Earthborn kept libraries of a million books? And the ground's magi had a city that floated, on a world "
        "nobody up here believed had cities at all?\n\nI've taught for eight centuries, and I've just been handed a "
        "reading list. Thank you. I mean that, though I'll deny it in the faculty room.",
        turn_in_npc_id=ACADEMY, requires_quests=["auq_lenses_from_the_keel"],
        grant_items=carry("au_q_survey_notes", "The Survey's Notes on the Ground", "A thick bundle of the survey's "
                          "notes on the ground's scholars, with a page at the back in an Earthborn hand.")))

    # =================================================================================== 4. LONG MEMORY
    A(Q("auq_the_doors_are_too_big", "The Doors Are Too Big", IDREL, 54, 55, "Measurer's",
        "Councillor Idrel Marrowell of the House of Long Memory says the Spire Palace was built for somebody taller "
        "than an Aetherian. She wants you to look at it with fresh eyes before the other houses tell you what to see.",
        [explore(*SPIRE_DOORS, "Stand at the Spire Palace's great doors"),
         explore(*WEST_COLUMN, "Look up at the winged column beside the stair"),
         explore(*EAST_GUARD, "Look at the guardian on the palace isle's east side")],
        "Everyone in Aurelion walks past the Spire every day and never looks at it. You haven't learned not to look "
        "yet. Go and stand at the great doors, then the winged column by the stair, then the guardian on the isle's "
        "east side, and tell me what's wrong with all three.",
        "Too big, yes. The doors, the column's steps, the guardian's reach. The keepers say it's grandeur, and "
        "they've said it for a thousand years.\n\nMy house says grandeur doesn't need a step a giant could climb "
        "comfortably. It's why the council laughs at us. You're welcome to laugh too, but you looked first, and "
        "that's more than they've done.",
        requires_quests=["auq_up_the_grand_avenue"]))
    A(Q("auq_built_for_guests", "Built for Guests", IDREL, 55, 55, "Longmemory",
        "Councillor Idrel Marrowell took rubbings of the oldest hinge plates on the Spire's doors. She wants Keeper of "
        "the Spire Ulmar Seyth to see what they say.",
        [deliver("au_q_hinge_rubbing", "Take the hinge rubbing to the Keeper of the Spire")],
        "I took these rubbings off the oldest hinge plates on the great doors, the ones the keepers have polished for a "
        "thousand years without reading. The script is ours, an old form of it. The measurements beside it aren't. "
        "Take them to Ulmar Seyth. He won't listen to me, but he might listen to you.",
        "That's our script, the oldest form of it. And those are a mason's marks.\n\nThe doors are cut to a Kharad's "
        "height. The ledge under the high windows is set at a Veyr's grip, for perching. Aetherian masons built the "
        "Spire, and they built it for the other two peoples to walk into. We've always said nobody knows who raised "
        "it, and it was us all along. We just never asked who we raised it for.",
        turn_in_npc_id=KEEPER, requires_quests=["auq_the_doors_are_too_big"],
        grant_items=carry("au_q_hinge_rubbing", "Hinge Rubbing", "Charcoal on thin paper, taken off a hinge plate "
                          "as tall as a door: a line of old Aetherian script and a column of measurements.")))

    # =================================================================================== 5. THE ALLIES ON THE PLAZA
    A(Q("auq_letters_from_the_wards", "Letters From the Wards", LEANDRO, 54, 54, "Wardfriend's",
        "Leandro Arrieta lived three years as one of the scholar houses' Earthborn wards. The wards still at Lenswatch "
        "gave him letters for the Ground Embassy, and he wants them in Hamid Sadeghi's hands today.",
        [deliver("au_q_wards_letters", "Take the wards' letters to Hamid Sadeghi at the Ground Embassy")],
        "These are from the Earthborn still living as the houses' wards. Some of them have been up here longer than "
        "me, and they've never been allowed to write to anyone. Hamid at the embassy knows what to do with them. Go "
        "now, please, before somebody on the council decides letters need a permit.",
        "There are names in here I've been looking for since I got the job. A nurse from Lyon, a man from Osaka, "
        "and a whole family from Manila.\n\nThey've been guests of the houses for three years, and guests who can't "
        "leave aren't guests. I'll write back to every one of them tonight.",
        turn_in_npc_id=HAMID,
        grant_items=carry("au_q_wards_letters", "Bundle of Wards' Letters", "A stack of letters tied with survey "
                          "cord, written in a dozen Earth languages on Aetherian paper.")))
    A(Q("auq_the_oldest_trees", "The Oldest Trees", ILAREN, 54, 54, "Gardenwalker's",
        "Ilaren Vey says nobody understands Aurelion until they've walked the Gardens. He wants you to go to the "
        "conservatory and the gold orchard, and meet Gardener Tamsin Ashgrove.",
        [explore(*CONSERVATORY, "Walk to the great conservatory's doors"),
         explore(*ORCHARD, "Walk through the gold orchard")],
        "My house is split down the middle, and the half that still speaks to me says I'm too fond of the ground. "
        "They're welcome to think so. I'll show the ground the best thing we have. Walk west round the Inner Ring to the Gardens, see the "
        "conservatory and the orchard, and find Tamsin Ashgrove. Don't pick an apple, because she counts them.",
        "You've seen the orchard, then, and you didn't pick anything, which puts you ahead of most of the council.\n\nThose trees were planted when the "
        "Inner Ring was laid. Some of them are older than the Academy. Three of them have stopped fruiting in my time, "
        "and the books don't tell me why.",
        turn_in_npc_id=TAMSIN))
    A(Q("auq_grafts_from_the_estate", "Grafts From the Estate", TAMSIN, 54, 55, "Grafter's",
        "House Vaelith's estate garden in the Anchorfields was grown from cuttings of these Gardens. Gardener Tamsin "
        "Ashgrove wants clean grafts back from it, carried by the Garden Repair-Drone that still tends it.",
        [fetch("au_q_clean_graft", 5)],
        "House Vaelith took cuttings from this orchard when they built their estate, centuries ago. Their trees are "
        "younger and stronger than mine now. Every Garden Repair-Drone on that estate carries sealed grafts in its "
        "kit, and they seal them properly, whatever else has gone wrong with them. Bring me clean wood, and I'll graft "
        "it onto the trees that have stopped.",
        "These are perfect. The drones never forgot how to seal a graft, even after they forgot everything else.\n\n"
        "It's a strange thing, mending the city's oldest trees with cuttings of themselves. I suppose that's what the "
        "Gardens have always been. Come back in a few years and see whether they took.",
        rewards=list(CYCLE[10]), requires_quests=["auq_the_oldest_trees"]))

    # =================================================================================== 6. THE EIGHTH'S REST
    A(Q("auq_soup_for_the_eighth", "Soup for the Eighth", YSOLDE, 54, 55, "Souper's",
        "Mother Ysolde Marsh feeds everyone at the Eighth's Rest on the council's bread and the houses' coin. She "
        "wants meat for the pot, and the Tiltside Goat out on the Anchorfields' Listing Isle is the best there is.",
        [fetch("au_q_goat_shank", 6)],
        "Bread and coin don't make a soup, wherever you're from. Meat makes a soup. The Tiltside Goat out on the Listing Isle is lean and "
        "stubborn, and it cooks down into something that'll keep an old man warm all night. Bring me shanks, and I'll "
        "feed the whole Rest on them.",
        "Look at the size of these. I'll have the pot going by sundown.\n\nThe Eighth used to keep goats, you know. "
        "We had pasture on the outermost ring, and the herds went down with it. Half of the Rest will taste this "
        "and cry, and the other half will ask for more. Both are fine."))
    A(Q("auq_what_the_eighth_remembers", "What the Eighth Remembers", CORRIN, 55, 55, "Eighthsworn",
        "Elder Corrin Ashlane watched the Eighth Ring fall. He wants a guest from the ground to stand at the memorial, "
        "then walk out to where the last stub of the ring breaks off.",
        [explore(*MEMORIAL, "Stand at the crystal memorial"),
         explore(*EIGHTH_STUB, "Walk to the end of the Eighth Ring's last stub")],
        "The memorial has every name we lost. Stand by it a while, then walk out along the stub past the Rest to "
        "where the ring breaks off. That's as close to home as any of us can get now. Come back and tell me what "
        "you saw out there.",
        "You saw nothing at all, and a long way down. That's the whole of the view.\n\nThe Eighth didn't fall all at once. It "
        "cracked for a hundred years before it went, and the council measured the cracks and argued. My grandmother "
        "said the ring was older than the council, and that whoever built it knew how to keep it up. Nobody up here "
        "knows any more.",
        requires_quests=["auq_soup_for_the_eighth"]))

    # =================================================================================== 7. THE SKYDOCKS
    A(Q("auq_fewer_every_year", "Fewer Every Year", GARRET, 54, 55, "Dockwarden's",
        "Dockmaster Garret Lune has watched the long-haulers dwindle for years. Now the Ascendancy Crystal-Weaver "
        "strips the crystal out of their engines for the camp at the Second Anchor.",
        [explore(*DOCK_RIM, "Look out from the Skydocks' rim"),
         k("Ascendancy Crystal-Weaver", 8)],
        "Look out from the rim first, and count the berths with nothing in them. Then go to the Anchorfields. Every "
        "Ascendancy Crystal-Weaver at the Second Anchor's camp is wearing crystal pulled out of a long-hauler's "
        "engine, and I know because I signed for some of it. Make them stop.",
        "The camp's shield pylon has gone dark, and I've had a captain ask me whether it's safe to put in again.\n\n"
        "It's not much, but it's the first good question anyone's asked me in a year. The Ascendancy takes what it "
        "needs from the city and calls it defence. Their fortresses on the Ascendant Bastions are built out of things "
        "like my ships."))
    A(Q("auq_the_free_skiffs", "The Free Skiffs", GARRET, 55, 55, "Skiff-Runner's",
        "A few skiff captains still fly out to the Ascendant Bastions, to a wreck the Ascendancy can't reach. Dockmaster "
        "Garret Lune wants you on the next one, with a letter for the captain who runs the camp there.",
        [deliver("au_q_garret_letter", "Take Garret's letter to Captain Isolde Marrane at Dawnspear Wreck")],
        "There's a camp on the Bastions, in the wreck of a war-skiff called the Dawnspear, and the deserters there send "
        "word of what the yard's building. The free skiffs fly to it from the end of my docks, past the airship dock on "
        "the rim. Take this letter to Captain Isolde Marrane. She'll want to know the city's finally listening.",
        "Garret Lune's hand. He's the only one in Aurelion who answered my letters while the council was arguing.\n\n"
        "Welcome to Dawnspear Wreck. It isn't much, but it's the only place on the Bastions where nobody's trying to "
        "kill you.",
        turn_in_npc_id="ab_wreck_captain", requires_quests=["auq_fewer_every_year"],
        grant_items=carry("au_q_garret_letter", "Garret's Letter", "A letter sealed with the Skydocks' anchor mark, "
                          "addressed to Captain Isolde Marrane of the Dawnspear.")))
    return out
