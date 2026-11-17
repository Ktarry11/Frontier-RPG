"""
South Western Plaguelands' quests, levels 51-54. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT SOUTH WPL IS ABOUT (docs/plaguelands_design.md). The Plaguelands as players remember them, with the Integration's
small adjustments: the Scourge works its cauldrons on Lordaeron's farms and holds Andorhal, the Cult of the Damned
tends the plague, and the Scarlet Crusade pushes patrols down from Hearthglen. Two hubs, and they don't like each
other much, and since 16 Nov 2026 they share one town: the Bulwark, the Forsaken's wall on the Tirisfal border, its
own map, with the Order of the Pale Flame camped inside it (they came down from Sorrow Hill, which is graves again;
docs/plaguelands_towns_plan.md). Before that the Order kept
keep beside Uther's Tomb, led by Earth transplants who walked out of the Crusade.

  THE BULWARK (17)   High Executor Marla Venn (the line, Andorhal, a dispatch to Sorrow Hill), Apothecary Dorian
                     Vesk (the cauldron chain, which ends at Sun Rock in Stonetalon), Deathstalker Ilsa Rook (the
                     Cult's couriers and a report for the Undercity), Deathguard Captain Ludo Vance (the farms' named
                     horrors), Surgeon Halbert Grey (snapjaw shell and Old Darrowjaw).
  THE ORDER (22)      Flamekeeper Rory Callahan (the Order's rule, the Scarlet patrols, Hearthglen's orders, Caer
                     Darrow), Drillmaster Kofi Mensah (Andorhal's dead), Chaplain Odile Marchand (Uther's rest, the
                     Haunt, the drowned of the lake), Innkeeper Priya Raman (the kitchen, and letters home by way of
                     Sun Rock), Roostkeeper Anders Holm (the sky and the hawks), Scout Agata Wrobel (eyes on
                     Andorhal), Ser Aldren Holt (his old company).
  OUT                Sun Rock in Stonetalon (Vesk's samples to Merrow Vane, Priya's letters to Dr. Lindqvist), the
                     Undercity (Rook's report to Deathstalker Rhyne), the Pale Watch in North WPL (the Crusade's orders).
  IN                 Undercity (Marwen's reagents to Vesk), Brill (Wexley's notice to Kofi), Tarren Mill (Blackwood's
                     letter to Odile): the way into the Plaguelands from the Forsaken's own country.
  CAVE               The Writhing Deep, under the Haunt (Agata: the burrows, then the Broodlord and the Silken Bride).

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and only
the people at the top know more. Inside the Order people talk about home freely (Kyle: "Loud in the Order"). The
Forsaken at the Bulwark call the Order's people newcomers. Marla Venn commands the wall and knows more than she says.

THE ORDER'S RULE: they kill the mindless dead and leave the thinking ones alone, so the Order's quests send you after
the Scourge's shamblers and the Crusade's fanatics, never a Forsaken.

WHO PAYS. The Forsaken pay for the Forsaken's quests and the Order for the Order's, except Venn's dispatch, which Rory hands in.
The Forsaken own more quests than anyone, and by the time a player reaches the Plaguelands they're most of the way
to Exalted with them (tools/qa_factions.py wants the last tiers to take at least the last 40% of a faction's
quests). So the Bulwark is kept small and the Plaguelands' own quests go to the Order and the Argent Dawn.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.plaguelands_quest_voice import VOICE

WS = "western_plaguelands_south"
WN = "western_plaguelands_north"
SR, UC = "sun_rock_retreat", "undercity"
WD = "the_writhing_deep"

# ---- the people
VENN, VESK, ROOK = "wpl_bulwark_commander", "wpl_bulwark_apothecary", "wpl_bulwark_sewer_agent"
VANCE, GREY = "wpl_bulwark_captain", "wpl_bulwark_surgeon"
RORY, KOFI, ODILE, PRIYA, ANDERS = ("wpl_pf_flamekeeper", "wpl_pf_drillmaster", "wpl_pf_chaplain", "wpl_pf_innkeeper",
                                    "wpl_pf_bat_keeper")
AGATA, ALDREN = "wpl_pf_scout", "wpl_pf_knight"
#: in from outside: Undercity's apothecary, Brill's crier, Tarren Mill's chaplain (all born here)
MARWEN, WEXLEY, EWEN = "uc_apothecary", "brill_town_crier", "tarren_mill_chaplain"
MERROW, HANNAH, RHYNE, LENA = ("sr_forsaken_apothecary", "sr_transplant_geologist", "uc_deathstalker",
                               "wpln_pf_watch_captain")

BULWARK = {VENN, VESK, ROOK, VANCE, GREY}
SORROW = {RORY, KOFI, ODILE, PRIYA, ANDERS, AGATA, ALDREN}
HUB_GIVERS = BULWARK | SORROW
#: who pays: the Forsaken pay for theirs, the Order for its own (the zone's own faction)
FACTION_BY_GIVER = {g: "the_forsaken" for g in BULWARK}
#: a quest that pays someone other than its giver's faction: Venn's dispatch is handed in to Rory, and the Order pays
FACTION_BY_QUEST = {"pls_a_dispatch_for_sorrow_hill": "pale_flame",
                    "pls_samples_for_the_bulwark": "the_forsaken"}     # handed in at the Bulwark
NATIVE_GIVERS = {MARWEN, WEXLEY, EWEN}


def k(target, n, zone=WS):
    return kill(target, n, zone=zone)


def boss(target, zone=WS):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=WS, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Felstone Cauldron Lord": [("pl_q_felstone_sample", "Felstone Cauldron Sample", "A stoppered flask of green "
                                "slurry from the Felstone cauldron. The glass is warm.", 1.0)],
    "Cauldron Necrolyte": [("pl_q_dalson_sample", "Dalson's Cauldron Sample", "A flask of the Dalson cauldron's brew. "
                            "It's thicker than the Felstone sample and smells of wet hay.")],
    "Haunt Cult Tender": [("pl_q_haunt_sample", "Writhing Haunt Sample", "A flask from the Writhing Haunt's cauldron. "
                           "Something small moves in it when you aren't looking."),
                          ("pl_q_cult_letter", "Cult Courier's Letter", "A letter in the Cult's cipher, folded small "
                           "enough to hide in a boot.")],
    "Andorhal Necromancer": [("pl_q_necro_focus", "Necromantic Focus", "A bone rod wound with black wire. It hums "
                              "against your palm.")],
    "Plague-Ridden Wolf": [("pl_q_clean_sinew", "Clean Wolf Sinew", "Sinew from a plagued wolf, cut from the parts "
                            "the plague hadn't reached yet. There weren't many.")],
    "Darrowmere Snapjaw": [("pl_q_snapjaw_plate", "Snapjaw Shell Plate", "A plate of turtle shell from Darrowmere, "
                            "hard as iron and nearly as heavy.")],
    "Scarlet Field Chaplain": [("pl_q_patrol_orders", "Scarlet Patrol Orders", "Orders in a clerk's hand, sealed with "
                                "the Crusade's flame and signed in Hearthglen.", 1.0)],
    "Andorhal Skeleton": [("pl_q_andorhal_blade", "Rusted Andorhal Blade", "A Lordaeron infantry sword, rusted but "
                           "sound. Good steel underneath."),
                          ("pl_q_company_ring", "Andorhal Company Ring", "A plain iron ring stamped with the mark of "
                           "a Lordaeron infantry company.")],
    "Andorhal Abomination": [("pl_q_stitching", "Abomination Stitching", "A length of the thick black thread that "
                              "holds an abomination together. It's tougher than wire.")],
    "Diseased Black Bear": [("pl_q_bear_flank", "Plague-Free Bear Flank", "A cut of bear from the back of the leg, "
                             "where the sickness hadn't reached. Priya says it's safe. Mostly.")],
    "Scarlet Outrider": [("pl_q_survey_map", "Andorhal Survey Map", "A Crusade surveyor's map of Andorhal, with the "
                          "Scourge's strong points marked in red and the Forsaken's in black.", 1.0)],
}

STARTER_DROPS = {}
STARTER_IDS = {}


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=WS, **engine):
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

    # ======================================================================================== THE BULWARK
    # ---- High Executor Marla Venn
    A(Q("pls_the_line_holds", "The Line Holds", VENN, 51, 52, "Bulwark",
        None,
        [k("Wandering Skeleton", 10), k("Plague-Ridden Wolf", 8)],
        None,
        None,
        [("chest", "armor", "plate", "tank"), ("legs", "armor", "cloth", "caster"),
         ("hands", "armor", "leather", "agility")], giver_zone=True, nxt="pls_andorhals_gate"))
    A(Q("pls_andorhals_gate", "Andorhal's Gate", VENN, 52, 52, "Bulwark",
        None,
        [k("Andorhal Skeleton", 10), k("Andorhal Skeletal Archer", 6)],
        None,
        None,
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], nxt="pls_the_necromancers"))
    A(Q("pls_the_necromancers", "The Necromancers of Andorhal", VENN, 53, 53, "Bulwark",
        None,
        [k("Andorhal Necromancer", 8), fetch("pl_q_necro_focus", 5)],
        None,
        None,
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="pls_the_magistrate"))
    A(Q("pls_the_magistrate", "The Magistrate", VENN, 54, 54, "Bulwark",
        None,
        [boss("Magistrate Andor"), k("Andorhal Abomination", 6)],
        None,
        None,
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")]))
    A(Q("pls_a_dispatch_for_sorrow_hill", "A Dispatch for the Flamekeeper", VENN, 51, 51, "Bulwark",
        None,
        [deliver("pl_q_venn_dispatch", "Bring Venn's dispatch to Flamekeeper Rory Callahan across the street")],
        None,
        None,
        [("waist", "armor", "mail", "tide_healer"), ("back", "armor", None, "physical"),
         ("feet", "armor", "cloth", "spirit_caster")], turn_in_npc_id=RORY,
        grant_items=carry("pl_q_venn_dispatch", "Venn's Dispatch", "A dispatch sealed with the Bulwark's black wax.")))

    # ---- Apothecary Dorian Vesk (the cauldrons)
    A(Q("pls_felstone_field", "Felstone Field", VESK, 51, 52, "Vesk's",
        None,
        [k("Felstone Ghoul", 8), k("Felstone Cultist", 6)],
        None,
        None,
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")], nxt="pls_a_sample_from_felstone"))
    A(Q("pls_a_sample_from_felstone", "A Sample from Felstone", VESK, 52, 52, "Vesk's",
        None,
        [k("Felstone Cauldron Lord", 1), fetch("pl_q_felstone_sample", 1)],
        None,
        None,
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="pls_dalsons_tears"))
    A(Q("pls_dalsons_tears", "Dalson's Tears", VESK, 52, 53, "Vesk's",
        None,
        [fetch("pl_q_dalson_sample", 1), k("Dalson's Ghoul", 8)],
        None,
        None,
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="pls_the_writhing_haunt"))
    A(Q("pls_the_writhing_haunt", "The Writhing Haunt", VESK, 53, 53, "Vesk's",
        None,
        [k("Haunt Cult Tender", 8), fetch("pl_q_haunt_sample", 1)],
        None,
        None,
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")], nxt="pls_what_the_plague_is_made_of"))
    A(Q("pls_what_the_plague_is_made_of", "What the Plague Is Made Of", VESK, 53, 54, "Vesk's",
        None,
        [deliver("pl_q_sample_case", "Bring the sample case to Apothecary Merrow Vane at Sun Rock Retreat")],
        None,
        None,
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "crusader"),
         ("ranged", "weapon", "gun", "hunter_crit")], turn_in_npc_id=MERROW,
        grant_items=carry("pl_q_sample_case", "Vesk's Sample Case", "A padded case with three labelled flasks. One of "
                                                                   "them knocks against the side now and then.")))

    # ---- Deathstalker Ilsa Rook
    A(Q("pls_cult_couriers", "Cult Couriers", ROOK, 52, 53, "Cipherbreaker's",
        None,
        [fetch("pl_q_cult_letter", 4)],
        None,
        None,
        [("legs", "armor", "leather", "assassin"), ("hands", "armor", "mail", "tide_healer"),
         ("main_hand", "weapon", "sword_1h", "caster")], nxt="pls_a_report_for_the_undercity"))
    A(Q("pls_a_report_for_the_undercity", "A Report for the Undercity", ROOK, 53, 53, "Cipherbreaker's",
        None,
        [deliver("pl_q_rook_report", "Bring Rook's report to Deathstalker Rhyne in the Undercity")],
        None,
        None,
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")], zone=WS, turn_in_npc_id=RHYNE,
        grant_items=carry("pl_q_rook_report", "Rook's Report", "A thin report sealed twice, once with wax and once "
                                                               "with something that smells like poison.")))
    A(Q("pls_the_mother_of_the_haunt", "The Mother of the Haunt", ROOK, 53, 54, "Cipherbreaker's",
        None,
        [boss("Mother of the Haunt"), k("Haunt Banshee", 8)],
        None,
        None,
        [("head", "armor", "mail", "hunter_precise"), ("chest", "armor", "plate", "tank"),
         ("off_hand", "weapon", "tome", "caster")]))

    # ---- Deathguard Captain Ludo Vance
    A(Q("pls_farmer_felstone", "Farmer Felstone", VANCE, 51, 52, "Fieldwatch",
        None,
        [boss("Farmer Felstone"), k("Felstone Ghoul", 6)],
        None,
        None,
        [("main_hand", "weapon", "polearm", "strength"), ("head", "armor", "cloth", "high_healer"),
         ("hands", "armor", "leather", "hunter")], nxt="pls_the_ghost_in_the_barn"))
    A(Q("pls_the_ghost_in_the_barn", "The Ghost in the Barn", VANCE, 53, 53, "Fieldwatch",
        None,
        [boss("The Dalson Ghost"), k("Dalson's Skeleton", 8)],
        None,
        None,
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")]))

    # ---- Surgeon Halbert Grey
    A(Q("pls_snapjaw_shell", "Snapjaw Shell", GREY, 52, 52, "Stitchwork",
        None,
        [fetch("pl_q_snapjaw_plate", 6)],
        None,
        None,
        [("legs", "armor", "mail", "tide_healer"), ("head", "armor", "plate", "strength"),
         ("ranged", "weapon", "wand", "caster")], nxt="pls_old_darrowjaw"))
    A(Q("pls_old_darrowjaw", "Old Darrowjaw", GREY, 53, 54, "Stitchwork",
        None,
        [boss("Old Darrowjaw"), k("Darrowmere Snapjaw", 6)],
        None,
        None,
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")]))

    # ======================================================================================== SORROW HILL
    # ---- Flamekeeper Rory Callahan
    A(Q("pls_what_we_kill", "What We Kill", RORY, 51, 52, "Flamekeeper's",
        None,
        [k("Scarlet Outrider", 8), k("Scarlet Field Chaplain", 6)],
        None,
        None,
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="pls_red_on_the_road"))
    A(Q("pls_red_on_the_road", "Red on the Road", RORY, 52, 52, "Flamekeeper's",
        None,
        [fetch("pl_q_patrol_orders", 1)],
        None,
        None,
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="pls_hearthglens_road"))
    A(Q("pls_hearthglens_road", "Hearthglen's Road", RORY, 52, 53, "Flamekeeper's",
        None,
        [deliver("pl_q_orders_for_lena", "Bring the Crusade's orders to Watch Captain Lena Fischer at the Pale Watch")],
        None,
        None,
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")], turn_in_npc_id=LENA,
        grant_items=carry("pl_q_orders_for_lena", "Hale's Orders", "The Crusade's orders from Hearthglen, still "
                                                                   "sealed, wrapped in oilcloth by Rory.")))
    A(Q("pls_the_groundskeeper", "The Groundskeeper", RORY, 54, 54, "Flamekeeper's",
        None,
        [boss("The Groundskeeper"), k("Caer Darrow Ghoul", 8)],
        None,
        None,
        [("chest", "armor", "plate", "strength"), ("waist", "armor", "cloth", "high_healer"),
         ("ranged", "weapon", "bow", "hunter")]))

    # ---- Drillmaster Kofi Mensah
    A(Q("pls_steel_for_sorrow_hill", "Steel for the Order", KOFI, 51, 52, "Drillyard",
        None,
        [fetch("pl_q_andorhal_blade", 8)],
        None,
        None,
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], nxt="pls_archers_on_the_wall"))
    A(Q("pls_archers_on_the_wall", "Archers on the Wall", KOFI, 52, 52, "Drillyard",
        None,
        [k("Andorhal Skeletal Archer", 8)],
        None,
        None,
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")], nxt="pls_the_abominations"))
    A(Q("pls_the_abominations", "The Abominations", KOFI, 53, 53, "Drillyard",
        None,
        [k("Andorhal Abomination", 6), fetch("pl_q_stitching", 5)],
        None,
        None,
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))
    A(Q("pls_shades_of_caer_darrow", "Shades of Caer Darrow", KOFI, 53, 54, "Drillyard",
        None,
        [k("Caer Darrow Shade", 8)],
        None,
        None,
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("ring", "armor", None, "hunter_crit")]))

    # ---- Chaplain Odile Marchand
    A(Q("pls_uthers_rest", "Uther's Rest", ODILE, 51, 51, "Tombwatch",
        None,
        [explore(115, 143, "Visit Uther's Tomb")],
        None,
        None,
        [("ring", "armor", None, "spirit_caster"), ("feet", "armor", "mail", "hunter_precise"),
         ("wrist", "armor", "plate", "plate_healer")], nxt="pls_laid_to_rest"))
    A(Q("pls_laid_to_rest", "Laid to Rest", ODILE, 52, 52, "Tombwatch",
        None,
        [k("Dalson's Ghoul", 8), k("Dalson's Skeleton", 6)],
        None,
        None,
        [("chest", "armor", "cloth", "caster"), ("legs", "armor", "plate", "strength"),
         ("hands", "armor", "leather", "wildheart")], nxt="pls_the_haunts_banshees"))
    A(Q("pls_the_haunts_banshees", "The Haunt's Banshees", ODILE, 53, 53, "Tombwatch",
        None,
        [k("Haunt Banshee", 8), k("Writhing Crypt Fiend", 6)],
        None,
        None,
        [("shoulder", "armor", "mail", "earthen"), ("head", "armor", "cloth", "caster_crit"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    A(Q("pls_darrowmeres_drowned", "Darrowmere's Drowned", ODILE, 53, 53, "Tombwatch",
        None,
        [k("Drowned Lakewalker", 10)],
        None,
        None,
        [("shoulder", "armor", "leather", "bruiser"), ("feet", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_1h", "wildheart")]))

    # ---- Innkeeper Priya Raman
    A(Q("pls_bear_stew", "Bear Stew", PRIYA, 51, 52, "Sorrow Hill",
        None,
        [fetch("pl_q_bear_flank", 6)],
        None,
        None,
        [("legs", "armor", "leather", "agility"), ("chest", "armor", "mail", "tide_healer"),
         ("feet", "armor", "plate", "tank")], nxt="pls_letters_home"))
    A(Q("pls_letters_home", "Letters Home", PRIYA, 52, 53, "Sorrow Hill",
        None,
        [deliver("pl_q_letter_bundle", "Bring the bundle of letters to Dr. Hannah Lindqvist at Sun Rock Retreat")],
        None,
        None,
        [("neck", "armor", None, "spirit_caster"), ("hands", "armor", "leather", "healer"),
         ("main_hand", "weapon", "polearm", "agility")], turn_in_npc_id=HANNAH,
        grant_items=carry("pl_q_letter_bundle", "Bundle of Letters", "A thick bundle of letters tied with kitchen "
                                                                     "string, addressed to people nobody has seen in "
                                                                     "three years.")))

    # ---- Roostkeeper Anders Holm
    A(Q("pls_clear_skies", "Clear Skies", ANDERS, 51, 52, "Roostkeeper's",
        None,
        [k("Plaguewing Vulture", 10)],
        None,
        None,
        [("shoulder", "armor", "leather", "hunter_crit"), ("waist", "armor", "plate", "tank"),
         ("back", "armor", None, "caster")], nxt="pls_jesses_for_the_hawks"))

    A(Q("pls_jesses_for_the_hawks", "Jesses for the Hawks", ANDERS, 52, 52, "Roostkeeper's",
        None,
        [fetch("pl_q_clean_sinew", 8)],
        None,
        None,
        [("hands", "armor", "plate", "tank"), ("chest", "armor", "cloth", "spirit_caster"),
         ("waist", "armor", "leather", "agility")]))

    # ---- Scout Agata Wrobel
    A(Q("pls_eyes_on_andorhal", "Eyes on Andorhal", AGATA, 52, 52, "Pathfinder's",
        None,
        [explore(57, 117, "Look over the middle of Andorhal")],
        None,
        None,
        [("feet", "armor", "leather", "assassin"), ("head", "armor", "plate", "crusader"),
         ("wrist", "armor", "cloth", "healer")], nxt="pls_the_survey_map"))
    A(Q("pls_the_survey_map", "The Survey Map", AGATA, 52, 53, "Pathfinder's",
        None,
        [fetch("pl_q_survey_map", 1)],
        None,
        None,
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "strength")]))

    # ---- Ser Aldren Holt
    A(Q("pls_the_fallen_of_andorhal", "The Fallen of Andorhal", ALDREN, 52, 53, "Holt's",
        None,
        [fetch("pl_q_company_ring", 6)],
        None,
        None,
        [("hands", "armor", "plate", "strength_crit"), ("shoulder", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "high_healer")], nxt="pls_the_necrolytes"))
    A(Q("pls_the_necrolytes", "The Necrolytes", ALDREN, 53, 53, "Holt's",
        None,
        [k("Cauldron Necrolyte", 8)],
        None,
        None,
        [("legs", "armor", "mail", "earthen"), ("waist", "armor", "leather", "feral"),
         ("main_hand", "weapon", "axe_2h", "strength")]))

    # ---- the Writhing Deep, the cave under the Writhing Haunt (tools/handbuilt_plaguelands_caves.py)
    A(Q("pls_under_the_haunt", "Under the Haunt", AGATA, 53, 54, "Scout's",
        None,
        [k("Writhing Burrower", 10, WD), k("Brood Guardian", 6, WD)],
        None,
        None,
        [("legs", "armor", "leather", "feral"), ("hands", "armor", "cloth", "shadow"),
         ("waist", "armor", "plate", "strength")], nxt="pls_the_broodlord"))
    A(Q("pls_the_broodlord", "The Broodlord", AGATA, 54, 55, "Scout's",
        None,
        [boss("Broodlord Szarak", WD), boss("The Silken Bride", WD)],
        None,
        None,
        [("chest", "armor", "mail", "hunter_crit"), ("head", "armor", "leather", "healer"),
         ("main_hand", "weapon", "staff", "fire")]))

    # ---- in from outside the Plaguelands: Undercity, Brill and Tarren Mill
    A(Q("pls_samples_for_the_bulwark", "Samples for the Bulwark", MARWEN, 51, 52, "Apothecary's",
        None,
        [deliver("pl_q_marwens_case", "Bring Marwen's reagent case to Apothecary Dorian Vesk at the Bulwark")],
        None,
        None,
        [("wrist", "armor", "cloth", "caster"), ("feet", "armor", "leather", "agility"),
         ("back", "armor", None, "tank_any")], zone=UC, turn_in_npc_id=VESK,
        grant_items=carry("pl_q_marwens_case", "Marwen's Reagent Case", "A small locked case of glass vials packed "
                          "in straw, every one labelled in a precise hand.")))
    A(Q("pls_hands_for_sorrow_hill", "Hands for the Order", WEXLEY, 51, 52, "Crier's",
        None,
        [deliver("pl_q_order_notice", "Bring the Order's notice to Drillmaster Kofi Mensah at the Bulwark")],
        None,
        None,
        [("shoulder", "armor", "plate", "tank"), ("hands", "armor", "mail", "earthen"),
         ("ring", "armor", None, "spirit_caster")], zone="brill", turn_in_npc_id=KOFI,
        grant_items=carry("pl_q_order_notice", "The Order's Notice", "A notice in a firm hand under a pale flame: "
                          "fighters wanted at the Bulwark, no questions asked about where you were born.")))
    A(Q("pls_a_chaplains_letter", "A Chaplain's Letter", EWEN, 51, 52, "Chaplain's",
        None,
        [deliver("pl_q_blackwoods_letter", "Bring Chaplain Blackwood's letter to Chaplain Odile Marchand at Uther's "
                 "Tomb")],
        None,
        None,
        [("neck", "armor", None, "holy"), ("legs", "armor", "mail", "tide_healer"),
         ("off_hand", "weapon", "shield", "shield_tank")], zone="tarren_mill", turn_in_npc_id=ODILE,
        grant_items=carry("pl_q_blackwoods_letter", "Chaplain Blackwood's Letter", "A letter sealed with plain "
                          "candle wax, addressed in careful capitals to the chaplain at Uther's Tomb.")))
    return out
