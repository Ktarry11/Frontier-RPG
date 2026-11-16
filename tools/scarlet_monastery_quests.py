"""
The Scarlet Monastery's quests, given in town (Brill, the Undercity and Tarren Mill), never at the door. Levels 28-42,
with one last step at 50 that carries the Order of the Pale Flame's thread on to Sorrow Hill. Read by
tools/build_scarlet_monastery_quests.py, which holds them to the Stonetalon pass's rules before anything is written.

WHAT THE MONASTERY IS ABOUT. The Scarlet Crusade's oldest house, a day's ride from Brill. Since the Integration the
Crusade has taken in transplants too, and some of the worst of it now speaks with accents nobody in Lordaeron ever
heard: an archivist keeping a ledger of everyone the Crusade has burned, a drill instructor turning farm boys into
fodder, a preacher filling the nave. The Order of the Pale Flame walked out of that Crusade. Their man in Brill is
watching the Monastery, and he wants three things out of it: a scout of theirs, a book of names, and the captain who
burned a transplant camp the night Rory Callahan left.

  BRILL (5)          Flamewarden Teodor Novak (the Order's chain, one quest a wing and the last at Sorrow Hill),
                     Gravedigger Hollis (the Monastery's dead).
  THE UNDERCITY (5)  Deathstalker Rhyne (the Crusade's leaders and its champion), Master Apothecary Sable
                     (Thalnos's blood), Loremaster Sennarath (Doan's codex), Apothecary Marwen (the Crusade's zeal).
  TARREN MILL (3)    Commander Thorne (Brennan's recruits), Scout Vask (Loksey's hounds), Chaplain Blackwood (the
                     preacher in the nave).
  KALIMDOR (4)       Merrow Vane at Sun Rock (a letter that starts you on Novak's road), Spirit-Walker Enu at
                     Freewind (the wraith in the burial ground), the warrior trainer in Orgrimmar (the Crusade's
                     master-at-arms), Corwin Hale at the Crossroads (his family's locket in the gallery).
  BACK WEST (1)      Sennarath sends the chapter of Doan's codex on the walking dead to Spiritwalker Tohana at Sun
                     Rock, who has been watching the dead rise in Mulgore.

WHO KNOWS WHAT (Kyle, 16 Nov 2026): every transplant knows they came from Earth; ordinary Azerothians don't, and
only the people at the top know more. So Novak and the Crusade's transplants talk about home freely, while Hollis,
Thorne, Blackwood, Vask and Marwen call them newcomers and never say Earth. Rhyne serves the Dark Lady and knows
more than he says.

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

G, L, A, C = ("scarlet_monastery:_graveyard", "scarlet_monastery:_library", "scarlet_monastery:_armory",
              "scarlet_monastery:_cathedral")
BR, UC, TM, WS = "brill", "undercity", "tarren_mill", "western_plaguelands_south"
# Kalimdor (Kyle, 16 Nov 2026: "You can have some SM quests from kalimdor too around appropriate levels" and "I want
# more links between EK and Kalimdor")
SR, FP, OG, XR = "sun_rock_retreat", "freewind_post", "orgrimmar", "crossroads"

# ---- the people
NOVAK = "brill_pf_flamewarden"                 # new (tools/build_scarlet_monastery_quests.NEW_NPCS)
HOLLIS = "brill_gravedigger"
RHYNE, SABLE, SENNARATH, MARWEN = "uc_deathstalker", "uc_master_apothecary", "uc_scholar", "uc_apothecary"
THORNE, VASK, BLACKWOOD = "tarren_mill_commander", "tarren_mill_scout", "tarren_mill_chaplain"
RORY = "wpl_pf_flamekeeper"
MERROW, ENU, GROMSHADOW, HALE, TOHANA = ("sr_forsaken_apothecary", "fw_spirit_walker", "org_warrior_trainer",
                                         "crossroads_human_traveler", "sr_spirit_walker")

HUB_GIVERS = {NOVAK, HOLLIS, RHYNE, SABLE, SENNARATH, MARWEN, THORNE, VASK, BLACKWOOD, MERROW, ENU, GROMSHADOW,
              HALE}


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Scarlet Torturer": [("sm_q_scarlet_zeal", "Vial of Zeal", "A stoppered vial of the oil the Crusade anoints "
                                                               "its faithful with. It smells of incense and hot iron.",
                          0.75)],
    "Scarlet Scryer": [("sm_q_scarlet_zeal", "Vial of Zeal", "A stoppered vial of the oil the Crusade anoints its "
                                                             "faithful with. It smells of incense and hot iron.", 0.75)],
    "Bloodmage Thalnos": [("sm_q_thalnos_blood", "Thalnos's Bloodstone", "A stone the size of an egg, dark red and "
                                                                       "warm. Something inside it beats, very slowly.",
                           1.0)],
    "Archivist Dana Mercer": [("sm_q_ledger_of_names", "The Ledger of Names", "A thick ledger in a careful hand. "
                               "Every line is a name, a date and a place, and what the Crusade did there.", 1.0)],
    "Arcanist Doan": [("sm_q_doans_codex", "Doan's Codex", "A heavy codex bound in red leather, its margins crowded "
                                                           "with notes in Doan's tiny hand.", 1.0)],
    "Smithmaster Corra Bellweather": [("sm_q_tempering_notes", "Bellweather's Tempering Notes", "A smith's notebook, "
                                       "black with soot. The Crusade's whole armoury is in here, piece by piece.",
                                       1.0)],
    "Curator Halbrecht": [("sm_q_hale_locket", "The Hale Locket", "A silver locket on a broken chain, engraved with "
                                                               "a ship and the name Hale. There's a lock of a "
                                                               "child's hair inside.", 1.0)],
    "Captain Elric Stane": [("sm_q_stanes_signet", "Stane's Signet", "A heavy signet ring with the Crusade's flame "
                                                                    "on it, worn smooth on one side.", 1.0)],
}

#: monster-drop quest starters (none here)
STARTER_DROPS = {}
STARTER_IDS = {}


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards, nxt=None, zone=BR, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def build():
    out = []
    A_ = out.append

    # ==================================================================================== THE ORDER'S CHAIN (Brill)
    A_(Q("sm_the_scout_in_the_cells", "The Scout in the Cells", NOVAK, 28, 30, "Pale Flame",
         "Flamewarden Teodor Novak keeps a room over the inn in Brill and a window that looks east, toward the "
         "Scarlet Monastery. He's with the Order of the Pale Flame, the ones who walked out of the Crusade, and "
         "he's lost a scout. Her name's Agata, and the Crusade took her on the road a week ago.\n\nHe says they'll "
         "have taken her down into the Graveyard, to the Chamber of Atonement, where Interrogator Maelis does "
         "his work. Agata won't have talked. He wants Maelis dead before she has to.",
         [boss("Interrogator Maelis", G)],
         "The Monastery's at the top of the road east out of Brill. Go in through the gate, and the Graveyard's "
         "down through the crypt chapel on the west side of the close. Maelis keeps to the torture room at the "
         "bottom of the halls. If Agata's alive, tell her Teo sent you, and she'll know you're one of ours.",
         "She was alive, then, and she's on her way here. Thank you.\n\nI was a firefighter in Brno before all "
         "this. You learn to count who comes out. I'm still counting.",
         [("chest", "armor", "leather", "agility"), ("wrist", "armor", "cloth", "healer"),
          ("hands", "armor", "plate", "tank")],
         nxt="sm_a_book_of_names"))
    A_(Q("sm_a_book_of_names", "A Book of Names", NOVAK, 32, 35, "Pale Flame",
         "Agata heard things in the cells. The Crusade has an archivist in the Library, a woman they call Archivist Dana "
         "Mercer, and she writes everything down: every camp the Crusade has burned, every name, every date. "
         "She was a records clerk back home, Agata says, and she's very good at it.\n\nNovak wants that ledger. "
         "There are families from home looking for people who were in those camps, and the Order owes them an "
         "answer, even a bad one.",
         [boss("Archivist Dana Mercer", L), fetch("sm_q_ledger_of_names", 1)],
         "Mercer keeps to the Closed Stacks, off the long hall that turns north in the Library. She'll shut "
         "your casters down if she can, so bring someone who hits things. The ledger doesn't leave her desk.",
         "That's her hand. I knew a few of these camps.\n\nI'll copy it out for the Flamekeeper, and then I'll "
         "start writing letters. Some of these people have been waiting three years.",
         [("head", "armor", "cloth", "caster"), ("legs", "armor", "mail", "hunter"),
          ("ring", "armor", None, "strength")],
         nxt="sm_cold_steel"))
    A_(Q("sm_cold_steel", "Cold Steel", NOVAK, 35, 37, "Pale Flame",
         "The ledger says where the Crusade sends its armour, and it's all made in one place: the forge off the "
         "Crusader's Armory in the Monastery, where Smithmaster Corra Bellweather works day and night.\n\n"
         "Novak wants her notebook. If the Order knows what the Crusade wears, the Order knows where it's thin.",
         [boss("Smithmaster Corra Bellweather", A), fetch("sm_q_tempering_notes", 1)],
         "The Armory's the middle door under the Monastery's front. Go through the Training Grounds and the two "
         "armouries, and the forge is up the short passage off the Crusader's Armory. She tempers her plate "
         "while you hit her, so don't let it pile up.",
         "Every buckle and rivet. She was thorough.\n\nThe Flamekeeper's going to like this. He was an "
         "ironworker in Boston, and he'll read it the way other men read letters from home.",
         [("shoulder", "armor", "plate", "strength"), ("feet", "armor", "leather", "bear"),
          ("main_hand", "weapon", "mace_1h", "caster")],
         nxt="sm_the_captain_of_the_doors"))
    A_(Q("sm_the_captain_of_the_doors", "The Captain of the Doors", NOVAK, 38, 40, "Pale Flame",
         "Novak has never told anyone in Brill why the Order left the Crusade, and he tells you now. The night "
         "Rory Callahan walked out, the Crusade burned a camp of transplants on the Darrowmere road for "
         "consorting with the dead. The man who gave the order was Captain Elric Stane, and he captains the Chapel "
         "Guard at the Cathedral's doors today.\n\nNovak doesn't want an apology. He wants Stane's signet, so "
         "the Flamekeeper knows it's done.",
         [boss("Captain Elric Stane", C), fetch("sm_q_stanes_signet", 1)],
         "The Cathedral's the right-hand door. Cross the Chapel Gardens and go up the steps, and Stane stands "
         "at the top. He'll call his centurions to him, so deal with them first or they'll bury you.",
         "That's the ring. I've seen it on his hand in a doorway with the fire behind him.\n\nTake it to Rory "
         "yourself. He should hear it from the one who did it.",
         [("chest", "armor", "mail", "tide_healer"), ("waist", "armor", "plate", "plate_healer"),
          ("off_hand", "weapon", "shield", "mail_caster")],
         nxt="sm_the_flamekeepers_due"))
    A_(Q("sm_the_flamekeepers_due", "The Flamekeeper's Due", NOVAK, 50, 51, "Pale Flame",
         "Novak wants Stane's signet put into Flamekeeper Rory Callahan's hand at Sorrow Hill, in the Western "
         "Plaguelands, where the Order keeps its hall by Uther's Tomb.\n\nThe road there runs past the Bulwark "
         "and into country that kills people who aren't ready for it. Novak says to wait until you are, and "
         "then to go.",
         [deliver("sm_q_stanes_signet_carried", "Bring Stane's signet to Flamekeeper Rory Callahan at Sorrow Hill")],
         "Out the east gate of Tirisfal, past the Bulwark, and keep to the King's Road until you see the hill "
         "with the chapel on it. Don't go before you're ready. I mean that.",
         "That's Elric Stane's ring.\n\nI stood next to him for a year, God help me, and I never once stopped him. "
         "Sit yourself down, because there's a lot of work out here, and the Order could use someone who finishes things.",
         [("back", "armor", None, "caster"), ("neck", "armor", None, "physical"),
          ("ring", "armor", None, "healer")],
         turn_in_npc_id=RORY,
         grant_items=carry("sm_q_stanes_signet_carried", "Stane's Signet", "Captain Elric Stane's signet ring, "
                                                                          "wrapped in a scrap of Novak's shirt.")))

    # ==================================================================================== BRILL
    A_(Q("sm_the_monasterys_dead", "The Monastery's Dead", HOLLIS, 28, 30, "Gravedigger's",
         "Gravedigger Hollis has buried half of Brill, some of them twice. The burial ground at the Scarlet "
         "Monastery was Lordaeron's before it was the Crusade's, and the people in it were somebody's family.\n\n"
         "They don't rest any more. The Anguished Dead claw their way up out of the graves in the Forlorn "
         "Cloister, and the Haunting Phantasms drift among the stones. Hollis wants them laid down, gently if "
         "you can manage it and any way you can if you can't.",
         [k("Anguished Dead", 8, G), k("Haunting Phantasm", 6, G)],
         "Into the Monastery's Graveyard, through the crypt chapel. Past the halls there's an open burial ground "
         "with a mausoleum in the middle. That's where they walk.",
         "Thank you. I'll say a word for them, whatever they were.\n\nThe Crusade calls us abominations, and "
         "then lets its own dead crawl out of the ground. I don't understand them, and I've stopped trying.",
         [("feet", "armor", "cloth", "spirit_caster"), ("wrist", "armor", "mail", "earthen"),
          ("main_hand", "weapon", "staff", "bear_weapon")],
         zone=BR))

    # ==================================================================================== THE UNDERCITY
    A_(Q("sm_hearts_of_zeal", "The Crusade's Zeal", MARWEN, 28, 31, "Apothecary's",
         "Apothecary Marwen wants to know what the Crusade puts in its faithful. The Scarlet Torturers and the "
         "Scarlet Scryers in the Monastery's Graveyard carry little vials of anointing oil, and Marwen thinks "
         "there's more in it than oil.\n\nBring her the vials, and she'll find out what makes a man burn his "
         "neighbours and sing while he does it.",
         [fetch("sm_q_scarlet_zeal", 6)],
         "The Torturers and the Scryers both keep to the halls and the Chamber of Atonement in the Graveyard. "
         "Most of them carry a vial. Don't drink any of it.",
         "Incense, oil, and something bitter under both.\n\nIt's a calming draught, and a strong one. They "
         "keep them calm while they do it. That's worse, somehow.",
         [("hands", "armor", "leather", "hunter"), ("neck", "armor", None, "healer"),
          ("shoulder", "armor", "cloth", "shadow")],
         zone=UC))
    A_(Q("sm_the_bloodmages_stone", "The Bloodmage's Stone", SABLE, 30, 32, "Royal Apothecary",
         "Master Apothecary Lorrane Sable has heard that the Crusade keeps a blood mage in the Graveyard's tomb, "
         "Bloodmage Thalnos, and that he's kept himself alive a long time on other people.\n\nShe wants the stone "
         "he does it with. The Society has its own uses for something that keeps a heart beating.",
         [boss("Bloodmage Thalnos", G), fetch("sm_q_thalnos_blood", 1)],
         "Thalnos holds Honor's Tomb, at the far end of the Graveyard past the open burial ground. His ward drinks "
         "spells, so hit him with steel. The stone will be on him.",
         "It's still warm, and it's still beating.\n\nThe Dark Lady will want to know about this. Leave it with me, and don't "
         "mention it in the tavern.",
         [("legs", "armor", "cloth", "blood"), ("chest", "armor", "plate", "strength"),
          ("ranged", "weapon", "wand", "shadow")],
         zone=UC))
    A_(Q("sm_doans_codex", "Doan's Codex", SENNARATH, 34, 36, "Loremaster's",
         "Loremaster Sennarath collects what the living throw away. Arcanist Doan of the Scarlet Crusade has "
         "spent years in the Athenaeum at the top of the Monastery's Library, writing a codex of everything "
         "he's learned about the dead, and how to end them.\n\nSennarath would like to read it before Doan "
         "uses it on anyone else.",
         [boss("Arcanist Doan", L), fetch("sm_q_doans_codex", 1)],
         "The Athenaeum's the great hall of shelves at the north end of the Library, past the Gallery of "
         "Treasures. When Doan's close to dying, he'll try to take the room with him. Get away from him.",
         "A great deal of this is wrong, and some of it's very, very right.\n\nI'll keep it somewhere safe, "
         "which in this city means somewhere I don't tell anyone about.",
         [("head", "armor", "leather", "wildheart"), ("off_hand", "weapon", "tome", "high_healer"),
          ("waist", "armor", "mail", "mail_caster")],
         zone=UC))
    A_(Q("sm_the_champion_of_the_hall", "The Champion of the Hall", RHYNE, 37, 39, "Deathstalker's",
         "Deathstalker Rhyne keeps a list of the Crusade's people who matter, and Herod is near the top. He's "
         "the Crusade's champion, he holds the Hall of Champions at the back of the Armory, and he's been "
         "sending his trainees down the road to Brill to practise.\n\nRhyne wants that to stop. He doesn't "
         "much care how.",
         [boss("Herod", A)],
         "The Hall of Champions is the last room of the Armory. Herod spins when he's angry, and he gets angry "
         "fast, so keep moving. When he falls, his trainees will come running. Don't stand in the doorway.",
         "That's good news, and the road to Brill will be quieter for it.\n\nThe Crusade has more champions than it has sense. Come "
         "back to me, because I've one more name.",
         [("main_hand", "weapon", "axe_2h", "strength"), ("legs", "armor", "leather", "feral"),
          ("hands", "armor", "mail", "tide_healer")],
         zone=UC, nxt="sm_in_the_name_of_the_light"))
    A_(Q("sm_in_the_name_of_the_light", "In the Name of the Light", RHYNE, 40, 42, "Deathstalker's",
         "The last names on Rhyne's list are the Crusade's in the Monastery: High Inquisitor Whitemane and "
         "Scarlet Commander Mograine, who keep court together in the Cathedral's chancel.\n\nRhyne tells you "
         "plainly that the Dark Lady knows more about the Crusade's newest recruits than the Crusade does, "
         "and that she wants the people giving them orders gone. He won't say more than that.",
         [boss("High Inquisitor Whitemane", C), boss("Scarlet Commander Mograine", C)],
         "Cross the Chapel Gardens, go up the steps, and walk the length of the Crusader's Chapel. They're at "
         "the altar. Mograine gets back up once, and Whitemane will try to put you to sleep. Kill them together.",
         "Then it's done, and the Crusade will have a long, loud argument about who leads it next.\n\nThe Dark "
         "Lady thanks you. I'm told to say that, and this once I mean it.",
         [("head", "armor", "plate", "crusader"), ("shoulder", "armor", "leather", "assassin"),
          ("main_hand", "weapon", "staff", "high_healer")],
         zone=UC))

    # ==================================================================================== TARREN MILL
    A_(Q("sm_the_hounds_of_the_library", "Hounds of the Library", VASK, 32, 34, "Tarren Mill",
         "Scout Mirren Vask lost two scouts on the Hillsbrad road last month, run down by Scarlet hounds. She "
         "tracked the hounds back to the kennels in the Monastery's Library, and to the man who breeds them, "
         "Houndmaster Loksey.\n\nShe wants Loksey dead, and his Scarlet Tracking Hounds with him.",
         [boss("Houndmaster Loksey", L), k("Scarlet Tracking Hound", 6, L)],
         "The kennels are in Huntsman's Cloister, the square of grass at the top of the Library's long halls. "
         "Kill the hounds before you go for Loksey, because they'll lick his wounds closed if you don't.",
         "Then it's done. I'll tell their families it was dogs, and that the dogs are gone.\n\nIt's not much. It's what "
         "I've got.",
         [("ranged", "weapon", "bow", "hunter_crit"), ("waist", "armor", "leather", "bruiser"),
          ("feet", "armor", "mail", "hunter")],
         zone=TM))
    A_(Q("sm_drilled_to_die", "Drilled to Die", THORNE, 35, 37, "Tarren Mill",
         "Commander Vellis Thorne has been finding Scarlet Soldiers dead in the hills, boys from Southshore "
         "barely old enough to lift a sword. The Crusade drills them in the Training Grounds of the Monastery's "
         "Armory, and the man doing the drilling is one of the newcomers, a Sergeant Major Cole Brennan.\n\nThorne "
         "says Brennan's very good at it. He wants Brennan dead and the yard emptied of Scarlet Soldiers.",
         [boss("Sergeant Major Cole Brennan", A), k("Scarlet Soldier", 8, A)],
         "The Armory's the middle door under the Monastery's front, and the Training Grounds are the open yard "
         "just inside. Brennan calls his recruits in waves. Don't let them surround your healer.",
         "The newcomers brought a lot of things with them. Some of them brought this, apparently.\n\nI'd "
         "rather fight soldiers than children. Thank you for making that likelier.",
         [("legs", "armor", "plate", "tank"), ("chest", "armor", "cloth", "frost"),
          ("main_hand", "weapon", "polearm", "agility")],
         zone=TM))
    A_(Q("sm_the_preacher_in_the_nave", "The Preacher in the Nave", BLACKWOOD, 39, 41, "Chaplain's",
         "Chaplain Ewen Blackwood keeps the Forsaken chapel in Tarren Mill, and he still prays, which makes him "
         "strange even here. He's heard about a preacher in the Scarlet Cathedral, Brother Corwin Ashe, one of "
         "the newcomers, who fills the nave every night and sends the faithful out to burn.\n\nBlackwood says "
         "faith is the one thing he was allowed to keep. He doesn't want to watch it used like that.",
         [boss("Brother Corwin Ashe", C)],
         "The Cathedral's the right-hand door. Go up past the gardens and into the Crusader's Chapel. Ashe "
         "preaches in the middle of the nave. His sermon shields him, so keep at him.",
         "I won't ask how he died. I'll only ask whether he was afraid.\n\nNo, don't tell me. I'll pray for "
         "him either way, because somebody should.",
         [("chest", "armor", "leather", "healer"), ("hands", "armor", "cloth", "holy"),
          ("ring", "armor", None, "agility")],
         zone=TM))

    # ==================================================================================== KALIMDOR
    A_(Q("sm_a_letter_for_brill", "A Letter for Brill", MERROW, 28, 29, "Sun Rock",
         "Apothecary Merrow Vane has a friend in Brill who isn't Forsaken and isn't Horde, and who's never once "
         "asked Merrow what he is. Flamewarden Teodor Novak watches the Scarlet Monastery for an order called "
         "the Pale Flame, and he needs people who can fight.\n\nMerrow has written to him about you. He'd like "
         "you to carry the letter yourself.",
         [deliver("sm_q_merrow_letter", "Bring Merrow's letter to Flamewarden Novak in Brill")],
         "Take the zeppelin from Orgrimmar to Tirisfal and walk down into Brill. Novak keeps a room over the inn. "
         "He's a big man with burn scars on his hands, and he doesn't bite.",
         "That's Merrow's handwriting. He always writes like he's apologising.\n\nHe says you're good. Sit down, and "
         "I'll tell you about the Monastery.",
         [("feet", "armor", "leather", "hunter"), ("wrist", "armor", "plate", "crusader"),
          ("waist", "armor", "cloth", "spirit_caster")],
         zone=SR, turn_in_npc_id=NOVAK,
         grant_items=carry("sm_q_merrow_letter", "Merrow's Letter", "A letter sealed with green wax that smells "
                                                                     "faintly of something medicinal.")))
    A_(Q("sm_the_sleepless", "The Sleepless", ENU, 30, 32, "Freewind",
         "Spirit-Walker Enu has looked for Thunder Bluff's dead and found them quiet. A Forsaken traveller who "
         "came up the ramp told him about a place where the dead are anything but quiet: the burial ground of "
         "the Scarlet Monastery, across the sea in Tirisfal, where a wraith called Azshir the Sleepless feeds on "
         "the spirits of the buried.\n\nEnu says a spirit that's eaten never gets to rest at all. He'd like "
         "Azshir ended, even so far from home.",
         [boss("Azshir the Sleepless", G)],
         "The zeppelins from Orgrimmar go to Tirisfal. From there it's the road east to the Monastery, and down "
         "through the crypt chapel into the Graveyard. Azshir walks the burial ground. Spread out when it wails, "
         "and cleanse the curse it lays on you.",
         "I felt something loosen, I think, a long way off.\n\nThank you. The dead there aren't ours, but the "
         "dead are the dead.",
         [("head", "armor", "mail", "tide_healer"), ("shoulder", "armor", "leather", "bruiser"),
          ("off_hand", "weapon", "shield", "shield_tank")],
         zone=FP))
    A_(Q("sm_the_master_at_arms", "The Master-at-Arms", GROMSHADOW, 38, 39, "Orgrimmar",
         "The warrior trainer in Orgrimmar has heard of a man in the Scarlet Monastery's Armory who has never "
         "lost a duel. They call him Master-at-Arms Dorran Pike, and they say he parries a blade and sends it "
         "back into the one who swung it.\n\nThe trainer would like to know if it's true, and the only way to "
         "know is to go and find out.",
         [boss("Master-at-Arms Dorran Pike", A)],
         "Take the zeppelin to Tirisfal and the road east to the Monastery. The Armory's the middle door. Pike "
         "holds the Crusader's Armory. Bring casters, because steel goes back the way it came.",
         "So it's true, and he's dead. Both are worth knowing.\n\nI'll teach the young ones what you've told "
         "me. Some of them might even listen.",
         [("main_hand", "weapon", "sword_2h", "strength_crit"), ("hands", "armor", "leather", "bear"),
          ("legs", "armor", "cloth", "caster")],
         zone=OG))
    A_(Q("sm_the_hale_locket", "The Hale Locket", HALE, 34, 36, "Crossroads",
         "Corwin Hale left Stormwind for reasons he doesn't talk about, and he took the coast road north to "
         "Lordaeron before he came south to the Barrens. The Crusade stopped him on that road and took "
         "everything he had, including his daughter's locket.\n\nHe's heard it's in a glass case in the "
         "Scarlet Monastery's Gallery of Treasures, which is kept by a Curator Halbrecht. He'd like it back.",
         [boss("Curator Halbrecht", L), fetch("sm_q_hale_locket", 1)],
         "Ride the zeppelin to Tirisfal and take the road east to the Monastery. The Library's the left-hand "
         "door. Halbrecht keeps the Gallery of Treasures past the kennels. He'll call his monks when you start, "
         "so kill them before you kill him.",
         "That's it, and that's her hair, still in it.\n\nShe was six when I left. I don't know where she is now. I "
         "keep thinking that if I've got this, I'll know her when I find her.",
         [("chest", "armor", "mail", "earthen"), ("back", "armor", None, "agility"),
          ("main_hand", "weapon", "dagger", "assassin")],
         zone=XR))
    A_(Q("sm_pages_for_sun_rock", "Pages for Sun Rock", SENNARATH, 36, 37, "Loremaster's",
         "Loremaster Sennarath has read Doan's codex through, and one chapter has troubled him: Doan studied "
         "the dead that rise far from the Scourge, with no necromancer behind them, and he wrote down how it "
         "starts. Sennarath has heard that the dead are rising like that in Mulgore.\n\nHe's copied the chapter "
         "for Spiritwalker Tohana at Sun Rock Retreat, in Stonetalon, who watches that border, and he'd like it "
         "carried.",
         [deliver("sm_q_codex_pages", "Bring the copied chapter to Spiritwalker Tohana at Sun Rock Retreat")],
         "Take the zeppelin to Orgrimmar and a wind rider to Sun Rock. Tohana's the one who talks to spirits. "
         "Tell him the Crusade's arcanist was wrong about a lot of things, but not, I think, about this.",
         "The dead getting up with nobody calling them.\n\nI've watched it happen on the Rim and not known "
         "what I was seeing. Now I've got a name for it, and I wish I didn't.",
         [("wrist", "armor", "leather", "healer"), ("ring", "armor", None, "caster"),
          ("shoulder", "armor", "plate", "tank_any")],
         zone=UC, turn_in_npc_id=TOHANA, requires_quests=["sm_doans_codex"],
         grant_items=carry("sm_q_codex_pages", "Copied Chapter", "A sheaf of pages in Sennarath's neat hand, tied "
                                                                 "with string, titled in Doan's words.")))
    return out
