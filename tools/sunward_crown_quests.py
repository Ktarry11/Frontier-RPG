"""
The Sunward Crown's quests (48-49): the first place the ground, the sky and the Earth people stand together, and it's
gone wrong already. Read by tools/build_sunward_crown_quests.py, which holds them to every rule before anything is
written. The brief is docs/worldtree_brief.md ("Twenty questions"); the maps are
tools/handbuilt_worldtree_sunward_crown.py and tools/handbuilt_worldtree_lenswatch.py.

THE THREADS (Kyle, 20 Nov 2026):
  The war: War-Leader Rakkuzi holds Spearhold for High Chieftain Zan'kaji and wants the Ascendancy off the tree. His
    scouts count the lancers and the humming shield poles on the Taken Crown; his wyvern-rider wants the sky beasts off
    the islets; and the centurion holding the north arm is the war's first real kill.
  The proof: the Ascendancy crashed the parley and each side thinks the other called it down. Envoy Garrok, sent by the
    Warchief to keep the Horde out of a war it doesn't understand, sends you to Speaker Hezza, who stood at the parley;
    Hezza sends you to the wreck and to Ilaren Vey, the scholar who stood across from her; Ilaren reads the legion's own
    orders, and they prove the survey didn't call the soldiers down. Rakkuzi believes it, and still wants his war.
  The survey: the House of the Patient Lens at Lenswatch, where you rest. Its surveyor wants to understand the crown; its
    archivist wants back the pages the Ascendancy took from the stones; its lensmaster wants the cloud measured and the
    storms read; its shipmaster wants the guns on the Chainhold quiet.
  The Earthborn: the Earth people the scholars found on the sky islands, kept at the Annex as guests who can't quite
    leave. Matias Arrieta, three years with the Aetherians, wants to know if they're allowed to go home; Dr. Rania Azar
    learns the sky's medicine; Pavel Novak takes apart Aetherian engineering; Ewan Docherty, who climbed the whole tree,
    maps the islets. Matias and Ilaren are the player's pair of allies, and they don't fully trust each other.
  The seal: the witch doctor sees light leaking up through the cloud, the archivist at the old ring reads warnings cut
    by the Kharad, and the guardians round it are waking. When every side's gathered at the ring, the guns fire, and the
    seal cracks. The Aetherians see there are worse things in the sky than the Ascendancy, Aurelion opens to the ground,
    and the Ascendancy's beachhead has to go so the council's skiff can come down. What's under the seal is a raid,
    later (the Celestial raid, docs/raid_tier1_design.md): nothing here names it.

THE RULES IT KEEPS: no map changes with quests (the crack is in the seal from the start; the quest is the moment it
gives); transplants are factionless (the Earthborn pay nobody); the Aetherians only ever say they don't know what the
change was. VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two
words, the useful thing first, every kill target named, no count beside an objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

SC = "sunward_crown"
LW = "lenswatch"

# ---- Spearhold
RAKKUZI, JINRA, TAZKAL, ZANSHI, GARROK = "sc_warleader", "sc_spear_scout", "sc_wyvern_rider", "sc_witchdoctor", "sc_envoy"
# ---- Lenswatch
DESTREN, TAVIAN, CORYN, HALDANE, SELLIS = "lw_surveyor", "lw_archivist", "lw_lensmaster", "lw_shipwright", "lw_warden"
# ---- the Annex
MATIAS, RANIA, PAVEL, EWAN = "sc_annex_lead", "sc_annex_doctor", "sc_annex_engineer", "sc_climber"
# ---- out on the crown
ZULMO, RANJO, HEZZA, ILAREN, ELYON, MUZZA, SAREN, DAKZIN = ("sc_gatewatch", "sc_lookdown", "sc_parley_troll",
                                                           "sc_parley_scholar", "sc_seal_watcher", "sc_line_scout",
                                                           "sc_dockhand", "sc_falls_hunter")

HUB_GIVERS = {RAKKUZI, JINRA, TAZKAL, ZANSHI, GARROK, DESTREN, TAVIAN, CORYN, HALDANE, SELLIS, MATIAS, RANIA, PAVEL,
              EWAN}
TRIBE_GIVERS = {RAKKUZI, JINRA, TAZKAL, ZANSHI, ZULMO, RANJO, HEZZA, MUZZA, DAKZIN}
HORDE_GIVERS = {GARROK}
SKY_GIVERS = {DESTREN, TAVIAN, CORYN, HALDANE, SELLIS, ILAREN, ELYON, SAREN}


def k(target, n, zone=SC):
    return kill(target, n, zone=zone)


def boss(target, zone=SC):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=SC, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Ascendancy Shield Drone": [("sc_q_shield_focus", "Shield Focus", "A palm-sized lens of blue crystal from an "
                                "Ascendancy Shield Drone. It still hums, and the air in front of it feels thick.")],
    "Ascendancy Legionary": [("sc_q_legion_orders", "Sealed Legion Orders", "A thin plate of crystal etched with "
                              "Aetherian script and sealed with the Ascendancy's sigil. Every legionary carries a "
                              "copy.", 0.6)],
    "Ascendancy Sky Lancer": [("sc_q_brothers_spear", "Highbough Spear", "A troll hunting spear with teal paint on the "
                               "haft, taken as a trophy by a sky lancer.", 0.5)],
    "Ascendancy Bombardier": [("sc_q_survey_page", "Stolen Survey Page", "A page of the survey's records in the Patient "
                               "Lens's tidy hand, creased where a soldier folded it into his pack.")],
    "Ascendancy Artillerist": [("sc_q_survey_page", "Stolen Survey Page", "A page of the survey's records in the Patient "
                                "Lens's tidy hand, creased where a soldier folded it into his pack.")],
    "Waking Guardian": [("sc_q_rune_shard", "Rune-Cut Shard", "A flake of grey stone off a Waking Guardian, cut with "
                         "Kharad runes so small and deep they look like cracks.")],
    "Bolt-Born Elemental": [("sc_q_charged_mote", "Charged Mote", "A bead of light left where a Bolt-Born Elemental "
                             "came apart. It crackles if you bring it near metal.")],
    "Gilded Moth": [("sc_q_gold_dust", "Pinch of Gold Dust", "The fine gold dust off a Gilded Moth's wings, wrapped in "
                     "a leaf. It numbs your fingers.")],
    "Construct Hound": [("sc_q_hound_gyro", "Hound Gyro", "A spinning brass core from a Construct Hound's chest. It "
                         "keeps turning long after the hound's stopped.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [23]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=SC, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
TAKEN_FORT = (136, 42)        # the Ascendancy's fort on the Taken Crown
WRECK = (182, 116)            # the war skiff that came down on the Parley Stones
SEAL_HEART = (176, 66)        # inside the old ring, in front of the seal
HANGAR = (240, 34)            # the Chainhold's lancer hangar
DRIFT_TWO = (187, 224)        # the second Driftlet
DRIFT_THREE = (158, 227)      # the third Driftlet
RIFT_NORTH = (230, 104)       # the tear north of the Annex
RIFT_WEST = (197, 146)        # the tear west of the Annex
RIFT_SOUTH = (262, 154)       # the tear south of the dock
ANCHOR = (104, 56)            # Lenswatch: the gravity anchor that holds the island


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE WAR
    A(Q("scq_every_spear", "Every Spear He Can Get", ZULMO, 48, 48, "Gatewatcher's",
        "Gatewatcher Zul'mo counts every climber who comes up through the old wall. War-Leader Rakkuzi wants every one "
        "of them who can fight sent west to Spearhold.",
        [deliver("sc_q_gate_tally", "Take Zul'mo's tally to War-Leader Rakkuzi at Spearhold")],
        "I tie a knot in this cord for every climber who comes up through the wall, and the war-leader wants to know "
        "how many spears he's got. Take him the tally, and take yourself with it. Spearhold's west of here, at the back "
        "of the crown.",
        "So that's every knot Zul'mo's tied, and you're the newest one.\n\nThat's good, because the sky people's "
        "soldiers fell on our parley, and they're sitting on the north arm of our tree like it's theirs. I need every "
        "spear I can get.",
        turn_in_npc_id=RAKKUZI, nxt="scq_spears_on_the_crown",
        grant_items=carry("sc_q_gate_tally", "Gatewatcher's Tally", "A knotted cord of bark fibre. Every knot is a "
                          "climber who came up through the old wall.")))
    A(Q("scq_spears_on_the_crown", "Spears on the Crown", RAKKUZI, 48, 48, "Spearhold",
        "War-Leader Rakkuzi wants the Ascendancy to learn what the Highbough's spears feel like. Every Ascendancy "
        "Legionary they could spare is holding the line across the north arm.",
        [k("Ascendancy Legionary", 8)],
        "Every Ascendancy Legionary on the north arm is standing in one line with his shield locked, like the tree is "
        "a wall they're guarding. Go up the arm and break that line. I want them to know the Highbough doesn't ask "
        "politely.",
        "They bleed like anyone else, then, and I'd been wondering.\n\nThe envoy from Orgrimmar will tell you that was a "
        "mistake. Go and listen to him if you want, but come back to me when he's finished.",
        nxt="scq_both_sides_of_the_stones"))
    A(Q("scq_count_the_lancers", "Count the Lancers", JINRA, 48, 48, "Lancer-Counter's",
        "Scout Jinra has counted the Ascendancy's lancers twice and come back with a bigger number each time. She wants "
        "someone to go right up to their fort on the Taken Crown and look.",
        [explore(*TAKEN_FORT, "Get inside the Ascendancy's fort on the Taken Crown and count what's there")],
        "I can't get past the humming poles without them seeing me, but you might. Go up the north arm to their fort "
        "on the Taken Crown and get a proper look. Count the tents and count the guns, and don't stop to fight "
        "anything that doesn't stop you first.",
        "Six tents and two of the lightning guns, and a standard as tall as a hut.\n\nThat's more than I counted the "
        "second time. They're not raiding us, they're moving in.",
        nxt="scq_humming_poles"))
    A(Q("scq_humming_poles", "The Humming Poles", JINRA, 48, 49, "Polebreaker's",
        "The Ascendancy Shield Drones hold up the shields on the Taken Crown. Jinra thinks the crystal lenses inside "
        "them are what make the poles hum.",
        [fetch("sc_q_shield_focus", 5)],
        "The poles hum because of the Ascendancy Shield Drones floating round them, and every drone carries a lens of "
        "blue crystal. Bring me those Shield Foci. If I know how they work, I'll find out how to make them stop.",
        "They're still humming, even in my hand.\n\nI'll give these to the witch doctor. If anyone can work out how to "
        "make a shield go quiet, it's Zanshi."))
    A(Q("scq_centurion_valeth_krane", "Centurion Valeth Krane", RAKKUZI, 49, 49, "Centurion's Bane",
        "The officer who holds the Taken Crown is Centurion Valeth Krane, and his soldiers won't give ground while "
        "he's alive. Rakkuzi has heard what the orders say, and he wants Krane dead anyway.",
        [boss("Centurion Valeth Krane")],
        "Your envoy proved the scholars didn't call the soldiers down, and fine, I believe him. They're still on my "
        "tree. Centurion Valeth Krane holds the north arm, and while he stands, his line stands. Go up there and put "
        "him down.",
        "Krane's dead, and his line's falling back to the tip of the arm.\n\nZan'kaji will hear about this tonight. "
        "We don't have the north arm back yet, but now they know we're coming for it.",
        requires_quests=["scq_carry_it_to_the_war_leader"]))
    A(Q("scq_rays_over_the_islets", "Rays Over the Islets", TAZKAL, 48, 48, "Islet Rider's",
        "Rider Taz'kal's wyverns won't fly anywhere near the Driftlets. The Drift Rays and Cloud Jellies that drift "
        "over the islets have them shaking in their roosts.",
        [k("Drift Ray", 7), k("Cloud Jelly", 5)],
        "My wyverns won't go near the Driftlets, the islets chained off the south side of the cloud. The Drift Rays "
        "glide round them like they own the sky, and every Cloud Jelly stings anything that comes close. Thin them out, "
        "and maybe my wyverns will remember they're wyverns.",
        "One of them flew over the first islet this morning, and she came back proud of herself.\n\nThere's something "
        "bigger out there that they're still scared of, though. I've seen its shadow on the cloud.",
        nxt="scq_mother_greatfin"))
    A(Q("scq_mother_greatfin", "Mother Greatfin", TAZKAL, 49, 49, "Greatfin",
        "A sky whale bigger than any of the others glides round the Driftlets, and Taz'kal's wyverns won't fly while "
        "it's in the sky. He calls her Mother Greatfin.",
        [boss("Mother Greatfin")],
        "There's a whale out over the Driftlets the size of a longhouse, and the others follow her like calves. I call "
        "her Mother Greatfin. My wyverns won't leave their roosts while she's singing. Go out over the chains and bring "
        "her down.",
        "The song's stopped, and every wyvern in Spearhold's in the air.\n\nI'm sorry it had to be her. She's the "
        "biggest living thing I've ever seen, and I hope there are more like her somewhere out there."))
    A(Q("scq_eels_at_the_falls", "Eels at the Falls", TAZKAL, 48, 48, "Fallswatcher's",
        "The Falls Eels and Mossback Tortoises at the Falls of Light have been taking the wyverns when they come down "
        "to drink.",
        [k("Falls Eel", 8), k("Mossback Tortoise", 4)],
        "My wyverns drink at the Falls of Light on the south side of the crown, and the Falls Eels have already "
        "taken two of them off the bank. The Mossback Tortoises are worse, because they'll sit in the water and wait. Clear "
        "the bank, so my wyverns can drink.",
        "That bank's safe again, for now.\n\nDak'zin hunts down there. He'll have heard you, and he'll want to talk to "
        "you about the big eel.",
        nxt="scq_the_dewdrinker"))
    A(Q("scq_old_sunantler", "Old Sunantler", TAZKAL, 49, 49, "Sunantler",
        "The Sunlit Stags of the Goldenwood follow an old king with antlers like a crown of light. Taz'kal says no "
        "rider on the crown has earned a trophy yet, and he wants the first one to be that stag's.",
        [boss("Old Sunantler")],
        "Up in the Goldenwood on the north arm there's a stag the others won't walk in front of. His antlers catch the "
        "sun and throw it back at you, and the trolls who've seen him call him Old Sunantler. Every rider on the crown "
        "wants him. I want you to get him first.",
        "That's a trophy no one at the Settlement will believe.\n\nWe'll hang the antlers over the war-leader's fire. "
        "He'll pretend he doesn't like them."))
    A(Q("scq_spirits_in_the_light", "Spirits in the Light", ZANSHI, 48, 48, "Light-Watcher's",
        "Witch Doctor Zanshi sees a light rising through the cloud where the old stones sink into it, and things are "
        "coming up with it. The Seal-Touched Shades round the ring frighten her.",
        [k("Seal-Touched Shade", 6)],
        "There's a ring of old stone out on the cloud, north-east of the stones where the parley was. Light's leaking up "
        "out of the middle of it, and Seal-Touched Shades are coming up with the light. They're not spirits I know, "
        "and the loa go quiet when I ask about them. Send them back where they came from.",
        "They came apart like smoke, and there was nothing behind them.\n\nThe loa still won't talk to me about that "
        "ring, and I've never known them to be scared of anything.",
        nxt="scq_what_the_loa_wont_say"))
    A(Q("scq_what_the_loa_wont_say", "What the Loa Won't Say", ZANSHI, 48, 49, "Runereader's",
        "The guardians round the old ring are covered in runes nobody on the tree can read. Zanshi swallows her pride "
        "and sends you to the Aetherian archivist who's been studying the stones.",
        [fetch("sc_q_rune_shard", 5)],
        "If the loa won't tell me what that ring is, then I'll ask someone who can read it. The Waking Guardians round "
        "it are cut all over with old runes. Bring Rune-Cut Shards off them to the pale archivist who sits by the ring, "
        "and tell him a troll witch doctor sent you. I'd like to see his face.",
        "A troll witch doctor sent you, did she? I'll admit I didn't expect that.\n\nThese are the same runes that are "
        "cut into the ring. They're Kharad, older than my people, and every one of them is a warning. Your witch "
        "doctor was right to be frightened.",
        turn_in_npc_id=ELYON, nxt="scq_keep_it_shut"))
    A(Q("scq_two_brothers", "Two Brothers", MUZZA, 48, 49, "Brother's",
        "Scout Muzza lost his two brothers to the sky lancers on the Taken Crown. The lancers took their spears as "
        "trophies, and Muzza wants them back.",
        [fetch("sc_q_brothers_spear", 2)],
        "My brothers went past the humming poles before any of us knew what the lancers could do. The Ascendancy Sky "
        "Lancers took their spears and carry them like prizes. Bring them back to me. I want to give them to our "
        "mother, because she'll never get anything else.",
        "That's Jaz'ri's spear, and that's Tok's. Tok painted the haft badly, and he never let anyone fix it.\n\n"
        "Thank you. I'll take them down the tree myself when this is over."))
    A(Q("scq_the_dewdrinker", "The Dewdrinker", DAKZIN, 49, 49, "Dewdrinker",
        "Hunter Dak'zin has hunted the falls for weeks and seen the same eel every time, bigger than a canoe and coiled "
        "under the spring. He calls it the Dewdrinker.",
        [boss("The Dewdrinker")],
        "There's an eel in the Falls of Light as long as a canoe, and it drinks from the spring like it's been doing it "
        "for a hundred years. I call it the Dewdrinker. I've had my spear in it twice, and twice it pulled me under. "
        "Go and finish what I started.",
        "So that's where you put the spear in one of these.\n\nI'll remember it. Every hunter on this crown is going "
        "to want to know."))

    # =================================================================================== 2. THE PROOF
    A(Q("scq_both_sides_of_the_stones", "Both Sides of the Stones", GARROK, 48, 48, "Envoy's",
        "Envoy Garrok Blackmane was sent by the Warchief to keep the Horde out of a war it doesn't understand. He "
        "wants to hear from the troll who stood at the parley, Speaker Hezza.",
        [deliver("sc_q_envoys_token", "Take the envoy's token to Speaker Hezza at the Parley Stones")],
        "The war-leader says the scholars called their soldiers down on the parley. The scholars say they didn't. Only "
        "one troll was standing on those stones when it happened, and that's Speaker Hezza. Take her my token so she "
        "knows I sent you, and hear what she has to say.",
        "That's Orgrimmar's token, so somebody's finally asking me instead of shouting.\n\nI was standing right here "
        "when the ship came down, and I saw the pale one's face across from me. He was as surprised as I was.",
        turn_in_npc_id=HEZZA, nxt="scq_what_hezza_saw",
        grant_items=carry("sc_q_envoys_token", "Envoy's Token", "An iron disc stamped with the Horde's mark, the sort "
                          "an envoy gives to show who sent you.")))
    A(Q("scq_what_hezza_saw", "What Hezza Saw", HEZZA, 48, 48, "Speaker's",
        "Speaker Hezza says the Ascendancy war skiff that came down on the parley carries its own soldiers' marks. She "
        "wants you to look at the wreck, and then tell the scholar who stood across from her.",
        [explore(*WRECK, "Look over the burnt war skiff at the Parley Stones")],
        "Look at the ship that came down on us, the burnt one at the edge of the stones. The marks on its side are the "
        "soldiers' marks, not the scholars'. When you've seen them, go and tell Ilaren Vey, the pale one standing over "
        "there. He'll read them better than either of us.",
        "You've been to the wreck. I saw you standing at it.\n\nThose are the Ascendancy's marks, and the skiff was "
        "fitted to fire before it ever came down. They didn't come to keep the peace. They came to break it, and they "
        "weren't fussy about who was standing on the stones.",
        turn_in_npc_id=ILAREN, nxt="scq_orders_under_seal"))
    A(Q("scq_orders_under_seal", "Orders Under Seal", ILAREN, 48, 49, "Patient Lens",
        "Ilaren Vey says every Ascendancy Legionary carries a copy of his orders, sealed in crystal. If he can read "
        "them, he can prove who sent the soldiers to the parley.",
        [fetch("sc_q_legion_orders", 3)],
        "Every Ascendancy Legionary carries his orders sealed in crystal, so he can't forget them and can't change "
        "them. The legionaries on the Taken Crown will have the orders for the parley. Bring me their Sealed Legion "
        "Orders, and I'll show your envoy what my own people meant to do.",
        "Here, in the second plate, it's plain enough. Strike the parley, and take the crown while both sides blame "
        "each other.\n\nThey meant to kill me too. I knew it when the ship came down, but it's different reading it.",
        nxt="scq_carry_it_to_the_war_leader"))
    A(Q("scq_carry_it_to_the_war_leader", "Carry It to the War-Leader", GARROK, 49, 49, "Truthbearer's",
        "Ilaren Vey's reading of the legion's orders proves the survey didn't call the soldiers down. Garrok wants "
        "the war-leader to hear it from someone who fought on the Taken Crown.",
        [deliver("sc_q_read_orders", "Take Ilaren's reading of the orders to War-Leader Rakkuzi")],
        "The scholar didn't call his soldiers down, and here's the proof in his own writing. Rakkuzi won't take it "
        "from me, because I'm Orgrimmar's and he thinks I want to stop his war. He might take it from you, though, "
        "because you've bled on that arm. Take it to him.",
        "So the pale one didn't call them down, and his own people meant to kill him too.\n\nAll right, I'll stop "
        "calling the scholars liars. That doesn't put the soldiers off my tree, and it doesn't stop my war.",
        turn_in_npc_id=RAKKUZI, nxt="scq_centurion_valeth_krane",
        grant_items=carry("sc_q_read_orders", "Ilaren's Reading of the Orders", "A sheet of fine Aetherian paper in "
                          "Ilaren Vey's careful hand, with the legion's orders written out in a language you can "
                          "read.")))

    # =================================================================================== 3. THE SURVEY
    A(Q("scq_a_guest_of_the_house", "A Guest of the House", SAREN, 48, 48, "Guest's",
        "Dockmaster Saren Holt keeps the gangway to Lenswatch, the survey's camp. The surveyor wants to meet everyone "
        "who comes up the tree, and you're next.",
        [deliver("sc_q_dock_pass", "Cross the gangway and give the pass to Surveyor-Captain Destren in Lenswatch")],
        "The surveyor's asked to meet every climber who comes up through the wall, and you're the one I've got. Take "
        "this pass over the gangway to Lenswatch and give it to Surveyor-Captain Destren in the court. They'll give "
        "you a bed there, which is more than the trolls will.",
        "You came, then. Sit down, please, and don't mind the lens.\n\nI've spent a year watching your world through "
        "it, and now you're standing in front of me. You're shorter than I expected, and much louder.",
        turn_in_npc_id=DESTREN, nxt="scq_what_the_ground_thinks",
        grant_items=carry("sc_q_dock_pass", "Dockmaster's Pass", "A slip of white card stamped with the eye of the "
                          "House of the Patient Lens.")))
    A(Q("scq_what_the_ground_thinks", "What the Ground Thinks", DESTREN, 48, 48, "Surveyor's",
        "Surveyor-Captain Destren wants to understand the crown, starting with the sungrass that grows on it. No "
        "plant in the upper sky stores light the way the tree's does.",
        [gather("herb_sungrass", 6, "Gather sungrass on the crown")],
        "Your herbalists call it sungrass, and it does something no plant in the upper sky can do. It holds the day's "
        "light and gives it back at dusk. Gather me some off the crown. I'd like to know why the tree can make "
        "something my whole people can't.",
        "It's warm, even in the shade of the court.\n\nWe make light out of crystal and we spend it. Your tree makes "
        "light out of nothing and saves it for later. I'll be writing about this for a month."))
    A(Q("scq_the_stolen_copy", "The Stolen Copy", TAVIAN, 48, 49, "Archivist's",
        "Archivist Tavian Rell writes everything down twice. The Ascendancy took his first copy when they came down "
        "on the stones, and their Bombardiers and Artillerists on the Chainhold have been passing the pages round.",
        [fetch("sc_q_survey_page", 6)],
        "When the soldiers came down on the stones they took my first copy of everything we'd learned, and now it's "
        "on the Chainhold, the islet chained off the north edge of the cloud. The Ascendancy Bombardiers and "
        "Artillerists there carry the pages folded up in their packs. Bring me my Stolen Survey Pages, every one you "
        "can find.",
        "They've been reading them, look, there are notes in the margins.\n\nEvery note's about the old ring in the "
        "cloud. They weren't after our measurements of the tree at all. They wanted to know what we'd learned about "
        "the seal."))
    A(Q("scq_mark_the_rifts", "Mark the Rifts", CORYN, 48, 48, "Riftmarker's",
        "Lensmaster Coryn Aldaer can see a coin on the ground from Lenswatch, but he can't see where the cloud is too "
        "thin to stand on. He wants three of the tears in the shelf marked for the lens.",
        [explore(*RIFT_NORTH, "Mark the tear north of the Annex"), explore(*RIFT_WEST, "Mark the tear west of the Annex"),
         explore(*RIFT_SOUTH, "Mark the tear south of the Survey Dock")],
        "The great lens looks straight through cloud, and that's the trouble, because it can't tell me where the cloud "
        "stops holding you up. There are three tears in the shelf I want marked, one north of the Annex, one west of "
        "it and one south of the dock. Stand at the edge of each one so I can fix it in the lens.",
        "I watched you at every one of them. You stood far closer to the edge than I'd have dared.\n\nThe tears are "
        "wider than they were a month ago. The cloud's thinning, and I don't know why."))
    A(Q("scq_storm_readings", "Storm Readings", CORYN, 48, 49, "Stormreader's",
        "The Stormbank, the dark cloud south-east of the shelf, has been getting heavier. Coryn wants Charged Motes from "
        "the Bolt-Born Elementals to read how much lightning it's holding.",
        [fetch("sc_q_charged_mote", 6), k("Stormbank Thunderbird", 5)],
        "The Stormbank's been getting darker every day, and the lens can't see into it at all. The Bolt-Born "
        "Elementals in it leave Charged Motes when they come apart, and each mote holds a little of the storm's charge. "
        "Bring me some, and while you're in there, keep the Stormbank Thunderbirds off you. They're drawn to anyone "
        "carrying a mote.",
        "There's twice as much charge in these as there should be.\n\nSomething in the middle of the Stormbank is "
        "pulling the lightning in and holding it. I'd very much like to know what it is.",
        nxt="scq_the_hollow_storm"))
    A(Q("scq_the_hollow_storm", "The Hollow Storm", CORYN, 49, 49, "Hollow Storm",
        "At the heart of the Stormbank there's a storm with an eye in it, and it's pulling all the lightning toward "
        "itself. Coryn calls it the Hollow Storm.",
        [boss("The Hollow Storm")],
        "There's a storm in the middle of the Stormbank with an eye in the middle of it, and every bolt in the bank "
        "goes into that eye. I'm calling it the Hollow Storm, because that's all I can see of it. If it keeps pulling "
        "the lightning in, sooner or later it'll let it all go at once. Put it out before it does.",
        "The whole bank flashed white when it went, and then it was only cloud.\n\nI've written down what you did, "
        "though I don't think the council will believe it."))
    A(Q("scq_guns_on_the_chainhold", "Guns on the Chainhold", HALDANE, 48, 49, "Shipmaster's",
        "Shipmaster Corin Haldane's survey ship has been shelled from the Chainhold twice. He wants the Ascendancy "
        "Artillerists and Ascendancy Bombardiers on the islet silenced.",
        [k("Ascendancy Artillerist", 7), k("Ascendancy Bombardier", 5)],
        "Twice now they've fired on my ship from the Chainhold, and the second time they took a strip off her hull. "
        "She's the oldest ship in the House's fleet, and she's our only way home. Cross the chains onto the islet, and "
        "silence the Ascendancy Artillerists and Ascendancy Bombardiers working the guns.",
        "No shells today, and the crew's sleeping on deck again.\n\nThe soldiers will bring more guns, because they "
        "always do. But they'll think twice before they point them at my ship."))
    A(Q("scq_wolves_on_the_cloud", "Wolves on the Cloud", HALDANE, 48, 48, "Cloudwalker's",
        "The Cloudrunner Wolves and Shelf Stalkers on the shelf have started following the survey's porters right up "
        "to the gangway.",
        [k("Cloudrunner Wolf", 8), k("Shelf Stalker", 5)],
        "My porters carry the ship's stores across the cloud, and every Cloudrunner Wolf on the shelf has learned to "
        "follow them. "
        "The Shelf Stalkers are worse, because you can't see them in the mist until they're on you. Thin them out so "
        "my porters can work without a guard on every one.",
        "They walked the whole shelf this morning and nothing followed them.\n\nI'd never seen a wolf until I came "
        "down here. I can't say I've missed them."))

    # =================================================================================== 4. THE EARTHBORN
    A(Q("scq_ask_them_yourself", "Ask Them Yourself", MATIAS, 48, 48, "Earthborn",
        "Matias Arrieta has lived with the Aetherians for three years, and in all that time nobody's told him whether "
        "the Earth people are allowed to leave. He wants someone else to ask the Warden.",
        [deliver("sc_q_matias_letter", "Take Matias's letter to Warden Sellis Varn in Lenswatch")],
        "I've asked Warden Varn twice if we're free to go, and twice he's told me it's complicated. He's kind about it, "
        "and that's the worst part. Take him this letter. You're not one of his guests, so maybe he'll give you a "
        "straight answer.",
        "Matias wrote this, I'd know his hand anywhere. He's asking whether they can leave.\n\nThe true answer is yes, "
        "they can, and the honest answer is that I've no idea where they'd go. I've never had the courage to say both "
        "at once. You can tell him I said it.",
        turn_in_npc_id=SELLIS, nxt="scq_the_two_they_took",
        grant_items=carry("sc_q_matias_letter", "Matias's Letter", "A folded letter in Spanish and then in careful "
                          "Aetherian, the same question twice.")))
    A(Q("scq_the_two_they_took", "The Two They Took", MATIAS, 49, 49, "Annexwarden's",
        "When the Ascendancy came down on the stones they took two of the Earthborn back to the Chainhold. Matias "
        "found out where, and the Construct Hounds guarding the hangar are all that's in the way.",
        [k("Construct Hound", 6), explore(*HANGAR, "Find the two Earthborn the Ascendancy took, in the Chainhold's hangar")],
        "The soldiers took two of ours when they hit the stones, Lise and Tomasz. I found out they're being kept in the "
        "hangar on the Chainhold, and the Construct Hounds guard it. Get through the hounds and get into that hangar. "
        "They'll follow you out if they see a face that isn't Aetherian.",
        "They're here, they're both here. Lise hasn't stopped shaking and Tomasz hasn't stopped talking.\n\nThe "
        "soldiers wanted to know where we came from. They asked over and over, and they didn't believe a word of the "
        "answer. Thank you.",
        requires_quests=["scq_ask_them_yourself"]))
    A(Q("scq_two_kinds_of_guest", "Two Kinds of Guest", MATIAS, 49, 49, "Guestfriend's",
        "Matias doesn't trust Ilaren Vey, and he says so, but Ilaren is the only scholar who comes to the Annex without "
        "a notebook. Matias sends him something from the Annex.",
        [deliver("sc_q_annex_bread", "Take the Annex's bread to Ilaren Vey at the Parley Stones")],
        "Ilaren Vey's the only one of them who comes to the Annex without a notebook, and he eats what Beatriz cooks. "
        "I still don't trust him, because I've never trusted any of them. But he stood on the stones when the soldiers "
        "came, and he's still here. Take him this, from the Annex.",
        "This is Beatriz's bread, which means Matias sent it, and he doesn't like me.\n\nHe's right not to, mostly. My house kept his "
        "people for three years and called it kindness. Tell him I said thank you, and that I'll come and eat it at "
        "the Annex, if he'll have me.",
        turn_in_npc_id=ILAREN, requires_quests=["scq_the_two_they_took"],
        grant_items=carry("sc_q_annex_bread", "Bread From the Annex", "A round loaf baked by Beatriz Lobo out of sky "
                          "grain and stubbornness. It smells like a bakery on a street a world away.")))
    A(Q("scq_sky_medicine", "Sky Medicine", RANIA, 48, 48, "Medic's",
        "Dr. Rania Azar is the only doctor for thirty Earth people on a cloud. She's learning which of the crown's herbs "
        "can do what her medicines used to.",
        [gather("herb_khadgar", 6, "Gather khadgar's whisker on the crown")],
        "I ran out of real medicine in my first year up here, so now I make it. The trolls showed me a herb that grows "
        "on the crown, khadgar's whisker, that brings down a fever better than anything I had in Beirut. Gather some "
        "for me, please, and I'll show you what I make of it.",
        "That's enough to treat the whole Annex through the next fever, and the trolls at Spearhold too.\n\nThe "
        "scholars watched me grind the first batch and wrote down every step. I've started explaining as I go. It's "
        "easier than being stared at.",
        nxt="scq_gold_dust_salve"))
    A(Q("scq_gold_dust_salve", "Gold Dust Salve", RANIA, 49, 49, "Salvemaker's",
        "Dr. Azar has found that the dust off a Gilded Moth's wings numbs pain. She wants enough to make a salve for "
        "the wounded at Spearhold and the Annex both.",
        [fetch("sc_q_gold_dust", 6)],
        "The Gilded Moths in the Goldenwood shed a dust that numbs whatever it touches. I've tried it on a burn, and it "
        "works. Bring me Pinches of Gold Dust and I'll make a salve, enough for the Annex and for the trolls at "
        "Spearhold. They're bleeding as much as we are.",
        "This will make three jars, and one of them's going to Spearhold whether the war-leader wants it or not.\n\n"
        "I took an oath to treat whoever's in front of me. Up here, that's everybody."))
    A(Q("scq_hound_gyros", "Hound Gyros", PAVEL, 48, 49, "Engineer's",
        "Pavel Novak designed bridges in Brno, and now the survey wants his opinion on engines that hold cities in the "
        "sky. He wants to see how the Ascendancy's Construct Hounds keep their balance.",
        [fetch("sc_q_hound_gyro", 5)],
        "The Construct Hounds on the Chainhold run on cloud, on chains, on anything, and they don't ever fall over. "
        "Something in their chests keeps them upright. Bring me those Hound Gyros. If I can understand how they balance "
        "a dog, I might understand how they balance an island.",
        "Look at it, it's still spinning. There's no motor in it at all.\n\nIt's not engineering the way I learned it, "
        "but it's not magic either. It's something in between, and I think I can learn it.",
        nxt="scq_how_to_anchor_an_island"))
    A(Q("scq_how_to_anchor_an_island", "How to Anchor an Island", PAVEL, 49, 49, "Anchorwright's",
        "Pavel wants to see the gravity anchor that holds Lenswatch in place, now that he understands the gyros.",
        [explore(*ANCHOR, "Look at the gravity anchor holding Lenswatch in place", zone=LW)],
        "Lenswatch is an island that floats, and it's held still by one anchor and a chain. I've asked to see it three "
        "times and three times they've said later. You're a guest of the House, so walk over to it, look at it "
        "properly, and come back and tell me everything you saw.",
        "A crystal the size of a bathtub, turning on its own, and a chain that goes down into the cloud and doesn't "
        "come back up.\n\nThe chain isn't holding the island up. It's holding it down. That changes everything I "
        "thought I knew about this place."))
    A(Q("scq_every_islet", "Every Islet", EWAN, 48, 49, "Islet-Walker's",
        "Ewan Docherty climbed the whole World Tree from the roots up. Now he wants to stand on every islet off the "
        "crown, starting with the two at the end of the Driftlets' chains.",
        [explore(*DRIFT_TWO, "Stand on the second Driftlet"), explore(*DRIFT_THREE, "Stand on the third Driftlet")],
        "I climbed this tree from the roots so I could be first to the top, and I wasn't. So now I'm going to stand on "
        "everything up here that anyone's ever named. The Driftlets are chained off the south side of the cloud, and "
        "the two at the far end of the chains are the ones nobody's walked. Walk them for me.",
        "Two more for the list, then. I'll walk them myself tomorrow, but you were first, and I'll write that "
        "down.\n\nIt's daft, I know. But the first time I stood on that cloud, I cried. I'd like to keep feeling that "
        "way about this place."))

    # =================================================================================== 5. THE SEAL
    A(Q("scq_lend_him_the_lens", "Lend Him the Lens", RANJO, 48, 48, "Lookdown",
        "Old Ranjo comes to the Lookdown every morning to make sure his village is still down there. He's heard the "
        "survey's lens can see a coin on the ground.",
        [deliver("sc_q_ranjo_charm", "Take Ranjo's charm to Lensmaster Coryn Aldaer in Lenswatch")],
        "The village I was born in is down there in Stranglethorn, and from here it's only a smudge. They say the sky "
        "people's lens can see a coin on the ground. Take this charm to whoever keeps the lens and ask him to look for "
        "my village. It's carved with the shape of the river bend we live on.",
        "A river bend, with a fallen temple on the north bank? I've seen it, I've seen it many times.\n\nThere's smoke "
        "from the cookfires every morning, and children in the river every afternoon. Tell your friend his village is "
        "still there.",
        turn_in_npc_id=CORYN,
        grant_items=carry("sc_q_ranjo_charm", "Ranjo's Charm", "A flat piece of jungle wood carved with the curve of a "
                          "river and a little broken temple on its bank.")))
    A(Q("scq_keep_it_shut", "Keep It Shut", ELYON, 49, 49, "Sealwarden's",
        "Archivist Elyon Sarre has read enough of the old ring to know its guardians are waking. The Waking Guardians "
        "and Unbound Storms round the seal are getting stronger every time the guns fire.",
        [k("Waking Guardian", 7), k("Unbound Storm", 5)],
        "Every word I can read on this ring means keep it shut. The Waking Guardians were set here to do exactly that, "
        "and they've woken up wrong, the way a sleeper wakes up fighting. The Unbound Storms were chained in the "
        "stones, and now they're coming loose. Put them both down before the ring shakes itself apart.",
        "The ring's quieter, and I can hear myself think.\n\nIt won't stay quiet, though. Every time the soldiers fire "
        "their guns on the north arm, the light under the seal gets brighter.",
        nxt="scq_the_stone_that_woke"))
    A(Q("scq_the_stone_that_woke", "The Stone That Woke", ELYON, 49, 49, "Stonewaker",
        "One of the ring's wardens has stood up. Elyon says the Stone That Woke is the oldest guardian of the seal, and "
        "it's attacking anything that comes near it, including the seal itself.",
        [boss("The Stone That Woke")],
        "The biggest of the ring's wardens has stood up off its plinth. The Kharad cut its name into its chest, and I "
        "think it means the stone that keeps watch, but it's not keeping watch now. It's tearing at the seal it was "
        "made to guard. Stop it before it opens the thing for us.",
        "It fought you right up until the end, and then it knelt facing the seal.\n\nI think it knew. I think it "
        "woke because something on the other side of the seal was pushing, and it couldn't hold it any more."))
    A(Q("scq_the_light_under_the_stones", "The Light Under the Stones", ILAREN, 49, 49, "Sealsworn",
        "Ilaren Vey wants every side of this fight to see the seal before it's too late. He's asked the war-leader, the "
        "envoy and the archivist to meet at the old ring, and he wants you there too.",
        [explore(*SEAL_HEART, "Stand at the seal in the middle of the old ring")],
        "Krane's dead and the stone's down, and the light under the seal's brighter than it's ever been. I've asked "
        "Rakkuzi, your envoy and Elyon to meet me at the ring, and to everyone's surprise they've all said yes. Come "
        "and stand with us. Whatever happens next, someone from every side should see it.",
        "You were there. You felt it go.\n\nThe guns on the north arm fired, the ground shook, and the seal split down "
        "the middle. Something underneath it breathed out. Rakkuzi dropped his spear, and I've never seen a troll "
        "drop his spear. Whatever's under that seal is older than the Ascendancy and older than my people, and "
        "it's awake.",
        requires_quests=["scq_the_stone_that_woke", "scq_centurion_valeth_krane"],
        nxt="scq_bigger_than_the_ascendancy"))
    A(Q("scq_bigger_than_the_ascendancy", "Bigger Than the Ascendancy", ILAREN, 49, 49, "Truthsworn",
        "Ilaren Vey has written down everything that happened at the seal. He wants the surveyor to send it to the "
        "council in Aurelion today.",
        [deliver("sc_q_ilarens_report", "Take Ilaren's report to Surveyor-Captain Destren in Lenswatch")],
        "My house has argued for a hundred years about whether the ground is worth talking to. We were arguing about "
        "the wrong thing. Take this to the surveyor, and tell him I said to send it to the council tonight, not "
        "tomorrow. The Ascendancy isn't the worst thing in the sky any more.",
        "I read it twice, and then I sent it to the council before I'd finished reading it a third time.\n\nThey'll "
        "have it before dawn. I don't know what they'll do, but I know what I'd do. I'd open the gates.",
        turn_in_npc_id=DESTREN, nxt="scq_lance_captain_varos_thale",
        grant_items=carry("sc_q_ilarens_report", "Ilaren's Report", "Six pages in Ilaren Vey's hand, written fast, with "
                          "the seal of the House of the Patient Lens pressed into the last one.")))
    A(Q("scq_lance_captain_varos_thale", "Lance-Captain Varos Thale", DESTREN, 49, 49, "Gatesworn",
        "The council has answered. Aurelion will open its gates to the ground, and the council's own skiff is coming "
        "down to fetch the survey's guests. Lance-Captain Varos Thale holds the Chainhold, and the skiff can't come "
        "down while he does.",
        [boss("Lance-Captain Varos Thale")],
        "The council's answered, and it's the answer I hoped for. Aurelion will open its gates to the ground for the "
        "first time in our history, and they're sending their own skiff down to the crown. But Lance-Captain Varos "
        "Thale holds the Chainhold, and he'll shoot it out of the sky. Cross the chains and put him down.",
        "The Chainhold's quiet, and the council's skiff is already on its way down.\n\nYou'll be on it, and so will "
        "Matias and Ilaren, whether they like sitting next to each other or not. Aurelion's open to you. I hope it's "
        "everything I've told you it is, and I'm afraid it's falling apart a little faster than I told you."))
    return out
