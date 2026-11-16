"""
South Western Plaguelands' quests, levels 51-54. Read by tools/build_plaguelands_quests.py, which holds them to the
Stonetalon pass's rules before anything is written.

WHAT SOUTH WPL IS ABOUT (docs/plaguelands_design.md). The Plaguelands as players remember them, with the Integration's
small adjustments: the Scourge works its cauldrons on Lordaeron's farms and holds Andorhal, the Cult of the Damned
tends the plague, and the Scarlet Crusade pushes patrols down from Hearthglen. Two hubs, and they don't like each
other much: the Bulwark, the Forsaken's wall on the Tirisfal border, and Sorrow Hill, the Order of the Pale Flame's
keep beside Uther's Tomb, led by Earth transplants who walked out of the Crusade.

  THE BULWARK (17)   High Executor Marla Venn (the line, Andorhal, a dispatch to Sorrow Hill), Apothecary Dorian
                     Vesk (the cauldron chain, which ends at Sun Rock in Stonetalon), Deathstalker Ilsa Rook (the
                     Cult's couriers and a report for the Undercity), Deathguard Captain Ludo Vance (the farms' named
                     horrors), Surgeon Halbert Grey (snapjaw shell and Old Darrowjaw).
  SORROW HILL (22)   Flamekeeper Rory Callahan (the Order's rule, the Scarlet patrols, Hearthglen's orders, Caer
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

WHO PAYS. The Bulwark pays the Forsaken and Sorrow Hill pays the Order, except Venn's dispatch, which Rory hands in.
The Forsaken own more quests than anyone, and by the time a player reaches the Plaguelands they're most of the way
to Exalted with them (tools/qa_factions.py wants the last tiers to take at least the last 40% of a faction's
quests). So the Bulwark is kept small and the Plaguelands' own quests go to the Order and the Argent Dawn.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

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
#: who pays: the Bulwark pays the Forsaken, Sorrow Hill the Order (the zone's own faction)
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
        "High Executor Marla Venn holds the Bulwark, the Forsaken's wall where Tirisfal ends and the Plaguelands "
        "begin. Everything east of it wants to come west.\n\nThe fields beyond the gate are full of Wandering "
        "Skeletons, and every Plague-Ridden Wolf in the south hunts the grass beside them. She wants them thinned before "
        "the next night comes.",
        [k("Wandering Skeleton", 10), k("Plague-Ridden Wolf", 8)],
        "Out the east gate and into the fields. The skeletons walk the King's Road and the wolves run the grass "
        "either side of it. Don't chase anything past the crossroads.",
        "The wall will sleep a little easier tonight.\n\nI've held this gate since the Dark Lady gave it to me, and "
        "I'll hold it after you've gone. That's what a wall is for.",
        [("chest", "armor", "plate", "tank"), ("legs", "armor", "cloth", "caster"),
         ("hands", "armor", "leather", "agility")], giver_zone=True, nxt="pls_andorhals_gate"))
    A(Q("pls_andorhals_gate", "Andorhal's Gate", VENN, 52, 52, "Bulwark",
        "Andorhal was a city once. Now it's the Scourge's in the middle of the south, and its dead march north to "
        "the crossroads and west to the Bulwark.\n\nVenn wants the Andorhal Skeletons that hold its gate cut down, "
        "and the Andorhal Skeletal Archers on its walls with them, so her patrols can see inside.",
        [k("Andorhal Skeleton", 10), k("Andorhal Skeletal Archer", 6)],
        "Andorhal's south of the crossroads, down the road toward the lake. You'll know it by the smoke. The archers "
        "keep to the broken walls, so come at them from the side.",
        "My patrols can see into the city now, and what they see isn't pretty.\n\nI've got a harder job for you, if "
        "you've the stomach for it.",
        [("feet", "armor", "mail", "hunter"), ("wrist", "armor", "plate", "strength"),
         ("ring", "armor", None, "caster")], nxt="pls_the_necromancers"))
    A(Q("pls_the_necromancers", "The Necromancers of Andorhal", VENN, 53, 53, "Bulwark",
        "The skeletons don't raise themselves. Andorhal Necromancers stand in the ruins and keep the dead on their "
        "feet, and every one of them carries a focus, a bone rod that does the work.\n\nVenn wants the "
        "necromancers dead and their foci on her desk, so the Royal Apothecary Society can learn how to break them.",
        [k("Andorhal Necromancer", 8), fetch("pl_q_necro_focus", 5)],
        "The necromancers keep to the middle of Andorhal, among the burned houses. Most of them carry a focus. Bring "
        "me the rods and don't hold them any longer than you have to.",
        "They hum, don't they? I hate that.\n\nThe Society will take them apart. One more job and Andorhal's ours to "
        "watch.",
        [("head", "armor", "cloth", "shadow"), ("shoulder", "armor", "mail", "earthen"),
         ("main_hand", "weapon", "dagger", "rogue_crit")], nxt="pls_the_magistrate"))
    A(Q("pls_the_magistrate", "The Magistrate", VENN, 54, 54, "Bulwark",
        "Andorhal's magistrate died with his city and got up again. Magistrate Andor still sits in the ruins and "
        "gives orders, and the Andorhal Abominations stand guard over him.\n\nVenn served in Lordaeron's army "
        "before she died. She knew the man. She'd like him put down by somebody who isn't her.",
        [boss("Magistrate Andor"), k("Andorhal Abomination", 6)],
        "He keeps to what's left of the town hall in the middle of Andorhal, and he isn't always there. Kill the "
        "abominations while you wait for him. He's stronger than he looks, so bring friends.",
        "Then he's at rest, and so is Andorhal, for a little while.\n\nHe signed my commission once. I'd rather "
        "not have watched him do it again.",
        [("legs", "armor", "plate", "tank_any"), ("chest", "armor", "leather", "healer"),
         ("main_hand", "weapon", "mace_2h", "strength")]))
    A(Q("pls_a_dispatch_for_sorrow_hill", "A Dispatch for Sorrow Hill", VENN, 51, 51, "Bulwark",
        "Venn doesn't like the Order of the Pale Flame. They wear what used to be Scarlet armour, they're led by "
        "newcomers, and they've a keep at Sorrow Hill under the Crusade's nose. They also kill the mindless dead "
        "and leave the Forsaken alone, and the wall needs every friend it can get.\n\nShe has a dispatch for their "
        "Flamekeeper, Rory Callahan.",
        [deliver("pl_q_venn_dispatch", "Bring Venn's dispatch to Flamekeeper Rory Callahan at Sorrow Hill")],
        "South from the crossroads on the road to the lake. Sorrow Hill's the keep by Uther's Tomb. Don't let them "
        "keep you there too long.",
        "Marla Venn's seal. She writes like she's sharpening a knife.\n\nShe wants to know if we'll hold the road "
        "south of Andorhal. Tell her we will, and that the Order sends its regards, which she'll hate.",
        [("waist", "armor", "mail", "tide_healer"), ("back", "armor", None, "physical"),
         ("feet", "armor", "cloth", "spirit_caster")], turn_in_npc_id=RORY,
        grant_items=carry("pl_q_venn_dispatch", "Venn's Dispatch", "A dispatch sealed with the Bulwark's black wax.")))

    # ---- Apothecary Dorian Vesk (the cauldrons)
    A(Q("pls_felstone_field", "Felstone Field", VESK, 51, 52, "Vesk's",
        "Apothecary Dorian Vesk wants to know what the Scourge is brewing in its cauldrons, and the nearest one is "
        "on the Felstone farm, north of the King's Road. It's guarded by the Felstone Cultists who tend it and the "
        "Felstone Ghouls who used to work the field.\n\nHe wants a way in.",
        [k("Felstone Ghoul", 8), k("Felstone Cultist", 6)],
        "North from the road at the crossroads, past the dead orchard. The cauldron's in the middle of the field. "
        "Clear the ghouls and the cultists around it and come back. Don't touch the cauldron yet.",
        "That'll do nicely. The way in's open now.\n\nNow for the part I actually care about.",
        [("hands", "armor", "cloth", "healer"), ("legs", "armor", "leather", "bear"),
         ("ring", "armor", None, "strength")], nxt="pls_a_sample_from_felstone"))
    A(Q("pls_a_sample_from_felstone", "A Sample from Felstone", VESK, 52, 52, "Vesk's",
        "The Felstone cauldron is kept by a Felstone Cauldron Lord, one of the Scourge's stitched brutes, and the "
        "only clean sample is the one in the flask it keeps at its belt.\n\nVesk wants that flask.",
        [k("Felstone Cauldron Lord", 1), fetch("pl_q_felstone_sample", 1)],
        "It stands at the cauldron. It's big and it's slow and it hits like a falling barn. The flask will be on "
        "it.",
        "It's still warm, and that's wonderful.\n\nThere are three more cauldrons in the south. I'd like them all.",
        [("chest", "armor", "mail", "mail_caster"), ("shoulder", "armor", "plate", "strength_crit"),
         ("main_hand", "weapon", "staff", "high_healer")], nxt="pls_dalsons_tears"))
    A(Q("pls_dalsons_tears", "Dalson's Tears", VESK, 52, 53, "Vesk's",
        "The Dalson farm north of the road has its own cauldron, and the Cauldron Necrolytes who stir it carry "
        "flasks of the brew. Dalson's Ghouls work the yard around them.\n\nVesk wants a sample from the Dalson "
        "cauldron to set beside the Felstone one.",
        [fetch("pl_q_dalson_sample", 1), k("Dalson's Ghoul", 8)],
        "North and a little east of Felstone, the farm with the big red barn. The necrolytes keep to the cauldron "
        "in the yard. Leave the barn alone, I mean it, and don't let them tip the cauldron.",
        "Thicker than Felstone's. They're changing the recipe from farm to farm.\n\nThat's either very bad or very "
        "interesting. I'd like one more before I decide.",
        [("head", "armor", "leather", "hunter"), ("wrist", "armor", "cloth", "caster"),
         ("off_hand", "weapon", "shield", "shield_tank")], nxt="pls_the_writhing_haunt"))
    A(Q("pls_the_writhing_haunt", "The Writhing Haunt", VESK, 53, 53, "Vesk's",
        "The last cauldron in the south is at the Writhing Haunt, east of Dalson's, where the Haunt Cult Tenders "
        "keep the brew stirred and the banshees keep everyone else away.\n\nVesk wants a sample, and he wants the "
        "tenders thinned so the next apothecary who goes there comes back.",
        [k("Haunt Cult Tender", 8), fetch("pl_q_haunt_sample", 1)],
        "East along the north road, where the ground goes soft and the trees die. The tenders carry flasks. The "
        "banshees will come when you start fighting, so pick your ground and don't stand in the open.",
        "Something's moving in this one. Look at that.\n\nI need someone who knows more about the walking dead "
        "than I do, and the only one I trust is on the other side of the sea.",
        [("feet", "armor", "plate", "plate_healer"), ("legs", "armor", "mail", "hunter"),
         ("neck", "armor", None, "caster")], nxt="pls_what_the_plague_is_made_of"))
    A(Q("pls_what_the_plague_is_made_of", "What the Plague Is Made Of", VESK, 53, 54, "Vesk's",
        "Vesk studied under Apothecary Merrow Vane, who's at Sun Rock Retreat in Stonetalon now, watching the "
        "dead get up on the Mulgore side of the mountain with nobody calling them. Vesk thinks the cauldrons and "
        "Mulgore might be the same sickness.\n\nHe's packed his samples, and he wants them in Merrow's hands.",
        [deliver("pl_q_sample_case", "Bring the sample case to Apothecary Merrow Vane at Sun Rock Retreat")],
        "Zeppelin from Tirisfal to Orgrimmar, and a wind rider to Sun Rock. Merrow will be the only Forsaken there. "
        "Keep the case upright and don't let the tauren open it.",
        "These are Dorian's samples, all right. He always did label everything twice.\n\nThis one, from the Haunt, moves the way the dead "
        "on the Rim move. I'll write to him tonight, and I'm afraid of what I'll be writing.",
        [("chest", "armor", "cloth", "high_healer"), ("hands", "armor", "plate", "crusader"),
         ("ranged", "weapon", "gun", "hunter_crit")], turn_in_npc_id=MERROW,
        grant_items=carry("pl_q_sample_case", "Vesk's Sample Case", "A padded case with three labelled flasks. One of "
                                                                   "them knocks against the side now and then.")))

    # ---- Deathstalker Ilsa Rook
    A(Q("pls_cult_couriers", "Cult Couriers", ROOK, 52, 53, "Cipherbreaker's",
        "Deathstalker Ilsa Rook watches the Cult of the Damned, and the Cult writes letters. The Haunt Cult Tenders "
        "at the Writhing Haunt carry them to somebody, and Rook would very much like to know who.\n\nShe wants the "
        "letters, in their cipher, before they're delivered.",
        [fetch("pl_q_cult_letter", 4)],
        "The tenders at the Writhing Haunt carry the letters. Only some of them have one. Bring me what you find, "
        "and don't try to read them. The cipher's a nasty one.",
        "Every letter's in a different hand, and the same name's in all of them.\n\nI'll need the Undercity to hear this.",
        [("legs", "armor", "leather", "assassin"), ("hands", "armor", "mail", "tide_healer"),
         ("main_hand", "weapon", "sword_1h", "caster")], nxt="pls_a_report_for_the_undercity"))
    A(Q("pls_a_report_for_the_undercity", "A Report for the Undercity", ROOK, 53, 53, "Cipherbreaker's",
        "The Cult's letters name somebody in the Undercity who's been passing them the city's patrol routes. Rook "
        "won't trust the bats with this, and she won't trust a courier she hasn't met.\n\nShe wants her report "
        "put into Deathstalker Rhyne's hand in the Undercity.",
        [deliver("pl_q_rook_report", "Bring Rook's report to Deathstalker Rhyne in the Undercity")],
        "West through the Bulwark gate and into Tirisfal, then down into the Undercity. Rhyne's in the Royal "
        "Quarter. Give it to him and nobody else, and don't stop for a drink on the way.",
        "So this is Rook's report. She writes like she's afraid of running out of ink.\n\nThis name's going to make some "
        "people very unhappy. Thank you. I'll handle it from here.",
        [("shoulder", "armor", "cloth", "caster_crit"), ("feet", "armor", "leather", "feral"),
         ("ring", "armor", None, "healer")], zone=WS, turn_in_npc_id=RHYNE,
        grant_items=carry("pl_q_rook_report", "Rook's Report", "A thin report sealed twice, once with wax and once "
                                                               "with something that smells like poison.")))
    A(Q("pls_the_mother_of_the_haunt", "The Mother of the Haunt", ROOK, 53, 54, "Cipherbreaker's",
        "The banshees at the Writhing Haunt answer to something Rook calls the Mother of the Haunt, a banshee old "
        "enough to remember the farm before the plague. The Haunt Banshees keep the Cult's tenders safe, and the "
        "Mother keeps the banshees.\n\nRook wants her silenced.",
        [boss("Mother of the Haunt"), k("Haunt Banshee", 8)],
        "She drifts through the Writhing Haunt, and she isn't always there. Thin the banshees while you wait for "
        "her. When she wails, back off and let it pass.",
        "That's one less voice in the Haunt.\n\nI can hear the wind out there now, and I'd forgotten what it sounded "
        "like.",
        [("head", "armor", "mail", "hunter_precise"), ("chest", "armor", "plate", "tank"),
         ("off_hand", "weapon", "tome", "caster")]))

    # ---- Deathguard Captain Ludo Vance
    A(Q("pls_farmer_felstone", "Farmer Felstone", VANCE, 51, 52, "Fieldwatch",
        "The man who owned Felstone Field still walks it. Farmer Felstone was a stubborn man alive, Vance says, "
        "and he's a worse one dead, and he's been killing the patrols that cut across his field with a rusted "
        "scythe.\n\nVance wants him put in the ground he wouldn't leave, and the Felstone Ghouls who work for him "
        "with him.",
        [boss("Farmer Felstone"), k("Felstone Ghoul", 6)],
        "Felstone Field's north of the crossroads. He wanders it, so look for the one with the scythe. He's tougher "
        "than his ghouls, so bring somebody.",
        "Then the field's quiet, for once.\n\nI'd have liked to buy grain off him, once. I suppose that's the "
        "Plaguelands for you.",
        [("main_hand", "weapon", "polearm", "strength"), ("head", "armor", "cloth", "high_healer"),
         ("hands", "armor", "leather", "hunter")], nxt="pls_the_ghost_in_the_barn"))
    A(Q("pls_the_ghost_in_the_barn", "The Ghost in the Barn", VANCE, 53, 53, "Fieldwatch",
        "Nobody goes into the Dalson barn. Vance lost a patrol there, and the one who came out said it was the "
        "father, Joseph Dalson, still looking for his family. The Dalson Ghost keeps the barn, and Dalson's "
        "Skeletons keep the yard.\n\nVance wants it ended, gently if you can.",
        [boss("The Dalson Ghost"), k("Dalson's Skeleton", 8)],
        "The red barn on the Dalson farm. The skeletons walk the yard, and the ghost won't come out of the barn. "
        "It's grieving, not hungry, but it'll kill you just the same.",
        "He's at rest, then. I hope he found them.\n\nSome things out here make you remember you were alive once. "
        "That was one of them.",
        [("chest", "armor", "leather", "wildheart"), ("legs", "armor", "plate", "plate_healer"),
         ("neck", "armor", None, "agility")]))

    # ---- Surgeon Halbert Grey
    A(Q("pls_snapjaw_shell", "Snapjaw Shell", GREY, 52, 52, "Stitchwork",
        "Grey braces broken limbs with plates of turtle shell, and the best shell in the Plaguelands is on the "
        "Darrowmere Snapjaws at the lake. It's hard as iron and it doesn't rot.\n\nHe wants shell plates, the "
        "bigger the better.",
        [fetch("pl_q_snapjaw_plate", 6)],
        "The snapjaws sun themselves on the lake shore south of Sorrow Hill. Go for the legs. The shell's too hard "
        "to cut through, which is the whole point.",
        "Look at the grain on that. That'll hold a femur together for a hundred years.\n\nThere's an old one at the "
        "lake I've wanted for a long time.",
        [("legs", "armor", "mail", "tide_healer"), ("head", "armor", "plate", "strength"),
         ("ranged", "weapon", "wand", "caster")], nxt="pls_old_darrowjaw"))
    A(Q("pls_old_darrowjaw", "Old Darrowjaw", GREY, 53, 54, "Stitchwork",
        "The oldest snapjaw in Darrowmere Lake has a name. Old Darrowjaw has been in the water since before the "
        "plague, and Grey wants his shell, which he says would brace a whole wall. The Darrowmere Snapjaws keep "
        "close to him.\n\nIt's a big turtle, he says, and a very bad-tempered one.",
        [boss("Old Darrowjaw"), k("Darrowmere Snapjaw", 6)],
        "He keeps to the deep end of the lake and comes up when he likes. Thin the young ones while you wait. When "
        "he pulls you under, fight your way back to the shore, and don't panic.",
        "Now that's a shell, a real one.\n\nI'll have the whole Deathguard braced by spring. The newcomers on the hill "
        "keep asking me how we stay on our feet, and now I'll have something to show them.",
        [("chest", "armor", "mail", "earthen"), ("wrist", "armor", "plate", "tank_any"),
         ("main_hand", "weapon", "mace_1h", "high_healer")]))

    # ======================================================================================== SORROW HILL
    # ---- Flamekeeper Rory Callahan
    A(Q("pls_what_we_kill", "What We Kill", RORY, 51, 52, "Flamekeeper's",
        "Rory Callahan wants you to understand the Order's one rule before you wear its flame. They kill the "
        "mindless dead and the fanatics who burn people, and nobody else. The Scarlet Outriders and the Scarlet "
        "Field Chaplains patrol Andorhal, and they burn anything that doesn't pray the way they do.\n\nThat's who "
        "the Order kills.",
        [k("Scarlet Outrider", 8), k("Scarlet Field Chaplain", 6)],
        "The Crusade's patrols come down from Hearthglen and work the north side of Andorhal. They'll be glad to see "
        "you, right up until they see the flame on your shoulder. Don't touch the Forsaken.",
        "That's the job. Some days it's a good one.\n\nI wore that red for a year, you know. I laid steel in Boston "
        "for twenty years, back on Earth, and I'd still rather do that.",
        [("chest", "armor", "plate", "crusader"), ("hands", "armor", "cloth", "caster_crit"),
         ("legs", "armor", "leather", "hunter")], nxt="pls_red_on_the_road"))
    A(Q("pls_red_on_the_road", "Red on the Road", RORY, 52, 52, "Flamekeeper's",
        "The Scarlet Field Chaplains in Andorhal carry orders from Hearthglen, and Rory wants to read them. The "
        "Crusade doesn't send chaplains this far south unless it's planning something.\n\nHe wants a set of their "
        "orders, seal unbroken if you can manage it.",
        [fetch("pl_q_patrol_orders", 1)],
        "Find a chaplain on the north side of Andorhal. They keep their orders in a satchel. Bring them back "
        "sealed, so I can see whose seal it is. Don't open them.",
        "That's Hearthglen's seal, and it's signed by Victor Hale himself.\n\nHe was a security contractor back home. I "
        "served beside him, God help me. If he's sending orders this far south, the Pale Watch needs to know.",
        [("shoulder", "armor", "plate", "tank"), ("feet", "armor", "leather", "healer"),
         ("main_hand", "weapon", "sword_2h", "strength_crit")], nxt="pls_hearthglens_road"))
    A(Q("pls_hearthglens_road", "Hearthglen's Road", RORY, 52, 53, "Flamekeeper's",
        "The orders say the Crusade is moving more patrols down the road from Hearthglen. The Order keeps a watch "
        "on that road, the Pale Watch, a camp in the northern Plaguelands under Watch Captain Lena Fischer.\n\n"
        "Rory wants the orders in her hands before the patrols are.",
        [deliver("pl_q_orders_for_lena", "Bring the Crusade's orders to Watch Captain Lena Fischer at the Pale Watch")],
        "North up the King's Road, through the gate at the top of the map, and keep on toward Hearthglen. The Pale "
        "Watch is a few tents and a banner where the road starts to climb. Lena's the one shouting.",
        "That's Hale's seal, of course it is.\n\nI was a police officer in Hamburg, back home, and I know what a man looks like when "
        "he's getting ready to do something terrible. Stay a while. I could use you up here.",
        [("legs", "armor", "mail", "hunter"), ("head", "armor", "leather", "bear"),
         ("back", "armor", None, "strength")], turn_in_npc_id=LENA,
        grant_items=carry("pl_q_orders_for_lena", "Hale's Orders", "The Crusade's orders from Hearthglen, still "
                                                                   "sealed, wrapped in oilcloth by Rory.")))
    A(Q("pls_the_groundskeeper", "The Groundskeeper", RORY, 54, 54, "Flamekeeper's",
        "Across the lake, Caer Darrow sits in front of Scholomance, where the Cult teaches necromancy to anyone who "
        "asks. Rory wants eyes on the island. Something called the Groundskeeper keeps it, a dead man with a spade, "
        "and the Caer Darrow Ghouls do whatever he tells them.\n\nRory wants him gone, so the Order can watch "
        "Scholomance's door.",
        [boss("The Groundskeeper"), k("Caer Darrow Ghoul", 8)],
        "Caer Darrow's the island in the east of the lake. Cross where the water's shallow. The Groundskeeper walks "
        "the grounds and the ghouls dig for him. He's strong, so go in with friends.",
        "Then the island's watched, and the Cult knows it.\n\nScholomance can wait. We'll be ready for it when it's "
        "time.",
        [("chest", "armor", "plate", "strength"), ("waist", "armor", "cloth", "high_healer"),
         ("ranged", "weapon", "bow", "hunter")]))

    # ---- Drillmaster Kofi Mensah
    A(Q("pls_steel_for_sorrow_hill", "Steel for Sorrow Hill", KOFI, 51, 52, "Drillyard",
        "Drillmaster Kofi Mensah trains the Order's recruits, and the recruits keep breaking their swords. The "
        "Andorhal Skeletons carry the old Lordaeron infantry's blades, and Rory says the steel under the rust is "
        "better than anything they can buy.\n\nKofi wants the blades for the forge.",
        [fetch("pl_q_andorhal_blade", 8)],
        "The skeletons are all over Andorhal. Most of them still carry a sword. Bring them back rusted, and Rory will "
        "make them good again. Don't bother cleaning them.",
        "That's a month of drills that won't end with somebody holding half a sword.\n\nI taught PE in Kumasi, back home. "
        "This is the same job, mostly, with more swords.",
        [("hands", "armor", "mail", "mail_caster"), ("feet", "armor", "plate", "strength"),
         ("back", "armor", None, "agility")], nxt="pls_archers_on_the_wall"))
    A(Q("pls_archers_on_the_wall", "Archers on the Wall", KOFI, 52, 52, "Drillyard",
        "Kofi takes the recruits into Andorhal to learn, and the Andorhal Skeletal Archers on the broken walls keep "
        "putting arrows into them. He'd like the walls cleared before the next lesson.",
        [k("Andorhal Skeletal Archer", 8)],
        "The archers stand on what's left of Andorhal's walls. Close the distance fast, because they won't. When "
        "you're done, I'll bring the recruits.",
        "They came back with no arrows in them today. That's a first.\n\nThere's something bigger in the city, "
        "and I'd like it gone too.",
        [("head", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "shadow"),
         ("main_hand", "weapon", "staff", "bear_weapon")], nxt="pls_the_abominations"))
    A(Q("pls_the_abominations", "The Abominations", KOFI, 53, 53, "Drillyard",
        "The Andorhal Abominations are the Scourge's stitched brutes, sewn together from whatever was lying around. "
        "Kofi wants them dead, and he wants their stitching. The thread that holds them together is tougher than "
        "wire, and the Order's armourers can use it.",
        [k("Andorhal Abomination", 6), fetch("pl_q_stitching", 5)],
        "They lumber around the middle of Andorhal. They're slow and they hit like a cart. Cut the thread out "
        "afterward, and wash your hands.",
        "That's some ugly thread. Thank you, I think.\n\nThe recruits can do the rest of Andorhal. You've earned a "
        "rest.",
        [("chest", "armor", "leather", "feral"), ("shoulder", "armor", "cloth", "healer"),
         ("main_hand", "weapon", "sword_2h", "tank_weapon")]))
    A(Q("pls_shades_of_caer_darrow", "Shades of Caer Darrow", KOFI, 53, 54, "Drillyard",
        "When Rory sent scouts toward Caer Darrow, the Caer Darrow Shades came off the island and over the water "
        "after them. Kofi lost a recruit that night.\n\nHe wants the shades destroyed.",
        [k("Caer Darrow Shade", 8)],
        "The shades drift on Caer Darrow, the island in the east of the lake, and on the water around it. They're "
        "cold to the touch, so wrap up warm. Don't let them get behind you.",
        "That's for Teodora. She was nineteen, and she'd only been here since the Integration.\n\nThank you. I'll tell the recruits who did it.",
        [("wrist", "armor", "mail", "tide_healer"), ("hands", "armor", "plate", "tank"),
         ("ring", "armor", None, "hunter_crit")]))

    # ---- Chaplain Odile Marchand
    A(Q("pls_uthers_rest", "Uther's Rest", ODILE, 51, 51, "Tombwatch",
        "Chaplain Odile Marchand keeps the Order's chapel by Uther's Tomb, where the Lightbringer was buried. The "
        "Order didn't build its keep here by accident.\n\nShe asks you to go and stand at the tomb before you do "
        "anything else for the Order, so you know what it's watching over.",
        [explore(115, 143, "Visit Uther's Tomb")],
        "The tomb's just south of the chapel, at the foot of the hill. Take a minute there. It's the quietest place "
        "in the Plaguelands, and I think it's the only one.",
        "It's quiet there, isn't it? Even the dead keep away.\n\nI taught history in Lyon, back on Earth. I never thought I'd be "
        "keeping a legend's grave.",
        [("ring", "armor", None, "spirit_caster"), ("feet", "armor", "mail", "hunter_precise"),
         ("wrist", "armor", "plate", "plate_healer")], nxt="pls_laid_to_rest"))
    A(Q("pls_laid_to_rest", "Laid to Rest", ODILE, 52, 52, "Tombwatch",
        "The Dalsons' farmhands didn't get a burial. They got up instead, and now Dalson's Ghouls and Dalson's "
        "Skeletons work the farm for the Scourge.\n\nOdile wants them put down, and she's asked you to say a word "
        "for each, if you can manage it.",
        [k("Dalson's Ghoul", 8), k("Dalson's Skeleton", 6)],
        "The Dalson farm, with the red barn, north of the road. The ghouls work the yard and the skeletons walk the "
        "fields. Say whatever you like over them. It's the saying that matters.",
        "Thank you. I've added their names to the chapel's book, the ones we know.\n\nThere's somewhere worse "
        "than Dalson's, and I'd like you to see it.",
        [("chest", "armor", "cloth", "caster"), ("legs", "armor", "plate", "strength"),
         ("hands", "armor", "leather", "wildheart")], nxt="pls_the_haunts_banshees"))
    A(Q("pls_the_haunts_banshees", "The Haunt's Banshees", ODILE, 53, 53, "Tombwatch",
        "Odile can hear the Writhing Haunt from the chapel on still nights. The Haunt Banshees wail over the farm "
        "there and the Writhing Crypt Fiends dig under it, and she says the sound gets into the stones.\n\nShe wants "
        "it quiet.",
        [k("Haunt Banshee", 8), k("Writhing Crypt Fiend", 6)],
        "The Writhing Haunt's east of Dalson's, where the trees die. The banshees drift and the fiends come up out "
        "of the ground. Cover your ears, if it helps.",
        "It's quieter tonight. I can hear the wind in the tomb's trees.\n\nThank you. Rest here, if you like. The "
        "chapel's warm.",
        [("shoulder", "armor", "mail", "earthen"), ("head", "armor", "cloth", "caster_crit"),
         ("off_hand", "weapon", "shield", "mail_caster")]))

    A(Q("pls_darrowmeres_drowned", "Darrowmere's Drowned", ODILE, 53, 53, "Tombwatch",
        "Odile walks down to Darrowmere Lake in the evenings, and the Drowned Lakewalkers walk up out of it to meet "
        "her. They're the people of Caer Darrow, she thinks, who went into the water when the plague crossed the "
        "lake and never came out.\n\nShe wants them laid to rest, and the shore made safe for the Order's camps.",
        [k("Drowned Lakewalker", 10)],
        "South and east, down past the tomb to the lake. They come out of the shallows. Stay on the shore if you "
        "can, because they're stronger in the water.",
        "I'll say their names tonight, the ones Ser Aldren remembers.\n\nWe had a lake at home too, Lac d'Annecy. "
        "I used to swim in it every summer. I don't think I'll swim in this one.",
        [("shoulder", "armor", "leather", "bruiser"), ("feet", "armor", "cloth", "caster"),
         ("main_hand", "weapon", "axe_1h", "wildheart")]))

    # ---- Innkeeper Priya Raman
    A(Q("pls_bear_stew", "Bear Stew", PRIYA, 51, 52, "Sorrow Hill",
        "Innkeeper Priya Raman feeds everyone at Sorrow Hill, and she's out of meat. The Diseased Black Bears are "
        "sick, but not all the way through, and she's found that a cut from the back of the leg comes out clean.\n\n"
        "She wants enough for a stew that'll feed the hill.",
        [fetch("pl_q_bear_flank", 6)],
        "The bears keep to the trees along the King's Road. Cut from the back of the leg, where it's still red. If "
        "it's grey, leave it.",
        "Oh, that's lovely, that's dinner for a week.\n\nI ran a restaurant in Leicester, back home. My mother's recipe works on "
        "bear, it turns out. She'd laugh herself silly.",
        [("legs", "armor", "leather", "agility"), ("chest", "armor", "mail", "tide_healer"),
         ("feet", "armor", "plate", "tank")], nxt="pls_letters_home"))
    A(Q("pls_letters_home", "Letters Home", PRIYA, 52, 53, "Sorrow Hill",
        "Nobody knows where anybody ended up after the Integration, and the people at Sorrow Hill write letters "
        "anyway. Priya keeps the bundle. The transplants at Sun Rock Retreat in Stonetalon pass letters along to "
        "Kalimdor's camps, and a geologist there, Dr. Hannah Lindqvist, keeps a list of names.\n\nPriya wants the "
        "bundle in Hannah's hands.",
        [deliver("pl_q_letter_bundle", "Bring the bundle of letters to Dr. Hannah Lindqvist at Sun Rock Retreat")],
        "Tirisfal, the zeppelin to Orgrimmar, and a wind rider to Sun Rock in Stonetalon. Hannah's the one with the "
        "maps of the volcano. Please don't lose any of them.",
        "So many of them. Let me see whose names I've got.\n\nThere's one here for a woman in Ratchet I wrote down "
        "last month. I'll make sure this gets to her. That's one, at least.",
        [("neck", "armor", None, "spirit_caster"), ("hands", "armor", "leather", "healer"),
         ("main_hand", "weapon", "polearm", "agility")], turn_in_npc_id=HANNAH,
        grant_items=carry("pl_q_letter_bundle", "Bundle of Letters", "A thick bundle of letters tied with kitchen "
                                                                     "string, addressed to people nobody has seen in "
                                                                     "three years.")))

    # ---- Roostkeeper Anders Holm
    A(Q("pls_clear_skies", "Clear Skies", ANDERS, 51, 52, "Roostkeeper's",
        "Roostkeeper Anders Holm keeps the Order's hawks, and the Plaguewing Vultures have started going after them "
        "in the air. He's lost two birds this week.\n\nHe wants the vultures cleared out of the sky over the hill.",
        [k("Plaguewing Vulture", 10)],
        "They circle over everything dead, which out here is most of the map. The ones nearest the hill are the "
        "ones that matter. Shoot them down if you can, and don't let them settle on the roost.",
        "That's much better, and my birds will fly tomorrow.\n\nI kept pigeons in Bergen when I was a boy, back on Earth. Hawks are harder, "
        "and they're worth it.",
        [("shoulder", "armor", "leather", "hunter_crit"), ("waist", "armor", "plate", "tank"),
         ("back", "armor", None, "caster")], nxt="pls_jesses_for_the_hawks"))

    A(Q("pls_jesses_for_the_hawks", "Jesses for the Hawks", ANDERS, 52, 52, "Roostkeeper's",
        "Anders ties his hawks with jesses, leather straps on their legs, and the plague rots leather. The "
        "Plague-Ridden Wolves in the fields carry good sinew under the rot, if you cut carefully, and sinew "
        "doesn't rot the way leather does.\n\nHe wants enough to rig every bird on the roost.",
        [fetch("pl_q_clean_sinew", 8)],
        "The wolves run the grass either side of the King's Road. Cut the sinew from the back legs, where the "
        "plague's slowest. Not all of them will have any worth taking.",
        "That's good sinew, and that's every bird on the roost tied properly.\n\nWe used gut string for the pigeons "
        "when I was a boy. It turns out it's the same knot.",
        [("hands", "armor", "plate", "tank"), ("chest", "armor", "cloth", "spirit_caster"),
         ("waist", "armor", "leather", "agility")]))

    # ---- Scout Agata Wrobel
    A(Q("pls_eyes_on_andorhal", "Eyes on Andorhal", AGATA, 52, 52, "Pathfinder's",
        "Scout Agata Wrobel is back on her feet after the Monastery's cells, and she wants to work. She needs "
        "someone to walk into Andorhal with her eyes and come back out. Rory wants to know where the Crusade's "
        "patrols cross the Scourge's.\n\nShe wants you to stand in the middle of the city and see who's there.",
        [explore(57, 117, "Look over the middle of Andorhal")],
        "Andorhal's south of the crossroads. Get to the middle of the city, by the old town hall, and look around. "
        "Count the red and count the dead, and then get out.",
        "So it's red to the north and dead to the south, and they meet in the square. That's useful to know.\n\nI was a mountain "
        "guide in the Tatras, back home. Getting people in and out of places is the only thing I was ever good at.",
        [("feet", "armor", "leather", "assassin"), ("head", "armor", "plate", "crusader"),
         ("wrist", "armor", "cloth", "healer")], nxt="pls_the_survey_map"))
    A(Q("pls_the_survey_map", "The Survey Map", AGATA, 52, 53, "Pathfinder's",
        "The Crusade's Scarlet Outriders carry a surveyor's map of Andorhal, with every Scourge strong point marked "
        "and every Forsaken one too. Agata wants it. If the Crusade knows where everyone is, the Order should know "
        "it too.",
        [fetch("pl_q_survey_map", 1)],
        "The outriders patrol the north side of Andorhal. One of them carries the map in a leather tube. Bring it "
        "back dry, and don't let them burn it.",
        "Look at this. They've marked the Bulwark's patrols to the hour.\n\nRory needs to see this, and then Venn "
        "does, whether she likes us or not.",
        [("chest", "armor", "mail", "hunter"), ("legs", "armor", "cloth", "caster_crit"),
         ("main_hand", "weapon", "mace_1h", "strength")]))

    # ---- Ser Aldren Holt
    A(Q("pls_the_fallen_of_andorhal", "The Fallen of Andorhal", ALDREN, 52, 53, "Holt's",
        "Ser Aldren Holt commanded an infantry company in Andorhal when the plague came. His men are the Andorhal "
        "Skeletons now, and some of them still wear the company's iron rings.\n\nHe wants the rings back. He means "
        "to bury them at the tomb, since he can't bury the men.",
        [fetch("pl_q_company_ring", 6)],
        "My company held the west end of Andorhal. The skeletons there were my men. Not all of them still have "
        "their rings. Bring me what you find, and forgive me for asking. I don't ask lightly.",
        "That's Corporal Brask's, and that's Hask's, and this one was little Tom Barrow's. He lied about his age.\n\nI'll bury them by the tomb in the "
        "morning. Thank you. I mean that more than you know.",
        [("hands", "armor", "plate", "strength_crit"), ("shoulder", "armor", "leather", "agility"),
         ("off_hand", "weapon", "tome", "high_healer")], nxt="pls_the_necrolytes"))
    A(Q("pls_the_necrolytes", "The Necrolytes", ALDREN, 53, 53, "Holt's",
        "Aldren buried his company's rings by Uther's Tomb, and then he asked who raised his men in the first "
        "place. The Cauldron Necrolytes at the Dalson farm learned their trade in Andorhal.\n\nHe wants them "
        "dead, and he's not ashamed to say it's personal.",
        [k("Cauldron Necrolyte", 8)],
        "They stir the cauldron at the Dalson farm north of the road. They'll raise anything that falls near them, "
        "so fight them away from the ghouls.",
        "That's some justice, at least. Not much, but some.\n\nThe Crusade told me this would feel like holiness. "
        "It doesn't feel like that at all. It feels like tidying up.",
        [("legs", "armor", "mail", "earthen"), ("waist", "armor", "leather", "feral"),
         ("main_hand", "weapon", "axe_2h", "strength")]))

    # ---- the Writhing Deep, the cave under the Writhing Haunt (tools/handbuilt_plaguelands_caves.py)
    A(Q("pls_under_the_haunt", "Under the Haunt", AGATA, 53, 54, "Scout's",
        "Scout Agata Wrobel has been watching the Writhing Haunt for the Order, and she's found a hole behind it "
        "that the crypt fiends keep crawling in and out of. She's been down far enough to know it doesn't stop.\n\n"
        "She wants the Writhing Burrowers and the Brood Guardians thinned out, so the Order can see what's at the "
        "bottom.",
        [k("Writhing Burrower", 10, WD), k("Brood Guardian", 6, WD)],
        "The cave mouth's behind the Writhing Haunt, out east of the road. It's a web of tunnels down there and they "
        "all lead back to the middle. Keep your back to a wall, because the burrowers come up out of the floor.",
        "That's the outer burrows quiet, then.\n\nI used to take tourists down caves in the Tatras, and not one of "
        "them ever tried to eat me. There's a chamber in the middle that everything was guarding, and I think we "
        "both know what's in it.",
        [("legs", "armor", "leather", "feral"), ("hands", "armor", "cloth", "shadow"),
         ("waist", "armor", "plate", "strength")], nxt="pls_the_broodlord"))
    A(Q("pls_the_broodlord", "The Broodlord", AGATA, 54, 55, "Scout's",
        "In the middle of the Writhing Deep, where every tunnel meets, Broodlord Szarak sits on the brood. Off the "
        "north rim there's a pocket of web that Agata won't go near, and she says The Silken Bride lives in it.\n\n"
        "She wants them both dead before the brood hatches.",
        [boss("Broodlord Szarak", WD), boss("The Silken Bride", WD)],
        "The broodlord's in the chamber in the middle, and the bride's up in the north-east, at the end of a "
        "tunnel off the outer ring. Bring something for poison, because she bites and it doesn't wear off.",
        "Then that's the brood finished, and the Haunt's lost its nursery.\n\nI've been in a cell and I've been in "
        "a web now. I'm not sure which I liked less. Here, take this, you've earned it.",
        [("chest", "armor", "mail", "hunter_crit"), ("head", "armor", "leather", "healer"),
         ("main_hand", "weapon", "staff", "fire")]))

    # ---- in from outside the Plaguelands: Undercity, Brill and Tarren Mill
    A(Q("pls_samples_for_the_bulwark", "Samples for the Bulwark", MARWEN, 51, 52, "Apothecary's",
        "Apothecary Marwen has read every report the Bulwark's sent back to Undercity, and she doesn't believe half "
        "of them. Apothecary Dorian Vesk says the plague in the western fields has changed, and she wants him to "
        "prove it.\n\nShe's packed a case of clean reagents for his tests and needs it carried to the Bulwark.",
        [deliver("pl_q_marwens_case", "Bring Marwen's reagent case to Apothecary Dorian Vesk at the Bulwark")],
        "Up through the Ruins and east across Tirisfal to the wall at the end of the road. That's the Bulwark. "
        "Don't open the case, because I've counted every vial and I'll know.",
        "Marwen's actually sent me clean reagents, and I didn't think she had any.\n\nShe thinks I'm wrong about the plague. She'll "
        "read my next report a lot more carefully once these tell her I'm right. Stay a while, because the fields "
        "need hands more than I need a courier.",
        [("wrist", "armor", "cloth", "caster"), ("feet", "armor", "leather", "agility"),
         ("back", "armor", None, "tank_any")], zone=UC, turn_in_npc_id=VESK,
        grant_items=carry("pl_q_marwens_case", "Marwen's Reagent Case", "A small locked case of glass vials packed "
                          "in straw, every one labelled in a precise hand.")))
    A(Q("pls_hands_for_sorrow_hill", "Hands for Sorrow Hill", WEXLEY, 51, 52, "Crier's",
        "Crier Wexley cries what Brill needs to hear, and lately that's a notice from the Order of the Pale Flame. "
        "They're asking for fighters at Sorrow Hill, in the Western Plaguelands, and they don't care where anyone "
        "was born.\n\nWexley's been asked to send the notice on with anyone who looks like they can swing a sword.",
        [deliver("pl_q_order_notice", "Bring the Order's notice to Drillmaster Kofi Mensah at Sorrow Hill")],
        "East through Tirisfal to the Bulwark, then south past it to the hill with the tomb on top. Sorrow Hill's "
        "the keep beside it. The Deathguard at the wall won't stop you, but they'll want to know where you're going.",
        "So Wexley sent you with the notice. He cries it twice a day in Brill, and nobody's told him to stop "
        "yet.\n\nI'm glad you came. "
        "Half my recruits walked out of the Crusade and the other half walked in off the road, so you'll fit in "
        "whatever you are. Go and see Rory when you've found a bunk.",
        [("shoulder", "armor", "plate", "tank"), ("hands", "armor", "mail", "earthen"),
         ("ring", "armor", None, "spirit_caster")], zone="brill", turn_in_npc_id=KOFI,
        grant_items=carry("pl_q_order_notice", "The Order's Notice", "A notice in a firm hand under a pale flame: "
                          "fighters wanted at Sorrow Hill, no questions asked about where you were born.")))
    A(Q("pls_a_chaplains_letter", "A Chaplain's Letter", EWEN, 51, 52, "Chaplain's",
        "Chaplain Ewen Blackwood still prays in Tarren Mill, and he's heard there's another chaplain who still prays "
        "at Uther's Tomb. Chaplain Odile Marchand keeps the tomb for the Order of the Pale Flame.\n\nHe's written her "
        "a letter. He's never met her, and he says that's the best reason to write.",
        [deliver("pl_q_blackwoods_letter", "Bring Chaplain Blackwood's letter to Chaplain Odile Marchand at Uther's "
                 "Tomb")],
        "The road north is shut, so go round through Tirisfal and east to the Bulwark. Uther's Tomb is on the hill "
        "south of the wall, beside Sorrow Hill. I'd take it myself, but somebody's got to keep the chapel open.",
        "A letter from Tarren Mill, from a chaplain I've never met.\n\nHe asks whether I'm afraid the Light will stop "
        "answering. I'm not, and I'm going to write back and tell him so properly. Thank you for carrying it all "
        "this way.",
        [("neck", "armor", None, "holy"), ("legs", "armor", "mail", "tide_healer"),
         ("off_hand", "weapon", "shield", "shield_tank")], zone="tarren_mill", turn_in_npc_id=ODILE,
        grant_items=carry("pl_q_blackwoods_letter", "Chaplain Blackwood's Letter", "A letter sealed with plain "
                          "candle wax, addressed in careful capitals to the chaplain at Uther's Tomb.")))
    return out
