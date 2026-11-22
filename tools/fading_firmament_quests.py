"""
The Fading Firmament's quests (57-60): the dying heart of Caelora, the last of the sky. Read by
tools/build_fading_firmament_quests.py, which holds them to every rule before anything is written. The map is
tools/handbuilt_worldtree_fading_firmament.py and the people are tools/build_fading_firmament_people.py. You come up the
Firmament Road from the Ascendant Bastions (abq_the_road_north, Lookout Fen Arden's last) onto the Road's End.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026): the Firmament was the oldest ground in the sky, and it's been dying for
centuries. Its people left in stages. The player is the newcomer.

THE THREADS (about 80% from the two hubs, Lastlight and Forgewatch):
  The general: Magister Orla Thessan followed her student north. Her trail, her orders, her wardens, and at the end the
    general herself, beaten and taken alive (Kyle, 21 Nov 2026), handed to the council. The magistrate sends word to
    Aurelion, and the First Speaker's answer is the arc's end: the council will send to Orgrimmar (the brief's twenty
    questions, 20: "They integrate themselves more in with the horde").
  The last people: the magistrate, the shrine's keeper and its crystal-cutter, the skiffmaster and the two Earthborn at
    Lastlight (a scrapman from Durban, a teacher from Umea), the two who won't leave their ground.
  The forge: the House of Long Memory at Forgewatch, its rune-reader and an Earthborn smith from Kumasi; the three
    hearths, and down into the Hearthdeep, the Wellspring and the Hollow Engine. THE SKY'S ONE MYSTERY, the Firmament's
    piece (docs/worldtree_brief.md): the Wellspring, where the wellstones were grown, took all three peoples to work.
    It says nothing about why they stopped, or about what's killing the sky.
  The turncoat: the Ascendancy's quartermaster behind the Siege Line, who has stopped wanting to feed the fleet.
  The links (world/links.py): the skiffmaster sends you out on the dusk currents, and the shrine's keeper over the
    skip-stone to the Rim, so the first quests teach them.

THE RULES IT KEEPS: transplants are factionless; the Aetherians only ever say they don't know what the change was, and
nothing about the three peoples points at it. VOICE (Kyle): whole sentences the way a person says them, contractions,
no dashes, no sentence of one or two words, the useful thing first, every kill target named, no count beside an
objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

FF = "fading_firmament"
#: the caves (tools/handbuilt_hearthdeep.py, handbuilt_wellspring.py, handbuilt_hollow_engine.py)
HD, WS, HE = "the_hearthdeep", "the_wellspring", "the_hollow_engine"
AURELION_SPEAKER = "au_first_speaker"

# ---- the Road's End
WARDEN = "ff_road_warden"
# ---- Lastlight
SABINE, ILSE, ORLA, DORRAN = "ff_shrine_keeper", "ff_last_magistrate", "ff_orla", "ff_skiffmaster"
ANSEL, SIPHO, MARGIT = "ff_lamp_cutter", "ff_salvager", "ff_child_minder"
# ---- the House of Long Memory, whose rooms moved from Forgewatch into Lastlight (22 Nov 2026, Kyle's town rule)
THEODORA, RHUN, KWABENA, CORRA = "ff_long_memory", "ff_forge_scholar", "ff_earthborn_smith", "ff_forgewatch_guard"
# ---- out on the islands
BENEDEK, YLLEN, IVO = "ff_last_resident", "ff_gardener", "ff_turncoat"

#: everyone who stands in Lastlight, the Firmament's town (its own map since 22 Nov 2026)
HUB_GIVERS = {SABINE, ILSE, ORLA, DORRAN, ANSEL, SIPHO, MARGIT, THEODORA, RHUN, KWABENA, CORRA}
#: the Aetherians pay the Aetherians; the Earthborn pay nobody
SKY_GIVERS = {WARDEN, SABINE, ILSE, ORLA, DORRAN, ANSEL, THEODORA, RHUN, CORRA, BENEDEK, YLLEN, IVO}


def k(target, n, zone=FF):
    return kill(target, n, zone=zone)


def boss(target, zone=FF):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=FF, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Fading Wisp": [("ff_q_guttering_light", "Guttering Light", "A little light caught out of a Fading Wisp, still "
                     "warm. The shrine at Lastlight can burn it.")],
    "Ascendancy Cutter": [("ff_q_forge_crystal", "Unspent Forge Crystal", "A crystal an Ascendancy Cutter prised out "
                           "of the Threefold Forge's hearth. It's never been used, and it still holds its light.")],
    "Broken Construct": [("ff_q_gear_assembly", "Working Gear Assembly", "A gear assembly out of a Broken Construct "
                          "that still turns when you push it. Up here that makes it valuable.")],
    "Quarter Sentinel": [("ff_q_school_slate", "Schoolroom Slate", "A child's writing slate from the Emptied Quarter's "
                          "school, kept safe for forty years by the Quarter Sentinel that took it.")],
    "Waking Forge-Guardian": [("ff_q_flue_stone", "Rune-Cut Flue Stone", "A stone off a Waking Forge-Guardian's "
                               "shoulder, cut with Kharad runes too big to read close up.")],
    "Ascendancy Scavenger": [("ff_q_family_silver", "Saar Family Silver", "A bundle of old silver cups and spoons an "
                              "Ascendancy Scavenger carried out of a house in the Emptied Quarter.")],
    "Siege Legionary": [("ff_q_sealed_orders", "Sealed Fleet Orders", "Orders under the Ascendant-General's own seal, "
                         "carried by a Siege Legionary for the Moorage.")],
    "Siege Artillerist": [("ff_q_supply_ledger", "Fleet Supply Ledger", "A Siege Artillerist's copy of the fleet's "
                           "supply ledger: grain, crystal and shot, and a date at the bottom of every page.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [131]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=FF, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
COLDFORGE_YARD = (90, 52)     # the Coldforges' yard, where the general's crews strip the forges
FORGE_RING = (172, 22)        # the broken rune circle among the three hearths
GIANTS_HEARTH = (166, 18)     # before the giant's hearth
SINGERS_HEARTH = (180, 32)    # before the singer's hearth, on its perch
CUTTERS_HEARTH = (160, 36)    # before the cutter's hearth
WOUNDS_EDGE = (112, 126)      # the Wound's Edge, where the skip-stone sets you down
PIER = (176, 122)             # the Moorage's pier, out over the Wound
LAST_GREEN = (28, 34)         # where the current sets you down on the Last Green
ENGINES_LANDING = (220, 56)   # where the current from the Forge sets you down among the Dead Engines
TOY_BIRD = (56, 160)          # the toy bird on a step in the Emptied Quarter


def build():
    out = []
    A = out.append

    # =================================================================================== 0. THE ROAD (the warden)
    A(Q("ffq_the_road_up", "The Road Up", WARDEN, 57, 57, "Roadwarden's",
        "Warden Kael Ostry keeps count of everyone who comes up the Firmament Road. He wants his count taken to "
        "Magistrate Ilse Varrow at Lastlight.",
        [deliver("ff_q_road_count", "Take the warden's count to Magistrate Ilse Varrow at Lastlight")],
        "I write down everyone who comes up this road, and the magistrate reads it every evening. Three columns of "
        "soldiers this week, and you. Take her the count, and tell her I'd like a relief before I start counting "
        "the ground going.",
        "Three columns of soldiers. She's bringing everything she has.\n\nThank Kael for me. You're the first newcomer to come up "
        "that road in a month who wasn't wearing her colours, and Lastlight could use the help.",
        turn_in_npc_id=ILSE,
        grant_items=carry("ff_q_road_count", "Road Warden's Count", "Kael Ostry's count of everyone who's come up the "
                          "Firmament Road this month, in a careful hand.")))

    # =================================================================================== 1. THE GENERAL (Orla)
    A(Q("ffq_the_students_trail", "The Student's Trail", ORLA, 57, 58, "Lensbearer's",
        "Magister Orla Thessan followed Ascendant-General Maelis Ardane north. She wants to know where her old student "
        "has been, and what she was looking at.",
        [explore(*COLDFORGE_YARD, "Look at what's been stripped in the Coldforges' yard"),
         explore(*FORGE_RING, "Look at the rune circle among the Threefold Forge's hearths"),
         explore(*WOUNDS_EDGE, "Take the skip-stone and look out from the Wound's Edge")],
        "Maelis came to the Firmament before her army did. She walked it alone, the way she used to walk the "
        "Patient Lens's library. Go where she went: the Coldforges' yard, the old forge at the top of the Plate, and "
        "over the skip-stone to the Wound's Edge. I want to know what she saw.",
        "She stripped the forges, she stood among the three hearths, and she looked into the hole in the sky.\n\nShe "
        "always did read the sky better than any of us. I think she looked at all of it and decided the Firmament was "
        "lost, and that whatever's left in it should go to her fleet."))
    A(Q("ffq_the_generals_orders", "The General's Orders", ORLA, 59, 59, "Sealbreaker's",
        "The Siege Legionary carries the general's sealed orders to the Moorage. Magister Orla Thessan wants them read.",
        [fetch("ff_q_sealed_orders", 6)],
        "Every Siege Legionary on the line carries a copy of her orders under her own seal. I taught her to write, so "
        "I'll know her hand. Bring me what they're carrying, and I'll tell you when her fleet sails.",
        "The fleet sails for the tree in two days, with every crystal she's cut out of the Firmament in its "
        "holds.\n\nShe writes the way she always did, every line exact and nothing wasted. I used to be proud of that.",
        requires_quests=["ffq_the_students_trail"]))
    A(Q("ffq_the_flagship_wardens", "Her Wardens", ORLA, 60, 60, "Gangway",
        "The Flagship Warden and the Ascendant Battlemage guard the gangway to the general's flagship at the Moorage. "
        "Magister Orla Thessan wants the way cleared.",
        [k("Flagship Warden", 8), k("Ascendant Battlemage", 8)],
        "She won't leave the Moorage now, not this close to sailing. Her Flagship Wardens hold the gangway and her "
        "Ascendant Battlemages hold the pier. Clear them off, and she'll have to come out and see to it herself.",
        "The pier's empty. She'll come down to see why, because she always does.\n\nI'll be there when you face her. I "
        "owe her that, and I owe her teacher's last lesson.",
        requires_quests=["ffq_the_generals_orders"]))
    A(Q("ffq_the_last_lesson", "The Last Lesson", ORLA, 60, 60, "Ascendant-Breaker's",
        "Ascendant-General Maelis Ardane stands on the Moorage's pier. Magister Orla Thessan wants her beaten and "
        "taken alive.",
        [boss("Ascendant-General Maelis Ardane")],
        "Don't kill her. She's earned a council's judgment, not a quiet end on a pier. Break her ward and she'll "
        "yield, because she's never fought a fight she'd already lost. She's the best the Ascendancy "
        "ever had, and her fleet's guns are on that pier with her, so bring friends you trust.",
        "She yielded to you. She looked at me, and she said I'd taught her better than this, and she put down the blade.\n\n"
        "The Lens-Wardens will take her to Aurelion in chains, and the council will decide what she is now. Her fleet "
        "won't sail without her. That's what matters today. Tomorrow I'll have to decide whether I can still call her "
        "my student.",
        elite=True, requires_quests=["ffq_the_flagship_wardens", "ffq_the_supply_ledger"]))

    # =================================================================================== 2. THE MAGISTRATE (Ilse)
    A(Q("ffq_columns_on_the_road", "Columns on the Road", ILSE, 57, 57, "Lastlight",
        "The Column Legionary and the Column Storm Caller come up the road every few days, and the columns take what "
        "they want from Lastlight on the way past. Magistrate Ilse Varrow wants the next one turned back.",
        [k("Column Legionary", 10), k("Column Storm Caller", 8)],
        "Every column that comes up the road stops at Lastlight and takes something: food, crystal, a boy old enough "
        "to carry a lance. Since the change they've come every week. I can't stop them, but you can. Meet the next Column Legionary and Column Storm Caller at "
        "the Road's End, and send them back down.",
        "They went back down the road short of men, and they didn't stop at Lastlight on the way.\n\nThe columns will "
        "keep coming. But the next one will know we've got friends now, and that's worth more than you'd think.",
        requires_quests=["ffq_the_road_up"]))
    A(Q("ffq_the_ones_who_stayed", "The Ones Who Stayed", ILSE, 57, 58, "Magistrate's",
        "Old Benedek Saar won't leave his house in the Emptied Quarter. Magistrate Ilse Varrow wants food taken to him.",
        [deliver("ff_q_benedek_parcel", "Take the parcel to Old Benedek Saar in the Emptied Quarter")],
        "Benedek was born in his house, and he says he'll go when it does. I've stopped arguing with him. Take him "
        "this parcel, and tell him the magistrate says he's still on her books whether he likes it or not.",
        "Bread, oil and a letter from the magistrate. She still writes to me every week.\n\nTell her I'm well. Tell "
        "her the house is still standing, and that I'll let her know if it changes its mind.",
        turn_in_npc_id=BENEDEK, requires_quests=["ffq_the_road_up"],
        grant_items=carry("ff_q_benedek_parcel", "Parcel for Old Benedek", "Bread, oil and a sealed letter, wrapped "
                          "in the magistrate's own shawl.")))
    A(Q("ffq_scavengers_in_the_quarter", "Scavengers in the Quarter", ILSE, 57, 58, "Quarterwarden's",
        "The Ascendancy Scavenger strips the Emptied Quarter's houses for anything the fleet can use. Magistrate Ilse "
        "Varrow wants them gone.",
        [k("Ascendancy Scavenger", 10)],
        "Those houses are empty, but they're not abandoned. Every family that left meant to come back for what they "
        "couldn't carry, and some of the Earthborn at Lastlight sleep in those houses on the nights they're brave. The Ascendancy Scavenger doesn't care about that. Drive them out of the Quarter.",
        "The houses can keep their things a while longer.\n\nNobody's coming back for most of it, I know. But I keep "
        "the Firmament's books, and on my books the Quarter still belongs to the people who built it."))
    A(Q("ffq_word_to_the_council", "Word to the Council", ILSE, 60, 60, "Councilbound",
        "The general's taken. Magistrate Ilse Varrow wants her account of the Firmament carried to First Speaker "
        "Aldren Sorvaine in Aurelion.",
        [deliver("ff_q_magistrate_account", "Take the magistrate's account to First Speaker Aldren Sorvaine in Aurelion")],
        "The council's going to judge Maelis, and they'll do it without ever having seen the Firmament. I've written "
        "it all down: the nine towns, the forges, the ones who stayed. Take it to the First Speaker yourself. He'll "
        "read it if a hero hands it to him.",
        "The magistrate's account. I've read her reports for thirty years and never once gone to see.\n\nThe council "
        "met last night. We're smaller than we thought, and the world under the cloud is bigger and changing faster "
        "than we can study it. We're sending envoys to Orgrimmar. The Horde stood with us at the Crown, and we'll "
        "stand with them now. I wanted you to hear it first.",
        turn_in_npc_id=AURELION_SPEAKER, requires_quests=["ffq_the_last_lesson"],
        grant_items=carry("ff_q_magistrate_account", "The Magistrate's Account", "Ilse Varrow's account of the "
                          "Firmament's last years, bound in blue cloth and sealed for the First Speaker.")))

    # =================================================================================== 3. THE SHRINE (Sabine)
    A(Q("ffq_light_for_the_shrine", "Light for the Shrine", SABINE, 57, 58, "Shrinekeeper's",
        "The Fading Wisp carries a little light it's stolen out of the Firmament. Keeper Sabine Aldour wants it back "
        "for the shrine.",
        [fetch("ff_q_guttering_light", 8)],
        "The shrine burns light, not oil, and the Firmament's running out of it. The Fading Wisp drifts between the "
        "islands drinking what's left. Bring me the light they're carrying, and the shrine burns another season.",
        "That's a season. Maybe more, if the nights stay short.\n\nPeople ask me why it matters. It's the last lit "
        "shrine on the Firmament. While it's burning, the people here have a reason to stay, and a reason to believe "
        "the sky isn't finished yet."))
    A(Q("ffq_over_the_skip_stone", "Over the Skip-Stone", SABINE, 59, 60, "Skipstone",
        "The Wound Crawler and the Unmade Wisp are coming up out of the Wound's Edge. Keeper Sabine Aldour wants them "
        "driven back before they reach the Plate.",
        [k("Wound Crawler", 10), k("Unmade Wisp", 8)],
        "There's an old skip-stone in the Quarter that takes you across to the Rim. Stand on it and it carries you "
        "over the drop. Things are coming up out of the Wound now, the Wound Crawler and the Unmade Wisp, and every "
        "week they're nearer the stone. Go over and push them back.",
        "They'll come again, but not so soon.\n\nMy grandmother walked the skip-stones every day of her life. "
        "Nobody living knows who set them. They just work, the way the wellstones work, and we've stopped asking how.",
        requires_quests=["ffq_light_for_the_shrine"]))
    A(Q("ffq_the_unmade", "The Unmade", SABINE, 60, 60, "Unmaker's",
        "The Edge Gale tears at anyone on the Wound's Edge, and the shrine's keeper says the Unmade walks there now. "
        "Keeper Sabine Aldour wants the Edge made safe to stand on.",
        [k("Edge Gale", 8), explore(*WOUNDS_EDGE, "Stand on the Wound's Edge when you've cleared it")],
        "Since the change the Wound's been wider every year. The Edge Gale comes out of it and tries to throw people "
        "off, and the old ones at Lastlight say the Unmade walks the Edge itself. Clear the Edge Gale off, then go "
        "and stand there, so I can tell the camp somebody did.",
        "You stood on the Edge and came back. I'll tell them tonight.\n\nWe don't know what the Wound is, or what made "
        "it start to widen, and I don't think anyone does. The scholars have their theories, and every one of them is a guess.",
        requires_quests=["ffq_over_the_skip_stone"]))

    # =================================================================================== 4. THE CUTTER (Ansel)
    A(Q("ffq_crystals_to_cut", "Crystals to Cut", ANSEL, 58, 58, "Crystalcutter's",
        "The Ascendancy Cutter prises unspent crystal out of the Threefold Forge's hearth. Cutter Ansel Fennick wants it "
        "for the shrine.",
        [fetch("ff_q_forge_crystal", 6)],
        "I've got nothing left to cut. The Ascendancy Cutter has a whole forge to strip, and he's taking crystal "
        "that's never been burned. Bring me what they've cut out, and I'll make lamps of it for the shrine.",
        "Unspent forge crystal. I haven't held a piece this clear since I was an apprentice.\n\nIt'll make a dozen "
        "lamps. The camp will see them lit and think the sky's getting better. Let them think it a little while."))
    A(Q("ffq_drones_in_the_coldforges", "Drones in the Coldforges", ANSEL, 58, 58, "Coldforge",
        "The Salvage Drone and the Ascendancy Salvager are stripping the Coldforges bare. Cutter Ansel Fennick trained "
        "in those forges and wants them left alone.",
        [k("Salvage Drone", 8), k("Ascendancy Salvager", 8)],
        "I was apprenticed in the Coldforges when four of them still burned. Now the Ascendancy Salvager is cutting "
        "the last fittings out, and the Salvage Drone carries them off to the fleet. Stop them, before there's "
        "nothing left to remember them by.",
        "Thank you. The forges are cold, but they're whole.\n\nMy master used to say a forge isn't dead until somebody "
        "takes its anvil. They've still got their anvils."))

    # =================================================================================== 5. THE SKIFFS (Dorran)
    A(Q("ffq_kestrels_on_the_approach", "Kestrels on the Approach", DORRAN, 57, 58, "Skiffwing",
        "The Dusk Kestrel dives at the last skiff every time it comes into Lastlight. Skiffmaster Dorran Vale wants "
        "the approach cleared.",
        [k("Dusk Kestrel", 10)],
        "Mine's the last skiff that flies out of the Firmament, and every Dusk Kestrel between here and the Bastions "
        "has learned it carries food. They go for the sail. Clear them off the approach, and I'll keep flying.",
        "Not a feather on the sail this morning.\n\nSince the change I've carried more Earthborn out of here than Aetherians, and every one of them asks me where I'm taking them. I'll keep flying as long as there's somewhere to land. That's "
        "all a skiffmaster ever asks."))
    A(Q("ffq_riding_the_dusk_currents", "Riding the Dusk Currents", DORRAN, 58, 59, "Currentrider's",
        "The Firmament's old wind currents still run in two places. Skiffmaster Dorran Vale wants to know they still "
        "carry somebody across.",
        [explore(*LAST_GREEN, "Ride the dusk current from the Gardens out to the Last Green"),
         explore(*ENGINES_LANDING, "Ride the dusk current from the Threefold Forge to the Dead Engines")],
        "Two of the old currents still run, violet now instead of white. One goes out from the Greyfall Gardens to "
        "an islet with one tree on it, and one goes from the Threefold Forge over to the Dead Engines. Stand where "
        "they rise and they'll carry you. I'd go myself, but I'm too old to trust the wind.",
        "Both of them still carry. I'll mark them on the charts for whoever comes after you.\n\nWhen I was a boy the "
        "currents ran all over the Firmament, white as cloud, and we rode them to school. There are two left now, and that's better than none."))
    A(Q("ffq_eels_in_the_lines", "Eels in the Lines", DORRAN, 58, 59, "Driftline",
        "The Drift Eel coils in the gaps round the Breaking and fouls the skiff's lines. Skiffmaster Dorran Vale wants "
        "them cleared out.",
        [k("Drift Eel", 10)],
        "The Breaking sheds rock every day, and the Drift Eel follows the rock down. They wrap round my lines when I "
        "fly past. Clear them out of the gaps round the Breaking, and I'll take the south way home again.",
        "I flew the south way this morning and the lines came back clean.\n\nThe Breaking will be gone in a year or "
        "two. I'll fly past it as long as it's there."))

    # =================================================================================== 6. THE SCRAPMAN (Sipho, Earthborn)
    A(Q("ffq_scrap_that_works", "Scrap That Works", SIPHO, 59, 59, "Scrapman's",
        "The Broken Construct still has working parts in it. Sipho Ndlovu wants them for the camp's machines.",
        [fetch("ff_q_gear_assembly", 6)],
        "Back home in Durban I'd have paid good money for a gear assembly like the ones in a Broken Construct. Up "
        "here they're lying all over the Dead Engines, still turning. Bring me the ones that work, and I'll keep the "
        "camp's pumps running another year.",
        "Every one of these turns clean. You've got a good eye for scrap.\n\nI ran a yard in Durban for twenty years, "
        "and I never saw machines built this well. Whoever made them meant them to last forever."))
    A(Q("ffq_salvage_the_breaking", "Salvage the Breaking", SIPHO, 59, 59, "Salvager's",
        "The Unmoored Stone and the Hollow Storm keep Sipho Ndlovu off the Breaking. He wants to salvage it before it "
        "falls.",
        [k("Unmoored Stone", 8), k("Hollow Storm", 8)],
        "The Breaking's going to fall, and everything on it falls too. I want to get in there and strip what's worth "
        "having first. The Unmoored Stone and the Hollow Storm won't let me near it. Clear the way and I'll do the "
        "rest.",
        "I got three loads off before the ground cracked again.\n\nThe Aetherians think I'm mad for going out there. "
        "I tell them where I'm from, people don't waste anything the ground gives them."))

    # =================================================================================== 7. THE TEACHER (Annika, Earthborn)
    A(Q("ffq_slates_for_the_children", "Slates for the Children", MARGIT, 57, 58, "Schoolmistress's",
        "The Quarter Sentinel still guards the Emptied Quarter's school, and won't let anything be taken out. Annika "
        "Sjoberg wants its slates for her pupils.",
        [fetch("ff_q_school_slate", 6)],
        "I've got eleven children and nothing to write on. There's a school in the Emptied Quarter with a cupboard "
        "full of slates, and the Quarter Sentinel that still guards it won't let anyone carry one out. Bring me the "
        "slates, and I'll teach them their letters.",
        "The children will be thrilled to have slates of their own.\n\nI taught primary in Umea for twenty years. I never thought I'd "
        "teach Aetherian children to read Swedish rhymes on slates out of an empty town in the sky."))
    A(Q("ffq_a_bird_for_the_youngest", "A Bird for the Youngest", MARGIT, 57, 58, "Toymaker's",
        "The youngest child at Lastlight lost a toy bird in the Emptied Quarter when her family left. Annika "
        "Sjoberg wants to know if it's still there.",
        [explore(*TOY_BIRD, "Find the toy bird on a step in the Emptied Quarter")],
        "Little Wenna left a toy bird on her front step when her family left the Quarter. She talks about it every "
        "night. It's a little bronze bird that floats if you wind it. Go and see if it's still on the step.",
        "It's still there? She'll want to know it's waiting for her.\n\nIt can stay on the step. The bird's not the "
        "point. The point is that somebody went and looked."))

    # =================================================================================== 8. THE FORGE (Theodora, Long Memory)
    A(Q("ffq_three_hearths", "Three Hearths", THEODORA, 58, 58, "Long Memory",
        "The Threefold Forge has three hearths, each one cut differently. Archivist Theodora Quell wants each of them "
        "looked at.",
        [explore(*GIANTS_HEARTH, "Look at the giant's hearth"),
         explore(*SINGERS_HEARTH, "Look at the singer's hearth, on its perch"),
         explore(*CUTTERS_HEARTH, "Look at the cutter's hearth")],
        "The other houses call this the Old Forge, and say the Aetherians built it. Look at it properly. One hearth's "
        "big enough to stand in, one's set on a perch like a bird's, and one's cut for a smith of our height. Kwabena, our "
        "Earthborn smith, says no forge where he's from ever had three. Look at each of them closely, then tell me it "
        "was built by one people.",
        "A giant's hearth, a singer's perch and a cutter's bench, all round one anvil.\n\nThe House of Long Memory has "
        "said for a thousand years that the Kharad were here before us, and the other houses have laughed. I'm "
        "starting to think it's worse for them than that. I think we were never here alone."))
    A(Q("ffq_below_the_forge", "Below the Forge", THEODORA, 58, 59, "Flue-Walker's",
        "The Ascendancy Salvage-Cutter is digging into the Hearthdeep under the forge, and the Flue Guardian is "
        "fighting them. Archivist Theodora Quell wants the way down cleared.",
        [k("Ascendancy Salvage-Cutter", 8, zone=HD), k("Flue Guardian", 6, zone=HD)],
        "There's a stair under the forge into the Hearthdeep, where the three flues go down into the stone. The "
        "Ascendancy Salvage-Cutter is down there taking it apart, and the Flue Guardian wakes up and fights anyone in "
        "its flue. Clear the way so my scholars can follow you down.",
        "Three flues, cut for three peoples, all meeting over one anvil. Rhun's beside himself.\n\nThere's a deeper "
        "stair at the bottom, at the Confluence. Nobody's been down it. I'd like you to be the first.",
        requires_quests=["ffq_three_hearths"]))
    A(Q("ffq_the_wellspring", "The Wellspring", THEODORA, 59, 59, "Wellspring",
        "The Unsung, something the Ascendancy woke, is loose in the Wellspring under the Hearthdeep. Archivist Theodora "
        "Quell wants it put down, so she can read the place.",
        [boss("The Unsung", zone=WS)],
        "Below the Confluence there's a hall nobody's seen in a thousand years. The salvage crews went down to cut out "
        "what's there, and they woke something. My scholars call it the Unsung, because it howls instead of singing. "
        "Put it down, and let me read what's on the walls.",
        "I've been down. I've read the walls, and I've sat on the floor of that hall for an hour.\n\nThat's where the "
        "wellstones came from. The beds are giants' work, the seeds in them were cut by Aetherian hands, and the "
        "channels round them were cut for Veyr songs to run through. It took all three to make a wellstone. We've "
        "drunk from them for three hundred years and never known. The walls don't say why the three stopped. I "
        "don't think anyone left alive knows.",
        requires_quests=["ffq_below_the_forge"]))
    A(Q("ffq_the_seedbed_warden", "The Seedbed Warden", THEODORA, 59, 59, "Seedbed",
        "The Seedbed Warden still keeps the Wellspring's beds, and won't let anyone near them. Archivist Theodora "
        "Quell wants to study the beds.",
        [boss("The Seedbed Warden", zone=WS)],
        "There's a spirit in the west seedbeds, a Kharad, my scholar thinks, who's still keeping the beds after "
        "everyone else went. The Seedbed Warden won't let anyone near them. Lay it to rest gently, if you can, and "
        "let us study what it's been keeping.",
        "It went quietly at the end, Rhun says, like it was glad someone had finally come.\n\nThe seeds are still in "
        "the beds. They'll never grow without the other two peoples, but we can learn what they are.",
        requires_quests=["ffq_below_the_forge"]))

    # =================================================================================== 9. THE RUNES (Rhun)
    A(Q("ffq_runes_on_the_guardians", "Runes on the Guardians", RHUN, 58, 58, "Runereader's",
        "The Waking Forge-Guardian is cut with Kharad runes too big to read close up. Scholar Rhun Adaire wants the "
        "stones brought to him.",
        [fetch("ff_q_flue_stone", 6)],
        "Every Waking Forge-Guardian is cut with Kharad runes, but you can't read a giant's writing standing next to "
        "the giant. Bring me the stones off their shoulders, and I'll lay them out on the ground and read them "
        "properly.",
        "Laid out in a row, they say the same thing over and over. Keep the fire, keep the fire, keep the fire.\n\nThe "
        "guardians were told to keep the forge lit, and the forge went out anyway. They've been waking up to do their "
        "job ever since, and failing at it."))
    A(Q("ffq_the_salvage_master", "The Salvage-Master", RHUN, 59, 59, "Salvagebreaker's",
        "Salvage-Master Corin Hask runs the Ascendancy's crews in the Hearthdeep. Scholar Rhun Adaire wants him stopped "
        "before he cuts out the cutters' works.",
        [boss("Salvage-Master Corin Hask", zone=HD)],
        "Salvage-Master Corin Hask is cutting the cutters' works out of the Hearthdeep piece by piece, benches and "
        "racks and all, for the fleet. Those benches are a thousand years old. Stop him, before there's nothing left "
        "down there to read.",
        "The benches are still bolted down, and Hask won't be cutting anything for a while.\n\nThere are marks on "
        "every bench, the cutters' own, the same marks the masons put on the Spire Palace's hinges. It's the same "
        "people, a thousand years apart.",
        requires_quests=["ffq_below_the_forge"]))
    A(Q("ffq_the_bellows_warden", "The Bellows-Warden", RHUN, 59, 59, "Bellowsbreaker's",
        "The Bellows-Warden keeps the Confluence's draught, and attacks anything that gets in its way. Scholar Rhun "
        "Adaire wants to reach the deep anvil.",
        [boss("The Bellows-Warden", zone=HD)],
        "The Bellows-Warden stands over the deep anvil at the Confluence, pumping air down flues that haven't held a "
        "fire in centuries. It thinks it's keeping the forge alive. I need to read the anvil, and it won't let me "
        "near. Put it down.",
        "The anvil's cut on three sides, one in each people's hand. The giants' side says strike, the singers' side "
        "says sing, and ours says cut.\n\nIt doesn't say what you get when you do all three. I think we found that "
        "out in the Wellspring.",
        requires_quests=["ffq_below_the_forge"]))

    # =================================================================================== 10. THE SMITH (Kwabena, Earthborn)
    A(Q("ffq_storms_in_the_flue", "Storms in the Flue", KWABENA, 58, 58, "Smith's",
        "The Hearth-Bound Storm comes up out of the forge's flues and scorches the camp. Kwabena Osei wants it put out.",
        [k("Hearth-Bound Storm", 10)],
        "A forge is meant to draw air down, not throw storms up. Every night a Hearth-Bound Storm comes out of the "
        "flues and burns the tents. Put them out, and I'll get on with learning how this thing worked.",
        "The tents didn't burn last night. Thank you.\n\nBack in Kumasi I'd have banked the fire and gone home. This "
        "forge hasn't had a fire in a thousand years, and it still throws sparks. I want to know how."))
    A(Q("ffq_the_hollow_engine", "The Hollow Engine", KWABENA, 59, 59, "Enginebreaker's",
        "The Black Lattice has grown in the dead core of the greatest engine on the Dead Engines. Kwabena Osei wants to "
        "see the engine's heart without it in the way.",
        [boss("The Black Lattice", zone=HE)],
        "The biggest of the Dead Engines has a hatch at its foot, and inside it's a machine the size of a town. "
        "Something's grown in its burned-out core, black crystal in a lattice, and it attacks anything that comes "
        "near. Kill it, and I'll go in and see how the engine was built.",
        "I walked the whole engine after you'd cleared it. I've never seen work like it.\n\nThe gears are cut by one "
        "hand and the crystal by another, and the casing's quarried the way the giants quarried. It's the forge all "
        "over again."))
    A(Q("ffq_the_last_governor", "The Last Governor", KWABENA, 59, 59, "Governor's",
        "The Last Governor keeps trying to restart the Hollow Engine, and the engine shakes the Dead Engines every time "
        "it tries. Kwabena Osei wants it switched off.",
        [boss("The Last Governor", zone=HE)],
        "There's a construct in the Hollow Engine's east gallery, the Last Governor, and it's spent centuries trying "
        "to start the engine again. Every time it tries, the whole island shakes. Switch it off before it shakes "
        "the island loose.",
        "It's quiet now, and so's the island.\n\nI almost felt sorry for it. It was doing its job. The engine just "
        "wasn't ever going to start again, and nobody was left to tell it.",
        requires_quests=["ffq_storms_in_the_flue"]))

    # =================================================================================== 11. THE GUARD (Corra)
    A(Q("ffq_cutters_at_the_door", "Cutters at the Door", CORRA, 58, 59, "Forgewarden's",
        "The Ascendancy Cutter works the Threefold Forge right up to Forgewatch's tents. Lens-Warden Corra Hale wants "
        "them pushed back.",
        [k("Ascendancy Cutter", 10)],
        "The Ascendancy Cutter comes up to the edge of the camp every day now, cutting crystal out of the hearths. "
        "They haven't come into the tents yet. I'd like it to stay that way. Push them back off the forge.",
        "They're working the far side now, well away from the tents.\n\nThe Archivist says this forge is the most "
        "important place in the sky. I don't know about that. I know it's my camp, and nobody cuts anything in it."))
    A(Q("ffq_dead_engine_golems", "The Dead Engines", CORRA, 59, 59, "Engineguard's",
        "The Dead-Crystal Golem and the Void-Touched Drifter roam the Dead Engines, and the scholars want to study "
        "there. Lens-Warden Corra Hale wants it made safe.",
        [k("Dead-Crystal Golem", 8), k("Void-Touched Drifter", 8)],
        "Ride the current across from the forge to the Dead Engines, and you'll find a Dead-Crystal Golem at every "
        "engine and a Void-Touched Drifter in every shadow. The Archivist wants her scholars over there next week. "
        "Make it safe enough that I can let them go.",
        "I'll send them over with an escort, but I'll send them.\n\nThe drifters frighten me more than the golems. A "
        "golem's just stone. Nobody knows what the drifters are, or what they want out of the dark."))

    # =================================================================================== 12. OUT ON THE ISLANDS
    A(Q("ffq_crawlers_on_my_street", "Crawlers on My Street", BENEDEK, 57, 58, "Streetkeeper's",
        "The Quarter Crawler comes up through the cracks in Old Benedek Saar's street. He wants them gone.",
        [k("Quarter Crawler", 10)],
        "There's a crack in the street outside my door, and every night a Quarter Crawler comes up out of it. I'm too "
        "old to fight them and too stubborn to leave. Clear them off my street, and I'll sleep for once.",
        "I haven't heard my street this quiet in years.\n\nMy mother kept this street swept every morning of her "
        "life. I can't sweep it any more, but I can keep it free of crawlers, with a little help."))
    A(Q("ffq_the_family_silver", "The Family Silver", BENEDEK, 57, 58, "Saar",
        "The Ascendancy Scavenger carried off the Saar family's silver. Old Benedek Saar wants it back.",
        [fetch("ff_q_family_silver", 5)],
        "They came into my house while I slept and took my mother's silver. An Ascendancy Scavenger has it now, in a "
        "sack bound for the fleet. It's no use to anyone but me. Bring it back.",
        "My mother's cups. My grandmother's spoons. All of it.\n\nThey'll go back on the shelf where they belong, and "
        "when the house goes, they'll go with it. That's how it should be.",
        requires_quests=["ffq_crawlers_on_my_street"]))
    A(Q("ffq_ash_off_the_leaves", "Ash off the Leaves", YLLEN, 58, 58, "Greenkeeper's",
        "The Ash Puffball bursts over the Greyfall Gardens and buries what's left in grey ash. Gardener Yllen Moss "
        "wants it cleared before the ash reaches the last tree.",
        [k("Ash Puffball", 10)],
        "Every Ash Puffball in the Gardens bursts when the wind gets up, and the ash blows out over the drop to my "
        "tree. A tree can't breathe through ash. Clear them out of the Gardens before they bury the last green thing "
        "on the Firmament. The Earthborn children at Lastlight call it the Christmas tree, and I haven't the heart to "
        "ask them what that means.",
        "The wind came up this morning and there wasn't any ash in it.\n\nI don't know why this tree's still alive "
        "when the rest went grey. I just know I want it to stay that way."))
    A(Q("ffq_the_pale_stags", "The Pale Stags", YLLEN, 58, 58, "Stagwarden's",
        "The Pale Stag strips the bark off the Gardens' last trees. Gardener Yllen Moss wants the herd thinned.",
        [k("Pale Stag", 8)],
        "The stags used to be gold. Now they're pale as the grass, and the Pale Stag eats the bark off anything still "
        "standing. If they find the current out to my tree, it's gone. Thin the herd in the Gardens.",
        "The herd's thinner, and the bark's staying on the trees.\n\nI'm sorry for the stags. They used to be the "
        "most beautiful thing in the Gardens. They're just hungry, like everything else up here.",
        requires_quests=["ffq_ash_off_the_leaves"]))
    A(Q("ffq_the_supply_lines", "The Supply Lines", IVO, 59, 60, "Quartermaster's",
        "The Bombardier Construct and the Vanguard Sky Lancer guard the Siege Line's supply camp. Quartermaster Ivo "
        "Darrance wants the fleet's supplies left unguarded.",
        [k("Bombardier Construct", 8), k("Vanguard Sky Lancer", 8)],
        "I fed the Ascendancy for twenty years. I've seen the general call the Earthborn in the Yard Pens a resource, and "
        "now I'd like her army to go hungry. The Bombardier Construct and the "
        "Vanguard Sky Lancer guard every crate on the Siege Line. Thin them out, and the supplies won't get to the "
        "Moorage on time.",
        "Half the wagons didn't move yesterday.\n\nThe general will notice, because she notices everything. But she can't sail "
        "a fleet that hasn't eaten, and I know exactly how long that fleet can go without."))
    A(Q("ffq_the_supply_ledger", "The Supply Ledger", IVO, 59, 60, "Ledgerkeeper's",
        "The Siege Artillerist carries copies of the fleet's supply ledger. Quartermaster Ivo Darrance wants them, to "
        "show what the fleet's carrying and where.",
        [fetch("ff_q_supply_ledger", 6)],
        "Every Siege Artillerist on the line has a copy of the ledger, so they know what shot to draw. Bring me the "
        "copies. I wrote the first one, and I'll show you what the general's taking to the tree.",
        "Grain for a year, crystal from every forge on the Firmament, and shot for a siege.\n\nShe isn't going to "
        "study the tree. She's going to take it, and anchor what's left of the sky to it, whatever it costs the "
        "people living on it. I won't feed that.",
        requires_quests=["ffq_the_supply_lines"]))
    A(Q("ffq_the_vanguard", "The Vanguard", IVO, 60, 60, "Vanguard",
        "The Moorage Marine and the Siege Legionary will board the fleet first. Quartermaster Ivo Darrance wants the "
        "vanguard broken before it sails.",
        [k("Moorage Marine", 8), k("Siege Legionary", 8)],
        "The Moorage Marine boards first, and the Siege Legionary follows. They're the ones who'll land on the tree "
        "and hold it while the rest come up. Break the vanguard now, and there's nobody to land first.",
        "The vanguard's broken. The general will have to come down and put it back together herself.\n\nWhen she "
        "does, she'll be on the pier, in the open, for the first time since she came north.",
        requires_quests=["ffq_the_supply_ledger"]))

    return out
