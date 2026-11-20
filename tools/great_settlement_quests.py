"""
The Great Settlement's quests: the Highbough Tribes' city in the heart of the World Tree (44-48). Read by
tools/build_great_settlement_quests.py, which holds them to every rule before anything is written. The brief is
docs/worldtree_brief.md; the city is tools/handbuilt_worldtree_great_settlement.py.

A city's set, not a zone's: every giver stands in the Settlement, and the work sends you back down to the Lower Boughs
or out to Orgrimmar. The threads:
  The audience: up the Great Lift, past the gate, to High Chieftain Zan'kaji, who wants the Bloodscalp's war leader
    on the tiers below dealt with before he trusts you with the tribes' business.
  Horde ground: Orgrimmar's envoy has waited a year for an answer. Zan'kaji gives him one, and you carry it to Thrall.
  Sky-bones: the scholars' wall of things fallen from the clouds, and what's hidden in the Silkwood's webs.
  The ward: Grandmother Ozai's lanterns, and the bat handler's bat lost in the webs below.
  Two transplants: Kofi Mensah wants a taste of home for the market, and Hana Sato wants a leaf that brews like tea.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. Earth comes up from the two
transplants and from trolls who've met them.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

GS = "great_settlement"
LB = "lower_boughs"
ORG = "orgrimmar"

# ---- the city
OZENNA, ZANKAJI, GRUKK, YENVAA, TELZAN = "gs_liftkeeper", "gs_zankaji", "gs_orc_envoy", "gs_scholar", "gs_scholar_hall"
OZAI, RUZKAH, KOFI, HANA, VASHI = "gs_ward_elder", "gs_flight_master", "gs_transplant_a", "gs_transplant_b", "gs_loa_priest"
ULANI = "gs_gardener"
TAGU = "gs_highlift_keeper"      # at the High Lift, not in the hub
# ---- elsewhere (turn-ins only)
THRALL = "org_thrall"
VOKRA = "mb_shadowhunter"

HUB_GIVERS = {OZENNA, ZANKAJI, GRUKK, YENVAA, TELZAN, OZAI, RUZKAH, KOFI, HANA, VASHI, ULANI}
TRIBE_GIVERS = HUB_GIVERS - {KOFI, HANA, GRUKK} | {TAGU}


def k(target, n, zone=LB):
    return kill(target, n, zone=zone)


def boss(target, zone=LB):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=LB, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Glimmerwing Moth": [("gs_q_lantern_dust", "Pinch of Glimmer Dust", "Wing dust from a Glimmerwing Moth. It glows "
                          "faintly gold, and the ward's lamplighters mix it into their lantern oil.")],
    "Silkwood Weaver": [("gs_q_webbed_crystal", "Web-Wrapped Crystal", "A chip of blue crystal wrapped tight in "
                         "spider silk. It's warm through the web.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [4]        # starts where twelve quests still cover the five combos the reward check wants


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=GS, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places on the Lower Boughs (checked)
SILK_NEST = (164, 104)          # the spiders' web-hall in the Silkwood


def build():
    out = []
    A = out.append

    # =================================================================================== 1. THE AUDIENCE
    A(Q("gsq_an_audience", "An Audience", OZENNA, 45, 45, "Liftwarden's",
        "Liftwarden Ozenna keeps the top of the Great Lift. Anyone the elders below send up is meant to present "
        "themselves to the High Chieftain, and she's written you a pass for the guards on the Rise.",
        [deliver("gs_q_lift_pass", "Present Ozenna's pass to High Chieftain Zan'kaji on the Chieftain's Rise")],
        "Tal'vani sent word you were coming up. Everybody she sends goes to the High Chieftain first, so take this "
        "pass and go along the ledge to the Heart Palace. You'll know it, it's the one wrapped round the trunk.",
        "Ozenna's pass, and Tal'vani's word before it. The tribes have been talking about you since Mossroof.\n\nMy name's "
        "Zan'kaji, and I hold this tree for the tribes who climbed it, and I don't hand out trust for a good story. Show "
        "me what you can do and we'll talk about what the tribes can do for you.",
        turn_in_npc_id=ZANKAJI, nxt="gsq_the_war_below",
        grant_items=carry("gs_q_lift_pass", "Liftwarden's Pass", "A strip of painted bark with Ozenna's mark on it, "
                          "for the guards on the Chieftain's Rise.")))
    A(Q("gsq_the_war_below", "The War Below", ZANKAJI, 45, 45, "Chieftain's",
        "High Chieftain Zan'kaji wants the Bloodscalp who climb onto the Great Bough broken, and their war leaders "
        "with them, before he trusts you with the tribes' business.",
        [k("Bloodscalp Reaver", 6), k("Bloodscalp Bough-Shaman", 4)],
        "The Bloodscalp come up the ropes at the Climbers' Cut, down on the Lower Boughs, and their Bloodscalp Reavers "
        "lead every climb. Their Bloodscalp Bough-Shamans call the storm down on anyone who's in their way. Go "
        "down and break them, and come back and tell me how it went.",
        "That's the kind of story I like, one with the ending already done.\n\nThe tribes will hear about this. "
        "From now on, when the Settlement needs something done, my people will come to you first.",
        nxt="gsq_horde_ground"))

    # =================================================================================== 2. HORDE GROUND
    A(Q("gsq_horde_ground", "Horde Ground", GRUKK, 45, 46, "Envoy's",
        "Envoy Grukk has waited a year for Zan'kaji's answer to Orgrimmar. The High Chieftain has finally given it, "
        "and Grukk would rather it went to Thrall with someone who's earned the tribes' trust.",
        [deliver("gs_q_zankajis_answer", "Carry Zan'kaji's answer to Thrall in Orgrimmar")],
        "A year I've sat on this terrace waiting, and he gives me his answer the week you turn up. I'd carry it "
        "myself, but I've been told to wait for the next one. Take it to Thrall in Grommash Hold, and take the bats "
        "from the Roost, they're faster than the boats.",
        "The tree isn't Horde ground, and it isn't Alliance ground either. It's theirs, and they'll stand with us "
        "when we stand with them.\n\nThat's a better answer than most I get. Tell Zan'kaji that Orgrimmar heard "
        "him, and that the Horde remembers who held the line when the world broke.",
        turn_in_npc_id=THRALL, requires_quests=["gsq_the_war_below"],
        grant_items=carry("gs_q_zankajis_answer", "Zan'kaji's Answer", "A sealed letter on bark, painted with the "
                          "Highbough's teal and red, for the Warchief.")))

    # =================================================================================== 3. SKY-BONES
    A(Q("gsq_the_wall_of_fallen_things", "The Wall of Fallen Things", YENVAA, 45, 46, "Skywatcher's",
        "Scholar Yenvaa keeps the wall in the market where the scholars show what's fallen from the clouds. The "
        "spiders below have been wrapping crystal chips in silk, and she wants them for the wall.",
        [fetch("gs_q_webbed_crystal", 5)],
        "Every piece on this wall's fallen out of the sky and caught in the branches. The Silkwood Weavers down in the "
        "Silkwood on the Lower Boughs have been wrapping the crystal chips up like prey. Get me some of them, silk and all.",
        "Look at the cut on these. Every one the same angle, and every one still warm.\n\nThey're not jewels. "
        "They're parts of something, and whatever it is, it was running when it broke.", nxt="gsq_into_the_web_hall"))
    A(Q("gsq_into_the_web_hall", "Into the Web-Hall", YENVAA, 46, 46, "Webcutter's",
        "Yenvaa's sure the biggest pieces are in the spiders' web-hall at the far end of the Silkwood, and she wants "
        "someone to go and look.",
        [explore(*SILK_NEST, "Search the spiders' web-hall at the end of the Silkwood"), k("Silkwood Stalker", 5)],
        "The biggest pieces must be in the web-hall at the far end of the Silkwood, where the spiders keep what they "
        "can't eat. Go and look for me. The Silkwood Stalkers will drop on you from the webs, so watch above you.",
        "A whole crystal, bigger than my fist, in a cocoon of silk. The spiders were guarding it like an egg.\n\n"
        "Tel'zan in the scholars' hall will want to write this down. Everything that comes off this wall, he "
        "writes down.", nxt="gsq_the_record"))
    A(Q("gsq_the_record", "The Record", YENVAA, 46, 46, "Archivist's",
        "Yenvaa wants the crystal from the web-hall entered into the scholars' record. Archivist Tel'zan keeps it in "
        "the scholars' hall at the Roost.",
        [deliver("gs_q_great_crystal", "Take the crystal to Archivist Tel'zan in the scholars' hall at the Roost")],
        "Tel'zan keeps the record of everything that's fallen from the sky, and he'll want to see this before it "
        "goes on the wall. Take it across the bridge to the scholars' hall at the Roost.",
        "That's the biggest piece anyone's brought me, and the record's three years long.\n\nThe pieces are "
        "getting bigger every month. Whatever's up there, it's coming apart faster than it was, and one day something "
        "a lot bigger than a crystal is going to fall on this city.",
        turn_in_npc_id=TELZAN,
        grant_items=carry("gs_q_great_crystal", "Cocooned Crystal", "A blue crystal as big as a fist, still wrapped in "
                          "spider silk. It hums very softly.")))

    # =================================================================================== 4. THE WARD
    A(Q("gsq_the_wards_lanterns", "The Ward's Lanterns", OZAI, 45, 46, "Lamplighter's",
        "Grandmother Ozai's ward burns glimmer dust in its lanterns, which gives the light its gold. The lamplighters "
        "have run short, and the moths on the tiers below are the only place it comes from.",
        [fetch("gs_q_lantern_dust", 8)],
        "Our lanterns burn with a pinch of glimmer dust in the oil, and that's why the ward glows gold at night. "
        "Little Jinto's run out. The Glimmerwing Moths along the trunk ledge below Mossroof carry it on their wings, "
        "so bring some back for him.",
        "That'll keep the ward gold for a month.\n\nJinto says if a lantern goes out, the loa can't find its way "
        "home. I told him that myself, when he was small. I'm not sure I believed it then, but I do now."))
    A(Q("gsq_a_bat_in_the_webs", "A Bat in the Webs", RUZKAH, 45, 46, "Batwing",
        "One of Bat Handler Ruzkah's bats flew down into the Silkwood in a storm and hasn't come back. She can hear "
        "it from the Roost at night, caught somewhere in the webs.",
        [k("Silkwood Weaver", 7)],
        "One of my bats went down into the Silkwood in last week's storm, and I can hear it calling at night from "
        "the webs. The Silkwood Weavers will have it wrapped by now if they haven't eaten it. Clear them out of the "
        "Silkwood and I'll go down and cut it loose.",
        "I found her this morning, wrapped up tight and furious about it. She bit me, which means she's fine.\n\n"
        "Bats don't forget. She'll fly you anywhere you like, and she'll fly faster for you than she does for me."))
    A(Q("gsq_offerings_for_the_loa", "Offerings for the Loa", VASHI, 45, 46, "Loa-Speaker's",
        "Loa-Speaker Vashi lays Goldthorn at the feet of the loa every new moon, because it's the herb the trolls "
        "carried up the tree on the first climb.",
        [gather("herb_goldthorn", 6, "Gather Goldthorn on the boughs")],
        "The first trolls who climbed this tree carried Goldthorn up with them, and we lay it at the loa's feet "
        "every new moon to remember them. It grows out on the boughs below. Bring me what you can pick.",
        "The loa will be pleased. The tree's been restless this month, and an offering never hurts.\n\nSince the "
        "world broke, the loa have been quiet everywhere but here. This one still answers, and we mean to keep it "
        "answering."))
    A(Q("gsq_soil_for_the_terrace", "Soil for the Terrace", ULANI, 45, 46, "Gardener's",
        "Gardener Ula'ni grows the ward's food on the garden terrace, and the soil wears thin. Bloodroot from the "
        "boughs, worked into the beds, brings it back.",
        [gather("wood_bloodroot_stump", 5, "Gather Bloodroot Wood on the boughs")],
        "Every basket of soil on this terrace came up the lift, and it wears thin in a season. Bloodroot wood from "
        "the boughs, chipped and worked in, brings it back. Bring me some and the ward'll eat well this winter.",
        "That's good wood. I'll have it chipped and in the beds by tomorrow.\n\nOne of the newcomers in the market "
        "told me they used to do this with coffee grounds, wherever she's from. I tried it. The trolls drank the "
        "coffee instead."))

    # =================================================================================== 5. TWO TRANSPLANTS
    A(Q("gsq_a_taste_of_home", "A Taste of Home", KOFI, 45, 46, "Market",
        "Kofi Mensah ran a market stall in Accra before the merge, and he wants to cook something that tastes like "
        "home for the Settlement's market day. The closest thing up here is the river fish below.",
        [gather("fish_redgill", 6, "Catch Redgill in the Great Bough's river")],
        "Back home I'd grill tilapia with pepper and onions every market day, and the whole street would come. The "
        "Redgill in the river on the Great Bough below Mossroof is close enough. Catch me some and I'll show these "
        "trolls what a market day smells like.",
        "That's exactly what I needed, and I've got the peppers from Provisioner Juno'ka and onions from the terrace.\n\nIt won't be the "
        "same. Nothing is, three years on. But when the smoke goes up and people start to queue, it feels close "
        "enough for an afternoon."))
    A(Q("gsq_a_leaf_for_tea", "A Leaf for Tea", HANA, 45, 46, "Tea-Master's",
        "Hana Sato's family kept a tea house in Kyoto for four generations. She's run out of the leaf she's been "
        "brewing up here, and she thinks Khadgar's Whisker might do instead.",
        [gather("herb_khadgar", 6, "Gather Khadgar's Whisker on the boughs")],
        "I've been brewing a leaf the trolls grow in the gardens, and it's gone. Khadgar's Whisker might take its "
        "place, it's bitter in the right way. It grows out on the boughs below. Bring me some and I'll try a pot.",
        "Oh, that's close. It's not sencha, but it's close.\n\nMy grandmother said a tea house is wherever you pour "
        "the tea properly. I didn't understand that until I was pouring it in a tree for trolls."))

    # =================================================================================== 6. ON UP
    A(Q("gsq_up_the_high_lift", "Up the High Lift", TAGU, 45, 45, "Highlift",
        "Liftwarden Tagu works the bottom of the High Lift. The shadow hunters at Heartwatch, up in the Middle Boughs, "
        "have asked the city for anyone who can fight, and Zan'kaji's been telling people about you.",
        [deliver("gs_q_tagus_token", "Ride the High Lift and give Tagu's token to Shadow Hunter Vokra at Heartwatch")],
        "Shadow Hunter Vokra's asked the city for fighters, and after the Bloodscalp business your name's the one "
        "everybody says. Take my token up the High Lift so Dezza at the top knows I sent you, and find Vokra at "
        "Heartwatch. Nobody's asked us for fighters since the merge.",
        "Tagu's token, and the High Chieftain's word before it. We've needed somebody like you for a month.\n\n"
        "Welcome to Heartwatch. The air's thin, the bark's sick, and there's a door behind me we don't open. Let me "
        "tell you why.",
        turn_in_npc_id=VOKRA, requires_quests=["gsq_the_war_below"],
        grant_items=carry("gs_q_tagus_token", "Tagu's Lift Token", "A disc of carved heartwood with the High Lift's "
                          "mark on it, for whoever works the top.")))
    return out
