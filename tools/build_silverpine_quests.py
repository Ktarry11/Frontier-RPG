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
DROPS = ROOT / "data/creatures/quest_drops.json"
SPN = "silverpine_north"

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

# ---- level tables (Undercity hub scale, +80 xp / +300 gold per level) ----------------------------------------------------------
XP = {11: 600, 12: 680, 13: 760, 14: 840, 15: 920, 16: 1000, 17: 1080}
GOLD = {11: 2700, 12: 3200, 13: 3600, 14: 3900, 15: 4200, 16: 4500, 17: 4800}


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
        [kill("Worg Prowler", 8, zone=SPN), kill("Feral Ghoul", 6, zone=SPN)],
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
        [kill("Farthing Hound", 8, zone=SPN), kill("Risen Farmhand", 6, zone=SPN)],
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
        [kill("Risen Husk", 8, zone=SPN)],
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
        [kill("Blighted Crow", 10, zone=SPN)],
        "The Dead Field, east of the Trunk Road. Blighted crows. Aim for the eyes. They notice.",
        "Fewer eyes on me, finally. I'm in your debt. Take a bow, if you like. I won't use it.", None))
    A(Q("spn_df_harrowers", "Harrowers in the Furrows", TOB, SPN, 13, 14, "spn_field",
        "Tobb the farmhand was the last to leave the Dead Field and the first to come back. He sleeps in the barn. He says the "
        "scarecrows walk at night, and he's tired of watching them from the loft.",
        [kill("Dead Field Harrower", 8, zone=SPN)],
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
        [kill("Corrupted Treant", 5, zone=SPN), kill("Feral Ghoul", 6, zone=SPN)],
        "The woods around the gate. Treants, ghouls. Anything that shuffles toward the door.",
        "The door stays closed to what should be kept out. Welcome inside, whenever you like.", None))

    # ============================================================================================ MALDEN'S ORCHARD
    MAL = "sp_orchard_warden"
    A(Q("spn_orchard_blight", "The Blight in the Boughs", MAL, SPN, 14, 15, "spn_orchard",
        "Malden's Orchard has not borne fruit in years, but the trees still drop it: a brown, heavy windfall that moves on its own. "
        "The orchard-warden wants the shamblers cleared and the wasps that hive in the rot driven out.",
        [kill("Orchard Shambler", 8, zone=SPN), kill("Windfall Wasp", 8, zone=SPN)],
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
        [kill("Bog Beast", 6, zone=SPN), kill("Murky Crocolisk", 6, zone=SPN)],
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
        [kill("Venomfang Skitterer", 8, zone=SPN), kill("Giant Spider", 4, zone=SPN)],
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
STARTER_DROPS = {      # item_id: (name, description, quest_id, [(creature, chance)])
    "sp_farmhand_locket": ("Farmhand's Silver Locket", "A small silver locket on a broken chain. The clasp is stuck.",
                           "spn_farmhand_locket", [("Risen Farmhand", 0.14)]),
    "sp_crow_ring": ("Tarnished Gold Ring", "A gold band, pecked loose from a nest. Inscribed on the inside.",
                     "spn_df_ring", [("Blighted Crow", 0.14)]),
}


def main():
    Z = north()
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
            assert r in ids or r.startswith(("sp_", "ets_", "etc_")), (q["quest_id"], r)
    OUT_N.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n")

    # the old one-line North quests are replaced by this pass
    fp = ROOT / "data/quests/forsaken_lands.json"
    fd = json.loads(fp.read_text())
    old = {"sp_raven_hill_risen", "sp_forsaken_watchman", "sp_pyrewood_worgen", "sp_lord_godfreys_remnant",
           "sp_shadowspring_bog", "sp_muckmaw"}
    fd["quests"] = [q for q in fd["quests"] if q["quest_id"] not in old]
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n")

    dd = json.loads(DROPS.read_text())
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
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n")
    print(f"silverpine north quests: {len(out)}, items {sum(len(q['unique_item_defs']) for q in out)}")


if __name__ == "__main__":
    main()
