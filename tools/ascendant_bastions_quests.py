"""
The Ascendant Bastions' quests (54-57): the Ascendancy's own ground, round the citadel that holds its two dungeons.
Read by tools/build_ascendant_bastions_quests.py, which holds them to every rule before anything is written. The map
is tools/handbuilt_worldtree_ascendant_bastions.py and the people are tools/build_ascendant_bastions_people.py. You
come in on a free skiff from Aurelion's Skydocks (auq_the_free_skiffs, Dockmaster Garret Lune's last quest), and land
at Dawnspear Wreck.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026): the fort was a scholar house's college for centuries before the Ascendancy took it
two hundred years ago; the slipways built long-haulers before they built warships; the storm collectors were an old
house's. The player is the newcomer.

THE THREADS (about 84% from the two hubs, Dawnspear Wreck and the Yard Pens):
  The warships: Captain Isolde Marrane, who brought the Dawnspear down rather than fire on Tethertown, counts the keels,
    burns the yard's work and points you at the Foundry's gate. Rosa Delgado in the pens has been welding the seams
    weak, and wants the drones that fix them gone.
  The general's teacher: Magister Orla Thessan of the Patient Lens taught Ascendant-General Maelis Ardane, and watches
    what her student is building. The clerk at the Censor-Archive copies before he burns. That's the sky's one mystery
    here (docs/worldtree_brief.md): a record one people kept and another destroyed, the plate with three seals on it.
  The deserter: Lancer Tavin Roake put his lance down in front of his wing, and wants the Proving Grounds broken.
  The wreck: the surgeon's burns and the Ashwake; the lookout's guns; the skiffmaster's hawks.
  The pens: the medic's water and the hounds; the rigger's gunships and thunderbirds; the cook's two hundred plates.
  The Storm Harvest: the old keeper who knows where the lightning goes.
  The road north: the Firmament Road's end, and the name of what's past it.

THE RULES IT KEEPS: transplants are factionless; the Aetherians only ever say they don't know what the change was, and
nothing about the three peoples points at it. VOICE (Kyle): whole sentences the way a person says them, contractions,
no dashes, no sentence of one or two words, the useful thing first, every kill target named, no count beside an
objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

AB = "ascendant_bastions"
#: the Citadel of Ascent's two dungeons (tools/handbuilt_gravity_foundry.py, tools/handbuilt_ascendant_spire.py)
GF1, GF2 = "the_gravity_foundry", "the_gravity_foundry:_the_keelworks"
AS1, AS2 = "the_ascendant_spire", "the_ascendant_spire:_the_command_spire"

# ---- Dawnspear Wreck
ISOLDE, ORLA, TAVIN, NELL = "ab_wreck_captain", "ab_unsworn_scholar", "ab_lancer_deserter", "ab_wreck_surgeon"
FEN, PELL = "ab_lookout", "ab_skiffmaster"
# ---- the Yard Pens
ROSA, SIOBHAN, TOMASZ, HAMZA = "ab_pens_foreman", "ab_pens_medic", "ab_pens_rigger", "ab_pens_cook"
# ---- out on the islands
ANSELM, EDDA = "ab_archive_clerk", "ab_harvest_keeper"

HUB_GIVERS = {ISOLDE, ORLA, TAVIN, NELL, FEN, PELL, ROSA, SIOBHAN, TOMASZ, HAMZA}
#: the Aetherians pay the Aetherians; the Earthborn in the pens pay nobody
SKY_GIVERS = {ISOLDE, ORLA, TAVIN, NELL, FEN, PELL, ANSELM, EDDA}


def k(target, n, zone=AB):
    return kill(target, n, zone=zone)


def boss(target, zone=AB):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=AB, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Censor-Inquisitor": [("ab_q_plate_fragment", "Rescued Plate Fragment", "A shard of an old stone plate, cut close "
                           "with writing, that a Censor-Inquisitor was carrying to the braziers.")],
    "Mounted Sky Lancer": [("ab_q_steed_core", "Construct Steed Core", "The crystal heart of a Mounted Sky Lancer's "
                            "bronze steed. Without it, the steed is a statue.")],
    "Smoke Jelly": [("ab_q_jelly_gel", "Cool Smoke-Jelly Gel", "A handful of cool, clear gel out of a Smoke Jelly. "
                     "Spread on a burn, it takes the heat out at once.")],
    "Keel Construct": [("ab_q_keel_governor", "Keel Core Governor", "The governor out of a Keel Construct's chest, the "
                        "part that tells it which keel to lay next.")],
    "Harvested Storm": [("ab_q_storm_rain", "Storm-Charged Rainwater", "A flask of rain wrung out of a Harvested Storm. "
                         "It fizzes a little, and it's the cleanest water on the Bastions.")],
    "Cinder Ray": [("ab_q_ray_fillet", "Cinder Ray Fillet", "A thick white fillet off a Cinder Ray. It's already "
                    "half cooked from the inside.")],
    "Bastion Legionary": [("ab_q_ration_tin", "Legionary Ration Tin", "A sealed tin of Ascendancy field rations off a "
                           "Bastion Legionary: dried meat, hard bread and a twist of good spice.")],
    "Lightning Elemental": [("ab_q_collector_crystal", "Overcharged Collector Crystal", "A crystal grown inside a "
                             "Lightning Elemental, so full of charge it hums against your palm.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [113]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=AB, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
PIER_WEST = (92, 206)         # the first finger pier, where the oldest keel lies
PIER_MID = (156, 206)         # the middle pier, the biggest berth
PIER_EAST = (220, 206)        # the last pier, the newest keel
FOUNDRY_GATE = (160, 130)     # before the citadel's south gate
PROVING_RING = (50, 110)      # the Proving Grounds' arena ring
ARCHIVE_YARD = (38, 42)       # the Censor-Archive's yard, by the braziers
GUN_ONE = (238, 114)          # the first gun platform
GUN_TWO = (256, 132)          # the second
GUN_THREE = (280, 152)        # the third
ROAD_END = (160, 10)          # the end of the Firmament Road


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE WARSHIPS (Isolde)
    A(Q("abq_count_the_keels", "Count the Keels", ISOLDE, 54, 55, "Keelcounter's",
        "Captain Isolde Marrane wants to know how many warships the Ascendancy has on its slipways. She needs someone "
        "to walk the piers and look.",
        [explore(*PIER_WEST, "Look at the keel on the first pier"),
         explore(*PIER_MID, "Look at the keel on the middle pier"),
         explore(*PIER_EAST, "Look at the keel on the last pier")],
        "The lookout counts hulls, but I want to know how far along they are. Walk out along the first pier, the "
        "middle one and the last one, and look at what's in the berths. The yard's busy, so keep moving.",
        "Five keels, and the one on the last pier is nearly ready to fly.\n\nWhen I was a young officer, these slipways "
        "built long-haulers, ships for carrying grain between the islands. Every ship in those berths now has a gun "
        "deck. I know exactly what they're for, because I was nearly the one who flew them."))
    A(Q("abq_rivets_and_rot", "Rivets and Rot", ISOLDE, 55, 56, "Shipbreaker's",
        "The warships on the slipways need hands to finish them. Captain Isolde Marrane wants the yard's Ascendancy "
        "Shipwright and its Keel Construct taken off the work.",
        [k("Ascendancy Shipwright", 8), k("Keel Construct", 6)],
        "Every day the yard works, those keels get closer to flying, and they're nearly there. Every Ascendancy Shipwright on the quay knows the "
        "ships better than I do, and every Keel Construct can lay a keel in a week. Take them off the work, and the "
        "warships wait.",
        "The quay's gone quiet, and I can hear the overseers shouting about it from here.\n\nThey'll bring more "
        "shipwrights from Aurelion, and it'll take them a month. A month is a long time when you're trying to keep a "
        "fleet away from a tree.",
        requires_quests=["abq_count_the_keels"]))
    A(Q("abq_the_unlaunched", "The Unlaunched", ISOLDE, 56, 56, "Hullbreaker's",
        "The oldest hull on the slipways was laid down and never launched. Somebody switched its guns on, and The "
        "Unlaunched now drifts along the quay firing at anything that moves. Captain Isolde Marrane wants it sunk.",
        [boss("The Unlaunched")],
        "There's a hull on the slipways that was never finished, and the yard's engineers woke its guns up to test them. "
        "They couldn't put it back to sleep. The Unlaunched drifts along the quay now, and it kills shipwrights as "
        "happily as it kills us. Put it down properly.",
        "So that's the end of it. I remember when they laid that keel. It was supposed to be the first of the new fleet, "
        "and it never flew a day.\n\nI'd say I'm sorry for it, but I'm not.",
        requires_quests=["abq_rivets_and_rot"]))
    A(Q("abq_the_foundry_gate", "The Foundry Gate", ISOLDE, 56, 57, "Gatewatcher's",
        "The warships' engines aren't built on the slipways. Captain Isolde Marrane wants you to see the citadel's south "
        "gate, where the Gravity Foundry is.",
        [explore(*FOUNDRY_GATE, "Look at the citadel's south gate, at the head of the causeway")],
        "The hulls are built on the slipways, but the engines aren't. They come down the causeway out of the citadel's "
        "south gate, from the Gravity Foundry under it. Go and look at that gate. I want you to know where it is, "
        "because sooner or later somebody's going to have to go through it.",
        "You've seen it, then. The foundry was a scholar house's workshop once, the lens-grinders' and the engine-"
        "wrights'. The Ascendancy kept the halls and changed what's made in them.\n\nBring friends when you go in. "
        "Bring a lot of them.",
        requires_quests=["abq_the_unlaunched"]))

    # ---- the Gravity Foundry (56-58), through the south gate
    A(Q("abq_the_foundry_master", "The Foundry-Master", HAMZA, 57, 57, "Foundry-Breaker's",
        "Every week the Gravity Foundry takes people out of the Yard Pens to work the pour, and Foundry-Master Cassor "
        "Vane picks them. Hamza Qureshi wants him dead in his own gallery.",
        [boss("Foundry-Master Cassor Vane", GF1)],
        "Every week Cassor Vane sends down for more hands, and every week I cook for fewer people. He picks them "
        "himself from the gallery at the top of the Gravity Foundry, with those stones going round his head. Go in "
        "through the citadel's south gate and put him down, and take friends, because the whole foundry works for him.",
        "Cassor Vane is dead? Then nobody's going down to the pour tomorrow.\n\nI'm making a proper curry tonight, the way we "
        "did it at home on a Friday. I've been saving the spice for something worth celebrating.",
        requires_quests=["abq_the_overseers"]))
    A(Q("abq_the_pourmasters", "The Pourmasters", SIOBHAN, 57, 57, "Burnsalver's",
        "Half the burns Siobhan Keane treats come out of the Gravity Foundry's quench halls. She wants Pourmaster Ilka "
        "and her brother Dov stopped.",
        [boss("Pourmaster Ilka", GF1)],
        "The twins run the quench halls in the Gravity Foundry. Ilka pours, Dov quenches, and when they're behind, "
        "they make the conscripts carry the crucibles by hand. I've had three people this month with molten crystal "
        "down their arms. You'll find them on the east side of the foundry, and you'll have to fight both of them at "
        "once.",
        "You stopped both of them? Good, I'd have liked to see their faces.\n\nI was a ward nurse for twenty years "
        "before all this. I've never wished anyone harm in my life, and I don't feel the least bit sorry.",
        requires_quests=["abq_medicine_run"]))
    A(Q("abq_the_warheart", "The Warheart", PELL, 58, 58, "Warheart-Breaker's",
        "The engine for the Ascendancy's first warship is being built in the Keelworks, under the Gravity Foundry. "
        "Skiffmaster Pell Daray wants it destroyed before it ever flies.",
        [boss("The Warheart", GF2)],
        "The day that first warship flies, the free skiffs stop flying, because nothing we've got can outrun a gun "
        "deck. Its engine's nearly done, down in the Keelworks under the foundry, and they call it the Warheart. Get "
        "down there through the foundry, past the Foundry-Master's lift, and break it. If it wakes up before you get "
        "there, break it anyway.",
        "It's done, then. Without that engine, none of those hulls is going anywhere for a long while.\n\nThe skiffs "
        "will keep flying. I'll tell the pilots tonight, and I expect they'll want to buy you a drink.",
        requires_quests=["abq_clear_skies"]))
    A(Q("abq_the_lance_commander", "The Lance-Commander", PELL, 60, 60, "Lance-Breaker's",
        "The lancer wings that hunt the free skiffs fly on Lance-Commander Aris Thane's orders. Skiffmaster Pell Daray "
        "wants him stopped in the Ascendant Spire.",
        [boss("Lance-Commander Aris Thane", AS1)],
        "I've lost four skiffs this year to lancer wings, and every one of them flew out on Aris Thane's orders. He "
        "holds the Lancer Halls inside the citadel's north gate, in the Ascendant Spire. Go in and unhorse him. Tavin "
        "says he won't stop while he's still in the saddle, and Tavin should know, because Thane trained him.",
        "He's finished, then. Tavin will want to hear it from you himself.\n\nWith nobody giving the wings their "
        "orders, my pilots might get a quiet month. I can't remember the last one.",
        requires_quests=["abq_the_warheart"]))
    A(Q("abq_the_inquisitor", "The Inquisitor", NELL, 60, 60, "Cellbreaker's",
        "Surgeon Nell Avary has treated the few who came back out of the Spire's cells. She wants High Inquisitor "
        "Seren Vash stopped.",
        [boss("High Inquisitor Seren Vash", AS1)],
        "Everyone the Ascendancy catches ends up in front of Seren Vash, in the Inquisitorium at the bottom of the "
        "Ascendant Spire's first halls. The ones who came back to me couldn't sleep for weeks. Go in through the north "
        "gate, past the lancers or round by the storm gallery, and put an end to the questions.",
        "There won't be any more of them, then. Thank you.\n\nI'll tell the ones who came back. I think it'll help "
        "them more than anything I've given them.",
        requires_quests=["abq_burn_salve"]))
    A(Q("abq_the_book_of_home", "The Book of Home", HAMZA, 60, 60, "Rememberer's",
        "The people in the Yard Pens kept a book of everything they remembered from home, and Archivist-Censor Mallen "
        "Roe took it to be burned. Hamza Qureshi wants the man who burns things stopped.",
        [boss("Archivist-Censor Mallen Roe", AS1)],
        "We kept a book in the pens, with recipes, songs, street names, anything anyone could remember from home so "
        "we wouldn't lose it. The Inquisitors took it for the Burning Archive in the Ascendant Spire, and the Censor, "
        "Mallen Roe, burns everything that comes in. He's off the Inquisitorium's north door. If the book's gone, at "
        "least stop him burning the next one.",
        "The book's gone, I know. But he won't burn the next one, and we've already started writing it again.\n\n"
        "My mother's dal is on the first page. I wrote it out from memory this morning, and I think I've got it right.",
        requires_quests=["abq_the_foundry_master"]))
    A(Q("abq_the_right_hand", "The Right Hand", ORLA, 60, 60, "Right Hand's Bane",
        "Exarch Lucan Thessaly speaks for Ascendant-General Maelis Ardane on the Bastions. Magister Orla Thessan wants "
        "him stopped at the top of the Ascendant Spire.",
        [boss("Exarch Lucan Thessaly", AS2)],
        "Maelis isn't here. She's gone north, and Lucan Thessaly gives her orders on the Bastions while she's away. He "
        "was my student too, before he was hers. You'll find him at the very top of the Ascendant Spire, in the "
        "Exarch's Sanctum, past the Aegis Engine and his own guard. Take him off the board, and she'll have to come "
        "back and see for herself.",
        "So Lucan's gone, and she'll know by tonight, wherever she is.\n\nI taught them both to read the sky. I "
        "never thought I'd have to ask anyone to do this, and I'm grateful you did it.",
        requires_quests=["abq_burn_nothing_more"]))

    # =================================================================================== 2. THE GENERAL'S TEACHER
    A(Q("abq_her_old_teacher", "Her Old Teacher", ORLA, 54, 55, "Teacher's",
        "Magister Orla Thessan taught Ascendant-General Maelis Ardane. She wants you to see two of the places her "
        "student made: the Proving Grounds' arena and the Censor-Archive.",
        [explore(*PROVING_RING, "Stand at the Proving Grounds' arena ring"),
         explore(*ARCHIVE_YARD, "Stand in the Censor-Archive's yard")],
        "Maelis built two things on the Bastions that I can't forgive. One trains children to ride at the tree, and the "
        "other burns the house's oldest records. Go and look at both, the arena on the Proving Grounds and the yard at "
        "the Censor-Archive. Then come back and tell me what you saw her people doing.",
        "They were burning books while you watched. I know, because they burn them every evening at the same hour.\n\n"
        "Maelis used to sit in the Patient Lens's library until they put the lamps out. She loved those records more "
        "than anyone I've ever taught. Now she burns them, and I don't know why."))
    A(Q("abq_what_they_burn", "What They Burn", ORLA, 55, 55, "Letterbearer's",
        "Magister Orla Thessan has a letter for Clerk Anselm Rook at the Censor-Archive, the clerk who reads what the "
        "Inquisitors bring him before it's burned.",
        [deliver("ab_q_orla_letter", "Take Magister Thessan's letter to Clerk Anselm Rook at the Censor-Archive")],
        "There's a clerk at the Censor-Archive called Anselm Rook. He was a copyist at the Patient Lens, a good one, and "
        "the Ascendancy took him with the archive. Give him this letter. He'll know my hand, and he'll know I'm asking "
        "him for something dangerous.",
        "Magister Thessan's hand. I haven't seen it in twelve years.\n\nShe wants to know what they're burning. I can "
        "tell her that. I've been copying every page before it goes into the brazier, and I've been waiting for "
        "someone to give the copies to.",
        turn_in_npc_id=ANSELM, requires_quests=["abq_her_old_teacher"],
        grant_items=carry("ab_q_orla_letter", "Magister Thessan's Letter", "A folded letter sealed with the Patient "
                          "Lens's mark, addressed in a careful old hand to Anselm Rook.")))
    A(Q("abq_burn_nothing_more", "Burn Nothing More", ORLA, 56, 56, "Bookkeeper's",
        "The Censor-Archive's braziers are fed by the Cinder-Script Wisp, born out of what's burned, and guarded by the "
        "Archive Warden. Magister Orla Thessan wants both gone, so the burning stops.",
        [k("Cinder-Script Wisp", 8), k("Archive Warden", 6)],
        "The fires at the Archive make things. Every Cinder-Script Wisp is a book that burned, still glowing with what "
        "was written in it, and every Archive Warden stands there to make sure the fire's fed. Put out the one and send "
        "the other packing.",
        "The braziers are cold tonight. Anselm sent word that he's never heard the Archive so quiet.\n\nIt won't last, "
        "but every evening they can't burn is an evening the records survive. That's how the Patient Lens works. We "
        "wait, and we keep what we can.",
        requires_quests=["abq_three_seals"]))

    # =================================================================================== 3. THE CENSOR-ARCHIVE (Anselm)
    A(Q("abq_copied_before_burned", "Copied Before Burned", ANSELM, 55, 56, "Copyist's",
        "Clerk Anselm Rook copies what he can before it burns, but the oldest plates are stone. The Censor-Inquisitor "
        "carries them to the braziers to be shattered. He wants the pieces.",
        [fetch("ab_q_plate_fragment", 6)],
        "I can copy paper, but I can't copy stone fast enough. The oldest records are plates, and every Censor-"
        "Inquisitor here carries them out to be broken in the fire. Bring me the pieces they're carrying, before they "
        "get there. I'll put them back together.",
        "Six pieces, and three of them fit together. That's never happened before.\n\nGive me a moment with them. "
        "There's something cut across the bottom that I've only ever seen half of.",
        requires_quests=["abq_what_they_burn"]))
    A(Q("abq_three_seals", "Three Seals", ANSELM, 56, 56, "Sealbearer's",
        "Clerk Anselm Rook pieced a plate together from what the Inquisitors were burning. It has three seals across "
        "the bottom, and he wants Magister Orla Thessan to see it.",
        [deliver("ab_q_three_seals", "Take the pieced plate to Magister Orla Thessan at Dawnspear Wreck")],
        "Look at the bottom of it. That's the old house mark, the one our oldest books carry. That's a Kharad rune, I'm "
        "sure of it. And that last one is a Veyr talon-print, pressed into the stone while it was soft. Three seals on "
        "one record, and the Ascendancy burns every copy it finds. Take it to the magister.",
        "Three seals, side by side, and the same words above each one.\n\nThe house kept records like this once, and "
        "somebody decided nobody should read them. Maelis was reading plates like this the year she left us. I always "
        "thought she left because we were slow. Now I wonder whether she left because of what she read.",
        turn_in_npc_id=ORLA, requires_quests=["abq_copied_before_burned"],
        grant_items=carry("ab_q_three_seals", "The Plate of Three Seals", "Three pieces of an old stone plate fitted "
                          "together. Across the bottom are three seals: an Aetherian house mark, a Kharad rune and a "
                          "Veyr talon-print.")))
    A(Q("abq_high_censor", "The High Censor", ANSELM, 56, 56, "Censor-Breaker's",
        "High Censor Ilsabet Morn decides what the Archive burns. Clerk Anselm Rook says she's started asking why his "
        "copies are taking so long.",
        [boss("High Censor Ilsabet Morn")],
        "High Censor Ilsabet Morn chooses what goes into the fire, and she reads everything first. She's started asking "
        "me why the copying takes so long, and sooner or later she'll come to my desk. I'd like her not to.",
        "She won't be asking any more questions. I'll tell the Inquisitors she was called to the citadel, and they'll believe it, because they "
        "always do.\n\nI'm not brave, as I told you. But I can keep copying now, and that's the only brave thing I know "
        "how to do.",
        requires_quests=["abq_what_they_burn"]))

    # =================================================================================== 4. THE DESERTER (Tavin)
    A(Q("abq_the_riders", "The Riders", TAVIN, 55, 56, "Deserter's",
        "On the Proving Grounds, the Mounted Sky Lancer rides down the recruits who fall behind in drill. Lancer Tavin "
        "Roake wants the riders gone.",
        [k("Mounted Sky Lancer", 8)],
        "The recruits are children, most of them, and they're frightened. They train on foot, and every Mounted Sky Lancer on the Proving "
        "Grounds rides down the ones who fall behind, to teach the rest to keep up. I did it myself, for two years, and "
        "I'd like you to stop them.",
        "The drill's stopped. I can hear the recruits from the bow, and they're not running.\n\nSome of them will come "
        "over to us now, not many and not quickly, but some."))
    A(Q("abq_unhorsed", "Unhorsed", TAVIN, 55, 56, "Unhorser's",
        "The wing that will fly at the tree rides construct steeds. Lancer Tavin Roake wants the crystal cores out of "
        "the Mounted Sky Lancer's steeds.",
        [fetch("ab_q_steed_core", 5)],
        "A lancer without a steed is a soldier who walks, and nobody's walking to the tree. Every Mounted Sky Lancer "
        "rides a bronze steed with a crystal core in its chest. Bring me the cores, and the wing stays on the ground.",
        "That's five steeds that'll stand in the hangar until somebody grows them new hearts.\n\nIt takes "
        "the foundry a season to grow one. I counted, when I was still counting for them.",
        requires_quests=["abq_the_riders"]))
    A(Q("abq_the_lance_master", "The Lance-Master", TAVIN, 56, 56, "Lancebreaker's",
        "Lance-Master Varro Dain trained Lancer Tavin Roake, and every lancer on the Proving Grounds. Tavin wants him "
        "stopped before the next intake arrives.",
        [boss("Lance-Master Varro Dain")],
        "Lance-Master Varro Dain taught me everything I know about the lance, and he taught me to ride down children. "
        "There's a new intake of recruits coming from Aurelion next month. I don't want him to be there to meet them.",
        "He was never unseated in thirty years. I suppose that's over.\n\nI thought I'd feel better. I feel like "
        "something I was part of has ended, and that's close enough.",
        requires_quests=["abq_unhorsed"]))
    A(Q("abq_the_wall_captain", "The Wall-Captain", TAVIN, 57, 57, "Wallbreaker's",
        "Wall-Captain Hesper Drace commands the guard on the citadel's apron. Lancer Tavin Roake says she hangs "
        "deserters from the walls.",
        [boss("Wall-Captain Hesper Drace")],
        "Wall-Captain Hesper Drace walks the apron round the citadel, and every deserter her guard catches hangs from "
        "the walls for a week. Two of the lancers who followed me here were caught on the way. I'd like the walls to "
        "be empty.",
        "They'll take the bodies down tonight. I've asked the skiffmaster to fly them home to Aurelion.\n\nThat's all "
        "I can do for them now. It's more than I thought I'd get to do.",
        requires_quests=["abq_the_lance_master"]))

    # =================================================================================== 5. THE SURGEON (Nell)
    A(Q("abq_burn_salve", "Burn Salve", NELL, 54, 55, "Salvemaker's",
        "Most of what Surgeon Nell Avary treats is burns from the storm guns. The Smoke Jelly in the Ashwake carries a "
        "cool gel that takes the heat out of them.",
        [fetch("ab_q_jelly_gel", 8)],
        "I've run out of burn salve, and the guns don't care. Every Smoke Jelly drifting in the Ashwake carries a cool "
        "gel inside it, and it's better than anything Aurelion ever sent me. Bring me as much as you can carry.",
        "That's enough for a month, if the guns are kind, and they won't be.\n\nI'll mix it tonight. You'd be "
        "surprised how many deserters come in with burns on their hands. Most of them grabbed a gun barrel on the way "
        "out."))
    A(Q("abq_ash_in_the_lungs", "Ash in the Lungs", NELL, 54, 55, "Ashclearer's",
        "The Forge-Ash Wisp drifts out of the citadel's chimneys and settles round the wreck, and everyone in camp is "
        "coughing. Surgeon Nell Avary wants the air cleared.",
        [k("Forge-Ash Wisp", 10)],
        "The citadel's chimneys never stop, and every Forge-Ash Wisp that comes out of them drifts down to the wreck. "
        "Half the camp coughs all night. I can't fix the chimneys, but you can thin out the ash.",
        "The children slept last night. Did you know there are children in the camp? Three of them, deserters' "
        "children.\n\nThe ash will come back. But they slept."))
    A(Q("abq_the_ash_mother", "The Ash-Mother", NELL, 55, 55, "Smoke-Breaker's",
        "Something in the Ashwake is breeding the Smoke Jelly faster than the wind can scatter them. Surgeon Nell Avary "
        "has heard the scouts call it The Ash-Mother.",
        [boss("The Ash-Mother")],
        "The scouts say there's something big out in the Ashwake, deep in the smoke, and the jellies drift out of it in "
        "clouds. They call it The Ash-Mother. It's thickened the smoke round the wreck until you can't see the bow from "
        "the stern. I want it dead.",
        "I can see the fort again from the camp. I'm not sure that's an improvement.\n\nThank you. The smoke was "
        "getting into everyone's wounds, and now it won't.",
        requires_quests=["abq_burn_salve"]))

    # =================================================================================== 6. THE LOOKOUT (Fen)
    A(Q("abq_eyes_on_the_gunline", "Eyes on the Gunline", FEN, 55, 56, "Spotter's",
        "Lookout Fen Arden can see the Gunline from the bow, but not what the guns are pointed at. He wants someone to "
        "look from each platform.",
        [explore(*GUN_ONE, "Look out from the first gun platform"),
         explore(*GUN_TWO, "Look out from the second gun platform"),
         explore(*GUN_THREE, "Look out from the third gun platform")],
        "The storm guns on the Gunline turn every evening, and I can't see what they're turning to face. Walk the "
        "platforms, all three, and look where the barrels point. The crews won't like you being there, so be quick.",
        "South, all three, and a little west. That's the way to the World Tree.\n\nThey're not guarding the fort. "
        "They're ranging the guns for the day the warships sail."))
    A(Q("abq_silence_the_guns", "Silence the Guns", FEN, 56, 57, "Gunsilencer's",
        "The Gunline's crews are ranging their guns on the World Tree. Lookout Fen Arden wants the Storm Artillerist "
        "and the Arcane Bombardier off the platforms.",
        [k("Storm Artillerist", 8), k("Arcane Bombardier", 6)],
        "A gun's only a gun without a crew. Every Storm Artillerist and every Arcane Bombardier on the Gunline knows how "
        "to range on a target a long way off. Take them off the platforms, and the guns can't find anything.",
        "The guns stopped turning this evening. First time in a year.\n\nThey'll train new crews, but training a storm "
        "crew takes longer than training a lancer. Every week counts.",
        requires_quests=["abq_eyes_on_the_gunline"]))
    A(Q("abq_the_battery_master", "The Battery-Master", FEN, 57, 57, "Batterybreaker's",
        "Battery-Master Ormund Krell commands the Gunline and calculates the ranges. Lookout Fen Arden wants his "
        "numbers gone with him.",
        [boss("Battery-Master Ormund Krell")],
        "Battery-Master Ormund Krell worked out the ranges to the tree himself, by hand, and it's taken him three years. Nobody else "
        "on the Gunline understands his numbers. If he goes, they have to start again.",
        "He kept his ranging tables in his coat, and they burned when he fell. Three years of work, gone in a "
        "moment.\n\nI almost feel sorry for him, but not quite.",
        requires_quests=["abq_silence_the_guns"]))
    A(Q("abq_the_road_north", "The Road North", FEN, 57, 57, "Roadwalker's",
        "The Firmament Road runs north off the citadel's northern bastion. Lookout Fen Arden wants to know where it "
        "goes, and who walks it.",
        [explore(*ROAD_END, "Walk to the end of the Firmament Road")],
        "Every few days a column goes north up the road off the northern bastion, and it never comes back the same "
        "size. Walk to the end of the road and look. I want to know what's out there that's worth so many soldiers.",
        "The Fading Firmament. I've heard the name all my life, and I've never seen it.\n\nThat's where the sky's dying "
        "fastest, the old engines going dark and the islands breaking up. If the Ascendancy's marching there, they're "
        "looking for something to take before it falls.",
        requires_quests=["abq_eyes_on_the_gunline"]))

    # =================================================================================== 7. THE SKIFFMASTER (Pell)
    A(Q("abq_clear_skies", "Clear Skies", PELL, 54, 55, "Skyclearer's",
        "The Smoke-Gale Hawk nests in the chimney smoke and dives at the free skiffs coming in to the wreck. "
        "Skiffmaster Pell Daray wants the approach cleared.",
        [k("Smoke-Gale Hawk", 10)],
        "Every Smoke-Gale Hawk between here and Aurelion has learned that a skiff's full of food. They dive at the sails "
        "and the rigging, and last week one brought a skiff down in the Ashwake. Clear them off the approach.",
        "Two skiffs came in this morning without a scratch. The pilots asked who to thank, and I said you.\n\nThey'll "
        "keep flying as long as the approach is clear. That's all they need."))

    # =================================================================================== 8. THE PENS (Rosa)
    A(Q("abq_weak_seams", "Weak Seams", ROSA, 55, 56, "Seamwelder's",
        "Rosa Delgado welds the warships' hulls, and she's been welding some seams weak on purpose. She's marked which "
        "ones on a chart for Captain Isolde Marrane.",
        [deliver("ab_q_seam_chart", "Take Rosa's seam chart to Captain Isolde Marrane at Dawnspear Wreck")],
        "Every seam I weld, I weld well, because they check. But not every seam gets checked. I've marked the ones that "
        "won't hold in a storm, every one, ship by ship. Take this to the captain at the wreck. She'll know what it's "
        "worth.",
        "She marked them all. Every weak seam on every hull, ship by ship.\n\nIf those ships ever sail, I'll know which "
        "ones to hit and where. Tell her she's the bravest person on the Bastions. Then tell her to be careful.",
        turn_in_npc_id=ISOLDE,
        grant_items=carry("ab_q_seam_chart", "Rosa's Seam Chart", "A greasy chart of every warship hull on the "
                          "slipways, with some seams marked in a small careful hand.")))
    A(Q("abq_the_overseers", "The Overseers", ROSA, 55, 56, "Pensfriend's",
        "The Yard Overseer drives the Earthborn on the slipways from first light to dark. Rosa Delgado wants them "
        "taken off the quay.",
        [k("Yard Overseer", 8)],
        "Every Yard Overseer on the quay carries a rod, and they don't hesitate to use it. The conscripts work sixteen hours, and when "
        "someone falls asleep on a weld, they wake them up. Take the overseers off the quay for a while.",
        "Nobody worked past dark tonight. Siobhan says it's the first full night's sleep the pens have had in a "
        "year.\n\nThey'll send more overseers, and that's fine. We'll be rested when they get here."))
    A(Q("abq_the_drones_fix_it", "The Drones Fix It", ROSA, 55, 56, "Saboteur's",
        "The Slipway Repair-Drone inspects every seam on the hulls and fixes the weak ones. Rosa Delgado's work doesn't "
        "last a week with them about.",
        [k("Slipway Repair-Drone", 8)],
        "I weld a seam weak, and two days later a Slipway Repair-Drone finds it and fixes it properly. They're "
        "patient, and they never stop. If they're gone, my seams stay the way I left them.",
        "The drones have stopped crawling over the hulls. I welded three seams weak today and nobody touched them.\n\n"
        "You'd think I'd feel guilty about ruining good work, but I don't."))
    A(Q("abq_lay_no_more_keels", "Lay No More Keels", ROSA, 56, 56, "Keelbreaker's",
        "Each Keel Construct carries a governor that tells it which keel to lay next. Rosa Delgado wants the governors, "
        "so the yard can't start a new hull.",
        [fetch("ab_q_keel_governor", 4)],
        "The yard lays a new keel every month, and every Keel Construct carries the governor that knows the pattern. "
        "Bring me the governors. Without them, nobody here can start a new ship, and the five on the slipways are all "
        "they'll have.",
        "Four governors, and the yard's only got six constructs.\n\nI'll take these apart tonight. I want to know how "
        "they think, in case I ever need to make one think something else.",
        requires_quests=["abq_the_drones_fix_it"]))

    # =================================================================================== 9. THE PENS (Siobhan)
    A(Q("abq_medicine_run", "Medicine Run", SIOBHAN, 54, 55, "Runner's",
        "Siobhan Keane is out of almost everything in the pens. She wants a note taken to Surgeon Nell Avary at "
        "Dawnspear Wreck, asking for what the deserters can spare.",
        [deliver("ab_q_medicine_note", "Take Siobhan's note to Surgeon Nell Avary at Dawnspear Wreck")],
        "I've got two hundred patients and one tent, and the yard gives us nothing. The surgeon at the wreck sends "
        "what she can, when someone can carry it. Take her this list. Don't let the hounds on the causeway see you.",
        "Bandages, clean water, something for fever, and burn salve. She always asks for burn salve.\n\nTell her I'll "
        "send what I can. It's never enough, but it's never nothing either.",
        turn_in_npc_id=NELL,
        grant_items=carry("ab_q_medicine_note", "Siobhan's List", "A scrap of sailcloth with a list written on it in "
                          "charcoal, in a quick nurse's hand.")))
    A(Q("abq_clean_water", "Clean Water", SIOBHAN, 56, 57, "Waterbearer's",
        "The pens drink what runs off the slipways, and half of the conscripts are sick from it. The Harvested Storm on "
        "the Storm Harvest holds rain clean enough to drink. Siobhan Keane wants some.",
        [fetch("ab_q_storm_rain", 6)],
        "The water we get runs off the slipways, through the rivets and the oil, and it's making people sick. Every Harvested Storm on the rock to "
        "the north-east holds rain inside it, clean rain, the cleanest on the Bastions. Bring me what you can wring "
        "out of them.",
        "It fizzes, but it's clean. I've tested it the only way I can, which is drinking it myself.\n\nI'll give it to "
        "the sickest first. Thank you. You don't know what this means here.",
        requires_quests=["abq_medicine_run"]))
    A(Q("abq_the_hounds", "The Hounds", SIOBHAN, 56, 56, "Houndbreaker's",
        "The Causeway Construct Hound runs down conscripts who try to slip out of the pens. Siobhan Keane wants the "
        "causeway clear.",
        [k("Causeway Construct Hound", 8)],
        "Every Causeway Construct Hound on the causeway is set to hunt anyone who hasn't got an Ascendancy mark. Two of my "
        "patients tried to reach the wreck last month. The hounds brought back what was left. Clear the causeway.",
        "The causeway's quiet. Rosa says two of the welders want to try for the wreck tonight.\n\nI've told them to "
        "wait a week. But I'm glad they've got the choice."))

    # =================================================================================== 10. THE PENS (Tomasz)
    A(Q("abq_cut_the_rigging", "Cut the Rigging", TOMASZ, 57, 57, "Riggingcutter's",
        "The finished warships fly patrols up the Firmament Road. Tomasz Bielecki rigged every one, and he wants the "
        "Ascendancy Gunship brought down.",
        [k("Ascendancy Gunship", 6)],
        "I rigged every Ascendancy Gunship that flies the Firmament Road. I know where their sails are weakest, because "
        "I made them that way when I could. Bring them down. I'd like to know my knots did something useful.",
        "Six of them. I remember rigging every one, you know. I remember the names they gave them.\n\nI'm not sorry. "
        "I'm only telling you I remember."))
    A(Q("abq_thunderbirds", "Thunderbirds", TOMASZ, 56, 57, "Stormwatcher's",
        "The Harvest Thunderbird nests on the Storm Harvest and tears through the warships' sails in the storms. "
        "Tomasz Bielecki has to mend every tear by hand, and the yard blames him for each one.",
        [k("Harvest Thunderbird", 8)],
        "Every storm, a Harvest Thunderbird or two comes down off the north-east rock and goes through the warships' "
        "sails like a knife. The yard says I rig them badly and docks our rations. Thin them out, and the pens eat "
        "properly.",
        "The yard's stopped docking our rations, because the sails came through last night's storm in one piece.\n\n"
        "Funny how that works. You fix the birds, and suddenly I'm a good rigger again."))
    A(Q("abq_old_thunderhead", "Old Thunderhead", TOMASZ, 57, 57, "Thunderbreaker's",
        "The oldest of the thunderbirds, Old Thunderhead, leads the rest down on the slipways. Tomasz Bielecki wants it "
        "gone.",
        [boss("Old Thunderhead")],
        "There's one thunderbird bigger than the rest, grey round the beak, and the others follow it. The storm-keeper "
        "calls it Old Thunderhead. When it comes down, the whole flock comes with it. Put it down, and the rest will "
        "scatter.",
        "The keeper sent word that the flock's scattered all over the north-east rock and won't settle.\n\nI'm glad they're "
        "confused, and I hope it lasts a while. The sails will thank you.",
        requires_quests=["abq_thunderbirds"]))

    # =================================================================================== 11. THE PENS (Hamza)
    A(Q("abq_two_hundred_plates", "Two Hundred Plates", HAMZA, 54, 55, "Cook's",
        "Hamza Qureshi feeds the whole of the pens on scraps. The Cinder Ray in the Ashwake has meat on it that cooks "
        "itself, and he wants enough for everyone.",
        [fetch("ab_q_ray_fillet", 8)],
        "Two hundred people, one pot and whatever the yard throws away. Every Cinder Ray out in the Ashwake has a "
        "fillet on it that's half cooked from the inside already. Bring me enough, and I'll feed the pens something "
        "they'll remember.",
        "Look at these. I could open a restaurant with these.\n\nI'll do them in the pot with what spice I've got left. "
        "Two hundred plates, and not one of them sent back. I'd put money on it."))
    A(Q("abq_spice_from_the_stores", "Spice From the Stores", HAMZA, 56, 57, "Forager's",
        "The Ascendancy feeds its soldiers properly. Each Bastion Legionary on the apron carries a ration tin with real "
        "spice in it, and Hamza Qureshi wants it.",
        [fetch("ab_q_ration_tin", 6)],
        "The conscripts eat scraps, and the soldiers eat well. Every Bastion Legionary on the apron carries a ration "
        "tin, and every tin has a twist of good spice in it. I want the spice. I'll share the bread with Siobhan's "
        "patients.",
        "That's cumin, and I could cry. I haven't smelled cumin since Bradford.\n\nTonight the pens eat a proper curry. You're "
        "invited, if you can get here without the hounds seeing you."))

    # =================================================================================== 12. THE STORM HARVEST (Edda)
    A(Q("abq_the_storm_misbehaves", "The Storm Misbehaves", EDDA, 56, 57, "Stormkeeper's",
        "The collectors on the Storm Harvest drink lightning, and the Ascendancy has them drinking faster than they "
        "were built for. The Harvested Storm breaks loose. Storm-Keeper Edda Quill wants them calmed.",
        [k("Harvested Storm", 10)],
        "These collectors were built to sip at the storms, a little at a time, and that's all they can take. The Ascendancy has them gulping, and "
        "every Harvested Storm that breaks loose from them wanders the rock throwing lightning about. Calm them down "
        "the only way that works.",
        "It's quieter already, and I can hear the collectors humming properly again.\n\nThey were built by a house that's gone "
        "now, three hundred years ago. I've kept them for forty. I'd like them to outlast me."))
    A(Q("abq_collector_crystals", "Collector Crystals", EDDA, 56, 57, "Crystalkeeper's",
        "The collectors' crystals are cracking from the strain. The Lightning Elemental on the Storm Harvest grows new "
        "ones inside it, and Storm-Keeper Edda Quill wants them.",
        [fetch("ab_q_collector_crystal", 6)],
        "The crystals in the collectors are cracking, and the Ascendancy won't send new ones. Every Lightning Elemental "
        "on the rock grows a crystal inside itself, overcharged but sound. Bring me those, and I'll set them in the "
        "collectors myself.",
        "These will hold. They're angry, but they'll hold.\n\nI'll set them tomorrow. It takes a steady hand and a dry "
        "day, and we don't get many of those up here.",
        requires_quests=["abq_the_storm_misbehaves"]))
    A(Q("abq_where_the_lightning_goes", "Where the Lightning Goes", EDDA, 57, 57, "Ledgerbearer's",
        "Storm-Keeper Edda Quill keeps a ledger of where the collectors' lightning is sent. She wants Magister Orla "
        "Thessan at Dawnspear Wreck to read it.",
        [deliver("ab_q_storm_ledger", "Take Edda's ledger to Magister Orla Thessan at Dawnspear Wreck")],
        "I write down where every charge goes, because the old house taught me to. Half of it goes down into the "
        "citadel, to the foundry. The rest goes into the warships' engines, a little every day, more than a ship needs "
        "to fly. Take this ledger to the scholar at the wreck. She'll understand what it means. I don't want to.",
        "More than a ship needs to fly, and Edda's right about that.\n\nThey're not building warships to sail to the tree, or not only "
        "that. They're building them to carry something heavy. Maelis always thought bigger than the rest of us. I'm "
        "afraid of what she's thinking about now.",
        turn_in_npc_id=ORLA, requires_quests=["abq_collector_crystals"],
        grant_items=carry("ab_q_storm_ledger", "Edda's Storm Ledger", "A worn ledger of charges and destinations, "
                          "forty years of them, in a small tidy hand.")))
    return out
