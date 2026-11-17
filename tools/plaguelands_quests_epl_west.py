"""
West Eastern Plaguelands' quests, levels 55-58. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT WEST EPL IS ABOUT (docs/plaguelands_design.md). The road from the river to Stratholme, and the worst of the
Plaguelands. Plaguewood and Terrordale are the Scourge's own country, the Cult runs its plague carts through Corin's
Crossing, the Marris family still works their farm long after they died, something fungal is growing in the vale,
and the dead knights at Stratholme's gates let nobody near the city.

There's no camp on this map, so its quests are given next door at Light's Hope Chapel (Crown Guard's people moved in
there on 16 Nov 2026), which
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
  ALSO               Gwen Pike (Crown Guard's bat handler, at Light's Hope now) on the gargoyles over Stratholme's gates.

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and only
the people at the top know more. Bram, Edda, Osric, Greta, Roland and Dawnbringer were born here and say newcomers.
Sun Li and Kaia are transplants and talk about home.

WHO PAYS. Everything here pays the Argent Dawn, the zone's own faction.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.plaguelands_quest_voice import VOICE

EW = "eastern_plaguelands_west"
MC = "the_marris_crypt"

# ---- the people
BRAM, EDDA, SUNLI, OSRIC, GRETA = ("epl_cg_outrider", "epl_cg_widow", "epl_cg_mycologist", "epl_cg_gravewarden",
                                   "epl_cg_innkeeper")
ROLAND, KAIA, DAWN = "epl_lh_knight", "epl_lh_huntress", "epl_lh_commander"
JESSA = "epl_lh_innkeeper"
TOHANA, YUKI = "sr_spirit_walker", "es_volunteer_botanist"
GWEN = "epl_cg_flight"

HUB_GIVERS = {BRAM, EDDA, SUNLI, OSRIC, GRETA, ROLAND, KAIA, DAWN, GWEN, JESSA}
NATIVE_GIVERS = {BRAM, EDDA, OSRIC, GRETA, ROLAND, DAWN, GWEN, JESSA}
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
    # the words are the giver's own, in tools/plaguelands_quest_voice.py (Kyle, 16 Nov 2026: the Plaguelands' quests
    # read "as total disconnected third character"; Emerald Sanctuary is the model). Every quest has an entry there.
    v = VOICE[qid]
    desc, accept, done, title = v["desc"], v["accept"], v["done"], v["title"] or title
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
        None,
        [k("Plague Hound", 8), k("Frenzied Ghoul", 8)],
        None,
        None,
        [("chest", "armor", "plate", "tank"), ("legs", "armor", "cloth", "caster"),
         ("hands", "armor", "leather", "agility")], nxt="plw_corins_crossing"))
    A(Q("plw_corins_crossing", "Corin's Crossing", BRAM, 56, 56, "Outrider's",
        None,
        [k("Cult Plaguebringer", 8), k("Cult Cart Driver", 6)],
        None,
        None,
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], nxt="plw_the_manifest"))
    A(Q("plw_the_manifest", "The Manifest", BRAM, 56, 56, "Outrider's",
        None,
        [fetch("pl_q_cart_manifest", 1)],
        None,
        None,
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="plw_the_crossings_abominations"))
    A(Q("plw_the_crossings_abominations", "The Crossing's Abominations", BRAM, 57, 57, "Outrider's",
        None,
        [k("Crossing Abomination", 5)],
        None,
        None,
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")], nxt="plw_cartmaster_corin"))
    A(Q("plw_cartmaster_corin", "Cartmaster Corin", BRAM, 57, 57, "Outrider's",
        None,
        [boss("Cartmaster Corin")],
        None,
        None,
        [("head", "armor", "mail", "hunter_precise"), ("waist", "armor", "plate", "crusader"),
         ("back", "armor", None, "physical")]))

    # ---- Edda Marris
    A(Q("plw_the_marris_stead", "The Marris Stead", EDDA, 55, 56, "Marris",
        None,
        [k("Marris Farmhand", 8), k("Stead Crow", 6)],
        None,
        None,
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="plw_the_marris_locket"))
    A(Q("plw_the_marris_locket", "The Marris Locket", EDDA, 56, 56, "Marris",
        None,
        [fetch("pl_q_marris_locket", 1)],
        None,
        None,
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="plw_old_marris"))
    A(Q("plw_old_marris", "Old Marris", EDDA, 56, 56, "Marris",
        None,
        [boss("Old Marris")],
        None,
        None,
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")]))

    # ---- Dr. Sun Li
    A(Q("plw_the_fungal_vale", "The Fungal Vale", SUNLI, 56, 56, "Mycologist's",
        None,
        [k("Vale Plague Slime", 8), k("Spore-Walker", 6)],
        None,
        None,
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")], nxt="plw_spore_caps"))
    A(Q("plw_spore_caps", "Spore Caps", SUNLI, 56, 57, "Mycologist's",
        None,
        [fetch("pl_q_spore_cap", 5)],
        None,
        None,
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "crusader"),
         ("ranged", "weapon", "gun", "hunter_crit")], nxt="plw_the_fungal_mass"))
    A(Q("plw_the_fungal_mass", "The Fungal Mass", SUNLI, 57, 57, "Mycologist's",
        None,
        [boss("The Fungal Mass")],
        None,
        None,
        [("legs", "armor", "leather", "assassin"), ("hands", "armor", "mail", "tide_healer"),
         ("main_hand", "weapon", "sword_1h", "caster")]))
    A(Q("plw_spores_for_the_sanctuary", "Spores for the Sanctuary", SUNLI, 57, 57, "Mycologist's",
        None,
        [deliver("pl_q_spore_sample", "Bring Sun Li's spore sample to Yuki Hashimoto at the Emerald Sanctuary")],
        None,
        None,
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")], turn_in_npc_id=YUKI,
        grant_items=carry("pl_q_spore_sample", "Sealed Spore Sample", "A glass jar sealed in red wax, with something "
                                                                      "grey and soft growing on the inside of the "
                                                                      "glass.")))

    # ---- Gravewarden Osric Vey
    A(Q("plw_terrordale", "Terrordale", OSRIC, 56, 57, "Gravewarden's",
        None,
        [k("Terrordale Ghoul", 8), k("Terrordale Spirit", 6)],
        None,
        None,
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")], nxt="plw_the_skeletal_mages"))
    A(Q("plw_the_skeletal_mages", "The Skeletal Mages", OSRIC, 57, 57, "Gravewarden's",
        None,
        [k("Terrordale Skeletal Mage", 8)],
        None,
        None,
        [("shoulder", "armor", "leather", "bruiser"), ("feet", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_1h", "wildheart")], nxt="plw_the_terror_of_the_dale"))
    A(Q("plw_the_terror_of_the_dale", "The Terror of the Dale", OSRIC, 57, 57, "Gravewarden's",
        None,
        [boss("The Terror of the Dale")],
        None,
        None,
        [("hands", "armor", "plate", "tank"), ("chest", "armor", "cloth", "spirit_caster"),
         ("waist", "armor", "leather", "agility")], nxt="plw_word_for_sun_rock"))
    A(Q("plw_word_for_sun_rock", "Word for Sun Rock", OSRIC, 57, 57, "Gravewarden's",
        None,
        [deliver("pl_q_osric_account", "Bring Osric's account of Terrordale to Spiritwalker Tohana at Sun Rock")],
        None,
        None,
        [("legs", "armor", "mail", "tide_healer"), ("head", "armor", "plate", "strength"),
         ("ranged", "weapon", "wand", "caster")], turn_in_npc_id=TOHANA,
        grant_items=carry("pl_q_osric_account", "Osric's Account", "A long letter in a gravewarden's careful hand, "
                                                                   "sealed with the Dawn's sunburst.")))

    # ---- Innkeeper Greta Lowe
    A(Q("plw_crow_pie", "Crow Pie", GRETA, 55, 56, "Hearthside",
        None,
        [fetch("pl_q_crow", 6)],
        None,
        None,
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")]))

    # ======================================================================================== LIGHT'S HOPE
    # ---- Ser Roland Ashcombe
    A(Q("plw_gargoyles_over_the_road", "Gargoyles over the Road", ROLAND, 56, 57, "Ashcombe's",
        None,
        [k("Stone-Winged Gargoyle", 8)],
        None,
        None,
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="plw_the_gates_of_stratholme"))
    A(Q("plw_the_gates_of_stratholme", "The Gates of Stratholme", ROLAND, 57, 58, "Ashcombe's",
        None,
        [k("Gate Death Knight", 6), k("Gate Gargoyle", 6)],
        None,
        None,
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="plw_gatekeeper_vorthas"))
    A(Q("plw_gatekeeper_vorthas", "Gatekeeper Vorthas", ROLAND, 58, 58, "Ashcombe's",
        None,
        [boss("Gatekeeper Vorthas")],
        None,
        None,
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")]))

    A(Q("plw_sigils_of_the_fallen", "Sigils of the Fallen", ROLAND, 57, 58, "Ashcombe's",
        None,
        [fetch("pl_q_knight_sigil", 5)],
        None,
        None,
        [("chest", "armor", "mail", "hunter_precise"), ("feet", "armor", "plate", "tank_any"),
         ("ring", "armor", None, "caster")]))

    # ---- Huntress Kaia Lindgren
    A(Q("plw_plaguewood", "Plaguewood", KAIA, 56, 57, "Huntress's",
        None,
        [k("Plaguewood Spider", 8), k("Plaguewood Crypt Fiend", 5)],
        None,
        None,
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], nxt="plw_plaguewood_silk"))
    A(Q("plw_plaguewood_silk", "Plaguewood Silk", KAIA, 57, 57, "Huntress's",
        None,
        [fetch("pl_q_spider_silk", 6)],
        None,
        None,
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")], nxt="plw_the_plaguewood_matriarch"))
    A(Q("plw_the_plaguewood_matriarch", "The Plaguewood Matriarch", KAIA, 58, 58, "Huntress's",
        None,
        [boss("The Plaguewood Matriarch")],
        None,
        None,
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))
    A(Q("plw_carrion_grubs", "Carrion Grubs", KAIA, 55, 56, "Huntress's",
        None,
        [k("Carrion Grub", 10)],
        None,
        None,
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    A(Q("plw_hound_fangs", "Hound Fangs", KAIA, 55, 56, "Huntress's",
        None,
        [fetch("pl_q_hound_fang", 6)],
        None,
        None,
        [("legs", "armor", "leather", "agility"), ("waist", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "assassin")]))

    # ---- Commander Eligor Dawnbringer
    A(Q("plw_a_look_at_stratholme", "A Look at Stratholme", DAWN, 57, 57, "Dawnbringer's",
        None,
        [explore(43, 10, "Look at Stratholme's gate")],
        None,
        None,
        [("waist", "armor", "mail", "tide_healer"), ("back", "armor", None, "physical"),
         ("feet", "armor", "cloth", "spirit_caster")]))

    # ---- the Marris Crypt, under the stead (tools/handbuilt_plaguelands_caves.py)
    A(Q("plw_the_family_crypt", "The Family Crypt", EDDA, 56, 57, "Widow's",
        None,
        [k("Crypt Shambler", 10, MC), k("Marris Ossuary Guard", 6, MC)],
        None,
        None,
        [("head", "armor", "mail", "storm"), ("legs", "armor", "cloth", "arcane"),
         ("hands", "armor", "plate", "bruiser")], nxt="plw_the_sexton"))
    A(Q("plw_the_sexton", "The Sexton", EDDA, 57, 58, "Widow's",
        None,
        [boss("Sexton Hollowell", MC), boss("The Bone Choir", MC)],
        None,
        None,
        [("chest", "armor", "plate", "crusader"), ("feet", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "polearm", "bear_weapon")]))

    # ---- Bat Handler Gwen Pike: the gargoyles over Stratholme's gates
    A(Q("plw_gargoyles_over_the_gates", "Gargoyles Over the Gates", GWEN, 57, 58, "Bat Handler's",
        None,
        [k("Gate Gargoyle", 8), k("Stone-Winged Gargoyle", 8)],
        None,
        None,
        [("shoulder", "armor", "leather", "wildheart"), ("wrist", "armor", "mail", "hunter_precise"),
         ("off_hand", "weapon", "tome", "precise_caster")]))

    # ---- in from Felwood: Yuki writes back
    A(Q("plw_what_grew_in_the_jar", "What Grew in the Jar", YUKI, 54, 55, "Botanist's",
        None,
        [deliver("pl_q_yukis_jar", "Bring Yuki's jar to Dr. Sun Li at Light's Hope Chapel")],
        None,
        None,
        [("waist", "armor", "leather", "nature"), ("head", "armor", "plate", "shield_tank"),
         ("neck", "armor", None, "haste_caster")], zone="emerald_sanctuary", turn_in_npc_id=SUNLI,
        grant_items=carry("pl_q_yukis_jar", "Yuki's Jar", "A sealed specimen jar wrapped in a scarf. Something "
                          "pale inside it presses against the glass, and taps.")))

    # ======================================================================================== STRATHOLME
    # Given at Light's Hope and Crown Guard (Kyle: dungeon quests are given in town).
    LV, D1, D2 = "stratholme", "stratholme:_service_entrance", "stratholme:_slaughter_square"
    A(Q("plw_the_grand_crusader", "The Grand Crusader", ROLAND, 58, 59, "Ashcombe's",
        None,
        [boss("Grand Crusader Dathrohan", LV)],
        None,
        None,
        [("main_hand", "weapon", "mace_1h", "high_healer"), ("legs", "armor", "mail", "hunter"),
         ("head", "armor", "leather", "agility")]))
    A(Q("plw_the_baron", "The Baron", JESSA, 59, 60, "Moonfield's",
        None,
        [boss("Baron Rivendare", D2)],
        None,
        None,
        [("main_hand", "weapon", "polearm", "strength"), ("waist", "armor", "plate", "tank_any"),
         ("hands", "armor", "cloth", "caster")]))
    A(Q("plw_the_three_ziggurats", "The Three Ziggurats", OSRIC, 58, 59, "Gravewarden's",
        None,
        [boss("Nerub'enkan", D1), boss("Baroness Anastari", D1), boss("Maleki the Pallid", D1)],
        None,
        None,
        [("shoulder", "armor", "cloth", "caster"), ("feet", "armor", "mail", "earthen"),
         ("ring", "armor", None, "physical")]))
    A(Q("plw_the_gorger", "The Gorger", SUNLI, 59, 60, "Mycologist's",
        None,
        [boss("Ramstein the Gorger", D2)],
        None,
        None,
        [("wrist", "armor", "leather", "healer"), ("back", "armor", None, "caster"),
         ("legs", "armor", "plate", "strength")]))
    return out
