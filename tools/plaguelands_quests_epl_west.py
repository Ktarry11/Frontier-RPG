"""
West Eastern Plaguelands' quests, levels 55-58. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT WEST EPL IS ABOUT (docs/plaguelands_design.md). The road from the river to Stratholme, and the worst of the
Plaguelands. Plaguewood and Terrordale are the Scourge's own country, the Cult runs its plague carts through Corin's
Crossing, the Marris family still works their farm long after they died, something fungal is growing in the vale,
and the dead knights at Stratholme's gates let nobody near the city.

There's no camp on this map, so its quests are given at the two hubs next door, Crown Guard and Light's Hope, which
is how the Argent Dawn has always fought this war: from holy ground, a long walk from the enemy.

  CROWN GUARD (20)   Outrider Bram Tolliver (the road west and Corin's Crossing), Edda Marris (her family's farm),
                     Dr. Sun Li (the Fungal Vale, and spores for Felwood), Gravewarden Osric Vey (Terrordale, and a
                     word for Sun Rock), Innkeeper Greta Lowe (crow pie).
  LIGHT'S HOPE (10)  Ser Roland Ashcombe (Stratholme's gates), Huntress Kaia Lindgren (Plaguewood), Commander Eligor
                     Dawnbringer (a look at Stratholme).
  OUT                Sun Rock in Stonetalon (Osric's account of Terrordale to Spiritwalker Tohana, who's watching
                     the dead rise in Mulgore), the Emerald Sanctuary in Felwood (Sun Li's spores to Yuki Hashimoto).
  IN                 Felwood (Yuki's jar back to Sun Li).
  CAVE               The Marris Crypt, under the stead (Edda: the family's dead, then the sexton and the choir).
  ALSO               Bat Handler Gwen Pike (Crown Guard) on the gargoyles over Stratholme's gates.

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and only
the people at the top know more. Bram, Edda, Osric, Greta, Roland and Dawnbringer were born here and say newcomers.
Sun Li and Kaia are transplants and talk about home.

WHO PAYS. Everything here pays the Argent Dawn, the zone's own faction.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

EW = "eastern_plaguelands_west"
MC = "the_marris_crypt"

# ---- the people
BRAM, EDDA, SUNLI, OSRIC, GRETA = ("epl_cg_outrider", "epl_cg_widow", "epl_cg_mycologist", "epl_cg_gravewarden",
                                   "epl_cg_innkeeper")
ROLAND, KAIA, DAWN = "epl_lh_knight", "epl_lh_huntress", "epl_lh_commander"
TOHANA, YUKI = "sr_spirit_walker", "es_volunteer_botanist"
GWEN = "epl_cg_flight"

HUB_GIVERS = {BRAM, EDDA, SUNLI, OSRIC, GRETA, ROLAND, KAIA, DAWN, GWEN}
NATIVE_GIVERS = {BRAM, EDDA, OSRIC, GRETA, ROLAND, DAWN, GWEN}
FACTION_BY_GIVER = {}


def k(target, n, zone=EW):
    return kill(target, n, zone=zone)


def boss(target, zone=EW):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=EW, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Cult Cart Driver": [("pl_q_cart_manifest", "Plague Cart Manifest", "A cart driver's manifest, listing barrels "
                          "of grain by the farm they're going to. Every farm on it is still alive.", 1.0)],
    "Spore-Walker": [("pl_q_spore_cap", "Spore-Walker Cap", "A mushroom cap the size of a dinner plate, cut from a "
                      "spore-walker's shoulders. It breathes, very slowly.")],
    "Plaguewood Spider": [("pl_q_spider_silk", "Plaguewood Silk", "A hank of grey silk from a Plaguewood spider. It's "
                           "stronger than rope and sticky to the touch.")],
    "Gate Death Knight": [("pl_q_knight_sigil", "Knightly Sigil", "An enamelled sigil from a death knight's "
                           "breastplate, the colours of a Lordaeron house still bright under the frost.")],
    "Plague Hound": [("pl_q_hound_fang", "Plague Hound Fang", "A long canine from a plague hound, hard as flint and "
                      "nearly as sharp.")],
    "Stead Crow": [("pl_q_crow", "Plump Stead Crow", "A fat crow from the Marris Stead. Greta swears they're the "
                    "best thing to eat for miles. Greta has strange tastes.")],
    "Marris Farmhand": [("pl_q_marris_locket", "The Marris Locket", "A small brass locket with a painting of a "
                         "family inside, two parents and three children in their Sunday best.", 0.5)],
}

STARTER_DROPS = {}
STARTER_IDS = {}


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=EW, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def build():
    out = []
    A = out.append

    # ======================================================================================== CROWN GUARD
    # ---- Outrider Bram Tolliver
    A(Q("plw_the_road_west", "The Road West", BRAM, 55, 55, "Outrider's",
        "Outrider Bram Tolliver rides the road west from Crown Guard to the river, and he's the only one who does it "
        "regularly. The Plague Hounds hunt along it in packs, and the Frenzied Ghouls come out of the ditches when "
        "they hear horses.\n\nHe wants the road safe enough for someone other than him.",
        [k("Plague Hound", 8), k("Frenzied Ghoul", 8)],
        "West from Crown Guard, along the old road toward the river. The hounds run the open ground and the ghouls "
        "hide in the ditches. Don't stop moving, because they'll swarm you.",
        "That's a road a wagon could use again.\n\nThe newcomers at the chapel keep asking me why I ride it alone. "
        "I tell them it's because nobody else is daft enough.",
        [("chest", "armor", "plate", "tank"), ("legs", "armor", "cloth", "caster"),
         ("hands", "armor", "leather", "agility")], nxt="plw_corins_crossing"))
    A(Q("plw_corins_crossing", "Corin's Crossing", BRAM, 56, 56, "Outrider's",
        "Corin's Crossing was a crossroads town until the Cult took it over. Now it's where the plague carts load up. "
        "The Cult Plaguebringers fill the barrels and the Cult Cart Drivers take them out to the farms that are "
        "still alive.\n\nBram wants the crossing shut down.",
        [k("Cult Plaguebringer", 8), k("Cult Cart Driver", 6)],
        "West along the road from Crown Guard, where the roads cross. The plaguebringers are at the barrels in the "
        "square and the drivers are with the carts. Kill the plaguebringers first, because they'll throw the "
        "barrels.",
        "No carts left the crossing today. That's the first day in a year.\n\nOne of the drivers had papers on "
        "him, and I'd like you to see them.",
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], nxt="plw_the_manifest"))
    A(Q("plw_the_manifest", "The Manifest", BRAM, 56, 56, "Outrider's",
        "The Cult Cart Drivers carry manifests that say where every barrel of plague is going. Bram wants one, so "
        "the Dawn can warn the farms on it before the carts get there.",
        [fetch("pl_q_cart_manifest", 1)],
        "Find a driver at the crossing and take his manifest off him. It'll be in his coat. Bring it back as fast as "
        "you can, because those carts don't wait.",
        "These are all farms in Lordaeron that are still alive, and some in the hills past it.\n\nI'll have riders "
        "out to every one of them by nightfall. You've saved lives today, whether you see them or not.",
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="plw_the_crossings_abominations"))
    A(Q("plw_the_crossings_abominations", "The Crossing's Abominations", BRAM, 57, 57, "Outrider's",
        "The Cult brought in Crossing Abominations to guard the carts after the drivers started dying. They stand "
        "in the square at Corin's Crossing and they don't move unless something comes near.\n\nBram wants them "
        "brought down before the Cult can use them again.",
        [k("Crossing Abomination", 5)],
        "They stand in the square at the crossing, around the carts. They're slow and they hit like a falling "
        "barn. Pull them one at a time if you can.",
        "That's the crossing's muscle gone.\n\nThere's only one man left running the carts, and I know exactly "
        "where he sleeps.",
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")], nxt="plw_cartmaster_corin"))
    A(Q("plw_cartmaster_corin", "Cartmaster Corin", BRAM, 57, 57, "Outrider's",
        "Cartmaster Corin gave the crossing its name. He ran a carting business there before the plague, and now he "
        "runs it for the Cult, with the same ledgers and the same smile.\n\nBram wants him dead and his ledgers "
        "burned.",
        [boss("Cartmaster Corin")],
        "He's in the old counting house at the crossing. He doesn't fight fair and he'll call everything nearby to "
        "help. Take friends with you.",
        "Then the carts stop for good. I'll burn the counting house myself tonight.\n\nI bought horses off him "
        "once, you know. He gave me a fair price.",
        [("head", "armor", "mail", "hunter_precise"), ("waist", "armor", "plate", "crusader"),
         ("back", "armor", None, "physical")]))

    # ---- Edda Marris
    A(Q("plw_the_marris_stead", "The Marris Stead", EDDA, 55, 56, "Marris",
        "Edda Marris married into the Marris family two summers before the plague, and she was in town the day it "
        "reached the farm. She came home to find everyone dead and still working. The Marris Farmhands still walk "
        "the fields, and the Stead Crows pick at them.\n\nShe wants them put to rest.",
        [k("Marris Farmhand", 8), k("Stead Crow", 6)],
        "The Marris Stead is south of the road, toward Terrordale. The farmhands work the fields and the crows "
        "follow them. They were good people, and they'd want it quick.",
        "Thank you. I've wanted that done for a long time, and I couldn't do it myself.\n\nOne of them always wore "
        "a locket. I'd give anything to have it back.",
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="plw_the_marris_locket"))
    A(Q("plw_the_marris_locket", "The Marris Locket", EDDA, 56, 56, "Marris",
        "Edda's sister-in-law wore a brass locket with a painting of the whole family inside. She's still wearing it, "
        "out in the fields with the other Marris Farmhands. Edda wants it back.",
        [fetch("pl_q_marris_locket", 1)],
        "She'll be one of the farmhands in the fields at the stead. It's a little brass locket on a chain. You'll "
        "know it when you see it.",
        "That's them, all of them. That's the summer before everything.\n\nI'm not in it. I hadn't married in yet. "
        "There's one more of them out there, though, and he's the worst to think about.",
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="plw_old_marris"))
    A(Q("plw_old_marris", "Old Marris", EDDA, 56, 56, "Marris",
        "Old Marris was the head of the family, a stubborn man who built the farm with his own hands. He still walks "
        "it, still giving orders to the dead. Edda wants him to rest with the others.",
        [boss("Old Marris")],
        "He's in the farmhouse, or in the barn behind it. He's strong, because he always was. Take friends if you "
        "can, and be kind to him if you can't.",
        "Then they're all at rest. The farm can go back to being a farm.\n\nI think I'll go back there in the "
        "spring and plant something. He'd have liked that.",
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")]))

    # ---- Dr. Sun Li
    A(Q("plw_the_fungal_vale", "The Fungal Vale", SUNLI, 56, 56, "Mycologist's",
        "Dr. Sun Li studied fungi at a university in Kunming, back home, and the Fungal Vale is the most frightening "
        "thing she's ever seen. Something is growing there, and the Vale Plague Slimes and the Spore-Walkers are "
        "spreading it.\n\nShe wants them thinned before it spreads further.",
        [k("Vale Plague Slime", 8), k("Spore-Walker", 6)],
        "The vale's north of the crossing, along the road toward Stratholme. The slimes crawl on the ground and the "
        "walkers drift between the caps. Don't breathe the spores, and keep your mouth shut.",
        "That's slowed it down, I think. It's hard to tell with fungus.\n\nI need samples, if you'll go back, and "
        "I want them fresh.",
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")], nxt="plw_spore_caps"))
    A(Q("plw_spore_caps", "Spore Caps", SUNLI, 56, 57, "Mycologist's",
        "The Spore-Walkers in the Fungal Vale grow caps on their shoulders, and Sun Li thinks the caps are where the "
        "plague is changing. She wants them, cut fresh.",
        [fetch("pl_q_spore_cap", 5)],
        "Cut the caps off the walkers in the vale. Put them in the sacks I gave you and tie them tight. If one "
        "starts to puff, drop it and don't look back.",
        "These are breathing. They're actually breathing.\n\nIt's not one fungus, it's dozens growing together. "
        "Something at the middle of the vale is holding them together.",
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "crusader"),
         ("ranged", "weapon", "gun", "hunter_crit")], nxt="plw_the_fungal_mass"))
    A(Q("plw_the_fungal_mass", "The Fungal Mass", SUNLI, 57, 57, "Mycologist's",
        "At the heart of the Fungal Vale there's something Sun Li can only call a mass, a fungus the size of a "
        "house that moves when it wants to. The Fungal Mass is what's feeding the rest. She wants it killed.",
        [boss("The Fungal Mass")],
        "It sits in the middle of the vale and it'll come at you when you get close. It's huge and it's poisonous. "
        "Take friends and take antidotes.",
        "It's really dead? Then the vale will start dying back in a week.\n\nThat was the strangest organism I've ever "
        "studied, and I'm glad it's gone.",
        [("legs", "armor", "leather", "assassin"), ("hands", "armor", "mail", "tide_healer"),
         ("main_hand", "weapon", "sword_1h", "caster")]))
    A(Q("plw_spores_for_the_sanctuary", "Spores for the Sanctuary", SUNLI, 57, 57, "Mycologist's",
        "Sun Li has sealed a sample of the Fungal Vale's spores in wax, and she knows a botanist at the Emerald "
        "Sanctuary in Felwood, Yuki Hashimoto, who's cataloguing everything that grows back in corrupted ground.\n\n"
        "She wants the sample in Yuki's hands, so they can compare.",
        [deliver("pl_q_spore_sample", "Bring Sun Li's spore sample to Yuki Hashimoto at the Emerald Sanctuary")],
        "Zeppelin from Tirisfal to Orgrimmar, then north through Ashenvale to Felwood. Yuki's at the Sanctuary, "
        "probably on her knees in a flowerbed. Don't break the wax.",
        "From Dr. Sun? I read her papers at university, back home.\n\nThe corruption here makes things grow back "
        "wrong, and these spores are doing the same thing. I'll write to her tonight.",
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")], turn_in_npc_id=YUKI,
        grant_items=carry("pl_q_spore_sample", "Sealed Spore Sample", "A glass jar sealed in red wax, with something "
                                                                      "grey and soft growing on the inside of the "
                                                                      "glass.")))

    # ---- Gravewarden Osric Vey
    A(Q("plw_terrordale", "Terrordale", OSRIC, 56, 57, "Gravewarden's",
        "Gravewarden Osric Vey keeps the Argent Dawn's dead, and Terrordale is full of dead nobody's kept. The "
        "Terrordale Ghouls hunt the hills and the Terrordale Spirits wail over them.\n\nHe wants the valley quieter.",
        [k("Terrordale Ghoul", 8), k("Terrordale Spirit", 6)],
        "Terrordale is in the south west, past the Marris Stead. The ghouls hunt the valley floor and the spirits "
        "drift along the hills. Stay out of the spirits' reach, because they'll drain you.",
        "I felt that from here. The valley's quieter tonight.\n\nThere's worse in Terrordale, though. The ones who "
        "raise the dead are still there.",
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")], nxt="plw_the_skeletal_mages"))
    A(Q("plw_the_skeletal_mages", "The Skeletal Mages", OSRIC, 57, 57, "Gravewarden's",
        "Terrordale's dead don't stay down because the Terrordale Skeletal Mages raise them again every night. "
        "They were Kirin Tor mages once, Osric thinks, sent to fight the plague and lost to it.\n\nHe wants them "
        "destroyed.",
        [k("Terrordale Skeletal Mage", 8)],
        "They stand among the dead in Terrordale, raising them. Kill them quickly, because they'll raise anything "
        "you kill around them.",
        "No more risings in Terrordale. Thank the Light.\n\nThe thing that rules that valley is still there, "
        "though, and it's what made them.",
        [("shoulder", "armor", "leather", "bruiser"), ("feet", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_1h", "wildheart")], nxt="plw_the_terror_of_the_dale"))
    A(Q("plw_the_terror_of_the_dale", "The Terror of the Dale", OSRIC, 57, 57, "Gravewarden's",
        "Terrordale is named for what lives in it. The Terror of the Dale was a lich's apprentice who stayed behind "
        "when the lich moved north, and it's held the valley ever since. Osric wants it ended.",
        [boss("The Terror of the Dale")],
        "It holds the ruined chapel in the middle of Terrordale. It's a caster, and it'll freeze you if you let it. "
        "Take friends, and keep moving.",
        "Then Terrordale belongs to nobody, and it can rest.\n\nI'll write what happened there and send it west. "
        "There's someone across the sea who needs to read it.",
        [("hands", "armor", "plate", "tank"), ("chest", "armor", "cloth", "spirit_caster"),
         ("waist", "armor", "leather", "agility")], nxt="plw_word_for_sun_rock"))
    A(Q("plw_word_for_sun_rock", "Word for Sun Rock", OSRIC, 57, 57, "Gravewarden's",
        "Osric has heard from the Forsaken that the dead are rising in Mulgore, across the sea, with nobody calling "
        "them. A tauren spiritwalker at Sun Rock Retreat in Stonetalon, Tohana, is trying to understand why. Osric "
        "has written down everything he knows about Terrordale.\n\nHe wants his account in Tohana's hands.",
        [deliver("pl_q_osric_account", "Bring Osric's account of Terrordale to Spiritwalker Tohana at Sun Rock")],
        "Zeppelin from Tirisfal to Orgrimmar, and a wind rider to Sun Rock. Tohana's the spiritwalker by the "
        "fire. Give it to Tohana and nobody else.",
        "From the Plaguelands? From a gravewarden of the Dawn?\n\nThe spirits in Mulgore are restless the same way, "
        "like something's calling them and they don't know where from. This helps more than you know. Tell him the earth thanks him.",
        [("legs", "armor", "mail", "tide_healer"), ("head", "armor", "plate", "strength"),
         ("ranged", "weapon", "wand", "caster")], turn_in_npc_id=TOHANA,
        grant_items=carry("pl_q_osric_account", "Osric's Account", "A long letter in a gravewarden's careful hand, "
                                                                   "sealed with the Dawn's sunburst.")))

    # ---- Innkeeper Greta Lowe
    A(Q("plw_crow_pie", "Crow Pie", GRETA, 55, 56, "Hearthside",
        "Greta's grandmother made crow pie, and the Stead Crows at the Marris Stead are the fattest crows Greta has "
        "ever seen. She wants to make it for the camp, whether the camp likes it or not.",
        [fetch("pl_q_crow", 6)],
        "The crows follow the farmhands at the Marris Stead, south of the road. Get the fat ones. Don't tell anyone "
        "what's in the pie until after they've had seconds.",
        "Look at the size of them! That's a pie for the whole camp.\n\nThe newcomers will eat it and ask what it "
        "was. I'll tell them it's chicken, and they'll believe me.",
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")]))

    # ======================================================================================== LIGHT'S HOPE
    # ---- Ser Roland Ashcombe
    A(Q("plw_gargoyles_over_the_road", "Gargoyles over the Road", ROLAND, 56, 57, "Ashcombe's",
        "Ser Roland Ashcombe keeps the Argent Dawn's watch on Stratholme, and the Stone-Winged Gargoyles keep "
        "watching him back. They fly over the road from the city and dive on anyone who looks too long.\n\nRoland "
        "wants the sky over the road cleared.",
        [k("Stone-Winged Gargoyle", 8)],
        "They circle over the road north of the crossing, toward Stratholme. They'll turn to stone if they're hurt, "
        "so finish them quickly. Don't let them get above you.",
        "I can see the road again without a gargoyle in the way.\n\nThe gate's a different matter, and that's "
        "where the real work is.",
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="plw_the_gates_of_stratholme"))
    A(Q("plw_the_gates_of_stratholme", "The Gates of Stratholme", ROLAND, 57, 58, "Ashcombe's",
        "Stratholme's gates are held by Gate Death Knights and the Gate Gargoyles that perch over them. Roland was a "
        "knight of Lordaeron, and some of those death knights were his brothers in arms.\n\nHe wants the gates "
        "thinned, so the Dawn can get close enough to see inside.",
        [k("Gate Death Knight", 6), k("Gate Gargoyle", 6)],
        "Follow the road north past the Fungal Vale and west through Plaguewood. The gates are at the end of it. "
        "The death knights don't retreat, so pick them off one at a time.",
        "I knew some of those men. I'll pray for them, the ones I recognised.\n\nThere's one left at the gate who "
        "holds it, and he's the one I want.",
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="plw_gatekeeper_vorthas"))
    A(Q("plw_gatekeeper_vorthas", "Gatekeeper Vorthas", ROLAND, 58, 58, "Ashcombe's",
        "Gatekeeper Vorthas was a captain of Stratholme's guard, and he held the gate when the city fell. He holds it "
        "still, for the Scourge now. Roland served under him.\n\nHe wants his old captain at rest.",
        [boss("Gatekeeper Vorthas")],
        "He stands at Stratholme's gate, where he always stood. He's a death knight now, and he's strong. Take "
        "friends, and don't fight him alone.",
        "Then he's at rest. I hope he knows that I'm sorry.\n\nHe taught me how to hold a shield. Every one of us "
        "who served under him owes you for this.",
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")]))

    A(Q("plw_sigils_of_the_fallen", "Sigils of the Fallen", ROLAND, 57, 58, "Ashcombe's",
        "The Gate Death Knights still wear the sigils of the knightly houses they served when they were alive. "
        "Roland wants them back, so the houses that are left can know what happened to their sons and daughters.",
        [fetch("pl_q_knight_sigil", 5)],
        "The death knights at Stratholme's gate wear the sigils on their breastplates. Cut them off and bring them "
        "here. I'll know every house by its colours.",
        "That's Barov, and that's Mardenholde, and this one's my own cousin's house.\n\nI'll write to every family "
        "that's left. It's the least they deserve, and it's more than most of them will get.",
        [("chest", "armor", "mail", "hunter_precise"), ("feet", "armor", "plate", "tank_any"),
         ("ring", "armor", None, "caster")]))

    # ---- Huntress Kaia Lindgren
    A(Q("plw_plaguewood", "Plaguewood", KAIA, 56, 57, "Huntress's",
        "Huntress Kaia Lindgren hunted reindeer in the north of Norway before the Integration, and now she hunts "
        "for Light's Hope. Plaguewood's the worst hunting ground she's ever seen. The Plaguewood Spiders spin their "
        "webs across every path, and the Plaguewood Crypt Fiends dig under them.\n\nShe wants them cleared.",
        [k("Plaguewood Spider", 8), k("Plaguewood Crypt Fiend", 5)],
        "Plaguewood's north and west of the crossing, on the road to Stratholme. The spiders are in the trees and the "
        "fiends are underground. Watch where you step, because they come up underneath you.",
        "That's some ugly hunting. Thank you for doing it with me.\n\nI was a reindeer herder outside Tromso, back "
        "home. I never thought I'd miss the cold.",
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], nxt="plw_plaguewood_silk"))
    A(Q("plw_plaguewood_silk", "Plaguewood Silk", KAIA, 57, 57, "Huntress's",
        "Kaia makes her own snares, and the Plaguewood Spiders spin silk that's stronger than any rope in the "
        "Plaguelands. She wants enough of it to rig snares around the whole chapel.",
        [fetch("pl_q_spider_silk", 6)],
        "The spiders in Plaguewood carry silk in their glands. Cut it out carefully, because it sticks to "
        "everything. Wear gloves if you've got them.",
        "This is beautiful silk. I'll have snares around the chapel by the weekend.\n\nThere's a big one in "
        "Plaguewood, the mother of all of them. I'd like to see her gone.",
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")], nxt="plw_the_plaguewood_matriarch"))
    A(Q("plw_the_plaguewood_matriarch", "The Plaguewood Matriarch", KAIA, 58, 58, "Huntress's",
        "Every spider in Plaguewood came from the same nest, and the thing that laid them still sits in it. Kaia "
        "calls her the Plaguewood Matriarch, and she's bigger than a horse.\n\nKaia wants her dead.",
        [boss("The Plaguewood Matriarch")],
        "She's in the deepest part of Plaguewood, where the webs are thickest. She's fast and she's poisonous. Take "
        "friends, and bring a knife for the webs.",
        "She's really dead? Then Plaguewood will empty out in a season.\n\nI'll make you a snare from her silk, if you "
        "like. It'd hold a dragon.",
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))
    A(Q("plw_carrion_grubs", "Carrion Grubs", KAIA, 55, 56, "Huntress's",
        "The Carrion Grubs eat everything that dies on the road west, and then they eat everything that's alive "
        "and slow. Kaia's lost a dozen snares to them.\n\nShe wants them gone.",
        [k("Carrion Grub", 10)],
        "They swarm the road and the ditches beside it. They're slow and they're soft, but there are always more. "
        "Burn them if you can.",
        "That's the road clear of them for a while, anyway.\n\nThank you. I'd rather hunt anything else in the "
        "world than those.",
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    A(Q("plw_hound_fangs", "Hound Fangs", KAIA, 55, 56, "Huntress's",
        "Kaia's run out of arrowheads, and the Plague Hounds on the road west have fangs as hard as flint. She's "
        "been knapping them into points, and they fly true.\n\nShe wants more fangs.",
        [fetch("pl_q_hound_fang", 6)],
        "The hounds run in packs along the road west from Crown Guard. Pull the big canines, the ones at the front. "
        "I'll do the rest by the fire.",
        "These are perfect. I'll have a quiver full by tomorrow night.\n\nMy grandfather made fishhooks from bone, "
        "back home. I didn't think I'd ever need to know how.",
        [("legs", "armor", "leather", "agility"), ("waist", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "assassin")]))

    # ---- Commander Eligor Dawnbringer
    A(Q("plw_a_look_at_stratholme", "A Look at Stratholme", DAWN, 57, 57, "Dawnbringer's",
        "Dawnbringer has never seen Stratholme since it fell, and he won't send the Dawn in until someone has. He "
        "wants you to walk to the city's gate and look at it.\n\nJust look, he says. Then come back.",
        [explore(43, 10, "Look at Stratholme's gate")],
        "West along the road, north past the Fungal Vale, and west through Plaguewood. The gate's at the end of the "
        "road. Don't go in, whatever you hear.",
        "Then it's as bad as we thought.\n\nThe newcomers say they've seen cities like that in their dreams, burned "
        "and empty. I wish they hadn't.",
        [("waist", "armor", "mail", "tide_healer"), ("back", "armor", None, "physical"),
         ("feet", "armor", "cloth", "spirit_caster")]))

    # ---- the Marris Crypt, under the stead (tools/handbuilt_plaguelands_caves.py)
    A(Q("plw_the_family_crypt", "The Family Crypt", EDDA, 56, 57, "Widow's",
        "Edda Marris married into the family whose farm is still being worked by the dead. The Marris dead have a "
        "crypt under the stead, and Edda's heard they don't stay in their niches any more.\n\nShe wants the Crypt "
        "Shamblers put down and the Marris Ossuary Guards stopped, so the family can lie where they were put.",
        [k("Crypt Shambler", 10, MC), k("Marris Ossuary Guard", 6, MC)],
        "The stair down's at the stead, south of the farmhouse. It's laid out like a grid down there, so count your "
        "turns. The guards were the family's own men once, and they'll still try to stop you.",
        "Thank you. My husband's grandmother is down there somewhere, and I hope she's back where she belongs.\n\n"
        "There's more, though. Something's still singing down there, and it isn't any hymn I know.",
        [("head", "armor", "mail", "storm"), ("legs", "armor", "cloth", "arcane"),
         ("hands", "armor", "plate", "bruiser")], nxt="plw_the_sexton"))
    A(Q("plw_the_sexton", "The Sexton", EDDA, 57, 58, "Widow's",
        "Edda says the family's sexton buried every Marris for forty years and wouldn't stop when the plague came. "
        "Sexton Hollowell is still down there digging, and the dead he's buried sing for him.\n\nShe wants him put "
        "in the ground for good, and The Bone Choir silenced.",
        [boss("Sexton Hollowell", MC), boss("The Bone Choir", MC)],
        "The sexton's hall is in the middle of the crypt, and the choir sings from the chapel at the head of it. "
        "You'll hear them both. Don't listen to the words, because they'll tell you to lie down.",
        "It's gone quiet down there. I didn't know how loud it was until it stopped.\n\nI'll go down myself next week and say their "
        "names. Somebody in the family should, and I'm the only one of us left breathing.",
        [("chest", "armor", "plate", "crusader"), ("feet", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "polearm", "bear_weapon")]))

    # ---- Bat Handler Gwen Pike: the gargoyles over Stratholme's gates
    A(Q("plw_gargoyles_over_the_gates", "Gargoyles Over the Gates", GWEN, 57, 58, "Bat Handler's",
        "Bat Handler Gwen Pike flies the Argent Dawn's bats between Light's Hope and the western road, and the Gate "
        "Gargoyles over Stratholme have started coming out to meet them. She's lost two bats this month.\n\nShe "
        "wants the Gate Gargoyles knocked out of the sky, and the Stone-Winged Gargoyles that hunt the open ground "
        "below them too.",
        [k("Gate Gargoyle", 8), k("Stone-Winged Gargoyle", 8)],
        "The gate ones roost on Stratholme's walls at the top of the western road, and the wild ones hunt the open "
        "country under them. Bring them down where you can reach them, because they don't like to land.",
        "My bats'll fly the western road again. They're nervous animals and so am I, but we'll manage.\n\nThe "
        "gargoyles never used to come out this far. Something in that city's waking up.",
        [("shoulder", "armor", "leather", "wildheart"), ("wrist", "armor", "mail", "hunter_precise"),
         ("off_hand", "weapon", "tome", "precise_caster")]))

    # ---- in from Felwood: Yuki writes back
    A(Q("plw_what_grew_in_the_jar", "What Grew in the Jar", YUKI, 54, 55, "Botanist's",
        "Yuki Hashimoto catalogues everything that grows back in Felwood, and she's had a jar of spores from the "
        "Fungal Vale on her bench for a week. They've grown, and they've grown into something she's never seen.\n\n"
        "She wants Dr. Sun Li to see what her spores turn into.",
        [deliver("pl_q_yukis_jar", "Bring Yuki's jar to Dr. Sun Li at Crown Guard")],
        "Dr. Sun Li's at Crown Guard, in the east of the Eastern Plaguelands. It's a long way, so wrap the jar in "
        "something and keep it upright. It's started tapping on the glass, and I'd rather it didn't get out.",
        "Oh, that's beautiful, and I hate it.\n\nI studied fungi in Kunming for twenty years, back home, and nothing "
        "ever moved on its own. Tell Yuki I owe her a very long letter, and come back when you've rested. The vale's worse than I "
        "thought.",
        [("waist", "armor", "leather", "nature"), ("head", "armor", "plate", "shield_tank"),
         ("neck", "armor", None, "haste_caster")], zone="emerald_sanctuary", turn_in_npc_id=SUNLI,
        grant_items=carry("pl_q_yukis_jar", "Yuki's Jar", "A sealed specimen jar wrapped in a scarf. Something "
                          "pale inside it presses against the glass, and taps.")))
    return out
