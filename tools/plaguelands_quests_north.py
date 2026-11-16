"""
North Western Plaguelands' quests, levels 53-56. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT NORTH WPL IS ABOUT (docs/plaguelands_design.md). Hearthglen's country. The Scarlet Crusade's last great hold in
the west sits at the top of the map behind its walls, and its people work the fields, the lumber camp at Northridge
and the roads in between. The Scourge has a cauldron at Gahrron's Withering, and the Thondroril river runs down the
east edge. The Order of the Pale Flame keeps a camp, the Pale Watch, at the foot of the road up to Hearthglen, close
enough to see the walls.

  THE PALE WATCH (33) Watch Captain Lena Fischer (Hearthglen's gate and its soldiers, and word to Rory), Scout Mateo
                      Brandt (the roads and the river), Field Medic Noah Kowal (the river's dead, the cauldron at
                      Gahrron's Withering, and a serum for Felwood), Sister Amalie Crane (the inquisitors she used to
                      serve beside), Woodwright Jonah Lind (Northridge), Oona Byrne (the river), Clerk Wendel Ashby
                      (Hearthglen's rosters and its dogs).
  OUT                 Sorrow Hill (Lena to Rory, Amalie to Odile), the Emerald Sanctuary in Felwood (Noah's serum to
                      Dr. Nkechi Adeyemi).
  IN                  Felwood (Dr. Adeyemi's field kit to Noah).
  CAVE                The Weeping Cave, above the river (Oona: the water; Amalie: the Weeper; Wendel: the Hermit).

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and only
the people at the top know more. Inside the Order people talk about home freely. Amalie and Wendel are Lordaeron born,
walked out of Hearthglen, and call the others newcomers.

WHO PAYS. Everything here pays the Order of the Pale Flame, the zone's own faction.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

WN = "western_plaguelands_north"
WC = "the_weeping_cave"

# ---- the people
LENA, MATEO, NOAH = "wpln_pf_watch_captain", "wpln_pf_scout", "wpln_pf_field_medic"
AMALIE, JONAH, OONA, WENDEL = "wpln_pf_sister", "wpln_pf_woodwright", "wpln_pf_angler", "wpln_pf_clerk"
RORY, ODILE, NKECHI, NOVAK = "wpl_pf_flamekeeper", "wpl_pf_chaplain", "es_volunteer_medic", "brill_pf_flamewarden"

HUB_GIVERS = {LENA, MATEO, NOAH, AMALIE, JONAH, OONA, WENDEL}
NATIVE_GIVERS = {AMALIE, WENDEL}
FACTION_BY_GIVER = {}


def k(target, n, zone=WN):
    return kill(target, n, zone=zone)


def boss(target, zone=WN):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=WN, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Cauldron Sludge": [("pl_q_sludge_sample", "Cauldron Sludge Sample", "A jar of green sludge that crawled out of "
                         "the Withering's cauldron. It presses against the lid.")],
    "Hearthglen Inquisitor": [("pl_q_confession", "Signed Confession", "A confession in a clerk's hand with a shaky "
                               "signature at the bottom. The name's foreign and the crime is being born somewhere "
                               "else.")],
    "Scarlet Sawyer": [("pl_q_seasoned_plank", "Seasoned Plank", "A length of good seasoned oak, cut at Northridge "
                        "and stamped with Hearthglen's flame.")],
    "Blighted Stag": [("pl_q_stag_antler", "Blighted Stag Antler", "A tine of antler, sound under the grime. It'll "
                       "carve, if you've got a good knife.")],
    "Skeletal Wanderer": [("pl_q_keepsake", "Traveller's Keepsake", "Something small a traveller carried in a "
                           "pocket, a pipe or a thimble or a carved horse. It's been carried a long way.")],
    "Scarlet Lumberjack": [("pl_q_saw_blade", "Hearthglen Saw Blade", "A long two-man saw blade of good Hearthglen "
                            "steel, stamped with the Crusade's flame near the handle.")],
    "Scarlet Sentry": [("pl_q_patrol_roster", "Hearthglen Patrol Roster", "A week's roster of who stands where on "
                        "Hearthglen's walls, in a clerk's tidy columns.", 1.0)],
}

STARTER_DROPS = {}
STARTER_IDS = {}


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=WN, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def build():
    out = []
    A = out.append

    # ---- Watch Captain Lena Fischer
    A(Q("pln_the_gate_of_hearthglen", "The Gate of Hearthglen", LENA, 53, 53, "Pale Watch",
        "Watch Captain Lena Fischer runs the Pale Watch, the Order's camp at the foot of the road to Hearthglen. "
        "Before she sends anyone up that road, she wants them to see it.\n\nShe asks you to walk up to Hearthglen's "
        "gate and look at the walls, and then come back down without starting anything.",
        [explore(100, 22, "Look at Hearthglen's gate")],
        "Straight up the road north of the camp. You'll see the gate long before you reach it. Don't draw steel, "
        "and don't let them get a good look at your face.",
        "So now you've seen it. Walls, towers, and a lot of people who'd like to burn you.\n\nI was a police "
        "officer in Hamburg, back home. I've raided worse places, but never with a sword.",
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], nxt="pln_sentries_on_the_road"))
    A(Q("pln_sentries_on_the_road", "Sentries on the Road", LENA, 54, 55, "Pale Watch",
        "Every Scarlet Sentry on the road below Hearthglen's walls turns back anyone who isn't wearing "
        "red. Lately they've started coming down toward the Pale Watch at night.\n\nLena wants them pushed back up "
        "the hill.",
        [k("Scarlet Sentry", 10)],
        "They stand in pairs along the road and in the fields below the gate. They'll call for help, so don't let "
        "one run. Keep it quick and quiet.",
        "That'll keep them on their own side of the hill for a while.\n\nHale used to be a security contractor, "
        "back on Earth. He knows what an open flank looks like, and so do I.",
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="pln_crossbows_on_the_wall"))
    A(Q("pln_crossbows_on_the_wall", "Crossbows on the Wall", LENA, 55, 56, "Pale Watch",
        "With the sentries gone, Hearthglen's put a Scarlet Crossbowman in every hedge to cover the road. They "
        "shot one of Mateo's scouts yesterday from a hedgerow.\n\nLena wants them cleared out of the fields.",
        [k("Scarlet Crossbowman", 8)],
        "They hide in the hedges and the ditches below the walls. Close the distance fast, because a crossbow "
        "takes a while to wind and they'll know it. Don't stand still in the open.",
        "Mateo's scout is going to live, and the fields are ours to walk again.\n\nI've got something for Rory, if "
        "you're heading south.",
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")], nxt="pln_word_from_the_watch"))
    A(Q("pln_word_from_the_watch", "Word from the Watch", LENA, 55, 55, "Pale Watch",
        "Lena has watched Hearthglen's gates for a month, and she's written down everything she's seen. Hale is "
        "gathering his people inside the walls, and Lena doesn't think he's planning to defend them.\n\nShe wants "
        "her report in Rory Callahan's hands at Sorrow Hill.",
        [deliver("pl_q_lena_report", "Bring Lena's report to Flamekeeper Rory Callahan at Sorrow Hill")],
        "South down the King's Road to Sorrow Hill, by Uther's Tomb. Fly if you can. Give it to Rory and wait while "
        "he reads it, because he'll have an answer.",
        "Lena's report, in her lovely tidy hand. She writes like she's filling out a form.\n\nHale's getting ready "
        "to march. I knew he would. Tell Lena to hold the Watch, and that I'm coming north.",
        [("waist", "armor", "mail", "tide_healer"), ("back", "armor", None, "physical"),
         ("feet", "armor", "cloth", "spirit_caster")], turn_in_npc_id=RORY,
        grant_items=carry("pl_q_lena_report", "Lena's Report", "A thick report in a neat hand, with a sketch of "
                                                               "Hearthglen's gate on the back of the last page.")))

    A(Q("pln_a_letter_for_brill", "A Letter for Brill", LENA, 55, 56, "Pale Watch",
        "The Order keeps a man in Brill, Flamewarden Teodor Novak, who watches the Scarlet Monastery from a window "
        "over the inn. Lena wants him to know what Hale is doing in Hearthglen, because if Hale marches, the "
        "Monastery will march with him.\n\nShe wants her letter carried to Brill.",
        [deliver("pl_q_letter_for_novak", "Bring Lena's letter to Flamewarden Teodor Novak in Brill")],
        "South to the Bulwark, west through the gate into Tirisfal, and on to Brill. Teodor lodges over the inn. "
        "He'll offer you a drink, and you should take it.",
        "Lena's writing to me? Then it's bad.\n\nI was a firefighter in Brno, back home, and I know what it looks "
        "like when two fires are about to join up. Tell her I'll keep my eyes on the Monastery.",
        [("chest", "armor", "leather", "bruiser"), ("feet", "armor", "mail", "tide_healer"),
         ("neck", "armor", None, "spirit_caster")], turn_in_npc_id=NOVAK,
        grant_items=carry("pl_q_letter_for_novak", "Lena's Letter", "A short letter sealed with the Pale Flame, "
                                                                     "addressed to Brill in a tidy hand.")))

    # ---- Scout Mateo Brandt
    A(Q("pln_worgs_on_the_road", "Worgs on the Road", MATEO, 53, 53, "Watchman's",
        "Scout Mateo Brandt keeps the Pale Watch's roads open, and the Rotting Worgs have learned that the road is "
        "where the food walks. They run in packs and they don't let go.\n\nHe wants the packs broken up.",
        [k("Rotting Worg", 10)],
        "They run the roads south and west of the camp, mostly at dusk. Don't fight more than two at once. They'll "
        "go for your legs, so keep moving.",
        "That's a road I can walk at dusk again.\n\nI taught kids to ride horses outside Rosario, back home. Out "
        "here the horses are dead and the dogs want to eat me.",
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="pln_skeletal_wanderers"))
    A(Q("pln_skeletal_wanderers", "Skeletal Wanderers", MATEO, 53, 54, "Watchman's",
        "The Skeletal Wanderers walk the roads with nowhere to go. Mateo thinks they were travellers once, caught "
        "on the road when the plague came. They're slow, but there are a lot of them, and they never stop "
        "walking.\n\nHe wants the roads cleared of them.",
        [k("Skeletal Wanderer", 10)],
        "They wander everywhere, but the roads are where they gather. They'll turn and follow you once they've seen "
        "you. Don't let them pin you against a wall.",
        "Thank you. I hated watching them walk.\n\nThey were going somewhere, once. I suppose we all were.",
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="pln_down_to_the_river"))
    A(Q("pln_down_to_the_river", "Down to the River", MATEO, 54, 54, "Watchman's",
        "Mateo wants a way down to the Thondroril, the river along the east edge of the Plaguelands, so the Watch "
        "can fill its barrels without a long walk. He wants someone to find a safe path down to the bank and stand "
        "on it.",
        [explore(160, 60, "Find a way down to the Thondroril's bank")],
        "East from the camp, through the fields and down to the river. Find somewhere on the bank the dead don't "
        "use. You'll know it when you see it.",
        "That's a good path. We'll put a marker on it and a barrel at the bottom.\n\nOona's down there most days, "
        "fishing. Say hello if you see her.",
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")]))
    A(Q("pln_the_blighted_herd", "The Blighted Herd", MATEO, 54, 54, "Watchman's",
        "The Blighted Stags run in a herd across the fields north of the camp, and when something spooks them they "
        "stampede straight through the Pale Watch. They've flattened the tents twice.\n\nMateo wants the herd "
        "thinned before the third time.",
        [k("Blighted Stag", 8)],
        "They graze in the fields north and east of the camp. Don't stand in front of them when they run. Pick off "
        "the ones on the edge of the herd.",
        "Our tents are still standing this morning. That's a first this week.\n\nTake one of these. It's the least "
        "I can do.",
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")]))

    A(Q("pln_travellers_keepsakes", "Travellers' Keepsakes", MATEO, 54, 54, "Watchman's",
        "Mateo thinks the Skeletal Wanderers were travellers caught on the road, and some of them still carry what "
        "they had in their pockets. He wants their keepsakes, so the Order can write down what they were and "
        "maybe find someone who's still waiting for them.",
        [fetch("pl_q_keepsake", 6)],
        "The wanderers walk the roads all around the camp. Some of them still carry something small, a ring or a "
        "letter or a toy. Bring me whatever you find, and I'll write it all down.",
        "A pipe, a thimble, a child's wooden horse. Every one of these belonged to somebody.\n\nOdile at Sorrow "
        "Hill will want these for her book. I'll send them south.",
        [("hands", "armor", "plate", "plate_healer"), ("shoulder", "armor", "leather", "hunter"),
         ("back", "armor", None, "caster")]))

    # ---- Field Medic Noah Kowal
    A(Q("pln_riverbank_ghouls", "Riverbank Ghouls", NOAH, 54, 55, "Medic's",
        "Field Medic Noah Kowal patches up whoever makes it back to the Pale Watch, and lately that's been people "
        "attacked at the river. The Riverbank Ghouls hide in the reeds along the Thondroril and drag people into "
        "the water.\n\nNoah wants them cleared out.",
        [k("Riverbank Ghoul", 10)],
        "They lie in the reeds on the Thondroril's banks, east of the camp. They'll come at you from the water. "
        "Stay on the high ground and let them come to you.",
        "Nobody came in from the river with bites today. That's a good day.\n\nI was a nurse in Winnipeg, back "
        "home, and I've never been happier to have nothing to do.",
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "crusader"),
         ("ranged", "weapon", "gun", "hunter_crit")], nxt="pln_sludge_samples"))
    A(Q("pln_sludge_samples", "Sludge Samples", NOAH, 55, 55, "Medic's",
        "There's a cauldron at Gahrron's Withering, east of the camp, and Noah says the Cauldron Sludge that crawls "
        "out of the cauldron is the plague in its purest form. Noah wants to make a serum, and he needs to start with the real "
        "thing.\n\nHe wants samples, sealed.",
        [fetch("pl_q_sludge_sample", 5)],
        "The sludges crawl around the cauldron at the Withering. Kill one and scoop what's left into a jar. Keep the "
        "lid on tight, and don't breathe it in.",
        "This is horrible. Thank you.\n\nIf I can make something from this that stops the sickness, every medic on "
        "both sides of the sea will want it.",
        [("legs", "armor", "leather", "assassin"), ("hands", "armor", "mail", "tide_healer"),
         ("main_hand", "weapon", "sword_1h", "caster")], nxt="pln_the_withering"))
    A(Q("pln_the_withering", "The Withering", NOAH, 55, 55, "Medic's",
        "The cauldron at Gahrron's Withering is kept by the Cult. The Withering Cultists stir it and the Withering "
        "Ghouls carry the plague out to the fields. Noah wants the cauldron left untended.",
        [k("Withering Ghoul", 8), k("Withering Cultist", 6)],
        "East of the camp, past the dead orchard. The cultists stand at the cauldron and the ghouls work around "
        "it. Kill the cultists first, because they'll heal the rest.",
        "The cauldron's cold. That's one less in the Plaguelands.\n\nThere's someone in charge out there, though, "
        "and he isn't going to stay dead on his own.",
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")], nxt="pln_gahrron_the_withered"))
    A(Q("pln_gahrron_the_withered", "Gahrron the Withered", NOAH, 56, 56, "Medic's",
        "Gahrron owned the farm that the Withering is named for. He died there and the Cult raised him to guard "
        "their cauldron, and Gahrron the Withered still walks his land, still thinking it's his.\n\nNoah wants him "
        "put to rest, so the farm can be burned clean.",
        [boss("Gahrron the Withered")],
        "He walks the Withering, near the cauldron. He's slow, but he's strong, and the sickness comes off him in "
        "waves. Take friends, and take something for the nausea.",
        "Then the Withering's done. We'll burn it in the morning.\n\nHe was a farmer. I keep thinking about that. "
        "He just wanted to keep his farm.",
        [("head", "armor", "mail", "hunter_precise"), ("chest", "armor", "plate", "tank"),
         ("off_hand", "weapon", "tome", "caster")]))
    A(Q("pln_a_serum_for_felwood", "A Serum for Felwood", NOAH, 55, 56, "Medic's",
        "Noah's made a serum from the sludge. It doesn't cure anything, but it slows the plague down long enough to "
        "get someone to a priest. There's a doctor at the Emerald Sanctuary in Felwood, Dr. Nkechi Adeyemi, who's "
        "treating a sickness that sounds a lot like this one.\n\nNoah wants a vial of it in her hands.",
        [deliver("pl_q_serum_vial", "Bring Noah's serum to Dr. Nkechi Adeyemi at the Emerald Sanctuary")],
        "Zeppelin from Tirisfal to Orgrimmar, and then north through Ashenvale to Felwood. The Sanctuary's the clean "
        "glade in the middle of it. Keep it out of the sun.",
        "A serum, from the Plaguelands? Let me see.\n\nThis is clever work. I was an emergency doctor in Lagos, "
        "back home, and I'd have been glad of this then. Tell him I'll try it on the felblight, and I'll write.",
        [("legs", "armor", "mail", "earthen"), ("waist", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "high_healer")], turn_in_npc_id=NKECHI,
        grant_items=carry("pl_q_serum_vial", "Noah's Serum", "A small vial of pale green serum, wrapped in a "
                                                             "bandage and labelled in careful capitals.")))

    # ---- Sister Amalie Crane
    A(Q("pln_the_inquisitors", "The Inquisitors", AMALIE, 55, 56, "Sister's",
        "Sister Amalie Crane was a priestess in Hearthglen until the Hearthglen Inquisitors started questioning the "
        "newcomers. She stood in the room while they did it, and then she walked out and kept walking until she "
        "reached the Pale Watch.\n\nShe wants the inquisitors stopped.",
        [k("Hearthglen Inquisitor", 8)],
        "They walk the fields below the walls in pairs, looking for anyone to question. They'll burn you if they "
        "can, so don't let them finish a prayer.",
        "I knew some of them. I prayed beside some of them.\n\nI won't pretend I'm not glad they're gone. That's "
        "something I'll have to make peace with.",
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")], nxt="pln_the_confessions"))
    A(Q("pln_the_confessions", "The Confessions", AMALIE, 55, 56, "Sister's",
        "The Hearthglen Inquisitors carry the confessions they've forced out of people, signed and sealed, so they "
        "can be read out before a burning. Amalie wants them.\n\nEvery one has a name on it, and she wants those "
        "names remembered by someone who isn't going to burn them.",
        [fetch("pl_q_confession", 5)],
        "The inquisitors keep the confessions in their satchels. Not all of them will have one. Bring me whatever "
        "you find, and don't read them, please.",
        "Here's Agnieszka Nowak, and Tunde Bello, and Hyun-woo Park, and they didn't even spell them properly.\n\nThese people came "
        "here from nowhere and we burned them for it. I'll make sure they're remembered.",
        [("shoulder", "armor", "leather", "bruiser"), ("feet", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_1h", "wildheart")], nxt="pln_the_book_of_names"))
    A(Q("pln_the_book_of_names", "The Book of Names", AMALIE, 56, 56, "Sister's",
        "Chaplain Odile Marchand at Sorrow Hill keeps a book of names, everyone the Order knows who died in the "
        "Plaguelands. Amalie wants the confessions taken to her, so the people in them go into the book.",
        [deliver("pl_q_confession_bundle", "Bring the confessions to Chaplain Odile Marchand at Sorrow Hill")],
        "South to Sorrow Hill, by Uther's Tomb. Odile keeps the chapel there. Tell her they're from me, and that "
        "I'm sorry there are so many.",
        "These are from Amalie? She was in Hearthglen when these were taken.\n\nI'll write every name in the book tonight. "
        "Some of them were from Lyon, you know. I knew one of these streets.",
        [("hands", "armor", "plate", "tank"), ("chest", "armor", "cloth", "spirit_caster"),
         ("waist", "armor", "leather", "agility")], turn_in_npc_id=ODILE,
        grant_items=carry("pl_q_confession_bundle", "Bundle of Confessions", "The inquisitors' confessions, tied "
                                                                             "with a ribbon Amalie took from her own "
                                                                             "habit.")))
    A(Q("pln_high_inquisitor_faulk", "High Inquisitor Faulk", AMALIE, 56, 56, "Sister's",
        "High Inquisitor Faulk runs the inquisition at Hearthglen. Amalie served under him, and she says he's the "
        "one who decided the newcomers were the Scourge's agents. He walks the fields himself on feast days, with "
        "the Hearthglen Inquisitors at his back.\n\nAmalie wants him gone.",
        [boss("High Inquisitor Faulk"), k("Hearthglen Inquisitor", 4)],
        "He walks the fields below the walls, close to the gate. He's got a temper and a lot of fire, and he heals "
        "himself when he's hurt. Bring friends, and bring someone to stop his prayers.",
        "Then it's done, and the inquisition's got nobody to lead it.\n\nI keep waiting to feel something. I think "
        "maybe I feel lighter.",
        [("legs", "armor", "mail", "tide_healer"), ("head", "armor", "plate", "strength"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    # ---- Woodwright Jonah Lind
    A(Q("pln_northridge", "Northridge", JONAH, 53, 54, "Woodwright's",
        "Woodwright Jonah Lind builds everything at the Pale Watch, and he'd like to build it out of Hearthglen's "
        "timber. The Crusade runs the lumber camp at Northridge in the west, and the Scarlet Lumberjacks and "
        "Scarlet Sawyers there cut the best oak in the north.\n\nJonah wants the camp emptied.",
        [k("Scarlet Lumberjack", 8), k("Scarlet Sawyer", 6)],
        "Northridge is west of the camp, in the trees. The lumberjacks are in the woods and the sawyers are at the "
        "mill. They're working men with axes, so don't underestimate them.",
        "That's the camp quiet, then. Now we can see about the wood.\n\nI built houses in Duluth, back home. Long "
        "winters, good timber. This place reminds me of it, except for the dead.",
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")], nxt="pln_woodsman_archers"))
    A(Q("pln_woodsman_archers", "Woodsman Archers", JONAH, 54, 54, "Woodwright's",
        "With the lumberjacks gone, the Crusade's sent the Scarlet Woodsman Archers into Northridge's trees to "
        "guard the timber. They're good shots, and they know the woods.\n\nJonah wants them gone before he sends "
        "wagons in.",
        [k("Scarlet Woodsman Archer", 8)],
        "They hide in the trees around the lumber camp. Look up, because they like the high branches. Don't let "
        "them pin you down.",
        "The woods are clear. My wagons go in tomorrow.\n\nI'll need someone to pick out the good planks before the "
        "rest of them burn the lot.",
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="pln_seasoned_oak"))
    A(Q("pln_seasoned_oak", "Seasoned Oak", JONAH, 54, 55, "Woodwright's",
        "The Scarlet Sawyers at Northridge carry the camp's best seasoned planks to the carts, and Jonah wants "
        "them. The Pale Watch's palisade is green wood that's started to warp, and seasoned oak won't.\n\nHe wants "
        "enough to rebuild the gate.",
        [fetch("pl_q_seasoned_plank", 6)],
        "The sawyers at the mill carry the planks. Take them off the sawyers before they reach the carts. Look for "
        "Hearthglen's stamp, because that's the good stuff.",
        "Feel the weight of that. That's proper oak.\n\nThe gate will be up by the end of the week. I'd like to "
        "meet the man who's been running that camp, though.",
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="pln_foreman_harrow"))
    A(Q("pln_foreman_harrow", "Foreman Harrow", JONAH, 55, 55, "Woodwright's",
        "Foreman Harrow runs Northridge for the Crusade, and he's the one who's been sending the archers out. He "
        "came back to the camp yesterday with a fresh crew. Jonah wants him gone, so the camp stays empty.",
        [boss("Foreman Harrow")],
        "He's at the mill in the middle of Northridge. He's a big man with a big axe, and he doesn't like visitors. "
        "Take friends with you.",
        "That's the end of Northridge for the Crusade.\n\nThe camp's ours now. I'll put a crew in there next month "
        "and we'll cut our own timber.",
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")]))

    A(Q("pln_saw_blades", "Saw Blades", JONAH, 54, 54, "Woodwright's",
        "Jonah can't cut timber without saws, and the Crusade took every saw in the Plaguelands to Northridge. The "
        "Scarlet Lumberjacks carry good steel blades, Hearthglen forged, and Jonah wants them.",
        [fetch("pl_q_saw_blade", 5)],
        "The lumberjacks in the woods at Northridge carry their saws on their backs. Bring me the blades and leave "
        "the handles. I'll make my own.",
        "These are beautiful blades. Hearthglen's smiths know their business, I'll give them that.\n\nWe'll have a "
        "proper sawpit at the Watch by the end of the week.",
        [("legs", "armor", "plate", "strength"), ("head", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_2h", "strength")]))

    # ---- Oona Byrne
    A(Q("pln_snapjaws_on_the_thondroril", "Snapjaws on the Thondroril", OONA, 54, 54, "Angler's",
        "Oona Byrne fishes the Thondroril for the Pale Watch's supper, and the Thondroril Snapjaws keep taking her "
        "catch and her lines. They're big and they're mean and they've got nothing to fear in the river.\n\nShe "
        "wants them thinned.",
        [k("Thondroril Snapjaw", 8)],
        "They sun themselves on the banks of the Thondroril, east of the camp. Watch out for the bite, because "
        "they don't let go. Stay out of the water.",
        "My lines will last the day now.\n\nI fished out of Galway, back home. The fish here are different, but "
        "the patience is the same.",
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], nxt="pln_old_thondroril"))
    A(Q("pln_plague_bats", "Plague Bats", OONA, 53, 54, "Angler's",
        "The Plague Bats come out over the Thondroril at dusk and dive at the water, and at Oona. She's sure they "
        "carry the plague, and she's tired of fighting them off with a fishing rod.\n\nShe wants them gone.",
        [k("Plague Bat", 10)],
        "They roost in the trees along the river and come out at dusk. They're fast, so don't chase them. Let them "
        "come to you.",
        "I can fish at dusk again. That's the best time for it.\n\nThank you. Take one of these, and I'll keep a "
        "fish back for you at supper.",
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")]))
    A(Q("pln_antler_hooks", "Antler Hooks", OONA, 54, 54, "Angler's",
        "Oona's run out of fishhooks, and there's nowhere to buy them out here. She carves her own from antler, and "
        "the Blighted Stags in the fields have antlers that are sound under the grime.\n\nShe wants the antlers.",
        [fetch("pl_q_stag_antler", 6)],
        "The stags graze in the fields north and east of the camp. Bring me the tines, not the whole rack. I'll "
        "carve them tonight.",
        "These will carve beautifully.\n\nMy grandfather taught me this, back home, on the beach at Salthill. I "
        "never thought I'd need it.",
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))
    A(Q("pln_old_thondroril", "Old Thondroril", OONA, 55, 55, "Angler's",
        "There's one snapjaw in the Thondroril that Oona's never been able to drive off. Old Thondroril is older "
        "than the plague and bigger than a cart, and the Thondroril Snapjaws follow him like he's their king.\n\n"
        "Oona wants him gone, so she can fish the deep pools.",
        [boss("Old Thondroril"), k("Thondroril Snapjaw", 4)],
        "He keeps to the deepest pool on the Thondroril, and he comes up when he's hungry. Kill the young ones "
        "while you wait. Stay on the bank, because he's stronger in the water.",
        "The deep pools are mine now. Look at the size of the fish down there.\n\nYou'll eat well at the Pale "
        "Watch tonight, and every night after.",
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("ring", "armor", None, "hunter_crit")]))

    # ---- Clerk Wendel Ashby
    A(Q("pln_the_patrol_roster", "The Patrol Roster", WENDEL, 55, 55, "Clerk's",
        "Clerk Wendel Ashby kept Hearthglen's books until he saw what was being written in them. He knows the "
        "Scarlet Sentries carry the week's roster, which tells everyone where to stand on the walls.\n\nHe wants "
        "a copy, so the Watch knows the walls as well as he used to.",
        [fetch("pl_q_patrol_roster", 1)],
        "The sentries on the road below the gate carry the roster. It's in a leather case at the belt. Bring it "
        "back dry, please, because the ink runs.",
        "This is in Brother Jessup's hand. I'd know his capitals anywhere.\n\nThe newcomers here always ask how "
        "I can read the walls from a page. It's just bookkeeping, really.",
        [("feet", "armor", "leather", "assassin"), ("head", "armor", "plate", "crusader"),
         ("wrist", "armor", "cloth", "healer")], nxt="pln_hearthglens_hounds"))
    A(Q("pln_hearthglens_hounds", "Hearthglen's Hounds", WENDEL, 55, 56, "Clerk's",
        "The roster says Hearthglen sends its Scarlet War Hounds out at night to hunt anyone near the walls. "
        "Wendel used to feed them. He says they were good dogs once.\n\nHe wants them stopped.",
        [k("Scarlet War Hound", 10)],
        "They hunt the fields below the walls at night, and they hunt in packs. Don't let them circle you. Back up "
        "against something and let them come.",
        "They were good dogs once. I used to give them the scraps from the kitchen.\n\nThat's done, then. Thank "
        "you. I'll write it down, because somebody should.",
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "strength")]))

    # ---- the Weeping Cave, in the hill above the Thondroril (tools/handbuilt_plaguelands_caves.py)
    A(Q("pln_the_water_under_the_hill", "The Water Under the Hill", OONA, 55, 56, "Angler's",
        "Oona Byrne has fished the Thondroril every day since the Watch made camp, and she says the river's gone "
        "wrong. There's water running out of the hill above it that tastes of the grave, and it's coming out of the "
        "Weeping Cave.\n\nShe wants the Cave Drowned and the Seepwater Shades cleared out of the water.",
        [k("Cave Drowned", 8, WC), k("Seepwater Shade", 8, WC)],
        "The cave's in the hill on the east side, up above the river. You'll hear it before you see it, because the "
        "water never stops running down the walls. Mind your feet in there, it's slick all the way down.",
        "The fish'll come back now, give it a week.\n\nThere's a cave like that on the coast near Galway, back home. "
        "The water ran out of it clean. I never thought I'd miss a cave.",
        [("legs", "armor", "leather", "hunter"), ("shoulder", "armor", "cloth", "frost"),
         ("feet", "armor", "plate", "tank_any")], nxt="pln_the_weeper"))
    A(Q("pln_the_weeper", "The Weeper", AMALIE, 56, 56, "Sister's",
        "Sister Amalie Crane heard Oona's account of the Weeping Cave, and she knows the story behind it. A woman "
        "went into the pool at the end of the cave to look for her family after Hearthglen took them for "
        "questioning, and she never came out.\n\nAmalie says The Weeper is her, and she's asking you to let her rest.",
        [boss("The Weeper", WC)],
        "The pool's at the far end of the cave, past both galleries. She'll know you're coming, because she's been "
        "waiting for somebody for years. Be gentle if you can, and be quick if you can't.",
        "Thank you. I'll write her name in the chapel book, under the ones Hearthglen never wrote down.\n\nI kept "
        "quiet in that room for a long time. I'm trying to make up for it, one name at a time.",
        [("head", "armor", "cloth", "spirit_healer"), ("hands", "armor", "leather", "rogue_crit"),
         ("main_hand", "weapon", "sword_1h", "strength_hit")]))
    A(Q("pln_the_hermits_account", "The Hermit's Account", WENDEL, 56, 56, "Clerk's",
        "Clerk Wendel Ashby remembers every name in Hearthglen's ledgers, and one of them belonged to a hermit who "
        "lived in the cave above the river and paid his tithe in fish. The Crusade stopped taking his fish when the "
        "plague came, and he stopped coming down.\n\nWendel's heard that The Drowned Hermit still keeps his cell in "
        "the roof of the Weeping Cave, and that he won't let anyone past.",
        [boss("The Drowned Hermit", WC)],
        "His cell's up through the roof of the upper gallery, about halfway along. He'll have his oar, I expect, "
        "because he never went anywhere without it. Close his account for me, would you?",
        "Tobias Fenn, paid in perch every quarter for eleven years. I'll mark him settled.\n\nIt's a small thing, "
        "closing an account properly. Somebody ought to do it for everyone Hearthglen forgot.",
        [("waist", "armor", "mail", "mail_caster"), ("back", "armor", None, "assassin"),
         ("wrist", "armor", "plate", "plate_healer")]))

    # ---- in from Felwood
    A(Q("pln_supplies_from_felwood", "Supplies from Felwood", NKECHI, 52, 53, "Doctor's",
        "Dr. Nkechi Adeyemi has heard from the Order of the Pale Flame that their field medic at the Pale Watch is "
        "stitching people up with thread he boils in a pot. She's packed everything the Emerald Sanctuary can "
        "spare.\n\nShe needs it carried to Field Medic Noah Kowal in the Western Plaguelands.",
        [deliver("pl_q_nkechis_kit", "Bring Dr. Adeyemi's field kit to Field Medic Noah Kowal at the Pale Watch")],
        "It's a long way, I know. Get yourself to the Eastern Kingdoms, through Tirisfal to the Bulwark, and keep "
        "going north. The Pale Watch is at the foot of the road to Hearthglen. Don't let anyone ration the sutures.",
        "Real sutures, clean dressings, and a bottle of something I haven't seen since Winnipeg.\n\nTell Dr. Adeyemi "
        "she's saved more people today than I've managed all month. Then come back, because I've got work for you.",
        [("chest", "armor", "cloth", "high_healer"), ("legs", "armor", "plate", "strength_crit"),
         ("ring", "armor", None, "agility")], zone="emerald_sanctuary", turn_in_npc_id=NOAH,
        grant_items=carry("pl_q_nkechis_kit", "Dr. Adeyemi's Field Kit", "A canvas roll of sutures, dressings and "
                          "small brown bottles, packed tight and labelled in English.")))
    return out
