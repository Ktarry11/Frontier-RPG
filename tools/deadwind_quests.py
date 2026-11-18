"""
Deadwind Pass's quests: the tunnel, both maps of the pass, Ariden's Watch, the two caves and the Exclusion Zone.
Levels 55-60. Read by tools/build_deadwind_quests.py, which holds them to every rule before anything is written. The
plan is docs/deadwind_quest_plan.md and the vision docs/deadwind_brief.md.

Kyle, 18 Nov 2026: "beautifully written quests. Lots of lore....they should be exciting to do", then "ensure that the
writing is pristine and storydriven and good", and "I love the history of Chernobyl in real life and I want this to
do it justice."

THE STORY. When the worlds came together, the leylines under Deadwind tore, and two things came out: time broke, and
the fallout leaked. The question under every quest is whether the tear is healing or growing, and the answer is
worse: it's remembering. Everything that dies near it, it keeps a copy of, and the copies are what crawl out. The
liquidators hold Ariden's Watch against it. Halyna Bondar runs the camp; her brother Mykola went down into the tear
three months ago and didn't come back.

THE THREADS, so a player meets the same people over and over and sees them change:
  Tomas, the runner who never reached the fence (the first quest), whose name goes on the board at the end.
  Mykola: the Bridge Echo, the Stopped Man, and Halyna's last quest.
  Morwen and Lisbeth: what the head apothecary is really testing the Seep on, and who she reports to.
  Agatha Morgan and the coachman who crashes below her family's graves.
  Grull, and the chief who is two ogres at once.
  Ariden, and the evening he can't get out of.
  The board of names, read at the start and read again at the end.

CHERNOBYL is in the liquidators' mouths, never as an object (Kyle: "JUST the wheel"): the word itself, the three days
they told Pripyat it would be, the bridge where people stood to watch the fire, the divers who drained the pools, the
ninety-second shifts on the roof, the miners who dug under the reactor, the iodine, the Red Forest, the dogs, the old
women who walked back in. The others came from the places where it happened too: Fukushima, the Nevada downwind,
Semey, Goiania, Rongelap.

VOICE (Kyle): whole sentences the way a person says them, contractions, no dashes, no sentence of one or two words,
the useful thing first, every kill target named, no count beside an objective word.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

# ---- the maps (the key the game passes on a kill: the map's name lowercased, spaces to underscores, no apostrophes)
DW, DE, AW = "deadwind_west", "deadwind_east", "ariden_watch"
WN, DS, EZ = "the_widows_nest", "the_drowned_seep", "the_exclusion_zone"
GG = "gromgol"

# ---- the people
HALYNA, KENJI, HARROW, TOBIAH = "dw_halyna", "dw_kenji", "dw_harrow", "dw_tobiah"
AIGERIM, MORWEN, LISBETH, LUIZ = "dw_aigerim", "dw_morwen", "dw_lisbeth", "dw_luiz"
RINE, SELA = "dw_rine", "dw_innkeeper"
DELGADO, AGATHA, GRULL, HANNA = "dw_delgado", "dw_mourner", "dw_grull", "dw_hanna"
ARIDEN, ECHO, VESSA = "dw_ariden", "dw_bridge_echo", "dw_vessa"
PELL = "gromgol_storesman"

WATCH_GIVERS = {HALYNA, KENJI, HARROW, TOBIAH, AIGERIM, MORWEN, LISBETH, LUIZ, RINE, SELA}
HUB_GIVERS = WATCH_GIVERS


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone, radius=6):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Tunnel Slagcrawler": [("dw_q_seep_glass", "Seep-Glass Shard", "A sliver of black glass with a green light "
                            "caught somewhere inside it. It's warm, and it shouldn't be.")],
    "Grave Ooze": [("dw_q_grave_tallow", "Grave Tallow", "A greasy lump skimmed off a grave ooze. It smells of "
                    "candles and something worse.")],
    "Pustule Boar": [("dw_q_swollen_gland", "Swollen Gland", "A gland the size of a fist, tight and shining. Morwen "
                      "wants them whole.")],
    "Plot Risen": [("dw_q_seep_marrow", "Seep-Soaked Marrow", "Marrow from a thighbone, gone the colour of weak "
                    "tea and glowing faintly at the break.")],
    "Tumour Wolf": [("dw_q_tumour", "Wolf Tumour", "A hard grey lump cut from a wolf's flank. Dr. Seitkali wraps "
                     "every one in its own cloth.")],
    "Bridge Onlooker": [("dw_q_glowing_trinket", "Glowing Trinket", "A button, a comb, a broken buckle, each of "
                         "them glowing a soft green. Somebody picked it up because it was pretty.")],
    "Grosh'gok Sore-Shaman": [("dw_q_totem_piece", "Piece of the Grosh'gok Totem", "A carved chunk of old wood "
                               "painted with an ogre's handprint, small, like a child's.")],
    "Funnel Widow": [("dw_q_widow_silk", "Clean Widow Silk", "A hank of silk from the inside of the funnel, where "
                      "the glow never reached. It's as soft as anything you've ever touched.")],
    "Book Flock": [("dw_q_archivist_page", "A Page in Nine Hands", "A page from Karazhan's library, written by one "
                    "hand at nine different ages. The ink is fresh on all nine.")],
    "Gorge Slagcrawler": [("dw_q_slag_ore", "Slag Ore", "A heavy lump of the slag that crusts the gorge, black "
                           "and green, dense as lead.")],
    "Stopped Volunteer": [("dw_q_liquidator_kit", "A Liquidator's Kit", "A canvas satchel with a beaked mask, a "
                           "dosimeter and a ration tin in it. The name stitched inside the flap is still legible.")],
    "Aged Volunteer": [("dw_q_liquidator_kit", "A Liquidator's Kit", "A canvas satchel with a beaked mask, a "
                        "dosimeter and a ration tin in it. The name stitched inside the flap is still legible.")],
    "Bubbler Ooze": [("dw_q_bubbler_sample", "Bubbler Pool Sample", "A sealed flask of the seep from the bottom of "
                      "the Bubbler Pools. It glows through the glass and the stopper.")],
}
STARTER_DROPS = {}
STARTER_IDS = {}

#: reward triples, (slot, kind, type, identity), cycled through so every spec gets something (the builder checks it)
CYCLE = [
    [("chest", "armor", "mail", "hunter"), ("waist", "armor", "cloth", "caster"), ("feet", "armor", "plate", "tank")],
    [("hands", "armor", "leather", "agility"), ("shoulder", "armor", "mail", "tide_healer"), ("neck", "armor", None, "caster")],
    [("back", "armor", None, "physical"), ("wrist", "armor", "cloth", "healer"), ("legs", "armor", "plate", "strength")],
    [("head", "armor", "leather", "bear"), ("ring", "armor", None, "healer"), ("hands", "armor", "mail", "earthen")],
    [("main_hand", "weapon", "staff", "caster"), ("chest", "armor", "leather", "strength"), ("waist", "armor", "plate", "plate_healer")],
    [("shoulder", "armor", "cloth", "caster"), ("legs", "armor", "leather", "agility"), ("wrist", "armor", "plate", "tank")],
    [("off_hand", "weapon", "shield", "haste_caster"), ("feet", "armor", "mail", "hunter"), ("chest", "armor", "cloth", "spirit_healer")],
    [("off_hand", "weapon", "shield", "shield_tank"), ("legs", "armor", "leather", "bear"), ("hands", "armor", "cloth", "arcane")],
    [("main_hand", "weapon", "polearm", "strength"), ("head", "armor", "cloth", "healer"), ("hands", "armor", "leather", "feral")],
    [("legs", "armor", "mail", "storm"), ("back", "armor", None, "caster"), ("shoulder", "armor", "plate", "strength")],
    [("main_hand", "weapon", "staff", "agility"), ("waist", "armor", "leather", "agility"), ("ring", "armor", None, "strength")],
    [("chest", "armor", "plate", "plate_healer"), ("feet", "armor", "cloth", "caster"), ("wrist", "armor", "mail", "wildheart")],
    [("ranged", "weapon", "bow", "hunter"), ("head", "armor", "mail", "tide_healer"), ("legs", "armor", "cloth", "caster")],
    [("main_hand", "weapon", "dagger", "agility"), ("shoulder", "armor", "leather", "healer"), ("feet", "armor", "plate", "strength")],
    [("off_hand", "weapon", "tome", "healer"), ("hands", "armor", "plate", "tank"), ("waist", "armor", "mail", "hunter")],
    [("main_hand", "weapon", "mace_1h", "healer"), ("chest", "armor", "leather", "wildheart"), ("neck", "armor", None, "strength")],
    [("main_hand", "weapon", "sword_2h", "strength"), ("wrist", "armor", "leather", "agility"), ("head", "armor", "cloth", "caster")],
]
_cyc = [0]


def R():
    """The next reward triple off the cycle."""
    r = CYCLE[_cyc[0] % len(CYCLE)]
    _cyc[0] += 1
    return list(r)


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=AW, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# --------------------------------------------------------------------------------------------- places on the maps
# Deadwind West
TUNNEL_CART = (38, 158)
SICKWATER_READING, TARN_READING, WOOD_READING = (110, 36), (84, 142), (152, 44)
MORGAN_CRYPT, COACH_WRECK, BLACK_WELL = (146, 130), (138, 90), (100, 147)
# Deadwind East
STOPPED_WATER, STOPPED_PLACES, HANGING_SLIDE = (68, 80), (112, 72), (96, 46)
KARAZHAN_FOOT, TIME_DOOR = (148, 138), (124, 74)
SPIRE_BASE, CRATER_LIP, WHEEL_WEST, WHEEL_EAST = (136, 102), (152, 97), (142, 92), (162, 92)
# Ariden's Watch
NAMES_BOARD, SEALED_STORE, PYRE = (40, 34), (30, 68), (48, 40)


def build():
    out = []
    A = out.append

    # ======================================================================================= 1. A GLOW IN THE WRONG PLACE
    A(Q("dw_the_runners_cart", "The Runner's Cart", PELL, 55, 55, "Runner's",
        "A crack opened in the mountain on the far side of the Rotvine Fen when the worlds came together, and the "
        "liquidators in Deadwind Pass, newcomers every one of them, send a runner down through it for supplies. Storesman Pell has had their "
        "runner, Tomas, through Grom'gol every week for a year.\n\nThis week Tomas left with a handcart of iodine "
        "and bandages, and nobody at the far end has seen him.",
        [explore(*TUNNEL_CART, "Find Tomas's handcart in the cracked tunnel", DW)],
        "The tunnel's in the rock past the fen, east of the Steps. Follow the cart ruts. If you find Tomas, tell him "
        "he still owes me for a sack of salt.",
        "You found the cart and not the boy. I know how that goes.\n\nI'm Corporal Delgado, and this is my fence. "
        "Tomas made this run forty times, and he never once left his cart.",
        zone=GG, turn_in_npc_id=DELGADO))
    A(Q("dw_still_clicking", "Still Clicking", DELGADO, 55, 55, "Clicking",
        "Tomas's dosimeter was hanging off the handle of his cart, still counting. Corporal Delgado wants Kenji "
        "Watanabe to read it, because Kenji can tell from a dosimeter where a man walked and how long he stood "
        "there.\n\nKenji is at his map table in Ariden's Watch, north up the old pass road.",
        [deliver("dw_q_tomas_dosimeter", "Bring Tomas's dosimeter to Kenji Watanabe in Ariden's Watch")],
        "Up the road to Deadman's Crossing, and the Watch is through the gate on your right. Scrub at the troughs "
        "before you hand it over, or Harrow won't let you past him.",
        "His readings climb steadily for an hour, and then they climb very fast, and then they stop.\n\nHe didn't "
        "walk back toward the fence. He walked north, into the pass, toward the wheel. I'll put his name on the "
        "board tonight.",
        turn_in_npc_id=KENJI, zone=DW,
        grant_items=carry("dw_q_tomas_dosimeter", "Tomas's Dosimeter", "A brass and glass dosimeter on a leather "
                          "strap. Its needle is pressed hard against the end of the scale.")))
    A(Q("dw_glow_in_the_rock", "Glow in the Rock", DELGADO, 55, 55, "Rockglow",
        "The fallout is getting into the rock of the tunnel, and things are growing out of it where it pools. "
        "Corporal Delgado calls them slagcrawlers, and every week there are more between his fence and the fen.\n\n"
        "He wants the Tunnel Slagcrawlers cleared before they reach the Stranglethorn end.",
        [k("Tunnel Slagcrawler", 8, DW)],
        "They're in the tunnel south of the fence, mostly where the walls glow. When we opened this crossing the "
        "rock was clean all the way down, and that was a year ago.",
        "That's a lot better for the fence. The glow's still in the rock, and they'll grow back, but slower.\n\nIn Utah my grandmother kept a "
        "jar of the dirt from her yard on the windowsill. She said she wanted to see it the day it stopped "
        "being poison. It never did."))
    A(Q("dw_the_board_by_the_pyre", "The Board by the Pyre", HARROW, 55, 55, "Pyrewatch",
        "Deathguard Harrow keeps the gate at Ariden's Watch, and every newcomer gets the same order from him: scrub "
        "at the troughs, then go and read the board by the pyre before you do anything else.\n\nEvery name on the "
        "board is someone Deadwind has taken since the camp was built.",
        [explore(*NAMES_BOARD, "Read the board of names beside the pyre in Ariden's Watch", AW, radius=4)],
        "Read all of it. Old Tobiah keeps the pyre and the board both, and he'll want to know you did.",
        "Every name, all the way down? Most of them don't. They read the first few and look at the fire instead.\n\n"
        "My name's Tobiah. I burn what the pass kills so it doesn't get up again, and I talk to it while it burns, and "
        "afterwards I write the name down if it had one.",
        turn_in_npc_id=TOBIAH))
    A(Q("dw_what_a_liquidator_is", "What a Liquidator Is", HALYNA, 55, 55, "Liquidator's",
        "Chief Liquidator Halyna Bondar runs Ariden's Watch, and she has a job for anyone Tobiah sends her. The "
        "Tumour Wolves come down out of the dead forest after the supply carts, and they've taken two drivers this "
        "month.\n\nHalyna wants the road kept clear between the fence and Deadman's Crossing.",
        [k("Tumour Wolf", 10, DW)],
        "Every Tumour Wolf in the dead forest hunts along the pass road. Don't let them bite you, and wash at the "
        "troughs when you come back, every time.",
        "Thank you. You asked what we are, so I'll tell you.\n\nIn 1986 a reactor exploded at Chernobyl, and the "
        "Soviet government sent six hundred thousand people to clean it up. They called them likvidatory. My "
        "father was one. We took the word because it's the only honest one we know.",
        requires_quests=["dw_the_board_by_the_pyre"]))
    A(Q("dw_readings_in_the_dead_forest", "Readings in the Dead Forest", KENJI, 55, 56, "Surveyor's",
        "Kenji Watanabe maps the fallout across the pass, and he wants three fresh readings from the west: the "
        "Sickwater where it comes off the mountain, the Black Tarn where it pools, and the Widows' Wood.\n\nHe'll "
        "give you a dosimeter of his own to carry. He makes them out of Seep-glass and cat gut.",
        [explore(*SICKWATER_READING, "Take a reading where the Sickwater comes off the mountain", DW),
         explore(*TARN_READING, "Take a reading on the shore of the Black Tarn", DW),
         explore(*WOOD_READING, "Take a reading in the Widows' Wood", DW)],
        "Hold it at arm's length and count to sixty, and don't stand in the water. At Fukushima we did this on foot "
        "for three years, house by house, until we knew every field by its number.",
        "The tarn is twice what it was a month ago, and the wood is worse than the tarn.\n\nIt's coming from the "
        "east, from the wheel, and it isn't coming steadily. It comes in pulses, like breathing.",
        requires_quests=["dw_still_clicking"]))

    # ======================================================================================= 2. THE DEAD FOREST
    A(Q("dw_downwind", "Downwind", DELGADO, 56, 56, "Downwind",
        "When the wind comes off the middle of the pass, the Fused Bats ride it west and roost in the tunnel, and "
        "they carry the fallout on their wings. Corporal Delgado has watched them do it every evening for a week.",
        [k("Fused Bat", 8, DW)],
        "The Fused Bats roost in the tunnel and hunt over the Sickwater at dusk. You'll want a scarf over your mouth.",
        "My grandmother's town was downwind of the Nevada test site in the fifties. The government told them the "
        "clouds were safe and the cancer came twenty years later, a whole town of it.\n\nSo when something here "
        "rides the wind toward people, I kill it."))
    A(Q("dw_too_many_eyes", "Too Many Eyes", DELGADO, 56, 56, "Watcher's",
        "The Many-Eyed Crows sit along the fence posts and watch the camp, and Corporal Delgado swears they "
        "watch in shifts. The Forsaken say crows like that carry what they see back to whatever made them.",
        [k("Many-Eyed Crow", 10, DW)],
        "The Many-Eyed Crows are all over the dead forest. Shoot the ones on the fence first. I don't care what "
        "they're carrying, I care that they're watching.",
        "That's a lot quieter. I can't prove they were reporting to anything.\n\nThe ones you missed went east, all of "
        "them, the same way, toward the middle of the pass."))
    A(Q("dw_nothing_up_the_sickwater", "Nothing Up the Sickwater", HARROW, 56, 56, "Gatekeeper's",
        "The Sickwater runs past the camp's well on its way south, and the Sickwater Leeches have started coming "
        "up out of it at night. Deathguard Harrow found one in the water barrel this morning.",
        [k("Sickwater Leech", 10, DW)],
        "Follow the Sickwater north or south of the ford, and kill every Sickwater Leech you see in it. The living "
        "drink from that well, and I'd like them to keep living.",
        "The barrel's clean and the well's clean. I'm the only one at this gate who doesn't need to drink, so I'm "
        "the only one who remembers to check."))
    A(Q("dw_the_ones_that_got_up", "The Ones That Got Up", TOBIAH, 56, 56, "Pyrekeeper's",
        "The dead at Morgan's Plot don't stay in the ground any more, and Old Tobiah can't carry them all back to "
        "his pyre. The Plot Risen walk the graves in the south-east of the pass.\n\nHe wants them put back down, "
        "and he'll do the rest.",
        [k("Plot Risen", 10, DW)],
        "Morgan's Plot is south of Coachman's Bend, under the cliff. Put the Plot Risen down and leave them. I'll "
        "go out with the cart tonight and fetch them home.",
        "Thank you. I'll bring them back one at a time and tell each of them where they are.\n\nThey were buried "
        "once, properly, by people who loved them. Something dug them up and wore them, and that isn't their "
        "fault."))
    A(Q("dw_tallow_for_the_pyre", "Tallow for the Pyre", TOBIAH, 56, 56, "Tallowed",
        "The dead forest burns green and fast, and Old Tobiah's pyre eats it faster than he can cut it. He's found "
        "that the tallow the Grave Oozes leave behind them burns slow and hot, and it doesn't smoke as badly.",
        [fetch("dw_q_grave_tallow", 6)],
        "The Grave Oozes seep up out of the graves at Morgan's Plot. Skim the tallow off them and bring it here. "
        "This fire hasn't gone out once since the camp was built, and it isn't going to go out on my watch.",
        "That'll keep it going for a week.\n\nKenji says there's a forest at home in Chernobyl that turned red "
        "and died in a few days, and they had to bury the trees. Here we burn them. I think that's kinder."))
    A(Q("dw_samples_living", "Samples, Living", MORWEN, 55, 55, "Apothecary's",
        "Master Apothecary Morwen Ashgrave studies what the Seep does to living things, and she wants glands from "
        "the Pustule Boars, whole, before they burst.\n\nThe Undercity pays her to know what the Seep is. She "
        "says she has reasons of her own as well.",
        [fetch("dw_q_swollen_gland", 6)],
        "The Pustule Boars root all through the dead forest. Cut the glands out cleanly, and don't squeeze them. "
        "I've lost two assistants to impatience.",
        "Beautiful, isn't it? Look at the colour inside.\n\nThe Seep doesn't kill tissue, you see. It keeps it growing "
        "long after it should stop. That's what the tumours are, and the extra eyes. It's life that doesn't know "
        "when to end.",
        nxt="dw_samples_dead"))
    A(Q("dw_samples_dead", "Samples, Dead", MORWEN, 56, 56, "Marrowed",
        "Morwen Ashgrave has seen what the Seep does to the living, and now she wants to see what it does to the "
        "dead. The Plot Risen have marrow in them that glows.",
        [fetch("dw_q_seep_marrow", 6)],
        "The Plot Risen at Morgan's Plot. Break the long bones and take the marrow from the break. It'll be warm. "
        "Don't let that alarm you.",
        "Warm, and soft, and alive. It's mending, in dead bone.\n\nThank you. That will be all for now. Lisbeth "
        "will see you out."))
    A(Q("dw_what_master_ashgrave_keeps", "What Master Ashgrave Keeps", LISBETH, 56, 56, "Ledger",
        "Apothecary Lisbeth Vane is Morwen Ashgrave's second, and she's worried about her. Morwen locks her own "
        "notes in the sealed store behind the laboratory, and lately she's been taking samples in there and not "
        "bringing them out.\n\nLisbeth can't be seen going in herself.",
        [explore(*SEALED_STORE, "Look inside the sealed store behind the laboratory", AW, radius=3)],
        "The sealed store's behind the laboratory, south-west of the pyre. The lock's for the living. You'll get "
        "past it. Just look, and tell me what you saw.",
        "Her own arm? She's been injecting the Seep into her own arm?\n\nAnd the arm's healing. The rot's going "
        "out of it, the flesh is coming back. She's found a way for us to stop rotting, and she hasn't told "
        "anyone.",
        requires_quests=["dw_samples_dead"], nxt="dw_a_sample_of_her_own"))
    A(Q("dw_a_sample_of_her_own", "A Sample of Her Own", LISBETH, 56, 56, "Confessor's",
        "Lisbeth Vane took one of Morwen's vials out of the sealed store, and she doesn't know whether to send it "
        "to the Royal Apothecary Society or to throw it in the pyre.\n\nShe wants Morwen to see that someone knows, "
        "and she wants it to be you who hands it to her.",
        [deliver("dw_q_morwens_vial", "Give Morwen Ashgrave back her vial")],
        "Give it to her and see what she says. If she lies to you, I'll know what to do with it. If she doesn't, "
        "I'll have to think.",
        "So Lisbeth found it.\n\nI've been dead twelve years. I can feel my fingers again, and I'd forgotten what "
        "that was like. I know what the Seep does to the living, and I know what it would do to the Undercity if "
        "the Society got its hands on it. I'll tell them myself, when I know it's safe.",
        turn_in_npc_id=MORWEN,
        grant_items=carry("dw_q_morwens_vial", "Morwen's Vial", "A stoppered glass vial of the Seep, labelled in a "
                          "fine hand: 'Subject: M. A. Dose eleven.'")))
    A(Q("dw_what_the_wolves_carry", "What the Wolves Carry", AIGERIM, 55, 55, "Physician's",
        "Dr. Aigerim Seitkali runs the infirmary at Ariden's Watch, and she wants to understand the tumours before "
        "they show up in her patients. The Tumour Wolves carry them in every stage.",
        [fetch("dw_q_tumour", 6)],
        "The Tumour Wolves run the dead forest along the pass road. Cut the growths out and wrap each one on its "
        "own. I'll want to know how fast they grow.",
        "These are the same as the ones I saw in Semey.\n\nThe Soviets tested their bombs on the Polygon for forty "
        "years, more than four hundred and fifty of them, and the wind blew across our town the whole time. Nobody told us. "
        "I learned to read these before I learned to drive."))
    A(Q("dw_the_dying_stags", "The Dying Stags", AIGERIM, 56, 56, "Merciful",
        "The Dissolving Stags are coming apart while they're still walking, and they come to the camp's fence at "
        "night as if someone there could help them. Dr. Seitkali can't.\n\nShe's asked for someone to end it for "
        "them, quickly.",
        [k("Dissolving Stag", 8, DW)],
        "The Dissolving Stags graze the dead forest and the shore of the Black Tarn. Be quick about it. They've "
        "suffered more than enough already.",
        "Thank you. I'm a doctor, and I know when nothing more can be done.\n\nAt home in Semey there was a museum of "
        "jars, animals and children born near the Polygon. I used to think it was cruel to keep them. Now I think "
        "it was the only way anyone would believe us."))
    A(Q("dw_seep_glass", "Seep-Glass", LUIZ, 55, 55, "Scavenger's",
        "Luiz Ferreira scavenges for the camp, and Kenji needs Seep-glass for the dosimeters he builds. The "
        "Tunnel Slagcrawlers grow it on their backs.\n\nLuiz won't let anyone else in the camp handle the glass. "
        "He wants it brought straight to him.",
        [fetch("dw_q_seep_glass", 6)],
        "The Tunnel Slagcrawlers are in the cracked tunnel south of Delgado's fence. Wrap the shards before you "
        "put them in your pack, and don't keep one for yourself, however pretty it is.",
        "Thank you. These go to Kenji, in a lead box, and the box stays shut until he opens it.\n\nIn Goiania the "
        "scrapyard man gave the glowing powder away to his family and friends, because it was beautiful. A little "
        "girl ate her dinner with it on her hands. I was nine, and I knew her."))
    A(Q("dw_a_name_worn_away", "A Name Worn Away", AGATHA, 56, 56, "Mourner's",
        "Agatha Morgan's family buried their dead at Morgan's Plot for two hundred years, and her son is in the "
        "crypt on the north side. When the tear opened, time ran fast over the Plot for a moment, and his name "
        "was aged off the stone.\n\nShe can't read it. She'd like someone to try.",
        [explore(*MORGAN_CRYPT, "Look for a name on the Morgan crypt", DW, radius=4)],
        "It's the small crypt on the north side, with the angel beside it. Run your hand over the door. "
        "Sometimes you can feel a name you can't see.",
        "There isn't a letter left on it.\n\nI've buried him, and lost him, and forgotten the shape of his name all in "
        "the same lifetime. I'd hoped it was only my eyes.",
        nxt="dw_the_coachmans_plate", zone=DW))
    A(Q("dw_the_coachmans_plate", "The Coachman's Plate", AGATHA, 56, 56, "Coachman's",
        "Agatha Morgan's son drove the mail coach over the pass, before the plague came west. He went off the "
        "road at the bend below the Plot one winter, and the coach went with him.\n\nThe wreck still lies at "
        "Coachman's Bend, and the old coaches carried their driver's name on a brass plate.",
        [explore(*COACH_WRECK, "Find the brass plate on the wreck at Coachman's Bend", DW, radius=4)],
        "Coachman's Bend is north of here, on the road. Something crashes there every few minutes. Don't stand "
        "in the road when it does.",
        "It says Edwin Morgan, Coachman, my Edwin.\n\nAnd you say the wagon comes down the hill again every few minutes, and "
        "the driver goes over the edge again, and he's wearing my son's coat. Then it isn't only his name the "
        "pass has kept.",
        nxt="dw_again_and_again", zone=DW))
    A(Q("dw_again_and_again", "Again, and Again", AGATHA, 56, 56, "Edwin's",
        "The tear kept a copy of Edwin Morgan's last moment, and it plays it over and over at Coachman's Bend: "
        "the coach, the ice, the drop. The Wagon Driver is what's left of him, and he's crashed a thousand times.\n\n"
        "Agatha wants it to stop. If he's killed outside the moment, the next crash won't come.",
        [boss("The Wagon Driver", DW)],
        "Wait for the coach at Coachman's Bend and catch the Wagon Driver before he reaches the edge. Be gentle "
        "with him if you can, and quick if you can't.",
        "The road's quiet. I stood there an hour and nothing came down it.\n\nI'll carve his name myself, deep "
        "this time, with my own two hands. Thank you for giving him back to me long enough to bury.",
        zone=DW))
    A(Q("dw_hannas_potatoes", "Baba Hanna's Potatoes", HANNA, 56, 56, "Kupuvate",
        "Baba Hanna lives alone in a lean-to in the dead forest west of Deadman's Crossing, and she grows potatoes "
        "in the poisoned ground. The liquidators have asked her to move into the Watch a dozen times.\n\nThe "
        "Pustule Boars have found her garden.",
        [k("Pustule Boar", 8, DW)],
        "The Pustule Boars come out of the trees all round my garden at dawn. Chase them off for good. I'm too old "
        "to sit up all night with a stick.",
        "So I'll have potatoes this winter after all.\n\nThey moved us out of Kupuvate in 1986 and told us it was "
        "for three days. I went back the next spring with my sister, through the wire, and we lived there thirty "
        "years. The soldiers left us bread. Nobody bothers an old woman in a poisoned village.", zone=DW))
    A(Q("dw_the_well", "The Well", HANNA, 56, 56, "Wellwater",
        "Baba Hanna drinks from the old well on the shore of the Black Tarn, and lately the water tastes of "
        "pennies. She wants someone to look down it and tell her what they see.",
        [explore(*BLACK_WELL, "Look down the old well on the shore of the Black Tarn", DW, radius=4)],
        "The well's on the tarn's north-east shore, with the stone ring round it. Look down it, that's all. "
        "Kenji will tell me not to drink from it, and I'll ignore him.",
        "Green, you say, and moving like eyes.\n\nWell, I've drunk worse. At home in Kupuvate the water was clean and the "
        "milk wasn't, and we drank the milk anyway because the cow was all we had. I'll boil it twice.",
        zone=DW))
    A(Q("dw_spiders_in_the_root_cellar", "Spiders in the Root Cellar", HANNA, 56, 56, "Cellarer's",
        "Baba Hanna keeps her potatoes in a root cellar under her lean-to, and the Deadwind Widows from the wood "
        "to the north-east have started nesting in it. She went down with a lamp this morning and came back up "
        "very quickly.",
        [k("Deadwind Widow", 10, DW)],
        "They come from the Widows' Wood, in the north-east. Kill the Deadwind Widows where they breed and they'll "
        "stop coming to me. I'm not afraid of spiders, but these glow.",
        "I went down with the lamp again and there was nothing but potatoes.\n\nBack home in the Zone the wolves came "
        "back, and the horses, and the elk. Everything came back once the people left. Here it comes back wrong.",
        zone=DW))
    A(Q("dw_the_dogs", "Taras's Dogs", HANNA, 56, 57, "Dogwatch",
        "Baba Hanna feeds a pack of strays that has followed Taras's dog Kashtan out of the Watch, and the Tumour "
        "Wolves have started taking them at night. She wants the wolves that hunt round her homestead gone.\n\n"
        "In Chernobyl the dogs stayed when the people left, and the old women fed them.",
        [k("Tumour Wolf", 8, DW)],
        "Every Tumour Wolf in these trees circles my place at dusk. Kill them and come and tell me, and you can "
        "have soup. The dogs won't share theirs.",
        "The strays slept by my fire last night, all six. Kashtan came out to check on them in the morning, as "
        "proud as a sergeant.\n\nWhen they made us leave, they shot the dogs, because the dogs carried the dust. "
        "I hid two in my sister's cellar. They lived to be very old.",
        zone=DW))

    # ======================================================================================= 3. GROSH'GOK
    A(Q("dw_the_ogre_at_the_ravine", "The Ogre at the Ravine", HARROW, 56, 56, "Parley",
        "An ogre came to the gate of Ariden's Watch three nights ago, alone and unarmed, and asked for help in a "
        "child's voice. Deathguard Harrow sent him away with a bone token and a promise.\n\nHis name is Grull, and "
        "he's waiting on the ravine road outside Grosh'gok Compound.",
        [deliver("dw_q_parley_token", "Bring Harrow's token to Grull on the ravine road")],
        "West from Deadman's Crossing, up Deadwind Ravine. He'll be outside the compound's gate. Show him the "
        "token, so he knows I kept my word.",
        "The dead man kept his promise. The little one in me said he would, and the big one said he wouldn't.\n\n"
        "My name is Grull. I was the chief's son once, and then the light came, and now I'm the chief's son and the "
        "chief's son when he was small, both in this skin.",
        turn_in_npc_id=GRULL, zone=DW,
        grant_items=carry("dw_q_parley_token", "Harrow's Bone Token", "A knucklebone carved with the Watch's mark, "
                          "a pyre with a line through it.")))
    A(Q("dw_put_them_down_kindly", "Put Them Down Kindly", GRULL, 56, 56, "Kindly",
        "The ogres of Grosh'gok Compound survived the tear, and Grull says that was worse than dying. They've "
        "swollen and fused, and the ones who still think are frightened all the time.\n\nHe wants his clan put "
        "down, kindly, so they can stop being frightened.",
        [k("Grosh'gok Brute", 8, DW), k("Grosh'gok Two-Face", 6, DW)],
        "The Grosh'gok Brutes and the Grosh'gok Two-Faces hold the ravine and the yard. Hit them hard, so it's "
        "quick. They were my uncles and my cousins, and they used to carry me on their shoulders.",
        "It's quieter in the ravine. I can hear the wind again.\n\nThe little one in me cried the whole time. The "
        "big one held him, the way my father used to hold me.",
        requires_quests=["dw_the_ogre_at_the_ravine"], nxt="dw_the_totem_in_the_bones", zone=DW))
    A(Q("dw_the_totem_in_the_bones", "The Totem in the Bones", GRULL, 57, 57, "Totemic",
        "Grosh'gok's clan totem had the handprint of every ogre born in the compound painted on it, and the "
        "Grosh'gok Sore-Shamans broke it apart for their fires when the light came.\n\nGrull wants the pieces "
        "back. His own handprint is on it, when he was very small.",
        [fetch("dw_q_totem_piece", 5)],
        "The Grosh'gok Sore-Shamans carry the pieces in their bags, in the yard past the gate. Bring me every "
        "piece you find.",
        "That small handprint's mine.\n\nI'll stand it up again at the gate when it's over, so whatever comes "
        "after us knows somebody lived here and was happy once.",
        nxt="dw_the_chained_ones", zone=DW))
    A(Q("dw_the_chained_ones", "The Chained Ones", GRULL, 57, 57, "Chainbreaker",
        "Grosh'gok kept beasts for war and for the pot, and the Chained Maulers were the worst of them even before "
        "the light came. Now they've fused with their own chains, and they'd tear the walls down if they could "
        "get loose.\n\nGrull doesn't want them loose when he goes for the chief.",
        [k("Chained Mauler", 8, DW)],
        "The Chained Maulers are staked in the ravine and round the yard. Kill them where they stand. When I go "
        "for my father, I don't want anything at my back.",
        "So now there's only him.\n\nHe's sitting in the middle of the compound, and he's waiting for me. He "
        "always knew I'd come.",
        nxt="dw_mograk", zone=DW))
    A(Q("dw_mograk", "Mog'grak the Twice-Born", GRULL, 57, 57, "Twice-Born",
        "Mog'grak was Grosh'gok's chief, and he's Grull's father. When the light came it fused him with the boy "
        "he used to be, and the boy is the one who hurts people now.\n\nGrull can't fight his own father. He's "
        "asked you to do it for him.",
        [boss("Mog'grak the Twice-Born", DW)],
        "He's somewhere in Grosh'gok Compound. You'll know him, because there are two of him. Don't listen to "
        "the small one. He was always the cruel one.",
        "It's done, then.\n\nThe little one in me is glad. The big one isn't sure yet. I think he'll be glad "
        "too, once he's finished being sad.",
        requires_quests=["dw_the_chained_ones"], zone=DW))

    # ======================================================================================= 4. THE WIDOWS' NEST
    A(Q("dw_silk_for_the_beds", "Silk for the Beds", SELA, 57, 57, "Silken",
        "Innkeeper Sela Crowe wants silk from the inside of the Widows' Nest, where the glow never reached. It's "
        "the only thing in the pass clean enough to sleep under, and the living at the Watch don't sleep well as "
        "it is.",
        [fetch("dw_q_widow_silk", 6)],
        "The Widows' Nest is in the crag at the top of the Widows' Wood, north-east of the crossing. The Funnel "
        "Widows spin the clean silk deep in the funnel. Bring me what you can.",
        "That's a whole bed's worth. I'll give it to Dr. Seitkali's patients first.\n\nI don't sleep myself, you "
        "know. I used to love it. I keep the beds the way I'd want one kept."))
    A(Q("dw_the_last_egg", "The Last Egg", MORWEN, 58, 58, "Egg-Bearer's",
        "The Silk Mother is a widow queen who has grown into her own cocoon at the bottom of the Widows' Nest, and "
        "her eggs glow. Morwen Ashgrave wants the last of them alive, from the brood chamber itself.\n\nHalyna and "
        "Dr. Seitkali want the brood burned. Only one of them can have it.",
        [boss("The Silk Mother", WN)],
        "The brood is at the top of the Throat, past the retreat holes. Kill the Silk Mother and bring me the egg "
        "she's sitting on, warm. If the Seep can grow a brood like that, it can grow a hand back.",
        "Warm, and it's moving. Thank you.\n\nAigerim will be angry, and she's right to be. I'll keep it under "
        "glass, and I'll burn it myself if it so much as cracks.",
        excludes_quests=["dw_burn_the_brood"]))
    A(Q("dw_burn_the_brood", "Burn the Brood", AIGERIM, 58, 58, "Broodburner's",
        "The Silk Mother has grown into her own cocoon at the bottom of the Widows' Nest, and every egg she lays "
        "carries the Seep out into the pass. Dr. Seitkali wants her killed and the brood burned.\n\nMorwen "
        "Ashgrave wants the last egg alive for her studies. Only one of them can have it.",
        [boss("The Silk Mother", WN)],
        "The brood is at the top of the Throat, past the retreat holes. Kill the Silk Mother and burn everything "
        "she's sitting on. Morwen will argue, and I don't care.",
        "All of it? Then that's one brood that won't hatch.\n\nMorwen thinks I'm afraid of what she might learn. I'm afraid of what I've already "
        "learned. In Semey they kept studying us for forty years, and none of the studies made anyone well.",
        excludes_quests=["dw_the_last_egg"]))

    # ======================================================================================= 5. BROKEN TIME
    A(Q("dw_a_dosimeter_for_time", "A Dosimeter for Time", KENJI, 57, 57, "Timekeeper's",
        "Kenji Watanabe has built a second dosimeter, one that measures time instead of the fallout. It has a "
        "pendulum inside it, and in some parts of the east the pendulum stops in the middle of a swing.\n\nHe wants "
        "readings from three of the stopped places, and he wants to know whether they're getting bigger.",
        [explore(*STOPPED_WATER, "Take a reading where the river stopped in the Sleeping Gorge", DE),
         explore(*STOPPED_PLACES, "Take a reading under the elder tree in the Stopped Places", DE),
         explore(*HANGING_SLIDE, "Take a reading under the Hanging Slide", DE)],
        "East over the ford, down the gorge and up the ramp on the far side. Watch the pendulum, not the "
        "scenery. If it stops while you're holding it, step back until it starts again.",
        "They're growing, all three, about a hand's width every day.\n\nAt Fukushima we drew circles on the map, "
        "twenty kilometres, thirty, and told people which side of the line to live on. Here the circles move. I "
        "don't know where to draw them.",
        requires_quests=["dw_readings_in_the_dead_forest"]))
    A(Q("dw_flicker_hounds", "Flicker Hounds", VESSA, 56, 56, "Flickering",
        "Deathstalker Vessa Morrow watches the middle of the pass for the Dark Lady, and the Flicker Hounds hunt "
        "her scouts across the Ashen Rise. They're never quite where you see them, because a moment of them is "
        "always a little ahead.",
        [k("Flicker Hound", 8, DE)],
        "The Flicker Hounds run the open ground between the gorge and the rupture. Aim where they're about to be. "
        "It takes a while to learn.",
        "You learned quickly. My first scout lost an arm finding out.\n\nI've watched them for a month. They "
        "don't eat what they kill. They only want the moment it dies, and then they're off after the next one.",
        zone=DE))
    A(Q("dw_three_ages_of_a_wolf", "Three Ages of a Wolf", VESSA, 57, 57, "Three-Age",
        "The Three-Age Wolves of the Ashen Rise have three heads, and Vessa Morrow says they're the same wolf at "
        "three ages: a pup, a grown hunter and an old grey. All three heads are hungry.",
        [k("Three-Age Wolf", 8, DE)],
        "Each Three-Age Wolf hunts the open ground and the slopes under the Hanging Slide. Go for the old head "
        "first. It's the one that remembers how to fight.",
        "You've thinned them. There's one I'd have you look for, though.\n\nThe pack had a leader before the "
        "tear, an old wolf the hunters in Duskwood used to talk about. He's still out there, and he has all three "
        "of his ages at once.",
        nxt="dw_old_three_heads", zone=DE))
    A(Q("dw_old_three_heads", "Old Three-Heads", VESSA, 58, 58, "Three-Headed",
        "Old Three-Heads led the Deadwind pack for twenty years, and when the tear opened it gave him back every "
        "age he'd ever been. He hunts the Stopped Places with a pup's head, a hunter's and an old wolf's on one "
        "body.",
        [boss("Old Three-Heads", DE)],
        "He keeps to the Stopped Places, round the elder tree. The pup's head will try to play with you. Don't "
        "let it.",
        "The old head looked at me before it died. I think it was grateful.\n\nI was a girl in Brill once. I'd "
        "hate to be every age at once, all of them hungry.",
        zone=DE))
    A(Q("dw_the_crow_king", "The Crow King", VESSA, 58, 58, "Crowned",
        "Every Many-Eyed Crow in Deadwind flies to the Drowned Hollow in the end, and Vessa Morrow has seen why. "
        "Something there has gathered the crows into itself until it's one bird made of hundreds.\n\nThe Forsaken "
        "call it the Crow King, and it sees everything the crows see.",
        [boss("The Crow King", DE)],
        "The Crow King circles the Drowned Hollow, over the mere and the cave mouth. Take it down and the crows "
        "will scatter. They won't remember what they were looking for.",
        "The crows are scattering in every direction now.\n\nWhatever it was watching for, it was watching the "
        "west. It was watching your camp.",
        zone=DE))
    A(Q("dw_the_onlookers", "The Onlookers", ECHO, 56, 56, "Onlooker's",
        "There's a liquidator's echo on the broken bridge over the Sleeping Gorge, stuck in the middle of a "
        "stride, and he can only get a few words out each time the moment loops. The Bridge Onlookers crowd round "
        "him, and every time they touch him he loses a word.\n\nThe Forsaken say the onlookers came to the bridge "
        "to watch the glow the night the tear opened, and stayed.",
        [k("Bridge Onlooker", 8, DE)],
        "...the bridge...too many of them...they watched it open and they won't stop watching. Get them away "
        "from me. I'm trying to remember something.",
        "...that's better, I can hear myself again.\n\nThere was a bridge at home where people went to watch the reactor "
        "burn. They brought their children to see the colours. Halya, I told them to go home. Halya, where are you...",
        zone=DE))
    A(Q("dw_tell_halya", "Tell Halya", ECHO, 57, 57, "Messenger's",
        "With the onlookers gone, the Bridge Echo can say more of what he's been trying to say. He keeps asking "
        "for Halya, and he keeps saying the readings were wrong.\n\nHe's wearing a liquidator's coat with a name "
        "stitched inside the collar: Mykola Bondar.",
        [deliver("dw_q_bridge_notes", "Bring your notes from the bridge to Halyna Bondar in Ariden's Watch")],
        "...tell Halya the readings were wrong...tell her I'm sorry...tell her it's not a hole, it's...it's...",
        "That's Mykola, my little brother. He came through with me from Slavutych.\n\nHe went down into the tear three months ago with Kenji's "
        "dosimeter and a rope, and he never came back up the rope. I wrote his name on the board myself, and "
        "tonight I'm going to take it down again. You're telling me he's standing on a bridge, talking.",
        turn_in_npc_id=HALYNA, requires_quests=["dw_the_onlookers"], zone=DE,
        grant_items=carry("dw_q_bridge_notes", "Notes from the Bridge", "Everything the echo said, written down in "
                          "the order he said it. Most of it is the same six words.")))
    A(Q("dw_the_readings_were_wrong", "The Readings Were Wrong", ECHO, 57, 57, "Readings",
        "Mykola's echo keeps saying the readings were wrong, and now he's pointing down into the Sleeping Gorge, "
        "at the stretch where the river stopped. He wants someone to stand in it.",
        [explore(*STOPPED_WATER, "Stand in the stopped river on the floor of the Sleeping Gorge", DE, radius=4)],
        "...down there...stand in the water that doesn't move...look which way it's leaning...",
        "...it leans toward the wheel. It's not flowing, it's being pulled.\n\nI told them. A hole doesn't pull. "
        "Halya, a hole doesn't pull...",
        requires_quests=["dw_tell_halya"], zone=DE))
    A(Q("dw_its_a_mouth", "It's a Mouth", ECHO, 58, 58, "Mouthward",
        "Mykola's echo is pointing at the wheel now, at the glow crater at its foot, and he's almost finished his "
        "sentence. He wants someone to go to the edge of the crater and look down.",
        [explore(*CRATER_LIP, "Look down into the glow crater at the foot of the wheel", DE, radius=4)],
        "...go to the edge...look down...you'll see what I saw...don't go in alone, I went in alone...",
        "...it's not a hole. It's a mouth.\n\nIt swallows things, and it keeps them, and it makes them again. "
        "It made me again. Tell Halya to come and let me go.",
        requires_quests=["dw_the_readings_were_wrong"], zone=DE))

    # ======================================================================================= 6. KARAZHAN'S SPILL
    A(Q("dw_this_evening", "This Evening", ARIDEN, 57, 57, "Evening's",
        "Ariden has watched Karazhan from his camp on the rim of the Sleeping Gorge for forty years. Every evening "
        "the light in the tower's high window goes out at the same moment.\n\nSince the tear, he's lived the same "
        "evening over and over, and he only half knows it. He'd like you to go to the tower's foot and look up.",
        [explore(*KARAZHAN_FOOT, "Look up at the high window from the foot of Karazhan", DE, radius=6)],
        "Down the gorge and east through the Vice, to the tower's gate. Look at the high window and tell me if "
        "the light's on. I can never tell from here if it's going out or coming on.",
        "Still on, you say. And it's always on when you look, and always going out when I look.\n\nI've been "
        "standing in this evening a long time, haven't I? I can feel it, like a coat I can't take off.",
        nxt="dw_pages_in_the_wind", zone=DE))
    A(Q("dw_pages_in_the_wind", "Pages in the Wind", ARIDEN, 57, 57, "Pagebound",
        "When Karazhan sealed, its library came apart, and the Book Flocks blew out of the windows. Every page is "
        "written by the tower's librarian, and Ariden has noticed something strange about the hand.\n\nHe wants "
        "the pages collected, before the wind takes them over the gorge.",
        [fetch("dw_q_archivist_page", 6)],
        "The Book Flocks drift round Karazhan and the Stopped Places. Catch the pages, and bring them here to "
        "me. I've read three already, and I can't stop thinking about them.",
        "Look at the hands. A boy's, a young man's, a grown man's, an old man's, all nine of them on one page, all "
        "the same person.\n\nAnd this one is about the night the tear opened. He wrote it before it happened. "
        "He's down there, in the wound. He's been writing it all down.",
        nxt="dw_the_master_isnt_dining", zone=DE))
    A(Q("dw_the_master_isnt_dining", "The Master Isn't Dining", ARIDEN, 58, 58, "Servant's",
        "Karazhan's servants wandered out before the tower sealed, and they're still serving a dinner nobody "
        "came to. The Spectral Servants carry cold trays across the Vice, and the Ballroom Phantoms dance with "
        "anyone they catch.\n\nAriden says they took his wife's dance the year the tower went dark.",
        [k("Spectral Servant", 8, DE), k("Ballroom Phantom", 6, DE)],
        "The Spectral Servants and the Ballroom Phantoms gather at Karazhan's foot, round the old stables. Let "
        "them rest. Dinner's been over for a very long time.",
        "It's quiet at the tower. The music's stopped, for the first time in years.\n\nMarta danced with one of "
        "them the night the light went out, and she didn't come home. I've been waiting for the end of that "
        "evening ever since. I think that's why it never ends.",
        nxt="dw_let_the_evening_end", zone=DE))
    A(Q("dw_let_the_evening_end", "Let the Evening End", ARIDEN, 58, 58, "Eventide",
        "There's a doorway in the Stopped Places that stands on its own, with no wall round it, and Ariden says "
        "his evening comes in through it every time it starts again.\n\nHe wants someone to walk through it from "
        "the other side, and let the evening finish.",
        [explore(*TIME_DOOR, "Walk through the standing doorway in the Stopped Places", DE, radius=3)],
        "It's on the far side of the elder tree. Walk through it backwards, the way the evening comes in. I don't "
        "know what you'll see. I hope it's a morning.",
        "The light in the window went out, and then it got dark, and then it got light again.\n\nI'd forgotten "
        "that's what happens after an evening. Thank you. I think I'll sleep now. I think I'll sleep a long time.",
        zone=DE))

    # ======================================================================================= 7. THE DROWNED SEEP
    A(Q("dw_whats_in_the_water", "What's in the Water", SELA, 57, 57, "Drainwater",
        "The fallout pools in the Drowned Hollow and drains down through the hill into a cave the Forsaken call "
        "the Drowned Seep, and Innkeeper Sela Crowe has a theory. Every time the leeches in the Seep breed, the "
        "camp's well goes bad a week later.",
        [k("Seep Leech", 8, DS)],
        "The Drowned Seep's in the hill above the mere in the Drowned Hollow, in the south-west of Deadwind East. "
        "The Seep Leeches cling all along the channel. Clear them and we'll see if I'm right.",
        "The well's sweet this morning. I was right, then.\n\nDon't tell Harrow. He'll want to take the credit, "
        "and I'll have to let him, because he's my brother."))
    A(Q("dw_the_drowned_thing", "The Drowned Thing", LISBETH, 58, 58, "Sumpdiver",
        "At the bottom of the Drowned Seep is the sump, where everything the drain carries ends up, and something "
        "has grown in it out of mud, roots and drowned animals. Lisbeth Vane wants it dead before the Royal "
        "Apothecary Society hears about it and wants it alive.",
        [boss("The Drowned Thing", DS)],
        "Follow the channel down through the oxbows to the sump. The Drowned Thing pulls people under, so stay "
        "out of the water. Kill it, and I'll write that it was already dead when you found it.",
        "That's one thing the Society won't get to keep in a tank.\n\nI've started writing two reports. "
        "One is for the Undercity, and the other is true. I haven't decided which one to send."))

    # ======================================================================================= 8. THE WHEEL
    A(Q("dw_slag_for_the_spire", "Slag for the Spire", RINE, 57, 57, "Spiremaker's",
        "Rine Lajuon is raising a containment spire at the edge of the rupture, Kenji's design and Morwen's runes. "
        "The base needs weight, and the heaviest thing in the pass is the slag the Gorge Slagcrawlers carry.",
        [fetch("dw_q_slag_ore", 8)],
        "The Gorge Slagcrawlers crawl the floor of the Sleeping Gorge. Bring me their slag and I'll pour the "
        "footings.",
        "That's a footing. Heavy as sin.\n\nOn Rongelap the ash came down like snow in 1954, and the children "
        "played in it. They moved us off and back and off again. I build things that keep people away from "
        "places, and I've never once built something to keep a place away from people."))
    A(Q("dw_the_four_chains", "The Four Chains", RINE, 58, 58, "Chainwarden's",
        "The wheel's gondolas hang on chains over the glow crater, and Morwen's runes have to be cut into the "
        "chains themselves for the spire to hold. Rine Lajuon has the runes on wax tablets.\n\nShe needs someone "
        "to stand under the wheel on both sides and press them on.",
        [explore(*WHEEL_WEST, "Press the runes onto the chains on the west side of the wheel", DE, radius=4),
         explore(*WHEEL_EAST, "Press the runes onto the chains on the east side of the wheel", DE, radius=4)],
        "The wheel's in the rupture, east of the Stopped Places. Press the tablets flat against the chains, hold "
        "them for a slow count of ten, and don't look up at the gondolas.",
        "Both sides took. I felt the spire's footings settle from here.\n\nDid you look up? Everybody looks up. "
        "There's never anyone in them. There never was, Halyna says, not even at home."))
    A(Q("dw_what_comes_up", "What Comes Up", RINE, 58, 58, "Ruptureguard",
        "Every time the spire grows, the rupture answers it. Fused Masses heave themselves up out of the crater, "
        "and the Many-Armed Things reach for the scaffolding.\n\nRine Lajuon's crew can't work with them at "
        "their backs.",
        [k("Fused Mass", 8, DE), k("Many-Armed Thing", 6, DE)],
        "The Fused Masses and the Many-Armed Things come up all round the rupture. Keep them off the spire. Kill "
        "the Many-Armed Things first, they're the ones that pull my crew off the ladders.",
        "The crew's back on the scaffold, and nobody's been pulled off it today.\n\nWe'll top it out tonight. "
        "Come and watch, if you like. You've earned it.",
        nxt="dw_raise_the_spire"))
    A(Q("dw_raise_the_spire", "Raise the Spire", RINE, 58, 58, "Containment",
        "The containment spire is finished, and Rine Lajuon wants someone who helped build it standing at its foot "
        "when it lights. Kenji will be there with his dosimeters, and Morwen with her runes.\n\nIf it works, the "
        "glow from the crater won't spread past it.",
        [explore(*SPIRE_BASE, "Stand at the foot of the containment spire when it lights", DE, radius=4)],
        "The spire's on the west edge of the rupture. Stand at its foot and keep your eyes on Kenji's needle. If "
        "it drops, we've done it.",
        "It dropped by half, and it's holding there.\n\nIt won't close the tear. At Chernobyl they poured a sarcophagus "
        "over the reactor in six months, and it leaked for thirty years, and it still bought everyone thirty years. "
        "That's what a liquidator does. We buy time.",
        requires_quests=["dw_slag_for_the_spire", "dw_the_four_chains"]))
    A(Q("dw_the_craters_edge", "The Crater's Edge", LUIZ, 58, 58, "Craterside",
        "Luiz Ferreira wants to salvage what's left of the camp the liquidators first built at the edge of the "
        "rupture, before they pulled back to Ariden's Watch. The Bloated Walkers wander through it, and when "
        "they burst, the seep goes everywhere.",
        [k("Bloated Walker", 8, DE)],
        "The Bloated Walkers shamble round the rupture. Kill them from a distance if you can, and you'll want to "
        "stand upwind when they go.",
        "There's good iron in that old camp, and some of our first tools.\n\nThe Bloated Walkers were Forsaken "
        "once, the first ones who went to the crater to help. That's what Harrow told me. He didn't tell me he "
        "knew their names."))

    # ======================================================================================= 9. THE EXCLUSION ZONE
    A(Q("dw_gristlemaw", "Gristlemaw", HARROW, 57, 57, "Gristlebane",
        "Grull says some of Grosh'gok's ogres walked into the crater the night the tear opened, and the wound "
        "made them into one body. The liquidators call it Gristlemaw. It holds the crater floor at the bottom of "
        "the Exclusion Zone's rim.\n\nGrull asked Deathguard Harrow to send someone.",
        [boss("Gristlemaw", EZ)],
        "The Exclusion Zone's door is in the glow crater at the foot of the wheel. Gristlemaw's on the crater "
        "floor, right where you climb down. Take friends, and don't let it pull you into the heap.",
        "Grull will want to know. I'll tell him myself.\n\nHe asked me once whether the dead remember being "
        "alive. I told him I remember all of it, and that it doesn't help.",
        requires_quests=["dw_mograk"]))
    A(Q("dw_broodmother_vexis", "Broodmother Vexis", MORWEN, 58, 58, "Broodbane",
        "The Silk Mother wasn't the first widow queen in Deadwind. Broodmother Vexis went down into the tear a "
        "month before the camp was built, and the liquidators found her in the rim's west chamber, fused with her "
        "own clutch.\n\nMorwen Ashgrave wants her heart, and she's promised Dr. Seitkali she'll burn the rest.",
        [boss("Broodmother Vexis", EZ)],
        "Vexis is in the Brood, the west chamber, round the rim from the crater floor. Bring me her heart, sealed. "
        "Aigerim's going to watch me burn the rest.",
        "Thank you. This is the oldest brood the Seep ever grew.\n\nAigerim stood beside me while I burned the "
        "body, the whole time, and neither of us said a word. I think that's the closest we've come to agreeing "
        "on anything."))
    A(Q("dw_the_glow_eater", "The Glow-Eater", AIGERIM, 58, 58, "Gloweater",
        "There are two pools of the seep in the rim's north chamber, and the liquidators call them the Bubbler "
        "Pools. Something lives between them that eats the seep and grows on it, and Dr. Seitkali calls it the "
        "Glow-Eater.\n\nKenji's readings say it's the reason the pulses from the wheel have been getting stronger.",
        [boss("The Glow-Eater", EZ)],
        "The Bubbler Pools are the north chamber, round the rim past the Brood. The Glow-Eater gets stronger the "
        "longer it feeds, so don't give it time.",
        "Halyna's father knew one of the men who drained the bubbler pools under the reactor in 1986. Three of "
        "them went into the flooded basement in the dark to open the valves, so the core couldn't fall into the "
        "water.\n\nShe named those pools for them. I think they'd have liked you."))
    A(Q("dw_archivist_nine", "Archivist Nine", KENJI, 59, 59, "Archivist's",
        "Ariden's pages were written by Karazhan's librarian at nine different ages, and Kenji has worked out "
        "where he went. The rim's east chamber is shelved with black glass, every moment the tear has kept is "
        "filed on it, and the librarian is still writing.\n\nThe liquidators call him Archivist Nine. Kenji wants "
        "his first page, the one about the night the tear opened.",
        [boss("Archivist Nine", EZ)],
        "The Stacks are the east chamber, round the rim past the Bubbler Pools. He'll read you your own death "
        "while you fight him, Ariden says. Don't let him finish the sentence.",
        "The first page. He saw the leylines bunch under the tower, and he saw them tear, and he wrote down that "
        "it was beautiful.\n\nAt Fukushima the sea wall was built for a wave of five metres, and the wave was "
        "fourteen. Somebody always writes down that it's fine.",
        requires_quests=["dw_let_the_evening_end"]))
    A(Q("dw_let_him_go", "Let Him Go", HALYNA, 59, 59, "Mykola's",
        "The spoke that runs from the Stacks to the heart of the Exclusion Zone is full of stopped time, and the "
        "liquidators work it in ninety-second shifts, like the men who cleared the roof at Chernobyl by hand. At the "
        "middle of it stands a figure frozen in the middle of a scream.\n\nThe Stopped Man is Mykola Bondar, and "
        "Halyna has asked you to let him go.",
        [boss("The Stopped Man", EZ)],
        "The Ninety Seconds is the spoke east of the heart, behind the Stacks. He'll fight you, because the wound "
        "made him again and it wants to keep him. Don't hesitate when you see his face, because he wouldn't want you to.",
        "Thank you.\n\nWhen I was small he used to hide under the kitchen table, under our father's dosimeter, and "
        "I'd pretend I couldn't find him. He'd stay there for hours. I'll put his name back on the board in the "
        "morning, and this time it'll stay there.",
        requires_quests=["dw_its_a_mouth", "dw_raise_the_spire"]))
    A(Q("dw_the_elephants_foot", "The Elephant's Foot", KENJI, 60, 60, "Fallout",
        "At the hub of the Exclusion Zone is the knot that keeps every copy the wound makes: flesh, black glass "
        "and stopped light, fused into one mass. Kenji gave it the name the first time he saw it.\n\nUnder "
        "Chernobyl's reactor, the core melted through the floor and set in the basement as a lump of fuel, sand "
        "and concrete. They called it the Elephant's Foot, and five minutes beside it would kill you.",
        [boss("The Wound's Heart", EZ)],
        "Cross the bridge at the end of the Ninety Seconds onto the island in the middle. The Wound's Heart is "
        "waiting there. Killing it won't close the tear, but it'll stop it remembering, and then what dies in "
        "Deadwind can stay dead.",
        "The needles all fell at once. Every dosimeter in the camp.\n\nThe tear's still open, and it'll be open "
        "when I'm dead. But it's stopped making things, and nothing it kept is coming back. For a liquidator, "
        "that's what winning looks like.",
        requires_quests=["dw_let_him_go"]))
    A(Q("dw_the_volunteers_kits", "The Volunteers' Kits", LUIZ, 59, 59, "Volunteer's",
        "Liquidators went down into the Exclusion Zone before the camp knew what was down there, and some of them "
        "are still there, stopped or aged to dust where they stood. Luiz Ferreira wants their kits back.\n\nEvery "
        "kit has a name stitched inside the flap.",
        [fetch("dw_q_liquidator_kit", 5)],
        "The Stopped Volunteers and the Aged Volunteers are along the Ninety Seconds and round the heart. Bring "
        "me every kit you find, masks and all. The families can't have the bodies, but they can have these.",
        "There are five names here. Kenji knew two of them, and Halyna knew all five.\n\nWe can't send them home. There's no "
        "post to where we came from. But the board will have them, and somebody will read it."))
    A(Q("dw_deep_samples", "Deep Samples", LISBETH, 59, 59, "Deepwater",
        "Lisbeth Vane wants a sample from the very bottom of the Bubbler Pools, before the Wound's Heart dies and "
        "the seep changes. She's decided which report she's sending, and she needs the samples to prove it.",
        [fetch("dw_q_bubbler_sample", 5)],
        "The Bubbler Oozes live in the pools in the Exclusion Zone's north chamber. Seal each flask before you "
        "lift it out, and don't spill a drop on your boots.",
        "Thank you. These go to the Undercity with the true report.\n\nMaster Ashgrave's arm, and what the Seep "
        "does to the living, and every name on the board. If the Society wants to use it as a weapon, they'll "
        "have to read all of that first."))

    # ======================================================================================= 10. THE BOARD OF NAMES
    A(Q("dw_the_board_of_names", "The Board of Names", HALYNA, 60, 60, "Board's",
        "The Wound's Heart is dead, and nothing in Deadwind is getting up again. Halyna Bondar has put Mykola's "
        "name back on the board by the pyre, a little way under Tomas's.\n\nShe's asked you to read the names out loud at the "
        "pyre, all of them, the way they read them at home every April.",
        [explore(*NAMES_BOARD, "Read every name on the board of names aloud", AW, radius=4)],
        "Read them slowly. Everyone in the camp will be there, and the Forsaken too. Start at the top and don't "
        "stop until you get to Mykola.",
        "Thank you.\n\nMy father never talked about Chernobyl, not once in his whole life. He kept the dosimeter on "
        "the shelf so he'd remember, and he kept quiet so we wouldn't have to. I'm going to talk about this place "
        "every day until I die.",
        requires_quests=["dw_the_elephants_foot"]))
    A(Q("dw_let_it_go_out", "Let It Go Out", TOBIAH, 60, 60, "Embers",
        "Old Tobiah's pyre hasn't gone out once since Ariden's Watch was built, because anything that died in "
        "Deadwind got up again unless it was burned. Now nothing gets up.\n\nTobiah wants someone to stand with "
        "him while he lets it go out.",
        [explore(*PYRE, "Stand with Tobiah while the pyre goes out", AW, radius=4)],
        "Stand with me, that's all. I don't want to do it alone, and I don't want to do it with someone who'll "
        "make a speech.",
        "It's only embers now.\n\nI talked to every one of them while they burned, and I told them they "
        "were home. Now nothing in Deadwind needs burning twice. I think I'll sit here a while and let it get "
        "cold.",
        requires_quests=["dw_the_board_of_names"]))
    return out
