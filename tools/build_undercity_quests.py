#!/usr/bin/env python3
"""Undercity quest pass (2026-10-23).  Idempotent.

    python3 tools/build_undercity_quests.py && python3 tools/retier_quest_rewards.py

Writes data/quests/undercity.json:
  * 19 hub quests, L10-16.  Undercity has no wilderness of its own, so the hub sends you out to Eastern Tirisfal and Silverpine North
    and brings you back: kill / fetch / boss / explore, plus the quest-engine spice - DELIVER (Halloran's slip, the Sennarath <-> Oswin
    scroll swap that bridges into Silverpine), CRAFT (smelting at the Undercity Forge), DROP-STARTED quests (stray vial, groundskeeper
    scrap) and a Linken's-Sword gate ("The Dark Lady's Ear" needs the Silverpine ledger, the Scarlet interrogator and the Scourge cave).
  * 11 Plague Depths quests, L30-34: Gatewarden Sorrel's cull, Master Apothecary Sable's chain, one boss quest per boss, a Linken gate
    (all four Court/Lab bosses) before Zul'keth, and the report back to Sylvanas.  Kill / fetch / boss ONLY - no escorts.
Fetch items reuse the Tirisfal drops already in quest_drops.json (oracle_pearl etc.) plus the pd_* drops from build_plague_depths_content.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import kill, fetch     # noqa: E402
from tools import tirisfal_gear                         # noqa: E402
from tools.tirisfal_gear import reward_pack             # noqa: E402

OUT = ROOT / "data/quests/undercity.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
UC, ET, SPN, PD = "undercity", "eastern_tirisfal", "silverpine_north", "plague_depths"

# ---- reward-name themes for this pass --------------------------------------------------------------------------------------
tirisfal_gear.THEMES.update({
    "uc_hall": (["Deathguard", "Rotunda", "Long-Descent", "Ward-Bell", "Muster-Roll", "Lamplit"],
                ["Issued in the Rotunda, mended in the dark.", "Cold as the elevator shaft, and about as comforting.",
                 "The Forsaken wear what lasts."]),
    "uc_war": (["Drillyard", "Pit-Scarred", "Bone-Banded", "Ironbrow's", "War-Quarter", "Recruit-Hardened"],
               ["Beaten into shape by a drillmaster who has all the time in the world.", "It has seen the pit and said nothing.",
                "Stamped with the forge's mark and the smith's opinion."]),
    "uc_magic": (["Violet-Spire", "Sigil-Cut", "Magister's", "Hexed", "Ritual-Stained", "Candle-Gutter"],
                 ["Woven in a hall that hums.", "The sigil inside is still warm.", "Studied-over and, thankfully, mostly studied."]),
    "uc_apoth": (["Apothecarium", "Reagent-Stained", "Vial-Pocket", "Retort-Singed", "Marwen's", "Distiller's"],
                 ["Smells of cloves and something you'd rather not name.", "Every pocket holds a stopper.",
                  "Scorch marks that never came out."]),
    "uc_scout": (["Rhyne's", "Deathstalker", "Silverpine-Worn", "Night-Road", "Pathfinder's", "Shadow-Hide"],
                 ["Cut for someone who walks and does not rattle.", "The road dust has become the colour.",
                  "Silent soles, sharp edges."]),
    "uc_court": (["Dark Lady's", "Royal-Quarter", "Lordaeron-Gilt", "Sylvan", "Banshee-Thread", "Sovereign's"],
                 ["Black silk edged in a violet that does not fade.", "She doesn't give gifts. She issues them.",
                  "Lordaeron's colours, on Lordaeron's dead."]),
    "uc_plague": (["Blight-Court", "Plague-Cellar", "Rot-Veined", "Cistern-Foul", "Alchemist's Wake", "Vat-Born"],
                  ["Cut from the cellar and cured in the Cistern.", "It still twitches, now and then.",
                   "Society-made, and not for the Society's good."]),
    "uc_sump": (["Sump-Soaked", "Conduit", "Gutter-Pressed", "Overflow", "Sluice-Worn", "Quarantine"],
                ["Wet to the bone, even dry.", "Marked with the Society's warning glyph.", "Stained green at every seam."]),
})

# ---- level tables ----------------------------------------------------------------------------------------------------------
HUB_XP = {10: 520, 11: 600, 12: 680, 13: 760, 14: 840, 15: 920, 16: 1000}
HUB_GOLD = {10: 2400, 11: 2700, 12: 3200, 13: 3600, 14: 3900, 15: 4200, 16: 4500}
PD_XP = {30: 2400, 31: 2500, 32: 2600, 33: 2700, 34: 2800}
PD_GOLD = {30: 8000, 31: 8300, 32: 8600, 33: 8900, 34: 9200}


def explore(zone, x, y, radius=6):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def boss(target, zone):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def craft(recipe, label, n=1):
    return dict(type="craft", target=recipe, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, mult=None, **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if (is_boss and ilvl >= 10) else "uncommon"
    m = mult if mult is not None else (1.3 if is_boss else 1.0)
    xp, gold = (PD_XP, PD_GOLD) if hi >= 30 else (HUB_XP, HUB_GOLD)
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, reward_exp=int(xp[hi] * m), reward_gold=int(gold[hi] * m),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             rewards=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3))
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def quests():
    Z = []
    A = Z.append

    # ============================================================================================ HUB: ARRIVAL
    HAL, EXE, SYL = "uc_guard_2", "uc_executor", "uc_sylvanas"
    A(Q("ucq_rotunda_walk", "Know the Wheel", HAL, UC, 10, 10, "uc_hall",
        "Deathguard Halloran has watched a hundred newly-arrived dead wander into the Canal because they could not tell the quarters "
        "from one another. Walk the four great halls - Royal, Magic, War and Apothecarium - and learn the wheel before it learns you.",
        [explore(UC, 46, 52, 8), explore(UC, 154, 52, 8), explore(UC, 46, 148, 8), explore(UC, 154, 148, 8)],
        "Four quarters, one wheel. Royal to the north-west, Magic north-east, War south-west, Apothecarium south-east. Walk them all.",
        "You came back and you are not green. The Undercity has a use for you yet.", "ucq_muster_slip"))
    A(Q("ucq_muster_slip", "A Slip for the Executor", HAL, UC, 10, 10, "uc_hall",
        "Halloran has a muster slip for Executor Wrenfall, who holds the Royal Quarter's north gate. Halloran cannot leave his post. "
        "He would very much like it to be delivered without anyone reading it, as the Executor is touchy about her paperwork.",
        [deliver("uc_muster_slip", "Take Halloran's muster slip to Executor Wrenfall")],
        "Along the north promenade, west of the elevator. The Executor will want it in her hand.",
        "Halloran. Of course. Never a word wasted. Here, take something for your troubles.", None,
        turn_in_npc_id=EXE,
        grant_items=carry("uc_muster_slip", "Halloran's Muster Slip", "A neatly-folded slip stamped with the Deathguard sigil.")))
    A(Q("ucq_scarlet_pressure", "The Crusade at the Door", EXE, UC, 10, 12, "uc_hall",
        "Scarlet Zealots and Bowmen are patrolling the Tirisfal road to the Ruins, close enough to see the portal. Executor Wrenfall "
        "has no intention of finding out whether they are brave enough to try the gate. Thin them out before they find out for her.",
        [kill("Scarlet Zealot", 8, zone=ET), kill("Scarlet Bowman", 6, zone=ET)],
        "The Scarlet Watch Post, east of Brill. Zealots and bowmen. Leave none in sight of the road.",
        "Good. The portal stays dark and the Crusade stays outside. Quarter-master's thanks, from me.", "ucq_scarlet_orders",
        requires_quests=["ucq_muster_slip"]))
    A(Q("ucq_scarlet_orders", "Orders in Scarlet Ink", EXE, UC, 11, 12, "uc_hall",
        "Wrenfall wants to read what the Crusade has been told. The Scarlet converts and initiates carry orders in a neat red hand; "
        "she needs five of them to piece together a picture.",
        [fetch("crusade_orders", 5)],
        "The Crusader's Outpost, east of Brill, and the farm roads. Anyone in Scarlet who can read. Bring me five.",
        "A very tidy hand. They are afraid of us, and have been told to hide it. I find that touching.", None))

    # ============================================================================================ HUB: WAR QUARTER (craft + drill)
    SMITH, HASK = "uc_blacksmith", "uc_drillmaster"
    A(Q("ucq_tin_bars", "Tin for the Forge", SMITH, UC, 10, 12, "uc_war",
        "Smith Ironbrow has a bench, a quench trough, and no tin. The Undercity Forge in the War Quarter is cold because nobody has "
        "bothered to light it. Smelt three tin bars at the forge and he'll know the fire is yours.",
        [craft("bar_tin", "Smelt tin bars at the Undercity Forge", 3)],
        "Tin ore from the western hills if you've no stock. The forge is south-west of the War Hall. Light it, and smelt three bars.",
        "Three bars, and not a cinder wasted. That's how you light a forge.", "ucq_iron_bars"))
    A(Q("ucq_iron_bars", "Iron for the Guard", SMITH, UC, 11, 12, "uc_war",
        "With tin in hand, Ironbrow wants rough iron for the Royal Guard's greaves. Smelt three rough iron bars at the Undercity Forge. "
        "He'll even let you use his good tongs.",
        [craft("bar_rough_iron", "Smelt rough iron bars at the Undercity Forge", 3)],
        "Rough iron, three bars. Don't touch the tongs on the left. They bite.",
        "Rough iron, rough work. The Guard will wear them with pride, or at least with plates.", None))
    A(Q("ucq_drill_remnants", "Live Targets", HASK, UC, 10, 11, "uc_war",
        "Drillmaster Hask is running out of recruits who do not mind being hit. The Lordaeron Remnants in the Ruins above are persistent "
        "and cheerfully hostile, and it is high time somebody used them for target practice.",
        [kill("Lordaeron Remnant", 8, zone=ET), fetch("lordaeron_signet", 4)],
        "North, up the shaft, then south along the road to the Ruins. Eight remnants, four signets. Pretend you are teaching them.",
        "Eight and four. The recruits will learn more from your signets than from my yelling.", "ucq_drill_brennic"))
    A(Q("ucq_drill_brennic", "A Captain for the Pit", HASK, UC, 11, 12, "uc_war",
        "Crusader Brennic holds the Scarlet outpost east of Brill. Hask would like him in the pit, in a manner of speaking.",
        [boss("Crusader Brennic", ET)],
        "The Crusader's Outpost. His armour is polished. His faith is brittle. Break one of them.",
        "Polished and brittle indeed. Take your prize and tell the recruits you did not enjoy it.", None))

    # ============================================================================================ HUB: MAGIC QUARTER
    VAL, KOL, SEN = "uc_mage_trainer", "uc_warlock_trainer", "uc_scholar"
    A(Q("ucq_valdis_relics", "Wards of the Old Crypt", VAL, UC, 10, 12, "uc_magic",
        "Magistrix Valdis has been studying the Agamand wards, and the wards have been studying her. She needs five grave relics from "
        "the crypt-keepers in Western Tirisfal to complete her notes.",
        [fetch("grave_relic", 5)],
        "The Agamand Family Crypt, Western Tirisfal. The wights and graverobbers carry the relics. Five.",
        "A ward of twelve strokes, carved by a mason who couldn't count. Delightful. Thank you.", None))
    A(Q("ucq_kolven_ledger", "Whose Demon Is It?", KOL, UC, 11, 12, "uc_magic",
        "Dreadmaster Kol'ven wants to know who the Cult of the Damned bargain with. The cultists carry ledger pages. The pages carry "
        "names. The names carry weight. Bring him six.",
        [fetch("cult_ledger_page", 6)],
        "Cult Farm, Eastern Tirisfal. Acolytes, fanatics. Don't read the last line of any page. Trust me.",
        "Six pages. So it isn't one of mine. Pity - I'd have enjoyed the argument.", None))

    # ============================================================================================ HUB: APOTHECARIUM
    MAR, SAB = "uc_apothecary", "uc_master_apothecary"
    A(Q("ucq_marwen_sacs", "Venom for the Retorts", MAR, UC, 10, 11, "uc_apoth",
        "Apothecary Marwen runs on venom, bile and spite. The Venomweb skitterers east of Brill carry sacs that clear the throat of "
        "a retort like nothing else. Bring her six.",
        [fetch("venom_sac", 6)],
        "Venomweb Vale in Eastern Tirisfal. Sacs, not spiders - the spiders are mostly legs. Six, unbroken.",
        "Fat, ripe and unburst. You have a gift. Here, for the effort.", None))
    A(Q("ucq_stray_vial", "A Vial in the Wrong Hands", "item:uc_stray_vial", UC, 13, 14, "uc_apoth",
        "A sealed vial taken off a Plagued Courier on the Silverpine road. The Apothecary Society's wax is on the stopper, and so is a "
        "hairline crack. Master Apothecary Sable will want to know why a Society vial is running about the forest.",
        [deliver("uc_stray_vial", "Take the stray vial to Master Apothecary Sable")],
        "The Master Apothecary's lab, Apothecarium. Hand it over and tell her where you found it.",
        "The wax is ours. The compound is not on any ledger I signed. Someone has been busy behind my back.", None,
        turn_in_npc_id=SAB))

    # ============================================================================================ HUB: SCHOLAR (the bridge to Silverpine)
    OSW = "sp_north_cemetery_keeper"
    A(Q("ucq_sennarath_scroll", "A Scroll for Raven Hill", SEN, UC, 12, 13, "uc_magic",
        "Loremaster Sennarath has tracked the Cult's cipher across half of Lordaeron, and now believes Keeper Oswin at Raven Hill "
        "Cemetery has the missing key. The scroll is sealed in grave-wax and she is not letting it leave the Undercity except in a "
        "pair of steady hands.",
        [deliver("uc_sennarath_scroll", "Take the scroll to Keeper Oswin, Raven Hill Cemetery, Silverpine North")],
        "North, by portal, into Silverpine. Raven Hill Cemetery. Oswin knows the cipher. Put it in his hand. Do not read it.",
        "He frowns the way I do. A good sign. Give me a moment - there will be a reply.", None,
        turn_in_npc_id=OSW,
        grant_items=carry("uc_sennarath_scroll", "Sennarath's Sealed Scroll", "Grave-wax over parchment. It smells of old libraries.")))
    A(Q("ucq_oswin_reply", "Oswin's Reply", OSW, SPN, 12, 13, "uc_scout",
        "Keeper Oswin has read Sennarath's scroll twice and written a reply. The reply is short, and clearly not meant for the road. "
        "Take it back to Loremaster Sennarath in the Magic Quarter.",
        [deliver("uc_oswin_reply", "Return Oswin's reply to Loremaster Sennarath in the Undercity")],
        "Back to the Undercity and Sennarath. Keep it dry. Keep it close. Keep your opinions to yourself.",
        "'Yes, the key is in the husks.' Of course it is. Oswin always did like his answers buried.", None,
        requires_quests=["ucq_sennarath_scroll"], turn_in_npc_id=SEN,
        grant_items=carry("uc_oswin_reply", "Oswin's Reply", "Two lines in a cramped hand. The ink is still damp.")))
    A(Q("ucq_groundskeeper_scrap", "A Scrap in the Soil", "item:uc_groundskeeper_scrap", UC, 12, 14, "uc_magic",
        "Torn from the pocket of a Skeletal Groundskeeper at Raven Hill: a fragment of ledger in the Cult's cipher. Sennarath is the "
        "only person in the Undercity who might read it.",
        [deliver("uc_groundskeeper_scrap", "Deliver the scrap to Loremaster Sennarath")],
        "Sennarath, the Magic Quarter. She loves a scrap. She'll love this one more.",
        "A line of the cipher, in a groundskeeper's pocket. How very careless of someone. Thank you.", None,
        turn_in_npc_id=SEN))

    # ============================================================================================ HUB: HUNTERS + DEATHSTALKERS
    ISO, RHY = "uc_hunter_trainer", "uc_deathstalker"
    A(Q("ucq_pyrewood_hunt", "The Pyrewood Pack", ISO, UC, 15, 16, "uc_scout",
        "Ranger Isolde hunts what the Dark Lady needs hunted, and this season it's the worgen around Pyrewood Village: thickening in "
        "number, bolder in daylight, and very much not our friends. Thin the ambushers and the feral ones both.",
        [kill("Worgen Ambusher", 6, zone="silverpine_south"), kill("Feral Worgen", 6, zone="silverpine_south")],
        "Pyrewood Village, Silverpine South. Watch the treeline. They love the treeline.",
        "Twelve less to watch. The Dark Lady will hear of it, if only because I'll tell her.", None))
    A(Q("ucq_watchman", "The Watchman Who Stayed", RHY, UC, 15, 16, "uc_scout",
        "A Forsaken Watchman at Raven Hill never stopped his patrol. He no longer answers challenges, or his own name. Deathstalker "
        "Rhyne has been asked to put him down quietly, and has decided the quiet option is you.",
        [kill("Skeletal Groundskeeper", 6, zone=SPN), boss("The Forsaken Watchman", SPN)],
        "Raven Hill Cemetery, Silverpine North. The groundskeepers first - they hear everything. Then the Watchman.",
        "Quiet work. Efficient. I may recommend you to Rhyne's less dignified cousins.", None))

    # ============================================================================================ HUB: THE LINKEN GATE + THE DEEPS WARNING
    A(Q("ucq_dark_ladys_ear", "The Dark Lady's Ear", EXE, UC, 14, 16, "uc_court",
        "Three separate reports have reached Wrenfall: the Scarlet interrogator's ledger, the Scourge Cave's necromancer, and the "
        "Agamand cipher in Silverpine. Each is a thread. Sylvanas would like to see them tied. Whoever carried those three threads "
        "should stand in front of her.",
        [explore(UC, 46, 46, 6)],
        "The Queen is in the Royal Quarter's great hall. Stand before her. Bow, if the knees allow it.",
        "She has been told. She says: 'Remember the face.' I would take that as the highest praise she gives.", None,
        mult=1.5, turn_in_npc_id=SYL, requires_quests=["sp_ledger_cipher", "ets_vishas", "etc_orvyn"]))
    GAT = "uc_gatewarden"
    A(Q("ucq_deeps_warning", "The Seal at the Bottom", GAT, UC, 15, 16, "uc_hall",
        "Gatewarden Sorrel keeps the iron door at the south end of the wheel. Nothing has come up from the Deeps for weeks, which "
        "she does not like. She wants someone to stand at the gate and see whether it feels as quiet as it sounds.",
        [explore(UC, 100, 178, 5)],
        "Stand at the iron door in the south. Count to thirty. Tell me if you hear anything. Do not open it.",
        "You heard it too, then. Good. Come back when you are much stronger. There is work below.", None))

    # ============================================================================================ PLAGUE DEPTHS (L30-34)
    # The Royal Apothecary Society's inner circle is breeding a plague beneath the city to depose the Dark Lady.
    A(Q("ucq_pd_gate", "Cull the Cistern", GAT, UC, 30, 31, "uc_sump",
        "Sorrel is no longer certain what is coming up the Deeps stair. Whatever the Society's alchemists are breeding down there is "
        "flooding the Outer Cistern with rats, worms, hounds and walking corpses. She wants the first chamber quieter.",
        [kill("Plague Zombie", 8, zone=PD), kill("Plagued Hound", 6, zone=PD), kill("Rot Worm", 6, zone=PD)],
        "Through the iron door, then down. The Outer Cistern. Bring friends. The Society's work is not for lone travellers.",
        "You came up with all your limbs and a better colour than most. That is progress.", None))
    A(Q("ucq_pd_sump", "Sump Samples", SAB, UC, 30, 31, "uc_sump",
        "Master Apothecary Lorrane Sable cannot prove it, but she suspects the sump water in the Plague Depths is carrying the plague "
        "to the Cistern's lower works. She wants six sealed vials of the sludge from the spore-things and the rot worms, to test.",
        [fetch("pd_sump_vial", 6)],
        "The Outer Cistern. Plague Spores and Rot Worms. Six vials, stoppers on. If you drop one, don't tell me.",
        "Six. Green-grey. Warm. Not natural, not remotely. Someone is feeding this on purpose. Thank you.", "ucq_pd_vex",))
    A(Q("ucq_pd_vex", "The Plagueweaver", SAB, UC, 31, 32, "uc_plague",
        "The sludge reads like a recipe: a familiar hand, a familiar flourish. It is Vex's. The Plagueweaver of the Society's inner "
        "circle weaves the plague through the Weaving Hall's looms, and she is not working for the Dark Lady any more.",
        [boss("Plagueweaver Vex", PD)],
        "The Weaving Hall, west of the Mid Conduit. She was a friend once. That is the worst of it.",
        "Her needle. Of course. She always did sew too tightly. Thank you - and I am sorry you had to do it.", None,
        requires_quests=["ucq_pd_sump"]))
    A(Q("ucq_pd_notes", "The Surgeon's Notes", MAR, UC, 31, 32, "uc_apoth",
        "Marwen has heard rumours that the Plague Surgeons are the Society's loyal hands, taking notes for a clinical record of "
        "the plague's progress. If there is a ledger of the spread, she wants it. Five pages from the surgeons.",
        [fetch("pd_surgeon_notes", 5)],
        "The Lab wing. Plague Surgeons. The pages are bloodied but legible. Five.",
        "Five pages. A neat hand, a steady one, and a growing unease in the last entries. We know how it spreads now.", None,))
    A(Q("ucq_pd_ledger", "The Court's Ledger", SEN, UC, 31, 32, "uc_plague",
        "Loremaster Sennarath knows who the conspirators bribed, because the Blighted Courtiers of the Throne of Rot keep a ledger of "
        "every favour. She wants four copies of the courtier ledger from the Court, to compare against Wrenfall's lists.",
        [fetch("pd_courtier_ledger", 4)],
        "The Court of Rot, north-west wing. The Blighted Courtiers. Four ledgers, any condition. I can read through a stain.",
        "Names, dates, sums. Every one struck through, and every sum still correct. Terrifying and tidy. Thank you.", None,))
    A(Q("ucq_pd_noble", "The Infected Noble", EXE, UC, 32, 33, "uc_court",
        "The Faulkner line was Lordaeron nobility. The last Faulkner was murdered in his bed, raised in a vat, and given a signet he "
        "does not remember. The Society dressed him as a figurehead for the coup. Wrenfall wants the figurehead removed and the signet recovered.",
        [boss("The Infected Noble", PD), fetch("pd_noble_signet", 1)],
        "Throne of Rot, the Plague Depths' west wing. Kill him. Take the signet off the body. Do not wear it.",
        "A dead man's ring on a dead man's finger. Good. It goes in the vault, and the vault stays shut.", None,
        requires_quests=["ucq_pd_ledger"]))
    A(Q("ucq_pd_voss", "Voss's Codex", SEN, UC, 32, 33, "uc_plague",
        "Plague Keeper Voss keeps the Archive: a thousand recipes, a thousand formulae, and the notes that tie them together. "
        "Sennarath wants the Codex, in one piece, and Voss out of the way of it.",
        [boss("Plague Keeper Voss", PD), fetch("pd_voss_codex", 1)],
        "The Blight Archive, east wing. Voss is a careful curator. Be more careful.",
        "A thousand recipes, one ledger. The conspiracy is on every page. We may yet outpace it.", None,
        requires_quests=["ucq_pd_ledger"]))
    A(Q("ucq_pd_vats", "Vat-Born Tissue", "uc_surgeon", UC, 32, 33, "uc_sump",
        "Surgeon Halvard needs to see what the Society has been growing in the Vault of Flesh. The failed experiments carry fistfuls "
        "of tissue still working out what they were supposed to be. Five samples will tell him how long the vats have been running.",
        [fetch("pd_vat_tissue", 5)],
        "The Vault of Flesh, east wing. Failed Experiments. Gloves on. Don't think about the faces.",
        "Five. Fresh, grey and still trying. The vats have been running longer than anyone told me.", "ucq_pd_abomination",))
    A(Q("ucq_pd_abomination", "What the Vats Grew", "uc_surgeon", UC, 33, 34, "uc_sump",
        "The tissue samples point to a single source: a creature at the heart of the Vault of Flesh, still growing. Halvard calls it the "
        "Vile Plague Abomination. It does not recognise anything as a friend.",
        [boss("Vile Plague Abomination", PD)],
        "The Vault of Flesh, deepest chamber. It is large, loud and wet. Bring a healer.",
        "Growth stopped. Marvellous and terrible. The Society should be ashamed. Take the pick of what's left.", None,
        requires_quests=["ucq_pd_vats"]))
    A(Q("ucq_pd_zulketh", "The Heart of the Plague", SAB, UC, 34, 34, "uc_plague",
        "Vex, the Noble, Voss and the Abomination were the Society's four limbs. Zul'keth is the heart, a Dark Sorcerer who "
        "believes the Dark Lady has failed, and who has built a pulsing furnace of plague under the city to prove it. End him, and the "
        "Society's coup ends with him.",
        [boss("Dark Sorcerer Zul'keth", PD)],
        "The Plague Heart, the deepest room. Everything you've killed so far was his. Finish it.",
        "It beats no more. The Society is leaderless and the Dark Lady is still on her throne. Take her gratitude, and mine.", "ucq_pd_report",
        mult=1.6, requires_quests=["ucq_pd_vex", "ucq_pd_noble", "ucq_pd_voss", "ucq_pd_abomination"],
        grant_items={"on_turn_in": [dict(item_id="uc_sable_report", name="Sable's Sealed Report",
                                         description="Four pages and a seal. The conspiracy in full, signed off by the one person who could.",
                                         count=1)]}))
    A(Q("ucq_pd_report", "The Dark Lady's Gratitude", SAB, UC, 34, 34, "uc_court",
        "Master Apothecary Sable has written the whole sorry tale of the Society's coup into a sealed report. It needs to reach the "
        "Queen herself - not by messenger, not by raven, but by the hand that finished it.",
        [deliver("uc_sable_report", "Take Sable's report to Lady Sylvanas")],
        "The Royal Quarter's great hall. Hand it to her. Do not say anything clever.",
        "She reads it, slowly. She says nothing. Then she says: 'The Forsaken do not forget.' That is as close to thanks as the Dark Lady gets.",
        None, mult=1.4, turn_in_npc_id=SYL, requires_quests=["ucq_pd_zulketh"]))
    return Z


# ---- drops -----------------------------------------------------------------------------------------------------------------
STARTER_DROPS = {      # item_id: (name, description, quest_id, [(creature, chance)])
    "uc_stray_vial": ("Unsealed Plague Vial", "A sealed vial taken off a courier, stamped with the Apothecary Society's wax. A hairline crack.",
                      "ucq_stray_vial", [("Plagued Courier", 0.18)]),
    "uc_groundskeeper_scrap": ("Groundskeeper's Ledger Scrap", "A torn fragment of a ledger in the Cult's cipher, folded small.",
                               "ucq_groundskeeper_scrap", [("Skeletal Groundskeeper", 0.14)]),
}


def main():
    Z = quests()
    ids = set()
    out = []
    for q in Z:
        assert q["quest_id"] not in ids, q["quest_id"]
        ids.add(q["quest_id"])
        rewards = q.pop("rewards")
        q["unique_item_defs"] = rewards
        q["gear_reward_gear_level"] = max(r["item_level"] for r in rewards)
        if any(r["rarity"] == "rare" for r in rewards):
            q["gear_reward_rarity"] = "rare"
        out.append(q)
    for q in out:
        n = q["next_quest_id"]
        assert n is None or n in ids, (q["quest_id"], n)
    OUT.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n")

    dd = json.loads(DROPS.read_text())
    drops = dd["drops"]
    for item_id, (name, desc, qid, srcs) in STARTER_DROPS.items():
        assert qid in ids, qid
        for creature, chance in srcs:
            lst = drops.setdefault(creature, [])
            lst[:] = [d for d in lst if d["item_id"] != item_id]
            lst.append(dict(item_id=item_id, name=name, category="quest", description=desc, chance=chance, starts_quest=qid))
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n")
    print(f"undercity quests: {len(out)} (hub {sum(1 for q in out if q['level_max'] < 30)}, "
          f"plague depths {sum(1 for q in out if q['level_max'] >= 30)}), items {sum(len(q['unique_item_defs']) for q in out)}")


if __name__ == "__main__":
    main()
