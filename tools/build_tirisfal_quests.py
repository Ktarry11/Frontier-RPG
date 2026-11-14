"""
Tirisfal quest pass (2026-10-22).  Idempotent.

    python3 tools/build_tirisfal_content.py && python3 tools/build_tirisfal_quests.py && python3 tools/sync_tirisfal_npcs.py

Writes data/quests/tirisfal.json (69 quests: Brill hub 17, Western Tirisfal 26, Eastern Tirisfal 26), removes the old
wt_* / et_* quests from forsaken_lands.json (they targeted the pre-rebuild subzones), adds the new NPCs to
ambient_npcs.json (positions come from the zone modules' NPC_POSITIONS via tools/sync_tirisfal_npcs.py) and the
fetch-item drops to data/creatures/quest_drops.json.  Updates Deathknell's dk_to_brill explore to Brill's new square.

NO ESCORTS.  Everything is kill / fetch / boss / explore.

GEOGRAPHY (matches the real Tirisfal map)
  Brill hub ........... High-street village; Deathguard Rennick at the square (46,44)
  Western Tirisfal .... Nightmare Vale (Corvin) | Cold Hearth Manor (Pell) | Whispering Shore (Quillon) | Crusader Outpost (Dessa)
                        Solliden Farmstead (Marren) | Stillwater Pond (Oswin) | Agamand Mills (Sorren) | Agamand Family Crypt (Halvard)
                        Garren's Haunt (Brask)
  Eastern Tirisfal .... Zeppelin Landing + Ruins of Lordaeron (Linnea) | Faol's Rest (Morvyn) | Brightwater Lake (Gunther)
                        Crusader's Outpost (Hallam) | Venomweb Vale (Ravel) | Balnir Farmstead (Edric)
                        Cult of the Damned Farm (Ysolde) | Scarlet Watch Post + North Coast (Hollowmere)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import kill, fetch      # noqa: E402
from tools.tirisfal_gear import reward_pack             # noqa: E402

OUT = ROOT / "data/quests/tirisfal.json"
OLD = ROOT / "data/quests/forsaken_lands.json"
DK_FILE = ROOT / "data/quests/deathknell.json"
NPCS = ROOT / "data/npcs/ambient_npcs.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
WT, ET, BR = "western_tirisfal", "eastern_tirisfal", "brill"
SC = "scourge_cave"

XP = {4: 250, 5: 340, 6: 400, 7: 460, 8: 500, 9: 560, 10: 620, 11: 720, 12: 820, 13: 910}
GOLD = {4: 550, 5: 850, 6: 1100, 7: 1500, 8: 1800, 9: 2100, 10: 2400, 11: 2700, 12: 3200, 13: 3600}


def k(target, n, zone):
    return kill(target, n, zone=zone)


def boss(target, zone):
    return dict(type="kill_boss", target=target, count=1, zone=zone)


def explore(zone, x, y, radius=6):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, exp=None, gold=None, **engine):
    """`engine` carries the quest-engine extras: requires_quests, turn_in_npc_id, grant_items (see world/quest.py)."""
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi if is_boss else hi - 1)
    rarity = "rare" if (is_boss and ilvl >= 10) else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=exp if exp is not None else int(XP[hi] * mult),
             reward_gold=gold if gold is not None else int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             rewards=reward_pack(qid, theme, ilvl, lo, rarity, 4 if is_boss else 3))
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def craft(recipe, label, n=1):
    return dict(type="craft", target=recipe, count=n, label=label)


def carry(item_id, name, desc):
    """grant_items for a quest that hands you something to carry."""
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=1)]}


def quests():
    Z = []
    A = Z.append

    # =====================================================================================================
    # BRILL - the hub
    # =====================================================================================================
    RENNICK, GUARD, WEX, GRAEL, HOLLIS = "brill_deathguard", "brill_guard", "brill_town_crier", "brill_apothecary_asst", "brill_gravedigger"
    MERYL, NETTLES, PRUIT, OHM, JOSS, ILV = ("brill_human_sympathizer", "brill_farmer", "brill_scarecrow_tender", "brill_bell_ringer",
                                              "brill_newly_risen_farmhand", "brill_beltelf_trader")
    A(Q("brl_wolves", "Wolves at the Door", RENNICK, BR, 6, 8, "vale",
        "Bleak Worgs have been trotting up the Deathknell road after dark. They haven't bitten anyone in Brill yet, which Rennick "
        "considers a stroke of luck and a warning. Thin the pack in Nightmare Vale before the luck runs out.",
        [k("Bleak Worg", 5, WT)],
        "Take the west road down to the Vale. Eight worgs. Bring me the count and I'll pretend I'm not worried.",
        "Eight? Good. Brill sleeps lighter than it admits. Take something from the crate.", "brl_nightmare"))
    A(Q("brl_nightmare", "Into the Nightmare Vale", RENNICK, BR, 7, 9, "vale",
        "Nobody has walked Nightmare Vale's lower road since the worgs came. Rennick wants someone to walk it end to end and "
        "report what is waiting at the bottom, because 'something' is a poor basis for a patrol roster.",
        [explore(WT, 86, 118, 6)],
        "South-west of the Cold Hearth road, past the Deathknell gate, the road goes into the trees. Walk it. Don't dawdle.",
        "So it's quiet down there. I like quiet less than you'd think. Good work.", None))
    A(Q("brl_glades", "Thin the Glades", GUARD, BR, 6, 8, "brill",
        "The Wretched Zombies that wander the glades west of Brill have started drifting toward the gate. They are slow and "
        "stupid and mean no harm, but the gate guard has a quota of corpses he is willing to step over.",
        [k("Wretched Zombie", 5, WT)],
        "Out along the road west. Zombies. Put eight of them down and I'll let you back in without a lecture.",
        "That's the road clear. I was getting a crick from all the stepping over.", None))
    A(Q("brl_news_landing", "Tidings from the Landing", WEX, BR, 7, 9, "landing",
        "Wexley prides himself on hearing everything first, and he has heard the Undercity zeppelin tower east of Brill is "
        "open for passengers. He has no way to confirm it. He would very much like you to go and look.",
        [explore(ET, 18, 99, 5)],
        "East along the high road, then south. The tower is a tangle of ropes and goblin curses. Go and tell me if it's real.",
        "Real! Real, and open for custom. I shall cry it from the steps. Thank you.", "brl_news_ruins"))
    A(Q("brl_news_ruins", "Word from the Ruins", WEX, BR, 9, 11, "ruins",
        "The Landing is one thing. The Ruins of Lordaeron, just south, are another: the old capital, gate to the Undercity, "
        "and full of rumours the town crier cannot afford to miss. Walk the approach and see who is still home.",
        [explore(ET, 12, 110, 6)],
        "South of the landing, along the road the Dark Lady took. Don't linger. The ghosts remember being important.",
        "The old throne's cold, then. Pity. It was a lovely rumour.", None))
    A(Q("brl_grael_pumpkins", "Blight Pumpkins", GRAEL, BR, 6, 8, "farm",
        "Assistant Grael needs the pumpkins the Solliden thrashers are growing: swollen, grey-green things that ferment into "
        "the Apothecary's best base for plague reagents. He will not go near them himself. The thrashers hit back.",
        [fetch("blighted_pumpkin", 5)],
        "The Grain Threshers in the Solliden fields carry them. Five, uncracked, please. I'm very particular about cracks.",
        "Perfectly foul. Look at the colour. Take something from the shelf, you've earned it.", "brl_grael_pearls"))
    A(Q("brl_grael_pearls", "Pearls from the Bay", GRAEL, BR, 7, 9, "shore",
        "The Vile Fin oracles on Whispering Shore wear salt-pearls the Apothecary can grind into a calming powder. Grael has "
        "no idea what the Vile Fins want them for, and not much interest in the answer.",
        [fetch("oracle_pearl", 5)],
        "North-west, where the bay meets the dead marsh. The little oracles. Five pearls, and don't scratch them.",
        "Lovely lustre. Ground fine, these'll keep a grave-robber asleep for a month. Take your pick.", "brl_grael_iceshard"))
    A(Q("brl_grael_iceshard", "Brightwater Ice", GRAEL, BR, 8, 10, "lake",
        "Brightwater Lake sheds shards of black ice no matter the weather, and the weeping shades that stalk its shore carry "
        "them like keepsakes. The Apothecary uses them for cold-fixing. Grael needs five.",
        [fetch("iceshard_fragment", 5)],
        "Eastern Tirisfal, Brightwater Lake. The shades and the drowned wretches carry fragments. Bring five, and gloves.",
        "Cold enough to hurt. Excellent. Your reward is on the third shelf. Do not touch the fourth.", None))
    A(Q("brl_hollis_robbers", "Fresh Graves, Empty", HOLLIS, BR, 8, 10, "haunt",
        "Gravedigger Hollis has been digging graves for thirty years, living and dead, and he knows when one's been robbed. "
        "Rot Hide gnolls up at Garren's Haunt are doing it, and they leave the bodies in the wrong places.",
        [k("Rot Hide Graverobber", 4, WT)],
        "The graverobbers use shovels. I recognise the shovels. They're mine. Put them in the ground.",
        "Six less. I'd say rest in peace, but they never earned it. Take your pick.", "brl_hollis_relics"))
    A(Q("brl_hollis_relics", "Returned to the Earth", HOLLIS, BR, 8, 10, "crypt",
        "Whatever the robbers and the crypt wights took, Hollis wants it back in the ground where it belongs: rings, "
        "seals, little carved relics from the Agamand family vault.",
        [fetch("grave_relic", 5)],
        "The wights in the Agamand crypt and the robbers at Garren's Haunt carry the best of it. Five relics, and no keeping any.",
        "All present. I'll bury them tonight with a proper word. Take something from the barrow.", None))
    A(Q("brl_meryl_orders", "A Brother in the Crusade", MERYL, BR, 7, 9, "outpost",
        "Meryl Ashdown has a brother in the Scarlet Crusade. She wants to know if he is still alive, still sane, or still "
        "listed. Convert orders from the Crusader Outpost might tell her. She will not ask what you do to get them.",
        [fetch("crusade_orders", 5)],
        "The Crusader Outpost west of the Solliden farms. The recruits carry their orders on them. Please. Five. And don't hurt him if you meet him.",
        "...He's on the roster. Alive, at least. Thank you. I won't forget this. Take something. It was his.", None))
    A(Q("brl_nettles_crows", "Crows Over Brill", NETTLES, BR, 6, 8, "farm",
        "Old Farmer Nettles swears the duskbats over the glades are the crows that used to eat his barley, and that they're "
        "still after it. Nothing grows, but he insists on the principle.",
        [k("Mangy Duskbat", 5, WT)],
        "Out in the glades, the big grey ones. They've had my crop and my patience. Eight of them, if you please.",
        "Eight. I'll hang them on the fence. It's what you do. Take some of the old tack.", None))
    A(Q("brl_pruit_straw", "Straw and Sorrow", PRUIT, BR, 6, 8, "farm",
        "Pruit tends the scarecrows that guard Brill's plots. The Rotting Dead that stumble in from the glades keep knocking "
        "them down and, worse, leaving their own shapes on the posts. He wants them cleared.",
        [k("Rotting Dead", 4, WT)],
        "Seven, and don't bring them back. I'll make do with straw.",
        "Straw's easier to stand up than they are. Thank you, friend. Take what you need.", None))
    A(Q("brl_ohmsted_toll", "A Toll for the Drowned", OHM, BR, 8, 10, "lake",
        "The bell-ringer rings once a day for those lost at Brightwater Lake. Lately the Drowned Wretches ring back, from "
        "the water. He wants them quiet.",
        [k("Drowned Wretch", 4, ET)],
        "East past Brill, the big lake on the north side. They rise at dusk and wail. Seven, please.",
        "Quieter, I think. Or I've gone deaf. Either way, thank you.", "brl_ohmsted_shades"))
    A(Q("brl_ohmsted_shades", "Silence the Weeping", OHM, BR, 8, 10, "lake",
        "The Weeping Shades answer the toll with their own. It is the worst sound in Tirisfal. Ohmsted would like them "
        "gone, or at least discouraged.",
        [k("Weeping Shade", 4, ET)],
        "Same lake. The shades. They're rather high-handed about it. Six, if you can stomach it.",
        "I can hear the bell again. It's a lovely sound, if you're me.", None))
    A(Q("brl_joss_home", "The Old Homestead", JOSS, BR, 9, 11, "balnir",
        "Farmhand Joss remembers a stable, a farmhouse and a woman who made bread. He thinks it was south of the Brill road, "
        "near an overgrown paddock. He wants someone to walk the place and tell him whether it's still there.",
        [explore(ET, 38, 98, 6)],
        "Balnir, I think they called it. South of the east road. Look at the farmhouse for me and tell me what's left.",
        "The stable's still standing? That's... something. Thank you. I'll remember it better now.", None))
    A(Q("brl_ilvessa_cargo", "Lost Cargo", ILV, BR, 7, 9, "landing",
        "Trader Ilvessa's shipment never made it from the Undercity zeppelin to her stall. Scavengers picked it clean on the "
        "road, and she wants her crates back before the next shipment arrives and the scavengers get ideas.",
        [fetch("stolen_cargo", 6)],
        "Ragged scavengers along the Eastern road. They steal anything that glints. Six crates, please.",
        "My goods! Mostly my goods. Take your cut, darling.", None))

    # =====================================================================================================
    # WESTERN TIRISFAL
    # =====================================================================================================
    CORVIN, PELL, QUILLON, DESSA, MARREN, OSWIN, SORREN, HALVARD, BRASK = (
        "wt_vale_ranger", "wt_coldhearth_watcher", "wt_shore_fisher", "wt_outpost_scout", "wt_solliden_farmer",
        "wt_pond_hermit", "wt_agamand_envoy", "wt_crypt_keeper", "wt_garren_warden")
    # ---- Corvin: Nightmare Vale
    A(Q("wtv_wolves", "Howls in the Vale", CORVIN, WT, 5, 7, "vale",
        "Ranger Corvin Ashe walks the Vale's edge for the Deathguard, and the Bleak Worgs have been getting bolder. He "
        "needs the pack thinned before it learns to climb the road.",
        [k("Bleak Worg", 5, WT)],
        "They hunt in the dusk. Eight should keep them wary. Aim for the grey ones, they lead.",
        "That's quieter. Nobody ever thanks a ranger for what doesn't happen. I'm thanking you.", "wtv_crawlers"))
    A(Q("wtv_crawlers", "Crawling Things", CORVIN, WT, 5, 7, "vale",
        "Nightcrawlers burrow in the Vale's loam and snap at anyone who walks overhead. Corvin has lost two boots to them "
        "and more dignity than he cares to admit.",
        [k("Young Nightcrawler", 4, WT)],
        "Under the roots. You'll feel them before you see them. Seven, please, before they grow.",
        "Good. A man can walk again. Take a piece of the kit.", "wtv_needler"))
    A(Q("wtv_needler", "The Needler", CORVIN, WT, 6, 8, "vale",
        "A big old duskbat called Ressan the Needler nests above the Vale road. Needle-sharp teeth, a taste for ankles, "
        "and a flock that follows him. Corvin has had enough.",
        [boss("Ressan the Needler", WT), k("Mangy Duskbat", 2, WT)],
        "He's a brute, flies low, and screams. Clear his flock and then him. I'll watch from here, with my boots on.",
        "He's down. I can hear myself think. Well done. Take your pick.", None))
    # ---- Pell: Cold Hearth Manor
    A(Q("wt_manor_reapers", "Reapers at the Door", PELL, WT, 6, 8, "manor",
        "Watcher Pell has kept the Cold Hearth gate for a year and the reapers have never stopped coming. They come "
        "up out of the manor cellars with scythes and no manners.",
        [k("Manor Reaper", 5, WT)],
        "Eight, and be careful with the scythes. They've been sharpened since before you died.",
        "Eight. That's the first quiet watch in a month. Take something from the pile.", "wt_manor_dead"))
    A(Q("wt_manor_dead", "The Hall Fills Up", PELL, WT, 7, 9, "manor",
        "The reapers aren't the only thing in the hall. Zombies and Rotting Dead pour out of the grounds as if the manor "
        "were calling them home.",
        [k("Wretched Zombie", 4, WT), k("Rotting Dead", 2, WT)],
        "Clear the gardens. Zombies and the rotted ones. The sooner they stop coming, the sooner I stop watching.",
        "The gardens are empty. For now. Thank you. Your pick of the lot.", "wt_aldous"))
    A(Q("wt_aldous", "The Reaper-Lord", PELL, WT, 8, 9, "manor",
        "Reaper-Lord Aldous is what the manor's dead report to: a tall, scythe-armed wreck who thinks the hall is still "
        "his. Pell would like him to be wrong.",
        [boss("Reaper-Lord Aldous", WT), k("Manor Reaper", 2, WT)],
        "Inside the hall, at the hearth. His reapers will guard him. Take them first, then Aldous.",
        "The Lord of the Hall, in pieces. I'll have the hearth lit again. Take what you want.", None))
    # ---- Quillon: Whispering Shore
    A(Q("wts_puddlejumpers", "Vile Fins on the Strand", QUILLON, WT, 6, 8, "shore",
        "Fisher Quillon's nets are in tatters and his boat is gone. The Vile Fin murlocs on Whispering Shore took the boat "
        "and use the nets as hats. He wants them put in their place.",
        [k("Vile Fin Puddlejumper", 5, WT)],
        "Along the strand to the north-west. The little ones. Eight, and bring back my dignity if you find it.",
        "That'll teach them. Probably not, but it'll teach me something. Take a piece of what's left.", "wts_pearls"))
    A(Q("wts_pearls", "Oracle's Pearls", QUILLON, WT, 7, 9, "shore",
        "The oracles wear pearls to speak to the tide, and the tide has been speaking a great deal of nonsense lately. "
        "Quillon thinks taking the pearls might quiet it.",
        [fetch("oracle_pearl", 5)],
        "The Minor Oracles carry them. Five pearls, and if the tide screams, run.",
        "Quiet at last. Even the gulls have stopped. Your pick, friend.", "wts_gillrot"))
    A(Q("wts_gillrot", "Old Gillrot", QUILLON, WT, 8, 9, "shore",
        "Old Gillrot leads the Vile Fins, a withered oracle with a staff made from a drowned man's mast. He's the one "
        "who stole the boat. Quillon wants it back.",
        [boss("Old Gillrot", WT), k("Vile Fin Minor Oracle", 2, WT)],
        "He sits on the biggest rock. His oracles heal him, so thin them first, then Gillrot.",
        "My boat's still rotten, but it's mine. Take whatever you like from his trove.", None))
    # ---- Dessa: Crusader Outpost
    A(Q("wto_converts", "Fresh Converts", DESSA, WT, 7, 9, "outpost",
        "Scout Dessa Vane watches the Crusader Outpost from the thorn-line. New recruits arrive weekly, wide-eyed and "
        "fanatical. The Deathguard would like fewer of them.",
        [k("Scarlet Convert", 5, WT)],
        "They're green and enthusiastic. That makes them dangerous. Eight, and keep to the shadows.",
        "Fewer recruits, fewer problems. The Crusade bleeds. Take your pick.", "wto_initiates"))
    A(Q("wto_initiates", "Initiates and Banners", DESSA, WT, 8, 9, "outpost",
        "Behind the converts stand the Initiates: trained, armed and devout. They carry the Crusade's banners and the "
        "outpost's stubbornness. Dessa wants them cut down before they march on Brill.",
        [k("Scarlet Initiate", 4, WT)],
        "They're better than the converts. Don't engage more than two at once. Six, please.",
        "A good cut. I'd say the Crusade will feel that. Take what you can carry.", "wto_korgal"))
    A(Q("wto_korgal", "Meven Korgal", DESSA, WT, 8, 9, "outpost",
        "Meven Korgal commands the Crusader Outpost: a veteran, a zealot and an excellent shot with a prayer. If he "
        "falls, the outpost will fall with him.",
        [boss("Meven Korgal", WT), k("Scarlet Convert", 2, WT)],
        "He's at the heart of the camp. His recruits will rally. Take them first, then him.",
        "Korgal's dead. The camp's a rabble. That'll buy Brill a season. Take your pick.", None))
    # ---- Marren: Solliden Farmstead
    A(Q("wtf_farmhands", "Hands Without Masters", MARREN, WT, 6, 8, "farm",
        "Widow Marren's farmhands stayed on after the master died, and after they died. They work the fields all hours "
        "with rusted tools and no direction.",
        [k("Solliden Farmhand", 5, WT)],
        "They don't know any better. Put them down gently. They were good men.",
        "Thank you. I'll sit with the ones who remain. Please, take something.", "wtf_threshers"))
    A(Q("wtf_threshers", "Blighted Harvest", MARREN, WT, 6, 8, "farm",
        "The grain threshers, blighted machines that run themselves, have eaten the last of the harvest and are looking for "
        "more. Marren cannot stop them.",
        [k("Blighted Grain Thresher", 4, WT)],
        "They're iron and rot. Seven of them, before they find the house.",
        "The fields are quiet. Still ruined, but quiet. Take some of the old tack.", "wtf_goodman"))
    A(Q("wtf_goodman", "Goodman Solliden", MARREN, WT, 7, 8, "farm",
        "Her husband, Goodman Solliden, walks the fields with a pitchfork and a blighted grin. She wants him laid to rest, "
        "and doesn't want to watch.",
        [boss("Goodman Solliden", WT), k("Solliden Farmhand", 2, WT)],
        "He's out among the pumpkins. His men will guard him. Be kind to him, if you can.",
        "...Thank you. He was a good man once. Take his things. I can't look at them.", None))
    # ---- Oswin: Stillwater Pond
    A(Q("wtp_lurkers", "Things in the Silt", OSWIN, WT, 5, 7, "pond",
        "Hermit Oswin lives by Stillwater Pond because no one else will. The crab-like lurkers in the silt are the only "
        "neighbours he has, and they bite.",
        [k("Stillwater Lurker", 5, WT)],
        "They hide in the mud and pinch. Eight, and watch your ankles.",
        "Fewer pincers. A man can wash his feet again. Thanks.", "wtp_dead"))
    A(Q("wtp_dead", "The Drowned Choir", OSWIN, WT, 6, 8, "pond",
        "The Rotting Dead shuffle out of the pond at all hours, singing a hymn no one remembers. Oswin finds it unrestful.",
        [k("Rotting Dead", 4, WT)],
        "They hum. I can't stand the humming. Seven, please.",
        "Silence at last. I think I'll sleep. Take your pick.", "wtp_murk"))
    A(Q("wtp_murk", "Murk the Bloated", OSWIN, WT, 6, 7, "pond",
        "Something large sits at the bottom of the pond. Oswin calls it Murk. It bloats with every drowned thing and "
        "belches them up on the shore.",
        [boss("Murk the Bloated", WT), k("Stillwater Lurker", 2, WT)],
        "It comes up when you splash. Clear the lurkers, then call it out. Don't fight in the water.",
        "The pond's clear. Well, clearer. Take his treasures. I've no use for them.", None))
    # ---- Sorren: Agamand Mills
    A(Q("wta_servants", "The Agamand Staff", SORREN, WT, 8, 10, "mills",
        "Envoy Sorren speaks for Brill at the old mill. The Agamand servants still tend the house they died in, and "
        "they'll murder anyone who tries to take the grain.",
        [k("Agamand Servant", 5, WT)],
        "They're stubborn, not smart. Eight, and don't let them corner you in the mill-race.",
        "That'll thin the household. Sorren thanks you. Take your pick.", "wta_keys"))
    A(Q("wta_keys", "Keys to the Cellar", SORREN, WT, 8, 10, "mills",
        "Captured farmers are held in the mill cellars, shackled and slowly rotting. The servants carry the keys. Sorren "
        "wants them freed, or at least unlocked.",
        [fetch("captured_farmer_shackle_key", 3)],
        "The servants have the keys on them. Three should open the lot. Bring them to me.",
        "Three keys. That's freedom for the lot of them. Take something for the trouble.", "wta_thurman"))
    A(Q("wta_thurman", "Thurman Agamand", SORREN, WT, 9, 10, "mills",
        "Thurman Agamand was the miller, then the lord, then something worse. He reigns in the mill-house with a "
        "family of ghouls. Sorren wants the house back.",
        [boss("Thurman Agamand", WT), k("Agamand Family Ghoul", 2, WT)],
        "He's at the heart of the mill. His ghouls come first. Be ready.",
        "The mill's ours. The Agamands are dust. Take what you like from the strongbox.", None))
    # ---- Halvard: Agamand Family Crypt
    A(Q("wtc_wights", "Wights Below", HALVARD, WT, 9, 10, "crypt",
        "Keeper Halvard guards the Agamand crypt gate and has not been inside since the wights woke. They hold the "
        "vaults now, and he wants them cleared.",
        [k("Agamand Crypt Wight", 5, WT)],
        "They're strong, hungry and old. Eight, and don't let them gang up.",
        "That's the vaults breathing easier. Thank you. Take something.", "wtc_dargol"))
    A(Q("wtc_dargol", "Captain Dargol", HALVARD, WT, 9, 10, "crypt",
        "Captain Dargol, last of the Agamand guard, rose to defend a family that is already dust. He fights anything that "
        "comes near the dead.",
        [boss("Captain Dargol", WT), k("Agamand Crypt Wight", 2, WT)],
        "He's at the deepest vault. His wights guard the door. Clear them, then him.",
        "Dargol's at rest. The vault is ours. Take your pick of the old arms.", None))
    # ---- Brask: Garren's Haunt
    A(Q("wth_mongrels", "Mongrels in the Fields", BRASK, WT, 8, 10, "haunt",
        "Warden Brask holds the line at Garren's Haunt. The Rot Hide mongrels that follow the gnolls have turned the "
        "fields into a kennel.",
        [k("Rot Hide Mongrel", 5, WT)],
        "They come in packs, mangy and starved. Eight, please.",
        "That's the field quiet. Take a piece of the kit.", "wth_gnolls"))
    A(Q("wth_gnolls", "Gnoll Camp", BRASK, WT, 8, 10, "haunt",
        "Behind the mongrels stand the Rot Hide gnolls: brutes in stitched hide with clubs as long as your arm. They "
        "dig up graves for fun. Brask is not amused.",
        [k("Rot Hide Gnoll", 4, WT)],
        "They have clubs and bad tempers. Seven should get the message across.",
        "Seven fewer clubs. Excellent. Your pick.", "wth_maggot"))
    A(Q("wth_maggot", "Maggot Eye", BRASK, WT, 9, 10, "haunt",
        "Maggot Eye is the gnoll chieftain: scarred, rotted and bigger than the rest. His tribe follows him because he "
        "bites harder than they do.",
        [boss("Maggot Eye", WT), k("Rot Hide Gnoll", 2, WT)],
        "He sits in the middle of the camp. His guards come first. Be quick.",
        "Maggot Eye's gone. The tribe will scatter. Take your pick of the camp's loot.", None))

    # =====================================================================================================
    # EASTERN TIRISFAL
    # =====================================================================================================
    LINNEA, MORVYN, GUNTHER, HALLAM, RAVEL, EDRIC, YSOLDE, HOLLOW = (
        "et_deathguard_linnea", "et_gravekeeper_morvyn", "et_gunther_lorn", "et_scout_hallam", "et_hunter_ravel",
        "et_balnir_edric", "et_cult_warden", "et_scarlet_watch_scout")
    # ---- Linnea: Zeppelin Landing / Ruins
    A(Q("etl_dusk", "Dusk Over the Landing", LINNEA, ET, 7, 9, "landing",
        "Deathguard Linnea keeps order at the zeppelin landing. Duskbats roost in the ropes and drop on passengers. It "
        "is, she says, bad for business.",
        [k("Mangy Duskbat", 5, ET)],
        "Up in the ropes and along the road. Eight, please, before the next boat.",
        "The landing is quieter. Thank you. Take something from the supply crate.", "etl_dead"))
    A(Q("etl_dead", "Walkers on the Brill Road", LINNEA, ET, 7, 9, "landing",
        "Zombies wander the road between Brill and the landing, blocking carts. They are slow and sullen and utterly "
        "uninterested in being moved.",
        [k("Wretched Zombie", 5, ET)],
        "They block the road and the carts. Eight, and drag them off the verge.",
        "The road is clear. Now we can complain about something else. Take your pick.", "etl_remnants"))
    A(Q("etl_remnants", "Ghosts of the Throne", LINNEA, ET, 9, 11, "ruins",
        "South of the landing lie the Ruins of Lordaeron: the old capital, the Undercity gate, and a thousand remnants of "
        "men who never left. They snap at anyone who passes.",
        [k("Lordaeron Remnant", 5, ET)],
        "Go south, to the ruins. The remnants are tireless. Eight, and don't stand in the open.",
        "That will give the road a rest. Take what you need.", "etl_signets"))
    A(Q("etl_signets", "Signets of Lordaeron", LINNEA, ET, 9, 11, "ruins",
        "The remnants wear the signet rings of the old court. Linnea wants them: not for the gold, but because some of "
        "them can still be traced to families who might want to know.",
        [fetch("lordaeron_signet", 4)],
        "Four signets. They're on the remnants. Treat them with a little respect.",
        "Four. Each one a family. I'll send them word. Take something for your trouble.", None))
    # ---- Morvyn: Faol's Rest
    A(Q("etm_restless", "The Restless of Faol", MORVYN, ET, 8, 10, "faol",
        "Gravekeeper Morvyn tends Faol's Rest, the old pilgrims' graveyard. The dead there will not stay put; they claw up "
        "through the soil and stand in the rows.",
        [k("Faol's Restless", 5, ET)],
        "They wander the rows. Eight, and be gentle with the stones.",
        "Back in the ground, or near enough. Thank you. Take your pick.", "etm_seals"))
    A(Q("etm_seals", "Faol's Seal", MORVYN, ET, 8, 10, "faol",
        "Faol's grave was sealed by a ring of stone fragments. The restless have been taking them. Morvyn wants them "
        "back before the seal fails.",
        [fetch("faols_seal_fragment", 4)],
        "The restless carry the fragments. Four will do it. Bring them to me.",
        "The seal is mended. Mostly. Take something for the trouble.", "etm_melrache"))
    A(Q("etm_melrache", "Captain Melrache", MORVYN, ET, 9, 10, "faol",
        "A Scarlet captain, Melrache, has made Faol's Rest his camp, digging up graves and calling it a crusade. Morvyn "
        "would like him to dig his own.",
        [boss("Captain Melrache", ET), k("Faol's Restless", 2, ET)],
        "He sits at the north end of the rows. Clear the restless, then him.",
        "Melrache's dead. Faol can rest. Take your pick of the camp.", None))
    # ---- Gunther: Brightwater Lake
    A(Q("etg_wretches", "Lake of the Drowned", GUNTHER, ET, 8, 10, "lake",
        "Warden Gunther Lorn watches Brightwater Lake. Drowned Wretches crawl out of it at dusk, moaning the names of "
        "the lost. He wants them back in the water.",
        [k("Drowned Wretch", 5, ET)],
        "They come out at dusk. Eight, and keep your feet dry if you can.",
        "That's the shore quiet. Thanks. Take your pick.", "etg_ice"))
    A(Q("etg_ice", "Shards of the Cold Lake", GUNTHER, ET, 8, 10, "lake",
        "The lake sheds black ice shards, and the shades hoard them. Gunther is convinced they are what is making the "
        "water cold. He'd like them gone.",
        [fetch("iceshard_fragment", 5)],
        "The shades carry them. Five shards, and don't stand too long near the water.",
        "Five. The lake will warm, I think. Slowly. Take something.", "etg_bethor"))
    A(Q("etg_bethor", "Bethor Iceshard", GUNTHER, ET, 9, 10, "lake",
        "Bethor Iceshard is a shade who has grown too cold to die. He stands at the centre of the lake and drains the "
        "warmth from anything near.",
        [boss("Bethor Iceshard", ET), k("Weeping Shade", 2, ET)],
        "He stands where the ice is thickest. His shades guard him. Take them first.",
        "The lake is warming already. I can feel it. Take your pick.", None))
    # ---- Hallam: Crusader's Outpost
    A(Q("eth_converts", "Recruits on the Rise", HALLAM, ET, 8, 10, "outpost",
        "Scout Hallam watches the Crusader's Outpost east of Brill. The recruits there are loud, young and entirely "
        "unprepared. They're also a month away from being a threat.",
        [k("Scarlet Convert", 5, ET)],
        "They train in the yard. Eight, and keep them from the road.",
        "Fewer recruits, fewer problems. Take your pick.", "eth_initiates"))
    A(Q("eth_initiates", "Initiates of the Outpost", HALLAM, ET, 9, 10, "outpost",
        "Behind the recruits come the Initiates: drilled, armed and fanatical. They guard the outpost's gate and its "
        "secrets.",
        [k("Scarlet Initiate", 4, ET)],
        "Don't take more than two at a time. Six should give them pause.",
        "Six. They'll be rattled. Take something from the supply.", "eth_brennic"))
    A(Q("eth_brennic", "Crusader Brennic", HALLAM, ET, 9, 10, "outpost",
        "Crusader Brennic commands the outpost. He's strong, devout and utterly merciless. Without him, the garrison "
        "will fall.",
        [boss("Crusader Brennic", ET), k("Scarlet Convert", 2, ET)],
        "He's in the tower. His recruits rally to him. Take them first, then him.",
        "Brennic's down. The outpost is leaderless. Take your pick.", None))
    # ---- Ravel: Venomweb Vale
    A(Q("etr_skitterers", "Skitterers of the Vale", RAVEL, ET, 10, 11, "venom",
        "Huntress Ravel tracks the spiders of Venomweb Vale. The skitterers breed faster than she can hunt them, and "
        "their bite paralyses.",
        [k("Venomweb Skitterer", 5, ET)],
        "They hide in the webs. Eight, and watch for the big one.",
        "The Vale is quieter. Thanks. Take something.", "etr_sacs"))
    A(Q("etr_sacs", "Venom for the Apothecary", RAVEL, ET, 10, 11, "venom",
        "Venomweb venom is worth a fortune to the Apothecaries. Ravel wants five sacs: for the Undercity, for the war, "
        "and for her own reasons.",
        [fetch("venom_sac", 5)],
        "The skitterers and the night-webs carry them. Five, and don't pop them.",
        "Five sacs. A fine haul. Take your pick of the lot.", "etr_mother"))
    A(Q("etr_mother", "Mother Venomweb", RAVEL, ET, 10, 11, "venom",
        "Mother Venomweb is the matriarch of the Vale: a huge spider, venom-fat and cunning. Every skitterer in the "
        "Vale is her brood.",
        [boss("Mother Venomweb", ET), k("Venomweb Skitterer", 2, ET)],
        "She sits at the heart of the web. Her brood guards her. Take them first.",
        "The Mother's dead. The Vale is yours. Take your pick of her hoard.", None))
    # ---- Edric: Balnir Farmstead
    A(Q("etb_worgs", "Worgs in the Paddock", EDRIC, ET, 9, 10, "balnir",
        "Stablehand Edric tends what remains of the Balnir farmstead. The Bleak Worgs have taken over the paddock and "
        "eat whatever stumbles in.",
        [k("Bleak Worg", 5, ET)],
        "They hide in the hay. Eight, and keep to the fences.",
        "That's the paddock clear. Take something from the tack.", "etb_stableboys"))
    A(Q("etb_stableboys", "The Stableboys' Rest", EDRIC, ET, 9, 11, "balnir",
        "The stableboys never left the farm. They roam the paddock with pitchforks, loyal to a master who died long "
        "ago. Edric wants them put to rest.",
        [k("Balnir Stableboy", 5, ET)],
        "They don't know. Treat them kindly. Eight.",
        "They're at rest. Thank you. Take your pick.", "etb_vachon"))
    A(Q("etb_vachon", "Captain Vachon", EDRIC, ET, 10, 11, "balnir",
        "Captain Vachon led the Balnir militia. He now leads the dead, a stubborn old soldier who refuses to give up "
        "the farm.",
        [boss("Captain Vachon", ET), k("Balnir Stableboy", 2, ET)],
        "He's at the farmhouse. His stableboys guard him. Take them first.",
        "Vachon's at peace. The farm is quiet. Take your pick.", None))
    # ---- Ysolde: Cult of the Damned Farm
    A(Q("etd_acolytes", "Acolytes of the Damned", YSOLDE, ET, 10, 12, "cult",
        "Warden Ysolde Grave watches the Cult of the Damned farm. Its acolytes call on powers no one should, and the "
        "Undercity wants them silenced.",
        [k("Cult Acolyte", 5, ET)],
        "They chant in the cellar. Eight, and don't let them finish a verse.",
        "That will quiet the cellar. Take something.", "etd_ledger"))
    A(Q("etd_ledger", "The Cult's Ledger", YSOLDE, ET, 10, 12, "cult",
        "The cult keeps meticulous records: names, tallies, debts. The pages are scattered on the bodies of its "
        "members. Ysolde wants them for the Undercity.",
        [fetch("cult_ledger_page", 5)],
        "The acolytes and the fanatics carry them. Five pages, and don't read them aloud.",
        "Five pages. Enough for a warrant. Take your pick.", "etd_thaddeus"))
    A(Q("etd_thaddeus", "Overseer Thaddeus", YSOLDE, ET, 11, 12, "cult",
        "Overseer Thaddeus leads the cult. He sits in the farm's deepest cellar, issuing orders to the damned. His "
        "death would unravel the lot.",
        [boss("Cult Overseer Thaddeus", ET), k("Cult Fanatic", 2, ET)],
        "He's in the cellar. His fanatics guard the stairs. Take them first.",
        "The cult is leaderless. Excellent. Take your pick of his robes.", None))
    # ---- Hollowmere: Scarlet Watch Post / North Coast
    A(Q("ets_bowmen", "Archers on the Coast", HOLLOW, ET, 10, 12, "watch",
        "Scout Hollowmere watches the Scarlet Watch Post from the lakeside slope. Their bowmen patrol the north coast "
        "road and pick off anyone who passes.",
        [k("Scarlet Bowman", 5, ET)],
        "Stay low. They shoot first. Eight, and watch the shadows.",
        "That's the road open. Thank you. Take something.", "ets_zealots"))
    A(Q("ets_zealots", "Zealots of the Watch", HOLLOW, ET, 10, 12, "watch",
        "The Watch Post is held by zealots, who preach as they fight. Hollowmere would like them to stop preaching.",
        [k("Scarlet Zealot", 5, ET)],
        "They don't stop. Eight, and keep your ears covered.",
        "Quieter. For a while. Take your pick.", "ets_preachers"))
    A(Q("ets_preachers", "Sermons in Fire", HOLLOW, ET, 10, 12, "watch",
        "The preachers are the worst of them. They call down fire on the faithless. Hollowmere has the burn scars to "
        "prove it.",
        [k("Scarlet Preacher", 4, ET)],
        "They stand on the steps and burn things. Six, and don't stand in the fire.",
        "Six sermons ended. Thank you. Take something.", "ets_vishas"))
    A(Q("ets_vishas", "Interrogator Vishas", HOLLOW, ET, 11, 12, "watch",
        "Interrogator Vishas runs the Watch Post's cells. He's patient, methodical and cruel. Hollowmere wants him dead, "
        "and the cells emptied.",
        [boss("Interrogator Vishas", ET), k("Scarlet Zealot", 2, ET)],
        "He's in the cells. His zealots guard the door. Take them first.",
        "Vishas is dead. The cells are open. Take your pick.", None))
    showcase(A)
    scourge_cave(A)
    return Z


def showcase(A):
    """Quest-engine showcase (2026-10-23): deliver, craft, monster-drop starters and a Linken's-Sword multi-zone gate that bridges
    into Silverpine North.  Not every quest is like this - these are the spice."""
    # ---- DELIVER across Tirisfal: Brill -> Faol's Rest
    A(Q("brl_dispatch", "A Dispatch for Faol's Rest", "brill_deathguard", BR, 8, 10, "brill",
        "Rennick doesn't trust the Faol's Rest gravekeeper's reports to arrive on their own, and he doesn't trust his own "
        "messenger boys to arrive at all. A sealed dispatch needs to reach Gravekeeper Morvyn, over the hills in the east.",
        [deliver("rennick_dispatch", "Take Rennick's dispatch to Gravekeeper Morvyn")],
        "Eastern Tirisfal, the graveyard on the hill at Faol's Rest. Put it in her hand, not on her desk. Don't read it.",
        "Rennick's seal. Hm. He worries so loudly for a man who never leaves the square. Here, for the road.", None,
        turn_in_npc_id="et_gravekeeper_morvyn",
        grant_items=carry("rennick_dispatch", "Sealed Deathguard Dispatch", "Wax-sealed, stamped with Brill's gallows crest.")))
    # ---- CRAFT: the gate guard wants proper kit.  Smelt, then forge.
    A(Q("brl_guard_smelt", "Bars for the Gate", "brill_guard", BR, 6, 8, "brill",
        "The gate guard's kit is falling apart, and Brill's new forge by the east market is going unused. Smelt two copper "
        "bars from Tirisfal ore and he'll show you what they're for.",
        [craft("bar_copper", "Smelt copper bars at Brill's forge", 2)],
        "Copper ore is in the hills. Smelt two bars at the forge past the market and bring them. I'll supply the nagging.",
        "Two bars. Clean, too. Let's make something of them.", "brl_guard_bracers"))
    A(Q("brl_guard_bracers", "Bracers for the Gate", "brill_guard", BR, 6, 8, "brill",
        "A pair of copper bracers, forged by your own hands at the Brill forge. The guard wants to see proof that the "
        "forge works before he trusts it with his armour.",
        [craft("blacksmith_copper_bracers", "Forge Copper Bracers at Brill's forge")],
        "Two bars, a hammer and some patience. Make the bracers. Mind the sparks.",
        "Crooked, but sturdy. I'll wear them proudly. Here's something for your trouble.", None))
    # ---- MONSTER-DROP STARTERS
    A(Q("brl_locket", "A Moldering Locket", "item:moldering_locket", WT, 6, 8, "farm",
        "A tarnished locket, found on one of the wandering dead. The portrait inside is almost gone, but the inscription on the "
        "back is plain enough: 'For Marren, from Aldric'. The widow Marren lives at the Solliden Farmstead.",
        [deliver("moldering_locket", "Return the locket to Widow Marren")],
        "You turn the locket over. The clasp has rusted shut, but the inscription is legible. Marren, at the Solliden fields.",
        "Marren turns it over and over in her hands. 'Aldric.' She says nothing else for a while. Then: 'Thank you. Take this.'",
        None, turn_in_npc_id="wt_solliden_farmer"))
    A(Q("ets_bowman_orders", "Bloodied Scarlet Orders", "item:scarlet_battle_orders", ET, 10, 12, "watch",
        "Scarlet Crusade orders, torn from a bowman's quiver: troop positions, patrol times and a map of the north coast. "
        "Deathguard Rennick will want these in Brill.",
        [deliver("scarlet_battle_orders", "Bring the orders to Deathguard Rennick")],
        "You skim the orders. Troop positions, patrol times, a route along the coast. This belongs with Rennick in Brill.",
        "Rennick reads it twice and swears quietly. 'Their patrols run to the hour. Good. This is worth a great deal.'",
        None, turn_in_npc_id="brill_deathguard"))
    # ---- LINKEN'S SWORD: the cult ledger bridge into Silverpine North (needs BOTH Eastern ledger work AND the Western Agamand work)
    A(Q("etd_ledger_courier", "The Ledger Bundle", "et_cult_warden", ET, 11, 12, "cult",
        "Ysolde has bound the ledger pages into a bundle and wants it in the hands of someone who can read the cult's cipher. "
        "The one she trusts is Keeper Oswin at Raven Hill Cemetery in Silverpine North, through the pass to the north-west.",
        [deliver("cult_ledger_bundle", "Carry the ledger bundle to Keeper Oswin in Silverpine North")],
        "The portal at the edge of the Landing leads into Silverpine. Raven Hill Cemetery, Keeper Oswin. Don't let anyone read it.",
        "Oswin turns the bundle over, and his face changes. 'The Agamand seal. Of course. Come back when you've seen their house.'",
        None, requires_quests=["etd_ledger"], turn_in_npc_id="sp_north_cemetery_keeper",
        grant_items=carry("cult_ledger_bundle", "Cult Ledger Bundle", "Pages bound in black cord and sealed with grave-wax."),
        exp=520, gold=1200))
    A(Q("sp_ledger_cipher", "The Agamand Cipher", "sp_north_cemetery_keeper", "silverpine_north", 12, 14, "cult",
        "Oswin can read the cult's ledger, but only half of it. The cipher keys are the Agamand family seals, and only someone "
        "who has stood in the Agamand mansion could match them. He needs the husks buried behind Raven Hill thinned out "
        "first, so the dead stop interrupting his reading.",
        [k("Risen Husk", 5, "Silverpine North")],
        "You've been through the Agamand house, and you carried the ledger here. Good. Now clear the husks at Raven Hill so I can read in peace.",
        "Eight husks, and the seals match. The ledger names the cult's patrons. Silverpine will want to hear this. Take your pick.",
        None, exp=800, gold=1400, requires_quests=["etd_ledger_courier", "wta_thurman"]))


def scourge_cave(A):
    """The Scourge Cave line (2026-10-23).  A CAVE: kill / fetch / boss / explore only, no escorts."""
    CAL = "et_cave_warden"
    A(Q("etc_descend", "Down the Spine", CAL, ET, 9, 11, "scourge",
        "The Cult of the Damned dug their cellar into something that was never meant to be dug: the bones of a Scourge "
        "Abomination, so large its spine is a corridor. Boneward Calder wants to know how far the passage runs before "
        "anyone commits to it.",
        [explore(SC, 45, 40, 7)],
        "The cave mouth is behind the cult's farm. Walk the spine to the middle of the ribs and come back. Don't pick anything up.",
        "So it runs that far. Right. Then the rest is a matter of killing what lives in the ribs. Good work.", "etc_warriors"))
    A(Q("etc_warriors", "Bones That Walk", CAL, ET, 10, 12, "scourge",
        "Scourge Warriors wander the rib tunnels in loose patrols. They don't sleep, they don't tire, and they are very "
        "bad at hiding.",
        [k("Scourge Warrior", 5, SC)],
        "Eight of them. Fight in the tunnels, not the open hall, and let them come to you.",
        "Eight fewer. The ribs sound quieter already. Take something.", "etc_ghouls"))
    A(Q("etc_ghouls", "Hungry Dead", CAL, ET, 10, 12, "scourge",
        "The ghouls came with the Scourge, but they stayed for the plague cellar. They are fast and they travel in packs.",
        [k("Scourge Ghoul", 5, SC)],
        "They hunt by the sound of heartbeats, which makes you a very noisy guest. Eight.",
        "Eight ghouls. Do you still have all your fingers? Good. Take your pick.", "etc_runes"))
    A(Q("etc_runes", "Scourge Rune Shards", CAL, ET, 11, 12, "scourge",
        "The Scourge Necromancers carve their wards onto black shards of stone, and the same wards hold the Abomination's "
        "bones in place. Calder wants a handful, to learn how to break them.",
        [fetch("scourge_rune_shard", 6)],
        "The necromancers carry them. Six shards, uncracked. Don't read the runes aloud.",
        "Six clean shards. Now I can see where the wards sit. The Abomination is next. Take your pick.", "etc_abomination"))
    A(Q("etc_abomination", "The Scourge Abomination", CAL, ET, 12, 13, "scourge",
        "The Abomination sits in the skull at the head of the spine, wired into the cult's rune stones. Kill it, and the "
        "cellar is just a cellar again.",
        [boss("Scourge Abomination", SC), k("Scourge Necromancer", 2, SC)],
        "The skull throne, at the north end of the spine. Necromancers keep it standing. Take them first.",
        "It's down. The cellar is quiet. I'll be sleeping with a candle on for a week. Take your pick of what it wore.", None))
    # ---- optional side chambers: open once you've walked the spine
    A(Q("etc_krag", "The Bone Pit", CAL, ET, 11, 12, "scourge",
        "Ghoulmaster Krag keeps his pack in a bone-lined pit west of the ribs. He feeds them on what the cult leaves behind.",
        [boss("Ghoulmaster Krag", SC), k("Scourge Ghoul", 2, SC)],
        "West of the second rib, down a side tunnel. He whistles for the pack when he's losing. Be quick.",
        "Krag's whistle is silent. Take your pick of his trophies.", None, requires_quests=["etc_descend"]))
    A(Q("etc_orvyn", "The Plague Lab", CAL, ET, 12, 13, "scourge",
        "Plaguemaster Orvyn runs the cult's laboratory in a side chamber east of the ribs, brewing the blight they pour on "
        "the farms above. Calder wants the vats cold.",
        [boss("Plaguemaster Orvyn", SC), k("Cult Acolyte", 2, SC)],
        "East of the third rib, past a tunnel of vials. His acolytes tend the vats. Keep your mouth covered.",
        "The vats are cold. Whatever he was brewing, it won't reach the farms. Take your pick.", None,
        requires_quests=["etc_descend"]))
    # ---- DROP-STARTED, cross-zone: the formula Orvyn carries goes to Brill's apothecary
    A(Q("etc_formula", "The Plaguemaster's Formula", "item:plaguemaster_formula", ET, 11, 13, "scourge",
        "A sheaf of stained notes pulled from the Plaguemaster's belt: dosages, ingredients, and a diagram of the cult's "
        "delivery vats. Assistant Grael at the Brill Apothecary would pay dearly for this.",
        [deliver("plaguemaster_formula", "Bring the formula to Assistant Grael in Brill")],
        "The handwriting is clinical. Every line ends in the same instruction: 'dilute before use'. Grael, at Brill's apothecary.",
        "Grael reads it twice and goes slightly pale. 'They were going to put this in the wells. Thank you. Truly.'",
        None, turn_in_npc_id="brill_apothecary_asst"))


# ----------------------------------------------------------------------
NEW_NPCS = [
    # Western
    dict(npc_id="wt_vale_ranger", name="Ranger Corvin Ashe", zone="western_tirisfal", gender="male", appearance_variant=4,
         facing="down", greeting="Keep to the road. The Vale doesn't like surprises, and neither do I."),
    dict(npc_id="wt_shore_fisher", name="Fisher Quillon", zone="western_tirisfal", gender="male", appearance_variant=8,
         facing="right", greeting="Nothing bites any more. Except the Vile Fins, and they bite with spears."),
    dict(npc_id="wt_outpost_scout", name="Scout Dessa Vane", zone="western_tirisfal", gender="female", appearance_variant=6,
         facing="left", greeting="Quiet. The Crusade has sharp eyes and a short list of things it forgives."),
    dict(npc_id="wt_solliden_farmer", name="Widow Marren", zone="western_tirisfal", gender="female", appearance_variant=2,
         facing="down", greeting="The fields are all that's left. I tend them. I don't know why."),
    dict(npc_id="wt_pond_hermit", name="Hermit Oswin", zone="western_tirisfal", gender="male", appearance_variant=10,
         facing="down", greeting="I came for the quiet. The pond has opinions about that."),
    dict(npc_id="wt_agamand_envoy", name="Envoy Sorren", zone="western_tirisfal", gender="male", appearance_variant=1,
         facing="right", greeting="Brill sends me to ask politely. After that, it sends you."),
    dict(npc_id="wt_crypt_keeper", name="Keeper Halvard", zone="western_tirisfal", gender="male", appearance_variant=7,
         facing="down", greeting="The family's dead and they won't stay quiet about it."),
    dict(npc_id="wt_garren_warden", name="Warden Brask", zone="western_tirisfal", gender="male", appearance_variant=5,
         facing="left", greeting="Garren's Haunt has always had gnolls. Lately it has more."),
    # Eastern
    dict(npc_id="et_deathguard_linnea", name="Deathguard Linnea", zone="eastern_tirisfal", gender="female",
         appearance_variant=3, facing="down", greeting="Passengers to the left, ropes to the right, ghosts directly overhead."),
    dict(npc_id="et_gravekeeper_morvyn", name="Gravekeeper Morvyn", zone="eastern_tirisfal", gender="female",
         appearance_variant=9, facing="down", greeting="They don't stay down any more. Not in Faol's Rest."),
    dict(npc_id="et_gunther_lorn", name="Warden Gunther Lorn", zone="eastern_tirisfal", gender="male",
         appearance_variant=6, facing="right", greeting="The lake's watching you. It watches everyone."),
    dict(npc_id="et_scout_hallam", name="Scout Hallam", zone="eastern_tirisfal", gender="male", appearance_variant=8,
         facing="left", greeting="Keep low. They've got archers on the wall."),
    dict(npc_id="et_hunter_ravel", name="Huntress Ravel", zone="eastern_tirisfal", gender="female",
         appearance_variant=1, facing="right", greeting="The Vale eats the careless. Mind your step."),
    dict(npc_id="et_balnir_edric", name="Stablehand Edric", zone="eastern_tirisfal", gender="male", appearance_variant=4,
         facing="down", greeting="The horses are gone. The stable remains. So do I."),
    dict(npc_id="et_cult_warden", name="Warden Ysolde Grave", zone="eastern_tirisfal", gender="female",
         appearance_variant=5, facing="down", greeting="I came here to watch. Now I count."),
    dict(npc_id="et_cave_warden", name="Boneward Calder", zone="eastern_tirisfal", gender="male",
         appearance_variant=2, facing="left", greeting="That hole behind the farm breathes. Don't tell me it doesn't."),
]

QUEST_DROPS = {
    "oracle_pearl": ("Oracle's Pearl", "A salt-white pearl, cold and faintly humming.",
                     [("Vile Fin Minor Oracle", 0.45), ("Vile Fin Puddlejumper", 0.1)]),
    "crusade_orders": ("Crusade Orders", "Folded orders, signed in a neat red hand.",
                       [("Scarlet Convert", 0.4), ("Scarlet Initiate", 0.35)]),
    "blighted_pumpkin": ("Blighted Pumpkin", "Swollen, grey-green and faintly warm.",
                         [("Blighted Grain Thresher", 0.5), ("Solliden Farmhand", 0.1)]),
    "grave_relic": ("Grave Relic", "A small carved token from the Agamand vault.",
                    [("Agamand Crypt Wight", 0.4), ("Rot Hide Graverobber", 0.4)]),
    "iceshard_fragment": ("Iceshard Fragment", "A shard of black ice that does not melt.",
                          [("Weeping Shade", 0.35), ("Drowned Wretch", 0.2), ("Bethor Iceshard", 0.5)]),
    "faols_seal_fragment": ("Faol's Seal Fragment", "A carved stone fragment, worn smooth by pilgrims.",
                            [("Faol's Restless", 0.4)]),
    "venom_sac": ("Venom Sac", "A swollen gland that oozes at a touch.",
                  [("Venomweb Skitterer", 0.45), ("Vicious Night Web Spider", 0.25)]),
    "cult_ledger_page": ("Cult Ledger Page", "A page of names, tallies and debts.",
                         [("Cult Acolyte", 0.4), ("Cult Fanatic", 0.4)]),
    "scourge_rune_shard": ("Scourge Rune Shard", "A shard of black rune-stone, etched and cold to the touch.",
                           [("Scourge Necromancer", 0.45), ("Scourge Warrior", 0.15)]),
    "lordaeron_signet": ("Lordaeron Signet", "A tarnished ring bearing the old court's crest.",
                         [("Lordaeron Remnant", 0.4)]),
    "stolen_cargo": ("Stolen Cargo Crate", "A small crate, battered and half-opened.",
                     [("Ragged Scavenger", 0.45)]),
}


# monster drops that START a quest (item -> (name, description, quest_id, [(creature, chance)]))
STARTER_DROPS = {
    "plaguemaster_formula": ("Plaguemaster's Formula", "Stained notes, dosages and a diagram of the cult's delivery vats.",
                             "etc_formula", [("Plaguemaster Orvyn", 0.6)]),
    "moldering_locket": ("Moldering Locket", "A tarnished locket. The inscription on the back is still legible.", "brl_locket",
                         [("Solliden Farmhand", 0.12), ("Rotting Dead", 0.05)]),
    "scarlet_battle_orders": ("Bloodied Scarlet Orders", "Crusade orders, torn and stained. Troop positions and patrol times.",
                              "ets_bowman_orders", [("Scarlet Bowman", 0.14), ("Scarlet Zealot", 0.08)]),
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
    OUT.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # drop the old wt_/et_ quests (pre-rebuild geography)
    data = json.loads(OLD.read_text(encoding="utf-8"))
    before = len(data["quests"])
    data["quests"] = [q for q in data["quests"] if not q["quest_id"].startswith(("wt_", "et_"))]
    OLD.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Deathknell's last quest points at Rennick on Brill's square
    dk = json.loads(DK_FILE.read_text(encoding="utf-8"))
    for q in dk["quests"]:
        if q["quest_id"] == "dk_to_brill":
            q["objectives"] = [dict(type="explore", target="brill", target_x=46, target_y=44, radius=6)]
    DK_FILE.write_text(json.dumps(dk, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # NPCs
    nd = json.loads(NPCS.read_text(encoding="utf-8"))
    nd["npcs"] = [n for n in nd["npcs"] if n["npc_id"] != "et_agamand_envoy"]
    have = {n["npc_id"]: n for n in nd["npcs"]}
    for n in NEW_NPCS:
        rec = dict(n, x=0, y=0, race="forsaken")
        if n["npc_id"] in have:
            have[n["npc_id"]].update({kk: rec[kk] for kk in ("name", "greeting", "gender", "appearance_variant", "facing", "race", "zone")})
        else:
            nd["npcs"].append(rec)
    NPCS.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # quest drops
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for item_id, (name, desc, srcs) in QUEST_DROPS.items():
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
    print(f"tirisfal quests: {len(out)} (removed {before - len(data['quests'])} old), "
          f"items {sum(len(q['unique_item_defs']) for q in out)}")


if __name__ == "__main__":
    main()
