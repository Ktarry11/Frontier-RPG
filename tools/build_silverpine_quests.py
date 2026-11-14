#!/usr/bin/env python3
"""Silverpine quest pass (2026-10-23).  Idempotent.  Sections are added stage by stage.

    python3 tools/build_silverpine_quests.py && python3 tools/retier_quest_rewards.py     (then `git checkout` every OTHER quest file)

Writes data/quests/silverpine_north.json: 31 quests, L11-17, on the real subzones of the rebuilt Silverpine North.
  Rear Guard (hub)        Captain Vesk, Apothecary Pell, Dark Cleric Ravenna, the road scout
  Olsen's Farthing        Gaffer Olsen + Widow Marta        hounds -> seeds -> Old Hob; a drop-started locket
  Raven Hill Cemetery     Keeper Oswin + Acolyte Dessa      husks -> The Forsaken Watchman; the Agamand cipher lives in tirisfal.json
  The Dead Field          Huntress Verrel + farmhand Tobb   crows / harrowers -> Gaunt the Scarecrow-King; a drop-started ring
  Sepulcher gate          Gatewarden Ilsa
  Malden's Orchard        Orchard-Warden Malwick            blight -> cores -> Orchardkeeper Gnarl
  Shadowspring Pools      Warden Yaelis                     beasts -> fangs -> Muckmaw
  The Skittering Dark     Webhunter Corvane                 skitterers -> egg sacs -> Longleg -> the Widow's Lair mouth
  and a "Linken gate" finale at the Rear Guard that needs all four boss quests.  Kill / fetch / boss / explore / deliver ONLY - no escorts.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import kill, fetch     # noqa: E402
from tools import tirisfal_gear                         # noqa: E402
from tools.tirisfal_gear import reward_pack             # noqa: E402

OUT_N = ROOT / "data/quests/silverpine_north.json"
OUT_S = ROOT / "data/quests/silverpine_south.json"
OUT_SEP = ROOT / "data/quests/sepulcher.json"
SEP = "sepulcher"
DROPS = ROOT / "data/creatures/quest_drops.json"
SPN = "silverpine_north"
SPS = "silverpine_south"

tirisfal_gear.THEMES.update({
    "spn_guard": (["Rear-Guard", "Palisade", "Vesk's", "Border-Watch", "Pine-Gate", "Sentry's"],
                  ["Issued at the northern gate, patched at the northern gate.", "The Rear Guard wears what lasts.",
                   "Smells of pine-smoke and old orders."]),
    "spn_farm": (["Farthing", "Olsen's", "Harvest-Blighted", "Hound-Wary", "Furrow-Worn", "Barn-Dust"],
                 ["Stitched by someone who still believed in next year's crop.", "The mud has outlived the farm.",
                  "A farmer's make-do."]),
    "spn_grave": (["Raven Hill", "Oswin's", "Grave-Keeper's", "Moss-Eaten", "Cemetery-Shadowed", "Vigil-Worn"],
                  ["Dug up, dusted off, declared fit.", "The dead don't mind. Mostly.", "Keeper's cut, keeper's wear."]),
    "spn_field": (["Dead Field", "Scarecrow's", "Crow-Pecked", "Harrower's", "Stubble-Torn", "Gaunt's"],
                  ["Straw in the seams and a feather in the lining.", "Nothing grows here. This is the proof.",
                   "Stitched with a farmer's last ounce of hope."]),
    "spn_orchard": (["Malden's", "Windfall", "Orchard-Warden's", "Rotapple", "Heartwood", "Blossom-Cursed"],
                    ["Smells of fruit that never ripened.", "Cut from a branch that kept walking.",
                     "Sweet, rotten, and surprisingly durable."]),
    "spn_pool": (["Shadowspring", "Mire-Slick", "Reed-Cut", "Black-Water", "Yaelis'", "Fen-Hardened"],
                 ["Dried, but never entirely.", "The spring runs black. So does the stitching.", "Salvaged from the shallows."]),
    "spn_web": (["Skittering", "Longleg's", "Silk-Wrapped", "Webhunter's", "Venom-Cured", "Carapace"],
                ["Spun in the dark.", "The silk is stronger than the stitching.", "Cured in venom, worn in spite."]),
})

tirisfal_gear.THEMES.update({
    "sep_keep": (["Sepulcher", "Keep-Hall", "Vane's", "Terrace-Worn", "Crypt-Stair", "Tomb-Warden's"],
                 ["Climbed a hundred steps and came back for more.", "Stone-cold and spotlessly kept.",
                  "The Keep issues it. The dead approve."]),
})

tirisfal_gear.THEMES.update({
    "sps_camp": (["Valgan's", "March-Issue", "Field-Camp", "Dallow's", "Cold-Rations", "Trench-Worn"],
                 ["Issued by a sergeant who counts everything twice.", "Seen more campaigns than winters.",
                  "Camp-mended, camp-stained."]),
    "sps_farm": (["Bucklebree", "Hog-Pen", "Quilted", "Barn-Worn", "Merriam's", "Pumpkin-Patch"],
                 ["Farm-spun and forgotten.", "Smells of hay and old straw.", "Patched by someone who still tries."]),
    "sps_marsh": (["Olivia's", "Marsh-Gas", "Reed-Cured", "Thorne's", "Bog-Fouled", "Peat-Stained"],
                  ["Damp, and not from the rain.", "Dried near a fire that never quite took.", "The pond leaves its mark."]),
    "sps_mine": (["Deep Elem", "Kobold-Cut", "Pit-Lamp", "Hobart's", "Gallery", "Candle-Guttered"],
                 ["Dusted in ore.", "Scuffed in the dark.", "Worn by a long shift that never ended."]),
    "sps_pyre": (["Pyrewood", "Ash-Singed", "Hearthwarden's", "Burned-Hall", "Cinder-Hewn", "Embered"],
                 ["Warm, long after the fire.", "Scorched at every seam.", "Pyrewood's last good cloth."]),
    "sps_talon": (["Talon-Hill", "Grief-Haunted", "Hask's", "Trapper's", "Wraith-Thread", "Berard's"],
                  ["Cold to the touch and slow to warm.", "Whispers when handled.", "Snared, skinned, and sewn."]),
    "sps_peril": (["Peril-Marked", "Packbreaker's", "Rynn's", "Den-Cured", "Moonlit", "Claw-Torn"],
                  ["Torn once and stitched twice.", "Smells of wet fur and worse.", "The pack's idea of fashion."]),
    "sps_wall": (["Greymane", "Wall-Sworn", "Teague's", "Gate-Watch", "Stonework", "Border-Held"],
                 ["Cold stone and colder duty.", "Marked with a lion's head.", "The wall's last uniform."]),
    "sps_amber": (["Ambermill", "Waygate-Lit", "Orsolo's", "Resin-Bound", "Dalaran-Cut", "Sawmill"],
                  ["Smells of pitch and old magic.", "Violet at the seams.", "Mill-dust and spellwork."]),
    "sps_ferry": (["Decrepit-Ferry", "Lakewater", "Gael's", "Dock-Rotted", "Mooring", "Tide-Tallied"],
                  ["Salt, moss and lake.", "The lake keeps a tally.", "Waterlogged, and proud of it."]),
})

# ---- level tables (Undercity hub scale, +80 xp / +300 gold per level) ----------------------------------------------------------
XP = {11: 600, 12: 680, 13: 760, 14: 840, 15: 920, 16: 1000, 17: 1080, 18: 1160, 19: 1240, 20: 1320}
GOLD = {11: 2700, 12: 3200, 13: 3600, 14: 3900, 15: 4200, 16: 4500, 17: 4800, 18: 5100, 19: 5400, 20: 5700}


def explore(zone, x, y, radius=6):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def boss(target, zone):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def carry(item_id, name, desc):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, mult=None, **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if (is_boss and ilvl >= 10) else "uncommon"
    m = mult if mult is not None else (1.3 if is_boss else 1.0)
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs, reward_exp=int(XP[hi] * m), reward_gold=int(GOLD[hi] * m),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             rewards=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3))
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def north():
    Z = []
    A = Z.append

    # ============================================================================================ THE REAR GUARD (hub)
    VESK, PELL, RAV, SCOUT = "sp_rg_captain", "sp_rg_apothecary", "sp_rg_cleric", "sp_north_scout"
    A(Q("spn_trunk_walk", "Walk the Trunk Road", VESK, SPN, 11, 12, "spn_guard",
        "Captain Vesk holds the Forsaken Rear Guard at the border gate, and the Trunk Road is the only thing keeping the garrison "
        "connected to the Sepulcher. Nobody has walked its whole length since the first frost. Walk it to the Crossroads and tell him "
        "what you see.",
        [explore(SPN, 78, 34, 6), explore(SPN, 76, 52, 6), explore(SPN, 72, 70, 6)],
        "South from the gate. Past the scout's post, past the Dead Field turning, down to the Crossroads. Keep your eyes open. "
        "I'd rather you kept them in your skull, too.",
        "No ambush, no wreckage, no trouble but the usual. That is the best news I've had all week. Here, you've earned this.",
        "spn_worg_cull"))
    A(Q("spn_worg_cull", "Thin the Woods", VESK, SPN, 11, 12, "spn_guard",
        "The worgs have taken to the verge of the road, and the ghouls have taken to the worgs' leavings. Vesk would like both pushed "
        "back out of range of the Trunk Road, preferably in pieces.",
        [kill("Worg Prowler", 6, zone=SPN), kill("Feral Ghoul", 5, zone=SPN)],
        "Anywhere in the Silverpine woods. Worg Prowlers and Feral Ghouls. Make them think twice about the road.",
        "A quieter road. Nobody will notice, which is exactly how it should be.", None,
        requires_quests=["spn_trunk_walk"]))
    A(Q("spn_pell_glands", "Venom for the Vats", PELL, SPN, 12, 13, "spn_guard",
        "Apothecary Pell has a theory that Silverpine spider venom, properly cut, can be used to slow the Plague's advance. Pell has "
        "a lot of theories. This one at least requires something killable. Bring six venom glands.",
        [fetch("sp_venom_gland", 6)],
        "Silverpine Spiders in the woods. Cut the gland out cleanly. Don't squeeze. I cannot stress enough: don't squeeze.",
        "Beautiful. Green, fresh, still faintly pulsing. If this works, the Dark Lady will hear my name. If it doesn't, you never met me.",
        None))
    A(Q("spn_ravenna_rite", "A Rite for the Widow", RAV, SPN, 12, 13, "spn_guard",
        "Dark Cleric Ravenna has prepared a Rite of Quieting for a woman in Olsen's Farthing whose husband will not stop walking "
        "past her window. Ravenna cannot leave the gate. Deliver the rite to Widow Marta, and do not read it aloud.",
        [deliver("sp_rite_scroll", "Deliver the Rite of Quieting to Widow Marta, Olsen's Farthing")],
        "West along the Farthing road. The widow lives in the house nearest the dead orchard. Tell her to read it at dusk.",
        "She said I'd send someone kind. I'd hoped she was joking. Thank you.", None,
        turn_in_npc_id="sp_farthing_widow",
        grant_items=carry("sp_rite_scroll", "Rite of Quieting", "A short rite on grave-wax paper. It smells of incense and old winter.")))
    A(Q("spn_scout_survey", "The Three Spurs", SCOUT, SPN, 13, 14, "spn_guard",
        "The Silverpine Scout watches the Trunk Road from the verge and has noticed fresh tracks on three of its spurs: the road "
        "east to the Dead Field, the path to the Shadowspring Pools, and the lane into Malden's Orchard. He wants eyes on the ends of all three.",
        [explore(SPN, 110, 48, 6), explore(SPN, 88, 107, 6), explore(SPN, 50, 125, 6)],
        "Dead Field road, Pool path, Orchard lane. The tracks are the same on all three, and I do not like that.",
        "Same boot on all three roads. Someone is scouting the Rear Guard's approaches. Vesk needs to hear this.", None))

    # ============================================================================================ OLSEN'S FARTHING
    OLS, MAR = "sp_farthing_gaffer", "sp_farthing_widow"
    A(Q("spn_farthing_hounds", "The Hounds of the Farthing", OLS, SPN, 12, 13, "spn_farm",
        "Gaffer Olsen kept hounds for forty years. Since the plague, they've kept him: hungry, rabid, and pacing the fence at night. "
        "The risen farmhands let them through the gate. He wants both dealt with, and is not above admitting he is afraid of his own dogs.",
        [kill("Farthing Hound", 6, zone=SPN), kill("Risen Farmhand", 5, zone=SPN)],
        "The fields around my farm. The hounds first. The farmhands - well. They were good lads once.",
        "Quieter. Thank you. I'll fill the troughs again, I think, when I'm brave enough.", "spn_olsens_seed"))
    A(Q("spn_olsens_seed", "Seed for Next Year", OLS, SPN, 13, 14, "spn_farm",
        "Olsen believes that if he can plant one decent row of wheat, the Farthing might remember it was a farm. The risen farmhands "
        "carry the last of the seed sacks in their pockets, as they did in life. Fetch five.",
        [fetch("sp_seed_sack", 5)],
        "The farmhands still carry them. I don't know why. Habit, I suppose. Five sacks. I'll do the rest.",
        "Good grain, if a little singed. I'll plant it at dawn. Somebody has to believe in dawn.", None,
        requires_quests=["spn_farthing_hounds"]))
    A(Q("spn_old_hob", "Old Hob", OLS, SPN, 14, 14, "spn_farm",
        "Old Hob was Olsen's best dog, and now leads the pack. He was a gentle old thing once. Olsen asks that you not make it slow.",
        [boss("Old Hob", SPN)],
        "In the fields south of the farm. The big one with the grey muzzle. He was a good boy.",
        "He'd have followed you home, once. Thank you for being quick.", None,
        requires_quests=["spn_farthing_hounds"]))
    A(Q("spn_farmhand_locket", "A Locket in the Furrow", "item:sp_farmhand_locket", SPN, 12, 14, "spn_farm",
        "A silver locket, pried from the pocket of a risen farmhand. Inside, a name: Marta. And a lock of hair the same colour as hers.",
        [deliver("sp_farmhand_locket", "Bring the locket to Widow Marta in Olsen's Farthing")],
        "Widow Marta, at the house nearest the orchard. She will want it back.",
        "He kept it. All this time, he kept it. Thank you. I won't forget this.", None,
        turn_in_npc_id=MAR))

    # ============================================================================================ RAVEN HILL CEMETERY
    OSW, DES = "sp_north_cemetery_keeper", "sp_rh_acolyte"
    A(Q("spn_rh_husks", "What Won't Stay Buried", OSW, SPN, 12, 14, "spn_grave",
        "Oswin has buried the same corpse three times this month. The risen husks of Raven Hill pull themselves out of the soil "
        "faster than he can fill the graves. Thin them out, and he'll try the burial again.",
        [kill("Risen Husk", 6, zone=SPN)],
        "Raven Hill Cemetery. They climb out at dusk. Beat them back.",
        "That will keep the shovel busy for another night, at least.", "spn_rh_moss"))
    A(Q("spn_rh_moss", "Moss on the Mourning Stones", DES, SPN, 13, 14, "spn_grave",
        "Acolyte Dessa believes the moss growing on Raven Hill's grave markers is feeding the dead. She wants six clippings from the "
        "Grave Moss Creepers that tend it, so she can study what they've been eating.",
        [fetch("sp_grave_moss", 6)],
        "The creepers at the lower graves. Take the moss from the body, not the stones. The stones are still sacred.",
        "Grey-green, thick with bone dust. It's feeding on them, and they're feeding on it. How very efficient.", "spn_rh_vigil",
        requires_quests=["spn_rh_husks"]))
    A(Q("spn_rh_vigil", "The Long Vigil", DES, SPN, 14, 15, "spn_grave",
        "To find where the dead are climbing from, Dessa needs someone to stand at the three oldest crypts and listen. It is, she admits, "
        "a poor job. She has asked three other people. None came back with an answer.",
        [explore(SPN, 50, 72, 5), explore(SPN, 34, 60, 5), explore(SPN, 44, 78, 5)],
        "Three crypts: east, north-west, south. Stand at each and count to ten. Listen for anything that isn't wind.",
        "Scratching. Under all three. As if something's digging up from below. Oswin needs to hear this.", None))
    A(Q("spn_rh_watchman", "The Forsaken Watchman", OSW, SPN, 15, 16, "spn_grave",
        "A Forsaken Watchman still patrols the upper cemetery. He no longer answers challenges, or his own name. Oswin knew him, and "
        "does not wish to watch him do it for another winter.",
        [boss("The Forsaken Watchman", SPN)],
        "The top of the hill, by the iron gate. He walks a circle. Don't be on the circle.",
        "He'll stand a post somewhere kinder now. Thank you for sending him.", None,
        requires_quests=["spn_rh_husks"]))

    # ============================================================================================ THE DEAD FIELD
    VER, TOB = "sp_df_huntress", "sp_df_farmhand"
    A(Q("spn_df_crows", "Carrion Calls", VER, SPN, 13, 14, "spn_field",
        "Huntress Verrel has been trying to shoot the crows of the Dead Field for a week. They don't die the way crows should; they "
        "just look at her, and settle on the next fence-post. She hands you a bow she's stopped trusting.",
        [kill("Blighted Crow", 8, zone=SPN)],
        "The Dead Field, east of the Trunk Road. Blighted crows. Aim for the eyes. They notice.",
        "Fewer eyes on me, finally. I'm in your debt. Take a bow, if you like. I won't use it.", None))
    A(Q("spn_df_harrowers", "Harrowers in the Furrows", TOB, SPN, 13, 14, "spn_field",
        "Tobb the farmhand was the last to leave the Dead Field and the first to come back. He sleeps in the barn. He says the "
        "scarecrows walk at night, and he's tired of watching them from the loft.",
        [kill("Dead Field Harrower", 6, zone=SPN)],
        "In the furrows, and along the fence lines. They wear farm coats. Don't mistake them for farmers.",
        "I sleep a little easier. I'll sleep a lot easier when I know where the straw goes.", "spn_df_straw"))
    A(Q("spn_df_straw", "Where the Straw Goes", TOB, SPN, 14, 15, "spn_field",
        "Every harrower carries a straw charm sewn into its coat. Tobb recognises the stitching: his own wife's. He wants five charms "
        "back, so that at least the stitches will be in a decent place.",
        [fetch("sp_harrower_straw", 5)],
        "Take the charm from the coat, the left breast. Don't pull the thread. It unravels.",
        "That's her hand, on every one. I'll bury them by the barn.", None,
        requires_quests=["spn_df_harrowers"]))
    A(Q("spn_df_ring", "A Ring in the Stubble", "item:sp_crow_ring", SPN, 13, 15, "spn_field",
        "A tarnished gold band, pecked loose from a crow's nest. The inside is engraved: T. & L., forever.",
        [deliver("sp_crow_ring", "Bring the ring to Tobb the farmhand at the Dead Field")],
        "Tobb, at the barn. He'll know it. He'll pretend he doesn't.",
        "Lena's. I thought the crows had it. I hoped they hadn't. Thank you.", None,
        turn_in_npc_id=TOB))
    A(Q("spn_df_king", "The Scarecrow-King", VER, SPN, 15, 15, "spn_field",
        "Something rules the Dead Field's scarecrows: a tall one in a straw crown, wrapped in a farmer's shroud. Verrel has "
        "shot it twice. It is still standing, and very much interested in her.",
        [boss("Gaunt the Scarecrow-King", SPN)],
        "The middle of the Dead Field, where the crows circle. The tall one. You'll know the crown.",
        "A quieter field, finally. I'll have to find a new hobby.", None,
        requires_quests=["spn_df_crows", "spn_df_harrowers"]))

    # ============================================================================================ SEPULCHER GATE
    ILS = "sp_sep_gatewarden"
    A(Q("spn_gate_hold", "Hold the Gate", ILS, SPN, 13, 14, "spn_guard",
        "Gatewarden Ilsa guards the iron door of the Sepulcher. The dead are welcome inside; the things that follow them are not. "
        "Treants and ghouls have been crowding the approach, and she's run out of patience.",
        [kill("Corrupted Treant", 4, zone=SPN), kill("Feral Ghoul", 5, zone=SPN)],
        "The woods around the gate. Treants, ghouls. Anything that shuffles toward the door.",
        "The door stays closed to what should be kept out. Welcome inside, whenever you like.", None))

    # ============================================================================================ MALDEN'S ORCHARD
    MAL = "sp_orchard_warden"
    A(Q("spn_orchard_blight", "The Blight in the Boughs", MAL, SPN, 14, 15, "spn_orchard",
        "Malden's Orchard has not borne fruit in years, but the trees still drop it: a brown, heavy windfall that moves on its own. "
        "The orchard-warden wants the shamblers cleared and the wasps that hive in the rot driven out.",
        [kill("Orchard Shambler", 6, zone=SPN), kill("Windfall Wasp", 6, zone=SPN)],
        "Under the old trees. The shamblers wear bark. The wasps wear a grudge.",
        "Fewer shamblers means more room for the trees to recover. Maybe.", "spn_orchard_cores"))
    A(Q("spn_orchard_cores", "Cores of Rotapple", MAL, SPN, 15, 16, "spn_orchard",
        "At the heart of every shambler is a seed-core of rotapple: black, dense, and faintly warm. Malwick believes the cores are "
        "what keep the blight spreading. Bring six, and he'll burn them in the orchard's last furnace.",
        [fetch("sp_rotapple_core", 6)],
        "Take them from the shamblers' chests. They are heavier than they look.",
        "Black as pitch. Warm as a living heart. They go to the furnace tonight.", None,
        requires_quests=["spn_orchard_blight"]))
    A(Q("spn_orchard_keeper", "The Orchardkeeper", MAL, SPN, 16, 16, "spn_orchard",
        "Under the biggest tree in the orchard stands a thing that was Malden's gardener. It tends the blight now. Malwick offers "
        "a bitter smile: 'He always did love his work.'",
        [boss("Orchardkeeper Gnarl", SPN)],
        "At the old tree, east of the trough. He holds a pruning hook the size of a plough.",
        "He'll tend something quieter now. Thank you.", None,
        requires_quests=["spn_orchard_blight"]))

    # ============================================================================================ SHADOWSPRING POOLS
    YAE = "sp_north_pools_warden"
    A(Q("spn_pools_beasts", "Teeth in the Water", YAE, SPN, 13, 14, "spn_pool",
        "The Shadowspring Pools were a Forsaken drinking-hole before the springs turned black. Now bog beasts and crocolisks "
        "hunt the shallows. Yaelis wants the pools made safe enough to stand beside.",
        [kill("Bog Beast", 5, zone=SPN), kill("Murky Crocolisk", 5, zone=SPN)],
        "The three pools, south-east of the crossroads. Don't wade. They can swim, and you can't.",
        "A quieter shoreline. I'll stand a little closer to the water now.", "spn_pools_fangs"))
    A(Q("spn_pools_fangs", "Fangs of the Mire", YAE, SPN, 14, 15, "spn_pool",
        "Rot Hide Slitherers hunt at the pools' edge, and their fangs carry a venom the Apothecary Society would pay handsomely for. "
        "Yaelis would settle for six, and the satisfaction of seeing them drained.",
        [fetch("sp_slitherer_fang", 6)],
        "Slitherers, in the reeds. Pull the fang with tongs. Please, use tongs.",
        "Six fangs, still wet. Pell at the Rear Guard will weep with joy.", None,
        requires_quests=["spn_pools_beasts"]))
    A(Q("spn_muckmaw", "Muckmaw", YAE, SPN, 16, 16, "spn_pool",
        "Something large and very old lives in the deepest pool. It has eaten two of Yaelis's scouts and a good portion of her patience. "
        "The locals call it Muckmaw. Kill it.",
        [boss("Muckmaw", SPN)],
        "The southernmost pool. Wait for the bubbles. Then don't wait.",
        "The water's still black. But it's quiet, and that's enough for now.", None,
        requires_quests=["spn_pools_beasts"]))

    # ============================================================================================ THE SKITTERING DARK
    COR = "sp_sd_webhunter"
    A(Q("spn_sd_skitterers", "Eight Legs, Too Many", COR, SPN, 15, 16, "spn_web",
        "Webhunter Corvane has tracked the spiders of the Skittering Dark for months, and the last month has been the worst: "
        "bigger, bolder, drifting toward the Trunk Road. He wants the breeding stock culled before they swarm.",
        [kill("Venomfang Skitterer", 6, zone=SPN), kill("Giant Spider", 3, zone=SPN)],
        "East of the Crossroads, in the hollows. Keep to the road till you see the webs.",
        "Fewer eyes in the dark. I'll almost sleep tonight.", "spn_sd_sacs"))
    A(Q("spn_sd_sacs", "Egg Sacs of the Dark", COR, SPN, 16, 16, "spn_web",
        "To end the swarm, Corvane needs the next generation. Egg sacs, carried by the skitterers themselves, and the only thing "
        "that makes the Widow's brood listen to anyone.",
        [fetch("sp_skitter_sac", 6)],
        "Take the sacs from their bodies. Don't puncture them. Carry them in silk, if you've got it.",
        "Six. Sealed. Warm. I'll burn them at the road. Never let a spider make a nest next to a road.", None,
        requires_quests=["spn_sd_skitterers"]))
    A(Q("spn_sd_longleg", "Longleg", COR, SPN, 17, 17, "spn_web",
        "A spider the size of a cart prowls the Skittering Dark, and takes a hunter a week. The others call it Longleg. "
        "Corvane has lost three apprentices to it, and wants it ended.",
        [boss("Longleg the Stalker", SPN)],
        "Deep in the Dark, where the webs get thick. It moves faster than it should.",
        "No more apprentices. Thank you.", "spn_sd_lair",
        requires_quests=["spn_sd_skitterers"]))
    A(Q("spn_sd_lair", "The Widow's Mouth", COR, SPN, 17, 17, "spn_web",
        "Longleg's brood came from somewhere, and Corvane thinks he knows where: the cave at the end of the Skittering road, "
        "the Widow's Lair. He wants someone to stand at the mouth and tell him how deep the webs go.",
        [explore(SPN, 148, 86, 4)],
        "East end of the Skittering road. Don't go in unprepared. And don't go in alone.",
        "As I feared. Silk to the ceiling. I'll hold the rest of the road. You, if you've the stomach, can hold the cave.", None,
        requires_quests=["spn_sd_longleg"]))

    # ============================================================================================ THE LINKEN GATE (finale)
    A(Q("spn_rg_reckoning", "The Rear Guard's Reckoning", VESK, SPN, 16, 17, "spn_guard",
        "Vesk has four reports on his desk: the Watchman is down, the Scarecrow-King is down, the Orchardkeeper is down, and "
        "Muckmaw is down. Whoever carried those four threads through the pines should stand at his desk and be thanked properly.",
        [explore(SPN, 84, 18, 5)],
        "Come back to the gate. Walk through it. I'd like you to see what you've protected.",
        "Four bosses, four reports, one hero. The Dark Lady's Rear Guard doesn't hand out praise. Take this instead.", None,
        mult=1.5, turn_in_npc_id=VESK,
        requires_quests=["spn_rh_watchman", "spn_df_king", "spn_orchard_keeper", "spn_muckmaw"]))
    return Z


def south():
    Z = []
    A = Z.append
    LYLE, HUNT, DAL, ASHE = "sp_south_gate_scout", "sp_south_hunter", "sp_south_march_sergeant", "sp_valgan_surgeon"

    # ============================================================================================ VALGAN'S FIELD (hub: the March)
    A(Q("sps_scout_report", "A Report for the March", LYLE, SPS, 15, 16, "sps_camp",
        "Deathguard Lyle has watched the south road from the gate for months. He has a short, grim report for Sergeant Dallow at "
        "Valgan's Field and no one to send. He would very much like it to arrive without having been read.",
        [deliver("sps_scout_report", "Deliver the scout's report to Sergeant Dallow at Valgan's Field")],
        "South along the trunk road. The field camp is under the banners, past the crossroad. Dallow will take it from you.",
        "Lyle always did write short. Two lines, a smudge, and a warning. I'll make something of it.", None,
        turn_in_npc_id=DAL,
        grant_items=carry("sps_scout_report", "Lyle's Scout Report", "A single folded page, sealed with a drop of black wax.")))
    A(Q("sps_forsaken_march", "Clear the March", DAL, SPS, 15, 16, "sps_camp",
        "The March exists to keep the road to Ambermill open, and the road is full of wolves and the leavings of bears that "
        "died of something the Apothecaries haven't named. Dallow wants both thinned before the next supply train.",
        [kill("Diseased Wolf", 6, zone=SPS), kill("Zombie Bear", 4, zone=SPS)],
        "Anywhere in the pines south of the gate. Wolves and bears. If it's limping and drooling, it's the one.",
        "Quieter roads, fewer drovers screaming. You're a credit to the March.", None))
    A(Q("sps_deserters", "Walk-Aways", DAL, SPS, 16, 17, "sps_camp",
        "Some of the March did not stay. A few dozen Forsaken, tired of orders, walked off Valgan's Field and set up as brigands "
        "on the farm. Dallow takes this personally, as the walking-off was done under his nose.",
        [kill("Field Deserter", 6, zone=SPS)],
        "Valgan's Field, the ruined farm around my camp. They wear March coats with the insignia torn off.",
        "I'd hoped they'd come back on their own. They didn't. Thank you for doing what I couldn't.", None,
        requires_quests=["sps_forsaken_march"]))
    A(Q("sps_deserter_tags", "Dog Tags", DAL, SPS, 16, 17, "sps_camp",
        "Every March soldier is issued an iron tag, stamped with a number. Dallow keeps the roll, and wants the tags of the "
        "deserters, so that when someone else asks who left, he can say who and by what number.",
        [fetch("sps_deserter_tag", 6)],
        "Off the bodies of the deserters. Iron tags on a cord. Six of them.",
        "Six names off the roll. They'll be remembered, though perhaps not kindly.", None,
        requires_quests=["sps_forsaken_march"]))
    A(Q("sps_deserter_letter", "The Letter in the Pocket", "item:sps_deserter_letter", SPS, 16, 18, "sps_camp",
        "A letter, taken from a dead deserter's pocket, addressed to someone in the Undercity. The seal is unbroken. "
        "Whatever it says, someone in the March ought to read it before it's posted.",
        [deliver("sps_deserter_letter", "Bring the letter to Sergeant Dallow")],
        "Dallow, at Valgan's Field. He will want to know who the deserters were writing to.",
        "A mother, in Brill. The man was nineteen. Gods. I'll see she's told the right way.", None,
        turn_in_npc_id=DAL))
    A(Q("sps_wight_bones", "Bones for the Surgeon", ASHE, SPS, 17, 18, "sps_camp",
        "Field Surgeon Ashe has run out of replacement bone. The battlefield wights of Valgan's Field wear the bones of better "
        "men, and she is not too proud to recycle them.",
        [fetch("sps_wight_bone", 6)],
        "The wights on the field. Take the long bones - arms and legs. Cleaned, if you can.",
        "These'll do. Slightly used, slightly regretful. Thank you.", None))
    A(Q("sps_deathguard_captain", "The Captain Who Never Stopped", DAL, SPS, 18, 18, "sps_camp",
        "A Deathguard Captain has been fighting the Third War on Valgan's Field since before Dallow arrived. He does not "
        "answer to orders, rank, or reason, and the March cannot hold the field while he walks it.",
        [boss("Deathguard Captain", SPS)],
        "Deep in the field, where the wights gather. He's the one still giving commands.",
        "He was a good officer once. The best of us, maybe. Thank you for ending the watch.", None,
        requires_quests=["sps_deserters"]))
    A(Q("sps_hunter_pelts", "Pelts for the Hunter", HUNT, SPS, 15, 16, "sps_camp",
        "The Forsaken Hunter wants six clean wolf pelts. 'Diseased' is fine; 'dissolving' is not. He's making a cloak for someone "
        "he used to know, and refuses to say who.",
        [fetch("sps_wolf_pelt", 6)],
        "The diseased wolves along the road. Skin them carefully. The cloak is a gift.",
        "Good work. A bit mangy, but a cloak that's been through something is worth more.", "sps_hunter_roost"))
    A(Q("sps_hunter_roost", "Carrion Calls", HUNT, SPS, 16, 17, "sps_camp",
        "The carrion birds have been following the Hunter's traps and stealing the kills. He doesn't mind sharing, much. He minds the "
        "birds taking the traps.",
        [kill("Carrion Bird", 6, zone=SPS)],
        "Anywhere in the pines. They're bold. Show them what boldness gets.",
        "That'll teach them manners. Doubt it, but it's a start.", None,
        requires_quests=["sps_hunter_pelts"]))

    # ============================================================================================ BUCKLEBREE FARM
    FAR, GOO = "sp_buckle_farmer", "sp_buckle_goodwife"
    A(Q("sps_hogs", "The Hogs Went First", FAR, SPS, 15, 16, "sps_farm",
        "The Bucklebree hogs went wrong the same week the plague reached the farm. They still root in the dirt, but what they "
        "root up is worse. Farmer Bucklebree wants the herd put down before it breeds.",
        [kill("Blightfed Hog", 6, zone=SPS), kill("Barn Ghoul", 5, zone=SPS)],
        "The pens and the barn. The hogs won't run. The ghouls will, and then come back.",
        "It's quiet on the farm for the first time in months. Odd how much I miss the noise.", None))
    A(Q("sps_quilts", "The Missing Quilts", GOO, SPS, 15, 16, "sps_farm",
        "Merriam sewed a quilt for every child born on the farm. The barn ghouls drag them off and sleep on them. She wants six "
        "scraps back, to piece together whatever's left of the family.",
        [fetch("sps_quilt_scrap", 6)],
        "The barn ghouls. They keep the scraps tucked into their rags.",
        "That's the blue one. That's my mother's stitching. Thank you. Thank you.", None))
    A(Q("sps_gorra", "Tusk-Mother Gorra", FAR, SPS, 17, 17, "sps_farm",
        "The old sow of the Bucklebree herd was the biggest hog in Silverpine. She did not die with the others. She grew. "
        "Bucklebree has a knife, and no stomach to use it.",
        [boss("Tusk-Mother Gorra", SPS)],
        "In the east field, past the fence. You'll hear her before you see her.",
        "She nursed forty litters. She was a good mother, in her way. Thank you.", None,
        requires_quests=["sps_hogs"]))

    # ============================================================================================ OLIVIA'S POND
    THO = "sp_pond_marshwalker"
    A(Q("sps_pond_ooze", "What Moves in the Water", THO, SPS, 16, 17, "sps_marsh",
        "Marshwalker Thorne has walked the edge of Olivia's Pond for two years, and for the last three weeks something has walked it "
        "with him. Marsh oozes, swamp ghouls, bloated things. He'd like fewer companions.",
        [kill("Marsh Ooze", 6, zone=SPS), kill("Swamp Ghoul", 5, zone=SPS)],
        "Around the pond. The oozes hug the shore. The ghouls come out at dusk.",
        "A little quieter. A little less of me sinking in the mud. Thank you.", None))
    A(Q("sps_pond_edge", "The Pond's Edge", THO, SPS, 16, 17, "sps_marsh",
        "Thorne wants someone to circle the pond on foot and tell him what's changed. He has a theory about where the water is "
        "going, and a stronger theory about where it's coming from.",
        [explore(SPS, 42, 56, 5), explore(SPS, 36, 70, 5), explore(SPS, 22, 68, 5)],
        "Three points: the east bank, the south bank, the south-west reeds. Count the dead fish. If there are none, run.",
        "No fish at all. That's the answer I was afraid of.", "sps_pond_samples",
        requires_quests=["sps_pond_ooze"]))
    A(Q("sps_pond_samples", "Gas from the Bloated", THO, SPS, 17, 18, "sps_marsh",
        "The bloated corpses of the pond carry bladders of marsh gas, and Thorne wants five, sealed, to test. He claims the gas is "
        "the source of the oozes. It has a simple remedy: stop it at the source.",
        [fetch("sps_marsh_sample", 5)],
        "The bloated corpses, by the south bank. Pierce them carefully. Do not breathe.",
        "That smell is worse than I'd hoped. That's how I know it's the right stuff.", None,
        requires_quests=["sps_pond_ooze"]))
    A(Q("sps_bloated_one", "The Bloated One", THO, SPS, 18, 18, "sps_marsh",
        "At the pond's heart lies a corpse so swollen it can no longer rise. It lashes at anything that comes near, and what it "
        "bursts into is worse than what it was. Thorne has finally found the source.",
        [boss("The Bloated One", SPS)],
        "The middle of the pond, up to your ankles in muck. Strike and step back. Strike and step back.",
        "It's burst, and it's done. I'll wash for a week. Thank you.", None,
        requires_quests=["sps_pond_ooze"]))

    # ============================================================================================ DEEP ELEM MINE
    HOB = "sp_elem_foreman"
    A(Q("sps_mine_kobolds", "Kobolds in the Gallery", HOB, SPS, 16, 17, "sps_mine",
        "Overseer Hobart held the Deep Elem Mine through the plague, the Scourge and the second strike. The kobolds that moved "
        "in after the collapse have moved in for good. He wants the gallery cleared, and he wants to see them go first.",
        [kill("Feral Rotting Kobold", 6, zone=SPS), kill("Deep Elem Digger", 5, zone=SPS)],
        "At the mine mouth and the old galleries. Kobolds, rotting and digging. Both bite.",
        "That's a clear gallery. I can almost smell the ore again.", None))
    A(Q("sps_mine_lamps", "Lamps in the Dark", HOB, SPS, 17, 18, "sps_mine",
        "Shamblers of dead miners still walk Deep Elem's galleries, carrying the lamps they died with. Hobart wants six. "
        "'They belonged to the company,' he says, a little too firmly.",
        [fetch("sps_miner_lamp", 6)],
        "The shamblers at the mine mouth. Take the lamps from their hands. Mind the oil.",
        "Six lamps, six names. The company will be pleased. I can stop pretending there's a company.", None,
        requires_quests=["sps_mine_kobolds"]))
    A(Q("sps_mine_gallery", "The Collapsed Gallery", HOB, SPS, 17, 18, "sps_mine",
        "The main gallery collapsed the day of the plague, and Hobart has never been back to look. He wants someone to stand "
        "at its mouth, and tell him whether the supports held.",
        [explore(SPS, 18, 98, 4)],
        "The mine mouth to the west. Don't go in. Stand at the threshold, and tell me what you see.",
        "Supports gone. Ore everywhere. And the foreman's lamp, still lit. I knew it.", None,
        requires_quests=["sps_mine_kobolds"]))
    A(Q("sps_gnawbone", "Gnawbone the Foreman", HOB, SPS, 18, 18, "sps_mine",
        "Gnawbone was the kobold foreman of Deep Elem, and the only one that kept his job after the collapse. He wears the "
        "company's hard-hat and gives orders in a tongue Hobart half-remembers. He has to go.",
        [boss("Gnawbone the Foreman", SPS)],
        "Deep in the mine, among the carts. He's the one with the bone pick and the helmet.",
        "My old foreman's helmet... on a kobold. I'll take it back. Thank you.", None,
        requires_quests=["sps_mine_kobolds"]))

    # ============================================================================================ PYREWOOD VILLAGE
    BRA = "sp_pyre_hearthwarden"
    A(Q("sps_pyre_ambush", "The Pyrewood Ambush", BRA, SPS, 17, 18, "sps_pyre",
        "The worgen of Pyrewood Village were people once, and ambush from the treeline is still how they hunt. Hearthwarden Brand wants "
        "the ambushers and the ferals thinned before the dead come to the village next.",
        [kill("Worgen Ambusher", 6, zone=SPS), kill("Feral Worgen", 5, zone=SPS)],
        "The village streets and the treeline. They hunt in packs. Don't be alone.",
        "Fewer fangs in the dark. I'll almost let myself breathe.", None))
    A(Q("sps_pyre_cultists", "The Ashen Cult", BRA, SPS, 18, 19, "sps_pyre",
        "A cult has taken up in Pyrewood's burned houses, casting spells over the dead hearths. Brand does not know which god "
        "they pray to. He knows it answers.",
        [kill("Pyrewood Cultist", 6, zone=SPS)],
        "The burned houses on the east side. They chant. They don't stop for you.",
        "Quiet at last. Whatever answered them has gone quiet too.", None,
        requires_quests=["sps_pyre_ambush"]))
    A(Q("sps_pyre_sigils", "The Cult's Sigils", BRA, SPS, 18, 19, "sps_pyre",
        "Each cultist carries an iron sigil, stamped with a cipher Brand doesn't recognise. He wants five, for a scholar in the "
        "Undercity who might.",
        [fetch("sps_cult_sigil", 5)],
        "From the cultists. Iron discs on cords. Don't read the cipher aloud.",
        "I'll have them sent to Sennarath in the Undercity. If anyone can read them, she can.", None,
        requires_quests=["sps_pyre_ambush"]))
    A(Q("sps_pyre_hall", "The Hall at the Heart", BRA, SPS, 18, 19, "sps_pyre",
        "Pyrewood Hall stands at the north end of the village, its roof half-gone and its doors barred from the inside. Brand wants "
        "someone to stand at its steps and tell him what's behind them.",
        [explore(SPS, 88, 87, 4)],
        "The Hall, at the north end of the green. Don't go in. Look at the doors.",
        "Barred from the inside, as I feared. Whatever's in there wants to stay.", None,
        requires_quests=["sps_pyre_ambush"]))
    A(Q("sps_godfrey", "Lord Godfrey's Remnant", BRA, SPS, 19, 19, "sps_pyre",
        "What stands in Pyrewood Hall is what the lord of the village left behind: a ghost in a noble's coat, pistol in one hand "
        "and cane in the other, still giving the dead orders.",
        [boss("Lord Godfrey's Remnant", SPS)],
        "Inside the Hall. Mind the pistol. It never misses, and it never reloads.",
        "He was a decent man, once. Not a good one. A decent one. That's more than most. Thank you.", None,
        requires_quests=["sps_pyre_ambush", "sps_pyre_cultists"]))

    # ============================================================================================ BERARD'S TALON
    HAS = "sp_talon_trapper"
    A(Q("sps_talon_stalkers", "Stalkers on the Hill", HAS, SPS, 17, 18, "sps_talon",
        "Berard's Talon is a ridge of broken stone above the old keep road. Crag stalkers hunt its slopes, and wraiths drift "
        "along its crest. Trapper Hask wants both cleared, so he can finally set his lines.",
        [kill("Crag Stalker", 6, zone=SPS), kill("Talon Wraith", 5, zone=SPS)],
        "The hill west of the keep road. Stalkers on the rocks, wraiths on the crest.",
        "The lines can go out tonight. Thank you.", None))
    A(Q("sps_talon_tokens", "Grave-Tokens", HAS, SPS, 18, 19, "sps_talon",
        "The wraiths of Berard's Talon carry small tokens of the dead - coins, buttons, rings - clutched in spectral fingers. "
        "Hask wants five, and plans to return them to the graves they came from.",
        [fetch("sps_grave_token", 5)],
        "Off the wraiths. Don't hold them too long. They remember.",
        "Five graves to visit. It'll take all winter. Good. I'm not in a hurry.", None,
        requires_quests=["sps_talon_stalkers"]))
    A(Q("sps_berard", "Berard the Forgotten", HAS, SPS, 19, 19, "sps_talon",
        "The hill is named for Berard, a man whose face no longer appears in any record. He walks the ridge each night and "
        "no one remembers what he is looking for.",
        [boss("Berard the Forgotten", SPS)],
        "On the crest, under the old stone ring. He moves like a man trying to remember.",
        "Maybe he'll rest now. Maybe someone will remember his face. Thank you.", None,
        requires_quests=["sps_talon_stalkers"]))

    # ============================================================================================ BEREN'S PERIL
    RYN = "sp_peril_packbreaker"
    A(Q("sps_peril_pack", "Break the Pack", RYN, SPS, 18, 19, "sps_peril",
        "A worgen pack has dug in under the hills of Beren's Peril, led by packmasters who've learned to hold a line. Packbreaker "
        "Rynn wants the line broken, and the stalkers that run in front of it.",
        [kill("Peril Packmaster", 6, zone=SPS), kill("Feral Worgen Stalker", 5, zone=SPS)],
        "The hills south-east of Pyrewood. They hold the high ground. Don't give them the high ground.",
        "That's the pack broken. A good start. The alpha next.", None))
    A(Q("sps_peril_teeth", "Teeth of the Packmasters", RYN, SPS, 19, 20, "sps_peril",
        "A packmaster wears the teeth of every rival he has bested. Rynn wants five of those necklaces, to show the Dark Lady what "
        "the Peril has been chewing on.",
        [fetch("sps_alpha_tooth", 5)],
        "From the packmasters. They wear the teeth on their necks. Don't pull too hard.",
        "That's a lot of rivals. I want the one who gave them the idea.", None,
        requires_quests=["sps_peril_pack"]))
    A(Q("sps_bloodmaw", "Bloodmaw the Alpha", RYN, SPS, 20, 20, "sps_peril",
        "At the heart of the Peril lives Bloodmaw, a grey-muzzled alpha who has outlived every challenger. He wears a collar of "
        "wolf teeth and a scar down his flank, and he is the only reason the pack still holds.",
        [boss("Bloodmaw the Alpha", SPS)],
        "At the den, deep in the hills. He isn't hiding. He's waiting.",
        "A pack without an alpha scatters. We'll see how many come back. Thank you.", None,
        requires_quests=["sps_peril_pack"]))

    # ============================================================================================ THE GREYMANE WALL
    TEA = "sp_wall_corporal"
    A(Q("sps_wall_breakers", "Wallbreakers", TEA, SPS, 18, 19, "sps_wall",
        "Worgen throw themselves at the Greymane Wall every night, and the dead of the wall rise to meet them. "
        "Corporal Teague wants the breakers thinned, and the ghosts calmed, if either can be done.",
        [kill("Wallbreaker Worgen", 6, zone=SPS), kill("Wall Wraith", 5, zone=SPS)],
        "The long wall, along the southern edge. They come in waves. Meet them one at a time.",
        "The wall holds. Another night. Thank you.", None))
    A(Q("sps_wall_seals", "Seals of the Greymane Guard", TEA, SPS, 19, 20, "sps_wall",
        "The ghosts of the Wall Guard carry the seals they swore their oaths on. Teague wants five, to lay on the shut gate "
        "when the next Forsaken relief arrives.",
        [fetch("sps_gilnean_seal", 5)],
        "From the wraiths. Iron seals, stamped with a lion. Handle gently.",
        "They'll rest easier on the gate than on the dead. Thank you.", None,
        requires_quests=["sps_wall_breakers"]))
    A(Q("sps_shut_gate", "The Shut Gate", TEA, SPS, 19, 20, "sps_wall",
        "The great gate in the Greymane Wall has not opened since the night Gilneas shut itself off from the world. Teague wants "
        "someone to stand before it and report whether there's any sign of change.",
        [explore(SPS, 120, 148, 6)],
        "The gate's in the middle of the wall. Don't touch it. Don't knock. Just look.",
        "Not a hair of change. Good. I'd rather the thing stay closed than learn what's behind it.", None,
        requires_quests=["sps_wall_breakers"]))
    A(Q("sps_wall_warden", "The Wall-Warden", TEA, SPS, 20, 20, "sps_wall",
        "The ghost of the Wall's last commander still walks the parapet, enforcing a sentence that was never lifted: nothing in, "
        "nothing out. The Forsaken cannot pass him either. He has to be put down.",
        [boss("Gilnean Wall-Warden", SPS)],
        "Along the parapet, by the gate. He challenges everyone. He means it.",
        "He was doing his duty. I'm sorry it came to this. I'm sorry for all of us.", None,
        requires_quests=["sps_wall_breakers"]))

    # ============================================================================================ AMBERMILL
    HSK, ORS = "sp_amber_millwright", "sp_amber_magister"
    A(Q("sps_amber_ghosts", "Ghosts at the Mill", HSK, SPS, 18, 19, "sps_amber",
        "Ambermill was a Dalaran lumber village until the plague took its mages. Their ghosts stayed behind, along with the "
        "wards they set on the mill. Millwright Haskell can't tell which are guarding the place, and which are guarding themselves.",
        [kill("Ambermill Ghost-Mage", 6, zone=SPS), kill("Ambermill Warden", 5, zone=SPS)],
        "The village and the mill-yard. The ghost-mages cast. The wardens hit.",
        "Fewer ghosts, fewer wards. I might get a plank cut before dark.", None))
    A(Q("sps_amber_resin", "Resin of the Wardens", HSK, SPS, 19, 20, "sps_amber",
        "The mill's wardens are made of amber resin, hardened by magic. Haskell wants six lumps. 'Fuel for the stove,' he says, and "
        "then admits it's for the stove he plans to build in a house that isn't there any more.",
        [fetch("sps_amber_resin", 6)],
        "From the wardens. Warm to the touch. Don't lick them.",
        "Six lumps. That's my winter. Thank you. Truly.", None,
        requires_quests=["sps_amber_ghosts"]))
    A(Q("sps_amber_waygate", "The Old Waygate", ORS, SPS, 19, 20, "sps_amber",
        "Magister Orsolo studied the Ambermill waygate for forty years. It leads somewhere, and he has finally decided he does not "
        "want to know where. He wants someone to stand at the gate and tell him what it looks like now.",
        [explore(SPS, 138, 91, 4)],
        "East of the mill, below the cliff. Stand at its feet. Don't touch the runes.",
        "Violet. Brighter than it was. So it's still listening. Thank you. I'll keep my distance.", None,
        requires_quests=["sps_amber_ghosts"]))
    A(Q("sps_quillfire", "Magister Quillfire", ORS, SPS, 20, 20, "sps_amber",
        "Orsolo's colleague, Magister Quillfire, never left the tower. Now he casts spells on anyone who nears it, and the waygate "
        "answers him. Orsolo cannot bring himself to do it, and asks that you do.",
        [boss("Magister Quillfire", SPS)],
        "Near the waygate. He writes in the air. Don't read it.",
        "He was a gentle man, and a better mage than I. I'm sorry it fell to you.", None,
        requires_quests=["sps_amber_ghosts"]))

    # ============================================================================================ THE DECREPIT FERRY
    GAE, PIM = "sp_ferryman", "sp_ferry_dockhand"
    A(Q("sps_ferry_deckhands", "Waterlogged Crew", GAE, SPS, 16, 17, "sps_ferry",
        "The ferry's crew drowned the night the boat went down, and walked back up the lake bed the next morning. They work the "
        "pier from dusk to dawn and will not let Gael sleep. He asks that you send them back.",
        [kill("Drowned Deckhand", 6, zone=SPS), kill("Carrion Bird", 3, zone=SPS)],
        "On and around the pier. The deckhands hold the boat-hooks. The birds hold grudges.",
        "A quieter dock. I may even sleep.", None))
    A(Q("sps_ferry_crates", "Lost Cargo", PIM, SPS, 17, 18, "sps_ferry",
        "Cargo crates wash up on the shore at all hours, and the deckhands guard them as if they were gold. Dockhand Pim wants "
        "five of them, delivered to the Rear Guard. 'If it's gold,' she says, 'the Dark Lady should have it.'",
        [fetch("sps_cargo_crate", 5)],
        "Off the deckhands. They carry them as if by instinct. Five crates.",
        "It's mostly rotten fish. But five of them sealed with Dalaran wax? Someone's lost something.", None,
        requires_quests=["sps_ferry_deckhands"]))
    A(Q("sps_ferry_ticket", "A Ticket to Somewhere", "item:sps_ferry_ticket", SPS, 16, 18, "sps_ferry",
        "A ticket stub for the Decrepit Ferry, stamped with a date from the last winter before the plague. The destination is "
        "Fenris Isle. Gael may remember who it was sold to.",
        [deliver("sps_ferry_ticket", "Bring the ticket stub to Ferryman Gael")],
        "The ferryman, at the pier. He keeps every stub.",
        "Last passenger I carried to the isle. I never saw him come back.", None,
        turn_in_npc_id=GAE))
    A(Q("sps_ferryman", "The Drowned Ferryman", GAE, SPS, 18, 18, "sps_ferry",
        "The first ferryman drowned with the boat, and rose to take it back. He steers at night, and his passengers are not "
        "the sort who pay. Gael wants him put in his grave.",
        [boss("Drowned Ferryman", SPS)],
        "On the pier head. He leans on his oar like it's holding him up.",
        "He taught me the trade. He deserves a better ending than that. Thank you.", None,
        requires_quests=["sps_ferry_deckhands"]))
    A(Q("sps_fenris_crossing", "The Crossing to Fenris", GAE, SPS, 18, 18, "sps_ferry",
        "With the old ferryman gone, Gael has agreed to take passengers to Fenris Isle again. He says he'll go as far as the "
        "pier head and no farther, and wants you to check the moorings.",
        [explore(SPS, 149, 44, 2)],
        "The end of the pier. The boat'll take you across when you're ready.",
        "Moorings hold. The lake's flat. The isle's waiting, if you've the stomach.", None,
        requires_quests=["sps_ferryman"]))

    # ============================================================================================ SHADOWFANG KEEP GATE
    MAR = "sp_sfk_gatekeeper"
    A(Q("sps_sfk_pickets", "Pickets at the Portcullis", MAR, SPS, 19, 20, "sps_wall",
        "Ghouls and stalkers crowd the keep road, drawn by whatever Arugal keeps inside. Gatekeeper Marl wants the road clear "
        "before the next party goes in.",
        [kill("Rotting Ghoul", 5, zone=SPS), kill("Feral Worgen Stalker", 4, zone=SPS)],
        "Near the gate. Ghouls on the road, stalkers in the trees.",
        "A clear road. Whatever you're walking into, you'll walk in with fresh boots.", None))
    A(Q("sps_sfk_forecourt", "The Keep's Forecourt", MAR, SPS, 19, 20, "sps_wall",
        "Marl has stood at Shadowfang's gate for years and cannot say whether the howling has grown louder or he has grown "
        "used to it. He wants someone to stand in the forecourt and tell him honestly.",
        [explore(SPS, 49, 148, 4)],
        "In front of the portcullis. Stand, listen, report.",
        "Louder. I thought so. Gods help whoever's inside.", None))

    # ============================================================================================ THE LINKEN GATE (finale)
    A(Q("sps_dallow_reckoning", "The March's Reckoning", DAL, SPS, 19, 20, "sps_camp",
        "Five reports lie on Dallow's table: the Deathguard Captain is down, the Bloated One is down, Lord Godfrey's Remnant is down, "
        "Berard rests, and Bloodmaw's pack has scattered. The March has not seen five victories in a row since the war.",
        [explore(SPS, 70, 48, 4)],
        "Come back to Valgan's Field. Stand where the March can see you.",
        "Five victories. A medal for each, if we had medals. Instead, take this. The March doesn't forget.", None,
        mult=1.6, turn_in_npc_id=DAL,
        requires_quests=["sps_deathguard_captain", "sps_bloated_one", "sps_godfrey", "sps_berard", "sps_bloodmaw"]))
    return Z


def sepulcher():
    Z = []
    A = Z.append
    VANE, DARNE, YS, WR, CASS, ELL, MOL, HER, OSK, MOUR, SOUL = (
        "sepulcher_commander", "sepulcher_relic_hunter", "sepulcher_bone_carver", "sepulcher_reagent_seller",
        "sepulcher_gravestone_reader", "sepulcher_tomb_keeper", "sepulcher_crypt_guard", "sepulcher_hermit",
        "sepulcher_pilgrim", "sepulcher_mourner", "sepulcher_lost_soul")
    A(Q("sep_keep_tour", "Know the Keep", VANE, SEP, 13, 14, "sep_keep",
        "Commander Vane does not give orders to people who cannot find the latrines. Walk the terraces - the lower court, the middle "
        "terrace and the graveyard wing - and report back. Do not touch anything that is not yours.",
        [explore(SEP, 44, 56, 6), explore(SEP, 44, 36, 5), explore(SEP, 13, 33, 5)],
        "Three stops: the court inside the gate, the middle terrace, and the Raven Hill graveyard to the west.",
        "You didn't fall off anything. That's a better start than most.", None))
    A(Q("sep_woods_cull", "The Woods Below", VANE, SEP, 13, 14, "sep_keep",
        "The Keep sits above the pines, and the pines are full of worg and the leavings of the plague. Vane wants the approach to "
        "the gate kept short of anything with teeth.",
        [kill("Worg Prowler", 6, zone=SPN), kill("Feral Ghoul", 5, zone=SPN)],
        "In the woods south of the Keep, along the road you walked in on.",
        "Fewer teeth on the approach. I'll note it in the ledger.", None,
        requires_quests=["sep_keep_tour"]))
    A(Q("sep_dispatch", "A Dispatch for the Rear Guard", VANE, SEP, 14, 15, "sep_keep",
        "Vane has written to Captain Vesk of the Rear Guard. It is three lines long. He would like it delivered by someone who "
        "will not read it, and, failing that, someone who will not remember it.",
        [deliver("sep_dispatch", "Deliver Vane's dispatch to Captain Vesk at the Rear Guard")],
        "North along the road to the Rear Guard. Vesk is at the gate.",
        "Three lines. Of course. It's rude, and exactly right.", None,
        turn_in_npc_id="sp_rg_captain", requires_quests=["sep_keep_tour"],
        grant_items=carry("sep_dispatch", "Vane's Dispatch", "A single sheet, folded thrice and sealed with the Keep's black wax.")))
    A(Q("sep_relic_shards", "Shards of the Faithful", DARNE, SEP, 14, 15, "sep_keep",
        "Relic Hunter Darne pays for grave-goods, and the skeletal groundskeepers of Raven Hill carry the best of them: ring-shards, "
        "buckle-bone, whatever they were buried with. She wants six, intact.",
        [fetch("sep_relic_shard", 6)],
        "From the groundskeepers at Raven Hill, to the south. Don't chip them.",
        "These are good. Old and honest. The collectors in Undercity will weep.", None))
    A(Q("sep_marrow", "Marrow Work", YS, SEP, 14, 15, "sep_keep",
        "Yseult carves bone into combs, buttons and, occasionally, regret. Risen husks have the best marrow, she says, and they "
        "never complain about the harvest.",
        [fetch("sep_bone_marrow", 6)],
        "Risen husks, wherever the field is thickest. Six dry marrow-bones.",
        "Dry and pale. I could carve a chapel out of these. I'll settle for a comb.", None))
    A(Q("sep_wasp_stings", "Stings for the Apothecary", WR, SEP, 15, 16, "sep_keep",
        "Windfall wasps in Malden's Orchard are full of a venom Wrenn has been trying to buy for years. The orchard won't sell it. "
        "The wasps won't either. Wrenn would like it taken.",
        [fetch("sep_wasp_sting", 6)],
        "Malden's Orchard, north of the Raven Hill road. The stings are on the abdomen. Handle with tongs.",
        "Six stings and no stinging. You have steadier hands than most.", None))
    A(Q("sep_stone_names", "Names on the Stones", CASS, SEP, 14, 15, "sep_keep",
        "Reader Cass reads the stones of the Raven Hill wing. Most are blank, rubbed smooth by rain and by something that rubs "
        "back. She wants three clusters visited and the weeds pulled away. 'Read them aloud,' she says. 'It helps.'",
        [explore(SEP, 8, 28, 4), explore(SEP, 16, 29, 4), explore(SEP, 11, 38, 4)],
        "The graveyard wing, west of the middle terrace. Three clusters of stones.",
        "Three more names. I'll write them on the wall, so they stay.", None))
    A(Q("sep_ellowyn_sleepers", "Sleepers That Won't", ELL, SEP, 15, 16, "sep_keep",
        "The tomb-keeper of the chapel yard counts sleepers each dusk. Some have stopped lying down. Groundskeepers and husks both "
        "wander from the Raven Hill plots in search of a bed that isn't theirs.",
        [kill("Skeletal Groundskeeper", 6, zone=SPN), kill("Risen Husk", 5, zone=SPN)],
        "At Raven Hill, south of the Keep. Send them back where they belong.",
        "Fewer wanderers. I'll sleep better. Metaphorically.", None))
    A(Q("sep_gate_crows", "Crows at the Gate", MOL, SEP, 14, 15, "sep_keep",
        "Crypt Guard Molsen is tired of the crows. They pick at the Keep's banners, steal buttons off his coat, and one of them has "
        "learned to open the gate-latch.",
        [kill("Blighted Crow", 6, zone=SPN), kill("Dead Field Harrower", 4, zone=SPN)],
        "The Dead Field, east of the road. The harrowers feed them; thin both.",
        "The latch-crow? Dead. Good. I owe you a drink I can't taste.", None,
        requires_quests=["sep_keep_tour"]))
    A(Q("sep_hermit_oil", "The Hermit's Oil", HER, SEP, 15, 16, "sep_keep",
        "The Hermit has not left his lean-to since the Plague. His lamp is nearly dry. Spider-fat burns clean, he says, and he "
        "cannot hunt it himself, because spiders have opinions about hermits.",
        [fetch("sep_spider_fat", 5)],
        "Silverpine spiders in the Skittering Dark. Five clean glands. Tell no one I asked.",
        "I can read again. Not that there is much I wish to read.", None))
    A(Q("sep_osk_road", "The Pilgrim's Road", OSK, SEP, 14, 15, "sep_keep",
        "Osk walks between the Keep and Tirisfal every autumn, ostensibly to pray. He has no idea who he is praying to. He asks that "
        "the road between be made less murderous.",
        [kill("Silverpine Spider", 5, zone=SPN), kill("Corrupted Treant", 2, zone=SPN)],
        "The woods north and east of the Keep. Spiders and treants, mainly.",
        "A quieter road. I'll walk it once more before the snow.", None))
    A(Q("sep_cracked_locket", "A Cracked Locket", "item:sep_cracked_locket", SEP, 14, 16, "sep_keep",
        "Taken from a skeletal groundskeeper's rib-cage: a cracked silver locket, with a single pressed flower inside. The one at "
        "the Keep who wanders the lower court without a name might know it.",
        [deliver("sep_cracked_locket", "Bring the locket to Something That Was Once Named in the lower court")],
        "The lower court of the Sepulcher. A figure who answers to nothing in particular.",
        "...yes. That one. Thank you. I think... I think I had a daughter.", None,
        turn_in_npc_id=SOUL))
    A(Q("sep_wreaths", "Wreaths for the Quiet", MOUR, SEP, 14, 15, "sep_keep",
        "The Mourner weaves wreaths from what the dead leave behind. Risen farmhands carry wilted sprays in their pockets - "
        "last year's offerings, never delivered. She wants six.",
        [fetch("sep_wilted_wreath", 6)],
        "The farmhands of Olsen's Farthing, south of the Keep.",
        "Even wilted, they mean something. I'll lay them where they were meant to go.", None))
    return Z


# ---- fetch items + drop-started items -------------------------------------------------------------------------------------------
FETCH_DROPS = {         # item_id: (name, description, [(creature, chance)])
    "sp_venom_gland": ("Silverpine Venom Gland", "A greenish gland, still faintly pulsing.", [("Silverpine Spider", 0.40)]),
    "sp_seed_sack": ("Farthing Seed Sack", "A small, singed sack of wheat seed.", [("Risen Farmhand", 0.40)]),
    "sp_grave_moss": ("Grave-Moss Clipping", "Grey-green moss, thick with bone dust.", [("Grave Moss Creeper", 0.42)]),
    "sp_harrower_straw": ("Harrower's Straw Charm", "A sewn straw charm, stitched in a wife's careful hand.", [("Dead Field Harrower", 0.42)]),
    "sp_rotapple_core": ("Rotapple Core", "A black, heavy seed-core, faintly warm.", [("Orchard Shambler", 0.42)]),
    "sp_slitherer_fang": ("Slitherer Fang", "A curved, wet fang. Handle with tongs.", [("Rot Hide Slitherer", 0.42)]),
    "sp_skitter_sac": ("Skitterer Egg Sac", "A silk-wrapped egg sac, warm to the touch.", [("Venomfang Skitterer", 0.42)]),
}
FETCH_DROPS.update({
    "sep_relic_shard": ("Grave-Goods Shard", "A ring-shard of tarnished silver, still warm from burial.", [("Skeletal Groundskeeper", 0.40)]),
    "sep_bone_marrow": ("Dry Marrow-Bone", "A pale, dry shin-bone, ideal for carving.", [("Risen Husk", 0.40)]),
    "sep_wasp_sting": ("Windfall Wasp Sting", "A glistening black barb, still wet.", [("Windfall Wasp", 0.42)]),
    "sep_spider_fat": ("Silverpine Spider Fat", "A pale, waxy gland. Burns clean.", [("Silverpine Spider", 0.42), ("Giant Spider", 0.42)]),
    "sep_wilted_wreath": ("Wilted Offering", "A spray of flowers that never reached its grave.", [("Risen Farmhand", 0.42)]),
})
FETCH_DROPS.update({
    "sps_deserter_tag": ("March Deserter's Tag", "An iron tag stamped with a March number.", [("Field Deserter", 0.45)]),
    "sps_wight_bone": ("Battlefield Long-Bone", "A long bone, picked clean. Someone's arm, once.", [("Battlefield Wight", 0.42)]),
    "sps_wolf_pelt": ("Diseased Wolf Pelt", "A mangy pelt. It will clean up, mostly.", [("Diseased Wolf", 0.42)]),
    "sps_quilt_scrap": ("Bucklebree Quilt Scrap", "A square of hand-stitched quilt, stained with barn straw.", [("Barn Ghoul", 0.42)]),
    "sps_marsh_sample": ("Sealed Marsh-Gas Bladder", "A swollen, foul bladder. It wobbles.", [("Bloated Corpse", 0.42)]),
    "sps_miner_lamp": ("Company Mining Lamp", "A battered brass lamp, stamped with the Deep Elem mark.", [("Mine Shambler", 0.42)]),
    "sps_cult_sigil": ("Pyrewood Cult Sigil", "A dull iron disc etched with a cipher you'd rather not read.", [("Pyrewood Cultist", 0.42)]),
    "sps_grave_token": ("Wraith-Held Token", "A small keepsake, cold as a gravestone.", [("Talon Wraith", 0.42)]),
    "sps_alpha_tooth": ("Packmaster's Tooth-Necklace", "A string of worgen teeth, each one a rival.", [("Peril Packmaster", 0.40)]),
    "sps_gilnean_seal": ("Wall Guard's Seal", "A lion-stamped iron seal, rubbed smooth.", [("Wall Wraith", 0.42)]),
    "sps_amber_resin": ("Warden's Amber Resin", "A warm lump of hardened resin.", [("Ambermill Warden", 0.42)]),
    "sps_cargo_crate": ("Waterlogged Cargo Crate", "A small crate, sealed with Dalaran wax.", [("Drowned Deckhand", 0.42)]),
})
STARTER_DROPS = {      # item_id: (name, description, quest_id, [(creature, chance)])
    "sp_farmhand_locket": ("Farmhand's Silver Locket", "A small silver locket on a broken chain. The clasp is stuck.",
                           "spn_farmhand_locket", [("Risen Farmhand", 0.14)]),
    "sp_crow_ring": ("Tarnished Gold Ring", "A gold band, pecked loose from a nest. Inscribed on the inside.",
                     "spn_df_ring", [("Blighted Crow", 0.14)]),
}
STARTER_DROPS.update({
    "sep_cracked_locket": ("Cracked Silver Locket", "A silver locket with a single pressed flower inside.",
                           "sep_cracked_locket", [("Skeletal Groundskeeper", 0.14)]),
    "sps_deserter_letter": ("Deserter's Sealed Letter", "A letter addressed to someone in the Undercity. The seal is unbroken.",
                            "sps_deserter_letter", [("Field Deserter", 0.14)]),
    "sps_ferry_ticket": ("Decrepit Ferry Ticket", "A water-stained ticket stub for a crossing to Fenris Isle.",
                         "sps_ferry_ticket", [("Drowned Deckhand", 0.14)]),
})


def _finish(Z):
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
        for r in q.get("requires_quests", []):
            assert r in ids or r.startswith(("sp_", "ets_", "etc_", "spn_", "sps_", "sep_", "fen_")), (q["quest_id"], r)
    return out, ids


def main():
    out_n, ids_n = _finish(north())
    OUT_N.write_text(json.dumps({"quests": out_n}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_s, ids_s = _finish(south())
    OUT_S.write_text(json.dumps({"quests": out_s}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_p, ids_p = _finish(sepulcher())
    OUT_SEP.write_text(json.dumps({"quests": out_p}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ids = ids_n | ids_s | ids_p

    # the old one-line quests are replaced by this pass
    fp = ROOT / "data/quests/forsaken_lands.json"
    fd = json.loads(fp.read_text(encoding="utf-8"))
    old = {"sp_raven_hill_risen", "sp_forsaken_watchman", "sp_pyrewood_worgen", "sp_lord_godfreys_remnant",
           "sp_shadowspring_bog", "sp_muckmaw",
           "sp_forsaken_march", "sp_deathguard_captain", "sp_rotting_marshes", "sp_the_bloated_one"}
    fd["quests"] = [q for q in fd["quests"] if q["quest_id"] not in old]
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for item_id, (name, desc, srcs) in FETCH_DROPS.items():
        for creature, chance in srcs:
            lst = drops.setdefault(creature, [])
            lst[:] = [d for d in lst if d["item_id"] != item_id]
            lst.append(dict(item_id=item_id, name=name, category="quest", description=desc, chance=chance))
    for item_id, (name, desc, qid, srcs) in STARTER_DROPS.items():
        assert qid in ids, qid
        for creature, chance in srcs:
            lst = drops.setdefault(creature, [])
            lst[:] = [d for d in lst if d["item_id"] != item_id]
            lst.append(dict(item_id=item_id, name=name, category="quest", description=desc, chance=chance, starts_quest=qid))
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"silverpine quests: north {len(out_n)}, south {len(out_s)}, sepulcher {len(out_p)}")


if __name__ == "__main__":
    main()
