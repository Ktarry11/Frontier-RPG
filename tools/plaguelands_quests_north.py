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
  OUT                 the Bulwark (Lena to Rory, Amalie to Odile), the Emerald Sanctuary in Felwood (Noah's serum to
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
from tools.plaguelands_quest_voice import VOICE

WN = "western_plaguelands_north"
WC = "the_weeping_cave"

# ---- the people
LENA, MATEO, NOAH = "wpln_pf_watch_captain", "wpln_pf_scout", "wpln_pf_field_medic"
AMALIE, JONAH, OONA, WENDEL = "wpln_pf_sister", "wpln_pf_woodwright", "wpln_pf_angler", "wpln_pf_clerk"
RORY, ODILE, NKECHI, NOVAK = "wpl_pf_flamekeeper", "wpl_pf_chaplain", "es_volunteer_medic", "brill_pf_flamewarden"

BEATRIZ, LIAM = "wpln_pf_innkeeper", "wpln_pf_roostkeeper"
HUB_GIVERS = {LENA, MATEO, NOAH, AMALIE, JONAH, OONA, WENDEL, BEATRIZ, LIAM}
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

    # ---- Watch Captain Lena Fischer
    A(Q("pln_the_gate_of_hearthglen", "The Gate of Hearthglen", LENA, 53, 53, "Pale Watch",
        None,
        [explore(100, 22, "Look at Hearthglen's gate")],
        None,
        None,
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], nxt="pln_sentries_on_the_road"))
    A(Q("pln_sentries_on_the_road", "Sentries on the Road", LENA, 54, 55, "Pale Watch",
        None,
        [k("Scarlet Sentry", 10)],
        None,
        None,
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="pln_crossbows_on_the_wall"))
    A(Q("pln_crossbows_on_the_wall", "Crossbows on the Wall", LENA, 55, 56, "Pale Watch",
        None,
        [k("Scarlet Crossbowman", 8)],
        None,
        None,
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")], nxt="pln_word_from_the_watch"))
    A(Q("pln_word_from_the_watch", "Word from the Watch", LENA, 55, 55, "Pale Watch",
        None,
        [deliver("pl_q_lena_report", "Bring Lena's report to Flamekeeper Rory Callahan at the Bulwark")],
        None,
        None,
        [("waist", "armor", "mail", "tide_healer"), ("back", "armor", None, "physical"),
         ("feet", "armor", "cloth", "spirit_caster")], turn_in_npc_id=RORY,
        grant_items=carry("pl_q_lena_report", "Lena's Report", "A thick report in a neat hand, with a sketch of "
                                                               "Hearthglen's gate on the back of the last page.")))

    A(Q("pln_a_letter_for_brill", "A Letter for Brill", LENA, 55, 56, "Pale Watch",
        None,
        [deliver("pl_q_letter_for_novak", "Bring Lena's letter to Flamewarden Teodor Novak in Brill")],
        None,
        None,
        [("chest", "armor", "leather", "bruiser"), ("feet", "armor", "mail", "tide_healer"),
         ("neck", "armor", None, "spirit_caster")], turn_in_npc_id=NOVAK,
        grant_items=carry("pl_q_letter_for_novak", "Lena's Letter", "A short letter sealed with the Pale Flame, "
                                                                     "addressed to Brill in a tidy hand.")))

    # ---- Scout Mateo Brandt
    A(Q("pln_worgs_on_the_road", "Worgs on the Road", MATEO, 53, 53, "Watchman's",
        None,
        [k("Rotting Worg", 10)],
        None,
        None,
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="pln_skeletal_wanderers"))
    A(Q("pln_skeletal_wanderers", "Skeletal Wanderers", MATEO, 53, 54, "Watchman's",
        None,
        [k("Skeletal Wanderer", 10)],
        None,
        None,
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="pln_down_to_the_river"))
    A(Q("pln_down_to_the_river", "Down to the River", MATEO, 54, 54, "Watchman's",
        None,
        [explore(160, 60, "Find a way down to the Thondroril's bank")],
        None,
        None,
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")]))
    A(Q("pln_the_blighted_herd", "The Blighted Herd", MATEO, 54, 54, "Watchman's",
        None,
        [k("Blighted Stag", 8)],
        None,
        None,
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")]))

    A(Q("pln_travellers_keepsakes", "Travellers' Keepsakes", MATEO, 54, 54, "Watchman's",
        None,
        [fetch("pl_q_keepsake", 6)],
        None,
        None,
        [("hands", "armor", "plate", "plate_healer"), ("shoulder", "armor", "leather", "hunter"),
         ("back", "armor", None, "caster")]))

    # ---- Field Medic Noah Kowal
    A(Q("pln_riverbank_ghouls", "Riverbank Ghouls", NOAH, 54, 55, "Medic's",
        None,
        [k("Riverbank Ghoul", 10)],
        None,
        None,
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "crusader"),
         ("ranged", "weapon", "gun", "hunter_crit")], nxt="pln_sludge_samples"))
    A(Q("pln_sludge_samples", "Sludge Samples", NOAH, 55, 55, "Medic's",
        None,
        [fetch("pl_q_sludge_sample", 5)],
        None,
        None,
        [("legs", "armor", "leather", "assassin"), ("hands", "armor", "mail", "tide_healer"),
         ("main_hand", "weapon", "sword_1h", "caster")], nxt="pln_the_withering"))
    A(Q("pln_the_withering", "The Withering", NOAH, 55, 55, "Medic's",
        None,
        [k("Withering Ghoul", 8), k("Withering Cultist", 6)],
        None,
        None,
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")], nxt="pln_gahrron_the_withered"))
    A(Q("pln_gahrron_the_withered", "Gahrron the Withered", NOAH, 56, 56, "Medic's",
        None,
        [boss("Gahrron the Withered")],
        None,
        None,
        [("head", "armor", "mail", "hunter_precise"), ("chest", "armor", "plate", "tank"),
         ("off_hand", "weapon", "tome", "caster")]))
    A(Q("pln_a_serum_for_felwood", "A Serum for Felwood", NOAH, 55, 56, "Medic's",
        None,
        [deliver("pl_q_serum_vial", "Bring Noah's serum to Dr. Nkechi Adeyemi at the Emerald Sanctuary")],
        None,
        None,
        [("legs", "armor", "mail", "earthen"), ("waist", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "high_healer")], turn_in_npc_id=NKECHI,
        grant_items=carry("pl_q_serum_vial", "Noah's Serum", "A small vial of pale green serum, wrapped in a "
                                                             "bandage and labelled in careful capitals.")))

    # ---- Sister Amalie Crane
    A(Q("pln_the_inquisitors", "The Inquisitors", AMALIE, 55, 56, "Sister's",
        None,
        [k("Hearthglen Inquisitor", 8)],
        None,
        None,
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")], nxt="pln_the_confessions"))
    A(Q("pln_the_confessions", "The Confessions", AMALIE, 55, 56, "Sister's",
        None,
        [fetch("pl_q_confession", 5)],
        None,
        None,
        [("shoulder", "armor", "leather", "bruiser"), ("feet", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_1h", "wildheart")], nxt="pln_the_book_of_names"))
    A(Q("pln_the_book_of_names", "The Book of Names", AMALIE, 56, 56, "Sister's",
        None,
        [deliver("pl_q_confession_bundle", "Bring the confessions to Chaplain Odile Marchand at the Bulwark")],
        None,
        None,
        [("hands", "armor", "plate", "tank"), ("chest", "armor", "cloth", "spirit_caster"),
         ("waist", "armor", "leather", "agility")], turn_in_npc_id=ODILE,
        grant_items=carry("pl_q_confession_bundle", "Bundle of Confessions", "The inquisitors' confessions, tied "
                                                                             "with a ribbon Amalie took from her own "
                                                                             "habit.")))
    A(Q("pln_high_inquisitor_faulk", "High Inquisitor Faulk", AMALIE, 56, 56, "Sister's",
        None,
        [boss("High Inquisitor Faulk"), k("Hearthglen Inquisitor", 4)],
        None,
        None,
        [("legs", "armor", "mail", "tide_healer"), ("head", "armor", "plate", "strength"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    # ---- Woodwright Jonah Lind
    A(Q("pln_northridge", "Northridge", JONAH, 53, 54, "Woodwright's",
        None,
        [k("Scarlet Lumberjack", 8), k("Scarlet Sawyer", 6)],
        None,
        None,
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")], nxt="pln_woodsman_archers"))
    A(Q("pln_woodsman_archers", "Woodsman Archers", JONAH, 54, 54, "Woodwright's",
        None,
        [k("Scarlet Woodsman Archer", 8)],
        None,
        None,
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="pln_seasoned_oak"))
    A(Q("pln_seasoned_oak", "Seasoned Oak", JONAH, 54, 55, "Woodwright's",
        None,
        [fetch("pl_q_seasoned_plank", 6)],
        None,
        None,
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="pln_foreman_harrow"))
    A(Q("pln_foreman_harrow", "Foreman Harrow", JONAH, 55, 55, "Woodwright's",
        None,
        [boss("Foreman Harrow")],
        None,
        None,
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")]))

    A(Q("pln_saw_blades", "Saw Blades", JONAH, 54, 54, "Woodwright's",
        None,
        [fetch("pl_q_saw_blade", 5)],
        None,
        None,
        [("legs", "armor", "plate", "strength"), ("head", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_2h", "strength")]))

    # ---- Oona Byrne
    A(Q("pln_snapjaws_on_the_thondroril", "Snapjaws on the Thondroril", OONA, 54, 54, "Angler's",
        None,
        [k("Thondroril Snapjaw", 8)],
        None,
        None,
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], nxt="pln_old_thondroril"))
    A(Q("pln_plague_bats", "Plague Bats", OONA, 53, 54, "Angler's",
        None,
        [k("Plague Bat", 10)],
        None,
        None,
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")]))
    A(Q("pln_antler_hooks", "Antler Hooks", OONA, 54, 54, "Angler's",
        None,
        [fetch("pl_q_stag_antler", 6)],
        None,
        None,
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))
    A(Q("pln_old_thondroril", "Old Thondroril", OONA, 55, 55, "Angler's",
        None,
        [boss("Old Thondroril"), k("Thondroril Snapjaw", 4)],
        None,
        None,
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("ring", "armor", None, "hunter_crit")]))

    # ---- Clerk Wendel Ashby
    A(Q("pln_the_patrol_roster", "The Patrol Roster", WENDEL, 55, 55, "Clerk's",
        None,
        [fetch("pl_q_patrol_roster", 1)],
        None,
        None,
        [("feet", "armor", "leather", "assassin"), ("head", "armor", "plate", "crusader"),
         ("wrist", "armor", "cloth", "healer")], nxt="pln_hearthglens_hounds"))
    A(Q("pln_hearthglens_hounds", "Hearthglen's Hounds", WENDEL, 55, 56, "Clerk's",
        None,
        [k("Scarlet War Hound", 10)],
        None,
        None,
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "strength")]))

    # ---- the Weeping Cave, in the hill above the Thondroril (tools/handbuilt_plaguelands_caves.py)
    A(Q("pln_the_water_under_the_hill", "The Water Under the Hill", OONA, 55, 56, "Angler's",
        None,
        [k("Cave Drowned", 8, WC), k("Seepwater Shade", 8, WC)],
        None,
        None,
        [("legs", "armor", "leather", "hunter"), ("shoulder", "armor", "cloth", "frost"),
         ("feet", "armor", "plate", "tank_any")], nxt="pln_the_weeper"))
    A(Q("pln_the_weeper", "The Weeper", AMALIE, 56, 56, "Sister's",
        None,
        [boss("The Weeper", WC)],
        None,
        None,
        [("head", "armor", "cloth", "spirit_healer"), ("hands", "armor", "leather", "rogue_crit"),
         ("main_hand", "weapon", "sword_1h", "strength_hit")]))
    A(Q("pln_the_hermits_account", "The Hermit's Account", WENDEL, 56, 56, "Clerk's",
        None,
        [boss("The Drowned Hermit", WC)],
        None,
        None,
        [("waist", "armor", "mail", "mail_caster"), ("back", "armor", None, "assassin"),
         ("wrist", "armor", "plate", "plate_healer")]))

    # ---- in from Felwood
    A(Q("pln_supplies_from_felwood", "Supplies from Felwood", NKECHI, 52, 53, "Doctor's",
        None,
        [deliver("pl_q_nkechis_kit", "Bring Dr. Adeyemi's field kit to Field Medic Noah Kowal at the Pale Watch")],
        None,
        None,
        [("chest", "armor", "cloth", "high_healer"), ("legs", "armor", "plate", "strength_crit"),
         ("ring", "armor", None, "agility")], zone="emerald_sanctuary", turn_in_npc_id=NOAH,
        grant_items=carry("pl_q_nkechis_kit", "Dr. Adeyemi's Field Kit", "A canvas roll of sutures, dressings and "
                          "small brown bottles, packed tight and labelled in English.")))

    # ======================================================================================== HEARTHGLEN
    # Given at the Pale Watch (Kyle: dungeon quests are given in town).
    HT, HK = "hearthglen", "hearthglen:_mardenholde_keep"
    A(Q("pln_closing_hearthglens_books", "Closing Hearthglen's Books", WENDEL, 59, 60, "Clerk's",
        None,
        [boss("Grand Crusader Victor Hale", HK)],
        None,
        None,
        [("main_hand", "weapon", "staff", "caster"), ("chest", "armor", "plate", "tank_any"),
         ("hands", "armor", "leather", "agility")]))
    A(Q("pln_the_infirmary", "The Infirmary", BEATRIZ, 58, 59, "Couto's",
        None,
        [boss("Chirurgeon Maeve Ostrowski", HT), boss("High Clerist Hendrick", HT)],
        None,
        None,
        [("head", "armor", "cloth", "healer"), ("waist", "armor", "mail", "hunter"),
         ("trinket", "armor", None, "physical")]))
    A(Q("pln_the_kennels", "The Kennels", LIAM, 58, 58, "Roostkeeper's",
        None,
        [boss("Huntsman Radley", HT), k("Hearthglen Mastiff", 6, HT)],
        None,
        None,
        [("ranged", "weapon", "bow", "agility"), ("shoulder", "armor", "leather", "healer"),
         ("wrist", "armor", "plate", "strength")]))
    return out
