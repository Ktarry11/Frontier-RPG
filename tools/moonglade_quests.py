"""
Moonglade's quests: Nighthaven and the Cenarion Circle, the Wakened on the west shore, and the Circle's watch out over
the sick lands. Levels 55-60. Read by tools/build_moonglade_quests.py, which holds them to every rule before anything
is written. The vision is docs/moonglade_brief.md.

Kyle, 18 Nov 2026: "moonglade can be quite a decent size but is still a town and hub. there will be an inn and a
flight path. no monsters", and the Circle and the Wakened "are in good standing with each other. The wakened is
transplant led while cenarion circle is true to lore. Moonglade looks similar but 'something else is waking up'".

THE STORY. Nothing in the valley needs killing, so its quests are its people's stories and the Circle sending you back
out to the sick lands it watches. Underneath them all, the glade is quiet in a way that frightens the people who know
it best. The sleepers in the Barrow Dens talk in their sleep; the arch in the north woods is warm at night; the great
moonwell runs over in the dark; the fish swim toward the island and the guests at the inn dream of a door under the
water. Nobody here knows what's waking, and these quests don't answer it: the three dungeons will.

THE THREADS:
  Ingrid Sandvik, who studied sleep for twenty years and woke up in the Dream's grass, and what the sleepers say.
  Danny Kowalczyk, who wants to fall asleep and wake up in Buffalo, and Adaeze Okafor, who won't let him try alone.
  Hamish MacLeod's wall of last memories, and the carving he makes for Danny.
  Hamuul Runetotem and the tauren who carried their totems out of Thunder Bluff.
  The Circle's watch: Felwood's satyrs and the Black Gate, the rot under Timbermaw Hold, the wound in Deadwind.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

# ---- the maps (the key the game passes on a kill: the map's name lowercased, spaces to underscores, no apostrophes)
MG = "moonglade"
NF, JD, RD = "north_felwood", "jaedenar", "the_rotroot_deeps"
TT = "timbermaw_tunnel"

# ---- the people: the Cenarion Circle
RABINE, HAMUUL, REMULOS, BUNTHEN = "mg_rabine", "mg_hamuul", "mg_remulos", "mg_bunthen"
AEDRIS, MAHALA, LETHIEL, TAERENAS = "mg_moonwell_keeper", "mg_tauren_elder", "mg_arch_watcher", "mg_barrow_warden"
MYLLA, ILYSSA, TALOWYN = "pt_mg_herbs", "pt_mg_fish", "mg_innkeeper"
# ---- the Wakened
SANDVIK, ADAEZE, HAMISH, MEILIN = "mg_sandvik", "mg_infirmary", "mg_carver", "mg_gardener"
DANNY = "mg_dreamer"
# ---- outside
SELVA, LONGTREAD, AELYRA = "tm_windtalker", "taurajo_elder", "es_arch_druid"

CIRCLE_GIVERS = {RABINE, HAMUUL, REMULOS, BUNTHEN, AEDRIS, MAHALA, LETHIEL, TAERENAS, MYLLA, ILYSSA, TALOWYN, SELVA}
WAKENED_GIVERS = {SANDVIK, ADAEZE, HAMISH, MEILIN, DANNY}
#: everyone in the valley is in town
HUB_GIVERS = (CIRCLE_GIVERS | WAKENED_GIVERS) - {SELVA}


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=MG, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Warpwood Treant": [("mg_q_warpwood_heart", "Warpwood Heartwood", "A length of heartwood from a treant the fel "
                         "turned. Under the black bark it's still pale and sound.")],
    "Moonlit Wisp": [("mg_q_wisp_light", "Caught Wisp-Light", "A soft white light that settles in your palm and "
                      "doesn't burn. It dims when you're frightened and brightens when you're not.")],
    "Seepage Ooze": [("mg_q_bloodvenom_residue", "Bloodvenom Residue", "A clot of the Bloodvenom's poison, green "
                      "and slow, sealed in wax so it can't touch the skin.")],
    "Dissolving Stag": [("mg_q_dissolving_antler", "Dissolving Antler", "An antler from a Deadwind stag, soft at the "
                         "tip where it's melting and hard at the base where it isn't yet.")],
    "Legash Satyr": [("mg_q_satyr_horn", "Legash Satyr Horn", "A satyr's horn, ridged and black. The Circle keeps a "
                      "count of them, and has for ten thousand years.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

#: reward triples, (slot, kind, type, identity), cycled through so every spec gets something (the builder checks it)
CYCLE = [
    [("chest", "armor", "mail", "hunter"), ("waist", "armor", "cloth", "caster"), ("feet", "armor", "plate", "tank")],
    [("hands", "armor", "leather", "agility"), ("shoulder", "armor", "mail", "tide_healer"), ("neck", "armor", None, "caster")],
    [("back", "armor", None, "physical"), ("wrist", "armor", "cloth", "healer"), ("legs", "armor", "plate", "strength")],
    [("head", "armor", "leather", "bear"), ("ring", "armor", None, "healer"), ("hands", "armor", "mail", "earthen")],
    [("main_hand", "weapon", "staff", "caster"), ("chest", "armor", "leather", "strength"), ("waist", "armor", "plate", "plate_healer")],
    [("shoulder", "armor", "cloth", "caster"), ("legs", "armor", "leather", "agility"), ("wrist", "armor", "plate", "tank")],
    [("off_hand", "weapon", "shield", "haste_caster"), ("feet", "armor", "mail", "hunter"), ("chest", "armor", "cloth", "spirit_healer")],
    [("off_hand", "weapon", "shield", "shield_tank"), ("legs", "armor", "leather", "bear"), ("hands", "armor", "cloth", "arcane")],
    [("main_hand", "weapon", "polearm", "strength"), ("head", "armor", "cloth", "healer"), ("hands", "armor", "leather", "feral")],
    [("legs", "armor", "mail", "storm"), ("back", "armor", None, "caster"), ("shoulder", "armor", "plate", "strength")],
    [("main_hand", "weapon", "staff", "agility"), ("waist", "armor", "leather", "agility"), ("ring", "armor", None, "strength")],
    [("chest", "armor", "plate", "plate_healer"), ("feet", "armor", "cloth", "caster"), ("wrist", "armor", "mail", "wildheart")],
    [("ranged", "weapon", "bow", "hunter"), ("head", "armor", "mail", "tide_healer"), ("legs", "armor", "cloth", "caster")],
    [("main_hand", "weapon", "dagger", "agility"), ("shoulder", "armor", "leather", "healer"), ("feet", "armor", "plate", "strength")],
    [("off_hand", "weapon", "tome", "healer"), ("hands", "armor", "plate", "tank"), ("waist", "armor", "mail", "hunter")],
    [("main_hand", "weapon", "mace_1h", "healer"), ("chest", "armor", "leather", "wildheart"), ("neck", "armor", None, "strength")],
    [("main_hand", "weapon", "sword_2h", "strength"), ("wrist", "armor", "leather", "agility"), ("head", "armor", "cloth", "caster")],
]
_cyc = [0]


def R():
    """The next reward triple off the cycle."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=MG, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# --------------------------------------------------------------------------------------------- places in the valley
GREAT_MOONWELL, TAUREN_MEMORIAL, PIER_END = (174, 86), (184, 56), (138, 88)
SHRINE, ARCH, FALLS_VIEW, NORTH_SHORE = (34, 46), (100, 27), (114, 44), (84, 48)
MEMORY_WALL, DREAM_COTS, LONGHOUSE, BARROW_DOOR = (42, 82), (30, 116), (24, 94), (34, 156)


def build():
    out = []
    A = out.append

    # ======================================================================================= 1. UP INTO THE GLADE
    A(Q("mg_the_way_up", "The Way Up", SELVA, 55, 55, "Wayfarer's",
        "The Moonglade passage past Windtalker Selva Brightpelt's spring was buried for three years, and the druids "
        "dug it out from their side. Selva has filled a jar from her spring for the Circle, so they'll know what "
        "the mountain's water tastes of down here.",
        [deliver("mg_q_spring_jar", "Take Selva's jar of spring water to Rabine Saturna in Nighthaven")],
        "Up the Moonglade passage, past the boulders they rolled aside, and out into the glade. Give the jar to "
        "Rabine Saturna in Nighthaven. Tell him the water still tastes of Felwood, and that I'm sorry for it.",
        "Felwood in a jar. I'd know that taste anywhere, and I wish I didn't.\n\nThank Selva for me. The Timbermaw "
        "kept the tunnel for us through three bad years, and we didn't even know they were doing it. Welcome to "
        "Moonglade.",
        turn_in_npc_id=RABINE, zone=TT,
        grant_items=carry("mg_q_spring_jar", "Jar of Spring Water", "A stoppered jar of water from Selva's spring. "
                          "It's cold, and there's a faint green taint in it when you hold it to the light.")))
    A(Q("mg_welcome_to_nighthaven", "Welcome to Nighthaven", RABINE, 55, 55, "Nighthaven",
        "Rabine Saturna keeps Nighthaven for the Cenarion Circle, and he wants you to see the glade properly before "
        "you're any use to it. Start at the great moonwell, then take his letter across the lake to the Wakened.",
        [explore(*GREAT_MOONWELL, "Stand at the great moonwell in Nighthaven's square"),
         deliver("mg_q_rabine_letter", "Take Rabine's letter to Dr. Ingrid Sandvik on the west shore")],
        "The great moonwell's in the square, a few steps north of here. Look into it for a while. Then follow the shore "
        "road round to the west side, where the Wakened live, and give Dr. Sandvik this letter. She'll explain them "
        "better than I can.",
        "Rabine writes the politest letters in the whole of Kalimdor. He's asking me to look after you, and to tell "
        "you how we got here.\n\nYou'd better sit down. It's not a short story, and you'll want to hear it before you hear "
        "anybody else's.",
        nxt="mg_the_first_morning", turn_in_npc_id=SANDVIK,
        grant_items=carry("mg_q_rabine_letter", "Rabine's Letter", "A letter sealed with a pressed leaf, addressed in "
                          "a careful hand to Dr. Ingrid Sandvik.")))
    A(Q("mg_the_first_morning", "The First Morning", SANDVIK, 55, 55, "Morning",
        "When the worlds came together, the transplants who came through near Moonglade arrived asleep. Dr. Ingrid "
        "Sandvik woke up on the grass by the lake with a druid standing over her, and she wants you to see the two "
        "places that tell the rest of it: the wall where the Wakened carve their last memories, and the cots where "
        "the ones who don't wake are kept.",
        [explore(*MEMORY_WALL, "Read the wall of last memories"),
         explore(*DREAM_COTS, "Sit for a while by the dream cots outside the infirmary")],
        "I spent twenty years in Trondheim studying sleep, what the brain does at night and why it dreams. I'd have "
        "told you I knew everything about it from the outside. Now go and look at the wall, and then at the cots, and come "
        "back and tell me which of them frightened you more.",
        "It's the cots, isn't it? It's always the cots.\n\nThe ones on the wall woke up and remembered something. "
        "The ones on the cots are still dreaming, and none of us knows what about. That's the question the Wakened are here to answer, "
        "and the Circle's trying to answer it too, from the other side."))

    # ======================================================================================= 2. THE WAKENED
    A(Q("mg_the_last_thing_you_remember", "The Last Thing You Remember", HAMISH, 56, 56, "Carver's",
        "Hamish MacLeod started the wall of last memories with his mother's kitchen on the Isle of Lewis. Every new "
        "Wakened carves a plank now, and he's out of wood, because the Circle won't let anyone cut a living tree in "
        "the glade. He's found a way round it that the druids have agreed to, just about.",
        [fetch("mg_q_warpwood_heart", 6)],
        "The Warpwood Treants in North Felwood were trees once, before the fel got into them. Under the bark the "
        "heartwood's still sound. Put them out of their misery and bring me the heartwood. The Circle says that's "
        "kinder than leaving them, and I'd like to think they're right.",
        "Clean as the day it grew, under all that black.\n\nThere's a new lad, came through last month, who can't "
        "remember anything but a red bus in the rain. This plank's his. It'll be the first thing on the wall that "
        "came out of Felwood clean.",
        nxt="mg_a_carving_for_danny"))
    A(Q("mg_a_carving_for_danny", "A Carving for Danny", HAMISH, 56, 56, "Whittled",
        "Hamish has carved a small plank for Danny Kowalczyk, the Wakened who keeps trying to fall asleep and wake "
        "up back home in Buffalo. Danny's never carved anything for the wall. Hamish thinks he might, if somebody "
        "else starts it for him.",
        [deliver("mg_q_danny_carving", "Give Hamish's carving to Danny Kowalczyk by the dream cots")],
        "It's his house, as near as I could get it from what he's told me. A porch, two wee boys on the steps and a "
        "dog I've made up. Danny's usually by the cots. Don't tell him it's from me until he's looked at it.",
        "That's the porch. That's exactly the porch, and the dog's wrong, we never had a dog.\n\nTell Hamish I'll "
        "finish it. I'll put the dog on. The boys always wanted one, and I always said next year.",
        turn_in_npc_id=DANNY,
        grant_items=carry("mg_q_danny_carving", "Hamish's Carving", "A small plank carved with a house, a porch, two "
                          "boys on the steps and a dog nobody asked for.")))
    A(Q("mg_the_man_who_wants_to_sleep", "The Man Who Wants to Sleep", DANNY, 57, 57, "Sleepless",
        "Danny Kowalczyk was asleep in Buffalo when the worlds came together, and he woke up here. He's convinced "
        "that if he falls asleep the right way, in the right place, he'll wake up back there with his wife and his "
        "boys. Tonight he wants to try it on the north shore, where the moonlight lies on the water, and he doesn't "
        "want to do it alone.",
        [explore(*NORTH_SHORE, "Sit with Danny on the north shore while he tries to sleep")],
        "Ingrid says it doesn't work like that, and Adaeze says I'm going to hurt myself. Maybe they're right. Come "
        "and sit with me on the north shore, that's all I'm asking, and if I don't wake up in the morning, you can "
        "tell them they were wrong.",
        "I did sleep, and I dreamed about the porch, and the boys were there, and I could hear them, but they couldn't "
        "hear me.\n\nI woke up here again. I knew I would. I think I'm going to stop trying for a while, and I "
        "think I'm going to finish that carving."))
    A(Q("mg_waking_badly", "Waking Badly", ADAEZE, 57, 57, "Nightnurse",
        "Some of the Wakened still wake badly, sitting up in the dark not knowing which world they're in. Nurse "
        "Adaeze Okafor has found that the soft light of a wisp calms them faster than anything she could give "
        "them in Lagos. The gentle wisps of South Felwood give their light up freely when they fade.",
        [fetch("mg_q_wisp_light", 6)],
        "The Moonlit Wisps drift through South Felwood, round the Emerald Sanctuary. When they fade, their light "
        "stays behind for a while. Catch it in your hands and bring it to me. I'll hang it over the cots, and "
        "nobody will wake up in the dark again.",
        "Look at that. It's like the night lights we had on the ward, the ones the children liked.\n\nI worked nights "
        "for eleven years. The worst moment is always the same one, when somebody opens their eyes and doesn't "
        "know where they are. Now there'll be something soft to look at while they work it out."))
    A(Q("mg_the_night_watch", "The Night Watch", DANNY, 57, 57, "Watchman's",
        "The Wakened keep a watch every night, because somebody ought to be awake in a valley full of sleepers. "
        "Danny Kowalczyk can't sleep, so he took the rota over, and tonight he's short a watchman. The round takes in the three places in Moonglade the Wakened don't like to leave alone in the dark.",
        [explore(*ARCH, "Walk the night watch past the Dreaming Arch in the north woods"),
         explore(*BARROW_DOOR, "Walk the night watch past the Barrow Dens' door"),
         explore(*PIER_END, "Finish the night watch at the end of Nighthaven's pier")],
        "The arch in the north woods first, then down the west shore to the Barrow Dens' door, then all the way "
        "round to the end of the pier in Nighthaven. You don't have to do anything at any of them. Just look, and "
        "remember what you saw.",
        "Warm stones, a door that whispers and an island that hums. You saw all three, then.\n\nIn Buffalo I drove a "
        "snowplough on the night shift, and the worst thing out there was the lake wind. Here I write down the same three things every night, and every night "
        "they're a little bit louder."))
    A(Q("mg_something_to_grow", "Something to Grow", MEILIN, 57, 57, "Gardener's",
        "Mei-Lin Zhou's grandmother grew chillies on a balcony in Chengdu, and Mei-Lin plants things in the Wakened's "
        "gardens because it's how she knows where she is. The druids grow everything here without her help, so "
        "she wants something of her own: a bed of Golden Sansam, which grows wild in the high places and nowhere "
        "in the glade.",
        [gather("herb_golden_sansam", 5, "Golden Sansam from the wild")],
        "Golden Sansam grows in Felwood, Azshara and the high passes, anywhere it's hard to get to. Pick it with "
        "the roots on and bring it back wrapped in damp moss. I'll do the rest.",
        "Look at the roots on those, they'll take in a week.\n\nMy grandmother talked to her plants every morning, in "
        "Sichuanese, and the neighbours thought she was mad. I talk to mine in Mandarin and English, and the "
        "druids think it's the most sensible thing any of us does."))
    A(Q("mg_what_the_sleepers_say", "What the Sleepers Say", SANDVIK, 57, 57, "Listener's",
        "The druids and the Wakened who sleep in the Barrow Dens have started talking in their sleep. Dr. Sandvik "
        "wants someone to sit outside the door and write down what they say, because the wardens won't, and the "
        "Circle has asked her not to go herself.",
        [explore(*BARROW_DOOR, "Sit by the Barrow Dens' door and write down what the sleepers say")],
        "The Barrow Dens are south of here, in the hills. Warden Taerenas will let you sit by the door if you don't touch it. Write down everything, even the words "
        "you don't understand, and those most of all. I've heard that some of it isn't in any language they speak here.",
        "That line's Norwegian, and that one's Yoruba, and those three are Polish, and this one's Darnassian, "
        "and they're all saying the same sentence.\n\nThey're saying it opens from underneath. I don't know what it "
        "is. Neither do they, I think, and that frightens me more than anything on that page.",
        nxt="mg_a_doctor_and_a_keeper"))
    A(Q("mg_a_doctor_and_a_keeper", "A Doctor and a Keeper", SANDVIK, 58, 58, "Keeper's",
        "Dr. Sandvik has copied out what the sleepers said, line by line, with the languages beside them. She's "
        "never asked Keeper Remulos for anything before, but she thinks he needs to see this, and she thinks he "
        "might listen to someone who isn't her.",
        [deliver("mg_q_sleepers_transcript", "Take Ingrid Sandvik's transcript to Keeper Remulos at his shrine")],
        "Remulos is under his tree on the north-west point. He's always been kind to us, and he's always treated "
        "us like patients. Give him this, and tell him it's from the doctor, not from one of the sleepers.",
        "Eleven languages, and one sentence. She's done in a night what the Circle couldn't do in a year.\n\nTell "
        "Ingrid I'll come to the longhouse myself. It's time the Circle stopped asking the Wakened to wait outside "
        "while we decide what's happening to all of us.",
        turn_in_npc_id=REMULOS,
        grant_items=carry("mg_q_sleepers_transcript", "Sandvik's Transcript", "Pages of neat handwriting, one line "
                          "repeated in eleven languages down the left side, and the doctor's notes down the right.")))

    A(Q("mg_the_ones_who_dont_wake", "The Ones Who Don't Wake", ADAEZE, 58, 58, "Dreamfoil",
        "Not every transplant who arrived asleep in Moonglade woke up. Nurse Adaeze Okafor visits the ones who "
        "didn't, in the Barrow Dens beside the druids, and lately their sleep has turned restless. A draught of "
        "Dreamfoil eases a dreamer's sleep without waking them, and the glade doesn't grow it.",
        [gather("herb_dreamfoil", 6, "Dreamfoil from the wild")],
        "Dreamfoil grows in the high wild places, in Felwood and Azshara and the passes. Bring me the leaves fresh "
        "and I'll steep them tonight. I can't wake them, but I can make sure they're not frightened while they "
        "sleep.",
        "This is good Dreamfoil, the bitter kind.\n\nOn the ward in Lagos we had patients who never woke, and we "
        "talked to them every shift because somebody told us they could hear. I still do it. I tell the sleepers "
        "here the news from the longhouse, and I swear one of them laughed last week."))
    A(Q("mg_iron_from_nothing", "Iron from Nothing", HAMISH, 58, 58, "Ironmonger's",
        "The wall of last memories has worn out every chisel the Wakened own. Hamish MacLeod wants proper steel ones, "
        "and the Wakened's new forge can make them, if somebody brings the ore. The Circle won't have mining in the "
        "glade, so it has to come from outside.",
        [gather("ore_thorium", 8, "Thorium ore from the hills")],
        "Thorium's in the hard country, the Plaguelands, Azshara's mountains and the passes up here. Bring me the "
        "ore and Tomas Ribeiro will smelt it. He sold hammers in Porto for nineteen years, and now he wants to make "
        "one.",
        "That's proper ore. Tomas will ruin the first three bars, and the fourth will be fine.\n\nOn Lewis my father "
        "said a good chisel outlasts the man who sharpens it. Every plank on that wall is going to outlast all of "
        "us, and I'd like the tools to as well."))

    # ======================================================================================= 3. THE CIRCLE'S WATCH
    A(Q("mg_a_lantern_for_the_longhouse", "A Lantern for the Longhouse", RABINE, 58, 58, "Lanternlit",
        "Keeper Remulos has told Rabine Saturna about Ingrid Sandvik's transcript, and Rabine has decided the Circle "
        "owes the Wakened more than politeness. He's sending them a moon lantern lit from the great moonwell, the "
        "same kind that hangs over every druid's door in Nighthaven.",
        [deliver("mg_q_moon_lantern", "Take the Circle's moon lantern to Dr. Ingrid Sandvik at the longhouse")],
        "Hang it over the longhouse door if she'll let you. It means the Wakened are welcome in any druid's house in "
        "Kalimdor, and that we'd like to be welcome in theirs. We should have done it three years ago.",
        "Over the door, yes. Everyone will see it from the water.\n\nWhen I first woke up, a druid gave me a blanket "
        "and asked my name, and I couldn't remember it for two days. I remember that blanket better than anything "
        "from my first year in Trondheim.",
        requires_quests=["mg_a_doctor_and_a_keeper"], turn_in_npc_id=SANDVIK,
        grant_items=carry("mg_q_moon_lantern", "Moon Lantern", "A lantern of curved silver wood with a cool blue "
                          "light in it that came from the great moonwell. It never needs refilling.")))
    A(Q("mg_satyrs_in_the_green", "Satyrs in the Green", RABINE, 56, 56, "Wardens'",
        "Felwood was the Circle's forest before the Legion poisoned it, and the satyrs of the Jadefire are still "
        "there, still spreading the rot. Rabine Saturna sends the Circle's help out to the sick lands, and he'd "
        "like to send you.",
        [k("Jadefire Felsworn", 8, NF), k("Jadefire Trickster", 6, NF)],
        "The Jadefire Felsworn and the Jadefire Tricksters run in North Felwood, round the Jadefire glens. The "
        "Felsworn are the ones spreading the fel, and the Tricksters are the ones making sure nobody stops them. "
        "Thin them both out, and don't let the Tricksters get behind you.",
        "The Emerald Reclamation will feel that before we do, and they've earned some good news.\n\nThe Circle can't heal Felwood from here. "
        "What we can do is make sure there's somebody left in it to heal it when the time comes.",
        nxt="mg_the_black_gate"))
    A(Q("mg_the_black_gate", "The Black Gate", RABINE, 57, 57, "Gatebreaker's",
        "Behind the Black Gate of Jaedenar, the Shadow Council keeps a demon chained, and Zar'gothrax the Unbound "
        "has been pulling at those chains since the worlds came together. The Circle has felt every pull in the "
        "roots of the glade. Rabine wants the demon dead.",
        [boss("Zar'gothrax the Unbound", JD)],
        "Jaedenar's in the north-west of North Felwood, behind the Black Gate. Zar'gothrax is at the very bottom, "
        "and you'll have to get through the Council first. Take friends you trust.",
        "The roots are quiet. For the first time in three years the roots are quiet.\n\nI'll tell the Emerald "
        "Reclamation it was you. Aelyra Moonbough has been asking the Circle for help for a long time, and this is "
        "the first time we've been able to send it."))
    A(Q("mg_the_rot_under_the_hold", "The Rot Under the Hold", HAMUUL, 57, 57, "Rotbreaker's",
        "The Timbermaw took Archdruid Hamuul Runetotem's people in for a night on their way up the mountain, when "
        "the tauren had nowhere else to go. Now the Timbermaw have a rot of their own under Timbermaw Hold in "
        "Azshara, and Hamuul hasn't forgotten the debt.",
        [boss("Xavras the Gloomtender", RD)],
        "Under Timbermaw Hold there's the Rotroot Deeps, and at the bottom of it waits Xavras the Gloomtender, the satyr "
        "growing the fel into the Hold's own roots. Go through the deep gate in the Hold's basin, and take friends. "
        "The Timbermaw will thank you, and so will I.",
        "The Timbermaw gave us honey and a fire and didn't ask a single question. That was the night I knew we "
        "might live.\n\nThere's a debt paid. My people have a lot of debts, and I'd like to pay every one of them "
        "before I die."))
    A(Q("mg_bloodvenom", "Bloodvenom", AEDRIS, 56, 56, "Moonwell",
        "Moonwell Keeper Aedris Silverbrook has kept Nighthaven's great moonwell for longer than most of Kalimdor has "
        "had names. She believes the water under Felwood and the water under Moonglade are the same water, and she "
        "wants to know how much of the Bloodvenom has found its way up the mountain.",
        [fetch("mg_q_bloodvenom_residue", 5)],
        "The Seepage Oozes at Bloodvenom Falls, in North Felwood, are the poison given a body. Bring me what's "
        "inside them, sealed in wax, and don't let it touch your skin. I'll set it beside a cup of moonwell water "
        "and see what each of them does.",
        "The moonwell water turned it clear. All of it, in less than an hour.\n\nSo the well can still heal what "
        "the Legion did. That's the best thing I've learned in three years. It means whatever's making the well run "
        "over at night isn't sickness."))
    A(Q("mg_what_dies_in_deadwind", "What Dies in Deadwind", REMULOS, 58, 58, "Dreamwalker's",
        "Keeper Remulos can walk the Emerald Dream to almost anywhere in Azeroth, and since the worlds came together "
        "there's one place he can't reach: Deadwind Pass. He wants to know what's happening to the living things "
        "there, and the deer of the pass will tell him, if you bring him what's left of them.",
        [fetch("mg_q_dissolving_antler", 5)],
        "The Dissolving Stags wander Deadwind West, coming apart a little more every day and not dying. Bring me "
        "their antlers. The bone remembers what the animal dreamed, and I'll read it.",
        "They don't dream at all. Every living thing dreams, and these don't.\n\nThe liquidators at Ariden's Watch "
        "have a name for what's happening to that pass. They say it's remembering. If the Dream can't reach it, then "
        "something else is doing the remembering, and I'd like very much to know what."))
    A(Q("mg_ten_thousand_years_of_horns", "Ten Thousand Years of Horns", HAMUUL, 57, 57, "Hornbreaker's",
        "The Circle has kept a count of satyrs since the War of the Ancients, horn by horn. Hamuul Runetotem has "
        "taken over the counting since he came, partly because the night elves asked and partly, he says, because "
        "it gives a tauren something to do with his hands.",
        [fetch("mg_q_satyr_horn", 6)],
        "The Legash Satyrs hold the old ruins in Central Azshara, round the Legash encampment. Bring me their "
        "horns. I'll add them to the count, and I'll tell the night elves, and they'll pretend they're not "
        "impressed.",
        "Six more on the count. The number's very long now, and it never seems to get shorter at the other end.\n\n"
        "My father told me the satyrs were night elves once, who wanted too much. I think about that every time I "
        "carve a mark."))

    # ======================================================================================= 4. THE TAUREN
    A(Q("mg_the_totems_on_our_backs", "The Totems on Our Backs", MAHALA, 56, 56, "Plainsborn",
        "When Thunder Bluff fell, the tauren who reached Moonglade carried their lodges' totems up the mountain on "
        "their backs. Elder Mahala Dawnhorn has kept them laid down ever since. She'd like someone who wasn't there "
        "to stand at the memorial the survivors built, and tell her what it looks like to a stranger.",
        [explore(*TAUREN_MEMORIAL, "Stand at the tauren memorial in Nighthaven")],
        "The memorial's a short walk south-east of here, by the lodges, a cairn with feathers on it. Look at it "
        "properly. Then come back and tell me whether it looks like a grave or a promise.",
        "You'd call it a promise, then. That's what the young ones say too, and the old ones say grave.\n\nWe've been arguing about it "
        "for three years, the old and the young. I'm glad it's a promise to you. It means the young ones might be "
        "right.",
        nxt="mg_moonwell_water_for_the_totems"))
    A(Q("mg_moonwell_water_for_the_totems", "Moonwell Water for the Totems", MAHALA, 57, 57, "Totemkeeper's",
        "Elder Mahala has decided to raise one of the totems the tauren carried out of Thunder Bluff. Only one, for "
        "the ones they carried, not the ones they left. Before it goes up it has to be washed, and she wants the "
        "water from Nighthaven's great moonwell, with Aedris Silverbrook's blessing.",
        [deliver("mg_q_moonwell_flask", "Bring a flask of the great moonwell's water to Elder Mahala")],
        "Aedris has already filled the flask. She put it in my hands and then took it back and said someone else "
        "should carry it. I think she means it shouldn't be one of us. Take it from her and bring it here.",
        "It's clean, and it's standing, and it looks like it belongs here.\n\nIt's for the ones we carried up the mountain, who lived because "
        "somebody wouldn't put them down. The ones we left will get theirs when we go home. If we go home.",
        grant_items=carry("mg_q_moonwell_flask", "Flask of Moonwell Water", "Water from Nighthaven's great moonwell, "
                          "glowing faintly through the glass. It's lighter than it should be.")))
    A(Q("mg_the_thunder_bluff_road", "The Thunder Bluff Road", BUNTHEN, 58, 58, "Windrider's",
        "Bunthen Plainswind flew the Thunder Bluff road for twenty years before it fell. Elder Longtread at Camp "
        "Taurajo keeps the seat for Cairne Bloodhoof, and Bunthen has never been able to bring himself to fly him "
        "the list of who reached Moonglade. Archdruid Hamuul has written it out, every name.",
        [deliver("mg_q_hamuuls_list", "Take Hamuul's list of the survivors to Elder Longtread at Camp Taurajo")],
        "Camp Taurajo's in the Southern Barrens. I'll fly you as far as the wind riders will go. Give Longtread the "
        "list, and tell him it's all of them. Tell him we looked, and that's everyone.",
        "He's written down every name. I'd heard some of them were alive, and I didn't let myself believe it.\n\nTell Bunthen I'll "
        "keep this with the seat. When the High Chieftain comes home, it'll be the first thing he reads. I'll make "
        "sure of it.",
        turn_in_npc_id=LONGTREAD,
        grant_items=carry("mg_q_hamuuls_list", "Hamuul's List", "A long roll of hide covered on both sides with "
                          "names, in Hamuul Runetotem's big careful hand.")))

    # ======================================================================================= 5. SOMETHING WAKING
    A(Q("mg_warm_stones", "Warm Stones", LETHIEL, 58, 58, "Dreamwatcher's",
        "The Dreaming Arch in the north woods has stood cold for ten thousand years. Now its stones are warm at "
        "night, and the flowers round it bloom only when they are. Dreamwatcher Lethiel sits with it every night, "
        "and she'd like a second pair of eyes she can trust.",
        [explore(*ARCH, "Put your hands on the Dreaming Arch's stones after dark")],
        "It's up the path into the north woods, behind the Shrine. Put your hands flat on the stones and hold them "
        "there. Tell me if they feel warm like a hearth, or warm like something alive.",
        "Like something alive. I knew it, and I didn't want to be the only one who knew it.\n\nThe arch doesn't "
        "lead anywhere. It never has. But the space inside it has started to look like it's waiting for something "
        "to come through, and I don't think it'll wait for ever."))
    A(Q("mg_the_well_runs_over", "The Well Runs Over", AEDRIS, 58, 58, "Overflow",
        "Every night the great moonwell runs over by a finger's width, and every morning it's settled again. "
        "Aedris Silverbrook has been writing down the times, and they match something on the lake. She wants "
        "someone at the end of the pier to watch the island while she watches the well.",
        [explore(*PIER_END, "Watch the island in the lake from the end of the pier")],
        "Go to the end of Nighthaven's pier and watch the island in the middle of the lake. When the well rises, "
        "I'll know. You'll know too, I think. Come back and tell me what you saw.",
        "The pool on the island lit, and the well rose, both at once.\n\nThe island's pool doesn't reflect the sky, "
        "it never has. The old keepers wrote that the night elves built something under the lake before the "
        "Sundering and flooded it on purpose. I always thought that was a story."))
    A(Q("mg_who_are_they_talking_to", "Who Are They Talking To?", TAERENAS, 58, 58, "Wardensworn",
        "Warden Taerenas guards the Barrow Dens' door, and he's heard the sleepers inside answer someone. Not each "
        "other, he says, but someone else. He wants a witness who isn't a warden, because the Circle will say a warden was "
        "only frightened.",
        [explore(*BARROW_DOOR, "Stand at the Barrow Dens' door and listen for the other voice")],
        "Stand at the door with me and listen, nothing more. Don't touch the thorns. If you hear it, you'll know "
        "it, because it's the only voice in there that doesn't sound asleep.",
        "You heard it. I can see it on your face.\n\nI've guarded sleepers for four hundred years. Sleepers dream, "
        "and they talk, and they turn over. They don't wait for an answer and then nod at it. Go and tell the "
        "Keeper, please. He'll believe you sooner than me."))
    A(Q("mg_the_fish_are_turning", "The Fish Are Turning", ILYSSA, 57, 57, "Lakeside",
        "Ilyssa Moonwater has fished Lake Elune'ara her whole life, and she says the fish have started turning toward "
        "the island at night, all of them, the way a field of flowers turns to the sun. She wants someone to see it "
        "from the falls, where the water's clearest.",
        [explore(*FALLS_VIEW, "Watch the lake from the foot of the Falls of Elune'ara")],
        "The Falls of Elune'ara come down on the north shore. Stand where the spray settles and look into the water. "
        "You'll see them, hundreds of them, all facing the same way.",
        "Hundreds, all facing the island and not moving.\n\nMy mother fished this lake and her mother before her, and "
        "not one of them ever saw it do that. The fish know something. Fish always know first."))
    A(Q("mg_the_same_dream", "The Same Dream", TALOWYN, 57, 57, "Innkeeper's",
        "Innkeeper Talowyn Nightbreeze keeps a book for her guests to write in, and for the last month half of them "
        "have written down the same dream: a door under water, and a stair going down. She wants Dr. Sandvik to see "
        "it, because the doctor's the only one in the glade who collects dreams on purpose.",
        [deliver("mg_q_guest_book", "Take Talowyn's guest book to Dr. Ingrid Sandvik")],
        "It's all in the back half of the book. People who've never met, writing the same thing in their own words. "
        "Take it round the lake to the doctor. She'll want it more than I do.",
        "A door under water and a stair going down, nineteen times, from nineteen strangers.\n\nIn Trondheim we'd "
        "have called this a contagion of suggestion and written a paper about it. Here I'm going to call it what "
        "it looks like: something under that lake is reaching out to everyone who sleeps near it.",
        turn_in_npc_id=SANDVIK,
        grant_items=carry("mg_q_guest_book", "Talowyn's Guest Book", "A thick book with a leaf pressed on the cover. "
                          "The back half is full of the same dream in different hands.")))
    A(Q("mg_seedlings_for_the_sanctuary", "Seedlings for the Sanctuary", MYLLA, 56, 56, "Seedbearer's",
        "Herbwarden Mylla Starbloom grows seedlings from the glade's oldest trees, and the Emerald Reclamation in "
        "Felwood has asked for them, to plant where the fel has been burned away. Moonglade's soil is the cleanest "
        "in Kalimdor, and the Sanctuary needs every bit of it.",
        [deliver("mg_q_seedling_tray", "Take Mylla's seedlings to Arch Druid Aelyra Moonbough at the Emerald Sanctuary")],
        "Fly down to the Emerald Sanctuary in South Felwood and give the tray to Arch Druid Aelyra Moonbough. Keep "
        "them out of the wind, and whatever happens, don't let them near Felwood's water.",
        "Moonglade oak, the real thing. I haven't had seedlings this clean since before the Legion came.\n\nTell "
        "Mylla we'll plant them on the burned ground by the old moonwell. In a hundred years there'll be a wood "
        "there, and somebody will wonder where it came from.",
        turn_in_npc_id=AELYRA,
        grant_items=carry("mg_q_seedling_tray", "Tray of Seedlings", "A shallow tray of moss with a dozen tiny silver "
                          "oak seedlings in it, each with two leaves.")))
    A(Q("mg_what_is_waking", "What Is Waking", REMULOS, 60, 60, "Keeper's",
        "The sleepers answer someone, the arch is warm, the well runs over when the island lights, and strangers "
        "dream of a stair under the water. Keeper Remulos has listened to all of it, and he wants you at his shrine "
        "while he walks into the Dream to look.",
        [explore(*SHRINE, "Keep watch at the Shrine of Remulos while the Keeper walks the Dream")],
        "Stand by the moonwell under my tree. If I don't come back by morning, don't wake me, whatever the druids "
        "tell you. Go to Ingrid Sandvik instead. She'll know better than they will how to bring somebody back.",
        "I came back. Something walked a long way with me, and then it turned aside.\n\nIt isn't one thing. It's "
        "something under the lake, and something behind the arch, and something in the dreams of the sleepers, all "
        "waking at once, as if they'd heard the same bell. When they open their eyes, Moonglade will need you.",
        requires_quests=["mg_warm_stones", "mg_the_well_runs_over", "mg_who_are_they_talking_to",
                         "mg_what_the_sleepers_say"]))
    return out
