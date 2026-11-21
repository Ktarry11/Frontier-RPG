"""
Dawnhaven's quests (1-9): Amberleaf Glade, Duskfall Woods, Firstlight Spire and the four caves. Read by
tools/build_dawnhaven_quests.py, which holds them to every rule before anything is written. The brief is
docs/dawnhaven_brief.md.

Kyle, 21 Nov 2026: "Even though it's early game, we still wan to make it nice, good quest, good story! A story of
survival, rebirth, and progress."

THE STORY, IN THREE ACTS
  SURVIVAL (Amberleaf Glade, 1-6). You wake on the Waking Shore with sand in your mouth and no idea where you are.
    Ranger-Captain Saelis meets you, and Amberwatch, the Sunreach Conclave's camp in the old outpost's ruined
    gatehouse, takes you in. The first days are the first days of anyone washed up somewhere: food (Thaelen's supper),
    shelter (Rosa's roofs), safety (the lynxes in the grove, the old crab on the shore) and finding out what else is
    on the island with you. Something is: the wardstones that hid Dawnhaven for a thousand years are broken and
    the wyrms are drinking what's left of them (Iriel); naga have landed in Brinecoil Cove and their orders say
    they're scouting the island for something (Kaelen); and the outpost's own dead don't rest (Aldaria). You set
    one wardstone burning again. You make the naga's tidecaller answer for her scouts, and you put the warden of the
    dead to rest. Then Saelis sends you north.
  REBIRTH (Duskfall Woods, 5-9). Dawnrest is a waystation with its roof back on, and Lightwarden Selanne wants the
    whole outpost back: the Lightwell in its heart fed everything once, and it's dark. The woods round it have gone
    feral (Lyra's hunt), the outpost's spilled magic has woken in the thicket (Aeron), the naga have their main camp
    on the north-west shore and a sea-witch under it drawing on that same spilled magic (Nerys, Aeron), and in the
    Withered Spires the outpost's last commander still keeps his post with what's left of his garrison (Halion).
    The well went dark because something under it was starving, and the outpost's last magister has been feeding it
    the outpost's dead to keep it quiet. You end the magister, you end the hunger, and the Lightwell burns again.
    The dead can rest; Halion goes with them.
  PROGRESS (Firstlight Spire, 9). With the well lit, the spire the founders raised lights too, for the first time in
    a thousand years. The Spire opens its doors: a room for everyone who woke on the shore, and Joost's boat makes
    the first crossing to Durotar, with the Conclave's letter to Orgrimmar and you aboard.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word. ASCII only.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401
from tools.moonglade_quests import CYCLE

AL = "amberleaf_glade"
DF = "duskfall_woods"
FS = "firstlight_spire"
GROTTO = "brinecoil_grotto"
VAULT = "the_quiet_vault"
HOLLOW = "saltspine_hollow"
DEEP = "the_lightwell_deep"

# ---- Amberleaf Glade
SAELIS, IRIEL, THAELEN, ROSA, KAELEN, ALDARIA = "dh_saelis", "dh_iriel", "dh_thaelen", "dh_rosa", "dh_kaelen", "dh_aldaria"
# ---- Duskfall Woods
SELANNE, AERON, LYRA, HALION, NERYS = "dh_selanne", "dh_aeron", "dh_lyra", "dh_halion", "dh_scout_nerys"
# ---- Firstlight Spire, and the far end of the crossing
LORIEN, JOOST, INNKEEPER, DOCKHAND = "dh_lorien", "dh_joost", "dh_innkeeper", "dh_durotar_dockhand"

HUB_GIVERS = {SAELIS, IRIEL, THAELEN, ROSA, KAELEN, ALDARIA, SELANNE, AERON, LYRA, LORIEN, JOOST}
CONCLAVE_GIVERS = {SAELIS, IRIEL, THAELEN, KAELEN, ALDARIA, SELANNE, AERON, LYRA, HALION, NERYS, LORIEN}


def k(target, n, zone=AL):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone=AL, radius=4):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Sunmane Boar": [("dh_q_boar_haunch", "Sunmane Boar Haunch", "A thick haunch of boar, marbled and gold-bristled. "
                      "It'll feed a fire's worth of people.")],
    "Amberleaf Lynx": [("dh_q_lynx_pelt", "Soft Lynx Pelt", "A lynx pelt, tawny and gold, thick enough to keep out "
                        "the rain if it's laid right.")],
    "Amberwood Wanderer": [("dh_q_leaf_heart", "Leaf-Heart", "A knot of gold leaves wound tight round a warm core. "
                            "It still rustles when you hold it.")],
    "Brinecoil Siren": [("dh_q_brinecoil_orders", "Brinecoil Orders", "A shell tablet scratched with naga script, "
                         "sealed with wax that smells of the sea.", 0.5)],
    "Restless Sentinel": [("dh_q_sentinel_badge", "Tarnished Sentinel Badge", "A silver badge gone black with age, a "
                           "name cut into the back of it.")],
    "Leafweaver Spider": [("dh_q_leafweaver_silk", "Leafweaver Silk", "A hank of fine silk, gold-red like the leaves "
                           "the spiders weave it into.")],
    "Wildmana Elemental": [("dh_q_spilled_shard", "Shard of Spilled Light", "A sliver of hardened magic, humming and "
                            "faintly warm, like a coal that won't go out.")],
    "Withered Magister": [("dh_q_spirit_lantern", "Spirit Lantern", "A small glass lantern with a pale flame in it "
                           "that gives no heat. The outpost's dead carried them on their rounds.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

_cyc = [5]


def R():
    """The next reward triple off the shared cycle (tools/moonglade_quests.CYCLE)."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=AL, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ------------------------------------------------------------------------------ places (walkable, checked)
WARDSTONE = (116, 55)         # the broken wardstone at the Fallen Wardstones
LIGHTWELL = (124, 59)         # the Lightwell, in its court
NAGA_STAIR = (22, 38)         # where the naga go down under Saltspine Shore
SPIRE_FOOT = (50, 38)         # the foot of Firstlight Spire, at the head of the Lit Court


def build():
    out = []
    A = out.append

    # ========================================================================= ACT ONE: SURVIVAL (Amberleaf Glade)
    A(Q("dhq_strange_shore", "A Strange Shore", SAELIS, 1, 2, "Shorewalker's",
        "You woke on the Waking Shore with sand in your mouth. Ranger-Captain Saelis Dawnbrook meets everyone the sea "
        "gives up, and the Tideshell Crabs are picking at the people who haven't got up yet.",
        [k("Tideshell Crab", 6)],
        "Breathe slowly, you're all right. You're on Dawnhaven, an island off Azshara, and you're not the first to wake up on this beach. "
        "The Tideshell Crabs come up the sand after anyone who's lying still. Drive them off while I check the "
        "others, and then we'll get you somewhere warm.",
        "That's the beach clear, and you're steadier on your feet than most.\n\nI've walked this shore every morning "
        "for a year. Some mornings there's nobody. Some mornings there are three. Nobody knows why, and I've stopped "
        "asking, and started counting instead.",
        nxt="dhq_up_to_amberwatch"))
    A(Q("dhq_up_to_amberwatch", "Up to Amberwatch", SAELIS, 1, 2, "Newcomer's",
        "Saelis wants you up the path to Amberwatch, the Sunreach Conclave's camp in the old outpost's gatehouse. "
        "Magistrix Iriel Brightleaf runs it, and she'll want your name.",
        [deliver("dh_q_saelis_note", "Take Saelis's note to Magistrix Iriel at Amberwatch")],
        "Amberwatch is up the path, in what's left of the outpost's old gatehouse. Take this note to Magistrix Iriel "
        "Brightleaf. It says you're one of mine and you can walk, which is more than I write for most.",
        "One of Saelis's, are you? Then welcome to Amberwatch.\n\nThis was an elven outpost once, a long time before "
        "any of us. The Conclave took it back last year, after we lost the spires of Quel'Thalas. It's a ruin, but "
        "it's our ruin, and there's room in it for you.",
        grant_items=carry("dh_q_saelis_note", "Saelis's Note", "A folded note in a neat ranger's hand: one more off "
                          "the shore, walking, and asking sensible questions."),
        turn_in_npc_id=IRIEL))
    A(Q("dhq_wyrms_at_the_wards", "Wyrms at the Wards", IRIEL, 2, 3, "Wardkeeper's",
        "The outpost's founders ringed Dawnhaven with wardstones that hid it from the sea. They're broken now, and the "
        "Ward-Drinker Wyrms are feeding on what's left of the magic in them.",
        [k("Ward-Drinker Wyrm", 8)],
        "Those wardstones east of here hid this island for a thousand years. They're broken, and the Ward-Drinker "
        "Wyrms are drinking what little power is left in them. Clear the wyrms off the Fallen Wardstones before "
        "they drain the stones dry.",
        "The stones are quiet again. They're weak, but they're still there, and that's something.\n\nIf I can wake "
        "even one of them, the island stops shouting its whereabouts to everything at sea. I've got an idea how.",
        nxt="dhq_leaf_hearts"))
    A(Q("dhq_leaf_hearts", "Hearts of the Wood", IRIEL, 3, 4, "Leafwarden's",
        "The magic that fed the wardstones has soaked into the woods round them, and some of the trees have got up "
        "and walked. Iriel wants what's in their hearts.",
        [fetch("dh_q_leaf_heart", 5)],
        "The ward magic didn't just vanish when the stones broke. It soaked into the trees, and some of them woke up. "
        "Every Amberwood Wanderer has a Leaf-Heart in it, a knot of the old magic. Bring me some, and I'll give it "
        "back to the stones it came from.",
        "Feel how warm they are. That's the founders' magic, still there after a thousand years.\n\nThere's enough "
        "here to wake one stone. Come with me, I'd like you to be the one who sets them.",
        nxt="dhq_the_first_stone"))
    A(Q("dhq_the_first_stone", "The First Stone", IRIEL, 4, 5, "Stonewaker's",
        "Iriel has the Leaf-Hearts ready. She wants them set in the broken wardstone at the heart of the Fallen "
        "Wardstones, to see if it will wake.",
        [explore(*WARDSTONE, "Set the Leaf-Hearts in the broken wardstone")],
        "Take the Leaf-Hearts to the wardstone in the middle of the ring, the one with the crack down its face, and "
        "press them into the crack. If I've got this right it'll wake. If I haven't, step back quickly.",
        "I felt it from here. It's burning again, one stone out of a ring of nine.\n\nIt won't hide the island on its "
        "own, not yet. But it's the first thing on Dawnhaven we've made work again instead of just living in the "
        "ruins of. I'll remember who lit it."))
    A(Q("dhq_supper", "Supper at Amberwatch", THAELEN, 2, 3, "Cook's",
        "Apothecary Thaelen feeds Amberwatch as well as tending it, and there are more mouths every week. The "
        "Sunmane Boars in Leafwhisper Grove are fat on the autumn mast.",
        [fetch("dh_q_boar_haunch", 6)],
        "Every new arrival eats like they haven't eaten in a week, and most of them haven't. The Sunmane Boars in "
        "Leafwhisper Grove are fat this time of year. Bring me some haunches and Amberwatch eats well tonight.",
        "That's a proper supper. You'll get the first plate, you've earned it.\n\nThe first night here is always the "
        "worst. A hot meal and a fire with people round it does more for them than anything in my bag."))
    A(Q("dhq_goldmane", "Goldmane", THAELEN, 4, 5, "Goldmane",
        "A great gold lynx the scouts call Goldmane has started taking people at the edge of the grove at dusk. "
        "Thaelen has patched up the ones who got away.",
        [k("Goldmane", 1)],
        "There's a lynx in Leafwhisper Grove the scouts call Goldmane, bigger than any cat has a right to be. It's "
        "started taking newcomers who wander off at dusk. I've stitched up two who were lucky. Please find it before "
        "it finds a third.",
        "Goldmane's dead at last. I'll tell the newcomers they can walk to the mere again without looking over their "
        "shoulders.\n\nIt was a beautiful animal. Most of the dangerous ones are.",
        requires_quests=["dhq_supper"]))
    A(Q("dhq_roofs", "Roofs Before the Rain", ROSA, 2, 3, "Roofer's",
        "Rosa Quintero woke on the shore a year ago and started building the day after. Amberwatch's roofs leak, and "
        "the autumn rains are coming. Lynx pelts make good thatch-liners.",
        [fetch("dh_q_lynx_pelt", 5)],
        "I built houses in Valparaiso for twenty-two years, and I know a roof that won't last a storm when I see one. "
        "The Amberleaf Lynx pelts are thick and they shed water. Bring me some and I'll line the worst roofs before "
        "the rain comes.",
        "These are good pelts. Those roofs will hold now, or at least they'll leak somewhere I can live with.\n\nBack "
        "home I'd have had tiles and a crew. Here I've got pelts and whoever walks up the path. I like the people "
        "better.",
        nxt="dhq_old_barnacle"))
    A(Q("dhq_old_barnacle", "Old Barnacle", ROSA, 3, 4, "Barnacle",
        "Rosa keeps a pile of driftwood timber on the Waking Shore, and a great old crab the newcomers call Old "
        "Barnacle has moved into it.",
        [k("Old Barnacle", 1)],
        "I keep my good driftwood in a pile on the beach, and a crab the size of a cart's moved into it. The "
        "newcomers call it Old Barnacle. It took a finger off the last person who tried to fetch me a plank. Please "
        "evict it, permanently.",
        "My timber is mine again. I'll have a new floor in the mess hall by the end of the week.\n\nYou know what the "
        "best part of this place is? Everything I build here is the first one. Nobody's ever done it before."))
    A(Q("dhq_naga_landing", "The Naga Landing", KAELEN, 3, 4, "Covewatcher's",
        "Naga have come ashore in Brinecoil Cove, in the island's south-east. Scout Kaelen Swiftarrow has been "
        "watching them, and he wants them pushed back into the sea.",
        [k("Brinecoil Scout", 6), k("Brinecoil Siren", 4)],
        "Naga came ashore in Brinecoil Cove a month ago, and they've been coming further inland every week since. "
        "Their Brinecoil Scouts walk the beach, and the Brinecoil Sirens sing to the sea all night. Push them back "
        "before they reach the camp.",
        "They've pulled back to the water's edge. They'll come again, but they'll think about it first.\n\nThey're "
        "not raiding. They're looking for something. I'd like to know what.",
        nxt="dhq_orders"))
    A(Q("dhq_orders", "Orders in the Brine", KAELEN, 4, 5, "Orderbreaker's",
        "Kaelen thinks the naga in Brinecoil Cove are under orders. Their sirens carry sealed shell tablets, and he "
        "wants one.",
        [fetch("dh_q_brinecoil_orders", 1)],
        "Every so often one of the Brinecoil Sirens comes out of their cave with a sealed shell tablet. Those are "
        "orders, I'd bet my bow on it. Bring me one, and Iriel can read naga script.",
        "Iriel read it to me. They were sent to find the island the wardstones hid, and to report what's on it.\n\n"
        "They've found us. Their tidecaller in the grotto is the one sending the reports back, and that has to "
        "stop.",
        nxt="dhq_tidecaller"))
    A(Q("dhq_tidecaller", "The Tidecaller", KAELEN, 5, 5, "Tidebreaker's",
        "Tidecaller Sszelith sends the naga's reports back to the sea from the altar at the head of Brinecoil Grotto. "
        "Kaelen wants her stopped before anything bigger comes to answer them.",
        [boss("Tidecaller Sszelith", GROTTO), k("Brinecoil Raider", 5, zone=GROTTO)],
        "Tidecaller Sszelith keeps an altar at the far end of Brinecoil Grotto, up the inlet, and she sends every "
        "scrap her scouts learn back out to sea. Fight past her Brinecoil Raiders and end her. Take friends, because "
        "she won't be alone.",
        "The altar's quiet and the reports have stopped. Whatever sent them will have to come looking on its own "
        "now.\n\nYou've bought us time. On this island, time is the thing we're shortest of."))
    A(Q("dhq_restless", "The Restless Watch", ALDARIA, 4, 5, "Watchwarden's",
        "Priestess Aldaria keeps the names of the outpost's dead at Amberwatch. At the Silent Barrow up the north-west "
        "road, those dead are walking their old rounds and attacking anyone who comes near.",
        [k("Restless Sentinel", 6), k("Forlorn Spirit", 4)],
        "The outpost buried its own at the Silent Barrow, up the north-west road, and they don't rest. The Restless "
        "Sentinels still walk their rounds, and the Forlorn Spirits wail among the stones. Give them some peace, "
        "even if it's only for a night.",
        "It's quieter up there tonight. I could hear it from here.\n\nThey're not wicked, you understand. They're "
        "still on duty. Nobody ever came to relieve them.",
        nxt="dhq_names"))
    A(Q("dhq_names", "Names for the Stone", ALDARIA, 5, 6, "Rememberer's",
        "Aldaria wants the outpost's dead remembered by name. Every Restless Sentinel still wears a silver badge with "
        "its name cut into the back.",
        [fetch("dh_q_sentinel_badge", 6)],
        "The Restless Sentinels still wear their badges, and every badge has a name cut into it. I'd like those names back. "
        "When the dead are remembered properly, they rest easier, and I mean to carve every one into the stone here.",
        "These names haven't been spoken in a thousand years. I'll read them out tonight, every one.\n\nOne badge is "
        "different. It's the warden's, the one who sealed the vault under the barrow with herself inside. She's the "
        "one keeping the others awake.",
        nxt="dhq_warden"))
    A(Q("dhq_warden", "The Warden's Rest", ALDARIA, 6, 6, "Wardenbreaker's",
        "Warden Isilien sealed herself into the Quiet Vault under the Silent Barrow when the outpost fell, to keep its "
        "dead safe. She's still keeping them, and she won't let them go.",
        [boss("Warden Isilien", VAULT), k("Bone-Bound Guard", 4, zone=VAULT)],
        "Warden Isilien sealed the Quiet Vault with herself inside when the outpost fell, and she's held its dead "
        "there ever since. She's not cruel. She just doesn't know the war's over. Go down past the Bone-Bound Guards "
        "to her tomb and let her rest.",
        "I felt them go, all at once, like a held breath let out.\n\nShe kept faith with them for a thousand years. I "
        "hope someone keeps faith with us that long. Thank you for being gentle with her."))
    A(Q("dhq_road_north", "The Road North", SAELIS, 6, 6, "Wayfarer's",
        "Amberwatch is safe now, or safer. Saelis wants you to carry word up the Duskfall road to Lightwarden Selanne "
        "at Dawnrest, where the real work of putting the outpost back has begun.",
        [deliver("dh_q_glade_report", "Take the Glade's report to Lightwarden Selanne at Dawnrest")],
        "You've done more for Amberwatch in a few days than most do in a season. There's a waystation north of here "
        "called Dawnrest, and Lightwarden Selanne is trying to wake the whole outpost, not just the camp. Take her "
        "my report, and take yourself with it.",
        "Saelis sent you? Then you're the one who lit the wardstone and put the warden to rest. Welcome to "
        "Dawnrest.\n\nSurviving was the first thing. Now we find out whether this place can be a home.",
        grant_items=carry("dh_q_glade_report", "The Glade's Report", "Saelis's report on Amberwatch: one wardstone "
                          "burning, the cove quiet, the barrow at rest, and one newcomer worth sending north."),
        turn_in_npc_id=SELANNE, requires_quests=["dhq_tidecaller", "dhq_warden"]))

    # =========================================================================== ACT TWO: REBIRTH (Duskfall Woods)
    A(Q("dhq_dawnrest_stands", "Dawnrest Stands", SELANNE, 5, 6, "Waystation",
        "Dawnrest is the outpost's old waystation, and the Conclave has only just got its roof back on. The woods "
        "round it have run wild in the thousand years it stood empty.",
        [k("Duskfall Prowler", 6, zone=DF), k("Leafweaver Spider", 5, zone=DF)],
        "We put the roof back on Dawnrest a month ago, and the woods haven't decided whether to let us keep it. The "
        "Duskfall Prowlers circle the camp at night, and the Leafweaver Spiders string webs across the road. Show the "
        "woods we're staying.",
        "The road's clear and the night watch can sit down for once.\n\nEvery wall we raise here is a wall the woods "
        "spent a thousand years taking down. We're taking it back one wall at a time.",
        zone=DF, nxt="dhq_the_dark_well"))
    A(Q("dhq_the_dark_well", "The Dark Well", SELANNE, 6, 7, "Wellseeker's",
        "Selanne wants you to see what she's trying to save: the Lightwell in the court beyond the Withered Spires, "
        "which fed the whole outpost once and has been dark for a thousand years.",
        [explore(*LIGHTWELL, "Look into the dark Lightwell", zone=DF)],
        "The Lightwell is east of here, past the Withered Spires, in its own court. It fed this whole outpost with "
        "light and magic once. Go and look at it, and tell me what you feel when you stand over it. I want to know if "
        "it's just me.",
        "So you felt it too, cold, and like something underneath was looking back up at you.\n\nIt's not just dark, "
        "then. Something underneath is taking the light as fast as the well makes it. We'll need to find out what.",
        zone=DF))
    A(Q("dhq_hollow_hunt", "The Hollow Hunt", LYRA, 6, 7, "Hollowhunter's",
        "Huntress Lyra Swiftbough feeds Dawnrest from the Red Hollow, west of the camp. This autumn the bears have "
        "come down bold and the prowlers with them.",
        [k("Hollow Bear", 6, zone=DF), k("Duskfall Prowler", 4, zone=DF)],
        "The Red Hollow feeds Dawnrest, if it's hunted properly. This year the Hollow Bears have come down bold, and "
        "the Duskfall Prowlers follow them for the scraps. Thin them out so my hunters can work.",
        "That's a hunt worth the name. My people can go back into the Hollow without counting their friends "
        "first.\n\nSomething's made them bold. The wild magic in the thicket, I think. Everything on this island "
        "is a little wrong since the well went dark.",
        zone=DF, nxt="dhq_leafweaver_silk"))
    A(Q("dhq_leafweaver_silk", "Leafweaver Silk", LYRA, 6, 7, "Silkweaver's",
        "Lyra's hunters need bowstrings and snares, and Leafweaver silk is the strongest thread on the island.",
        [fetch("dh_q_leafweaver_silk", 6)],
        "Leafweaver silk makes the best bowstrings I've ever drawn, and the best snares. The Leafweaver Spiders in the "
        "Red Hollow are thick with it. Bring me some, and I'll string every bow in Dawnrest.",
        "That's lovely silk, red as the leaves. I'll have new strings on every bow by morning.\n\nThe old outpost's "
        "hunters used this same silk. We found their snares in the Hollow, still set.",
        zone=DF, nxt="dhq_hollow_king"))
    A(Q("dhq_hollow_king", "The Hollow King", LYRA, 7, 8, "Hollow King's",
        "The bears of the Red Hollow follow one old giant the hunters call Ruddy, the Hollow King. Lyra thinks the "
        "Hollow won't settle while he rules it.",
        [k("Ruddy, the Hollow King", 1, zone=DF)],
        "There's a bear in the Red Hollow the hunters call Ruddy, the Hollow King, old and huge and clever. Every bear "
        "in the Hollow follows him, and he's leading them closer to Dawnrest every week. End his reign before he "
        "brings it to our door.",
        "The Hollow King is dead. The bears will scatter, and the Hollow will settle.\n\nI'll make a cloak of his "
        "hide for the hunter who brought him down, which is you. Wear it where the bears can see it.",
        zone=DF))
    A(Q("dhq_spilled_light", "Spilled Light", AERON, 6, 7, "Spillwarden's",
        "When the Lightwell went dark, the outpost's magic spilled out into the woods. Magister Aeron Ashveil says "
        "some of it has woken in the Wildmana Thicket north of Dawnrest.",
        [k("Wildmana Sprite", 7, zone=DF), k("Wildmana Elemental", 4, zone=DF)],
        "The Lightwell's magic didn't vanish when it went dark. It spilled out into the woods, and in the Wildmana "
        "Thicket north of here it woke up. The Wildmana Sprites and the Wildmana Elementals there are the outpost's "
        "own magic gone feral. Calm them, before they spread.",
        "The thicket's calmer. I can feel the difference from here, like a ringing in the ears that's stopped.\n\n"
        "They weren't evil, just lost. Magic needs somewhere to go. This magic used to go into the well.",
        zone=DF, nxt="dhq_shards"))
    A(Q("dhq_shards", "Shards of the Old Magic", AERON, 7, 8, "Shardbearer's",
        "Aeron wants to know why the Lightwell's magic spilled instead of fading. The Wildmana Elementals carry hard "
        "shards of it at their cores.",
        [fetch("dh_q_spilled_shard", 5)],
        "Every Wildmana Elemental carries a Shard of Spilled Light at its core, the old magic pressed hard. Bring me "
        "some. If I can read them, I can tell you why the well's magic ran out into the woods instead of just going "
        "out.",
        "I've read them, and I don't like what they say. The magic didn't spill because the well broke. It ran away.\n\n"
        "Something under the well is hungry, and the magic ran from it. And there's more. Someone down there has been "
        "working with old elven ink.",
        zone=DF, nxt="dhq_last_magister"))
    A(Q("dhq_saltspine_camp", "The Saltspine Camp", NERYS, 6, 7, "Saltspine",
        "The naga have their main camp on Saltspine Shore, on the island's north-west coast. Scout Nerys Duskmantle "
        "has been counting their sentries for three days.",
        [k("Saltspine Warrior", 6, zone=DF), k("Saltspine Siren", 4, zone=DF)],
        "That's the naga's main camp down there on Saltspine Shore. The Saltspine Warriors hold the beach and the "
        "Saltspine Sirens sing to something under the water. Break their sentry line so I can get closer.",
        "Their line's broken and they're scrambling. I can see the whole beach now.\n\nThey don't go into the sea at "
        "night. They go down. There's a way under the shore.",
        zone=DF, nxt="dhq_where_they_go"))
    A(Q("dhq_where_they_go", "Where the Naga Go", NERYS, 7, 7, "Tracker's",
        "Nerys has seen the naga go down somewhere under Saltspine Shore at night. She wants the way found, and word "
        "taken to Magister Aeron at Dawnrest.",
        [explore(*NAGA_STAIR, "Find where the naga go under Saltspine Shore", zone=DF),
         deliver("dh_q_nerys_sketch", "Take Nerys's sketch of the camp to Magister Aeron at Dawnrest")],
        "The naga go down under the shore at night, near the rocks at the north end. Find the way in, then take my "
        "sketch of the camp to Magister Aeron at Dawnrest. If there's magic involved, he'll know what it means.",
        "A temple door under the beach, and sirens singing down into it. And look here, on her sketch. They're "
        "carrying shards like the ones in the thicket.\n\nThe naga have a sea-witch down there, and she's feeding on "
        "the same spilled magic.",
        grant_items=carry("dh_q_nerys_sketch", "Nerys's Sketch", "A charcoal sketch of the Saltspine camp, every "
                          "sentry marked, and a note in the corner: they carry glowing stones down."),
        turn_in_npc_id=AERON, zone=DF))
    A(Q("dhq_sea_witch", "The Sea-Witch", AERON, 9, 9, "Witchbreaker's",
        "Sea-Witch Ilthessa holds the throne pool at the bottom of Saltspine Hollow, drinking the outpost's spilled "
        "magic and sending the naga out for more.",
        [boss("Sea-Witch Ilthessa", HOLLOW), k("Saltspine Myrmidon", 5, zone=HOLLOW)],
        "Sea-Witch Ilthessa sits on a throne at the bottom of Saltspine Hollow, down the terraces under the shore, and "
        "she's drinking the magic the Lightwell lost. Fight down past her Saltspine Myrmidons and end her. Take "
        "friends, because she won't be alone.",
        "She's gone, and the shards she'd gathered are lying cold on the throne. I'll bring them back up.\n\nThat's "
        "one thing that was feeding on the island finished. The other is under the well.",
        zone=DF, requires_quests=["dhq_where_they_go"]))
    A(Q("dhq_last_watch", "The Last Watch", HALION, 7, 8, "Lastwatch",
        "Commander Halion Brightspear held the outpost when it fell, and he still holds it, a spirit in the Withered "
        "Spires. His garrison is still with him, and they've forgotten who they're fighting.",
        [k("Unresting Guardian", 6, zone=DF), k("Withered Magister", 4, zone=DF)],
        "My garrison is still at their posts, but a thousand years has worn them thin. The Unresting Guardians "
        "attack anything that moves, and the Withered Magisters cast at shadows. Put them down. They'd thank you, if "
        "there were enough of them left to.",
        "It's quiet in the spires, the way it was before the end.\n\nI remember their names, every one. I don't "
        "remember my own wife's face any more, but I remember their names.",
        zone=DF, nxt="dhq_spirit_lanterns"))
    A(Q("dhq_spirit_lanterns", "Lanterns for the Lost", HALION, 8, 8, "Lanternbearer's",
        "Halion's dead carried spirit lanterns on their rounds. He wants the lanterns gathered, so that when the time "
        "comes, his garrison can find its way out of the dark.",
        [fetch("dh_q_spirit_lantern", 5)],
        "The Withered Magisters still carry the spirit lanterns we used on night rounds. When the well's lit, and I "
        "think you'll light it, my people will need those lanterns to find their way. Gather them, please.",
        "Five small lights. It's enough to lead them out.\n\nThere's something you should know. When the well went "
        "dark, our archivist went down into the works under it and never came back up. If anyone knows what's down "
        "there, it's him.",
        zone=DF, nxt="dhq_grieving_lady"))
    A(Q("dhq_grieving_lady", "The Grieving Lady", HALION, 8, 9, "Mourner's",
        "A spirit walks the Withered Spires weeping, and her grief turns the living cold. Halion knew her, once.",
        [k("The Grieving Lady", 1, zone=DF)],
        "There's a spirit in the Withered Spires the scouts call the Grieving Lady. She was our healer. She lost "
        "everyone she tried to save the night the outpost fell, and she's never stopped weeping for them. End her "
        "grief, please, gently.",
        "She's quiet now. I hope she's found them, wherever they are.\n\nThank you. I couldn't do it myself. I "
        "tried, a hundred times, and every time I heard her I put my sword down.",
        zone=DF))
    A(Q("dhq_last_magister", "The Last Magister", AERON, 9, 9, "Archivist's",
        "The outpost's archivist, Lorethas, went down into the works under the Lightwell when it went dark and never "
        "came back. Aeron's shards say someone below is still writing.",
        [boss("Archivist Lorethas", DEEP), k("Lorebound Shade", 4, zone=DEEP)],
        "Commander Halion says the outpost's archivist, Lorethas, went down under the well and never came up. My "
        "shards say someone below is still working with elven ink. I think Archivist Lorethas found the hunger under the "
        "well and bargained with it. Find him in the archive below, past his Lorebound Shades, and end it.",
        "Then it's true. He was feeding the hunger the outpost's dead, a few at a time, to keep it from coming up. "
        "That's why they never rested.\n\nHe thought he was saving us. Now the hunger has nothing to eat, and it'll "
        "come up looking. Selanne needs to know.",
        zone=DF, requires_quests=["dhq_spirit_lanterns"]))
    A(Q("dhq_starved_light", "The Starved Light", SELANNE, 9, 9, "Lightbringer's",
        "Under the Lightwell, in the font chamber of the old works, the hunger that put out the outpost's light has "
        "taken a shape. Selanne calls it the Starved Light.",
        [boss("The Starved Light", DEEP), k("Hungering Remnant", 5, zone=DEEP)],
        "The thing under the well is called the Starved Light now, because that's what it is: a hunger that ate the "
        "outpost's light and wants more. It's in the font chamber at the top of the works, under the Lightwell. Go "
        "down past the Hungering Remnants and end it. Take friends, and take the light with you.",
        "It's gone for good. I can feel the well filling from here, slow and warm, like a hearth catching.\n\nGo and look at "
        "it. You lit it. You should be the first to see it burn.",
        zone=DF, requires_quests=["dhq_last_magister", "dhq_the_dark_well"], nxt="dhq_first_light"))
    A(Q("dhq_first_light", "First Light", SELANNE, 9, 9, "Firstlight",
        "The Starved Light is gone, and the Lightwell is filling again. Selanne wants you to see it burn, and then go "
        "up the Spire road to Firstlight Spire, where the Spire-Keeper is waiting.",
        [explore(*LIGHTWELL, "See the Lightwell burning", zone=DF)],
        "Go and stand over the well, and then go north up the Spire road. Spire-Keeper Lorien Ashbloom has swept the "
        "spire's stair every day for years, waiting for this. He'll want to hear it from you.",
        "I saw it from the top of the stair before you got here. The spire caught the well's light and it's burning "
        "for the first time in a thousand years.\n\nCommander Halion's people went out with the lanterns at dawn. "
        "He went last. He asked me to tell you he was relieved of duty, and that he was grateful.",
        zone=DF, turn_in_npc_id=LORIEN))

    # ======================================================================= ACT THREE: PROGRESS (Firstlight Spire)
    A(Q("dhq_the_spire_wakes", "The Spire Wakes", LORIEN, 9, 9, "Spirewalker's",
        "Firstlight Spire is lit for the first time in a thousand years, and Grand Magister Velanthe has brought the "
        "Sunreach Conclave home to it. Lorien wants you to stand at its foot.",
        [explore(*SPIRE_FOOT, "Stand at the foot of the lit spire", zone=FS)],
        "Go and stand at the foot of the spire, in the Lit Court. The founders built it as the first light a ship "
        "would see coming to Dawnhaven, and it's burning again. The Grand Magister calls this the Conclave's home now. "
        "Go and see what you've given us.",
        "Everyone came out to look. The newcomers from the shore, the Conclave, the hunters from Dawnrest, all of us "
        "standing in the court with our heads tipped back.\n\nWe lost the spires of Quel'Thalas. We'll never get them "
        "back. But this one is ours, and we lit it ourselves.",
        zone=FS, nxt="dhq_room_for_everyone"))
    A(Q("dhq_room_for_everyone", "Room for Everyone", LORIEN, 9, 9, "Hearthkeeper's",
        "Firstlight Spire has rooms to spare now, and Lorien means for every newcomer the sea gives up to have one. "
        "The innkeeper keeps the register.",
        [deliver("dh_q_spire_key", "Take the spire's first key to Innkeeper Liriel")],
        "This is the first key to the spire's guest rooms. Take it to Innkeeper Liriel. From tonight, everyone who "
        "wakes on the Waking Shore gets a bed in Firstlight Spire, a hot meal and a name in the register, for as long "
        "as they want them.",
        "The first key. I'll hang it over the hearth so everyone can see it.\n\nThe register's open. Your name goes "
        "first, if you'll write it. You were a newcomer once too, not so long ago.",
        grant_items=carry("dh_q_spire_key", "The Spire's First Key", "A small bronze key on a red cord, the first "
                          "key to the guest rooms of Firstlight Spire."),
        zone=FS, turn_in_npc_id=INNKEEPER))
    A(Q("dhq_the_first_crossing", "The First Crossing", JOOST, 9, 10, "Crossing",
        "Joost Achterberg has the Spire's boat ready, and the Conclave has a letter for Orgrimmar: Dawnhaven is open, "
        "and its people will stand with the Horde. The first crossing goes to a pier on Durotar's north-east coast.",
        [deliver("dh_q_conclave_letter", "Carry the Conclave's letter across to the dockhand at Durotar's pier")],
        "Forty years I piloted ships into Rotterdam, and I've never been prouder of one than this little boat. The "
        "Conclave has a letter for Orgrimmar, and the Grand Magister wants it carried by someone from the island, "
        "and that's you. Step aboard, and we'll make the first crossing together.",
        "From Dawnhaven, is it? The elves said a boat might come. I'll see the letter goes up the road to Orgrimmar "
        "today.\n\nOrgrimmar's north of here, and Razor Hill's south-west. Welcome to Durotar. It's a long way from "
        "an island, and it'll be glad of you.",
        grant_items=carry("dh_q_conclave_letter", "The Conclave's Letter", "A letter sealed in gold wax with the "
                          "Sunreach sun: Dawnhaven is open, and its people will stand with the Horde."),
        zone=FS, turn_in_npc_id=DOCKHAND, requires_quests=["dhq_the_spire_wakes"]))
    return out
