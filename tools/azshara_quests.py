"""
Azshara's quests: West, Central and East Azshara, Talrendis Landing, Timbermaw Hold, the two caves and the two
dungeons. Levels 52-60. Read by tools/build_azshara_quests.py, which holds them to the Stonetalon and Felwood rules
before anything is written. The plan is docs/azshara_quest_plan.md.

THE STORY IS BRAIDED (Kyle, 18 Nov 2026: "Braided, both ends").
  THE LANDING   the salvage feud. Orgrimmar's crews and the Sunreach Conclave's magisters share Talrendis Landing and
                the dig at Eldarath, and neither trusts the other with what comes up. A relic goes missing, each side
                blames the other, and Dr. Okafor, who works for both, finds the naga took it: they're digging too, from
                the sea side, because the relics are keys to Azshara's palace. It ends in the Drowned Palace.
  THE HOLD      the rot (build_hold, the second half of this file). It ends in the Rotroot Deeps.
  ELDARATH      where the two meet: the rot is Highborne magic gone bad, and the dig sits on its root.

Reputation goes by giver: the Conclave's magisters and the Stormwatch ranger pay the Sunreach Conclave, the orcs and
the transplants pay Orgrimmar, the Hold pays Timbermaw Hold (tools/build_azshara_quests.FACTION_BY_GIVER).

VOICE (Kyle): whole sentences the way a person says them, contractions, the useful thing first, no dashes, no counts
beside an objective word, every kill target named. Earth comes up about a quarter of the time, from the transplants.
"""
from tools.build_durotar_quests import kill, fetch  # noqa: F401

# ---- the maps (the key the game passes on a kill: the map's name lowercased, spaces to underscores, no apostrophes)
WA, CA, EA = "west_azshara", "central_azshara", "east_azshara"
TL, TH = "talrendis_landing", "timbermaw_hold"
HD, HG = "haldarr_den", "hetaeras_grotto"
RD, DP, DV = "the_rotroot_deeps", "the_drowned_palace", "the_drowned_palace:_the_queens_vault"
ORG, ST, TT, UC = "orgrimmar", "splintertree_post", "timbermaw_tunnel", "undercity"

# ---- the people
DURGASH, RUKKA, CAELIN, YSOLDE = "tl_overseer", "tl_salvage_boss", "tl_conclave_archivist", "tl_conclave_dig_magister"
OKAFOR, THRAG, ILANTHE, MAZKAR, SALEH = ("tl_archaeologist", "tl_farseer", "tl_gate_spellbreaker", "tl_gate_grunt",
                                         "tl_innkeeper")
AELIS = "tl_conclave_warder"
OKKAR, ZARGA, THESSALY = "az_valormok_grunt", "az_stormwatch_captain", "az_stormwatch_ranger"
TORGUN, GORADA, GROSK, MARWEN = "org_elder_2", "splintertree_commander", "tm_pathfinder", "uc_apothecary"
ASHGRYM = "durotar_burning_blade_warden"
# the Hold's (build_hold)
ELDER, UNGAR, LESSA, GROTHAR, ULMA = "tm_elder", "th_totemkeeper", "th_spring_keeper", "th_deep_warden", "th_deep_warden_b"
BENNIK, INGRID, HROLM, BURRFOOT = "th_carver", "th_volunteer", "th_gate_warden", "th_tunnel_warden"
GRASHAK, FENNA = "th_orc_envoy", "pt_th_herbs"

LANDING_GIVERS = {DURGASH, RUKKA, CAELIN, YSOLDE, OKAFOR, THRAG, ILANTHE, MAZKAR, SALEH, AELIS}
HOLD_GIVERS = {ELDER, UNGAR, LESSA, GROTHAR, ULMA, BENNIK, INGRID, HROLM, BURRFOOT, GRASHAK, FENNA}
HUB_GIVERS = LANDING_GIVERS | HOLD_GIVERS


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def explore(x, y, label, zone, radius=7):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius, label=label)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


#: creature -> [(item_id, name, description[, chance])], three in four unless a chance is given
FETCH_DROPS = {
    "Russet Boar": [("az_q_boar_haunch", "Russet Boar Haunch", "A heavy haunch of red-bristled boar. It'll feed a "
                                                               "table of orcs, or two of elves.")],
    "Cliff Hippogryph": [("az_q_hippogryph_plume", "Cliff Hippogryph Plume", "A long gold-and-russet flight feather, "
                                                                              "stiff as a quill.")],
    "Southridge Shorecrab": [("az_q_crab_meat", "Southridge Crab Meat", "Sweet white meat in a shell the size of a "
                                                                        "shield. It smells like the sea.")],
    "Eldarath Shade": [("az_q_highborne_keepsake", "Highborne Keepsake", "A small thing a Highborne carried: a comb, a "
                                                                         "ring, a cracked locket. The shade wanted it back.")],
    "Eldarath Construct": [("az_q_construct_core", "Construct Core", "A fist of violet crystal that hums when you hold "
                                                                     "it. It's still trying to give orders.")],
    "Mennar Mana Wyrm": [("az_q_wyrm_essence", "Mana Wyrm Essence", "A vial of something that glows blue and tries to "
                                                                    "climb the glass.")],
    "Stormbay Siren": [("az_q_siren_pearl", "Siren's Pearl", "A black pearl carved with a rune the naga use. Dr. "
                                                             "Okafor wants every one of them.")],
    "Bitter Reaches Raider": [("az_q_stolen_relic", "The Stolen Relic", "A Highborne key of gold and moonstone as long "
                                                                        "as your forearm, still sticky with the dig's "
                                                                        "clay.", 0.35)],
    "Promenade Noble": [("az_q_court_seal", "Court Seal", "A Highborne noble's seal of office in sea-green gold. The "
                                                          "Conclave can read the names on them.")],
}
#: monster-drop quest starters: creature -> [(item_id, name, description, chance)]
STARTER_DROPS = {
    "Bitter Reaches Wavecaller": [("az_q_naga_dig_map", "A Naga Dig Map", "A sharkskin map of the coast with digging "
                                   "marks along it. One of them is right under Eldarath, coming in from the sea.",
                                   0.12)],
}
STARTER_IDS = {"az_q_naga_dig_map": "az_the_sea_side_dig"}

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


def Q(qid, title, giver, lo, hi, prefix, desc, objs, accept, done, rewards=None, nxt=None, zone=TL, **engine):
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             _prefix=prefix, _rewards=rewards or R())
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def build_landing():
    out = []
    A = out.append

    # ============================================================================================ IN
    A(Q("az_the_north_gate", "The North Gate", ASHGRYM, 52, 52, "Northgate",
        "Bloodwarden Ashgrym has a sealed report from Elder Torgun for Overseer Durgash Stonejaw, who runs Orgrimmar's half of the dig at "
        "Talrendis Landing. The new gate out of the canyon north of the Valley of Honor opens onto Azshara.\n\nThe "
        "Warchief wants to know what the elves are pulling out of the ground, and he wants to know before they do.",
        [deliver("az_q_torgun_report", "Bring the report to Overseer Durgash Stonejaw in Talrendis Landing")],
        "Out the north gate and up through the forest. The Landing's on the point to the west. Don't let the elves "
        "see the seal, they'll want to read it.",
        "Torgun's seal, and the Warchief's questions underneath it. They're the same questions I've been asking "
        "for a month.\n\nWelcome to the Landing. Don't trust anything that comes out of the ground until it's been "
        "counted twice.",
        zone=ORG, turn_in_npc_id=DURGASH,
        grant_items=carry("az_q_torgun_report", "Torgun's Sealed Report", "A report sealed with Elder Torgun's mark. "
                                                                         "It's mostly questions.")))
    # ===================================================================================== THE LANDING
    # ---- Grunt Mazkar, at the gate
    A(Q("az_boar_for_the_mess", "Boar for the Mess", MAZKAR, 52, 52, "Messhall",
        "Grunt Mazkar says the mess is short of meat and the Provisioner won't cook elf food for orcs. The russet "
        "boars root all over the forest outside the gate.",
        [fetch("az_q_boar_haunch", 8)],
        "The boars are thick in the trees all round the Landing. Bring the haunches back here and Dana will do "
        "the rest. She's from somewhere called the North Sea and she can cook anything.",
        "That's a proper dinner. The elves will complain it's too much meat, and then they'll eat it anyway. Dana says back home on her rig the meat came frozen in boxes, so she's thrilled."))
    A(Q("az_wolves_on_the_road", "Wolves on the Road", MAZKAR, 52, 53, "Roadwatch",
        "Every Autumn Timber Wolf in the forest has taken to following the supply carts out of the Landing, and twice "
        "now they've had a driver.\n\nMazkar wants them taught to stay off the road. Half the drivers are newcomers who'd never seen a wolf before the Integration.",
        [k("Autumn Timber Wolf", 10, WA)],
        "Autumn Timber Wolves run the forest between here and the crossroads. Thin them out. They'll learn, or "
        "they'll stop needing to. The Autumn Timber Wolves are clever, but they aren't that clever.",
        "The carts got through clean this morning. You've done the drivers a favour they won't thank you for, "
        "because they'll never know."))

    # ---- Innkeeper Layla Saleh (her brother Mohammed is Azshara's recruit, by the inn door)
    A(Q("az_plumes_for_the_pillows", "Plumes for the Pillows", SALEH, 53, 53, "Featherbed",
        "Layla Saleh and her brother ran a guesthouse on the Red Sea before the Integration. She says the beds at the Landing are "
        "a disgrace, and the cliff hippogryphs drop the best feathers she's ever seen.",
        [fetch("az_q_hippogryph_plume", 8)],
        "The cliff hippogryphs nest up on the Ursolan heights, north of here. Bring me the plumes and I'll make "
        "pillows an elf can't complain about. Well, not much.",
        "These are beautiful. In Aqaba I had down from Turkey, and it wasn't this good.\n\nThe magisters will "
        "sleep better, and I'll get less complaining at breakfast."))
    A(Q("az_ghosts_in_my_dreams", "Ghosts in His Dreams", SALEH, 57, 57, "Dreamer",
        "Half the Landing dreams of the same street every night: a white marble boulevard running into the sea, "
        "with people in it who don't see you. Layla's brother Mohammed dreams it every night, and he thinks it's the Drowned "
        "Promenade on the coast.\n\nLayla wants someone to go and look, so she can tell her guests it's a real place. They came "
        "through three years ago, and she's learned to take her brother's dreams seriously since.",
        [explore(140, 108, "Walk the Drowned Promenade on the East Azshara coast", EA, radius=9)],
        "East, past Stormwatch and down to the shore. The Promenade's the marble road that runs into the sea. Tell "
        "me if there are people in it, and tell me if they see you.",
        "They saw you? Then they're not dreams, they're ghosts, and they're calling.\n\nI'll tell my guests to "
        "sleep with the lamps lit. It won't help, but it'll make them feel better."))

    # ---- Overseer Durgash Stonejaw
    A(Q("az_two_lists", "Two Lists", DURGASH, 53, 53, "Overseer",
        "Overseer Durgash keeps one list of everything that comes out of the dig at the Ruins of Eldarath, and "
        "Magister Brightspire keeps the other. They never match.\n\nDurgash wants someone with no side to walk the "
        "dig and see what's in the trenches before either of them counts it.",
        [explore(112, 144, "Walk the dig at the Ruins of Eldarath in Central Azshara", CA, radius=9)],
        "Eldarath's in Central Azshara, south of the lake, east of here. Walk the trenches, see what's lying in them, "
        "and come back and tell me before you tell the elves.",
        "Crates, columns, and a lot of stone with writing on it nobody can read. That's what I've got on my list "
        "too.\n\nSo either the elves are lying, or something's walking off before anyone counts it. Three years I've run digs for Orgrimmar, and this is the first one that frightens me.",
        nxt="az_the_road_to_eldarath"))
    A(Q("az_the_road_to_eldarath", "The Road to Eldarath", DURGASH, 53, 54, "Haulroad",
        "The carts from the dig come back light, and the drivers say it's satyrs. Haldarr's rogues come down out of "
        "their encampment and cut the ropes while the carts climb.\n\nDurgash wants the road cleared, and he wants "
        "the satyrs to know who cleared it. Half the drivers are newcomers from Earth, and they didn't sign on to fight satyrs.",
        [k("Haldarr Rogue", 10, WA)],
        "Haldarr Rogues come down from the encampment in the south-east of West Azshara. Go up there and make them "
        "regret every crate they've cut loose.",
        "The carts came back full yesterday. Full, and the count still doesn't match the elves'.\n\nSo it isn't "
        "the satyrs. Not only the satyrs."))
    A(Q("az_who_took_the_relic", "Who Took the Relic?", DURGASH, 56, 56, "Inquest",
        "The crews found a Highborne key in the trenches, gold and moonstone, as long as your arm. It was on both "
        "lists on Monday. On Tuesday it was on neither.\n\nDurgash thinks the elves have it. The elves think he "
        "sold it. Dr. Okafor works for both, and Durgash wants you to ask her what she saw.",
        [deliver("az_q_durgash_tally", "Bring Durgash's tally to Dr. Amara Okafor at the dig")],
        "Take my tally to Dr. Okafor. She's down in the dig, usually up to her knees in it. She's the only one "
        "here both sides will talk to.",
        "I saw it come up, and I saw it go into the crate. Then the crate went into the yard, and the next morning "
        "the crate was soaked through with seawater.\n\nNeither the orcs nor the elves took it. Something came up from the sea.",
        turn_in_npc_id=OKAFOR, nxt="az_the_relic_trail",
        grant_items=carry("az_q_durgash_tally", "Durgash's Tally", "Every crate from the last fortnight, counted twice "
                                                                   "and initialled.")))
    A(Q("az_the_overseers_report", "The Overseer's Report", DURGASH, 58, 58, "Warchief's",
        "With the relic back and the naga's dig on the map, Durgash has a report for Orgrimmar that he doesn't want "
        "to write. The relics are keys, the naga want them, and the palace they open is coming up out of the sea.\n\n"
        "He wants Elder Torgun to read it from someone who's seen it.",
        [deliver("az_q_durgash_report", "Bring Durgash's report to Elder Torgun in Orgrimmar")],
        "Take it to Elder Torgun in Orgrimmar, the north gate's quickest. Tell him what you've seen. He'll believe "
        "you before he believes me.",
        "A palace under the sea, and a queen the night elves say drowned ten thousand years ago. Durgash isn't one "
        "to make things up.\n\nThe Warchief will want it opened, and he'll want our people first through the door.",
        zone=TL, turn_in_npc_id=TORGUN, requires_quests=["az_the_sea_side_dig"],
        grant_items=carry("az_q_durgash_report", "Durgash's Report", "A thick report in Durgash's square hand. He "
                                                                     "pressed hard enough to tear the paper.")))
    A(Q("az_the_tidelord", "The Tidelord", MAZKAR, 59, 60, "Tidelord's",
        "Grunt Mazkar has orders from the Overseer. The naga in the Drowned Palace answer to Tidelord Vashj'ren, and his warriors are the ones who took the "
        "relic off our yard. He sits on a coral throne in the palace's flooded halls, with the sea all round him.\n\n"
        "Durgash wants the Warchief's answer delivered in person.",
        [boss("Tidelord Vashj'ren", DP)],
        "The palace's door is at the head of the Drowned Court, off the East Azshara shore. Get through the flooded "
        "halls to his throne and put him down. You'll want friends with you, a lot of them.",
        "The Tidelord's dead and the halls are ours. Orgrimmar will hear about this, and so will the elves, and "
        "they'll both pretend it was their idea.",
        requires_quests=["az_the_overseers_report"]))

    # ---- Salvage Boss Rukka Ironhide
    A(Q("az_shades_in_the_trenches", "Shades in the Trenches", RUKKA, 55, 55, "Trenchwork",
        "Rukka's crews won't work the deep trenches at Eldarath after dark, because the Highborne dead come up out "
        "of them looking for what was theirs.\n\nShe wants the Eldarath Shades put back down so the night shift "
        "can dig. Two of her diggers are from Earth, and they say back home the ghosts at least stayed in the stories.",
        [k("Eldarath Shade", 10, CA)],
        "The Eldarath Shades walk the ruins all round the dig, south of the lake in Central Azshara. They're dead already, so you won't feel bad. "
        "My crews will do the rest.",
        "The night shift dug three new trenches in one night. I haven't seen them work that hard since we left Durotar."))
    A(Q("az_crab_season", "Crab Season", SALEH, 54, 54, "Shellbreaker",
        "Layla promised the dig crews a crab boil after the big lift, and Dana Whitfield, who cooked on a North "
        "Sea rig before the Integration, says she knows how to do it properly. The shorecrabs on Southridge Beach are the size of shields.",
        [fetch("az_q_crab_meat", 8)],
        "Southridge Beach is the south coast of Central Azshara. Crack the Southridge Shorecrabs and bring the meat "
        "back here. Dana's got the pot on already, and I've promised everyone.",
        "Dana says back home in Scotland they'd charge a fortune for these. Here they just walk up the beach and try to cut "
        "your toes off."))
    A(Q("az_cores_for_the_crane", "Cores for the Crane", RUKKA, 56, 56, "Cranelift",
        "The Conclave's crane at the dig runs on arcane cores, and the elves won't spare theirs for orc lifts. "
        "Rukka has noticed the Eldarath Constructs have cores of their own.",
        [fetch("az_q_construct_core", 6)],
        "The Eldarath Constructs stomp round the ruins near the dig. Break them open and bring me their cores. The "
        "elves can't say no to a crane that runs on Highborne parts.",
        "The crane's running and the elves are furious. Best day I've had since we got here. Dr. Okafor says on Earth they'd put a crane like this in a museum.",
        nxt="az_the_lost_crew"))
    A(Q("az_the_lost_crew", "The Lost Crew", RUKKA, 56, 57, "Searchparty",
        "One of Rukka's crews went up the coast to Hetaera's Clutch to salvage a spire that washed up there, and "
        "they haven't come back. The naga have a beachhead on the Clutch.\n\nRukka wants her crew, or she wants to "
        "know.",
        [k("Stormbay Tidehunter", 8, CA)],
        "Hetaera's Clutch is the headland past the Bay of Storms, north-east Central Azshara. The Stormbay "
        "Tidehunters hold the beach. Break them, and look for my crew.",
        "Their nets and their tools, piled by the sea cave. The naga dragged them into the grotto.\n\nI'm not "
        "sending anyone else in there. I'm sending you.",
        nxt="az_hetaera"))
    A(Q("az_hetaera", "Hetaera", RUKKA, 57, 58, "Hydra-bane",
        "Rukka's crew went into Hetaera's Grotto under the Clutch and didn't come out. The naga keep a hydra down "
        "there, Hetaera, and they feed her.\n\nRukka wants the hydra dead before she feeds anyone else.",
        [boss("Hetaera", HG)],
        "The grotto's the sea cave in the crag on Hetaera's Clutch. Hetaera keeps to a deep pool off the second "
        "turn of the spiral. You'll want people with you, because a lot of heads means a lot of bites.",
        "So the hydra's dead, and that's good.\n\nI'll carve my crew's names on the crane. They lifted more than anyone, and they'd want it "
        "there."))

    # ---- Magister Caelin Brightspire (the Conclave's archivist)
    A(Q("az_keepsakes_of_the_highborne", "Keepsakes of the Highborne", CAELIN, 55, 55, "Archivist's",
        "Magister Brightspire says the Eldarath Shades are looking for things they lost: rings, combs, lockets. The "
        "Conclave wants them, because every one has a name on it, and the names are its history. The orcs call it robbing graves, and the newcomers on the crews call it archaeology.",
        [fetch("az_q_highborne_keepsake", 8)],
        "The Eldarath Shades walk the ruins round the dig. Take what they carry. I'll write down every name, and "
        "then the orcs will write them down too, and then we'll argue.",
        "This one belonged to a scribe. This one to a child.\n\nWe forget they were people. It's easier to dig "
        "them up when we forget."))
    A(Q("az_the_ravencrest_records", "The Ravencrest Records", ILANTHE, 54, 54, "Ravencrest",
        "The monument at Ravencrest in West Azshara has the names of Highborne lords cut into it, and the Conclave "
        "wants a rubbing. The Ravencrest Shades don't want anyone that close.",
        [k("Ravencrest Shade", 8, WA), explore(100, 104, "Take a rubbing of the Ravencrest Monument", WA)],
        "The monument's in the middle of West Azshara, east of the Landing. Clear the Ravencrest Shades round it "
        "and take the rubbing. Use the paper I gave you, not the cheap orc stuff.",
        "Lord Ravencrest's name, and the names of everyone who served him. One of them is a Sunreach.\n\nThe Grand "
        "Magister will want to see this."))
    A(Q("az_the_bound_magister", "The Bound Magister", CAELIN, 56, 56, "Unbinder's",
        "Haldarr's satyrs keep a Highborne magister bound in the far pocket of their den, and they've kept him there "
        "ten thousand years. The Conclave wants him freed.\n\nBrightspire knows what freeing him means. He's asking "
        "anyway.",
        [boss("The Bound Magister", HD)],
        "Haldarr Den is under the satyrs' encampment in the south-east of West Azshara. The Bound Magister's in the "
        "farthest pocket off the taproot. Free him gently, if you can. I don't think it'll be gentle.",
        "So he's gone, and that means he's free.\n\nTen thousand years in chains, and he fought you for the chains. I'll write "
        "that down too."))
    A(Q("az_the_chamberlains_ledger", "The Chamberlain's Ledger", CAELIN, 59, 59, "Ledgerkeeper's",
        "The Drowned Chamberlain keeps the palace's ledger in its flooded archive, ten thousand years of who owed "
        "the queen what. Brightspire says it's the most important book in the world.\n\nHe wants it, and the "
        "Chamberlain won't lend it.",
        [boss("The Drowned Chamberlain", DP)],
        "The archive's in the Drowned Palace's flooded halls, past the collapsed gallery. The Chamberlain keeps "
        "the ledger. Take it off him, and try not to get it any wetter than it is.",
        "Every debt the Highborne owed their queen. Every debt she owed the things under the sea.\n\nShe owed them a great "
        "deal, and I don't think they've forgotten."))

    # ---- Magistrix Ysolde Emberwind (the Conclave's dig magister)
    A(Q("az_the_font", "The Font", YSOLDE, 55, 55, "Leyfont",
        "The leylines under the coast meet at the Mennar Font on Lake Mennar, and Magistrix Emberwind says they've "
        "started to pull toward the sea. She wants someone to stand at the Font and tell her which way the water "
        "turns. The leylines have been restless since the Integration, but never like this.",
        [explore(76, 116, "Stand at the Mennar Font on Lake Mennar's shore", CA, radius=8)],
        "Lake Mennar's in the south-west of Central Azshara. The Font's on its north-east shore, ringed with "
        "crystal trees. Stand in it. You'll feel which way it pulls.",
        "Toward the sea, toward the Drowned Court. Exactly where I didn't want it to point.",
        nxt="az_wyrm_essence"))
    A(Q("az_wyrm_essence", "Wyrm Essence", YSOLDE, 55, 56, "Wyrmglass",
        "The mana wyrms at Lake Mennar drink straight from the Font, and Emberwind wants to know what they're "
        "drinking. Their essence holds a little of the leyline's pull.",
        [fetch("az_q_wyrm_essence", 8)],
        "The Mennar Mana Wyrms swarm round the Font and the lake. Bottle what's in them. It climbs the glass, so "
        "cork it fast.",
        "Every vial leans toward the sea. Even the essence wants to go home.",
        nxt="az_the_blues_who_guard"))
    A(Q("az_the_blues_who_guard", "The Blues Who Guard", YSOLDE, 56, 56, "Leyward",
        "The blue dragonflight guards the leylines at Lake Mennar, and the Azure Dragonspawn won't let the "
        "Conclave's tappers near the Font. They're not evil, Emberwind says, they're just in the way.",
        [k("Azure Dragonspawn", 8, CA)],
        "The Azure Dragonspawn stand guard all round Lake Mennar. Drive them off the Font. I'd rather talk, but "
        "they've stopped listening.",
        "They'll be back, and next time they'll bring the drake. Still, the tappers are in, and the readings are "
        "what I was afraid of.",
        nxt="az_azurewing"))
    A(Q("az_azurewing", "Azurewing", AELIS, 57, 57, "Azure",
        "The dragonspawn answer to a blue drake, Azurewing, who circles Lake Mennar. Spellwarder Aelis would rather "
        "not fight a dragon, but Azurewing has started burning the Conclave's tappers.",
        [boss("Azurewing", CA)],
        "Azurewing hunts over Lake Mennar. When it lands at the Font, be there. It breathes frost, so you'll want to dress warm.",
        "I'm sorry it came to that. The blues were right to guard the Font. They just didn't know what was "
        "pulling at it."))
    A(Q("az_magistrix_elaria", "Magistrix Elaria", AELIS, 60, 60, "Undying",
        "Under the Drowned Palace there's a vault the sea never reached, and in it a magistrix who never died. "
        "Magistrix Elaria the Undying keeps the cracked well at its heart, and it's her well the leylines are "
        "pulling toward.\n\nAelis keeps the Conclave's wards, and she wants the pull stopped.",
        [boss("Magistrix Elaria the Undying", DV)],
        "Down the flooded stair past the Tidelord's throne, into the Queen's Vault. Elaria's at the well in the "
        "Arcanum. She drinks from it to heal, so hit her hard and don't stop.",
        "The pull's eased, though it hasn't stopped.\n\nShe was my teacher's teacher's teacher, you know. A long way "
        "back. I'd have liked to ask her things.",
        requires_quests=["az_the_font"]))

    # ---- Dr. Amara Okafor (the transplant archaeologist)
    A(Q("az_pearls_with_runes", "Pearls with Runes", OKAFOR, 56, 56, "Fieldwork",
        "Dr. Okafor has found the same rune on half the naga's pearls and on the Highborne stones in the dig. She "
        "dug Iron Age sites in Nigeria for twenty years and she's never seen two peoples share a mark like this.",
        [fetch("az_q_siren_pearl", 8)],
        "The Stormbay Sirens on the Bay of Storms carry the pearls. Bring me as many as you can. Don't wear them, "
        "they sing.",
        "It's the same rune on all of them, and on the key that came out of the trench.\n\nThe naga aren't just "
        "raiding us. They're looking for the same thing we are. Back home in Lagos nobody would believe a word of it."))
    A(Q("az_the_relic_trail", "The Relic Trail", OKAFOR, 56, 57, "Seaward",
        "Seawater in the crate, and wet footprints across the yard that weren't orc or elf. Dr. Okafor followed them "
        "to the shore. The naga raiding the Bitter Reaches in East Azshara have been trading Highborne gold.\n\nShe "
        "thinks the relic went north with them.",
        [fetch("az_q_stolen_relic", 1)],
        "The Bitter Reaches is East Azshara's north coast, wrecks and a naga shrine. The Bitter Reaches Raiders "
        "carry what they steal. One of them has our key.",
        "There it is. Gold and moonstone, and the rune on the bow of it.\n\nI'll give it to both sides at once, in "
        "the middle of the yard, with everyone watching. On Earth I'd have called the police. Here I call you.",
        requires_quests=["az_who_took_the_relic"]))
    A(Q("az_the_sea_side_dig", "The Sea-Side Dig", "item:az_q_naga_dig_map", 58, 58, "Undersea",
        "The map shows the naga digging all along the coast, and one tunnel coming in under Eldarath from the sea. "
        "The marks end at the Temple of Zin-Malor on the southern headland.\n\nDr. Okafor will want this.",
        [explore(157, 166, "See what the naga are digging at the Temple of Zin-Malor", EA, radius=9)],
        "Someone at Talrendis Landing ought to see this map. Dr. Okafor's the one, before anyone takes sides.",
        "They're digging from the sea toward the same chamber we're digging toward from the land. A door, both "
        "sides of it.\n\nThe keys open the palace. Everyone wants in, and nobody's asked what's inside.",
        zone=EA, turn_in_npc_id=OKAFOR))
    A(Q("az_tide_priestess", "Tide-Priestess Sel'thira", OKAFOR, 57, 58, "Tidecaller's",
        "The naga's dig is run from Hetaera's Grotto by a sea witch, Tide-Priestess Sel'thira, who reads the runes "
        "better than anyone in the Landing. Dr. Okafor would rather talk to her. Sel'thira would rather drown "
        "people.",
        [boss("Tide-Priestess Sel'thira", HG)],
        "The grotto's under Hetaera's Clutch. Sel'thira keeps the drowned hall at the heart of the spiral. If she "
        "has notes, bring them. If she doesn't, bring her down.",
        "She had notes. In a language nobody alive reads, on sharkskin, with diagrams.\n\nI'm going to be up "
        "all night. I haven't stayed up this late since my thesis, back home."))
    A(Q("az_lady_ssiriss", "Lady Ssiriss", OKAFOR, 59, 59, "Siren-Queen's",
        "The naga's siren queen, Lady Ssiriss, holds the court inside the Drowned Palace's door, and every naga on "
        "this coast sings what she sings. Dr. Okafor says she's the one who wanted the keys.",
        [boss("Lady Ssiriss", DP)],
        "Through the Drowned Court's door and into the Siren's Court. Ssiriss sits on a coral dais in the pool, one "
        "fallen column out to her. Don't listen to her sing.",
        "She's quiet now, and the whole coast's quieter with her.\n\nFor the record, she had the other keys. The palace was always "
        "going to open. Now it's opening for us."))

    # ---- Farseer Thrag Windcaller
    A(Q("az_the_leylines_pull", "The Leylines Pull", THRAG, 57, 57, "Farseer's",
        "Farseer Thrag says the spirits of this coast are restless, and the leylines are dragging them toward the "
        "sea. The Tower of Eldara on East Azshara's northern cape still hums, and he thinks it's holding them back. The spirits have been uneasy since the day the world changed, Thrag says, and the coast is the worst of it.",
        [explore(172, 32, "Listen at the foot of the Tower of Eldara", EA, radius=9)],
        "The tower's on the northern cape of East Azshara. Stand at its foot and listen. If it's humming, it's "
        "holding. If it's quiet, run.",
        "Humming, but out of tune. It's holding, for now.\n\nThe elves won't believe a shaman. They might believe "
        "you."))
    A(Q("az_imps_at_forlorn_ridge", "Imps at Forlorn Ridge", THRAG, 56, 56, "Ridgeward",
        "The fel gate at Forlorn Ridge never quite closed, and the imps keep crawling out of it into Central "
        "Azshara's woods. Thrag can hear the trees complain.",
        [k("Forlorn Imp", 12, CA)],
        "Forlorn Ridge is the south-west of Central Azshara. The Forlorn Imps swarm round the gate. Burn them out "
        "of the trees before they set them alight, and they've already started.",
        "The trees are quieter. The gate isn't.",
        nxt="az_the_gate_that_wont_close"))
    A(Q("az_the_gate_that_wont_close", "The Gate That Won't Close", THRAG, 57, 57, "Gatebreaker",
        "Thrag wants the gate at Forlorn Ridge shut, and the ones holding it open are the Legion's leftovers: the "
        "Forlorn Eredar who keep the rite going and the Forlorn Doomguard who guard them.",
        [k("Forlorn Eredar", 8, CA), k("Forlorn Doomguard", 6, CA)],
        "Up on Forlorn Ridge, round the gate. The Forlorn Eredar keep the rite alive and the Forlorn Doomguard keep "
        "you off them. You've got to break both of them.",
        "The rite's broken. The gate's still standing, but nothing's feeding it.",
        nxt="az_gatekeeper_azgaroth"))
    A(Q("az_gatekeeper_azgaroth", "Gatekeeper Azgaroth", THRAG, 57, 57, "Doomward",
        "One doomguard still stands at the gate on Forlorn Ridge, and he's the one the Legion left in charge: "
        "Gatekeeper Azgaroth. As long as he stands, it'll open again.",
        [boss("Gatekeeper Azgaroth", CA)],
        "Azgaroth keeps the gate on Forlorn Ridge. He hits like a falling tree and burns like one too. You'll want "
        "a healer with you.",
        "The gate's dark. The spirits can rest a little.\n\nGo and tell the elves a shaman shut their demon "
        "door. Watch their faces."))

    # ---- Spellbreaker Ilanthe
    A(Q("az_satyrs_on_the_road", "Satyrs on the Road", ILANTHE, 53, 53, "Spellbreaker's",
        "Spellbreaker Ilanthe watches the road for satyrs, and the Haldarr Tricksters have started setting curses on "
        "it, so the carts go round in circles in the woods until the drivers cry.",
        [k("Haldarr Trickster", 8, WA)],
        "The Haldarr Tricksters come down out of their encampment in the south-east of West Azshara. Break their "
        "tricks, and then break them. They're cowards when it's done to them.",
        "No more circles. The grunt will say it was his idea to send you, and I'm going to let him. The carters are newcomers, and they'd never seen a satyr in their lives."))
    A(Q("az_the_shadowcasters_of_legash", "The Shadowcasters of Legash", ILANTHE, 56, 56, "Legash",
        "The satyrs' war camp at Legash Encampment under the northern mountains is where the curses come from. The "
        "Legash Shadowcasters teach them to the Haldarr, and Ilanthe wants the teachers gone.",
        [k("Legash Shadowcaster", 8, CA)],
        "Legash Encampment's in the north of Central Azshara, under the mountains. The Legash Shadowcasters keep to "
        "the tents round the throne. Take them out.",
        "The curses on the road have stopped. The warlord at Legash will have noticed.",
        nxt="az_warlord_sethrak"))
    A(Q("az_warlord_sethrak", "Warlord Seth'rak", ILANTHE, 57, 57, "Warlord's",
        "Warlord Seth'rak sits on the throne at Legash Encampment, under a Timbermaw totem the satyrs stole. "
        "Ilanthe wants him off it, and the Timbermaw would like their totem back.",
        [boss("Warlord Seth'rak", CA)],
        "Seth'rak's throne is at the heart of Legash Encampment. He fights with a glaive, and he'll pin you to "
        "the throne if you let him.",
        "The warlord's dead. Send word to Timbermaw Hold that their totem's waiting."))

    # ======================================================================================== THE FIELD
    # ---- Grunt Okkar, Valormok
    A(Q("az_valormok_burned", "Valormok Burned", OKKAR, 54, 54, "Valormok",
        "The satyrs burned Valormok to the ground a month ago, and Grunt Okkar's the only one of the watch still "
        "here. The Haldarr Felsworn did the burning. Valormok went up three years ago, when the Integration opened the road north.",
        [k("Haldarr Felsworn", 8, WA)],
        "The Haldarr Felsworn came down from the encampment to the east. Go up there and burn them the way they "
        "burned us. Don't leave a tent standing.",
        "That's a start on what they owe. Not the end of it.",
        zone=WA, nxt="az_vrexx_the_hornbreaker"))
    A(Q("az_vrexx_the_hornbreaker", "Vrexx the Hornbreaker", OKKAR, 55, 55, "Hornbreaker",
        "The satyr who led the raid on Valormok is Vrexx the Hornbreaker, and Okkar watched him laugh while it "
        "burned. He keeps to the Haldarr Encampment.",
        [boss("Vrexx the Hornbreaker", WA)],
        "Vrexx is up in the Haldarr Encampment, east of here. He's big and horned, with fel fire in both hands. "
        "Make him stop laughing.",
        "So he's dead, and that's good.\n\nI'll build the watchtower back myself, one log at a time.",
        zone=WA))
    A(Q("az_thunder_in_the_mere", "Thunder in the Mere", OKKAR, 54, 54, "Merewalker",
        "The thunder lizards in the Sundering Mere have started coming up onto the Orgrimmar road, and Okkar says "
        "the caravans won't run past them.",
        [k("Mere Thunderhide", 8, WA)],
        "The Sundering Mere's south of here, east of the road. The Mere Thunderhides wallow in the shallows. "
        "Drive them back into the water.",
        "The caravans ran this morning. Two wagons, and both of them got through.",
        zone=WA, nxt="az_old_stormhide"))
    A(Q("az_old_stormhide", "Old Stormhide", OKKAR, 55, 55, "Stormhide",
        "The biggest thunder lizard in the Mere is Old Stormhide, and the caravan drivers have stories about it. "
        "Okkar says the stories are true.",
        [boss("Old Stormhide", WA)],
        "Old Stormhide wallows at the heart of the Sundering Mere. When it stamps, the whole Mere shakes, so don't "
        "let it put you on your back.",
        "The drivers won't believe it's dead until they see the hide. I'll nail it over the gate.",
        zone=WA))

    # ---- Captain Zarga Bloodfang, Stormwatch
    A(Q("az_raiders_of_the_reaches", "Raiders of the Reaches", MAZKAR, 57, 57, "Stormwatch",
        "The naga on the Bitter Reaches strip every wreck that washes up on East Azshara's north coast, and lately "
        "they've started on the Horde's supply boats. Captain Zarga at Stormwatch has asked the Landing for help, "
        "and Grunt Mazkar is sending you.",
        [k("Bitter Reaches Raider", 10, EA)],
        "The Bitter Reaches is the north coast, and there are wrecks everywhere. The Bitter Reaches Raiders work "
        "the wrecks, and they'll fight you for them.",
        "They'll come back, they always do. But they'll come back fewer.",
        zone=EA, nxt="az_the_wavecallers"))
    A(Q("az_the_wavecallers", "The Wavecallers", ZARGA, 58, 58, "Wavebreaker",
        "The raiders don't wreck the boats themselves. The Bitter Reaches Wavecallers call the waves that do it, "
        "from the naga shrine on the Reaches.",
        [k("Bitter Reaches Wavecaller", 8, EA)],
        "The Bitter Reaches Wavecallers sing from the shrine on the north coast. Shut them up, and the sea'll calm.",
        "The sea's calm for the first time in a week. My boats are running. Two of my boat crews are newcomers who sailed on Earth, and they say they've never seen a sea do that.",
        zone=EA, nxt="az_captain_ssarith"))
    A(Q("az_captain_ssarith", "Captain Ssarith", ZARGA, 58, 58, "Wreckbreaker",
        "The raiders answer to Captain Ssarith, a naga who sails a stolen Kul Tiran hull up and down the coast. "
        "Zarga wants the captain, and she wants the hull.",
        [boss("Captain Ssarith", EA)],
        "Ssarith holds the biggest wreck on the Bitter Reaches. She fights with a trident made from a ship's "
        "anchor. Don't let her hook you.",
        "The hull's ours. I'll have it patched and flying the Horde's colours by the end of the month.",
        zone=EA))
    A(Q("az_the_temple_guard", "The Temple Guard", ZARGA, 59, 59, "Templebreaker",
        "The naga have taken the Temple of Zin-Malor on the southern headland and filled it with guards. Zarga "
        "wants to know why they need that many.",
        [k("Zin-Malor Warden", 8, EA)],
        "The Temple of Zin-Malor's on the southern headland. The Zin-Malor Wardens hold the steps. Break the "
        "guard.",
        "Under all those guards, a door going down. The naga are guarding a tunnel.",
        zone=EA, nxt="az_high_priestess_nazeth"))
    A(Q("az_high_priestess_nazeth", "High Priestess Naz'eth", ZARGA, 59, 59, "Zin-Malor",
        "The temple's high priestess, Naz'eth, is the one who ordered the tunnel dug, and Zarga wants it to stop "
        "at her.",
        [boss("High Priestess Naz'eth", EA)],
        "Naz'eth keeps the heart of the Temple of Zin-Malor. She'll flood the floor under you, so don't stand still.",
        "The tunnel's collapsing on its own now. Whatever they were digging toward, they won't get there from "
        "this side.",
        zone=EA))

    # ---- Ranger Thessaly Dawnsong, Stormwatch (the Conclave's)
    A(Q("az_the_court_dead", "The Court Dead", AELIS, 59, 59, "Courtwatch",
        "The Drowned Court is full of Highborne dead who think it's ten thousand years ago, and the Court Sentinels "
        "still guard the streets for a queen who isn't there. The sea came up over Quel'Thalas's coast the day the world changed, and the Conclave has been looking for a shore ever since.",
        [k("Court Sentinel", 8, EA)],
        "Out along the causeway from the Promenade to the Drowned Court. The Court Sentinels walk the streets. "
        "Let them rest. They've stood watch long enough.",
        "My grandmother's grandmother walked those streets. I'd like to walk them too, one day, without being "
        "stabbed.",
        zone=EA))
    A(Q("az_seals_of_the_court", "Seals of the Court", THESSALY, 58, 58, "Sealbearer's",
        "Every Promenade Noble still carries the seal of their office, and the Conclave can read the names on them. "
        "Thessaly wants the names before the sea takes them back.",
        [fetch("az_q_court_seal", 8)],
        "The Promenade Nobles walk the marble road into the sea. Take their seals, gently if you can. They were "
        "somebody once, and they don't know they've stopped.",
        "Lords, ladies, a court physician. And one name that's on the ledger Brightspire's after.",
        zone=EA, nxt="az_the_weeping_duchess"))
    A(Q("az_the_weeping_duchess", "The Weeping Duchess", THESSALY, 59, 59, "Duchess's",
        "One of the names on the seals is a duchess who drowned waiting for her husband to come back from the "
        "palace. The Weeping Duchess still walks the Drowned Court, and the other ghosts follow her.",
        [boss("The Weeping Duchess", EA)],
        "She walks the heart of the Drowned Court. Her grief's a weapon. Don't let her hold you.",
        "She's at rest. I'll write her name in the Conclave's book myself.",
        zone=EA))
    A(Q("az_eldaras_guardians", "Eldara's Guardians", THESSALY, 58, 58, "Eldara",
        "The Tower of Eldara on the northern cape still hums, and the Eldara Arcane Guardians won't let the "
        "Conclave anywhere near it. Thessaly wants inside.",
        [k("Eldara Arcane Guardian", 8, EA)],
        "The tower's on the northern cape. The Eldara Arcane Guardians walk its foot. Break enough of them and "
        "the door should open.",
        "The door's open, and there's someone inside who still thinks he's in charge.",
        zone=EA, nxt="az_magus_valethion"))
    A(Q("az_magus_valethion", "Magus Valethion", THESSALY, 58, 58, "Valethion's",
        "The tower's keeper is a Highborne magus who never left, Magus Valethion, and the tower answers to him. "
        "Thessaly wants it to answer to the Conclave.",
        [boss("Magus Valethion", EA)],
        "Valethion's inside the Tower of Eldara. He'll ward himself when he's hurt. Break the ward, then him.",
        "The tower's ours. It's still holding the leylines back, and now we know how.",
        zone=EA))
    return out


def build():
    """Every quest in Azshara, in the order the builder writes them."""
    _cyc[0] = 0
    out = build_landing()
    try:
        from tools.azshara_quests_hold import build_hold
        out += build_hold()
    except ImportError:
        pass
    return out
