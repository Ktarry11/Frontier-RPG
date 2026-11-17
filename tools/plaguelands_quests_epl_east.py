"""
East Eastern Plaguelands' quests, levels 56-60. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT EAST EPL IS ABOUT (docs/plaguelands_design.md). The far end of the Plaguelands, where the Argent Dawn holds
Light's Hope Chapel on holy ground, its own town map now, with Crown Guard's camp moved inside it (16 Nov 2026,
docs/plaguelands_towns_plan.md); Crown Guard's people still keep the road between the chapel and Stratholme
open. Darrowshire's ghosts still fight the battle they lost, the Scarlet Crusade holds Tyr's Hand on the coast, the
Mossflayer trolls of Zul'Mashar raid the roads, Quel'Lithien Lodge's rangers walk their posts long after they died,
and the Scourge is building something out of bones in the Pestilent Scar.

  LIGHT'S HOPE (21)  Commander Eligor Dawnbringer (Tyr's Hand, the Abbot, a word with the Order), Archmage Lysander
                     Hale (the Scar's marrow and the Bone Colossus), Lightwarden Ysolde Carrow (Darrowshire's dead,
                     the Scar, the Mossflayer hexes), Sergeant Marisol Reyes (the Mossflayers and their medicine, and
                     a colleague at Talonbranch), Ranger Faelis Dawnreach (his old lodge), Innkeeper Jessa Moonfield
                     (lamp oil).
  CROWN GUARD (13)   Captain Joss Varden (the road, Darrowshire's ghouls, Tyr's Hand's hounds and archers), Corporal
                     Ines Duarte (Blackwood Lake, and filters for Felwood), Innkeeper Greta Lowe (horse for the pot,
                     a barrel for the Order), Bat Handler Gwen Pike (the wild bats, and a young one for Light's
                     Hope).
  DARROWSHIRE (3)    Pamela Redpath, a little girl's ghost who's still waiting for her father.
  OUT                Felwood (Ines's filters to Tomasz Wolny at the Emerald Sanctuary, Marisol's notes to Marcus
                     Oyelaran at Talonbranch), the Bulwark (Dawnbringer to Rory, Greta to Priya, Pamela to Odile).
  IN                 Arathi (Overlord Gath'rok's answer to Dawnbringer).
  CAVE               The Bone Mines, under the Scar (Ysolde: the miners; Faelis: the Overseer, then the Ossifier).

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and only
the people at the top know more. The Argent Dawn takes anyone who'll stand on the wall and doesn't ask where they came
from. Its people call the transplants newcomers. Dawnbringer knows more than he says. Ines and Marisol are
transplants and talk about home the way anyone does.

WHO PAYS. Everything here pays the Argent Dawn, the zone's own faction.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.plaguelands_quest_voice import VOICE

EE = "eastern_plaguelands_east"
BM = "the_bone_mines"

# ---- the people
VARDEN, GRETA, GWEN, INES = "epl_cg_captain", "epl_cg_innkeeper", "epl_cg_flight", "epl_cg_corporal"
DAWN, HALE, JESSA, ALDOUS = "epl_lh_commander", "epl_lh_scourgestones", "epl_lh_innkeeper", "epl_lh_flight"
YSOLDE, MARISOL, FAELIS = "epl_lh_lightwarden", "epl_lh_volunteer", "epl_lh_ranger"
PAMELA = "epl_ds_pamela"
GATHROK = "hammerfall_commander"
RORY, PRIYA, ODILE = "wpl_pf_flamekeeper", "wpl_pf_innkeeper", "wpl_pf_chaplain"
TOMASZ, MARCUS = "es_volunteer_carpenter", "fn_talonbranch_medic"

HUB_GIVERS = {VARDEN, GRETA, GWEN, INES, DAWN, HALE, JESSA, YSOLDE, MARISOL, FAELIS}
#: the people born here, who say newcomers and never Earth
NATIVE_GIVERS = {VARDEN, GRETA, GWEN, DAWN, HALE, JESSA, YSOLDE, FAELIS, PAMELA, GATHROK}
FACTION_BY_GIVER = {}


def k(target, n, zone=EE):
    return kill(target, n, zone=zone)


def boss(target, zone=EE):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=EE, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Blackwood Snapjaw": [("pl_q_gizzard_stone", "Snapjaw Gizzard Stone", "A smooth stone from a snapjaw's gizzard, "
                           "stained green where the lake water's soaked into it.")],
    "Blighted Warhorse": [("pl_q_warhorse_flank", "Warhorse Flank", "A cut from a blighted warhorse's flank. Greta "
                           "says the plague cooks out. Greta says a lot of things.")],
    "Scar Bone Construct": [("pl_q_scar_marrow", "Scar Marrow", "A plug of grey marrow from a bone construct. It's "
                             "cold, and it stays cold however long you hold it.")],
    "Mossflayer Shadowhunter": [("pl_q_hex_fetish", "Mossflayer Hex Fetish", "A bundle of feathers, teeth and "
                                 "string, knotted around a scrap of cloth from the chapel's laundry.")],
    "Mossflayer Scout": [("pl_q_herb_pouch", "Mossflayer Herb Pouch", "A troll's herb pouch, full of dried leaves "
                          "and roots that smell clean, which is rare out here.")],
    "Restless Lodge Ranger": [("pl_q_ranger_token", "Quel'Lithien Ranger's Token", "A silver leaf on a green cord, "
                               "the token every ranger of the lodge carried. It's tarnished but whole.")],
    "Plague-Rotted Bear": [("pl_q_bear_fat", "Rendered Bear Fat", "A lump of fat cut from the parts of a bear the rot "
                            "hadn't reached. It'll burn clean in a lamp, if nothing else.")],
    "Darrowshire Ghoul": [("pl_q_pamelas_doll", "Pamela's Doll", "A rag doll in a blue dress, muddy and missing a "
                           "button eye. Someone loved it very much.", 1.0)],
}

STARTER_DROPS = {}
STARTER_IDS = {}


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=EE, **engine):
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
    # ---- Captain Joss Varden
    A(Q("ple_the_road_between", "The Road Between", VARDEN, 56, 57, "Crown Guard",
        None,
        [k("Blighted Warhorse", 8), k("Plague-Rotted Bear", 6)],
        None,
        None,
        [("chest", "armor", "plate", "tank"), ("legs", "armor", "cloth", "caster"),
         ("hands", "armor", "leather", "agility")], nxt="ple_darrowshires_ghouls"))
    A(Q("ple_word_to_lights_hope", "Word to the Commander", VARDEN, 56, 56, "Crown Guard",
        None,
        [deliver("pl_q_varden_report", "Bring Varden's report to Commander Eligor Dawnbringer at Light's Hope")],
        None,
        None,
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], turn_in_npc_id=DAWN,
        grant_items=carry("pl_q_varden_report", "Varden's Report", "A folded report in a soldier's square hand, "
                                                                   "sealed with Crown Guard's tower.")))
    A(Q("ple_darrowshires_ghouls", "Darrowshire's Ghouls", VARDEN, 57, 57, "Crown Guard",
        None,
        [k("Darrowshire Ghoul", 10)],
        None,
        None,
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="ple_the_houndmasters"))
    A(Q("ple_the_houndmasters", "The Houndmasters", VARDEN, 58, 58, "Crown Guard",
        None,
        [k("Tyr's Hand Houndmaster", 8)],
        None,
        None,
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")], nxt="ple_arrows_on_the_road"))
    A(Q("ple_arrows_on_the_road", "Arrows on the Road", VARDEN, 58, 59, "Crown Guard",
        None,
        [k("Tyr's Hand Marksman", 8)],
        None,
        None,
        [("head", "armor", "mail", "hunter_precise"), ("waist", "armor", "plate", "crusader"),
         ("back", "armor", None, "physical")]))

    # ---- Corporal Ines Duarte
    A(Q("ple_the_blackwood_shore", "The Blackwood Shore", INES, 56, 57, "Duarte's",
        None,
        [k("Blackwood Drowned", 10)],
        None,
        None,
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")], nxt="ple_whats_in_the_water"))
    A(Q("ple_whats_in_the_water", "What's in the Water", INES, 56, 57, "Duarte's",
        None,
        [fetch("pl_q_gizzard_stone", 6)],
        None,
        None,
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="ple_the_blackwood_drowner"))
    A(Q("ple_the_blackwood_drowner", "The Blackwood Drowner", INES, 57, 57, "Duarte's",
        None,
        [boss("The Blackwood Drowner"), k("Blackwood Snapjaw", 6)],
        None,
        None,
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="ple_filters_for_felwood"))
    A(Q("ple_filters_for_felwood", "Filters for Felwood", INES, 57, 57, "Duarte's",
        None,
        [deliver("pl_q_filter_drawings", "Bring Ines's filter drawings to Tomasz Wolny at the Emerald Sanctuary")],
        None,
        None,
        [("legs", "armor", "leather", "bruiser"), ("hands", "armor", "mail", "tide_healer"),
         ("ranged", "weapon", "gun", "hunter_crit")], turn_in_npc_id=TOMASZ,
        grant_items=carry("pl_q_filter_drawings", "Ines's Filter Drawings", "A roll of careful drawings in pencil, "
                                                                           "labelled in Portuguese and then again in "
                                                                           "Common.")))

    # ---- Innkeeper Greta Lowe
    A(Q("ple_horse_for_the_pot", "Horse for the Pot", GRETA, 56, 56, "Hearthside",
        None,
        [fetch("pl_q_warhorse_flank", 6)],
        None,
        None,
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")]))
    A(Q("ple_a_barrel_for_sorrow_hill", "A Barrel for the Order", GRETA, 56, 57, "Hearthside",
        None,
        [deliver("pl_q_ale_barrel", "Bring Greta's barrel of ale to Priya Raman at the Bulwark")],
        None,
        None,
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "tank"),
         ("main_hand", "weapon", "sword_1h", "caster")], turn_in_npc_id=PRIYA,
        grant_items=carry("pl_q_ale_barrel", "Barrel of Crown Guard Ale", "A small barrel of dark ale, stamped with "
                                                                         "Greta's mark and heavier than it looks.")))

    # ---- Bat Handler Gwen Pike
    A(Q("ple_wild_bats", "Wild Bats", GWEN, 56, 57, "Nightwing",
        None,
        [k("Carrion Bat", 10)],
        None,
        None,
        [("legs", "armor", "mail", "earthen"), ("waist", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "high_healer")], nxt="ple_a_bat_for_lights_hope"))
    A(Q("ple_a_bat_for_lights_hope", "A Bat for the Perch", GWEN, 57, 57, "Nightwing",
        None,
        [deliver("pl_q_young_bat", "Bring the young bat to Flight Master Aldous Grey at Light's Hope")],
        None,
        None,
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")], turn_in_npc_id=ALDOUS,
        grant_items=carry("pl_q_young_bat", "Covered Basket", "A wicker basket under a heavy cloth. Something inside "
                                                              "chirps whenever you stop walking.")))

    # ======================================================================================== LIGHT'S HOPE
    # ---- Commander Eligor Dawnbringer
    A(Q("ple_tyrs_hand", "Tyr's Hand", DAWN, 58, 58, "Dawnbringer's",
        None,
        [k("Tyr's Hand Crusader", 10)],
        None,
        None,
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="ple_the_abbots"))
    A(Q("ple_the_abbots", "The Abbots of Tyr's Hand", DAWN, 58, 59, "Dawnbringer's",
        None,
        [k("Tyr's Hand Abbot", 8)],
        None,
        None,
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="ple_abbot_varenne"))
    A(Q("ple_abbot_varenne", "Abbot Varenne", DAWN, 59, 59, "Dawnbringer's",
        None,
        [boss("Abbot Varenne")],
        None,
        None,
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")]))
    A(Q("ple_a_word_with_the_order", "A Word with the Order", DAWN, 58, 58, "Dawnbringer's",
        None,
        [deliver("pl_q_dawnbringer_letter", "Bring Dawnbringer's letter to Flamekeeper Rory Callahan at the "
                                            "Bulwark")],
        None,
        None,
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], turn_in_npc_id=RORY,
        grant_items=carry("pl_q_dawnbringer_letter", "Dawnbringer's Letter", "A letter sealed with the Argent "
                                                                             "Dawn's sunburst, addressed in a careful "
                                                                             "hand to the Flamekeeper.")))

    # ---- Archmage Lysander Hale
    A(Q("ple_marrow_of_the_scar", "Marrow of the Scar", HALE, 58, 58, "Hale's",
        None,
        [fetch("pl_q_scar_marrow", 6)],
        None,
        None,
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")], nxt="ple_the_bone_colossus"))
    A(Q("ple_the_bone_colossus", "The Bone Colossus", HALE, 60, 60, "Hale's",
        None,
        [boss("The Bone Colossus"), k("Scar Bone Construct", 6)],
        None,
        None,
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))

    # ---- Lightwarden Ysolde Carrow
    A(Q("ple_darrowshires_dead", "Darrowshire's Dead", YSOLDE, 57, 58, "Lightwarden's",
        None,
        [k("Darrowshire Spirit", 10)],
        None,
        None,
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("ring", "armor", None, "hunter_crit")]))
    A(Q("ple_the_pestilent_scar", "The Pestilent Scar", YSOLDE, 57, 57, "Lightwarden's",
        None,
        [explore(110, 56, "Look into the Pestilent Scar")],
        None,
        None,
        [("ring", "armor", None, "spirit_caster"), ("feet", "armor", "mail", "hunter_precise"),
         ("wrist", "armor", "plate", "plate_healer")]))
    A(Q("ple_the_shadowhunters", "The Shadowhunters", YSOLDE, 58, 58, "Lightwarden's",
        None,
        [k("Mossflayer Shadowhunter", 8)],
        None,
        None,
        [("chest", "armor", "cloth", "caster"), ("legs", "armor", "plate", "strength"),
         ("hands", "armor", "leather", "wildheart")], nxt="ple_hex_fetishes"))
    A(Q("ple_hex_fetishes", "Hex Fetishes", YSOLDE, 58, 59, "Lightwarden's",
        None,
        [fetch("pl_q_hex_fetish", 5)],
        None,
        None,
        [("shoulder", "armor", "mail", "earthen"), ("head", "armor", "cloth", "caster_crit"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    # ---- Sergeant Marisol Reyes
    A(Q("ple_troll_medicine", "Troll Medicine", MARISOL, 57, 58, "Reyes's",
        None,
        [fetch("pl_q_herb_pouch", 5)],
        None,
        None,
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "strength")], nxt="ple_mossflayer_raiders"))
    A(Q("ple_mossflayer_raiders", "Mossflayer Raiders", MARISOL, 58, 58, "Reyes's",
        None,
        [k("Mossflayer Warrior", 8), k("Mossflayer Scout", 6)],
        None,
        None,
        [("feet", "armor", "leather", "assassin"), ("head", "armor", "plate", "crusader"),
         ("wrist", "armor", "cloth", "healer")], nxt="ple_zulmashar_the_last"))
    A(Q("ple_zulmashar_the_last", "Zul'Mashar the Last", MARISOL, 59, 59, "Reyes's",
        None,
        [boss("Zul'Mashar the Last")],
        None,
        None,
        [("hands", "armor", "plate", "strength_crit"), ("shoulder", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "caster")]))
    A(Q("ple_the_medics_network", "The Medics' Network", MARISOL, 58, 58, "Reyes's",
        None,
        [deliver("pl_q_medic_notes", "Bring Marisol's notes to Marcus Oyelaran at Talonbranch Glade")],
        None,
        None,
        [("chest", "armor", "plate", "strength"), ("waist", "armor", "cloth", "high_healer"),
         ("ranged", "weapon", "bow", "hunter")], turn_in_npc_id=MARCUS,
        grant_items=carry("pl_q_medic_notes", "Marisol's Notes", "A bundle of notes in a quick, slanted hand, with "
                                                                 "pressed leaves taped beside every recipe.")))

    # ---- Ranger Faelis Dawnreach
    A(Q("ple_the_restless_lodge", "The Restless Lodge", FAELIS, 57, 57, "Dawnreach's",
        None,
        [k("Restless Lodge Ranger", 8)],
        None,
        None,
        [("chest", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "tank"),
         ("back", "armor", None, "caster")], nxt="ple_the_silver_leaves"))
    A(Q("ple_the_silver_leaves", "The Silver Leaves", FAELIS, 57, 58, "Dawnreach's",
        None,
        [fetch("pl_q_ranger_token", 6)],
        None,
        None,
        [("legs", "armor", "leather", "bruiser"), ("head", "armor", "plate", "strength"),
         ("ranged", "weapon", "wand", "caster")], nxt="ple_ranger_lord_saelith"))
    A(Q("ple_ranger_lord_saelith", "Ranger-Lord Saelith", FAELIS, 59, 59, "Dawnreach's",
        None,
        [boss("Ranger-Lord Saelith")],
        None,
        None,
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")]))

    # ---- Innkeeper Jessa Moonfield
    A(Q("ple_lamp_oil", "Lamp Oil", JESSA, 56, 57, "Lightwarden's",
        None,
        [fetch("pl_q_bear_fat", 6)],
        None,
        None,
        [("shoulder", "armor", "leather", "hunter_crit"), ("waist", "armor", "plate", "tank"),
         ("main_hand", "weapon", "polearm", "agility")]))

    # ======================================================================================== DARROWSHIRE
    # ---- Pamela Redpath
    A(Q("ple_pamelas_doll", "Pamela's Doll", PAMELA, 57, 57, "Darrowshire",
        None,
        [fetch("pl_q_pamelas_doll", 1)],
        None,
        None,
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")], nxt="ple_a_letter_for_auntie"))
    A(Q("ple_a_letter_for_auntie", "A Letter for Auntie", PAMELA, 57, 57, "Darrowshire",
        None,
        [deliver("pl_q_pamelas_letter", "Bring Pamela's letter to Chaplain Odile Marchand at the Bulwark")],
        None,
        None,
        [("feet", "armor", "mail", "earthen"), ("wrist", "armor", "leather", "agility"),
         ("back", "armor", None, "caster")], turn_in_npc_id=ODILE, nxt="ple_where_daddy_is",
        grant_items=carry("pl_q_pamelas_letter", "Pamela's Letter", "A letter in a child's big round letters, with a "
                                                                    "drawing of a house and a doll on the back.")))
    A(Q("ple_where_daddy_is", "Where Daddy Is", PAMELA, 58, 58, "Darrowshire",
        None,
        [boss("Captain Redpath's Shade")],
        None,
        None,
        [("main_hand", "weapon", "polearm", "strength"), ("head", "armor", "cloth", "high_healer"),
         ("hands", "armor", "leather", "hunter")]))

    # ---- the Bone Mines, under the Pestilent Scar (tools/handbuilt_plaguelands_caves.py)
    A(Q("ple_the_bones_of_the_east", "The Bones of the East", YSOLDE, 58, 59, "Lightwarden's",
        None,
        [k("Bone Miner", 10, BM), k("Scourge Pit Guard", 6, BM)],
        None,
        None,
        [("chest", "armor", "leather", "bear"), ("hands", "armor", "cloth", "void"),
         ("feet", "armor", "mail", "earthen")], nxt="ple_the_overseer"))
    A(Q("ple_the_overseer", "The Overseer", FAELIS, 59, 60, "Ranger's",
        None,
        [boss("Overseer Marrowgrim", BM)],
        None,
        None,
        [("legs", "armor", "plate", "strength"), ("shoulder", "armor", "mail", "hunter"),
         ("main_hand", "weapon", "wand", "dark_haste")], nxt="ple_the_ossifier"))
    A(Q("ple_the_ossifier", "The Ossifier", FAELIS, 60, 60, "Ranger's",
        None,
        [boss("The Ossifier", BM)],
        None,
        None,
        [("head", "armor", "cloth", "fel"), ("waist", "armor", "leather", "blood"),
         ("main_hand", "weapon", "axe_2h", "strength_crit")]))

    # ---- in from Arathi: Hammerfall's answer
    A(Q("ple_hammerfalls_answer", "Hammerfall's Answer", GATHROK, 55, 56, "Overlord's",
        None,
        [deliver("pl_q_gathroks_answer", "Bring Gath'rok's answer to Commander Eligor Dawnbringer at Light's Hope")],
        None,
        None,
        [("wrist", "armor", "leather", "physical"), ("chest", "armor", "mail", "battlemage"),
         ("back", "armor", None, "sturdy_caster")], zone="arathi_central", turn_in_npc_id=DAWN,
        grant_items=carry("pl_q_gathroks_answer", "Gath'rok's Answer", "A strip of hide branded with Hammerfall's "
                          "mark and a few lines in Orcish, rolled tight and tied with sinew.")))
    return out
