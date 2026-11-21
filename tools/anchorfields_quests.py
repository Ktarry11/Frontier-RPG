"""
The Anchorfields' quests (51-54): the engine country, where three anchors have held a shelf of stone up for a thousand
years and the third is slipping. Read by tools/build_anchorfields_quests.py, which holds them to every rule before
anything is written. The brief is docs/worldtree_brief.md; the maps are tools/handbuilt_worldtree_anchorfields.py and
tools/handbuilt_keel.py. You arrive from the Celestial Expanse with the council's second letter (ceq_word_to_the_wardens):
Aurelion's outer rings can't take visitors while the Third Anchor slips.

ANCIENT, NOT NEW (Kyle, 20 Nov 2026: "aurelion is ancient, we are new. we are learning lore not having it being new to
the world"). The wardens have kept the anchors for a thousand years, the House of Measures has written down the shelf's
lean every night for as long, the island that fell is centuries gone, and the failing is a long decline that's got
faster. The player is the newcomer, learning it.

THE THREADS:
  The wardens of Keelstone: Warden-Prime Aldric Sorne wants all three anchors walked and the Third saved. The
    chainwright keeps the First's named links; the engineer reads the Third and goes after what's coming up out of its
    cracks; the scout watches the Ascendancy at the Second, which they seized and can't keep; the old warden carries the
    story of the island that fell, word for word, and wants the lost wardens in the Keel laid to rest.
  The House of Measures: a thousand years of nightly measurements in a ledger that suddenly isn't big enough, lights
    that move against the stars, and the house's oldest records in a hand nobody can read. That record is the zone's
    piece of the sky's one mystery (docs/worldtree_brief.md): the oldest pages are in three scripts at once.
  Tiltside: the Earthborn camped on the Listing Isle, measuring a tilt the Aetherians stopped measuring.
  Out on the shards: House Vaelith's steward and heir on the estate, the engine-tender in the Gearwork, the warden
    posted at the Third Anchor, and an Earthborn scavenger picking over the island that fell.
  The Keel: the Third Anchor's root, the wardens who went down to tend it, and the thing grown out of its crack.

THE RULES IT KEEPS: no map changes with quests; transplants are factionless; the Aetherians only ever say they don't know
what the change was, and nothing about the three peoples points at it. VOICE (Kyle): whole sentences the way a person
says them, contractions, no dashes, no sentence of one or two words, the useful thing first, every kill target named,
no count beside an objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

AF = "anchorfields"
KL = "keel"             # the cave (tools/handbuilt_keel.py)

# ---- Keelstone
PRIME, CHAIN, ENGINEER, SCOUT, OLDW, SKIFF = ("af_warden_prime", "af_chainwright", "af_keel_engineer",
                                             "af_warden_scout", "af_old_warden", "af_skiffmaster")
# ---- the Observatory
MEASURER, STARS, ARCHIVIST = "af_measurer", "af_star_reader", "af_obs_archivist"
# ---- Tiltside
MARGIT, BARTOSZ, NGOZI = "af_tilt_lead", "af_tilt_surveyor", "af_tilt_medic"
# ---- out on the shards
STEWARD, HEIR, TENDER, SIRAN, WADE = ("af_steward", "af_house_heir", "af_gear_tender", "af_slip_watcher",
                                      "af_drop_scavenger")

HUB_GIVERS = {PRIME, CHAIN, ENGINEER, SCOUT, OLDW, SKIFF, MEASURER, STARS, ARCHIVIST, MARGIT, BARTOSZ, NGOZI}
#: the Aetherians pay the Aetherians; the Earthborn (Margit, Bartosz, Ngozi, Wade) pay nobody
SKY_GIVERS = {PRIME, CHAIN, ENGINEER, SCOUT, OLDW, SKIFF, MEASURER, STARS, ARCHIVIST, STEWARD, HEIR, TENDER, SIRAN}


def k(target, n, zone=AF):
    return kill(target, n, zone=zone)


def boss(target, zone=AF):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=AF, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def gather(material, n, label):
    return dict(type="gather", target=material, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Anchorlight Wisp": [("af_q_anchorlight_mote", "Mote of Anchorlight", "A bead of gold light left where an "
                          "Anchorlight Wisp came apart. It's warm, and it pulls very slightly toward the First Anchor.")],
    "Ascendancy Engineer": [("af_q_drift_log", "Second Anchor Drift Log", "An Ascendancy Engineer's slate, scratched "
                             "with readings of the Second Anchor. Every line is a little worse than the one before.")],
    "Overflow Elemental": [("af_q_star_glass", "Clear Overflow Glass", "A lens of clear crystal that set inside an "
                            "Overflow Elemental when it came apart. Light goes through it without bending at all.")],
    "Wreck-Rubble Elemental": [("af_q_archive_plate", "Fallen Archive Plate", "A thin plate of stone from the island "
                                "that fell, cut close with writing, pried out of a Wreck-Rubble Elemental's back.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [61]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=AF, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
FIRST_FOOT = (190, 62)        # the foot of the First Anchor
SEIZED = (222, 128)           # the Ascendancy's camp round the Second Anchor
SLIPPING = (176, 192)         # the foot of the Third Anchor
DROPFIELD = (30, 222)         # out on the Dropfield, where the island fell
ESTATE_EDGE = (38, 44)        # the Estates' far edge, the house's old survey mark
LISTING_TIP = (286, 192)      # the Listing Isle's low tip
LISTING_HEAD = (280, 132)     # the Listing Isle's high end


def build():
    out = []
    A = out.append

    # =================================================================================== 1. KEELSTONE
    A(Q("afq_walk_the_anchors", "Walk the Anchors", PRIME, 51, 51, "Anchorwalker's",
        "Warden-Prime Aldric Sorne wants the council's help to see what the wardens see. He's asked you to walk to all "
        "three anchors before he tells you anything else.",
        [explore(*FIRST_FOOT, "Stand at the foot of the First Anchor"),
         explore(*SEIZED, "Look over the Ascendancy's camp at the Second Anchor"),
         explore(*SLIPPING, "Stand at the foot of the Third Anchor")],
        "I won't tell you about the anchors. You'll understand them better if you walk to them. Go to the First, then "
        "look at the Second from as close as the Ascendancy lets you, then stand under the Third. Come back and tell me "
        "which one frightened you.",
        "The Third, then. Everyone says the Third.\n\nThe First has held for a thousand years and hums like it could "
        "hold for a thousand more. The Third has held for a thousand years too, and you can hear it now, the way you "
        "hear an old beam before it goes."))
    A(Q("afq_the_bombers_over_keelstone", "Bombers Over Keelstone", PRIME, 52, 53, "Keelguard's",
        "The Ascendancy flies bomber constructs from the Second Anchor over Keelstone, to remind the wardens who holds "
        "it. The Warden-Prime wants every Ascendancy Bomber Construct that can still fly brought down.",
        [k("Ascendancy Bomber Construct", 6)],
        "Every Ascendancy Bomber Construct they launch from the Second Anchor flies right over my hold and drops its "
        "load on the chain-field. They say it's an exercise. Bring them down where they're parked, and we'll see how "
        "much they like exercising on foot.",
        "No bombers over Keelstone this morning, and the chainwright's stopped flinching.\n\nThe Ascendancy will send "
        "word that I'm provoking them. I've been provoked for six years, so I'll survive it."))
    A(Q("afq_anchor_marshal_corvan_sael", "Anchor-Marshal Corvan Sael", PRIME, 54, 54, "Marshal's Bane",
        "Anchor-Marshal Corvan Sael commands the Ascendancy at the Second Anchor. He took it from the wardens six years "
        "ago, and the Warden-Prime has the drift logs to prove he's letting it go.",
        [boss("Anchor-Marshal Corvan Sael")],
        "Anchor-Marshal Corvan Sael took the Second Anchor and told the council the wardens were too old and too slow "
        "to keep it. His own engineers' logs say it's drifted further in six years than in the six centuries before. "
        "I'm done writing letters about him. Go and take it back.",
        "Sael's gone, and his soldiers are packing their tents.\n\nWe'll have wardens on the Second Anchor by nightfall. "
        "It'll take years to undo his six, but at least now the hands on it know what they're holding.",
        requires_quests=["afq_their_own_logs"]))
    A(Q("afq_the_keel_heart", "The Keel-Heart", PRIME, 54, 54, "Keelsaver's",
        "The Third Anchor is slipping because its keel is cracking, and something has grown out of the crack. The "
        "Warden-Prime wants it torn out before the keel splits in two.",
        [boss("The Keel-Heart", zone=KL)],
        "The engineer's found it. The keel's cracked, and something's grown out of the crack, feeding on the keel's own "
        "light. We call it the Keel-Heart because nobody's got a better word. Go down into the Keel and tear it out, "
        "before it eats the thing that's holding the shelf up.",
        "The Third Anchor's stopped slipping. The engineer's been sitting by it all night, just listening.\n\nIt "
        "isn't mended, and it may never be. But it's holding, and I can write to the council and tell them the outer "
        "rings are safe. Aurelion will open the bridge for you. You've earned it twice over.",
        requires_quests=["afq_the_unmoored", "afq_down_to_the_keel"]))
    A(Q("afq_links_with_names", "Links With Names", CHAIN, 51, 52, "Chainwright's",
        "Every link in the First Anchor's chains has a name and a wright who forged it. The Chain-Wind Elemental that "
        "scours the chain-field wears the names off.",
        [k("Chain-Wind Elemental", 8)],
        "The wind's always blown across the chain-field, but a Chain-Wind Elemental is the wind with a grudge. They "
        "scour the links until the names cut into them are gone, and a link without a name is a link nobody's checked. "
        "Clear them off my chains.",
        "I walked the chains this morning and read every name I could.\n\nHalvi, Orren, Ysmay the Elder. Some of those "
        "wrights died nine hundred years ago, and their links are still holding the shelf up. I'd like mine to do the "
        "same."))
    A(Q("afq_anchorlight", "Anchorlight", CHAIN, 52, 52, "Linkforger's",
        "The chainwright tempers new links in anchorlight, the gold light the First Anchor gives off. The Anchorlight "
        "Wisp is made of it, and the wardens have always taken their light from the wisps.",
        [fetch("af_q_anchorlight_mote", 6)],
        "Every Anchorlight Wisp in the chain-field is a little of the First Anchor's light that's wandered off. The "
        "wardens have always tempered new links in it, and the Third Anchor needs new links badly. Bring me the motes, "
        "and I'll forge what I can.",
        "That's enough light for six links, maybe seven if I'm careful.\n\nThe Third needs forty. I'll start with these, "
        "because the oldest rule of the chain-field is that you never wait for enough.",
        nxt="afq_starfall"))
    A(Q("afq_starfall", "Starfall, the Burning Shard", CHAIN, 53, 53, "Starfall's Bane",
        "A shard of something burning fell into the First Anchor's chain-field a month ago and didn't go out. The "
        "wardens call it Starfall, the Burning Shard, and it's been melting links.",
        [boss("Starfall, the Burning Shard")],
        "Starfall, the Burning Shard came down out of the sky into my chain-field, and it's been drifting along the "
        "chains ever since, melting every link it touches. I've lost four this month. Put it out before it reaches "
        "the anchor.",
        "It's out, and it's just a lump of black glass now.\n\nThe House of Measures says things have been falling out "
        "of the sky more often since the change. I don't know what's up there, and I don't think they do either.",
        requires_quests=["afq_anchorlight"]))
    A(Q("afq_reading_the_third", "Reading the Third", ENGINEER, 52, 53, "Keelreader's",
        "Engineer Pell Oravane reads the anchors the way a healer reads a pulse. He wants the Slipstone Elemental round "
        "the Third Anchor cleared so he can hear it properly.",
        [k("Slipstone Elemental", 7)],
        "The Third Anchor's stone has started coming loose, and every Slipstone Elemental round its foot is a piece of "
        "the shelf that's woken up and walked off. They grind so loud I can't hear the anchor. Break them up, and I'll "
        "listen.",
        "Now I can hear it, and I wish I couldn't.\n\nThere's a crack in the keel, the crystal it's grown round. I can "
        "hear it widening, slowly, like ice on a pond in spring.",
        nxt="afq_out_of_the_crack"))
    A(Q("afq_out_of_the_crack", "Out of the Crack", ENGINEER, 53, 54, "Crackwarden's",
        "Things are coming up out of the cracks round the Third Anchor: the Keelcrack Crawler and the Void-Touched Wisp. "
        "Pell thinks they're coming from the keel itself.",
        [k("Keelcrack Crawler", 7), k("Void-Touched Wisp", 5)],
        "Every Keelcrack Crawler and Void-Touched Wisp round the Third Anchor came up out of the cracks in the last few "
        "years. Before that, the old wardens' logs don't mention them once in a thousand years. Drive them back down, "
        "and I'll find out where they're coming from.",
        "They're coming up from the keel. I'm sure of it now.\n\nAnd there's something bigger down there with them, "
        "something that lifts the stone round it like it weighs nothing.",
        requires_quests=["afq_reading_the_third"], nxt="afq_the_unmoored"))
    A(Q("afq_the_unmoored", "The Unmoored", ENGINEER, 54, 54, "Unmoored's Bane",
        "Something round the Third Anchor makes the stone near it lose its weight. Pell calls it the Unmoored, and every "
        "time it passes, the anchor slips a little further.",
        [boss("The Unmoored")],
        "The Unmoored drifts round the Third Anchor, and wherever it goes, the stone forgets how heavy it is. That's "
        "the one thing an anchor can't stand. Find it and end it.",
        "The stone's heavy again. I've never been so glad to drop a hammer on my foot.\n\nThe anchor's still slipping, "
        "but slower. Whatever's wrong now is down in the keel, and the Warden-Prime will want to talk to you about "
        "going down there.",
        requires_quests=["afq_out_of_the_crack"]))
    A(Q("afq_count_their_wardens", "Count Their Wardens", SCOUT, 52, 52, "Seized Anchor",
        "Scout Varen Ashby has watched the Ascendancy at the Second Anchor from the bridge for six years. He wants "
        "someone to get into their camp and count what's there.",
        [explore(*SEIZED, "Get into the Ascendancy's camp at the Second Anchor and count what's there")],
        "I've counted their tents from the bridge so often I could draw them asleep. From the bridge I can't "
        "see what they're doing to the anchor. Get into their camp and look at it, and don't stop to fight anything that "
        "doesn't stop you first.",
        "Two guns and a shield pylon round an anchor they don't know how to read.\n\nThey've got the chains tied off "
        "wrong. Any warden apprentice could tell them, and none of them would ask an apprentice.",
        nxt="afq_hold_the_line"))
    A(Q("afq_hold_the_line", "Hold the Line", SCOUT, 53, 54, "Lineholder's",
        "The Ascendancy Warden and the Ascendancy Crystal-Weaver hold the Second Anchor's camp. Varen wants them thinned "
        "before the wardens try to take it back.",
        [k("Ascendancy Warden", 7), k("Ascendancy Crystal-Weaver", 5)],
        "Every Ascendancy Warden in that camp calls himself a warden, and not one of them's ever checked a chain. The "
        "Ascendancy Crystal-Weaver keeps the shield pylon up. Thin them both, and the real wardens can walk back in.",
        "They've pulled back behind the pylon, and the camp's half empty.\n\nThe engineers are still there, though, "
        "writing down the anchor's drift like they're proud of it.",
        requires_quests=["afq_count_their_wardens"]))
    A(Q("afq_their_own_logs", "Their Own Logs", SCOUT, 53, 54, "Logtaker's",
        "The Ascendancy Engineer at the Second Anchor keeps a log of its drift. Varen wants those logs, because they're "
        "the proof the council will listen to.",
        [fetch("af_q_drift_log", 5)],
        "The council won't believe a warden who says the Ascendancy's losing the anchor. They might believe the "
        "Ascendancy's own engineers. Every Ascendancy Engineer there carries a drift log. Bring me those logs.",
        "Six years of drift, in their own hand, every line a little worse.\n\nI'll copy these for the council tonight. "
        "The Warden-Prime will want the anchor-marshal next, and now he can say why."))
    A(Q("afq_word_for_word", "Word for Word", OLDW, 51, 52, "Rememberer's",
        "Old Warden Ebbe Tharn carries the story of the island that fell the way it came down to him, word for word. "
        "He wants you to stand where it fell before he tells it.",
        [explore(*DROPFIELD, "Stand on the Dropfield, where the island fell")],
        "My grandfather's grandfather saw an island fall, and the story's come down to me word for word. I won't tell "
        "it to someone who hasn't stood there. Go out onto the Dropfield and look at what's left, then come back.",
        "Then I'll tell it to you the way it was told to me.\n\nThe anchor that held it was the Fourth. Its keel cracked, "
        "and the wardens went down to mend it, and they didn't come up, and three days later the island went. That's "
        "why there are three anchors now, and why the Third frightens us all.",
        nxt="afq_down_to_the_keel"))
    A(Q("afq_down_to_the_keel", "Down to the Keel", OLDW, 53, 54, "Keelwalker's",
        "The wardens who went down into the Third Anchor's keel a generation ago never came back up. The Keel is full of "
        "Ballast Golem and Hollowed Warden, and Ebbe wants the way down cleared.",
        [k("Ballast Golem", 5, zone=KL), k("Hollowed Warden", 5, zone=KL)],
        "When the Third began to slip, a company of wardens went down into the Keel to tend it, and they're still down "
        "there. They're something else now, and we call each one a Hollowed Warden. The Ballast Golem that walks the "
        "halls was set there to keep the shelf level. Clear the way down so the rest of us can follow.",
        "I knew some of them. I knew their names.\n\nTheir captain was Oris Hale, and if he's down there, he's still "
        "holding his post. That would be like him.",
        requires_quests=["afq_word_for_word"], nxt="afq_warden_captain_oris_hale"))
    A(Q("afq_warden_captain_oris_hale", "Warden-Captain Oris Hale", OLDW, 54, 54, "Last Post",
        "Warden-Captain Oris Hale led the company that went down into the Keel. Ebbe believes he's still holding the "
        "wardens' last post, and that he won't leave it until someone relieves him.",
        [boss("Warden-Captain Oris Hale", zone=KL)],
        "Warden-Captain Oris Hale never left a post in his life without being relieved. If he's down there, he's still "
        "holding it, and he'll fight anyone who comes near, because nobody ever came to relieve him. Go and relieve him. "
        "You'll have to do it with a blade.",
        "He's at rest, then. The post's empty for the first time in thirty years.\n\nI'll cut his name on the First "
        "Anchor's links, next to the wrights. He held a post a thousand years old, and that's what wardens do.",
        requires_quests=["afq_down_to_the_keel"]))
    A(Q("afq_carrion_over_the_skiffs", "Carrion Over the Skiffs", SKIFF, 52, 53, "Skyroute",
        "The Carrion Gale Hawk nests on the Dropfield and hunts the skiff routes out of Keelstone. Skiffmaster Jorun "
        "Kell has lost two lines to them this month.",
        [k("Carrion Gale Hawk", 7)],
        "Every Carrion Gale Hawk on the Dropfield thinks my skiffs are big slow birds worth chasing. They're tearing the sail "
        "lines and fouling the crystal hoods. Thin them out where they nest, out on the fallen island.",
        "The routes are clear, and the skiffs are flying on time, which is a first this season.\n\nYou'll always get a "
        "seat on one of mine. That's not a favour, it's a debt."))

    # =================================================================================== 2. THE OBSERVATORY
    A(Q("afq_a_bigger_ledger", "A Bigger Ledger", MEASURER, 51, 52, "Measurer's",
        "The House of Measures has written down the shelf's lean every night for a thousand years. Master Ivo Kestrel "
        "wants this year's figures taken to the Warden-Prime by hand.",
        [deliver("af_q_lean_figures", "Take the house's figures to Warden-Prime Aldric Sorne at Keelstone")],
        "For nine hundred years the number in our ledger barely moved. For the last forty it's moved every year, and "
        "since the change it's moved more than the forty before. Take these figures to the Warden-Prime, and put them in his "
        "hand yourself. He'll read them twice.",
        "The house sends me its figures every year, and every year I read them twice.\n\nThis year I'll read them "
        "three times. Thank the master for me, and tell him I'm grateful and I hate it.",
        turn_in_npc_id=PRIME,
        grant_items=carry("af_q_lean_figures", "The Year's Lean Figures", "A folded sheet of the House of Measures' "
                          "nightly figures for the year, each in the same careful hand, the last column circled.")))
    A(Q("afq_measure_the_lean", "Measure the Lean", MEASURER, 52, 53, "Plumbline",
        "The house's oldest survey marks are cut into the shelf at its far edges. Master Kestrel wants both read against "
        "the Observatory, the way the house has read them for a thousand years.",
        [explore(*ESTATE_EDGE, "Read the house's old survey mark at the Estates' far edge"),
         explore(*LISTING_TIP, "Read the survey mark at the Listing Isle's low tip")],
        "Our oldest marks are cut into the shelf at its edges, one past the Estates and one on the Listing Isle. The "
        "house has read them every year since before my great-grandmother was born. I'm too old for the walk, so go "
        "and read them for me, and I'll compare.",
        "The Estates' mark is where the ledger says. The Listing Isle's is six spans lower than it was ten years ago.\n\n"
        "That's not a lean any more. That's a fall happening very slowly."))
    A(Q("afq_lights_that_move", "Lights That Move", STARS, 52, 52, "Stargazer's",
        "Star-Reader Caelan Duir measures the islands' drift against the stars. The Lantern Puffball drifts across the "
        "shards at night and spoils every reading.",
        [k("Lantern Puffball", 8)],
        "The stars don't move, so when an island moves against them, I see it. Every Lantern Puffball on the shards "
        "glows just like a star and drifts just like an island, and it ruins my count. Pop them, please, so I can see "
        "what's actually moving.",
        "Clear skies tonight, and nothing glowing that shouldn't.\n\nThe Listing Isle moved against the stars again. "
        "I'd hoped the puffballs had been fooling me about that one.",
        nxt="afq_clear_glass"))
    A(Q("afq_clear_glass", "Clear Glass", STARS, 52, 53, "Lensgrinder's",
        "The Observatory's great lens has clouded with age. Caelan wants the clear glass that sets inside the Overflow "
        "Elemental in the Gearwork to grind a new one.",
        [fetch("af_q_star_glass", 5)],
        "Our great lens was ground before the house had its name, and it's gone cloudy. Every Overflow Elemental in the "
        "Gearwork sets into clear glass when it comes apart, the clearest there is. Bring me enough, and I'll grind a "
        "lens to see the drift properly.",
        "This is beautiful glass. The light goes straight through it.\n\nIt'll take me a month to grind. When it's "
        "done, the house will see the shelf move more clearly than anyone has in a thousand years. I'm not sure I'm "
        "glad about that.",
        requires_quests=["afq_lights_that_move"]))
    A(Q("afq_three_hands", "Three Hands", ARCHIVIST, 52, 53, "Archivist's",
        "The House of Measures' oldest records were copied from stone plates nobody can read. Archivist Bram Iselworth "
        "thinks the island that fell carried more of them, and the Wreck-Rubble Elemental on the Dropfield is made of "
        "its stone.",
        [fetch("af_q_archive_plate", 4)],
        "Our oldest pages are copies of stone plates in a hand nobody in the house can read, and we've copied them "
        "faithfully for a thousand years anyway. The island that fell carried a library. Every Wreck-Rubble Elemental "
        "on the Dropfield is made of its stone, and some of them carry plates. Bring me what you find.",
        "Look at this one. It isn't one hand at all, it's three, side by side, saying the same thing.\n\nThis column is "
        "old Aetherian, and I can almost read it. This one is cut in runes like the ones on the Kharad ruins in the "
        "Expanse. And this one's notation, like music, the way the Veyr write their songs. Three peoples wrote the "
        "first measure of this shelf together. My house has no story where that ever happened.",
        nxt="afq_the_first_measure"))
    A(Q("afq_the_first_measure", "The First Measure", ARCHIVIST, 53, 53, "Firstmeasure",
        "Archivist Iselworth has made a rubbing of the three-handed plate. He wants Old Warden Ebbe Tharn to see it, "
        "because the wardens remember things the house never wrote down.",
        [deliver("af_q_plate_rubbing", "Take the archivist's rubbing to Old Warden Ebbe Tharn at Keelstone")],
        "The wardens don't write their history down. They keep it by mouth, word for word, and some of it's older than our ledger. "
        "Take this rubbing to Old Warden Ebbe Tharn and ask him if anything in his stories has three hands in it.",
        "Three hands, yes, there's a line about that. It's the oldest line in the whole story, and I never knew what it meant.\n\n"
        "\"The first anchor was raised by three, and three kept it.\" I always thought it meant three wardens. I don't "
        "think it did.",
        turn_in_npc_id=OLDW, requires_quests=["afq_three_hands"],
        grant_items=carry("af_q_plate_rubbing", "Rubbing of the Three-Handed Plate", "A charcoal rubbing of a stone "
                          "plate, three columns of writing side by side, none of them in the same script.")))

    # =================================================================================== 3. TILTSIDE
    A(Q("afq_four_degrees_and_climbing", "Four Degrees and Climbing", MARGIT, 52, 53, "Tiltside",
        "The Earthborn at Tiltside drive marker stakes into the Listing Isle to track its tilt. The Tiltside Goat knocks "
        "them over faster than they can be set.",
        [k("Tiltside Goat", 7)],
        "We drive a stake every morning to see how far the island's leaned overnight, and every Tiltside Goat on the "
        "isle thinks a stake is something to butt. I kept rigs standing in the North Sea, and I never had a goat problem. "
        "Clear them off the stakes.",
        "The stakes are standing, and the reading's clean for once.\n\nFour degrees and a quarter. It was four even last "
        "week. Nobody in Keelstone will come over here and look at it.",
        nxt="afq_old_hornback"))
    A(Q("afq_old_hornback", "Old Hornback", MARGIT, 53, 53, "Hornbreaker's",
        "The biggest goat on the Listing Isle is Old Hornback, and he's been charging the camp. Margit has two people "
        "with bruised ribs and one with a broken stake through her tent.",
        [boss("Old Hornback")],
        "Old Hornback isn't like the others. He charges anything that stands on his island, and he's decided the whole "
        "camp's standing on it. Two of my people have cracked ribs. Make him stop.",
        "He's down, and I'm a little sorry. My aunt kept goats back home in Norway, and none of them had his nerve.\n\nWe'll keep the "
        "stakes, though. Somebody has to keep measuring this.",
        requires_quests=["afq_four_degrees_and_climbing"]))
    A(Q("afq_stakes_in_the_ground", "Stakes in the Ground", BARTOSZ, 52, 53, "Surveyor's",
        "Bartosz Wierzbicki measures the Listing Isle's tilt from both ends. He wants his marks at the high end and the "
        "low tip read the same morning.",
        [explore(*LISTING_HEAD, "Read Bartosz's mark at the Listing Isle's high end"),
         explore(*LISTING_TIP, "Read Bartosz's mark at the Listing Isle's low tip")],
        "I measured land in Krakow for twenty years, and you always take both ends the same morning. The isle's high end "
        "is up by the leaning tower, and the low tip's at the south. Read my marks at both, and I'll do the sum.",
        "Four degrees, eighteen minutes. It's a quarter of a degree a month.\n\nAt that rate the low tip goes under the "
        "cloud in six years. I'll write it down for the house, and they'll write it in their ledger, and then we'll "
        "both know.",
        nxt="afq_pins_for_the_marks"))
    A(Q("afq_pins_for_the_marks", "Pins for the Marks", BARTOSZ, 53, 53, "Pinsetter's",
        "Bartosz wants proper survey pins in the Listing Isle instead of wooden stakes. Truesilver doesn't rust or "
        "shift, and it's in the shelf's stone.",
        [gather("ore_truesilver", 5, "Mine Truesilver from the shelf")],
        "Wooden stakes move, and goats eat them, and I'm tired of both. Back home in Krakow I'd have had steel pins. Truesilver doesn't rust and doesn't shift, and "
        "there's some in the shelf's stone. Mine me enough, and I'll set pins that'll still be there when my "
        "grandchildren measure this.",
        "That's proper survey metal. I'll have pins in by tonight.\n\nThe Aetherians made their anchors to last a "
        "thousand years. My pins only need to last until somebody believes me.",
        requires_quests=["afq_stakes_in_the_ground"]))
    A(Q("afq_dust_in_the_lungs", "Dust in the Lungs", NGOZI, 52, 53, "Medic's",
        "Dr. Ngozi Eze has half the camp coughing. The Cliffside Moth sheds a dust over the Listing Isle that settles in "
        "people's lungs.",
        [k("Cliffside Moth", 7)],
        "Every Cliffside Moth on the isle sheds a fine dust when it flies, and it settles in everybody's chest. Half the "
        "camp's coughing, and I've run out of things that help. Back home in Ibadan I'd have a pharmacy down the road. Clear them off the isle, and I'll do the rest.",
        "Nobody coughed in the night for the first time in weeks.\n\nThat's the best medicine I've had to give since I "
        "got here, and you made it."))
    A(Q("afq_sprains_and_salves", "Sprains and Salves", NGOZI, 52, 53, "Salvemaker's",
        "Everyone at Tiltside walks on a slope, and Ngozi has more sprained ankles than she can bind. Khadgar's Whisker "
        "grows on the shards, and she's learned to make a salve from it.",
        [gather("herb_khadgar", 6, "Gather Khadgar's Whisker on the shards")],
        "An Aetherian herbalist showed me how to make a salve from Khadgar's Whisker, and it works better than anything "
        "I had in Ibadan. Everyone here walks on a slope, so everyone here sprains something. Gather me some, and I'll "
        "make enough for the camp.",
        "That's a month of salve, maybe two if people watch their feet.\n\nThey won't, but I'll tell them to anyway. "
        "That's half of being a doctor."))

    # =================================================================================== 4. OUT ON THE SHARDS
    A(Q("afq_the_clocks_still_need_winding", "The Clocks Still Need Winding", STEWARD, 51, 52, "Steward's",
        "Steward Olin Varrow keeps House Vaelith's estate for a family that left for Aurelion. The house's Estate "
        "Sentinel no longer knows him, and it won't let him into his own clock tower.",
        [k("Estate Sentinel", 7)],
        "The house's sentinels have guarded this estate for six hundred years, and they've always known me. Since the "
        "shelf began to lean, every Estate Sentinel has forgotten who belongs here. They won't let me wind the clocks, "
        "and a house this old doesn't like its clocks stopped.",
        "The clocks are wound, and the house sounds like itself again.\n\nThe family won't come back. I know that. But "
        "somebody should keep the house the way they left it, in case they're wrong."))
    A(Q("afq_the_garden_gone_wild", "The Garden Gone Wild", STEWARD, 51, 52, "Groundskeeper's",
        "The estate's garden drones were built to tend the lawns, and the Orchard Fowl were brought in to eat the "
        "grubs. Now the Garden Repair-Drone prunes anything that moves, and the fowl have eaten the orchard bare.",
        [k("Garden Repair-Drone", 6), k("Orchard Fowl", 5)],
        "Every Garden Repair-Drone on the estate has decided that anything moving is a branch that needs cutting. The "
        "Orchard Fowl were brought in to eat the grubs, and they've eaten the fruit, the seed and half a hedge. Clear "
        "both off the lawns.",
        "The lawn's quiet, and the orchard's got a chance.\n\nThe heir will tell you the drones were built by his great "
        "grandmother's great grandmother. He's right about that, and she'd have hated what they've become."))
    A(Q("afq_the_gardener", "The Gardener", HEIR, 52, 52, "Gardener's Bane",
        "The estate's oldest construct is the Gardener, built to tend House Vaelith's grounds a thousand years ago. "
        "Corwen Vaelith says it's started tending the people on them, the way it tends weeds.",
        [boss("The Gardener")],
        "The Gardener's been tending these grounds since before my family had a name in Aurelion. It planted the "
        "orchard my grandmother's grandmother walked in. Now it's pulling up anything it doesn't recognise, and it "
        "doesn't recognise anyone any more. I can't do it myself, so please do it for me.",
        "It's still, and the grounds are mine again, for whatever that's worth on a shelf that's leaning.\n\nI'll "
        "plant something where it fell. It would have wanted something planted.",
        requires_quests=["afq_the_garden_gone_wild"]))
    A(Q("afq_sounds_i_dont_know", "Sounds I Don't Know", TENDER, 52, 53, "Enginetender's",
        "Engine-Tender Halvard Cree knows every engine in the Gearwork by its sound. The Overloaded Construct and the "
        "Scrap-Walker are making sounds he's never heard.",
        [k("Overloaded Construct", 7), k("Scrap-Walker", 5)],
        "These engines have fed the anchors since before the houses had names, and the constructs that tend them have "
        "always been quiet, but they aren't now. Every Overloaded Construct is crackling now, and every Scrap-Walker is grinding itself apart "
        "and walking anyway. Break them down before they break the engines.",
        "That's better, and I can hear the engines again under all that racket.\n\nOne of them's still wrong, though, the "
        "seventh. It's louder than all the rest put together.",
        nxt="afq_engine_seven"))
    A(Q("afq_engine_seven", "Engine Seven", TENDER, 53, 53, "Enginebreaker's",
        "The seventh engine in the Gearwork got up and walked off its mount. Halvard calls it Engine Seven, and it's "
        "tearing the other engines apart.",
        [boss("Engine Seven")],
        "Engine Seven fed the Third Anchor for nine hundred years. Last month it pulled itself off its mount and started "
        "walking, and now it's tearing into the others like it's looking for something. Stop it, before it reaches the "
        "First Anchor's feed.",
        "It's stopped, and I'll have the others back to their proper sound in a week.\n\nI looked inside it afterwards. It "
        "was full of the Third Anchor's crystal, grown right through its works. It was trying to get back to the keel.",
        requires_quests=["afq_sounds_i_dont_know"]))
    A(Q("afq_sirans_report", "Siran's Report", SIRAN, 52, 52, "Watchman's",
        "Warden Siran Holt is posted at the Third Anchor to watch it slip. He's written down what he's seen this week, "
        "and he wants it in the engineer's hands.",
        [deliver("af_q_sirans_report", "Take Siran's report to Engineer Pell Oravane at Keelstone")],
        "I write down everything the Third Anchor does, every hour, and I take it to the engineer once a week. This "
        "week I can't leave it, because it slipped twice in one night. Take my report to Pell at Keelstone for me.",
        "Twice in one night. He's right to stay.\n\nI'll go out myself tomorrow. Tell Siran he's doing exactly what a "
        "warden should, and that I'm bringing him something hot to drink.",
        turn_in_npc_id=ENGINEER,
        grant_items=carry("af_q_sirans_report", "Siran's Report", "A week of hourly notes on the Third Anchor in a "
                          "warden's cramped hand. Two lines near the end are underlined twice.")))
    A(Q("afq_the_best_wreck_ive_ever_been_on", "The Best Wreck I've Ever Been On", WADE, 52, 53, "Salvager's",
        "Wade Prentiss is picking over the island that fell, centuries after anyone else stopped. The Dropfield Stalker "
        "and the Wreck-Rubble Elemental keep driving him off it.",
        [k("Dropfield Stalker", 7), k("Wreck-Rubble Elemental", 5)],
        "I salvaged wrecks off Halifax for fifteen years, and this is the best wreck I've ever been on. Every Dropfield "
        "Stalker on it thinks I'm dinner, and every Wreck-Rubble Elemental thinks I'm stealing, which is fair. Clear "
        "them off long enough for me to work.",
        "That's the best day's salvage I've had up here. There's a whole house under that rubble, still furnished.\n\n"
        "There's something down in the middle that won't let me near, though. It's big, and it doesn't move unless you "
        "touch what it's sitting on.",
        nxt="afq_old_ballast"))
    A(Q("afq_old_ballast", "Old Ballast", WADE, 53, 53, "Ballastbreaker's",
        "In the middle of the Dropfield sits a stone guardian the size of a house, on top of the fallen island's "
        "heaviest wreck. Wade calls it Old Ballast.",
        [boss("Old Ballast")],
        "Old Ballast was a weight, once, hung under the island that fell to keep it level. When the island went, it "
        "came down with it, and it's been sitting on the wreck ever since, guarding it. I want what's under it. Back home in Halifax I'd "
        "have hired a crane, and up here I've got you.",
        "It's off, and you won't believe what was under it.\n\nIt's the anchor's chain, the Fourth Anchor's, still "
        "fastened to the island's keel. Whatever held the other end let go first. The wardens are going to want to see "
        "this.",
        requires_quests=["afq_the_best_wreck_ive_ever_been_on"]))
    return out
